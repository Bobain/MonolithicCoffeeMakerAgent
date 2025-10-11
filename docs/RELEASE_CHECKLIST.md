# Code Developer Daemon - Release Checklist

Run this checklist before creating a new release (v1.x.x, v2.x.x, etc.)

## Pre-Release Testing

### Core Tests
- [ ] All unit tests pass: `pytest tests/`
- [ ] Smoke tests pass: `pytest tests/ci_tests/test_daemon_smoke.py`
- [ ] Non-regression tests pass: `pytest tests/autonomous/test_daemon_regression.py`
- [ ] No test failures or errors in test suite

### Manual Testing
- [ ] Manual daemon test completed (15 min run, no infinite loops)
- [ ] Test in clean environment (fresh virtualenv)
- [ ] Test with real ROADMAP.md
- [ ] Test with multiple priorities (planned, in-progress, complete)
- [ ] Verify daemon moves through priorities correctly
- [ ] Verify daemon creates notifications when blocked

### Database & State
- [ ] Notifications database verified: `python scripts/verify_notifications.py`
- [ ] No database corruption or lock issues
- [ ] Daemon state persists correctly across restarts

### CI/CD
- [ ] GitHub Actions workflow passing
- [ ] All CI test jobs succeed (smoke, unit, integration, regression)
- [ ] No failing checks on main branch

## Integration Testing

### Claude CLI Mode
- [ ] Claude CLI installed and configured
- [ ] Daemon works in CLI mode: `--use-claude-cli`
- [ ] CLI authentication works
- [ ] CLI execution succeeds
- [ ] Token usage tracked correctly

### Anthropic API Mode
- [ ] API key configured: `ANTHROPIC_API_KEY`
- [ ] Daemon works in API mode (default)
- [ ] API authentication works
- [ ] API execution succeeds
- [ ] Token usage tracked correctly

### Error Handling
- [ ] Test network failures (disconnect during run)
- [ ] Test API errors (invalid key, rate limits)
- [ ] Test malformed ROADMAP
- [ ] Test missing dependencies
- [ ] All errors handled gracefully with clear messages

### Notification System
- [ ] Notifications created for blocked priorities
- [ ] Notifications created for max retries
- [ ] Notifications created for no changes
- [ ] User can respond to notifications
- [ ] Daemon respects user responses

## Code Quality

### Code Review
- [ ] Code follows project style guide
- [ ] No pylint/flake8 warnings
- [ ] Type hints present where appropriate
- [ ] No security vulnerabilities
- [ ] No hardcoded credentials or secrets

### Documentation
- [ ] CHANGELOG.md updated with release notes
- [ ] Breaking changes documented
- [ ] New features documented
- [ ] API changes documented
- [ ] README.md updated if needed

## Version Management

### Version Bump
- [ ] Version number bumped in `pyproject.toml`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Version tag matches release number

### ROADMAP Update
- [ ] ROADMAP.md status updated for completed priorities
- [ ] In-progress priorities documented
- [ ] Next priorities planned
- [ ] Dependencies verified

## Deployment

### Pre-Deployment
- [ ] All pre-release checks complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team notified of pending release

### Git Operations
- [ ] Create git tag: `git tag -a v1.x.x -m "Release v1.x.x"`
- [ ] Push tag: `git push origin v1.x.x`
- [ ] Verify GitHub Actions triggered automatically
- [ ] Monitor CI workflow progress

### GitHub Release
- [ ] Create GitHub release from tag
- [ ] Add release notes from CHANGELOG
- [ ] Highlight breaking changes
- [ ] Include upgrade instructions
- [ ] Attach artifacts if needed

### Deployment Verification
- [ ] GitHub Actions completed successfully
- [ ] Release published on GitHub
- [ ] Docker images built (if applicable)
- [ ] Package published to PyPI (if applicable)

## Post-Release

### Monitoring (First 24 Hours)
- [ ] Monitor logs for 24h after release
- [ ] Check notification system working
- [ ] Verify no infinite loops
- [ ] Verify no regressions reported
- [ ] Monitor error rates

### ROADMAP Updates
- [ ] Update ROADMAP with completion status
- [ ] Mark released priorities as "✅ Complete"
- [ ] Update version numbers in ROADMAP
- [ ] Plan next release priorities

### Communication
- [ ] Announce release to team
- [ ] Update documentation website (if applicable)
- [ ] Notify users of breaking changes
- [ ] Provide migration guide if needed

### Rollback Plan
- [ ] Document rollback procedure
- [ ] Keep previous version available
- [ ] Test rollback process
- [ ] Monitor for issues requiring rollback

## Release Notes Template

```markdown
# Release v1.x.x

## 🎉 What's New

- New feature 1
- New feature 2
- Enhancement to existing feature

## 🐛 Bug Fixes

- Fixed issue with X
- Resolved problem with Y

## ⚠️ Breaking Changes

- Changed API for Z (migration guide: link)
- Deprecated feature W (will be removed in v2.0)

## 📚 Documentation

- Updated user guide
- Added new examples
- Improved troubleshooting section

## 🔧 Technical Changes

- Upgraded dependency X to v2.0
- Improved performance of Y
- Refactored Z for maintainability

## 📦 Installation

\`\`\`bash
pip install code-developer==1.x.x
# or
poetry add code-developer@1.x.x
\`\`\`

## 🙏 Contributors

Thanks to everyone who contributed to this release!

---

Full Changelog: https://github.com/org/repo/compare/v1.x-1.x...v1.x.x
```

## Emergency Rollback

If critical issues are discovered after release:

1. **Immediate Actions**:
   - [ ] Stop promoting the release
   - [ ] Document the issue
   - [ ] Notify affected users

2. **Rollback**:
   - [ ] Tag previous stable version
   - [ ] Update installation instructions
   - [ ] Revert documentation changes

3. **Fix & Re-release**:
   - [ ] Create hotfix branch
   - [ ] Fix critical issue
   - [ ] Run full test suite
   - [ ] Release new patch version

## Sign-off

**Release Manager**: _____________________ Date: __________

**QA Lead**: _____________________ Date: __________

**Technical Lead**: _____________________ Date: __________

---

**Release Approved**: ☐ Yes ☐ No

**Notes**:
