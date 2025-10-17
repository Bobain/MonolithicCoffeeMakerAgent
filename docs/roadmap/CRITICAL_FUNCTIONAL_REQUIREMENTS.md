# Critical Functional Requirements - System Invariants

**Version**: 2.2
**Date**: 2025-10-17
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

### Ownership Matrix (with Maintenance Responsibilities - CFR-005)

| Directory/File | Owner | Can Modify? | Maintenance Duties (CFR-005) | Others |
|----------------|-------|-------------|------------------------------|--------|
| **User Interface** | user_listener | ONLY UI for all user interactions | N/A (no files owned) | All others: NO UI (backend only) |
| **docs/*.md** | project_manager | YES - Top-level files ONLY (not subdirectories) | Keep current, remove obsolete, simplify | All others: READ-ONLY |
| **docs/roadmap/** | project_manager | YES - Strategic planning ONLY | Archive completed work, consolidate specs, keep ROADMAP organized | All others: READ-ONLY |
| **docs/roadmap/learnings/** | project_manager | YES - Capture all lessons | Maintenance: Create monthly summaries, archive old lessons, update agent definitions | All others: READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | project_manager: Strategic, code_developer: Status only | Archive old priorities, simplify structure | All others: READ-ONLY |
| **docs/PRIORITY_*_STRATEGIC_SPEC.md** | project_manager | YES - Creates strategic specs | Remove obsolete specs, consolidate duplicates | All others: READ-ONLY |
| **docs/architecture/** | architect | YES - Technical specs, ADRs, guidelines | Archive old ADRs, update specs, organize directories, monitor code quality weekly | All others: READ-ONLY |
| **docs/architecture/specs/** | architect | YES - Technical specifications | Update with system changes, archive superseded | All others: READ-ONLY |
| **docs/architecture/decisions/** | architect | YES - ADRs (Architectural Decision Records) | Archive superseded ADRs, keep organized | All others: READ-ONLY |
| **docs/architecture/guidelines/** | architect | YES - Implementation guidelines | Remove obsolete, update for current practices | All others: READ-ONLY |
| **docs/architecture/refactoring/** | architect | YES - Refactoring plans | Clean up completed plans, organize by date | All others: READ-ONLY |
| **docs/generator/** | generator | YES - Execution traces | Rotate trace files, archive old, summarize | All others: READ-ONLY |
| **docs/reflector/** | reflector | YES - Delta items (insights) | Archive old deltas, consolidate similar insights | All others: READ-ONLY |
| **docs/curator/** | curator | YES - Playbooks and curation | Prune duplicates, remove low-effectiveness patterns | All others: READ-ONLY |
| **docs/code-searcher/** | project_manager | YES - Code analysis documentation | Archive old analyses, organize by type | code-searcher: Prepares findings (READ-ONLY) |
| **docs/templates/** | project_manager | YES - Documentation templates | Update templates, keep aligned with practices | All others: READ-ONLY |
| **docs/tutorials/** | project_manager | YES - Tutorial content | Update examples, verify links work | All others: READ-ONLY |
| **docs/user_interpret/** | project_manager | YES - Meta-docs about user_interpret | Keep current with user_interpret changes | All others: READ-ONLY |
| **docs/code_developer/** | project_manager | YES - Meta-docs about code_developer | Keep current with code_developer changes | All others: READ-ONLY |
| **pyproject.toml** | architect | YES - Dependency management (requires user approval) | Review dependencies periodically, remove unused | All others: READ-ONLY |
| **poetry.lock** | architect | YES - Dependency lock file | Keep synchronized with pyproject.toml | All others: READ-ONLY |
| **.claude/** | code_developer | YES - Technical configurations | Update CLAUDE.md, keep configs current | All others: READ-ONLY |
| **.claude/agents/** | code_developer | YES - Agent configurations | Update agent definitions as roles evolve | All others: READ-ONLY |
| **.claude/commands/** | code_developer | YES - Prompt templates | Update prompts, remove obsolete | All others: READ-ONLY |
| **.claude/mcp/** | code_developer | YES - MCP configurations | Keep MCP configs current | All others: READ-ONLY |
| **.claude/CLAUDE.md** | code_developer | YES - Technical setup and implementation guide | Update as system evolves, keep accurate | All others: READ-ONLY |
| **coffee_maker/** | code_developer | YES - All implementation | Refactor complex code (when architect requests), remove unused code, update comments | All others: READ-ONLY |
| **tests/** | code_developer | YES - All test code | Organize test files, clean up temp files, maintain coverage | All others: READ-ONLY |
| **scripts/** | code_developer | YES - Utility scripts | Remove obsolete scripts, update documentation | All others: READ-ONLY |
| **.pre-commit-config.yaml** | code_developer | YES - Pre-commit hooks | Keep hooks current, update configurations | All others: READ-ONLY |
| **data/user_interpret/** | user_interpret | YES - Operational data (conversation logs, etc.) | Rotate logs, archive old conversations | All others: READ-ONLY |

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

## CFR-005: Ownership Includes Maintenance Responsibility

**Purpose**: Implements CFR-000 by ensuring owners proactively maintain their files/directories.

**This CFR prevents**: Technical debt accumulation and system degradation from neglected maintenance.

**Rule**: Owning files/directories means maintaining them (cleaning, simplifying, updating, organizing).

**Core Principle**:

Ownership is not just about write access. It includes ongoing care and stewardship.

**Maintenance Responsibilities**:

### For ALL Owners

Every agent that owns files/directories MUST:

### 1. Keep Directories Clean

- Remove obsolete files
- Archive old versions
- Delete temporary files
- Organize subdirectories logically

### 2. Simplify Documents

- Remove redundant content
- Consolidate duplicated information
- Refactor overly complex documents
- Split large files into smaller ones

### 3. Update Regularly

- Keep documentation current
- Update stale information
- Refresh examples
- Verify links still work

### 4. Improve Over Time

- Enhance clarity
- Add missing sections
- Improve organization
- Fix formatting issues

### Specific Responsibilities by Owner

**code_developer** (owns coffee_maker/, tests/, .claude/):
- Refactor complex code when architect identifies technical debt
- Remove unused functions/classes
- Update stale comments
- Organize test files logically
- Clean up temporary test files
- Update .claude/CLAUDE.md as system evolves

**project_manager** (owns docs/roadmap/):
- Archive completed priorities
- Remove obsolete strategic specs
- Consolidate duplicate priorities
- Keep ROADMAP organized and readable
- Update TEAM_COLLABORATION.md as workflows evolve
- Simplify CRITICAL_FUNCTIONAL_REQUIREMENTS.md if it grows too large

**architect** (owns docs/architecture/):
- Archive superseded ADRs
- Update technical specs as system changes
- Organize specs/decisions/guidelines directories
- Remove obsolete guidelines
- Refactor complex technical documents
- Keep refactoring plans directory clean
- Monitor code quality weekly (identifies refactoring needs)
- Create refactoring plans when needed (docs/architecture/refactoring/)

**generator** (owns docs/generator/):
- Archive old execution traces
- Rotate trace files (keep recent, archive old)
- Summarize historical traces
- Clean up large trace files

**reflector** (owns docs/reflector/):
- Archive old delta items
- Consolidate similar insights
- Remove duplicated learnings
- Keep deltas directory organized

**curator** (owns docs/curator/):
- Prune playbook duplicates (semantic de-duplication)
- Remove low-effectiveness patterns
- Consolidate similar patterns
- Keep playbook under size limits

### When to Perform Maintenance

**Regular Schedule** (Weekly/Monthly):
- Review owned directories
- Identify cleanup opportunities
- Schedule maintenance work
- Execute cleanups

**Triggered Maintenance** (Event-based):
- After major feature completion
- When directory grows >50 files
- When single file grows >2000 lines
- When architect identifies technical debt

**Proactive Maintenance** (Continuous):
- While working in owned files
- During feature implementation
- During bug fixes
- During reviews

### Maintenance Workflow

```
Owner monitors owned directories
    ↓
Owner identifies maintenance needed
    ↓
Owner plans maintenance (if large, escalate to user)
    ↓
Owner executes maintenance
    ↓
Owner commits with clear message: "chore: Clean up docs/roadmap/"
```

### Escalation for Large Maintenance

If maintenance requires >4 hours:
1. Owner escalates to project_manager
2. project_manager creates maintenance task in ROADMAP
3. User approves priority
4. Owner executes with dedicated time

### Examples

**Good Maintenance** (code_developer):
```bash
git log --oneline
abc123 chore: Remove unused utility functions in coffee_maker/utils/
def456 refactor: Split 1500-line daemon.py into mixins
ghi789 chore: Clean up test fixtures in tests/unit/
```

**Good Maintenance** (project_manager):
```bash
git log --oneline
abc123 chore: Archive completed priorities PRIORITY 1-10
def456 chore: Consolidate duplicate strategic specs
ghi789 docs: Reorganize ROADMAP for better readability
```

**Good Maintenance** (architect):
```bash
git log --oneline
abc123 chore: Archive superseded ADR-003 (replaced by ADR-007)
def456 docs: Update SPEC-001 with new architecture
ghi789 chore: Organize refactoring plans by year
```

### Enforcement

**Level 1: Self-Check**
- Owner regularly reviews owned directories
- Owner identifies maintenance opportunities
- Owner schedules maintenance work

**Level 2: architect Monitoring** (for code quality)
- architect monitors code complexity
- architect schedules refactoring when needed
- See US-044 for workflow

**Level 3: project_manager Monitoring** (for documentation)
- project_manager monitors docs/ size
- project_manager schedules cleanup when needed

**Level 4: User Review**
- User can request cleanup: "Please clean up docs/roadmap/"
- Owner executes cleanup
- Owner reports completion

### Failure to Maintain = Violation

If owner neglects maintenance:
- Directories become cluttered
- Files become unmaintainable
- Technical debt accumulates
- System degrades over time

This violates the spirit of ownership and CFR-000 (prevent system degradation).

### Metrics

**Healthy Ownership**:
- Files <2000 lines (mostly)
- Directories <50 files (mostly)
- No obsolete files >6 months old
- Regular maintenance commits (monthly)
- Code complexity within limits

**Unhealthy Ownership** (needs attention):
- Files >3000 lines
- Directories >100 files
- Many obsolete files
- No maintenance commits in 3+ months
- Code complexity exceeds limits

### Benefits

**For Owners**:
- Easier to work in clean directories
- Less cognitive load
- Faster to find things
- Pride in well-maintained code

**For System**:
- Better code quality
- Easier onboarding
- Lower technical debt
- Sustainable long-term

**For Users**:
- Faster feature delivery
- Fewer bugs from complexity
- Confidence in system health

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

## Ownership-Aware File Tools

**Purpose**: Enforce CFR-000 at the tool level by restricting write operations automatically.

### Tool Architecture

Every agent is equipped with two file operation tools:

#### 1. READ Tool (Unrestricted)

**Access**: All agents can read all files

**Why Unrestricted**:
- Reading never causes file conflicts
- Agents need context from multiple sources
- assistant needs to read entire codebase
- code-searcher analyzes all files
- No risk of corruption from reads

**Usage**:
```python
# Any agent can read any file
content = read_file("docs/roadmap/ROADMAP.md")
content = read_file(".claude/CLAUDE.md")
content = read_file("coffee_maker/autonomous/daemon.py")
# All allowed - reading is safe
```

#### 2. WRITE Tool (Ownership-Restricted)

**Access**: Each agent's WRITE tool is pre-configured with ownership boundaries

**Why Restricted**:
- Writing can cause file conflicts
- Must enforce CFR-001 (Document Ownership Boundaries)
- Automatic enforcement prevents accidents
- Cannot bypass even if agent tries

**Configuration Per Agent**:

```python
# code_developer WRITE tool configuration
code_developer_write = WriteTool(
    allowed_paths=[
        ".claude/",
        "coffee_maker/",
        "tests/",
        "scripts/",
        ".pre-commit-config.yaml",
        "pyproject.toml",  # ONLY if architect delegates
        "poetry.lock",     # ONLY if architect delegates
    ]
)

# project_manager WRITE tool configuration
project_manager_write = WriteTool(
    allowed_paths=[
        "docs/roadmap/",
        "docs/templates/",
        "docs/tutorials/",
        "docs/code-searcher/",
        "docs/user_interpret/",
        "docs/code_developer/",
    ]
)

# architect WRITE tool configuration
architect_write = WriteTool(
    allowed_paths=[
        "docs/architecture/",
        "pyproject.toml",
        "poetry.lock",
    ]
)

# assistant WRITE tool configuration
assistant_write = WriteTool(
    allowed_paths=[]  # EMPTY - assistant owns NO files
)
# assistant can only read and delegate
```

**Enforcement Logic**:

```python
class WriteTool:
    def __init__(self, agent_type: AgentType, allowed_paths: List[str]):
        self.agent_type = agent_type
        self.allowed_paths = allowed_paths

    def write_file(self, file_path: str, content: str) -> WriteResult:
        """Write file with automatic ownership enforcement."""

        # Check if file path is within allowed boundaries
        if not self._is_path_allowed(file_path):
            # BLOCK - ownership violation
            owner = FileOwnership.get_owner(file_path)

            raise OwnershipViolationError(
                f"Agent '{self.agent_type}' cannot write to '{file_path}'\n"
                f"Owner: {owner}\n"
                f"Action: Delegate to {owner} instead.\n"
                f"\n"
                f"This agent can only write to:\n" +
                "\n".join(f"  - {path}" for path in self.allowed_paths)
            )

        # Allowed - perform write
        return self._perform_write(file_path, content)

    def _is_path_allowed(self, file_path: str) -> bool:
        """Check if file path is within allowed boundaries."""
        for allowed_path in self.allowed_paths:
            if file_path.startswith(allowed_path):
                return True
        return False
```

**Example: Automatic Blocking**

```python
# project_manager attempts to write to .claude/CLAUDE.md
try:
    project_manager_write.write_file(
        ".claude/CLAUDE.md",
        "Updated content"
    )
except OwnershipViolationError as e:
    print(e)
    # Output:
    # Agent 'project_manager' cannot write to '.claude/CLAUDE.md'
    # Owner: code_developer
    # Action: Delegate to code_developer instead.
    #
    # This agent can only write to:
    #   - docs/roadmap/
    #   - docs/templates/
    #   - docs/tutorials/
    #   - docs/code-searcher/
    #   - docs/user_interpret/
    #   - docs/code_developer/
```

**Example: Automatic Delegation**

```python
# project_manager needs to update .claude/CLAUDE.md
# Instead of direct write, use delegation tool

result = delegate_task(
    task="Update .claude/CLAUDE.md with new ownership matrix",
    context={"updates": ownership_updates},
    target_file=".claude/CLAUDE.md"
)

# generator receives delegation request
# generator checks: Who owns .claude/CLAUDE.md?
# generator finds: code_developer
# generator delegates to code_developer
# code_developer WRITE tool allows (within owned paths)
# code_developer performs update
# Result returns to project_manager
```

### Benefits

**Automatic Enforcement**:
- Agents cannot accidentally write outside boundaries
- No need for manual ownership checks in agent code
- Impossible to bypass (tool-level enforcement)

**Clear Error Messages**:
- Agent immediately knows what went wrong
- Owner clearly identified
- Allowed paths listed for reference
- Suggestion to delegate

**Zero Configuration for Agents**:
- Agent just calls `write_file(path, content)`
- Tool handles all ownership checks
- Agent doesn't need to know ownership matrix
- Enforcement is transparent

**Integration with Delegation**:
- Blocked writes automatically suggest delegation
- Delegation tool routes to correct owner
- Owner's WRITE tool allows the operation
- Seamless workflow

### Tool Configuration Management

**Centralized Configuration**:

```python
# coffee_maker/autonomous/ace/file_tool_config.py

FILE_TOOL_OWNERSHIP = {
    AgentType.CODE_DEVELOPER: [
        ".claude/",
        "coffee_maker/",
        "tests/",
        "scripts/",
        ".pre-commit-config.yaml",
    ],

    AgentType.PROJECT_MANAGER: [
        "docs/roadmap/",
        "docs/templates/",
        "docs/tutorials/",
        "docs/code-searcher/",
        "docs/user_interpret/",
        "docs/code_developer/",
    ],

    AgentType.ARCHITECT: [
        "docs/architecture/",
        "pyproject.toml",
        "poetry.lock",
    ],

    AgentType.GENERATOR: [
        "docs/generator/",
    ],

    AgentType.REFLECTOR: [
        "docs/reflector/",
    ],

    AgentType.CURATOR: [
        "docs/curator/",
    ],

    AgentType.ASSISTANT: [],  # READ-ONLY
    AgentType.USER_LISTENER: [],  # Delegation-only
    AgentType.CODE_SEARCHER: [],  # READ-ONLY
    AgentType.UX_DESIGN_EXPERT: [],  # Provides specs only
}

def create_write_tool(agent_type: AgentType) -> WriteTool:
    """Create WRITE tool configured for agent's ownership boundaries."""
    allowed_paths = FILE_TOOL_OWNERSHIP.get(agent_type, [])
    return WriteTool(agent_type, allowed_paths)

def create_read_tool(agent_type: AgentType) -> ReadTool:
    """Create READ tool (unrestricted for all agents)."""
    return ReadTool(agent_type)  # No path restrictions
```

**Single Source of Truth**:
- Ownership matrix in CRITICAL_FUNCTIONAL_REQUIREMENTS.md
- Tool configuration mirrors ownership matrix
- Changes to ownership require updating both
- Consistency enforced through documentation

### Integration with Existing Enforcement

**Four Layers of Protection**:

```
Layer 1: Singleton Enforcement (US-035)
    ↓
    Prevents multiple instances of file-owning agents

Layer 2: Tool-Level Enforcement (NEW)
    ↓
    WRITE tool blocks writes outside owned paths

Layer 3: generator Enforcement (US-038)
    ↓
    generator checks ownership before delegation

Layer 4: Multi-Level Validation (US-039)
    ↓
    User story/request/agent validation

= COMPLETE CFR-000 IMPLEMENTATION
```

**Defense in Depth**: Multiple layers ensure CFR-000 cannot be violated.

### Testing Strategy

**Unit Tests**:
```python
def test_write_tool_allows_owned_paths():
    tool = create_write_tool(AgentType.CODE_DEVELOPER)
    result = tool.write_file("coffee_maker/test.py", "content")
    assert result.success

def test_write_tool_blocks_unowned_paths():
    tool = create_write_tool(AgentType.PROJECT_MANAGER)
    with pytest.raises(OwnershipViolationError):
        tool.write_file("coffee_maker/test.py", "content")

def test_read_tool_unrestricted():
    tool = create_read_tool(AgentType.ASSISTANT)
    # Can read anything
    content1 = tool.read_file("docs/roadmap/ROADMAP.md")
    content2 = tool.read_file(".claude/CLAUDE.md")
    content3 = tool.read_file("coffee_maker/autonomous/daemon.py")
    # All succeed
```

**Integration Tests**:
```python
def test_delegation_flow_on_ownership_violation():
    # project_manager tries to write .claude/CLAUDE.md
    try:
        project_manager_write.write_file(".claude/CLAUDE.md", "content")
    except OwnershipViolationError:
        # Delegates to code_developer
        result = delegate_task(
            task="Update .claude/CLAUDE.md",
            context={"content": "content"}
        )
        # Should succeed
        assert result.success
```

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

## CFR-006: Lessons Learned Must Be Captured and Applied

**Rule**: All key lessons (both failures and successes) MUST be documented, owned, and actively used.

**Core Principle**:
The system must LEARN from experience. Lessons that aren't captured and applied lead to repeated errors and missed opportunities.

**Ownership**: **project_manager** owns docs/roadmap/learnings/

**Why project_manager**:
- Strategic visibility into project patterns
- Owns ROADMAP (sees what goes wrong during execution)
- Coordinates between all agents
- Best positioned to identify recurring patterns
- Can escalate lessons to CRITICAL_FUNCTIONAL_REQUIREMENTS when needed

### Lessons Learned Directory

**Location**: `docs/roadmap/learnings/`

**Owner**: project_manager (exclusive ownership)

**File Types**:
1. **Workflow Failures**: `WORKFLOW_FAILURE_*.md`
   - Process breakdowns
   - Agent coordination failures
   - Missing safeguards

2. **Technical Failures**: `TECHNICAL_FAILURE_*.md`
   - Architecture mistakes
   - Implementation errors that caused issues
   - Design flaws

3. **User Frustration**: `USER_FRUSTRATION_*.md`
   - Issues that frustrated user
   - Gaps in user experience
   - Communication failures

4. **Success Patterns**: `SUCCESS_PATTERN_*.md`
   - What worked well
   - Effective workflows
   - Best practices discovered

5. **Monthly Summaries**: `LESSONS_YYYY_MM.md`
   - Monthly rollup of all lessons
   - Patterns identified
   - Actions taken

### Capturing Both Failures and Successes

**Important**: Lessons system captures both failures and successes to learn key lessons.

**Why Failures Matter**:
- Identify what to avoid
- Prevent recurrence of errors
- Understand root causes
- Improve system reliability

**Why Successes Matter**:
- Identify what works well
- Enable replication of effective patterns
- Build best practices library
- Guide future decisions

**Lesson Types**:
1. **Workflow Lessons**: Process effectiveness (what worked/didn't work)
2. **Technical Lessons**: Implementation outcomes (efficient/inefficient approaches)
3. **Performance Lessons**: Speed and efficiency gains or issues
4. **User Experience Lessons**: What pleased or frustrated users
5. **Collaboration Lessons**: Effective or ineffective agent coordination

### Lesson Capture Workflow

**When to Capture**:
- Any failure (workflow, technical, process)
- User expresses frustration
- Same mistake happens twice
- Significant success worth replicating
- User expresses satisfaction
- Performance significantly exceeds or misses expectations
- Collaboration works exceptionally well or poorly
- Key insight discovered
- Milestone achieved significantly ahead or behind schedule

**Who Captures**:
1. **Any agent** can identify a lesson
2. **Agent delegates to project_manager**: "Capture lesson: [description]"
3. **project_manager** creates lesson document in docs/roadmap/learnings/
4. **project_manager** updates relevant documents (CFRs, ROADMAP, workflows)

**Lesson Document Template**:
```markdown
# [Lesson Type]: [Brief Title]

**Date**: YYYY-MM-DD
**Severity**: [CRITICAL/HIGH/MEDIUM/LOW]
**Category**: [Workflow/Technical/User Experience/Success]
**Reported By**: [agent_name or user]

## What Happened

[Clear description of the event/failure/success]

## Root Cause

[Why it happened - be specific]

## Impact

- User frustration level: [High/Medium/Low]
- Time wasted: [estimate]
- Trust impact: [description]
- System integrity: [description]

## Lesson Learned

[The key takeaway - what we learned]

## Prevention / Replication

[How to prevent if failure, or replicate if success]

**Specific Actions**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Update Required Documents**:
- [ ] CRITICAL_FUNCTIONAL_REQUIREMENTS.md (if fundamental)
- [ ] TEAM_COLLABORATION.md (if workflow-related)
- [ ] Relevant agent definitions (if agent-specific)
- [ ] US-039 validation rules (if validation-related)

## Status

- [ ] Lesson documented
- [ ] Documents updated
- [ ] Agents notified
- [ ] Preventive measures implemented
- [ ] Verified resolved (no recurrence)
```

### Success Pattern Document Template

```markdown
# SUCCESS PATTERN: [Brief Title]

**Date**: YYYY-MM-DD
**Impact**: [HIGH/MEDIUM/LOW]
**Category**: [Workflow/Technical/Performance/User Experience/Collaboration]
**Key Contributors**: [agents or user]

## What Succeeded

[Clear description of the success]

**Metrics**:
- Expected outcome: [what we expected]
- Actual outcome: [what we achieved]
- Improvement: [quantify if possible]

## Why It Worked

[Root cause of success - be specific about what made this effective]

**Key Factors**:
1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

## Context

[What conditions enabled this success? What was different?]

## Value Delivered

- **User benefit**: [how this helped the user]
- **System benefit**: [how this improved the system]
- **Time saved**: [estimate if applicable]
- **Quality improvement**: [if applicable]

## Replication Guide

**How to replicate this success**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**When to use this pattern**:
- Situation 1
- Situation 2
- Situation 3

**Cautions**:
- [What to watch out for when replicating]

## Update Required Documents

- [ ] Best practices added to agent definitions
- [ ] Pattern added to TEAM_COLLABORATION.md
- [ ] Approach documented in relevant guides
- [ ] Success referenced in future planning

## Recognition

[Acknowledge agents/user who contributed to this success]

## Status

- [ ] Success documented
- [ ] Documents updated with best practice
- [ ] Pattern shared with all agents
- [ ] Replication guide verified
```

### Using Lessons to Prevent Recurrence

**Required Reading**:
All agents MUST read docs/roadmap/learnings/ periodically:
- **Weekly**: Recent lessons (last 7 days)
- **Monthly**: All lessons from current month
- **Quarterly**: Full directory review

**Integration Points**:

1. **agent role definitions** (.claude/agents/*.md):
   - Add "Common Mistakes to Avoid" section
   - Reference specific lesson documents
   - Update based on learnings

2. **CRITICAL_FUNCTIONAL_REQUIREMENTS.md**:
   - Promote frequent/critical lessons to CFRs
   - Example: US-040 failure → CFR-006

3. **US-039 validation**:
   - Check against known failure patterns
   - Reference lessons in validation logic

4. **reflector analysis**:
   - Analyzes lesson documents
   - Identifies recurring patterns
   - Suggests systemic improvements

5. **curator playbook**:
   - Incorporates lessons into agent playbooks
   - Creates avoidance patterns
   - Updates effectiveness metrics

### Examples of Lessons

**Already Captured**:
- ✅ WORKFLOW_FAILURE_US_040.md (user story without CFR validation)
- ✅ OWNERSHIP_VIOLATION_US_038.md (file ownership violation patterns)

**Should Be Captured** (from recent sessions):
- File searching wasteful → US-042 created
- architect agent not operational → US-041 created
- Parallel execution needed → US-043 created
- Refactoring workflow missing → US-044 created
- Ownership includes maintenance → CFR-005 created

### Monthly Summaries (LESSONS_YYYY_MM.md)

**Required Sections**:
1. **Summary Statistics**:
   - Total lessons captured
   - By category: Failures, Successes, etc.

2. **Key Failures** (up to 5):
   - Brief description
   - Impact
   - Status (prevented/recurring)

3. **Key Successes** (up to 5):
   - Brief description
   - Impact
   - Replication status

4. **Patterns Identified**:
   - Recurring themes
   - Systemic issues
   - Effective approaches

5. **Actions Taken**:
   - Documents updated
   - CFRs promoted
   - Agent behaviors changed

6. **Effectiveness Metrics**:
   - Recurrence rate (target: <10%)
   - Time to resolution
   - User satisfaction signals

### Maintenance Responsibility (CFR-005 Applied)

**project_manager maintains docs/roadmap/learnings/**:

**Weekly** (project_manager):
- Review new lessons
- Update relevant documents

**Monthly** (first week of month):
- Create LESSONS_YYYY_MM.md summary
- Identify patterns across lessons
- Promote critical lessons to CFRs if needed
- Archive old lessons (>6 months to archive/ subdirectory)
- Update agent definitions with lessons learned

**Quarterly** (Q1, Q2, Q3, Q4):
- Review all lessons for recurring themes
- Escalate systemic issues to architect
- Update TEAM_COLLABORATION.md with workflow improvements
- Report lessons summary to user

**Metrics to Track**:
- Total lessons captured
- Lessons by severity
- Lessons by category (failures and successes)
- Recurrence rate (same lesson multiple times = problem)
- Time to resolution (how long to implement prevention/replication)
- Effectiveness (did prevention/replication work?)

### Escalation

**When to Escalate**:
- Same lesson captured 3+ times (systemic issue)
- CRITICAL severity lesson
- Lesson requires architecture change
- User explicitly requests escalation

**Escalation Path**:
```
project_manager identifies pattern
    ↓
Escalate to architect (technical solution needed?)
    ↓
architect designs systemic fix
    ↓
code_developer implements
    ↓
project_manager verifies (no recurrence)
```

### Integration with ACE Framework

**generator**:
- Reads lessons before routing tasks
- Avoids known failure patterns
- Logs new failure patterns for lessons capture

**reflector**:
- Analyzes lesson documents
- Extracts patterns across multiple lessons
- Suggests root cause categories

**curator**:
- Incorporates lessons into agent playbooks
- Creates "never do this" patterns
- Updates avoidance strategies

### Success Criteria for CFR-006

**Healthy Lessons System**:
- ✅ All failures documented within 24 hours
- ✅ Monthly summaries created consistently
- ✅ No recurring lessons (same mistake <2 times)
- ✅ Documents updated within 1 week of lesson
- ✅ Agents reference lessons when working
- ✅ User sees improving system (fewer repeated mistakes)

**Unhealthy Lessons System**:
- ❌ Failures not documented
- ❌ Same mistakes repeated 3+ times
- ❌ Lessons documents ignored
- ❌ No updates to agent behaviors
- ❌ User frustrated by recurring issues

### Why This CFR Is Critical

**Without Lessons System**:
- Same mistakes repeated endlessly
- User wastes time on known issues
- Trust degrades ("they never learn")
- System appears unintelligent
- No improvement over time

**With Lessons System**:
- Mistakes learned from immediately
- Prevention implemented proactively
- User sees continuous improvement
- Trust builds ("they learn and adapt")
- System becomes smarter over time

---

## CFR-010: Architect Must Continuously Review and Improve Specs

**Rule**: The architect MUST regularly re-read ALL specs and the FULL ROADMAP to proactively improve specifications and think ahead about implementation complexities.

**Why This Is Critical**:

1. **Continuous Improvement**: Specs get better with fresh perspectives
2. **Anticipate Problems**: Early detection of complexity prevents wasted implementation effort
3. **Cross-Feature Optimization**: See patterns and reuse opportunities across specs
4. **Simplification Opportunities**: Find ways to reduce complexity as understanding deepens
5. **Consistency**: Ensure all specs align with latest architectural decisions

**Frequency**:
- **Daily**: Quick review of ROADMAP changes
- **Weekly**: Deep review of all active specs
- **Before Each New Spec**: Review all existing specs for patterns and reuse
- **After Implementation**: Review spec based on what was actually built

**Review Process**:

1. **Re-read FULL ROADMAP**:
   - Note new priorities added
   - Identify dependencies between features
   - Spot opportunities for consolidation
   - Update priority on what needs specs next

2. **Re-read ALL Existing Specs**:
   - Check for outdated assumptions
   - Look for simplification opportunities
   - Find duplicated patterns that could be shared
   - Identify specs that can be merged or eliminated

3. **Think Ahead**:
   - What complexities will code_developer face?
   - Can we reduce implementation effort by 30-50%?
   - Are there existing solutions we can reuse?
   - What's the MINIMUM viable implementation?

4. **Update Specs Proactively**:
   - Add simplifications discovered
   - Update with better approaches
   - Add warnings about pitfalls
   - Document shortcuts and copy-paste examples

5. **Create Improvement ADRs**:
   - Document why specs changed
   - Explain what was learned
   - Capture patterns for future reference

**Example Workflow**:

```
Monday Morning (30 min):
  → architect reviews ROADMAP for changes
  → Identifies 2 new priorities need specs
  → Reviews existing SPEC-009, SPEC-010
  → Finds duplication: both use notification patterns
  → Creates shared NotificationHelper utility
  → Updates both specs to use helper
  → Reduces implementation from 6 hours → 3 hours

Wednesday (1 hour):
  → Deep review of all 5 active specs
  → Discovers 3 specs use similar git operations
  → Proposes GitOpsHelper abstraction
  → Creates ADR-004 documenting decision
  → Updates specs with simpler approach
  → Total reduction: 12 hours → 6 hours

Friday (30 min):
  → Reviews code_developer's completed work
  → Sees they struggled with config management
  → Updates related specs with clearer config examples
  → Adds "Common Pitfalls" section
  → Prevents future implementations from same struggle
```

**Deliverables**:

1. **Weekly Improvement Report** (`docs/architecture/WEEKLY_SPEC_REVIEW_[date].md`):
   - What was reviewed
   - What was improved
   - Effort savings achieved
   - Patterns identified

2. **Updated Specs**:
   - Simpler implementations
   - Better examples
   - Clearer warnings

3. **New ADRs** (as needed):
   - Document significant improvements
   - Explain architectural evolution

**Metrics to Track**:

- **Simplification Rate**: % reduction in implementation complexity
- **Reuse Rate**: % of new specs using shared components
- **Effort Saved**: Hours saved by spec improvements
- **Iteration Speed**: Time from spec creation to completion

**Benefits**:

- code_developer gets progressively better specs
- Implementation time decreases over time
- Fewer blockers and questions
- Higher quality, more maintainable code
- System learns and improves continuously

**User Story**: US-049: Architect Continuous Spec Improvement Loop

---

## CFR-011: Architect Must Integrate code-searcher Findings Daily

**Rule**: The architect MUST read code-searcher analysis reports daily AND proactively analyze the codebase itself to identify **refactoring opportunities and technical debt reduction**, then integrate ALL findings into technical specifications.

**What "Improvements" Means**:
- ✅ **Refactoring**: Code restructuring (splitting large files, extracting utilities, removing duplication)
- ✅ **Technical Debt Reduction**: Addressing accumulated quality issues (test coverage gaps, inconsistent patterns, missing abstractions)
- ✅ **Code Quality**: Simplification, maintainability, readability improvements
- ✅ **Security Fixes**: Addressing vulnerabilities and security concerns
- ❌ **NOT New Features**: This is about improving existing code quality, not adding functionality

**Why This Is Critical**:

1. **Prevent Technical Debt Accumulation**: Address quality issues before they compound
2. **Data-Driven Refactoring**: Use actual codebase metrics, not assumptions
3. **Continuous Code Quality**: Codebase improves daily through systematic refactoring
4. **Proactive Maintenance**: Fix problems before they become blockers
5. **Knowledge Integration**: code-searcher finds patterns architect must address through refactoring specs

**Two-Part Mandate**:

### Part 1: Read code-searcher Analysis Reports Daily

**Frequency**: EVERY DAY (automated enforcement)

**What to Read**:
- `/docs/*_AUDIT_*.md` - Security, quality, dependency audits
- `/docs/*_ANALYSIS_*.md` - Code quality, pattern, reuse analyses
- `/docs/CODEBASE_ANALYSIS_SUMMARY_*.md` - Executive summaries

**What to Do**:
1. **Extract Refactoring Items**: Identify code that needs restructuring (large files, duplication, complexity)
2. **Prioritize**: High-impact, low-effort refactorings first
3. **Create Refactoring Specs**: For each major refactoring (SPEC-050: Split roadmap_cli.py, SPEC-051: Extract prompt utilities)
4. **Update Existing Specs**: Integrate quality improvements into current specs
5. **Track Integration**: Document what refactorings were addressed and why

### Part 2: Proactively Analyze Code Yourself

**Frequency**: WEEKLY (minimum)

**What to Analyze**:
1. **New Code**: Review recent commits (git log --since=1.week)
2. **Problem Areas**: Files with frequent changes or bugs
3. **Complex Modules**: Large files (>500 LOC), high complexity
4. **Duplicate Patterns**: Look for code that can be abstracted
5. **Missing Abstractions**: Opportunities for utilities/helpers

**Tools to Use**:
- `Read` tool: Examine specific files
- `Grep` tool: Find patterns across codebase
- `Glob` tool: Identify similar files
- `Bash` tool: Run metrics (`wc -l`, `git log`, etc.)

**What to Do**:
1. **Document Refactoring Opportunities**: Create analysis notes on code that needs improvement
2. **Create Refactoring Specs**: Address technical debt and quality issues found
3. **Update ADRs**: Document refactoring decisions and patterns
4. **Inform code_developer**: Provide guidance on refactoring patterns and best practices

**Enforcement Mechanism**:

```python
# In architect agent startup/daily routine:

class ArchitectDailyRoutine:
    """Enforces CFR-011 daily integration workflow."""

    def __init__(self):
        self.last_code_searcher_read = self._load_last_read_date()
        self.last_codebase_analysis = self._load_last_analysis_date()

    def enforce_cfr_011(self):
        """Mandatory daily check before architect can create new specs."""
        today = datetime.now().date()

        # Part 1: code-searcher report reading
        if self.last_code_searcher_read < today:
            reports = self._find_new_code_searcher_reports()
            if reports and not self._has_read_reports(reports):
                raise CFR011ViolationError(
                    f"CFR-011 VIOLATION: Must read {len(reports)} new code-searcher "
                    f"reports before creating specs today.\n\n"
                    f"Reports to read:\n" + "\n".join(f"- {r}" for r in reports) +
                    f"\n\nRun: architect daily-integration"
                )
            self._mark_reports_read(today)

        # Part 2: Weekly codebase analysis
        days_since_analysis = (today - self.last_codebase_analysis).days
        if days_since_analysis >= 7:
            raise CFR011ViolationError(
                f"CFR-011 VIOLATION: {days_since_analysis} days since last "
                f"codebase analysis (max: 7 days).\n\n"
                f"Must analyze codebase yourself before creating new specs.\n"
                f"Run: architect analyze-codebase"
            )

    def daily_integration_workflow(self):
        """Guided workflow for integrating code-searcher findings."""
        # 1. Read all new reports
        reports = self._find_new_code_searcher_reports()
        for report in reports:
            print(f"Reading: {report}")
            self._display_report_summary(report)

        # 2. Extract refactoring opportunities
        refactorings = self._extract_refactoring_items(reports)
        print(f"\nFound {len(refactorings)} refactoring opportunities")

        # 3. Create refactoring specs for high-impact items
        for refactoring in refactorings:
            if refactoring.impact == "HIGH" or refactoring.effort <= "4 hours":
                self._create_refactoring_spec(refactoring)

        # 4. Update existing specs with quality improvements
        self._integrate_findings_into_specs(refactorings)

        # 5. Document integration
        self._create_integration_report(reports, refactorings)

        # 6. Mark complete
        self._mark_reports_read(datetime.now().date())

    def analyze_codebase_workflow(self):
        """Guided workflow for architect's own codebase analysis."""
        # 1. Recent commits
        recent_commits = self._analyze_recent_commits()

        # 2. Problem areas
        problem_files = self._identify_problem_areas()

        # 3. Complexity hot spots
        complex_modules = self._find_complex_modules()

        # 4. Duplicate patterns
        duplications = self._find_duplicate_patterns()

        # 5. Create findings report
        self._create_architect_analysis_report({
            "commits": recent_commits,
            "problems": problem_files,
            "complexity": complex_modules,
            "duplications": duplications
        })

        # 6. Create refactoring specs
        self._create_refactoring_specs_from_analysis()

        # 7. Mark complete
        self._mark_analysis_complete(datetime.now().date())
```

**Deliverables**:

1. **Daily Integration Report** (`docs/architecture/CODE_SEARCHER_INTEGRATION_[date].md`):
   - Which reports were read
   - Refactoring opportunities extracted
   - Refactoring specs created/updated
   - Cross-references

2. **Weekly Analysis Report** (`docs/architecture/ARCHITECT_CODEBASE_ANALYSIS_[date].md`):
   - What architect analyzed
   - Refactoring opportunities and technical debt identified
   - Refactoring specs created (SPEC-050: Split files, SPEC-051: Extract utilities, etc.)
   - Metrics tracked

3. **Updated Specs**:
   - Existing specs updated with quality improvements
   - New refactoring specs created (SPEC-050+)

4. **Tracking File** (`data/architect_integration_status.json`):
   ```json
   {
     "last_code_searcher_read": "2025-10-17",
     "last_codebase_analysis": "2025-10-17",
     "reports_read": [
       "SECURITY_AUDIT_2025-10-17.md",
       "CODE_QUALITY_ANALYSIS_2025-10-17.md"
     ],
     "action_items_total": 12,
     "specs_created": 4,
     "specs_updated": 6,
     "next_analysis_due": "2025-10-24"
   }
   ```

**Correct Workflow**:

```
Daily (Every Morning):
1. architect agent starts
2. CFR-011 enforcement check runs automatically
3. If new code-searcher reports exist: MUST read before creating specs
4. If >7 days since codebase analysis: MUST analyze before creating specs
5. Run daily-integration workflow
6. THEN: Create new specs for priorities

Weekly (Every Monday):
1. Run architect analyze-codebase
2. Review last 7 days of commits
3. Identify problem areas
4. Find duplicate patterns
5. Create improvement specs
6. Update tracking file
```

**Incorrect Workflow** (BLOCKED):

```
❌ architect tries to create new spec without reading code-searcher reports
   → CFR011ViolationError raised
   → Spec creation BLOCKED
   → Clear error message with reports to read

❌ architect hasn't analyzed codebase in 8 days
   → CFR011ViolationError raised
   → Must run analyze-codebase first
   → Clear error message with days overdue
```

**Metrics**:

- **Integration Rate**: % of code-searcher findings addressed
- **Response Time**: Days from code-searcher report to spec integration
- **Improvement Velocity**: Number of improvement specs created per week
- **Quality Trend**: Are quality metrics improving over time?

**Benefits**:

- **Proactive**: Issues caught before they become blockers
- **Data-Driven**: Decisions based on real code analysis
- **Continuous**: Architecture improves every day
- **Comprehensive**: Both automated (code-searcher) and manual (architect) analysis
- **Enforced**: Code prevents violations, not just guidelines

**Integration with Other CFRs**:

- **CFR-008**: architect creates all specs → includes improvement specs
- **CFR-010**: Continuous spec review → informed by code-searcher findings
- **ADR-003**: Simplification-first → use metrics to prove simplification

**User Story**: US-054: Architect Daily Integration of code-searcher Findings (NEW)

---

## CFR-009: ONLY user_listener Uses Sound Notifications

**Rule**: ONLY the user_listener agent can use sound notifications. All other agents (code_developer, architect, project_manager, etc.) MUST use silent notifications only.

**Why This Is Critical**:

1. **User Experience**: Only user-facing interactions should make sound
2. **Background Work**: Autonomous agents work silently in background
3. **Role Clarity**: user_listener is the ONLY UI agent - only it should alert user with sound
4. **Noise Prevention**: Prevents notification spam from multiple agents

**Allowed**:
```
user_listener:
  → Play sound for user interactions
  → Use NotificationDB with sound=True
  → Alert user with audio feedback
```

**NOT Allowed**:
```
code_developer, architect, project_manager, assistant, etc:
  → NEVER play sounds
  → Use NotificationDB with sound=False
  → Silent notifications only
  → User checks notifications when convenient
```

**Implementation**:

In NotificationDB calls:
```python
# ✅ CORRECT (code_developer, background agents)
self.notifications.create(
    title="Task Complete",
    message="PRIORITY 9 done",
    level="info",
    sound=False  # Silent for background work
)

# ✅ CORRECT (user_listener only)
self.notifications.create(
    title="User Action Required",
    message="Please review PR #123",
    level="high",
    sound=True  # Sound for user interaction
)

# ❌ WRONG (code_developer playing sound)
self.notifications.create(
    title="Implementation failed",
    level="high",
    sound=True  # CFR-009 VIOLATION!
)
```

**Current Violation**:
The daemon is currently playing sounds for "Max Retries Reached" - this violates CFR-009.

**Remediation**:
1. Update daemon to use sound=False for all notifications
2. Only user_listener plays sounds
3. User checks silent notifications when convenient

**User Story**: US-048: Enforce CFR-009 Silent Background Agents

---

## CFR-008: Architect Creates ALL Specs - code_developer NEVER Creates Specs

**Rule**: ONLY the architect agent creates technical specifications. The code_developer agent MUST NEVER create specs.

**Why This Is Critical**:

1. **Big Picture Architecture**: architect needs to see the FULL ROADMAP to make optimal architectural decisions
2. **Consistency**: One architect ensures consistent architectural patterns across all features
3. **Role Clarity**: Violating this boundary causes infinite loops and stuck agents
4. **Proactive Planning**: architect should create ALL specs proactively, not reactively

**Correct Flow**:
```
architect (proactively):
  → Reviews FULL ROADMAP
  → Creates ALL needed specs
  → Ensures architectural consistency
  → Considers cross-feature dependencies
  → Optimizes for simplification and reuse

code_developer:
  → Reads spec created by architect
  → Implements exactly what spec describes
  → NEVER creates specs
  → NEVER modifies specs
```

**Violation Example** (WRONG):
```
code_developer: "I need a spec for PRIORITY 9"
code_developer: Tries to create spec from template
→ WRONG! This violates CFR-008
```

**Correct Example**:
```
architect: "Let me review the full ROADMAP"
architect: Creates specs for PRIORITY 9, 10, 11, 12 proactively
architect: Ensures they work together architecturally
code_developer: Reads PRIORITY 9 spec
code_developer: Implements it
```

**Remediation** (when violation detected):

1. **Stop**: Halt code_developer immediately
2. **Notify**: Alert user that architect needs to create specs
3. **Delegate**: Pass spec creation to architect
4. **Wait**: code_developer waits for architect to finish
5. **Resume**: code_developer implements using architect's spec

**Implementation**:

In daemon.py `_ensure_technical_spec()`:
```python
def _ensure_technical_spec(self, priority: dict) -> bool:
    """Check if technical spec exists.

    CFR-008: code_developer NEVER creates specs.
    If spec missing, notify user and delegate to architect.
    """
    if spec_exists:
        return True

    # CFR-008: Do NOT create spec - that's architect's job
    logger.error("❌ CFR-008 VIOLATION PREVENTED")
    logger.error("Spec missing for {priority}")
    logger.error("code_developer CANNOT create specs")
    logger.error("→ Delegating to architect")

    # Mark as blocked, notify user
    self.notify_user_spec_needed(priority)
    return False  # Block until architect creates spec
```

**User Story**: US-047: Enforce CFR-008 Architect-Only Spec Creation

---

## CFR-007: Agent Context Budget (30% Maximum)

**Rule**: An agent's core materials (prompt, role, responsibilities, tools, and owned critical documents with context) MUST fit in at most 30% of its context window.

**Core Principle**:
Agents must have room to work. If core materials consume too much context, the agent cannot effectively process user queries, read additional files, or generate responses.

**Why This Is Critical**:

Context window exhaustion causes:
1. **Agent Ineffectiveness**: No room left for actual work
2. **Truncated Instructions**: Important guidelines cut off
3. **Missing Context**: Cannot read additional files when needed
4. **Poor Responses**: Insufficient space for thoughtful output
5. **System Degradation**: Agent becomes unusable

**30% Breakdown**:

For an agent with 200K token context window:
- **Max 60K tokens** for core materials (30%)
- **Min 140K tokens** remaining for work (70%)

**Core Materials Include**:
1. **Agent Prompt**: System instructions, role definition
2. **Responsibilities**: What the agent does
3. **Tools**: Tool descriptions and usage
4. **Owned Critical Documents**: Must-read files with full context
5. **Examples**: Few-shot examples in prompt

**Core Materials EXCLUDE** (not counted toward 30%):
- User query/request (dynamic input)
- Retrieved documents requested during work
- Generated output/responses
- Conversation history (if applicable)

### Enforcement Strategy

**Measurement**:
```python
def measure_core_context(agent_type: AgentType) -> int:
    """Measure tokens in agent's core materials."""
    total_tokens = 0

    # 1. Agent prompt/role definition
    total_tokens += count_tokens(f".claude/agents/{agent_type}.md")

    # 2. Critical owned documents (marked as "Always Read")
    for doc in agent_critical_docs(agent_type):
        total_tokens += count_tokens(doc)

    # 3. Tools at disposal
    total_tokens += count_tokens(agent_tools_description(agent_type))

    return total_tokens

def check_context_budget(agent_type: AgentType):
    """Enforce 30% context budget."""
    context_window = agent_context_window_size(agent_type)  # e.g., 200K
    max_allowed = context_window * 0.30
    actual = measure_core_context(agent_type)

    if actual > max_allowed:
        raise ContextBudgetViolationError(
            f"Agent '{agent_type}' core context: {actual:,} tokens\n"
            f"Max allowed (30%): {max_allowed:,} tokens\n"
            f"Overage: {actual - max_allowed:,} tokens ({(actual/context_window)*100:.1f}% of window)\n"
            f"\n"
            f"ACTION REQUIRED: Sharpen owned documents or split into indexed structure."
        )
```

**When to Check**:
- Before agent deployment (startup validation)
- After updating agent definitions
- After modifying owned critical documents
- Monthly context budget review

### Remediation Strategies

**When 30% budget is exceeded**, the agent MUST:

#### Strategy 1: Sharpen Main Knowledge Document

**Transform verbose document into concise version**:

**Before (Verbose - 50K tokens)**:
```markdown
# Agent Instructions

This agent is responsible for managing the project ROADMAP.
The ROADMAP is a critical document that contains...

[20 pages of detailed explanations]

## Detailed Procedures

When you receive a request to update the ROADMAP, you should:
1. First, carefully read the entire ROADMAP...
2. Then, analyze the user's request in detail...
[500 lines of step-by-step instructions]
```

**After (Sharpened - 5K tokens)**:
```markdown
# Agent Instructions

Manage project ROADMAP (docs/roadmap/ROADMAP.md).

## Core Responsibilities
- Update priorities
- Track status
- Coordinate agents

## Key Procedures
See: docs/roadmap/project_manager_procedures.md (lines 1-50, 120-180, 300-350)

## Common Scenarios
- Update priority: See procedures.md:1-50
- Add new US: See procedures.md:120-180
- Archive completed: See procedures.md:300-350
```

**Result**: Main document becomes an INDEX pointing to detailed procedures document.

#### Strategy 2: Create Detail Documents (Not Always Read)

**Split large owned document into**:

1. **Main Knowledge Document** (Always Read - counted in 30%)
   - Index/table of contents
   - Core concepts only
   - Pointers to detail documents with line numbers

2. **Detail Documents** (Read On-Demand - NOT counted in 30%)
   - Detailed procedures
   - Extended examples
   - Edge case handling
   - Historical context

**Example Structure**:

```
docs/roadmap/
├── CRITICAL_FUNCTIONAL_REQUIREMENTS.md  (Main - Always Read)
│   ├── Summary of each CFR (1-2 sentences)
│   ├── Pointer: "Details in CFR_DETAILS.md:100-250"
│   └── Emergency quick reference
│
└── CFR_DETAILS.md  (Detail - Read On-Demand)
    ├── Full CFR-000 explanation (lines 1-100)
    ├── Full CFR-001 explanation (lines 101-250)
    ├── Full CFR-002 explanation (lines 251-400)
    └── etc.
```

**Agent behavior**:
- Reads main document (in core context)
- When needs details: Reads specific lines from detail document
- Detail document NOT counted toward 30% budget

#### Strategy 3: Use Line Number References

**In main document, use precise line references**:

```markdown
## CFR-001: Document Ownership

**Summary**: Each file has exactly one owner agent.

**Details**: docs/roadmap/CFR_DETAILS.md:101-250
- Ownership matrix: lines 101-150
- Enforcement: lines 151-200
- Examples: lines 201-250

**Quick Ref**: Ownership matrix in CRITICAL_FUNCTIONAL_REQUIREMENTS.md:169-200
```

**Benefits**:
- Agent knows exactly where to find details
- No wasteful full-file reads
- Surgical precision in context usage
- Main document stays compact

#### Strategy 4: Compress Examples

**Before (Verbose Examples - 20K tokens)**:
```markdown
## Example 1: Complete Walkthrough

Step 1: User requests update
The user might say something like "Please update priority 5 to In Progress"
When you receive this request, you should...

[500 lines of example with full conversation]
```

**After (Compressed Examples - 2K tokens)**:
```markdown
## Example 1: Update Priority Status

Input: "Update priority 5 to In Progress"
Actions: Read ROADMAP → Find Priority 5 → Change status → Commit
Details: docs/roadmap/examples/update_priority_example.md

## Example 2: Add User Story
[Compressed version]
```

### Monitoring & Reporting

**Monthly Context Budget Report**:

```
Agent Context Budget Report - 2025-10
===========================================

Agent              | Core Context | Max Allowed | Usage | Status
-------------------|--------------|-------------|-------|--------
code_developer     |    45K       |    60K      | 75%   | ✅ OK
project_manager    |    58K       |    60K      | 97%   | ⚠️ WARN
architect          |    35K       |    60K      | 58%   | ✅ OK
assistant          |    25K       |    60K      | 42%   | ✅ OK
user_listener      |    30K       |    60K      | 50%   | ✅ OK

WARNINGS:
- project_manager at 97% (58K/60K) - approaching limit
  - Recommend: Sharpen CRITICAL_FUNCTIONAL_REQUIREMENTS.md
  - Consider: Split into main + details structure
```

**Thresholds**:
- **0-70%**: ✅ Healthy (green zone)
- **71-90%**: ⚠️ Warning (yellow zone) - plan remediation
- **91-100%**: ❌ Critical (red zone) - immediate action required
- **>100%**: 🚨 VIOLATION - agent cannot start

### Implementation Requirements

**For Each Agent**:

1. **Identify Critical Documents**
   - Which owned documents are "Always Read"?
   - Which are "Read On-Demand"?
   - Mark clearly in agent definition

2. **Measure Current Context**
   - Run context measurement tool
   - Document current usage percentage
   - Track over time

3. **Optimize If Needed**
   - If >90%: Sharpen documents immediately
   - If >70%: Plan optimization
   - If <70%: Monitor monthly

4. **Maintain Budget**
   - When updating docs: Check impact on context
   - Before adding "Always Read" doc: Verify budget
   - Monthly review: Ensure compliance

### Example: project_manager Optimization

**Current State** (Hypothetical - 97% of budget):
```
Core Context Breakdown:
- .claude/agents/project_manager.md: 5K tokens
- docs/roadmap/ROADMAP.md: 15K tokens (Always Read)
- docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md: 35K tokens (Always Read)
- Tool descriptions: 3K tokens
TOTAL: 58K tokens (97% of 60K budget) ⚠️
```

**Optimization Plan**:

**Step 1**: Sharpen CRITICAL_FUNCTIONAL_REQUIREMENTS.md
```markdown
# CRITICAL_FUNCTIONAL_REQUIREMENTS.md (Sharpened to 8K tokens)

## CFR-000: Prevent File Conflicts
**Rule**: Never allow two agents writing to same file.
**Details**: docs/roadmap/CFR_DETAILS.md:1-200
**Enforcement**: 4 layers (Singleton, Tool, generator, Validation)

## CFR-001: Document Ownership
**Rule**: One owner per file/directory.
**Matrix**: docs/roadmap/CFR_DETAILS.md:201-400
**Enforcement**: generator auto-delegation

## CFR-002: Agent Role Boundaries
**Rule**: One primary role per agent, no overlaps.
**Matrix**: docs/roadmap/CFR_DETAILS.md:401-500

[etc. - all CFRs summarized with pointers]

## Quick Reference
[Essential quick ref only - 1-2 pages]
```

**Step 2**: Create CFR_DETAILS.md (Read On-Demand - NOT in core context)
```markdown
# CFR_DETAILS.md

Lines 1-200: CFR-000 Full Details
Lines 201-400: CFR-001 Full Details including ownership matrix
Lines 401-500: CFR-002 Full Details including role matrix
[etc.]
```

**Result After Optimization**:
```
Core Context Breakdown:
- .claude/agents/project_manager.md: 5K tokens
- docs/roadmap/ROADMAP.md: 15K tokens (Always Read)
- docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md: 8K tokens (Sharpened) ✅
- Tool descriptions: 3K tokens
TOTAL: 31K tokens (52% of 60K budget) ✅ HEALTHY
```

**Savings**: 27K tokens (45% reduction)

### Violation Response

**If Agent Exceeds 30% Budget**:

1. **Detection**: Startup validation fails
2. **Block Deployment**: Agent cannot start
3. **Error Message**:
   ```
   🚨 CONTEXT BUDGET VIOLATION - CFR-007

   Agent: project_manager
   Core Context: 68,000 tokens
   Max Allowed (30%): 60,000 tokens
   Overage: 8,000 tokens (34% of context window)

   REMEDIATION REQUIRED:
   1. Sharpen owned documents (recommended)
   2. Split into indexed structure
   3. Move detail to Read On-Demand documents

   Owned Documents:
   - docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md: 35K tokens ⚠️
   - docs/roadmap/ROADMAP.md: 15K tokens
   - docs/roadmap/TEAM_COLLABORATION.md: 10K tokens

   SUGGESTED ACTION:
   Sharpen CRITICAL_FUNCTIONAL_REQUIREMENTS.md to <10K tokens
   Create CFR_DETAILS.md for full details
   ```

4. **Owner Takes Action**: code_developer (owns .claude/agents/) OR document owner
5. **Verify Fix**: Re-run context measurement
6. **Deploy**: Once budget compliant, agent can start

### Benefits

**For Agents**:
- Always have room to work (70% context available)
- Can read additional files as needed
- Can generate thoughtful, complete responses
- No truncation of critical instructions

**For System**:
- Agents remain effective over time
- Scalable as documents grow
- Clear optimization path when needed
- Proactive management prevents crisis

**For Users**:
- Agents consistently perform well
- No degradation over time
- Fast response (agents not context-choked)
- Reliable system behavior

### Integration with Other CFRs

**CFR-005** (Ownership Includes Maintenance):
- Owners must monitor context budget of owned docs
- When doc grows >threshold: Split or sharpen
- Maintenance includes context optimization

**CFR-001** (Document Ownership):
- Owner responsible for keeping owned docs within budget
- Owner must sharpen if needed
- Owner creates detail documents as needed

**Agent File Access Patterns**:
- "Always Read" docs count toward 30%
- "Read On-Demand" docs do NOT count toward 30%
- Clear distinction required in agent definitions

### Success Criteria

**Healthy System**:
- ✅ All agents <70% context budget
- ✅ Clear "Always Read" vs "Read On-Demand" distinction
- ✅ Main documents are indexes with line references
- ✅ Detail documents available when needed
- ✅ Monthly context budget reviews performed
- ✅ No agent deployment blocked by context violations

**Unhealthy System** (needs attention):
- ❌ Any agent >90% context budget
- ❌ Verbose "Always Read" documents
- ❌ No indexed structure
- ❌ Agents can't read additional files
- ❌ Context violations blocking deployment

### Enforcement Timeline

**Immediate** (2025-10-16):
- Add CFR-007 to CRITICAL_FUNCTIONAL_REQUIREMENTS.md ✅
- Update CLAUDE.md with context budget requirement
- Create context measurement script

**Phase 1** (Next 1-2 weeks):
- Measure all agents' current context usage
- Identify agents >70% (optimization needed)
- Create optimization plans for high-usage agents

**Phase 2** (Next 2-4 weeks):
- Implement optimizations (sharpen, split, index)
- Deploy context validation at agent startup
- Establish monthly review process

**Ongoing**:
- Monthly context budget reports
- Proactive optimization when >70%
- Maintain all agents <90%

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

## CFR-012: Agent Responsiveness Priority (Immediate Requests Override Background Work)

**Rule**: ALL agents MUST prioritize immediate requests from users or other agents OVER their continuous background work loops.

**Core Principle**:
```
Priority 1 (HIGHEST): User requests
Priority 2 (HIGH): Inter-agent delegation requests
Priority 3 (NORMAL): Continuous background work
```

**Why This Is Critical**:

1. **Team Collaboration is Priority**: Focus is encouraged, but teamwork takes precedence
2. **Responsiveness Matters**: Users and agents shouldn't wait while background work runs
3. **Dynamic Task Assignment**: Work priorities change; agents must adapt
4. **Prevent Isolation**: Agents can't ignore the team while doing background tasks

**Real-World Example**:
```
architect is in continuous loop creating specs for future priorities
  ↓
user_listener: "architect, review PRIORITY 9 spec - it's blocking implementation"
  ↓
architect MUST:
  ✅ INTERRUPT background work immediately
  ✅ Handle the urgent request
  ✅ THEN resume background work after

architect MUST NOT:
  ❌ Ignore request and continue background loop
  ❌ Say "I'm busy with continuous work"
  ❌ Delay response until loop completes
```

### Enforcement

**Every agent's continuous work loop MUST**:

```python
while True:  # Continuous mode
    # Priority 1: Check for immediate requests
    if has_user_request() or has_agent_delegation():
        handle_immediately()  # INTERRUPT loop
        # Resume loop after handling

    # Priority 3: Background work
    do_continuous_background_work()
```

**Work Loop Pattern**:
```
CONTINUOUS AGENT WORKFLOW:

┌─────────────────────────────────────┐
│  Check: Any immediate requests?     │
│  - User asking something?            │
│  - Another agent needs help?         │
└──────────┬──────────────────────────┘
           │
           ├─YES──► INTERRUPT background work
           │        Handle request immediately
           │        Resume background work after
           │
           └─NO───► Continue background work
                    - Create specs
                    - Analyze code
                    - Monitor progress
                    - Generate reports
                    └─► Loop back to check requests
```

### Examples

**✅ CORRECT: architect prioritizes user request**:
```
architect: [Creating SPEC-068 in background loop...]

user: "architect, is SPEC-050 ready for implementation?"

architect: [INTERRUPTS SPEC-068 creation]
architect: "Yes, SPEC-050 is complete. Here's the summary: ..."
architect: [RESUMES SPEC-068 creation after answering]
```

**✅ CORRECT: code_developer handles delegation**:
```
code_developer: [Implementing SPEC-050 phase 3...]

project_manager: "code_developer, urgent bug in notifications.py"

code_developer: [SAVES current work]
code_developer: [SWITCHES to bug fix]
code_developer: "Bug fixed, tests passing"
code_developer: [RESUMES SPEC-050 phase 3]
```

**❌ INCORRECT: agent ignores request**:
```
architect: [Creating SPEC-069...]

user: "architect, review this spec please"

architect: [Continues SPEC-069 creation, ignores user]
architect: [Completes entire background loop first]
architect: [Finally responds 30 minutes later]

→ VIOLATION: User had to wait unnecessarily
```

### Implementation Requirements

1. **Request Detection**: Agents must check for new requests at start of each loop iteration
2. **Immediate Interruption**: Background work paused immediately when request arrives
3. **Context Preservation**: Save background work state before interrupting
4. **Resume After**: Return to background work after handling request
5. **Clear Communication**: Acknowledge receipt of urgent requests

### Relationship to Other CFRs

**CFR-000 (File Conflicts)**: Still applies - interrupted agent can't violate ownership
**CFR-008 (Architect Creates Specs)**: User/agent requests override background spec creation
**CFR-011 (Code-searcher Integration)**: Daily integration can be interrupted for urgent needs

### There is Always Work Left

**Key Insight**: "There is always some work left that the agent could do"

- **architect**: Always more complexity to analyze, specs to improve, patterns to document
- **code_developer**: Always more refactoring, test coverage, code quality improvements
- **project_manager**: Always more coordination, metrics tracking, strategic planning
- **assistant**: Always more testing, demos to create, documentation to improve
- **code-searcher**: Always more analysis, security audits, pattern detection

**But**: This continuous work must yield to immediate team needs.

### Success Metrics

- **Response Time**: How quickly do agents respond to requests?
- **Interruption Smoothness**: Do agents cleanly pause/resume work?
- **Team Coordination**: Are agents helping each other effectively?
- **User Satisfaction**: Do users feel agents are responsive?

**User Story**: US-055: Agent Continuous Work with Interruption Handling

---

## CFR-013: All Agents Must Work on `roadmap` Branch Only

**Rule**: ALL agents MUST stay on the `roadmap` branch at ALL times. NO agent can switch branches or create new branches.

**Core Principle**:
```
✅ ALLOWED: Work on roadmap branch
❌ FORBIDDEN: git checkout <other-branch>
❌ FORBIDDEN: git checkout -b <new-branch>
❌ FORBIDDEN: Working on main branch
❌ FORBIDDEN: Working on feature/* branches
```

**Why This Is Critical**:

1. **Single Source of Truth**: All work happens in one place - easy to track and coordinate
2. **No Branch Conflicts**: Eliminates merge conflicts between parallel feature branches
3. **Simplified Workflow**: No confusion about which branch has latest work
4. **Prevents Work Loss**: All commits immediately visible to entire team
5. **Easier Rollback**: Single branch history simplifies reverting changes

**Real-World Problem This Solves**:
```
BEFORE CFR-013 (chaotic):
- code_developer creates feature/us-047-architect-only-specs
- architect creates feature/us-048-silent-background-agents
- project_manager updates roadmap branch
→ Result: Work scattered across 3 branches
→ Result: Merge conflicts when trying to combine
→ Result: Lost track of what's where

AFTER CFR-013 (clean):
- ALL agents work on roadmap branch
- code_developer commits to roadmap
- architect commits to roadmap
- project_manager commits to roadmap
→ Result: All work immediately visible
→ Result: No merge conflicts
→ Result: Perfect coordination
```

### Enforcement

**Git Operations - ALLOWED**:
```bash
✅ git status              # Check status
✅ git add <files>         # Stage changes
✅ git commit -m "..."     # Commit to roadmap
✅ git push origin roadmap # Push to remote
✅ git pull origin roadmap # Pull latest
✅ git log                 # View history
✅ git diff                # View changes
```

**Git Operations - FORBIDDEN**:
```bash
❌ git checkout main                    # CFR-013 VIOLATION
❌ git checkout feature/my-branch       # CFR-013 VIOLATION
❌ git checkout -b feature/new-branch   # CFR-013 VIOLATION
❌ git switch main                      # CFR-013 VIOLATION
❌ git branch new-branch                # CFR-013 VIOLATION
```

**Error Message on Violation**:
```
CFR-013 VIOLATION: Attempted to switch away from roadmap branch

Current branch: roadmap
Attempted checkout: feature/my-feature
Violating agent: code_developer

CFR-013 requires ALL agents to work on roadmap branch ONLY.
Switching branches is FORBIDDEN.

✅ ALLOWED: git add/commit/push on roadmap branch
❌ FORBIDDEN: git checkout <other-branch>

Reason: Single source of truth, prevents branch conflicts, simplifies coordination.
```

### Implementation

**Pre-Commit Hook** (Recommended):
```bash
#!/bin/bash
# .git/hooks/pre-commit

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "roadmap" ]; then
    echo "❌ CFR-013 VIOLATION: You are on branch '$CURRENT_BRANCH'"
    echo "   ALL work must happen on 'roadmap' branch"
    echo "   Run: git checkout roadmap"
    exit 1
fi
```

**Agent Validation** (Before git operations):
```python
def validate_cfr_013():
    """Ensure agent is on roadmap branch before any git operation."""
    import subprocess

    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        text=True
    ).strip()

    if current_branch != "roadmap":
        raise CFR013ViolationError(
            f"CFR-013 VIOLATION: Currently on branch '{current_branch}'. "
            f"ALL agents must work on 'roadmap' branch ONLY. "
            f"Run: git checkout roadmap"
        )
```

### Examples

**✅ CORRECT: Agent stays on roadmap**:
```
code_developer: [Currently on roadmap branch]
code_developer: [Edits coffee_maker/autonomous/daemon.py]
code_developer: git add coffee_maker/autonomous/daemon.py
code_developer: git commit -m "feat: Add feature X"
code_developer: git push origin roadmap

✅ All work done on roadmap branch - CFR-013 compliant
```

**✅ CORRECT: Agent pulls latest before working**:
```
architect: git checkout roadmap  # Already on roadmap, this is safe
architect: git pull origin roadmap  # Get latest changes
architect: [Creates SPEC-066.md]
architect: git add docs/architecture/specs/SPEC-066.md
architect: git commit -m "docs: Add SPEC-066"

✅ Stays on roadmap throughout - CFR-013 compliant
```

**❌ INCORRECT: Agent switches to feature branch**:
```
code_developer: git checkout -b feature/my-feature  # CFR-013 VIOLATION!
code_developer: [Makes changes]
code_developer: git commit -m "feat: Add feature"

❌ Created feature branch - CFR-013 VIOLATION
❌ Work isolated from team - CFR-013 VIOLATION
❌ REQUIRED: Switch back to roadmap and commit there
```

**❌ INCORRECT: Agent works on main**:
```
project_manager: git checkout main  # CFR-013 VIOLATION!
project_manager: [Updates ROADMAP.md]
project_manager: git commit -m "docs: Update roadmap"

❌ Worked on main instead of roadmap - CFR-013 VIOLATION
❌ Changes not visible to team on roadmap - CFR-013 VIOLATION
❌ REQUIRED: Work on roadmap branch only
```

### Exceptions

**NONE**. There are NO exceptions to CFR-013.

- **ALL agents** (code_developer, architect, project_manager, assistant, etc.) work on roadmap
- **ALL work** (code, docs, specs, reports, etc.) goes to roadmap
- **ALL commits** happen on roadmap branch

**Release Process** (Future):
When ready to release, a designated human maintainer can:
1. Merge roadmap → main
2. Tag the release
3. Deploy from main

But agents NEVER do this - they always work on roadmap.

### Git Tagging on Roadmap Branch

**Complementary Strategy**: While CFR-013 requires all work on `roadmap` branch, git tags provide version markers and rollback points WITHOUT needing separate branches.

**Tag Types** (See GUIDELINE-004 for complete details):

1. **`wip-*`** (Work In Progress) - created by code_developer
   - After implementation complete with tests passing
   - Example: `wip-us-047`

2. **`dod-verified-*`** (DoD Verified) - created by project_manager
   - After Puppeteer testing confirms DoD satisfied
   - Example: `dod-verified-us-047`

3. **`milestone-*`** (Major Milestone) - created by project_manager
   - After completing major feature or epic
   - Example: `milestone-priority-9`

4. **`stable-v*.*.*`** (Stable Release) - created by project_manager
   - Production-ready release with semantic versioning
   - Example: `stable-v1.3.0`

**Example Workflow**:
```bash
# All work on roadmap branch (CFR-013)
git branch
# * roadmap  ✅

# code_developer: Mark implementation complete
git tag -a wip-us-047 -m "US-047 implementation complete, awaiting DoD"
git push origin wip-us-047

# project_manager: Mark DoD verified
git tag -a dod-verified-us-047 -m "US-047 DoD verified with Puppeteer"
git push origin dod-verified-us-047

# project_manager: Mark stable release
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement"
git push origin stable-v1.3.0

# Result: Progressive stability markers on single branch ✅
```

**Benefits of Tags + Single Branch**:
- Version tracking without branch complexity
- Rollback points without merge conflicts
- CI/CD deployment from `stable-*` tags
- Clear progression: wip → dod-verified → stable
- Complements CFR-013 perfectly

**Reference**: See `docs/architecture/guidelines/GUIDELINE-004-git-tagging-strategy.md` for comprehensive tagging guidelines, examples, and best practices.

### Relationship to Other CFRs

**CFR-000 (Prevent File Conflicts)**: Working on single branch reduces merge conflicts
**CFR-001 (Document Ownership)**: Ownership applies regardless of branch, but single branch simplifies
**CFR-008 (Architect Creates Specs)**: architect creates specs on roadmap branch
**CFR-012 (Agent Responsiveness)**: Agents can interrupt work, but always on roadmap branch
**GUIDELINE-004 (Git Tagging)**: Tags provide version markers on roadmap branch without needing feature branches

### Success Metrics

- **Branch Compliance**: 100% of commits on roadmap branch
- **No Feature Branches**: Zero feature/* branches created by agents
- **Team Visibility**: All team members see all work immediately
- **Merge Conflicts**: Reduced to near-zero (only from concurrent edits)

**Enforcement**: Code-level validation before any git checkout operation
**Monitoring**: Track git history to ensure no feature branches created
**User Story**: US-056: Single Branch Workflow Enforcement (to be created)

---

## Agent File Access Patterns

**Purpose**: Agents should KNOW which files to read, not search for them.

### The Rule: Context Upfront, Not Discovery During Execution

**Principle**: Each agent should have their required files SPECIFIED in their role definition.

**Why**:
- **Performance**: No wasteful Glob/Grep during execution
- **Clarity**: Clear what agent needs to function
- **Predictability**: Reproducible behavior
- **Separation of Concerns**: code-searcher handles discovery

### Required Files by Agent

Each agent's `.claude/agents/[agent_name].md` should include:

```markdown
## Required Files (Context)

**Always Read Before Work**:
- File 1: Why needed
- File 2: Why needed
- File 3: Why needed
```

**Example Specifications**:

**code_developer**:
```markdown
## Required Files (Context)

**Always Read Before Work**:
- docs/roadmap/ROADMAP.md - Source of priorities to implement
- .claude/CLAUDE.md - Project instructions and standards
- .claude/agents/code_developer.md - Own role definition

**Read When Implementing Priority X**:
- docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md - Strategic requirements (if exists)
- docs/architecture/specs/SPEC-*-*.md - Technical design (if exists)
- docs/architecture/guidelines/GUIDELINE-*.md - Implementation patterns (as needed)

**Never Search**: code_developer should NOT use Glob/Grep during implementation.
**Exception**: May search codebase to understand existing implementation patterns.
```

**project_manager**:
```markdown
## Required Files (Context)

**Always Read Before Work**:
- docs/roadmap/ROADMAP.md - Master task list (owns this)
- docs/roadmap/TEAM_COLLABORATION.md - Agent collaboration guide
- docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md - System invariants
- .claude/CLAUDE.md - Project instructions

**Never Search**: project_manager should NOT use Glob/Grep for strategic work.
```

**architect**:
```markdown
## Required Files (Context)

**Always Read Before Work**:
- docs/roadmap/ROADMAP.md - Understand requirements
- .claude/CLAUDE.md - Project architecture standards
- docs/architecture/decisions/ADR-*.md - Past architectural decisions (skim existing)
- docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md - Strategic requirements to design for

**May Search**: architect MAY use code-searcher for codebase analysis when designing.
```

**assistant**:
```markdown
## Required Files (Context)

**Always Read Before Work**:
- docs/roadmap/ROADMAP.md - Full project context
- .claude/CLAUDE.md - Complete project instructions
- .claude/agents/assistant.md - Own role definition

**May Search**: assistant delegates to code-searcher for deep code analysis.
**For Simple Queries**: assistant uses Grep/Read for 1-2 file lookups.
```

**code-searcher**:
```markdown
## Required Files (Context)

**Always Read Before Work**:
- None - code-searcher DISCOVERS files (that's the role)

**Primary Tool**: Glob, Grep, Read (for discovery and analysis)
```

### When to Use code-searcher

**Delegate to code-searcher when**:
- "Find all files that..."
- "Where is X implemented?"
- "Analyze security patterns across..."
- "Identify code reuse opportunities..."

**Don't use code-searcher for**:
- Reading known files (just use Read tool)
- Reading agent's own context files
- Reading well-documented paths in CLAUDE.md

### Performance Impact

**BAD (wasteful)**:
```python
# code_developer during implementation
roadmap_files = glob("docs/**/*ROADMAP*")  # ❌ Searching! Why?
for f in roadmap_files:
    # ... check if it's the right one
