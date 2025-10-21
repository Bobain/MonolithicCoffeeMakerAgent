# SPEC-055: Architect Daily Integration of code-searcher Findings (CFR-011)

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CFR-011, US-054
**Estimated Duration**: 1-2 days (SIMPLIFIED)

---

## Executive Summary

Implement CFR-011: architect MUST read code-searcher reports daily and analyze codebase weekly before creating new specs. This enforces continuous integration of code quality findings into architectural decisions.

**Key Principle**: architect cannot create specs in a vacuum - must integrate code-searcher insights to reduce technical debt and improve code quality continuously.

---

## Problem Statement

### Current Situation
- **code-searcher reports ignored**: Valuable analysis sits unread in docs/
- **Technical debt accumulates**: Refactoring opportunities missed
- **Duplicate work**: Same patterns implemented multiple times
- **Quality degradation**: Code quality issues not addressed proactively
- **No enforcement**: architect can create specs without considering existing code quality

### Root Cause
No systematic process for architect to:
1. Read code-searcher reports daily
2. Analyze codebase weekly (personally)
3. Integrate findings into new specs
4. Block spec creation if integration overdue

### Goal
Create lightweight enforcement ensuring architect maintains code quality through continuous integration of code-searcher findings.

### Non-Goals
- ❌ Complex project management system
- ❌ Automated code analysis (code-searcher already does this)
- ❌ Real-time monitoring (daily/weekly checks sufficient)
- ❌ Automatic refactoring (human judgment required)

---

## Proposed Solution: SIMPLIFIED APPROACH

### Core Concept
1. **Daily**: Check for new code-searcher reports → Read → Extract action items
2. **Weekly**: Analyze codebase personally → Document findings → Create refactoring specs
3. **Enforcement**: Block spec creation if integration overdue
4. **Tracking**: Simple JSON file tracks last integration dates

### Architecture (SIMPLE)
```
Architect Creates Spec
    ↓
Pre-Check: enforce_cfr_011()
    ↓
Check 1: Any unread code-searcher reports?
    - YES: BLOCK with error "Read reports first"
    - NO: Continue
    ↓
Check 2: Last analysis > 7 days ago?
    - YES: BLOCK with error "Analyze codebase first"
    - NO: Continue
    ↓
ALLOW spec creation
    ↓
Update tracking file (last_spec_created)
```

**NO complex systems, just date checks + simple enforcement!**

---

## Implementation Plan: PHASED & SIMPLE

### Phase 1: Tracking System (Day 1 - 4 hours)

**Goal**: Track architect's integration activities.

**Files to Create**:

