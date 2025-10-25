# SPEC-025 - Phase 4: Spec Migration

**Estimated Time**: 3 hours
**Dependencies**: Phase 1 complete, Phase 3 in progress (guidelines library)
**Status**: Planned
**Files Modified**: Existing specs converted to hierarchical format

---

## Goal

Migrate existing monolithic specifications to hierarchical format, demonstrating migration process and validating backward compatibility. Focus on recent, actively-used specs first.

**What This Phase Accomplishes**:
- Migrate 3+ recent specs to hierarchical format
- Document migration process for future use
- Validate both formats coexist (backward compatibility)
- Create migration tooling for efficiency

---

## Prerequisites

- [x] Phase 1 complete (hierarchical spec support available)
- [ ] Phase 3 in progress (guidelines available to reference)
- [ ] Identified candidate specs for migration

---

## Detailed Steps

### Step 1: Identify Migration Candidates

**What**: Select 3-5 specs to migrate based on criteria

**Why**: Prioritize high-value specs that benefit most from hierarchical format

**How**:
1. Review recent specs (created in last 3 months)
2. Look for specs >300 lines (high context waste)
3. Look for specs with clear phases (easy to migrate)
4. Prioritize actively-used specs (ongoing implementation)

**Candidate Selection Criteria**:
- ✅ Spec >300 lines (benefits from context reduction)
- ✅ Has clear implementation phases
- ✅ Currently in use (PRIORITY in Planned or In Progress status)
- ✅ Uses patterns documented in guidelines (can reference)
- ❌ Avoid deprecated specs (low value)
- ❌ Avoid specs <200 lines (already concise)

**Expected Candidates** (examples):
1. SPEC-108-parallel-agent-execution-with-git-worktree.md (~400 lines)
   - Clear phases: Design, Orchestrator, Daemon, Testing
   - Actively used (PRIORITY 23)

2. SPEC-070-dependency-pre-approval-matrix.md (~350 lines)
   - Clear phases: Matrix, CLI, Integration, Testing
   - Actively used (PRIORITY 24)

3. SPEC-050-poc-management-and-workflow.md (~300 lines)
   - Clear phases: POC Structure, Workflow, Integration
   - Referenced frequently

**Files to Create/Modify**:
- None yet (selection phase)

---

### Step 2: Create Migration Script (Optional but Recommended)

**What**: Create Python script to automate monolithic → hierarchical conversion

**Why**: Manual migration error-prone; script ensures consistency

