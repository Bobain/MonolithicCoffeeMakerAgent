# user_interpret Proactive Intelligence System

**Owner**: user_interpret agent
**Status**: Active
**Version**: 1.0

## Overview

The **user_interpret Proactive Intelligence System** enables the user_interpret agent to be context-aware and proactive in conversations. Instead of just reacting to user messages, it can:

- **Track conversation history** for pattern learning
- **Monitor pending requests** (features, bugs, docs)
- **Provide proactive updates** when work is completed
- **Suggest helpful tips** based on context

## Architecture

```
docs/user_interpret/          # Document ownership (user_interpret owns)
├── conversation_history.jsonl  # All conversations (JSONL format)
├── conversation_summaries.json # Summaries by date/topic
├── user_requests.json          # Pending/completed requests
└── README.md                   # This file

coffee_maker/cli/user_interpret/
├── __init__.py
├── conversation_logger.py      # Logs all conversations
├── request_tracker.py          # Tracks feature/bug/doc requests
└── proactive_suggestions.py    # Generates proactive messages
```

## Components

### 1. ConversationLogger

**Purpose**: Log and retrieve conversation history

**File**: `coffee_maker/cli/user_interpret/conversation_logger.py`

**Features**:
- Logs every conversation with timestamp, intent, agent, sentiment
- Stores in JSONL format for easy streaming/analysis
- Retrieves recent conversations
- Filters by intent
- Generates activity summaries

**Example**:
```python
from coffee_maker.cli.user_interpret import ConversationLogger

logger = ConversationLogger()

# Log conversation
entry = logger.log_conversation(
    user_message="add a login feature",
    intent="add_feature",
    delegated_to="code_developer",
    sentiment_signals=[],
    confidence=0.9
)

# Get recent conversations
recent = logger.get_recent_conversations(limit=10)

# Get summary
summary = logger.summarize_recent_activity(days=7)
print(f"Total conversations: {summary['total_conversations']}")
print(f"Average confidence: {summary['avg_confidence']}")
```

### 2. RequestTracker

**Purpose**: Track pending user requests and their completion status

**File**: `coffee_maker/cli/user_interpret/request_tracker.py`

**Features**:
- Tracks feature requests, bug reports, documentation requests
- Maintains status (pending, in_progress, completed)
- Records completion timestamps and result locations
- Provides pending/completed summaries

**Example**:
```python
from coffee_maker.cli.user_interpret import RequestTracker

tracker = RequestTracker()

# Add request
request_id = tracker.add_request(
    request_type="feature",
    description="Login feature",
    user_message="add a login feature",
    delegated_to="code_developer"
)

# Later: mark complete
tracker.mark_completed(
    request_id,
    result_location="/docs/login_tutorial.md"
)

# Get pending
pending = tracker.get_pending_requests()
print(f"Pending: {len(pending)}")

# Get recently completed
completed = tracker.get_recently_completed(hours=24)
for req in completed:
    print(f"✅ {req['description']} - {req['result_location']}")
```

### 3. ProactiveSuggestions

**Purpose**: Generate proactive messages based on context

**File**: `coffee_maker/cli/user_interpret/proactive_suggestions.py`

**Features**:
- Greeting suggestions (show completed work on startup)
- Contextual suggestions (helpful tips during conversation)
- Completion notifications (announce finished work)
- Pending summaries (status updates)

**Example**:
```python
from coffee_maker.cli.user_interpret import ProactiveSuggestions

suggester = ProactiveSuggestions()

# Get greeting suggestions
greeting = suggester.get_greeting_suggestions()
for msg in greeting:
    print(msg)
    # "✨ Hey! The feature you requested is ready: 'Login system'"
    # "📋 I'm tracking 5 pending requests for you."

# Get contextual suggestions
contextual = suggester.get_contextual_suggestions("what's the status?")
for msg in contextual:
    print(msg)
    # "I'm tracking 3 pending items. Want details on any specific request?"

# Get completion notification
notification = suggester.get_completion_notification(request_id)
print(notification)
# "✨ Great news! The feature you requested is ready: 'Auth system'"
```

## Integration with user_interpret

The `UserInterpret` agent automatically integrates all three components:

```python
from coffee_maker.cli.user_interpret import UserInterpret

agent = UserInterpret()

# Interpret (automatically logs conversation and tracks requests)
result = agent.interpret("add authentication feature")

# Proactive methods
greeting = agent.get_greeting_suggestions()
contextual = agent.get_contextual_suggestions("show me status")
pending = agent.get_pending_requests()
summary = agent.get_conversation_summary(days=7)
```

## Integration with user_listener

The `user_listener` CLI shows proactive messages:

**On Startup**:
```
Welcome! I'm your interface to the autonomous development team.

✨ Hey! The feature you requested is ready: 'Login system'
📖 Check it out at: /docs/login_tutorial.md

Type 'help' for commands, 'agents' to see team members, or 'exit' to quit.
```

**During Conversation**:
```
> show me the roadmap

I'll ask project_manager to show you the roadmap.

💡 Pro tip: You can also check real-time status with `poetry run project-manager developer-status`
```

## Data Storage

All data is stored in `docs/user_interpret/`:

### conversation_history.jsonl

JSONL format (one JSON object per line):

```jsonl
{"timestamp": "2025-10-15T10:30:00", "user_message": "add login", "intent": "add_feature", "delegated_to": "code_developer", "sentiment_signals": [], "confidence": 0.9, "conversation_id": "20251015_103000_123456"}
{"timestamp": "2025-10-15T10:35:00", "user_message": "what's the status", "intent": "check_status", "delegated_to": "project_manager", "sentiment_signals": [], "confidence": 0.85, "conversation_id": "20251015_103500_654321"}
```

### user_requests.json

