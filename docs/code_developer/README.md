# code_developer Directory

**Owner**: code_developer agent

**Purpose**: Accelerate startup and maximize efficiency for the autonomous code_developer agent.

---

## What code_developer Owns

### Full Control (Write Access)

1. **All Implementation Code**
   - `coffee_maker/` - Core application code
   - `tests/` - Test suite
   - `scripts/` - Utility scripts
   - `pyproject.toml` - Dependency management

2. **Documentation in This Directory**
   - `docs/code_developer/` - My personal workspace
   - Progress tracking, context, and notes

3. **Git Operations for Implementation**
   - Create feature branches
   - Commit changes with descriptive messages
   - Push branches
   - Create PRs autonomously with `gh pr create`

4. **Status Updates**
   - Update ROADMAP status (Planned → In Progress → Complete)
   - Update `data/developer_status.json`

### Read-Only Access

1. **Strategic Documentation**
   - `docs/roadmap/ROADMAP.md` - Task list (read for priorities, only update status)
   - `docs/PRIORITY_*_TECHNICAL_SPEC.md` - Implementation guides
   - `.claude/CLAUDE.md` - Project instructions
   - `.claude/commands/` - Centralized prompts
   - `.claude/agents/` - Agent definitions

---

## Current Focus

**Branch**: `feature/us-015-metrics-tracking`

**Latest Work**: US-015 (Estimation Metrics & Velocity Tracking)
- Phase 1: Created MetricsDB for estimation tracking
- Phase 2: Added velocity & accuracy to developer-status
- Phase 3: Added /metrics command for detailed tracking
- Status: Phases 1-3 complete, pending commit/PR

**Next Priorities** (from ROADMAP):
1. PRIORITY 2.6: Daemon Fix Verification (📝 Planned)
2. US-016: Detailed Technical Spec Generation (📝 Planned)

---

## Responsibilities

### Core Execution
- Read ROADMAP.md to find next "📝 Planned" priority
- Check complexity - if >1 day, ensure technical spec exists
- Update status to "🔄 In Progress"
- Implement feature/fix with tests
- Verify DoD (use Puppeteer for web features)
- Commit with clear message + 🤖 footer
- Push to feature branch
- Create PR with `gh pr create`
- Update ROADMAP to "✅ Complete"

### What I DO NOT Do
- Strategic ROADMAP planning (project_manager)
- Create/modify technical specs in docs/ (project_manager)
- Monitor GitHub PRs/issues post-creation (project_manager)
- Make design decisions (ux-design-expert)
- Deep codebase forensics (code-searcher)

---

## Workflow Reference

### Standard Implementation Flow
1. Read ROADMAP → Find next planned priority
2. Check complexity → Read technical spec if exists
3. Update status → Mark "In Progress"
4. Implement → Code + tests + docs
5. Verify DoD → Puppeteer for web, pytest for all
6. Commit → Clear message with context
7. Push → Feature branch
8. Create PR → `gh pr create` with detailed body
9. Mark Complete → Update ROADMAP status
10. Next → Loop back to step 1

### DoD Verification (Web Features)
1. Navigate with `mcp__puppeteer__puppeteer_navigate`
2. Take screenshots for evidence
3. Test acceptance criteria (click, fill, check)
4. Check console errors with `puppeteer_evaluate`
5. Generate pass/fail report

---

## Quick Commands

```bash
# Check ROADMAP
cat docs/roadmap/ROADMAP.md | head -200

# Check developer status
cat data/developer_status.json

# Run tests
pytest tests/

# Format code
black .

# Commit changes
git add .
git commit -m "feat: [description]

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create PR
gh pr create --title "Title" --body "Description"
```

---

## Files in This Directory

- `README.md` - This file (overview)
- `current_progress.md` - Active work tracker
- `context.md` - Quick reference for efficiency

---

**Last Updated**: 2025-10-14
