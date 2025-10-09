# Single Roadmap Enforcement

**Date**: 2025-10-09
**Purpose**: Document how we enforce the "one roadmap" rule
**Status**: ✅ Implemented and Active

---

## 🎯 The Rule

**There is ONE and ONLY ONE roadmap file**: `docs/ROADMAP.md`

This file is the **SINGLE SOURCE OF TRUTH** for:
- All project priorities
- Feature specifications
- Implementation status
- Timeline and planning

**Used by**:
- 🤖 Autonomous Daemon
- 🎯 Project Manager CLI
- 👨‍💻 Human Developers
- 🔧 CI/CD Systems

---

## 🛡️ Enforcement Mechanisms

We enforce this rule at **multiple levels** to prevent accidents:

### 1. Documentation (Level 1)

**Files**:
- `README.md` - Prominent warning at top
- `docs/README_DOCS.md` - Complete documentation structure guide
- `docs/ROADMAP.md` - References itself as single source of truth

**Purpose**: Educate developers about the rule

---

### 2. Code-Level Validation (Level 2) ✅ **ACTIVE**

**File**: `coffee_maker/config.py`

**Implementation**:
```python
# Validates on import
validate_single_roadmap()

# Raises RuntimeError if multiple roadmap files detected
if unofficial_roadmaps:
    raise RuntimeError(
        "ERROR: Multiple roadmap files detected!\n"
        "Only docs/ROADMAP.md is allowed."
    )
```

**When It Runs**:
- Every time `coffee_maker` package is imported
- During tests
- During daemon startup
- During CLI usage

**What It Detects**:
- Any file in `docs/` with "roadmap" in the name (case-insensitive)
- Excludes official `ROADMAP.md`
- Lists unauthorized files with paths

**Example Error**:
```
RuntimeError: ERROR: Multiple roadmap files detected!

Only docs/ROADMAP.md is allowed.

Found unauthorized roadmap files:
  - docs/roadmap_v2.md
  - docs/ROADMAP_backup.md

Please delete these files and use only the official ROADMAP.md.
See docs/README_DOCS.md for documentation guidelines.
```

---

### 3. Git Hooks (Level 3) - Future

**File**: `.git/hooks/pre-commit` (to be created)

```bash
#!/bin/bash
# Prevent committing multiple roadmap files

roadmap_count=$(find docs -iname "*roadmap*.md" -not -name "ROADMAP.md" | wc -l)

if [ $roadmap_count -gt 0 ]; then
    echo "❌ ERROR: Multiple roadmap files detected!"
    echo "Only docs/ROADMAP.md is allowed."
    find docs -iname "*roadmap*.md" -not -name "ROADMAP.md"
    echo ""
    echo "Please delete these files before committing."
    exit 1
fi
```

**When It Runs**: Before every git commit

**Status**: Not yet implemented (planned for PRIORITY 2)

---

### 4. CI/CD Validation (Level 4) - Future

**File**: `.github/workflows/validate_docs.yml` (to be created)

```yaml
name: Validate Documentation Structure

on: [push, pull_request]

jobs:
  validate-roadmap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate single roadmap
        run: |
          count=$(find docs -iname "*roadmap*.md" -not -name "ROADMAP.md" | wc -l)
          if [ $count -gt 0 ]; then
            echo "ERROR: Multiple roadmap files detected"
            find docs -iname "*roadmap*.md" -not -name "ROADMAP.md"
            exit 1
          fi
          echo "✅ Validation passed: Single roadmap confirmed"

      - name: Validate roadmap exists
        run: |
          if [ ! -f docs/ROADMAP.md ]; then
            echo "ERROR: docs/ROADMAP.md not found!"
            exit 1
          fi
          echo "✅ Roadmap exists at correct path"
```

**When It Runs**: On every push and pull request

**Status**: Not yet implemented (planned for PRIORITY 2)

---

### 5. Daemon Safety Check (Level 5) - Future

**File**: `coffee_maker/autonomous/minimal_daemon.py`

```python
def __init__(self, roadmap_path: str = None):
    # Always use config.ROADMAP_PATH, ignore parameter if provided
    if roadmap_path and roadmap_path != str(config.ROADMAP_PATH):
        logger.warning(
            f"Ignoring custom roadmap path: {roadmap_path}\n"
            f"Using official roadmap: {config.ROADMAP_PATH}"
        )

    self.roadmap_path = config.ROADMAP_PATH

    # Validate on startup
    config.validate_single_roadmap()
```

**Purpose**: Prevent daemon from using alternative roadmap files

**Status**: Will be implemented with daemon (PRIORITY 1)

---

## 🔍 Current Status

### ✅ Implemented (Active Now)

1. **Documentation** - README.md, docs/README_DOCS.md
2. **Code Validation** - coffee_maker/config.py with runtime checks
3. **Constants** - ROADMAP_PATH enforced in config

### 📋 Planned (Future Priorities)

