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
│   ├── roadmap/                     # Project planning ⭐
│   │   ├── ROADMAP.md               # Master task list
│   │   └── PRIORITY_*_STRATEGIC_SPEC.md # Strategic specs (project_manager)
│   ├── architecture/                # Technical design ⭐
│   │   ├── specs/                   # Technical specifications (architect)
│   │   ├── decisions/               # ADRs (architect)
│   │   ├── guidelines/              # Implementation guidelines (architect)
│   │   ├── pocs/                    # Proof-of-Concepts (architect) ⭐ NEW
│   │   │   ├── POC-000-template/    # Template for creating POCs
│   │   │   └── POC-{number}-{slug}/ # Individual POCs
│   │   └── POC_CREATION_GUIDE.md    # POC creation guide (architect)
│   └── PROMPT_MANAGEMENT_SYSTEM.md  # Prompt system docs
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

### Git Workflow ⭐ UPDATED (CFR-013)
- **Branch**: `roadmap` ONLY - ALL agents work on roadmap branch (CFR-013)
- **NO Feature Branches**: Agents cannot create or switch to feature/* branches
- **Commits**: Descriptive messages with 🤖 footer
- **Pre-commit**: Hooks run automatically (black, autoflake, trailing-whitespace)
- **Single Source of Truth**: All work immediately visible to entire team
- **Tags**: Use git tags to mark stable versions and milestones (see GUIDELINE-004)
  - `wip-*`: code_developer marks implementation complete, tests passing
  - `dod-verified-*`: project_manager marks DoD verified with Puppeteer
  - `milestone-*`: Major features/epics complete
  - `stable-v*.*.*`: Production-ready releases (semantic versioning)

### Dependency Management ⭐ NEW (ADR-013)
**IMPORTANT**: Three-tier dependency approval system (SPEC-070)

```python
# ❌ DON'T: code_developer cannot modify pyproject.toml directly
subprocess.run(["poetry", "add", "some-package"])

# ✅ DO: Use DependencyChecker to determine approval workflow
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

checker = DependencyChecker()
status = checker.get_approval_status("pytest-timeout")

if status == ApprovalStatus.PRE_APPROVED:
    # Auto-approve (2-5 min, NO user approval)
    subprocess.run(["poetry", "add", "pytest-timeout"])
    # Create minimal ADR (automated)

elif status == ApprovalStatus.NEEDS_REVIEW:
    # Delegate to architect for review (20-30 min)
    # architect uses dependency-conflict-resolver skill
    # User approval required

elif status == ApprovalStatus.BANNED:
    # Reject immediately with alternatives
    alternatives = checker.get_alternatives("pytest-timeout")
    print(f"Banned package. Use alternatives: {alternatives}")
```

**Three Tiers**:
1. **PRE-APPROVED** (63 packages): Auto-add, no user approval
   - Testing: pytest, pytest-cov, pytest-xdist, mypy, radon, etc. (17 packages)
   - Formatting: black, autoflake, isort, ruff, pre-commit, etc. (8 packages)
   - Observability: langfuse, opentelemetry-*, prometheus-client, etc. (6 packages)
   - Performance: cachetools, redis, hiredis, diskcache, msgpack (5 packages)
   - CLI: click, typer, rich, prompt-toolkit, etc. (7 packages)
   - Data Validation: pydantic, marshmallow, jsonschema, etc. (5 packages)
   - HTTP: requests, httpx, urllib3, aiohttp (4 packages)
   - Date/Time: python-dateutil, pytz (2 packages)
   - Config: python-dotenv, pyyaml, toml (3 packages)
   - AI/ML: anthropic, openai, tiktoken, langchain, etc. (6 packages)

2. **NEEDS REVIEW**: Requires architect evaluation + user approval (existing workflow)
   - architect uses dependency-conflict-resolver skill (15 min)
   - User approves via user_listener (5-10 min)
   - Total: 20-30 minutes

3. **BANNED**: Auto-reject with alternatives (immediate)
   - GPL-licensed: mysql-connector-python → Use pymysql or aiomysql
   - Unmaintained: nose → Use pytest
   - High-CVE packages (>5 critical vulnerabilities)

**CLI Command**:
```bash
# Check if package is pre-approved
poetry run project-manager check-dependency pytest-timeout
# → ✅ pytest-timeout is PRE-APPROVED (version: >=2.0,<3.0)
```

**Pre-Commit Hook**:
- Automatically checks pyproject.toml for unapproved dependencies
- Blocks commits with BANNED or NEEDS_REVIEW packages
- See: `.pre-commit-config.yaml` (check-dependencies hook)

**Time Savings**:
- Pre-approved: 2-5 min (vs. 20-30 min with user approval)
- Per month: 0.9-1.4 hours saved (3-5 pre-approved additions/month)
- Per year: 10.8-16.8 hours saved

**References**:
- [SPEC-070: Dependency Pre-Approval Matrix](docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md)
- [ADR-013: Dependency Pre-Approval Matrix](docs/architecture/decisions/ADR-013-dependency-pre-approval-matrix.md)

### Sound Notifications (CFR-009) ⭐ NEW
**CRITICAL**: ONLY user_listener can use sound notifications. All background agents MUST use `sound=False`.

```python
# ✅ CORRECT (code_developer, architect, project_manager, assistant - background agents)
self.notifications.create_notification(
    title="Task Complete",
    message="PRIORITY 13 implemented successfully",
    level="info",
    sound=False,  # Silent for background work
    agent_id="code_developer"
)

# ✅ CORRECT (user_listener only - UI agent)
self.notifications.create_notification(
    title="User Action Required",
    message="Please review PR #123",
    level="high",
    sound=True,  # Sound allowed for user interaction
    agent_id="user_listener"
)

# ❌ INCORRECT (background agent trying to play sound)
self.notifications.create_notification(
    title="Error Occurred",
    message="Max retries reached",
    level="error",
    sound=True,  # ❌ RAISES CFR009ViolationError!
    agent_id="code_developer"
)
```

**Why This Is Critical**:
- **User Experience**: Only UI agent (user_listener) should interrupt users with sounds
- **Background Work**: Autonomous agents work silently in the background
- **Role Clarity**: user_listener is the ONLY UI agent - only it should alert user with sound
- **Noise Prevention**: Prevents notification fatigue from multiple agents

**Enforcement**:
- `NotificationDB.create_notification()` validates `agent_id` and `sound` parameters
- Raises `CFR009ViolationError` if background agent tries `sound=True`
- Backward compatible: `agent_id=None` skips validation (legacy code)
- Comprehensive test coverage: 17 tests in `tests/unit/test_cfr009_enforcement.py`

**References**:
- [CFR-009 Documentation](docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-009-only-user_listener-uses-sound-notifications)
- [NotificationDB Implementation](coffee_maker/cli/notifications.py:303-309)
- [US-048: Enforce CFR-009](docs/roadmap/ROADMAP.md#us-048-enforce-cfr-009-silent-background-agents)

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

### 4. Git Tagging Workflow (GUIDELINE-004)

```bash
# code_developer: After completing implementation
pytest  # Ensure all tests pass
git add .
git commit -m "feat: Implement US-047 - Architect-only spec creation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git tag -a wip-us-047 -m "US-047 implementation complete, awaiting DoD

Features:
- Architect-only spec creation
- User approval workflow
- Error handling improvements

Tests: All passing (23 tests)
Status: Awaiting DoD verification"
git push origin roadmap
git push origin wip-us-047

# project_manager: After DoD verification with Puppeteer
git tag -a dod-verified-us-047 -m "US-047 DoD verified with Puppeteer testing

Verification Steps:
- Tested spec creation workflow end-to-end ✅
- Confirmed user approval process works ✅
- Verified error handling scenarios ✅

DoD Status: All criteria met
Tested By: project_manager"
git push origin dod-verified-us-047

# project_manager: After multiple priorities complete
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement

New Features:
- Architect-only spec creation (US-045, US-047) ✅
- User approval workflow (US-046) ✅
- Silent background agents (US-048) ✅

Tests: 156 passing, 0 failing
DoD: All priorities verified
Status: Production ready"
git push origin stable-v1.3.0
```

### 5. Creating a POC for Complex Implementation ⭐ NEW

**When to use**: Complex features (>16 hours + High complexity) need validation before implementation

```bash
# architect evaluates user story
# Decision: Effort = 84 hours, Complexity = HIGH (multi-process, IPC)
# → POC REQUIRED

# 1. Create POC directory from template
cd docs/architecture/pocs/
cp -r POC-000-template/ POC-055-claude-skills-integration/
cd POC-055-claude-skills-integration/

# 2. Fill in README template
# - Update header (number, name, date, time budget: 20-30% of full = 17-25h)
# - List 3-5 concepts to prove
# - Define what's NOT in scope

# 3. Implement MINIMAL working code (20-30% scope)
# - Focus ONLY on proving core concepts
# - Skip error handling edge cases
# - Use print statements for logging (OK for POC)

# 4. Write basic tests
# - One test per concept
# - Just prove it works

# 5. Run and validate
python poc_component.py  # Should work!
python test_poc.py       # All tests pass!

# 6. Document learnings in README
# - What worked well
# - What needs adjustment
# - Recommendations for code_developer

# 7. Reference POC in technical spec
# Add to SPEC-055: "See POC-055 for proof-of-concept validation"

# 8. Commit to git
git add docs/architecture/pocs/POC-055-*/
git commit -m "feat: Add POC-055 - Claude Skills Integration

