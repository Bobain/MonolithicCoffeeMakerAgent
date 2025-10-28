# Realistic Context Budget Analysis

**Date**: 2025-10-28
**Issue**: Previous analysis had flawed assumption about external docs
**Reality Check**: If AI needs it, it must be in context

---

## The Flawed Assumption

**I claimed**:
- Write 120-line prompts
- Put examples in external docs (WORKFLOWS.md)
- "External docs don't count toward budget"

**The flaw**:
- If AI loads external docs → they DO count toward budget
- If AI never loads them → they're useless for AI execution
- Either way, my calculation was wrong

---

## Reality: What AI Actually Needs

For an AI to execute a command effectively, it needs:

### 1. Essential (Always Needed) - ~60-80 lines
- Purpose (5 lines)
- Parameters (15 lines)
- Workflow steps (15 lines)
- Database queries (20 lines)
- Result object (15 lines)
- Error handling (15 lines)

### 2. Contextual (Often Needed) - ~40-60 lines
- At least 1 good example (20 lines)
- Implementation patterns (20 lines)
- Edge case handling (20 lines)

### 3. Optional (Rarely Needed) - ~30-50 lines
- Additional examples (30 lines)
- Troubleshooting (20 lines)

**Total needed for good execution**: 100-140 lines minimum per command

---

## True Context Budget Calculation

### Scenario: CodeDeveloper implements a task

**Commands AI will load**:
1. `implement` command - Need: Essential + Contextual = 120 lines
2. `test` command - Need: Essential + Contextual = 110 lines
3. `finalize` command - Need: Essential + Contextual = 115 lines

**Total**: 345 lines = **22% context**

**BUT WAIT**: AI also needs:
- Task specification (50-100 lines)
- Existing code context (100-200 lines)
- Error messages if debugging (50-100 lines)

**Realistic total**: 545-745 lines = **34-47% context** ❌ **OVER BUDGET**

---

## The Real Problem

**30% budget = 480 lines is NOT ENOUGH for**:
- 3 command prompts (300-400 lines)
- Task/spec context (50-100 lines)
- Code context (100-200 lines)
- Working memory (50-100 lines)

**We need a different approach entirely.**

---

## Solution Options (Honest Assessment)

### Option 1: Extremely Minimal Prompts (40-60 lines)

**Concept**: Prompts are EXTREMELY terse, assume AI intelligence

```markdown
# implement

## Purpose
Load spec, generate code, track files

## Params
task_id: str

## Workflow
1. SELECT * FROM specs_task WHERE task_id=?
2. Generate code from spec
3. Write files
4. Return ImplementResult(files, status)

## Errors
- SpecNotFound: Check task_id
- CodeGenFailed: Review spec

## Example
impl = implement("TASK-42")
# Returns: ImplementResult(files=["a.py"], status="success")
```

**Size**: 40-50 lines per command
**Loading 3**: 150 lines = **9% context** ✅

**Pros**:
- Fits in budget with room for task context
- Simple, minimal

**Cons**:
- ❌ No detailed examples
- ❌ No implementation guidance
- ❌ AI might make mistakes without guidance
- ❌ Relies heavily on AI's base knowledge

---

### Option 2: True Hierarchical with Lazy Loading

**Concept**: Load examples ONLY when AI explicitly needs help

```python
# Initial load: Just essentials
core = load_prompt("implement/core")  # 60 lines

# AI executes...
try:
    result = execute_implement(task_id)
except UnknownPatternError:
    # NOW load examples
    examples = load_prompt("implement/examples")  # +40 lines
    retry_with_examples()
```

**Normal execution**: 60 + 55 + 50 = 165 lines = **10% context** ✅
**With help needed**: 165 + 120 (examples) = 285 lines = **18% context** ✅

**Pros**:
- Most executions stay under budget
- Examples available when actually needed
- Realistic and practical

**Cons**:
- More complex loading logic
- Need to detect when AI needs help

---

### Option 3: Agent-Specific Context Windows

**Concept**: Accept that different agents have different needs

| Agent | Typical Commands | Lines | % Budget | Strategy |
|-------|------------------|-------|----------|----------|
| CodeDeveloper | 3 commands | 360 | 23% | Minimal prompts (60 lines each) |
| ProjectManager | 2 commands | 220 | 14% | Can use fuller prompts (110 lines each) |
| CodeReviewer | 2 commands | 240 | 15% | Can use fuller prompts (120 lines each) |
| UserListener | 1 command | 90 | 6% | Can use full prompt (90 lines) |

**Pros**:
- Tailored to actual usage patterns
- Realistic about tradeoffs

**Cons**:
- Inconsistent prompt sizes
- Complex to manage

---

### Option 4: Compressed Prompt Format

**Concept**: Use ultra-compact notation

```markdown
# implement

Purpose: Load spec → gen code → track files
Params: task_id:str
Query: `SELECT * FROM specs_task WHERE task_id=?`
Workflow: Load→Gen→Track→Return
Result: ImplementResult(files:List[str], status:str)
Errors: SpecNotFound→CheckID | CodeGenFail→ReviewSpec
Ex: `impl=implement("T-42")` → `ImplementResult(["a.py"],"ok")`
```

