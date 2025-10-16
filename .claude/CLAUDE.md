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
   - `assistant`: Documentation expert and intelligent dispatcher
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

### Tool Ownership Matrix

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **Puppeteer DoD (during impl)** | code_developer | Verify features DURING implementation | project_manager for POST-completion verification |
| **Puppeteer DoD (post-impl)** | project_manager | Verify completed work on user request | - |
| **Puppeteer demos** | assistant | Show features visually (demos only) | NOT for verification |
| **GitHub PR create** | code_developer | Create PRs autonomously | - |
| **GitHub monitoring** | project_manager | Monitor PRs, issues, CI/CD status | - |
| **GitHub queries** | project_manager | All `gh` commands | assistant delegates |
| **Code editing** | code_developer | ALL code changes | assistant READ-ONLY |
| **Code search (simple)** | assistant | 1-2 files with Grep/Read | Delegate complex to code-searcher |
| **Code search (complex)** | code-searcher | Deep analysis, patterns, forensics | - |
| **ROADMAP updates** | project_manager (full), code_developer (status only) | Strategic vs. execution updates | assistant READ-ONLY |
| **Design decisions** | ux-design-expert | All UI/UX, Tailwind, charts | Others delegate |

### Key Principles

1. **assistant is a TRIAGE agent**
   - Handles quick questions directly
   - Delegates complex tasks to specialists
   - Does NOT compete with specialized agents
   - Think of it as "first-line support"

2. **code_developer owns EXECUTION**
   - All code changes go through code_developer
   - Creates PRs autonomously
   - Verifies DoD during implementation
   - Does NOT monitor project health (that's project_manager)

3. **project_manager owns OVERSIGHT**
   - Monitors GitHub (PRs, issues, CI)
   - Verifies completed work (post-implementation)
   - Makes strategic ROADMAP decisions
   - Warns users about blockers
   - Does NOT create PRs (that's code_developer)

4. **Specialized agents own their domain**
   - code-searcher: Code analysis
   - ux-design-expert: Design
   - architect: Technical specifications and dependency management

### When in Doubt

```
"Who should handle X?"
    ↓
Does user need a UI? → user_listener (ONLY agent with UI)
Is it architectural design? → architect
Is it a quick question? → assistant
Is it about code internals? → code-searcher
Is it about project status? → project_manager
Is it about design? → ux-design-expert
Is it implementation? → code_developer
```

### Examples

**✅ Correct Usage**:
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
assistant tries to verify DoD with Puppeteer
→ NO! Use project_manager for verification

project_manager tries to create a PR
→ NO! code_developer creates PRs

assistant tries to edit code
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
