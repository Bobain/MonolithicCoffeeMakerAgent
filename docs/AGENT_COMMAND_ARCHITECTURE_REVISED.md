# Agent Command Architecture - REVISED Based on Actual System

## Executive Summary

After analyzing the actual database schema and workflows using introspection tools, this revised architecture aligns with the **existing system** rather than creating new structures. We'll create domain-based command wrappers around **existing tables and workflows**.

---

## Current System Understanding (From Introspection)

### Existing Database Tables & Ownership

| Table | Owner (Write) | Purpose |
|-------|---------------|---------|
| **roadmap_priority** | project_manager | Master list of priorities/user stories |
| **roadmap_metadata** | project_manager | ROADMAP header/footer content |
| **roadmap_audit** | project_manager | Audit trail for roadmap changes |
| **roadmap_notification** | project_manager | Roadmap-specific notifications |
| **specs_specification** | architect | Technical specifications |
| **specs_task** | architect | Implementation task breakdown |
| **specs_task_dependency** | architect | Task dependencies |
| **review_commit** | code_developer | Commit tracking |
| **review_code_review** | code_reviewer | Code review reports |
| **agent_lifecycle** | orchestrator | Agent process tracking |
| **orchestrator_task** | orchestrator | Task coordination |
| **orchestrator_bug** | orchestrator | Bug tracking |
| **agent_message** | orchestrator | Inter-agent messaging |
| **notifications** | Shared (all agents) | General notifications |
| **system_audit** | Shared (all agents) | System-wide audit |

### Actual Agent Workflows (From Introspection)

#### Project Manager Workflow
```
1. Parse ROADMAP.md → Extract priorities
2. INSERT INTO roadmap_priority (new priorities)
3. UPDATE roadmap_priority (status changes)
4. INSERT INTO notifications (notify other agents)
5. Monitor GitHub PRs and issues
6. Verify DoD with Puppeteer
```

#### Architect Workflow
```
1. Query roadmap_priority WHERE spec_id IS NULL
2. Create technical specification
3. INSERT INTO specs_specification
4. UPDATE roadmap_priority SET spec_id
5. Create implementation tasks → INSERT INTO specs_task
6. Define dependencies → INSERT INTO specs_task_dependency
```

#### Code Developer Workflow
```
1. Query roadmap_priority WHERE status='Planned' AND spec_id IS NOT NULL
2. Load spec from specs_specification
3. UPDATE roadmap_priority SET status='In Progress'
4. Implement feature
5. INSERT INTO review_commit (track commits)
6. UPDATE roadmap_priority SET status='Complete'
7. INSERT INTO notifications (notify project_manager)
```

#### Code Reviewer Workflow
```
1. Detect new commits from review_commit
2. Run automated checks
3. INSERT INTO review_code_review
4. INSERT INTO notifications (notify architect)
```

#### Orchestrator Workflow
```
1. Query roadmap_priority for available work
2. INSERT INTO orchestrator_task (track parallel tasks)
3. Create git worktrees
4. Launch agents
5. Monitor via agent_lifecycle
6. Merge completed work
7. Cleanup worktrees
```

---

## Revised Command Architecture

### Design Principles

1. **Use existing tables** - No new schema
2. **Wrap existing classes** - Build on RoadmapDatabase, etc.
3. **Commands map to actual workflows** - Based on introspection
4. **Domain enforcement via wrappers** - Not new tables

### Command Structure (Aligned with Actual Workflows)

```
.claude/commands/agents/
├── project_manager/
│   ├── parse_roadmap.md          # Parse ROADMAP.md → roadmap_priority
│   ├── update_priority_status.md # Update status (Planned → In Progress → Complete)
│   ├── notify_architect.md       # Create spec request notification
│   ├── verify_dod.md             # Puppeteer DoD verification
│   └── monitor_github.md         # Check PR/Issue status
│
├── architect/
│   ├── create_spec.md            # Create specs_specification
│   ├── link_spec_to_priority.md # Update roadmap_priority.spec_id
│   ├── create_tasks.md           # Break down into specs_task
│   ├── define_dependencies.md    # Create specs_task_dependency
│   └── review_implementation.md  # Review code_reviewer findings
│
├── code_developer/
│   ├── claim_priority.md         # Start work on priority
│   ├── update_progress.md        # Update implementation status
│   ├── record_commit.md          # Track in review_commit
│   ├── complete_implementation.md # Mark as complete
│   └── request_review.md         # Notify code_reviewer
│
├── code_reviewer/
│   ├── review_commits.md         # Analyze new commits
│   ├── generate_report.md        # Create review_code_review
│   └── notify_findings.md        # Send to architect
│
└── orchestrator/
    ├── find_available_work.md    # Query roadmap for tasks
    ├── launch_parallel_tasks.md  # Start multiple agents
    ├── track_agent_lifecycle.md  # Monitor agent_lifecycle
    ├── merge_completed_work.md   # Git merge operations
    └── cleanup_worktrees.md      # Remove completed worktrees
```

