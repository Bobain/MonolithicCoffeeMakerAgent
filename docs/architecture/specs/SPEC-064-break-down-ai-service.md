# SPEC-064: Break Down ai_service.py

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**: REFACTORING_BACKLOG.md (P0 Item #2), ADR-001 (Mixins Pattern)

---

## Problem Statement

`coffee_maker/cli/ai_service.py` has grown to **1,269 lines of code**, which is **2.5x the recommended 500 LOC limit**. This monolithic file contains a single `AIService` class with 18 methods handling multiple distinct responsibilities:

- API/CLI provider integration (Claude API vs Claude CLI)
- Request classification (Phase 2 US-021)
- Document updates integration (Phase 3 US-021)
- User story extraction and analysis
- Streaming responses
- System prompt construction
- Metadata extraction
- Technical spec generation integration
- Warning notifications

This violates the Single Responsibility Principle and makes the code:
- Hard to test (tight coupling between concerns)
- Difficult to maintain (changes ripple across the file)
- Challenging to understand (cognitive overload)
- Risky to modify (high chance of breaking unrelated functionality)

---

## Proposed Solution

Break down `ai_service.py` into a **modular AI service architecture** using composition and clear separation of concerns.

### High-Level Architecture

```
coffee_maker/cli/ai/
├── __init__.py                     # Public API exports
├── service.py                      # Core AIService coordinator (200 LOC)
├── providers/
│   ├── __init__.py
│   ├── base.py                     # BaseProvider interface (50 LOC)
│   ├── api_provider.py             # Anthropic API client (150 LOC)
│   └── cli_provider.py             # Claude CLI client (150 LOC)
├── classification/
│   ├── __init__.py
│   ├── classifier_integration.py   # RequestClassifier integration (150 LOC)
│   └── clarification.py            # Clarification prompt builder (100 LOC)
├── document/
│   ├── __init__.py
│   └── updater_integration.py      # DocumentUpdater integration (200 LOC)
├── user_stories/
│   ├── __init__.py
│   ├── extractor.py                # Story extraction from NL (200 LOC)
│   ├── analyzer.py                 # Impact analysis (150 LOC)
│   └── prioritizer.py              # Prioritization questions (100 LOC)
├── streaming/
│   ├── __init__.py
│   └── stream_handler.py           # Streaming response logic (150 LOC)
├── prompts/
│   ├── __init__.py
│   ├── builder.py                  # System prompt construction (150 LOC)
│   └── metadata_extractor.py       # Metadata extraction (150 LOC)
└── notifications/
    ├── __init__.py
    └── warning_notifier.py         # User warning system (100 LOC)
```

**Total LOC after breakdown**: ~1,850 LOC (across 17 files)
**Average file size**: ~109 LOC (all under 200 LOC target)

---

## Architecture

### Component Design

#### 1. `service.py` - Core Coordinator (200 LOC)

**Responsibility**: Orchestrate AI operations, delegate to specialized components.

```python
from coffee_maker.cli.ai.providers.base import BaseProvider
from coffee_maker.cli.ai.classification.classifier_integration import ClassifierIntegration
from coffee_maker.cli.ai.document.updater_integration import DocumentUpdaterIntegration

class AIService:
    """Core AI service coordinator.

    Delegates to specialized components:
    - Provider (API/CLI)
    - Classifier (request classification)
    - DocumentUpdater (document updates)
    - UserStoryExtractor (story parsing)
    """

    def __init__(self, provider: BaseProvider, ...):
        self.provider = provider
        self.classifier = ClassifierIntegration() if available else None
        self.document_updater = DocumentUpdaterIntegration() if available else None
        self.user_story_extractor = UserStoryExtractor(provider)
        # ...

    def process_request(self, user_input: str, context: Dict, history: List[Dict]) -> AIResponse:
        """Main entry point - delegates to components."""
        # 1. Classify request
        classification = self.classifier.classify(user_input) if self.classifier else None

        # 2. Build prompt
        prompt = self.prompt_builder.build(context, classification)

        # 3. Execute via provider
        response = self.provider.execute(prompt, history)

        # 4. Update documents if needed
        if self.document_updater and classification:
            self.document_updater.update(classification, user_input, response)

        return response
```

**Public API**:
- `process_request(user_input, context, history) -> AIResponse`
- `process_request_stream(user_input, context, history) -> Generator`
- `classify_intent(user_input) -> str`
- `extract_user_story(user_input) -> Optional[Dict]`
- `generate_prioritization_question(story1, story2) -> str`
- `analyze_user_story_impact(story, roadmap_summary, priorities) -> str`
- `check_available() -> bool`
- `classify_user_request(user_input) -> Optional[Dict]`
- `warn_user(title, message, priority, context) -> int`
- `generate_technical_spec(user_story, feature_type, complexity) -> Dict`

---

#### 2. `providers/` - AI Provider Abstraction

**Responsibility**: Encapsulate API/CLI provider differences behind a common interface.

**`base.py`** (50 LOC):
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ProviderResponse:
    content: str
    success: bool
    error: Optional[str] = None

class BaseProvider(ABC):
    """Abstract base for AI providers."""

    @abstractmethod
    def execute(self, prompt: str, messages: List[Dict]) -> ProviderResponse:
        """Execute prompt with message history."""
        pass

    @abstractmethod
    def execute_stream(self, prompt: str, messages: List[Dict]) -> Generator[str, None, None]:
        """Execute prompt with streaming response."""
        pass

    @abstractmethod
    def check_available(self) -> bool:
        """Check if provider is available."""
        pass
```

**`api_provider.py`** (150 LOC):
```python
from anthropic import Anthropic

class APIProvider(BaseProvider):
    """Anthropic API provider."""

    def __init__(self, model: str, max_tokens: int, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def execute(self, system_prompt: str, messages: List[Dict]) -> ProviderResponse:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages
        )
        return ProviderResponse(
            content=response.content[0].text,
            success=True
        )

    def execute_stream(self, system_prompt: str, messages: List[Dict]) -> Generator:
        with self.client.messages.stream(...) as stream:
            for text in stream.text_stream:
                yield text
```

**`cli_provider.py`** (150 LOC):
```python
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

class CLIProvider(BaseProvider):
    """Claude CLI provider (subscription-based)."""

    def __init__(self, model: str, max_tokens: int, claude_path: str):
        self.cli = ClaudeCLIInterface(
            claude_path=claude_path,
            model=model,
            max_tokens=max_tokens
        )

    def execute(self, system_prompt: str, messages: List[Dict]) -> ProviderResponse:
        full_prompt = self._build_full_prompt(system_prompt, messages)
        result = self.cli.execute_prompt(full_prompt)

        return ProviderResponse(
            content=result.content,
            success=result.success,
            error=result.error
        )

    def execute_stream(self, system_prompt: str, messages: List[Dict]) -> Generator:
        # CLI doesn't support streaming, simulate with word-by-word
        response = self.execute(system_prompt, messages)
        for word in response.content.split():
            yield word + " "
            time.sleep(0.01)
```

---

#### 3. `classification/` - Request Classification

**Responsibility**: Integrate RequestClassifier and handle clarification.

**`classifier_integration.py`** (150 LOC):
```python
from coffee_maker.cli.request_classifier import RequestClassifier, ClassificationResult

class ClassifierIntegration:
    """Integrates RequestClassifier into AI service."""

    def __init__(self):
        self.classifier = RequestClassifier()

    def classify(self, user_input: str) -> Optional[ClassificationResult]:
        """Classify user request."""
        try:
            return self.classifier.classify(user_input)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None

    def needs_clarification(self, classification: ClassificationResult) -> bool:
        """Check if clarification is needed."""
        return (
            classification.request_type.value == "clarification_needed"
            or classification.confidence < 0.5
        )
```

**`clarification.py`** (100 LOC):
```python
def build_clarification_prompt(classification: ClassificationResult) -> str:
    """Build clarification prompt from classification result."""
    prompt = "I need some clarification to help you effectively.\n\n"

    if classification.confidence < 0.5:
        prompt += f"I'm not confident about interpreting your request (confidence: {classification.confidence:.0%}).\n\n"

    if classification.suggested_questions:
        prompt += "\n".join(classification.suggested_questions)

    # Add detected indicators for transparency
    if classification.feature_indicators:
        indicators = ", ".join([ind.split(": ")[1] for ind in classification.feature_indicators[:3]])
        prompt += f"\n\nFeature indicators I detected: {indicators}"

    return prompt
```

---

#### 4. `document/` - Document Update Integration

**Responsibility**: Integrate DocumentUpdater and handle update results.

**`updater_integration.py`** (200 LOC):
```python
from coffee_maker.cli.document_updater import DocumentUpdater, DocumentUpdateError

class DocumentUpdaterIntegration:
    """Integrates DocumentUpdater into AI service."""

    def __init__(self):
        self.updater = DocumentUpdater()

    def update_documents(
        self,
        classification: ClassificationResult,
        user_input: str,
        ai_response: str
    ) -> Optional[Dict[str, bool]]:
        """Update documents based on classification."""
        if not self.should_update(classification):
            return None

        try:
            metadata = self._extract_metadata(user_input, ai_response, classification)

            results = self.updater.update_documents(
                request_type=classification.request_type,
                content=user_input,
                target_documents=classification.target_documents,
                metadata=metadata
            )

            self._log_results(results)
            return results

        except DocumentUpdateError as e:
            logger.error(f"Document update failed: {e}")
            return None

    def should_update(self, classification: ClassificationResult) -> bool:
        """Check if documents should be updated."""
        return (
            classification.request_type.value != "clarification_needed"
            and classification.target_documents
        )

    def _extract_metadata(self, user_input: str, ai_response: str, classification: ClassificationResult) -> Dict:
        """Extract metadata for document update."""
        # Delegate to MetadataExtractor
        from coffee_maker.cli.ai.prompts.metadata_extractor import extract_metadata
        return extract_metadata(user_input, ai_response, classification)
```

---

#### 5. `user_stories/` - User Story Processing

**Responsibility**: Extract, analyze, and prioritize user stories.

**`extractor.py`** (200 LOC):
```python
class UserStoryExtractor:
    """Extracts user stories from natural language."""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def extract(self, user_input: str) -> Optional[Dict]:
        """Extract User Story components from natural language."""
        prompt = self._build_extraction_prompt(user_input)
        response = self.provider.execute(prompt, [])

        if "NOT_A_USER_STORY" in response.content:
            return None

        return self._parse_xml_response(response.content)

    def _build_extraction_prompt(self, user_input: str) -> str:
        return f"""Extract User Story from this input:

{user_input}

Respond ONLY in this exact XML format:
<user_story>
<role>system administrator</role>
<want>deploy code_developer on GCP</want>
<so_that>it runs 24/7 autonomously</so_that>
<title>Deploy code_developer on GCP</title>
</user_story>

If this is NOT a User Story (no clear feature request), respond with: NOT_A_USER_STORY
"""

    def _parse_xml_response(self, content: str) -> Optional[Dict]:
        """Parse XML response into story dict."""
        role_match = re.search(r"<role>(.+?)</role>", content, re.DOTALL)
        want_match = re.search(r"<want>(.+?)</want>", content, re.DOTALL)
        so_that_match = re.search(r"<so_that>(.+?)</so_that>", content, re.DOTALL)
        title_match = re.search(r"<title>(.+?)</title>", content, re.DOTALL)

        if not all([role_match, want_match, so_that_match, title_match]):
            return None

        return {
            "role": role_match.group(1).strip(),
            "want": want_match.group(1).strip(),
            "so_that": so_that_match.group(1).strip(),
            "title": title_match.group(1).strip(),
        }
```

**`analyzer.py`** (150 LOC):
```python
class UserStoryAnalyzer:
    """Analyzes roadmap impact of user stories."""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def analyze_impact(
        self,
        story: Dict,
        roadmap_summary: Dict,
        priorities: List[Dict]
    ) -> str:
        """Analyze roadmap impact of adding a User Story."""
        prompt = self._build_analysis_prompt(story, roadmap_summary, priorities)
        response = self.provider.execute(prompt, [])
        return response.content

    def _build_analysis_prompt(self, story: Dict, roadmap_summary: Dict, priorities: List[Dict]) -> str:
        priorities_text = "\n".join([
            f"- {p['number']}: {p['title']} ({p['status']})"
            for p in priorities[:10]
        ])

        return f"""Analyze the roadmap impact of adding this User Story:

**New User Story:**
- Title: {story.get('title', 'Unknown')}
- As a: {story.get('role', 'user')}
- I want: {story.get('want', 'feature')}
- So that: {story.get('so_that', 'benefit')}
- Estimated effort: {story.get('estimated_effort', 'TBD')}

**Current Roadmap:**
Total priorities: {roadmap_summary.get('total', 0)}
Completed: {roadmap_summary.get('completed', 0)}
In Progress: {roadmap_summary.get('in_progress', 0)}
Planned: {roadmap_summary.get('planned', 0)}

**Existing Priorities:**
{priorities_text}

Analyze:
1. Which existing priority(ies) could this User Story fit into?
2. Would this require a new priority?
3. What priorities might be delayed if we add this?
4. What dependencies exist?
5. What are the risks?
6. What's your recommendation?

Provide a concise analysis in markdown format.
"""
```

**`prioritizer.py`** (100 LOC):
```python
def generate_prioritization_question(story1: Dict, story2: Dict) -> str:
    """Generate natural question asking user to prioritize between two stories."""
    return f"""
Between these two User Stories, which is more urgent for you?

**A) {story1.get('title', 'Story 1')}**
   As a: {story1.get('role', 'user')}
   I want: {story1.get('want', '...')}
   Estimated effort: {story1.get('estimated_effort', 'TBD')}

**B) {story2.get('title', 'Story 2')}**
   As a: {story2.get('role', 'user')}
   I want: {story2.get('want', '...')}
   Estimated effort: {story2.get('estimated_effort', 'TBD')}

Your business priorities will help me organize the roadmap effectively.
Type **A** or **B** to indicate which story is more important to complete first.
""".strip()
```

---

#### 6. `streaming/` - Streaming Response Handler

**Responsibility**: Handle streaming responses from providers.

**`stream_handler.py`** (150 LOC):
```python
class StreamHandler:
    """Handles streaming responses from AI providers."""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict]
    ) -> Generator[str, None, None]:
        """Stream response from provider."""
        try:
            for chunk in self.provider.execute_stream(system_prompt, messages):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"\n\n❌ Sorry, I encountered an error: {str(e)}"
