# CLEANUP-001: Tactical Breakdown

**Status**: Ready to execute
**Total Files**: 91 files with assistant (using code analysis skills) references
**Estimated Time**: 3-4 hours

---

## Category Breakdown

| Category | Files | Priority | Time | Approach |
|----------|-------|----------|------|----------|
| Python Code | 9 files | HIGH | 1h | Manual update |
| Agent Docs | 6 files | HIGH | 1h | Manual update |
| Test Files | 8 files | MEDIUM | 1h | Manual/semi-automated |
| General Docs | 59 files | LOW | 1h | Semi-automated |
| Historical | 9 files | LOWEST | 30m | Archive/mark obsolete |

---

## Phase 1: Critical Python Code (9 files) - 1 hour

**Priority**: HIGH - These affect functionality

### Files to Update:

1. **coffee_maker/cli/architect_cli.py** (7 refs)
   - Remove `daily-integration` command (reads assistant (using code analysis skills) reports)
   - Update help text
   - Remove CFR-011 assistant (using code analysis skills) checks

2. **coffee_maker/autonomous/daemon_spec_manager.py** (7 refs)
   - Remove CFR-011 assistant (using code analysis skills) enforcement
   - Update spec creation checks
   - Remove report reading requirements

3. **coffee_maker/autonomous/architect_daily_routine.py** (8 refs)
   - Remove `ArchitectDailyRoutine` class entirely (reads assistant (using code analysis skills) reports)
   - Update imports where used

4. **coffee_maker/autonomous/orchestrator.py** (4 refs)
   - Update comments about code quality improvements
   - Remove assistant (using code analysis skills) scheduling

5. **coffee_maker/autonomous/agents/base_agent.py** (2 refs)
   - Update comments about check intervals

6. **coffee_maker/autonomous/agents/architect_agent.py** (1 ref)
   - Update CFR-011 enforcement comment

7. **coffee_maker/autonomous/ace/generator.py** (4 refs)
   - Remove assistant (using code analysis skills) from expected search agents
   - Update search tracking logic

8. **coffee_maker/autonomous/implementation_task_creator.py** (1 ref)
   - Update comment about code search skills

9. **coffee_maker/orchestrator/architect_coordinator.py** (2 refs)
   - Update CFR-011 compliance comments

### Action Plan:
```bash
# For each file:
1. Read file and identify references
2. Determine if functional code or just comments
3. If functional: refactor to remove dependency
4. If comments: update to reference assistant + skills
5. Test changes
```

---

## Phase 2: Agent Documentation (6 files) - 1 hour

**Priority**: HIGH - User-facing documentation

### Files to Update:

1. **.claude/agents/architect.md** (7 refs)
   - Update CFR-011 requirements (remove assistant (using code analysis skills) reports)
   - Update delegation rules
   - Update workflow examples

2. **.claude/agents/assistant.md** (8 refs)
   - Add section: assistant now handles code analysis via skills
   - Update delegation examples
   - Document code-forensics and security-audit skills

3. **.claude/agents/README.md** (4 refs)
   - Remove assistant (using code analysis skills) from agent list
   - Update agent count (8 → 7 agents)
   - Update skill ownership

4. **.claude/agents/user_listener.md** (3 refs)
   - Update routing examples
   - Remove assistant (using code analysis skills) from delegation patterns

5. **.claude/agents/orchestrator.md** (2 refs)
   - Update agent coordination list
   - Remove assistant (using code analysis skills) scheduling

6. **.claude/agents/project_manager.md** (1 ref)
   - Update delegation examples

### Action Plan:
```bash
# For each file:
1. Find all "assistant (using code analysis skills)" mentions
2. Replace with "assistant (using code-forensics/security-audit skills)"
3. Update agent lists and counts
4. Verify examples still make sense
```

---

## Phase 3: Test Files (8 files) - 1 hour

**Priority**: MEDIUM - Tests need to pass

### Files to Update:

1. **tests/unit/test_agent_registry.py** (1 ref)
   - Fix enum validation test
   - Remove ASSISTANT from expected agent types

2. **tests/unit/test_context_upfront.py** (5 refs)
   - Update context loading tests
   - Remove assistant agent (with code analysis skills) tests
   - Update search expectation tests

3. **tests/unit/test_file_ownership_enforcement.py** (2 refs)
   - Remove docs/assistant (using code analysis skills)/ ownership test

4. **tests/unit/test_phase2_skills.py** (4 refs)
   - Update security-audit skill tests
   - Change agent from assistant (using code analysis skills) to assistant

5. **tests/unit/test_phase3_skills.py** (10 refs)
   - Update code-forensics skill tests
   - Change agent from assistant (using code analysis skills) to assistant

6. **tests/unit/test_architect_daily_routine.py** (1 ref)
   - Remove assistant (using code analysis skills) report tests OR
   - Archive entire test file if ArchitectDailyRoutine removed

7. **tests/unit/test_singleton_enforcement.py** (1 ref)
   - Remove assistant (using code analysis skills) parallel run test

8. **tests/ci_tests/test_cfr_011_integration.py** (5 refs)
   - Remove CFR-011 assistant (using code analysis skills) report requirements
   - Update integration tests

### Action Plan:
```bash
# For each test file:
1. Run test to see current failures
2. Update test expectations
3. Re-run to verify passes
4. Consider: Archive entire test if feature removed
```

