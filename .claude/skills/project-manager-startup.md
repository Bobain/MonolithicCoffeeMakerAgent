# Project Manager Agent Startup Skill

## Step 1: Load Required Context

- [ ] Read docs/roadmap/ROADMAP.md
- [ ] Read .claude/CLAUDE.md
- [ ] Read .claude/agents/project-manager.md

## Step 2: Validate CFR-007 Compliance

- [ ] Calculate total context budget:
  - Agent prompt (project-manager.md): ~10K tokens
  - Required docs (ROADMAP, CLAUDE.md): ~15K tokens
  - Total: ~25K tokens
- [ ] Check against context window (200K tokens)
- [ ] Verify <30% (60K tokens max)

## Step 3: Health Checks

- [ ] Verify GitHub access:
  - GITHUB_TOKEN (optional but recommended)
  - gh command available
- [ ] Verify file access:
  - docs/roadmap/ (writable)
  - docs/ (writable for top-level files)

## Step 4: Initialize Project Resources

- [ ] Check GitHub repository status
- [ ] Verify ROADMAP.md is readable
- [ ] Register with AgentRegistry

## Success Criteria

- ✅ GitHub access working (or gracefully degraded)
- ✅ ROADMAP.md readable
- ✅ Context budget <30%
- ✅ Agent registered
