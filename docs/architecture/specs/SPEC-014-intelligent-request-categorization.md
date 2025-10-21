# SPEC-014: Intelligent Request Categorization and Document Routing

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-014 - PM Context Awareness: Auto-Detect Feature vs Methodology Changes

**Related ADRs**: None

**Assigned To**: code_developer

---

## Executive Summary

This specification describes the technical design for automatic request categorization in project_manager. The system will detect whether user input is a feature request, process/methodology change, or both, and route information to the appropriate documents (ROADMAP.md vs COLLABORATION_METHODOLOGY.md). This eliminates manual categorization and ensures information is documented in the correct location.

---

## Problem Statement

### Current Situation

When users communicate with project_manager, their input can be:
- **Feature requests** → Should update `ROADMAP.md`
- **Process/methodology changes** → Should update `COLLABORATION_METHODOLOGY.md`
- **Both** → Should update both documents
- **Questions** → No document update needed

Currently, PM may not correctly identify the input type, leading to:
- Information documented in wrong place
- Methodology changes lost or treated as features
- Features mistakenly documented as process changes
- Manual effort to categorize every request

### Goal

Implement automatic request categorization that:
- Detects request type from natural language input
- Routes to correct document(s) for updates
- Asks clarifying questions when ambiguous
- Provides confidence scores for transparency
- Completes categorization in < 100ms (rule-based, not ML)

### Non-Goals

- NOT implementing document editing (use existing RoadmapEditor, create MethodologyEditor)
- NOT implementing multi-document search (just categorization)
- NOT implementing ML-based classification (rule-based for MVP)
- NOT implementing request prioritization (separate concern)

---

## Requirements

### Functional Requirements

1. **FR-1**: Classify user input into categories: feature, methodology, both, question, other
2. **FR-2**: Extract key indicators (keywords, patterns) for classification
3. **FR-3**: Return confidence score (0.0-1.0) with classification
4. **FR-4**: Ask clarifying questions when confidence < 0.5
5. **FR-5**: Route to RoadmapEditor when feature detected
6. **FR-6**: Route to MethodologyEditor when process change detected
7. **FR-7**: Route to both when mixed request detected
8. **FR-8**: Support override (user can explicitly specify category)

### Non-Functional Requirements

1. **NFR-1**: Classification completes in < 100ms (rule-based, fast)
2. **NFR-2**: Accuracy > 92% for clear feature requests
3. **NFR-3**: Accuracy > 85% for clear methodology changes
4. **NFR-4**: False positive rate < 10% (avoid wrong document)
5. **NFR-5**: Graceful degradation (conservative when uncertain)

### Constraints

- Must use rule-based classification (keywords + patterns, no ML)
- Must integrate with existing ChatInterface
- Must support both API mode and CLI mode
- Must follow COLLABORATION_METHODOLOGY.md Section 3.2.1 (request categorization)
- Must be explainable (user can see why classification was made)

---

## Proposed Solution

### High-Level Approach

Implement a rule-based classifier that:
1. Extracts keywords and patterns from user input
2. Matches against predefined dictionaries (feature keywords vs methodology keywords)
3. Calculates confidence based on keyword density and patterns
4. Returns category with confidence score
5. Asks clarifying questions when ambiguous (confidence < 0.5)

Use a `RequestClassifier` class with keyword dictionaries and pattern matchers. Integrate with `DocumentRouter` to route to appropriate editor (RoadmapEditor or MethodologyEditor).

### Architecture Diagram

```
┌─────────────────┐
│  User (Chat)    │
└────────┬────────┘
         │
         │ "I want users to review PRs before merging"
         v
┌───────────────────────────────────────────────┐
│  ChatInterface                                │
│  (project_manager)                            │
└────────┬──────────────────────────────────────┘
         │
         │ Classify request
         v
┌───────────────────────────────────────────────┐
│  RequestClassifier (NEW)                      │
│  .classify(user_input)                        │
└────────┬──────────────────────────────────────┘
         │
         │ Returns RequestCategory
         v
┌───────────────────────────────────────────────┐
│  DocumentRouter (NEW)                         │
│  .route(category, input)                      │
└────────┬──────────────────────────────────────┘
         │
         ├─ If category=FEATURE ────────────────┐
         │                                       v
         │                          ┌─────────────────────┐
         │                          │  RoadmapEditor      │
         │                          │  .add_user_story()  │
         │                          └─────────────────────┘
         │
         ├─ If category=METHODOLOGY ────────────┐
         │                                       v
         │                          ┌─────────────────────┐
         │                          │  MethodologyEditor  │
         │                          │  .add_process()     │
         │                          └─────────────────────┘
         │
         └─ If category=BOTH ───────────────────┐
                                                 v
                                    ┌─────────────────────┐
                                    │  Update both docs   │
                                    └─────────────────────┘
```