1. **`coffee_maker/autonomous/architect_integration.py`** (~150 lines)
   - Track last code-searcher report read
   - Track last weekly codebase analysis
   - Enforce CFR-011 before spec creation

   ```python
   """Architect integration tracking for CFR-011.

   Ensures architect reads code-searcher reports daily and analyzes
   codebase weekly before creating new specs.
   """

   from pathlib import Path
   from datetime import datetime, timedelta
   import json
   from typing import Dict, Optional

   INTEGRATION_STATUS_FILE = Path("data/architect_integration_status.json")
   MAX_DAYS_BETWEEN_ANALYSIS = 7  # Weekly requirement

   class ArchitectIntegrationTracker:
       """Track architect's integration of code-searcher findings."""

       def __init__(self):
           self.status_file = INTEGRATION_STATUS_FILE
           self.status = self._load_status()

       def _load_status(self) -> Dict:
           """Load integration status from disk."""
           if not self.status_file.exists():
               return {
                   "last_code_searcher_read": None,
                   "last_weekly_analysis": None,
                   "last_spec_created": None,
                   "unread_reports": [],
                   "action_items": []
               }

           try:
               return json.loads(self.status_file.read_text())
           except Exception as e:
               print(f"Warning: Could not load status: {e}")
               return {}

       def _save_status(self):
           """Save integration status to disk."""
           self.status_file.parent.mkdir(parents=True, exist_ok=True)
           self.status_file.write_text(json.dumps(self.status, indent=2))

       def check_unread_reports(self) -> list[Path]:
           """Check for unread code-searcher reports.

           Returns:
               List of unread report paths
           """
           reports_dir = Path("docs/code-searcher")
           if not reports_dir.exists():
               return []

           # Find all analysis reports
           all_reports = sorted(reports_dir.glob("*_analysis_*.md"))

           # Filter to reports created after last read
           last_read = self.status.get("last_code_searcher_read")
           if not last_read:
               # Never read any reports
               return list(all_reports)

           last_read_date = datetime.fromisoformat(last_read)
           unread = []

           for report in all_reports:
               # Check file modification time
               report_mtime = datetime.fromtimestamp(report.stat().st_mtime)
               if report_mtime > last_read_date:
                   unread.append(report)

           return unread

       def days_since_last_analysis(self) -> int:
           """Get days since last weekly codebase analysis.

           Returns:
               Days since last analysis (999 if never analyzed)
           """
           last_analysis = self.status.get("last_weekly_analysis")
           if not last_analysis:
               return 999  # Never analyzed

           last_date = datetime.fromisoformat(last_analysis)
           delta = datetime.now() - last_date
           return delta.days

       def enforce_cfr_011(self) -> bool:
           """Enforce CFR-011: Check architect has done integration work.

           Returns:
               True if compliant

           Raises:
               CFR011ViolationError: If integration overdue
           """
           # Check 1: Unread code-searcher reports?
           unread = self.check_unread_reports()
           if unread:
               raise CFR011ViolationError(
                   f"CFR-011 VIOLATION: {len(unread)} unread code-searcher reports!\n"
                   f"\n"
                   f"Unread Reports:\n" +
                   "\n".join(f"  - {r.name}" for r in unread[:5]) +
                   (f"\n  - ... and {len(unread)-5} more" if len(unread) > 5 else "") +
                   f"\n\n"
                   f"ACTION REQUIRED:\n"
                   f"1. Read all code-searcher reports\n"
                   f"2. Extract action items (refactorings, improvements)\n"
                   f"3. Update existing specs with findings\n"
                   f"4. Create refactoring specs if needed\n"
                   f"5. Run: architect mark-reports-read\n"
                   f"\n"
                   f"Then you can create new specs.\n"
               )

           # Check 2: Weekly analysis overdue?
           days_since = self.days_since_last_analysis()
           if days_since > MAX_DAYS_BETWEEN_ANALYSIS:
               raise CFR011ViolationError(
                   f"CFR-011 VIOLATION: Weekly codebase analysis overdue!\n"
                   f"\n"
                   f"Last Analysis: {days_since} days ago\n"
                   f"Max Allowed: {MAX_DAYS_BETWEEN_ANALYSIS} days\n"
                   f"Overdue By: {days_since - MAX_DAYS_BETWEEN_ANALYSIS} days\n"
                   f"\n"
                   f"ACTION REQUIRED:\n"
                   f"1. Analyze codebase for:\n"
                   f"   - Large files (>500 lines)\n"
                   f"   - Code duplication\n"
                   f"   - Missing abstractions\n"
                   f"   - Test coverage gaps\n"
                   f"2. Document findings in analysis report\n"
                   f"3. Create refactoring specs as needed\n"
                   f"4. Run: architect mark-analysis-complete\n"
                   f"\n"
                   f"Then you can create new specs.\n"
               )

           # All checks passed
           return True

       def mark_reports_read(self, notes: str = ""):
           """Mark code-searcher reports as read.

           Args:
               notes: Optional notes about action items extracted
           """
           self.status["last_code_searcher_read"] = datetime.now().isoformat()
           self.status["unread_reports"] = []

           if notes:
               if "action_items" not in self.status:
                   self.status["action_items"] = []
               self.status["action_items"].append({
                   "date": datetime.now().isoformat(),
                   "notes": notes
               })

           self._save_status()
           print("✅ code-searcher reports marked as read")

       def mark_analysis_complete(self, findings: str = ""):
           """Mark weekly codebase analysis as complete.

           Args:
               findings: Summary of analysis findings
           """
           self.status["last_weekly_analysis"] = datetime.now().isoformat()

           if findings:
               if "analysis_history" not in self.status:
                   self.status["analysis_history"] = []
               self.status["analysis_history"].append({
                   "date": datetime.now().isoformat(),
                   "findings": findings
               })

           self._save_status()
           print("✅ Weekly analysis marked complete")

       def record_spec_created(self, spec_name: str):
           """Record that a spec was created (after CFR-011 check).

           Args:
               spec_name: Spec identifier (e.g., "SPEC-055")
           """
           self.status["last_spec_created"] = {
               "spec": spec_name,
               "date": datetime.now().isoformat()
           }
           self._save_status()

   class CFR011ViolationError(Exception):
       """Raised when architect violates CFR-011 (integration requirement)."""
       pass
   ```

