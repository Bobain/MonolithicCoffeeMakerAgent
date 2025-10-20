# Skill: Activity and Progress Summary

**Name**: `activity-summary`
**Owner**: orchestrator
**Purpose**: Generate comprehensive summaries of development activity, progress, and current agent status
**Priority**: HIGH - Enables observability and progress tracking

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ When user requests status update or progress report
- ✅ For scheduled status reports (daily, every N hours)
- ✅ After major milestones (priority completion, parallel execution batch)
- ✅ When diagnosing system health or performance issues
- ✅ For handoffs between development sessions

**AVOID** in these situations:
- ❌ During active implementation (wait for natural pause)
- ❌ When system is under heavy load (>80% CPU/Memory)

**Example Triggers**:
```python
# User requests status
user_message = "What's been accomplished? What are we working on?"
# → Use activity-summary skill

# Scheduled report (cron job)
current_time = datetime.now()
if current_time.hour in [2, 4, 6, 8]:  # Every 2 hours
    # → Use activity-summary skill

# After parallel execution completes
parallel_batch_complete = True
# → Use activity-summary skill
```

---

## Skill Execution Steps

### Step 1: Collect Activity Data

**Data Sources**:
1. **Git commits** (last N hours)
2. **Running agents** (ps, status files)
3. **Worktrees** (git worktree list)
4. **ROADMAP** (completed vs in-progress priorities)
5. **Notifications** (recent activity alerts)
6. **Logs** (orchestrator, code_developer, architect)

**Commands**:

```bash
# 1. Get recent commits (last 6 hours)
SINCE_TIME=$(date -v -6H "+%Y-%m-%d %H:%M:%S")
git log --since="$SINCE_TIME" --pretty=format:"%h|%ai|%s" --no-merges

# 2. Check running agents
ps aux | grep -E "(code_developer|architect|code-reviewer|project_manager)" | grep python | grep -v grep

# 3. Check worktrees
git worktree list

# 4. Check agent status files
ls -la data/agent_status/*.json

# 5. Get recent notifications
sqlite3 data/notifications.db "SELECT type, title, created_at FROM notifications WHERE created_at > datetime('now', '-6 hours') ORDER BY created_at DESC LIMIT 20"
```

---

### Step 2: Analyze Completed Work

**Inputs Needed**:
- `$TIME_WINDOW`: Hours to look back (default: 6)
- `$ROADMAP_PATH`: Path to ROADMAP.md

**Actions**:

**1. Parse Git Commits**:
```python
from datetime import datetime, timedelta
import subprocess
import re

def get_recent_commits(hours: int = 6) -> List[Dict]:
    """Get commits from last N hours."""
    since = datetime.now() - timedelta(hours=hours)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = f'git log --since="{since_str}" --pretty=format:"%h|%ai|%s" --no-merges'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    commits = []
    for line in result.stdout.split('\n'):
        if not line:
            continue
        hash, date, subject = line.split('|', 2)

        # Extract US/PRIORITY from commit
        us_match = re.search(r'(US-\d+|PRIORITY \d+)', subject)

        commits.append({
            'hash': hash,
            'date': date,
            'subject': subject,
            'priority': us_match.group(1) if us_match else None
        })

    return commits
```

**2. Group by Priority**:
```python
from collections import defaultdict

def group_commits_by_priority(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Group commits by their priority."""
    by_priority = defaultdict(list)

    for commit in commits:
        priority = commit['priority'] or 'Other'
        by_priority[priority].append(commit)

    return dict(by_priority)
```

**3. Extract Completion Status**:
```python
def find_completed_priorities(commits: List[Dict]) -> List[str]:
    """Find priorities that were marked complete in commits."""
    completed = []

    for commit in commits:
        # Look for "Complete US-XXX" or "Implement US-XXX" patterns
        if re.search(r'(complete|implement|feat).*US-\d+', commit['subject'], re.I):
            if commit['priority']:
                completed.append(commit['priority'])

    return list(set(completed))
```

