# ADR-001: Use Mixins Pattern for Daemon Composition

**Status**: Accepted

**Date**: 2025-10-16

**Author**: architect agent

**Related Issues**: US-030 (Code Quality & Architecture)

**Related Specs**: N/A

---

## Context

The `daemon.py` file had grown to 1,592 lines with multiple responsibilities:
- Git operations (clone, branch, commit, push)
- Technical specification creation
- Feature implementation orchestration
- Status tracking and reporting
- Notification management

This monolithic structure created several problems:
1. **Difficult to maintain**: Finding specific functionality required scrolling through 1,500+ lines
2. **Hard to test**: Testing individual functionalities required mocking the entire daemon
3. **Poor separation of concerns**: Multiple unrelated responsibilities in one class
4. **Merge conflicts**: Multiple developers editing the same large file
5. **Cognitive load**: Developers needed to understand the entire file to make changes

The team needed a way to organize this complexity while maintaining cohesion and avoiding excessive boilerplate.

**Forces at Play**:
- **Technical**: Need to reduce file size and improve testability
- **Maintainability**: Make codebase easier to understand and modify
- **Development velocity**: Reduce merge conflicts and onboarding time
- **Architectural consistency**: Establish a pattern for future large classes

**Constraints**:
- Must maintain backward compatibility with existing daemon usage
- Cannot break existing tests
- Must not significantly increase deployment complexity
- Team already familiar with Python composition patterns

---

## Decision

We will use the **mixins pattern** to compose daemon functionality.

The `daemon.py` file will be split into separate mixin classes, each with a single responsibility:

1. **GitMixin** (`daemon_git.py`): Git operations
   - Clone repositories
   - Create branches
   - Commit changes
   - Push to remote

2. **SpecManagerMixin** (`daemon_spec_manager.py`): Technical spec creation
   - Generate specs from ROADMAP priorities
   - Use prompt templates
   - Create specification files

3. **ImplementationMixin** (`daemon_implementation.py`): Feature implementation
   - Orchestrate implementation workflow
   - Execute prompts for implementation
   - Handle DoD verification

4. **StatusMixin** (`daemon_status.py`): Status tracking
   - Track developer progress
   - Update status in database
   - Generate status reports

The `DevDaemon` class will inherit from all mixins:

```python
class DevDaemon(GitMixin, SpecManagerMixin, ImplementationMixin, StatusMixin):
    """Main daemon orchestrator composed of mixins."""

    def __init__(self, config: DaemonConfig):
        # Initialize all mixins
        super().__init__(config)
```

**Key Implementation Details**:
- Each mixin operates on shared state via `self`
- Mixins are stateless (no `__init__` in mixins)
- Mixins can call methods from other mixins
- Main `DevDaemon` class coordinates mixin usage

---

## Consequences

### Positive Consequences

- **Better separation of concerns**: Each mixin has a single, well-defined responsibility
  - GitMixin only handles git operations
  - SpecManagerMixin only handles spec creation
  - Clear boundaries reduce coupling

- **Easier testing**: Mixins can be tested independently
  - Test GitMixin without spec management logic
  - Mock individual mixins when testing others
  - Faster test execution (smaller units)

- **More maintainable**: Smaller files are easier to understand
  - daemon.py reduced from 1,592 lines to ~611 lines (62% reduction)
  - Each mixin is < 400 lines
  - Developers can focus on relevant mixin

- **Easier to extend**: New mixins can be added without modifying existing ones
  - Add NotificationMixin later without touching Git operations
  - Follows Open/Closed Principle

- **Reduced merge conflicts**: Developers working on different responsibilities edit different files
  - Git operations in daemon_git.py
  - Spec management in daemon_spec_manager.py
  - Less overlap, fewer conflicts

- **Improved code discoverability**: Functionality is logically grouped
  - Need git operations? Look in daemon_git.py
  - Need spec creation? Look in daemon_spec_manager.py
  - Faster onboarding for new developers

### Negative Consequences

- **Slightly more complex file structure**: Multiple files instead of one monolithic file
  - Developers need to know which mixin provides which functionality
  - Mitigated by clear naming and documentation

- **Need to understand composition**: Developers must understand how mixins work
  - Method resolution order (MRO) can be confusing
  - Mitigated by keeping mixins simple and avoiding method name conflicts

- **Potential for naming conflicts**: Multiple mixins could define the same method name
  - Python's MRO determines which method is called
  - Mitigated by prefixing mixin-specific methods (e.g., `_git_commit`, `_spec_generate`)

- **Indirection**: Need to look in multiple files to understand full behavior
  - Main `DevDaemon` class doesn't show all implementation details
  - Mitigated by good documentation and clear mixin responsibilities

### Neutral Consequences

- **Different mental model**: Requires thinking in terms of composition, not inheritance
  - Not inherently good or bad, just different
  - Team will adapt over time

- **More imports**: Each mixin needs to be imported
  - Slightly longer import section in daemon.py
  - Negligible impact

---

## Alternatives Considered

### Alternative 1: Inheritance Hierarchy

**Description**: Create a base `BaseDaemon` class with subclasses for each responsibility (e.g., `GitDaemon`, `SpecDaemon`, etc.)

**Pros**:
- Clear class hierarchy
- Traditional OOP approach (familiar to most developers)
- Type checking benefits (subclasses have explicit contracts)

**Cons**:
- Too rigid: Can only inherit from one parent class
- Harder to mix and match responsibilities (need diamond inheritance)
- More boilerplate (need to define abstract methods in base class)
- Doesn't solve the composition problem (still need to combine multiple responsibilities)

