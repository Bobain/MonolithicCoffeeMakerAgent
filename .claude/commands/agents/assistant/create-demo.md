---
command: create-demo
agent: assistant
action: create_demo_session
tables: [ui_demo_sessions]
tools: [puppeteer_mcp, file_system]
duration: 15m
---

## Purpose

Create new demo session for feature demonstration with recording metadata and Puppeteer MCP initialization.

## Input Parameters

```yaml
FEATURE_NAME:
  type: string
  description: Name of the feature being demonstrated
  example: "Roadmap Visualization"

DEMO_TYPE:
  type: string
  enum: [interactive, video, screenshot_series]
  description: Type of demo to create

DESCRIPTION:
  type: string
  optional: true
  description: Detailed description of what the demo showcases
```

## Database Operations

### INSERT ui_demo_sessions

```sql
INSERT INTO ui_demo_sessions (
    session_id, feature_name, created_by, created_at, status, metadata
) VALUES (?, ?, ?, datetime('now'), 'recording', ?)
```

**Fields**:
- `session_id` - Generated UUID (DEMO-{timestamp}-{random})
- `feature_name` - From FEATURE_NAME parameter
- `created_by` - 'assistant'
- `status` - 'recording' (will update to completed/failed)
- `metadata` - JSON object with demo configuration

## External Tools

### Puppeteer MCP (if interactive demo)

```javascript
// Initialize Puppeteer session for interactive demo
if DEMO_TYPE == "interactive":
  puppeteer_navigate(url="http://localhost:8501")
  session_id = capture_session_id()
  UPDATE ui_demo_sessions SET puppeteer_session_id = ?
```

## Success Criteria

- Session ID generated and returned
- Database record created with valid status
- Output directory created at `demos/{session_id}/`
- Puppeteer MCP session initialized (if interactive)
- Metadata structure valid JSON

## Output Format

```json
{
  "success": true,
  "session_id": "DEMO-20251027-abc123",
  "feature_name": "Roadmap Visualization",
  "demo_type": "interactive",
  "created_at": "2025-10-27T10:30:00Z",
  "output_path": "demos/DEMO-20251027-abc123",
  "puppeteer_session_id": "pup-xyz789",
  "status": "recording",
  "message": "Demo session created and ready for recording"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session creation failed | Database insert error | Retry with new session ID |
| Invalid demo type | DEMO_TYPE not in enum | Reject and list valid types |
| Output directory exists | Previous demo with same ID | Generate new session ID |
| Puppeteer init failed | MCP connection error | Log warning, continue without MCP |

## Examples

### Example 1: Interactive Demo

```bash
/agents:assistant:create-demo \
  FEATURE_NAME="Roadmap Visualization" \
  DEMO_TYPE="interactive" \
  DESCRIPTION="Interactive walkthrough of new roadmap UI"
```

**Response**:
```json
{
  "success": true,
  "session_id": "DEMO-20251027-abc123",
  "demo_type": "interactive",
  "puppeteer_session_id": "pup-xyz789"
}
```

### Example 2: Video Demo

```bash
/agents:assistant:create-demo \
  FEATURE_NAME="User Authentication" \
  DEMO_TYPE="video"
```

**Response**:
```json
{
  "success": true,
  "session_id": "DEMO-20251027-def456",
  "demo_type": "video",
  "output_path": "demos/DEMO-20251027-def456"
}
```

## Implementation Notes

- Session IDs use format: `DEMO-{YYYYMMDD-HHMM}-{6-char-random}`
- Metadata JSON includes:
  - `demo_type` - Type of demo
  - `description` - Demo description
  - `steps` - Array of steps (initially empty)
  - `screenshots` - Array of screenshot paths (initially empty)
  - `video_path` - Video file path (if applicable)
- Output directory structure:
  ```
  demos/{session_id}/
  ├── metadata.json
  ├── screenshots/
  │   ├── step-1.png
  │   ├── step-2.png
  │   └── ...
  └── video.mp4 (if video demo)
  ```
- Puppeteer MCP integration: Store session ID for later use in `record-demo-session` command
- Database connection via DomainWrapper (coffee_maker.autonomous.domain.DomainWrapper)
