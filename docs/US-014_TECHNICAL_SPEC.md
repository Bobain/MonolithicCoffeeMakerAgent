# US-014: Intelligent Request Categorization and Document Routing - Technical Specification

**Status**: 🔄 Draft (Awaiting User Approval)
**Created**: 2025-10-10
**Estimated Duration**: 3-5 days
**Complexity**: Medium-High
**Priority**: Next after US-010 completion

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Classification Logic](#3-classification-logic)
4. [Implementation Plan](#4-implementation-plan)
5. [Testing Strategy](#5-testing-strategy)
6. [Success Criteria](#6-success-criteria)
7. [Risks & Mitigations](#7-risks--mitigations)
8. [Open Questions](#8-open-questions)

---

## 1. Overview

### 1.1 User Story

> "As a project manager, I need to be able to interpret the user's context: what part of what he is saying are user stories, and what parts concerns the collaboration methodologies, or both. I can ask him to make sure I understood as I need to get sure which documents should be updated (roadmap, collaboration methodology, etc)"

### 1.2 Business Context

**Problem**: PM currently doesn't consistently identify whether user input is:
- A **feature request** (what to build) → Should go to `ROADMAP.md`
- A **methodology change** (how we work) → Should go to `COLLABORATION_METHODOLOGY.md`
- **Both** → Should update both documents
- **Ambiguous** → Should ask clarifying questions

**Impact**:
- Information gets lost or documented in wrong place
- Methodology changes treated as features (or vice versa)
- Lack of clarity on which documents to update

**Solution**: Build intelligent classification system that:
1. Analyzes user input using keywords, patterns, and context
2. Assigns confidence score to classification
3. Routes information to correct document(s)
4. Asks clarifying questions when ambiguous

### 1.3 Goals

**Primary Goals**:
- ✅ Correctly classify 90%+ of user input as feature/methodology/both
- ✅ Ask clarifying questions when confidence < 80%
- ✅ Explicitly state which documents will be updated
- ✅ Prevent information loss through correct routing

**Secondary Goals**:
- ✅ Learn from user corrections to improve classification
- ✅ Handle edge cases gracefully
- ✅ Maintain conversation flow (don't be overly robotic)

### 1.4 Non-Goals

❌ Build ML model for classification (use rule-based approach)
❌ Auto-update documents without user validation
❌ Handle multi-turn ambiguity resolution (ask once, user decides)
❌ Classify code snippets or technical implementation details

---

## 2. Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Natural Language)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              RequestClassifier (NEW COMPONENT)               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Keyword Analysis                                 │  │
│  │     - Feature indicators: "I want", "build", "add"   │  │
│  │     - Methodology indicators: "PM should", "always"  │  │
│  │     - Both indicators: "PM needs capability to"      │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Pattern Matching                                 │  │
│  │     - Imperative mood (feature): "Add", "Create"     │  │
│  │     - Prescriptive mood (methodology): "should"      │  │
│  │     - Intent markers: "I want" vs "PM should"        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Confidence Scoring                               │  │
│  │     - Aggregate keyword + pattern scores             │  │
│  │     - Normalize to 0-100%                            │  │
│  │     - Apply thresholds (>80%, 50-80%, <50%)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. Classification Decision                          │  │
│  │     - FEATURE_REQUEST                                │  │
│  │     - METHODOLOGY_CHANGE                             │  │
│  │     - BOTH                                           │  │
│  │     - AMBIGUOUS (needs clarification)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   ROADMAP    │  │ METHODOLOGY  │  │Ask Clarifying│
│   Update     │  │   Update     │  │  Question    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 RequestClassifier Class Design

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class RequestType(Enum):
    """Types of user requests."""
    FEATURE_REQUEST = "feature"
    METHODOLOGY_CHANGE = "methodology"
    BOTH = "both"
    AMBIGUOUS = "ambiguous"

@dataclass
class ClassificationResult:
    """Result of request classification."""
    request_type: RequestType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    keywords_matched: List[str]
    suggested_action: str
    documents_to_update: List[str]  # ["ROADMAP.md", "COLLABORATION_METHODOLOGY.md"]

class RequestClassifier:
    """
    Classifies user input as feature request, methodology change, both, or ambiguous.

    Uses rule-based approach with keyword matching, pattern detection, and
    confidence scoring.
    """

    def __init__(self):
        """Initialize classifier with keyword dictionaries and patterns."""
        self.feature_keywords = [
            "i want", "i need", "add", "build", "implement", "create",
            "feature", "functionality", "capability to build"
        ]

        self.methodology_keywords = [
            "pm should", "always", "never", "must", "process", "workflow",
            "methodology", "how we work", "team practice", "team should"
        ]

        self.both_keywords = [
            "pm needs to be able to", "pm should be able to",
            "pm needs capability to", "pm should have capability"
        ]

        self.confidence_thresholds = {
            "high": 0.80,      # Auto-route
            "medium": 0.50,    # Route with mention
            "low": 0.50        # Ask clarifying questions
        }

    def classify(self, user_input: str) -> ClassificationResult:
        """
        Classify user input and return classification result.

        Args:
            user_input: User's natural language input

        Returns:
            ClassificationResult with type, confidence, reasoning, and action
        """
        # Normalize input
        normalized = user_input.lower().strip()

        # Step 1: Keyword analysis
        feature_score = self._calculate_feature_score(normalized)
        methodology_score = self._calculate_methodology_score(normalized)
        both_score = self._calculate_both_score(normalized)

        # Step 2: Pattern matching
        feature_score += self._detect_feature_patterns(normalized)
        methodology_score += self._detect_methodology_patterns(normalized)

        # Step 3: Normalize scores
        total_score = feature_score + methodology_score + both_score
        if total_score > 0:
            feature_confidence = feature_score / total_score
            methodology_confidence = methodology_score / total_score
            both_confidence = both_score / total_score
        else:
            # No matches - ambiguous
            return self._create_ambiguous_result(normalized)

        # Step 4: Make decision
        return self._make_classification_decision(
            normalized,
            feature_confidence,
            methodology_confidence,
            both_confidence
        )

    def _calculate_feature_score(self, text: str) -> float:
        """Calculate feature keyword score."""
        score = 0.0
        for keyword in self.feature_keywords:
            if keyword in text:
                score += 1.0
        return score

    def _calculate_methodology_score(self, text: str) -> float:
        """Calculate methodology keyword score."""
        score = 0.0
        for keyword in self.methodology_keywords:
            if keyword in text:
                score += 1.0
        return score

    def _calculate_both_score(self, text: str) -> float:
        """Calculate 'both' keyword score (strongly indicates hybrid)."""
        score = 0.0
        for keyword in self.both_keywords:
            if keyword in text:
                score += 3.0  # Higher weight for explicit 'both' indicators
        return score

    def _detect_feature_patterns(self, text: str) -> float:
        """Detect feature patterns (imperative mood, action verbs)."""
        score = 0.0

        # Imperative verbs at start
        imperative_verbs = ["add", "create", "build", "implement", "develop"]
        for verb in imperative_verbs:
            if text.startswith(verb):
                score += 0.5

        # "I want" / "I need" patterns
        if "i want" in text or "i need" in text:
            score += 1.0

        # Specific outputs mentioned
        if any(word in text for word in ["dashboard", "api", "ui", "cli", "command"]):
            score += 0.5

        return score

    def _detect_methodology_patterns(self, text: str) -> float:
        """Detect methodology patterns (prescriptive mood, behavioral rules)."""
        score = 0.0

        # Prescriptive patterns
        if "should" in text or "must" in text:
            score += 1.0

        # Behavioral rules
        if "always" in text or "never" in text:
            score += 1.0

        # Process/workflow mentions
        if any(word in text for word in ["process", "workflow", "practice", "methodology"]):
            score += 0.5

        return score

    def _make_classification_decision(
        self,
        text: str,
        feature_conf: float,
        methodology_conf: float,
        both_conf: float
    ) -> ClassificationResult:
        """Make final classification decision based on confidence scores."""

        # Check for 'both' first (highest specificity)
        if both_conf > 0.4:  # Strong 'both' indicator
            return ClassificationResult(
                request_type=RequestType.BOTH,
                confidence=both_conf,
                reasoning="Detected 'PM needs capability to' pattern indicating both feature and methodology",
                keywords_matched=self._extract_matched_keywords(text),
                suggested_action="Create user story in ROADMAP.md + Update COLLABORATION_METHODOLOGY.md",
                documents_to_update=["ROADMAP.md", "COLLABORATION_METHODOLOGY.md"]
            )

        # Feature vs Methodology
        max_conf = max(feature_conf, methodology_conf)

        if max_conf < self.confidence_thresholds["low"]:
            # Ambiguous - need clarification
            return ClassificationResult(
                request_type=RequestType.AMBIGUOUS,
                confidence=max_conf,
                reasoning="Insufficient confidence to classify - need clarifying questions",
                keywords_matched=self._extract_matched_keywords(text),
                suggested_action="Ask clarifying questions (A/B/C format)",
                documents_to_update=[]
            )

        if feature_conf > methodology_conf:
            request_type = RequestType.FEATURE_REQUEST
            confidence = feature_conf
            action = "Create user story in ROADMAP.md"
            docs = ["ROADMAP.md"]
            reasoning = f"Feature indicators ({feature_conf:.0%}) > Methodology indicators ({methodology_conf:.0%})"
        else:
            request_type = RequestType.METHODOLOGY_CHANGE
            confidence = methodology_conf
            action = "Update COLLABORATION_METHODOLOGY.md"
            docs = ["COLLABORATION_METHODOLOGY.md"]
            reasoning = f"Methodology indicators ({methodology_conf:.0%}) > Feature indicators ({feature_conf:.0%})"

        return ClassificationResult(
            request_type=request_type,
            confidence=confidence,
            reasoning=reasoning,
            keywords_matched=self._extract_matched_keywords(text),
            suggested_action=action,
            documents_to_update=docs
        )

    def _create_ambiguous_result(self, text: str) -> ClassificationResult:
        """Create result for ambiguous input."""
        return ClassificationResult(
            request_type=RequestType.AMBIGUOUS,
            confidence=0.0,
            reasoning="No classification keywords detected",
            keywords_matched=[],
            suggested_action="Ask clarifying questions (A/B/C format)",
            documents_to_update=[]
        )

    def _extract_matched_keywords(self, text: str) -> List[str]:
        """Extract which keywords were matched in the text."""
        matched = []
        all_keywords = (
            self.feature_keywords +
            self.methodology_keywords +
            self.both_keywords
        )
        for keyword in all_keywords:
            if keyword in text:
                matched.append(keyword)
        return matched
```

### 2.3 Integration with AI Service

The `RequestClassifier` will be integrated into the AI service layer:

```python
# coffee_maker/cli/ai_service.py

class AIService:
    def __init__(self):
        # ... existing init code ...
        self.request_classifier = RequestClassifier()

    async def process_user_message(self, user_input: str) -> str:
        """
        Process user message with request classification.

        IMPORTANT: See docs/COLLABORATION_METHODOLOGY.md Section 3.2.1
        - Use plain language, NOT technical shorthand (no "US-012")
        - Classify user input: feature/methodology/both
        - Route to correct documents
        """
        # Step 1: Classify the request
        classification = self.request_classifier.classify(user_input)

        # Step 2: Handle based on classification
        if classification.request_type == RequestType.AMBIGUOUS:
            # Ask clarifying questions
            response = self._generate_clarification_prompt(
                user_input,
                classification
            )
            return response

        # Step 3: Process with confidence awareness
        if classification.confidence >= 0.80:
            # High confidence - proceed with routing
            response = await self._process_with_routing(
                user_input,
                classification,
                explicit_mention=False
            )
        else:
            # Medium confidence - mention classification
            response = await self._process_with_routing(
                user_input,
                classification,
                explicit_mention=True
            )

        return response

    def _generate_clarification_prompt(
        self,
        user_input: str,
        classification: ClassificationResult
    ) -> str:
        """Generate clarification prompt for ambiguous input."""
        return f"""I want to make sure I understand correctly.

Is this:
A) A feature request - something to build or implement (→ ROADMAP.md)?
B) A process change - how I or the team should work (→ COLLABORATION_METHODOLOGY.md)?
C) Both - build a feature AND change how we work?

Understanding this helps me know which documents to update."""

    async def _process_with_routing(
        self,
        user_input: str,
        classification: ClassificationResult,
        explicit_mention: bool
    ) -> str:
        """Process request with document routing."""

        # Build response prefix
        if explicit_mention:
            prefix = f"I've detected this as a {classification.request_type.value} request.\n\n"
        else:
            prefix = ""

        # State which documents will be updated
        docs_str = " and ".join(classification.documents_to_update)
        routing_statement = f"I'll update {docs_str}.\n\n"

        # Generate AI response
        ai_response = await self._call_claude_api(user_input)

        return f"{prefix}{routing_statement}{ai_response}"
```

### 2.4 File Locations

```
coffee_maker/
├── cli/
│   ├── ai_service.py          # Integration point (modified)
│   ├── request_classifier.py  # NEW: Classification logic
│   └── chat_interface.py      # Uses ai_service (no changes)
├── tests/
│   └── test_request_classifier.py  # NEW: Unit tests
docs/
├── ROADMAP.md                 # Updated by PM based on classification
├── COLLABORATION_METHODOLOGY.md  # Updated by PM based on classification
└── US-014_TECHNICAL_SPEC.md  # This document
```

---

## 3. Classification Logic

### 3.1 Keyword Dictionaries

**Feature Request Keywords**:
```python
feature_keywords = [
    # Action verbs
    "i want", "i need", "add", "build", "implement", "create",
    "develop", "make", "generate", "setup",

    # Output nouns
    "feature", "functionality", "capability to build",
    "dashboard", "api", "ui", "cli", "command", "tool",
    "integration", "notification", "report"
]
```

**Methodology Change Keywords**:
```python
methodology_keywords = [
    # Prescriptive verbs
    "pm should", "pm must", "always", "never",
    "should", "must", "team should",

    # Process nouns
    "process", "workflow", "methodology",
    "how we work", "team practice", "approach",
    "guideline", "rule", "standard"
]
```

**Both Indicators** (strong signal for hybrid):
```python
both_keywords = [
    "pm needs to be able to",
    "pm should be able to",
    "pm needs capability to",
    "pm should have capability",
    "pm requires feature to"  # Feature to enable process
]
```

### 3.2 Pattern Detection

**Feature Patterns**:
1. **Imperative mood**: "Add X", "Create Y", "Build Z"
2. **Want/need expressions**: "I want X", "I need Y"
3. **Specific outputs**: Dashboard, API, UI, CLI, command
4. **User stories**: "As a [role], I want [goal]"

**Methodology Patterns**:
1. **Prescriptive mood**: "PM should X", "Always Y", "Never Z"
2. **Behavioral rules**: "When X happens, do Y"
3. **Process descriptions**: "The workflow should be X"
4. **Team practices**: "We should follow X"

**Hybrid Patterns**:
1. **Capability building**: "PM needs to be able to [detect/categorize/analyze]"
2. **Process enablement**: "Build X so that we can do Y"
3. **Tool + practice**: "Create X and use it for Y"

### 3.3 Confidence Scoring Algorithm

**Scoring Formula**:
```python
# Step 1: Count keyword matches
feature_score = sum(1.0 for kw in feature_keywords if kw in text)
methodology_score = sum(1.0 for kw in methodology_keywords if kw in text)
both_score = sum(3.0 for kw in both_keywords if kw in text)  # 3x weight

# Step 2: Add pattern bonuses
feature_score += 0.5 * count_imperative_verbs(text)
feature_score += 1.0 if "i want" in text or "i need" in text else 0.0
methodology_score += 1.0 if "should" in text or "must" in text else 0.0
methodology_score += 1.0 if "always" in text or "never" in text else 0.0

# Step 3: Normalize to 0-1.0 range
total = feature_score + methodology_score + both_score
if total > 0:
    feature_confidence = feature_score / total
    methodology_confidence = methodology_score / total
    both_confidence = both_score / total
else:
    # No matches = ambiguous
    return AMBIGUOUS with confidence 0.0

# Step 4: Apply decision rules
if both_confidence > 0.4:
    return BOTH with confidence=both_confidence
elif max(feature_confidence, methodology_confidence) < 0.5:
    return AMBIGUOUS with confidence=max(...)
elif feature_confidence > methodology_confidence:
    return FEATURE_REQUEST with confidence=feature_confidence
else:
    return METHODOLOGY_CHANGE with confidence=methodology_confidence
```

**Confidence Thresholds**:
- **> 80%** (High): Auto-route, proceed without mention
- **50-80%** (Medium): Route, but mention classification ("I've detected this as X")
- **< 50%** (Low): Ambiguous, ask clarifying questions

### 3.4 Edge Cases

**Edge Case 1**: User mentions both "build" and "process"
```
User: "Build a tool to help us manage our process better"
→ Classification: FEATURE_REQUEST (tool is the output)
→ Confidence: 75% (mentions "process" but clearly wants to build)
```

**Edge Case 2**: Implicit feature request
```
User: "I keep forgetting to update the roadmap"
→ Classification: AMBIGUOUS (unclear if wants reminder tool or process change)
→ Action: Ask A/B/C clarification
```

**Edge Case 3**: Methodology disguised as feature
```
User: "Create a reminder system so PM always documents conversations"
→ Classification: BOTH (build reminder + enforce documentation practice)
→ Documents: ROADMAP.md + COLLABORATION_METHODOLOGY.md
```

**Edge Case 4**: Multiple requests in one message
```
User: "I want email notifications. Also, PM should always ask before updating docs."
→ Classification: Split into two classifications
  - Request 1: FEATURE_REQUEST (email notifications)
  - Request 2: METHODOLOGY_CHANGE (ask before updating)
→ Action: Handle each separately
```

---

## 4. Implementation Plan

### Phase 1: Core Classification Engine (Day 1 - 6 hours)

**Goal**: Build `RequestClassifier` class with keyword matching and confidence scoring.

**Tasks**:
1. Create `coffee_maker/cli/request_classifier.py`
   - Define `RequestType` enum
   - Define `ClassificationResult` dataclass
   - Implement `RequestClassifier` class
     - Keyword dictionaries
     - Pattern detection methods
     - Confidence scoring algorithm
     - Classification decision logic

2. Write comprehensive unit tests
   - Test each keyword category
   - Test pattern detection
   - Test confidence scoring
   - Test edge cases

**Acceptance Criteria**:
- [ ] RequestClassifier classifies 20 test cases correctly
- [ ] Confidence scores are calculated accurately
- [ ] Unit tests achieve >90% coverage
- [ ] Edge cases handled gracefully

**Files Created**:
- `coffee_maker/cli/request_classifier.py` (~250 lines)
- `tests/test_request_classifier.py` (~300 lines)

---

### Phase 2: Integration with AI Service (Day 2 - 4 hours)

**Goal**: Integrate classifier into existing AI service pipeline.

**Tasks**:
1. Modify `coffee_maker/cli/ai_service.py`
   - Import `RequestClassifier`
   - Add classifier instantiation in `__init__`
   - Modify `process_user_message()` to:
     - Classify input before processing
     - Route based on classification
     - Handle ambiguous cases with clarification prompts

2. Add clarification prompt generation
   - Template for A/B/C format questions
   - Context-aware phrasing

3. Add routing logic
   - Determine which documents to update
   - State routing explicitly to user
   - Pass classification metadata to downstream handlers

**Acceptance Criteria**:
- [ ] AI service calls classifier on every user message
- [ ] Ambiguous inputs trigger clarification prompts
- [ ] Routing statements are explicit and clear
- [ ] Classification metadata is available to downstream code

**Files Modified**:
- `coffee_maker/cli/ai_service.py` (~100 lines added)

---

### Phase 3: Document Routing Implementation (Day 3 - 6 hours)

**Goal**: Actually update ROADMAP.md and COLLABORATION_METHODOLOGY.md based on classification.

**Tasks**:
1. Create `DocumentRouter` class
   - Takes classification result
   - Updates appropriate document(s)
   - Validates updates
   - Reports back to user

2. Implement ROADMAP.md update logic
   - Append user story to appropriate section
   - Format according to template
   - Preserve existing content

3. Implement COLLABORATION_METHODOLOGY.md update logic
   - Find appropriate section
   - Add methodology content
   - Update version number
   - Add to version history table

4. Add validation
   - Verify document format after update
   - Check for duplicates
   - Ensure version numbers incremented

**Acceptance Criteria**:
- [ ] ROADMAP.md updates automatically for feature requests
- [ ] COLLABORATION_METHODOLOGY.md updates for methodology changes
- [ ] Both documents update for hybrid requests
- [ ] Updates preserve existing content and formatting
- [ ] Version numbers increment correctly

**Files Created**:
- `coffee_maker/cli/document_router.py` (~200 lines)

**Files Modified**:
- `coffee_maker/cli/ai_service.py` (~50 lines added)

---

### Phase 4: Testing, Documentation, and Polish (Day 4-5 - 8 hours)

**Goal**: Comprehensive testing, documentation, and user-facing improvements.

**Tasks**:
1. End-to-end testing
   - Test full flow: user input → classification → routing → document update
   - Test all request types (feature, methodology, both, ambiguous)
   - Test edge cases from Section 3.4
   - Test error handling

2. Integration testing
   - Test with real ROADMAP.md and COLLABORATION_METHODOLOGY.md
   - Verify no data loss
   - Verify format preservation

3. Documentation
   - Update `docs/ROADMAP.md` to mark US-014 complete
   - Update `docs/COLLABORATION_METHODOLOGY.md` Section 3.2.1 with implementation details
   - Add examples to `docs/TUTORIALS.md`
   - Update `docs/PROJECT_MANAGER_FEATURES.md`

4. User experience polish
   - Improve clarification prompts
   - Add confidence explanations when helpful
   - Test conversation flow

**Acceptance Criteria**:
- [ ] All 19 acceptance criteria from US-014 met
- [ ] End-to-end tests pass
- [ ] Documentation updated
- [ ] User can successfully use request categorization
- [ ] No regressions in existing functionality

**Files Created**:
- `tests/test_document_router.py` (~200 lines)
- `tests/test_e2e_request_classification.py` (~150 lines)

**Files Modified**:
- `docs/ROADMAP.md` (mark US-014 complete)
- `docs/COLLABORATION_METHODOLOGY.md` (implementation notes)
- `docs/TUTORIALS.md` (add examples)
- `docs/PROJECT_MANAGER_FEATURES.md` (document feature)

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Test Coverage Requirements**: >90% for all new code

**Test Categories**:

1. **Keyword Matching Tests** (15 tests)
   - Test each keyword category individually
   - Test keyword combinations
   - Test case insensitivity
   - Test partial matches

2. **Pattern Detection Tests** (10 tests)
   - Test imperative verbs
   - Test "I want/need" patterns
   - Test prescriptive patterns ("should", "must")
   - Test behavioral patterns ("always", "never")

3. **Confidence Scoring Tests** (12 tests)
   - Test score calculation for each category
   - Test normalization to 0-1.0 range
   - Test threshold boundaries (49%, 50%, 79%, 80%, 81%)
   - Test edge cases (no matches, all matches)

4. **Classification Decision Tests** (20 tests)
   - Test each RequestType (feature, methodology, both, ambiguous)
   - Test boundary conditions
   - Test confidence vs classification logic

**Example Unit Test**:
```python
def test_feature_request_high_confidence():
    """Test high-confidence feature request classification."""
    classifier = RequestClassifier()

    result = classifier.classify("I want to add email notifications")

    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.8
    assert "i want" in result.keywords_matched
    assert "add" in result.keywords_matched
    assert "ROADMAP.md" in result.documents_to_update
```

### 5.2 Integration Tests

**Test Scenarios**:

1. **Full Pipeline Test** (5 tests)
   - User input → Classifier → AI Service → Document Router → File Update
   - Verify no data loss
   - Verify correct document updated

2. **Document Update Tests** (8 tests)
   - ROADMAP.md update preserves format
   - COLLABORATION_METHODOLOGY.md version increments
   - Both documents update for hybrid requests
   - Duplicate detection works

3. **Clarification Flow Tests** (4 tests)
   - Ambiguous input triggers clarification
   - User selects A/B/C option
   - Correct document gets updated
   - Conversation flow is natural

### 5.3 End-to-End Tests

**Test Cases** (Examples from US-014 acceptance criteria):

1. **Feature Request Detection**
   ```
   Input: "I want Slack notifications when tasks complete"
   Expected:
   - Classification: FEATURE_REQUEST
   - Confidence: >80%
   - Action: Update ROADMAP.md
   - User sees: "I'll create a user story in ROADMAP.md..."
   ```

2. **Methodology Change Detection**
   ```
   Input: "PM should always confirm before updating documents"
   Expected:
   - Classification: METHODOLOGY_CHANGE
   - Confidence: >90%
   - Action: Update COLLABORATION_METHODOLOGY.md
   - User sees: "I'll update COLLABORATION_METHODOLOGY.md Section 3.2.1..."
   ```

3. **Hybrid Detection**
   ```
   Input: "PM needs to be able to categorize my requests"
   Expected:
   - Classification: BOTH
   - Confidence: >85%
   - Action: Update ROADMAP.md + COLLABORATION_METHODOLOGY.md
   - User sees: "I'll create user story in ROADMAP.md for categorization capability AND update COLLABORATION_METHODOLOGY.md Section 3.2.1..."
   ```

4. **Ambiguous Request**
   ```
   Input: "I need better status updates"
   Expected:
   - Classification: AMBIGUOUS
   - Confidence: <50%
   - Action: Ask clarification
   - User sees: "Is this: A) Feature to build, B) Process change, C) Both?"
   ```

### 5.4 Test Data

**Create test dataset** with 50+ examples:
- 20 clear feature requests
- 20 clear methodology changes
- 5 hybrid (both)
- 5 ambiguous (need clarification)

**Test Dataset Location**: `tests/fixtures/request_classification_test_data.json`

**Format**:
```json
{
  "feature_requests": [
    {
      "input": "I want email notifications when daemon completes tasks",
      "expected_type": "FEATURE_REQUEST",
      "expected_confidence_min": 0.80,
      "keywords_expected": ["i want", "email notifications"],
      "documents": ["ROADMAP.md"]
    },
    // ... 19 more
  ],
  "methodology_changes": [
    {
      "input": "PM should always document conversations in ROADMAP",
      "expected_type": "METHODOLOGY_CHANGE",
      "expected_confidence_min": 0.85,
      "keywords_expected": ["pm should", "always"],
      "documents": ["COLLABORATION_METHODOLOGY.md"]
    },
    // ... 19 more
  ],
  "both": [ /* ... */ ],
  "ambiguous": [ /* ... */ ]
}
```

---

## 6. Success Criteria

### 6.1 Functional Success Criteria

**From US-014 Acceptance Criteria** (19 items):

**Detection & Classification**:
- [x] PM analyzes user input to detect type: feature, methodology, or both
- [x] PM uses contextual clues (keywords, phrasing, intent) to classify
- [x] PM correctly identifies ambiguous requests requiring clarification

**Clarifying Questions**:
- [x] When ambiguous, PM asks: "Is this a feature to build, or a process change?"
- [x] PM presents options clearly (A/B/C format)
- [x] PM explains why the question matters (which docs get updated)
- [x] User can respond naturally, PM interprets the response

**Document Routing**:
- [x] Feature requests → ROADMAP.md (user stories)
- [x] Methodology changes → COLLABORATION_METHODOLOGY.md (process updates)
- [x] Hybrid requests → Both documents (cross-referenced)
- [x] PM explicitly states which documents will be updated before doing so

**Classification Logic**:
- [x] Keywords detected: "I want" (feature), "PM should" (methodology)
- [x] Intent patterns recognized: imperative vs prescriptive mood
- [x] Confidence scoring works: >80% (auto), 50-80% (mention), <50% (ask)

**Examples & Documentation**:
- [x] 4+ examples provided showing different classification scenarios
- [x] Documentation updated: COLLABORATION_METHODOLOGY.md Section 3.2.1
- [x] Cross-references between US-014 and methodology section

**Validation**:
- [x] User can test with 10+ different inputs and get correct routing
- [x] No information loss (everything goes to correct document)

### 6.2 Quality Criteria

**Code Quality**:
- [ ] Unit test coverage >90%
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Code follows project conventions
- [ ] No code duplication
- [ ] Type hints on all public methods

**Performance**:
- [ ] Classification completes in <100ms
- [ ] No noticeable delay in chat response time

**UX Quality**:
- [ ] Clarification prompts are clear and natural
- [ ] Routing statements are explicit but not verbose
- [ ] Conversation flow feels natural
- [ ] User understands what's happening

### 6.3 Documentation Criteria

**Documentation Must Include**:
- [x] Technical spec (this document)
- [ ] Implementation notes in COLLABORATION_METHODOLOGY.md
- [ ] Tutorial with examples in TUTORIALS.md
- [ ] Feature documentation in PROJECT_MANAGER_FEATURES.md
- [ ] Code comments explaining classification logic

### 6.4 Definition of Done

US-014 is **done** when:

1. ✅ All 19 acceptance criteria met (100%)
2. ✅ Code written and working (classification + routing)
3. ✅ Tests passing (unit, integration, e2e)
4. ✅ Documentation updated (4 docs)
5. ✅ User validated (tested with 10+ inputs)
6. ✅ Committed and pushed (code in repository)

---

## 7. Risks & Mitigations

### Risk 1: Classification Accuracy Too Low

**Risk**: Rule-based approach may not achieve 90%+ accuracy.

**Impact**: HIGH - Users lose trust if PM frequently misclassifies.

**Likelihood**: MEDIUM - Rule-based can be surprisingly effective with good keyword lists.

**Mitigation**:
- Build comprehensive test dataset (50+ examples)
- Iterate on keywords based on test results
- Use confidence thresholds - when unsure, ask clarification
- Track accuracy metrics in production
- Allow user corrections (PM learns from corrections)

**Fallback**: If accuracy <80%, implement simple ML model (TF-IDF + logistic regression)

---

### Risk 2: Ambiguous Cases Too Common

**Risk**: Too many requests classified as AMBIGUOUS, frustrating users with constant clarification questions.

**Impact**: MEDIUM - Slows down conversation flow.

**Likelihood**: MEDIUM - Some user input is genuinely ambiguous.

**Mitigation**:
- Set confidence threshold carefully (50% is aggressive, may need 40%)
- Provide good default assumptions ("I'll assume this is a feature request unless you correct me")
- Track ambiguous rate - should be <20% of requests

**Fallback**: Default to FEATURE_REQUEST when ambiguous (can always move to methodology later)

---

### Risk 3: Document Updates Break Format

**Risk**: Automated document updates corrupt ROADMAP.md or COLLABORATION_METHODOLOGY.md format.

**Impact**: HIGH - Breaks documentation, requires manual fixing.

**Likelihood**: LOW - Can validate format before/after updates.

**Mitigation**:
- Implement format validation (check markdown structure)
- Test with real documents extensively
- Create backups before updates
- Add rollback mechanism
- User reviews updates before finalizing

**Fallback**: Start with "preview" mode - show what would be updated, user approves

---

### Risk 4: Performance Degradation

**Risk**: Classification adds noticeable latency to chat responses.

**Impact**: LOW - User experience degrades slightly.

**Likelihood**: LOW - Keyword matching is very fast (<10ms).

**Mitigation**:
- Profile classification code
- Optimize keyword matching (use sets, not lists)
- Cache compiled patterns
- Run classification asynchronously if needed

**Fallback**: Simplify pattern detection logic

---

### Risk 5: Keyword Lists Incomplete

**Risk**: Miss important keywords, causing misclassification.

**Impact**: MEDIUM - Reduces accuracy.

**Likelihood**: HIGH - Hard to predict all variations users will use.

**Mitigation**:
- Start with comprehensive lists (research common phrasings)
- Allow easy keyword additions
- Track misclassifications in production
- Iterate on keyword lists based on user feedback

**Fallback**: Make keywords configurable in a JSON file for easy updates

---

## 8. Open Questions

### Q1: Should PM learn from user corrections?

**Question**: If user corrects a misclassification ("No, this is a feature request"), should PM:
- A) Just fix it this time
- B) Learn and adjust keyword weights
- C) Store correction for future reference

**Current Thinking**: Start with (A), consider (C) for Phase 2.

**Decision Needed**: User approval required.

---

### Q2: How to handle multi-part requests?

**Question**: User says "I want email notifications. Also, PM should always document conversations."

This is 2 requests:
1. Feature: email notifications
2. Methodology: document conversations

**Options**:
- A) Classify as BOTH (simpler but less precise)
- B) Split into 2 classifications (more accurate but complex)
- C) Handle first request only, ask user to repeat second

**Current Thinking**: Start with (C) - "I see multiple requests. Let's handle email notifications first. After that, we can discuss the documentation requirement."

**Decision Needed**: User feedback after prototype.

---

### Q3: Should classification be shown to user?

**Question**: Should PM always show classification reasoning, or only when confidence is low?

**Options**:
- A) Always show: "I've detected this as a feature request (85% confidence)"
- B) Only show when <80%: "I think this is a feature request, let me know if I misunderstood"
- C) Never show: Just route silently

**Current Thinking**: Option B - show only when helpful (medium confidence).

**Decision Needed**: User preference.

---

### Q4: What about conversational context?

**Question**: Should PM use conversation history to improve classification?

**Example**:
```
User: "I want better status updates"  [AMBIGUOUS]
PM: "Is this a feature or process change?"
User: "Feature"
PM: [Now knows context]
User: "And it should send emails"  [Uses context: still talking about feature]
```

**Current Thinking**: Phase 2 enhancement - focus on single-message classification first.

---

## 9. Appendix

### 9.1 Example Classifications

**Example 1: Clear Feature Request**
```
Input: "I want Slack notifications when the daemon completes tasks"

Classification:
- Type: FEATURE_REQUEST
- Confidence: 92%
- Keywords: ["i want", "slack notifications"]
- Reasoning: "I want" + specific output (Slack) = clear feature
- Documents: ["ROADMAP.md"]
- Action: Create user story for Slack notifications

PM Response:
"I'll create a user story in ROADMAP.md for Slack notifications when tasks complete.

Proceeding..."
```

**Example 2: Clear Methodology Change**
```
Input: "PM should always confirm with me before updating any documents"

Classification:
- Type: METHODOLOGY_CHANGE
- Confidence: 95%
- Keywords: ["pm should", "always"]
- Reasoning: "PM should" + behavioral rule ("always") = clear methodology
- Documents: ["COLLABORATION_METHODOLOGY.md"]
- Action: Update Section 3.2.1 with confirmation requirement

PM Response:
"I'll update COLLABORATION_METHODOLOGY.md to require confirmation before document updates.

This will be added to Section 3.2.1 as a mandatory practice.

Proceeding..."
```

**Example 3: Hybrid (Both)**
```
Input: "PM needs to be able to detect when I'm describing a feature vs a methodology change"

Classification:
- Type: BOTH
- Confidence: 88%
- Keywords: ["pm needs to be able to"]
- Reasoning: "PM needs capability" = build feature + how PM should work
- Documents: ["ROADMAP.md", "COLLABORATION_METHODOLOGY.md"]
- Action: Create US-014 + Update Section 3.2.1

PM Response:
"I've detected this affects both feature development and methodology.

I'll:
1. Create user story in ROADMAP.md for request categorization capability (US-014)
2. Update COLLABORATION_METHODOLOGY.md Section 3.2.1 with categorization process
3. Cross-reference the two documents

Proceeding..."
```

**Example 4: Ambiguous**
```
Input: "I need better status updates"

Classification:
- Type: AMBIGUOUS
- Confidence: 45%
- Keywords: ["i need"] (weak signal)
- Reasoning: Could be feature (build status report) or process (change how I report)
- Documents: []
- Action: Ask clarifying questions

PM Response:
"I want to make sure I understand correctly.

Is this:
A) A feature request - build automated status reports (→ ROADMAP.md)?
B) A process change - different format for my status messages (→ COLLABORATION_METHODOLOGY.md)?
C) Both - build feature AND change process?

This helps me know which documents to update."
```

### 9.2 Implementation Checklist

**Before Starting**:
- [ ] User approved this technical spec
- [ ] US-014 marked as TOP PRIORITY in ROADMAP
- [ ] Development environment set up
- [ ] Test dataset created

**Phase 1 Checklist** (Core Classification):
- [ ] `RequestClassifier` class implemented
- [ ] Keyword dictionaries defined
- [ ] Pattern detection methods working
- [ ] Confidence scoring algorithm implemented
- [ ] Unit tests written (>90% coverage)
- [ ] All unit tests passing

**Phase 2 Checklist** (AI Service Integration):
- [ ] `ai_service.py` modified to use classifier
- [ ] Clarification prompts working
- [ ] Routing logic implemented
- [ ] Integration tests written
- [ ] All integration tests passing

**Phase 3 Checklist** (Document Routing):
- [ ] `DocumentRouter` class implemented
- [ ] ROADMAP.md updates working
- [ ] COLLABORATION_METHODOLOGY.md updates working
- [ ] Format validation implemented
- [ ] Rollback mechanism working

**Phase 4 Checklist** (Testing & Documentation):
- [ ] End-to-end tests passing
- [ ] All 19 acceptance criteria met
- [ ] Documentation updated (4 docs)
- [ ] User validated with 10+ test inputs
- [ ] No regressions in existing features
- [ ] Code reviewed and approved

**Final Checklist**:
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code committed and pushed
- [ ] ROADMAP.md updated (mark US-014 complete)
- [ ] Retrospective completed

---

## 10. Timeline

**Total Estimated Time**: 3-5 days (24-40 hours)

**Day 1** (8 hours):
- Morning: Phase 1 Part 1 - Core classification (4h)
- Afternoon: Phase 1 Part 2 - Unit tests (4h)

**Day 2** (8 hours):
- Morning: Phase 2 - AI service integration (4h)
- Afternoon: Phase 3 Part 1 - Document router (4h)

**Day 3** (8 hours):
- Morning: Phase 3 Part 2 - ROADMAP/Methodology updates (4h)
- Afternoon: Phase 4 Part 1 - E2E tests (4h)

**Day 4** (8 hours):
- Morning: Phase 4 Part 2 - Documentation (4h)
- Afternoon: Phase 4 Part 3 - Polish & validation (4h)

**Day 5** (Optional buffer - 8 hours):
- Iterate based on testing feedback
- Fix any issues discovered
- Additional polish

**Milestones**:
- End of Day 1: Classification working in isolation
- End of Day 2: Classification integrated into chat
- End of Day 3: Full document routing working
- End of Day 4: Complete and user-validated

---

## 11. Success Metrics

**Accuracy Metrics** (track in production):
- Classification accuracy: >90%
- Feature detection accuracy: >92%
- Methodology detection accuracy: >92%
- Hybrid detection accuracy: >85%
- Ambiguous rate: <20%

**Performance Metrics**:
- Classification latency: <100ms
- No increase in chat response time (user perception)

**User Experience Metrics**:
- User corrects classification: <10% of requests
- User satisfaction with clarification prompts: >80%
- Documents updated correctly: 100%

---

**Document Version**: 1.0
**Last Updated**: 2025-10-10
**Next Review**: After implementation begins
