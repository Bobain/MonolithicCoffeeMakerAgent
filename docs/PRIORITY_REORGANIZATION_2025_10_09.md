# Priority Reorganization - Daemon First Approach

**Date**: 2025-10-09
**Reason**: User request - "let's make a first version of the daemon claude-cli implementing and updating the roadmap.md the highest priority"
**Impact**: Re-order all priorities to focus on autonomous daemon first

---

## New Priority Order

### 🔴 **PRIORITY 1: Autonomous Development Daemon (Minimal MVP)** 🤖

**Estimated Duration**: 3-5 days
**Impact**: ⭐⭐⭐⭐⭐ (Game-changing)
**Status**: 📝 Planned
**Dependency**: None - self-contained minimal implementation

**What Changed**:
- Previously PRIORITY 3, now moved to PRIORITY 1
- Simplified to work WITHOUT Project Manager CLI (will integrate later)
- Uses direct file editing for ROADMAP.md updates (with file lock)
- No database notifications initially (terminal only)

**Why This Order**:
1. Get daemon working ASAP to prove autonomous development concept
2. Daemon can implement other priorities autonomously
3. Database sync and PM CLI become daemon's first tasks!

---

### 🔴 **PRIORITY 2: Database Synchronization Architecture** 🚨

**Estimated Duration**: 2-3 days (design phase)
**Status**: 📝 Planned
**Dependency**: PRIORITY 1 (daemon will implement this!)

**What Changed**:
- Previously PRIORITY 1.5, now PRIORITY 2
- Will be implemented BY THE DAEMON (first real task)
- Human designs, daemon implements

---

### 🔴 **PRIORITY 3: Project Manager CLI** 🎯

**Estimated Duration**: 2-3 days per phase
**Status**: 📝 Planned
**Dependency**: PRIORITY 2 (database sync must be designed first)

**What Changed**:
- Previously PRIORITY 2, now PRIORITY 3
- Will be implemented BY THE DAEMON
- Daemon will use its own work as validation

---

### 🟡 **PRIORITY 4: Analytics & Observability**

**Estimated Duration**: 2-3 weeks
**Status**: 📝 Planned
**Dependency**: PRIORITY 2, 3

**What Changed**:
- Previously PRIORITY 1, now PRIORITY 4
- Still important but daemon doesn't need it to start
- Daemon will implement this autonomously

---

### 🟡 **PRIORITY 5+**: All other priorities (Streamlit dashboards, documentation, etc.)

---

## Rationale for New Order

### Why Daemon First?

1. **Prove the Concept**: Get autonomous development working immediately
2. **Meta-Implementation**: Daemon implements its own infrastructure
3. **Faster Delivery**: Daemon can work 24/7 on remaining priorities
4. **Real-World Validation**: Test daemon on real tasks (database sync, PM CLI)

### What Does Minimal Daemon Need?

**Absolutely Essential**:
- ✅ Read ROADMAP.md
- ✅ Parse next task
- ✅ Call Claude CLI via subprocess
- ✅ Edit ROADMAP.md (direct file edit with filelock)
- ✅ Basic Git operations (branch, commit, push)
- ✅ Terminal notifications only (no database yet)

**NOT Needed for MVP**:
- ❌ Database sync (will implement this next!)
- ❌ Project Manager CLI integration (will build this next!)
- ❌ Slack notifications (later)
- ❌ Docker isolation (use local environment first)
- ❌ Advanced monitoring (later)

---

## Simplified Daemon MVP Architecture

```python
# coffee_maker/autonomous/minimal_daemon.py (single file, ~500 LOC)

from pathlib import Path
from filelock import FileLock
import subprocess
import re

class MinimalDaemon:
    """Minimal autonomous development daemon.

    Single file implementation - no dependencies on other priorities.
    """

    def __init__(self, roadmap_path: str = "docs/ROADMAP.md"):
        self.roadmap_path = Path(roadmap_path)
        self.roadmap_lock = FileLock("/tmp/roadmap.lock")

    def run_forever(self):
        """Main daemon loop - runs continuously."""
        while True:
            try:
                # 1. Read ROADMAP.md
                task = self.get_next_task()

                if not task:
                    print("✅ All priorities completed! Waiting for new tasks...")
                    time.sleep(60)
                    continue

                # 2. Implement task via Claude CLI
                print(f"🤖 Starting: {task['name']}")
                self.implement_task(task)

                # 3. Update ROADMAP.md status
                self.update_task_status(task, "completed")

                # 4. Create PR
                self.create_pull_request(task)

                print(f"✅ Completed: {task['name']}")

            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

    def get_next_task(self) -> dict:
        """Parse ROADMAP.md and find next pending task."""
        content = self.roadmap_path.read_text()

        # Simple regex to find first "Status: 📝 Planned" priority
        pattern = r'### 🔴 \*\*PRIORITY (\d+): (.+?)\*\*.*?Status\*\*: 📝 Planned'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return {
                "priority": match.group(1),
                "name": match.group(2),
                "full_text": match.group(0)
            }
        return None

    def implement_task(self, task: dict):
        """Call Claude CLI to implement task."""
        prompt = f"""
        Read the file docs/ROADMAP.md and implement PRIORITY {task['priority']}: {task['name']}.

        Follow all guidelines in the roadmap.
        Create proper git commits as you work.
        Run tests before finishing.
        Update documentation.
        """

        # Call Claude CLI via subprocess
        result = subprocess.run(
            ["claude", "code", "-p", prompt],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Claude CLI failed: {result.stderr}")

        return result.stdout

    def update_task_status(self, task: dict, status: str):
        """Update ROADMAP.md with new status (with file lock)."""
        with self.roadmap_lock:
            content = self.roadmap_path.read_text()

            # Replace "Status: 📝 Planned" with "Status: ✅ Completed"
            if status == "completed":
                new_content = content.replace(
                    f"PRIORITY {task['priority']}: {task['name']}**.*?Status**: 📝 Planned",
                    f"PRIORITY {task['priority']}: {task['name']}** ✅\n**Status**: ✅ Completed"
                )
            elif status == "in_progress":
                new_content = content.replace(
                    f"PRIORITY {task['priority']}: {task['name']}**.*?Status**: 📝 Planned",
                    f"PRIORITY {task['priority']}: {task['name']}** 🔄\n**Status**: 🔄 In Progress"
                )

            self.roadmap_path.write_text(new_content)

    def create_pull_request(self, task: dict):
        """Create PR via gh CLI."""
        subprocess.run([
            "gh", "pr", "create",
            "--title", f"feat: Implement PRIORITY {task['priority']} - {task['name']}",
            "--body", f"Autonomous implementation by daemon.\n\nTask: {task['name']}"
        ])

# Run daemon
if __name__ == "__main__":
    daemon = MinimalDaemon()
    daemon.run_forever()
```

**Key Simplifications**:
1. Single file (~500 LOC)
2. Direct file editing (no database)
3. Simple regex parsing (no complex markdown parser)
4. Terminal output only (no notifications database)
5. Local environment (no Docker yet)
6. File lock prevents conflicts

---

## Implementation Timeline

### Day 1: Minimal Daemon Core (6-8h)

**Goal**: Get basic daemon working - read ROADMAP, call Claude CLI, update status

**Tasks**:
- [ ] Create `coffee_maker/autonomous/minimal_daemon.py`
- [ ] Implement `get_next_task()` - regex parse ROADMAP.md
- [ ] Implement `implement_task()` - subprocess call to Claude CLI
- [ ] Implement `update_task_status()` - direct file edit with filelock
- [ ] Test: Can it read ROADMAP and find next task?
- [ ] Test: Can it call Claude CLI successfully?
- [ ] Test: Can it update ROADMAP without conflicts?

**Acceptance Criteria**:
- ✅ Daemon reads ROADMAP.md and finds "PRIORITY X: Status: 📝 Planned"
- ✅ Daemon calls Claude CLI with proper prompt
- ✅ Daemon updates ROADMAP.md status to "✅ Completed"
- ✅ File lock prevents concurrent edits

---

### Day 2: Git Integration & PR Creation (4-6h)

**Goal**: Automate branch creation and PR creation

**Tasks**:
- [ ] Implement `create_branch()` - git checkout -b feature/priority-X
- [ ] Implement `commit_changes()` - git add, commit with proper message
- [ ] Implement `push_branch()` - git push origin feature/priority-X
- [ ] Implement `create_pull_request()` - gh pr create
- [ ] Test: Full workflow from start to PR creation

**Acceptance Criteria**:
- ✅ Daemon creates feature branch automatically
- ✅ Claude CLI commits are preserved
- ✅ Daemon pushes branch to origin
- ✅ Daemon creates PR with proper title/body
- ✅ Full workflow works end-to-end

---

### Day 3: Error Handling & Safety (4-6h)

**Goal**: Make daemon robust and safe

**Tasks**:
- [ ] Add retry logic (if Claude CLI fails, retry with error context)
- [ ] Add rollback (if tests fail, revert changes)
- [ ] Add logging (structured logs to file)
- [ ] Add safety checks (confirm ROADMAP.md exists, git repo is clean)
- [ ] Add graceful shutdown (CTRL+C stops cleanly)
- [ ] Test: Error scenarios (Claude fails, tests fail, conflicts)

