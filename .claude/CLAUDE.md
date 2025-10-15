# MonolithicCoffeeMakerAgent - Claude Instructions

## Project Overview

**MonolithicCoffeeMakerAgent** is an autonomous software development system featuring multiple AI agents that work together to implement features, manage projects, and provide assistance.

**Key Philosophy**: Autonomous, observable, multi-AI provider support

---

## Architecture

### Core Components

1. **Autonomous Agents**
   - `user_listener`: **PRIMARY USER INTERFACE** - Interprets user intent and delegates to team (ONLY agent with UI)
   - `code_developer`: Autonomous implementation of priorities from ROADMAP
   - `project_manager`: Project coordination, notifications, status tracking, GitHub monitoring (backend only)
   - `assistant`: Documentation expert and intelligent dispatcher
   - `code-searcher`: Deep codebase analysis and forensic examination
   - `ux-design-expert`: UI/UX design guidance and Tailwind CSS
   - `memory-bank-synchronizer`: Documentation synchronization with code reality

2. **Prompt Management System** ⭐ NEW
   - **Local Store**: `.claude/commands/` (centralized prompt templates)
   - **Source of Truth**: Langfuse (Phase 2 - planned)
   - **Loader**: `coffee_maker/autonomous/prompt_loader.py`
   - **Benefits**: Multi-AI provider support (Claude, Gemini, OpenAI)

3. **MCP Integration** ⭐ NEW
   - **Puppeteer MCP**: Browser automation for agents
   - **Project Config**: `.claude/mcp/puppeteer.json` (project-scoped)
   - **Global Config**: `~/Library/Application Support/Claude/config.json` (alternative)
   - **Use Cases**: Web testing, visual documentation, screenshots

4. **Observability**
   - Langfuse integration for tracking
   - Developer status dashboard
   - Real-time progress monitoring

5. **ACE Framework** (Agentic Context Engineering)
   - `generator`: Dual execution observation, trace capture
   - `reflector`: Insight extraction from traces
   - `curator`: Playbook maintenance, semantic de-duplication
   - **Reference**: https://www.arxiv.org/abs/2510.04618

---

## Project Structure

```
MonolithicCoffeeMakerAgent/
├── .claude/
│   ├── CLAUDE.md                    # This file (instructions)
│   ├── commands/                    # Centralized prompts ⭐
│   │   ├── create-technical-spec.md
│   │   ├── implement-documentation.md
│   │   ├── implement-feature.md
│   │   ├── test-web-app.md
│   │   └── capture-visual-docs.md
│   ├── mcp/                         # MCP server configs ⭐
│   │   └── puppeteer.json
│   └── settings.local.json
│
├── docs/
│   ├── roadmap/                     # Project planning ⭐
│   │   ├── ROADMAP.md               # Master task list
│   │   └── TEAM_COLLABORATION.md    # Agent interaction guide
│   ├── PROMPT_MANAGEMENT_SYSTEM.md  # Prompt system docs ⭐
│   ├── PRIORITY_4_1_TECHNICAL_SPEC.md # Puppeteer MCP ⭐
│   └── PRIORITY_*_TECHNICAL_SPEC.md # Feature specs
│
├── coffee_maker/
│   ├── autonomous/
│   │   ├── daemon.py                # Main daemon orchestrator
│   │   ├── daemon_spec_manager.py   # Spec creation (uses prompts)
│   │   ├── daemon_implementation.py # Implementation (uses prompts)
│   │   ├── prompt_loader.py         # Prompt loading utility ⭐ NEW
│   │   ├── developer_status.py      # Status tracking
│   │   └── claude_cli_interface.py  # Claude CLI integration
│   ├── cli/
│   │   ├── notifications.py         # Notification system
│   │   └── roadmap_cli.py          # CLI commands
│   └── langfuse_observe/           # Observability
│
└── tickets/                         # Bug tracking
    ├── BUG-001.md
    └── BUG-002.md
```

---

## Coding Standards

### Python Style
- **Formatter**: Black (enforced by pre-commit hooks)
- **Imports**: Use `autoflake` to remove unused imports
- **Line Length**: 120 characters (Black default: 88)
- **Type Hints**: Use where appropriate

