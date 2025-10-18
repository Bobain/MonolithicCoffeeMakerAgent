---
description: Automate git workflows (commit, tag, PR) with conventional commits and semantic versioning
---

# Git Workflow Automation Skill

**Purpose**: Accelerate git operations (commit, tag, PR creation) by 5-8x through automation and convention

**Category**: code_developer acceleration
**Impact**: 10-15 min → 2-3 min per release cycle

---

## What This Skill Does

Automates three critical git workflows:

### 1. Conventional Commit Generation
- Analyzes git diff to categorize changes (feat/fix/refactor/docs/test)
- Generates conventional commit messages with auto-footer
- Creates consistent commit history for changelog generation

### 2. Semantic Versioning & Tagging
- Auto-calculates version bump (major.minor.patch)
- Creates tagged releases with detailed change summaries
- Supports multiple tag types (wip-*, dod-verified-*, stable-v*)

### 3. Pull Request Automation
- Generates PR descriptions from commits
- Auto-links related priorities/issues
- Creates PR body from template with section summaries

**Time Saved**: 10-15 min per release → 2-3 min (87% reduction)

---

## When To Use

### Scenario 1: code_developer Completes Feature

```bash
# After implementing PRIORITY 5 and tests pass
$ cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Step 1: Auto-generate conventional commit
$ python scripts/git_commit_generator.py --diff-since last-tag
✅ Generated commit message:
   feat(api): Add pagination to list endpoints (PRIORITY 5)

   - Implement offset/limit query parameters
   - Update API schemas and validation
   - Add integration tests

   Tests: 127 passing, 0 failing
   Closes: #45

# Step 2: Create semantic version tag
$ python scripts/semantic_tagger.py --version-auto
✅ Version bump: v1.2.3 → v1.3.0 (minor bump: new features)

# Step 3: Create PR with auto-generated summary
$ python scripts/pr_creator.py --auto --from roadmap --to main
✅ PR created: #123 - feat(api): Add pagination to list endpoints

Time total: 3-5 min (vs 10-15 min manual)
```

### Scenario 2: architect Finalizes Spec for Review

```bash
# After creating technical spec
$ python scripts/git_commit_generator.py --type docs --scope specs
✅ docs(specs): Add SPEC-070-Priority-5-API-Improvements

# Create WIP tag for internal tracking
$ python scripts/semantic_tagger.py --type wip --name us-070
✅ Tag created: wip-us-070

# Push changes
$ git push origin roadmap && git push origin wip-us-070
```

### Scenario 3: project_manager Marks Completion

```bash
# After DoD verification with Puppeteer
$ python scripts/semantic_tagger.py --type dod-verified --name us-070
✅ Tag created: dod-verified-us-070

# Auto-generates summary:
# - Tested spec creation workflow end-to-end
# - Confirmed user approval process works
# - Verified error handling scenarios
```

---

## Instructions

### Step 1: Analyze Git Diff

```bash
# Generate conventional commit from diff
python scripts/git_commit_generator.py \
    [--diff-since COMMIT] \
    [--diff-staged] \
    [--type feat|fix|refactor|docs|test|perf] \
    [--scope SCOPE]
```

**What it does**:
1. Parse git diff to identify changed files
2. Categorize changes by type (feat/fix/refactor/docs/test)
3. Extract scope from directory structure
4. Generate conventional commit message
5. Add co-author and tracking footer

**Example Output**:
```
feat(auth): Add JWT refresh token rotation

- Implement rotate_token() with expiration tracking
- Add refresh token blacklist cache
- Update tests (23 new, 0 modified)

Implements: US-062
Tests: 156 passing, 0 failing
Coverage: 87% (+3%)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Time**: 30-60s (vs 3-5 min manual)

### Step 2: Create Semantic Version Tag

```bash
# Auto-calculate version and create tag
python scripts/semantic_tagger.py \
    [--version-auto] \
    [--version MAJOR.MINOR.PATCH] \
    [--type wip|dod-verified|stable] \
    [--name PRIORITY_ID]