```

---

#### 7. `prompts/` - Prompt Construction

**Responsibility**: Build system prompts and extract metadata.

**`builder.py`** (150 LOC):
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

class PromptBuilder:
    """Builds system prompts with context."""

    def build(self, context: Dict, classification: Optional[ClassificationResult] = None) -> str:
        """Build system prompt with roadmap context and classification."""
        base_prompt = self._build_base_prompt(context)

        if classification:
            base_prompt = self._add_classification_guidance(base_prompt, classification)

        return base_prompt

    def _build_base_prompt(self, context: Dict) -> str:
        """Build base system prompt from context."""
        roadmap_summary = context.get("roadmap_summary", {})

        # Load centralized prompt
        prompt = load_prompt(
            PromptNames.AGENT_PROJECT_MANAGER,
            {
                "TOTAL_PRIORITIES": str(roadmap_summary.get("total", 0)),
                "COMPLETED_PRIORITIES": str(roadmap_summary.get("completed", 0)),
                "IN_PROGRESS_PRIORITIES": str(roadmap_summary.get("in_progress", 0)),
                "PLANNED_PRIORITIES": str(roadmap_summary.get("planned", 0)),
                "PRIORITY_LIST": self._build_priority_list(roadmap_summary),
            },
        )

        return prompt

    def _add_classification_guidance(self, prompt: str, classification: ClassificationResult) -> str:
        """Add classification guidance to prompt."""
        guidance = f"""

**Request Classification (US-021 Phase 2):**
- Type: {classification.request_type.value}
- Confidence: {classification.confidence:.0%}
- Target Documents: {', '.join(classification.target_documents)}

**Your Instructions Based on Classification:**
1. Acknowledge the request type explicitly (e.g., "I see you're requesting a new feature...")
2. Explain which documents will be updated: {', '.join(classification.target_documents)}
3. If hybrid request (both feature + methodology), explain you'll update both ROADMAP and TEAM_COLLABORATION
4. Provide your response addressing the specific request type
5. End with confirmation: "I'll update [documents] with this information."

Remember: Be transparent about what you'll do with the user's request!
"""
        return prompt + guidance

    def _build_priority_list(self, roadmap_summary: Dict) -> str:
        """Build formatted priority list."""
        priorities = roadmap_summary.get("priorities", [])
        if not priorities:
            return "No priorities currently listed."

        priority_list = ""
        for p in priorities[:10]:  # Limit to first 10
            priority_list += f"- {p['number']}: {p['title']} ({p['status']})\n"

        return priority_list
```

