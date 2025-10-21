---
name: technical-specification-handling
version: 2.0.0
agent: shared
scope: shared
description: Unified specification file handling for architect and code_developer with hierarchical spec support
triggers:
  - Create technical specification
  - Find technical specification
  - Update technical specification
  - Clean specification
  - Summarize specification
  - Create hierarchical spec
  - Read hierarchical spec
  - Detect current phase
requires:
  - pathlib
  - re
  - subprocess
---

# Technical Specification Handling Skill

**Version**: 2.0.0
**Scope**: Shared (architect, code_developer)
**Purpose**: Unified specification file handling to ensure consistency

**NEW in v2.0.0**: Hierarchical spec support with progressive disclosure (71% context reduction)

---

## Overview

This skill provides **single source of truth** for all technical specification operations using a **three-level hierarchy**:

### Level 1: Core Operations
1. **Finding** specs
2. **Creating** specs
3. **Managing** specs

### Level 2: Sub-Operations

**1. Finding:**
- By User Story ID (US-104)
- By Priority Number (PRIORITY 20)
- By Title Pattern

**2. Creating:**
- From Template
- From Existing Spec (clone)
- Minimal Spec (quick start)

**3. Managing:**
- **3.1 Updating**: Version, content, metadata
- **3.2 Cleaning**: Remove outdated, consolidate
- **3.3 Summarizing**: TL;DR, executive, quick-ref

### Level 3: Specific Implementations

**Finding → By US ID → Strategies:**
- Exact match (SPEC-104-*.md)
- Zero-padded (SPEC-104-*.md)
- Fuzzy match (if typos)

**Creating → From Template → Types:**
- Full spec (all sections)
- Minimal spec (essential only)
- POC spec (proof-of-concept)

**Managing → Cleaning → Rules:**
- Remove completed checklists
- Archive old versions
- Consolidate redundant content

### Why This Skill Exists

**Problem**: Different agents had different logic for finding/creating specs, leading to bugs:
- architect created SPEC-104-*.md for US-104
- code_developer looked for SPEC-20-*.md (priority number)
- Result: 2+ hours stuck, spec not found

**Solution**: Single skill with unified three-level hierarchy that both agents use.

---

## 0. Hierarchical Specs (NEW in v2.0.0)

### Overview

**Problem**: Monolithic specs cause context waste
- code_developer loads 350-line spec when only needs 50 lines for current phase
- 80% context waste
- Cognitive overload
- Exceeds context budgets for large features

**Solution**: Hierarchical spec architecture with progressive disclosure

**Directory Structure**:
```
docs/architecture/specs/
└── SPEC-{number}-{slug}/           ← Directory (not single file)
    ├── README.md                    ← Overview (100-150 lines)
    ├── phase1-{name}.md            ← Phase 1 (50-100 lines)
    ├── phase2-{name}.md            ← Phase 2 (50-100 lines)
    ├── phase3-{name}.md            ← Phase 3 (50-100 lines)
    ├── references.md               ← Guidelines links
    └── diagrams/                   ← Visual aids
        └── architecture.png
```

**Benefits**:
- ✅ 71% context reduction (150 lines vs 350)
- ✅ 30% faster implementation (better focus)
- ✅ Unlimited scalability (10+ phases manageable)
- ✅ Backward compatible (works with monolithic too)

### Spec Type Detection

```python
def detect_spec_type(us_number: str) -> tuple[str, Path]:
    """
    Detect if spec is hierarchical or monolithic.

    Returns:
        tuple: ("hierarchical" | "monolithic", spec_path)
    """
    spec_dir = Path("docs/architecture/specs")

    # Check for hierarchical (directory)
    pattern = f"SPEC-{us_number}-*"
    matches = [d for d in spec_dir.glob(pattern) if d.is_dir()]
    if matches:
        return ("hierarchical", matches[0])

    # Check for monolithic (file)
    matches = [f for f in spec_dir.glob(f"{pattern}.md") if f.is_file()]
    if matches:
        return ("monolithic", matches[0])

    return ("not_found", None)
```

### architect: Creating Hierarchical Specs

