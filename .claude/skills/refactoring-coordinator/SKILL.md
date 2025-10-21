---
description: Coordinate safe multi-file refactorings with dependency analysis and automated rollback
---

# Refactoring Coordinator Skill

**Purpose**: Enable safe, large-scale refactorings (>5 files) with automated dependency analysis and rollback

**Category**: code_developer acceleration
**Impact**: 3-5 hours manual testing per refactoring → 30-60 minutes automated

---

## What This Skill Does

Automates the dangerous parts of multi-file refactoring:

1. **Dependency Analysis** - Maps import relationships across all files
2. **Safe Refactoring Order** - Calculates topological sort for safe execution
3. **Automated Testing** - Runs tests after each file with pytest-xdist
4. **Automatic Rollback** - Reverts all changes if ANY test fails
5. **Impact Report** - Shows what changed, what could break, risk assessment

**Key Features**:
- ✅ Builds complete dependency graph (imports, function calls)
- ✅ Detects circular dependencies automatically
- ✅ Calculates safe refactoring order via topological sort
- ✅ Executes refactoring incrementally (one file at a time)
- ✅ Runs full test suite after each file
- ✅ Parallel test execution with pytest-xdist
- ✅ Automatic rollback if tests fail
- ✅ Comprehensive impact reports

---

## When To Use

### Use Case 1: Rename Function Across Codebase

```bash
# code_developer: Rename get_user() → fetch_user_by_id()
$ refactoring-coordinator --type rename \
    --search "def get_user" \
    --replace "def fetch_user_by_id"

✅ Dependency Analysis: Found 23 references across 8 files
✅ Refactoring Order: auth.py → handlers.py → services.py → tests/
✅ Refactoring Progress:
   [████░░░░] coffee_maker/auth/user.py (tests passing)
   [████████] coffee_maker/auth/handlers.py (tests passing)
   [████████] coffee_maker/services/auth.py (tests passing)
✅ All tests passing! Refactoring complete.

Time: 12 min (vs 45 min manual)
```

### Use Case 2: Extract Function to New Module

```bash
# Extract rate limiting logic to separate module
$ refactoring-coordinator --type extract \
    --source-file "coffee_maker/api/middleware.py:67-98" \
    --target-file "coffee_maker/utils/rate_limiting.py" \
    --function "rate_limiter"

✅ Analysis:
   - 5 files import rate_limiter
   - 3 test files cover rate_limiter
   - No circular dependencies

✅ Creating target file with proper structure
✅ Updating 5 import statements
✅ Running tests...
   ✅ 127 tests passing
✅ Complete! All code references updated.
```

### Use Case 3: Move Classes Between Modules

```bash
# Move UserService from services/user.py to services/users/service.py
$ refactoring-coordinator --type move \
    --source "coffee_maker/services/user.py:UserService" \
    --target "coffee_maker/services/users/service.py"

✅ Dependency Analysis:
   - 12 files import UserService (direct or indirect)
   - 4 circular dependency chains detected
   - Safe refactoring order: 12 files → Refactor in 3 groups (no cycles)

✅ Group 1 (no dependencies):
   [████████] test_user_service.py ✓

✅ Group 2 (depends on Group 1):
   [████████] handlers.py ✓
   [████████] cli/user_commands.py ✓

✅ Group 3 (depends on Groups 1-2):
   [████████] integration_test.py ✓

✅ All 147 tests passing!
Time: 22 min (vs 60+ min manual with careful testing)
```

---

## Instructions

### Step 1: Analyze Dependencies

```bash
python scripts/dependency_analyzer.py \
    --files "coffee_maker/auth/*.py" \
    [--output deps.json]
```

**What it does**:
1. Scans all Python files in specified directory
2. Parses with AST to extract imports
3. Builds directed graph: file → dependencies
4. Detects circular dependencies
5. Calculates dependency statistics

**Output**:
```json
{
  "total_files": 8,
  "total_functions": 234,
  "total_classes": 45,
  "circular_deps": [
    ["auth.py", "handlers.py", "auth.py"]
  ],
  "dependency_graph": {
    "auth.py": ["types.py", "config.py"],
    "handlers.py": ["auth.py", "exceptions.py"],
    "services.py": ["auth.py", "models.py"]
  },
  "complexity_stats": {
    "avg_imports_per_file": 4.2,
    "max_dependencies": 7,
    "max_dependents": 12
  }
}
```

**Time**: 5-10 seconds per 10 files

### Step 2: Plan Refactoring Order

```bash
python scripts/refactor_planner.py \
    --deps deps.json \
    --refactoring-type rename|extract|move|consolidate \
    [--output plan.json]
```

**What it does**:
1. Reads dependency graph
2. Identifies files affected by refactoring
3. Performs topological sort → safe order
4. Breaks into groups if circular dependencies
5. Validates no circular dependencies in refactoring

