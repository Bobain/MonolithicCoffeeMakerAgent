# Consolidated Commands User Guide

## Overview

MonolithicCoffeeMakerAgent uses a **consolidated command architecture** that reduces the number of individual commands from 100+ to just **36 unified commands** across all agents.

Instead of remembering dozens of commands, each agent now has **3-6 consolidated commands** that handle multiple actions through parameter routing.

### Key Benefits

- **Easier to learn**: 36 commands instead of 100+
- **Consistent interface**: All commands follow the same pattern
- **Action-based routing**: Commands use `action` parameter to specify what to do
- **Backward compatible**: Old commands still work with deprecation warnings
- **Faster execution**: Reduced cognitive load means faster implementation

---

## Command Pattern

All consolidated commands follow this pattern:

```python
# Old style (deprecated, but still works)
result = agent.command_name(param1, param2)

# New style (recommended)
result = agent.consolidated_command(action="specific_action", param1=value1, param2=value2)
```

### Example

```python
# Project Manager - Old style
pm.check_priority_status("PRIORITY-28")
pm.get_priority_details("PRIORITY-28")

# Project Manager - New style
pm.roadmap(action="status", priority_id="PRIORITY-28")
pm.roadmap(action="details", priority_id="PRIORITY-28")
```

---

## Agent Command Reference

### 1. Project Manager (5 Commands)

**Role**: Manage ROADMAP, track status, monitor GitHub, handle dependencies

#### command: `roadmap`

**Description**: All ROADMAP priority operations

**Actions**:
- `list` - List all priorities (with optional filtering)
- `details` - Get details for a specific priority
- `update` - Update priority metadata
- `status` - Check priority status

**Example**:
```python
# List all priorities
result = pm.roadmap(action="list", status="In Progress")

# Get priority details
result = pm.roadmap(action="details", priority_id="PRIORITY-28")

# Update priority
result = pm.roadmap(action="update", priority_id="PRIORITY-28", metadata={
    "assignee": "code_developer",
    "estimated_completion": "2025-11-15"
})

# Check status
result = pm.roadmap(action="status", priority_id="PRIORITY-28")
```

**Parameters**:
- `action` (str, required): Action to perform
- `status` (str, optional): Filter by status (e.g., "In Progress", "Complete")
- `priority_id` (str, optional): Priority identifier
- `metadata` (dict, optional): Metadata to update

---

#### command: `status`

**Description**: Developer status and notifications

**Actions**:
- `developer` - Get developer status
- `notifications` - Get all notifications
- `read` - Mark notification as read

**Example**:
```python
# Get developer status
result = pm.status(action="developer")

# Get notifications
result = pm.status(action="notifications")

# Mark notification as read
result = pm.status(action="read", notification_id=42)
```

---

#### command: `dependencies`

**Description**: Dependency management and validation

**Actions**:
- `check` - Check if dependency is approved
- `add` - Add new dependency
- `list` - List all dependencies

**Example**:
```python
# Check dependency approval
result = pm.dependencies(action="check", package_name="numpy")

# Add new dependency (requires pre-approval)
result = pm.dependencies(action="add", package_name="pandas", version="2.0.0")

# List dependencies
result = pm.dependencies(action="list")
```

---

#### command: `github`

**Description**: GitHub PR and issue monitoring

**Actions**:
- `monitor_pr` - Monitor PR status
- `track_issue` - Track GitHub issue
- `sync` - Sync GitHub status

**Example**:
```python
# Monitor PR
result = pm.github(action="monitor_pr", pr_number=42)

# Track issue
result = pm.github(action="track_issue", issue_number=15)

# Sync status
result = pm.github(action="sync")
```

---

#### command: `stats`

**Description**: Project statistics and metrics

**Actions**:
- `roadmap` - Roadmap statistics
- `feature` - Feature statistics
- `spec` - Specification statistics
- `audit` - Audit trail

**Example**:
```python
# Get ROADMAP stats
result = pm.stats(action="roadmap")

# Get feature stats
result = pm.stats(action="feature")

# Get spec stats
result = pm.stats(action="spec")

# Get audit trail
result = pm.stats(action="audit", days=30)
```

