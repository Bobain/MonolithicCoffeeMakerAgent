# SPEC-108: Parallel Agent Execution with Git Worktree

**Status**: Implemented

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-20

**Related**: [PRIORITY 23 - US-108](../../roadmap/ROADMAP.md#priority-23-us-108---parallel-agent-execution-with-git-worktree-📝-planned)

**Related ADRs**: None

**Assigned To**: code_developer (implementation), orchestrator (execution)

---

## Executive Summary

This specification describes the technical design for parallel agent execution using git worktrees. The system enables multiple code_developer instances to work simultaneously on independent tasks, increasing development velocity by 75-150%. This is achieved by creating separate git working directories (worktrees) for each agent instance, ensuring complete isolation while sharing the same git repository.

---

## Problem Statement

### Current Situation

Currently, the MonolithicCoffeeMakerAgent system has a fundamental limitation:
- **Singleton Enforcement**: Only ONE instance of each agent type can run at a time (US-035)
- **Sequential Execution**: code_developer works on one task at a time, completing it fully before moving to the next
- **Idle Resources**: While one task is executing, other parallelizable tasks sit idle in the ROADMAP
- **Missed Velocity Opportunity**: Acceleration Dashboard analysis shows 12+ parallelizable tasks available, representing 75-150% potential velocity increase

Example bottleneck:
```
Current State:
Time 0:00 → code_developer starts US-065 (3 hours)
Time 3:00 → code_developer completes US-065
Time 3:01 → code_developer starts US-066 (2 hours)
Time 5:01 → code_developer completes US-066
TOTAL: 5 hours for 2 tasks

Desired State (with parallel execution):
Time 0:00 → Developer Instance 1 starts US-065 (3 hours)
Time 0:00 → Developer Instance 2 starts US-066 (2 hours)
Time 2:00 → Developer Instance 2 completes US-066
Time 3:00 → Developer Instance 1 completes US-065
TOTAL: 3 hours for 2 tasks (40% faster)
```

### Goal

Implement a parallel execution system that:
- Spawns multiple code_developer instances safely using git worktrees
- Validates task independence (no file conflicts)
- Monitors parallel instances
- Merges completed work automatically
- Achieves 75-150% velocity increase (2-3x faster with 2-3 parallel instances)
- Maintains code quality and git workflow integrity

### Non-Goals

What we are explicitly NOT trying to achieve:
- NOT supporting more than 3 parallel instances (resource limits)
- NOT parallelizing tasks with file conflicts (architect validates separation)
- NOT implementing distributed execution across multiple machines
- NOT modifying singleton enforcement within each worktree (one agent per worktree)
- NOT supporting parallel execution of non-code_developer agents (orchestrator only for now)

---

## Requirements

### Functional Requirements

1. **FR-1**: Create git worktrees programmatically from roadmap branch
2. **FR-2**: Spawn code_developer instances in separate worktree directories
3. **FR-3**: Validate task independence using architect's task-separator skill
4. **FR-4**: Monitor multiple agent instances simultaneously
5. **FR-5**: Detect instance completion and failure
6. **FR-6**: Merge completed work back to roadmap branch automatically
7. **FR-7**: Handle merge conflicts gracefully (manual resolution required)
8. **FR-8**: Clean up worktrees after completion
9. **FR-9**: Provide status monitoring for parallel execution
10. **FR-10**: Support configurable max parallel instances (default: 2-3)

### Non-Functional Requirements

1. **NFR-1**: Performance: Achieve 75-150% velocity increase with 2-3 instances
2. **NFR-2**: Resource Safety: Prevent resource exhaustion (CPU <80%, Memory <80%)
3. **NFR-3**: Data Integrity: No git corruption, clean merges >90% of time
4. **NFR-4**: Observability: Log all parallel execution events
5. **NFR-5**: Reliability: Handle instance crashes without corrupting repository
6. **NFR-6**: Scalability: Support up to 3 parallel instances maximum
7. **NFR-7**: Maintainability: Clean code following project style guide

### Constraints

- Must use git worktree feature (requires Git 2.5+)
- Must enforce singleton within each worktree
- Must maintain CFR-013 compliance (all work on roadmap branch or worktree branches)
- Must ask architect for task separation validation
- Budget: No additional infrastructure costs (runs on local machine)

---

## Proposed Solution

### High-Level Approach

The parallel execution system uses git worktrees to create isolated working directories for each agent instance. The orchestrator coordinates the entire workflow:

1. **Task Selection**: Orchestrator identifies parallelizable tasks from ROADMAP
2. **Validation**: Ask architect's task-separator skill to validate independence
3. **Worktree Creation**: Create separate worktrees with feature branches
4. **Instance Spawning**: Launch code_developer in each worktree
5. **Monitoring**: Track progress and resource usage
6. **Merging**: Automatically merge completed work to roadmap branch
7. **Cleanup**: Remove worktrees and feature branches

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                             │
│  (coffee_maker/orchestrator/parallel_execution_coordinator.py)   │
└────────────┬──────────────────────────────────────┬─────────────┘
             │                                       │
             │ 1. Validate                          │ 2. Create
             │    Tasks                             │    Worktrees
             ▼                                       ▼
    ┌────────────────┐                   ┌──────────────────────┐
    │   ARCHITECT     │                   │   WorktreeManager    │
    │ task-separator  │                   │  (git worktree add)  │
    │     skill       │                   └──────────┬───────────┘
    └────────────────┘                               │
                                                     │ 3. Spawn
                                                     ▼
                                  ┌──────────────────────────────────┐
                                  │      PARALLEL INSTANCES          │
                                  ├──────────────────────────────────┤
                                  │ Worktree 1:                      │
                                  │ /path/to/repo-wt1                │
                                  │ → code_developer (US-065)        │
                                  │ → Branch: feature/us-065         │
                                  ├──────────────────────────────────┤
                                  │ Worktree 2:                      │
                                  │ /path/to/repo-wt2                │
                                  │ → code_developer (US-066)        │
                                  │ → Branch: feature/us-066         │
                                  ├──────────────────────────────────┤
                                  │ Worktree 3:                      │
                                  │ /path/to/repo-wt3                │
                                  │ → code_developer (US-067)        │
                                  │ → Branch: feature/us-067         │
                                  └──────────────────────────────────┘
                                                     │
                                                     │ 4. Monitor
                                                     ▼
                                  ┌──────────────────────────────────┐
                                  │    ResourceMonitor               │
                                  │  - CPU usage                     │
                                  │  - Memory usage                  │
                                  │  - Instance status               │
                                  └──────────────────────────────────┘
                                                     │
                                                     │ 5. Merge
                                                     ▼
                                  ┌──────────────────────────────────┐
                                  │   Git Merge to Roadmap Branch    │
                                  │   - Auto-merge if no conflicts   │
                                  │   - Manual if conflicts exist    │
                                  └──────────────────────────────────┘
                                                     │
                                                     │ 6. Cleanup
                                                     ▼
                                  ┌──────────────────────────────────┐
                                  │   Remove Worktrees               │
                                  │   - git worktree remove          │
                                  │   - Delete feature branches      │
                                  └──────────────────────────────────┘
```

### Component Details

#### 1. ParallelExecutionCoordinator

**Location**: `coffee_maker/orchestrator/parallel_execution_coordinator.py`

**Responsibilities**:
- Orchestrate entire parallel execution workflow
- Create and manage git worktrees
- Spawn agent instances
- Monitor progress
- Merge completed work
- Clean up resources

**Key Methods**:
```python
class ParallelExecutionCoordinator:
    def execute_parallel_batch(priority_ids: List[int]) -> Dict[str, Any]
    def _validate_task_separation(priority_ids: List[int]) -> Dict[str, Any]
    def _create_worktrees(priority_ids: List[int]) -> List[WorktreeConfig]
    def _spawn_instances(worktrees: List[WorktreeConfig])
    def _monitor_instances(worktrees: List[WorktreeConfig]) -> Dict[str, Any]
    def _merge_completed_work(worktrees: List[WorktreeConfig]) -> Dict[int, str]
    def _cleanup_worktrees(worktrees: List[WorktreeConfig])
```

#### 2. WorktreeConfig

**Location**: `coffee_maker/orchestrator/parallel_execution_coordinator.py`

**Purpose**: Track worktree state

```python
@dataclass
class WorktreeConfig:
    priority_id: int                      # PRIORITY number
    worktree_path: Path                   # Path to worktree directory
    branch_name: str                      # Git branch name
    process: Optional[subprocess.Popen]   # Running process handle
    status: str                           # pending|running|completed|failed
    start_time: Optional[datetime]        # When started
    end_time: Optional[datetime]          # When completed
```

#### 3. ResourceMonitor

**Location**: `coffee_maker/orchestrator/parallel_execution_coordinator.py`

**Responsibilities**:
- Monitor CPU and memory usage
- Prevent resource exhaustion
- Enforce resource limits

**Key Methods**:
```python
class ResourceMonitor:
    def check_resources_available() -> Tuple[bool, str]
    def get_resource_status() -> Dict[str, Any]
```

**Resource Limits**:
- CPU: <80% usage
- Memory: <80% usage
- Disk: Monitor free space

#### 4. Task Separator Skill (Architect)

**Location**: `.claude/skills/architect/task-separator/task_separator.py`

**Responsibilities**:
- Analyze task independence
- Detect file conflicts
- Generate separation report

**Algorithm**:
1. Read specs for each priority
2. Extract file paths mentioned in specs
3. Find all pairs of priorities
4. For each pair, check for shared files
5. Mark pair as independent if NO shared files
6. Return list of independent pairs + conflict report

**Example Output**:
```python
{
    "valid": True,
    "independent_pairs": [(65, 66), (65, 67), (66, 67)],
    "conflicts": {},
    "task_file_map": {
        65: ["coffee_maker/recipes.py", "tests/test_recipes.py"],
        66: ["coffee_maker/notifications.py", "tests/test_notifications.py"],
        67: ["coffee_maker/cli.py", "tests/test_cli.py"]
    }
}
```

---

## Detailed Design

### 1. Git Worktree Management

**What is a Git Worktree?**

A git worktree is a separate working directory linked to the same git repository. It allows multiple branches to be checked out simultaneously in different directories.

**Example**:
```bash
# Main workspace
/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent
  └── branch: roadmap

# Worktree 1
/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt1
  └── branch: feature/us-065

# Worktree 2
/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt2
  └── branch: feature/us-066
```

**Creating Worktrees**:
```bash
# Create worktree from roadmap branch
git worktree add -b feature/us-065 ../MonolithicCoffeeMakerAgent-wt1 roadmap

# List worktrees
git worktree list
# /path/to/MonolithicCoffeeMakerAgent      abc123 [roadmap]
# /path/to/MonolithicCoffeeMakerAgent-wt1  def456 [feature/us-065]

# Remove worktree
git worktree remove ../MonolithicCoffeeMakerAgent-wt1
git branch -D feature/us-065
```

**Implementation Details**:
```python
def _create_worktrees(self, priority_ids: List[int]) -> List[WorktreeConfig]:
    """Create git worktrees for each priority."""
    worktrees = []

    for priority_id in priority_ids:
        # Naming convention: {repo_name}-wt{priority_id}
        worktree_name = f"{self.repo_root.name}-wt{priority_id}"
        worktree_path = self.repo_root.parent / worktree_name

        # Branch naming: feature/us-{priority_id:03d}
        branch_name = f"feature/us-{priority_id:03d}"

        # Create worktree from roadmap branch
        subprocess.run([
            "git", "worktree", "add",
            "-b", branch_name,
            str(worktree_path),
            "roadmap"
        ], cwd=self.repo_root, check=True)

        worktrees.append(WorktreeConfig(
            priority_id=priority_id,
            worktree_path=worktree_path,
            branch_name=branch_name,
            status="created"
        ))

    return worktrees
```

### 2. Agent Instance Spawning

**Process Spawning**:
```python
def _spawn_instances(self, worktrees: List[WorktreeConfig], auto_approve: bool = False):
    """Spawn code_developer instances in each worktree."""
    for worktree in worktrees:
        # Build command with priority assignment
        cmd = [
            "poetry", "run", "code-developer",
            f"--priority={worktree.priority_id}"
        ]
        if auto_approve:
            cmd.append("--auto-approve")

        # Spawn subprocess in worktree directory
        process = subprocess.Popen(
            cmd,
            cwd=worktree.worktree_path,  # Run in worktree!
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        worktree.process = process
        worktree.status = "running"
        worktree.start_time = datetime.now()
```

**Key Points**:
- Each instance runs in its own worktree directory
- `--priority=N` flag tells code_developer which priority to work on
- Singleton enforcement works within each worktree (AgentRegistry per worktree)
- Instances are completely isolated (separate working directories)

### 3. Monitoring

**Polling Strategy**:
```python
def _monitor_instances(self, worktrees: List[WorktreeConfig], poll_interval: int = 10):
    """Monitor running instances until all complete."""
    while True:
        all_done = True

        for worktree in worktrees:
            if worktree.status == "running" and worktree.process:
                # Check if process finished
                poll_result = worktree.process.poll()

                if poll_result is not None:
                    # Process finished
                    worktree.end_time = datetime.now()

                    if poll_result == 0:
                        worktree.status = "completed"
                    else:
                        worktree.status = "failed"

            if worktree.status == "running":
                all_done = False

        if all_done:
            break

        time.sleep(poll_interval)  # Wait 10 seconds
```

**Status States**:
- `pending`: Worktree created, not started
- `running`: code_developer instance executing
- `completed`: Instance finished successfully (exit code 0)
- `failed`: Instance crashed or returned error code

### 4. Merging Strategy

**Auto-Merge for Clean Merges**:
```python
def _merge_completed_work(self, worktrees: List[WorktreeConfig]):
    """Merge completed work to roadmap branch."""
    for worktree in worktrees:
        if worktree.status != "completed":
            continue  # Skip failed instances

        # Switch to roadmap branch
        subprocess.run(["git", "checkout", "roadmap"], cwd=self.repo_root)

        # Attempt merge
        result = subprocess.run([
            "git", "merge", "--no-ff",
            worktree.branch_name,
            "-m", f"Merge PRIORITY {worktree.priority_id} from parallel execution"
        ], cwd=self.repo_root, capture_output=True)

        if result.returncode == 0:
            logger.info(f"✅ Merged PRIORITY {worktree.priority_id}")
        else:
            logger.error(f"❌ Merge conflict for PRIORITY {worktree.priority_id}")
            # Leave conflict for manual resolution
```

**Merge Conflict Handling**:
- Clean merges: Automatic (>90% expected based on architect validation)
- Conflicts: Log error, notify user for manual resolution
- No automatic conflict resolution (too risky)

### 5. Resource Management

**CPU and Memory Limits**:
```python
class ResourceMonitor:
    def check_resources_available(self) -> Tuple[bool, str]:
        """Check if we can spawn another instance."""
        # Check CPU
        cpu_percent = psutil.cpu_percent(interval=1.0)
        if cpu_percent > self.max_cpu_percent:  # Default: 80%
            return False, f"CPU too high: {cpu_percent:.1f}%"

        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > self.max_memory_percent:  # Default: 80%
            return False, f"Memory too high: {memory.percent:.1f}%"

        return True, "Resources available"
```

**Max Instances Limit**:
- Default: 2 parallel instances
- Configurable up to 3 instances maximum
- Hard limit enforced in ParallelExecutionCoordinator

---

## Workflow Example

### Scenario: Orchestrator Executes 3 Parallel Tasks

**Step 1: Task Selection**
```python
# Orchestrator reads ROADMAP
priority_ids = [65, 66, 67]  # Three tasks to parallelize
```

**Step 2: Validation**
```python
# Ask architect to validate
coordinator = ParallelExecutionCoordinator()
result = coordinator.execute_parallel_batch(priority_ids)

# architect task-separator returns:
# {
#   "valid": True,
#   "independent_pairs": [(65, 66), (65, 67), (66, 67)],
#   "conflicts": {}
# }
```

**Step 3: Create Worktrees**
```bash
# Creates:
git worktree add -b feature/us-065 ../MonolithicCoffeeMakerAgent-wt65 roadmap
git worktree add -b feature/us-066 ../MonolithicCoffeeMakerAgent-wt66 roadmap
git worktree add -b feature/us-067 ../MonolithicCoffeeMakerAgent-wt67 roadmap
```

**Step 4: Spawn Instances**
```python
# Worktree 1:
poetry run code-developer --priority=65  # In wt65 directory

# Worktree 2:
poetry run code-developer --priority=66  # In wt66 directory

# Worktree 3:
poetry run code-developer --priority=67  # In wt67 directory
```

**Step 5: Monitor Progress**
```
Time 0:00 → All 3 instances start
Time 1:30 → Instance 2 (US-066) completes ✅
Time 2:15 → Instance 3 (US-067) completes ✅
Time 3:00 → Instance 1 (US-065) completes ✅
```

**Step 6: Merge Work**
```bash
git checkout roadmap
git merge --no-ff feature/us-066  # ✅ Clean merge
git merge --no-ff feature/us-067  # ✅ Clean merge
git merge --no-ff feature/us-065  # ✅ Clean merge
```

**Step 7: Cleanup**
```bash
git worktree remove ../MonolithicCoffeeMakerAgent-wt65
git worktree remove ../MonolithicCoffeeMakerAgent-wt66
git worktree remove ../MonolithicCoffeeMakerAgent-wt67
git branch -D feature/us-065 feature/us-066 feature/us-067
```

**Result**:
- 3 tasks completed in 3 hours (instead of 6+ hours sequentially)
- 50-100% velocity increase
- All work merged to roadmap branch
- Clean git history

---

## Testing Strategy

### Unit Tests

**Test Coverage** (20+ tests):

1. **WorktreeManager Tests**:
   - ✅ Create worktree with correct branch name
   - ✅ Remove worktree and cleanup branch
   - ✅ List active worktrees
   - ✅ Handle worktree already exists

2. **ResourceMonitor Tests**:
   - ✅ Check CPU threshold
   - ✅ Check memory threshold
   - ✅ Get resource status

3. **TaskSeparator Tests**:
   - ✅ Detect independent tasks
   - ✅ Detect file conflicts
   - ✅ Extract file paths from specs
   - ✅ Handle missing specs

4. **ParallelExecutionCoordinator Tests**:
   - ✅ Execute parallel batch successfully
   - ✅ Handle validation failures
   - ✅ Spawn instances correctly
   - ✅ Monitor instance completion
   - ✅ Merge completed work
   - ✅ Cleanup on errors

### Integration Tests

**Full Workflow Test**:
```python
def test_full_parallel_execution():
    """Test complete parallel execution workflow."""
    # Setup: Create test repository with 3 independent tasks
    priority_ids = [65, 66, 67]

    # Execute
    coordinator = ParallelExecutionCoordinator()
    result = coordinator.execute_parallel_batch(priority_ids)

    # Verify
    assert result["success"] == True
    assert len(result["priorities_executed"]) == 3
    assert result["merge_results"][65] == "merged successfully"
    assert result["merge_results"][66] == "merged successfully"
    assert result["merge_results"][67] == "merged successfully"
```

---

## Performance Metrics

### Expected Results

**Velocity Increase**:
- 2 parallel instances: +75% faster (6h → 3.5h)
- 3 parallel instances: +150% faster (6h → 2.5h)

**Success Metrics**:
- Auto-merge rate: >90% (architect validation ensures independence)
- Resource usage: CPU <80%, Memory <80%
- Instance failure rate: <10%

**Observed Results** (to be updated after deployment):
- TBD: Actual velocity increase
- TBD: Merge success rate
- TBD: Resource usage statistics

---

## Security Considerations

1. **File System Isolation**: Each worktree is isolated, preventing cross-contamination
2. **Git Safety**: All work committed to feature branches, never direct to roadmap
3. **Process Isolation**: subprocess.Popen ensures clean process separation
4. **Resource Limits**: Hard caps prevent DoS from too many instances

---

## Maintenance & Support

### Debugging Parallel Execution

**Check Worktree Status**:
```bash
git worktree list
```

**Check Running Instances**:
```bash
ps aux | grep code-developer
```

**View Instance Logs**:
```bash
# Check logs in each worktree
tail -f ../MonolithicCoffeeMakerAgent-wt65/logs/code_developer.log
```

### Common Issues

**Issue**: Merge conflict during auto-merge
**Solution**: Manual merge required
```bash
git checkout roadmap
git merge feature/us-065  # Shows conflict
# Resolve conflict manually
git add .
git commit
```

**Issue**: Worktree already exists
**Solution**: Clean up stale worktrees
```bash
git worktree remove --force ../MonolithicCoffeeMakerAgent-wt65
git worktree prune
```

**Issue**: Resource exhaustion
**Solution**: Reduce max_instances
```python
coordinator = ParallelExecutionCoordinator(max_instances=2)
```

---

## Future Enhancements

**Phase 2 Improvements**:
1. Distributed execution across multiple machines
2. Support for non-code_developer agents (architect, assistant)
3. Intelligent task scheduling (priority + effort estimation)
4. Smart conflict resolution (LLM-based merge conflict resolver)
5. Web dashboard for monitoring parallel execution
6. Cost tracking per instance
7. Automatic rollback on test failures

---

## References

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [US-108 User Story](../../roadmap/ROADMAP.md#priority-23-us-108)
- [GUIDELINE-008: Git Worktree Best Practices](../guidelines/GUIDELINE-008-git-worktree-best-practices.md)
- [Acceleration Dashboard Analysis](../../roadmap/ROADMAP.md#phase-1)
- [CFR-013: Git Workflow](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013)
- [US-035: Singleton Enforcement](../../roadmap/ROADMAP.md)

---

## Appendix A: Code Locations

**Implementation Files**:
- `coffee_maker/orchestrator/parallel_execution_coordinator.py` - Main coordinator
- `.claude/skills/architect/task-separator/task_separator.py` - Task separation skill
- `coffee_maker/autonomous/daemon_cli.py` - CLI with --priority flag

**Documentation Files**:
- `docs/architecture/specs/SPEC-108-parallel-agent-execution.md` - This file
- `docs/architecture/guidelines/GUIDELINE-008-git-worktree-best-practices.md` - Best practices
- `.claude/skills/orchestrator/parallel-execution/SKILL.md` - Orchestrator skill docs
- `.claude/skills/architect/task-separator/SKILL.md` - Architect skill docs

**Test Files**:
- `tests/orchestrator/test_parallel_execution_coordinator.py`
- `tests/skills/test_task_separator.py`

---

**Document Version**: 1.0
**Last Review**: 2025-10-20
