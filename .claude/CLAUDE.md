# MonolithicCoffeeMakerAgent - Claude Instructions

## Project Overview

**MonolithicCoffeeMakerAgent** is an autonomous software development system with multiple AI agents working together to implement features, manage projects, and provide assistance.

**Key Philosophy**: Autonomous, observable, multi-AI provider support

---

## Core Agents

| Agent | Role | Interaction |
|-------|------|-------------|
| **user_listener** | PRIMARY USER INTERFACE - Only agent with UI | Direct user interaction |
| **architect** | Architectural design, specs, ADRs, dependencies | Through user_listener |
| **code_developer** | Autonomous implementation from ROADMAP | Backend only |
| **project_manager** | Project coordination, GitHub monitoring, notifications | Backend only |
| **assistant** | Documentation expert, intelligent dispatcher, demo creator | Mixed |
| **ux-design-expert** | UI/UX design guidance and Tailwind CSS | Through user_listener |
| **code-reviewer** | Automated QA, reviews commits, notifies architect | Backend only |

**See [docs/AGENT_OWNERSHIP.md](../docs/AGENT_OWNERSHIP.md) for complete agent boundaries and responsibilities.**

---

## Project Structure

```
MonolithicCoffeeMakerAgent/
├── .claude/                         # Claude Code configuration
│   ├── commands/                    # Centralized prompts (MANDATORY location)
│   └── skills/                      # Claude Skills
├── docs/
│   ├── roadmap/ROADMAP.md          # Master task list (project_manager)
│   ├── architecture/               # Specs, ADRs, guidelines, POCs (architect)
│   ├── WORKFLOWS.md                # Detailed workflows
│   └── AGENT_OWNERSHIP.md          # Agent responsibilities
├── coffee_maker/                   # All implementation (code_developer)
└── tests/                          # All test code (code_developer)
```

---

## Critical Standards (MANDATORY)

### Python Style
- **Follow**: `.gemini/styleguide.md` - ALL code MUST comply
- **Black formatting**: Enforced by pre-commit hooks
- **Type hints**: Required for all functions
- **Line length**: 120 characters

### Architecture Patterns
- **Mixins**: Use composition (daemon uses mixins pattern)
- **Singletons**: AgentRegistry, HTTPConnectionPool, GlobalRateTracker (use context manager)
- **Observability**: Langfuse decorators for tracking

### Key Rules (CFRs)

**CFR-000 - Singleton Agent Enforcement**: Each agent type MUST have only ONE running instance at a time
- **Implementation**: `AgentRegistry` in `coffee_maker/autonomous/agent_registry.py`
- **Usage**: Always use context manager pattern: `with AgentRegistry.register(AgentType.CODE_DEVELOPER):`
- **Reason**: Prevents file conflicts, duplicate work, and resource waste
- **Docs**: See [docs/AGENT_SINGLETON_ARCHITECTURE.md](../docs/AGENT_SINGLETON_ARCHITECTURE.md)
- **Tests**: `tests/unit/test_agent_registry.py` (30+ comprehensive tests)

**CFR-007 - Context Budget**: Agent core materials MUST fit in ≤30% of context window
- See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` for remediation strategies

**CFR-009 - Sound Notifications**: ONLY `user_listener` uses `sound=True`. All background agents MUST use `sound=False`

**CFR-013 - Git Workflow**: ALL agents work on `roadmap` branch ONLY. NO feature branches.
- **Exception**: orchestrator may create temporary `roadmap-implementation_task-*` worktree branches for parallel execution
- **Branch naming**: `roadmap-implementation_task-{task_id}` (e.g., `roadmap-implementation_task-TASK-31-1`)
- **One worktree per task**: Each implementation task gets its own isolated worktree and branch
- architect merges `roadmap-implementation_task-*` → `roadmap` after EACH task completes, then orchestrator cleans up
- **Sequential within group**: TASK-31-1 → merge → TASK-31-2 → merge (each in own worktree)
- **Parallel across groups**: TASK-31-1 and TASK-32-1 can run simultaneously (different worktrees)
- See [GUIDELINE-004](../docs/architecture/guidelines/GUIDELINE-004-git-tagging-workflow.md) for tagging
- See CFR-013 "Git Worktree Workflow" section for complete lifecycle

**CFR-014 - Database Tracing**: ALL orchestrator activities in SQLite database. JSON files FORBIDDEN.

**CFR-015 - Centralized Database Storage**: ALL database files MUST be stored in `data/` directory ONLY.
- **Implementation**: All .db, .sqlite, .sqlite3 files in `data/` directory
- **Prohibited**: Database files in root, `.claude/`, or any other location
- **Reason**: Organization, backup, security, and deployment simplicity
- **Docs**: See [docs/CFR-015-CENTRALIZED-DATABASE-STORAGE.md](../docs/CFR-015-CENTRALIZED-DATABASE-STORAGE.md)

### Prompts
- **Location**: `.claude/commands/` (centralized, MANDATORY)
- **Usage**: `load_prompt(PromptNames.X, {...})` from `coffee_maker.autonomous.prompt_loader`

### Dependencies
- **Three-tier approval**: See [SPEC-070](../docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md)
- **CLI check**: `poetry run project-manager check-dependency <package>`

### POCs (Proof of Concepts)
- **When**: Complex features (>2 days OR high complexity)
- **Location**: `docs/architecture/pocs/POC-{number}-{slug}/`
- **Guide**: See [docs/architecture/POC_CREATION_GUIDE.md](../docs/architecture/POC_CREATION_GUIDE.md)
- **Spec**: [SPEC-050](../docs/architecture/specs/SPEC-050-poc-management-and-workflow.md)

---

## Running the System

```bash
# Start autonomous daemon
poetry run code-developer --auto-approve

