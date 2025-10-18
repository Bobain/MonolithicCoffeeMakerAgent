# Skill: Git Workflow Automation

**Name**: `git-workflow-automation`
**Owner**: code_developer
**Purpose**: Automate git operations (commit, push, PR creation) to speed up implementation workflow
**Priority**: HIGH - Reduces manual git work from 10-15 minutes to 2-3 minutes

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ After completing priority implementation
- ✅ After DoD verification passes
- ✅ When ready to create pull request
- ✅ During autonomous development workflow

**Example Trigger**:
```python
# code_developer: After DoD verification passes
dod_result = self._verify_dod(priority_name)
if dod_result["status"] == "PASS":
    git_result = self._execute_git_workflow(priority_name, dod_result["report"])
```

---

## Skill Execution Steps

### Step 1: Analyze Changes and Generate Commit Message

**Inputs Needed**:
- `$PRIORITY_NAME`: Priority identifier (e.g., "PRIORITY 10")
- `$PRIORITY_DESCRIPTION`: Full priority description
- `$FILES_CHANGED`: List of modified files
- `$DOD_REPORT_PATH`: Path to DoD verification report

**Actions**:

**1. Get changed files**:
```bash
# Staged files
git diff --cached --name-only

# Unstaged files
git diff --name-only

# Untracked files
git ls-files --others --exclude-standard
```

**2. Analyze changes**:
```bash
# Get diff statistics
git diff --stat

# Get detailed changes
git diff
```

**3. Generate commit message**:

**Format** (following conventional commits):
```
<type>(<scope>): <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation only
- `test`: Adding/updating tests
- `chore`: Maintenance (dependencies, configs)
- `perf`: Performance improvement

**Example**:
```
feat(recipes): Implement recipe creation feature

Implements PRIORITY 10 - User Recipe Management

Features:
- Create new coffee recipes with name, coffee amount, water amount
- Validate recipe inputs (positive values required)
- Display recipes in list view
- Error handling for invalid inputs

