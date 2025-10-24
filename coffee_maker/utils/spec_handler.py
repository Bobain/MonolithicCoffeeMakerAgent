"""Technical Specification Handler - Unified spec operations for architect and code_developer.

This module provides a single source of truth for all technical specification operations,
ensuring consistency across all agents.

Usage:
    from coffee_maker.utils.spec_handler import SpecHandler

    handler = SpecHandler()
    spec_path = handler.find_spec(priority)
    spec_content = handler.create_spec(us_number="104", title="Feature Name", ...)
"""

import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpecHandler:
    """Unified technical specification handler for all agents."""

    def __init__(self):
        """Initialize the spec handler."""
        self.specs_dir = Path("docs/architecture/specs")
        self.roadmap_dir = Path("docs/roadmap")

    # ==================== FINDING SPECIFICATIONS ====================

    def find_spec(self, priority: Dict[str, Any]) -> Optional[Path]:
        """Find spec file for a priority.

        Args:
            priority: Dict with keys:
                - "number": Priority number (e.g., "20")
                - "title": Title (e.g., "US-104 - Orchestrator...")
                - "name": Name (e.g., "US-104" or "PRIORITY 20")

        Returns:
            Path to spec file or None

        Examples:
            >>> priority = {"number": "20", "title": "US-104 - Feature"}
            >>> spec_path = handler.find_spec(priority)
            >>> # Returns: docs/architecture/specs/SPEC-104-feature.md
        """
        # 1. Extract US number from title
        us_match = re.search(r"US-(\d+)", priority.get("title", ""))
        us_number = us_match.group(1) if us_match else None

        # 2. Try specs directory with multiple patterns
        patterns = []

        # PRIMARY: Try US number (e.g., SPEC-104-*.md)
        if us_number:
            patterns.extend(
                [
                    f"SPEC-{us_number}-*.md",
                    f"SPEC-{us_number.zfill(3)}-*.md",  # Zero-padded
                ]
            )

        # FALLBACK: Try priority number (backward compatibility)
        priority_num = priority.get("number", "")
        if priority_num:
            patterns.extend(
                [
                    f"SPEC-{priority_num}-*.md",
                    f"SPEC-{priority_num.replace('.', '-')}-*.md",
                ]
            )

        # Search for first match
        for pattern in patterns:
            matches = list(self.specs_dir.glob(pattern))
            if matches:
                logger.debug(f"Found spec using pattern {pattern}: {matches[0]}")
                return matches[0]

        # Fallback: Old location (docs/roadmap/)
        old_path = self.roadmap_dir / f"PRIORITY_{priority_num}_TECHNICAL_SPEC.md"
        if old_path.exists():
            logger.debug(f"Found spec in old location: {old_path}")
            return old_path

        logger.debug(f"No spec found for priority {priority_num}")
        return None

    def find_spec_by_us_id(self, us_id: str) -> Optional[Path]:
        """Find spec by US-XXX identifier.

        Args:
            us_id: US identifier (e.g., "US-104" or "104")

        Returns:
            Path to spec file or None
        """
        # Extract number from US-XXX format
        us_match = re.search(r"(\d+)", us_id)
        if not us_match:
            return None

        us_number = us_match.group(1)

        # Try different patterns
        patterns = [
            f"SPEC-{us_number}-*.md",
            f"SPEC-{us_number.zfill(3)}-*.md",
        ]

        for pattern in patterns:
            matches = list(self.specs_dir.glob(pattern))
            if matches:
                return matches[0]

        return None

    def spec_exists(self, priority: Dict[str, Any]) -> bool:
        """Check if spec exists for priority.

        Args:
            priority: Priority dict

        Returns:
            bool: True if spec exists, False otherwise
        """
        return self.find_spec(priority) is not None

    # ==================== CREATING SPECIFICATIONS ====================

    def create_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str = "",
        user_story: str = "",
        architecture: str = "",
        implementation_plan: str = "",
        testing_strategy: str = "",
        estimated_effort: str = "TBD",
        template_type: str = "full",
    ) -> str:
        """Create technical specification content.

        Args:
            us_number: User story number (e.g., "104")
            title: Feature title (e.g., "Orchestrator Continuous Agent Work Loop")
            priority_number: Priority number (e.g., "20")
            problem_statement: What problem are we solving?
            user_story: As {role}, I want {feature} so that {benefit}
            architecture: Architecture description
            implementation_plan: Step-by-step implementation
            testing_strategy: Testing approach
            estimated_effort: Time estimate (e.g., "40-50 hours")
            template_type: "full", "minimal", or "poc"

        Returns:
            str: Spec file content
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        if template_type == "minimal":
            return self._create_minimal_spec(
                us_number, title, priority_number, problem_statement, estimated_effort, date_str
            )
        elif template_type == "poc":
            return self._create_poc_spec(us_number, title, priority_number, problem_statement, date_str)
        else:
            return self._create_full_spec(
                us_number,
                title,
                priority_number,
                problem_statement,
                user_story,
                architecture,
                implementation_plan,
                testing_strategy,
                estimated_effort,
                date_str,
            )

    def _create_full_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str,
        user_story: str,
        architecture: str,
        implementation_plan: str,
        testing_strategy: str,
        estimated_effort: str,
        date_str: str,
    ) -> str:
        """Create full technical specification."""
        # Default values for optional sections
        default_impl_plan = """### Phase 1: Foundation (X hours)
