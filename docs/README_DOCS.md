# Documentation Directory Structure

**Last Updated**: 2025-10-09

---

## ⚠️ CRITICAL: Single Source of Truth

### 📋 **ROADMAP.md** - THE ONE AND ONLY ROADMAP

**Location**: `docs/roadmap/ROADMAP.md`

**Purpose**: The **SINGLE SOURCE OF TRUTH** for all project priorities, features, and planning.

**Who Uses It**:
- ✅ **Project Manager CLI** (`coffee-roadmap`) - Reads and updates this file
- ✅ **Autonomous Daemon** (Claude CLI daemon) - Reads and updates this file
- ✅ **Human Developers** - Plan features by editing this file
- ✅ **CI/CD Systems** - Parse this file for automation

**IMPORTANT RULES**:
1. ❌ **NEVER create another roadmap file** (no ROADMAP_v2.md, roadmap_backup.md, etc.)
2. ❌ **NEVER duplicate roadmap content** into other files
3. ✅ **ALWAYS edit ROADMAP.md directly** (use filelock if needed)
4. ✅ **ALWAYS reference ROADMAP.md** in code (never hardcode paths to other files)

**File Lock**: Both Project Manager and Daemon use `filelock` library to prevent concurrent edits:
```python
from filelock import FileLock

ROADMAP_LOCK = "/tmp/roadmap.lock"

with FileLock(ROADMAP_LOCK, timeout=10):
    # Edit ROADMAP.md safely
    content = Path("docs/roadmap/ROADMAP.md").read_text()
    # ... modify content ...
    Path("docs/roadmap/ROADMAP.md").write_text(new_content)
```

**Docker Volume**: Daemon shares the SAME file via Docker volume:
```yaml
volumes:
  - ./docs/roadmap/ROADMAP.md:/project/docs/roadmap/ROADMAP.md:rw  # SAME FILE!
```

---

## 📚 Supporting Documentation Files

These files are **documentation ABOUT** the roadmap, not alternative roadmaps:

### Design Documents (Detailed Specifications)

- **`PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`** - Database synchronization architecture (450 lines)
  - Problem analysis
  - 4 architectural options
  - Data ownership matrix
  - Implementation guidelines

- **`PROJECT_MANAGER_MVP_DESIGN.md`** - Project Manager CLI design (696 lines)
  - Docker configuration
  - Database guardrails
  - CLI commands spec
  - Implementation plan

- **`DAEMON_FIRST_STRATEGY.md`** - Autonomous daemon implementation guide
  - Complete code structure (~500 LOC)
  - 5-day timeline
  - Risk mitigation
  - Success criteria

### Summary Documents (Changelogs & Updates)

- **`CHANGELOG_2025_10_09_database_guardrails.md`** - Summary of database decisions
  - Key decisions made
  - Architecture choices
  - Success criteria

- **`PRIORITY_REORGANIZATION_2025_10_09.md`** - Rationale for daemon-first approach
  - New priority order
  - Timeline comparison
  - Risk mitigation

- **`READY_TO_BUILD_DAEMON.md`** - Final summary before implementation
  - All documents created
  - Next steps
  - Questions for user

### Historical Documents (Past Work)

- **`sprint1_improvements_summary.md`** - Sprint 1 refactoring results
- **`code_improvements_2025_01.md`** - Code analysis report
- **`refactoring_complete_summary.md`** - Architecture refactoring results

---

## 🚨 What NOT to Create

❌ **Do NOT create**:
- `ROADMAP_v2.md`
- `roadmap_backup.md`
- `ROADMAP_draft.md`
- `roadmap_project_manager.md`
- `roadmap_daemon.md`
- Any file with "roadmap" in the name that contains priorities/tasks

❌ **Do NOT duplicate**:
- Priority lists into other files
- Task descriptions into separate documents
- Roadmap content into wiki/notion/other systems

---

## ✅ How to Add Documentation

**If you need to document something related to the roadmap**:

### Option 1: Add to Existing ROADMAP.md
If it's a priority, feature, or task → Add directly to `ROADMAP.md`

### Option 2: Create Supporting Design Document
If it's detailed design/architecture → Create new file like:
- `PRIORITY_X_DETAILED_DESIGN.md`
- `FEATURE_X_ARCHITECTURE.md`
- Then **reference** it from ROADMAP.md