**Size**: 30-40 lines per command
**Loading 3**: 120 lines = **8% context** ✅

**Pros**:
- Maximum compression
- Leaves room for task context

**Cons**:
- ❌ Hard to read/maintain
- ❌ May confuse AI
- ❌ No implementation guidance

---

## My Honest Recommendation

### Hybrid Approach: Minimal Core + Optional Examples

**Structure**:
```
.claude/commands/
├── code_developer/
│   ├── implement.md          # 60 lines - Essential only
│   ├── implement_examples.md # 60 lines - Loaded when needed
│   ├── test.md               # 55 lines
│   ├── test_examples.md      # 55 lines
│   └── finalize.md           # 50 lines
```

**Loading strategy**:
```python
# Default: Load core only
prompts = ["implement", "test", "finalize"]  # 165 lines = 10%

# If AI struggles or user requests examples:
prompts.append("implement_examples")  # +60 lines = 14%
```

**Validation**:
- **Normal execution**: 165 lines (10%) + 200 lines (task/code) = 365 lines (23%) ✅
- **With examples**: 225 lines (14%) + 200 lines (task/code) = 425 lines (27%) ✅
- **All examples**: 330 lines (21%) + 200 lines (task/code) = 530 lines (33%) ⚠️

**Compromise**:
- ✅ Works for normal execution
- ✅ Examples available when truly needed
- ⚠️ Loading all examples still pushes budget
- ✅ But that's rare - only when AI is stuck

---

## Core Prompt Template (60 lines)

```markdown
# implement

## Purpose
Implement task from specification: load spec, generate code, track files.

## Parameters
```yaml
task_id: str  # Required, format: TASK-N-M
auto_test: bool = true  # Run tests after implementation
```

## Workflow
1. Load: `SELECT spec_id, description, files FROM specs_task WHERE task_id=?`
2. Generate code based on spec requirements
3. Write/modify files as specified
4. Track all file changes
5. Return ImplementResult

## Database
```sql
-- Load task
SELECT st.spec_id, st.description, st.metadata,
       ts.dependencies, ts.complexity_score
FROM specs_task st
JOIN technical_spec ts ON st.spec_id = ts.spec_id
WHERE st.task_id = ?
```

## Result
```python
@dataclass
class ImplementResult:
    files_changed: List[str]
    spec_id: str
    status: str  # "success" | "partial" | "failed"
    metadata: dict
```

## Errors
| Error | Cause | Action |
|-------|-------|--------|
| SpecNotFound | Invalid task_id | Verify task exists in DB |
| CodeGenFailed | Spec unclear | Review spec, ask architect |
| FileWriteError | Permission denied | Check file permissions |

## Example
```python
result = implement(task_id="TASK-42")
# ImplementResult(
#   files_changed=["auth.py", "test_auth.py"],
#   spec_id="SPEC-100",
#   status="success"
# )
```

## DB Connection
Use: `with get_connection() as conn:` (auto-pooled)

## Related
- test() - Validate implementation
- finalize() - Quality checks + commit

(Total: ~60 lines)
```

---

## Examples File Template (60 lines)

```markdown
# implement - Examples & Patterns

## Example 1: Simple Implementation
```python
result = implement(task_id="TASK-42")
assert result.status == "success"
assert len(result.files_changed) == 2
```

## Example 2: With Auto-Test Disabled
```python
result = implement(task_id="TASK-43", auto_test=False)
# Implement only, skip testing
```

## Example 3: Handling Failures
```python
result = implement(task_id="TASK-44")
if result.status == "failed":
    print(f"Error: {result.metadata['error']}")
    # Review spec or ask for clarification
```

## Pattern: Multi-File Implementation
When spec requires multiple files:
1. Generate all files first
2. Ensure imports are correct
3. Track all in files_changed
4. Test as a unit

## Pattern: Database Schema Changes
When implementing DB changes:
1. Create migration file
2. Update models
3. Add to files_changed
4. Test migrations separately

## Pattern: Error Recovery
If CodeGenFailed:
1. Check spec clarity
2. Verify dependencies available
3. Consult architect if needed
4. Retry with clarified spec

## Common Issues
- Missing dependencies: Check spec.dependencies
- Unclear requirements: Spec may need architect review
- File conflicts: Coordinate with other tasks

## Performance Tips
- Use spec.complexity_score to estimate time
- High complexity (>7): Consider POC first
- Simple tasks (<3): Direct implementation

(Total: ~60 lines)
```

---

## Final Recommendation

**Use Minimal Core + Optional Examples**:

1. **Create 25 core prompts** (60 lines each)
   - Essential information only
   - One basic example
   - Clear and focused

2. **Create 25 example files** (60 lines each)
   - Detailed patterns
   - Edge cases
   - Troubleshooting
   - Load only when needed

3. **Smart loading logic**:
   - Default: Load core prompts only
   - On error: Load relevant examples
   - User request: Load examples

**Total files**: 50 (25 cores + 25 examples)
**Normal context**: 10-15% per agent ✅
**With examples**: 20-27% per agent ✅

---

**Status**: 🎯 **REALISTIC ASSESSMENT**
**Recommendation**: 50 files (25 core + 25 examples), lazy load examples
**Normal usage**: 10-15% context ✅
**With help**: 20-27% context ✅
