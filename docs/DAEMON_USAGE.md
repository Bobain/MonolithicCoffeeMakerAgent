# Autonomous Development Daemon - Usage Guide

The **DevDaemon** is an autonomous development system that continuously reads `docs/ROADMAP.md` and automatically implements planned priorities using Claude CLI.

## 🎯 Overview

```
ROADMAP.md → DevDaemon → Claude CLI → Implementation → Git → PR → Update ROADMAP
```

**What it does**:
1. Reads `ROADMAP.md` to find next planned priority
2. Requests your approval (unless `--auto` mode)
3. Executes Claude CLI to implement the feature
4. Commits changes with proper message
5. Pushes branch and creates PR
6. Updates `ROADMAP.md` status
7. Repeats until all priorities complete

## 🚀 Quick Start

### 1. Prerequisites

- **Claude CLI** installed and authenticated: `claude --version`
- **gh CLI** installed and authenticated: `gh auth status`
- **Git repository** with remote configured
- **Python 3.10+** with `coffee-maker` installed

### 2. Run the Daemon

**Safe mode** (asks for approval):
```bash
python run_dev_daemon.py
```

**Auto mode** (implements without asking):
```bash
python run_dev_daemon.py --auto
```

### 3. Monitor Progress

In another terminal:
```bash
# View notifications
project-manager notifications

# Approve a task
project-manager respond <notif_id> approve

# Decline a task
project-manager respond <notif_id> decline
```

### 4. Stop the Daemon

Press `Ctrl+C` to stop gracefully.

---

## 📖 Command Reference

### Basic Usage

```bash
python run_dev_daemon.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--roadmap PATH` | Path to ROADMAP.md | `docs/ROADMAP.md` |
| `--auto` | Auto-approve (skip confirmation) | `False` |
| `--no-pr` | Skip PR creation | `False` |
| `--sleep N` | Sleep N seconds between iterations | `30` |
| `--model NAME` | Claude model to use | `claude-sonnet-4` |

### Examples

**Default (safe) mode**:
```bash
python run_dev_daemon.py
```

**Custom roadmap path**:
```bash
python run_dev_daemon.py --roadmap projects/my-app/roadmap.md
```

**Fast iteration (10s sleep)**:
```bash
python run_dev_daemon.py --sleep 10
```

**Use different Claude model**:
```bash
python run_dev_daemon.py --model claude-opus-4
```

**Full automation** (⚠️ use with caution!):
```bash
python run_dev_daemon.py --auto --no-pr --sleep 60
```

---

## 🔄 Workflow Details

### 1. Roadmap Format

The daemon looks for priorities in this format:

```markdown
### 🔴 **PRIORITY 1: Feature Name** ⚡ TAG

**Status**: 📝 Planned
**Deliverables**:
- Implement X
- Add tests for Y
- Update documentation
```

Status indicators:
- `📝 Planned` - Ready for implementation
- `🔄 In Progress` - Currently being implemented
- `✅ Complete` - Finished

### 2. Approval Workflow (Non-Auto Mode)

When the daemon finds a planned priority:

1. **Daemon creates notification**:
   ```
   [INFO] Created notification 123 - waiting for response
   Check notifications with: project-manager notifications
   Approve with: project-manager respond 123 approve
   ```

2. **You check notifications**:
   ```bash
   project-manager notifications
   ```

   Output:
   ```
   📬 Pending Notifications

   [1] Implement PRIORITY 3?
       Type: QUESTION | Priority: HIGH
       The daemon wants to implement:
       Basic Autonomous Development Daemon

       Approve?

       Respond: project-manager respond 1 approve
   ```

3. **You approve**:
   ```bash
   project-manager respond 1 approve
   ```

4. **Daemon implements**:
   - Creates branch `feature/priority-3`
   - Executes Claude CLI with implementation prompt
   - Commits changes
   - Pushes to remote
   - Creates PR
   - Sends completion notification

### 3. Implementation Prompt

The daemon sends this prompt to Claude CLI:

```
Read docs/ROADMAP.md and implement PRIORITY X: Feature Name.

Follow the roadmap guidelines and deliverables. Update docs/ROADMAP.md with your progress.

Important:
- Follow all coding standards
- Add tests where appropriate
- Document your changes
- Update ROADMAP.md status to "🔄 In Progress" first, then "✅ Complete" when done
- Commit frequently with clear messages

Priority details:
<priority content...>

Begin implementation now.
```

### 4. Git Operations

For each priority, the daemon:

1. **Creates branch**: `feature/priority-{number}-{name}`
2. **Commits** with message:
   ```
   feat: Implement PRIORITY X - Feature Name

   Autonomous implementation by DevDaemon.

   Priority: PRIORITY X
   Status: ✅ Complete

   🤖 Generated with [Claude Code](https://claude.com/claude-code) via DevDaemon

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
3. **Pushes**: `git push -u origin feature/priority-{number}-{name}`
4. **Creates PR** via `gh CLI`:
   ```
   gh pr create --title "Implement PRIORITY X: Feature Name" \
     --body "<PR description>" \
     --base main
   ```

---

## ⚙️ Configuration

### Environment Variables

The daemon respects these environment variables:

- `LANGFUSE_PUBLIC_KEY` - For observability
- `LANGFUSE_SECRET_KEY` - For observability
- `CLAUDE_API_KEY` - Claude CLI authentication (if not using `claude login`)

### Daemon Parameters (Programmatic)

If using the daemon as a library:

```python
from coffee_maker.autonomous.daemon import DevDaemon

daemon = DevDaemon(
    roadmap_path="docs/ROADMAP.md",
    auto_approve=False,          # Ask for approval
    create_prs=True,             # Create PRs automatically
    sleep_interval=30,           # Sleep 30s between iterations
    model="claude-sonnet-4"      # Claude model
)

daemon.run()
```

---

## 🛡️ Safety Features

### 1. Git-Based Safety

- **All changes in branches**: Never commits to `main` directly
- **PR workflow**: Every implementation goes through PR review
- **Reversible**: All changes tracked in Git, can be reverted

### 2. User Approval (Non-Auto Mode)

- **Explicit approval required**: Daemon waits up to 5 minutes
- **Skip unwanted tasks**: Respond "decline" to skip
- **Review before implementation**: Check deliverables first

### 3. Timeouts

- **Claude CLI timeout**: 1 hour per implementation
- **Approval timeout**: 5 minutes to respond
- **Git operation timeout**: 30 seconds

### 4. Error Handling

- **Retry logic**: Database operations retry up to 3 times
- **Graceful failures**: Logs error, sleeps, continues
- **Keyboard interrupt**: `Ctrl+C` stops cleanly

---

## 📊 Monitoring

### Logs

The daemon writes logs to:
- **Console**: Real-time progress
- **File**: `dev_daemon.log` (persistent log)

Log levels:
```
INFO  - Normal progress
WARN  - Non-critical issues
ERROR - Failed operations
```

### Notifications

Check notifications anytime:
```bash
project-manager notifications
```

View all notifications (including completed):
```bash
project-manager notifications --all
```

### Git Status

Check daemon's Git activity:
```bash
git log --oneline --author="Claude"
```

View daemon branches:
```bash
git branch -r | grep feature/priority
```

---

## 🐛 Troubleshooting

### Daemon Not Finding Planned Priorities

**Symptom**: "No more planned priorities - all done!"

**Solutions**:
1. Check ROADMAP.md has priorities with `📝 Planned` status
2. Verify priority format matches:
   ```markdown
   ### 🔴 **PRIORITY X: Title** ⚡ TAG
   **Status**: 📝 Planned
   ```
3. Check daemon is reading correct roadmap path

### Claude CLI Fails

**Symptom**: "Claude CLI failed: <error>"

**Solutions**:
1. Verify Claude CLI installed: `claude --version`
2. Check authentication: `claude login`
3. Test manually: `claude code -p "Hello"`
4. Check timeout (default 1 hour) is sufficient

### Git Operations Fail

**Symptom**: "Failed to push branch"

**Solutions**:
1. Check remote configured: `git remote -v`
2. Verify authentication: `git push` manually
3. Check branch doesn't already exist
4. Ensure working directory is clean

### PR Creation Fails

**Symptom**: "Failed to create PR"

**Solutions**:
1. Verify gh CLI installed: `gh --version`
2. Check authentication: `gh auth status`
3. Test manually: `gh pr list`
4. Ensure base branch exists (usually `main`)

### Approval Timeout

**Symptom**: "User did not respond in time - skipping"

**Solutions**:
1. Respond faster (5 minute timeout)
2. Use `--auto` mode (skip approval)
3. Check notification system: `project-manager notifications`

---

## 🎯 Best Practices

### 1. Start Small

Begin with 1-2 simple priorities to test the workflow:
```markdown
### 🔴 **PRIORITY 1: Add Hello World Function** ⚡ TEST

