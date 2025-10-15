# Ownership Enforcement

**Version**: 1.0
**Date**: 2025-10-15
**Status**: Active

---

## Critical Rules

### Rule 1: NO OVERLAPS
**An agent CANNOT own a parent directory if another agent owns a subdirectory.**

Example:
- ❌ BAD: `docs/` owned by project_manager, `docs/architecture/` owned by architect
- ✅ GOOD: `docs/roadmap/` owned by project_manager, `docs/architecture/` owned by architect

**Why This Matters**:
- Prevents file conflicts when agents modify the same file
- Eliminates confusion about responsibility
- Enables true parallel operations
- Makes ownership validation possible

---

### Rule 2: WRITE RESTRICTION
**An agent can ONLY write to its owned directories (nowhere else).**

Enforced at runtime by `DocumentOwnershipGuard` (future enhancement).

**Examples**:
- ✅ code_developer writes to `coffee_maker/cli/roadmap_cli.py` → ALLOWED
- ❌ code_developer writes to `docs/roadmap/ROADMAP.md` (strategic section) → BLOCKED
- ✅ code_developer writes to `docs/roadmap/ROADMAP.md` (status field only) → ALLOWED (shared write)
- ❌ project_manager writes to `coffee_maker/cli/roadmap_cli.py` → BLOCKED

---

### Rule 3: EXPLICIT OWNERSHIP
**Every writable directory must be explicitly owned.**

No implicit ownership through parent directories.

**Bad Example** (implicit):
```python
# ❌ WRONG - Implicit ownership
"docs/": "project_manager"  # This implies ALL subdirectories
```

**Good Example** (explicit):
```python
# ✅ CORRECT - Explicit ownership
"docs/*.md": "project_manager"        # Top-level files only
"docs/roadmap/": "project_manager"    # Explicit subdirectory
"docs/architecture/": "architect"      # Different owner - NO OVERLAP
```

---

### Rule 4: RUNTIME VALIDATION
**Ownership rules validated on module import.**

System will not start if overlaps detected.

**Validation Checks**:
1. No parent directory ownership when subdirectories have different owners
2. Each path has exactly one owner (except shared write fields)
3. All write operations check ownership before execution
4. Violations raise `OwnershipViolation` exception

---

## Ownership Matrix (Complete)

### Directory Ownership

| Directory | Owner | Purpose |
|-----------|-------|---------|
| `docs/*.md` | project_manager | Top-level doc files (NOT subdirectories) |
| `docs/roadmap/` | project_manager | Strategic planning |
| `docs/architecture/` | architect | Technical specs, ADRs |
| `docs/generator/` | generator | Execution traces |
| `docs/reflector/` | reflector | Insights (deltas) |
| `docs/curator/` | curator | Playbooks |
| `docs/code-searcher/` | project_manager | Code analysis docs |
| `docs/templates/` | project_manager | Doc templates |
| `docs/tutorials/` | project_manager | Tutorials |
| `docs/user_interpret/` | project_manager | user_interpret meta-docs |
| `docs/code_developer/` | project_manager | code_developer meta-docs |
| `coffee_maker/` | code_developer | Implementation code |
| `tests/` | code_developer | Test code |
| `scripts/` | code_developer | Utility scripts |
| `.claude/` | code_developer | Technical configs |
| `.pre-commit-config.yaml` | code_developer | Pre-commit hooks |
| `data/user_interpret/` | user_interpret | Operational data |

### File Ownership (Special Cases)

| File | Owner(s) | Notes |
|------|----------|-------|
| `pyproject.toml` | architect | Dependency management (requires user approval) |
| `poetry.lock` | architect | Dependency lock file |
| `docs/roadmap/ROADMAP.md` | project_manager + code_developer | Shared write (different fields) |

### Shared Write Rules

**docs/roadmap/ROADMAP.md**:
- **project_manager**: Strategic fields
  - Add/remove priorities
  - Change priority order
  - Modify descriptions, acceptance criteria, dependencies
- **code_developer**: Status fields ONLY
  - Update status (Planned → In Progress → Complete)
  - Update progress percentage
  - Add implementation notes (in designated section)

**Enforcement**: Field-level validation (future enhancement)

---

## Verification

### Manual Verification

Run this checklist quarterly or when adding new agents:

- [ ] Each directory has EXACTLY one owner
- [ ] Each file has EXACTLY one owner (or clearly defined shared write)
- [ ] No parent directory ownership when subdirectories have different owners
- [ ] All agents know their owned directories
- [ ] Ownership documented in `.claude/CLAUDE.md`
- [ ] Ownership documented in `docs/DOCUMENT_OWNERSHIP_MATRIX.md`
- [ ] This enforcement guide is up to date

### Automated Verification (Future)

