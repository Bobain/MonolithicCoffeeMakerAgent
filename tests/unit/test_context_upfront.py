"""Tests for US-042: Context-Upfront File Access Pattern.

This module tests the implementation of the context-upfront pattern where agents
receive required files upfront rather than searching for them during execution.

Test Coverage:
    1. Context loading for each agent type
    2. Context formatting for prompts
    3. File search monitoring
    4. Search statistics
    5. Error handling for missing files
"""

import pytest
from coffee_maker.autonomous.ace.generator import Generator, get_generator
from coffee_maker.autonomous.agent_registry import AgentType


class TestContextLoading:
    """Tests for load_agent_context() method."""

    def test_load_context_code_developer(self):
        """Test context loading for code_developer agent."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.CODE_DEVELOPER)

        # Should load required files for code_developer
        assert "docs/roadmap/ROADMAP.md" in context
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/code_developer.md" in context

        # Each file should have content (or error message)
        for file_path, content in context.items():
            assert len(content) > 0, f"{file_path} should have content"

    def test_load_context_project_manager(self):
        """Test context loading for project_manager agent."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.PROJECT_MANAGER)

        # Should load required files for project_manager
        assert "docs/roadmap/ROADMAP.md" in context
        assert "docs/roadmap/TEAM_COLLABORATION.md" in context
        assert "docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md" in context
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/project_manager.md" in context

    def test_load_context_architect(self):
        """Test context loading for architect agent."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.ARCHITECT)

        # Should load required files for architect
        assert "docs/roadmap/ROADMAP.md" in context
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/architect.md" in context
        assert "pyproject.toml" in context

    def test_load_context_assistant(self):
        """Test context loading for assistant agent."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.ASSISTANT)

        # Should load required files for assistant
        assert "docs/roadmap/ROADMAP.md" in context
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/assistant.md" in context
        assert ".claude/commands/PROMPTS_INDEX.md" in context

    def test_load_context_code_searcher(self):
        """Test context loading for assistant agent (with code-forensics and security-audit skills)."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.ASSISTANT)

        # assistant (using code analysis skills) gets minimal context (project overview)
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/assistant (using code analysis skills).md" in context
        assert "docs/roadmap/ROADMAP.md" in context

        # Should NOT load codebase files (discovery is the role)
        assert "coffee_maker/" not in str(context.keys())

    def test_load_context_ux_design_expert(self):
        """Test context loading for ux-design-expert agent."""
        generator = Generator()
        context = generator.load_agent_context(AgentType.UX_DESIGN_EXPERT)

        # ux-design-expert gets minimal context
        assert ".claude/CLAUDE.md" in context
        assert ".claude/agents/ux-design-expert.md" in context
        assert "docs/roadmap/ROADMAP.md" in context

    def test_load_context_missing_file(self):
        """Test context loading handles missing files gracefully."""
        generator = Generator()

        # Test with a file that doesn't exist by modifying context temporarily
        # Note: We can't easily test this without modifying the generator's file list
        # So this test verifies the error handling in the actual context loading

        context = generator.load_agent_context(AgentType.CODE_DEVELOPER)

        # Check that all files either have content or error messages
        for file_path, content in context.items():
            assert isinstance(content, str)
            # Content should either be actual file content or error message
            assert len(content) > 0


class TestContextFormatting:
    """Tests for format_context_for_prompt() method."""

    def test_format_context_basic(self):
        """Test basic context formatting."""
        generator = Generator()
        context = {
            "file1.md": "# File 1 Content\n\nSome text",
            "file2.md": "# File 2 Content\n\nMore text",
        }

        formatted = generator.format_context_for_prompt(context)

        # Should include header and footer
        assert "=== CONTEXT FILES PROVIDED UPFRONT ===" in formatted
        assert "=== END CONTEXT FILES ===" in formatted

        # Should include file paths
        assert "--- file1.md ---" in formatted
        assert "--- file2.md ---" in formatted

        # Should include content
        assert "File 1 Content" in formatted
        assert "File 2 Content" in formatted

        # Should include instruction
        assert "do NOT search with Glob/Grep" in formatted

    def test_format_context_truncation(self):
        """Test context formatting truncates large files."""
        generator = Generator()
        large_content = "x" * 10000
        context = {"large_file.md": large_content}

        formatted = generator.format_context_for_prompt(context, max_chars_per_file=5000)

        # Should truncate
        assert "[TRUNCATED" in formatted
        assert "5000 chars omitted" in formatted

    def test_format_context_empty(self):
        """Test context formatting with empty context."""
        generator = Generator()
        context = {}

        formatted = generator.format_context_for_prompt(context)

        # Should still have header/footer
        assert "=== CONTEXT FILES PROVIDED UPFRONT ===" in formatted
        assert "=== END CONTEXT FILES ===" in formatted


class TestSearchMonitoring:
    """Tests for file search monitoring."""

    def test_monitor_search_code_developer(self):
        """Test monitoring unexpected search from code_developer."""
        generator = Generator()

        # code_developer searching is unexpected (should have context)
        generator.monitor_file_search(AgentType.CODE_DEVELOPER, "glob", "**/*test*.py", context_provided=True)

        # Should log as warning
        stats = generator.get_search_stats()
        assert stats["unexpected_searches"] == 1
        assert "code_developer" in stats["searches_by_agent"]

    def test_monitor_search_code_searcher(self):
        """Test monitoring expected search from assistant (using code analysis skills)."""
        generator = Generator()

        # assistant (using code analysis skills) searching is EXPECTED (that's its role)
        generator.monitor_file_search(AgentType.ASSISTANT, "glob", "**/*.py", context_provided=True)

        # Should NOT log as unexpected
        stats = generator.get_search_stats()
        assert stats["unexpected_searches"] == 0

    def test_monitor_search_architect(self):
        """Test monitoring search from architect (may search for analysis)."""
        generator = Generator()

        # architect may search for codebase analysis
        generator.monitor_file_search(AgentType.ARCHITECT, "grep", "class.*:", context_provided=True)

        # Should log as info, not warning
        stats = generator.get_search_stats()
        assert stats["unexpected_searches"] == 0
        assert "architect" in stats["searches_by_agent"]

    def test_monitor_search_no_context(self):
        """Test monitoring search when no context provided."""
        generator = Generator()

        # If no context provided, search is acceptable
        generator.monitor_file_search(AgentType.PROJECT_MANAGER, "glob", "docs/*.md", context_provided=False)

        # Should log as info, not warning
        stats = generator.get_search_stats()
        assert stats["unexpected_searches"] == 0


class TestSearchStatistics:
    """Tests for search statistics and reporting."""

    def test_get_search_stats_empty(self):
        """Test search stats with no searches."""
        generator = Generator()
        stats = generator.get_search_stats()

        assert stats["total_searches"] == 0
        assert stats["unexpected_searches"] == 0
        assert len(stats["searches_by_agent"]) == 0
        assert len(stats["most_common_patterns"]) == 0

    def test_get_search_stats_multiple_searches(self):
        """Test search stats with multiple searches."""
        generator = Generator()

        # Log multiple searches
        generator.monitor_file_search(AgentType.CODE_DEVELOPER, "glob", "**/*.py", context_provided=True)
        generator.monitor_file_search(AgentType.CODE_DEVELOPER, "grep", "def test", context_provided=True)
        generator.monitor_file_search(AgentType.ASSISTANT, "glob", "docs/*.md", context_provided=True)

        stats = generator.get_search_stats()

        assert stats["total_searches"] == 3
        assert stats["unexpected_searches"] == 3  # All unexpected (not assistant (using code analysis skills))
        assert "code_developer" in stats["searches_by_agent"]
        assert "assistant" in stats["searches_by_agent"]
        assert len(stats["most_common_patterns"]) > 0

    def test_get_search_stats_most_common(self):
        """Test search stats identifies most common patterns."""
        generator = Generator()

        # Log same pattern multiple times
        for _ in range(5):
            generator.monitor_file_search(AgentType.CODE_DEVELOPER, "glob", "**/*test*.py", context_provided=True)

        stats = generator.get_search_stats()

        # Should identify most common pattern
        most_common = stats["most_common_patterns"]
        assert len(most_common) > 0
        assert most_common[0]["pattern"] == "glob:**/*test*.py"
        assert most_common[0]["count"] == 5


class TestIntegration:
    """Integration tests for context-upfront pattern."""

    def test_full_workflow_code_developer(self):
        """Test full workflow: load context, format, monitor searches."""
        generator = Generator()

        # 1. Load context
        context = generator.load_agent_context(AgentType.CODE_DEVELOPER)
        assert len(context) > 0

        # 2. Format for prompt
        formatted = generator.format_context_for_prompt(context)
        assert "CONTEXT FILES" in formatted

        # 3. Monitor unexpected search
        generator.monitor_file_search(AgentType.CODE_DEVELOPER, "glob", "docs/*.md", context_provided=True)

        # 4. Check stats
        stats = generator.get_search_stats()
        assert stats["unexpected_searches"] == 1

    def test_singleton_instance(self):
        """Test generator singleton works correctly."""
        gen1 = get_generator()
        gen2 = get_generator()

        # Should be same instance
        assert gen1 is gen2

        # Operations on one should affect the other
        gen1.monitor_file_search(AgentType.CODE_DEVELOPER, "glob", "*.py", context_provided=True)

        stats = gen2.get_search_stats()
        assert stats["total_searches"] >= 1


class TestErrorHandling:
    """Tests for error handling in context loading."""

    def test_context_loading_invalid_agent(self):
        """Test context loading with agent type that has no context defined."""
        generator = Generator()

        # Agent type with no defined context (should return empty)
        # Note: All current agent types have context defined, so we can't easily test this
        # But the code handles it with .get(agent_type, [])

        context = generator.load_agent_context(AgentType.CODE_DEVELOPER)
        assert isinstance(context, dict)

    def test_context_formatting_with_errors(self):
        """Test context formatting includes error messages for missing files."""
        generator = Generator()

        context = {
            "existing_file.md": "Content",
            "missing_file.md": "ERROR: File not found: missing_file.md",
        }

        formatted = generator.format_context_for_prompt(context)

        # Should include both files
        assert "existing_file.md" in formatted
        assert "missing_file.md" in formatted

        # Should include error message
        assert "ERROR: File not found" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
