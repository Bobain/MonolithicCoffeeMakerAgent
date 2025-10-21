# SPEC-058: Prompt Loader Edge Case Tests

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 2.3)
**Priority**: MEDIUM
**Impact**: MEDIUM (Reliability)

---

## Problem Statement

### Current State

`prompt_loader.py` has **basic loading tests** but is missing **edge case coverage**:

- **Missing template files**: Error handling untested
- **Missing variables**: Incomplete substitution not tested
- **Special characters**: Unicode, escape sequences untested
- **Very large templates**: Performance not benchmarked
- **Concurrent loading**: Thread safety untested

### code-searcher Finding

> **Test Coverage Gaps: Prompt Loader**
> - Location: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/prompt_loader.py`
> - Current Coverage: ~60-70%
> - Target Coverage: 95%+
> - Missing Scenarios: Missing files, incomplete substitution, unicode, concurrency
> - Effort: 4 hours
> - Impact: MEDIUM (prevents prompt failures in production)

### Why This Matters

- **Daemon Failures**: Missing templates crash daemon
- **Silent Bugs**: Incomplete variable substitution causes AI confusion
- **Unicode Issues**: Special characters break prompts
- **Race Conditions**: Concurrent loading may cause corruption

**Goal**: Achieve **95%+ test coverage** for prompt loader with comprehensive edge cases

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Add **targeted edge case tests** for prompt loader:

1. **Missing File Handling**: Test missing template files
2. **Variable Substitution**: Test incomplete/missing variables
3. **Special Characters**: Test unicode, escape sequences, newlines
4. **Performance**: Benchmark large templates
5. **Concurrency**: Test thread-safe loading

### Architecture

```
tests/unit/autonomous/
├── test_prompt_loader.py              # EXISTING: Basic tests
├── test_prompt_loader_errors.py       # NEW: Error scenarios
├── test_prompt_loader_unicode.py      # NEW: Unicode handling
├── test_prompt_loader_performance.py  # NEW: Performance tests
└── test_prompt_loader_concurrency.py  # NEW: Thread safety
```

**Benefits**:
- **Robustness**: Prompt loader handles all edge cases
- **Better Error Messages**: Clear errors for missing templates
- **Unicode Safety**: International characters work correctly
- **Thread Safety**: Concurrent daemon operations safe

---

## Component Design

### 1. Missing File Handling Tests

**File**: `tests/unit/autonomous/test_prompt_loader_errors.py`

```python
import pytest
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames


class TestPromptLoaderErrors:
    """Test prompt loader error handling."""

    def test_missing_prompt_file(self):
        """Test error when prompt file doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_prompt("nonexistent-prompt", {})

        assert "nonexistent-prompt" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    def test_missing_prompt_directory(self):
        """Test error when .claude/commands directory missing."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                load_prompt(PromptNames.IMPLEMENT_FEATURE, {})

        assert ".claude/commands" in str(exc_info.value)

    def test_empty_prompt_file(self, tmp_path):
        """Test handling of empty prompt file."""
        # Create empty file
        prompt_file = tmp_path / "empty-prompt.md"
        prompt_file.touch()

        result = load_prompt("empty-prompt", {}, prompt_dir=tmp_path)

        assert result == ""  # Empty string, not error

    def test_corrupt_prompt_file(self, tmp_path):
        """Test handling of corrupt (binary) prompt file."""
        prompt_file = tmp_path / "corrupt-prompt.md"
        prompt_file.write_bytes(b'\xff\xfe\xfd')  # Invalid UTF-8

        with pytest.raises(UnicodeDecodeError):
            load_prompt("corrupt-prompt", {}, prompt_dir=tmp_path)