Proves Code Execution Tool integration, SkillLoader, ExecutionController work correctly.

Time: 4.5 hours (22% of 20-hour minimal scope)
Scope: 25% of SPEC-055

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Decision Matrix** (see `docs/architecture/POC_CREATION_GUIDE.md`):
- Effort >16h + Complexity HIGH → **POC REQUIRED**
- Effort >16h + Complexity MEDIUM → MAYBE (ask user)
- All other cases → No POC

**Reference**: `docs/architecture/POC_CREATION_GUIDE.md` for complete guide

### 6. Architect CFR-011 Compliance (Daily Integration) ⭐ NEW

**When to use**: architect MUST follow this workflow daily and weekly to maintain CFR-011 compliance

**CRITICAL**: architect CANNOT create technical specs until compliant with CFR-011:
- Daily: Read ALL code-searcher reports
- Weekly: Analyze codebase (max 7 days between analyses)

```bash
# Daily workflow (run every day)
poetry run architect daily-integration

# Output:
# 📋 Found 2 unread code-searcher report(s):
#
#   1. CODE_QUALITY_ANALYSIS_2025-10-17.md
#   2. SECURITY_AUDIT_2025-10-18.md
#
# 📖 Please read all reports now:
# [displays each report for review]
#
# Have you read this report and extracted action items? [y/N]: y
# ✅ Marked CODE_QUALITY_ANALYSIS_2025-10-17.md as read
#
# ✅ Daily integration complete!

# Weekly workflow (run every 7 days max)
poetry run architect analyze-codebase

# Output:
# 🔍 Starting weekly codebase analysis...
#
# 📊 Analyzing codebase for:
#   - Complexity metrics (radon --average)
#   - Large files (>500 LOC)
#   - Test coverage (pytest --cov)
#   - TODO/FIXME comments
#
# (This may take 5-10 minutes...)
#
# 📄 Report saved: docs/architecture/CODEBASE_ANALYSIS_2025-10-18.md
#
# ✅ Codebase analysis complete!
#    Next analysis due: 2025-10-25

# Check compliance status anytime
poetry run architect cfr-011-status

# Output:
# 📋 CFR-011 Compliance Status
#
# ============================================================
# ✅ COMPLIANT - No violations detected
#
# Last code-searcher read: 2025-10-18
# Last codebase analysis: 2025-10-18
# Next analysis due: 2025-10-25
#
# Metrics:
#   Reports read: 12
#   Refactoring specs created: 4
#   Specs updated: 6
```

