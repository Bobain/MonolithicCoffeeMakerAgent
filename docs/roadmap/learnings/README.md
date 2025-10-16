# Lessons Learned Directory

**Owner**: project_manager (CFR-006)

**Purpose**: Capture and apply lessons to prevent repeated errors and user frustration.

## Directory Structure

```
learnings/
├── README.md (this file)
├── WORKFLOW_FAILURE_*.md
├── TECHNICAL_FAILURE_*.md
├── USER_FRUSTRATION_*.md
├── SUCCESS_PATTERN_*.md
├── LESSONS_YYYY_MM.md (monthly summaries)
└── archive/ (lessons >6 months old)
```

## Current Lessons

### Workflow Failures
- [WORKFLOW_FAILURE_US_040.md](WORKFLOW_FAILURE_US_040.md) - User story without CFR validation

### Ownership Violations
- [OWNERSHIP_VIOLATION_US_038.md](OWNERSHIP_VIOLATION_US_038.md) - File ownership violation patterns

### Technical Failures
- (none yet)

### User Frustration
- (none yet)

### Success Patterns
- (to be documented)

### Monthly Summaries
- (will be created monthly starting 2025-11)

## How to Use This Directory

**For Agents**:
1. Read recent lessons weekly
2. Check category relevant to your work
3. Avoid documented failure patterns
4. Reference lessons when uncertain

**For project_manager** (owner):
1. Capture lessons as they occur
2. Create monthly summaries
3. Update agent definitions based on lessons
4. Promote critical lessons to CFRs

**For architect**:
1. Review technical failures
2. Design systemic fixes for recurring issues
3. Update architecture docs based on lessons

**For User**:
1. Review monthly summaries
2. Confirm lessons are being applied
3. Request lesson capture for any frustration

## Lesson Capture Request

Any agent can request lesson capture:
```
delegate_task(
    agent="project_manager",
    task="Capture lesson: [description]",
    context={
        "type": "workflow_failure",
        "severity": "high",
        "description": "...",
        "impact": "..."
    }
)
```

## Maintenance Schedule

**Weekly** (project_manager):
- Review new lessons
- Update relevant documents

**Monthly** (project_manager):
- Create LESSONS_YYYY_MM.md summary
- Archive old lessons (>6 months)

**Quarterly** (project_manager):
- Report to user on lessons and improvements
- Escalate systemic issues to architect

## Statistics

**Total Lessons Captured**: 2
- Workflow Failures: 1
- Ownership Violations: 1
- Technical Failures: 0
- User Frustration: 0
- Success Patterns: 0

**Last Updated**: 2025-10-16
**Next Summary Due**: 2025-11-01 (LESSONS_2025_10.md)
