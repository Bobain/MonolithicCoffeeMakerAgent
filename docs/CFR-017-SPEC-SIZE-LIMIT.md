# CFR-017: Technical Specification Size Limit

**Status**: Active ✅
**Created**: 2025-10-28
**Owner**: Architect
**Related**: CFR-007 (Context Budget), CFR-016 (Incremental Implementation)

---

## Requirement

**All technical specifications MUST be ≤320 lines (20% of context budget).**

This is a hard limit enforced during spec creation and task assignment.

---

## Rationale

### 1. Context Budget Mathematics

**Total context window**: 32,000 tokens ≈ 1,600 lines (at 20 tokens/line)

**Agent execution context breakdown**:
```
Commands (3 loaded):     360 lines (23% budget)
Task spec (this limit):  320 lines (20% budget)
Code context:            240 lines (15% budget)
───────────────────────────────────────────────
Total execution:         920 lines (58% budget) ✅
```

**Why 58% matters**: See Anthropic's <60% recommendation below.

### 2. Anthropic's <60% Context Recommendation

**Source**: Anthropic best practices for long-context LLMs

**The Problem**: "Lost in the Middle" Effect
- LLMs perform worse when critical information is buried in long context
- Attention mechanisms degrade with distance from query
- Information recall drops significantly past 60% context utilization

**Research Findings**:
- **0-40% context**: Excellent recall and reasoning
- **40-60% context**: Good performance, acceptable degradation
- **60-80% context**: Noticeable quality drop, "middle" information lost
- **80-100% context**: Severe degradation, unreliable outputs

**Graph (Conceptual)**:
```
Quality
  100% |████████████████░░░░░░░░░░░░░░░░░░░░░░░
   90% |████████████████████░░░░░░░░░░░░░░░░░░
   80% |████████████████████████░░░░░░░░░░░░░░
   70% |████████████████████████████░░░░░░░░░░
   60% |█████████████████████████████░░░░░░░░░
   50% |██████████████████████████████░░░░░░░░
       └────────────────────────────────────────
        0%    20%    40%    60%    80%   100%
                Context Utilization
```

**Our Target**: **58% total context during task execution**
- Optimal performance zone (40-60%)
- Leaves 42% buffer for system prompts and dynamic content
- Ensures critical information (spec, commands) is well-attended

### 3. Spec Quality Benefits

**Forces clarity and focus**:
- Architect must prioritize essential information
- Eliminates verbose documentation
- Makes specs more actionable

**Reduces cognitive load**:
- Code developers can quickly understand requirements
- Less scrolling, faster comprehension
- Clear, concise task definitions

**Prevents scope creep**:
- 320-line limit naturally bounds feature complexity
- Encourages modular design
- Complex features → multiple specs (decomposition)

### 4. Real-World Impact

**Without this limit** (observed problems):
- Specs ballooned to 500-800 lines
- Code developers overwhelmed by detail
- Context budget violations (>80% utilization)
- Degraded LLM performance, errors in implementation

**With this limit** (expected benefits):
- Concise, focused specifications
- Predictable context usage
- Better LLM performance
- Faster implementation cycles

---

## Specification Structure (320 Lines)

### Recommended Template

```markdown
# SPEC-XXX: {Title}

## Overview (30 lines)
**Purpose**: What problem does this solve?
**Goals**: Measurable success criteria
**Scope**: What's included/excluded

## Architecture (60 lines)
**System Design**: Component diagram (ASCII or description)
**Interactions**: How components communicate
**Data Models**: Key entities and relationships
**Patterns**: Design patterns used

## Implementation Tasks (120 lines)
**Breakdown**: 5-8 implementation tasks

### TASK-XXX-1: {Task Title} (15-20 lines each)
- **Description**: What to implement
- **Files**: Files to create/modify
- **Database**: Tables/columns needed
- **Tests**: Test requirements
- **Estimate**: Hours (1-8h per task)
- **Dependencies**: Blocking tasks (if any)

[Repeat for each task]

## Database Schema (40 lines)
**Tables**: New tables with columns
**Indexes**: Performance indexes
**Migrations**: Migration steps
**Sample Queries**: Common operations

## Testing Strategy (30 lines)
**Unit Tests**: Coverage targets (>90%)
**Integration Tests**: Key scenarios
**Edge Cases**: Error conditions
**Performance**: Benchmarks (if applicable)

## Acceptance Criteria (20 lines)
**Definition of Done (DoD)**:
- [ ] All tests pass
- [ ] Code review complete
- [ ] Documentation updated
- [ ] Performance validated

## Dependencies (20 lines)
**External Packages**: New dependencies (with approval status)
**Internal Modules**: Existing code dependencies
**Breaking Changes**: Impact on existing features
```

