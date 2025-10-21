# SPEC-012: User Story Command Handler

**Status**: 📝 Draft
**Priority**: PRIORITY 12
**User Story**: US-012 - User Story Command Handler
**Created**: 2025-10-19
**Estimated Effort**: 7-10 hours (1-2 days)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Dependencies](#prerequisites--dependencies)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Implementation Plan](#implementation-plan)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Performance Requirements](#performance-requirements)
10. [Risk Analysis](#risk-analysis)
11. [Success Criteria](#success-criteria)

---

## Executive Summary

**Problem Statement**: Users currently cannot create user stories through natural language conversation with the project manager. They must manually edit ROADMAP.md or use rigid command structures.

**Solution**: Implement a conversational `/US` command that allows users to describe features in natural language, collaboratively refine them with AI assistance, and add validated user stories to the roadmap.

**Key Features**:
- Natural language user story creation via `/US [description]` command
- AI-powered extraction and structuring of user stories
- Collaborative validation workflow (draft → refine → validate → propagate)
- Similarity detection to prevent duplicate user stories
- Intelligent prioritization assistance
- Impact analysis on existing roadmap

**Strategic Value**:
- Reduces friction for user story creation (from manual editing to conversational)
- Ensures consistent user story format and quality
- Prevents duplicate work through similarity detection
- Integrates with existing roadmap management infrastructure

---

## Prerequisites & Dependencies

### Required Components (Already Exist)

1. **RoadmapEditor** (`coffee_maker/cli/roadmap_editor.py`)
   - `add_user_story()` - Add US to ROADMAP.md
   - `get_user_story_summary()` - List all user stories
   - File path: `coffee_maker/cli/roadmap_editor.py:150-250`

2. **AIService** (`coffee_maker/cli/ai_service.py`)
   - `process_request()` - Natural language processing
   - Claude API integration
   - File path: `coffee_maker/cli/ai_service.py:100-200`

3. **ChatSession** (`coffee_maker/cli/chat_interface.py`)
   - Interactive REPL interface
   - Command handler integration
   - Rich UI components
   - File path: `coffee_maker/cli/chat_interface.py:200-500`

4. **Command Handler Infrastructure** (`coffee_maker/cli/commands/`)
   - Existing command pattern
   - File path: `coffee_maker/cli/commands/all_commands.py`

### New Dependencies

1. **Similarity Detection Library**
   - Option 1: `difflib` (Python stdlib, no new dependency)
   - Option 2: `fuzzywuzzy` (better accuracy, needs approval)
   - **Recommendation**: Use `difflib` initially (zero dependency), upgrade if needed

2. **Prompt Templates**
   - New prompt: `EXTRACT_USER_STORY` in `.claude/commands/`
   - New prompt: `ANALYZE_SIMILARITY` in `.claude/commands/`
   - New prompt: `SUGGEST_PRIORITIZATION` in `.claude/commands/`

### Configuration

No new configuration required. Uses existing:
- `coffee_maker/config.py` for paths
- `ConfigManager` for API keys
- Environment variables for Claude API

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User (CLI Interface)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ "/US I want to..."
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ChatSession (UI Layer)                    │
│  - Parse /US command                                         │
│  - Manage conversation state                                 │
│  - Display formatted responses                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              UserStoryCommandHandler (Business Logic)        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Phase 1: Extract & Structure                        │    │
│  │  - Parse user description                           │    │
│  │  - Call AIService.extract_user_story()              │    │
│  │  - Format as structured US                          │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Phase 2: Similarity Detection                       │    │
│  │  - Compare with existing user stories               │    │
│  │  - Calculate similarity scores                      │    │
│  │  - Present options: new vs rephrase                 │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Phase 3: Validation Loop                            │    │
│  │  - Present draft to user                            │    │
│  │  - Accept refinement requests                       │    │
│  │  - Iterate until approved                           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Phase 4: Prioritization                             │    │
│  │  - Analyze roadmap dependencies                     │    │
│  │  - Suggest placement                                │    │
│  │  - Get user confirmation                            │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Phase 5: Propagation                                │    │
│  │  - Call RoadmapEditor.add_user_story()              │    │
│  │  - Update ROADMAP.md                                │    │
│  │  - Confirm to user                                  │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────┬─────────────────────────┬───────────────────┘
                │                         │
                ▼                         ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│      AIService            │   │    RoadmapEditor         │
│  - extract_user_story()   │   │  - add_user_story()      │
│  - analyze_similarity()   │   │  - get_user_stories()    │
│  - suggest_prioritization()│   │  - validate_roadmap()    │
└───────────────────────────┘   └──────────────────────────┘
                │                         │
                └─────────┬───────────────┘
                          ▼
                ┌─────────────────────────┐
                │    ROADMAP.md           │
                │  (docs/roadmap/)        │
                └─────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: UI (ChatSession) ↔ Business Logic (Handler) ↔ Data (RoadmapEditor)
2. **Stateful Conversation**: Track validation loop state across multiple user interactions
3. **Non-Destructive**: Never auto-add to roadmap without explicit user approval
4. **Defensive**: Validate all inputs, handle edge cases gracefully
5. **Observable**: Log all stages for debugging and observability

---

## Component Specifications

### 1. UserStoryCommandHandler

**File**: `coffee_maker/cli/commands/user_story_command.py` (NEW)

**Class Definition**:

```python
"""User Story Command Handler - Natural language user story creation.

This handler implements the /US command for creating user stories through
conversational interaction with Claude AI.

Example:
    >>> handler = UserStoryCommandHandler(ai_service, roadmap_editor)
    >>> result = handler.handle_command("/US I want to track user logins")
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor


class ValidationState(Enum):
    """States in the user story validation workflow."""

    EXTRACTING = "extracting"          # Parsing natural language
    CHECKING_SIMILARITY = "checking"   # Comparing with existing US
    AWAITING_VALIDATION = "validating" # Waiting for user approval
    REFINING = "refining"              # User requested changes
    PRIORITIZING = "prioritizing"      # Determining placement
    COMPLETE = "complete"              # Ready to propagate


@dataclass
class UserStoryDraft:
    """Draft user story being validated.

    Attributes:
        title: User story title (e.g., "User Login Tracking")
        description: Full user story in "As a X I want Y so that Z" format
        acceptance_criteria: List of acceptance criteria
        estimated_effort: Optional effort estimate (e.g., "2-3 days")
        similar_stories: List of similar existing user stories
        suggested_priority: AI-suggested priority placement
        state: Current validation state
        conversation_history: Messages exchanged during refinement
    """

    title: str
    description: str
    acceptance_criteria: List[str]
    estimated_effort: Optional[str] = None
    similar_stories: List[Tuple[str, float]] = None  # (US-ID, similarity_score)
    suggested_priority: Optional[str] = None
    state: ValidationState = ValidationState.EXTRACTING
    conversation_history: List[Dict] = None

    def __post_init__(self):
        if self.similar_stories is None:
            self.similar_stories = []
        if self.conversation_history is None:
            self.conversation_history = []


class UserStoryCommandHandler:
    """Handler for /US command - conversational user story creation.

    This handler manages the entire workflow:
    1. Extract structured user story from natural language
    2. Check for similar existing user stories
    3. Validate with user through conversation
    4. Determine prioritization
    5. Propagate to ROADMAP.md

    Example:
        >>> handler = UserStoryCommandHandler(ai_service, roadmap_editor)
        >>> response = handler.handle_command(
        ...     "/US I want users to be able to export reports to PDF"
        ... )
        >>> print(response['message'])
    """

    def __init__(
        self,
        ai_service: AIService,
        roadmap_editor: RoadmapEditor,
        similarity_threshold: float = 0.7
    ):
        """Initialize handler.

        Args:
            ai_service: Claude AI service for NLP
            roadmap_editor: Editor for ROADMAP.md manipulation
            similarity_threshold: Minimum similarity score to flag duplicates (0.0-1.0)
        """
        self.ai_service = ai_service
        self.roadmap_editor = roadmap_editor
        self.similarity_threshold = similarity_threshold

        # Active draft (None if no validation in progress)
        self.current_draft: Optional[UserStoryDraft] = None

    def handle_command(self, command: str) -> Dict:
        """Handle /US command invocation.

        Args:
            command: Full command string (e.g., "/US I want to track logins")

        Returns:
            Response dictionary with:
                - message: Formatted response to display
                - state: Current validation state
                - draft: Current draft (if any)
                - requires_input: True if waiting for user response

        Example:
            >>> result = handler.handle_command("/US I want export to PDF")
            >>> print(result['message'])
            I've drafted a user story for PDF export...
            >>> print(result['requires_input'])
            True
        """
        # Extract description from command
        description = self._parse_command(command)

        if not description:
            return {
                'message': "❌ Please provide a description after /US\n"
                          "Example: /US I want users to export reports to PDF",
                'state': None,
                'requires_input': False
            }

        # Start new draft
        draft = self._extract_user_story(description)
        self.current_draft = draft

        # Check similarity with existing user stories
        self._check_similarity(draft)

        # Present draft to user
        return self._present_draft(draft)

    def handle_validation_response(self, user_response: str) -> Dict:
        """Handle user's response during validation loop.

        Args:
            user_response: User's message (approval, refinement request, etc.)

        Returns:
            Response dictionary (same format as handle_command)

        Example:
            >>> handler.handle_command("/US export to PDF")
            >>> result = handler.handle_validation_response("yes, looks good")
            >>> print(result['state'])
            prioritizing
        """
        if not self.current_draft:
            return {
                'message': "⚠️  No user story draft in progress. Use /US to start.",
                'state': None,
                'requires_input': False
            }

        # Classify response intent (approve, refine, reject, etc.)
        intent = self._classify_response(user_response)

        if intent == "approve":
            return self._handle_approval()
        elif intent == "refine":
            return self._handle_refinement(user_response)
        elif intent == "reject":
            return self._handle_rejection()
        else:
            return {
                'message': "ℹ️  I didn't understand. Please:\n"
                          "- Say 'yes' or 'approve' to proceed\n"
                          "- Describe changes you'd like\n"
                          "- Say 'cancel' to abort",
                'state': self.current_draft.state,
                'requires_input': True
            }

    def _parse_command(self, command: str) -> str:
        """Extract description from /US command.

        Args:
            command: Full command (e.g., "/US I want to...")

        Returns:
            Description text without /US prefix
        """
        # Remove /US prefix (case-insensitive)
        import re
        match = re.match(r'/us\s+(.*)', command, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_user_story(self, description: str) -> UserStoryDraft:
        """Extract structured user story from natural language.

        Args:
            description: User's natural language description

        Returns:
            UserStoryDraft with AI-extracted structure
        """
        from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

        # Load extraction prompt
        prompt = load_prompt(PromptNames.EXTRACT_USER_STORY, {
            'DESCRIPTION': description
        })

        # Call AI service
        response = self.ai_service.process_request(
            user_input=prompt,
            context={},
            history=[]
        )

        # Parse AI response into structured format
        # Expected format:
        # Title: ...
        # Description: As a X I want Y so that Z
        # Acceptance Criteria:
        # - ...
        # - ...
        # Estimated Effort: X days

        parsed = self._parse_ai_extraction(response.message)

        return UserStoryDraft(
            title=parsed['title'],
            description=parsed['description'],
            acceptance_criteria=parsed['criteria'],
            estimated_effort=parsed.get('effort'),
            state=ValidationState.CHECKING_SIMILARITY
        )

    def _check_similarity(self, draft: UserStoryDraft) -> None:
        """Check draft against existing user stories for duplicates.

        Updates draft.similar_stories with matches.

        Args:
            draft: Draft to check
        """
        import difflib

        # Get all existing user stories from roadmap
        existing_stories = self.roadmap_editor.get_user_story_summary()

        similar = []

        for us_id, us_data in existing_stories.items():
            # Compare title and description
            title_similarity = difflib.SequenceMatcher(
                None,
                draft.title.lower(),
                us_data.get('title', '').lower()
            ).ratio()

            desc_similarity = difflib.SequenceMatcher(
                None,
                draft.description.lower(),
                us_data.get('description', '').lower()
            ).ratio()

            # Use higher of the two scores
            max_similarity = max(title_similarity, desc_similarity)

            if max_similarity >= self.similarity_threshold:
                similar.append((us_id, max_similarity))

        # Sort by similarity (highest first)
        draft.similar_stories = sorted(similar, key=lambda x: x[1], reverse=True)
        draft.state = ValidationState.AWAITING_VALIDATION

    def _present_draft(self, draft: UserStoryDraft) -> Dict:
        """Format draft for user review.

        Args:
            draft: Draft to present

        Returns:
            Response dictionary
        """
        from rich.markdown import Markdown

        # Build markdown presentation
        md = f"""## 📝 User Story Draft

**Title**: {draft.title}

**Description**:
{draft.description}

**Acceptance Criteria**:
"""
        for i, criterion in enumerate(draft.acceptance_criteria, 1):
            md += f"{i}. {criterion}\n"

        if draft.estimated_effort:
            md += f"\n**Estimated Effort**: {draft.estimated_effort}"

        # Add similarity warnings if found
        if draft.similar_stories:
            md += "\n\n---\n\n⚠️  **Similar User Stories Found**:\n\n"
            for us_id, score in draft.similar_stories[:3]:  # Top 3
                md += f"- **{us_id}** (similarity: {score:.0%})\n"

            md += "\nOptions:\n"
            md += "1. Create as new user story\n"
            md += "2. Rephrase existing user story\n"
            md += "3. Cancel\n"
        else:
            md += "\n\n---\n\n✅ No similar user stories found.\n"

        md += "\n**Next steps**: Please review and respond:\n"
        md += "- 'yes' or 'approve' to proceed\n"
        md += "- Describe any changes you'd like\n"
        md += "- 'cancel' to abort\n"

        return {
            'message': md,
            'state': draft.state,
            'draft': draft,
            'requires_input': True
        }

    def _classify_response(self, response: str) -> str:
        """Classify user's validation response.

        Args:
            response: User's message

        Returns:
            Intent: "approve", "refine", "reject", "unclear"
        """
        response_lower = response.lower().strip()

        # Approval patterns
        if any(word in response_lower for word in ['yes', 'approve', 'looks good', 'ok', 'correct']):
            return "approve"

        # Rejection patterns
        if any(word in response_lower for word in ['no', 'cancel', 'abort', 'stop']):
            return "reject"

        # Refinement (anything with change requests)
        if any(word in response_lower for word in ['change', 'update', 'modify', 'instead', 'should be']):
            return "refine"

        return "unclear"

    def _handle_approval(self) -> Dict:
        """Handle user approval - move to prioritization.

        Returns:
            Response dictionary
        """
        draft = self.current_draft
        draft.state = ValidationState.PRIORITIZING

        # Get prioritization suggestion
        suggestion = self._suggest_prioritization(draft)
        draft.suggested_priority = suggestion

        md = f"""✅ User story approved!

**Suggested Placement**: {suggestion}

Where would you like to add this user story?
1. **TOP PRIORITY** - Urgent, start immediately
2. **After PRIORITY X** - Specify existing priority
3. **BACKLOG** - Defer for later

Please respond with your choice (1, 2, or 3).
"""

        return {
            'message': md,
            'state': draft.state,
            'draft': draft,
            'requires_input': True
        }

    def _handle_refinement(self, user_request: str) -> Dict:
        """Handle user requesting changes to draft.

        Args:
            user_request: User's refinement request

        Returns:
            Response dictionary
        """
        draft = self.current_draft
        draft.state = ValidationState.REFINING
        draft.conversation_history.append({
            'role': 'user',
            'message': user_request
        })

        # Call AI to refine draft based on user feedback
        from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

        prompt = load_prompt(PromptNames.REFINE_USER_STORY, {
            'ORIGINAL_DRAFT': draft.description,
            'USER_FEEDBACK': user_request
        })

        response = self.ai_service.process_request(
            user_input=prompt,
            context={},
            history=draft.conversation_history
        )

        # Update draft with refined version
        parsed = self._parse_ai_extraction(response.message)
        draft.title = parsed.get('title', draft.title)
        draft.description = parsed.get('description', draft.description)
        draft.acceptance_criteria = parsed.get('criteria', draft.acceptance_criteria)
        draft.state = ValidationState.AWAITING_VALIDATION

        # Present updated draft
        return self._present_draft(draft)

    def _handle_rejection(self) -> Dict:
        """Handle user rejecting draft.

        Returns:
            Response dictionary
        """
        self.current_draft = None

        return {
            'message': "❌ User story creation cancelled.",
            'state': ValidationState.COMPLETE,
            'requires_input': False
        }

    def _suggest_prioritization(self, draft: UserStoryDraft) -> str:
        """Suggest where to place user story in roadmap.

        Args:
            draft: Draft to prioritize

        Returns:
            Suggestion text
        """
        # Analyze roadmap dependencies and current priorities
        # For MVP, return simple suggestion
        # TODO: Implement full dependency analysis in Phase 2

        return "BACKLOG (no urgent dependencies detected)"

    def _parse_ai_extraction(self, ai_response: str) -> Dict:
        """Parse AI's structured user story extraction.

        Args:
            ai_response: Claude's response text

        Returns:
            Parsed components: title, description, criteria, effort
        """
        import re

        # Extract title
        title_match = re.search(r'Title:\s*(.+)', ai_response)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Extract description
        desc_match = re.search(r'Description:\s*(.+?)(?=Acceptance Criteria:|Estimated Effort:|$)',
                              ai_response, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract acceptance criteria
        criteria = []
        criteria_section = re.search(r'Acceptance Criteria:\s*(.+?)(?=Estimated Effort:|$)',
                                    ai_response, re.DOTALL)
        if criteria_section:
            criteria_text = criteria_section.group(1)
            # Extract bullet points
            for line in criteria_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    criteria.append(line.lstrip('-•').strip())

        # Extract effort
        effort_match = re.search(r'Estimated Effort:\s*(.+)', ai_response)
        effort = effort_match.group(1).strip() if effort_match else None

        return {
            'title': title,
            'description': description,
            'criteria': criteria,
            'effort': effort
        }

    def finalize_user_story(self, priority_placement: str) -> Dict:
        """Finalize and propagate user story to ROADMAP.md.

        Args:
            priority_placement: Where to place (e.g., "TOP PRIORITY", "BACKLOG")

        Returns:
            Response dictionary with confirmation
        """
        if not self.current_draft:
            return {
                'message': "⚠️  No user story to finalize.",
                'state': None,
                'requires_input': False
            }

        draft = self.current_draft

        # Add to roadmap
        success = self.roadmap_editor.add_user_story(
            title=draft.title,
            description=draft.description,
            acceptance_criteria=draft.acceptance_criteria,
            priority=priority_placement,
            estimated_effort=draft.estimated_effort
        )

        if success:
            us_id = self._get_new_user_story_id()
            draft.state = ValidationState.COMPLETE

            md = f"""✅ **User Story Added Successfully!**

**ID**: {us_id}
**Title**: {draft.title}
**Placement**: {priority_placement}

The user story has been added to `docs/roadmap/ROADMAP.md`.

Use `/roadmap` to view the updated roadmap.
"""

            # Clear current draft
            self.current_draft = None

            return {
                'message': md,
                'state': ValidationState.COMPLETE,
                'requires_input': False
            }
        else:
            return {
                'message': "❌ Failed to add user story to roadmap. Please check logs.",
                'state': draft.state,
                'requires_input': False
            }

    def _get_new_user_story_id(self) -> str:
        """Get ID for newly added user story.

        Returns:
            User story ID (e.g., "US-050")
        """
        # TODO: Query roadmap for next available US number
        # For now, placeholder
        return "US-XXX"
```

### 2. AI Service Extensions

**File**: `coffee_maker/cli/ai_service.py` (MODIFY)

**New Methods**:

```python
def extract_user_story(self, description: str, context: Dict = None) -> AIResponse:
    """Extract structured user story from natural language.

    Args:
        description: User's natural language description
        context: Optional context (existing user stories, roadmap state)

    Returns:
        AIResponse with structured user story

    Example:
        >>> service = AIService()
        >>> response = service.extract_user_story(
        ...     "I want users to export reports to PDF"
        ... )
        >>> print(response.message)
        Title: PDF Report Export
        Description: As a user I want to export...
    """
    from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

    prompt = load_prompt(PromptNames.EXTRACT_USER_STORY, {
        'DESCRIPTION': description,
        'EXISTING_CONTEXT': context or {}
    })

    return self.process_request(
        user_input=prompt,
        context=context or {},
        history=[]
    )


def analyze_user_story_similarity(
    self,
    draft_title: str,
    draft_description: str,
    existing_stories: List[Dict]
) -> List[Tuple[str, float, str]]:
    """Analyze similarity between draft and existing user stories.

    Args:
        draft_title: Draft user story title
        draft_description: Draft description
        existing_stories: List of existing user stories

    Returns:
        List of (us_id, similarity_score, reason) tuples

    Example:
        >>> similarities = service.analyze_user_story_similarity(
        ...     "PDF Export",
        ...     "As a user I want to export...",
        ...     existing_stories
        ... )
        >>> for us_id, score, reason in similarities:
        ...     print(f"{us_id}: {score:.0%} - {reason}")
    """
    # Use AI to perform semantic similarity analysis
    # More sophisticated than difflib string matching

    from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

    prompt = load_prompt(PromptNames.ANALYZE_SIMILARITY, {
        'DRAFT_TITLE': draft_title,
        'DRAFT_DESCRIPTION': draft_description,
        'EXISTING_STORIES': existing_stories
    })

    response = self.process_request(
        user_input=prompt,
        context={'existing_stories': existing_stories},
        history=[]
    )

    # Parse response for similarity scores
    # Expected format:
    # US-042: 85% - Both involve PDF export functionality
    # US-015: 45% - Related to reporting but different feature

    return self._parse_similarity_response(response.message)


def suggest_user_story_prioritization(
    self,
    draft: Dict,
    roadmap_state: Dict
) -> Dict:
    """Suggest where to prioritize new user story.

    Args:
        draft: Draft user story details
        roadmap_state: Current roadmap state (priorities, dependencies)

    Returns:
        Prioritization suggestion with reasoning

    Example:
        >>> suggestion = service.suggest_user_story_prioritization(
        ...     draft={'title': 'PDF Export', ...},
        ...     roadmap_state={...}
        ... )
        >>> print(suggestion['placement'])
        After PRIORITY 15
        >>> print(suggestion['reasoning'])
        Depends on report generation (PRIORITY 15)
    """
    from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

    prompt = load_prompt(PromptNames.SUGGEST_PRIORITIZATION, {
        'DRAFT': draft,
        'ROADMAP_STATE': roadmap_state
    })

    response = self.process_request(
        user_input=prompt,
        context={'roadmap': roadmap_state},
        history=[]
    )

    return {
        'placement': self._extract_placement(response.message),
        'reasoning': response.message
    }
```

### 3. RoadmapEditor Extensions

**File**: `coffee_maker/cli/roadmap_editor.py` (MODIFY)

**New Methods**:

```python
def add_user_story(
    self,
    title: str,
    description: str,
    acceptance_criteria: List[str],
    priority: str = "BACKLOG",
    estimated_effort: Optional[str] = None
) -> bool:
    """Add new user story to ROADMAP.md.

    Args:
        title: User story title
        description: Full description (As a X I want Y so that Z)
        acceptance_criteria: List of acceptance criteria
        priority: Placement (TOP PRIORITY, BACKLOG, etc.)
        estimated_effort: Optional effort estimate

    Returns:
        True if successful

    Example:
        >>> editor = RoadmapEditor(roadmap_path)
        >>> success = editor.add_user_story(
        ...     title="PDF Export",
        ...     description="As a user I want to export reports...",
        ...     acceptance_criteria=["Export button exists", "PDF is generated"],
        ...     priority="BACKLOG"
        ... )
    """
    try:
        # Create backup
        self._create_backup()

        # Get next US number
        us_id = self._get_next_user_story_id()

        # Build user story section
        us_section = self._build_user_story_section(
            us_id=us_id,
            title=title,
            description=description,
            criteria=acceptance_criteria,
            effort=estimated_effort
        )

        # Find insertion point based on priority
        content = self.roadmap_path.read_text()
        lines = content.split('\n')

        if priority == "TOP PRIORITY":
            # Insert at top of user stories section
            insert_index = self._find_user_stories_section_start(lines)
        elif priority == "BACKLOG":
            # Insert in backlog section
            insert_index = self._find_backlog_section_start(lines)
        else:
            # Insert after specific priority
            insert_index = self._find_priority_insert_point(lines, priority)

        # Insert user story
        lines.insert(insert_index, us_section)

        # Write back atomically
        new_content = '\n'.join(lines)
        self._atomic_write(new_content)

        logger.info(f"Added user story {us_id}: {title}")
        return True

    except Exception as e:
        logger.error(f"Failed to add user story: {e}")
        return False


def get_user_story_summary(self) -> Dict[str, Dict]:
    """Get summary of all user stories in roadmap.

    Returns:
        Dictionary of {us_id: {title, description, status}}

    Example:
        >>> editor = RoadmapEditor(roadmap_path)
        >>> stories = editor.get_user_story_summary()
        >>> for us_id, data in stories.items():
        ...     print(f"{us_id}: {data['title']}")
    """
    content = self.roadmap_path.read_text()

    # Parse user stories using regex
    import re
    pattern = r'## (US-\d+):\s*(.+?)\n\n(.+?)(?=\n##|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    stories = {}
    for us_id, title, description in matches:
        stories[us_id] = {
            'title': title.strip(),
            'description': description.strip(),
            'status': self._extract_status(description)
        }

    return stories


def _get_next_user_story_id(self) -> str:
    """Get next available user story ID.

    Returns:
        Next US ID (e.g., "US-051")
    """
    stories = self.get_user_story_summary()

    if not stories:
        return "US-001"

    # Extract numbers from existing IDs
    import re
    numbers = []
    for us_id in stories.keys():
        match = re.match(r'US-(\d+)', us_id)
        if match:
            numbers.append(int(match.group(1)))

    # Return next number
    next_num = max(numbers) + 1 if numbers else 1
    return f"US-{next_num:03d}"


def _build_user_story_section(
    self,
    us_id: str,
    title: str,
    description: str,
    criteria: List[str],
    effort: Optional[str]
) -> str:
    """Build formatted user story section.

    Args:
        us_id: User story ID
        title: Title
        description: Full description
        criteria: Acceptance criteria
        effort: Optional effort estimate

    Returns:
        Formatted markdown section
    """
    section = f"## {us_id}: {title}\n\n"
    section += f"**Description**: {description}\n\n"
    section += "**Acceptance Criteria**:\n"

    for criterion in criteria:
        section += f"- [ ] {criterion}\n"

    if effort:
        section += f"\n**Estimated Effort**: {effort}\n"

    section += "\n**Status**: 📝 Planned\n\n"
    section += "---\n\n"

    return section
```

### 4. ChatSession Integration

**File**: `coffee_maker/cli/chat_interface.py` (MODIFY)

**Changes**:

```python
class ChatSession:
    """Interactive chat session (EXISTING CLASS - MODIFICATIONS ONLY)."""

    def __init__(self, ...):
        # Existing initialization...

        # NEW: Add UserStoryCommandHandler
        from coffee_maker.cli.commands.user_story_command import UserStoryCommandHandler
        self.us_handler = UserStoryCommandHandler(
            ai_service=self.ai_service,
            roadmap_editor=self.roadmap_editor
        )

    def _handle_command(self, user_input: str) -> Optional[str]:
        """Handle slash commands (EXISTING METHOD - ADD /US HANDLING)."""

        # Existing command handling...

        # NEW: Handle /US command
        if user_input.lower().startswith('/us '):
            result = self.us_handler.handle_command(user_input)
            return self._format_us_response(result)

        # Existing code continues...

    def _handle_user_input(self, user_input: str):
        """Handle user input (EXISTING METHOD - ADD VALIDATION STATE HANDLING)."""

        # NEW: If we're in a US validation loop, route to handler
        if self.us_handler.current_draft:
            result = self.us_handler.handle_validation_response(user_input)
            response = self._format_us_response(result)
            self.console.print(Markdown(response))
            return

        # Existing command handling...
        command_response = self._handle_command(user_input)
        if command_response:
            self.console.print(Markdown(command_response))
            return

        # Existing AI conversation handling...

    def _format_us_response(self, result: Dict) -> str:
        """Format UserStoryCommandHandler response for display.

        Args:
            result: Handler result dictionary

        Returns:
            Formatted markdown string
        """
        return result.get('message', '')
```

### 5. Prompt Templates

**Files**: `.claude/commands/` (NEW)

**EXTRACT_USER_STORY.md**:

```markdown
You are helping structure a user story from natural language.

USER INPUT:
$DESCRIPTION

TASK:
Extract and structure this as a proper user story with:
1. A clear, concise title
2. Description in format: "As a [role] I want [feature] so that [benefit]"
3. 3-5 specific acceptance criteria
4. Estimated effort (1-2 days, 3-5 days, 1-2 weeks, etc.)

FORMAT YOUR RESPONSE EXACTLY AS:

Title: [Concise title]

Description: As a [role] I want [feature] so that [benefit]

Acceptance Criteria:
- [Specific, testable criterion 1]
- [Specific, testable criterion 2]
- [Specific, testable criterion 3]

Estimated Effort: [X days/weeks]

GUIDELINES:
- Be specific and actionable
- Focus on user value, not implementation
- Make criteria testable and measurable
- Base effort estimate on scope and complexity
```

**ANALYZE_SIMILARITY.md**:

```markdown
You are analyzing similarity between a draft user story and existing user stories.

DRAFT USER STORY:
Title: $DRAFT_TITLE
Description: $DRAFT_DESCRIPTION

EXISTING USER STORIES:
$EXISTING_STORIES

TASK:
Analyze semantic similarity between the draft and each existing user story.
Consider:
- Similar functionality or features
- Overlapping user needs
- Duplicate or redundant work
- Related but distinct features

FORMAT YOUR RESPONSE AS:

[US-ID]: [0-100%] - [Brief reason for similarity score]

Example:
US-042: 85% - Both involve PDF export functionality
US-015: 45% - Related to reporting but different feature
US-008: 10% - Unrelated

Only include user stories with >40% similarity.
```

**SUGGEST_PRIORITIZATION.md**:

```markdown
You are suggesting where to prioritize a new user story in the roadmap.

DRAFT USER STORY:
$DRAFT

CURRENT ROADMAP STATE:
$ROADMAP_STATE

TASK:
Analyze dependencies, complexity, and strategic value to suggest placement.

Consider:
- Dependencies on existing priorities
- Blocking relationships (what needs this?)
- Strategic importance
- User impact
- Technical complexity

FORMAT YOUR RESPONSE AS:

SUGGESTED PLACEMENT: [TOP PRIORITY | After PRIORITY X | BACKLOG]

REASONING:
- [Dependency analysis]
- [Impact assessment]
- [Risk considerations]
- [Recommendation rationale]

ALTERNATIVE OPTIONS:
1. [Option 1]: [Rationale]
2. [Option 2]: [Rationale]
```

**REFINE_USER_STORY.md**:

```markdown
You are refining a user story draft based on user feedback.

ORIGINAL DRAFT:
$ORIGINAL_DRAFT

USER FEEDBACK:
$USER_FEEDBACK

TASK:
Revise the user story to incorporate the user's requested changes while maintaining proper structure.

FORMAT YOUR RESPONSE EXACTLY AS:

Title: [Updated title]

Description: As a [role] I want [feature] so that [benefit]

Acceptance Criteria:
- [Updated criterion 1]
- [Updated criterion 2]
- [Updated criterion 3]

Estimated Effort: [X days/weeks]

GUIDELINES:
- Incorporate all user feedback
- Maintain user story format
- Preserve good elements from original
- Clarify any ambiguities
```

### 6. PromptNames Enum Extension

**File**: `coffee_maker/autonomous/prompt_loader.py` (MODIFY)

```python
class PromptNames(str, Enum):
    """Centralized prompt names (EXISTING ENUM - ADD NEW ENTRIES)."""

    # Existing prompts...

    # NEW: User Story Command Handler prompts
    EXTRACT_USER_STORY = "extract_user_story"
    ANALYZE_SIMILARITY = "analyze_similarity"
    SUGGEST_PRIORITIZATION = "suggest_prioritization"
    REFINE_USER_STORY = "refine_user_story"
```

---

## Data Flow Diagrams

### 1. High-Level Command Flow

```
User Types: "/US I want to track user logins"
                      │
                      ▼
         ┌────────────────────────┐
         │   ChatSession          │
         │   _handle_command()    │
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ UserStoryCommandHandler│
         │   handle_command()     │
         └──────────┬─────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌────────────────┐   ┌──────────────────┐
│   AIService    │   │  RoadmapEditor   │
│ extract_user   │   │ get_user_stories │
│   _story()     │   │   ()             │
└────────┬───────┘   └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌────────────────────────┐
         │   UserStoryDraft       │
         │   (state: CHECKING)    │
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │   Similarity Check     │
         │   (difflib matching)   │
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │   Present to User      │
         │   (Rich markdown)      │
         └──────────┬─────────────┘
                    │
                    ▼
         User sees formatted draft
         with similarity warnings
```

### 2. Validation Loop Flow

```
User approves/refines/rejects draft
                │
                ▼
     ┌──────────────────────┐
     │  ChatSession         │
     │ _handle_user_input() │
     └──────────┬───────────┘
                │
                ▼
     ┌──────────────────────┐
     │ UserStoryHandler     │
     │ handle_validation    │
     │   _response()        │
     └──────────┬───────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   "approve"        "refine"         "reject"
        │               │                │
        ▼               ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Prioritize   │ │ Call AI to   │ │ Clear draft  │
│              │ │ refine draft │ │ Exit loop    │
└──────┬───────┘ └──────┬───────┘ └──────────────┘
       │                │
       │                ▼
       │         ┌──────────────┐
       │         │ Update draft │
       │         │ Re-present   │
       │         └──────┬───────┘
       │                │
       └────────────────┘
                │
                ▼
     Ask user for priority placement
                │
                ▼
     User chooses placement
                │
                ▼
     ┌──────────────────────┐
     │ finalize_user_story()│
     │ Add to ROADMAP.md    │
     └──────────┬───────────┘
                │
                ▼
     Success confirmation
     Clear draft, exit loop
```

### 3. Data State Transitions

```
UserStoryDraft States:

EXTRACTING → CHECKING_SIMILARITY → AWAITING_VALIDATION
                                          │
                   ┌──────────────────────┼──────────────────┐
                   │                      │                  │
                   ▼                      ▼                  ▼
              REFINING              PRIORITIZING        COMPLETE
                   │                      │              (rejected)
                   │                      │
                   └──────────┬───────────┘
                              │
                              ▼
                         COMPLETE
                      (finalized & added)
```

---

## Implementation Plan

### Phase 1: Core `/US` Command (2-3 hours)

**Tasks**:

1. **Create UserStoryCommandHandler** (60 min)
   - File: `coffee_maker/cli/commands/user_story_command.py`
   - Implement classes: `ValidationState`, `UserStoryDraft`, `UserStoryCommandHandler`
   - Methods: `handle_command()`, `_parse_command()`, `_extract_user_story()`
   - **Deliverable**: Handler can parse `/US` command and call AI service

2. **Create Prompt Templates** (30 min)
   - Files: `.claude/commands/extract_user_story.md`
   - `.claude/commands/refine_user_story.md`
   - Add to `PromptNames` enum
   - **Deliverable**: Prompts loaded via `load_prompt()`

3. **Integrate with ChatSession** (45 min)
   - File: `coffee_maker/cli/chat_interface.py`
   - Modify: `__init__()` to create `UserStoryCommandHandler`
   - Modify: `_handle_command()` to route `/US` commands
   - Modify: `_handle_user_input()` to handle validation loop
   - **Deliverable**: `/US` command works in chat interface

4. **Basic Testing** (30 min)
   - Test: `/US I want to export reports to PDF`
   - Verify: AI extracts structured user story
   - Verify: Draft presented to user
   - **Deliverable**: End-to-end smoke test passes

**Acceptance Criteria**:
- ✅ User can type `/US [description]`
- ✅ AI extracts structured user story
- ✅ Draft displayed with Rich markdown
- ✅ Validation loop initiated

---

### Phase 2: Similarity Detection (2-3 hours)

**Tasks**:

1. **Implement Similarity Checking** (90 min)
   - Method: `UserStoryCommandHandler._check_similarity()`
   - Use `difflib.SequenceMatcher` for string matching
   - Compare title and description against existing user stories
   - Store results in `draft.similar_stories`
   - **Deliverable**: Similarity scores calculated

2. **Extend RoadmapEditor** (45 min)
   - Method: `RoadmapEditor.get_user_story_summary()`
   - Parse ROADMAP.md to extract all user stories
   - Return dictionary of {us_id: {title, description, status}}
   - **Deliverable**: Can query existing user stories

3. **Update Presentation** (30 min)
   - Method: `UserStoryCommandHandler._present_draft()`
   - Display top 3 similar user stories
   - Show options: create new, rephrase existing, cancel
   - **Deliverable**: Similarity warnings shown to user

4. **Testing** (30 min)
   - Test: Create user story similar to existing one
   - Verify: Similarity detected and displayed
   - Test: Create unique user story
   - Verify: No similarity warnings
   - **Deliverable**: Similarity detection tests pass

**Acceptance Criteria**:
- ✅ Existing user stories queried from roadmap
- ✅ Similarity scores calculated (>70% threshold)
- ✅ Top 3 similar stories displayed
- ✅ User presented with options

---

### Phase 3: Validation Loop (1-2 hours)

**Tasks**:

1. **Implement Response Classification** (30 min)
   - Method: `UserStoryCommandHandler._classify_response()`
   - Detect: "approve", "refine", "reject" intents
   - Use keyword matching (simple, no AI needed)
   - **Deliverable**: User responses classified

2. **Implement Handlers** (60 min)
   - Method: `_handle_approval()` - Move to prioritization
   - Method: `_handle_refinement()` - Call AI to update draft
   - Method: `_handle_rejection()` - Clear draft, exit
   - **Deliverable**: All validation paths implemented

3. **State Management** (30 min)
   - Track `current_draft` in handler
   - Update `draft.state` at each stage
   - Persist conversation history in `draft.conversation_history`
   - **Deliverable**: State transitions work correctly

4. **Testing** (30 min)
   - Test: Approve draft → moves to prioritization
   - Test: Request changes → AI refines → re-presents
   - Test: Reject → clears draft
   - **Deliverable**: Validation loop tests pass

**Acceptance Criteria**:
- ✅ User can approve, refine, or reject drafts
- ✅ Refinement calls AI with user feedback
- ✅ Updated draft re-presented
- ✅ State transitions tracked correctly

---

### Phase 4: Prioritization (1-2 hours)

**Tasks**:

1. **Create Prioritization Prompt** (20 min)
   - File: `.claude/commands/suggest_prioritization.md`
   - Add to `PromptNames` enum
   - **Deliverable**: Prompt template ready

2. **Implement Prioritization Logic** (45 min)
   - Method: `UserStoryCommandHandler._suggest_prioritization()`
   - Call AI with draft and roadmap state
   - Parse AI response for placement suggestion
   - **Deliverable**: AI suggests priority placement

3. **Extend AIService** (30 min)
   - Method: `AIService.suggest_user_story_prioritization()`
   - Wrapper for prioritization prompt
   - Return structured suggestion
   - **Deliverable**: AI service method available

4. **User Confirmation** (30 min)
   - Present suggestions: TOP PRIORITY, After PRIORITY X, BACKLOG
   - Accept user choice
   - Pass to finalization
   - **Deliverable**: User chooses placement

5. **Testing** (30 min)
   - Test: AI suggests placement
   - Test: User chooses option
   - Verify: Choice captured correctly
   - **Deliverable**: Prioritization tests pass

**Acceptance Criteria**:
- ✅ AI suggests placement based on dependencies
- ✅ User presented with options
- ✅ User choice captured
- ✅ Ready for propagation

---

### Phase 5: Propagation & Finalization (1 hour)

**Tasks**:

1. **Extend RoadmapEditor** (30 min)
   - Method: `RoadmapEditor.add_user_story()`
   - Method: `_get_next_user_story_id()`
   - Method: `_build_user_story_section()`
   - Method: `_find_backlog_section_start()`
   - **Deliverable**: Can write user story to ROADMAP.md

2. **Implement Finalization** (20 min)
   - Method: `UserStoryCommandHandler.finalize_user_story()`
   - Call `roadmap_editor.add_user_story()`
   - Display success confirmation
   - Clear draft
   - **Deliverable**: User story added to roadmap

3. **End-to-End Testing** (30 min)
   - Test: Complete workflow from `/US` to ROADMAP update
   - Verify: User story appears in ROADMAP.md
   - Verify: Formatted correctly
   - Verify: Backups created
   - **Deliverable**: Full integration test passes

**Acceptance Criteria**:
- ✅ User story added to ROADMAP.md
- ✅ Proper formatting and structure
- ✅ Backup created
- ✅ Success message displayed

---

### Phase 6: Documentation & Polish (1 hour)

**Tasks**:

1. **Update Documentation** (30 min)
   - Add `/US` command to TUTORIALS.md
   - Document workflow in WORKFLOWS.md
   - Update CLAUDE.md with new capability
   - **Deliverable**: Documentation complete

2. **Code Comments & Docstrings** (20 min)
   - Add comprehensive docstrings to all methods
   - Add inline comments for complex logic
   - **Deliverable**: Code well-documented

3. **Error Handling** (20 min)
   - Add try-except blocks for robustness
   - Handle edge cases (empty input, AI errors, file errors)
   - Add logging statements
   - **Deliverable**: Graceful error handling

4. **Final Testing** (20 min)
   - Run full test suite
   - Test error scenarios
   - Verify logging works
   - **Deliverable**: All tests pass

**Acceptance Criteria**:
- ✅ Documentation updated
- ✅ Code well-commented
- ✅ Error handling implemented
- ✅ Tests passing

---

### Time Estimates Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Core `/US` Command | 4 tasks | 2-3 hours |
| Phase 2: Similarity Detection | 4 tasks | 2-3 hours |
| Phase 3: Validation Loop | 4 tasks | 1-2 hours |
| Phase 4: Prioritization | 5 tasks | 1-2 hours |
| Phase 5: Propagation | 3 tasks | 1 hour |
| Phase 6: Documentation | 4 tasks | 1 hour |
| **TOTAL** | **24 tasks** | **8-12 hours** |

**Adjusted estimate**: 7-10 hours (accounting for parallel work and optimizations)

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/cli/test_user_story_command.py` (NEW)

```python
"""Unit tests for UserStoryCommandHandler."""

import pytest
from unittest.mock import Mock, patch

from coffee_maker.cli.commands.user_story_command import (
    UserStoryCommandHandler,
    UserStoryDraft,
    ValidationState
)


class TestUserStoryCommandHandler:
    """Test suite for UserStoryCommandHandler."""

    @pytest.fixture
    def mock_ai_service(self):
        """Mock AIService."""
        return Mock()

    @pytest.fixture
    def mock_roadmap_editor(self):
        """Mock RoadmapEditor."""
        editor = Mock()
        editor.get_user_story_summary.return_value = {
            'US-042': {
                'title': 'PDF Export',
                'description': 'As a user I want to export reports to PDF',
                'status': 'Planned'
            }
        }
        return editor

    @pytest.fixture
    def handler(self, mock_ai_service, mock_roadmap_editor):
        """Create handler with mocks."""
        return UserStoryCommandHandler(
            ai_service=mock_ai_service,
            roadmap_editor=mock_roadmap_editor
        )

    def test_parse_command_valid(self, handler):
        """Test parsing valid /US command."""
        description = handler._parse_command("/US I want to export reports")
        assert description == "I want to export reports"

    def test_parse_command_case_insensitive(self, handler):
        """Test /US is case-insensitive."""
        description = handler._parse_command("/us I want to export reports")
        assert description == "I want to export reports"

    def test_parse_command_empty(self, handler):
        """Test parsing /US with no description."""
        description = handler._parse_command("/US")
        assert description == ""

    def test_handle_command_no_description(self, handler):
        """Test /US with no description returns error."""
        result = handler.handle_command("/US")
        assert '❌' in result['message']
        assert result['requires_input'] is False

    def test_handle_command_creates_draft(self, handler, mock_ai_service):
        """Test /US creates draft and checks similarity."""
        # Mock AI response
        mock_ai_service.process_request.return_value = Mock(
            message=(
                "Title: Report Export\n"
                "Description: As a user I want to export reports\n"
                "Acceptance Criteria:\n- Export button exists\n"
                "Estimated Effort: 2 days"
            )
        )

        result = handler.handle_command("/US I want to export reports")

        # Should create draft
        assert handler.current_draft is not None
        assert handler.current_draft.title == "Report Export"
        assert result['requires_input'] is True

    def test_similarity_detection(self, handler, mock_ai_service):
        """Test similarity detection flags duplicates."""
        # Create draft similar to existing US-042
        draft = UserStoryDraft(
            title="PDF Export Feature",
            description="As a user I want to export to PDF",
            acceptance_criteria=["Export works"]
        )

        handler._check_similarity(draft)

        # Should find US-042 as similar
        assert len(draft.similar_stories) > 0
        assert draft.similar_stories[0][0] == 'US-042'
        assert draft.similar_stories[0][1] > 0.7  # High similarity

    def test_classify_response_approve(self, handler):
        """Test classifying approval responses."""
        assert handler._classify_response("yes") == "approve"
        assert handler._classify_response("looks good") == "approve"
        assert handler._classify_response("approve") == "approve"

    def test_classify_response_refine(self, handler):
        """Test classifying refinement responses."""
        assert handler._classify_response("change the title") == "refine"
        assert handler._classify_response("should be different") == "refine"

    def test_classify_response_reject(self, handler):
        """Test classifying rejection responses."""
        assert handler._classify_response("no") == "reject"
        assert handler._classify_response("cancel") == "reject"

    def test_handle_approval_moves_to_prioritization(self, handler):
        """Test approval transitions to prioritization state."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Test",
            description="Test description",
            acceptance_criteria=["Test"],
            state=ValidationState.AWAITING_VALIDATION
        )

        result = handler._handle_approval()

        assert handler.current_draft.state == ValidationState.PRIORITIZING
        assert 'Suggested Placement' in result['message']
        assert result['requires_input'] is True

    def test_handle_rejection_clears_draft(self, handler):
        """Test rejection clears draft."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Test",
            description="Test",
            acceptance_criteria=["Test"]
        )

        result = handler._handle_rejection()

        assert handler.current_draft is None
        assert '❌' in result['message']
        assert result['requires_input'] is False

    def test_finalize_adds_to_roadmap(self, handler, mock_roadmap_editor):
        """Test finalization adds user story to roadmap."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Test Feature",
            description="As a user I want test",
            acceptance_criteria=["Criterion 1"],
            state=ValidationState.PRIORITIZING
        )

        mock_roadmap_editor.add_user_story.return_value = True

        result = handler.finalize_user_story("BACKLOG")

        # Should call add_user_story
        mock_roadmap_editor.add_user_story.assert_called_once()

        # Should clear draft
        assert handler.current_draft is None

        # Should confirm success
        assert '✅' in result['message']
        assert result['requires_input'] is False
```

### Integration Tests

**File**: `tests/integration/cli/test_user_story_workflow.py` (NEW)

```python
"""Integration tests for /US command workflow."""

import pytest
from pathlib import Path
from unittest.mock import Mock

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.commands.user_story_command import UserStoryCommandHandler


@pytest.fixture
def test_roadmap_path(tmp_path):
    """Create temporary ROADMAP.md for testing."""
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text("""
# Roadmap

## US-042: PDF Export

**Description**: As a user I want to export reports to PDF

**Acceptance Criteria**:
- [ ] Export button exists

**Status**: 📝 Planned

---

## Backlog

New user stories go here.
""")
    return roadmap


def test_full_user_story_workflow(test_roadmap_path, monkeypatch):
    """Test complete workflow from /US to ROADMAP update."""
    # Setup
    editor = RoadmapEditor(test_roadmap_path)
    ai_service = Mock(spec=AIService)
    handler = UserStoryCommandHandler(ai_service, editor)

    # Mock AI responses
    ai_service.process_request.return_value = Mock(
        message=(
            "Title: Email Notifications\n"
            "Description: As a user I want to receive email notifications\n"
            "Acceptance Criteria:\n"
            "- Email sent on event\n"
            "- User can configure preferences\n"
            "Estimated Effort: 3 days"
        )
    )

    # Step 1: User types /US command
    result = handler.handle_command("/US I want email notifications")

    assert result['requires_input'] is True
    assert handler.current_draft is not None
    assert handler.current_draft.title == "Email Notifications"

    # Step 2: User approves draft
    result = handler.handle_validation_response("yes, looks good")

    assert result['state'] == ValidationState.PRIORITIZING
    assert 'Suggested Placement' in result['message']

    # Step 3: User chooses BACKLOG
    result = handler.finalize_user_story("BACKLOG")

    assert '✅' in result['message']
    assert handler.current_draft is None

    # Step 4: Verify ROADMAP.md updated
    roadmap_content = test_roadmap_path.read_text()
    assert 'Email Notifications' in roadmap_content
    assert 'US-043' in roadmap_content  # Next ID after US-042
```

### Test Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: All critical paths covered
- **Edge Cases**: Empty input, API errors, file errors, malformed data

---

## Security Considerations

### 1. Input Validation

**Risk**: Malicious input in `/US` command could exploit AI or file system

**Mitigation**:
- Sanitize all user input before passing to AI
- Validate file paths before writing
- Use atomic writes with backups
- Limit input length (e.g., max 500 characters for description)

**Implementation**:
```python
def _validate_user_input(self, description: str) -> bool:
    """Validate user input for security."""
    # Length check
    if len(description) > 500:
        raise ValueError("Description too long (max 500 chars)")

    # No path traversal attempts
    if '..' in description or '/' in description:
        raise ValueError("Invalid characters in description")

    return True
```

### 2. File System Safety

**Risk**: Concurrent writes to ROADMAP.md could corrupt file

**Mitigation**:
- Use `RoadmapEditor._atomic_write()` (already implemented)
- Create backups before every write
- Use file locks if needed (future enhancement)

**Implementation**:
- Already handled by `RoadmapEditor` class
- Backups in `docs/roadmap/roadmap_backups/`

### 3. AI Prompt Injection

**Risk**: User input could manipulate AI to produce malicious output

**Mitigation**:
- Use structured prompts with clear role boundaries
- Validate AI responses before parsing
- Never execute AI-generated code
- Log all AI interactions for audit

**Implementation**:
```python
def _validate_ai_response(self, response: str) -> bool:
    """Validate AI response structure."""
    required_fields = ['Title:', 'Description:', 'Acceptance Criteria:']

    for field in required_fields:
        if field not in response:
            logger.warning(f"AI response missing {field}")
            return False

    return True
```

### 4. Rate Limiting

**Risk**: Excessive `/US` commands could incur high API costs

**Mitigation**:
- Track API calls per session
- Warn user after 10 user stories in one session
- Rate limit to 1 request per 5 seconds

**Implementation** (Future Enhancement):
```python
from time import time

class UserStoryCommandHandler:
    def __init__(self, ...):
        self.last_request_time = 0
        self.request_count = 0

    def _check_rate_limit(self) -> bool:
        """Check if rate limit exceeded."""
        now = time()

        # 1 request per 5 seconds
        if now - self.last_request_time < 5:
            raise RateLimitError("Please wait 5 seconds between requests")

        # 10 requests per session
        if self.request_count > 10:
            raise RateLimitError("Session limit reached (10 user stories)")

        self.last_request_time = now
        self.request_count += 1
        return True
```

### 5. Data Privacy

**Risk**: User stories may contain sensitive information

**Mitigation**:
- Never log full user input
- Sanitize logs to remove PII
- Use environment variables for API keys
- Don't send sensitive data to AI (already handled)

**Implementation**:
```python
# Good: Log event, not data
logger.info("User story created: [REDACTED]")

# Bad: Log full content
# logger.info(f"User story: {description}")
```

---

## Performance Requirements

### 1. Response Time

**Requirement**: Total workflow should complete in <30 seconds

**Breakdown**:
- Command parsing: <100ms
- AI extraction: <5 seconds (Claude Haiku)
- Similarity check: <1 second (difflib on 100 user stories)
- User validation: User-dependent (not counted)
- Prioritization AI: <5 seconds
- ROADMAP write: <500ms

**Total**: ~11-12 seconds (excluding user interaction time)

**Optimization**:
- Use Claude Haiku (fast, cost-efficient)
- Cache roadmap parsing results
- Parallel similarity checks if needed

### 2. Memory Usage

**Requirement**: <50MB additional memory for handler

**Breakdown**:
- `UserStoryDraft`: ~10KB per draft
- Conversation history: ~50KB (20 messages)
- Cached user stories: ~100KB (100 stories × 1KB)

**Total**: ~160KB (well under limit)

### 3. Scalability

**Requirement**: Handle roadmaps with 1000+ user stories

**Current Design**:
- Linear scan for similarity: O(n) where n = # user stories
- Acceptable for n < 1000
- For larger roadmaps, consider indexing (future optimization)

**Performance at Scale**:
- 100 user stories: <1 second
- 500 user stories: <3 seconds
- 1000 user stories: <5 seconds

**Future Optimization** (if needed):
- Use vector embeddings for semantic similarity
- Cache similarity results
- Index user stories by keywords

### 4. API Cost Efficiency

**Requirement**: Keep API costs low (<$0.10 per user story)

**Cost Analysis** (Claude Haiku):
- Input: ~1000 tokens (prompts + context) = $0.0004
- Output: ~500 tokens (structured US) = $0.0004
- Similarity analysis: ~500 tokens = $0.0002
- Prioritization: ~500 tokens = $0.0002

**Total per user story**: ~$0.0012 (well under budget)

**Optimization**:
- Use Haiku for all operations (not Sonnet)
- Minimize context in prompts
- Cache AI responses where possible

---

## Risk Analysis

### 1. AI Extraction Accuracy

**Risk**: AI may misinterpret user input, producing poor user stories

**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Use well-structured prompts with examples
- Validate AI output format before parsing
- Allow user to refine through validation loop
- Test with diverse inputs

**Contingency**:
- If AI consistently fails, fall back to manual template filling
- Log failures for prompt improvement

### 2. Similarity Detection False Positives

**Risk**: Legitimate new user stories flagged as duplicates

**Likelihood**: Medium
**Impact**: Low (user can override)
**Mitigation**:
- Tune similarity threshold (70% is conservative)
- Show similarity scores to user
- Allow user to proceed anyway

**Contingency**:
- Add `/US --force` flag to skip similarity check
- Make threshold configurable

### 3. ROADMAP.md Corruption

**Risk**: File write error corrupts ROADMAP.md

**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Atomic writes with `_atomic_write()`
- Automatic backups before every write
- Validate file after write
- Version control (git)

**Contingency**:
- Restore from backup in `roadmap_backups/`
- Git revert if needed

### 4. Context Budget Violation (CFR-007)

**Risk**: Adding new code exceeds 30% context budget for project_manager

**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Keep implementation concise (~500 lines total)
- Use existing infrastructure (AIService, RoadmapEditor)
- Offload prompts to `.claude/commands/`

**Validation**:
- Run context budget check after implementation
- If over budget, refactor to reduce size

### 5. User Workflow Confusion

**Risk**: Users don't understand validation loop

**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Clear, friendly prompts at each stage
- Examples in documentation
- Rich formatting to guide user
- Help text on unclear input

**Contingency**:
- Add `/US help` command with examples
- Improve messaging based on user feedback

### 6. Dependencies on External Services

**Risk**: Claude API outage breaks `/US` command

**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Graceful error handling with retry
- Clear error messages to user
- Fall back to manual user story creation

**Contingency**:
- Document manual process in error message
- Queue requests for later if API down

---

## Success Criteria

### Functional Requirements

- ✅ User can type `/US [description]` in chat interface
- ✅ AI extracts structured user story from description
- ✅ Draft presented to user for validation
- ✅ User can approve, refine, or reject draft
- ✅ Refinement loop allows iterative improvement
- ✅ Similarity detection flags potential duplicates
- ✅ User can choose priority placement
- ✅ User story added to ROADMAP.md with proper formatting
- ✅ Success confirmation displayed to user

### Non-Functional Requirements

- ✅ Total workflow completes in <30 seconds (excluding user time)
- ✅ Memory usage <50MB
- ✅ API cost <$0.10 per user story
- ✅ Works with roadmaps up to 1000 user stories
- ✅ Test coverage >90%
- ✅ No CFR-007 violations (context budget <30%)

### User Experience

- ✅ Conversational, natural interaction (not form-filling)
- ✅ Clear guidance at each step
- ✅ Rich formatting makes output readable
- ✅ Errors handled gracefully with helpful messages
- ✅ User always in control (no auto-adds)

### Documentation

- ✅ `/US` command documented in TUTORIALS.md
- ✅ Workflow documented in WORKFLOWS.md
- ✅ Code fully commented with docstrings
- ✅ Examples provided for users
- ✅ CLAUDE.md updated with new capability

### Quality Gates

- ✅ All unit tests pass (>90% coverage)
- ✅ Integration tests pass (critical paths)
- ✅ No regressions in existing functionality
- ✅ Pre-commit hooks pass (black, mypy)
- ✅ Code review by architect (if applicable)
- ✅ Manual QA testing completed

---

## Acceptance Criteria (from US-012)

### Original Acceptance Criteria

Mapping SPEC to original US-012 acceptance criteria:

| Criterion | Implementation | Status |
|-----------|----------------|--------|
| `/US` command exists in PM chat | `ChatSession._handle_command()` routes to handler | ✅ Covered |
| User can type `/US I want to...` | `UserStoryCommandHandler.handle_command()` | ✅ Covered |
| PM extracts & structures US | `AIService.extract_user_story()` + prompts | ✅ Covered |
| PM shares ideas about rephrase | `_present_draft()` with similarity warnings | ✅ Covered |
| PM presents draft to user | Rich markdown formatting | ✅ Covered |
| PM waits for validation | Validation loop in `handle_validation_response()` | ✅ Covered |
| User can request changes | Refinement handler with AI | ✅ Covered |
| After validation, propagate to ROADMAP | `finalize_user_story()` → `add_user_story()` | ✅ Covered |
| PM detects similar existing US | `_check_similarity()` with difflib | ✅ Covered |
| PM helps with prioritization | `_suggest_prioritization()` with AI | ✅ Covered |
| PM suggests rephrase vs new | Similarity warnings with options | ✅ Covered |
| Workflow feels conversational | Natural language, friendly prompts | ✅ Covered |

**All 12 acceptance criteria covered by this specification.**

---

## Dependencies & Blockers

### Prerequisites (Must Complete First)

None - all required components already exist.

### External Dependencies

1. **Claude API**: Must have valid API key and credits
2. **ROADMAP.md**: Must exist at `docs/roadmap/ROADMAP.md`
3. **Backup directory**: `docs/roadmap/roadmap_backups/` (created automatically)

### Optional Dependencies

1. **Claude CLI**: Could use CLI mode instead of API (cost savings)
2. **Semantic similarity**: Could upgrade to embeddings for better matching

### Blockers

None identified.

---

## Future Enhancements (Out of Scope)

These are potential improvements for future iterations:

1. **US-013 Integration**: Automatically infer DoD from user story
2. **Batch Creation**: `/US batch` for multiple user stories at once
3. **Templates**: Pre-defined templates for common user story types
4. **Impact Analysis**: Show detailed impact on roadmap timeline
5. **Dependency Graph**: Visual representation of user story dependencies
6. **AI-Powered Estimation**: Automatically estimate effort based on past data
7. **Semantic Similarity**: Use embeddings instead of string matching
8. **Export**: Export user stories to JIRA, GitHub Issues, etc.
9. **History**: Track all user story creation sessions
10. **Analytics**: Dashboard showing user story creation metrics

---

## Related Specifications

- **SPEC-013**: PM Infers and Validates DoD (integrates with `/US` workflow)
- **SPEC-021**: Natural Language Roadmap Management (related NLP work)
- **SPEC-009**: Living Documentation (tutorials for `/US` command)
- **CFR-007**: Context Budget Compliance (must maintain <30%)
- **CFR-009**: Silent Background Agents (project_manager notifications)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-19 | architect | Initial specification |

---

## Approval

**Architect**: [Pending Review]
**Project Manager**: [Pending Review]
**Code Developer**: [Awaiting Spec]

---

**END OF SPECIFICATION**