**`metadata_extractor.py`** (150 LOC):
```python
def extract_metadata(
    user_input: str,
    ai_response: str,
    classification: ClassificationResult
) -> Dict:
    """Extract metadata for document update from AI response and user input."""
    metadata = {}

    # Extract title from user input
    metadata["title"] = extract_title(user_input)

    # Set defaults based on request type
    if classification.request_type.value == "feature_request":
        metadata["business_value"] = "TBD - please specify business value"
        metadata["estimated_effort"] = "TBD - to be estimated during planning"
        metadata["acceptance_criteria"] = [
            "Feature implemented and tested",
            "Documentation updated",
            "User acceptance testing passed",
        ]
    elif classification.request_type.value == "methodology_change":
        metadata["rationale"] = "TBD - please specify rationale"
        metadata["applies_to"] = "All team members"
        metadata["section"] = "General Guidelines"
    elif classification.request_type.value == "hybrid":
        # Hybrid gets both feature and methodology metadata
        metadata["business_value"] = "TBD - please specify business value"
        metadata["estimated_effort"] = "TBD - to be estimated during planning"
        metadata["acceptance_criteria"] = [
            "Feature implemented and tested",
            "Methodology documented and communicated",
        ]
        metadata["rationale"] = "TBD - please specify rationale"
        metadata["applies_to"] = "All team members"

    return metadata

def extract_title(text: str) -> str:
    """Extract title from user input."""
    text = text.strip()
    prefixes_to_remove = [
        "i want to ",
        "i need to ",
        "we should ",
        "can we ",
        "please ",
        "could you ",
    ]

    lower_text = text.lower()
    for prefix in prefixes_to_remove:
        if lower_text.startswith(prefix):
            text = text[len(prefix):]
            break

    # Capitalize first letter
    text = text[0].upper() + text[1:] if text else text

    # Take first sentence or truncate to 80 chars
    first_sentence = text.split(".")[0]
    if len(first_sentence) > 80:
        first_sentence = first_sentence[:77] + "..."

    return first_sentence
```

