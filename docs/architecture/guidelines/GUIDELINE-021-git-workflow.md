# GUIDELINE-021: Git Workflow

**Category**: Best Practice

**Applies To**: All commits, branches, and PRs

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: [SPEC-025: Hierarchical Modular Spec Architecture](../specs/SPEC-025-hierarchical-modular-spec-architecture/README.md)

---

## Overview

This guideline describes the standard git workflow including commit message format, branch naming, tagging strategy, and pull request creation.

---

## When to Use

Follow this workflow for:
- All feature implementations
- Bug fixes
- Documentation updates
- Any changes to the codebase

---

## When NOT to Use

N/A - This workflow applies to all git work

---

## The Pattern

### Explanation

Our git workflow emphasizes:
1. **Conventional Commits**: Structured commit messages
2. **Feature Branches**: Work on feature branches (per CFR-013, only roadmap branch)
3. **Descriptive Messages**: Clear commit history
4. **Small Commits**: One logical change per commit
5. **Git Tags**: Version control with semantic versioning

### Principles

1. **One Task Per Commit**: Each commit does one thing
2. **Descriptive Messages**: Message explains WHY, not just WHAT
3. **Clean History**: Rebasing to maintain linear history
4. **Tags for Milestones**: Mark important versions
5. **PRs for Review**: All changes via pull requests
6. **Reference Tickets**: Link to PRIORITY or issue numbers

---

## How to Implement

### Step 1: Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, semicolons)
- `refactor`: Code refactoring without feature change
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build, dependencies, CI configuration

**Examples**:

```bash
# Feature with priority reference
feat(PRIORITY 25): Create guidelines library

Create GUIDELINE-012 through GUIDELINE-021 with implementation patterns.
Extract common patterns from existing specs and update references.

Implements Phase 3 of hierarchical spec architecture.
Closes #123

# Bug fix
fix(auth): Fix JWT token expiration validation

Previously, expired tokens were accepted if expiration was exactly now.
Now properly rejects tokens where exp <= current_time.

Adds regression test for edge case.

# Documentation
docs(README): Update installation instructions

Added Python 3.11+ requirement and poetry setup steps.

# Refactoring
refactor(api): Simplify error handling in auth routes

Extracted common HTTPException creation into _create_error_response().
No behavior change, improves maintainability.

# Performance
perf(db): Add indexes to frequently queried columns

Added indexes on users.email and sessions.user_id.
Improves login performance by 40% (measured in tests).
```

### Step 2: Branching Strategy

Per CFR-013, all work happens on the `roadmap` branch:

```bash
# Check out roadmap branch
git checkout roadmap

# Ensure up to date
git pull origin roadmap

# Create feature branch (optional, for parallel work)
git checkout -b roadmap-feature-name

# Make commits
git add .
git commit -m "feat(PRIORITY 25): Implement guidelines"

# Push to remote
git push origin roadmap-feature-name

# Create PR or merge (per orchestrator pattern)
# For sequential work, commit directly to roadmap
```

**Branch Naming** (when creating feature branches for parallel work):
```
roadmap-{priority-name}
roadmap-priority-25-guidelines
roadmap-priority-26-migration
```

### Step 3: Commit for Phase Completion

When completing a phase in hierarchical implementation:

```bash
# Make changes for the phase
git add coffee_maker/ tests/

# Commit with phase reference
git commit -m "feat(PRIORITY 25): Phase 3 - Guidelines Library

Create guidelines GUIDELINE-012 through GUIDELINE-021:
- GUIDELINE-012: Hierarchical Spec Creation
- GUIDELINE-013: Progressive Implementation
- GUIDELINE-014: FastAPI Endpoints
- GUIDELINE-015: Database Migrations
- GUIDELINE-016: Testing Strategy
- GUIDELINE-017: Custom Exceptions
- GUIDELINE-018: Async/Await
- GUIDELINE-019: Configuration
- GUIDELINE-020: Observability
- GUIDELINE-021: Git Workflow

Extract common patterns from existing specs.
Update 2+ specs to reference guidelines.
Update architect.md with guideline creation workflow.

All acceptance criteria met. Ready for Phase 4."

# Push to roadmap
git push origin roadmap
```

### Step 4: Tagging Milestones

Tag important versions with semantic versioning:

```bash
# Tag after phase completion (per GUIDELINE-004)
git tag -a phase3-guidelines -m "PRIORITY 25 Phase 3: Guidelines Library Complete"
git push origin phase3-guidelines

# Tag before major release
git tag -a v1.0.0 -m "Release 1.0.0: Initial version"
git push origin v1.0.0
```

**Tag Format** (per GUIDELINE-004):
- `phase{N}-{name}`: Phase completion (e.g., phase3-guidelines)
- `v{major}.{minor}.{patch}`: Release version (e.g., v1.0.0)
- `wip-{branch}`: Work in progress (e.g., wip-priority-25)

### Step 5: Create Pull Requests

When code is ready for review:

```bash
# Push feature branch
git push origin roadmap-priority-25

# Create PR with template
gh pr create \
  --title "feat(PRIORITY 25): Phase 3 - Guidelines Library" \
  --body "## Summary

Create guidelines library with 10 initial guidelines (012-021).
Extract common patterns and update specs.

## Changes

- Create GUIDELINE-012 through GUIDELINE-021
- Update SPEC-025 architecture
- Update architect.md workflow
- Add guidelines documentation

## Test Plan

- [x] All guidelines follow template format
- [x] Guidelines include code examples
- [x] Anti-patterns documented
- [x] Testing approach included
- [x] 2+ specs updated with references
- [x] Pre-commit hooks pass

## Implementation Details

See docs/roadmap/PRIORITY_25_TECHNICAL_SPEC.md for phase 3 details.
Implements section 'Step 3: Create Initial Guidelines' completely."
```

### Step 6: Squash and Merge

After PR approval:

```bash
# Squash commits before merge
git rebase -i origin/roadmap

# Mark commits as fixup or squash as appropriate
# Then force push
git push --force origin roadmap-priority-25

# Merge to roadmap
git checkout roadmap
git pull origin roadmap
git merge --squash roadmap-priority-25
git commit -m "feat(PRIORITY 25): Phase 3 - Guidelines Library

[PR #123 merged after review]"
git push origin roadmap

# Delete feature branch
git push origin --delete roadmap-priority-25
git branch -d roadmap-priority-25
```

### Step 7: Update ROADMAP After Commit

After committing, update ROADMAP.md:

```bash
# Edit ROADMAP.md
vi docs/roadmap/ROADMAP.md

# Change status
# FROM: ### PRIORITY 25: ... 📝 Planned - Phase 3
# TO: ### PRIORITY 25: ... ✅ Complete - Phase 3

# Commit the ROADMAP update
git add docs/roadmap/ROADMAP.md
git commit -m "docs(ROADMAP): Mark PRIORITY 25 Phase 3 complete"
git push origin roadmap
```

---

## Anti-Patterns to Avoid

❌ **Don't write vague commit messages**
```bash
# BAD: Vague message
git commit -m "fixes"  # ❌ What was fixed?
git commit -m "update stuff"  # ❌ What stuff?
git commit -m "WIP"  # ❌ Work in progress on what?
```
**Better**: Descriptive messages
```bash
git commit -m "fix(auth): Fix JWT token validation edge case"
git commit -m "feat(api): Add user profile endpoint"
git commit -m "docs(README): Update installation steps"
```

❌ **Don't commit multiple unrelated changes**
```bash
# BAD: Multiple changes in one commit
git add .
git commit -m "updates"  # Includes guideline changes AND typo fixes AND refactoring
```
**Better**: Separate logical commits
```bash
git add docs/guidelines/*.md
git commit -m "feat(guidelines): Add new guidelines"

git add coffee_maker/typos.txt
git commit -m "fix: Fix typo in error message"

git add coffee_maker/refactoring/
git commit -m "refactor: Simplify error handling"
```

❌ **Don't push without testing**
```bash
# BAD: Push untested code
git commit -m "feat: New feature"
git push origin  # ❌ Code not tested!
```
**Better**: Test before push
```bash
pytest  # Run tests
black .  # Format code
pre-commit run --all-files  # Run hooks
git commit -m "feat: New feature"
git push origin  # ✅ Tested and formatted
```

❌ **Don't use rebase on shared branches**
```bash
# BAD: Force push to shared branch
git rebase -i origin/main
git push --force origin main  # ❌ Breaks others' branches!
```
**Better**: Use rebase only on feature branches
```bash
git checkout feature-branch
git rebase -i origin/roadmap
git push --force origin feature-branch  # ✅ Only affects feature branch
```

❌ **Don't forget to reference tickets**
```bash
# BAD: No reference to PRIORITY
git commit -m "Create new guidelines"  # ❌ Which priority?
```
**Better**: Reference priority/issue
```bash
git commit -m "feat(PRIORITY 25): Create new guidelines

Implements Phase 3 of hierarchical spec architecture."
```

---

## Testing Approach

### Verify Commit History

```bash
# View recent commits
git log --oneline -10

# View detailed commit
git show abc123

# Verify commit message format
git log --format=%B | head -20
```

### Verify Tags

```bash
# List tags
git tag -l

# Verify tag points to correct commit
git show phase3-guidelines

# Verify semantic versioning
git tag -l 'v*' | sort -V
```

---

## Related Guidelines

- [GUIDELINE-004: Git Tagging Strategy](./GUIDELINE-004-git-tagging-strategy.md)
- [GUIDELINE-012: Hierarchical Spec Creation](./GUIDELINE-012-hierarchical-spec-creation.md)
- [GUIDELINE-013: Progressive Implementation](./GUIDELINE-013-progressive-implementation.md)

---

## Examples in Codebase

- Git history in roadmap branch
- Tags for phase completions
- ROADMAP.md status updates

---

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI Reference](https://cli.github.com/manual/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial git workflow guideline |
