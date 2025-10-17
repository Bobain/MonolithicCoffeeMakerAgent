# SPEC-060: ACE API Completeness Testing

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 3.2)
**Priority**: MEDIUM
**Impact**: MEDIUM (ACE Framework Reliability)

---

## Problem Statement

### Current State
ACE API (`ace/api.py`) has partial test coverage, missing:
- Trace creation and retrieval tests
- File ownership enforcement verification
- Agent registry integration tests
- Error scenarios (unauthorized access, missing traces)

### code-searcher Finding
> **Test Coverage Gaps: ACE API**
> - Location: `coffee_maker/autonomous/ace/api.py`
> - Missing Coverage: Trace management, ownership enforcement, integration tests
> - Effort: 7 hours
> - Impact: MEDIUM (ACE framework reliability)

### Why This Matters
- ACE framework is foundation for agent coordination
- File ownership violations could corrupt documentation
- Missing traces break agent analysis
- Integration issues hard to debug

---

## Proposed Solution

Add comprehensive tests for ACE API:

1. **Trace Management** (4 tests)
   - Create trace
   - Retrieve trace
   - List traces by agent
   - Update trace status

2. **File Ownership Enforcement** (3 tests)
   - Verify owner can modify
   - Verify non-owner cannot modify
   - Test ownership transfer

3. **Agent Registry Integration** (3 tests)
   - Agent registration tracking
   - Concurrent agent prevention
   - Agent unregistration

4. **Error Scenarios** (3 tests)
   - Unauthorized access attempts
   - Missing trace retrieval
   - Invalid trace updates

---

## Component Design

### New Test File

**`tests/unit/autonomous/ace/test_ace_api.py`**:

```python
class TestACETraceManagement:
    """Test ACE trace creation and retrieval."""

    def test_create_trace(self):
        """Test creating a new execution trace."""
        api = ACEApi()

        trace_id = api.create_trace(
            agent="generator",
            task="Implement feature X"
        )

        assert trace_id is not None
        trace = api.get_trace(trace_id)
        assert trace["agent"] == "generator"

    def test_retrieve_trace(self):
        """Test retrieving existing trace."""
        api = ACEApi()
        trace_id = api.create_trace(agent="generator", task="Test")

        trace = api.get_trace(trace_id)

        assert trace is not None
        assert trace["task"] == "Test"

    def test_list_traces_by_agent(self):
        """Test listing traces for specific agent."""
        api = ACEApi()
        api.create_trace(agent="generator", task="Task 1")
        api.create_trace(agent="generator", task="Task 2")
        api.create_trace(agent="reflector", task="Task 3")

        traces = api.list_traces(agent="generator")

        assert len(traces) == 2
        assert all(t["agent"] == "generator" for t in traces)

    def test_update_trace_status(self):
        """Test updating trace execution status."""
        api = ACEApi()
        trace_id = api.create_trace(agent="generator", task="Test")

        api.update_trace(trace_id, status="completed")

        trace = api.get_trace(trace_id)
        assert trace["status"] == "completed"


class TestACEFileOwnership:
    """Test file ownership enforcement."""

    def test_owner_can_modify_file(self):
        """Test file owner can modify their files."""
        api = ACEApi()
        api.register_file_owner("docs/test.md", "generator")

        result = api.verify_ownership("docs/test.md", "generator")

        assert result is True

    def test_non_owner_cannot_modify(self):
        """Test non-owner cannot modify file."""
        api = ACEApi()
        api.register_file_owner("docs/test.md", "generator")

        result = api.verify_ownership("docs/test.md", "reflector")

        assert result is False

    def test_ownership_transfer(self):
        """Test file ownership can be transferred."""
        api = ACEApi()
        api.register_file_owner("docs/test.md", "generator")

        api.transfer_ownership("docs/test.md", "reflector")

        assert api.verify_ownership("docs/test.md", "reflector") is True
        assert api.verify_ownership("docs/test.md", "generator") is False


class TestACEAgentRegistry:
    """Test agent registry integration."""

    def test_agent_registration_tracked(self):
        """Test agent registration is tracked in ACE."""
        api = ACEApi()

        api.register_agent("generator")

        assert api.is_agent_running("generator") is True

    def test_concurrent_agent_prevention(self):
        """Test ACE prevents concurrent agents."""
        api = ACEApi()
        api.register_agent("generator")

        with pytest.raises(AgentAlreadyRunningError):
            api.register_agent("generator")

    def test_agent_unregistration(self):
        """Test agent unregistration."""
        api = ACEApi()
        api.register_agent("generator")

        api.unregister_agent("generator")

        assert api.is_agent_running("generator") is False


class TestACEErrorScenarios:
    """Test ACE API error handling."""

    def test_unauthorized_access_attempt(self):
        """Test error when agent tries unauthorized access."""
        api = ACEApi()
        api.register_file_owner("docs/test.md", "generator")

        with pytest.raises(PermissionError):
            api.modify_file("docs/test.md", "reflector", "new content")

    def test_missing_trace_retrieval(self):
        """Test error when retrieving non-existent trace."""
        api = ACEApi()

        with pytest.raises(KeyError):
            api.get_trace("nonexistent-trace-id")

    def test_invalid_trace_update(self):
        """Test error when updating with invalid status."""
        api = ACEApi()
        trace_id = api.create_trace(agent="generator", task="Test")

        with pytest.raises(ValueError):
            api.update_trace(trace_id, status="invalid_status")
```

---

## Technical Details

### Test Coverage Goals
- Trace management: 95%
- File ownership: 100%
- Agent registry integration: 90%
- Error handling: 90%

### Mock Infrastructure
```python
@pytest.fixture
def mock_ace_api():
    """Create mock ACE API for testing."""
    return ACEApi(db_path=":memory:")
```

---

## Rollout Plan

### Week 1: Implementation (7 hours)
- **Day 1**: Trace management tests (2 hours)
- **Day 2**: Ownership tests (2 hours)
- **Day 3**: Registry + error tests (3 hours)

---

## Success Criteria

### Quantitative
- ✅ 13 new tests added
- ✅ ACE API coverage ≥90%
- ✅ All error scenarios tested
- ✅ File ownership enforcement verified

### Qualitative
- ✅ ACE framework more reliable
- ✅ Ownership violations prevented
- ✅ Easier to debug ACE issues

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 7 hours
**Actual Effort**: TBD
