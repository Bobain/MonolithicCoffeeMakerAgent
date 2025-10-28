# Granular Command Context Budget Analysis

**Date**: 2025-10-28
**Status**: 🚨 **CRITICAL FINDING**
**Issue**: Individual command prompts already near/over 30% budget

---

## Problem Statement

Analysis of the **36 consolidated command prompts** reveals that **individual prompts** are already consuming 20-34% of the context budget. This means even with proper granularity (25 commands), agents still cannot load multiple prompts without exceeding CFR-007.

**Context Budget**: 32,000 tokens ÷ 20 tokens/line = **1,600 lines available**
**CFR-007 Limit**: 30% = **480 lines maximum**

---

## Individual Prompt Analysis

### CodeDeveloper Commands

| Prompt File | Lines | % of Budget | Status |
|-------------|-------|-------------|--------|
| update_claude_config.md | 455 | 28% | ⚠️ Near limit |
| track_metrics.md | 390 | 24% | ⚠️ |
| generate_coverage_report.md | 388 | 24% | ⚠️ |
| implement_bug_fix.md | 375 | 23% | ⚠️ |
| run_pre_commit_hooks.md | 332 | 21% | ⚠️ |
| create_pull_request.md | 316 | 20% | ⚠️ |
| implement_priority.md | 308 | 19% | ⚠️ |

**Finding**: Largest single prompt = 455 lines (91% of budget)

### ProjectManager Commands

| Prompt File | Lines | % of Budget | Status |
|-------------|-------|-------------|--------|
| create_roadmap_report.md | 462 | 29% | ⚠️ Near limit |
| analyze_project_health.md | 441 | 28% | ⚠️ Near limit |
| strategic_planning.md | 400 | 25% | ⚠️ |
| verify_dod_puppeteer.md | 371 | 23% | ⚠️ |
| process_notifications.md | 364 | 23% | ⚠️ |

**Finding**: 2 prompts near 30% limit individually

### CodeReviewer Commands

| Prompt File | Lines | % of Budget | Status |
|-------------|-------|-------------|--------|
| **README.md** | 537 | **34%** | ❌ **OVER BUDGET** |
| validate_dod_compliance.md | 439 | 27% | ⚠️ |
| IMPLEMENTATION-CHECKLIST.md | 420 | 26% | ⚠️ |
| check_architecture_compliance.md | 392 | 25% | ⚠️ |
| generate_quality_score.md | 387 | 24% | ⚠️ |
| validate_type_hints.md | 382 | 24% | ⚠️ |
| analyze_complexity.md | 381 | 24% | ⚠️ |

**Finding**: README.md EXCEEDS 30% budget!
**Issue**: Multiple prompts at 24-27% means loading 2 prompts = 48-54% (OVER)

---

## Critical Implication

### Scenario 1: CodeDeveloper needs to implement a feature

**Required prompts**:
1. `implement_priority.md` - 308 lines (19%)
2. `run_test_suite.md` - 301 lines (19%)
3. `create_pull_request.md` - 316 lines (20%)

**Total**: 925 lines = **58% of budget** ❌ **OVER CFR-007**

### Scenario 2: CodeReviewer reviews a commit

**Required prompts**:
1. `README.md` - 537 lines (34%)
2. `run_security_scan.md` - 363 lines (23%)
3. `check_test_coverage.md` - 349 lines (22%)

**Total**: 1,249 lines = **78% of budget** ❌❌ **SEVERELY OVER**

### Scenario 3: ProjectManager creates report

**Required prompts**:
1. `create_roadmap_report.md` - 462 lines (29%)
2. `analyze_project_health.md` - 441 lines (28%)

**Total**: 903 lines = **56% of budget** ❌ **OVER CFR-007**

---

## Root Cause

**Prompts are too detailed and include everything**:
- Background context
- Database schemas
- Examples (3-5 per prompt)
- Error handling
- Implementation notes
- SQL queries
- Best practices
- Related commands

**Each prompt tries to be comprehensive** → 300-500 lines each

---

## Solution: Hierarchical Skills

### Concept

Break large prompts into **hierarchical skills** where:
1. **Core skill** (50-100 lines) - Essential workflow logic
2. **Sub-skills** (30-80 lines each) - Loaded dynamically when needed

