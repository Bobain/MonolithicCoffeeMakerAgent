# SPEC-025: Refactor Skill Loading to Use Proper Python Imports

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Related**: PRIORITY 25, ADR-002 (Integrate Claude Skills)

**Related Specs**: SPEC-055 (Claude Skills Phase 1), SPEC-108 (Parallel Agent Execution)

**Assigned To**: code_developer

---

## Executive Summary

This specification defines the refactoring of skill loading from non-Pythonic `importlib.util` dynamic loading to proper Python package structure with standard imports. This change improves type safety, IDE support, testability, and maintainability while maintaining 100% backward compatibility with existing skill functionality.

**Key Deliverables**:
1. **Directory Restructuring**: Convert `.claude/skills/` to proper Python package with `__init__.py` files
2. **Module Renaming**: Rename hyphenated directories to underscored (PEP 8 compliance)
3. **Import Refactoring**: Replace `importlib.util` with standard Python imports
4. **Skill Registry Enhancement**: Centralized skill loading API
5. **Test Updates**: Update all skill tests to use new import paths

**Expected Impact**:
- ✅ IDE autocomplete, type checking, refactoring support
- ✅ Cleaner, more maintainable code
- ✅ Faster skill loading (no dynamic module creation)
- ✅ Better error messages (import errors vs. file-not-found)
- ✅ Easier testing (can mock imports)

**Estimated Effort**: 4-6 hours

---

## Problem Statement

### Current Situation

The orchestrator currently loads skills using non-Pythonic dynamic module loading with `importlib.util`:

**Current Implementation** (`coffee_maker/orchestrator/continuous_work_loop.py:1042-1054`):
```python
import importlib.util

skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"

if not skill_path.exists():
    return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}

spec = importlib.util.spec_from_file_location("task_separator", skill_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Call skill
result = module.main({"priority_ids": priority_ids})
```

**Similar pattern in** (`coffee_maker/orchestrator/parallel_execution_coordinator.py:227-234`).

### Issues with Current Approach

| Issue | Impact | Severity |
|-------|--------|----------|
| **Not Pythonic** | Treats skills as external scripts rather than Python modules | Medium |
| **No IDE support** | Autocomplete, type checking, refactoring don't work | High |
| **Error-prone** | File paths can break, typos not caught until runtime | Medium |
| **Hard to test** | Can't easily mock or test skill imports | Medium |
| **No dependency tracking** | Unclear what skills depend on | Low |
| **PEP 8 violations** | Directory names use hyphens (e.g., `task-separator`) | Low |
| **Slower loading** | Dynamic module creation has overhead | Low |
| **Poor error messages** | "File not found" instead of "ImportError: No module named..." | Medium |

### Example Problem

**Current workflow**:
```python
# orchestrator needs task-separator skill
skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"
# ❌ No autocomplete for skill_path
# ❌ Typo in path not caught until runtime
# ❌ If file moved, error is cryptic: "File not found: /path/to/skill"
# ❌ Can't easily test with mocked skill
```

**Desired workflow**:
```python
# orchestrator imports skill like any Python module
from claude.skills.architect.task_separator import main as task_separator_main
# ✅ Autocomplete works (IDE knows module exists)
# ✅ Typo caught immediately (import fails at startup)
# ✅ If file moved, error is clear: "ImportError: No module named 'claude.skills.architect.task_separator'"
# ✅ Easy to mock: unittest.mock.patch('claude.skills.architect.task_separator.main')
```

### Goal

Refactor skill loading to use proper Python package structure and standard imports, achieving:
1. **IDE Support**: Full autocomplete, type checking, refactoring
2. **Type Safety**: mypy can validate skill imports
3. **Better Error Messages**: Import errors instead of file-not-found
4. **Easier Testing**: Can mock skill imports
5. **PEP 8 Compliance**: Module names use underscores
6. **Faster Loading**: No dynamic module creation overhead
7. **100% Backward Compatibility**: All existing skill functionality preserved

### Non-Goals

**This refactoring does NOT include**:
- ❌ Changing skill functionality (only loading mechanism)
- ❌ Modifying skill APIs (skills still export `main()` function)
- ❌ Altering skill discovery logic (SkillRegistry/SkillLoader unchanged)
- ❌ Adding new skills (only refactoring existing ones)
- ❌ Changing skill execution (SkillInvoker unchanged)

---

## Requirements

### Functional Requirements

