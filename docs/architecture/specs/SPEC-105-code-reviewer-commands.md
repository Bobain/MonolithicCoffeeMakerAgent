# SPEC-105: Code Reviewer Commands

**Status**: Active
**Created**: 2025-10-26
**Author**: code_developer
**Parent Spec**: SPEC-100
**Related Specs**: SPEC-101 (Foundation), SPEC-103 (Architect Commands)
**Related CFRs**: CFR-000 (Singleton Enforcement), CFR-013 (Git Workflow)
**Dependencies**: SPEC-101 (Foundation), code_reviewer agent operational

## Executive Summary

Implement 13 commands for the code_reviewer agent, covering automated code quality analysis, compliance verification, and review reporting. These commands enable continuous quality assurance by analyzing commits from code_developer and providing actionable feedback to architect.

### Key Objectives

1. **Review Lifecycle** - Poll for commits, generate reviews, notify architect (3 commands)
2. **Code Analysis** - Run style, security, complexity, coverage, type checking (6 commands)
3. **Quality Reporting** - Track issues, score quality, document findings, verify DoD (4 commands)

### Design Principles

- **Automated Quality Assurance**: No manual intervention needed for code analysis
- **Multi-Tool Integration**: Black, flake8, pylint, bandit, radon, mypy, pytest
- **Actionable Feedback**: Each issue includes severity, file location, and recommendation
- **Architect Notification**: Critical findings escalated with evidence
- **Database-Driven**: All results stored in `review_code_review` table

---

## Architecture Overview

### Command Groups

```
Code Reviewer (13 commands)
├── Review Lifecycle (3 commands)
│   ├── detect_new_commits           - Poll for unreviewed commits
│   ├── generate_review_report       - Analyze code and create review
│   └── notify_architect             - Send critical findings
│
├── Code Analysis (6 commands)
│   ├── check_style_compliance       - Run black, flake8, pylint
│   ├── run_security_scan            - Run bandit security scanner
│   ├── analyze_complexity           - Use radon for metrics
│   ├── check_test_coverage          - Verify coverage >90%
│   ├── validate_type_hints          - Check mypy compliance
│   └── check_architecture_compliance - Verify CFRs and patterns
│
└── Quality Reporting (4 commands)
    ├── track_issue_resolution       - Monitor issue fixes
    ├── generate_quality_score       - Calculate 1-10 score
    ├── review_documentation         - Check docstrings
    └── validate_dod_compliance      - Verify acceptance criteria
```

### Database Domain

**Tables Owned (Write Access)**:
- `review_code_review` - Complete review reports with findings
- `review_issue` - Individual code quality issues found

**Tables Read**:
- `review_commit` - Unreviewed commits from code_developer
- `specs_specification` - Technical specs for DoD verification
- `roadmap_priority` - Priority context for reviews
- `notifications` - Review notifications

**Key Fields**:
- `commit_sha` - Git commit hash
- `review_date` - When review was conducted
- `quality_score` - 1-10 scale
- `critical_issues` - Security/architecture violations
- `style_issues` - Code formatting issues
- `approved` - Boolean: ready to merge

---

## Command Group 1: Review Lifecycle (3 Commands)

### Command: code_reviewer.detect_new_commits

**Purpose**: Poll review_commit table for unreviewed commits, identify which are ready for review

**Tables**:
- Read: `review_commit`, `specs_specification`, `roadmap_priority`
- Write: `review_code_review` (empty entry for tracking)

**Input Parameters**:
```yaml
max_age_minutes: integer   # Only review commits <X minutes old (default: 60)
priority_filter: string    # Optional - review only these priorities
batch_size: integer        # Max commits per run (default: 5)
```

**Output**:
```json
{
  "commits_found": 3,
  "commits_ready": 2,
  "commits_skipped": 1,
  "skip_reasons": ["Blocked by previous review"]
}
```

**Success Criteria**:
- ✅ Queries review_commit for unreviewed commits
- ✅ Checks commit age (recent only)
- ✅ Identifies blocking reviews
- ✅ Returns batch-sized result set
- ✅ Creates review_code_review entry with status="pending"

