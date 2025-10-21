# Skill: Agent Message Handling

**Name**: `agent-message-handling`
**Owner**: ALL agents (architect, code_developer, project_manager, assistant, code_searcher, ux_design_expert)
**Purpose**: Send and receive inter-agent messages via orchestrator's SQLite message queue
**Priority**: CRITICAL - Enables agent-to-agent communication

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ Sending task requests to other agents (spec creation, demo requests, etc.)
- ✅ Receiving task delegations from orchestrator
- ✅ Sending responses back to requesting agents
- ✅ Sending user-facing responses via user_listener
- ✅ Polling for new messages in agent's inbox

**Example Triggers**:
```python
# architect: Notify code_developer that spec is ready
send_task_response(
    recipient="code_developer",
    task_type="spec_created",
    payload={"spec_id": "SPEC-072", "priority": "PRIORITY 11"}
)

# code_developer: Request demo from assistant
send_task_request(
    suggested_recipient="assistant",
    task="Create demo for PRIORITY 11",
    reason="Implementation complete, needs QA demo"
)

# assistant: Send response to user via user_listener
send_user_response(
    response="✅ Demo completed successfully for PRIORITY 11",
    original_task_id="abc-123"
)
```

---

## Architecture: Orchestrator-Centric Messaging

**CRITICAL PRINCIPLE**: ALL inter-agent messages go THROUGH the orchestrator.

```
Agent A → orchestrator (with suggested_recipient: Agent B)
          ↓
     orchestrator analyzes and routes
          ↓
     orchestrator → Agent B (best available agent)
```

**Benefits**:
- Central routing & load balancing
- Bottleneck detection (orchestrator measures task duration)
- Velocity metrics (track all agent performance)
- Flexibility (orchestrator can override recipient suggestions)

---

## Skill Execution Steps

### Step 1: Import MessageQueue

**ALWAYS** import the MessageQueue from the correct module:

```python
from coffee_maker.autonomous.message_queue import (
    MessageQueue,
    Message,
    MessageType
)
```

**Available in BaseAgent**:
- `self._read_messages(type_filter=None, limit=10)` - Read messages from your inbox
- All agents inherit this method from BaseAgent

---

### Step 2: Reading Messages (Receiving)

**Use Case**: Check inbox for new task delegations

**Method**: `self._read_messages(type_filter=None, limit=10)`

**Example 1: Read all messages**
```python
def _do_background_work(self):
    """Agent's main work loop."""
    # Check for new messages
    messages = self._read_messages(limit=10)

    for message in messages:
        self._handle_message(message)

    # Continue with regular background work
    self._check_for_new_priorities()
```

**Example 2: Filter by message type**
```python
def _process_commit_reviews(self):
    """Process commit review requests only."""
    # Read only commit_review_request messages
    messages = self._read_messages(
        type_filter="commit_review_request",
        limit=3  # Process max 3 per iteration
    )

    for message in messages:
        self._review_single_commit(message)
```

**Example 3: Handle different message types**
```python
def _handle_message(self, message: Dict):
    """Route message based on type."""
    msg_type = message.get("type")

    if msg_type == MessageType.TASK_REQUEST.value:
        # Orchestrator delegated a task to us
        task = message["payload"].get("task")
        self._execute_task(task)

    elif msg_type == MessageType.SPEC_CREATED.value:
        # architect notified us of new spec
        spec_id = message["payload"].get("spec_id")
        self._start_implementation(spec_id)

    elif msg_type == MessageType.DEMO_REQUEST.value:
        # Request to create a demo
        priority = message["payload"].get("priority")
        self._create_demo(priority)
```

**Message Structure**:
```python
message = {
    "type": "task_request",              # MessageType.value
    "sender": "architect",               # AgentType.value
    "recipient": "code_developer",       # AgentType.value
    "payload": {                         # Dict with message data
        "task": "Implement SPEC-072",
        "spec_id": "SPEC-072",
        "priority": "PRIORITY 11"
    },
    "priority": 2,                       # 1=highest, 10=lowest
    "task_id": "abc-123-def-456",       # Unique ID
    "timestamp": "2025-10-19T11:00:00"  # ISO8601
}
```

---

### Step 3: Sending Messages (To Other Agents)

**CRITICAL**: ALWAYS send TO orchestrator with suggested_recipient, NOT directly to agents!

**Method**: Create `MessageQueue()` and call `.send(Message(...))`

