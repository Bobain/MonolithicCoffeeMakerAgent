# demo

## Purpose
Create visual demos using Puppeteer MCP: record browser sessions, capture screenshots, generate GIFs, validate feature functionality.

## Parameters
```yaml
feature: str  # Required, feature name to demo
url: str  # Required, starting URL
steps: List[dict]  # Required, demo steps [{action, selector, value}]
output_format: str = "gif"  # "gif" | "video" | "screenshots"
output_path: str = "demos/{feature}.gif"  # Save location
validate_output: bool = true  # Check demo completed successfully
```

## Workflow
1. Initialize Puppeteer browser session
2. Navigate to starting URL
3. Execute demo steps:
   - **click**: Click element
   - **fill**: Fill input field
   - **screenshot**: Capture screen
   - **wait**: Wait for element/timeout
   - **hover**: Hover element
4. Capture output (GIF/video/screenshots)
5. Validate demo completed successfully
6. Save to output_path
7. Return DemoResult

## Puppeteer MCP Integration
```python
# Available Puppeteer actions
puppeteer_navigate(url)
puppeteer_screenshot(name, selector=None)
puppeteer_click(selector)
puppeteer_fill(selector, value)
puppeteer_hover(selector)
puppeteer_evaluate(script)
```

## Database Operations
```sql
-- Track demo creation
INSERT INTO demo_tracker (
    demo_id, feature_name, demo_path, created_at,
    steps_count, validation_passed, metadata
) VALUES (?, ?, ?, datetime('now'), ?, ?, ?)

-- Link to priority
UPDATE demo_tracker
SET related_priority_id = ?, related_spec_id = ?
WHERE demo_id = ?
```

## Result Object
```python
@dataclass
class DemoResult:
    demo_id: str
    feature: str
    output_path: str
    steps_executed: int
    validation_passed: bool
    duration_seconds: float
    status: str  # "success" | "failed"
```

## Demo Steps Format
```yaml
steps:
  - action: navigate
    url: "http://localhost:3000"
  - action: fill
    selector: "#username"
    value: "testuser"
  - action: click
    selector: "button[type=submit]"
  - action: wait
    selector: ".dashboard"
  - action: screenshot
    name: "dashboard-view"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| NavigationFailed | URL unreachable | Check server running |
| SelectorNotFound | Element missing | Review selector |
| ValidationFailed | Expected state not reached | Check demo steps |
| PuppeteerError | Browser crashed | Restart Puppeteer |

## Example
```python
result = demo(
    feature="user-login",
    url="http://localhost:3000/login",
    steps=[
        {"action": "fill", "selector": "#email", "value": "user@example.com"},
        {"action": "fill", "selector": "#password", "value": "password123"},
        {"action": "click", "selector": "button[type=submit]"},
        {"action": "wait", "selector": ".dashboard"}
    ]
)
# DemoResult(
#   demo_id="demo-001",
#   feature="user-login",
#   output_path="demos/user-login.gif",
#   steps_executed=4,
#   validation_passed=True,
#   duration_seconds=3.2,
#   status="success"
# )
```

## Related Commands
- docs() - Documentation generation
- bug() - Report bugs found during demos

---
Estimated: 65 lines | Context: ~4% | Examples: demo_examples.md
