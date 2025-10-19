# SPEC-054: Architect Daily Integration of code-searcher Findings (CFR-011)

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: US-054, CFR-011
**Estimated Duration**: 1-2 days (8-16 hours)

---

## Executive Summary

Implement CFR-011 enforcement: architect MUST read code-searcher analysis reports daily AND analyze the codebase weekly before being allowed to create new technical specifications. This creates a continuous feedback loop where code quality findings are systematically integrated into architectural decisions.

**Key Innovation**: Block spec creation until architect reviews all findings, ensuring technical debt and refactoring opportunities are addressed proactively.

---

## 🔍 Architecture Reuse Check (MANDATORY)

### Problem Domain
**Data tracking + Workflow enforcement** - Need to track architect's integration activities and enforce compliance before spec creation.

### Existing Components Evaluated

#### 1. File-based Tracking (Pattern from DeveloperStatus)
- **Location**: `coffee_maker/autonomous/developer_status.py`
- **Functionality**: JSON file tracking of agent state
- **Fitness**: 95% (perfect fit for tracking architect activities)
- **Decision**: ✅ **REUSE** this pattern
- **Rationale**:
  - Proven pattern in codebase (DeveloperStatus uses it)
  - Simple JSON file tracking (no database needed)
  - Atomic writes with file_io utilities
  - Easy to query and update

#### 2. CLI Command Pattern (From roadmap_cli.py)
- **Location**: `coffee_maker/cli/roadmap_cli.py`
- **Functionality**: Click-based CLI commands
- **Fitness**: 100% (exact match for `architect` commands)
- **Decision**: ✅ **REUSE** existing CLI patterns
- **Rationale**:
  - Consistent with project CLI conventions
  - Click library already used throughout
  - Easy to integrate with existing CLI

#### 3. Validation Exceptions (Pattern from AgentRegistry)
- **Location**: `coffee_maker/autonomous/agent_registry.py` (`AgentAlreadyRunningError`)
- **Functionality**: Custom exceptions for enforcement
- **Fitness**: 100% (same pattern for CFR-011 violations)
- **Decision**: ✅ **REUSE** this pattern
- **Rationale**:
  - Proven enforcement pattern (singleton enforcement)
  - Clear error messages
  - Catchable for graceful handling

#### 4. code-searcher Report Reading
- **Location**: `docs/code-searcher/*.md` (analysis reports)
- **Functionality**: Read and parse analysis reports
- **Fitness**: 100% (just read markdown files)
- **Decision**: ✅ **REUSE** simple file reading
- **Rationale**:
  - Reports are markdown files (easy to read)
  - No special parsing needed (just check if read)

### Final Decision

**Chosen Approach**: ✅ **REUSE existing patterns** (no new infrastructure needed)

**Reuse Benefits**:
- ✅ No new architectural components (simple JSON + CLI + exceptions)
- ✅ Uses proven patterns from DeveloperStatus and AgentRegistry
- ✅ Consistent with project conventions
- ✅ Easy to test (mock JSON file)

**Trade-offs Accepted**:
- ⚠️ Manual tracking (architect must call CLI commands)
- ✅ But: Simple and explicit (no hidden automation)

---

## Problem Statement

### Current Situation
code-searcher produces valuable analysis reports:
- `docs/code-searcher/CODE_QUALITY_ANALYSIS_2025-10-17.md`
- `docs/code-searcher/SECURITY_AUDIT_2025-10-18.md`
- etc.

**But architect ignores them**:
- Reports sit unread
- Technical debt accumulates
- Duplicate code not identified
- Refactoring opportunities missed

**No enforcement**:
- Nothing requires architect to read reports
- No tracking of when reports were reviewed
- No weekly codebase analysis

### Goal
Implement CFR-011 enforcement where:
1. architect MUST read ALL code-searcher reports before creating specs
2. architect MUST analyze codebase weekly (max 7 days between analyses)
3. Spec creation BLOCKED if violations detected
4. Tracking data maintained for compliance

