# End-to-End Testing Guide for Autonomous Daemon

Complete guide for validating the autonomous development daemon end-to-end.

## 🎯 Overview

End-to-end (E2E) testing validates the **complete autonomous development workflow**:

```
ROADMAP.md → Daemon → Claude CLI → Implementation → Git → PR → ROADMAP Update
```

Unlike unit tests (test individual functions) or integration tests (test components together), E2E tests validate the **entire system working as a user would experience it**.

---

## ⚠️ Important Warnings

### E2E Tests Perform REAL Operations

E2E tests are **not mocked** - they perform actual operations:

- ✅ **Create real Git branches** in your repository
- ✅ **Execute real Claude CLI commands** (uses API credits)
- ✅ **Make real Git commits** to branches
- ✅ **Push to remote repository** (if enabled)
- ✅ **Create real pull requests** (if enabled)
- ✅ **Modify files** in your working directory

### When to Run E2E Tests

✅ **Do run E2E tests when**:
- Validating the daemon works end-to-end
- Testing a major daemon change
- Verifying deployment configuration
- Demonstrating the system to stakeholders
- Before marking PRIORITY 3 as complete

❌ **Don't run E2E tests when**:
- In CI/CD pipelines (too slow, uses credits)
- During regular development (use unit/integration tests)
- On the main branch (use feature branches)
- Without Claude CLI authentication
- Without understanding what will happen

---

## 📋 Prerequisites

Before running E2E tests, ensure:

### 1. Claude CLI Installed and Authenticated

```bash
# Check Claude CLI is available
claude --version

# Authenticate (if needed)
claude login

# Verify authentication
claude code -p "print('test')"
```

