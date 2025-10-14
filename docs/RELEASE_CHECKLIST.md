# code_developer Daemon - Release Checklist

Run this checklist before creating a new release (v1.x.x, v2.x.x, etc.) to ensure the daemon is production-ready.

## 🎯 Overview

This checklist ensures:
- ✅ All tests pass
- ✅ No regressions introduced
- ✅ Documentation is up-to-date
- ✅ Daemon works for end users
- ✅ Release is tagged and published correctly

## 📋 Pre-Release Testing

### 1. Unit Tests
```bash
# Run all unit tests
pytest tests/ -v

# Expected: All tests pass
```

- [ ] All unit tests pass
- [ ] No test failures or errors
- [ ] No skipped tests (unless intentional)

### 2. CI Tests
```bash
# Run CI test suite
pytest tests/ci_tests/ -v

# Expected: All tests pass in <10 minutes
```

- [ ] Smoke tests pass (`test_daemon_smoke.py`)
- [ ] CLI mode tests pass (`test_daemon_cli_mode.py`)
- [ ] API mode tests pass (`test_daemon_api_mode.py`)
- [ ] User scenario tests pass (`test_daemon_user_scenarios.py`)
- [ ] ROADMAP parsing tests pass (`test_roadmap_parsing.py`)
- [ ] Error handling tests pass (`test_error_handling.py`)

### 3. Non-Regression Tests
```bash
# Run non-regression suite
pytest tests/autonomous/test_daemon_regression.py -v

# Expected: All critical functionality intact
```

- [ ] Daemon initialization works
- [ ] ROADMAP parsing works
- [ ] Git operations work
- [ ] Both CLI and API modes work
- [ ] Backward compatibility maintained

### 4. Integration Tests (Manual)

**Important**: Run these in a **separate terminal** (not inside Claude Code session).

```bash
# Test 1: Daemon initialization
poetry run code-developer --verbose

# Expected: Daemon starts without errors

# Test 2: Daemon finds next priority
# Check logs: Should find next 📝 Planned priority

# Test 3: Prerequisite checks pass
# Check logs: All prerequisites OK

# Stop daemon (Ctrl+C) after verification
```

- [ ] Daemon initializes successfully
- [ ] Finds next planned priority
- [ ] All prerequisite checks pass
- [ ] No errors in logs

### 5. Health Checks
```bash
# Check daemon health (if logs exist)
python scripts/check_daemon_health.py

# Check notification system
python scripts/verify_notifications.py
```

- [ ] No infinite loop patterns detected
- [ ] Notification system working
- [ ] Database schema correct

### 6. GitHub Actions
```bash
# Verify GitHub Actions workflow exists
cat .github/workflows/daemon-test.yml

# Expected: Workflow properly configured
```

- [ ] GitHub Actions workflow exists
- [ ] Workflow configured for PRs to main
- [ ] Workflow configured for releases
- [ ] All jobs properly defined

## 📚 Documentation

### 1. Update CHANGELOG
```bash
# Edit CHANGELOG.md
vim CHANGELOG.md
```

- [ ] New version section added
- [ ] All features listed
- [ ] All bug fixes listed
- [ ] Breaking changes documented (if any)
- [ ] Credits/contributors mentioned

### 2. Update Version Number
```bash
# Update version in pyproject.toml
vim pyproject.toml

# Example: version = "1.2.0"
```

- [ ] Version bumped in `pyproject.toml`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Version matches release tag (v1.2.0 → 1.2.0)

### 3. Update ROADMAP
```bash
# Mark completed priorities
vim docs/roadmap/ROADMAP.md
```

- [ ] Completed priorities marked ✅ Complete
- [ ] New priorities added (if any)
- [ ] Status section updated
- [ ] "Next Priority" pointer updated

### 4. Verify Documentation
```bash
# Check all docs are up-to-date
ls docs/*.md

# Key docs to verify:
# - QUICKSTART_DAEMON.md
# - CLAUDE_CLI_MODE.md
# - DAEMON_TESTING.md
# - TROUBLESHOOTING.md
```

- [ ] QUICKSTART updated with latest features
- [ ] CLI mode docs updated
- [ ] Testing guide updated
- [ ] Troubleshooting updated with new issues
- [ ] No broken links in documentation

## 🚀 Deployment

### 1. Create Git Tag
```bash
# Create annotated tag
git tag -a v1.2.0 -m "Release v1.2.0: Description of release"

# Example:
git tag -a v1.2.0 -m "Release v1.2.0: Add CI testing infrastructure"

# Verify tag
git tag -l -n9 v1.2.0
```

- [ ] Tag created with correct version
- [ ] Tag has descriptive message
- [ ] Tag is annotated (not lightweight)