1. **FR-1**: Convert `.claude/skills/` to proper Python package with `__init__.py` files
2. **FR-2**: Rename all hyphenated skill directories to use underscores (PEP 8)
3. **FR-3**: Replace all `importlib.util` skill loading with standard Python imports
4. **FR-4**: Update orchestrator to import skills directly
5. **FR-5**: Update SkillLoader to support both file-based and import-based loading (transition period)
6. **FR-6**: Update all skill tests to use new import paths
7. **FR-7**: Ensure all existing skill functionality works identically after refactoring

### Non-Functional Requirements

1. **NFR-1**: Backward Compatibility: All existing skill calls work without changes (100%)
2. **NFR-2**: Performance: Skill loading ≥10% faster (no dynamic module overhead)
3. **NFR-3**: IDE Support: PyCharm/VSCode autocomplete works for all skill imports
4. **NFR-4**: Type Safety: mypy can validate skill imports without errors
5. **NFR-5**: Testability: Can mock any skill import with `unittest.mock.patch`
6. **NFR-6**: Error Messages: Import failures provide clear, actionable error messages
7. **NFR-7**: Code Quality: All skill modules pass `black`, `flake8`, `mypy` checks

### Constraints

- **MUST** maintain 100% backward compatibility (no skill behavior changes)
- **MUST** work on `roadmap` branch only (CFR-013)
- **MUST** pass all existing tests (no regressions)
- **MUST** rename directories to use underscores (PEP 8)
- **MUST NOT** break orchestrator parallel execution (PRIORITY 23)
- **Timeline**: 4-6 hours total (low-risk refactoring)

---

## Current Implementation Analysis

### Affected Files

**Orchestrator Files** (dynamic loading):
1. `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/continuous_work_loop.py:1042-1054`
   - Uses `importlib.util` to load `task-separator` skill
   - 2 occurrences

2. `/Users/bobain/PycharmProjects/MonithicCoffeeMakerAgent/coffee_maker/orchestrator/parallel_execution_coordinator.py:227-234`
   - Uses `importlib.util` to load `task-separator` skill
   - 1 occurrence

**Skill Loader Files** (may need updates):
1. `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/skill_loader.py`
   - Currently loads skills from `.claude/skills/` using file paths
   - May need dual-mode support (file-based + import-based)

2. `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/skill_loader.py`
   - Startup skill loader (loads markdown skills, not Python)
   - No changes needed

**Test Files**:
1. `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/unit/test_skill_loader.py`
   - Tests skill loading from `.claude/skills/`
   - May need import path updates

### Current Directory Structure

```
.claude/skills/
├── architect/
│   ├── task-separator/              # ❌ Hyphenated (not Python-friendly)
│   │   └── task_separator.py
│   ├── merge-worktree-branches/     # ❌ Hyphenated
│   │   └── merge_worktree_branches.py
│   ├── architecture-reuse-check/    # ❌ Hyphenated
│   │   └── SKILL.md
│   └── code-review-history/         # ❌ Hyphenated
├── shared/
│   ├── bug-tracking/                # ❌ Hyphenated
│   │   └── bug_tracking.md
│   ├── roadmap-management.md        # ✅ File (not directory)
│   └── orchestrator-agent-management.md
├── proactive-refactoring-analysis/  # ❌ Hyphenated (top-level)
└── git-workflow-automation/         # ❌ Hyphenated (top-level)
```

**Problems**:
- Hyphenated directories can't be imported as Python modules
- No `__init__.py` files (not a Python package)
- Skills in root directory (not organized by agent)

---

## Proposed Solution

### High-Level Approach

**Three-Phase Migration**:

1. **Phase 1: Directory Restructuring** (1 hour)
   - Add `__init__.py` to all skill directories
   - Rename hyphenated directories to underscored
   - Verify directory structure

2. **Phase 2: Import Refactoring** (2-3 hours)
   - Replace `importlib.util` with standard imports in orchestrator
   - Update SkillLoader to support import-based loading
   - Add error handling for import failures

3. **Phase 3: Test Updates** (1 hour)
   - Update skill tests to use new import paths
   - Add tests for import-based loading
   - Verify all tests pass

### Proposed Directory Structure