**How**:
1. Parse monolithic spec markdown
2. Extract sections (Overview, Implementation Plan, etc.)
3. Identify phase boundaries (## Phase 1:, ## Phase 2:, etc.)
4. Generate directory structure
5. Create README.md with overview
6. Create phase documents from extracted content
7. Preserve all content (no information loss)

**Script Structure**:
```python
# scripts/migrate_spec_to_hierarchical.py

import re
from pathlib import Path
from typing import List, Dict

def parse_monolithic_spec(spec_path: Path) -> Dict:
    """Parse monolithic spec into sections."""
    content = spec_path.read_text()

    # Extract metadata
    us_match = re.search(r'SPEC-(\d+)', spec_path.name)
    us_number = us_match.group(1) if us_match else "000"

    title_match = re.search(r'^# SPEC-\d+: (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"

    # Extract phases from Implementation Plan
    phases = []
    phase_pattern = r'### Phase (\d+): (.+?) \((.+?)\)'
    for match in re.finditer(phase_pattern, content):
        phase_num = int(match.group(1))
        phase_name = match.group(2).strip()
        phase_hours = match.group(3).strip()

        # Extract phase content (between this phase and next)
        phase_start = match.start()
        next_phase = re.search(r'### Phase \d+:', content[phase_start + 1:])
        phase_end = phase_start + next_phase.start() if next_phase else len(content)

        phase_content = content[phase_start:phase_end].strip()

        phases.append({
            "number": phase_num,
            "name": phase_name,
            "hours": phase_hours,
            "content": phase_content
        })

    return {
        "us_number": us_number,
        "title": title,
        "overview": extract_overview(content),
        "phases": phases,
        "references": extract_references(content)
    }

def create_hierarchical_spec(spec_data: Dict, output_dir: Path):
    """Create hierarchical spec from parsed data."""
    # Create directory
    slug = to_kebab_case(spec_data["title"])
    spec_dir = output_dir / f"SPEC-{spec_data['us_number']}-{slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Create README.md
    readme = generate_readme(spec_data)
    (spec_dir / "README.md").write_text(readme)

    # Create phase files
    for phase in spec_data["phases"]:
        phase_file = spec_dir / f"phase{phase['number']}-{to_kebab_case(phase['name'])}.md"
        phase_content = generate_phase_doc(phase, spec_data)
        phase_file.write_text(phase_content)

    print(f"✅ Created hierarchical spec: {spec_dir}")
    print(f"   Files: README.md + {len(spec_data['phases'])} phase files")

def migrate_spec(spec_path: Path, output_dir: Path = None):
    """Main migration function."""
    if output_dir is None:
        output_dir = spec_path.parent

    spec_data = parse_monolithic_spec(spec_path)
    create_hierarchical_spec(spec_data, output_dir)

    # Archive original
    archive_path = spec_path.with_suffix('.md.ARCHIVE')
    spec_path.rename(archive_path)
    print(f"📦 Archived original: {archive_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python migrate_spec_to_hierarchical.py <spec_file>")
        sys.exit(1)

    spec_file = Path(sys.argv[1])
    migrate_spec(spec_file)
```

**Files to Create/Modify**:
- `scripts/migrate_spec_to_hierarchical.py` (new script)

---

### Step 3: Migrate First Spec (Manual or Script)

**What**: Convert SPEC-108 (or selected candidate) to hierarchical format

**Why**: Prove migration process, validate approach

**How**:
1. Read monolithic spec
2. Identify phase boundaries
3. Create directory structure
4. Move overview content to README.md
5. Move each phase to separate file
6. Add cross-references between phases
7. Archive original monolithic spec

**Manual Migration Process**:
```bash
# 1. Create directory
mkdir docs/architecture/specs/SPEC-108-parallel-agent-execution/

# 2. Create README.md (overview)
# - Copy: Problem Statement, High-Level Architecture, Tech Stack
# - Add: Phase summary (brief, with links to phase files)
# - Remove: Detailed phase content (moved to phase files)

# 3. Create phase files
# - phase1-orchestrator-design.md (from "Phase 1" section)
# - phase2-worktree-manager.md (from "Phase 2" section)
# - phase3-daemon-integration.md (from "Phase 3" section)
# - phase4-testing-validation.md (from "Phase 4" section)

# 4. Archive original
mv docs/architecture/specs/SPEC-108-parallel-agent-execution.md \
   docs/architecture/specs/SPEC-108-parallel-agent-execution.md.ARCHIVE
```

**OR using script**:
```bash
python scripts/migrate_spec_to_hierarchical.py \
    docs/architecture/specs/SPEC-108-parallel-agent-execution.md
```

**Validation**:
```bash
# Check directory created
ls -la docs/architecture/specs/SPEC-108-*/

# Check files
# Expected: README.md + 4 phase files

# Check content preserved (line count similar)
wc -l docs/architecture/specs/SPEC-108-*/*.md
wc -l docs/architecture/specs/SPEC-108-*.ARCHIVE
# Should be approximately equal (content preserved)
```

**Files to Create/Modify**:
- `docs/architecture/specs/SPEC-108-parallel-agent-execution/` (new directory)
- `docs/architecture/specs/SPEC-108-parallel-agent-execution.md.ARCHIVE` (archived)

---

### Step 4: Migrate Additional Specs (2-3 more)

**What**: Repeat migration for 2-3 more candidate specs

**Why**: Validate process works for different spec structures

**How**:
1. Use script (if created) or manual process
2. Adapt to each spec's unique structure
3. Ensure phase boundaries make sense
4. Add guideline references where applicable
5. Test that code_developer can read migrated specs

**Specs to Migrate**:
1. ✅ SPEC-108-parallel-agent-execution.md (completed in Step 3)
2. SPEC-070-dependency-pre-approval-matrix.md
3. SPEC-050-poc-management-and-workflow.md
4. (Optional) One more if time allows

**Files to Create/Modify**:
- `docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix/` (new)
- `docs/architecture/specs/SPEC-050-poc-management-and-workflow/` (new)

---

### Step 5: Document Migration Guide

**What**: Create migration guide for future spec conversions

**Why**: Enable others to migrate specs independently

**How**:
1. Create `docs/architecture/SPEC_MIGRATION_GUIDE.md`
2. Document decision criteria (when to migrate)
3. Document manual process (step-by-step)
4. Document script usage (if created)
5. Include troubleshooting tips
6. Add examples (before/after)

**Guide Structure**:
```markdown
# Spec Migration Guide: Monolithic → Hierarchical

## When to Migrate

Migrate a monolithic spec when:
- Spec >300 lines (high context waste)
- Spec has clear phases (easy to split)
- Spec actively used (high value)
- CFR-016 compliance needed

Don't migrate when:
- Spec <200 lines (already concise)
- Spec deprecated (low value)
- Spec has no clear phases (complex migration)

## Migration Process

### Option 1: Manual Migration (Recommended for First Time)

Step 1: Create directory structure
...

### Option 2: Script-Based Migration (Faster)

```bash
python scripts/migrate_spec_to_hierarchical.py <spec_file>
```

## Validation Checklist

- [ ] Directory created with README + phase files
- [ ] Content preserved (line count similar)
- [ ] Phase links work (README → phase files)
- [ ] code_developer can read spec successfully
- [ ] Original archived (.ARCHIVE suffix)

## Troubleshooting

**Issue**: Phase boundaries unclear
**Solution**: Manually identify logical breakpoints

**Issue**: Content loss during migration
**Solution**: Compare line counts, review ARCHIVE file

...
```

**Files to Create/Modify**:
- `docs/architecture/SPEC_MIGRATION_GUIDE.md` (new file)

---

### Step 6: Update ROADMAP References

**What**: Update ROADMAP.md to reference new hierarchical spec locations

**Why**: Ensure code_developer finds migrated specs

**How**:
1. Find ROADMAP entries referencing migrated specs
2. Update file paths (if needed)
3. Add note about hierarchical format
4. Verify links work

**Example Update**:
```markdown
# Before
**Technical Specification**: [SPEC-108-parallel-agent-execution.md](../architecture/specs/SPEC-108-parallel-agent-execution.md)

# After
**Technical Specification**: [SPEC-108-parallel-agent-execution/](../architecture/specs/SPEC-108-parallel-agent-execution/)
**Format**: Hierarchical (71% context reduction ✅)
```

**Files to Create/Modify**:
- `docs/roadmap/ROADMAP.md` (update 3+ spec references)

---

## Acceptance Criteria

**This phase is complete when**:

- [ ] 3+ monolithic specs migrated to hierarchical format
- [ ] Migration script created (optional but recommended)
- [ ] SPEC_MIGRATION_GUIDE.md created
- [ ] ROADMAP.md updated with new spec locations
- [ ] All migrated specs validated (code_developer can read)
- [ ] Original specs archived (.ARCHIVE suffix)
- [ ] No information loss (content preserved)
- [ ] Both formats coexist (backward compatibility)

**Validation Tests**:
```bash
# Check hierarchical specs exist
ls -d docs/architecture/specs/SPEC-*/
# Expected: 3+ directories

# Check archives exist
ls docs/architecture/specs/*.ARCHIVE
# Expected: 3+ archived files

# Test code_developer reading
poetry run code-developer --priority=108 --dry-run
# Expected: Loads hierarchical SPEC-108 successfully
```

---

## Testing This Phase

### Manual Testing

1. **Test migrated spec reading**:
   ```bash
   # Load hierarchical spec
   python -c "from coffee_maker.utils.spec_handler import SpecHandler; \
     handler = SpecHandler(); \
     result = handler.read_hierarchical('PRIORITY-108'); \
     print(f'Success: {result[\"success\"]}, Type: {result[\"spec_type\"]}')"
   # Expected: Success: True, Type: hierarchical
   ```

2. **Test backward compatibility**:
   ```bash
   # Load monolithic spec (unmigrated)
   python -c "from coffee_maker.utils.spec_handler import SpecHandler; \
     handler = SpecHandler(); \
     result = handler.read_hierarchical('PRIORITY-20'); \
     print(f'Success: {result[\"success\"]}, Type: {result.get(\"spec_type\", \"monolithic\")}')"
   # Expected: Success: True, Type: monolithic (fallback)
   ```

3. **Validate content preservation**:
   ```bash
   # Compare line counts
   wc -l docs/architecture/specs/SPEC-108-*/*.md
   wc -l docs/architecture/specs/SPEC-108-*.ARCHIVE

   # Should be approximately equal (±10%)
   ```

---

## References for This Phase

**Tools**:
- `scripts/migrate_spec_to_hierarchical.py` (migration script)
- `docs/architecture/SPEC_MIGRATION_GUIDE.md` (migration guide)

**Related Documents**:
- [GUIDELINE-012: Hierarchical Spec Creation](../../guidelines/GUIDELINE-012-hierarchical-spec-creation.md)
- [technical-specification-handling skill](/.claude/skills/shared/technical-specification-handling/SKILL.md)

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 5: Testing and Documentation](phase5-testing-docs.md)**

**Deliverable Handoff**:
- 3+ specs successfully migrated
- Migration guide available for future conversions
- Both formats coexist (backward compatibility proven)
- Ready for comprehensive testing and documentation

---

**Note**: Migration is non-destructive (originals archived). If issues arise, can restore from .ARCHIVE files.
