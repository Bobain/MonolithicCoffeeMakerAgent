# Autonomous Scaling Workflow

**Status**: Active ✅
**Version**: 1.0
**Date**: 2025-10-19
**Author**: architect + code_developer (based on user requirements)

---

## Overview

The MonolithicCoffeeMakerAgent system automatically scales parallel execution when the orchestrator detects independent work items. This document describes the complete end-to-end workflow for autonomous scaling, from task evaluation to worktree cleanup.

**Key Principle**: All work happens on the `roadmap` branch or temporary `roadmap-*` branches for parallel execution (CFR-013 compliant).

---

## Participants

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **orchestrator** | Coordinator | Detects workload, creates worktrees, spawns agents, monitors progress, notifies architect, cleans up |
| **architect** | Task Evaluator + Merger | Evaluates task independence with task-separator skill, merges completed work from worktrees back to roadmap |
| **code_developer** | Implementer | Implements features in assigned worktree, runs tests, commits work |
| **code-reviewer** | Quality Assurance | Reviews code in worktree, reports issues to architect via notifications |

---

## Complete Workflow

### Phase 1: Task Evaluation & Worktree Creation

**Trigger**: Orchestrator detects multiple planned priorities in ROADMAP with specs ready

**Steps**:

1. **Orchestrator analyzes ROADMAP**
   ```python
   # In continuous_work_loop.py _work_cycle()
   # Step 1: Poll ROADMAP for changes
   roadmap_updated = self._poll_roadmap()

   # Identify next 2-3 PLANNED priorities with specs
   planned_with_specs = [p for p in priorities if p["status"] == "📝" and p["has_spec"]][:3]
   ```

2. **Orchestrator requests architect evaluation**
   ```python
   # Orchestrator spawns architect with task-separator skill
   result = self.agent_mgmt.execute(
       action="spawn_architect",
       task_type="task_separator",
       priorities=planned_with_specs,  # US-104, US-105, US-106
       auto_approve=True,
   )
   ```

3. **Architect evaluates task independence**
   ```bash
   # architect uses task-separator skill
   # Analyzes specs for:
   # - Shared files (conflicts)
   # - Shared data structures (conflicts)
   # - API dependencies (blocking)
   # - Execution order requirements

   # Returns:
   # {
   #   "US-104": {"independent": true, "can_parallel": true},
   #   "US-105": {"independent": true, "can_parallel": true},
   #   "US-106": {"independent": false, "blocking_on": "US-105"}
   # }
   ```

4. **Orchestrator creates git worktrees** (if tasks are independent)
   ```bash
   # Create worktree directories
   mkdir -p /tmp/worktrees

   # Create worktree 1 for US-104
   git worktree add /tmp/worktrees/wt1 -b roadmap-wt1 roadmap

   # Create worktree 2 for US-105
   git worktree add /tmp/worktrees/wt2 -b roadmap-wt2 roadmap

   # Copy .env to worktrees
   cp .env /tmp/worktrees/wt1/.env
   cp .env /tmp/worktrees/wt2/.env

   # Verify CFR-013 compliance
   cd /tmp/worktrees/wt1 && git branch --show-current
   # Output: roadmap-wt1 ✅ (allowed by CFR-013 extension)
   ```

5. **Orchestrator logs worktree assignments**
   ```python
   logger.info("🌿 Created worktrees for parallel execution:")
   logger.info("  - /tmp/worktrees/wt1 (roadmap-wt1) → US-104")
   logger.info("  - /tmp/worktrees/wt2 (roadmap-wt2) → US-105")
   ```

---

### Phase 2: Parallel Execution

**Trigger**: Worktrees created, tasks assigned

**Steps**:

1. **Orchestrator spawns code_developer instances**
   ```python
   # Spawn code_developer for US-104 in wt1
   result1 = self.agent_mgmt.execute(
       action="spawn_code_developer",
       priority_number=104,
       worktree_path="/tmp/worktrees/wt1",
       auto_approve=True,
   )

   # Spawn code_developer for US-105 in wt2
   result2 = self.agent_mgmt.execute(
       action="spawn_code_developer",
       priority_number=105,
       worktree_path="/tmp/worktrees/wt2",
       auto_approve=True,
   )

   logger.info(f"🚀 code_developer spawned (PID {result1['result']['pid']}) for US-104 in wt1")
   logger.info(f"🚀 code_developer spawned (PID {result2['result']['pid']}) for US-105 in wt2")
   ```

2. **code_developer agents work independently**
   ```bash
   # In /tmp/worktrees/wt1 (roadmap-wt1)
   cd /tmp/worktrees/wt1
   git branch --show-current  # roadmap-wt1

   # code_developer implements US-104
   # - Reads SPEC-104-*.md
   # - Creates/modifies files in coffee_maker/
   # - Writes tests in tests/
   # - Runs pytest (all tests pass ✅)
   # - Commits work:
   git add .
   git commit -m "feat: Implement US-104 - Feature X

   Features:
   - Feature X implementation
   - Comprehensive tests (15 tests)

   Tests: All passing (156 tests total)
   Status: Ready for merge

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"

   # Pushes to remote (optional):
   git push origin roadmap-wt1
   ```

3. **code-reviewer reviews commits** (if enabled)
   ```python
   # code-reviewer monitors commits in worktrees
   # Creates review report: docs/code-reviews/REVIEW-2025-10-19-abc123d.md
   # If issues found: notifies architect (high priority)
   # If approved: marks as ready for merge
   ```

4. **Orchestrator monitors progress**
   ```python
   # In continuous_work_loop.py _monitor_tasks()
   # Every 30 seconds:
   # - Check agent status (running/completed/failed)
   # - Check for hung agents (>30 min timeout)
   # - Log progress

   # Example log:
   # 14:30:00 - code_developer (PID 12345) for US-104: Running (15 min elapsed)
   # 14:30:00 - code_developer (PID 12346) for US-105: Running (15 min elapsed)
   ```

---

### Phase 3: Merge Detection & Notification

**Trigger**: code_developer completes work in worktree (commits exist, tests pass)

**Steps**:

1. **Orchestrator detects completed worktrees**
   ```python
   # In continuous_work_loop.py _check_worktree_merges()
   # Runs every poll interval (default: 30 seconds)

   # Uses ArchitectCoordinator to detect roadmap-* branches
   completed_worktrees = self.architect_coordinator.get_completed_worktrees()

   # Output:
   # [
   #   {
   #     "branch": "roadmap-wt1",
   #     "commits_ahead": 3,
   #     "last_commit_msg": "feat: Implement US-104 - Feature X",
   #     "us_number": "104"
   #   },
   #   {
   #     "branch": "roadmap-wt2",
   #     "commits_ahead": 5,
   #     "last_commit_msg": "feat: Implement US-105 - Feature Y",
   #     "us_number": "105"
   #   }
   # ]
   ```

2. **Orchestrator notifies architect for each completed worktree**
   ```python
   # For each completed worktree:
   self.architect_coordinator.notify_architect_for_merge(worktree_info)

   # Creates high-priority notification:
   # Title: "Worktree Ready for Merge: roadmap-wt1"
   # Message:
   #   Parallel work in roadmap-wt1 is ready for merge to roadmap.
   #
   #   US Number: US-104
   #   Commits Ahead: 3
   #   Last Commit: feat: Implement US-104 - Feature X
   #
   #   Action Required:
   #   1. Use merge-worktree-branches skill to merge
   #   2. Run tests after merge
   #   3. Push to remote
   #   4. Notify orchestrator when ready for cleanup
   #
   #   Command:
   #   architect merge-worktree-branches --merge roadmap-wt1 --us-number 104

   logger.info("📬 Notified architect to merge roadmap-wt1 (US-104)")
   logger.info("📬 Notified architect to merge roadmap-wt2 (US-105)")
   ```

---

### Phase 4: Architect Merges Parallel Work

**Trigger**: Architect receives merge notification from orchestrator