```

**Tag Types**:
- `wip-*`: Work in progress (implementation complete, tests passing)
- `dod-verified-*`: Definition of Done verified (Puppeteer testing passed)
- `stable-v*.*.*`: Production release (semantic version)

**Version Auto-Calculation**:
```
wip-us-070 commits since last stable?
├── feat commits → minor bump (v1.2.0 → v1.3.0)
├── fix commits → patch bump (v1.2.3 → v1.2.4)
└── refactor commits → no bump
```

**Example Output**:
```
✅ Version bump: v1.2.3 → v1.3.0

wip-us-070:
- Implementing JWT refresh token rotation
- All tests passing (156 tests)
- DoD awaiting verification

dod-verified-us-070:
- Puppeteer testing: All flows verified
- Integration: Complete
- Ready for release

stable-v1.3.0:
- Release: Multiple features completed
- Total commits: 12
- Tests: 189 passing
```

**Time**: 30-60s (vs 2-3 min manual calculation)

### Step 3: Create Pull Request

```bash
# Auto-generate PR with summary
python scripts/pr_creator.py \
    [--auto] \
    [--from BRANCH] \
    [--to TARGET_BRANCH] \
    [--title CUSTOM_TITLE] \
    [--template template-name]
```

**What it does**:
1. Analyze commits since merge base
2. Extract change summary from conventional commits
3. Link related priorities/issues
4. Generate PR body from template
5. Create PR via GitHub API

**Example PR Body**:
```
## Summary
- Implement JWT refresh token rotation (US-062)
- Add token expiration tracking
- Implement blacklist caching for revoked tokens

## Tests
- 156 tests passing (23 new)
- Code coverage: 87% (+3%)
- Integration: All scenarios verified

## Definition of Done
- [x] Technical spec approved
- [x] All tests passing
- [x] Code reviewed
- [x] Documentation updated
- [ ] Puppeteer verification (awaiting)

Related: #45, US-062, PRIORITY 5
```

**Time**: 1-2 min (vs 5-10 min manual)

---

## Scripts

### git_commit_generator.py

```bash
python scripts/git_commit_generator.py [OPTIONS]
```

**Purpose**: Generate conventional commit from git diff

**Options**:
- `--diff-since COMMIT`: Changes since commit (default: HEAD~1)
- `--diff-staged`: Only staged changes
- `--type feat|fix|...`: Override auto-detected type
- `--scope SCOPE`: Override auto-detected scope
- `--format json|text`: Output format

**Logic**:
1. Get diff (unstaged, staged, or since commit)
2. Analyze file paths and changes
3. Categorize by type (feat/fix/refactor/docs/test/perf/chore)
4. Extract scope from directory structure
5. Generate message with body and footer

**Output**: Conventional commit text ready for `git commit -m`

### semantic_tagger.py

```bash
python scripts/semantic_tagger.py [OPTIONS]
```

**Purpose**: Create semantic version tags with change summary

**Options**:
- `--version-auto`: Auto-calculate from commits since last tag
- `--version X.Y.Z`: Explicit version
- `--type wip|dod-verified|stable`: Tag type
- `--name PRIORITY_ID`: Tag name (e.g., us-070)
- `--message MESSAGE`: Custom tag message

**Logic**:
1. Get commits since last tag
2. Count feat/fix/refactor commits
3. Calculate version bump (semver)
4. Generate comprehensive tag message
5. Create annotated git tag

**Output**: Git tag with message

### pr_creator.py

```bash
python scripts/pr_creator.py [OPTIONS]
```

**Purpose**: Create GitHub PR with auto-generated summary

**Options**:
- `--auto`: Use defaults (from roadmap → to main)
- `--from BRANCH`: Source branch
- `--to TARGET_BRANCH`: Target branch
- `--title TITLE`: PR title (default: from commits)
- `--template TEMPLATE_NAME`: Body template

**Logic**:
1. Analyze commits roadmap → main
2. Extract conventional commit bodies
3. Identify issue/PR links
4. Generate PR body from template
5. Call `gh pr create`

**Output**: GitHub PR URL

---

## Integration with DeveloperStatus

Metrics tracked for **code_developer** performance:

```python
from coffee_maker.autonomous.developer_status import DeveloperStatus

