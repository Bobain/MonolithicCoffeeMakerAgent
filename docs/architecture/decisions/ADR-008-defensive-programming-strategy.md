# ADR-008: Adopt Defensive Programming Strategy Throughout Codebase

**Status**: Proposed
**Date**: 2025-10-16
**Author**: architect agent
**Related**: REFACTOR-003, CODE_QUALITY_AUDIT_2025-10-16

---

## Context

The MonolithicCoffeeMakerAgent codebase has experienced **production reliability issues** due to insufficient error handling:

**Current Pain Points**:
1. **Daemon crashes** on transient failures (file I/O, network errors)
2. **Data loss** when operations fail mid-execution
3. **Cryptic error messages** that don't guide users to resolution
4. **Long mean time to recovery** (45 minutes on average)
5. **Difficult debugging** due to missing context in logs

**Specific Examples**:
- Daemon crashed when ROADMAP.md temporarily had wrong permissions
- Network API call failure brought down entire system (no retry)
- Malformed priority section caused parser crash (no validation)
- Concurrent file writes corrupted roadmap (no locking/atomicity)

**Operational Metrics** (last 30 days):
- Daemon crashes: 5 (preventable)
- User-reported "mysterious failures": 8
- Average time to debug: 45 minutes
- Data loss incidents: 2

**Code Analysis**:
- File I/O without error handling: 15+ locations
- Network calls without retry: 8+ locations
- Missing input validation: 20+ locations
- Uncaught exceptions in daemon loop: 5+ locations

**Developer Feedback**:
- "I'm afraid to add new features - might break something"
- "Hard to know what errors to handle and how"
- "Error messages don't tell me what went wrong"

---

## Decision

We will adopt a **comprehensive defensive programming strategy** throughout the codebase:

### 1. Create Defensive Utilities Layer

Create reusable utilities for common error-prone operations:

**`coffee_maker/utils/defensive_io.py`**:
- `DefensiveFileMixin` for safe file operations
- Automatic backups before writes
- Atomic write operations (temp file + rename)
- Clear error logging

**`coffee_maker/utils/retry.py`**:
- `retry_with_backoff` decorator for network operations
- Exponential backoff (1s, 2s, 4s...)
- Configurable max attempts
- Log retry attempts

**`coffee_maker/utils/validation.py`**:
- `Validator` class for input validation
- Common validations: not_none, not_empty, file_exists, range_check
- Clear error messages

### 2. Apply to Critical Paths First

**Priority Order**:
1. **daemon.py**: Core autonomous loop (crashes affect entire system)
2. **roadmap_parser.py**: File parsing (malformed input causes crashes)
3. **claude_api_interface.py**: External API calls (network failures)
4. **status_report_generator.py**: File I/O heavy module

### 3. Establish Error Handling Patterns

**Pattern 1: File Operations**
```python
# Use DefensiveFileMixin
content = self.read_file_safely(
    path,
    default="# Empty\n",  # Safe default
    encoding='utf-8'
)
if content is None:
    logger.error(f"Failed to read {path}")
    return self._handle_missing_file()
```

**Pattern 2: Network Operations**
```python
# Use retry decorator
@retry_with_backoff(max_attempts=3, initial_delay=2.0)
def _call_api(self):
    return self.client.execute(...)
```

**Pattern 3: Input Validation**
```python
# Validate inputs early
priority_name = Validator.validate_not_empty(
    next_priority.get('name'),
    'priority name'
)
```

**Pattern 4: Error Recovery**
```python
# Provide recovery path
try:
    result = self._risky_operation()
except RecoverableError as e:
    logger.warning(f"Operation failed: {e}. Trying fallback...")
    result = self._fallback_operation()
except FatalError as e:
    logger.error(f"Fatal error: {e}")
    self._notify_user_and_stop()
    raise
```

### 4. Error Message Standards

**Bad**:
```python
logger.error("Failed to parse")  # What failed? Why?
```

**Good**:
```python
logger.error(
    f"Failed to parse priority section in {roadmap_path}. "
    f"Expected format: '### 🔴 **PRIORITY X:**'. "
    f"Found: '{section_header}'. "
    f"Please check ROADMAP.md line {line_num}."
)
```

**Components of a Good Error Message**:
1. **What** went wrong
2. **Where** it happened (file, line, context)
3. **Why** it failed (expected vs actual)
4. **How** to fix it (actionable guidance)