```
.claude/skills/
├── __init__.py                          # NEW: Makes skills a package
├── shared/
│   ├── __init__.py                      # NEW
│   ├── bug_tracking/                    # RENAMED: bug-tracking → bug_tracking
│   │   ├── __init__.py                  # NEW
│   │   └── bug_tracking.py              # RENAMED: bug_tracking.md → .py (if Python)
│   ├── roadmap_management.py            # EXISTING (already .py)
│   └── orchestrator_agent_management.py # EXISTING (already .py)
└── architect/
    ├── __init__.py                      # NEW
    ├── task_separator/                  # RENAMED: task-separator → task_separator
    │   ├── __init__.py                  # NEW
    │   └── task_separator.py            # EXISTING
    ├── merge_worktree_branches/         # RENAMED: merge-worktree-branches
    │   ├── __init__.py                  # NEW
    │   └── merge_worktree_branches.py   # EXISTING
    ├── architecture_reuse_check/        # RENAMED: architecture-reuse-check
    │   ├── __init__.py                  # NEW
    │   └── SKILL.md                     # EXISTING (markdown skill)
    └── code_review_history/             # RENAMED: code-review-history
        ├── __init__.py                  # NEW
        └── code_review_history.py       # NEW (convert from markdown if needed)
```

**Root-Level Skills** (move to appropriate directories):
```
.claude/skills/
├── shared/
│   ├── git_workflow_automation/         # MOVED: from root
│   │   ├── __init__.py
│   │   └── git_workflow_automation.py
│   └── proactive_refactoring_analysis/  # MOVED: from root (or architect?)
│       ├── __init__.py
│       └── proactive_refactoring_analysis.py
```

### Directory Renaming Map

| Current (Hyphenated) | New (Underscored) | Location |
|----------------------|-------------------|----------|
| `task-separator/` | `task_separator/` | `.claude/skills/architect/` |
| `merge-worktree-branches/` | `merge_worktree_branches/` | `.claude/skills/architect/` |
| `architecture-reuse-check/` | `architecture_reuse_check/` | `.claude/skills/architect/` |
| `code-review-history/` | `code_review_history/` | `.claude/skills/architect/` |
| `dependency-conflict-resolver/` | `dependency_conflict_resolver/` | `.claude/skills/architect/` |
| `bug-tracking/` | `bug_tracking/` | `.claude/skills/shared/` |
| `git-workflow-automation/` | `git_workflow_automation/` | `.claude/skills/shared/` |
| `proactive-refactoring-analysis/` | `proactive_refactoring_analysis/` | `.claude/skills/architect/` or `shared/` |

### Import Refactoring

**Before** (dynamic loading):
```python
# orchestrator/continuous_work_loop.py:1042-1054
import importlib.util

skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"

if not skill_path.exists():
    return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}

spec = importlib.util.spec_from_file_location("task_separator", skill_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.main({"priority_ids": priority_ids})
```

**After** (standard import):
```python
# orchestrator/continuous_work_loop.py
from claude.skills.architect.task_separator.task_separator import main as task_separator_main

try:
    result = task_separator_main({"priority_ids": priority_ids})
except ImportError as e:
    logger.error(f"Failed to import task_separator skill: {e}")
    return {"valid": False, "reason": f"task_separator skill not available: {e}"}
except Exception as e:
    logger.error(f"Error running task_separator skill: {e}", exc_info=True)
    return {"valid": False, "reason": f"Error: {e}"}
```

**Benefits**:
- ✅ 15 lines → 9 lines (40% reduction)
- ✅ No file path construction (fewer error points)
- ✅ IDE autocomplete works
- ✅ Import failures caught at startup (not runtime)
- ✅ Can mock: `@patch('claude.skills.architect.task_separator.task_separator.main')`

### SkillLoader Enhancement

**Current** (`coffee_maker/autonomous/skill_loader.py`):
```python
class SkillLoader:
    def load(self, skill_name: str) -> SkillMetadata:
        # Try agent-specific first
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata.from_skill_md(agent_skill_path)
        # ...
```

**Enhanced** (dual-mode support):
```python
class SkillLoader:
    def load(self, skill_name: str) -> SkillMetadata:
        # NEW: Try import-based loading first (faster, more reliable)
        try:
            module_path = f"claude.skills.{self.agent_type.value.replace('_', '-')}.{skill_name}"
            module = importlib.import_module(module_path)
            return SkillMetadata.from_module(module)
        except ImportError:
            pass  # Fall back to file-based loading

        # EXISTING: File-based loading (backward compatibility)
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata.from_skill_md(agent_skill_path)
        # ...
```

**Rationale**: Dual-mode support allows gradual migration. New skills use imports, old skills still work.

### Testing Approach

**New Test Cases**:
```python
# tests/unit/test_skill_loading_imports.py

def test_import_task_separator_skill():
    """Test importing task-separator skill using standard Python import."""
    from claude.skills.architect.task_separator.task_separator import main

    # Skill should have main() function
    assert callable(main)

    # Call with test data
    result = main({"priority_ids": [1, 2]})
    assert isinstance(result, dict)

def test_import_all_skills():
    """Test all skills can be imported (no import errors)."""
    skills = [
        "claude.skills.architect.task_separator",
        "claude.skills.architect.merge_worktree_branches",
        "claude.skills.shared.bug_tracking",
        # ... all skills
    ]

    for skill_path in skills:
        try:
            importlib.import_module(skill_path)
        except ImportError as e:
            pytest.fail(f"Failed to import {skill_path}: {e}")

def test_mock_skill_import():
    """Test skills can be mocked (important for testing orchestrator)."""
    with patch('claude.skills.architect.task_separator.task_separator.main') as mock_main:
        mock_main.return_value = {"valid": True, "independent_pairs": [[1, 2]]}

        # Call orchestrator code that uses skill
        from coffee_maker.orchestrator.continuous_work_loop import OrchestratorWorkLoop
        # ... test orchestrator with mocked skill
```

---

## Implementation Plan

### Phase 1: Directory Restructuring (1 hour)

**Step 1.1: Add `__init__.py` Files** (15 min)
```bash
# Create package structure
touch .claude/skills/__init__.py
touch .claude/skills/shared/__init__.py
touch .claude/skills/architect/__init__.py

# Add __init__.py to all skill directories
find .claude/skills -type d -exec touch {}/__init__.py \;
```

**Step 1.2: Rename Hyphenated Directories** (30 min)
```bash
# Architect skills
cd .claude/skills/architect
mv task-separator task_separator
mv merge-worktree-branches merge_worktree_branches
mv architecture-reuse-check architecture_reuse_check
mv code-review-history code_review_history
mv dependency-conflict-resolver dependency_conflict_resolver

# Shared skills
cd .claude/skills/shared
mv bug-tracking bug_tracking

# Root-level skills (move to shared)
cd .claude/skills
mv git-workflow-automation shared/git_workflow_automation
mv proactive-refactoring-analysis architect/proactive_refactoring_analysis
```

**Step 1.3: Verify Structure** (15 min)
```bash
# Check all skills have __init__.py
find .claude/skills -name "*.py" -path "*/skills/*" | grep -v __pycache__

# Verify no hyphenated directories remain
find .claude/skills -type d -name "*-*" | grep -v __pycache__
```

### Phase 2: Import Refactoring (2-3 hours)

**Step 2.1: Update Orchestrator `continuous_work_loop.py`** (30 min)

**File**: `coffee_maker/orchestrator/continuous_work_loop.py`

**Change 1**: Add import at top of file
```python
# Add after existing imports
from claude.skills.architect.task_separator.task_separator import main as task_separator_main
```

**Change 2**: Replace dynamic loading (lines 1042-1054)
```python
# OLD (DELETE):
import importlib.util
skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"
if not skill_path.exists():
    return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}
spec = importlib.util.spec_from_file_location("task_separator", skill_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.main({"priority_ids": priority_ids})

# NEW (REPLACE WITH):
try:
    result = task_separator_main({"priority_ids": priority_ids})
    return result
except ImportError as e:
    logger.error(f"Failed to import task_separator skill: {e}")
    return {"valid": False, "reason": f"task_separator skill not available: {e}"}
except Exception as e:
    logger.error(f"Error running task_separator skill: {e}", exc_info=True)
    return {"valid": False, "reason": f"Error: {e}"}
```

**Step 2.2: Update Orchestrator `parallel_execution_coordinator.py`** (30 min)

**File**: `coffee_maker/orchestrator/parallel_execution_coordinator.py`

**Change**: Same as Step 2.1 (lines 227-234)
```python
# Add import at top
from claude.skills.architect.task_separator.task_separator import main as task_separator_main

# Replace dynamic loading (lines 227-234)
try:
    result = task_separator_main({"priority_ids": priority_ids})
except ImportError as e:
    return {"valid": False, "reason": f"task_separator skill not available: {e}"}
except Exception as e:
    logger.error(f"Error running task_separator skill: {e}", exc_info=True)
    return {"valid": False, "reason": f"Error: {e}"}
```

**Step 2.3: Update SkillLoader (Optional - Dual Mode)** (1 hour)

**File**: `coffee_maker/autonomous/skill_loader.py`

Add import-based loading as primary method, file-based as fallback:

```python
import importlib
from typing import Optional

class SkillLoader:
    def load(self, skill_name: str) -> SkillMetadata:
        """Load a specific skill by name.

        Tries import-based loading first (faster, more reliable),
        falls back to file-based loading (backward compatibility).
        """
        # Try import-based loading first
        module = self._try_import_skill(skill_name)
        if module:
            return SkillMetadata.from_module(module)

        # Fall back to file-based loading (existing logic)
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata.from_skill_md(agent_skill_path)

        shared_skill_path = self.shared_skills_dir / skill_name
        if shared_skill_path.exists():
            return SkillMetadata.from_skill_md(shared_skill_path)

        raise FileNotFoundError(f"Skill '{skill_name}' not found")

    def _try_import_skill(self, skill_name: str) -> Optional[Any]:
        """Try to import skill as Python module.

        Args:
            skill_name: Skill name (e.g., "task_separator")

        Returns:
            Imported module or None if import fails
        """
        # Try agent-specific skill first
        agent_dir = self.agent_type.value.replace("_", "-")
        module_path = f"claude.skills.{agent_dir}.{skill_name}.{skill_name}"

        try:
            return importlib.import_module(module_path)
        except ImportError:
            pass

        # Try shared skill
        module_path = f"claude.skills.shared.{skill_name}.{skill_name}"
        try:
            return importlib.import_module(module_path)
        except ImportError:
            pass

        return None
```

**Step 2.4: Add Error Handling** (30 min)

Ensure all import failures provide clear error messages:
```python
try:
    from claude.skills.architect.task_separator.task_separator import main
except ImportError as e:
    logger.error(
        f"Failed to import task_separator skill: {e}\n"
        f"Make sure .claude/skills/architect/task_separator/ exists and has __init__.py"
    )
    raise
```

### Phase 3: Test Updates (1 hour)

**Step 3.1: Update Existing Tests** (30 min)

**File**: `tests/unit/test_skill_loader.py`

Update any tests that reference old hyphenated paths:
```python
# OLD:
skill_dir = tmp_path / "shared" / "test-skill"

# NEW:
skill_dir = tmp_path / "shared" / "test_skill"
```

**Step 3.2: Add Import-Based Tests** (30 min)

**New File**: `tests/unit/test_skill_imports.py`

```python
"""Test skills can be imported as Python modules."""

import importlib
import pytest


class TestSkillImports:
    """Test skill import functionality."""

    def test_import_task_separator(self):
        """Test task_separator skill can be imported."""
        from claude.skills.architect.task_separator.task_separator import main
        assert callable(main)

    def test_import_merge_worktree_branches(self):
        """Test merge_worktree_branches skill can be imported."""
        from claude.skills.architect.merge_worktree_branches.merge_worktree_branches import main
        assert callable(main)

    def test_all_skills_importable(self):
        """Test all skills can be imported without errors."""
        skills = [
            "claude.skills.architect.task_separator.task_separator",
            "claude.skills.architect.merge_worktree_branches.merge_worktree_branches",
            # Add all other skills
        ]

        for skill_path in skills:
            try:
                importlib.import_module(skill_path)
            except ImportError as e:
                pytest.fail(f"Failed to import {skill_path}: {e}")

    def test_skill_mocking(self):
        """Test skills can be mocked for testing."""
        from unittest.mock import patch

        with patch('claude.skills.architect.task_separator.task_separator.main') as mock_main:
            mock_main.return_value = {"valid": True}

            # Import and call
            from claude.skills.architect.task_separator.task_separator import main
            result = main({})

            assert result == {"valid": True}
            mock_main.assert_called_once()
```

---

## Migration Strategy

### Backward Compatibility

**Goal**: Ensure all existing code works during and after migration.

**Approach**:
1. **Phase 1**: Directory restructuring (no code changes yet)
   - Old code still uses `importlib.util` (works with new directory names)
   - New directory names don't break file path lookups (just rename, no moves)

2. **Phase 2**: Add import-based loading (dual mode)
   - SkillLoader tries import first, falls back to file-based
   - Old code gradually migrated to imports

3. **Phase 3**: Remove file-based loading (future, not in scope)
   - After all code migrated to imports
   - Clean up SkillLoader fallback logic

### Rollback Plan

If issues occur:
1. **Immediate Rollback** (5 min): Revert directory renames via git
   ```bash
   git checkout HEAD -- .claude/skills/
   ```

2. **Partial Rollback** (10 min): Revert orchestrator changes, keep directory structure
   ```bash
   git checkout HEAD -- coffee_maker/orchestrator/
   ```