### Technology Stack

- **Classification**: Rule-based (keyword dictionaries + regex patterns)
- **Document Routing**: New `DocumentRouter` class
- **ROADMAP Updates**: Existing `RoadmapEditor`
- **Methodology Updates**: New `MethodologyEditor` (similar to RoadmapEditor)
- **Keywords**: Configurable dictionaries in YAML or JSON

---

## Detailed Design

### Component 1: RequestClassifier

**Responsibility**: Classify user requests into categories using rule-based approach

**Interface**:
```python
@dataclass
class RequestCategory:
    """Classification result with confidence."""
    category: str  # "feature", "methodology", "both", "question", "other"
    confidence: float  # 0.0-1.0
    indicators: List[str]  # Keywords/patterns that triggered classification
    explanation: str  # Human-readable explanation


class RequestClassifier:
    """
    Rule-based classifier for user requests.

    Uses keyword dictionaries and pattern matching to categorize requests
    as feature requests, methodology changes, or both.

    Target Accuracy (from US-014):
    - Feature detection: >92%
    - Methodology detection: >85%
    - Process detection: >88%
    - Mixed detection: >80%
    """

    # Keyword dictionaries
    FEATURE_KEYWORDS = {
        # User-facing features
        "add", "create", "build", "implement", "feature", "functionality",
        "support", "enable", "allow", "user", "dashboard", "ui", "interface",
        "notification", "email", "slack", "integration", "api", "endpoint",

        # Technical features
        "database", "cache", "storage", "authentication", "authorization",
        "logging", "monitoring", "metrics", "performance", "optimization"
    }

    METHODOLOGY_KEYWORDS = {
        # Process keywords
        "process", "workflow", "methodology", "procedure", "guideline",
        "policy", "rule", "standard", "convention", "practice",

        # Team collaboration
        "review", "approval", "collaboration", "communication", "meeting",
        "standup", "retrospective", "planning", "estimation",

        # Documentation
        "document", "documentation", "guide", "tutorial", "README",
        "onboarding", "training"
    }

    QUESTION_KEYWORDS = {
        # Question indicators
        "what", "how", "why", "when", "where", "who", "which",
        "can you", "could you", "would you", "should I", "is it",
        "does it", "explain", "clarify", "help me understand"
    }

    # Patterns for advanced detection
    FEATURE_PATTERNS = [
        r"I want (users? to|to|a|an) .+",  # "I want users to..."
        r"add support for .+",
        r"build a .+ (feature|system|component)",
        r"implement .+ functionality",
    ]

    METHODOLOGY_PATTERNS = [
        r"(we|let's|should we) (review|approve|check) .+",
        r"change (the|our) (process|workflow|methodology) .+",
        r"update (the|our) (guideline|policy|procedure) .+",
        r"require .+ (review|approval|sign-off)",
    ]

    def __init__(self):
        """Initialize classifier with keyword dictionaries."""
        pass

    def classify(self, user_input: str) -> RequestCategory:
        """
        Classify user request into category.

        Args:
            user_input: Natural language input from user

        Returns:
            RequestCategory with category, confidence, and explanation

        Example:
            >>> classifier.classify("I want users to review PRs before merging")
            RequestCategory(
                category="methodology",
                confidence=0.88,
                indicators=["users", "review", "approval pattern"],
                explanation="Detected methodology change based on keywords:
                            'users', 'review' and pattern 'require review'"
            )
        """
        # 1. Extract keywords
        feature_keywords = self._extract_keywords(user_input, self.FEATURE_KEYWORDS)
        methodology_keywords = self._extract_keywords(user_input, self.METHODOLOGY_KEYWORDS)
        question_keywords = self._extract_keywords(user_input, self.QUESTION_KEYWORDS)

        # 2. Check patterns
        feature_patterns = self._match_patterns(user_input, self.FEATURE_PATTERNS)
        methodology_patterns = self._match_patterns(user_input, self.METHODOLOGY_PATTERNS)

        # 3. Calculate scores
        feature_score = self._calculate_score(feature_keywords, feature_patterns)
        methodology_score = self._calculate_score(methodology_keywords, methodology_patterns)
        question_score = len(question_keywords) / 3.0  # Normalize

        # 4. Determine category
        return self._determine_category(
            feature_score,
            methodology_score,
            question_score,
            feature_keywords,
            methodology_keywords,
            question_keywords,
            feature_patterns,
            methodology_patterns
        )

    def _extract_keywords(
        self,
        text: str,
        keyword_set: Set[str]
    ) -> List[str]:
        """Extract matching keywords from text."""
        # Lowercase, tokenize, find matches
        words = text.lower().split()
        return [word for word in words if word in keyword_set]

    def _match_patterns(
        self,
        text: str,
        patterns: List[str]
    ) -> List[str]:
        """Match regex patterns in text."""
        matched = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matched.append(pattern)
        return matched

    def _calculate_score(
        self,
        keywords: List[str],
        patterns: List[str]
    ) -> float:
        """
        Calculate confidence score.

        Score = (keyword_count * 0.2) + (pattern_count * 0.3)
        Max score: 1.0
        """
        keyword_score = min(len(keywords) * 0.2, 0.6)  # Max 0.6 from keywords
        pattern_score = min(len(patterns) * 0.3, 0.4)  # Max 0.4 from patterns
        return min(keyword_score + pattern_score, 1.0)

    def _determine_category(
        self,
        feature_score: float,
        methodology_score: float,
        question_score: float,
        feature_keywords: List[str],
        methodology_keywords: List[str],
        question_keywords: List[str],
        feature_patterns: List[str],
        methodology_patterns: List[str]
    ) -> RequestCategory:
        """
        Determine final category based on scores.

        Logic:
        - If question_score > 0.5: category = "question"
        - If feature_score > 0.8 AND methodology_score > 0.8: category = "both"
        - If feature_score > methodology_score AND > 0.5: category = "feature"
        - If methodology_score > feature_score AND > 0.5: category = "methodology"
        - Else: category = "other" (ambiguous, ask user)
        """
        # Question detection (highest priority)
        if question_score > 0.5:
            return RequestCategory(
                category="question",
                confidence=question_score,
                indicators=question_keywords,
                explanation=f"Detected question based on keywords: {', '.join(question_keywords)}"
            )

        # Both detection
        if feature_score > 0.5 and methodology_score > 0.5:
            confidence = (feature_score + methodology_score) / 2
            return RequestCategory(
                category="both",
                confidence=confidence,
                indicators=feature_keywords + methodology_keywords,
                explanation=f"Detected both feature and methodology changes. "
                           f"Feature indicators: {', '.join(feature_keywords)}. "
                           f"Methodology indicators: {', '.join(methodology_keywords)}."
            )

        # Feature detection
        if feature_score > methodology_score and feature_score > 0.5:
            return RequestCategory(
                category="feature",
                confidence=feature_score,
                indicators=feature_keywords + feature_patterns,
                explanation=f"Detected feature request based on: {', '.join(feature_keywords)}"
            )

        # Methodology detection
        if methodology_score > feature_score and methodology_score > 0.5:
            return RequestCategory(
                category="methodology",
                confidence=methodology_score,
                indicators=methodology_keywords + methodology_patterns,
                explanation=f"Detected methodology change based on: {', '.join(methodology_keywords)}"
            )

        # Ambiguous (ask user)
        return RequestCategory(
            category="other",
            confidence=max(feature_score, methodology_score),
            indicators=[],
            explanation="Ambiguous input. Please clarify if this is a feature request or process change."
        )
```

