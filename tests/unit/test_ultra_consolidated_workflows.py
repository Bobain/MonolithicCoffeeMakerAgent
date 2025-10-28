"""Tests for ultra-consolidated workflow commands.

Tests the 8 workflow commands that replace the 36 consolidated commands.
Each workflow command handles a complete workflow, not individual steps.
"""

import pytest
from unittest.mock import Mock, patch
from coffee_maker.commands.workflow.code_developer_workflow import (
    CodeDeveloperWorkflow,
    WorkStatus,
    WorkResult,
)
from coffee_maker.commands.workflow.architect_workflow import ArchitectWorkflow
from coffee_maker.commands.workflow.project_manager_workflow import ProjectManagerWorkflow
from coffee_maker.commands.workflow.code_reviewer_workflow import CodeReviewerWorkflow
from coffee_maker.commands.workflow.orchestrator_workflow import OrchestratorWorkflow
from coffee_maker.commands.workflow.user_listener_workflow import UserListenerWorkflow
from coffee_maker.commands.workflow.assistant_workflow import AssistantWorkflow
from coffee_maker.commands.workflow.ux_design_workflow import UXDesignWorkflow


class TestCodeDeveloperWorkflow:
    """Test code_developer.work() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.code_developer_workflow.CodeDeveloperCommands"):
            return CodeDeveloperWorkflow(db_path=":memory:")

    def test_work_auto_mode_success(self, workflow):
        """Test full autonomous workflow execution."""
        # Mock all command responses
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100", "description": "Test task"},  # load
                {"files": ["test.py", "test2.py"]},  # write_code
            ]
        )
        workflow.commands.test = Mock(return_value={"total": 10, "passed": 10})
        workflow.commands.quality = Mock(return_value={"status": "passed"})
        workflow.commands.git = Mock(return_value="abc123def")

        result = workflow.work(task_id="TASK-1", mode="auto")

        assert result.status == WorkStatus.SUCCESS
        assert result.task_id == "TASK-1"
        assert len(result.steps_completed) >= 5
        assert len(result.steps_failed) == 0
        assert len(result.files_changed) == 2
        assert result.tests_run == 10
        assert result.tests_passed == 10
        assert result.commit_sha == "abc123def"

    def test_work_auto_mode_with_test_failures_then_fix(self, workflow):
        """Test workflow with test failures that get auto-fixed."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100", "description": "Test task"},
                {"files": ["test.py"]},
            ]
        )
        # First test run fails, after fix attempt, second run passes
        workflow.commands.test = Mock(
            side_effect=[
                {"total": 10, "passed": 8},  # First run: 2 failures
                None,  # Fix action (doesn't return test results)
                {"total": 10, "passed": 10},  # After fix: all pass
            ]
        )
        workflow.commands.quality = Mock(return_value={"status": "passed"})
        workflow.commands.git = Mock(return_value="abc123def")

        result = workflow.work(task_id="TASK-1", mode="auto")

        # After successful fix and re-run, should succeed
        assert result.status == WorkStatus.SUCCESS
        assert result.tests_run == 10
        assert result.tests_passed == 10
        # run (fail) + fix + run (pass) = 3 calls
        assert workflow.commands.test.call_count == 3

    def test_work_test_only_mode(self, workflow):
        """Test test-only mode (no code changes)."""
        workflow.commands.test = Mock(return_value={"total": 5, "passed": 5})

        result = workflow.work(task_id="TASK-1", mode="test-only")

        assert result.status == WorkStatus.SUCCESS
        assert "run_tests" in result.steps_completed
        assert result.tests_run == 5
        assert result.tests_passed == 5
        assert result.commit_sha is None

    def test_work_commit_only_mode(self, workflow):
        """Test commit-only mode (commit existing changes)."""
        workflow.commands.git = Mock(return_value="xyz789abc")

        result = workflow.work(task_id="TASK-1", mode="commit-only", commit_message="fix: test commit")

        assert result.status == WorkStatus.SUCCESS
        assert "commit" in result.steps_completed
        assert result.commit_sha == "xyz789abc"

    def test_work_code_only_mode(self, workflow):
        """Test code-only mode (no tests or commit)."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                {"files": ["code.py"]},
            ]
        )

        result = workflow.work(task_id="TASK-1", mode="code-only")

        assert result.status == WorkStatus.SUCCESS
        assert "load_task" in result.steps_completed
        assert "write_code" in result.steps_completed
        assert len(result.files_changed) == 1
        assert result.commit_sha is None

    def test_work_step_mode(self, workflow):
        """Test step-by-step mode (currently delegates to auto)."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                {"files": ["step.py"]},
            ]
        )
        workflow.commands.test = Mock(return_value={"total": 1, "passed": 1})
        workflow.commands.quality = Mock(return_value={"status": "passed"})
        workflow.commands.git = Mock(return_value="step123")

        result = workflow.work(task_id="TASK-1", mode="step")

        # Currently delegates to auto mode
        assert result.status == WorkStatus.SUCCESS

    def test_work_skip_tests_flag(self, workflow):
        """Test skipping tests with flag."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                {"files": ["test.py"]},
            ]
        )
        workflow.commands.quality = Mock(return_value={"status": "passed"})
        workflow.commands.git = Mock(return_value="abc123")

        result = workflow.work(task_id="TASK-1", mode="auto", skip_tests=True)

        assert result.status == WorkStatus.SUCCESS
        assert result.metadata.get("tests_skipped") is True
        assert result.tests_run == 0

    def test_work_skip_quality_flag(self, workflow):
        """Test skipping quality checks with flag."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                {"files": ["test.py"]},
            ]
        )
        workflow.commands.test = Mock(return_value={"total": 1, "passed": 1})
        workflow.commands.git = Mock(return_value="abc123")

        result = workflow.work(task_id="TASK-1", mode="auto", skip_quality=True)

        assert result.status == WorkStatus.SUCCESS
        assert result.metadata.get("quality_skipped") is True

    def test_work_no_auto_commit(self, workflow):
        """Test disabling auto-commit."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                {"files": ["test.py"]},
            ]
        )
        workflow.commands.test = Mock(return_value={"total": 1, "passed": 1})
        workflow.commands.quality = Mock(return_value={"status": "passed"})

        result = workflow.work(task_id="TASK-1", mode="auto", auto_commit=False)

        assert result.status == WorkStatus.SUCCESS
        assert result.commit_sha is None
        assert result.metadata.get("commit_skipped") is True

    def test_work_invalid_mode(self, workflow):
        """Test error handling for invalid mode."""
        result = workflow.work(task_id="TASK-1", mode="invalid-mode")

        assert result.status == WorkStatus.FAILED
        assert "Invalid mode" in result.error_message

    def test_work_load_task_failure(self, workflow):
        """Test failure at load task step."""
        workflow.commands.implement = Mock(side_effect=Exception("Task not found"))

        result = workflow.work(task_id="TASK-1", mode="auto")

        assert result.status == WorkStatus.FAILED
        assert "load_task" in result.steps_failed
        assert "Task not found" in result.error_message

    def test_work_write_code_failure(self, workflow):
        """Test failure at write code step."""
        workflow.commands.implement = Mock(
            side_effect=[
                {"spec_id": "SPEC-100"},
                Exception("Code generation failed"),
            ]
        )

        result = workflow.work(task_id="TASK-1", mode="auto")

        # Since load_task succeeded, status should be PARTIAL, not FAILED
        assert result.status == WorkStatus.PARTIAL
        assert "write_code" in result.steps_failed
        assert "Code generation failed" in result.error_message

    def test_work_result_string_representation(self):
        """Test WorkResult __str__ method."""
        result = WorkResult(
            status=WorkStatus.SUCCESS,
            task_id="TASK-1",
            steps_completed=["load", "code", "test", "commit"],
            files_changed=["file1.py", "file2.py"],
            tests_run=10,
            tests_passed=10,
            commit_sha="abc123def456",
            duration_seconds=45.2,
        )

        result_str = str(result)
        assert "success" in result_str  # lowercase, not uppercase
        assert "TASK-1" in result_str
        assert "4 completed" in result_str
        assert "2 changed" in result_str
        assert "10/10 passed" in result_str
        assert "abc123de" in result_str  # First 8 chars
        assert "45.2s" in result_str

    def test_generate_commit_message_feat(self, workflow):
        """Test commit message generation for feature."""
        result = WorkResult(
            status=WorkStatus.SUCCESS,
            task_id="TASK-1",
            files_changed=["new_feature.py"],
            tests_run=5,
            tests_passed=5,
        )
        result.metadata = {
            "task_data": {
                "spec_id": "SPEC-100",
                "description": "Add new dashboard feature",
            }
        }

        message = workflow._generate_commit_message("TASK-1", result)

        assert message.startswith("feat:")
        assert "Add new dashboard feature" in message
        assert "SPEC-100" in message
        assert "1 files" in message
        assert "5/5 passing" in message
        assert "🤖 Generated with" in message
        assert "Co-Authored-By: Claude" in message

    def test_generate_commit_message_fix(self, workflow):
        """Test commit message generation for bug fix."""
        result = WorkResult(status=WorkStatus.SUCCESS, task_id="TASK-1")
        result.metadata = {
            "task_data": {
                "spec_id": "SPEC-101",
                "description": "Fix authentication bug in login",
            }
        }

        message = workflow._generate_commit_message("TASK-1", result)

        assert message.startswith("fix:")
        assert "authentication bug" in message


class TestArchitectWorkflow:
    """Test architect.spec() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.architect_workflow.ArchitectCommands"):
            return ArchitectWorkflow(db_path=":memory:")

    def test_spec_full_workflow(self, workflow):
        """Test full architectural design workflow."""
        workflow.commands.design = Mock(return_value={"complexity": "medium"})
        workflow.commands.specs = Mock(return_value={"spec_id": "SPEC-5"})
        workflow.commands.adr = Mock(return_value={"adr_id": "ADR-5"})

        result = workflow.spec(priority_id="PRIORITY-5")

        assert result.status == "success"
        assert result.spec_id == "SPEC-5"
        assert result.priority_id == "PRIORITY-5"
        assert len(result.steps_completed) >= 4
        assert result.adr_created is True

    def test_spec_quick_mode(self, workflow):
        """Test quick design workflow."""
        workflow.commands.design = Mock(return_value={"design": "created"})
        workflow.commands.specs = Mock(return_value={"spec_id": "SPEC-6"})

        result = workflow.spec(priority_id="PRIORITY-6", depth="quick")

        assert result.status == "success"
        assert result.spec_id == "SPEC-6"
        assert result.adr_created is False  # Quick mode skips ADR
        assert result.poc_created is False  # Quick mode skips POC

    def test_spec_with_dependencies(self, workflow):
        """Test spec with dependency checking."""
        workflow.commands.design = Mock(return_value={"complexity": "low"})
        workflow.commands.specs = Mock(return_value={"spec_id": "SPEC-7"})
        workflow.commands.dependency = Mock(return_value={"approved": True})
        workflow.commands.adr = Mock(return_value={"adr_id": "ADR-7"})

        result = workflow.spec(priority_id="PRIORITY-7", dependencies=["fastapi", "pydantic"])

        assert result.status == "success"
        assert len(result.dependencies_checked) == 2
        assert "fastapi" in result.dependencies_checked
        assert "pydantic" in result.dependencies_checked

    def test_spec_with_poc_required(self, workflow):
        """Test spec with POC creation."""
        workflow.commands.design = Mock(return_value={"complexity": "high"})
        workflow.commands.specs = Mock(return_value={"spec_id": "SPEC-8"})
        workflow.commands.poc = Mock(return_value={"poc_created": True})
        workflow.commands.adr = Mock(return_value={"adr_id": "ADR-8"})

        result = workflow.spec(priority_id="PRIORITY-8", poc_required=True)

        assert result.status == "success"
        assert result.poc_created is True
        workflow.commands.poc.assert_called_once()

    def test_spec_invalid_depth(self, workflow):
        """Test error handling for invalid depth."""
        result = workflow.spec(priority_id="PRIORITY-9", depth="invalid")

        assert result.status == "failed"
        assert "Invalid depth" in result.error_message


