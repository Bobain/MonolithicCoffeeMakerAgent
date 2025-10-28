# Command Quick Reference - Consolidated Architecture

**Quick lookup for all 36 consolidated commands across 8 agents.**

---

## project_manager (5 commands)

```python
from coffee_maker.agents.project_manager import ProjectManager
pm = ProjectManager()

# 1. roadmap - All ROADMAP operations
pm.roadmap(action="list", status="blocked")             # List priorities
pm.roadmap(action="details", priority_id="PRIORITY-28") # Get details
pm.roadmap(action="update", priority_id="...", metadata={...})  # Update
pm.roadmap(action="status", priority_id="PRIORITY-28")  # Check status

# 2. status - Developer status and notifications
pm.status(action="developer")                    # Get developer status
pm.status(action="notifications", level="error") # List notifications
pm.status(action="read", notification_id=123)    # Mark read

# 3. dependencies - Dependency management
pm.dependencies(action="check", package="pytest")      # Check approved
pm.dependencies(action="add", package="pytest", version="7.4.0")  # Add
pm.dependencies(action="list")                         # List all

# 4. github - GitHub integration
pm.github(action="monitor_pr", pr_number=123)    # Monitor PR
pm.github(action="track_issue", issue_number=45) # Track issue
pm.github(action="sync")                         # Sync status

# 5. stats - Project statistics
pm.stats(action="roadmap")                # ROADMAP stats
pm.stats(action="feature")                # Feature stats
pm.stats(action="spec")                   # Spec stats
pm.stats(action="audit", days=7)          # Audit trail
```

---

## architect (5 commands)

```python
from coffee_maker.agents.architect import Architect
arch = Architect()

# 1. spec - Technical specification operations
arch.spec(action="create", title="...", content={...})   # Create spec
arch.spec(action="update", spec_id="SPEC-102", ...)      # Update spec
arch.spec(action="approve", spec_id="SPEC-102")          # Approve spec
arch.spec(action="deprecate", spec_id="SPEC-102")        # Deprecate spec
arch.spec(action="link", spec_id="SPEC-102", priority_id="...")  # Link

# 2. tasks - Task decomposition and management
arch.tasks(action="decompose", spec_id="SPEC-102")       # Decompose to tasks
arch.tasks(action="update_order", task_id="...", order=2) # Update order
arch.tasks(action="merge_branch", branch="feature-x")    # Merge branch

# 3. documentation - ADRs, guidelines, style guides
arch.documentation(action="create_adr", title="...", content="...")  # ADR
arch.documentation(action="update_guidelines", guideline_id="...")   # Guideline
arch.documentation(action="update_styleguide", section="...")        # Style guide

# 4. review - Architecture validation and review
arch.review(action="validate_architecture", spec_id="SPEC-102")  # Validate
arch.review(action="design_api", spec_id="SPEC-102")             # Design API

# 5. dependencies - Technical dependency management
arch.dependencies(action="check", package="redis")       # Check
arch.dependencies(action="add", package="redis", ...)    # Add
arch.dependencies(action="evaluate", package="redis")    # Evaluate
```

---

## code_developer (6 commands)

```python
from coffee_maker.agents.code_developer import CodeDeveloper
dev = CodeDeveloper()

# 1. implement - Full implementation lifecycle
dev.implement(action="claim", priority_id="PRIORITY-28")   # Claim work
dev.implement(action="load", priority_id="PRIORITY-28")    # Load spec
dev.implement(action="update_status", status="in_progress") # Update status
dev.implement(action="record_commit", commit="abc123")      # Record commit
dev.implement(action="complete", priority_id="PRIORITY-28") # Mark complete

# 2. test - Testing operations
dev.test(action="run")                          # Run test suite
dev.test(action="fix", test_name="test_auth")   # Fix failing test
dev.test(action="coverage")                     # Generate coverage

# 3. git - Git operations
dev.git(action="commit", message="feat: Add auth")  # Create commit
dev.git(action="create_pr", title="Add auth", body="...")  # Create PR

# 4. review - Code review operations
dev.review(action="request", commit="abc123")   # Request review
dev.review(action="track", review_id=456)       # Track review status

# 5. quality - Code quality operations
dev.quality(action="pre_commit")                # Run pre-commit hooks
dev.quality(action="metrics")                   # Track metrics
dev.quality(action="lint")                      # Run linter

# 6. config - Configuration management
dev.config(action="update_claude", config={...})  # Update Claude config
dev.config(action="update_config", file="...", content={...})  # Update config
```

---

## code_reviewer (4 commands)

```python
from coffee_maker.agents.code_reviewer import CodeReviewer
reviewer = CodeReviewer()

# 1. review - Complete review operations
reviewer.review(action="generate_report", commit="abc123")  # Generate report
reviewer.review(action="score", commit="abc123")            # Quality score
reviewer.review(action="validate_dod", commit="abc123")     # DoD compliance

# 2. analyze - All analysis types (parameterized)
reviewer.analyze(type="style", file="...")        # Style analysis
reviewer.analyze(type="security", file="...")     # Security scan
reviewer.analyze(type="complexity", file="...")   # Complexity analysis
reviewer.analyze(type="coverage", file="...")     # Coverage check
reviewer.analyze(type="types", file="...")        # Type hints check
reviewer.analyze(type="architecture", file="...")  # Architecture compliance
reviewer.analyze(type="docs", file="...")         # Documentation review

# 3. monitor - Commit and issue tracking
reviewer.monitor(action="detect_commits")         # Detect new commits
reviewer.monitor(action="track_issues")           # Track issue resolution

# 4. notify - Send notifications
reviewer.notify(agent="architect", message="...")       # Notify architect
reviewer.notify(agent="code_developer", message="...")  # Notify developer
```

