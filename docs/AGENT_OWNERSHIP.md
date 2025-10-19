# Agent Tool Ownership & Boundaries

**IMPORTANT**: Each agent has specific tool ownership to prevent overlap and confusion.

---

## File & Directory Ownership Matrix

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
| **docs/code-reviews/** | code-reviewer | YES - Code review reports | architect: Reads frequently via skill, All others: READ-ONLY |
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

---

## Tool Ownership Matrix

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

---

## Key Principles

### 1. assistant is a DOCUMENTATION EXPERT + INTELLIGENT DISPATCHER + DEMO CREATOR + BUG REPORTER

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

### 2. code_developer owns EXECUTION & TECHNICAL CONFIGURATION

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

### 3. project_manager owns STRATEGIC DOCUMENTATION

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

### 4. Specialized agents own their domain

**code-searcher**: Deep codebase analysis (READ-ONLY)
- Has PROFOUND KNOWLEDGE of entire codebase structure, dependencies, patterns
- Performs security audits, dependency tracing, code reuse identification
- Identifies refactoring opportunities, architectural analysis
- **Documentation Process**: Prepares findings → Presents to assistant → assistant delegates to project_manager → project_manager writes docs
- **NEVER writes docs directly** - Always delegates via assistant to project_manager
- **Document Format**: docs/[analysis_type]_analysis_[date].md (e.g., docs/security_audit_2025-10-13.md)
- See .claude/agents/code-searcher.md for complete documentation workflow

**ux-design-expert**: Design decisions (provides specs, doesn't implement)

### 5. architect owns ARCHITECTURAL DESIGN & DEPENDENCIES

- **ONLY agent that creates architectural specifications**
- **ONLY agent that manages dependencies (pyproject.toml, poetry.lock)**
- Designs system architecture BEFORE code_developer implements
- Creates technical specifications in docs/architecture/specs/
- Documents architectural decisions (ADRs) in docs/architecture/decisions/
- Provides implementation guidelines in docs/architecture/guidelines/
- **Proactive**: Asks user for approval on important decisions (especially dependencies)
- **Dependency management**: ONLY architect can run `poetry add` (requires user consent)
- **Continuous Improvement (US-049, CFR-010)**: Reviews and improves all specs
  - **Daily quick reviews** (5-10 min): Scan ROADMAP for simplification opportunities
  - **Daily code-review checks** (2-3 min): Use code-review-history skill to review recent reports
  - **Weekly deep reviews** (1-2 hours): Read ALL specs, identify reuse patterns
  - **Weekly trend analysis** (5-10 min): Use code-review-history skill for quality trends
  - **Automated triggers**: Daemon detects when reviews needed, creates notifications
  - **Metrics tracking**: Records simplifications, reuse, effort saved
  - **Weekly reports**: Generates improvement reports in `docs/architecture/WEEKLY_SPEC_REVIEW_*.md`
  - **Refactoring insights**: Uses code-review-history skill to inform refactoring plans
  - **Success**: 30-87% complexity reduction typical (e.g., SPEC-009: 80h → 16h = 80% reduction)
  - See [GUIDELINE-006: Architect Review Process](architecture/guidelines/GUIDELINE-006-architect-review-process.md)
- Interacts with user through user_listener for architectural discussions
- Does NOT implement code (that's code_developer)
- Does NOT create strategic roadmap docs (that's project_manager)
- Does NOT modify coffee_maker/ (that's code_developer)

---

## Decision Framework

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

---

## Examples

### ✅ Correct Usage - Demo Creation & Bug Reporting

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

### ✅ Correct Usage - Other Tasks

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

### ❌ Incorrect Usage

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