**Installation**:
- macOS: `brew install anthropics/claude/claude`
- Other: See [Claude CLI documentation](https://docs.anthropic.com/en/docs/cli)

### 2. gh CLI Installed and Authenticated

```bash
# Check gh CLI is available
gh --version

# Authenticate (if needed)
gh auth login

# Verify authentication
gh auth status
```

**Installation**:
- macOS: `brew install gh`
- Other: See [GitHub CLI documentation](https://cli.github.com/)

### 3. Git Repository with Remote

```bash
# Verify remote exists
git remote -v

# Should show origin (or other remote)
# origin  git@github.com:user/repo.git (fetch)
# origin  git@github.com:user/repo.git (push)

# If no remote, add one
git remote add origin <your-repo-url>
```

### 4. On a Feature Branch (Not main/master)

```bash
# Check current branch
git branch --show-current

# If on main/master, create feature branch
git checkout -b feature/e2e-testing
```

**Why**: E2E tests create branches and commits. Running on main could cause conflicts.

### 5. Clean Working Directory

```bash
# Check status
git status

# Should show "nothing to commit, working tree clean"
# If not, commit or stash changes
git stash
```

---

## 🚀 Quick Start

### Method 1: Run Automated E2E Tests

Run the pytest-based E2E test suite:

```bash
# Enable E2E tests via environment variable
export DAEMON_E2E_TEST=1

# Run all E2E tests (safe - doesn't create PRs)
pytest tests/e2e/test_daemon_e2e.py -v -s

# Run with pytest flag instead
pytest tests/e2e/test_daemon_e2e.py -v -s --run-e2e

# Run specific test
pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2ESimple::test_daemon_reads_test_roadmap -v -s --run-e2e
```

**These tests**:
- ✅ Create test roadmaps
- ✅ Test daemon initialization
- ✅ Verify roadmap parsing
- ✅ Test component integration
- ❌ Do NOT execute Claude CLI (safe)
- ❌ Do NOT create PRs (safe)

### Method 2: Run Full E2E Test (Creates Real PRs!)

⚠️ **WARNING**: This creates real branches, commits, and PRs!

```bash
# Enable full E2E testing
export DAEMON_E2E_TEST=1
export DAEMON_E2E_FULL=1

# Run full implementation test
pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2EFull::test_daemon_full_implementation -v -s
```

**This test**:
- ✅ Creates real Git branch
- ✅ Executes Claude CLI (uses credits!)
- ✅ Makes real commits
- ⚠️ Can push to remote (if configured)
- ⚠️ Can create real PRs (if configured)

### Method 3: Manual E2E Testing

Most controlled method - you run each step manually:

See [Manual E2E Testing](#manual-e2e-testing) section below.

---

## 🔬 Automated E2E Test Details

### Test Structure

```
tests/e2e/
├── __init__.py
└── test_daemon_e2e.py
    ├── TestDaemonE2EPrerequisites     # Verify prerequisites
    ├── TestDaemonE2ESimple            # Simple tests (safe)
    ├── TestDaemonE2EFull              # Full tests (creates PRs!)
    └── TestDaemonE2EManual            # Generate manual instructions
```

### Test Fixtures

**`simple_test_roadmap`**: Creates a minimal test roadmap:
```markdown
### 🔴 **PRIORITY 1: Add Hello World Function**
**Status**: 📝 Planned
**Deliverables**:
- Create hello_world.py
- Add test_hello_world.py
```

**`test_roadmap_dir`**: Temporary directory for test files

### Running Individual Test Suites

**Prerequisites Tests** (verify setup):
```bash
pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2EPrerequisites -v
```

Validates:
- Claude CLI available
- gh CLI available and authenticated
- Git remote configured
- Not on main branch

**Simple E2E Tests** (safe):
```bash
pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2ESimple -v -s --run-e2e
```

Tests:
- Daemon reads test roadmap
- Finds next planned priority
- Extracts deliverables
- No real implementation

**Full E2E Tests** (creates PRs!):
```bash
export DAEMON_E2E_FULL=1
pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2EFull -v -s --run-e2e
```

Tests:
- Daemon initialization
- Complete implementation workflow
- Real Claude CLI execution
- Real Git operations

---

## 📖 Manual E2E Testing

### Overview

Manual E2E testing gives you complete control over each step. Use this method when:
- Learning how the daemon works
- Debugging daemon issues
- Demonstrating to stakeholders
- Want to see each step in detail

### Step-by-Step Procedure

#### Step 1: Create Test Roadmap

Create a simple roadmap for testing:

```bash
cat > /tmp/ROADMAP_E2E_TEST.md <<'EOF'
# E2E Test Roadmap

### 🔴 **PRIORITY 1: Add Hello World Function** ⚡ E2E-TEST

**Status**: 📝 Planned
**Estimated Duration**: 5 minutes
**Impact**: ⭐ (Test only)

**Deliverables**:
- Create `coffee_maker/hello_world.py` with `hello()` function
- Function should return the string "Hello, World!"
- Add docstring explaining the function
- Create `tests/test_hello_world.py` with one test
- Test should verify function returns "Hello, World!"

**Implementation Notes**:
- Keep implementation simple
- Follow existing project structure
- Use type hints
- Add proper docstrings

---
EOF
```

#### Step 2: Verify Prerequisites

Before running daemon:

```bash
# 1. Check Claude CLI
claude --version
claude code -p "print('test')"

# 2. Check gh CLI
gh --version
gh auth status

# 3. Check Git
git remote -v
git status

# 4. Check branch
git branch --show-current  # Should NOT be main/master
```

#### Step 3: Run Daemon on Test Roadmap

Run daemon in controlled mode:

**Option A: No PR Creation** (safest):
```bash
python run_daemon.py \
    --roadmap /tmp/ROADMAP_E2E_TEST.md \
    --auto-approve \
    --no-pr \
    --sleep 5 \
    --model claude-sonnet-4
```

**Option B: With PR Creation**:
```bash
python run_daemon.py \
    --roadmap /tmp/ROADMAP_E2E_TEST.md \
    --auto-approve \
    --sleep 5 \
    --model claude-sonnet-4
```

**Option C: Interactive (asks for approval)**:
```bash
python run_daemon.py \
    --roadmap /tmp/ROADMAP_E2E_TEST.md \
    --sleep 5
```

#### Step 4: Monitor Daemon Output

Watch for these log messages:

**1. Daemon Startup**:
```
╔════════════════════════════════════════════════════════════════╗
║            Autonomous Development Daemon v1.0                  ║
╚════════════════════════════════════════════════════════════════╝

Config:
  - Roadmap: /tmp/ROADMAP_E2E_TEST.md
  - Auto-approve: True
  - Create PRs: False
  - Sleep: 5s
  - Model: claude-sonnet-4

[INFO] Starting daemon loop...
```

**2. Roadmap Parsing**:
```
[INFO] Reading roadmap: /tmp/ROADMAP_E2E_TEST.md
[INFO] Found 1 priorities
[INFO] Next planned priority: PRIORITY 1 (Add Hello World Function)
```

**3. Approval** (if not auto-approve):
```
[INFO] Requesting user approval for PRIORITY 1...
[INFO] Created notification 25
[INFO] Waiting for approval (timeout: 5 minutes)...
[INFO] Check: project-manager notifications
[INFO] Approve: project-manager respond 25 approve
```

**4. Branch Creation**:
```
[INFO] User approved PRIORITY 1
[INFO] Creating feature branch: feature/priority-1
[INFO] Successfully created branch: feature/priority-1
[INFO] Checked out branch: feature/priority-1
```

**5. Claude CLI Execution**:
```
[INFO] Executing Claude CLI to implement PRIORITY 1...
[INFO] Prompt: Read roadmap and implement PRIORITY 1: Add Hello World Function
[INFO] Model: claude-sonnet-4
[INFO] Timeout: 3600s
[INFO] Executing: claude code -p "..."
```

(This will take 1-5 minutes while Claude implements)

**6. Implementation Complete**:
```
[INFO] Claude CLI completed successfully
[INFO] Exit code: 0
[INFO] Files created/modified: 2
[INFO]   - coffee_maker/hello_world.py
[INFO]   - tests/test_hello_world.py
```

**7. Git Operations**:
```
[INFO] Staging changes...
[INFO] Staged 2 files
[INFO] Committing changes...
[INFO] Commit created: abc1234
[INFO] Commit message: feat: Implement PRIORITY 1 - Add Hello World Function
```

**8. Push** (if not --no-pr):
```
[INFO] Pushing to remote: origin/feature/priority-1
[INFO] Successfully pushed
```

**9. PR Creation** (if not --no-pr):
```
[INFO] Creating pull request...
[INFO] Base branch: main
[INFO] Head branch: feature/priority-1
[INFO] PR created: https://github.com/user/repo/pull/123
[INFO] PR #123: Implement PRIORITY 1: Add Hello World Function
```

**10. Completion**:
```
[INFO] PRIORITY 1 completed successfully
[INFO] Sleeping for 5 seconds before next iteration...
[INFO] Checking for next priority...
[INFO] No more planned priorities
[INFO] Daemon shutting down gracefully
```

#### Step 5: Validate Implementation

Check that daemon created the expected files:

```bash
# Switch to feature branch (if not already there)
git checkout feature/priority-1

# List created files
ls -la coffee_maker/hello_world.py
ls -la tests/test_hello_world.py

# View file contents
cat coffee_maker/hello_world.py
cat tests/test_hello_world.py

# Run tests
pytest tests/test_hello_world.py -v

# Expected output:
# tests/test_hello_world.py::test_hello PASSED
```

#### Step 6: Review Commit

Check the commit created by daemon:

```bash
# View commit history
git log --oneline -n 3

# View commit details
git show HEAD

# Expected commit message format:
# feat: Implement PRIORITY 1 - Add Hello World Function
#
# Deliverables:
# - Created hello_world.py with hello() function
# - Added test_hello_world.py with test
#
# 🤖 Generated with Claude Code via DevDaemon
#
# Co-Authored-By: Claude <noreply@anthropic.com>
```

#### Step 7: Review PR (if created)

If `--no-pr` was NOT used:

```bash
# View PR in terminal
gh pr view

# View PR in browser
gh pr view --web

# Check PR status
gh pr checks

# View PR diff
gh pr diff
```

Expected PR format:
- **Title**: "Implement PRIORITY 1: Add Hello World Function"
- **Body**: Deliverables checklist + summary
- **Labels**: Auto-labeled as "autonomous-development"
- **Checks**: CI should be running

#### Step 8: Merge PR (Optional)

If implementation looks good:

```bash
# Review one more time
gh pr view

# Merge PR (squash merge recommended)
gh pr merge --squash

# Or merge in browser
gh pr view --web
```

#### Step 9: Cleanup

After E2E test complete:

```bash
# Return to original branch
git checkout main  # or your original branch

# Pull merged changes (if you merged PR)
git pull

# Delete feature branch locally
git branch -D feature/priority-1

# Delete feature branch remotely (if not merged)
git push origin --delete feature/priority-1

# Remove test roadmap
rm /tmp/ROADMAP_E2E_TEST.md
```

---

## ✅ Success Criteria

### E2E Test Passes If:

1. ✅ **Daemon Starts**: No crashes on startup
2. ✅ **Roadmap Parsed**: Successfully reads and parses test roadmap
3. ✅ **Priority Found**: Identifies PRIORITY 1 as planned
4. ✅ **Branch Created**: Creates `feature/priority-1` branch
5. ✅ **Claude Executes**: Claude CLI runs without errors
6. ✅ **Files Created**: All deliverable files exist
7. ✅ **Tests Pass**: New tests pass (pytest returns 0)
8. ✅ **Commit Made**: Git commit created with proper format
9. ✅ **Push Succeeds**: Branch pushed to remote (if enabled)
10. ✅ **PR Created**: Pull request created (if enabled)
11. ✅ **No Errors**: No exceptions or critical errors in logs
12. ✅ **Daemon Continues**: Daemon checks for next priority

### Additional Quality Checks:

- ✅ Code follows project style (type hints, docstrings)
- ✅ Commit message follows conventions
- ✅ PR description is clear and complete
- ✅ No unintended files modified
- ✅ Branch is clean (no uncommitted changes)

---

## ❌ Troubleshooting

### Daemon Hangs or Freezes

**Symptom**: Daemon stops responding, no output

**Common Causes**:
1. Running inside Claude Code session
2. Claude CLI waiting for input
3. Git waiting for credentials
4. Network timeout

**Solutions**:
```bash
# 1. Check if in Claude session
echo $CLAUDE_CODE_SESSION  # Should be empty

# 2. Kill daemon
Ctrl+C  # or kill process

# 3. Run in separate terminal (not Claude Code)
# 4. Check Claude CLI works: claude code -p "test"
# 5. Check Git credentials: git push origin main
```

### Claude CLI Fails

**Symptom**: `[ERROR] Claude CLI failed: ...`

**Common Causes**:
1. Not authenticated
2. API rate limit
3. Invalid prompt
4. Timeout

**Solutions**:
```bash
# 1. Re-authenticate
claude login

# 2. Test manually
claude code -p "print hello world"

# 3. Check API status
# Visit https://status.anthropic.com

# 4. Increase timeout
python run_daemon.py --roadmap /tmp/test.md --timeout 7200
```

### Branch Creation Fails

**Symptom**: `[ERROR] Failed to create branch`

**Common Causes**:
1. Uncommitted changes
2. Branch already exists
3. Not in Git repo

**Solutions**:
```bash
# 1. Check status
git status

# 2. Stash changes
git stash

# 3. Delete existing branch
git branch -D feature/priority-1

# 4. Verify Git repo
git remote -v
```

### PR Creation Fails

**Symptom**: `[ERROR] Failed to create PR`

**Common Causes**:
1. gh CLI not authenticated
2. Branch not pushed
3. Base branch doesn't exist
4. PR already exists

**Solutions**:
```bash
# 1. Re-authenticate gh
gh auth login

# 2. Check authentication
gh auth status

# 3. Test PR creation manually
gh pr create --title "Test" --body "Test"

# 4. List existing PRs
gh pr list
```

### Tests Fail

**Symptom**: Created files exist but tests fail

**Common Causes**:
1. Implementation bug
2. Test expectations wrong
3. Missing dependencies

**Solutions**:
```bash
# 1. Run tests with verbose output
pytest tests/test_hello_world.py -vv

# 2. Check implementation
cat coffee_maker/hello_world.py

# 3. Run pytest with debugging
pytest tests/test_hello_world.py -vv --pdb

# 4. Check dependencies
poetry install
```

### Files Not Created

**Symptom**: Claude CLI succeeds but no files created

**Common Causes**:
1. Claude misunderstood prompt
2. Files created in wrong location
3. Git ignored files

**Solutions**:
```bash
# 1. Check all directories
find . -name "*hello*" -type f

# 2. Check Claude CLI output
# Review daemon logs for Claude's response

# 3. Check .gitignore
cat .gitignore

# 4. Try simpler priority
# Use more explicit deliverables
```

---

## 📊 E2E Test Results Template

Use this template to document E2E test results:

```markdown
# E2E Test Results - [Date]

## Test Configuration
- **Roadmap**: /tmp/ROADMAP_E2E_TEST.md
- **Priority**: PRIORITY 1 (Add Hello World Function)
- **Auto-approve**: Yes/No
- **Create PRs**: Yes/No
- **Model**: claude-sonnet-4
- **Branch**: feature/e2e-testing

## Test Results

### ✅ Successes
- [x] Daemon started without errors
- [x] Roadmap parsed successfully
- [x] Branch created: feature/priority-1
- [x] Claude CLI executed (3m 24s)
- [x] Files created: hello_world.py, test_hello_world.py
- [x] Tests passed (1/1)
- [x] Commit created: abc1234
- [x] Pushed to remote
- [x] PR created: #123

### ❌ Failures
- None

### ⚠️ Warnings
- None

### 📈 Metrics
- **Total Time**: 4m 35s
- **Claude CLI Time**: 3m 24s
- **Files Created**: 2
- **Tests Added**: 1
- **Lines of Code**: 25

### 📝 Notes
- Claude implementation was clean and followed project style
- Tests passed on first run
- PR description was clear and complete
- No manual intervention required

### ✅ Conclusion
E2E test **PASSED**. Daemon is fully operational and ready for production use.
```

---

## 🎓 E2E Testing Best Practices

### 1. Start Small

Begin with simple priorities:
- Single file creation
- Simple function implementation
- One test file

Example:
```markdown
### PRIORITY 1: Add Hello World
**Deliverables**:
- Create hello.py
- Function returns "Hello"
- Add test
```

### 2. Test in Safe Environment

- Use feature branches (not main)
- Use `--no-pr` flag first
- Test roadmap in /tmp first
- Use separate Git remote for testing

### 3. Monitor Closely

- Watch daemon output in real-time
- Keep terminal visible
- Check files immediately after creation
- Review commits before pushing

### 4. Validate Thoroughly

After each E2E test:
- Run all tests: `pytest -v`
- Check Git history: `git log`
- Review file contents
- Verify code style

### 5. Document Results

Record:
- What worked
- What failed
- Unexpected behaviors
- Performance metrics

### 6. Iterate

- Start with simple tests
- Gradually increase complexity
- Test edge cases
- Refine prompts based on results

---

## 🚀 Next Steps After E2E Validation

Once E2E tests pass:

### 1. Mark PRIORITY 3 Complete

Update ROADMAP.md:
```markdown
**Status**: ✅ COMPLETE (E2E tested and validated)
```

### 2. Run on Real Roadmap

Start using daemon for real work:
```bash
python run_daemon.py \
    --roadmap docs/ROADMAP.md \
    --sleep 30 \
    --model claude-sonnet-4
```

### 3. Implement Remaining Priorities

Let daemon implement PRIORITY 4-8 autonomously:
- PRIORITY 4: Streamlit Analytics Dashboard
- PRIORITY 5: Error Monitoring Dashboard
- PRIORITY 6: Agent Interaction UI
- PRIORITY 7: Professional Documentation
- PRIORITY 8: Innovative Projects

### 4. Monitor and Refine

- Watch daemon performance
- Review PRs created
- Refine roadmap deliverables
- Adjust sleep intervals
- Tune prompts

### 5. Dogfooding

Use the system to improve itself:
- Let daemon fix its own bugs
- Add features to daemon via roadmap
- Document improvements
- Create metrics dashboard

---

## 📚 Additional Resources

- [DAEMON_USAGE.md](DAEMON_USAGE.md) - Complete daemon usage guide
- [PROJECT_MANAGER_CLI_USAGE.md](PROJECT_MANAGER_CLI_USAGE.md) - CLI guide
- [ROADMAP.md](ROADMAP.md) - Project roadmap
- [ADR_001](ADR_001_DATABASE_SYNC_STRATEGY.md) - Database sync architecture

---

## 🎉 Success!

If E2E tests pass, congratulations! You have a fully operational autonomous development system!

The daemon can now:
- Read roadmaps autonomously
- Implement features without human intervention
- Create branches, commits, and PRs automatically
- Update roadmap status
- Continue until all priorities complete

**Next**: Let it implement PRIORITY 4-8 and watch your project grow autonomously!

---

**Generated**: 2025-10-09
**Last Updated**: 2025-10-09
**Version**: 1.0
**Status**: ✅ Complete
