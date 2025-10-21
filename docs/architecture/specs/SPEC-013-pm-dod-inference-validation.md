# SPEC-013: PM DoD Inference and Validation

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-013 - Automatic DoD Inference During `/US` Workflow

**Related ADRs**: None

**Assigned To**: code_developer

---

## Executive Summary

This specification describes the technical design for automatic Definition of Done (DoD) inference during the `/US` command workflow. The system will check for similar existing user stories, detect if features are already shipped or partially complete, and infer DoD based on the user story description. This enhances US-012 with intelligent DoD generation and similarity detection to prevent duplicate work.

---

## Problem Statement

### Current Situation

When users create user stories via `/US` command (US-012):
- No DoD is automatically generated (user must write manually)
- No check for similar existing user stories
- Risk of creating duplicate user stories for already-shipped features
- Risk of missing that a feature is partially complete (should enhance, not create new)

This leads to:
- Wasted effort on already-completed features
- Fragmented work across multiple similar user stories
- Missing DoD (reduces clarity on completion criteria)

### Goal

Enhance the `/US` workflow (US-012) to:
- Check ROADMAP for similar existing user stories BEFORE creating new one
- Detect if requested feature is already shipped or partially complete
- Present options: enhance existing, create new, or inform user it's complete
- Infer DoD from user story description if user doesn't provide one
- Allow user to validate/modify inferred DoD before adding to ROADMAP

### Non-Goals

- NOT implementing automatic prioritization (manual user decision)
- NOT implementing feature flagging or deployment detection (just ROADMAP analysis)
- NOT implementing advanced similarity algorithms (simple keyword matching for MVP)

---

## Requirements

### Functional Requirements

1. **FR-1**: Check ROADMAP for similar user stories when `/US` command is run
2. **FR-2**: Detect if feature already exists (status: "✅ COMPLETE")
3. **FR-3**: Detect if feature is partially complete (similar US exists, incomplete)
4. **FR-4**: Present options to user: enhance existing, create new, or inform complete
5. **FR-5**: Infer DoD from user story description using AI
6. **FR-6**: Present inferred DoD to user for validation
7. **FR-7**: Allow user to modify DoD before adding to ROADMAP
8. **FR-8**: Add validated DoD to user story in ROADMAP
9. **FR-9**: Support manual DoD entry if user prefers (bypass inference)

### Non-Functional Requirements

1. **NFR-1**: Similarity check completes in < 2 seconds (ROADMAP scan)
2. **NFR-2**: DoD inference completes in < 3 seconds (Claude API)
3. **NFR-3**: Similarity detection accuracy > 75% (keyword-based for MVP)
4. **NFR-4**: DoD inference quality > 80% (testable, specific criteria)
5. **NFR-5**: Graceful degradation if AI unavailable (prompt user for manual DoD)

### Constraints

- Must integrate with US-012 workflow (not standalone)
- Must use existing AIService for DoD inference
- Must use existing RoadmapEditor for ROADMAP scanning
- Must follow COLLABORATION_METHODOLOGY.md Section 6 (DoD template)
- Must not slow down `/US` command significantly (< 5 sec total)

---

## Proposed Solution

### High-Level Approach

Extend US-012's `/US` workflow with two new phases:
1. **Similarity Check**: Before drafting user story, scan ROADMAP for similar titles/descriptions
2. **DoD Inference**: After user validates user story structure, infer DoD and present for validation

New components:
- `SimilarityChecker`: Scan ROADMAP for similar user stories
- `DoDInferenceService`: Use AI to infer DoD from user story description
- Enhanced `UserStoryCommandHandler`: Orchestrate similarity check → US draft → DoD inference → validation

### Architecture Diagram

