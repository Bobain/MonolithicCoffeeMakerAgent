---
name: workflow-and-data-flow-guide
version: 1.0.0
agent: shared
scope: shared
description: Comprehensive workflow and data flow documentation that describes how data flows through the system, which agents perform which operations, on what events, and provides full data lineage for orchestration
triggers:
  - "designing new workflows"
  - "understanding data flows"
  - "orchestrating agent tasks"
  - "determining agent responsibilities"
  - "troubleshooting workflow issues"
  - "planning feature implementation"
requires:
  - database-schema-guide
---

# Workflow and Data Flow Guide Skill

This skill provides comprehensive documentation of system workflows, data flows, agent responsibilities, and event-driven processes to enable effective orchestration and system understanding.

## Purpose

This skill answers critical questions:
- **What happens after X?** (event-driven workflows)
- **Who does what?** (agent responsibilities)
- **Where is data stored?** (database tables and data lineage)
- **When does work happen?** (triggers and conditions)
- **How do agents collaborate?** (inter-agent workflows)

## Key Capabilities

### 1. Data Lineage Tracking
- Complete trace of data from creation → transformation → storage
- Example: "User creates priority → project_manager validates → writes to roadmap_priority table → code_developer reads → updates status → audit trail in roadmap_audit"

### 2. Event-Driven Workflows
- Maps events to agent actions and database operations
- Example: "When ROADMAP item status changes to 'Planned' → architect checks if spec_id is null → creates technical spec → writes to specs_specification → links via spec_id foreign key"

### 3. Agent Responsibility Verification
- Ensures agent descriptions match actual implemented workflows
- Validates that claimed responsibilities are actually performed in code

### 4. Orchestration Knowledge
- Provides the information orchestrator needs to coordinate workflows
- Defines preconditions, postconditions, and dependencies

## Usage

```python
from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

# Load the skill
skill = load_skill(SkillNames.WORKFLOW_AND_DATA_FLOW_GUIDE)

# RECOMMENDED: Get workflows for specific agent (filtered, reduced context)
my_workflows = skill.execute(
    action="get_workflows_for_agent",
    agent="architect"  # or "code_developer", "project_manager", etc.
)
# Returns: Only workflows where this agent participates, with:
#   - Your specific role and actions
#   - Upstream context (what happens before you)
#   - Downstream context (what happens after you)
#   - Database operations you perform

# Example result for architect:
# {
#   "agent": "architect",
#   "workflows": {
#     "priority_created": {
#       "name": "Priority Creation and Implementation",
#       "trigger": "New PRIORITY in ROADMAP.md",
#       "your_role": [
#         {
#           "agent": "architect",
#           "actions": ["Query roadmap_priority...", "Create spec..."],
#           "database_ops": {...}
#         }
#       ],
#       "context": {
#         "upstream": [
#           {"agent": "project_manager", "summary": "Parse ROADMAP.md"}
#         ],
#         "downstream": [
#           {"agent": "code_developer", "summary": "Query for next work"}
#         ]
#       }
#     }
#   },
#   "summary": "Agent architect participates in 2 workflows"
# }

# Get complete workflow (all agents) - useful for orchestration
workflow = skill.execute(
    action="get_workflow",
    event="priority_created"
)
# Returns: Complete workflow with all agents, database ops, conditions

# Get agent responsibilities
responsibilities = skill.execute(
    action="get_agent_responsibilities",
    agent="architect"
)
# Returns: All workflows where architect participates, database tables touched

# Get data lineage
lineage = skill.execute(
    action="get_data_lineage",
    entity="technical_spec"
)
# Returns: Creation → Updates → Status changes → Related tables

# Validate agent description
validation = skill.execute(
    action="validate_agent_description",
    agent="project_manager"
)
# Returns: Claimed vs actual responsibilities, missing/extra claims

# Get table access patterns
access = skill.execute(
    action="get_table_access",
    table="roadmap_priority"
)
# Returns: Which agents read/write, on which events, what conditions
```