**Algorithm**:
```python
def detect_new_commits(db, params):
    # Get unreviewed commits
    commits = db.query(
        "SELECT * FROM review_commit WHERE reviewed_at IS NULL "
        "AND created_at > datetime('now', '-' || ? || ' minutes') "
        "ORDER BY created_at DESC LIMIT ?",
        [params['max_age_minutes'], params['batch_size']]
    )

    ready_commits = []
    skip_reasons = {}

    for commit in commits:
        # Check if any blocking reviews exist
        blocking_reviews = db.query(
            "SELECT * FROM review_code_review "
            "WHERE commit_sha = ? AND status IN ('reviewing', 'needs_changes')",
            [commit['sha']]
        )

        if blocking_reviews:
            skip_reasons[commit['sha']] = "Blocked by previous review"
        else:
            ready_commits.append(commit)
            # Create review entry
            db.insert("review_code_review", {
                "commit_sha": commit['sha'],
                "review_date": datetime.now(),
                "status": "pending",
                "started_at": datetime.now()
            })

    return {
        "commits_found": len(commits),
        "commits_ready": len(ready_commits),
        "commits_skipped": len(skip_reasons),
        "skip_reasons": skip_reasons
    }
```

---

### Command: code_reviewer.generate_review_report

**Purpose**: Analyze a commit's code and generate comprehensive review report

**Tables**:
- Read: `review_commit`, `specs_specification`
- Write: `review_code_review`, `review_issue`

**Input Parameters**:
```yaml
commit_sha: string         # Required - commit to review
run_all_checks: boolean    # Run full analysis (default: true)
focus_areas: array         # Optional - ["security", "performance", "style"]
```

**Output**:
```json
{
  "review_id": "REV-123",
  "commit_sha": "abc123",
  "quality_score": 7,
  "total_issues": 5,
  "critical_issues": 1,
  "style_issues": 3,
  "coverage_issues": 1,
  "approved": false,
  "analysis_time_seconds": 45.2
}
```

**Success Criteria**:
- ✅ Analyzes commit diff
- ✅ Runs all check commands
- ✅ Calculates quality_score (1-10)
- ✅ Identifies critical issues first
- ✅ Stores all issues in review_issue table
- ✅ Updates review_code_review with findings
- ✅ Completes in <60 seconds

**Algorithm**:
```python
def generate_review_report(db, params):
    commit_sha = params['commit_sha']
    start_time = time.time()

    # Get commit details
    review = db.query_one(
        "SELECT * FROM review_code_review WHERE commit_sha = ?",
        [commit_sha]
    )

    # Run analysis checks
    all_issues = []

    if not params.get('focus_areas') or 'style' in params.get('focus_areas', []):
        style_issues = run_check_style_compliance(commit_sha)
        all_issues.extend(style_issues)

    if not params.get('focus_areas') or 'security' in params.get('focus_areas', []):
        security_issues = run_security_scan(commit_sha)
        all_issues.extend(security_issues)

    # ... other checks

    # Calculate quality score
    critical_count = len([i for i in all_issues if i['severity'] == 'CRITICAL'])
    high_count = len([i for i in all_issues if i['severity'] == 'HIGH'])
    quality_score = max(1, 10 - (critical_count * 2) - (high_count * 0.5))

    # Store issues
    for issue in all_issues:
        db.insert("review_issue", {
            "review_id": review['id'],
            "severity": issue['severity'],
            "category": issue['category'],
            "file_path": issue['file_path'],
            "line_number": issue.get('line_number'),
            "description": issue['description'],
            "recommendation": issue['recommendation']
        })

    # Update review
    db.update("review_code_review", review['id'], {
        "quality_score": int(quality_score),
        "total_issues": len(all_issues),
        "critical_issues": critical_count,
        "status": "completed",
        "completed_at": datetime.now()
    })

    return {
        "review_id": review['id'],
        "commit_sha": commit_sha,
        "quality_score": int(quality_score),
        "total_issues": len(all_issues),
        "critical_issues": critical_count,
        "approved": quality_score >= 7,
        "analysis_time_seconds": time.time() - start_time
    }
```