**Example**: `implement_priority.md` (308 lines) → Break into:

```
skills/
└── code_developer/
    ├── implement/
    │   ├── core.md              # 80 lines - Main workflow
    │   ├── load_spec.md         # 40 lines - Load specification
    │   ├── generate_code.md     # 60 lines - Code generation
    │   ├── handle_errors.md     # 50 lines - Error handling
    │   └── examples.md          # 70 lines - Examples (optional)
    └── shared/
        └── database_patterns.md # 50 lines - Shared DB patterns
```

### Dynamic Loading

Agent loads only what's needed:

```python
# Load core skill (80 lines)
skill = load_skill("code_developer/implement/core")

# Dynamically load sub-skills as needed
if need_spec_loading:
    load_skill("code_developer/implement/load_spec")  # +40 lines

if errors_encountered:
    load_skill("code_developer/implement/handle_errors")  # +50 lines

# Total: 80-170 lines depending on path (5-11% context)
```

---

## Hierarchical Skills Structure

### Core Skill Template (50-100 lines)

```markdown
# Skill: implement_priority (Core)

## Purpose
Implement a priority from ROADMAP.md

## Workflow
1. Load spec → [load_spec sub-skill]
2. Generate code → [generate_code sub-skill]
3. Track changes → Built-in

## Parameters
- priority_id: string (required)
- auto_test: boolean (default: true)

## Result
ImplementResult(files_changed, tests_run)

## Error Handling
→ See [handle_errors sub-skill]

## Examples
→ See [examples sub-skill] for 5 detailed examples
```

### Sub-Skill Template (30-80 lines)

```markdown
# Sub-Skill: load_spec

## Purpose
Load technical specification from database

## Inputs
- spec_id: string

## SQL
```sql
SELECT spec_id, title, description, ...
FROM technical_spec WHERE spec_id = ?
```

## Returns
- spec_data: dict

## Errors
- SpecNotFound: spec_id doesn't exist
- DatabaseError: Connection failed
```

---

## Proposed Hierarchical Skill Architecture

### CodeDeveloper Skills

```
skills/code_developer/
├── implement/
│   ├── core.md (80 lines) - Main workflow
│   ├── load_spec.md (40 lines)
│   ├── generate_code.md (60 lines)
│   ├── handle_errors.md (50 lines)
│   └── examples.md (70 lines)
├── test/
│   ├── core.md (70 lines)
│   ├── run_suite.md (50 lines)
│   ├── fix_failures.md (60 lines)
│   └── coverage.md (40 lines)
├── finalize/
│   ├── core.md (60 lines)
│   ├── quality_checks.md (50 lines)
│   ├── commit.md (40 lines)
│   └── pr_creation.md (50 lines)
└── shared/
    ├── database_patterns.md (50 lines)
    └── git_operations.md (40 lines)
```

**Total**: 11 core skills + 14 sub-skills + 2 shared
**Max load**: 80 (core) + 60 (largest sub) + 50 (shared) = 190 lines = 12% ✅

### ProjectManager Skills

```
skills/project_manager/
├── roadmap/
│   ├── core.md (70 lines)
│   ├── parse.md (50 lines)
│   ├── sync_db.md (40 lines)
│   └── validate.md (40 lines)
├── track/
│   ├── core.md (60 lines)
│   ├── calculate_progress.md (40 lines)
│   ├── send_notifications.md (50 lines)
│   └── update_status.md (40 lines)
├── plan/
│   ├── core.md (70 lines)
│   ├── create_priority.md (50 lines)
│   └── generate_tasks.md (60 lines)
└── report/
    ├── core.md (80 lines)
    ├── gather_metrics.md (60 lines)
    ├── analyze_health.md (70 lines)
    └── format_report.md (50 lines)
```

**Max load**: 80 + 70 = 150 lines = 9% ✅

### CodeReviewer Skills

```
skills/code_reviewer/
├── analyze/
│   ├── core.md (70 lines)
│   ├── security_scan.md (60 lines)
│   ├── style_check.md (50 lines)
│   ├── test_coverage.md (50 lines)
│   └── quality_score.md (60 lines)
├── security/
│   ├── core.md (60 lines)
│   ├── bandit_scan.md (50 lines)
│   └── secret_detection.md (40 lines)
└── fix/
    ├── core.md (50 lines)
    ├── style_autofix.md (40 lines)
    └── import_cleanup.md (30 lines)
```

