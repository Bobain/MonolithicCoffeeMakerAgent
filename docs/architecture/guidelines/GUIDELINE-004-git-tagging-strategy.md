# GUIDELINE-004: Git Tagging Strategy for Stable Versions and Milestones

**Category**: Best Practice

**Applies To**: All agents (code_developer, project_manager, assistant)

**Author**: project_manager

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Status**: Active

**Related CFRs**: CFR-013 - All Agents Must Work on `roadmap` Branch Only

**Related Specs**: SPEC-009 - Enhanced Communication, SPEC-045 - Architect-Only Spec Creation

---

## Overview

This guideline establishes a consistent git tagging strategy for marking stable versions, milestones, and DoD-verified features. Tags provide rollback points, release tracking, and clear visibility into project progress.

**Key Principle**: Tags are lightweight markers for important states - use them to mark stability, completion, and milestones, not every commit.

---

## When to Use

Use git tags when:

- **code_developer** completes a priority with all tests passing (wip-*)
- **project_manager** verifies DoD with Puppeteer testing (dod-verified-*)
- **assistant** confirms comprehensive testing shows stability (ready for stable-*)
- **Team** reaches a major milestone (milestone-*)
- **Multiple priorities** are complete and verified (stable-v*.*.*)

Tags complement CFR-013 (roadmap branch workflow) by marking important states without requiring branch switching.

---

## When NOT to Use

Do NOT use git tags when:

- Work is incomplete or has failing tests
- Changes are minor (typos, formatting)
- Feature hasn't been tested yet
- DoD hasn't been verified
- It's just a routine commit (use regular commits instead)

---

## The Pattern

### Explanation

Our git tagging strategy uses four tag types:

1. **`wip-*`**: Work In Progress - Feature complete, tests passing, awaiting DoD
2. **`dod-verified-*`**: Definition of Done verified with Puppeteer testing
3. **`milestone-*`**: Major feature or epic complete (multiple priorities)
4. **`stable-v*.*.*`**: Production-ready release with all priorities verified

This approach provides:
- Clear rollback points to known-good states
- Visible release history in git log
- CI/CD integration (deploy from stable-* tags)
- Progress tracking for stakeholders
- Easy identification of DoD-verified vs stable releases

### Principles

1. **Progressive Stability**: Tags mark increasing levels of confidence (wip → dod-verified → stable)
2. **Agent Ownership**: Each agent type creates specific tag types based on their role
3. **Semantic Versioning**: stable-* tags follow semver (v1.2.3) for clear version tracking
4. **Descriptive Messages**: Tag messages explain what's included and why it's significant
5. **Complement Commits**: Tags mark states, commits record changes - use both appropriately

---

## Tag Types

### 1. WIP Tags (`wip-*`)

**Created By**: code_developer

**When**: After completing priority implementation with all tests passing

**Format**: `wip-us-XXX` or `wip-priority-X`

**Purpose**: Mark feature complete but awaiting DoD verification

**Example**:
```bash
# code_developer completes US-047
git tag -a wip-us-047 -m "US-047 implementation complete, awaiting DoD verification

Features:
- Architect-only spec creation
- User approval workflow
- Error handling improvements

Tests: All passing (23 tests)
Status: Awaiting DoD verification with Puppeteer"

git push origin wip-us-047
```

**Benefits**:
- Clear marker that implementation is done
- Tests are passing but DoD not yet verified
- Easy to rollback if DoD fails
- Visible in git log for team tracking

---

### 2. DoD-Verified Tags (`dod-verified-*`)

**Created By**: project_manager (or assistant during demo testing)

**When**: After verifying DoD requirements with Puppeteer testing

**Format**: `dod-verified-us-XXX` or `dod-verified-priority-X`

**Purpose**: Mark feature as DoD-verified and ready for stable release