**Testing**:
- Create dummy code-searcher report
- Check unread reports detected
- Mark as read, verify count zero
- Simulate 8 days since analysis
- Verify enforcement blocks spec creation

**Acceptance Criteria**:
- ✅ Tracking file created and loaded
- ✅ Unread reports detected
- ✅ Days since analysis calculated
- ✅ CFR-011 enforcement blocks when overdue
- ✅ Mark as read/complete updates status

---

### Phase 2: CLI Integration (Day 1 - 3 hours)

**Goal**: Add CLI commands for architect integration workflow.

**Files to Modify**:

1. **`coffee_maker/cli/roadmap_cli.py`** (~40 lines added)
   - Add command: `architect integration-status`
   - Add command: `architect mark-reports-read`
   - Add command: `architect mark-analysis-complete`
   - Route to ArchitectIntegrationTracker

   ```python
   # Add to roadmap_cli.py

   @chat_group.command("integration-status")
   def architect_integration_status():
       """Check architect integration status (CFR-011).

       Shows:
       - Unread code-searcher reports
       - Days since last weekly analysis
       - CFR-011 compliance status
       """
       from coffee_maker.autonomous.architect_integration import ArchitectIntegrationTracker

       tracker = ArchitectIntegrationTracker()

       console.print("\n[bold]Architect Integration Status (CFR-011)[/bold]\n")

       # Check unread reports
       unread = tracker.check_unread_reports()
       if unread:
           console.print(f"[red]⚠️ {len(unread)} Unread code-searcher Reports:[/red]")
           for report in unread[:5]:
               console.print(f"  - {report.name}")
           if len(unread) > 5:
               console.print(f"  - ... and {len(unread)-5} more")
       else:
           console.print("[green]✅ No unread code-searcher reports[/green]")

       # Check weekly analysis
       days_since = tracker.days_since_last_analysis()
       if days_since > 7:
           console.print(f"\n[red]⚠️ Weekly Analysis Overdue:[/red]")
           console.print(f"  Last analysis: {days_since} days ago")
           console.print(f"  Max allowed: 7 days")
           console.print(f"  Overdue by: {days_since - 7} days")
       else:
           console.print(f"\n[green]✅ Weekly Analysis Current:[/green]")
           console.print(f"  Last analysis: {days_since} days ago")

       # Overall status
       try:
           tracker.enforce_cfr_011()
           console.print("\n[bold green]✅ CFR-011 COMPLIANT[/bold green]")
           console.print("You may create new specs.\n")
       except Exception as e:
           console.print("\n[bold red]🚫 CFR-011 VIOLATION[/bold red]")
           console.print("Cannot create new specs until resolved.\n")

   @chat_group.command("mark-reports-read")
   @click.option("--notes", help="Action items extracted from reports")
   def mark_reports_read(notes: Optional[str]):
       """Mark code-searcher reports as read."""
       from coffee_maker.autonomous.architect_integration import ArchitectIntegrationTracker

       tracker = ArchitectIntegrationTracker()
       tracker.mark_reports_read(notes or "")
       console.print("[green]✅ Reports marked as read[/green]")

   @chat_group.command("mark-analysis-complete")
   @click.option("--findings", help="Summary of analysis findings")
   def mark_analysis_complete(findings: Optional[str]):
       """Mark weekly codebase analysis as complete."""
       from coffee_maker.autonomous.architect_integration import ArchitectIntegrationTracker

       tracker = ArchitectIntegrationTracker()
       tracker.mark_analysis_complete(findings or "")
       console.print("[green]✅ Analysis marked complete[/green]")
   ```

**Testing**:
- Run `architect integration-status` → see status
- Run `architect mark-reports-read` → reports cleared
- Run `architect mark-analysis-complete` → analysis updated
- Verify fast (<1 second)

**Acceptance Criteria**:
- ✅ CLI commands work
- ✅ Status display clear
- ✅ Mark commands update tracking
- ✅ Fast feedback

