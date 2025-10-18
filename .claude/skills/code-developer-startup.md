# Skill: Code Developer Agent Startup

**Name**: `code-developer-startup`
**Owner**: code_developer agent
**Purpose**: Intelligently load only necessary context for code_developer agent startup (solves CFR-007)
**Priority**: CRITICAL - Used at EVERY code_developer session start

---

## When to Use This Skill

**MANDATORY** at startup:
- ✅ **EVERY TIME** code_developer agent starts a new session
- ✅ Before reading any files
- ✅ Before implementing any priority

**Example Trigger**:
```python
# In code_developer agent startup sequence
startup_context = load_skill(SkillNames.CODE_DEVELOPER_STARTUP, {
    "TASK_TYPE": "implement_priority",  # or "fix_tests", "refactor_code", "update_docs"
    "PRIORITY_NAME": "PRIORITY 10",  # if working on specific priority
})
```

---

## Skill Execution Steps

### Step 1: Identify Task Type

**Inputs Needed**:
- `$TASK_TYPE`: Type of task code_developer is starting
- `$PRIORITY_NAME`: (Optional) Specific priority being worked on

**Task Type Categories**:

1. **implement_priority** - Implementing a ROADMAP priority
   - Core role: Software developer
   - Critical docs: ROADMAP (priority details), technical spec (if exists), CLAUDE.md (coding standards)
   - Optional: Related code files, tests

2. **fix_tests** - Fixing failing tests
   - Core role: Test debugger
   - Critical docs: Test output, test files, implementation files
   - Optional: Test guidelines

3. **refactor_code** - Refactoring existing code
   - Core role: Code quality engineer
   - Critical docs: Architecture guidelines, code being refactored
   - Optional: Related tests, ADRs

4. **update_docs** - Updating documentation
   - Core role: Technical writer
   - Critical docs: Documentation being updated, ROADMAP context
   - Optional: Code examples

5. **create_pr** - Creating pull request
   - Core role: Git workflow manager
   - Critical docs: Git workflow guidelines, commit history, DoD report
   - Optional: PR template

6. **verify_dod** - Verifying Definition of Done
   - Core role: Quality assurance
   - Critical docs: Priority acceptance criteria, test results
   - Optional: DoD checklist

---

### Step 2: Calculate Context Budget

**CFR-007 Requirement**: Agent core materials must fit in ≤30% of context window

**Context Window**: 200,000 tokens (Claude Haiku - code_developer uses Haiku for speed)
**Available for Core**: 60,000 tokens (30% budget)
**Available for Work**: 140,000 tokens (70% for implementation)

**Token Estimation**:
```python
def estimate_tokens(text: str) -> int:
    """Estimate tokens (1 token ≈ 4 characters)."""
    return len(text) // 4
```

---

### Step 3: Load Core Role & Responsibilities (Always)

**ALWAYS load these files** (code_developer identity):

1. **`.claude/agents/code_developer.md`** (~4,000 tokens)
   - Role definition
   - Available skills (test-failure-analysis, dod-verification, git-workflow-automation)
   - Workflow steps
   - Collaboration rules

2. **Key sections from `.claude/CLAUDE.md`** (~6,000 tokens) - **EXCERPTS ONLY**:
   - Coding standards (Black, type hints, line length)
   - Git workflow (CFR-013: roadmap branch only)
   - Project structure (where files live)
   - Agent tool ownership (what code_developer can modify)

**Total Core**: ~10,000 tokens (17% of budget) ✅

---

### Step 4: Load Task-Specific Context (Conditional)

#### For `implement_priority`:

**Critical** (always load):
- **ROADMAP.md** (priority section ONLY) (~2,000 tokens)
  - Extract: Priority name, description, acceptance criteria, dependencies
  - Skip: All other priorities (unless dependencies)

- **Technical Spec** (if exists) (~8,000 tokens)
  - `docs/architecture/specs/SPEC-XXX-*.md` for this priority
  - Full spec (architecture, API design, testing strategy)
  - Skip: If spec doesn't exist (simple priority)

