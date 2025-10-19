# Development Workflows

This document contains detailed workflows for common development tasks in the MonolithicCoffeeMakerAgent project.

---

## 1. Implementing a New Priority

```bash
# 1. Check ROADMAP
cat docs/roadmap/ROADMAP.md

# 2. Create technical spec (if needed)
# Daemon uses: .claude/commands/create-technical-spec.md

# 3. Implement feature
# Daemon uses: .claude/commands/implement-feature.md or implement-documentation.md

# 4. Test and commit
pytest
git add .
git commit -m "feat: Implement PRIORITY X"
```

---

## 2. Adding a New Prompt

```bash
# 1. Create prompt file
cat > .claude/commands/my-new-prompt.md << 'EOF'
Do something with $VARIABLE_NAME.

Instructions:
- Step 1
- Step 2

Context:
$CONTEXT
EOF

# 2. Add to PromptNames
# Edit: coffee_maker/autonomous/prompt_loader.py
class PromptNames:
    MY_NEW_PROMPT = "my-new-prompt"

# 3. Use in code
prompt = load_prompt(PromptNames.MY_NEW_PROMPT, {
    "VARIABLE_NAME": value,
    "CONTEXT": context
})

# 4. Later: Sync to Langfuse (Phase 2)
# coffee_maker prompts sync
```

---

## 3. Using Puppeteer MCP

```bash
# In Claude Desktop, use browser automation:
"Navigate to https://example.com and take a screenshot"

# Or in code (future):
# result = await puppeteer_client.navigate("https://example.com")
# screenshot = await puppeteer_client.screenshot()
```

---

## 4. Git Tagging Workflow

See [GUIDELINE-004](architecture/guidelines/GUIDELINE-004-git-tagging-workflow.md) for complete details.

**Quick Reference**:

```bash
# code_developer: After completing implementation
pytest  # Ensure all tests pass
git add .
git commit -m "feat: Implement US-047 - Architect-only spec creation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git tag -a wip-us-047 -m "US-047 implementation complete, awaiting DoD

Features:
- Architect-only spec creation
- User approval workflow
- Error handling improvements

Tests: All passing (23 tests)
Status: Awaiting DoD verification"
git push origin roadmap
git push origin wip-us-047

# project_manager: After DoD verification with Puppeteer
git tag -a dod-verified-us-047 -m "US-047 DoD verified with Puppeteer testing

Verification Steps:
- Tested spec creation workflow end-to-end ✅
- Confirmed user approval process works ✅
- Verified error handling scenarios ✅

DoD Status: All criteria met
Tested By: project_manager"
git push origin dod-verified-us-047

# project_manager: After multiple priorities complete
git tag -a stable-v1.3.0 -m "Release v1.3.0 - Architect Enablement

New Features:
- Architect-only spec creation (US-045, US-047) ✅
- User approval workflow (US-046) ✅
- Silent background agents (US-048) ✅

Tests: 156 passing, 0 failing
DoD: All priorities verified
Status: Production ready"
git push origin stable-v1.3.0
```

**Tag Types**:
- `wip-*`: code_developer marks implementation complete, tests passing
- `dod-verified-*`: project_manager marks DoD verified with Puppeteer
- `milestone-*`: Major features/epics complete
- `stable-v*.*.*`: Production-ready releases (semantic versioning)

---

## 5. Creating a POC for Complex Implementation

See [POC_CREATION_GUIDE.md](architecture/POC_CREATION_GUIDE.md) for complete details.

**When to use**: Complex features (>16 hours + High complexity) need validation before implementation

**Decision Matrix**:
- Effort >16h + Complexity HIGH → **POC REQUIRED**
- Effort >16h + Complexity MEDIUM → MAYBE (ask user)
- All other cases → No POC

**Quick Workflow**:

```bash
# architect evaluates user story
# Decision: Effort = 84 hours, Complexity = HIGH (multi-process, IPC)
# → POC REQUIRED

# 1. Create POC directory from template
cd docs/architecture/pocs/
cp -r POC-000-template/ POC-055-claude-skills-integration/
cd POC-055-claude-skills-integration/

# 2. Fill in README template
# - Update header (number, name, date, time budget: 20-30% of full = 17-25h)
# - List 3-5 concepts to prove
# - Define what's NOT in scope

# 3. Implement MINIMAL working code (20-30% scope)
# - Focus ONLY on proving core concepts
# - Skip error handling edge cases
# - Use print statements for logging (OK for POC)

# 4. Write basic tests
# - One test per concept
# - Just prove it works

# 5. Run and validate
python poc_component.py  # Should work!
python test_poc.py       # All tests pass!

# 6. Document learnings in README
# - What worked well
# - What needs adjustment
# - Recommendations for code_developer

# 7. Reference POC in technical spec
# Add to SPEC-055: "See POC-055 for proof-of-concept validation"

# 8. Commit to git
git add docs/architecture/pocs/POC-055-*/
git commit -m "feat: Add POC-055 - Claude Skills Integration

Proves Code Execution Tool integration, SkillLoader, ExecutionController work correctly.

Time: 4.5 hours (22% of 20-hour minimal scope)
Scope: 25% of SPEC-055

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 6. Architect CFR-011 Compliance (Daily Integration)

See [ARCHITECT_DAILY_ROUTINE_GUIDE.md](architecture/ARCHITECT_DAILY_ROUTINE_GUIDE.md) for complete details.

**CRITICAL**: architect CANNOT create technical specs until compliant with CFR-011:
- Daily: Read ALL code-searcher reports
- Weekly: Analyze codebase (max 7 days between analyses)

**Daily Workflow**:

```bash
# Run every day
poetry run architect daily-integration

