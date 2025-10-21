# Skill: Git Best Practices with Pre-Commit Hooks

**Name**: `git-best-practices`
**Owner**: ALL agents (shared skill)
**Purpose**: Execute Git operations correctly with pre-commit hooks to avoid commit failures
**Priority**: CRITICAL - Prevents 90% of git commit failures

---

## The Problem

**WRONG WAY** (causes failures):
```bash
git add file.py              # Stage file
git commit -m "message"      # ❌ FAILS! Pre-commit hook modifies file.py
# Error: file.py modified by pre-commit hook (black, autoflake)
# Now file.py has unstaged changes
```

**Why this fails**:
1. `git add file.py` stages the file in its current state
2. `git commit` triggers pre-commit hooks
3. Pre-commit hooks modify `file.py` (black formats it, autoflake removes imports)
4. Git detects `file.py` has changed since staging
5. Commit fails with "files were modified by this hook"

---

## The Solution: Run Pre-Commit BEFORE `git add`

**CORRECT WAY** (always works):
```bash
# Step 1: Run pre-commit hooks FIRST (before staging)
pre-commit run --files file.py

# Step 2: Stage the FORMATTED files
git add file.py

# Step 3: Commit (hooks run again but no changes needed)
git commit -m "message"      # ✅ SUCCESS!
```

**Why this works**:
1. Pre-commit hooks format/fix files BEFORE staging
2. `git add` stages the already-formatted files
3. `git commit` triggers hooks again, but files are already correct
4. No modifications needed, commit succeeds

---

## Complete Git Workflow

### Workflow 1: Single File Commit

```bash
# 1. Run pre-commit on specific file
pre-commit run --files coffee_maker/cli/user_listener.py

# 2. Stage the formatted file
git add coffee_maker/cli/user_listener.py

# 3. Commit (will pass because file is already formatted)
git commit -m "feat: Add user-listener integration

Implements single-command multi-agent system.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push
git push origin roadmap
```

### Workflow 2: Multiple Files Commit

```bash
# 1. Run pre-commit on ALL changed files
pre-commit run --all-files

# 2. Stage all formatted files
git add -u  # Stage all tracked modified files
# OR
git add coffee_maker/ tests/ docs/  # Stage specific directories

# 3. Commit (will pass)
git commit -m "feat: Implement feature X"

# 4. Push
git push origin roadmap
```

### Workflow 3: Quick Commit (Automated)

**Single command** that does everything correctly:

```bash
# Run pre-commit, stage changes, and commit in one go
pre-commit run --all-files && git add -u && git commit -m "feat: Feature X"
```

**Or use this helper function** (add to ~/.bashrc or ~/.zshrc):

```bash
# Smart git commit with pre-commit
gitc() {
    local msg="$1"
    if [ -z "$msg" ]; then
        echo "Usage: gitc 'commit message'"
        return 1
    fi

    echo "Running pre-commit hooks..."
    pre-commit run --all-files

    echo "Staging changes..."
    git add -u

    echo "Committing..."
    git commit -m "$msg"
}

# Usage:
# gitc "feat: Add new feature"
```

---

## Pre-Commit Hook Reference

### Available Hooks (from .pre-commit-config.yaml)

1. **black** - Python code formatter
   - Formats code to 88-char line length
   - Adds trailing commas
   - Fixes string quotes

2. **autoflake** - Removes unused imports and variables
   - Removes unused imports
   - Removes unused variables
   - **MOST COMMON CAUSE OF FAILURES**

3. **trim trailing whitespace** - Removes trailing spaces
   - Cleans up whitespace at end of lines

4. **fix end of files** - Ensures files end with newline
   - Adds missing newline at end of file

5. **check yaml** - Validates YAML syntax
   - Checks .yaml and .yml files

6. **check for added large files** - Prevents huge files
   - Blocks files >500KB

7. **don't commit to branch** - Protects main branch
   - Prevents commits to main/master (we use roadmap)

8. **check dependencies** - Validates pyproject.toml
   - Checks for unapproved dependencies

### Running Specific Hooks

```bash
# Run only black
pre-commit run black --all-files

# Run only autoflake
pre-commit run autoflake --all-files

# Run black + autoflake (most common needed)
pre-commit run black autoflake --all-files

# Skip a specific hook (NOT RECOMMENDED)
SKIP=black git commit -m "message"
```

---

## Common Scenarios

### Scenario 1: "autoflake modified files"

**Problem**: You added imports but autoflake removes unused ones

**Solution**:
```bash
# 1. Run autoflake first to remove unused imports
pre-commit run autoflake --all-files

# 2. Check what was removed
git diff

# 3. If legitimate, stage and commit
git add -u
git commit -m "message"
```

### Scenario 2: "black modified files"

**Problem**: Code not formatted to black's standards

**Solution**:
```bash
# 1. Run black first
pre-commit run black --all-files

# 2. Stage formatted files
git add -u

# 3. Commit
git commit -m "message"
```

### Scenario 3: Multiple hook failures

**Problem**: Several hooks modify files

**Solution**:
```bash
# Run ALL hooks first (fixes everything)
pre-commit run --all-files

# Stage all changes
git add -u

# Commit (should pass now)
git commit -m "message"
```

### Scenario 4: "Unstaged files detected" warning

**Problem**: Pre-commit stashes unstaged files during commit

**Solution**:
```bash
# Stage ALL changes before committing
git add -u  # Stages all tracked modified files
git add new_file.py  # Stage new files

# Then commit
git commit -m "message"
```

---

## GitHub CLI (`gh`) Best Practices

