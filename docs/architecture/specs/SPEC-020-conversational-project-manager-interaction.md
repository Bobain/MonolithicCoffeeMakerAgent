# SPEC-020: Conversational Project Manager Interaction

**Status**: 📝 Draft
**Created**: 2025-10-20
**User Story**: US-020
**Estimated Effort**: 4-5 days
**Business Value**: ⭐⭐⭐⭐⭐ Critical

---

## Table of Contents

1. [Overview](#overview)
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

## Overview

### Problem Statement

Currently, when users initiate a new user story, the interaction feels:
- ❌ **Robotic**: "Please answer questions 1-6"
- ❌ **Inflexible**: All questions at once, no adaptation to user feedback
- ❌ **One-directional**: PM asks, user answers, no true dialogue
- ❌ **Disconnected**: No confirmation of understanding before proceeding

### Desired Solution

Transform project_manager into a conversational agent that:
- ✅ **Natural**: Collaborative flow, human-like interaction
- ✅ **Adaptive**: Reconsiders questions when user corrects or clarifies
- ✅ **One-by-one**: Single question at a time, not overwhelming batches
- ✅ **Confirmatory**: Shows draft before adding to ROADMAP

### Strategic Value

This transformation is critical for user experience:
- Makes PM feel human, not robotic
- Reduces friction in user story creation
- Higher quality specifications (better questions → better answers)
- 85%+ approval rate on first-try drafts (target metric)

### Scope

**When This Applies**:
- User initiates new user story via chat: `"user story: As a [role] I want [goal]..."`
- PM needs to gather requirements through clarifying questions

**Out of Scope**:
- Non-user-story conversations (status updates, queries, etc.)
- Existing non-conversational PM commands
- ROADMAP manipulation (that remains programmatic)

---

## Prerequisites & Dependencies

###Required Components (Already Exist)

1. **project_manager Agent** (`coffee_maker/autonomous/agents/project_manager.py`)
   - Chat interface capability
   - ROADMAP.md write access
   - User story template generation

2. **NotificationManager** (`coffee_maker/utils/notifications.py`)
   - For sending conversational responses to user
   - Sound notifications for user attention (CFR-009 compliant)

3. **AI Provider Integration** (`coffee_maker/utils/ai_provider.py`)
   - LLM access for generating questions, detecting corrections, etc.

### Dependencies on Other User Stories

- **US-006**: Chat UX (foundational requirement for conversational flow)
- **Section 3.1**: User role definition (COLLABORATION_METHODOLOGY.md)

### External Dependencies

- **Langfuse**: Observability for conversation tracking
- **Poetry**: Python environment
- **Black**: Code formatting

---

## Architecture Overview

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                      User Interface                                │
│                   (project_manager chat)                           │
└────────────────┬──────────────────────────────────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────────────────────────────────┐
│              ConversationOrchestrator                              │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  - Detect conversation intent (new story/answer/           │   │
│  │    correction/approval)                                    │   │
│  │  - Route to appropriate handler                            │   │
│  │  - Manage conversation lifecycle                           │   │
│  └────────────────────────────────────────────────────────────┘   │
└──┬──────────────────────┬──────────────────────┬───────────────────┘
   │                      │                      │
   ▼                      ▼                      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│Conversation  │  │ Question     │  │  Draft               │
│StateManager  │  │ Generator    │  │  Formatter           │
│              │  │              │  │                      │
│- Track state │  │- Generate Q's│  │- Create draft spec   │
│- Store       │  │- Adapt on    │  │- Format for approval │
│  answers     │  │  correction  │  │- Handle edits        │
│- Handle      │  │- LLM-powered │  │                      │
│  corrections │  │              │  │                      │
└──────────────┘  └──────────────┘  └──────────────────────┘
       │                  │                     │
       └──────────────────┴─────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │  Conversational      │
              │  Tone Enforcer       │
              │                      │
              │ - Validate messages  │
              │ - Add transitions    │
              │ - Prevent anti-      │
              │   patterns           │
              └──────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │   ROADMAP.md         │
              │   (Final Storage)    │
              └──────────────────────┘
```

### Component Responsibilities

1. **ConversationOrchestrator**: High-level conversation management
2. **ConversationStateManager**: State tracking, correction handling
3. **QuestionGenerator**: LLM-powered question generation (adaptive)
4. **DraftFormatter**: User story draft creation and formatting
5. **ConversationalToneEnforcer**: Anti-pattern detection, tone validation

---

## Component Specifications

*Note: Due to length, I'm providing high-level signatures. Full implementation details available in ROADMAP US-020 section.*

### 1. ConversationStateManager

**Location**: `coffee_maker/autonomous/conversation/conversation_state_manager.py`

**Key Methods**:
- `__init__(initial_user_story: str)` - Initialize conversation
- `get_next_question() -> Optional[str]` - Get next question
- `record_answer(answer: str)` - Record user's answer
- `handle_correction(correction: str, new_questions: List[str])` - Handle corrections
- `set_draft(draft: str)` - Store draft for review
- `mark_complete()` - Mark conversation complete

**State Tracking**:
- Current question index
- All Q&A pairs
- Corrections history
- Conversation phase (INIT, QUESTIONING, DRAFT_REVIEW, COMPLETE)

### 2. QuestionGenerator

**Location**: `coffee_maker/autonomous/conversation/question_generator.py`

**Key Methods**:
- `generate_initial_questions(user_story: str) -> List[str]` - Generate 3-7 questions
- `generate_questions_after_correction(original, correction, prev_answers) -> List[str]`

**LLM Integration**:
- Uses AIProvider for question generation
- Structured prompts with clear instructions
- Parses numbered list responses

### 3. DraftFormatter

**Location**: `coffee_maker/autonomous/conversation/draft_formatter.py`

**Key Methods**:
- `generate_draft(user_story_text: str, qa_pairs: Dict) -> str` - Create draft
- `update_draft(existing_draft: str, requested_changes: str) -> str` - Update draft

**Draft Format**:
- Follows ROADMAP.md template
- Includes: User Story, Scope, Acceptance Criteria, Implementation Plan, Effort Estimate

### 4. ConversationalToneEnforcer

**Location**: `coffee_maker/autonomous/conversation/tone_enforcer.py`

**Key Methods**:
- `validate_message(message: str)` - Check for robotic patterns
- `add_question_transition(question: str, idx: int) -> str` - Add conversational transitions
- `get_correction_acknowledgment() -> str` - Random acknowledgment
- `format_draft_for_approval(draft: str) -> str` - Format with approval prompt

**Anti-Patterns Detected**:
- "Please answer questions 1-6"
- "Q1:", "Q2:" formatting
- Batched questions

### 5. ConversationOrchestrator

**Location**: `coffee_maker/autonomous/conversation/orchestrator.py`

**Key Methods**:
- `handle_user_input(user_input: str)` - Main entry point
- `_start_new_conversation(user_story_text: str)` - Start new story
- `_handle_answer(answer: str)` - Process answer
- `_handle_correction(correction: str)` - Process correction
- `_handle_approval_response(response: str)` - Process approval
- `_approve_and_add_to_roadmap()` - Add to ROADMAP.md

**Intent Detection**:
- New user story patterns
- Correction patterns ("sorry", "actually", "I meant")
- Approval responses ("yes", "no", "cancel")

---

## Data Flow Diagrams

### Happy Path Flow

```
User: "user story: As a dev I want syntax highlighting"
  ↓
ConversationOrchestrator detects: New user story
  ↓
QuestionGenerator generates 5 questions via LLM
  ↓
ConversationStateManager stores questions
  ↓
Q1 asked with transition: "Let me ask some questions..."
  ↓
User answers Q1
  ↓
ConversationStateManager records answer, advances to Q2
  ↓
Q2 asked with transition: "Got it! Next question..."
  ↓
[Repeat for Q3, Q4, Q5]
  ↓
All questions answered
  ↓
DraftFormatter generates draft from Q&A via LLM
  ↓
Draft shown with approval prompt
  ↓
User: "yes"
  ↓
Draft added to ROADMAP.md
  ↓
Notification: "✅ Added to ROADMAP.md!"
```

### Correction Flow

```
User starts story → Q1 asked → User answers
  ↓
User: "Sorry, the real story is [corrected story]"
  ↓
Orchestrator detects correction pattern
  ↓
ToneEnforcer provides acknowledgment: "Ah, I understand now!"
  ↓
QuestionGenerator generates NEW questions for corrected story
  ↓
StateManager preserves relevant answers, updates questions
  ↓
Next question asked (adapted to correction)
  ↓
[Continue with new questions]
```

---

## Implementation Plan

### Phase 1: Core Components (1.5 days, ~13 hours)

**Tasks**:
1. Create ConversationStateManager (4h)
2. Create QuestionGenerator (3h)
3. Implement correction detection (2h)
4. Add answer preservation logic (2h)
5. Write unit tests (2h)

**Deliverables**:
- `conversation_state_manager.py` with 8+ unit tests
- `question_generator.py` with 5+ unit tests

---

### Phase 2: Conversation Flow (1 day, ~9 hours)

**Tasks**:
1. Create DraftFormatter (2h)
2. Create ConversationalToneEnforcer (2h)
3. Implement one-by-one flow in Orchestrator (3h)
4. Add conversational transitions (1h)
5. Write integration tests (1h)

**Deliverables**:
- `draft_formatter.py` with 4+ unit tests
- `tone_enforcer.py` with 8+ unit tests
- `orchestrator.py` with basic flow

---

### Phase 3: Draft Approval Workflow (0.5 day, ~6 hours)

**Tasks**:
1. Implement draft display (2h)
2. Add approval detection (1h)
3. Handle "changes needed" workflow (2h)
4. Write tests (1h)

**Deliverables**:
- Complete approval/rejection handling
- 8+ approval flow tests

---

### Phase 4: Anti-Pattern Prevention (0.5 day, ~5 hours)

**Tasks**:
1. Verify anti-pattern detection (completed in Phase 2)
2. Add conversational validation (1h)
3. Add tone validation tests (2h)
4. Manual testing (2h)

**Deliverables**:
- 10+ anti-pattern tests
- Zero robotic patterns in production

---

### Phase 5: Integration & Testing (1.5 days, ~13 hours)

**Tasks**:
1. Integrate into ProjectManager agent (3h)
2. Add ROADMAP.md writing (2h)
3. Add session persistence (2h)
4. End-to-end testing (4h)
5. Bug fixes and refinement (2h)

**Deliverables**:
- Integration with project_manager
- 5 E2E test scenarios
- Session save/load functionality

---

### Phase 6: Documentation (0.5 day, ~5 hours)

**Tasks**:
1. Write Section 4.5 in COLLABORATION_METHODOLOGY.md (3h)
2. Add examples from testing (1h)
3. Cross-reference documentation (1h)

**Deliverables**:
- Section 4.5: "Conversational Interaction Patterns"
- 3 example interactions
- Version bump to 1.9

---

**Total Effort**: 4-5 days (51 hours + 20% buffer = 61 hours)

---

## Testing Strategy

### Unit Tests (25+ tests)

- **ConversationStateManager** (8 tests): State transitions, corrections, history
- **QuestionGenerator** (5 tests): Question generation, parsing, correction adaptation
- **DraftFormatter** (4 tests): Draft generation, updates, formatting
- **ConversationalToneEnforcer** (8 tests): Pattern detection, transitions, variety

### Integration Tests (10+ tests)

- **Orchestrator** (10 tests): Happy path, correction path, cancellation, intent detection

### End-to-End Tests (5 tests)

1. Simple story (no corrections)
2. Story with mid-conversation correction
3. Story with draft changes requested
4. Story cancellation
5. Multiple stories in sequence

### Performance Tests (2 tests)

1. Question generation time: <3 seconds
2. Draft generation time: <5 seconds

---

## Security Considerations

### 1. Input Validation

**Risk**: Malicious user input could exploit LLM

**Mitigation**:
- Sanitize user input (remove code blocks, HTML tags)
- Limit input length (max 10,000 chars)
- Validate ROADMAP.md path (prevent directory traversal)

### 2. LLM Prompt Injection

**Risk**: User could inject malicious prompts

**Mitigation**:
- Use structured prompts with clear delimiters
- Treat user input as data, not instructions
- Validate LLM responses

### 3. File System Access

**Risk**: Writing to ROADMAP.md could corrupt file

**Mitigation**:
- Atomic writes (temp file + rename)
- Backup before every write
- File locking to prevent concurrent writes
- Path validation

### 4. Sensitive Data Exposure

**Risk**: User might include secrets in user story

**Mitigation**:
- Detect patterns (API keys, passwords, tokens)
- Warn user if potential secrets detected
- Don't log sensitive data to Langfuse

### 5. CFR-009 Compliance

**Note**: ConversationOrchestrator is used by user_listener ONLY (not background agents)
- All notifications use `sound=True` (allowed for user_listener)
- Background agents MUST NOT use this component

---

## Performance Requirements

### Response Time Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Question generation (LLM) | <3 seconds | User waiting |
| Draft generation (LLM) | <5 seconds | User waiting |
| Answer recording | <100ms | Should be instant |
| Correction handling | <4 seconds | 1s ack + 3s questions |
| State persistence | <200ms | Background operation |

### Scalability

- **Single user system**: One conversation at a time
- **LLM rate limits**: 50 requests/min (Claude Sonnet)
- **Memory usage**: <100KB per conversation
- **ROADMAP.md size**: No concerns (currently 1.1MB)

### Monitoring

Use Langfuse to track:
- LLM call duration
- End-to-end conversation duration
- Draft approval rate (target: >85%)

---

## Risk Analysis

### High Risks

#### Risk 1: LLM Hallucination in Questions
- **Impact**: HIGH | **Probability**: MEDIUM
- **Mitigation**: Structured prompts, question count validation, manual review
- **Contingency**: Use predefined question templates with LLM fill-in

#### Risk 2: Correction Detection False Positives
- **Impact**: MEDIUM | **Probability**: MEDIUM
- **Mitigation**: Specific patterns, context change required
- **Contingency**: Add explicit correction command

#### Risk 3: Draft Quality Below Expectations
- **Impact**: HIGH | **Probability**: LOW
- **Mitigation**: Detailed prompts, unlimited revisions, target >85% approval
- **Contingency**: Few-shot prompting with successful examples

### Medium Risks

#### Risk 4: Conversation State Loss on Crash
- **Impact**: MEDIUM | **Probability**: LOW
- **Mitigation**: Session persistence, save after every answer
- **Contingency**: User re-starts conversation

#### Risk 5: ROADMAP.md Corruption
- **Impact**: HIGH | **Probability**: VERY LOW
- **Mitigation**: Atomic writes, backups, file locking
- **Contingency**: Restore from backup or git revert

---

## Success Criteria

### Primary Goals (Must-Have)

#### 1. Conversational Flow ✅
- **Metric**: Human reviewer rates 4-5 out of 5
- **Test**: Transcript review by user
- **Validation**: Questions one-by-one, natural transitions, smooth corrections

#### 2. Adaptive Questioning ✅
- **Metric**: PM generates new questions after correction
- **Test**: E2E Test 2 (correction scenario)
- **Validation**: Draft matches corrected story, not original

#### 3. Anti-Pattern Prevention ✅
- **Metric**: Zero robotic patterns
- **Test**: Automated validation on all messages
- **Validation**: All tests pass tone validation

#### 4. Draft Approval Rate ✅
- **Metric**: >85% approved on first try
- **Test**: 20 real user stories
- **Validation**: 17+ out of 20 approved

#### 5. Technical Implementation ✅
- **Metric**: 40+ tests, 100% passing
- **Validation**: All components implemented and tested

### Secondary Goals (Nice-to-Have)

#### 6. Performance ⚡
- Question generation: <3 seconds
- Draft generation: <5 seconds

#### 7. Documentation 📖
- Section 4.5 in COLLABORATION_METHODOLOGY.md
- 3 example interactions
- Version 1.9

#### 8. User Satisfaction 😊
- User rates 4-5 out of 5
- "Exactly what I expected from PM"

---

## Appendix

### File Structure

```
coffee_maker/autonomous/conversation/
├── __init__.py
├── conversation_state_manager.py
├── question_generator.py
├── draft_formatter.py
├── tone_enforcer.py
├── orchestrator.py
└── conversation_persistence.py

tests/autonomous/conversation/
├── test_conversation_state_manager.py
├── test_question_generator.py
├── test_draft_formatter.py
├── test_tone_enforcer.py
├── test_orchestrator.py
└── test_approval.py

tests/e2e/
└── test_conversational_pm.py
```

### Timeline Summary

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Core Components | 1.5 days | 13 hours |
| Phase 2: Conversation Flow | 1 day | 9 hours |
| Phase 3: Draft Approval | 0.5 day | 6 hours |
| Phase 4: Anti-Patterns | 0.5 day | 5 hours |
| Phase 5: Integration & Testing | 1.5 days | 13 hours |
| Phase 6: Documentation | 0.5 day | 5 hours |
| **Total** | **4-5 days** | **51 hours** |

**Buffer**: 20% (10 hours) for unexpected issues
**Total with Buffer**: **5-6 days** or **61 hours**

---

## Conclusion

This specification provides a comprehensive blueprint for implementing US-020: Conversational Project Manager Interaction.

**Key Features**:
- Natural, human-like dialogue
- Adaptive questioning (responds to corrections)
- Anti-pattern prevention (no robotic tone)
- Draft approval workflow
- 85%+ approval rate target
- <3 second response times

**Next Steps**:
1. Review and approve this spec
2. Create feature branch: `feature/us-020-conversational-pm`
3. Begin Phase 1: Core Components
4. Daily check-ins with architect
5. Code review after each phase
6. Final DoD verification with Puppeteer demo

---

**Spec Author**: architect
**Spec Reviewer**: TBD
**Implementation Lead**: code_developer
**Estimated Start Date**: TBD
**Estimated Completion Date**: TBD (5 days after start)
