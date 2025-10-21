# ADR-XXX: [Title of Architectural Decision]

**Status**: Proposed | Accepted | Deprecated | Superseded by [ADR-YYY](./ADR-YYY-title.md)

**Date**: YYYY-MM-DD

**Author**: architect agent

**Related Issues**: [Link to GitHub issues or ROADMAP priorities if applicable]

**Related Specs**: [Link to technical specs if applicable]

---

## Context

What is the issue that we're seeing that is motivating this decision or change?

- What is the current situation?
- What problem are we trying to solve?
- What are the forces at play (technical, business, political, social)?
- What constraints do we face?

**Example**:
```
The daemon.py file has grown to 1,592 lines with multiple responsibilities
(git operations, spec management, implementation, status tracking). This makes
the file hard to maintain, test, and understand. We need a way to organize
this complexity while maintaining cohesion.
```

---

## Decision

What is the change that we're proposing and/or doing?

Be specific and concrete. State the decision clearly and unambiguously.

**Example**:
```
We will use the mixins pattern to compose daemon functionality. The daemon
will be split into:
- GitMixin: Git operations (clone, commit, push)
- SpecManagerMixin: Technical spec creation
- ImplementationMixin: Feature implementation
- StatusMixin: Status tracking and reporting

The DevDaemon class will inherit from all mixins and coordinate their usage.
```

---

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive Consequences

List the benefits and improvements:

- **Benefit 1**: Description
- **Benefit 2**: Description
- **Benefit 3**: Description

**Example**:
```
- Better separation of concerns: Each mixin has a single responsibility
- Easier testing: Can test mixins independently
- More maintainable: Smaller files are easier to understand
- Easier to extend: New mixins can be added without changing existing ones
```

### Negative Consequences

List the drawbacks and costs:

- **Drawback 1**: Description
- **Drawback 2**: Description
- **Drawback 3**: Description

**Example**:
```
- Slightly more complex file structure: Multiple files instead of one
- Need to understand composition: Developers must know which mixin provides what
- Potential for naming conflicts: Multiple mixins could define same method
```

### Neutral Consequences

List changes that are neither positive nor negative:

- **Change 1**: Description
- **Change 2**: Description

---

## Alternatives Considered

What other approaches did we consider and why were they rejected?

### Alternative 1: [Name]

**Description**: Brief description of alternative

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Why Rejected**: Explain why this alternative was not chosen

**Example**:
```
### Alternative 1: Inheritance Hierarchy

**Description**: Create a base class with subclasses for each responsibility

**Pros**:
- Clear class hierarchy
- Traditional OOP approach

**Cons**:
- Too rigid: Can only inherit from one parent
- Harder to mix and match responsibilities
- More boilerplate

**Why Rejected**: Doesn't provide the flexibility needed for composing
multiple responsibilities.
```

### Alternative 2: [Name]

**Description**: Brief description of alternative

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Why Rejected**: Explain why this alternative was not chosen

---

## Implementation Notes

How should this decision be implemented?

- What steps are needed?
- What order should they be done in?
- Any special considerations?
- Dependencies on other work?

**Example**:
```
1. Create mixin files in coffee_maker/autonomous/
2. Move relevant methods from daemon.py to each mixin
3. Update DevDaemon class to inherit from all mixins
4. Update tests to test mixins independently
5. Update documentation to explain mixin pattern
```

---

## Validation

How will we know if this decision is working?

- What metrics indicate success?
- What tests validate the decision?
- How long before we reevaluate?

**Example**:
```
Success metrics:
- daemon.py reduced to < 700 lines
- Each mixin has < 400 lines
- Test coverage maintained at > 80%
- No increase in bug reports

Reevaluate in 3 months to assess if pattern is working well.
```

---

## References

Links to relevant resources:

- [Link to discussion or RFC]
- [Link to technical spec]
- [Link to related documentation]
- [Link to research or articles]

**Example**:
```
- Python Mixins: https://realpython.com/inheritance-composition-python/
- PRIORITY 2: Project Manager CLI (motivation for refactoring)
- Code quality analysis showing file size issues
```

---

## History

Track changes to this ADR:

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Created | architect |
| YYYY-MM-DD | Status changed to Accepted | architect |
| YYYY-MM-DD | Added implementation notes | architect |

---

## Notes

Any additional context or information that doesn't fit elsewhere:

- **Risk 1**: Description and mitigation
- **Risk 2**: Description and mitigation
- **Open Questions**: Questions that need answers
- **Future Work**: Related work that could be done later

---

**Remember**: An ADR is a snapshot of a decision at a point in time. It's okay if the decision is later superseded - that's what the "Superseded by" status is for. The important thing is to document WHY decisions were made, so future developers understand the reasoning.