- [ ] Task 1
- [ ] Task 2

### Phase 2: Core Features (X hours)
- [ ] Task 3
- [ ] Task 4

### Phase 3: Polish (X hours)
- [ ] Task 5
- [ ] Task 6"""

        default_testing = """1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test full workflow

**Test Coverage Target**: >80%"""

        # Use provided values or defaults
        impl_plan_content = implementation_plan or default_impl_plan
        testing_content = testing_strategy or default_testing
        problem_content = problem_statement or "TODO: What problem are we solving? Why is this important?"
        user_story_content = (
            user_story or f"As a developer, I want {title.lower()} so that the system is more effective."
        )
        architecture_content = architecture or "TODO: Add architecture description"

        return f"""# SPEC-{us_number.zfill(3)}: {title}

**Status**: Draft
**Author**: architect agent
**Date**: {date_str}
**Version**: 1.0.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## Executive Summary

**TL;DR**: {problem_content}

**User Story**: {user_story_content}

**Success Criteria**:
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Code coverage >80%
- [ ] Documentation updated

---

## Problem Statement

{problem_content}

**Current Pain Points**:
1. TODO: Pain point 1
2. TODO: Pain point 2

**Desired Outcome**: TODO: What success looks like.

---

## Architecture

### High-Level Design

{architecture_content}

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

{impl_plan_content}

**Total Estimate**: {estimated_effort}

---

## Testing Strategy

{testing_content}

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
| TODO: Risk 1 | Medium | High | Mitigation strategy |
| TODO: Risk 2 | Low | Medium | Mitigation strategy |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {date_str} | architect | Initial specification |

---

## References

- [ROADMAP](../../roadmap/ROADMAP.md)
- Related specs: TODO
- Related ADRs: TODO
"""

    def _create_minimal_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str,
        estimated_effort: str,
        date_str: str,
    ) -> str:
        """Create minimal technical specification."""
        return f"""# SPEC-{us_number.zfill(3)}: {title}

**Status**: Draft
**Author**: architect agent
**Date**: {date_str}
**Version**: 1.0.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## Summary

{problem_statement or "TODO: What are we building and why?"}

---

## Implementation

**Estimated Effort**: {estimated_effort}

**Tasks**:
- [ ] TODO: Task 1
- [ ] TODO: Task 2
- [ ] TODO: Task 3

---

