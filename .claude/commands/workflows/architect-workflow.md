---
command: architect-workflow
workflow: spec
agent: architect
purpose: Complete architectural design workflow
tables: [roadmap_priority, technical_spec, adr, dependency_matrix, poc]
tools: [file_system, git]
duration: 20-90m
---

## Purpose

Execute complete architectural design workflow: analyze requirements → design solution → check dependencies → create POC (if needed) → write ADR → generate technical spec. This is the PRIMARY workflow command for the architect agent, replacing 5 individual commands with one intelligent workflow.

## Workflow Overview

```
spec(priority_id) → Analyze → Design → Dependencies → POC → ADR → Spec → SpecResult
```

**Key Features**:
- **4 depth levels**: FULL (complete workflow), QUICK (fast design), UPDATE (modify existing), REVIEW (validate only)
- **Auto POC detection**: Automatically determines if POC required based on complexity
- **Dependency checking**: Validates all dependencies before proceeding
- **ADR auto-creation**: Creates Architectural Decision Records for major decisions
- **Rich result tracking**: Comprehensive SpecResult with all artifacts created

## Input Parameters

```yaml
PRIORITY_ID:
  type: string
  required: true
  description: Priority to create spec for
  example: "PRIORITY-5"

DEPTH:
  type: string
  default: "full"
  enum: [full, quick, update, review]
  description: |
    - full: Complete workflow with POC/ADR
    - quick: Fast design without POC/ADR
    - update: Update existing spec
    - review: Review and validate only

POC_REQUIRED:
  type: boolean
  optional: true
  description: Override auto-detection for POC requirement

DEPENDENCIES:
  type: list[string]
  optional: true
  description: Explicit dependencies to check
  example: ["fastapi", "pydantic", "sqlalchemy"]

NOTIFY:
  type: boolean
  default: true
  description: Notify project manager and code developer on completion

VERBOSE:
  type: boolean
  default: false
  description: Enable detailed logging
```

## Workflow Execution

### FULL Depth (Default)

Complete architectural workflow:

```python
1. Analyze priority requirements
2. Check complexity score
3. Auto-detect POC requirement
4. Check all dependencies (3-tier approval)
5. Create POC if required (high complexity)
6. Design solution architecture
7. Create ADR for major decisions
8. Generate technical spec document
9. Link spec to priority in database
10. Notify relevant agents
11. Return comprehensive SpecResult
```

### QUICK Depth

Fast design without POC/ADR:

```python
1. Analyze priority requirements
2. Check dependencies
3. Design solution (simplified)
4. Generate technical spec
5. Link to priority
6. Return SpecResult
```

### UPDATE Depth

Update existing specification:

```python
1. Load existing spec
2. Apply updates
3. Re-check dependencies if changed
4. Update spec document
5. Create ADR for significant changes
6. Return SpecResult
```

### REVIEW Depth

Validate existing specification:

```python
1. Load spec document
2. Validate structure
3. Check dependencies still valid
4. Verify ADRs exist for decisions
5. Check POC status if applicable
6. Return validation SpecResult
```

## Result Object

```python
@dataclass
class SpecResult:
    spec_id: str  # SPEC-XXX
    status: str  # success | partial | failed
    priority_id: str
    steps_completed: List[str]
    steps_failed: List[str]
    dependencies_checked: List[str]
    adr_created: bool
    poc_created: bool
    duration_seconds: float
    error_message: Optional[str]
    metadata: Dict[str, Any]
```

## Success Criteria

### Full Success (status = "success")

- ✅ Requirements analyzed
- ✅ Dependencies checked and approved
- ✅ POC created (if required)
- ✅ ADR created (if major decisions)
- ✅ Technical spec generated
- ✅ Database records created
- ✅ Notifications sent

### Partial Success (status = "partial")

- ✅ Spec created
- ⚠️ Some dependencies need approval
- ⚠️ POC skipped or failed
- ⚠️ ADR creation failed

### Failure (status = "failed")

- ❌ Critical error occurred
- ❌ Priority not found
- ❌ Dependency check blocked
- ❌ Cannot proceed with design

## Database Operations

### Query: Load Priority

```sql
SELECT
    rp.priority_id,
    rp.title,
    rp.description,
    rp.assigned_agent,
    rp.metadata
FROM roadmap_priority rp
WHERE rp.priority_id = ?
```

### Insert: Technical Spec

```sql
INSERT INTO technical_spec (
    spec_id, priority_id, title, description,
    complexity_score, dependencies, file_path,
    created_at, status
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), 'active')
```

### Insert: ADR

```sql
INSERT INTO adr (
    adr_id, spec_id, title, decision, rationale,
    alternatives, consequences, created_at, status
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), 'accepted')
```

### Query: Check Dependencies