**Implementation Notes**:
- Rule-based (no ML dependencies, fast, explainable)
- Keyword dictionaries tuned via testing
- Pattern matching with regex for complex cases
- Confidence thresholds: >0.8 (high), 0.5-0.8 (medium), <0.5 (ask user)
- Explainable: returns keywords/patterns that triggered classification

### Component 2: DocumentRouter

**Responsibility**: Route classified requests to appropriate document editor

**Interface**:
```python
class DocumentRouter:
    """
    Routes classified requests to appropriate document editors.

    Routes:
    - feature → RoadmapEditor
    - methodology → MethodologyEditor
    - both → Both editors
    - question → No routing (respond directly)
    - other → Ask user for clarification
    """

    def __init__(
        self,
        roadmap_editor: RoadmapEditor,
        methodology_editor: MethodologyEditor,
        ai_service: AIService
    ):
        """Initialize with document editors."""
        self.roadmap_editor = roadmap_editor
        self.methodology_editor = methodology_editor
        self.ai_service = ai_service

    def route(
        self,
        category: RequestCategory,
        user_input: str
    ) -> str:
        """
        Route request to appropriate document editor.

        Args:
            category: Classification result
            user_input: Original user input

        Returns:
            Response message to user

        Example:
            >>> router.route(category, "Add email notifications")
            "I've categorized this as a feature request and added it to ROADMAP.md."
        """
        if category.category == "feature":
            return self._route_to_roadmap(user_input, category)

        elif category.category == "methodology":
            return self._route_to_methodology(user_input, category)

        elif category.category == "both":
            return self._route_to_both(user_input, category)

        elif category.category == "question":
            return self._handle_question(user_input)

        else:  # "other" - ambiguous
            return self._ask_clarification(category)

    def _route_to_roadmap(
        self,
        user_input: str,
        category: RequestCategory
    ) -> str:
        """Route feature request to ROADMAP.md."""
        # Use /US command flow (US-012) to extract user story
        # Add to ROADMAP via RoadmapEditor
        return f"I've categorized this as a feature request (confidence: {category.confidence*100:.0f}%).\n\n" \
               f"Indicators: {', '.join(category.indicators)}\n\n" \
               f"Would you like me to create a user story for this? (/US)"

    def _route_to_methodology(
        self,
        user_input: str,
        category: RequestCategory
    ) -> str:
        """Route methodology change to COLLABORATION_METHODOLOGY.md."""
        # Extract process description
        # Add to COLLABORATION_METHODOLOGY via MethodologyEditor
        return f"I've categorized this as a methodology change (confidence: {category.confidence*100:.0f}%).\n\n" \
               f"Indicators: {', '.join(category.indicators)}\n\n" \
               f"I'll update COLLABORATION_METHODOLOGY.md with this process change."

    def _route_to_both(
        self,
        user_input: str,
        category: RequestCategory
    ) -> str:
        """Route mixed request to both documents."""
        return f"I've detected both a feature and methodology change (confidence: {category.confidence*100:.0f}%).\n\n" \
               f"I'll update:\n" \
               f"- ROADMAP.md (feature request)\n" \
               f"- COLLABORATION_METHODOLOGY.md (process change)\n\n" \
               f"Does this sound correct?"

    def _handle_question(self, user_input: str) -> str:
        """Handle question (no document update)."""
        # Use AI to answer question
        return self.ai_service.process_request(user_input, context={}, history=[])

    def _ask_clarification(self, category: RequestCategory) -> str:
        """Ask user to clarify ambiguous request."""
        return f"I'm not sure if this is a feature request or methodology change (confidence: {category.confidence*100:.0f}%).\n\n" \
               f"Could you clarify:\n" \
               f"A) This is a feature request (add to ROADMAP)\n" \
               f"B) This is a process/methodology change (add to COLLABORATION_METHODOLOGY)\n" \
               f"C) This is both\n\n" \
               f"Which is it? (A/B/C)"
```