## Acceptance Criteria

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {date_str} | architect | Initial specification |
"""

    def _create_poc_spec(
        self, us_number: str, title: str, priority_number: str, problem_statement: str, date_str: str
    ) -> str:
        """Create POC technical specification."""
        return f"""# SPEC-{us_number.zfill(3)}: {title} (POC)

**Status**: POC
**Author**: architect agent
**Date**: {date_str}
**Version**: 0.1.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## POC Goals

{problem_statement or "TODO: What concepts are we proving?"}

**Key Questions**:
1. TODO: Question 1
2. TODO: Question 2

---

## Scope

**In Scope**:
- TODO: What we're testing
- TODO: Minimal implementation

**Out of Scope**:
- Production code
- Error handling
- Performance optimization

---

## Success Criteria

- [ ] Concept 1 proven
- [ ] Concept 2 proven
- [ ] Concept 3 proven

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | {date_str} | architect | Initial POC specification |
"""

    def generate_spec_filename(self, us_number: str, title: str) -> str:
        """Generate spec filename from US number and title.

        Args:
            us_number: User story number (e.g., "104")
            title: Feature title

        Returns:
            str: Filename (e.g., "SPEC-104-orchestrator-continuous-agent-work-loop.md")
        """
        # Convert title to kebab-case
        kebab_title = title.lower()
        kebab_title = re.sub(r"[^a-z0-9\s-]", "", kebab_title)  # Remove special chars
        kebab_title = re.sub(r"\s+", "-", kebab_title)  # Replace spaces with hyphens
        kebab_title = re.sub(r"-+", "-", kebab_title)  # Collapse multiple hyphens

        return f"SPEC-{us_number.zfill(3)}-{kebab_title}.md"

    def create_hierarchical_spec(
        self,
        us_number: str,
        title: str,
        phases: list,
        problem_statement: str = "",
        architecture: str = "",
        technology_stack: str = "",
    ) -> Path:
        """Create hierarchical specification directory structure.

        Args:
            us_number: User story number (e.g., "104")
            title: Spec title
            phases: List of phase dicts with keys:
                - name: Phase name (e.g., "database-schema")
                - hours: Estimated hours
                - description: Optional phase description
            problem_statement: What problem does this solve?
            architecture: High-level architecture description
            technology_stack: Technologies used

        Returns:
            Path: Path to created spec directory

        Example:
            >>> handler = SpecHandler()
            >>> spec_dir = handler.create_hierarchical_spec(
            ...     us_number="104",
            ...     title="Authentication System",
            ...     phases=[
            ...         {"name": "database", "hours": 1, "description": "Create tables"},
            ...         {"name": "auth-logic", "hours": 2, "description": "Login/logout"}
            ...     ]
            ... )
        """
        # Create directory
        kebab_title = self._slugify(title)
        spec_dir = self.specs_dir / f"SPEC-{us_number.zfill(3)}-{kebab_title}"
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Calculate total hours
        total_hours = sum(phase.get("hours", 0) for phase in phases)

        # Create README.md
        readme_content = self._create_hierarchical_readme(
            us_number,
            title,
            phases,
            total_hours,
            problem_statement,
            architecture,
            technology_stack,
        )

        readme_path = spec_dir / "README.md"
        readme_path.write_text(readme_content)

        # Create phase files
        for i, phase in enumerate(phases, start=1):
            phase_content = self._create_phase_file(
                us_number,
                i,
                phase["name"],
                phase.get("hours", 1),
                phase.get("description", ""),
                len(phases),
            )

            phase_file = spec_dir / f"phase{i}-{phase['name']}.md"
            phase_file.write_text(phase_content)

        logger.info(f"Created hierarchical spec: {spec_dir}")
        return spec_dir

    def _create_hierarchical_readme(
        self,
        us_number: str,
        title: str,
        phases: list,
        total_hours: float,
        problem_statement: str,
        architecture: str,
        technology_stack: str,
    ) -> str:
        """Create README.md for hierarchical spec."""
        date_str = datetime.now().strftime("%Y-%m-%d")

        problem_content = problem_statement or "TODO: What problem does this solve?"
        arch_content = architecture or "TODO: Add architecture description"
        tech_content = (
            technology_stack
            or """- **Language**: Python 3.11+
