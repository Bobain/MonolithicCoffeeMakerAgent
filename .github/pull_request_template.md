# Pull Request

## Description

[Provide a brief description of the changes in this PR]

## Related Issue/User Story

- Closes #[issue number]
- Implements: US-[number] - [name]
- ROADMAP Priority: [priority number]

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Changes Made

### Code Changes
- [List main code changes]
- [Component A: what changed]
- [Component B: what changed]

### Tests Added/Modified
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed
- Test coverage: [X%] (aim for >80%)

### Documentation Changes
- [ ] Code comments added (explain WHY, not WHAT)
- [ ] Technical documentation updated

## Developer Documentation (US-011 Requirement)

**Required**: Developer must create documentation per template: `docs/templates/DEVELOPER_DOCUMENTATION_TEMPLATE.md`

- [ ] **User Guide** created (how to use the feature)
  - File: [path or section]
  - Includes: Quick start, common use cases, examples

- [ ] **API Reference** created (if feature has commands/functions)
  - File: [path or section]
  - Includes: All parameters, return values, error codes

- [ ] **Troubleshooting** section added (common errors + solutions)
  - File: [path or section]
  - Includes: Symptoms, causes, solutions

- [ ] **Changelog entry** added (what changed)
  - File: docs/CHANGELOG.md
  - Includes: Breaking changes (if any), migration guide

- [ ] **Technical Spec updated** with implementation results
  - File: [path to spec]
  - Includes: What was built, deviations, how it works

**Why This Matters**: Assistants need these docs to help users. If assistants can't help users with your feature, the feature isn't done!

**N/A Reason**: [If documentation not applicable, explain why]

## Definition of Done

### Functional Criteria
- [ ] All acceptance criteria met (100%)
- [ ] Feature works end-to-end
- [ ] Edge cases handled
- [ ] Error handling implemented

### Technical Criteria
- [ ] Code follows project conventions (Black, type hints)
- [ ] No code duplication
- [ ] Performance acceptable (<1s for UI operations)
- [ ] Cross-platform tested (if applicable)

### Testing Criteria
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Manual testing completed
- [ ] Test coverage >80% for new code
- [ ] All existing tests passing

### Quality Checks
- [ ] Pre-commit hooks pass (black, autoflake, trailing-whitespace)
- [ ] No lint errors
- [ ] Type hints added where appropriate
- [ ] Security considerations addressed

### Git Criteria
- [ ] Branch is up to date with main
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts

### User Validation (if applicable)
- [ ] User tested the feature
- [ ] User approved the implementation
- [ ] User signed off on acceptance criteria

## How to Test

### Setup
```bash
# Steps to set up test environment
```

### Test Cases
1. **Test Case 1**: [Description]
   - Steps: [Step-by-step]
   - Expected: [Expected result]
   - Actual: [Actual result]

2. **Test Case 2**: [Description]
   - Steps: [Step-by-step]
   - Expected: [Expected result]
   - Actual: [Actual result]

### Manual Testing Evidence (if applicable)
- [ ] Screenshots attached (for UI changes)
- [ ] Puppeteer verification completed (for web features)
- [ ] Console logs checked (no errors)

## Screenshots (if applicable)

[Add screenshots showing before/after, UI changes, or test results]

## Breaking Changes

[List any breaking changes and migration steps, or write "None"]

## Performance Impact

[Describe any performance implications, or write "None"]

## Security Considerations

[Describe any security implications, or write "None"]

## Deployment Notes

[Any special deployment steps or considerations, or write "Standard deployment"]

## Checklist Before Requesting Review

- [ ] Self-review completed
- [ ] Code commented (explain WHY, not WHAT)
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] Pre-commit hooks pass
- [ ] No console errors or warnings
- [ ] Feature tested in clean environment

## Additional Context

[Add any other context about the PR here]

---

**Generated with Claude Code** 🤖

Co-Authored-By: Claude <noreply@anthropic.com>