3. **Full Rollback** (15 min): Revert entire branch
   ```bash
   git reset --hard HEAD~1
   ```

### Validation Steps

**After each phase**:
1. Run tests: `pytest -v`
2. Check skill loading: `poetry run orchestrator --validate-skills`
3. Manual verification: Test parallel execution with task-separator skill
4. Check git status: `git status` (ensure no unexpected changes)

---

## Testing Strategy

### Unit Tests

**Test Coverage**:
- ✅ Import all skills (no ImportError)
- ✅ Call skill main() functions with test data
- ✅ Mock skills for orchestrator tests
- ✅ SkillLoader import-based loading
- ✅ SkillLoader file-based fallback
- ✅ Error handling (import failures)

**Test Files**:
1. `tests/unit/test_skill_imports.py` (NEW)
   - Test all skills importable
   - Test skill mocking

2. `tests/unit/test_skill_loader.py` (UPDATED)
   - Update paths (hyphenated → underscored)
   - Add import-based loading tests

3. `tests/unit/test_orchestrator_skills.py` (NEW)
   - Test orchestrator with imported skills
   - Test orchestrator with mocked skills

### Integration Tests

**Test Scenarios**:
1. **Orchestrator Parallel Execution**:
   - Load 2-3 priorities
   - Run task_separator skill
   - Verify independent pairs detected
   - Verify conflicts detected

2. **End-to-End Skill Execution**:
   - Start orchestrator
   - Run full work loop
   - Verify skills load and execute correctly

### Manual Testing

**Test Checklist**:
- [ ] Run orchestrator with `--dry-run` flag
- [ ] Verify task-separator skill loads
- [ ] Check logs for import errors
- [ ] Test with real priorities (PRIORITY 23, 24)
- [ ] Verify parallel execution still works

---

## Rollout Plan

### Pre-Rollout (Before Implementation)

1. **Announce Change** (5 min):
   - Notify team of upcoming refactoring
   - Explain benefits (IDE support, type safety)

2. **Backup Current State** (5 min):
   ```bash
   git branch backup-before-skill-refactoring
   ```

3. **Create Rollback Script** (10 min):
   ```bash
   # scripts/rollback_skill_refactoring.sh
   #!/bin/bash
   echo "Rolling back skill refactoring..."
   git checkout backup-before-skill-refactoring -- .claude/skills/
   git checkout backup-before-skill-refactoring -- coffee_maker/orchestrator/
   echo "Rollback complete."
   ```

### Rollout (Implementation)

1. **Phase 1: Directory Restructuring** (1 hour)
   - Execute Step 1.1-1.3
   - Run tests: `pytest -v`
   - Commit: `git commit -m "refactor: Rename skill directories to use underscores (PEP 8)"`

2. **Phase 2: Import Refactoring** (2-3 hours)
   - Execute Step 2.1-2.4
   - Run tests: `pytest -v`
   - Commit: `git commit -m "refactor: Replace importlib.util with standard imports for skills"`

3. **Phase 3: Test Updates** (1 hour)
   - Execute Step 3.1-3.2
   - Run tests: `pytest -v`
   - Commit: `git commit -m "test: Add import-based skill tests"`

### Post-Rollout (Verification)

1. **Run Full Test Suite** (5 min):
   ```bash
   pytest
   pre-commit run --all-files
   ```

2. **Verify Orchestrator** (10 min):
   ```bash
   poetry run orchestrator --validate-skills
   poetry run orchestrator --dry-run
   ```

3. **Monitor Production** (1 week):
   - Check logs for import errors
   - Monitor skill execution success rate
   - Check Langfuse for skill performance

---

## Risks & Mitigations

### Risk 1: Import Path Errors

**Risk**: Typos in import paths cause ImportError at runtime

**Likelihood**: Medium (manual typing required)

**Impact**: High (orchestrator fails to load skills)

**Mitigation**:
- Use IDE autocomplete (catches typos immediately)
- Add `test_all_skills_importable()` test (runs on CI)
- Run `mypy` to validate imports before commit

**Rollback**: Revert orchestrator changes via git

### Risk 2: Circular Import Dependencies

**Risk**: Skills import each other, creating circular dependencies

**Likelihood**: Low (skills currently independent)

**Impact**: Medium (import fails at startup)

**Mitigation**:
- Review skill dependencies before migration
- Use lazy imports if needed (`import` inside function)
- Add circular import detection to tests

**Rollback**: Revert to file-based loading (dual-mode fallback)

