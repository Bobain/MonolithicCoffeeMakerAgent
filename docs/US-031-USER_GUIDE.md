# US-031: User Guide - Custom AI Development Environment

**Status**: Complete
**Created**: 2025-10-23
**Related**: US-031 - Custom AI Development Environment

## Overview

This guide shows you how to use the MonolithicCoffeeMakerAgent system across its different modes and interfaces. Learn when to use each mode and how to switch between them effortlessly.

---

## Table of Contents

1. [System Modes Overview](#system-modes-overview)
2. [CLI Mode - Interactive Chat](#cli-mode---interactive-chat)
3. [Project Manager Mode](#project-manager-mode)
4. [Daemon Mode - Autonomous Operation](#daemon-mode---autonomous-operation)
5. [Architect Mode](#architect-mode)
6. [Orchestrator Mode](#orchestrator-mode)
7. [Switching Between Modes](#switching-between-modes)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## System Modes Overview

MonolithicCoffeeMakerAgent offers multiple interfaces for different use cases:

| Mode | Command | Purpose | When to Use |
|------|---------|---------|-------------|
| **CLI Mode** | `user-listener` | Interactive chat, agent routing | Quick questions, code exploration |
| **Project Manager** | `project-manager` | ROADMAP management, status | View priorities, manage tasks |
| **Daemon Mode** | `code-developer` | Autonomous implementation | Hands-off feature development |
| **Architect Mode** | `architect` | Technical design, specs | Create specs, ADRs, architecture |
| **Orchestrator** | `orchestrator` | Parallel execution | Run multiple priorities simultaneously |

### Quick Decision Guide

**Use CLI Mode when you want to**:
- Ask questions about the codebase
- Search for specific code
- Get quick help or explanations
- Interactively explore features

**Use Project Manager when you want to**:
- View the ROADMAP
- Check priority status
- Manage notifications
- Add user stories
- View metrics and analytics

**Use Daemon Mode when you want to**:
- Implement features automatically
- Run continuous development overnight
- Hands-off autonomous operation

**Use Architect Mode when you want to**:
- Create technical specifications
- Write ADRs (Architecture Decision Records)
- Design system architecture
- Analyze codebase weekly (CFR-011)

**Use Orchestrator when you want to**:
- Work on multiple priorities in parallel
- Speed up development with concurrent execution
- Manage complex multi-priority workflows

---

## CLI Mode - Interactive Chat

### Starting CLI Mode

```bash
poetry run user-listener
```

### Features

- **Interactive chat interface** with rich console output
- **Agent routing** - automatically delegates to specialized agents
- **Multi-line input** - compose complex queries
- **Command history** - up/down arrows
- **Syntax highlighting** - code snippets beautifully formatted
- **User story detection** - automatic detection of feature requests

### Example Session

```
$ poetry run user-listener

┌──────────────────────────────────────────────────┐
│  Coffee Maker Agent - User Listener             │
│  Type /help for commands, /exit to quit         │
└──────────────────────────────────────────────────┘

You: Where is the notification database code?

[Routes to assistant agent (with code-forensics and security-audit skills)...]
