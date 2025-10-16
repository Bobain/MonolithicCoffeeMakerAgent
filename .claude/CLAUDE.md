# MonolithicCoffeeMakerAgent - Claude Instructions

## Project Overview

**MonolithicCoffeeMakerAgent** is an autonomous software development system featuring multiple AI agents that work together to implement features, manage projects, and provide assistance.

**Key Philosophy**: Autonomous, observable, multi-AI provider support

---

## Architecture

### Core Components

1. **Autonomous Agents**
   - `user_listener`: **PRIMARY USER INTERFACE** - Interprets user intent and delegates to team (ONLY agent with UI)
   - `architect`: Architectural design and technical specifications (interacts through user_listener)
   - `code_developer`: Autonomous implementation of priorities from ROADMAP
   - `project_manager`: Project coordination, notifications, status tracking, GitHub monitoring (backend only)
   - `assistant`: Documentation expert, intelligent dispatcher, demo creator, and bug reporter
   - `code-searcher`: Deep codebase analysis and forensic examination
   - `ux-design-expert`: UI/UX design guidance and Tailwind CSS

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
│   ├── ROADMAP.md                   # Master task list
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
- **Singletons**: Critical resources use singleton pattern (AgentRegistry, HTTPConnectionPool, GlobalRateTracker)
- **Observability**: Use Langfuse decorators for tracking
- **Error Handling**: Defensive programming, validate inputs, handle None gracefully

### Singleton Pattern (US-035) ⭐ NEW
**CRITICAL**: Only ONE instance of each agent type can run at a time.

```python
# ✅ RECOMMENDED: Use context manager for automatic cleanup
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    # Agent work here
    # Automatically unregistered on exit, even if exception occurs
    pass

# ✅ ALTERNATIVE: Manual registration
registry = AgentRegistry()
try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
    # ... do work ...
finally:
    registry.unregister_agent(AgentType.CODE_DEVELOPER)

# ❌ DON'T: Try to run multiple instances of same agent
# This will raise AgentAlreadyRunningError:
# "Agent 'code_developer' is already running! PID: 12345"
```

**Why Singleton Enforcement?**
- Prevents file corruption from concurrent writes
- Eliminates race conditions in daemon operations
- Avoids duplicate work execution
- Prevents resource conflicts