**Example**:
```bash
# project_manager verifies DoD with Puppeteer
git tag -a dod-verified-us-047 -m "US-047 DoD verified with Puppeteer testing

Verification Steps:
- Tested spec creation workflow end-to-end
- Confirmed user approval process works
- Verified error handling scenarios
- Validated integration with daemon

DoD Status: ✅ All criteria met
Tested By: project_manager
Test Date: 2025-10-17"

git push origin dod-verified-us-047
```

**Benefits**:
- Confirms feature meets all DoD criteria
- Includes verification evidence (Puppeteer tests)
- Ready for inclusion in stable release
- Provides audit trail for QA

---

### 3. Milestone Tags (`milestone-*`)

**Created By**: project_manager (or team consensus)

**When**: After completing major feature or epic (multiple priorities)

**Format**: `milestone-priority-X` or `milestone-epic-name`

**Purpose**: Mark significant project achievements

**Example**:
```bash
# Team completes PRIORITY 9 (multiple user stories)
git tag -a milestone-priority-9 -m "Milestone: PRIORITY 9 - Architect Enablement Complete

Completed User Stories:
- US-045: Daemon delegates spec creation to architect ✅
- US-046: Architect asks user for approval ✅
- US-047: Architect-only spec creation ✅
- US-048: Silent background agents ✅
- US-049: Continuous spec improvement ✅

Impact:
- Architect now handles all spec creation
- User approval workflow established
- Agents run silently in background
- Continuous improvement process in place

Total Effort: 12 days
Status: All DoD verified, ready for stable release"

git push origin milestone-priority-9
```

**Benefits**:
- Celebrates major achievements
- Groups related priorities together
- Provides high-level progress view
- Useful for stakeholder reporting

---

### 4. Stable Version Tags (`stable-v*.*.*`)

**Created By**: project_manager (with team agreement)

**When**: After multiple priorities are DoD-verified and system is stable

**Format**: `stable-vMAJOR.MINOR.PATCH` (semantic versioning)

**Purpose**: Mark production-ready releases for deployment

**Versioning**:
- **MAJOR**: Breaking changes or major architectural shifts
- **MINOR**: New features, backward-compatible
- **PATCH**: Bug fixes, minor improvements

**Example**:
```bash
# System stable with US-045, US-047, US-048 complete
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement & Silent Agents

New Features:
- Architect-only spec creation (US-045, US-047) ✅
- User approval workflow for important decisions ✅
- Silent background agents (US-048) ✅
- Continuous spec improvement loop (US-049) ✅

Bug Fixes:
- Fixed daemon crash on missing priority content
- Improved error handling in spec creation

Breaking Changes: None

DoD Status: All priorities DoD-verified
Tests: 156 passing, 0 failing
CI/CD: All checks passing
Deployment: Ready for production

Previous: stable-v1.2.0
Next: stable-v1.4.0 (planned)"

git push origin stable-v1.3.0
```

**Benefits**:
- Clear version numbering for releases
- Includes comprehensive release notes
- Signals production readiness
- CI/CD can deploy from these tags
- Easy rollback to previous stable versions

---

## Implementation

### Step-by-Step Guide

#### 1. code_developer: Create WIP Tag After Implementation

```bash
# 1. Ensure all tests pass
pytest
# All tests must pass before tagging!

# 2. Ensure on roadmap branch (CFR-013)
git branch
# * roadmap  ✅ Correct

# 3. Commit all changes
git add .
git commit -m "feat: Implement US-047 - Architect-only spec creation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Create WIP tag
git tag -a wip-us-047 -m "US-047 implementation complete, awaiting DoD verification

Features:
- Architect-only spec creation
- User approval workflow
- Error handling improvements

Tests: All passing (23 tests)
Status: Awaiting DoD verification with Puppeteer"

# 5. Push commit AND tag
git push origin roadmap
git push origin wip-us-047

# 6. Notify project_manager
# (DeveloperStatus notification sent automatically)
```

---

#### 2. project_manager: Create DoD-Verified Tag After Testing

