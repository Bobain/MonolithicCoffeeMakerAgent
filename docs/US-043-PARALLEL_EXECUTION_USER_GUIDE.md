# US-043: Parallel Agent Execution User Guide

**Last Updated**: 2025-10-21
**Status**: ✅ Production Ready
**Related**: SPEC-108, PRIORITY 23

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding Parallel Execution](#understanding-parallel-execution)
3. [CLI Commands](#cli-commands)
4. [Monitoring Parallel Work](#monitoring-parallel-work)
5. [When to Use Parallel Execution](#when-to-use-parallel-execution)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

---

## Quick Start

### Start Orchestrator (Handles Parallelization Automatically)

```bash
# Start orchestrator - it automatically detects parallelization opportunities
poetry run orchestrator start

# Output:
🚀 Starting Orchestrator Continuous Work Loop
   Poll interval: 30s
   Spec backlog target: 3
   Max retries: 3

Press Ctrl+C to stop gracefully
```

The orchestrator will:
1. Poll ROADMAP every 30 seconds
2. Detect independent priorities that can run in parallel
3. Automatically spawn parallel code_developer instances
4. Monitor progress and merge when complete

### Check Parallel Execution Status

```bash
poetry run orchestrator status

# Output:
📊 Orchestrator Status
============================================================
Last ROADMAP Update: 2025-10-21 08:51:08

Active Tasks: 3
  - US-043: Parallel execution docs (agent: code_developer, PID: 12345)
  - US-044: Refactoring workflow (agent: code_developer, PID: 12346)
  - US-045: Context-upfront (agent: code_developer, PID: 12347)

Running Agents: 3
  - PID 12345: code_developer (worktree: wt043)
  - PID 12346: code_developer (worktree: wt044)
  - PID 12347: code_developer (worktree: wt045)

💻 Resources:
   CPU: 45.2%
   Memory: 3.1 GB / 16 GB (19.4%)
   Disk: 42.3 GB free

Speedup: 3x faster than sequential execution! 🎉
```

### Monitor in Real-Time Dashboard

```bash
poetry run orchestrator dashboard

# Launches interactive dashboard showing:
# - All running agents
# - Task progress bars
# - Resource usage graphs
# - Estimated completion times
```

---

## Understanding Parallel Execution

### What Is Parallel Execution?

Instead of working on one priority at a time (sequential), multiple agents work on different priorities **simultaneously** (parallel).

**Sequential Execution** (Before):
```
Time 0:   Start US-043 (30 min)
Time 30:  Start US-044 (30 min)
Time 60:  Start US-045 (30 min)
Time 90:  All complete

Total: 90 minutes
```

**Parallel Execution** (Now):
```
Time 0:   Start all 3 simultaneously
          - US-043 (code_developer in wt043)
          - US-044 (code_developer in wt044)
          - US-045 (code_developer in wt045)
Time 30:  All 3 complete

Total: 30 minutes
Speedup: 3x faster! 🎉
```

### Why Is It Safe?

Thanks to our comprehensive enforcement system:

1. **File Ownership** (CFR-001, US-038)
   - Each agent owns specific directories
   - No two agents modify the same files
   - See `docs/AGENT_OWNERSHIP.md` for ownership matrix

2. **Singleton Enforcement** (CFR-000, US-035)
   - Each agent type runs only ONE instance at a time
   - Within each git worktree, singleton is enforced
   - Different worktrees = different processes = no conflicts

3. **Git Worktrees**
   - Each parallel instance works in its own worktree
   - Isolated file systems (different directories)
   - Clean merges because different files modified

### Example: Safe Parallel Execution

```
Main repo: /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt043/

Worktree 1: /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt043/
  - Branch: roadmap-043
  - Agent: code_developer
  - Working on: US-043 (parallel execution docs)
  - Modifies: docs/US-043-*.md

Worktree 2: /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt044/
  - Branch: roadmap-044
  - Agent: code_developer
  - Working on: US-044 (refactoring workflow)
  - Modifies: coffee_maker/refactor/analyzer.py

Worktree 3: /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt045/
  - Branch: roadmap-045
  - Agent: code_developer
  - Working on: US-045 (context-upfront)
  - Modifies: coffee_maker/context/provider.py

No file overlap = No conflicts! ✅
```

---

## CLI Commands

### Start Orchestrator

```bash
# Default configuration
poetry run orchestrator start

# Custom configuration
poetry run orchestrator start \
    --poll-interval 60 \      # Check ROADMAP every 60 seconds
    --spec-backlog 5 \         # Keep 5 specs ahead
    --max-retries 3            # Retry failed tasks 3 times
```

**Options**:
- `--poll-interval`: How often to check ROADMAP (default: 30s)
- `--spec-backlog`: Number of specs to keep prepared (default: 3)
- `--max-retries`: Retry attempts for failed tasks (default: 3)

### Check Status

```bash
# Quick status check
poetry run orchestrator status

# Outputs:
# - Active tasks (what's running)
# - Running agents (PIDs, worktrees)
# - Resource usage (CPU, memory, disk)
# - Speedup metrics
```

### View Dashboard

```bash
# Launch interactive dashboard
poetry run orchestrator dashboard

# Dashboard shows:
# - Real-time task progress
# - Resource graphs
# - Agent activity timeline
# - Estimated completion times
```

### Generate Activity Summary

```bash
# Summary of recent work
poetry run orchestrator activity-summary

# Outputs:
# - Completed tasks (last 24 hours)
# - Active tasks (currently running)
# - Queued tasks (waiting to start)
# - Performance metrics (speedup, efficiency)
```

### Stop Orchestrator

```bash
# Graceful shutdown (waits for tasks to complete)
poetry run orchestrator stop

# Force shutdown (immediate, may lose work)
# Use Ctrl+C while orchestrator is running
```

---

## Monitoring Parallel Work

### Real-Time Status

The `orchestrator status` command provides instant visibility:

```bash
$ poetry run orchestrator status

📊 Orchestrator Status
============================================================

Active Tasks: 3
  ┌─────────────────────────────────────────────────────┐
  │ US-043: Parallel execution docs                     │
  │ Agent: code_developer (wt043)                       │
  │ Status: Running (75% complete, ~5 min remaining)    │
  │ PID: 12345                                          │
  └─────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │ US-044: Refactoring workflow                        │
  │ Agent: code_developer (wt044)                       │
  │ Status: Running (40% complete, ~10 min remaining)   │
  │ PID: 12346                                          │
  └─────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │ US-045: Context-upfront                             │
  │ Agent: code_developer (wt045)                       │
  │ Status: Running (90% complete, ~2 min remaining)    │
  │ PID: 12347                                          │
  └─────────────────────────────────────────────────────┘

💻 Resources:
   CPU: 45.2% (under threshold ✅)
   Memory: 3.1 GB / 16 GB (19.4%) (under threshold ✅)
   Disk: 42.3 GB free

⚡ Performance:
   Speedup: 3x faster than sequential
   Estimated total time: 10 minutes (vs 30 min sequential)
   Time saved: 20 minutes 🎉
```

### Dashboard Monitoring

For longer-running work, use the interactive dashboard:

```bash
$ poetry run orchestrator dashboard
```

The dashboard displays:

1. **Agent Activity Timeline**
   - Visual timeline of agent work
   - Color-coded by status (running, completed, failed)
   - Hover for details

2. **Resource Usage Graphs**
   - Real-time CPU, memory, disk graphs
   - Historical trends
   - Threshold indicators

3. **Task Progress Bars**
   - Individual progress for each task
   - Estimated completion times
   - Dependencies visualization

4. **Speedup Metrics**
   - Current speedup vs sequential
   - Historical speedup trends
   - Cumulative time saved

---

## When to Use Parallel Execution

### ✅ Perfect for Parallel Execution

These scenarios benefit from parallel execution:

1. **Multiple Independent Features**
   - Different code modules
   - Different documentation sections
   - Different test suites

   Example:
   ```
   US-043: Parallel execution docs (docs/)
   US-044: Refactoring workflow (coffee_maker/refactor/)
   US-045: Context-upfront (coffee_maker/context/)

   All modify different files = Perfect for parallel! ✅
   ```

2. **Different Agent Types**
   - code_developer + project_manager
   - code_developer + architect
   - architect + project_manager

   Example:
   ```
   code_developer: Implementing US-043 (coffee_maker/)
   project_manager: Writing strategic spec (docs/roadmap/)
   architect: Designing US-046 (docs/architecture/)

   Different files, different agents = Perfect for parallel! ✅
   ```

3. **Documentation + Implementation**
   - One agent writes docs
   - Another implements code
   - Assistant creates demos

   Example:
   ```
   code_developer: Implementing feature (coffee_maker/)
   project_manager: Updating ROADMAP (docs/roadmap/)
   assistant: Creating demo (read-only, no files)

   No conflicts = Perfect for parallel! ✅
   ```

### ❌ NOT Suitable for Parallel Execution

These scenarios must run sequentially:

1. **Dependent Tasks**
   - Task B needs results from task A
   - Must wait for A to complete first

   Example:
   ```
   US-046: Design architecture spec (architect)
   US-047: Implement based on spec (code_developer)

   US-047 depends on US-046 = Must run sequentially ❌
   ```

2. **Same File Modifications**
   - Both tasks modify the same file
   - Would cause merge conflicts

   Example:
   ```
   US-048: Add function to utils.py
   US-049: Modify same function in utils.py

   Same file = Must run sequentially ❌
   ```

3. **Resource Constraints**
   - System under heavy load (CPU > 80%, Memory > 80%)
   - Already running max parallel instances

   Example:
   ```
   3 instances running, CPU at 85%

   System overloaded = Queue for later ❌
   ```

---

## Troubleshooting

### Issue: Parallel Execution Not Starting

**Symptom**: Orchestrator runs tasks sequentially instead of parallel

**Possible Causes**:

1. **Resource Constraints**
   ```bash
   # Check resource usage
   poetry run orchestrator status

   # If CPU > 80% or Memory > 80%, parallelization disabled
   # Solution: Wait for resources to free up, or stop other processes
   ```

2. **Dependent Tasks**
   ```bash
   # Check ROADMAP for dependencies
   # Tasks with "Depends on: US-XXX" must wait
   # Solution: Let dependency complete first
   ```

3. **File Conflicts**
   ```bash
   # Check if tasks modify same files
   # Look at file ownership in docs/AGENT_OWNERSHIP.md
   # Solution: Ensure tasks modify different files
   ```

### Issue: Worktree Merge Conflicts

**Symptom**: Error message "⚠️ Merge conflict in roadmap-XXX"

**Solution**:

```bash
# 1. Check the conflict
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt043
git status

# 2. Resolve manually
git checkout roadmap
git merge roadmap-XXX

# 3. Fix conflicts in editor
# 4. Complete merge
git add .
git commit -m "Resolve merge conflict for US-XXX"

# 5. Notify orchestrator
poetry run orchestrator status
```

### Issue: High Resource Usage

**Symptom**: System slow, CPU/Memory > 80%

**Solution**:

```bash
# 1. Check current parallel count
poetry run orchestrator status

# 2. System automatically reduces parallel instances
# Wait for it to scale down (monitors every 30s)

# 3. Or manually stop orchestrator and restart with lower max
poetry run orchestrator stop
poetry run orchestrator start --max-parallel 2
```

### Issue: Worktree Cleanup Fails

**Symptom**: Old worktrees remain after completion

**Solution**:

```bash
# 1. List worktrees
git worktree list

# 2. Manually remove stuck worktrees
git worktree remove /path/to/worktree --force

# 3. Restart orchestrator
poetry run orchestrator stop
poetry run orchestrator start
```

---

## Best Practices

### 1. Let Orchestrator Manage Parallelization

**Don't**: Manually spawn parallel instances
**Do**: Let orchestrator detect opportunities automatically

```bash
# ✅ Good: Let orchestrator decide
poetry run orchestrator start

# ❌ Avoid: Manual parallel management (unless debugging)
git worktree add ../wt043 roadmap-043
poetry run code-developer --worktree wt043
```

### 2. Monitor Resource Usage

Keep an eye on system resources:

```bash
# Check periodically
poetry run orchestrator status

# If resources consistently high:
# - Reduce max_parallel
# - Close other applications
# - Upgrade system resources
```

### 3. Design for Independence

When creating user stories, design them to be **independent**:

**Good** (Independent):
```
US-043: Parallel execution docs (docs/)
US-044: Refactoring workflow (coffee_maker/refactor/)
US-045: Context-upfront (coffee_maker/context/)
```

**Bad** (Dependent):
```
US-043: Design API (docs/architecture/)
US-044: Implement API (coffee_maker/api/)  # Depends on US-043
US-045: Test API (tests/api/)               # Depends on US-044
```

### 4. Use Clear File Ownership

Follow file ownership rules in `docs/AGENT_OWNERSHIP.md`:

- code_developer: `coffee_maker/`, `tests/`, `.claude/`
- project_manager: `docs/roadmap/`, `docs/*.md`
- architect: `docs/architecture/`, `pyproject.toml`

Clear ownership = Clean merges = Safe parallelization

### 5. Monitor Speedup Metrics

Track your productivity gains:

```bash
# Weekly review
poetry run orchestrator activity-summary

# Look for:
# - Average speedup (target: 2-4x)
# - Time saved per week
# - Parallelization rate (% of time running parallel)
```

---

## FAQ

### Q: How many parallel instances can I run?

**A**: Default is 4 instances. This is configurable but depends on your system:

- **4 instances**: Modern laptop (8+ cores, 16GB+ RAM)
- **2-3 instances**: Older laptop (4 cores, 8GB RAM)
- **6+ instances**: Workstation (16+ cores, 32GB+ RAM)

The system automatically adjusts based on resource usage.

### Q: What happens if one parallel instance fails?

**A**: Other instances continue running! The system handles failures gracefully:

1. Failed instance logs error
2. Worktree marked as "failed"
3. Other instances unaffected
4. Orchestrator retries failed task (up to max_retries)
5. User notified of failure

### Q: Can I manually trigger parallel execution?

**A**: Generally not needed (orchestrator handles it), but yes:

```bash
# Advanced: Manual parallel spawn (for debugging)
poetry run orchestrator spawn-parallel --priority 43
```

### Q: How do I know if tasks are independent?

**A**: Check three things:

1. **File ownership**: Do they modify different files?
   - See `docs/AGENT_OWNERSHIP.md`

2. **Dependencies**: Does one depend on the other?
   - Check ROADMAP "Depends on" section

3. **Agent types**: Are they different agent types?
   - Different agents = Usually safe for parallel

### Q: What's the speedup for my workload?

**A**: Depends on independence of tasks:

| Scenario | Speedup |
|----------|---------|
| 4 fully independent tasks | 4x faster |
| 3 independent tasks | 3x faster |
| 2 independent + 1 dependent | 2x faster |
| All dependent tasks | 1x (no benefit) |

Check your actual speedup:
```bash
poetry run orchestrator activity-summary
# Look for "Average speedup" metric
```

### Q: Can different agent types run in parallel?

**A**: Yes! This is the **most common** parallel scenario:

```
code_developer + project_manager + architect + assistant
= 4 agents working simultaneously = 4x speedup! 🎉
```

Each agent type owns different files, so **no conflicts**.

### Q: What if I need to stop parallel execution?

**A**: Stop orchestrator gracefully:

```bash
# Graceful stop (waits for current tasks)
poetry run orchestrator stop

# Or press Ctrl+C while orchestrator running
```

Worktrees are automatically cleaned up when stopped.

---

## Quick Reference Card

### Essential Commands

```bash
# Start orchestrator (handles parallelization)
poetry run orchestrator start

# Check status
poetry run orchestrator status

# View dashboard
poetry run orchestrator dashboard

# Activity summary
poetry run orchestrator activity-summary

# Stop orchestrator
poetry run orchestrator stop
```

### Resource Thresholds

| Resource | Threshold | Action |
|----------|-----------|--------|
| CPU | < 50% | Spawn 4 instances |
| CPU | 50-70% | Spawn 3 instances |
| CPU | 70-80% | Spawn 2 instances |
| CPU | > 80% | Sequential only |
| Memory | < 50% | Spawn 4 instances |
| Memory | > 80% | Reduce parallelism |

### File Ownership Quick Reference

| Agent | Owns | Examples |
|-------|------|----------|
| code_developer | Implementation | `coffee_maker/`, `tests/`, `.claude/` |
| project_manager | Strategic docs | `docs/roadmap/`, `docs/*.md` |
| architect | Architecture | `docs/architecture/`, `pyproject.toml` |
| assistant | None | Read-only (demos, bug reports) |

---

## Support

**Documentation**:
- Implementation Guide: `docs/US-043-PARALLEL_EXECUTION_IMPLEMENTATION_GUIDE.md`
- Testing Guide: `docs/US-043-PARALLEL_EXECUTION_TESTING_GUIDE.md`
- Agent Ownership: `docs/AGENT_OWNERSHIP.md`

**Specifications**:
- SPEC-108: Technical specification
- US-108: Strategic requirement
- PRIORITY 23: Implementation priority

**Troubleshooting**:
- Check orchestrator logs: `data/orchestrator.db`
- Check git status: `git worktree list`
- Check resources: `poetry run orchestrator status`

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-21

Enjoy 3-4x faster delivery with parallel agent execution! 🎉
