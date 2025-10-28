# Simplified Approach - Reconsidering Hierarchical Skills

**Date**: 2025-10-28
**Issue**: 150 skill files is over-engineered and complex
**Goal**: Find simpler path to CFR-007 compliance

---

## Reality Check

### My Original Calculation
- 8 agents × ~12 skills each = 96 agent files
- 12 shared skills
- 40+ optional example files
- **Total: ~150 files** ❌ Too complex!

### The Real Problem
Current prompts are 300-500 lines because they include:
- Verbose explanations
- 3-5 detailed examples per prompt
- Background context
- Implementation notes
- Database schemas
- Error handling details
- Best practices
- Related commands

**We don't need complex hierarchy - we need CONCISE prompts!**

---

## Alternative Approaches

### Option 1: Concise Single-File Prompts (SIMPLEST)

**Concept**: Just write tighter prompts!

```
25 commands = 25 prompt files
Each prompt: 120-150 lines (focused, essential only)
```

**Structure per prompt**:
```markdown
# Command: implement

## Purpose (2 lines)
Implement a task from specification

## Parameters (10 lines)
- task_id: string (required)
- auto_test: boolean (default: true)

## Workflow (15 lines)
1. Load spec from database
2. Generate code
3. Track files changed
4. Return result

## Database Query (20 lines)
```sql
SELECT ... FROM specs_task WHERE task_id = ?
```

## Result Object (15 lines)
@dataclass class ImplementResult: ...

## Error Handling (15 lines)
| Error | Recovery |
|-------|----------|
| SpecNotFound | Verify task_id |

## Quick Example (10 lines)
result = implement(task_id="TASK-42")

## Implementation Notes (20 lines)
- Use context manager for DB
- Track file operations
- Return structured result

(Total: ~120 lines)
```

**Agent context usage**:
- Load 3 commands: 3 × 150 = 450 lines = **28%** ✅
- Load 2 commands: 2 × 150 = 300 lines = **19%** ✅

**Pros**:
- ✅ Simple: 25 files total
- ✅ Easy to maintain
- ✅ Clear and focused
- ✅ CFR-007 compliant

**Cons**:
- ⚠️ No detailed examples (link to docs instead)
- ⚠️ Less hand-holding for AI

---

### Option 2: Core + Examples Split (BALANCED)

**Concept**: Split only the optional content

```
25 commands:
├── 25 core prompt files (~120 lines each)
└── 25 example files (~80 lines each, loaded on request)

Total: 50 files
```

**Structure**:
```
.claude/commands/
├── code_developer/
│   ├── implement.md          # 120 lines - Essential
│   ├── implement_examples.md # 80 lines - Optional
│   ├── test.md               # 120 lines
│   ├── test_examples.md      # 80 lines
│   └── finalize.md           # 120 lines
```

**Loading**:
```python
# Normal execution
prompt = load_command("implement")  # 120 lines

# User requests help
examples = load_examples("implement")  # +80 lines if needed
```

**Agent context usage**:
- Normal: 3 × 120 = 360 lines = **23%** ✅
- With examples: 3 × 200 = 600 lines = **38%** ⚠️ (but rare)

**Pros**:
- ✅ Simple: 50 files
- ✅ Examples available when needed
- ✅ CFR-007 compliant for normal usage

**Cons**:
- ⚠️ Loading examples pushes over budget
- ⚠️ Still need to manage 50 files

---

### Option 3: Minimal Hierarchical (TARGETED)

**Concept**: Use hierarchy ONLY for the largest prompts

**Identify problematic prompts** (>400 lines):
- code_reviewer/README.md: 537 lines
- project_manager/create_roadmap_report.md: 462 lines
- code_developer/update_claude_config.md: 455 lines

**Split only these 3-5 largest prompts**:
```
25 commands total
├── 20 commands: Single file (~120-150 lines)
└── 5 commands: Core + 2 sub-skills
    ├── core.md (100 lines)
    ├── sub1.md (60 lines)
    └── sub2.md (60 lines)

Total: 20 + (5 × 3) = 35 files
```

**Pros**:
- ✅ Targeted solution
- ✅ Simple for most commands
- ✅ Hierarchical only where needed

**Cons**:
- ⚠️ Inconsistent structure
- ⚠️ More complex loading logic

---

## My Recommendation: Option 1 (Concise Single-File)

### Why Option 1 is Best

**Simplicity wins**:
- 25 files (one per command)
- Each 120-150 lines
- No complex loading logic
- Easy to understand and maintain

**It actually works**:
- 3 commands loaded = 450 lines = 28% ✅
- 2 commands loaded = 300 lines = 19% ✅
- Most agents only need 2-3 commands max

**Writing technique**:
Instead of including everything in prompts, we:
1. **Be concise** - No verbose explanations
2. **Link to docs** - "See WORKFLOWS.md for examples"
3. **Essential only** - Remove nice-to-have content
4. **Trust the AI** - Claude is smart, doesn't need hand-holding
5. **Use references** - Point to existing docs instead of repeating

---

## Prompt Size Comparison

### Before: Verbose Prompt (462 lines)

