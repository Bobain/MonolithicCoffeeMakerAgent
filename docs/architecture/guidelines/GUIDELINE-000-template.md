# GUIDELINE-XXX: [Title]

**Category**: Design Pattern | Best Practice | Anti-Pattern | Code Standard

**Applies To**: [What part of codebase - e.g., "All service classes", "CLI modules", "Test files"]

**Author**: architect agent

**Date Created**: YYYY-MM-DD

**Last Updated**: YYYY-MM-DD

**Status**: Draft | Active | Deprecated

**Related ADRs**: [Link to relevant ADRs]

**Related Specs**: [Link to technical specs if applicable]

---

## Overview

Brief 1-2 sentence summary of what this guideline covers.

**Example**:
```
This guideline describes how to implement error handling in service classes
using custom exceptions and defensive programming techniques. It ensures
consistent error handling across the codebase.
```

---

## When to Use

When should developers use this pattern/practice?

**Example**:
```
Use this error handling pattern when:
- Implementing service classes that interact with external systems
- Handling user input that could be invalid
- Performing operations that could fail (file I/O, network calls, database)
- Any code where you need to provide meaningful error messages to users
```

---

## When NOT to Use

When should developers avoid this pattern/practice?

**Example**:
```
Do NOT use this error handling pattern when:
- Inside data classes (they should be simple)
- In test fixtures (use pytest's built-in exception handling)
- For expected flow control (use if/else, not exceptions)
- When performance is critical and errors are rare (use error codes)
```

---

## The Pattern

### Explanation

Explain the pattern in detail.

**Example**:
```
Our error handling pattern uses:

1. **Custom Exception Hierarchy**: All exceptions inherit from base exception
2. **Defensive Programming**: Validate inputs early, fail fast
3. **Contextual Information**: Include relevant data in exception messages
4. **Graceful Degradation**: Catch exceptions at service boundaries
5. **User-Friendly Messages**: Translate technical errors to user language
6. **Logging**: Log all exceptions with context for debugging

This approach provides:
- Consistent error handling across codebase
- Helpful error messages for debugging
- User-friendly error messages for CLI/API
- Traceable errors via logging
```

### Principles

Key principles behind this pattern:

1. **Principle 1**: Explanation
2. **Principle 2**: Explanation
3. **Principle 3**: Explanation

**Example**:
```
1. **Fail Fast**: Validate inputs at function entry, don't wait for errors later
2. **Be Specific**: Use specific exception types (FileNotFoundError vs Exception)
3. **Add Context**: Include relevant data in error messages
4. **Log Everything**: Log exceptions with full context for debugging
5. **User-Friendly**: Translate technical errors to readable messages
```

---

## Implementation

### Step-by-Step Guide

1. **Step 1**: Description
   ```python
   # Code example
   ```

2. **Step 2**: Description
   ```python
   # Code example
   ```

3. **Step 3**: Description
   ```python
   # Code example
   ```