```
┌─────────────────┐
│  User (Chat)    │
└────────┬────────┘
         │
         │ "/US I want email notifications"
         v
┌───────────────────────────────────────────────┐
│  UserStoryCommandHandler (ENHANCED)           │
│  Step 1: Check similarity                     │
└────────┬──────────────────────────────────────┘
         │
         │ Find similar user stories
         v
┌───────────────────────────────────────────────┐
│  SimilarityChecker (NEW)                      │
│  .find_similar_user_stories(description)      │
└────────┬──────────────────────────────────────┘
         │
         │ Returns similar stories or None
         v
┌───────────────────────────────────────────────┐
│  UserStoryCommandHandler                      │
│  Step 2a: If similar found → Present options  │
│  Step 2b: If none found → Extract user story  │
└────────┬──────────────────────────────────────┘
         │
         │ (if no duplicates)
         v
┌───────────────────────────────────────────────┐
│  AIService.extract_user_story()               │
│  (US-012 - existing)                          │
└────────┬──────────────────────────────────────┘
         │
         │ User validates draft
         v
┌───────────────────────────────────────────────┐
│  UserStoryCommandHandler                      │
│  Step 3: Ask for DoD or infer                 │
└────────┬──────────────────────────────────────┘
         │
         │ User: "Infer it" or provides DoD
         v
┌───────────────────────────────────────────────┐
│  DoDInferenceService (NEW)                    │
│  .infer_dod(user_story_draft)                 │
└────────┬──────────────────────────────────────┘
         │
         │ Returns inferred DoD
         v
┌───────────────────────────────────────────────┐
│  UserStoryCommandHandler                      │
│  Step 4: Present DoD for validation           │
└────────┬──────────────────────────────────────┘
         │
         │ User validates DoD
         v
┌───────────────────────────────────────────────┐
│  RoadmapEditor.add_user_story()               │
│  (includes validated DoD)                     │
└───────────────────────────────────────────────┘
         │
         v
     ROADMAP.md updated ✅
```

### Technology Stack

- **Similarity Detection**: Keyword matching + TF-IDF (scikit-learn, optional)
- **DoD Inference**: Claude API (via AIService)
- **ROADMAP Scanning**: Existing RoadmapEditor
- **Prompts**: `.claude/commands/infer-dod.md`

---

## Detailed Design

### Component 1: SimilarityChecker

**Responsibility**: Find similar user stories in ROADMAP to prevent duplicates

**Interface**:
```python
@dataclass
class SimilarUserStory:
    """Similar user story found in ROADMAP."""
    id: str  # e.g., "US-009"
    title: str
    status: str  # "✅ COMPLETE", "🔄 In Progress", "📝 PLANNED"
    similarity_score: float  # 0.0-1.0
    description: Optional[str] = None


class SimilarityChecker:
    """
    Finds similar user stories in ROADMAP to prevent duplicates.

    Uses keyword-based similarity for MVP (simple, fast).
    Future: TF-IDF or embeddings for better accuracy.
    """

    def __init__(self, roadmap_editor: RoadmapEditor):
        """Initialize with roadmap editor."""
        self.roadmap_editor = roadmap_editor

    def find_similar_user_stories(
        self,
        description: str,
        threshold: float = 0.6
    ) -> List[SimilarUserStory]:
        """
        Find user stories similar to description.

        Args:
            description: User's natural language input
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of similar user stories (sorted by similarity)

        Example:
            >>> checker.find_similar_user_stories("email notifications")
            [
                SimilarUserStory(
                    id="US-009",
                    title="Notification System",
                    status="✅ COMPLETE",
                    similarity_score=0.82,
                    description="Add sound notifications..."
                )
            ]
        """
        pass

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text (lowercase, remove stopwords)."""
        # Simple implementation:
        # 1. Lowercase
        # 2. Remove common stopwords ("the", "a", "is", etc.)
        # 3. Extract nouns/verbs (or just all words for MVP)
        pass

    def _calculate_similarity(
        self,
        keywords1: Set[str],
        keywords2: Set[str]
    ) -> float:
        """
        Calculate Jaccard similarity between keyword sets.

        Jaccard similarity = |intersection| / |union|

        Returns:
            Similarity score 0.0-1.0
        """
        # Jaccard similarity: simple and fast
        # intersection / union
        pass

    def _parse_user_story_from_roadmap(
        self,
        roadmap_text: str
    ) -> List[Dict[str, str]]:
        """Parse user stories from ROADMAP markdown."""
        # Extract US-XXX sections with regex
        # Parse title, status, description
        pass
```

