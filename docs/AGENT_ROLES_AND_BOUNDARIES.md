# Agent Roles & Boundaries

**Version**: 1.0
**Date**: 2025-10-15
**Status**: Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Critical Principles](#critical-principles)
3. [Agent Directory](#agent-directory)
4. [Detailed Agent Roles](#detailed-agent-roles)
5. [File Ownership Matrix](#file-ownership-matrix)
6. [Tool Ownership Matrix](#tool-ownership-matrix)
7. [Parallel Operations](#parallel-operations)
8. [Git Strategy](#git-strategy)
9. [ACE Integration](#ace-integration)
10. [Workflow Examples](#workflow-examples)
11. [Summary](#summary)

---

## Overview

This document defines clear roles, responsibilities, file ownership, and boundaries for all agents in the MonolithicCoffeeMakerAgent system.

**Goal**: Prevent overlapping responsibilities, clarify ownership, enable parallel operations.

---

## Critical Principles

### 1. One Owner Per File
- Each file/directory has ONE owner
- Only the owner can modify
- Others can read but not write

### 2. Read-Only for Others
- Non-owners can read files for context
- Non-owners NEVER modify files they don't own
- Delegation is required for modifications

### 3. No Branch Switching
- All agents work on `roadmap` branch
- NEVER switch branches (git checkout/switch forbidden)
- code_developer uses tags instead of branches

### 4. Singleton Agents
- Only ONE instance of each agent at a time
- Prevents file conflicts
- Critical for code_developer (only one can modify code)

### 5. ACE by Default
- All agents have ACE enabled (except user_listener)
- Traces captured automatically
- Continuous learning loop

### 6. UI Ownership
- user_listener is the ONLY agent with a UI
- All other agents are backend only
- Users interact ONLY through user_listener

---

## Agent Directory

| Agent | Primary Role | ACE Enabled | Always Running | UI Access |
|-------|-------------|-------------|----------------|-----------|
| **user_listener** | User interface (ONLY agent with UI) | ❌ (UI, no learning) | ✅ (interactive) | ✅ (ONLY agent) |
| **user_interpret** | Intent + sentiment + delegation | ✅ | ✅ (singleton) | ❌ (backend) |
| **architect** | Architectural design and technical specifications | ✅ | As needed | ❌ (backend) |
| **code_developer** | Implementation, PRs, DoD verification | ✅ | ⚠️ (ONE instance only) | ❌ (backend) |
| **project_manager** | Strategy, docs, monitoring | ✅ | As needed | ❌ (backend) |
| **assistant** | Questions, demos, documentation expert | ✅ | As needed | ❌ (backend) |
| **code-searcher** | Deep code analysis | ✅ | As needed | ❌ (backend) |
| **ux-design-expert** | Design decisions | ✅ | As needed | ❌ (backend) |
| **generator** (ACE) | Observe executions, create traces | N/A (part of ACE) | ✅ (wraps all agents) | ❌ (backend) |
| **reflector** (ACE) | Extract insights from traces | N/A (part of ACE) | Manual/Scheduled | ❌ (backend) |
| **curator** (ACE) | Maintain evolving playbooks | N/A (part of ACE) | Manual/Scheduled | ❌ (backend) |

---

## Detailed Agent Roles

### user_listener

**Role**: User interface (only agent users interact with)

**Responsibilities**:
- Display UI (Rich console, Streamlit future)
- Get user input via CLI
- Call user_interpret for intent analysis
- Delegate to chosen agent
- Show proactive suggestions from user_interpret
- Ask curator feedback questions
- Show progress indicators
- Display agent responses with colors
- Synthesize multi-agent responses

**Owned Files**: None (UI only)

**Can Read**: All (for display purposes)

**Can Write**: None

**ACE**: Disabled (UI only, no learning needed)

**Communication Style**:
- Friendly, approachable
- Plain language
- Proactive suggestions
- Attribution (which agent said what)

**Example Interaction**:
```
User: "What's the status?"

user_listener:
1. Calls user_interpret to analyze intent
2. user_interpret returns: delegate_to="project_manager"
3. Calls project_manager to get status
4. Synthesizes response with attribution
5. Displays: "[project_manager] Current status: ..."
```

---

### user_interpret

**Role**: Interpret intent, analyze sentiment, choose agent

**Responsibilities**:
- Analyze user sentiment (frustration, satisfaction, confusion, etc.)
- Interpret user intent (add_feature, ask_how_to, view_roadmap, etc.)
- Choose appropriate agent for delegation
- Log conversations for proactive suggestions
- Track user requests (features, bugs, questions)
- Generate proactive suggestions based on history
- Learn from feedback via ACE

**Owned Files**:
- `docs/user_interpret/conversation_history.jsonl`
- `docs/user_interpret/user_requests.json`
- `docs/user_interpret/conversation_summaries.json`
- `docs/user_interpret/proactive_context.json`

**Can Read**: All conversation history, playbook

**Can Write**: Own docs only

**ACE**: ✅ Enabled (high volume, fast feedback)

**Intent Types**:
- `add_feature`: User wants to implement something
- `ask_how_to`: User wants to learn how to do something
- `view_roadmap`: User wants to see ROADMAP
- `report_bug`: User reports an issue
- `request_demo`: User wants to see a feature in action
- `code_search`: User wants to find code
- `check_status`: User wants project status
- `general_question`: General inquiry

**Sentiment Types**:
- `neutral`: No strong emotion
- `frustration`: User is frustrated
- `satisfaction`: User is happy
- `confusion`: User is unclear
- `impatience`: User wants faster response

**Example Traces**:
- "User said 'implement login' → Intent: add_feature, Delegate: code_developer"
- "User said 'ugh broken' → Intent: report_bug, Sentiment: frustration, Delegate: code_developer"

---

### architect

**Role**: Architectural design and technical specification

**Responsibilities**:
- Analyze architectural requirements
- Design system architecture
- Create detailed technical specifications
- Document architectural decisions (ADRs)
- Provide implementation guidelines
- Review implementation for architectural compliance
- Interact with user (through user_listener) on architectural topics

**Owned Files**:
- `docs/architecture/**` (all architectural documentation)
  - `docs/architecture/specs/` (technical specifications)
  - `docs/architecture/decisions/` (ADRs)
  - `docs/architecture/guidelines/` (implementation guidelines)

**Can Read**: All (for architectural context)

**Can Write**: docs/architecture/

**ACE**: ✅ Enabled (learns architectural patterns)

**Key Characteristics**:
- Works BEFORE code_developer (pre-implementation phase)
- Focuses on design, not implementation
- Creates specifications that code_developer follows
- Documents decisions for future reference
- Ensures architectural consistency

**Workflow Position**:
```
User Request
    ↓
user_listener (UI)
    ↓
architect (design & specs)
    ↓
code_developer (implementation)
    ↓
project_manager (verification & docs)
```

**Example Traces**:
- "Created caching layer spec with Redis architecture (45s, 1 file created)"
- "Documented ADR-015: PostgreSQL vs MongoDB decision (30s, 1 file created)"
- "Provided error handling guidelines for code_developer (20s, 1 file created)"

**Document Types**:
1. **Technical Specifications**: Detailed design for implementation
   - Location: `docs/architecture/specs/`
   - Audience: code_developer (primary)

2. **Architectural Decision Records (ADRs)**: Document key decisions
   - Location: `docs/architecture/decisions/`
   - Audience: All team members

3. **Implementation Guidelines**: Best practices for implementation
   - Location: `docs/architecture/guidelines/`
   - Audience: code_developer

---

### code_developer

**Role**: Implement features, fix bugs, create PRs

**Responsibilities**:
- Implement priorities from ROADMAP
- Write Python code (coffee_maker/, tests/, scripts/)
- Run tests (pytest)
- Create git tags (feature/us-XXX-start, feature/us-XXX-complete)
- Create PRs (gh pr create) **autonomously**
- Verify DoD with Puppeteer (during implementation)
- Update ROADMAP status (Planned → In Progress → Complete)
- Use tag-based workflow (NO branch switching)

**Owned Files**:
- `coffee_maker/**/*.py` (all Python code)
- `tests/**/*.py` (all tests)
- `scripts/**/*` (utility scripts)
- `pyproject.toml` (dependencies)
- `.claude/**/*` (technical configurations)
  - `.claude/agents/` (agent definitions and configurations)
  - `.claude/CLAUDE.md` (technical setup and implementation guide)
  - `.claude/commands/` (prompt templates)
  - `.claude/mcp/` (MCP server configurations)

**Can Read**: All (for context)

**Can Write**: coffee_maker/, tests/, scripts/, pyproject.toml, .claude/

**ACE**: ✅ Enabled (learns implementation patterns)

**CRITICAL**: Only ONE instance at a time!

**Git Workflow** (Tag-Based):
1. Verify on `roadmap` branch (ALWAYS)
2. Create start tag: `feature/us-033-name-start`
3. Implement feature
4. Commit with completion tag: `feature/us-033-name-complete`
5. Push with tags: `git push origin roadmap --tags`
6. Create PR: `gh pr create` (from roadmap branch)

**Example Traces**:
- "Implemented US-033 Streamlit app (180s, 5 files created)"
- "Fixed bug in roadmap_cli.py (45s, 1 file modified)"

**DoD Verification**:
- Use Puppeteer DURING implementation
- Navigate to http://localhost:8501
- Test acceptance criteria
- Capture screenshots for evidence
- Check console for errors

---

### project_manager

**Role**: Strategy, documentation, project health

**Responsibilities**:
- Manage ROADMAP (strategic decisions)
- Create/update technical specs
- Monitor GitHub (PRs, issues, CI/CD)
- Verify completed work (post-implementation, when user requests)
- Warn about blockers (via warn_user())
- Project health assessment
- NOT for creating PRs (code_developer does this)
- NOT for technical configurations in .claude/ (code_developer does this)

**Owned Files**:
- `docs/**/*.md` (all strategic documentation)
- `docs/roadmap/ROADMAP.md` (strategy only, not status)
- `docs/PRIORITY_*_TECHNICAL_SPEC.md`

**Can Read**: All

**Can Write**: docs/

**ACE**: ✅ Enabled (strategic decisions benefit from learning)

**Warning System**:
```python
from coffee_maker.cli.ai_service import AIService

service = AIService()
service.warn_user(
    title="🚨 BLOCKER: Technical spec review needed",
    message="US-021 waiting on spec approval. code_developer cannot proceed.",
    priority="critical",
    context={"priority": "US-021", "blocker_type": "spec_review"}
)
```

**Example Traces**:
- "Created technical spec for US-033 (30s, 1 file created)"
- "Updated ROADMAP strategic priorities (15s, 1 file modified)"

---

### assistant

**Role**: Answer questions, create demos, documentation expert

**Responsibilities**:
- Answer user questions
- Search codebase (simple, 1-2 files)
- Create demos (using Puppeteer via user_listener)
- Explain concepts
- Delegate complex analysis to code-searcher
- Read-only access to all docs
- **NEVER modifies code or docs** (always delegates)

**Owned Files**: None (read-only agent)

**Can Read**: All

**Can Write**: None

**ACE**: ✅ Enabled (learns better answers)

**Example Traces**:
- "Explained how ACE curator works (12s, no files)"
- "Searched for authentication code (8s, found in 3 files)"

---

### code-searcher

**Role**: Deep codebase analysis

**Responsibilities**:
- Security audits
- Dependency tracing
- Code reuse identification
- Pattern detection
- Architectural analysis
- Prepare findings (delegates to project_manager for docs)
- **NEVER writes docs directly** (always delegates)

**Owned Files**: None (prepares findings, doesn't write)

**Can Read**: All

**Can Write**: None (delegates to project_manager)

**ACE**: ✅ Enabled (learns better search patterns)

**Documentation Process**:
1. code-searcher analyzes code
2. Prepares findings
3. Presents to assistant
4. assistant delegates to project_manager
5. project_manager writes docs

**Document Format**: `docs/[analysis_type]_analysis_[date].md`

**Example Traces**:
- "Security audit identified 3 vulnerabilities (120s, no files)"
- "Traced dependency chain for auth module (45s, no files)"

---

### ux-design-expert

**Role**: Design decisions (provides specs, doesn't implement)

**Responsibilities**:
- All UI/UX decisions
- Tailwind CSS design specs
- Highcharts configurations
- Design systems
- Mockups and wireframes
- **Provides specs, doesn't implement** (code_developer implements)

**Owned Files**: None (provides specs, doesn't write code)

**Can Read**: All (for design context)

**Can Write**: None (code_developer writes implementation)

**ACE**: ✅ Enabled (learns design patterns)

**Example Traces**:
- "Created dashboard layout spec with Tailwind (30s, no files)"
- "Designed Highcharts configuration (15s, no files)"

---

### Generator (ACE)

**Role**: Observe agent executions, create traces

**Responsibilities**:
- Wrap agent executions
- Capture plan, difficulties, concerns
- Capture pre-execution state (git, files)
- Capture external observation (git changes, files)
- Capture internal observation (reasoning, tools, decisions)
- Conditional dual execution (if fast AND no files modified)
- Save comprehensive trace JSON/Markdown files

**Owned Files**:
- `docs/generator/traces/**/*.json`
- `docs/generator/traces/**/*.md`

**Can Read**: Agent execution context

**Can Write**: Own directory only

**ACE**: N/A (is part of ACE)

**Conditional Second Execution**:
- **Runs IF**: duration < 30s AND no owned files modified
- **Skips IF**: duration ≥ 30s OR files modified
- **Rationale**: Avoid duplicating expensive feature implementations

**Example Traces Generated**:
- `trace_1760510850655276.md`: user_interpret execution (2 executions, fast)
- `trace_1760520000000000.json`: code_developer execution (1 execution, long)

---

### Reflector (ACE)

**Role**: Extract insights from traces

**Responsibilities**:
- Analyze traces (batches of 5-10)
- Perform cross-trace pattern analysis
- Extract success patterns
- Identify failure modes
- Suggest optimizations
- Generate delta items with evidence
- Assign priority and confidence

**Owned Files**:
- `docs/reflector/deltas/**/*.json`

**Can Read**: Generator traces

**Can Write**: Own directory only

**ACE**: N/A (is part of ACE)

**Insight Types**:
- `success_pattern`: Strategy that consistently works
- `failure_mode`: Pattern that consistently fails
- `optimization`: Way to improve efficiency
- `best_practice`: General guideline
- `tool_usage`: Specific tool guidance
- `domain_concept`: Domain knowledge

**Example Deltas Generated**:
- "When user says 'implement', interpret as add_feature (confidence: 0.95)"
- "Sentiment analysis times out on messages > 500 chars (confidence: 0.85)"

---

### Curator (ACE)

**Role**: Maintain evolving playbooks

**Responsibilities**:
- Load deltas from reflector
- Load existing playbook
- Perform semantic de-duplication (OpenAI embeddings)
- Merge/update/add insights based on similarity
- Prune low-value bullets (helpful_count < 2 && pruned often)
- Enforce max size (150 bullets)
- Track playbook health metrics
- Suggest feedback questions to user_listener
- Record user feedback

**Owned Files**:
- `docs/curator/playbooks/**/*.json`
- `docs/curator/feedback/**/*.jsonl`

**Can Read**: Reflector deltas, feedback history

**Can Write**: Own directory only

**ACE**: N/A (is part of ACE)

**De-duplication Rules**:
- Similarity > 0.90: Merge as identical
- Similarity > 0.85: Consolidate if same category
- Similarity > 0.75: Update if delta more specific
- Similarity < 0.75: Keep separate

**Health Metrics**:
- `effectiveness_ratio`: helpful / (helpful + harmful)
- `coverage_score`: 0-1 (strategy space coverage)
- `avg_helpful_count`: Average helpfulness
- `bullets_added/updated/pruned`: Session changes

**Example Playbooks Managed**:
- `code_developer_playbook.json`: 147 bullets, effectiveness 0.92
- `user_interpret_playbook.json`: 47 bullets, effectiveness 0.88

---

## File Ownership Matrix

| Directory/File | Owner | Others |
|----------------|-------|--------|
| **User Interface** | user_listener | ❌ (ONLY user_listener has UI) |
| **coffee_maker/** | code_developer | READ-ONLY (all others) |
| **tests/** | code_developer | READ-ONLY |
| **scripts/** | code_developer | READ-ONLY |
| **pyproject.toml** | code_developer | READ-ONLY |
| **.claude/** | code_developer | READ-ONLY |
| **.claude/agents/** | code_developer | READ-ONLY |
| **.claude/CLAUDE.md** | code_developer | READ-ONLY (others) |
| **.claude/commands/** | code_developer | READ-ONLY (others load, don't modify) |
| **.claude/mcp/** | code_developer | READ-ONLY |
| **docs/** | project_manager | READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | READ-ONLY (others) |
| **docs/PRIORITY_*_TECHNICAL_SPEC.md** | project_manager | READ-ONLY |
| **docs/architecture/** | architect | READ-ONLY (all others) |
| **docs/user_interpret/** | user_interpret | READ-ONLY |
| **docs/generator/** | Generator (ACE) | READ-ONLY |
| **docs/reflector/** | Reflector (ACE) | READ-ONLY |
| **docs/curator/** | Curator (ACE) | READ-ONLY |

### Ownership Rules

1. **ONE OWNER** per file/directory
2. **Owner has WRITE access**
3. **Others have READ-ONLY access**
4. **Modifications require DELEGATION** to owner
5. **No exceptions** (prevents conflicts)

---

## Tool Ownership Matrix

| Tool/Capability | Owner | Usage | Others |
|----------------|-------|-------|--------|
| **User Interface (ALL)** | user_listener | ONLY agent with UI, chat, CLI | All others: Backend only, NO UI ❌ |
| **ACE UI Commands** | user_listener | `/curate`, `/playbook` in CLI | project_manager: Deprecated ❌ |
| **Architecture specs** | architect | Creates technical specifications before implementation | code_developer reads and implements |
| **ADRs (Architectural Decision Records)** | architect | Documents architectural decisions | All others: READ-ONLY |
| **Implementation guidelines** | architect | Provides detailed implementation guides | code_developer follows during implementation |
| **Puppeteer DoD (during impl)** | code_developer | Verify features DURING implementation | - |
| **Puppeteer DoD (post-impl)** | project_manager | Verify completed work on user request | - |
| **Puppeteer demos** | user_listener | Show features visually via UI (delegates to assistant) | assistant prepares demos |
| **GitHub PR create** | code_developer | Create PRs autonomously | project_manager: Monitoring only ❌ |
| **GitHub monitoring** | project_manager | Monitor PRs, issues, CI/CD status | - |
| **GitHub queries** | project_manager | All `gh` commands | user_listener delegates via UI |
| **Code editing** | code_developer | ALL code changes | assistant: READ-ONLY ❌ |
| **Code search (simple)** | assistant | 1-2 files with Grep/Read | user_listener delegates via UI |
| **Code search (complex)** | code-searcher | Deep analysis, patterns, forensics | user_listener delegates via UI |
| **Code analysis docs** | project_manager | Creates docs/[analysis]_[date].md | code-searcher prepares findings |
| **ROADMAP updates** | project_manager (full), code_developer (status only) | Strategic vs. execution updates | assistant: READ-ONLY ❌ |
| **Design decisions** | ux-design-expert | All UI/UX, Tailwind, charts | user_listener delegates via UI |
| **ACE observation** | Generator | Capture all agent executions | All agents: Observed by generator |
| **ACE reflection** | Reflector | Extract insights from traces | - |
| **ACE curation** | Curator | Maintain evolving playbooks | user_listener invokes via UI |

---

## Parallel Operations

### Safe Parallel Combinations

✅ **code_developer + project_manager**: Different files (code vs docs)
✅ **architect + project_manager**: Different directories (architecture vs strategic docs)
✅ **architect + code_developer**: Different directories (architect designs, code_developer implements different feature)
✅ **assistant + code-searcher**: Both read-only
✅ **user_listener + any backend agent**: UI separate from backend
✅ **Reflector + Generator**: Different directories
✅ **user_interpret + any agent**: user_interpret delegates, doesn't block
✅ **Multiple read-only agents**: assistant, code-searcher, etc.

### Unsafe Parallel Combinations

❌ **code_developer + code_developer**: Only ONE allowed! (file conflicts)
❌ **user_interpret + user_interpret**: Singleton agent (confusion)
❌ **architect + code_developer (same feature)**: architect must finish design first

### How to Ensure Safety

1. **Singleton Enforcement**: Only one code_developer instance at a time
2. **File Ownership**: Clear ownership prevents conflicts
3. **Read-Only Agents**: assistant, code-searcher never write
4. **Tag-Based Git**: No branch switching eliminates major conflict source
5. **Coordination**: Agents that share files must coordinate

---

## Git Strategy

### Tag-Based Workflow (NO Branch Switching!)

**🚨 CRITICAL: All agents work on `roadmap` branch - NEVER switch branches! 🚨**

### Why Tag-Based?

1. **Parallel Operations**: Multiple agents work simultaneously on `roadmap` branch
2. **No Branch Switching**: Eliminates major source of errors
3. **Single Source of Truth**: One CLAUDE.md, no synchronization needed
4. **Simpler Git State**: Easier to reason about
5. **File Ownership**: Each agent owns different files, no conflicts

### Tag Naming Convention

**code_developer uses tags**:
- Start: `feature/us-XXX-name-start`
- Complete: `feature/us-XXX-name-complete`
- Milestones: `feature/us-XXX-milestone-name`

**Other agents commit directly** to roadmap:
- No tags needed
- Just commit with descriptive message

### Example Workflow

```bash
# code_developer:
# 1. Verify on roadmap branch (CRITICAL)
git branch --show-current  # Must show: roadmap

# 2. Create start tag
git tag -a feature/us-033-streamlit-app-start -m "Start US-033"

# 3. Implement feature (commits on roadmap)
git add .
git commit -m "feat: Implement US-033 - Streamlit App"

# 4. Create completion tag
git tag -a feature/us-033-streamlit-app-complete -m "Complete US-033"

# 5. Push with tags
git push origin roadmap --tags

# 6. Create PR (from roadmap branch)
gh pr create --title "..." --body "..."

# project_manager:
# 1. Verify on roadmap branch
git branch --show-current  # Must show: roadmap

# 2. Make changes, commit
git add .
git commit -m "docs: Update ROADMAP (project_manager)"
git push origin roadmap
```

### Safety Checks

- **GitStrategy**: Module verifies roadmap branch before every operation
- **Daemon**: Automatically creates tags for features
- **Pre-commit hook**: Enforces roadmap branch (future)

### What NOT to Do

❌ **NEVER do this**:
```bash
git checkout -b feature/my-feature  # NO!
git checkout feature/branch         # NO!
git switch some-branch              # NO!
```

✅ **ALWAYS do this**:
```bash
# Always verify
git branch --show-current  # Should be: roadmap

# Use tags for milestones (handled by daemon)
# Tags are created automatically during implementation
```

---

## ACE Integration

### Which Agents Have ACE?

| Agent | ACE Enabled | Reason |
|-------|-------------|--------|
| user_listener | ❌ | UI only, no learning needed |
| user_interpret | ✅ | High volume, fast feedback |
| architect | ✅ | Learn architectural patterns |
| code_developer | ✅ | Learn implementation patterns |
| project_manager | ✅ | Learn strategic decisions |
| assistant | ✅ | Learn better answers |
| code-searcher | ✅ | Learn better search patterns |
| ux-design-expert | ✅ | Learn design patterns |

### ACE Workflow for Each Agent

Every agent with ACE enabled follows this flow:

```
1. User request → user_listener
2. user_interpret analyzes intent (ACE observes)
3. Delegates to appropriate agent
4. Generator wraps agent execution
5. Agent executes with playbook context
6. Generator captures trace
7. (Later) Reflector analyzes traces
8. Curator consolidates to playbook
9. Next execution uses updated playbook
```

### Playbook Usage

Each agent has its own playbook:
- `docs/curator/playbooks/code_developer_playbook.json`
- `docs/curator/playbooks/user_interpret_playbook.json`
- `docs/curator/playbooks/project_manager_playbook.json`
- etc.

Generator loads the appropriate playbook for each agent.

---

## Workflow Examples

### Example 1: User Asks for Feature

```
User: "Implement login feature"
    ↓
user_listener (UI)
    ↓
user_interpret
    ├─ Sentiment: neutral
    ├─ Intent: add_feature
    ├─ Agent: code_developer
    ├─ Log conversation (docs/user_interpret/)
    ├─ Track request (feature_20251015_143215)
    └─ Return: "I'll ask code_developer to implement this feature"
         ↓
user_listener delegates to code_developer
    ↓
code_developer (with ACE)
    ├─ Generator wraps execution
    ├─ Load playbook: code_developer_playbook.json
    ├─ Implement feature:
    │  ├─ Verify on roadmap branch ✅
    │  ├─ Create start tag: feature/us-035-login-start
    │  ├─ Read technical spec
    │  ├─ Write code (coffee_maker/auth/)
    │  ├─ Write tests (tests/test_auth.py)
    │  ├─ Verify DoD with Puppeteer
    │  ├─ Commit with completion tag
    │  ├─ Push with tags
    │  └─ Create PR: gh pr create
    ├─ Update ROADMAP status: Complete ✅
    └─ Generator saves trace (180s, 5 files created, no second execution)
         ↓
user_interpret marks request completed
    └─ result_location: /coffee_maker/auth/login.py
         ↓
Next time user_listener wakes up:
    └─ Shows proactive message:
        "✨ Hey! The feature you requested is ready: 'Login feature'
         Check it out at: /coffee_maker/auth/login.py
         PR: #42 (merged)"
```

### Example 2: User Asks Question

```
User: "How do I run tests?"
    ↓
user_listener (UI)
    ↓
user_interpret
    ├─ Sentiment: neutral
    ├─ Intent: ask_how_to
    ├─ Agent: assistant
    └─ Return: "I'll ask assistant to explain this"
         ↓
user_listener delegates to assistant
    ↓
assistant (with ACE)
    ├─ Generator wraps execution
    ├─ Load playbook: assistant_playbook.json
    ├─ Search docs for test info
    ├─ Format answer
    └─ Generator saves trace (8s, no files, second execution runs)
         ↓
user_listener shows answer
    └─ "To run tests: `poetry run pytest`"
```

### Example 3: Complex Delegation Chain

```
User: "I want to add a new dashboard feature"
    ↓
user_listener (UI)
    ↓
user_interpret
    ├─ Sentiment: neutral
    ├─ Intent: add_feature
    ├─ Complexity: high (requires design + implementation)
    └─ Return: "This requires multiple agents"
         ↓
user_listener coordinates:
    ↓
1. ux-design-expert (with ACE)
   ├─ Design dashboard layout
   ├─ Create Tailwind specs
   ├─ Create Highcharts config
   └─ Generator saves trace (30s, no files)
    ↓
2. project_manager (with ACE)
   ├─ Create technical spec
   ├─ Save to docs/PRIORITY_X_TECHNICAL_SPEC.md
   └─ Generator saves trace (20s, 1 file created)
    ↓
3. code_developer (with ACE)
   ├─ Implement dashboard
   ├─ Create PR
   └─ Generator saves trace (180s, 8 files created)
    ↓
user_listener synthesizes responses
    └─ "Dashboard implemented! PR: #43"
```

### Example 4: Feedback Loop

```
Scenario: user_interpret misinterprets intent
    ↓
1. User: "Show me the roadmap"
2. user_interpret (ACE observes)
   ├─ Intent: view_roadmap
   ├─ Delegate: project_manager
   └─ Trace saved
    ↓
3. project_manager shows ROADMAP
    ↓
4. user_listener asks feedback:
   "Was the intent interpretation accurate?"
    ↓
5. User: "Yes, correct!"
    ↓
6. FeedbackSuggestor.record_feedback()
   ├─ bullet_023.helpful_count++
   └─ Save to docs/curator/feedback/user_interpret_feedback.jsonl
    ↓
7. Next curation:
   ├─ bullet_023 has high helpful_count
   ├─ Not pruned
   └─ Confidence increased
```

---

## Summary

### Key Principles

1. **One Owner Per File**: Each file has ONE owner
2. **Read-Only for Others**: Non-owners can read but not modify
3. **No Branch Switching**: All agents work on `roadmap` branch
4. **Singleton Agents**: Only ONE instance of critical agents (code_developer)
5. **ACE by Default**: All agents learn continuously (except user_listener)
6. **UI Ownership**: user_listener is the ONLY agent with UI access

### Agent Responsibilities Summary

| Agent | Main Job | Owns | ACE |
|-------|----------|------|-----|
| user_listener | UI and delegation | No files (UI only) | ❌ |
| user_interpret | Intent + sentiment | docs/user_interpret/ | ✅ |
| architect | Architectural design & specs | docs/architecture/ | ✅ |
| code_developer | Implementation + PRs + Technical config | coffee_maker/, tests/, .claude/ | ✅ |
| project_manager | Strategy + docs | docs/ | ✅ |
| assistant | Questions + demos | None (read-only) | ✅ |
| code-searcher | Deep analysis | None (read-only) | ✅ |
| ux-design-expert | Design specs | None (provides specs) | ✅ |
| Generator | Observe executions | docs/generator/ | N/A |
| Reflector | Extract insights | docs/reflector/ | N/A |
| Curator | Maintain playbooks | docs/curator/ | N/A |

### Delegation Decision Tree

```
"Who should handle X?"
    ↓
Does user need a UI? → user_listener (ONLY agent with UI)
Is it about user intent? → user_interpret (delegates to others)
Is it architectural design? → architect
Is it about writing code? → code_developer
Is it about strategy/docs? → project_manager
Is it about design? → ux-design-expert
Is it about code analysis? → code-searcher
Is it a quick question? → assistant
Is it ACE curation? → user_listener (delegates to curator)
```

### File Modification Decision Tree

```
"Can I modify file X?"
    ↓
Am I the owner? → YES: Modify directly
    ↓ NO
Can I read it? → YES: Read for context, delegate to owner for modifications
    ↓ NO
Request access → Owner grants read access OR provides information
```

### Git Workflow Decision Tree

```
"How should I commit?"
    ↓
Am I code_developer?
    ↓ YES
    1. Verify on roadmap branch
    2. Create start tag
    3. Implement
    4. Commit with completion tag
    5. Push with tags
    6. Create PR
    ↓ NO
    1. Verify on roadmap branch
    2. Make changes
    3. Commit with descriptive message
    4. Push to roadmap
```

---

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Complete agent roles and boundaries documentation