**Example**:
```
### Step-by-Step Guide

1. **Define Custom Exceptions**: Create exception hierarchy in exceptions.py
   ```python
   # coffee_maker/exceptions.py
   class CoffeeMakerError(Exception):
       """Base exception for all coffee maker errors."""
       pass

   class RoadmapError(CoffeeMakerError):
       """Errors related to ROADMAP operations."""
       pass

   class ValidationError(CoffeeMakerError):
       """Errors related to input validation."""
       pass
   ```

2. **Validate Inputs**: Check inputs at function entry
   ```python
   def get_priority(priority_id: str) -> Priority:
       """Get priority from ROADMAP."""
       # Validate input
       if not priority_id:
           raise ValidationError("priority_id cannot be empty")

       if not priority_id.startswith("PRIORITY "):
           raise ValidationError(f"Invalid priority_id: {priority_id}")

       # ... rest of implementation
   ```

3. **Provide Context**: Include relevant data in exceptions
   ```python
   def update_status(priority_id: str, new_status: str) -> None:
       """Update priority status."""
       if new_status not in VALID_STATUSES:
           raise ValidationError(
               f"Invalid status '{new_status}'. "
               f"Valid statuses: {', '.join(VALID_STATUSES)}"
           )

       # ... rest of implementation
   ```

4. **Catch at Boundaries**: Catch exceptions at service layer
   ```python
   def cli_update_status(priority_id: str, new_status: str) -> None:
       """CLI command to update status."""
       try:
           roadmap_service.update_status(priority_id, new_status)
           print(f"✅ Updated {priority_id} to {new_status}")
       except ValidationError as e:
           print(f"❌ Error: {e}")
           sys.exit(1)
       except RoadmapError as e:
           print(f"❌ ROADMAP error: {e}")
           logger.exception("Failed to update status")
           sys.exit(1)
   ```

5. **Log Exceptions**: Log with context for debugging
   ```python
   def update_status(priority_id: str, new_status: str) -> None:
       """Update priority status."""
       try:
           # ... implementation
       except Exception as e:
           logger.exception(
               "Failed to update status",
               extra={
                   "priority_id": priority_id,
                   "new_status": new_status,
                   "traceback": traceback.format_exc()
               }
           )
           raise RoadmapError(f"Failed to update {priority_id}") from e
   ```
```

### Code Examples

#### Good Example

```python
# Show CORRECT implementation with explanation
```

**Why This is Good**:
- Reason 1
- Reason 2
- Reason 3

**Example**:
```python
#### Good Example: Proper Error Handling

```python
def load_roadmap(filepath: str) -> Roadmap:
    """
    Load ROADMAP from file.

    Args:
        filepath: Path to ROADMAP.md file

    Returns:
        Parsed Roadmap object

    Raises:
        ValidationError: If filepath is invalid
        RoadmapError: If file cannot be loaded or parsed
    """
    # Validate input
    if not filepath:
        raise ValidationError("filepath cannot be empty")

    if not filepath.endswith(".md"):
        raise ValidationError(f"filepath must be .md file: {filepath}")

    # Load file
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise RoadmapError(f"ROADMAP file not found: {filepath}")
    except PermissionError:
        raise RoadmapError(f"Permission denied reading: {filepath}")
    except Exception as e:
        logger.exception("Failed to load ROADMAP", extra={"filepath": filepath})
        raise RoadmapError(f"Failed to load {filepath}") from e

    # Parse content
    try:
        roadmap = parse_roadmap(content)
    except Exception as e:
        logger.exception("Failed to parse ROADMAP", extra={"filepath": filepath})
        raise RoadmapError(f"Invalid ROADMAP format in {filepath}") from e

    return roadmap
```

**Why This is Good**:
- Validates inputs early (fail fast)
- Uses specific exception types (ValidationError vs RoadmapError)
- Provides contextual error messages
- Logs exceptions with context
- Uses exception chaining (from e) to preserve stack trace
- Documents exceptions in docstring
```

#### Bad Example

```python
# Show INCORRECT implementation with explanation
```

**Why This is Bad**:
- Problem 1
- Problem 2
- Problem 3

**How to Fix**: Explanation of how to fix it

**Example**:
```python
#### Bad Example: Poor Error Handling

```python
def load_roadmap(filepath):
    # ❌ No type hints
    # ❌ No docstring
    # ❌ No input validation
    f = open(filepath, "r")  # ❌ No error handling
    content = f.read()
    f.close()  # ❌ Should use context manager

    roadmap = parse_roadmap(content)  # ❌ No error handling
    return roadmap
```

**Why This is Bad**:
- No type hints (unclear what types expected)
- No docstring (no documentation)
- No input validation (crashes with None or invalid input)
- No error handling (crashes with unclear errors)
- No context manager (file not closed on error)
- No logging (hard to debug failures)
- Bare except would swallow all errors

**How to Fix**:
- Add type hints and docstring
- Validate input at function entry
- Use context manager for file operations
- Catch specific exceptions and provide context
- Log errors with relevant data
- Use exception chaining to preserve stack trace
```