**Pattern Details**:
- `__new__` method ensures single registry instance
- Thread-safe locking with `threading.Lock`
- Context manager for automatic cleanup
- Clear error messages with PID and timestamp

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
cat docs/ROADMAP.md

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
| **docs/*.md** | project_manager | YES - Top-level files ONLY (not subdirectories) | All others: READ-ONLY |
| **docs/roadmap/** | project_manager | YES - Strategic planning ONLY | All others: READ-ONLY |
| **docs/architecture/** | architect | YES - Technical specs, ADRs, guidelines | All others: READ-ONLY |
| **docs/architecture/specs/** | architect | YES - Technical specifications | All others: READ-ONLY |
| **docs/architecture/decisions/** | architect | YES - ADRs (Architectural Decision Records) | All others: READ-ONLY |
| **docs/architecture/guidelines/** | architect | YES - Implementation guidelines | All others: READ-ONLY |
| **docs/PRIORITY_*_TECHNICAL_SPEC.md** | project_manager | YES - Creates strategic specs | All others: READ-ONLY |
| **docs/generator/** | generator | YES - Execution traces | All others: READ-ONLY |
| **docs/reflector/** | reflector | YES - Delta items (insights) | All others: READ-ONLY |
| **docs/curator/** | curator | YES - Playbooks and curation | All others: READ-ONLY |
| **docs/code-searcher/** | project_manager | YES - Code analysis documentation | code-searcher: Prepares findings (READ-ONLY) |
| **docs/templates/** | project_manager | YES - Documentation templates | All others: READ-ONLY |
| **docs/tutorials/** | project_manager | YES - Tutorial content | All others: READ-ONLY |
| **docs/user_interpret/** | project_manager | YES - Meta-docs about user_interpret | All others: READ-ONLY |
| **docs/code_developer/** | project_manager | YES - Meta-docs about code_developer | All others: READ-ONLY |
| **pyproject.toml** | architect | YES - Dependency management (requires user approval) | All others: READ-ONLY |
| **poetry.lock** | architect | YES - Dependency lock file | All others: READ-ONLY |
| **.claude/** | code_developer | YES - Technical configurations | All others: READ-ONLY |
| **.claude/agents/** | code_developer | YES - Agent configurations | All others: READ-ONLY |
| **coffee_maker/** | code_developer | YES - All implementation | All others: READ-ONLY |
| **tests/** | code_developer | YES - All test code | All others: READ-ONLY |
| **scripts/** | code_developer | YES - Utility scripts | All others: READ-ONLY |
| **.pre-commit-config.yaml** | code_developer | YES - Pre-commit hooks | All others: READ-ONLY |
| **data/user_interpret/** | user_interpret | YES - Operational data (conversation logs, etc.) | All others: READ-ONLY |

### Tool Ownership Matrix

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **User Interface (ALL)** | user_listener | **ONLY** agent with UI, chat, CLI interface | All others: Backend only, NO UI |
| **Architecture specs** | architect | Creates technical specifications before implementation | code_developer reads and implements |
| **ADRs (Architectural Decision Records)** | architect | Documents architectural decisions | All others: READ-ONLY |
| **Implementation guidelines** | architect | Provides detailed implementation guides | code_developer follows during implementation |
| **Dependency management** | architect | ONLY agent that can run `poetry add` (requires user approval) | code_developer: CANNOT modify dependencies |
| **User approval requests** | architect | Proactively asks user for approval on important decisions | user_listener presents to user |
| **Puppeteer DoD (during impl)** | code_developer | Verify features DURING implementation | project_manager for POST-completion verification |
| **Puppeteer DoD (post-impl)** | project_manager | Verify completed work on user request | - |
| **Puppeteer demos & testing** | assistant | Create visual demos, test features, report bugs | user_listener delegates demo requests to assistant |
| **Bug reporting from demos** | assistant | Analyze bugs found during demos → report to project_manager | project_manager adds critical priorities to ROADMAP |
| **GitHub PR create** | code_developer | Create PRs autonomously | - |
| **GitHub monitoring** | project_manager | Monitor PRs, issues, CI/CD status | - |
| **GitHub queries** | project_manager | All `gh` commands | user_listener delegates via UI |
| **Code editing** | code_developer | ALL code changes | assistant READ-ONLY |
| **Code search (simple)** | assistant | 1-2 files with Grep/Read | user_listener delegates via UI |
| **Code search (complex)** | code-searcher | Deep analysis, patterns, forensics | user_listener delegates via UI |
| **Code analysis docs** | project_manager | Creates docs/[analysis]_[date].md | code-searcher prepares findings, user_listener delegates |
| **ROADMAP updates** | project_manager (full), code_developer (status only) | Strategic vs. execution updates | assistant READ-ONLY |
| **Design decisions** | ux-design-expert | All UI/UX, Tailwind, charts | user_listener delegates via UI |
| **ACE observation** | generator | Capture all agent executions | Others: Observed by generator |
| **ACE reflection** | reflector | Extract insights from traces | - |
| **ACE curation** | curator | Maintain evolving playbooks | user_listener invokes via UI |

### Key Principles

1. **assistant is a DOCUMENTATION EXPERT + INTELLIGENT DISPATCHER + DEMO CREATOR + BUG REPORTER**
   - **Documentation Expert**: Has profound knowledge of ALL project docs (ROADMAP, specs, CLAUDE.md)
   - **Intelligent Dispatcher**: Routes requests to appropriate specialized agents
   - **Demo Creator**: Creates visual demos using Puppeteer MCP to showcase features (ONLY agent that creates demos)
   - **Bug Reporter**: Tests features, detects bugs, analyzes them, and reports to project_manager
   - Handles quick questions directly using deep documentation knowledge
   - Delegates complex tasks to specialists based on clear decision framework
   - Does NOT compete with specialized agents
   - Think of it as "librarian + traffic controller + demo producer + QA reporter"
   - **NEVER modifies code or strategic docs** - Always READ-ONLY for code/docs, but ACTIVE for demos and bug reports
   - **Keeps ROADMAP in great detail in mind** at all times

2. **code_developer owns EXECUTION & TECHNICAL CONFIGURATION**
   - **ONLY agent that writes/modifies code and .claude/ configurations**
   - All code changes in coffee_maker/, tests/, scripts/ go through code_developer
   - All technical configuration changes in .claude/ go through code_developer
   - Creates PRs autonomously (does NOT wait for project_manager)
   - Verifies DoD during implementation
   - Updates ROADMAP status (Planned → In Progress → Complete)
   - Manages agent configurations (.claude/agents/), prompts (.claude/commands/), MCP (.claude/mcp/)
   - Updates .claude/CLAUDE.md (technical setup and implementation guide)
   - Does NOT monitor project health (that's project_manager)
   - Does NOT make strategic ROADMAP decisions (that's project_manager)
   - Does NOT create strategic documentation in docs/ (that's project_manager)

3. **project_manager owns STRATEGIC DOCUMENTATION**
   - **ONLY agent that modifies docs/roadmap/ directory**
   - Creates and updates strategic specs (docs/PRIORITY_*_TECHNICAL_SPEC.md)
   - Makes strategic ROADMAP decisions (priorities, planning)
   - Monitors GitHub (PRs, issues, CI)
   - Verifies completed work (post-implementation, when user requests)
   - Warns users about blockers
   - Does NOT create PRs (that's code_developer)
   - Does NOT write implementation code (that's code_developer)
   - Does NOT modify .claude/ (that's code_developer)
   - Does NOT modify docs/architecture/ (that's architect)
   - Does NOT modify pyproject.toml (that's architect)

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

5. **architect owns ARCHITECTURAL DESIGN & DEPENDENCIES**
   - **ONLY agent that creates architectural specifications**
   - **ONLY agent that manages dependencies (pyproject.toml, poetry.lock)**
   - Designs system architecture BEFORE code_developer implements
   - Creates technical specifications in docs/architecture/specs/
   - Documents architectural decisions (ADRs) in docs/architecture/decisions/
   - Provides implementation guidelines in docs/architecture/guidelines/
   - **Proactive**: Asks user for approval on important decisions (especially dependencies)
   - **Dependency management**: ONLY architect can run `poetry add` (requires user consent)
   - Interacts with user through user_listener for architectural discussions
   - Does NOT implement code (that's code_developer)
   - Does NOT create strategic roadmap docs (that's project_manager)
   - Does NOT modify coffee_maker/ (that's code_developer)

### When in Doubt

```
"Who should handle X?"
    ↓
Does user need a UI? → user_listener (ONLY agent with UI)
Is it architectural design? → architect
Is it a quick question? → assistant
Is it a demo creation? → assistant (ONLY agent that creates demos)
Is it a bug found in demo? → assistant analyzes → reports to project_manager
Is it about code internals? → code-searcher
Is it about project status? → project_manager
Is it about design? → ux-design-expert
Is it implementation? → code_developer
```

### Examples

**✅ Correct Usage - Demo Creation & Bug Reporting**:
```
User to user_listener: "Show me how the dashboard works"
→ user_listener delegates to assistant
→ assistant creates visual demo with Puppeteer

code_developer: "Feature X is complete"
→ user_listener asks assistant to create demo
→ assistant creates demo to showcase feature

assistant (during demo): Detects bug in feature
→ assistant analyzes bug thoroughly
→ assistant reports to project_manager with analysis
→ project_manager adds critical priority to ROADMAP

User to user_listener: "Test the registration flow"
→ user_listener delegates to assistant
→ assistant tests with Puppeteer
→ If bugs found: assistant reports to project_manager
```

**✅ Correct Usage - Other Tasks**:
```
User: "Where is authentication implemented?"
→ code-searcher (complex code analysis)

User: "What's our PR status?"
→ project_manager (GitHub monitoring)

User: "Design a dashboard"
→ ux-design-expert (design)

User: "Implement feature X"
→ code_developer (implementation)
```

**❌ Incorrect Usage**:
```
project_manager tries to create demos
→ NO! assistant is ONLY agent that creates demos

user_listener tries to create demos directly
→ NO! user_listener delegates to assistant

assistant tries to verify DoD post-completion
→ NO! Use project_manager for post-completion verification

assistant tries to add bugs to ROADMAP directly
→ NO! assistant reports to project_manager, who adds to ROADMAP

project_manager tries to create a PR
→ NO! code_developer creates PRs

assistant tries to edit code to fix bugs
→ NO! code_developer owns all code changes

code_developer tries to monitor all PRs
→ NO! project_manager monitors project health
```

---

## Special Instructions for Claude

### When Implementing Features
1. **Always check ROADMAP** first: `docs/ROADMAP.md`
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
→ `docs/ROADMAP.md`

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
