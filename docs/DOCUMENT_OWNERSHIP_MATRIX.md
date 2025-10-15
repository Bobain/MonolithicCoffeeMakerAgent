# Document Ownership Matrix

**Version**: 1.0
**Created**: 2025-10-15
**Last Updated**: 2025-10-15

---

## Critical Rule: NO OVERLAPS

**CRITICAL REQUIREMENT**: NEVER allow two agents to write to the same file or directory.

This is a **non-negotiable requirement** for parallel agent operations. Overlaps cause:
- File conflicts when agents modify the same file
- Lost work when one agent overwrites another's changes
- Confusion about which agent is responsible for what
- Race conditions in git commits

**project_manager is responsible for preventing and detecting overlaps.**

---

## Ownership Structure (NO OVERLAPS)

### CRITICAL RULE: NO PARENT DIRECTORY OWNERSHIP

**NO agent can own a parent directory when subdirectories have different owners.**

Example:
- ❌ WRONG: project_manager owns `docs/` AND architect owns `docs/architecture/` → OVERLAP!
- ✅ CORRECT: project_manager owns `docs/roadmap/`, architect owns `docs/architecture/` → NO overlap

### project_manager Owns

**Full Write Control**:
- `docs/*.md` (top-level markdown files ONLY - not subdirectories)
  - `docs/PRIORITY_*_TECHNICAL_SPEC.md` (strategic specifications)
  - `docs/README.md` (if exists)
  - `docs/CONTRIBUTING.md` (if exists)
- `docs/roadmap/` (strategic planning ONLY)
  - `ROADMAP.md` (strategic updates; code_developer updates status fields)
  - `TEAM_COLLABORATION.md`
- `docs/templates/` (documentation templates)
- `docs/tutorials/` (tutorial content)
- `docs/code-searcher/` (code analysis documentation - project_manager writes reports from code-searcher findings)
- `docs/user_interpret/` (meta-documentation about user_interpret agent)
- `docs/code_developer/` (meta-documentation about code_developer agent)

**Does NOT own**:
- `docs/` (parent directory - would create overlaps)
- `docs/architecture/` (architect owns)
- `docs/generator/` (generator owns)
- `docs/reflector/` (reflector owns)
- `docs/curator/` (curator owns)

**Shared Write (with clear boundaries)**:
- `docs/roadmap/ROADMAP.md`
  - **project_manager**: Strategic updates (add/remove priorities, change order, modify descriptions)
  - **code_developer**: Status updates only (Planned → In Progress → Complete, progress percentages)

**Documentation Delegation Pattern**:
- **code-searcher** prepares findings → **assistant** receives → **assistant** delegates to **project_manager** → **project_manager** writes docs
- **code-searcher** and **assistant** NEVER write directly to docs/

---

### architect Owns

**Full Write Control**:
- `docs/architecture/` (all architectural documentation)
  - `docs/architecture/specs/` (detailed technical specifications)
  - `docs/architecture/decisions/` (Architectural Decision Records - ADRs)
  - `docs/architecture/guidelines/` (implementation guidelines)
- `pyproject.toml` (dependency management - requires user approval)
- `poetry.lock` (dependency lock file)

**Critical Responsibilities**:
- **Proactive approval**: Must ask user before important decisions
- **Dependency management**: ONLY architect can run `poetry add`
- **Code design**: All architectural and design decisions
- **User interaction**: Asks user_listener to present approval requests

**Workflow for Dependencies**:
1. architect analyzes need for new dependency
2. architect requests user approval via user_listener
3. User approves/rejects
4. If approved: architect runs `poetry add [package]`
5. architect documents decision in ADR

**Workflow for Architecture**:
1. architect analyzes architectural requirements
2. architect creates technical specification in `docs/architecture/specs/`
3. architect documents decisions in ADRs (`docs/architecture/decisions/`)
4. architect provides guidelines in `docs/architecture/guidelines/`
5. code_developer reads specifications and guidelines
6. code_developer implements following architect's design
7. architect reviews implementation

**Interaction Pattern**:
- User discusses architecture with architect through user_listener
- architect creates specifications BEFORE implementation
- code_developer reads specifications and implements
- Clear separation: architect designs, code_developer implements

---

### code_developer Owns

**Full Write Control**:
- `coffee_maker/` (all implementation code)
- `tests/` (all test code)
- `scripts/` (utility scripts)
- `.claude/` (technical configurations)
  - `.claude/agents/` (agent definitions and configurations)
  - `.claude/CLAUDE.md` (technical setup and implementation guide)
  - `.claude/commands/` (prompt templates)
  - `.claude/mcp/` (MCP server configurations)
