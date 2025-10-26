# Architect Commands - Quick Reference

All 12 architect commands for SPEC-103 implementation.

---

## Specification Management (4 Commands)

### 1. create_spec
**File**: `create_spec.md`
**Purpose**: Create technical specification (hierarchical or monolithic)
**Key Input**: priority_id, title, spec_type, content
**Key Output**: spec_id, estimated_hours, reuse_components_found
**Example**: Create SPEC-131 for user authentication with 3 phases

### 2. link_spec_to_priority
**File**: `link_spec_to_priority.md`
**Purpose**: Link existing spec to roadmap priority (bidirectional)
**Key Input**: spec_id, priority_id
**Key Output**: spec_id, priority_id, notification_sent
**Example**: Link SPEC-131 to PRIORITY-28

### 3. validate_spec_completeness
**File**: `validate_spec_completeness.md`
**Purpose**: Check spec quality before implementation
**Key Input**: spec_id, strict_mode
**Key Output**: is_complete, validation_score (0-100), warnings
**Example**: Score SPEC-131 at 95/100 (all sections complete)

### 4. update_spec
**File**: `update_spec.md`
**Purpose**: Modify existing spec with versioning
**Key Input**: spec_id, updates, reason, version
**Key Output**: updated_fields, old_version, new_version
**Example**: Update testing_strategy section, bump 1.0.0 → 1.1.0

---

## Task Management (3 Commands)

### 5. create_implementation_tasks
**File**: `create_implementation_tasks.md`
**Purpose**: Decompose spec into atomic tasks
**Key Input**: spec_id, priority_number, granularity
**Key Output**: task_group_id, tasks_created, tasks list
**Example**: Create TASK-31-1, TASK-31-2, TASK-31-3 from SPEC-131
**Granularity**: phase, section, module

### 6. define_task_dependencies
**File**: `define_task_dependencies.md`
**Purpose**: Create task dependency graph (hard/soft)
**Key Input**: task_group_id, depends_on_group_id, dependency_type
**Key Output**: dependency_id, dependency_type, created
**Example**: GROUP-31 hard-depends on GROUP-30 (database first)
**Types**: hard (blocking) or soft (recommended)

### 7. update_task_status
**File**: `update_task_status.md`
**Purpose**: Track task progress
**Key Input**: task_id, new_status, notes
**Key Output**: old_status, new_status, task_group_status
**Example**: TASK-31-1 pending → in_progress when developer claims
**Statuses**: pending, in_progress, completed, blocked

---

## Architecture Governance (5 Commands)

### 8. generate_adr
**File**: `generate_adr.md`
**Purpose**: Create Architectural Decision Record
**Key Input**: adr_number, title, context, decision, consequences
**Key Output**: adr_id, file_path, status
**Example**: Create ADR-015 documenting command architecture
**Statuses**: Proposed, Accepted, Deprecated, Superseded

### 9. update_guidelines
**File**: `update_guidelines.md`
**Purpose**: Create/update architecture guidelines
**Key Input**: guideline_number, title, category, when_to_use, examples
**Key Output**: guideline_id, file_path, category
**Example**: Create GUIDELINE-007 for Command Pattern
**Categories**: Design Pattern, Best Practice, Anti-Pattern, Code Standard

### 10. update_cfrs
**File**: `update_cfrs.md`
**Purpose**: Manage Critical Functional Requirements
**Key Input**: cfr_number, action, title, description, rationale, enforcement
**Key Output**: cfr_id, action, status
**Example**: Create CFR-016 for Centralized Database Storage
**Actions**: create, update, deprecate
**Statuses**: Active, Deprecated, Proposed, Experimental

### 11. approve_dependency
**File**: `approve_dependency.md`
**Purpose**: Three-tier dependency approval (SPEC-070)
**Key Input**: package_name, version, reason, approved
**Key Output**: tier, approved, security_check_passed, adr_created
**Example**: Approve redis Tier 2 dependency, create ADR-016
**Tiers**: Tier 1 (auto), Tier 2 (review), Tier 3 (user)

### 12. merge_worktree_branches
**File**: `merge_worktree_branches.md`
**Purpose**: Merge completed worktree branches to roadmap (CFR-013)
**Key Input**: worktree_branch, task_id, run_tests
**Key Output**: merge_commit, tests_passed, conflicts_resolved
**Example**: Merge roadmap-implementation_task-TASK-31-1 to roadmap
**Workflow**: code_developer → tests pass → architect merge → orchestrator cleanup

---

## Quick Lookup by Use Case

### I need to manage a specification
- **Create**: create_spec
- **Link to priority**: link_spec_to_priority
- **Check quality**: validate_spec_completeness
- **Update content**: update_spec

