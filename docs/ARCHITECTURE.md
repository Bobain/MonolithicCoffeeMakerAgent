# MonolithicCoffeeMakerAgent - System Architecture

**Version**: 1.0
**Date**: 2025-10-12
**Status**: Active Development

---

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Agent System](#agent-system)
5. [Data Flow](#data-flow)
6. [Configuration System](#configuration-system)
7. [Error Handling Architecture](#error-handling-architecture)
8. [Directory Structure](#directory-structure)

---

## System Overview

MonolithicCoffeeMakerAgent is an autonomous software development system that uses AI agents to implement features, manage projects, and provide assistance. The system follows a multi-agent architecture with specialized agents for different tasks.

### Core Philosophy
- **Autonomous**: Agents work independently with minimal human intervention
- **Observable**: Full integration with Langfuse for tracking and analytics
- **Multi-Provider**: Supports Claude, Gemini, and OpenAI
- **Modular**: Clean separation of concerns with mixins and utilities

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MonolithicCoffeeMakerAgent                          │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          User Interface Layer                         │   │
│  │                                                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │     CLI      │  │   Streamlit  │  │  Chat        │              │   │
│  │  │  (Typer)     │  │  Dashboards  │  │  Interface   │              │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  └─────────┼──────────────────┼──────────────────┼────────────────────┘   │
│            │                  │                  │                          │
│  ┌─────────┴──────────────────┴──────────────────┴────────────────────┐   │
│  │                      Application Services Layer                      │   │
│  │                                                                       │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │   │
│  │  │  AI Service    │  │  Roadmap       │  │  Notification  │        │   │
│  │  │  (Multi-LLM)   │  │  Editor        │  │  Manager       │        │   │
│  │  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘        │   │
│  └───────────┼────────────────────┼────────────────────┼───────────────┘   │
│              │                    │                    │                    │
│  ┌───────────┴────────────────────┴────────────────────┴───────────────┐   │
│  │                       Agent Orchestration Layer                      │   │
│  │                                                                       │   │
│  │  ┌────────────┐  ┌───────────┐  ┌──────────┐  ┌─────────────┐     │   │
│  │  │ code_      │  │ project_  │  │assistant │  │code-searcher│     │   │
│  │  │ developer  │  │ manager   │  │          │  │             │     │   │
│  │  │ (Daemon)   │  │ (CLI)     │  │ (Triage) │  │ (Analysis)  │     │   │
│  │  └─────┬──────┘  └─────┬─────┘  └────┬─────┘  └──────┬──────┘     │   │
│  │        │               │              │               │             │   │
│  │        │  ┌───────────┐│  ┌──────────┐│  ┌───────────┐│            │   │
│  │        │  │ux-design- ││  │ memory-  ││  │specialized││            │   │
│  │        │  │expert     ││  │bank-sync ││  │ agents... ││            │   │
│  │        │  └───────────┘│  └──────────┘│  └───────────┘│            │   │
│  └────────┼────────────────┼──────────────┼───────────────┼───────────┘   │
│           │                │              │               │                │
│  ┌────────┴────────────────┴──────────────┴───────────────┴───────────┐   │
│  │                       Core Infrastructure Layer                      │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │ Config      │  │ Exception  │  │ Logging    │  │ File I/O   │  │   │
│  │  │ Manager     │  │ Hierarchy  │  │ Utilities  │  │ Utilities  │  │   │
│  │  └─────────────┘  └────────────┘  └────────────┘  └────────────┘  │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌────────────┐  ┌────────────┐                   │   │
│  │  │ Langfuse    │  │ AI         │  │ Code       │                   │   │
│  │  │ Observ.     │  │ Providers  │  │ Review     │                   │   │
│  │  └─────────────┘  └────────────┘  └────────────┘                   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                       External Services Layer                          │ │
│  │                                                                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │ │
│  │  │ Anthropic│  │ OpenAI   │  │ Google   │  │ Langfuse │             │ │
│  │  │ Claude   │  │ GPT      │  │ Gemini   │  │ Analytics│             │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │ │
│  │                                                                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                            │ │
│  │  │ GitHub   │  │ Git      │  │ File     │                            │ │
│  │  │ API      │  │ CLI      │  │ System   │                            │ │
│  │  └──────────┘  └──────────┘  └──────────┘                            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Autonomous Daemon (code_developer)

The `code_developer` daemon is the heart of the autonomous development system.

```
┌───────────────────────────────────────────────────────────────┐
│                    Autonomous Daemon                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Core Daemon (daemon.py)                     │  │
│  │                     611 lines                             │  │
│  │                                                           │  │
│  │  • Orchestrates all daemon operations                    │  │
│  │  • Manages daemon lifecycle                              │  │
│  │  • Coordinates mixins                                    │  │
│  └──────┬─────────────────────────────────────────────┬────┘  │
│         │                                              │        │
│  ┌──────▼──────────┐                         ┌────────▼────┐  │
│  │  GitOpsMixin    │                         │ StatusMixin │  │
│  │  (231 lines)    │                         │ (313 lines) │  │
│  │                 │                         │             │  │
│  │ • commit_changes│                         │ • update    │  │
│  │ • push_changes  │                         │ • report    │  │
│  │ • create_pr     │                         │ • notify    │  │
│  └─────────────────┘                         └─────────────┘  │
│                                                                 │
│  ┌──────────────────┐                    ┌───────────────────┐│
│  │ SpecManagerMixin │                    │ImplementationMixin││
│  │ (181 lines)      │                    │ (481 lines)       ││
│  │                  │                    │                   ││
│  │ • create_spec    │                    │ • implement       ││
│  │ • validate_spec  │                    │ • execute_task    ││
│  │ • update_status  │                    │ • verify_dod      ││
│  └──────────────────┘                    └───────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Supporting Modules                          │  │
│  │                                                           │  │
│  │  • developer_status.py - Status tracking                │  │
│  │  • claude_cli_interface.py - CLI integration            │  │
│  │  • prompt_loader.py - Centralized prompts               │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 2. CLI Layer (project_manager)

```
┌───────────────────────────────────────────────────────────────┐
│                      CLI Layer (Typer)                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           roadmap_cli.py (Main Entry)                    │  │
│  │                                                           │  │
│  │  Commands:                                               │  │
│  │  • /roadmap - View/edit ROADMAP.md                      │  │
│  │  • /status - Daemon status                              │  │
│  │  • notifications - View notifications                    │  │
│  │  • developer-status - Current progress                   │  │
│  └──────────────┬────────────────┬─────────────────────────┘  │
│                 │                │                              │
│  ┌──────────────▼──────┐  ┌──────▼─────────────┐             │
│  │  roadmap_editor.py  │  │  ai_service.py     │             │
│  │  (945 lines)        │  │  (739 lines)       │             │
│  │                     │  │                    │             │
│  │  • Edit roadmap     │  │  • Multi-provider  │             │
│  │  • Parse priorities │  │  • AI requests     │             │
│  │  • Validate format  │  │  • Rate limiting   │             │
│  └─────────────────────┘  └────────────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              commands/ (Sub-commands)                    │  │
│  │                                                           │  │
│  │  • user_story.py - User story management                │  │
│  │  • Other specialized commands                           │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 3. AI Providers Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     AI Providers System                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            ai_providers/__init__.py                      │  │
│  │              (Provider Registry)                          │  │
│  │                                                           │  │
│  │  • get_provider(provider_type) → Provider                │  │
│  │  • Unified interface for all AI providers               │  │
│  └──────────────┬────────────────┬──────────────┬──────────┘  │
│                 │                │              │              │
│  ┌──────────────▼──┐  ┌─────────▼──┐  ┌───────▼────────┐    │
│  │ ClaudeProvider │  │OpenAI      │  │  Gemini        │    │
│  │                │  │Provider    │  │  Provider      │    │
│  │ • Anthropic    │  │            │  │                │    │
│  │   API          │  │ • GPT-4    │  │  • Gemini Pro  │    │
│  │ • Claude CLI   │  │ • GPT-3.5  │  │                │    │
│  └────────────────┘  └────────────┘  └────────────────┘    │
│                                                                 │
│  Common Interface:                                             │
│  • send_message(prompt, context) → Response                   │
│  • stream_response(prompt) → Iterator[str]                    │
│  • get_usage() → TokenUsage                                   │
│  • estimate_cost() → float                                    │
└───────────────────────────────────────────────────────────────┘
```

### 4. Configuration System

```
┌───────────────────────────────────────────────────────────────┐
│                   Configuration Architecture                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         ConfigManager (Singleton)                        │  │
│  │         coffee_maker/config/manager.py                   │  │
│  │                                                           │  │
│  │  API Key Management:                                     │  │
│  │  • get_anthropic_api_key(required=False) → str          │  │
│  │  • get_openai_api_key(required=False) → str             │  │
│  │  • get_gemini_api_key(required=False) → str             │  │
│  │  • get_langfuse_public_key(required=False) → str        │  │
│  │  • get_langfuse_secret_key(required=False) → str        │  │
│  │                                                           │  │
│  │  Validation:                                             │  │
│  │  • has_*_api_key() → bool                               │  │
│  │  • get_all_api_keys() → Dict[str, Optional[str]]        │  │
│  │                                                           │  │
│  │  Features:                                               │  │
│  │  • Configuration caching                                 │  │
│  │  • Fallback support                                      │  │
│  │  • Custom exceptions (APIKeyMissingError)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Environment Variables:                                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ANTHROPIC_API_KEY      - Claude API access             │  │
│  │  OPENAI_API_KEY         - OpenAI GPT access             │  │
│  │  GOOGLE_API_KEY         - Gemini access                 │  │
│  │  LANGFUSE_PUBLIC_KEY    - Langfuse analytics            │  │
│  │  LANGFUSE_SECRET_KEY    - Langfuse analytics            │  │
│  │  GITHUB_TOKEN           - GitHub API access             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Database Paths:                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  NOTIFICATIONS_DB       - SQLite notifications DB       │  │
│  │  ANALYTICS_DB           - SQLite analytics DB           │  │
│  │  CODE_REVIEW_DB         - SQLite code review DB         │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## Agent System

### Agent Hierarchy and Ownership

**CRITICAL**: Each agent has EXCLUSIVE ownership of specific files/directories to prevent conflicts.

```
┌───────────────────────────────────────────────────────────────┐
│                      Agent Ecosystem                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │               assistant (Triage Agent)                   │  │
│  │                                                           │  │
│  │  Responsibilities:                                       │  │
│  │  • First-line user support                              │  │
│  │  • Quick questions and simple debugging                 │  │
│  │  • Delegates complex tasks to specialists              │  │
│  │  • READ-ONLY access to ALL files                       │  │
│  │  • NEVER modifies code or docs                         │  │
│  │                                                           │  │
│  │  Delegates to:                                           │  │
│  │    ↓                ↓               ↓                    │  │
│  └────┼────────────────┼───────────────┼────────────────────┘  │
│       │                │               │                        │
│  ┌────▼────────┐  ┌────▼────────┐  ┌──▼──────────────┐       │
│  │code_developer│  │project_     │  │code-searcher    │       │
│  │             │  │manager      │  │                 │       │
│  │EXECUTION    │  │OVERSIGHT    │  │ANALYSIS         │       │
│  │             │  │             │  │                 │       │
│  │OWNS:        │  │OWNS:        │  │OWNS:            │       │
│  │• coffee_    │  │• docs/      │  │• READ-ONLY      │       │
│  │  maker/     │  │• .claude/   │  │                 │       │
│  │• tests/     │  │  agents/    │  │DOES:            │       │
│  │• scripts/   │  │• .claude/   │  │• Deep code      │       │
│  │• pyproject. │  │  commands/  │  │  analysis       │       │
│  │  toml       │  │             │  │• Pattern        │       │
│  │             │  │DOES:        │  │  detection      │       │
│  │DOES:        │  │• GitHub     │  │• Security       │       │
│  │• All code   │  │  monitoring │  │  analysis       │       │
│  │  changes    │  │• Verify DoD │  │• Forensics      │       │
│  │• Create PRs │  │  (post-impl)│  │                 │       │
│  │• Verify DoD │  │• Strategic  │  │                 │       │
│  │  during     │  │  ROADMAP    │  │                 │       │
│  │  implement. │  │• Tech specs │  │                 │       │
│  │• Puppeteer  │  │• Agent      │  │                 │       │
│  │  during     │  │  configs    │  │                 │       │
│  │  implement. │  │• Warn on    │  │                 │       │
│  │             │  │  blockers   │  │                 │       │
│  └─────────────┘  └─────────────┘  └─────────────────┘       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ux-design-    │  │memory-bank-  │  │ specialized        │  │
│  │expert        │  │synchronizer  │  │ agents...          │  │
│  │              │  │              │  │                    │  │
│  │DESIGN        │  │DOCUMENTATION │  │                    │  │
│  │              │  │              │  │                    │  │
│  │OWNS:         │  │OWNS:         │  │OWNS:               │  │
│  │• (provides   │  │• .claude/    │  │• Domain-specific   │  │
│  │   specs only)│  │  CLAUDE.md   │  │  files             │  │
│  │              │  │  (shared)    │  │                    │  │
│  │DOES:         │  │              │  │DOES:               │  │
│  │• All UI/UX   │  │DOES:         │  │• Domain-specific   │  │
│  │  decisions   │  │• Keep        │  │  tasks             │  │
│  │• Tailwind CSS│  │  CLAUDE.md   │  │                    │  │
│  │• Highcharts  │  │  files       │  │                    │  │
│  │• Design      │  │  current     │  │                    │  │
│  │  systems     │  │• Sync docs   │  │                    │  │
│  │              │  │  with code   │  │                    │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### File Ownership Matrix

**CRITICAL**: These rules prevent conflicts and ensure clear responsibility.

```
┌────────────────────────────────────────────────────────────────────┐
│                     File/Directory Ownership                        │
├──────────────────────┬──────────────┬──────────────────────────────┤
│ File/Directory       │ Owner        │ Can Modify?                  │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ coffee_maker/        │ code_        │ YES - All implementation     │
│                      │ developer    │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ tests/               │ code_        │ YES - All test code          │
│                      │ developer    │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ scripts/             │ code_        │ YES - Utility scripts        │
│                      │ developer    │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ pyproject.toml       │ code_        │ YES - Dependency mgmt        │
│                      │ developer    │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ docs/                │ project_     │ YES - Full control           │
│                      │ manager      │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ docs/ROADMAP.md      │ project_     │ project_manager: Full        │
│                      │ manager,     │ code_developer: Status only  │
│                      │ code_        │ (others READ-ONLY)           │
│                      │ developer    │                              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ docs/PRIORITY_*.md   │ project_     │ YES - Creates/updates specs  │
│                      │ manager      │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ .claude/agents/      │ project_     │ YES - Agent configs          │
│                      │ manager      │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ .claude/commands/    │ project_     │ YES - Prompt management      │
│                      │ manager      │ (others READ-ONLY)           │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ .claude/CLAUDE.md    │ project_     │ YES - Strategic updates      │
│                      │ manager,     │ (code_developer READ-ONLY)   │
│                      │ memory-bank- │                              │
│                      │ synchronizer │                              │
└──────────────────────┴──────────────┴──────────────────────────────┘
```

### Tool Ownership Matrix

```
┌────────────────────────────────────────────────────────────────────┐
│                       Tool/Capability Ownership                     │
├──────────────────────┬──────────────┬──────────────────────────────┤
│ Tool/Capability      │ Owner        │ Usage                        │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Puppeteer DoD        │ code_        │ Verify during implementation │
│ (during impl)        │ developer    │                              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Puppeteer DoD        │ project_     │ Verify completed work        │
│ (post-impl)          │ manager      │ on user request              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Puppeteer demos      │ assistant    │ Show features visually       │
│                      │              │ (demos only, NOT verify)     │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ GitHub PR create     │ code_        │ Create PRs autonomously      │
│                      │ developer    │                              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ GitHub monitoring    │ project_     │ Monitor PRs, issues, CI/CD   │
│                      │ manager      │                              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ GitHub queries       │ project_     │ All gh commands              │
│ (gh commands)        │ manager      │ (assistant delegates)        │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Code editing         │ code_        │ ALL code changes             │
│                      │ developer    │ (assistant READ-ONLY)        │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Code search (simple) │ assistant    │ 1-2 files with Grep/Read     │
│                      │              │ Delegate complex to          │
│                      │              │ code-searcher                │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Code search (complex)│ code-        │ Deep analysis, patterns,     │
│                      │ searcher     │ forensics                    │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ ROADMAP updates      │ project_     │ Strategic vs. execution      │
│                      │ manager      │ updates                      │
│                      │ (full),      │ (assistant READ-ONLY)        │
│                      │ code_        │                              │
│                      │ developer    │                              │
│                      │ (status only)│                              │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Design decisions     │ ux-design-   │ All UI/UX, Tailwind, charts  │
│                      │ expert       │ (others delegate)            │
├──────────────────────┼──────────────┼──────────────────────────────┤
│ Doc sync             │ memory-bank- │ Keep CLAUDE.md files current │
│                      │ synchronizer │                              │
└──────────────────────┴──────────────┴──────────────────────────────┘
```

### Agent Boundary Enforcement

**Key Rules to Prevent Conflicts**:

1. **code_developer NEVER modifies docs/** - Delegates to project_manager
2. **project_manager NEVER modifies coffee_maker/** - Delegates to code_developer
3. **assistant NEVER modifies ANY files** - Always delegates to appropriate agent
4. **code_developer creates PRs** - project_manager does NOT create PRs
5. **project_manager monitors GitHub** - code_developer focuses on implementation

**Delegation Flow**:
```
User → assistant (triage) → specialized agent (execute)
```

**Anti-Patterns (DO NOT DO)**:
- assistant editing code directly
- project_manager implementing features
- code_developer creating technical specs in docs/
- Multiple agents modifying the same file
- Agents competing for the same task

---

## Data Flow

### 1. Autonomous Development Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Autonomous Development Workflow                 │
└─────────────────────────────────────────────────────────────────┘

  1. ROADMAP Update
  ┌──────────────────────────────────────────────┐
  │ User updates ROADMAP.md with new priority    │
  │ • Adds priority description                  │
  │ • Sets DoD criteria                          │
  │ • Commits to git                             │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  2. Daemon Detection
  ┌──────────────────────────────────────────────┐
  │ code_developer daemon detects new priority   │
  │ • Polls ROADMAP.md (or git webhook)         │
  │ • Parses priority content                    │
  │ • Validates format                           │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  3. Spec Creation (If Needed)
  ┌──────────────────────────────────────────────┐
  │ SpecManagerMixin creates technical spec      │
  │ • Loads prompt from .claude/commands/        │
  │ • Sends to AI provider                       │
  │ • Saves to docs/PRIORITY_X_TECHNICAL_SPEC.md│
  │ • Updates developer_status.json              │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  4. Implementation
  ┌──────────────────────────────────────────────┐
  │ ImplementationMixin executes task            │
  │ • Loads implementation prompt                │
  │ • AI generates code changes                  │
  │ • Writes files                               │
  │ • Runs tests (if applicable)                 │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  5. Verification (DoD)
  ┌──────────────────────────────────────────────┐
  │ Verify Definition of Done                    │
  │ • Run tests                                  │
  │ • Use Puppeteer for UI tests                │
  │ • Check acceptance criteria                 │
  │ • Validate functionality                     │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  6. Git Operations
  ┌──────────────────────────────────────────────┐
  │ GitOpsMixin handles version control          │
  │ • git add changed files                      │
  │ • git commit with message                    │
  │ • git push to feature branch                 │
  │ • gh pr create (if configured)               │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  7. Status Update & Notification
  ┌──────────────────────────────────────────────┐
  │ StatusMixin reports progress                 │
  │ • Update developer_status.json               │
  │ • Create notification in DB                  │
  │ • Update ROADMAP status                      │
  │ • Log to Langfuse                            │
  └──────────────────────────────────────────────┘
```

### 2. User Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interaction Flow                        │
└─────────────────────────────────────────────────────────────────┘

  User Command
  ┌──────────────────────────────────────────────┐
  │ $ poetry run project-manager /roadmap        │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  CLI Processing (Typer)
  ┌──────────────────────────────────────────────┐
  │ roadmap_cli.py handles command               │
  │ • Parse arguments                            │
  │ • Route to appropriate handler               │
  └───────────────────┬──────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
  Read ROADMAP              Edit ROADMAP
  ┌────────────────┐       ┌────────────────┐
  │ Display current│       │ AI-assisted    │
  │ priorities     │       │ editing        │
  │ • Format       │       │ • Validate     │
  │ • Highlight    │       │ • Save         │
  └────────────────┘       └────────┬───────┘
                                    │
                                    ▼
                           Update Git
                           ┌────────────────┐
                           │ Commit changes │
                           │ Notify daemon  │
                           └────────────────┘
```

### 3. AI Provider Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       AI Provider Flow                           │
└─────────────────────────────────────────────────────────────────┘

  Request Initiation
  ┌──────────────────────────────────────────────┐
  │ Component needs AI assistance                │
  │ • Load prompt from .claude/commands/         │
  │ • Add context variables                      │
  │ • Format request                             │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  Provider Selection
  ┌──────────────────────────────────────────────┐
  │ ConfigManager selects provider               │
  │ • Check available API keys                   │
  │ • Select based on config                     │
  │ • Create provider instance                   │
  └───────────────────┬──────────────────────────┘
                      │
         ┌────────────┴────────────┬──────────────┐
         │                         │              │
         ▼                         ▼              ▼
  Claude Provider          OpenAI Provider  Gemini Provider
  ┌────────────────┐      ┌──────────────┐ ┌──────────────┐
  │ Anthropic API  │      │ GPT-4 API    │ │ Gemini API   │
  │ • Rate limit   │      │ • Rate limit │ │ • Rate limit │
  │ • Retry logic  │      │ • Retry logic│ │ • Retry logic│
  └────────┬───────┘      └──────┬───────┘ └──────┬───────┘
           │                     │                 │
           └─────────────────────┴─────────────────┘
                                 │
                                 ▼
                        Response Processing
                        ┌────────────────┐
                        │ Parse response │
                        │ Log to Langfuse│
                        │ Return result  │
                        └────────────────┘
```

---

## Configuration System

### Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration System Flow                     │
└─────────────────────────────────────────────────────────────────┘

  Component Initialization
  ┌──────────────────────────────────────────────┐
  │ Component needs configuration                │
  │ (e.g., AI provider needs API key)            │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  ConfigManager Request
  ┌──────────────────────────────────────────────┐
  │ from coffee_maker.config import ConfigManager│
  │ api_key = ConfigManager.get_anthropic_api_key│
  │                         (required=True)       │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  Check Cache
  ┌──────────────────────────────────────────────┐
  │ Is key already cached?                       │
  └───────┬───────────────────────┬──────────────┘
          │ Yes                   │ No
          │                       │
          ▼                       ▼
  ┌──────────────┐      ┌────────────────────────┐
  │ Return cached│      │ Read from environment  │
  │ value        │      │ os.getenv('ANTHROPIC_  │
  │              │      │            API_KEY')    │
  └──────────────┘      └────────┬───────────────┘
                                 │
                        ┌────────┴────────┐
                        │ Found?          │
                        └────┬────────┬───┘
                           Yes      No
                            │        │
                            ▼        ▼
                   ┌────────────┐  ┌──────────────────┐
                   │ Cache &    │  │ required=True?   │
                   │ return     │  │                  │
                   └────────────┘  └──┬───────────┬───┘
                                    Yes         No
                                     │           │
                                     ▼           ▼
                            ┌──────────────┐  ┌───────────┐
                            │ Raise        │  │ Return    │
                            │ APIKeyMissing│  │ None      │
                            │ Error        │  │           │
                            └──────────────┘  └───────────┘
```

---

## Error Handling Architecture

### Exception Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Exception Hierarchy                           │
│            coffee_maker/exceptions.py                            │
└─────────────────────────────────────────────────────────────────┘

                    CoffeeMakerError (Base)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ConfigError      ProviderError      ResourceError
        │                   │                   │
        ├─ APIKeyMissing    ├─ RateLimitError   ├─ FileNotFound
        ├─ ConfigNotFound   ├─ ModelError       ├─ DatabaseError
        └─ ValidationError  └─ APIError         └─ NetworkError

        ┌───────────────────┼───────────────────┐
        │                   │                   │
    DaemonError      FileOperationError   AnalyticsError
        │                                       │
        ├─ DaemonCrashError                    ├─ LangfuseError
        └─ DaemonStateError                    └─ MetricError
```

### Error Recovery Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Error Recovery Flow                          │
└─────────────────────────────────────────────────────────────────┘

  Operation Execution
  ┌──────────────────────────────────────────────┐
  │ Execute operation (API call, file I/O, etc.) │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  Try Block
  ┌──────────────────────────────────────────────┐
  │ try:                                         │
  │     result = dangerous_operation()           │
  └───────────────────┬──────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │ Success                 │ Error
         ▼                         ▼
  ┌──────────────┐      ┌────────────────────────┐
  │ Return result│      │ Exception caught       │
  └──────────────┘      └────────┬───────────────┘
                                 │
                                 ▼
                        Classify Error
                        ┌────────────────┐
                        │ Match exception│
                        │ to recovery    │
                        │ strategy       │
                        └────────┬───────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
  Retry Strategy        Circuit Breaker      Fallback
  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
  │ Exponential  │     │ Open/Closed  │    │ Use default  │
  │ backoff      │     │ Half-open    │    │ Degraded mode│
  │ Max 3 retries│     │ Track        │    │ Alternative  │
  └──────┬───────┘     └──────┬───────┘    └──────┬───────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
                        Log Error
                        ┌────────────────┐
                        │ • Log to file  │
                        │ • Log to       │
                        │   Langfuse     │
                        │ • Notify user  │
                        └────────────────┘
```

---

## Directory Structure

### Complete System Layout

```
MonolithicCoffeeMakerAgent/
├── .claude/                        # Claude Code configuration
│   ├── CLAUDE.md                   # Project instructions
│   ├── commands/                   # Centralized prompts ⭐
│   │   ├── create-technical-spec.md
│   │   ├── implement-feature.md
│   │   ├── implement-documentation.md
│   │   └── ...
│   ├── mcp/                        # MCP server configs ⭐
│   │   └── puppeteer.json
│   └── settings.local.json
│
├── coffee_maker/                   # Main application package
│   ├── __init__.py
│   │
│   ├── ai_providers/               # AI provider abstraction
│   │   ├── __init__.py            # Provider registry
│   │   └── providers/
│   │       ├── claude_provider.py
│   │       ├── openai_provider.py
│   │       └── gemini_provider.py
│   │
│   ├── autonomous/                 # Autonomous daemon system
│   │   ├── daemon.py              # Core daemon (611 lines)
│   │   ├── daemon_git_ops.py      # GitOpsMixin (231 lines)
│   │   ├── daemon_spec_manager.py # SpecManagerMixin (181 lines)
│   │   ├── daemon_implementation.py # ImplementationMixin (481 lines)
│   │   ├── daemon_status.py       # StatusMixin (313 lines)
│   │   ├── developer_status.py    # Status tracking
│   │   ├── claude_cli_interface.py # CLI integration
│   │   └── prompt_loader.py       # Prompt loading ⭐
│   │
│   ├── cli/                        # Command-line interfaces
│   │   ├── roadmap_cli.py         # Main CLI (Typer)
│   │   ├── roadmap_editor.py      # ROADMAP editing (945 lines)
│   │   ├── ai_service.py          # AI service (739 lines)
│   │   ├── notifications.py       # Notification system
│   │   ├── github.py              # GitHub utilities
│   │   └── commands/              # Sub-commands
│   │       ├── user_story.py
│   │       └── ...
│   │
│   ├── config/                     # Configuration system ⭐
│   │   ├── __init__.py
│   │   ├── manager.py             # ConfigManager (centralized)
│   │   └── database_paths.py
│   │
│   ├── utils/                      # Utility modules ⭐
│   │   ├── logging.py             # Logging utilities
│   │   ├── file_io.py             # File I/O utilities
│   │   ├── time.py                # Time utilities
│   │   ├── validation.py          # Validation helpers
│   │   └── run_daemon_process.py
│   │
│   ├── exceptions.py               # Exception hierarchy ⭐
│   │
│   ├── langfuse_observe/           # Langfuse integration
│   │   ├── __init__.py
│   │   ├── llm.py                 # LLM with observability
│   │   ├── retry.py               # Retry logic
│   │   ├── agents.py              # Agent tracking
│   │   ├── cost_calculator.py
│   │   └── analytics/
│   │
│   ├── code_reviewer/              # Code review system
│   │   ├── main.py
│   │   └── perspectives/
│   │
│   └── streamlit_apps/             # Dashboard UIs
│       ├── streamlit_analytics.py
│       ├── streamlit_agent_ui.py
│       └── streamlit_errors.py
│
├── docs/                           # Documentation
│   ├── ROADMAP.md                 # Master task list ⭐
│   ├── ARCHITECTURE.md            # This file ⭐
│   ├── REFACTORING_GUIDE.md       # Refactoring guide ⭐
│   ├── ERROR_RECOVERY_STRATEGIES.md # Error handling ⭐
│   ├── PRIORITY_*_TECHNICAL_SPEC.md # Feature specs
│   ├── DAILY_STANDUP_GUIDE.md
│   └── ...
│
├── data/                           # Runtime data
│   ├── developer_status.json      # Daemon status
│   ├── notifications.db           # SQLite DB
│   └── analytics.db
│
├── tests/                          # Test suite
│   ├── unit/
│   ├── integration/
│   └── ci_tests/
│
├── tickets/                        # Bug tracking
│   ├── BUG-001.md
│   └── BUG-002.md
│
├── pyproject.toml                  # Poetry configuration
├── poetry.lock
└── README.md
```

### Key Directories Explained

**`.claude/`**: Claude Code configuration
- `CLAUDE.md` - Main instructions for Claude
- `commands/` - Centralized prompt templates for all agents
- `mcp/` - Model Context Protocol server configurations

**`coffee_maker/autonomous/`**: The autonomous daemon
- Core daemon orchestrates all operations
- Mixins provide separation of concerns
- Prompt loader enables multi-provider support

**`coffee_maker/config/`**: Unified configuration
- ConfigManager centralizes all configuration
- API key management with validation
- Environment variable handling

**`coffee_maker/utils/`**: Shared utilities
- Logging utilities with consistent formatting
- File I/O utilities with atomic operations
- Validation and helper functions

**`docs/`**: Living documentation
- ROADMAP.md - Source of truth for priorities
- Technical specs for each major feature
- Guides for development and operations

---

## Technology Stack

### Core Technologies

```
┌─────────────────────────────────────────────────────────────────┐
│                        Technology Stack                          │
├─────────────────────────────────────────────────────────────────┤
│ Language              │ Python 3.11+                            │
├─────────────────────────────────────────────────────────────────┤
│ Package Management    │ Poetry                                  │
├─────────────────────────────────────────────────────────────────┤
│ CLI Framework         │ Typer (based on Click)                  │
├─────────────────────────────────────────────────────────────────┤
│ Web Framework         │ Streamlit (dashboards)                  │
├─────────────────────────────────────────────────────────────────┤
│ AI Providers          │ Anthropic Claude, OpenAI, Google Gemini │
├─────────────────────────────────────────────────────────────────┤
│ Observability         │ Langfuse                                │
├─────────────────────────────────────────────────────────────────┤
│ Database              │ SQLite (local), PostgreSQL (future)     │
├─────────────────────────────────────────────────────────────────┤
│ Version Control       │ Git, GitHub API                         │
├─────────────────────────────────────────────────────────────────┤
│ Browser Automation    │ Puppeteer (via MCP)                     │
├─────────────────────────────────────────────────────────────────┤
│ Testing               │ pytest                                  │
├─────────────────────────────────────────────────────────────────┤
│ Code Quality          │ black, mypy, pre-commit hooks           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Dependencies

- **anthropic**: Claude API client
- **openai**: OpenAI GPT client
- **google-generativeai**: Gemini client
- **langfuse**: Analytics and observability
- **typer**: CLI framework
- **streamlit**: Dashboard framework
- **pydantic**: Data validation
- **sqlalchemy**: Database ORM
- **requests**: HTTP client
- **pyyaml**: Configuration files
- **rich**: Terminal formatting

---

## Development Guidelines

### Adding New Components

1. **New Agent**: Add to `coffee_maker/autonomous/` or create specialized module
2. **New CLI Command**: Add to `coffee_maker/cli/commands/`
3. **New Utility**: Add to `coffee_maker/utils/`
4. **New AI Provider**: Add to `coffee_maker/ai_providers/providers/`

### Architecture Principles

1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Dependency Injection**: Use constructor injection for testability
3. **Configuration Over Code**: Use ConfigManager for all configuration
4. **Error Handling**: Use custom exceptions with proper recovery strategies
5. **Observability**: Log all operations to Langfuse
6. **Documentation**: Update architecture docs when making structural changes

### Design Patterns Used

- **Mixin Pattern**: Daemon functionality split into composable mixins
- **Strategy Pattern**: AI providers implement common interface
- **Singleton Pattern**: ConfigManager (single instance)
- **Factory Pattern**: Provider registry creates appropriate providers
- **Observer Pattern**: Status updates notify multiple listeners
- **Command Pattern**: CLI commands encapsulate operations

---

## Future Architecture Improvements

### Phase 2.4: langfuse_observe Restructuring (Deferred)

**Current Issue**: Only 13% of files in `langfuse_observe/` actually use the `@observe` decorator

**Proposed Structure**:
```
coffee_maker/
├── langfuse_observe/          # Only files using @observe
│   ├── agents.py
│   ├── cost_calculator.py
│   ├── retry.py
│   └── analytics/
├── llm/                       # Core LLM abstractions (new)
│   ├── llm.py
│   ├── rate_limiting/
│   ├── strategies/
│   └── providers/
└── utils/                     # General utilities
    ├── http_pool.py
    └── token_estimator.py
```

**Benefits**:
- Clear separation of Langfuse-specific vs general LLM code
- Easier to understand and maintain
- Reduces confusion about what goes where
- Estimated effort: 5-6 days

### Phase 4: Performance Optimization

- Profile and optimize slow operations
- Add caching layers
- Optimize import statements
- Reduce test execution time (<2 minutes)

### Long-term Goals

- Web-based dashboard (alternative to CLI)
- Real-time collaboration features
- Plugin system for custom agents
- Multi-project workspace support
- Advanced analytics and reporting

---

## Maintenance and Updates

This architecture document should be updated when:
- Major new components are added
- Significant refactoring changes structure
- New architectural patterns are introduced
- Agent ownership/responsibilities change

**Last Updated**: 2025-10-12
**Next Review**: After Phase 2.4 completion

---

## References

- ROADMAP.md - Current priorities and status
- REFACTORING_GUIDE.md - Code quality guidelines
- ERROR_RECOVERY_STRATEGIES.md - Error handling patterns
- .claude/CLAUDE.md - Claude Code instructions
- Individual PRIORITY_*_TECHNICAL_SPEC.md files for feature details