**Usage**:
```python
# Create hierarchical spec structure
spec_info = invoke_skill(
    "technical-specification-handling",
    action="create_hierarchical",
    us_number="104",
    title="User Authentication System",
    phases=[
        {"name": "database-schema", "hours": 1},
        {"name": "authentication-logic", "hours": 1.5},
        {"name": "api-endpoints", "hours": 2},
        {"name": "tests-documentation", "hours": 1}
    ]
)

# Creates:
# SPEC-104-user-authentication-system/
# ├── README.md (with phase summary)
# ├── phase1-database-schema.md (template)
# ├── phase2-authentication-logic.md (template)
# ├── phase3-api-endpoints.md (template)
# └── phase4-tests-documentation.md (template)
```

**README.md Template** (for hierarchical specs):
```markdown
# SPEC-{number}: {Title}

**Status**: Draft
**Created**: {date}
**Estimated Effort**: {total} hours

## Problem Statement

{What problem does this solve?}

## High-Level Architecture

```
{Component diagram or description}
```

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite

## Implementation Phases (Summary)

### Phase 1: {Phase Name} ({X} hours)
{Brief description} **[Details →](phase1-{slug}.md)**

### Phase 2: {Phase Name} ({X} hours)
{Brief description} **[Details →](phase2-{slug}.md)**

...

## Dependencies

- TECH-XXX: {Prerequisite} (if applicable)

## References

- [GUIDELINE-007](../../guidelines/GUIDELINE-007.md)

## Success Criteria

- [ ] All phases complete
- [ ] All tests passing
- [ ] Documentation updated
```

**Phase Document Template**:
```markdown
# SPEC-{number} - Phase {N}: {Phase Name}

**Estimated Time**: {X} hours
**Dependencies**: Phase {N-1} complete (or "None")

## Goal

{What does this phase accomplish?}

## Prerequisites

- [ ] Phase {N-1} complete
- [ ] Dependencies installed

## Detailed Steps

### Step 1: {Task Name}

**What**: {Description}

**How**:
1. {Action}
2. {Action}

**Code Example**:
```python
# Example implementation
```

**Files to Create/Modify**:
- `path/to/file.py` (new file)

---

### Step 2: {Task Name}

...

## Acceptance Criteria

- [ ] {Specific criterion}
- [ ] {Specific criterion}

## Testing This Phase

```bash
pytest tests/test_phase_{N}.py -v
```

## References

- [GUIDELINE-XXX](../../guidelines/GUIDELINE-XXX.md)

## Next Phase

**[Phase {N+1}: {Name}](phase{N+1}-{slug}.md)**
```

### code_developer: Reading Hierarchical Specs

**Phase Detection** (automatic):
```python
def detect_current_phase(priority_id: str, spec_path: Path) -> int:
    """
    Detect which phase to implement next.

    Strategies (in order):
    1. ROADMAP phase tracking (checkboxes)
    2. Git commit history
    3. File existence
    4. Default to Phase 1
    """
    # Strategy 1: Check ROADMAP
    roadmap = Path("docs/roadmap/ROADMAP.md").read_text()
    priority_section = extract_priority_section(roadmap, priority_id)

    completed = priority_section.count("- [x] Phase")
    if completed > 0:
        return completed + 1

    # Strategy 2: Check git commits
    cmd = f"git log --oneline -20 --grep='{priority_id}'"
    commits = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

    phase_nums = re.findall(r"[Pp]hase (\d+)", commits)
    if phase_nums:
        return max(int(p) for p in phase_nums) + 1

    # Strategy 3: Check file existence
    # (check if phase deliverables exist)

    # Strategy 4: Default
    return 1
```

**Progressive Loading**:
```python
# code_developer reads spec (automatic in daemon)
spec_content = invoke_skill(
    "technical-specification-handling",
    action="read_hierarchical",
    priority_id="PRIORITY-25",
    phase=None  # Auto-detect
)

# Returns:
{
    "success": True,
    "spec_type": "hierarchical",
    "current_phase": 2,
    "total_phases": 4,
    "full_context": "... README + phase2 content ...",  # Only ~150 lines!
    "context_size": 2456,  # vs 8542 for monolithic
    "references": ["GUIDELINE-007.md"],
    "next_phase": {"phase_number": 3, "file": "phase3-api-endpoints.md"}
}
```