**Implementation Notes**:
- Uses keyword-based Jaccard similarity for MVP (simple, no ML dependencies)
- Stopwords: ["the", "a", "an", "is", "are", "want", "need", "to", "for"]
- Similarity threshold: 0.6 (adjustable, tuned via testing)
- Future: Use sentence embeddings (SBERT) for better semantic similarity

### Component 2: DoDInferenceService

**Responsibility**: Infer DoD from user story description using AI

**Interface**:
```python
@dataclass
class DoDCriteria:
    """Definition of Done criteria."""
    criteria: List[str]  # List of testable acceptance criteria
    confidence: float  # 0.0-1.0 (AI confidence in inference)


class DoDInferenceService:
    """
    Infers Definition of Done from user story using AI.

    Uses Claude API with specialized prompt following
    COLLABORATION_METHODOLOGY.md Section 6 DoD template.
    """

    def __init__(self, ai_service: AIService):
        """Initialize with AI service."""
        self.ai_service = ai_service

    def infer_dod(self, user_story_draft: UserStoryDraft) -> DoDCriteria:
        """
        Infer DoD from user story draft.

        Args:
            user_story_draft: User story awaiting DoD

        Returns:
            DoDCriteria with inferred acceptance criteria

        Raises:
            ValueError: If user story is invalid
            AIServiceError: If Claude API fails

        Example:
            >>> service.infer_dod(draft)
            DoDCriteria(
                criteria=[
                    "✅ Email notifications sent when daemon completes task",
                    "✅ Email includes task name and completion status",
                    "✅ User can configure email address in settings",
                    "✅ Email delivery confirmed via SMTP logs",
                    "✅ Tests verify email sent on task completion"
                ],
                confidence=0.92
            )
        """
        # Use centralized prompt
        prompt = load_prompt(PromptNames.INFER_DOD, {
            "TITLE": user_story_draft.title,
            "DESCRIPTION": user_story_draft.description,
            "AS_A": user_story_draft.as_a or "",
            "I_WANT": user_story_draft.i_want or "",
            "SO_THAT": user_story_draft.so_that or ""
        })

        # Call Claude API
        response = self.ai_service.client.messages.create(
            model=self.ai_service.model,
            max_tokens=self.ai_service.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response into DoDCriteria
        dod = self._parse_dod_response(response.content[0].text)

        return dod

    def _parse_dod_response(self, response_text: str) -> DoDCriteria:
        """Parse Claude's DoD response into structured format."""
        # Expected format:
        # ✅ Criterion 1
        # ✅ Criterion 2
        # ✅ Criterion 3
        # Confidence: 0.92
        pass

    def _validate_dod_quality(self, criteria: List[str]) -> bool:
        """
        Validate that DoD criteria are testable and specific.

        Good: "✅ User can log in with email and password"
        Bad: "✅ Login works"

        Returns:
            True if criteria meet quality standards
        """
        # Check:
        # 1. Each criterion is actionable (contains verb)
        # 2. Each criterion is testable (not vague)
        # 3. Minimum 3 criteria (comprehensive)
        pass
```

**Implementation Notes**:
- Uses new prompt: `.claude/commands/infer-dod.md`
- Follows COLLABORATION_METHODOLOGY.md Section 6 DoD template
- Generates 3-7 testable acceptance criteria
- Each criterion starts with ✅ (consistent with ROADMAP format)
- Validates quality: specific, testable, actionable

### Component 3: Enhanced UserStoryCommandHandler

**Responsibility**: Orchestrate similarity check → US draft → DoD inference workflow

