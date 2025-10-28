#!/usr/bin/env python3
"""Update all command specifications with consolidated architecture.

This script updates SPEC-103 through SPEC-114 with the new consolidated
command architecture, reducing from ~100 commands to 36 commands across all agents.

Usage:
    python3 update_all_command_specs.py
"""

import sys

sys.path.insert(0, "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent")

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "roadmap.db"

# All specs to update
SPECS = {
    103: {
        "title": "Architect Commands (Consolidated Architecture)",
        "commands_before": 13,
        "commands_after": 5,
        "commands": ["spec", "tasks", "documentation", "review", "dependencies"],
        "estimated_hours": 14.0,
        "roadmap_item_id": "CONSOLIDATION-ARCH",
        "phases": [
            {
                "number": 1,
                "name": "command-definitions",
                "hours": 6.0,
                "description": "Define 5 consolidated commands for architect",
                "content": """## Phase 1: Command Definitions

### 1. spec Command
**Actions**: create, update, approve, deprecate, link
**Purpose**: All technical specification operations (CRUD + workflow)

### 2. tasks Command
**Actions**: decompose, update_order, merge_branch
**Purpose**: Task decomposition and management

### 3. documentation Command
**Actions**: create_adr, update_guidelines, update_styleguide
**Purpose**: ADRs, guidelines, style guides

### 4. review Command
**Actions**: validate_architecture, design_api
**Purpose**: Architecture validation and compliance

### 5. dependencies Command
**Actions**: check, add, evaluate
**Purpose**: Technical dependency management with approval workflow
""",
            },
            {
                "number": 2,
                "name": "implementation",
                "hours": 4.0,
                "description": "Implement command methods with database operations",
                "content": """## Phase 2: Implementation

Private methods for each action:
- _create_spec(), _update_spec(), _approve_spec()
- _decompose_spec_to_tasks(), _update_task_order()
- _create_adr(), _update_guidelines()
- _validate_architecture(), _design_api()
- _check_dependency(), _add_dependency()

Database tables:
- specs_specification (technical specs)
- implementation_tasks (task decomposition)
- adrs (architectural decisions)
- dependencies (dependency tracking)
""",
            },
            {
                "number": 3,
                "name": "testing-and-migration",
                "hours": 4.0,
                "description": "Aliases and tests",
                "content": """## Phase 3: Testing & Migration

### Backward Compatibility
Create aliases for 13 legacy commands with deprecation warnings.

### Tests
- Unit tests (95% coverage)
- Integration tests (full workflows)
- Backward compatibility tests

### Migration Timeline
Week 1-2: Implement with aliases
Week 3-4: Update internal code
Week 5-6: Deprecation warnings
Week 7+: Remove aliases
""",
            },
        ],
    },
    104: {
        "title": "Code Developer Commands (Consolidated Architecture)",
        "commands_before": 14,
        "commands_after": 6,
        "commands": ["implement", "test", "git", "review", "quality", "config"],
        "estimated_hours": 16.0,
        "roadmap_item_id": "CONSOLIDATION-DEV",
        "phases": [
            {
                "number": 1,
                "name": "command-definitions",
                "hours": 8.0,
                "description": "Define 6 consolidated commands",
                "content": """## Phase 1: Command Definitions

### 1. implement Command
**Actions**: claim, load, update_status, record_commit, complete
**Purpose**: Full implementation lifecycle in one command

### 2. test Command
**Actions**: run, fix, coverage
**Purpose**: Run tests, fix failures, generate coverage reports

### 3. git Command
**Actions**: commit, create_pr
**Purpose**: Git operations (commits and pull requests)

### 4. review Command
**Actions**: request, track
**Purpose**: Request and track code reviews

### 5. quality Command
**Actions**: pre_commit, metrics, lint
**Purpose**: Code quality checks

### 6. config Command
**Actions**: update_claude, update_config
**Purpose**: Configuration management
""",
            },
            {
                "number": 2,
                "name": "implementation",
                "hours": 4.0,
                "description": "Implement command methods",
                "content": """## Phase 2: Implementation

Lifecycle commands combine multiple operations:
- implement(action="claim") → claim_priority()
- implement(action="complete") → complete_implementation()

Database operations:
- roadmap_priority (work tracking)
- implementation_tasks (task status)
- commits (commit history)
- code_reviews (review tracking)
""",
            },
            {
                "number": 3,
                "name": "testing-and-migration",
                "hours": 4.0,
                "description": "Aliases and tests",
                "content": """## Phase 3: Testing & Migration

### Backward Compatibility
Create aliases for 14 legacy commands.

### Tests
- Lifecycle tests (claim → implement → complete)
- Git workflow tests
- Quality check tests
""",
            },
        ],
    },
    105: {
        "title": "Code Reviewer Commands (Consolidated Architecture)",
        "commands_before": 13,
        "commands_after": 4,
        "commands": ["review", "analyze", "monitor", "notify"],
        "estimated_hours": 12.0,
        "roadmap_item_id": "CONSOLIDATION-REVIEWER",
        "phases": [
            {
                "number": 1,
                "name": "command-definitions",
                "hours": 6.0,
                "description": "Define 4 consolidated commands",
                "content": """## Phase 1: Command Definitions

### 1. review Command
**Actions**: generate_report, score, validate_dod
**Purpose**: Complete review with report and quality scoring

### 2. analyze Command
**Actions**: style, security, complexity, coverage, types, architecture, docs
**Purpose**: All types of code analysis (parameterized by type)

### 3. monitor Command
**Actions**: detect_commits, track_issues
**Purpose**: Track commits and issue resolution

### 4. notify Command
**Actions**: architect, code_developer
**Purpose**: Send notifications to relevant agents
""",
            },
            {
                "number": 2,
                "name": "implementation",
                "hours": 3.0,
                "description": "Implement command methods",
                "content": """## Phase 2: Implementation

Analysis command with type parameter:
- analyze(type="style") → check_style_compliance()
- analyze(type="security") → run_security_scan()
- analyze(type="complexity") → analyze_complexity()

Database operations:
- code_reviews (review records)
- analysis_results (analysis findings)
- notifications (alert delivery)
""",
            },
            {
                "number": 3,
                "name": "testing-and-migration",
                "hours": 3.0,
                "description": "Aliases and tests",
                "content": """## Phase 3: Testing & Migration

### Backward Compatibility
Create aliases for 13 legacy commands.

### Tests
- Review workflow tests
- All analysis types
- Notification delivery
""",
            },
        ],
    },
    106: {
        "title": "Orchestrator Commands (Consolidated Architecture)",
        "commands_before": 15,
        "commands_after": 5,
        "commands": ["agents", "orchestrate", "worktree", "messages", "monitor"],
        "estimated_hours": 16.0,
        "roadmap_item_id": "CONSOLIDATION-ORCH",
        "phases": [
            {
                "number": 1,
                "name": "command-definitions",
                "hours": 8.0,
                "description": "Define 5 consolidated commands",
                "content": """## Phase 1: Command Definitions

### 1. agents Command
**Actions**: spawn, kill, restart, monitor_lifecycle, handle_errors
**Purpose**: Agent lifecycle management

### 2. orchestrate Command
**Actions**: coordinate_deps, find_work, create_tasks, detect_deadlocks
**Purpose**: Work coordination and scheduling

### 3. worktree Command
**Actions**: create, cleanup, merge
**Purpose**: Git worktree operations for parallel execution

### 4. messages Command
**Actions**: route, send, receive
**Purpose**: Inter-agent communication

### 5. monitor Command
**Actions**: resources, activity_summary
**Purpose**: Resource usage and activity monitoring
""",
            },
            {
                "number": 2,
                "name": "implementation",
                "hours": 4.0,
                "description": "Implement command methods",
                "content": """## Phase 2: Implementation

Agent lifecycle:
- agents(action="spawn") → spawn_agent_session()
- agents(action="kill") → kill_stalled_agent()

Database operations:
- orchestrator_agents (agent registry)
- orchestrator_tasks (task queue)
- orchestrator_messages (message routing)
- worktree_tracking (worktree lifecycle)
""",
            },
            {
                "number": 3,
                "name": "testing-and-migration",
                "hours": 4.0,
                "description": "Aliases and tests",
                "content": """## Phase 3: Testing & Migration

### Backward Compatibility
Create aliases for 15 legacy commands.

### Tests
- Agent lifecycle tests
- Worktree management tests
- Message routing tests
- Resource monitoring tests
""",
            },
        ],
    },
    114: {
        "title": "UI & Utility Agent Commands (Consolidated Architecture)",
        "commands_before": 30,
        "commands_after": 11,
        "commands": {
            "assistant": ["demo", "bug", "delegate", "docs"],
            "user_listener": ["understand", "route", "conversation"],
            "ux_design_expert": ["design", "components", "review", "debt"],
        },
        "estimated_hours": 20.0,
        "roadmap_item_id": "CONSOLIDATION-UI",
        "phases": [
            {
                "number": 1,
                "name": "assistant-commands",
                "hours": 6.0,
                "description": "4 commands for assistant agent",
                "content": """## Phase 1: Assistant Commands

### 1. demo Command
**Actions**: create, record, validate
**Purpose**: Demo creation and management

### 2. bug Command
**Actions**: report, track_status, link_to_priority
**Purpose**: Bug reporting and tracking

### 3. delegate Command
**Actions**: classify, route, monitor
**Purpose**: Intelligent request routing

### 4. docs Command
**Actions**: generate, update_readme
**Purpose**: Documentation generation
""",
            },
            {
                "number": 2,
                "name": "user-listener-commands",
                "hours": 4.0,
                "description": "3 commands for user_listener agent",
                "content": """## Phase 2: User Listener Commands

### 1. understand Command
**Actions**: classify_intent, extract_entities, determine_agent
**Purpose**: NLU for user requests

### 2. route Command
**Actions**: route_request, queue, handle_fallback
**Purpose**: Route to appropriate agent

### 3. conversation Command
**Actions**: track, update_context, manage_session
**Purpose**: Conversation state management
""",
            },
            {
                "number": 3,
                "name": "ux-design-commands",
                "hours": 6.0,
                "description": "4 commands for ux_design_expert agent",
                "content": """## Phase 3: UX Design Expert Commands

### 1. design Command
**Actions**: generate_ui_spec, create_component_spec
**Purpose**: UI/component specifications

### 2. components Command
**Actions**: manage_library, tailwind_config, design_tokens, chart_theme
**Purpose**: Component library and design system

### 3. review Command
**Actions**: review_implementation, suggest_improvements, validate_accessibility
**Purpose**: UI review and accessibility

### 4. debt Command
**Actions**: track, prioritize, remediate
**Purpose**: Design debt management
""",
            },
            {
                "number": 4,
                "name": "testing-and-migration",
                "hours": 4.0,
                "description": "Unified testing and migration",
                "content": """## Phase 4: Testing & Migration

### Backward Compatibility
Create aliases for all 30 legacy commands across 3 agents.

### Tests
- Assistant: demo creation, bug tracking, delegation
- User Listener: intent classification, routing, conversation
- UX Design Expert: design specs, component management, reviews

### Migration
Week 1-2: Implement with aliases
Week 3-4: Update internal code
Week 5-6: Deprecation warnings
Week 7+: Remove aliases
""",
            },
        ],
    },
}


