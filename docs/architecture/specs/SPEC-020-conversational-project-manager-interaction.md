# SPEC-020: Conversational Project Manager Interaction

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-020 - Conversational Project Manager Interaction

**Related ADRs**: None

**Assigned To**: code_developer

---

## Executive Summary

This specification describes the technical design for implementing conversational, human-like interaction patterns in the project_manager agent during user story creation. The system will transform the current rigid, question-batch approach into a natural, adaptive, one-by-one conversational flow that feels collaborative and human. This addresses the critical UX gap between "robotic interrogation" and "natural collaboration" that users expect from an AI assistant.

**Key Innovation**: Adaptive question flow that reconsiders remaining questions when users provide corrections mid-conversation, eliminating redundant questions and creating a truly collaborative experience.

---

## Problem Statement

### Current Situation

When users initiate a new user story, the project_manager agent exhibits robotic, inflexible behavior:

**Current Problems**:
- ❌ **Batch questioning**: "Please answer questions 1-6" - overwhelming and impersonal
- ❌ **Inflexible flow**: All questions asked upfront with no adaptation to user responses
- ❌ **One-directional**: PM asks, user answers - no dialogue or collaboration
- ❌ **No confirmation**: Proceeds directly to ROADMAP without showing draft
- ❌ **Ignores corrections**: When user says "sorry, I meant...", PM continues with irrelevant questions
- ❌ **Robotic tone**: Technical language, numbered questions, no conversational transitions

**User Experience Impact**:
- Users feel interrogated, not collaborated with
- Cognitive overload from seeing all questions at once
- Frustration when PM asks questions that user's clarification already answered
- Lack of confidence in PM understanding their intent
- Reduced engagement and willingness to create user stories

### Goal

Transform project_manager into a conversational partner that:
- ✅ **One-by-one flow**: Asks questions individually, waits for each response
- ✅ **Adaptive to corrections**: Reconsiders remaining questions when user clarifies/corrects
- ✅ **Integrates user input**: User's words have authority - immediately accept and adapt
- ✅ **Clear confirmation**: Shows draft for approval before adding to ROADMAP
- ✅ **Natural tone**: Conversational transitions ("Got it!", "Perfect!"), not robotic
- ✅ **Collaborative feel**: Feels like working WITH PM, not being interrogated BY PM

**Success Metrics**:
- Draft approval rate >85% on first try (indicates PM understood intent)
- User satisfaction score >4/5 for "natural and collaborative" (subjective feedback)
- Zero redundant questions after user correction (automated test)
- Average conversation length <8 questions (efficient without being rigid)

### Non-Goals

- **NOT** implementing multi-session conversation memory (only within single session)
- **NOT** implementing automatic priority assignment (manual user decision)
- **NOT** implementing similarity detection with existing user stories (separate US)
- **NOT** implementing voice/speech interface (text-based for MVP)

---

## Requirements

### Functional Requirements

**FR-1: One-by-One Question Flow**
- PM asks questions individually, never in batches
- Waits for user response before asking next question
- Each question appears on its own, not numbered or grouped
- Conversational transitions between questions ("Got it! Next question:", "Perfect!")

**FR-2: Adaptive Question Regeneration**
- When user corrects/clarifies, PM reconsiders remaining questions
- Detection patterns: "sorry", "actually", "I meant", "let me clarify"
- PM regenerates question list based on corrected understanding
- PM preserves answers that still apply to corrected story
- PM skips redundant questions that correction already answered

**FR-3: User Input Authority**
- User's words have final authority on requirements
- PM accepts corrections immediately without hesitation or permission-asking
- Changes apply even if they affect priorities or code_developer work
- No "Are you sure?" or "This will change X, proceed?" - just adapt

**FR-4: Draft Confirmation Workflow**
- After gathering all answers, PM shows formatted user story draft
- PM waits for user approval: "yes"/"no"/"changes needed"
- If "no", PM asks what to adjust and shows updated draft
- If "changes needed", PM accepts modifications and updates draft
- Only adds to ROADMAP after explicit "yes" or "approve"

**FR-5: Conversational Tone**
- No robotic language ("Please answer questions 1-6")
- Conversational transitions ("Got it!", "Perfect!", "Excellent!")
- Natural acknowledgments of user responses
- No numbered questions or batch formatting
- Feels like dialogue, not interrogation

**FR-6: Session Persistence**
- In-progress conversation survives user disconnect/reconnect (within session)
- PM resumes from current question if connection lost
- Conversation state preserved until user approves or cancels
- No cross-session memory (new session = new conversation)

**FR-7: Cancellation Support**
- User can cancel at any stage with "cancel" or "nevermind"
- PM acknowledges cancellation and discards draft
- No lingering conversation state after cancellation

**FR-8: Anti-Pattern Prevention**
- Automated detection of robotic patterns (unit tests)
- Prevents batch question formatting at runtime
- Enforces conversational transitions programmatically
- Logs warnings if robotic tone detected (for debugging)

### Non-Functional Requirements

**NFR-1: Response Latency**
- Question generation: <2 seconds (AI processing)
- Answer recording: <100ms (local state update)
- Draft generation: <3 seconds (AI formatting)
- Total conversation: <30 seconds for 5-8 questions

**NFR-2: Accuracy**
- Question relevance: >90% of questions deemed relevant by user
- Correction detection: >95% accuracy (detects "sorry", "actually" patterns)
- Answer preservation: >90% of still-relevant answers preserved after correction
- Draft accuracy: >85% approval rate on first try

**NFR-3: Reliability**
- No conversation state corruption (atomic state updates)
- Graceful degradation if AI service unavailable (fallback to manual entry)
- Session persistence across temporary disconnects (<5 minutes)
- Transaction safety (all-or-nothing ROADMAP updates)

**NFR-4: Maintainability**
- Clear separation of concerns (state management, AI prompts, chat UI)
- Comprehensive unit test coverage (>90% for conversation logic)
- Well-documented conversation state transitions
- Easy to add new question types or adjust tone

**NFR-5: Scalability**
- Conversation state size: <10KB per active conversation
- Supports up to 50 concurrent conversation sessions (multi-user future)
- AI token usage: <2000 tokens per conversation (cost control)

### Constraints

**Technical Constraints**:
- Must use existing `AIService` class for Claude API integration
- Must use existing `RoadmapEditor` class for safe ROADMAP updates
- Must integrate with existing `ChatSession` class in `chat_interface.py`
- Must use existing notification system (`NotificationDB`) for alerts
- Must follow COLLABORATION_METHODOLOGY.md Section 4.6 (plain language, no technical shorthand)

**Business Constraints**:
- Implementation must complete within 4-5 days (per US-020 estimate)
- Must maintain backward compatibility with existing chat commands
- Cannot break existing user story creation workflows
- Must work with current Claude API tier (no premium features)

**UX Constraints**:
- Must feel natural to non-technical users
- Cannot require users to learn special syntax or commands
- Must provide clear feedback at every step
- Cannot be slower than current approach (user perception)

---

## Proposed Solution

### High-Level Approach

Implement a **three-layer architecture** for conversational state management:

1. **Conversation State Layer** (`ConversationStateManager`)
   - Tracks current question, answers, corrections
   - Manages question regeneration logic
   - Preserves relevant answers after corrections
   - Provides draft generation

2. **AI Orchestration Layer** (`ConversationalAIOrchestrator`)
   - Generates initial questions from user story text
   - Regenerates questions after corrections
   - Formats final user story draft
   - Detects correction intent in user messages

3. **Chat Integration Layer** (Enhanced `ChatSession`)
   - Detects new user story intent
   - Routes messages to conversation manager
   - Applies conversational tone and transitions
   - Handles approval workflow

**Key Innovation**: The `ConversationStateManager` maintains a **question dependency graph** that allows intelligent question regeneration. When a user corrects mid-conversation, the system:
1. Identifies which answers are still valid
2. Determines which questions were already implicitly answered by the correction
3. Generates only the remaining necessary questions
4. Resumes conversation from the right point

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User (Chat Interface)                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ChatSession (chat_interface.py)                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Responsibilities:                                            │  │
│  │  - Detect user story creation intent                          │  │
│  │  - Route messages to conversation manager                     │  │
│  │  - Apply conversational tone/transitions                      │  │
│  │  - Handle draft approval workflow                             │  │
│  │  - Display formatted messages with Rich UI                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│            ConversationStateManager (NEW)                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  State Management:                                            │  │
│  │  - current_question_idx: int                                  │  │
│  │  - questions: List[Question]                                  │  │
│  │  - answers: Dict[str, str]                                    │  │
│  │  - corrections: List[str]                                     │  │
│  │  - user_story_text: str                                       │  │
│  │                                                                │  │
│  │  Methods:                                                      │  │
│  │  - get_next_question() -> Optional[Question]                  │  │
│  │  - record_answer(answer: str)                                 │  │
│  │  - handle_correction(correction: str)                         │  │
│  │  - generate_draft() -> str                                    │  │
│  │  - is_complete() -> bool                                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│         ConversationalAIOrchestrator (NEW)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  AI Coordination:                                             │  │
│  │  - generate_initial_questions(user_story: str)                │  │
│  │  - regenerate_questions_after_correction(                     │  │
│  │      original_story: str,                                     │  │
│  │      correction: str,                                         │  │
│  │      existing_answers: Dict[str, str]                         │  │
│  │    ) -> List[Question]                                        │  │
│  │  - detect_correction_intent(message: str) -> bool             │  │
│  │  - format_draft(story: str, answers: Dict) -> str             │  │
│  │  - preserve_relevant_answers(                                 │  │
│  │      old_answers: Dict,                                       │  │
│  │      new_questions: List[Question]                            │  │
│  │    ) -> Dict[str, str]                                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AIService (Existing)                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Claude API Integration:                                      │  │
│  │  - send_message(prompt: str) -> str                           │  │
│  │  - Uses existing Claude API client                            │  │
│  │  - Handles retries and error recovery                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              ConversationalToneEnforcer (NEW)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Tone Validation:                                             │  │
│  │  - validate_message(message: str) -> bool                     │  │
│  │  - add_transition(message: str, idx: int) -> str              │  │
│  │  - detect_robotic_patterns(message: str) -> List[str]         │  │
│  │  - get_random_acknowledgment() -> str                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   RoadmapEditor (Existing)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ROADMAP Management:                                          │  │
│  │  - add_user_story(story_spec: str)                            │  │
│  │  - assign_next_us_number() -> str                             │  │
│  │  - Safe file updates with backups                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