**Output**: Dictionary with completed priorities and their commits

---

### Step 3: Analyze Current Work

**Inputs Needed**:
- `$AGENT_STATUS_DIR`: Path to agent status files (default: `data/agent_status/`)

**Actions**:

**1. Check Running Agents**:
```python
import json
from pathlib import Path
import subprocess

def get_running_agents() -> List[Dict]:
    """Get all currently running agents."""
    agents = []

    # Method 1: Check process list
    cmd = 'ps aux | grep -E "(code_developer|architect|code-reviewer|project_manager)" | grep python | grep -v grep'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    for line in result.stdout.split('\n'):
        if not line:
            continue

        parts = line.split()
        pid = int(parts[1])

        # Extract agent type and priority from command
        cmd_line = ' '.join(parts[10:])

        agent_type = None
        priority = None

        if 'code_developer' in cmd_line or 'daemon' in cmd_line:
            agent_type = 'code_developer'
            priority_match = re.search(r'--priority[= ](\d+)', cmd_line)
            if priority_match:
                priority = priority_match.group(1)
        elif 'architect' in cmd_line:
            agent_type = 'architect'
        elif 'code-reviewer' in cmd_line:
            agent_type = 'code-reviewer'

        if agent_type:
            agents.append({
                'type': agent_type,
                'pid': pid,
                'priority': priority,
                'command': cmd_line
            })

    return agents
```

**2. Read Agent Status Files**:
```python
def get_agent_status_from_files() -> Dict[str, Dict]:
    """Read agent status from status files."""
    status_dir = Path("data/agent_status")
    statuses = {}

    for status_file in status_dir.glob("*.json"):
        try:
            status = json.loads(status_file.read_text())
            agent_type = status['agent_type']
            statuses[agent_type] = status
        except:
            continue

    return statuses
```

**3. Check Worktrees**:
```python
def get_active_worktrees() -> List[Dict]:
    """Get all active git worktrees."""
    cmd = 'git worktree list --porcelain'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    worktrees = []
    current_wt = {}

    for line in result.stdout.split('\n'):
        if line.startswith('worktree '):
            if current_wt:
                worktrees.append(current_wt)
            current_wt = {'path': line.split(' ', 1)[1]}
        elif line.startswith('branch '):
            current_wt['branch'] = line.split(' ', 1)[1]
        elif line.startswith('HEAD '):
            current_wt['commit'] = line.split(' ', 1)[1]

    if current_wt:
        worktrees.append(current_wt)

    # Filter out main worktree
    return [wt for wt in worktrees if '-wt' in wt['path']]
```

**Output**: Dictionary with running agents, their status, and active worktrees

---

### Step 4: Check Upcoming Work

**Inputs Needed**:
- `$ROADMAP_PATH`: Path to ROADMAP.md

**Actions**:

**1. Parse ROADMAP for Planned Priorities**:
```python
def get_planned_priorities(roadmap_path: Path, limit: int = 5) -> List[Dict]:
    """Get next N planned priorities from ROADMAP."""
    content = roadmap_path.read_text()

    planned = []

    # Find all priorities with "PLANNED" or "📝 Planned" status
    priority_pattern = r'##\s+(US-\d+|PRIORITY \d+):\s+(.+?)$'
    status_pattern = r'\*\*Status\*\*:\s*(.+?)$'

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Match priority header
        priority_match = re.match(priority_pattern, line)
        if priority_match:
            priority_name = priority_match.group(1)
            priority_title = priority_match.group(2)

            # Look ahead for status
            for j in range(i+1, min(i+10, len(lines))):
                status_match = re.match(status_pattern, lines[j])
                if status_match:
                    status = status_match.group(1)

                    if 'PLANNED' in status.upper() or '📝' in status:
                        planned.append({
                            'name': priority_name,
                            'title': priority_title,
                            'status': status
                        })

                        if len(planned) >= limit:
                            return planned
                    break

        i += 1

    return planned
```

