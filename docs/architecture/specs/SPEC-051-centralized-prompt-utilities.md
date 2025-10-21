# SPEC-051: Centralized Prompt Utilities

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CODE_QUALITY_ANALYSIS_2025-10-17.md (Finding #2)
**Priority**: MEDIUM
**Impact**: MEDIUM (Code Quality, Consistency)

---

## Problem Statement

### Current State
Prompt building logic is **duplicated across multiple files**, resulting in:
- **~150 LOC of duplicated code** across 3+ files
- **Inconsistent truncation logic** (some files use 1500 chars, others vary)
- **Copy-paste maintenance burden** (fix same bug in multiple places)
- **No standardized priority context building**

### code-searcher Finding
> "Code Duplication - Prompt Building
> Pattern: Similar prompt construction patterns across files
> Duplication: ~150 LOC
> Files: daemon_implementation.py, spec_generator.py, ai_service.py
> Recommendation: Extract to shared utility module
> Effort: 2-3 hours
> Impact: MEDIUM (maintenance)"

### Examples of Duplication

**daemon_implementation.py** (line 431):
```python
priority_content = priority.get("content", "")[:1500]
if len(priority.get("content", "")) > 1500:
    priority_content += "..."
```

**spec_generator.py** (similar pattern):
```python
content = priority.get("content", "")
if len(content) > 1500:
    content = content[:1500] + "..."
```

**ai_service.py** (another variation):
```python
truncated = priority["content"][:1500] if len(priority["content"]) > 1500 else priority["content"]
```

**Problems**:
- 3 different implementations of same logic
- Inconsistent variable names
- Different truncation markers ("...", " [truncated]", etc.)
- Hard to change truncation limit globally

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Create **single utility module** (`coffee_maker/utils/prompt_builders.py`) that provides:
1. **Content truncation** (standardized)
2. **Priority context building** (consistent structure)
3. **Template variable generation** (for prompt_loader)

### Architecture

```
coffee_maker/utils/
├── prompt_builders.py          # NEW: Centralized prompt utilities
│   ├── truncate_content()      # Standard truncation
│   ├── build_priority_context() # Priority → template vars
│   ├── build_spec_context()    # Spec → template vars
│   └── build_roadmap_context() # Roadmap → template vars
│
└── (existing utils)
```

**Benefits**:
- **DRY**: Single implementation, used everywhere
- **Consistency**: Same truncation logic across all prompts
- **Maintainability**: Change truncation limit in one place
- **Testability**: Easy to unit test utilities

---

## Component Design

### 1. Core Truncation Utility

```python
def truncate_content(
    content: str,
    max_chars: int = 1500,
    truncation_marker: str = "...",
    preserve_sentences: bool = True
) -> str:
    """
    Truncate content to specified length with optional sentence preservation.

    Args:
        content: Text to truncate
        max_chars: Maximum characters (default: 1500)
        truncation_marker: String to append when truncated (default: "...")
        preserve_sentences: If True, try to end at sentence boundary (default: True)

    Returns:
        Truncated content with marker if needed

    Examples:
        >>> truncate_content("Short text", max_chars=1500)
        "Short text"

        >>> truncate_content("Very long text..." * 200, max_chars=100)
        "Very long text...Very long text...Very long text...Very long..."

        >>> truncate_content("Sentence one. Sentence two.", max_chars=15, preserve_sentences=True)
        "Sentence one..."
    """
    if len(content) <= max_chars:
        return content

    truncated = content[:max_chars]

    if preserve_sentences:
        # Try to end at last sentence boundary (., !, ?)
        last_period = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        if last_period > max_chars * 0.5:  # Only if >50% of max_chars
            truncated = truncated[:last_period + 1]

    return truncated.rstrip() + truncation_marker
```

### 2. Priority Context Builder

```python
def build_priority_context(
    priority: dict,
    max_content_chars: int = 1500,
    include_metadata: bool = True
) -> dict:
    """
    Build standardized priority context for prompt templates.

    Args:
        priority: Priority dictionary from ROADMAP parsing
        max_content_chars: Maximum chars for content field
        include_metadata: Include status, dates, etc.

    Returns:
        Dictionary with template variables for PromptLoader

    Example:
        >>> priority = {
        ...     "name": "PRIORITY 5",
        ...     "title": "Build dashboard",
        ...     "content": "Long description...",
        ...     "status": "Planned",
        ...     "estimated_hours": 8
        ... }
        >>> context = build_priority_context(priority)
        >>> context.keys()
        dict_keys(['PRIORITY_NAME', 'PRIORITY_TITLE', 'PRIORITY_CONTENT',
                   'PRIORITY_STATUS', 'ESTIMATED_HOURS'])
    """
    context = {
        "PRIORITY_NAME": priority.get("name", "Unknown"),
        "PRIORITY_TITLE": priority.get("title", "No title"),
        "PRIORITY_CONTENT": truncate_content(
            priority.get("content", ""),
            max_chars=max_content_chars
        ),
    }

    if include_metadata:
        context.update({
            "PRIORITY_STATUS": priority.get("status", "Unknown"),
            "ESTIMATED_HOURS": str(priority.get("estimated_hours", "TBD")),
        })

    return context
```

### 3. Spec Context Builder

```python
def build_spec_context(
    spec_filename: str,
    priority_name: str,
    additional_context: str = "",
    max_context_chars: int = 2000
) -> dict:
    """
    Build standardized spec context for technical specification prompts.

    Args:
        spec_filename: Target spec filename (e.g., "SPEC-050-feature.md")
        priority_name: Priority being specified
        additional_context: Extra context to include
        max_context_chars: Max chars for additional_context

    Returns:
        Dictionary with template variables

    Example:
        >>> context = build_spec_context(
        ...     "SPEC-050-auth.md",
        ...     "PRIORITY 10",
        ...     "User authentication system..."
        ... )
        >>> context['SPEC_FILENAME']
        'SPEC-050-auth.md'
    """
    return {
        "SPEC_FILENAME": spec_filename,
        "PRIORITY_NAME": priority_name,
        "ADDITIONAL_CONTEXT": truncate_content(
            additional_context,
            max_chars=max_context_chars
        ),
    }
```

### 4. Roadmap Context Builder

```python
def build_roadmap_context(
    roadmap_content: str,
    current_priority: str,
    max_roadmap_chars: int = 3000
) -> dict:
    """
    Build roadmap context for daemon prompts.

    Args:
        roadmap_content: Full ROADMAP.md content
        current_priority: Priority currently being worked on
        max_roadmap_chars: Max chars for roadmap excerpt

    Returns:
        Dictionary with template variables
    """
    # Extract relevant section (current priority + next 3)
    # (Implementation details omitted for brevity)

    return {
        "ROADMAP_EXCERPT": truncate_content(
            roadmap_content,
            max_chars=max_roadmap_chars
        ),
        "CURRENT_PRIORITY": current_priority,
    }
```

---

## Technical Details

### Migration Strategy

**Phase 1: Create Utility Module** (30 min)
```bash
# Create file
touch coffee_maker/utils/prompt_builders.py

# Add to __init__.py
echo "from .prompt_builders import *" >> coffee_maker/utils/__init__.py
```

**Phase 2: Implement Functions** (1 hour)
1. Write `truncate_content()` with tests
2. Write `build_priority_context()` with tests
3. Write `build_spec_context()` with tests
4. Write `build_roadmap_context()` with tests

**Phase 3: Update Existing Code** (1 hour)
1. Find all duplicate truncation logic:
   ```bash
   grep -r "priority.get.*content.*\[:1500\]" coffee_maker/
   ```
2. Replace with `from coffee_maker.utils import truncate_content, build_priority_context`
3. Update daemon_implementation.py
4. Update spec_generator.py
5. Update ai_service.py

**Phase 4: Validate** (30 min)
1. Run unit tests
2. Verify no regressions
3. Test daemon with real priority

### Files to Update

1. **daemon_implementation.py**
   - Replace `_build_documentation_prompt()` logic
   - Replace `_build_feature_prompt()` logic
   - Use `build_priority_context()`

2. **spec_generator.py**
   - Replace truncation logic
   - Use `build_spec_context()`

3. **ai_service.py**
   - Replace prompt building patterns
   - Use standardized builders

4. **New file: coffee_maker/utils/prompt_builders.py**
   - Implement all utility functions
   - Add comprehensive docstrings
   - Add type hints

### Constants to Define

```python
# coffee_maker/config/constants.py (if doesn't exist, create it)

# Prompt truncation limits
PROMPT_CONTENT_MAX_CHARS = 1500        # Priority content
PROMPT_CONTEXT_MAX_CHARS = 2000        # Additional context
PROMPT_ROADMAP_MAX_CHARS = 3000        # Roadmap excerpts
PROMPT_TRUNCATION_MARKER = "..."       # Truncation indicator

# Use in prompt_builders.py
from coffee_maker.config.constants import (
    PROMPT_CONTENT_MAX_CHARS,
    PROMPT_TRUNCATION_MARKER
)
```

---

## Data Structures

### Input: Priority Dictionary
```python
{
    "name": str,           # e.g., "PRIORITY 5"
    "title": str,          # e.g., "Build dashboard"
    "content": str,        # Full description (may be long)
    "status": str,         # "Planned", "In Progress", "Complete"
    "estimated_hours": int # Optional
}
```

### Output: Template Variables
```python
{
    "PRIORITY_NAME": str,     # Direct from priority["name"]
    "PRIORITY_TITLE": str,    # Direct from priority["title"]
    "PRIORITY_CONTENT": str,  # Truncated content
    "PRIORITY_STATUS": str,   # Optional metadata
    "ESTIMATED_HOURS": str    # Optional metadata
}
```

---

## Testing Strategy

### Unit Tests

**New Test File**: `tests/unit/utils/test_prompt_builders.py`

```python
import pytest
from coffee_maker.utils.prompt_builders import (
    truncate_content,
    build_priority_context,
    build_spec_context,
)

class TestTruncateContent:
    def test_no_truncation_when_short(self):
        result = truncate_content("Short text", max_chars=1500)
        assert result == "Short text"

    def test_truncation_with_marker(self):
        long_text = "a" * 2000
        result = truncate_content(long_text, max_chars=100)
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")

    def test_preserve_sentences(self):
        text = "Sentence one. Sentence two. Sentence three."
        result = truncate_content(text, max_chars=20, preserve_sentences=True)
        assert result == "Sentence one..."

    def test_custom_marker(self):
        result = truncate_content("a" * 100, max_chars=10, truncation_marker=" [cut]")
        assert result.endswith(" [cut]")

class TestBuildPriorityContext:
    def test_basic_context(self):
        priority = {
            "name": "PRIORITY 5",
            "title": "Test",
            "content": "Description"
        }
        context = build_priority_context(priority)
        assert context["PRIORITY_NAME"] == "PRIORITY 5"
        assert context["PRIORITY_TITLE"] == "Test"
        assert context["PRIORITY_CONTENT"] == "Description"

    def test_truncates_long_content(self):
        priority = {
            "name": "PRIORITY 5",
            "title": "Test",
            "content": "a" * 2000
        }
        context = build_priority_context(priority, max_content_chars=100)
        assert len(context["PRIORITY_CONTENT"]) <= 103  # 100 + "..."

    def test_includes_metadata(self):
        priority = {
            "name": "PRIORITY 5",
            "title": "Test",
            "content": "Description",
            "status": "Planned",
            "estimated_hours": 8
        }
        context = build_priority_context(priority, include_metadata=True)
        assert context["PRIORITY_STATUS"] == "Planned"
        assert context["ESTIMATED_HOURS"] == "8"
```

### Integration Tests

**Verify Daemon Integration**: `tests/ci_tests/test_daemon_prompt_building.py`

```python
def test_daemon_uses_prompt_builders():
    """Verify daemon uses centralized prompt builders."""
    from coffee_maker.autonomous.daemon_implementation import ImplementationMixin

    # Mock priority
    priority = {
        "name": "PRIORITY 5",
        "title": "Test priority",
        "content": "a" * 2000  # Long content
    }

    # Should use prompt_builders internally
    # (Test implementation details omitted)
```

### Manual Testing
```bash
# 1. Run daemon with real priority
poetry run code-developer --auto-approve

# 2. Verify prompts are correctly built
# Check developer_status.json for prompt content

# 3. Verify truncation works
# Long priorities should be truncated with "..."
```

---

## Rollout Plan

### Week 1: Implementation
- **Day 1**: Create `prompt_builders.py` module (1 hour)
- **Day 1**: Write unit tests for all functions (1.5 hours)
- **Day 2**: Update daemon_implementation.py (30 min)
- **Day 2**: Update spec_generator.py (30 min)
- **Day 2**: Update ai_service.py (30 min)

### Week 1: Testing & Validation
- **Day 3**: Run full test suite (30 min)
- **Day 3**: Manual testing with daemon (30 min)
- **Day 3**: Fix any issues (1 hour buffer)

### Week 1: Cleanup
- **Day 3**: Remove old duplicate code (30 min)
- **Day 3**: Update CLAUDE.md documentation (30 min)

**Total Timeline**: 3 days (6.5 hours actual work)

---

## Risks & Mitigations

### Risk 1: Breaking Prompt Generation
**Likelihood**: LOW
**Impact**: HIGH (daemon won't work)
**Mitigation**:
- Comprehensive unit tests before rollout
- Keep old code until validation complete
- Manual testing with real priorities
- Rollback plan: revert commits if issues

### Risk 2: Different Truncation Behavior
**Likelihood**: MEDIUM
**Impact**: LOW (prompts slightly different)
**Mitigation**:
- Test with existing priorities
- Compare before/after prompt content
- Adjust truncation logic if needed

### Risk 3: Import Circular Dependencies
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- prompt_builders is pure utility (no imports from daemon)
- Only imports from config/constants
- Clear dependency hierarchy

---

## Success Criteria

### Quantitative
- ✅ ~150 LOC of duplication removed
- ✅ All truncation logic uses `truncate_content()`
- ✅ All priority contexts use `build_priority_context()`
- ✅ 100% of existing tests passing
- ✅ New utility functions have ≥90% test coverage
- ✅ No performance degradation (<1ms per prompt build)

### Qualitative
- ✅ Developers use utilities for new prompt building
- ✅ Consistent truncation across all prompts
- ✅ Easy to change truncation limits globally
- ✅ Clear, reusable API for prompt context

---

## Before & After Comparison

### Before: daemon_implementation.py
```python
# daemon_implementation.py - DUPLICATED LOGIC ❌
def _build_documentation_prompt(self, priority: dict) -> str:
    priority_content = priority.get("content", "")[:1500]  # DUPLICATE
    if len(priority.get("content", "")) > 1500:            # DUPLICATE
        priority_content += "..."                           # DUPLICATE

    return load_prompt(PromptNames.IMPLEMENT_DOCUMENTATION, {
        "PRIORITY_NAME": priority["name"],                  # DUPLICATE
        "PRIORITY_TITLE": priority["title"],                # DUPLICATE
        "PRIORITY_CONTENT": priority_content,
    })
```

### After: daemon_implementation.py
```python
# daemon_implementation.py - USES UTILITIES ✅
from coffee_maker.utils.prompt_builders import build_priority_context

def _build_documentation_prompt(self, priority: dict) -> str:
    context = build_priority_context(priority)  # CENTRALIZED ✅

    return load_prompt(PromptNames.IMPLEMENT_DOCUMENTATION, context)
```

**Reduction**: 6 lines → 1 line (83% reduction)

---

## Related Work

### Depends On
- None (independent utility module)

### Enables
- **SPEC-050**: Modular CLI commands can use utilities
- **Future**: Easier to add new prompt types
- **Future**: Multi-language prompt support (i18n)

### Related Specs
- **SPEC-052**: Error handling (similar utility pattern)

---

## Future Enhancements

### After This Implementation
1. **Prompt Validation**: Validate generated prompts before use
2. **Prompt Metrics**: Track prompt sizes, truncation frequency
3. **Smart Truncation**: ML-based important content extraction
4. **Multi-Provider Templates**: Provider-specific prompt formats

---

## Appendix A: Current Duplication Analysis

### Duplicate Pattern Locations

| File | Lines | Pattern | Truncation |
|------|-------|---------|------------|
| daemon_implementation.py | 431-434 | priority.get("content")[:1500] | "..." |
| daemon_implementation.py | 463-466 | priority.get("content")[:1500] | "..." |
| spec_generator.py | 88-91 | content[:1500] | "..." |
| ai_service.py | 145-148 | priority["content"][:1500] | " [truncated]" |

**Total Duplication**: ~150 LOC across 4 locations

### After Centralization

| File | Lines | Pattern |
|------|-------|---------|
| prompt_builders.py | 1-50 | Single implementation |
| daemon_implementation.py | 1 | build_priority_context() |
| spec_generator.py | 1 | build_spec_context() |
| ai_service.py | 1 | build_priority_context() |

**Total**: ~52 LOC (65% reduction)

---

## Appendix B: API Reference

### truncate_content()
```python
def truncate_content(
    content: str,
    max_chars: int = 1500,
    truncation_marker: str = "...",
    preserve_sentences: bool = True
) -> str
```

### build_priority_context()
```python
def build_priority_context(
    priority: dict,
    max_content_chars: int = 1500,
    include_metadata: bool = True
) -> dict
```

### build_spec_context()
```python
def build_spec_context(
    spec_filename: str,
    priority_name: str,
    additional_context: str = "",
    max_context_chars: int = 2000
) -> dict
```

### build_roadmap_context()
```python
def build_roadmap_context(
    roadmap_content: str,
    current_priority: str,
    max_roadmap_chars: int = 3000
) -> dict
```

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 6.5 hours
**Actual Effort**: TBD
