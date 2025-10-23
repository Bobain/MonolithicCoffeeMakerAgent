# Dependency Impact Analysis

**Date**: 2025-10-19 12:41
**Package**: pytest
**Migration**: 7.0.0 → 8.0.0
**Risk Level**: MEDIUM 🟡

## Summary

- **Breaking Changes**: 3
- **Codebase Usages**: 2
- **Migration Risk**: MEDIUM
- **Estimated Effort**: 1-2 hours

## Breaking Changes

1. Removed deprecated API `old_function()`
2. Changed parameter order in `configure()`
3. Renamed module `old_module` to `new_module`


## Codebase Impact

**Affected Files**: 2

- `coffee_maker/autonomous/daemon.py`: import pytest
- `tests/unit/test_daemon.py`: from pytest import SomeClass


## Rollout Plan

1. Update pytest in pyproject.toml
2. Run test suite to identify failures
3. Fix breaking changes
4. Run integration tests
5. Commit and merge to roadmap


## Recommendations

1. Review breaking changes
2. Run full test suite
3. Fix any failures
4. Merge with confidence
