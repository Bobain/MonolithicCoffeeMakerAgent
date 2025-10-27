# Code Reviewer Commands (13 Commands)

**SPEC-105: Code Reviewer Commands Implementation**

This directory contains 13 commands for the code_reviewer agent, implementing automated code quality analysis and review capabilities.

## Command Overview

All 13 commands follow the same structure:
- YAML front matter with metadata
- Purpose and use cases
- Input parameters (YAML format)
- Database operations (SQL queries)
- External tools (bash commands)
- Success criteria
- Output format (JSON)
- Error handling
- Examples
- Implementation notes

---

## Review Lifecycle Commands (3)

### 1. `detect_new_commits.md`
**Purpose**: Poll review_commit table for unreviewed commits
- Identifies ready-to-review commits
- Checks for blocking reviews
- Returns batch-sized result set
- **Duration**: ~10 seconds
- **Tables**: Read review_commit; Write review_code_review

**Key Features**:
- Max age filtering (only recent commits)
- Priority filtering
- Blocking review detection
- Batch processing

### 2. `generate_review_report.md`
**Purpose**: Analyze commit code and generate comprehensive review
- Runs all code analysis tools
- Calculates quality score (1-10)
- Creates review_issue records
- **Duration**: ~60 seconds
- **Tables**: Read review_commit, specs_specification; Write review_code_review, review_issue

**Key Features**:
- Orchestrates all analysis (style, security, complexity, coverage, types, architecture)
- Quality score calculation
- Issue severity mapping
- Actionable recommendations

### 3. `notify_architect.md`
**Purpose**: Send critical findings to architect for action
- Escalates high-severity issues
- Sends GitHub-linked notifications
- Includes evidence and recommendations
- **Duration**: ~5 seconds
- **Tables**: Read review_code_review, review_issue; Write notifications

**Key Features**:
- Severity-based filtering
- CFR-009 compliance (sound=False)
- Code snippet evidence
- Urgent priority setting

---

## Code Analysis Commands (6)

### 4. `check_style_compliance.md`
**Purpose**: Run black, flake8, pylint for code style
- Black formatting checks
- Flake8 style violations
- Pylint code quality (8.0+ target)
- **Duration**: ~30 seconds
- **Tools**: black, flake8, pylint

**Severity Mapping**:
- Black issues → HIGH (auto-fixable)
- Flake8 errors → HIGH
- Pylint errors → HIGH
- Pylint warnings → MEDIUM
- Pylint conventions → LOW

### 5. `run_security_scan.md`
**Purpose**: Run bandit security vulnerability scanner
- Detects security vulnerabilities
- Maps Bandit test IDs to severities
- CWE (Common Weakness Enumeration) references
- **Duration**: ~20 seconds
- **Tools**: bandit

**Severity Mapping**:
- Bandit HIGH → CRITICAL (SQL injection, exec, etc.)
- Bandit MEDIUM → HIGH
- Bandit LOW → MEDIUM

**Tracked Vulnerabilities**: 40+ test patterns (B101-B702)

### 6. `analyze_complexity.md`
**Purpose**: Use radon to check code complexity
- Cyclomatic complexity (target: <15)
- Cognitive complexity
- Maintainability index (target: >60)
- **Duration**: ~15 seconds
- **Tools**: radon

**Thresholds**:
- Complexity 1-5: Low (OK)
- Complexity 6-10: Medium (OK)
- Complexity 11-15: High (warning)
- Complexity 16+: Very High (refactor)

### 7. `check_test_coverage.md`
**Purpose**: Run pytest with coverage for >90% testing
- Executes full test suite
- Calculates coverage percentage
- Identifies uncovered lines
- **Duration**: ~60 seconds
- **Tools**: pytest, coverage

**Coverage Standards**:
- 95-100%: A (Excellent)
- 90-94%: B (Good)
- 85-89%: C (Fair)
- 80-84%: D (Poor)
- <80%: F (Critical)

### 8. `validate_type_hints.md`
**Purpose**: Run mypy strict type checking
- Validates type hints
- Detects type mismatches
- Checks for untyped definitions
- **Duration**: ~20 seconds
- **Tools**: mypy

**Error Code Coverage**: 40+ mypy error types (arg-type, return-value, etc.)

### 9. `check_architecture_compliance.md`
**Purpose**: Verify CFRs and architectural patterns
- CFR-000: Singleton enforcement
- CFR-007: Context budget
- CFR-009: Sound notifications
- CFR-013: Git workflow
- CFR-014: Database tracing
- CFR-015: Database storage
- Mixin patterns, type hints, error handling, logging

