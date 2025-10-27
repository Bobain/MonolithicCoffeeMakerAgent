---
command: code_reviewer.check_architecture_compliance
agent: code_reviewer
action: check_architecture_compliance
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [git, grep]
estimated_duration_seconds: 25
---

# Command: code_reviewer.check_architecture_compliance

## Purpose

Verify that code follows Critical Functional Requirements (CFRs) and architectural patterns defined in the project. This command ensures architectural consistency across the codebase.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to check
review_id: string               # Required - link issues to review
check_cfrs: array               # CFRs to verify (default: all)
check_patterns: array           # Patterns to verify (default: all)
check_dependencies: boolean     # Check dependency patterns (default: true)
check_singletons: boolean       # Check singleton usage (default: true)
show_recommendations: boolean   # Include fix recommendations (default: true)
```

## Database Operations

**Query: Insert architecture issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Architecture', ?, ?, ?, ?, datetime('now'));
```

## CFR Compliance Checks

### CFR-000: Singleton Agent Enforcement

**Requirement**: Each agent type must have only ONE running instance at a time

**Check**:
```bash
# Verify AgentRegistry is used correctly
grep -r "AgentRegistry.register" coffee_maker/ --include="*.py" | wc -l

# Should have pattern: with AgentRegistry.register(AgentType.X):
grep -r "with AgentRegistry.register" coffee_maker/ --include="*.py"
```

**Issues to detect**:
- ❌ Creating agent instances without AgentRegistry
- ❌ Multiple instances of same agent type
- ❌ Not using context manager pattern
- ❌ Registry not properly initialized

**Severity**: CRITICAL

### CFR-007: Context Budget Compliance

**Requirement**: Agent core materials must fit in ≤30% of context window

**Check**:
```bash
# Check for excessive spec loading
grep -r "read_full_spec\|load_entire_spec" coffee_maker/ --include="*.py"

# Verify progressive disclosure usage
grep -r "read_hierarchical_spec" coffee_maker/ --include="*.py"
```

**Issues to detect**:
- ❌ Loading entire specs instead of hierarchical sections
- ❌ No context budget calculations
- ❌ All materials loaded regardless of task
- ❌ CFR-007 comments missing

**Severity**: HIGH

### CFR-009: Sound Notifications

**Requirement**: Only user_listener uses sound=True, all background agents use sound=False

**Check**:
```bash
# Find all notification calls
grep -r "sound=True" coffee_maker/ --include="*.py"

# Verify sound=False for background agents
grep -r "sound=False" coffee_maker/autonomous --include="*.py"
```

**Issues to detect**:
- ❌ Background agents using sound=True
- ❌ code_developer, architect, project_manager with sound=True
- ❌ Missing sound parameter (defaults to True)

**Severity**: HIGH

### CFR-013: Git Workflow

**Requirement**: Work on roadmap branch only, use worktree for parallel tasks

**Check**:
```bash
# Verify branch name
git branch | grep "roadmap"

# Check for feature branches (should not exist)
git branch | grep -E "feature/|develop|master"

# Verify worktree naming convention
git worktree list | grep "roadmap-implementation_task-"
```

**Issues to detect**:
- ❌ Working on non-roadmap branch
- ❌ Creating feature branches
- ❌ Not using worktrees for parallel work
- ❌ Incorrect worktree naming

**Severity**: HIGH

### CFR-014: Database Tracing

**Requirement**: ALL orchestrator activities in SQLite database, JSON files forbidden

**Check**:
```bash
# Find JSON file writes from orchestrator
grep -r "json.dump\|json.dumps" coffee_maker/orchestrator --include="*.py"

# Verify database usage
grep -r "INSERT INTO\|UPDATE" coffee_maker/orchestrator --include="*.py"
```

**Issues to detect**:
- ❌ JSON files created from orchestrator code
- ❌ Missing database tracing
- ❌ Duplicate tracking in both JSON and DB

**Severity**: CRITICAL

### CFR-015: Database Storage

**Requirement**: Database files in data/ directory only

**Check**:
```bash
# Find databases outside data/ directory
find coffee_maker -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3"

# Verify all databases in data/
ls -la data/*.db 2>/dev/null | wc -l
```

**Issues to detect**:
- ❌ Database files in root, .claude/, or other directories
- ❌ No data/ directory
- ❌ Hardcoded database paths

**Severity**: CRITICAL

## Architectural Pattern Checks

### Pattern: Mixin Composition

**Requirement**: Use composition (mixins) instead of inheritance

**Check**:
```bash
# Find mixin usage
grep -r "class.*Mixin" coffee_maker/ --include="*.py"

# Verify no deep inheritance chains
grep -r "class.*[^Mixin].*([^O].*class" coffee_maker/ --include="*.py"
```

**Issues to detect**:
- ❌ Deep inheritance hierarchies
- ❌ No mixins for shared functionality
- ❌ Mixin code duplication

**Severity**: MEDIUM

### Pattern: Type Hints

**Requirement**: Type hints required for all functions

**Check**:
```bash
# Find functions without type hints
grep -r "def [a-zA-Z_]" coffee_maker/ --include="*.py" | grep -v " ->"

# Verify in coffee_maker/ but not tests/
grep -r "def [a-zA-Z_].*:" coffee_maker/ --include="*.py" | wc -l
```

**Issues to detect**:
- ❌ Missing parameter type hints
- ❌ Missing return type hints
- ❌ Untyped function definitions

**Severity**: MEDIUM

### Pattern: Error Handling

**Requirement**: Defensive error handling with specific exceptions

**Check**:
```bash
# Find bare except clauses
grep -r "except:" coffee_maker/ --include="*.py"

# Verify exception chaining
grep -r "except.*as.*:" coffee_maker/ --include="*.py" | wc -l
```

**Issues to detect**:
- ❌ Bare except clauses catching all exceptions
- ❌ No exception context preservation
- ❌ Generic Exception usage instead of specific types

**Severity**: HIGH

### Pattern: Logging

**Requirement**: Use structured logging with context

**Check**:
```bash
# Verify logging setup
grep -r "logger = logging.getLogger" coffee_maker/ --include="*.py"

# Check for f-string logging (should use formatting)
grep -r "logger.*f\"" coffee_maker/ --include="*.py"
```

**Issues to detect**:
- ❌ Missing logger initialization
- ❌ print() statements instead of logging
- ❌ Insufficient log context

**Severity**: MEDIUM

## Success Criteria

- ✅ Checks all specified CFRs
- ✅ Verifies architectural patterns
- ✅ Creates issues for violations
- ✅ Provides fix recommendations
- ✅ Ranks violations by severity
- ✅ Completes in <25 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "compliance_check_duration_seconds": 18.5,
  "cfr_compliance": {
    "total_cfrs_checked": 6,
    "cfrs_passed": 5,
    "cfrs_failed": 1,
    "compliance_score": 83.3
  },
  "pattern_compliance": {
    "total_patterns_checked": 4,
    "patterns_passed": 3,
    "patterns_failed": 1,
    "compliance_score": 75.0
  },
  "violations": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Architecture",
      "type": "CFR-009",
      "description": "CFR-009 violation: project_manager agent uses sound=True",
      "file_path": "coffee_maker/autonomous/daemon.py",
      "line_number": 245,
      "requirement": "Background agents must use sound=False (CFR-009)",
      "recommendation": "Change sound=True to sound=False",
      "cfr_link": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/docs/architecture/guidelines/CFR-009.md"
    },
    {
      "id": "ISS-2",
      "severity": "MEDIUM",
      "category": "Architecture",
      "type": "Pattern",
      "description": "Missing type hints in function definition",
      "file_path": "coffee_maker/utils.py",
      "line_number": 42,
      "requirement": "All functions require complete type hints",
      "recommendation": "Add type hints: def process(data: dict) -> str:",
      "example": "def process(data: dict) -> str:\n    return str(data)"
    }
  ],
  "summary": {
    "total_violations": 2,
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 1,
    "architecture_health": "GOOD"
  }
}
```

## Error Handling

**Perfect Compliance**:
```json
{
  "status": "success",
  "cfr_compliance": {
    "cfrs_passed": 6,
    "cfrs_failed": 0,
    "compliance_score": 100
  },
  "pattern_compliance": {
    "patterns_passed": 4,
    "patterns_failed": 0,
    "compliance_score": 100
  },
  "message": "Perfect architecture compliance"
}
```

**Multiple Violations**:
```json
{
  "status": "warning",
  "violations": [...],
  "summary": {
    "total_violations": 5,
    "critical_count": 2,
    "high_count": 2,
    "medium_count": 1
  },
  "note": "Fix critical violations before merge"
}
```

## Examples

### Example 1: Full architecture check

```bash
code_reviewer.check_architecture_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_cfrs=["CFR-000", "CFR-007", "CFR-009", "CFR-013", "CFR-014", "CFR-015"],
  check_patterns=["mixin_composition", "type_hints", "error_handling", "logging"]
)
```

### Example 2: CFR-only check

```bash
code_reviewer.check_architecture_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_cfrs=["CFR-000", "CFR-009"],
  check_patterns=[]
)
```

## Implementation Notes

- CFR violations are more severe than pattern violations
- Critical violations block merge
- Provide links to CFR documentation
- Include examples of compliant code
- Track architecture violations for trend analysis
- Consider legacy exceptions for refactoring tasks

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.notify_architect` - Escalate violations
- `code_reviewer.check_style_compliance` - Code quality checks

---

**Version**: 1.0
**Last Updated**: 2025-10-26