**Phase 1: User Initiates User Story**
```
User: "user story: As a developer I want syntax highlighting in code blocks"
    │
    ▼
ChatSession detects new user story intent
    │
    ▼
ChatSession creates ConversationStateManager(user_story_text)
    │
    ▼
ConversationStateManager → ConversationalAIOrchestrator.generate_initial_questions()
    │
    ▼
ConversationalAIOrchestrator → AIService (Claude API)
    │
    ▼
AIService returns: ["What programming languages?", "Where should highlighting appear?", ...]
    │
    ▼
ConversationStateManager stores questions
    │
    ▼
ConversationStateManager.get_next_question() → Question 1
    │
    ▼
ConversationalToneEnforcer.add_transition() → "Let me ask some clarifying questions.\n\nWhat programming languages should be highlighted?"
    │
    ▼
ChatSession displays to user
```

**Phase 2: User Answers Question**
```
User: "Python, JavaScript, and Bash"
    │
    ▼
ChatSession → ConversationStateManager.record_answer(answer)
    │
    ▼
ConversationStateManager stores answer, increments current_question_idx
    │
    ▼
ConversationStateManager.get_next_question() → Question 2
    │
    ▼
ConversationalToneEnforcer.add_transition() → "Got it! Where should this highlighting appear?"
    │
    ▼
ChatSession displays to user
```

**Phase 3: User Corrects Mid-Conversation**
```
User: "sorry the real story is: As a user I want to be notified when a delivery is ready to ship"
    │
    ▼
ChatSession → ConversationalAIOrchestrator.detect_correction_intent() → True
    │
    ▼
ChatSession → ConversationStateManager.handle_correction(correction_text)
    │
    ▼
ConversationStateManager → ConversationalAIOrchestrator.regenerate_questions_after_correction(
    original_story="...syntax highlighting...",
    correction="...delivery notifications...",
    existing_answers={"What programming languages?": "Python, JavaScript, and Bash"}
)
    │
    ▼
ConversationalAIOrchestrator → AIService (Claude API analyzes correction)
    │
    ▼
AIService returns NEW questions: ["What notifications?", "How to notify?", ...]
    │
    ▼
ConversationalAIOrchestrator.preserve_relevant_answers() → {} (no answers relevant to new story)
    │
    ▼
ConversationStateManager resets state with new questions, preserved answers (empty)
    │
    ▼
ConversationalToneEnforcer.add_transition() → "Ah, I understand now! Let me adjust my questions based on that.\n\nWhat notifications do you want to receive?"
    │
    ▼
ChatSession displays to user
```

**Phase 4: All Questions Answered**
```
ConversationStateManager.is_complete() → True
    │
    ▼
ConversationStateManager.generate_draft()
    │
    ▼
ConversationalAIOrchestrator.format_draft(user_story_text, answers)
    │
    ▼
AIService formats draft user story (title, DoD, scope, etc.)
    │
    ▼
ChatSession displays draft with separator bars
    │
    ▼
ChatSession prompts: "Does this match what you had in mind?\n\nOptions:\n- 'yes'/'approve' → I'll add this to ROADMAP.md\n- 'no'/'changes needed' → Tell me what to adjust\n- 'cancel' → Discard this user story"
    │
    ▼
User responds (approval workflow)
```

**Phase 5: User Approves**
```
User: "yes"
    │
    ▼
ChatSession detects approval
    │
    ▼
ChatSession → RoadmapEditor.assign_next_us_number() → "US-021"
    │
    ▼
ChatSession → RoadmapEditor.add_user_story(formatted_draft)
    │
    ▼
RoadmapEditor safely updates ROADMAP.md with backup
    │
    ▼
ChatSession → NotificationDB.create_notification("✅ Added to ROADMAP.md!")
    │
    ▼
ChatSession displays success message
    │
    ▼
ConversationStateManager destroyed (conversation complete)
```

### Component Specifications

#### 1. ConversationStateManager

**Location**: `coffee_maker/cli/conversation_state_manager.py`

**Purpose**: Manage conversational state during user story creation, including question tracking, answer recording, and correction handling.

**Class Definition**:
```python
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Question:
    """Represents a single question in the conversation.

    Attributes:
        text: The question text to display to user
        key: Unique identifier for this question (for answer mapping)
        category: Question category (scope, acceptance_criteria, effort, etc.)
        dependencies: List of question keys this depends on (for regeneration logic)
    """
    text: str
    key: str
    category: str
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ConversationStateManager:
    """Manages conversational state during user story creation.

    Tracks:
    - Current question being asked
    - User answers collected so far
    - Remaining questions to ask
    - User corrections/clarifications
    - Question dependency graph for intelligent regeneration

    Example:
        >>> manager = ConversationStateManager("As a dev I want syntax highlighting")
        >>> question = manager.get_next_question()
        >>> manager.record_answer("Python, JavaScript, Bash")
        >>> next_q = manager.get_next_question()
        >>> manager.handle_correction("sorry, I meant email notifications")
        >>> # Questions regenerated based on correction
    """

    def __init__(
        self,
        user_story_text: str,
        ai_orchestrator: 'ConversationalAIOrchestrator'
    ):
        """Initialize conversation state.

        Args:
            user_story_text: Initial user story description
            ai_orchestrator: AI orchestrator for question generation
        """
        self.user_story_text = user_story_text
        self.ai_orchestrator = ai_orchestrator

        # Generate initial questions
        self.questions: List[Question] = self.ai_orchestrator.generate_initial_questions(
            user_story_text
        )

        # Conversation state
        self.current_question_idx: int = 0
        self.answers: Dict[str, str] = {}  # question_key -> answer
        self.corrections: List[str] = []

    def get_next_question(self) -> Optional[Question]:
        """Get the next question to ask user (one at a time).

        Returns:
            Next Question object, or None if all questions answered
        """
        if self.current_question_idx >= len(self.questions):
            return None
        return self.questions[self.current_question_idx]

    def record_answer(self, answer: str):
        """Record user's answer to current question.

        Args:
            answer: User's response text
        """
        if self.current_question_idx >= len(self.questions):
            raise ValueError("No current question to answer")

        current_question = self.questions[self.current_question_idx]
        self.answers[current_question.key] = answer
        self.current_question_idx += 1

    def handle_correction(self, correction: str):
        """User corrected/clarified something - reconsider questions.

        Examples:
        - "sorry the real story is..."
        - "I meant X not Y"
        - "actually, let me clarify..."

        Args:
            correction: User's correction text
        """
        self.corrections.append(correction)

        # Update user story text with correction
        self.user_story_text = correction

        # Regenerate questions based on corrected understanding
        new_questions = self.ai_orchestrator.regenerate_questions_after_correction(
            original_story=self.user_story_text,
            correction=correction,
            existing_answers=self.answers
        )

        # Preserve answers that still apply
        preserved_answers = self.ai_orchestrator.preserve_relevant_answers(
            old_answers=self.answers,
            new_questions=new_questions
        )

        # Reset state with new questions
        self.questions = new_questions
        self.answers = preserved_answers
        self.current_question_idx = len(preserved_answers)

    def is_complete(self) -> bool:
        """Check if all questions have been answered.

        Returns:
            True if all questions answered, False otherwise
        """
        return self.current_question_idx >= len(self.questions)

    def generate_draft(self) -> str:
        """Generate user story specification draft for user approval.

        Returns:
            Formatted user story draft (markdown)
        """
        return self.ai_orchestrator.format_draft(
            user_story=self.user_story_text,
            answers=self.answers,
            questions=self.questions
        )

    def get_progress(self) -> tuple[int, int]:
        """Get conversation progress.

        Returns:
            (answered_count, total_count) tuple
        """
        return (self.current_question_idx, len(self.questions))
```

**File Size Estimate**: ~200 lines (including docstrings, tests will be separate)

**Dependencies**:
- `ConversationalAIOrchestrator` (for AI-powered question generation)
- Python stdlib: `dataclasses`, `typing`

---

#### 2. ConversationalAIOrchestrator

**Location**: `coffee_maker/cli/conversational_ai_orchestrator.py`

**Purpose**: Orchestrate AI interactions for conversational user story creation, including question generation, correction detection, and draft formatting.