```bash
# 1. Test with Puppeteer
# Use MCP or Python client to verify DoD criteria

# 2. If DoD satisfied, create tag
git tag -a dod-verified-us-047 -m "US-047 DoD verified with Puppeteer testing

Verification Steps:
- Tested spec creation workflow end-to-end ✅
- Confirmed user approval process works ✅
- Verified error handling scenarios ✅
- Validated integration with daemon ✅

DoD Status: All criteria met
Tested By: project_manager
Test Date: $(date +%Y-%m-%d)"

# 3. Push tag
git push origin dod-verified-us-047

# 4. Update ROADMAP status to Complete ✅
# (Use roadmap_cli.py to update status)
```

---

#### 3. project_manager: Create Milestone Tag After Epic Complete

```bash
# 1. Verify all priorities in milestone are DoD-verified
git tag -l "dod-verified-us-*"
# dod-verified-us-045
# dod-verified-us-046
# dod-verified-us-047
# dod-verified-us-048
# dod-verified-us-049

# 2. Create milestone tag
git tag -a milestone-priority-9 -m "Milestone: PRIORITY 9 - Architect Enablement Complete

Completed User Stories:
- US-045: Daemon delegates spec creation to architect ✅
- US-046: Architect asks user for approval ✅
- US-047: Architect-only spec creation ✅
- US-048: Silent background agents ✅
- US-049: Continuous spec improvement ✅

Impact:
- Architect now handles all spec creation
- User approval workflow established
- Agents run silently in background
- Continuous improvement process in place

Total Effort: 12 days
Status: All DoD verified, ready for stable release"

# 3. Push tag
git push origin milestone-priority-9
```

---

#### 4. project_manager: Create Stable Version Tag After System Stable

```bash
# 1. Verify system stability
# - All tests passing
# - All DoD-verified tags present
# - No known critical bugs
# - CI/CD checks passing

# 2. Determine version number
# - Current: stable-v1.2.0
# - Changes: New features (minor bump)
# - Next: stable-v1.3.0

# 3. Create stable tag
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement & Silent Agents

New Features:
- Architect-only spec creation (US-045, US-047) ✅
- User approval workflow for important decisions ✅
- Silent background agents (US-048) ✅
- Continuous spec improvement loop (US-049) ✅

Bug Fixes:
- Fixed daemon crash on missing priority content
- Improved error handling in spec creation

Breaking Changes: None

DoD Status: All priorities DoD-verified
Tests: 156 passing, 0 failing
CI/CD: All checks passing
Deployment: Ready for production

Previous: stable-v1.2.0
Next: stable-v1.4.0 (planned)"

# 4. Push tag
git push origin stable-v1.3.0

# 5. Notify team (optional)
# Send notification that new stable release is ready
```

---

### Code Examples

#### Good Example: Progressive Tagging Workflow

```bash
# ✅ GOOD: Progressive tags marking increasing stability

# Day 1: code_developer completes implementation
git tag -a wip-us-047 -m "Implementation complete, tests passing"
git push origin wip-us-047

# Day 2: project_manager verifies DoD
git tag -a dod-verified-us-047 -m "DoD verified with Puppeteer"
git push origin dod-verified-us-047

# Day 5: All PRIORITY 9 user stories complete
git tag -a milestone-priority-9 -m "PRIORITY 9 complete"
git push origin milestone-priority-9

# Day 7: System stable, ready for release
git tag -a stable-v1.3.0 -m "Release v1.3.0"
git push origin stable-v1.3.0
```

**Why This is Good**:
- Progressive stability markers (wip → dod-verified → milestone → stable)
- Each agent creates appropriate tags for their role
- Clear progression visible in git log
- Easy to rollback to any stability level
- Complements CFR-013 (all on roadmap branch)

---

#### Bad Example: Inconsistent Tagging

```bash
# ❌ BAD: Creating stable tag without DoD verification

# Day 1: code_developer completes and immediately tags as stable
git tag -a stable-v1.3.0 -m "Done"  # ❌ No DoD verification!
git push origin stable-v1.3.0

# Result: Unstable release marked as stable!
```