**Command**:
```bash
python -c "from coffee_maker.autonomous.document_ownership import DocumentOwnershipGuard; \
           guard = DocumentOwnershipGuard(); \
           print('✅ No overlaps' if not guard.validate_no_overlaps() else '❌ Overlaps detected')"
```

**Test**:
```bash
pytest tests/unit/test_document_ownership.py::test_no_overlapping_ownership_critical -v
```

---

## Violation Examples

### Example 1: Parent Directory Overlap

**Violation**:
```python
OWNERSHIP = {
    "docs/": "project_manager",           # ❌ Parent directory
    "docs/architecture/": "architect"     # ❌ Subdirectory with different owner
}
```

**Error**: `OwnershipViolation: 'docs/' owned by project_manager but 'docs/architecture/' owned by architect`

**Fix**:
```python
OWNERSHIP = {
    "docs/roadmap/": "project_manager",   # ✅ Explicit subdirectory
    "docs/architecture/": "architect"      # ✅ Different subdirectory
}
```

---

### Example 2: Code Developer Modifying Docs

**Violation**:
```python
# code_developer tries to modify docs/roadmap/ROADMAP.md (strategic section)
with open("docs/roadmap/ROADMAP.md", "w") as f:
    f.write("PRIORITY 100: My new feature")  # ❌ Strategic change
```

**Error**: `OwnershipViolation: code_developer cannot modify strategic section of ROADMAP.md`

**Fix**:
```python
# code_developer only updates status field
roadmap.update_status("US-033", Status.IN_PROGRESS)  # ✅ Status update only
```

---

### Example 3: Code Developer Adding Dependency

**Violation**:
```bash
# code_developer tries to add dependency
poetry add requests  # ❌ BLOCKED
```

**Error**: `OwnershipViolation: Only architect can modify pyproject.toml`

**Fix**:
```
code_developer: "I need requests library"
    ↓
code_developer: Requests architect to add dependency
    ↓
architect: Analyzes, requests user approval
    ↓
architect: Runs `poetry add requests` (after approval)  # ✅ ALLOWED
```

---

### Example 4: Project Manager Modifying Code

**Violation**:
```python
# project_manager tries to fix bug in CLI
with open("coffee_maker/cli/roadmap_cli.py", "w") as f:
    f.write("# Fixed bug")  # ❌ BLOCKED
```

**Error**: `OwnershipViolation: project_manager cannot modify coffee_maker/`

**Fix**:
```
project_manager: Identifies bug
    ↓
project_manager: Delegates to code_developer
    ↓
code_developer: Fixes bug in coffee_maker/cli/roadmap_cli.py  # ✅ ALLOWED
```

---

## Enforcement Mechanisms

### 1. Runtime Guards (Future Enhancement)

**DocumentOwnershipGuard** class:
```python
class DocumentOwnershipGuard:
    """Enforces document ownership rules at runtime"""

    OWNERSHIP_RULES = {
        "docs/roadmap/": {"project_manager"},
        "docs/architecture/": {"architect"},
        "coffee_maker/": {"code_developer"},
        "pyproject.toml": {"architect"},
        # ... full ownership map
    }

    def check_write(self, agent_name: str, file_path: str) -> None:
        """Check if agent can write to file"""
        owner = self.get_owner(file_path)

        # Handle shared write (ROADMAP.md)
        if file_path == "docs/roadmap/ROADMAP.md":
            if agent_name == "code_developer":
                # Only allow status field updates
                if not self.is_status_field_update(file_path):
                    raise OwnershipViolation(
                        f"code_developer can only update status fields in ROADMAP.md"
                    )
            elif agent_name != "project_manager":
                raise OwnershipViolation(
                    f"{agent_name} cannot write to {file_path}"
                )
        elif owner != agent_name:
            raise OwnershipViolation(
                f"{agent_name} cannot write to {file_path} (owned by {owner})"
            )

    def validate_no_overlaps(self) -> bool:
        """Validate no overlapping ownership"""
        for path1 in self.OWNERSHIP_RULES:
            for path2 in self.OWNERSHIP_RULES:
                if path1 != path2 and self.is_parent_child(path1, path2):
                    if self.OWNERSHIP_RULES[path1] != self.OWNERSHIP_RULES[path2]:
                        return False  # Overlap detected
        return True  # No overlaps
```

**Usage**:
```python
from coffee_maker.autonomous.document_ownership import DocumentOwnershipGuard

guard = DocumentOwnershipGuard()

# Before write operation
guard.check_write(agent_name="code_developer", file_path="coffee_maker/cli/foo.py")  # OK
guard.check_write(agent_name="code_developer", file_path="docs/roadmap/ROADMAP.md")  # Error
```

---

### 2. Pre-commit Hooks

