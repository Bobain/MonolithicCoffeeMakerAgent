---
command: project_manager.create_roadmap_report
agent: project_manager
action: create_roadmap_report
data_domain: reporting
write_tables: [system_audit]
read_tables: [roadmap_priority, specs_specification, review_code_review]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.create_roadmap_report

## Purpose

Generate comprehensive roadmap status report in multiple formats (markdown, JSON, HTML). Includes metrics, progress visualizations, and status summaries.

## Input Parameters

```yaml
report_type: string      # Optional - "summary", "detailed", "executive" (default: "summary")
output_format: string    # Optional - "markdown", "json", "html" (default: "markdown")
include_charts: boolean  # Optional - Include visualization data (default: true)
include_metrics: boolean # Optional - Include detailed metrics (default: true)
output_file: string      # Optional - Write to file (default: auto-generate)
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status, estimated_hours, priority_number,
       created_at, started_at, completed_at
FROM roadmap_priority
ORDER BY priority_number;

SELECT id, priority_id, status
FROM specs_specification;

SELECT id, priority_id, status, passed
FROM review_code_review;
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('roadmap_reporting', ?, 'generate', 'report_type', ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify report_type is valid (summary, detailed, executive)
   - Verify output_format is valid (markdown, json, html)
   - Generate output_file path if not provided

2. **Fetch Data**
   - Query all priorities
   - Query all specifications
   - Query all code reviews
   - Calculate metrics

3. **Group Priorities by Status**
   - Completed priorities
   - In Progress priorities
   - Planned priorities
   - Rejected/Blocked priorities

4. **Calculate Metrics**
   - Total count by status
   - Completion percentage
   - Average cycle time
   - Spec coverage
   - Code review pass rate

5. **Generate Content**
   - Build report sections based on report_type
   - Format for specified output_format
   - Include charts data if requested

6. **Write Report**
   - Write to file system (reports directory)
   - Generate unique filename with timestamp
   - Return file path

7. **Create Audit Log Entry**

8. **Return Results**

## Output

```json
{
  "success": true,
  "report_type": "summary",
  "output_format": "markdown",
  "generated_at": "2025-10-26T15:00:00Z",
  "report_url": "docs/reports/roadmap-summary-2025-10-26.md",
  "summary": {
    "total_priorities": 50,
    "completed": 30,
    "in_progress": 10,
    "planned": 8,
    "rejected": 2,
    "completion_rate": 60,
    "avg_cycle_time_days": 3.5
  },
  "metrics": {
    "spec_coverage_percent": 95,
    "code_review_pass_rate": 98,
    "on_time_completion_percent": 85,
    "blocker_count": 2
  },
  "chart_data": {
    "status_distribution": {
      "labels": ["Completed", "In Progress", "Planned", "Rejected"],
      "data": [30, 10, 8, 2]
    }
  }
}
```

## Report Formats

### Summary Report (Default)
- Executive summary
- Key metrics
- Status distribution (chart)
- Completion rate
- Recent completions (last 5)

### Detailed Report
- Summary section
- Metrics section
- Complete priority list with status
- Spec coverage analysis
- Code review results
- Blockers and recommendations

### Executive Report
- High-level overview
- Strategic metrics
- Key risks/blockers (top 5)
- Recommendations (top 3)
- Trend analysis

## Implementation Pattern

```python
def create_roadmap_report(db: DomainWrapper, params: dict):
    """Generate comprehensive roadmap status report."""
    from datetime import datetime
    import json
    from pathlib import Path

    report_type = params.get("report_type", "summary").lower()
    output_format = params.get("output_format", "markdown").lower()
    include_charts = params.get("include_charts", True)
    include_metrics = params.get("include_metrics", True)
    output_file = params.get("output_file")

    # 1. Validate input
    if report_type not in ["summary", "detailed", "executive"]:
        raise ValueError(f"Invalid report_type: {report_type}")

    if output_format not in ["markdown", "json", "html"]:
        raise ValueError(f"Invalid output_format: {output_format}")

    # 2. Fetch data
    priorities = db.read("roadmap_priority")
    specs = db.read("specs_specification")
    reviews = db.read("review_code_review")

    # 3. Group priorities by status
    status_groups = {
        "completed": [p for p in priorities if p.get("status") == "✅ Complete"],
        "in_progress": [p for p in priorities if p.get("status") == "🏗️ In Progress"],
        "planned": [p for p in priorities if p.get("status") == "📝 Planned"],
        "rejected": [p for p in priorities if p.get("status") == "❌ Rejected"],
        "blocked": [p for p in priorities if p.get("status") == "🔴 Blocked"]
    }

    # 4. Calculate metrics
    total = len(priorities)
    completed = len(status_groups["completed"])
    completion_rate = (completed / total * 100) if total > 0 else 0

    # Spec coverage
    with_specs = sum(1 for p in priorities if p.get("spec_id"))
    spec_coverage = (with_specs / total * 100) if total > 0 else 0

    # Code review pass rate
    passed_reviews = sum(1 for r in reviews if r.get("passed"))
    total_reviews = len(reviews)
    review_pass_rate = (passed_reviews / total_reviews * 100) if total_reviews > 0 else 0

    # Average cycle time
    cycle_times = []
    for p in status_groups["completed"]:
        if p.get("started_at") and p.get("completed_at"):
            try:
                start = datetime.fromisoformat(p["started_at"])
                end = datetime.fromisoformat(p["completed_at"])
                days = (end - start).days
                cycle_times.append(days)
            except (ValueError, TypeError):
                pass

    avg_cycle_time = (
        sum(cycle_times) / len(cycle_times) if cycle_times else 0
    )

    # 5. Build report content
    if output_format == "markdown":
        content = build_markdown_report(
            report_type=report_type,
            status_groups=status_groups,
            total=total,
            completed=completed,
            completion_rate=completion_rate,
            spec_coverage=spec_coverage,
            review_pass_rate=review_pass_rate,
            avg_cycle_time=avg_cycle_time,
            include_metrics=include_metrics
        )
    elif output_format == "json":
        content = build_json_report(
            report_type=report_type,
            status_groups=status_groups,
            metrics={
                "completion_rate": completion_rate,
                "spec_coverage": spec_coverage,
                "review_pass_rate": review_pass_rate,
                "avg_cycle_time": avg_cycle_time
            }
        )
    else:  # html
        content = build_html_report(
            report_type=report_type,
            status_groups=status_groups,
            metrics={
                "completion_rate": completion_rate,
                "spec_coverage": spec_coverage,
                "review_pass_rate": review_pass_rate,
                "avg_cycle_time": avg_cycle_time
            }
        )

    # 6. Write report to file
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d")

    if not output_file:
        report_dir = Path("docs/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        output_file = report_dir / f"roadmap-{report_type}-{timestamp}.{output_format}"

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(content)

    # 7. Create audit log entry
    db.write("system_audit", {
        "table_name": "roadmap_reporting",
        "item_id": f"report_{timestamp}",
        "action": "generate",
        "field_changed": "report_type",
        "new_value": json.dumps({
            "report_type": report_type,
            "output_format": output_format,
            "total_priorities": total,
            "completion_rate": completion_rate,
            "timestamp": now.isoformat()
        }),
        "changed_by": "project_manager",
        "changed_at": now.isoformat()
    }, action="create")

    # 8. Build chart data
    chart_data = {}
    if include_charts:
        chart_data = {
            "status_distribution": {
                "labels": ["Completed", "In Progress", "Planned", "Rejected", "Blocked"],
                "data": [
                    len(status_groups["completed"]),
                    len(status_groups["in_progress"]),
                    len(status_groups["planned"]),
                    len(status_groups["rejected"]),
                    len(status_groups["blocked"])
                ]
            }
        }

    # 9. Return results
    return {
        "success": True,
        "report_type": report_type,
        "output_format": output_format,
        "generated_at": now.isoformat(),
        "report_url": str(output_file),
        "summary": {
            "total_priorities": total,
            "completed": completed,
            "in_progress": len(status_groups["in_progress"]),
            "planned": len(status_groups["planned"]),
            "rejected": len(status_groups["rejected"]),
            "completion_rate": round(completion_rate, 1),
            "avg_cycle_time_days": round(avg_cycle_time, 1)
        },
        "metrics": {
            "spec_coverage_percent": round(spec_coverage, 1),
            "code_review_pass_rate": round(review_pass_rate, 1)
        } if include_metrics else {},
        "chart_data": chart_data
    }

def build_markdown_report(report_type: str, status_groups: dict,
                         total: int, completed: int, completion_rate: float,
                         spec_coverage: float, review_pass_rate: float,
                         avg_cycle_time: float, include_metrics: bool) -> str:
    """Build markdown format report."""
    from datetime import datetime

    lines = [
        "# Roadmap Status Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## Executive Summary",
        f"\n- **Total Priorities**: {total}",
        f"- **Completed**: {completed} ({completion_rate:.1f}%)",
        f"- **In Progress**: {len(status_groups['in_progress'])}",
        f"- **Planned**: {len(status_groups['planned'])}",
        f"- **Rejected/Blocked**: {len(status_groups['rejected']) + len(status_groups['blocked'])}",
    ]

    if include_metrics:
        lines.extend([
            "\n## Metrics",
            f"\n- **Spec Coverage**: {spec_coverage:.1f}%",
            f"- **Code Review Pass Rate**: {review_pass_rate:.1f}%",
            f"- **Average Cycle Time**: {avg_cycle_time:.1f} days",
        ])

    if report_type == "detailed":
        lines.append("\n## Completed Priorities\n")
        for p in status_groups["completed"][:10]:
            lines.append(f"- {p.get('id')}: {p.get('title', 'Unknown')}")

        lines.append("\n## In Progress Priorities\n")
        for p in status_groups["in_progress"]:
            lines.append(f"- {p.get('id')}: {p.get('title', 'Unknown')}")

    return "\n".join(lines)

def build_json_report(report_type: str, status_groups: dict, metrics: dict) -> str:
    """Build JSON format report."""
    import json
    from datetime import datetime

    report = {
        "generated_at": datetime.now().isoformat(),
        "report_type": report_type,
        "summary": {
            "total_priorities": sum(len(v) for v in status_groups.values()),
            "by_status": {k: len(v) for k, v in status_groups.items()}
        },
        "metrics": metrics
    }

    return json.dumps(report, indent=2)

def build_html_report(report_type: str, status_groups: dict, metrics: dict) -> str:
    """Build HTML format report."""
    from datetime import datetime

    html = f"""
    <html>
    <head>
        <title>Roadmap Status Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Roadmap Status Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Summary</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Count</th>
            </tr>
    """

    for status, items in status_groups.items():
        html += f"<tr><td>{status}</td><td>{len(items)}</td></tr>"

    html += """
        </table>
    </body>
    </html>
    """

    return html
```

## Report Types

### Summary (Default)
- Quick overview of status
- Key metrics
- 5-item samples from each category

### Detailed
- All priority details listed
- Complete metrics
- Analysis by status
- Useful for full review

### Executive
- High-level overview
- Strategic focus
- Key risks and recommendations
- Trend analysis

## Success Criteria

- ✅ Report generated in requested format
- ✅ All metrics included
- ✅ Charts generated (if requested)
- ✅ Report saved to file
- ✅ Audit log created
- ✅ File path returned

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| InvalidReportTypeError | Unknown report_type | Use "summary", "detailed", or "executive" |
| InvalidFormatError | Unknown output_format | Use "markdown", "json", or "html" |
| FileWriteError | Cannot write to file | Check directory permissions |

## CFR Compliance

- **CFR-009**: No sound notifications
- **CFR-015**: File-based reports in docs/reports directory
- **CFR-007**: Efficient report generation with caching

## Related Commands

- `project_manager.analyze_project_health` - Health analysis
- `project_manager.strategic_planning` - Next priority planning