### Non-Goals
- ❌ Automatic report summarization (architect reads full reports)
- ❌ AI-generated action items (architect extracts manually)
- ❌ Database tracking (simple JSON file sufficient)

---

## Prerequisites & Dependencies

### Required Utilities
- ✅ **`coffee_maker.utils.file_io`**: JSON read/write utilities (already exists)
  - `read_json_file(path, default=None)`: Read JSON with default fallback
  - `write_json_file(path, data, indent=2)`: Write JSON with formatting
  - `atomic_write_json(path, data)`: Atomic writes to prevent corruption

### Required Packages
- ✅ **radon>=6.0**: Code complexity metrics (pre-approved)
- ✅ **pytest>=7.0**: Test coverage analysis (pre-approved)

### Dependencies
- None (standalone utility)

---

## Architecture Overview

### Components (REUSE existing patterns)

```
┌─────────────────────────────────────────────────────────────┐
│                    Architect Workflow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. architect daily-integration                              │
│     ↓                                                        │
│  2. Check for new code-searcher reports                      │
│     ↓                                                        │
│  3. Read all unread reports                                  │
│     ↓                                                        │
│  4. Extract action items (manual)                            │
│     ↓                                                        │
│  5. Update tracking file (architect_integration_status.json) │
│     ↓                                                        │
│  6. architect analyze-codebase (weekly)                      │
│     ↓                                                        │
│  7. Scan codebase for issues                                 │
│     ↓                                                        │
│  8. Document findings in analysis report                     │
│     ↓                                                        │
│  9. Update tracking file (last_codebase_analysis)            │
│                                                              │
│  SPEC CREATION ENFORCEMENT:                                  │
│  Before creating spec → Check tracking file                  │
│  If violations → Raise CFR011ViolationError                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```python
# Tracking file: data/architect_integration_status.json
{
    "last_code_searcher_read": "2025-10-18",
    "last_codebase_analysis": "2025-10-18",
    "reports_read": [
        "CODE_QUALITY_ANALYSIS_2025-10-17.md",
        "SECURITY_AUDIT_2025-10-18.md"
    ],
    "refactoring_specs_created": 4,
    "specs_updated": 6,
    "next_analysis_due": "2025-10-25"  # 7 days from last analysis
}
```

---

## Component Specifications

### 1. ArchitectDailyRoutine Class

**File**: `coffee_maker/autonomous/architect_daily_routine.py`

**Purpose**: Encapsulate daily integration and weekly analysis logic

```python
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from coffee_maker.utils.file_io import read_json_file, write_json_file

class CFR011ViolationError(Exception):
    """Raised when architect violates CFR-011."""
    pass