---

#### 8. `notifications/` - Warning Notification System

**Responsibility**: Create user warnings and notifications.

**`warning_notifier.py`** (100 LOC):
```python
from coffee_maker.cli.notifications import NotificationDB

class WarningNotifier:
    """Manages user warning notifications."""

    def __init__(self):
        self.db = NotificationDB()

    def warn_user(
        self,
        title: str,
        message: str,
        priority: str = "high",
        context: Optional[Dict] = None,
        play_sound: bool = True,
    ) -> int:
        """Create a warning notification for the user."""
        try:
            notif_id = self.db.create_notification(
                type="warning",
                title=title,
                message=message,
                priority=priority,
                context=context,
                play_sound=play_sound,
            )

            logger.info(f"User warning created: {title} (ID: {notif_id})")
            return notif_id

        except Exception as e:
            logger.error(f"Failed to create warning notification: {e}")
            logger.warning(f"USER WARNING: {title} - {message}")
            return -1
```

---

## Technical Details

### Migration Strategy

**Phase 1: Create New Module Structure (Day 1)**
1. Create `coffee_maker/cli/ai/` directory structure
2. Implement `BaseProvider` interface
3. Extract providers: `APIProvider`, `CLIProvider`
4. Add tests for provider abstraction

**Phase 2: Extract Support Components (Day 2)**
5. Extract `ClassifierIntegration` and `clarification.py`
6. Extract `UserStoryExtractor`, `UserStoryAnalyzer`, `prioritizer.py`
7. Extract `StreamHandler`
8. Extract `PromptBuilder`, `metadata_extractor.py`
9. Extract `WarningNotifier`
10. Add tests for each component

