---
command: code_reviewer.validate_dod_compliance
agent: code_reviewer
action: validate_dod_compliance
tables:
  write: [review_code_review]
  read: [specs_specification, review_code_review, review_issue, review_commit]
required_tools: [git]
estimated_duration_seconds: 15
---

# Command: code_reviewer.validate_dod_compliance

## Purpose

Verify that a commit meets all acceptance criteria defined in the technical specification (Definition of Done). This command is the final gate before approval, ensuring all requirements are met.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to validate
review_id: string               # Required - associated review
spec_id: string                 # Optional - specific spec to validate against
strict_mode: boolean            # Require 100% compliance (default: false)
check_test_evidence: boolean    # Verify tests pass (default: true)
check_documentation: boolean    # Verify docs updated (default: true)
auto_detect_spec: boolean       # Infer spec from commit message (default: true)
```

## Database Operations

**Query 1: Get spec for priority**
```sql
SELECT content, acceptance_criteria
FROM specs_specification
WHERE id = ? OR title LIKE ?;
```

**Query 2: Get review findings**
```sql
SELECT COUNT(*) as total, severity
FROM review_issue
WHERE review_id = ? AND severity IN ('CRITICAL', 'HIGH')
GROUP BY severity;
```

**Query 3: Update review DoD status**
```sql
UPDATE review_code_review
SET dod_compliant = ?,
    dod_findings = ?,
    dod_checked_at = datetime('now')
WHERE id = ?;
```

## DoD Validation Algorithm

```
1. Load specification acceptance criteria
2. For each acceptance criterion:
   a) Check if feature is implemented
   b) Check if tests exist for feature
   c) Check if documentation exists
   d) Verify test passes
   e) Check for regressions
3. Calculate compliance percentage
4. Determine if meets threshold
5. Report findings
```

## Acceptance Criteria Categories

### Category 1: Functionality

**Criteria Type**: Feature implemented and working

**Example**:
```
[ ] Feature: User authentication
  [ ] Users can log in with username/password
  [ ] Login form rejects invalid credentials
  [ ] Session persists across requests
  [ ] Logout clears session
```

**Verification**:
- Code exists in specified files
- Test coverage >80% for feature
- No test failures
- Integration tests pass

### Category 2: Testing

**Criteria Type**: Tests written and passing

**Example**:
```
[ ] Tests: >90% coverage for auth module
[ ] Tests: All happy path scenarios covered
[ ] Tests: All error cases tested
[ ] Tests: Security scenarios tested
```

**Verification**:
- Coverage report >=90%
- Test count >=N (depends on feature)
- All tests passing
- No test skips

### Category 3: Documentation

**Criteria Type**: Documentation updated

**Example**:
```
[ ] Documentation: README updated with new API
[ ] Documentation: Type hints complete
[ ] Documentation: Docstrings added
[ ] Documentation: Examples provided
```

**Verification**:
- Files modified (git diff shows changes)
- Docstring completeness >90%
- Type hint coverage 100%
- Examples section exists

### Category 4: Quality Standards

**Criteria Type**: Code quality requirements

**Example**:
```
[ ] Quality: Code style compliant (Black)
[ ] Quality: No security vulnerabilities (Bandit)
[ ] Quality: Complexity within limits (Radon)
[ ] Quality: Type hints complete (Mypy)
```

**Verification**:
- Black compliant or auto-fixed
- Bandit findings = 0 (HIGH+CRITICAL)
- Cyclomatic complexity <15
- Mypy strict compliant

### Category 5: Architecture

**Criteria Type**: Architectural compliance

**Example**:
```
[ ] Architecture: CFR compliance verified
[ ] Architecture: Design patterns followed
[ ] Architecture: No shortcuts/hacks
[ ] Architecture: Refactoring complete
```

**Verification**:
- CFR violations = 0 (or approved exceptions)
- Pattern analysis passed
- Code review approved
- No technical debt items

## Success Criteria

- ✅ Loads specification acceptance criteria
- ✅ Verifies each criterion is met
- ✅ Provides detailed compliance report
- ✅ Identifies blocking criteria (must-haves)
- ✅ Identifies optional criteria (nice-to-haves)
- ✅ Completes in <15 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "dod_check_duration_seconds": 9.8,
  "specification": {
    "spec_id": "SPEC-104",
    "title": "User Authentication System",
    "priority": "US-104",
    "acceptance_criteria_count": 12
  },
  "dod_compliance": {
    "total_criteria": 12,
    "met": 11,
    "not_met": 1,
    "compliance_percentage": 91.7,
    "status": "COMPLIANT"
  },
  "criteria_breakdown": {
    "functionality": {
      "total": 4,
      "met": 4,
      "status": "PASS"
    },
    "testing": {
      "total": 3,
      "met": 3,
      "status": "PASS"
    },
    "documentation": {
      "total": 2,
      "met": 2,
      "status": "PASS"
    },
    "quality": {
      "total": 2,
      "met": 1,
      "status": "PARTIAL"
    },
    "architecture": {
      "total": 1,
      "met": 1,
      "status": "PASS"
    }
  },
  "met_criteria": [
    {
      "criterion": "Users can log in with username/password",
      "category": "Functionality",
      "evidence": {
        "test_file": "tests/test_auth.py::test_login",
        "test_result": "PASSED",
        "code_file": "coffee_maker/auth.py",
        "coverage": 95.2
      }
    },
    {
      "criterion": "Test coverage >90% for auth module",
      "category": "Testing",
      "evidence": {
        "coverage": 92.3,
        "test_count": 18,
        "test_result": "18 passed"
      }
    }
  ],
  "unmet_criteria": [
    {
      "criterion": "No security vulnerabilities (Bandit scan)",
      "category": "Quality",
      "severity": "HIGH",
      "reason": "Bandit found 1 HIGH severity issue",
      "details": {
        "issue": "SQL injection vulnerability",
        "file": "coffee_maker/auth.py",
        "line": 45,
        "recommendation": "Use parameterized queries"
      },
      "blocking": true
    }
  ],
  "blockers": [
    {
      "criterion": "Security scan clean",
      "reason": "SQL injection vulnerability",
      "must_fix": true,
      "estimated_effort": "30 minutes"
    }
  ],
  "approval_decision": {
    "dod_compliant": false,
    "reason": "1 blocking criterion not met (Security)",
    "can_merge": false,
    "next_steps": [
      "Fix SQL injection in coffee_maker/auth.py:45",
      "Run Bandit scan again to verify fix",
      "Re-run DoD validation"
    ]
  }
}
```

