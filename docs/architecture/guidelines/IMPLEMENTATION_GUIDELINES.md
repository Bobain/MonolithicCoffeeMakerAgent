# Implementation Guidelines

## General Principles
- Follow architectural decisions in docs/architecture/decisions/
- Read specifications in docs/architecture/specs/ before implementing
- Maintain consistency with existing patterns
- Document deviations from architecture

## Review Process
1. Architect creates specification
2. User reviews and approves
3. code_developer reads specification
4. code_developer implements following guidelines
5. Architect reviews implementation

## Coding Standards
- Use Black formatter (88 chars)
- Type hints required
- Comprehensive docstrings
- Unit tests for all new code

## Architecture Patterns
- Singleton for agents (ACEAgent base class)
- Mixins for composable functionality
- Dependency injection over globals
- Interface-based design

## Documentation Requirements
- Update ROADMAP.md for status changes
- Create ADRs for significant decisions
- Update technical specs when deviating
- Comment complex algorithms

## Testing Requirements
- Unit tests: 80% coverage minimum
- Integration tests for cross-component features
- Pytest fixtures for common setups
- Mock external dependencies

## Pre-commit Checklist
- [ ] All tests passing
- [ ] Black formatting applied
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] No unused imports
- [ ] ROADMAP updated