4. **Git Hooks** - Pre-commit validation
5. **CI/CD** - GitHub Actions validation
6. **Daemon Safety** - Startup checks

---

## 🧪 Testing

### Test That Validation Works

```python
# Test 1: Normal case (should pass)
from coffee_maker.config import ROADMAP_PATH
print(f"✅ {ROADMAP_PATH}")

# Test 2: Create unauthorized file (should fail)
Path("docs/roadmap_test.md").write_text("test")
try:
    importlib.reload(coffee_maker.config)
except RuntimeError as e:
    print(f"✅ Caught unauthorized file: {e}")
finally:
    Path("docs/roadmap_test.md").unlink()  # cleanup
```

### Test File Lock Mechanism

```python
from filelock import FileLock
from coffee_maker.config import ROADMAP_PATH, ROADMAP_LOCK_PATH

with FileLock(ROADMAP_LOCK_PATH):
    content = ROADMAP_PATH.read_text()
    # Modify content
    ROADMAP_PATH.write_text(new_content)
```

---

## 📊 Benefits of Enforcement

### Prevents Common Mistakes

❌ **Without Enforcement**:
```
docs/
├── ROADMAP.md          # Official
├── roadmap_v2.md       # Oops, created by mistake
├── ROADMAP_backup.md   # Oops, saved a backup
└── roadmap_draft.md    # Oops, working draft
```
→ Daemon reads `roadmap_v2.md`, PM CLI reads `ROADMAP.md` → CONFLICT!

✅ **With Enforcement**:
```
docs/
└── ROADMAP.md          # Only one, everyone uses it
```
→ Daemon and PM CLI read the SAME file → NO CONFLICT!

### Ensures Synchronization

**Before**:
- User edits `ROADMAP.md`
- Daemon reads `roadmap_daemon.md` (stale!)
- Conflict and confusion

**After**:
- User edits `ROADMAP.md` (with filelock)
- Daemon reads `ROADMAP.md` (same file!)
- Perfect synchronization

---

## 🚨 What to Do If You Need Multiple Views

**Wrong Approach** ❌:
```
docs/
├── ROADMAP.md
├── roadmap_frontend.md    # Separate roadmap for frontend
└── roadmap_backend.md     # Separate roadmap for backend
```

**Right Approach** ✅:
```
docs/
└── ROADMAP.md             # One roadmap with sections
    ├── PRIORITY 1: Backend Feature X
    ├── PRIORITY 2: Frontend Feature Y
    └── PRIORITY 3: Backend Feature Z
```

**Or** ✅:
```
docs/
├── ROADMAP.md             # Main roadmap (references details)
├── BACKEND_DESIGN.md      # Design doc (NOT a roadmap)
└── FRONTEND_DESIGN.md     # Design doc (NOT a roadmap)
```

**Key Principle**: Design docs are OK, but only ONE roadmap!

---

## 📝 Checklist for Developers

Before creating a new document:

- [ ] Is this a priority/task? → Add to `ROADMAP.md`
- [ ] Is this design/architecture? → Create `PRIORITY_X_DESIGN.md`
- [ ] Is this a summary/changelog? → Create `CHANGELOG_DATE_topic.md`
- [ ] Is this historical? → Create `*_summary.md`
- [ ] Does it have "roadmap" in the name? → **STOP! Use ROADMAP.md instead**

---

## 🎯 Success Metrics

**Goal**: Zero unauthorized roadmap files

**Current**: ✅ 0 unauthorized files
- Only `docs/ROADMAP.md` exists
- `ROADMAP_UPDATE_2025_10_09.md` renamed to `CHANGELOG_2025_10_09_database_guardrails.md`

**Monitoring**:
```bash
# Check for unauthorized files
find docs -iname "*roadmap*.md" -not -name "ROADMAP.md"

# Should return nothing
```

---

## 🔗 Related Documents

- `README.md` - Project overview with roadmap warning
- `docs/README_DOCS.md` - Complete documentation structure
- `docs/ROADMAP.md` - The one and only roadmap
- `coffee_maker/config.py` - Code-level enforcement

---

## 📞 Questions?

**Q: Can I create a backup of ROADMAP.md?**
A: Use git! `git log docs/ROADMAP.md` shows all history. No separate backup files needed.

**Q: Can I create a draft roadmap while planning?**
A: Edit ROADMAP.md directly. Use git branches if you want to experiment.

**Q: What if I need project-specific roadmaps (frontend, backend)?**
A: Use sections in the main ROADMAP.md. All priorities in one file.

**Q: What if the daemon and I edit ROADMAP.md at the same time?**
A: File lock prevents this! One of you waits while the other edits.

**Q: Can I use a different name like ROADMAP.yaml or roadmap.json?**
A: No! Only `docs/ROADMAP.md` in markdown format. Tools expect this exact file.

---

**Status**: ✅ Enforced at code level, documented for humans
**Next**: Add git hooks and CI/CD validation (PRIORITY 2)