```sql
SELECT
    dm.package_name,
    dm.approval_tier,
    dm.status,
    dm.rationale
FROM dependency_matrix dm
WHERE dm.package_name IN (?)
```

### Insert: POC Record

```sql
INSERT INTO poc (
    poc_id, spec_id, title, directory_path,
    status, created_at, completed_at
) VALUES (?, ?, ?, ?, 'in_progress', datetime('now'), NULL)
```

## POC Auto-Detection Logic

```python
def determine_poc_requirement(complexity_score, metadata):
    # Auto-detect based on multiple factors
    if complexity_score >= 8:  # Very high complexity
        return True

    if metadata.get("estimated_days", 0) > 5:  # Long duration
        return True

    if metadata.get("new_architecture", False):  # New patterns
        return True

    if metadata.get("external_integration", False):  # External APIs
        return True

    return False  # Default to no POC
```

## Dependency Checking (3-Tier)

### Tier 1: Pre-Approved (Auto-Accept)

```python
TIER_1 = ["pydantic", "fastapi", "sqlalchemy", "pytest", "black"]
# Automatically approved, no blocking
```

### Tier 2: Review Required (Warn)

```python
TIER_2 = ["numpy", "pandas", "requests", "boto3"]
# Requires architect review, warns but doesn't block
```

### Tier 3: Approval Required (Block)

```python
TIER_3 = ["tensorflow", "pytorch", "django"]
# Requires explicit approval, blocks until approved
```

## Error Handling

| Error | Cause | Recovery | Status |
|-------|-------|----------|--------|
| Priority not found | Invalid PRIORITY_ID | Verify priority exists | failed |
| Dependency blocked | Tier 3 not approved | Submit approval request | failed |
| POC creation failed | File system error | Review POC directory | partial |
| ADR creation failed | Write error | Manual ADR creation | partial |
| Spec exists | Duplicate spec_id | Use UPDATE depth | failed |

## Examples

### Example 1: Full Workflow

```python
result = workflow.spec(
    priority_id="PRIORITY-5",
    depth="full",
    notify=True
)
```

**Result**:
```python
SpecResult(
    spec_id="SPEC-100",
    status="success",
    priority_id="PRIORITY-5",
    steps_completed=["analyze", "dependencies", "poc", "adr", "spec"],
    steps_failed=[],
    dependencies_checked=["fastapi", "pydantic", "sqlalchemy"],
    adr_created=True,
    poc_created=True,
    duration_seconds=1800.0,  # 30 minutes
    error_message=None,
    metadata={
        "complexity_score": 8,
        "poc_path": "docs/architecture/pocs/POC-042-auth-system/",
        "adr_path": "docs/architecture/adrs/ADR-025-jwt-tokens.md",
        "spec_path": "docs/architecture/specs/SPEC-100-auth-system.md"
    }
)
```

### Example 2: Quick Design

```python
result = workflow.spec(
    priority_id="PRIORITY-6",
    depth="quick",
    notify=False
)
```

**Result**:
```python
SpecResult(
    spec_id="SPEC-101",
    status="success",
    priority_id="PRIORITY-6",
    steps_completed=["analyze", "dependencies", "spec"],
    steps_failed=[],
    dependencies_checked=["requests"],
    adr_created=False,
    poc_created=False,
    duration_seconds=600.0,  # 10 minutes
    error_message=None,
    metadata={
        "complexity_score": 4,
        "spec_path": "docs/architecture/specs/SPEC-101-api-client.md"
    }
)
```

### Example 3: POC Required

```python
result = workflow.spec(
    priority_id="PRIORITY-7",
    depth="full",
    poc_required=True,  # Force POC creation
    dependencies=["tensorflow", "keras"]
)
```

**Result**:
```python
SpecResult(
    spec_id="SPEC-102",
    status="partial",
    priority_id="PRIORITY-7",
    steps_completed=["analyze", "poc", "spec"],
    steps_failed=["dependencies"],
    dependencies_checked=["tensorflow", "keras"],
    adr_created=False,
    poc_created=True,
    duration_seconds=3600.0,  # 60 minutes
    error_message="Dependency 'tensorflow' requires Tier 3 approval",
    metadata={
        "complexity_score": 9,
        "poc_path": "docs/architecture/pocs/POC-043-ml-model/",
        "blocked_dependencies": ["tensorflow"]
    }
)
```

### Example 4: Update Existing Spec

```python
result = workflow.spec(
    priority_id="PRIORITY-5",
    depth="update",
    dependencies=["fastapi", "pydantic", "redis"]  # Added redis
)
```

