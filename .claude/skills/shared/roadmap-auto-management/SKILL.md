# roadmap-auto-management Skill

**Agents**: project_manager, architect
**Purpose**: Autonomous ROADMAP planning, health monitoring, and technical optimization

## Overview

This skill enables continuous, autonomous ROADMAP management:
- **project_manager**: Strategic planning, priority creation, dependency analysis
- **architect**: Technical feasibility review, refactoring priorities, POC recommendations
- **Together**: Coordinated ROADMAP optimization for maximum delivery velocity

## Capabilities

### 1. Auto-Planning (project_manager)
- **analyze_roadmap_health**: Check for gaps, missing work, blocked priorities
- **identify_next_priorities**: Suggest next 5-10 priorities based on trends
- **create_priority**: Add new priority to ROADMAP with strategic spec
- **adjust_priorities**: Reorder priorities based on dependencies/urgency
- **estimate_velocity**: Calculate team velocity, predict completion dates

### 2. Technical Review (architect)
- **review_technical_feasibility**: Check if priorities are implementable
- **identify_refactoring_needs**: Find technical debt to prioritize
- **recommend_pocs**: Suggest POCs for high-risk priorities
- **validate_dependencies**: Ensure dependency chains are correct
- **estimate_complexity**: Provide technical complexity estimates

### 3. Collaboration (both)
- **sync_roadmap**: project_manager presents plan → architect reviews → consensus
- **escalate_blockers**: Identify work that needs user decision
- **track_decisions**: Log planning decisions and rationale
- **generate_report**: Weekly planning report with metrics

## Usage Examples

### project_manager: Analyze ROADMAP health
```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("roadmap-auto-management")

# Check ROADMAP health
result = skill.execute(action="analyze_roadmap_health")

# Returns:
# {
#   "health_score": 85,  # 0-100
#   "gaps": [
#     "No testing priorities for next 2 sprints",
#     "Security audit overdue (90 days since last)"
#   ],
#   "blocked_priorities": [
#     {"number": 15, "blocker": "Waiting for SPEC-015"}
#   ],
#   "velocity_trend": "declining (-10% last week)"
# }
```

### project_manager: Identify next priorities
```python
# Get AI-suggested next priorities
result = skill.execute(
    action="identify_next_priorities",
    count=10,
    context="Focus on user-facing features and performance"
)

# Returns:
# {
#   "suggested_priorities": [
#     {
#       "title": "Implement caching layer for API responses",
#       "rationale": "30% of requests are repeat queries, caching would improve UX",
#       "estimated_effort": "8 hours",
#       "priority_score": 8.5
#     },
#     ...
#   ]
# }
```

### project_manager: Create new priority
```python
# Add priority to ROADMAP
result = skill.execute(
    action="create_priority",
    title="Implement Redis caching layer",
    description="Cache API responses to improve performance",
    estimated_effort="8 hours",
    dependencies=["US-050"],  # Depends on dependency management
    create_strategic_spec=True
)

# Returns:
# {
#   "priority_number": 73,
#   "priority_name": "US-073",
#   "strategic_spec_created": true,
#   "added_to_roadmap": true
# }
```

### architect: Review technical feasibility
```python
# Review next 5 priorities for technical issues
result = skill.execute(
    action="review_technical_feasibility",
    priority_numbers=[10, 12, 15, 20, 25]
)

# Returns:
# {
#   "feasibility_report": [
#     {
#       "priority": 10,
#       "feasible": true,
#       "confidence": 0.9,
#       "concerns": []
#     },
#     {
#       "priority": 15,
#       "feasible": false,
#       "confidence": 0.3,
#       "concerns": [
#         "Missing dependency: redis client not installed",
#         "Architectural complexity: requires multi-process coordination"
#       ],
#       "recommended_action": "Create POC-015 first"
#     }
#   ]
# }
```

### architect: Identify refactoring needs
```python
# Find technical debt to prioritize
result = skill.execute(
    action="identify_refactoring_needs",
    use_code_review_history=True,  # Use code-review-history skill
    min_priority_score=7
)

# Returns:
# {
#   "refactoring_priorities": [
#     {
#       "title": "Extract duplicated error handling into shared ErrorHandler mixin",
#       "files_affected": ["daemon.py", "git_manager.py", "roadmap_parser.py"],
#       "occurrences": 12,
#       "estimated_effort": "4 hours",
#       "priority_score": 8.5,
#       "rationale": "Appears in 3 code reviews, reduces maintenance burden"
#     }
#   ]
# }
```

