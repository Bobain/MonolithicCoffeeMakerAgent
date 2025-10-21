# Skill: Parallel Agent Execution

**Name**: `parallel-execution`
**Owner**: orchestrator
**Purpose**: Execute multiple code_developer instances in parallel using git worktrees to increase velocity by 75-150%
**Priority**: CRITICAL - Enables 2-3x development speed for independent tasks

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ When Acceleration Dashboard shows 2+ parallelizable tasks
- ✅ When ROADMAP has multiple independent priorities marked as "Planned"
- ✅ When orchestrator detects idle time and available tasks
- ✅ After completing current priority and evaluating next work

**AVOID** in these situations:
- ❌ When tasks have file conflicts (architect will warn)
- ❌ When system resources are constrained (CPU >80%, Memory >80%)
- ❌ When only 1 task available
- ❌ When tasks are sequential dependencies

**Example Trigger**:
```python
# orchestrator: After completing a priority
current_priority_complete = True
roadmap_tasks = read_roadmap()
parallelizable_tasks = [t for t in roadmap_tasks if t.status == "Planned"]

if len(parallelizable_tasks) >= 2:
    # Use parallel-execution skill
    result = execute_parallel_batch(parallelizable_tasks[:3])
```

---

## Skill Execution Steps

### Prerequisites Check

**Before executing, verify**:
1. ✅ Git 2.5+ installed (`git --version`)
2. ✅ On roadmap branch (`git branch --show-current`)
3. ✅ No uncommitted changes (`git status`)
4. ✅ At least 2 parallelizable tasks in ROADMAP
5. ✅ System resources available (CPU <60%, Memory <60%)

**Commands**:
```bash
# Check git version
git --version  # Must be 2.5+

# Check current branch
git branch --show-current  # Should be "roadmap"

# Check for uncommitted changes
git status --porcelain  # Should be empty

# Check system resources
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

---

### Step 1: Identify Parallelizable Tasks

**Inputs Needed**:
- `$ROADMAP_PATH`: Path to ROADMAP.md (default: `docs/roadmap/ROADMAP.md`)
- `$MAX_INSTANCES`: Maximum parallel instances (default: 2, max: 3)

**Actions**:

**1. Read ROADMAP**:
```python
from pathlib import Path

roadmap_path = Path("docs/roadmap/ROADMAP.md")
content = roadmap_path.read_text()

# Find all "📝 Planned" priorities
import re
planned_pattern = r"### PRIORITY (\d+):.*?📝 Planned"
planned_priorities = re.findall(planned_pattern, content)
```

**2. Filter candidates**:
```python
# Get first N planned priorities (where N = MAX_INSTANCES)
max_instances = 2  # Default: 2 parallel instances
candidate_priorities = [int(p) for p in planned_priorities[:max_instances + 1]]
```

**3. Example output**:
```python
# Found 3 candidates for parallel execution:
# PRIORITY 65: Recipe Management
# PRIORITY 66: Notification System
# PRIORITY 67: CLI Improvements
candidate_priorities = [65, 66, 67]
```

---

### Step 2: Validate Task Separation (Ask Architect)

**Inputs Needed**:
- `$PRIORITY_IDS`: List of priority numbers to validate (e.g., [65, 66, 67])

**Actions**:

**1. Call architect's task-separator skill**:
```python
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

coordinator = ParallelExecutionCoordinator()

# Validate task separation
validation_result = coordinator._validate_task_separation([65, 66, 67])
```

**2. Analyze result**:
```python
if not validation_result["valid"]:
    print(f"❌ Cannot parallelize: {validation_result['reason']}")
    print(f"Conflicts: {validation_result['conflicts']}")
    # STOP: Run sequentially instead
else:
    print(f"✅ Found {len(validation_result['independent_pairs'])} independent pairs")
    print(f"Independent pairs: {validation_result['independent_pairs']}")
    # CONTINUE: Safe to parallelize