# Output:
# 📋 Found 2 unread code-searcher report(s):
#
#   1. CODE_QUALITY_ANALYSIS_2025-10-17.md
#   2. SECURITY_AUDIT_2025-10-18.md
#
# 📖 Please read all reports now:
# [displays each report for review]
#
# Have you read this report and extracted action items? [y/N]: y
# ✅ Marked CODE_QUALITY_ANALYSIS_2025-10-17.md as read
#
# ✅ Daily integration complete!
```

**Weekly Workflow**:

```bash
# Run every 7 days max
poetry run architect analyze-codebase

# Output:
# 🔍 Starting weekly codebase analysis...
#
# 📊 Analyzing codebase for:
#   - Complexity metrics (radon --average)
#   - Large files (>500 LOC)
#   - Test coverage (pytest --cov)
#   - TODO/FIXME comments
#
# (This may take 5-10 minutes...)
#
# 📄 Report saved: docs/architecture/CODEBASE_ANALYSIS_2025-10-18.md
#
# ✅ Codebase analysis complete!
#    Next analysis due: 2025-10-25
```

**Check Compliance Status**:

```bash
poetry run architect cfr-011-status

# Output:
# 📋 CFR-011 Compliance Status
#
# ============================================================
# ✅ COMPLIANT - No violations detected
#
# Last code-searcher read: 2025-10-18
# Last codebase analysis: 2025-10-18
# Next analysis due: 2025-10-25
#
# Metrics:
#   Reports read: 12
#   Refactoring specs created: 4
#   Specs updated: 6
```

**What happens if not compliant?**

```python
# architect tries to create spec without compliance
# → CFR011ViolationError raised

CFR-011 violation detected! Cannot create spec until resolved:
  - Unread code-searcher reports: SECURITY_AUDIT_2025-10-18.md
  - Weekly codebase analysis overdue (last: 2025-10-10)

Actions required:
  1. Run: architect daily-integration
  2. Run: architect analyze-codebase
```

**Why CFR-011 matters**:
- **Quality loop**: code-searcher finds issues → architect reads → specs incorporate improvements → code_developer implements better code
- **Technical debt reduction**: Refactoring opportunities identified and acted upon
- **Continuous improvement**: Weekly codebase analysis catches issues early
- **Enforcement**: Spec creation BLOCKED until compliance restored

---

## 7. Dependency Management

See [SPEC-070](architecture/specs/SPEC-070-dependency-pre-approval-matrix.md) and [ADR-013](architecture/decisions/ADR-013-dependency-pre-approval-matrix.md) for complete details.

**Quick Check**:

```bash
# Check if package is pre-approved
poetry run project-manager check-dependency pytest-timeout
# → ✅ pytest-timeout is PRE-APPROVED (version: >=2.0,<3.0)
```

**In Code**:

```python
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

checker = DependencyChecker()
status = checker.get_approval_status("pytest-timeout")

if status == ApprovalStatus.PRE_APPROVED:
    # Auto-approve (2-5 min, NO user approval)
    subprocess.run(["poetry", "add", "pytest-timeout"])
    # Create minimal ADR (automated)

elif status == ApprovalStatus.NEEDS_REVIEW:
    # Delegate to architect for review (20-30 min)
    # architect uses dependency-conflict-resolver skill
    # User approval required

elif status == ApprovalStatus.BANNED:
    # Reject immediately with alternatives
    alternatives = checker.get_alternatives("pytest-timeout")
    print(f"Banned package. Use alternatives: {alternatives}")
```

---

## Quick Command Reference

```bash
# Start autonomous daemon
poetry run code-developer --auto-approve

# Check ROADMAP
poetry run project-manager /roadmap

# Developer status
poetry run project-manager developer-status

# View notifications
poetry run project-manager notifications

# Run tests
pytest

# Format code
black .

# Pre-commit hooks
pre-commit run --all-files
```
