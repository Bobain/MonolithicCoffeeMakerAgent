"""Integration tests for Generator ownership enforcement (US-038 Phase 2).

These tests verify that the Generator correctly enforces file ownership
and auto-delegates to the correct owner when violations are detected.

Test Coverage:
    - Generator blocks ownership violations
    - Generator auto-delegates to correct owner
    - WriteTool enforces ownership
    - ReadTool allows unrestricted access
    - Delegation traces are logged correctly
    - Integration between Generator, WriteTool, and FileOwnership
"""

import pytest

from coffee_maker.autonomous.ace.file_ownership import (
    OwnershipViolationError,
)
from coffee_maker.autonomous.ace.file_tools import ReadTool, WriteTool
from coffee_maker.autonomous.ace.generator import (
    FileOperationType,
    Generator,
    get_generator,
)
from coffee_maker.autonomous.agent_registry import AgentType


class TestGeneratorOwnershipEnforcement:
    """Test Generator enforcement of file ownership."""

    def setup_method(self):
        """Reset state before each test."""
        # Create fresh Generator instance
        self.generator = Generator()
        self.generator.clear_traces()

    def test_generator_allows_owner_to_write(self):
        """Test Generator allows file owner to write."""
        # code_developer owns .claude/CLAUDE.md
        result = self.generator.intercept_file_operation(
            agent_type=AgentType.CODE_DEVELOPER,
            file_path=".claude/CLAUDE.md",
            operation="write",
            content="# Updated",
        )

        assert result.success is True
        assert result.delegated is False
        assert result.delegated_to is None

    def test_generator_blocks_non_owner_write(self):
        """Test Generator detects ownership violation and delegates."""
        # project_manager tries to write to code_developer's file
        result = self.generator.intercept_file_operation(
            agent_type=AgentType.PROJECT_MANAGER,
            file_path=".claude/CLAUDE.md",
            operation="write",
            content="# Updated",
        )

        assert result.success is True  # Delegated operation succeeds
        assert result.delegated is True
        assert result.delegated_to == AgentType.CODE_DEVELOPER

    def test_generator_allows_all_reads(self):
        """Test Generator allows read operations without ownership check."""
        # assistant reads code_developer's file (allowed)
        result = self.generator.intercept_file_operation(
            agent_type=AgentType.ASSISTANT,
            file_path=".claude/CLAUDE.md",
            operation="read",
        )

        assert result.success is True
        assert result.delegated is False

        # assistant reads project_manager's file (allowed)
        result = self.generator.intercept_file_operation(
            agent_type=AgentType.ASSISTANT,
            file_path="docs/roadmap/ROADMAP.md",
            operation="read",
        )

        assert result.success is True
        assert result.delegated is False

    def test_generator_logs_delegation_trace(self):
        """Test Generator logs delegation traces for reflector analysis."""
        # Clear traces
        self.generator.clear_traces()

        # Trigger delegation
        result = self.generator.intercept_file_operation(
            agent_type=AgentType.ASSISTANT,
            file_path="coffee_maker/test.py",
            operation="write",
            content="# test",
        )

        # Check trace was logged
        traces = self.generator.get_delegation_traces()
        assert len(traces) == 1

        trace = traces[0]
        assert trace.requesting_agent == AgentType.ASSISTANT
        assert trace.owner_agent == AgentType.CODE_DEVELOPER
        assert trace.file_path == "coffee_maker/test.py"
        assert trace.operation == FileOperationType.WRITE
        assert trace.success is True

    def test_generator_delegation_stats(self):
        """Test Generator provides delegation statistics."""
        self.generator.clear_traces()

        # Create multiple delegations
        self.generator.intercept_file_operation(AgentType.ASSISTANT, "coffee_maker/test1.py", "write", content="test")
        self.generator.intercept_file_operation(AgentType.ASSISTANT, "coffee_maker/test2.py", "write", content="test")
        self.generator.intercept_file_operation(AgentType.PROJECT_MANAGER, ".claude/CLAUDE.md", "write", content="test")

        stats = self.generator.get_delegation_stats()

        assert stats["total_delegations"] == 3
        assert stats["delegations_by_requesting_agent"]["assistant"] == 2
        assert stats["delegations_by_requesting_agent"]["project_manager"] == 1
        assert stats["delegations_by_owner"]["code_developer"] == 3

    def test_generator_multiple_operations(self):
        """Test Generator handles multiple operation types."""
        # Test write
        result = self.generator.intercept_file_operation(
            AgentType.PROJECT_MANAGER,
            ".claude/CLAUDE.md",
            "write",
        )
        assert result.delegated is True

        # Test edit
        result = self.generator.intercept_file_operation(
            AgentType.PROJECT_MANAGER,
            ".claude/CLAUDE.md",
            "edit",
        )
        assert result.delegated is True

        # Test delete
        result = self.generator.intercept_file_operation(
            AgentType.PROJECT_MANAGER,
            ".claude/CLAUDE.md",
            "delete",
        )
        assert result.delegated is True

        # Test read (always allowed)
        result = self.generator.intercept_file_operation(
            AgentType.PROJECT_MANAGER,
            ".claude/CLAUDE.md",
            "read",
        )
        assert result.delegated is False


