# Daemon Split Plan - Option D

**Created**: 2025-10-12
**Target**: Split daemon.py (1583 lines) into 4-5 logical modules

## Current Structure Analysis

### DevDaemon Class (1583 lines)
- **Core loop**: `__init__`, `run`, `_check_prerequisites`, `_reset_claude_context`
- **Git operations**: `_sync_roadmap_branch`, `_merge_to_roadmap`
- **Spec management**: `_ensure_technical_spec`, `_build_spec_creation_prompt`
- **Implementation**: `_request_approval`, `_implement_priority`, `_build_*_prompt` methods (5 methods)
- **Status/Notifications**: `_notify_completion`, `_notify_persistent_failure`, `_write_status`, `_update_subtask`

### Existing External Dependencies
Already split into separate files:
- `claude_api_interface.py` - ClaudeAPI
- `git_manager.py` - GitManager
- `roadmap_parser.py` - RoadmapParser
- `developer_status.py` - DeveloperStatus
- `task_metrics.py` - TaskMetricsDB

## Proposed Split Strategy

### Option 1: Mixin Pattern (Recommended)
Split into mixins that DevDaemon composes via multiple inheritance:

```
coffee_maker/autonomous/
├── daemon.py                    # Main DevDaemon (200-300 lines)
├── daemon_git_ops.py           # GitOpsMixin (~150 lines)
├── daemon_spec_manager.py      # SpecManagerMixin (~200 lines)
├── daemon_implementation.py    # ImplementationMixin (~600 lines)
└── daemon_status.py            # StatusMixin (~200 lines)
```

**Benefits**:
- Minimal changes to public API
- Clear separation of concerns
- Easy to test each mixin independently
- Maintains backward compatibility

**DevDaemon structure**:
```python
class DevDaemon(GitOpsMixin, SpecManagerMixin,
                ImplementationMixin, StatusMixin):
    """Main daemon orchestrator."""

    def __init__(self, ...):
        # Initialize all mixins
        pass

    def run(self):
        # Main loop using mixin methods
        pass
```

### Option 2: Strategy/Dependency Injection Pattern
Extract strategies as separate classes:

```
coffee_maker/autonomous/daemon/
├── __init__.py                 # Re-export DevDaemon
├── core.py                     # DevDaemon main class
├── git_strategy.py             # GitStrategy class
├── spec_strategy.py            # SpecStrategy class
├── implementation_strategy.py  # ImplementationStrategy class
└── status_strategy.py          # StatusStrategy class
```

**Benefits**:
- Pure dependency injection
- Easier to mock for testing
- More explicit dependencies
- Better for Option B (dependency injection)

**DevDaemon structure**:
```python
class DevDaemon:
    def __init__(
        self,
        git_strategy: GitStrategy,
        spec_strategy: SpecStrategy,
        impl_strategy: ImplementationStrategy,
        status_strategy: StatusStrategy,
    ):
        self.git_ops = git_strategy
        self.spec_manager = spec_strategy
        self.implementation = impl_strategy
        self.status_manager = status_strategy
```

## Decision: Hybrid Approach

Start with **Option 1 (Mixins)** for quick wins, then migrate to **Option 2 (Strategies)** as part of Option B (dependency injection).

**Phase 1**: Extract mixins (this task)
- Quick to implement
- Minimal breaking changes
- Immediate readability improvement

**Phase 2**: Convert to strategies (Option B task)
- Proper dependency injection
- Interface extraction
- Full testability

## Implementation Plan - Phase 1 (Mixins)

### Step 1: Create GitOpsMixin (~150 lines)
Extract from daemon.py lines 603-787:
- `_sync_roadmap_branch()` - Syncs with origin/roadmap
- `_merge_to_roadmap()` - Merges feature branch to roadmap

**Dependencies**:
- `self.git` (GitManager)
- `self.developer_status` (DeveloperStatus)
- `self.logger`

**File**: `coffee_maker/autonomous/daemon_git_ops.py`

### Step 2: Create SpecManagerMixin (~200 lines)
Extract from daemon.py lines 788-920:
- `_ensure_technical_spec()` - Ensures spec exists or creates it
- `_build_spec_creation_prompt()` - Builds prompt for spec creation

