---
command: user-listener-workflow
workflow: interact
agent: user_listener
purpose: Complete user interaction workflow
tables: [user_session, conversation_log, intent_classification]
tools: [notification, sound]
duration: 1-5s
---

## Purpose

Execute complete user interaction workflow: classify intent → determine target agent → route request → provide response. This is the PRIMARY workflow command for the user_listener agent - the ONLY agent with direct user interface (CFR-009).

## Workflow Overview

```
interact(input) → Classify → Determine Agent → Route → Respond → InteractResult
```

**Key Features**:
- **Intent classification**: NLP-based user intent detection
- **Smart routing**: Automatically routes to appropriate agent
- **Context tracking**: Maintains conversation context
- **Sound notifications**: User-facing notifications (CFR-009 compliant)
- **Session management**: Tracks user sessions

## Input Parameters

```yaml
INPUT:
  type: string
  required: true
  description: User's natural language input
  example: "Show me the current roadmap status"

CONTEXT:
  type: dict
  optional: true
  description: Conversation context from previous interactions
  example: {"priority_id": "PRIORITY-5", "last_action": "query"}

SUGGESTED_AGENT:
  type: string
  optional: true
  description: Hint for which agent should handle request
  example: "project_manager"
```

## Workflow Execution

### Complete Workflow

```python
1. Parse user input
2. Classify intent (query, command, request)
3. Extract entities (priority IDs, task IDs, etc.)
4. Determine target agent
5. Update conversation context
6. Route request to target agent
7. Format response for user
8. Send notification with sound=True (CFR-009)
9. Return InteractResult
```

## Result Object

```python
@dataclass
class InteractResult:
    user_input: str
    response: str  # Formatted response for user
    intent: str  # query | command | request
    target_agent: str  # Which agent handled request
    duration_seconds: float
    metadata: Dict[str, Any]
```

## Intent Classification

### Intent Types

| Intent | Description | Example | Target Agent |
|--------|-------------|---------|--------------|
| query_status | Status inquiry | "What's the status of PRIORITY-5?" | project_manager |
| request_feature | Feature request | "Add OAuth support" | architect |
| command_agent | Direct agent command | "Run tests" | code_developer |
| request_help | Help/documentation | "How do I use this?" | assistant |
| report_bug | Bug report | "I found an issue" | assistant |
| design_request | UI/UX question | "Make this button look better" | ux-design-expert |

### Entity Extraction

```python
# Extract priority IDs
priority_ids = extract_pattern(input, r"PRIORITY-\d+")

# Extract task IDs
task_ids = extract_pattern(input, r"TASK-\d+-\d+")

# Extract spec IDs
spec_ids = extract_pattern(input, r"SPEC-\d+")

# Extract file paths
file_paths = extract_pattern(input, r"[\w/]+\.py")
```

## Agent Routing

### Routing Rules

```python
def determine_agent(intent, entities, context):
    if intent == "query_status":
        return "project_manager"

    if intent == "request_feature":
        return "architect"

    if intent == "command_agent":
        if "test" in input:
            return "code_developer"
        if "review" in input:
            return "code_reviewer"

    if intent == "request_help":
        return "assistant"

    if intent == "design_request":
        return "ux-design-expert"

    # Default
    return "assistant"  # Intelligent dispatcher
```

## Database Operations

### Insert: User Session

```sql
INSERT INTO user_session (
    session_id, user_id, started_at, last_interaction, context
) VALUES (?, ?, datetime('now'), datetime('now'), ?)
```

### Insert: Conversation Log

