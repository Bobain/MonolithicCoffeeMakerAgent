# Refactoring Backlog

**Purpose**: Track complexity reduction opportunities across the codebase.

**Updated**: 2025-10-17

**Owner**: architect agent

---

## Priority Matrix

| Priority | Item | Complexity Reduction | Effort | Risk |
|----------|------|---------------------|--------|------|
| P0 | Break down chat_interface.py (1,453 LOC) | CRITICAL | 2-3 days | Medium |
| P0 | Break down ai_service.py (1,269 LOC) | CRITICAL | 2-3 days | Medium |
| P1 | Break down roadmap_editor.py (945 LOC) | HIGH | 1-2 days | Low |
| P1 | Break down spec_generator.py (805 LOC) | HIGH | 1-2 days | Low |
| P1 | Break down story_metrics.py (715 LOC) | HIGH | 1-2 days | Low |
| P1 | Break down document_updater.py (731 LOC) | HIGH | 1-2 days | Low |
| P2 | Break down daemon.py (633 LOC) | MEDIUM | 1 day | Medium |
| P2 | Break down preview_generator.py (603 LOC) | MEDIUM | 1 day | Low |
| P3 | Extract shared error handling utilities | LOW | 4 hours | Low |
| P3 | Extract shared validation utilities | LOW | 4 hours | Low |
| P3 | Consolidate logging setup | LOW | 2 hours | Low |

---

## P0: Critical Refactoring (DO FIRST)

### 1. Break down chat_interface.py (1,453 LOC) ⚠️ CRITICAL

**File**: `coffee_maker/cli/chat_interface.py`

**Current State**:
- **1,453 lines** - nearly 3x the recommended 500 LOC limit
- Contains 3 classes: `DeveloperStatusMonitor`, `ProjectManagerCompleter`, `ChatSession`
- `ChatSession` is a God Class with ~30 methods
- Mixes multiple responsibilities: UI, streaming, commands, bug tracking, daemon communication

**Problems**:
- Hard to test individual components
- Changes in one area can break others
- Cognitive overload when navigating the file
- Violates Single Responsibility Principle

**Recommended Breakdown**:

```
coffee_maker/cli/
├── chat/                           # NEW: Chat system module
│   ├── __init__.py
│   ├── session.py                  # Core ChatSession (200 LOC)
│   ├── status_monitor.py           # DeveloperStatusMonitor (150 LOC)
│   ├── completer.py                # ProjectManagerCompleter (70 LOC)
│   ├── command_handler.py          # Command routing (150 LOC)
│   ├── natural_language.py         # NL processing (200 LOC)
│   ├── display.py                  # UI rendering (150 LOC)
│   ├── daemon_integration.py       # Daemon communication (150 LOC)
│   ├── bug_integration.py          # Bug tracking (100 LOC)
│   └── assistant_integration.py    # Assistant bridge (100 LOC)
```

**Benefits**:
- Each component <200 LOC (easily testable)
- Clear separation of concerns
- Easier to maintain and extend
- Better code reuse

**Effort**: 2-3 days

**Risk**: Medium (requires careful testing of UI interactions)

**Dependencies**: None (can start immediately)

---

### 2. Break down ai_service.py (1,269 LOC) ⚠️ CRITICAL

**File**: `coffee_maker/cli/ai_service.py`

**Current State**:
- **1,269 lines** - 2.5x the recommended limit
- Single `AIService` class with ~25 methods
- Handles: API/CLI integration, classification, document updates, user stories, streaming

**Problems**:
- Too many responsibilities in one class
- Hard to test individual features
- Changes ripple across the file
- Difficult to understand the full scope

**Recommended Breakdown**:

```
coffee_maker/cli/ai/                # NEW: AI service module
├── __init__.py
├── service.py                      # Core AIService (200 LOC)
├── api_client.py                   # API/CLI integration (150 LOC)
├── classifier_integration.py       # Request classification (200 LOC)
├── document_integration.py         # DocumentUpdater integration (200 LOC)
├── user_story_extractor.py         # User story parsing (200 LOC)
├── streaming.py                    # Streaming responses (150 LOC)
├── prompt_builder.py               # System prompt construction (150 LOC)
└── metadata_extractor.py           # Metadata extraction (150 LOC)
```

**Benefits**:
- Each component <200 LOC
- Clear API boundaries
- Easier to add new AI providers (Gemini, OpenAI)
- Better testability

**Effort**: 2-3 days

**Risk**: Medium (requires careful API contract preservation)

**Dependencies**: None (can start immediately)

---

## P1: High Priority Refactoring

### 3. Break down roadmap_editor.py (945 LOC)

**File**: `coffee_maker/cli/roadmap_editor.py`

**Current State**:
- 945 lines (nearly 2x the limit)
- Single `RoadmapEditor` class
- Handles: parsing, editing, status updates, summaries

**Recommended Breakdown**:

```
coffee_maker/cli/roadmap/
├── __init__.py
├── editor.py                       # Core editing API (200 LOC)
├── parser.py                       # ROADMAP parsing (200 LOC)
├── writer.py                       # File writing (150 LOC)
├── status_manager.py               # Status updates (150 LOC)
├── summary_generator.py            # Summaries and analytics (150 LOC)
└── validator.py                    # Validation logic (100 LOC)
```

**Effort**: 1-2 days

**Risk**: Low (well-defined boundaries)

---

### 4. Break down spec_generator.py (805 LOC)

**File**: `coffee_maker/autonomous/spec_generator.py`

**Current State**:
- 805 lines
- Handles: spec generation, task breakdown, time estimation, rendering

**Recommended Breakdown**:

```
coffee_maker/autonomous/spec/
├── __init__.py
├── generator.py                    # Core generation (200 LOC)
├── task_breakdown.py               # AI task breakdown (200 LOC)
├── time_estimator.py               # Time estimation (150 LOC)
├── phase_grouper.py                # Phase grouping (150 LOC)
└── markdown_renderer.py            # Markdown output (150 LOC)
```

**Effort**: 1-2 days

**Risk**: Low (clear functional boundaries)

---

### 5. Break down story_metrics.py (715 LOC)

**File**: `coffee_maker/autonomous/story_metrics.py`

**Current State**:
- 715 lines
- Handles: story parsing, duration extraction, confidence scoring

**Recommended Breakdown**:

```
coffee_maker/autonomous/metrics/
├── __init__.py
├── story_parser.py                 # Story parsing (200 LOC)
├── duration_extractor.py           # Duration extraction (200 LOC)
├── confidence_scorer.py            # Confidence scoring (150 LOC)
└── aggregator.py                   # Aggregation (150 LOC)
```

**Effort**: 1-2 days

**Risk**: Low

---

### 6. Break down document_updater.py (731 LOC)

**File**: `coffee_maker/cli/document_updater.py`

**Current State**:
- 731 lines
- Handles: document updates, template rendering, file I/O

**Recommended Breakdown**:

```
coffee_maker/cli/documents/
├── __init__.py
├── updater.py                      # Core updater (200 LOC)
├── template_engine.py              # Template rendering (200 LOC)
├── file_manager.py                 # File I/O operations (150 LOC)
└── validator.py                    # Update validation (150 LOC)
```

**Effort**: 1-2 days

**Risk**: Low

---

## P2: Medium Priority Refactoring

### 7. Break down daemon.py (633 LOC)

**File**: `coffee_maker/autonomous/daemon.py`

**Current State**:
- 633 lines (still over limit)
- Already uses mixins, but base class is still large

**Recommended Action**:
- Further extract workflow orchestration logic
- Create separate workflow modules
- Keep daemon.py as thin coordinator

**Effort**: 1 day

**Risk**: Medium (critical path code)

---

### 8. Break down preview_generator.py (603 LOC)

**File**: `coffee_maker/cli/preview_generator.py`

**Current State**:
- 603 lines
- Handles: preview generation, diff rendering, formatting

**Recommended Breakdown**:

```
coffee_maker/cli/preview/
├── __init__.py
├── generator.py                    # Core preview (200 LOC)
├── diff_renderer.py                # Diff rendering (200 LOC)
└── formatter.py                    # Format output (200 LOC)
```

**Effort**: 1 day

**Risk**: Low

---

## P3: Low Priority Refactoring (Quick Wins)

### 9. Extract shared error handling utilities (4 hours)

**Problem**: Error handling code duplicated across multiple files

**Solution**:
```
coffee_maker/utils/
├── error_handlers.py               # Common error handling
└── exceptions.py                   # Custom exceptions
```

**Files to Consolidate**:
- `coffee_maker/cli/error_handler.py` (176 LOC)
- Duplicated try/except blocks across CLI modules

**Benefits**:
- Consistent error handling
- Reduced duplication
- Easier to add error tracking

---

### 10. Extract shared validation utilities (4 hours)

**Problem**: Validation logic scattered across modules

**Solution**:
```
coffee_maker/utils/
└── validators.py                   # Input validation utilities
```

**Examples**:
- Priority name validation
- File path validation
- User story format validation

---

### 11. Consolidate logging setup (2 hours)

**Problem**: Logging configuration duplicated

**Solution**:
```
coffee_maker/utils/
└── logging_config.py               # Centralized logging setup
```

---

## Refactoring Guidelines

**When breaking down a large file**:

1. **Identify Responsibilities**: List all the things the file does
2. **Create Module Directory**: `coffee_maker/[area]/[module]/`
3. **Extract Components**: Each component <200 LOC
4. **Maintain Public API**: Keep backward compatibility
5. **Add Tests**: Test each new module independently
6. **Update Imports**: Gradually migrate imports
7. **Document Changes**: Update docs and ADRs

**Testing Strategy**:
- Write tests BEFORE refactoring (characterization tests)
- Ensure tests pass after each extraction
- Add new tests for isolated components
- Verify no regressions

**Rollout Plan**:
- One file at a time
- Create feature branch per refactoring
- Get code review before merging
- Update documentation with each change

---

## Technical Sprint Planning

### Sprint 1 (Week 1): Critical Files
- [ ] SPEC-056: Break down chat_interface.py
- [ ] SPEC-057: Break down ai_service.py

### Sprint 2 (Week 2): High Priority
- [ ] Break down roadmap_editor.py
- [ ] Break down spec_generator.py

### Sprint 3 (Week 3): Continued High Priority
- [ ] Break down story_metrics.py
- [ ] Break down document_updater.py

### Sprint 4 (Week 4): Medium Priority
- [ ] Break down daemon.py
- [ ] Break down preview_generator.py

### Sprint 5 (Week 5): Quick Wins
- [ ] Extract error handling utilities
- [ ] Extract validation utilities
- [ ] Consolidate logging setup

---

## Success Metrics

**Target**:
- No files >500 LOC
- No classes >300 LOC
- No methods >100 LOC
- Test coverage >80%

**Current Progress**:
- Files >500 LOC: **10** (see list above)
- Target by end of Sprint 5: **0**

---

## Notes

- This backlog is **living** - updated twice per week by architect
- Priority P0 items should start ASAP
- P1-P3 can be scheduled based on team capacity
- Each refactoring creates a new SPEC in `docs/architecture/specs/`
- Each completed refactoring updates this document

---

**Last Review**: 2025-10-17 (Initial Creation)
**Next Review**: 2025-10-19 (Friday)