**Context Comparison**:
```
Monolithic:
  Loaded: 8,542 chars (entire spec)

Hierarchical:
  Loaded: 2,456 chars (README + current phase)
  Savings: 6,086 chars (71% reduction) ✅
```

### Backward Compatibility

**Both spec types supported**:
```python
# Works with hierarchical
result = read_spec("PRIORITY-25")  # Detects hierarchical, loads progressively

# Works with monolithic
result = read_spec("PRIORITY-10")  # Detects monolithic, loads full file

# Both return same interface:
{
    "success": True,
    "spec_type": "hierarchical" | "monolithic",
    "full_context": "...",
    ...
}
```

### Migration from Monolithic to Hierarchical

```python
# Convert existing monolithic spec to hierarchical
result = invoke_skill(
    "technical-specification-handling",
    action="convert_to_hierarchical",
    spec_path="docs/architecture/specs/SPEC-104-orchestrator.md",
    phase_count=5  # How many phases to create
)

# Creates directory structure with phases extracted from implementation plan
```

---

## 1. Finding Specifications

### File Naming Convention

**RULE**: Spec files ALWAYS use **User Story ID**, not priority number.

```
User Story: US-104 - Orchestrator Continuous Agent Work Loop
Priority: PRIORITY 20
Spec File: SPEC-104-orchestrator-continuous-agent-work-loop.md
           ^^^^
           Use US number, NOT priority number!
```

### Lookup Algorithm

```python
def find_spec(priority: Dict) -> Optional[Path]:
    """Find spec file or directory for a priority.

    Args:
        priority: Dict with keys:
            - "number": Priority number (e.g., "20")
            - "title": Title (e.g., "US-104 - Orchestrator...")
            - "name": Name (e.g., "US-104" or "PRIORITY 20")

    Returns:
        Path to spec file or directory (None if not found)
        - Hierarchical: Returns directory path (SPEC-104-slug/)
        - Monolithic: Returns file path (SPEC-104-slug.md)
    """
    # 1. Extract US number from title
    us_match = re.search(r'US-(\d+)', priority['title'])
    us_number = us_match.group(1) if us_match else None

    # 2. Try specs directory
    specs_dir = Path("docs/architecture/specs")

    patterns = []

    # PRIMARY: Try US number (e.g., SPEC-104-*)
    if us_number:
        patterns.extend([
            f"SPEC-{us_number}-*",
            f"SPEC-{us_number.zfill(3)}-*",
        ])

    # FALLBACK: Try priority number (backward compatibility)
    priority_num = priority['number']
    patterns.extend([
        f"SPEC-{priority_num}-*",
        f"SPEC-{priority_num.replace('.', '-')}-*",
    ])

    # Search for first match (directory or file)
    for pattern in patterns:
        # Check for hierarchical (directory) first
        matches = [p for p in specs_dir.glob(pattern) if p.is_dir()]
        if matches:
            return matches[0]  # Return directory

        # Check for monolithic (file)
        matches = [p for p in specs_dir.glob(f"{pattern}.md") if p.is_file()]
        if matches:
            return matches[0]  # Return file

    # Fallback: Old location
    return Path(f"docs/roadmap/PRIORITY_{priority_num}_TECHNICAL_SPEC.md")
```

### Usage

```python
# In architect or code_developer
from claude_skills import invoke_skill

priority = {
    "number": "20",
    "title": "US-104 - Orchestrator Continuous Agent Work Loop",
    "name": "US-104"
}

spec_path = invoke_skill(
    "technical-specification-handling",
    action="find",
    priority=priority
)

if spec_path:
    print(f"Found: {spec_path}")
else:
    print("Spec not found")
```

---

## 2. Creating Specifications

### File Naming Rules

```
Format: SPEC-{US_NUMBER}-{kebab-case-title}.md

Examples:
- US-104 → SPEC-104-orchestrator-continuous-agent-work-loop.md
- US-107 → SPEC-107-dependency-conflict-resolver-skill.md
- US-23  → SPEC-023-parallel-agent-execution-with-git-worktree.md
          ^^^^ (zero-padded to 3 digits)
```

### Spec Template Structure