**Class Definition**:
```python
import logging
import re
from typing import Dict, List

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.conversation_state_manager import Question

logger = logging.getLogger(__name__)


class ConversationalAIOrchestrator:
    """Orchestrates AI for conversational user story creation.

    Responsibilities:
    - Generate initial questions from user story text
    - Regenerate questions after user corrections
    - Detect correction intent in user messages
    - Format final user story draft
    - Preserve relevant answers during question regeneration

    Example:
        >>> orchestrator = ConversationalAIOrchestrator(ai_service)
        >>> questions = orchestrator.generate_initial_questions("As a dev...")
        >>> is_correction = orchestrator.detect_correction_intent("sorry, I meant...")
        >>> draft = orchestrator.format_draft(story, answers, questions)
    """

    # Correction detection patterns
    CORRECTION_PATTERNS = [
        r"sorry.*real story",
        r"sorry.*meant",
        r"actually",
        r"I meant",
        r"let me clarify",
        r"correction",
        r"no.*I want",
        r"wait.*meant",
    ]

    def __init__(self, ai_service: AIService):
        """Initialize AI orchestrator.

        Args:
            ai_service: AIService instance for Claude API
        """
        self.ai_service = ai_service

    def generate_initial_questions(self, user_story: str) -> List[Question]:
        """Generate clarifying questions based on user story.

        Uses AI to analyze user story and generate 5-8 relevant questions
        about scope, acceptance criteria, effort, edge cases, etc.

        Args:
            user_story: Initial user story text

        Returns:
            List of Question objects
        """
        prompt = f"""Analyze this user story and generate 5-8 clarifying questions to understand it better:

User Story: "{user_story}"

Generate questions about:
1. Scope - What exactly should be included/excluded?
2. Acceptance Criteria - What defines success?
3. User Experience - How should it look/feel?
4. Edge Cases - What unusual scenarios to handle?
5. Dependencies - Does this rely on other features?
6. Effort - Complexity estimate (simple/medium/complex)?
7. Priority - How urgent is this?

Return questions as JSON array with this format:
[
    {{"text": "What programming languages should be supported?", "key": "languages", "category": "scope"}},
    {{"text": "Where should this feature appear?", "key": "location", "category": "scope"}},
    ...
]

Only the JSON array, no other text."""

        response = self.ai_service.send_message(prompt)

        # Parse JSON response
        import json
        try:
            question_data = json.loads(response.strip())
            questions = [
                Question(
                    text=q["text"],
                    key=q["key"],
                    category=q["category"]
                )
                for q in question_data
            ]
            logger.info(f"Generated {len(questions)} initial questions")
            return questions
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Fallback to default questions
            return self._get_default_questions()

    def regenerate_questions_after_correction(
        self,
        original_story: str,
        correction: str,
        existing_answers: Dict[str, str]
    ) -> List[Question]:
        """Regenerate questions after user correction.

        Analyzes correction and generates new questions, avoiding redundancy
        with information already provided in the correction.

        Args:
            original_story: Original user story text
            correction: User's correction text
            existing_answers: Answers already provided (question_key -> answer)

        Returns:
            New list of Question objects
        """
        prompt = f"""The user corrected their user story mid-conversation. Generate new clarifying questions.

Original Story: "{original_story}"

User Correction: "{correction}"

Previous Answers: {existing_answers}

Rules:
1. Generate questions for the CORRECTED story, not the original
2. Skip questions that the correction already answered
3. Don't ask redundant questions based on previous answers
4. Focus on what we still need to know
5. Generate 3-6 questions (fewer than initial since we have context)

Return questions as JSON array:
[
    {{"text": "...", "key": "...", "category": "..."}},
    ...
]

Only the JSON array, no other text."""

        response = self.ai_service.send_message(prompt)

        # Parse JSON response
        import json
        try:
            question_data = json.loads(response.strip())
            questions = [
                Question(
                    text=q["text"],
                    key=q["key"],
                    category=q["category"]
                )
                for q in question_data
            ]
            logger.info(f"Regenerated {len(questions)} questions after correction")
            return questions
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Fallback to initial question generation
            return self.generate_initial_questions(correction)

    def detect_correction_intent(self, message: str) -> bool:
        """Detect if user is correcting/clarifying.

        Args:
            message: User's message text

        Returns:
            True if correction detected, False otherwise
        """
        message_lower = message.lower()
        for pattern in self.CORRECTION_PATTERNS:
            if re.search(pattern, message_lower):
                logger.info(f"Correction detected (pattern: {pattern})")
                return True
        return False

    def format_draft(
        self,
        user_story: str,
        answers: Dict[str, str],
        questions: List[Question]
    ) -> str:
        """Format final user story draft for approval.

        Args:
            user_story: User story text
            answers: Collected answers (question_key -> answer)
            questions: Questions that were asked

        Returns:
            Formatted markdown draft
        """
        # Build context for AI
        qa_pairs = []
        for question in questions:
            if question.key in answers:
                qa_pairs.append(f"Q: {question.text}\nA: {answers[question.key]}")

        qa_text = "\n\n".join(qa_pairs)

        prompt = f"""Format this user story into a structured specification:

User Story: "{user_story}"

Questions & Answers:
{qa_text}

Format as:
## 📝 US-XXX - [Title]

**User Story**:
> "[user story text]"

**Scope**:
[What's included/excluded - from answers]

**Acceptance Criteria**:
1. [Criterion 1]
2. [Criterion 2]
...

**Implementation Plan**:
- Phase 1: [...]
- Phase 2: [...]

**Estimated Effort**: [X-Y days based on complexity answer]
**Business Value**: [⭐⭐⭐⭐⭐ based on priority answer]

Only return the formatted spec, no other text."""

        response = self.ai_service.send_message(prompt)
        return response.strip()

    def preserve_relevant_answers(
        self,
        old_answers: Dict[str, str],
        new_questions: List[Question]
    ) -> Dict[str, str]:
        """Keep answers that still apply to corrected story.

        Uses AI to determine which previous answers are still relevant
        to the new questions.

        Args:
            old_answers: Previous answers (question_key -> answer)
            new_questions: New questions after correction

        Returns:
            Preserved answers (question_key -> answer)
        """
        if not old_answers:
            return {}

        # Build mapping of new question keys
        new_keys = {q.key: q.text for q in new_questions}

        prompt = f"""Determine which previous answers are still relevant to new questions.

Previous Answers:
{old_answers}

New Questions:
{new_keys}

For each previous answer, determine if it's still relevant to ANY new question.
If yes, map it to the new question key.

Return as JSON:
{{
    "new_question_key": "previous answer text",
    ...
}}

Only the JSON object, no other text."""

        response = self.ai_service.send_message(prompt)

        # Parse JSON response
        import json
        try:
            preserved = json.loads(response.strip())
            logger.info(f"Preserved {len(preserved)} answers after correction")
            return preserved
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Conservative fallback: don't preserve any answers
            return {}

    def _get_default_questions(self) -> List[Question]:
        """Fallback default questions if AI fails.

        Returns:
            List of generic Question objects
        """
        return [
            Question("What is the main goal of this feature?", "goal", "scope"),
            Question("Who will use this feature?", "users", "scope"),
            Question("What defines success for this feature?", "success", "acceptance_criteria"),
            Question("Are there any edge cases to consider?", "edge_cases", "acceptance_criteria"),
            Question("How complex is this feature (simple/medium/complex)?", "complexity", "effort"),
        ]
```

**File Size Estimate**: ~400 lines (including docstrings and error handling)

**Dependencies**:
- `AIService` (existing)
- `Question` from `conversation_state_manager`
- Python stdlib: `json`, `re`, `logging`, `typing`

---

#### 3. ConversationalToneEnforcer

**Location**: `coffee_maker/cli/conversational_tone_enforcer.py`

**Purpose**: Ensure PM uses conversational tone and prevent robotic patterns.

**Class Definition**:
```python
import logging
import random
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


class ConversationalToneEnforcer:
    """Ensures PM uses conversational tone, not robotic.

    Responsibilities:
    - Validate messages for robotic patterns
    - Add conversational transitions to questions
    - Provide natural acknowledgments
    - Log warnings for tone violations

    Example:
        >>> enforcer = ConversationalToneEnforcer()
        >>> enforcer.validate_message("Please answer questions 1-6")  # Raises ValueError
        >>> msg = enforcer.add_transition("What languages?", question_idx=0)
        >>> # Returns: "Let me ask some clarifying questions.\n\nWhat languages?"
    """

    # Robotic patterns that should never appear
    ROBOTIC_PATTERNS = [
        r"please answer questions? \d+-\d+",  # "Please answer questions 1-6"
        r"q\d+:",  # "Q1:", "Q2:", etc.
        r"question \d+.*question \d+",  # Multiple questions at once
        r"answer the following",  # Interrogative tone
    ]

    # Conversational transitions for questions
    CONVERSATIONAL_TRANSITIONS = [
        "Got it! ",
        "Perfect! ",
        "Excellent! ",
        "Great! ",
        "I understand. ",
        "Thanks! ",
    ]

    # Acknowledgments for corrections
    CORRECTION_ACKNOWLEDGMENTS = [
        "Ah, I understand now! Let me adjust my questions based on that.",
        "Got it, thanks for clarifying! Let me reconsider what I need to ask.",
        "Perfect, that changes things. Let me ask different questions based on this.",
        "I see! Let me pivot to questions that fit this better.",
    ]

    def validate_message(self, message: str) -> bool:
        """Check if message violates conversational tone.

        Args:
            message: Message text to validate

        Returns:
            True if message is conversational

        Raises:
            ValueError: If robotic pattern detected
        """
        message_lower = message.lower()
        for pattern in self.ROBOTIC_PATTERNS:
            if re.search(pattern, message_lower):
                logger.error(f"Robotic tone detected: {pattern}")
                raise ValueError(
                    f"Robotic tone detected! Pattern: {pattern}\n"
                    f"Message: {message}\n"
                    f"Use conversational language instead."
                )
        return True

    def add_transition(self, message: str, question_idx: int) -> str:
        """Add conversational transition to question.

        Args:
            message: Question text
            question_idx: Index of current question (0-based)

        Returns:
            Message with conversational transition prepended
        """
        if question_idx == 0:
            # First question - set context
            prefix = "Let me ask some clarifying questions to understand better.\n\n"
        else:
            # Subsequent questions - add transition
            transition = random.choice(self.CONVERSATIONAL_TRANSITIONS)
            prefix = f"{transition}"

        return f"{prefix}{message}"

    def get_correction_acknowledgment(self) -> str:
        """Get random acknowledgment for user correction.

        Returns:
            Natural acknowledgment message
        """
        return random.choice(self.CORRECTION_ACKNOWLEDGMENTS)

    def detect_robotic_patterns(self, message: str) -> List[str]:
        """Detect robotic patterns in message (for testing).

        Args:
            message: Message text

        Returns:
            List of matched robotic patterns (empty if none)
        """
        message_lower = message.lower()
        matched = []
        for pattern in self.ROBOTIC_PATTERNS:
            if re.search(pattern, message_lower):
                matched.append(pattern)
        return matched
```