### Option 3: Create Changelog Entry
If it's a summary of decisions → Create:
- `CHANGELOG_YYYY_MM_DD_topic.md`

**Example**:
```markdown
# In ROADMAP.md
### 🔴 PRIORITY 3: Feature X
**Reference**: `docs/roadmap/PRIORITY_3_DETAILED_DESIGN.md`

# Create separate file with details
docs/roadmap/PRIORITY_3_DETAILED_DESIGN.md
```

---

## 🔍 How to Find Information

**Looking for current priorities?** → `docs/roadmap/ROADMAP.md`
**Looking for implementation details?** → `docs/roadmap/PRIORITY_X_*_DESIGN.md`
**Looking for decisions made?** → `docs/CHANGELOG_*.md`
**Looking for historical work?** → `docs/*_summary.md`

---

## 🤖 For Autonomous Agents & Tools

**If you're building a tool that reads the roadmap**:

```python
# CORRECT
ROADMAP_PATH = "docs/roadmap/ROADMAP.md"  # Hardcode this path

# WRONG
ROADMAP_PATH = find_roadmap_file()  # Don't search for it
ROADMAP_PATH = "docs/ROADMAP_v2.md"  # Don't use alternative files
```

**If you're building a tool that updates the roadmap**:

```python
from filelock import FileLock
from pathlib import Path

ROADMAP_PATH = Path("docs/roadmap/ROADMAP.md")
ROADMAP_LOCK = FileLock("/tmp/roadmap.lock")

def update_roadmap(changes):
    with ROADMAP_LOCK:
        content = ROADMAP_PATH.read_text()
        new_content = apply_changes(content, changes)
        ROADMAP_PATH.write_text(new_content)
```

---

## 📊 File Structure Summary

```
docs/
├── ROADMAP.md                                    ⭐ SINGLE SOURCE OF TRUTH
├── README_DOCS.md                                📖 This file
│
├── PRIORITY_*_DESIGN.md                          🏗️  Detailed designs
│   ├── PRIORITY_1.5_DATABASE_SYNC_DESIGN.md
│   └── PROJECT_MANAGER_MVP_DESIGN.md
│
├── *_STRATEGY.md                                 📋 Implementation plans
│   ├── DAEMON_FIRST_STRATEGY.md
│   └── PRIORITY_REORGANIZATION_2025_10_09.md
│
├── CHANGELOG_*.md                                📝 Decision summaries
│   └── CHANGELOG_2025_10_09_database_guardrails.md
│
├── READY_TO_*.md                                 ✅ Status summaries
│   └── READY_TO_BUILD_DAEMON.md
│
└── *_summary.md                                  📜 Historical records
    ├── sprint1_improvements_summary.md
    ├── refactoring_complete_summary.md
    └── code_improvements_2025_01.md
```

---

## 🔐 Enforcement

**To prevent accidental roadmap duplication**:

### Git Hooks (Future)
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Prevent creating multiple roadmap files

roadmap_files=$(find docs -name "*oadmap*.md" -not -name "ROADMAP.md" | wc -l)
if [ $roadmap_files -gt 0 ]; then
    echo "ERROR: Found multiple roadmap files!"
    echo "Only docs/roadmap/ROADMAP.md is allowed."
    find docs -name "*oadmap*.md" -not -name "ROADMAP.md"
    exit 1
fi
```

### CI/CD Check (Future)
```yaml
# .github/workflows/validate_docs.yml
- name: Validate single roadmap
  run: |
    count=$(find docs -name "*oadmap*.md" -not -name "ROADMAP.md" | wc -l)
    if [ $count -gt 0 ]; then
      echo "ERROR: Multiple roadmap files detected"
      exit 1
    fi
```

---

## 🎯 Key Takeaways

1. ✅ **docs/roadmap/ROADMAP.md** is the ONLY roadmap file
2. ✅ All tools read/write to this ONE file
3. ✅ Use filelock to prevent concurrent edits
4. ✅ Use Docker volume to share SAME file with daemon
5. ✅ Create supporting docs for details, not alternative roadmaps

**Remember**: One roadmap to rule them all! 📋👑

---

**Last Updated**: 2025-10-09
**Maintainer**: Human + Autonomous Daemon
**Source of Truth**: `docs/roadmap/ROADMAP.md`