**Output**:
```
REFACTORING PLAN: Rename get_user() → fetch_user_by_id()

Affected Files: 8
Groups: 3 (no circular dependencies detected)

Group 1 (Core functionality - no dependencies):
├── coffee_maker/auth/user.py (core change)
├── tests/test_user.py (tests updated)
└── (Parallel safe)

Group 2 (Mid-level - depends on Group 1):
├── coffee_maker/api/handlers.py (uses get_user)
├── coffee_maker/services/auth.py (uses get_user)
└── (Sequential after Group 1)

Group 3 (Integration - depends on Groups 1-2):
├── tests/test_integration.py (full system tests)
└── (Final validation)

Risk Assessment: LOW
- Clear dependency chain
- No circular dependencies
- Well-tested code
- Test coverage: 92%
```

**Time**: 2-3 minutes

### Step 3: Execute Refactoring

```bash
python scripts/refactor_executor.py \
    --plan plan.json \
    [--parallel N_JOBS]
```

**What it does**:
1. Reads refactoring plan
2. For each group:
   - Applies refactoring to all files in group
   - Runs full test suite (pytest with xdist for parallelism)
   - If tests fail: Rollback group immediately
   - If tests pass: Commit group and continue

**Safety Features**:
- Automatic git stash before changes
- Full rollback on any test failure
- Test results logged per file
- Git commits after each group

**Output**:
```
Refactoring Group 1 (2 files):
├── Refactoring coffee_maker/auth/user.py...
├── Refactoring tests/test_user.py...
├── Running tests (parallel, 4 workers)...
│  ✓ test_user.py (3.2s)
│  ✓ test_auth.py (2.1s)
│  ✓ test_integration.py (4.8s)
├── All 18 tests passing!
└── ✅ Group 1 complete

Refactoring Group 2 (2 files):
├── Refactoring coffee_maker/api/handlers.py...
├── Refactoring coffee_maker/services/auth.py...
├── Running tests (parallel, 4 workers)...
│  ✓ test_handlers.py (2.5s)
│  ✓ test_services.py (3.1s)
│  ✗ test_integration.py FAILED (7.2s)
├── ❌ Tests failed! Rolling back Group 2...
└── ⚠️  Rollback complete. Group 1 still safe.
```

**Time**: 5-30 minutes depending on scope (vs 1-3 hours manual)

### Step 4: Verify Completeness

```bash
python scripts/refactor_verifier.py \
    --old-pattern "get_user" \
    --new-pattern "fetch_user_by_id" \
    --scope "coffee_maker/"
```

**What it does**:
1. Searches for any remaining old patterns
2. Checks all test files updated
3. Validates import statements
4. Checks for broken references

**Output**:
```
Verification Report: Rename get_user() → fetch_user_by_id()

Old pattern occurrences: 0 ✓
New pattern occurrences: 23 ✓
Test files updated: 4/4 ✓
Import statements valid: 12/12 ✓
Docstrings updated: 8/8 ✓
Type hints updated: 6/6 ✓

✅ Refactoring complete and verified!
```

---

## Scripts

### dependency_analyzer.py

```bash
python scripts/dependency_analyzer.py --files PATTERN [--output FILE]
```

**Purpose**: Build dependency graph for impact analysis

**Output**: JSON with dependency graph, circular deps, statistics

### refactor_planner.py

```bash
python scripts/refactor_planner.py --deps FILE --type rename|extract|move|consolidate
```

**Purpose**: Calculate safe refactoring order via topological sort

**Output**: Plan JSON with groups and risk assessment

### refactor_executor.py

```bash
python scripts/refactor_executor.py --plan FILE [--parallel N_JOBS]
```

**Purpose**: Execute refactoring with automatic rollback

**Safety**:
- Tests after each group
- Rollback on failure
- Full commit trail

### refactor_verifier.py

```bash
python scripts/refactor_verifier.py --old OLD --new NEW --scope PATH
```

**Purpose**: Verify refactoring completeness

**Output**: Verification report with all-clear or TODOs

---

## Safety Guarantees

### What This Skill Guarantees

- ✅ **No partial changes**: If tests fail, everything rolls back
- ✅ **No lost code**: Git history preserved, can always recover
- ✅ **No broken imports**: All import paths validated
- ✅ **No untested changes**: Every change tested before commit
- ✅ **Clear dependencies**: All relationships mapped upfront

### What Still Requires Human Review

- ⚠️ **Semantic correctness**: Tests verify behavior, but edge cases might need review
- ⚠️ **API contract changes**: Renaming public APIs requires design review
- ⚠️ **Performance implications**: Refactoring might have perf impacts
- ⚠️ **Documentation updates**: Docstrings must be manually reviewed

---

## Integration with Other Skills

### code-index
- Uses code-index to discover affected files
- Fetches pre-built dependency graph

### test-failure-analysis
- If tests fail during refactoring, uses test-failure-analysis to understand why
- Helps classify failure as "refactoring error" vs "existing bug"

### git-workflow-automation
- Auto-commits after each successful group
- Uses conventional commits (refactor scope)

### dependency-conflict-resolver
- If refactoring adds new dependencies, uses this to evaluate them
- Validates no breaking changes to dependency tree

---

## Performance Metrics

### Refactoring Time Comparison

