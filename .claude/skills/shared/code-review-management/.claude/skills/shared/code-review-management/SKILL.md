# code-review-management Skill

**Agents**: code-reviewer, architect
**Purpose**: Collaborative code review tracking, action item extraction, and improvement coordination

## Overview

This skill enables code-reviewer and architect to work together on managing code reviews:
- **code-reviewer**: Creates reviews, tracks findings, marks issues as addressed
- **architect**: Reads reviews, extracts refactoring opportunities, integrates into specs

## Capabilities

### 1. Review Lifecycle Management
- **List reviews**: Get all reviews (filtered by status, priority, date range)
- **Get review**: Read specific review by ID or commit hash
- **Track status**: Mark reviews as pending/addressed/closed
- **Archive old reviews**: Clean up reviews older than N days

### 2. Action Item Extraction
- **Extract action items**: Parse reviews for TODO, FIXME, REFACTOR tags
- **Categorize findings**: Group by type (bug, refactoring, optimization, security)
- **Priority scoring**: Rank action items by severity and impact
- **Link to specs**: Associate action items with technical specs

### 3. Integration Tracking
- **Mark as integrated**: Track which review findings are in specs
- **Spec references**: Link reviews to SPEC-XXX documents
- **Progress tracking**: Monitor how many findings have been addressed
- **Trend analysis**: Identify recurring issues across reviews

### 4. Collaboration Features
- **Architect summaries**: Generate digest of reviews for architect daily review
- **Refactoring opportunities**: Highlight patterns suitable for SPEC creation
- **Follow-up reminders**: Alert when reviews need attention
- **Cross-reference**: Link related reviews and specs

## Usage Examples

### code-reviewer: Create and track reviews
```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("code-review-management")

# List recent reviews
result = skill.execute(action="list_reviews", status="pending", limit=10)

# Extract action items from a review
result = skill.execute(
    action="extract_action_items",
    review_path="docs/code-reviews/REVIEW-2025-10-19-abc123.md"
)

# Mark review as addressed
result = skill.execute(
    action="update_status",
    review_id="REVIEW-2025-10-19-abc123",
    status="addressed"
)
```

### architect: Integrate findings into specs
```python
# Get reviews for daily integration (CFR-011)
result = skill.execute(
    action="get_unread_reviews",
    agent="architect"
)

# Mark review as read and integrated
result = skill.execute(
    action="mark_integrated",
    review_id="REVIEW-2025-10-19-abc123",
    spec_ref="SPEC-075"
)

# Get refactoring opportunities
result = skill.execute(
    action="get_refactoring_opportunities",
    min_priority=7
)
```

## Output Format

### list_reviews
```json
{
  "reviews": [
    {
      "id": "REVIEW-2025-10-19-abc123",
      "commit": "abc123",
      "date": "2025-10-19",
      "status": "pending",
      "priority": "US-064",
      "findings_count": 5,
      "action_items": 3
    }
  ],
  "total": 15,
  "pending": 8,
  "addressed": 5,
  "closed": 2
}
```

### extract_action_items
```json
{
  "action_items": [
    {
      "type": "refactoring",
      "severity": 7,
      "description": "Extract duplicated logic into shared utility",
      "file": "daemon.py",
      "line": 245,
      "estimated_effort": "2h"
    }
  ],
  "summary": {
    "bugs": 2,
    "refactoring": 3,
    "optimization": 1,
    "security": 0
  }
}
```

### get_refactoring_opportunities
```json
{
  "opportunities": [
    {
      "pattern": "Duplicated error handling",
      "occurrences": 5,
      "files": ["daemon.py", "git_manager.py"],
      "recommended_action": "Create shared ErrorHandler mixin",
      "estimated_savings": "40 LOC",
      "priority": 8
    }
  ]
}
```

## Integration Points

### CFR-011: Architect Daily Integration
- architect uses `get_unread_reviews()` daily
- Must read ALL reviews before creating specs
- Tracks last read date per review

### CFR-010: Continuous Spec Improvement
- Identifies recurring patterns from reviews
- Suggests spec updates based on findings
- Tracks which specs need revision

### Code Review Workflow
1. **code-reviewer**: Creates review → `create_review()`
2. **code-reviewer**: Extracts findings → `extract_action_items()`
3. **architect**: Reads review → `mark_as_read()`
4. **architect**: Integrates into spec → `mark_integrated(spec_ref="SPEC-075")`
5. **code_developer**: Implements fixes → `update_status(status="addressed")`
6. **code-reviewer**: Verifies fixes → `update_status(status="closed")`

## Performance Targets

- List reviews: <100ms
- Extract action items: <500ms
- Get refactoring opportunities: <1s
- Archive old reviews: <2s

## Dependencies

- `docs/code-reviews/` directory (created by code-reviewer)
- `docs/code-reviews/INDEX.md` (review index)
- Review format: Markdown with frontmatter

## Error Handling

- Returns `{"result": null, "error": "message"}` on failure
- Graceful handling of missing files
- Validates review format before processing
- Logs all operations for debugging