### Both: Sync ROADMAP changes
```python
# project_manager proposes changes, architect reviews
result = skill.execute(
    action="sync_roadmap",
    proposed_priorities=[
        {"number": 73, "action": "add", "title": "Redis caching"},
        {"number": 15, "action": "postpone", "reason": "High complexity, need POC"}
    ],
    request_architect_review=True
)

# Returns:
# {
#   "architect_reviewed": true,
#   "approved": [73],
#   "rejected": [],
#   "requires_modification": [
#     {
#       "priority": 15,
#       "architect_feedback": "Agree postpone needed. Suggest creating POC-015 first.",
#       "recommended_action": "Add POC-015 as separate priority"
#     }
#   ]
# }
```

## Output Format

### analyze_roadmap_health
```json
{
  "health_score": 85,
  "metrics": {
    "planned_count": 32,
    "in_progress_count": 2,
    "completed_count": 45,
    "blocked_count": 1,
    "avg_cycle_time_days": 2.3,
    "velocity_trend": "stable"
  },
  "gaps": [
    "No security priorities in next 10 items",
    "Testing coverage declining (78% → 72%)"
  ],
  "recommendations": [
    "Add security audit priority",
    "Create test coverage improvement priority"
  ]
}
```

### identify_next_priorities
```json
{
  "suggested_priorities": [
    {
      "title": "Implement API response caching",
      "description": "Cache frequently accessed API responses using Redis",
      "estimated_effort": "8 hours",
      "priority_score": 8.5,
      "rationale": "30% performance improvement, high user impact",
      "dependencies": ["US-050"],
      "category": "performance"
    }
  ],
  "total_suggested": 10,
  "context_used": "User-facing features and performance"
}
```

## Integration with Orchestrator

```python
# In continuous_work_loop.py

def _coordinate_project_manager(self):
    """Spawn project_manager for auto-planning."""

    # Check if planning needed (weekly cycle)
    if self._should_run_planning():
        # Analyze ROADMAP health
        health = self.roadmap_mgmt.execute(action="analyze_roadmap_health")

        if health["result"]["health_score"] < 80:
            # Spawn project_manager to improve ROADMAP
            self.agent_mgmt.execute(
                action="spawn_project_manager",
                task_type="auto_planning",
                auto_approve=True
            )

def _coordinate_architect_roadmap_review(self):
    """Architect reviews ROADMAP for technical feasibility."""

    # Weekly technical review of next 10 priorities
    if self._should_run_technical_review():
        planned = self._get_next_planned_priorities(10)

        # Spawn architect for review
        self.agent_mgmt.execute(
            action="spawn_architect",
            task_type="roadmap_technical_review",
            priority_numbers=[p["number"] for p in planned],
            auto_approve=True
        )
```

## Triggers

### Auto-Planning Triggers (project_manager):
- **Weekly**: Every 7 days, analyze ROADMAP health
- **Low velocity**: When velocity drops >20%
- **Gaps detected**: When critical areas (security, testing) have no priorities
- **Completion milestone**: When major epic completes

### Technical Review Triggers (architect):
- **Weekly**: Review next 10 planned priorities
- **Before implementation**: Check feasibility before code_developer starts
- **After code reviews**: Extract refactoring opportunities from reviews
- **Dependency changes**: When pyproject.toml updated

## Performance Targets

- Analyze ROADMAP health: <2s
- Identify next priorities: <5s (AI-assisted)
- Create priority: <1s
- Review technical feasibility: <3s per priority
- Identify refactoring needs: <10s (reads code-review-history)

## Error Handling

- Returns `{"error": "message"}` on failure
- Validates ROADMAP format before modifications
- Backs up ROADMAP before changes
- Logs all planning decisions for audit trail

## Dependencies

- `roadmap-health` skill - ROADMAP analysis
- `code-review-history` skill - Extract refactoring needs
- `architecture-reuse-check` skill - Check for duplicate work
- `roadmap_parser.py` - Parse and modify ROADMAP
