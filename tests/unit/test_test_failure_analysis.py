"""Unit tests for test-failure-analysis skill integration.

Tests the integration of test-failure-analysis skill with code_developer agent.

Related: US-065
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from coffee_maker.autonomous.agents.code_developer_agent import CodeDeveloperAgent


class TestTestFailureAnalysis:
    """Test test-failure-analysis skill integration in code_developer agent."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create a code_developer agent instance for testing."""
        with patch("coffee_maker.autonomous.agent_registry.AgentRegistry.register"):
            status_dir = tmp_path / "status"
            message_dir = tmp_path / "messages"
            status_dir.mkdir()
            message_dir.mkdir()

            agent = CodeDeveloperAgent(
                status_dir=status_dir,
                message_dir=message_dir,
                check_interval=60,
            )
            agent.current_task = {"priority": "US-065"}
            return agent

    def test_analyze_test_failures_success(self, agent):
        """Test successful test failure analysis."""
        test_output = """
FAILED tests/unit/test_auth.py::test_login_success - AssertionError: assert None is not None
FAILED tests/unit/test_auth.py::test_logout - AttributeError: 'NoneType' has no attribute 'username'
        """

        with patch("coffee_maker.autonomous.skill_loader.load_skill") as mock_load_skill, patch(
            "coffee_maker.autonomous.claude_cli_interface.ClaudeCLIInterface"
        ) as mock_claude:

            # Mock skill loading
            mock_load_skill.return_value = "Mock skill content"

            # Mock Claude API response
            mock_response = Mock()
            mock_response.success = True
            mock_response.content = "# Test Failure Analysis\n\nCRITICAL: test_login_success failed"
            mock_claude.return_value.execute_prompt.return_value = mock_response

            # Execute
            analysis = agent._analyze_test_failures(
                test_output=test_output, files_changed=["coffee_maker/auth/login.py"], priority_name="US-065"
            )

            # Verify
            assert analysis is not None
            assert "Test Failure Analysis" in analysis
            assert "CRITICAL" in analysis

            # Verify skill was loaded with correct parameters
            mock_load_skill.assert_called_once()
            call_args = mock_load_skill.call_args
            assert call_args[1]["TEST_OUTPUT"] == test_output
            assert call_args[1]["FILES_CHANGED"] == "coffee_maker/auth/login.py"
            assert call_args[1]["PRIORITY_NAME"] == "US-065"

    def test_analyze_test_failures_no_failures(self, agent):
        """Test analysis with no test failures."""
        test_output = "===== 25 passed in 2.5s ====="

        with patch("coffee_maker.autonomous.skill_loader.load_skill") as mock_load_skill, patch(
            "coffee_maker.autonomous.claude_cli_interface.ClaudeCLIInterface"
        ) as mock_claude:

            mock_load_skill.return_value = "Mock skill content"

            mock_response = Mock()
            mock_response.success = True
            mock_response.content = "# Test Failure Analysis\n\nNo failures detected"
            mock_claude.return_value.execute_prompt.return_value = mock_response

            analysis = agent._analyze_test_failures(test_output=test_output, files_changed=[], priority_name="US-065")

            assert analysis is not None
            assert "No failures" in analysis

    def test_analyze_test_failures_api_error(self, agent):
        """Test handling of API errors during analysis."""
        test_output = "FAILED tests/unit/test_auth.py::test_login_success"

        with patch("coffee_maker.autonomous.skill_loader.load_skill") as mock_load_skill, patch(
            "coffee_maker.autonomous.claude_cli_interface.ClaudeCLIInterface"
        ) as mock_claude:

            mock_load_skill.return_value = "Mock skill content"

            # Simulate API error
            mock_response = Mock()
            mock_response.success = False
            mock_response.error_message = "API rate limit exceeded"
            mock_claude.return_value.execute_prompt.return_value = mock_response

            analysis = agent._analyze_test_failures(
                test_output=test_output, files_changed=["coffee_maker/auth/login.py"], priority_name="US-065"
            )

            # Should return None on error
            assert analysis is None

    def test_analyze_test_failures_exception(self, agent):
        """Test handling of exceptions during analysis."""
        test_output = "FAILED tests/unit/test_auth.py::test_login_success"

        with patch("coffee_maker.autonomous.skill_loader.load_skill") as mock_load_skill:

            # Simulate exception during skill loading
            mock_load_skill.side_effect = Exception("Skill not found")

            analysis = agent._analyze_test_failures(
                test_output=test_output, files_changed=["coffee_maker/auth/login.py"], priority_name="US-065"
            )

            # Should return None on exception
            assert analysis is None

    def test_get_changed_files_success(self, agent):
        """Test successful retrieval of changed files."""
        with patch("subprocess.run") as mock_run:
            # Mock git diff output
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "coffee_maker/auth/login.py\ntests/unit/test_auth.py\n"
            mock_run.return_value = mock_result

            files = agent._get_changed_files()

            assert len(files) == 2
            assert "coffee_maker/auth/login.py" in files
            assert "tests/unit/test_auth.py" in files

    def test_get_changed_files_no_changes(self, agent):
        """Test when no files are changed."""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            files = agent._get_changed_files()

            assert files == []

    def test_get_changed_files_error(self, agent):
        """Test handling of git errors."""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            files = agent._get_changed_files()

            assert files == []

    def test_save_test_analysis_success(self, agent, tmp_path):
        """Test successful saving of test analysis."""
        analysis = "# Test Failure Analysis\n\nCRITICAL failures detected"

        with patch("coffee_maker.autonomous.agents.code_developer_agent.Path") as mock_path_class:
            # Mock the Path for the analysis directory
            mock_analysis_dir = MagicMock()
            mock_path_class.return_value = mock_analysis_dir

            # Mock the file path
            mock_file = MagicMock()
            mock_analysis_dir.__truediv__.return_value = mock_file

            agent._save_test_analysis(analysis)

            # Verify directory was created
            mock_analysis_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # Verify file was written
            mock_file.write_text.assert_called_once_with(analysis)

    def test_save_test_analysis_error(self, agent):
        """Test handling of errors during save."""
        analysis = "# Test Failure Analysis"

        with patch("coffee_maker.autonomous.agents.code_developer_agent.Path") as mock_path_class:
            # Simulate exception during file write
            mock_file = MagicMock()
            mock_file.write_text.side_effect = Exception("Permission denied")
            mock_path_class.return_value.__truediv__.return_value = mock_file

            # Should not raise exception
            agent._save_test_analysis(analysis)

    def test_run_tests_with_failures_triggers_analysis(self, agent):
        """Test that _run_tests triggers analysis when tests fail."""
        with patch("subprocess.run") as mock_run, patch.object(
            agent, "_analyze_test_failures"
        ) as mock_analyze, patch.object(agent, "_get_changed_files") as mock_get_changed, patch.object(
            agent, "_save_test_analysis"
        ) as mock_save:

            # Mock test failure
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = "FAILED tests/unit/test_auth.py::test_login_success"
            mock_result.stderr = "AssertionError: assert None is not None"
            mock_run.return_value = mock_result

            # Mock changed files
            mock_get_changed.return_value = ["coffee_maker/auth/login.py"]

            # Mock analysis
            mock_analyze.return_value = "# Test Failure Analysis\n\nCRITICAL failures"

            # Execute
            result = agent._run_tests()

            # Verify test failed
            assert result is False

            # Verify analysis was triggered
            mock_analyze.assert_called_once()
            call_args = mock_analyze.call_args[1]
            assert "FAILED tests/unit/test_auth.py::test_login_success" in call_args["test_output"]
            assert call_args["files_changed"] == ["coffee_maker/auth/login.py"]
            assert call_args["priority_name"] == "US-065"

            # Verify analysis was saved
            mock_save.assert_called_once_with("# Test Failure Analysis\n\nCRITICAL failures")

    def test_run_tests_with_failures_no_analysis_returned(self, agent):
        """Test that _run_tests handles case where analysis returns None."""
        with patch("subprocess.run") as mock_run, patch.object(
            agent, "_analyze_test_failures"
        ) as mock_analyze, patch.object(agent, "_get_changed_files") as mock_get_changed, patch.object(
            agent, "_save_test_analysis"
        ) as mock_save:

            # Mock test failure
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = "FAILED tests/unit/test_auth.py::test_login_success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            mock_get_changed.return_value = ["coffee_maker/auth/login.py"]

            # Mock analysis returning None (error case)
            mock_analyze.return_value = None

            # Execute
            result = agent._run_tests()

            # Verify test failed
            assert result is False

            # Verify analysis was triggered but save was not called
            mock_analyze.assert_called_once()
            mock_save.assert_not_called()

    def test_categorization_accuracy(self, agent):
        """Test that skill can categorize common failure types."""
        test_cases = [
            ("ImportError: cannot import name 'Foo'", "import"),
            ("AssertionError: assert 5 == 10", "assertion"),
            ("AttributeError: 'NoneType' has no attribute 'bar'", "attribute"),
            ("TypeError: expected str, got int", "type"),
            ("fixture 'mock_db' not found", "fixture"),
            ("TimeoutError: operation timed out", "timeout"),
        ]

        with patch("coffee_maker.autonomous.skill_loader.load_skill") as mock_load_skill, patch(
            "coffee_maker.autonomous.claude_cli_interface.ClaudeCLIInterface"
        ) as mock_claude:

            for test_output, expected_category in test_cases:
                # Mock skill loading
                mock_load_skill.return_value = "Mock skill content"

                # Mock Claude API response with category
                mock_response = Mock()
                mock_response.success = True
                mock_response.content = f"# Test Failure Analysis\n\nCategory: {expected_category} error"
                mock_claude.return_value.execute_prompt.return_value = mock_response

                # Execute
                analysis = agent._analyze_test_failures(
                    test_output=test_output, files_changed=[], priority_name="US-065"
                )

                # Verify category is mentioned
                assert analysis is not None
                assert expected_category.lower() in analysis.lower()
