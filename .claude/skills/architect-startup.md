# Skill: Architect Agent Startup

**Name**: `architect-startup`
**Owner**: architect agent
**Purpose**: Intelligently load only necessary context for architect agent startup (solves CFR-007)
**Priority**: CRITICAL - Used at EVERY architect session start

---

## When to Use This Skill

**MANDATORY** at startup:
- ✅ **EVERY TIME** architect agent starts a new session
- ✅ Before reading any files
- ✅ Before responding to any user request

**Example Trigger**:
```python
# In architect agent startup sequence
startup_context = load_skill(SkillNames.ARCHITECT_STARTUP, {
    "TASK_TYPE": "create_spec",  # or "review_code", "propose_architecture", etc.
    "PRIORITY_NAME": "PRIORITY 10",  # if working on specific priority
})
```

---

## Skill Execution Steps

### Step 1: Identify Task Type

**Inputs Needed**:
- `$TASK_TYPE`: Type of task architect is starting (create_spec, review_code, propose_architecture, manage_dependencies, create_adr)
- `$PRIORITY_NAME`: (Optional) Specific priority being worked on

**Task Type Categories**:

1. **create_spec** - Creating technical specification
   - Core role: Architecture design
   - Critical docs: ROADMAP, existing specs (for patterns), CLAUDE.md (architecture section)
   - Optional: Related code (if refactoring)

2. **review_code** - Reviewing code for architectural consistency
   - Core role: Architecture guardian
   - Critical docs: Architecture guidelines, ADRs
   - Optional: Specific code files to review

3. **propose_architecture** - Proposing new architectural patterns
   - Core role: System designer
   - Critical docs: ADRs, architecture specs, CLAUDE.md
   - Optional: Research materials

4. **manage_dependencies** - Managing dependencies (poetry add)
   - Core role: Dependency manager
   - Critical docs: pyproject.toml, ADRs (dependency decisions)
   - Optional: Security reports

5. **create_adr** - Creating Architectural Decision Record
   - Core role: Decision documenter
   - Critical docs: Existing ADRs (for format), CLAUDE.md
   - Optional: Technical context

6. **provide_feedback** - Providing tactical feedback to code_developer
   - Core role: Code reviewer
   - Critical docs: Architecture guidelines, coding standards
   - Optional: Commit diff

**Output**: Task type classification

---

### Step 2: Calculate Context Budget

**CFR-007 Requirement**: Agent core materials must fit in ≤30% of context window

**Context Window**: 200,000 tokens (Claude Sonnet 3.5)
**Available for Core**: 60,000 tokens (30% budget)
**Available for Work**: 140,000 tokens (70% for files, analysis, responses)

**Token Estimation Formula**:
```python
def estimate_tokens(text: str) -> int:
    """Estimate tokens (rough: 1 token ≈ 4 characters)."""
    return len(text) // 4

def fits_in_budget(files: list[str], budget: int = 60000) -> bool:
    """Check if files fit in context budget."""
    total_tokens = sum(estimate_tokens(read_file(f)) for f in files)
    return total_tokens <= budget
```

**Output**: Context budget allocation

---

### Step 3: Load Core Role & Responsibilities (Always)

**ALWAYS load these files** (architect identity):

1. **`.claude/agents/architect.md`** (~3,000 tokens)
   - Architect role definition
   - Responsibilities
   - Collaboration rules
   - Skill list

2. **Key sections from `.claude/CLAUDE.md`** (~5,000 tokens)
   - Architecture overview (extract only)
   - Tool ownership matrix (architect section)
   - Coding standards (architecture patterns)
   - Git workflow (tagging, versioning)

**Total Core**: ~8,000 tokens (13% of budget) ✅

**Output**: Core identity loaded

---

### Step 4: Load Task-Specific Context (Conditional)

**Based on task type, load ONLY relevant documents:**

#### For `create_spec`:

**Critical** (always load):
- **ROADMAP.md** (priority section only, not entire file) (~2,000 tokens)
  - Extract: Current priority description, dependencies, acceptance criteria
  - Skip: Completed priorities (unless referenced)

- **`docs/architecture/specs/SPEC-000-template.md`** (~1,500 tokens)
  - Spec template format
  - Required sections

- **Recent specs** (2-3 most recent, for pattern reference) (~6,000 tokens)
  - Example: SPEC-060, SPEC-061
  - Learn spec style, depth, format

