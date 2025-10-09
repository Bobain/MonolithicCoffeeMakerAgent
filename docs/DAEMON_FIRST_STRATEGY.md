# Daemon-First Implementation Strategy

**Date**: 2025-10-09
**Status**: 🚀 Ready to Implement
**Timeline**: 3-5 days to working autonomous daemon

---

## Executive Summary

**New Strategy**: Build minimal autonomous daemon **FIRST**, then let daemon implement everything else autonomously!

**Why**:
- ✅ Prove autonomous development concept immediately
- ✅ Daemon works 24/7 on remaining priorities
- ✅ Faster overall delivery (daemon implements faster than human)
- ✅ Real-world validation (daemon builds its own infrastructure)

---

## The Plan: Meta-Implementation

```
Day 1-3: Human builds minimal daemon (500 LOC)
           ↓
Day 4:     Daemon implements Database Sync design
           ↓
Day 5-7:   Daemon implements Project Manager CLI
           ↓
Day 8-21:  Daemon implements Analytics & Observability
           ↓
Day 22+:   Daemon implements Streamlit dashboards
```

**Key Insight**: Building the daemon takes 3-5 days. Daemon then builds everything else in parallel while you review PRs!

---

## Minimal Daemon Requirements

### What It Needs (Essential)

1. **Read ROADMAP.md** - Parse markdown, find "Status: 📝 Planned"
2. **Call Claude CLI** - Subprocess wrapper: `claude code -p "implement PRIORITY X"`
3. **Update ROADMAP.md** - Direct file edit with filelock (no database needed)
4. **Git Automation** - Branch, commit, push, create PR via gh CLI
5. **Terminal Output** - Print progress (no notifications database yet)

### What It Doesn't Need (Later)

- ❌ Database synchronization (will implement this as first task!)
- ❌ Project Manager CLI integration (will build this as second task!)
- ❌ Docker isolation (use local environment first)
- ❌ Slack notifications (terminal is fine for MVP)
- ❌ Advanced monitoring (later)

---

## Implementation: Single File Daemon (~500 LOC)

### File Structure

```
coffee_maker/autonomous/
└── minimal_daemon.py          # Everything in one file!

scripts/
└── run_daemon.py              # Simple launcher
```

### Core Code Structure

```python
# coffee_maker/autonomous/minimal_daemon.py

from pathlib import Path
from filelock import FileLock
import subprocess
import re
import time

class MinimalDaemon:
    """Minimal autonomous development daemon.

    Reads ROADMAP.md, implements next task via Claude CLI, updates status.
    Runs continuously until all priorities completed.
    """

    def __init__(
        self,
        roadmap_path: str = "docs/ROADMAP.md",
        auto_approve: bool = True,
        create_prs: bool = True
    ):
        self.roadmap_path = Path(roadmap_path)
        self.roadmap_lock = FileLock("/tmp/roadmap.lock")
        self.auto_approve = auto_approve
        self.create_prs = create_prs

    def run_forever(self):
        """Main daemon loop - runs continuously."""
        print("🤖 Autonomous Development Daemon Started")
        print(f"📋 Watching: {self.roadmap_path}")
        print("=" * 80)

        while True:
            try:
                # 1. Find next task
                task = self.get_next_task()

                if not task:
                    print("✅ All priorities completed! Waiting for new tasks...")
                    time.sleep(60)
                    continue

                # 2. Mark as in progress
                self.update_task_status(task, "in_progress")

                # 3. Create feature branch
                self.create_branch(task)

                # 4. Implement via Claude CLI
                print(f"\n🤖 Starting: PRIORITY {task['priority']} - {task['name']}")
                print("=" * 80)
                self.implement_task(task)

                # 5. Run tests
                if not self.run_tests():
                    print("❌ Tests failed - rolling back...")
                    self.rollback(task)
                    continue

                # 6. Mark as completed
                self.update_task_status(task, "completed")

                # 7. Push and create PR
                self.push_branch(task)
                if self.create_prs:
                    self.create_pull_request(task)

                print(f"✅ Completed: PRIORITY {task['priority']} - {task['name']}")
                print("=" * 80)

            except KeyboardInterrupt:
                print("\n🛑 Daemon stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)  # Wait before retry

    def get_next_task(self) -> dict:
        """Parse ROADMAP.md and find next pending task."""
        content = self.roadmap_path.read_text()

        # Find first "Status: 📝 Planned" priority
        pattern = r'### 🔴 \*\*PRIORITY (\d+): (.+?)\*\*.*?\*\*Status\*\*: 📝 Planned'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return {
                "priority": match.group(1),
                "name": match.group(2).strip(),
            }
        return None

    def implement_task(self, task: dict):
        """Call Claude CLI to implement task."""
        prompt = f"""
Read the file docs/ROADMAP.md and implement PRIORITY {task['priority']}: {task['name']}.

IMPORTANT: Follow ALL guidelines in the roadmap including:
- Apply recurring best practices (code refactoring, documentation, tests, etc.)
- Use @observe and @with_retry decorators where appropriate
- Follow database access patterns if working with databases
- Update documentation and type hints
- Run tests before finishing
- Create proper git commits as you work

Work autonomously and thoroughly. When complete, ensure:
1. All code is clean and follows existing patterns
2. Tests are passing
3. Documentation is updated
4. ROADMAP.md status is updated (you can edit it directly)
"""

        # Call Claude CLI via subprocess
        result = subprocess.run(
            ["claude", "code", "-p", prompt],
            capture_output=False,  # Show output in real-time
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Claude CLI failed with code {result.returncode}")

    def update_task_status(self, task: dict, status: str):
        """Update ROADMAP.md with new status (with file lock)."""
        with self.roadmap_lock:
            content = self.roadmap_path.read_text()

            # Status emoji mapping
            status_map = {
                "in_progress": "🔄 In Progress",
                "completed": "✅ Completed"
            }

            # Find and replace status line
            pattern = f"(PRIORITY {task['priority']}: {re.escape(task['name'])}.*?\\*\\*Status\\*\\*:) 📝 Planned"
            replacement = f"\\1 {status_map.get(status, status)}"

            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

            if new_content != content:
                self.roadmap_path.write_text(new_content)
                print(f"📝 Updated ROADMAP.md: Status → {status_map.get(status, status)}")
            else:
                print(f"⚠️  Warning: Could not update status for PRIORITY {task['priority']}")

    def create_branch(self, task: dict):
        """Create feature branch."""
        branch_name = f"feature/priority-{task['priority']}-{task['name'].lower().replace(' ', '-')[:50]}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"🌳 Created branch: {branch_name}")

    def run_tests(self) -> bool:
        """Run test suite."""
        print("\n🧪 Running tests...")
        result = subprocess.run(["pytest", "tests/", "-v"], capture_output=True)

        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Tests failed")
            print(result.stdout.decode())
            return False

    def rollback(self, task: dict):
        """Rollback changes if tests fail."""
        print("🔄 Rolling back changes...")
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)
        subprocess.run(["git", "checkout", "main"], check=True)
        self.update_task_status(task, "planned")

    def push_branch(self, task: dict):
        """Push branch to origin."""
        result = subprocess.run(["git", "push", "origin", "HEAD"], check=True)
        print("⬆️  Pushed branch to origin")

    def create_pull_request(self, task: dict):
        """Create PR via gh CLI."""
        title = f"feat: Implement PRIORITY {task['priority']} - {task['name']}"
        body = f"""## Autonomous Implementation

**Priority**: PRIORITY {task['priority']}
**Task**: {task['name']}
**Implemented by**: Autonomous Development Daemon

### Summary
[Claude will have added details in commits]

### Testing
- ✅ All tests passing
- ✅ Code follows project patterns
- ✅ Documentation updated

🤖 Generated with Autonomous Development Daemon
"""

        subprocess.run([
            "gh", "pr", "create",
            "--title", title,
            "--body", body
        ], check=True)
        print("📬 Created pull request")


# Run daemon
if __name__ == "__main__":
    daemon = MinimalDaemon()
    daemon.run_forever()
```

