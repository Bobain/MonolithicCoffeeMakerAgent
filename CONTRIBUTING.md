# Contributing to Coffee Maker Agent

Thank you for your interest in contributing to Coffee Maker Agent!

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Roadmap Updates (Special Case)](#roadmap-updates-special-case)
5. [Pull Request Process](#pull-request-process)
6. [Code Style](#code-style)
7. [Testing](#testing)
8. [Documentation](#documentation)

---

## Code of Conduct

This project follows standard open source practices. Please be respectful and professional in all interactions.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- Git
- Claude CLI (optional, for free usage) or Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Verify installation
project-manager --help
```

---

## Development Workflow

### Standard Feature Development

1. **Create a feature branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our [code style](#code-style)
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push and create PR**:
   ```bash
   git push -u origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

5. **Wait for review**: A maintainer will review your PR before merging.

---

## Roadmap Updates (Special Case)

**⚠️ IMPORTANT: This process is ONLY for updating ROADMAP.md and documentation**

### Why This Is Different

The `main` branch has protection rules requiring Pull Requests for all changes. However, when using the autonomous `project-manager` or `code_developer` agents to update the roadmap, we need a streamlined process to keep the roadmap current without manual PR approval overhead.

### When To Use This

✅ **ONLY use this automated merge process when**:
- Updating `docs/ROADMAP.md`
- Updating `docs/COLLABORATION_METHODOLOGY.md`
- Updating documentation files (`docs/*.md`)
- Changes made by `project-manager` agent
- Changes made by `code_developer` daemon

❌ **NEVER use this automated merge for**:
- Code changes (`coffee_maker/**/*.py`)
- Dependency changes (`pyproject.toml`)
- Configuration changes (`config.yaml`)
- CI/CD changes (`.github/**`)
- Any other non-documentation changes

### Automated Roadmap Update Process

We provide a Python script that uses the GitHub API to automatically create and merge PRs for roadmap updates.

#### Setup (One-time)

1. **Create a GitHub Personal Access Token**:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - Copy the token

2. **Set the token in your environment**:
   ```bash
   # Add to your .env file
   echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

   # Or export in your shell
   export GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Install PyGithub**:
   ```bash
   poetry add PyGithub
   ```

#### Using the Automated Script

```bash
# After making roadmap changes on a feature branch:
git checkout feature/roadmap-update
git add docs/ROADMAP.md docs/COLLABORATION_METHODOLOGY.md
git commit -m "docs: Update roadmap with latest priorities"
git push -u origin feature/roadmap-update

# Use the automated script to create and merge PR
python scripts/merge_roadmap_pr.py feature/roadmap-update
```

#### Manual Process (Alternative)

If the script fails or you prefer manual control:

```python
from github import Github
import os

# Initialize GitHub client
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo("Bobain/MonolithicCoffeeMakerAgent")

# Get the branch
branch_name = "feature/roadmap-update"
branch = repo.get_branch(branch_name)

# Create PR
pr = repo.create_pull(
    title="docs: Update roadmap and documentation",
    body="""
## Summary
Automated roadmap update via project-manager agent.

## Changes
- Updated ROADMAP.md with latest priorities
- Updated COLLABORATION_METHODOLOGY.md

🤖 Auto-generated roadmap update
    """,
    head=branch_name,
    base="main"
)

print(f"✅ PR created: {pr.html_url}")

# Merge PR (only if all checks pass)
if pr.mergeable:
    pr.merge(merge_method="squash")
    print(f"✅ PR merged: {pr.html_url}")
else:
    print(f"⚠️ PR not mergeable - manual review required: {pr.html_url}")
```

#### Using in project-manager Agent

The `project-manager` agent can use this workflow to keep the roadmap updated:

```python
# In coffee_maker/cli/roadmap_editor.py

def update_roadmap_on_main(self, commit_message: str):
    """Update roadmap and push to main via automated PR."""
    import subprocess
    from github import Github
    import os

    # Create feature branch
    branch_name = f"roadmap-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    subprocess.run(["git", "checkout", "-b", branch_name])

    # Commit changes
    subprocess.run(["git", "add", "docs/ROADMAP.md", "docs/COLLABORATION_METHODOLOGY.md"])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "-u", "origin", branch_name])

    # Create and merge PR via GitHub API
    g = Github(os.environ.get('GITHUB_TOKEN'))
    repo = g.get_repo("Bobain/MonolithicCoffeeMakerAgent")

    pr = repo.create_pull(
        title=commit_message,
        body=f"""
## Summary
Automated roadmap update via project-manager.

## Changes
{self.get_recent_changes()}

🤖 Auto-generated via project-manager agent
        """,
        head=branch_name,
        base="main"
    )

    # Auto-merge if mergeable
    if pr.mergeable:
        pr.merge(merge_method="squash")
        print(f"✅ Roadmap updated on main: {pr.html_url}")

        # Return to main and clean up
        subprocess.run(["git", "checkout", "main"])
        subprocess.run(["git", "pull", "origin", "main"])
        subprocess.run(["git", "branch", "-d", branch_name])

        return pr.html_url
    else:
        print(f"⚠️ Manual review required: {pr.html_url}")
        return None
```

### Safety Checks

The automated script includes these safety checks:

1. ✅ **Documentation-only**: Only merges if changes are in `docs/**`
2. ✅ **Main branch protection**: Respects GitHub branch protection rules
3. ✅ **Conflict detection**: Fails if PR has merge conflicts
4. ⚠️ **Manual review fallback**: If auto-merge fails, outputs PR URL for manual review

### Example Workflow

```bash
# 1. Agent makes roadmap changes
$ poetry run project-manager chat
You: Update roadmap with US-020 completion
Claude: ✅ Updated ROADMAP.md
        📝 Creating automated PR for main branch...
        ✅ PR created and merged: https://github.com/.../pull/123
        🎉 Roadmap is now up-to-date on main!

# 2. Main branch is automatically updated
$ git checkout main
$ git pull origin main
Already up to date.
```

---

## Pull Request Process

### For Regular Code Changes

1. **Ensure your PR**:
   - Has a clear title following [Conventional Commits](https://www.conventionalcommits.org/)
   - Includes a description of changes
   - References any related issues
   - Has passing tests
   - Updates relevant documentation

2. **PR Template**:
   ```markdown
   ## Summary
   Brief description of changes

   ## Changes
   - Change 1
   - Change 2

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Manual testing completed

   ## Documentation
   - [ ] README updated (if needed)
   - [ ] ROADMAP updated (if needed)
   - [ ] Docstrings added/updated
   ```

3. **Review Process**:
   - At least one approval required
   - All CI checks must pass
   - Maintainer will merge when ready

---

## Code Style

### Python

We use:
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking (where applicable)

```bash
# Format code
black coffee_maker/

# Run linters
flake8 coffee_maker/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix bug in X
docs: update README
chore: update dependencies
test: add tests for Y
refactor: refactor Z
```

---

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_roadmap_parser.py

# Run with coverage
poetry run pytest --cov=coffee_maker
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_roadmap_parser_handles_empty_file`

---

## Documentation

### Documentation Requirements

Every code change must include documentation updates:

1. **Code Documentation**:
   - Docstrings for all public functions/classes
   - Type hints for function parameters
   - Usage examples in docstrings

2. **User Documentation**:
   - Update `docs/ROADMAP.md` if adding features
   - Update `docs/QUICKSTART*.md` if changing user workflows
   - Update `docs/COLLABORATION_METHODOLOGY.md` if changing processes

3. **Inline Comments**:
   - Explain "why", not "what"
   - Document complex logic
   - Link to related issues/PRs

### Documentation Style

- Use clear, concise language
- Include examples
- Keep docs up-to-date with code changes
- Link related documents

---

## Questions?

- **Documentation**: Check `docs/` directory
- **Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Discussions**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

---

**Thank you for contributing!** 🎉
