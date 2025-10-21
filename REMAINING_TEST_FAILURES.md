# Remaining Test Failures Analysis (37 failures remaining)

## Summary
- **Total tests**: 1585
- **Passing**: 1548 (97.7%)
- **Failing**: 37 (2.3%)
- **Progress**: Fixed 7 tests this session (from 44 to 37)

## Test Failures by Category

### 1. AutoPickerLLMRefactored Missing Methods (9 failures)

**Files**: `tests/unit/test_auto_picker_llm_refactored.py`

**Missing Methods**:
- `_estimate_tokens(input_data, model_name)` - Estimate token count for input
- `enable_context_fallback` - Property to enable/disable context length fallback
- `_check_context_length()` - Check if input exceeds context length

**Root Cause**: Refactored class missing these methods that are called in tests

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/langfuse_observe/auto_picker_llm_refactored.py`

**Implementation Path**:
1. Add `_estimate_tokens()` method (similar to one in `scheduled_llm.py` line ~50)
2. Add `enable_context_fallback` property to `__init__` parameters
3. Add `_check_context_length()` method that verifies input size vs model's context window

**Effort**: 2-3 hours

---

### 2. RateLimitTracker API Mismatch (3 failures)

**Files**: `tests/unit/test_scheduling_strategy.py`

**Missing Method**:
- `get_current_usage(model_name)` - Return current token usage for model

**Root Cause**: RateLimitTracker API changed but tests not updated

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/langfuse_observe/rate_limiter.py`

**Implementation Path**:
1. Add `get_current_usage()` method to RateLimitTracker class
2. Should return tuple of (current_tokens, limit_tokens)
3. Update `ProactiveRateLimitScheduler` to use new API

**Effort**: 1-2 hours

---

### 3. Analytics Validation (2 failures)

**Files**: `tests/unit/test_analytics.py`

**Issues**:
- `test_default_config`: Expects 'pk-test' but gets 'fake_public'
- `test_missing_credentials`: Should raise ValueError but doesn't

**Root Cause**: ExportConfig validation not enforcing credential requirements

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/analytics.py`

**Implementation Path**:
1. Update ExportConfig validation to check for real credentials
2. Add ValueError when required fields are missing/invalid
3. Ensure default credentials don't bypass validation

**Effort**: 1 hour

---

### 4. Gemini API Key Loading (3 failures)

**Files**: `tests/ci_tests/auto_gemini_styleguide/test_auto_gemini_styleguide.py`

**Issues**:
- `test_load_api_key_from_env_var`: Getting real key instead of test key
- `test_load_api_key_from_file`: Getting real key instead of test key
- `test_load_api_key_not_found`: Should be None but getting real key

**Root Cause**: Tests not properly mocking environment/file loading

**Fix Location**: `tests/ci_tests/auto_gemini_styleguide/test_auto_gemini_styleguide.py`

**Implementation Path**:
1. Mock environment variables in test setup
2. Mock file system reads
3. Ensure test isolation (real API keys not leaking)

**Effort**: 1-2 hours

---

### 5. DevDaemon Initialization Parameters (3 failures)

**Files**:
- `tests/ci_tests/test_daemon_user_scenarios.py`
- `tests/ci_tests/test_error_handling.py`

**Issues**:
- `test_user_scenario_daemon_verbose_mode`: DevDaemon doesn't accept 'verbose' parameter
- `test_daemon_rejects_invalid_max_retries`: DevDaemon doesn't accept 'max_retries' parameter

**Root Cause**: Test expectations don't match actual DevDaemon API

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon.py`

**Implementation Path**:
1. Add `verbose` parameter to DevDaemon.__init__()
2. Add `max_retries` parameter to DevDaemon.__init__()
3. OR update tests to not pass these parameters

**Effort**: 1 hour

---

### 6. NotificationDB API Changes (2 failures)

**Files**: `tests/ci_tests/test_notification_system.py`

**Issues**:
- `test_create_notification`: API expects different parameter names
- `test_retrieve_notification`: Similar API mismatch

**Root Cause**: NotificationDB API changed, parameter names updated but tests not

**Fix Location**: `tests/ci_tests/test_notification_system.py` or `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/notifications.py`

**Implementation Path**:
1. Check current NotificationDB.create_notification() signature
2. Update test calls to use correct parameter names
3. Current code uses: `type=` but tests may use `notification_type=`

**Effort**: 1 hour

---

### 7. Code Reviewer Perspectives (5 failures)

**Files**: `tests/code_reviewer/test_perspectives.py`

