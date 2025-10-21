# SPEC-056: Claude Skills Integration - Phase 2 (Medium-Value Skills)

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-056 (PRIORITY 18), SPEC-001 (General Claude Skills Integration), SPEC-055 (Phase 1)

**Related ADRs**: ADR-002-integrate-claude-skills.md

**Assigned To**: code_developer

---

## Executive Summary

This specification defines Phase 2 of Claude Skills integration: implementing **6 medium-value skills** for strategic workflows across project_manager, architect, assistant, and code-searcher agents. Phase 2 expands automation coverage to ROADMAP health monitoring, architecture analysis, demo creation, bug analysis, and security audits.

**Key Deliverables**:
1. **project_manager Skill**: ROADMAP Health Monitoring
2. **architect Skills** (2): Architecture Analysis, Dependency Impact Analysis
3. **assistant Skills** (2): Demo Creation, Bug Analysis
4. **code-searcher Skill**: Security Audit

**Expected Impact**: Comprehensive automation coverage across all major workflows, 30-75% time savings per workflow.

**Dependencies**: SPEC-055 (Phase 1) must be complete.

---

## Problem Statement

### Current Situation

Phase 1 (SPEC-055) implemented:
- ✅ Core skills infrastructure (ExecutionController, SkillLoader, SkillRegistry, SkillInvoker)
- ✅ code_developer skills (TDD, Refactoring, PR Creation)
- ✅ architect skill (Spec Generator)
- ✅ project_manager skill (DoD Verification)

**Remaining manual workflows**:
- ❌ ROADMAP health monitoring (manual analysis of blockers, priorities)
- ❌ Architecture analysis (manual codebase review, dependency mapping)
- ❌ Demo creation (manual Puppeteer scripting, screenshot capture)
- ❌ Bug analysis (manual reproduction, root cause investigation)
- ❌ Security audits (manual vulnerability scanning)
- ❌ Dependency impact analysis (manual change assessment)

**Time Cost of Manual Workflows**:
- ROADMAP health report: 30-45 minutes
- Architecture analysis: 2-3 hours
- Demo creation: 45 minutes per demo
- Bug analysis: 1-2 hours per bug
- Security audit: 3 hours
- Dependency impact: 45 minutes per dependency

**Total Manual Time (Monthly)**: ~15-20 hours

### Goal

Implement 6 Phase 2 skills that:
1. **Automate strategic workflows**: ROADMAP monitoring, architecture reviews
2. **Enhance quality**: Automated demos, comprehensive bug analysis
3. **Improve security**: Regular security audits, dependency risk assessment
4. **Integrate with Phase 1**: Use existing infrastructure seamlessly
5. **Maintain performance**: Skills execute in <10 minutes (90% of cases)

### Non-Goals

**Phase 2 does NOT include**:
- ❌ Code Forensics (Phase 3)
- ❌ Design System Generation (Phase 3)
- ❌ Visual Regression Testing (Phase 3)
- ❌ Performance tuning (Phase 3)
- ❌ Skill marketplace submission (Phase 3)

---

## Requirements

### Functional Requirements

1. **FR-1**: Implement ROADMAP Health Skill (project_manager)
2. **FR-2**: Implement Architecture Analysis Skill (architect)
3. **FR-3**: Implement Dependency Impact Skill (architect)
4. **FR-4**: Implement Demo Creation Skill (assistant)
5. **FR-5**: Implement Bug Analysis Skill (assistant)
6. **FR-6**: Implement Security Audit Skill (code-searcher)
7. **FR-7**: Integrate with Phase 1 infrastructure (ExecutionController, etc.)
8. **FR-8**: Add Langfuse tracking for skill executions
9. **FR-9**: Generate synthetic reports (1-2 pages, not 20+ pages)
10. **FR-10**: All skills must support composition (chainable)

### Non-Functional Requirements

