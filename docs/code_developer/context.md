# Quick Context Reference for code_developer

**Purpose**: Fast startup, maximize efficiency, reduce context-loading time

---

## Essential File Paths

### Must Read on Every Startup
1. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/ROADMAP.md`**
   - My task list (first 200 lines show priorities)
   - Find next "📝 Planned" priority

2. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/CLAUDE.md`**
   - Project instructions and coding standards
   - Agent boundaries and tool ownership

3. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/code_developer/current_progress.md`**
   - What I was working on last session

### Read As Needed
4. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/PRIORITY_X_TECHNICAL_SPEC.md`**
   - Technical specs for complex priorities (>1 day)

5. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/commands/`**
   - Centralized prompts (load via PromptLoader)

6. **`/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/data/developer_status.json`**
   - Current daemon status

---

## Common Patterns

### Startup Checklist
```
[ ] Read docs/ROADMAP.md (first 200 lines)
[ ] Read docs/code_developer/current_progress.md
[ ] Check git status and current branch
[ ] Identify next priority or continue current work
[ ] Load technical spec if needed
[ ] Begin implementation
```

### Implementation Pattern
```python
# 1. Load prompt from centralized store
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {
    "PRIORITY_NAME": "US-015",
    "TECHNICAL_SPEC": spec_content
})

# 2. Follow coding standards
# - Black formatting (88 chars)
# - Type hints
# - Pytest tests
# - Comprehensive docstrings

# 3. Update status
from coffee_maker.autonomous.developer_status import DeveloperStatus
status = DeveloperStatus()
status.start_task("US-015", "Implementing metrics tracking")
```

### Git Pattern
```bash
# 1. Create feature branch (if not exists)
git checkout -b feature/us-015-metrics-tracking

# 2. Implement changes
# ... code here ...

# 3. Run tests
pytest tests/

# 4. Format code
black .

# 5. Commit with standard message
git add .
git commit -m "feat: US-015 Phase X - Description

Implemented:
- Feature 1
- Feature 2

Tests:
- Added test_feature_1
- Added test_feature_2

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push branch
git push -u origin feature/us-015-metrics-tracking

# 7. Create PR
gh pr create --title "US-015: Estimation Metrics & Velocity Tracking" --body "$(cat <<'EOF'
## Summary
- Implemented MetricsDB for tracking estimations
- Added velocity and accuracy calculations
- Created /metrics CLI command

## Test Plan
- [x] pytest tests/ passes
- [x] MetricsDB stores and retrieves data
- [x] CLI commands work correctly

🤖 Generated with Claude Code
EOF
)"
```

---

## Frequently Modified Files

### Core Implementation
- `coffee_maker/autonomous/daemon.py` - Main daemon orchestrator
- `coffee_maker/cli/` - CLI commands
- `coffee_maker/storage/` - Database classes
- `coffee_maker/llm/` - AI provider integrations

### Testing
- `tests/unit/` - Unit tests
- `tests/ci_tests/` - Integration tests

### Status Tracking
- `data/developer_status.json` - Daemon status (auto-updated)
- `docs/ROADMAP.md` - Status field only (read-mostly)

---

## Coding Standards Quick Reference

### Python Style
```python
# Type hints
def process_data(input_data: dict[str, Any]) -> list[str]:
    """Process input data and return results.

    Args:
        input_data: Dictionary containing input parameters

    Returns:
        List of processed result strings

    Raises:
        ValueError: If input_data is invalid
    """
    pass

# Imports (autoflake removes unused)
from typing import Any
import json

# Black formatting (88 chars default)
# Pre-commit hooks enforce this automatically
```

### Error Handling
```python
# Use specific exceptions from coffee_maker.exceptions
from coffee_maker.exceptions import (
    CoffeeMakerError,
    ConfigurationError,
    StorageError
)

try:
    result = risky_operation()
