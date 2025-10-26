# Complete Agent Commands Matrix

## Overview

This document maps ALL agent responsibilities to commands, including:
1. **Documented workflows** from introspection tools ✅
2. **Additional responsibilities** from agent prompts not yet in introspection 🆕
3. **Required skills** for each command

---

## ARCHITECT Agent Commands

### From Introspection (Existing Workflows) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `create_spec` | INSERT specs_specification | Create technical specification | technical_specification_handling |
| `link_spec_to_priority` | UPDATE roadmap_priority.spec_id | Link spec to roadmap item | database_schema_guide |
| `create_implementation_tasks` | INSERT specs_task | Break spec into tasks | task_separator |
| `define_task_dependencies` | INSERT specs_task_dependency | Define task order | dependency_impact |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `generate_adr` | INSERT arch_adrs (new table) | Create Architectural Decision Record | technical_specification_handling |
| `approve_dependency` | UPDATE pyproject.toml (file) | Three-tier dependency approval | dependency_conflict_resolver |
| `update_guidelines` | UPDATE docs/architecture/guidelines/* | Maintain architecture guidelines | architecture_analysis |
| `merge_worktree_branches` | Git operations | Merge implementation branches | merge_worktree_branches |
| `review_code_quality` | READ review_code_review | Review code_reviewer findings | code_review_history |
| `create_poc` | CREATE docs/architecture/pocs/* | Design POC for complex features | proactive_refactoring_analysis |
| `validate_spec_completeness` | CHECK specs_specification | Ensure specs meet standards | technical_specification_handling |
| `update_cfrs` | UPDATE docs/roadmap/CFRs | Maintain Critical Functional Requirements | architecture_reuse_check |

---

## CODE_DEVELOPER Agent Commands

### From Introspection (Existing Workflows) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `claim_priority` | UPDATE roadmap_priority.status | Start work on priority | roadmap_database_handling |
| `load_spec` | READ specs_specification | Get implementation details | technical_specification_handling |
| `update_implementation_status` | UPDATE roadmap_priority | Track progress | roadmap_database_handling |
| `record_commit` | INSERT review_commit | Track commits | git_workflow_automation |
| `complete_implementation` | UPDATE roadmap_priority.status | Mark complete | dod_verification |
| `request_code_review` | INSERT notifications | Notify code_reviewer | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `run_test_suite` | Execute pytest | Run all tests | test-failure-analysis |
| `fix_failing_tests` | UPDATE code files | Debug and fix tests | test-failure-analysis |
| `create_pull_request` | GitHub API | Create PR on GitHub | git_workflow_automation |
| `implement_bug_fix` | UPDATE code + INSERT review_commit | Fix reported bugs | bug_tracking_helper |
| `update_implementation_metrics` | INSERT metrics_subtask | Track time/effort | None |
| `run_pre_commit_hooks` | Execute pre-commit | Ensure code quality | None |
| `generate_test_coverage` | Execute pytest --cov | Check coverage >80% | test-failure-analysis |
| `update_claude_config` | UPDATE .claude/* | Maintain Claude config | None |

---

## PROJECT_MANAGER Agent Commands

### From Introspection (Existing Workflows) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `parse_roadmap` | INSERT/UPDATE roadmap_priority | Sync ROADMAP.md to database | roadmap_database_handling |
| `update_priority_status` | UPDATE roadmap_priority.status | Change priority status | roadmap_database_handling |
| `create_notification` | INSERT notifications | Notify other agents | None |
| `process_notifications` | UPDATE notifications.status | Handle incoming notifications | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `verify_dod_puppeteer` | Puppeteer MCP | Visual DoD verification | verify-dod-puppeteer |
| `monitor_github_prs` | GitHub API (gh pr list) | Check PR status | github_integration |
| `monitor_github_issues` | GitHub API (gh issue list) | Track issues | github_integration |
| `analyze_project_health` | READ multiple tables | Generate health metrics | roadmap_health |
| `create_roadmap_report` | AGGREGATE data | Weekly/monthly reports | roadmap_health |
| `detect_stale_priorities` | CHECK implementation_started_at | Find stuck work | roadmap_health |
| `send_agent_notification` | INSERT pm_notifications | Agent-specific notifications | None |
| `strategic_planning` | ANALYZE roadmap_priority | Recommend next priorities | auto_plan |
| `track_bug_reports` | READ orchestrator_bug | Monitor bug status | bug_tracking_helper |
| `update_roadmap_metadata` | UPDATE roadmap_metadata | Update header/footer | None |

---

## CODE_REVIEWER Agent Commands

### From Introspection (Existing Workflows) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `detect_new_commits` | READ review_commit | Find commits to review | None |
| `generate_review_report` | INSERT review_code_review | Create review summary | security_audit_skill |
| `notify_architect` | INSERT notifications | Send findings to architect | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `check_style_compliance` | Execute black, flake8 | Verify style guide | None |
| `run_security_scan` | Execute bandit | Security vulnerability check | security_audit_skill |
| `analyze_complexity` | Execute radon | Complexity metrics | code_forensics |
| `check_test_coverage` | Read coverage report | Verify >80% coverage | None |
| `validate_type_hints` | Execute mypy | Type checking | None |
| `check_architecture_compliance` | Compare to specs | Verify follows design | technical_specification_handling |
| `track_issue_resolution` | UPDATE review_code_review | Monitor fix status | None |
| `generate_quality_score` | Calculate 0-100 score | Overall quality metric | None |
| `review_documentation` | CHECK docstrings | Documentation completeness | None |
| `validate_dod_compliance` | CHECK against DoD | Ensure criteria met | dod_verification |

---

## ORCHESTRATOR Agent Commands

### From Introspection (Existing Workflows) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `find_available_work` | READ roadmap_priority | Query for ready tasks | None |
| `create_parallel_tasks` | INSERT orchestrator_task | Track parallel execution | orchestrator_agent_management |
| `monitor_agent_lifecycle` | UPDATE agent_lifecycle | Track agent health | orchestrator_health_monitor |
| `merge_completed_work` | Git merge operations | Merge task branches | None |
| `cleanup_worktrees` | Git worktree remove | Clean up after tasks | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `spawn_agent_session` | Launch Claude session | Start new agent | orchestrator_agent_management |
| `kill_stalled_agent` | Terminate process | Stop hung agents | orchestrator_health_monitor |
| `detect_deadlocks` | ANALYZE agent_lifecycle | Find circular waits | orchestrator_health_monitor |
| `auto_restart_agent` | Restart on failure | Fault tolerance | orchestrator_health_monitor |
| `route_inter_agent_message` | INSERT agent_message | Message routing | None |
| `monitor_resource_usage` | System metrics | Track CPU/memory | activity-summary |
| `generate_activity_summary` | AGGREGATE agent_lifecycle | Daily summaries | activity-summary |
| `coordinate_dependencies` | CHECK specs_task_dependency | Ensure order | None |
| `parallel_execution_planning` | ANALYZE dependencies | Optimize parallelism | parallel-execution |
| `handle_agent_errors` | UPDATE agent_lifecycle.error | Error recovery | orchestrator_health_monitor |

---

## ASSISTANT Agent Commands

### From Introspection (Minimal Coverage) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `answer_question` | READ multiple tables | General Q&A | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `create_demo` | Puppeteer MCP | Visual demonstrations | puppeteer_skills |
| `test_feature` | Puppeteer + validation | Interactive testing | puppeteer_skills |
| `detect_bug_during_demo` | Analyze behavior | Find bugs in demos | bug_tracking_helper |
| `report_bug_comprehensive` | INSERT orchestrator_bug | Detailed bug reports | bug_tracking_helper |
| `delegate_to_specialist` | Route to other agents | Smart delegation | None |
| `explain_code` | READ + analyze | Code explanations | code-explainer |
| `search_documentation` | READ docs/* | Find relevant docs | None |
| `check_logs` | READ log files | Debug issues | None |
| `run_diagnostics` | Execute commands | System health check | None |
| `create_tutorial` | Puppeteer + markdown | Create tutorials | puppeteer_skills |

---

## USER_LISTENER Agent Commands

### From Introspection (Minimal Coverage) ✅

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `receive_input` | Process user input | REPL interface | None |

### From Agent Prompt (Additional Responsibilities) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `classify_intent` | Pattern match + AI | Determine user intent | None |
| `route_to_agent` | Delegate request | Send to specialist | None |
| `maintain_conversation` | Track context | Multi-turn handling | None |
| `play_sound_notification` | Audio alert | User feedback (CFR-009) | None |
| `format_response` | Rich formatting | Display responses | None |
| `track_session` | INSERT user_sessions | Session management | None |
| `show_agent_status` | READ agent_lifecycle | Display agent states | None |
| `handle_commands` | Process /commands | Built-in commands | None |

---

## UX_DESIGN_EXPERT Agent Commands

### From Agent Prompt (Not in Introspection) 🆕

| Command | Table/Operation | Purpose | Required Skills |
|---------|----------------|---------|-----------------|
| `design_interface` | CREATE design specs | UI/UX design | None |
| `create_component_library` | Design components | Reusable components | None |
| `define_design_tokens` | Colors, spacing, etc. | Design system | None |
| `configure_highcharts` | Chart configurations | Data visualization | None |
| `optimize_user_flow` | UX improvements | Simplify workflows | None |
| `create_tailwind_config` | Tailwind setup | CSS framework | None |
| `design_dashboard_layout` | Layout design | Dashboard UX | None |
| `accessibility_audit` | WCAG compliance | A11y check | None |
| `responsive_design` | Mobile optimization | Multi-device | None |
| `create_style_guide` | Documentation | Design docs | None |

---

## Command Template Structure

```markdown
---
command: agent.action
agent: architect|code_developer|project_manager|...
action: specific_action_name
tables:
  write: [table1, table2]  # Tables this command writes to
  read: [table3, table4]   # Tables this command reads from
files:
  write: [path1, path2]    # Files this command writes
  read: [path3, path4]     # Files this command reads
required_skills: [skill1, skill2]
required_tools: [git, gh, pytest, puppeteer]
---

# Command: agent.action

## Purpose
Clear description of what this command does

## Trigger
When/why this command is executed:
- Event that triggers it
- Condition that requires it
- User action that initiates it

## Input Parameters
- param1: type - description
- param2: type - description

## Database Operations
```sql
-- Actual SQL that will be executed
```

## File Operations
```python
# File read/write operations
```

## External Tools
```bash
# External commands (git, gh, pytest, etc.)
```

## Required Skills
- skill1: How it's used
- skill2: How it's used

## Success Criteria
- [ ] Condition 1
- [ ] Condition 2

## Error Handling
- Error type 1: How to handle
- Error type 2: How to handle

## Downstream Effects
What happens after this command succeeds:
- Next command triggered
- Notification sent
- State change

## Example Usage
```python
# How to invoke this command
```
```

---

## Implementation Priority

### Phase 1: Core Operations (Week 1)
Commands that match existing introspection workflows:
- project_manager.parse_roadmap
- architect.create_spec
- code_developer.claim_priority
- orchestrator.find_available_work

### Phase 2: Missing Operations (Week 2)
Commands from prompts not in introspection:
- architect.generate_adr
- project_manager.verify_dod_puppeteer
- code_reviewer.run_security_scan
- assistant.create_demo

### Phase 3: Enhancement Operations (Week 3)
Commands that enhance existing workflows:
- project_manager.analyze_project_health
- orchestrator.detect_deadlocks
- code_developer.generate_test_coverage

### Phase 4: New Capabilities (Week 4)
Commands for features not yet implemented:
- ux_design_expert (all commands)
- user_listener.show_agent_status
- assistant.create_tutorial

---

## Skills Mapping

### Required Skills by Agent

**Architect**:
- technical_specification_handling ✅
- database_schema_guide ✅
- task_separator ✅
- dependency_impact ✅
- architecture_analysis 🆕
- merge_worktree_branches 🆕
- code_review_history 🆕

**Code Developer**:
- roadmap_database_handling ✅
- technical_specification_handling ✅
- git_workflow_automation ✅
- dod_verification ✅
- test-failure-analysis 🆕
- bug_tracking_helper 🆕

**Project Manager**:
- roadmap_database_handling ✅
- verify-dod-puppeteer 🆕
- github_integration 🆕
- roadmap_health 🆕
- auto_plan 🆕
- bug_tracking_helper 🆕

**Code Reviewer**:
- security_audit_skill 🆕
- code_forensics 🆕
- dod_verification 🆕

**Orchestrator**:
- orchestrator_agent_management ✅
- orchestrator_health_monitor 🆕
- activity-summary 🆕
- parallel-execution 🆕

**Assistant**:
- puppeteer_skills 🆕
- bug_tracking_helper 🆕
- code-explainer 🆕

---

## Validation Checklist

For each command, verify:
1. ✅ **Exists in introspection** OR **documented in agent prompt**
2. ✅ **Table permissions** align with domain ownership
3. ✅ **Required skills** are available or can be created
4. ✅ **Downstream effects** are documented
5. ✅ **Error handling** is comprehensive

---

**Document Version**: 1.0
**Date**: 2025-10-26
**Status**: Complete Command Matrix
**Coverage**: 100% of documented + prompt responsibilities
