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

## Ownership Structure

### project_manager Owns

**Full Write Control**:
- `docs/*.md` (all top-level markdown files)
- `docs/roadmap/` (strategic planning)
  - `ROADMAP.md` (strategic updates only; code_developer updates status fields)
  - `TEAM_COLLABORATION.md`
- `docs/templates/` (documentation templates)
- `docs/tutorials/` (tutorial content)
- `docs/code-searcher/` (code analysis documentation)

**Shared Write (with clear boundaries)**:
- `docs/roadmap/ROADMAP.md`
  - **project_manager**: Strategic updates (add/remove priorities, change order, modify descriptions)
  - **code_developer**: Status updates only (Planned → In Progress → Complete, progress percentages)

**Documentation Delegation Pattern**:
- **code-searcher** prepares findings → **assistant** receives → **assistant** delegates to **project_manager** → **project_manager** writes docs
- **code-searcher** and **assistant** NEVER write directly to docs/

---

### code_developer Owns

**Full Write Control**:
- `coffee_maker/` (all implementation code)
- `tests/` (all test code)
- `scripts/` (utility scripts)
- `pyproject.toml` (dependency management)
- `poetry.lock` (dependency lock)
- `.pre-commit-config.yaml` (pre-commit configuration)
- `.claude/` (technical configurations)
  - `.claude/agents/` (agent definitions and configurations)
  - `.claude/CLAUDE.md` (technical setup and implementation guide)
  - `.claude/commands/` (prompt templates)
  - `.claude/mcp/` (MCP server configurations)

**Shared Write (with clear boundaries)**:
- `docs/roadmap/ROADMAP.md`
  - **Status updates only**: Planned → In Progress → Complete
  - **Progress tracking**: Percentage complete
  - **Does NOT** modify: Priority order, descriptions, strategic content

---

### user_interpret Owns

**Full Write Control**:
- `docs/user_interpret/` (user interaction documentation)
  - `IMPLEMENTATION_SUMMARY.md`
  - `README.md`

**NOTE**: This is documentation ABOUT user_interpret, not operational data.

**Operational Data** (NOT docs/):
- `data/user_interpret/` (future location - not yet created)
  - `conversation_history.jsonl`
  - `user_requests.json`
  - `conversation_summaries.json`

**Current State**: user_interpret docs are in `docs/user_interpret/` which creates confusion.

**Resolution**: See "Overlap Resolution" section below.

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

### architect Owns

**Full Write Control**:
- `docs/architecture/` (all architectural documentation)
  - `docs/architecture/specs/` (detailed technical specifications)
  - `docs/architecture/decisions/` (Architectural Decision Records - ADRs)
  - `docs/architecture/guidelines/` (implementation guidelines for code_developer)
  - `docs/architecture/README.md` (architecture documentation overview)

**Workflow**:
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

**DEPRECATED** - Removed completely

Previously owned: `.claude/CLAUDE.md` (synchronization updates)

**Status**: No longer needed due to tag-based workflow (no branch switching)
**New Owner**: code_developer owns `.claude/CLAUDE.md` as technical configuration

---

## Overlap Detection

### Identified Overlap: docs/user_interpret/

**Problem**: `docs/user_interpret/` contains documentation ABOUT user_interpret

**Current Ownership**:
- Directory exists in `docs/` (project_manager territory)
- Contains user_interpret-specific docs
- Creates confusion: Is this docs or operational data?

**Analysis**:
- `docs/user_interpret/IMPLEMENTATION_SUMMARY.md` - Documentation ABOUT user_interpret implementation
- `docs/user_interpret/README.md` - Documentation ABOUT user_interpret agent

**Verdict**: This is META-DOCUMENTATION about the agent, not operational data.

**Resolution**: Keep in `docs/user_interpret/` as project_manager owned documentation.

**Future Operational Data**: If user_interpret needs to store conversation logs, those should go in `data/user_interpret/` (not docs/)

---

## Overlap Resolution Plan

### Resolved: No Current Overlaps Detected

After thorough analysis:

1. **docs/user_interpret/**: Correctly located (project_manager owned)
   - Contains documentation ABOUT the agent
   - Does NOT contain operational data
   - No overlap

2. **docs/roadmap/ROADMAP.md**: Clear boundaries defined
   - project_manager: Strategic updates
   - code_developer: Status updates only
   - No overlap (different fields)

3. **ACE components**: Each has dedicated directory
   - generator: `docs/generator/`
   - reflector: `docs/reflector/`
   - curator: `docs/curator/`
   - No overlap

4. **.claude/CLAUDE.md**: Single owner with clear rules
   - code_developer: Primary owner (technical configurations)
   - memory-bank-synchronizer: DEPRECATED (removed)
   - No overlap

**Conclusion**: Current ownership structure is clean with NO overlaps.

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