---

### 2. Code Developer (6 Commands)

**Role**: Implementation, testing, and quality assurance

#### command: `implement`

**Description**: Full implementation lifecycle management

**Actions**:
- `claim` - Claim a priority to work on
- `load` - Load technical specification
- `update_status` - Update implementation status
- `record_commit` - Record a git commit
- `complete` - Mark implementation complete

**Example**:
```python
# Claim priority
result = cd.implement(action="claim", priority_id="PRIORITY-10")

# Load spec
result = cd.implement(action="load", priority_id="PRIORITY-10")

# Update status
result = cd.implement(action="update_status", priority_id="PRIORITY-10",
                      status="in_progress")

# Record commit
result = cd.implement(action="record_commit", commit_sha="abc123def456",
                      commit_message="feat: Implement authentication")

# Complete implementation
result = cd.implement(action="complete", priority_id="PRIORITY-10")
```

---

#### command: `test`

**Description**: Testing operations and coverage

**Actions**:
- `run` - Run test suite
- `fix` - Debug and fix test failures
- `coverage` - Generate coverage report

**Example**:
```python
# Run tests
result = cd.test(action="run", path="tests/")

# Fix failures
result = cd.test(action="fix", test_file="tests/test_auth.py")

# Coverage report
result = cd.test(action="coverage", min_percentage=80)
```

---

#### command: `git`

**Description**: Git operations (commits and PRs)

**Actions**:
- `commit` - Create git commit
- `push` - Push to remote
- `create_pr` - Create pull request

**Example**:
```python
# Create commit
result = cd.git(action="commit", message="feat: Add authentication")

# Push to remote
result = cd.git(action="push", branch="feature/auth")

# Create PR
result = cd.git(action="create_pr", title="Add Authentication",
               description="Implements user authentication")
```

---

#### command: `review`

**Description**: Code review requests and tracking

**Actions**:
- `request` - Request code review
- `status` - Check review status
- `feedback` - Get review feedback

**Example**:
```python
# Request review
result = cd.review(action="request", commit_sha="abc123",
                  files=["auth.py", "test_auth.py"])

# Check status
result = cd.review(action="status", review_id=42)

# Get feedback
result = cd.review(action="feedback", review_id=42)
```

---

#### command: `quality`

**Description**: Code quality checks and analysis

**Actions**:
- `check` - Run quality checks
- `lint` - Run linter
- `analyze` - Analyze code complexity

**Example**:
```python
# Run quality checks
result = cd.quality(action="check", path="coffee_maker/")

# Run linter
result = cd.quality(action="lint", fix=True)

# Analyze complexity
result = cd.quality(action="analyze", file="coffee_maker/auth.py")
```

---

#### command: `config`

**Description**: Configuration management

**Actions**:
- `update` - Update configuration
- `validate` - Validate configuration
- `get` - Get configuration

**Example**:
```python
# Get configuration
result = cd.config(action="get", key="implementation_timeout")

# Update configuration
result = cd.config(action="update", key="implementation_timeout", value=3600)

# Validate configuration
result = cd.config(action="validate")
```

---

### 3. Architect (5 Commands)

**Role**: Technical design, specifications, and architecture

#### command: `spec`

**Description**: Specification management

**Actions**:
- `create` - Create new technical specification
- `update` - Update existing specification
- `validate` - Validate specification completeness
- `link` - Link spec to priority

**Example**:
```python
# Create spec
result = arch.spec(action="create", title="User Authentication",
                  priority_id="PRIORITY-10")

# Update spec
result = arch.spec(action="update", spec_id="SPEC-100",
                  content="Updated spec content")

# Validate spec
result = arch.spec(action="validate", spec_id="SPEC-100")

# Link to priority
result = arch.spec(action="link", spec_id="SPEC-100",
                  priority_id="PRIORITY-10")
```

---

#### command: `task`

**Description**: Implementation task management

**Actions**:
- `create` - Create implementation tasks
- `define_deps` - Define task dependencies
- `update_status` - Update task status
- `assign` - Assign task to developer