```markdown
# Command: create_roadmap_report

## Background Context (50 lines)
The roadmap is the central source of truth...
It contains priorities which have tasks...
Each priority has a status...
[Lots of background]

## Purpose (20 lines)
Create a comprehensive report of roadmap status...
This report helps project managers...
[Verbose explanation]

## Parameters (40 lines)
scope: string
  - Type: string
  - Required: false
  - Default: "all"
  - Valid values: ["all", "active", "completed"]
  - Description: The scope of the report to generate
  - Example: scope="active"
  - Notes: When scope is "all", include all priorities...
[Overly detailed]

## Database Queries (80 lines)
[Full schemas, multiple queries, detailed explanations]

## Examples (150 lines)
### Example 1: Full Report
[50 lines of detailed example]

### Example 2: Active Only
[50 lines]

### Example 3: With Filters
[50 lines]

## Error Handling (60 lines)
[Detailed error scenarios]

## Implementation Notes (62 lines)
[Various tips and tricks]
```

### After: Concise Prompt (140 lines)

```markdown
# Command: create_roadmap_report

## Purpose
Generate markdown report of roadmap status with metrics and health analysis.

## Parameters
```yaml
scope: string = "all"  # "all" | "active" | "completed"
include_metrics: boolean = true
output_path: string = "reports/roadmap-{date}.md"
```

## Workflow
1. Query roadmap priorities by scope
2. Calculate completion metrics
3. Identify blockers and risks
4. Generate markdown report
5. Save to output_path

## Database Query
```sql
SELECT rp.priority_id, rp.title, rp.status,
       rp.progress, rp.assigned_agent
FROM roadmap_priority rp
WHERE rp.status IN (?) -- Filtered by scope
ORDER BY rp.created_at DESC
```

## Metrics Calculated
- Total priorities
- Completion rate (%)
- Blockers count
- Average progress
- Time to completion estimates

## Result Object
```python
@dataclass
class ReportResult:
    report_path: str
    priorities_analyzed: int
    completion_rate: float
    blockers_found: int
    status: str
```

## Error Handling
| Error | Recovery |
|-------|----------|
| NoActivePriorities | Return empty report |
| DatabaseError | Retry with backoff |
| FileWriteError | Check permissions |

## Example
```python
result = create_roadmap_report(scope="active")
# Result: ReportResult(
#   report_path="reports/roadmap-20251028.md",
#   priorities_analyzed=12,
#   completion_rate=0.45,
#   blockers_found=2,
#   status="success"
# )
```

## Report Format
See: docs/WORKFLOWS.md#roadmap-reports for full format specs

## Related
- docs/roadmap/ROADMAP.md - Source data
- update_roadmap() - Modify roadmap
- track_progress() - Update priorities
```

**Reduction**: 462 → 140 lines (70% reduction)

---

## Implementation: Concise Prompt Writing Guidelines

### 1. Purpose (2-5 lines)
One sentence describing what the command does.

### 2. Parameters (10-20 lines)
```yaml
param_name: type = default  # Valid values | Description
```
No verbose explanations - use YAML syntax for clarity.

### 3. Workflow (10-20 lines)
Numbered steps, concise.

### 4. Database Queries (15-30 lines)
Essential SQL only. Reference schema docs for full details.

### 5. Result Object (10-20 lines)
Dataclass definition. Comments inline, not separate explanations.

### 6. Error Handling (10-20 lines)
Table format: Error | Recovery
No verbose explanations.

### 7. Example (10-20 lines)
ONE good example with result.
Link to docs for more: "See WORKFLOWS.md for 5 detailed examples"

### 8. Related (5-10 lines)
Links to docs, related commands.

**Target: 120-150 lines total**

---

## What About Examples?

### Strategy: Link to External Documentation

Instead of:
```markdown
## Examples (150 lines)
[5 detailed examples inline]
```

Do this:
```markdown
## Example
```python
result = implement(task_id="TASK-42")
```

## More Examples
See: docs/WORKFLOWS.md#implement-command
- Simple implementation
- With error handling
- Step-by-step mode
- Integration with test/finalize
- Edge cases and troubleshooting
```

**External docs** (docs/WORKFLOWS.md):
- Can be as long as needed
- Doesn't count toward context budget
- Agent references them only when needed
- User can read them anytime

---

## Validation: Does This Work?

### Scenario: CodeDeveloper implements a feature

**Commands needed**:
1. `implement.md` - 130 lines
2. `test.md` - 120 lines
3. `finalize.md` - 125 lines

**Total**: 375 lines = **23% context** ✅

### Scenario: CodeReviewer full review

**Commands needed**:
1. `analyze.md` - 140 lines
2. `security.md` - 130 lines

**Total**: 270 lines = **17% context** ✅

### Scenario: ProjectManager comprehensive report

**Commands needed**:
1. `roadmap.md` - 125 lines
2. `report.md` - 140 lines

**Total**: 265 lines = **17% context** ✅

**All scenarios pass!** ✅

---

## Recommendation

**Go with Option 1: Concise Single-File Prompts**

### Implementation Plan

1. **Create 25 prompt files** (~120-150 lines each)
   - Focus on essential content only
   - Link to docs for examples
   - Use concise formats (YAML, tables)
   - Trust Claude's intelligence

2. **Update WORKFLOWS.md** with detailed examples
   - 5-10 examples per command
   - Troubleshooting guides
   - Integration patterns
   - Doesn't count toward context

3. **Validate context budget**
   - Test real-world scenarios
   - Ensure <30% per agent

**Total files to create: 25 prompt files** (not 150!)

**Estimated effort**:
- 25 prompts × 30 minutes = ~12 hours (1-2 days)
- Much better than 150 files × 20 minutes = 50 hours!

---

**Status**: 💡 **SIMPLIFIED APPROACH**
**Recommendation**: Option 1 (25 concise prompts, 120-150 lines each)
**Files to create**: 25 (not 150!)
**Context budget**: <30% per agent ✅
