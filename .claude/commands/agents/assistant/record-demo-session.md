---
command: record-demo-session
agent: assistant
action: record_demo_steps
tables: [ui_demo_sessions]
tools: [puppeteer_mcp, file_system]
duration: 30m
---

## Purpose

Execute and record demo steps with screenshots and metadata tracking for interactive or video-based demos.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Demo session identifier from create-demo
  example: "DEMO-20251027-abc123"

STEPS:
  type: array
  description: Array of demo steps to execute
  items:
    type: object
    properties:
      step_number: integer
      description: string
      action: string (navigate|click|fill|screenshot)
      selector: string (for click/fill)
      value: string (for fill)
      url: string (for navigate)
      screenshot_name: string

VERIFY_CRITERIA:
  type: array
  optional: true
  description: Assertions to verify after each step
  items:
    type: object
    properties:
      selector: string
      assertion_type: string (exists|visible|has_text|has_value)
      expected_value: string
```

## Database Operations

### UPDATE ui_demo_sessions

```sql
UPDATE ui_demo_sessions
SET metadata = json_object(
    'steps', json_array(...),
    'screenshots', json_array(...),
    'verification_results', json_array(...)
)
WHERE session_id = ?
```

## External Tools

### Puppeteer MCP Integration

```javascript
// Execute each step
for (const step of STEPS) {
  if (step.action == "navigate") {
    puppeteer_navigate(url=step.url)
  } else if (step.action == "click") {
    puppeteer_click(selector=step.selector)
  } else if (step.action == "fill") {
    puppeteer_fill(selector=step.selector, value=step.value)
  } else if (step.action == "screenshot") {
    puppeteer_screenshot(name=step.screenshot_name)
  }

  // Verify step completion
  for (const criteria of VERIFY_CRITERIA) {
    puppeteer_evaluate(script=generate_assertion(criteria))
  }
}
```

## Success Criteria

- All steps executed without errors
- Screenshots captured at designated points
- Verification criteria passed for all steps
- Metadata updated with step results
- Output files saved to demo directory

## Output Format

```json
{
  "success": true,
  "session_id": "DEMO-20251027-abc123",
  "total_steps": 5,
  "executed_steps": 5,
  "failed_steps": 0,
  "screenshots_captured": [
    "demos/DEMO-20251027-abc123/screenshots/step-1.png",
    "demos/DEMO-20251027-abc123/screenshots/step-2.png"
  ],
  "verification_results": [
    {"step": 1, "assertion": "exists", "selector": "#roadmap-button", "passed": true},
    {"step": 2, "assertion": "has_text", "selector": ".title", "expected": "Roadmap", "passed": true}
  ],
  "duration_seconds": 42,
  "message": "Demo recording completed successfully"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | Return 404, suggest valid IDs |
| Step execution failed | Element not found or action failed | Log failure, continue if not critical |
| Screenshot failed | Puppeteer error | Retry up to 3 times |
| Verification failed | Assertion failed | Log failure, update status to partial |
| Demo already completed | Session status != recording | Return error, suggest validation |

## Examples

### Example 1: Record Roadmap Demo

```bash
/agents:assistant:record-demo-session \
  SESSION_ID="DEMO-20251027-abc123" \
  STEPS='[
    {
      "step_number": 1,
      "description": "Navigate to roadmap page",
      "action": "navigate",
      "url": "http://localhost:8501/roadmap"
    },
    {
      "step_number": 2,
      "description": "Take screenshot of main view",
      "action": "screenshot",
      "screenshot_name": "roadmap-main"
    },
    {
      "step_number": 3,
      "description": "Click on priority item",
      "action": "click",
      "selector": ".priority-item:first-child"
    },
    {
      "step_number": 4,
      "description": "Verify modal opened",
      "action": "screenshot",
      "screenshot_name": "priority-detail"
    }
  ]'
```

### Example 2: Record Form Demo

```bash
/agents:assistant:record-demo-session \
  SESSION_ID="DEMO-20251027-def456" \
  STEPS='[
    {"step_number": 1, "action": "navigate", "url": "http://localhost:8501/login"},
    {"step_number": 2, "action": "fill", "selector": "#username", "value": "demo@example.com"},
    {"step_number": 3, "action": "fill", "selector": "#password", "value": "password123"},
    {"step_number": 4, "action": "click", "selector": ".login-button"},
    {"step_number": 5, "action": "screenshot", "screenshot_name": "after-login"}
  ]' \
  VERIFY_CRITERIA='[
    {"selector": ".welcome-message", "assertion_type": "exists"},
    {"selector": ".user-profile", "assertion_type": "visible"}
  ]'
```

## Implementation Notes

- Steps executed sequentially in order
- Each screenshot automatically timestamped
- Verification failures logged but non-blocking (unless critical)
- Demo directory must exist (created by create-demo)
- Screenshots saved as PNG in `demos/{session_id}/screenshots/`
- Metadata stored as JSON for later validation
- Maximum 60 steps per demo session
- Timeout per step: 30 seconds
- Puppeteer MCP session reused from create-demo