**Example 1: Task Request (Agent needs help from another agent)**
```python
from coffee_maker.autonomous.message_queue import MessageQueue, Message, MessageType

def request_spec_creation(self, priority_name: str):
    """Request architect to create spec (via orchestrator)."""
    queue = MessageQueue()

    message = Message(
        sender=self.agent_type.value,           # "code_developer"
        recipient="orchestrator",               # ALWAYS orchestrator!
        type=MessageType.TASK_REQUEST.value,
        payload={
            "suggested_recipient": "architect", # Suggest architect
            "task": f"Create technical spec for {priority_name}",
            "priority": priority_name,
            "reason": "Spec needed before implementation"
        },
        priority=1  # High priority (1=highest, 10=lowest)
    )

    queue.send(message)
    logger.info(f"Requested spec creation from architect (via orchestrator)")
```

**Example 2: Task Response (Reply to requester)**
```python
def notify_spec_complete(self, spec_id: str, requester: str, original_task_id: str):
    """Notify requester that spec is complete."""
    queue = MessageQueue()

    message = Message(
        sender=self.agent_type.value,           # "architect"
        recipient="orchestrator",               # ALWAYS orchestrator!
        type=MessageType.TASK_RESPONSE.value,
        payload={
            "original_task_id": original_task_id,
            "spec_id": spec_id,
            "status": "complete",
            "spec_path": f"docs/architecture/specs/{spec_id}.md"
        },
        priority=2
    )

    queue.send(message)
    logger.info(f"Notified {requester} that spec {spec_id} is complete")
```

**Example 3: User Response (Send to user via user_listener)**
```python
def send_demo_result_to_user(self, demo_result: str, task_id: str):
    """Send demo result to user via user_listener."""
    queue = MessageQueue()

    message = Message(
        sender=self.agent_type.value,           # "assistant"
        recipient="user_listener",              # Direct to user_listener
        type=MessageType.USER_RESPONSE.value,
        payload={
            "response": demo_result,
            "original_task_id": task_id
        },
        priority=1  # User-facing = high priority
    )

    queue.send(message)
    logger.info("Sent demo result to user_listener")
```

**Example 4: Bug Report to project_manager**
```python
def report_bug_to_pm(self, bug_details: Dict):
    """Report bug to project_manager for ROADMAP priority creation."""
    queue = MessageQueue()

    message = Message(
        sender=self.agent_type.value,           # "assistant"
        recipient="orchestrator",               # Via orchestrator
        type=MessageType.BUG_REPORT.value,
        payload={
            "suggested_recipient": "project_manager",
            "title": bug_details["title"],
            "description": bug_details["description"],
            "reproduction_steps": bug_details["steps"],
            "severity": "CRITICAL",
            "found_in_priority": bug_details["priority"]
        },
        priority=1  # Bugs are high priority
    )

    queue.send(message)
    logger.info("Reported bug to project_manager")
```

---

### Step 4: Message Lifecycle Management

**Mark messages as processed**:

When using `_read_messages()`, messages are automatically marked as "started".
After handling, you should mark them as "completed" or "failed":

```python
from coffee_maker.autonomous.message_queue import MessageQueue

def _handle_message(self, message: Dict):
    """Handle message and mark lifecycle."""
    queue = MessageQueue()
    task_id = message["task_id"]

    try:
        # Process the message
        result = self._do_task(message)

        # Mark as completed (with duration tracking)
        queue.mark_completed(task_id, duration_ms=1500)

        logger.info(f"✅ Task {task_id} completed")

    except Exception as e:
        # Mark as failed with error message
        queue.mark_failed(task_id, error_message=str(e))

        logger.error(f"❌ Task {task_id} failed: {e}")
```

---

## Message Priority Guidelines

Use these priorities for different message types:

| Priority | Use Case | Example |
|----------|----------|---------|
| 1 (highest) | User requests, critical bugs, blocking issues | User input, CRITICAL bugs |
| 2 | Urgent coordination, spec requests | code_developer → architect spec request |
| 3 | Normal task delegation | Demo requests, analysis requests |
| 4-5 (normal) | Status updates, notifications | Progress updates, heartbeats |
| 6-10 (low) | Background work, analytics | Weekly analysis, metrics |

---

## Common Patterns

### Pattern 1: Request-Response Cycle

**Requester (code_developer)**:
```python
# 1. Send request
message = Message(
    sender="code_developer",
    recipient="orchestrator",
    type=MessageType.TASK_REQUEST.value,
    payload={
        "suggested_recipient": "architect",
        "task": "Create spec for US-072"
    },
    priority=2
)
queue.send(message)

# 2. Store task_id for response tracking
self.pending_requests[message.task_id] = {
    "type": "spec_request",
    "priority": "PRIORITY 11",
    "requested_at": datetime.now()
}
```