JSON format:

```json
{
  "feature_requests": [
    {
      "id": "feature_20251015_103000",
      "type": "feature",
      "description": "add login",
      "user_message": "add login feature",
      "delegated_to": "code_developer",
      "status": "completed",
      "created_at": "2025-10-15T10:30:00",
      "updated_at": "2025-10-15T14:00:00",
      "completed_at": "2025-10-15T14:00:00",
      "result_location": "/docs/login_tutorial.md"
    }
  ],
  "bug_reports": [],
  "documentation_requests": [],
  "questions": []
}
```

## Use Cases

### 1. Feature Request Workflow

**User**: "add authentication"

**user_interpret**:
- Interprets intent: `add_feature`
- Logs conversation
- Creates request tracking
- Returns: "I'll ask code_developer to implement this feature"

**Later (when code_developer completes)**:
- code_developer calls: `agent.mark_request_completed(request_id, "/docs/auth_tutorial.md")`

**Next time user starts user_listener**:
- Greeting shows: "✨ Hey! The feature you requested is ready: 'authentication' - Check it out at: /docs/auth_tutorial.md"

### 2. Status Inquiry

**User**: "what's the status?"

**user_interpret**:
- Interprets intent: `check_status`
- Gets contextual suggestion
- Shows: "💡 I'm tracking 5 pending items. Want details on any specific request?"

### 3. Conversation Pattern Learning

**After 10 conversations**:
- `summarize_recent_activity()` shows:
  - Most common intents: `add_feature` (5), `check_status` (3), `report_bug` (2)
  - Most used agents: `code_developer` (6), `project_manager` (4)
  - Average confidence: 0.87

This data can be used for:
- Improving intent interpretation
- Understanding user preferences
- Optimizing agent delegation

## API Reference

### ConversationLogger

```python
logger = ConversationLogger(docs_dir="docs/user_interpret")

# Log conversation
entry = logger.log_conversation(
    user_message: str,
    intent: str,
    delegated_to: str,
    sentiment_signals: List[SentimentSignal],
    confidence: float
) -> Dict[str, Any]

# Get recent
recent = logger.get_recent_conversations(limit: int = 10) -> List[Dict]

# Filter by intent
filtered = logger.get_conversations_by_intent(intent: str, limit: int = 5) -> List[Dict]

# Summarize
summary = logger.summarize_recent_activity(days: int = 7) -> Dict[str, Any]
```

### RequestTracker

```python
tracker = RequestTracker(docs_dir="docs/user_interpret")

# Add request
request_id = tracker.add_request(
    request_type: str,  # "feature", "bug", "documentation", "question"
    description: str,
    user_message: str,
    delegated_to: str
) -> str

# Mark completed
tracker.mark_completed(request_id: str, result_location: Optional[str] = None)

# Update status
tracker.update_status(request_id: str, status: str, notes: Optional[str] = None)

# Get pending
pending = tracker.get_pending_requests() -> List[Dict]

# Get completed
completed = tracker.get_recently_completed(hours: int = 24) -> List[Dict]

# Get specific request
request = tracker.get_request(request_id: str) -> Optional[Dict]
```

### ProactiveSuggestions

```python
suggester = ProactiveSuggestions()

# Greeting suggestions
greeting = suggester.get_greeting_suggestions() -> List[str]

# Contextual suggestions
contextual = suggester.get_contextual_suggestions(user_message: str) -> List[str]

# Completion notification
notification = suggester.get_completion_notification(request_id: str) -> Optional[str]

# Pending summary
summary = suggester.get_pending_summary() -> Dict[str, Any]
```

### UserInterpret Integration

```python
from coffee_maker.cli.user_interpret import UserInterpret

agent = UserInterpret()

# Automatic logging + tracking
result = agent.interpret(user_message: str) -> Dict[str, Any]

# Proactive methods
greeting = agent.get_greeting_suggestions() -> List[str]
contextual = agent.get_contextual_suggestions(user_message: str) -> List[str]
pending = agent.get_pending_requests() -> List[Dict]
summary = agent.get_conversation_summary(days: int = 7) -> Dict[str, Any]
agent.mark_request_completed(request_id: str, result_location: Optional[str] = None)
```

## Future Enhancements

### Phase 2: Advanced Analytics
- Intent prediction based on conversation patterns
- User preference learning (favorite agents, common requests)
- Sentiment trend analysis
- Automated suggestion improvements

### Phase 3: Cross-Agent Coordination
- Notify project_manager when requests are created
- Coordinate with code_developer for completion status
- Integration with GitHub issues for better tracking

### Phase 4: Machine Learning
- Train models on conversation history
- Predict user intent more accurately
- Personalized proactive suggestions
- Anomaly detection (frustrated users, stuck requests)

## Testing

Run tests:
```bash
pytest tests/unit/test_user_interpret_proactive.py -v
```

Test coverage includes:
- ConversationLogger logging and retrieval
- RequestTracker pending/completed tracking
- ProactiveSuggestions message generation
- UserInterpret integration
- End-to-end greeting workflow

## Maintenance

### Clearing Old Data

To reset conversation history:
```bash
rm -rf docs/user_interpret/conversation_history.jsonl
```

To reset request tracking:
```bash
rm -rf docs/user_interpret/user_requests.json
```

### Backup

Backup conversation data:
```bash
cp -r docs/user_interpret/ docs/user_interpret_backup_$(date +%Y%m%d)/
```

## Questions?

This system is owned and maintained by the **user_interpret** agent.

For feature requests or bug reports, contact:
- **Owner**: user_interpret
- **Delegate to**: code_developer (for implementation)
- **Documentation**: project_manager (for spec updates)

---

**Version**: 1.0
**Last Updated**: 2025-10-15
**Status**: Production Ready