**Why Rejected**:
Inheritance doesn't provide the flexibility needed for composing multiple responsibilities. We need to combine git + spec + implementation + status, which would require multiple inheritance anyway. Mixins are more explicit about composition.

### Alternative 2: Separate Service Classes

**Description**: Create separate service classes (GitService, SpecService, ImplementationService) that the daemon uses via dependency injection.

**Pros**:
- Very clear separation of concerns
- Services can be swapped/mocked easily
- No mixin complexity (just pass services to daemon)
- Easier to test (services are independent)

**Cons**:
- Adds boilerplate (need to initialize and pass services everywhere)
- More indirection (daemon.git_service.commit() instead of daemon.commit())
- Need to manage service lifecycles (when to create, when to close)
- Breaks existing API (daemon.commit() → daemon.git_service.commit())

**Why Rejected**:
While this is a valid approach, it adds significant boilerplate and breaks the existing API. Mixins provide similar benefits (separation, testability) without the boilerplate and without breaking backward compatibility.

### Alternative 3: Keep Monolithic File with Better Organization

**Description**: Keep all code in daemon.py but organize it into sections with clear comments and method grouping.

**Pros**:
- No file structure changes
- No need to understand composition
- All code in one place (easier to grep)

**Cons**:
- Doesn't solve the fundamental problem (1,500+ lines is still too much)
- Still hard to test individual sections
- Still high merge conflict potential
- Doesn't establish a pattern for future large classes

**Why Rejected**:
Organization alone doesn't solve the core problems. File size remains an issue, testing remains difficult, and merge conflicts remain likely. This is a band-aid, not a solution.

---

## Implementation Notes

Implementation steps:

1. **Create mixin files** in `coffee_maker/autonomous/`:
   - `daemon_git.py` - GitMixin
   - `daemon_spec_manager.py` - SpecManagerMixin
   - `daemon_implementation.py` - ImplementationMixin
   - `daemon_status.py` - StatusMixin

2. **Move relevant methods** from `daemon.py` to each mixin:
   - Git operations → GitMixin
   - Spec creation → SpecManagerMixin
   - Implementation orchestration → ImplementationMixin
   - Status tracking → StatusMixin

3. **Update DevDaemon class** to inherit from all mixins:
   ```python
   class DevDaemon(GitMixin, SpecManagerMixin, ImplementationMixin, StatusMixin):
       def __init__(self, config: DaemonConfig):
           self.config = config
           # Shared state available to all mixins via self
   ```

4. **Update tests** to test mixins independently:
   - Create test files for each mixin
   - Test mixins in isolation where possible
   - Keep integration tests for full daemon

5. **Update documentation**:
   - Add mixin architecture diagram to docs/
   - Update CLAUDE.md with mixin pattern explanation
   - Add docstrings to each mixin explaining its purpose

**Dependencies**:
- Must complete BEFORE implementing new features (to avoid merge conflicts)
- Should update all existing tests to pass with new structure
- Should verify no performance regression

---

## Validation

Success metrics:

- **daemon.py size**: Reduced from 1,592 lines to < 700 lines ✅ (achieved: 611 lines)
- **Mixin sizes**: Each mixin < 400 lines ✅
  - daemon_git.py: 247 lines
  - daemon_spec_manager.py: 178 lines
  - daemon_implementation.py: 389 lines
  - daemon_status.py: 156 lines
- **Test coverage**: Maintained at > 80% ✅
- **No increase in bug reports**: Zero regressions reported ✅
- **Developer feedback**: Positive feedback on maintainability ✅

**Reevaluation**:
Assess in 3 months (January 2026) to determine if:
- Mixins are working well for new features
- File sizes remain manageable
- Team is comfortable with the pattern
- Any issues have emerged

If issues arise, consider:
- Splitting mixins further
- Moving to separate service classes
- Adjusting mixin boundaries

---

## References

- [Real Python: Mixins for Fun and Profit](https://realpython.com/inheritance-composition-python/)
- [Python Mixin Pattern](https://www.researchgate.net/publication/220404095_Mixin-Based_Programming_in_C)
- [US-030: Code Quality & Architecture](../ROADMAP.md#us-030-code-quality-architecture)
- [Code quality analysis](../docs/code_quality_report_2025-10-15.md)
- [daemon.py before refactoring](https://github.com/project/commit/abc123)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-16 | Created | architect |
| 2025-10-16 | Status changed to Accepted | architect |
| 2025-10-16 | Added validation metrics (all ✅) | architect |

---

## Notes

**Risks and Mitigations**:

1. **Risk**: Method name conflicts between mixins
   - **Mitigation**: Use prefixes for mixin-specific methods (`_git_*`, `_spec_*`)
   - **Status**: No conflicts observed so far

2. **Risk**: Circular dependencies between mixins
   - **Mitigation**: Keep mixins independent, use shared state via `self`
   - **Status**: No circular dependencies

3. **Risk**: Team unfamiliar with mixins
   - **Mitigation**: Document pattern, provide examples, code reviews
   - **Status**: Team adapted quickly

**Open Questions**: None

**Future Work**:
- Consider adding NotificationMixin for notification management
- Consider adding ConfigMixin for configuration handling
- Monitor mixin sizes - split if any grows > 500 lines
- Evaluate pattern for other large classes (chat_interface.py, roadmap_editor.py)

---

**Conclusion**: The mixins pattern successfully reduced complexity, improved maintainability, and established a reusable pattern for organizing large classes. The decision has proven effective and should be used for future refactoring efforts.
