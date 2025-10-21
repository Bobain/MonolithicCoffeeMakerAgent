# ADR-005: Modular CLI Architecture

**Status**: Accepted
**Date**: 2025-10-17
**Author**: architect agent

---

## Context

The `coffee_maker/cli/` directory has grown to contain several monolithic files:

- `chat_interface.py` - **1,453 LOC** (3x limit)
- `ai_service.py` - **1,269 LOC** (2.5x limit)
- `roadmap_editor.py` - **945 LOC** (2x limit)
- `document_updater.py` - **731 LOC** (1.5x limit)

These files violate our **500 LOC per file** guideline and cause:

1. **Cognitive Overload**: Difficult to understand the full scope
2. **Testing Challenges**: Hard to test individual components in isolation
3. **Change Risk**: Changes in one area can break others
4. **Code Reuse**: Difficult to reuse components
5. **Onboarding**: New developers overwhelmed by file size

### Current Problems

**chat_interface.py (1,453 LOC)**:
- Mixes UI rendering, command routing, streaming, bug tracking, daemon communication
- God Class `ChatSession` with ~30 methods
- Three classes in one file (`DeveloperStatusMonitor`, `ProjectManagerCompleter`, `ChatSession`)

**ai_service.py (1,269 LOC)**:
- Single `AIService` class with ~25 methods
- Handles API/CLI integration, classification, document updates, user stories, streaming
- Difficult to extend for new AI providers

**roadmap_editor.py (945 LOC)**:
- Handles parsing, editing, status updates, summaries all in one class
- Hard to test individual operations

---

## Decision

We will adopt a **modular architecture** for the CLI layer, breaking down monolithic files into focused, single-responsibility modules.

### Architectural Principles

1. **Single Responsibility**: Each module does ONE thing well
2. **<200 LOC per File**: Target module size for maintainability
3. **Clear Boundaries**: Well-defined interfaces between modules
4. **Testability**: Each module can be tested in isolation
5. **Composability**: Modules can be easily combined

### Module Organization Pattern

```
coffee_maker/cli/
├── [feature]/                      # Feature-based module
│   ├── __init__.py                 # Public API
│   ├── [component1].py             # Component 1 (<200 LOC)
│   ├── [component2].py             # Component 2 (<200 LOC)
│   └── [component3].py             # Component 3 (<200 LOC)
```

### Refactoring Plan

#### Phase 1: Chat Interface (SPEC-056)

**Before**:
```
coffee_maker/cli/
└── chat_interface.py (1,453 LOC)
```

**After**:
```
coffee_maker/cli/chat/
├── __init__.py                     # Public API
├── session.py                      # Core ChatSession (200 LOC)
├── status_monitor.py               # DeveloperStatusMonitor (150 LOC)
├── completer.py                    # ProjectManagerCompleter (70 LOC)
├── command_handler.py              # Command routing (150 LOC)
├── natural_language.py             # NL processing (200 LOC)
├── display.py                      # UI rendering (150 LOC)
├── daemon_integration.py           # Daemon communication (150 LOC)
├── bug_integration.py              # Bug tracking (100 LOC)
└── assistant_integration.py        # Assistant bridge (100 LOC)
```

#### Phase 2: AI Service (SPEC-057)

**Before**:
```
coffee_maker/cli/
└── ai_service.py (1,269 LOC)
```

**After**:
```
coffee_maker/cli/ai/
├── __init__.py                     # Public API
├── service.py                      # Core AIService (200 LOC)
├── api_client.py                   # API/CLI integration (150 LOC)
├── classifier_integration.py       # Request classification (200 LOC)
├── document_integration.py         # DocumentUpdater integration (200 LOC)
├── user_story_extractor.py         # User story parsing (200 LOC)
├── streaming.py                    # Streaming responses (150 LOC)
├── prompt_builder.py               # System prompt construction (150 LOC)
└── metadata_extractor.py           # Metadata extraction (150 LOC)
```