**Total**: ≤320 lines

---

## Enforcement

### 1. Validation During Spec Creation

**Architect agent MUST validate before saving spec**:

```python
def validate_spec_size(spec_content: str, spec_id: str) -> None:
    """Validate spec fits in 20% context budget (CFR-017)."""
    lines = spec_content.split('\n')
    line_count = len([l for l in lines if l.strip()])  # Non-empty lines

    MAX_LINES = 320

    if line_count > MAX_LINES:
        raise SpecSizeViolationError(
            f"CFR-017 VIOLATION: {spec_id} has {line_count} lines "
            f"(max: {MAX_LINES}). Spec is too large.\n\n"
            f"Options:\n"
            f"1. Compress content (remove verbosity)\n"
            f"2. Split into multiple specs\n"
            f"3. Move details to ADR/POC documentation"
        )

    if line_count > 280:  # Warning at 88% of limit
        logger.warning(
            f"CFR-017 WARNING: {spec_id} has {line_count} lines "
            f"({line_count/MAX_LINES:.0%} of limit). Consider compression."
        )
```

### 2. Validation Before Task Assignment

**Code developer / Orchestrator MUST validate before starting task**:

```python
def load_task_with_spec(task_id: str) -> dict:
    """Load task and validate spec size (CFR-017)."""
    # Load from database
    task = db.query("SELECT * FROM specs_task WHERE task_id = ?", task_id)
    spec = db.query("SELECT * FROM technical_spec WHERE spec_id = ?", task.spec_id)

    # Validate spec size
    spec_lines = len(spec.content.split('\n'))

    if spec_lines > 320:
        notify_architect(
            f"CFR-017 VIOLATION: {spec.spec_id} is {spec_lines} lines. "
            f"Cannot proceed with implementation until compressed."
        )
        raise SpecSizeViolationError(f"Spec too large: {spec_lines} lines")

    return {"task": task, "spec": spec}
```

### 3. Pre-Commit Hook (Optional)

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check all spec files
for spec in docs/architecture/specs/SPEC-*.md; do
    lines=$(wc -l < "$spec" | tr -d ' ')
    if [ "$lines" -gt 320 ]; then
        echo "❌ CFR-017 VIOLATION: $spec has $lines lines (max: 320)"
        exit 1
    fi
done
```

---

## Handling Large Features

### When Feature is Legitimately Complex

**Option 1: Decompose into Multiple Specs**

```
Original: SPEC-042: Complete OAuth2 System (650 lines) ❌

Decomposed:
├── SPEC-042: OAuth2 Core Flow (280 lines) ✅
├── SPEC-043: OAuth2 Provider Management (250 lines) ✅
└── SPEC-044: OAuth2 Token Refresh (200 lines) ✅
```

**Benefits**:
- Each spec fits budget
- Enables parallel implementation
- Clearer task boundaries
- Better testability

**Option 2: Extract to POC**

```
SPEC-042: OAuth2 Implementation (320 lines) ✅
  ├── Overview: 30 lines
  ├── Architecture: 60 lines (high-level)
  ├── Tasks: 120 lines
  ├── Schema: 40 lines
  ├── Testing: 30 lines
  ├── Criteria: 20 lines
  └── Dependencies: 20 lines

POC-015: OAuth2 Detailed Architecture (500 lines)
  ├── Detailed flow diagrams
  ├── Security analysis
  ├── Edge case handling
  ├── Performance benchmarks
  └── Integration examples
```

**Benefits**:
- Spec remains concise (320 lines)
- POC has unlimited space for detail
- POC serves as reference, not execution context

**Option 3: Extract to ADR**

```
SPEC-042: OAuth2 Implementation (300 lines) ✅

ADR-023: OAuth2 vs SAML Decision (unlimited)
  ├── Why OAuth2 chosen
  ├── SAML evaluation
  ├── Trade-off analysis
  └── Implementation rationale