## Available Actions

### 1. **get_workflow** - Get complete workflow for an event
   - Parameters: `event` (required)
   - Returns: Dict with sequence of agent actions, database operations, conditions
   - Example events:
     - `priority_created`
     - `spec_requested`
     - `implementation_started`
     - `implementation_complete`
     - `review_requested`
     - `notification_created`

### 2. **get_agent_responsibilities** - Get all responsibilities for an agent
   - Parameters: `agent` (required)
   - Returns: Dict with workflows participated in, database tables accessed, claimed responsibilities
   - Agents: `project_manager`, `architect`, `code_developer`, `code_reviewer`, `orchestrator`

### 3. **get_data_lineage** - Trace data flow for an entity
   - Parameters: `entity` (required)
   - Returns: Dict with creation event, all transformations, storage locations, related entities
   - Entities: `roadmap_priority`, `technical_spec`, `implementation_task`, `notification`, `audit_entry`

### 4. **validate_agent_description** - Verify agent description matches implementation
   - Parameters: `agent` (required)
   - Returns: Dict with validation results, discrepancies, recommendations
   - Checks: Claimed responsibilities vs actual code, database access patterns

### 5. **get_table_access** - Get access patterns for a database table
   - Parameters: `table` (required)
   - Returns: Dict with agents that access table, operations (read/write), conditions, frequency
   - Tables: All tables from database schema

### 6. **get_orchestration_plan** - Get plan for orchestrator to execute workflow
   - Parameters: `workflow_name` (required)
   - Returns: Dict with sequence of tasks, preconditions, postconditions, error handling
   - Workflows: `implement_priority`, `create_spec`, `review_code`, `merge_pr`

### 7. **list_workflows** - Get all documented workflows
   - Parameters: None
   - Returns: List of workflow names with descriptions

### 8. **list_events** - Get all documented events
   - Parameters: None
   - Returns: List of events with descriptions and triggered workflows

### 9. **validate_workflow_design** - Validate a proposed workflow design (ARCHITECT)
   - Parameters: `workflow_design` (dict with proposed workflow)
   - Returns: Dict with validation results, missing steps, data inconsistencies, recommendations
   - Checks: Data flow completeness, agent responsibilities, database constraints, error handling

### 10. **get_design_patterns** - Get recommended design patterns for workflow (ARCHITECT)
   - Parameters: `workflow_type` (e.g., 'data_processing', 'inter_agent_communication')
   - Returns: Dict with recommended patterns, examples, anti-patterns to avoid
   - Patterns: Event sourcing, CQRS, saga pattern, notification pattern

### 11. **check_data_consistency** - Verify data consistency across tables (ARCHITECT)
   - Parameters: `entities` (list of entities to check)
   - Returns: Dict with consistency rules, potential violations, foreign key integrity
   - Checks: Orphaned records, missing foreign keys, circular dependencies

### 12. **analyze_bottlenecks** - Identify potential workflow bottlenecks (ARCHITECT)
   - Parameters: `workflow_name` (required)
   - Returns: Dict with bottleneck analysis, concurrent vs sequential steps, optimization suggestions
   - Analysis: Single-threaded steps, database contention, agent dependencies

### 13. **suggest_database_changes** - Suggest database schema changes for workflow (ARCHITECT)
   - Parameters: `workflow_requirements` (dict with requirements)
   - Returns: Dict with suggested tables, columns, indexes, migration steps
   - Suggestions: New tables, denormalization opportunities, index recommendations

### 14. **validate_agent_boundaries** - Verify agent doesn't violate boundaries (ARCHITECT)
   - Parameters: `agent`, `proposed_responsibilities` (list)
   - Returns: Dict with boundary violations, overlaps with other agents, recommendations
   - Checks: Database access violations, file ownership conflicts, responsibility overlaps