**File Size Estimate**: ~150 lines

**Dependencies**:
- Python stdlib: `random`, `re`, `logging`, `typing`

---

#### 4. ChatSession Integration (Enhanced)

**Location**: `coffee_maker/cli/chat_interface.py` (modifications)

**Purpose**: Integrate conversational user story creation into existing chat interface.

**Changes Required**:

**A. Add Conversation State Tracking**
```python
# In ChatSession.__init__()
self.active_conversation: Optional[ConversationStateManager] = None
self.awaiting_approval: bool = False
self.draft_text: Optional[str] = None

# Initialize new components
from coffee_maker.cli.conversational_ai_orchestrator import ConversationalAIOrchestrator
from coffee_maker.cli.conversational_tone_enforcer import ConversationalToneEnforcer

self.ai_orchestrator = ConversationalAIOrchestrator(self.ai_service)
self.tone_enforcer = ConversationalToneEnforcer()
```

**B. Add User Story Intent Detection**
```python
def _is_new_user_story(self, message: str) -> bool:
    """Detect if user is initiating a new user story.

    Patterns:
    - "user story: ..."
    - "US: ..."
    - "As a [role] I want [goal]..."

    Args:
        message: User's input message

    Returns:
        True if new user story intent detected
    """
    message_lower = message.lower()

    # Explicit patterns
    if message_lower.startswith("user story:"):
        return True
    if message_lower.startswith("us:"):
        return True

    # As-a-user pattern
    if re.search(r"as an? .+ I want", message_lower):
        return True

    return False
```

**C. Add Conversation Routing**
```python
def handle_user_message(self, message: str):
    """Route user message to appropriate handler.

    Args:
        message: User's input message
    """
    # Check if we're in an active conversation
    if self.active_conversation:
        self._handle_conversation_message(message)
        return

    # Check if starting new user story
    if self._is_new_user_story(message):
        self._start_user_story_conversation(message)
        return

    # Otherwise, handle as normal chat message
    self._handle_normal_chat(message)

def _start_user_story_conversation(self, user_story_text: str):
    """Start new user story conversation.

    Args:
        user_story_text: Initial user story description
    """
    from coffee_maker.cli.conversation_state_manager import ConversationStateManager

    # Extract story text (remove "user story:" prefix)
    story = user_story_text.lower().replace("user story:", "").strip()
    story = story.replace("us:", "").strip()

    # Create conversation manager
    self.active_conversation = ConversationStateManager(
        user_story_text=story,
        ai_orchestrator=self.ai_orchestrator
    )

    # Ask first question
    self._ask_next_question()

def _handle_conversation_message(self, message: str):
    """Handle message during active conversation.

    Args:
        message: User's input message
    """
    # Check if user is canceling
    if message.lower() in ["cancel", "nevermind", "stop"]:
        self._cancel_conversation()
        return

    # Check if waiting for approval
    if self.awaiting_approval:
        self._handle_approval_response(message)
        return

    # Check if user is correcting
    if self.ai_orchestrator.detect_correction_intent(message):
        self._handle_correction(message)
        return

    # Record answer and ask next question
    self.active_conversation.record_answer(message)
    self._ask_next_question()

def _ask_next_question(self):
    """Ask next question with conversational tone."""
    next_q = self.active_conversation.get_next_question()

    if next_q:
        # Get progress for display
        answered, total = self.active_conversation.get_progress()

        # Add conversational transition
        message = self.tone_enforcer.add_transition(
            next_q.text,
            question_idx=self.active_conversation.current_question_idx
        )

        # Validate tone (will raise if robotic)
        self.tone_enforcer.validate_message(message)

        # Display with progress indicator
        self.console.print(f"\n[bold cyan]PM[/bold cyan] ({answered}/{total}):")
        self.console.print(message)
    else:
        # All questions answered - show draft
        self._show_draft_for_approval()

def _handle_correction(self, correction: str):
    """Handle user correction mid-conversation.

    Args:
        correction: User's correction text
    """
    # Apply correction
    self.active_conversation.handle_correction(correction)

    # Acknowledge correction
    ack = self.tone_enforcer.get_correction_acknowledgment()
    self.console.print(f"\n[bold cyan]PM[/bold cyan]:")
    self.console.print(ack)

    # Ask next question (from regenerated list)
    self._ask_next_question()

def _show_draft_for_approval(self):
    """Show draft user story and wait for approval."""
    # Generate draft
    self.draft_text = self.active_conversation.generate_draft()

    # Display draft with separator
    self.console.print("\n" + "═" * 70)
    self.console.print("[bold green]Draft User Story[/bold green]\n")
    self.console.print(Markdown(self.draft_text))
    self.console.print("═" * 70)

    # Prompt for approval
    self.console.print("\n[bold cyan]PM[/bold cyan]:")
    self.console.print("Does this match what you had in mind?\n")
    self.console.print("Options:")
    self.console.print("  - [green]'yes'[/green] or [green]'approve'[/green] → I'll add this to ROADMAP.md")
    self.console.print("  - [yellow]'no'[/yellow] or [yellow]'changes needed'[/yellow] → Tell me what to adjust")
    self.console.print("  - [red]'cancel'[/red] → Discard this user story")

    self.awaiting_approval = True

def _handle_approval_response(self, response: str):
    """Handle user's response to draft.

    Args:
        response: User's approval response
    """
    response_lower = response.lower().strip()

    if response_lower in ["yes", "approve", "y", "approved", "looks good"]:
        # Add to ROADMAP
        self._add_to_roadmap(self.draft_text)
        self.console.print("\n[bold green]✅ Added to ROADMAP.md![/bold green]")

        # Clean up conversation state
        self._cleanup_conversation()

    elif response_lower in ["no", "changes", "change", "changes needed"]:
        self.console.print("\n[bold cyan]PM[/bold cyan]:")
        self.console.print("What would you like me to adjust?")
        # User will respond, and we'll handle as modification
        # TODO: Implement modification handling

    elif response_lower == "cancel":
        self._cancel_conversation()
    else:
        # Unclear response
        self.console.print("\n[yellow]I didn't understand. Please respond with 'yes', 'no', or 'cancel'.[/yellow]")

def _add_to_roadmap(self, draft: str):
    """Add approved user story to ROADMAP.

    Args:
        draft: Formatted user story draft
    """
    # Assign next US number
    us_number = self.roadmap_editor.assign_next_us_number()

    # Replace placeholder US-XXX with actual number
    final_draft = draft.replace("US-XXX", us_number)

    # Add to ROADMAP
    self.roadmap_editor.add_user_story(final_draft)

    # Create notification
    self.notification_db.create_notification(
        title=f"New User Story: {us_number}",
        message="Added to ROADMAP via conversational flow",
        level="info",
        sound=False,  # CFR-009 compliance
        agent_id="project_manager"
    )

def _cancel_conversation(self):
    """Cancel current conversation and discard draft."""
    self.console.print("\n[yellow]User story discarded.[/yellow]")
    self._cleanup_conversation()

def _cleanup_conversation(self):
    """Clean up conversation state."""
    self.active_conversation = None
    self.awaiting_approval = False
    self.draft_text = None
```

**File Size Estimate**: +300 lines to existing `chat_interface.py`

**Dependencies**:
- `ConversationStateManager` (new)
- `ConversationalAIOrchestrator` (new)
- `ConversationalToneEnforcer` (new)
- Existing: `RoadmapEditor`, `AIService`, `NotificationDB`

---

## Implementation Plan

### Phase 1: Conversation State Manager (1-1.5 days / 10-12 hours)

**Objective**: Build core conversation state management with question tracking and correction handling.

**Tasks**:

1. **Create `conversation_state_manager.py`** (4 hours)
   - Define `Question` dataclass with text, key, category, dependencies
   - Implement `ConversationStateManager` class
   - Add `get_next_question()` method
   - Add `record_answer()` method
   - Add `is_complete()` method
   - Add `get_progress()` method
   - Add comprehensive docstrings

2. **Implement correction handling** (3 hours)
   - Add `handle_correction()` method
   - Track corrections in state
   - Call AI orchestrator for question regeneration
   - Preserve relevant answers during regeneration
   - Update current question index

3. **Add draft generation** (2 hours)
   - Implement `generate_draft()` method
   - Call AI orchestrator for formatting
   - Return formatted markdown draft

4. **Write unit tests** (3 hours)
   - Test question tracking (`get_next_question`, `record_answer`)
   - Test correction handling (question regeneration, answer preservation)
   - Test edge cases (no questions, all answered, mid-conversation correction)
   - Test `is_complete()` logic
   - Achieve >90% code coverage