1. **NFR-1**: Performance: 90% of skills execute in <10 minutes
2. **NFR-2**: Reliability: >95% success rate for skill execution
3. **NFR-3**: Context Budget: Skills fit within CFR-007 (≤30% agent context)
4. **NFR-4**: Observability: Langfuse tracking for all executions
5. **NFR-5**: Quality: Synthetic reports are actionable (not verbose)
6. **NFR-6**: Security: Security Audit skill detects >90% of OWASP Top 10
7. **NFR-7**: Testability: >80% code coverage for all skills

### Constraints

- **MUST** build on Phase 1 infrastructure (no reinventing)
- **MUST** integrate Langfuse tracking (Phase 2 requirement)
- **MUST** generate synthetic reports (1-2 pages maximum)
- **MUST** work on `roadmap` branch only (CFR-013)
- **Timeline**: 3 weeks (76-96 hours)

---

## Proposed Solution

### High-Level Approach

Expand skills coverage to strategic workflows:
1. **ROADMAP Health**: Automated health monitoring (blockers, GitHub status)
2. **Architecture Analysis**: Codebase review, dependency graph, improvement suggestions
3. **Dependency Impact**: Analyze dependency changes, identify risks
4. **Demo Creation**: Puppeteer automation with screenshots and narration
5. **Bug Analysis**: Reproduce bugs, capture logs, root cause analysis
6. **Security Audit**: Comprehensive vulnerability scanning (OWASP Top 10)

**Key Design Principles**:
- **Build on Phase 1**: Reuse ExecutionController, SkillLoader, etc.
- **Synthetic reports**: 1-2 pages maximum (actionable, not verbose)
- **Langfuse integration**: Track all skill executions for observability
- **Composable**: Skills can chain together for complex workflows

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT EXECUTION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │project_mgr   │  │  architect   │  │  assistant   │  ...      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                    │
│         └─────────────────┴──────────────────┘                   │
│                           ▼                                       │
│                ┌─────────────────────┐                          │
│                │ ExecutionController │ ◄── (Phase 1 - Unchanged)│
│                └─────────┬───────────┘                          │
│                          │                                       │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │SkillInvoker │  │  Langfuse   │  │  Puppeteer  │  (Phase 2) │
│  │  (Phase 1)  │  │  Tracker    │  │    MCP      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  .claude/skills/                                                 │
│  ├── project-manager/                                            │
│  │   └── roadmap-health/       ◄── NEW (Phase 2)               │
│  ├── architect/                                                  │
│  │   ├── architecture-analysis/ ◄── NEW (Phase 2)              │
│  │   └── dependency-impact/     ◄── NEW (Phase 2)              │
│  ├── assistant/                                                  │
│  │   ├── demo-creator/          ◄── NEW (Phase 2)              │
│  │   └── bug-analyzer/          ◄── NEW (Phase 2)              │
│  └── code-searcher/                                              │
│      └── security-audit/        ◄── NEW (Phase 2)               │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Phase 1 Infrastructure**: ExecutionController, SkillLoader, SkillRegistry, SkillInvoker (unchanged)
- **Langfuse**: Skill execution tracking and observability (NEW)
- **Puppeteer MCP**: Browser automation for demos (NEW)
- **GitHub CLI (gh)**: ROADMAP health monitoring (existing)
- **radon**: Code complexity metrics (existing)
- **bandit**: Security vulnerability scanning (NEW - pre-approved)
- **safety**: Dependency vulnerability scanning (NEW - pre-approved)

---

## Detailed Design

### Phase 2 Skills Specifications

### Skill 1: ROADMAP Health (project_manager)

**Location**: `.claude/skills/project-manager/roadmap-health/`

**Purpose**: Automated ROADMAP health monitoring with GitHub integration

