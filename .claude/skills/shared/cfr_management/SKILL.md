# cfr-management Skill

**Agents**: project_manager, architect
**Purpose**: Consistent CFR (Critical Functional Requirement) management and compliance checking

## Overview

This skill enables both project_manager and architect to manage CFRs consistently:
- **project_manager**: CFR creation, tracking, enforcement monitoring
- **architect**: CFR compliance checking, technical implementation guidance
- **Together**: Coordinated system integrity and requirement enforcement

## Capabilities

### 1. CFR Discovery
- **list_cfrs**: List all CFRs with summaries
- **read_cfr**: Read specific CFR details
- **search_cfrs**: Find CFRs by keyword or topic
- **get_next_cfr_number**: Get next available CFR number

### 2. CFR Creation (project_manager primary, architect assists)
- **create_cfr**: Create new CFR with proper formatting
- **validate_cfr_format**: Check CFR follows standard template
- **generate_cfr_skeleton**: Create CFR template with placeholders

### 3. CFR Compliance (architect primary, project_manager monitors)
- **check_compliance**: Verify code/process complies with CFR
- **find_violations**: Scan for potential CFR violations
- **suggest_fixes**: Recommend fixes for violations

### 4. CFR Reporting
- **generate_cfr_summary**: Create summary report of all CFRs
- **get_cfr_metrics**: Track CFR adoption and violations
- **find_related_cfrs**: Find CFRs related to specific topic

## Usage Examples

### List all CFRs
```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("cfr-management")

# List all CFRs
result = skill.execute(action="list_cfrs")

# Returns:
# {
#   "cfrs": [
#     {
#       "number": "CFR-000",
#       "title": "Prevent File Conflicts At All Costs",
#       "status": "active",
#       "enforcement": "code-level"
#     },
#     {
#       "number": "CFR-001",
#       "title": "Document Ownership Boundaries",
#       "status": "active",
#       "enforcement": "code-level"
#     },
#     ...
#   ],
#   "total_count": 15
# }
```

### Read specific CFR
```python
# Get CFR details
result = skill.execute(
    action="read_cfr",
    cfr_number=14
)

# Returns:
# {
#   "cfr_number": "CFR-014",
#   "title": "All Orchestrator Activities Must Be Traced in Database",
#   "rule": "ALL orchestrator activities...",
#   "core_principles": [...],
#   "enforcement": {...},
#   "related_cfrs": ["CFR-000", "CFR-001"],
#   "user_story": "US-110"
# }
```

### Search CFRs by keyword
```python
# Find CFRs related to "database"
result = skill.execute(
    action="search_cfrs",
    keyword="database"
)

# Returns:
# {
#   "matches": [
#     {
#       "cfr_number": "CFR-014",
#       "title": "All Orchestrator Activities Must Be Traced in Database",
#       "relevance_score": 0.95,
#       "excerpt": "...ALL orchestrator activities must be persisted in SQLite database..."
#     }
#   ]
# }
```

### Get next CFR number
```python
# Get next available CFR number
result = skill.execute(action="get_next_cfr_number")

# Returns:
# {
#   "next_cfr_number": 15,
#   "formatted": "CFR-015"
# }
```

### Create new CFR (project_manager)
```python
# Create CFR template
result = skill.execute(
    action="create_cfr",
    title="Agent Health Monitoring",
    rule="All agents MUST report health status every 60 seconds",
    why_critical=[
        "Early detection of hung agents",
        "Proactive failure recovery",
        "System reliability metrics"
    ],
    enforcement_type="code-level",
    related_user_story="US-120"
)

# Returns:
# {
#   "cfr_number": "CFR-015",
#   "file_path": "docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md",
#   "line_number": 4200,
#   "preview": "## CFR-015: Agent Health Monitoring\n\n**Rule**: All agents..."
# }
```

### Validate CFR format
```python
# Check if CFR follows template
result = skill.execute(
    action="validate_cfr_format",
    cfr_number=14
)

# Returns:
# {
#   "valid": true,
#   "issues": [],
#   "completeness_score": 100,
#   "sections_present": [
#     "Rule",
#     "Core Principle",
#     "Why This Is Critical",
#     "Real-World Problem This Solves",
#     "Enforcement",
#     "Acceptance Criteria",
#     "Related CFRs"
#   ],
#   "missing_sections": []
# }
```

### Check CFR compliance (architect)
```python
# Check if code complies with CFR-014
result = skill.execute(
    action="check_compliance",
    cfr_number=14,
    files=[
        ".claude/skills/shared/orchestrator-agent-management/agent_management.py",
        "coffee_maker/orchestrator/dashboard.py"
    ]
)

# Returns:
# {
#   "compliant": false,
#   "violations": [
#     {
#       "file": "agent_management.py",
#       "line": 139,
#       "violation": "Writing to JSON file instead of database",
#       "severity": "high",
#       "cfr_section": "Enforcement - JSON files FORBIDDEN",
#       "suggested_fix": "Replace JSON write with SQLite INSERT"
#     }
#   ],
#   "compliance_score": 60,  # 60% compliant
#   "remediation_effort": "2 hours"
# }
```

### Find violations across codebase (architect)
```python
# Scan for CFR-014 violations
result = skill.execute(
    action="find_violations",
    cfr_number=14,
    scope="orchestrator"  # Only scan orchestrator files
)

# Returns:
# {
#   "total_violations": 3,
#   "violations": [
#     {
#       "file": "agent_management.py",
#       "lines": [139, 408],
#       "violation_type": "json_write_forbidden",
#       "severity": "high"
#     },
#     {
#       "file": "dashboard.py",
#       "lines": [64],
#       "violation_type": "reading_json_state",
#       "severity": "medium"
#     }
#   ],
#   "remediation_plan": [
#     "Step 1: Create agent_lifecycle table migration",
#     "Step 2: Update agent_management.py to use SQLite",
#     "Step 3: Update dashboard.py to query database",
#     "Step 4: Remove JSON write operations"
#   ]
# }
```

