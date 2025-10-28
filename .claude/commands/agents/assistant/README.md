# Assistant Agent Commands

11 commands for demo management, bug reporting, and intelligent delegation.

## Commands

### Demo Management (3 commands)

- **create-demo** - Create new demo session for feature demonstration
  - Input: FEATURE_NAME, DEMO_TYPE (interactive|video|screenshot_series)
  - Output: session_id, output_path, puppeteer_session_id
  - Use case: Start recording feature demos with Puppeteer MCP

- **record-demo-session** - Execute and record demo steps with screenshots
  - Input: SESSION_ID, STEPS (array), VERIFY_CRITERIA (optional)
  - Output: screenshots_captured, verification_results, duration_seconds
  - Use case: Automate demo execution with step-by-step recording

- **validate-demo-output** - Verify demo results meet acceptance criteria
  - Input: SESSION_ID, CRITERIA (array), MARK_COMPLETE (bool)
  - Output: validation_results, overall_status
  - Use case: Quality assurance for recorded demos

### Bug Reporting (3 commands)

- **report-bug** - Create structured bug report in database
  - Input: TITLE, DESCRIPTION, SEVERITY, PRIORITY_ID (optional)
  - Output: bug_id (BUG-XXX), status=open, created_at
  - Use case: Log issues found during testing or demos

- **track-bug-status** - Monitor bug lifecycle and resolution
  - Input: BUG_ID, STATUS, RESOLUTION_NOTES (if resolved), NOTIFY_REPORTER
  - Output: previous_status, new_status, resolved_at
  - Use case: Update bug progress from open → in_progress → resolved

- **link-bug-to-priority** - Associate bug with roadmap priority
  - Input: BUG_ID, PRIORITY_ID
  - Output: bug_id, priority_id, priority_name
  - Use case: Track which priorities are affected by bugs

### Intelligent Delegation (3 commands)

- **classify-request** - Determine request type and complexity
  - Input: REQUEST_TEXT, CONTEXT (optional), REQUEST_HISTORY (optional)
  - Output: request_type, complexity, confidence, required_expertise
  - Use case: LLM-based classification of user requests

- **route-to-agent** - Select appropriate agent for task
  - Input: REQUEST_TYPE, REQUEST_TEXT, PRIORITY (optional)
  - Output: session_id, target_agent, fallback_agent, routing_confidence
  - Use case: Intelligent agent selection based on request type

- **monitor-delegation** - Track delegation outcomes and patterns
  - Input: SESSION_ID, OUTCOME (success|failed|timeout), NOTES, COMPLETION_TIME
  - Output: outcome, agent_success_rate, completion_time
  - Use case: Monitor and optimize agent performance

### Documentation (2 commands)

- **generate-docs** - Auto-generate documentation from code/specs
  - Input: SOURCE (spec|code|both), TARGET_PATH, SPEC_ID (optional)
  - Output: generated_doc_path, word_count, sections, cross_references
  - Use case: Create markdown documentation from technical specs

- **update-readme** - Keep README files synchronized with features
  - Input: README_PATH, SECTION (optional), INCLUDE_PRIORITIES, INCLUDE_LINKS
  - Output: readme_path, sections_updated, features_added, links_updated
  - Use case: Auto-update README with completed priorities

## Implementation

Located in: `coffee_maker/commands/assistant_commands.py`

### Usage Example

```python
from coffee_maker.commands.assistant_commands import AssistantCommands

assistant = AssistantCommands()

# Create demo
demo = assistant.create_demo(
    feature_name="Roadmap Visualization",
    demo_type="interactive"
)

# Record steps
steps = [
    {"action": "navigate", "url": "http://localhost:8501/roadmap"},
    {"action": "screenshot", "screenshot_name": "main"},
    {"action": "click", "selector": ".priority-item:first"},
]
result = assistant.record_demo_session(demo["session_id"], steps)

# Report bug found
bug = assistant.report_bug(
    title="Layout broken on mobile",
    description="Sidebar overlaps content",
    severity="high",
    priority_id="PRIORITY-28"
)

# Track progress
assistant.track_bug_status(
    bug_id=bug["bug_id"],
    status="resolved",
    resolution_notes="Fixed with CSS media query"
)
```

## Database Tables

- `ui_demo_sessions` - Demo recording metadata and status
- `ui_bug_reports` - Bug tracking with severity and resolution
- `ui_delegation_log` - Delegation decisions and outcomes

## Testing

Run tests with:
```bash
pytest tests/unit/test_spec114_commands.py::TestAssistantCommands -v
```

Test coverage includes:
- Demo creation (interactive, video, screenshot_series)
- Demo recording with screenshots
- Demo output validation
- Bug reporting with severity levels
- Bug status tracking and transitions
- Priority linking
- Request classification and routing
- Delegation outcome monitoring
- Documentation generation
- README updates

## Performance

- Demo creation: <100ms
- Bug reporting: <50ms
- Bug status tracking: <50ms
- Request classification: <1s (LLM call)
- Delegation routing: <100ms

## Error Handling

All commands return:
```json
{
  "success": true/false,
  "error": "error message if failed",
  "...": "command-specific results"
}
```

Common errors:
- Invalid enum values (demo_type, severity, status)
- Missing required parameters
- Database record not found
- Timestamp and ID generation issues