**SKILL.md**:
```yaml
---
name: roadmap-health
version: 1.0.0
agent: project-manager
scope: agent-specific
description: >
  Automated ROADMAP health monitoring: analyze priorities, check GitHub
  status, identify blockers, generate synthetic health report.

triggers:
  - "check roadmap health"
  - "analyze roadmap status"
  - "identify blockers"
  - "roadmap health report"

requires:
  - gh>=2.0  # GitHub CLI

inputs:
  generate_report:
    type: bool
    required: false
    description: Generate health report file? (default: true)

outputs:
  health_status:
    type: string
    description: Overall health (HEALTHY, WARNING, CRITICAL)

  blockers:
    type: list[dict]
    description: List of blockers (priority, blocker, severity)

  github_status:
    type: dict
    description: GitHub status (open PRs, CI failures, etc.)

  report_path:
    type: string
    description: Path to generated health report

author: architect agent
created: 2025-10-19
---

# ROADMAP Health Skill

Automated ROADMAP health monitoring for project_manager.

## Workflow

1. **Parse ROADMAP**: Extract all priorities, statuses
2. **Check GitHub**: Query PRs, issues, CI/CD status
3. **Identify Blockers**: Detect stuck priorities, failed CI
4. **Analyze Trends**: Compare vs last week
5. **Generate Report**: Synthetic 1-2 page report
6. **Send Notification**: Alert user if critical blockers

## Expected Time Savings

- **Manual Health Check**: 30-45 minutes
- **With Skill**: 5 minutes
- **Time Saved**: 85% reduction
```

**roadmap-health.py**:
```python
"""
ROADMAP Health Skill for project_manager.
Automated health monitoring: parse → github → blockers → report.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ROADMAP health monitoring."""
    generate_report = context.get("generate_report", True)

    print("Analyzing ROADMAP health...")

    # Step 1: Parse ROADMAP
    priorities = parse_roadmap()

    # Step 2: Check GitHub status
    github_status = check_github_status()

    # Step 3: Identify blockers
    blockers = identify_blockers(priorities, github_status)

    # Step 4: Analyze trends
    trends = analyze_trends(priorities)

    # Step 5: Determine overall health
    health = determine_health(blockers, github_status)

    # Step 6: Generate report
    report_path = None
    if generate_report:
        report_path = generate_health_report(
            health, priorities, blockers, github_status, trends
        )

    # Step 7: Send notification if critical
    if health == "CRITICAL":
        send_notification(blockers)

    return {
        "health_status": health,
        "blockers": blockers,
        "github_status": github_status,
        "report_path": str(report_path) if report_path else None
    }


def parse_roadmap() -> List[Dict[str, Any]]:
    """Parse ROADMAP.md and extract priorities."""
    roadmap = Path("docs/roadmap/ROADMAP.md").read_text()

    priorities = []
    # Parse priorities with regex or markdown parser
    # Extract: priority number, status, estimated effort, dependencies
    # Return structured list

    return priorities


def check_github_status() -> Dict[str, Any]:
    """Check GitHub status using gh CLI."""
    # gh pr list --state open
    open_prs = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--json", "number,title,state"],
        capture_output=True,
        text=True
    )

    # gh run list --limit 10
    ci_runs = subprocess.run(
        ["gh", "run", "list", "--limit", "10", "--json", "status,conclusion"],
        capture_output=True,
        text=True
    )

    # Parse JSON output
    prs = json.loads(open_prs.stdout) if open_prs.stdout else []
    runs = json.loads(ci_runs.stdout) if ci_runs.stdout else []

    return {
        "open_prs": len(prs),
        "failed_ci": sum(1 for r in runs if r.get("conclusion") == "failure"),
        "prs": prs,
        "runs": runs
    }


def identify_blockers(
    priorities: List[Dict[str, Any]],
    github_status: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Identify blockers (stuck priorities, failed CI, etc.)."""
    blockers = []

    # Check for stuck priorities (In Progress >7 days)
    # Check for failed CI blocking PRs
    # Check for missing dependencies
    # Classify by severity (CRITICAL, HIGH, MEDIUM, LOW)

    return blockers


def analyze_trends(priorities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze trends (compare vs last week)."""
    # Compare completion rate vs last week
    # Identify velocity changes
    # Detect patterns (consistently blocked agent, etc.)

    return {
        "completion_rate_change": 0.0,
        "velocity_trend": "stable",
        "patterns": []
    }


def determine_health(
    blockers: List[Dict[str, Any]],
    github_status: Dict[str, Any]
) -> str:
    """Determine overall health status."""
    critical_blockers = [b for b in blockers if b["severity"] == "CRITICAL"]
    failed_ci = github_status.get("failed_ci", 0)

    if critical_blockers or failed_ci > 3:
        return "CRITICAL"
    elif len(blockers) > 5 or failed_ci > 0:
        return "WARNING"
    else:
        return "HEALTHY"


def generate_health_report(
    health: str,
    priorities: List[Dict[str, Any]],
    blockers: List[Dict[str, Any]],
    github_status: Dict[str, Any],
    trends: Dict[str, Any]
) -> Path:
    """Generate synthetic health report (1-2 pages max)."""
    report = f"""# ROADMAP Health Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Health Status**: {health} {'🔴' if health == 'CRITICAL' else '🟡' if health == 'WARNING' else '🟢'}

## Summary

- **Total Priorities**: {len(priorities)}
- **In Progress**: {sum(1 for p in priorities if p['status'] == 'In Progress')}
- **Blocked**: {len(blockers)}
- **Open PRs**: {github_status['open_prs']}
- **Failed CI**: {github_status['failed_ci']}

## Top 3 Blockers

"""

    # Show top 3 most critical blockers
    for i, blocker in enumerate(blockers[:3], 1):
        report += f"""### {i}. {blocker['priority']} ({blocker['severity']})
**Blocker**: {blocker['blocker']}
**Action**: {blocker['action']}

"""

    report += f"""## Trends

- **Completion Rate**: {trends['completion_rate_change']:+.1f}% vs last week
- **Velocity**: {trends['velocity_trend']}

## Recommended Actions

"""

    # Generate 3-5 actionable recommendations
    # Based on blockers and trends

    # Save report
    report_path = Path("evidence/roadmap-health-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return report_path


def send_notification(blockers: List[Dict[str, Any]]):
    """Send notification if critical blockers."""
    # Use notification system to alert user
    pass


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 85% reduction (30-45 minutes → 5 minutes)

---

### Skill 2: Architecture Analysis (architect)

**Location**: `.claude/skills/architect/architecture-analysis/`

**Purpose**: Automated codebase architecture analysis

**SKILL.md**:
```yaml
---
name: architecture-analysis
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Automated architecture analysis: scan codebase, build dependency graph,
  identify patterns, suggest improvements, generate synthetic report.