### 2. Push Tag
```bash
# Push tag to origin
git push origin v1.2.0

# This triggers GitHub Actions automatically
```

- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow triggered
- [ ] All CI tests pass on GitHub

### 3. Create GitHub Release
```bash
# Go to GitHub → Releases → Draft a new release
# Or use gh CLI:
gh release create v1.2.0 --title "v1.2.0" --notes-file RELEASE_NOTES.md
```

Release notes should include:

- [ ] Release title (e.g., "v1.2.0: CI Testing Infrastructure")
- [ ] What's new (features)
- [ ] What's fixed (bug fixes)
- [ ] Breaking changes (if any)
- [ ] Upgrade instructions (if needed)
- [ ] Credits/acknowledgments

**Release Notes Template**:
```markdown
## v1.2.0 - YYYY-MM-DD

### ✨ What's New
- Feature 1: Description
- Feature 2: Description

### 🐛 Bug Fixes
- Fix 1: Description
- Fix 2: Description

### 📚 Documentation
- Updated guides for X
- Added examples for Y

### ⚠️ Breaking Changes
- None (or list changes)

### 🔧 Upgrade Instructions
1. `git pull origin main`
2. `poetry install`
3. `poetry run code-developer --version`

### 👏 Credits
Thanks to contributors: @username1, @username2
```

- [ ] Release created on GitHub
- [ ] Release notes comprehensive
- [ ] Release marked as "Latest" (if appropriate)

## 🔍 Post-Release Verification

### 1. Verify Release Artifacts
```bash
# Clone fresh copy and test
git clone https://github.com/yourname/project.git fresh-test
cd fresh-test
git checkout v1.2.0
poetry install
poetry run code-developer --version
```

- [ ] Fresh clone works
- [ ] Installation succeeds
- [ ] Version number correct
- [ ] Daemon starts without errors

### 2. Monitor First Production Run
```bash
# Start daemon and monitor
poetry run code-developer --verbose

# Watch for:
# - Initialization errors
# - Prerequisite check failures
# - Unexpected errors
```

**Monitor for 15-30 minutes**:
- [ ] No initialization errors
- [ ] Daemon finds priorities correctly
- [ ] No infinite loops
- [ ] Notifications created correctly
- [ ] Git operations work

### 3. Check GitHub Actions Results
Go to GitHub → Actions → Check workflow run for tag

- [ ] All jobs passed
- [ ] Smoke tests passed
- [ ] Unit tests passed
- [ ] Health checks passed
- [ ] Test coverage acceptable

### 4. Update Project Status
```bash
# Update README or status badge
vim README.md
```

- [ ] README updated with latest version
- [ ] Status badges updated (if any)
- [ ] Quick-start commands verified

## 📊 Post-Release Monitoring (24h)

After release, monitor for:

### Day 1 (First 24 hours)
- [ ] Check logs for errors
- [ ] Monitor notification system
- [ ] Verify no infinite loops
- [ ] Check GitHub issues for problems
- [ ] Monitor CI runs on new PRs

### Week 1 (First 7 days)
- [ ] Gather user feedback
- [ ] Fix any critical bugs
- [ ] Update documentation based on feedback
- [ ] Plan next release priorities

## ✅ Release Completion

Once all items checked:

```bash
# Update ROADMAP to reflect completion
vim docs/roadmap/ROADMAP.md

# Add release to CHANGELOG
vim CHANGELOG.md

# Commit and push
git add .
git commit -m "docs: Mark release v1.2.0 complete"
git push origin main
```

- [ ] All checklist items complete
- [ ] Release verified working
- [ ] Documentation updated
- [ ] Team notified of release

## 🚨 Rollback Plan (If Issues Found)

If critical issues discovered after release:

### Option 1: Hot Fix Release
```bash
# Create hotfix branch
git checkout -b hotfix/v1.2.1 v1.2.0

# Make fixes
# ... fix code ...

# Create new release v1.2.1
git tag -a v1.2.1 -m "Hotfix: Description"
git push origin v1.2.1
```

### Option 2: Revert Release
```bash
# Mark release as pre-release on GitHub
# Update docs to warn users
# Create issue tracking the problem
```

- [ ] Rollback plan documented
- [ ] Users notified if issues found
- [ ] Hotfix released if needed

## 📞 Emergency Contacts

**If critical issues found**:
- Create GitHub issue immediately
- Tag release as "pre-release" if needed
- Update README with warning
- Notify users via issues/discussions

## 📝 Notes

**Use this space for release-specific notes**:

- Release version: __________
- Release date: __________
- Release manager: __________
- Special notes: __________

---

**✨ Congratulations on the release! ✨**

Remember: A good release is tested, documented, and monitored. Take your time with this checklist!