### 5. Testing Standards

**Every error path must have a test**:
```python
def test_read_file_with_permission_error():
    """Test reading file with permission error returns default."""
    mixin = DefensiveFileMixin()
    file.chmod(0o000)  # Remove permissions

    result = mixin.read_file_safely(file, default="default")

    assert result == "default"  # Falls back gracefully
```

---

## Consequences

### Positive

1. **Reliability ✅**
   - Daemon uptime: 85% → >99%
   - Data loss incidents: 2/month → 0/month
   - Mean time to recover: 45min → <5min

2. **Debuggability ✅**
   - Clear, actionable error messages
   - Rich context in logs (file, line, values)
   - Easier to reproduce issues in tests

3. **Developer Experience ✅**
   - Reusable error handling utilities
   - Clear patterns to follow
   - Confidence in making changes

4. **User Experience ✅**
   - System "just works" more often
   - Clear guidance when errors occur
   - Automatic recovery from transient failures

5. **Operational Excellence ✅**
   - Fewer on-call incidents
   - Faster problem resolution
   - Better observability

### Negative

1. **Initial Implementation Cost** 😞
   - **Effort**: 10-15 hours to implement utilities
   - **Effort**: 20-30 hours to apply throughout codebase
   - **Effort**: 10-15 hours to write error simulation tests
   - **Total**: 40-60 hours

2. **More Code** 😞
   - Error handling adds ~20-30% more code per module
   - More tests needed (error paths)
   - Slightly slower development initially

3. **Learning Curve** 😐
   - Team needs to learn new patterns
   - May feel like "boilerplate" at first
   - Requires discipline to apply consistently

4. **Potential Over-Engineering** 😐
   - Risk of handling errors that never happen
   - Need to balance defensive vs. pragmatic
   - May hide real bugs if error handling too aggressive

### Mitigations

**For Implementation Cost**:
- ✅ Prioritize by ROI (critical paths first)
- ✅ Incremental rollout (one module at a time)
- ✅ Reusable utilities reduce duplication

**For Code Volume**:
- ✅ Utilities abstract complexity
- ✅ Decorator pattern keeps business logic clean
- ✅ Better code quality justifies slight increase

**For Learning Curve**:
- ✅ Create GUIDELINE-XXX: Error Handling Best Practices
- ✅ Code examples in ADR
- ✅ Code review feedback
- ✅ Pair programming for first implementations

**For Over-Engineering**:
- ✅ Focus on observed failures first
- ✅ Document error rates (monitor what matters)
- ✅ Balance pragmatism with defense

---

## Alternatives Considered

### Alternative 1: Status Quo (Do Nothing)

**Pros**:
- No implementation cost
- No code changes
- No learning curve

**Cons**:
- Continued production crashes
- Poor user experience
- Developer anxiety about breaking things
- Operational burden (debugging, recovery)

**Verdict**: ❌ **Rejected** - Cost of inaction too high

---

### Alternative 2: Add Error Handling Ad-Hoc (As Bugs Occur)

**Pros**:
- Lower upfront cost
- Focus on real problems only
- Incremental approach

**Cons**:
- Inconsistent error handling patterns
- Reactive (fix after problems occur)
- No systematic coverage
- Different error messages everywhere
- Higher long-term cost (fix same bug multiple times)

**Verdict**: ❌ **Rejected** - Leads to inconsistency

---

### Alternative 3: Use External Error Handling Library (e.g., tenacity, retrying)

**Pros**:
- Battle-tested libraries
- Less code to maintain
- Well-documented patterns

**Cons**:
- External dependency (licensing, maintenance)
- May not fit our specific needs
- Learning curve for library API
- Less control over behavior

**Verdict**: ⚠️ **Partially Adopted**
- Use `tenacity` for retry logic (if user approves dependency)
- Write our own defensive I/O (too specific to our needs)

---

### Alternative 4: Implement Error Handling in Base Classes Only

**Pros**:
- Centralized error handling
- Less code duplication
- Easier to maintain

**Cons**:
- Forces rigid class hierarchy
- Not all code uses classes (functions, scripts)
- Hard to customize per-module

**Verdict**: ⚠️ **Partially Adopted**
- Mixins for reusable patterns (DefensiveFileMixin)
- Decorators for standalone functions (retry_with_backoff)
- Allow per-module customization