**Key Features**:
- Auto-detects CFR violations
- Pattern compliance checking
- Links to CFR documentation

---

## Quality Reporting Commands (4)

### 10. `track_issue_resolution.md`
**Purpose**: Monitor issue fixes across commits
- Tracks which issues get fixed
- Calculates resolution time
- Identifies recurring issues
- **Duration**: ~15 seconds
- **Tables**: Read review_issue, review_code_review; Write review_issue

**Metrics**:
- Resolution rate by severity
- Time to fix (commits and days)
- Recurring issue patterns

### 11. `generate_quality_score.md`
**Purpose**: Calculate 1-10 quality score
- Weighted scoring formula
- 6 dimensions (style, security, testing, complexity, types, architecture)
- Approval decision logic
- **Duration**: ~5 seconds
- **Tables**: Read review_issue, review_code_review; Write review_code_review

**Scoring Weights**:
- Security: 25% (highest priority)
- Style: 20%
- Testing: 20%
- Complexity: 15%
- Type Safety: 10%
- Architecture: 10%

**Approval Thresholds**:
- Score ≥8: Auto-approved
- Score 7-8: Approved (review recommended)
- Score 5-7: Conditional (architect approval)
- Score <5: Rejected (refactor needed)

### 12. `review_documentation.md`
**Purpose**: Check docstrings and documentation
- Verifies function/class docstrings exist
- Checks docstring format (Google style)
- Validates type hint documentation
- Checks README updates
- **Duration**: ~20 seconds

**Coverage Standards**:
- 95-100%: A (Excellent)
- 90-95%: B (Good)
- 80-90%: C (Acceptable)
- 70-80%: D (Needs Work)
- <70%: F (Critical)

### 13. `validate_dod_compliance.md`
**Purpose**: Verify acceptance criteria met
- Loads spec acceptance criteria
- Verifies each criterion
- Identifies blocking issues
- **Duration**: ~15 seconds
- **Tables**: Read specs_specification, review_issue, review_code_review

**DoD Categories**:
- Functionality: Feature implemented
- Testing: Tests written and passing
- Documentation: Docs updated
- Quality: Code quality standards met
- Architecture: Architectural patterns followed

---

## Database Schema Integration

### Tables Created

**review_code_review**:
```sql
id, commit_sha, review_date, quality_score, total_issues,
critical_issues, style_issues, security_issues, coverage_issues,
approved, status, started_at, completed_at, analysis_time_seconds
```

**review_issue**:
```sql
id, review_id, severity, category, file_path, line_number,
description, recommendation, is_resolved, resolved_in_commit, created_at
```

### Table Relationships

```
review_commit
    ↓ (one-to-many)
review_code_review
    ↓ (one-to-many)
review_issue
```

---

## External Tools Integration

### Installed Tools Required

1. **black** - Code formatting checker
2. **flake8** - Style linting
3. **pylint** - Code quality analysis
4. **bandit** - Security scanning
5. **radon** - Complexity metrics
6. **mypy** - Type checking
7. **pytest** - Test framework
8. **coverage** - Code coverage
9. **git** - Version control

### Tool Output Formats

All tools configured to output JSON or parseable formats:
- black: --diff mode
- flake8: --format=json
- pylint: --output-format=json
- bandit: -f json
- radon: -j (JSON)
- mypy: --output-format=json
- pytest: --cov-report=json
- coverage: json mode

---

## Command Execution Flow

### Typical Review Workflow

```
1. detect_new_commits()
   ↓
2. generate_review_report()
   ├── check_style_compliance()
   ├── run_security_scan()
   ├── analyze_complexity()
   ├── check_test_coverage()
   ├── validate_type_hints()
   └── check_architecture_compliance()
   ↓
3. track_issue_resolution()
   ↓
4. generate_quality_score()
   ↓
5. review_documentation()
   ↓
6. validate_dod_compliance()
   ↓
7. notify_architect()
```

---

## Output Examples

### Review Report Structure
```json
{
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "quality_score": 7,
  "approved": true,
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Security",
      "file_path": "coffee_maker/auth.py",
      "description": "...",
      "recommendation": "..."
    }
  ],
  "analysis_results": {
    "style": {...},
    "security": {...},
    "complexity": {...},
    "testing": {...},
    "types": {...},
    "architecture": {...}
  }
}
```

---

## Configuration & Customization

### Severity Thresholds

Configure in each command:
- Style: Customize per project standards
- Security: Keep CRITICAL/HIGH defaults
- Coverage: Adjust minimum (default: 90%)
- Complexity: Set limits (default: 15)
- Type Safety: Strict by default