**Phase 3: Refactor Core Service (Day 3)**
11. Refactor `AIService` to use extracted components
12. Update imports to use new module paths
13. Ensure backward compatibility with existing API
14. Run full test suite

**Phase 4: Update Consumers (Day 3)**
15. Update imports in consuming modules:
    - `coffee_maker/cli/chat_interface.py`
    - `coffee_maker/cli/roadmap_cli.py`
    - Tests
16. Deprecate old imports with warnings

**Phase 5: Documentation & Cleanup (Day 3)**
17. Update documentation
18. Remove old `ai_service.py` file
19. Final testing and verification

### Backward Compatibility

**Public API remains unchanged**:
```python
# Old import (still works)
from coffee_maker.cli.ai_service import AIService, AIResponse

# New import (preferred)
from coffee_maker.cli.ai import AIService, AIResponse
```

**All existing methods preserved**:
- `process_request()`
- `process_request_stream()`
- `classify_intent()`
- `extract_user_story()`
- `generate_prioritization_question()`
- `analyze_user_story_impact()`
- `check_available()`
- `classify_user_request()`
- `warn_user()`
- `generate_technical_spec()`

---

## Testing Strategy

### Unit Tests

**Per Component**:
```python
# tests/unit/cli/ai/test_providers.py
def test_api_provider_execute():
    """Test API provider execution."""
    provider = APIProvider(model="claude-3-5-haiku-20241022", max_tokens=1000, api_key="test")
    response = provider.execute("system prompt", [{"role": "user", "content": "test"}])
    assert response.success

# tests/unit/cli/ai/test_classifier_integration.py
def test_classifier_integration():
    """Test classifier integration."""
    integration = ClassifierIntegration()
    result = integration.classify("I want to add email notifications")
    assert result.request_type.value == "feature_request"

# tests/unit/cli/ai/test_user_story_extractor.py
def test_extract_user_story():
    """Test user story extraction."""
    extractor = UserStoryExtractor(mock_provider)
    story = extractor.extract("As a developer, I want to deploy on GCP")
    assert story["role"] == "developer"
```