**Steps**:

1. **Architect checks merge readiness**
   ```bash
   # architect uses merge-worktree-branches skill
   architect merge-worktree-branches --check roadmap-wt1

   # Output:
   # ✅ Tests passing (156 tests)
   # ✅ No conflicts detected
   # ✅ Ready for merge
   ```

2. **Architect performs merge** (using skill or manual workflow)
   ```bash
   # Step 1: Switch to roadmap branch
   git checkout roadmap
   git pull origin roadmap

   # Step 2: Merge worktree branch
   git merge roadmap-wt1 --no-ff -m "Merge parallel work from roadmap-wt1: US-104 - Feature X

   Features:
   - Feature X implementation
   - Comprehensive tests (15 tests)

   Tests: All passing (156 tests total)
   Status: Ready for production

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"

   # Step 3: If conflicts occur
   # - Resolve manually
   # - For ROADMAP.md conflicts: keep both entries
   # - For code conflicts: review carefully, prioritize working code
   # - git add <resolved-files>
   # - git commit

   # Step 4: Validate merge
   pytest  # Ensure all tests still pass
   # Check ROADMAP.md for duplicates
   # Verify git status clean

   # Step 5: Push to remote
   git push origin roadmap
   ```

3. **Architect notifies orchestrator** (merge complete)
   ```python
   # architect sends notification
   self.notifications.create_notification(
       title="Merge Complete",
       message="roadmap-wt1 merged to roadmap (US-104)",
       level="info",
       sound=False,  # CFR-009: Silent for background agents
       agent_id="architect"
   )

   logger.info("✅ Merge complete for roadmap-wt1, notified orchestrator")
   ```

4. **Architect repeats for roadmap-wt2**
   ```bash
   # Same process for roadmap-wt2 (US-105)
   git checkout roadmap
   git pull origin roadmap
   git merge roadmap-wt2 --no-ff -m "Merge parallel work from roadmap-wt2: US-105 - Feature Y

   Features:
   - Feature Y implementation
   - Comprehensive tests (18 tests)

   Tests: All passing (174 tests total)
   Status: Ready for production

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"

   pytest  # Validate
   git push origin roadmap
   ```

---

### Phase 5: Worktree Cleanup

**Trigger**: Architect notifies orchestrator that merge is complete

**Steps**:

1. **Orchestrator receives merge notification**
   ```python
   # In continuous_work_loop.py _monitor_tasks()
   # Checks for architect notifications
   notifications = self.notifications.get_notifications(agent_id="orchestrator")

   # Finds "Merge Complete" notification for roadmap-wt1
   if "Merge Complete" in notification.title:
       worktree_branch = extract_branch(notification.message)  # roadmap-wt1
       worktree_path = get_worktree_path(worktree_branch)  # /tmp/worktrees/wt1

       logger.info(f"🧹 Cleanup requested for {worktree_branch}")
   ```

2. **Orchestrator removes worktrees**
   ```bash
   # Remove worktree 1
   git worktree remove /tmp/worktrees/wt1 --force

   # Remove worktree 2
   git worktree remove /tmp/worktrees/wt2 --force

   # Remove temporary directory
   rm -rf /tmp/worktrees

   logger.info("🧹 Removed worktrees: wt1, wt2")
   ```

3. **Orchestrator deletes remote branches** (if pushed)
   ```bash
   # Delete remote branches (optional cleanup)
   git push origin --delete roadmap-wt1
   git push origin --delete roadmap-wt2

   logger.info("🧹 Deleted remote branches: roadmap-wt1, roadmap-wt2")
   ```

4. **Orchestrator updates state**
   ```python
   # Update work loop state
   self.current_state["parallel_executions_completed"] += 2
   self.current_state["last_cleanup"] = time.time()
   self._save_state()

   logger.info("✅ Parallel execution complete, state saved")
   ```

---

