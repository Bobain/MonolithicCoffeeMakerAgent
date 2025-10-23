#!/usr/bin/env python3
"""Debug timestamp generation."""

from datetime import datetime, timedelta

# What the test generates
stale_time = (datetime.now() - timedelta(hours=25)).isoformat()
recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
now = datetime.now().isoformat()

print("Test timestamp generation:")
print(f"  Now:        {now}")
print(f"  25h ago:    {stale_time}")
print(f"  1h ago:     {recent_time}")

# Check if 25h ago is actually before 24h threshold
import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT
        ? as stale_time,
        datetime(?) as parsed_stale,
        datetime('now', '-24 hours') as threshold,
        CASE WHEN datetime(?) < datetime('now', '-24 hours')
             THEN 'YES' ELSE 'NO' END as is_stale
""",
    (stale_time, stale_time, stale_time),
)

result = cursor.fetchone()
print("\nSQLite evaluation:")
print(f"  Stale time:  {result[0]}")
print(f"  Parsed:      {result[1]}")
print(f"  Threshold:   {result[2]}")
print(f"  Is stale?    {result[3]}")

conn.close()