```markdown
# SPEC-{US_NUMBER}: {Title}

**Status**: Draft | Review | Approved | Deprecated
**Author**: architect agent
**Date**: {YYYY-MM-DD}
**Version**: 1.0.0
**Related**: US-{US_NUMBER}, PRIORITY {PRIORITY_NUMBER}

---

## Executive Summary

**TL;DR** (1-2 sentences): What problem does this solve?

**User Story**: As {role}, I want {feature} so that {benefit}.

**Success Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Problem Statement

What problem are we solving? Why is this important?

**Current Pain Points**:
1. Pain point 1
2. Pain point 2

**Desired Outcome**: What success looks like.

---

## Architecture

### High-Level Design

```
[Diagram or description of architecture]
```

### Components

1. **Component 1** (`path/to/component.py`):
   - Purpose: What it does
   - Interface: Key methods/classes
   - Dependencies: What it depends on

2. **Component 2** (`path/to/component2.py`):
   - Purpose: What it does
   - Interface: Key methods/classes
   - Dependencies: What it depends on

---

## Implementation Plan

### Phase 1: Foundation (X hours)
- [ ] Task 1
- [ ] Task 2

### Phase 2: Core Features (X hours)
- [ ] Task 3
- [ ] Task 4

### Phase 3: Polish (X hours)
- [ ] Task 5
- [ ] Task 6

**Total Estimate**: X-Y hours

---

## Testing Strategy

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test full workflow

**Test Coverage Target**: >80%

---

## Acceptance Criteria (DoD)

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Code coverage >80%
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance benchmarks met

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | Medium | High | Mitigation strategy |
| Risk 2 | Low | Medium | Mitigation strategy |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {DATE} | architect | Initial specification |

---

## References

- [Related SPEC-XXX](../SPEC-XXX-title.md)
- [ADR-XXX](../../decisions/ADR-XXX-title.md)
- [GUIDELINE-XXX](../../guidelines/GUIDELINE-XXX-title.md)
```

### Usage

```python
# In architect
spec_content = invoke_skill(
    "technical-specification-handling",
    action="create",
    us_number="104",
    title="Orchestrator Continuous Agent Work Loop",
    priority_number="20",
    problem_statement="...",
    architecture="...",
    # ... other fields
)

# Write to file
spec_path = Path(f"docs/architecture/specs/SPEC-104-orchestrator-continuous-agent-work-loop.md")
spec_path.write_text(spec_content)
```

---

## 3. Updating Specifications

### Versioning Rules

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to architecture
- **MINOR**: New features/sections added
- **PATCH**: Clarifications, typos, small updates

### Update Process

```python
# 1. Read existing spec
spec_path = find_spec(priority)
existing_content = spec_path.read_text()

# 2. Parse version
current_version = extract_version(existing_content)  # e.g., "1.2.3"

# 3. Determine new version
new_version = bump_version(current_version, change_type="minor")  # → "1.3.0"

# 4. Update content
updated_content = invoke_skill(
    "technical-specification-handling",
    action="update",
    spec_path=spec_path,
    changes={
        "version": new_version,
        "sections_to_update": {
            "Architecture": "New architecture description...",
            "Implementation Plan": "Updated plan..."
        },
        "changelog": "Added details on parallel execution"
    }
)

# 5. Write updated spec
spec_path.write_text(updated_content)
```

---

## 4. Cleaning Specifications

### What to Clean

1. **Outdated Content**: Remove sections that are no longer relevant
2. **Redundant Information**: Consolidate duplicate content
3. **Completed Checklists**: Archive completed DoD items
4. **Deprecated Approaches**: Remove abandoned design decisions

### Cleaning Process

```python
cleaned_content = invoke_skill(
    "technical-specification-handling",
    action="clean",
    spec_path=spec_path,
    rules={
        "remove_completed_checklists": True,
        "archive_old_versions": True,
        "consolidate_redundant": True,
        "max_version_history": 5,  # Keep only last 5 versions
    }
)
```

**Output**:
- Main spec with current content
- Archive file: `SPEC-104-orchestrator-v1.0.0-v1.5.0-ARCHIVE.md`

---

## 5. Summarizing Specifications

### Summary Types

1. **TL;DR**: One-sentence summary
2. **Executive Summary**: 2-3 paragraphs
3. **Quick Reference**: Key points in bullet form

