# Skill: Test Failure Analysis

**Name**: `test-failure-analysis`
**Owner**: code_developer agent
**Purpose**: Rapidly analyze test failures, identify root causes, and suggest fixes
**Priority**: HIGH - Reduces debugging time from 30-60 min to 5-10 min

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ After `pytest` fails during implementation
- ✅ When CI/CD tests fail on GitHub
- ✅ When pre-commit hooks report test failures
- ✅ During debugging sessions when tests are red

**Example Trigger**:
```python
# In code_developer_agent.py
test_result = self._run_tests()
if not test_result:
    # Use test-failure-analysis skill
    analysis = self._analyze_test_failures()
```

---

## Skill Execution Steps

### Step 1: Capture Test Output

**Inputs Needed**:
- `$TEST_OUTPUT`: Full pytest output (stdout + stderr)
- `$FILES_CHANGED`: List of files changed in current implementation
- `$PRIORITY_NAME`: Current priority being implemented

**Actions**:
1. Parse pytest output to extract:
   - Failed test names
   - Error messages
   - Tracebacks
   - Line numbers
   - Assertion failures

**Output**: Structured failure data

```python
failures = {
    "test_user_authentication": {
        "file": "tests/unit/test_auth.py",
        "line": 45,
        "error_type": "AssertionError",
        "message": "assert None is not None",
        "traceback": "..."
    }
}
```

### Step 2: Categorize Failures

**Common Failure Categories**:

1. **Import Errors** - Missing dependencies, circular imports
   - Pattern: `ImportError`, `ModuleNotFoundError`
   - Cause: Missing files, dependency issues
   - Fix: Add imports, install dependencies, fix circular deps

2. **Assertion Failures** - Logic errors, incorrect assumptions
   - Pattern: `AssertionError`, `assert X == Y`
   - Cause: Wrong implementation logic
   - Fix: Correct the implementation

3. **Attribute Errors** - Missing methods/properties
   - Pattern: `AttributeError: 'X' has no attribute 'Y'`
   - Cause: Incomplete implementation, typos
   - Fix: Add missing methods/properties

4. **Type Errors** - Wrong types passed to functions
   - Pattern: `TypeError: expected X, got Y`
   - Cause: Type mismatch
   - Fix: Correct types or add type conversion

5. **Fixture Errors** - pytest fixture issues
   - Pattern: `fixture 'X' not found`
   - Cause: Missing fixtures, scope issues
   - Fix: Add fixtures or fix scope

6. **Mock Errors** - Mocking/patching issues
   - Pattern: `AttributeError` in `mock.patch`
   - Cause: Incorrect mock paths, missing attributes
   - Fix: Correct mock paths

**Decision Tree**:
```
Test failure
    │
    ├─ ImportError? → Check imports, dependencies
    ├─ AssertionError? → Check logic, implementation
    ├─ AttributeError? → Check implementation completeness
    ├─ TypeError? → Check types
    ├─ Fixture error? → Check test setup
    └─ Mock error? → Check mock configuration
```

### Step 3: Correlate with Recent Changes

**Analysis**:
- Compare failed tests with `$FILES_CHANGED`
- Identify which changes likely caused each failure
- Prioritize failures by relevance to current work

**Example**:
```
File changed: coffee_maker/auth/login.py
Failed test: tests/unit/test_auth.py::test_login_success

Correlation: HIGH (same module)
Likely cause: Recent changes to login() function
```

### Step 4: Generate Fix Recommendations

**For Each Failure**:
1. **Root Cause**: What went wrong?
2. **Fix**: What needs to change?
3. **Code Snippet**: Exact code to fix the issue
4. **Priority**: CRITICAL / HIGH / MEDIUM (based on correlation)

**Output Format**:
```markdown
## Test Failure Analysis

### Summary
- Total Failures: 5
- CRITICAL (blocking current work): 3
- HIGH (related to changes): 1
- MEDIUM (pre-existing): 1

### CRITICAL Failures

#### 1. test_login_success (tests/unit/test_auth.py:45)

**Error**: AssertionError - assert None is not None

**Root Cause**:
The `login()` function returns `None` instead of a User object when credentials are valid.

**File**: coffee_maker/auth/login.py:23

**Fix**:
```python
# BEFORE (incorrect)
def login(username, password):
    if authenticate(username, password):
        return None  # ❌ Should return user

# AFTER (correct)
def login(username, password):
    if authenticate(username, password):
        return User.get(username)  # ✅ Return user object
```

**Priority**: CRITICAL - Blocking PRIORITY $PRIORITY_NAME

**Action**: Fix immediately before proceeding
```

### Step 5: Provide Quick-Fix vs Deep-Fix Options

**Quick Fix** (5 minutes):
- Minimal change to make tests pass
- May not be optimal long-term
- Good for unblocking work

**Deep Fix** (20-30 minutes):
- Proper solution addressing root cause
- Better long-term quality
- Recommended when time permits

**Example**:
```markdown
### Fix Options for test_login_success

**Quick Fix** (5 min):
```python
# Just make it return something
return User.get(username) or User()
```
✅ Tests pass
❌ May mask issues

**Deep Fix** (20 min):
```python
# Proper error handling
def login(username, password):
    if not authenticate(username, password):
        raise AuthenticationError("Invalid credentials")

    user = User.get(username)
    if not user:
        raise UserNotFoundError(f"User {username} not found")

    return user
```
✅ Tests pass
✅ Proper error handling
✅ Better long-term quality
```

### Step 6: Estimate Fix Time

**Time Estimation**:
- CRITICAL failures: Estimate time to fix each
- Prioritize by (correlation × impact / time)
- Suggest optimal fix order