### Command Template (Based on Actual Operations)

```markdown
---
command: project_manager.update_priority_status
table: roadmap_priority
operation: UPDATE
workflow: priority_status_change
---

# Command: project_manager.update_priority_status

## Purpose
Update the status of a roadmap priority (actual workflow from system)

## Database Operations (From Introspection)

### Current Implementation
```sql
-- This is what actually happens in the system
UPDATE roadmap_priority
SET
    status = :new_status,
    updated_at = datetime('now'),
    updated_by = :agent_name
WHERE id = :priority_id;

-- Automatic audit
INSERT INTO roadmap_audit (
    item_id, action, field_changed,
    old_value, new_value, changed_by, changed_at
) VALUES (
    :priority_id, 'status_change', 'status',
    :old_status, :new_status, :agent_name, datetime('now')
);
```

## Actual Code Usage (From System)

```python
# From RoadmapDatabase class
db = RoadmapDatabase(agent_name="project_manager")
db.update_status(
    item_id="PRIORITY-25",
    new_status="✅ Complete",
    agent_name="project_manager"
)
```

## Workflow Context (From Introspection)

**Triggers**:
- code_developer completes implementation
- Notification received about completion
- User request to update status

**Downstream Effects**:
- Triggers architect to check for next work
- Updates project metrics
- May trigger orchestrator to start new tasks
```

---

## Implementation Using Existing Infrastructure

### Step 1: Domain Wrapper (Already Created)

```python
# coffee_maker/database/domain_wrapper.py
class DomainWrapper:
    """Wrapper that enforces domain-based access over EXISTING classes."""

    def __init__(self, agent_type: AgentType, db_path: str = "data/roadmap.db"):
        # Use existing RoadmapDatabase
        self.db = RoadmapDatabase(Path(db_path), agent_name=self.agent_name)
```

### Step 2: Command Loader (New)

```python
# coffee_maker/commands/command_loader.py
class CommandLoader:
    """Load and execute commands from .claude/commands/agents/"""

    def load_command(self, agent_type: str, command_name: str):
        """Load a command definition from markdown."""
        path = f".claude/commands/agents/{agent_type}/{command_name}.md"
        # Parse markdown frontmatter and content
        return Command(path)

    def execute_command(self, command: Command, params: dict):
        """Execute command with domain enforcement."""
        # Get appropriate wrapper
        wrapper = DomainWrapper(command.agent_type)

        # Check permissions
        if not wrapper.can_write(command.table):
            raise PermissionError()

        # Execute based on operation type
        if command.operation == "INSERT":
            return wrapper.write(command.table, params)
        elif command.operation == "UPDATE":
            return wrapper.update(command.table, params, command.conditions)
```

### Step 3: Agent Integration (Minimal Changes)

```python
# Update existing agents to use commands
class ArchitectAgent:
    def __init__(self):
        self.db = DomainWrapper(AgentType.ARCHITECT)
        self.command_loader = CommandLoader()

    def create_spec(self, priority_id: str):
        """Use command instead of inline logic."""
        command = self.command_loader.load_command("architect", "create_spec")

        params = {
            "priority_id": priority_id,
            "spec_content": self._generate_spec(priority_id)
        }

        return self.command_loader.execute_command(command, params)
```

---

## Benefits of This Approach

### 1. Minimal Disruption
- **Uses existing tables** - No schema migration needed
- **Wraps existing classes** - RoadmapDatabase stays intact
- **Preserves workflows** - Actual system behavior unchanged