### Suggest fixes for violations (architect)
```python
# Get fix recommendations
result = skill.execute(
    action="suggest_fixes",
    cfr_number=14,
    file="agent_management.py",
    line=139
)

# Returns:
# {
#   "violation": "Writing agent state to JSON file",
#   "cfr_requirement": "ALL orchestrator activities must use SQLite database",
#   "suggested_fixes": [
#     {
#       "approach": "Replace JSON write with SQLite INSERT",
#       "code_example": """
#         # BEFORE (violation)
#         self.state["active_agents"][str(process.pid)] = agent_info
#         self._save_state()  # Writes JSON
#
#         # AFTER (compliant)
#         with sqlite3.connect("data/orchestrator.db") as conn:
#             conn.execute('''
#                 INSERT INTO agent_lifecycle
#                 (pid, agent_type, task_id, spawned_at, status, command)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (process.pid, agent_type, task_id, spawned_at, 'spawned', command))
#       """,
#       "files_to_modify": ["agent_management.py"],
#       "estimated_effort": "15 minutes"
#     }
#   ]
# }
```

### Generate CFR summary report (project_manager)
```python
# Create CFR summary for status meeting
result = skill.execute(
    action="generate_cfr_summary",
    format="markdown"
)

# Returns:
# {
#   "report_path": "reports/cfr-summary-20251020.md",
#   "summary": {
#     "total_cfrs": 15,
#     "active_cfrs": 15,
#     "enforcement_breakdown": {
#       "code-level": 10,
#       "process-level": 3,
#       "design-level": 2
#     },
#     "compliance_status": {
#       "fully_compliant": 12,
#       "partial_compliance": 2,
#       "non_compliant": 1
#     },
#     "recent_cfrs": ["CFR-014", "CFR-013"]
#   }
# }
```

### Get CFR metrics (project_manager)
```python
# Track CFR health metrics
result = skill.execute(action="get_cfr_metrics")

# Returns:
# {
#   "metrics": {
#     "total_cfrs": 15,
#     "avg_compliance_score": 87.5,
#     "critical_violations": 2,
#     "medium_violations": 5,
#     "low_violations": 8,
#     "cfrs_with_violations": ["CFR-014", "CFR-009"],
#     "recently_added": ["CFR-014"],
#     "most_violated": "CFR-013",
#     "best_compliance": "CFR-001"
#   }
# }
```

### Find related CFRs
```python
# Find CFRs related to CFR-014
result = skill.execute(
    action="find_related_cfrs",
    cfr_number=14
)

# Returns:
# {
#   "related_cfrs": [
#     {
#       "cfr_number": "CFR-000",
#       "title": "Prevent File Conflicts At All Costs",
#       "relationship": "Database provides ACID transactions, prevents race conditions",
#       "relevance_score": 0.8
#     },
#     {
#       "cfr_number": "CFR-001",
#       "title": "Document Ownership Boundaries",
#       "relationship": "orchestrator owns data/orchestrator.db, no conflicts",
#       "relevance_score": 0.6
#     }
#   ]
# }
```

## CFR Template Structure

When creating new CFRs, the skill ensures this structure:

```markdown
## CFR-{NUMBER}: {TITLE}

**Rule**: {Single sentence rule statement}

**Core Principle**:
```
✅ ALLOWED: {What's allowed}
❌ FORBIDDEN: {What's forbidden}
```

**Why This Is Critical**:

1. **{Reason 1}**: {Explanation}
2. **{Reason 2}**: {Explanation}
...

**Real-World Problem This Solves**:

```
BEFORE CFR-{NUMBER} (chaotic):
{Problem description}
→ Result: {Negative outcomes}

AFTER CFR-{NUMBER} (clean):
{Solution description}
→ Result: {Positive outcomes}
```

### Enforcement

{Enforcement mechanisms}

### Acceptance Criteria

1. ✅ {Criterion 1}
2. ✅ {Criterion 2}
...

### Relationship to Other CFRs

**CFR-{NUMBER}**: {Relationship}
...

### Success Metrics

{Measurable metrics}

**Enforcement**: {How it's enforced}
**Monitoring**: {How it's monitored}
**User Story**: {Related US}
```

## Integration Points

### With project_manager
- Monitor CFR compliance across codebase
- Track CFR metrics in status reports
- Escalate violations to architect for remediation

### With architect
- Use CFR compliance checks before approving specs
- Generate remediation plans for violations
- Update CFRs based on architectural changes

### With code_developer
- Reference CFRs in commit messages when fixing violations
- Check CFR compliance before marking US complete

## Expected Time Savings

- **Manual CFR Management**: 30-60 minutes per CFR
- **With Skill**: 5-10 minutes per CFR
- **Time Saved**: 70-80% reduction

## File Locations

- **CFR Document**: `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- **CFR Template**: `.claude/skills/shared/cfr-management/templates/cfr-template.md`
- **Violation Reports**: `reports/cfr-violations/`

## Related Skills

- `roadmap-auto-management`: CFRs integrated into ROADMAP planning
- `code-forensics`: Used for finding CFR violations in code
- `architecture-reuse-check`: Checks specs comply with CFRs

## Author

architect + code_developer

## Created

2025-10-20

## Version

1.0.0