**Enhanced Workflow**:
```python
class UserStoryCommandHandler:
    """ENHANCED from US-012 to include similarity check + DoD inference."""

    def __init__(
        self,
        ai_service: AIService,
        roadmap_editor: RoadmapEditor,
        similarity_checker: SimilarityChecker,  # NEW
        dod_service: DoDInferenceService  # NEW
    ):
        """Initialize with all required services."""
        self.ai_service = ai_service
        self.roadmap_editor = roadmap_editor
        self.draft_manager = UserStoryDraftManager()
        self.similarity_checker = similarity_checker  # NEW
        self.dod_service = dod_service  # NEW

    def handle_command(
        self,
        user_input: str,
        session_id: str
    ) -> str:
        """
        Handle /US command with similarity check + DoD inference.

        Workflow:
        1. Parse /US [description]
        2. Check for similar user stories (NEW)
        3. If similar found → present options (NEW)
        4. Extract user story draft (US-012)
        5. User validates draft
        6. Infer DoD (NEW)
        7. User validates DoD (NEW)
        8. Add to ROADMAP with DoD

        Returns:
            Response message to user
        """
        # Parse command
        description = self._parse_us_command(user_input)
        if not description:
            return "Please provide a description: /US [what you want]"

        # STEP 1: Check for similar user stories (NEW)
        similar = self.similarity_checker.find_similar_user_stories(description)

        if similar:
            # Present options to user
            return self._present_similarity_options(similar, description, session_id)

        # STEP 2: No duplicates, proceed with extraction (US-012)
        draft = self.ai_service.extract_user_story(description)
        self.draft_manager.store_draft(session_id, draft)

        # Present draft for validation
        return self.draft_manager.format_for_review(draft)

    def _present_similarity_options(
        self,
        similar: List[SimilarUserStory],
        description: str,
        session_id: str
    ) -> str:
        """
        Present options when similar user stories found.

        Options:
        A) Enhance existing user story (if incomplete)
        B) Create new user story (separate from existing)
        C) Already complete (if similar story is ✅ COMPLETE)
        """
        # Format options based on similar story status
        top_match = similar[0]

        if top_match.status == "✅ COMPLETE":
            return f"""I'm checking if this already exists...

Found: {top_match.id} ({top_match.title}) is already COMPLETE! ✅

This feature may already be implemented. I recommend:
A) Test the existing feature to verify it works
B) Create a new user story if this is different

Which would you prefer? (A/B)"""

        elif top_match.status in ["🔄 In Progress", "📝 PLANNED"]:
            return f"""I'm checking if this already exists...

Found: {top_match.id} ({top_match.title}) - Status: {top_match.status}

I see two options:
A) Enhance {top_match.id} to include your requirements (already {self._estimate_completion(top_match)}% done)
B) Create new user story (separate feature)

Which approach would you prefer? (A/B)"""

        else:
            # Unknown status, default to create new
            return self._proceed_with_extraction(description, session_id)

    def handle_dod_inference(
        self,
        session_id: str,
        user_choice: str
    ) -> str:
        """
        Handle DoD inference after user validates user story draft.

        Workflow:
        1. Ask user if they have DoD in mind
        2. If no → infer DoD using AI
        3. Present inferred DoD for validation
        4. User validates or modifies
        5. Add to ROADMAP with validated DoD
        """
        draft = self.draft_manager.get_draft(session_id)

        if user_choice.lower() in ["infer", "infer it", "generate", "no"]:
            # Infer DoD using AI
            dod = self.dod_service.infer_dod(draft)

            # Store in draft
            draft.dod_criteria = dod.criteria
            self.draft_manager.update_draft(session_id, draft)

            # Present for validation
            return self._format_dod_for_review(dod)

        elif user_choice.startswith("DoD:"):
            # User provided manual DoD
            manual_dod = user_choice[4:].strip().split("\n")
            draft.dod_criteria = manual_dod
            self.draft_manager.update_draft(session_id, draft)

            return "Great! DoD added. Confirm to add to ROADMAP? (yes/no)"

        else:
            return "Would you like me to infer DoD, or provide your own? (infer / DoD: [criteria])"

    def _format_dod_for_review(self, dod: DoDCriteria) -> str:
        """Format inferred DoD for user review."""
        criteria_text = "\n".join(dod.criteria)

        return f"""I've inferred Definition of Done for this user story:

{criteria_text}

Confidence: {dod.confidence*100:.0f}%

Does this look correct? You can:
- Approve: 'Yes, add it'
- Edit: 'Add criterion: [X]' or 'Remove criterion 3'
- Provide your own: 'DoD: [your criteria]'"""

    def _estimate_completion(self, similar_story: SimilarUserStory) -> int:
        """Estimate % completion of similar story (rough heuristic)."""
        # Simple heuristic based on status
        if "In Progress" in similar_story.status:
            return 50  # Assume 50% done
        elif "PLANNED" in similar_story.status:
            return 0  # Not started
        else:
            return 100  # Complete
```