---

## Phase 4: General Documentation (59 files) - 1 hour

**Priority**: LOW - Can be semi-automated

### Approach: Semi-Automated Replacement

Most of these are in docs/ and .claude/ directories with simple mentions.

### Files Include:
- `.claude/AGENT_DELEGATION_RULES.md` (28 refs) - Heavy update needed
- `.claude/skills/` documentation (5 files)
- `docs/` various guides and specs

### Action Plan:
```bash
# Create sed script for bulk replacement:

# Pattern 1: Simple agent mentions
sed -i '' 's/assistant agent (with code analysis skills)/assistant agent (using code analysis skills)/g' FILE

# Pattern 2: Agent lists
sed -i '' 's/, assistant (using code analysis skills)//g' FILE
sed -i '' 's/assistant (using code analysis skills), //g' FILE

# Pattern 3: Delegation examples
sed -i '' 's/delegate to assistant (using code analysis skills)/delegate to assistant for code analysis/g' FILE

# Then manually verify critical files:
- AGENT_DELEGATION_RULES.md (complex examples)
- WORKFLOWS.md (workflow descriptions)
- Any architectural docs
```

### Critical Files Needing Manual Review:
1. `.claude/AGENT_DELEGATION_RULES.md` (28 refs) - Complex delegation logic
2. `docs/WORKFLOWS.md` (5 refs) - Workflow descriptions
3. `docs/AGENT_SINGLETON_ARCHITECTURE.md` (2 refs) - Architecture docs

---

## Phase 5: Historical Files (9 files) - 30 minutes

**Priority**: LOWEST - Historical records

### Files:
- `evidence/activity-summary-*.md` (remaining ones not moved)
- `tickets/BUG-003-pattern-matching-priority.md`

### Options:
**Option A**: Archive all to backup
**Option B**: Add header noting assistant (using code analysis skills) is deprecated
**Option C**: Update references inline

### Recommendation: **Option B**
```markdown
> **Note**: This document references the deprecated `assistant (using code analysis skills)` agent.
> As of 2025-10-24, code analysis is handled by `assistant` using skills
> (code-forensics, security-audit). See CLEANUP-001 for details.
```

---

## Execution Order

### Session 1 (2 hours):
1. **Python Code** (Phase 1) - 1 hour
   - Start with architect_daily_routine.py (may need removal)
   - Then daemon_spec_manager.py (CFR-011 changes)
   - Update remaining files

2. **Agent Docs** (Phase 2) - 1 hour
   - architect.md
   - assistant.md
   - README.md and others

### Session 2 (1-2 hours):
3. **Test Files** (Phase 3) - 1 hour
   - Fix test_agent_registry.py first (quick win)
   - Update skill tests
   - Handle CFR-011 integration tests

4. **General Docs** (Phase 4) - 30-60 minutes
   - Run semi-automated replacements
   - Manual review of AGENT_DELEGATION_RULES.md
   - Verify WORKFLOWS.md

5. **Historical** (Phase 5) - 15-30 minutes
   - Add deprecation headers
   - Or move to backup

---

## Testing Strategy

After each phase:
```bash
# 1. Search verification
grep -r "assistant (using code analysis skills)" --include="*.py" --include="*.md" . | \
  grep -v ".git/" | \
  grep -v ".claude/skills/assistant (using code analysis skills)/" | \
  wc -l

# 2. Test suite
pytest tests/unit/test_agent_registry.py -v
pytest tests/unit/test_phase2_skills.py -v
pytest tests/unit/test_phase3_skills.py -v

# 3. Commit
git add -A
git commit -m "phase X: description"
```

---

## Quick Wins (Do First)

These are simple and build momentum:

1. **test_agent_registry.py** - Remove ASSISTANT from enum list (5 min)
2. **agent README.md** - Update agent list (10 min)
3. **file_ownership.py** - Already done ✅
4. **implementation_task_creator.py** - Comment update (2 min)

---

## Potentially Complex Files

These may need design decisions:

1. **architect_daily_routine.py** (8 refs)
   - **Decision**: Remove entire module? Or repurpose?
   - CFR-011 requires architect to read assistant (using code analysis skills) reports
   - If no reports exist, what should CFR-011 be?

2. **daemon_spec_manager.py** (7 refs)
   - **Decision**: How to enforce CFR-011 without assistant (using code analysis skills)?
   - Remove CFR-011 entirely?
   - Replace with different requirement?

3. **test_cfr_011_integration.py** (5 refs)
   - **Decision**: Archive test or update?
   - If CFR-011 changes, test needs rewrite

4. **.claude/AGENT_DELEGATION_RULES.md** (28 refs)
   - **Decision**: Extensive rewrite needed
   - Many delegation examples involve assistant (using code analysis skills)
   - Need to rethink code analysis delegation

---

## Success Metrics

- [ ] Zero "assistant (using code analysis skills)" references (except in skills directory)
- [ ] All tests pass
- [ ] Documentation accurate
- [ ] No broken links or examples
- [ ] Skills still accessible and documented

---

## Rollback Plan

If issues arise:
```bash
git revert HEAD  # Revert last commit
# Or
git reset --hard ca3d6d5  # Reset to before cleanup
```

---

**Ready to Execute**: Yes
**Start with**: Quick wins, then Phase 1 (Python code)