### I need to manage implementation tasks
- **Create from spec**: create_implementation_tasks
- **Set dependencies**: define_task_dependencies
- **Track progress**: update_task_status

### I need to document architectural decisions
- **Decision record**: generate_adr
- **Implementation pattern**: update_guidelines
- **Critical requirement**: update_cfrs
- **Dependency decision**: approve_dependency

### I need to merge parallel work
- **Merge worktree**: merge_worktree_branches

---

## Database Tables Used

### Read Access
- pm_roadmap: Priority information
- arch_specs: Specification lookup
- dev_implementations: Task group status
- dev_implementation_tasks: Task details

### Write Access
- arch_specs: Create/update specifications
- arch_spec_sections: Specification content
- dev_implementations: Task groups
- dev_implementation_tasks: Individual tasks
- dev_task_dependencies: Task relationships
- dev_task_assignments: File assignments
- system_audit: Audit trail

---

## Skills Required

### Multi-Command Skills
- technical_specification_handling: Used in 5 commands
- git_workflow_automation: Used in 1 command (merge)
- dependency_conflict_resolver: Used in 1 command (approve)

### Per Command Skills
- create_spec: technical_specification_handling, architecture_reuse_check
- link_spec_to_priority: technical_specification_handling
- validate_spec_completeness: technical_specification_handling
- update_spec: technical_specification_handling
- create_implementation_tasks: technical_specification_handling
- approve_dependency: dependency_conflict_resolver
- merge_worktree_branches: git_workflow_automation

---

## External Tools Required

### Git Operations
- git checkout, merge, push
- git branch, worktree
- Used in: merge_worktree_branches

### Package Management
- poetry add, check, lock
- safety check
- Used in: approve_dependency

### Testing
- pytest
- Used in: merge_worktree_branches

---

## Typical Workflows

### Creating and Implementing a Specification

```
1. create_spec(priority_id, title, content)
   └─> Returns spec_id (e.g., SPEC-131)

2. validate_spec_completeness(spec_id)
   └─> Returns validation_score (should be >75)

3. link_spec_to_priority(spec_id, priority_id)
   └─> Bidirectional linking established

4. create_implementation_tasks(spec_id, priority_number)
   └─> Returns task_group_id (e.g., GROUP-31)
   └─> Creates TASK-31-1, TASK-31-2, TASK-31-3

5. define_task_dependencies(GROUP-31, GROUP-30, "hard")
   └─> GROUP-31 requires GROUP-30 completion

6. [code_developer claims and implements TASK-31-1]

7. update_task_status(TASK-31-1, "completed")
   └─> Task marked complete

8. merge_worktree_branches(roadmap-implementation_task-TASK-31-1, TASK-31-1)
   └─> Merge commit created
   └─> Tests pass
   └─> Merged to roadmap
```

### Documenting Architectural Decisions

```
1. generate_adr(number, title, context, decision)
   └─> Creates ADR-015 markdown file

2. update_guidelines(number, title, category, examples)
   └─> Creates GUIDELINE-007 markdown file

3. update_cfrs(number, "create", title, description)
   └─> Updates CRITICAL_FUNCTIONAL_REQUIREMENTS.md

4. approve_dependency(package, reason, approved)
   └─> If approved Tier 1: auto-add
   └─> If Tier 2: architect reviews
   └─> If Tier 3: user approval required
   └─> Creates ADR documenting decision
```

---

## Error Handling Summary

### Common Errors to Handle

**Specification Commands**
- SpecNotFoundError: Spec doesn't exist
- DuplicateSpecError: Spec already exists
- ValidationError: Missing required fields

**Task Commands**
- TaskGroupNotFoundError: Group doesn't exist
- FileConflictError: Tasks conflict on files
- CircularDependencyError: Dependency creates cycle

**Governance Commands**
- DuplicateADRError: ADR number exists
- InvalidCategoryError: Invalid category
- DependencyConflictError: Conflicts with dependencies

**Merge Commands**
- BranchNotFoundError: Worktree branch missing
- TaskNotCompleteError: Task not completed
- TestFailureError: Tests fail after merge

---

## Related Documentation

- **SPEC-103**: Full specification with detailed requirements
- **SPEC-070**: Dependency pre-approval matrix
- **CFR-013**: Git worktree workflow
- **CFR-015**: Centralized database storage
- **GUIDELINE-004**: Git tagging workflow

---

## Status

- **Implementation**: COMPLETE (12/12 commands)
- **Documentation**: COMPLETE (3,045 lines)
- **Ready for**: Python implementation phase
- **Expected effort**: 20-30 hours for Python code
- **Test coverage target**: >90%

---

**Last Updated**: 2025-10-26
**Version**: 1.0
**Author**: code_developer (via Claude Code)