---

### Phase 3: Spec Creation Integration (Day 2 - 4 hours)

**Goal**: Integrate CFR-011 enforcement into spec creation workflow.

**Files to Modify**:

1. **`coffee_maker/autonomous/daemon_spec_manager.py`** (~15 lines)
   - Add CFR-011 check before creating specs
   - Block if integration overdue
   - Log enforcement events

   ```python
   # Add to daemon_spec_manager.py

   from coffee_maker.autonomous.architect_integration import (
       ArchitectIntegrationTracker,
       CFR011ViolationError
   )

   def create_technical_spec(self, priority: dict) -> Path:
       """Create technical specification for priority.

       Enforces CFR-011 before allowing spec creation.
       """
       # CFR-011: Enforce architect integration
       try:
           tracker = ArchitectIntegrationTracker()
           tracker.enforce_cfr_011()
       except CFR011ViolationError as e:
           self.logger.error(f"CFR-011 violation: {e}")
           raise

       # Proceed with spec creation
       spec_path = self._delegate_to_architect(priority)

       # Record spec created
       spec_name = spec_path.stem
       tracker.record_spec_created(spec_name)

       return spec_path
   ```

2. **`.claude/agents/architect.md`** (~20 lines)
   - Add "Before Creating Specs" section
   - Document CFR-011 requirements
   - Explain integration workflow

   ```markdown
   ## Before Creating Specs (CFR-011 Requirement)

   **CRITICAL**: You MUST complete integration work before creating new specs.

   ### Daily Integration (Every Day)
   1. Check for new code-searcher reports: `architect integration-status`
   2. Read all unread reports
   3. Extract action items (refactorings, improvements)
   4. Update existing specs with findings
   5. Mark as read: `architect mark-reports-read --notes "Action items"`

   ### Weekly Analysis (Every 7 Days)
   1. Analyze codebase yourself:
      - Large files (>500 lines)
      - Code duplication
      - Missing abstractions
      - Test coverage gaps
   2. Document findings in analysis report
   3. Create refactoring specs as needed
   4. Mark complete: `architect mark-analysis-complete --findings "Summary"`

   ### Spec Creation Enforcement
   - System checks CFR-011 compliance before allowing spec creation
   - If violated: Error with clear remediation steps
   - If compliant: Spec creation proceeds normally

   **Why This Matters**:
   - Prevents architectural debt accumulation
   - Ensures specs incorporate existing code quality insights
   - Maintains continuous improvement loop
   - Enforces proactive quality management
   ```

**Testing**:
- Try creating spec without integration → verify blocked
- Complete integration work → verify spec creation allowed
- Check logs → verify enforcement events recorded

**Acceptance Criteria**:
- ✅ Spec creation blocked if CFR-011 violated
- ✅ Clear error messages with remediation
- ✅ Spec creation proceeds if compliant
- ✅ All events logged

---

## Component Design

### ArchitectIntegrationTracker

**Responsibility**: Track and enforce architect's integration of code-searcher findings.

**Interface**:
```python
class ArchitectIntegrationTracker:
    """Track architect's integration activities (CFR-011)."""

    def check_unread_reports(self) -> list[Path]:
        """Find unread code-searcher reports."""
        pass

    def days_since_last_analysis(self) -> int:
        """Days since last weekly codebase analysis."""
        pass

    def enforce_cfr_011(self) -> bool:
        """Enforce CFR-011 requirements.

        Raises:
            CFR011ViolationError: If integration overdue
        """
        pass

    def mark_reports_read(self, notes: str = ""):
        """Mark reports as read."""
        pass

    def mark_analysis_complete(self, findings: str = ""):
        """Mark weekly analysis complete."""
        pass

    def record_spec_created(self, spec_name: str):
        """Record spec creation."""
        pass
```

---

## Data Structures

### Integration Status File
```json
{
  "last_code_searcher_read": "2025-10-17T08:00:00",
  "last_weekly_analysis": "2025-10-15T10:00:00",
  "last_spec_created": {
    "spec": "SPEC-055",
    "date": "2025-10-17T09:00:00"
  },
  "unread_reports": [],
  "action_items": [
    {
      "date": "2025-10-17T08:00:00",
      "notes": "Refactor large files identified in security_audit_2025-10-15.md"
    }
  ],
  "analysis_history": [
    {
      "date": "2025-10-15T10:00:00",
      "findings": "Found 5 large files >500 lines, 3 code duplication patterns"
    }
  ]
}
```