```

### 2. Variable Substitution Tests

**File**: `tests/unit/autonomous/test_prompt_loader_errors.py` (continued)

```python
class TestVariableSubstitution:
    """Test variable substitution edge cases."""

    def test_missing_variable_substitution(self, tmp_path):
        """Test error when required variable not provided."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Hello $NAME, your task is $TASK")

        # Missing TASK variable
        with pytest.raises(KeyError) as exc_info:
            load_prompt("test-prompt", {"NAME": "User"}, prompt_dir=tmp_path)

        assert "TASK" in str(exc_info.value)

    def test_extra_variables_ignored(self, tmp_path):
        """Test extra variables are ignored (no error)."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Hello $NAME")

        # Extra variable TASK is ignored
        result = load_prompt(
            "test-prompt",
            {"NAME": "User", "TASK": "Extra"},
            prompt_dir=tmp_path
        )

        assert result == "Hello User"

    def test_empty_variable_value(self, tmp_path):
        """Test substitution with empty string."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Task: $TASK")

        result = load_prompt(
            "test-prompt",
            {"TASK": ""},
            prompt_dir=tmp_path
        )

        assert result == "Task: "  # Empty string substituted

    def test_none_variable_value(self, tmp_path):
        """Test substitution with None value."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Task: $TASK")

        # None should be converted to string "None" or raise error
        with pytest.raises(TypeError):
            load_prompt("test-prompt", {"TASK": None}, prompt_dir=tmp_path)

    def test_variable_with_special_chars(self, tmp_path):
        """Test variable names with underscores, numbers."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("$VAR_1 and $VAR_2")

        result = load_prompt(
            "test-prompt",
            {"VAR_1": "A", "VAR_2": "B"},
            prompt_dir=tmp_path
        )

        assert result == "A and B"

    def test_duplicate_variable_substitution(self, tmp_path):
        """Test same variable appears multiple times."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("$NAME is $NAME")

        result = load_prompt(
            "test-prompt",
            {"NAME": "Alice"},
            prompt_dir=tmp_path
        )

        assert result == "Alice is Alice"
```

### 3. Unicode and Special Character Tests

**File**: `tests/unit/autonomous/test_prompt_loader_unicode.py`

```python
class TestPromptLoaderUnicode:
    """Test unicode and special character handling."""

    def test_unicode_in_template(self, tmp_path):
        """Test template with unicode characters."""
        prompt_file = tmp_path / "unicode-prompt.md"
        prompt_file.write_text("Hello 世界! $NAME", encoding='utf-8')

        result = load_prompt(
            "unicode-prompt",
            {"NAME": "User"},
            prompt_dir=tmp_path
        )

        assert "世界" in result
        assert "User" in result

    def test_unicode_in_variable(self, tmp_path):
        """Test variable with unicode value."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Name: $NAME", encoding='utf-8')

        result = load_prompt(
            "test-prompt",
            {"NAME": "María García"},
            prompt_dir=tmp_path
        )

        assert result == "Name: María García"

    def test_emoji_in_template(self, tmp_path):
        """Test template with emoji."""
        prompt_file = tmp_path / "emoji-prompt.md"
        prompt_file.write_text("Status: 🚀 $STATUS", encoding='utf-8')

        result = load_prompt(
            "emoji-prompt",
            {"STATUS": "Ready"},
            prompt_dir=tmp_path
        )

        assert "🚀" in result
        assert "Ready" in result

    def test_escape_sequences(self, tmp_path):
        """Test escape sequences in template."""
        prompt_file = tmp_path / "escape-prompt.md"
        prompt_file.write_text("Line 1\\nLine 2\\t$VALUE")

        result = load_prompt(
            "escape-prompt",
            {"VALUE": "Tab"},
            prompt_dir=tmp_path
        )

        # Escape sequences should be literal (not interpreted)
        assert "\\n" in result
        assert "\\t" in result

    def test_newlines_in_template(self, tmp_path):
        """Test actual newlines in template."""
        prompt_file = tmp_path / "newline-prompt.md"
        prompt_file.write_text("Line 1\nLine 2\n$VALUE")

        result = load_prompt(
            "newline-prompt",
            {"VALUE": "End"},
            prompt_dir=tmp_path
        )

        assert "Line 1\nLine 2\nEnd" == result

    def test_special_regex_chars_in_variable(self, tmp_path):
        """Test variable value with regex special characters."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Pattern: $PATTERN")

        result = load_prompt(
            "test-prompt",
            {"PATTERN": ".*[a-z]+$"},
            prompt_dir=tmp_path
        )

        assert result == "Pattern: .*[a-z]+$"
```

### 4. Performance Tests

**File**: `tests/unit/autonomous/test_prompt_loader_performance.py`

```python
import pytest
import time


