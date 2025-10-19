# SPEC-012: Natural Language User Story Management

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-012 - `/US` Command with Conversational Validation Workflow

**Related ADRs**: None

**Assigned To**: code_developer

---

## Executive Summary

This specification describes the technical design for a natural language `/US` command that enables users to create user stories conversationally with project_manager. The system will extract user story structure from natural language, present a draft for validation, and only propagate to ROADMAP after user approval. This implements a "share ideas → validate → propagate" workflow, NOT immediate addition.

---

## Problem Statement

### Current Situation

Users currently must manually format user stories following the ROADMAP structure (title, DoD, effort, business value, etc.). This is:
- Time-consuming and error-prone
- Requires knowledge of ROADMAP formatting conventions
- Discourages quick idea capture
- Creates friction in the user-PM collaboration workflow

### Goal

Implement a natural language `/US` command that:
- Accepts freeform user input describing what they want
- Extracts structured user story components using AI
- Presents a formatted draft for user validation
- Only adds to ROADMAP after explicit user approval
- Supports iterative refinement through conversation

### Non-Goals

- NOT implementing DoD inference (that's US-013, separate spec)
- NOT implementing automatic prioritization (manual user decision)
- NOT implementing similarity detection (that's US-013)
- NOT implementing multi-turn conversation memory (simple request-response for MVP)

---

## Requirements

### Functional Requirements

1. **FR-1**: Accept `/US [description]` command in project_manager chat
2. **FR-2**: Extract user story title, description, and key requirements from natural language
3. **FR-3**: Present structured user story draft with placeholder fields
4. **FR-4**: Wait for user validation/modification before adding to ROADMAP
5. **FR-5**: Support user edits to draft (title, description, effort estimate)
6. **FR-6**: Add validated user story to ROADMAP only after user confirms
7. **FR-7**: Assign next available US-XXX identifier automatically
8. **FR-8**: Support cancellation at any stage

### Non-Functional Requirements

1. **NFR-1**: Response time < 3 seconds for AI extraction (Claude API)
2. **NFR-2**: Extraction accuracy > 85% (title and description correctly identified)
3. **NFR-3**: User-friendly error messages for malformed input
4. **NFR-4**: Graceful degradation if AI service unavailable (fallback to manual entry)
5. **NFR-5**: Conversation state maintained within single session (no persistence needed for MVP)

### Constraints

- Must use existing AIService class (Claude API integration already available)
- Must use existing RoadmapEditor class for safe ROADMAP updates
- Must follow COLLABORATION_METHODOLOGY.md Section 4.6 (plain language, no technical shorthand)
- Must integrate with existing project_manager chat interface
- Must assign status as "📝 PLANNED" by default

---

## Proposed Solution

### High-Level Approach

Implement a three-phase conversational workflow:
1. **Extract**: Parse natural language input to structured user story draft
2. **Validate**: Present draft to user for confirmation/modification
3. **Propagate**: Add validated user story to ROADMAP.md

Use existing AIService with a specialized prompt for user story extraction. Add a new `UserStoryDraftManager` class to handle validation workflow state. Integrate with existing ChatInterface to handle multi-turn conversation.

### Architecture Diagram

```
┌─────────────────┐
│  User (Chat)    │
└────────┬────────┘
         │
         │ "/US I want email notifications"
         v
┌─────────────────────────────────────────┐
│  ChatInterface                          │
│  (project_manager)                      │
└────────┬────────────────────────────────┘
         │
         │ Delegates to new command handler
         v
┌─────────────────────────────────────────┐
│  UserStoryCommandHandler (NEW)          │
│  - Parse /US command                    │
│  - Manage workflow state                │
└────────┬────────────────────────────────┘
         │
         │ Extract user story
         v
┌─────────────────────────────────────────┐
│  AIService                              │
│  .extract_user_story(description)       │
└────────┬────────────────────────────────┘
         │
         │ Returns UserStoryDraft
         v
┌─────────────────────────────────────────┐
│  UserStoryDraftManager (NEW)            │
│  - Store draft in session               │
│  - Format for user review               │
│  - Handle user edits                    │
└────────┬────────────────────────────────┘
         │
         │ Present to user
         v
┌─────────────────┐
│  User (Chat)    │ ← "Here's what I understood..."
└────────┬────────┘
         │
         │ "Yes, add it" or "Change title to X"
         v
┌─────────────────────────────────────────┐
│  UserStoryCommandHandler                │
│  - Parse validation response            │
│  - Apply edits if requested             │
└────────┬────────────────────────────────┘
         │
         │ User confirmed
         v
┌─────────────────────────────────────────┐
│  RoadmapEditor                          │
│  .add_user_story(draft)                 │
└─────────────────────────────────────────┘
         │
         v
     ROADMAP.md updated ✅
```

### Technology Stack

- **AI Extraction**: Claude API (via existing AIService)
- **ROADMAP Updates**: Existing RoadmapEditor class
- **State Management**: In-memory session state (ChatInterface session)
- **Conversation**: Existing ChatInterface with new command handler
- **Prompts**: Centralized prompt in `.claude/commands/extract-user-story.md`

---

## Detailed Design

### Component 1: UserStoryCommandHandler

**Responsibility**: Handle `/US` command, orchestrate extraction → validation → propagation workflow

**Interface**:
```python
class UserStoryCommandHandler:
    """
    Handles /US command for natural language user story creation.

    Workflow:
    1. Parse /US [description] from user input
    2. Call AIService to extract user story structure
    3. Present draft to user for validation
    4. Handle user edits/confirmation
    5. Propagate to ROADMAP via RoadmapEditor
    """

    def __init__(self, ai_service: AIService, roadmap_editor: RoadmapEditor):
        """Initialize with AI service and roadmap editor."""
        self.ai_service = ai_service
        self.roadmap_editor = roadmap_editor
        self.draft_manager = UserStoryDraftManager()

    def handle_command(
        self,
        user_input: str,
        session_id: str
    ) -> str:
        """
        Handle /US command from user.

        Args:
            user_input: User's input (e.g., "/US I want email notifications")
            session_id: Chat session identifier for state management

        Returns:
            Response message to user

        Example:
            >>> handler.handle_command("/US I want email notifications", "session-123")
            "I've drafted a user story based on your input:\n\n..."
        """
        pass

    def handle_validation_response(
        self,
        user_response: str,
        session_id: str
    ) -> str:
        """
        Handle user's response to draft validation.

        Args:
            user_response: User's validation response
            session_id: Chat session identifier

        Returns:
            Response message (confirmation or further questions)

        Example:
            >>> handler.handle_validation_response("Yes, add it", "session-123")
            "Great! I've added US-025 to the ROADMAP."
        """
        pass

    def _parse_us_command(self, user_input: str) -> Optional[str]:
        """Extract description from /US command."""
        pass

    def _is_confirmation(self, user_response: str) -> bool:
        """Check if user response is confirmation (yes/approve/add it)."""
        pass

    def _is_cancellation(self, user_response: str) -> bool:
        """Check if user wants to cancel (no/cancel/nevermind)."""
        pass

    def _extract_edits(self, user_response: str) -> Optional[Dict[str, str]]:
        """Extract field edits from user response (e.g., 'change title to X')."""
        pass
```

**Implementation Notes**:
- Uses regex to parse `/US [description]` command
- Maintains conversation state in UserStoryDraftManager (indexed by session_id)
- Handles three types of user responses: confirmation, cancellation, edits
- Uses plain language in responses (no "US-XXX", say "the email notification feature")

### Component 2: UserStoryDraftManager

**Responsibility**: Manage user story draft state during validation workflow

**Interface**:
```python
@dataclass
class UserStoryDraft:
    """User story draft awaiting validation."""
    id: str  # Will become US-XXX after validation
    title: str
    description: str
    as_a: Optional[str] = None
    i_want: Optional[str] = None
    so_that: Optional[str] = None
    estimated_effort: Optional[str] = None
    business_value: Optional[str] = None
    status: str = "📝 PLANNED"
    created_at: datetime = None


class UserStoryDraftManager:
    """
    Manages user story drafts awaiting validation.

    Stores drafts in memory (session-scoped) during validation workflow.
    """

    def __init__(self):
        """Initialize draft storage."""
        self._drafts: Dict[str, UserStoryDraft] = {}

    def store_draft(self, session_id: str, draft: UserStoryDraft) -> None:
        """Store draft for session."""
        pass

    def get_draft(self, session_id: str) -> Optional[UserStoryDraft]:
        """Retrieve draft for session."""
        pass

    def update_draft(self, session_id: str, edits: Dict[str, str]) -> bool:
        """Apply edits to draft."""
        pass

    def clear_draft(self, session_id: str) -> None:
        """Clear draft after validation or cancellation."""
        pass

    def format_for_review(self, draft: UserStoryDraft) -> str:
        """
        Format draft as human-readable text for user review.

        Returns:
            Formatted string showing draft fields

        Example:
            "I've drafted a user story based on your input:

            Title: Email Notification System
            Description: Add email notifications when daemon finishes tasks

            As a: Project manager
            I want: Email notifications for daemon task completion
            So that: I can stay informed without checking the dashboard

            Estimated Effort: 2-3 days
            Business Value: ⭐⭐⭐ (Medium)

            Does this look correct? You can:
            - Approve: 'Yes, add it'
            - Edit: 'Change title to...' or 'Effort should be...'
            - Cancel: 'No, cancel'"
        """
        pass
```

**Implementation Notes**:
- Drafts stored in memory (no database needed for MVP)
- Session-scoped storage (cleared on confirmation/cancellation)
- format_for_review() uses plain language, easy-to-read format
- Supports partial drafts (some fields may be None if AI couldn't extract)

### Component 3: AIService Enhancement

**Responsibility**: Add user story extraction capability to existing AIService

**New Method**:
```python
class AIService:
    """Existing AIService class - ADD this method."""

    def extract_user_story(self, description: str) -> UserStoryDraft:
        """
        Extract user story structure from natural language description.

        Args:
            description: Natural language description of what user wants

        Returns:
            UserStoryDraft with extracted fields

        Raises:
            ValueError: If description is empty or invalid
            AIServiceError: If Claude API call fails

        Example:
            >>> service.extract_user_story("I want email notifications when daemon finishes")
            UserStoryDraft(
                id="DRAFT",
                title="Email Notification System",
                description="Add email notifications...",
                as_a="Project manager",
                i_want="Email notifications for daemon task completion",
                so_that="I can stay informed without checking the dashboard",
                estimated_effort="2-3 days",
                business_value="⭐⭐⭐"
            )
        """
        # Use centralized prompt
        prompt = load_prompt(PromptNames.EXTRACT_USER_STORY, {
            "DESCRIPTION": description
        })

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response into UserStoryDraft
        # (Claude returns structured JSON with extracted fields)
        extracted = self._parse_user_story_response(response.content[0].text)

        return UserStoryDraft(**extracted)
```

**Implementation Notes**:
- Uses new centralized prompt: `.claude/commands/extract-user-story.md`
- Claude returns structured JSON with extracted fields
- Gracefully handles missing fields (returns None for unextractable fields)
- Validates extracted title is meaningful (not empty, > 5 chars)

### Component 4: RoadmapEditor Enhancement

**Responsibility**: Add method to append user story to ROADMAP

**New Method**:
```python
class RoadmapEditor:
    """Existing RoadmapEditor class - ADD this method."""

    def add_user_story(self, draft: UserStoryDraft) -> str:
        """
        Add user story to ROADMAP.md.

        Args:
            draft: Validated user story draft

        Returns:
            Assigned user story ID (e.g., "US-025")

        Raises:
            IOError: If ROADMAP update fails

        Example:
            >>> editor.add_user_story(draft)
            "US-025"
        """
        # 1. Assign next US-XXX ID
        next_id = self._get_next_user_story_id()

        # 2. Format user story in ROADMAP markdown format
        us_markdown = self._format_user_story(draft, next_id)

        # 3. Append to ROADMAP under appropriate section
        # (default: "## 📝 PLANNED" section)
        self._append_to_section("## 📝 PLANNED", us_markdown)

        # 4. Create backup and write atomically
        self._atomic_write()

        return next_id

    def _get_next_user_story_id(self) -> str:
        """Find next available US-XXX identifier."""
        # Scan ROADMAP for existing US-XXX IDs
        # Return US-{max+1}
        pass

    def _format_user_story(self, draft: UserStoryDraft, us_id: str) -> str:
        """Format user story as ROADMAP markdown."""
        # Returns formatted markdown like:
        # ## 📝 PLANNED: US-025 - Email Notification System
        # **Status**: 📝 **PLANNED**
        # **As a**: Project manager
        # **I want**: Email notifications...
        # ...
        pass
```

**Implementation Notes**:
- Scans existing ROADMAP to find highest US-XXX number
- Formats according to ROADMAP conventions (status, as a/i want/so that, etc.)
- Uses atomic write with backup (existing RoadmapEditor pattern)
- Adds to "📝 PLANNED" section by default

---

## Data Structures

### UserStoryDraft
```python
@dataclass
class UserStoryDraft:
    """User story draft awaiting validation."""
    id: str  # "DRAFT" until validated, then "US-XXX"
    title: str  # Required - extracted from description
    description: str  # Required - user's input

    # User story format fields (optional)
    as_a: Optional[str] = None  # "As a [role]"
    i_want: Optional[str] = None  # "I want [capability]"
    so_that: Optional[str] = None  # "So that [benefit]"

    # Metadata fields (optional)
    estimated_effort: Optional[str] = None  # e.g., "2-3 days"
    business_value: Optional[str] = None  # e.g., "⭐⭐⭐⭐"
    status: str = "📝 PLANNED"  # Always PLANNED for new stories
    created_at: datetime = field(default_factory=datetime.now)
```

### ConversationState
```python
@dataclass
class ConversationState:
    """Conversation state for /US command."""
    session_id: str
    stage: str  # "awaiting_validation" | "completed" | "cancelled"
    draft: Optional[UserStoryDraft] = None
    created_at: datetime = field(default_factory=datetime.now)
```

---

## API Definitions

### ChatInterface Integration

**New Command Registration**:
```python
# In ChatInterface.__init__()
self.commands = {
    "/help": self.show_help,
    "/status": self.show_status,
    "/roadmap": self.show_roadmap,
    "/US": self.handle_user_story_command,  # NEW
    # ... existing commands
}
```

**New Method**:
```python
def handle_user_story_command(self, args: str, session_id: str) -> str:
    """
    Handle /US command for user story creation.

    Args:
        args: Command arguments (description)
        session_id: Current chat session ID

    Returns:
        Response message to user
    """
    # Delegate to UserStoryCommandHandler
    return self.us_handler.handle_command(f"/US {args}", session_id)
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/unit/test_user_story_command_handler.py`

**Test Cases**:
1. `test_parse_us_command_valid()` - Extracts description from "/US I want X"
2. `test_parse_us_command_empty()` - Handles "/US" with no description
3. `test_is_confirmation()` - Detects "yes", "add it", "approve", etc.
4. `test_is_cancellation()` - Detects "no", "cancel", "nevermind", etc.
5. `test_extract_edits()` - Parses "change title to X" instructions
6. `test_handle_command_success()` - Full flow: extract → present draft
7. `test_handle_validation_confirmed()` - User confirms → add to ROADMAP
8. `test_handle_validation_cancelled()` - User cancels → clear draft
9. `test_handle_validation_edited()` - User edits → update draft → present again

**Test File**: `tests/unit/test_user_story_draft_manager.py`

**Test Cases**:
1. `test_store_draft()` - Stores draft for session
2. `test_get_draft_existing()` - Retrieves stored draft
3. `test_get_draft_missing()` - Returns None for unknown session
4. `test_update_draft()` - Applies edits to draft
5. `test_clear_draft()` - Clears draft from storage
6. `test_format_for_review()` - Formats draft as readable text

**Test File**: `tests/unit/test_ai_service_user_story.py`

**Test Cases**:
1. `test_extract_user_story_complete()` - All fields extracted
2. `test_extract_user_story_partial()` - Some fields missing
3. `test_extract_user_story_empty_description()` - Raises ValueError
4. `test_extract_user_story_api_error()` - Handles Claude API failure

**Test File**: `tests/unit/test_roadmap_editor_user_story.py`

**Test Cases**:
1. `test_add_user_story()` - Adds to ROADMAP, returns US-XXX ID
2. `test_get_next_user_story_id()` - Increments from max existing
3. `test_format_user_story()` - Correct markdown format
4. `test_add_user_story_backup_created()` - Backup file exists

### Integration Tests

**Test File**: `tests/integration/test_us_command_workflow.py`

**Test Cases**:
1. `test_us_command_end_to_end()` - Full workflow: /US → extract → validate → add
2. `test_us_command_with_edits()` - User requests title change → re-validate → add
3. `test_us_command_cancellation()` - User cancels mid-workflow
4. `test_us_command_malformed_input()` - Handles gibberish input gracefully
5. `test_us_command_ai_service_down()` - Fallback when Claude API unavailable

### Manual Testing

**Scenario 1: Happy Path**
```
User: /US I want email notifications when the daemon finishes tasks

PM: I've drafted a user story based on your input:

    Title: Email Notification System
    Description: Add email notifications when daemon finishes tasks

    As a: Project manager
    I want: To receive email notifications when the daemon completes tasks
    So that: I can stay informed without constantly checking the dashboard

    Estimated Effort: 2-3 days
    Business Value: ⭐⭐⭐

    Does this look correct? You can:
    - Approve: 'Yes, add it'
    - Edit: 'Change title to...'
    - Cancel: 'No, cancel'

User: Yes, add it

PM: Great! I've added the email notification feature to the ROADMAP as US-025.
```

**Scenario 2: Edit Title**
```
User: /US Build a dashboard for monitoring agent activity

PM: [Presents draft with title "Agent Activity Dashboard"]

User: Change the title to "Real-Time Agent Monitoring Dashboard"

PM: Updated! Here's the revised draft:

    Title: Real-Time Agent Monitoring Dashboard
    [... rest of draft ...]

    Does this look correct?

User: Perfect, add it

PM: Great! I've added the real-time monitoring dashboard to the ROADMAP as US-026.
```

**Scenario 3: Cancellation**
```
User: /US Add support for PostgreSQL

PM: [Presents draft]

User: Actually, nevermind, we're using SQLite

PM: No problem! I've cancelled the draft. Let me know if you need anything else.
```

---

## Rollout Plan

### Phase 1: Core Extraction (3-4 hours)

**Goal**: Implement basic /US command with AI extraction

**Timeline**: Day 1

**Tasks**:
1. Create `UserStoryCommandHandler` class (1 hour)
2. Create `UserStoryDraftManager` class (1 hour)
3. Add `AIService.extract_user_story()` method (1 hour)
4. Create `.claude/commands/extract-user-story.md` prompt (30 min)
5. Write unit tests for extraction logic (30 min)

**Success Criteria**:
- `/US [description]` parsed correctly
- Claude API extracts title, description, as a/i want/so that
- Draft stored in session state

### Phase 2: Validation Workflow (3-4 hours)

**Goal**: Implement user validation and editing

**Timeline**: Day 1-2

**Tasks**:
1. Implement `handle_validation_response()` logic (1.5 hours)
2. Add edit parsing (`_extract_edits()`) (1 hour)
3. Implement `UserStoryDraftManager.update_draft()` (30 min)
4. Format draft for review (`format_for_review()`) (30 min)
5. Write unit tests for validation workflow (1 hour)

**Success Criteria**:
- User can confirm draft → triggers ROADMAP update
- User can edit fields → draft updated → re-presented
- User can cancel → draft cleared

### Phase 3: ROADMAP Integration (2-3 hours)

**Goal**: Add validated stories to ROADMAP.md

**Timeline**: Day 2

**Tasks**:
1. Implement `RoadmapEditor.add_user_story()` (1 hour)
2. Implement `_get_next_user_story_id()` (30 min)
3. Implement `_format_user_story()` markdown generation (30 min)
4. Write unit tests for ROADMAP integration (1 hour)

**Success Criteria**:
- Validated draft added to ROADMAP under "📝 PLANNED"
- Next US-XXX ID assigned correctly
- Backup created before write
- Markdown format matches existing user stories

### Phase 4: ChatInterface Integration (1-2 hours)

**Goal**: Integrate /US command into project_manager chat

**Timeline**: Day 2

**Tasks**:
1. Register `/US` command in ChatInterface (15 min)
2. Wire up UserStoryCommandHandler (15 min)
3. Handle conversation state across messages (30 min)
4. Write integration tests (1 hour)

**Success Criteria**:
- `/US` command available in project_manager chat
- Multi-turn conversation works (draft → validation → add)
- Session state maintained correctly

### Phase 5: Testing & Polish (2 hours)

**Goal**: End-to-end testing and error handling

**Timeline**: Day 2-3

**Tasks**:
1. Manual testing of all scenarios (1 hour)
2. Add error handling for edge cases (30 min)
3. Improve user-facing messages (plain language) (30 min)

**Success Criteria**:
- All manual test scenarios pass
- Error messages are user-friendly
- No technical jargon in user-facing messages

---

## Risks & Mitigations

### Risk 1: AI Extraction Quality

**Description**: Claude may extract incorrect or incomplete information from vague descriptions

**Likelihood**: Medium

**Impact**: Medium (user must manually correct, adds friction)

**Mitigation**:
- Use high-quality extraction prompt with examples
- Allow users to edit any field before confirmation
- Show draft for validation (user can catch errors)
- Collect feedback to improve prompt over time

### Risk 2: Session State Loss

**Description**: In-memory session state lost if PM process restarts

**Likelihood**: Low

**Impact**: Low (user just re-runs /US command)

**Mitigation**:
- Accept as acceptable risk for MVP (simple recovery: re-run command)
- Document in user help: "If draft is lost, re-run /US command"
- Future: persist to SQLite if becomes pain point

### Risk 3: Duplicate User Story IDs

**Description**: Concurrent /US commands might assign same US-XXX ID

**Likelihood**: Very Low (single-user system)

**Impact**: Medium (ROADMAP corruption)

**Mitigation**:
- Use file locking in RoadmapEditor (already exists)
- Read ROADMAP fresh before assigning ID
- Future: use database for ID generation if multi-user

### Risk 4: Claude API Unavailable

**Description**: Claude API down prevents /US command from working

**Likelihood**: Low

**Impact**: High (feature unusable)

**Mitigation**:
- Graceful error message: "AI service unavailable, please try again"
- Future: fallback to template-based manual entry
- Log errors for debugging

---

## Observability

### Metrics

Metrics to track:
- `us_command.extraction_success_rate` (gauge) - % of successful AI extractions
- `us_command.extraction_latency` (histogram) - Time to extract user story
- `us_command.validation_confirmed` (counter) - # of drafts confirmed
- `us_command.validation_cancelled` (counter) - # of drafts cancelled
- `us_command.validation_edited` (counter) - # of drafts edited
- `us_command.roadmap_updates` (counter) - # of stories added to ROADMAP

### Logs

Logs to emit:
- INFO: /US command received (user input)
- INFO: User story extracted (draft fields)
- INFO: Draft presented for validation (session_id)
- INFO: User confirmed draft (session_id, US-XXX ID)
- INFO: User edited draft (session_id, edited fields)
- INFO: User cancelled draft (session_id)
- INFO: User story added to ROADMAP (US-XXX ID, title)
- ERROR: AI extraction failed (error message)
- ERROR: ROADMAP update failed (error message)

---

## Documentation

### User Documentation

**Update**: `docs/TUTORIALS.md` - Add section on /US command

**Content**:
```markdown
## Creating User Stories with Natural Language

The `/US` command lets you create user stories conversationally:

1. Describe what you want:
   `/US I want email notifications when the daemon finishes tasks`

2. Review the draft the PM creates

3. Approve, edit, or cancel:
   - "Yes, add it" → adds to ROADMAP
   - "Change title to X" → edits draft
   - "Cancel" → discards draft
```

### Developer Documentation

**Create**: `docs/architecture/USER_STORY_COMMAND.md`

**Content**:
- Architecture diagram
- Component responsibilities
- Workflow diagram (extract → validate → propagate)
- Code examples for extending

---

## Security Considerations

1. **Input Validation**: Sanitize user input before sending to Claude API (no code injection)
2. **ROADMAP Integrity**: Use RoadmapEditor's atomic write with backups
3. **Session Isolation**: Draft for session A not visible to session B
4. **API Key Security**: Claude API key stored in environment variable (existing pattern)
5. **Rate Limiting**: Respect Claude API rate limits (existing in AIService)

---

## Cost Estimate

**Development**:
- Phase 1: 3-4 hours (core extraction)
- Phase 2: 3-4 hours (validation workflow)
- Phase 3: 2-3 hours (ROADMAP integration)
- Phase 4: 1-2 hours (ChatInterface integration)
- Phase 5: 2 hours (testing & polish)
- **Total**: 11-15 hours (~1.5-2 days)

**Infrastructure**:
- Claude API costs: ~$0.01 per user story extraction (minimal)

**Ongoing**:
- Maintenance: 1 hour/month (monitor extraction quality)
- Prompt tuning: 2 hours/quarter (improve based on feedback)

---

## Future Enhancements

Phase 2+ Enhancements (not in scope):
1. Multi-turn conversation memory (context from previous messages)
2. Similarity detection (check for duplicate user stories)
3. Automatic DoD inference (US-013)
4. Prioritization suggestions based on business value
5. Template library for common user story types
6. Export to external tools (Jira, Linear, etc.)

---

## References

- US-012: `/US` Command with Conversational Validation Workflow (ROADMAP.md line 1129)
- COLLABORATION_METHODOLOGY.md Section 4.6: Plain language guidelines
- Existing AIService: `coffee_maker/cli/ai_service.py`
- Existing RoadmapEditor: `coffee_maker/cli/roadmap_editor.py`
- Existing ChatInterface: `coffee_maker/cli/chat_interface.py`
- Centralized Prompts: `.claude/commands/`

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created | architect |
| 2025-10-19 | Status: Draft | architect |

---

## Approval

Who needs to approve this spec?

- [ ] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (strategic alignment)
- [ ] User (final approval)

**Approval Date**: TBD

---

**Estimated Implementation Time**: 11-15 hours (1.5-2 days)