### 15. **get_workflow_dependencies** - Get all dependencies for a workflow (ARCHITECT)
   - Parameters: `workflow_name` (required)
   - Returns: Dict with required tables, agents, external services, configuration
   - Dependencies: Database tables, APIs, file system, other workflows

### 16. **compare_workflow_alternatives** - Compare design alternatives (ARCHITECT)
   - Parameters: `alternatives` (list of workflow designs)
   - Returns: Dict with comparison matrix, pros/cons, complexity analysis, recommendation
   - Criteria: Performance, maintainability, complexity, scalability

## Architect-Specific Design Validation

### Design Validation Workflow

When designing a new feature, architect should:

```python
skill = load_skill(SkillNames.WORKFLOW_AND_DATA_FLOW_GUIDE)

# 1. Get design patterns for the workflow type
patterns = skill.execute(
    action="get_design_patterns",
    workflow_type="inter_agent_communication"
)
# Returns: Notification pattern, message queue, event sourcing

# 2. Design the workflow (create workflow_design dict)
workflow_design = {
    "name": "spec_review_workflow",
    "steps": [
        {"agent": "architect", "action": "create_spec", "database": ["specs_specification"]},
        {"agent": "code_reviewer", "action": "review_spec", "database": ["notifications"]},
        {"agent": "architect", "action": "update_spec", "database": ["specs_specification"]}
    ],
    "data_flow": {
        "input": "roadmap_priority",
        "output": "specs_specification",
        "intermediate": ["notifications"]
    }
}

# 3. Validate the design
validation = skill.execute(
    action="validate_workflow_design",
    workflow_design=workflow_design
)
# Returns: Missing error handling, no audit trail, recommend adding rollback

# 4. Check data consistency requirements
consistency = skill.execute(
    action="check_data_consistency",
    entities=["specs_specification", "roadmap_priority"]
)
# Returns: Foreign key spec_id must exist, orphaned specs warning

# 5. Identify potential bottlenecks
bottlenecks = skill.execute(
    action="analyze_bottlenecks",
    workflow_name="spec_review_workflow"
)
# Returns: Sequential review step blocks progress, suggest async notification

# 6. Suggest database changes if needed
db_changes = skill.execute(
    action="suggest_database_changes",
    workflow_requirements={
        "entities": ["spec_review"],
        "relationships": ["specs_specification → spec_review"],
        "access_patterns": ["query by reviewer", "query by spec_id"]
    }
)
# Returns: Create spec_reviews table, add indexes, add foreign keys

# 7. Validate agent boundaries
boundary_check = skill.execute(
    action="validate_agent_boundaries",
    agent="architect",
    proposed_responsibilities=["create_spec", "update_spec", "review_spec"]
)
# Returns: Warning - "review_spec" belongs to code_reviewer, remove from architect

# 8. Compare alternatives if you have multiple designs
comparison = skill.execute(
    action="compare_workflow_alternatives",
    alternatives=[workflow_design_a, workflow_design_b]
)
# Returns: Alternative A is simpler, Alternative B is more scalable

# 9. Get all dependencies
dependencies = skill.execute(
    action="get_workflow_dependencies",
    workflow_name="spec_review_workflow"
)
# Returns: Requires specs_specification table, notifications table, architect agent, code_reviewer agent
```

### Design Quality Checklist (Enforced by Skill)

The skill validates that designs meet these criteria:

#### 1. **Data Flow Completeness**
- ✅ All inputs defined
- ✅ All outputs defined
- ✅ Intermediate data storage identified
- ✅ Data transformations documented
- ❌ No "magic" data appearing from nowhere

#### 2. **Agent Responsibility Clarity**
- ✅ Each step assigned to specific agent
- ✅ No overlapping responsibilities
- ✅ Agent boundaries respected (file ownership, database access)
- ✅ No agent violating read-only restrictions
- ❌ No ambiguous "someone will do this" steps

