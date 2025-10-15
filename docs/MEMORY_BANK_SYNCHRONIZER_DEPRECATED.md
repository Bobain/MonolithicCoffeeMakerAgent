# memory-bank-synchronizer: DEPRECATED

**Status**: No longer needed as of 2025-10-15

**Reason**: Git branch strategy changed to tag-based workflow on single `roadmap` branch

---

## Why Deprecated?

With the new git branch strategy implemented in US-034:
- **All work happens on `roadmap` branch** - No feature branches
- **code_developer uses tags** - Instead of branches for milestones
- **Single CLAUDE.md is source of truth** - No need to sync across branches
- **No branch switching** - Eliminates synchronization complexity

## What It Did

Previously, `memory-bank-synchronizer` was responsible for:
- Synchronizing `.claude/CLAUDE.md` across different feature branches
- Keeping branch-specific documentation current
- Preventing documentation drift between branches

## Why It's No Longer Needed

### Old Workflow (Branch-Based)
```
main branch
  └── feature/us-033
       └── .claude/CLAUDE.md (needs sync from main)
  └── feature/us-034
       └── .claude/CLAUDE.md (needs sync from main)
  └── feature/us-035
       └── .claude/CLAUDE.md (needs sync from main)

Problem: 3+ copies of CLAUDE.md that drift out of sync
Solution: memory-bank-synchronizer keeps them synchronized
```

### New Workflow (Tag-Based)
```
roadmap branch (ONLY branch)
  └── .claude/CLAUDE.md (single source of truth)
  └── Tags mark milestones:
       - feature/us-033-streamlit-app-start
       - feature/us-033-streamlit-app-complete
       - feature/us-034-git-strategy-start
       - feature/us-034-git-strategy-complete

Problem: NONE - single CLAUDE.md file
Solution: No synchronization needed
```

## Migration

All branch-specific logic has been removed:
- Single CLAUDE.md maintained on roadmap branch by all agents
- project_manager and code_developer update CLAUDE.md directly
- No cross-branch synchronization required

## Related Documentation

- **Git Strategy**: `.claude/CLAUDE.md` (Git Branch Strategy section)
- **code_developer Workflow**: `.claude/agents/code_developer.md`
- **GitStrategy Module**: `coffee_maker/autonomous/git_strategy.py`

---

**Deprecated**: 2025-10-15
**Replaced By**: Single-branch workflow with tags