**Why This is Bad**:
- Skipped DoD verification step
- No Puppeteer testing done
- Tag message lacks detail
- Misleads team about stability

**How to Fix**:
- Use wip-* tag first
- Let project_manager verify DoD
- Only create stable-* after verification
- Include comprehensive tag message

---

#### Edge Cases

```bash
# Edge Case 1: DoD verification fails after wip tag
git tag -a wip-us-047 -m "Implementation complete"
git push origin wip-us-047

# project_manager tests and finds bugs
# Solution: Fix bugs, create new wip tag
git tag -a wip-us-047-v2 -m "Bug fixes applied, ready for DoD retry"
git push origin wip-us-047-v2

# Edge Case 2: Need to rollback from stable release
git tag -l "stable-*"
# stable-v1.2.0 (previous good version)
# stable-v1.3.0 (current broken version)

# Solution: Rollback to previous stable tag
git checkout stable-v1.2.0
# Create new branch for hotfix if needed

# Edge Case 3: Multiple features complete simultaneously
# Solution: Create individual dod-verified tags, then one milestone tag
git tag -a dod-verified-us-045 -m "US-045 DoD verified"
git tag -a dod-verified-us-047 -m "US-047 DoD verified"
git tag -a milestone-priority-9 -m "All PRIORITY 9 features complete"

# Edge Case 4: Hotfix on stable release
git checkout stable-v1.3.0
# Create hotfix branch (exception to CFR-013 for emergencies)
git checkout -b hotfix-critical-bug
# Fix bug...
git commit -m "fix: Critical bug in authentication"
# Create patch release
git tag -a stable-v1.3.1 -m "Hotfix release: Critical auth bug"
git push origin stable-v1.3.1
```

---

## Testing

### Verifying Tags

```bash
# List all tags
git tag -l

# List specific tag types
git tag -l "wip-*"
git tag -l "dod-verified-*"
git tag -l "milestone-*"
git tag -l "stable-*"

# Show tag details
git show wip-us-047

# Verify tag is pushed to remote
git ls-remote --tags origin

# Check what commit a tag points to
git rev-parse wip-us-047
git rev-parse HEAD  # Should match if tagging current commit
```

### Tag Validation Checklist

Before creating each tag type, verify:

**WIP Tags**:
- [ ] All tests passing (`pytest`)
- [ ] On roadmap branch (`git branch`)
- [ ] Changes committed
- [ ] Tag message includes features and test status

**DoD-Verified Tags**:
- [ ] Puppeteer testing completed
- [ ] All DoD criteria met
- [ ] Tag message includes verification details
- [ ] Corresponding wip-* tag exists

**Milestone Tags**:
- [ ] All related priorities have dod-verified-* tags
- [ ] Tag message lists all completed work
- [ ] Impact summary included

**Stable Tags**:
- [ ] Multiple dod-verified-* tags exist
- [ ] All tests passing
- [ ] CI/CD checks passing
- [ ] Version follows semver
- [ ] Comprehensive release notes included

---

## Common Pitfalls

### Pitfall 1: Creating Stable Tags Too Early

**Description**: Marking work as stable before proper verification

**Example**:
```bash
# ❌ Bad: Creating stable tag immediately after implementation
git commit -m "feat: New feature"
git tag -a stable-v1.3.0 -m "Done"  # No testing!
```

**Solution**:
```bash
# ✅ Good: Progressive stability markers
git commit -m "feat: New feature"
git tag -a wip-us-047 -m "Implementation complete, awaiting DoD"
# ... project_manager tests with Puppeteer ...
git tag -a dod-verified-us-047 -m "DoD verified"
# ... multiple priorities verified ...
git tag -a stable-v1.3.0 -m "Release v1.3.0 with full release notes"
```

---

### Pitfall 2: Vague Tag Messages

**Description**: Tag messages that don't explain what's included

**Example**:
```bash
# ❌ Bad: Vague tag message
git tag -a stable-v1.3.0 -m "New version"  # What's new?
```

