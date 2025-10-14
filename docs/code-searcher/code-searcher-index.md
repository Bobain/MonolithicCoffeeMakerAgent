# Code-Searcher Module Index

**Last Updated**: 2025-10-14
**Purpose**: Quick reference for module locations, functionalities, and key components
**Owner**: code-searcher agent

---

## Table of Contents

1. [Autonomous System](#autonomous-system)
2. [CLI Layer](#cli-layer)
3. [Observability](#observability)
4. [Tests](#tests)
5. [Configuration](#configuration)

---

## Autonomous System

### Module: `coffee_maker/autonomous/daemon.py`
**Purpose**: Main orchestrator for autonomous development
**Key Classes**:
- `AutonomousDeveloperDaemon`: Main daemon class using mixin pattern
- Mixins: `SpecManagerMixin`, `ImplementationMixin`, `StatusMixin`, `NotificationMixin`

**Key Functions**:
- `run()`: Main event loop
- `_check_for_work()`: Scans ROADMAP for work
- `_handle_status_update()`: Updates developer status

**Dependencies**:
- `daemon_spec_manager.py`
- `daemon_implementation.py`
- `developer_status.py`
- `prompt_loader.py`

---

### Module: `coffee_maker/autonomous/daemon_spec_manager.py`
**Purpose**: Technical specification creation
**Key Classes**:
- `SpecManagerMixin`: Handles spec generation workflow

**Key Functions**:
- `create_technical_spec()`: Creates specs from ROADMAP priorities
- `_read_priority_content()`: Extracts priority details

**Prompts Used**:
- `PromptNames.CREATE_TECHNICAL_SPEC` → `.claude/commands/create-technical-spec.md`

---

### Module: `coffee_maker/autonomous/daemon_implementation.py`
**Purpose**: Feature implementation workflow
**Key Classes**:
- `ImplementationMixin`: Handles feature and documentation implementation

**Key Functions**:
- `implement_priority()`: Routes to feature or doc implementation
- `_implement_feature()`: Code implementation
- `_implement_documentation()`: Documentation implementation

**Prompts Used**:
- `PromptNames.IMPLEMENT_FEATURE` → `.claude/commands/implement-feature.md`
- `PromptNames.IMPLEMENT_DOCUMENTATION` → `.claude/commands/implement-documentation.md`

---

### Module: `coffee_maker/autonomous/prompt_loader.py`
**Purpose**: Centralized prompt management system
**Key Classes**:
- `PromptNames`: Enum-like class for prompt identifiers

**Key Functions**:
- `load_prompt(prompt_name, variables)`: Loads and interpolates prompts

**Location**: `.claude/commands/`
**Supported Prompts**:
- `create-technical-spec.md`
- `implement-feature.md`
- `implement-documentation.md`
- `test-web-app.md`
- `capture-visual-docs.md`

---

### Module: `coffee_maker/autonomous/developer_status.py`
**Purpose**: Status tracking and reporting
**Key Classes**:
- `DeveloperStatus`: Tracks daemon execution state

**Key Functions**:
- `set_working()`: Sets status to working
- `set_idle()`: Sets status to idle
- `get_status()`: Retrieves current status

**Storage**: `data/developer_status.json`

---

### Module: `coffee_maker/autonomous/claude_cli_interface.py`
**Purpose**: Interface to Claude CLI
**Key Classes**:
- `ClaudeCLIInterface`: Wrapper for Claude CLI commands

**Key Functions**:
- `chat()`: Sends messages to Claude CLI
- `_execute_command()`: Executes shell commands

---

## CLI Layer

### Module: `coffee_maker/cli/roadmap_cli.py`
**Purpose**: ROADMAP management commands
**Key Functions**:
- `roadmap()`: Displays ROADMAP
- `status()`: Shows developer status
- `work_status()`: Detailed work status

**CLI Commands**:
- `poetry run project-manager /roadmap`
- `poetry run project-manager /status`

---

### Module: `coffee_maker/cli/notifications.py`
**Purpose**: Notification system (sound, desktop, logs)
**Key Functions**:
- `notify()`: Sends notifications
- `play_sound()`: Plays notification sounds
- `desktop_notification()`: OS-level notifications

**Notification Types**:
- `INFO`, `SUCCESS`, `ERROR`, `WARNING`

---

## Observability

### Module: `coffee_maker/langfuse_observe/`
**Purpose**: Langfuse integration for tracking
**Key Components**:
- Decorators for tracing
- Cost tracking
- Latency monitoring

**Future**: Prompt source of truth (Phase 2)

---

## Tests

### Directory: `tests/unit/`
**Coverage**: Unit tests for core modules
**Key Files**:
- `test_daemon.py`: Daemon tests
- `test_prompt_loader.py`: Prompt loading tests
- `test_developer_status.py`: Status tracking tests

---

### Directory: `tests/ci_tests/`
**Coverage**: Integration tests
**Key Files**:
- `test_roadmap_integration.py`: ROADMAP workflow tests

---

## Configuration

### File: `.claude/CLAUDE.md`
**Purpose**: Project instructions and architecture documentation
**Owner**: project_manager, memory-bank-synchronizer

---

### File: `docs/roadmap/ROADMAP.md`
**Purpose**: Master task list and priorities
**Owner**: project_manager (strategy), code_developer (status updates)

---

### File: `.claude/commands/`
**Purpose**: Centralized prompt templates
**Owner**: project_manager
**Format**: Markdown with `$VARIABLE_NAME` placeholders

---

### File: `.claude/agents/`
**Purpose**: Agent configurations and instructions
**Owner**: project_manager
**Key Files**:
- `assistant.md`
- `code_developer.md`
- `project_manager.md`
- `code-searcher.md`

---

## Quick Reference

### Finding Authentication Logic
```
Location: coffee_maker/autonomous/claude_cli_interface.py
Pattern: API key management, CLI authentication
```

### Finding ROADMAP Parsing
```
Location: coffee_maker/autonomous/daemon.py
Function: _check_for_work()
Pattern: Regex matching for priority status
```

### Finding Prompt System
```
Location: coffee_maker/autonomous/prompt_loader.py
Templates: .claude/commands/*.md
Usage: load_prompt(PromptNames.X, {...})
```

### Finding Notification System
```
Location: coffee_maker/cli/notifications.py
Functions: notify(), play_sound(), desktop_notification()
Types: INFO, SUCCESS, ERROR, WARNING
```

---

## Module Dependency Graph

```
daemon.py
    ├── daemon_spec_manager.py
    ├── daemon_implementation.py
    ├── developer_status.py
    ├── prompt_loader.py
    └── claude_cli_interface.py

roadmap_cli.py
    ├── developer_status.py
    └── notifications.py

prompt_loader.py
    └── .claude/commands/*.md
```

---

## Notes

- **Mixin Pattern**: Daemon uses composition for modularity
- **Prompt Centralization**: All prompts in `.claude/commands/`
- **Multi-AI Support**: Provider-agnostic design
- **Observability**: Langfuse tracking throughout
- **Pre-commit Hooks**: Black, autoflake, trailing-whitespace

---

**Update Protocol**: Update this index when:
- New modules are added
- Module responsibilities change
- New key functions are introduced
- Architecture patterns evolve