## Workflow Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PHASE 1: TASK EVALUATION                        │
└─────────────────────────────────────────────────────────────────────────┘
    orchestrator                architect
         │                          │
         ├─ Poll ROADMAP ───────────┤
         │                          │
         ├─ Spawn architect ────────►
         │                          │
         │                     Use task-separator
         │                     skill to evaluate
         │                     independence
         │                          │
         │◄────── Return results ───┤
         │                          │
         ├─ Create worktrees ───────┤
         │   (roadmap-wt1, wt2)     │
         │                          │

┌─────────────────────────────────────────────────────────────────────────┐
│                       PHASE 2: PARALLEL EXECUTION                        │
└─────────────────────────────────────────────────────────────────────────┘
    orchestrator           code_developer (wt1)    code_developer (wt2)
         │                          │                        │
         ├─ Spawn agents ───────────►                        │
         │                          │                        │
         └──────────────────────────┼────────────────────────►
                                    │                        │
                              Implement US-104         Implement US-105
                              in roadmap-wt1           in roadmap-wt2
                                    │                        │
                              Run tests ✅              Run tests ✅
                                    │                        │
                              Commit work              Commit work
                                    │                        │

┌─────────────────────────────────────────────────────────────────────────┐
│                  PHASE 3: MERGE DETECTION & NOTIFICATION                 │
└─────────────────────────────────────────────────────────────────────────┘
    orchestrator                architect
         │                          │
         ├─ Detect completed ───────┤
         │   worktrees              │
         │   (roadmap-wt1, wt2)     │
         │                          │
         ├─ Notify architect ───────►
         │   for merge              │
         │                          │

┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: ARCHITECT MERGES WORK                        │
└─────────────────────────────────────────────────────────────────────────┘
    orchestrator                architect
         │                          │
         │                     Check merge
         │                     readiness
         │                          │
         │                     Merge roadmap-wt1
         │                     to roadmap
         │                          │
         │                     Run tests ✅
         │                          │
         │                     Push to remote
         │                          │
         │◄──── Notify complete ────┤
         │                          │
         │                     Merge roadmap-wt2
         │                     to roadmap
         │                          │
         │                     Run tests ✅
         │                          │
         │                     Push to remote
         │                          │
         │◄──── Notify complete ────┤
         │                          │

┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 5: WORKTREE CLEANUP                        │
└─────────────────────────────────────────────────────────────────────────┘
    orchestrator
         │
         ├─ Remove worktrees
         │   (wt1, wt2)
         │
         ├─ Delete remote branches
         │   (roadmap-wt1, wt2)
         │
         ├─ Update state
         │
         └─ ✅ Complete
```

---

## CFR-013 Compliance

**Rule**: All agents work ONLY on `roadmap` branch or `roadmap-*` branches for parallel execution.

**Implementation**:

1. **Main branch**: `roadmap` (single source of truth)
2. **Worktree branches**: `roadmap-wt1`, `roadmap-wt2`, `roadmap-wt3`, etc.
3. **Validation**: `_validate_cfr_013()` in `daemon.py` allows `roadmap` OR `roadmap-*`
4. **Enforcement**: code_developer fails to start on non-roadmap branches

**Benefits**:
- ✅ Single source of truth (roadmap branch)
- ✅ No merge conflicts between feature branches
- ✅ All work immediately visible to team after merge
- ✅ Parallel execution enabled via worktrees
- ✅ Temporary branches cleaned up automatically

---

## CFR-009 Compliance

**Rule**: Only `user_listener` uses sound notifications. Background agents (orchestrator, architect, code_developer) MUST use `sound=False`.

**Implementation**:

```python
# ✅ CORRECT (orchestrator)
self.notifications.create_notification(
    title="Worktree Ready for Merge",
    message="roadmap-wt1 ready for merge (US-104)",
    level="high",
    sound=False,  # Silent for background agent
    agent_id="orchestrator"
)