**What happens if not compliant?**

```python
# architect tries to create spec without compliance
# → CFR011ViolationError raised

CFR-011 violation detected! Cannot create spec until resolved:
  - Unread code-searcher reports: SECURITY_AUDIT_2025-10-18.md
  - Weekly codebase analysis overdue (last: 2025-10-10)

Actions required:
  1. Run: architect daily-integration
  2. Run: architect analyze-codebase
```

**Why CFR-011 matters**:
- **Quality loop**: code-searcher finds issues → architect reads → specs incorporate improvements → code_developer implements better code
- **Technical debt reduction**: Refactoring opportunities identified and acted upon
- **Continuous improvement**: Weekly codebase analysis catches issues early
- **Enforcement**: Spec creation BLOCKED until compliance restored

**Reference**: `docs/architecture/ARCHITECT_DAILY_ROUTINE_GUIDE.md` for complete guide

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

### Context Budget (CFR-007) ⭐ CRITICAL
**Agent core materials must fit in ≤30% of context window.** This ensures agents have room to work (70% remaining for files, analysis, and responses). Core materials include: agent prompt, role, responsibilities, tools, and owned critical documents. See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` CFR-007 for remediation strategies.

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

## 🚀 Running the System

### ⭐ MOST IMPORTANT: Start Autonomous Daemon

**To make code_developer work autonomously on ROADMAP priorities:**

```bash
poetry run code-developer --auto-approve
```

**What this does:**
- 🤖 **Autonomous Mode**: code_developer works continuously without manual approval
- 📋 **Implements ROADMAP**: Automatically picks next priority from `docs/roadmap/ROADMAP.md`
- 🔄 **Continuous Work**: Runs until you stop it (Ctrl+C)
- ✅ **Auto-Approve**: Makes implementation decisions automatically
- 🌿 **CFR-013 Compliant**: All work happens on `roadmap` branch only

**Monitor progress:**
```bash
# Check what code_developer is working on
poetry run project-manager developer-status

