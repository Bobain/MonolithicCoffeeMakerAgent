# SPEC-059: Chat Interface Command Testing

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 3.1)
**Priority**: MEDIUM
**Impact**: MEDIUM (Quality)

---

## Problem Statement

### Current State
Chat interface command parsing and execution lacks comprehensive test coverage:
- Command parsing logic (`_parse_command`) has basic tests only
- Error handling for invalid commands untested
- Help text generation uncovered
- Command validation missing tests

### code-searcher Finding
> **Test Coverage Gaps: Chat Interface Commands**
> - Location: `coffee_maker/cli/chat_interface.py`
> - Missing Coverage: Command parsing, validation, error paths
> - Effort: 6 hours
> - Impact: MEDIUM (better command reliability)

### Why This Matters
- Invalid commands crash chat session
- Users get cryptic error messages
- Hard to add new commands safely
- Regression risk when refactoring

---

## Proposed Solution

Add 10 targeted tests for chat command handling:

1. **Command Parsing** (3 tests)
   - Simple commands (`/help`)
   - Commands with arguments (`/view PRIORITY 5`)
   - Invalid command formats

2. **Command Validation** (3 tests)
   - Valid vs invalid command names
   - Argument count validation
   - Argument type validation

3. **Error Handling** (2 tests)
   - Unknown commands
   - Malformed arguments

4. **Help System** (2 tests)
   - Generate help text
   - Command-specific help

---

## Component Design

### New Test File

**`tests/unit/cli/test_chat_commands.py`**:

```python
class TestChatCommandParsing:
    """Test command parsing logic."""

    def test_parse_simple_command(self):
        """Test parsing command without arguments."""
        chat = ChatSession(mock_ai, mock_editor)

        cmd, args = chat._parse_command("/help")

        assert cmd == "help"
        assert args == []

    def test_parse_command_with_args(self):
        """Test parsing command with arguments."""
        chat = ChatSession(mock_ai, mock_editor)

        cmd, args = chat._parse_command("/view PRIORITY 5")

        assert cmd == "view"
        assert args == ["PRIORITY", "5"]

    def test_parse_invalid_command_format(self):
        """Test parsing malformed command."""
        chat = ChatSession(mock_ai, mock_editor)

        with pytest.raises(ValueError):
            chat._parse_command("not a command")


class TestChatCommandValidation:
    """Test command validation."""

    def test_validate_known_command(self):
        """Test validation accepts known commands."""
        chat = ChatSession(mock_ai, mock_editor)

        is_valid = chat._validate_command("help")

        assert is_valid is True

    def test_validate_unknown_command(self):
        """Test validation rejects unknown commands."""
        chat = ChatSession(mock_ai, mock_editor)

        is_valid = chat._validate_command("invalid")

        assert is_valid is False

    def test_validate_command_arg_count(self):
        """Test validation checks argument count."""
        chat = ChatSession(mock_ai, mock_editor)

        # /view requires 1 argument
        with pytest.raises(ValueError):
            chat._validate_command_args("view", [])


class TestChatErrorHandling:
    """Test command error handling."""

    def test_unknown_command_error_message(self):
        """Test error message for unknown command."""
        chat = ChatSession(mock_ai, mock_editor)

        result = chat._handle_command("invalid", [])

        assert "unknown command" in result.lower()
        assert "invalid" in result

    def test_malformed_args_error_message(self):
        """Test error message for malformed arguments."""
        chat = ChatSession(mock_ai, mock_editor)

        result = chat.cmd_view(["invalid arg"])

        assert "invalid" in result.lower()


class TestChatHelpSystem:
    """Test help system."""

    def test_generate_help_text(self):
        """Test help text generation."""
        chat = ChatSession(mock_ai, mock_editor)

        help_text = chat.cmd_help([])

        assert "/help" in help_text
        assert "/view" in help_text
        assert "/add" in help_text

    def test_command_specific_help(self):
        """Test command-specific help."""
        chat = ChatSession(mock_ai, mock_editor)

        help_text = chat.cmd_help(["view"])

        assert "view" in help_text.lower()
        assert "usage" in help_text.lower()
```

---

## Technical Details

### Test Coverage Goals
- `_parse_command`: 100% (from ~50%)
- `_validate_command`: 100% (from ~30%)
- Command error handling: 90% (from ~40%)
- Help system: 95% (from ~60%)

### Test Infrastructure
```python
@pytest.fixture
def mock_chat_session():
    """Create mock chat session for testing."""
    ai = Mock(spec=AIService)
    editor = Mock(spec=RoadmapEditor)
    return ChatSession(ai, editor)
```

---

## Rollout Plan

### Week 1: Implementation (6 hours)
- **Day 1**: Command parsing tests (2 hours)
- **Day 2**: Validation tests (2 hours)
- **Day 3**: Error handling + help tests (2 hours)

---

## Success Criteria

### Quantitative
- ✅ 10 new tests added
- ✅ Command parsing coverage ≥95%
- ✅ Command validation coverage ≥95%
- ✅ Error handling coverage ≥90%

### Qualitative
- ✅ Better command reliability
- ✅ Clear error messages
- ✅ Easier to add new commands

---

## Related Work

### Related Specs
- **SPEC-056**: ChatSession breakdown (will make testing easier)
- **SPEC-052**: Error handling (will standardize error messages)

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 6 hours
**Actual Effort**: TBD
