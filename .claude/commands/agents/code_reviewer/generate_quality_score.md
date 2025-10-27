---
command: code_reviewer.generate_quality_score
agent: code_reviewer
action: generate_quality_score
tables:
  write: [review_code_review]
  read: [review_issue, review_code_review, review_commit]
required_tools: []
estimated_duration_seconds: 5
---

# Command: code_reviewer.generate_quality_score

## Purpose

Calculate a comprehensive quality score (1-10 scale) for a commit based on multiple quality dimensions: style, security, testing, complexity, type safety, and architecture. This unified score enables easy comparison and decisions.

## Input Parameters

```yaml
review_id: string               # Required - review to score
calculation_method: string      # "weighted", "min", "average" (default: "weighted")
weights: object                 # Custom weights for dimensions:
                                # style, security, testing, complexity,
                                # type_safety, architecture, docs
approval_threshold: number      # Score needed to approve (default: 7.0)
include_confidence: boolean     # Include confidence metric (default: true)
```

## Database Operations

**Query 1: Get all issues for review**
```sql
SELECT severity, category, COUNT(*) as count
FROM review_issue
WHERE review_id = ?
GROUP BY severity, category;
```

**Query 2: Get review metrics**
```sql
SELECT quality_score, total_issues, critical_issues, style_issues,
       security_issues, coverage_issues, approved
FROM review_code_review
WHERE id = ?;
```

**Query 3: Update review with final score**
```sql
UPDATE review_code_review
SET quality_score = ?,
    approved = ?,
    style_compliance = ?,
    architecture_compliance = ?
WHERE id = ?;
```

## Scoring Formula

### Base Score: 10.0

### Scoring Categories (Weighted)

**1. Style Compliance (20% weight)**
```
black_issues:      -0.5 each (capped -1.0)
flake8_issues:     -0.3 each (capped -1.0)
pylint_issues:     -0.1 per point below 8.0 (capped -1.0)
docstring_issues:  -0.2 each (capped -1.0)

style_score = max(0, 2.0 - total_deductions)
contribution = style_score × 0.20
```

**2. Security (25% weight - HIGHEST PRIORITY)**
```
critical_vulnerabilities: -2.5 each
high_vulnerabilities:     -1.5 each
medium_vulnerabilities:   -0.75 each
low_vulnerabilities:      -0.25 each

security_score = max(0, 2.5 - total_deductions)
contribution = security_score × 0.25
```

**3. Testing (20% weight)**
```
coverage >= 95%: 2.0
coverage >= 90%: 1.8
coverage >= 85%: 1.5
coverage >= 80%: 1.0
coverage < 80%:  0.5

test_failure:   -2.0 (auto-fails)

testing_score = coverage_score
contribution = testing_score × 0.20
```

**4. Complexity (15% weight)**
```
high_complexity_functions (>15): -0.5 each (capped -1.0)
maintainability_index:
  >= 80: 1.5
  >= 70: 1.2
  >= 60: 0.8
  >= 50: 0.4
  <  50: 0.0

complexity_score = max(0, 1.5 - deductions)
contribution = complexity_score × 0.15
```

**5. Type Safety (10% weight)**
```
mypy_errors:              -1.0 each (capped -1.0)
missing_type_hints:       -0.1 per function (capped -0.5)
type_compliance_100%:      1.0

type_score = max(0, 1.0 - deductions)
contribution = type_score × 0.10
```

**6. Architecture (10% weight - CRITICAL)**
```
CFR_violations:     -2.0 each (capped -1.0 per CFR)
Pattern_violations: -1.0 each (capped -0.5)
Singleton_issues:   -2.0
Context_budget:     -1.0 (CFR-007)

arch_score = max(0, 1.0 - deductions)
contribution = arch_score × 0.10

CRITICAL: Any CFR violation auto-disqualifies
```

### Final Calculation

```python
total_score = (
    style_contribution +
    security_contribution +
    testing_contribution +
    complexity_contribution +
    type_safety_contribution +
    architecture_contribution
)

final_score = max(1, min(10, total_score))

approved = (
    final_score >= approval_threshold and
    critical_issues == 0 and
    cfr_violations == 0
)
```

## Success Criteria