| Task | Manual | Automated | Savings |
|------|--------|-----------|---------|
| **Dependency analysis** | 30-60 min | 5-10 sec | 99% |
| **Refactoring execution** | 1-3 hours | 5-30 min | 80-90% |
| **Testing** | 30-60 min (manual spot checks) | 2-5 min (full suite) | 90% |
| **Rollback/retry on failure** | 20-40 min | 1-2 min (automatic) | 95% |
| **Total per refactoring** | 2-5 hours | 15-50 min | 75-85% |

### Example: Rename Function

```
Manual approach:
1. Find all occurrences (grep/IDE): 15 min
2. Manually update each file: 30 min
3. Update tests: 20 min
4. Run full test suite: 30 min
5. Fix failures (if any): 20 min
Total: 115 minutes

Automated approach:
1. dependency_analyzer: 10 sec
2. refactor_planner: 2 min
3. refactor_executor (parallel tests): 10 min
4. refactor_verifier: 1 min
Total: 13 minutes (89% faster)
```

---

## Examples

### Example 1: Consolidate Similar Utilities

```bash
# Consolidate 3 duplicate rate-limiting implementations into one module
$ refactoring-coordinator --type consolidate \
    --files "coffee_maker/api/rate_limiter.py, \
             coffee_maker/services/throttle.py, \
             coffee_maker/utils/rate_limit_utils.py"

✅ Found 3 implementations of rate limiting
✅ Analyzing 23 dependent files...
✅ Consolidation plan (4 groups, no circular deps):
   Group 1: Extract common interface
   Group 2: Migrate coffee_maker/api to use common interface
   Group 3: Migrate coffee_maker/services to use common interface
   Group 4: Delete duplicate implementations

✅ Executing consolidation...
   [████████] Group 1: Interface extraction (✓ 12 tests)
   [████████] Group 2: API migration (✓ 34 tests)
   [████████] Group 3: Services migration (✓ 28 tests)
   [████████] Group 4: Cleanup (✓ 45 tests)

✅ Consolidation complete!
   - 3 modules → 1 unified module
   - Duplicate code: 247 LOC → 0 LOC
   - All 189 tests passing
   - Code reuse: 15 files now using single implementation

Time: 28 min (vs 2-3 hours manual)
```

### Example 2: Extract Large Class

```bash
# Extract UserManagement from UserService (class got too big)
$ refactoring-coordinator --type extract \
    --source "coffee_maker/services/user.py:UserService" \
    --extract-method "manage_*" \
    --target "coffee_maker/services/user_management.py"

✅ Impact Analysis:
   - 8 files import UserService
   - 12 test files test UserService
   - 5 files call manage_* methods
   - Risk: MEDIUM (public API change)

✅ Refactoring Plan (3 groups):
   Group 1: Create UserManagement class
   Group 2: Update internal calls
   Group 3: Update tests

✅ Executing...
   [████████] Group 1 (✓ 8 tests)
   [████████] Group 2 (✓ 34 tests)
   [████████] Group 3 (✓ 67 tests)

✅ Complete! UserService split:
   - UserService: 120 LOC → 45 LOC (simpler)
   - UserManagement: NEW → 75 LOC (focused)
   - All tests passing (109/109)

Time: 18 min (vs 90+ min manual)
```

---

## Limitations

**What This Skill CAN Do**:
- ✅ Safely rename functions, classes, files
- ✅ Extract code to new modules
- ✅ Move classes between files
- ✅ Consolidate duplicate code
- ✅ Update all references automatically
- ✅ Validate with tests
- ✅ Rollback on failure

**What This Skill CANNOT Do**:
- ❌ Understand semantic correctness (only syntactic)
- ❌ Update external documentation
- ❌ Handle breaking API changes (requires design review)
- ❌ Evaluate performance implications
- ❌ Change non-Python files

**Workarounds**:
- For semantics: Manual review of test results
- For documentation: Update docs separately
- For breaking changes: Plan API versioning separately
- For performance: Profile before and after
- For non-Python: Integrate language-specific tools

---

## Rollout Plan

### Week 1: Infrastructure ✅ (conceptual - now building)
- [x] Create this skill definition
- [ ] Implement dependency_analyzer.py
- [ ] Implement refactor_planner.py

### Week 2: Execution & Testing
- [ ] Implement refactor_executor.py
- [ ] Implement refactor_verifier.py
- [ ] Test on simple refactoring
- [ ] Test automatic rollback

### Week 3: Integration & Validation
- [ ] Integrate with code-index
- [ ] Integrate with test-failure-analysis
- [ ] Test on real codebase refactoring
- [ ] Measure time savings

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Dependency analysis time** | <10s for typical codebase |
| **Plan calculation** | <2 min for complex cases |
| **Refactoring execution** | 80-90% faster than manual |
| **Test pass rate** | 100% (or full rollback) |
| **False positive rollbacks** | 0% (only real failures) |
| **Developer confidence** | "I trust it completely" |

---

**Created**: 2025-10-18
**Status**: Ready for Implementation
**Related US**: US-102, US-090 (Code Analysis Skills)
**ROI**: 2-5 hours → 15-50 minutes per refactoring (75-85% faster)
