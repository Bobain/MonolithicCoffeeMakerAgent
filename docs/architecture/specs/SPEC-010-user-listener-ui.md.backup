# SPEC-010: User-Listener UI Command

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-16
**Related**: PRIORITY 9 (User-Listener Implementation)

---

## Problem Statement

Currently, the `project-manager chat` command serves as the user interface for the MonolithicCoffeeMakerAgent system. However, this violates the architectural principle that **user_listener** should be the PRIMARY USER INTERFACE agent. The current implementation creates confusion about agent boundaries and responsibilities:

- `project_manager` should focus on strategic tasks (ROADMAP, GitHub monitoring, backend operations)
- `user_listener` should be the ONLY agent with direct UI responsibility
- No standalone `user-listener` command exists
- `AgentType.USER_LISTENER` is defined but not implemented

This creates architectural debt and prevents clear separation of concerns between UI (user_listener) and backend operations (other agents).

---

## Proposed Solution

Create a standalone `poetry run user-listener` command that serves as the primary interactive UI for all user interactions. This command will:

1. **Provide interactive chat interface** - Similar to current `project-manager chat` but clearer in purpose
2. **Delegate to specialized agents** - Route requests to project_manager, architect, code_developer, assistant, code-searcher, ux-design-expert
3. **Use Haiku 4.5 for cost efficiency** - Lightweight model for UI orchestration
4. **Enforce singleton pattern** - Only one user_listener instance can run at a time
5. **Maintain conversation context** - Preserve context across agent delegations

---

## Architecture

### High-Level Architecture

```
User
  ↓
user-listener (CLI command: poetry run user-listener)
  ├─→ Haiku 4.5 (UI orchestration, intent classification)
  └─→ Delegates to:
      ├─→ project_manager (strategic tasks, GitHub, ROADMAP)
      ├─→ architect (design, specs, ADRs, dependencies)
      ├─→ code_developer (implementation, PRs)
      ├─→ assistant (docs, demos, bugs)
      ├─→ code-searcher (deep code analysis)
      └─→ ux-design-expert (UI/UX design)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     user-listener CLI                        │
│  File: coffee_maker/cli/user_listener.py                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         UserListenerCLI (main class)               │    │
│  │  - ai_service: AIService (Haiku 4.5)              │    │
│  │  - chat_session: ChatSession (reused)             │    │
│  │  - agent_router: AgentDelegationRouter            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│              AgentDelegationRouter (new class)               │
│  File: coffee_maker/cli/agent_router.py                     │
│                                                              │
│  Methods:                                                    │
│  - classify_intent(user_input) → AgentType                  │
│  - delegate_to_agent(agent_type, request, context) → str    │
│  - get_delegation_prompt(agent_type) → str                  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌──────────────┬─────────────┬──────────────┬─────────────────┐
│ project_mgr  │  architect  │ code_dev     │  assistant      │
│ (strategic)  │ (design)    │ (impl)       │ (docs/demos)    │
└──────────────┴─────────────┴──────────────┴─────────────────┘
```

### Data Flow

```
1. User types: "Design a caching layer"
   ↓
2. user-listener receives input
   ↓
3. Haiku 4.5 classifies intent → "architectural design"
   ↓
4. AgentDelegationRouter routes to architect
   ↓
5. architect creates technical spec
   ↓
6. user-listener displays response to user
   ↓
7. Conversation context maintained for follow-ups
```

---

## Technical Details

### Component Specifications

#### 1. UserListenerCLI Class

**Location**: `coffee_maker/cli/user_listener.py`

**Responsibilities**:
- Manage interactive chat session
- Classify user intent (via Haiku 4.5)
- Delegate to appropriate agents
- Display responses with rich formatting
- Maintain conversation history

**Key Methods**:

```python
class UserListenerCLI:
    """Primary user interface for MonolithicCoffeeMakerAgent.

    ONLY agent with UI responsibility. All user interactions go through here.
    """

    def __init__(self):
        """Initialize user-listener CLI."""
        # Use Haiku 4.5 for cost-efficient UI orchestration
        self.ai_service = AIService(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000
        )

        # Reuse existing ChatSession infrastructure
        self.chat_session = ChatSession(
            ai_service=self.ai_service,
            editor=None,  # user_listener doesn't modify roadmap directly
            enable_streaming=True
        )

        # Agent delegation router
        self.agent_router = AgentDelegationRouter(self.ai_service)

        # Register as singleton
        self.registry = AgentRegistry()

    def start(self):
        """Start interactive user-listener session.

        Registers as singleton and starts REPL loop.
        """
        with AgentRegistry.register(AgentType.USER_LISTENER):
            self._display_welcome()
            self._run_repl_loop()

    def _run_repl_loop(self):
        """Main REPL loop for user interaction."""
        while True:
            user_input = self.chat_session.prompt_session.prompt("› ")

            if not user_input.strip():
                continue

            # Handle exit
            if user_input.lower() in ["/exit", "/quit"]:
                break

            # Classify intent and delegate
            response = self._process_input(user_input)

            # Display response
            self.chat_session._display_response(response)

    def _process_input(self, user_input: str) -> str:
        """Process user input and delegate to appropriate agent.

        Args:
            user_input: User's message

        Returns:
            Response from delegated agent or user_listener
        """
        # Classify intent (which agent should handle this?)
        agent_type, confidence = self.agent_router.classify_intent(user_input)

        # If high confidence, delegate directly
        if confidence > 0.8:
            return self.agent_router.delegate_to_agent(
                agent_type,
                user_input,
                self.chat_session.history
            )

        # Otherwise, ask user_listener's AI (Haiku 4.5) to handle
        return self._handle_with_ai(user_input)

    def _handle_with_ai(self, user_input: str) -> str:
        """Handle request with user_listener's AI (Haiku 4.5).

        Used for general questions, clarifications, and ambiguous requests.

        Args:
            user_input: User's message

        Returns:
            AI response
        """
        # Use existing ChatSession AI handling
        context = self._build_context()

        response = self.ai_service.process_request(
            user_input=user_input,
            context=context,
            history=self.chat_session.history,
            stream=False
        )

        return response.message

    def _build_context(self) -> Dict:
        """Build context for AI requests.

        Returns:
            Context dictionary with agent info
        """
        return {
            "role": "user_listener",
            "responsibilities": [
                "Primary user interface",
                "Intent classification",
                "Agent delegation",
                "Context maintenance"
            ],
            "available_agents": [
                "project_manager - Strategic tasks, ROADMAP, GitHub",
                "architect - Design, specs, ADRs, dependencies",
                "code_developer - Implementation, PRs",
                "assistant - Documentation, demos, bugs",
                "code-searcher - Deep code analysis",
                "ux-design-expert - UI/UX design"
            ]
        }

    def _display_welcome(self):
        """Display welcome message."""
        console = Console()
        console.print("\n[bold]User Listener[/] [dim]·[/] Primary Interface")
        console.print("[dim]Powered by Claude Haiku 4.5[/]\n")
        console.print("[dim]I'm your interface to the agent team.[/]")
        console.print("[dim]Tell me what you need, and I'll route it to the right specialist.[/]\n")
```

#### 2. AgentDelegationRouter Class

**Location**: `coffee_maker/cli/agent_router.py`

**Responsibilities**:
- Classify user intent → determine which agent should handle request
- Delegate requests to specialized agents
- Manage agent communication protocol
- Pass context between agents

**Key Methods**:

```python
class AgentDelegationRouter:
    """Routes user requests to appropriate specialized agents.

    Uses pattern matching and AI classification to determine
    which agent should handle each type of request.
    """

    def __init__(self, ai_service: AIService):
        """Initialize agent router.

        Args:
            ai_service: AI service for intent classification
        """
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)

    def classify_intent(self, user_input: str) -> Tuple[AgentType, float]:
        """Classify user intent to determine appropriate agent.

        Uses keyword matching + AI classification for high accuracy.

        Args:
            user_input: User's message

        Returns:
            Tuple of (agent_type, confidence)

        Example:
            >>> router.classify_intent("Design a caching layer")
            (AgentType.ARCHITECT, 0.95)
        """
        # Pattern-based classification (fast)
        patterns = {
            AgentType.ARCHITECT: [
                "design", "architecture", "technical spec", "adr",
                "dependency", "add package", "design pattern"
            ],
            AgentType.PROJECT_MANAGER: [
                "roadmap", "priority", "github", "pr status",
                "strategic", "planning", "milestone"
            ],
            AgentType.CODE_DEVELOPER: [
                "implement", "code", "pull request", "pr",
                "fix bug", "write code", "develop"
            ],
            AgentType.ASSISTANT: [
                "documentation", "demo", "show me", "explain",
                "test", "bug report", "how does"
            ],
            AgentType.CODE_SEARCHER: [
                "find in code", "where is", "search code",
                "analyze code", "code forensics", "dependency trace"
            ],
            AgentType.UX_DESIGN_EXPERT: [
                "ui", "ux", "design", "tailwind", "dashboard",
                "chart", "visualization", "layout"
            ]
        }

        # Check patterns
        lower_input = user_input.lower()
        for agent_type, keywords in patterns.items():
            if any(keyword in lower_input for keyword in keywords):
                self.logger.info(f"Intent classified: {agent_type.value} (pattern match)")
                return (agent_type, 0.9)  # High confidence from pattern match

        # Fallback to AI classification for ambiguous cases
        return self._classify_with_ai(user_input)

    def _classify_with_ai(self, user_input: str) -> Tuple[AgentType, float]:
        """Use AI to classify ambiguous intents.

        Args:
            user_input: User's message

        Returns:
            Tuple of (agent_type, confidence)
        """
        prompt = f"""Classify this user request to determine which specialized agent should handle it:

User request: "{user_input}"

Available agents:
- architect: Design, technical specs, ADRs, dependency management
- project_manager: Strategic planning, ROADMAP, GitHub monitoring
- code_developer: Implementation, pull requests, bug fixes
- assistant: Documentation, demos, bug reports, explanations
- code-searcher: Deep code analysis, searching codebase
- ux-design-expert: UI/UX design, Tailwind, charts

Respond ONLY with the agent name and confidence (0.0-1.0):
<classification>
<agent>architect</agent>
<confidence>0.95</confidence>
</classification>
"""

        response = self.ai_service.process_request(
            user_input=prompt,
            context={},
            history=[],
            stream=False
        )

        # Parse response
        agent_match = re.search(r"<agent>(.+?)</agent>", response.message)
        conf_match = re.search(r"<confidence>(.+?)</confidence>", response.message)

        if agent_match and conf_match:
            agent_name = agent_match.group(1).strip()
            confidence = float(conf_match.group(1).strip())

            # Map name to AgentType
            agent_map = {
                "architect": AgentType.ARCHITECT,
                "project_manager": AgentType.PROJECT_MANAGER,
                "code_developer": AgentType.CODE_DEVELOPER,
                "assistant": AgentType.ASSISTANT,
                "code-searcher": AgentType.CODE_SEARCHER,
                "ux-design-expert": AgentType.UX_DESIGN_EXPERT,
            }

            agent_type = agent_map.get(agent_name, AgentType.ASSISTANT)
            self.logger.info(f"Intent classified: {agent_type.value} (AI, {confidence:.2f})")
            return (agent_type, confidence)

        # Default to assistant for unknown
        self.logger.warning("Failed to classify intent, defaulting to assistant")
        return (AgentType.ASSISTANT, 0.5)

    def delegate_to_agent(
        self,
        agent_type: AgentType,
        request: str,
        conversation_history: List[Dict]
    ) -> str:
        """Delegate request to specified agent.

        Args:
            agent_type: Which agent to delegate to
            request: User's request
            conversation_history: Previous conversation context

        Returns:
            Agent's response
        """
        self.logger.info(f"Delegating to {agent_type.value}: {request[:50]}...")

        # Get delegation prompt for this agent type
        delegation_prompt = self._get_delegation_prompt(agent_type, request)

        # Execute delegation
        # NOTE: In Phase 1, we simulate delegation by using AI with agent-specific prompts
        # In Phase 2, this would integrate with actual agent instances

        response = self.ai_service.process_request(
            user_input=delegation_prompt,
            context={"agent_type": agent_type.value},
            history=conversation_history[-5:],  # Last 5 messages for context
            stream=False
        )

        return response.message

    def _get_delegation_prompt(self, agent_type: AgentType, request: str) -> str:
        """Get agent-specific delegation prompt.

        Each agent has a specialized prompt that guides the AI to respond
        as that agent would.

        Args:
            agent_type: Agent to delegate to
            request: User's request

        Returns:
            Formatted delegation prompt
        """
        # Load agent-specific prompts from .claude/agents/
        agent_prompts = {
            AgentType.ARCHITECT: load_prompt(
                PromptNames.AGENT_ARCHITECT,
                {"USER_REQUEST": request}
            ),
            AgentType.PROJECT_MANAGER: load_prompt(
                PromptNames.AGENT_PROJECT_MANAGER,
                {"USER_REQUEST": request}
            ),
            # Add other agents as needed
        }

        return agent_prompts.get(agent_type, request)
```