**Example**:
```python
# Create tasks
result = arch.task(action="create", spec_id="SPEC-100",
                  tasks=["Database schema", "API endpoints"])

# Define dependencies
result = arch.task(action="define_deps", task_id="TASK-1",
                  depends_on=["TASK-0"])

# Update status
result = arch.task(action="update_status", task_id="TASK-1",
                  status="in_progress")
```

---

#### command: `adr`

**Description**: Architecture Decision Records

**Actions**:
- `create` - Create new ADR
- `update` - Update ADR
- `list` - List ADRs
- `archive` - Archive ADR

**Example**:
```python
# Create ADR
result = arch.adr(action="create", title="Use SQLite for storage",
                 decision="Store all data in SQLite")

# Update ADR
result = arch.adr(action="update", adr_id=1, status="accepted")

# List ADRs
result = arch.adr(action="list")

# Archive ADR
result = arch.adr(action="archive", adr_id=1)
```

---

#### command: `guideline`

**Description**: Architecture guidelines and standards

**Actions**:
- `create` - Create new guideline
- `update` - Update guideline
- `list` - List guidelines
- `enforce` - Enforce guideline compliance

**Example**:
```python
# Create guideline
result = arch.guideline(action="create", name="Error Handling",
                       description="Standard error handling patterns")

# Update guideline
result = arch.guideline(action="update", guideline_id=1,
                       description="Updated description")

# List guidelines
result = arch.guideline(action="list")

# Enforce compliance
result = arch.guideline(action="enforce", guideline_id=1,
                       path="coffee_maker/")
```

---

#### command: `cfr`

**Description**: Critical Functional Requirements management

**Actions**:
- `create` - Create CFR
- `update` - Update CFR
- `validate` - Validate CFR compliance
- `list` - List CFRs

**Example**:
```python
# Create CFR
result = arch.cfr(action="create", number=14,
                 title="Database Tracing",
                 description="All activities in SQLite database")

# Update CFR
result = arch.cfr(action="update", cfr_id="CFR-014",
                 status="active")

# Validate compliance
result = arch.cfr(action="validate", cfr_id="CFR-014", path="coffee_maker/")
```

---

### 4. Code Reviewer (6 Commands)

**Role**: Automated code review and quality assurance

#### command: `review`

**Description**: Code review operations

**Actions**:
- `analyze` - Analyze code quality
- `check_style` - Check style compliance
- `check_architecture` - Check architecture compliance
- `check_coverage` - Check test coverage
- `generate_report` - Generate review report

**Example**:
```python
# Analyze code quality
result = cr.review(action="analyze", commit_sha="abc123")

# Check style
result = cr.review(action="check_style", file="coffee_maker/auth.py")

# Check architecture
result = cr.review(action="check_architecture", path="coffee_maker/")

# Check coverage
result = cr.review(action="check_coverage", min_percentage=80)

# Generate report
result = cr.review(action="generate_report", commit_sha="abc123")
```

---

#### command: `detect`

**Description**: Issue and vulnerability detection

**Actions**:
- `new_commits` - Detect new commits
- `security` - Security scan
- `complexity` - Analyze complexity
- `issues` - Detect issues

**Example**:
```python
# Detect new commits
result = cr.detect(action="new_commits", branch="roadmap")

# Security scan
result = cr.detect(action="security", path="coffee_maker/")

# Complexity analysis
result = cr.detect(action="complexity", file="coffee_maker/auth.py")

# Issue detection
result = cr.detect(action="issues", path="coffee_maker/")
```

---

#### command: `validate`

**Description**: Validation checks

**Actions**:
- `dod` - Validate Definition of Done
- `type_hints` - Validate type hints
- `documentation` - Validate documentation
- `tests` - Validate tests

**Example**:
```python
# Validate DoD
result = cr.validate(action="dod", priority_id="PRIORITY-10")

# Validate type hints
result = cr.validate(action="type_hints", path="coffee_maker/")

# Validate documentation
result = cr.validate(action="documentation", priority_id="PRIORITY-10")

# Validate tests
result = cr.validate(action="tests", path="tests/")
```

---

#### command: `notify`

**Description**: Notifications and alerts