```

**GOOD (efficient)**:
```python
# code_developer during implementation
roadmap = read_file("docs/roadmap/ROADMAP.md")  # ✅ Known path!
```

### Exception: Intentional Discovery

**Only acceptable time to search**:
- Agent is new and learning the codebase structure
- Explicit discovery task: "Find all test files"
- code-searcher delegated task
- architect analyzing codebase patterns for design

### Enforcement

**During agent invocation**:
1. Agent receives context files in prompt or configuration
2. Agent reads specified files upfront
3. Agent works with known context
4. Agent delegates to code-searcher if discovery needed

**generator should**:
- Provide context files to agents when routing
- Log if agent uses Glob/Grep unexpectedly
- Create reflection trace: "Agent searched for files - should context be clearer?"

### Benefits

**Performance**:
- No wasteful file system operations
- Faster agent startup
- Predictable execution time

**Clarity**:
- Clear what agent needs
- Obvious if context is missing
- Easy to debug issues

**Maintainability**:
- Single source of truth for agent context
- Easy to update when file paths change
- Clear separation of concerns

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

### I need to write to a file
→ Use your WRITE tool: `write_file(path, content)`
→ If ownership violation: Error tells you who owns it
→ Delegate to owner using delegation tool

### I need to read a file
→ Use READ tool: `read_file(path)`
→ Always allowed - any agent can read any file
→ Reading never causes conflicts

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

## Parallel Execution Enabled by CFR-000

**Key Insight**: Because we enforce file conflict prevention (CFR-000), parallel agent execution is SAFE.

**User Request** (2025-10-16):
> "I don't understand why I hardly see some agents working in parallel: this is not the expected behavior, we want agents to work in parallel as much as possible in order to deliver faster"

**Why Parallel Execution Is Safe**:

Thanks to our CFR enforcement:
1. **CFR-000**: No file conflicts possible (ownership enforced at tool level)
2. **US-035**: Singleton prevents same-agent conflicts (one instance per agent type)
3. **US-038**: File ownership prevents cross-agent conflicts (different directories)
4. **CFR-001**: Clear ownership boundaries (no ambiguity about who owns what)

**Parallel Execution Matrix**:

| Agent 1 | Working On | Agent 2 | Working On | Safe? | Why? |
|---------|-----------|---------|-----------|-------|------|
| code_developer | coffee_maker/ | project_manager | docs/roadmap/ | ✅ PARALLEL SAFE | Different files (CFR-001) |
| code_developer | coffee_maker/ | architect | docs/architecture/ | ✅ PARALLEL SAFE | Different files (CFR-001) |
| project_manager | docs/roadmap/ | architect | docs/architecture/ | ✅ PARALLEL SAFE | Different files (CFR-001) |
| assistant | Creating demo | code_developer | Implementing | ✅ PARALLEL SAFE | assistant read-only |
| code_developer #1 | coffee_maker/ | code_developer #2 | coffee_maker/ | ❌ SEQUENTIAL ONLY | Singleton (US-035) |
| project_manager #1 | ROADMAP.md | project_manager #2 | ROADMAP.md | ❌ SEQUENTIAL ONLY | Singleton (US-035) |

**Example Parallel Workflow**:

```
Time 0:
  - code_developer: Implementing US-038 Phase 2 (coffee_maker/)
  - project_manager: Writing strategic spec for US-045 (docs/roadmap/)
  - assistant: Creating demo for US-036 (read-only, no files)
  - architect: Designing technical spec for US-046 (docs/architecture/)