**Deliverables**:
- `coffee_maker/cli/conversation_state_manager.py` (~200 lines)
- `tests/unit/test_conversation_state_manager.py` (~300 lines, 15-20 tests)

**Success Criteria**:
- All unit tests pass
- Conversation state correctly tracks questions and answers
- Correction handling regenerates questions without losing relevant answers

---

### Phase 2: AI Orchestration Layer (1.5-2 days / 12-16 hours)

**Objective**: Build AI orchestration for question generation, correction detection, and draft formatting.

**Tasks**:

1. **Create `conversational_ai_orchestrator.py`** (5 hours)
   - Implement `ConversationalAIOrchestrator` class
   - Add `generate_initial_questions()` with AI prompt
   - Add JSON parsing for AI responses
   - Add fallback default questions
   - Add error handling for AI failures
   - Write comprehensive docstrings

2. **Implement correction detection** (2 hours)
   - Add `detect_correction_intent()` method
   - Define correction regex patterns (sorry, actually, I meant, etc.)
   - Test pattern matching with various phrases
   - Log detection for debugging

3. **Add question regeneration** (4 hours)
   - Implement `regenerate_questions_after_correction()` method
   - Design AI prompt for regeneration (considers original + correction + existing answers)
   - Parse AI response to new questions
   - Fallback to `generate_initial_questions()` if parsing fails

4. **Implement answer preservation** (3 hours)
   - Add `preserve_relevant_answers()` method
   - Design AI prompt for relevance detection
   - Parse AI response for preserved answers
   - Conservative fallback (preserve nothing if uncertain)

5. **Add draft formatting** (2 hours)
   - Implement `format_draft()` method
   - Design AI prompt for structured formatting
   - Generate markdown with title, scope, DoD, effort, business value

6. **Write unit tests** (4 hours)
   - Test initial question generation (5 tests)
   - Test correction detection (8 tests for different patterns)
   - Test question regeneration (4 tests)
   - Test answer preservation (4 tests)
   - Test draft formatting (3 tests)
   - Mock AI responses for deterministic testing
   - Achieve >90% code coverage

**Deliverables**:
- `coffee_maker/cli/conversational_ai_orchestrator.py` (~400 lines)
- `tests/unit/test_conversational_ai_orchestrator.py` (~500 lines, 24+ tests)

**Success Criteria**:
- All unit tests pass
- AI orchestrator generates relevant questions
- Correction detection accurately identifies user corrections
- Question regeneration avoids redundant questions

---

### Phase 3: Conversational Tone Enforcement (0.5 day / 4 hours)

**Objective**: Ensure PM never uses robotic language and maintains conversational tone.

**Tasks**:

1. **Create `conversational_tone_enforcer.py`** (2 hours)
   - Implement `ConversationalToneEnforcer` class
   - Add `validate_message()` with robotic pattern detection
   - Add `add_transition()` for question transitions
   - Add `get_correction_acknowledgment()` for corrections
   - Add `detect_robotic_patterns()` for testing
   - Define robotic patterns (regex)
   - Define conversational transitions (templates)

2. **Write unit tests** (2 hours)
   - Test robotic pattern detection (10 tests for different patterns)
   - Test transition addition (first question vs. subsequent)
   - Test correction acknowledgment randomization
   - Test validation raises error on robotic patterns
   - Achieve 100% code coverage (small, focused class)

**Deliverables**:
- `coffee_maker/cli/conversational_tone_enforcer.py` (~150 lines)
- `tests/unit/test_conversational_tone_enforcer.py` (~200 lines, 15+ tests)

**Success Criteria**:
- All unit tests pass
- Robotic patterns reliably detected
- Conversational transitions feel natural
- Validation prevents robotic messages

---

### Phase 4: Chat Interface Integration (1 day / 8 hours)

**Objective**: Integrate conversational flow into existing ChatSession class.

**Tasks**:

1. **Add conversation state tracking** (1 hour)
   - Add `self.active_conversation` field
   - Add `self.awaiting_approval` field
   - Add `self.draft_text` field
   - Initialize AI orchestrator and tone enforcer

2. **Implement user story intent detection** (1 hour)
   - Add `_is_new_user_story()` method
   - Detect "user story:", "US:", "As a [role]..." patterns
   - Test with various user inputs

3. **Add conversation routing** (2 hours)
   - Modify `handle_user_message()` to route to conversation
   - Add `_start_user_story_conversation()` method
   - Add `_handle_conversation_message()` method
   - Add `_ask_next_question()` method with tone enforcement

4. **Implement correction handling** (1 hour)
   - Add `_handle_correction()` method
   - Display correction acknowledgment
   - Resume conversation from updated questions

5. **Add draft approval workflow** (2 hours)
   - Implement `_show_draft_for_approval()` method
   - Display draft with Rich UI formatting
   - Add `_handle_approval_response()` method
   - Handle yes/no/cancel responses

6. **Add ROADMAP integration** (1 hour)
   - Implement `_add_to_roadmap()` method
   - Assign next US number
   - Call `RoadmapEditor.add_user_story()`
   - Create notification (CFR-009 compliant: sound=False)
   - Add `_cancel_conversation()` and `_cleanup_conversation()`

**Deliverables**:
- Modified `coffee_maker/cli/chat_interface.py` (+300 lines)
- Integration documented in code comments

**Success Criteria**:
- Conversation flow works end-to-end in chat interface
- User can create user story conversationally
- Draft approval workflow functions correctly
- ROADMAP updated only after user approval

---

### Phase 5: Integration Testing (1 day / 8 hours)

**Objective**: Test end-to-end conversational flow with realistic scenarios.

**Tasks**:

1. **Write integration tests** (4 hours)
   - Test Scenario 1: Simple user story, no corrections (E2E)
   - Test Scenario 2: User correction mid-conversation (E2E)
   - Test Scenario 3: User requests changes to draft (E2E)
   - Test Scenario 4: User cancels mid-conversation (E2E)
   - Test Scenario 5: Robotic pattern prevention (automated check)
   - Mock AI responses for deterministic testing
   - Each scenario validates full flow from user input to ROADMAP update

2. **Manual testing** (3 hours)
   - Test with real user stories (5-10 examples)
   - Verify conversational tone feels natural
   - Test correction scenarios
   - Test draft approval workflow
   - Test edge cases (empty answer, very long answer, special characters)

3. **Bug fixes and refinement** (1 hour)
   - Address issues found during testing
   - Refine conversational transitions
   - Improve error messages
   - Optimize AI prompts

**Deliverables**:
- `tests/integration/test_conversational_user_story_creation.py` (~400 lines, 5+ E2E tests)
- Manual testing checklist with results
- Bug fixes applied

**Success Criteria**:
- All integration tests pass
- Manual testing confirms natural, collaborative feel
- No robotic patterns detected in any test
- Draft approval rate >85% (manual evaluation)

---

### Phase 6: Documentation & Methodology Update (0.5 day / 4 hours)

**Objective**: Document conversational interaction patterns for team and update methodology.

**Tasks**:

1. **Update COLLABORATION_METHODOLOGY.md** (2 hours)
   - Add Section 4.5: Conversational Interaction Patterns
   - Document one-by-one questioning principle
   - Document adaptive question regeneration
   - Document anti-patterns to avoid
   - Include examples from testing
   - Version bump to 1.9

2. **Create usage examples** (1 hour)
   - Write example conversations in docs/
   - Show correction scenario
   - Show draft approval workflow
   - Show cancellation

3. **Update CLAUDE.md** (1 hour)
   - Document new conversational workflow
   - Update agent responsibilities
   - Add examples of conversational tone
   - Cross-reference COLLABORATION_METHODOLOGY.md

**Deliverables**:
- Updated `docs/COLLABORATION_METHODOLOGY.md` (Section 4.5, ~300 lines)
- Updated `.claude/CLAUDE.md` (conversational workflow section)
- Example conversations in `docs/examples/conversational_user_story_examples.md`

**Success Criteria**:
- Documentation clearly explains conversational patterns
- Examples demonstrate natural flow
- Anti-patterns explicitly listed
- COLLABORATION_METHODOLOGY.md version bumped to 1.9

---

## Testing Strategy

### Unit Tests

**Coverage Target**: >90% for all new components

**Test Files**:
1. `tests/unit/test_conversation_state_manager.py` (~300 lines, 15-20 tests)
2. `tests/unit/test_conversational_ai_orchestrator.py` (~500 lines, 24+ tests)
3. `tests/unit/test_conversational_tone_enforcer.py` (~200 lines, 15+ tests)

**Test Categories**:

**A. ConversationStateManager Tests**:
- `test_initialization` - Verify initial state setup
- `test_get_next_question` - Returns questions in order
- `test_record_answer` - Stores answer and increments index
- `test_record_answer_no_current_question` - Raises error if no question
- `test_is_complete_false` - Returns False when questions remain
- `test_is_complete_true` - Returns True when all answered
- `test_get_progress` - Returns (answered, total) tuple
- `test_handle_correction` - Regenerates questions
- `test_handle_correction_preserves_answers` - Keeps relevant answers
- `test_handle_correction_resets_index` - Sets index correctly
- `test_generate_draft` - Calls AI orchestrator
- `test_multiple_corrections` - Handles multiple corrections
- `test_correction_with_no_previous_answers` - Works when no answers yet
- `test_correction_removes_irrelevant_answers` - Discards non-relevant answers

