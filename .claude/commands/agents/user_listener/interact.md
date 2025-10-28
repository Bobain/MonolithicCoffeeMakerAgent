# interact

## Purpose
PRIMARY USER INTERFACE - Handle user interaction, classify intent, delegate to specialized agents, manage conversation context (CFR-009: sound=True).

## Parameters
```yaml
user_input: str  # Required, user's message
context: dict = None  # Conversation context {history, current_task}
sound: bool = true  # ALWAYS true for user_listener (CFR-009)
delegate_threshold: float = 0.7  # Confidence needed to delegate
```

## Workflow
1. Parse user input and extract intent
2. Load conversation context
3. Classify intent (question, command, request)
4. Determine if delegation needed:
   - Architectural design → architect
   - Implementation → code_developer
   - Project status → project_manager
   - Documentation → assistant
   - UI/UX design → ux_design_expert
   - Simple questions → answer directly
5. Delegate or respond
6. Update conversation context
7. Return InteractResult

## Intent Classification
```yaml
Categories:
  - architectural_design: "design X", "create spec", "POC needed"
  - implementation: "implement Y", "fix bug", "write code"
  - project_management: "status?", "roadmap", "what's blocked?"
  - documentation: "explain X", "document Y", "create demo"
  - ux_design: "improve UI", "design system", "component library"
  - simple_question: "what is X?", "how does Y work?"
  - system_command: "/commit", "/test", "/roadmap"
```

## Database Operations
```sql
-- Track user interaction
INSERT INTO user_interaction (
    interaction_id, user_input, intent, confidence,
    delegated_to, response, timestamp
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))

-- Update conversation context
INSERT INTO conversation_context (
    session_id, turn_number, user_input, agent_response,
    context_data, timestamp
) VALUES (?, ?, ?, ?, ?, datetime('now'))

-- Create delegation notification
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message,
    metadata, created_at, status
) VALUES (?, ?, 'high', ?, ?, datetime('now'), 'pending')
```

## Result Object
```python
@dataclass
class InteractResult:
    intent: str
    confidence: float  # 0.0-1.0
    delegated_to: str  # None if answered directly
    response: str
    context_updated: bool
    status: str  # "success" | "failed"
```

## Delegation Decision Matrix
| Intent | Confidence | Action |
|--------|-----------|--------|
| architectural_design | ≥0.7 | Delegate to architect |
| implementation | ≥0.7 | Delegate to code_developer |
| project_management | ≥0.7 | Delegate to project_manager |
| documentation | ≥0.7 | Delegate to assistant |
| ux_design | ≥0.7 | Delegate to ux_design_expert |
| simple_question | Any | Answer directly |
| unclear | <0.7 | Ask clarifying question |

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| IntentUnclear | Ambiguous input | Ask clarifying question |
| DelegationFailed | Target agent offline | Queue for later or handle directly |
| ContextLoadFailed | Session expired | Start new context |
| DatabaseError | Tracking failed | Log warning, continue |

## Example
```python
result = interact(
    user_input="Create a spec for OAuth2 authentication",
    context={"history": [...], "current_task": None}
)
# InteractResult(
#   intent="architectural_design",
#   confidence=0.92,
#   delegated_to="architect",
#   response="I'll delegate this to the architect agent to create a comprehensive spec.",
#   context_updated=True,
#   status="success"
# )
```

## CFR-009 Compliance
- **sound=True**: ONLY user_listener uses sound notifications
- **All other agents**: MUST use sound=False
- **Reason**: Prevent notification spam from background agents

## Related Commands
- All other agent commands (delegation targets)

---
Estimated: 75 lines | Context: ~4.7% | Examples: interact_examples.md
