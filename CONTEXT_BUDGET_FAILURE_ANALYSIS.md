# Context Budget Failure Analysis

**Date**: 2025-10-28
**Status**: ❌ **CRITICAL FAILURE**
**Issue**: Ultra-consolidation does NOT achieve CFR-007 compliance

---

## Problem Statement

The ultra-consolidated workflow commands **still call the consolidated command prompts**, which means each agent must load:
1. Their workflow prompt (348-591 lines)
2. ALL their consolidated command prompts (1,291-5,905 lines)

**Total context per agent MASSIVELY exceeds 30% budget.**

---

## Actual Context Budget Calculation

### Context Window: 32,000 tokens
- **30% budget**: 9,600 tokens
- **At 20 tokens/line**: 480 lines maximum per agent

### Consolidated Command Prompts

| Agent | Command Prompts | Lines |
|-------|----------------|-------|
| code_developer | 15 files | 4,396 |
| project_manager | 15 files | 4,878 |
| architect | 13 files | 3,337 |
| code_reviewer | 15 files | 5,375 |
| orchestrator | 16 files | 3,938 |
| user_listener | 10 files | 1,291 |
| assistant | 12 files | 1,518 |
| ux_design_expert | 11 files | 1,651 |

### Workflow Prompts

| Agent | Workflow Prompt | Lines |
|-------|----------------|-------|
| code_developer | code-developer-workflow.md | 531 |
| project_manager | project-manager-workflow.md | 539 |
| architect | architect-workflow.md | 591 |
| code_reviewer | code-reviewer-workflow.md | 530 |
| orchestrator | orchestrator-workflow.md | 382 |
| user_listener | user-listener-workflow.md | 348 |
| assistant | assistant-workflow.md | 372 |
| ux_design_expert | ux-design-workflow.md | 529 |

### **TOTAL CONTEXT PER AGENT**

| Agent | Command + Workflow | Total Lines | Tokens | % of Context | Status |
|-------|-------------------|-------------|--------|--------------|--------|
| code_developer | 4,396 + 531 | **4,927** | **98,540** | **308%** | ❌❌❌ |
| project_manager | 4,878 + 539 | **5,417** | **108,340** | **339%** | ❌❌❌ |
| architect | 3,337 + 591 | **3,928** | **78,560** | **245%** | ❌❌❌ |
| code_reviewer | 5,375 + 530 | **5,905** | **118,100** | **369%** | ❌❌❌ |
| orchestrator | 3,938 + 382 | **4,320** | **86,400** | **270%** | ❌❌❌ |
| user_listener | 1,291 + 348 | **1,639** | **32,780** | **102%** | ❌ |
| assistant | 1,518 + 372 | **1,890** | **37,800** | **118%** | ❌ |
| ux_design_expert | 1,651 + 529 | **2,180** | **43,600** | **136%** | ❌ |

### **CFR-007 Requirement**: ≤30% (9,600 tokens / 480 lines)

**Result**: ❌ **ALL agents exceed budget**
- **Worst**: code_reviewer at 369% (12x over budget!)
- **Best**: user_listener at 102% (still 3x over budget)
- **Average**: 226% (7.5x over budget)

---

## Root Cause

The workflow commands are NOT self-contained. They call consolidated commands:

```python
# coffee_maker/commands/workflow/code_developer_workflow.py
class CodeDeveloperWorkflow:
    def __init__(self, db_path: Optional[str] = None):
        self.commands = CodeDeveloperCommands(db_path)  # ← Loads ALL consolidated commands!

    def work(self, task_id: str):
        self.commands.implement(action="load_task", task_id=task_id)  # ← Needs load_task.md prompt
        self.commands.implement(action="write_code", task_id=task_id)  # ← Needs write_code.md prompt
        self.commands.test(action="run_suite", task_id=task_id)  # ← Needs run_suite.md prompt
        self.commands.quality(action="check_all", task_id=task_id)  # ← Needs check_all.md prompt
        self.commands.git(action="commit", ...)  # ← Needs commit.md prompt
```

Each `self.commands.X()` call requires loading that command's prompt file from `.claude/commands/agents/code_developer/`.

---

## Why This Happened

1. **Phase 1**: Created 36 consolidated commands with 108 prompt files (26,517 lines)
2. **Phase 2**: Created 8 workflow commands that **delegate to** the 36 consolidated commands
3. **Phase 3**: Created 8 workflow prompts (3,822 lines)
4. **Problem**: Workflows are wrappers, not replacements. They still load all underlying command prompts.

