# Command Redundancy Analysis

## Current Command Count (Far Too Many!)

### Total: ~100 Commands Across All Agents

| Agent | SPEC | Command Count | Status |
|-------|------|---------------|---------|
| project_manager | SPEC-102 | 15 commands | Too many |
| architect | SPEC-103 | 13 commands | Too many |
| code_developer | SPEC-104 | 14 commands | Too many |
| code_reviewer | SPEC-105 | 13 commands | Too many |
| orchestrator | SPEC-106 | 15 commands | Too many |
| assistant | SPEC-114 | 11 commands | Too many |
| user_listener | SPEC-114 | 9 commands | Excessive |
| ux_design_expert | SPEC-114 | 10 commands | Too many |

## Redundancy Analysis

### 1. Project Manager (15 → 5 commands)

**Current Commands:**
- check_priority_status
- get_priority_details
- list_all_priorities
- update_priority_metadata
- developer_status
- notifications
- check_dependency
- add_dependency
- monitor_github_pr
- track_github_issue
- sync_github_status
- roadmap_stats
- feature_stats
- spec_stats
- audit_trail

**REDUNDANT/AGGREGATABLE:**
- `check_priority_status`, `get_priority_details`, `list_all_priorities` → **roadmap** (single command with parameters)
- `developer_status`, `notifications` → **status** (combined status command)
- `check_dependency`, `add_dependency` → **dependencies** (single command with action parameter)
- `monitor_github_pr`, `track_github_issue`, `sync_github_status` → **github** (single command)
- `roadmap_stats`, `feature_stats`, `spec_stats` → **stats** (single command with type parameter)

**PROPOSED: 5 commands**
1. **roadmap** - All ROADMAP operations (list, details, update)
2. **status** - Developer and notification status
3. **dependencies** - Manage all dependencies
4. **github** - All GitHub operations
5. **stats** - All statistics and metrics

### 2. Architect (13 → 5 commands)

**Current Commands:**
- create_spec
- update_spec
- approve_spec
- deprecate_spec
- link_spec_to_priority
- decompose_spec_to_tasks
- update_task_order
- merge_task_branch
- create_adr
- update_guidelines
- update_styleguide
- design_api
- validate_architecture

**REDUNDANT/AGGREGATABLE:**
- `create_spec`, `update_spec`, `approve_spec`, `deprecate_spec`, `link_spec_to_priority` → **spec** (with action parameter)
- `decompose_spec_to_tasks`, `update_task_order`, `merge_task_branch` → **tasks**
- `create_adr`, `update_guidelines`, `update_styleguide` → **documentation**
- `design_api`, `validate_architecture` → Merge into **spec** or **review**

**PROPOSED: 5 commands**
1. **spec** - All spec operations (CRUD + approval)
2. **tasks** - Task decomposition and management
3. **documentation** - ADRs, guidelines, style guides
4. **review** - Architecture validation and review
5. **dependencies** - Manage technical dependencies

### 3. Code Developer (14 → 6 commands)

**Current Commands:**
- claim_priority
- load_spec
- update_implementation_status
- record_commit
- complete_implementation
- request_code_review
- create_pull_request
- run_test_suite
- fix_failing_tests
- run_pre_commit_hooks
- implement_bug_fix
- track_metrics
- generate_coverage_report
- update_claude_config

**REDUNDANT/AGGREGATABLE:**
- `claim_priority`, `update_implementation_status`, `complete_implementation` → **implement** (lifecycle command)
- `run_test_suite`, `fix_failing_tests`, `generate_coverage_report` → **test**
- `record_commit`, `create_pull_request` → **git**
- `run_pre_commit_hooks`, `track_metrics` → Merge into **test** or **quality**

**PROPOSED: 6 commands**
1. **implement** - Claim, update, complete workflow
2. **test** - Run tests, fix failures, coverage
3. **git** - Commits and pull requests
4. **review** - Request and track reviews
5. **quality** - Pre-commit, metrics, code quality
6. **config** - Update configurations

### 4. Code Reviewer (13 → 4 commands)

**Current Commands:**
- detect_new_commits
- generate_review_report
- notify_architect
- check_style_compliance
- run_security_scan
- analyze_complexity
- check_test_coverage
- validate_type_hints
- check_architecture_compliance
- track_issue_resolution
- generate_quality_score
- review_documentation
- validate_dod_compliance

**REDUNDANT/AGGREGATABLE:**
- All analysis commands → **analyze** (with type: style|security|complexity|coverage|types|architecture|docs)
- `generate_review_report`, `generate_quality_score`, `validate_dod_compliance` → **review**
- `detect_new_commits`, `track_issue_resolution` → **monitor**

**PROPOSED: 4 commands**
1. **review** - Complete review with report and scoring
2. **analyze** - All types of analysis (parameterized)
3. **monitor** - Track commits and issues
4. **notify** - Send notifications to relevant agents

### 5. Orchestrator (15 → 5 commands)

