# Naming Improvements - US-021 Phase 2.5

**Created**: 2025-10-12
**Status**: 📝 Planned

## Overview

Systematic renaming to improve code clarity and remove redundancy.

## Principles

1. **No redundant suffixes**: `logging_utils.py` → `logging.py`
2. **Clear, specific names**: No generic `utils.py`, `helpers.py`
3. **Consistent patterns**: `*_manager`, `*_interface`, `*_parser` only when needed
4. **Stdlib-safe**: Use full import paths to avoid conflicts

## Proposed Renamings

### Category 1: Redundant `_utils` Suffix ⚡ HIGH PRIORITY

| Current | Proposed | Rationale | Risk |
|---------|----------|-----------|------|
| `utils/logging_utils.py` | `utils/logging.py` | Already in `utils/`, suffix redundant | Low - use absolute imports |
| `utils/time_utils.py` | `utils/time.py` | Already in `utils/`, suffix redundant | Low - use absolute imports |
| `langchain_observe/retry_utils.py` | `langchain_observe/retry.py` | Suffix redundant | Low |

**Import pattern safety:**
```python
# SAFE (absolute import):
from coffee_maker.utils.logging import get_logger
from coffee_maker.utils.time import format_duration

# AVOID (relative import could conflict):
from .logging import get_logger  # OK within coffee_maker
import logging  # This gets stdlib, not ours - OK!

# The only conflict would be:
from coffee_maker.utils import logging  # Gets our module
import logging  # Gets stdlib - these don't conflict!
```

**Estimated Impact**: 71 files import `logging_utils`, 20+ files import `time_utils`, 10+ files import `retry_utils`

---