#### 3. CLI Entry Point

**Location**: `coffee_maker/cli/user_listener.py` (bottom of file)

```python
def main():
    """Main entry point for user-listener CLI.

    Command: poetry run user-listener
    """
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    try:
        # Create and start user-listener CLI
        cli = UserListenerCLI()
        cli.start()

    except AgentAlreadyRunningError as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/]\n")
        sys.exit(1)

    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[dim]Goodbye![/]\n")
        sys.exit(0)

    except Exception as e:
        console = Console()
        console.print(f"\n[red]Unexpected error: {e}[/]\n")
        logger.error(f"Fatal error in user-listener", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

#### 4. Poetry Script Registration

**Location**: `pyproject.toml`

```toml
[tool.poetry.scripts]
project-manager = "coffee_maker.cli.roadmap_cli:main"
code-developer = "coffee_maker.autonomous.daemon_cli:main"
user-listener = "coffee_maker.cli.user_listener:main"  # NEW
```

---

## Agent Delegation Protocol

### How user_listener Communicates with Other Agents

**Phase 1 (Current Implementation)**: AI-Powered Simulation
- user_listener uses Haiku 4.5 with agent-specific prompts
- Each agent has a prompt template in `.claude/agents/`
- AI responds "as if" it were that agent
- Works immediately, no inter-process communication needed

**Phase 2 (Future Enhancement)**: True Agent-to-Agent Communication
- user_listener sends structured messages to actual agent instances
- Uses notification system or message queue
- Agents respond via callbacks or async messages
- Enables true multi-agent collaboration

### Context Passing Mechanism

```python
# Context structure passed between agents
delegation_context = {
    "user_request": "Design a caching layer",
    "conversation_history": [...],  # Last 5-10 messages
    "delegated_from": "user_listener",
    "delegated_to": "architect",
    "timestamp": "2025-10-16T10:30:00Z",
    "metadata": {
        "confidence": 0.95,
        "classification_method": "pattern_match"
    }
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (4-6 hours)

**Tasks**:
1. **Create `coffee_maker/cli/user_listener.py`** (2h)
   - Define `UserListenerCLI` class
   - Implement `main()` entry point
   - Integrate with `ChatSession` (reuse existing)
   - Add singleton registration

2. **Create `coffee_maker/cli/agent_router.py`** (2h)
   - Define `AgentDelegationRouter` class
   - Implement pattern-based classification
   - Implement AI-based classification fallback
   - Add delegation methods

3. **Register Poetry script** (0.5h)
   - Add `user-listener = "coffee_maker.cli.user_listener:main"` to `pyproject.toml`
   - Test: `poetry run user-listener`

4. **Basic testing** (1h)
   - Unit tests for `AgentDelegationRouter.classify_intent()`
   - Integration test for full user-listener flow
   - Manual testing of CLI

### Phase 2: Agent-Specific Prompts (2-3 hours)

**Tasks**:
1. **Create delegation prompts** (1.5h)
   - `.claude/commands/delegate-to-architect.md`
   - `.claude/commands/delegate-to-project-manager.md`
   - `.claude/commands/delegate-to-assistant.md`
   - Add to `PromptNames` enum

2. **Update `AgentDelegationRouter`** (1h)
   - Load prompts using `load_prompt()`
   - Test delegation with each agent type
   - Verify responses match expected agent behavior

3. **Add confidence thresholds** (0.5h)
   - If confidence < 0.6, ask clarifying questions
   - If confidence < 0.8, show delegation choice to user
   - If confidence >= 0.8, delegate automatically

### Phase 3: Migration & Documentation (2-3 hours)

**Tasks**:
1. **Update CLAUDE.md** (1h)
   - Document `poetry run user-listener` command
   - Update agent ownership matrix
   - Add usage examples

2. **Deprecation strategy for `project-manager chat`** (1h)
   - Add deprecation warning to `project-manager chat`
   - Redirect users to `user-listener`
   - Plan removal timeline (e.g., 2-3 releases)

3. **User migration guide** (1h)
   - Create `docs/USER_LISTENER_MIGRATION.md`
   - Explain differences between old and new commands
   - Provide migration checklist

### Phase 4: Advanced Features (Optional, 3-4 hours)

**Tasks**:
1. **Multi-agent collaboration** (2h)
   - Handle requests that require multiple agents
   - Example: "Design and implement a caching layer"
     - Step 1: architect creates spec
     - Step 2: code_developer implements spec
     - User sees both responses

2. **Agent status awareness** (1h)
   - Check if agent is available/busy before delegating
   - Queue requests if agent is busy
   - Provide ETA to user

3. **Conversation threading** (1h)
   - Maintain separate conversation threads per agent
   - Allow user to switch between threads
   - Example: `/thread architect` to see architect conversation

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_user_listener.py`

```python
def test_classify_intent_architect():
    """Test classification for architect requests."""
    router = AgentDelegationRouter(ai_service)
    agent_type, confidence = router.classify_intent("Design a caching layer")

    assert agent_type == AgentType.ARCHITECT
    assert confidence > 0.8


def test_classify_intent_project_manager():
    """Test classification for project_manager requests."""
    router = AgentDelegationRouter(ai_service)
    agent_type, confidence = router.classify_intent("Show me the roadmap")

    assert agent_type == AgentType.PROJECT_MANAGER
    assert confidence > 0.8


def test_singleton_enforcement():
    """Test that only one user_listener can run at a time."""
    with AgentRegistry.register(AgentType.USER_LISTENER):
        # Try to register another instance
        with pytest.raises(AgentAlreadyRunningError):
            AgentRegistry().register_agent(AgentType.USER_LISTENER)
```

**File**: `tests/unit/test_agent_router.py`

```python
def test_delegation_to_architect():
    """Test delegation to architect agent."""
    router = AgentDelegationRouter(ai_service)
    response = router.delegate_to_agent(
        AgentType.ARCHITECT,
        "Design a caching layer",
        conversation_history=[]
    )

    # Response should contain architectural concepts
    assert any(word in response.lower() for word in ["design", "architecture", "spec"])


def test_get_delegation_prompt():
    """Test agent-specific prompt generation."""
    router = AgentDelegationRouter(ai_service)
    prompt = router._get_delegation_prompt(
        AgentType.ARCHITECT,
        "Design a caching layer"
    )

    assert "architect" in prompt.lower()
    assert "Design a caching layer" in prompt
```

### Integration Tests

**File**: `tests/ci_tests/test_user_listener_integration.py`

```python
def test_end_to_end_user_listener():
    """Test full user-listener flow."""
    # Start user-listener (in test mode, no REPL)
    cli = UserListenerCLI()

    # Simulate user input
    response = cli._process_input("Design a caching layer")

    # Should delegate to architect
    assert "spec" in response.lower() or "architecture" in response.lower()


def test_conversation_context_preservation():
    """Test that conversation context is maintained."""
    cli = UserListenerCLI()

    # First message
    response1 = cli._process_input("Design a caching layer")

    # Follow-up message (should have context from first)
    response2 = cli._process_input("What technology should we use?")

    # Response should reference caching
    assert "cach" in response2.lower()
```

### Manual Testing

**Test Scenarios**:

1. **Basic Delegation**
   ```bash
   $ poetry run user-listener
   › Design a caching layer
   [Delegates to architect, returns spec outline]
   ```

2. **Multi-Turn Conversation**
   ```bash
   $ poetry run user-listener
   › Design a caching layer
   [architect response]
   › What about Redis vs Memcached?
   [architect continues with context]
   ```

3. **Ambiguous Request**
   ```bash
   $ poetry run user-listener
   › Help me with something
   [user_listener asks clarifying questions]
   ```

4. **Singleton Enforcement**
   ```bash
   # Terminal 1
   $ poetry run user-listener

   # Terminal 2 (should fail)
   $ poetry run user-listener
   Error: Agent 'user_listener' is already running!
   ```

---

## Rollout Plan

### Phase 1: Soft Launch (Week 1)

**Goals**:
- Launch `poetry run user-listener` command
- Run alongside existing `project-manager chat` (no breaking changes)
- Gather user feedback

**Actions**:
1. Deploy Phase 1 implementation
2. Add banner to `project-manager chat` suggesting `user-listener`
3. Monitor usage and errors

### Phase 2: Promote (Week 2-3)

**Goals**:
- Make `user-listener` the recommended interface
- Update all documentation to use `user-listener`

**Actions**:
1. Update README.md to feature `user-listener`
2. Add deprecation warning to `project-manager chat`
3. Send notification to users about new command

### Phase 3: Deprecate (Week 4+)

**Goals**:
- Remove `project-manager chat` or redirect to `user-listener`

**Actions**:
1. Redirect `project-manager chat` to `user-listener`
2. Remove chat-specific code from `project_manager`
3. Clean up agent boundaries

---

## Risks & Mitigations

### Risk 1: User Confusion

**Risk**: Users may not understand the difference between `project-manager chat` and `user-listener`.

**Mitigation**:
- Clear documentation explaining roles
- Deprecation warnings in old command
- Redirect old command to new one

### Risk 2: Context Loss

**Risk**: Context may be lost when delegating between agents.

**Mitigation**:
- Pass conversation history (last 5-10 messages) with every delegation
- Test multi-turn conversations extensively
- Add context summary if needed

### Risk 3: Classification Errors

**Risk**: Intent classification may be incorrect, routing to wrong agent.

**Mitigation**:
- Combine pattern matching + AI classification
- Add confidence thresholds (< 0.8 = ask user)
- Allow user to override: `/ask architect: Design a caching layer`

### Risk 4: Performance

**Risk**: AI classification adds latency to every request.

**Mitigation**:
- Pattern matching first (fast, no API call)
- Cache classification results for similar requests
- Use Haiku 4.5 (fast, cheap) for classification

### Risk 5: Agent Availability

**Risk**: Delegated agent may not be available (e.g., architect busy).

**Mitigation**:
- Phase 1: No issue (AI simulation)
- Phase 2: Check agent status, queue if busy
- Provide ETA to user

---

## Dependencies

**Required**:
- `anthropic` - Already installed (for Haiku 4.5)
- `prompt-toolkit` - Already installed (for ChatSession)
- `rich` - Already installed (for console output)

**Optional** (Future phases):
- Inter-process communication library (if moving to true agent instances)
- Message queue system (for agent-to-agent communication)

---

## Success Metrics

**Phase 1**:
- ✅ `poetry run user-listener` command works
- ✅ Intent classification accuracy > 80%
- ✅ Singleton enforcement prevents duplicate instances
- ✅ Conversation context maintained across turns

**Phase 2**:
- ✅ All agent types can be delegated to
- ✅ Agent-specific responses match expected behavior
- ✅ Confidence thresholds work correctly

**Phase 3**:
- ✅ Users successfully migrated from `project-manager chat`
- ✅ Documentation updated
- ✅ Zero breaking changes for existing workflows

**User Satisfaction**:
- Users prefer `user-listener` over `project-manager chat`
- Average response time < 3 seconds
- 90% of requests routed to correct agent

---

## Future Enhancements

### Multi-Agent Workflows

Enable requests that require coordination between multiple agents:

```
User: "Design and implement a caching layer"
  ↓
user_listener recognizes multi-step request
  ↓
Step 1: architect designs spec → returns SPEC-010-caching.md
  ↓
Step 2: code_developer implements spec → returns PR #123
  ↓
user_listener presents both results to user
```

### Agent Status Dashboard

Add `/status` command to show agent availability:

```bash
› /status

Agent Status:
  🟢 architect       - Available
  🟢 project_manager - Available
  🟡 code_developer  - Busy (working on PRIORITY 5)
  🟢 assistant       - Available
  🟢 code-searcher   - Available
  🟢 ux-design-expert - Available
```

### Conversation Persistence

Save multi-agent conversations for later review:

```bash
› /history

Recent Conversations:
  1. With architect - "Design caching layer" (2 hours ago)
  2. With code_developer - "Implement US-045" (1 day ago)
  3. With assistant - "Show me dashboard demo" (2 days ago)

› /resume 1
[Resumes conversation with architect about caching]
```

---

## Conclusion

This specification provides a complete implementation plan for the `user-listener` command, establishing it as the PRIMARY USER INTERFACE for the MonolithicCoffeeMakerAgent system. The design:

- ✅ Enforces clear agent boundaries (user_listener = UI, others = backend)
- ✅ Reuses existing infrastructure (ChatSession, AIService, AgentRegistry)
- ✅ Uses cost-efficient model (Haiku 4.5) for UI orchestration
- ✅ Provides smooth migration path from `project-manager chat`
- ✅ Enables future multi-agent collaboration

**Total Estimated Effort**: 11-16 hours (across 4 phases)

**Priority**: HIGH (architectural debt, foundational for multi-agent system)

**Next Steps**:
1. Review this spec with user_listener via user interface
2. Get approval for Phase 1 implementation
3. Begin implementation: `UserListenerCLI` class
4. Test with manual scenarios
5. Deploy and monitor

---

**Status**: Ready for Review
**Approver**: User via user_listener (once implemented, this will be dogfooded!)
**Implementation**: code_developer (once spec approved)