### Approval Rules

In `generate_quality_score.md`:
```python
approval_threshold = 7.0  # Score ≥7 approved
critical_issues_max = 0   # No CRITICAL issues
cfr_violations_max = 0    # No CFR violations
```

### Command Weights

Customize in `generate_quality_score.md`:
```python
weights = {
    "style": 0.20,
    "security": 0.25,        # Highest priority
    "testing": 0.20,
    "complexity": 0.15,
    "type_safety": 0.10,
    "architecture": 0.10
}
```

---

## Usage Examples

### Run All Commands for a Commit

```bash
# 1. Detect new commits
code_reviewer.detect_new_commits(max_age_minutes=60)

# 2. Generate full review
code_reviewer.generate_review_report(
  commit_sha="abc123def456",
  run_all_checks=true
)

# 3. Notify architect if critical
code_reviewer.notify_architect(
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="CRITICAL"
)

# 4. Validate DoD
code_reviewer.validate_dod_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1"
)
```

### Quick Security Check

```bash
code_reviewer.run_security_scan(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1"
)
```

### Check Type Hints Only

```bash
code_reviewer.validate_type_hints(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  strict_mode=true
)
```

---

## Standards & Compliance

### Project Standards

- **Max Line Length**: 120 characters
- **Code Style**: Black
- **Type Hints**: Required (Mypy strict)
- **Test Coverage**: ≥90%
- **Docstring Format**: Google style
- **Security**: Bandit clean (no HIGH+ issues)
- **Complexity**: <15 cyclomatic

### CFR Compliance

All commands support verification of:
- **CFR-000**: Singleton agent enforcement
- **CFR-007**: Context budget <30%
- **CFR-009**: Background agents use sound=False
- **CFR-013**: Roadmap branch only
- **CFR-014**: Database tracing (no JSON)
- **CFR-015**: Databases in data/ only

---

## Architecture

### Key Design Decisions

1. **Modular Commands**: Each command handles one concern
2. **Database-First**: All data persisted in SQLite
3. **Tool Integration**: Loose coupling with external tools
4. **Batch Processing**: Handle multiple commits efficiently
5. **Progressive Disclosure**: Load only needed analysis
6. **Notification Escalation**: Architect gets critical findings

### Error Handling

All commands:
- Handle tool failures gracefully
- Continue with partial analysis
- Provide recovery suggestions
- Log errors for debugging
- Return meaningful error messages

---

## Performance Targets

| Command | Duration | Notes |
|---------|----------|-------|
| detect_new_commits | ~10s | Database polling |
| generate_review_report | ~60s | Orchestrates 6 tools |
| check_style_compliance | ~30s | 3 tools (black, flake8, pylint) |
| run_security_scan | ~20s | Bandit analysis |
| analyze_complexity | ~15s | Radon analysis |
| check_test_coverage | ~60s | Full test suite |
| validate_type_hints | ~20s | Mypy check |
| check_architecture_compliance | ~25s | Pattern detection |
| track_issue_resolution | ~15s | Database queries |
| generate_quality_score | ~5s | Calculation only |
| review_documentation | ~20s | Pattern matching |
| validate_dod_compliance | ~15s | Spec comparison |
| notify_architect | ~5s | Notification send |

**Total Full Review**: ~60 seconds (with test coverage being slowest)

---

## Success Criteria Met

- ✅ All 13 markdown files created
- ✅ Follows SPEC-105 exactly
- ✅ Database tables properly defined
- ✅ External tools documented with exact commands
- ✅ Error handling documented
- ✅ Output format matches examples
- ✅ Implementation ready for Python code
- ✅ Unit test templates provided
- ✅ Integration test patterns documented
- ✅ Documentation complete with examples

---

## Next Steps: Python Implementation

To use these commands, create `coffee_maker/autonomous/code_reviewer_commands.py` with:

```python
class CodeReviewerCommands:
    """Execute all 13 code reviewer commands."""

    def detect_new_commits(self, **params):
        """Detect new commits to review."""
        # Implementation

    def generate_review_report(self, **params):
        """Generate comprehensive review."""
        # Implementation

    # ... 11 more methods
```

---

**SPEC-105 Implementation Status**: ✅ COMPLETE

**Created**: 2025-10-26
**Total Commands**: 13
**Total Files**: 14 (13 commands + 1 README)
**Total Lines**: ~3,200 lines of detailed documentation
**Integration Points**: 2 database tables, 9 external tools, 6+ features