class TestProjectManagerWorkflow:
    """Test project_manager.manage() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.project_manager_workflow.ProjectManagerCommands"):
            return ProjectManagerWorkflow(db_path=":memory:")

    def test_manage_roadmap_action(self, workflow):
        """Test roadmap management."""
        workflow.commands.roadmap = Mock(return_value={"priorities": []})
        workflow.commands.notifications = Mock(return_value={"sent": 0})

        result = workflow.manage(action="roadmap")

        assert result.status == "success"
        assert result.action == "roadmap"
        assert isinstance(result.data, dict)
        assert workflow.commands.roadmap.called

    def test_manage_track_action(self, workflow):
        """Test progress tracking."""
        workflow.commands.tasks = Mock(return_value={"tasks": [], "total": 0})

        result = workflow.manage(action="track")

        assert result.status == "success"
        assert result.action == "track"
        assert isinstance(result.data, dict)

    def test_manage_invalid_action(self, workflow):
        """Test error handling for invalid action."""
        result = workflow.manage(action="invalid")

        assert result.status == "failed"
        assert "Invalid action" in result.data


class TestCodeReviewerWorkflow:
    """Test code_reviewer.review() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.code_reviewer_workflow.CodeReviewerCommands"):
            return CodeReviewerWorkflow(db_path=":memory:")

    def test_review_full_scope(self, workflow):
        """Test full code review."""
        workflow.commands.review = Mock(return_value={"quality_score": 85, "issues_found": 2})

        result = workflow.review(target="abc123", scope="full")

        assert result.status == "success"
        assert result.quality_score == 85
        assert result.target == "abc123"

    def test_review_quick_scope(self, workflow):
        """Test quick review."""
        workflow.commands.review = Mock(return_value={"quality_score": 90})

        result = workflow.review(target="def456", scope="quick")

        assert result.status == "success"
        assert result.quality_score == 90