**Output**: List of upcoming priorities

---

### Step 5: Generate Summary Report

**Inputs Needed**:
- `$COMPLETED_WORK`: From Step 2
- `$CURRENT_WORK`: From Step 3
- `$UPCOMING_WORK`: From Step 4
- `$TIME_WINDOW`: Hours covered by report

**Actions**:

**1. Format Summary**:
```python
def generate_summary_report(
    completed_work: Dict,
    current_work: Dict,
    upcoming_work: List[Dict],
    time_window: int = 6
) -> str:
    """Generate human-readable summary report."""

    report = f"""
# Development Activity Report
**Period**: Last {time_window} hours
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## ✅ Completed Work

"""

    # Completed priorities
    if completed_work.get('completed_priorities'):
        report += "### Priorities Completed:\n"
        for priority in completed_work['completed_priorities']:
            commits = completed_work['commits_by_priority'].get(priority, [])
            report += f"- **{priority}**: {len(commits)} commit(s)\n"
            for commit in commits[:3]:  # Show first 3 commits
                report += f"  - `{commit['hash']}` {commit['subject']}\n"
        report += "\n"
    else:
        report += "_No priorities completed in this period_\n\n"

    # All commits
    total_commits = len(completed_work.get('all_commits', []))
    report += f"**Total Commits**: {total_commits}\n\n"

    if total_commits > 0:
        report += "### Recent Commits:\n"
        for commit in completed_work['all_commits'][:10]:
            report += f"- `{commit['hash']}` {commit['subject']} _{commit['date']}_\n"
        report += "\n"

    report += "---\n\n"

    # Current work
    report += "## 🚀 Current Work in Progress\n\n"

    running_agents = current_work.get('running_agents', [])
    if running_agents:
        report += f"**Active Agents**: {len(running_agents)}\n\n"

        # Group by type
        by_type = {}
        for agent in running_agents:
            agent_type = agent['type']
            if agent_type not in by_type:
                by_type[agent_type] = []
            by_type[agent_type].append(agent)

        for agent_type, agents in by_type.items():
            report += f"### {agent_type.replace('_', ' ').title()} ({len(agents)})\n"
            for agent in agents:
                priority_str = f" - Priority {agent['priority']}" if agent['priority'] else ""
                report += f"- PID {agent['pid']}{priority_str}\n"
            report += "\n"
    else:
        report += "_No agents currently running_\n\n"

    # Worktrees
    worktrees = current_work.get('worktrees', [])
    if worktrees:
        report += f"**Active Worktrees**: {len(worktrees)}\n\n"
        for wt in worktrees:
            branch = wt.get('branch', 'unknown')
            path = wt.get('path', '')
            priority = re.search(r'wt(\d+)', path)
            priority_num = priority.group(1) if priority else '?'
            report += f"- Priority {priority_num}: `{branch}` at `{path}`\n"
        report += "\n"

    # Agent status details
    agent_statuses = current_work.get('agent_statuses', {})
    if agent_statuses:
        report += "### Agent Status Details:\n\n"
        for agent_type, status in agent_statuses.items():
            state = status.get('state', 'unknown')
            task = status.get('current_task', {})
            health = status.get('health', 'unknown')

            report += f"**{agent_type}**: {state} ({health})\n"
            if task:
                task_type = task.get('type', 'unknown')
                task_priority = task.get('priority', task.get('title', ''))
                report += f"  - Task: {task_type}"
                if task_priority:
                    report += f" ({task_priority})"
                report += "\n"
            report += "\n"

    report += "---\n\n"

    # Upcoming work
    report += "## 📋 Upcoming Work\n\n"

    if upcoming_work:
        report += f"**Next {len(upcoming_work)} Priorities**:\n\n"
        for i, priority in enumerate(upcoming_work, 1):
            report += f"{i}. **{priority['name']}**: {priority['title']}\n"
            report += f"   Status: {priority['status']}\n"
        report += "\n"
    else:
        report += "_No planned priorities found_\n\n"

    report += "---\n\n"

    # Summary statistics
    report += "## 📊 Summary Statistics\n\n"
    report += f"- Commits in period: {total_commits}\n"
    report += f"- Active agents: {len(running_agents)}\n"
    report += f"- Parallel worktrees: {len(worktrees)}\n"
    report += f"- Completed priorities: {len(completed_work.get('completed_priorities', []))}\n"
    report += f"- Upcoming priorities: {len(upcoming_work)}\n"

    return report
```