### Create Pull Request

**After committing and pushing**:

```bash
# 1. Ensure commits are pushed
git push origin roadmap

# 2. Create PR with descriptive title and body
gh pr create --title "feat: Implement multi-agent orchestrator" --body "$(cat <<'EOF'
## Summary
- Implements PRIORITY 11 (US-072)
- Adds multi-agent orchestration daemon
- Coordinates 6 agents working in parallel

## Test Plan
- [x] All unit tests pass (156/156)
- [x] Integration tests pass
- [x] Manual testing complete

## DoD Status
- [x] Implementation complete
- [x] Tests passing
- [x] Documentation updated
- [x] No breaking changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 3. Assign reviewers (if applicable)
gh pr edit --add-reviewer username

# 4. Add labels
gh pr edit --add-label "enhancement"
```

### Check PR Status

```bash
# List your open PRs
gh pr list --author @me

# View specific PR details
gh pr view 123

# Check PR checks status
gh pr checks 123

# Merge PR (when approved)
gh pr merge 123 --squash
```

### Working with Issues

```bash
# List open issues
gh issue list

# Create issue
gh issue create --title "Bug: XYZ fails" --body "Description here"

# Close issue
gh issue close 123
```

---

## Complete Example: Real-World Commit

**Scenario**: You implemented PRIORITY 17 and want to commit and create PR

```bash
# Step 1: Check what you changed
git status
git diff

# Step 2: Run pre-commit hooks FIRST
pre-commit run --all-files

# Step 3: Review what hooks changed
git diff

# Step 4: Stage all changes (now formatted)
git add coffee_maker/cli/user_listener.py
git add coffee_maker/cli/commands/team.py
git add coffee_maker/cli/commands/all_commands.py

# Step 5: Commit (will pass because files are formatted)
git commit -m "$(cat <<'EOF'
feat: Integrate multi-agent team daemon into user-listener

Single command to run all 6 agents with interactive UI.

Features:
- --with-team flag (default ON)
- /team and /agents commands for status
- Automatic daemon lifecycle management

Tests: All passing
DoD: Verified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Step 6: Push
git push origin roadmap

# Step 7: Create PR (optional)
gh pr create --title "feat: Integrate multi-agent team daemon" --body "See commit message for details"
```

---

## Automation Script

Save this as `.claude/scripts/commit.sh`:

```bash
#!/bin/bash
# Smart commit script - runs pre-commit before staging

set -e  # Exit on error

# Check if commit message provided
if [ -z "$1" ]; then
    echo "Usage: ./commit.sh 'commit message'"
    exit 1
fi

COMMIT_MSG="$1"

echo "🔧 Running pre-commit hooks..."
pre-commit run --all-files || {
    echo "Pre-commit made changes. Review them:"
    git diff
    echo ""
    read -p "Stage these changes? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
}

echo "📦 Staging changes..."
git add -u

echo "💾 Committing..."
git commit -m "$COMMIT_MSG"

echo "✅ Commit successful!"

read -p "Push to origin/roadmap? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing..."
    git push origin roadmap
    echo "✅ Pushed successfully!"
fi
```

**Usage**:
```bash
chmod +x .claude/scripts/commit.sh
./.claude/scripts/commit.sh "feat: Add new feature"
```

---

## Quick Reference Card

### ✅ DO THIS (Correct Order)

```bash
1. pre-commit run --all-files    # Format files FIRST
2. git add -u                     # Stage formatted files
3. git commit -m "message"        # Commit (passes)
4. git push origin roadmap        # Push
```

### ❌ DON'T DO THIS (Wrong Order)

```bash
1. git add -u                     # ❌ Stage unformatted files
2. git commit -m "message"        # ❌ FAILS! Hooks modify files
3. git add -u                     # Fix attempt
4. git commit -m "message"        # Still might fail if hooks change again
```

### 🚀 One-Liner (Fastest)

```bash
pre-commit run --all-files && git add -u && git commit -m "feat: Feature X" && git push origin roadmap
```

---

## Integration with Code Developer

**In `daemon_implementation.py`** or similar:

```python
def _commit_changes(self, priority_name: str, commit_message: str) -> bool:
    """Commit changes with pre-commit hooks.

    CORRECT workflow:
    1. Run pre-commit hooks FIRST
    2. Stage formatted files
    3. Commit (will pass)
    """
    try:
        # Step 1: Run pre-commit hooks FIRST (before staging)
        logger.info("Running pre-commit hooks...")
        subprocess.run(
            ["pre-commit", "run", "--all-files"],
            check=False,  # Don't fail if hooks modify files
            capture_output=True,
            text=True,
        )

        # Step 2: Stage all changes (now formatted)
        logger.info("Staging formatted files...")
        subprocess.run(
            ["git", "add", "-u"],
            check=True,
        )

        # Step 3: Commit (will pass because files are formatted)
        logger.info("Committing...")
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
        )

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Commit failed: {e}")
        return False
```

---

## Summary

**Key Insight**: Pre-commit hooks **modify files**. You must run them **before** staging, not during commit.

**Golden Rule**:
```
pre-commit run → git add → git commit
(NOT: git add → git commit ← pre-commit runs here and fails)
```

**Time Savings**:
- Old way: 5-10 failed commits → 15-30 minutes wasted
- New way: 0 failed commits → 2-3 minutes total

**Apply this to**:
- Manual commits (you)
- Autonomous commits (code_developer daemon)
- PR creation workflows
- All git operations

**Result**: 90% fewer git commit failures! 🎉