**B. ConversationalAIOrchestrator Tests**:
- `test_generate_initial_questions_success` - Parses AI response
- `test_generate_initial_questions_invalid_json` - Falls back to defaults
- `test_generate_initial_questions_missing_keys` - Handles malformed data
- `test_detect_correction_intent_sorry` - Detects "sorry" pattern
- `test_detect_correction_intent_actually` - Detects "actually" pattern
- `test_detect_correction_intent_i_meant` - Detects "I meant" pattern
- `test_detect_correction_intent_clarify` - Detects "clarify" pattern
- `test_detect_correction_intent_no_pattern` - Returns False when no correction
- `test_detect_correction_intent_case_insensitive` - Works with different cases
- `test_regenerate_questions_success` - Regenerates based on correction
- `test_regenerate_questions_invalid_json` - Falls back to initial generation
- `test_regenerate_questions_fewer_than_initial` - Generates 3-6 questions
- `test_preserve_relevant_answers_success` - Maps old to new
- `test_preserve_relevant_answers_empty_old` - Returns empty dict
- `test_preserve_relevant_answers_invalid_json` - Falls back to empty
- `test_preserve_relevant_answers_partial_match` - Preserves only matching
- `test_format_draft_success` - Formats as markdown
- `test_format_draft_with_all_categories` - Includes scope, DoD, effort, etc.
- `test_get_default_questions` - Returns 5 generic questions

**C. ConversationalToneEnforcer Tests**:
- `test_validate_message_conversational` - Returns True for natural language
- `test_validate_message_robotic_questions_1_6` - Raises error for "questions 1-6"
- `test_validate_message_robotic_q1` - Raises error for "Q1:"
- `test_validate_message_robotic_multiple_questions` - Raises error for batch
- `test_validate_message_robotic_answer_following` - Raises error for "answer the following"
- `test_add_transition_first_question` - Adds context-setting prefix
- `test_add_transition_subsequent_question` - Adds random transition
- `test_add_transition_randomization` - Varies transitions
- `test_get_correction_acknowledgment` - Returns random acknowledgment
- `test_get_correction_acknowledgment_randomization` - Varies acknowledgments
- `test_detect_robotic_patterns_none` - Returns empty list
- `test_detect_robotic_patterns_multiple` - Returns all matched patterns
- `test_detect_robotic_patterns_case_insensitive` - Works with different cases

### Integration Tests

**Coverage Target**: 5+ end-to-end scenarios

**Test File**: `tests/integration/test_conversational_user_story_creation.py` (~400 lines)

**Scenarios**:

**Scenario 1: Simple User Story (No Corrections)**
```python
def test_simple_user_story_no_corrections():
    """Test complete flow from user story to ROADMAP without corrections."""
    # Setup
    chat = ChatSession(...)

    # User initiates
    chat.handle_user_message("user story: As a developer I want syntax highlighting")

    # Verify first question asked
    assert "Let me ask some clarifying questions" in last_message()

    # User answers all questions
    chat.handle_user_message("Python, JavaScript, Bash")  # Q1
    chat.handle_user_message("In the chat interface")  # Q2
    # ... continue for all questions

    # Verify draft shown
    assert "Draft User Story" in last_message()
    assert "═" * 70 in last_message()

    # User approves
    chat.handle_user_message("yes")

    # Verify added to ROADMAP
    roadmap = read_roadmap()
    assert "US-XXX" in roadmap  # Replace with actual number
    assert "syntax highlighting" in roadmap
```

**Scenario 2: User Correction Mid-Conversation**
```python
def test_user_correction_mid_conversation():
    """Test correction triggers question regeneration."""
    # Setup
    chat = ChatSession(...)

    # User initiates
    chat.handle_user_message("user story: As a dev I want syntax highlighting")

    # Answer first question
    chat.handle_user_message("Python, JavaScript")

    # User corrects
    chat.handle_user_message("sorry the real story is: As a user I want email notifications")

    # Verify correction acknowledged
    assert "Ah, I understand now!" in last_message() or "Let me adjust" in last_message()

    # Verify new questions asked (not about syntax highlighting)
    next_message = get_next_message()
    assert "syntax" not in next_message.lower()
    assert "highlight" not in next_message.lower()
    # Should ask about notifications instead
    assert "notif" in next_message.lower() or "email" in next_message.lower()
```

**Scenario 3: User Requests Changes to Draft**
```python
def test_user_requests_draft_changes():
    """Test user can request changes to draft before approval."""
    # Setup and complete questions
    # ...

    # Draft shown
    assert "Draft User Story" in last_message()

    # User says no
    chat.handle_user_message("no")

    # Verify PM asks what to adjust
    assert "What would you like me to adjust?" in last_message()

    # User provides feedback
    chat.handle_user_message("Add edge cases to acceptance criteria")

    # Verify updated draft shown
    # (Implementation may vary - just verify flow works)
```

**Scenario 4: User Cancels Mid-Conversation**
```python
def test_user_cancels_mid_conversation():
    """Test user can cancel at any stage."""
    # Setup
    chat = ChatSession(...)

    # User initiates and answers first question
    chat.handle_user_message("user story: As a dev I want X")
    chat.handle_user_message("Answer 1")

    # User cancels
    chat.handle_user_message("cancel")

    # Verify conversation discarded
    assert "discarded" in last_message().lower()
    assert chat.active_conversation is None

    # Verify ROADMAP not modified
    roadmap_before = read_roadmap()
    # Start new conversation and cancel at draft stage
    chat.handle_user_message("user story: As a dev I want Y")
    # ... answer all questions ...
    # Draft shown
    chat.handle_user_message("cancel")
    roadmap_after = read_roadmap()
    assert roadmap_before == roadmap_after
```

**Scenario 5: Anti-Pattern Prevention**
```python
def test_anti_pattern_prevention():
    """Test robotic patterns are prevented at runtime."""
    # Setup
    chat = ChatSession(...)

    # Inject robotic message (simulating bug)
    # This should raise ValueError due to tone enforcement
    with pytest.raises(ValueError, match="Robotic tone detected"):
        enforcer = ConversationalToneEnforcer()
        enforcer.validate_message("Please answer questions 1-6")

    # Verify normal flow never produces robotic patterns
    chat.handle_user_message("user story: As a dev I want X")

    # Capture all PM messages
    messages = get_all_pm_messages()

    # Verify no robotic patterns in any message
    for msg in messages:
        robotic_patterns = enforcer.detect_robotic_patterns(msg)
        assert len(robotic_patterns) == 0, f"Robotic pattern in: {msg}"
```

### Manual Testing

**Checklist**:

1. **Natural Tone Verification**
   - [ ] Create 3 user stories with different complexity
   - [ ] Read conversation transcripts
   - [ ] Verify transitions feel natural ("Got it!", "Perfect!")
   - [ ] No robotic language detected

2. **Correction Scenarios**
   - [ ] Test correction at question 1
   - [ ] Test correction at question 3
   - [ ] Test correction at question 5
   - [ ] Verify new questions relevant to corrected story
   - [ ] Verify no redundant questions

3. **Draft Approval Workflow**
   - [ ] Test "yes" approval
   - [ ] Test "no" with changes requested
   - [ ] Test "cancel" at draft stage
   - [ ] Verify ROADMAP updated only on "yes"

4. **Edge Cases**
   - [ ] Empty user story text
   - [ ] Very long user story (>500 words)
   - [ ] User story with special characters
   - [ ] Multiple corrections in single conversation
   - [ ] Correction that undoes previous correction

5. **Performance**
   - [ ] Measure response time for question generation
   - [ ] Measure response time for draft generation
   - [ ] Verify <3 seconds for AI operations
   - [ ] Total conversation <30 seconds

6. **User Satisfaction**
   - [ ] Get feedback from 3-5 users
   - [ ] Measure approval rate on first-try draft
   - [ ] Target: >85% approval rate
   - [ ] Ask: "Did the conversation feel natural and collaborative?" (target: >4/5)

---

## Security Considerations

### Input Validation

**User Message Validation**:
- Sanitize user input before sending to AI (strip control characters)
- Limit message length (max 2000 characters for user story, max 500 per answer)
- Validate JSON responses from AI (schema validation)
- Prevent injection attacks in AI prompts (escape special characters)

**Implementation**:
```python
def _sanitize_user_input(message: str) -> str:
    """Sanitize user input for AI processing.

    Args:
        message: Raw user input

    Returns:
        Sanitized input
    """
    # Strip control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', message)

    # Limit length
    if len(sanitized) > 2000:
        sanitized = sanitized[:2000]
        logger.warning("User input truncated to 2000 characters")

    return sanitized.strip()
```

### AI Response Validation

**JSON Schema Validation**:
- Validate AI responses match expected schema
- Reject malformed responses (fallback to defaults)
- Prevent code injection via crafted JSON

**Implementation**:
```python
import jsonschema

QUESTION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "minLength": 10, "maxLength": 200},
            "key": {"type": "string", "pattern": "^[a-z_]+$"},
            "category": {"type": "string", "enum": ["scope", "acceptance_criteria", "effort", "priority"]}
        },
        "required": ["text", "key", "category"]
    }
}

def _validate_ai_questions(response: str) -> List[dict]:
    """Validate AI question response.

    Args:
        response: JSON string from AI

    Returns:
        Validated question data

    Raises:
        jsonschema.ValidationError: If response invalid
    """
    data = json.loads(response)
    jsonschema.validate(data, QUESTION_SCHEMA)
    return data
```

### ROADMAP File Safety

**Transaction Safety**:
- Create backup before any ROADMAP modification
- Use atomic file writes (write to temp, then rename)
- Verify ROADMAP syntax after update (markdown validation)
- Rollback to backup if update fails

**Implementation** (existing in `RoadmapEditor`):
```python
# Already implemented in RoadmapEditor
# - Uses backup files
# - Atomic writes with tempfile
# - No changes needed for this spec
```

### Rate Limiting