---

## Implementation Plan

### Phase 1: Foundation (Week 1, 10-15 hours)

**Step 1.1**: Create Defensive Utilities (6 hours)
- [ ] `defensive_io.py`: DefensiveFileMixin
- [ ] `retry.py`: retry_with_backoff decorator
- [ ] `validation.py`: Validator class
- [ ] Unit tests for each utility

**Step 1.2**: Apply to daemon.py (6 hours)
- [ ] Replace file reads with read_file_safely
- [ ] Add retry to Claude API calls
- [ ] Validate priority structure before processing
- [ ] Test error scenarios

**Checkpoint**: Daemon runs 24h without crashes

### Phase 2: Core Modules (Week 2, 15-20 hours)

**Step 2.1**: Apply to roadmap_parser.py (4 hours)
- [ ] Defensive file reading
- [ ] Validate priority sections
- [ ] Handle malformed content gracefully

**Step 2.2**: Apply to claude_api_interface.py (4 hours)
- [ ] Retry logic for all API calls
- [ ] Rate limit handling
- [ ] Clear error messages

**Step 2.3**: Apply to status_report_generator.py (4 hours)
- [ ] Defensive file operations
- [ ] Validate extracted data
- [ ] Handle missing fields

**Step 2.4**: Integration Testing (3 hours)
- [ ] Error simulation tests
- [ ] Recovery scenario tests
- [ ] End-to-end reliability tests

**Checkpoint**: Core modules have >90% error handling coverage

### Phase 3: Rollout (Week 3-4, 10-15 hours)

**Step 3.1**: Apply to Remaining Modules (8 hours)
- [ ] CLI modules
- [ ] Reporting modules
- [ ] Utility modules

**Step 3.2**: Documentation (3 hours)
- [ ] GUIDELINE-XXX: Error Handling Best Practices
- [ ] Update module docstrings
- [ ] Add to onboarding docs

**Step 3.3**: Monitoring (2 hours)
- [ ] Track error rates
- [ ] Monitor recovery success
- [ ] Alert on persistent failures

**Checkpoint**: System-wide reliability >99%

---

## Monitoring & Success Criteria

### Metrics to Track

**Before Implementation** (Baseline):
- Daemon uptime: 85%
- Crashes per month: 5
- Data loss incidents: 2
- Mean time to recover: 45 minutes
- User-reported failures: 8

**After Implementation** (Target):
- Daemon uptime: >99%
- Crashes per month: <1
- Data loss incidents: 0
- Mean time to recover: <5 minutes
- User-reported failures: <2

### How to Measure Success

**Quantitative**:
- ✅ Daemon runs 7+ days without crashes
- ✅ Zero data loss incidents for 30 days
- ✅ Error recovery time <5 minutes (95th percentile)
- ✅ Error handling coverage >90%

**Qualitative**:
- ✅ Developer feedback: "More confident making changes"
- ✅ User feedback: "Fewer mysterious failures"
- ✅ On-call feedback: "Easier to debug issues"

---

## Communication Plan

### Team Announcement

**When**: After ADR approval, before implementation
**Who**: architect to all developers
**What**: Explain strategy, utilities, patterns, timeline

### Training

**When**: Week 1 (during Phase 1 implementation)
**Format**: Code walkthrough + Q&A
**Content**:
- Why defensive programming?
- How to use utilities (DefensiveFileMixin, retry, validation)
- Error message standards
- Testing error paths

### Code Reviews

**Focus Areas**:
- Error handling present in new code?
- Using utilities correctly?
- Error messages clear and actionable?
- Tests cover error paths?

---

## Related Decisions

**Supersedes**: None
**Superseded By**: None
**Related**:
- ADR-001: Use Mixins Pattern (enables DefensiveFileMixin)
- ADR-XXX: Centralize Pattern Extraction (complements defensive I/O)
- ADR-XXX: Command Pattern for CLI (benefits from consistent error handling)

---

## Approval & Sign-Off

**Decision Date**: _____________
**Approved By**: _____________

**Stakeholders**:
- [x] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (operations)
- [ ] User (final authority)

---

**ADR created**: 2025-10-16 by architect agent
**Status**: Proposed (awaiting approval)
**Next Action**: Present to team for review and approval