---

### Command: code_reviewer.notify_architect

**Purpose**: Send critical findings from review to architect for action

**Tables**:
- Read: `review_code_review`, `review_issue`
- Write: `notifications`

**Input Parameters**:
```yaml
review_id: string          # Required - review to report on
severity_threshold: string # Notify on: "CRITICAL", "HIGH", "MEDIUM" (default: "HIGH")
include_evidence: boolean  # Attach code snippets (default: true)
```

**Output**:
```json
{
  "notification_sent": true,
  "notification_id": "NOTIF-456",
  "recipient": "architect",
  "critical_count": 2,
  "high_count": 4,
  "priority": "high"
}
```

**Success Criteria**:
- ✅ Queries review_code_review and review_issue
- ✅ Filters issues by severity threshold
- ✅ Sends notification to architect
- ✅ Includes code snippets if requested
- ✅ Links to commit in GitHub
- ✅ Sets notification priority based on severity

---

## Command Group 2: Code Analysis (6 Commands)

### Command: code_reviewer.check_style_compliance

**Purpose**: Run black, flake8, pylint to check code style and standards

**External Tools**:
```bash
# Black formatter check (PEP 8 compliance)
black --check --diff coffee_maker/ tests/

# Flake8 linter
flake8 coffee_maker/ tests/ --max-line-length=120

# Pylint for code quality
pylint coffee_maker/ --max-line-length=120 --disable=C0114,C0115,C0116
```

**Severity Mapping**:
- `black failure` → HIGH (auto-fixable)
- `flake8 error` → HIGH
- `pylint error` → HIGH
- `pylint warning` → MEDIUM
- `pylint convention` → LOW

**Output**:
```json
{
  "black_compliant": true,
  "flake8_issues": 3,
  "pylint_score": 8.5,
  "total_style_issues": 3,
  "auto_fixable": 2
}
```

---

### Command: code_reviewer.run_security_scan

**Purpose**: Run bandit security scanner to detect vulnerabilities

**External Tools**:
```bash
# Bandit security vulnerability scanner
bandit -r coffee_maker/ -f json -o /tmp/bandit-report.json
```

**Severity Mapping**:
- `bandit HIGH` → CRITICAL (immediate action needed)
- `bandit MEDIUM` → HIGH
- `bandit LOW` → MEDIUM

**Output**:
```json
{
  "vulnerabilities_found": 2,
  "critical_count": 1,
  "high_count": 1,
  "medium_count": 0,
  "scan_duration_seconds": 12.5
}
```

---

### Command: code_reviewer.analyze_complexity

**Purpose**: Use radon to analyze code complexity metrics

**External Tools**:
```bash
# Radon complexity analysis
radon cc coffee_maker/ -a -j
radon mi coffee_maker/ -j

# Check for cognitive complexity
radon cc coffee_maker/ --show-complexity --average
```

**Thresholds**:
- `cyclomatic_complexity > 15` → HIGH issue
- `cognitive_complexity > 10` → MEDIUM issue
- `maintainability_index < 60` → MEDIUM issue

**Output**:
```json
{
  "average_complexity": 3.2,
  "maintainability_index": 82.1,
  "high_complexity_functions": 2,
  "issues_found": 2
}
```

---

### Command: code_reviewer.check_test_coverage

**Purpose**: Run pytest with coverage to verify >90% test coverage

**External Tools**:
```bash
# Pytest with coverage report
pytest --cov=coffee_maker --cov-report=json --cov-report=html tests/

# Parse coverage JSON
coverage json
```

**Thresholds**:
- `coverage < 90%` → HIGH issue
- `coverage < 80%` → CRITICAL issue
- `coverage >= 95%` → EXCELLENT