### Risk 3: File Path Breakage

**Risk**: Renamed directories break file path references (SKILL.md, scripts)

**Likelihood**: Medium (many file paths in codebase)

**Impact**: Medium (skills fail to load metadata)

**Mitigation**:
- Search codebase for all skill path references: `grep -r "task-separator" .`
- Update all references before commit
- Add integration test for skill metadata loading

**Rollback**: Revert directory renames via git

### Risk 4: Test Failures

**Risk**: Existing tests fail after refactoring

**Likelihood**: Medium (many tests reference skill paths)

**Impact**: Medium (can't merge without passing tests)

**Mitigation**:
- Update tests incrementally (one skill at a time)
- Run tests after each change
- Fix failures immediately (don't accumulate)

**Rollback**: Revert test changes via git

### Risk 5: Performance Regression

**Risk**: Import-based loading slower than file-based

**Likelihood**: Very Low (imports are faster, not slower)

**Impact**: Low (skill loading is not a bottleneck)

**Mitigation**:
- Benchmark before/after with `pytest --benchmark`
- Verify import overhead <10ms per skill
- Cache imported modules if needed

**Rollback**: N/A (performance should improve, not regress)

---

## Success Metrics

### Implementation Success

**Criteria**:
- ✅ All skills renamed to use underscores (PEP 8 compliant)
- ✅ All `importlib.util` code removed from orchestrator
- ✅ All tests pass (100% pass rate)
- ✅ No import errors in logs
- ✅ Pre-commit hooks pass (black, flake8, mypy)

### Quality Metrics

**Before Refactoring**:
- Skill loading: 15 lines of code (dynamic loading)
- IDE autocomplete: ❌ Not supported
- Type checking: ❌ Not supported
- Test mocking: ❌ Hard to mock
- Error messages: "File not found: /path/to/skill"

**After Refactoring**:
- Skill loading: 9 lines of code (40% reduction)
- IDE autocomplete: ✅ Full support
- Type checking: ✅ mypy validates imports
- Test mocking: ✅ Easy (`@patch('claude.skills...')`)
- Error messages: "ImportError: No module named 'claude.skills.architect.task_separator'"

### Performance Metrics

**Before**:
- Skill load time: ~5-10ms (file reading + dynamic module creation)
- Import errors: Runtime (when skill called)

**After**:
- Skill load time: ~1-2ms (import cached after first use)
- Import errors: Startup (fail fast)

**Target**: ≥50% faster skill loading

---

## Definition of Done

### Code Complete

- [ ] All skill directories renamed to use underscores
- [ ] All `__init__.py` files added to skill directories
- [ ] All `importlib.util` code replaced with standard imports
- [ ] SkillLoader updated to support import-based loading
- [ ] All orchestrator skill calls use imports
- [ ] All file path references updated

### Testing Complete

- [ ] All existing tests pass (100% pass rate)
- [ ] New import-based tests added and passing
- [ ] Integration tests pass (orchestrator parallel execution)
- [ ] Manual testing complete (orchestrator --dry-run)
- [ ] No import errors in logs

### Code Quality

- [ ] Pre-commit hooks pass (black, flake8, mypy)
- [ ] No PEP 8 violations (all directories use underscores)
- [ ] Type hints valid (mypy --strict)
- [ ] Code coverage ≥80%

### Documentation

- [ ] SPEC-025 created and approved
- [ ] ROADMAP.md updated (PRIORITY 25 → Complete)
- [ ] Commit messages descriptive
- [ ] Code comments added for import logic

### Deployment

- [ ] Changes merged to `roadmap` branch
- [ ] CI pipeline passes (all tests, linting)
- [ ] Orchestrator verified in production
- [ ] No rollback needed (stable for 1 week)

---

## Future Work

### Phase 2: Remove File-Based Loading (Future)

After all code migrated to imports:
- Remove file-based fallback from SkillLoader
- Delete `SkillMetadata.from_skill_md()` method
- Simplify SkillLoader (import-only)

**Timeline**: 3-6 months after import-based loading proven stable

### Phase 3: Type Hints for Skills (Future)

Add type hints to all skill `main()` functions:
```python
from typing import TypedDict

class TaskSeparatorInput(TypedDict):
    priority_ids: List[int]

class TaskSeparatorOutput(TypedDict):
    valid: bool
    independent_pairs: List[Tuple[int, int]]
    conflicts: Dict[str, List[str]]

def main(input: TaskSeparatorInput) -> TaskSeparatorOutput:
    ...
```

**Benefits**:
- ✅ mypy validates skill input/output types
- ✅ IDE autocomplete for skill parameters
- ✅ Catch type errors before runtime

**Timeline**: After Phase 1 stable (this spec)

### Phase 4: Skill Versioning (Future)

Add version compatibility checks:
```python
# claude/skills/architect/task_separator/__init__.py
__version__ = "1.0.0"
__requires_python__ = ">=3.10"
__requires_packages__ = ["pydantic>=2.0"]
```

**Benefits**:
- ✅ Prevent version incompatibilities
- ✅ Clear dependency requirements
- ✅ Easier skill upgrades

**Timeline**: When multiple skill versions exist

---

## References

- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python Import System](https://docs.python.org/3/reference/import.html)
- [importlib Documentation](https://docs.python.org/3/library/importlib.html)
- [SPEC-055: Claude Skills Phase 1](./SPEC-055-claude-skills-phase-1-foundation.md)
- [SPEC-108: Parallel Agent Execution](./SPEC-108-parallel-agent-execution-with-git-worktree.md)
- [ADR-002: Integrate Claude Skills](../decisions/ADR-002-integrate-claude-skills.md)
- [PRIORITY 25: Refactor Skill Loading](../../roadmap/ROADMAP.md)

---

## Appendix A: Complete File Rename Checklist

```bash
# Architect skills
.claude/skills/architect/task-separator/ → task_separator/
.claude/skills/architect/merge-worktree-branches/ → merge_worktree_branches/
.claude/skills/architect/architecture-reuse-check/ → architecture_reuse_check/
.claude/skills/architect/code-review-history/ → code_review_history/
.claude/skills/architect/dependency-conflict-resolver/ → dependency_conflict_resolver/

# Shared skills
.claude/skills/shared/bug-tracking/ → bug_tracking/

# Root-level skills (to move)
.claude/skills/git-workflow-automation/ → shared/git_workflow_automation/
.claude/skills/proactive-refactoring-analysis/ → architect/proactive_refactoring_analysis/

# Other hyphenated directories (if any)
find .claude/skills -type d -name "*-*" | grep -v __pycache__
```

---

## Appendix B: Import Path Mapping

| Skill | Old Path (File) | New Path (Import) |
|-------|----------------|-------------------|
| task-separator | `.claude/skills/architect/task-separator/task_separator.py` | `claude.skills.architect.task_separator.task_separator` |
| merge-worktree-branches | `.claude/skills/architect/merge-worktree-branches/merge_worktree_branches.py` | `claude.skills.architect.merge_worktree_branches.merge_worktree_branches` |
| bug-tracking | `.claude/skills/shared/bug-tracking/bug_tracking.md` | `claude.skills.shared.bug_tracking.bug_tracking` |
| git-workflow-automation | `.claude/skills/git-workflow-automation/...` | `claude.skills.shared.git_workflow_automation.git_workflow_automation` |

---

## Appendix C: Example Refactored Code

**Before** (orchestrator/continuous_work_loop.py):
```python
def _can_run_parallel(self, priority_ids: List[int]) -> Dict[str, Any]:
    try:
        import importlib.util
        skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"

        if not skill_path.exists():
            return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}

        spec = importlib.util.spec_from_file_location("task_separator", skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.main({"priority_ids": priority_ids})
        return result
    except Exception as e:
        logger.error(f"Error running task-separator skill: {e}", exc_info=True)
        return {"valid": False, "reason": f"Error: {e}"}
```

**After** (orchestrator/continuous_work_loop.py):
```python
from claude.skills.architect.task_separator.task_separator import main as task_separator_main

def _can_run_parallel(self, priority_ids: List[int]) -> Dict[str, Any]:
    try:
        result = task_separator_main({"priority_ids": priority_ids})
        return result
    except ImportError as e:
        logger.error(f"Failed to import task_separator skill: {e}")
        return {"valid": False, "reason": f"task_separator skill not available: {e}"}
    except Exception as e:
        logger.error(f"Error running task_separator skill: {e}", exc_info=True)
        return {"valid": False, "reason": f"Error: {e}"}
```

**Improvements**:
- ✅ 16 lines → 10 lines (37% reduction)
- ✅ Clearer error handling (ImportError vs. Exception)
- ✅ IDE autocomplete works for `task_separator_main`
- ✅ Can mock: `@patch('claude.skills.architect.task_separator.task_separator.main')`
- ✅ Import failure caught at module load (startup), not runtime

---

**End of Specification**
