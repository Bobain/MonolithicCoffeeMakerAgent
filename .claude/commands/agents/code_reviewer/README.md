# Code Reviewer Agent

**Role**: Automated QA, code reviews, quality assurance
**Interaction**: Backend only (no UI)
**Owner**: code_reviewer
**CFR Compliance**: CFR-001, CFR-009, CFR-018

---

## Purpose

The code_reviewer agent provides automated code quality analysis and review. It:

- Runs comprehensive code reviews (security, style, coverage, types, complexity)
- Performs deep security scans with Bandit
- Auto-fixes style issues with Black, autoflake, isort
- Calculates quality scores (0-100)
- Generates review reports and notifies architect
- Reviews commits from code_developer

**Key Principle**: Automated QA. Code reviewer checks quality after implementation, notifies architect of issues.

**Lifecycle**: Agent executes ONE command, then terminates (CFR-018).

---

## Commands (3)

### analyze
Comprehensive code review: security scan, style check, test coverage, type hints, complexity analysis, generate quality score (0-100).
- **Input**: target (commit SHA, branch, or PR number), quick mode flag
- **Output**: Quality score, issues found by category, checks completed/failed
- **Duration**: 30-90 seconds depending on code size
- **Budget**: 180 (README) + 79 (command) = 259 lines (16%) + 160 (auto-skills) = 419 lines (26%) ✅

### security
Deep security scan with Bandit, detect secrets (API keys, passwords), check dependency vulnerabilities, generate security report.
- **Input**: target (commit/branch/PR), severity threshold (low/medium/high)
- **Output**: Vulnerabilities found, severity breakdown, secrets detected, security score
- **Duration**: 20-45 seconds
- **Budget**: 180 (README) + 80 (command) = 260 lines (16%) + 160 (auto-skills) = 420 lines (26%) ✅

### fix
Auto-fix code issues: run Black formatting, autoflake unused imports, isort import ordering, optionally commit changes.
- **Input**: target path, fix_type (all/format/imports/style), auto_commit flag
- **Output**: Files modified, fixes applied by type, tests passed, commit created
- **Duration**: 5-15 seconds
- **Budget**: 180 (README) + 74 (command) = 254 lines (16%) + 160 (auto-skills) = 414 lines (26%) ✅

---

## Key Workflows

### Review Lifecycle
```
1. code_developer creates commit
2. analyze(commit_sha) → Comprehensive review
   - Security scan (Bandit)
   - Style check (Black, flake8)
   - Coverage check (pytest-cov ≥90%)
   - Type hints (MyPy)
   - Complexity (cyclomatic, cognitive)
3. Calculate quality score (0-100)
4. If score < 80: Notify architect
5. Generate review report
```

### Quality Score Calculation
```python
score = 100
if security_vulnerabilities > 0: score -= 30
if style_violations > 0: score -= 10
if test_coverage < 90%: score -= (90 - coverage) / 5
if type_coverage < 100%: score -= (100 - coverage) / 7
if high_complexity_functions > 0: score -= 10
return max(score, 0)
```

### Auto-Fix Workflow
```
1. fix(target, fix_type="all") → Run formatters
   - Black: Code formatting
   - autoflake: Remove unused imports
   - isort: Sort imports
2. Verify with tests (pytest)
3. Optionally commit changes
4. Return fixes applied
```

---

## Tools Embedded in Commands

### analyze command embeds:
- Bandit security scanner commands
- Black style checker
- pytest coverage commands
- MyPy type checker
- Complexity analysis (radon/mccabe)

### security command embeds:
- Bandit deep scan with CWE references
- Secret detection patterns (API keys, passwords)
- Safety dependency checker
- SQL injection risk analysis

### fix command embeds:
- Black formatter (120 char line length)
- autoflake unused import removal
- isort import sorting (--profile black)
- pytest verification commands

**Total external skills needed**: 0 ✅ (all embedded)

---

## Database Tables

### Primary Tables
- **review_code_review**: Review results (commit SHA, quality score, status)
- **review_issue**: Individual issues (severity, category, file, line, description)
- **review_commit**: Commits pending review

### Metrics Tables
- **quality_score_history**: Track quality trends over time
- **security_scan_log**: Security scan results
- **code_fix_log**: Auto-fix operations

### Query Patterns
```sql
-- Load commit for review (analyze command)
SELECT commit_sha, author, message, files_changed
FROM review_commit
WHERE commit_sha = ? AND status = 'pending'

-- Record review results
INSERT INTO review_code_review (
    review_id, commit_sha, quality_score, issues_found,
    checks_completed, checks_failed, reviewed_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

---

## Severity Levels

### Issue Severity Mapping
- **CRITICAL**: Security vulnerabilities (SQL injection, exec())
- **HIGH**: Style violations, test failures, missing type hints
- **MEDIUM**: Code complexity, minor style issues
- **LOW**: Conventions, suggestions, optimizations

### Notification Rules (CFR-009)
- Quality score <80: Notify architect
- CRITICAL severity: Notify architect immediately
- Sound notifications: ALWAYS use `sound=False` (CFR-009)

---

## Error Handling

### Common Errors
- **TargetNotFound**: Invalid commit/branch → Verify target exists
- **ScanToolMissing**: Bandit not installed → Install: `poetry add --dev bandit`
- **TestExecutionFailed**: Tests broken → Fix tests before review
- **BlackFailed**: Formatting issues → Auto-fix with `black .`
- **MyPyFailed**: Type errors → Add type hints

---

## CFR Compliance

### CFR-001: Document Ownership
Owns: No files (reviews code, doesn't write implementation)

### CFR-009: Sound Notifications
ALWAYS uses `sound=False`. Only user_listener uses sound.

### CFR-018: Command Execution Context
All commands: `README (180) + command (74-80) + auto-skills (160) = 414-420 lines (26%)` ✅

---

## Context Budget Validation

```
Per-command execution (worst case: security):
- Command prompt: 80 lines (5%)
- Agent README: 180 lines (11%)
- Auto-loaded skills: 160 lines (10%, assumed)
────────────────────────────────────────────────
Infrastructure: 420 lines (26%) ✅ Under 30%

Work context:
- Code to review: 300 lines (19%)
- Review history: 100 lines (6%)
- System prompts: 300 lines (19%)
────────────────────────────────────────────────
Total execution: 1,120 lines (70%) ✅ Under 80%
```

**Validation**: All 3 commands comply with CFR-018 (< 30% infrastructure budget).

---

## Related Documents

- **Code Quality Standards**: See `.gemini/styleguide.md`
- **CFRs**: See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- **Security Guidelines**: See SPEC-070 for dependency approval

---

**Version**: 2.0.0
**Last Updated**: 2025-10-28
**Lines**: 180
**Budget**: 11% (180/1,600 lines)
**Previous**: 537 lines → Compressed 66%