#### Edge Cases

Examples of edge cases to handle:

```python
# Edge case 1
```

```python
# Edge case 2
```

**Example**:
```python
#### Edge Cases to Handle

```python
# Edge Case 1: Empty file
try:
    roadmap = load_roadmap("empty.md")
except RoadmapError as e:
    # Should provide clear error: "ROADMAP is empty"
    pass

# Edge Case 2: File exists but has invalid format
try:
    roadmap = load_roadmap("invalid.md")
except RoadmapError as e:
    # Should provide clear error about what's invalid
    pass

# Edge Case 3: File path with special characters
try:
    roadmap = load_roadmap("path/with spaces/roadmap.md")
except RoadmapError as e:
    # Should handle gracefully
    pass

# Edge Case 4: Concurrent access (file changed while reading)
try:
    roadmap = load_roadmap("roadmap.md")
except RoadmapError as e:
    # Should retry or provide clear error
    pass
```
```

---

## Testing

### Unit Testing

How to test code using this pattern:

```python
# Test example
```

**Example**:
```python
### Unit Testing Error Handling

```python
# tests/unit/test_roadmap_loader.py
import pytest
from coffee_maker.exceptions import ValidationError, RoadmapError
from coffee_maker.roadmap_loader import load_roadmap

def test_load_roadmap_empty_filepath():
    """Should raise ValidationError for empty filepath."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        load_roadmap("")

def test_load_roadmap_invalid_extension():
    """Should raise ValidationError for non-.md file."""
    with pytest.raises(ValidationError, match="must be .md file"):
        load_roadmap("roadmap.txt")

def test_load_roadmap_file_not_found():
    """Should raise RoadmapError for missing file."""
    with pytest.raises(RoadmapError, match="not found"):
        load_roadmap("nonexistent.md")

def test_load_roadmap_invalid_format(tmp_path):
    """Should raise RoadmapError for invalid ROADMAP format."""
    filepath = tmp_path / "invalid.md"
    filepath.write_text("invalid content")

    with pytest.raises(RoadmapError, match="Invalid ROADMAP format"):
        load_roadmap(str(filepath))

def test_load_roadmap_success(tmp_path):
    """Should successfully load valid ROADMAP."""
    filepath = tmp_path / "roadmap.md"
    filepath.write_text("# ROADMAP\n\n## PRIORITY 1\n...")

    roadmap = load_roadmap(str(filepath))
    assert roadmap is not None
    assert len(roadmap.priorities) > 0
```
```

### Integration Testing

How to test integration with other components:

```python
# Integration test example
```

---

## Common Pitfalls

### Pitfall 1: [Name]

**Description**: What is the pitfall?

**Example**:
```python
# Bad code demonstrating the pitfall
```

**Solution**:
```python
# Good code showing how to avoid it
```

**Example**:
```
### Pitfall 1: Catching Too Broad Exceptions

**Description**: Catching `Exception` or `BaseException` hides bugs

**Example**:
```python
# ❌ Bad: Catches ALL exceptions including KeyboardInterrupt
try:
    result = dangerous_operation()
except Exception:
    return None  # Swallows real errors!
```

**Solution**:
```python
# ✅ Good: Catch specific exceptions
try:
    result = dangerous_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise ValidationError(f"Invalid input") from e
except IOError as e:
    logger.error(f"I/O error: {e}")
    raise RoadmapError(f"File operation failed") from e
# Let other exceptions propagate
```
```

### Pitfall 2: [Name]

**Description**: What is the pitfall?

**Example**:
```python
# Bad code
```

**Solution**:
```python
# Good code
```

---

## Performance Considerations

**Performance Impact**: High | Medium | Low

**Description**: How does this pattern impact performance?

**Optimization Tips**:
- Tip 1
- Tip 2
- Tip 3

**Example**:
```
**Performance Impact**: Low

**Description**:
Exception handling has minimal performance impact in Python when exceptions
are rare. The cost of try/except blocks is negligible when no exception is
raised. Only when exceptions are actually thrown do you pay a performance
cost (stack unwinding, traceback generation).

**Optimization Tips**:
- Don't use exceptions for normal flow control (use if/else instead)
- Validate inputs early to fail fast (cheaper than catching exceptions later)
- Cache validation results if same inputs are used repeatedly
- Use `pytest.raises()` in tests instead of try/except
- Profile code to identify exception hotspots if performance is critical
```

---

## Related Patterns

### Related Guideline 1

[Link to GUIDELINE-XXX]

**Relationship**: How is it related?

**Example**:
```
### Related Guideline: GUIDELINE-002-logging-standards

[Link to GUIDELINE-002](./GUIDELINE-002-logging-standards.md)

**Relationship**: Error handling should use structured logging to capture
context. See GUIDELINE-002 for how to log exceptions with relevant data.
```

### Related Guideline 2

[Link to GUIDELINE-YYY]

**Relationship**: How is it related?

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: [Name]

**Description**: What is the anti-pattern?

**Why It's Bad**: Explanation

**Example**:
```python
# Bad code
```

**Instead Do**:
```python
# Good code
```

**Example**:
```
### Anti-Pattern 1: Silent Failures

**Description**: Catching exceptions and doing nothing

**Why It's Bad**:
- Hides bugs and makes debugging impossible
- Users don't know operations failed
- System state becomes inconsistent

**Example**:
```python
# ❌ Anti-pattern: Silent failure
try:
    save_to_database(data)
except Exception:
    pass  # Swallows error, user thinks save succeeded!
```

**Instead Do**:
```python
# ✅ Good: Log and re-raise or provide feedback
try:
    save_to_database(data)
except DatabaseError as e:
    logger.exception("Failed to save to database", extra={"data": data})
    raise RoadmapError("Failed to save changes") from e
```
```

### Anti-Pattern 2: [Name]

**Description**: What is the anti-pattern?

**Why It's Bad**: Explanation

**Example**:
```python
# Bad code
```

**Instead Do**:
```python
# Good code
```

---

## Checklist

When implementing this pattern, verify:

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
- [ ] Item 4
- [ ] Item 5

**Example**:
```
## Checklist for Error Handling

When implementing error handling, verify:

- [ ] All inputs are validated at function entry
- [ ] Custom exception types are used (not generic Exception)
- [ ] Error messages include relevant context
- [ ] Exceptions are caught at service boundaries
- [ ] All exceptions are logged with context
- [ ] User-facing errors are translated to friendly messages
- [ ] Exception chaining is used (from e) to preserve stack traces
- [ ] Docstrings document what exceptions are raised
- [ ] Unit tests cover all error cases
- [ ] Edge cases are handled gracefully
```

---

## References

Links to relevant resources:

- [Link to documentation]
- [Link to article]
- [Link to code examples]

**Example**:
```
## References

- Python Exception Handling: https://docs.python.org/3/tutorial/errors.html
- PEP 3134 - Exception Chaining: https://www.python.org/dev/peps/pep-3134/
- Defensive Programming: https://en.wikipedia.org/wiki/Defensive_programming
- ADR-003: Custom Exception Hierarchy
- SPEC-002: Error Handling Architecture
```

---

## Change Log

Track changes to this guideline:

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Created | architect |
| YYYY-MM-DD | Added edge cases section | architect |
| YYYY-MM-DD | Updated based on code review feedback | architect |

---

## Notes

Any additional context or information:

**Example**:
```
## Notes

- This guideline supersedes the old error handling approach (bare try/except)
- All new code should follow this pattern
- Existing code will be refactored gradually (tracked in PRIORITY 10)
- If you find code not following this pattern, create a tech debt ticket
- Questions? Contact architect agent or ask in #architecture channel
```

---

**Remember**: Guidelines are meant to help, not hinder. If you find a case where this guideline doesn't fit, discuss with the team and consider creating an exception or updating the guideline. Always prioritize clarity and maintainability!
