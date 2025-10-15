# Technical Specification Generation Tutorial

**Feature**: US-016 - Interactive Spec Generation with Time Estimates
**Command**: `/spec`
**Purpose**: Generate detailed technical specifications from user stories with AI-powered task breakdown and delivery estimates

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Usage Examples](#usage-examples)
4. [Understanding the Output](#understanding-the-output)
5. [Workflow Details](#workflow-details)
6. [FAQ](#faq)
7. [Advanced Usage](#advanced-usage)

---

## Overview

The `/spec` command allows you to generate comprehensive technical specifications from natural language user stories. It uses AI to:

- Break down user stories into phases and tasks
- Estimate time for each task with confidence levels
- Calculate realistic delivery dates with buffer
- Update ROADMAP with spec references
- Generate markdown documentation

### Key Benefits

- **Faster Planning**: Generate detailed specs in minutes instead of hours
- **Consistent Format**: All specs follow the same structure
- **Realistic Estimates**: Time estimates include testing, documentation, and buffers
- **Historical Learning**: Estimates improve based on completed tasks (Phase 4)
- **ROADMAP Integration**: Approved specs are automatically linked in ROADMAP

---

## Quick Start

### Basic Usage

```bash
poetry run project-manager /spec "As a user, I want email notifications" --type integration --complexity medium --id US-033
```

### What Happens

1. AI analyzes the user story and generates a technical spec
2. You see a summary with time estimates and delivery date
3. You review and approve/reject the spec
4. If approved, ROADMAP is updated with spec reference

### Command Options

- `user_story` (required): Natural language description of feature
- `--type` (optional): Feature type (crud, integration, ui, infrastructure, analytics, security) - default: general
- `--complexity` (optional): Overall complexity (low, medium, high) - default: medium
- `--id` (optional): User story ID (e.g., US-033) - required for ROADMAP integration

---

## Usage Examples

### Example 1: Simple CRUD Feature

```bash
poetry run project-manager /spec \
  "As an admin, I want to manage user accounts with create, read, update, delete operations" \
  --type crud \
  --complexity low \
  --id US-040
```

**Generated Spec Includes:**
- Database model design
- CRUD API endpoints
- Input validation
- Error handling
- Unit and integration tests

**Typical Estimate:** 8-12 hours (1-1.5 days)

---

### Example 2: Integration Feature

```bash
poetry run project-manager /spec \
  "As a user, I want to receive email notifications when tasks are completed" \
  --type integration \
  --complexity medium \
  --id US-033
```

**Generated Spec Includes:**
- Email service integration
- Notification templates
- Event triggers
- Error handling and retries
- Integration tests

**Typical Estimate:** 16-24 hours (2-3 days)

---

### Example 3: Complex UI Feature

```bash
poetry run project-manager /spec \
  "As a user, I want a dashboard showing real-time analytics with charts and filters" \
  --type ui \
  --complexity high \
  --id US-045
```

**Generated Spec Includes:**
- UI component design
- Data fetching and caching
- Chart library integration
- Responsive design
- User interaction tests

**Typical Estimate:** 24-40 hours (3-5 days)

---

### Example 4: Without User Story ID (Exploratory)

```bash
poetry run project-manager /spec \
  "File upload with virus scanning" \
  --type security \
  --complexity high
```

**Note:** Without `--id`, the spec is generated but ROADMAP is not updated. Use this for exploratory planning or features not yet in ROADMAP.

---

## Understanding the Output

### Step 1: Spec Summary

```
Specification complete! 📋

Total Estimated Time: 24.0 hours (3.0 days)
Phases: 4
Tasks: 12
Confidence: 85%

With 15% buffer for unknowns:
- Buffered Time: 27.6 hours (4.6 days)
- Expected Delivery: 2025-10-20

Spec saved to: docs/US-033_TECHNICAL_SPEC.md

Would you like to review the spec? [y/n]
```

**What This Means:**
- **Total Estimated Time**: Base estimate without buffer (24h = 3 days @ 8h/day)
- **Phases**: Number of implementation phases (typically 2-6)
- **Tasks**: Total number of tasks across all phases (typically 8-20)
- **Confidence**: AI's confidence in the estimate (70-95%)
- **Buffer**: Automatic buffer based on confidence (10-20%)
- **Buffered Time**: Realistic estimate including buffer (27.6h = 4.6 days @ 6h/day velocity)
- **Expected Delivery**: Target completion date from today

### Step 2: Review Spec

If you answer `y`, the spec file opens in your editor. Review:
- Feature description and business value
- Phase breakdown and task details
- Time estimates and dependencies
- Risks and success criteria

### Step 3: ROADMAP Update Preview

```
When approved, ROADMAP.md will be updated:

## US-033: Email Notification System

**Status**: 📝 READY TO IMPLEMENT
**Estimated Time**: 27.6 hours (4.6 days)
**Spec**: docs/US-033_TECHNICAL_SPEC.md
**Confidence**: 85%
**Expected Delivery**: 2025-10-20 (with 15% buffer)

Approve this spec and update ROADMAP? [y/n]
```

### Step 4: Approval

- **Approve (y)**: Spec is marked approved, ROADMAP is updated
- **Reject (n)**: You'll be asked for a reason. Spec is saved but ROADMAP is not updated

---

## Workflow Details

### Full Workflow Diagram

```
User Input
    ↓
/spec command
    ↓
AI Analysis (SpecGenerator)
    ↓
Task Breakdown (TaskEstimator)
    ↓
Time Estimation with Historical Adjustment
    ↓
Delivery Calculation with Buffer
    ↓
Spec File Generated (docs/US-XXX_TECHNICAL_SPEC.md)
    ↓
User Review
    ↓
Approve? → Yes → ROADMAP Updated
         → No  → Rejected (spec kept for reference)
```

### Buffer Calculation

Buffer is automatically calculated based on confidence:

- **High Confidence (90%+)**: 10% buffer
- **Medium Confidence (70-90%)**: 15% buffer
- **Low Confidence (<70%)**: 20% buffer

### Velocity Adjustment

Estimates use **6 hours/day velocity** (not 8 hours) to account for:
- Meetings (1h/day)
- Code reviews (0.5h/day)
- Interruptions (0.5h/day)

This makes delivery dates more realistic.

---

## FAQ

### Q: How accurate are the time estimates?

**A:** Initial estimates (Phase 1-3) have ~70-85% confidence. With historical data (Phase 4), confidence improves to 85-95%. Estimates include:
- Core implementation time
- Testing (30% multiplier)
- Documentation (15% multiplier)
- Security (25% multiplier, if applicable)
- Integration complexity (20% multiplier, if applicable)

### Q: Can I regenerate a spec if I'm not happy with it?

**A:** Yes! Just run the `/spec` command again. You can adjust:
- User story description (add more detail)
- Feature type (more specific type = better estimates)
- Complexity (adjust if AI got it wrong)

### Q: What happens if I reject a spec?

**A:** The spec file is kept for reference (in case you want to revisit it), but ROADMAP is not updated. You can generate a new spec with refined requirements.

### Q: Can I edit the generated spec?

**A:** Yes! The spec is a markdown file in `docs/`. Edit it as needed, then manually update ROADMAP if required.

### Q: Do I need to provide a user story ID?

**A:** Only if you want ROADMAP integration. Without `--id`, you can still generate specs for exploratory planning.

### Q: What if my feature doesn't fit the standard types?

**A:** Use `--type general` (default). The AI will infer the appropriate breakdown. You can also combine types by describing them in the user story.

### Q: How do I know which complexity to choose?

**A:** Guidelines:
- **Low**: Simple features, 1-2 components, minimal dependencies (e.g., CRUD operations)
- **Medium**: Moderate features, 3-5 components, some integration (e.g., email notifications)
- **High**: Complex features, 6+ components, heavy integration/UI (e.g., real-time dashboard)

### Q: Can I see examples of generated specs?

**A:** Yes! Check the `docs/` directory for spec files. Look for `*_TECHNICAL_SPEC.md` files.

### Q: What file types are supported?

**A:** Feature types include:
- **crud**: Create, Read, Update, Delete operations
- **integration**: Third-party service integration
- **ui**: User interface components
- **infrastructure**: DevOps, deployment, monitoring
- **analytics**: Data analysis, reporting
- **security**: Authentication, authorization, encryption
- **general**: Default for mixed or exploratory features

---

## Advanced Usage

### Custom Velocity

If your team has a different velocity, you can adjust it in the code:

```python
# In roadmap_cli.py, cmd_spec()
workflow = SpecWorkflow(ai_service, velocity_hours_per_day=7.0)  # Increase to 7h/day
```

### Historical Estimate Adjustment (Phase 4)

Enable historical adjustment to improve estimates based on completed tasks:

```python
# In task_estimator.py
estimator = TaskEstimator(use_historical_adjustment=True)
```

This requires metrics data from US-015.

### Batch Spec Generation

Generate specs for multiple user stories:

```bash
# specs.txt contains one user story per line
while IFS= read -r story; do
  poetry run project-manager /spec "$story" --type integration --complexity medium
done < specs.txt
```

### Spec Templates

All specs use the template in `.claude/commands/generate-technical-spec.md`. You can customize this template to match your team's standards.

---

## Related Documentation

- **US-016 Implementation Summary**: See `docs/US-016_IMPLEMENTATION_SUMMARY.md`
- **SpecGenerator Internals**: See `coffee_maker/autonomous/spec_generator.py`
- **TaskEstimator Details**: See `coffee_maker/utils/task_estimator.py`
- **Metrics Integration**: See `docs/US-015_TECHNICAL_SPEC.md`
- **ROADMAP Format**: See `docs/ROADMAP.md`

---

## Troubleshooting

### Spec generation fails with "AI error"

**Solution:** Check your AI service configuration:
```bash
# Check if Claude CLI is available
which claude

# Or use API mode by setting environment variable
export USE_CLAUDE_CLI=false
```

### ROADMAP not updating after approval

**Solution:** Ensure:
1. You provided `--id` parameter
2. The user story ID exists in ROADMAP.md
3. You approved the spec (answered 'y' to both prompts)

### Estimates seem too high/low

**Solution:**
1. Adjust complexity level
2. Provide more detail in user story
3. Use more specific feature type
4. Enable historical adjustment (if US-015 is complete)

---

**Version:** 1.0 (US-016 Phase 6)
**Last Updated:** 2025-10-16
**Maintainer:** project_manager agent
