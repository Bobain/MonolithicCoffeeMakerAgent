# Refactoring Recommendations

**Owner**: code-sanitizer
**Purpose**: Code quality analysis and refactoring recommendations

## Directory Structure

```
docs/refacto/
├── README.md (this file)
└── refactoring_analysis_YYYY-MM-DD_HH-MM-SS.md (generated reports)
```

## Workflow

1. **code_developer** makes code changes
2. **code-sanitizer** wakes up automatically
3. **code-sanitizer** analyzes code quality
4. **code-sanitizer** writes report to `docs/refacto/`
5. **project_manager** reads report
6. **project_manager** decides: refactor vs implement

## Report Contents

Each report includes:
- Complexity analysis (cyclomatic complexity)
- Code duplication detection
- Style compliance (PEP 8)
- Refactoring recommendations (prioritized)
- Suggested patterns (Extract Function, DRY, etc.)

## For project_manager

Use these reports to make priority decisions:
- **High-priority refactoring items** → Schedule refactoring sprint
- **Medium-priority items** → Include in next sprint
- **Low-priority items** → Backlog for future cleanup

## Tools Used

- **radon**: Complexity metrics
- **flake8**: PEP 8 compliance
- **pylint**: Code quality
- **.gemini.styleguide.md**: Style guidelines

---

**Last Updated**: 2025-10-15
**Maintained By**: code-sanitizer