```

**3. Example successful validation**:
```json
{
  "valid": true,
  "independent_pairs": [
    [65, 66],
    [65, 67],
    [66, 67]
  ],
  "conflicts": {},
  "task_file_map": {
    "65": ["coffee_maker/recipes.py", "tests/test_recipes.py"],
    "66": ["coffee_maker/notifications.py", "tests/test_notifications.py"],
    "67": ["coffee_maker/cli.py", "tests/test_cli.py"]
  }
}
```

**4. Example validation failure**:
```json
{
  "valid": false,
  "reason": "Tasks 65 and 66 have file conflicts",
  "independent_pairs": [[65, 67]],
  "conflicts": {
    "[65, 66]": ["coffee_maker/database.py"]
  }
}
```

**Output**: Validation result with independent pairs or conflict report

---

### Step 3: Execute Parallel Batch

**Inputs Needed**:
- `$PRIORITY_IDS`: Validated priority IDs (e.g., [65, 66, 67])
- `$AUTO_APPROVE`: Whether to auto-approve code_developer actions (default: false)
- `$MAX_INSTANCES`: Maximum parallel instances (default: 2)

**Actions**:

**1. Initialize coordinator**:
```python
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

coordinator = ParallelExecutionCoordinator(
    repo_root=Path.cwd(),
    max_instances=2,  # 2 parallel instances
    auto_merge=True   # Auto-merge clean merges
)
```

**2. Execute parallel batch**:
```python
result = coordinator.execute_parallel_batch(
    priority_ids=[65, 66, 67],
    auto_approve=False  # Require user approval
)
```

**3. Monitor execution**:
```python
# Coordinator automatically:
# - Creates worktrees (MonolithicCoffeeMakerAgent-wt65, -wt66, -wt67)
# - Spawns code_developer in each worktree
# - Monitors progress every 10 seconds
# - Merges completed work to roadmap branch
# - Cleans up worktrees when done

# Monitor via logs:
import logging
logging.basicConfig(level=logging.INFO)
# Coordinator logs all steps automatically
```

**4. Handle result**:
```python
if result["success"]:
    print(f"✅ Parallel execution completed!")
    print(f"Priorities executed: {result['priorities_executed']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Merge results: {result['merge_results']}")
else:
    print(f"❌ Parallel execution failed: {result['error']}")
```

**Example successful result**:
```json
{
  "success": true,
  "priorities_executed": [65, 66],
  "worktrees_created": 2,
  "monitoring_result": {
    "completed": 2,
    "failed": 0,
    "total": 2
  },
  "merge_results": {
    "65": "merged successfully",
    "66": "merged successfully"
  },
  "duration_seconds": 3245.6,
  "start_time": "2025-10-20T10:30:00",
  "end_time": "2025-10-20T11:24:05"
}
```

**Output**: Execution result with completion status

---

### Step 4: Verify Merge Success

**Inputs Needed**:
- `$MERGE_RESULTS`: Merge results from Step 3

**Actions**:

**1. Check merge results**:
```python
merge_results = result["merge_results"]

successful_merges = [
    p for p, status in merge_results.items()
    if status == "merged successfully"
]

failed_merges = [
    p for p, status in merge_results.items()
    if "conflict" in status or "failed" in status
]

print(f"✅ Successful merges: {successful_merges}")
if failed_merges:
    print(f"❌ Failed merges (manual resolution required): {failed_merges}")
```

**2. For failed merges, provide guidance**:
```bash
# Manual merge for conflicts
git checkout roadmap
git merge feature/us-065

# Resolve conflicts
# 1. Open conflicted files
# 2. Resolve markers (<<<<<<, =======, >>>>>>>)
# 3. Stage resolved files
git add .

# 4. Complete merge
git commit

# 5. Clean up feature branch
git branch -D feature/us-065

# 6. Remove worktree manually
git worktree remove ../MonolithicCoffeeMakerAgent-wt65
```

**Output**: List of successful and failed merges

---

### Step 5: Update ROADMAP Status

**Inputs Needed**:
- `$SUCCESSFUL_PRIORITIES`: List of successfully completed priorities

**Actions**:

**1. For each successful priority, update ROADMAP**:
```python
for priority_id in successful_merges:
    # Update status in ROADMAP.md
    # Change "📝 Planned" → "✅ Complete"
    # Add completion date
    pass  # Handled by code_developer instances