#### 3. **Error Handling**
- ✅ Error paths defined for each step
- ✅ Rollback strategy documented
- ✅ Notification on failure
- ✅ Retry logic for transient failures
- ❌ No "happy path only" designs

#### 4. **Database Integrity**
- ✅ Foreign keys defined
- ✅ Constraints documented
- ✅ Indexes for query patterns
- ✅ Audit trail for mutations
- ❌ No orphaned records possible

#### 5. **Audit and Observability**
- ✅ All mutations create audit entries
- ✅ Workflow progress trackable
- ✅ Notification created for async steps
- ✅ Metrics available for monitoring
- ❌ No "black box" operations

#### 6. **Concurrency and Locking**
- ✅ Concurrent access patterns identified
- ✅ Locking strategy defined
- ✅ Deadlock prevention considered
- ✅ Isolation levels appropriate
- ❌ No race conditions possible

#### 7. **Scalability**
- ✅ Bottlenecks identified
- ✅ Parallelization opportunities noted
- ✅ Database query optimization
- ✅ Pagination for large datasets
- ❌ No O(n²) operations

### Design Pattern Recommendations

The skill recommends these proven patterns:

#### Pattern 1: Notification Pattern
**When**: Inter-agent communication, async work delegation
**Structure**:
```
Agent A → INSERT INTO notifications (target_agent, message)
Agent B → Poll notifications WHERE target_agent='B' AND status='pending'
Agent B → Process work
Agent B → UPDATE notifications SET status='processed'
```
**Benefits**: Decouples agents, audit trail, retry support

#### Pattern 2: Event Sourcing
**When**: Need complete history, audit requirements, replay capability
**Structure**:
```
All changes → INSERT INTO events (entity_id, event_type, data)
Current state → Materialized view from event log
Replay → Rebuild state from events
```
**Benefits**: Complete audit trail, time travel, debugging

#### Pattern 3: Saga Pattern
**When**: Multi-step workflows with rollback requirements
**Structure**:
```
Step 1 → Database mutation + compensation saved
Step 2 → Database mutation + compensation saved
On failure → Execute compensations in reverse order
```
**Benefits**: Rollback support, consistency, error recovery

#### Pattern 4: CQRS (Command Query Responsibility Segregation)
**When**: Complex reads, performance optimization
**Structure**:
```
Writes → roadmap_priority (normalized, consistent)
Reads → roadmap_summary (denormalized, optimized for queries)
Sync → Trigger or periodic job updates summary
```
**Benefits**: Read performance, write safety, scalability

## Core Workflows

### Workflow 1: Priority Creation and Implementation