status = DeveloperStatus.load()
status.track_git_operation("commit", 2.5)  # 2.5 min
status.track_git_operation("tag", 1.0)     # 1.0 min
status.track_git_operation("pr", 3.0)      # 3.0 min
status.save()
```

**Reporting**:
- Git operations per session
- Time per operation (measure automation benefit)
- PRs created per week
- Commit quality metrics

---

## Conventional Commits Reference

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| **feat** | New feature | `feat(auth): Add JWT refresh` |
| **fix** | Bug fix | `fix(api): Handle null params` |
| **refactor** | Code restructuring | `refactor(daemon): Split mixins` |
| **docs** | Documentation | `docs(specs): Add SPEC-070` |
| **test** | Test additions | `test(auth): Add JWT rotation tests` |
| **perf** | Performance optimization | `perf(cache): Add ROADMAP caching` |
| **chore** | Build/deps/config | `chore: Update dependencies` |

### Scope Examples

| Scope | Applies To |
|-------|-----------|
| **auth** | Authentication files |
| **api** | API routes and handlers |
| **daemon** | Daemon core |
| **specs** | Technical specifications |
| **tests** | Test infrastructure |
| **docs** | Documentation |

### Footer Keywords

```
Closes: #123                    # Close GitHub issue
Implements: US-062             # Link to user story
Relates-to: PRIORITY 5         # Link to priority
Depends-on: US-061             # Dependency tracking
Breaking-change: API v2        # Major version bump indicator
```

---

## Tag Naming Convention

### WIP Tags (Work in Progress)
```
wip-us-070                     # User story complete, tests passing
wip-priority-5                 # Priority complete
wip-feature-name               # Feature name
```

### DoD Tags (Definition of Done Verified)
```
dod-verified-us-070            # DoD verification complete
dod-verified-priority-5
```

### Release Tags (Production)
```
stable-v1.3.0                  # Semantic version
stable-v1.3.0-rc1             # Release candidate
stable-v1.3.0-hotfix          # Hotfix release
```

---

## Performance Metrics

| Operation | Manual | Automated | Savings |
|-----------|--------|-----------|---------|
| **Commit generation** | 3-5 min | 30-60s | 80-90% |
| **Version tagging** | 2-3 min | 30-60s | 75-80% |
| **PR creation** | 5-10 min | 1-2 min | 70-80% |
| **Per release cycle** | 10-15 min | 2-3 min | 80% |

**Example Session**:
```
Manual workflow (without skill):
1. Write conventional commit message (3-5 min)
2. Calculate semantic version (2-3 min)
3. Create PR with summary (5-10 min)
Total: 10-18 min

Automated workflow (with skill):
1. git_commit_generator.py (30-60s)
2. semantic_tagger.py (30-60s)
3. pr_creator.py (1-2 min)
Total: 2-4 min ✅ 75-80% faster
```

---

## Examples

### Example 1: Commit Feature Implementation

```bash
# Implement PRIORITY 5 (API pagination)
$ git diff --stat
 coffee_maker/api/routes.py      | 45 +++
 coffee_maker/api/schemas.py     | 28 ++
 coffee_maker/api/validation.py  | 32 ++
 tests/test_api_pagination.py    | 89 +++
 docs/API.md                     | 12 +

# Auto-generate conventional commit
$ python scripts/git_commit_generator.py --diff-since HEAD~1
✅ feat(api): Add pagination support to list endpoints

- Implement offset/limit query parameters
- Add comprehensive input validation
- Update OpenAPI schemas
- Add 28 integration tests

Implements: PRIORITY 5
Tests: 127 passing, 0 failing
Coverage: 87% (+3%)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>

# Use the message
$ git commit -m "feat(api): Add pagination support..."
```

### Example 2: Release with Semantic Versioning

```bash
# After completing week's work
$ git log --oneline wip-v1.2.3..HEAD
87a3c21 feat(auth): Add refresh token rotation
f2b8e34 fix(api): Handle concurrent requests
c9d4f12 refactor(daemon): Simplify status reporting
d8e5f23 test(auth): Add JWT edge cases