**Solution**:
```bash
# ✅ Good: Comprehensive tag message
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement

New Features:
- Architect-only spec creation ✅
- User approval workflow ✅
- Silent background agents ✅

Bug Fixes:
- Fixed daemon crash
- Improved error handling

Breaking Changes: None

Tests: 156 passing
DoD: All priorities verified"
```

---

### Pitfall 3: Not Pushing Tags to Remote

**Description**: Creating tags locally but forgetting to push them

**Example**:
```bash
# ❌ Bad: Tag exists locally only
git tag -a stable-v1.3.0 -m "Release v1.3.0"
# Forgot to push! ❌
# Result: CI/CD can't deploy, team can't see tag
```

**Solution**:
```bash
# ✅ Good: Always push tags
git tag -a stable-v1.3.0 -m "Release v1.3.0"
git push origin stable-v1.3.0  # Push tag to remote ✅

# Or push all tags at once
git push origin --tags
```

---

### Pitfall 4: Deleting Tags Without Communication

**Description**: Deleting tags that others may depend on

**Example**:
```bash
# ❌ Bad: Deleting stable tag without warning
git tag -d stable-v1.3.0  # Local delete
git push origin :refs/tags/stable-v1.3.0  # Remote delete
# Result: CI/CD breaks, team confused!
```

**Solution**:
```bash
# ✅ Good: Create new version instead of deleting
# If v1.3.0 is broken, create v1.3.1 with fix
git tag -a stable-v1.3.1 -m "Hotfix: Fixed critical bug from v1.3.0"
git push origin stable-v1.3.1

# Or deprecate old tag (if absolutely necessary)
git tag -a stable-v1.3.0-deprecated -m "Deprecated: Use stable-v1.3.1 instead"
git push origin stable-v1.3.0-deprecated
# Notify team before deleting!
```

---

## Performance Considerations

**Performance Impact**: Low

**Description**:
Git tags are lightweight references (just pointers to commits) with minimal storage and performance overhead. Creating, pushing, and listing tags is fast even with thousands of tags.

**Optimization Tips**:
- Use annotated tags (`-a`) for important markers (includes metadata)
- Use lightweight tags for temporary markers (just `git tag name`)
- Prune old wip-* tags periodically to keep tag list clean
- Use tag namespaces (wip-*, dod-verified-*) for easy filtering
- Consider tag retention policy (keep stable-* forever, archive wip-* after 90 days)

---

## Integration with CFR-013 (Roadmap Branch Workflow)

### How Tags Complement CFR-013

**CFR-013** requires all agents work on `roadmap` branch only (no feature branches).

**Git tags complement this by**:
- Providing rollback points without needing branches
- Marking stability levels on the same branch
- Enabling version tracking without branch complexity
- Supporting CI/CD deployment without feature branches

**Combined Workflow**:
```bash
# All work happens on roadmap branch (CFR-013)
git branch
# * roadmap  ✅

# Progressive tags mark stability on same branch
git log --oneline --decorate
# abc123 (HEAD -> roadmap, tag: stable-v1.3.0) feat: Complete PRIORITY 9
# def456 (tag: dod-verified-us-047) feat: Add DoD verification
# ghi789 (tag: wip-us-047) feat: Implement US-047
# ...

# Result: Clear progression on single branch ✅
```

**Benefits**:
- Simpler git history (one branch)
- Clear stability markers (tags)
- No merge conflicts from multiple branches
- Easy to see what's stable vs in-progress
- Compliant with CFR-013

---

## Integration with CI/CD

### Deployment from Stable Tags

```yaml
# Example GitHub Actions workflow
name: Deploy to Production

on:
  push:
    tags:
      - 'stable-v*.*.*'  # Trigger on stable version tags only

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/stable-v}" >> $GITHUB_OUTPUT

      - name: Deploy to production
        run: ./scripts/deploy.sh ${{ steps.version.outputs.VERSION }}
```

**Benefits**:
- Automated deployment from stable tags
- No manual intervention needed
- Clear version tracking in production
- Easy rollback to previous stable-* tag