**Implementation Notes**:
- Routes based on category from RequestClassifier
- Shows confidence score and indicators to user (transparent)
- Asks for confirmation when confidence < 0.8
- Handles ambiguous cases by asking clarifying questions

### Component 3: MethodologyEditor (NEW)

**Responsibility**: Safe editing of COLLABORATION_METHODOLOGY.md (similar to RoadmapEditor)

**Interface**:
```python
class MethodologyEditor:
    """
    Safe editor for COLLABORATION_METHODOLOGY.md.

    Similar to RoadmapEditor, provides:
    - Atomic writes with backups
    - Section updates (add process, update workflow)
    - Validation
    """

    def __init__(self, methodology_path: Path):
        """Initialize with COLLABORATION_METHODOLOGY.md path."""
        self.methodology_path = Path(methodology_path)
        self.backup_dir = self.methodology_path.parent / "methodology_backups"
        self.backup_dir.mkdir(exist_ok=True)

    def add_process(
        self,
        section: str,
        process_name: str,
        description: str,
        steps: List[str]
    ) -> bool:
        """
        Add new process to COLLABORATION_METHODOLOGY.md.

        Args:
            section: Section name (e.g., "## 3. Development Workflow")
            process_name: Process name (e.g., "PR Review Process")
            description: Process description
            steps: List of process steps

        Returns:
            True if successful

        Example:
            >>> editor.add_process(
            ...     section="## 3. Development Workflow",
            ...     process_name="PR Review Process",
            ...     description="All PRs require review before merging",
            ...     steps=["1. Create PR", "2. Request review", "3. Merge after approval"]
            ... )
            True
        """
        pass

    def update_section(
        self,
        section_name: str,
        new_content: str
    ) -> bool:
        """Update existing section in COLLABORATION_METHODOLOGY.md."""
        pass

    def _create_backup(self) -> None:
        """Create timestamped backup of COLLABORATION_METHODOLOGY.md."""
        pass

    def _atomic_write(self, content: str) -> None:
        """Atomically write content to file."""
        pass
```