**AI API Protection**:
- Limit conversation creation to 10 per hour per user (prevent abuse)
- Limit AI calls per conversation (max 20 questions)
- Implement exponential backoff for AI failures

**Implementation**:
```python
from datetime import datetime, timedelta
from collections import defaultdict

class ConversationRateLimiter:
    """Rate limit conversation creation to prevent abuse."""

    def __init__(self, max_per_hour: int = 10):
        self.max_per_hour = max_per_hour
        self.conversation_timestamps = defaultdict(list)

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # Remove old timestamps
        self.conversation_timestamps[user_id] = [
            ts for ts in self.conversation_timestamps[user_id]
            if ts > one_hour_ago
        ]

        # Check limit
        if len(self.conversation_timestamps[user_id]) >= self.max_per_hour:
            return False

        # Record this conversation
        self.conversation_timestamps[user_id].append(now)
        return True
```

### Sensitive Data Protection

**No PII in Logs**:
- Avoid logging user story content (may contain sensitive info)
- Log only metadata (question count, answer count, timestamps)
- Mask user input in error messages

**Implementation**:
```python
def _log_conversation_event(event: str, metadata: dict):
    """Log conversation event without sensitive data.

    Args:
        event: Event name (e.g., "question_asked", "answer_recorded")
        metadata: Non-sensitive metadata (question_idx, category, etc.)
    """
    # ✅ Safe to log
    logger.info(f"Conversation event: {event}", extra=metadata)

    # ❌ DO NOT log user content
    # logger.info(f"User answered: {user_answer}")  # NO!
```

---

## Performance Requirements

### Response Time Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Initial question generation | <2s | AI call |
| Question regeneration after correction | <2s | AI call |
| Draft generation | <3s | AI call |
| Answer recording | <100ms | Local state update |
| Correction detection | <50ms | Regex matching |
| Tone validation | <50ms | Regex matching |
| Total conversation (8 questions) | <30s | Including user think time |

### Resource Constraints

**Memory Usage**:
- Conversation state: <10KB per active conversation
- Maximum concurrent conversations: 50 (for multi-user future)
- Total memory overhead: <500KB

**AI Token Usage**:
- Initial questions: ~800 tokens (prompt + response)
- Question regeneration: ~1000 tokens (includes existing answers)
- Draft formatting: ~1200 tokens (includes all Q&A pairs)
- Total per conversation: <3000 tokens (~$0.015 at current Claude pricing)

**Network**:
- AI API calls: 3-5 per conversation (questions, regeneration, draft)
- Each call: 1-2 seconds latency
- Total network time: <10 seconds per conversation

### Optimization Strategies

**Caching**:
- Cache default questions (no AI call needed for fallback)
- Cache correction patterns (compiled regex)
- Cache conversational transitions (pre-generated)

**Batch Processing**:
- NOT applicable (one-by-one questioning is core requirement)

