# roadmap

## Purpose
Parse, validate, and sync ROADMAP.md with database: ensure consistency between file and roadmap_priority table.

## Parameters
```yaml
priority_id: str = None  # Specific priority, None = all
updates: dict = None  # Updates to apply {field: value}
validate_only: bool = false  # Just validate, don't sync
```

## Workflow
1. Parse docs/roadmap/ROADMAP.md
2. Extract priorities with status, progress, tasks
3. Validate structure and data integrity
4. Query database for existing priorities
5. Sync: INSERT new, UPDATE changed, flag deleted
6. Apply updates if provided
7. Return RoadmapResult with sync summary

## Database Operations
```sql
-- Load existing priorities
SELECT priority_id, title, status, progress, assigned_agent, metadata
FROM roadmap_priority
ORDER BY created_at DESC

-- Sync priority
INSERT INTO roadmap_priority (priority_id, title, status, progress, assigned_agent, metadata, created_at)
VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
ON CONFLICT(priority_id) DO UPDATE SET
    status=excluded.status, progress=excluded.progress, updated_at=datetime('now')
```

## Result Object
```python
@dataclass
class RoadmapResult:
    priorities_synced: int
    priorities_added: int
    priorities_updated: int
    priorities_deleted: int
    validation_errors: List[str]
    status: str  # "success" | "partial" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| FileNotFound | ROADMAP.md missing | Check docs/roadmap/ROADMAP.md exists |
| ParseError | Invalid markdown format | Fix ROADMAP.md syntax |
| DatabaseError | DB connection failed | Retry with backoff |
| ValidationError | Priority format invalid | Review priority structure |

## Example
```python
result = roadmap(validate_only=False)
# RoadmapResult(
#   priorities_synced=12,
#   priorities_added=2,
#   priorities_updated=3,
#   priorities_deleted=0,
#   validation_errors=[],
#   status="success"
# )
```

## Related Commands
- track() - Update priority status/progress
- plan() - Create new priorities

---
Estimated: 60 lines | Context: ~4% | Examples: roadmap_examples.md