class TestWriteToolOwnershipEnforcement:
    """Test WriteTool enforcement of file ownership."""

    def test_write_tool_allows_owner(self):
        """Test WriteTool allows owner to write."""
        tool = WriteTool(AgentType.CODE_DEVELOPER)

        # code_developer owns coffee_maker/
        result = tool.write_file("coffee_maker/test.py", "# code")

        assert result is True

    def test_write_tool_delegates_non_owner(self):
        """Test WriteTool auto-delegates when non-owner tries to write."""
        tool = WriteTool(AgentType.PROJECT_MANAGER)

        # project_manager tries to write to code_developer's file
        result = tool.write_file("coffee_maker/test.py", "# code")

        # Should delegate and succeed
        assert result is True

    def test_write_tool_raises_on_violation_if_requested(self):
        """Test WriteTool raises exception if raise_on_violation=True."""
        tool = WriteTool(AgentType.PROJECT_MANAGER)

        # project_manager tries to write to code_developer's file
        with pytest.raises(OwnershipViolationError) as exc_info:
            tool.write_file("coffee_maker/test.py", "# code", raise_on_violation=True)

        assert exc_info.value.agent == AgentType.PROJECT_MANAGER
        assert exc_info.value.owner == AgentType.CODE_DEVELOPER

    def test_write_tool_can_write_check(self):
        """Test WriteTool.can_write() correctly checks ownership."""
        tool = WriteTool(AgentType.CODE_DEVELOPER)

        # Owns these files
        assert tool.can_write("coffee_maker/test.py") is True
        assert tool.can_write(".claude/CLAUDE.md") is True

        # Doesn't own these files
        assert tool.can_write("docs/roadmap/ROADMAP.md") is False
        assert tool.can_write("docs/architecture/spec.md") is False

    def test_write_tool_get_allowed_paths(self):
        """Test WriteTool.get_allowed_paths() returns correct patterns."""
        tool = WriteTool(AgentType.CODE_DEVELOPER)

        allowed = tool.get_allowed_paths()

        assert ".claude/**" in allowed
        assert "coffee_maker/**" in allowed
        assert "tests/**" in allowed
        assert "docs/roadmap/**" not in allowed

    def test_write_tool_edit_operation(self):
        """Test WriteTool.edit_file() with ownership enforcement."""
        tool = WriteTool(AgentType.CODE_DEVELOPER)

        # Edit owned file
        result = tool.edit_file("coffee_maker/test.py", "old", "new")
        assert result is True

    def test_write_tool_delete_operation(self):
        """Test WriteTool.delete_file() with ownership enforcement."""
        tool = WriteTool(AgentType.CODE_DEVELOPER)

        # Delete owned file
        result = tool.delete_file("coffee_maker/test.py")
        assert result is True