**Output**:
```json
{
  "total_coverage": 92.3,
  "line_coverage": 91.5,
  "branch_coverage": 88.2,
  "coverage_status": "GOOD",
  "uncovered_lines": 145
}
```

---

### Command: code_reviewer.validate_type_hints

**Purpose**: Run mypy to check type hint compliance

**External Tools**:
```bash
# Mypy static type checker
mypy coffee_maker/ --strict --show-error-codes --json

# Check compliance
mypy coffee_maker/ --strict
```

**Severity Mapping**:
- `error` → HIGH
- `warning` → MEDIUM
- `note` → LOW

**Output**:
```json
{
  "type_errors": 0,
  "type_warnings": 3,
  "compliance_score": 98.5,
  "files_checked": 45
}
```

---

### Command: code_reviewer.check_architecture_compliance

**Purpose**: Verify CFRs and architectural patterns are followed

**Manual Checks**:
- CFR-000: Only one instance of each agent type
- CFR-007: Context budget <30% for agents
- CFR-009: sound=False for background agents
- CFR-013: Working on `roadmap` branch only
- CFR-014: Database tracing for orchestrator
- CFR-015: Database files in `data/` only

**Patterns to Check**:
- AgentRegistry singleton usage
- Mixin composition patterns
- Error handling consistency
- Langfuse decorators present
- Type hints complete
- Docstrings present

**Output**:
```json
{
  "cfr_compliant": true,
  "cfrs_checked": 6,
  "cfrs_passed": 6,
  "pattern_issues": 0,
  "compliance_score": 100
}
```

---

## Command Group 3: Quality Reporting (4 Commands)

### Command: code_reviewer.track_issue_resolution

**Purpose**: Monitor if issues from previous reviews are actually fixed

**Tables**:
- Read: `review_code_review`, `review_issue`
- Write: `review_issue` (update is_resolved)

**Algorithm**:
- Get all issues marked as "needs_changes"
- Check if fixed in current commit
- Mark as resolved or escalate if still present
- Track resolution time (commits between issue and fix)

---

### Command: code_reviewer.generate_quality_score

**Purpose**: Calculate 1-10 quality score based on multiple factors

**Scoring Formula**:
```
base_score = 10

# Style and formatting
- black violations: -0.5 per issue (max -1.0)
- flake8 violations: -0.5 per issue (max -2.0)
- pylint score: -0.1 per point below 8.0

# Security
- bandit vulnerabilities: -2.0 per CRITICAL, -1.0 per HIGH

# Testing
- coverage < 90%: -1.0 per 5% below target
- test count: +0.5 if >90% increase

# Complexity
- high complexity functions: -0.5 per function

# Type safety
- mypy errors: -1.0 per error
- missing type hints: -0.1 per function

# Architecture
- CFR violations: -2.0 per violation
- Pattern violations: -1.0 per pattern

final_score = max(1, min(10, base_score))
```

**Output**:
```json
{
  "quality_score": 7,
  "score_breakdown": {
    "style": 8,
    "security": 10,
    "testing": 6,
    "complexity": 8,
    "type_safety": 7,
    "architecture": 9
  }
}
```

---

### Command: code_reviewer.review_documentation

**Purpose**: Check that docstrings and documentation are present and complete

**Checks**:
- Function docstrings exist (format: Google/PEP 257)
- Class docstrings exist
- Module-level docstrings exist
- README updated if public APIs changed
- Type hints have descriptions

**Tools**:
```bash
# Check docstring presence
pylint --load-plugins pylint.extensions.docparams coffee_maker/
```

---

### Command: code_reviewer.validate_dod_compliance

**Purpose**: Verify acceptance criteria from technical spec are met

**Tables**:
- Read: `specs_specification`, `review_code_review`

**Algorithm**:
1. Get spec linked to commit's priority
2. Extract acceptance criteria
3. Check against review findings:
   - Quality score meets spec minimum
   - All critical features present
   - Tests passing
   - Documentation complete
   - No architectural violations
4. Mark as "dod_met" or "dod_failed"

---

## Implementation Requirements