class TestOrchestratorWorkflow:
    """Test orchestrator.coordinate() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.orchestrator_workflow.OrchestratorCommands"):
            return OrchestratorWorkflow(db_path=":memory:")

    def test_coordinate_agents_action(self, workflow):
        """Test agent coordination."""
        workflow.commands.agents = Mock(return_value={"agents": ["code_developer"]})

        result = workflow.coordinate(action="agents")

        assert result.status == "success"
        assert result.action == "agents"
        assert "agents" in result.metadata

    def test_coordinate_work_action(self, workflow):
        """Test work assignment."""
        workflow.commands.orchestrate = Mock(return_value={"work_found": True})

        result = workflow.coordinate(action="work")

        assert result.status == "success"
        assert result.action == "work"

    def test_coordinate_invalid_action(self, workflow):
        """Test error handling for invalid action."""
        result = workflow.coordinate(action="invalid")

        assert result.status == "failed"


class TestUserListenerWorkflow:
    """Test user_listener.interact() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.user_listener_workflow.UserListenerCommands"):
            return UserListenerWorkflow(db_path=":memory:")

    def test_interact_basic(self, workflow):
        """Test basic user interaction."""
        workflow.commands.understand = Mock(
            side_effect=[
                {"intent": "query"},  # classify_intent call
                "code_developer",  # determine_agent call
            ]
        )
        workflow.commands.route = Mock(return_value={"routed": True})

        result = workflow.interact(input="Hello")

        # interact() returns a formatted string
        assert isinstance(result, str)
        assert "code_developer" in result


