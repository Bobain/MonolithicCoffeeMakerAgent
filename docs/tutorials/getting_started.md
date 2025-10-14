# Getting Started with MonolithicCoffeeMakerAgent

Welcome! This guide will help you get up and running with the MonolithicCoffeeMakerAgent system.

## Table of Contents

1. [What is MonolithicCoffeeMakerAgent?](#what-is-monolithiccoffeemakeragent)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Running the System](#running-the-system)
5. [Essential Commands](#essential-commands)
6. [Monitoring Progress](#monitoring-progress)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## What is MonolithicCoffeeMakerAgent?

MonolithicCoffeeMakerAgent is an **autonomous software development system** featuring multiple AI agents that work together to:

- **Implement features autonomously** - The `code_developer` agent reads the ROADMAP and implements priorities automatically
- **Manage the project** - The `project_manager` agent coordinates work, monitors GitHub, and verifies completion
- **Answer questions** - The `assistant` agent has deep knowledge of all documentation and helps you navigate the system
- **Analyze code** - The `code-searcher` agent performs deep codebase analysis and security audits
- **Design interfaces** - The `ux-design-expert` agent provides UI/UX guidance

**Key Philosophy**: Autonomous, observable, multi-AI provider support

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (Python dependency management)
- Git
- A Claude API key or Claude CLI access

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent

# 2. Install dependencies with Poetry
poetry install

# 3. Set up environment variables (if using API mode)
cp .env.example .env
# Edit .env and add your Claude API key

# 4. Verify installation
poetry run pytest
```

**Success?** You should see all tests passing!

---

## Core Concepts

Before diving in, understand these key concepts:

### 1. The ROADMAP is King

**`docs/roadmap/ROADMAP.md`** is the **single source of truth** for all project work.

- Lists all priorities and features
- Tracks status (Planned, In Progress, Complete)
- Used by autonomous agents to decide what to work on
- Updated by `project_manager` (strategy) and `code_developer` (status)

### 2. Agents are Specialists

Each agent has a specific role and boundaries:

- **code_developer** - Writes and modifies ALL code
- **project_manager** - Manages documentation and strategic planning
- **assistant** - Answers questions and routes requests
- **code-searcher** - Performs deep code analysis (read-only)
- **ux-design-expert** - Provides design guidance

**Important**: Never ask an agent to do work outside their domain!

### 3. Two Modes of Operation

**Autonomous Mode** (Daemon):
```bash
poetry run code-developer --auto-approve
```
The system works independently, implementing priorities from the ROADMAP.

**Interactive Mode** (CLI):
```bash
poetry run project-manager /roadmap
poetry run project-manager developer-status
```
You interact with the system through commands.

### 4. Observability Matters

The system tracks everything:
- Developer status dashboard
- Langfuse integration for trace monitoring
- Notification system for daemon communication
- Real-time progress updates

---

## Running the System

### Option 1: Autonomous Daemon (Recommended)

The daemon runs continuously and implements features autonomously:

```bash
# Start the autonomous daemon
poetry run code-developer --auto-approve

# In another terminal, monitor progress
poetry run project-manager developer-status
```

**What happens:**
1. Daemon reads `docs/roadmap/ROADMAP.md`
2. Finds next priority marked as "Planned"
3. Creates technical spec (if needed)
4. Implements the feature
5. Runs tests and creates PR
6. Moves to next priority

### Option 2: Interactive CLI

Use the CLI for manual control:

```bash
# View the roadmap
poetry run project-manager /roadmap

# Check developer status
poetry run project-manager developer-status

# View notifications from daemon
poetry run project-manager notifications

# Get AI assistance
poetry run assistant "How do I implement authentication?"
```

### Option 3: Using Claude Desktop

If you have Claude Desktop configured:

1. Open Claude Desktop
2. Navigate to the project directory
3. Ask questions or delegate tasks to agents
4. The system will route your request appropriately

---

## Essential Commands

### Project Management Commands

```bash
# View the complete roadmap
poetry run project-manager /roadmap

# View a specific priority's details
poetry run project-manager /priority 15

# Check developer status
poetry run project-manager developer-status

# List notifications
poetry run project-manager notifications

# Check metrics (velocity, accuracy)
poetry run project-manager /metrics
```

### Development Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_roadmap.py

# Run tests with verbose output
pytest -v

# Format code (auto-runs on commit)
black .

# Check for code issues
flake8 coffee_maker/
```

### Daemon Commands

```bash
# Start daemon in autonomous mode
poetry run code-developer --auto-approve

# Start daemon in interactive mode (asks for approval)
poetry run code-developer

# Check daemon status (run from another terminal)
poetry run project-manager developer-status
```

### Git Commands

```bash
# Check current branch and status
git status

# View recent commits
git log --oneline -10

# Create a new feature branch
git checkout -b feature/my-feature

# Push to remote
git push origin feature/my-feature
```

---

## Monitoring Progress

### Developer Status Dashboard

The developer status dashboard shows real-time progress:

```bash
poetry run project-manager developer-status
```

**Shows:**
- Current priority being worked on
- Current phase (Spec Creation, Implementation, Testing, etc.)
- Progress percentage
- Estimated time remaining
- Velocity and accuracy metrics

### Notifications

The daemon communicates through notifications:

```bash
# List all notifications
poetry run project-manager notifications

# View a specific notification
poetry run project-manager notification <id>

# Approve daemon's work
poetry run project-manager respond <id> approve
```

### Langfuse Observability

If Langfuse is configured, you can view detailed traces:

1. Open your Langfuse dashboard
2. View traces for each agent execution
3. Analyze prompts, responses, and timing
4. Track costs and token usage

---

## Common Workflows

### Workflow 1: Starting a New Feature

**Scenario**: You want to implement a new feature.

```bash
# 1. Add the feature to ROADMAP.md
# Edit docs/roadmap/ROADMAP.md and add your priority

# 2. Start the daemon
poetry run code-developer --auto-approve

# 3. Monitor progress
poetry run project-manager developer-status

# 4. Review the PR when complete
# Check GitHub for the automatically created PR
```

### Workflow 2: Asking a Question

**Scenario**: You need to understand how something works.

```bash
# Option 1: Use the assistant agent via CLI
poetry run assistant "How does the prompt loading system work?"

# Option 2: Use Claude Desktop (if configured)
# Just ask your question naturally, and the assistant will help
```

**What the assistant does:**
- Searches relevant documentation
- Reads code files if needed
- Provides clear explanations with examples
- Delegates to specialized agents if needed

### Workflow 3: Checking Project Status

**Scenario**: You want to know what's happening in the project.

```bash
# 1. View the roadmap
poetry run project-manager /roadmap

# 2. Check what's in progress
poetry run project-manager developer-status

# 3. View metrics (velocity, estimation accuracy)
poetry run project-manager /metrics

# 4. Check recent activity
git log --oneline -10
```

### Workflow 4: Debugging an Issue

**Scenario**: Something isn't working correctly.

```bash
# 1. Run tests to identify failures
pytest -v

# 2. Check logs
cat data/developer_status.json

# 3. Ask the assistant for help
poetry run assistant "Why are tests failing in test_roadmap.py?"

# 4. If it's a code issue, delegate to code_developer
# "Please fix the bug in coffee_maker/cli/roadmap_cli.py"
```

### Workflow 5: Analyzing the Codebase

**Scenario**: You need deep code analysis or security audit.

```bash
# Ask the assistant, it will delegate to code-searcher
poetry run assistant "Find all authentication code and check for security issues"

# Or use Claude Desktop
# "I need a security audit of the authentication system"
```

**What happens:**
1. Assistant delegates to code-searcher agent
2. code-searcher performs deep analysis (read-only)
3. Prepares findings document
4. Presents findings to assistant
5. assistant delegates to project_manager
6. project_manager creates `docs/security_audit_2025-10-14.md`

---

## Troubleshooting

### Problem: "Command not found"

**Solution**: Make sure you're using Poetry to run commands:

```bash
# Wrong
code-developer --auto-approve

# Correct
poetry run code-developer --auto-approve
```

### Problem: "Tests are failing"

**Solution**: Check pre-commit hooks and run formatters:

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Format code
black .

# Run tests again
pytest
```

### Problem: "Daemon isn't doing anything"

**Solution**: Check the ROADMAP for available work:

```bash
# View roadmap
poetry run project-manager /roadmap

# Look for priorities marked as "📝 Planned"
# If none exist, add work to the ROADMAP
```

### Problem: "I don't know which agent to use"

**Solution**: Start with the assistant agent:

```bash
# Ask the assistant - it will route appropriately
poetry run assistant "I need to [your task here]"
```

The assistant is a documentation expert and intelligent dispatcher. It will:
- Answer simple questions directly
- Delegate complex tasks to appropriate agents
- Explain which agent handles what

### Problem: "Permission denied" or "Git errors"

**Solution**: Make sure you have proper GitHub authentication:

```bash
# Check your Git config
git config --list

# Set up GitHub authentication (PAT or SSH)
# See README.md for detailed instructions
```

### Problem: "Import errors" or "Module not found"

**Solution**: Reinstall dependencies:

```bash
# Remove existing environment
poetry env remove python

# Reinstall
poetry install

# Try again
poetry run pytest
```

---

## Next Steps

Now that you understand the basics:

1. **Read [Agent Interaction](./agent_interaction.md)** - Learn how to work with specialized agents
2. **Explore the ROADMAP** - See what features are planned and in progress
3. **Try autonomous mode** - Let the daemon implement a feature
4. **Ask questions** - Use the assistant agent to learn more

## Quick Reference Card

```bash
# Daily Commands
poetry run project-manager /roadmap          # View roadmap
poetry run project-manager developer-status  # Check progress
poetry run code-developer --auto-approve     # Start autonomous daemon
pytest                                       # Run tests

# Get Help
poetry run assistant "your question here"    # Ask for help
cat docs/roadmap/ROADMAP.md                          # Read roadmap
cat .claude/CLAUDE.md                        # Read project instructions
```

---

**Remember**: The system is designed to be autonomous and helpful. When in doubt, ask the assistant agent - it has deep knowledge of all documentation and will guide you appropriately!

**Next Tutorial**: [Agent Interaction](./agent_interaction.md) - Learn how agents work together

---

**Last Updated**: 2025-10-14
**Version**: 1.0