**Current Commands:**
- spawn_agent_session
- kill_stalled_agent
- auto_restart_agent
- monitor_agent_lifecycle
- handle_agent_errors
- coordinate_dependencies
- find_available_work
- create_parallel_tasks
- route_inter_agent_messages
- create_worktree
- cleanup_worktrees
- merge_completed_work
- detect_deadlocks
- monitor_resource_usage
- generate_activity_summary

**REDUNDANT/AGGREGATABLE:**
- `spawn_agent_session`, `kill_stalled_agent`, `auto_restart_agent`, `monitor_agent_lifecycle` → **agents**
- `coordinate_dependencies`, `find_available_work`, `create_parallel_tasks`, `detect_deadlocks` → **orchestrate**
- `create_worktree`, `cleanup_worktrees`, `merge_completed_work` → **worktree**
- `monitor_resource_usage`, `generate_activity_summary` → **monitor**

**PROPOSED: 5 commands**
1. **agents** - Lifecycle management (spawn, kill, restart, monitor)
2. **orchestrate** - Work coordination and scheduling
3. **worktree** - Git worktree operations
4. **messages** - Inter-agent communication
5. **monitor** - Resources and activity monitoring

### 6. Assistant (11 → 4 commands)

**Current Commands:**
- create_demo
- record_demo_session
- validate_demo_output
- report_bug
- track_bug_status
- link_bug_to_priority
- classify_request
- route_to_agent
- monitor_delegation
- generate_docs
- update_readme

**REDUNDANT/AGGREGATABLE:**
- `create_demo`, `record_demo_session`, `validate_demo_output` → **demo**
- `report_bug`, `track_bug_status`, `link_bug_to_priority` → **bug**
- `classify_request`, `route_to_agent`, `monitor_delegation` → **delegate**
- `generate_docs`, `update_readme` → **docs**

**PROPOSED: 4 commands**
1. **demo** - Create and manage demos
2. **bug** - Bug reporting and tracking
3. **delegate** - Intelligent request routing
4. **docs** - Documentation generation

### 7. User Listener (9 → 3 commands)

**Current Commands:**
- classify_intent
- extract_entities
- determine_agent
- route_request
- queue_for_agent
- handle_fallback
- track_conversation
- update_context
- manage_session

**REDUNDANT/AGGREGATABLE:**
- `classify_intent`, `extract_entities`, `determine_agent` → **understand**
- `route_request`, `queue_for_agent`, `handle_fallback` → **route**
- `track_conversation`, `update_context`, `manage_session` → **conversation**

**PROPOSED: 3 commands**
1. **understand** - Intent/entity extraction and classification
2. **route** - Route to appropriate agent
3. **conversation** - Manage conversation state

### 8. UX Design Expert (10 → 4 commands)

**Current Commands:**
- generate_ui_spec
- create_component_spec
- validate_accessibility
- manage_component_library
- generate_tailwind_config
- create_design_tokens
- configure_chart_theme
- review_ui_implementation
- suggest_improvements
- track_design_debt

**REDUNDANT/AGGREGATABLE:**
- `generate_ui_spec`, `create_component_spec` → **design**
- `manage_component_library`, `generate_tailwind_config`, `create_design_tokens`, `configure_chart_theme` → **components**
- `review_ui_implementation`, `suggest_improvements`, `validate_accessibility` → **review**

**PROPOSED: 4 commands**
1. **design** - Create UI/component specifications
2. **components** - Manage component library and tokens
3. **review** - Review implementations and accessibility
4. **debt** - Track and manage design debt

## Summary: From 100 → 37 Commands

### Proposed Consolidated Command Count

| Agent | Original | Proposed | Reduction |
|-------|----------|----------|-----------|
| project_manager | 15 | 5 | -67% |
| architect | 13 | 5 | -62% |
| code_developer | 14 | 6 | -57% |
| code_reviewer | 13 | 4 | -69% |
| orchestrator | 15 | 5 | -67% |
| assistant | 11 | 4 | -64% |
| user_listener | 9 | 3 | -67% |
| ux_design_expert | 10 | 4 | -60% |
| **TOTAL** | **100** | **36** | **-64%** |

## Design Principles for Consolidation

1. **Parameter-Driven**: Use parameters to specify sub-actions rather than separate commands
2. **Lifecycle Commands**: Combine related workflow steps (e.g., claim → implement → complete)
3. **Single Responsibility**: Each command has one clear domain (e.g., "git", "test", "review")
4. **Consistency**: Similar patterns across agents (most have ~4-6 commands)
5. **Discoverability**: Fewer commands are easier to remember and use

## Implementation Approach

Each consolidated command would use parameters to specify the action:

```python
# Instead of:
code_developer.run_test_suite()
code_developer.fix_failing_tests()
code_developer.generate_coverage_report()

# Use:
code_developer.test(action="run")
code_developer.test(action="fix", test_name="test_auth")
code_developer.test(action="coverage")
```

This reduces cognitive load while maintaining full functionality.
