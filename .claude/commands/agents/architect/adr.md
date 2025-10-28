# adr

## Purpose
Record architectural decision: document context, decision, consequences, alternatives considered, create ADR document.

## Parameters
```yaml
title: str  # Required, decision title
context: str  # Required, problem description
decision: str  # Required, chosen solution
alternatives: List[str]  # Required, options considered
consequences: dict = None  # {positive: [...], negative: [...]}
relates_to: List[str] = []  # Related ADR/SPEC/POC IDs
```

## Workflow
1. Generate next ADR number
2. Create ADR document in docs/architecture/adrs/
3. Record decision in database
4. Link to related specs/POCs if specified
5. Notify relevant agents
6. Return AdrResult

## Database Operations
```sql
-- Get next ADR number
SELECT MAX(CAST(SUBSTR(adr_id, 5) AS INTEGER)) + 1
FROM architectural_decision

-- Insert ADR
INSERT INTO architectural_decision (
    adr_id, title, context, decision, alternatives,
    consequences, status, created_at, relates_to
) VALUES (?, ?, ?, ?, ?, ?, 'accepted', datetime('now'), ?)

-- Link to spec/POC
UPDATE technical_spec
SET related_adrs = json_insert(related_adrs, '$[#]', ?)
WHERE spec_id IN (?)
```

## ADR Document Structure
```markdown
# ADR-{number}: {title}

**Status**: Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Relates to**: SPEC-042, POC-015

## Context
[Problem description]

## Decision
[Chosen solution]

## Alternatives Considered
1. Option A - [Reason rejected]
2. Option B - [Reason rejected]

## Consequences
**Positive**: [Benefits]
**Negative**: [Trade-offs]

## Implementation Notes
[Technical details]
```

## Result Object
```python
@dataclass
class AdrResult:
    adr_id: str  # Format: ADR-NNN
    file_path: str
    related_items: List[str]  # Linked specs/POCs
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| InvalidFormat | Missing required fields | Check all parameters provided |
| FileWriteError | Can't create ADR file | Check directory permissions |
| DatabaseError | Insert failed | Retry with backoff |
| LinkingFailed | Related item not found | Verify IDs exist |

## Example
```python
result = adr(
    title="Use PostgreSQL for Multi-Tenancy",
    context="Need scalable database for tenant isolation",
    decision="Implement row-level security with PostgreSQL",
    alternatives=["Separate databases per tenant", "MongoDB with collections"],
    relates_to=["SPEC-042"]
)
# AdrResult(
#   adr_id="ADR-023",
#   file_path="docs/architecture/adrs/ADR-023-postgresql-multitenancy.md",
#   related_items=["SPEC-042"],
#   status="success"
# )
```

## Related Commands
- design() - Specs may trigger ADRs
- poc() - POC evaluations often lead to ADRs

---
Estimated: 65 lines | Context: ~4% | Examples: adr_examples.md