```
Event: User creates new PRIORITY in ROADMAP.md
↓
project_manager:
  1. Parse ROADMAP.md content
  2. Extract priority metadata
  3. Call roadmap_db.create_item(
       item_id="PRIORITY-X",
       item_type="priority",
       number="X",
       title=extracted_title,
       status="📝 Planned",
       content=full_markdown,
       priority_order=auto_increment
     )
  4. Database: INSERT INTO roadmap_priority
  5. Database: INSERT INTO roadmap_audit (action='create', changed_by='project_manager')
  6. If spec_id is NULL:
     - Database: INSERT INTO notifications (
         target_agent='architect',
         notification_type='spec_needed',
         item_id='PRIORITY-X'
       )
↓
architect (triggered by notification or daily check):
  1. Query: SELECT * FROM roadmap_priority WHERE spec_id IS NULL AND status='📝 Planned'
  2. For each priority:
     a. Create technical specification (hierarchical or monolithic)
     b. Database: INSERT INTO specs_specification (
          spec_number=next_number,
          title=spec_title,
          roadmap_item_id='PRIORITY-X',
          status='draft',
          spec_type='hierarchical',
          content=spec_content,
          total_phases=N
        )
     c. Database: UPDATE roadmap_priority
                  SET spec_id=new_spec_id
                  WHERE id='PRIORITY-X'
     d. Database: INSERT INTO roadmap_audit (action='spec_linked')
     e. Database: UPDATE notifications
                  SET status='processed'
                  WHERE item_id='PRIORITY-X'
↓
code_developer (autonomous daemon):
  1. Query: SELECT * FROM roadmap_priority
            WHERE status='📝 Planned'
            AND spec_id IS NOT NULL
            ORDER BY priority_order ASC
            LIMIT 1
  2. Load spec: SELECT * FROM specs_specification WHERE id=spec_id
  3. Determine phase: Check current_phase_status, parse ROADMAP
  4. Update status: UPDATE roadmap_priority
                    SET status='🔄 In Progress',
                        implementation_started_at=NOW()
                    WHERE id='PRIORITY-X'
  5. Database: INSERT INTO roadmap_audit (action='status_change')
  6. Implement feature (reads spec content, phase files)
  7. Run tests
  8. Commit code
  9. Create PR: git push + gh pr create
 10. Update status: UPDATE roadmap_priority
                    SET status='✅ Complete'
                    WHERE id='PRIORITY-X'
 11. Database: INSERT INTO roadmap_audit (action='complete')
 12. Database: INSERT INTO notifications (
       target_agent='project_manager',
       notification_type='implementation_complete',
       item_id='PRIORITY-X'
     )
↓
code_reviewer (triggered after commit):
  1. Detect new commit (git hook or polling)
  2. Run automated checks (style, tests, security)
  3. Generate review report
  4. Database: INSERT INTO notifications (
       target_agent='architect',
       notification_type='review_complete',
       message=review_summary
     )
↓
project_manager (responds to notification or user request):
  1. Query: SELECT * FROM notifications
            WHERE target_agent='project_manager'
            AND status='pending'
  2. Verify DoD with Puppeteer (optional)
  3. Check GitHub PR status: gh pr view <pr_number>
  4. Mark complete in ROADMAP: UPDATE roadmap_priority
                                SET status='✅ Complete'
  5. Database: UPDATE notifications SET status='processed'
```

### Workflow 2: Spec Creation (Architect-Driven)

```
Event: architect creates new technical specification
↓
architect:
  1. Determine spec type (hierarchical vs monolithic)
  2. Generate spec number: SELECT MAX(spec_number) FROM specs_specification
  3. Create spec content (using templates)
  4. Database: INSERT INTO specs_specification (
       id='SPEC-{number}',
       spec_number={number},
       title=spec_title,
       roadmap_item_id=NULL,  -- May be linked later
       status='draft',
       spec_type='hierarchical',
       content=overview_content,
       phase_files=json_list_of_files,
       total_phases=N,
       estimated_hours=sum_of_phases
     )
  5. If hierarchical:
     a. Create directory: docs/architecture/specs/SPEC-{number}-{slug}/
     b. Write README.md (content field)
     c. Write phase files (referenced in phase_files field)
  6. Database: INSERT INTO system_audit (
       table_name='specs_specification',
       action='create',
       changed_by='architect'
     )
  7. If roadmap_item_id provided:
     Database: UPDATE roadmap_priority
               SET spec_id='SPEC-{number}'
               WHERE id=roadmap_item_id
```

### Workflow 3: Orchestrator Task Coordination

```
Event: orchestrator starts parallel implementation tasks
↓
orchestrator:
  1. Query available work: SELECT * FROM roadmap_priority
                           WHERE status='📝 Planned'
                           AND spec_id IS NOT NULL
                           ORDER BY priority_order
  2. Group by dependencies (can run in parallel if no shared deps)
  3. For each parallel group:
     a. Create git worktree: git worktree add path/to/worktree-{task_id} -b roadmap-implementation_task-{task_id}
     b. Database: INSERT INTO orchestrator_tasks (
          task_id=unique_id,
          roadmap_item_id='PRIORITY-X',
          worktree_path=path,
          branch_name=branch,
          status='running',
          started_at=NOW()
        )
     c. Launch code_developer agent in worktree
     d. Monitor progress (database polling)
  4. On completion:
     a. Database: UPDATE orchestrator_tasks SET status='complete'
     b. Merge to roadmap: git checkout roadmap && git merge {task-branch}
     c. Cleanup: git worktree remove path && git branch -D {task-branch}
  5. Database: INSERT INTO orchestrator_audit (
       action='parallel_execution_complete',
       tasks_completed=N
     )
```

