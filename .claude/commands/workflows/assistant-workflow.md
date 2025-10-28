---
command: assistant-workflow
workflow: assist
agent: assistant
purpose: Help, documentation, and delegation workflow
tables: [ui_demo_sessions, bug_report, documentation]
tools: [puppeteer_mcp, file_system]
duration: 2-20m
---

## Purpose

Execute complete assistance workflow: classify request → generate docs/demo/bug report → delegate to specialist. This is the PRIMARY workflow command for the assistant agent - the intelligent dispatcher and documentation expert.

## Workflow Overview

```
assist(request) → Classify → AUTO Route → DOCS | DEMO | BUG | DELEGATE → AssistResult
```

**Key Features**:
- **Auto-routing**: Automatically determines request type
- **4 request types**: DOCS (generate docs), DEMO (create demo), BUG (track bug), DELEGATE (route to agent)
- **Puppeteer integration**: Creates interactive demos
- **Documentation generation**: Auto-generates component docs
- **Bug tracking**: Links bugs to priorities

## Input Parameters

```yaml
REQUEST:
  type: string
  required: true
  description: User's assistance request
  example: "Create demo for authentication system"

TYPE:
  type: string
  default: "auto"
  enum: [auto, docs, demo, bug, delegate]
  description: |
    - auto: Automatically classify and route
    - docs: Generate documentation
    - demo: Create interactive demo
    - bug: Track bug report
    - delegate: Route to specialist agent
```

## Workflow Execution

### AUTO Type (Default)

Automatically classify and route:

```python
1. Classify request intent
2. Extract entities (component names, features, etc.)
3. Determine request type (docs, demo, bug, delegate)
4. Route to appropriate handler
5. Return AssistResult
```

### DOCS Type

Generate documentation:

```python
1. Parse component/feature name
2. Analyze codebase
3. Generate markdown documentation
4. Save to docs/ directory
5. Return documentation path
```

### DEMO Type

Create interactive demo:

```python
1. Initialize Puppeteer MCP session
2. Navigate to feature
3. Record interaction steps
4. Capture screenshots
5. Generate demo report
6. Return demo session ID
```

### BUG Type

Track bug report:

```python
1. Parse bug description
2. Link to priority if applicable
3. Create bug record in database
4. Notify project_manager
5. Return bug tracking ID
```

### DELEGATE Type

Route to specialist agent:

```python
1. Classify request intent
2. Determine target agent
3. Format request for agent
4. Forward to agent
5. Return delegation result
```

## Result Object

```python
@dataclass
class AssistResult:
    request: str
    status: str  # success | partial | failed
    result_data: Any  # Type-specific result
    duration_seconds: float
    metadata: Dict[str, Any]
```

## Database Operations

### Insert: Demo Session

```sql
INSERT INTO ui_demo_sessions (
    session_id, feature_name, demo_type,
    created_by, status, metadata, created_at
) VALUES (?, ?, ?, 'assistant', 'recording', ?, datetime('now'))
```

### Insert: Bug Report

```sql
INSERT INTO bug_report (
    bug_id, title, description, priority_id,
    reported_by, status, created_at
) VALUES (?, ?, ?, ?, 'assistant', 'open', datetime('now'))
```

### Insert: Documentation

```sql
INSERT INTO documentation (
    doc_id, component, file_path, created_by,
    created_at, status
) VALUES (?, ?, ?, 'assistant', datetime('now'), 'active')
```

## Examples

### Example 1: Auto-Route Documentation

```python
result = workflow.assist(
    request="Generate docs for the authentication module"
)
```

**Result**:
```python
AssistResult(
    request="Generate docs for the authentication module",
    status="success",
    result_data={
        "doc_id": "DOC-042",
        "file_path": "docs/components/authentication.md",
        "sections": ["Overview", "API", "Examples", "Testing"]
    },
    duration_seconds=8.5,
    metadata={"type": "docs", "auto_routed": True}
)
```

### Example 2: Create Demo

```python
result = workflow.assist(
    request="Create demo for OAuth login flow",
    type="demo"
)
```