**Responder (architect)**:
```python
# 1. Receive request
messages = self._read_messages(type_filter="task_request")

for msg in messages:
    # 2. Do the work
    spec_id = self._create_spec(msg["payload"]["task"])

    # 3. Send response
    response = Message(
        sender="architect",
        recipient="orchestrator",
        type=MessageType.TASK_RESPONSE.value,
        payload={
            "original_task_id": msg["task_id"],
            "spec_id": spec_id,
            "status": "complete"
        },
        priority=2
    )
    queue.send(response)
```

### Pattern 2: Broadcast Notification

**Sender (code_developer)**:
```python
# Notify ALL agents of completion (via orchestrator routing)
message = Message(
    sender="code_developer",
    recipient="orchestrator",
    type=MessageType.TASK_COMPLETE.value,
    payload={
        "priority": "PRIORITY 11",
        "status": "implementation_complete",
        "files_changed": ["daemon.py", "orchestrator.py"]
    },
    priority=3
)
queue.send(message)
# Orchestrator will route to interested agents (assistant for demo, PM for tracking)
```

### Pattern 3: Error Recovery

```python
def send_with_retry(message: Message, max_retries: int = 3):
    """Send message with retry logic."""
    queue = MessageQueue()

    for attempt in range(max_retries):
        try:
            queue.send(message)
            logger.info(f"✅ Message sent (attempt {attempt + 1})")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Send failed (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"❌ Message send failed after {max_retries} attempts")
                return False
            time.sleep(2 ** attempt)  # Exponential backoff

    return False
```

---

## Quick Reference

### Read Messages
```python
# All messages
messages = self._read_messages(limit=10)

# Filter by type
messages = self._read_messages(type_filter="commit_review_request", limit=5)
```

### Send to Another Agent (via orchestrator)
```python
queue = MessageQueue()
message = Message(
    sender=self.agent_type.value,
    recipient="orchestrator",
    type=MessageType.TASK_REQUEST.value,
    payload={"suggested_recipient": "assistant", "task": "..."},
    priority=2
)
queue.send(message)
```

### Send to User (via user_listener)
```python
queue = MessageQueue()
message = Message(
    sender=self.agent_type.value,
    recipient="user_listener",
    type=MessageType.USER_RESPONSE.value,
    payload={"response": "Task complete!"},
    priority=1
)
queue.send(message)
```

### Mark as Complete
```python
queue = MessageQueue()
queue.mark_completed(task_id, duration_ms=1500)
```

### Mark as Failed
```python
queue = MessageQueue()
queue.mark_failed(task_id, error_message="Spec not found")
```

---

## Testing Your Message Handling

**Test sending a message**:
```python
# In agent code
def test_send_message(self):
    """Test message sending."""
    queue = MessageQueue()

    message = Message(
        sender=self.agent_type.value,
        recipient="orchestrator",
        type=MessageType.TASK_REQUEST.value,
        payload={"suggested_recipient": "assistant", "task": "test"},
        priority=5
    )

    queue.send(message)
    logger.info("✅ Test message sent")
```

**Test reading messages**:
```python
# In agent code
def test_read_messages(self):
    """Test message reading."""
    messages = self._read_messages(limit=5)
    logger.info(f"📬 Read {len(messages)} messages")

    for msg in messages:
        logger.info(f"  - Type: {msg['type']}, Sender: {msg['sender']}")
```

---

## Troubleshooting

### Issue: Messages not arriving

**Solution 1: Check recipient**
- ALWAYS send to "orchestrator", NOT directly to agents
- Orchestrator routes based on suggested_recipient

**Solution 2: Check database**
```bash
# Check message queue
sqlite3 data/orchestrator.db "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10;"
```

**Solution 3: Check orchestrator logs**
- Orchestrator logs all routing decisions
- Look for "Routing USER_REQUEST" or "Routing TASK_REQUEST"

### Issue: Message not marked as complete

**Solution**: Ensure you call `mark_completed()` after handling:
```python
try:
    self._do_work(message)
    queue.mark_completed(message["task_id"], duration_ms=1000)
except Exception as e:
    queue.mark_failed(message["task_id"], error_message=str(e))
```

### Issue: AttributeError: '_read_messages' not found

**Solution**: Ensure BaseAgent has the `_read_messages` method (should be added in base_agent.py around line 364).

---

## References

- **MessageQueue API**: `coffee_maker/autonomous/message_queue.py`
- **BaseAgent**: `coffee_maker/autonomous/agents/base_agent.py` (line 364+)
- **Orchestrator routing**: `coffee_maker/autonomous/orchestrator.py`
- **SPEC-057**: Technical specification for orchestrator architecture
- **US-057**: Multi-agent orchestrator strategic requirements