**Implementation Notes**:
- Similar architecture to RoadmapEditor (backups, atomic writes)
- Supports section-based updates (markdown heading detection)
- Validates section names before updates
- Creates backups before every write

---

## Data Structures

### RequestCategory
```python
@dataclass
class RequestCategory:
    """Classification result."""
    category: str  # "feature", "methodology", "both", "question", "other"
    confidence: float  # 0.0-1.0
    indicators: List[str]  # Keywords/patterns that matched
    explanation: str  # Human-readable explanation
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/unit/test_request_classifier.py`

**Test Cases**:
1. `test_classify_clear_feature()` - "Add email notifications" → feature (>0.9 confidence)
2. `test_classify_clear_methodology()` - "Require PR reviews" → methodology (>0.85 confidence)
3. `test_classify_question()` - "How do I..." → question (>0.8 confidence)
4. `test_classify_both()` - Mixed indicators → both (>0.8 confidence)
5. `test_classify_ambiguous()` - Unclear → other (<0.5 confidence)
6. `test_extract_keywords()` - Correct keyword extraction
7. `test_match_patterns()` - Regex patterns match correctly
8. `test_calculate_score()` - Score calculation accurate
9. `test_feature_accuracy_target_92()` - Accuracy >92% on test set
10. `test_methodology_accuracy_target_85()` - Accuracy >85% on test set

**Test File**: `tests/unit/test_document_router.py`

**Test Cases**:
1. `test_route_feature()` - Routes to RoadmapEditor
2. `test_route_methodology()` - Routes to MethodologyEditor
3. `test_route_both()` - Routes to both editors
4. `test_route_question()` - Handles question directly
5. `test_route_ambiguous()` - Asks clarifying question
6. `test_ask_clarification()` - Correct clarification message

**Test File**: `tests/unit/test_methodology_editor.py`

**Test Cases**:
1. `test_add_process()` - Adds process to section
2. `test_update_section()` - Updates existing section
3. `test_create_backup()` - Backup created before write
4. `test_atomic_write()` - Atomic write succeeds

### Integration Tests

**Test File**: `tests/integration/test_us_014_workflow.py`

**Test Cases**:
1. `test_feature_request_end_to_end()` - Feature classified → added to ROADMAP
2. `test_methodology_request_end_to_end()` - Methodology classified → added to COLLABORATION_METHODOLOGY
3. `test_both_request_end_to_end()` - Both classified → added to both docs
4. `test_ambiguous_request_clarification()` - User clarifies → routed correctly
5. `test_classification_accuracy_on_real_data()` - >90% accuracy on 100 real examples

### Manual Testing