### Architecture Patterns
- **Mixins**: Daemon uses composition with mixins (SpecManagerMixin, ImplementationMixin, etc.)
- **Observability**: Use Langfuse decorators for tracking
- **Error Handling**: Defensive programming, validate inputs, handle None gracefully

### Prompt Management ⭐
**IMPORTANT**: All prompts MUST go in `.claude/commands/`

```python
# ❌ DON'T: Hardcode prompts
prompt = f"""Create a spec for {priority_name}..."""

# ✅ DO: Use centralized prompts
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": priority_name,
    "SPEC_FILENAME": spec_filename,
    "PRIORITY_CONTEXT": context
})
```

### Git Workflow
- **Branch**: Feature branches (`feature/priority-X`)
- **Commits**: Descriptive messages with 🤖 footer
- **Pre-commit**: Hooks run automatically (black, autoflake, trailing-whitespace)

---

## Key Workflows

### 1. Implementing a New Priority

```bash
# 1. Check ROADMAP
cat docs/roadmap/ROADMAP.md

# 2. Create technical spec (if needed)
# Daemon uses: .claude/commands/create-technical-spec.md

# 3. Implement feature
# Daemon uses: .claude/commands/implement-feature.md or implement-documentation.md

# 4. Test and commit
pytest
git add .
git commit -m "feat: Implement PRIORITY X"
```

### 2. Adding a New Prompt

```bash
# 1. Create prompt file
cat > .claude/commands/my-new-prompt.md << 'EOF'
Do something with $VARIABLE_NAME.

Instructions:
- Step 1
- Step 2

Context:
$CONTEXT
EOF

# 2. Add to PromptNames
# Edit: coffee_maker/autonomous/prompt_loader.py
class PromptNames:
    MY_NEW_PROMPT = "my-new-prompt"

# 3. Use in code
prompt = load_prompt(PromptNames.MY_NEW_PROMPT, {
    "VARIABLE_NAME": value,
    "CONTEXT": context
})

# 4. Later: Sync to Langfuse (Phase 2)
# coffee_maker prompts sync
```

### 3. Using Puppeteer MCP

```bash
# In Claude Desktop, use browser automation:
"Navigate to https://example.com and take a screenshot"

# Or in code (future):
# result = await puppeteer_client.navigate("https://example.com")
# screenshot = await puppeteer_client.screenshot()
```

---

## Important Context

### Recent Developments (2025-10-12)

1. **✅ Prompt Centralization Complete**
   - All prompts moved to `.claude/commands/`
   - `PromptLoader` utility created
   - Daemon code updated to use centralized prompts
   - Ready for multi-AI provider support

2. **✅ Puppeteer MCP Integration Ready**
   - Technical spec created (PRIORITY 4.1)
   - Claude Desktop configured with MCP
   - Agents can now use browser automation

3. **📝 Langfuse Integration Planned (Phase 2)**
   - Langfuse will be source of truth for prompts
   - `.claude/commands/` becomes local cache
   - Full observability of all executions
   - Estimated: 10-14 hours to implement

### Bug Fixes
- **BUG-001**: Daemon stuck without `--auto-approve` → ✅ Fixed
- **BUG-002**: Daemon crashes with missing priority content → ✅ Fixed

### Completed Priorities
- PRIORITY 1: Analytics ✅
- PRIORITY 2: Project Manager CLI ✅
- PRIORITY 2.7: Daemon Crash Recovery ✅
- PRIORITY 2.8: Daemon Status Reporting ✅
- PRIORITY 2.9: Sound Notifications ✅
- PRIORITY 3: code_developer ✅
- PRIORITY 4: Developer Status Dashboard ✅

---

## Running the System

### Start Autonomous Daemon
```bash
# With auto-approve (autonomous mode)
poetry run code-developer --auto-approve

# Check status
poetry run project-manager developer-status

# View notifications
poetry run project-manager notifications
```

### Manual Commands
```bash
# Run tests
pytest

# Format code
black .

# Check roadmap
poetry run project-manager /roadmap

# View developer status
poetry run project-manager /status
```