---

## Usage

### Starting the Daemon

```bash
# Simple start
python -m coffee_maker.autonomous.minimal_daemon

# Or via script
python scripts/run_daemon.py

# With configuration
python -m coffee_maker.autonomous.minimal_daemon \
    --roadmap docs/ROADMAP.md \
    --auto-approve \
    --create-prs
```

### What You'll See

```
🤖 Autonomous Development Daemon Started
📋 Watching: docs/ROADMAP.md
================================================================================

🤖 Starting: PRIORITY 2 - Database Synchronization Architecture
================================================================================
📝 Updated ROADMAP.md: Status → 🔄 In Progress
🌳 Created branch: feature/priority-2-database-synchronization-architecture

[Claude CLI output appears here in real-time]

🧪 Running tests...
✅ All tests passed
📝 Updated ROADMAP.md: Status → ✅ Completed
⬆️  Pushed branch to origin
📬 Created pull request

✅ Completed: PRIORITY 2 - Database Synchronization Architecture
================================================================================

🤖 Starting: PRIORITY 3 - Project Manager CLI
================================================================================
[... continues automatically ...]
```

---

## 5-Day Implementation Timeline

### Day 1: Core Daemon (6-8h)

**Morning (3-4h)**:
- [ ] Create `coffee_maker/autonomous/minimal_daemon.py`
- [ ] Implement `get_next_task()` - regex parse ROADMAP.md
- [ ] Implement `update_task_status()` - filelock + regex replace
- [ ] Test: Parse ROADMAP, find next task, update status

**Afternoon (3-4h)**:
- [ ] Implement `implement_task()` - subprocess call to Claude CLI
- [ ] Implement `run_forever()` - main loop with error handling
- [ ] Test: Full cycle with mock task
- [ ] Add logging and status messages

**Deliverable**: Daemon can read ROADMAP, call Claude CLI, update status

---

### Day 2: Git Integration (4-6h)

**Morning (2-3h)**:
- [ ] Implement `create_branch()` - git checkout -b
- [ ] Implement `push_branch()` - git push origin HEAD
- [ ] Implement `create_pull_request()` - gh pr create
- [ ] Test: Branch creation and PR creation

**Afternoon (2-3h)**:
- [ ] Implement `run_tests()` - pytest integration
- [ ] Implement `rollback()` - git reset --hard on test failure
- [ ] Test: Error scenarios (tests fail, rollback works)
- [ ] Add retry logic for transient failures

**Deliverable**: Daemon creates branches, runs tests, creates PRs

---

### Day 3: Safety & Robustness (4-6h)

**Morning (2-3h)**:
- [ ] Add graceful shutdown (handle CTRL+C)
- [ ] Add configuration file support (YAML)
- [ ] Add structured logging (to file + console)
- [ ] Test: Long-running daemon, shutdown cleanly

**Afternoon (2-3h)**:
- [ ] Add safety checks (roadmap exists, git repo clean, etc.)
- [ ] Add timeout per task (4-hour max)
- [ ] Add telemetry (track successful implementations)
- [ ] Final testing with multiple mock tasks

**Deliverable**: Production-ready daemon with safety features

---

### Day 4: Documentation & First Real Task (4-6h)

**Morning (2h)**:
- [ ] Write README for daemon
- [ ] Create `scripts/run_daemon.py` launcher
- [ ] Add configuration examples
- [ ] Record demo video (optional)

**Afternoon (2-4h)**:
- [ ] **REAL TEST**: Add fake PRIORITY to ROADMAP
- [ ] Start daemon, let it implement fake task
- [ ] Monitor quality, fix issues if needed
- [ ] Validate end-to-end workflow

**Deliverable**: Daemon successfully implements at least one complete task

---

### Day 5: Production & Handoff (2-4h)