**Acceptance Criteria**:
- ✅ Daemon retries on transient failures
- ✅ Daemon rolls back on test failures
- ✅ Daemon logs all actions to file
- ✅ Daemon handles CTRL+C gracefully
- ✅ Daemon never corrupts ROADMAP.md

---

### Day 4: Documentation & First Real Task (4-6h)

**Goal**: Document daemon and use it to implement PRIORITY 2 (Database Sync)

**Tasks**:
- [ ] Write README for daemon (setup, usage, troubleshooting)
- [ ] Create `scripts/run_daemon.py` launcher
- [ ] Test daemon on fake PRIORITY (add test priority to roadmap)
- [ ] **REAL TEST**: Start daemon, let it implement PRIORITY 2 (Database Sync design)
- [ ] Monitor daemon's work, verify quality
- [ ] Create meta-documentation (daemon documenting itself)

**Acceptance Criteria**:
- ✅ README complete with examples
- ✅ Daemon successfully implements at least one real priority
- ✅ Output quality is acceptable (comparable to human implementation)
- ✅ Daemon's self-documentation is clear

---

### Day 5: Polish & Handoff (2-4h)

**Goal**: Prepare daemon to autonomously implement remaining priorities

**Tasks**:
- [ ] Final code review and cleanup
- [ ] Add configuration file (daemon_config.yaml)
- [ ] Add telemetry (track successful implementations)
- [ ] Create video demo (optional)
- [ ] **START AUTONOMOUS PHASE**: Let daemon implement PRIORITY 3, 4, 5...

**Acceptance Criteria**:
- ✅ Code is clean and documented
- ✅ Daemon is configurable
- ✅ Ready to run unsupervised
- ✅ User can start daemon and walk away

---

## Success Metrics

**MVP Success** if:
1. ✅ Daemon reads ROADMAP.md without errors
2. ✅ Daemon calls Claude CLI successfully
3. ✅ Daemon updates ROADMAP.md status correctly
4. ✅ Daemon creates branches and PRs
5. ✅ Daemon completes at least ONE real priority autonomously
6. ✅ Output quality is acceptable (code works, tests pass)

**Long-term Success** if:
7. ✅ Daemon implements PRIORITY 2 (Database Sync) autonomously
8. ✅ Daemon implements PRIORITY 3 (Project Manager CLI) autonomously
9. ✅ Daemon implements PRIORITY 4 (Analytics) autonomously
10. ✅ User only reviews PRs, doesn't write code

---

## Key Differences from Previous Plan

| Aspect | Previous Plan | New Plan |
|--------|--------------|----------|
| Priority Order | Analytics → DB Sync → PM CLI → Daemon | Daemon → DB Sync → PM CLI → Analytics |
| Daemon Complexity | Full-featured with Docker, notifications, DB | Minimal single-file, local environment |
| Database Integration | Required from start | NOT required (terminal only) |
| PM CLI Integration | Required from start | NOT required (direct file edit) |
| Timeline | 10+ days (including dependencies) | 3-5 days (self-contained) |
| First Task | Human implements analytics | Daemon implements database sync |

---

## Risk Mitigation

**Risk 1**: Daemon corrupts ROADMAP.md
- **Mitigation**: File lock + git versioning (every edit is committed)

**Risk 2**: Claude CLI produces low-quality code
- **Mitigation**: Run tests automatically, rollback on failure

**Risk 3**: Daemon gets stuck in infinite loop
- **Mitigation**: Add timeout per task (4-hour max)

**Risk 4**: Daemon implements wrong priority
- **Mitigation**: Parse ROADMAP.md carefully, validate priority number

**Risk 5**: User and daemon edit ROADMAP simultaneously
- **Mitigation**: File lock prevents this (one waits for other)

---

## Next Steps

1. **User Approval**: Confirm new priority order
2. **Start Day 1**: Begin minimal daemon implementation
3. **Test Incrementally**: Validate each component before integration
4. **First Real Task**: Daemon implements PRIORITY 2 (Database Sync)
5. **Iterate**: Improve daemon based on first real task experience

---

## Questions for User

1. **Approve New Priority Order**: Daemon first, everything else after?
2. **Minimal vs Full-Featured**: Should we start with minimal single-file daemon?
3. **First Real Task**: Should daemon's first task be Database Sync design implementation?
4. **Supervision Level**: Should daemon require approval before PRs, or auto-create?

---

**Status**: Ready for user approval
**Next Action**: Begin Day 1 implementation of minimal daemon