class TestReadToolUnrestricted:
    """Test ReadTool allows unrestricted access."""

    def test_read_tool_reads_any_file(self):
        """Test ReadTool allows reading any file."""
        tool = ReadTool(AgentType.ASSISTANT)

        # Should allow reading code_developer's files
        result = tool.file_exists(".claude/CLAUDE.md")
        assert result is True

        # Should allow reading project_manager's files
        result = tool.file_exists("docs/roadmap/ROADMAP.md")
        # May not exist, but operation is allowed
        assert isinstance(result, bool)

    def test_read_tool_no_ownership_restrictions(self):
        """Test ReadTool has no ownership restrictions."""
        # Different agents should all be able to read the same file
        tool1 = ReadTool(AgentType.ASSISTANT)
        tool2 = ReadTool(AgentType.CODE_DEVELOPER)
        tool3 = ReadTool(AgentType.PROJECT_MANAGER)

        # All should be able to check existence
        exists1 = tool1.file_exists(".claude/CLAUDE.md")
        exists2 = tool2.file_exists(".claude/CLAUDE.md")
        exists3 = tool3.file_exists(".claude/CLAUDE.md")

        assert exists1 == exists2 == exists3


class TestGeneratorIntegration:
    """Test integration between Generator, FileOwnership, and tools."""

    def test_full_delegation_workflow(self):
        """Test complete workflow from violation detection to delegation."""
        generator = Generator()
        generator.clear_traces()

        # 1. project_manager tries to write to code_developer's file
        result = generator.intercept_file_operation(
            agent_type=AgentType.PROJECT_MANAGER,
            file_path="coffee_maker/cli/test.py",
            operation="write",
            content="# test",
        )

        # 2. Verify delegation happened
        assert result.delegated is True
        assert result.delegated_to == AgentType.CODE_DEVELOPER

        # 3. Check delegation trace
        traces = generator.get_delegation_traces(agent=AgentType.PROJECT_MANAGER)
        assert len(traces) == 1
        assert traces[0].requesting_agent == AgentType.PROJECT_MANAGER
        assert traces[0].owner_agent == AgentType.CODE_DEVELOPER

    def test_multiple_agents_delegation_patterns(self):
        """Test delegation patterns across multiple agents."""
        generator = Generator()
        generator.clear_traces()

        # assistant tries various files
        generator.intercept_file_operation(AgentType.ASSISTANT, "coffee_maker/test.py", "write", content="test")
        generator.intercept_file_operation(AgentType.ASSISTANT, "docs/roadmap/ROADMAP.md", "write", content="test")
        generator.intercept_file_operation(AgentType.ASSISTANT, ".claude/CLAUDE.md", "write", content="test")

        # Check stats
        stats = generator.get_delegation_stats()
        assert stats["total_delegations"] == 3
        assert stats["delegations_by_requesting_agent"]["assistant"] == 3

        # Check most common violation patterns
        violations = stats["most_common_violations"]
        # Should have assistant → code_developer and assistant → project_manager
        patterns = [v["pattern"] for v in violations]
        assert "assistant → code_developer" in patterns
        assert "assistant → project_manager" in patterns

    def test_ownership_unclear_allows_operation(self):
        """Test Generator allows operation when ownership unclear."""
        generator = Generator()

        # Try file with unclear ownership (not in ownership rules)
        result = generator.intercept_file_operation(
            agent_type=AgentType.ASSISTANT,
            file_path="some/unknown/file.txt",
            operation="write",
            content="test",
        )

        # Should allow (fail open)
        assert result.success is True
        assert result.delegated is False

    def test_generator_singleton(self):
        """Test get_generator() returns singleton instance."""
        gen1 = get_generator()
        gen2 = get_generator()

        assert gen1 is gen2

    def test_write_tool_integration_with_generator(self):
        """Test WriteTool correctly integrates with Generator."""
        generator = Generator()
        generator.clear_traces()

        tool = WriteTool(AgentType.PROJECT_MANAGER, generator=generator)

        # Write to non-owned file (should delegate)
        result = tool.write_file("coffee_maker/test.py", "# test")
        assert result is True

        # Check delegation was logged
        traces = generator.get_delegation_traces()
        assert len(traces) == 1
        assert traces[0].requesting_agent == AgentType.PROJECT_MANAGER
        assert traces[0].owner_agent == AgentType.CODE_DEVELOPER