class ArchitectDailyRoutine:
    """Manages architect's daily integration of code-searcher findings."""

    TRACKING_FILE = Path("data/architect_integration_status.json")
    REPORTS_DIR = Path("docs/code-searcher")
    MAX_DAYS_BETWEEN_ANALYSIS = 7

    def __init__(self):
        """Initialize with tracking data."""
        self.status = self._load_status()

    def _load_status(self) -> Dict:
        """Load tracking data from JSON file."""
        # Use read_json_file with default parameter
        return read_json_file(
            self.TRACKING_FILE,
            default={
                "last_code_searcher_read": None,
                "last_codebase_analysis": None,
                "reports_read": [],
                "refactoring_specs_created": 0,
                "specs_updated": 0,
                "next_analysis_due": None
            }
        )

    def _save_status(self):
        """Save tracking data to JSON file (atomic write)."""
        write_json_file(self.TRACKING_FILE, self.status)

    def get_unread_reports(self) -> List[Path]:
        """Find all code-searcher reports not yet read."""
        if not self.REPORTS_DIR.exists():
            return []

        all_reports = list(self.REPORTS_DIR.glob("*.md"))
        read_reports = set(self.status["reports_read"])

        unread = [
            report for report in all_reports
            if report.name not in read_reports
        ]

        return sorted(unread, key=lambda p: p.stat().st_mtime)

    def mark_reports_read(self, reports: List[Path]):
        """Mark reports as read and update tracking."""
        for report in reports:
            if report.name not in self.status["reports_read"]:
                self.status["reports_read"].append(report.name)

        self.status["last_code_searcher_read"] = datetime.now().strftime("%Y-%m-%d")
        self._save_status()

    def is_codebase_analysis_due(self) -> bool:
        """Check if weekly codebase analysis is due."""
        if not self.status["last_codebase_analysis"]:
            return True  # Never analyzed, due now

        last_analysis = datetime.strptime(
            self.status["last_codebase_analysis"],
            "%Y-%m-%d"
        )
        days_since = (datetime.now() - last_analysis).days

        return days_since >= self.MAX_DAYS_BETWEEN_ANALYSIS

    def mark_codebase_analyzed(self):
        """Mark codebase as analyzed and update tracking."""
        today = datetime.now()
        self.status["last_codebase_analysis"] = today.strftime("%Y-%m-%d")
        self.status["next_analysis_due"] = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        self._save_status()

    def enforce_cfr_011(self):
        """Enforce CFR-011 before spec creation.

        Raises:
            CFR011ViolationError: If violations detected
        """
        violations = []

        # Check for unread reports
        unread = self.get_unread_reports()
        if unread:
            violations.append(
                f"Unread code-searcher reports: {', '.join(r.name for r in unread)}"
            )

        # Check if weekly analysis due
        if self.is_codebase_analysis_due():
            last = self.status["last_codebase_analysis"] or "NEVER"
            violations.append(
                f"Weekly codebase analysis overdue (last: {last})"
            )

        if violations:
            raise CFR011ViolationError(
                "CFR-011 violation detected! Cannot create spec until resolved:\n"
                + "\n".join(f"  - {v}" for v in violations)
                + "\n\nActions required:"
                + "\n  1. Run: architect daily-integration"
                + "\n  2. Run: architect analyze-codebase"
            )

    def get_compliance_status(self) -> Dict:
        """Get current CFR-011 compliance status."""
        return {
            "compliant": len(self.get_unread_reports()) == 0 and not self.is_codebase_analysis_due(),
            "last_code_searcher_read": self.status["last_code_searcher_read"],
            "last_codebase_analysis": self.status["last_codebase_analysis"],
            "unread_reports": [r.name for r in self.get_unread_reports()],
            "analysis_due": self.is_codebase_analysis_due(),
            "next_analysis_due": self.status["next_analysis_due"],
            "reports_read": len(self.status["reports_read"]),
            "refactoring_specs_created": self.status["refactoring_specs_created"],
            "specs_updated": self.status["specs_updated"]
        }
```

### 2. CLI Commands

**File**: `coffee_maker/cli/architect_cli.py` (new file)

```python
import click
from pathlib import Path
from coffee_maker.autonomous.architect_daily_routine import ArchitectDailyRoutine, CFR011ViolationError

@click.group()
def architect():
    """Architect agent CLI commands."""
    pass

@architect.command()
def daily_integration():
    """Guided workflow for reading code-searcher reports."""
    routine = ArchitectDailyRoutine()

    # Check for unread reports
    unread = routine.get_unread_reports()

    if not unread:
        click.echo("✅ No unread code-searcher reports. You're up to date!")
        return

    click.echo(f"📋 Found {len(unread)} unread code-searcher report(s):\n")

    for i, report in enumerate(unread, 1):
        click.echo(f"  {i}. {report.name}")

    click.echo("\n📖 Please read all reports now:")

    for report in unread:
        click.echo(f"\n{'='*60}")
        click.echo(f"Reading: {report.name}")
        click.echo('='*60)

        # Display report content
        content = report.read_text(encoding="utf-8")
        click.echo(content)

        click.echo('\n' + '='*60)

        # Confirm read
        if click.confirm("Have you read this report and extracted action items?"):
            routine.mark_reports_read([report])
            click.echo(f"✅ Marked {report.name} as read")
        else:
            click.echo(f"⚠️  Skipping {report.name} - you must read it later")

    click.echo("\n✅ Daily integration complete!")