**Scenario 1: Feature Request**
```
User: Add email notifications when daemon finishes tasks

PM: I've categorized this as a feature request (confidence: 94%).

Indicators: add, email, notifications, daemon

Would you like me to create a user story for this? (/US)

User: Yes

PM: [Proceeds with /US workflow from US-012]
```

**Scenario 2: Methodology Change**
```
User: We should require code reviews before merging PRs

PM: I've categorized this as a methodology change (confidence: 88%).

Indicators: require, reviews, process pattern

I'll update COLLABORATION_METHODOLOGY.md with this process change.

[Updates Section 3: Development Workflow with PR review requirement]

Done! Added "PR Review Process" to COLLABORATION_METHODOLOGY.md.
```

**Scenario 3: Both**
```
User: Add a dashboard for monitoring agent activity and require PM approval before deploying new agents

PM: I've detected both a feature and methodology change (confidence: 86%).

I'll update:
- ROADMAP.md (dashboard feature)
- COLLABORATION_METHODOLOGY.md (approval process)

Does this sound correct?

User: Yes

PM: [Updates both documents]
```

**Scenario 4: Ambiguous**
```
User: Improve the system

PM: I'm not sure if this is a feature request or methodology change (confidence: 32%).

Could you clarify:
A) This is a feature request (add to ROADMAP)
B) This is a process/methodology change (add to COLLABORATION_METHODOLOGY)
C) This is both

Which is it? (A/B/C)

User: A

PM: Thanks! I've categorized this as a feature request.
    [Proceeds with /US workflow]
```

---

## Rollout Plan

### Phase 1: Request Classifier (3-4 hours)

**Goal**: Implement rule-based classifier

**Timeline**: Day 1

**Tasks**:
1. Create `RequestClassifier` class (1.5 hours)
2. Define keyword dictionaries (feature, methodology, question) (1 hour)
3. Implement pattern matching for complex cases (1 hour)
4. Write unit tests for classifier (1 hour)

**Success Criteria**:
- Feature detection >92% accurate
- Methodology detection >85% accurate
- Classification completes in <100ms

### Phase 2: Document Router (2-3 hours)

**Goal**: Implement routing logic

**Timeline**: Day 1

**Tasks**:
1. Create `DocumentRouter` class (1 hour)
2. Implement routing for each category (1 hour)
3. Write unit tests for router (1 hour)

**Success Criteria**:
- Routes feature → ROADMAP
- Routes methodology → COLLABORATION_METHODOLOGY
- Routes both → both documents
- Asks clarification when ambiguous

### Phase 3: Methodology Editor (3-4 hours)

**Goal**: Implement safe COLLABORATION_METHODOLOGY.md editor

**Timeline**: Day 2

**Tasks**:
1. Create `MethodologyEditor` class (1.5 hours)
2. Implement `add_process()` and `update_section()` (1.5 hours)
3. Implement backup and atomic write (1 hour)
4. Write unit tests for editor (1 hour)

**Success Criteria**:
- Adds processes to sections
- Creates backups before write
- Atomic write ensures consistency

### Phase 4: ChatInterface Integration (1-2 hours)

**Goal**: Integrate classifier + router into project_manager chat

**Timeline**: Day 2

**Tasks**:
1. Add classification step before request processing (30 min)
2. Route classified requests to appropriate handler (30 min)
3. Show classification explanation to user (30 min)
4. Write integration tests (1 hour)

**Success Criteria**:
- All requests classified before processing
- User sees classification explanation
- Correct routing to document editors

### Phase 5: Testing & Polish (2-3 hours)

**Goal**: End-to-end testing and accuracy tuning

**Timeline**: Day 2-3

**Tasks**:
1. Manual testing of all scenarios (1 hour)
2. Collect 100 real request examples (30 min)
3. Tune keyword dictionaries and thresholds (1 hour)
4. Improve user-facing messages (30 min)

**Success Criteria**:
- All manual test scenarios pass
- Accuracy >90% on real examples
- Clear, helpful messages to user

---

## Risks & Mitigations

### Risk 1: Keyword-Based Limitations

**Description**: Simple keyword matching may miss semantic meaning

**Likelihood**: Medium

**Impact**: Medium (some misclassifications)

