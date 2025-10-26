# SPEC-103: Architect Commands

**Status**: Draft
**Created**: 2025-10-26
**Author**: architect
**Parent Spec**: SPEC-100
**Related Specs**: SPEC-101 (Foundation), SPEC-102 (Project Manager)
**Related CFRs**: CFR-007 (Context Budget), CFR-011 (Daily Integration), CFR-013 (Git Workflow)
**Dependencies**: SPEC-101 (Foundation), SPEC-102 (Project Manager)

## Executive Summary

Implement 12 commands for the architect agent, covering technical specification creation, implementation task management, and architecture governance. These commands enforce the architect's exclusive write access to the `specs` schema while enabling architectural decision-making and code quality oversight.

### Key Objectives

1. **Specification Management** - Create and link technical specs (4 commands)
2. **Task Management** - Create tasks, define dependencies (3 commands)
3. **Architecture Governance** - ADRs, guidelines, dependencies, worktree merging (5 commands)

### Design Principles

- **Database-First**: Specs stored in database, files are backup only
- **Hierarchical Specs**: Context budget management through progressive disclosure
- **Exclusive Write Access**: ONLY architect writes to `specs_*` tables
- **Code Quality Loop**: Read code reviews, take action on findings

---

## Architecture Overview

### Command Groups

```
Architect (12 commands)
├── Specification Management (4 commands)
│   ├── create_spec                    - Create technical specification
│   ├── link_spec_to_priority          - Link spec to roadmap item
│   ├── validate_spec_completeness     - Check spec has all sections
│   └── update_spec                    - Modify existing spec
│
├── Task Management (3 commands)
│   ├── create_implementation_tasks    - Break spec into tasks
│   ├── define_task_dependencies       - Set task prerequisites
│   └── update_task_status             - Track task progress
│
└── Architecture Governance (5 commands)
    ├── generate_adr                   - Create ADR document
    ├── update_guidelines              - Modify architecture guidelines
    ├── update_cfrs                    - Update CFR documents
    ├── approve_dependency             - Review and approve packages
    └── merge_worktree_branches        - Merge parallel work to roadmap
```

### Database Domain

**Tables Owned (Write Access)**:
- `specs_specification` - Technical specifications (database-first, hierarchical JSON)
- `specs_task` - Implementation tasks (with granularity and context management)
- `specs_task_dependency` - Task dependencies (hard/soft)

**Tables Read**:
- `roadmap_priority` - Priorities needing specs
- `review_code_review` - Code quality findings from code_reviewer
- `orchestrator_task` - Parallel task status
- `notifications` - Spec requests, review notifications

---

## Command Group 1: Specification Management (4 Commands)

### Command: architect.create_spec

**Purpose**: Create a technical specification (hierarchical or monolithic) in the database

**Tables**:
- Write: `specs_specification`
- Read: `roadmap_priority`, `specs_specification` (for existing specs)

**Files**:
- Read: `docs/roadmap/ROADMAP.md` (via database)
- Write: `docs/architecture/specs/SPEC-{num}-{slug}.md` (backup export only)

**Required Skills**: `technical_specification_handling`, `architecture_reuse_check`

**Input Parameters**:
```yaml
spec_number: integer         # Required - Spec number (e.g., 131)
title: string                # Required - Spec title
roadmap_item_id: string      # Required - Linked priority (e.g., "PRIORITY-28")
spec_type: string            # "hierarchical" or "monolithic"
content: object              # Hierarchical: {overview, api_design, implementation, ...}
                             # Monolithic: single markdown string
estimated_hours: float       # Total effort estimate
phases: array                # For hierarchical: [{name, hours, description, content}]
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "spec_type": "hierarchical",
  "estimated_hours": 24.0,
  "phases_created": 3,
  "notification_sent": true,
  "reuse_components_found": 2
}
```

**Success Criteria**:
- ✅ Spec created in database with JSON content
- ✅ Hierarchical structure enables progressive disclosure
- ✅ Linked to roadmap priority
- ✅ Notification sent to project_manager
- ✅ Reuse analysis performed before creation

**Database Operations**:

```python
def create_spec(db: DomainWrapper, params: dict):
    spec_id = f"SPEC-{params['spec_number']}"

    # MANDATORY: Run reuse analysis first
    reuse_skill = load_skill("architecture_reuse_check")
    reuse_analysis = reuse_skill.execute({
        "spec_title": params["title"],
        "roadmap_item_id": params["roadmap_item_id"]
    })

    # Build spec content
    if params["spec_type"] == "hierarchical":
        content = {
            "type": "hierarchical",
            "overview": params["content"]["overview"],
            "phases": params["phases"],
            "architecture": params["content"].get("architecture", ""),
            "reuse_components": reuse_analysis.get("components", [])
        }
    else:
        content = {
            "type": "monolithic",
            "content": params["content"]
        }

    # Write to database
    spec_data = {
        "id": spec_id,
        "spec_number": params["spec_number"],
        "title": params["title"],
        "roadmap_item_id": params["roadmap_item_id"],
        "spec_type": params["spec_type"],
        "content": json.dumps(content),  # JSON in database
        "estimated_hours": params.get("estimated_hours", 0),
        "status": "draft",
        "created_by": "architect",
        "created_at": datetime.now().isoformat()
    }

    db.write("specs_specification", spec_data, action="create")

    # Notify project_manager
    db.send_notification("project_manager", {
        "type": "spec_created",
        "spec_id": spec_id,
        "roadmap_item_id": params["roadmap_item_id"],
        "message": f"Technical spec {spec_id} created for {params['roadmap_item_id']}"
    })

    # Optional: Export backup file
    if params.get("export_file", False):
        export_spec_to_file(spec_id, content)

    return {
        "success": True,
        "spec_id": spec_id,
        "spec_type": params["spec_type"],
        "estimated_hours": params.get("estimated_hours", 0),
        "reuse_components_found": len(reuse_analysis.get("components", []))
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| DuplicateSpecError | Spec number already exists | Use next available number |
| InvalidPriorityError | Roadmap item not found | Verify priority exists |
| ValidationError | Missing required fields | Provide all required params |
| PermissionError | Not architect agent | Only architect can create specs |

**Downstream Effects**:
- project_manager links spec to roadmap item
- orchestrator detects spec is ready
- code_developer can load spec for implementation
- Reuse components identified for future specs

---

### Command: architect.link_spec_to_priority

**Purpose**: Link an existing spec to a roadmap priority (bidirectional reference)

**Tables**:
- Write: `specs_specification`
- Read: `roadmap_priority`, `specs_specification`

**Required Skills**: `technical_specification_handling`, `roadmap_database_handling`

**Input Parameters**:
```yaml
spec_id: string              # Spec to link (e.g., "SPEC-131")
priority_id: string          # Priority to link (e.g., "PRIORITY-28")
notify_project_manager: boolean  # Send notification (default: true)
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "priority_id": "PRIORITY-28",
  "notification_sent": true
}
```

**Success Criteria**:
- ✅ Spec updated with priority_id
- ✅ Notification sent to project_manager
- ✅ Bidirectional link established

---

### Command: architect.validate_spec_completeness

**Purpose**: Check if a spec has all required sections and is ready for implementation

**Tables**:
- Read: `specs_specification`

**Required Skills**: `technical_specification_handling`

**Input Parameters**:
```yaml
spec_id: string              # Spec to validate
strict_mode: boolean         # Fail on warnings (default: false)
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "is_complete": true,
  "missing_sections": [],
  "warnings": ["Test strategy could be more detailed"],
  "validation_score": 95
}
```

**Success Criteria**:
- ✅ All required sections present
- ✅ Content quality assessed
- ✅ Warnings identified
- ✅ Validation score calculated (0-100)

---

### Command: architect.update_spec

**Purpose**: Modify an existing spec (add sections, update content, change status)

**Tables**:
- Write: `specs_specification`, `system_audit`
- Read: `specs_specification`

**Required Skills**: `technical_specification_handling`

**Input Parameters**:
```yaml
spec_id: string              # Spec to update
updates: object              # Fields to update {status, content, estimated_hours, ...}
reason: string               # Optional - Reason for update
version: string              # Optional - Version bump (e.g., "1.1.0")
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "updated_fields": ["status", "estimated_hours"],
  "old_version": "1.0.0",
  "new_version": "1.1.0",
  "audit_entry_created": true
}
```

**Success Criteria**:
- ✅ Spec updated in database
- ✅ Audit trail created
- ✅ Version incremented if content changed
- ✅ Notifications sent if status changed

---

## Command Group 2: Task Management (3 Commands)

### Command: architect.create_implementation_tasks

**Purpose**: Break a technical spec into implementation tasks (using ImplementationTaskCreator)

**Tables**:
- Write: `specs_task`
- Read: `specs_specification`

**Required Skills**: `technical_specification_handling`

**Input Parameters**:
```yaml
spec_id: string              # Spec to decompose
priority_number: integer     # Priority for task ordering
granularity: string          # "phase", "section", "module"
assign_files: boolean        # Auto-assign files to tasks (default: true)
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "tasks_created": 3,
  "task_group_id": "GROUP-31",
  "tasks": [
    {
      "task_id": "TASK-31-1",
      "scope_description": "Phase 1: Database Schema",
      "spec_sections": ["data_model", "implementation"],
      "assigned_files": ["coffee_maker/models/user.py"],
      "estimated_hours": 8.0
    }
  ]
}
```

**Success Criteria**:
- ✅ Tasks created with unique IDs
- ✅ Task group assigned (GROUP-{priority_number})
- ✅ Spec sections mapped to tasks
- ✅ Files assigned without conflicts
- ✅ Priority order set

**Database Operations**:

```python
def create_implementation_tasks(db: DomainWrapper, params: dict):
    from coffee_maker.autonomous.implementation_task_creator import ImplementationTaskCreator

    creator = ImplementationTaskCreator("data/roadmap.db", agent_name="architect")

    # Decompose spec into tasks
    tasks = creator.create_works_for_spec(
        spec_id=params["spec_id"],
        priority_number=params["priority_number"],
        granularity=params.get("granularity", "phase")
    )

    task_group_id = f"GROUP-{params['priority_number']}"

    # Tasks are automatically written to specs_task table by creator
    # with assigned files and priority ordering

    return {
        "success": True,
        "spec_id": params["spec_id"],
        "tasks_created": len(tasks),
        "task_group_id": task_group_id,
        "tasks": tasks
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| FileConflictError | Tasks overlap on same files | Adjust granularity, split differently |
| InvalidGranularityError | Unknown granularity type | Use "phase", "section", or "module" |
| SpecNotFoundError | Spec doesn't exist | Verify spec_id |

**Downstream Effects**:
- orchestrator can assign tasks to code_developer
- Tasks execute in priority order
- File conflicts prevented
- Progress tracked per task

---

### Command: architect.define_task_dependencies

**Purpose**: Define dependencies between task groups (hard/soft)

**Tables**:
- Write: `specs_task_dependency`
- Read: `specs_task`

**Required Skills**: None

**Input Parameters**:
```yaml
task_group_id: string        # Task group (e.g., "GROUP-31")
depends_on_group_id: string  # Prerequisite group (e.g., "GROUP-30")
dependency_type: string      # "hard" (blocking) or "soft" (recommended)
reason: string               # Why this dependency exists
```

**Output**:
```json
{
  "success": true,
  "task_group_id": "GROUP-31",
  "depends_on_group_id": "GROUP-30",
  "dependency_type": "hard",
  "dependency_id": "dep-123"
}
```

**Success Criteria**:
- ✅ Dependency created in database
- ✅ Dependency type recorded
- ✅ Reason documented
- ✅ orchestrator respects dependency order

**Database Operations**:

```python
def define_task_dependencies(db: DomainWrapper, params: dict):
    dependency_data = {
        "task_group_id": params["task_group_id"],
        "depends_on_group_id": params["depends_on_group_id"],
        "dependency_type": params["dependency_type"],
        "reason": params["reason"],
        "created_by": "architect",
        "created_at": datetime.now().isoformat()
    }

    dep_id = db.write("specs_task_dependency", dependency_data, action="create")

    return {
        "success": True,
        "task_group_id": params["task_group_id"],
        "depends_on_group_id": params["depends_on_group_id"],
        "dependency_type": params["dependency_type"],
        "dependency_id": dep_id
    }
```

---

### Command: architect.update_task_status

**Purpose**: Update task status (for monitoring, not execution)

**Tables**:
- Write: `specs_task`
- Read: `specs_task`

**Required Skills**: None

**Input Parameters**:
```yaml
task_id: string              # Task to update (e.g., "TASK-31-1")
new_status: string           # "pending", "in_progress", "completed", "blocked"
notes: string                # Optional - Status change notes
```

**Output**:
```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "old_status": "pending",
  "new_status": "in_progress"
}
```

**Success Criteria**:
- ✅ Task status updated
- ✅ Audit trail created
- ✅ orchestrator notified if status=completed

---

## Command Group 3: Architecture Governance (5 Commands)

### Command: architect.generate_adr

**Purpose**: Create an Architectural Decision Record document

**Tables**:
- Write: `system_audit`

**Files**:
- Write: `docs/architecture/decisions/ADR-{num}-{slug}.md`

**Required Skills**: None

**Input Parameters**:
```yaml
adr_number: integer          # ADR number (sequential)
title: string                # ADR title
context: string              # Problem context
decision: string             # Decision made
consequences: object         # {positive: [...], negative: [...]}
alternatives: array          # [{option, reason_rejected}, ...]
status: string               # "Proposed", "Accepted", "Deprecated", "Superseded"
```

**Output**:
```json
{
  "success": true,
  "adr_id": "ADR-015",
  "file_path": "docs/architecture/decisions/ADR-015-use-command-architecture.md",
  "status": "Proposed"
}
```

**Success Criteria**:
- ✅ ADR file created with correct format
- ✅ Status set appropriately
- ✅ Alternatives documented
- ✅ Audit log created

**File Operations**:

```python
def generate_adr(db: DomainWrapper, params: dict):
    adr_id = f"ADR-{params['adr_number']:03d}"
    slug = slugify(params["title"])
    filename = f"ADR-{params['adr_number']:03d}-{slug}.md"
    filepath = f"docs/architecture/decisions/{filename}"

    # Generate ADR content from template
    content = f"""# {adr_id}: {params['title']}

**Status**: {params['status']}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Author**: architect agent

## Context

{params['context']}

## Decision

{params['decision']}

## Consequences

### Positive
{format_list(params['consequences']['positive'])}

### Negative
{format_list(params['consequences']['negative'])}

## Alternatives Considered

{format_alternatives(params['alternatives'])}
"""

    # Write ADR file
    with open(filepath, 'w') as f:
        f.write(content)

    # Audit log
    db.write("system_audit", {
        "table_name": "adr_documents",
        "item_id": adr_id,
        "action": "create",
        "field_changed": "file",
        "new_value": filepath,
        "changed_by": "architect",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "adr_id": adr_id,
        "file_path": filepath,
        "status": params["status"]
    }
```

---

### Command: architect.update_guidelines

**Purpose**: Create or update architecture guidelines

**Tables**:
- Write: `system_audit`

**Files**:
- Write: `docs/architecture/guidelines/GUIDELINE-{num}-{slug}.md`

**Required Skills**: None

**Input Parameters**:
```yaml
guideline_number: integer    # Guideline number (sequential)
title: string                # Guideline title
category: string             # "Design Pattern", "Best Practice", "Anti-Pattern", "Code Standard"
when_to_use: string          # When to apply this guideline
how_to_implement: string     # Implementation details
anti_patterns: string        # What NOT to do
examples: array              # Code examples
```

**Output**:
```json
{
  "success": true,
  "guideline_id": "GUIDELINE-007",
  "file_path": "docs/architecture/guidelines/GUIDELINE-007-command-pattern.md"
}
```

**Success Criteria**:
- ✅ Guideline file created
- ✅ Category set
- ✅ Examples provided
- ✅ Anti-patterns documented

---

### Command: architect.update_cfrs

**Purpose**: Update Critical Functional Requirements documentation

**Tables**:
- Write: `system_audit`

**Files**:
- Write: `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`

**Required Skills**: None

**Input Parameters**:
```yaml
cfr_number: integer          # CFR number
action: string               # "create", "update", "deprecate"
title: string                # CFR title
description: string          # Requirement description
rationale: string            # Why this is critical
enforcement: string          # How it's enforced
```

**Output**:
```json
{
  "success": true,
  "cfr_id": "CFR-016",
  "action": "create",
  "file_updated": true
}
```

**Success Criteria**:
- ✅ CFR document updated
- ✅ Enforcement method documented
- ✅ Audit log created

---

### Command: architect.approve_dependency

**Purpose**: Review and approve a dependency request from code_developer

**Tables**:
- Write: `system_audit`, `notifications`

**Files**:
- Write: `pyproject.toml` (via poetry)

**Required Skills**: `dependency_conflict_resolver`

**Input Parameters**:
```yaml
package_name: string         # Package to approve
version: string              # Optional - Specific version
reason: string               # Why this dependency is needed
approved: boolean            # Approval decision
security_check: boolean      # Run security audit (default: true)
```

**Output**:
```json
{
  "success": true,
  "package_name": "redis",
  "version": "5.0.0",
  "approved": true,
  "security_check_passed": true,
  "adr_created": "ADR-016-use-redis.md"
}
```

**Success Criteria**:
- ✅ Dependency evaluated (security, licensing, maintenance)
- ✅ User approval requested if tier 2/3
- ✅ Package added via `poetry add` if approved
- ✅ ADR created documenting decision
- ✅ Notification sent to code_developer

**External Tool Usage**:

```bash
# Add dependency
poetry add redis==5.0.0

# Check for conflicts
poetry check

# Update lock file
poetry lock
```

**Database Operations**:

```python
def approve_dependency(db: DomainWrapper, params: dict):
    package = params["package_name"]
    version = params.get("version", "latest")

    # Security check
    if params.get("security_check", True):
        security_result = check_package_security(package, version)
        if not security_result["safe"]:
            return {
                "success": False,
                "error": "Security issues found",
                "issues": security_result["issues"]
            }

    # If approved, add dependency
    if params["approved"]:
        # Add via poetry
        cmd = ["poetry", "add", f"{package}=={version}"] if version != "latest" else ["poetry", "add", package]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to add dependency: {result.stderr}"
            }

        # Create ADR
        adr_num = get_next_adr_number()
        generate_adr(db, {
            "adr_number": adr_num,
            "title": f"Use {package} for {params['reason']}",
            "context": f"Need {package} for {params['reason']}",
            "decision": f"Add {package} version {version}",
            "consequences": {
                "positive": ["Solves immediate need", "Well-maintained package"],
                "negative": ["Additional dependency", "Potential security surface"]
            },
            "alternatives": [],
            "status": "Accepted"
        })

        # Notify code_developer
        db.send_notification("code_developer", {
            "type": "dependency_approved",
            "package": package,
            "version": version,
            "message": f"{package} approved and added"
        })

        return {
            "success": True,
            "package_name": package,
            "version": version,
            "approved": True,
            "adr_created": f"ADR-{adr_num:03d}-use-{package}.md"
        }
    else:
        # Notify code_developer of rejection
        db.send_notification("code_developer", {
            "type": "dependency_rejected",
            "package": package,
            "reason": params.get("rejection_reason", "Not approved")
        })

        return {
            "success": True,
            "package_name": package,
            "approved": False
        }
```

---

### Command: architect.merge_worktree_branches

**Purpose**: Merge completed work from roadmap-implementation_task-* branches back to roadmap

**Tables**:
- Read: `specs_task`, `orchestrator_task`
- Write: `system_audit`

**Files**:
- Git operations on worktree branches

**Required Skills**: `git_workflow_automation`

**Required Tools**: `git`

**Input Parameters**:
```yaml
worktree_branch: string      # Branch to merge (e.g., "roadmap-implementation_task-TASK-31-1")
task_id: string              # Task ID for validation
run_tests: boolean           # Run tests before merge (default: true)
resolve_conflicts: boolean   # Auto-resolve conflicts (default: false)
```

**Output**:
```json
{
  "success": true,
  "worktree_branch": "roadmap-implementation_task-TASK-31-1",
  "merge_commit": "abc123def",
  "conflicts_resolved": 0,
  "tests_passed": true,
  "notification_sent": true
}
```

**Success Criteria**:
- ✅ Merge executed successfully
- ✅ Tests pass (if run_tests=true)
- ✅ Conflicts resolved (manually or auto)
- ✅ Merge commit created
- ✅ Notification sent to orchestrator for cleanup

**External Tool Usage**:

```bash
# Switch to roadmap branch
git checkout roadmap
git pull origin roadmap

# Merge worktree branch
git merge roadmap-implementation_task-TASK-31-1 --no-ff -m "Merge parallel work..."

# Run tests
pytest

# Push to remote
git push origin roadmap
```

**Database Operations**:

```python
def merge_worktree_branches(db: DomainWrapper, params: dict):
    worktree_branch = params["worktree_branch"]
    task_id = params["task_id"]

    # Validate task is complete
    task = db.read("specs_task", {"id": task_id})[0]
    if task["status"] != "completed":
        return {
            "success": False,
            "error": f"Task {task_id} not completed yet"
        }

    # Switch to roadmap branch
    subprocess.run(["git", "checkout", "roadmap"], check=True)
    subprocess.run(["git", "pull", "origin", "roadmap"], check=True)

    # Merge
    merge_msg = f"""Merge parallel work from {worktree_branch}: {task_id}

Features:
- {task['scope_description']}

Tests: {'Passed' if params.get('run_tests', True) else 'Skipped'}
Status: Ready for integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

    result = subprocess.run(
        ["git", "merge", worktree_branch, "--no-ff", "-m", merge_msg],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        # Conflicts detected
        if params.get("resolve_conflicts", False):
            # Auto-resolve (ROADMAP.md conflicts common)
            resolve_roadmap_conflicts()
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "--no-edit"], check=True)
        else:
            return {
                "success": False,
                "error": "Merge conflicts detected",
                "conflicts": get_conflict_files()
            }

    # Run tests if requested
    if params.get("run_tests", True):
        test_result = subprocess.run(["pytest"], capture_output=True)
        if test_result.returncode != 0:
            return {
                "success": False,
                "error": "Tests failed after merge"
            }

    # Push to remote
    subprocess.run(["git", "push", "origin", "roadmap"], check=True)

    # Get merge commit
    merge_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True
    ).stdout.strip()

    # Notify orchestrator to clean up worktree
    db.send_notification("orchestrator", {
        "type": "merge_complete",
        "worktree_branch": worktree_branch,
        "task_id": task_id,
        "merge_commit": merge_commit,
        "message": f"Merge complete for {worktree_branch}, ready for cleanup"
    })

    return {
        "success": True,
        "worktree_branch": worktree_branch,
        "merge_commit": merge_commit,
        "tests_passed": True,
        "notification_sent": True
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| MergeConflictError | Conflicting changes | Resolve manually or auto-resolve |
| TestFailureError | Tests fail after merge | Fix tests, re-merge |
| GitError | Git operation failed | Check git status, retry |
| TaskNotCompleteError | Task not finished | Wait for completion |

---

## Implementation Tasks

### Task Breakdown (CFR-007 Compliant: <30% context each)

#### TASK-103-1: Specification Management Commands (10 hours)

**Scope**:
- Implement `create_spec` command
- Implement `link_spec_to_priority` command
- Implement `validate_spec_completeness` command
- Implement `update_spec` command

**Files**:
- Create: `.claude/commands/agents/architect/create_spec.md`
- Create: `.claude/commands/agents/architect/link_spec_to_priority.md`
- Create: `.claude/commands/agents/architect/validate_spec_completeness.md`
- Create: `.claude/commands/agents/architect/update_spec.md`
- Create: `coffee_maker/commands/architect/specification_management.py`

**Tests**:
- Create: `tests/unit/test_architect_specification_management.py`
- Test hierarchical spec creation
- Test spec linking
- Test validation logic
- Test spec updates with versioning

**Context Size**: ~28% (4 commands + hierarchical JSON handling + tests)

**Success Criteria**:
- ✅ Specs created in database with JSON content
- ✅ Hierarchical structure enables progressive disclosure
- ✅ Linking works bidirectionally
- ✅ Validation comprehensive

---

#### TASK-103-2: Task Management Commands (8 hours)

**Scope**:
- Implement `create_implementation_tasks` command
- Implement `define_task_dependencies` command
- Implement `update_task_status` command

**Files**:
- Create: `.claude/commands/agents/architect/create_implementation_tasks.md`
- Create: `.claude/commands/agents/architect/define_task_dependencies.md`
- Create: `.claude/commands/agents/architect/update_task_status.md`
- Create: `coffee_maker/commands/architect/task_management.py`

**Tests**:
- Create: `tests/unit/test_architect_task_management.py`
- Test task decomposition
- Test dependency creation
- Test status updates
- Test file conflict prevention

**Context Size**: ~24% (3 commands + ImplementationTaskCreator integration + tests)

**Success Criteria**:
- ✅ Tasks created with correct granularity
- ✅ Dependencies enforce ordering
- ✅ File conflicts prevented
- ✅ Status updates tracked

---

#### TASK-103-3: Architecture Governance Commands (12 hours)

**Scope**:
- Implement `generate_adr` command
- Implement `update_guidelines` command
- Implement `update_cfrs` command
- Implement `approve_dependency` command
- Implement `merge_worktree_branches` command

**Files**:
- Create: `.claude/commands/agents/architect/generate_adr.md`
- Create: `.claude/commands/agents/architect/update_guidelines.md`
- Create: `.claude/commands/agents/architect/update_cfrs.md`
- Create: `.claude/commands/agents/architect/approve_dependency.md`
- Create: `.claude/commands/agents/architect/merge_worktree_branches.md`
- Create: `coffee_maker/commands/architect/governance.py`

**Tests**:
- Create: `tests/unit/test_architect_governance.py`
- Test ADR generation
- Test guideline updates
- Test CFR updates
- Test dependency approval (mock poetry)
- Test worktree merging (mock git)

**Context Size**: ~29% (5 commands + file operations + git integration + tests)

**Success Criteria**:
- ✅ ADRs formatted correctly
- ✅ Guidelines follow template
- ✅ Dependency approval workflow complete
- ✅ Worktree merging handles conflicts

---

## Total Effort Estimate

| Task | Hours | Complexity | Context % |
|------|-------|------------|-----------|
| TASK-103-1: Specification Management | 10 | High | 28% |
| TASK-103-2: Task Management | 8 | Medium | 24% |
| TASK-103-3: Architecture Governance | 12 | High | 29% |
| **TOTAL** | **30** | **High** | **<30% each** ✅ |

---

## Success Criteria

### Functional
- ✅ All 12 commands implemented
- ✅ Hierarchical specs enable progressive disclosure
- ✅ Task decomposition prevents file conflicts
- ✅ Dependencies enforce execution order
- ✅ ADRs/guidelines generated correctly
- ✅ Worktree merging automated

### Technical
- ✅ All unit tests pass (>90% coverage)
- ✅ Database-first spec storage
- ✅ JSON content format validated
- ✅ Git operations safe
- ✅ Context budget <30% per task

### Integration
- ✅ Commands load via CommandLoader
- ✅ Permissions enforced (write access to specs_*)
- ✅ Skills integrate correctly
- ✅ External tools (git, poetry) work

---

## Dependencies

### Python Packages
- `frontmatter` - Markdown parsing (Tier 1 approved)
- Existing: `sqlite3`, `json`, `subprocess`

### External Tools
- `git` - Worktree and branch management
- `poetry` - Dependency management
- `pytest` - Test execution

### Existing Infrastructure
- ImplementationTaskCreator - Task decomposition
- TechnicalSpecSkill - Spec handling
- SkillLoader - For architecture skills

---

## Related Documents

- [SPEC-100: Unified Agent Commands Architecture (Master)](SPEC-100-unified-agent-commands-architecture.md)
- [SPEC-101: Foundation Infrastructure](SPEC-101-foundation-infrastructure.md)
- [SPEC-102: Project Manager Commands](SPEC-102-project-manager-commands.md)
- [.claude/agents/architect.md](../../../.claude/agents/architect.md)
- [CFR-011: Daily Integration](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-011)
- [CFR-013: Git Workflow](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013)

---

**Specification Status**: Draft - Ready for Review
**Estimated Effort**: 30 hours
**Complexity**: High
**Context Budget**: All tasks <30% ✅
**Dependencies**: SPEC-101 (Foundation), SPEC-102 (Project Manager)
