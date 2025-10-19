# MonolithicCoffeeMakerAgent - Claude Instructions

## Project Overview

**MonolithicCoffeeMakerAgent** is an autonomous software development system featuring multiple AI agents that work together to implement features, manage projects, and provide assistance.

**Key Philosophy**: Autonomous, observable, multi-AI provider support

---

## Core Agents

- **user_listener**: PRIMARY USER INTERFACE - Interprets user intent and delegates to team (ONLY agent with UI)
- **architect**: Architectural design and technical specifications (interacts through user_listener)
- **code_developer**: Autonomous implementation of priorities from ROADMAP
- **project_manager**: Project coordination, notifications, status tracking, GitHub monitoring (backend only)
- **assistant**: Documentation expert, intelligent dispatcher, demo creator, and bug reporter
- **code-searcher**: Deep codebase analysis and forensic examination
- **ux-design-expert**: UI/UX design guidance and Tailwind CSS
- **code-reviewer**: Automated quality assurance, reviews code_developer commits, notifies architect

---

## Project Structure

```
MonolithicCoffeeMakerAgent/
├── .claude/
│   ├── CLAUDE.md                    # This file (instructions)
│   ├── commands/                    # Centralized prompts
│   ├── skills/                      # Claude Skills (Phase 2)
│   ├── mcp/                         # MCP server configs
│   └── settings.local.json
│
├── docs/
│   ├── roadmap/                     # Project planning (project_manager)
│   │   ├── ROADMAP.md               # Master task list
│   │   └── PRIORITY_*_STRATEGIC_SPEC.md
│   ├── architecture/                # Technical design (architect)
│   │   ├── specs/                   # Technical specifications
│   │   ├── decisions/               # ADRs
│   │   ├── guidelines/              # Implementation guidelines
│   │   └── pocs/                    # Proof-of-Concepts
│   ├── WORKFLOWS.md                 # Detailed workflows
│   └── AGENT_OWNERSHIP.md           # Agent responsibilities
│
├── coffee_maker/                    # All implementation (code_developer)
│   ├── autonomous/                  # Daemon and agents
│   ├── cli/                         # CLI commands
│   └── utils/                       # Utilities
│
└── tests/                           # All test code (code_developer)
```

---

## Critical Coding Standards

### Python Style ⭐ **MANDATORY**
- **Style Guide**: `.gemini/styleguide.md` - ALL code MUST follow this guide
- **Formatter**: Black (enforced by pre-commit hooks)
- **Type Hints**: REQUIRED for all functions
- **Docstrings**: Google style with triple double quotes
- **Line Length**: 120 characters
- See `.gemini/styleguide.md` for complete details

### Architecture Patterns
- **Mixins**: Daemon uses composition with mixins
- **Singletons**: Critical resources use singleton pattern (AgentRegistry, HTTPConnectionPool, GlobalRateTracker)
- **Observability**: Use Langfuse decorators for tracking
- **Error Handling**: Defensive programming, validate inputs, handle None gracefully

### Singleton Pattern (US-035)
**CRITICAL**: Only ONE instance of each agent type can run at a time.

```python
# ✅ RECOMMENDED: Use context manager
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    # Agent work here - automatically unregistered on exit
    pass
```

### Prompt Management
**IMPORTANT**: All prompts MUST go in `.claude/commands/`

```python
# ✅ DO: Use centralized prompts
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": priority_name,
    "SPEC_FILENAME": spec_filename,
    "PRIORITY_CONTEXT": context
})
```