**Implementation Notes**:
- Similarity check runs BEFORE extraction (prevent duplicate work)
- User always chooses: enhance existing vs. create new
- DoD inference runs AFTER user validates user story structure
- User can provide manual DoD or let AI infer
- DoD validation is separate step (user can modify before adding)

---

## Data Structures

### SimilarUserStory
```python
@dataclass
class SimilarUserStory:
    """Similar user story found in ROADMAP."""
    id: str  # e.g., "US-009"
    title: str
    status: str  # "✅ COMPLETE", "🔄 In Progress", "📝 PLANNED"
    similarity_score: float  # 0.0-1.0
    description: Optional[str] = None
```

### DoDCriteria
```python
@dataclass
class DoDCriteria:
    """Definition of Done criteria."""
    criteria: List[str]  # e.g., ["✅ Feature works", "✅ Tests pass"]
    confidence: float  # 0.0-1.0 (AI confidence)
```

### UserStoryDraft (ENHANCED from US-012)
```python
@dataclass
class UserStoryDraft:
    """User story draft (ENHANCED with DoD field)."""
    id: str
    title: str
    description: str
    as_a: Optional[str] = None
    i_want: Optional[str] = None
    so_that: Optional[str] = None
    estimated_effort: Optional[str] = None
    business_value: Optional[str] = None
    dod_criteria: Optional[List[str]] = None  # NEW - DoD criteria
    status: str = "📝 PLANNED"
    created_at: datetime = None
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/unit/test_similarity_checker.py`

**Test Cases**:
1. `test_find_similar_exact_match()` - 100% similarity for identical description
2. `test_find_similar_partial_match()` - ~70% similarity for related features
3. `test_find_similar_no_match()` - Returns empty list for unrelated
4. `test_extract_keywords()` - Removes stopwords, lowercase
5. `test_calculate_similarity_jaccard()` - Correct Jaccard score
6. `test_parse_user_story_from_roadmap()` - Extracts US-XXX sections

**Test File**: `tests/unit/test_dod_inference_service.py`

**Test Cases**:
1. `test_infer_dod_complete_draft()` - Generates 3-7 criteria
2. `test_infer_dod_minimal_draft()` - Handles sparse input
3. `test_parse_dod_response()` - Parses Claude's response correctly
4. `test_validate_dod_quality_good()` - Accepts specific criteria
5. `test_validate_dod_quality_bad()` - Rejects vague criteria
6. `test_infer_dod_api_error()` - Handles Claude API failure

**Test File**: `tests/unit/test_user_story_command_handler_enhanced.py`

**Test Cases**:
1. `test_handle_command_no_duplicates()` - Proceeds with extraction (US-012 flow)
2. `test_handle_command_duplicate_complete()` - Presents "already complete" option
3. `test_handle_command_duplicate_in_progress()` - Presents enhance/create options
4. `test_present_similarity_options()` - Correct formatting
5. `test_handle_dod_inference_user_provides()` - Uses manual DoD
6. `test_handle_dod_inference_ai_infers()` - Uses AI-inferred DoD
7. `test_format_dod_for_review()` - Readable DoD presentation

### Integration Tests

**Test File**: `tests/integration/test_us_013_workflow.py`

**Test Cases**:
1. `test_us_workflow_with_duplicate_complete()` - User informed feature complete
2. `test_us_workflow_with_duplicate_enhance()` - User chooses to enhance existing
3. `test_us_workflow_with_duplicate_create_new()` - User creates new despite similarity
4. `test_us_workflow_with_dod_inference()` - Full flow: extract → validate → infer DoD → add
5. `test_us_workflow_with_manual_dod()` - User provides DoD manually
6. `test_us_workflow_ai_unavailable()` - Fallback when Claude API down

### Manual Testing