# View recent notifications
poetry run project-manager notifications

# Check ROADMAP status
poetry run project-manager /roadmap
```

**Stop the daemon:**
- Press `Ctrl+C` in the terminal where it's running
- The daemon will clean up and exit gracefully

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
| **docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md** | project_manager | YES - Creates strategic specs | All others: READ-ONLY |
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
   - **Bug Reporter**: Tests features, detects bugs, provides comprehensive analysis to project_manager
   - **Bug Report Content**: When bugs found, assistant provides:
     - Root cause analysis (what went wrong technically)
     - Requirements for fix (specific changes needed)
     - Expected behavior once corrected (how it should work)
     - Complete reproduction steps, environment details, impact assessment
     - This enables architect and code_developer to fix the problem before assistant retries demo
   - Handles quick questions directly using deep documentation knowledge
   - Delegates complex tasks to specialists based on clear decision framework
   - Does NOT compete with specialized agents
   - Think of it as "librarian + traffic controller + demo producer + comprehensive QA reporter"
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
   - Creates and updates strategic specs (docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md)
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
   - **⭐ NEW (US-049, CFR-010)**: Continuously reviews and improves all specs
     - **Daily quick reviews** (5-10 min): Scan ROADMAP for simplification opportunities
     - **Weekly deep reviews** (1-2 hours): Read ALL specs, identify reuse patterns
     - **Automated triggers**: Daemon detects when reviews needed, creates notifications
     - **Metrics tracking**: Records simplifications, reuse, effort saved
     - **Weekly reports**: Generates improvement reports in `docs/architecture/WEEKLY_SPEC_REVIEW_*.md`
     - **Success**: 30-87% complexity reduction typical (e.g., SPEC-009: 80h → 16h = 80% reduction)
     - See [GUIDELINE-006: Architect Review Process](docs/architecture/guidelines/GUIDELINE-006-architect-review-process.md)
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
→ assistant analyzes bug COMPREHENSIVELY:
   - Root cause analysis (technical explanation)
   - Requirements for fix (specific changes needed)
   - Expected behavior once corrected (how it should work)
   - Complete reproduction steps, environment, impact
→ assistant reports COMPREHENSIVE analysis to project_manager
→ project_manager adds critical priority to ROADMAP with full details
→ architect designs fix based on assistant's analysis
→ code_developer implements fix using architect's design + assistant's requirements
→ assistant retries demo to verify fix works

User to user_listener: "Test the registration flow"
→ user_listener delegates to assistant
→ assistant tests with Puppeteer
→ If bugs found: assistant provides comprehensive bug report to project_manager
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

assistant provides BRIEF bug report without analysis
→ NO! assistant must provide COMPREHENSIVE report with:
   - Root cause analysis
   - Requirements for fix
   - Expected behavior once corrected
   - Complete details for architect/code_developer

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
1. **Always check ROADMAP** first: `docs/roadmap/ROADMAP.md`
2. **Look for strategic specs**: `docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md`
3. **Look for technical specs**: `docs/architecture/specs/SPEC-*-*.md`
4. **Use centralized prompts**: Load from `.claude/commands/`
5. **Update status**: Use DeveloperStatus class for progress tracking
6. **Follow mixins pattern**: Don't create monolithic files

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
4. **Tag appropriately**: Use git tags for significant milestones (see GUIDELINE-004)
   - code_developer: Create `wip-*` tags after tests pass
   - project_manager: Create `dod-verified-*` after Puppeteer verification
   - project_manager: Create `stable-v*.*.*` for production releases

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