triggers:
  - "analyze architecture"
  - "review codebase structure"
  - "architecture health check"

requires:
  - radon>=6.0  # Code complexity metrics
  - graphviz>=0.20  # Dependency graphs

inputs:
  scope:
    type: string
    required: false
    description: Scope to analyze (default: entire codebase)

outputs:
  complexity_score:
    type: float
    description: Average cyclomatic complexity

  dependency_graph:
    type: string
    description: Path to dependency graph (PNG)

  recommendations:
    type: list[string]
    description: List of improvement recommendations

  report_path:
    type: string
    description: Path to analysis report

author: architect agent
created: 2025-10-19
---

# Architecture Analysis Skill

Automated architecture analysis for architect.

## Workflow

1. **Scan Codebase**: Analyze all Python files
2. **Measure Complexity**: Calculate cyclomatic complexity
3. **Build Dependency Graph**: Visualize module dependencies
4. **Identify Patterns**: Detect anti-patterns, code smells
5. **Generate Recommendations**: Suggest refactorings, improvements
6. **Create Report**: Synthetic 1-2 page report

## Expected Time Savings

- **Manual Architecture Review**: 2-3 hours
- **With Skill**: 15-20 minutes
- **Time Saved**: 85% reduction
```

**architecture-analysis.py**:
```python
"""
Architecture Analysis Skill for architect.
Automated analysis: scan → complexity → graph → patterns → report.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute architecture analysis."""
    scope = context.get("scope", "coffee_maker/")

    print(f"Analyzing architecture: {scope}")

    # Step 1: Scan codebase
    files = scan_codebase(scope)

    # Step 2: Measure complexity
    complexity = measure_complexity(files)

    # Step 3: Build dependency graph
    graph_path = build_dependency_graph(files)

    # Step 4: Identify patterns
    patterns = identify_patterns(files)

    # Step 5: Generate recommendations
    recommendations = generate_recommendations(complexity, patterns)

    # Step 6: Create report
    report_path = create_analysis_report(
        complexity, graph_path, patterns, recommendations
    )

    return {
        "complexity_score": complexity["average"],
        "dependency_graph": str(graph_path),
        "recommendations": recommendations,
        "report_path": str(report_path)
    }