**Scenario 1: Duplicate Detection (Complete)**
```
User: /US I want sound notifications when daemon finishes

PM: I'm checking if this already exists...

Found: US-009 (Sound Notifications) is already COMPLETE! ✅

This feature may already be implemented. I recommend:
A) Test the existing feature to verify it works
B) Create a new user story if this is different

Which would you prefer? (A/B)

User: A

PM: Great! Please test the sound notification feature and let me know if it meets your needs.
```

**Scenario 2: Duplicate Detection (Enhance)**
```
User: /US I want email notifications for daemon events

PM: I'm checking if this already exists...

Found: US-009 (Notification System) - Status: ✅ COMPLETE

I see two options:
A) Enhance US-009 to add email support (already 100% done for sound)
B) Create new US-XXX for email-specific notifications

Which approach would you prefer? (A/B)

User: B

PM: [Proceeds with user story extraction...]
```

**Scenario 3: DoD Inference**
```
User: [User story validated]

PM: Great! Do you have a Definition of Done in mind, or should I infer one? (provide DoD / infer)

User: infer

PM: I've inferred Definition of Done for this user story:

✅ Email notifications sent when daemon completes task
✅ Email includes task name and completion status
✅ User can configure email address in settings
✅ Email delivery confirmed via SMTP logs
✅ Tests verify email sent on task completion

Confidence: 92%

Does this look correct? You can:
- Approve: 'Yes, add it'
- Edit: 'Add criterion: [X]'
- Provide your own: 'DoD: [criteria]'

User: Yes, add it

PM: Excellent! I've added the email notification feature to the ROADMAP as US-025.
```

---

## Rollout Plan

### Phase 1: Similarity Detection (2-3 hours)

**Goal**: Detect similar user stories to prevent duplicates

**Timeline**: Day 1

**Tasks**:
1. Create `SimilarityChecker` class (1 hour)
2. Implement keyword extraction and Jaccard similarity (30 min)
3. Implement ROADMAP parsing for user stories (30 min)
4. Write unit tests for similarity detection (1 hour)

**Success Criteria**:
- Finds exact matches (100% similarity)
- Finds partial matches (>60% similarity)
- Returns empty for unrelated descriptions

### Phase 2: DoD Inference (3-4 hours)

**Goal**: Infer DoD from user story using AI

**Timeline**: Day 1-2

**Tasks**:
1. Create `DoDInferenceService` class (1 hour)
2. Create `.claude/commands/infer-dod.md` prompt (30 min)
3. Implement DoD parsing and validation (1 hour)
4. Write unit tests for DoD inference (1.5 hours)

**Success Criteria**:
- Generates 3-7 testable criteria
- Criteria follow ✅ format
- Confidence score >80% on average

### Phase 3: Workflow Integration (2-3 hours)

**Goal**: Integrate similarity check + DoD inference into /US workflow

**Timeline**: Day 2

**Tasks**:
1. Enhance `UserStoryCommandHandler` with similarity check (1 hour)
2. Add DoD inference step after user story validation (1 hour)
3. Update `UserStoryDraft` to include `dod_criteria` field (30 min)
4. Write integration tests (1 hour)

**Success Criteria**:
- Similarity check runs before extraction
- Options presented when duplicates found
- DoD inference runs after user story validation
- User can approve/edit/reject inferred DoD

### Phase 4: Testing & Polish (1-2 hours)

**Goal**: End-to-end testing and error handling

**Timeline**: Day 2

**Tasks**:
1. Manual testing of all scenarios (1 hour)
2. Improve error messages and user guidance (30 min)
3. Tune similarity threshold (testing with real data) (30 min)

**Success Criteria**:
- All manual test scenarios pass
- Clear user guidance at each step
- Similarity detection >75% accurate

---

## Risks & Mitigations

### Risk 1: False Positive Similarity

**Description**: Keyword matching may flag unrelated stories as similar

**Likelihood**: Medium

**Impact**: Medium (user spends time dismissing false matches)

**Mitigation**:
- Set threshold high enough (0.6) to reduce false positives
- Show similarity score to user (transparent)
- User always has option to ignore and create new
- Future: use embeddings for better semantic matching

### Risk 2: Low DoD Quality

**Description**: AI-inferred DoD may be vague or untestable

**Likelihood**: Medium

**Impact**: Medium (unclear completion criteria)