**2. Save Report**:
```python
def save_report(report: str, timestamp: datetime):
    """Save report to evidence directory."""
    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    filename = f"activity-summary-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
    report_path = evidence_dir / filename
    report_path.write_text(report)

    return report_path
```

**Output**: Formatted summary report (markdown)

---

### Step 6: Create Notification

**Inputs Needed**:
- `$REPORT`: Summary report from Step 5
- `$REPORT_PATH`: Path where report was saved

**Actions**:

```python
def create_summary_notification(report: str, report_path: Path):
    """Create notification with summary."""
    from coffee_maker.cli.notifications import NotificationDB

    # Extract key stats for notification
    stats_match = re.search(r'- Commits in period: (\d+)', report)
    commits = stats_match.group(1) if stats_match else '0'

    agents_match = re.search(r'- Active agents: (\d+)', report)
    agents = agents_match.group(1) if agents_match else '0'

    completed_match = re.search(r'- Completed priorities: (\d+)', report)
    completed = completed_match.group(1) if completed_match else '0'

    # Create concise notification
    title = "Development Activity Summary"
    message = f"""
Activity report generated for last 6 hours:

✅ Completed: {completed} priorities
🚀 Active: {agents} agents running
📝 Commits: {commits}

Full report: {report_path}
"""

    notifications = NotificationDB()
    notifications.create_notification(
        type="activity_summary",
        title=title,
        message=message.strip(),
        priority="normal",
        sound=False,  # CFR-009: No sound for background reports
        agent_id="orchestrator"
    )
```

**Output**: Notification created

---

## Example Workflow

### Scenario: Generate Status Report at 2AM

**Context**:
- User requested scheduled reports at 2AM, 4AM, 6AM
- Need to summarize last 2 hours of activity

**Execution**:

```python
from datetime import datetime
from pathlib import Path

# Step 1: Collect data
time_window = 2  # hours
commits = get_recent_commits(hours=time_window)
running_agents = get_running_agents()
agent_statuses = get_agent_status_from_files()
worktrees = get_active_worktrees()

# Step 2: Analyze completed work
commits_by_priority = group_commits_by_priority(commits)
completed_priorities = find_completed_priorities(commits)

completed_work = {
    'all_commits': commits,
    'commits_by_priority': commits_by_priority,
    'completed_priorities': completed_priorities
}

# Step 3: Analyze current work
current_work = {
    'running_agents': running_agents,
    'agent_statuses': agent_statuses,
    'worktrees': worktrees
}

# Step 4: Get upcoming work
roadmap_path = Path("docs/roadmap/ROADMAP.md")
upcoming_work = get_planned_priorities(roadmap_path, limit=5)

# Step 5: Generate report
report = generate_summary_report(
    completed_work=completed_work,
    current_work=current_work,
    upcoming_work=upcoming_work,
    time_window=time_window
)

# Step 6: Save and notify
timestamp = datetime.now()
report_path = save_report(report, timestamp)
create_summary_notification(report, report_path)

print(f"✅ Activity summary generated: {report_path}")
```