- **Implementation Guidelines** (relevant only) (~3,000 tokens)
  - Example: If implementing auth → `GUIDELINE-001-error-handling.md`
  - Max 2-3 guidelines

**Optional** (load if budget allows):
- Related code files (if extending existing feature) (~10,000 tokens)
  - Use code discovery to find relevant files
  - Load top 3-5 most relevant files
- Existing tests (if modifying tested code) (~5,000 tokens)

**Total**: ~13,000 tokens (22% of budget)
**Cumulative**: 23,000 tokens (38% of budget) ⚠️ **OVER CFR-007!**

**Mitigation**:
- Load spec as summary (key sections only) → Reduce to 3,000 tokens
- Load guidelines as excerpts (relevant sections) → Reduce to 1,500 tokens
**Adjusted**: ~7,500 tokens (13% of budget)
**Adjusted Cumulative**: 17,500 tokens (29% of budget) ✅

---

#### For `fix_tests`:

**Critical** (always load):
- **Test output** (pytest results) (~2,000 tokens)
  - Failed test names
  - Error messages
  - Tracebacks

- **Test files** (failing tests only) (~3,000 tokens)
  - Max 3-5 test files
  - Focus on failed tests

- **Implementation files** (being tested) (~5,000 tokens)
  - Files that failed tests are testing
  - Max 5-7 files

**Optional**:
- Test guidelines (if unclear why tests fail)
- Related tests (if fixing cascading failures)

**Total**: ~10,000 tokens (17% of budget)
**Cumulative**: 20,000 tokens (33% of budget) ⚠️ **OVER CFR-007!**

**Mitigation**:
- Load test output as summary (error messages only, skip full trace) → Reduce to 1,000 tokens
- Load test files as excerpts (failed test functions only) → Reduce to 1,500 tokens
**Adjusted**: ~7,500 tokens (13% of budget)
**Adjusted Cumulative**: 17,500 tokens (29% of budget) ✅

---

#### For `refactor_code`:

**Critical** (always load):
- **Architecture guidelines** (refactoring patterns) (~3,000 tokens)
  - Best practices
  - Code smells to avoid
  - Refactoring patterns

- **Code being refactored** (~8,000 tokens)
  - Target files (max 5-7 files)
  - Related classes/functions