**Actions**:
- `architect` - Notify architect
- `developer` - Notify developer
- `team` - Notify team

**Example**:
```python
# Notify architect
result = cr.notify(action="architect", message="Review needed",
                  commit_sha="abc123")

# Notify developer
result = cr.notify(action="developer", message="Changes requested",
                  commit_sha="abc123")

# Notify team
result = cr.notify(action="team", message="Review complete",
                  commit_sha="abc123")
```

---

#### command: `track`

**Description**: Issue tracking and metrics

**Actions**:
- `metrics` - Track review metrics
- `quality_score` - Generate quality score
- `issue_resolution` - Track issue resolution

**Example**:
```python
# Track metrics
result = cr.track(action="metrics", period="week")

# Quality score
result = cr.track(action="quality_score", commit_sha="abc123")

# Issue resolution
result = cr.track(action="issue_resolution", issue_id=42)
```

---

### 5. Orchestrator (5 Commands)

**Role**: Agent coordination and work distribution

#### command: `agents`

**Description**: Agent lifecycle management

**Actions**:
- `spawn` - Spawn new agent
- `kill` - Kill running agent
- `restart` - Restart agent
- `monitor_lifecycle` - Monitor lifecycle
- `handle_errors` - Handle errors

**Example**:
```python
# Spawn agent
result = orch.agents(action="spawn", agent_type="code_developer",
                    task_id="TASK-31-1")

# Kill agent
result = orch.agents(action="kill", agent_id=1)

# Restart agent
result = orch.agents(action="restart", agent_id=1)

# Monitor lifecycle
result = orch.agents(action="monitor_lifecycle", agent_id=1)

# Handle errors
result = orch.agents(action="handle_errors", agent_id=1)
```

---

#### command: `orchestrate`

**Description**: Work coordination and scheduling

**Actions**:
- `coordinate_deps` - Coordinate dependencies
- `find_work` - Find available work
- `create_tasks` - Create parallel tasks
- `detect_deadlocks` - Detect deadlocks

**Example**:
```python
# Coordinate dependencies
result = orch.orchestrate(action="coordinate_deps")

# Find work
result = orch.orchestrate(action="find_work", status="ready")

# Create tasks
result = orch.orchestrate(action="create_tasks", priority_id="PRIORITY-10")

# Detect deadlocks
result = orch.orchestrate(action="detect_deadlocks")
```

---

#### command: `worktree`

**Description**: Git worktree operations

**Actions**:
- `create` - Create worktree
- `cleanup` - Clean up worktrees
- `merge` - Merge completed work

**Example**:
```python
# Create worktree
result = orch.worktree(action="create", task_id="TASK-31-1",
                      branch="roadmap-implementation_task-TASK-31-1")

# Cleanup
result = orch.worktree(action="cleanup", task_id="TASK-31-1")

# Merge
result = orch.worktree(action="merge", task_id="TASK-31-1")
```

---

#### command: `messages`

**Description**: Inter-agent communication

**Actions**:
- `route` - Route message to agent
- `send` - Send message
- `receive` - Receive messages

**Example**:
```python
# Route message
result = orch.messages(action="route", from_agent="code_developer",
                      to_agent="architect", message="Need spec")

# Send message
result = orch.messages(action="send", to_agent="code_reviewer",
                      content="Review ready")

# Receive messages
result = orch.messages(action="receive", agent_id=1)
```

---

#### command: `monitor`

**Description**: Resource usage and activity monitoring

**Actions**:
- `resources` - Monitor resource usage
- `activity_summary` - Generate activity summary

**Example**:
```python
# Monitor resources
result = orch.monitor(action="resources", agent_id=1)

# Activity summary
result = orch.monitor(action="activity_summary", period="day")
```

---

### 6. Assistant (4 Commands)

**Role**: Documentation, demo creation, and intelligent assistance

#### command: `docs`

**Description**: Documentation operations

**Actions**:
- `generate` - Generate documentation
- `update` - Update documentation
- `validate` - Validate documentation