### Integration Tests

**Full Service Workflow**:
```python
# tests/integration/test_ai_service.py
def test_ai_service_process_request_with_classification():
    """Test full request processing with classification."""
    service = AIService(use_claude_cli=False)
    response = service.process_request(
        "I want to add email notifications",
        context={"roadmap_summary": {}},
        history=[]
    )

    assert response.message
    assert response.metadata["classification"]["request_type"] == "feature_request"
```

### Characterization Tests

**Capture Current Behavior**:
```python
def test_current_behavior_extract_user_story():
    """Characterization test: capture current behavior before refactoring."""
    service = AIService()
    story = service.extract_user_story("I want to deploy on GCP")

    # Assert current output
    assert story is not None
    assert "role" in story
    assert "want" in story
```

**Run these tests BEFORE refactoring, ensure they pass AFTER refactoring.**

---

## Rollout Plan

### Timeline

- **Day 1**: Create module structure, extract providers, add tests
- **Day 2**: Extract support components, add tests
- **Day 3**: Refactor core service, update consumers, documentation

**Total Effort**: 3 days

### Rollback Plan

If issues arise:
1. Keep old `ai_service.py` file until fully verified
2. Use feature flags to toggle between old/new implementations
3. Monitor error rates in production
4. Roll back to old implementation if >5% error rate increase