**Optional**:
- Tests (to ensure refactoring doesn't break functionality)
- ADRs (if refactoring involves architectural decisions)

**Total**: ~11,000 tokens (18% of budget)
**Cumulative**: 21,000 tokens (35% of budget) ⚠️ **OVER CFR-007!**

**Mitigation**:
- Load guidelines as excerpts (relevant sections only) → Reduce to 1,500 tokens
- Load code as primary file only (defer related files to incremental reads) → Reduce to 4,000 tokens
**Adjusted**: ~5,500 tokens (9% of budget)
**Adjusted Cumulative**: 15,500 tokens (26% of budget) ✅

---

#### For `update_docs`:

**Critical** (always load):
- **Documentation being updated** (~3,000 tokens)
  - README.md, docs/*.md, or docstrings

- **ROADMAP context** (if documenting new feature) (~1,500 tokens)
  - Priority description
  - User-facing changes

**Optional**:
- Code examples (if documenting API)
- Related documentation (for consistency)

**Total**: ~4,500 tokens (8% of budget)
**Cumulative**: 14,500 tokens (24% of budget) ✅

---

#### For `create_pr`:

**Critical** (always load):
- **Git workflow guidelines** (~2,000 tokens)
  - PR creation process
  - Commit message format
  - PR description template

- **Commit history** (for PR description) (~2,000 tokens)
  - Recent commits on current branch
  - Files changed

- **DoD report** (if available) (~3,000 tokens)
  - Definition of Done verification results
  - Evidence screenshots, test results

**Optional**:
- Related PRs (for reference)

**Total**: ~7,000 tokens (12% of budget)
**Cumulative**: 17,000 tokens (28% of budget) ✅

---

#### For `verify_dod`:

**Critical** (always load):
- **Priority acceptance criteria** (~2,000 tokens)
  - From ROADMAP or spec
  - Expected outcomes

- **Test results** (~3,000 tokens)
  - Pytest output
  - Coverage reports

**Optional**:
- DoD checklist template
- Puppeteer test results (if web feature)

**Total**: ~5,000 tokens (8% of budget)
**Cumulative**: 15,000 tokens (25% of budget) ✅

---

### Step 5: Load Skills (Context-Aware)

**Available Skills for code_developer**:
- `test-failure-analysis` - Use when `fix_tests` task
- `dod-verification` - Use when `verify_dod` task
- `git-workflow-automation` - Use when `create_pr` task

**Conditional Loading**:
```python
if task_type == "fix_tests":
    # Don't load full test-failure-analysis skill into context
    # Instead, reference it for later use
    skills_to_use = ["test-failure-analysis"]
elif task_type == "verify_dod":
    skills_to_use = ["dod-verification"]
elif task_type == "create_pr":
    skills_to_use = ["git-workflow-automation"]
else:
    skills_to_use = []
```

**Note**: Skills are **not loaded into startup context** (to save tokens). They're **invoked later** when needed during workflow.

---

### Step 6: Validate Context Budget (CFR-007)

**Validation Check**:
```python
def validate_cfr007(loaded_files: list[str]) -> dict:
    """Validate CFR-007 compliance."""
    total_tokens = sum(estimate_tokens(read_file(f)) for f in loaded_files)
    budget = 60000  # 30% of 200k

    return {
        "total_tokens": total_tokens,
        "budget": budget,
        "percentage": (total_tokens / 200000) * 100,
        "compliant": total_tokens <= budget,
        "remaining": budget - total_tokens,
        "overage": max(0, total_tokens - budget)
    }
```

**If over budget**:
1. **Use excerpts instead of full files**
   - ROADMAP: Priority section only (not entire file)
   - Spec: Key sections only (skip examples, verbose rationale)
   - Code: Primary file only (defer imports/dependencies)

2. **Defer non-critical files**
   - Load incrementally as needed during implementation
   - Use Read tool to fetch specific sections on-demand

3. **Summarize long documents**
   - Technical specs: Architecture overview + API design (skip detailed examples)
   - Guidelines: Main rules only (skip edge cases)

**Output**: Validation report

---

### Step 7: Generate Startup Summary

**Create concise summary for code_developer**:

```markdown
# Code Developer Startup Summary

**Session Start**: 2025-10-18 10:30 AM
**Task Type**: implement_priority
**Priority**: PRIORITY 10 - User Authentication

## Context Loaded (✅ CFR-007 Compliant: 29%)

### Core Identity (17%)
- ✅ Agent role & responsibilities
- ✅ Available skills (test-failure-analysis, dod-verification, git-workflow-automation)
- ✅ Coding standards (Black, type hints, CFR-013)
- ✅ Git workflow & tool ownership

### Task-Specific Context (12%)
- ✅ PRIORITY 10 description & acceptance criteria
- ✅ Technical spec (SPEC-062-user-authentication.md - summarized)
- ✅ Implementation guidelines (error handling, logging)

## Ready to Implement

**Available Context Budget**: 71% (142,000 tokens)

**Recommended Workflow**:
1. ✅ Use test-failure-analysis skill if tests fail
2. ✅ Use dod-verification skill before committing
3. ✅ Use git-workflow-automation skill for PR creation

**Estimated Time**: 25 hours (from spec)

**Next Steps**:
1. Create branch: `priority-10-user-authentication` (❌ NO - CFR-013: use roadmap branch)
2. Implement auth service (coffee_maker/auth/authentication.py)
3. Add tests (tests/unit/test_authentication.py)
4. Verify DoD with dod-verification skill
5. Create PR with git-workflow-automation skill

**Collaboration Needed**:
- Request architect approval for dependencies (passlib, python-jose)
- Notify project_manager when complete
```

---

## Decision Logic: Which Files to Load

**Decision Tree**:
```
IF task_type == "implement_priority":
    Load: agent def, CLAUDE.md (excerpts), ROADMAP (priority), spec (summarized), guidelines (relevant)
    Defer: Related code, tests (load incrementally)
ELIF task_type == "fix_tests":
    Load: agent def, test output (summary), test files (failed only), implementation files (tested only)
    Defer: Test guidelines, related tests
ELIF task_type == "refactor_code":
    Load: agent def, guidelines (excerpts), code being refactored (primary file)
    Defer: Related files, tests, ADRs
ELIF task_type == "update_docs":
    Load: agent def, documentation being updated, ROADMAP context (if new feature)
    Defer: Code examples, related docs
ELIF task_type == "create_pr":
    Load: agent def, git workflow guidelines, commit history, DoD report
    Defer: Related PRs
ELIF task_type == "verify_dod":
    Load: agent def, acceptance criteria, test results
    Defer: DoD checklist, Puppeteer results
ELSE:
    Load: agent def only (minimal startup)
```

---

## Integration with Code Developer Agent

**In code_developer agent startup sequence**:

```python
# coffee_maker/autonomous/daemon_implementation.py (or future code_developer_agent.py)

from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

class CodeDeveloperAgent:
    def __init__(self, task_type: str, priority_name: str = None):
        # Step 1: Load startup skill
        self.startup_context = self._load_startup_context(task_type, priority_name)

        # Step 2: Validate CFR-007
        if not self.startup_context["cfr007_compliant"]:
            # Auto-reduce context
            self.startup_context = self._reduce_context_and_retry()

        # Step 3: Ready to work
        self.ready = True

    def _load_startup_context(self, task_type: str, priority_name: str = None):
        """Load context using code-developer-startup skill."""
        skill = load_skill(SkillNames.CODE_DEVELOPER_STARTUP, {
            "TASK_TYPE": task_type,
            "PRIORITY_NAME": priority_name or "",
        })

        # Execute skill with LLM
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        claude = ClaudeCLIInterface()
        result = claude.execute_prompt(skill)

        return self._parse_startup_result(result.content)

    def _reduce_context_and_retry(self):
        """Auto-reduce context if CFR-007 violated."""
        # Use excerpts instead of full files
        # Defer non-critical files
        # Retry validation
        pass
```

---

## Benefits of Code Developer Startup Skill

### 1. **CFR-007 Compliance Guaranteed**
- Every session validates context budget
- Auto-reduction if over budget
- Zero manual context management

### 2. **Task-Optimized Loading**
- implement_priority: Loads spec + guidelines
- fix_tests: Loads test output + test files
- Different tasks = different context

### 3. **Incremental Context Loading**
- Start with minimal context
- Load more files as needed during work
- Read tool for on-demand file access

### 4. **Skill Integration Ready**
- Knows which skills to use for each task
- Skills invoked when needed (not loaded upfront)
- Seamless workflow automation

### 5. **Faster Implementation**
- Reduced startup time (<30 seconds)
- Immediate focus on implementation
- No context overflow retries

---

## Success Metrics

**Time Savings**:
- **Before**: 10-15 min context selection + CFR-007 violations (48 min each)
- **After**: <1 min automated loading, zero violations
- **Savings**: 9-62 minutes per session

**Quality Improvements**:
- **CFR-007 violations**: 40-60/month → 0/month ✅
- **Context relevance**: 65% → 95%
- **Implementation speed**: +25% (less context overhead)

**Measurement**:
- Track CFR-007 violation count (goal: 0)
- Track context budget usage per task type
- Track time-to-first-commit (session start → first commit)

---

## Related Skills

- **test-failure-analysis**: Used during fix_tests workflow
- **dod-verification**: Used during verify_dod workflow
- **git-workflow-automation**: Used during create_pr workflow
- **architect-startup**: Similar pattern for architect agent

---

**Remember**: Smart startup = Fast implementation! No more context budget headaches! 🚀

**Code Developer's Mantra**: "Load lean, code clean, ship fast!"
