#!/usr/bin/env python3
"""
Migrate technical specifications from files to database.

CRITICAL: Specs MUST be stored in database, NOT files!
This script migrates SPEC-100 through SPEC-104 from markdown files
into the specs_specification table.
"""

import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def extract_title(content: str) -> str:
    """Extract title from markdown content."""
    match = re.search(r"^#\s+SPEC-\d+:\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown Title"


def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata from spec frontmatter."""
    metadata = {
        "status": "draft",
        "created": datetime.now().isoformat(),
        "author": "architect",
        "parent_spec": None,
        "dependencies": [],
        "cfrs": [],
    }

    # Extract status
    status_match = re.search(r"\*\*Status\*\*:\s+(\w+)", content)
    if status_match:
        metadata["status"] = status_match.group(1).lower()

    # Extract created date
    created_match = re.search(r"\*\*Created\*\*:\s+([\d-]+)", content)
    if created_match:
        metadata["created"] = created_match.group(1)

    # Extract author
    author_match = re.search(r"\*\*Author\*\*:\s+(\w+)", content)
    if author_match:
        metadata["author"] = author_match.group(1)

    # Extract parent spec
    parent_match = re.search(r"\*\*Parent Spec\*\*:\s+(SPEC-\d+)", content)
    if parent_match:
        metadata["parent_spec"] = parent_match.group(1)

    # Extract dependencies
    deps_match = re.search(r"\*\*Dependencies\*\*:\s+(.+)", content)
    if deps_match:
        deps_text = deps_match.group(1)
        metadata["dependencies"] = re.findall(r"SPEC-\d+", deps_text)

    # Extract CFRs
    cfrs_match = re.findall(r"CFR-\d+", content)
    if cfrs_match:
        metadata["cfrs"] = list(set(cfrs_match))

    return metadata


def estimate_hours(content: str, spec_number: int) -> float:
    """Extract or estimate hours for spec."""
    # Try to extract from content
    effort_match = re.search(r"\*\*Total\*\*[^\d]*(\d+)", content)
    if effort_match:
        return float(effort_match.group(1))

    # Fallback estimates by spec number
    estimates = {
        100: 0,  # Master spec (no implementation)
        101: 20,  # Foundation
        102: 32,  # Project Manager
        103: 30,  # Architect
        104: 28,  # Code Developer
    }
    return estimates.get(spec_number, 0)


def migrate_spec_to_database(spec_file: Path, db_path: Path):
    """Migrate a single spec file to database."""

    # Read file content
    content = spec_file.read_text()

    # Extract spec number from filename
    match = re.match(r"SPEC-(\d+)", spec_file.stem)
    if not match:
        print(f"⚠️  Skipping {spec_file} - invalid filename format")
        return

    spec_number = int(match.group(1))
    spec_id = f"SPEC-{spec_number}"

    # Extract metadata
    title = extract_title(content)
    metadata = extract_metadata(content)
    estimated_hours = estimate_hours(content, spec_number)

    print(f"\n📝 Migrating {spec_id}: {title}")
    print(f"   Status: {metadata['status']}")
    print(f"   Estimated Hours: {estimated_hours}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if spec already exists
    cursor.execute("SELECT id FROM specs_specification WHERE id = ?", (spec_id,))
    existing = cursor.fetchone()

    if existing:
        print(f"   ⚠️  Spec already exists in database - updating")
        action = "update"
    else:
        print(f"   ✅ New spec - inserting")
        action = "insert"

    # Prepare data (match actual schema)
    spec_data = {
        "id": spec_id,
        "spec_number": spec_number,
        "title": title,
        "status": metadata["status"],
        "spec_type": "monolithic",  # All current specs are monolithic
        "content": content,  # FULL content in database!
        "estimated_hours": estimated_hours,
        "dependencies": json.dumps(metadata.get("dependencies", [])),
        "updated_by": "architect",
        "updated_at": datetime.now().isoformat(),
    }

    if action == "insert":
        # Insert new spec
        cursor.execute(
            """
            INSERT INTO specs_specification (
                id, spec_number, title, status, spec_type, content,
                estimated_hours, dependencies, updated_by, updated_at
            ) VALUES (
                :id, :spec_number, :title, :status, :spec_type, :content,
                :estimated_hours, :dependencies, :updated_by, :updated_at
            )
        """,
            spec_data,
        )
    else:
        # Update existing spec
        cursor.execute(
            """
            UPDATE specs_specification
            SET title = :title,
                status = :status,
                content = :content,
                estimated_hours = :estimated_hours,
                dependencies = :dependencies,
                updated_by = :updated_by,
                updated_at = :updated_at
            WHERE id = :id
        """,
            spec_data,
        )

    conn.commit()

    # Verify migration
    cursor.execute(
        """
        SELECT id, spec_number, title, LENGTH(content) as content_length,
               estimated_hours, status
        FROM specs_specification
        WHERE id = ?
    """,
        (spec_id,),
    )

    result = cursor.fetchone()
    if result:
        print(f"   ✅ Verified in database:")
        print(f"      - Content length: {result[3]} bytes")
        print(f"      - Estimated hours: {result[4]}")
        print(f"      - Status: {result[5]}")

    conn.close()


def main():
    """Migrate all specs from files to database."""

    print("=" * 80)
    print("SPEC MIGRATION: Files → Database")
    print("=" * 80)

    # Paths
    specs_dir = Path("docs/architecture/specs")
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    # Find all spec files
    spec_files = sorted(specs_dir.glob("SPEC-1*.md"))

    if not spec_files:
        print(f"❌ No spec files found in {specs_dir}")
        return

    print(f"\nFound {len(spec_files)} spec files to migrate:")
    for spec_file in spec_files:
        print(f"  - {spec_file.name}")

    # Migrate each spec
    for spec_file in spec_files:
        try:
            migrate_spec_to_database(spec_file, db_path)
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback

            traceback.print_exc()

    # Verification report
    print("\n" + "=" * 80)
    print("VERIFICATION REPORT")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, spec_number, title, LENGTH(content), estimated_hours, status
        FROM specs_specification
        WHERE spec_number BETWEEN 100 AND 104
        ORDER BY spec_number
    """
    )

    results = cursor.fetchall()

    if results:
        print(f"\n✅ Successfully migrated {len(results)} specs to database:\n")
        print(f"{'Spec ID':<12} {'Title':<50} {'Content':<12} {'Hours':<8} {'Status':<10}")
        print("-" * 100)

        for row in results:
            spec_id, spec_num, title, content_len, hours, status = row
            # Truncate title if too long
            if len(title) > 47:
                title = title[:44] + "..."
            print(f"{spec_id:<12} {title:<50} {content_len:>10}B {hours:>6}h {status:<10}")

        total_hours = sum(row[4] for row in results)
        total_bytes = sum(row[3] for row in results)

        print("-" * 100)
        print(f"{'TOTAL':<12} {'':<50} {total_bytes:>10}B {total_hours:>6}h")
    else:
        print("\n❌ No specs found in database!")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Verify database contents above")
    print("2. code_developer: Read specs FROM database (query specs_specification table)")
    print("3. architect: Write specs TO database (DomainWrapper.write())")
    print("4. Files in docs/architecture/specs/ are BACKUP ONLY - DO NOT modify directly!")
    print("\nDATABASE-FIRST ARCHITECTURE RESTORED ✅")


if __name__ == "__main__":
    main()