---

## Risks & Mitigations

### Risk 1: Breaking Existing Consumers

**Likelihood**: Medium
**Impact**: High

**Mitigation**:
- Maintain backward compatibility with old imports
- Add deprecation warnings for old imports
- Run full test suite before merging
- Use feature flags for gradual rollout

### Risk 2: Provider Interface Changes

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Define clear `BaseProvider` interface
- Add integration tests for both API and CLI providers
- Verify with production traffic before deprecating old code

### Risk 3: Performance Degradation

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Benchmark old vs new implementation
- Ensure no significant performance regression (<10% slower acceptable)
- Profile hot paths if issues detected

---

## Success Metrics

**Before Refactoring**:
- 1 file: `ai_service.py` (1,269 LOC)
- 1 class: `AIService` (18 methods)
- Cognitive complexity: HIGH
- Test coverage: ~60%

**After Refactoring**:
- 17 files (average ~109 LOC each)
- 10 classes (average ~3-4 methods each)
- Cognitive complexity: LOW (each file focused on single responsibility)
- Test coverage: >80% (easier to test isolated components)

**Key Improvements**:
- ✅ All files <200 LOC (target achieved)
- ✅ Clear separation of concerns
- ✅ Easier to test (isolated components)
- ✅ Easier to extend (add new providers, classifiers, etc.)
- ✅ Better code reuse
- ✅ Reduced coupling

---

## Related Work

- **SPEC-063**: Break down chat_interface.py (similar complexity)
- **ADR-001**: Use Mixins Pattern (composition over inheritance)
- **ADR-004**: Code Quality Improvement Strategy (simplification first)
- **REFACTORING_BACKLOG**: P0 Item #2

---

## Implementation Notes

### Component Dependencies

```
AIService (coordinator)
├── Provider (API or CLI)
├── ClassifierIntegration
├── DocumentUpdaterIntegration
├── UserStoryExtractor
├── UserStoryAnalyzer
├── StreamHandler
├── PromptBuilder
└── WarningNotifier
```

**All dependencies injected via constructor** (enables testing with mocks).

### File Organization

```python
# coffee_maker/cli/ai/__init__.py
"""AI service module for natural language understanding."""

from coffee_maker.cli.ai.service import AIService, AIResponse
from coffee_maker.cli.ai.providers.base import BaseProvider
from coffee_maker.cli.ai.providers.api_provider import APIProvider
from coffee_maker.cli.ai.providers.cli_provider import CLIProvider

__all__ = ["AIService", "AIResponse", "BaseProvider", "APIProvider", "CLIProvider"]
```

### Deprecation Warnings

```python
# coffee_maker/cli/ai_service.py (old file)
import warnings

warnings.warn(
    "coffee_maker.cli.ai_service is deprecated. Use coffee_maker.cli.ai instead.",
    DeprecationWarning,
    stacklevel=2
)

from coffee_maker.cli.ai import AIService, AIResponse

__all__ = ["AIService", "AIResponse"]
```

---

## Open Questions

1. **Should we add a plugin system for providers?**
   - Would enable community-contributed providers (Gemini, OpenAI, local models)
   - Requires provider registry and discovery mechanism
   - Decision: Defer to Phase 2 (keep simple for now)

2. **Should classification be mandatory or optional?**
   - Current: Optional (backward compatibility)
   - Future: Could be mandatory for better UX
   - Decision: Keep optional for now, evaluate after US-021 Phase 3

3. **Should we use dependency injection framework?**
   - Current: Manual constructor injection
   - Alternative: Use framework like `injector` or `di`
   - Decision: Manual injection sufficient for now (avoid added complexity)

---

## Approval

**Pending approval from code_developer** for implementation.

Once approved, code_developer will:
1. Create feature branch: `refactor/break-down-ai-service`
2. Implement according to this spec
3. Add comprehensive tests
4. Update documentation
5. Create PR for review

---

## Version History

- **v1.0** (2025-10-17): Initial draft by architect agent
