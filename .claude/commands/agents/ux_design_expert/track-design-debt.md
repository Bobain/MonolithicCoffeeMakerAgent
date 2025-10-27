---
command: track-design-debt
agent: ux_design_expert
action: manage_design_debt
tables: [ui_design_debt]
tools: []
duration: 10m
---

## Purpose

Monitor UI/UX technical debt with severity assessment and remediation planning.

## Input Parameters

```yaml
ACTION:
  type: string
  enum: [add, update, resolve, list]
  description: Debt management action

DESCRIPTION:
  type: string
  optional: true
  description: Design debt description (required for add)

SEVERITY:
  type: string
  optional: true
  enum: [critical, high, medium, low]
  description: Debt severity level

COMPONENT_ID:
  type: string
  optional: true
  description: Associated component identifier

DEBT_ID:
  type: string
  optional: true
  description: Debt identifier (for update/resolve)

REMEDIATION_PLAN:
  type: string
  optional: true
  description: Plan to fix the debt
```

## Database Operations

### INSERT ui_design_debt (for ADD)

```sql
INSERT INTO ui_design_debt (
    debt_id, description, severity, component_id,
    created_by, created_at, status
) VALUES (?, ?, ?, ?, 'ux_design_expert', datetime('now'), 'open')
```

### UPDATE ui_design_debt (for UPDATE/RESOLVE)

```sql
UPDATE ui_design_debt
SET status = ?, remediation_plan = ?, resolved_at = datetime('now')
WHERE debt_id = ?
```

### SELECT ui_design_debt (for LIST)

```sql
SELECT * FROM ui_design_debt WHERE status = ? ORDER BY severity DESC
```

## Success Criteria

- Debt tracked in database
- Severity assessed
- Remediation plan created (if provided)
- Status updated appropriately
- Audit trail created

## Output Format

```json
{
  "success": true,
  "action": "add",
  "debt_id": "DEBT-DESIGN-042",
  "description": "Dashboard colors don't follow design system",
  "severity": "medium",
  "component_id": "COMP-DASHBOARD",
  "status": "open",
  "created_at": "2025-10-27T10:30:00Z",
  "estimated_effort_hours": 4,
  "message": "Design debt tracked successfully"
}
```

## Severity Guide

| Severity | Criteria | Example |
|----------|----------|---------|
| critical | Blocks accessibility or major feature | Missing ARIA labels, broken layout |
| high | Significant UX degradation | Inconsistent spacing, confusing navigation |
| medium | Noticeable quality issue | Color mismatch, missing hover states |
| low | Minor polish needed | Icon alignment, subtle color differences |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Debt not found | Invalid DEBT_ID | List recent debt items |
| Invalid severity | SEVERITY not in enum | List valid severities |
| Insert failed | Database error | Retry up to 3 times |

## Examples

### Example 1: Add Design Debt

```bash
/agents:ux_design_expert:track-design-debt \
  ACTION="add" \
  DESCRIPTION="Dashboard uses hardcoded colors instead of design tokens" \
  SEVERITY="medium" \
  COMPONENT_ID="COMP-DASHBOARD"
```

### Example 2: Resolve Design Debt

```bash
/agents:ux_design_expert:track-design-debt \
  ACTION="resolve" \
  DEBT_ID="DEBT-DESIGN-042" \
  REMEDIATION_PLAN="Updated all colors to use design tokens from ui_design_tokens"
```

### Example 3: List Design Debt

```bash
/agents:ux_design_expert:track-design-debt \
  ACTION="list"
```

## Implementation Notes

- Debt IDs use format: `DEBT-DESIGN-{sequential-number}`
- Assess severity level for each debt item
- Include component link for context
- Provide remediation plan for resolution
- Track resolution date and notes
- Generate design debt reports by severity
- Monitor debt accumulation over time
- Prioritize by severity and effort