**File**: `.git/hooks/pre-commit-ownership-check`

```bash
#!/bin/bash
# Check git diff for ownership violations

# Get changed files
changed_files=$(git diff --cached --name-only)

for file in $changed_files; do
    # Check if file modification violates ownership
    python -c "
from coffee_maker.autonomous.document_ownership import DocumentOwnershipGuard
guard = DocumentOwnershipGuard()
# Validate ownership (implementation details)
"
done
```

---

### 3. Unit Tests

**File**: `tests/unit/test_document_ownership.py`

```python
import pytest
from coffee_maker.autonomous.document_ownership import (
    DocumentOwnershipGuard,
    OwnershipViolation
)


def test_no_overlapping_ownership_critical():
    """CRITICAL: Verify no directory/file has overlapping owners"""
    guard = DocumentOwnershipGuard()

    # This test MUST PASS for system to be valid
    assert guard.validate_no_overlaps(), "Overlapping ownership detected!"


def test_code_developer_cannot_modify_docs():
    """Verify code_developer cannot write to docs/"""
    guard = DocumentOwnershipGuard()

    with pytest.raises(OwnershipViolation):
        guard.check_write("code_developer", "docs/roadmap/ROADMAP.md")  # Strategic section


def test_project_manager_cannot_modify_code():
    """Verify project_manager cannot write to coffee_maker/"""
    guard = DocumentOwnershipGuard()

    with pytest.raises(OwnershipViolation):
        guard.check_write("project_manager", "coffee_maker/cli/roadmap_cli.py")


def test_code_developer_cannot_modify_dependencies():
    """Verify code_developer cannot write to pyproject.toml"""
    guard = DocumentOwnershipGuard()

    with pytest.raises(OwnershipViolation):
        guard.check_write("code_developer", "pyproject.toml")


def test_architect_can_modify_dependencies():
    """Verify architect CAN write to pyproject.toml"""
    guard = DocumentOwnershipGuard()

    # Should not raise
    guard.check_write("architect", "pyproject.toml")


def test_shared_write_roadmap_status():
    """Verify code_developer can update status in ROADMAP.md"""
    guard = DocumentOwnershipGuard()

    # Should not raise when updating status field
    guard.check_write("code_developer", "docs/roadmap/ROADMAP.md", field="status")
```

**Run Tests**:
```bash
pytest tests/unit/test_document_ownership.py -v
```

---

### 4. Documentation Review

**project_manager responsibility**:
- Review this document quarterly
- Check for new overlaps when agents are added
- Update ownership rules as project evolves
- Warn user if potential overlaps detected
- Run validation tests before major releases

**Review Checklist**:
- [ ] Run `test_no_overlapping_ownership_critical` test
- [ ] Review all agent definitions in `.claude/agents/`
- [ ] Check for new directories in `docs/`
- [ ] Verify ownership matrix is up to date
- [ ] Update enforcement guide if needed
- [ ] Notify user of any changes

---

## Common Questions

### Q: Can I temporarily violate ownership for a quick fix?

**A: NO.** Ownership rules are non-negotiable. Even "quick fixes" must follow ownership. If you need a fix:
1. Identify correct owner
2. Delegate to that agent
3. Let them make the change

### Q: What if two agents need to modify the same file?

**A: Use field-level shared write (like ROADMAP.md).** Define clear boundaries:
- Agent A: Owns fields X, Y
- Agent B: Owns fields Z

Or create separate files:
- Agent A: `docs/foo_a.md`
- Agent B: `docs/foo_b.md`

### Q: Can I add a new agent without reviewing ownership?

**A: NO.** Every new agent MUST:
1. Have explicit ownership defined
2. Not create overlaps
3. Pass validation tests
4. Be documented in ownership matrix

### Q: What if I find an overlap?

**A: Report immediately and fix.** Overlaps are critical bugs:
1. Create notification/warning for user
2. Document the overlap in this file
3. Propose fix (reassign ownership)
4. Update all documentation
5. Run validation tests

---

## Version History

**v1.0 (2025-10-15)**:
- Initial version
- Defined NO OVERLAP rule
- Created ownership matrix
- Documented enforcement mechanisms
- Added validation tests
- Provided examples and common questions

---

## Related Documentation

- `.claude/CLAUDE.md` - Agent Tool Ownership & Boundaries
- `docs/DOCUMENT_OWNERSHIP_MATRIX.md` - Complete ownership matrix
- `docs/ARCHITECTURE_WORKFLOW.md` - Workflow including dependency management
- `docs/roadmap/TEAM_COLLABORATION.md` - Team collaboration guide

---

**Maintained By**: project_manager
**Review Frequency**: Quarterly or when adding new agents
**Next Review**: 2026-01-15
**Status**: Active and Enforced