```

**Note**: Each code_developer instance updates its own priority status automatically. Orchestrator just verifies all updates occurred.

**2. Verify updates**:
```bash
# Check ROADMAP for status changes
grep "PRIORITY 65\|PRIORITY 66" docs/roadmap/ROADMAP.md
# Should show "✅ Complete"
```

---

### Step 6: Report Results

**Inputs Needed**:
- `$RESULT`: Complete execution result from Step 3

**Actions**:

**1. Generate summary report**:
```python
def generate_summary(result: Dict[str, Any]) -> str:
    """Generate human-readable summary."""
    priorities = result["priorities_executed"]
    duration = result["duration_seconds"]
    completed = result["monitoring_result"]["completed"]
    failed = result["monitoring_result"]["failed"]

    summary = f"""
Parallel Execution Complete ✅

Priorities Executed: {', '.join(map(str, priorities))}
Duration: {duration/3600:.1f} hours
Success Rate: {completed}/{completed + failed} ({100*completed/(completed+failed):.0f}%)

Merge Results:
"""
    for priority_id, status in result["merge_results"].items():
        emoji = "✅" if "success" in status else "❌"
        summary += f"  {emoji} PRIORITY {priority_id}: {status}\n"

    return summary
```

**2. Create notification**:
```python
from coffee_maker.utils.notifications import NotificationManager

notifications = NotificationManager()
notifications.create_notification(
    title="Parallel Execution Complete",
    message=generate_summary(result),
    level="info",
    sound=False,  # No sound for background work (CFR-009)
    agent_id="orchestrator"
)
```

**Output**: Summary report and notification

---

## Example Workflow

### Scenario: Orchestrator Runs 2 Tasks in Parallel

**Context**:
- ROADMAP shows US-065 and US-066 as "Planned"
- Both are independent (no file conflicts)
- System resources available

**Execution**:

```python
from pathlib import Path
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

# Step 1: Identify tasks
priority_ids = [65, 66]

# Step 2: Initialize coordinator
coordinator = ParallelExecutionCoordinator(
    repo_root=Path.cwd(),
    max_instances=2,
    auto_merge=True
)

# Step 3: Execute parallel batch
result = coordinator.execute_parallel_batch(
    priority_ids=priority_ids,
    auto_approve=False
)

# Step 4: Check results
if result["success"]:
    print(f"✅ Completed in {result['duration_seconds']/3600:.1f} hours")
    print(f"Velocity increase: {(6 - result['duration_seconds']/3600) / 6 * 100:.0f}%")
else:
    print(f"❌ Failed: {result['error']}")
```

**Expected Output**:
```
Creating worktrees...
  ✅ Created MonolithicCoffeeMakerAgent-wt65 (branch: feature/us-065)
  ✅ Created MonolithicCoffeeMakerAgent-wt66 (branch: feature/us-066)

Spawning instances...
  ✅ Spawned code_developer for PRIORITY 65 (PID: 12345)
  ✅ Spawned code_developer for PRIORITY 66 (PID: 12346)

Monitoring...
  [10:30] Instance 65: Running (20% complete)
  [10:30] Instance 66: Running (15% complete)
  [11:00] Instance 66: Completed ✅
  [11:15] Instance 65: Completed ✅

Merging...
  ✅ Merged PRIORITY 66 successfully
  ✅ Merged PRIORITY 65 successfully

Cleanup...
  ✅ Removed worktree MonolithicCoffeeMakerAgent-wt65
  ✅ Removed worktree MonolithicCoffeeMakerAgent-wt66

✅ Completed in 0.75 hours
Velocity increase: 87%
```

---

## Success Criteria

**Skill succeeds when**:
- ✅ All selected priorities execute in parallel
- ✅ At least 90% of merges are successful (clean merges)
- ✅ Velocity increase of 75-150% achieved
- ✅ No git repository corruption
- ✅ System resources stay below limits (CPU <80%, Memory <80%)
- ✅ All worktrees cleaned up properly

**Skill fails when**:
- ❌ Task validation fails (architect detects conflicts)
- ❌ Resources unavailable (CPU/Memory too high)
- ❌ Git worktree creation fails
- ❌ All instances fail to spawn
- ❌ Repository corruption detected

---

## Error Handling

### Common Errors

**1. Validation Failure**:
```python
# Error: "Tasks 65 and 66 have file conflicts"
# Solution: Run sequentially instead
result = {"valid": False, "reason": "file conflicts"}
if not result["valid"]:
    print("⚠️  Cannot parallelize, running sequentially")
    for priority_id in [65, 66]:
        run_sequential(priority_id)
```

**2. Resource Exhaustion**:
```python
# Error: "CPU usage too high: 85.2% > 80%"
# Solution: Wait or reduce instances
import time
while cpu_percent() > 60:
    print("⏳ Waiting for resources...")
    time.sleep(30)
