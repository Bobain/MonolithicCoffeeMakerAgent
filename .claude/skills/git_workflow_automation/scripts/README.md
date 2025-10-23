# Git Workflow Automation Scripts

This directory contains standalone scripts for automating git workflows with conventional commits and semantic versioning.

## Scripts

### git_commit_generator.py

Generate conventional commit messages from git diffs.

**Usage:**
```bash
# Generate from unstaged changes
python git_commit_generator.py

# Generate from staged changes
python git_commit_generator.py --diff-staged

# Generate from changes since specific commit
python git_commit_generator.py --diff-since HEAD~3

# Override auto-detected type and scope
python git_commit_generator.py --type refactor --scope daemon

# Add priority reference
python git_commit_generator.py --priority US-067 --issue 123
```

**Output:** Conventional commit message ready for `git commit -m`

---

### semantic_tagger.py

Create semantic version tags with automatic version calculation.

**Usage:**
```bash
# Auto-calculate version from commits
python semantic_tagger.py --version-auto

# Explicit version
python semantic_tagger.py --version 1.3.0

# Create WIP tag
python semantic_tagger.py --type wip --name us-067

# Create DoD verified tag
python semantic_tagger.py --type dod-verified --name us-067

# Push tag to remote
python semantic_tagger.py --type wip --name us-067 --push
```

**Output:** Git tag created with message

---

### pr_creator.py

Create GitHub PRs with auto-generated descriptions from commits.

**Usage:**
```bash
# Auto mode (roadmap → main)
python pr_creator.py --auto

# Custom branches
python pr_creator.py --from feature-branch --to main

# With custom title
python pr_creator.py --from roadmap --to main \
    --title "feat: Complete Phase 0 Skills"

# Create draft PR
python pr_creator.py --auto --draft
```

**Output:** GitHub PR URL

---

## Requirements

- Git repository
- Python 3.8+
- GitHub CLI (`gh`) for PR creation
- Git configured with user name and email

## Installation

No installation required. Scripts use only Python standard library and git/gh commands.

## Examples

### Complete Workflow Example

```bash
# 1. Stage your changes
git add coffee_maker/skills/git_workflow_automation/

# 2. Generate commit message
python .claude/skills/git-workflow-automation/scripts/git_commit_generator.py \
    --diff-staged \
    --priority US-067 > /tmp/commit_msg.txt

# 3. Review and commit
cat /tmp/commit_msg.txt
git commit -F /tmp/commit_msg.txt

# 4. Create WIP tag
python .claude/skills/git-workflow-automation/scripts/semantic_tagger.py \
    --type wip --name us-067 --push

# 5. Create PR when ready
python .claude/skills/git-workflow-automation/scripts/pr_creator.py --auto
```

### Quick Commit

```bash
# One-liner for quick commits
git commit -m "$(python .claude/skills/git-workflow-automation/scripts/git_commit_generator.py --diff-staged --priority US-067)"
```

---

## Integration with code_developer

These scripts are designed to be used by the `code_developer` agent for autonomous git workflows.

**See:** `.claude/skills/git-workflow-automation/SKILL.md` for full documentation.

---

**Created:** 2025-10-19
**Status:** Production Ready
