# Critical Functional Requirements - System Invariants

**Version**: 1.0
**Date**: 2025-10-16
**Status**: Active
**Owner**: project_manager

---

## Purpose

These are CRITICAL system rules that MUST be enforced at ALL times:
- Before implementations
- Before user stories
- Before user requests
- Before agent decisions

**Violations are NOT ALLOWED.** When detected, the system must:
1. Stop the violating action
2. Expose the problem to the user
3. Provide safe alternatives that respect boundaries

---

## Master Requirement: CFR-000

### CFR-000: PREVENT FILE CONFLICTS AT ALL COSTS

**Rule**: The system MUST NEVER allow file conflicts, inconsistencies, or corruption.

**Core Principle**:
AT ANY GIVEN MOMENT, for ANY file in the system:
- EXACTLY ZERO or ONE agent is writing to that file
- NEVER two or more agents writing to the same file
- NEVER two instances of same agent writing to same file

**Why This Is Critical**:

File conflicts cause:
1. **Data Corruption**: Two agents writing simultaneously → corrupted file
2. **Inconsistencies**: Partial writes from different sources → inconsistent state
3. **Lost Work**: One agent's changes overwrite another's → work lost
4. **Merge Conflicts**: Git conflicts that block progress
5. **System Failure**: Corrupted config files → system unusable

**Real-World Example**:
```
Time: 10:00:00.000
- code_developer instance 1: Writes line 10 of daemon.py
- code_developer instance 2: Writes line 10 of daemon.py (different content)
→ Result: daemon.py line 10 is corrupted (mixed content or overwritten)
→ Consequence: daemon.py won't run, syntax errors, system failure
```

**Prevention Mechanisms**:

All other CFRs exist to prevent this master requirement from being violated:

1. **CFR-001: Document Ownership Boundaries**
   - Ensures only ONE agent can modify any given file
   - If code_developer owns coffee_maker/, ONLY code_developer can write there
   - Other agents MUST delegate to code_developer for changes
   - **Prevents**: Two different agents writing to same file

2. **US-035: Singleton Agent Enforcement**
   - Ensures only ONE instance of each agent type runs at a time
   - If code_developer is running, no second code_developer instance can start
   - **Exception**: Agents that own NO files (assistant) can have multiple instances
   - **Prevents**: Two instances of same agent writing to same file

3. **US-038: File Ownership Enforcement (generator)**
   - generator checks ownership BEFORE any write operation
   - Blocks writes if violating ownership
   - Auto-delegates to correct owner
   - **Prevents**: Any agent accidentally writing to file it doesn't own

4. **US-039: Comprehensive CFR Enforcement**
   - Level 2, 3, 4 validation before actions
   - User notification when violations detected
   - Safe alternatives provided
   - **Prevents**: Any action that could lead to file conflicts

**Enforcement Strategy**:

```
Before ANY write operation:
    ↓
1. Check Singleton (US-035): Is another instance of this agent running?
   - If YES and agent owns files: BLOCK (prevent same-agent conflict)
   - If YES and agent owns NO files: ALLOW (safe - no conflicts possible)
   - If NO: Continue
    ↓
2. Check Ownership (US-038): Does this agent own this file?
   - If YES: Continue
   - If NO: BLOCK, auto-delegate to owner
    ↓
3. Check CFRs (US-039): Does this action violate any CFR?
   - If YES: BLOCK, expose to user with alternatives
   - If NO: Continue
    ↓
4. ALLOW write operation
```

**Singleton Exception - Agents That Own No Files**:

Some agents are READ-ONLY or delegation-only and own NO files:

| Agent | Owns Files? | Multiple Instances OK? | Why? |
|-------|-------------|------------------------|------|
| assistant | NO (only reads/delegates) | YES | Cannot cause file conflicts |
| user_listener | NO (only delegates) | YES | Cannot cause file conflicts |
| code-searcher | NO (only reads) | YES | Cannot cause file conflicts |
| code_developer | YES (.claude/, coffee_maker/, tests/) | NO | Could cause conflicts |
| project_manager | YES (docs/roadmap/) | NO | Could cause conflicts |
| architect | YES (docs/architecture/) | NO | Could cause conflicts |

**Rule**:
- If agent owns files: ENFORCE singleton (US-035)
- If agent owns NO files: Multiple instances OK (no conflict risk)

**Verification**:

Before allowing any agent to start:
```python
if agent.owns_files():
    # Enforce singleton - prevent file conflicts
    if AgentRegistry.is_registered(agent.type):
        raise AgentAlreadyRunningError(
            f"Agent '{agent.type}' already running. "
            f"Cannot start second instance - would risk file conflicts. "
            f"Stop existing instance first."
        )
else:
    # Agent owns no files, multiple instances safe
    # No singleton enforcement needed
    pass
```

**Monitoring**:

The system MUST monitor for file conflicts:
- Git detects uncommitted changes before pull
- File system watchers detect concurrent writes
- Lock files for critical operations
- Atomic operations where possible

**Recovery**:

If file conflict detected despite all safeguards:
1. STOP all agent operations immediately
2. Alert user to conflict
3. Provide conflict resolution tools
4. Log incident for reflector analysis
5. Update CFR enforcement to prevent recurrence

---

## CFR-001: Document Ownership Boundaries

**Purpose**: Implements CFR-000 by ensuring only ONE agent can modify any file.

**This CFR prevents**: Two different agents writing to the same file.

**Rule**: Each directory/file has EXACTLY ONE owner agent. Only the owner can modify.

### Ownership Matrix

| Directory/File | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| **User Interface** | user_listener | ONLY UI for all user interactions | All others: NO UI (backend only) |
| **docs/*.md** | project_manager | YES - Top-level files ONLY (not subdirectories) | All others: READ-ONLY |
| **docs/roadmap/** | project_manager | YES - Strategic planning ONLY | All others: READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | project_manager: Strategic, code_developer: Status only | All others: READ-ONLY |
| **docs/PRIORITY_*_STRATEGIC_SPEC.md** | project_manager | YES - Creates strategic specs | All others: READ-ONLY |
| **docs/architecture/** | architect | YES - Technical specs, ADRs, guidelines | All others: READ-ONLY |
| **docs/architecture/specs/** | architect | YES - Technical specifications | All others: READ-ONLY |
| **docs/architecture/decisions/** | architect | YES - ADRs (Architectural Decision Records) | All others: READ-ONLY |
| **docs/architecture/guidelines/** | architect | YES - Implementation guidelines | All others: READ-ONLY |
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
| **.claude/commands/** | code_developer | YES - Prompt templates | All others: READ-ONLY |
| **.claude/mcp/** | code_developer | YES - MCP configurations | All others: READ-ONLY |
| **.claude/CLAUDE.md** | code_developer | YES - Technical setup and implementation guide | All others: READ-ONLY |
| **coffee_maker/** | code_developer | YES - All implementation | All others: READ-ONLY |
| **tests/** | code_developer | YES - All test code | All others: READ-ONLY |
| **scripts/** | code_developer | YES - Utility scripts | All others: READ-ONLY |
| **.pre-commit-config.yaml** | code_developer | YES - Pre-commit hooks | All others: READ-ONLY |
| **data/user_interpret/** | user_interpret | YES - Operational data (conversation logs, etc.) | All others: READ-ONLY |

### Enforcement

**When**: Before any Write/Edit/NotebookEdit operation

**How**: generator checks ownership before allowing file modifications

**Action**: If violator != owner:
1. Block the action immediately
2. Auto-delegate to correct owner (generator orchestrates)
3. Log delegation trace for reflector analysis
4. Return result transparently to requesting agent

**Example Violations**:

project_manager tries to modify .claude/CLAUDE.md
code_developer tries to modify docs/roadmap/ROADMAP.md (strategic content)
assistant tries to modify coffee_maker/cli/roadmap_cli.py

**Safe Alternatives**:

project_manager delegates to code_developer for .claude/ changes
code_developer delegates to project_manager for ROADMAP strategic changes
assistant delegates to code_developer for code changes

---

## CFR-002: Agent Role Boundaries

**Purpose**: Implements CFR-000 by ensuring clear ownership and preventing confusion.

**This CFR prevents**: Role confusion leading to concurrent modifications.

**Rule**: Each agent has EXACTLY ONE primary role. NO overlaps allowed.

### Role Matrix

| Agent | Primary Role | Scope | Cannot Do |
|-------|-------------|-------|-----------|
| **user_listener** | User Interface (ONLY) | All user interactions, chat UI, CLI interface | Backend work, implementation, strategic planning |
| **project_manager** | Strategic Planning (WHAT/WHY) | ROADMAP management, strategic specs, GitHub monitoring | Technical design (HOW), implementation (DOING) |
| **architect** | Technical Design (HOW) | Technical specs, ADRs, architecture, dependencies | Strategic planning (WHAT/WHY), implementation (DOING) |
| **code_developer** | Implementation (DOING) | Code, tests, technical configs, PRs | Strategic planning, technical design |
| **assistant** | Demos + Documentation + Dispatch | Visual demos, bug reports, documentation expert, intelligent routing | Code/doc modifications (READ-ONLY) |
| **code-searcher** | Deep Code Analysis | Security audits, dependency tracing, refactoring analysis | Writing documentation (prepares findings only) |
| **ux-design-expert** | UI/UX Design | Design decisions, Tailwind CSS, visual specifications | Implementation (provides specs only) |
| **generator** | Ownership Enforcement + Trace Capture | Central enforcement point, auto-delegation, execution observation | Direct file modifications (orchestrates only) |
| **reflector** | Insight Extraction | Analyzes execution traces, identifies patterns | Direct actions (analytical only) |
| **curator** | Playbook Maintenance | Semantic de-duplication, effectiveness tracking | Direct actions (curation only) |

### Enforcement

**When**: Before delegating work to any agent

**How**: Check if requested work matches agent's primary role

**Action**: If action outside agent's role:
1. Block the request
2. Identify correct agent for the work
3. Redirect to appropriate agent
4. Notify user if ambiguous

**Example Violations**:

project_manager creates technical specifications (architect's role - HOW)
code_developer makes strategic ROADMAP decisions (project_manager's role - WHAT/WHY)
assistant implements features (code_developer's role - DOING)
architect implements code (code_developer's role - DOING)

**Safe Alternatives**:

project_manager defines strategic requirements → architect designs → code_developer implements
code_developer reports completion → project_manager updates strategic status
assistant analyzes bug → project_manager adds priority → architect designs → code_developer fixes
architect requests approval → user approves → code_developer adds dependency

---

## CFR-003: No Overlap - Documents

**Purpose**: Implements CFR-000 by ensuring no shared ownership creates conflict opportunities.

**This CFR prevents**: Ambiguous ownership leading to concurrent modifications.

**Rule**: No two agents can own the same directory/file. Ownership must be exclusive.

### Current Ownership (No Overlaps)

**Confirmed Exclusive Ownership**:
- docs/roadmap/ → project_manager ONLY
- docs/architecture/ → architect ONLY
- docs/generator/ → generator ONLY
- docs/reflector/ → reflector ONLY
- docs/curator/ → curator ONLY
- .claude/ → code_developer ONLY
- coffee_maker/ → code_developer ONLY
- tests/ → code_developer ONLY
- pyproject.toml → architect ONLY
- data/user_interpret/ → user_interpret ONLY

**No Shared Ownership Exists**

### Enforcement

**Source of Truth**: Ownership matrix in CFR-001 is authoritative

**Change Process**: Any proposed ownership change requires:
1. User approval
2. Update to CFR-001 ownership matrix
3. Update to .claude/CLAUDE.md
4. Update to generator's FileOwnership registry
5. Notification to all agents

**New Directory Creation**:
1. Must assign single owner before creation
2. Document in ownership matrix
3. Update generator's registry

**Violation Prevention**:
- Before creating new directory: Assign single owner
- Before user story involving new docs: Clarify ownership
- If ambiguous: Stop, ask user to decide owner

---

## CFR-004: No Overlap - Responsibilities

**Purpose**: Implements CFR-000 by ensuring clear role boundaries.

**This CFR prevents**: Responsibility confusion leading to concurrent work.

**Rule**: No two agents can have overlapping primary responsibilities.

### Responsibility Matrix (No Overlaps)

| Responsibility | Owner | Why Exclusive | Others Cannot |
|----------------|-------|---------------|---------------|
| **User Interface (ALL)** | user_listener | ONLY agent with UI/chat | All others: Backend only |
| **Strategic Specs (WHAT/WHY)** | project_manager | Business focus, strategic planning | architect: Cannot create strategic specs |
| **Technical Specs (HOW)** | architect | Technical expertise, architectural design | project_manager: Cannot create technical specs |
| **Implementation (DOING)** | code_developer | Coding skill, execution | All others: Cannot write code |
| **Dependency Management** | architect | Architecture decisions, requires user approval | code_developer: Cannot run poetry add |
| **Demos & Visual Tutorials** | assistant | Testing & QA, Puppeteer expertise | All others: Cannot create demos |
| **Bug Reporting** | assistant | Quality assurance, testing | All others: Cannot report bugs directly |
| **ROADMAP Strategic Management** | project_manager | Strategic planning | code_developer: Status updates only |
| **GitHub PR Creation** | code_developer | Autonomous implementation workflow | project_manager: Monitoring only |
| **GitHub Monitoring** | project_manager | Project health tracking | code_developer: Creates PRs only |
| **Ownership Enforcement** | generator | Central enforcement point, ACE framework | All others: Subject to enforcement |
| **Deep Code Analysis** | code-searcher | Forensic examination, security audits | assistant: Simple searches only |

### Enforcement

**When**: Before work assignment or delegation

**How**: Check responsibility matrix for exclusive ownership

**Action**: If overlap detected:
1. Escalate to user for clarification
2. Request explicit responsibility assignment
3. Update matrix with user approval only

**Violation Prevention**:
- User stories must clearly state which agent handles what
- If ambiguous responsibility: Stop, ask user to clarify
- Document new responsibilities explicitly in this matrix

---

## Enforcement Mechanisms

### Level 1: generator (ACE Framework) - PRIMARY ENFORCEMENT

**When**: Before EVERY action (Write/Edit/NotebookEdit)

**What**: Check file ownership and role appropriateness

**How**:
1. Intercept all file modification tool calls
2. Check FileOwnership registry for correct owner
3. Compare requesting agent vs. file owner
4. If mismatch: Auto-delegate to correct owner
5. If match: Allow action to proceed

**Action**:
- Block violations automatically
- Auto-delegate to correct agent (transparent)
- Log delegation trace for reflector analysis
- Return result to requesting agent as if they did it

**Reference**: US-038 (generator ownership enforcement implementation)

### Level 2: User Story Validation

**When**: Before adding user story to ROADMAP

**What**: Check if user story violates ownership/role boundaries

**How**:
1. Parse user story requirements
2. Identify which agents would be involved
3. Check against ownership matrix (CFR-001)
4. Check against role matrix (CFR-002)
5. Verify no overlaps (CFR-003, CFR-004)

**Action**: If violation detected:
1. Stop user story creation
2. Expose problem to user with clear explanation
3. Suggest alternatives that respect boundaries
4. Wait for user decision

### Level 3: User Request Validation

**When**: User makes a request to any agent

**What**: Check if request would violate boundaries

**How**:
1. Analyze user request intent
2. Identify required actions and agents
3. Check against CFR rules
4. Verify all actions respect boundaries

**Action**: If violation detected:
1. Explain problem clearly to user
2. Offer safe alternatives
3. Recommend correct delegation path
4. Wait for user confirmation

### Level 4: Agent Self-Check

**When**: Agent plans work

**What**: Agent verifies it owns the files and has the role

**How**:
1. Before starting work, check ownership matrix
2. Verify agent owns target files
3. Verify work matches agent's primary role
4. If uncertain, consult CFR rules

**Action**: If violation detected:
1. Do NOT execute the work
2. Delegate to correct agent instead
3. Report to user if critical

---

## Task Delegation Tool

**Purpose**: All agents use a delegation tool instead of directly calling other agents.

**How It Works**:
1. Agent needs work done outside its boundaries
2. Agent calls: `delegate_task(task_description, context)`
3. Delegation tool → generator
4. generator analyzes task, checks CFRs, decides routing
5. generator delegates to appropriate agent(s)
6. Result returns to requesting agent

**Benefits**:
- Centralized routing through generator (ACE framework)
- Automatic CFR checking before delegation
- Consistent delegation patterns
- Traceability for reflector/curator

**Example**:
```python
# ❌ DON'T: Direct agent-to-agent call
result = code_developer.implement_feature(feature)

# ✅ DO: Use delegation tool
result = delegate_task(
    task="Implement feature X",
    context={"feature_spec": spec, "priority": "high"},
    requesting_agent="project_manager"
)
# → generator routes to code_developer
```

**Integration**:
- All agents have access to delegation tool
- generator is central orchestrator (ACE framework)
- Delegation traces captured for learning

---

## Complexity Escalation Workflow

**When to Escalate**: Agent faces complexity that makes it hard to respect CFRs.

**Escalation Chain**:
```
Agent (complexity detected)
    ↓
    Escalates to project_manager
    ↓
project_manager (strategic simplification)
    ↓ (if still complex)
    Escalates to architect
    ↓
architect (technical simplification)
    ↓ (if still complex)
    Escalates to user
    ↓
User (final decision)
```

### Example 1: Agent Faces Complexity

**Scenario**: code_developer needs to implement feature that requires modifying both .claude/ (owned) and docs/roadmap/ (not owned).

**Step 1: code_developer recognizes complexity**
- "I need to modify docs/roadmap/ROADMAP.md but I don't own it"
- "This violates CFR-001"

**Step 2: code_developer escalates to project_manager**
```
Message to project_manager:
"I'm implementing US-040 and need to update ROADMAP.md to mark completion.
However, ROADMAP.md is owned by you (CFR-001).

Options I see:
1. Delegate ROADMAP update to you
2. Create a different mechanism to track completion
3. Request temporary access (violates CFR)

The complexity: I need ROADMAP updates synchronized with code changes.

Can you help simplify this approach while respecting CFR-001?"
```

**Step 3: project_manager analyzes and simplifies**
```
Response from project_manager:
"Use delegation approach (Option 1):
1. You implement feature
2. You commit code
3. You delegate to me: 'Mark US-040 complete in ROADMAP'
4. I update ROADMAP.md
5. I commit ROADMAP change

This respects CFR-001 (ownership boundaries) and is simple.
Proceed with implementation."
```

**Result**: Complexity resolved, CFRs respected.

### Example 2: project_manager Escalates to architect

**Scenario**: project_manager receives escalation but needs technical guidance.

**Step 1: project_manager receives complexity escalation**
From code_developer: "US-041 requires architectural changes I'm not sure how to approach"

**Step 2: project_manager escalates to architect**
```
Message to architect:
"code_developer is implementing US-041 (multi-tenant architecture).
They're unsure how to structure the code to respect:
- CFR-002 (role boundaries - implementation is their role)
- But they need architectural guidance on approach

Can you create a technical specification that:
1. Provides clear architectural design
2. Allows code_developer to implement within their role
3. Respects all CFRs

Or should we escalate to user for guidance?"
```

**Step 3: architect provides technical simplification**
```
Response from architect:
"I'll create docs/architecture/user_stories/US_041_TECHNICAL_SPEC.md with:
- Clear architectural design (my role)
- Implementation guidelines for code_developer
- Respects CFR-002 (I design, they implement)

No user escalation needed. I'll have spec ready in 2 hours."
```

**Result**: Complexity resolved at architect level.

### Example 3: Escalation to User

**Scenario**: Both project_manager and architect cannot resolve without breaking CFRs.

**Step 1: architect recognizes fundamental conflict**
```
Message to project_manager:
"US-042 requires changes to ownership boundaries:
- Feature needs docs in both docs/roadmap/ and docs/architecture/
- Current ownership: separate (you + me)
- Options:
  1. Split feature across both directories (complex coordination)
  2. Create new shared directory (violates CFR-003: no overlap)
  3. Change ownership boundaries (needs user approval)

I cannot simplify this without user decision."
```

**Step 2: project_manager escalates to user**
```
Message to user:
"⚠️ COMPLEXITY ESCALATION - User Decision Needed

Feature: US-042 (Unified Documentation System)

Conflict: Requires documentation that spans strategic and technical boundaries.

Current CFR: CFR-003 (No Overlap - Documents)
- docs/roadmap/ → project_manager only
- docs/architecture/ → architect only
- No shared ownership allowed

Options:
1. Split feature: Strategic docs in roadmap/, technical docs in architecture/
   - Pros: Respects CFRs
   - Cons: Complex coordination, documentation fragmented

2. Create new shared directory: docs/unified/
   - Pros: Simpler, documentation centralized
   - Cons: VIOLATES CFR-003 (would need two owners)

3. Assign unified docs to one owner (architect or project_manager)
   - Pros: Respects CFRs, single owner
   - Cons: One agent does work outside typical role

4. Redesign feature to avoid cross-boundary documentation
   - Pros: Respects all CFRs
   - Cons: May change feature significantly

Which option do you prefer?"
```

**Step 3: User decides**
User chooses Option 3: "Assign unified docs to architect since it's primarily technical documentation"

**Step 4: CFRs updated (with user approval)**
- Update CRITICAL_FUNCTIONAL_REQUIREMENTS.md
- docs/unified/ → architect (single owner, respects CFR-003)
- Notify all agents of boundary change

**Result**: Complexity resolved with user decision, CFRs maintained.

### Escalation Guidelines

**When to Escalate**:
- ✅ Agent cannot complete task without violating CFR
- ✅ Multiple approaches all violate CFRs
- ✅ Unclear which agent owns responsibility
- ✅ Fundamental conflict between CFRs and requirements

**When NOT to Escalate**:
- ❌ Agent simply doesn't want to delegate
- ❌ Solution is obvious (just needs delegation)
- ❌ Agent hasn't tried to find CFR-respecting approach
- ❌ Trying to shortcut proper workflows

**Escalation Message Format**:
```
COMPLEXITY ESCALATION

From: [Agent Name]
To: [project_manager or architect]

Task: [What I'm trying to do]

Complexity: [Why it's hard to respect CFRs]

CFRs Involved: [Which CFRs are at risk]

Options I've Considered:
1. [Option 1] - Why it violates/doesn't work
2. [Option 2] - Why it violates/doesn't work
3. [Option 3] - Why it violates/doesn't work

Request: [What guidance/decision I need]
```

### Benefits of Escalation Workflow

**For Agents**:
- Clear path when stuck
- No need to violate CFRs
- Expert guidance available

**For project_manager**:
- Visibility into complexity
- Opportunity to simplify strategically
- Control over CFR exceptions

**For architect**:
- Can provide technical guidance
- Ensures clean architectural decisions
- Prevents technical debt from workarounds

**For Users**:
- Only involved when truly needed
- Clear options presented
- Final authority on CFR changes

---

## Violation Response Workflow

### Step 1: Detect Violation

**Example**: project_manager attempts to modify .claude/CLAUDE.md

**Detection Point**: generator intercepts Edit tool call

### Step 2: Stop Action

Block the file modification immediately

**No partial execution** - violation prevents action entirely

### Step 3: Analyze Violation

Questions to answer:
- What was attempted? (Edit .claude/CLAUDE.md)
- Who attempted it? (project_manager)
- Who should do it instead? (code_developer - owner of .claude/)
- Why is this a problem? (Violates CFR-001 document ownership)

### Step 4: Choose Response Path

**Option A: Auto-Delegate (generator does this automatically)**
- generator delegates to code_developer
- code_developer executes Edit on .claude/CLAUDE.md
- Result returned to project_manager transparently
- Violation prevented, work completed
- Delegation trace logged for reflector

**Option B: Expose to User (for ambiguous cases)**
- Create user notification with warning
- Explain the violation clearly
- Provide options for user to choose
- Wait for user decision

### Step 5: Expose to User (Option B Only)

**Message Format**:
```
OWNERSHIP VIOLATION DETECTED

project_manager attempted to modify:
  .claude/CLAUDE.md

Owner of this file:
  code_developer

This violates CFR-001 (Document Ownership Boundaries).

Options:
1. Auto-delegate to code_developer (recommended)
2. Cancel this action
3. Review ownership matrix: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md

Which option do you choose?
```

### Step 6: User Decides (Option B Only)

**Option 1: Delegate**
- generator delegates to code_developer
- code_developer makes the change
- Violation prevented

**Option 2: Cancel**
- Action cancelled
- No changes made
- User informed

**Option 3: Review**
- Show ownership matrix
- Explain CFR rules
- Return to Step 5

### Step 7: Execute Safe Alternative

**If auto-delegation (Option A or user chooses Option 1)**:
1. generator delegates to correct owner
2. Owner executes the action
3. Result returned to requesting agent
4. Delegation trace logged
5. Work completed successfully

**Why This Works**:
- Violations automatically corrected
- Work still gets done
- Ownership boundaries respected
- System learns from delegation patterns
- No manual intervention needed (usually)

---

## Safe Alternative Patterns

### Pattern 1: Delegation Chain

**Instead of**: Agent A violating to modify file owned by Agent B

**Do**: Agent A → generator → Agent B (owner) → modifies file

**Example**:
```
project_manager needs to update .claude/CLAUDE.md
    ↓
generator intercepts Edit tool call
    ↓
generator delegates to code_developer (owner)
    ↓
code_developer executes Edit on .claude/CLAUDE.md
    ↓
Result returned to project_manager
    ✅ Ownership respected, work completed
```

### Pattern 2: Multi-Agent Workflow

**Instead of**: One agent doing work outside its role

**Do**: Workflow across agents respecting role boundaries

**Example**:
```
User: "Add authentication feature"
    ↓
project_manager: Creates strategic spec (WHAT/WHY)
    → docs/roadmap/PRIORITY_X_STRATEGIC_SPEC.md
    ↓
architect: Creates technical spec (HOW)
    → docs/architecture/user_stories/US_X_TECHNICAL_SPEC.md
    ↓
code_developer: Implements feature (DOING)
    → coffee_maker/auth/*.py
    ✅ Each agent in their role
```

### Pattern 3: Request Decomposition

**Instead of**: User request that would violate boundaries

**Do**: Decompose into sub-tasks, each within boundaries

**Example**:
```
User: "Implement feature X and update ROADMAP"
    ↓
Decompose into:
  1. code_developer: Implement feature (implementation)
  2. project_manager: Update ROADMAP (strategic docs)
    ↓
Each sub-task respects boundaries
    ✅ No violations
```

### Pattern 4: Cross-Agent Communication

**Instead of**: Agent A modifying Agent B's files

**Do**: Agent A provides input → Agent B makes changes

**Example**:
```
assistant finds bug during demo
    ↓
assistant analyzes bug comprehensively (root cause, requirements)
    ↓
assistant reports to project_manager (with full analysis)
    ↓
project_manager adds priority to ROADMAP
    ↓
architect designs fix based on assistant's analysis
    ↓
code_developer implements fix using architect's design
    ↓
assistant retests to verify fix
    ✅ Each agent in their role, no file ownership violations
```

### Pattern 5: Ownership Transfer Request

**Instead of**: Forcing change with current ownership

**Do**: Request ownership transfer with user approval

**Example**:
```
New requirement: code_developer needs to own docs/tutorials/
    ↓
agent requests ownership change
    ↓
Expose to user:
  "Ownership change requested:
   - File: docs/tutorials/
   - Current owner: project_manager
   - Requested owner: code_developer
   - Reason: [explanation]

   Approve ownership transfer?"
    ↓
User decides:
  Option 1: Approve → Update CFR-001, CLAUDE.md, generator registry
  Option 2: Deny → Keep current ownership, find alternative
    ✅ User controls ownership boundaries
```

---

## Updating These Requirements

### Process

1. **Proposal**: Any agent or user proposes change
2. **Review**:
   - project_manager: Strategic impact assessment
   - architect: Technical feasibility assessment
   - generator: Enforcement implementation impact
3. **User Approval**: REQUIRED for any CFR changes
4. **Documentation Update**:
   - Update this document (CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
   - Update .claude/CLAUDE.md ownership matrix
   - Update generator's FileOwnership registry
   - Update agent configurations if needed
5. **Notification**: Notify all agents of change
6. **Verification**: Test enforcement with new rules

### Restrictions

CANNOT do without user approval:
- Remove CFRs
- Weaken enforcement mechanisms
- Create ownership overlaps
- Create role overlaps
- Change ownership assignments
- Disable auto-delegation

CAN do with agent consensus:
- Add new enforcement mechanisms
- Clarify ambiguous rules
- Add examples and patterns
- Improve violation detection
- Enhance logging and observability

### Change Log

All CFR changes must be documented here:

**Version 1.0** (2025-10-16):
- Initial creation
- Defined CFR-001 through CFR-004
- Established enforcement mechanisms
- Documented violation response workflow
- Created safe alternative patterns

---

## Integration with Existing Systems

### US-038: generator Ownership Enforcement

**Status**: Planned

**Purpose**: Implement Level 1 enforcement (generator auto-delegation)

**How CFRs Support US-038**:
- CFR-001 defines ownership matrix (source of truth)
- CFR-002 defines role boundaries
- CFR-003 ensures no ownership overlaps
- CFR-004 ensures no role overlaps
- Enforcement mechanisms specify generator's responsibilities

**US-038 Must Implement**:
1. FileOwnership registry based on CFR-001
2. Automatic ownership checking before file operations
3. Auto-delegation to correct owner when violations detected
4. Delegation trace logging for reflector
5. Transparent result passing to requesting agent

### US-035: Singleton Agent Enforcement

**Status**: Planned

**Purpose**: Ensure agents are singletons (one instance per agent type)

**How CFRs Support US-035**:
- CFR-002 defines exclusive agent roles
- CFR-004 ensures no role overlaps
- Singleton enforcement prevents multiple instances competing

**US-035 Must Respect CFRs**:
- Each agent type has exactly ONE instance
- Each instance has exactly ONE primary role
- No role overlap between instances

### TEAM_COLLABORATION.md

**Purpose**: Defines how agents work together

**How CFRs Support Collaboration**:
- CFR-001/003: Clear file ownership prevents conflicts
- CFR-002/004: Clear role boundaries prevent overlap
- Enforcement mechanisms: Automatic violation prevention
- Safe patterns: Proven delegation workflows

**TEAM_COLLABORATION.md Must Reference CFRs**:
- Link to this document for detailed rules
- Use safe alternative patterns for workflows
- Explain enforcement mechanisms
- Document violation response process

### .claude/CLAUDE.md

**Purpose**: Project instructions and ownership matrix

**How CFRs Support CLAUDE.md**:
- CFR-001 ownership matrix is authoritative source
- CLAUDE.md references CFRs for detailed rules
- Keeps ownership documentation in sync

**CLAUDE.md Must Match CFRs**:
- Ownership matrix identical to CFR-001
- Tool ownership aligned with CFR-002
- No conflicting information

---

## Examples of CFR Enforcement

### Example 1: Auto-Delegation (Success)

**Scenario**: project_manager needs to update .claude/CLAUDE.md with new agent information

**Flow**:
```
1. project_manager calls Edit tool:
   Edit(.claude/CLAUDE.md, old_string, new_string)

2. generator intercepts Edit call
   - Checks FileOwnership registry
   - Finds: .claude/ owned by code_developer
   - Detects: Requesting agent (project_manager) != owner (code_developer)

3. generator auto-delegates
   - Logs: "Ownership violation - auto-delegating to code_developer"
   - Calls code_developer with same Edit parameters

4. code_developer executes Edit
   - Modifies .claude/CLAUDE.md successfully
   - Returns success status

5. generator captures delegation trace
   - Violating agent: project_manager
   - Correct owner: code_developer
   - File: .claude/CLAUDE.md
   - Operation: Edit
   - Result: Success
   - Timestamp: 2025-10-16 14:23:45

6. generator returns success to project_manager
   - project_manager receives result as if it did the edit
   - Transparent delegation (no manual intervention needed)

RESULT:
✅ File updated correctly
✅ Ownership respected
✅ Violation prevented
✅ Delegation trace logged for learning
```

### Example 2: User Request Validation (Prevention)

**Scenario**: User asks assistant to implement new feature

**Flow**:
```
1. User: "Implement the new authentication feature"

2. assistant analyzes request
   - Required action: Implement code
   - Checks CFR-002: assistant's role is Demos + Documentation + Dispatch
   - Checks CFR-002: code_developer's role is Implementation
   - Detects: assistant cannot implement code (READ-ONLY)

3. assistant explains to user
   "I can't implement code directly (CFR-002: Role Boundaries).
    I'll delegate to code_developer who handles all implementation.

    Would you like me to:
    1. Delegate to code_developer to implement the feature
    2. Have project_manager create a strategic spec first
    3. Show you the current authentication system"

4. User chooses Option 2

5. assistant delegates to project_manager
   - project_manager creates strategic spec (WHAT/WHY)
   - architect creates technical spec (HOW)
   - code_developer implements (DOING)

RESULT:
✅ Violation prevented before occurring
✅ User educated about boundaries
✅ Correct delegation path followed
```

### Example 3: User Story Validation (Early Detection)

**Scenario**: User proposes user story that violates boundaries

**Flow**:
```
1. User: "Create US-040: project_manager should refactor the CLI code"

2. project_manager analyzes user story
   - Required action: Modify code in coffee_maker/cli/
   - Checks CFR-001: coffee_maker/ owned by code_developer
   - Checks CFR-002: project_manager's role is Strategic Planning
   - Checks CFR-002: code_developer's role is Implementation
   - Detects: TWO violations:
     a. Document ownership (project_manager can't modify coffee_maker/)
     b. Role boundary (project_manager can't do implementation)

3. project_manager warns user
   "⚠️ USER STORY VIOLATION DETECTED

   US-040 proposes: project_manager refactors CLI code

   Violations:
   1. CFR-001: coffee_maker/ owned by code_developer (NOT project_manager)
   2. CFR-002: Implementation is code_developer's role (NOT project_manager)

   Safe Alternatives:
   Option 1: project_manager creates strategic requirement
             → architect designs refactoring plan
             → code_developer implements refactoring

   Option 2: project_manager identifies refactoring needs
             → code_developer analyzes and implements

   Option 3: Rewrite US-040 to assign work correctly

   Which approach do you prefer?"

4. User chooses Option 1

5. project_manager creates corrected user story:
   "US-040: Refactor CLI code for better maintainability
    - project_manager: Define strategic requirements (WHAT/WHY)
    - architect: Design refactoring approach (HOW)
    - code_developer: Implement refactoring (DOING)

    Each agent in their role ✅"

RESULT:
✅ Violation prevented at user story level
✅ User story corrected before implementation
✅ Clear delegation path established
```

### Example 4: Ownership Conflict Resolution (User Decision Required)

**Scenario**: Two agents both claim to need ownership of new directory

**Flow**:
```
1. New requirement: Create docs/performance/ directory

2. Two agents claim need:
   - architect: "I need to document performance requirements (technical)"
   - project_manager: "I need to track performance metrics (strategic)"

3. System detects potential overlap
   - CFR-003: No two agents can own same directory
   - Both claims are valid in their context
   - Ambiguous situation

4. System escalates to user
   "⚠️ OWNERSHIP CONFLICT - USER DECISION REQUIRED

   New directory: docs/performance/

   Competing claims:
   1. architect: Technical performance specifications
      - Rationale: Architecture-level performance design
      - Would contain: Technical benchmarks, optimization guides

   2. project_manager: Strategic performance tracking
      - Rationale: Project-level performance monitoring
      - Would contain: Performance metrics, tracking reports

   CFR-003 requires exclusive ownership.

   Options:
   A. Split into two directories:
      - docs/architecture/performance/ (architect)
      - docs/roadmap/performance_tracking/ (project_manager)

   B. Assign single owner, other agent delegates:
      - docs/performance/ → architect (project_manager delegates)
      - docs/performance/ → project_manager (architect delegates)

   C. Create hybrid approach (requires CFR update)

   Which approach do you prefer?"

5. User chooses Option A (split directories)

6. System implements decision
   - Create docs/architecture/performance/ (owner: architect)
   - Create docs/roadmap/performance_tracking/ (owner: project_manager)
   - Update CFR-001 with new directories
   - Update generator's FileOwnership registry
   - Notify both agents

RESULT:
✅ Ownership conflict resolved
✅ CFR-003 maintained (no overlap)
✅ Both agents can work independently
✅ User made informed decision
```

---

## Conclusion

These Critical Functional Requirements are SYSTEM INVARIANTS:

✅ MUST be enforced at all times
✅ MUST be checked before any action
✅ MUST stop violations and provide alternatives
✅ CANNOT be bypassed without user approval

**Violation = System Failure**

When in doubt:
1. STOP
2. CHECK OWNERSHIP (CFR-001)
3. CHECK ROLE (CFR-002)
4. CHECK FOR OVERLAPS (CFR-003, CFR-004)
5. DELEGATE APPROPRIATELY

---

## Quick Reference: Master Rule

**MASTER RULE: CFR-000 - NEVER ALLOW FILE CONFLICTS**

Before ANY write operation, verify:
- No other instance of this agent running (US-035) - IF agent owns files
- This agent owns the file being written (US-038)
- No CFR violations would occur (US-039)

If ANY check fails: STOP, delegate, or escalate.

**Why This Matters**: File conflicts cause corruption, data loss, system failure.

---

## Quick Reference: What to Do When...

### I need another agent to do work
→ Use delegation tool: `delegate_task(description, context)`
→ generator routes to appropriate agent

### I can't complete task without violating CFR
→ Escalate to project_manager with:
  - Task description
  - CFR conflict
  - Options considered
→ project_manager helps simplify or escalates further

### I'm project_manager and receive escalation
→ Analyze: Can I simplify strategically?
→ If yes: Provide simplified approach
→ If no: Escalate to architect (technical complexity)
→ If architect can't resolve: Escalate to user

### I'm architect and receive escalation
→ Analyze: Can I simplify technically?
→ If yes: Create technical spec or guidelines
→ If no: Return to project_manager for user escalation

### I'm user and receive escalation
→ Review options presented
→ Choose option that:
  - Meets business needs
  - Respects CFRs (or explicitly approves exception)
  - Is sustainable long-term
→ Make final decision

---

## Quick Reference: Violation Detection

**File Ownership Violated?** → generator auto-delegates to correct owner (CFR-001)

**Role Boundary Violated?** → Stop, redirect to correct agent (CFR-002)

**Ownership Overlap Detected?** → Escalate to user for resolution (CFR-003)

**Role Overlap Detected?** → Escalate to user for clarification (CFR-004)

**User Story Violates CFRs?** → Warn user, suggest safe alternatives

**Ambiguous Situation?** → Stop, ask user to decide

**Need to Change CFRs?** → Requires user approval + documentation update

---

**Remember**: These CFRs exist to prevent the system from breaking itself. They are not optional. They are not suggestions. They are CRITICAL FUNCTIONAL REQUIREMENTS.

**Version**: 1.2
**Last Updated**: 2025-10-16
**Next Review**: After US-038 and US-039 implementation

**Changelog**:
- **v1.2** (2025-10-16): Added CFR-000 (MASTER REQUIREMENT) - Prevent File Conflicts At All Costs
  - All other CFRs now explicitly derive from CFR-000
  - Documented singleton exception for agents that own no files
  - Added enforcement strategy with 4-level checks
  - Updated Quick Reference with master rule
- **v1.1** (2025-10-16): Added Task Delegation Tool, Complexity Escalation Workflow, Enhanced Quick Reference
- **v1.0** (2025-10-16): Initial creation with CFR-001 through CFR-004, enforcement mechanisms
