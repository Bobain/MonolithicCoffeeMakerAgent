# delegate

## Purpose
Intelligent request routing: analyze requests, determine best agent, create delegation records, track delegation outcomes.

## Parameters
```yaml
request: str  # Required, user request or task
context: dict = None  # Additional context {priority_id, spec_id}
preferred_agent: str = None  # Override auto-detection
create_notification: bool = true  # Notify target agent
track_outcome: bool = true  # Monitor delegation result
```

## Workflow
1. Parse request and extract intent
2. Analyze request complexity and type
3. Determine target agent:
   - Architectural → architect
   - Implementation → code_developer
   - Project management → project_manager
   - Code quality → code_reviewer
   - Coordination → orchestrator
   - UI/UX → ux_design_expert
4. Create delegation record
5. Notify target agent
6. Return DelegateResult

## Agent Selection Matrix
| Request Type | Keywords | Target Agent |
|-------------|----------|--------------|
| Design | "spec", "architecture", "design", "POC" | architect |
| Implement | "implement", "code", "build", "create" | code_developer |
| Review | "review", "quality", "security", "analyze" | code_reviewer |
| Coordinate | "assign", "parallelize", "orchestrate" | orchestrator |
| Track | "status", "roadmap", "progress", "report" | project_manager |
| Design UI | "component", "design system", "UI" | ux_design_expert |

## Database Operations
```sql
-- Create delegation record
INSERT INTO delegation_tracker (
    delegation_id, request, target_agent, delegated_by,
    context, created_at, status
) VALUES (?, ?, ?, 'assistant', ?, datetime('now'), 'pending')

-- Notify agent
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message,
    metadata, created_at, status
) VALUES (?, ?, 'medium', ?, ?, datetime('now'), 'pending')

-- Track outcome
UPDATE delegation_tracker
SET status = ?, completed_at = datetime('now'), outcome = ?
WHERE delegation_id = ?
```

## Result Object
```python
@dataclass
class DelegateResult:
    delegation_id: str
    request: str
    target_agent: str
    confidence: float  # 0.0-1.0 (routing confidence)
    notification_sent: bool
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| AmbiguousRequest | Can't determine agent | Ask for clarification |
| AgentOffline | Target agent unavailable | Queue or suggest alternative |
| NotificationFailed | Agent unreachable | Retry with backoff |
| InvalidContext | Malformed context data | Use request only |

## Example
```python
result = delegate(
    request="Create technical spec for OAuth2 authentication system",
    context={"priority_id": "PRIORITY-8"},
    create_notification=True
)
# DelegateResult(
#   delegation_id="del-001",
#   request="Create technical spec for OAuth2 authentication system",
#   target_agent="architect",
#   confidence=0.95,
#   notification_sent=True,
#   status="success"
# )
```

## Related Commands
- All agent commands (delegation targets)
- interact() (user_listener) - Primary delegation source

---
Estimated: 60 lines | Context: ~4% | Examples: delegate_examples.md