# Monitor progress
poetry run project-manager developer-status
poetry run project-manager notifications
poetry run project-manager /roadmap
```

---

## Workflows

**See [docs/WORKFLOWS.md](../docs/WORKFLOWS.md) for all detailed workflows:**

1. Implementing a New Priority
2. Adding a New Prompt
3. Using Puppeteer MCP
4. Git Tagging Workflow
5. Creating a POC for Complex Implementation
6. Architect CFR-011 Compliance (Daily Integration)
7. Dependency Management

**Quick Commands:**
```bash
pytest                              # Run tests
black .                             # Format code
poetry run project-manager /roadmap # Check ROADMAP
pre-commit run --all-files         # Run all hooks
```

### GitHub CLI (`gh`)
GitHub CLI is configured and available for all GitHub operations:

```bash
# Pull Requests
gh pr list                          # List open PRs
gh pr view 123                      # View PR details
gh pr create --title "..." --body "..."  # Create PR
gh pr checks                        # Check CI status
gh pr merge                         # Merge PR

# Issues
gh issue list                       # List open issues
gh issue view 42                    # View issue details
gh issue create --title "..." --body "..."  # Create issue
gh issue close 42                   # Close issue

# Repository Info
gh repo view                        # View repo details
gh api repos/Bobain/MonolithicCoffeeMakerAgent/branches/roadmap  # API access

# Releases
gh release list                     # List releases
gh release create v1.0.0            # Create release
```

**When to use `gh`:**
- Checking PR/issue status (project_manager monitoring)
- Creating PRs from commits (code_developer workflow)
- Viewing CI check results
- Querying repository information
- Managing releases and tags

---

## Agent Decision Framework

```
"Who should handle X?"
    ↓
UI needed? → user_listener
Architectural design? → architect
Quick question? → assistant
Demo creation? → assistant
Project status? → project_manager
Design? → ux-design-expert
Implementation? → code_developer
```

---

## Implementation Checklist

When implementing features:

1. **Check ROADMAP first**: `docs/roadmap/ROADMAP.md`
2. **Find specs**: Strategic (`docs/roadmap/PRIORITY_*`) and technical (`docs/architecture/specs/SPEC-*`)
3. **Use centralized prompts**: Load from `.claude/commands/`
4. **Follow patterns**: Mixins, singletons, defensive programming
5. **Commit properly**: Descriptive message + 🤖 footer + Co-Authored-By

---

## Key Systems

1. **Prompt Management**: `.claude/commands/` (centralized)
2. **MCP Integration**: Puppeteer for browser automation
3. **Claude Skills**: Automated capabilities (in `.claude/skills/`)
4. **Observability**: Langfuse tracking for all executions

---

## Multi-AI Provider Support

Designed to work with multiple AI providers (Claude, Gemini, OpenAI). All prompts use centralized loading system for provider-agnostic execution.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Where are prompts? | `.claude/commands/*.md` |
| Where's ROADMAP? | `docs/roadmap/ROADMAP.md` |
| Style guide? | `.gemini/styleguide.md` |
| Agent boundaries? | `docs/AGENT_OWNERSHIP.md` |
| Workflows? | `docs/WORKFLOWS.md` |
| Daemon status? | `poetry run project-manager developer-status` |
| **ACE Tutorial?** | **[docs/ACE_CONSOLE_DEMO_TUTORIAL.md](../docs/ACE_CONSOLE_DEMO_TUTORIAL.md)** ⭐ |
| **ACE Quick Ref?** | **[docs/ACE_QUICK_REFERENCE.md](../docs/ACE_QUICK_REFERENCE.md)** |

---

**Last Updated**: 2025-10-20 | **Status**: Production ✅

**Remember**: Autonomy, observability, multi-provider support. Keep prompts centralized, track everything, design for flexibility.