**Example**:
```python
# Generate docs
result = asst.docs(action="generate", priority_id="PRIORITY-10",
                  format="markdown")

# Update docs
result = asst.docs(action="update", file="README.md",
                  content="Updated content")

# Validate docs
result = asst.docs(action="validate", priority_id="PRIORITY-10")
```

---

#### command: `demo`

**Description**: Demo creation and validation

**Actions**:
- `create` - Create demo
- `record` - Record demo session
- `validate` - Validate demo output

**Example**:
```python
# Create demo
result = asst.demo(action="create", priority_id="PRIORITY-10",
                  duration=300)

# Record session
result = asst.demo(action="record", demo_id=1)

# Validate output
result = asst.demo(action="validate", demo_id=1)
```

---

#### command: `classify`

**Description**: Request classification and routing

**Actions**:
- `classify` - Classify user request
- `route` - Route to agent
- `fallback` - Handle fallback

**Example**:
```python
# Classify request
result = asst.classify(action="classify", request="Create new spec")

# Route to agent
result = asst.classify(action="route", request="Create new spec",
                      agent="architect")

# Fallback
result = asst.classify(action="fallback", request="Unknown")
```

---

#### command: `track`

**Description**: Bug tracking and status management

**Actions**:
- `report_bug` - Report bug
- `track_status` - Track bug status
- `link_priority` - Link bug to priority

**Example**:
```python
# Report bug
result = asst.track(action="report_bug", title="Authentication fails",
                   description="Users can't login")

# Track status
result = asst.track(action="track_status", bug_id=42)

# Link to priority
result = asst.track(action="link_priority", bug_id=42,
                   priority_id="PRIORITY-10")
```

---

### 7. User Listener (3 Commands)

**Role**: User interface and request handling

#### command: `route`

**Description**: Route user request to appropriate agent

**Actions**:
- `classify` - Classify intent
- `route` - Route to agent
- `handle_fallback` - Handle fallback

**Example**:
```python
# Classify intent
result = ul.route(action="classify", request="What's the project status?")

# Route to agent
result = ul.route(action="route", request="What's the project status?",
                 agent="project_manager")

# Fallback
result = ul.route(action="handle_fallback", request="Unknown request")
```

---

#### command: `session`

**Description**: Session management

**Actions**:
- `start` - Start session
- `update` - Update session context
- `track` - Track conversation

**Example**:
```python
# Start session
result = ul.session(action="start", user_id="user123")

# Update context
result = ul.session(action="update", context={"priority": "PRIORITY-10"})

# Track conversation
result = ul.session(action="track", message="User asked about status")
```

---

#### command: `context`

**Description**: Context management and entity extraction

**Actions**:
- `extract` - Extract entities
- `update` - Update context
- `get` - Get context

**Example**:
```python
# Extract entities
result = ul.context(action="extract", message="Implement PRIORITY-10")

# Update context
result = ul.context(action="update", key="priority",
                   value="PRIORITY-10")

# Get context
result = ul.context(action="get")
```

---

### 8. UX Design Expert (3 Commands)

**Role**: UI/UX design and component specification

#### command: `design`

**Description**: UI/UX design operations

**Actions**:
- `create_spec` - Create component spec
- `create_tokens` - Create design tokens
- `generate_config` - Generate Tailwind config

**Example**:
```python
# Create component spec
result = ux.design(action="create_spec", component="Button",
                  props=["size", "color", "disabled"])

# Create design tokens
result = ux.design(action="create_tokens", colors=["primary", "secondary"])

# Generate Tailwind config
result = ux.design(action="generate_config", theme="light")
```

---

#### command: `component`

**Description**: Component library management

**Actions**:
- `manage` - Manage components
- `review` - Review implementation
- `validate_accessibility` - Validate accessibility

**Example**:
```python
# Manage components
result = ux.component(action="manage", component="Button",
                     version="1.0.0")

# Review implementation
result = ux.component(action="review", file="Button.tsx")

# Validate accessibility
result = ux.component(action="validate_accessibility", component="Button")
```

---

#### command: `improve`

**Description**: UI improvement suggestions

**Actions**:
- `suggest` - Suggest improvements
- `track_debt` - Track design debt
- `configure_theme` - Configure theme