**Issues**:
- `test_detect_complex_function`: assert 0 > 0 (detection not working)
- `test_detect_nested_loops`: assert 0 > 0 (detection not working)
- `test_detect_string_concatenation_in_loop`: assert 0 > 0 (detection not working)
- `test_detect_database_query_in_loop`: assert 0 > 0 (detection not working)
- `test_detect_sql_injection`: assert 0 > 0 (detection not working)

**Root Cause**: Code perspective detectors not finding expected patterns

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/code_reviewer/perspectives.py`

**Implementation Path**:
1. Debug why pattern detection returns 0 instead of expected count
2. Check regex patterns or AST parsing logic
3. Verify test inputs match expected patterns

**Effort**: 2-3 hours

---

### 8. Bug002 Verification (1 failure)

**Files**: `tests/unit/test_bug_002_verification.py`

**Issue**:
- `test_ensure_technical_spec_spec_not_found`: Should log CFR-008 enforcement message

**Root Cause**: Implementation no longer logs this specific message

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_spec_manager.py`

**Note**: This was changed as part of today's fix to implement architect delegation. The test expectations need updating.

**Effort**: 1 hour

---

### 9. Startup Skill Executor Context Budget (1 failure)

**Files**: `tests/unit/test_startup_skill_executor.py`

**Issue**:
- `test_cfr007_validation_success`: assert 1.6575 < 1.0 (context budget exceeded)

**Root Cause**: Context budget validation threshold may be wrong

**Fix Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/startup_skill_executor.py`

**Implementation Path**:
1. Check CFR-007 context budget requirements (should be < 1.0 meaning < 100%)
2. Verify token calculation and budget allocation
3. May need to increase budget allocation or reduce token estimates

**Effort**: 1-2 hours

---

### 10. Other Failures (2 failures)

**Files**:
- `tests/ci_tests/test_coffee_maker_mains.py`
- `tests/manual_tests/test_daemon_e2e.py`

**Issues**:
- Various import and authentication errors
- Likely due to environment setup or missing dependencies

**Effort**: 1-2 hours each

---

## Fix Priority Recommendation

### High Priority (Quick Wins - 4-5 hours total)
1. **Analytics Validation** (1 hour)
2. **NotificationDB API** (1 hour)
3. **DevDaemon Parameters** (1 hour)
4. **Bug002 Verification** (1 hour)
5. **RateLimitTracker API** (1 hour)

### Medium Priority (Implementation Effort - 8-10 hours total)
1. **AutoPickerLLMRefactored** (2-3 hours)
2. **Code Reviewer Perspectives** (2-3 hours)
3. **Gemini API Key Loading** (1-2 hours)
4. **Startup Skill Executor** (1-2 hours)

### Lower Priority (Environment/Integration)
1. Other CI test failures (may be environment-specific)

---

## Session Summary

**Completed Work**:
1. Created `get_command_handler()` and `list_commands()` functions - Fixed 3 import errors
2. Fixed `test_daemon_architect_delegation.py` test fixtures - 10 tests now passing
3. Added `_build_architect_delegation_prompt()` to SpecManagerMixin - Delegates spec creation to architect
4. Implemented `register_command()` decorator - Fixed circular import issue

**Test Results**:
- Started with: 44 failures
- Now at: 37 failures
- Tests passing: 1548/1585 (97.7%)
- **Improvement**: 7 tests fixed, 18.75% reduction in failure count

**Total Session Time**: ~2 hours
**Remaining Effort**: 12-18 hours to fix all remaining issues

---

## Code Changes Made

### File 1: `/coffee_maker/cli/commands/__init__.py`
- Added `register_command()` decorator
- Added `get_command_handler()` function
- Added `list_commands()` function
- Moved ALL_COMMANDS import to _initialize_registry() to prevent circular imports

### File 2: `/coffee_maker/autonomous/daemon_spec_manager.py`
- Added `_build_architect_delegation_prompt()` method
- Added `_build_spec_creation_prompt()` method (backward compatibility)
- Updated `_ensure_technical_spec()` to delegate to architect via Claude
- Added content validation warnings

### File 3: `tests/unit/test_daemon_architect_delegation.py`
- Removed `__init__` from TestDaemonWithArchitectDelegation
- Added `setup()` method instead
- Added MockNotifications mock class
- Updated both test class fixtures to use setup() pattern

---

## Next Steps for Future Sessions

1. Run failing tests in smaller batches
2. Focus on one category at a time (e.g., all RateLimitTracker tests first)
3. Consider using `git blame` to understand when APIs changed
4. Create separate branches for each category fix
5. Run full test suite after each category is complete