**Morning (1-2h)**:
- [ ] Code review and cleanup
- [ ] Final documentation polish
- [ ] Add troubleshooting guide
- [ ] Update ROADMAP with daemon as PRIORITY 1

**Afternoon (1-2h)**:
- [ ] **START AUTONOMOUS PHASE**
- [ ] Let daemon implement PRIORITY 2 (Database Sync)
- [ ] Monitor from sidelines
- [ ] Only intervene if critical issues

**Deliverable**: Daemon running autonomously on real priorities

---

## Success Metrics

### MVP Success (Day 3)
1. ✅ Daemon reads ROADMAP.md correctly
2. ✅ Daemon calls Claude CLI successfully
3. ✅ Daemon updates ROADMAP.md status
4. ✅ Daemon creates branches and PRs
5. ✅ Daemon handles errors gracefully
6. ✅ Can run unsupervised for hours

### Real-World Success (Day 5)
7. ✅ Daemon implements at least ONE real priority
8. ✅ Output quality is acceptable (tests pass, code works)
9. ✅ PRs are reviewable (good commit messages, clear diffs)
10. ✅ User only reviews, doesn't write code

### Long-Term Success (Week 2+)
11. ✅ Daemon implements PRIORITY 2 (Database Sync)
12. ✅ Daemon implements PRIORITY 3 (Project Manager CLI)
13. ✅ Daemon implements PRIORITY 4 (Analytics)
14. ✅ User intervention <10% of time

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Daemon corrupts ROADMAP.md | File lock + git commits (every edit tracked) |
| Claude produces low-quality code | Run tests automatically, rollback on failure |
| Daemon gets stuck | Timeout per task (4 hours), auto-skip if stuck |
| Daemon implements wrong priority | Careful regex parsing, validate priority number |
| Concurrent edits (user + daemon) | File lock prevents this (one waits for other) |
| Claude CLI fails | Retry with error context, exponential backoff |

---

## Comparison: Old vs New Approach

| Aspect | Old Approach | New Approach |
|--------|-------------|--------------|
| First Priority | Analytics & Observability | Autonomous Daemon |
| Database Sync | Human designs + implements | Human designs, Daemon implements |
| Project Manager CLI | Human implements | Daemon implements |
| Analytics | Human implements | Daemon implements |
| Timeline (All Priorities) | 6-8 weeks (human) | 3-5 days (daemon setup) + 2-3 weeks (daemon implements) |
| Human Effort | High (full implementation) | Low (review PRs only) |
| Validation | End of each priority | Continuous (daemon self-validates) |

**Key Insight**: Initial investment of 3-5 days yields 4-6 weeks of autonomous development!

---

## Dependencies

### Required Libraries

```bash
# Already in requirements
pip install filelock  # File locking

# System dependencies
claude-cli  # Claude Code CLI (already installed)
gh          # GitHub CLI (for PR creation)
git         # Git CLI (already installed)
pytest      # Testing framework (already installed)
```

### Configuration

```yaml
# daemon_config.yaml
roadmap_path: "docs/ROADMAP.md"
auto_approve: true
create_prs: true
max_task_duration_hours: 4
log_file: "logs/daemon.log"
test_command: "pytest tests/ -v"
```

---

## Next Steps

1. **User Approval**: Confirm daemon-first strategy
2. **Day 1 Start**: Implement core daemon functionality
3. **Day 2-3**: Add Git integration and safety features
4. **Day 4**: Validate with real task
5. **Day 5**: Launch autonomous phase

---

## Questions for User

1. **Approve Strategy**: Build daemon first, let it implement everything else?
2. **Auto-Approve**: Should daemon auto-create PRs or ask for approval?
3. **First Real Task**: Should daemon's first task be Database Sync implementation?
4. **Supervision**: How much oversight do you want? (Daily check-in vs full autonomy)

---

**Status**: 🚀 Ready to implement
**Estimated Start**: Now
**Estimated Completion**: 5 days
**Expected Outcome**: Working autonomous daemon + first priority implemented

**Let's build the future of software development! 🤖**