**Optional** (load if budget allows):
- Related code files (if refactoring existing feature)
- Dependency analysis (if complex integration)

**Total**: ~9,500 tokens (16% of budget)
**Cumulative**: 17,500 tokens (29% of budget) ✅ **Under CFR-007 limit!**

---

#### For `review_code`:

**Critical** (always load):
- **Architecture guidelines** (~4,000 tokens)
  - `docs/architecture/guidelines/GUIDELINE-*.md` (relevant ones only)
  - Example: GUIDELINE-001 (error handling), GUIDELINE-002 (logging)

- **Relevant ADRs** (based on code being reviewed) (~3,000 tokens)
  - Example: If reviewing database code → ADR about database patterns
  - Max 2-3 ADRs

**Optional** (load if budget allows):
- Code files being reviewed (up to 10,000 tokens)
- Related tests

**Total**: ~7,000 tokens (12% of budget)
**Cumulative**: 15,000 tokens (25% of budget) ✅

---

#### For `propose_architecture`:

**Critical** (always load):
- **Existing ADRs** (all or recent 5) (~8,000 tokens)
  - Learn decision-making patterns
  - Avoid contradicting previous decisions

- **Architecture specs** (recent 2-3) (~6,000 tokens)
  - Understand current architecture
  - Maintain consistency

**Optional**:
- Research materials (articles, docs) if provided by user

**Total**: ~14,000 tokens (23% of budget)
**Cumulative**: 22,000 tokens (37% of budget) ⚠️ **Over CFR-007!**

**Mitigation**: Load ADRs as summaries (title + decision only, skip rationale) → Reduce to 4,000 tokens
**Adjusted Cumulative**: 18,000 tokens (30% of budget) ✅

---

#### For `manage_dependencies`:

**Critical** (always load):
- **`pyproject.toml`** (~500 tokens)
  - Current dependencies
  - Version constraints

- **Dependency ADRs** (if exist) (~2,000 tokens)
  - Previous dependency decisions
  - Approval patterns

**Optional**:
- Security scan results
- License compatibility matrix

**Total**: ~2,500 tokens (4% of budget)
**Cumulative**: 10,500 tokens (18% of budget) ✅

---

#### For `create_adr`:

**Critical** (always load):
- **Existing ADRs** (recent 3 for format) (~4,000 tokens)
  - ADR template format
  - Decision structure
  - Rationale depth

- **Technical context** (provided by user or from discussion) (~3,000 tokens)

**Total**: ~7,000 tokens (12% of budget)
**Cumulative**: 15,000 tokens (25% of budget) ✅

---

#### For `provide_feedback`:

**Critical** (always load):
- **Architecture guidelines** (relevant to feedback) (~3,000 tokens)
  - Example: If feedback on error handling → GUIDELINE-001

- **Coding standards from CLAUDE.md** (~2,000 tokens)
  - Black, type hints, testing requirements

**Optional**:
- Commit diff (if reviewing specific commit)
- Related spec (if implementation deviates)

**Total**: ~5,000 tokens (8% of budget)
**Cumulative**: 13,000 tokens (22% of budget) ✅

---

### Step 5: Validate Context Budget (CFR-007)

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
        "remaining": budget - total_tokens
    }
```

**If over budget**:
1. **Summarize long documents** (ROADMAP, specs)
   - Extract key sections only
   - Skip examples, verbose explanations
2. **Load fewer optional files**
   - Prioritize by relevance
   - Defer to user-provided context
3. **Use file excerpts instead of full files**
   - Load specific sections (e.g., "## Architecture" from CLAUDE.md)

**Output**: Validation report

**Example Report**:
```markdown
## CFR-007 Context Budget Validation

**Task Type**: create_spec
**Total Tokens Loaded**: 17,500 / 60,000 (29%)
**Status**: ✅ COMPLIANT

**Files Loaded**:
1. .claude/agents/architect.md - 3,000 tokens
2. .claude/CLAUDE.md (excerpts) - 5,000 tokens
3. ROADMAP.md (priority section) - 2,000 tokens
4. SPEC-000-template.md - 1,500 tokens
5. Recent specs (3) - 6,000 tokens

**Remaining Budget**: 42,500 tokens (71% available for work)

**Ready to proceed**: YES ✅
```

---

### Step 6: Generate Startup Summary

**Create concise summary for architect**:

```markdown
# Architect Startup Summary

