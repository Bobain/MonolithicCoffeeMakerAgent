#!/usr/bin/env python3
"""Migrate monolithic specifications to hierarchical format.

This script automates the conversion of monolithic spec files to hierarchical format,
reducing context usage and improving modularity.

Usage:
    python scripts/migrate_spec_to_hierarchical.py <spec_file>
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    # Remove special characters except spaces and hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace spaces with hyphens and convert to lowercase
    text = re.sub(r"[-\s]+", "-", text).strip("-").lower()
    return text


def extract_overview(content: str) -> str:
    """Extract overview section from monolithic spec."""
    # Extract everything before Implementation Plan or Migration Plan (where phases are)
    # Try multiple section names where phases might be located
    for section_name in ["Implementation Plan", "Migration Plan", "Phases"]:
        impl_match = re.search(rf"^## {section_name}", content, re.MULTILINE)
        if impl_match:
            return content[: impl_match.start()].strip()

    # If no phase section found, find first "### Phase" marker
    phase_match = re.search(r"^### Phase \d+:", content, re.MULTILINE)
    if phase_match:
        return content[: phase_match.start()].strip()

    return content


def extract_references(content: str) -> List[str]:
    """Extract guideline and reference links from content."""
    references = []
    # Find guideline references
    guideline_pattern = r"\[GUIDELINE-\d+[^\]]*\]\([^\)]+\)"
    references.extend(re.findall(guideline_pattern, content))

    # Find spec references
    spec_pattern = r"\[SPEC-\d+[^\]]*\]\([^\)]+\)"
    references.extend(re.findall(spec_pattern, content))

    return list(set(references))


def parse_monolithic_spec(spec_path: Path) -> Dict:
    """Parse monolithic spec into sections."""
    content = spec_path.read_text()

    # Extract metadata
    us_match = re.search(r"(SPEC|REFACTOR)-(\d+)", spec_path.name)
    prefix = us_match.group(1) if us_match else "SPEC"
    us_number = us_match.group(2) if us_match else "000"

    title_match = re.search(r"^# (?:SPEC|REFACTOR)-\d+: (.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # Extract phases from Implementation Plan
    phases = []
    phase_pattern = r"### Phase (\d+): (.+?) \((.+?)\)"

    phase_matches = list(re.finditer(phase_pattern, content))

    for i, match in enumerate(phase_matches):
        phase_num = int(match.group(1))
        phase_name = match.group(2).strip()
        phase_hours = match.group(3).strip()

        # Extract phase content (between this phase and next)
        phase_start = match.start()

        # Find the next phase or end of document
        if i + 1 < len(phase_matches):
            phase_end = phase_matches[i + 1].start()
        else:
            # Look for next major section or end of file
            next_section = re.search(r"\n## [A-Z]", content[phase_start + 1 :])
            if next_section:
                phase_end = phase_start + next_section.start() + 1
            else:
                phase_end = len(content)

        phase_content = content[phase_start:phase_end].strip()

        phases.append({"number": phase_num, "name": phase_name, "hours": phase_hours, "content": phase_content})

    return {
        "prefix": prefix,
        "us_number": us_number,
        "title": title,
        "overview": extract_overview(content),
        "phases": phases,
        "references": extract_references(content),
    }


def generate_readme(spec_data: Dict) -> str:
    """Generate README.md content for hierarchical spec."""
    prefix = spec_data["prefix"]
    us_number = spec_data["us_number"]
    title = spec_data["title"]

    readme = f"""# {prefix}-{us_number}: {title}

## Overview

{spec_data["overview"]}

---

## Implementation Phases

This specification is organized into phases for progressive disclosure and context efficiency.

"""

    # Add phase links
    for phase in spec_data["phases"]:
        phase_slug = to_kebab_case(phase["name"])
        readme += f"""### Phase {phase["number"]}: {phase["name"]} ({phase["hours"]})
**Document**: [phase{phase["number"]}-{phase_slug}.md](./phase{phase["number"]}-{phase_slug}.md)