@architect.command()
def analyze_codebase():
    """Perform weekly codebase analysis.

    Analysis includes:
    1. Radon complexity metrics (cyclomatic complexity average)
    2. Large file detection (>500 LOC)
    3. Test coverage analysis (pytest --cov)
    4. TODO/FIXME comment extraction
    5. Code duplication detection (basic pattern matching)

    Output: Synthetic 1-2 page report saved to docs/architecture/
    """
    routine = ArchitectDailyRoutine()

    click.echo("🔍 Starting weekly codebase analysis...\n")

    # Check if analysis is due
    if not routine.is_codebase_analysis_due():
        last = routine.status["last_codebase_analysis"]
        next_due = routine.status["next_analysis_due"]
        click.echo(f"ℹ️  Analysis not due yet:")
        click.echo(f"   Last analysis: {last}")
        click.echo(f"   Next due: {next_due}")

        if not click.confirm("\nPerform analysis anyway?"):
            return

    click.echo("📊 Analyzing codebase for:")
    click.echo("  - Complexity metrics (radon --average)")
    click.echo("  - Large files (>500 LOC)")
    click.echo("  - Test coverage (pytest --cov)")
    click.echo("  - TODO/FIXME comments")
    click.echo("\n(This may take 5-10 minutes...)\n")

    # Perform codebase analysis
    import subprocess
    from datetime import datetime

    results = {}

    # 1. Radon complexity analysis
    try:
        result = subprocess.run(
            ["radon", "cc", "coffee_maker/", "--average"],
            capture_output=True,
            text=True
        )
        results["complexity"] = result.stdout
    except Exception as e:
        click.echo(f"⚠️  Radon analysis failed: {e}")
        results["complexity"] = "Failed to analyze"

    # 2. Large file detection
    large_files = []
    for py_file in Path("coffee_maker/").rglob("*.py"):
        line_count = len(py_file.read_text().splitlines())
        if line_count > 500:
            large_files.append((str(py_file), line_count))
    results["large_files"] = large_files

    # 3. Test coverage
    try:
        result = subprocess.run(
            ["pytest", "--cov=coffee_maker", "--cov-report=term"],
            capture_output=True,
            text=True
        )
        results["coverage"] = result.stdout
    except Exception as e:
        click.echo(f"⚠️  Coverage analysis failed: {e}")
        results["coverage"] = "Failed to analyze"

    # 4. TODO/FIXME extraction
    todos = []
    for py_file in Path("coffee_maker/").rglob("*.py"):
        for i, line in enumerate(py_file.read_text().splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                todos.append((str(py_file), i, line.strip()))
    results["todos"] = todos[:20]  # Limit to top 20

    # 5. Generate synthetic report
    report_path = Path(f"docs/architecture/CODEBASE_ANALYSIS_{datetime.now().strftime('%Y-%m-%d')}.md")
    report_content = f"""# Codebase Analysis Report

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Scope**: coffee_maker/

## Complexity Metrics

```
{results["complexity"]}
```

## Large Files (>500 LOC)

"""
    if large_files:
        for file, loc in large_files:
            report_content += f"- `{file}`: {loc} lines\n"
    else:
        report_content += "✅ No files exceed 500 LOC\n"

    report_content += f"""

## Test Coverage

```
{results["coverage"]}
```

## TODO/FIXME Comments ({len(todos)} found, showing top 20)

"""
    for file, line_num, line_content in todos:
        report_content += f"- `{file}:{line_num}`: {line_content}\n"

    report_content += f"""

## Recommendations

**Based on analysis**:
1. Review large files (>500 LOC) for potential refactoring opportunities
2. Address TODO/FIXME comments systematically
3. Maintain test coverage above 80%

**Next Analysis**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""

    # Save report
    report_path.write_text(report_content)
    click.echo(f"\n📄 Report saved: {report_path}")

    # Mark as analyzed
    routine.mark_codebase_analyzed()

    click.echo(f"\n✅ Codebase analysis complete!")
    click.echo(f"   Next analysis due: {routine.status['next_analysis_due']}")

@architect.command("cfr-011-status")
def cfr_011_status():
    """Check CFR-011 compliance status."""
    routine = ArchitectDailyRoutine()

    status = routine.get_compliance_status()

    click.echo("\n📋 CFR-011 Compliance Status\n")
    click.echo("="*60)

    if status["compliant"]:
        click.echo("✅ COMPLIANT - No violations detected\n")
    else:
        click.echo("❌ NOT COMPLIANT - Violations detected\n")

    click.echo(f"Last code-searcher read: {status['last_code_searcher_read'] or 'NEVER'}")
    click.echo(f"Last codebase analysis: {status['last_codebase_analysis'] or 'NEVER'}")
    click.echo(f"Next analysis due: {status['next_analysis_due'] or 'ASAP'}\n")

    if status["unread_reports"]:
        click.echo(f"⚠️  Unread reports ({len(status['unread_reports'])}):")
        for report in status["unread_reports"]:
            click.echo(f"  - {report}")
        click.echo()

    if status["analysis_due"]:
        click.echo("⚠️  Weekly codebase analysis is OVERDUE\n")

    click.echo("Metrics:")
    click.echo(f"  Reports read: {status['reports_read']}")
    click.echo(f"  Refactoring specs created: {status['refactoring_specs_created']}")
    click.echo(f"  Specs updated: {status['specs_updated']}")

    if not status["compliant"]:
        click.echo("\n📝 Actions Required:")
        if status["unread_reports"]:
            click.echo("  1. Run: architect daily-integration")
        if status["analysis_due"]:
            click.echo("  2. Run: architect analyze-codebase")

    click.echo()

if __name__ == "__main__":
    architect()
```

### 3. Integration with Spec Creation

**Modify**: `coffee_maker/autonomous/daemon_spec_manager.py` (or wherever architect creates specs)

```python
from coffee_maker.autonomous.architect_daily_routine import ArchitectDailyRoutine, CFR011ViolationError

class SpecManagerMixin:
    """Mixin for spec creation (code_developer daemon)."""

    def _ensure_technical_spec(self, priority_name: str) -> Path:
        """Ensure technical spec exists.

        IMPORTANT: This method is being phased out per US-047.
        architect should create specs proactively, NOT reactively.
        """

        # BEFORE creating any spec, enforce CFR-011
        routine = ArchitectDailyRoutine()

        try:
            routine.enforce_cfr_011()
        except CFR011ViolationError as e:
            logger.error(f"CFR-011 violation detected: {e}")
            # Notify user
            self.notifications.create_notification(
                type="cfr_violation",
                title="CFR-011 Violation: architect Must Review Findings",
                body=str(e),
                sound=False  # Background agent (CFR-009)
            )
            raise  # Block spec creation

        # Continue with spec creation...
        # (rest of existing logic)
```

---

## Implementation Plan

### Phase 1: Core Implementation (Day 1 - 4-6 hours)

**Tasks**:
1. Create `ArchitectDailyRoutine` class
   - File: `coffee_maker/autonomous/architect_daily_routine.py`
   - Implement all methods
   - Add docstrings and type hints
2. Create `CFR011ViolationError` exception
3. Create tracking file structure
   - Directory: `data/`
   - File: `architect_integration_status.json`
4. Write unit tests for `ArchitectDailyRoutine`
   - Test: `tests/unit/test_architect_daily_routine.py`
   - Coverage: 100%

### Phase 2: CLI Commands (Day 1 - 2-3 hours)

**Tasks**:
1. Create `architect_cli.py`
   - File: `coffee_maker/cli/architect_cli.py`
   - Implement `architect daily-integration`
   - Implement `architect analyze-codebase`
   - Implement `architect cfr-011-status`
2. Register CLI commands in `pyproject.toml`
   ```toml
   [tool.poetry.scripts]
   architect = "coffee_maker.cli.architect_cli:architect"
   ```
3. Test CLI commands manually

### Phase 3: Spec Creation Integration (Day 2 - 3-4 hours)

**Tasks**:
1. Modify `daemon_spec_manager.py`
   - Add CFR-011 enforcement before spec creation
   - Add error handling (catch `CFR011ViolationError`)
   - Add user notification on violation
2. Test integration with daemon
   - Simulate violation (unread reports)
   - Verify spec creation blocked
   - Verify user notification sent

### Phase 4: Testing & Documentation (Day 2 - 2-3 hours)

**Tasks**:
1. Integration tests
   - Test: Spec creation blocked when violations exist
   - Test: Spec creation allowed when compliant
2. Documentation updates
   - Update CFR-011 in `CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
   - Update `.claude/CLAUDE.md` with new workflow
   - Update `architect.md` with daily routine
3. Create user guide
   - Document: `docs/architecture/ARCHITECT_DAILY_ROUTINE_GUIDE.md`

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_architect_daily_routine.py`

```python
import pytest
from pathlib import Path
from coffee_maker.autonomous.architect_daily_routine import (
    ArchitectDailyRoutine,
    CFR011ViolationError
)

def test_get_unread_reports_empty(tmp_path, monkeypatch):
    """Test when no reports exist."""
    monkeypatch.setattr(ArchitectDailyRoutine, "REPORTS_DIR", tmp_path)

    routine = ArchitectDailyRoutine()
    unread = routine.get_unread_reports()

    assert unread == []

def test_get_unread_reports_some_unread(tmp_path, monkeypatch):
    """Test when some reports are unread."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Create reports
    report1 = reports_dir / "ANALYSIS_2025-10-17.md"
    report2 = reports_dir / "AUDIT_2025-10-18.md"
    report1.write_text("Report 1")
    report2.write_text("Report 2")

    monkeypatch.setattr(ArchitectDailyRoutine, "REPORTS_DIR", reports_dir)

    routine = ArchitectDailyRoutine()

    # Mark report1 as read
    routine.mark_reports_read([report1])

    # Get unread
    unread = routine.get_unread_reports()

    assert len(unread) == 1
    assert unread[0].name == "AUDIT_2025-10-18.md"

def test_enforce_cfr_011_violation_unread_reports(tmp_path, monkeypatch):
    """Test CFR-011 enforcement with unread reports."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    report = reports_dir / "ANALYSIS.md"
    report.write_text("Report")

    monkeypatch.setattr(ArchitectDailyRoutine, "REPORTS_DIR", reports_dir)

    routine = ArchitectDailyRoutine()

    with pytest.raises(CFR011ViolationError, match="Unread code-searcher reports"):
        routine.enforce_cfr_011()

def test_enforce_cfr_011_violation_analysis_due(tmp_path, monkeypatch):
    """Test CFR-011 enforcement when weekly analysis due."""
    routine = ArchitectDailyRoutine()

    # Never analyzed
    with pytest.raises(CFR011ViolationError, match="Weekly codebase analysis overdue"):
        routine.enforce_cfr_011()

def test_enforce_cfr_011_compliant(tmp_path, monkeypatch):
    """Test CFR-011 enforcement when compliant."""
    routine = ArchitectDailyRoutine()

    # Mark as analyzed today
    routine.mark_codebase_analyzed()

    # Should not raise
    routine.enforce_cfr_011()
```

### Integration Tests

**File**: `tests/ci_tests/test_cfr_011_integration.py`

```python
def test_spec_creation_blocked_on_violation():
    """Test that spec creation is blocked when CFR-011 violated."""
    # TODO: Implement after daemon integration

def test_spec_creation_allowed_when_compliant():
    """Test that spec creation is allowed when CFR-011 compliant."""
    # TODO: Implement after daemon integration
```

---

## Rollout Plan

### Week 1: Implementation

- Day 1-2: Implement ArchitectDailyRoutine + CLI + Integration
- Day 2: Testing + Documentation

### Week 2: Validation

- architect uses CLI commands daily for 1 week
- Collect feedback on workflow
- Fix any usability issues

### Week 3: Full Enforcement

- Enable CFR-011 enforcement in daemon
- Monitor for violations
- Adjust as needed

---

## Success Criteria

**Functional**:
- [ ] `ArchitectDailyRoutine` class implemented with 100% test coverage
- [ ] CLI commands working: `architect daily-integration`, `architect analyze-codebase`, `architect cfr-011-status`
- [ ] Tracking file maintained correctly
- [ ] Spec creation blocked when violations exist
- [ ] Spec creation allowed when compliant
- [ ] User notifications sent on violations

**Quality**:
- [ ] All unit tests pass (100% coverage)
- [ ] Integration tests pass
- [ ] Documentation complete (ARCHITECT_DAILY_ROUTINE_GUIDE.md)
- [ ] CFR-011 enforced system-wide

**User Experience**:
- [ ] CLI commands easy to use (guided workflow)
- [ ] Clear error messages on violations
- [ ] Compliance status visible (`architect cfr-011-status`)

---

## Risk Analysis

**Risks**:
1. **architect forgets to run daily-integration**: MITIGATION: Send daily reminders
2. **Workflow too manual**: MITIGATION: Start simple, automate later if needed
3. **Reports too numerous**: MITIGATION: Limit code-searcher to 1-2 reports/week

**Assumptions**:
- architect will use CLI commands as intended
- code-searcher produces <5 reports/week
- Weekly codebase analysis can be done in <2 hours

---

## Appendix: Example Usage

### Example 1: Daily Integration

```bash
$ architect daily-integration

📋 Found 2 unread code-searcher report(s):

  1. CODE_QUALITY_ANALYSIS_2025-10-17.md
  2. SECURITY_AUDIT_2025-10-18.md

📖 Please read all reports now:

============================================================
Reading: CODE_QUALITY_ANALYSIS_2025-10-17.md
============================================================
[report content displayed]

============================================================

Have you read this report and extracted action items? [y/N]: y
✅ Marked CODE_QUALITY_ANALYSIS_2025-10-17.md as read

[... repeat for next report ...]

✅ Daily integration complete!
```

### Example 2: CFR-011 Status Check

```bash
$ architect cfr-011-status

📋 CFR-011 Compliance Status

============================================================
✅ COMPLIANT - No violations detected

Last code-searcher read: 2025-10-18
Last codebase analysis: 2025-10-18
Next analysis due: 2025-10-25

Metrics:
  Reports read: 12
  Refactoring specs created: 4
  Specs updated: 6
```

### Example 3: Spec Creation Blocked

```python
# architect tries to create spec without reading reports

try:
    spec = architect.create_technical_spec("PRIORITY 20")
except CFR011ViolationError as e:
    print(e)
    # Output:
    # CFR-011 violation detected! Cannot create spec until resolved:
    #   - Unread code-searcher reports: SECURITY_AUDIT_2025-10-18.md
    #   - Weekly codebase analysis overdue (last: 2025-10-10)
    #
    # Actions required:
    #   1. Run: architect daily-integration
    #   2. Run: architect analyze-codebase
```

---

**End of SPEC-054**