---

## orchestrator (5 commands)

```python
from coffee_maker.agents.orchestrator import Orchestrator
orch = Orchestrator()

# 1. agents - Agent lifecycle management
orch.agents(action="spawn", agent_type="code_developer")  # Spawn agent
orch.agents(action="kill", agent_id="...")                # Kill agent
orch.agents(action="restart", agent_id="...")             # Restart agent
orch.agents(action="monitor_lifecycle")                   # Monitor all agents
orch.agents(action="handle_errors", agent_id="...")       # Handle errors

# 2. orchestrate - Work coordination
orch.orchestrate(action="coordinate_deps")        # Coordinate dependencies
orch.orchestrate(action="find_work")              # Find available work
orch.orchestrate(action="create_tasks")           # Create parallel tasks
orch.orchestrate(action="detect_deadlocks")       # Detect deadlocks

# 3. worktree - Git worktree operations
orch.worktree(action="create", task_id="TASK-31-1")  # Create worktree
orch.worktree(action="cleanup", task_id="...")        # Cleanup worktree
orch.worktree(action="merge", task_id="...")          # Merge work

# 4. messages - Inter-agent communication
orch.messages(action="route", from_agent="...", to_agent="...", message="...")
orch.messages(action="send", agent_id="...", message="...")
orch.messages(action="receive", agent_id="...")

# 5. monitor - Resources and activity
orch.monitor(action="resources")                  # Resource usage
orch.monitor(action="activity_summary", days=7)   # Activity summary
```

---

## assistant (4 commands)

```python
from coffee_maker.agents.assistant import Assistant
asst = Assistant()

# 1. demo - Demo creation and management
asst.demo(action="create", name="...")           # Create demo
asst.demo(action="record", demo_id="...")        # Record session
asst.demo(action="validate", demo_id="...")      # Validate output

# 2. bug - Bug reporting and tracking
asst.bug(action="report", title="...", description="...")  # Report bug
asst.bug(action="track_status", bug_id="...")              # Track status
asst.bug(action="link_to_priority", bug_id="...", priority_id="...")  # Link

# 3. delegate - Intelligent request routing
asst.delegate(action="classify", request="...")   # Classify request
asst.delegate(action="route", request="...")      # Route to agent
asst.delegate(action="monitor", request_id="...") # Monitor delegation

# 4. docs - Documentation generation
asst.docs(action="generate", spec_id="...")      # Generate docs
asst.docs(action="update_readme", section="...")  # Update README
```

---

## user_listener (3 commands)

```python
from coffee_maker.agents.user_listener import UserListener
ul = UserListener()

# 1. understand - Intent/entity extraction
ul.understand(action="classify_intent", text="...")     # Classify intent
ul.understand(action="extract_entities", text="...")    # Extract entities
ul.understand(action="determine_agent", text="...")     # Determine agent

# 2. route - Request routing
ul.route(action="route_request", text="...", agent="...")  # Route request
ul.route(action="queue", request="...")                    # Queue for agent
ul.route(action="handle_fallback", request="...")          # Handle fallback

# 3. conversation - Conversation management
ul.conversation(action="track", conversation_id="...")     # Track conversation
ul.conversation(action="update_context", context={...})    # Update context
ul.conversation(action="manage_session", session_id="...")  # Manage session
```

---

## ux_design_expert (4 commands)

```python
from coffee_maker.agents.ux_design_expert import UXDesignExpert
ux = UXDesignExpert()

# 1. design - UI/component specifications
ux.design(action="generate_ui_spec", feature="...")        # UI spec
ux.design(action="create_component_spec", component="...")  # Component spec

# 2. components - Component library and design system
ux.components(action="manage_library")                     # Manage library
ux.components(action="tailwind_config", config={...})      # Tailwind config
ux.components(action="design_tokens", tokens={...})        # Design tokens
ux.components(action="chart_theme", theme={...})           # Chart theme

# 3. review - UI review and accessibility
ux.review(action="review_implementation", feature="...")   # Review UI
ux.review(action="suggest_improvements", feature="...")    # Suggest improvements
ux.review(action="validate_accessibility", feature="...")   # Accessibility check

# 4. debt - Design debt management
ux.debt(action="track", debt_id="...")                     # Track debt
ux.debt(action="prioritize")                               # Prioritize debt
ux.debt(action="remediate", debt_id="...")                 # Remediate debt
```

---

## Summary

| Agent | Commands | Most Used |
|-------|----------|-----------|
| project_manager | 5 | `roadmap`, `status` |
| architect | 5 | `spec`, `tasks`, `review` |
| code_developer | 6 | `implement`, `test`, `git` |
| code_reviewer | 4 | `review`, `analyze` |
| orchestrator | 5 | `agents`, `orchestrate` |
| assistant | 4 | `delegate`, `docs` |
| user_listener | 3 | `understand`, `route` |
| ux_design_expert | 4 | `design`, `review` |
| **TOTAL** | **36** | |

---

## Pattern

All commands follow the same pattern:

```python
agent.command(action="operation", **params)
```

**Benefits**:
- ✅ Consistent API across all agents
- ✅ Self-documenting (action names describe purpose)
- ✅ Easy to discover (fewer commands to remember)
- ✅ Easy to extend (add new actions)

---

**Last Updated**: 2025-10-27
**Status**: ✅ Complete
**Source**: SPEC-102 through SPEC-114
