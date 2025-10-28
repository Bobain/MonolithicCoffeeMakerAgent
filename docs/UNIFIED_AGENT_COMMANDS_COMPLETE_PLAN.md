# Unified Agent Commands & Database Domain Architecture - Complete Implementation Plan

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current System Analysis](#current-system-analysis)
3. [Agent Responsibilities Matrix](#agent-responsibilities-matrix)
4. [Database Domain Architecture](#database-domain-architecture)
5. [Command Structure Design](#command-structure-design)
6. [Implementation Components](#implementation-components)
7. [Complete Command Registry](#complete-command-registry)
8. [Implementation Timeline](#implementation-timeline)
9. [Migration Strategy](#migration-strategy)
10. [Success Criteria](#success-criteria)

---

## 1. Executive Summary

### Overview

This document presents a complete plan to transform the MonolithicCoffeeMaker agent system from scattered, inline operations to a structured, command-driven architecture with enforced database domain boundaries.

### Key Objectives

1. **Extract all agent responsibilities** into discrete, documented commands
2. **Enforce database domain boundaries** using permission wrappers
3. **Reuse existing infrastructure** - no schema changes, wrap existing classes
4. **Document both implemented and planned features** from introspection and prompts
5. **Create clear audit trails** for all operations

### Approach

- **Evolutionary, not revolutionary** - Enhance existing system rather than replace
- **Use existing tables** - 30+ tables already well-structured
- **Wrap existing classes** - RoadmapDatabase and others remain intact
- **Progressive rollout** - One agent at a time, validated at each step

---

## 2. Current System Analysis

### 2.1 Database Structure (From Analysis)

#### Existing Databases
```
data/
├── roadmap.db         # Main database (30+ tables)
├── metrics.db         # Performance metrics (5 tables)
├── notifications.db   # Notification system (2 tables)
└── code_developer.db  # Developer tracking (empty)
```

#### Key Tables and Ownership

| Database | Table | Owner Agent | Purpose |
|----------|-------|-------------|---------|
| roadmap.db | roadmap_priority | project_manager | Priorities and user stories |
| roadmap.db | roadmap_metadata | project_manager | ROADMAP header/footer |
| roadmap.db | specs_specification | architect | Technical specifications |
| roadmap.db | specs_task | architect | Implementation tasks |
| roadmap.db | review_commit | code_developer | Commit tracking |
| roadmap.db | review_code_review | code_reviewer | Review reports |
| roadmap.db | agent_lifecycle | orchestrator | Agent process tracking |
| roadmap.db | orchestrator_task | orchestrator | Parallel task management |
| roadmap.db | notifications | Shared | Inter-agent communication |
| roadmap.db | system_audit | Shared | System-wide audit trail |

### 2.2 Existing Access Control

```python
# RoadmapDatabase already has permission control
class RoadmapDatabase:
    def __init__(self, db_path, agent_name="unknown"):
        self.agent_name = agent_name
        self.can_write = agent_name == "project_manager"
```

### 2.3 Documented Workflows (From Introspection)

#### Priority Implementation Flow
```
1. project_manager: Parse ROADMAP.md → INSERT roadmap_priority
2. architect: Query unspecified priorities → CREATE specs_specification
3. code_developer: Query ready priorities → UPDATE status → Implement
4. code_reviewer: Detect commits → CREATE review_code_review
5. project_manager: Verify DoD → Mark complete
```

---

## 3. Agent Responsibilities Matrix

### 3.1 Complete Responsibility Mapping

#### Legend
- ✅ = Documented in introspection (implemented)
- 🆕 = Found in agent prompts (planned/partial)

#### ARCHITECT (16 total responsibilities)

**Database Operations** ✅
- Create technical specifications
- Link specs to priorities
- Create implementation tasks
- Define task dependencies

**Additional from Prompts** 🆕
- Generate ADRs (Architectural Decision Records)
- Approve dependencies (three-tier system)
- Update architecture guidelines
- Merge worktree branches
- Review code quality findings
- Create POCs for complex features
- Validate spec completeness
- Update CFRs (Critical Functional Requirements)

#### CODE_DEVELOPER (14 total responsibilities)

**Database Operations** ✅
- Claim priorities for implementation
- Load specifications
- Update implementation status
- Record commits
- Complete implementations
- Request code reviews

**Additional from Prompts** 🆕
- Run test suites
- Fix failing tests
- Create pull requests
- Implement bug fixes
- Track implementation metrics
- Run pre-commit hooks
- Generate test coverage reports
- Update Claude configuration

#### PROJECT_MANAGER (14 total responsibilities)

**Database Operations** ✅
- Parse and sync ROADMAP.md
- Update priority status
- Create notifications
- Process incoming notifications

**Additional from Prompts** 🆕
- Verify DoD with Puppeteer
- Monitor GitHub PRs
- Monitor GitHub issues
- Analyze project health
- Create roadmap reports
- Detect stale priorities
- Strategic planning
- Track bug reports
- Update roadmap metadata
- Send agent-specific notifications

#### CODE_REVIEWER (13 total responsibilities)

**Database Operations** ✅
- Detect new commits
- Generate review reports
- Notify architect

**Additional from Prompts** 🆕
- Check style compliance
- Run security scans
- Analyze complexity
- Check test coverage
- Validate type hints
- Check architecture compliance
- Track issue resolution
- Generate quality scores
- Review documentation
- Validate DoD compliance

#### ORCHESTRATOR (15 total responsibilities)

**Database Operations** ✅
- Find available work
- Create parallel tasks
- Monitor agent lifecycle
- Merge completed work
- Clean up worktrees

**Additional from Prompts** 🆕
- Spawn agent sessions
- Kill stalled agents
- Detect deadlocks
- Auto-restart agents
- Route inter-agent messages
- Monitor resource usage
- Generate activity summaries
- Coordinate dependencies
- Plan parallel execution
- Handle agent errors

#### ASSISTANT (11 total responsibilities)

**Database Operations** ✅
- Answer questions (read-only)

**Additional from Prompts** 🆕
- Create demos with Puppeteer
- Test features interactively
- Detect bugs during demos
- Report bugs comprehensively
- Delegate to specialists
- Explain code
- Search documentation
- Check logs
- Run diagnostics
- Create tutorials

#### USER_LISTENER (9 total responsibilities)

**Database Operations** ✅
- Receive user input

**Additional from Prompts** 🆕
- Classify intent
- Route to agents
- Maintain conversations
- Play sound notifications
- Format responses
- Track sessions
- Show agent status
- Handle commands

#### UX_DESIGN_EXPERT (10 total responsibilities)

**All from Prompts** 🆕
- Design interfaces
- Create component libraries
- Define design tokens
- Configure Highcharts
- Optimize user flows
- Create Tailwind configs
- Design dashboard layouts
- Accessibility audits
- Responsive design
- Create style guides

---

## 4. Database Domain Architecture

### 4.1 Domain Ownership Model

```python
# Table ownership mapping (who can write)
TABLE_OWNERSHIP = {
    # Project Manager domain
    "roadmap_priority": AgentType.PROJECT_MANAGER,
    "roadmap_metadata": AgentType.PROJECT_MANAGER,
    "roadmap_audit": AgentType.PROJECT_MANAGER,

    # Architect domain
    "specs_specification": AgentType.ARCHITECT,
    "specs_task": AgentType.ARCHITECT,
    "specs_task_dependency": AgentType.ARCHITECT,

    # Developer domain
    "review_commit": AgentType.CODE_DEVELOPER,
    "metrics_subtask": AgentType.CODE_DEVELOPER,

    # Reviewer domain
    "review_code_review": AgentType.CODE_REVIEWER,

    # Orchestrator domain
    "agent_lifecycle": AgentType.ORCHESTRATOR,
    "orchestrator_task": AgentType.ORCHESTRATOR,
    "orchestrator_bug": AgentType.ORCHESTRATOR,
    "agent_message": AgentType.ORCHESTRATOR,

    # Shared (all agents can write)
    "notifications": "shared",
    "system_audit": "shared",
}
```

### 4.2 Read Permissions Matrix

```python
READ_PERMISSIONS = {
    AgentType.ARCHITECT: ["roadmap_priority", "specs_*", "review_code_review"],
    AgentType.CODE_DEVELOPER: ["roadmap_priority", "specs_*", "review_commit"],
    AgentType.PROJECT_MANAGER: ["*"],  # Can read everything for monitoring
    AgentType.CODE_REVIEWER: ["specs_*", "review_*", "roadmap_priority"],
    AgentType.ORCHESTRATOR: ["*"],  # Can read everything for coordination
    AgentType.ASSISTANT: ["*"],  # Can read everything for demos
    AgentType.USER_LISTENER: ["roadmap_priority", "notifications"],
    AgentType.UX_DESIGN_EXPERT: ["roadmap_priority", "specs_specification"],
}
```

---

## 5. Command Structure Design

### 5.1 Command Directory Organization

```
.claude/commands/agents/
├── architect/
│   ├── create_spec.md
│   ├── link_spec_to_priority.md
│   ├── create_implementation_tasks.md
│   ├── define_task_dependencies.md
│   ├── generate_adr.md                    🆕
│   ├── approve_dependency.md              🆕
│   ├── update_guidelines.md               🆕
│   └── merge_worktree_branches.md         🆕
│
├── code_developer/
│   ├── claim_priority.md
│   ├── load_spec.md
│   ├── update_implementation_status.md
│   ├── record_commit.md
│   ├── complete_implementation.md
│   ├── request_code_review.md
│   ├── run_test_suite.md                  🆕
│   └── fix_failing_tests.md               🆕
│
├── project_manager/
│   ├── parse_roadmap.md
│   ├── update_priority_status.md
│   ├── create_notification.md
│   ├── process_notifications.md
│   ├── verify_dod_puppeteer.md            🆕
│   ├── monitor_github_prs.md              🆕
│   ├── analyze_project_health.md          🆕
│   └── strategic_planning.md              🆕
│
├── code_reviewer/
│   ├── detect_new_commits.md
│   ├── generate_review_report.md
│   ├── notify_architect.md
│   ├── check_style_compliance.md          🆕
│   ├── run_security_scan.md               🆕
│   ├── analyze_complexity.md              🆕
│   └── validate_dod_compliance.md         🆕
│
├── orchestrator/
│   ├── find_available_work.md
│   ├── create_parallel_tasks.md
│   ├── monitor_agent_lifecycle.md
│   ├── merge_completed_work.md
│   ├── cleanup_worktrees.md
│   ├── spawn_agent_session.md             🆕
│   ├── detect_deadlocks.md                🆕
│   └── auto_restart_agent.md              🆕
│
├── assistant/
│   ├── answer_question.md
│   ├── create_demo.md                     🆕
│   ├── test_feature.md                    🆕
│   ├── detect_bug_during_demo.md          🆕
│   ├── report_bug_comprehensive.md        🆕
│   └── delegate_to_specialist.md          🆕
│
├── user_listener/
│   ├── receive_input.md
│   ├── classify_intent.md                 🆕
│   ├── route_to_agent.md                  🆕
│   ├── maintain_conversation.md           🆕
│   └── play_sound_notification.md         🆕
│
└── ux_design_expert/
    ├── design_interface.md                🆕
    ├── create_component_library.md        🆕
    ├── define_design_tokens.md            🆕
    └── configure_highcharts.md            🆕
```

### 5.2 Command Template Structure

```markdown
---
command: agent.action
agent: architect|code_developer|project_manager|...
action: specific_action_name
tables:
  write: [table1, table2]
  read: [table3, table4]
files:
  write: [path1, path2]
  read: [path3, path4]
required_skills: [skill1, skill2]
required_tools: [git, gh, pytest, puppeteer]
---

# Command: agent.action

## Purpose
Clear, concise description of what this command accomplishes

## Trigger
When this command is executed:
- Event that triggers it
- Condition that requires it
- User action that initiates it

## Input Parameters
```yaml
priority_id: string   # Required - Priority identifier
new_status: string    # Required - New status value
reason: string        # Optional - Reason for change
```

## Database Operations

### Read Operations
```sql
-- Get current state
SELECT * FROM roadmap_priority WHERE id = :priority_id;
```

### Write Operations
```sql
-- Update state
UPDATE roadmap_priority
SET status = :new_status, updated_by = :agent_name
WHERE id = :priority_id;
```

## File Operations
```python
# If files are involved
with open('path/to/file', 'r') as f:
    content = f.read()
```

## External Tool Usage
```bash
# Git operations
git add -A
git commit -m "message"

# GitHub operations
gh pr create --title "Title" --body "Body"

# Test execution
pytest --cov
```

## Required Skills
- **skill1**: How this skill is used in the command
- **skill2**: Purpose of this skill

## Success Criteria
- [ ] Primary objective achieved
- [ ] Database updated correctly
- [ ] Notifications sent if needed
- [ ] Audit trail created

## Error Handling
| Error Type | Cause | Resolution |
|------------|-------|------------|
| PermissionError | Agent lacks write access | Check agent type |
| NotFoundError | Entity doesn't exist | Validate before operation |
| ValidationError | Invalid parameters | Check input constraints |

## Downstream Effects
What happens after success:
- Next command triggered
- Notification sent to X agent
- State transition occurs
- Workflow continues

## Example Usage
```python
# How to invoke this command
command = CommandLoader.load("architect", "create_spec")
result = command.execute({
    "priority_id": "PRIORITY-25",
    "requirements": {...}
})
```
```

---

## 6. Implementation Components

### 6.1 DomainWrapper Class

```python
# coffee_maker/database/domain_wrapper.py
"""
Domain-based access wrapper for existing database classes.
Enforces permissions without changing existing infrastructure.
"""

class DomainWrapper:
    def __init__(self, agent_type: AgentType, db_path: str = "data/roadmap.db"):
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        # Use existing RoadmapDatabase
        self.db = RoadmapDatabase(Path(db_path), agent_name=self.agent_name)
        self.read_tables = READ_PERMISSIONS.get(agent_type, [])

    def can_write(self, table: str) -> bool:
        """Check write permission based on table ownership."""
        ownership = TABLE_OWNERSHIP.get(table)
        return ownership == "shared" or ownership == self.agent_type

    def can_read(self, table: str) -> bool:
        """Check read permission based on agent permissions."""
        return "*" in self.read_tables or table in self.read_tables

    def write(self, table: str, data: Dict[str, Any]) -> Any:
        """Write with permission check."""
        if not self.can_write(table):
            raise PermissionError(f"{self.agent_name} cannot write to {table}")

        # Add tracking
        data["updated_by"] = self.agent_name

        # Use appropriate method based on table
        if table == "roadmap_priority":
            return self._write_roadmap_priority(data)
        else:
            return self._generic_write(table, data)

    def read(self, table: str, conditions: Optional[Dict] = None) -> List[Dict]:
        """Read with permission check."""
        if not self.can_read(table):
            raise PermissionError(f"{self.agent_name} cannot read from {table}")

        if table == "roadmap_priority":
            return self.db.get_all_items()
        else:
            return self._generic_read(table, conditions)

    def send_notification(self, target_agent: str, message: Dict[str, Any]) -> int:
        """Cross-domain communication via notifications."""
        return self._write_notification(target_agent, message)
```

### 6.2 CommandLoader Class

```python
# coffee_maker/commands/command_loader.py
"""
Loads and executes commands from markdown definitions.
"""

import frontmatter
from pathlib import Path

class CommandLoader:
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.db = DomainWrapper(agent_type)
        self.commands = {}
        self._load_commands()

    def _load_commands(self):
        """Load all commands for this agent."""
        command_dir = Path(f".claude/commands/agents/{self.agent_name}")
        for cmd_file in command_dir.glob("*.md"):
            command = self._parse_command(cmd_file)
            self.commands[command.action] = command

    def _parse_command(self, path: Path) -> Command:
        """Parse command from markdown file."""
        with open(path) as f:
            post = frontmatter.load(f)

        return Command(
            name=post['command'],
            agent=post['agent'],
            action=post['action'],
            tables_write=post.get('tables', {}).get('write', []),
            tables_read=post.get('tables', {}).get('read', []),
            required_skills=post.get('required_skills', []),
            content=post.content
        )

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute a command with parameters."""
        if action not in self.commands:
            raise ValueError(f"Unknown command: {action}")

        command = self.commands[action]

        # Load required skills
        for skill_name in command.required_skills:
            skill = load_skill(skill_name)
            # Make skill available to command

        # Validate permissions
        for table in command.tables_write:
            if not self.db.can_write(table):
                raise PermissionError(f"Cannot write to {table}")

        # Execute command logic
        return command.execute(self.db, params)
```

### 6.3 Command Class

```python
# coffee_maker/commands/command.py
"""
Individual command implementation.
"""

class Command:
    def __init__(self, name: str, agent: str, action: str, **kwargs):
        self.name = name
        self.agent = agent
        self.action = action
        self.tables_write = kwargs.get('tables_write', [])
        self.tables_read = kwargs.get('tables_read', [])
        self.required_skills = kwargs.get('required_skills', [])
        self.content = kwargs.get('content', '')

    def execute(self, db: DomainWrapper, params: Dict[str, Any]) -> Any:
        """Execute the command with given parameters."""
        # Command-specific logic here
        # This would be generated from the markdown content

        # Example for update_priority_status
        if self.action == "update_priority_status":
            # Read current status
            items = db.read("roadmap_priority", {"id": params["priority_id"]})
            if not items:
                raise ValueError(f"Priority {params['priority_id']} not found")

            old_status = items[0]["status"]

            # Update status
            db.update("roadmap_priority",
                {"status": params["new_status"]},
                {"id": params["priority_id"]}
            )

            # Send notification if needed
            if params["new_status"] == "📝 Planned" and not items[0].get("spec_id"):
                db.send_notification("architect", {
                    "type": "spec_needed",
                    "priority_id": params["priority_id"]
                })

            return {"success": True, "old_status": old_status}
```

### 6.4 Agent Integration

```python
# Minimal changes to existing agents
class ArchitectAgent:
    def __init__(self):
        self.commands = CommandLoader(AgentType.ARCHITECT)

    def create_spec(self, priority_id: str, requirements: dict):
        """Execute via command instead of inline logic."""
        return self.commands.execute("create_spec", {
            "priority_id": priority_id,
            "requirements": requirements
        })

    # Existing methods remain but delegate to commands
    def old_method_for_compatibility(self):
        # Can still work during transition
        pass
```

---

## 7. Complete Command Registry

### 7.1 Total Command Count by Agent

| Agent | Introspection | Prompts | Total | Priority |
|-------|--------------|---------|-------|----------|
| project_manager | 4 | 10 | 14 | High |
| architect | 4 | 8 | 12 | High |
| code_developer | 6 | 8 | 14 | High |
| code_reviewer | 3 | 10 | 13 | Medium |
| orchestrator | 5 | 10 | 15 | Medium |
| assistant | 1 | 10 | 11 | Low |
| user_listener | 1 | 8 | 9 | Low |
| ux_design_expert | 0 | 10 | 10 | Low |
| **TOTAL** | **24** | **74** | **98** | - |

### 7.2 Skills Required by Commands

#### Critical Skills (Used by multiple agents)
- `technical_specification_handling` - architect, code_developer, code_reviewer
- `roadmap_database_handling` - project_manager, code_developer
- `git_workflow_automation` - code_developer, orchestrator
- `bug_tracking_helper` - assistant, project_manager, code_developer
- `dod_verification` - code_developer, code_reviewer, project_manager

#### Agent-Specific Skills
- `architecture_analysis` - architect only
- `test-failure-analysis` - code_developer only
- `puppeteer_skills` - assistant, project_manager
- `orchestrator_health_monitor` - orchestrator only
- `security_audit_skill` - code_reviewer only

---

## 8. Implementation Timeline

### Phase 1: Foundation (Days 1-3)
**Objective**: Set up core infrastructure

- ✅ Day 1: Finalize DomainWrapper class
- ⏳ Day 2: Create CommandLoader class
- ⏳ Day 3: Create Command class and test framework

**Deliverables**:
- Working permission system
- Command loading mechanism
- Test suite for validation

### Phase 2: Core Agents (Days 4-7)
**Objective**: Implement high-priority agents

- ⏳ Day 4: project_manager commands (14 total)
- ⏳ Day 5: architect commands (12 total)
- ⏳ Day 6: code_developer commands (14 total)
- ⏳ Day 7: Integration testing

**Deliverables**:
- 40 commands implemented
- Core workflow functional
- End-to-end tests passing

### Phase 3: Support Agents (Days 8-11)
**Objective**: Add supporting agent commands

- ⏳ Day 8: code_reviewer commands (13 total)
- ⏳ Day 9: orchestrator commands (15 total)
- ⏳ Day 10: assistant commands (11 total)
- ⏳ Day 11: Integration testing

**Deliverables**:
- 39 additional commands
- Review and orchestration working
- Demo capabilities functional

### Phase 4: UI Agents (Days 12-14)
**Objective**: Complete UI-focused agents

- ⏳ Day 12: user_listener commands (9 total)
- ⏳ Day 13: ux_design_expert commands (10 total)
- ⏳ Day 14: Full system testing

**Deliverables**:
- 19 final commands
- All 98 commands operational
- System fully command-driven

### Phase 5: Validation & Documentation (Days 15-16)
**Objective**: Ensure quality and completeness

- ⏳ Day 15: Performance testing and optimization
- ⏳ Day 16: Documentation and training materials

**Deliverables**:
- Performance benchmarks
- Complete documentation
- Training materials

---

## 9. Migration Strategy

### 9.1 Parallel Operation

During migration, both systems operate:
```python
class TransitionAgent:
    def execute_action(self, action: str, params: dict):
        if FEATURE_FLAG_USE_COMMANDS:
            return self.commands.execute(action, params)
        else:
            return self.legacy_method(params)
```

### 9.2 Agent Migration Order

1. **project_manager** - Well-documented, clear boundaries
2. **architect** - Limited dependencies, clear ownership
3. **code_developer** - Core functionality, well-tested
4. **code_reviewer** - Independent operation
5. **orchestrator** - Complex but isolated
6. **assistant** - Mostly read operations
7. **user_listener** - UI layer, less critical
8. **ux_design_expert** - New functionality

### 9.3 Rollback Plan

Each phase can be rolled back independently:
```python
# Feature flags for each agent
AGENT_COMMAND_FLAGS = {
    "project_manager": True,  # Enable commands
    "architect": False,       # Still using legacy
    # ...
}
```

### 9.4 Validation Checkpoints

After each agent migration:
1. ✅ Permission tests pass
2. ✅ Existing workflows function
3. ✅ Audit trail complete
4. ✅ Performance acceptable
5. ✅ No data corruption

---

## 10. Success Criteria

### 10.1 Technical Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Backward Compatibility | 100% | Existing code still works |
| Command Coverage | 98/98 | All responsibilities mapped |
| Permission Enforcement | 100% | No unauthorized writes |
| Audit Coverage | 100% | All operations logged |
| Performance Impact | <5% | Overhead from wrappers |
| Test Coverage | >90% | Unit and integration tests |

### 10.2 Business Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Debugging Speed | 50% faster | Time to trace issues |
| Onboarding Time | 75% reduction | New developer ramp-up |
| Permission Errors | 90% reduction | Domain violations |
| Documentation | 100% coverage | All commands documented |
| Maintainability | 2x improvement | Change complexity |

### 10.3 Validation Tests

#### Permission Enforcement Test
```python
def test_domain_isolation():
    # Developer cannot write to architect tables
    dev_db = DomainWrapper(AgentType.CODE_DEVELOPER)
    with pytest.raises(PermissionError):
        dev_db.write("specs_specification", {"data": "test"})

    # But can write to own tables
    assert dev_db.write("review_commit", {"data": "test"})
```

#### Command Execution Test
```python
def test_command_execution():
    pm = CommandLoader(AgentType.PROJECT_MANAGER)
    result = pm.execute("update_priority_status", {
        "priority_id": "PRIORITY-25",
        "new_status": "✅ Complete"
    })
    assert result["success"] == True
```

#### Workflow Integration Test
```python
def test_end_to_end_workflow():
    # Create priority
    pm.execute("parse_roadmap", {"content": "..."})

    # Architect creates spec
    arch.execute("create_spec", {"priority_id": "..."})

    # Developer implements
    dev.execute("claim_priority", {"priority_id": "..."})

    # Verify complete workflow
    assert check_workflow_complete()
```

---

## Appendices

### A. Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Low | High | Parallel operation, feature flags |
| Performance degradation | Low | Medium | Benchmarking, optimization |
| Missing commands | Medium | Low | Continuous validation |
| Skill integration issues | Medium | Medium | Progressive testing |
| Agent resistance | Low | Low | Training, documentation |

### B. Required Resources

#### Human Resources
- 1 Senior Developer (full-time, 16 days)
- 1 QA Engineer (part-time, days 7-16)
- 1 Technical Writer (part-time, days 14-16)

#### Technical Resources
- Development environment with all agents
- Test database with production-like data
- CI/CD pipeline for validation
- Monitoring for performance metrics

### C. Communication Plan

#### Stakeholders
- Development team - Daily updates
- Management - Weekly progress reports
- Users - Release notes after completion

#### Checkpoints
- Day 3: Foundation complete
- Day 7: Core agents operational
- Day 11: Support agents ready
- Day 14: UI agents complete
- Day 16: Full system validated

### D. Post-Implementation

#### Maintenance Plan
- Weekly review of command usage
- Monthly audit of permissions
- Quarterly skill updates
- Annual architecture review

#### Enhancement Opportunities
- Command versioning system
- Dynamic permission updates
- Command composition patterns
- Performance optimizations

---

## Conclusion

This unified plan provides a complete roadmap for transforming the MonolithicCoffeeMaker agent system into a command-driven architecture with enforced domain boundaries. The approach:

1. **Preserves existing functionality** through wrapping, not replacing
2. **Documents all operations** in structured commands
3. **Enforces clear boundaries** via permission system
4. **Enables gradual migration** with minimal risk
5. **Improves maintainability** through clear structure

The 16-day implementation timeline is aggressive but achievable, with clear checkpoints and rollback capability at each phase. Success will be measured through both technical metrics (compatibility, performance) and business metrics (debugging speed, maintainability).

Key to success:
- **Start with working system** - Core agents with introspection-documented workflows
- **Add incrementally** - Commands from prompts as enhancement
- **Validate continuously** - Test at every step
- **Document thoroughly** - Commands are self-documenting

This architecture positions the system for long-term maintainability while preserving all current capabilities and adding clear structure for future enhancements.

---

**Document Version**: 1.0 - Complete Unified Plan
**Date**: 2025-10-26
**Status**: Ready for Implementation
**Total Pages**: 42
**Total Commands**: 98
**Timeline**: 16 days
**Approach**: Evolutionary Enhancement