### Git Workflow (CFR-013)
- **Branch**: `roadmap` ONLY - ALL agents work on roadmap branch
- **NO Feature Branches**: Agents cannot create or switch to feature/* branches
- **Commits**: Descriptive messages with 🤖 footer
- **Tags**: See [GUIDELINE-004](../docs/architecture/guidelines/GUIDELINE-004-git-tagging-workflow.md)
  - `wip-*`: code_developer marks implementation complete
  - `dod-verified-*`: project_manager marks DoD verified
  - `stable-v*.*.*`: Production-ready releases

### Dependency Management (ADR-013)
**Three-tier approval system** - See [SPEC-070](../docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md)

```python
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

checker = DependencyChecker()
status = checker.get_approval_status("package-name")

if status == ApprovalStatus.PRE_APPROVED:
    # Auto-approve (63 packages: pytest, black, langfuse, etc.)
    subprocess.run(["poetry", "add", "package-name"])
elif status == ApprovalStatus.NEEDS_REVIEW:
    # Delegate to architect (requires user approval)
elif status == ApprovalStatus.BANNED:
    # Reject with alternatives
```

**CLI Check**:
```bash
poetry run project-manager check-dependency package-name
```

### Sound Notifications (CFR-009)
**CRITICAL**: ONLY user_listener can use sound notifications. All background agents MUST use `sound=False`.

```python
# ✅ CORRECT (background agents: code_developer, architect, project_manager, assistant)
self.notifications.create_notification(
    title="Task Complete",
    message="PRIORITY 13 implemented",
    level="info",
    sound=False,  # Silent for background work
    agent_id="code_developer"
)

# ✅ CORRECT (user_listener only)
self.notifications.create_notification(
    title="User Action Required",
    message="Please review PR #123",
    level="high",
    sound=True,  # Sound allowed for user interaction
    agent_id="user_listener"
)
```

---

## 🚀 Running the System

### Start Autonomous Daemon

```bash
poetry run code-developer --auto-approve
```

**What this does:**
- 🤖 Autonomous Mode: code_developer works continuously
- 📋 Implements ROADMAP: Automatically picks next priority
- ✅ Auto-Approve: Makes implementation decisions automatically
- 🌿 CFR-013 Compliant: All work on `roadmap` branch only

**Monitor progress:**
```bash
poetry run project-manager developer-status
poetry run project-manager notifications
poetry run project-manager /roadmap
```

**Stop the daemon:** Press `Ctrl+C`

---

## Key Workflows

**See [docs/WORKFLOWS.md](../docs/WORKFLOWS.md) for detailed workflows:**

1. Implementing a New Priority
2. Adding a New Prompt
3. Using Puppeteer MCP
4. Git Tagging Workflow
5. Creating a POC for Complex Implementation
6. Architect CFR-011 Compliance (Daily Integration)
7. Dependency Management

**Quick Commands:**
```bash
# Run tests
pytest

# Format code
black .

# Check ROADMAP
poetry run project-manager /roadmap

# Pre-commit hooks
pre-commit run --all-files
```

---

## Agent Ownership & Boundaries

**See [docs/AGENT_OWNERSHIP.md](../docs/AGENT_OWNERSHIP.md) for complete details.**

### Quick Reference

| Agent | Primary Responsibility | Cannot Do |
|-------|----------------------|-----------|
| **user_listener** | ONLY UI agent | Backend tasks |
| **architect** | Specs, ADRs, dependencies | Code implementation |
| **code_developer** | Code, .claude/ configs | Strategic docs, dependencies |
| **project_manager** | docs/roadmap/, GitHub | Code, .claude/, architecture |
| **assistant** | Docs expert, dispatcher, demos, QA | Code editing, strategic decisions |
| **code-searcher** | Deep code analysis | Writing docs directly |

### Decision Framework

```
"Who should handle X?"
    ↓
UI needed? → user_listener
Architectural design? → architect
Quick question? → assistant
Demo creation? → assistant
Code internals? → code-searcher
Project status? → project_manager
Design? → ux-design-expert
Implementation? → code_developer
```

---

## Important Context

### Context Budget (CFR-007) ⭐ CRITICAL
**Agent core materials must fit in ≤30% of context window.** This ensures agents have room to work (70% remaining for files, analysis, and responses). See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` CFR-007 for remediation strategies.

### Key Systems

1. **Prompt Management**: `.claude/commands/` (centralized), Langfuse (Phase 2 - planned)
2. **MCP Integration**: Puppeteer for browser automation
3. **Claude Skills**: Automated capabilities (roadmap-health, architecture-analysis, demo-creator, security-audit, etc.)
4. **Observability**: Langfuse tracking for all executions

---

## Special Instructions for Claude

### When Implementing Features
1. **Check ROADMAP first**: `docs/roadmap/ROADMAP.md`
2. **Look for specs**: Strategic (`docs/roadmap/PRIORITY_*`) and technical (`docs/architecture/specs/SPEC-*`)
3. **Use centralized prompts**: Load from `.claude/commands/`
4. **Follow mixins pattern**: Don't create monolithic files
5. **Update status**: Use DeveloperStatus class

### When Creating Prompts
1. **Save to**: `.claude/commands/`
2. **Use placeholders**: `$VARIABLE_NAME` format
3. **Add to PromptNames**: In `prompt_loader.py`

### When Committing
1. **Descriptive message**: Explain what and why
2. **Include footer**: 🤖 Generated with Claude Code
3. **Co-author**: `Co-Authored-By: Claude <noreply@anthropic.com>`
4. **Tag appropriately**: See GUIDELINE-004 for git tagging workflow

---

## Multi-AI Provider Support

This project is designed to work with **multiple AI providers** (Claude, Gemini, OpenAI).

**Migration Path**:
```python
# Works with ANY provider
prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {...})

# Provider-specific execution
result = provider.execute(prompt)  # Claude, Gemini, or OpenAI
```

---

## Quick Troubleshooting

| Question | Answer |
|----------|--------|
| Where are the prompts? | `.claude/commands/*.md` |
| Where's the ROADMAP? | `docs/roadmap/ROADMAP.md` |
| How do I check daemon status? | `poetry run project-manager developer-status` |
| Tests failing? | `pre-commit run --all-files` |
| Detailed workflows? | See `docs/WORKFLOWS.md` |
| Agent responsibilities? | See `docs/AGENT_OWNERSHIP.md` |

---

## Version

**Last Updated**: 2025-10-19
**Status**: Production ✅

---

**Remember**: This project emphasizes autonomy, observability, and multi-provider support. Keep prompts centralized, track everything, and design for flexibility! 🚀