### Category 2: Typos and Clarity Issues ⚡ HIGH PRIORITY

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `utils/run_deamon_process.py` | `utils/run_daemon_process.py` | Fix typo: deamon → daemon |
| `langchain_observe/auto_picker_llm_refactored.py` | `langchain_observe/auto_picker.py` | Remove "refactored" suffix (it's done!), shorten name |
| `langchain_observe/utils.py` | `langchain_observe/helpers.py` or better: merge into specific modules | Too generic |

---

### Category 3: Verbose or Unclear Names

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `autonomous/claude_api_interface.py` | Keep as-is | Clear: interface to Claude API |
| `autonomous/claude_cli_interface.py` | Keep as-is | Clear: interface to Claude CLI |
| `autonomous/git_manager.py` | Keep as-is | Clear: manages git operations |
| `config/manager.py` | Keep as-is | Clear: manages configuration |
| `langchain_observe/llm_tools.py` | Consider: `langchain_observe/tools.py` | Already has tools.py - merge? |
| `langchain_observe/llm.py` | Keep as-is | Core LLM abstraction |
| `cli/ai_service.py` | Keep as-is | It IS a service layer |

---

### Category 4: Directory Structure Issues

**Issue**: Some modules have both `X.py` and `X_utils.py`:
```
langchain_observe/
├── tools.py           # What are these tools?
├── llm_tools.py       # LLM-specific tools?
├── utils.py           # Generic utilities?
└── retry_utils.py     # Retry utilities
```

**Proposal**: Consolidate or clarify:
```
langchain_observe/
├── llm.py             # Core LLM class
├── tools.py           # Merge llm_tools.py here
├── retry.py           # Rename from retry_utils.py
└── [no utils.py]      # Move functions to specific modules
```

---

## Migration Strategy

### Phase 1: Simple Renames (Low Risk)

**Day 1 Morning** (2 hours):

1. **Rename without changing imports** (git mv):
   ```bash
   git mv coffee_maker/langchain_observe/retry_utils.py \
          coffee_maker/langchain_observe/retry.py

   git mv coffee_maker/utils/run_deamon_process.py \
          coffee_maker/utils/run_daemon_process.py
   ```

2. **Update imports automatically**:
   ```bash
   # Find and replace in all files
   find coffee_maker -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.langchain_observe\.retry_utils/from coffee_maker.langchain_observe.retry/g' {} +

   find coffee_maker -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.utils\.run_deamon_process/from coffee_maker.utils.run_daemon_process/g' {} +
   ```

3. **Test**:
   ```bash
   pytest tests/
   python -m coffee_maker.cli.chat_interface --help
   ```

4. **Commit**:
   ```bash
   git commit -m "refactor: Rename retry_utils → retry, fix daemon typo"
   ```

**Estimated Time**: 2 hours

---

### Phase 2: Critical Renames (Medium Risk)

**Day 1 Afternoon** (4 hours):

1. **Rename `logging_utils.py` → `logging.py`**:
   ```bash
   git mv coffee_maker/utils/logging_utils.py coffee_maker/utils/logging.py
   ```

2. **Update all 71 imports**:
   ```bash
   # Create migration script
   cat > /tmp/migrate_logging.py << 'EOF'
   import sys
   import re
   from pathlib import Path

   def migrate_file(filepath):
       content = filepath.read_text()
       original = content

       # Pattern 1: from coffee_maker.utils.logging_utils import X
       content = re.sub(
           r'from coffee_maker\.utils\.logging_utils import',
           'from coffee_maker.utils.logging import',
           content
       )

       # Pattern 2: from coffee_maker.utils import logging_utils
       content = re.sub(
           r'from coffee_maker\.utils import logging_utils',
           'from coffee_maker.utils import logging',
           content
       )

       # Pattern 3: logging_utils.get_logger
       content = re.sub(
           r'\blogging_utils\.',
           'logging.',
           content
       )

       if content != original:
           filepath.write_text(content)
           print(f"✓ Updated: {filepath}")
       else:
           print(f"  Skipped: {filepath}")

   # Migrate all Python files
   for filepath in Path("coffee_maker").rglob("*.py"):
       migrate_file(filepath)

   for filepath in Path("tests").rglob("*.py"):
       migrate_file(filepath)
   EOF

   python /tmp/migrate_logging.py
   ```

3. **Fix any import conflicts**:
   - Check files that have both `import logging` (stdlib) and our logging
   - Ensure absolute imports: `from coffee_maker.utils.logging import get_logger`

4. **Update `__all__` in utils/__init__.py if needed**

5. **Test thoroughly**:
   ```bash
   # Unit tests
   pytest tests/ -v

   # Type checking
   mypy coffee_maker/

   # Import test
   python -c "from coffee_maker.utils.logging import get_logger; print('✓ Import works')"
   python -c "import logging; print('✓ Stdlib not affected')"

   # Integration test
   python -m coffee_maker.cli.chat_interface --help
   ```

6. **Commit**:
   ```bash
   git add -A
   git commit -m "refactor: Rename logging_utils → logging (remove redundant suffix)

   - Renamed coffee_maker/utils/logging_utils.py → logging.py
   - Updated 71 import statements across codebase
   - Verified no conflicts with stdlib logging module
   - All tests passing
   "
   ```

**Estimated Time**: 4 hours

---

### Phase 3: time_utils Rename (Low Risk)

**Day 2 Morning** (2 hours):

Similar process for `time_utils.py` → `time.py`:

1. Count files: `grep -r "time_utils" coffee_maker/ | wc -l`
2. Rename file
3. Update imports
4. Test
5. Commit

**Estimated Time**: 2 hours

---

### Phase 4: Complex Renames (Optional - Medium Risk)

**Day 2 Afternoon** (4 hours):

Only if time permits:

1. **Rename `auto_picker_llm_refactored.py` → `auto_picker.py`**
2. **Consolidate `langchain_observe/utils.py`** → merge into specific modules
3. **Consider merging `llm_tools.py` → `tools.py`**

**Estimated Time**: 4 hours

---

## Import Update Examples

### Example 1: logging_utils → logging

**Before**:
```python
import logging
from coffee_maker.utils.logging_utils import get_logger, log_error, LogFormatter

logger = logging.getLogger(__name__)  # Stdlib logger (old pattern)
```

**After**:
```python
from coffee_maker.utils.logging import get_logger, log_error, LogFormatter

logger = get_logger(__name__)  # Our standardized logger
```

**No conflict because**:
- Stdlib `logging` not imported
- Our module: `coffee_maker.utils.logging` (fully qualified)

---

### Example 2: Files with both

**Before**:
```python
import logging  # Stdlib
from coffee_maker.utils.logging_utils import log_error  # Ours

logger = logging.getLogger(__name__)  # Stdlib
log_error(logger, "Failed", exception)  # Ours
```

**After**:
```python
from coffee_maker.utils.logging import get_logger, log_error  # All ours

logger = get_logger(__name__)  # Our implementation (wraps stdlib)
log_error(logger, "Failed", exception)  # Ours
```

**Benefit**: Consistent usage of our utilities

---

## Testing Checklist

After each rename:

- [ ] `pytest tests/ -v` - All unit tests pass
- [ ] `mypy coffee_maker/` - No new type errors
- [ ] `python -m coffee_maker.cli.chat_interface --help` - CLI works
- [ ] `python -m coffee_maker.autonomous.daemon --help` - Daemon works
- [ ] Import test: `python -c "from coffee_maker.utils.X import Y"`
- [ ] No circular imports: Check import order
- [ ] Git mv preserved history: `git log --follow path/to/file.py`

---

## Rollback Plan

Each rename is a separate commit, can rollback individually:

```bash
# Rollback single rename
git revert <commit-hash>

# Or restore old file
git checkout HEAD~1 coffee_maker/utils/logging_utils.py
# Re-update imports
git checkout HEAD coffee_maker/  # Get all import updates
mv coffee_maker/utils/logging.py coffee_maker/utils/logging_utils.py
# Run migration script in reverse
```

---

## Migration Priority Order

**Recommended sequence:**

1. ✅ **Phase 1** (2h): Simple renames (retry_utils, fix typo)
2. ✅ **Phase 2** (4h): logging_utils → logging (71 files)
3. ✅ **Phase 3** (2h): time_utils → time (20 files)
4. ⏸️  **Phase 4** (4h): Optional complex renames

**Total essential**: 8 hours (Day 1-2)
**Total with optional**: 12 hours

---

## Communication Plan

**Before starting:**
- [ ] Get user approval on renaming plan
- [ ] Clarify: stdlib conflict handling acceptable?
- [ ] Confirm: git mv to preserve history?

**During migration:**
- [ ] Commit per rename (atomic changes)
- [ ] Update ROADMAP.md progress
- [ ] Merge to roadmap branch daily

**After completion:**
- [ ] Update documentation with new import paths
- [ ] Create migration guide for contributors
- [ ] Add to CONTRIBUTING.md

---

## Impact Analysis

### Files Affected by Each Rename

**logging_utils → logging**: 71 files
```bash
grep -r "logging_utils" coffee_maker/ --include="*.py" | wc -l
# 71 files
```

**time_utils → time**: ~20 files
```bash
grep -r "time_utils" coffee_maker/ --include="*.py" | wc -l
# 20 files
```

**retry_utils → retry**: ~10 files
```bash
grep -r "retry_utils" coffee_maker/ --include="*.py" | wc -l
# 10 files
```

**Total**: ~101 file edits across 3 core renames

---

## Decision: stdlib Conflict Handling

**Question**: Is `coffee_maker/utils/logging.py` safe given stdlib `logging`?

**Answer**: ✅ YES, completely safe because:

1. **Different namespaces**:
   - Stdlib: `import logging` → gets Python's logging module
   - Ours: `from coffee_maker.utils import logging` → gets our module
   - No ambiguity when using absolute imports

2. **Common pattern** in Python projects:
   - Django has `django.utils.logging`
   - Flask has `flask.logging`
   - Many projects wrap stdlib logging

3. **Best practice**:
   - Always use absolute imports: `from coffee_maker.utils.logging import X`
   - Never use bare `import logging` for our module
   - Document in module docstring

4. **Verification**:
   ```python
   # test_no_conflict.py
   import logging as stdlib_logging
   from coffee_maker.utils.logging import get_logger

   # These are different:
   assert stdlib_logging != get_logger
   print("✓ No conflict")
   ```

---

## Recommended Action

**User approval required for:**

1. ✅ Rename `logging_utils.py` → `logging.py`
2. ✅ Rename `time_utils.py` → `time.py`
3. ✅ Rename `retry_utils.py` → `retry.py`
4. ✅ Fix typo: `run_deamon_process.py` → `run_daemon_process.py`
5. ⏸️  Optional: Complex renames (auto_picker_llm_refactored, etc.)

**Estimated time**: 8-12 hours

**Start after**: Phase 2.5 migration plan approved

---

## Next Steps

1. **Get user approval** on this naming plan
2. **Execute renames** before starting utility adoption
3. **Update Phase 2.5 migration plan** with new import paths
4. **Proceed with** Option A → Option B → Option D

---

**End of Naming Improvements Document**