- **Framework**: TBD
- **Database**: SQLite"""
        )

        # Build phase summary
        phase_summary = ""
        for i, phase in enumerate(phases, start=1):
            phase_name = phase["name"].replace("-", " ").title()
            phase_hours = phase.get("hours", 1)
            phase_desc = phase.get("description", "TODO: Add description")
            phase_summary += f"""### Phase {i}: {phase_name} ({phase_hours} hours)
{phase_desc}

**[Details →](phase{i}-{phase['name']}.md)**

"""

        return f"""# SPEC-{us_number.zfill(3)}: {title}

**Status**: Draft
**Created**: {date_str}
**Estimated Effort**: {total_hours} hours
**Type**: Hierarchical (Progressive Disclosure)

---

## Problem Statement

{problem_content}

---

## High-Level Architecture

{arch_content}

---

## Technology Stack

{tech_content}

---

## Implementation Phases (Summary)

{phase_summary}

---

## Success Criteria

- [ ] All phases complete
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code review approved

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {date_str} | architect | Initial hierarchical specification |
"""

    def _create_phase_file(
        self,
        us_number: str,
        phase_number: int,
        phase_name: str,
        estimated_hours: float,
        description: str,
        total_phases: int,
    ) -> str:
        """Create individual phase file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        phase_title = phase_name.replace("-", " ").title()
        next_phase = phase_number + 1 if phase_number < total_phases else None

        prerequisites = f"- [ ] Phase {phase_number - 1} complete" if phase_number > 1 else "- [ ] None (first phase)"

        next_phase_link = (
            f"\n\n**[Next Phase →](phase{next_phase}-*.md)**"
            if next_phase
            else "\n\n**Final phase - Ready for deployment!**"
        )

        return f"""# SPEC-{us_number.zfill(3)} - Phase {phase_number}: {phase_title}

**Estimated Time**: {estimated_hours} hours
**Dependencies**: Phase {phase_number - 1} complete (or None)
**Created**: {date_str}

---

## Goal

{description or f"TODO: What does Phase {phase_number} accomplish?"}

---

## Prerequisites

{prerequisites}

---

## Detailed Steps

### Step 1: TODO

**What**: Describe the task

**How**:
1. Action 1
2. Action 2

**Code Example**:
```python
# TODO: Add example implementation
```

**Files to Create/Modify**:
- `path/to/file.py` (new file)

---

### Step 2: TODO

**What**: Describe the task

**How**:
1. Action 1
2. Action 2

---

## Acceptance Criteria

- [ ] Specific criterion 1
- [ ] Specific criterion 2
- [ ] Specific criterion 3

---

## Testing This Phase

```bash
# TODO: Add test commands
pytest tests/test_phase_{phase_number}.py -v
```

---

## References

- [GUIDELINE-XXX](../../guidelines/GUIDELINE-XXX.md)
- [ADR-XXX](../../decisions/ADR-XXX.md)
{next_phase_link}
"""

    def _slugify(self, text: str) -> str:
        """Convert text to kebab-case slug."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"-+", "-", text)
        text = text.strip("-")
        return text

    # ==================== UPDATING SPECIFICATIONS ====================

    def update_spec(self, spec_path: Path, changes: Dict[str, Any]) -> str:
        """Update existing specification.

        Args:
            spec_path: Path to existing spec
            changes: Dict with:
                - "version": New version (optional, will auto-bump if not provided)
                - "sections_to_update": Dict of section name -> new content
                - "changelog": Description of changes

        Returns:
            str: Updated spec content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        # Extract current version
        current_version = self.extract_version(content)

        # Determine new version
        new_version = changes.get("version")
        if not new_version:
            # Auto-bump minor version
            new_version = self.bump_version(current_version, "minor")

        # Update version in header
        content = re.sub(r"\*\*Version\*\*: .+", f"**Version**: {new_version}", content)

        # Update sections
        sections_to_update = changes.get("sections_to_update", {})
        for section_name, new_content in sections_to_update.items():
            content = self._update_section(content, section_name, new_content)

        # Add to version history
        changelog = changes.get("changelog", "Updated specification")
        date_str = datetime.now().strftime("%Y-%m-%d")
        content = self._add_version_history(content, new_version, date_str, changelog)

        return content

    def extract_version(self, content: str) -> str:
        """Extract version from spec content.

        Args:
            content: Spec file content

        Returns:
            str: Version (e.g., "1.2.3") or "1.0.0" if not found
        """
        match = re.search(r"\*\*Version\*\*: (\d+\.\d+\.\d+)", content)
        return match.group(1) if match else "1.0.0"

    def bump_version(self, version: str, bump_type: str = "minor") -> str:
        """Bump version number.

        Args:
            version: Current version (e.g., "1.2.3")
            bump_type: "major", "minor", or "patch"

        Returns:
            str: New version
        """
        parts = version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"

    def _update_section(self, content: str, section_name: str, new_content: str) -> str:
        """Update a section in the spec.

        Args:
            content: Full spec content
            section_name: Section header (e.g., "Architecture")
            new_content: New section content

        Returns:
            str: Updated content
        """
        # Find section header
        pattern = rf"(## {re.escape(section_name)}\s*\n)(.*?)(?=\n##|\Z)"

        def replace_section(match):
            header = match.group(1)
            return f"{header}\n{new_content}\n"

        updated = re.sub(pattern, replace_section, content, flags=re.DOTALL)
        return updated

    def _add_version_history(self, content: str, version: str, date: str, changelog: str) -> str:
        """Add entry to version history table.

        Args:
            content: Full spec content
            version: New version
            date: Date string
            changelog: Description of changes

        Returns:
            str: Updated content
        """
        # Find version history table
        pattern = r"(## Version History\s*\n.*?\n)(.*?)(\n---|\Z)"

        def add_entry(match):
            header = match.group(1)
            table = match.group(2)
            footer = match.group(3)

            # Add new entry after header row
            lines = table.split("\n")
            if len(lines) >= 2:
                # Insert after header separator
                new_entry = f"| {version} | {date} | architect | {changelog} |"
                lines.insert(2, new_entry)
                table = "\n".join(lines)

            return f"{header}{table}{footer}"

        updated = re.sub(pattern, add_entry, content, flags=re.DOTALL)
        return updated

    # ==================== CLEANING SPECIFICATIONS ====================

    def clean_spec(self, spec_path: Path, rules: Dict[str, Any]) -> str:
        """Clean specification by removing outdated content.

        Args:
            spec_path: Path to spec
            rules: Dict with:
                - "remove_completed_checklists": bool (default: True)
                - "archive_old_versions": bool (default: True)
                - "consolidate_redundant": bool (default: False)
                - "max_version_history": int (default: 5)

        Returns:
            str: Cleaned spec content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        # Remove completed checklists
        if rules.get("remove_completed_checklists", True):
            content = self._remove_completed_checklists(content)

        # Limit version history
        max_versions = rules.get("max_version_history", 5)
        content = self._limit_version_history(content, max_versions)

        return content

    def _remove_completed_checklists(self, content: str) -> str:
        """Remove completed checklist items.

        Args:
            content: Spec content

        Returns:
            str: Content with completed items removed
        """
        # Remove lines with [x] or [X]
        lines = content.split("\n")
        cleaned_lines = [line for line in lines if not re.match(r"^\s*-\s*\[[xX]\]", line)]
        return "\n".join(cleaned_lines)

    def _limit_version_history(self, content: str, max_entries: int) -> str:
        """Limit version history table to N entries.

        Args:
            content: Spec content
            max_entries: Maximum number of entries to keep

        Returns:
            str: Content with limited version history
        """
        pattern = r"(## Version History\s*\n.*?\n)(.*?)(\n---|\Z)"

        def limit_table(match):
            header = match.group(1)
            table = match.group(2)
            footer = match.group(3)

            lines = table.split("\n")
            if len(lines) > max_entries + 2:  # +2 for header and separator
                # Keep header, separator, and top N entries
                lines = lines[:2] + lines[2 : 2 + max_entries]
                table = "\n".join(lines)

            return f"{header}{table}{footer}"

        updated = re.sub(pattern, limit_table, content, flags=re.DOTALL)
        return updated

    # ==================== SUMMARIZING SPECIFICATIONS ====================

    def summarize_spec(self, spec_path: Path, summary_type: str = "executive", max_length: int = 500) -> str:
        """Summarize specification.

        Args:
            spec_path: Path to spec
            summary_type: "tldr", "executive", or "quick_reference"
            max_length: Maximum words (approximate)

        Returns:
            str: Summary content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        if summary_type == "tldr":
            return self._extract_tldr(content)
        elif summary_type == "executive":
            return self._extract_executive_summary(content)
        else:  # quick_reference
            return self._generate_quick_reference(content)

    # ==================== HIERARCHICAL SPEC SUPPORT ====================

    def read_hierarchical(self, priority_id: str, phase: Optional[int] = None) -> Dict[str, Any]:
        """Read hierarchical spec with progressive disclosure.

        Detects current phase and loads only README + current phase document.
        Falls back to monolithic spec if hierarchical not found.

        Args:
            priority_id: Priority identifier (e.g., "PRIORITY 25", "US-104")
            phase: Specific phase to load (None = auto-detect)

        Returns:
            Dict with keys:
                - success: bool
                - spec_type: "hierarchical" | "monolithic" | "not_found"
                - current_phase: int (for hierarchical)
                - total_phases: int (for hierarchical)
                - full_context: str (README + current phase for hierarchical, full content for monolithic)
                - context_size: int (character count)
                - references: list (guideline references if present)
                - reason: str (error message if success=False)
        """
        # Try to find spec (hierarchical directory or monolithic file)
        spec_path = self._find_spec_by_priority_id(priority_id)

        if not spec_path:
            return {
                "success": False,
                "spec_type": "not_found",
                "reason": f"No spec found for {priority_id}",
                "full_context": "",
                "context_size": 0,
            }

        # Check if hierarchical (directory) or monolithic (file)
        if spec_path.is_dir():
            return self._read_hierarchical_spec(spec_path, phase)
        elif spec_path.is_file():
            # Monolithic spec
            content = spec_path.read_text(encoding="utf-8")
            return {
                "success": True,
                "spec_type": "monolithic",
                "full_context": content,
                "context_size": len(content),
                "references": [],
            }
        else:
            return {
                "success": False,
                "spec_type": "not_found",
                "reason": f"Spec exists but is neither file nor directory: {spec_path}",
                "full_context": "",
                "context_size": 0,
            }

    def _find_spec_by_priority_id(self, priority_id: str) -> Optional[Path]:
        """Find spec by priority ID (e.g., "PRIORITY 25", "US-104").

        This method queries the database first, then falls back to file system search.

        Args:
            priority_id: Priority identifier

        Returns:
            Path to spec (directory for hierarchical, file for monolithic) or None
        """
        # Try database first
        try:
            from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

            db = RoadmapDatabase(agent_name="code_developer")
            spec_data = db.get_technical_spec(roadmap_item_id=priority_id)

            if spec_data and spec_data.get("file_path"):
                file_path = Path(spec_data["file_path"])
                if file_path.exists():
                    logger.debug(f"Found spec in database: {file_path}")
                    return file_path
                else:
                    logger.warning(f"Database has spec entry but file not found: {file_path}")
        except Exception as e:
            logger.debug(f"Database query failed (falling back to file system): {e}")

        # Fallback: file system search
        spec_dir = Path("docs/architecture/specs")
        if not spec_dir.exists():
            return None

        # Extract number from various formats
        match = re.search(r"(\d+)", priority_id)
        if not match:
            return None

        priority_num = match.group(1)

        # Try patterns (hierarchical first, then monolithic)
        patterns = [
            f"SPEC-{priority_num}-*",
            f"SPEC-{priority_num.zfill(3)}-*",
        ]

        for pattern in patterns:
            # Check for hierarchical (directory)
            matches = [p for p in spec_dir.glob(pattern) if p.is_dir()]
            if matches:
                return matches[0]

            # Check for monolithic (file)
            matches = [p for p in spec_dir.glob(f"{pattern}.md") if p.is_file()]
            if matches:
                return matches[0]

        return None

    def _read_hierarchical_spec(self, spec_dir: Path, phase: Optional[int] = None) -> Dict[str, Any]:
        """Read hierarchical spec directory.

        Args:
            spec_dir: Path to spec directory (SPEC-XXX-slug/)
            phase: Specific phase to load (None = auto-detect)

        Returns:
            Dict with hierarchical spec data
        """
        # Check if README.md exists
        readme_path = spec_dir / "README.md"
        if not readme_path.exists():
            return {
                "success": False,
                "spec_type": "hierarchical",
                "reason": f"README.md not found in {spec_dir}",
                "full_context": "",
                "context_size": 0,
            }

        readme_content = readme_path.read_text(encoding="utf-8")

        # Detect current phase if not specified
        if phase is None:
            phase = self._detect_current_phase(spec_dir)

        # Count total phases
        total_phases = self._count_phases(spec_dir)

        # Load current phase document
        spec_dir / f"phase{phase}-*.md"
        phase_matches = list(spec_dir.glob(f"phase{phase}-*.md"))

        if not phase_matches:
            # Phase file missing, return README only
            logger.warning(f"Phase {phase} file not found in {spec_dir}")
            return {
                "success": True,
                "spec_type": "hierarchical",
                "current_phase": phase,
                "total_phases": total_phases,
                "full_context": readme_content,
                "context_size": len(readme_content),
                "references": self._extract_references(readme_content),
                "missing_phase_file": True,
            }

        # Read phase file
        phase_path = phase_matches[0]
        phase_content = phase_path.read_text(encoding="utf-8")

        # Combine README + phase content
        combined_content = f"{readme_content}\n\n---\n\n{phase_content}"

        return {
            "success": True,
            "spec_type": "hierarchical",
            "current_phase": phase,
            "total_phases": total_phases,
            "full_context": combined_content,
            "context_size": len(combined_content),
            "phase_file": str(phase_path),
            "references": self._extract_references(combined_content),
            "next_phase": (
                {
                    "phase_number": phase + 1,
                    "available": phase < total_phases,
                }
                if phase < total_phases
                else None
            ),
        }

    def _detect_current_phase(self, spec_dir: Path) -> int:
        """Detect which phase to work on next using multiple strategies.

        Strategies (in order of preference):
        1. ROADMAP phase tracking (checkboxes)
        2. Git commit history
        3. File existence
        4. Default to Phase 1

        Args:
            spec_dir: Path to spec directory

        Returns:
            int: Phase number to work on (1, 2, 3, ...)
        """
        # Extract priority name from spec directory (e.g., SPEC-025-hierarchical-spec)
        spec_name = spec_dir.name
        priority_match = re.search(r"SPEC-(\d+)", spec_name)
        priority_num = priority_match.group(1) if priority_match else None

        # Strategy 1: Check ROADMAP for phase completion
        try:
            roadmap_path = Path("docs/roadmap/ROADMAP.md")
            if roadmap_path.exists():
                roadmap_content = roadmap_path.read_text(encoding="utf-8")

                # Look for PRIORITY XXX section
                if priority_num:
                    priority_pattern = f"PRIORITY {priority_num}:|US-{priority_num} "
                    if re.search(priority_pattern, roadmap_content):
                        # Find completed phases
                        # Look for pattern like "- [x] Phase N complete"
                        completed_phases = re.findall(r"- \[x\] Phase (\d+)", roadmap_content)
                        if completed_phases:
                            max_completed = max(int(p) for p in completed_phases)
                            next_phase = max_completed + 1
                            logger.info(
                                f"Phase detection (ROADMAP): Completed up to Phase {max_completed}, "
                                f"next = Phase {next_phase}"
                            )
                            return next_phase
        except Exception as e:
            logger.debug(f"Failed to detect phase from ROADMAP: {e}")

        # Strategy 2: Check git commit history
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "-30"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent.parent),
            )

            if result.returncode == 0:
                commits = result.stdout
                # Look for "Phase N" mentions
                phase_nums = re.findall(r"Phase (\d+)", commits)
                if phase_nums:
                    max_phase = max(int(p) for p in phase_nums)
                    next_phase = max_phase + 1
                    logger.info(
                        f"Phase detection (git): Found Phase {max_phase} in commits, " f"next = Phase {next_phase}"
                    )
                    return next_phase
        except Exception as e:
            logger.debug(f"Failed to detect phase from git: {e}")

        # Strategy 3: Check file existence
        try:
            phase_files = sorted(spec_dir.glob("phase*.md"))
            if phase_files:
                # All phases exist, check for deliverables
                # This is a placeholder - could be enhanced
                logger.debug(f"Phase detection (files): Found {len(phase_files)} phase files")
        except Exception as e:
            logger.debug(f"Failed to detect phase from files: {e}")

        # Strategy 4: Default to Phase 1
        logger.info("Phase detection: Defaulting to Phase 1 (no detection strategy succeeded)")
        return 1

    def _count_phases(self, spec_dir: Path) -> int:
        """Count total phases in hierarchical spec.

        Args:
            spec_dir: Path to spec directory

        Returns:
            int: Number of phase files found
        """
        phase_files = list(spec_dir.glob("phase*.md"))
        return len(phase_files)

    def _extract_references(self, content: str) -> list:
        """Extract guideline references from spec content.

        Args:
            content: Spec content

        Returns:
            list: List of guideline references found
        """
        # Look for patterns like "[GUIDELINE-007](..)"
        matches = re.findall(r"\[GUIDELINE-(\d+)[^\]]*\]", content)
        return [f"GUIDELINE-{m}" for m in matches]

    def _extract_tldr(self, content: str) -> str:
        """Extract TL;DR from spec."""
        # Try to find existing TL;DR
        match = re.search(r"\*\*TL;DR\*\*:?\s*(.+?)(?:\n|$)", content)
        if match:
            return match.group(1).strip()

        # Fallback: Extract from executive summary
        match = re.search(r"## Executive Summary\s*\n\s*(.+?)(?:\n\n|\n##)", content, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # Take first sentence
            first_sentence = summary.split(".")[0]
            return first_sentence + "."

        return "No summary available"

    def _extract_executive_summary(self, content: str) -> str:
        """Extract executive summary from spec."""
        match = re.search(r"## Executive Summary\s*\n(.*?)(?:\n##|\Z)", content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return "No executive summary available"

    def _generate_quick_reference(self, content: str) -> str:
        """Generate quick reference from spec."""
        ref = []

        # Extract key sections
        sections = {
            "Problem": r"## Problem Statement\s*\n(.*?)(?:\n##|\Z)",
            "Architecture": r"## Architecture\s*\n(.*?)(?:\n##|\Z)",
            "DoD": r"## Acceptance Criteria.*?\s*\n(.*?)(?:\n##|\Z)",
        }

        for name, pattern in sections.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_content = match.group(1).strip()
                # Take first 2-3 lines
                lines = section_content.split("\n")[:3]
                ref.append(f"**{name}**: {' '.join(lines)}")

        return "\n\n".join(ref) if ref else "No quick reference available"