class TestAssistantWorkflow:
    """Test assistant.assist() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.assistant_workflow.AssistantCommands"):
            return AssistantWorkflow(db_path=":memory:")

    def test_assist_auto_type(self, workflow):
        """Test auto-detection of assistance type."""
        workflow.commands.delegate = Mock(return_value={"intent": "docs"})
        workflow.commands.docs = Mock(return_value={"generated": True})

        result = workflow.assist(request="Generate docs for feature X", type="auto")

        assert result["generated"] is True

    def test_assist_docs_type(self, workflow):
        """Test explicit docs assistance."""
        workflow.commands.docs = Mock(return_value={"docs": "created"})

        result = workflow.assist(request="API reference", type="docs")

        assert result["docs"] == "created"

    def test_assist_demo_type(self, workflow):
        """Test demo creation assistance."""
        workflow.commands.demo = Mock(return_value={"demo": "created"})

        result = workflow.assist(request="Create demo", type="demo")

        assert result["demo"] == "created"


class TestUXDesignWorkflow:
    """Test ux_design.design() workflow command."""

    @pytest.fixture
    def workflow(self):
        """Create workflow instance."""
        with patch("coffee_maker.commands.workflow.ux_design_workflow.UXDesignExpertCommands"):
            return UXDesignWorkflow(db_path=":memory:")

    def test_design_full_phase(self, workflow):
        """Test full design workflow."""
        workflow.commands.design = Mock(return_value="spec_created")
        workflow.commands.components = Mock(return_value="components_created")

        result = workflow.design(feature="Dashboard", phase="full")

        assert result["spec"] == "spec_created"
        assert result["components"] == "components_created"