**Result**:
```python
SpecResult(
    spec_id="SPEC-100",
    status="success",
    priority_id="PRIORITY-5",
    steps_completed=["load", "dependencies", "update", "adr"],
    steps_failed=[],
    dependencies_checked=["fastapi", "pydantic", "redis"],
    adr_created=True,  # Created for Redis addition
    poc_created=False,
    duration_seconds=300.0,  # 5 minutes
    error_message=None,
    metadata={
        "changes": ["added_dependency:redis"],
        "adr_path": "docs/architecture/adrs/ADR-026-redis-caching.md"
    }
)
```

## Technical Spec Structure

### Spec File Format

```markdown
# SPEC-100: Authentication System

**Priority**: PRIORITY-5
**Status**: Active
**Complexity**: 8/10
**Estimated Duration**: 5-7 days
**Dependencies**: fastapi, pydantic, sqlalchemy

## Overview
[High-level description]

## Requirements
[Functional and non-functional requirements]

## Architecture
[System design and architecture diagrams]

## Components
[Detailed component breakdown]

## Database Schema
[Database tables and relationships]

## API Endpoints
[REST API definitions]

## Security Considerations
[Security analysis]

## Testing Strategy
[Test plan]

## Deployment
[Deployment considerations]

## Dependencies
- fastapi >= 0.100.0
- pydantic >= 2.0.0
- sqlalchemy >= 2.0.0

## Related Documents
- ADR-025: JWT Token Implementation
- POC-042: Auth System Prototype
```

### ADR Format

```markdown
# ADR-025: JWT Token Implementation

**Status**: Accepted
**Date**: 2025-10-28
**Context**: SPEC-100

## Decision
Use JWT tokens for stateless authentication

## Rationale
- Stateless design scales better
- Industry standard
- Good library support

## Alternatives Considered
1. Session-based auth (rejected: doesn't scale)
2. OAuth2 only (rejected: overkill)

## Consequences
### Positive
- Better scalability
- Simpler deployment

### Negative
- Cannot revoke tokens easily
- Need refresh token strategy
```

## Implementation Notes

### Complexity Scoring

```python
def calculate_complexity(priority):
    score = 0

    # Estimated duration (1 point per day)
    score += metadata.get("estimated_days", 3)

    # New architecture patterns (+3 points)
    if metadata.get("new_architecture"):
        score += 3

    # External integrations (+2 points each)
    score += len(metadata.get("external_apis", [])) * 2

    # Database changes (+2 points)
    if metadata.get("database_changes"):
        score += 2

    return min(score, 10)  # Cap at 10
```

### POC Directory Structure

```
docs/architecture/pocs/POC-042-auth-system/
├── README.md                 # POC overview
├── prototype.py              # Working prototype code
├── requirements.txt          # Dependencies
├── tests/                    # POC tests
│   └── test_prototype.py
├── results/                  # POC results
│   ├── performance.md
│   └── findings.md
└── artifacts/                # Generated artifacts
    └── diagram.png
```

## Integration with Other Workflows

### → Project Manager (plan creation)

```python
# PM creates plan, architect creates spec
pm_result = project_manager.manage(action="plan", priority_id="PRIORITY-5")
arch_result = architect.spec(priority_id="PRIORITY-5")
```

### → Code Developer (implementation)

```python
# Architect creates spec, developer implements
arch_result = architect.spec(priority_id="PRIORITY-5")
if arch_result.status == "success":
    dev_result = developer.work(task_id="TASK-5-1")
```

### → Code Reviewer (spec review)

```python
# Architect creates spec, reviewer validates
arch_result = architect.spec(priority_id="PRIORITY-5", depth="review")
```

## Performance Expectations

| Depth | Duration | POC Created | ADR Created | Dependencies |
|-------|----------|-------------|-------------|--------------|
| FULL (simple) | 20-30m | No | Maybe | 1-3 |
| FULL (medium) | 30-60m | Maybe | Yes | 3-6 |
| FULL (complex) | 60-90m | Yes | Yes | 6-12 |
| QUICK | 5-15m | No | No | 1-3 |
| UPDATE | 5-20m | No | Maybe | Varies |
| REVIEW | 2-10m | N/A | N/A | Verify only |

## Best Practices

1. **Use FULL depth** for new priorities (default)
2. **Use QUICK depth** for simple updates or low-complexity work
3. **Use UPDATE depth** when modifying existing specs
4. **Use REVIEW depth** before implementation starts
5. **Trust POC auto-detection** (95% accuracy)
6. **Always check dependencies** before implementation
7. **Create ADRs** for all architectural decisions
8. **Review SpecResult.steps_failed** for issues

## Related Commands

- `project_manager.manage()` - Create priorities before specs
- `developer.work()` - Implement specs after creation
- `reviewer.review()` - Review spec compliance after implementation

---

**Workflow Reduction**: This single `spec()` command replaces:
1. `analyze_requirements()`
2. `check_dependencies()`
3. `create_poc()`
4. `create_adr()`
5. `generate_spec()`

**Context Savings**: ~350 lines vs ~2,000 lines (5 commands)