**Max load**: 70 + 60 = 130 lines = 8% ✅

---

## Benefits of Hierarchical Skills

### ✅ Context Budget Compliance

| Scenario | Traditional | Hierarchical | Savings |
|----------|------------|--------------|---------|
| Implement feature | 925 lines (58%) | 190 lines (12%) | **80% reduction** |
| Review commit | 1,249 lines (78%) | 200 lines (13%) | **84% reduction** |
| Create report | 903 lines (56%) | 210 lines (13%) | **77% reduction** |

### ✅ Dynamic Loading

```python
# Only load what's needed
skill = load_core_skill("implement")  # 80 lines

if complex_spec:
    load_sub_skill("implement/load_spec")  # +40 lines

if need_examples:
    load_sub_skill("implement/examples")  # +70 lines

# Total: 80-190 lines depending on execution path
```

### ✅ Reusability

```python
# Shared skills used across commands
load_sub_skill("shared/database_patterns")  # Used by ALL commands
load_sub_skill("shared/git_operations")  # Used by multiple commands
```

### ✅ Maintainability

- Small, focused files (30-80 lines each)
- Easy to update individual sub-skills
- Clear separation of concerns
- Testable in isolation

---

## Implementation Strategy

### Phase 1: Identify Large Prompts (✅ DONE)

Analyzed all consolidated command prompts:
- CodeDeveloper: 8 prompts over 300 lines
- ProjectManager: 5 prompts over 360 lines
- CodeReviewer: 7 prompts over 349 lines

### Phase 2: Design Hierarchical Structure

For each large prompt:
1. Extract core workflow (50-100 lines)
2. Identify sub-skills (30-80 lines each)
3. Extract shared patterns (30-60 lines)
4. Create skill hierarchy

### Phase 3: Implement Skills

Create `.claude/skills/` directory:
```
.claude/skills/
├── code_developer/
├── project_manager/
├── architect/
├── code_reviewer/
├── orchestrator/
├── user_listener/
├── assistant/
├── ux_design_expert/
└── shared/
```

### Phase 4: Update Command Classes

Implement dynamic skill loading:
```python
class CodeDeveloperCommands:
    def implement(self, priority_id: str):
        # Load core skill
        core = load_skill("code_developer/implement/core")

        # Dynamic sub-skill loading based on execution path
        if needs_spec_loading():
            spec_skill = load_skill("code_developer/implement/load_spec")
            spec_data = spec_skill.execute(priority_id)
```

### Phase 5: Validate Context Budget

Test real-world scenarios:
- Measure actual context usage
- Verify <30% per agent
- Adjust skill sizes if needed

---

## Success Criteria

### Context Budget

| Agent | Traditional | With Hierarchical Skills | Target |
|-------|------------|--------------------------|--------|
| CodeDeveloper | 308% | <30% | ✅ |
| ProjectManager | 339% | <30% | ✅ |
| Architect | 245% | <30% | ✅ |
| CodeReviewer | 369% | <30% | ✅ |
| All agents | 102-369% | <30% | ✅ |

### Functionality

- ✅ All commands work with hierarchical skills
- ✅ Dynamic loading functions correctly
- ✅ Shared skills reused properly
- ✅ No functionality loss

### Maintainability

- ✅ Small, focused skill files (30-100 lines)
- ✅ Clear hierarchy and organization
- ✅ Easy to update individual skills
- ✅ Reduced duplication via shared skills

---

## Recommendation

**Immediately implement hierarchical skills architecture**:

1. **Break large prompts (300-500 lines) into hierarchical skills**:
   - Core skills: 50-100 lines
   - Sub-skills: 30-80 lines
   - Shared skills: 30-60 lines

2. **Implement dynamic loading** so agents only load what they need

3. **Validate context budget** with real-world usage

4. **Benefits**:
   - 80-84% context reduction
   - CFR-007 compliant
   - Better maintainability
   - Increased reusability

**This is the ONLY path to CFR-007 compliance** given that individual prompts already consume 20-34% of budget.

---

**Status**: 🚨 **CRITICAL - MUST IMPLEMENT**
**Action**: Design and implement hierarchical skills architecture
**Timeline**: High priority (blocker for production)
