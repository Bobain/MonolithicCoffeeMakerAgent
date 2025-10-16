# Refactoring Plans Directory

**Owner**: architect

**Purpose**: architect creates detailed refactoring plans here for code_developer to execute.

## Directory Structure

- `templates/` - Templates for refactoring plans
- `active/` - Currently active refactoring work
- `completed/` - Archived completed refactorings

## Workflow

1. architect monitors code quality weekly
2. architect detects technical debt
3. architect creates refactoring plan in `active/`
4. code_developer executes plan
5. architect moves plan to `completed/` when done

## File Naming

- Active: `REFACTOR_YYYY_MM_DD_description.md`
- Completed: `REFACTOR_YYYY_MM_DD_description_COMPLETED.md`