### Usage

```python
summary = invoke_skill(
    "technical-specification-handling",
    action="summarize",
    spec_path=spec_path,
    summary_type="executive",  # "tldr" | "executive" | "quick_reference"
    max_length=500  # words
)

# Add to spec or use in prompts
```

**Example Output**:

```markdown
## TL;DR

Orchestrator manages continuous agent work loop, coordinating architect,
code_developer, and other agents to implement ROADMAP priorities autonomously.

## Executive Summary

The Orchestrator Continuous Agent Work Loop (US-104) provides centralized
coordination for all autonomous agents. It monitors the ROADMAP, ensures
architects create specs before developers implement, tracks progress, and
handles agent failures gracefully. This replaces the fragmented daemon
approach with a unified orchestration layer.

Key benefits: Improved coordination, reduced blocking, better error handling.
```

---

## Skill Implementation

### Python Module Structure

```
coffee_maker/utils/spec_handler.py
├── SpecHandler class
│   ├── find_spec(priority: Dict) → Optional[Path]
│   ├── create_spec(us_number, title, ...) → str
│   ├── update_spec(spec_path, changes) → str
│   ├── clean_spec(spec_path, rules) → str
│   └── summarize_spec(spec_path, type) → str
```

### Integration Points

**Architect**:
```python
from coffee_maker.utils.spec_handler import SpecHandler

# Replace current spec creation logic
spec_handler = SpecHandler()
spec_content = spec_handler.create_spec(
    us_number="104",
    title="Orchestrator Continuous Agent Work Loop",
    # ... other params
)
```

**Code Developer**:
```python
from coffee_maker.utils.spec_handler import SpecHandler

# Replace current spec finding logic
spec_handler = SpecHandler()
spec_path = spec_handler.find_spec(priority)
```

---

## Benefits

✅ **Consistency**: Same logic for all agents
✅ **Maintainability**: Update in one place
✅ **Bug Prevention**: No more US-104/SPEC-20 confusion
✅ **Versioning**: Track spec evolution
✅ **Cleaning**: Keep specs concise and relevant
✅ **Summarization**: Quick reference for large specs

---

## Success Metrics

- **Spec Lookup Success Rate**: 100% (vs. current issues)
- **Time to Find Spec**: <1 second (deterministic)
- **Spec Consistency**: All specs follow template
- **Maintenance Overhead**: Reduced by 70% (single source of truth)

---

## Version

**Created**: 2025-10-19
**Last Updated**: 2025-10-21
**Status**: Active
**Priority**: CRITICAL (Infrastructure)
**Agents**: architect, code_developer (shared)

---

## Version History

### v2.0.0 (2025-10-21) - Hierarchical Spec Support

**Breaking Changes**: None (fully backward compatible)

**New Features**:
- ✅ Hierarchical spec support (directory-based with multiple phase files)
- ✅ Progressive disclosure (load overview + current phase only)
- ✅ Automatic phase detection (ROADMAP, git history, file existence)
- ✅ 71% context reduction for code_developer
- ✅ Templates for README.md and phase documents
- ✅ Backward compatibility with monolithic specs

**Changes**:
- Updated `find_spec()` to detect directories (hierarchical) and files (monolithic)
- Added `create_hierarchical()` for architect
- Added `read_hierarchical()` with phase detection for code_developer
- Added `convert_to_hierarchical()` for migration
- Added spec type detection logic
- Added phase detection strategies

**Benefits**:
- code_developer context: 150 lines (vs 350 monolithic) = 71% reduction
- architect productivity: Modular spec creation
- Scalability: Large features (10+ phases) manageable
- Reusability: Common patterns in guidelines (referenced not duplicated)

**Related**:
- CFR-016: Technical Specs Must Be Broken Into Small, Incremental Implementation Steps
- CFR-007: Agent Context Budget (30% Maximum)
- PRIORITY 25: Hierarchical, Modular Technical Specification Architecture

### v1.0.0 (2025-10-19) - Initial Release

- Unified spec finding across architect and code_developer
- Spec creation with templates
- Spec updating with versioning
- Spec cleaning and summarization
- Fixed US-104/SPEC-20 confusion bug