---

## Related Patterns

### Related Guideline 1: GUIDELINE-003 - Spec Review Process

[Link to GUIDELINE-003](./GUIDELINE-003-spec-review-process.md)

**Relationship**: Spec reviews and DoD verification often happen at the same time. When project_manager verifies specs are followed during implementation, they can create dod-verified-* tags to mark completion.

### Related CFR: CFR-013 - All Agents Must Work on `roadmap` Branch Only

[Link to CFR-013](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013)

**Relationship**: Tags complement the single-branch workflow by providing rollback points and version markers without needing feature branches.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Tag Everything

**Description**: Creating tags for every commit or minor change

**Why It's Bad**:
- Clutters tag list, making it hard to find important versions
- Dilutes meaning of tags (what's actually stable?)
- Makes git log noisy and hard to read

**Example**:
```bash
# ❌ Anti-pattern: Too many tags
git tag wip-typo-fix
git tag wip-formatting
git tag wip-minor-refactor
git tag wip-updated-comment
# Result: 100+ tags, none meaningful!
```

**Instead Do**:
```bash
# ✅ Good: Tag only significant states
git commit -m "fix: Minor typo"  # Just a commit, no tag
git commit -m "style: Format code"  # Just a commit, no tag
git commit -m "feat: Complete US-047"  # NOW tag it!
git tag -a wip-us-047 -m "US-047 complete, all tests passing"
```

---

### Anti-Pattern 2: Inconsistent Tag Naming

**Description**: Using different tag formats for same type

**Why It's Bad**:
- Hard to filter tags with `git tag -l`
- Confusing for team members
- Breaks CI/CD automation

**Example**:
```bash
# ❌ Anti-pattern: Inconsistent naming
git tag wip-us-047
git tag wip_us_048  # Underscore instead of hyphen
git tag WIP-US-049  # Different case
git tag work-in-progress-us-050  # Different format
# Result: Can't filter with `git tag -l "wip-*"`
```

**Instead Do**:
```bash
# ✅ Good: Consistent naming convention
git tag -a wip-us-047 -m "..."
git tag -a wip-us-048 -m "..."
git tag -a wip-us-049 -m "..."
git tag -a wip-us-050 -m "..."
# Result: Easy to filter with `git tag -l "wip-*"`
```

---

## Checklist

When creating tags, verify:

- [ ] On correct branch (roadmap for CFR-013 compliance)
- [ ] All tests passing (for wip-* tags)
- [ ] DoD verified with Puppeteer (for dod-verified-* tags)
- [ ] Multiple priorities verified (for stable-* tags)
- [ ] Tag name follows convention (wip-*, dod-verified-*, milestone-*, stable-v*.*.*)
- [ ] Tag message is comprehensive (what, why, status)
- [ ] Tag is annotated (`-a` flag) for metadata
- [ ] Tag is pushed to remote (`git push origin <tag>`)
- [ ] Team is notified (automatic via DeveloperStatus or manual)
- [ ] ROADMAP status updated (for dod-verified-* tags)

---

## References

- Git Tagging Documentation: https://git-scm.com/book/en/v2/Git-Basics-Tagging
- Semantic Versioning: https://semver.org/
- CFR-013: All Agents Must Work on `roadmap` Branch Only
- GUIDELINE-003: Spec Review Process
- GitHub Actions: Deploy from Tags

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created guideline | project_manager |

---

## Notes

- This guideline complements CFR-013 (roadmap branch workflow) by providing rollback points without needing branches
- Tags are permanent markers - only create them for significant states
- If unsure whether to tag, ask: "Would I want to rollback to this exact state?" If yes, tag it!
- For questions about tag strategy, contact project_manager or architect
- CI/CD integration examples can be found in `.github/workflows/` (when implemented)

---

**Remember**: Tags are like bookmarks in a book - use them to mark important chapters (milestones), not every page (commit). They should make it easier to navigate your git history, not harder!