except ConfigurationError as e:
    logger.error(f"Configuration issue: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise CoffeeMakerError(f"Operation failed: {e}")
```

### Configuration Access
```python
# Use ConfigManager (centralized)
from coffee_maker.config.manager import ConfigManager

config = ConfigManager()
api_key = config.get_anthropic_api_key(required=True)

# Don't use os.getenv() directly (old pattern)
```

---

## Tool Boundaries

### What I Own (Write Access)
- All code in `coffee_maker/`
- All tests in `tests/`
- Scripts in `scripts/`
- `pyproject.toml`
- My docs in `docs/code_developer/`
- Git branches, commits, PRs
- ROADMAP status updates (Planned → In Progress → Complete)

### What I Don't Own (Read-Only)
- Strategic docs in `docs/` (project_manager creates/updates)
- Technical specs `docs/PRIORITY_*_TECHNICAL_SPEC.md` (project_manager)
- Agent definitions `.claude/agents/` (project_manager)
- Centralized prompts `.claude/commands/` (project_manager)
- Strategic ROADMAP decisions (project_manager)

### When to Delegate
```
"Where is X implemented?" → code-searcher (deep analysis)
"Monitor PR status" → project_manager (GitHub monitoring)
"Design a UI" → ux-design-expert (design decisions)
"Create technical spec" → project_manager (documentation)
```

---

## Common Commands

```bash
# Find planned priorities
grep "📝 Planned" docs/ROADMAP.md | head -10

# Check current status
cat data/developer_status.json

# Run specific test
pytest tests/unit/test_metrics.py -v

# Search for function
grep -r "def function_name" coffee_maker/

# Find all TODOs
grep -r "TODO" coffee_maker/ tests/

# Check recent commits
git log --oneline -10

# Check branch status
git status
git diff --stat

# Format all code
black coffee_maker/ tests/ scripts/

# Run pre-commit hooks
pre-commit run --all-files
```

---

## Decision Trees

### Should I Create a Technical Spec?
```
Is priority >1 day effort?
├─ Yes → Check if docs/PRIORITY_X_TECHNICAL_SPEC.md exists
│   ├─ Exists → Read it and implement
│   └─ Missing → Request project_manager to create it first
└─ No → Implement directly
```

### Should I Verify DoD with Puppeteer?
```
Is this a web feature?
├─ Yes → Use Puppeteer MCP during implementation
│   ├─ Navigate to app
│   ├─ Test acceptance criteria
│   ├─ Take screenshots for evidence
│   └─ Check console errors
└─ No → Use pytest for verification
```

### Should I Create a PR?
```
Is implementation complete?
├─ Yes → All phases done?
│   ├─ Yes → Tests passing?
│   │   ├─ Yes → Create PR autonomously
│   │   └─ No → Fix tests first
│   └─ No → Continue implementation
└─ No → Keep working
```

---

## Performance Tips

### Minimize Context Loading
- Read ROADMAP first 200 lines (enough for priorities)
- Read current_progress.md to pick up where I left off
- Only read technical specs when implementing that priority
- Use grep to find specific content instead of reading full files

### Efficient Searching
```bash
# Fast: Use Grep tool with pattern
Grep: pattern="class MetricsDB" path="coffee_maker/"

# Fast: Use Glob for file patterns
Glob: pattern="**/*metrics*.py"

# Avoid: Using bash grep/find (slower, less efficient)
```

### Parallel Operations
- Read multiple files in parallel when starting
- Run independent git commands together
- Check multiple test files simultaneously

---

## Emergency Procedures

### If Tests Fail
1. Read test output carefully
2. Fix failing tests first (don't commit broken code)
3. Run tests again to verify
4. If persistent failure, create notification for user

### If Git Conflicts
1. Check git status
2. Try git pull --rebase origin main
3. Resolve conflicts if simple
4. If complex, create notification for user

### If Daemon Crashes
1. Check data/developer_status.json for last state
2. Review recent commits for issues
3. Check BUG-001/BUG-002 fixes still in place
4. Create notification if can't self-recover

---

## Success Metrics

**Track in current_progress.md**:
- Priorities completed per day
- Test pass rate
- Time from start to PR creation
- Number of autonomous sessions without human intervention

**Goals**:
- 1+ priority per day average
- 100% test pass rate before commit
- <8 hours from start to PR for standard features
- 5+ autonomous sessions in a row

---

**Last Updated**: 2025-10-14
**Version**: 1.0