**Mitigation**:
- Validate DoD quality before presenting (check for actionable verbs)
- Show confidence score to user
- User can always edit or provide manual DoD
- Collect feedback to improve prompt over time

### Risk 3: Performance

**Description**: Similarity check + DoD inference adds latency

**Likelihood**: Low

**Impact**: Low (5-6 seconds total, acceptable)

**Mitigation**:
- Optimize ROADMAP parsing (cache parsed user stories)
- Run similarity check asynchronously if needed
- Set timeout for Claude API calls (3 sec max)

---

## Observability

### Metrics

- `us_013.similarity_check_time` (histogram) - Time to check similarity
- `us_013.similar_found` (counter) - # times similar US found
- `us_013.user_chose_enhance` (counter) - # times user enhanced existing
- `us_013.user_chose_create_new` (counter) - # times user created new despite similarity
- `us_013.dod_inference_time` (histogram) - Time to infer DoD
- `us_013.dod_inference_confidence` (histogram) - AI confidence scores
- `us_013.dod_user_approved` (counter) - # times user approved inferred DoD
- `us_013.dod_user_edited` (counter) - # times user edited inferred DoD
- `us_013.dod_user_manual` (counter) - # times user provided manual DoD

### Logs

- INFO: Similarity check started (description)
- INFO: Similar user stories found (count, top match)
- INFO: User chose option (enhance/create new/test existing)
- INFO: DoD inference started (user story ID)
- INFO: DoD inferred (criteria count, confidence)
- INFO: User approved DoD (user story ID)
- INFO: User edited DoD (changes)
- ERROR: Similarity check failed (error)
- ERROR: DoD inference failed (error)

---

## Documentation

### User Documentation

**Update**: `docs/TUTORIALS.md` - Add section on DoD inference

**Content**:
```markdown
## Definition of Done (DoD)

When creating user stories with `/US`, the PM can infer DoD for you:

1. After validating user story structure, PM asks for DoD
2. Choose "infer" to let AI generate DoD
3. Review inferred criteria
4. Approve, edit, or provide your own

Example:
PM: "Do you have a DoD in mind, or should I infer one?"
You: "infer"
PM: [Shows inferred criteria with confidence score]
You: "Yes, add it" or "Add criterion: [X]"
```

### Developer Documentation

**Update**: `docs/architecture/USER_STORY_COMMAND.md`

**Add Section**:
- Similarity detection algorithm
- DoD inference prompt design
- Integration with US-012 workflow

---

## Security Considerations

1. **ROADMAP Parsing**: Sanitize regex patterns to prevent ReDoS attacks
2. **DoD Injection**: Validate user-provided DoD (no malicious code)
3. **API Rate Limiting**: Respect Claude API limits (existing in AIService)
4. **Data Leakage**: DoD inference doesn't leak sensitive ROADMAP data to Claude

---

## Cost Estimate

**Development**:
- Phase 1: 2-3 hours (similarity detection)
- Phase 2: 3-4 hours (DoD inference)
- Phase 3: 2-3 hours (workflow integration)
- Phase 4: 1-2 hours (testing & polish)
- **Total**: 8-12 hours (~1-1.5 days)

**Infrastructure**:
- Claude API costs: ~$0.02 per user story (extraction + DoD inference)

**Ongoing**:
- Maintenance: 1 hour/month (monitor quality)
- Prompt tuning: 2 hours/quarter (improve DoD quality)

---

## Future Enhancements

Phase 2+ Enhancements (not in scope):
1. Semantic similarity using sentence embeddings (SBERT)
2. Automatic DoD validation against completed user stories
3. DoD template library for common feature types
4. Learning from user edits to improve inference
5. Multi-language DoD support

---

## References

- US-013: PM Infers and Validates DoD for Every User Story (ROADMAP.md line 1279)
- US-012: Natural Language User Story Management (SPEC-012)
- COLLABORATION_METHODOLOGY.md Section 6: DoD template
- Existing AIService: `coffee_maker/cli/ai_service.py`
- Existing RoadmapEditor: `coffee_maker/cli/roadmap_editor.py`

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

**Estimated Implementation Time**: 8-12 hours (1-1.5 days)