"""

    # Add references section if any
    if spec_data["references"]:
        readme += "\n---\n\n## Related Documents\n\n"
        for ref in sorted(set(spec_data["references"])):
            readme += f"- {ref}\n"

    readme += """
---

**Note**: This specification uses hierarchical format for 71% context reduction.
Each phase is in a separate file - read only the phase you're implementing.
"""

    return readme


def generate_phase_doc(phase: Dict, spec_data: Dict) -> str:
    """Generate phase document content."""
    prefix = spec_data["prefix"]
    us_number = spec_data["us_number"]

    # Remove the phase header from content since we're adding our own
    content = phase["content"]
    # Remove "### Phase N: Title (hours)" line if it exists at the start
    content = re.sub(r"^### Phase \d+: .+? \(.+?\)\n+", "", content)

    phase_doc = f"""# {prefix}-{us_number} - Phase {phase["number"]}: {phase["name"]}

**Estimated Time**: {phase["hours"]}
**Status**: Planned

---

{content}

---

## Next Phase

"""

    if phase["number"] < len(spec_data["phases"]):
        next_phase = spec_data["phases"][phase["number"]]  # 0-indexed, so phase 2 is at index 1
        next_slug = to_kebab_case(next_phase["name"])
        phase_doc += f"""**After completing this phase, proceed to**:
- **[Phase {next_phase["number"]}: {next_phase["name"]}](phase{next_phase["number"]}-{next_slug}.md)**
"""
    else:
        phase_doc += "**This is the final phase.**\n"

    return phase_doc


def create_hierarchical_spec(spec_data: Dict, output_dir: Path) -> Path:
    """Create hierarchical spec from parsed data."""
    # Create directory
    slug = to_kebab_case(spec_data["title"])
    spec_dir = output_dir / f"{spec_data['prefix']}-{spec_data['us_number']}-{slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Create README.md
    readme = generate_readme(spec_data)
    (spec_dir / "README.md").write_text(readme)

    # Create phase files
    for phase in spec_data["phases"]:
        phase_slug = to_kebab_case(phase["name"])
        phase_file = spec_dir / f"phase{phase['number']}-{phase_slug}.md"
        phase_content = generate_phase_doc(phase, spec_data)
        phase_file.write_text(phase_content)

    print(f"✅ Created hierarchical spec: {spec_dir}")
    print(f"   Files: README.md + {len(spec_data['phases'])} phase files")

    return spec_dir


def migrate_spec(spec_path: Path, output_dir: Path = None) -> None:
    """Main migration function."""
    if not spec_path.exists():
        print(f"❌ Error: Spec file not found: {spec_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = spec_path.parent

    print(f"🔄 Migrating: {spec_path.name}")

    # Parse spec
    spec_data = parse_monolithic_spec(spec_path)

    if not spec_data["phases"]:
        print(f"⚠️  Warning: No phases found in spec. Skipping migration.")
        print(f"   Ensure spec has '### Phase N: Title (hours)' markers.")
        sys.exit(1)

    print(f"   Found {len(spec_data['phases'])} phases")

    # Create hierarchical structure
    spec_dir = create_hierarchical_spec(spec_data, output_dir)

    # Archive original
    archive_path = spec_path.with_suffix(".md.ARCHIVE")
    spec_path.rename(archive_path)
    print(f"📦 Archived original: {archive_path.name}")

    print(f"\n✅ Migration complete!")
    print(f"   Directory: {spec_dir.name}/")
    print(f"   Files: {len(list(spec_dir.glob('*.md')))} markdown files")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_spec_to_hierarchical.py <spec_file>")
        print("\nExample:")
        print("  python scripts/migrate_spec_to_hierarchical.py \\")
        print("    docs/architecture/specs/SPEC-108-parallel-agent-execution.md")
        sys.exit(1)

    spec_file = Path(sys.argv[1])
    migrate_spec(spec_file)


if __name__ == "__main__":
    main()