class TestCrossAgentDelegation:
    """Test delegation scenarios between different agents."""

    def test_code_developer_to_project_manager_delegation(self):
        """Test code_developer delegating to project_manager."""
        generator = Generator()

        # code_developer tries to write to project_manager's file
        result = generator.intercept_file_operation(
            agent_type=AgentType.CODE_DEVELOPER,
            file_path="docs/roadmap/ROADMAP.md",
            operation="write",
            content="# roadmap",
        )

        assert result.delegated is True
        assert result.delegated_to == AgentType.PROJECT_MANAGER

    def test_project_manager_to_architect_delegation(self):
        """Test project_manager delegating to architect."""
        generator = Generator()

        # project_manager tries to write to architect's file
        result = generator.intercept_file_operation(
            agent_type=AgentType.PROJECT_MANAGER,
            file_path="docs/architecture/specs/spec.md",
            operation="write",
            content="# spec",
        )

        assert result.delegated is True
        assert result.delegated_to == AgentType.ARCHITECT

    def test_architect_to_code_developer_delegation(self):
        """Test architect delegating to code_developer."""
        generator = Generator()

        # architect tries to write to code_developer's file
        result = generator.intercept_file_operation(
            agent_type=AgentType.ARCHITECT,
            file_path="coffee_maker/test.py",
            operation="write",
            content="# test",
        )

        assert result.delegated is True
        assert result.delegated_to == AgentType.CODE_DEVELOPER


class TestDelegationTraceFiltering:
    """Test delegation trace filtering and querying."""

    def test_filter_traces_by_agent(self):
        """Test filtering delegation traces by requesting agent."""
        generator = Generator()
        generator.clear_traces()

        # Create delegations from different agents
        generator.intercept_file_operation(AgentType.ASSISTANT, "coffee_maker/test.py", "write", content="test")
        generator.intercept_file_operation(AgentType.PROJECT_MANAGER, "coffee_maker/test.py", "write", content="test")
        generator.intercept_file_operation(AgentType.ASSISTANT, "docs/roadmap/ROADMAP.md", "write", content="test")

        # Filter by assistant
        assistant_traces = generator.get_delegation_traces(agent=AgentType.ASSISTANT)
        assert len(assistant_traces) == 2
        assert all(t.requesting_agent == AgentType.ASSISTANT for t in assistant_traces)

        # Filter by project_manager
        pm_traces = generator.get_delegation_traces(agent=AgentType.PROJECT_MANAGER)
        assert len(pm_traces) == 1
        assert pm_traces[0].requesting_agent == AgentType.PROJECT_MANAGER

    def test_trace_serialization(self):
        """Test delegation trace can be serialized to dict."""
        generator = Generator()
        generator.clear_traces()

        # Create delegation
        generator.intercept_file_operation(AgentType.ASSISTANT, "coffee_maker/test.py", "write", content="test")

        # Get trace and serialize
        traces = generator.get_delegation_traces()
        trace_dict = traces[0].to_dict()

        # Verify structure
        assert "trace_id" in trace_dict
        assert "timestamp" in trace_dict
        assert trace_dict["requesting_agent"] == "assistant"
        assert trace_dict["owner_agent"] == "code_developer"
        assert trace_dict["file_path"] == "coffee_maker/test.py"
        assert trace_dict["operation"] == "write"
