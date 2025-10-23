#!/usr/bin/env python3
"""Debug script to check the stale specs query."""

import sqlite3
from pathlib import Path

db_path = Path("data/unified_roadmap_specs.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what specs exist
cursor.execute(
    """
    SELECT id, status, started_at,
           datetime(started_at) as parsed_start,
           datetime('now') as now_time,
           datetime('now', '-24 hours') as threshold,
           CASE WHEN datetime(started_at) < datetime('now', '-24 hours')
                THEN 'STALE' ELSE 'OK' END as is_stale
    FROM technical_specs
    WHERE spec_number IN (9999, 9998)
    ORDER BY spec_number
"""
)

print("Debug query results:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}")
    print(f"    Status: {row[1]}")
    print(f"    Started at: {row[2]}")
    print(f"    Parsed: {row[3]}")
    print(f"    Now: {row[4]}")
    print(f"    Threshold: {row[5]}")
    print(f"    Is stale: {row[6]}")
    print()

# Now test the exact query used in reset_stale_specs
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
print(f"Found {len(stale)} stale specs using the actual query")
for s in stale:
    print(f"  {s}")

conn.close()
