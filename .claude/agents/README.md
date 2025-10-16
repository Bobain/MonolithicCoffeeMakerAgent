# Agent Definitions

This directory contains agent definitions for the MonolithicCoffeeMakerAgent project.

## Available Agents

### 1. code-developer
**Purpose**: Autonomous software developer that implements ROADMAP priorities

**Use When**:
- Implementing features from ROADMAP
- Creating technical specifications
- Autonomous code development
- DoD verification with Puppeteer

**Invoke**: `> Use the code-developer subagent to implement the next priority`

---

### 2. project-manager
**Purpose**: AI project manager for strategic planning and ROADMAP management

**Use When**:
- Analyzing project health
- Managing priorities
- Verifying completed work
- Checking GitHub PR/issue status
- Strategic planning

**Invoke**: `> Use the project-manager subagent to analyze the ROADMAP`

---

### 3. assistant
**Purpose**: General-purpose AI assistant for support and questions

**Use When**:
- Answering code questions
- Debugging problems
- Explaining architecture
- Demonstrating features
- Looking up GitHub info

**Invoke**: `> Use the assistant subagent to explain how the prompt system works`

---

### 4. architect
**Purpose**: Technical design authority for architectural specifications and dependency management

**Use When**:
- Creating technical specifications before implementation
- Documenting architectural decisions (ADRs)
- Managing dependencies (ONLY agent that can modify pyproject.toml)
- Providing implementation guidelines
- Ensuring architectural consistency

**Invoke**: `> Use the architect subagent to create a technical specification for feature X`

---

### 5. code-searcher
**Purpose**: Deep codebase analysis and forensic examination

**Use When**:
- Finding code patterns across the codebase
- Security audits
- Dependency tracing
- Architectural analysis of existing code
- Identifying refactoring opportunities

**Invoke**: `> Use the code-searcher subagent to find all authentication code`

---

### 6. ux-design-expert
**Purpose**: UI/UX design guidance and Tailwind CSS expertise

**Use When**:
- Designing dashboard layouts
- Making UI/UX decisions
- Configuring Highcharts visualizations
- Providing Tailwind CSS guidance
- Creating design systems

**Invoke**: `> Use the ux-design-expert subagent to design a dashboard layout`

---

## How to Use

### Via Claude CLI

**List available agents**:
```bash
claude --help  # or /agents command in interactive mode
```

**Explicit invocation**:
```
> Use the code-developer subagent to implement PRIORITY 5
> Use the project-manager subagent to check if US-032 is complete
> Use the assistant subagent to show me the dashboard with Puppeteer
```

**Automatic delegation**: Claude will automatically select the appropriate agent based on your request.

### In Python Code (Future Integration)

The agents defined here will later be integrated with the coded agents in the project:

```python
# Future: DevDaemon will use code-developer agent definition
from coffee_maker.autonomous.daemon import DevDaemon

daemon = DevDaemon()
daemon.run()  # Uses .claude/agents/code-developer.md for context
```

---

## Agent Capabilities

All agents have access to:

- **File Operations**: Read, Write, Edit
- **Code Search**: Glob, Grep
- **Bash Commands**: Run terminal commands
- **Puppeteer MCP**: Browser automation for testing/verification
- **GitHub CLI**: `gh` commands for issue/PR management

Each agent has specific tools configured in their YAML frontmatter.

---

## Context Management

### 📖 Critical Documents

Each agent has been configured to read specific critical documents at startup. These documents provide essential context for the agent to work effectively.

#### code-developer - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `docs/roadmap/ROADMAP.md` - Task list (read FIRST)
2. 🔴 `.claude/CLAUDE.md` - Project instructions (read SECOND)

**READ AS NEEDED**:
- `docs/roadmap/PRIORITY_*_TECHNICAL_SPEC.md` - Technical specs for complex priorities
- `.claude/commands/PROMPTS_INDEX.md` - Available prompts
- `.claude/commands/implement-feature.md` - Implementation guide
- `.claude/commands/verify-dod-puppeteer.md` - DoD verification guide

#### project-manager - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `docs/roadmap/ROADMAP.md` - Project status (read FIRST)
2. 🔴 `.claude/CLAUDE.md` - Project context (read SECOND)

**READ AS NEEDED**:
- `docs/roadmap/PRIORITY_*_TECHNICAL_SPEC.md` - Priority details
- `.claude/commands/PROMPTS_INDEX.md` - System capabilities
- `.claude/commands/verify-dod-puppeteer.md` - DoD verification

#### assistant - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `.claude/CLAUDE.md` - Project overview (read FIRST)
2. 🔴 `docs/roadmap/ROADMAP.md` - Current work (read SECOND)

**READ AS NEEDED**:
- `.claude/commands/PROMPTS_INDEX.md` - Prompt documentation
- Relevant code files (via Grep/Glob)
- `docs/roadmap/PRIORITY_*_TECHNICAL_SPEC.md` - Feature details
- `README.md` - Project overview

#### architect - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `docs/roadmap/ROADMAP.md` - Current priorities (read FIRST)
2. 🔴 `.claude/CLAUDE.md` - Project instructions (read SECOND)
3. 🔴 `.claude/agents/architect.md` - Own role definition (read THIRD)
4. 🔴 `docs/DOCUMENT_OWNERSHIP_MATRIX.md` - File ownership boundaries

**READ AS NEEDED**:
- `docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md` - Strategic requirements from project_manager
- `docs/architecture/specs/SPEC-*.md` - Previous technical specs for consistency
- `docs/architecture/decisions/ADR-*.md` - Historical architectural decisions
- `docs/architecture/guidelines/GUIDELINE-*.md` - Existing implementation guidelines
- `pyproject.toml` - Current dependencies (when evaluating new dependencies)

#### code-searcher - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `.claude/CLAUDE.md` - Project overview (read FIRST)
2. 🔴 `.claude/agents/code-searcher.md` - Own role definition (read SECOND)

**READ AS NEEDED**:
- All codebase files (comprehensive access for analysis)
- `docs/roadmap/ROADMAP.md` - Context for analysis requests
- Specific files/directories requested by user

#### ux-design-expert - Startup Documents

**READ AT STARTUP (MANDATORY)**:
1. 🔴 `.claude/CLAUDE.md` - Project standards (read FIRST)
2. 🔴 `.claude/agents/ux-design-expert.md` - Own role definition (read SECOND)

**READ AS NEEDED**:
- Design system documentation
- Tailwind configuration files
- Existing UI components
- `docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md` - Feature requirements

---

## File Format

Agent definitions use markdown with YAML frontmatter:

```markdown
---
name: agent-name
description: When to use this agent
tools: tool1, tool2, tool3
model: sonnet
---

Agent system prompt and instructions go here...
```

**Required fields**:
- `name`: Unique identifier (lowercase, hyphen-separated)
- `description`: Natural language description of purpose

**Optional fields**:
- `tools`: Specific tools the agent can use
- `model`: Model to use (`sonnet`, `opus`, `haiku`, `inherit`)

---

## Version

**Version**: 2.0 (US-032 - Puppeteer DoD + GitHub CLI)
**Last Updated**: 2025-10-12

All agents equipped with:
- Puppeteer MCP for browser automation
- GitHub CLI for issue/PR management
- DoD verification capabilities
- Comprehensive context files

---

## Related Documentation

- **Prompts**: `.claude/commands/` - All agent prompts
- **Prompt Index**: `.claude/commands/PROMPTS_INDEX.md` - Prompt documentation
- **Project Instructions**: `.claude/CLAUDE.md` - How to work with this project
- **ROADMAP**: `docs/roadmap/ROADMAP.md` - Current priorities and status