- `.pre-commit-config.yaml` (pre-commit hooks)

**Does NOT own**:
- `pyproject.toml` (architect owns - dependency management)
- `poetry.lock` (architect owns)
- `docs/` (any subdirectory - various owners)

**Shared Write (with clear boundaries)**:
- `docs/roadmap/ROADMAP.md`
  - **Status updates only**: Planned → In Progress → Complete
  - **Progress tracking**: Percentage complete
  - **Does NOT** modify: Priority order, descriptions, strategic content

**CRITICAL**: code_developer CANNOT modify dependencies. Must request architect to add dependencies.

---

### user_interpret Owns

**Full Write Control**:
- `data/user_interpret/` (operational data - future location)
  - `conversation_history.jsonl`
  - `user_requests.json`
  - `conversation_summaries.json`

**Does NOT own**:
- `docs/user_interpret/` (project_manager owns - this is meta-documentation ABOUT user_interpret)

**NOTE**: `docs/user_interpret/` contains documentation ABOUT the agent, not operational data. This is owned by project_manager as strategic documentation.

---

### ACE Components Own

**generator** (Full Write Control):
- `docs/generator/` (execution traces)
  - `README.md`
  - `traces/` (all trace files)

**reflector** (Full Write Control):
- `docs/reflector/` (insights and deltas)
  - `README.md`
  - `deltas/` (all delta files)

**curator** (Full Write Control):
- `docs/curator/` (playbooks and curation)
  - `README.md`
  - `playbooks/` (all playbook files)

---

### code-searcher Owns

**NONE** - code-searcher is READ-ONLY

**Process**:
1. code-searcher performs analysis (READ-ONLY)
2. code-searcher prepares findings report
3. code-searcher presents to assistant
4. assistant delegates to project_manager
5. project_manager creates documentation in `docs/code-searcher/`

**Document Format**: `docs/code-searcher/[analysis_type]_analysis_[date].md`

---

### assistant Owns

**NONE** - assistant is READ-ONLY

**Role**: Documentation expert and intelligent dispatcher
- Reads all documentation
- Answers questions using deep documentation knowledge
- Delegates modifications to appropriate agents

---

### ux-design-expert Owns

**NONE** - ux-design-expert provides specifications, does not write code or docs

**Process**:
1. ux-design-expert provides design specifications
2. code_developer implements design
3. project_manager documents design decisions (if needed)

---

### memory-bank-synchronizer Owns

**DEPRECATED** - Completely removed

Previously owned: `.claude/CLAUDE.md` (synchronization updates)

**Status**: No longer needed due to tag-based workflow (no branch switching)
**New Owner**: code_developer owns `.claude/CLAUDE.md` as technical configuration

---

## Overlap Detection

### ✅ NO OVERLAPS DETECTED

After thorough analysis with the NO PARENT DIRECTORY OWNERSHIP rule:

1. **docs/ directories**: Each subdirectory has EXACTLY one owner
   - `docs/*.md`: project_manager (top-level files ONLY)
   - `docs/roadmap/`: project_manager
   - `docs/architecture/`: architect
   - `docs/generator/`: generator
   - `docs/reflector/`: reflector
   - `docs/curator/`: curator
   - `docs/templates/`: project_manager
   - `docs/tutorials/`: project_manager
   - `docs/code-searcher/`: project_manager
   - `docs/user_interpret/`: project_manager (meta-docs ABOUT user_interpret)
   - `docs/code_developer/`: project_manager (meta-docs ABOUT code_developer)
   - **NO agent owns `docs/` parent directory** ✅

2. **docs/roadmap/ROADMAP.md**: Clear boundaries defined
   - project_manager: Strategic updates (add/remove priorities, descriptions)
   - code_developer: Status updates only (Planned → In Progress → Complete)
   - No overlap (different fields) ✅

3. **Dependency management**: Single owner with clear workflow
   - architect: ONLY owner of `pyproject.toml` and `poetry.lock`
   - code_developer: CANNOT modify dependencies
   - architect: Must request user approval before changes ✅

4. **ACE components**: Each has dedicated directory
   - generator: `docs/generator/`
   - reflector: `docs/reflector/`
   - curator: `docs/curator/`
   - No overlap ✅

