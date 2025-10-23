# DoD Verification Scripts

This directory contains the main DoD verification script and supporting utilities.

## Quick Start

### Basic Usage

```bash
# Verify DoD for a priority
python dod_verification.py \
    --priority "US-066" \
    --description "Implement dod-verification skill..." \
    --files-changed "file1.py,file2.py" \
    --report-output "data/dod_reports/"
```

### Run Specific Checks

```bash
# Only automated checks (tests, formatting, security)
python dod_verification.py --priority "US-066" --check-type automated

# Only code quality
python dod_verification.py --priority "US-066" --check-type code_quality

# Only functionality (with Puppeteer)
python dod_verification.py --priority "US-066" --check-type functionality --app-url "http://localhost:8501"
```

## Check Types

- **automated**: Tests, formatting, pre-commit hooks, security scans
- **code_quality**: Docstrings, type hints, code patterns
- **functionality**: Functional requirements testing (Puppeteer for web, CLI for commands)
- **documentation**: Code and user documentation completeness
- **integration**: Backward compatibility, dependencies, config changes
- **all**: Run all checks (default)

## Output

The script generates two files:

1. **JSON Report**: `{priority}_dod_{timestamp}.json` - Machine-readable results
2. **Markdown Report**: `{priority}_dod_{timestamp}.md` - Human-readable report with recommendations

## Example Report

```markdown
# Definition of Done (DoD) Verification Report

**Priority**: US-066
**Date**: 2025-10-19T18:00:00Z
**Overall Status**: ✅ PASS

## Executive Summary

- Criteria Tested: 8
- Checks Passed: 5/5
- Recommendation: READY TO MERGE

## Detailed Results

### Automated Checks ✅
- Tests: 45 passed, 0 failed
- Formatting: PASS (black)
- Security: PASS (bandit)

### Code Quality ✅
- Files Checked: 8
- Total Issues: 0

### Functionality ✅
- Criteria Tested: 5
- Criteria Passed: 5
- Screenshots: 3 captured

### Documentation ✅
- Code Documentation: PASS
- User Documentation: PASS

### Integration ✅
- Backward Compatible: true
- Integration Tests: PASS
- Dependencies: PASS

## Recommendations

✅ All DoD criteria met. Ready to merge.

**Next Steps**:
1. Create pull request
2. Request code review
3. Merge to main branch
```

## Integration with code_developer

```python
from coffee_maker.skills import dod_verification

# After implementation complete
result = dod_verification.verify_priority(
    priority_name="US-066",
    priority_description=description,
    files_changed=["coffee_maker/skills/dod_verifier.py"],
)

if result["status"] == "PASS":
    commit_changes()
    create_pull_request()
    mark_priority_complete()
```

## Exit Codes

- **0**: DoD verification PASSED
- **1**: DoD verification FAILED (see report for details)

## Requirements

- Python 3.11+
- pytest (for test execution)
- black (for formatting checks)
- pre-commit (for hook execution)
- bandit (for security scans, optional)
- Puppeteer MCP (for web testing, optional)
