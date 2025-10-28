# Spec Migration Guide: Monolithic → Hierarchical

**Purpose**: Guide for migrating monolithic specifications to hierarchical format for better context efficiency and modular implementation.

**Context Reduction**: Hierarchical specs achieve **71% context reduction** (150 lines vs 350 lines per code_developer iteration).

---

## When to Migrate

### Migrate When:
- ✅ **Spec >300 lines** (high context waste potential)
- ✅ **Clear implementation phases** (easy to modularize)
- ✅ **Actively used** (high value from optimization)
- ✅ **CFR-016 compliance needed** (incremental implementation steps)
- ✅ **References patterns** documented in guidelines (can link instead of duplicate)

### Don't Migrate When:
- ❌ **Spec <200 lines** (already concise, low benefit)
- ❌ **Deprecated spec** (low value, not worth effort)
- ❌ **No clear phases** (complex migration, unclear structure)
- ❌ **Single-file implementation** (no phasing needed)

---

## Migration Options

### Option 1: Automated Script (Recommended)

**Best for**: Specs with standard structure and clear phase markers

```bash
# Basic usage
python scripts/migrate_spec_to_hierarchical.py docs/architecture/specs/SPEC-XXX-name.md

# The script will:
# 1. Parse the monolithic spec
# 2. Extract phases (### Phase N: Title (hours))
# 3. Create hierarchical directory structure
# 4. Generate README.md with overview
# 5. Create phase files (phase1-name.md, phase2-name.md, ...)
# 6. Archive original (.ARCHIVE suffix)
```

**What the Script Does**:
1. Parses spec metadata (number, title)
2. Extracts overview (content before Implementation/Migration Plan)
3. Identifies phase boundaries (`### Phase N: Title (hours)`)
4. Creates directory: `SPEC-XXX-kebab-case-title/`
5. Generates `README.md` with overview + phase links
6. Creates phase files with extracted content
7. Archives original as `.md.ARCHIVE`

**Script Output**:
```
docs/architecture/specs/SPEC-XXX-feature-name/
├── README.md (overview, 100-350 lines)
├── phase1-component-design.md (50-150 lines)
├── phase2-implementation.md (50-150 lines)
├── phase3-testing.md (30-100 lines)
└── references.md (optional, if many references)
```

---

### Option 2: Manual Migration

**Best for**: Specs with non-standard structure or when learning the process

**Step 1**: Create directory structure
```bash
# Example for SPEC-108
mkdir docs/architecture/specs/SPEC-108-feature-name/
cd docs/architecture/specs/SPEC-108-feature-name/
```

**Step 2**: Create README.md (Overview)
```markdown
# SPEC-108: Feature Name

## Overview

[Copy overview content from original spec]
- Problem Statement
- High-Level Architecture
- Tech Stack
- Dependencies

---

## Implementation Phases

### Phase 1: Component Design (3 hours)
**Document**: [phase1-component-design.md](./phase1-component-design.md)

### Phase 2: Implementation (5 hours)
**Document**: [phase2-implementation.md](./phase2-implementation.md)

...
```

**Step 3**: Create phase files
```bash
# Create each phase file
touch phase1-component-design.md
touch phase2-implementation.md
...
```

**Step 4**: Extract phase content

For each phase file:
```markdown
# SPEC-108 - Phase 1: Component Design

**Estimated Time**: 3 hours
**Status**: Planned

---

[Copy detailed phase content from original spec]

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 2: Implementation](phase2-implementation.md)**
```

**Step 5**: Archive original
```bash
mv docs/architecture/specs/SPEC-108-feature-name.md \
   docs/architecture/specs/SPEC-108-feature-name.md.ARCHIVE
```

---

## Validation Checklist

After migration, verify:

- [ ] **Directory created** with `SPEC-XXX-*/` pattern
- [ ] **README.md exists** with overview and phase links
- [ ] **Phase files exist** (phase1-*.md, phase2-*.md, ...)
- [ ] **Content preserved** (total line count ≈ original + headers)
- [ ] **Phase links work** (README → phase files)
- [ ] **Original archived** (.ARCHIVE suffix)
- [ ] **No duplicate content** (phases don't repeat overview)
- [ ] **Headers consistent** (all phases follow same format)

**Quick Validation**:
```bash
# Check directory exists
ls -d docs/architecture/specs/SPEC-XXX-*/

# Check files
ls docs/architecture/specs/SPEC-XXX-*/*.md
# Expected: README.md + N phase files

# Compare line counts (should be roughly equivalent)
wc -l docs/architecture/specs/SPEC-XXX-*/*.md
wc -l docs/architecture/specs/SPEC-XXX-*.ARCHIVE
# Total should be within 10-20% (accounting for headers)
```

---

## Testing Migration

### Test 1: Manual Read
```bash
# Verify README is readable and provides good overview
cat docs/architecture/specs/SPEC-XXX-*/README.md

# Verify phase files are focused and actionable
cat docs/architecture/specs/SPEC-XXX-*/phase1-*.md
```

### Test 2: Code Developer Loading (Future)

Once hierarchical spec loading is integrated with `code_developer`:

```bash
# Test hierarchical spec loading
python -c "
from coffee_maker.utils.spec_handler import SpecHandler
handler = SpecHandler()
result = handler.read_hierarchical('PRIORITY-XXX')
print(f'Success: {result[\"success\"]}, Type: {result[\"spec_type\"]}')
"
# Expected: Success: True, Type: hierarchical
```

### Test 3: Backward Compatibility

Unmigrated specs should still work:

```bash
# Test monolithic spec (unmigrated)
python -c "
from coffee_maker.utils.spec_handler import SpecHandler
handler = SpecHandler()
result = handler.read_hierarchical('PRIORITY-YYY')  # Unmigrated spec
print(f'Success: {result[\"success\"]}, Type: {result.get(\"spec_type\", \"monolithic\")}')
"
# Expected: Success: True, Type: monolithic (fallback)
```

---

## Troubleshooting

### Issue: Phase boundaries unclear

**Symptom**: Script can't find phases or manual extraction is difficult

**Solution**:
1. Look for `### Phase N:` markers in original spec
2. If phases aren't explicitly marked, identify logical breakpoints:
   - Design → Implementation → Testing
   - Component A → Component B → Integration
3. Manually create phase boundaries
4. Consider if spec structure needs improvement before migration

### Issue: Content loss during migration

**Symptom**: Migrated spec has significantly fewer lines than original

**Solution**:
1. Compare total line counts (hierarchical vs ARCHIVE)
2. Check if overview extraction cut off important content
3. Review ARCHIVE file for missing sections
4. Manually add missing content to README or appropriate phase file

### Issue: Duplicate content in phase files

**Symptom**: Same content appears in multiple phase files

**Solution**:
1. Review phase extraction logic (script may be over-inclusive)
2. Manually edit phase files to remove duplication
3. Move shared content to README overview section

### Issue: Script fails with "No phases found"

**Symptom**: `⚠️  Warning: No phases found in spec. Skipping migration.`

**Solution**:
1. Verify spec has `### Phase N: Title (hours)` markers
2. Check phase markers match expected format (number, title, hours in parentheses)
3. If spec structure is different, use manual migration instead
4. Update script regex pattern if needed (for your team's specific format)

### Issue: Links broken after migration

**Symptom**: ROADMAP or other docs reference old monolithic spec path

**Solution**:
1. Search for references: `grep -r "SPEC-XXX-name.md" docs/`
2. Update to directory: `SPEC-XXX-name/`
3. Update ROADMAP spec links (see below)

---

## Updating References

### Update ROADMAP.md

After migrating a spec, update ROADMAP references:

**Before**:
```markdown
**Technical Specification**: [SPEC-108-parallel-agent-execution.md](../architecture/specs/SPEC-108-parallel-agent-execution.md)
```

**After**:
```markdown
**Technical Specification**: [SPEC-108-parallel-agent-execution/](../architecture/specs/SPEC-108-parallel-agent-execution/)
**Format**: Hierarchical (71% context reduction ✅)
```

### Update Cross-References

If other specs reference the migrated spec:

```bash
# Find all references
grep -r "SPEC-XXX-name.md" docs/architecture/

# Update each reference
# Old: [SPEC-XXX](./SPEC-XXX-name.md)
# New: [SPEC-XXX](./SPEC-XXX-name/)
```

---

## Migration Examples

### Example 1: REFACTOR-001 (Split Monolithic CLI)

**Original**: 576 lines, 3 phases
**Migrated**:
- `README.md` (353 lines - overview)
- `phase1-extract-commands.md` (34 lines)
- `phase2-refactor-chat-interface.md` (31 lines)
- `phase3-update-tests-documentation.md` (24 lines)

**Context Reduction**:
- Code developer reads README (353 lines) + one phase (~30 lines) = **383 lines** vs 576 lines monolithic
- **34% reduction** for overview + phase 1

### Example 2: SPEC-025 (Hierarchical Spec Architecture)

**Original**: N/A (created hierarchical from start)
**Structure**:
- `README.md` (overview)
- `phase1-shared-skill.md` (Phase 1 details)
- `phase2-daemon-enhancement.md` (Phase 2 details)
- `phase3-guidelines-library.md` (Phase 3 details)
- `phase4-spec-migration.md` (Phase 4 details)
- `phase5-testing-docs.md` (Phase 5 details)

**Benefits**: Each phase self-contained, no need to read entire spec for implementation.

---

## Best Practices

### For README.md:
1. **Keep overview concise** (100-350 lines)
2. **Include problem statement** (why this spec exists)
3. **Add phase summary** with links (table of contents)
4. **List prerequisites** and dependencies
5. **Avoid implementation details** (those go in phase files)

### For Phase Files:
1. **One phase = one file** (clear boundaries)
2. **Include time estimate** (helps planning)
3. **List acceptance criteria** (definition of done)
4. **Link to next phase** (guide progression)
5. **Keep focused** (50-150 lines ideal)

### For Guidelines References:
1. **Link, don't duplicate** (reference [GUIDELINE-XXX](path))
2. **Explain why guideline applies** (context for link)
3. **List all relevant guidelines** in references section
4. **Keep guidelines atomic** (one pattern/rule per guideline)

---

## Related Documents

- [SPEC-025: Hierarchical, Modular Technical Specification Architecture](./specs/SPEC-025-hierarchical-modular-spec-architecture/)
- [GUIDELINE-012: Hierarchical Spec Creation](./guidelines/GUIDELINE-012-hierarchical-spec-creation.md)
- [Technical Specification Handling Skill](../../.claude/skills/shared/technical-specification-handling/SKILL.md)
- [CFR-007: Agent Context Budget](../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md) (30% Maximum)
- [CFR-016: Technical Specs - Incremental Implementation](../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)

---

## FAQ

### Q: Should I migrate all existing specs?

**A**: No. Prioritize:
1. Active specs (currently being implemented)
2. Large specs (>300 lines)
3. Specs with clear phases

Leave small (<200 lines) or deprecated specs as-is.

### Q: Can hierarchical and monolithic specs coexist?

**A**: Yes! The system supports both formats (backward compatible). Migrate specs incrementally as needed.

### Q: What if I make a mistake during migration?

**A**: The original spec is preserved as `.ARCHIVE`. You can:
1. Delete the hierarchical directory
2. Restore from `.ARCHIVE` (remove suffix)
3. Re-run migration with corrections

### Q: How do I create a NEW spec in hierarchical format?

**A**: Use the template in [GUIDELINE-012](./guidelines/GUIDELINE-012-hierarchical-spec-creation.md) or refer to SPEC-025 as an example. Start hierarchical from the beginning instead of migrating.

### Q: Does hierarchical format work with all specs?

**A**: Best for specs with:
- Clear implementation phases (design → implement → test)
- Multiple distinct components
- Large scope (5+ hours)

Not ideal for:
- Quick fixes (<2 hours total)
- Single-file changes
- Exploratory spikes (structure unclear)

---

**Last Updated**: 2025-10-25
**Version**: 1.0.0
**Status**: Ready for use ✅
