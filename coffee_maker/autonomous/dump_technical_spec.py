#!/usr/bin/env python3
"""Dump technical specifications from database to markdown files for human review.

Usage:
    python dump_technical_spec.py SPEC-131
    python dump_technical_spec.py --all
    python dump_technical_spec.py --recent 5
"""

import argparse
import json
import sqlite3
from pathlib import Path

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase


def dump_spec_to_markdown(spec_id: str, output_dir: Path) -> None:
    """Dump a technical spec to markdown file.

    Args:
        spec_id: Spec ID (e.g., "SPEC-131")
        output_dir: Directory to write markdown file
    """
    db = RoadmapDatabase(agent_name="dump_tool")
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM specs_specification
        WHERE id = ?
    """,
        (spec_id,),
    )
    spec = cursor.fetchone()
    conn.close()

    if not spec:
        print(f"❌ Spec {spec_id} not found in database")
        return

    spec = dict(spec)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate markdown filename
    filename = f"{spec_id}-{spec['title'].replace(' ', '-').replace('/', '-')[:50]}.md"
    output_path = output_dir / filename

    # Build markdown content
    markdown_lines = []

    # Header
    markdown_lines.append(f"# {spec_id}: {spec['title']}")
    markdown_lines.append("")
    markdown_lines.append(f"**Status**: {spec['status']}")
    markdown_lines.append(f"**Type**: {spec['spec_type']}")
    if spec["roadmap_item_id"]:
        markdown_lines.append(f"**Roadmap Item**: {spec['roadmap_item_id']}")
    if spec["estimated_hours"]:
        markdown_lines.append(f"**Estimated Hours**: {spec['estimated_hours']}")
    markdown_lines.append(f"**Updated**: {spec['updated_at']} by {spec['updated_by']}")
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")

    # Content
    if spec["spec_type"] == "hierarchical":
        # Parse hierarchical spec JSON
        try:
            content_json = json.loads(spec["content"])

            # Define standard section order
            standard_sections = [
                "/overview",
                "/architecture",
                "/api_design",
                "/data_model",
                "/implementation",
                "/test_strategy",
                "/dependencies",
                "/success_criteria",
            ]

            # Write sections in standard order
            for section_key in standard_sections:
                if section_key in content_json:
                    markdown_lines.append(f"## {section_key}")
                    markdown_lines.append("")
                    markdown_lines.append(content_json[section_key].strip())
                    markdown_lines.append("")

            # Write any remaining sections not in standard order
            for section_key, section_content in content_json.items():
                if f"/{section_key}" not in standard_sections:
                    markdown_lines.append(f"## /{section_key}")
                    markdown_lines.append("")
                    markdown_lines.append(section_content.strip())
                    markdown_lines.append("")

        except json.JSONDecodeError:
            # Fallback: treat as plain markdown
            markdown_lines.append(spec["content"])
    else:
        # Non-hierarchical spec
        markdown_lines.append(spec["content"])

    # Write to file
    with open(output_path, "w") as f:
        f.write("\n".join(markdown_lines))

    print(f"✅ Dumped {spec_id} to {output_path}")


def dump_all_specs(output_dir: Path) -> None:
    """Dump all technical specs to markdown files."""
    db = RoadmapDatabase(agent_name="dump_tool")
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM specs_specification ORDER BY spec_number")
    spec_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"📋 Dumping {len(spec_ids)} technical specs...")
    for spec_id in spec_ids:
        dump_spec_to_markdown(spec_id, output_dir)

    print(f"\n✅ Dumped {len(spec_ids)} specs to {output_dir}")


def dump_recent_specs(count: int, output_dir: Path) -> None:
    """Dump N most recent technical specs."""
    db = RoadmapDatabase(agent_name="dump_tool")
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM specs_specification
        ORDER BY updated_at DESC
        LIMIT ?
    """,
        (count,),
    )
    spec_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"📋 Dumping {len(spec_ids)} most recent technical specs...")
    for spec_id in spec_ids:
        dump_spec_to_markdown(spec_id, output_dir)

    print(f"\n✅ Dumped {len(spec_ids)} recent specs to {output_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dump technical specifications from database to markdown files")
    parser.add_argument(
        "spec_id",
        nargs="?",
        help="Spec ID to dump (e.g., SPEC-131), or omit to use --all/--recent",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Dump all technical specs",
    )
    parser.add_argument(
        "--recent",
        type=int,
        metavar="N",
        help="Dump N most recent technical specs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/architecture/specs/exported"),
        help="Output directory for markdown files (default: docs/architecture/specs/exported)",
    )

    args = parser.parse_args()

    if args.all:
        dump_all_specs(args.output_dir)
    elif args.recent:
        dump_recent_specs(args.recent, args.output_dir)
    elif args.spec_id:
        dump_spec_to_markdown(args.spec_id, args.output_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