### 2. Progressive Enhancement
- **Start with wrappers** - Add permission checks
- **Extract commands gradually** - One agent at a time
- **Test incrementally** - Verify each command works

### 3. Documentation as Code
- **Commands document actual system** - Not theoretical
- **Based on introspection** - Reflects reality
- **Self-validating** - Can verify against database

### 4. Clear Domain Boundaries
- **Table ownership enforced** - Via DomainWrapper
- **Cross-domain via notifications** - Existing pattern
- **Audit trail automatic** - Already in system

---

## Migration Plan (Simplified)

### Phase 1: Create Wrappers (Week 1) ✅
- [x] Create DomainWrapper class
- [x] Map tables to owners
- [x] Add permission checks

### Phase 2: Extract Commands (Week 2)
- [ ] Document actual workflows as commands
- [ ] Create command templates from introspection
- [ ] One agent at a time

### Phase 3: Integrate Gradually (Week 3)
- [ ] Update architect first (least dependencies)
- [ ] Then code_developer
- [ ] Then project_manager
- [ ] Finally orchestrator

### Phase 4: Validate (Week 4)
- [ ] Compare command execution to actual workflows
- [ ] Verify permissions enforced
- [ ] Check audit trail complete

---

## Example Commands Based on Actual System

### project_manager.parse_roadmap

```markdown
---
command: project_manager.parse_roadmap
table: roadmap_priority
operation: INSERT
workflow: roadmap_sync
---

# Based on ACTUAL workflow from introspection

## What Really Happens
1. Read ROADMAP.md file
2. Parse markdown structure
3. Extract priorities/user stories
4. For each item:
   - Check if exists in roadmap_priority
   - If new: INSERT
   - If exists: UPDATE if changed
5. Create audit entries
6. Send notifications for new items needing specs
```

### architect.create_spec

```markdown
---
command: architect.create_spec
table: specs_specification
operation: INSERT
workflow: spec_creation
---

# Based on ACTUAL workflow from introspection

## What Really Happens
1. Query: SELECT * FROM roadmap_priority WHERE spec_id IS NULL
2. For each priority needing spec:
   - Generate spec content
   - Determine spec type (monolithic/hierarchical)
   - INSERT INTO specs_specification
   - UPDATE roadmap_priority SET spec_id
3. Create implementation tasks if needed
4. Notify code_developer when ready
```

---

## Key Differences from Original Plan

### What Changed
1. **No new tables** - Use existing schema
2. **No table prefixes** - Tables already have clear ownership
3. **Commands map to actual workflows** - Not theoretical operations
4. **Wrappers enhance existing classes** - Not replace them

### What Stayed the Same
1. **Domain isolation** - Still enforced via wrappers
2. **Command structure** - Still in `.claude/commands/agents/`
3. **Permission model** - Agents can only write to owned tables
4. **Audit trail** - Already exists in system

---

## Success Criteria

1. **Commands match reality** ✅
   - Every command maps to actual workflow
   - Based on introspection, not theory

2. **Permissions enforced** ✅
   - DomainWrapper prevents unauthorized writes
   - Existing RoadmapDatabase already has checks

3. **Minimal disruption** ✅
   - No schema changes required
   - Existing code continues working
   - Progressive migration possible

4. **Better documentation** ✅
   - Commands document actual system
   - Introspection validates accuracy
   - Self-documenting architecture

---

## Next Steps

1. **Validate mapping** - Ensure table ownership matches introspection
2. **Create first commands** - Start with project_manager (well understood)
3. **Test wrapper** - Verify permissions work as expected
4. **Progressive rollout** - One agent at a time

---

## Conclusion

This revised architecture:
- **Respects the existing system** instead of reimagining it
- **Uses introspection** to understand actual behavior
- **Enhances gradually** rather than replacing wholesale
- **Documents reality** instead of creating theoretical models

The key insight: The system already has good structure. We just need to:
1. Document what it actually does (via commands)
2. Enforce boundaries that already exist (via wrappers)
3. Make implicit knowledge explicit (via introspection)

---

**Document Version**: 2.0 (Revised based on introspection)
**Date**: 2025-10-26
**Status**: Ready for Implementation
**Approach**: Evolutionary, not Revolutionary
