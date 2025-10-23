#!/usr/bin/env python3
"""Test the stale spec query directly."""

import sqlite3
from datetime import datetime
from pathlib import Path

db_path = Path("data/unified_roadmap_specs.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert test data with very old timestamp
very_old = "2025-10-01T10:00:00"  # Definitely >24 hours ago
cursor.execute(
    """
    INSERT OR REPLACE INTO technical_specs (
        id, spec_number, title, status, started_at,
        updated_at, updated_by, spec_type, content
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
    (
        "SPEC-TEST",
        99999,
        "Test spec",
        "in_progress",
        very_old,
        datetime.now().isoformat(),
        "test",
        "monolithic",
        "test",
    ),
)
conn.commit()

# Try the query
print("Testing query with very old timestamp:", very_old)
cursor.execute(
    """
    SELECT id, status, started_at,
           datetime(started_at) as parsed,
           datetime('now', '-24 hours') as threshold
    FROM technical_specs
    WHERE id = 'SPEC-TEST'
"""
)
result = cursor.fetchone()
print(f"  ID: {result[0]}")
print(f"  Status: {result[1]}")
print(f"  Started: {result[2]}")
print(f"  Parsed: {result[3]}")
print(f"  Threshold: {result[4]}")

# Now test the actual stale query
cursor.execute(
    """
    SELECT id, title, started_at
    FROM technical_specs
    WHERE status = 'in_progress'
    AND started_at IS NOT NULL
    AND datetime(started_at) < datetime('now', '-24 hours')
"""
)
stale = cursor.fetchall()
print(f"\nFound {len(stale)} stale specs")
for s in stale:
    print(f"  {s}")

# Clean up
cursor.execute("DELETE FROM technical_specs WHERE id = 'SPEC-TEST'")
conn.commit()
conn.close()
