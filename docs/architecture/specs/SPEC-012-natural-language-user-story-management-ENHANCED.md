# SPEC-012: Natural Language User Story Management (ENHANCED)

**Status**: Draft - Enhanced Technical Specification

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-012 - `/US` Command with Conversational Validation Workflow

**Related ADRs**: ADR-006 (Centralized Error Handling), ADR-013 (Dependency Management)

**Assigned To**: code_developer

**Complexity**: High (Multi-component integration, AI-driven workflow, conversational state management)

**Estimated Effort**: 15-20 hours (2-3 days)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Requirements](#requirements)
4. [Proposed Solution](#proposed-solution)
5. [Detailed Design](#detailed-design)
6. [Data Flow & Sequence Diagrams](#data-flow--sequence-diagrams)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Security Considerations](#security-considerations)
10. [Performance Requirements](#performance-requirements)
11. [Risk Analysis](#risk-analysis)
12. [Success Criteria](#success-criteria)
13. [Rollout Plan](#rollout-plan)

---

## Executive Summary

This specification describes the comprehensive technical design for implementing a natural language `/US` command that enables users to create user stories conversationally with project_manager. The system will:

- Extract structured user story components from freeform natural language input using Claude AI
- Present an interactive draft for validation through a conversational workflow
- Support iterative refinement (title changes, effort adjustments, description edits)
- Only propagate to ROADMAP.md after explicit user confirmation
- Maintain conversation state across multiple turns
- Provide intelligent error handling and graceful degradation

**Key Innovation**: This implements a "share ideas → validate → propagate" workflow, NOT immediate addition to the roadmap. This ensures quality control and user alignment before documentation.

**Business Value**: Reduces friction in user story creation from 5-10 minutes (manual formatting) to 30-60 seconds (natural language conversation), increasing roadmap quality and user engagement.

---

## Problem Statement

### Current Situation

Users currently must manually format user stories following the ROADMAP structure:
- **As a**: [role]
- **I want**: [capability]
- **So that**: [benefit]
- **Estimated Effort**: [time]
- **Business Value**: [stars]
- **Status**: [emoji + text]

This process is:
- **Time-consuming**: 5-10 minutes per user story
- **Error-prone**: Inconsistent formatting, missing fields
- **Friction-heavy**: Requires knowledge of ROADMAP markdown conventions
- **Discourages quick capture**: Users delay documenting ideas due to formatting overhead
- **Reduces collaboration**: User must context-switch from conversation to documentation mode

### Goal

Implement a natural language `/US` command that:
1. Accepts freeform user input describing what they want (e.g., "I want email notifications when tasks complete")
2. Extracts structured user story components using Claude AI
3. Presents a formatted draft for user validation
4. Supports iterative refinement through conversation
5. Only adds to ROADMAP after explicit user approval
6. Assigns next available US-XXX identifier automatically
7. Maintains conversation state across multiple turns

### Non-Goals (Out of Scope for US-012)

- ❌ DoD (Definition of Done) inference → US-013 (separate spec)
- ❌ Similarity detection and duplicate prevention → US-013
- ❌ Automatic prioritization based on dependencies → US-014
- ❌ Multi-turn conversation memory across sessions (sessions only, not persistent)
- ❌ Integration with external tools (Jira, Linear, etc.)

### Success Metrics

- **Time Reduction**: User story creation time reduced from 5-10 min → 30-60 sec
- **Extraction Accuracy**: ≥85% of title/description correctly identified by AI
- **User Satisfaction**: ≥4/5 rating for workflow ease of use
- **Adoption Rate**: ≥70% of new user stories created via `/US` command within 1 month

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-1 | Accept `/US [description]` command in project_manager chat | P0 | Command parsed correctly, description extracted |
| FR-2 | Extract user story title, description, and key requirements from natural language | P0 | ≥85% accuracy on title/description extraction |
| FR-3 | Present structured user story draft with all standard fields | P0 | Draft includes: title, description, as a/i want/so that, effort, business value |
| FR-4 | Wait for user validation/modification before adding to ROADMAP | P0 | No automatic ROADMAP updates without user confirmation |
| FR-5 | Support user edits to draft (title, description, effort estimate) | P0 | Users can say "change title to X" and draft updates |
| FR-6 | Add validated user story to ROADMAP only after user confirms | P0 | Confirmation triggers ROADMAP update with backup |
| FR-7 | Assign next available US-XXX identifier automatically | P0 | IDs assigned sequentially without gaps or duplicates |
| FR-8 | Support cancellation at any stage | P1 | Users can say "cancel" and draft is cleared |
| FR-9 | Maintain conversation state within single session | P1 | Multiple turns tracked, state cleared after completion |
| FR-10 | Provide helpful error messages for malformed input | P1 | Plain language errors, no technical jargon |

### Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | AI extraction response time | < 3 seconds | 95th percentile latency |
| NFR-2 | Extraction accuracy | ≥ 85% | Title/description correctness (manual review) |
| NFR-3 | User-friendly error messages | 100% plain language | No stack traces or technical terms shown to user |
| NFR-4 | Graceful degradation if AI unavailable | Fallback message shown | User notified, can retry |
| NFR-5 | Conversation state maintained within session | 100% retention | State not lost during multi-turn conversation |
| NFR-6 | ROADMAP data integrity | Zero corruption | Atomic writes with backups |
| NFR-7 | Concurrent safety (multi-user future-proof) | File locking | No duplicate US-XXX IDs assigned |

### Constraints

- **Must** use existing `AIService` class (Claude API integration already available)
- **Must** use existing `RoadmapEditor` class for safe ROADMAP updates
- **Must** follow COLLABORATION_METHODOLOGY.md Section 4.6 (plain language, no technical shorthand)
- **Must** integrate with existing project_manager chat interface
- **Must** assign status as "📝 PLANNED" by default for new user stories
- **Must** use centralized prompts in `.claude/commands/`
- **Must** respect Claude API rate limits (managed by AIService)
- **Must** create backup before any ROADMAP modification

---

## Proposed Solution

### High-Level Approach

Implement a **three-phase conversational workflow**:

```
Phase 1: EXTRACT
User provides natural language input
    ↓
Claude AI extracts structured components
    ↓
Draft created in memory (session-scoped)

Phase 2: VALIDATE
Draft presented to user for review
    ↓
User responds: Confirm | Edit | Cancel
    ↓
If Edit: Apply changes and re-present
If Cancel: Clear draft and exit
If Confirm: Proceed to Phase 3

Phase 3: PROPAGATE
Assign next US-XXX ID
    ↓
Format as ROADMAP markdown
    ↓
Create backup of ROADMAP.md
    ↓
Atomically write to ROADMAP
    ↓
Confirm to user with US-XXX reference
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  USER (via project_manager chat)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ "/US I want email notifications"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ChatInterface (existing)                                   │
│  - Command routing                                          │
│  - Session management                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Delegates to new handler
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  UserStoryCommandHandler (NEW)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Responsibilities:                                    │   │
│  │ - Parse /US command                                 │   │
│  │ - Orchestrate workflow phases                       │   │
│  │ - Manage conversation state                         │   │
│  │ - Parse user validation responses                   │   │
│  │ - Apply edits to drafts                             │   │
│  └─────────────────────────────────────────────────────┘   │
└────────┬──────────────────────┬─────────────────────────────┘
         │                      │
         │ Extract              │ Propagate
         ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│  AIService          │  │  RoadmapEditor      │
│  (existing)         │  │  (existing)         │
│                     │  │                     │
│  .extract_user_     │  │  .add_user_story()  │
│   story()           │  │  .get_next_us_id()  │
│  (NEW METHOD)       │  │  (NEW METHOD)       │
└─────────────────────┘  └─────────────────────┘
         │                      │
         │ Returns              │ Updates
         ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│  UserStoryDraft     │  │  ROADMAP.md         │
│  (NEW dataclass)    │  │  + backup           │
└─────────────────────┘  └─────────────────────┘
         │
         │ Stored in
         ▼
┌─────────────────────────────────────────────────────────────┐
│  UserStoryDraftManager (NEW)                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Responsibilities:                                    │   │
│  │ - Store drafts in session (in-memory)               │   │
│  │ - Format drafts for user review                     │   │
│  │ - Apply user edits to drafts                        │   │
│  │ - Clear drafts after completion/cancellation        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Storage: Dict[session_id, UserStoryDraft]                 │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| AI Extraction | Claude API (via AIService) | Already integrated, high accuracy |
| ROADMAP Updates | RoadmapEditor class | Atomic writes, backups, validation |
| State Management | In-memory Dict (session-scoped) | Simple, sufficient for MVP |
| Conversation | ChatInterface | Existing project_manager chat |
| Prompts | Centralized (`.claude/commands/`) | Consistency, versioning, reusability |
| Data Classes | Python `dataclass` | Type safety, auto-generated methods |

---

## Detailed Design

### Component 1: UserStoryCommandHandler

**Location**: `coffee_maker/cli/user_story_command_handler.py` (NEW FILE)

**Responsibility**: Orchestrate the `/US` command workflow from extraction through validation to propagation.

**Full Interface**:

```python
"""User Story Command Handler - Natural language user story creation.

This module handles the /US command workflow:
1. Parse /US [description] command
2. Extract user story structure via AIService
3. Present draft for validation
4. Handle user edits/confirmation
5. Propagate to ROADMAP via RoadmapEditor

Example:
    >>> from coffee_maker.cli.user_story_command_handler import UserStoryCommandHandler
    >>> from coffee_maker.cli.ai_service import AIService
    >>> from coffee_maker.cli.roadmap_editor import RoadmapEditor
    >>>
    >>> handler = UserStoryCommandHandler(
    ...     ai_service=AIService(),
    ...     roadmap_editor=RoadmapEditor(ROADMAP_PATH)
    ... )
    >>> response = handler.handle_command(
    ...     user_input="/US I want email notifications",
    ...     session_id="session-123"
    ... )
    >>> print(response)
"""

import logging
import re
from typing import Dict, Optional

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.user_story_draft_manager import (
    UserStoryDraft,
    UserStoryDraftManager,
)

logger = logging.getLogger(__name__)


class UserStoryCommandHandler:
    """
    Handles /US command for natural language user story creation.

    Workflow:
    1. Parse /US [description] from user input
    2. Call AIService to extract user story structure
    3. Present draft to user for validation
    4. Handle user edits/confirmation
    5. Propagate to ROADMAP via RoadmapEditor

    Attributes:
        ai_service: AIService instance for Claude API calls
        roadmap_editor: RoadmapEditor instance for safe ROADMAP updates
        draft_manager: UserStoryDraftManager instance for session state

    Example:
        >>> handler = UserStoryCommandHandler(ai_service, roadmap_editor)
        >>> response = handler.handle_command(
        ...     "/US I want email notifications when daemon finishes",
        ...     "session-123"
        ... )
    """

    # Confirmation patterns (case-insensitive)
    CONFIRMATION_PATTERNS = [
        r"^yes\b",
        r"^yep\b",
        r"^yeah\b",
        r"^sure\b",
        r"^ok\b",
        r"^okay\b",
        r"\badd it\b",
        r"\bcreate it\b",
        r"\bapprove\b",
        r"\blooks good\b",
        r"\bperfect\b",
        r"\bcorrect\b",
    ]

    # Cancellation patterns (case-insensitive)
    CANCELLATION_PATTERNS = [
        r"^no\b",
        r"^nope\b",
        r"\bcancel\b",
        r"\bnevermind\b",
        r"\bnever mind\b",
        r"\bdiscard\b",
        r"\babort\b",
    ]

    # Edit patterns (case-insensitive)
    EDIT_PATTERNS = {
        "title": r"(?:change|update|set|make)\s+(?:the\s+)?title\s+(?:to\s+)?['\"]?(.+?)['\"]?$",
        "description": r"(?:change|update|set)\s+(?:the\s+)?description\s+(?:to\s+)?['\"]?(.+?)['\"]?$",
        "effort": r"(?:change|update|set)\s+(?:the\s+)?(?:effort|estimate|duration)\s+(?:to\s+)?['\"]?(.+?)['\"]?$",
        "business_value": r"(?:change|update|set)\s+(?:the\s+)?(?:value|business value)\s+(?:to\s+)?['\"]?(.+?)['\"]?$",
    }

    def __init__(self, ai_service: AIService, roadmap_editor: RoadmapEditor):
        """Initialize UserStoryCommandHandler.

        Args:
            ai_service: AIService instance for Claude API calls
            roadmap_editor: RoadmapEditor instance for ROADMAP updates
        """
        self.ai_service = ai_service
        self.roadmap_editor = roadmap_editor
        self.draft_manager = UserStoryDraftManager()

        logger.info("UserStoryCommandHandler initialized")

    def handle_command(self, user_input: str, session_id: str) -> str:
        """
        Handle /US command from user.

        This is the entry point for new /US commands. It parses the command,
        extracts the user story via AIService, and presents a draft for validation.

        Args:
            user_input: User's input (e.g., "/US I want email notifications")
            session_id: Chat session identifier for state management

        Returns:
            Response message to user (draft presentation)

        Raises:
            ValueError: If command format is invalid or description is empty
            AIServiceError: If Claude API call fails

        Example:
            >>> handler.handle_command("/US I want email notifications", "session-123")
            "I've drafted a user story based on your input:\n\n..."
        """
        logger.info(f"Handling /US command for session {session_id}")

        # Parse command to extract description
        description = self._parse_us_command(user_input)
        if not description:
            return (
                "I need a description to create a user story. "
                "Try: `/US I want to be able to [description]`"
            )

        logger.debug(f"Extracted description: {description}")

        try:
            # Extract user story structure via AI
            draft = self.ai_service.extract_user_story(description)
            logger.info(f"User story extracted: {draft.title}")

            # Store draft in session
            self.draft_manager.store_draft(session_id, draft)

            # Format for user review
            return self.draft_manager.format_for_review(draft)

        except Exception as e:
            logger.error(f"Failed to extract user story: {e}", exc_info=True)
            return (
                f"I encountered an error while analyzing your description: {str(e)}\n\n"
                "Please try rephrasing or check that the AI service is available."
            )

    def handle_validation_response(self, user_response: str, session_id: str) -> str:
        """
        Handle user's response to draft validation.

        This handles the user's response after a draft is presented. The user can:
        - Confirm: Add to ROADMAP
        - Cancel: Discard draft
        - Edit: Update specific fields

        Args:
            user_response: User's validation response
            session_id: Chat session identifier

        Returns:
            Response message (confirmation, further questions, or error)

        Raises:
            ValueError: If no draft exists for session

        Example:
            >>> handler.handle_validation_response("Yes, add it", "session-123")
            "Great! I've added the email notification feature to the ROADMAP as US-025."
        """
        logger.info(f"Handling validation response for session {session_id}")

        # Retrieve draft from session
        draft = self.draft_manager.get_draft(session_id)
        if not draft:
            return (
                "I don't have a user story draft for you to validate. "
                "Start by using `/US [description]` to create one."
            )

        # Check if user is confirming
        if self._is_confirmation(user_response):
            logger.info(f"User confirmed draft for session {session_id}")
            return self._propagate_to_roadmap(draft, session_id)

        # Check if user is cancelling
        if self._is_cancellation(user_response):
            logger.info(f"User cancelled draft for session {session_id}")
            self.draft_manager.clear_draft(session_id)
            return "No problem! I've cancelled the draft. Let me know if you need anything else."

        # Check if user is editing
        edits = self._extract_edits(user_response)
        if edits:
            logger.info(f"User requested edits for session {session_id}: {edits}")
            self.draft_manager.update_draft(session_id, edits)
            updated_draft = self.draft_manager.get_draft(session_id)
            return (
                "Updated! Here's the revised draft:\n\n"
                + self.draft_manager.format_for_review(updated_draft)
            )

        # Unrecognized response
        return (
            "I'm not sure what you'd like to do. You can:\n"
            "- Approve: 'Yes, add it'\n"
            "- Edit: 'Change title to...' or 'Effort should be...'\n"
            "- Cancel: 'No, cancel'"
        )

    def _parse_us_command(self, user_input: str) -> Optional[str]:
        """
        Extract description from /US command.

        Args:
            user_input: Raw user input (e.g., "/US I want email notifications")

        Returns:
            Description text (after "/US "), or None if invalid

        Example:
            >>> self._parse_us_command("/US I want email notifications")
            "I want email notifications"
        """
        # Match /US followed by whitespace and capture everything after
        match = re.match(r"^/US\s+(.+)$", user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _is_confirmation(self, user_response: str) -> bool:
        """
        Check if user response is confirmation (yes/approve/add it).

        Args:
            user_response: User's response text

        Returns:
            True if response matches confirmation pattern

        Example:
            >>> self._is_confirmation("Yes, add it")
            True
            >>> self._is_confirmation("Change the title")
            False
        """
        user_response_lower = user_response.lower()
        return any(
            re.search(pattern, user_response_lower)
            for pattern in self.CONFIRMATION_PATTERNS
        )

    def _is_cancellation(self, user_response: str) -> bool:
        """
        Check if user wants to cancel (no/cancel/nevermind).

        Args:
            user_response: User's response text

        Returns:
            True if response matches cancellation pattern

        Example:
            >>> self._is_cancellation("No, cancel")
            True
            >>> self._is_cancellation("Yes, add it")
            False
        """
        user_response_lower = user_response.lower()
        return any(
            re.search(pattern, user_response_lower)
            for pattern in self.CANCELLATION_PATTERNS
        )

    def _extract_edits(self, user_response: str) -> Optional[Dict[str, str]]:
        """
        Extract field edits from user response.

        Parses responses like:
        - "Change title to Real-Time Dashboard"
        - "Set effort to 3-4 days"
        - "Update business value to 5 stars"

        Args:
            user_response: User's response text

        Returns:
            Dict of field edits, or None if no edits detected

        Example:
            >>> self._extract_edits("Change title to Real-Time Dashboard")
            {"title": "Real-Time Dashboard"}
        """
        edits = {}
        user_response_lower = user_response.lower()

        for field, pattern in self.EDIT_PATTERNS.items():
            match = re.search(pattern, user_response_lower, re.IGNORECASE)
            if match:
                edits[field] = match.group(1).strip()

        return edits if edits else None

    def _propagate_to_roadmap(self, draft: UserStoryDraft, session_id: str) -> str:
        """
        Propagate validated draft to ROADMAP.md.

        This is Phase 3 of the workflow. It:
        1. Assigns next US-XXX ID
        2. Adds to ROADMAP via RoadmapEditor
        3. Clears session draft
        4. Returns confirmation message

        Args:
            draft: Validated user story draft
            session_id: Chat session identifier

        Returns:
            Confirmation message with US-XXX ID

        Raises:
            IOError: If ROADMAP update fails
        """
        try:
            # Assign next US-XXX ID and add to ROADMAP
            us_id = self.roadmap_editor.add_user_story(draft)
            logger.info(f"User story added to ROADMAP: {us_id} - {draft.title}")

            # Clear draft from session
            self.draft_manager.clear_draft(session_id)

            # Return user-friendly confirmation (plain language, not "US-XXX")
            return (
                f"Great! I've added the {draft.title.lower()} to the ROADMAP as {us_id}.\n\n"
                f"You can see it in the roadmap now. Want to create another user story?"
            )

        except Exception as e:
            logger.error(f"Failed to add user story to ROADMAP: {e}", exc_info=True)
            return (
                f"I encountered an error while adding to the ROADMAP: {str(e)}\n\n"
                "The draft is still saved. You can try again or check the ROADMAP file."
            )
```

**Key Design Decisions**:
1. **Regex patterns for parsing**: Simple, maintainable, covers common variations
2. **Plain language responses**: No "US-XXX" in user-facing messages (COLLABORATION_METHODOLOGY.md compliance)
3. **Defensive error handling**: All external calls wrapped in try/except with user-friendly errors
4. **Logging at INFO level**: All workflow stages logged for debugging
5. **Separation of concerns**: Command handler delegates to DraftManager for state, AIService for extraction, RoadmapEditor for persistence

---

### Component 2: UserStoryDraftManager

**Location**: `coffee_maker/cli/user_story_draft_manager.py` (NEW FILE)

**Responsibility**: Manage user story drafts in session state (in-memory storage).

**Full Interface**:

```python
"""User Story Draft Manager - Session-scoped draft storage.

This module manages user story drafts during the validation workflow.
Drafts are stored in memory (session-scoped) until validated or cancelled.

Example:
    >>> from coffee_maker.cli.user_story_draft_manager import (
    ...     UserStoryDraft,
    ...     UserStoryDraftManager
    ... )
    >>>
    >>> manager = UserStoryDraftManager()
    >>> draft = UserStoryDraft(
    ...     id="DRAFT",
    ...     title="Email Notifications",
    ...     description="Send emails when tasks complete"
    ... )
    >>> manager.store_draft("session-123", draft)
    >>> retrieved = manager.get_draft("session-123")
    >>> print(manager.format_for_review(retrieved))
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class UserStoryDraft:
    """
    User story draft awaiting validation.

    This represents a user story in draft state (not yet added to ROADMAP).
    It contains all fields that will eventually be written to ROADMAP.md.

    Attributes:
        id: Draft identifier ("DRAFT" until validated, then "US-XXX")
        title: User story title (required)
        description: User's original description (required)
        as_a: "As a [role]" (optional, AI-extracted)
        i_want: "I want [capability]" (optional, AI-extracted)
        so_that: "So that [benefit]" (optional, AI-extracted)
        estimated_effort: e.g., "2-3 days" (optional, AI-estimated)
        business_value: e.g., "⭐⭐⭐⭐" (optional, AI-estimated)
        status: Always "📝 PLANNED" for new stories
        created_at: Timestamp of draft creation

    Example:
        >>> draft = UserStoryDraft(
        ...     id="DRAFT",
        ...     title="Email Notification System",
        ...     description="I want email notifications when daemon finishes tasks",
        ...     as_a="Project manager",
        ...     i_want="Email notifications for daemon task completion",
        ...     so_that="I can stay informed without checking the dashboard",
        ...     estimated_effort="2-3 days",
        ...     business_value="⭐⭐⭐"
        ... )
    """

    id: str  # "DRAFT" until validated
    title: str  # Required - extracted from description
    description: str  # Required - user's input

    # User story format fields (optional - AI may not extract all)
    as_a: Optional[str] = None
    i_want: Optional[str] = None
    so_that: Optional[str] = None

    # Metadata fields (optional - AI estimates)
    estimated_effort: Optional[str] = None
    business_value: Optional[str] = None

    # Status (always PLANNED for new stories)
    status: str = "📝 PLANNED"

    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)


class UserStoryDraftManager:
    """
    Manages user story drafts awaiting validation.

    Stores drafts in memory (session-scoped) during validation workflow.
    Drafts are cleared after confirmation or cancellation.

    Attributes:
        _drafts: Dict mapping session_id to UserStoryDraft

    Example:
        >>> manager = UserStoryDraftManager()
        >>> draft = UserStoryDraft(id="DRAFT", title="Feature", description="...")
        >>> manager.store_draft("session-123", draft)
        >>> retrieved = manager.get_draft("session-123")
    """

    def __init__(self):
        """Initialize draft storage."""
        self._drafts: Dict[str, UserStoryDraft] = {}
        logger.debug("UserStoryDraftManager initialized")

    def store_draft(self, session_id: str, draft: UserStoryDraft) -> None:
        """
        Store draft for session.

        Args:
            session_id: Chat session identifier
            draft: UserStoryDraft to store

        Example:
            >>> manager.store_draft("session-123", draft)
        """
        self._drafts[session_id] = draft
        logger.debug(f"Draft stored for session {session_id}: {draft.title}")

    def get_draft(self, session_id: str) -> Optional[UserStoryDraft]:
        """
        Retrieve draft for session.

        Args:
            session_id: Chat session identifier

        Returns:
            UserStoryDraft if exists, None otherwise

        Example:
            >>> draft = manager.get_draft("session-123")
            >>> if draft:
            ...     print(draft.title)
        """
        draft = self._drafts.get(session_id)
        if draft:
            logger.debug(f"Draft retrieved for session {session_id}: {draft.title}")
        else:
            logger.debug(f"No draft found for session {session_id}")
        return draft

    def update_draft(self, session_id: str, edits: Dict[str, str]) -> bool:
        """
        Apply edits to draft.

        Args:
            session_id: Chat session identifier
            edits: Dict of field edits (e.g., {"title": "New Title"})

        Returns:
            True if successful, False if no draft exists

        Example:
            >>> manager.update_draft("session-123", {"title": "New Title"})
            True
        """
        draft = self._drafts.get(session_id)
        if not draft:
            logger.warning(f"Cannot update draft: no draft for session {session_id}")
            return False

        # Apply edits to draft
        for field, value in edits.items():
            if hasattr(draft, field):
                setattr(draft, field, value)
                logger.info(f"Updated draft field '{field}' for session {session_id}")
            else:
                logger.warning(f"Unknown field '{field}' in edit request")

        return True

    def clear_draft(self, session_id: str) -> None:
        """
        Clear draft after validation or cancellation.

        Args:
            session_id: Chat session identifier

        Example:
            >>> manager.clear_draft("session-123")
        """
        if session_id in self._drafts:
            draft_title = self._drafts[session_id].title
            del self._drafts[session_id]
            logger.info(f"Draft cleared for session {session_id}: {draft_title}")
        else:
            logger.debug(f"No draft to clear for session {session_id}")

    def format_for_review(self, draft: UserStoryDraft) -> str:
        """
        Format draft as human-readable text for user review.

        Args:
            draft: UserStoryDraft to format

        Returns:
            Formatted string showing draft fields in plain language

        Example:
            >>> print(manager.format_for_review(draft))
            I've drafted a user story based on your input:

            Title: Email Notification System
            Description: I want email notifications when daemon finishes tasks

            As a: Project manager
            I want: Email notifications for daemon task completion
            So that: I can stay informed without checking the dashboard

            Estimated Effort: 2-3 days
            Business Value: ⭐⭐⭐

            Does this look correct? You can:
            - Approve: 'Yes, add it'
            - Edit: 'Change title to...' or 'Effort should be...'
            - Cancel: 'No, cancel'
        """
        lines = [
            "I've drafted a user story based on your input:",
            "",
            f"**Title**: {draft.title}",
            f"**Description**: {draft.description}",
            "",
        ]

        # Add optional fields if present
        if draft.as_a:
            lines.append(f"**As a**: {draft.as_a}")
        if draft.i_want:
            lines.append(f"**I want**: {draft.i_want}")
        if draft.so_that:
            lines.append(f"**So that**: {draft.so_that}")

        lines.append("")  # Blank line

        if draft.estimated_effort:
            lines.append(f"**Estimated Effort**: {draft.estimated_effort}")
        if draft.business_value:
            lines.append(f"**Business Value**: {draft.business_value}")

        # Add instructions
        lines.extend([
            "",
            "Does this look correct? You can:",
            "- Approve: 'Yes, add it'",
            "- Edit: 'Change title to...' or 'Effort should be...'",
            "- Cancel: 'No, cancel'",
        ])

        return "\n".join(lines)
```

**Key Design Decisions**:
1. **In-memory storage**: Sufficient for MVP, no database needed
2. **Session-scoped**: Drafts isolated per session, automatic cleanup
3. **Plain language formatting**: Easy-to-read draft presentation
4. **Defensive field access**: `hasattr()` check before `setattr()` in `update_draft()`
5. **Comprehensive logging**: All operations logged for debugging

---

### Component 3: AIService Enhancement

**Location**: `coffee_maker/cli/ai_service.py` (EXISTING FILE - ADD METHOD)

**Responsibility**: Extract user story structure from natural language using Claude AI.

**New Method to Add**:

```python
# In coffee_maker/cli/ai_service.py, add this method to the AIService class:

from coffee_maker.cli.user_story_draft_manager import UserStoryDraft
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
import json


def extract_user_story(self, description: str) -> UserStoryDraft:
    """
    Extract user story structure from natural language description.

    This method uses Claude AI to analyze the user's natural language input
    and extract structured user story components:
    - Title
    - As a / I want / So that
    - Estimated effort
    - Business value

    Args:
        description: Natural language description of what user wants
            (e.g., "I want email notifications when daemon finishes tasks")

    Returns:
        UserStoryDraft with extracted fields

    Raises:
        ValueError: If description is empty or too short (< 5 characters)
        AIServiceError: If Claude API call fails

    Example:
        >>> service = AIService()
        >>> draft = service.extract_user_story(
        ...     "I want email notifications when daemon finishes tasks"
        ... )
        >>> print(draft.title)
        "Email Notification System"
        >>> print(draft.estimated_effort)
        "2-3 days"
    """
    # Validate input
    if not description or len(description.strip()) < 5:
        raise ValueError("Description must be at least 5 characters")

    logger.info(f"Extracting user story from: {description[:50]}...")

    try:
        # Load centralized prompt
        prompt = load_prompt(PromptNames.EXTRACT_USER_STORY, {
            "DESCRIPTION": description
        })

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response (Claude returns structured JSON)
        response_text = response.content[0].text
        extracted = self._parse_user_story_response(response_text)

        logger.info(f"User story extracted successfully: {extracted.get('title', 'N/A')}")

        # Create UserStoryDraft
        return UserStoryDraft(
            id="DRAFT",
            title=extracted.get("title", "Untitled User Story"),
            description=description,  # Original user input
            as_a=extracted.get("as_a"),
            i_want=extracted.get("i_want"),
            so_that=extracted.get("so_that"),
            estimated_effort=extracted.get("estimated_effort"),
            business_value=extracted.get("business_value"),
        )

    except Exception as e:
        logger.error(f"Failed to extract user story: {e}", exc_info=True)
        raise AIServiceError(f"User story extraction failed: {str(e)}")


def _parse_user_story_response(self, response_text: str) -> Dict[str, str]:
    """
    Parse Claude API response into structured dict.

    Claude is instructed to return JSON with extracted fields.
    This method parses that JSON and handles errors gracefully.

    Args:
        response_text: Raw Claude API response text (JSON string)

    Returns:
        Dict with extracted fields (keys: title, as_a, i_want, so_that, estimated_effort, business_value)

    Raises:
        ValueError: If response is not valid JSON or missing required fields

    Example:
        >>> response = '{"title": "Email Notifications", "as_a": "User", ...}'
        >>> parsed = self._parse_user_story_response(response)
        >>> print(parsed["title"])
        "Email Notifications"
    """
    try:
        # Parse JSON response
        data = json.loads(response_text)

        # Validate required field (title)
        if "title" not in data or not data["title"]:
            raise ValueError("Response missing required 'title' field")

        # Return extracted fields (optional fields may be None)
        return {
            "title": data.get("title"),
            "as_a": data.get("as_a"),
            "i_want": data.get("i_want"),
            "so_that": data.get("so_that"),
            "estimated_effort": data.get("estimated_effort"),
            "business_value": data.get("business_value"),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        raise ValueError(f"Invalid JSON response from Claude: {str(e)}")


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass
```

**Supporting Centralized Prompt**:

**Location**: `.claude/commands/extract-user-story.md` (NEW FILE)

```markdown
# Extract User Story from Natural Language

You are an expert product manager helping extract structured user stories from natural language descriptions.

## User Input
The user described what they want:

```
$DESCRIPTION
```

## Your Task
Extract the following structured information:

1. **Title**: A concise title (5-10 words) summarizing the user story
2. **As a**: The role/persona (e.g., "Project manager", "Developer", "User")
3. **I want**: The capability requested (start with verb: "to receive", "to see", "to track")
4. **So that**: The benefit/motivation (outcome or value)
5. **Estimated Effort**: Time estimate (e.g., "2-3 days", "1 week", "3-5 hours")
6. **Business Value**: Priority rating using stars (⭐ to ⭐⭐⭐⭐⭐)

## Output Format
Return ONLY valid JSON with these fields:

```json
{
  "title": "Concise title (5-10 words)",
  "as_a": "Role or persona",
  "i_want": "Capability requested (start with verb)",
  "so_that": "Benefit or motivation",
  "estimated_effort": "Time estimate",
  "business_value": "⭐⭐⭐⭐" (1-5 stars)
}
```

## Guidelines
- **Title**: Make it descriptive but concise (e.g., "Email Notification System", "Real-Time Agent Dashboard")
- **As a**: Infer from context (default to "User" if unclear)
- **I want**: Extract the core capability, use infinitive verb form
- **So that**: Explain the benefit/value (why is this needed?)
- **Effort**: Estimate based on complexity (simple=hours, medium=days, complex=weeks)
- **Value**:
  - ⭐⭐⭐⭐⭐ (Critical - blocks other work or high user value)
  - ⭐⭐⭐⭐ (High - significant value)
  - ⭐⭐⭐ (Medium - useful but not urgent)
  - ⭐⭐ (Low - nice to have)
  - ⭐ (Very low - minimal value)

## Examples

### Example 1
Input: "I want email notifications when the daemon finishes tasks"

Output:
```json
{
  "title": "Email Notification System",
  "as_a": "Project manager",
  "i_want": "To receive email notifications when the daemon completes tasks",
  "so_that": "I can stay informed without constantly checking the dashboard",
  "estimated_effort": "2-3 days",
  "business_value": "⭐⭐⭐⭐"
}
```

### Example 2
Input: "Build a dashboard showing real-time agent activity and health metrics"

Output:
```json
{
  "title": "Real-Time Agent Monitoring Dashboard",
  "as_a": "System administrator",
  "i_want": "To view real-time agent activity and health metrics on a dashboard",
  "so_that": "I can quickly identify issues and monitor system performance",
  "estimated_effort": "1-2 weeks",
  "business_value": "⭐⭐⭐⭐⭐"
}
```

### Example 3
Input: "Add support for PostgreSQL database"

Output:
```json
{
  "title": "PostgreSQL Database Support",
  "as_a": "Developer",
  "i_want": "To use PostgreSQL as the database backend",
  "so_that": "I can leverage advanced PostgreSQL features and scalability",
  "estimated_effort": "4-6 days",
  "business_value": "⭐⭐⭐"
}
```

## Important
- Return ONLY the JSON object, no additional text
- All fields are required (use "null" if you cannot extract a field)
- Be concise but accurate
- Estimate conservatively (better to overestimate effort)
```

---

### Component 4: RoadmapEditor Enhancement

**Location**: `coffee_maker/cli/roadmap_editor.py` (EXISTING FILE - ADD METHODS)

**Responsibility**: Add validated user story to ROADMAP.md with automatic ID assignment.

**New Methods to Add**:

```python
# In coffee_maker/cli/roadmap_editor.py, add these methods to the RoadmapEditor class:

from coffee_maker.cli.user_story_draft_manager import UserStoryDraft
import re


def add_user_story(self, draft: UserStoryDraft) -> str:
    """
    Add user story to ROADMAP.md.

    This method:
    1. Assigns next available US-XXX ID
    2. Formats user story as ROADMAP markdown
    3. Creates backup of ROADMAP
    4. Atomically writes updated ROADMAP
    5. Returns assigned US-XXX ID

    Args:
        draft: Validated user story draft

    Returns:
        Assigned user story ID (e.g., "US-025")

    Raises:
        ValueError: If draft is invalid (missing required fields)
        IOError: If ROADMAP update fails

    Example:
        >>> editor = RoadmapEditor(ROADMAP_PATH)
        >>> draft = UserStoryDraft(
        ...     id="DRAFT",
        ...     title="Email Notifications",
        ...     description="Send emails when tasks complete",
        ...     estimated_effort="2-3 days",
        ...     business_value="⭐⭐⭐⭐"
        ... )
        >>> us_id = editor.add_user_story(draft)
        >>> print(us_id)
        "US-025"
    """
    logger.info(f"Adding user story to ROADMAP: {draft.title}")

    # Validate draft
    if not draft.title or not draft.description:
        raise ValueError("Draft must have title and description")

    # Assign next US-XXX ID
    next_id = self._get_next_user_story_id()
    logger.info(f"Assigned ID: {next_id}")

    # Format user story markdown
    us_markdown = self._format_user_story(draft, next_id)

    # Create backup before modification
    self._create_backup()

    # Read current ROADMAP
    with open(self.roadmap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find "## 📝 PLANNED" section and append user story
    planned_section_pattern = r"(## 📝 PLANNED[^\n]*\n)"
    match = re.search(planned_section_pattern, content)

    if match:
        # Insert after "## 📝 PLANNED" section header
        insertion_point = match.end()
        updated_content = (
            content[:insertion_point]
            + "\n"
            + us_markdown
            + "\n"
            + content[insertion_point:]
        )
    else:
        # If no PLANNED section exists, append to end
        logger.warning("No PLANNED section found, appending to end of ROADMAP")
        updated_content = content + "\n\n" + us_markdown + "\n"

    # Atomically write updated ROADMAP
    with open(self.roadmap_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    logger.info(f"User story added successfully: {next_id}")
    return next_id


def _get_next_user_story_id(self) -> str:
    """
    Find next available US-XXX identifier.

    Scans ROADMAP for existing US-XXX IDs and returns US-{max+1}.

    Returns:
        Next available US-XXX ID (e.g., "US-025")

    Example:
        >>> # If ROADMAP has US-001 through US-024
        >>> next_id = editor._get_next_user_story_id()
        >>> print(next_id)
        "US-025"
    """
    logger.debug("Scanning ROADMAP for existing US-XXX IDs")

    with open(self.roadmap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all US-XXX patterns (e.g., US-001, US-012, US-105)
    us_pattern = r"US-(\d+)"
    matches = re.findall(us_pattern, content)

    if matches:
        # Find maximum ID
        max_id = max(int(num) for num in matches)
        next_id = max_id + 1
    else:
        # No existing user stories, start at 1
        next_id = 1

    # Format as US-XXX (zero-padded to 3 digits)
    formatted_id = f"US-{next_id:03d}"
    logger.debug(f"Next available ID: {formatted_id}")

    return formatted_id


def _format_user_story(self, draft: UserStoryDraft, us_id: str) -> str:
    """
    Format user story as ROADMAP markdown.

    Generates markdown following ROADMAP conventions:
    - Section header with emoji and status
    - User story fields (As a, I want, So that)
    - Metadata (Effort, Business Value, Status)

    Args:
        draft: User story draft
        us_id: Assigned US-XXX ID

    Returns:
        Formatted markdown string

    Example:
        >>> markdown = editor._format_user_story(draft, "US-025")
        >>> print(markdown)
        ## 📝 READY TO IMPLEMENT: US-025 - Email Notification System

        **Project**: **📧 US-025 - Email Notifications for Task Completion**

        **Status**: 📝 **PLANNED** (2025-10-19)

        **User Story**:
        > "As a project manager, I want to receive email notifications when the daemon completes tasks, so that I can stay informed without constantly checking the dashboard."

        **Definition of Done**:
        > TBD (To be defined in US-013 workflow)

        **Estimated Effort**: 2-3 days

        **Business Value**: ⭐⭐⭐⭐
    """
    # Extract date
    date_str = draft.created_at.strftime("%Y-%m-%d")

    # Build markdown
    lines = [
        f"## 📝 READY TO IMPLEMENT: {us_id} - {draft.title}",
        "",
        f"**Project**: **{us_id} - {draft.title}**",
        "",
        f"**Status**: {draft.status} ({date_str})",
        "",
        "**User Story**:",
    ]

    # Add user story format if available
    if draft.as_a and draft.i_want and draft.so_that:
        lines.append(
            f'> "As a {draft.as_a}, I want {draft.i_want}, '
            f'so that {draft.so_that}."'
        )
    else:
        lines.append(f'> "{draft.description}"')

    lines.extend([
        "",
        "**Definition of Done**:",
        "> TBD (To be defined in US-013 workflow)",
        "",
    ])

    # Add metadata
    if draft.estimated_effort:
        lines.append(f"**Estimated Effort**: {draft.estimated_effort}")
        lines.append("")

    if draft.business_value:
        lines.append(f"**Business Value**: {draft.business_value}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def _create_backup(self) -> None:
    """
    Create timestamped backup of ROADMAP before modification.

    Backup saved to: roadmap_backups/ROADMAP_backup_YYYYMMDD_HHMMSS.md

    Example:
        >>> editor._create_backup()
        # Creates: roadmap_backups/ROADMAP_backup_20251019_143022.md
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"ROADMAP_backup_{timestamp}.md"
    backup_path = self.backup_dir / backup_filename

    shutil.copy2(self.roadmap_path, backup_path)
    logger.info(f"Backup created: {backup_path}")
```

---

## Data Flow & Sequence Diagrams

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                │
│   "/US I want email notifications when daemon finishes tasks"    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 1: EXTRACTION                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. ChatInterface receives command                          │ │
│  │ 2. Routes to UserStoryCommandHandler                       │ │
│  │ 3. Handler parses "/US [description]"                      │ │
│  │ 4. Calls AIService.extract_user_story(description)         │ │
│  │ 5. AIService loads prompt from .claude/commands/           │ │
│  │ 6. AIService calls Claude API                              │ │
│  │ 7. Claude returns JSON with extracted fields               │ │
│  │ 8. AIService creates UserStoryDraft object                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
                   UserStoryDraft
              (id="DRAFT", title="...", ...)
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 2: VALIDATION                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 9. DraftManager.store_draft(session_id, draft)             │ │
│  │ 10. DraftManager.format_for_review(draft) → text           │ │
│  │ 11. Handler returns formatted text to user                 │ │
│  │                                                              │ │
│  │ USER SEES DRAFT AND RESPONDS:                               │ │
│  │ Option A: "Yes, add it" (confirmation)                      │ │
│  │ Option B: "Change title to X" (edit)                        │ │
│  │ Option C: "Cancel" (cancellation)                           │ │
│  │                                                              │ │
│  │ 12. ChatInterface receives user response                    │ │
│  │ 13. Handler.handle_validation_response(response, session)  │ │
│  │ 14. Handler checks: confirmation? edit? cancel?            │ │
│  │                                                              │ │
│  │ IF EDIT:                                                     │ │
│  │   15a. Handler._extract_edits(response) → edits dict       │ │
│  │   16a. DraftManager.update_draft(session, edits)           │ │
│  │   17a. DraftManager.format_for_review(updated_draft)       │ │
│  │   18a. Return updated draft to user (loop to step 11)      │ │
│  │                                                              │ │
│  │ IF CANCEL:                                                   │ │
│  │   15b. DraftManager.clear_draft(session)                   │ │
│  │   16b. Return cancellation message                          │ │
│  │                                                              │ │
│  │ IF CONFIRM:                                                  │ │
│  │   15c. Proceed to Phase 3                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 3: PROPAGATION                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 19. RoadmapEditor._get_next_user_story_id() → "US-025"     │ │
│  │ 20. RoadmapEditor._format_user_story(draft, "US-025")      │ │
│  │ 21. RoadmapEditor._create_backup() → backup file           │ │
│  │ 22. RoadmapEditor reads ROADMAP.md                         │ │
│  │ 23. RoadmapEditor inserts formatted user story             │ │
│  │ 24. RoadmapEditor atomically writes ROADMAP.md             │ │
│  │ 25. DraftManager.clear_draft(session)                      │ │
│  │ 26. Handler returns confirmation: "Added US-025!"          │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   USER SEES CONFIRMATION                          │
│   "Great! I've added the email notification system to the        │
│    ROADMAP as US-025. You can see it in the roadmap now."        │
└──────────────────────────────────────────────────────────────────┘
```

### Sequence Diagram: Happy Path (No Edits)

```
User         ChatInterface    Handler        AIService    DraftMgr    RoadmapEditor
 │                │              │              │            │             │
 │ /US [desc]     │              │              │            │             │
 ├───────────────>│              │              │            │             │
 │                │ handle_cmd   │              │            │             │
 │                ├─────────────>│              │            │             │
 │                │              │ extract_user_│            │             │
 │                │              │   story()    │            │             │
 │                │              ├─────────────>│            │             │
 │                │              │              │ Claude API │             │
 │                │              │              ├───────────>│             │
 │                │              │              │ JSON resp  │             │
 │                │              │              │<───────────┤             │
 │                │              │ UserStory    │            │             │
 │                │              │   Draft      │            │             │
 │                │              │<─────────────┤            │             │
 │                │              │              │            │             │
 │                │              │ store_draft()│            │             │
 │                │              ├─────────────────────────>│             │
 │                │              │              │            │             │
 │                │              │ format_for_  │            │             │
 │                │              │   review()   │            │             │
 │                │              ├─────────────────────────>│             │
 │                │              │              │ formatted  │             │
 │                │              │              │   text     │             │
 │                │              │<─────────────────────────┤             │
 │                │ return text  │              │            │             │
 │                │<─────────────┤              │            │             │
 │ Draft preview  │              │              │            │             │
 │<───────────────┤              │              │            │             │
 │                │              │              │            │             │
 │ "Yes, add it"  │              │              │            │             │
 ├───────────────>│              │              │            │             │
 │                │ handle_valid │              │            │             │
 │                ├─────────────>│              │            │             │
 │                │              │ get_draft()  │            │             │
 │                │              ├─────────────────────────>│             │
 │                │              │              │ UserStory  │             │
 │                │              │              │   Draft    │             │
 │                │              │<─────────────────────────┤             │
 │                │              │              │            │             │
 │                │              │ _propagate_to_roadmap()  │             │
 │                │              ├──────────────────────────────────────>│
 │                │              │              │            │ get_next_id│
 │                │              │              │            │ ├─────────┤
 │                │              │              │            │ │ scan    │
 │                │              │              │            │ │ ROADMAP │
 │                │              │              │            │ │<────────┤
 │                │              │              │            │ │ US-025  │
 │                │              │              │            │ │         │
 │                │              │              │            │ format_us │
 │                │              │              │            │ ├─────────┤
 │                │              │              │            │ │ markdown│
 │                │              │              │            │ │<────────┤
 │                │              │              │            │           │
 │                │              │              │            │ backup()  │
 │                │              │              │            │ ├─────────┤
 │                │              │              │            │ │ copy    │
 │                │              │              │            │ │<────────┤
 │                │              │              │            │           │
 │                │              │              │            │ write()   │
 │                │              │              │            │ ├─────────┤
 │                │              │              │            │ │ atomic  │
 │                │              │              │            │ │<────────┤
 │                │              │              │            │           │
 │                │              │              │            │ "US-025"  │
 │                │              │<──────────────────────────────────────┤
 │                │              │              │            │           │
 │                │              │ clear_draft()│            │           │
 │                │              ├─────────────────────────>│           │
 │                │              │              │            │           │
 │                │ confirmation │              │            │           │
 │                │<─────────────┤              │            │           │
 │ "Added US-025!"│              │              │            │           │
 │<───────────────┤              │            │           │           │
```

### Sequence Diagram: Edit Path

```
User         ChatInterface    Handler        DraftMgr
 │                │              │              │
 │ [Draft shown]  │              │              │
 │<───────────────┼──────────────┼──────────────┤
 │                │              │              │
 │ "Change title  │              │              │
 │  to Real-Time  │              │              │
 │  Dashboard"    │              │              │
 ├───────────────>│              │              │
 │                │ handle_valid │              │
 │                ├─────────────>│              │
 │                │              │ get_draft()  │
 │                │              ├─────────────>│
 │                │              │<─────────────┤
 │                │              │              │
 │                │              │ _extract_    │
 │                │              │   edits()    │
 │                │              ├─────────┐    │
 │                │              │ parse   │    │
 │                │              │ regex   │    │
 │                │              │<────────┘    │
 │                │              │ {"title":    │
 │                │              │  "Real-Time  │
 │                │              │   Dashboard"}│
 │                │              │              │
 │                │              │ update_draft()│
 │                │              ├─────────────>│
 │                │              │              │
 │                │              │ get_draft()  │
 │                │              ├─────────────>│
 │                │              │<─────────────┤
 │                │              │              │
 │                │              │ format_for_  │
 │                │              │   review()   │
 │                │              ├─────────────>│
 │                │              │<─────────────┤
 │                │ updated text │              │
 │                │<─────────────┤              │
 │ Updated draft  │              │              │
 │<───────────────┤              │              │
 │                │              │              │
 │ "Yes, add it"  │              │              │
 ├───────────────>│ [Proceed to propagation...] │
```

---

## Implementation Plan

This section provides a **step-by-step implementation plan** with time estimates for each task. Total estimated time: **15-20 hours (2-3 days)**.

### Phase 1: Core Data Structures (2-3 hours)

**Goal**: Create foundational data structures and storage.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 1.1 | Create `UserStoryDraft` dataclass | `user_story_draft_manager.py` | 30 min | Define all fields, add validation |
| 1.2 | Create `UserStoryDraftManager` class | `user_story_draft_manager.py` | 1 hour | Implement store/get/update/clear/format |
| 1.3 | Write unit tests for DraftManager | `tests/unit/test_user_story_draft_manager.py` | 1 hour | Test all methods, edge cases |
| 1.4 | Add logging throughout | `user_story_draft_manager.py` | 15 min | DEBUG/INFO logs for all operations |

**Acceptance Criteria**:
- [ ] `UserStoryDraft` dataclass created with all fields
- [ ] `UserStoryDraftManager` can store/retrieve/update/clear drafts
- [ ] `format_for_review()` produces human-readable text
- [ ] Unit tests cover all methods (≥90% coverage)
- [ ] Logging added at appropriate levels

---

### Phase 2: AI Extraction (3-4 hours)

**Goal**: Implement Claude AI extraction of user story components.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 2.1 | Create extraction prompt | `.claude/commands/extract-user-story.md` | 1 hour | Write prompt with examples, test with Claude |
| 2.2 | Add `extract_user_story()` to `AIService` | `coffee_maker/cli/ai_service.py` | 1 hour | Call Claude API, parse JSON response |
| 2.3 | Add `_parse_user_story_response()` helper | `coffee_maker/cli/ai_service.py` | 30 min | Parse JSON, handle errors |
| 2.4 | Add `PromptNames.EXTRACT_USER_STORY` | `coffee_maker/autonomous/prompt_loader.py` | 15 min | Register new prompt |
| 2.5 | Write unit tests for extraction | `tests/unit/test_ai_service_user_story.py` | 1 hour | Test extraction, error handling, edge cases |
| 2.6 | Manual testing with various inputs | N/A | 30 min | Test vague/detailed/ambiguous descriptions |

**Acceptance Criteria**:
- [ ] Centralized prompt created in `.claude/commands/`
- [ ] `extract_user_story()` method added to `AIService`
- [ ] Extraction accuracy ≥85% on manual test cases
- [ ] Error handling for invalid input, API failures
- [ ] Unit tests cover success and error paths

---

### Phase 3: Command Handler (4-5 hours)

**Goal**: Implement `/US` command workflow orchestration.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 3.1 | Create `UserStoryCommandHandler` class | `user_story_command_handler.py` | 1 hour | Basic structure, init, logging |
| 3.2 | Implement `handle_command()` | `user_story_command_handler.py` | 1 hour | Parse command, call AIService, store draft |
| 3.3 | Implement `handle_validation_response()` | `user_story_command_handler.py` | 1.5 hours | Detect confirm/cancel/edit, route logic |
| 3.4 | Implement `_parse_us_command()` | `user_story_command_handler.py` | 15 min | Regex parsing of /US command |
| 3.5 | Implement confirmation/cancel detection | `user_story_command_handler.py` | 30 min | Regex patterns for yes/no/cancel |
| 3.6 | Implement `_extract_edits()` | `user_story_command_handler.py` | 45 min | Regex patterns for "change title to X" |
| 3.7 | Write unit tests for handler | `tests/unit/test_user_story_command_handler.py` | 1.5 hours | Test all paths, edge cases |

**Acceptance Criteria**:
- [ ] `UserStoryCommandHandler` created with all methods
- [ ] `/US [description]` parsed correctly
- [ ] Confirmation/cancellation detected reliably
- [ ] Edit extraction works for title/effort/value changes
- [ ] Unit tests cover all workflow branches

---

### Phase 4: ROADMAP Integration (3-4 hours)

**Goal**: Add validated stories to ROADMAP.md safely.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 4.1 | Implement `add_user_story()` | `coffee_maker/cli/roadmap_editor.py` | 1 hour | Orchestrate ID assignment, formatting, write |
| 4.2 | Implement `_get_next_user_story_id()` | `coffee_maker/cli/roadmap_editor.py` | 45 min | Scan ROADMAP, find max US-XXX, increment |
| 4.3 | Implement `_format_user_story()` | `coffee_maker/cli/roadmap_editor.py` | 1 hour | Generate markdown following ROADMAP format |
| 4.4 | Implement `_create_backup()` (if not exists) | `coffee_maker/cli/roadmap_editor.py` | 15 min | Timestamped backup to roadmap_backups/ |
| 4.5 | Write unit tests for ROADMAP integration | `tests/unit/test_roadmap_editor_user_story.py` | 1.5 hours | Test ID assignment, formatting, backups |
| 4.6 | Manual testing with actual ROADMAP | N/A | 30 min | Test on real ROADMAP, verify format |

**Acceptance Criteria**:
- [ ] `add_user_story()` assigns correct next US-XXX ID
- [ ] Formatted markdown matches existing ROADMAP style
- [ ] Backup created before every write
- [ ] Atomic write ensures ROADMAP integrity
- [ ] Unit tests verify all components

---

### Phase 5: ChatInterface Integration (1-2 hours)

**Goal**: Wire up `/US` command in project_manager chat.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 5.1 | Register `/US` command in ChatInterface | `coffee_maker/cli/chat_interface.py` | 15 min | Add to commands dict (if exists) |
| 5.2 | Add `handle_user_story_command()` method | `coffee_maker/cli/chat_interface.py` | 30 min | Delegate to UserStoryCommandHandler |
| 5.3 | Manage session state across turns | `coffee_maker/cli/chat_interface.py` | 30 min | Track session_id, clear on completion |
| 5.4 | Write integration tests | `tests/integration/test_us_command_workflow.py` | 1 hour | End-to-end test with ChatInterface |

**Acceptance Criteria**:
- [ ] `/US` command available in project_manager chat
- [ ] Multi-turn conversation works (draft → validation → add)
- [ ] Session state maintained correctly
- [ ] Integration tests pass

---

### Phase 6: Error Handling & Polish (2-3 hours)

**Goal**: Robust error handling, user-friendly messages, edge case coverage.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 6.1 | Add error handling for AI service failures | All components | 1 hour | Graceful degradation, user-friendly errors |
| 6.2 | Add input validation (empty descriptions, etc.) | `user_story_command_handler.py` | 30 min | Validate before AI call |
| 6.3 | Improve user-facing messages (plain language) | All components | 1 hour | Remove jargon, use "the feature" not "US-XXX" |
| 6.4 | Add comprehensive logging | All components | 30 min | INFO for workflow, DEBUG for details |
| 6.5 | Manual testing of edge cases | N/A | 1 hour | Test malformed input, API down, etc. |

**Acceptance Criteria**:
- [ ] All error messages user-friendly (no stack traces)
- [ ] Input validation prevents invalid AI calls
- [ ] Logging comprehensive for debugging
- [ ] Edge cases handled gracefully

---

### Phase 7: Documentation (1 hour)

**Goal**: Document new feature for users and developers.

| # | Task | File | Time | Details |
|---|------|------|------|---------|
| 7.1 | Update TUTORIALS.md with `/US` examples | `docs/TUTORIALS.md` | 30 min | Add section with examples |
| 7.2 | Document architecture | `docs/architecture/USER_STORY_COMMAND.md` | 30 min | Workflow, components, examples |

**Acceptance Criteria**:
- [ ] TUTORIALS.md has `/US` command section
- [ ] Architecture documented for future maintainers

---

## Testing Strategy

### Unit Tests (Coverage Goal: ≥90%)

#### Test File 1: `tests/unit/test_user_story_draft_manager.py`

```python
"""Unit tests for UserStoryDraftManager."""

import pytest
from coffee_maker.cli.user_story_draft_manager import (
    UserStoryDraft,
    UserStoryDraftManager,
)


class TestUserStoryDraft:
    """Test UserStoryDraft dataclass."""

    def test_create_minimal_draft(self):
        """Test creating draft with minimal fields."""
        draft = UserStoryDraft(
            id="DRAFT",
            title="Test Feature",
            description="Test description"
        )

        assert draft.id == "DRAFT"
        assert draft.title == "Test Feature"
        assert draft.description == "Test description"
        assert draft.status == "📝 PLANNED"
        assert draft.as_a is None
        assert draft.created_at is not None

    def test_create_complete_draft(self):
        """Test creating draft with all fields."""
        draft = UserStoryDraft(
            id="DRAFT",
            title="Email Notifications",
            description="I want email notifications",
            as_a="Project manager",
            i_want="Email notifications",
            so_that="I stay informed",
            estimated_effort="2-3 days",
            business_value="⭐⭐⭐⭐"
        )

        assert draft.as_a == "Project manager"
        assert draft.estimated_effort == "2-3 days"
        assert draft.business_value == "⭐⭐⭐⭐"


class TestUserStoryDraftManager:
    """Test UserStoryDraftManager class."""

    @pytest.fixture
    def manager(self):
        """Create fresh DraftManager for each test."""
        return UserStoryDraftManager()

    @pytest.fixture
    def sample_draft(self):
        """Create sample draft."""
        return UserStoryDraft(
            id="DRAFT",
            title="Test Feature",
            description="Test description"
        )

    def test_store_and_retrieve_draft(self, manager, sample_draft):
        """Test storing and retrieving draft."""
        manager.store_draft("session-123", sample_draft)
        retrieved = manager.get_draft("session-123")

        assert retrieved is not None
        assert retrieved.title == "Test Feature"
        assert retrieved.id == "DRAFT"

    def test_get_draft_nonexistent_session(self, manager):
        """Test retrieving draft for nonexistent session."""
        result = manager.get_draft("nonexistent")
        assert result is None

    def test_update_draft_title(self, manager, sample_draft):
        """Test updating draft title."""
        manager.store_draft("session-123", sample_draft)
        success = manager.update_draft("session-123", {"title": "New Title"})

        assert success is True
        updated = manager.get_draft("session-123")
        assert updated.title == "New Title"

    def test_update_draft_multiple_fields(self, manager, sample_draft):
        """Test updating multiple draft fields."""
        manager.store_draft("session-123", sample_draft)
        edits = {
            "title": "New Title",
            "estimated_effort": "3-4 days",
            "business_value": "⭐⭐⭐⭐⭐"
        }
        manager.update_draft("session-123", edits)

        updated = manager.get_draft("session-123")
        assert updated.title == "New Title"
        assert updated.estimated_effort == "3-4 days"
        assert updated.business_value == "⭐⭐⭐⭐⭐"

    def test_update_draft_nonexistent_session(self, manager):
        """Test updating draft for nonexistent session."""
        success = manager.update_draft("nonexistent", {"title": "X"})
        assert success is False

    def test_clear_draft(self, manager, sample_draft):
        """Test clearing draft."""
        manager.store_draft("session-123", sample_draft)
        manager.clear_draft("session-123")

        result = manager.get_draft("session-123")
        assert result is None

    def test_clear_draft_nonexistent_session(self, manager):
        """Test clearing draft for nonexistent session (no error)."""
        manager.clear_draft("nonexistent")  # Should not raise error

    def test_format_for_review_minimal(self, manager, sample_draft):
        """Test formatting minimal draft for review."""
        formatted = manager.format_for_review(sample_draft)

        assert "Test Feature" in formatted
        assert "Test description" in formatted
        assert "Does this look correct?" in formatted
        assert "Approve: 'Yes, add it'" in formatted

    def test_format_for_review_complete(self, manager):
        """Test formatting complete draft for review."""
        draft = UserStoryDraft(
            id="DRAFT",
            title="Email Notifications",
            description="I want emails",
            as_a="User",
            i_want="Email notifications",
            so_that="I stay informed",
            estimated_effort="2-3 days",
            business_value="⭐⭐⭐⭐"
        )
        formatted = manager.format_for_review(draft)

        assert "Email Notifications" in formatted
        assert "As a: User" in formatted
        assert "2-3 days" in formatted
        assert "⭐⭐⭐⭐" in formatted
```

#### Test File 2: `tests/unit/test_user_story_command_handler.py`

```python
"""Unit tests for UserStoryCommandHandler."""

import pytest
from unittest.mock import Mock, MagicMock
from coffee_maker.cli.user_story_command_handler import UserStoryCommandHandler
from coffee_maker.cli.user_story_draft_manager import UserStoryDraft


class TestUserStoryCommandHandler:
    """Test UserStoryCommandHandler class."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create mock AIService."""
        mock = Mock()
        mock.extract_user_story = Mock(return_value=UserStoryDraft(
            id="DRAFT",
            title="Test Feature",
            description="Test description",
            estimated_effort="2-3 days"
        ))
        return mock

    @pytest.fixture
    def mock_roadmap_editor(self):
        """Create mock RoadmapEditor."""
        mock = Mock()
        mock.add_user_story = Mock(return_value="US-025")
        return mock

    @pytest.fixture
    def handler(self, mock_ai_service, mock_roadmap_editor):
        """Create UserStoryCommandHandler with mocks."""
        return UserStoryCommandHandler(mock_ai_service, mock_roadmap_editor)

    def test_parse_us_command_valid(self, handler):
        """Test parsing valid /US command."""
        result = handler._parse_us_command("/US I want email notifications")
        assert result == "I want email notifications"

    def test_parse_us_command_empty(self, handler):
        """Test parsing /US command with no description."""
        result = handler._parse_us_command("/US")
        assert result is None

    def test_parse_us_command_case_insensitive(self, handler):
        """Test /US command is case-insensitive."""
        result = handler._parse_us_command("/us I want notifications")
        assert result == "I want notifications"

    def test_is_confirmation_yes(self, handler):
        """Test confirmation detection for 'yes'."""
        assert handler._is_confirmation("Yes, add it") is True
        assert handler._is_confirmation("yes") is True
        assert handler._is_confirmation("Yep, looks good") is True

    def test_is_confirmation_negative(self, handler):
        """Test confirmation detection rejects non-confirmations."""
        assert handler._is_confirmation("No, cancel") is False
        assert handler._is_confirmation("Change title") is False

    def test_is_cancellation_no(self, handler):
        """Test cancellation detection for 'no'."""
        assert handler._is_cancellation("No, cancel") is True
        assert handler._is_cancellation("Nevermind") is True

    def test_is_cancellation_negative(self, handler):
        """Test cancellation detection rejects non-cancellations."""
        assert handler._is_cancellation("Yes, add it") is False

    def test_extract_edits_title(self, handler):
        """Test extracting title edit."""
        edits = handler._extract_edits("Change title to New Title")
        assert edits == {"title": "New Title"}

    def test_extract_edits_effort(self, handler):
        """Test extracting effort edit."""
        edits = handler._extract_edits("Set effort to 3-4 days")
        assert edits == {"effort": "3-4 days"}

    def test_extract_edits_no_match(self, handler):
        """Test extract_edits returns None for non-edit text."""
        edits = handler._extract_edits("This is random text")
        assert edits is None

    def test_handle_command_success(self, handler, mock_ai_service):
        """Test handling /US command successfully."""
        response = handler.handle_command(
            "/US I want email notifications",
            "session-123"
        )

        # Verify AIService called
        mock_ai_service.extract_user_story.assert_called_once_with(
            "I want email notifications"
        )

        # Verify response contains draft
        assert "Test Feature" in response
        assert "Does this look correct?" in response

    def test_handle_command_empty_description(self, handler):
        """Test handling /US with no description."""
        response = handler.handle_command("/US", "session-123")
        assert "need a description" in response.lower()

    def test_handle_validation_confirmed(self, handler, mock_roadmap_editor):
        """Test handling confirmation response."""
        # First, create a draft
        handler.handle_command("/US Test feature", "session-123")

        # Then confirm
        response = handler.handle_validation_response("Yes, add it", "session-123")

        # Verify roadmap updated
        mock_roadmap_editor.add_user_story.assert_called_once()
        assert "US-025" in response
        assert "added" in response.lower()

    def test_handle_validation_cancelled(self, handler):
        """Test handling cancellation response."""
        # First, create a draft
        handler.handle_command("/US Test feature", "session-123")

        # Then cancel
        response = handler.handle_validation_response("No, cancel", "session-123")

        assert "cancelled" in response.lower()

        # Verify draft cleared
        draft = handler.draft_manager.get_draft("session-123")
        assert draft is None

    def test_handle_validation_edited(self, handler):
        """Test handling edit response."""
        # First, create a draft
        handler.handle_command("/US Test feature", "session-123")

        # Then edit
        response = handler.handle_validation_response(
            "Change title to New Title",
            "session-123"
        )

        assert "Updated" in response
        assert "New Title" in response

        # Verify draft updated
        draft = handler.draft_manager.get_draft("session-123")
        assert draft.title == "New Title"

    def test_handle_validation_no_draft(self, handler):
        """Test handling validation when no draft exists."""
        response = handler.handle_validation_response("Yes", "session-999")
        assert "don't have a user story draft" in response.lower()
```

#### Test File 3: `tests/unit/test_ai_service_user_story.py`

```python
"""Unit tests for AIService.extract_user_story()."""

import pytest
from unittest.mock import Mock, patch
from coffee_maker.cli.ai_service import AIService, AIServiceError
from coffee_maker.cli.user_story_draft_manager import UserStoryDraft


class TestAIServiceUserStoryExtraction:
    """Test AIService user story extraction."""

    @pytest.fixture
    def ai_service(self):
        """Create AIService instance."""
        return AIService()

    def test_extract_user_story_empty_description(self, ai_service):
        """Test extraction with empty description raises ValueError."""
        with pytest.raises(ValueError, match="at least 5 characters"):
            ai_service.extract_user_story("")

    def test_extract_user_story_too_short(self, ai_service):
        """Test extraction with too-short description raises ValueError."""
        with pytest.raises(ValueError):
            ai_service.extract_user_story("hi")

    @patch('coffee_maker.cli.ai_service.load_prompt')
    @patch.object(AIService, 'client')
    def test_extract_user_story_success(self, mock_client, mock_load_prompt, ai_service):
        """Test successful user story extraction."""
        # Mock prompt loading
        mock_load_prompt.return_value = "Test prompt"

        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"title": "Email Notifications", '
                                            '"as_a": "User", '
                                            '"estimated_effort": "2-3 days", '
                                            '"business_value": "⭐⭐⭐⭐"}')]
        mock_client.messages.create.return_value = mock_response

        # Extract
        draft = ai_service.extract_user_story("I want email notifications")

        assert draft.title == "Email Notifications"
        assert draft.as_a == "User"
        assert draft.estimated_effort == "2-3 days"

    @patch.object(AIService, 'client')
    def test_extract_user_story_api_error(self, mock_client, ai_service):
        """Test extraction handles Claude API errors."""
        mock_client.messages.create.side_effect = Exception("API Error")

        with pytest.raises(AIServiceError):
            ai_service.extract_user_story("Test description")

    def test_parse_user_story_response_valid(self, ai_service):
        """Test parsing valid JSON response."""
        json_response = '''
        {
            "title": "Email Notifications",
            "as_a": "User",
            "i_want": "Email notifications",
            "so_that": "I stay informed",
            "estimated_effort": "2-3 days",
            "business_value": "⭐⭐⭐⭐"
        }
        '''

        parsed = ai_service._parse_user_story_response(json_response)

        assert parsed["title"] == "Email Notifications"
        assert parsed["as_a"] == "User"

    def test_parse_user_story_response_missing_title(self, ai_service):
        """Test parsing response without title raises ValueError."""
        json_response = '{"as_a": "User"}'

        with pytest.raises(ValueError, match="missing required 'title'"):
            ai_service._parse_user_story_response(json_response)

    def test_parse_user_story_response_invalid_json(self, ai_service):
        """Test parsing invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            ai_service._parse_user_story_response("not json")
```

#### Test File 4: `tests/unit/test_roadmap_editor_user_story.py`

```python
"""Unit tests for RoadmapEditor user story methods."""

import pytest
from pathlib import Path
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.user_story_draft_manager import UserStoryDraft


class TestRoadmapEditorUserStory:
    """Test RoadmapEditor user story methods."""

    @pytest.fixture
    def temp_roadmap(self, tmp_path):
        """Create temporary ROADMAP for testing."""
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text("""# ROADMAP

## 📝 PLANNED

## EXISTING CONTENT

### PRIORITY 1: Existing Priority

**Status**: ✅ Complete

**Existing User Stories:**
- US-001: First Feature
- US-024: Last Feature
""")
        return roadmap_path

    @pytest.fixture
    def editor(self, temp_roadmap):
        """Create RoadmapEditor with temp ROADMAP."""
        return RoadmapEditor(temp_roadmap)

    @pytest.fixture
    def sample_draft(self):
        """Create sample draft."""
        return UserStoryDraft(
            id="DRAFT",
            title="Email Notifications",
            description="I want emails",
            as_a="User",
            i_want="Email notifications",
            so_that="I stay informed",
            estimated_effort="2-3 days",
            business_value="⭐⭐⭐⭐"
        )

    def test_get_next_user_story_id_existing_stories(self, editor):
        """Test getting next ID when stories exist."""
        next_id = editor._get_next_user_story_id()
        assert next_id == "US-025"  # Max is US-024, so next is US-025

    def test_get_next_user_story_id_no_existing_stories(self, tmp_path):
        """Test getting next ID when no stories exist."""
        roadmap_path = tmp_path / "ROADMAP_empty.md"
        roadmap_path.write_text("# ROADMAP\n\n## 📝 PLANNED\n")
        editor = RoadmapEditor(roadmap_path)

        next_id = editor._get_next_user_story_id()
        assert next_id == "US-001"

    def test_format_user_story_complete(self, editor, sample_draft):
        """Test formatting complete user story."""
        markdown = editor._format_user_story(sample_draft, "US-025")

        assert "US-025" in markdown
        assert "Email Notifications" in markdown
        assert "As a User" in markdown
        assert "2-3 days" in markdown
        assert "⭐⭐⭐⭐" in markdown

    def test_format_user_story_minimal(self, editor):
        """Test formatting minimal user story (no optional fields)."""
        draft = UserStoryDraft(
            id="DRAFT",
            title="Test Feature",
            description="Test description"
        )

        markdown = editor._format_user_story(draft, "US-025")

        assert "US-025" in markdown
        assert "Test Feature" in markdown
        assert "Test description" in markdown

    def test_add_user_story_success(self, editor, sample_draft):
        """Test adding user story to ROADMAP."""
        us_id = editor.add_user_story(sample_draft)

        # Verify ID assigned
        assert us_id == "US-025"

        # Verify ROADMAP updated
        roadmap_content = editor.roadmap_path.read_text()
        assert "US-025" in roadmap_content
        assert "Email Notifications" in roadmap_content

    def test_add_user_story_backup_created(self, editor, sample_draft):
        """Test backup created before adding user story."""
        editor.add_user_story(sample_draft)

        # Verify backup exists
        backups = list(editor.backup_dir.glob("ROADMAP_backup_*.md"))
        assert len(backups) >= 1

    def test_add_user_story_invalid_draft(self, editor):
        """Test adding invalid draft raises ValueError."""
        invalid_draft = UserStoryDraft(
            id="DRAFT",
            title="",  # Empty title
            description=""
        )

        with pytest.raises(ValueError, match="must have title"):
            editor.add_user_story(invalid_draft)

    def test_add_user_story_incremental_ids(self, editor):
        """Test adding multiple user stories assigns incremental IDs."""
        draft1 = UserStoryDraft(id="DRAFT", title="Feature 1", description="Desc 1")
        draft2 = UserStoryDraft(id="DRAFT", title="Feature 2", description="Desc 2")

        id1 = editor.add_user_story(draft1)
        id2 = editor.add_user_story(draft2)

        assert id1 == "US-025"
        assert id2 == "US-026"
```

### Integration Tests

#### Test File: `tests/integration/test_us_command_workflow.py`

```python
"""Integration tests for /US command workflow."""

import pytest
from pathlib import Path
from coffee_maker.cli.user_story_command_handler import UserStoryCommandHandler
from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor


class TestUSCommandWorkflow:
    """Test end-to-end /US command workflow."""

    @pytest.fixture
    def temp_roadmap(self, tmp_path):
        """Create temporary ROADMAP."""
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text("# ROADMAP\n\n## 📝 PLANNED\n")
        return roadmap_path

    @pytest.fixture
    def handler(self, temp_roadmap):
        """Create UserStoryCommandHandler with real dependencies."""
        ai_service = AIService()
        roadmap_editor = RoadmapEditor(temp_roadmap)
        return UserStoryCommandHandler(ai_service, roadmap_editor)

    @pytest.mark.integration
    def test_us_command_end_to_end(self, handler, temp_roadmap):
        """Test full workflow: /US → extract → validate → add."""
        session_id = "test-session-001"

        # Step 1: User issues /US command
        response1 = handler.handle_command(
            "/US I want email notifications when daemon finishes tasks",
            session_id
        )

        # Verify draft presented
        assert "drafted a user story" in response1.lower()
        assert "Does this look correct?" in response1

        # Step 2: User confirms
        response2 = handler.handle_validation_response("Yes, add it", session_id)

        # Verify confirmation
        assert "added" in response2.lower()
        assert "US-001" in response2

        # Verify ROADMAP updated
        roadmap_content = temp_roadmap.read_text()
        assert "US-001" in roadmap_content

    @pytest.mark.integration
    def test_us_command_with_edits(self, handler):
        """Test workflow with title edit."""
        session_id = "test-session-002"

        # Step 1: Create draft
        handler.handle_command("/US Build a dashboard", session_id)

        # Step 2: Edit title
        response = handler.handle_validation_response(
            "Change title to Real-Time Dashboard",
            session_id
        )

        # Verify updated draft shown
        assert "Real-Time Dashboard" in response

        # Step 3: Confirm
        response = handler.handle_validation_response("Yes, add it", session_id)
        assert "added" in response.lower()

    @pytest.mark.integration
    def test_us_command_cancellation(self, handler):
        """Test cancellation workflow."""
        session_id = "test-session-003"

        # Step 1: Create draft
        handler.handle_command("/US Test feature", session_id)

        # Step 2: Cancel
        response = handler.handle_validation_response("No, cancel", session_id)

        # Verify cancelled
        assert "cancelled" in response.lower()

        # Verify draft cleared
        draft = handler.draft_manager.get_draft(session_id)
        assert draft is None

    @pytest.mark.integration
    def test_us_command_malformed_input(self, handler):
        """Test handling of malformed input."""
        response = handler.handle_command("/US", "session-004")
        assert "need a description" in response.lower()
```

### Manual Testing Scenarios

**Scenario 1: Happy Path**
```
1. Run project_manager chat
2. Enter: /US I want email notifications when daemon finishes tasks
3. Verify: Draft presented with title, description, effort, value
4. Enter: Yes, add it
5. Verify: Confirmation message with US-XXX ID
6. Check ROADMAP.md: Verify US-XXX exists in PLANNED section
```

**Scenario 2: Edit Title**
```
1. Enter: /US Build a dashboard for monitoring agents
2. Verify: Draft shown with title "Agent Monitoring Dashboard"
3. Enter: Change title to Real-Time Agent Dashboard
4. Verify: Updated draft shown with new title
5. Enter: Yes, add it
6. Verify: US-XXX added with correct title
```

**Scenario 3: Cancel**
```
1. Enter: /US Add PostgreSQL support
2. Verify: Draft shown
3. Enter: Cancel
4. Verify: Cancellation message shown
5. Enter: /US Another feature
6. Verify: New draft shown (previous draft cleared)
```

**Scenario 4: AI Service Down**
```
1. Stop Claude API (or use invalid API key)
2. Enter: /US Test feature
3. Verify: User-friendly error message (not stack trace)
4. Verify: Suggestion to retry
```

---

## Security Considerations

### Input Validation

**Risk**: User input sent to Claude API could contain malicious content or prompt injection attempts.

**Mitigation**:
1. **Length validation**: Limit description to 2000 characters
2. **Sanitization**: Remove control characters, null bytes
3. **Prompt design**: Claude prompt explicitly instructs to return JSON only (no code execution)

**Implementation**:
```python
def extract_user_story(self, description: str) -> UserStoryDraft:
    # Validate length
    if len(description) > 2000:
        raise ValueError("Description too long (max 2000 characters)")

    # Sanitize input
    description = description.strip()
    description = re.sub(r'[\x00-\x1f\x7f]', '', description)  # Remove control chars

    # Proceed with extraction...
```

### ROADMAP Data Integrity

**Risk**: Concurrent writes or system crash during ROADMAP update could corrupt data.

**Mitigation**:
1. **Atomic writes**: Write to temp file, then rename (atomic operation on most filesystems)
2. **Backups**: Create timestamped backup before every write
3. **File locking**: Use `fcntl.flock()` (Unix) or `msvcrt.locking()` (Windows) during write
4. **Validation after write**: Read back and verify US-XXX exists

**Implementation**:
```python
def _atomic_write(self, content: str):
    """Atomically write to ROADMAP with file locking."""
    temp_path = self.roadmap_path.with_suffix('.tmp')

    # Write to temp file
    with open(temp_path, 'w', encoding='utf-8') as f:
        # Lock file (exclusive)
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(content)
        # Lock released when file closed

    # Atomic rename
    temp_path.replace(self.roadmap_path)
```

### Session Isolation

**Risk**: User A's draft visible to User B if session IDs predictable or leaked.

**Mitigation**:
1. **Random session IDs**: Use `uuid.uuid4()` for session identifiers
2. **Session cleanup**: Clear drafts after completion/timeout
3. **No persistence**: Drafts stored in memory only (not logged or saved)

**Implementation**:
```python
# In ChatInterface
import uuid

def start_session(self):
    """Start new chat session with random ID."""
    return str(uuid.uuid4())
```

### API Key Security

**Risk**: Claude API key exposed in logs, errors, or source code.

**Mitigation**:
1. **Environment variable**: API key loaded from `ANTHROPIC_API_KEY` env var
2. **No logging**: Never log API key (already implemented in AIService)
3. **Error messages**: Sanitize errors to remove API key if present

**Implementation** (already exists in AIService):
```python
class AIService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
```

### Rate Limiting

**Risk**: Malicious user floods `/US` command, exhausts Claude API quota.

**Mitigation**:
1. **Per-session rate limit**: Max 10 extractions per session per hour
2. **Global rate limit**: Respect Claude API limits (already in AIService)
3. **Exponential backoff**: Retry with backoff on rate limit errors

**Implementation**:
```python
from collections import defaultdict
from time import time

class UserStoryCommandHandler:
    def __init__(self, ...):
        ...
        self._rate_limits = defaultdict(list)  # session_id -> [timestamps]
        self._max_per_hour = 10

    def _check_rate_limit(self, session_id: str) -> bool:
        """Check if session has exceeded rate limit."""
        now = time()
        cutoff = now - 3600  # 1 hour ago

        # Remove old timestamps
        self._rate_limits[session_id] = [
            ts for ts in self._rate_limits[session_id] if ts > cutoff
        ]

        # Check limit
        if len(self._rate_limits[session_id]) >= self._max_per_hour:
            return False

        # Record this request
        self._rate_limits[session_id].append(now)
        return True
```

---

## Performance Requirements

### Response Time Targets

| Operation | Target | 95th Percentile | Measurement |
|-----------|--------|-----------------|-------------|
| AI Extraction | < 3 sec | < 5 sec | Time from /US to draft presentation |
| Validation Response | < 100 ms | < 200 ms | Time from user response to next prompt |
| ROADMAP Write | < 500 ms | < 1 sec | Time to write and verify ROADMAP update |
| End-to-End (no edits) | < 5 sec | < 7 sec | /US to "Added US-XXX" confirmation |

### Scalability Considerations

**Current Design** (MVP):
- In-memory session storage (Dict)
- Single-threaded command handling
- File-based ROADMAP storage

**Limitations**:
- Max concurrent sessions: ~1000 (memory-bound)
- Max ROADMAP size: ~10MB (read/write performance degrades)

**Future Optimizations** (if needed):
1. **Persistent session storage**: SQLite for drafts (scales to 100K+ sessions)
2. **Database-backed ROADMAP**: Move ROADMAP to SQLite (faster queries, concurrent writes)
3. **Caching**: Cache parsed ROADMAP structure, invalidate on write
4. **Async AI calls**: Use `asyncio` for concurrent Claude API calls

### Resource Usage

**Memory**:
- UserStoryDraft: ~1 KB per draft
- Max concurrent sessions: 100 (reasonable assumption)
- Total draft storage: ~100 KB (negligible)

**Disk**:
- ROADMAP backups: ~50 KB per backup
- Retention: Keep last 100 backups (~5 MB)
- Cleanup: Purge backups older than 30 days

**API Quota**:
- Claude API: 50K tokens/day (typical)
- Average extraction: 1K tokens (prompt + response)
- Max extractions/day: ~50 (well within quota)

---

## Risk Analysis

### Risk Matrix

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|------------|--------|----------|------------|
| AI extraction quality low | Medium | Medium | **Medium** | User validation, edits, prompt tuning |
| Session state loss (process restart) | Low | Low | **Low** | Acceptable for MVP, document recovery |
| Duplicate US-XXX IDs | Very Low | High | **Medium** | File locking, atomic writes |
| Claude API unavailable | Low | High | **Medium** | Graceful error, retry suggestion |
| ROADMAP corruption | Very Low | Critical | **Medium** | Backups, atomic writes, validation |
| User frustration with edits | Medium | Low | **Low** | Support multiple edit types, clear instructions |
| Rate limit exceeded | Very Low | Medium | **Low** | Per-session rate limiting |

### Detailed Risk Analysis

#### Risk 1: AI Extraction Quality

**Description**: Claude may extract incorrect or incomplete information from vague/ambiguous descriptions.

**Likelihood**: Medium (users may provide unclear descriptions)

**Impact**: Medium (user must manually correct, adds friction but not blocking)

**Mitigation Strategy**:
1. **High-quality prompt**: Use examples, clear instructions in extraction prompt
2. **User validation**: User reviews draft before ROADMAP update (catches errors)
3. **Edit support**: User can easily fix title, effort, etc.
4. **Feedback loop**: Log extraction failures, improve prompt over time
5. **Partial extraction**: Allow missing fields (don't require all fields)

**Residual Risk**: Low (validation catches most errors, edits provide escape hatch)

---

#### Risk 2: Session State Loss

**Description**: In-memory session state lost if project_manager process restarts.

**Likelihood**: Low (process rarely restarts during active session)

**Impact**: Low (user just re-runs `/US` command, minimal data loss)

**Mitigation Strategy**:
1. **Accept as MVP limitation**: Document in help text
2. **User guidance**: "If draft is lost, re-run `/US` command"
3. **Future enhancement**: Persist to SQLite if becomes pain point

**Residual Risk**: Very Low (acceptable for MVP)

---

#### Risk 3: Duplicate User Story IDs

**Description**: Concurrent `/US` commands might assign same US-XXX ID if reads/writes not synchronized.

**Likelihood**: Very Low (single-user system, unlikely concurrent commands)

**Impact**: High (ROADMAP corruption, duplicate IDs)

**Mitigation Strategy**:
1. **File locking**: Use `fcntl.flock()` during ROADMAP read/write
2. **Re-read before assign**: Read ROADMAP fresh before assigning ID (not cached)
3. **Validation after write**: Verify US-XXX exists after write
4. **Backups**: If corruption occurs, restore from backup

**Residual Risk**: Very Low (file locking prevents race conditions)

---

#### Risk 4: Claude API Unavailable

**Description**: Claude API down prevents `/US` command from working.

**Likelihood**: Low (Claude API has high uptime)

**Impact**: High (feature completely unusable during outage)

**Mitigation Strategy**:
1. **Graceful error message**: "AI service unavailable, please try again later"
2. **Retry suggestion**: "Check status at https://status.anthropic.com"
3. **Logging**: Log API errors for debugging
4. **Future fallback**: Template-based manual entry (Phase 2 enhancement)

**Residual Risk**: Low (outages rare, users can retry)

---

#### Risk 5: ROADMAP Corruption

**Description**: System crash or disk error during ROADMAP write corrupts file.

**Likelihood**: Very Low (modern filesystems, rare crashes)

**Impact**: Critical (ROADMAP unusable, all user stories lost)

**Mitigation Strategy**:
1. **Atomic writes**: Write to temp file, then atomic rename
2. **Backups**: Timestamped backup before every write
3. **Validation**: Read back after write, verify integrity
4. **Recovery process**: Documented restoration from backup
5. **Version control**: ROADMAP.md tracked in git (additional safety net)

**Residual Risk**: Very Low (multi-layer protection)

---

## Success Criteria

### Functional Acceptance Criteria

**Phase 1: Core Workflow**
- [ ] `/US` command available in project_manager chat
- [ ] User can type: `/US I want to be able to [description]`
- [ ] PM extracts and structures user story from description
- [ ] PM presents draft user story to user with all fields
- [ ] PM waits for user validation (does NOT auto-add to roadmap)
- [ ] User can approve: "Yes, add it" → adds to ROADMAP
- [ ] User can cancel: "No, cancel" → discards draft
- [ ] User can edit: "Change title to X" → updates draft and re-presents
- [ ] After validation, PM propagates to ROADMAP.md
- [ ] User receives confirmation with US-XXX ID
- [ ] ROADMAP.md updated in "📝 PLANNED" section
- [ ] Backup created before ROADMAP update

**Phase 2: Quality**
- [ ] Extraction accuracy ≥85% on 20 test cases (manual review)
- [ ] All error messages user-friendly (no stack traces)
- [ ] Conversation feels natural (not form-filling)
- [ ] Plain language used ("the feature" not "US-XXX")

**Phase 3: Robustness**
- [ ] Empty description handled gracefully
- [ ] AI service down handled gracefully
- [ ] Concurrent commands don't create duplicate IDs
- [ ] Session state maintained across multi-turn conversation
- [ ] ROADMAP integrity maintained (no corruption)

### Non-Functional Acceptance Criteria

**Performance**
- [ ] AI extraction completes in < 3 seconds (95th percentile)
- [ ] End-to-end workflow < 5 seconds (no edits)
- [ ] Validation response < 100 ms

**Usability**
- [ ] Time to create user story reduced from 5-10 min to < 1 min
- [ ] User satisfaction ≥4/5 (manual survey of 5 users)

**Code Quality**
- [ ] Unit test coverage ≥90%
- [ ] All tests passing (unit + integration)
- [ ] Code reviewed by architect
- [ ] Follows Python style guide (.gemini/styleguide.md)
- [ ] Logging comprehensive (INFO for workflow, DEBUG for details)

**Documentation**
- [ ] TUTORIALS.md updated with `/US` examples
- [ ] Architecture documented in docs/architecture/
- [ ] Code comments explain complex logic
- [ ] Help text available via `/help` command

---

## Rollout Plan

### Pre-Launch Checklist

**Code Completion**
- [ ] All components implemented (Handler, DraftManager, AIService, RoadmapEditor)
- [ ] Unit tests written and passing (≥90% coverage)
- [ ] Integration tests written and passing
- [ ] Manual testing completed (all scenarios)
- [ ] Code reviewed by architect
- [ ] Pre-commit hooks passing (black, mypy, pylint)

**Documentation**
- [ ] TUTORIALS.md updated
- [ ] Architecture docs created
- [ ] Inline code comments added
- [ ] Help text updated

**Infrastructure**
- [ ] Claude API key configured
- [ ] Centralized prompt created (`.claude/commands/extract-user-story.md`)
- [ ] Backup directory created (`roadmap_backups/`)
- [ ] Logging configured

### Launch Steps

**Day 1: Soft Launch (Internal Testing)**
1. Merge feature branch to `roadmap`
2. Tag as `wip-US-012`
3. Announce in team chat: "US-012 available for testing"
4. Collect feedback from 3-5 test users
5. Monitor logs for errors

**Day 2-3: Bug Fixes**
1. Address bugs found in soft launch
2. Improve error messages based on feedback
3. Tune extraction prompt if accuracy < 85%

**Day 4: Hard Launch**
1. Tag as `dod-verified-US-012` (after project_manager verification)
2. Announce in docs: Update CHANGELOG.md
3. Send notification: "New `/US` command available!"

**Day 5-7: Monitoring**
1. Monitor usage metrics (# of /US commands, success rate)
2. Collect user feedback
3. Identify improvement opportunities

### Post-Launch Monitoring

**Metrics to Track**:
- `/US` command usage count (daily)
- AI extraction success rate (% of drafts confirmed)
- AI extraction latency (95th percentile)
- Error rate (% of commands resulting in errors)
- User story creation time (before/after comparison)

**Alerts**:
- Error rate > 10%: Investigate immediately
- Extraction latency > 5 sec: Check Claude API status
- Success rate < 70%: Review extraction prompt

**Feedback Channels**:
- In-app: Add feedback option to `/US` workflow
- Direct: Ask users for feedback in team meetings
- Passive: Monitor support tickets related to user story creation

---

## Appendix

### A. Example Prompts and Responses

**Example 1: Simple Feature**
```
User: /US I want to see agent health metrics

PM: I've drafted a user story based on your input:

**Title**: Agent Health Metrics Dashboard

**Description**: I want to see agent health metrics

**As a**: System administrator
**I want**: To view agent health metrics in real-time
**So that**: I can quickly identify and resolve issues

**Estimated Effort**: 3-5 days
**Business Value**: ⭐⭐⭐⭐

Does this look correct? You can:
- Approve: 'Yes, add it'
- Edit: 'Change title to...' or 'Effort should be...'
- Cancel: 'No, cancel'

User: Yes, add it

PM: Great! I've added the agent health metrics dashboard to the ROADMAP as US-025.
You can see it in the roadmap now. Want to create another user story?
```

**Example 2: With Edits**
```
User: /US Build a notification system for task completion

PM: I've drafted a user story based on your input:

**Title**: Task Completion Notification System

**Description**: Build a notification system for task completion

**As a**: Project manager
**I want**: To receive notifications when tasks complete
**So that**: I stay informed without constantly checking

**Estimated Effort**: 4-6 days
**Business Value**: ⭐⭐⭐⭐

Does this look correct?

User: Change business value to 5 stars and effort to 2-3 days

PM: Updated! Here's the revised draft:

**Title**: Task Completion Notification System

**Description**: Build a notification system for task completion

**As a**: Project manager
**I want**: To receive notifications when tasks complete
**So that**: I stay informed without constantly checking

**Estimated Effort**: 2-3 days
**Business Value**: ⭐⭐⭐⭐⭐

Does this look correct?

User: Perfect, add it

PM: Great! I've added the task completion notification system to the ROADMAP as US-026.
```

---

### B. File Structure

```
MonolithicCoffeeMakerAgent/
├── .claude/
│   └── commands/
│       └── extract-user-story.md           # NEW: AI extraction prompt
│
├── coffee_maker/
│   ├── cli/
│   │   ├── ai_service.py                   # MODIFIED: Add extract_user_story()
│   │   ├── roadmap_editor.py               # MODIFIED: Add add_user_story()
│   │   ├── user_story_command_handler.py   # NEW: Command handler
│   │   └── user_story_draft_manager.py     # NEW: Draft manager
│   │
│   └── autonomous/
│       └── prompt_loader.py                # MODIFIED: Add EXTRACT_USER_STORY
│
├── docs/
│   ├── architecture/
│   │   └── specs/
│   │       └── SPEC-012-*.md               # THIS FILE
│   │
│   ├── roadmap/
│   │   ├── ROADMAP.md                      # MODIFIED: New user stories added
│   │   └── roadmap_backups/                # NEW: Backup directory
│   │
│   └── TUTORIALS.md                        # MODIFIED: Add /US section
│
└── tests/
    ├── unit/
    │   ├── test_user_story_draft_manager.py    # NEW
    │   ├── test_user_story_command_handler.py  # NEW
    │   ├── test_ai_service_user_story.py       # NEW
    │   └── test_roadmap_editor_user_story.py   # NEW
    │
    └── integration/
        └── test_us_command_workflow.py         # NEW
```

---

### C. Dependencies

**Python Standard Library**:
- `re` - Regular expressions for parsing
- `json` - JSON parsing for Claude responses
- `logging` - Logging throughout
- `dataclasses` - UserStoryDraft dataclass
- `datetime` - Timestamps for drafts and backups
- `shutil` - File operations (backups)
- `pathlib.Path` - Path handling

**External Dependencies** (Already Installed):
- `anthropic` - Claude API client
- `pytest` - Testing framework

**No New Dependencies Required** ✅

---

### D. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created enhanced specification | architect |
| 2025-10-19 | Added detailed code examples, data flow diagrams | architect |
| 2025-10-19 | Added comprehensive testing strategy | architect |
| 2025-10-19 | Added security and performance analysis | architect |
| 2025-10-19 | Added step-by-step implementation plan with time estimates | architect |

---

### E. Approval

Who needs to approve this spec?

- [ ] architect (author) - Self-approval pending
- [ ] code_developer (implementer) - Review for implementability
- [ ] project_manager (strategic alignment) - Review for roadmap fit
- [ ] User (final approval) - Review for usability and value

**Approval Date**: TBD

---

**Estimated Implementation Time**: 15-20 hours (2-3 days)

**Complexity**: High (Multi-component integration, AI-driven workflow, conversational state management)

**Priority**: Medium (US-012 is PLANNED, improves user experience significantly)

---

END OF SPECIFICATION
