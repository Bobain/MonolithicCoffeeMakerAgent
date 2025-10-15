# Team Collaboration Guide

Visual guide to agent interactions, ownership, and workflows in the MonolithicCoffeeMakerAgent system.

## Table of Contents
- [Agent Overview](#agent-overview)
- [Architecture: user_listener → Backend Agents](#architecture-user_listener--backend-agents)
- [Request Flow Diagrams](#request-flow-diagrams)
- [Ownership Matrix](#ownership-matrix)
- [Decision Tree: Which Agent?](#decision-tree-which-agent)
- [Common Workflows](#common-workflows)
- [Examples](#examples)
- [Version History](#version-history)

---

## Agent Overview

The MonolithicCoffeeMakerAgent system consists of 8 active specialized AI agents:

1. **user_listener** (PRIMARY UI)
2. **architect** (architectural design)
3. **code_developer** (implementation)
4. **code-sanitizer** (code quality)
5. **project_manager** (strategic oversight)
6. **assistant** (documentation expert & dispatcher)
7. **code-searcher** (deep analysis)
8. **ux-design-expert** (design)

Plus ACE Framework components:
- **generator** (trace capture)
- **reflector** (insight extraction)
- **curator** (playbook curation)

```
┌────────────────────────────────────────────────────────────────┐
│                  MonolithicCoffeeMakerAgent                    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  user_listener  │ ◄── PRIMARY UI (ONLY agent with UI)
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼───────┐  ┌─────▼─────┐  ┌──────▼──────┐
    │   assistant   │  │ architect │  │code_developer│
    │ (Dispatcher)  │  │ (Design)  │  │ (Execution)  │
    └───────┬───────┘  └─────┬─────┘  └──────┬───────┘
            │                │                │
    ┌───────┴────────────────┴────────────────┴──────┐
    │                                                 │
┌───▼────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│code-       │  │ux-design-    │  │project_mgr   │  │code-         │
│searcher    │  │expert        │  │(Oversight)   │  │sanitizer     │
│(Analysis)  │  │(Design)      │  │              │  │(Quality)     │
└────────────┘  └──────────────┘  └──────┬───────┘  └──────────────┘
                                          │
                                  ┌───────▼───────┐
                                  │ACE Framework  │
                                  │(Learning)     │
                                  └───────────────┘
```

### PRIMARY USER INTERFACE

**user_listener** - PRIMARY USER INTERFACE ⭐
- Role: ONLY agent with UI - interprets user intent and delegates to team
- Scope: User interaction, chat interface, CLI
- Authority: Routes all user requests to appropriate backend agents
- Important: ALL other agents are backend-only (NO UI)
- Motto: "Your single point of contact"

### Backend Agents (NO UI)

**assistant** - Documentation Expert + Intelligent Dispatcher
- Role: Routes requests to appropriate agents
- Knowledge: Deep understanding of ALL project documentation
- Approach: Handles quick questions, delegates complex tasks
- Access: READ-ONLY on all files
- Motto: "Librarian + Traffic Controller"

**architect** - Strategic Architecture & Roadmap Optimization
- Role: Strategic architectural oversight, roadmap optimization, dependency management
- Scope: docs/architecture/, pyproject.toml, poetry.lock
- Authority: Creates ADRs, manages dependencies (requires user approval), provides implementation guidelines, influences ROADMAP prioritization
- Philosophy: Takes a step back - analyzes ENTIRE roadmap and ENTIRE codebase (big picture)
- Workflow: Works BEFORE code_developer (strategic design and priority optimization)
- Impact: Identifies implementation synergies, recommends priority reordering to maximize value
- Motto: "Design first, optimize priorities, implement efficiently"

**code_developer** - Autonomous Implementation
- Role: Executes all code changes
- Scope: coffee_maker/, tests/, scripts/, .claude/
- Authority: Creates PRs autonomously, updates ROADMAP status
- Workflow: Implements AFTER architect designs
- Motto: "I write the code, not the docs"

**code-sanitizer** - Code Quality Monitoring
- Role: Analyze code quality, detect refactoring opportunities
- Scope: docs/refacto/, .gemini.styleguide.md
- Trigger: Wakes automatically when code_developer commits
- Authority: Generates refactoring recommendations for project_manager
- Access: READ-ONLY on coffee_maker/ (analyzes but doesn't modify)
- Motto: "Monitor quality, recommend improvements"

**project_manager** - Strategic Oversight
- Role: Project coordination and documentation
- Scope: docs/*.md, docs/roadmap/, docs/templates/, docs/code-searcher/, .claude/agents/, .claude/commands/
- Authority: Strategic ROADMAP decisions, technical specs, GitHub monitoring
- Motto: "Plan, coordinate, verify"

### Specialized Backend Agents

**code-searcher** - Deep Codebase Analysis
- Role: Security audits, dependency tracing, pattern analysis
- Access: READ-ONLY entire codebase
- Output: Findings presented to assistant → delegated to project_manager for docs
- Motto: "I find it, you document it"

**ux-design-expert** - UI/UX Design
- Role: Design decisions, Tailwind CSS, charts
- Output: Design specifications (does not implement)
- Motto: "Form follows function"

**ACE Framework** - Continuous Learning
- generator: Captures execution traces → docs/generator/
- reflector: Extracts insights → docs/reflector/
- curator: Maintains evolving playbooks → docs/curator/
- Motto: "Learn, adapt, improve"

---

## Architecture: user_listener → Backend Agents

**CRITICAL UNDERSTANDING**:

```
┌─────────────────────────────────────────────┐
│         USER INTERACTION LAYER              │
│                                             │
│         ┌─────────────────┐                 │
│         │  user_listener  │ ◄── ONLY UI    │
│         └────────┬────────┘                 │
└──────────────────┼──────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│          │  │          │  │          │
│ Backend  │  │ Backend  │  │ Backend  │
│ Agents   │  │ Agents   │  │ Agents   │
│ (NO UI)  │  │ (NO UI)  │  │ (NO UI)  │
│          │  │          │  │          │
└──────────┘  └──────────┘  └──────────┘
  assistant    architect    code-sanitizer
  project_mgr  code_dev     code-searcher
  ux-design    generator    reflector
               curator
```

**Key Points**:
- user_listener is the ONLY agent with UI
- ALL other agents are backend-only
- User never interacts directly with backend agents
- All requests flow through user_listener

---

## Request Flow Diagrams

### Basic User Request Flow

```
User Request
     │
     ▼
┌─────────────┐
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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

### Architecture Design Flow

```
User: "Design authentication system"
     │
     ▼
┌─────────────┐
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  architect  │ ◄── Pre-implementation design
└──────┬──────┘
       │
       ├──► Analyze requirements
       ├──► Design architecture
       ├──► Create technical spec (docs/architecture/specs/)
       ├──► Document decisions (ADRs in docs/architecture/decisions/)
       ├──► Provide guidelines (docs/architecture/guidelines/)
       │
       ▼
┌──────────────┐
│code_developer│ ◄── Reads spec and implements
└──────────────┘
```

### Code Quality Monitoring Flow

```
code_developer commits code
     │
     ▼
┌──────────────┐
│code-sanitizer│ ◄── Wakes automatically
└──────┬───────┘
       │
       ├──► Analyze complexity (radon)
       ├──► Check style (flake8)
       ├──► Detect duplication
       ├──► Generate recommendations
       │
       ▼
Write report to docs/refacto/refactoring_analysis_YYYY-MM-DD.md
       │
       ▼
┌──────────────┐
│project_mgr   │ ◄── Reads report
└──────┬───────┘
       │
       ▼
Decision: Next priority = REFACTOR or IMPLEMENT?
```

### Code Change Request Flow

```
User: "Fix bug in roadmap_cli.py"
     │
     ▼
┌─────────────┐
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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
│project_mgr   │ ◄── ONLY agent that modifies docs/*.md
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
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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
│user_listener│ ◄── PRIMARY USER INTERFACE (ONLY agent with UI)
└──────┬──────┘
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

### File and Directory Ownership (NO OVERLAPS)

**CRITICAL RULE**: NO agent can own a parent directory when subdirectories have different owners.

| Path | Owner | Permissions | Others |
|------|-------|-------------|--------|
| **docs/*.md** | project_manager | Top-level files ONLY | READ-ONLY |
| **docs/roadmap/** | project_manager | Full control | READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | PM: Strategic, CD: Status only | READ-ONLY |
| **docs/architecture/** | architect | Technical specs, ADRs, guidelines | READ-ONLY |
| **docs/refacto/** | code-sanitizer | Refactoring recommendations | READ-ONLY (PM uses for decisions) |
| **docs/generator/** | generator | Execution traces | READ-ONLY |
| **docs/reflector/** | reflector | Delta items (insights) | READ-ONLY |
| **docs/curator/** | curator | Playbooks | READ-ONLY |
| **docs/templates/** | project_manager | Documentation templates | READ-ONLY |
| **docs/code-searcher/** | project_manager | Code analysis docs | code-searcher prepares (READ-ONLY) |
| **pyproject.toml** | architect | Dependency management (user approval required) | READ-ONLY |
| **poetry.lock** | architect | Dependency lock | READ-ONLY |
| **.gemini.styleguide.md** | code-sanitizer | Code quality guidelines | READ-ONLY |
| **.claude/** | code_developer | Technical configurations | READ-ONLY |
| **coffee_maker/** | code_developer | All implementation | READ-ONLY |
| **tests/** | code_developer | All test code | READ-ONLY |
| **scripts/** | code_developer | Utility scripts | READ-ONLY |
| **.pre-commit-config.yaml** | code_developer | Pre-commit hooks | READ-ONLY |
| **data/user_interpret/** | user_interpret | Operational data | READ-ONLY |

**Why NO overlaps?**
- Enables parallel agent operations without conflicts
- Each directory has EXACTLY one owner
- Runtime validation enforces this rule (system crashes if violated)
- Tests verify NO overlaps exist (34 ownership tests)

### Tool Ownership

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **User Interface (ALL)** | user_listener | ONLY agent with UI | All others: Backend only |
| **Code Editing** | code_developer | ALL code changes | None |
| **Doc Editing (docs/*.md, docs/roadmap/, docs/templates/)** | project_manager | Strategic docs | None |
| **Architecture Specs** | architect | Creates technical specifications before implementation | code_developer reads and implements |
| **ADRs** | architect | Documents architectural decisions | READ-ONLY |
| **Dependency Management** | architect | ONLY agent that runs `poetry add` (user approval required) | code_developer CANNOT modify |
| **Code Quality Analysis** | code-sanitizer | Analyzes complexity, duplication, style | Generates reports for project_manager |
| **Refactoring Recommendations** | code-sanitizer | Prioritized refactoring suggestions | project_manager uses for decisions |
| **Style Enforcement** | code-sanitizer | Enforces .gemini.styleguide.md | code_developer follows guidelines |
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
                            ▼
                    ┌───────────────┐
                    │ user_listener │ ◄── PRIMARY UI (ONLY agent with UI)
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │               │
                Quick              Complex
                question?          task?
                    │               │
                    ▼               │
            ┌───────────────┐      │
            │   assistant   │      │
            │ (answers now) │      │
            └───────────────┘      │
                                    │
        ┌───────────────────────────┘
        │
    What type?
        │
    ┌───┼───┼───┼───┼───┼───┐
    │   │   │   │   │   │   │
    v   v   v   v   v   v   v
  Code Docs Arch Quality Design GitHub ACE
    │   │   │   │   │   │   │
    v   v   v   v   v   v   v
  code_ proj arch code- ux-  proj gen/
  dev   mgr  itect sanit design mgr ref/
                        izer  expert     cur
```

### Quick Reference

**User interaction?** → user_listener
- ONLY agent with UI
- All user requests start here
- Routes to backend agents

**Code changes?** → code_developer
- Anything in coffee_maker/, tests/, scripts/, .claude/
- Bug fixes, feature implementation
- Test writing

**Documentation?** → project_manager
- Anything in docs/*.md, docs/roadmap/, docs/templates/
- Technical specs, ROADMAP updates
- Agent definitions, prompt management

**Architectural design?** → architect
- STRATEGIC: Analyzes ENTIRE roadmap and ENTIRE codebase
- Roadmap optimization: Identifies synergies, recommends priority reordering
- System architecture, technical specs
- ADRs (Architectural Decision Records)
- Dependency management (user approval required)
- Works BEFORE code_developer (strategic design + priority optimization)

**Code quality?** → code-sanitizer
- Complexity analysis
- Refactoring recommendations
- Style enforcement
- Wakes when code_developer commits

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

**ACE Framework?**
- Trace capture → generator
- Insight extraction → reflector
- Playbook curation → curator

---

## Common Workflows

### Workflow 1: architect Strategic Analysis & Roadmap Optimization

```
1. User: "We need Slack integration and Email notifications"
        │
        ▼
2. user_listener → architect:
   "Analyze notification requirements and optimize implementation"
        │
        ▼
3. architect (STRATEGIC ANALYSIS - Step Back, Big Picture):
   ├─► Analyze ENTIRE ROADMAP:
   │   • US-034: Slack Integration (Status: Planned, Estimate: 8h)
   │   • US-042: Email Notifications (Status: Planned, Estimate: 8h)
   │   • Both currently separate priorities
   │
   ├─► Analyze ENTIRE CODEBASE:
   │   • coffee_maker/notifications/ already exists
   │   • Base notification system implemented
   │   • Pattern: Channel-agnostic notification framework
   │
   ├─► IDENTIFY SYNERGY:
   │   • Both US-034 and US-042 use same notification patterns
   │   • If Slack implemented first with extensibility,
   │     Email becomes trivial (reuse 80% of infrastructure)
   │   • TIME SAVINGS IDENTIFIED: 6 hours (37.5% reduction!)
   │
   ├─► CREATE SYNERGY REPORT:
   │   docs/architecture/synergies/SYNERGY_2025-10-15_notifications.md
   │   Contains:
   │   - Original estimates: US-034 (8h) + US-042 (8h) = 16h total
   │   - Optimized estimates: US-034 (8h) + US-042 (2h) = 10h total
   │   - Time savings: 6h (37.5%)
   │   - Recommendation: Move US-042 immediately after US-034
   │
        ▼
4. architect → project_manager:
   "PRIORITY OPTIMIZATION RECOMMENDATION:

   Current ROADMAP order:
   - US-030: Feature A
   - US-031: Feature B
   - US-034: Slack Integration (8h)
   - US-040: Feature C
   - US-042: Email Notifications (8h)
   Total: 16h for notifications

   RECOMMENDED order:
   - US-030: Feature A
   - US-031: Feature B
   - US-034: Slack Integration (8h - implement with extensibility)
   - US-042: Email Notifications (2h - reuse infrastructure!)
   - US-040: Feature C
   Total: 10h for notifications (SAVES 6 hours!)

   Rationale: Implementing consecutively allows 80% code reuse.
   This ships both features faster, maximizing value/time."
        │
        ▼
5. project_manager:
   ├─► Reviews architect's synergy report
   ├─► Updates ROADMAP priorities (reorders US-042)
   ├─► Reduces US-042 estimate from 8h to 2h
   ├─► Documents synergy in US-042 description
   └─► Notifies team of priority changes
        │
        ▼
6. architect:
   ├─► Creates technical specifications:
   │   docs/architecture/specs/notification_framework_spec.md
   ├─► Designs extensible architecture
   ├─► Creates ADR: docs/architecture/decisions/ADR-007-notification-channels.md
   ├─► Provides implementation guidelines for code_developer
        │
        ▼
7. code_developer:
   ├─► Implements US-034 (Slack) with extensibility per architect's design
   ├─► Then quickly implements US-042 (Email) reusing infrastructure
   └─► Total time: 10h instead of 16h ✅
```

**Key Distinction**:
- **architect** = STRATEGIC (step back, entire roadmap, entire codebase, find synergies)
- **code_developer** = TACTICAL (focus on next priority, execute design)

### Workflow 2: Architect Design & Dependency Management

```
1. User: "Add authentication system"
        │
        ▼
2. user_listener → architect:
   "Design authentication architecture"
        │
        ▼
3. architect:
   ├─► Analyze requirements
   ├─► Design architecture
   ├─► Create docs/architecture/specs/authentication_spec.md
   ├─► Create ADR: docs/architecture/decisions/ADR-005-jwt-vs-session.md
   ├─► Check dependencies needed
   │
   ├─► Need PyJWT? Ask user approval via user_listener
   │   User approves ✅
   ├─► Run: poetry add pyjwt
   ├─► Document decision in ADR
   │
   └─► Write implementation guidelines
        │
        ▼
4. architect → code_developer:
   "Implement authentication per spec"
        │
        ▼
5. code_developer:
   ├─► Read docs/architecture/specs/authentication_spec.md
   ├─► Read docs/architecture/guidelines/
   ├─► Implement in coffee_maker/auth/
   ├─► Write tests
   ├─► Commit and PR
        │
        ▼
6. architect reviews implementation (optional)
```

### Workflow 3: Code Quality Monitoring

```
1. code_developer commits code
        │
        ▼
2. code-sanitizer wakes up automatically:
   ├─► Analyze complexity (radon)
   ├─► Check style (flake8)
   ├─► Detect duplication
   ├─► Compare against .gemini.styleguide.md
        │
        ▼
3. code-sanitizer generates report:
   docs/refacto/refactoring_analysis_2025-10-15.md

   Contains:
   - High priority: 2 items (complexity > 15)
   - Medium priority: 3 items
   - Low priority: 5 items
        │
        ▼
4. project_manager reads report:
   ├─► Reviews high-priority items
   ├─► Assesses impact on velocity
   ├─► Checks ROADMAP priorities
        │
        ▼
5. project_manager decides:

   Option A: Many high-priority issues
   → Create ROADMAP priority: "REFACTOR: Reduce complexity"
   → code_developer refactors next sprint

   Option B: Few issues, features more important
   → Acknowledge recommendations
   → Add to backlog
   → Continue with features
```

### Workflow 4: Implement New Feature

```
1. User: "Implement PRIORITY 12: Email Notifications"
        │
        ▼
2. user_listener → assistant:
   [Routes request to backend]
        │
        ▼
3. assistant analyzes:
   - Reads docs/roadmap/ROADMAP.md
   - Checks PRIORITY 12 details
   - Sees technical spec exists: docs/PRIORITY_12_TECHNICAL_SPEC.md
   - Determines: Code implementation task
        │
        ▼
4. assistant delegates to code_developer:
   "Please implement PRIORITY 12 per the technical spec"
        │
        ▼
5. code_developer:
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
6. code_developer reports: "PRIORITY 12 complete, PR #42 created"
```

### Workflow 5: Create Technical Spec

```
1. User: "Create spec for PRIORITY 15: Dashboard Redesign"
        │
        ▼
2. user_listener → assistant:
   [Routes request to backend]
        │
        ▼
3. assistant:
   - Reads docs/roadmap/ROADMAP.md
   - Checks PRIORITY 15 details
   - Determines: Documentation task
   - May need design input
        │
        ▼
4. assistant checks if design input needed:
   "Should I involve ux-design-expert for design recommendations?"
        │
        ├─► If Yes:
        │   ├─► Delegate to ux-design-expert
        │   └─► Get design specs
        │
        ▼
5. assistant delegates to project_manager:
   "Create technical spec for PRIORITY 15"
   [Includes design specs if applicable]
        │
        ▼
6. project_manager:
   ├─► Read docs/roadmap/ROADMAP.md PRIORITY 15
   ├─► Incorporate design specs (if provided)
   ├─► Create docs/PRIORITY_15_TECHNICAL_SPEC.md
   ├─► Update docs/roadmap/ROADMAP.md with spec reference
   └─► Git commit
        │
        ▼
7. project_manager reports: "Spec created at docs/PRIORITY_15_TECHNICAL_SPEC.md"
```

### Workflow 6: Investigate Bug

```
1. User: "Why is the CLI crashing on startup?"
        │
        ▼
2. user_listener → assistant:
   [Routes request to backend]
        │
        ▼
3. assistant:
   - Simple investigation? Try quick analysis
   - Complex? Delegate to code-searcher
        │
        ▼
4. code-searcher (for complex issues):
   ├─► Grep for crash patterns
   ├─► Trace CLI initialization
   ├─► Check recent commits
   ├─► Identify root cause
   │
   ▼
5. code-searcher presents findings to assistant:
   "Found: Circular import in coffee_maker/cli/__init__.py"
        │
        ▼
6. assistant delegates fix to code_developer:
   "Fix circular import issue found by code-searcher"
        │
        ▼
7. code_developer:
   ├─► Fix circular import
   ├─► Add test to prevent regression
   ├─► Run tests
   └─► Commit and create PR
```

### Workflow 7: Check Project Status

```
1. User: "How's the project going?"
        │
        ▼
2. user_listener → assistant:
   [Routes request to backend]
        │
        ▼
3. assistant:
   - Quick overview? Handle directly
   - Detailed analysis? Delegate to project_manager
        │
        ▼
4. project_manager (detailed analysis):
   ├─► Read docs/roadmap/ROADMAP.md
   ├─► Check GitHub: gh pr list, gh issue list
   ├─► Check CI status: gh pr checks
   ├─► Analyze velocity, blockers
   │
   ▼
5. project_manager generates report:

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

user_listener → assistant:
[Routes to backend]

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

code_developer tries to add dependencies
→ NO! architect manages dependencies (with user approval)

project_manager tries to modify coffee_maker/
→ NO! code_developer owns coffee_maker/ directory
```

### Example 3: Quick Question (assistant Handles)

```
User: "What's the current priority?"

✅ CORRECT:

user_listener → assistant:
[Routes to backend]

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

user_listener → assistant:
[Routes to backend]

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

user_listener → assistant:
[Routes to backend]

assistant:
"Checking GitHub status via project_manager..."

[project_manager runs: gh pr list]
[project_manager runs: gh pr checks for each]

project_manager:
"PR #42: Ready to merge ✅ (all checks passing)
PR #43: Blocked ❌ (failing tests)
PR #44: In review 🔄 (waiting on approval)"
```

### Example 6: Architectural Design (Delegate)

```
User: "Design a microservices architecture"

✅ CORRECT:

user_listener → assistant:
[Routes to backend]

assistant:
"Delegating to architect for system design..."

architect:
├─► Analyze requirements
├─► Research patterns
├─► Create docs/architecture/specs/microservices_design.md
├─► Create ADR: docs/architecture/decisions/ADR-006-monolith-to-microservices.md
└─► Document guidelines

architect:
"Architecture designed. See docs/architecture/ for details."
```

### Example 7: Code Quality Check (Automatic)

```
code_developer commits code to feature/us-015-metrics-tracking

✅ AUTOMATIC:

code-sanitizer wakes up:
├─► Analyzes coffee_maker/metrics/
├─► Detects: 2 functions with complexity > 15
├─► Generates: docs/refacto/refactoring_analysis_2025-10-15.md

project_manager reads report:
"High-priority refactoring items detected.
Should we address before continuing?"

[Decision: Continue with features, add refactoring to backlog]
```

---

## Key Principles

### 1. user_listener is PRIMARY UI

```
┌──────────────────────────────────┐
│         user_listener            │
│                                  │
│  ONLY AGENT WITH UI              │
│  • Chat interface                │
│  • CLI interaction               │
│  • All user requests             │
│                                  │
│  RESPONSIBILITIES:               │
│  • Interpret user intent         │
│  • Route to backend agents       │
│  • No backend logic              │
└──────────────────────────────────┘
```

### 2. assistant is Documentation Expert + Dispatcher

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

### 3. architect Strategizes First (STRATEGIC vs TACTICAL)

```
┌──────────────────────────────────┐
│         architect                │
│                                  │
│  ROLE: STRATEGIC                 │
│  • Step back (big picture)       │
│  • Analyzes ENTIRE roadmap       │
│  • Analyzes ENTIRE codebase      │
│                                  │
│  OWNS:                           │
│  • docs/architecture/            │
│  • docs/architecture/synergies/  │
│  • pyproject.toml                │
│  • poetry.lock                   │
│                                  │
│  RESPONSIBILITIES:               │
│  • Roadmap optimization          │
│  • Identify synergies            │
│  • Recommend priority reordering │
│  • Maximize value/time           │
│  • System architecture           │
│  • Technical specifications      │
│  • ADRs                          │
│  • Dependency management         │
│  • Works BEFORE code_developer   │
│                                  │
│  IMPACT ON PRIORITIZATION:       │
│  • Can recommend moving up/down  │
│  • Identifies quick wins         │
│  • Estimates time savings        │
│  • project_manager adjusts       │
│                                  │
│  REQUIRES:                       │
│  • User approval for deps        │
└──────────────────────────────────┘
```

### 4. code_developer Implements Second (TACTICAL)

```
┌──────────────────────────────────┐
│       code_developer             │
│                                  │
│  ROLE: TACTICAL                  │
│  • Focus on next priority        │
│  • Execute design                │
│  • Single priority at a time     │
│                                  │
│  OWNS:                           │
│  • coffee_maker/                 │
│  • tests/                        │
│  • scripts/                      │
│  • .claude/                      │
│                                  │
│  RESPONSIBILITIES:               │
│  • ALL code changes              │
│  • Test writing                  │
│  • Create PRs autonomously       │
│  • Update ROADMAP status         │
│  • DoD verification (during)     │
│  • Works AFTER architect         │
│                                  │
│  DOES NOT:                       │
│  • Analyze entire roadmap        │
│  • Optimize priorities           │
│  • Create technical specs        │
│  • Monitor project health        │
│  • Make strategic decisions      │
│  • Manage dependencies           │
│                                  │
│  KEY DISTINCTION:                │
│  architect = STRATEGIC           │
│  code_developer = TACTICAL       │
└──────────────────────────────────┘
```

### 5. code-sanitizer Monitors Quality

```
┌──────────────────────────────────┐
│       code-sanitizer             │
│                                  │
│  OWNS:                           │
│  • docs/refacto/                 │
│  • .gemini.styleguide.md         │
│                                  │
│  RESPONSIBILITIES:               │
│  • Analyze complexity            │
│  • Detect duplication            │
│  • Check style                   │
│  • Generate recommendations      │
│  • Wakes AFTER code_developer    │
│                                  │
│  ACCESS:                         │
│  • READ-ONLY on coffee_maker/    │
│  • Analyzes but doesn't modify   │
└──────────────────────────────────┘
```

### 6. project_manager Oversees Strategy

```
┌──────────────────────────────────┐
│       project_manager            │
│                                  │
│  OWNS:                           │
│  • docs/*.md                     │
│  • docs/roadmap/                 │
│  • docs/templates/               │
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
│  • Manage dependencies           │
└──────────────────────────────────┘
```

### 7. Specialized Agents Have Clear Domains

```
code-searcher:          ux-design-expert:       ACE Framework:
READ-ONLY analysis      Design specifications   Continuous learning
│                       │                       │
└─► Findings to         └─► Specs to            └─► Traces/Insights
    assistant               implementer             to system
```

---

## Reference Documents

- **ROADMAP**: docs/roadmap/ROADMAP.md
- **Agent Definitions**: .claude/agents/
- **Ownership Matrix**: .claude/CLAUDE.md (Agent Tool Ownership section)
- **Prompt Index**: .claude/commands/PROMPTS_INDEX.md
- **Architecture**: docs/ARCHITECTURE.md

---

## Version History

**v3.0 (2025-10-15)** - Major architectural update
- Added architect agent (architectural design & dependencies)
- Added code-sanitizer agent (code quality monitoring)
- Added user_listener as PRIMARY UI
- Removed memory-bank-synchronizer (obsolete - tag-based workflow)
- Fixed ownership overlaps (NO overlaps enforced)
- Updated all workflows and decision trees
- pyproject.toml now owned by architect (not code_developer)

**v2.0 (2025-10-14)** - Documentation reorganization

**v1.0 (Original)** - Initial team collaboration guide

---

**Created**: 2025-10-14
**Last Updated**: 2025-10-15
**Part of**: Documentation reorganization initiative
**Maintained by**: project_manager
