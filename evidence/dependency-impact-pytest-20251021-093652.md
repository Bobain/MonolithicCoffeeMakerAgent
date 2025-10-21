# Dependency Impact Analysis

**Date**: 2025-10-21 09:36
**Package**: pytest
**Migration**: 7.0.0 → 8.0.0
**Risk Level**: HIGH 🟠

## Summary

- **Breaking Changes**: 3
- **Codebase Usages**: 124
- **Migration Risk**: HIGH
- **Estimated Effort**: 2-4 hours

## Breaking Changes

1. Removed deprecated API `old_function()`
2. Changed parameter order in `configure()`
3. Renamed module `old_module` to `new_module`


## Codebase Impact

**Affected Files**: 124

- `coffee_maker/sec_vuln_helper/run_dependencies_tests.py`: if "import pytest" in content or "from pytest" in content:
- `tests/unit/test_dependency_analyzer.py`: import pytest
- `tests/unit/test_scheduling_strategy.py`: import pytest
- `tests/unit/test_request_classifier.py`: import pytest
- `tests/unit/test_status_report_generator.py`: import pytest

_...and 119 more usages_


## Rollout Plan

1. Create feature branch for pytest migration
2. Update dependency in pyproject.toml
3. Run full test suite to identify failures
4. Fix breaking changes one-by-one with focused commits
5. Run integration tests to verify no regressions
6. Request code review from architect
7. Merge to roadmap branch after approval
8. Monitor for 24 hours before marking complete


## Recommendations

1. Review all breaking changes carefully
2. Update tests to reflect new API
3. Test thoroughly before merging
4. Monitor for issues after deployment