### Database Schema

**New Tables**:

```sql
CREATE TABLE review_code_review (
    id TEXT PRIMARY KEY,
    commit_sha TEXT NOT NULL,
    review_date DATETIME NOT NULL,
    quality_score INTEGER,
    total_issues INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    style_issues INTEGER DEFAULT 0,
    security_issues INTEGER DEFAULT 0,
    coverage_issues INTEGER DEFAULT 0,
    approved BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'pending',  -- pending, reviewing, completed, needs_changes
    started_at DATETIME,
    completed_at DATETIME,
    analysis_time_seconds REAL,
    FOREIGN KEY (commit_sha) REFERENCES review_commit(sha)
);

CREATE TABLE review_issue (
    id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL,
    severity TEXT NOT NULL,  -- CRITICAL, HIGH, MEDIUM, LOW
    category TEXT NOT NULL,  -- Security, Style, Complexity, Coverage, etc.
    file_path TEXT NOT NULL,
    line_number INTEGER,
    description TEXT NOT NULL,
    recommendation TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_in_commit TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES review_code_review(id),
    FOREIGN KEY (resolved_in_commit) REFERENCES review_commit(sha)
);
```

### Required Tools

**Python Packages**:
- `black` - Code formatting checker
- `flake8` - Style linter
- `pylint` - Code quality analyzer
- `bandit` - Security vulnerability scanner
- `radon` - Code complexity metrics
- `pytest-cov` - Test coverage (already in use)
- `mypy` - Static type checker

### Command File Format

Each command MUST be a markdown file in `.claude/commands/agents/code_reviewer/`:

```markdown
---
command: code_reviewer.{command_name}
agent: code_reviewer
action: {command_name}
tables:
  write: [review_code_review, review_issue]
  read: [review_commit, specs_specification]
required_tools: [tool1, tool2, ...]
estimated_duration_seconds: 30
---

# Command: code_reviewer.{command_name}

## Purpose
[Purpose statement]

## Input Parameters
[YAML format parameters]

## Database Operations
[SQL/database operations]

## External Tools
[Bash commands for external tools]

## Success Criteria
[Acceptance criteria]

## Output Format
[JSON structure]

## Error Handling
[How errors are caught and reported]

## Examples
[Usage examples]
```

---

## Success Criteria

- ✅ All 13 command markdown files created
- ✅ Follow spec exactly for purpose and parameters
- ✅ Database tables properly defined
- ✅ External tools documented with exact commands
- ✅ Error handling documented
- ✅ Output format matches examples
- ✅ Python implementation of commands follows CFRs
- ✅ Unit tests for all 13 commands (>90% coverage)
- ✅ Integration tests verifying database operations
- ✅ Documentation complete with examples

---

## Deliverables

1. **Markdown Command Files** (13 files in `.claude/commands/agents/code_reviewer/`)
   - detect_new_commits.md
   - generate_review_report.md
   - notify_architect.md
   - check_style_compliance.md
   - run_security_scan.md
   - analyze_complexity.md
   - check_test_coverage.md
   - validate_type_hints.md
   - check_architecture_compliance.md
   - track_issue_resolution.md
   - generate_quality_score.md
   - review_documentation.md
   - validate_dod_compliance.md

2. **Database Schema** (`coffee_maker/models/code_reviewer_schema.sql`)
   - review_code_review table
   - review_issue table

3. **Python Implementation** (`coffee_maker/autonomous/code_reviewer_commands.py`)
   - Execute all 13 commands

4. **Tests** (`tests/unit/test_code_reviewer_commands.py`)
   - Unit tests for each command
   - Integration tests with database
   - Mock external tools

---

## Related Specifications

- SPEC-100: Agent Command Framework (parent)
- SPEC-101: Foundation Commands (CI-related baseline)
- SPEC-103: Architect Commands (similar structure)
- SPEC-102: Project Manager Commands (workflow pattern)

---

**Version**: 1.0
**Status**: Ready for Implementation
**Last Updated**: 2025-10-26