**Mitigation**:
- Use patterns in addition to keywords (catches complex cases)
- Show confidence score to user (transparency)
- Ask clarification when uncertain (confidence < 0.5)
- Collect feedback to improve keywords over time
- Future: use embeddings for semantic similarity

### Risk 2: Ambiguous Requests

**Description**: Some requests genuinely ambiguous (both feature + methodology)

**Likelihood**: Medium

**Impact**: Low (user clarifies)

**Mitigation**:
- Detect "both" category explicitly
- Ask user to confirm when detected
- Provide clear options (A/B/C choice)
- Log ambiguous cases for analysis

### Risk 3: Performance

**Description**: Classification may add latency

**Likelihood**: Low

**Impact**: Low (<100ms, acceptable)

**Mitigation**:
- Use rule-based approach (fast, no ML)
- Optimize keyword matching (sets, not lists)
- Cache compiled regex patterns
- Set performance test: <100ms target

---

## Observability

### Metrics

- `us_014.classification_time` (histogram) - Time to classify
- `us_014.feature_detected` (counter) - # feature requests
- `us_014.methodology_detected` (counter) - # methodology changes
- `us_014.both_detected` (counter) - # mixed requests
- `us_014.question_detected` (counter) - # questions
- `us_014.ambiguous_detected` (counter) - # ambiguous requests
- `us_014.confidence_score` (histogram) - Distribution of confidence scores
- `us_014.accuracy` (gauge) - Classification accuracy (from feedback)

### Logs

- INFO: Request classified (category, confidence, indicators)
- INFO: Routed to ROADMAP (feature request)
- INFO: Routed to COLLABORATION_METHODOLOGY (methodology change)
- INFO: Routed to both (mixed request)
- INFO: Asked clarification (ambiguous)
- WARN: Classification low confidence (<0.5)
- ERROR: Classification failed (exception)

---

## Documentation

### User Documentation

**Update**: `docs/TUTORIALS.md` - Add section on automatic categorization

**Content**:
```markdown
## Automatic Request Categorization

The project manager automatically detects whether your input is:
- Feature request → adds to ROADMAP
- Methodology change → adds to COLLABORATION_METHODOLOGY
- Both → updates both documents

You'll see the classification with confidence score and can confirm or override.
```

### Developer Documentation

**Create**: `docs/architecture/REQUEST_CLASSIFICATION.md`

**Content**:
- Classifier algorithm (keywords + patterns)
- Keyword dictionaries
- Confidence score calculation
- Accuracy metrics and tuning
- How to extend with new categories

---

## Security Considerations

1. **Input Validation**: Sanitize user input before regex matching (prevent ReDoS)
2. **Document Integrity**: Use atomic writes with backups (MethodologyEditor)
3. **Access Control**: Only project_manager can update COLLABORATION_METHODOLOGY
4. **Audit Trail**: Log all document updates for traceability

---

## Cost Estimate

**Development**:
- Phase 1: 3-4 hours (request classifier)
- Phase 2: 2-3 hours (document router)
- Phase 3: 3-4 hours (methodology editor)
- Phase 4: 1-2 hours (ChatInterface integration)
- Phase 5: 2-3 hours (testing & polish)
- **Total**: 11-16 hours (~1.5-2 days)

**Infrastructure**:
- No additional costs (rule-based, no API calls)

**Ongoing**:
- Maintenance: 1 hour/month (keyword tuning)
- Accuracy monitoring: 1 hour/quarter

---

## Future Enhancements

Phase 2+ Enhancements (not in scope):
1. Semantic classification using embeddings (SBERT)
2. Multi-label classification (e.g., feature + bug + methodology)
3. Priority detection (urgent, high, medium, low)
4. Automatic sub-categorization (bug, enhancement, refactoring)
5. Learning from user corrections (feedback loop)

---

## References

- US-014: Intelligent Request Categorization and Document Routing (ROADMAP.md line 1454)
- COLLABORATION_METHODOLOGY.md Section 3.2.1: Request categorization rules
- Existing RoadmapEditor: `coffee_maker/cli/roadmap_editor.py`
- Existing ChatInterface: `coffee_maker/cli/chat_interface.py`

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

**Estimated Implementation Time**: 11-16 hours (1.5-2 days)