**Expected Output**:
```
# Development Activity Report
**Period**: Last 2 hours
**Generated**: 2025-10-21 02:00:15

---

## ✅ Completed Work

_No priorities completed in this period_

**Total Commits**: 3

### Recent Commits:
- `087909c` fix: Add missing type parameter to create_notification _2025-10-20 23:20:55_
- `24d5479` fix: Change level to priority in architect_coordinator notification _2025-10-20 23:19:42_
- `16b8931` fix: Enable parallel execution by skipping CFR-011 in worktrees _2025-10-20 23:18:30_

---

## 🚀 Current Work in Progress

**Active Agents**: 2

### Code Developer (2)
- PID 420 - Priority 038
- PID 421 - Priority 039

**Active Worktrees**: 2

- Priority 038: `roadmap-038` at `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt038`
- Priority 039: `roadmap-039` at `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt039`

---

## 📋 Upcoming Work

**Next 5 Priorities**:

1. **US-043**: Implement DoD Automation System
   Status: 📝 PLANNED
2. **US-031**: Create Advanced Prompt Engineering System
   Status: 📝 PLANNED
3. **US-112**: Implement Multi-Provider LLM Support
   Status: 📝 PLANNED

---

## 📊 Summary Statistics

- Commits in period: 3
- Active agents: 2
- Parallel worktrees: 2
- Completed priorities: 0
- Upcoming priorities: 5
```

---

## CLI Integration

**Add to orchestrator CLI**:

```python
# In coffee_maker/cli/orchestrator_cli.py

@cli.command()
@click.option('--hours', default=6, help='Hours to look back')
@click.option('--save', is_flag=True, help='Save report to evidence/')
def activity_summary(hours: int, save: bool):
    """Generate activity and progress summary."""
    # Use the skill
    from activity_summary_skill import generate_activity_summary

    report = generate_activity_summary(time_window=hours)

    click.echo(report)

    if save:
        timestamp = datetime.now()
        path = save_report(report, timestamp)
        click.echo(f"\n✅ Saved to: {path}")
```

**Usage**:
```bash
# Generate summary for last 6 hours
poetry run orchestrator activity-summary

# Generate for last 2 hours
poetry run orchestrator activity-summary --hours 2

# Save to file
poetry run orchestrator activity-summary --save
```

---

## Scheduled Reports (Cron)

**Setup cron job for scheduled reports**:

```bash
# Edit crontab
crontab -e

# Add these lines for 2AM, 4AM, 6AM reports
0 2 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run orchestrator activity-summary --save --hours 2
0 4 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run orchestrator activity-summary --save --hours 2
0 6 * * * cd /path/to/MonolithicCoffeeMakerAgent && poetry run orchestrator activity-summary --save --hours 2
```

**Alternative: Python scheduler**:

```python
import schedule
import time
from datetime import datetime

def scheduled_report():
    """Generate scheduled activity report."""
    report = generate_activity_summary(time_window=2)
    timestamp = datetime.now()
    path = save_report(report, timestamp)
    create_summary_notification(report, path)
    print(f"{timestamp}: Generated report at {path}")

# Schedule reports at 2AM, 4AM, 6AM
schedule.every().day.at("02:00").do(scheduled_report)
schedule.every().day.at("04:00").do(scheduled_report)
schedule.every().day.at("06:00").do(scheduled_report)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

---

## Success Criteria

**Skill succeeds when**:
- ✅ Report generated within 30 seconds
- ✅ All data sources successfully queried
- ✅ Report saved to evidence directory
- ✅ Notification created successfully
- ✅ Report is accurate and complete

**Skill fails when**:
- ❌ Unable to read ROADMAP
- ❌ Git commands fail
- ❌ Agent status files missing/corrupt
- ❌ Report generation times out

---

## Version History

**v1.0** (2025-10-20):
- Initial implementation
- Completed work analysis
- Current work tracking
- Upcoming work preview
- Scheduled report support

---

**Skill Version**: 1.0
**Last Updated**: 2025-10-20
**Owner**: orchestrator