- ✅ Calculates score based on all dimensions
- ✅ Applies weights correctly
- ✅ Security weighted heavily (25%)
- ✅ Architecture violations block approval
- ✅ Score range 1-10
- ✅ Completes in <5 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "quality_score": 7,
  "approved": true,
  "approval_threshold": 7.0,
  "score_calculation": {
    "base_score": 10.0,
    "dimensions": {
      "style": {
        "score": 1.8,
        "weight": 0.20,
        "contribution": 0.36,
        "issues": {
          "black": 0,
          "flake8": 1,
          "pylint": 0,
          "docstrings": 0
        }
      },
      "security": {
        "score": 2.3,
        "weight": 0.25,
        "contribution": 0.575,
        "issues": {
          "critical": 0,
          "high": 1,
          "medium": 0,
          "low": 0
        }
      },
      "testing": {
        "score": 1.8,
        "weight": 0.20,
        "contribution": 0.36,
        "metrics": {
          "coverage": 92.3,
          "passing_tests": 145,
          "failing_tests": 0
        }
      },
      "complexity": {
        "score": 1.5,
        "weight": 0.15,
        "contribution": 0.225,
        "metrics": {
          "avg_complexity": 3.5,
          "high_complexity_functions": 0,
          "maintainability_index": 85.2
        }
      },
      "type_safety": {
        "score": 0.95,
        "weight": 0.10,
        "contribution": 0.095,
        "metrics": {
          "mypy_errors": 0,
          "type_compliance": 98.5,
          "untyped_functions": 1
        }
      },
      "architecture": {
        "score": 1.0,
        "weight": 0.10,
        "contribution": 0.10,
        "issues": {
          "cfr_violations": 0,
          "pattern_violations": 0,
          "compliance_score": 100
        }
      }
    },
    "total_contribution": 1.745,
    "penalties": 0,
    "final_score": 7
  },
  "score_interpretation": {
    "rating": "B - Good",
    "meaning": "Code quality is good and acceptable for merge",
    "notes": [
      "Fix 1 flake8 issue before merging (optional)",
      "Security: Address 1 HIGH vulnerability before merging"
    ]
  },
  "approval_decision": {
    "approved": true,
    "reason": "Score 7.0 meets threshold and no critical issues",
    "blockers": [],
    "warnings": ["1 high severity issue found"]
  }
}
```

## Score Interpretation Guide

| Score | Rating | Approval | Notes |
|-------|--------|----------|-------|
| 9-10 | A+ | APPROVED | Excellent code quality |
| 8-9 | A | APPROVED | Very good quality |
| 7-8 | B+ | APPROVED | Good quality |
| 6-7 | B | APPROVED* | Acceptable, minor issues |
| 5-6 | C | CONDITIONAL | Needs fixes before merge |
| 4-5 | D | REJECTED | Major issues, refactor needed |
| 1-4 | F | REJECTED | Critical issues, do not merge |

*Approved only if no critical issues

## Approval Rules

**Auto-Approved** (Score >= 8):
- No review needed
- Can merge immediately

**Approved** (7 <= Score < 8):
- Passes review
- Can merge
- Note any HIGH issues

**Conditional** (5 <= Score < 7):
- Needs human review
- Architect must approve
- Must address HIGH issues

**Rejected** (Score < 5):
- Cannot merge
- Must refactor
- Architect must review

**Auto-Blocked** (Despite high score):
- Any CRITICAL issues present
- Any CFR violations
- Security vulnerabilities in critical areas
- Test failures

## Error Handling

**Insufficient Data**:
```json
{
  "status": "error",
  "error_type": "INCOMPLETE_ANALYSIS",
  "message": "Cannot calculate score - missing analysis data",
  "missing": ["security_scan", "test_coverage"],
  "recommendation": "Run all analysis checks before scoring"
}
```

**No Issues Found (Perfect Score)**:
```json
{
  "status": "success",
  "quality_score": 10,
  "approved": true,
  "message": "Perfect code quality!",
  "approval_decision": {
    "approved": true,
    "reason": "Perfect score: No issues detected"
  }
}
```

## Examples

### Example 1: Standard scoring

```bash
code_reviewer.generate_quality_score(
  review_id="REV-2025-10-26T10-35-abc1",
  calculation_method="weighted",
  approval_threshold=7.0
)
```

### Example 2: Security-focused

```bash
code_reviewer.generate_quality_score(
  review_id="REV-2025-10-26T10-35-abc1",
  calculation_method="weighted",
  weights={
    "security": 0.40,
    "style": 0.15,
    "testing": 0.15,
    "complexity": 0.10,
    "type_safety": 0.10,
    "architecture": 0.10
  }
)
```

### Example 3: Strict approval

```bash
code_reviewer.generate_quality_score(
  review_id="REV-2025-10-26T10-35-abc1",
  approval_threshold=8.0
)
```

## Implementation Notes

- Scores enable rapid decision-making
- Weighted formula reflects project priorities
- Security and architecture weighted heavily
- Transparent calculation (show all components)
- Auto-blocks more reliable than manual decision
- Audit trail for approval decisions

## Related Commands

- `code_reviewer.generate_review_report` - Collect all data
- `code_reviewer.notify_architect` - Report low scores
- All analysis commands - Input for scoring

---

**Version**: 1.0
**Last Updated**: 2025-10-26
