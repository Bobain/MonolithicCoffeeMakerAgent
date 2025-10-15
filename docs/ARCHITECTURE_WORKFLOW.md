# Architecture Workflow

**Version**: 1.0
**Date**: 2025-10-15
**Status**: Complete

---

## Overview

The architect agent is responsible for architectural design and technical specifications. This document describes how architect integrates into the development workflow.

---

## Workflow Stages

### Stage 1: User Request
User discusses feature or system change with user_listener

### Stage 2: Architect Analysis
architect receives request and analyzes requirements:
- Functional requirements
- Non-functional requirements
- Constraints
- Dependencies

### Stage 3: Architecture Design
architect designs system architecture:
- Components and interfaces
- Data flow
- Patterns to use
- Technology choices

### Stage 4: Specification Creation
architect creates detailed technical specification:
- File: `docs/architecture/specs/[feature]_spec.md`
- Contains: Requirements, design, implementation plan, testing strategy

### Stage 5: Decision Documentation
architect documents key decisions:
- File: `docs/architecture/decisions/ADR-XXX-[title].md`
- Contains: Context, decision, consequences, alternatives

### Stage 6: Implementation Guidelines
architect provides guidelines:
- File: `docs/architecture/guidelines/[topic]_guidelines.md`
- Contains: Principles, patterns, best practices

### Stage 7: code_developer Implementation
code_developer reads specifications and implements:
- Follows architectural design
- Adheres to guidelines
- Implements according to spec

### Stage 8: Architect Review
architect reviews implementation:
- Verifies architectural compliance
- Checks adherence to guidelines
- Approves or requests changes

---

## Interaction Patterns

### Pattern 1: New Feature
```
User: "I need a caching layer"
    ↓
user_listener → architect
    ↓
architect: Analyzes requirements, designs architecture
    ↓
architect: Creates docs/architecture/specs/caching_layer_spec.md
    ↓
architect: Creates ADR-015-redis-for-caching.md
    ↓
code_developer: Reads spec and implements
    ↓
architect: Reviews implementation
```

### Pattern 2: Architectural Decision
```
User: "Should we use REST or GraphQL?"
    ↓
user_listener → architect
    ↓
architect: Analyzes trade-offs
    ↓
architect: Creates ADR-016-rest-vs-graphql.md
    ↓
architect: Provides recommendation with rationale
```

### Pattern 3: Implementation Question
```
code_developer: "How should I structure the authentication module?"
    ↓
architect: Reviews docs/architecture/guidelines/
    ↓
architect: Provides guidance based on existing patterns
```

---

## Document Types

### Technical Specifications
- **Purpose**: Detailed design for implementation
- **Location**: `docs/architecture/specs/`
- **Template**: `SPEC_TEMPLATE.md`
- **Audience**: code_developer (primary), all team (reference)

### Architectural Decision Records (ADRs)
- **Purpose**: Document key architectural decisions
- **Location**: `docs/architecture/decisions/`
- **Template**: `ADR_TEMPLATE.md`
- **Audience**: All team members

### Implementation Guidelines
- **Purpose**: Best practices for implementation
- **Location**: `docs/architecture/guidelines/`
- **Audience**: code_developer (primary)

---

## Best Practices

### For architect
1. **Design Before Implementation**: Always complete specifications before code_developer starts
2. **Document Decisions**: Create ADR for every significant architectural decision
3. **Provide Context**: Explain WHY, not just WHAT
4. **Consider Alternatives**: Document alternatives considered and why rejected
5. **Review Implementation**: Verify code_developer followed architectural design

### For code_developer
1. **Read Specifications**: Always read relevant specs in docs/architecture/specs/
2. **Follow Guidelines**: Adhere to implementation guidelines
3. **Ask Questions**: Consult architect if design unclear
4. **Document Deviations**: If you must deviate from architecture, document why
5. **Request Review**: Ask architect to review implementation

### For project_manager
1. **Strategic vs Technical**: Create strategic specs, architect creates technical specs
2. **Coordinate Workflow**: Ensure architect completes design before implementation
3. **Track Decisions**: Reference ADRs in roadmap and project documentation

---

## Tools and Automation

### architect Commands (through user_listener)
- `/architect design [feature]` - Create architectural design
- `/architect spec [feature]` - Create technical specification
- `/architect adr [title]` - Create Architectural Decision Record
- `/architect review [feature]` - Review implementation

### Integration with ACE
- architect inherits from ACEAgent (automatic ACE)
- All architectural decisions traced
- Playbook evolves with architectural patterns
- Feedback loop improves design quality

---

## Examples

### Example 1: New Feature Architecture
```
docs/architecture/specs/caching_layer_spec.md
docs/architecture/decisions/ADR-015-redis-for-caching.md
docs/architecture/guidelines/caching_best_practices.md
```

### Example 2: System Refactoring
```
docs/architecture/specs/modular_architecture_refactor_spec.md
docs/architecture/decisions/ADR-016-microservices-vs-monolith.md
docs/architecture/guidelines/module_boundaries.md
```

---

## Related Documentation
- `.claude/CLAUDE.md` - Agent responsibilities
- `docs/DOCUMENT_OWNERSHIP_MATRIX.md` - File ownership
- `docs/AGENT_ROLES_AND_BOUNDARIES.md` - Agent roles

---

**Maintained By**: project_manager
**Review Frequency**: Quarterly or when adding new agents
**Next Review**: 2026-01-15
