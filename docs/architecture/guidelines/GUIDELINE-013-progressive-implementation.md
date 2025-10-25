# GUIDELINE-013: Progressive Implementation Workflow

**Category**: Best Practice

**Applies To**: Code_developer agent, Feature implementation

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: [SPEC-025: Hierarchical Modular Spec Architecture](../specs/SPEC-025-hierarchical-modular-spec-architecture/README.md)

---

## Overview

This guideline describes how code_developer implements features using hierarchical specifications. It covers phase detection, progressive implementation, testing between phases, and ROADMAP updates.

---

## When to Use

Use this workflow when:
- Implementing a feature with hierarchical spec (multiple phases)
- Reading ROADMAP.md to determine current task
- code_developer is working on a phase of a larger feature
- Need to track phase completion and progress

**NOT for**: Monolithic specs (single-document, all implemented at once)

---

## When NOT to Use

Do NOT use this workflow when:
- Feature uses monolithic spec (implement entire feature at once)
- Feature is <4 hours (typically single phase)
- Bug fix or small enhancement
- Quick task that doesn't fit phase-based approach

---

## The Pattern

### Explanation

Progressive implementation breaks large features into phases and implements them sequentially:

1. **Read ROADMAP**: Find current priority and phase
2. **Detect Phase**: Which phase are we on? (Phase 1, 2, 3, etc.)
3. **Read Phase Spec**: Load ONLY the current phase's details (~50-100 lines)
4. **Implement Phase**: Write code, add tests, get tests passing
5. **Update ROADMAP**: Mark phase as complete
6. **Repeat**: Move to next phase

**Benefits**:
- **Context Efficiency**: Load only current phase (~150 lines vs 350+ for full spec)
- **Focus**: Clear deliverables for current phase
- **Testing**: Verify phase works independently
- **Git History**: Each phase gets its own commits
- **Rollback**: Can rollback single phase if needed

### Principles

1. **One Phase at a Time**: Never jump ahead to future phases
2. **Phase Independence**: Each phase is testable and can be reviewed independently
3. **Progressive Testing**: Tests written and passing before moving to next phase
4. **Clear Commits**: Each phase gets committed with clear message
5. **ROADMAP Truth**: ROADMAP.md is source of truth for current phase

---

## How to Implement

### Step 1: Read ROADMAP and Detect Current Priority

```bash
# Read ROADMAP to find current priority
poetry run project-manager /roadmap

# Look for "PRIORITY X: {Feature Name} - Phase Y"
# Example: "PRIORITY 25: Hierarchical Spec Architecture - Phase 3"
```

### Step 2: Read Architecture Overview

Read only the README.md to understand overall architecture:

```bash
# Example: SPEC-25 Phase 3
cat docs/architecture/specs/SPEC-025-hierarchical-modular-spec-architecture/README.md

# Output shows:
# - Overall feature goal
# - Architecture overview
# - Phase breakdown
# - Prerequisites
```

Expected output: ~100-150 lines with phase summary

### Step 3: Detect Current Phase

Use daemon's phase detection or check ROADMAP directly:

```python
# Option 1: Check ROADMAP for phase marker
import re

with open("docs/roadmap/ROADMAP.md") as f:
    content = f.read()
    match = re.search(r"PRIORITY \d+.*Phase (\d+)", content)
    if match:
        current_phase = int(match.group(1))
        print(f"Current phase: {current_phase}")

# Option 2: Check git branch
import subprocess

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], text=True
).strip()
# Example: "roadmap" means phase-based on ROADMAP
```

### Step 4: Read Current Phase Spec

Read ONLY the current phase file:

```bash
# Example: Phase 3 of SPEC-025
cat docs/architecture/specs/SPEC-025-hierarchical-modular-spec-architecture/phase3-guidelines-library.md

# Output: ~50-100 lines with:
# - Goal of this phase
# - Detailed implementation steps
# - Code examples
# - Acceptance criteria
# - Testing approach
```

**Key point**: Don't read other phases yet. Focus on current phase only.

### Step 5: Implement the Phase

Implement according to phase spec:

```python
# Example: Phase 3 (Guidelines Library) implementation

# Step 1: Create guidelines directory
os.makedirs("docs/architecture/guidelines", exist_ok=True)

# Step 2: Create guideline files
for guideline_num in range(12, 22):
    create_guideline(guideline_num)

# Step 3: Run tests
subprocess.run(["pytest", "tests/", "-v"])

# Step 4: Verify acceptance criteria
verify_acceptance_criteria()

# Step 5: Commit with phase message
subprocess.run([
    "git", "commit", "-m",
    "feat(PRIORITY 25): Phase 3 - Create guidelines library\n\nImplement 10 initial guidelines (012-021)\nUpdate specs to reference guidelines\nUpdate ROADMAP to mark phase complete"
])
```

### Step 6: Verify Phase Complete

Check that all acceptance criteria are met:

```bash
# Example: Phase 3 acceptance criteria
- [ ] 10 guidelines created (GUIDELINE-012 through GUIDELINE-021)
- [ ] Guidelines follow template format
- [ ] At least 2 specs reference guidelines
- [ ] architect.md updated with guideline workflow
- [ ] Tests passing (pytest)
- [ ] ROADMAP updated to mark phase complete
```

### Step 7: Update ROADMAP

Mark phase as complete in ROADMAP:

```markdown
### PRIORITY 25: Hierarchical Spec Architecture

**Status**: 🔄 In Progress - Phase 3 Complete ✅

**Phase 1**: Database Schema ✅ Complete
**Phase 2**: API Endpoints ✅ Complete
**Phase 3**: Guidelines Library ✅ Complete (2025-10-21)
**Phase 4**: Spec Migration 📝 Planned

Next: Proceed to Phase 4
```

### Step 8: Commit and Push

Commit phase completion:

```bash
git add -A
git commit -m "feat(PRIORITY 25): Complete Phase 3 - Guidelines Library

- Create GUIDELINE-012 through GUIDELINE-021
- Extract common patterns from specs
- Update 2 specs to reference guidelines
- Update architect.md with guideline workflow
- All acceptance criteria met"

git push origin roadmap
```

---

## Anti-Patterns to Avoid

❌ **Don't read all phases at once**
- Wastes context on information not yet needed
- Creates cognitive overload
- **Better**: Read current phase only, read others when needed

❌ **Don't implement multiple phases in one commit**
- Makes review and rollback harder
- Violates incremental implementation principle
- **Better**: One phase per commit with clear message

❌ **Don't skip tests for current phase**
- Can't verify phase works independently
- Risk of introducing bugs that surface later
- **Better**: Write and run tests for each phase before moving on

❌ **Don't forget to update ROADMAP**
- Next run of code_developer won't know phase is complete
- Can cause duplicate work
- **Better**: Update ROADMAP immediately after phase completion

❌ **Don't jump to next phase without tests passing**
- Can't verify phase is truly complete
- Breaks dependencies for next phase
- **Better**: Ensure 100% test pass rate before committing

---

## Testing Approach

### Test Phase Implementation

```bash
# Run tests for current phase
pytest tests/test_phase_3.py -v

# Check acceptance criteria
- All tests passing
- Coverage >80%
- No new warnings
```

### Test Phase Independence

```bash
# Verify phase works standalone
# (previous phases already complete)
cd coffee_maker
python -c "from module import feature; feature.test_phase_3()"
```

### Test Spec References

```bash
# Verify phase spec is complete
- Goal clearly stated
- All steps actionable
- Code examples provided
- Acceptance criteria specific
- Testing approach documented
```

---

## Related Guidelines

- [GUIDELINE-012: Hierarchical Spec Creation](./GUIDELINE-012-hierarchical-spec-creation.md)
- [GUIDELINE-014: FastAPI Endpoints](./GUIDELINE-014-fastapi-endpoints.md)
- [GUIDELINE-016: Testing Strategy](./GUIDELINE-016-testing-strategy.md)

---

## Examples in Codebase

- Phase-based implementation: All PRIORITY 25 phases (SPEC-025)
- ROADMAP tracking: `docs/roadmap/ROADMAP.md` (tracks phases)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial guideline for progressive implementation workflow |
