"""Tests for code-sanitizer agent with ACE integration."""

from unittest.mock import Mock, patch
from pathlib import Path

from coffee_maker.autonomous.agents.code_sanitizer import CodeSanitizer


class TestCodeSanitizerAgent:
    """Test code-sanitizer agent functionality."""

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_code_sanitizer_automatically_enables_ace(self, mock_config, mock_generator_class, mock_getenv):
        """Verify code-sanitizer automatically enables ACE."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_CODE_SANITIZER":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        # Create agent
        agent = CodeSanitizer()

        # Verify ACE enabled
        assert agent.ace_enabled is True
        assert agent.generator is not None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_can_disable_ace(self, mock_getenv):
        """Verify code-sanitizer can disable ACE via env var."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_CODE_SANITIZER":
                return "false"
            return default

        mock_getenv.side_effect = getenv_side_effect

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        # Create agent
        agent = CodeSanitizer()

        # Verify ACE disabled
        assert agent.ace_enabled is False
        assert agent.generator is None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_creates_directories(self, mock_getenv):
        """Verify code-sanitizer creates required directories."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        agent = CodeSanitizer()

        # Verify directories exist
        assert agent.refacto_dir.exists()
        assert agent.refacto_dir == Path("docs/refacto")

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_properties(self, mock_getenv):
        """Verify code-sanitizer agent properties."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        agent = CodeSanitizer()

        assert agent.agent_name == "code_sanitizer"
        assert "quality" in agent.agent_objective.lower()
        assert "refactoring" in agent.agent_objective.lower()
        assert "recommendations" in agent.success_criteria.lower()

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_singleton_pattern(self, mock_getenv):
        """Verify code-sanitizer uses singleton pattern."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        # Create two instances
        agent1 = CodeSanitizer()
        agent2 = CodeSanitizer()

        # Verify they're the same instance
        assert agent1 is agent2

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.agents.code_sanitizer.subprocess.run")
    def test_code_sanitizer_execute_implementation(self, mock_subprocess, mock_getenv):
        """Verify code-sanitizer can execute analysis tasks."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        # Mock subprocess calls (radon, flake8)
        mock_subprocess.return_value = Mock(returncode=0, stdout="{}", stderr="")

        agent = CodeSanitizer()

        # Execute task
        result = agent._execute_implementation(code_path="coffee_maker/", context={"changed_files": ["test.py"]})

        # Verify result
        assert result["status"] == "success"
        assert "report_path" in result
        assert "recommendations" in result
        assert "summary" in result

        # Verify summary contains priority counts
        assert "high_priority" in result["summary"]
        assert "medium_priority" in result["summary"]
        assert "low_priority" in result["summary"]

        # Cleanup generated report
        report_path = Path(result["report_path"])
        if report_path.exists():
            report_path.unlink()

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_wake_on_code_change(self, mock_getenv):
        """Verify code-sanitizer can wake on code changes."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        agent = CodeSanitizer()

        # Mock _execute_implementation
        with patch.object(agent, "_execute_implementation") as mock_execute:
            mock_execute.return_value = {"status": "success"}

            # Wake on code change
            result = agent.wake_on_code_change(changed_files=["file1.py", "file2.py"])

            # Verify execute_implementation was called
            assert mock_execute.called
            # Verify context was passed
            call_kwargs = mock_execute.call_args[1]
            assert "context" in call_kwargs
            assert "changed_files" in call_kwargs["context"]
            assert len(call_kwargs["context"]["changed_files"]) == 2

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_load_style_guide(self, mock_getenv):
        """Verify code-sanitizer can load style guide."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        agent = CodeSanitizer()

        # Load style guide
        style_guide = agent._load_style_guide()

        # If style guide exists, verify it was loaded
        if agent.style_guide_path.exists():
            assert style_guide.get("loaded") is True
            assert "content" in style_guide

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_code_sanitizer_generate_recommendations(self, mock_getenv):
        """Verify code-sanitizer generates recommendations correctly."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(CodeSanitizer, "_instance"):
            delattr(CodeSanitizer, "_instance")

        agent = CodeSanitizer()

        # Test complexity-based recommendations
        complexity = {
            "test.py": [{"name": "complex_function", "complexity": 16}, {"name": "simple_function", "complexity": 5}]
        }

        duplication = {"duplicates_found": 0, "details": []}

        style = {"total_violations": 5, "details": ""}

        style_guide = {"loaded": True}

        recommendations = agent._generate_recommendations(complexity, duplication, style, style_guide)

        # Verify high-priority recommendation for complex function
        high_priority = [r for r in recommendations if r["priority"] == "high"]
        assert len(high_priority) == 1
        assert high_priority[0]["function"] == "complex_function"
        assert high_priority[0]["complexity"] == 16

        # Verify no recommendations for simple function
        simple_recs = [r for r in recommendations if r.get("function") == "simple_function"]
        assert len(simple_recs) == 0
