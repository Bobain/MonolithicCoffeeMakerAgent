# Skill: Definition of Done (DoD) Verification

**Name**: `dod-verification`
**Owner**: code_developer (during implementation), project_manager (post-completion)
**Purpose**: Rapid DoD verification for priorities to ensure completeness and quality
**Priority**: CRITICAL - Ensures work meets acceptance criteria before marking complete

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ code_developer: After completing priority implementation (before committing)
- ✅ project_manager: When user requests DoD verification of completed work
- ✅ Before marking priority as "✅ Complete" in ROADMAP
- ✅ Before creating pull request
- ✅ During code review to verify all DoD criteria met

**Example Triggers**:
```python
# code_developer: After implementation
tests_pass = self._run_tests()
if tests_pass:
    dod_report = self._verify_dod(priority_name, priority_description)
    if dod_report["status"] == "PASS":
        self._mark_priority_complete()
        self._create_pull_request()

# project_manager: User requests verification
if user_request == "verify PRIORITY X":
    dod_report = self._verify_dod_post_completion(priority_name)
```

---

## Skill Execution Steps

### Step 1: Extract DoD Criteria from Priority

**Inputs Needed**:
- `$PRIORITY_NAME`: Priority identifier (e.g., "PRIORITY 10")
- `$PRIORITY_DESCRIPTION`: Full priority description from ROADMAP
- `$IMPLEMENTATION_CONTEXT`: What was implemented (files changed, features added)
- `$TEST_RESULTS`: Pytest output (optional, if tests exist)

**Actions**:
1. Parse priority description to extract acceptance criteria
2. Look for explicit DoD markers:
   - "Acceptance Criteria:"
   - "Definition of Done:"
   - Numbered/bulleted lists of requirements
   - "Must have", "Should have", "MUST", "SHALL"
3. Extract implicit requirements:
   - Code changes → Need tests
   - New features → Need documentation
   - UI changes → Need visual verification
   - API changes → Need integration tests
   - Database changes → Need migration scripts

**Output**: Structured DoD checklist
```python
dod_criteria = [
    {
        "criterion": "User can create new coffee recipe",
        "type": "functionality",
        "verification_method": "manual_test",  # or "automated_test", "code_review", "visual"
        "priority": "MUST",  # or "SHOULD", "NICE_TO_HAVE"
        "status": "pending"
    },
    {
        "criterion": "All tests pass",
        "type": "testing",
        "verification_method": "automated_test",
        "priority": "MUST",
        "status": "pending"
    },
    {
        "criterion": "Code follows Black formatting",
        "type": "quality",
        "verification_method": "automated_check",
        "priority": "MUST",
        "status": "pending"
    }
]
```

### Step 2: Automated Verification Checks

**Run Automated Checks** (where applicable):

**1. Code Quality Checks**
```bash
# Formatting
black --check coffee_maker/ tests/
autoflake --check coffee_maker/ tests/

# Linting (if configured)
pylint coffee_maker/ --fail-under=8.0

# Type checking (if configured)
mypy coffee_maker/ --strict
```

**2. Test Coverage**
```bash
# Run all tests
pytest tests/ -v --tb=short

# Check coverage (if configured)
pytest --cov=coffee_maker --cov-report=term-missing --cov-fail-under=80
```

**3. Security Checks** (if applicable)
```bash
# Check for security issues
bandit -r coffee_maker/ -ll

# Check dependencies for vulnerabilities
safety check
```

**4. Pre-commit Hooks**
```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

**Output**: Automated check results
```python
automated_results = {
    "formatting": {"status": "PASS", "details": "All files formatted with Black"},
    "tests": {"status": "PASS", "details": "23/23 tests passing, 0 failed"},
    "coverage": {"status": "PASS", "details": "Coverage: 87% (threshold: 80%)"},
    "pre_commit": {"status": "PASS", "details": "All hooks passed"},
    "security": {"status": "PASS", "details": "No security issues found"}
}
```

### Step 3: Code Review Checks

**Manual Code Review** (systematically check):

**1. Files Changed Analysis**
```python
# Get list of changed files
changed_files = git diff --name-only HEAD~1

