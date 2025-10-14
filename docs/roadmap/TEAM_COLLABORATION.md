# Team Collaboration Guide

Visual guide to agent interactions, ownership, and workflows in the MonolithicCoffeeMakerAgent system.

## Table of Contents
- [Agent Overview](#agent-overview)
- [Request Flow Diagrams](#request-flow-diagrams)
- [Ownership Matrix](#ownership-matrix)
- [Decision Tree: Which Agent?](#decision-tree-which-agent)
- [Common Workflows](#common-workflows)
- [Examples](#examples)

---

## Agent Overview

The MonolithicCoffeeMakerAgent system consists of specialized AI agents, each with distinct responsibilities:

```
┌────────────────────────────────────────────────────────────────┐
│                  MonolithicCoffeeMakerAgent                    │
└────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │   assistant   │  │code_developer│ │project_mgr  │
    │ (Dispatcher)  │  │ (Execution)  │  │(Oversight)  │
    └───────┬───────┘  └──────────────┘  └──────┬──────┘
            │                                     │
    ┌───────┴────────────────────────────────────┴──────┐
    │                                                    │
┌───▼────────┐  ┌──────────────┐  ┌──────────────┐  ┌──▼───────┐
│code-       │  │ux-design-    │  │memory-bank-  │  │ACE       │
│searcher    │  │expert        │  │synchronizer  │  │Framework │
│(Analysis)  │  │(Design)      │  │(Doc Sync)    │  │(Learning)│
└────────────┘  └──────────────┘  └──────────────┘  └──────────┘
```

### Core Agents

**assistant** - Documentation Expert + Intelligent Dispatcher
- Role: Routes requests to appropriate agents
- Knowledge: Deep understanding of ALL project documentation
- Approach: Handles quick questions, delegates complex tasks
- Motto: "Librarian + Traffic Controller"

**code_developer** - Autonomous Implementation
- Role: Executes all code changes
- Scope: coffee_maker/, tests/, scripts/, pyproject.toml
- Authority: Creates PRs autonomously, updates ROADMAP status
- Motto: "I write the code, not the docs"

**project_manager** - Strategic Oversight
- Role: Project coordination and documentation
- Scope: docs/, .claude/agents/, .claude/commands/
- Authority: Strategic ROADMAP decisions, technical specs, GitHub monitoring
- Motto: "Plan, coordinate, verify"

### Specialized Agents

**code-searcher** - Deep Codebase Analysis
- Role: Security audits, dependency tracing, pattern analysis
- Access: READ-ONLY entire codebase
- Output: Findings presented to assistant → delegated to project_manager for docs
- Motto: "I find it, you document it"

**ux-design-expert** - UI/UX Design
- Role: Design decisions, Tailwind CSS, charts
- Output: Design specifications (does not implement)
- Motto: "Form follows function"

**memory-bank-synchronizer** - Documentation Sync
- Role: Keep CLAUDE.md files current with code reality
- Scope: .claude/CLAUDE.md updates
- Motto: "Docs reflect reality"

**ACE Framework** - Continuous Learning
- generator: Captures execution traces
- reflector: Extracts insights
- curator: Maintains evolving playbooks
- Motto: "Learn, adapt, improve"

---

## Request Flow Diagrams

### Basic User Request Flow

```
User Request
     │
     ▼
┌─────────────┐
│  assistant  │ ◄── Has profound knowledge of:
└──────┬──────┘     • docs/roadmap/ROADMAP.md
       │            • docs/PRIORITY_*_TECHNICAL_SPEC.md
       │            • .claude/CLAUDE.md
       │            • All project documentation
       │
       ├──── Quick question? ──► Answer directly
       │
       └──── Complex task? ───► Delegate to specialist
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
            ┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐
            │code_developer │  │project_mgr  │  │code-searcher│
            │               │  │             │  │   /other    │
            └───────────────┘  └─────────────┘  └─────────────┘
```

### Code Change Request Flow

```
User: "Fix bug in roadmap_cli.py"
     │
     ▼
┌─────────────┐
│  assistant  │  READ ONLY - Never modifies code
└──────┬──────┘
       │
       │ Recognizes: Code change → Delegate
       │
       ▼
┌──────────────┐
│code_developer│ ◄── ONLY agent that writes/modifies code
└──────┬───────┘
       │
       ├──► Read code
       ├──► Analyze bug
       ├──► Fix code
       ├──► Run tests
       ├──► Update ROADMAP status (if priority-related)
       ├──► Git commit
       └──► Create PR autonomously
```

### Documentation Request Flow

```
User: "Create technical spec for PRIORITY 15"
     │
     ▼
┌─────────────┐
│  assistant  │  READ ONLY - Never modifies docs
└──────┬──────┘
       │
       │ Recognizes: Documentation → Delegate
       │
       ▼
┌──────────────┐
│project_mgr   │ ◄── ONLY agent that modifies docs/ directory
└──────┬───────┘
       │
       ├──► Read ROADMAP (docs/roadmap/ROADMAP.md)
       ├──► Understand PRIORITY 15 requirements
       ├──► Create docs/PRIORITY_15_TECHNICAL_SPEC.md
       ├──► Update docs/roadmap/ROADMAP.md with spec reference
       └──► Git commit
```

### Complex Analysis Flow

```
User: "Find all places where authentication is implemented"
     │
     ▼
┌─────────────┐
│  assistant  │  Can handle 1-2 file searches
└──────┬──────┘
       │
       │ Recognizes: Complex search → Delegate
       │
       ▼
┌──────────────┐
│code-searcher │ ◄── Deep analysis, multiple files
└──────┬───────┘     READ-ONLY access
       │
       ├──► Grep entire codebase
       ├──► Trace dependencies
       ├──► Identify patterns
       ├──► Analyze architecture
       │
       ▼
┌──────────────┐
│code-searcher │ Prepares findings
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  assistant  │ Reviews findings
└──────┬──────┘
       │
       │ Should document? Yes
       │
       ▼
┌──────────────┐
│project_mgr   │ Creates docs/authentication_analysis_2025-10-14.md
└──────────────┘
```

### DoD Verification Flow (Post-Implementation)

```
User: "Is the analytics dashboard complete?"
     │
     ▼
┌─────────────┐
│  assistant  │
└──────┬──────┘
       │
       │ Recognizes: DoD verification → Delegate
       │
       ▼
┌──────────────┐
│project_mgr   │ ◄── Post-completion verification
└──────┬───────┘
       │
       ├──► Check ROADMAP status
       ├──► Use Puppeteer MCP:
       │    • Navigate to http://localhost:8501
       │    • Take screenshots
       │    • Test features
       │    • Check console errors
       │
       ▼
┌──────────────┐
│project_mgr   │ Reports findings:
└──────────────┘ ✅ Verified complete with evidence
                 ❌ Issues found, needs attention
```

### GitHub Monitoring Flow

```
User: "What's the status of our PRs?"
     │
     ▼
┌─────────────┐
│  assistant  │
└──────┬──────┘
       │
       │ Recognizes: GitHub query → Delegate
       │
       ▼
┌──────────────┐
│project_mgr   │ ◄── All gh commands
└──────┬───────┘
       │
       ├──► gh pr list
       ├──► gh pr checks <pr-number>
       ├──► gh issue list
       ├──► Analyze results
       │
       ▼
Report: "PR #5 ready to merge, PR #4 tests failing"
```

---

## Ownership Matrix

### File and Directory Ownership

| Path | Owner | Permissions | Others |
|------|-------|-------------|--------|
| **docs/** | project_manager | Full control | READ-ONLY |
| **docs/roadmap/** | project_manager | Full control | READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | project_manager: Full, code_developer: Status only | READ-ONLY |
| **docs/PRIORITY_*_TECHNICAL_SPEC.md** | project_manager | Creates/updates specs | READ-ONLY |
| **.claude/CLAUDE.md** | project_manager, memory-bank-synchronizer | Strategic updates | READ-ONLY |
| **.claude/agents/** | project_manager | Agent definitions | READ-ONLY |
| **.claude/commands/** | project_manager | Prompt management | READ-ONLY (load only) |
| **coffee_maker/** | code_developer | All implementation | READ-ONLY |
| **tests/** | code_developer | All test code | READ-ONLY |
| **scripts/** | code_developer | Utility scripts | READ-ONLY |
| **pyproject.toml** | code_developer | Dependencies | READ-ONLY |

### Tool Ownership

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **Code Editing** | code_developer | ALL code changes | None |
| **Doc Editing** | project_manager | ALL docs/ changes | None |
| **Puppeteer DoD (during impl)** | code_developer | Verify DURING implementation | - |
| **Puppeteer DoD (post-impl)** | project_manager | Verify AFTER completion | - |
| **Puppeteer Demos** | assistant | Show features visually | Not for verification |
| **GitHub PR Create** | code_developer | Autonomous PR creation | - |
| **GitHub Monitoring** | project_manager | Monitor PRs, issues, CI | - |
| **Code Search (simple)** | assistant | 1-2 files | - |
| **Code Search (complex)** | code-searcher | Deep analysis | - |
| **ROADMAP Updates (strategy)** | project_manager | Priorities, planning | - |
| **ROADMAP Updates (status)** | code_developer | Status tracking | - |
| **Design Decisions** | ux-design-expert | UI/UX, Tailwind | - |
| **Doc Sync** | memory-bank-synchronizer | CLAUDE.md updates | - |
| **ACE Observation** | generator | Capture traces | - |
| **ACE Reflection** | reflector | Extract insights | - |
| **ACE Curation** | curator | Maintain playbooks | - |

---

## Decision Tree: Which Agent?

```
                    ┌───────────────┐
                    │ User Request  │
                    └───────┬───────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
        Quick                           Complex
        question?                       task?
            │                               │
            ▼                               │
    ┌───────────────┐                      │
    │   assistant   │                      │
    │ (answers now) │                      │
    └───────────────┘                      │
                                            │
                    ┌───────────────────────┘
                    │
        ┌───────────┴────────────┐
        │ What type of request?  │
        └───────────┬────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    │               │               │
    ▼               ▼               ▼
┌────────┐    ┌──────────┐    ┌──────────┐
│  Code  │    │   Docs   │    │ Analysis │
│changes?│    │ changes? │    │  search? │
└───┬────┘    └────┬─────┘    └────┬─────┘
    │              │               │
    ▼              ▼               ▼
┌────────┐    ┌──────────┐    ┌──────────┐
│  code_ │    │project_  │    │1-2 files?│
│develop │    │  mgr     │    └────┬─────┘
└────────┘    └──────────┘         │
                              ┌────┴────┐
                              │         │
                             Yes       No
                              │         │
                              ▼         ▼
                        ┌──────────┐ ┌──────────┐
                        │assistant │ │  code-   │
                        │(Grep/    │ │ searcher │
                        │ Read)    │ │          │
                        └──────────┘ └──────────┘

    ┌───────────────┬───────────────┬───────────────┐
    │               │               │               │
    ▼               ▼               ▼               ▼
┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Design │    │  GitHub  │    │   DoD    │    │Doc sync? │
│decision?│    │ query?   │    │  verify? │    │          │
└───┬────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
    │              │               │               │
    ▼              ▼               ▼               ▼
┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ ux-    │    │project_  │    │During:   │    │memory-   │
│design- │    │  mgr     │    │code_dev  │    │  bank-   │
│expert  │    │(gh CLI)  │    │After:    │    │sync      │
└────────┘    └──────────┘    │proj_mgr  │    └──────────┘
                               └──────────┘
```

### Quick Reference

**Code changes?** → code_developer
- Anything in coffee_maker/, tests/, scripts/
- Bug fixes, feature implementation
- Test writing, dependency updates

**Documentation?** → project_manager
- Anything in docs/ directory
- Technical specs, ROADMAP updates
- Agent definitions, prompt management

**Simple search?** → assistant
- Finding 1-2 files
- Quick Grep/Read operations

**Complex analysis?** → code-searcher
- Multiple files, patterns
- Security audits, dependency tracing
- Architecture analysis

**Design decisions?** → ux-design-expert
- UI/UX layout
- Tailwind CSS
- Chart design

**GitHub queries?** → project_manager
- PR status, issue tracking
- CI/CD monitoring

**DoD verification?**
- During implementation → code_developer
- Post-completion → project_manager

**Doc sync?** → memory-bank-synchronizer
- Keep CLAUDE.md current

---

## Common Workflows

### Workflow 1: Implement New Feature

```
1. User: "Implement PRIORITY 12: Email Notifications"
        │
        ▼
2. assistant analyzes:
   - Reads docs/roadmap/ROADMAP.md
   - Checks PRIORITY 12 details
   - Sees technical spec exists: docs/PRIORITY_12_TECHNICAL_SPEC.md
   - Determines: Code implementation task
        │
        ▼
3. assistant delegates to code_developer:
   "Please implement PRIORITY 12 per the technical spec"
        │
        ▼
4. code_developer:
   ├─► Read docs/PRIORITY_12_TECHNICAL_SPEC.md
   ├─► Update ROADMAP: Planned → In Progress
   ├─► Implement in coffee_maker/notifications/email.py
   ├─► Write tests in tests/notifications/test_email.py
   ├─► Run tests: pytest
   ├─► Use Puppeteer to verify DoD
   ├─► Update ROADMAP: In Progress → Complete
   ├─► Git commit with descriptive message
   └─► Create PR autonomously
        │
        ▼
5. code_developer reports: "PRIORITY 12 complete, PR #42 created"
```

### Workflow 2: Create Technical Spec

```
1. User: "Create spec for PRIORITY 15: Dashboard Redesign"
        │
        ▼
2. assistant:
   - Reads docs/roadmap/ROADMAP.md
   - Checks PRIORITY 15 details
   - Determines: Documentation task
   - May need design input
        │
        ▼
3. assistant checks if design input needed:
   "Should I involve ux-design-expert for design recommendations?"
        │
        ├─► If Yes:
        │   ├─► Delegate to ux-design-expert
        │   └─► Get design specs
        │
        ▼
4. assistant delegates to project_manager:
   "Create technical spec for PRIORITY 15"
   [Includes design specs if applicable]
        │
        ▼
5. project_manager:
   ├─► Read docs/roadmap/ROADMAP.md PRIORITY 15
   ├─► Incorporate design specs (if provided)
   ├─► Create docs/PRIORITY_15_TECHNICAL_SPEC.md
   ├─► Update docs/roadmap/ROADMAP.md with spec reference
   └─► Git commit
        │
        ▼
6. project_manager reports: "Spec created at docs/PRIORITY_15_TECHNICAL_SPEC.md"
```

### Workflow 3: Investigate Bug

```
1. User: "Why is the CLI crashing on startup?"
        │
        ▼
2. assistant:
   - Simple investigation? Try quick analysis
   - Complex? Delegate to code-searcher
        │
        ▼
3. code-searcher (for complex issues):
   ├─► Grep for crash patterns
   ├─► Trace CLI initialization
   ├─► Check recent commits
   ├─► Identify root cause
   │
   ▼
4. code-searcher presents findings to assistant:
   "Found: Circular import in coffee_maker/cli/__init__.py"
        │
        ▼
5. assistant delegates fix to code_developer:
   "Fix circular import issue found by code-searcher"
        │
        ▼
6. code_developer:
   ├─► Fix circular import
   ├─► Add test to prevent regression
   ├─► Run tests
   └─► Commit and create PR
```

### Workflow 4: Check Project Status

```
1. User: "How's the project going?"
        │
        ▼
2. assistant:
   - Quick overview? Handle directly
   - Detailed analysis? Delegate to project_manager
        │
        ▼
3. project_manager (detailed analysis):
   ├─► Read docs/roadmap/ROADMAP.md
   ├─► Check GitHub: gh pr list, gh issue list
   ├─► Check CI status: gh pr checks
   ├─► Analyze velocity, blockers
   │
   ▼
4. project_manager generates report:

   ## Project Status

   **Overall**: 65% complete, good progress

   **Recent Completions**:
   - PRIORITY 12: Email Notifications ✅
   - PRIORITY 13: Error Handling ✅

   **In Progress**:
   - PRIORITY 15: Dashboard Redesign (60% complete)

   **Blockers**: None identified

   **Next Up**: PRIORITY 16: API Integration

   **GitHub**:
   - Open PRs: 2 (1 ready to merge, 1 in review)
   - Open Issues: 3 (all low priority)
   - CI: All checks passing ✅
```

---

## Examples

### Example 1: Correct Delegation

```
User: "Add logging to the daemon and document it"

✅ CORRECT:

assistant:
"This task requires TWO agents:
1. code_developer - Add logging (code changes)
2. project_manager - Document it (docs/ updates)

Let me coordinate..."

[Delegates to code_developer first for implementation]
[Then delegates to project_manager for documentation]
```

### Example 2: Incorrect Approach (Don't Do This)

```
User: "Add logging to the daemon and document it"

❌ INCORRECT:

assistant tries to modify code directly
→ NO! code_developer owns ALL code changes

assistant tries to update docs directly
→ NO! project_manager owns docs/ directory
```

### Example 3: Quick Question (assistant Handles)

```
User: "What's the current priority?"

✅ CORRECT:

assistant:
[Reads docs/roadmap/ROADMAP.md]

"Current priority is PRIORITY 15: Dashboard Redesign
Status: In Progress (60% complete)
Expected completion: 2 days"

[No delegation needed - quick documentation lookup]
```

### Example 4: Complex Search (Delegate)

```
User: "Find all database queries in the codebase"

✅ CORRECT:

assistant:
"This requires deep codebase analysis.
Delegating to code-searcher..."

[code-searcher greps entire codebase]
[code-searcher traces patterns]
[code-searcher presents findings]

assistant:
"Found 47 database queries across 12 files.
Should I have project_manager document this?"
```

### Example 5: GitHub Status (Delegate)

```
User: "Are our PRs ready to merge?"

✅ CORRECT:

assistant:
"Checking GitHub status via project_manager..."

[project_manager runs: gh pr list]
[project_manager runs: gh pr checks for each]

project_manager:
"PR #42: Ready to merge ✅ (all checks passing)
PR #43: Blocked ❌ (failing tests)
PR #44: In review 🔄 (waiting on approval)"
```

---

## Key Principles

### 1. assistant is Documentation Expert + Dispatcher

```
┌──────────────────────────────────┐
│         assistant                │
│                                  │
│  PROFOUND KNOWLEDGE OF:          │
│  • docs/roadmap/ROADMAP.md       │
│  • All technical specs           │
│  • .claude/CLAUDE.md             │
│  • Project architecture          │
│                                  │
│  RESPONSIBILITIES:               │
│  • Answer quick questions        │
│  • Delegate complex tasks        │
│  • Never modify code/docs        │
│  • Always READ-ONLY              │
└──────────────────────────────────┘
```

### 2. code_developer Owns Execution

```
┌──────────────────────────────────┐
│       code_developer             │
│                                  │
│  OWNS:                           │
│  • coffee_maker/                 │
│  • tests/                        │
│  • scripts/                      │
│  • pyproject.toml                │
│                                  │
│  RESPONSIBILITIES:               │
│  • ALL code changes              │
│  • Test writing                  │
│  • Create PRs autonomously       │
│  • Update ROADMAP status         │
│  • DoD verification (during)     │
│                                  │
│  DOES NOT:                       │
│  • Create technical specs        │
│  • Monitor project health        │
│  • Make strategic decisions      │
└──────────────────────────────────┘
```

### 3. project_manager Owns Oversight

```
┌──────────────────────────────────┐
│       project_manager            │
│                                  │
│  OWNS:                           │
│  • docs/                         │
│  • .claude/agents/               │
│  • .claude/commands/             │
│                                  │
│  RESPONSIBILITIES:               │
│  • Strategic ROADMAP decisions   │
│  • Create technical specs        │
│  • GitHub monitoring             │
│  • DoD verification (post)       │
│  • Warn about blockers           │
│                                  │
│  DOES NOT:                       │
│  • Write implementation code     │
│  • Create PRs                    │
└──────────────────────────────────┘
```

### 4. Specialized Agents Have Clear Domains

```
code-searcher:          ux-design-expert:       memory-bank-sync:
READ-ONLY analysis      Design specifications   Doc synchronization
│                       │                       │
└─► Findings to         └─► Specs to            └─► Updates to
    assistant               implementer             CLAUDE.md
```

---

## Reference Documents

- **ROADMAP**: docs/roadmap/ROADMAP.md
- **Agent Definitions**: .claude/agents/
- **Ownership Matrix**: .claude/CLAUDE.md (Agent Tool Ownership section)
- **Prompt Index**: .claude/commands/PROMPTS_INDEX.md
- **Architecture**: docs/ARCHITECTURE.md

---

## Version

**Created**: 2025-10-14
**Part of**: Documentation reorganization initiative
**Maintained by**: project_manager