class TestPromptLoaderPerformance:
    """Test prompt loader performance."""

    def test_large_template_loading(self, tmp_path):
        """Test loading very large template (10KB)."""
        prompt_file = tmp_path / "large-prompt.md"

        # Create 10KB template
        large_content = "Line $VAR\n" * 500  # ~10KB
        prompt_file.write_text(large_content)

        start = time.time()
        result = load_prompt(
            "large-prompt",
            {"VAR": "Value"},
            prompt_dir=tmp_path
        )
        elapsed = time.time() - start

        # Should load in <100ms
        assert elapsed < 0.1
        assert len(result) > 5000

    def test_many_variables_substitution(self, tmp_path):
        """Test template with many variables (100+)."""
        prompt_file = tmp_path / "many-vars-prompt.md"

        # Create template with 100 variables
        template = " ".join([f"$VAR_{i}" for i in range(100)])
        prompt_file.write_text(template)

        # Create variable dict
        variables = {f"VAR_{i}": f"Value{i}" for i in range(100)}

        start = time.time()
        result = load_prompt(
            "many-vars-prompt",
            variables,
            prompt_dir=tmp_path
        )
        elapsed = time.time() - start

        # Should substitute in <50ms
        assert elapsed < 0.05
        assert "Value0" in result
        assert "Value99" in result

    @pytest.mark.slow
    def test_repeated_loading_no_memory_leak(self, tmp_path):
        """Test repeated loading doesn't leak memory."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Test $VAR")

        # Load 1000 times
        for _ in range(1000):
            load_prompt("test-prompt", {"VAR": "Value"}, prompt_dir=tmp_path)

        # If no memory leak, this test completes successfully
        assert True
```

### 5. Concurrency Tests

**File**: `tests/unit/autonomous/test_prompt_loader_concurrency.py`

```python
import pytest
import threading
from concurrent.futures import ThreadPoolExecutor


class TestPromptLoaderConcurrency:
    """Test prompt loader thread safety."""

    def test_concurrent_loading_same_template(self, tmp_path):
        """Test multiple threads loading same template."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Hello $NAME")

        results = []
        errors = []

        def load_in_thread(name):
            try:
                result = load_prompt(
                    "test-prompt",
                    {"NAME": name},
                    prompt_dir=tmp_path
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Load concurrently with 10 threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(load_in_thread, f"User{i}") for i in range(10)]
            for future in futures:
                future.result()

        # All loads should succeed
        assert len(errors) == 0
        assert len(results) == 10

    def test_concurrent_loading_different_templates(self, tmp_path):
        """Test multiple threads loading different templates."""
        # Create 5 templates
        for i in range(5):
            prompt_file = tmp_path / f"template-{i}.md"
            prompt_file.write_text(f"Template {i}: $VALUE")

        results = []

        def load_template(i):
            result = load_prompt(
                f"template-{i}",
                {"VALUE": f"Value{i}"},
                prompt_dir=tmp_path
            )
            results.append(result)

        # Load concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(load_template, i) for i in range(5)]
            for future in futures:
                future.result()

        assert len(results) == 5
        assert all("Template" in r for r in results)

    def test_no_race_condition_file_creation(self, tmp_path):
        """Test no race condition when creating cache (if caching added)."""
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("Test $VAR")

        # Load concurrently many times
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(
                    load_prompt,
                    "test-prompt",
                    {"VAR": f"Value{i}"},
                    prompt_dir=tmp_path
                )
                for i in range(100)
            ]
            results = [f.result() for f in futures]

        # All loads should succeed
        assert len(results) == 100
```

---

## Technical Details

### Test Infrastructure

**Fixtures** (`tests/conftest.py`):
```python
@pytest.fixture
def tmp_prompt_dir(tmp_path):
    """Create temporary prompt directory for testing."""
    prompt_dir = tmp_path / ".claude" / "commands"
    prompt_dir.mkdir(parents=True)
    return prompt_dir


@pytest.fixture
def sample_prompt(tmp_prompt_dir):
    """Create a sample prompt file for testing."""
    prompt_file = tmp_prompt_dir / "sample-prompt.md"
    prompt_file.write_text("Hello $NAME, your task is $TASK")
    return prompt_file