```

**Benefits**:
- Spec focused on "what" and "how"
- ADR captures "why" (historical context)
- ADR doesn't load during implementation

---

## Metrics and Monitoring

### Spec Size Dashboard

Track compliance over time:

```sql
-- Average spec size
SELECT AVG(LENGTH(content) / 20) as avg_lines
FROM technical_spec
WHERE created_at > date('now', '-30 days');

-- Oversized specs
SELECT spec_id, title, LENGTH(content) / 20 as lines
FROM technical_spec
WHERE LENGTH(content) / 20 > 320
ORDER BY lines DESC;

-- Compliance rate
SELECT
    COUNT(*) as total_specs,
    SUM(CASE WHEN LENGTH(content)/20 <= 320 THEN 1 ELSE 0 END) as compliant,
    ROUND(100.0 * SUM(CASE WHEN LENGTH(content)/20 <= 320 THEN 1 ELSE 0 END) / COUNT(*), 1) as compliance_rate
FROM technical_spec;
```

---

## Examples

### ✅ Good Example: SPEC-042 (280 lines)

```markdown
# SPEC-042: OAuth2 Authentication Flow

## Overview (25 lines)
Implement OAuth2 authentication with Google, GitHub providers.
Success: Users can login via OAuth2, sessions persist.

## Architecture (55 lines)
- OAuth2Provider model (database)
- AuthController (Flask routes)
- TokenManager (session handling)
[Component diagram...]

## Implementation Tasks (110 lines)

### TASK-42-1: OAuth2 Provider Model (18 lines)
- Create OAuth2Provider table
- Fields: provider_name, client_id, client_secret, redirect_uri
- Migration: 20251028_add_oauth2_providers.py

### TASK-42-2: Auth Routes (20 lines)
- /auth/oauth2/login/<provider>
- /auth/oauth2/callback/<provider>
- Handle state validation

[... 3 more tasks ...]

## Database Schema (35 lines)
[Tables, indexes, migrations]

## Testing Strategy (28 lines)
[Unit, integration, edge cases]

## Acceptance Criteria (15 lines)
[DoD checklist]

## Dependencies (12 lines)
- authlib (pre-approved)
- flask-session
```

**Total: 280 lines** ✅ Under limit, well-structured

### ❌ Bad Example: SPEC-999 (650 lines)

```markdown
# SPEC-999: Complete User Management System

## Overview (100 lines)
[Overly detailed problem statement, extensive background, multiple use cases]

## Architecture (200 lines)
[Exhaustive component descriptions, detailed sequence diagrams in ASCII,
every possible interaction documented, defensive over-engineering]

## Implementation Tasks (250 lines)
[20 micro-tasks with excessive detail, redundant information]

## Database Schema (80 lines)
[Every field documented with examples, sample data, extensive notes]

## Testing Strategy (20 lines)
## Acceptance Criteria (20 lines)
```

**Total: 650 lines** ❌ Violates CFR-017

**Fix**: Split into 3 specs or compress by 50%

---

## FAQ

### Q: What if my feature genuinely needs more detail?

**A**: Use POC or ADR for deep dives. Specs are execution documents, not encyclopedias. Also see CFR-016 for breaking specs into incremental steps.

### Q: Can I reference external docs to save space?

**A**: Yes, but remember:
- If architect/code_developer loads external docs → they count toward budget
- If never loaded → they're useless
- Better to inline essential info, external docs for optional reading

### Q: How do I count lines?

**A**: Non-empty lines only. Use validation script:
```bash
grep -v '^\s*$' spec.md | wc -l
```

### Q: What counts as "context budget"?

**A**: Everything loaded during task execution:
- Commands (3 prompts)
- Technical spec (this CFR limits)
- Code being modified
- Examples (if loaded)
- Skills (if loaded)

### Q: Can I request exemption?

**A**: No. This is a hard architectural constraint. If feature is too complex, decompose it.

---

## Related CFRs

- **CFR-007**: Context Budget (30% for commands)
- **CFR-013**: Git Workflow (worktree per task)
- **CFR-015**: Centralized Database Storage
- **CFR-016**: Incremental Implementation (break specs into phases)

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2025-10-28 | Initial CFR creation |

---

**Last Updated**: 2025-10-28
**Status**: Active ✅
**Compliance Required**: All new specs from 2025-10-28 onwards