Tests: 23/23 passing (87% coverage)
DoD: Verified (see data/dod_reports/PRIORITY_10_dod_20251018.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Output**: Commit message draft
```python
commit_message = {
    "type": "feat",
    "scope": "recipes",
    "subject": "Implement recipe creation feature",
    "body": "Implements PRIORITY 10...",
    "full_message": "feat(recipes): Implement recipe creation feature\n\n..."
}
```

### Step 2: Stage Files Intelligently

**Smart Staging Logic**:

**1. Always stage**:
- Implementation files (coffee_maker/*.py)
- Test files (tests/*.py)
- Documentation (docs/*.md, README.md)
- Configuration (.claude/*.md, pyproject.toml if architect approved)

**2. Never stage**:
- Secrets (.env, *.key, credentials.json)
- Large files (>1MB unless intentional)
- IDE files (.idea/, .vscode/ unless already tracked)
- Build artifacts (__pycache__/, *.pyc, .pytest_cache/)

**3. Warn before staging**:
- database.db (data files)
- Binary files (unless part of requirement)

**Implementation**:
```bash
# Stage implementation files
git add coffee_maker/

# Stage tests
git add tests/

# Stage docs (if changed)
git add docs/ README.md

# Stage .claude configs (if changed)
git add .claude/

# Check for secrets BEFORE staging
if grep -r "API_KEY\|SECRET\|PASSWORD" coffee_maker/ tests/; then
    echo "⚠️  WARNING: Potential secrets detected!"
    # Don't stage, warn user
fi
```

**Output**: Staged files list
```python
staged_files = [
    "coffee_maker/recipes.py",
    "tests/unit/test_recipes.py",
    "README.md"
]
```

### Step 3: Create Commit with Validation

**Pre-commit Validation**:

**1. Run pre-commit hooks**:
```bash
# This runs automatically on git commit
# But we can run manually first to catch issues
pre-commit run --all-files
```

**2. If hooks fail**:
```python
if pre_commit_failed:
    # Fix issues automatically
    black coffee_maker/ tests/
    autoflake --in-place --remove-all-unused-imports coffee_maker/ tests/

    # Re-stage fixed files
    git add coffee_maker/ tests/

    # Retry commit
```

**3. Create commit**:
```bash
# Use heredoc for multiline message
git commit -m "$(cat <<'EOF'
feat(recipes): Implement recipe creation feature

Implements PRIORITY 10 - User Recipe Management

Features:
- Create new coffee recipes
- Validate inputs
- Display recipes

Tests: 23/23 passing (87% coverage)
DoD: Verified (see data/dod_reports/PRIORITY_10_dod_20251018.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Output**: Commit result
```python
commit_result = {
    "status": "success",
    "commit_hash": "abc123def",
    "files_committed": 3,
    "message": "feat(recipes): Implement recipe creation feature"
}
```

### Step 4: Create Git Tag (Optional)

**When to tag**:
- After implementation complete and tests passing → `wip-*` tag
- After DoD verification → `dod-verified-*` tag (project_manager does this)

**Tag Format**:
```bash
# WIP tag (code_developer creates)
git tag -a wip-priority-10 -m "PRIORITY 10 implementation complete, awaiting DoD

Features:
- Recipe creation
- Recipe validation
- Recipe display

Tests: 23/23 passing (87% coverage)
Status: Implementation complete, awaiting DoD verification"
```

**Output**: Tag created
```python
tag_result = {
    "tag_name": "wip-priority-10",
    "message": "PRIORITY 10 implementation complete...",
    "created": True
}
```

### Step 5: Push to Remote

**Push Strategy** (CFR-013: roadmap branch only):

**1. Check current branch**:
```bash
current_branch=$(git branch --show-current)

if [ "$current_branch" != "roadmap" ]; then
    echo "❌ ERROR: Must be on 'roadmap' branch (CFR-013)"
    exit 1
fi
```

**2. Push commit**:
```bash
# Push to roadmap branch
git push origin roadmap

# Push tag (if created)
git push origin wip-priority-10
```

**3. Handle push failures**:
```python
if push_failed:
    # Likely: Remote has commits we don't have
    # Solution: Pull and rebase

    git pull --rebase origin roadmap

    # Resolve conflicts (if any)
    # Re-push
    git push origin roadmap
```

**Output**: Push result
```python
push_result = {
    "status": "success",
    "branch": "roadmap",
    "remote": "origin",
    "commits_pushed": 1,
    "tags_pushed": ["wip-priority-10"]
}
```

### Step 6: Create Pull Request

**PR Creation with gh CLI**:

**1. Generate PR title**:
```
Implement PRIORITY 10 - User Recipe Management
```

**2. Generate PR body**:
```markdown
## Summary

Implements PRIORITY 10: User Recipe Management

Features:
- ✅ Create new coffee recipes with name, coffee amount, water amount
- ✅ Validate recipe inputs (positive values required)
- ✅ Display recipes in list view
- ✅ Error handling for invalid inputs

## Changes

### Implementation
- `coffee_maker/recipes.py` - Recipe creation logic
- `coffee_maker/models/recipe.py` - Recipe data model

### Tests
- `tests/unit/test_recipes.py` - Unit tests (23 tests)
- `tests/integration/test_recipe_workflow.py` - Integration tests (5 tests)

### Documentation
- `README.md` - Updated with recipe creation instructions

## Test Results

- ✅ Unit tests: 23/23 passing
- ✅ Integration tests: 5/5 passing
- ✅ Coverage: 87% (threshold: 80%)
- ✅ Pre-commit hooks: All passed

## DoD Verification

**Status**: ✅ PASS

See full DoD report: `data/dod_reports/PRIORITY_10_dod_20251018.md`

All MUST-HAVE criteria met:
- ✅ User can create new coffee recipe
- ✅ All tests pass
- ✅ Code follows Black formatting
- ✅ No console errors in UI
- ✅ Documentation updated

## Deployment Notes

No special deployment steps required. No database migrations needed.

## Related Issues

Closes #10 (if GitHub issue exists)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**3. Create PR**:
```bash
gh pr create \
    --title "Implement PRIORITY 10 - User Recipe Management" \
    --body "$(cat <<'EOF'
## Summary
...
EOF
)" \
    --base main \
    --head roadmap \
    --assignee @me \
    --label "feature" \
    --label "priority-10"
```

**Output**: PR created
```python
pr_result = {
    "status": "success",
    "pr_number": 42,
    "pr_url": "https://github.com/user/repo/pull/42",
    "title": "Implement PRIORITY 10 - User Recipe Management"
}
```

### Step 7: Update ROADMAP Status

**Update ROADMAP.md**:

**Before**:
```markdown
## PRIORITY 10: User Recipe Management 🔄 In Progress
```

**After**:
```markdown
## PRIORITY 10: User Recipe Management ✅ Complete

**PR**: #42 (https://github.com/user/repo/pull/42)
**DoD**: Verified (data/dod_reports/PRIORITY_10_dod_20251018.md)
**Completed**: 2025-10-18
```

**Implementation**:
```python
# Read ROADMAP
roadmap_path = Path("docs/roadmap/ROADMAP.md")
roadmap = roadmap_path.read_text()

# Update status
old_line = f"## {priority_name}: {priority_title} 🔄 In Progress"
new_line = f"""## {priority_name}: {priority_title} ✅ Complete

**PR**: #{pr_number} ({pr_url})
**DoD**: Verified ({dod_report_path})
**Completed**: {datetime.now().strftime('%Y-%m-%d')}
"""

roadmap = roadmap.replace(old_line, new_line)

# Write back
roadmap_path.write_text(roadmap)

# Commit ROADMAP update
git add docs/roadmap/ROADMAP.md
git commit -m "docs(roadmap): Mark PRIORITY 10 as complete"
git push origin roadmap
```

**Output**: ROADMAP updated
```python
roadmap_result = {
    "status": "updated",
    "priority": "PRIORITY 10",
    "new_status": "✅ Complete"
}
```

---

## Complete Workflow Summary

**Skill executes this workflow automatically**:

```python
def execute_git_workflow(priority_name, priority_description, dod_report_path):
    """Execute complete git workflow."""

    # Step 1: Generate commit message
    commit_msg = generate_commit_message(priority_name, priority_description, dod_report_path)

    # Step 2: Stage files
    staged_files = stage_files_intelligently()

    # Step 3: Commit with validation
    commit_result = create_commit_with_validation(commit_msg)

    # Step 4: Create tag
    tag_result = create_wip_tag(priority_name)

    # Step 5: Push to remote
    push_result = push_to_remote(branch="roadmap", tag=tag_result["tag_name"])

    # Step 6: Create PR
    pr_result = create_pull_request(priority_name, priority_description, dod_report_path)

    # Step 7: Update ROADMAP
    roadmap_result = update_roadmap_status(priority_name, pr_result["pr_url"])

    return {
        "status": "success",
        "commit_hash": commit_result["commit_hash"],
        "pr_number": pr_result["pr_number"],
        "pr_url": pr_result["pr_url"],
        "roadmap_updated": True
    }
```

---

## Integration with code_developer Agent

```python
# coffee_maker/autonomous/daemon_implementation.py

def _complete_priority_workflow(self, priority_name: str, priority_description: str):
    """Complete workflow: Implement → DoD → Git → PR → ROADMAP update."""

    # 1. Implement priority
    self._implement_priority(priority_name, priority_description)

    # 2. Verify DoD
    dod_result = self._verify_dod(priority_name, priority_description)

    if dod_result["status"] != "PASS":
        logger.error(f"❌ DoD verification failed for {priority_name}")
        return

    # 3. Execute git workflow using skill
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

    skill = load_skill(SkillNames.GIT_WORKFLOW_AUTOMATION, {
        "PRIORITY_NAME": priority_name,
        "PRIORITY_DESCRIPTION": priority_description,
        "FILES_CHANGED": ", ".join(self._get_changed_files()),
        "DOD_REPORT_PATH": dod_result["report_path"],
    })

    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    if result and result.success:
        logger.info(f"✅ Git workflow complete for {priority_name}")
        logger.info(f"   PR: {result.content}")
    else:
        logger.error(f"❌ Git workflow failed for {priority_name}")
```

---

## Skill Checklist (code_developer Must Complete)

After DoD verification passes:

- [ ] ✅ Load git-workflow-automation skill
- [ ] ✅ Generate conventional commit message
- [ ] ✅ Stage files intelligently (exclude secrets)
- [ ] ✅ Run pre-commit hooks, fix issues if needed
- [ ] ✅ Create commit with descriptive message + 🤖 footer
- [ ] ✅ Create `wip-*` tag for implementation milestone
- [ ] ✅ Push commit and tag to roadmap branch (CFR-013)
- [ ] ✅ Create PR with comprehensive description
- [ ] ✅ Update ROADMAP.md status to "✅ Complete"
- [ ] ✅ Move to next priority

**Failure to follow git workflow = Messy history, unclear commits, delayed reviews**

---

## Success Metrics

**Time Savings**:
- **Before**: 10-15 minutes manual git operations
- **After**: 2-3 minutes with skill automation
- **Savings**: 7-12 minutes per priority

**Quality Improvements**:
- **Consistent commit messages**: Conventional commits format every time
- **Better PR descriptions**: Comprehensive, includes DoD report
- **Proper tagging**: Milestones marked with tags
- **No secrets committed**: Automated secret detection

**Measurement**:
- Track time from "DoD PASS" to "PR created"
- Track number of commits with proper format
- Track number of accidental secret commits (should be 0)

---

## Related Skills

- **dod-verification**: Verify DoD before git workflow (prerequisite)
- **test-failure-analysis**: Fix tests before committing
- **roadmap-health-check**: Monitor priority completion progress

---

**Remember**: Git workflow automation = Faster iterations, cleaner history! 🚀

**code_developer's Mantra**: "Automate git, focus on code!"