## DoD Compliance Statuses

| Status | Compliance | Action |
|--------|-----------|--------|
| COMPLIANT | 100% | Can merge immediately |
| COMPLIANT_PARTIAL | 90-99% | Can merge (minor items optional) |
| NON_COMPLIANT_MINOR | 80-89% | Requires architect approval |
| NON_COMPLIANT | <80% | Cannot merge, must fix |
| BLOCKED | Any blocking issue | Cannot merge under any circumstances |

## Error Handling

**Perfect Compliance**:
```json
{
  "status": "success",
  "dod_compliance": {
    "compliance_percentage": 100.0,
    "status": "COMPLIANT"
  },
  "approval_decision": {
    "dod_compliant": true,
    "can_merge": true,
    "reason": "All acceptance criteria met"
  }
}
```

**Spec Not Found**:
```json
{
  "status": "warning",
  "error": "Cannot locate specification",
  "auto_detect_attempted": true,
  "commit_message": "feat: Add authentication",
  "recommendation": "Provide spec_id parameter or ensure commit message contains US-XXX"
}
```

**Multiple Blockers**:
```json
{
  "status": "error",
  "blockers": [
    {"criterion": "Security scan clean", "blocking": true},
    {"criterion": "All tests passing", "blocking": true},
    {"criterion": "Documentation complete", "blocking": true}
  ],
  "approval_decision": {
    "dod_compliant": false,
    "can_merge": false,
    "reason": "3 blocking criteria not met"
  }
}
```

## Examples

### Example 1: Full DoD validation

```bash
code_reviewer.validate_dod_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  spec_id="SPEC-104",
  strict_mode=false,
  auto_detect_spec=true
)
```

### Example 2: Strict validation

```bash
code_reviewer.validate_dod_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  strict_mode=true
)
```

### Example 3: Quick check (no tests)

```bash
code_reviewer.validate_dod_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_test_evidence=false,
  check_documentation=false
)
```

## Implementation Notes

- DoD validation is final gate before merge
- Blocking criteria override other approvals
- Criteria should be verifiable and objective
- Some criteria can be auto-verified (tests, coverage)
- Some require human judgment (code review, design)
- Store DoD results for compliance reporting
- Track DoD violations for quality metrics

## Common DoD Criteria Patterns

### Pattern 1: Feature Implementation

```markdown
## Acceptance Criteria: Feature Implementation

- [ ] Feature code exists in specified modules
- [ ] Feature works with happy path inputs
- [ ] Feature handles error cases gracefully
- [ ] Feature integrates with existing code
- [ ] Feature doesn't break existing functionality
```

### Pattern 2: Testing Requirements

```markdown
## Acceptance Criteria: Testing

- [ ] Unit tests for all new functions
- [ ] Integration tests for feature workflows
- [ ] Error condition tests
- [ ] Test coverage >= 90%
- [ ] All tests passing
- [ ] No test skips or xfails
```

### Pattern 3: Code Quality

```markdown
## Acceptance Criteria: Code Quality

- [ ] Code style compliant (Black, flake8)
- [ ] Type hints complete (Mypy)
- [ ] Complexity within limits (Radon)
- [ ] Security scan clean (Bandit)
- [ ] No architectural violations (CFRs)
```

### Pattern 4: Documentation

```markdown
## Acceptance Criteria: Documentation

- [ ] Function docstrings complete
- [ ] Examples provided for public APIs
- [ ] README updated
- [ ] Architecture doc updated (if relevant)
- [ ] CHANGELOG entry added
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review data
- `code_reviewer.generate_quality_score` - Quality metrics
- `code_reviewer.check_architecture_compliance` - CFR checks

---

**Version**: 1.0
**Last Updated**: 2025-10-26