---

## Impact

### CFR-007 Violations

| Agent | Budget | Actual | Over Budget |
|-------|--------|--------|-------------|
| code_developer | 9,600 | 98,540 | +1,027% |
| project_manager | 9,600 | 108,340 | +1,128% |
| architect | 9,600 | 78,560 | +818% |
| code_reviewer | 9,600 | 118,100 | +1,230% |
| orchestrator | 9,600 | 86,400 | +900% |
| user_listener | 9,600 | 32,780 | +341% |
| assistant | 9,600 | 37,800 | +394% |
| ux_design_expert | 9,600 | 43,600 | +454% |

### Operational Issues

- ❌ Agents cannot load their full context (exceeds window)
- ❌ CFR-007 critically violated (not even close to 30%)
- ❌ Ultra-consolidation effort FAILED to achieve its primary goal
- ❌ System is not production-ready

---

## Solution Options

### Option 1: Self-Contained Workflow Prompts (RECOMMENDED)

**Eliminate dependency on consolidated commands:**

```python
# Workflow commands should NOT call consolidated commands
# Instead, implement logic directly with database queries

class CodeDeveloperWorkflow:
    def __init__(self, db_path: Optional[str] = None):
        self.db = Database(db_path)  # ← Direct database access only
        # NO self.commands!

    def work(self, task_id: str):
        # Direct implementation without command prompts
        task_data = self.db.query("SELECT * FROM specs_task WHERE task_id = ?", task_id)
        # ... implement directly
```

**Context per agent**: 348-591 lines (workflow prompt only)
- **Tokens**: 6,960-11,820
- **Percentage**: 22-37% of context
- **Status**: ❌ Still slightly over 30% for some agents

**Needs**: Further prompt reduction to get under 30%

### Option 2: Micro-Prompts (Most Radical)

**Break workflow prompts into tiny, focused prompts (<50 lines each):**

```
.claude/commands/micro/
├── code_developer/
│   ├── load_task.md (40 lines)
│   ├── write_code.md (50 lines)
│   ├── run_tests.md (35 lines)
│   └── commit.md (30 lines)
```

**Context per agent**: ~150-250 lines total
- **Tokens**: 3,000-5,000
- **Percentage**: 9-16% of context
- **Status**: ✅ Compliant

### Option 3: Dynamic Prompt Loading

**Load only the prompts needed for current action:**

```python
def work(self, task_id: str, mode: str = "auto"):
    if mode == "auto":
        prompts = ["load_task", "write_code", "test", "commit"]
    elif mode == "test-only":
        prompts = ["test"]  # Only load test prompt

    # Load only required prompts dynamically
    for prompt in prompts:
        load_prompt(f"code_developer_{prompt}.md")
```

**Context per agent**: Varies by action (50-400 lines)
- **Tokens**: 1,000-8,000
- **Percentage**: 3-25% of context
- **Status**: ✅ Compliant

### Option 4: Abort Ultra-Consolidation

**Revert to original architecture or Phase 1 consolidated commands**
- Accept that context budget cannot be met
- Implement workarounds (context pruning, external documentation)
- **Status**: ⚠️ Not recommended

---

## Recommended Path Forward

### Immediate Actions

1. **STOP** using ultra-consolidated workflows in production
2. **ANALYZE** which approach fits project needs:
   - Option 1: Self-contained workflows (medium effort)
   - Option 2: Micro-prompts (high effort, best result)
   - Option 3: Dynamic loading (medium effort, complex)

3. **IMPLEMENT** chosen solution
4. **VALIDATE** actual context usage with real agents
5. **UPDATE** CFR-007 compliance status

### Priority: **CRITICAL**

The system cannot operate with 10x context budget violations. This must be fixed before any agent integration.

---

## Lessons Learned

1. **Context budget must include ALL prompts** loaded by an agent
2. **Wrapper commands** don't reduce context (they add to it)
3. **Validation must be complete** (not just workflow prompts alone)
4. **Architectural assumptions** must be validated early

---

**Status**: ❌ **ULTRA-CONSOLIDATION FAILED CFR-007**
**Action Required**: Choose and implement solution option
**Blocker**: System not production-ready until fixed
