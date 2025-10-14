"""Tests for ACE Generator."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.generator import ACEGenerator


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for test config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ACEConfig(
            enabled=True,
            trace_dir=Path(tmpdir) / "traces",
            delta_dir=Path(tmpdir) / "deltas",
            playbook_dir=Path(tmpdir) / "playbooks",
        )
        yield config


@pytest.fixture
def mock_agent_interface():
    """Create mock agent interface."""
    mock = MagicMock()
    mock.send_message.return_value = {
        "result": "success",
        "reasoning": ["Step 1", "Step 2"],
        "decisions": ["Use pytest"],
        "tool_calls": [{"tool": "read", "params": {"file": "test.py"}}],
        "token_usage": 1000,
    }
    return mock


class TestACEGenerator:
    """Tests for ACEGenerator class."""

    def test_init(self, mock_agent_interface, temp_config_dir):
        """Test generator initialization."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        assert generator.agent_name == "code_developer"
        assert generator.config == temp_config_dir
        assert generator.trace_manager is not None

    def test_init_creates_directories(self, mock_agent_interface, temp_config_dir):
        """Test that initialization creates necessary directories."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        assert temp_config_dir.trace_dir.exists()

    def test_execute_with_trace(self, mock_agent_interface, temp_config_dir):
        """Test executing with trace capture."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        with patch.object(
            generator,
            "_capture_git_state",
            return_value={"staged": [], "unstaged": [], "untracked": []},
        ):
            result = generator.execute_with_trace(prompt="Test prompt")

        assert "result" in result
        assert "trace_id" in result
        assert "duration" in result
        assert mock_agent_interface.send_message.called

    def test_execute_with_trace_calls_agent_twice(self, mock_agent_interface, temp_config_dir):
        """Test that agent is called twice for dual execution when conditions met."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        # Mock response with quick execution and no file changes
        mock_agent_interface.send_message.return_value = {
            "result": "success",
            "reasoning": ["Quick check"],
            "decisions": [],
            "tool_calls": [],
            "token_usage": 100,
        }

        with patch.object(
            generator,
            "_capture_git_state",
            return_value={"staged": [], "unstaged": [], "untracked": []},
        ):
            with patch.object(generator, "_diff_states") as mock_diff:
                from coffee_maker.autonomous.ace.models import ExternalObservation

                # Return empty observation (no files changed)
                mock_diff.return_value = ExternalObservation()

                # Mock execution time to be quick
                # Need enough values for: exec1_start, exec1_end, exec2_start, exec2_end, plus one for trace_id
                with patch("time.time", side_effect=[100, 0, 10, 10, 20]):  # trace_id, exec1 (10s), exec2 (10s)
                    generator.execute_with_trace(prompt="Test prompt")

        # Should be called twice (quick execution, no owned files modified)
        assert mock_agent_interface.send_message.call_count == 2

    def test_execute_with_trace_writes_trace(self, mock_agent_interface, temp_config_dir):
        """Test that trace is written to file."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        with patch.object(
            generator,
            "_capture_git_state",
            return_value={"staged": [], "unstaged": [], "untracked": []},
        ):
            result = generator.execute_with_trace(prompt="Test prompt")

        # Check that trace file was created
        trace_id = result["trace_id"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        trace_path = temp_config_dir.trace_dir / date_str / f"trace_{trace_id}.json"
        assert trace_path.exists()

    def test_execute_once(self, mock_agent_interface, temp_config_dir):
        """Test single execution."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        with patch.object(
            generator,
            "_capture_git_state",
            return_value={"staged": [], "unstaged": [], "untracked": []},
        ):
            execution = generator._execute_once(execution_id=1, prompt="Test")

        assert execution.execution_id == 1
        assert execution.result_status == "success"
        assert execution.duration_seconds > 0

    def test_execute_once_handles_errors(self, mock_agent_interface, temp_config_dir):
        """Test single execution with errors."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        # Make agent raise exception
        mock_agent_interface.send_message.side_effect = Exception("Test error")

        with patch.object(
            generator,
            "_capture_git_state",
            return_value={"staged": [], "unstaged": [], "untracked": []},
        ):
            execution = generator._execute_once(execution_id=1, prompt="Test")

        assert execution.result_status == "failure"
        assert len(execution.errors) > 0
        assert "Test error" in execution.errors[0]

    def test_capture_git_state(self, mock_agent_interface, temp_config_dir):
        """Test capturing git state."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = " M test.py\n?? new.py\n"
            state = generator._capture_git_state()

        assert "staged" in state
        assert "unstaged" in state
        assert "untracked" in state

    def test_diff_states(self, mock_agent_interface, temp_config_dir):
        """Test diffing git states."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        pre_state = {"staged": [], "unstaged": [], "untracked": []}
        post_state = {"staged": ["test.py"], "unstaged": [], "untracked": ["new.py"]}

        external_obs = generator._diff_states(pre_state, post_state)

        assert len(external_obs.files_modified) > 0 or len(external_obs.files_created) > 0

    def test_extract_internal_observation(self, mock_agent_interface, temp_config_dir):
        """Test extracting internal observation from response."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        response = {
            "reasoning": ["Step 1", "Step 2"],
            "decisions": ["Use pytest"],
            "tool_calls": [{"tool": "read"}],
        }

        internal_obs = generator._extract_internal_observation(response)

        assert len(internal_obs.reasoning_steps) == 2
        assert len(internal_obs.decisions_made) == 1
        assert len(internal_obs.tools_called) == 1

    def test_compare_executions_same_outcome(self, mock_agent_interface, temp_config_dir):
        """Test comparing executions with same outcome."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=5.0,
        )

        exec2 = Execution(
            execution_id=2,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=6.0,
        )

        comparison = generator._compare_executions(exec1, exec2)

        assert comparison.consistency == "same_outcome"
        assert "Execution 1 was faster" in comparison.effectiveness_comparison

    def test_compare_executions_different_outcomes(self, mock_agent_interface, temp_config_dir):
        """Test comparing executions with different outcomes."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=5.0,
        )

        exec2 = Execution(
            execution_id=2,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="failure",
            duration_seconds=3.0,
        )

        comparison = generator._compare_executions(exec1, exec2)

        assert comparison.consistency == "different_outcomes"
        assert "Execution 1 was more effective" in comparison.effectiveness_comparison

    def test_identify_new_insights(self, mock_agent_interface, temp_config_dir):
        """Test identifying new insights from executions."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(files_created=["test.py", "utils.py"]),
            internal_observation=InternalObservation(),
            result_status="success",
            errors=["Warning: deprecated API"],
        )

        exec2 = Execution(
            execution_id=2,
            external_observation=ExternalObservation(files_created=["test.py", "utils.py"]),
            internal_observation=InternalObservation(),
            result_status="success",
            errors=["Warning: deprecated API"],
        )

        insights = generator._identify_new_insights(exec1, exec2)

        assert len(insights) > 0
        # Should identify consistent patterns

    def test_load_current_context(self, mock_agent_interface, temp_config_dir):
        """Test loading current context."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        context = generator._load_current_context()

        assert isinstance(context, str)
        assert len(context) > 0

    def test_second_execution_skipped_long_duration(self, mock_agent_interface, temp_config_dir):
        """Second execution skipped when first takes >= 30 seconds."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        # Create execution that took 35 seconds
        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=35.0,
        )

        should_run = generator._should_run_second_execution(exec1)
        assert should_run is False

        skip_reason = generator._get_skip_reason(exec1)
        assert "30s threshold" in skip_reason
        assert "35.0s" in skip_reason

    def test_second_execution_skipped_owned_files_modified(self, mock_agent_interface, temp_config_dir):
        """Second execution skipped when owned files modified."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        # Create execution that modified coffee_maker/ (owned by code_developer)
        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(
                files_modified=["coffee_maker/cli/roadmap_cli.py"],
                files_created=["tests/test_new.py"],
            ),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=15.0,
        )

        should_run = generator._should_run_second_execution(exec1)
        assert should_run is False

        skip_reason = generator._get_skip_reason(exec1)
        assert "owned directories were modified" in skip_reason
        assert "2 files changed" in skip_reason

    def test_second_execution_runs_quick_no_changes(self, mock_agent_interface, temp_config_dir):
        """Second execution runs when quick and no owned files modified."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        # Create quick execution with no file changes
        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=10.0,
        )

        should_run = generator._should_run_second_execution(exec1)
        assert should_run is True

    def test_second_execution_runs_non_owned_files_modified(self, mock_agent_interface, temp_config_dir):
        """Second execution runs when only non-owned files modified."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        from coffee_maker.autonomous.ace.models import (
            Execution,
            ExternalObservation,
            InternalObservation,
        )

        # Create execution that modified data/ (not owned by code_developer)
        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(files_modified=["data/some_file.json"]),
            internal_observation=InternalObservation(),
            result_status="success",
            duration_seconds=10.0,
        )

        should_run = generator._should_run_second_execution(exec1)
        assert should_run is True

    def test_check_owned_directories_modified_code_developer(self, mock_agent_interface, temp_config_dir):
        """Test checking owned directories for code_developer."""
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=temp_config_dir,
            agent_name="code_developer",
        )

        from coffee_maker.autonomous.ace.models import ExternalObservation

        # Test owned files
        obs1 = ExternalObservation(files_modified=["coffee_maker/cli/test.py"])
        assert generator._check_owned_directories_modified(obs1) is True

        obs2 = ExternalObservation(files_modified=["tests/test_file.py"])
        assert generator._check_owned_directories_modified(obs2) is True

        obs3 = ExternalObservation(files_modified=["pyproject.toml"])
        assert generator._check_owned_directories_modified(obs3) is True

        # Test non-owned files
        obs4 = ExternalObservation(files_modified=["docs/README.md"])
        assert generator._check_owned_directories_modified(obs4) is False

        obs5 = ExternalObservation(files_modified=["data/status.json"])
        assert generator._check_owned_directories_modified(obs5) is False

    def test_check_owned_directories_modified_project_manager(self, mock_agent_interface, temp_config_dir):
        """Test checking owned directories for project_manager."""
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=temp_config_dir,
            agent_name="project_manager",
        )

        from coffee_maker.autonomous.ace.models import ExternalObservation

        # Test owned files
        obs1 = ExternalObservation(files_modified=["docs/roadmap/ROADMAP.md"])
        assert generator._check_owned_directories_modified(obs1) is True

        obs2 = ExternalObservation(files_modified=[".claude/CLAUDE.md"])
        assert generator._check_owned_directories_modified(obs2) is True

        # Test non-owned files
        obs3 = ExternalObservation(files_modified=["coffee_maker/cli/test.py"])
        assert generator._check_owned_directories_modified(obs3) is False

    def test_execute_with_trace_conditional_skip(self, mock_agent_interface, temp_config_dir):
        """Test that trace has skip_reason when second execution skipped."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        # Mock agent to return long execution
        with patch.object(generator, "_execute_once") as mock_execute:
            from coffee_maker.autonomous.ace.models import (
                Execution,
                ExternalObservation,
                InternalObservation,
            )

            mock_execute.return_value = Execution(
                execution_id=1,
                external_observation=ExternalObservation(),
                internal_observation=InternalObservation(),
                result_status="success",
                duration_seconds=35.0,
            )

            result = generator.execute_with_trace(prompt="Test prompt")

        # Should only execute once
        assert mock_execute.call_count == 1

        # Check trace was written with skip_reason
        trace_id = result["trace_id"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        trace_path = temp_config_dir.trace_dir / date_str / f"trace_{trace_id}.json"
        assert trace_path.exists()

        # Load trace and check skip_reason
        import json

        with open(trace_path) as f:
            trace_data = json.load(f)

        assert trace_data["skip_reason"] is not None
        assert "30s threshold" in trace_data["skip_reason"]
        assert len(trace_data["executions"]) == 1

    def test_execute_with_trace_conditional_run(self, mock_agent_interface, temp_config_dir):
        """Test that trace has no skip_reason when second execution runs."""
        generator = ACEGenerator(agent_interface=mock_agent_interface, config=temp_config_dir)

        # Mock agent to return quick execution
        with patch.object(generator, "_execute_once") as mock_execute:
            from coffee_maker.autonomous.ace.models import (
                Execution,
                ExternalObservation,
                InternalObservation,
            )

            mock_execute.return_value = Execution(
                execution_id=1,
                external_observation=ExternalObservation(),
                internal_observation=InternalObservation(),
                result_status="success",
                duration_seconds=10.0,
            )

            result = generator.execute_with_trace(prompt="Test prompt")

        # Should execute twice
        assert mock_execute.call_count == 2

        # Check trace was written without skip_reason
        trace_id = result["trace_id"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        trace_path = temp_config_dir.trace_dir / date_str / f"trace_{trace_id}.json"
        assert trace_path.exists()

        # Load trace and check no skip_reason
        import json

        with open(trace_path) as f:
            trace_data = json.load(f)

        assert trace_data["skip_reason"] is None
        assert len(trace_data["executions"]) == 2
