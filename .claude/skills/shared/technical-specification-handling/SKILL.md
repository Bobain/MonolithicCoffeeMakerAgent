---
name: technical-specification-handling
version: 1.0.0
agent: shared
scope: shared
description: Unified specification file handling for architect and code_developer
triggers:
  - Create technical specification
  - Find technical specification
  - Update technical specification
  - Clean specification
  - Summarize specification
requires:
  - pathlib
  - re
---

# Technical Specification Handling Skill

**Version**: 1.0.0
**Scope**: Shared (architect, code_developer)
**Purpose**: Unified specification file handling to ensure consistency

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
    """Find spec file for a priority.

    Args:
        priority: Dict with keys:
            - "number": Priority number (e.g., "20")
            - "title": Title (e.g., "US-104 - Orchestrator...")
            - "name": Name (e.g., "US-104" or "PRIORITY 20")

    Returns:
        Path to spec file or None
    """
    # 1. Extract US number from title
    us_match = re.search(r'US-(\d+)', priority['title'])
    us_number = us_match.group(1) if us_match else None

    # 2. Try specs directory
    specs_dir = Path("docs/architecture/specs")

    patterns = []

    # PRIMARY: Try US number (e.g., SPEC-104-*.md)
    if us_number:
        patterns.extend([
            f"SPEC-{us_number}-*.md",
            f"SPEC-{us_number.zfill(3)}-*.md",
        ])

    # FALLBACK: Try priority number (backward compatibility)
    priority_num = priority['number']
    patterns.extend([
        f"SPEC-{priority_num}-*.md",
        f"SPEC-{priority_num.replace('.', '-')}-*.md",
    ])

    # Search for first match
    for pattern in patterns:
        matches = list(specs_dir.glob(pattern))
        if matches:
            return matches[0]  # Return first match

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
**Status**: Active
**Priority**: CRITICAL (Infrastructure)
**Agents**: architect, code_developer (shared)
