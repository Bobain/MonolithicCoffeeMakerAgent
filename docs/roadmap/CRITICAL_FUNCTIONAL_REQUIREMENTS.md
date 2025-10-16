# Critical Functional Requirements - System Invariants

**Version**: 1.6
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

### Ownership Matrix (with Maintenance Responsibilities - CFR-005)

| Directory/File | Owner | Can Modify? | Maintenance Duties (CFR-005) | Others |
|----------------|-------|-------------|------------------------------|--------|
| **User Interface** | user_listener | ONLY UI for all user interactions | N/A (no files owned) | All others: NO UI (backend only) |
| **docs/*.md** | project_manager | YES - Top-level files ONLY (not subdirectories) | Keep current, remove obsolete, simplify | All others: READ-ONLY |
| **docs/roadmap/** | project_manager | YES - Strategic planning ONLY | Archive completed work, consolidate specs, keep ROADMAP organized | All others: READ-ONLY |
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

**Version**: 1.6
**Last Updated**: 2025-10-16
**Next Review**: After US-038, US-039, US-043, and US-044 implementation

**Changelog**:
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