# Auto-calculate version (contains feat commits → minor bump)
$ python scripts/semantic_tagger.py --version-auto
✅ Version bump: v1.2.3 → v1.3.0

Creates tag:
- Version: v1.3.0
- Previous: v1.2.3 (3 weeks ago)
- Commits: 4 included
- Type: Stable release

# Push release
$ git push origin stable-v1.3.0
```

### Example 3: Create PR for Phase 0 Completion

```bash
# After implementing all Phase 0 skills
$ python scripts/pr_creator.py \
    --from roadmap \
    --to main \
    --title "feat: Complete Phase 0 - Force Multiplier Skills"

✅ PR created: #234

## Summary
- Implement 9 code analysis skills (US-090 through US-096)
- Create git workflow automation (US-065-067)
- Create refactoring coordinator (US-102)
- Migrate code-searcher to skills (complete)

## Impact
- code_developer velocity: +200-400% (3-5x faster)
- code analysis speed: 50-150x faster (10-30s → <200ms)
- architect productivity: +78% (117 min → 25 min per spec)
- Monthly time savings: 80-120 hours

## Tests
- 187 tests passing
- Code coverage: 89%
- All Phase 0 acceptance criteria met

## Definition of Done
- [x] All skills implemented
- [x] Skills documented
- [x] Integration tests passing
- [x] Performance validated
- [x] Code reviewed

Related: Phase 0 roadmap, US-090 through US-103

URL: https://github.com/bobain/MonolithicCoffeeMakerAgent/pull/234
```

---

## Troubleshooting

### Issue: Git Diff Includes Unwanted Files

**Solution**: Stage only the files you want committed
```bash
git add coffee_maker/api/  # Only add API files
git commit -m "$(python scripts/git_commit_generator.py --diff-staged)"
```

### Issue: Auto-Generated Commit Message Doesn't Match Intent

**Solution**: Override type or scope
```bash
python scripts/git_commit_generator.py \
    --type refactor \
    --scope daemon
```

### Issue: Version Bump Seems Wrong

**Solution**: Manually specify version
```bash
python scripts/semantic_tagger.py --version 2.0.0
```

### Issue: PR Not Created

**Solution**: Check GitHub CLI authentication
```bash
gh auth status
gh auth login  # Re-authenticate if needed
```

---

## Integration with Other Skills

### spec-creation-automation
- Uses commit messages to track spec creation effort
- Includes version history in effort estimates

### dod-verification
- Tracks DoD verification via `dod-verified-*` tags
- Metrics integrated with developer status

### test-failure-analysis
- Links test failures to commits
- Helps correlate bugs with code changes

---

## Maintenance

**Updating Conventional Commit Types**:
Edit `COMMIT_TYPES` in `git_commit_generator.py`

**Updating Version Calculation**:
Edit `calculate_version_bump()` in `semantic_tagger.py`

**Custom PR Templates**:
Add templates to `.claude/skills/git-workflow-automation/templates/`

---

## Limitations

**What This Skill CAN Do**:
- ✅ Generate conventional commits from diffs
- ✅ Auto-calculate semantic versions
- ✅ Create GitHub PRs via CLI
- ✅ Track git operations in DeveloperStatus

**What This Skill CANNOT Do**:
- ❌ Handle complex merge conflicts (requires human intervention)
- ❌ Rewrite git history (safety measure)
- ❌ Update remote repositories (safety measure, use manual git push)
- ❌ Enforce commit policies (that's pre-commit hooks)

---

## Related Documents

- `.claude/CLAUDE.md`: Git workflow rules (branch strategy, tagging)
- `GUIDELINE-004-git-tagging.md`: Tagging strategy and timeline
- `docs/REFACTORING_GUIDE.md`: Refactoring patterns and commit messages

---

**Created**: 2025-10-18
**Status**: Ready for Implementation
**Related USs**: US-065, US-066, US-067 (combined as single skill)
**ROI**: 80% time savings on git operations (10-15 min → 2-3 min per cycle)