**Lazy Loading**:
- Generate questions on-demand (don't generate all upfront)
- Only call AI when user provides input (not preemptively)

---

## Risk Analysis

### Technical Risks

**Risk 1: AI Service Unavailable**
- **Impact**: High - Cannot generate questions or draft
- **Probability**: Medium (API outages happen)
- **Mitigation**:
  - Implement fallback to default questions
  - Retry with exponential backoff (3 retries)
  - Degrade gracefully to manual user story entry
  - Display clear error message to user
- **Detection**: Monitor AI API response codes
- **Recovery**: Automatic retry, then fallback

**Risk 2: AI Generates Irrelevant Questions**
- **Impact**: Medium - Poor user experience, low approval rate
- **Probability**: Medium (AI can misunderstand)
- **Mitigation**:
  - Test prompts extensively with diverse user stories
  - Include examples in AI prompts (few-shot learning)
  - Allow user to skip irrelevant questions
  - Track approval rate metric (alert if <70%)
- **Detection**: Manual testing, user feedback
- **Recovery**: Improve AI prompts, add more examples

**Risk 3: Conversation State Corruption**
- **Impact**: High - Lost conversation progress, user frustration
- **Probability**: Low (good state management design)
- **Mitigation**:
  - Atomic state updates (all-or-nothing)
  - Deep copy for state modifications
  - Unit tests for all state transitions
  - Log state changes for debugging
- **Detection**: Unit tests, integration tests
- **Recovery**: Restart conversation if corruption detected

**Risk 4: Robotic Tone Slips Through**
- **Impact**: Medium - Defeats purpose of conversational UX
- **Probability**: Low (tone enforcer in place)
- **Mitigation**:
  - Automated detection in unit tests
  - Raise error on robotic patterns (fail-fast)
  - Manual review of all conversation transcripts
  - User feedback mechanism
- **Detection**: Unit tests, manual testing
- **Recovery**: Fix prompts/transitions, add pattern to enforcer

**Risk 5: Performance Degradation (Slow AI)**
- **Impact**: Medium - User perception of slowness
- **Probability**: Medium (AI latency varies)
- **Mitigation**:
  - Set strict timeout (5 seconds per AI call)
  - Show loading indicators to user
  - Fallback to defaults on timeout
  - Monitor AI latency metrics
- **Detection**: Performance tests, monitoring
- **Recovery**: Timeout → fallback, retry with backoff

### UX Risks

**Risk 6: Users Prefer Old Workflow**
- **Impact**: Low - Can keep old workflow alongside
- **Probability**: Low (conversational should be better)
- **Mitigation**:
  - A/B test with small user group first
  - Collect user satisfaction feedback
  - Keep old workflow as fallback option
  - Document when to use each workflow
- **Detection**: User surveys, adoption metrics
- **Recovery**: Revert if satisfaction <3/5

**Risk 7: Conversation Too Long**
- **Impact**: Medium - User fatigue, abandonment
- **Probability**: Medium (AI may over-ask)
- **Mitigation**:
  - Limit questions to 5-8 (hard cap)
  - Design AI prompts to be concise
  - Track average conversation length
  - Allow user to skip optional questions
- **Detection**: Manual testing, analytics
- **Recovery**: Reduce question count, simplify prompts

**Risk 8: Draft Doesn't Match User Intent**
- **Impact**: High - Low approval rate, user frustration
- **Probability**: Medium (AI formatting errors)
- **Mitigation**:
  - Extensive testing of draft formatting
  - Show draft for approval (not auto-add)
  - Allow user to request changes
  - Track approval rate (alert if <85%)
- **Detection**: Manual testing, approval rate metric
- **Recovery**: Improve draft formatting prompt, add examples

### Operational Risks

**Risk 9: High AI Costs**
- **Impact**: Low - Still within budget
- **Probability**: Low (~$0.015 per conversation)
- **Mitigation**:
  - Monitor token usage per conversation
  - Set budget alerts (<$10/day)
  - Optimize prompts to reduce tokens
  - Cache where possible
- **Detection**: Cost monitoring dashboard
- **Recovery**: Reduce token usage, implement stricter caching

**Risk 10: Inconsistent Behavior Across AI Versions**
- **Impact**: Medium - Different UX over time
- **Probability**: Low (API versioning stable)
- **Mitigation**:
  - Pin Claude API version in code
  - Test new API versions before upgrading
  - Log API version in all requests
  - Have regression tests
- **Detection**: Integration tests fail after API update
- **Recovery**: Pin to previous stable version, fix prompts

---

## Success Criteria

### Functional Criteria (Must-Have)

1. **✅ One-by-One Question Flow**
   - PM asks questions individually (verified: no batching in any test)
   - Waits for user response before next question (verified: state machine blocks)
   - No numbered or grouped questions (verified: tone enforcer prevents)

2. **✅ Adaptive Question Regeneration**
   - Detects user corrections with >95% accuracy (verified: unit tests)
   - Regenerates questions based on corrected understanding (verified: integration tests)
   - Preserves relevant answers (verified: unit tests)
   - No redundant questions after correction (verified: manual testing)

3. **✅ User Input Authority**
   - Accepts corrections immediately (verified: no confirmation prompts)
   - Changes apply without hesitation (verified: state updates atomic)
   - No "Are you sure?" prompts (verified: code review)

4. **✅ Draft Confirmation**
   - Shows formatted draft before ROADMAP update (verified: integration tests)
   - Waits for explicit approval (verified: state machine)
   - Only adds on "yes"/"approve" (verified: unit tests)

5. **✅ Conversational Tone**
   - No robotic language in any message (verified: automated checks)
   - Conversational transitions present (verified: manual review)
   - Natural acknowledgments (verified: manual review)

6. **✅ Session Persistence**
   - Conversation state preserved during session (verified: integration tests)
   - Cleanup on completion/cancellation (verified: memory leak tests)

### Non-Functional Criteria (Should-Have)

7. **✅ Response Latency**
   - Question generation <2s (verified: performance tests)
   - Draft generation <3s (verified: performance tests)
   - Total conversation <30s for 8 questions (verified: manual testing)

8. **✅ Accuracy**
   - Draft approval rate >85% (verified: manual testing with 10+ user stories)
   - Correction detection >95% (verified: unit tests with 20+ patterns)
   - Answer preservation >90% (verified: unit tests)

9. **✅ Reliability**
   - No state corruption (verified: stress tests)
   - Graceful AI failure handling (verified: unit tests with mocked failures)
   - Transaction safety for ROADMAP (verified: existing RoadmapEditor tests)

10. **✅ Maintainability**
    - Code coverage >90% for new components (verified: coverage report)
    - Clear component separation (verified: architecture review)
    - Comprehensive documentation (verified: docstring coverage)

### User Experience Criteria (Nice-to-Have)

11. **✅ User Satisfaction**
    - "Natural and collaborative" rating >4/5 (verified: user surveys)
    - Users prefer conversational flow over old approach (verified: A/B test)
    - Reduced friction in user story creation (verified: task completion time)

12. **✅ Efficiency**
    - Average conversation length <8 questions (verified: analytics)
    - No abandoned conversations due to length (verified: analytics)
    - Time to complete user story <5 minutes (verified: manual testing)

---

## Appendix

### Example Conversations

**Example 1: Simple Flow (No Corrections)**

```
User: user story: As a developer I want syntax highlighting in code blocks

PM: Let me ask some clarifying questions to understand better.

What programming languages should be highlighted?

User: Python, JavaScript, and Bash

PM: Got it! Where should this highlighting appear?

User: In the chat interface when displaying code

PM: Perfect! What defines success for this feature?

User: Code is visually distinct with correct syntax colors

PM: Excellent! How complex is this feature (simple/medium/complex)?

User: Medium complexity

PM: Great! I have all the information I need. Here's the user story draft:

════════════════════════════════════════════════════════════════
## 📝 US-021 - Syntax Highlighting in Code Blocks

**User Story**:
> "As a developer I want syntax highlighting in code blocks"

**Scope**:
- Languages: Python, JavaScript, Bash
- Location: Chat interface code display
- Visual distinction with syntax colors

**Acceptance Criteria**:
1. Python code highlighted with correct syntax colors
2. JavaScript code highlighted with correct syntax colors
3. Bash code highlighted with correct syntax colors
4. Code visually distinct from regular text

**Implementation Plan**:
- Phase 1: Integrate syntax highlighting library (e.g., Pygments)
- Phase 2: Add language detection for code blocks
- Phase 3: Apply highlighting in chat interface

**Estimated Effort**: 2-3 days
**Business Value**: ⭐⭐⭐⭐
════════════════════════════════════════════════════════════════

Does this match what you had in mind?

Options:
  - 'yes' or 'approve' → I'll add this to ROADMAP.md
  - 'no' or 'changes needed' → Tell me what to adjust
  - 'cancel' → Discard this user story

User: yes

PM: ✅ Added to ROADMAP.md!
```

**Example 2: With Correction Mid-Conversation**

```
User: user story: As a pm I want to see branches related to what I document

PM: Let me ask some clarifying questions to understand better.

What information do you need from branches?

User: Branch names and their status

PM: Got it! How should branches be displayed?

User: sorry the real story is: As a user I want to be notified when a delivery is ready to ship

PM: Ah, I understand now! Let me adjust my questions based on that.

What notifications do you want to receive?

User: When PR is opened and when it's ready for review

PM: Perfect! How should you be notified?

User: Desktop notification and email

PM: Excellent! What defines "ready to ship"?

User: All tests pass and code review approved

PM: Great! I have all the information I need. Here's the user story draft:

════════════════════════════════════════════════════════════════
## 📝 US-022 - Delivery Ready Notifications

**User Story**:
> "As a user I want to be notified when a delivery is ready to ship"

**Scope**:
- Notifications when PR opened
- Notifications when PR ready for review
- Delivery methods: Desktop notification + Email

**Acceptance Criteria**:
1. Notification sent when PR is opened
2. Notification sent when PR ready for review
3. "Ready to ship" defined as: All tests pass AND code review approved
4. Desktop notification displays correctly
5. Email notification includes PR link and summary

**Implementation Plan**:
- Phase 1: Set up notification service integration
- Phase 2: Add PR event listeners (opened, review requested)
- Phase 3: Implement desktop notification display
- Phase 4: Implement email notification sending

**Estimated Effort**: 3-4 days
**Business Value**: ⭐⭐⭐⭐⭐
════════════════════════════════════════════════════════════════

Does this match what you had in mind?

Options:
  - 'yes' or 'approve' → I'll add this to ROADMAP.md
  - 'no' or 'changes needed' → Tell me what to adjust
  - 'cancel' → Discard this user story

User: yes

PM: ✅ Added to ROADMAP.md!
```

### Glossary

**Terms**:

- **Conversational Flow**: Question-answer interaction that feels natural, adaptive, and collaborative (not robotic)
- **One-by-One Questioning**: Asking questions individually and waiting for each response before proceeding
- **Adaptive Questioning**: Reconsideration of remaining questions when user provides corrections or clarifications
- **Correction Intent**: User signals that they want to change/clarify their previous input (detected via patterns like "sorry", "actually")
- **Question Regeneration**: Process of generating new questions based on corrected user story understanding
- **Answer Preservation**: Keeping previous answers that are still relevant after a correction
- **Draft Approval**: Showing formatted user story to user and waiting for explicit "yes"/"approve" before adding to ROADMAP
- **Robotic Pattern**: Language that feels mechanical or interrogative (e.g., "Please answer questions 1-6")
- **Conversational Transition**: Natural phrase connecting questions (e.g., "Got it! Next question:")
- **Tone Enforcement**: Automated prevention of robotic language patterns

**Acronyms**:

- **PM**: Project Manager (agent)
- **AI**: Artificial Intelligence (Claude API)
- **DoD**: Definition of Done
- **UX**: User Experience
- **E2E**: End-to-End (testing)
- **MVP**: Minimum Viable Product
- **FR**: Functional Requirement
- **NFR**: Non-Functional Requirement

### References

**Related Documents**:

- **US-020** in `docs/roadmap/ROADMAP.md` - User story this spec implements
- **SPEC-012** in `docs/architecture/specs/SPEC-012-natural-language-user-story-management.md` - Related natural language processing spec
- **COLLABORATION_METHODOLOGY.md** Section 4.6 - Communication guidelines (plain language, no technical shorthand)
- **CFR-009** in `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` - Sound notification rules (project_manager must use `sound=False`)

**External Resources**:

- **Claude API Documentation**: https://docs.anthropic.com/claude/reference
- **Prompt Engineering Guide**: https://www.promptingguide.ai/
- **Conversational Design Principles**: Nielsen Norman Group (https://www.nngroup.com/articles/conversational-interfaces/)

---

## Implementation Checklist

Use this checklist during implementation to track progress:

**Phase 1: Conversation State Manager**
- [ ] Create `conversation_state_manager.py`
- [ ] Implement `Question` dataclass
- [ ] Implement `ConversationStateManager` class
- [ ] Add `get_next_question()` method
- [ ] Add `record_answer()` method
- [ ] Add `handle_correction()` method
- [ ] Add `is_complete()` method
- [ ] Add `get_progress()` method
- [ ] Add `generate_draft()` method
- [ ] Write unit tests (15-20 tests)
- [ ] Achieve >90% code coverage

**Phase 2: AI Orchestration Layer**
- [ ] Create `conversational_ai_orchestrator.py`
- [ ] Implement `ConversationalAIOrchestrator` class
- [ ] Add `generate_initial_questions()` method
- [ ] Add `detect_correction_intent()` method
- [ ] Add `regenerate_questions_after_correction()` method
- [ ] Add `preserve_relevant_answers()` method
- [ ] Add `format_draft()` method
- [ ] Add `_get_default_questions()` fallback
- [ ] Write unit tests (24+ tests)
- [ ] Achieve >90% code coverage

**Phase 3: Conversational Tone Enforcement**
- [ ] Create `conversational_tone_enforcer.py`
- [ ] Implement `ConversationalToneEnforcer` class
- [ ] Add `validate_message()` method
- [ ] Add `add_transition()` method
- [ ] Add `get_correction_acknowledgment()` method
- [ ] Add `detect_robotic_patterns()` method
- [ ] Define robotic patterns (regex list)
- [ ] Define conversational transitions (templates)
- [ ] Write unit tests (15+ tests)
- [ ] Achieve 100% code coverage

**Phase 4: Chat Interface Integration**
- [ ] Add conversation state fields to `ChatSession`
- [ ] Initialize AI orchestrator and tone enforcer
- [ ] Add `_is_new_user_story()` method
- [ ] Modify `handle_user_message()` for routing
- [ ] Add `_start_user_story_conversation()` method
- [ ] Add `_handle_conversation_message()` method
- [ ] Add `_ask_next_question()` method
- [ ] Add `_handle_correction()` method
- [ ] Add `_show_draft_for_approval()` method
- [ ] Add `_handle_approval_response()` method
- [ ] Add `_add_to_roadmap()` method
- [ ] Add `_cancel_conversation()` method
- [ ] Add `_cleanup_conversation()` method

**Phase 5: Integration Testing**
- [ ] Write Scenario 1: Simple user story (no corrections)
- [ ] Write Scenario 2: User correction mid-conversation
- [ ] Write Scenario 3: User requests changes to draft
- [ ] Write Scenario 4: User cancels mid-conversation
- [ ] Write Scenario 5: Anti-pattern prevention
- [ ] Manual testing with 10+ user stories
- [ ] Measure draft approval rate (target: >85%)
- [ ] Fix bugs found during testing
- [ ] Refine conversational tone

**Phase 6: Documentation**
- [ ] Add Section 4.5 to COLLABORATION_METHODOLOGY.md
- [ ] Update `.claude/CLAUDE.md` with conversational workflow
- [ ] Create example conversations document
- [ ] Update version to 1.9 in COLLABORATION_METHODOLOGY.md
- [ ] Review all docstrings for completeness
- [ ] Add comments to complex logic

**Final Verification**
- [ ] All unit tests pass (>90% coverage)
- [ ] All integration tests pass
- [ ] Manual testing complete (10+ user stories)
- [ ] Draft approval rate >85%
- [ ] No robotic patterns detected
- [ ] User satisfaction >4/5
- [ ] Documentation complete
- [ ] Code review passed

---

**END OF SPECIFICATION**