def scan_codebase(scope: str) -> List[Path]:
    """Scan codebase and return Python files."""
    # Find all *.py files in scope
    # Exclude tests, __pycache__, etc.
    pass


def measure_complexity(files: List[Path]) -> Dict[str, Any]:
    """Measure cyclomatic complexity using radon."""
    # radon cc --average
    # Calculate: average, min, max, distribution
    pass


def build_dependency_graph(files: List[Path]) -> Path:
    """Build dependency graph visualization."""
    # Parse imports from each file
    # Build graph using graphviz
    # Save as PNG
    pass


def identify_patterns(files: List[Path]) -> List[Dict[str, Any]]:
    """Identify patterns (good and bad)."""
    # Detect: god classes, long methods, duplicated code
    # Detect: mixins, singletons, dependency injection (good)
    # Return list of patterns with locations
    pass


def generate_recommendations(
    complexity: Dict[str, Any],
    patterns: List[Dict[str, Any]]
) -> List[str]:
    """Generate improvement recommendations."""
    recommendations = []

    # High complexity? → Recommend refactoring
    # God classes? → Recommend splitting
    # Duplicated code? → Recommend extraction

    return recommendations


def create_analysis_report(
    complexity: Dict[str, Any],
    graph_path: Path,
    patterns: List[Dict[str, Any]],
    recommendations: List[str]
) -> Path:
    """Create synthetic architecture analysis report."""
    report = f"""# Architecture Analysis Report

**Date**: {datetime.now().strftime("%Y-%m-%d")}

## Complexity Metrics

- **Average Complexity**: {complexity['average']:.2f}
- **Max Complexity**: {complexity['max']:.2f} ({complexity['max_file']})
- **Files Analyzed**: {complexity['file_count']}

## Dependency Graph

![Dependency Graph]({graph_path})

## Patterns Detected

### Good Patterns ✅
{format_patterns([p for p in patterns if p['type'] == 'good'])}

### Anti-Patterns ⚠️
{format_patterns([p for p in patterns if p['type'] == 'bad'])}

## Top 3 Recommendations

{format_recommendations(recommendations[:3])}

"""

    # Save report
    report_path = Path("evidence/architecture-analysis-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return report_path


def format_patterns(patterns: List[Dict[str, Any]]) -> str:
    """Format patterns for report."""
    # Format as markdown list
    pass


def format_recommendations(recommendations: List[str]) -> str:
    """Format recommendations for report."""
    # Format as numbered list with actionable items
    pass


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 85% reduction (2-3 hours → 15-20 minutes)

---

### Skill 3: Dependency Impact (architect)

**Location**: `.claude/skills/architect/dependency-impact/`

**Purpose**: Analyze dependency change impact

**SKILL.md**:
```yaml
---
name: dependency-impact
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Automated dependency impact analysis: analyze dependency changes,
  identify breaking changes, assess migration risk, suggest rollout plan.

triggers:
  - "analyze dependency impact"
  - "assess dependency change"
  - "dependency migration risk"

requires:
  - safety>=2.0  # Dependency vulnerability scanner

inputs:
  package_name:
    type: string
    required: true
    description: Package to analyze

  current_version:
    type: string
    required: true
    description: Current version

  target_version:
    type: string
    required: true
    description: Target version to upgrade to

outputs:
  breaking_changes:
    type: list[string]
    description: List of breaking changes

  migration_risk:
    type: string
    description: Risk level (LOW, MEDIUM, HIGH, CRITICAL)

  rollout_plan:
    type: list[string]
    description: Suggested rollout steps

  report_path:
    type: string
    description: Path to impact analysis report

author: architect agent
created: 2025-10-19
---

# Dependency Impact Skill

Automated dependency impact analysis for architect.

## Workflow

1. **Fetch Changelog**: Get changelog between versions
2. **Identify Breaking Changes**: Parse for breaking changes
3. **Scan Codebase**: Find usages of changed APIs
4. **Assess Risk**: Determine migration risk level
5. **Generate Rollout Plan**: Suggest migration steps
6. **Create Report**: Synthetic 1-2 page report

## Expected Time Savings

- **Manual Impact Analysis**: 45 minutes
- **With Skill**: 5-10 minutes
- **Time Saved**: 80% reduction
```

**dependency-impact.py** (implementation similar to above patterns)

**Expected Time Savings**: 80% reduction (45 minutes → 5-10 minutes)

---

### Skill 4: Demo Creator (assistant)

**Location**: `.claude/skills/assistant/demo-creator/`

**Purpose**: Automated Puppeteer demo creation

**SKILL.md**:
```yaml
---
name: demo-creator
version: 1.0.0
agent: assistant
scope: agent-specific
description: >
  Automated demo creation: use Puppeteer MCP to interact with app,
  capture screenshots, generate narration, create visual demo.

triggers:
  - "create demo"
  - "show how feature works"
  - "visual demonstration"
  - "generate demo video"

requires:
  - puppeteer (MCP)

inputs:
  feature_name:
    type: string
    required: true
    description: Feature to demonstrate

  url:
    type: string
    required: false
    description: App URL (default: http://localhost:8000)

  steps:
    type: list[string]
    required: false
    description: Demo steps (auto-generated if not provided)

outputs:
  screenshots:
    type: list[string]
    description: List of screenshot paths

  narration:
    type: string
    description: Demo narration text

  demo_path:
    type: string
    description: Path to demo markdown file

author: architect agent
created: 2025-10-19
---

# Demo Creator Skill

Automated demo creation for assistant.

## Workflow

1. **Plan Demo**: Define interaction steps
2. **Launch Browser**: Start Puppeteer session
3. **Execute Steps**: Interact with app, capture screenshots
4. **Generate Narration**: Create demo narration text
5. **Compile Demo**: Create markdown with screenshots + narration
6. **Save Demo**: Write to docs/demos/

## Expected Time Savings

- **Manual Demo Creation**: 45 minutes
- **With Skill**: 10 minutes
- **Time Saved**: 78% reduction
```

**demo-creator.py** (uses Puppeteer MCP for browser automation)

**Expected Time Savings**: 78% reduction (45 minutes → 10 minutes)

---

### Skill 5: Bug Analyzer (assistant)

**Location**: `.claude/skills/assistant/bug-analyzer/`

**Purpose**: Automated bug analysis and reporting

**SKILL.md**:
```yaml
---
name: bug-analyzer
version: 1.0.0
agent: assistant
scope: agent-specific
description: >
  Automated bug analysis: reproduce bug, capture logs/screenshots,
  analyze root cause, generate comprehensive bug report.

triggers:
  - "analyze bug"
  - "reproduce bug"
  - "bug root cause analysis"
  - "comprehensive bug report"

requires:
  - puppeteer (MCP)

inputs:
  bug_description:
    type: string
    required: true
    description: Bug description

  reproduction_steps:
    type: list[string]
    required: false
    description: Steps to reproduce (auto-generated if not provided)

outputs:
  reproduced:
    type: bool
    description: Bug successfully reproduced?

  root_cause:
    type: string
    description: Root cause analysis

  logs:
    type: list[string]
    description: Captured log files

  screenshots:
    type: list[string]
    description: Bug screenshots

  report_path:
    type: string
    description: Path to bug report

author: architect agent
created: 2025-10-19
---

# Bug Analyzer Skill

Automated bug analysis for assistant.

## Workflow

1. **Reproduce Bug**: Execute reproduction steps
2. **Capture Evidence**: Logs, screenshots, stack traces
3. **Analyze Root Cause**: Identify failing code path
4. **Generate Report**: Comprehensive bug report with:
   - Root cause analysis
   - Requirements for fix
   - Expected behavior once corrected
   - Complete reproduction steps
   - Environment details
   - Impact assessment

## Expected Time Savings

- **Manual Bug Analysis**: 1-2 hours
- **With Skill**: 15-20 minutes
- **Time Saved**: 75-85% reduction
```

**bug-analyzer.py** (comprehensive bug analysis with evidence capture)

**Expected Time Savings**: 75-85% reduction (1-2 hours → 15-20 minutes)

---

### Skill 6: Security Audit (code-searcher)

**Location**: `.claude/skills/code-searcher/security-audit/`

**Purpose**: Comprehensive security vulnerability scanning

**SKILL.md**:
```yaml
---
name: security-audit
version: 1.0.0
agent: code-searcher
scope: agent-specific
description: >
  Comprehensive security audit: scan for OWASP Top 10 vulnerabilities,
  check dependencies, analyze authentication flows, generate report.

triggers:
  - "security audit"
  - "scan for vulnerabilities"
  - "check security"
  - "OWASP audit"

requires:
  - bandit>=1.7  # Python security scanner
  - safety>=2.0  # Dependency vulnerability scanner

inputs:
  scope:
    type: string
    required: false
    description: Scope to audit (default: entire codebase)

outputs:
  vulnerabilities:
    type: list[dict]
    description: List of vulnerabilities found

  security_score:
    type: float
    description: Security score (0-100)

  report_path:
    type: string
    description: Path to security audit report

author: architect agent
created: 2025-10-19
---

# Security Audit Skill

Comprehensive security audit for code-searcher.

## Workflow

1. **Scan Code**: Use bandit to scan for vulnerabilities
2. **Check Dependencies**: Use safety to scan dependencies
3. **Analyze Auth Flows**: Review authentication/authorization
4. **Classify Vulnerabilities**: Map to OWASP Top 10
5. **Generate Score**: Calculate security score
6. **Create Report**: Synthetic security audit report

## Expected Time Savings

- **Manual Security Audit**: 3 hours
- **With Skill**: 30 minutes
- **Time Saved**: 83% reduction
```

**security-audit.py** (uses bandit + safety for comprehensive scanning)

**Expected Time Savings**: 83% reduction (3 hours → 30 minutes)

---

## Langfuse Integration

### Tracking Implementation

**File**: `coffee_maker/langfuse_observe/skill_tracking.py`

```python
"""Langfuse tracking for Claude Skills."""

from langfuse.decorators import observe


@observe(name="skill_execution")
def track_skill_execution(
    agent_type: str,
    skill_name: str,
    duration: float,
    success: bool,
    errors: list[str],
    context_size: int
):
    """Track skill execution in Langfuse."""
    from langfuse import Langfuse

    langfuse = Langfuse()
    langfuse.track(
        name="skill_execution",
        properties={
            "agent_type": agent_type,
            "skill_name": skill_name,
            "duration_seconds": duration,
            "success": success,
            "error_count": len(errors),
            "errors": errors,
            "context_size_bytes": context_size
        }
    )
```

---

## Testing Strategy

### Unit Tests

**Test files**: `tests/unit/test_phase2_skills.py`

**Test cases**:
1. `test_roadmap_health_skill()` - ROADMAP health monitoring
2. `test_architecture_analysis_skill()` - Architecture analysis
3. `test_dependency_impact_skill()` - Dependency impact analysis
4. `test_demo_creator_skill()` - Demo creation
5. `test_bug_analyzer_skill()` - Bug analysis
6. `test_security_audit_skill()` - Security scanning

### Integration Tests

**Test files**: `tests/integration/test_phase2_integration.py`

**Test cases**:
1. `test_roadmap_health_end_to_end()` - Full workflow
2. `test_architecture_analysis_end_to_end()` - Full workflow
3. `test_langfuse_tracking()` - Verify tracking works
4. `test_synthetic_reports()` - Reports are 1-2 pages max

---

## Rollout Plan

### Week 1: Strategic Skills (project_manager + architect)

**Goal**: Implement ROADMAP Health and Architecture Analysis skills

**Timeline**: 5 days (28-36 hours)

**Tasks**:
1. Implement ROADMAP Health skill (12 hours)
2. Implement Architecture Analysis skill (12 hours)
3. Implement Dependency Impact skill (8 hours)
4. Integration tests (4 hours)
5. Langfuse tracking integration (4 hours)

**Success Criteria**:
- ROADMAP Health generates reports in 5 minutes
- Architecture Analysis completes in 15-20 minutes
- Dependency Impact completes in 5-10 minutes

---

### Week 2: Quality Skills (assistant)

**Goal**: Implement Demo Creator and Bug Analyzer skills

**Timeline**: 5 days (24-32 hours)

**Tasks**:
1. Implement Demo Creator skill (12 hours)
2. Implement Bug Analyzer skill (12 hours)
3. Integration tests (4 hours)
4. Puppeteer MCP integration testing (4 hours)

**Success Criteria**:
- Demo Creator creates demos in 10 minutes
- Bug Analyzer analyzes bugs in 15-20 minutes
- Both skills integrate with Puppeteer MCP

---

### Week 3: Security Skills (code-searcher) + Documentation

**Goal**: Implement Security Audit skill and complete documentation

**Timeline**: 5 days (24-28 hours)

**Tasks**:
1. Add bandit + safety dependencies (via architect) (2 hours)
2. Implement Security Audit skill (12 hours)
3. Integration tests (4 hours)
4. Documentation updates (8 hours)
5. Performance benchmarks (4 hours)

**Success Criteria**:
- Security Audit completes in 30 minutes
- Detects >90% of OWASP Top 10 vulnerabilities
- All 6 Phase 2 skills operational
- Documentation updated

---

## Risks & Mitigations

### Risk 1: Puppeteer MCP Instability

**Description**: Puppeteer MCP may fail or be unavailable

**Likelihood**: Medium

**Impact**: High (demos and bug analysis blocked)

**Mitigation**:
- Fallback to manual demo creation
- Test Puppeteer MCP thoroughly before deployment
- Monitor Puppeteer MCP uptime
- Document manual fallback procedures

---

### Risk 2: Verbose Reports

**Description**: Skills may generate 20+ page reports (not synthetic)

**Likelihood**: Medium

**Impact**: Medium (defeats purpose of automation)

**Mitigation**:
- Enforce 1-2 page maximum in skill templates
- Review report quality during testing
- Use truncation and summarization
- Focus on actionable insights only

---

### Risk 3: Langfuse Integration Complexity

**Description**: Langfuse tracking may add significant overhead

**Likelihood**: Low

**Impact**: Medium (performance regression)

**Mitigation**:
- Async tracking (non-blocking)
- Minimal tracking data (only essentials)
- Performance benchmarks before/after
- Disable tracking in dev if needed

---

## Success Metrics

**Phase 2** (Month 1):
- ✅ All 6 skills operational
- ✅ Skills execute in <10 minutes (90% of cases)
- ✅ Langfuse tracking integrated
- ✅ Synthetic reports are 1-2 pages maximum
- ✅ >95% success rate

---

## References

- [SPEC-055: Phase 1 (Foundation)](SPEC-055-claude-skills-phase-1-foundation.md)
- [SPEC-001: General Claude Skills Integration](SPEC-001-claude-skills-integration.md)
- [US-056: Phase 2 Requirements](docs/roadmap/ROADMAP.md#us-056)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created Phase 2 spec | architect |
| 2025-10-19 | Status: Draft | architect |

---

## Approval

- [ ] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (strategic alignment)
- [ ] User (final approval)

**Approval Date**: TBD

---

**Status**: Ready for review by project_manager and user approval