**Status**: 📝 Planned
**Deliverables**:
- Create `hello.py` with `hello()` function
- Add unit test
```

### 2. Use Non-Auto Mode First

Always start with manual approval:
```bash
python run_dev_daemon.py  # Non-auto by default
```

Review the first few implementations before using `--auto`.

### 3. Monitor Closely

Keep an eye on:
- Daemon logs (`dev_daemon.log`)
- Git activity (`git log`)
- PR quality (GitHub)

### 4. Clear Deliverables

Write specific, actionable deliverables:

✅ **Good**:
```markdown
**Deliverables**:
- Create `database.py` with SQLite connection helper
- Add `insert_user()` and `get_user()` functions
- Write 5 unit tests covering CRUD operations
- Update README with database setup instructions
```

❌ **Bad**:
```markdown
**Deliverables**:
- Add database stuff
- Make it work
```

### 5. Regular PR Reviews

Don't let PRs pile up. Review and merge regularly to:
- Keep roadmap current
- Prevent merge conflicts
- Provide feedback for future implementations

### 6. Roadmap Updates

Keep `ROADMAP.md` up to date:
- Mark completed priorities as `✅ Complete`
- Add new priorities as needed
- Update deliverables based on feedback

---

## 🔮 Advanced Usage

### Running Multiple Daemons

Run separate daemons for different roadmaps:

**Terminal 1** (main roadmap):
```bash
python run_dev_daemon.py --roadmap docs/ROADMAP.md
```

**Terminal 2** (feature roadmap):
```bash
python run_dev_daemon.py --roadmap projects/feature-x/roadmap.md --sleep 60
```

### Custom Implementation Prompts

Programmatic usage allows custom prompts:

```python
from coffee_maker.autonomous.daemon import DevDaemon

class CustomDaemon(DevDaemon):
    def _build_implementation_prompt(self, priority):
        return f"""
        Implement {priority['name']} following our team's standards:

        1. Use TypeScript strict mode
        2. Follow Airbnb style guide
        3. Write tests first (TDD)
        4. Document all public APIs

        {priority['content']}
        """

daemon = CustomDaemon(roadmap_path="docs/ROADMAP.md")
daemon.run()
```

### Integration with CI/CD

Run daemon in CI to implement features on schedule:

```yaml
# .github/workflows/autonomous-dev.yml
name: Autonomous Development

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:       # Manual trigger

jobs:
  implement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run DevDaemon
        run: |
          python run_dev_daemon.py --auto --sleep 0
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 📚 Related Documentation

- [ROADMAP.md](../docs/ROADMAP.md) - Project roadmap
- [PRIORITY 3 Details](../docs/ROADMAP.md#priority-3) - Daemon implementation details
- [Notification System](../docs/ROADMAP.md#priority-2) - project-manager CLI

---

## 🤝 Support

If you encounter issues:

1. Check logs: `dev_daemon.log`
2. Review this guide's troubleshooting section
3. Test components individually:
   ```bash
   # Test roadmap parser
   python -c "from coffee_maker.autonomous.roadmap_parser import RoadmapParser; p = RoadmapParser('docs/ROADMAP.md'); print(p.get_priorities())"

   # Test Claude CLI
   claude code -p "print hello world"

   # Test Git
   git status
   ```
4. Run integration tests: `pytest tests/integration/test_daemon_integration.py -v`

---

**Happy Autonomous Development! 🤖**