**Output**:
```markdown
## Recommended Fix Order

1. **test_login_success** (CRITICAL)
   - Estimated time: 5 minutes (quick fix) / 20 minutes (deep fix)
   - Impact: Blocks current priority
   - Correlation: HIGH (recent changes)

2. **test_logout** (HIGH)
   - Estimated time: 10 minutes
   - Impact: Related functionality
   - Correlation: MEDIUM

3. **test_password_reset** (MEDIUM)
   - Estimated time: 30 minutes
   - Impact: Pre-existing issue
   - Correlation: LOW
   - Recommendation: Defer to separate PR
```

---

## Integration with code_developer Agent

### When Tests Fail

```python
# coffee_maker/autonomous/agents/code_developer_agent.py

def _run_tests(self) -> bool:
    """Run pytest test suite."""
    import subprocess

    result = subprocess.run(
        ["pytest", "tests/unit/", "--ignore=tests/unit/_deprecated", "-v"],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode == 0:
        logger.info("✅ Tests passed")
        return True
    else:
        logger.error(f"❌ Tests failed")

        # Use test-failure-analysis skill
        analysis = self._analyze_test_failures(
            test_output=result.stdout + "\n" + result.stderr,
            files_changed=self._get_changed_files(),
            priority_name=self._current_priority_name
        )

        # Log analysis
        logger.info(f"📊 Test Failure Analysis:\n{analysis}")

        # Save analysis for review
        self._save_test_analysis(analysis)

        return False

def _analyze_test_failures(self, test_output: str, files_changed: list, priority_name: str) -> str:
    """Analyze test failures using skill."""
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

    skill = load_skill(SkillNames.TEST_FAILURE_ANALYSIS, {
        "TEST_OUTPUT": test_output,
        "FILES_CHANGED": ", ".join(files_changed),
        "PRIORITY_NAME": priority_name,
    })

    # Execute with LLM
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    return result.content if result and result.success else "Analysis failed"
```

---

## Skill Checklist (code_developer Must Complete)

When tests fail:

- [ ] ✅ Capture full test output (stdout + stderr)
- [ ] ✅ Identify files changed in current implementation
- [ ] ✅ Load test-failure-analysis skill
- [ ] ✅ Execute skill with captured data
- [ ] ✅ Review generated analysis
- [ ] ✅ Categorize failures (CRITICAL/HIGH/MEDIUM)
- [ ] ✅ Choose fix strategy (quick vs deep)
- [ ] ✅ Estimate fix time
- [ ] ✅ Follow recommended fix order
- [ ] ✅ Rerun tests after fixes
- [ ] ✅ Save analysis for learning

**Failure to use skill when tests fail = Wasted debugging time (30-60 min vs 5-10 min)**

---

## Success Metrics

**Time Savings**:
- **Before**: 30-60 minutes to debug test failures manually
- **After**: 5-10 minutes with skill-guided analysis
- **Savings**: 20-50 minutes per test failure session

**Quality Improvements**:
- **Faster root cause identification**: 80% faster
- **Better fix prioritization**: Fix blocking issues first
- **Learning**: Build institutional knowledge about common failure patterns

**Measurement**:
- Track time from "tests fail" to "tests pass"
- Track number of test failures per implementation
- Track fix quality (does it stay fixed?)

---

## Example Output

```markdown
# Test Failure Analysis Report
**Priority**: PRIORITY 10 - User authentication
**Files Changed**: coffee_maker/auth/login.py, tests/unit/test_auth.py
**Total Failures**: 3

## Summary
- CRITICAL: 2 failures (blocking current work)
- MEDIUM: 1 failure (pre-existing)
- Estimated fix time: 15-25 minutes

## CRITICAL Failures

### 1. test_login_success (tests/unit/test_auth.py:45)
**Error**: AssertionError - assert None is not None
**Root Cause**: login() returns None instead of User object
**Fix**: Return User.get(username) after successful authentication
**File**: coffee_maker/auth/login.py:23
**Time**: 5 min (quick) / 20 min (deep)
**Priority**: 1 (highest)

### 2. test_login_invalid_password (tests/unit/test_auth.py:52)
**Error**: AttributeError - 'NoneType' object has no attribute 'username'
**Root Cause**: Same as #1 - login() returns None
**Fix**: Same as #1
**Time**: Included in #1
**Priority**: 1 (will be fixed with #1)

## MEDIUM Failures

### 3. test_password_complexity (tests/unit/test_auth.py:89)
**Error**: AssertionError - Expected "weak", got "strong"
**Root Cause**: Password complexity algorithm changed in v2.0
**Fix**: Update test expectations or revert algorithm
**File**: tests/unit/test_auth.py:89
**Time**: 10 minutes
**Priority**: 3 (defer to separate PR)
**Note**: Pre-existing issue, not related to current changes

## Recommended Fix Order

1. Fix #1 and #2 together (same root cause): 5-20 min
2. Defer #3 to separate PR (not blocking)

**Total time to unblock**: 5-20 minutes
**Total time if fixing all**: 15-30 minutes

## Quick Fix Code

```python
# coffee_maker/auth/login.py:23
def login(username, password):
    if authenticate(username, password):
        return User.get(username)  # Add this line
    raise AuthenticationError("Invalid credentials")
```
```

---

## Related Skills

- **architecture-reuse-check**: Check existing test utilities before writing new ones
- **proactive-refactoring-analysis**: Identify test code duplication and complexity
- **commit-review**: Architect reviews test changes for quality

---

**Remember**: Fast test failure analysis = Faster implementation = Higher velocity! 🚀

**code_developer's Mantra**: "Tests failed? Load test-failure-analysis skill first, debug manually second!"
