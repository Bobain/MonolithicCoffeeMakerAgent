# Backward Compatibility Examples

This document shows practical examples of using the backward compatibility layer.

## Quick Comparison

### Before and After for Each Agent

#### ProjectManager

```python
from coffee_maker.commands.consolidated import ProjectManagerCommands

pm = ProjectManagerCommands()

# OLD WAY (Still Works but Deprecated)
status = pm.check_priority_status("PRIORITY-28")
details = pm.get_priority_details("PRIORITY-28")
all_priorities = pm.list_all_priorities(status="blocked")
dev_status = pm.developer_status()
notifications = pm.notifications()
dependency_info = pm.check_dependency("requests")
new_dep_added = pm.add_dependency("pytest", "7.0.0")
pr_info = pm.monitor_github_pr(123)
issue_info = pm.track_github_issue(456)
sync_done = pm.sync_github_status()
stats = pm.roadmap_stats()

# NEW WAY (Recommended)
status = pm.roadmap(action="status", priority_id="PRIORITY-28")
details = pm.roadmap(action="details", priority_id="PRIORITY-28")
all_priorities = pm.roadmap(action="list", status="blocked")
dev_status = pm.status(action="developer")
notifications = pm.status(action="notifications")
dependency_info = pm.dependencies(action="check", package="requests")
new_dep_added = pm.dependencies(action="add", package="pytest", version="7.0.0")
pr_info = pm.github(action="monitor_pr", pr_number=123)
issue_info = pm.github(action="track_issue", issue_number=456)
sync_done = pm.github(action="sync")
stats = pm.stats(action="roadmap")
```

#### Architect

```python
from coffee_maker.commands.consolidated import ArchitectCommands

arch = ArchitectCommands()

# OLD WAY (Still Works but Deprecated)
spec = arch.create_technical_spec(title="Feature X", content="...")
updated = arch.update_technical_spec(spec_id="SPEC-1", content="...")
approved = arch.approve_spec(spec_id="SPEC-1")
tasks = arch.decompose_spec_to_tasks(spec_id="SPEC-1")
ordered = arch.update_task_order(spec_id="SPEC-1")
adr = arch.create_adr(title="ADR-1", content="...")
guidelines = arch.update_guidelines(content="...")

# NEW WAY (Recommended)
spec = arch.spec(action="create", title="Feature X", content="...")
updated = arch.spec(action="update", spec_id="SPEC-1", content="...")
approved = arch.spec(action="approve", spec_id="SPEC-1")
tasks = arch.tasks(action="decompose", spec_id="SPEC-1")
ordered = arch.tasks(action="update_order", spec_id="SPEC-1")
adr = arch.documentation(action="create_adr", title="ADR-1", content="...")
guidelines = arch.documentation(action="update_guidelines", content="...")
```

#### CodeDeveloper

```python
from coffee_maker.commands.consolidated import CodeDeveloperCommands

dev = CodeDeveloperCommands()

# OLD WAY (Still Works but Deprecated)
work = dev.claim_priority("PRIORITY-28")
spec_data = dev.load_spec(spec_id="SPEC-1")
status = dev.run_tests()
fixed = dev.fix_test_failures()
committed = dev.git_commit(message="feat: Add feature X")
pr = dev.create_pull_request()
review = dev.request_code_review(spec_id="SPEC-1")

# NEW WAY (Recommended)
work = dev.implement(action="claim", priority_id="PRIORITY-28")
spec_data = dev.implement(action="load", spec_id="SPEC-1")
status = dev.test(action="run")
fixed = dev.test(action="fix")
committed = dev.git(action="commit", message="feat: Add feature X")
pr = dev.git(action="create_pr")
review = dev.review(action="request", spec_id="SPEC-1")
```

#### CodeReviewer

```python
from coffee_maker.commands.consolidated import CodeReviewerCommands

reviewer = CodeReviewerCommands()

# OLD WAY (Still Works but Deprecated)
report = reviewer.generate_review_report(commit_sha="abc123")
score = reviewer.score_code_quality(commit_sha="abc123")
valid = reviewer.validate_definition_of_done(commit_sha="abc123")
style = reviewer.check_style_compliance(filepath="file.py")
secure = reviewer.run_security_scan()

# NEW WAY (Recommended)
report = reviewer.review(action="generate_report", commit_sha="abc123")
score = reviewer.review(action="score", commit_sha="abc123")
valid = reviewer.review(action="validate_dod", commit_sha="abc123")
style = reviewer.analyze(action="check_style_compliance", filepath="file.py")
secure = reviewer.analyze(action="run_security_scan")
```

#### Orchestrator