```sql
INSERT INTO conversation_log (
    log_id, session_id, user_input, intent, target_agent,
    response, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Intent Classification

```sql
INSERT INTO intent_classification (
    classification_id, user_input, intent, confidence,
    entities_extracted, created_at
) VALUES (?, ?, ?, ?, ?, datetime('now'))
```

## Examples

### Example 1: Status Query

```python
result = workflow.interact(
    input="What's the status of PRIORITY-5?"
)
```

**Result**:
```python
InteractResult(
    user_input="What's the status of PRIORITY-5?",
    response="PRIORITY-5 is IN_PROGRESS with 50% completion. 3/6 tasks done.",
    intent="query_status",
    target_agent="project_manager",
    duration_seconds=0.8,
    metadata={
        "entities": {"priority_id": "PRIORITY-5"},
        "confidence": 0.95
    }
)
```

### Example 2: Feature Request

```python
result = workflow.interact(
    input="Can we add OAuth2 authentication support?"
)
```

**Result**:
```python
InteractResult(
    user_input="Can we add OAuth2 authentication support?",
    response="Feature request created as PRIORITY-8. Architect will create technical spec.",
    intent="request_feature",
    target_agent="architect",
    duration_seconds=1.2,
    metadata={
        "priority_created": "PRIORITY-8",
        "notified_agents": ["architect", "project_manager"]
    }
)
```

### Example 3: Command Request

```python
result = workflow.interact(
    input="Run tests for TASK-42"
)
```

**Result**:
```python
InteractResult(
    user_input="Run tests for TASK-42",
    response="Tests running... 15 passed, 0 failed (2.3s)",
    intent="command_agent",
    target_agent="code_developer",
    duration_seconds=3.5,
    metadata={
        "entities": {"task_id": "TASK-42"},
        "test_results": {"passed": 15, "failed": 0}
    }
)
```

### Example 4: Help Request

```python
result = workflow.interact(
    input="How do I create a new priority?"
)
```

**Result**:
```python
InteractResult(
    user_input="How do I create a new priority?",
    response="""To create a new priority:
1. Update docs/roadmap/ROADMAP.md
2. Run: poetry run project-manager parse-roadmap
3. Verify: poetry run project-manager /roadmap

Or use CLI: project_manager.manage(action='plan', updates={...})
""",
    intent="request_help",
    target_agent="assistant",
    duration_seconds=0.5,
    metadata={
        "documentation_links": ["docs/WORKFLOWS.md", "docs/roadmap/ROADMAP.md"]
    }
)
```

## Notification Handling (CFR-009)

### Sound Notifications

```python
# User Listener is ONLY agent with sound=True
notify(
    message=response,
    level="info",
    sound=True  # ← CFR-009: Only user_listener uses sound=True
)

# All other agents MUST use sound=False
```

### Notification Levels

```python
if intent == "error":
    level = "error"  # Red, urgent sound
elif intent == "warning":
    level = "warning"  # Yellow, attention sound
else:
    level = "info"  # Blue, soft sound
```

## Context Management

### Session Context

```python
context = {
    "session_id": "SESSION-20251028-abc123",
    "priority_id": "PRIORITY-5",  # Last referenced priority
    "task_id": "TASK-5-2",  # Last referenced task
    "agent_stack": ["project_manager", "architect"],  # Agent history
    "conversation_turns": 5
}
```

### Context Carryover

```python
# User: "What's the status of PRIORITY-5?"
# → context["priority_id"] = "PRIORITY-5"

# User: "What tasks are left?"  # ← Implicit reference
# → Uses context["priority_id"] = "PRIORITY-5"
```

## Performance Expectations

| Input Type | Duration | Agent Routing | Entities Extracted |
|------------|----------|---------------|-------------------|
| Simple query | <1s | Direct | 0-1 |
| Complex query | 1-2s | Direct | 2-5 |
| Feature request | 1-3s | Architect | 1-3 |
| Command | 2-5s | Variable | 1-4 |

## Best Practices

1. **Keep responses concise** - User is waiting for response
2. **Use context effectively** - Track conversation state
3. **Route to specialist agents** - Don't try to do everything
4. **Format responses clearly** - Use markdown for readability
5. **Provide actionable next steps** - Help user know what to do
6. **Use sound=True appropriately** - CFR-009 compliance
7. **Log all interactions** - For debugging and improvement

## Related Commands

- `assistant.assist()` - Handle help requests
- `project_manager.manage()` - Handle status queries
- `architect.spec()` - Handle feature requests
- `developer.work()` - Handle command requests

---

**Workflow Reduction**: This single `interact()` command replaces:
1. `classify_intent()`
2. `extract_entities()`
3. `determine_agent()`
4. `route_request()`
5. `format_response()`

**Context Savings**: ~150 lines vs ~900 lines (5 commands)