**Result**:
```python
AssistResult(
    request="Create demo for OAuth login flow",
    status="success",
    result_data={
        "session_id": "DEMO-20251028-abc123",
        "feature_name": "OAuth Login",
        "demo_type": "interactive",
        "screenshots": 8,
        "duration": 45.2
    },
    duration_seconds=120.0,
    metadata={
        "puppeteer_session": "pup-xyz789",
        "output_path": "demos/DEMO-20251028-abc123/"
    }
)
```

### Example 3: Track Bug

```python
result = workflow.assist(
    request="Login form validation fails for emails with + symbol",
    type="bug"
)
```

**Result**:
```python
AssistResult(
    request="Login form validation fails for emails with + symbol",
    status="success",
    result_data={
        "bug_id": "BUG-089",
        "priority_id": "PRIORITY-5",  # Auto-linked
        "severity": "medium",
        "status": "open"
    },
    duration_seconds=3.2,
    metadata={
        "notified": ["project_manager", "architect"],
        "linked_to_priority": True
    }
)
```

### Example 4: Delegate Request

```python
result = workflow.assist(
    request="What's the status of PRIORITY-5?",
    type="delegate"
)
```

**Result**:
```python
AssistResult(
    request="What's the status of PRIORITY-5?",
    status="success",
    result_data={
        "target_agent": "project_manager",
        "response": "PRIORITY-5 is IN_PROGRESS with 50% completion"
    },
    duration_seconds=1.5,
    metadata={"delegation_successful": True}
)
```

## Request Classification

### Classification Logic

```python
def classify_request(request):
    # Documentation keywords
    if any(kw in request.lower() for kw in ["docs", "document", "explain"]):
        return "docs"

    # Demo keywords
    if any(kw in request.lower() for kw in ["demo", "show", "walkthrough"]):
        return "demo"

    # Bug keywords
    if any(kw in request.lower() for kw in ["bug", "issue", "problem", "fails"]):
        return "bug"

    # Status query keywords
    if any(kw in request.lower() for kw in ["status", "progress", "what's"]):
        return "delegate"

    # Default to delegate
    return "delegate"
```

## Puppeteer Integration

### Demo Creation Workflow

```python
1. Initialize Puppeteer MCP
   puppeteer_navigate(url="http://localhost:8501")

2. Capture initial state
   puppeteer_screenshot(name="step-1-initial")

3. Interact with feature
   puppeteer_click(selector="#login-button")
   puppeteer_fill(selector="#email", value="test@example.com")

4. Capture each step
   puppeteer_screenshot(name="step-2-login")

5. Generate demo report
   create_demo_report(screenshots, steps)
```

## Documentation Generation

### Auto-Documentation Format

```markdown
# Component: Authentication

**Module**: `coffee_maker.auth`
**Status**: Active
**Coverage**: 95%

## Overview
[Auto-generated description from docstrings]

## API Reference

### `authenticate(user, password)`
[Function signature and description]

### `validate_token(token)`
[Function signature and description]

## Examples

```python
# Example 1: Basic authentication
result = authenticate(user="test@example.com", password="secure123")
```

## Testing
[Auto-generated test examples]
```

## Performance Expectations

| Type | Duration | External Tools | Output |
|------|----------|----------------|--------|
| docs | 5-15m | File system | Markdown file |
| demo | 10-30m | Puppeteer MCP | Screenshots + report |
| bug | 2-5m | Database | Bug record |
| delegate | 1-3m | Agent routing | Agent response |

## Best Practices

1. **Use auto type** for most requests (90% accuracy)
2. **Explicit type** when auto-classification might fail
3. **Link bugs to priorities** for better tracking
4. **Generate docs** for all new components
5. **Create demos** for user-facing features
6. **Delegate complex queries** to specialist agents

## Related Commands

- `user_listener.interact()` - Routes help requests to assistant
- `project_manager.manage()` - Handles status queries after delegation
- `architect.spec()` - Creates specs referenced in docs

---

**Workflow Reduction**: This single `assist()` command replaces:
1. `classify_request()`
2. `generate_docs()`
3. `create_demo()`
4. `track_bug()`
5. `delegate_to_agent()`

**Context Savings**: ~150 lines vs ~1,000 lines (5 commands)