## Database Tables and Ownership

### roadmap_priority
- **Owner**: project_manager (write), all agents (read)
- **Purpose**: Master list of priorities and user stories
- **Created by**: project_manager (parsing ROADMAP.md or CLI commands)
- **Updated by**:
  - project_manager: Creates, updates content, final approval
  - code_developer: Updates status (Planned → In Progress → Complete)
  - architect: Links spec_id after spec creation
- **Read by**: All agents for context and planning

### specs_specification
- **Owner**: architect (write), all agents (read)
- **Purpose**: Technical specifications with hierarchical phase support
- **Created by**: architect (manual or automated)
- **Updated by**:
  - architect: Creates, updates content, manages phases
  - code_developer: Updates phase status during implementation
- **Read by**:
  - code_developer: Reads during implementation
  - project_manager: Reads for planning
  - orchestrator: Reads for task coordination

### notifications
- **Owner**: All agents (write their own), recipient agent (processes)
- **Purpose**: Inter-agent communication and task delegation
- **Created by**: Any agent needing another agent's attention
- **Updated by**: Recipient agent (marks as processed)
- **Cleanup**: Periodic pruning of old processed notifications

### roadmap_audit / system_audit
- **Owner**: All agents (append-only)
- **Purpose**: Complete audit trail for compliance and debugging
- **Created by**: Automatic on every database mutation
- **Updated by**: Never (append-only)
- **Read by**: Monitoring, debugging, compliance checks

### orchestrator_tasks
- **Owner**: orchestrator (write), monitoring agents (read)
- **Purpose**: Track parallel task execution
- **Created by**: orchestrator when starting parallel work
- **Updated by**: orchestrator (status changes)
- **Read by**: Monitoring dashboards, health checks

## Agent Responsibilities (Enforced)

### project_manager
**Database Operations**:
- roadmap_priority: CREATE, UPDATE (content, status finalization)
- notifications: CREATE (outgoing), UPDATE (mark processed)
- roadmap_audit: CREATE (automatic)

**Claimed Responsibilities**:
- Parse ROADMAP.md and sync to database
- Create new priorities and user stories
- Monitor GitHub PRs and issues
- Verify DoD (post-implementation)
- Create notifications for other agents

**Validation**: ✅ All claims match implementation

### architect
**Database Operations**:
- specs_specification: CREATE, UPDATE (all fields)
- roadmap_priority: UPDATE (spec_id linkage only)
- notifications: CREATE (outgoing), UPDATE (mark processed)
- system_audit: CREATE (automatic)

**Claimed Responsibilities**:
- Create technical specifications
- Design system architecture
- Manage dependencies (pyproject.toml)
- Link specs to roadmap items
- Provide implementation guidelines

**Validation**: ✅ All claims match implementation

### code_developer
**Database Operations**:
- roadmap_priority: UPDATE (status only: Planned → In Progress → Complete)
- specs_specification: UPDATE (phase status, actual_hours)
- notifications: CREATE (implementation_complete)
- roadmap_audit: CREATE (automatic)

**Claimed Responsibilities**:
- Implement features from specs
- Update implementation status
- Run tests and create PRs
- Manage technical configuration (.claude/)
- Write all code in coffee_maker/, tests/

**Validation**: ✅ All claims match implementation

### code_reviewer
**Database Operations**:
- notifications: CREATE (review_complete)