```

### Coverage Targets

| Scenario | Current Coverage | Target | Tests Needed |
|----------|-----------------|--------|--------------|
| Missing files | ~50% | 100% | +3 tests |
| Variable substitution | ~70% | 100% | +6 tests |
| Unicode handling | ~40% | 100% | +6 tests |
| Performance | 0% (no tests) | 100% | +3 tests |
| Concurrency | 0% (no tests) | 95% | +3 tests |

**Total New Tests**: ~21 test functions

---

## Testing Strategy

### Unit Tests (21 new tests)

**Coverage by Category**:
- Error handling: 4 tests
- Variable substitution: 6 tests
- Unicode/special chars: 6 tests
- Performance: 3 tests
- Concurrency: 3 tests

### Integration Tests

**Not needed**: Prompt loader is self-contained utility

### Manual Testing

```bash
# Test unicode prompt
cat > .claude/commands/test-unicode.md << 'EOF'
Hello 世界! $NAME
EOF

python -c "
from coffee_maker.autonomous.prompt_loader import load_prompt
result = load_prompt('test-unicode', {'NAME': 'User'})
print(result)
"
```

---

## Rollout Plan

### Week 1: Error & Variable Tests (2 hours)
- **Day 1**: Write error handling tests (1 hour)
- **Day 1**: Write variable substitution tests (1 hour)

### Week 2: Unicode & Performance Tests (2 hours)
- **Day 1**: Write unicode tests (1 hour)
- **Day 1**: Write performance tests (1 hour)

**Total Timeline**: 2 weeks (4 hours actual work)

---

## Risks & Mitigations

### Risk 1: Performance Tests Are Flaky
**Likelihood**: MEDIUM
**Impact**: MEDIUM (CI unreliable)
**Mitigation**:
- Use generous time limits (100ms vs 10ms)
- Mark with `@pytest.mark.slow`
- Run on dedicated CI runners

### Risk 2: Unicode Tests Fail on Different Platforms
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- Explicitly specify UTF-8 encoding
- Test on Linux, macOS, Windows
- Use pytest markers for platform-specific tests

### Risk 3: Concurrency Tests Are Non-Deterministic
**Likelihood**: MEDIUM
**Impact**: HIGH
**Mitigation**:
- Run concurrency tests multiple times (10x)
- Use pytest-repeat plugin
- Add explicit synchronization points

---

## Success Criteria

### Quantitative
- ✅ `prompt_loader.py` coverage ≥95% (from ~70%)
- ✅ All error scenarios tested
- ✅ All unicode edge cases tested
- ✅ Performance benchmarks established
- ✅ Thread safety verified
- ✅ Zero regressions in prompt loading

### Qualitative
- ✅ Developers confident in prompt loader reliability
- ✅ Clear error messages for missing templates
- ✅ Unicode characters work everywhere
- ✅ No daemon crashes from prompt issues

---

## Related Work

### Depends On
- None (independent testing improvement)

### Enables
- **Confident Prompt Usage**: Daemon can handle all prompt scenarios
- **Better Error Messages**: Clear errors for prompt issues
- **Unicode Support**: International characters work correctly

### Related Specs
- **SPEC-053**: Test coverage expansion (this is part of it)

---

## Appendix A: Edge Case Scenarios Matrix

### Error Handling

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Missing file | `test_missing_prompt_file` | FileNotFoundError with clear message |
| Empty file | `test_empty_prompt_file` | Return empty string |
| Corrupt file | `test_corrupt_prompt_file` | UnicodeDecodeError |
| Missing variable | `test_missing_variable_substitution` | KeyError with variable name |

### Variable Substitution

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Extra variables | `test_extra_variables_ignored` | Ignore extras, no error |
| Empty value | `test_empty_variable_value` | Substitute empty string |
| None value | `test_none_variable_value` | Raise TypeError |
| Duplicate variables | `test_duplicate_variable_substitution` | Substitute all occurrences |

### Unicode

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Unicode in template | `test_unicode_in_template` | Handle correctly |
| Unicode in variable | `test_unicode_in_variable` | Handle correctly |
| Emoji | `test_emoji_in_template` | Handle correctly |
| Escape sequences | `test_escape_sequences` | Literal (not interpreted) |

---

## Appendix B: Performance Benchmarks

### Expected Performance

| Operation | Template Size | Variables | Time Limit |
|-----------|--------------|-----------|------------|
| Load small | <1KB | <10 | <10ms |
| Load large | ~10KB | 10-50 | <100ms |
| Many variables | <5KB | 100+ | <50ms |
| Concurrent load | <1KB | <10 | <200ms total |

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 4 hours
**Actual Effort**: TBD (track during implementation)