```python
from coffee_maker.commands.consolidated import OrchestratorCommands

orch = OrchestratorCommands()

# OLD WAY (Still Works but Deprecated)
agent = orch.spawn_agent_session("code_developer")
killed = orch.kill_stalled_agent("code_developer")
restarted = orch.restart_agent("code_developer")
worktree = orch.create_worktree("task-123")
cleaned = orch.cleanup_worktrees()

# NEW WAY (Recommended)
agent = orch.agents(action="spawn", agent_type="code_developer")
killed = orch.agents(action="kill", agent_type="code_developer")
restarted = orch.agents(action="restart", agent_type="code_developer")
worktree = orch.worktree(action="create_worktree", task_id="task-123")
cleaned = orch.worktree(action="cleanup_worktrees")
```

## Migration Guide

### Step 1: Find Legacy Commands in Your Code

```python
from coffee_maker.commands.consolidated.migration import find_legacy_commands

# Find all legacy command usage in your codebase
findings = find_legacy_commands("coffee_maker/")

for filepath, occurrences in findings.items():
    print(f"\n{filepath}:")
    for cmd, line_no, line_content in occurrences:
        print(f"  Line {line_no}: {cmd}")
        print(f"    {line_content}")
```

**Output Example:**
```
coffee_maker/commands/old_impl.py:
  Line 45: check_priority_status
    status = pm.check_priority_status("PRIORITY-28")
  Line 67: list_all_priorities
    priorities = pm.list_all_priorities(status="blocked")
```

### Step 2: Get Migration Suggestions

```python
from coffee_maker.commands.consolidated.migration import CodeMigrator

migrator = CodeMigrator()

# Get the migration suggestion for a command
suggestion = migrator.get_migration_suggestion("check_priority_status")
print(suggestion)
# Output: roadmap(action='status', ...)
```

### Step 3: Update Your Code

For each legacy command found, replace it with the suggested new format:

```python
# Before
status = pm.check_priority_status("PRIORITY-28")

# After
status = pm.roadmap(action="status", priority_id="PRIORITY-28")
```

### Step 4: Verify No Legacy Commands Remain

```python
from coffee_maker.commands.consolidated.migration import validate_directory_migrated

# Check if your directory has been fully migrated
is_valid, errors = validate_directory_migrated("coffee_maker/")

if is_valid:
    print("Migration complete! All legacy commands replaced.")
else:
    print("Still have legacy commands:")
    for error in errors:
        print(f"  - {error}")
```

## Full Example: Migrating a File

Here's a complete before/after example:

### Before Migration

```python
# coffee_maker/priority_manager.py
from coffee_maker.commands.consolidated import ProjectManagerCommands

class PriorityManager:
    def __init__(self):
        self.pm = ProjectManagerCommands()

    def show_priority_status(self, priority_id):
        # Using deprecated legacy command
        status = self.pm.check_priority_status(priority_id)
        return status

    def get_details(self, priority_id):
        # Using deprecated legacy command
        details = self.pm.get_priority_details(priority_id)
        return details

    def list_all(self, status=None):
        # Using deprecated legacy command
        priorities = self.pm.list_all_priorities(status=status)
        return priorities
```

### After Migration

```python
# coffee_maker/priority_manager.py
from coffee_maker.commands.consolidated import ProjectManagerCommands

class PriorityManager:
    def __init__(self):
        self.pm = ProjectManagerCommands()

    def show_priority_status(self, priority_id):
        # Using new consolidated command
        status = self.pm.roadmap(action="status", priority_id=priority_id)
        return status

    def get_details(self, priority_id):
        # Using new consolidated command
        details = self.pm.roadmap(action="details", priority_id=priority_id)
        return details

    def list_all(self, status=None):
        # Using new consolidated command
        priorities = self.pm.roadmap(action="list", status=status)
        return priorities
```

## Deprecation Warnings

When you use a legacy command, you'll see a warning (once per session):

```python
from coffee_maker.commands.consolidated import ProjectManagerCommands
import warnings

pm = ProjectManagerCommands()

# First call shows deprecation warning
status = pm.check_priority_status("PRIORITY-28")

# Warning output:
# DeprecationWarning: 'check_priority_status' is deprecated,
# use 'roadmap(action='status')' instead.

# Subsequent calls in same session won't show warning
status2 = pm.check_priority_status("PRIORITY-29")  # No warning
```

## Common Migration Patterns

### Pattern 1: Single Parameter Mapping

**Old**: `pm.check_priority_status(priority_id)`
**New**: `pm.roadmap(action="status", priority_id=priority_id)`

### Pattern 2: Multiple Parameters

**Old**: `pm.list_all_priorities(status="blocked", assignee="dev1")`
**New**: `pm.roadmap(action="list", status="blocked", assignee="dev1")`

### Pattern 3: No Parameters

**Old**: `pm.developer_status()`
**New**: `pm.status(action="developer")`

### Pattern 4: Method Chaining Compatibility

Both old and new styles support the same behavior:

```python
# Both work the same way:
pm.check_priority_status("PRIORITY-28")  # Old
pm.roadmap(action="status", priority_id="PRIORITY-28")  # New
```

## Testing Backward Compatibility

### Test that Legacy Commands Work

```python
import pytest
from coffee_maker.commands.consolidated import ProjectManagerCommands

def test_legacy_command_works():
    pm = ProjectManagerCommands()

    # Legacy command should be callable
    assert callable(pm.check_priority_status)

    # Should exist as a method
    assert hasattr(pm, "check_priority_status")
```

### Test that New Commands Work

```python
def test_new_command_works():
    pm = ProjectManagerCommands()

    # New command should be callable
    assert callable(pm.roadmap)

    # Should accept action parameter
    # (actual implementation depends on handlers)
```

### Test Deprecation Warning

```python
import warnings

def test_deprecation_warning_shown():
    pm = ProjectManagerCommands()

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        try:
            pm.check_priority_status()
        except:
            pass  # Expected to fail, we just want the warning

        # Check warning was issued
        assert any("deprecated" in str(warning.message).lower()
                  for warning in w)
```

## Troubleshooting

### Q: I'm still seeing the legacy command working, should I migrate?

**A**: Yes! While it still works, you should migrate because:
- New format is cleaner and more consistent
- Consolidation reduces cognitive load
- Future versions may deprecate these aliases
- Migration tools make it easy

### Q: How do I know which commands I'm using that are legacy?

**A**: Use the migration tools:
```python
from coffee_maker.commands.consolidated.migration import find_legacy_commands

findings = find_legacy_commands("your_directory/")
# Shows you exactly which legacy commands are used and where
```

### Q: Can I mix old and new commands in the same file?

**A**: Yes, but it's not recommended. You can:
- Use old commands while they're supported
- Gradually migrate to new commands
- Eventually remove all old commands

### Q: What if I have a lot of legacy commands to migrate?

**A**: Use the bulk migration approach:
```python
from coffee_maker.commands.consolidated.migration import CodeMigrator

migrator = CodeMigrator()

# 1. Generate a report
report = migrator.generate_migration_report("coffee_maker/")
print(report)

# 2. Use find/replace to update similar patterns
# 3. Run tests to verify everything works
# 4. Validate migration is complete
from coffee_maker.commands.consolidated.migration import (
    validate_directory_migrated
)
is_valid, errors = validate_directory_migrated("coffee_maker/")
```

## Command Coverage Map

For quick reference, here's which legacy command maps to which new command:

```
ProjectManager (15 legacy commands)
├─ roadmap (4): check_priority_status, get_priority_details, list_all_priorities, update_priority_metadata
├─ status (2): developer_status, notifications
├─ dependencies (2): check_dependency, add_dependency
├─ github (3): monitor_github_pr, track_github_issue, sync_github_status
└─ stats (4): roadmap_stats, feature_stats, spec_stats, audit_trail

Architect (16 legacy commands)
├─ spec (5): create_technical_spec, update_technical_spec, approve_spec, deprecate_spec, link_spec_to_priority
├─ tasks (3): decompose_spec_to_tasks, update_task_order, merge_task_branches
├─ documentation (3): create_adr, update_guidelines, update_styleguide
├─ review (2): validate_architecture, design_api
└─ dependencies (3): check_dependency, add_dependency, evaluate_dependency

CodeDeveloper (17 legacy commands)
├─ implement (5): claim_priority, load_spec, update_implementation_status, record_commit, complete_implementation
├─ test (3): run_tests, fix_test_failures, generate_coverage_report
├─ git (2): git_commit, create_pull_request
├─ review (2): request_code_review, track_review_status
├─ quality (3): run_pre_commit_hooks, generate_quality_metrics, lint_code
└─ config (2): update_claude_config, update_project_config

CodeReviewer (14 legacy commands)
├─ review (3): generate_review_report, score_code_quality, validate_definition_of_done
├─ analyze (7): check_style_compliance, run_security_scan, analyze_complexity, check_test_coverage, validate_type_hints, validate_architecture, validate_documentation
├─ monitor (2): detect_new_commits, track_issue_resolution
└─ notify (2): notify_architect, notify_code_developer

Orchestrator (17 legacy commands)
├─ agents (5): spawn_agent_session, kill_stalled_agent, restart_agent, monitor_agent_lifecycle, handle_agent_errors
├─ messages (3): route_inter_agent_messages, send_message, receive_message
├─ orchestrate (4): coordinate_dependencies, find_available_work, create_parallel_tasks, detect_deadlocks
├─ worktree (3): create_worktree, cleanup_worktrees, merge_completed_work
└─ monitor (2): monitor_resource_usage, generate_activity_summary

TOTAL: 79 legacy commands mapped
```

---

**Version**: 2.0.0
**Last Updated**: 2025-10-27