# ✅ CORRECT (architect)
self.notifications.create_notification(
    title="Merge Complete",
    message="roadmap-wt1 merged to roadmap (US-104)",
    level="info",
    sound=False,  # Silent for background agent
    agent_id="architect"
)
```

**Enforcement**: Using `sound=True` with background `agent_id` raises `CFR009ViolationError`.

---

## Timing & Performance

**Typical Timeline** (for 2 parallel tasks):

| Phase | Duration | Notes |
|-------|----------|-------|
| Task Evaluation | 2-3 min | architect evaluates with task-separator skill |
| Worktree Creation | 30 sec | git worktree add + copy .env |
| Parallel Execution | 30-120 min | Depends on task complexity (saved 50% time!) |
| Merge Detection | <30 sec | Orchestrator polls every 30 sec |
| Architect Merge | 5-10 min per worktree | Includes conflict resolution, validation, push |
| Worktree Cleanup | 30 sec | git worktree remove |
| **Total** | **40-135 min** | **50% faster than sequential (80-270 min)** |

**Performance Benefits**:
- **2 parallel tasks**: 50% time saved
- **3 parallel tasks**: 66% time saved
- **Example**: US-104 (60 min) + US-105 (60 min) = 60 min parallel (vs. 120 min sequential)

---

## Error Handling

| Error Scenario | Detection | Resolution |
|----------------|-----------|------------|
| **Task not independent** | architect task-separator skill | Sequential execution (no worktrees) |
| **Worktree creation fails** | orchestrator git worktree add | Log error, fall back to sequential |
| **code_developer fails in worktree** | orchestrator monitors agent status | Kill agent, cleanup worktree, retry or escalate |
| **Tests fail after merge** | architect validates post-merge | Revert merge (`git reset --hard HEAD~1`), investigate |
| **Merge conflicts** | architect detects during merge | Resolve manually, request user guidance if complex |
| **Hung agent (>30 min)** | orchestrator timeout check | Kill agent, cleanup worktree, retry with different approach |
| **ROADMAP.md duplicates** | architect validates during merge | Remove duplicates manually, keep single entry |
| **Remote push rejected** | architect push fails | Pull latest, rebase if needed, retry push |

---

## Success Criteria

**Metrics Tracked**:

1. **Parallel Execution Rate**: % of tasks executed in parallel (target: >30%)
2. **Time Savings**: Minutes saved vs. sequential execution (target: >40% reduction)
3. **Merge Success Rate**: % of merges completed without issues (target: >90%)
4. **Conflict Resolution Time**: Average time to resolve merge conflicts (target: <10 min)
5. **Worktree Lifecycle**: Average time from creation to cleanup (target: <3 hours)

**Success Indicators**:
- ✅ Orchestrator detects independent tasks automatically
- ✅ Worktrees created within 30 seconds
- ✅ code_developer instances run in parallel without interference
- ✅ Architect merges completed work back to roadmap within 10 minutes
- ✅ Worktrees cleaned up automatically after merge
- ✅ Tests pass after every merge (100% success rate)
- ✅ Single source of truth maintained (roadmap branch always up-to-date)

---

## Related Documentation

- [SPEC-108: Parallel Agent Execution with Git Worktree](specs/SPEC-108-parallel-agent-execution-with-git-worktree.md) - Technical specification
- [CFR-013: Roadmap Branch Only](../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013) - Branch compliance requirement
- [CFR-009: Silent Background Agents](../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-009) - Notification compliance
- [Architect Agent Definition](./.claude/agents/architect.md) - Workflow 7: Merging Parallel Work from Worktrees
- [Merge Worktree Branches Skill](./.claude/skills/architect/merge-worktree-branches/SKILL.md) - Architect merge skill
- [ArchitectCoordinator](../../coffee_maker/orchestrator/architect_coordinator.py) - Merge notification system
- [ContinuousWorkLoop](../../coffee_maker/orchestrator/continuous_work_loop.py) - Orchestrator main loop

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-19 | Initial complete autonomous scaling workflow documentation |

---

**Status**: Active ✅

This workflow is fully implemented and operational. All components (orchestrator, architect, code_developer, merge skill) are integrated and working together to enable autonomous parallel execution.

🚀 **Ready for autonomous scaling!**