5. **.claude/**: Single owner
   - code_developer: Primary owner (all technical configurations)
   - memory-bank-synchronizer: DEPRECATED (completely removed)
   - No overlap ✅

**Conclusion**: Current ownership structure is clean with NO overlaps.

---

## Overlap Prevention Strategy

### Rule Enforcement

1. **NO parent directory ownership when subdirectories have different owners**
2. **Each file/directory has EXACTLY one owner**
3. **Shared write ONLY for specific fields (ROADMAP.md status)**
4. **Runtime validation** (future enhancement)

---

## Enforcement Mechanisms

### 1. Runtime Checks (Future Enhancement)

Create `DocumentOwnershipGuard` class:

```python
class DocumentOwnershipGuard:
    """Enforces document ownership rules"""

    OWNERSHIP = {
        "docs/": "project_manager",
        "docs/generator/": "generator",
        "docs/reflector/": "reflector",
        "docs/curator/": "curator",
        "coffee_maker/": "code_developer",
        "tests/": "code_developer",
        # ... full ownership map
    }

    def check_write(self, agent_name: str, file_path: str):
        """Check if agent can write to file"""
        owner = self.get_owner(file_path)
        if owner != agent_name:
            raise OwnershipViolation(
                f"{agent_name} cannot write to {file_path} (owned by {owner})"
            )
```

### 2. Pre-commit Hooks

Add pre-commit hook to detect ownership violations:

```bash
#!/bin/bash
# .git/hooks/pre-commit-ownership-check

# Check git diff for modified files
# Verify agent-specific commits don't violate ownership
# Warn if suspicious patterns detected
```

### 3. Tests

Create `tests/test_document_ownership.py`:

```python
def test_no_overlapping_ownership():
    """Verify no directory/file has multiple owners"""
    ownership = load_ownership_matrix()

    for path in ownership.keys():
        owners = get_owners(path)
        assert len(owners) == 1, f"{path} has multiple owners: {owners}"
```

### 4. Documentation Review

**project_manager responsibility**:
- Review this document quarterly
- Check for new overlaps when agents are added
- Update ownership rules as project evolves
- Warn user if potential overlaps detected

---

## Verification Checklist

**Run this checklist when adding new agents or directories**:

- [ ] Each directory has EXACTLY one owner
- [ ] Each file has EXACTLY one owner
- [ ] No shared write access (except explicit shared fields in ROADMAP.md)
- [ ] All agents know their owned directories
- [ ] Ownership documented in CLAUDE.md
- [ ] Tests enforce ownership rules (future)
- [ ] Pre-commit hook checks ownership (future)

---

## Examples

### Correct Ownership

**User**: "Update the ROADMAP to add a new priority"

**Flow**:
1. user_listener receives request
2. user_interpret determines intent: modify ROADMAP
3. Delegates to project_manager (owns docs/roadmap/)
4. project_manager updates ROADMAP.md (strategic change)
5. Success - correct owner

---

**User**: "Fix the bug in roadmap_cli.py"

**Flow**:
1. user_listener receives request
2. user_interpret determines intent: code change
3. Delegates to code_developer (owns coffee_maker/)
4. code_developer modifies coffee_maker/cli/roadmap_cli.py
5. Success - correct owner

---

**User**: "Document the authentication system"

**Flow**:
1. user_listener receives request
2. user_interpret determines intent: create documentation
3. Delegates to project_manager (owns docs/)
4. project_manager creates docs/AUTHENTICATION_DESIGN.md
5. Success - correct owner

---

### Incorrect Attempts (Prevented)

**User**: "assistant, update the ROADMAP"

**Flow**:
1. assistant recognizes: I don't own docs/
2. assistant delegates to project_manager
3. project_manager updates ROADMAP.md
4. Success - prevented overlap

---

**User**: "project_manager, fix the CLI bug"

**Flow**:
1. project_manager recognizes: I don't own coffee_maker/
2. project_manager delegates to code_developer
3. code_developer fixes bug
4. Success - prevented overlap

---

## Related Documentation

- `.claude/CLAUDE.md` - Agent Tool Ownership & Boundaries section
- `.claude/agents/README.md` - Agent definitions
- `docs/roadmap/TEAM_COLLABORATION.md` - Team collaboration methodology
- `docs/AGENT_ROLES_AND_BOUNDARIES.md` - Detailed role descriptions (if exists)

---

## Version History

**v1.0 (2025-10-15)**:
- Initial version
- Analyzed all current agents
- Verified NO overlaps exist
- Defined clear ownership rules
- Documented enforcement mechanisms

---

**Maintained By**: project_manager
**Review Frequency**: Quarterly or when adding new agents
**Next Review**: 2026-01-15