---

## Testing Strategy

### Unit Tests (~2 hours)

**`tests/unit/test_architect_integration.py`**:
```python
def test_check_unread_reports():
    """Test unread report detection."""
    tracker = ArchitectIntegrationTracker()
    # Create dummy report
    Path("docs/code-searcher/test_report.md").write_text("test")
    unread = tracker.check_unread_reports()
    assert len(unread) > 0

def test_days_since_analysis():
    """Test days calculation."""
    tracker = ArchitectIntegrationTracker()
    tracker.status["last_weekly_analysis"] = "2025-10-10T00:00:00"
    days = tracker.days_since_last_analysis()
    assert days >= 0

def test_enforce_cfr_011_violation():
    """Test CFR-011 enforcement blocks when overdue."""
    tracker = ArchitectIntegrationTracker()
    # Simulate 8 days since analysis
    old_date = (datetime.now() - timedelta(days=8)).isoformat()
    tracker.status["last_weekly_analysis"] = old_date

    with pytest.raises(CFR011ViolationError):
        tracker.enforce_cfr_011()

def test_mark_reports_read():
    """Test marking reports as read."""
    tracker = ArchitectIntegrationTracker()
    tracker.mark_reports_read("Test notes")
    assert tracker.status["last_code_searcher_read"] is not None
```

### Integration Tests (~1 hour)

**Manual Testing**:
1. Create code-searcher report
2. Run `architect integration-status` → verify unread shown
3. Try creating spec → verify blocked
4. Run `architect mark-reports-read`
5. Run `architect mark-analysis-complete`
6. Try creating spec → verify allowed

---

## Rollout Plan

### Day 1 (7 hours)
- Create ArchitectIntegrationTracker class (4 hours)
- Add CLI commands (3 hours)
- Test tracking system

### Day 2 (4 hours)
- Integrate with daemon_spec_manager (2 hours)
- Update architect.md documentation (1 hour)
- Write tests (1 hour)
- Manual end-to-end testing

**Total: 1-2 days (11 hours)**

---

## Success Criteria

### Must Have (P0)
- ✅ Tracking system implemented
- ✅ CFR-011 enforcement blocks spec creation when overdue
- ✅ CLI commands for integration workflow
- ✅ Integration with daemon spec creation
- ✅ Clear error messages with remediation

### Should Have (P1)
- ✅ Unit tests for tracker
- ✅ Documentation in architect.md
- ✅ Integration history tracked

### Could Have (P2) - DEFERRED
- ⚪ Automated analysis suggestions
- ⚪ Integration metrics dashboard
- ⚪ Notification system for overdue integration

---

## Why This is SIMPLE

### What We REUSE
✅ **Existing JSON tracking**: Simple file-based storage
✅ **Existing CLI**: Just add commands
✅ **Existing daemon workflow**: Minimal integration
✅ **code-searcher reports**: Already being generated

**New code**: ~200 lines total (ArchitectIntegrationTracker + CLI + integration)

---

## Risks & Mitigations

### Risk 1: architect forgets to do integration

**Impact**: High
**Mitigation**:
- System blocks spec creation (forced compliance)
- Clear error messages explain what to do
- CLI commands make workflow easy

### Risk 2: Weekly analysis takes too long

**Impact**: Medium
**Mitigation**:
- Set realistic time limits (1-2 hours max)
- Focus on high-impact findings only
- Can be done incrementally during the week

### Risk 3: False positives (reports already read manually)

**Impact**: Low
**Mitigation**:
- `mark-reports-read` command available
- Manual override possible
- Tracking file can be edited if needed

---

## Future Enhancements (NOT NOW)

Phase 2+ (if needed):
1. Automated analysis scheduling
2. Integration metrics dashboard
3. Notification system for overdue work
4. AI-powered finding prioritization

**But**: Start simple with manual workflow!

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending
- [ ] User (final approval) - Approval pending

---

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements (1-2 days)

**Remember**: CFR-011 ensures architect maintains code quality through continuous integration of code-searcher findings. This is a critical feedback loop that prevents architectural debt accumulation!
