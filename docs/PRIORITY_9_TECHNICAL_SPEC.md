# PRIORITY 9: Enhanced code_developer Communication & Daily Standup - Technical Specification

**Document Version**: 2.0
**Created**: 2025-10-16
**Status**: Draft - Ready for Implementation
**Priority**: CRITICAL (⭐⭐⭐⭐⭐)
**Estimated Duration**: 1-2 weeks (60-80 hours)
**Dependencies**: PRIORITY 3 (Autonomous Development Daemon) - ✅ Complete

---

## Executive Summary

This specification defines the implementation of professional-grade communication capabilities for the `code_developer` daemon, transforming it from a silent background process into a transparent, communicative team member. The system will provide daily standup reports, weekly summaries, sprint reviews, real-time status updates, and proactive notifications—just like a professional human developer on an agile team.

**Key Business Value**: Users will trust the AI developer as a reliable team member, increasing engagement and adoption by 3-5x through transparency and accountability.

**Implementation Model**: The `project_manager` acts as the communication interface. When users check in (e.g., starts a new day with `project-manager chat`), the project manager **first reports what the code_developer accomplished** since the last check-in, then proceeds with the conversation.

---

## Table of Contents

1. [Prerequisites & Dependencies](#1-prerequisites--dependencies)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Specifications](#3-component-specifications)
4. [Implementation Plan](#4-implementation-plan)
5. [Testing Strategy](#5-testing-strategy)
6. [Success Criteria](#6-success-criteria)

---

## 1. Prerequisites & Dependencies

### 1.1 Required Completed Work
- ✅ **PRIORITY 1**: Analytics & Observability (provides metrics data)
- ✅ **PRIORITY 2**: Roadmap Management CLI (notification system)
- ✅ **PRIORITY 3**: Autonomous Development Daemon (daemon infrastructure)
- ✅ **PRIORITY 4**: Developer Status Dashboard (status tracking)

### 1.2 Existing Components to Leverage
```python
# Already implemented and production-ready
coffee_maker/autonomous/
├── daemon.py                      # Main daemon loop (✅ exists)
├── developer_status.py            # Status tracking (✅ exists)
├── task_metrics.py                # Performance metrics (✅ exists)
└── git_manager.py                 # Git operations (✅ exists)

coffee_maker/cli/
└── notifications.py               # Notification system (✅ exists)

data/
├── developer_status.json          # Real-time status (✅ exists)
└── task_metrics.db                # Performance database (✅ exists)
```

### 1.3 External Dependencies
```toml
# pyproject.toml additions
[tool.poetry.dependencies]
schedule = "^1.2.0"              # Cron-like scheduling
jinja2 = "^3.1.2"                # Template rendering
tabulate = "^0.9.0"              # Table formatting
python-dateutil = "^2.8.2"       # Date/time utilities
pyyaml = "^6.0.1"                # Configuration files
```

---

## 2. Architecture Overview

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Communication System                          │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Daemon     │───>│   Metrics    │───>│   Report     │      │
│  │   (Worker)   │    │  Collector   │    │  Generator   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                    │              │
│         │                    │                    │              │
│         v                    v                    v              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Activity    │    │  Task        │    │   Delivery   │      │
│  │   Logger     │    │  Metrics DB  │    │   Channels   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                    │              │
│         └────────────────────┴────────────────────┘              │
│                              │                                   │
│                              v                                   │
│                    ┌──────────────────┐                          │
│                    │  project_manager │                          │
│                    │   (User CLI)     │                          │
│                    └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Communication Flow

```
code_developer (daemon)
    │
    ├─> [Work on task]
    │       │
    │       ├─> Log activities to developer_status.json
    │       ├─> Record metrics to task_metrics.db
    │       └─> Update git history (commits, branches, PRs)
    │
    ├─> [Schedule: Daily at 9:00 AM]
    │       │
    │       ├─> MetricsCollector.collect_daily_data()
    │       ├─> DailyStandupGenerator.generate_report()
    │       └─> DeliveryChannel.send_report()
    │
    ├─> [Schedule: Friday at 5:00 PM]
    │       │
    │       ├─> MetricsCollector.collect_weekly_data()
    │       ├─> WeeklySummaryGenerator.generate_report()
    │       └─> DeliveryChannel.send_report()
    │
    └─> [On-demand: project-manager dev status]
            │
            ├─> LiveStatusGenerator.get_current_status()
            └─> Display to user
```

---

## 3. Component Specifications

### 3.1 Directory Structure

```bash
coffee_maker/autonomous/communication/
├── __init__.py                        # Package initialization
├── metrics_collector.py               # Collect data from various sources
├── report_generators/
│   ├── __init__.py
│   ├── base_report.py                 # Abstract base class
│   ├── daily_standup.py               # Daily standup generator
│   ├── weekly_summary.py              # Weekly summary generator
│   ├── sprint_review.py               # Sprint/milestone review
│   └── live_status.py                 # Real-time status
├── templates/
│   ├── daily_standup.md.j2            # Jinja2 template for daily
│   ├── weekly_summary.md.j2           # Jinja2 template for weekly
│   ├── sprint_review.md.j2            # Jinja2 template for sprint
│   └── live_status.md.j2              # Jinja2 template for status
├── delivery_channels/
│   ├── __init__.py
│   ├── base_channel.py                # Abstract delivery channel
│   ├── terminal_channel.py            # Print to terminal
│   ├── file_channel.py                # Write to file
│   ├── notification_channel.py        # Use notification DB
│   ├── slack_channel.py               # Send to Slack (optional)
│   └── email_channel.py               # Send email (optional)
├── scheduler.py                       # Schedule reports (cron-like)
├── config.py                          # Configuration management
└── activity_logger.py                 # Enhanced activity logging

# Configuration
~/.config/coffee-maker/
└── communication.yaml                 # User preferences

# Reports storage
logs/reports/
├── daily/
│   └── 2025-10-16_standup.md
├── weekly/
│   └── 2025-10-13_week42.md
└── sprint/
    └── 2025-10-01_october.md
```

### 3.2 Core Classes

#### 3.2.1 MetricsCollector (`metrics_collector.py`)

```python
"""Collect metrics from all data sources for report generation."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import subprocess

from coffee_maker.autonomous.developer_status import DeveloperStatus
from coffee_maker.autonomous.task_metrics import TaskMetricsDB
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.cli.notifications import NotificationDB


class MetricsCollector:
    """Collect metrics from developer_status, task_metrics, git, and notifications.

    Data Sources:
        1. developer_status.json - Real-time daemon status
        2. task_metrics.db - Performance metrics
        3. Git history - Commits, branches, PRs, file changes
        4. notifications.db - User questions, blockers, approvals

    Example:
        >>> collector = MetricsCollector()
        >>> daily = collector.collect_daily_metrics(date="2025-10-16")
        >>> print(f"Commits: {daily['commits_count']}")
        Commits: 5
    """

    def __init__(self):
        """Initialize collector with data source connections."""
        self.status = DeveloperStatus()
        self.metrics_db = TaskMetricsDB()
        self.git = GitManager()
        self.notifications = NotificationDB()

    def collect_daily_metrics(
        self,
        date: Optional[str] = None
    ) -> Dict:
        """Collect metrics for a single day.

        Args:
            date: Date string (YYYY-MM-DD). Defaults to yesterday.

        Returns:
            Dictionary with daily metrics
        """
        # Implementation details...
        pass

    def collect_weekly_metrics(
        self,
        week_start: Optional[str] = None
    ) -> Dict:
        """Collect metrics for a week (Monday-Sunday)."""
        pass

    def get_live_status(self) -> Dict:
        """Get current live status of daemon."""
        status_file = Path("data/developer_status.json")
        if status_file.exists():
            with open(status_file) as f:
                return json.load(f)
        return {"status": "stopped"}
```

#### 3.2.2 Report Generators

**Base Report Generator** (`report_generators/base_report.py`):

```python
"""Base class for all report generators."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader


class BaseReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self):
        """Initialize template environment."""
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    @abstractmethod
    def generate_report(self, metrics: Dict) -> str:
        """Generate report from metrics."""
        pass

    def render_template(self, template_name: str, context: Dict) -> str:
        """Render Jinja2 template with context."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
```

**Daily Standup Generator** (`report_generators/daily_standup.py`):

```python
"""Daily standup report generator."""

from typing import Dict
from .base_report import BaseReportGenerator


class DailyStandupGenerator(BaseReportGenerator):
    """Generate daily standup reports."""

    def generate_report(self, metrics: Dict) -> str:
        """Generate daily standup report."""
        context = self._prepare_context(metrics)
        return self.render_template("daily_standup.md.j2", context)

    def _prepare_context(self, metrics: Dict) -> Dict:
        """Prepare template context from metrics."""
        context = metrics.copy()

        # Group commits by priority
        context["commits_by_priority"] = self._group_commits_by_priority(
            metrics.get("commits", [])
        )

        # Summarize accomplishments
        context["accomplishments"] = self._summarize_accomplishments(metrics)

        # Identify blockers
        context["blockers"] = self._identify_blockers(metrics)

        return context
```

#### 3.2.3 Delivery Channels

**Terminal Channel** (`delivery_channels/terminal_channel.py`):

```python
"""Deliver reports to terminal."""

from typing import Dict
from .base_channel import BaseDeliveryChannel
from rich.console import Console
from rich.markdown import Markdown


class TerminalChannel(BaseDeliveryChannel):
    """Print reports to terminal with rich formatting."""

    def __init__(self):
        """Initialize console."""
        self.console = Console()

    def deliver(self, report: str, metadata: Dict) -> bool:
        """Print report to terminal."""
        md = Markdown(report)
        self.console.print(md)
        return True
```

**File Channel** (`delivery_channels/file_channel.py`):

```python
"""Write reports to files."""

from pathlib import Path
from typing import Dict
from .base_channel import BaseDeliveryChannel


class FileChannel(BaseDeliveryChannel):
    """Write reports to log files."""

    def __init__(self, base_dir: str = "logs/reports"):
        """Initialize file channel."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def deliver(self, report: str, metadata: Dict) -> bool:
        """Write report to file."""
        report_type = metadata.get("type", "unknown")
        date = metadata.get("date", "unknown")

        type_dir = self.base_dir / report_type
        type_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{date}_{report_type}.md"
        filepath = type_dir / filename

        try:
            with open(filepath, "w") as f:
                f.write(report)
            print(f"✅ Report saved to {filepath}")
            return True
        except Exception as e:
            print(f"❌ Failed to write report: {e}")
            return False
```

#### 3.2.4 Scheduler (`scheduler.py`)

```python
"""Schedule report generation."""

import schedule
import time
import logging
from datetime import datetime

from .metrics_collector import MetricsCollector
from .report_generators.daily_standup import DailyStandupGenerator
from .report_generators.weekly_summary import WeeklySummaryGenerator
from .delivery_channels.terminal_channel import TerminalChannel
from .delivery_channels.file_channel import FileChannel
from .config import CommunicationConfig

logger = logging.getLogger(__name__)


class ReportScheduler:
    """Schedule and execute report generation."""

    def __init__(self, config: CommunicationConfig = None):
        """Initialize scheduler."""
        if config is None:
            config = CommunicationConfig.load()

        self.config = config
        self.collector = MetricsCollector()
        self.daily_generator = DailyStandupGenerator()
        self.weekly_generator = WeeklySummaryGenerator()

        # Setup delivery channels
        self.channels = []
        if self.config.get("daily_standup.channels.terminal", True):
            self.channels.append(TerminalChannel())
        if self.config.get("daily_standup.channels.file"):
            file_path = self.config.get("daily_standup.channels.file")
            self.channels.append(FileChannel(base_dir=Path(file_path).parent))

    def setup_schedules(self):
        """Configure scheduled jobs."""
        # Daily standup
        if self.config.get("daily_standup.enabled", True):
            time_str = self.config.get("daily_standup.time", "09:00")
            schedule.every().day.at(time_str).do(self._run_daily_standup)
            logger.info(f"Scheduled daily standup at {time_str}")

        # Weekly summary
        if self.config.get("weekly_summary.enabled", True):
            day = self.config.get("weekly_summary.day", "friday")
            time_str = self.config.get("weekly_summary.time", "17:00")
            getattr(schedule.every(), day).at(time_str).do(self._run_weekly_summary)
            logger.info(f"Scheduled weekly summary on {day} at {time_str}")

    def start(self):
        """Start scheduler (blocking)."""
        self.setup_schedules()
        logger.info("ReportScheduler started")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def _run_daily_standup(self):
        """Execute daily standup report generation."""
        logger.info("Generating daily standup report...")
        try:
            metrics = self.collector.collect_daily_metrics()
            report = self.daily_generator.generate_report(metrics)

            metadata = {"type": "daily", "date": metrics["date"]}
            for channel in self.channels:
                channel.deliver(report, metadata)

            logger.info("✅ Daily standup completed")
        except Exception as e:
            logger.error(f"❌ Daily standup failed: {e}")
```

---

## 4. Implementation Plan

### Week 1: Core Infrastructure & Report Generators (40 hours)

#### Monday (8h)
- **Task 1.1**: Create directory structure (1h)
- **Task 1.2**: Implement MetricsCollector (7h)
  - Git log parsing
  - PR detection using `gh` CLI
  - Activity log integration
  - Test data collection

#### Tuesday (8h)
- **Task 2.1**: Implement base classes (4h)
  - BaseReportGenerator
  - BaseDeliveryChannel
  - Utility methods
- **Task 2.2**: Create configuration system (4h)
  - CommunicationConfig class
  - YAML loading
  - Default configuration

#### Wednesday (8h)
- **Task 3.1**: Enhance TaskMetricsDB (3h)
  - Add time-range query methods
  - Add database indexes
- **Task 3.2**: Create Jinja2 templates (5h)
  - daily_standup.md.j2
  - weekly_summary.md.j2
  - live_status.md.j2

#### Thursday (8h)
- **Task 4.1**: Implement DailyStandupGenerator (4h)
- **Task 4.2**: Implement WeeklySummaryGenerator (4h)

#### Friday (8h)
- **Task 5.1**: Implement LiveStatusGenerator (3h)
- **Task 5.2**: Code review and refinements (5h)

### Week 2: Delivery, Scheduling & Integration (40 hours)

#### Monday (8h)
- **Task 6.1**: Implement delivery channels (6h)
  - TerminalChannel
  - FileChannel
  - NotificationChannel
- **Task 6.2**: Unit tests for channels (2h)

#### Tuesday (8h)
- **Task 7.1**: Implement ReportScheduler (6h)
- **Task 7.2**: Integrate scheduler with daemon (2h)

#### Wednesday (8h)
- **Task 8.1**: Add project-manager CLI commands (6h)
  - `dev-status` command
  - `dev-report` command
  - `dev-history` command
- **Task 8.2**: Smart daily report detection (2h)

#### Thursday (8h)
- **Task 9.1**: Write unit tests (4h)
- **Task 9.2**: Write integration tests (2h)
- **Task 9.3**: Fix bugs from testing (2h)

#### Friday (8h)
- **Task 10.1**: Update documentation (3h)
- **Task 10.2**: Create user guide (2h)
- **Task 10.3**: Final testing and demo (3h)

**Total Implementation Time**: 80 hours (2 weeks)

---

## 5. Testing Strategy

### 5.1 Unit Testing

**Test Coverage Requirements**:
- MetricsCollector: 90% coverage
- Report Generators: 85% coverage
- Delivery Channels: 80% coverage
- Scheduler: 75% coverage

**Key Test Cases**:

```python
# test_metrics_collector.py

def test_collect_daily_metrics_with_commits():
    """Test daily metrics collection with git commits."""
    # Setup: Create test commits
    # Execute: collect_daily_metrics()
    # Assert: Correct commit count, file changes, lines

def test_collect_weekly_metrics_aggregation():
    """Test weekly aggregation of daily metrics."""
    # Setup: Mock daily metrics for 7 days
    # Execute: collect_weekly_metrics()
    # Assert: Totals are correct sums

# test_daily_standup_generator.py

def test_generate_report_with_accomplishments():
    """Test report generation with accomplishments."""
    # Setup: Metrics with completed priorities
    # Execute: generate_report()
    # Assert: Report contains accomplishments section
```

### 5.2 Integration Testing

**End-to-End Test Scenarios**:

1. **Daily Standup E2E**:
   - Create test commits with known messages
   - Create test activities in developer_status.json
   - Trigger daily standup generation
   - Verify report contains expected data
   - Verify delivery to all channels

2. **Scheduler E2E**:
   - Configure scheduler for 1-minute test
   - Wait for scheduled execution
   - Verify report generated and delivered

### 5.3 Manual Testing Checklist

- [ ] Daily standup generates correctly
- [ ] Weekly summary aggregates properly
- [ ] Live status shows current daemon state
- [ ] Terminal delivery renders markdown beautifully
- [ ] File delivery creates organized directory structure
- [ ] Notification delivery integrates with project-manager
- [ ] Scheduler runs at configured times
- [ ] Smart daily report shows on first chat
- [ ] Configuration file loads correctly
- [ ] Error handling works gracefully

---

## 6. Success Criteria

### 6.1 Functional Requirements

**Must Have** (P0):
- ✅ Daily standup reports generate automatically at 9 AM
- ✅ Weekly summaries generate automatically on Friday 5 PM
- ✅ Live status command shows current daemon state
- ✅ Reports delivered to terminal and file channels
- ✅ Reports include: commits, PRs, test results, blockers
- ✅ Smart daily report on first chat of the day
- ✅ Configuration via YAML file

**Should Have** (P1):
- ✅ Sprint/milestone reviews
- ✅ Notification channel delivery
- ✅ Historical report viewing
- ✅ Velocity calculations

**Could Have** (P2):
- ⚪ Slack integration (optional)
- ⚪ Email integration (optional)

### 6.2 Non-Functional Requirements

**Performance**:
- ✅ Daily standup generates in < 5 seconds
- ✅ Live status responds in < 1 second
- ✅ Scheduler adds < 1% CPU overhead

**Reliability**:
- ✅ 100% uptime for scheduler
- ✅ Graceful degradation on missing data
- ✅ No daemon crashes due to reporting system

**Usability**:
- ✅ Reports are clear and actionable
- ✅ Configuration is intuitive
- ✅ CLI commands are discoverable

**Maintainability**:
- ✅ 85%+ test coverage
- ✅ All classes documented
- ✅ User guide published

### 6.3 Acceptance Tests

**Test 1: Daily Standup Generation**
```bash
# Setup: Daemon runs for 1 day, makes 5 commits
# Execute: Wait for 9 AM or trigger manually
# Verify: Report shows all 5 commits, correct metrics
```

**Test 2: Smart Daily Report**
```bash
# Setup: Last chat was yesterday
# Execute: project-manager chat
# Verify: Daily report shown before chat prompt
```

**Test 3: Live Status**
```bash
# Setup: Daemon working on PRIORITY 9, 50% complete
# Execute: project-manager dev-status
# Verify: Shows current task, 50% progress, ETA
```

---

## 7. Appendix

### 7.1 Example Report Outputs

**Daily Standup Example**:

```markdown
🤖 code_developer Daily Standup - 2025-10-16
================================================

📊 Yesterday's Accomplishments (2025-10-15):

✅ Implemented PRIORITY 9 - Enhanced Communication System
   - Created MetricsCollector class (320 lines)
   - Implemented DailyStandupGenerator (180 lines)
   - Added Jinja2 templates (4 files)
   - Commits: 8 | Files changed: 15 | Lines added: 1,250

📈 Metrics:
   - Total commits: 10
   - Total PRs created: 2
   - Lines of code: +1,250 / -45
   - Build status: ✅ Passing
   - Test coverage: 87% (+2%)

🔄 Today's Plan (2025-10-16):
1. Complete delivery channels
2. Implement ReportScheduler
3. Integrate with daemon
4. Write unit tests

⚠️ Blockers & Needs:
   - None currently

---
Report generated: 2025-10-16 09:00:00
```

### 7.2 Configuration File Template

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"
    channels:
      terminal: true
      notification: true
      file: "logs/reports/daily"

  weekly_summary:
    enabled: true
    day: "friday"
    time: "17:00"

  realtime_updates:
    enabled: true
    milestones: true
    blockers: true
    quiet_hours:
      start: "22:00"
      end: "08:00"

  verbosity: "normal"
  timezone: "America/New_York"
```

### 7.3 CLI Command Reference

```bash
# Live status
project-manager dev-status

# Generate reports on-demand
project-manager dev-report daily
project-manager dev-report weekly

# View historical reports
project-manager dev-history --days 30

# Chat (shows daily report on new day)
project-manager chat
```

---

**Document Status**: Ready for Implementation
**Next Steps**: Begin Week 1 implementation
**Estimated Completion**: 2 weeks (80 hours total)