**Claimed Responsibilities**:
- Automated code quality checks
- Security scanning
- Style guide enforcement
- Generate review reports
- Notify architect of issues

**Validation**: ✅ All claims match implementation

### orchestrator
**Database Operations**:
- orchestrator_tasks: CREATE, UPDATE, DELETE
- roadmap_priority: READ (for planning)
- specs_specification: READ (for task details)

**Claimed Responsibilities**:
- Coordinate parallel agent execution
- Manage git worktrees for isolation
- Monitor task health
- Merge completed work
- Handle fault tolerance

**Validation**: ✅ All claims match implementation

## Event Catalog

### Database Events
1. **priority_created**: New row in roadmap_priority
2. **priority_status_changed**: UPDATE roadmap_priority.status
3. **spec_created**: New row in specs_specification
4. **spec_linked**: UPDATE roadmap_priority.spec_id
5. **implementation_started**: UPDATE roadmap_priority.status = 'In Progress'
6. **implementation_complete**: UPDATE roadmap_priority.status = 'Complete'
7. **notification_created**: New row in notifications
8. **notification_processed**: UPDATE notifications.status = 'processed'

### Git Events
1. **commit_created**: git commit
2. **pr_created**: gh pr create
3. **pr_merged**: gh pr merge
4. **branch_created**: git branch or git worktree add

### External Events
1. **user_request**: User asks for feature/change
2. **daily_check**: Scheduled agent check (cron-like)
3. **github_webhook**: PR status change, CI completion

## Orchestration Plans

### Plan: Implement Priority
**Preconditions**:
- roadmap_priority exists with status='📝 Planned'
- spec_id is not NULL
- specs_specification exists and status='complete' or 'draft'

**Steps**:
1. code_developer: Load spec
2. code_developer: Determine phase
3. code_developer: Update status → 'In Progress'
4. code_developer: Implement feature
5. code_developer: Run tests
6. code_developer: Commit and create PR
7. code_developer: Update status → 'Complete'
8. code_reviewer: Review commit
9. project_manager: Verify DoD (optional)
10. project_manager: Merge PR

**Postconditions**:
- Code committed and tested
- PR created on GitHub
- roadmap_priority.status = 'Complete'
- Audit trail created

**Error Handling**:
- If tests fail: Rollback, create notification
- If spec missing: Create notification for architect
- If conflicts: Manual resolution required

## Integration with Database Schema Guide

This skill USES the database-schema-guide skill for:
- Table structure information
- Column types and constraints
- Relationships and foreign keys

This skill ADDS on top:
- Who accesses what (agent → table mapping)
- When access happens (event → operation)
- Why access happens (workflow context)
- How data flows (lineage across tables)

## When to Use

- ✅ **BEFORE** designing new feature workflows
- ✅ **BEFORE** creating orchestration logic
- ✅ **WHEN** debugging workflow issues
- ✅ **WHEN** understanding agent responsibilities
- ✅ **WHEN** verifying agent descriptions match reality
- ✅ **DURING** onboarding new agents or developers
- ✅ **FOR** generating orchestration plans

## Validation and Compliance

This skill enables validation that:
1. **Agent descriptions are accurate** (claimed responsibilities match code)
2. **Database access is controlled** (only authorized agents write to tables)
3. **Workflows are complete** (all steps documented and implemented)
4. **Data lineage is traceable** (can track any data from source to destination)
5. **Orchestration is feasible** (preconditions and dependencies clear)

## See Also

- Database Schema Guide: `.claude/skills/shared/database_schema_guide/` (table structures)
- Agent Ownership: `docs/AGENT_OWNERSHIP.md` (official agent boundaries)
- Workflows: `docs/WORKFLOWS.md` (user-facing workflow documentation)
- Database Code: `coffee_maker/autonomous/roadmap_database.py` (implementation)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-25
**Status**: Ready for implementation ✅