def update_spec(spec_number: int, spec_data: dict) -> None:
    """Update a single spec in the database."""
    content = {
        "overview": f"""# SPEC-{spec_number}: {spec_data['title']}

## Executive Summary

Consolidate {spec_data['commands_before']} commands into {spec_data['commands_after']} unified commands.

**Reduction**: {100 * (spec_data['commands_before'] - spec_data['commands_after']) // spec_data['commands_before']}%

## New Commands

{chr(10).join(f"{i+1}. **{cmd}**" for i, cmd in enumerate(spec_data['commands'] if isinstance(spec_data['commands'], list) else [c for cmds in spec_data['commands'].values() for c in cmds]))}
""",
        "architecture": """# Architecture Design

## Parameter-Driven Pattern

Each command uses action-based routing:

```python
def command_name(self, action="default", **params):
    actions = {
        "action1": self._handle_action1,
        "action2": self._handle_action2,
    }
    return actions[action](**params)
```

## Benefits

- Reduced cognitive load
- Consistent pattern across agents
- Self-documenting API
- Easier maintenance
- Better discoverability
""",
        "phases": spec_data["phases"],
        "total_hours": spec_data["estimated_hours"],
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    content_json = json.dumps(content, indent=2)
    now = datetime.now().isoformat()
    phase_names = [p["name"] for p in spec_data["phases"]]

    cursor.execute(
        """
        UPDATE specs_specification
        SET
            title = ?,
            roadmap_item_id = ?,
            content = ?,
            spec_type = 'hierarchical',
            estimated_hours = ?,
            total_phases = ?,
            phase_files = ?,
            updated_at = ?,
            updated_by = 'architect'
        WHERE spec_number = ?
    """,
        (
            spec_data["title"],
            spec_data["roadmap_item_id"],
            content_json,
            spec_data["estimated_hours"],
            len(spec_data["phases"]),
            json.dumps(phase_names),
            now,
            spec_number,
        ),
    )

    conn.commit()
    conn.close()

    print(f"✅ Updated SPEC-{spec_number}: {spec_data['title']}")
    print(f"   Commands: {spec_data['commands_before']} → {spec_data['commands_after']}")
    print(f"   Estimated Hours: {spec_data['estimated_hours']}")
    print(f"   Phases: {len(spec_data['phases'])}")
    if isinstance(spec_data["commands"], list):
        print(f"   New commands: {', '.join(spec_data['commands'])}")
    print()


def main():
    """Update all command specs."""
    print("=" * 60)
    print("Updating Command Specifications")
    print("=" * 60)
    print()

    # Update each spec
    for spec_number, spec_data in SPECS.items():
        update_spec(spec_number, spec_data)

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    total_before = sum(s["commands_before"] for s in SPECS.values())
    total_after = sum(s["commands_after"] for s in SPECS.values())
    reduction = 100 * (total_before - total_after) // total_before

    print(f"Total commands BEFORE: {total_before}")
    print(f"Total commands AFTER: {total_after}")
    print(f"Reduction: {reduction}%")
    print()
    print("✅ All specs updated successfully!")


if __name__ == "__main__":
    main()
