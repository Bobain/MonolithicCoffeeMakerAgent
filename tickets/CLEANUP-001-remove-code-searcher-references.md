# CLEANUP-001: Remove Remaining code-searcher Agent References

**Type**: Cleanup
**Priority**: Medium
**Estimated Effort**: 4-6 hours
**Status**: Pending

---

## Background

The `code-searcher` agent has been removed from the system. The agent's **skills** (code-forensics, security-audit) remain in `.claude/skills/code-searcher/` and can be used by other agents (primarily `assistant`).

**Partial cleanup completed**: 2025-10-24
- Evidence files moved to backup (121 files)
- `docs/code-searcher/` directory moved to backup
- Critical Python routing updated (`agent_router.py`, `file_ownership.py`)
- AgentType enum no longer includes CODE_SEARCHER

---

## Remaining Work

**612 references** to `code-searcher` agent remain across:

### Documentation Files (~200 references)
- `.claude/agents/architect.md` - 7 references
- `.claude/agents/assistant.md` - 8 references
- `.claude/AGENT_DELEGATION_RULES.md` - 28 references
- `docs/WORKFLOWS.md` - 5 references
- `docs/AGENT_SINGLETON_ARCHITECTURE.md` - 2 references
- Many other documentation files

### Test Files (~50 references)
- `tests/unit/test_context_upfront.py` - 5 references
- `tests/unit/test_phase2_skills.py` - 4 references
- `tests/unit/test_phase3_skills.py` - 10 references
- `tests/ci_tests/test_cfr_011_integration.py` - 5 references
- Other test files

### Python Code (~30 references in comments/logic)
- `coffee_maker/cli/architect_cli.py` - 7 references
- `coffee_maker/autonomous/daemon_spec_manager.py` - 7 references
- `coffee_maker/autonomous/architect_daily_routine.py` - 8 references
- `coffee_maker/autonomous/orchestrator.py` - 4 references
- Others

### Historical/Evidence Files (~300+ references)
- `evidence/activity-summary-*.md` files
- `tickets/BUG-003-pattern-matching-priority.md`
- Historical records (consider archiving vs updating)

---

## Approach

### Phase 1: Update Critical Documentation (2 hours)
1. **Agent Documentation** (`.claude/agents/`)
   - Update architect.md delegation rules
   - Update assistant.md to clarify it now handles code search via skills
   - Update AGENT_DELEGATION_RULES.md
   - Update README.md agent list

2. **General Documentation** (`docs/`)
   - Update WORKFLOWS.md
   - Update AGENT_SINGLETON_ARCHITECTURE.md
   - Update US-031 and other user guides

### Phase 2: Update Test Files (1-2 hours)
1. **Unit Tests**
   - Update test_context_upfront.py
   - Update test_phase2_skills.py and test_phase3_skills.py
   - Fix test_agent_registry.py enum test
   - Update test_file_ownership_enforcement.py

2. **Integration Tests**
   - Update test_cfr_011_integration.py
   - Remove CFR-011 code-searcher report requirements

### Phase 3: Update Python Code (1 hour)
1. **CLI Files**
   - architect_cli.py - Update daily-integration command
   - Remove code-searcher report reading logic

2. **Autonomous Files**
   - daemon_spec_manager.py - Remove CFR-011 code-searcher checks
   - architect_daily_routine.py - Update report reading
   - orchestrator.py - Update comments

### Phase 4: Historical Files (1 hour - decision needed)
1. **Evidence Files** - Already moved to backup ✅
2. **Tickets** - Update BUG-003 or mark as historical
3. **Activity Summaries** - Consider archiving vs updating

---

## Replacement Pattern

When updating references, use this pattern:

**Old**:
```
assistant agent (with code-forensics and security-audit skills) performs deep code analysis
```

**New**:
```
assistant agent performs code analysis using skills (code-forensics, security-audit)
```

**Skills to mention**:
- `code-forensics` - Deep code pattern analysis
- `security-audit` - Security vulnerability scanning
- Available in `.claude/skills/code-searcher/` (directory name kept for organization)

---

## Testing After Cleanup

1. **Search Verification**:
   ```bash
   grep -r "code-searcher" --include="*.py" --include="*.md" . | \
     grep -v ".git/" | \
     grep -v ".claude/skills/code-searcher/" | \
     wc -l
   # Target: 0 references (except in skills directory)
   ```

2. **Test Suite**:
   ```bash
   pytest tests/unit/test_agent_registry.py -v
   # Should pass enum validation

   pytest tests/unit/ -x
   # Should have no code-searcher import errors
   ```

3. **Agent Routing**:
   ```bash
   # Test that code search queries route to assistant
   # Verify skills are accessible
   ```

---

## Files Created in This Cleanup

- `TEST_STATUS_2025-10-24.md` - Test status after database changes
- `remove_code_searcher.sh` - Automated cleanup script (partial)
- This ticket (CLEANUP-001)

---

## Related Changes

This cleanup is part of larger repository cleanup (2025-10-24):
- Code review system redesign (commit-level → implementation-level)
- Technical specs deletion (70 specs removed)
- Archives moved to `../MonolithicCoffeeMakerAgent_backups/2025-10-24/`

---

## Success Criteria

- [ ] Zero references to `code-searcher` agent in active codebase
- [ ] Skills directory `.claude/skills/code-searcher/` kept and documented
- [ ] All tests passing (especially test_agent_registry.py)
- [ ] Documentation updated with correct agent routing
- [ ] Code search functionality works via assistant + skills

---

## Notes

- **Skills are NOT being removed** - Only the agent
- Skills can be invoked by assistant or other agents
- Directory name `.claude/skills/code-searcher/` kept for organizational clarity
- Evidence files archived (not deleted) for historical reference

---

**Created**: 2025-10-24
**Assignee**: TBD
**Blocked By**: None
**Blocks**: None
