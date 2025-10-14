# Agent Permissions & Boundaries Reference

Quick reference for understanding agent capabilities, file ownership, and task delegation.

---

## File & Directory Ownership

**WHO can modify WHAT files**

| File/Directory | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| **docs/** | project_manager | YES - Full control | code_developer: READ-ONLY, assistant: READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | project_manager: Full, code_developer: Status updates only | assistant: READ-ONLY |
| **docs/PRIORITY_*_TECHNICAL_SPEC.md** | project_manager | YES - Creates and updates specs | code_developer: READ-ONLY, assistant: READ-ONLY |
| **.claude/agents/** | project_manager | YES - Defines agent configurations | All others: READ-ONLY |
| **.claude/CLAUDE.md** | project_manager, memory-bank-synchronizer | YES - Strategic updates | code_developer: READ-ONLY, assistant: READ-ONLY |
| **.claude/commands/** | project_manager | YES - Manages prompts | code_developer: READ-ONLY (loads during execution), assistant: READ-ONLY |
| **coffee_maker/** | code_developer | YES - All implementation | All others: READ-ONLY |
| **tests/** | code_developer | YES - All test code | All others: READ-ONLY |
| **scripts/** | code_developer | YES - Utility scripts | All others: READ-ONLY |
| **pyproject.toml** | code_developer | YES - Dependency management | All others: READ-ONLY |

---

## Agent Capabilities Summary

### assistant - Documentation Expert + Intelligent Dispatcher
**CAN DO**:
- Answer questions using deep knowledge of ALL project docs (ROADMAP, specs, CLAUDE.md)
- Delegate complex tasks to specialized agents
- Provide quick references and explanations
- Show features visually with Puppeteer (demos only)
- Simple code searches (1-2 files with Grep/Read)

**CANNOT DO**:
- Modify ANY code or documentation (always READ-ONLY)
- Make strategic decisions
- Implement features
- Create technical specs
- Verify Definition of Done

**Key Role**: Librarian + traffic controller - knows everything, delegates appropriately

---

### code_developer - Execution & Implementation
**CAN DO**:
- Write and modify ALL code (coffee_maker/, tests/, scripts/)
- Update dependencies (pyproject.toml)
- Create PRs autonomously
- Update ROADMAP status (Planned → In Progress → Complete)
- Verify DoD during implementation with Puppeteer
- Run tests and fix bugs

**CANNOT DO**:
- Modify docs/ directory (that's project_manager)
- Create technical specs (that's project_manager)
- Make strategic ROADMAP decisions (that's project_manager)
- Monitor project health (that's project_manager)
- Design UI/UX (that's ux-design-expert)

**Key Role**: The ONLY agent that writes/modifies code

---

### project_manager - Oversight & Documentation
**CAN DO**:
- Create and update technical specs (docs/PRIORITY_*_TECHNICAL_SPEC.md)
- Make strategic ROADMAP decisions (priorities, planning)
- Modify docs/ directory
- Manage .claude/agents/ (agent definitions)
- Manage .claude/commands/ (prompts)
- Monitor GitHub (PRs, issues, CI/CD status with gh commands)
- Verify completed work post-implementation with Puppeteer
- Warn users about blockers

**CANNOT DO**:
- Write implementation code (that's code_developer)
- Create PRs (that's code_developer)
- Run code directly (that's code_developer)

**Key Role**: The ONLY agent that modifies docs/ directory, strategic oversight

---

### code-searcher - Deep Codebase Analysis
**CAN DO**:
- Deep codebase analysis (READ-ONLY)
- Security audits
- Dependency tracing
- Code reuse identification
- Refactoring opportunity analysis
- Architectural analysis
- Prepare findings for documentation

**CANNOT DO**:
- Modify ANY files (always READ-ONLY)
- Write documentation directly (delegates to project_manager via assistant)

**Key Role**: Forensic code analyst, prepares findings for project_manager to document

**Documentation Process**: code-searcher prepares findings → presents to assistant → assistant delegates to project_manager → project_manager writes docs/[analysis_type]_analysis_[date].md

---

### ux-design-expert - Design Guidance
**CAN DO**:
- UI/UX design decisions
- Tailwind CSS recommendations
- Chart and visualization design
- Provide design specifications

**CANNOT DO**:
- Implement designs (that's code_developer)
- Modify code (that's code_developer)

**Key Role**: Design advisor, provides specifications for code_developer to implement

---

### memory-bank-synchronizer - Documentation Sync
**CAN DO**:
- Update .claude/CLAUDE.md to reflect code reality
- Ensure documentation accuracy
- Sync architectural changes

**CANNOT DO**:
- Modify implementation code (that's code_developer)

**Key Role**: Keeps documentation in sync with codebase

---

## Tool Ownership

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **Puppeteer DoD (during impl)** | code_developer | Verify features DURING implementation | project_manager for POST-completion |
| **Puppeteer DoD (post-impl)** | project_manager | Verify completed work on user request | - |
| **Puppeteer demos** | assistant | Show features visually (demos only) | NOT for verification |
| **GitHub PR create** | code_developer | Create PRs autonomously | - |
| **GitHub monitoring** | project_manager | Monitor PRs, issues, CI/CD status | - |
| **GitHub queries (gh)** | project_manager | All gh commands | assistant delegates |
| **Code editing** | code_developer | ALL code changes | assistant READ-ONLY |
| **Code search (simple)** | assistant | 1-2 files with Grep/Read | Delegate complex to code-searcher |
| **Code search (complex)** | code-searcher | Deep analysis, patterns, forensics | - |
| **ROADMAP updates** | project_manager (full), code_developer (status only) | Strategic vs. execution updates | assistant READ-ONLY |
| **Design decisions** | ux-design-expert | All UI/UX, Tailwind, charts | Others delegate |
| **Doc sync** | memory-bank-synchronizer | Keep CLAUDE.md current | - |

---

## Common Scenarios - Quick Decision Tree

### "I need to fix a bug in the code"
→ **code_developer** (ALL code changes)

### "I need to update documentation"
→ **project_manager** (owns docs/ directory)

### "I need to understand how X works"
→ **assistant** (quick questions) OR **code-searcher** (deep analysis)

### "I need to check project status"
→ **project_manager** (strategic oversight)

### "I need to design a UI"
→ **ux-design-expert** (design specs) THEN **code_developer** (implementation)

### "I need to implement a new feature"
→ **code_developer** (execution)

### "I need to create a technical spec"
→ **project_manager** (owns docs/)

### "I need to verify a feature is complete"
→ **project_manager** (post-implementation DoD verification)

### "I need to analyze the codebase for security issues"
→ **code-searcher** (analysis) THEN **project_manager** (documentation)

### "I need to sync CLAUDE.md with reality"
→ **memory-bank-synchronizer** (doc sync)

---

## Key Rules - Critical Boundaries

1. **assistant is READ-ONLY**
   - NEVER modifies code or docs
   - Always delegates to appropriate agent
   - Acts as documentation expert + dispatcher

2. **code_developer owns code/**
   - ONLY agent that modifies coffee_maker/, tests/, scripts/
   - Creates PRs autonomously
   - Does NOT touch docs/ directory

3. **project_manager owns docs/**
   - ONLY agent that modifies docs/ directory
   - Creates technical specs
   - Makes strategic decisions
   - Does NOT write implementation code

4. **code-searcher is READ-ONLY**
   - Prepares analysis findings
   - NEVER writes documentation directly
   - Always delegates to project_manager via assistant

5. **Clear delegation flow**
   - User → assistant → specialized agent
   - Don't skip steps or overlap responsibilities

---

## Incorrect vs. Correct Usage

### Incorrect Usage - Don't Do This

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

assistant tries to verify DoD
→ NO! project_manager verifies post-completion DoD
```

### Correct Usage - Do This

```
User: "Fix the bug in roadmap_cli.py"
→ code_developer (ALL code changes)

User: "Create a technical spec for PRIORITY 15"
→ project_manager (owns docs/ directory)

User: "Where is authentication implemented?"
→ code-searcher (complex code analysis)

User: "What's our PR status?"
→ project_manager (GitHub monitoring)

User: "Design a dashboard"
→ ux-design-expert (design) THEN code_developer (implementation)

User asks assistant: "Implement feature X"
→ assistant delegates to code_developer
```

---

## Delegation Flow Example

**User to assistant**: "Fix bug in CLI and update the docs"

**Correct Response**:
```
assistant: "This requires two agents:
1. code_developer - Fix the bug in CLI (code changes)
2. project_manager - Update documentation (docs/ directory)

Let me delegate appropriately..."

[assistant creates tasks for both agents, does NOT implement directly]
```

---

## Quick Reference Card

| Need | Agent | Reason |
|------|-------|--------|
| Code changes | code_developer | Owns coffee_maker/, tests/, scripts/ |
| Documentation | project_manager | Owns docs/ directory |
| Quick question | assistant | Documentation expert |
| Deep analysis | code-searcher | Forensic analysis (READ-ONLY) |
| Design guidance | ux-design-expert | UI/UX decisions |
| Project status | project_manager | Strategic oversight |
| DoD verification | project_manager | Post-completion verification |
| PR creation | code_developer | Autonomous PR creation |
| GitHub monitoring | project_manager | Strategic monitoring |

---

**Version**: 1.0
**Last Updated**: 2025-10-13
**Purpose**: Quick reference for agent boundaries and permissions