All 4 agents working SIMULTANEOUSLY - no conflicts!

Sequential would take: 4 × 30 minutes = 120 minutes
Parallel takes: max(30, 30, 30, 30) = 30 minutes
Speedup: 4x faster! 🎉
```

**How US-043 Will Enable This**:

US-043 (Parallel Agent Execution) creates a ParallelTaskScheduler that:
1. Accepts multiple tasks in a queue
2. Checks for conflicts using CFR enforcement:
   - File ownership conflicts (CFR-001, US-038)
   - Singleton constraints (US-035)
   - Dependencies between tasks
   - Resource limits (CPU, memory)
3. Schedules non-conflicting tasks in parallel (up to 4-6 agents)
4. Queues conflicting tasks until safe to execute
5. Monitors resource usage and throttles if needed

**Performance Impact**:

- **Expected Speedup**: 3-4x for independent tasks
- **Current State**: Mostly sequential execution
- **Target State**: 4-6 agents working in parallel when safe
- **Scheduling Overhead**: <100ms per task
- **Resource Efficiency**: <50% CPU, <4GB memory

**Safety Guarantees**:

All parallel execution respects CFRs:
- ✅ No file conflicts (CFR-000) - enforced by ownership checks
- ✅ No singleton violations (US-035) - enforced by agent registry
- ✅ No ownership violations (CFR-001) - enforced by FileOwnership registry
- ✅ No role confusion (CFR-002) - each agent stays in their role
- ✅ No overlaps (CFR-003, CFR-004) - clear boundaries maintained

**Implementation Status**:

- ✅ CFR-000 (File Conflict Prevention) - COMPLETE
- ✅ US-035 (Singleton Enforcement) - COMPLETE
- ✅ US-038 Phase 1 (File Ownership Registry) - COMPLETE
- 📝 US-043 (Parallel Task Scheduler) - PLANNED (HIGH PRIORITY)

This means US-043 (Parallel Execution) can be implemented safely thanks to CFR enforcement.

**Related**:
- docs/roadmap/ROADMAP.md - US-043 full specification
- User feedback: Performance is critical priority

---

**Remember**: These CFRs exist to prevent the system from breaking itself. They are not optional. They are not suggestions. They are CRITICAL FUNCTIONAL REQUIREMENTS.

**Version**: 2.2
**Last Updated**: 2025-10-17
**Next Review**: After US-038, US-039, US-043, US-044, and US-056 implementation

**Changelog**:
- **v2.2** (2025-10-17): Added CFR-013 (All Agents Must Work on roadmap Branch Only)
  - NO agent can switch branches (git checkout forbidden)
  - ALL work happens on roadmap branch (single source of truth)
  - Prevents: Branch conflicts, scattered work, merge complexity
  - Benefits: Team visibility, simpler coordination, reduced conflicts
  - Enforcement: Pre-commit hook + agent validation before git operations
  - Zero exceptions - ALL agents work on roadmap
  - Release process: Only human maintainers merge roadmap → main
  - Related: US-056 (Single Branch Workflow Enforcement - to be created)
- **v2.1** (2025-10-17): Added CFR-012 (Agent Responsiveness Priority)
  - Immediate user/agent requests override continuous background work
  - Priority: User requests (P1) > Inter-agent delegations (P2) > Background work (P3)
  - Enforcement: Check for requests at start of each loop iteration
  - Context preservation: Save state before interrupting
  - Key principle: "Team collaboration is priority - focus encouraged but teamwork takes precedence"
  - Key insight: "There is always some work left" - continuous work must yield to team needs
  - Related: US-055 (Agent Continuous Work with Interruption Handling)
- **v2.0** (2025-10-17): Added CFR-011 (Architect Must Integrate code-searcher Findings Daily)
- **v1.8** (2025-10-16): Added CFR-007 (Agent Context Budget - 30% Maximum)
  - New CFR-007: Agent core materials must fit in ≤30% of context window
  - Core materials: prompt, role, responsibilities, tools, owned critical documents
  - Remaining 70% reserved for actual work
  - Remediation strategies: Sharpen docs, create detail docs, use line references, compress examples
  - Main docs become indexes pointing to detail docs with line numbers
  - "Always Read" docs counted in 30%, "Read On-Demand" docs not counted
  - Monthly context budget reports required
  - Thresholds: <70% healthy, 71-90% warning, 91-100% critical, >100% violation
  - Startup validation blocks agent if budget exceeded
  - Integrates with CFR-005 (maintenance includes context optimization)
  - Enforcement timeline: Immediate (add CFR), Phase 1 (measure), Phase 2 (optimize), Ongoing (monitor)
- **v1.7** (2025-10-16): Added CFR-006 (Lessons Learned Must Be Captured and Applied)
  - New CFR-006: All failures, mistakes, and key lessons MUST be documented, owned, and actively used
  - project_manager owns docs/roadmap/learnings/ (exclusive ownership)
  - Lesson types: Workflow failures, technical failures, user frustration, success patterns, monthly summaries
  - Lesson capture workflow: Any agent identifies → delegates to project_manager → creates lesson document
  - Lesson document template with severity, category, root cause, impact, prevention
  - Required reading schedule: Weekly (last 7 days), Monthly (current month), Quarterly (full review)
  - Integration points: agent definitions, CFRs, US-039 validation, reflector, curator
  - Maintenance: Monthly summaries, quarterly reviews, archive old lessons
  - Escalation path for recurring patterns
  - Success criteria: All failures documented <24h, no recurring mistakes, continuous improvement
  - Why critical: Without lessons system, same mistakes repeat endlessly and user trust degrades
  - Updated ownership matrix with docs/roadmap/learnings/ (project_manager)
  - Examples: WORKFLOW_FAILURE_US_040.md, OWNERSHIP_VIOLATION_US_038.md already captured
- **v1.6** (2025-10-16): Added CFR-005 (Ownership Includes Maintenance Responsibility) and US-044 Integration
  - New CFR-005: Ownership means proactive maintenance (cleaning, simplifying, updating, organizing)
  - Updated ownership matrix (CFR-001) with maintenance duties column
  - architect monitors code quality weekly and creates refactoring plans
  - code_developer executes refactoring based on architect's detailed plans
  - All owners must maintain their files/directories (CFR-005)
  - Maintenance workflow: Regular, triggered, and proactive maintenance schedules
  - Enforcement: Self-check, architect monitoring, project_manager monitoring, user review
  - Metrics: Healthy vs. unhealthy ownership indicators
  - Related: US-044 (Regular Refactoring and Technical Debt Reduction Workflow)
- **v1.5** (2025-10-16): Added "Parallel Execution Enabled by CFR-000" section
  - Documented why parallel execution is SAFE (thanks to CFR enforcement)
  - Parallel execution matrix showing safe/unsafe combinations
  - Example parallel workflow (4 agents, 4x speedup)
  - How US-043 will enable parallel task scheduling
  - Performance impact expectations (3-4x speedup)
  - Safety guarantees (all CFRs respected during parallel execution)
  - Implementation status of prerequisites (US-035, US-038 Phase 1 complete)
  - Related: US-043 (Parallel Agent Execution) - HIGH PRIORITY user request
- **v1.4** (2025-10-16): Added Agent File Access Patterns (Performance & Clarity)
  - Context-upfront principle: agents KNOW which files to read
  - No wasteful Glob/Grep during execution (except code-searcher)
  - Clear "Required Files (Context)" specification for each agent
  - Performance optimization: predictable, fast agent startup
  - code-searcher handles discovery tasks (separation of concerns)
  - generator monitors unexpected file searches
  - Related: US-042 implementation
- **v1.3** (2025-10-16): Added Ownership-Aware File Tools
  - Tool-level enforcement of CFR-000 (Layer 2 protection)
  - READ tool unrestricted for all agents
  - WRITE tool pre-configured with ownership boundaries per agent
  - Automatic blocking with clear error messages
  - Integration with delegation tool
  - Centralized tool configuration in file_tool_config.py
  - Four-layer defense in depth strategy documented
  - Updated Quick Reference with file tool usage
- **v1.2** (2025-10-16): Added CFR-000 (MASTER REQUIREMENT) - Prevent File Conflicts At All Costs
  - All other CFRs now explicitly derive from CFR-000
  - Documented singleton exception for agents that own no files
  - Added enforcement strategy with 4-level checks
  - Updated Quick Reference with master rule
- **v1.1** (2025-10-16): Added Task Delegation Tool, Complexity Escalation Workflow, Enhanced Quick Reference
- **v1.0** (2025-10-16): Initial creation with CFR-001 through CFR-004, enforcement mechanisms