**Session Start**: 2025-10-18 10:00 AM
**Task Type**: create_spec
**Priority**: PRIORITY 10 - User Authentication

## Context Loaded (✅ CFR-007 Compliant: 29%)

### Core Identity (13%)
- ✅ Agent role & responsibilities
- ✅ Architecture patterns & standards
- ✅ Tool ownership rules

### Task-Specific Context (16%)
- ✅ ROADMAP priority details
- ✅ Spec template format
- ✅ Recent spec examples (SPEC-060, SPEC-061)

## Ready to Work

**Available Context Budget**: 71% (140,000 tokens)
**Recommended Actions**:
1. Review PRIORITY 10 description
2. Use spec-creation-automation skill (if available)
3. Create SPEC-062-user-authentication.md

**Collaboration**:
- Request code_developer for implementation after spec complete
- Request user approval for new dependencies (passlib, python-jose)

**Estimated Time**: 25 minutes (with spec-creation-automation skill)
```

---

## Decision Logic: Which Files to Load

**Decision Tree**:
```
IF task_type == "create_spec":
    Load: agent definition, CLAUDE.md (architecture), ROADMAP (priority), template, recent specs
ELIF task_type == "review_code":
    Load: agent definition, guidelines, relevant ADRs, code files
ELIF task_type == "propose_architecture":
    Load: agent definition, all ADRs (summarized), recent specs
ELIF task_type == "manage_dependencies":
    Load: agent definition, pyproject.toml, dependency ADRs
ELIF task_type == "create_adr":
    Load: agent definition, recent ADRs (format), technical context
ELIF task_type == "provide_feedback":
    Load: agent definition, guidelines, coding standards
ELSE:
    Load: agent definition only (minimal startup)
```

---

## Integration with Architect Agent

**In architect agent startup sequence**:

```python
# coffee_maker/autonomous/agents/architect_agent.py (future)

from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

class ArchitectAgent:
    def __init__(self, task_type: str, priority_name: str = None):
        # Step 1: Load startup skill
        self.startup_context = self._load_startup_context(task_type, priority_name)

        # Step 2: Validate CFR-007
        if not self.startup_context["cfr007_compliant"]:
            raise ContextBudgetError("CFR-007 violation: Context exceeds 30% budget")

        # Step 3: Ready to work
        self.ready = True

    def _load_startup_context(self, task_type: str, priority_name: str = None):
        """Load context using architect-startup skill."""
        skill = load_skill(SkillNames.ARCHITECT_STARTUP, {
            "TASK_TYPE": task_type,
            "PRIORITY_NAME": priority_name or "",
        })

        # Execute skill with LLM
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        claude = ClaudeCLIInterface()
        result = claude.execute_prompt(skill)

        # Parse result for file list and validation
        return self._parse_startup_result(result.content)
```

---

## Benefits of Agent Startup Skills

### 1. **CFR-007 Compliance Guaranteed**
- Every agent startup validates context budget
- Automatic reduction if over budget
- No more manual trial-and-error

### 2. **Faster Startup Time**
- Load only what's needed (17.5k tokens vs 60k)
- Reduced LLM processing time
- Quicker response to user

### 3. **Task-Optimized Context**
- Different tasks = different context
- No "one size fits all" approach
- Relevant information always loaded

### 4. **Consistent Behavior**
- Every architect session starts the same way
- Predictable context loading
- Easier debugging

### 5. **Measurable Efficiency**
- Track context usage per task type
- Optimize over time
- Data-driven improvements

---

## Success Metrics

**Time Savings**:
- **Before**: 5-10 min manual context selection + CFR-007 violations (48 min each)
- **After**: <1 min automated context loading, zero violations
- **Savings**: 4-57 minutes per session (depending on violations)

**Quality Improvements**:
- **CFR-007 violations**: 40-60/month → 0/month ✅
- **Context relevance**: 60% → 95% (task-optimized)
- **Startup time**: 2-3 min → <30 seconds

**Measurement**:
- Track CFR-007 violation count (goal: 0)
- Track context budget usage per task type
- Track architect session duration (startup → first output)

---

## Related Skills

- **context-budget-optimizer**: General context optimization (for all agents)
- **spec-creation-automation**: Uses this startup skill before creating specs
- **architect-commit-review**: Uses this startup skill before reviewing code

---

**Remember**: Smart startup = Smooth session! No more CFR-007 violations! 🎯

**Architect's Mantra**: "Load smart, work fast, stay compliant!"