#### Phase 3: Roadmap Editor

**Before**:
```
coffee_maker/cli/
└── roadmap_editor.py (945 LOC)
```

**After**:
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

#### Phase 4: Other Large Files

- `document_updater.py` → `coffee_maker/cli/documents/`
- `preview_generator.py` → `coffee_maker/cli/preview/`

---

## Consequences

### Positive

1. **Maintainability**: Each module <200 LOC, easy to understand
2. **Testability**: Can test each component in isolation
3. **Reusability**: Components can be used in different contexts
4. **Extensibility**: Easy to add new features without touching existing code
5. **Onboarding**: New developers can understand one module at a time
6. **Collaboration**: Multiple developers can work on different modules simultaneously
7. **Code Review**: Smaller, focused PRs are easier to review

### Negative

1. **Initial Effort**: Requires 2-3 weeks to refactor all monolithic files
2. **Import Changes**: Existing code needs import updates
3. **Testing**: Need to write new tests for isolated components
4. **Documentation**: Need to update docs with new structure
5. **Risk**: Could introduce regressions if not carefully tested

### Mitigation Strategies

1. **Characterization Tests**: Write tests BEFORE refactoring to prevent regressions
2. **Backward Compatibility**: Keep old imports working during transition
3. **Incremental Rollout**: One file at a time, merge after each refactoring
4. **Code Review**: Get thorough review of each refactoring PR
5. **Documentation**: Update architectural docs with each change

---

## Alternatives Considered

### Alternative 1: Leave As-Is

**Pros**:
- No effort required
- No risk of regressions

**Cons**:
- Technical debt continues to grow
- Harder to onboard new developers
- Testing remains difficult
- Changes become more risky over time

**Rejected**: Unsustainable long-term

---

### Alternative 2: Strict Class Extraction (No Module Directories)

**Pros**:
- Simpler file structure
- Fewer directories

**Cons**:
- Still have many files in `coffee_maker/cli/` (becomes cluttered)
- Harder to identify related components
- Less clear boundaries

**Rejected**: Doesn't scale well

---

### Alternative 3: Microservices Architecture

**Pros**:
- Complete isolation
- Can deploy components independently

**Cons**:
- Massive overkill for CLI application
- Adds network complexity
- Deployment complexity

**Rejected**: Way too complex for the problem

---

## Implementation Plan

### Step 1: Create SPEC-056 and SPEC-057

Technical specifications for breaking down the two largest files.

### Step 2: Write Characterization Tests

Before refactoring, ensure tests exist for all public APIs.

### Step 3: Extract Modules Incrementally

One module at a time, ensuring tests pass after each extraction.

### Step 4: Update Imports Gradually

Use `__init__.py` to provide backward compatibility during transition.

### Step 5: Update Documentation

Update `docs/architecture/` with new structure.

### Step 6: Remove Deprecated Imports

After transition period, clean up old imports.

---

## Success Criteria

1. ✅ All files <500 LOC
2. ✅ Each module has single responsibility
3. ✅ Test coverage maintained or improved (>80%)
4. ✅ No regressions in functionality
5. ✅ Clear documentation of new structure
6. ✅ Positive developer feedback on maintainability

---

## Related Documents

- `docs/architecture/REFACTORING_BACKLOG.md` - Full refactoring plan
- `docs/architecture/specs/SPEC-056-break-down-chat-session-class.md` - Chat interface refactoring
- `docs/architecture/specs/SPEC-057-break-down-ai-service.md` - AI service refactoring (to be created)
- `ADR-001-use-mixins-pattern.md` - Related pattern for daemon.py

---

## Notes

- This ADR focuses on CLI layer only
- Similar approach may apply to `coffee_maker/autonomous/` in the future
- Priority P0 refactorings (chat_interface, ai_service) should start ASAP
- Target completion: End of Sprint 4 (4 weeks)

---

**Status**: Accepted (2025-10-17)
**Review Date**: 2025-11-17 (assess progress after 1 month)