---

## Agent Tool Ownership & Boundaries

**IMPORTANT**: Each agent has specific tool ownership to prevent overlap and confusion.

### File & Directory Ownership Matrix

**CRITICAL**: These rules determine WHO can modify WHAT files.

| File/Directory | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| **User Interface** | user_listener | **ONLY UI** for all user interactions | All others: NO UI (backend only) |
| **docs/** | project_manager | YES - Full control | code_developer: READ-ONLY, assistant: READ-ONLY, user_listener: READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | project_manager: Full, code_developer: Status updates only | assistant: READ-ONLY, user_listener: READ-ONLY |
| **docs/PRIORITY_*_TECHNICAL_SPEC.md** | project_manager | YES - Creates and updates specs | code_developer: READ-ONLY (reads during implementation), assistant: READ-ONLY, user_listener: READ-ONLY |
| **.claude/agents/** | project_manager | YES - Defines agent configurations | All others: READ-ONLY |
| **.claude/CLAUDE.md** | project_manager, memory-bank-synchronizer | YES - Strategic updates | code_developer: READ-ONLY, assistant: READ-ONLY, user_listener: READ-ONLY |
| **.claude/commands/** | project_manager | YES - Manages prompts | code_developer: READ-ONLY (loads during execution), assistant: READ-ONLY, user_listener: READ-ONLY |
| **coffee_maker/** | code_developer | YES - All implementation | All others: READ-ONLY |
| **tests/** | code_developer | YES - All test code | All others: READ-ONLY |
| **scripts/** | code_developer | YES - Utility scripts | All others: READ-ONLY |
| **pyproject.toml** | code_developer | YES - Dependency management | All others: READ-ONLY |

### Tool Ownership Matrix

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **User Interface (ALL)** | user_listener | **ONLY** agent with UI, chat, CLI interface | All others: Backend only, NO UI |
| **ACE UI Commands** | user_listener | `/curate`, `/playbook` in user_listener CLI | project_manager: Deprecated |
| **Puppeteer DoD (during impl)** | code_developer | Verify features DURING implementation | project_manager for POST-completion verification |
| **Puppeteer DoD (post-impl)** | project_manager | Verify completed work on user request | - |
| **Puppeteer demos** | user_listener | Show features visually via UI (delegates to assistant) | assistant prepares demos |
| **GitHub PR create** | code_developer | Create PRs autonomously | - |
| **GitHub monitoring** | project_manager | Monitor PRs, issues, CI/CD status | - |
| **GitHub queries** | project_manager | All `gh` commands | user_listener delegates via UI |
| **Code editing** | code_developer | ALL code changes | assistant READ-ONLY |
| **Code search (simple)** | assistant | 1-2 files with Grep/Read | user_listener delegates via UI |
| **Code search (complex)** | code-searcher | Deep analysis, patterns, forensics | user_listener delegates via UI |
| **Code analysis docs** | project_manager | Creates docs/[analysis]_[date].md | code-searcher prepares findings, user_listener delegates |
| **ROADMAP updates** | project_manager (full), code_developer (status only) | Strategic vs. execution updates | assistant READ-ONLY |
| **Design decisions** | ux-design-expert | All UI/UX, Tailwind, charts | user_listener delegates via UI |
| **Doc sync** | memory-bank-synchronizer | Keep CLAUDE.md files current | - |
| **ACE observation** | generator | Capture all agent executions | Others: Observed by generator |
| **ACE reflection** | reflector | Extract insights from traces | - |
| **ACE curation** | curator | Maintain evolving playbooks | user_listener invokes via UI |

### Key Principles

1. **assistant is a DOCUMENTATION EXPERT + INTELLIGENT DISPATCHER**
   - **Documentation Expert**: Has profound knowledge of ALL project docs (ROADMAP, specs, CLAUDE.md)
   - **Intelligent Dispatcher**: Routes requests to appropriate specialized agents
   - Handles quick questions directly using deep documentation knowledge
   - Delegates complex tasks to specialists based on clear decision framework
   - Does NOT compete with specialized agents
   - Think of it as "librarian + traffic controller"
   - **NEVER modifies code or docs** - Always READ-ONLY, delegates to appropriate agent
   - **Keeps ROADMAP in great detail in mind** at all times

2. **code_developer owns EXECUTION**
   - **ONLY agent that writes/modifies code**
   - All code changes in coffee_maker/, tests/, scripts/ go through code_developer
   - Creates PRs autonomously (does NOT wait for project_manager)
   - Verifies DoD during implementation
   - Updates ROADMAP status (Planned → In Progress → Complete)
   - Does NOT monitor project health (that's project_manager)
   - Does NOT make strategic ROADMAP decisions (that's project_manager)

3. **project_manager owns OVERSIGHT & DOCUMENTATION**
   - **ONLY agent that modifies docs/ directory**
   - Creates and updates technical specs (docs/PRIORITY_*_TECHNICAL_SPEC.md)
   - Manages .claude/agents/ (agent definitions)
   - Makes strategic ROADMAP decisions (priorities, planning)
   - Monitors GitHub (PRs, issues, CI)
   - Verifies completed work (post-implementation, when user requests)
   - Warns users about blockers
   - Does NOT create PRs (that's code_developer)
   - Does NOT write implementation code (that's code_developer)

4. **Specialized agents own their domain**
   - **code-searcher**: Deep codebase analysis (READ-ONLY)
     - Has PROFOUND KNOWLEDGE of entire codebase structure, dependencies, patterns
     - Performs security audits, dependency tracing, code reuse identification
     - Identifies refactoring opportunities, architectural analysis
     - **Documentation Process**: Prepares findings → Presents to assistant → assistant delegates to project_manager → project_manager writes docs
     - **NEVER writes docs directly** - Always delegates via assistant to project_manager
     - **Document Format**: docs/[analysis_type]_analysis_[date].md (e.g., docs/security_audit_2025-10-13.md)
     - See .claude/agents/code-searcher.md for complete documentation workflow
   - **ux-design-expert**: Design decisions (provides specs, doesn't implement)
   - **memory-bank-synchronizer**: Documentation sync (updates .claude/CLAUDE.md)

### When in Doubt

```
"Who should handle X?"
    ↓
Does user need a UI? → user_listener (ONLY agent with UI)
Is it a quick question? → assistant
Is it about code internals? → code-searcher
Is it about project status? → project_manager
Is it about design? → ux-design-expert
Is it implementation? → code_developer
Is it doc sync? → memory-bank-synchronizer
Is it ACE curation? → user_listener (delegates to curator)
```

### Examples

**✅ Correct Usage - Code Changes**:
```
User: "Fix the bug in roadmap_cli.py"
→ code_developer (ALL code changes)

User: "Implement feature X from PRIORITY 12"
→ code_developer (implementation)

User: "Add tests for the authentication module"
→ code_developer (test code)

User: "Update pyproject.toml to add a new dependency"
→ code_developer (configuration files)
```

**✅ Correct Usage - Documentation**:
```
User: "Create a technical spec for PRIORITY 15"
→ project_manager (owns docs/ directory)

User: "Update the ROADMAP with new priorities"
→ project_manager (strategic ROADMAP management)

User: "Add a new agent definition"
→ project_manager (owns .claude/agents/)

User: "Update CLAUDE.md with new architecture"
→ project_manager or memory-bank-synchronizer
```

**✅ Correct Usage - Delegation**:
```
User: "Where is authentication implemented?"
→ code-searcher (complex code analysis)

User: "What's our PR status?"
→ project_manager (GitHub monitoring)

User: "Design a dashboard"
→ ux-design-expert (design)

User asks assistant: "Implement feature X"
→ assistant delegates to code_developer
```

**❌ Incorrect Usage - Don't Do This**:
```
assistant tries to edit code
→ NO! code_developer owns ALL code changes

assistant tries to update ROADMAP.md
→ NO! project_manager owns docs/ directory

project_manager tries to modify coffee_maker/cli/roadmap_cli.py
→ NO! code_developer owns coffee_maker/ directory

code_developer tries to create technical specs in docs/
→ NO! project_manager owns docs/ directory

project_manager tries to create a PR
→ NO! code_developer creates PRs autonomously

code_developer tries to monitor all PRs
→ NO! project_manager monitors project health

assistant tries to make strategic ROADMAP decisions
→ NO! project_manager makes strategic decisions

code_developer tries to design UI layouts
→ NO! ux-design-expert makes design decisions
```

**🎯 Correct Delegation Flow**:
```
User to user_listener: "Fix bug in CLI and update the docs"

user_listener: "I'll coordinate this for you:
1. code_developer - Fix the bug in CLI (code changes)
2. project_manager - Update documentation (docs/ directory)

Let me delegate to the team..."

[user_listener delegates to both agents, synthesizes responses]

User to user_listener: "Show me the ACE playbook"

user_listener: "Fetching playbook from curator..."
[curator] Playbook loaded: 237 bullets, effectiveness 0.82
[user_listener] "Here's the playbook summary with categories..."
```

---

## Special Instructions for Claude

### When Implementing Features
1. **Always check ROADMAP** first: `docs/roadmap/ROADMAP.md`
2. **Look for technical specs**: `docs/PRIORITY_*_TECHNICAL_SPEC.md`
3. **Use centralized prompts**: Load from `.claude/commands/`
4. **Update status**: Use DeveloperStatus class for progress tracking
5. **Follow mixins pattern**: Don't create monolithic files

### When Creating Prompts
1. **Save to**: `.claude/commands/`
2. **Use placeholders**: `$VARIABLE_NAME` format
3. **Add to PromptNames**: In `prompt_loader.py`
4. **Document**: Add example usage in docstring

### When Testing
1. **Run unit tests**: `pytest tests/unit/`
2. **Run integration tests**: `pytest tests/ci_tests/`
3. **Check daemon**: Start daemon and verify it uses new code

### When Committing
1. **Descriptive message**: Explain what and why
2. **Include footer**: 🤖 Generated with Claude Code
3. **Co-author**: `Co-Authored-By: Claude <noreply@anthropic.com>`

---

## Multi-AI Provider Support

This project is designed to work with **multiple AI providers**:

### Current: Claude
- API mode: `ClaudeAPI` class
- CLI mode: `ClaudeCLIInterface` class
- Default: Claude CLI (uses subscription)

### Future: Gemini, OpenAI
- Prompts in `.claude/commands/` are provider-agnostic
- Just swap the provider class
- Same `PromptLoader` API works for all

**Migration Path**:
```python
# Works with ANY provider
prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {...})

# Provider-specific execution
result = provider.execute(prompt)  # Claude, Gemini, or OpenAI
```

---

## Langfuse Observability (Coming in Phase 2)

**Goal**: All prompts stored in Langfuse as source of truth

**Architecture**:
```
Langfuse (production prompts)
    ↓ sync
.claude/commands/ (local cache)
    ↓ load
PromptLoader → Agents
    ↓ track
Langfuse (execution metrics)
```

**Benefits**:
- Version control for prompts
- A/B testing of variations
- Track success rates, costs, latency
- Team collaboration on prompts

---

## Questions & Troubleshooting

### "Where are the prompts?"
→ `.claude/commands/*.md`

### "How do I add a new prompt?"
→ Create `.claude/commands/my-prompt.md`, add to `PromptNames`, use `load_prompt()`

### "How do I use Puppeteer?"
→ Use Claude Desktop with MCP configured (already done), or implement Python client (future)

### "Where's the ROADMAP?"
→ `docs/roadmap/ROADMAP.md`

### "How do I check daemon status?"
→ `poetry run project-manager developer-status`

### "Tests failing?"
→ Check pre-commit hooks: `pre-commit run --all-files`

---

## Version

**Last Updated**: 2025-10-12
**Phase**: Prompt Centralization Complete (Phase 1) ✅
**Next**: Langfuse Integration (Phase 2) 📝

---

**Remember**: This project emphasizes autonomy, observability, and multi-provider support. Keep prompts centralized, track everything, and design for flexibility! 🚀