**Dependencies**:
- `self.claude` (ClaudeAPI)
- `self.roadmap_path`
- `self.logger`

**File**: `coffee_maker/autonomous/daemon_spec_manager.py`

### Step 3: Create ImplementationMixin (~600 lines)
Extract from daemon.py lines 921-1334:
- `_request_approval()` - Asks for user approval
- `_implement_priority()` - Main implementation logic
- `_build_implementation_prompt()` - Builds implementation prompt
- `_build_documentation_prompt()` - Builds doc prompt
- `_build_feature_prompt()` - Builds feature prompt
- `_build_commit_message()` - Builds commit message
- `_build_pr_body()` - Builds PR body

**Dependencies**:
- `self.claude` (ClaudeAPI)
- `self.git` (GitManager)
- `self.auto_approve`
- `self.create_prs`
- `self.developer_status`
- `self.logger`

**File**: `coffee_maker/autonomous/daemon_implementation.py`

### Step 4: Create StatusMixin (~200 lines)
Extract from daemon.py lines 1335-1579:
- `_notify_completion()` - Sends completion notification
- `_notify_persistent_failure()` - Sends failure notification
- `_write_status()` - Writes status to JSON
- `_update_subtask()` - Updates subtask status

**Dependencies**:
- `self.notif_db` (NotificationDB)
- `self.developer_status` (DeveloperStatus)
- `self.task_metrics` (TaskMetricsDB)
- `self.logger`

**File**: `coffee_maker/autonomous/daemon_status.py`

### Step 5: Update daemon.py (200-300 lines)
Keep only:
- Class docstring
- `__init__()` method
- `run()` main loop
- `_check_prerequisites()`
- `_reset_claude_context()`
- `stop()` method

Inherit from all mixins:
```python
class DevDaemon(GitOpsMixin, SpecManagerMixin,
                ImplementationMixin, StatusMixin):
    """Autonomous development daemon."""
```

## Testing Strategy

### Unit Tests
Each mixin should be testable independently:

```python
# test_daemon_git_ops.py
def test_sync_roadmap_branch():
    mixin = GitOpsMixin()
    mixin.git = Mock(GitManager)
    mixin.developer_status = Mock(DeveloperStatus)
    result = mixin._sync_roadmap_branch()
    assert result is True
```

### Integration Tests
Test DevDaemon with all mixins:

```python
# test_daemon_integration.py
def test_full_daemon_cycle():
    daemon = DevDaemon(auto_approve=True)
    # Mock external dependencies
    # Run one iteration
    # Verify all mixins were called
```

## Migration Checklist

- [ ] Create `daemon_git_ops.py` with GitOpsMixin
- [ ] Create `daemon_spec_manager.py` with SpecManagerMixin
- [ ] Create `daemon_implementation.py` with ImplementationMixin
- [ ] Create `daemon_status.py` with StatusMixin
- [ ] Update `daemon.py` to use all mixins
- [ ] Update imports in other files (if any direct daemon.py imports)
- [ ] Run existing tests to verify no breakage
- [ ] Add unit tests for each mixin
- [ ] Update documentation
- [ ] Commit and push

## Expected Benefits

**Readability**:
- daemon.py: 1583 lines → ~250 lines (84% reduction)
- Each mixin: 150-600 lines (manageable chunks)

**Maintainability**:
- Clear separation of concerns
- Easier to find and modify specific functionality
- Reduced cognitive load

**Testability**:
- Each mixin can be tested independently
- Easier to mock dependencies
- Better test coverage

## Risks and Mitigation

**Risk 1**: Breaking changes in public API
- **Mitigation**: Keep public API identical, only change internal structure
- **Verification**: Run full test suite

**Risk 2**: Circular dependencies between mixins
- **Mitigation**: Careful dependency analysis, use shared state via `self`
- **Verification**: Import tests

**Risk 3**: Complex multiple inheritance
- **Mitigation**: Use MRO (Method Resolution Order) carefully, document clearly
- **Verification**: Test method resolution

## Next Steps

1. Create GitOpsMixin first (smallest, lowest risk)
2. Test integration with DevDaemon
3. Continue with other mixins in order
4. Run full test suite after each mixin
5. Document changes in ROADMAP.md