```

**3. Merge Conflict**:
```python
# Error: "merge conflict: coffee_maker/database.py"
# Solution: Manual resolution required
merge_results = result["merge_results"]
for priority_id, status in merge_results.items():
    if "conflict" in status:
        print(f"❌ PRIORITY {priority_id} needs manual merge")
        print(f"Run: git merge feature/us-{priority_id:03d}")
```

**4. Instance Crash**:
```python
# Error: code_developer instance crashed (exit code 1)
# Solution: Check logs and retry
worktree_log = f"../MonolithicCoffeeMakerAgent-wt{priority_id}/logs/code_developer.log"
print(f"Check logs: {worktree_log}")
```

---

## Performance Metrics

**Expected Velocity Gains**:
- 2 parallel instances: **+75% faster** (6h → 3.5h)
- 3 parallel instances: **+150% faster** (6h → 2.5h)

**Actual Metrics** (to be measured):
```python
# Before parallel execution
sequential_time = 6.0  # hours for 2 tasks

# After parallel execution
parallel_time = result["duration_seconds"] / 3600  # hours

# Calculate improvement
velocity_increase = (sequential_time - parallel_time) / sequential_time * 100
print(f"Velocity increase: {velocity_increase:.0f}%")
```

**Target Success Metrics**:
- Auto-merge rate: >90%
- CPU usage: <80%
- Memory usage: <80%
- Instance failure rate: <10%

---

## Best Practices

### DO ✅

1. **Always validate task separation** via architect before spawning instances
2. **Check system resources** before starting parallel execution
3. **Monitor progress** regularly (every 10 seconds)
4. **Auto-merge** clean merges automatically
5. **Clean up worktrees** after completion
6. **Limit instances** to 2-3 maximum
7. **Log all events** for debugging

### DON'T ❌

1. **Don't skip validation** - file conflicts cause merge failures
2. **Don't ignore resource limits** - system exhaustion causes crashes
3. **Don't auto-merge conflicts** - too risky, require manual resolution
4. **Don't spawn >3 instances** - diminishing returns + resource pressure
5. **Don't forget cleanup** - stale worktrees cause confusion
6. **Don't parallelize sequential tasks** - wastes effort on conflict resolution

---

## Related Documentation

- [SPEC-108: Parallel Agent Execution](../../../docs/architecture/specs/SPEC-108-parallel-agent-execution.md) - Full technical specification
- [GUIDELINE-008: Git Worktree Best Practices](../../../docs/architecture/guidelines/GUIDELINE-008-git-worktree-best-practices.md) - Worktree usage guide
- [Task Separator Skill](../architect/task-separator/SKILL.md) - Task independence validation
- [US-108 User Story](../../../docs/roadmap/ROADMAP.md#priority-23-us-108) - Original requirement
- [CFR-013: Git Workflow](../../../docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013) - Git branching rules

---

## CLI Commands

**Check parallel execution status**:
```bash
# View coordinator status
poetry run orchestrator parallel-execution --status

# Expected output:
# Active Worktrees: 2
# Worktree 1: PRIORITY 65 (running, 45% complete)
# Worktree 2: PRIORITY 66 (running, 60% complete)
# CPU: 65.2%, Memory: 42.8%
```

**List active worktrees**:
```bash
git worktree list

# Expected output:
# /path/to/MonolithicCoffeeMakerAgent      abc123 [roadmap]
# /path/to/MonolithicCoffeeMakerAgent-wt65 def456 [feature/us-065]
# /path/to/MonolithicCoffeeMakerAgent-wt66 ghi789 [feature/us-066]
```

**Cleanup stale worktrees** (if needed):
```bash
# Remove all worktrees
git worktree list | grep "wt" | awk '{print $1}' | xargs -I {} git worktree remove --force {}

# Prune stale references
git worktree prune
```

---

## Version History

**v1.0** (2025-10-20):
- Initial implementation
- Support for 2-3 parallel instances
- architect task-separator integration
- Auto-merge for clean merges
- Resource monitoring

**Future Enhancements**:
- Distributed execution across machines
- Support for non-code_developer agents
- Smart conflict resolution (LLM-based)
- Web dashboard for monitoring
- Cost tracking per instance

---

**Skill Version**: 1.0
**Last Updated**: 2025-10-20
**Owner**: orchestrator