# For each changed file:
for file in changed_files:
    # Check if file needs:
    - Tests? (coffee_maker/*.py → tests/unit/test_*.py or tests/integration/test_*.py)
    - Documentation? (public APIs → docstrings, READMEs)
    - Type hints? (function signatures)
    - Error handling? (try/except blocks, validation)
```

**2. Code Quality Patterns**
Check for:
- ✅ Type hints on public functions
- ✅ Docstrings on classes and public methods
- ✅ Proper error handling (try/except with specific exceptions)
- ✅ No hardcoded values (use constants or config)
- ✅ No commented-out code (unless with explanation)
- ✅ No `print()` statements (use logging instead)
- ✅ Proper logging (logger = logging.getLogger(__name__))

**3. Architecture Patterns**
Verify adherence to project standards:
- ✅ Singleton pattern used correctly (if applicable)
- ✅ Mixins pattern followed (if adding to daemon)
- ✅ Prompt management used (no hardcoded prompts)
- ✅ Langfuse observability decorators added (if applicable)

**Output**: Code review findings
```python
code_review_results = {
    "files_needing_tests": [],  # Empty if all files have tests
    "files_missing_docstrings": [],
    "files_missing_type_hints": [],
    "hardcoded_values_found": [],
    "architecture_violations": [],
    "overall_status": "PASS"  # or "FAIL" if issues found
}
```

### Step 4: Functional Verification

**Verify Functional Requirements**:

**For Web Features** (use Puppeteer if available):
```python
# Navigate to application
puppeteer_navigate("http://localhost:8501")

# Take baseline screenshot
puppeteer_screenshot("baseline.png")

# Test each acceptance criterion
for criterion in functional_criteria:
    # Example: "User can create new coffee recipe"

    # 1. Click "New Recipe" button
    puppeteer_click("button[data-testid='new-recipe']")

    # 2. Fill form
    puppeteer_fill("input[name='recipe-name']", "Test Recipe")
    puppeteer_fill("input[name='coffee-amount']", "20")

    # 3. Submit
    puppeteer_click("button[type='submit']")

    # 4. Verify success
    success_message = puppeteer_evaluate("document.querySelector('.success-message').textContent")

    # 5. Screenshot evidence
    puppeteer_screenshot(f"{criterion['id']}_success.png")

    # 6. Check console errors
    console_errors = puppeteer_evaluate("console.errors")

    # Mark criterion as PASS/FAIL
    criterion["status"] = "PASS" if success_message and not console_errors else "FAIL"
```

**For CLI Features**:
```bash
# Test CLI commands
poetry run coffee-maker create-recipe "Test Recipe" --coffee=20 --water=200

# Verify output
# Expected: "Recipe 'Test Recipe' created successfully"

# Verify side effects (database, files created, etc.)
```

**For Library/API Features**:
```python
# Test API endpoints or library functions
from coffee_maker.some_module import new_function

result = new_function(param1="value1")
assert result == expected_value, "Function does not meet acceptance criteria"
```

**Output**: Functional verification results
```python
functional_results = {
    "criteria_tested": 5,
    "criteria_passed": 5,
    "criteria_failed": 0,
    "screenshots": ["baseline.png", "create_recipe_success.png"],
    "console_errors": [],
    "overall_status": "PASS"
}
```

### Step 5: Documentation Verification

**Check Documentation Requirements**:

**1. Code Documentation**
- ✅ All new public classes have docstrings
- ✅ All new public functions have docstrings
- ✅ Docstrings follow Google style (Args, Returns, Raises)
- ✅ Complex algorithms have inline comments

**2. User Documentation** (if user-facing changes)
- ✅ README updated (if CLI commands changed)
- ✅ Tutorial/guide created (if new feature)
- ✅ CHANGELOG updated (if applicable)

**3. Technical Documentation** (if architectural changes)
- ✅ ADR created (if architectural decision made)
- ✅ Technical spec updated (if implementation deviated)
- ✅ ROADMAP updated with status

**Output**: Documentation verification results
```python
documentation_results = {
    "code_docstrings": "PASS",
    "user_documentation": "PASS",
    "technical_documentation": "PASS",
    "missing_docs": [],
    "overall_status": "PASS"
}
```

### Step 6: Integration Checks

**Verify Integration with Existing System**:

**1. Backward Compatibility**
```python
# Check if changes break existing APIs
# Run integration tests
pytest tests/integration/ -v

# Check if existing features still work
# (regression testing)
```

**2. Database Migrations** (if applicable)
```bash
# If database changes:
# - Migration script created?
# - Migration tested (up and down)?
# - No data loss?
```

**3. Dependencies** (if new dependencies added)
```bash
# Verify dependencies properly added
poetry check

# Check for conflicts
poetry show --tree

# Verify lock file updated
git diff poetry.lock
```

**4. Configuration Changes** (if applicable)
```python
# If .claude/ or config files changed:
# - Backward compatible?
# - Documented?
# - Default values reasonable?
```

**Output**: Integration verification results
```python
integration_results = {
    "backward_compatible": True,
    "integration_tests": "PASS",
    "migrations": "N/A",  # or "PASS" if applicable
    "dependencies": "PASS",
    "config_changes": "PASS",
    "overall_status": "PASS"
}
```

### Step 7: Generate DoD Report

**Compile All Results into Comprehensive Report**:

```markdown
# Definition of Done (DoD) Verification Report

**Priority**: $PRIORITY_NAME
**Date**: $CURRENT_DATE
**Verified By**: code_developer / project_manager
**Overall Status**: ✅ PASS / ❌ FAIL

---

## Executive Summary

- ✅ All automated checks passed
- ✅ Code review: No issues found
- ✅ Functional verification: 5/5 criteria met
- ✅ Documentation: Complete
- ✅ Integration: No breaking changes

**Recommendation**: READY TO MERGE ✅

---

## DoD Criteria Checklist

### MUST-HAVE Criteria (5/5 passed)

1. ✅ **User can create new coffee recipe**
   - Method: Manual test with Puppeteer
   - Evidence: create_recipe_success.png
   - Status: PASS

2. ✅ **All tests pass**
   - Method: Automated (pytest)
   - Result: 23/23 tests passing
   - Coverage: 87%
   - Status: PASS

3. ✅ **Code follows Black formatting**
   - Method: Automated (black --check)
   - Status: PASS

4. ✅ **No console errors in UI**
   - Method: Puppeteer console check
   - Errors found: 0
   - Status: PASS

5. ✅ **Documentation updated**
   - Method: Manual review
   - Files updated: README.md, coffee_maker/recipes.py (docstrings)
   - Status: PASS

### SHOULD-HAVE Criteria (2/2 passed)

6. ✅ **Recipe validation works**
   - Method: Automated test
   - Test: test_recipe_validation
   - Status: PASS

7. ✅ **Error messages user-friendly**
   - Method: Manual verification
   - Status: PASS

---

## Automated Checks

### Code Quality ✅
- **Black formatting**: PASS - All files formatted
- **Autoflake**: PASS - No unused imports
- **Pre-commit hooks**: PASS - All hooks passed

### Testing ✅
- **Unit tests**: 23/23 passing (0 failed)
- **Integration tests**: 5/5 passing
- **Test coverage**: 87% (threshold: 80%) ✅
- **Test runtime**: 2.3 seconds

### Security ✅
- **Bandit scan**: PASS - No security issues
- **Dependency check**: PASS - No vulnerabilities

---

## Code Review Findings

### Files Changed (3 files)
1. `coffee_maker/recipes.py` - ✅ Has tests, docstrings, type hints
2. `tests/unit/test_recipes.py` - ✅ Comprehensive test coverage
3. `README.md` - ✅ Documentation updated

### Code Quality Patterns ✅
- ✅ Type hints: Present on all public functions
- ✅ Docstrings: Complete (Google style)
- ✅ Error handling: Proper try/except blocks
- ✅ Logging: Using logger (not print)
- ✅ No hardcoded values
- ✅ No commented-out code

### Architecture Compliance ✅
- ✅ Follows project patterns
- ✅ No prompt hardcoding (uses PromptLoader)
- ✅ Singleton pattern used correctly (N/A for this priority)

---

## Functional Verification

### Test Environment
- **URL**: http://localhost:8501
- **Browser**: Chrome (Puppeteer)
- **Date**: $CURRENT_DATE

### Acceptance Criteria Testing

**Criterion 1: User can create new coffee recipe** ✅
- Steps:
  1. Navigate to /recipes
  2. Click "New Recipe" button
  3. Fill form: Name="Test Recipe", Coffee=20g, Water=200ml
  4. Click "Create"
- Result: SUCCESS ✅
- Evidence: create_recipe_success.png
- Console errors: 0

**Criterion 2: Recipe appears in list** ✅
- Steps:
  1. After creating recipe
  2. Navigate to /recipes
  3. Verify "Test Recipe" appears
- Result: SUCCESS ✅
- Evidence: recipe_list.png

**Criterion 3: Validation prevents invalid recipes** ✅
- Steps:
  1. Try creating recipe with negative coffee amount
  2. Verify error message shown
- Result: SUCCESS ✅
- Error message: "Coffee amount must be positive"

### Screenshots
- baseline.png
- create_recipe_success.png
- recipe_list.png
- validation_error.png

---

## Documentation Review

### Code Documentation ✅
- ✅ `coffee_maker/recipes.py` - All functions have docstrings
- ✅ Docstrings follow Google style
- ✅ Complex logic has inline comments

### User Documentation ✅
- ✅ README.md updated with new recipe creation feature
- ✅ Example usage provided

### Technical Documentation ✅
- ✅ ROADMAP.md status updated to "✅ Complete"
- ✅ No ADR needed (simple feature)

---

## Integration Verification

### Backward Compatibility ✅
- ✅ Existing recipe functionality unchanged
- ✅ No breaking API changes
- ✅ Migration not needed (no database changes)

### Dependencies ✅
- ✅ No new dependencies added
- ✅ poetry.lock unchanged

### Configuration ✅
- ✅ No configuration changes

---

## Risk Analysis

### Risks Identified: 0

No risks identified. Implementation is straightforward and well-tested.

---

## Recommendations

### Immediate Action
✅ **READY TO MERGE** - All DoD criteria met

### Before Merging
1. ✅ Run `pytest` one final time → PASSED
2. ✅ Run `pre-commit run --all-files` → PASSED
3. ✅ Create pull request with this DoD report attached

### Post-Merge
1. Monitor for user feedback on new recipe creation feature
2. Consider adding recipe editing feature in next priority

---

## Conclusion

**DoD Status**: ✅ **PASS**

All MUST-HAVE criteria (5/5) met ✅
All SHOULD-HAVE criteria (2/2) met ✅
All automated checks passed ✅
Code quality excellent ✅
Documentation complete ✅
No integration risks ✅

**Verified By**: code_developer
**Date**: $CURRENT_DATE
**Recommendation**: Approve and merge to main branch

---

**Next Steps**:
1. Mark PRIORITY $PRIORITY_NAME as "✅ Complete" in ROADMAP
2. Create pull request with title "Implement $PRIORITY_NAME"
3. Attach this DoD report to PR description
4. Push to remote branch
```

---

## Integration with code_developer Agent

### During Implementation (code_developer)

```python
# coffee_maker/autonomous/daemon_implementation.py

def _verify_dod_before_commit(self, priority_name: str, priority_description: str) -> dict:
    """Verify DoD using skill before committing."""
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames
    from datetime import datetime

    # Get implementation context
    files_changed = self._get_changed_files()
    test_results = self._run_tests()

    skill = load_skill(SkillNames.DOD_VERIFICATION, {
        "PRIORITY_NAME": priority_name,
        "PRIORITY_DESCRIPTION": priority_description,
        "IMPLEMENTATION_CONTEXT": ", ".join(files_changed),
        "TEST_RESULTS": test_results,
        "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
    })

    # Execute with LLM
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    dod_report = result.content if result and result.success else "DoD verification failed"

    # Save report
    report_path = Path(f"data/dod_reports/{priority_name.replace(' ', '_')}_dod_{datetime.now().strftime('%Y%m%d')}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(dod_report, encoding="utf-8")

    # Parse result
    dod_status = "PASS" if "✅ PASS" in dod_report else "FAIL"

    return {
        "status": dod_status,
        "report": dod_report,
        "report_path": str(report_path)
    }

def _implement_priority_with_dod(self, priority_name: str):
    """Implement priority with DoD verification."""
    # ... implementation code ...

    # After implementation, verify DoD
    dod_result = self._verify_dod_before_commit(priority_name, priority_description)

    if dod_result["status"] == "PASS":
        logger.info(f"✅ DoD verification PASSED for {priority_name}")
        self._commit_changes(priority_name, dod_result["report_path"])
        self._create_pull_request(priority_name, dod_result["report"])
        self._mark_priority_complete(priority_name)
    else:
        logger.error(f"❌ DoD verification FAILED for {priority_name}")
        logger.error(f"See report: {dod_result['report_path']}")
        # Do NOT commit, fix issues first
        self._notify_user_dod_failed(priority_name, dod_result["report"])
```

### Post-Completion Verification (project_manager)

```python
# coffee_maker/autonomous/agents/project_manager_agent.py

def _verify_completed_priority(self, priority_name: str) -> str:
    """Verify completed priority using DoD skill."""
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames
    from datetime import datetime

    # Get priority details from ROADMAP
    priority = self._get_priority_from_roadmap(priority_name)

    skill = load_skill(SkillNames.DOD_VERIFICATION, {
        "PRIORITY_NAME": priority_name,
        "PRIORITY_DESCRIPTION": priority["description"],
        "IMPLEMENTATION_CONTEXT": self._get_implementation_context(priority_name),
        "TEST_RESULTS": self._get_test_results(),
        "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
    })

    # Execute with LLM
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    return result.content if result and result.success else "DoD verification failed"
```

---

## Skill Checklist (Agents Must Complete)

Before marking priority as complete:

- [ ] ✅ Load dod-verification skill with priority context
- [ ] ✅ Run all automated checks (tests, formatting, linting)
- [ ] ✅ Perform code review checks
- [ ] ✅ Verify functional requirements (Puppeteer for web, CLI tests for CLI)
- [ ] ✅ Check documentation completeness
- [ ] ✅ Verify integration/backward compatibility
- [ ] ✅ Generate comprehensive DoD report
- [ ] ✅ If PASS: Commit, create PR, mark complete
- [ ] ✅ If FAIL: Fix issues, re-run verification
- [ ] ✅ Save DoD report to data/dod_reports/

**Failure to verify DoD = Incomplete work, potential bugs, unhappy users**

---

## Success Metrics

**Time Savings**:
- **Before**: 20-40 minutes manual DoD verification
- **After**: 3-5 minutes with skill-generated report
- **Savings**: 15-35 minutes per priority

**Quality Improvements**:
- **Comprehensive**: Never miss DoD criteria
- **Consistent**: Same checks every time
- **Documented**: Evidence-based reports
- **Automated**: Reduces human error

**Measurement**:
- Track time from "implementation complete" to "DoD verified"
- Track number of priorities that fail DoD on first attempt
- Track number of bugs found in production (should decrease)

---

## Related Skills

- **test-failure-analysis**: code_developer debugs test issues before DoD verification
- **roadmap-health-check**: project_manager monitors priority health
- **architecture-reuse-check**: Architect ensures quality specs for complex priorities

---

**Remember**: DoD verification = Quality gate! Never skip it! 🎯

**code_developer's Mantra**: "Not done until DoD says PASS!"
**project_manager's Mantra**: "Trust, but verify with DoD skill!"