**Example**:
```python
# Suggest improvements
result = ux.improve(action="suggest", screen="Dashboard")

# Track design debt
result = ux.improve(action="track_debt", issue="Color inconsistency")

# Configure theme
result = ux.improve(action="configure_theme", theme="dark_mode")
```

---

## Migration Guide: Old to New

### Before (Old Style)

```python
# Many commands scattered across the codebase
pm.check_priority_status("PRIORITY-28")
pm.get_priority_details("PRIORITY-28")
pm.list_all_priorities(status="blocked")

cd.claim_priority("PRIORITY-10")
cd.run_tests("tests/")
cd.commit_code("feat: Add auth")
```

### After (New Style)

```python
# Consolidated commands with action routing
pm.roadmap(action="status", priority_id="PRIORITY-28")
pm.roadmap(action="details", priority_id="PRIORITY-28")
pm.roadmap(action="list", status="blocked")

cd.implement(action="claim", priority_id="PRIORITY-10")
cd.test(action="run", path="tests/")
cd.git(action="commit", message="feat: Add auth")
```

### Automatic Migration

Old commands still work! The system automatically aliases them to new consolidated commands:

```python
# This still works (with deprecation warning)
pm.check_priority_status("PRIORITY-28")

# But you should update to
pm.roadmap(action="status", priority_id="PRIORITY-28")
```

Use the migration tool to find and update old commands in your codebase:

```python
from coffee_maker.commands.consolidated.migration import (
    CodeMigrator,
    find_legacy_commands,
    generate_migration_report
)

# Find old commands
findings = find_legacy_commands("coffee_maker/")
print(f"Found {len(findings)} legacy commands")

# Generate migration report
report = generate_migration_report("coffee_maker/")
print(report)

# Run migrator
migrator = CodeMigrator("coffee_maker/")
migrator.migrate_all()
```

---

## Command Invocation Examples

### Python API

```python
from coffee_maker.commands.consolidated import ProjectManagerCommands

pm = ProjectManagerCommands()

# List priorities
result = pm.roadmap(action="list", status="In Progress")
print(result)

# Get priority details
details = pm.roadmap(action="details", priority_id="PRIORITY-10")
print(f"Priority: {details['title']}")
print(f"Status: {details['status']}")
```

### CLI

```bash
# Via CLI (if available)
poetry run project-manager roadmap list --status "In Progress"
poetry run project-manager roadmap details --priority-id PRIORITY-10

poetry run code-developer implement claim --priority-id PRIORITY-10
poetry run code-developer test run --path tests/
```

### Database

```python
from coffee_maker.database.domain_wrapper import DomainWrapper

db = DomainWrapper("data/coffee_maker.db")

# Commands work with database
pm = ProjectManagerCommands("data/coffee_maker.db")
result = pm.roadmap(action="list")
```

---

## Best Practices

1. **Use Action Parameter**: Always specify the `action` parameter
   ```python
   # Good
   pm.roadmap(action="list", status="In Progress")

   # Avoid
   pm.roadmap()  # What action to perform?
   ```

2. **Use Descriptive Parameters**: Be explicit about what you're doing
   ```python
   # Good
   cd.implement(action="claim", priority_id="PRIORITY-10")

   # Avoid
   cd.implement(action="claim", id="PRIORITY-10")
   ```

3. **Check Return Values**: Commands return result dictionaries
   ```python
   result = pm.roadmap(action="list")
   if result.get("success"):
       priorities = result.get("data", [])
   else:
       error = result.get("error")
   ```

4. **Handle Errors**: Always check for errors
   ```python
   try:
       result = cd.implement(action="claim", priority_id="INVALID")
       if not result.get("success"):
           print(f"Error: {result.get('error')}")
   except Exception as e:
       print(f"Exception: {e}")
   ```

---

## Related Documentation

- **API Reference**: See `docs/CONSOLIDATED_COMMANDS_API_REFERENCE.md` for detailed parameters
- **Migration Guide**: See consolidated command module for migration helpers
- **Architecture**: See `.claude/CLAUDE.md` for architectural overview

---

**Last Updated**: 2025-10-27
**Version**: 2.0 (Consolidated Architecture)
