# SPEC-023: Clear, Intuitive Module Hierarchy

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: [US-023: Clear, Intuitive Module Hierarchy](../../roadmap/ROADMAP.md#us-023)

**Related ADRs**:
- ADR-013: Dependency Pre-Approval Matrix
- Future: ADR-TBD: Module Organization Principles

**Assigned To**: code_developer

---

## Executive Summary

This specification describes the technical design for restructuring the `coffee_maker` codebase module hierarchy to improve library usability and developer experience. The restructuring will move 33 misplaced files from `langfuse_observe/` to semantically correct locations, creating a clear separation between observability, core LLM functionality, and utilities. This will reduce onboarding time, improve code discoverability, and establish clear module organization principles for future development.

---

## Problem Statement

### Current Situation

The `coffee_maker` codebase suffers from poor module organization that hinders library adoption and developer productivity:

**Critical Issues**:

1. **Misleading Directory Names**:
   - `langfuse_observe/` contains 39 files, but only 5 (13%) actually use the `@observe` decorator
   - The directory name suggests observability, but contains core LLM abstractions, rate limiting, strategies, and utilities

2. **Unclear Code Ownership**:
   - New developers cannot find reusable code at first sight
   - No clear entry points for library consumers
   - Mixed concerns in single directory (observability + LLM core + utilities)

3. **Scattered Utilities**:
   - Token estimation, HTTP pooling mixed with observability code
   - No logical grouping of related functionality
   - Difficult to understand dependencies

4. **Duplicate Code**:
   - `langfuse_observe/exceptions.py` duplicates `coffee_maker/exceptions.py`
   - Potential overlap between `langfuse_observe/llm_providers/` and `ai_providers/`

5. **Poor Developer Experience**:
   - Library users struggle to find where to start
   - Import paths don't reflect logical organization
   - No clear module hierarchy documentation

**Impact Metrics**:
- **Onboarding Time**: New contributors need 3-4 hours to understand structure
- **Code Discovery**: Developers spend 20-30 min finding reusable components
- **Import Confusion**: 87% of files in observability dir don't observe
- **Technical Debt**: Growing misplacement as new features added

### Goal

Transform the module hierarchy to achieve:

1. **Semantic Clarity**: Directory names accurately reflect contents
2. **Logical Grouping**: Related code lives together
3. **Clear Entry Points**: New users know where to start
4. **Minimal Duplication**: Consolidate scattered utilities
5. **Library Usability**: Enable easy consumption as a library

**Success Metrics**:
- 100% of files in correct semantic locations
- Onboarding time reduced by 60% (3-4h → 1-1.5h)
- Code discovery time reduced by 75% (20-30min → 5-8min)
- Zero duplicate exception definitions
- Clear module documentation with visual diagrams

### Non-Goals

What we are explicitly NOT doing:

1. **NOT changing functionality**: This is a pure refactoring (behavior unchanged)
2. **NOT rewriting code**: Moving files only, no code rewrites
3. **NOT changing external APIs**: Public APIs remain backward compatible
4. **NOT optimizing performance**: Performance is not a goal of this refactoring
5. **NOT adding new features**: Only organizational improvements

---

## Requirements

### Functional Requirements

1. **FR-1**: All files currently in `langfuse_observe/` must be categorized correctly
2. **FR-2**: Create new `coffee_maker/llm/` directory for core LLM abstractions
3. **FR-3**: Rename `langfuse_observe/` to `observability/` (clearer name)
4. **FR-4**: Keep only `@observe`-decorated files in `observability/`
5. **FR-5**: Move utilities to appropriate locations (`utils/`, `llm/utils/`)
6. **FR-6**: Consolidate duplicate exception definitions
7. **FR-7**: Create clear `__init__.py` exports for each package
8. **FR-8**: Update all import statements across codebase
9. **FR-9**: Maintain backward compatibility via deprecation warnings (if needed)
10. **FR-10**: Document new module hierarchy with visual diagrams

### Non-Functional Requirements

1. **NFR-1**: **Zero Breaking Changes**: All existing code continues to work
2. **NFR-2**: **Test Coverage**: 100% of tests pass after refactoring
3. **NFR-3**: **Import Performance**: Import times unchanged or improved
4. **NFR-4**: **Documentation**: Clear migration guide for external users
5. **NFR-5**: **Observability**: All Langfuse traces continue working
6. **NFR-6**: **Rollback Safety**: Changes can be reverted in <30 minutes
7. **NFR-7**: **Code Review**: All changes pass pre-commit hooks (black, autoflake)
8. **NFR-8**: **Maintainability**: Establish principles to prevent future misplacement

### Constraints

- **MUST** maintain backward compatibility (library may have external users)
- **MUST** pass all existing tests (156 tests currently passing)
- **MUST** follow Python style guide (`.gemini/styleguide.md`)
- **MUST** use `git mv` for moves (preserve history)
- **MUST** work on `roadmap` branch only (CFR-013)
- **SHOULD** complete in 3-4 days (estimated effort)
- **SHOULD** minimize import path changes for frequently-used modules

---

## Proposed Solution

### High-Level Approach

**Three-Phase Restructuring**:

**Phase 1: Analysis & Planning** (0.5 days)
- Audit all 39 files in `langfuse_observe/`
- Categorize by semantic purpose (observability, LLM core, utilities, etc.)
- Create detailed file-by-file migration plan
- Identify all import dependencies (estimated 100+ files affected)
- Get user approval for structure

**Phase 2: Core Restructuring** (2 days)
- Create new directory structure (`llm/`, `llm/rate_limiting/`, `llm/strategies/`, etc.)
- Move 33 misplaced files to correct locations using `git mv`
- Rename `langfuse_observe/` → `observability/`
- Consolidate exception definitions
- Create clear `__init__.py` exports

**Phase 3: Update Imports & Validation** (1 day)
- Update all import statements (100+ files)
- Run full test suite continuously
- Update documentation (README, ARCHITECTURE.md, getting started guide)
- Create visual diagram of new structure
- Final validation and commit

### Architecture Diagram

**Current Structure (Problematic)**:
```
coffee_maker/
├── langfuse_observe/                # ❌ Misleading name, mixed concerns
│   ├── llm.py                       # Core LLM (no @observe)
│   ├── llm_tools.py                 # Utilities (no @observe)
│   ├── llm_config.py                # Config (no @observe)
│   ├── scheduled_llm.py             # Scheduling (no @observe)
│   ├── auto_picker_llm_refactored.py # Selection (no @observe)
│   ├── builder.py                   # Builder pattern (no @observe)
│   ├── rate_limiter.py              # Rate limiting (no @observe)
│   ├── global_rate_tracker.py       # Tracking (no @observe)
│   ├── cost_budget.py               # Budgeting (no @observe)
│   ├── http_pool.py                 # HTTP utilities (no @observe)
│   ├── response_parser.py           # Parsing (no @observe)
│   ├── token_estimator.py           # Token counting (no @observe)
│   ├── exceptions.py                # Duplicates coffee_maker/exceptions.py
│   ├── agents.py                    # ✅ Uses @observe
│   ├── cost_calculator.py           # ✅ Uses @observe
│   ├── retry.py                     # ✅ Uses @observe (but duplicate in strategies/)
│   ├── tools.py                     # ✅ Uses @observe
│   ├── langfuse_logger.py           # Langfuse integration (no @observe)
│   ├── strategies/                  # Strategies (no @observe)
│   │   ├── retry.py                 # Duplicate of parent retry.py?
│   │   ├── fallback.py
│   │   ├── scheduling.py
│   │   ├── context.py
│   │   └── metrics.py
│   ├── analytics/                   # Mixed (some @observe)
│   │   ├── analyzer.py              # ✅ Uses @observe
│   │   ├── analyzer_sqlite.py       # Database (no @observe)
│   │   ├── exporter.py              # Export (no @observe)
│   │   ├── exporter_sqlite.py       # SQLite (no @observe)
│   │   ├── models.py                # Models (no @observe)
│   │   ├── models_sqlite.py         # SQLite models (no @observe)
│   │   ├── db_schema.py             # Schema (no @observe)
│   │   └── config.py                # Config (no @observe)
│   └── llm_providers/               # Providers (no @observe)
│       ├── openai.py
│       ├── gemini.py
│       └── __init__.py
├── ai_providers/                    # ❓ Overlap with llm_providers?
├── utils/                           # Existing utilities
└── exceptions.py                    # Duplicated in langfuse_observe/

Total: 39 files in langfuse_observe/
Files using @observe: 5 (13%)
Files NOT using @observe: 34 (87%)
```

**Proposed Structure (Clear Separation)**:
```
coffee_maker/
├── observability/                   # ✅ Clear name, focused purpose
│   ├── __init__.py                  # Export @observe-decorated classes
│   ├── agents.py                    # ✅ Uses @observe
│   ├── cost_calculator.py           # ✅ Uses @observe
│   ├── retry.py                     # ✅ Uses @observe (keep this, remove strategies/retry.py)
│   ├── tools.py                     # ✅ Uses @observe
│   ├── langfuse_logger.py           # Langfuse integration
│   └── analytics/                   # Analytics with @observe
│       ├── __init__.py
│       ├── analyzer.py              # ✅ Uses @observe
│       ├── exporter.py              # Export traces
│       ├── exporter_sqlite.py       # SQLite exporter
│       ├── models.py                # Data models
│       ├── models_sqlite.py         # SQLite models
│       ├── db_schema.py             # Database schema
│       └── config.py                # Analytics config
│
├── llm/                             # ✅ NEW: Core LLM abstractions
│   ├── __init__.py                  # Export main LLM classes
│   ├── llm.py                       # Core LLM class
│   ├── llm_tools.py                 # LLM utilities
│   ├── llm_config.py                # LLM configuration
│   ├── scheduled_llm.py             # Scheduled execution
│   ├── auto_picker.py               # LLM selection (renamed from auto_picker_llm_refactored.py)
│   ├── builder.py                   # Builder pattern
│   ├── rate_limiting/               # ✅ Rate limiting subsystem
│   │   ├── __init__.py
│   │   ├── rate_limiter.py          # Rate limiting logic
│   │   ├── global_rate_tracker.py   # Global rate tracking
│   │   └── cost_budget.py           # Budget management
│   ├── strategies/                  # ✅ LLM strategies
│   │   ├── __init__.py
│   │   ├── fallback.py              # Fallback strategies
│   │   ├── scheduling.py            # Scheduling strategies
│   │   ├── context.py               # Context management
│   │   └── metrics.py               # Metrics strategies
│   └── providers/                   # ✅ LLM providers
│       ├── __init__.py
│       ├── openai.py                # OpenAI provider
│       └── gemini.py                # Gemini provider
│
├── utils/                           # ✅ Existing + moved utilities
│   ├── __init__.py
│   ├── http_pool.py                 # Moved from langfuse_observe
│   ├── response_parser.py           # Moved from langfuse_observe
│   ├── token_estimator.py           # Moved from langfuse_observe
│   ├── logging.py                   # Already exists
│   ├── time.py                      # Already exists
│   └── file_io.py                   # Already exists
│
├── exceptions.py                    # ✅ Consolidated (merged langfuse_observe/exceptions.py)
└── ai_providers/                    # ✅ Existing (evaluate overlap with llm/providers/)

Summary:
- observability/: 12 files (all related to observability)
- llm/: 17 files (all core LLM functionality)
- utils/: 9 files (general utilities)
- exceptions.py: Single source of truth for exceptions
```

**Migration Flow**:
```
┌─────────────────────────────┐
│  Phase 1: Analysis          │
│  - Audit files              │
│  - Plan migrations          │
│  - Get approval             │
└─────────────┬───────────────┘
              │
              v
┌─────────────────────────────┐
│  Phase 2: Restructure       │
│  - Create new dirs          │
│  - git mv files             │
│  - Update __init__.py       │
│  - Consolidate exceptions   │
└─────────────┬───────────────┘
              │
              v
┌─────────────────────────────┐
│  Phase 3: Update & Validate │
│  - Update imports (100+)    │
│  - Run tests continuously   │
│  - Update docs              │
│  - Final validation         │
└─────────────────────────────┘
```

### Technology Stack

**No new dependencies required**. This is a pure refactoring using existing tools:

- **Python 3.10+**: Existing language version
- **Git**: Use `git mv` to preserve history
- **Black**: Format code after changes
- **Autoflake**: Remove unused imports
- **Pytest**: Validate all tests pass (156 existing tests)
- **Pre-commit hooks**: Ensure code quality

---

## Detailed Design

### Component Design

#### Component 1: File Categorization System

**Responsibility**: Categorize all 39 files in `langfuse_observe/` by semantic purpose

**Categories**:

1. **Category: Observability** (Keep in `observability/`)
   - Files: 5 files using `@observe` decorator
   - `agents.py`, `cost_calculator.py`, `retry.py`, `tools.py`
   - `analytics/analyzer.py` (uses @observe)

2. **Category: Core LLM** (Move to `llm/`)
   - Files: 6 files
   - `llm.py`, `llm_tools.py`, `llm_config.py`, `scheduled_llm.py`, `auto_picker_llm_refactored.py`, `builder.py`

3. **Category: Rate Limiting** (Move to `llm/rate_limiting/`)
   - Files: 3 files
   - `rate_limiter.py`, `global_rate_tracker.py`, `cost_budget.py`

4. **Category: Strategies** (Move to `llm/strategies/`)
   - Files: 4 files (NOT including duplicate retry.py)
   - `strategies/fallback.py`, `strategies/scheduling.py`, `strategies/context.py`, `strategies/metrics.py`

5. **Category: Utilities** (Move to `utils/`)
   - Files: 3 files
   - `http_pool.py`, `response_parser.py`, `token_estimator.py`

6. **Category: Providers** (Move to `llm/providers/`)
   - Files: 3 files
   - `llm_providers/openai.py`, `llm_providers/gemini.py`, `llm_providers/__init__.py`

7. **Category: Analytics** (Keep in `observability/analytics/`)
   - Files: 7 files
   - All files in `analytics/` subdirectory

8. **Category: Integration** (Keep in `observability/`)
   - Files: 1 file
   - `langfuse_logger.py`

9. **Category: Exceptions** (Merge to `coffee_maker/exceptions.py`)
   - Files: 1 file
   - `exceptions.py`

10. **Category: Duplicates** (Remove)
    - Files: 1 file
    - `strategies/retry.py` (duplicate of parent `retry.py`)

**Total**: 34 unique files (39 - 5 duplicates)

**Implementation**:
```python
# Script: scripts/audit_langfuse_observe.py
"""Audit langfuse_observe/ directory for @observe usage."""

import ast
import os
from pathlib import Path
from typing import List, Dict, Set

def find_observe_decorator(file_path: Path) -> bool:
    """Check if file uses @observe decorator."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'observe':
                        return True
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name) and decorator.func.id == 'observe':
                            return True
        return False
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return False

def categorize_files() -> Dict[str, List[Path]]:
    """Categorize all files in langfuse_observe/."""
    base = Path("coffee_maker/langfuse_observe")
    categories = {
        "observability": [],
        "core_llm": [],
        "rate_limiting": [],
        "strategies": [],
        "utilities": [],
        "providers": [],
        "analytics": [],
        "integration": [],
        "exceptions": [],
        "duplicates": []
    }

    for file_path in base.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue

        uses_observe = find_observe_decorator(file_path)
        relative = file_path.relative_to(base)

        # Categorization logic
        if uses_observe:
            categories["observability"].append(file_path)
        elif "llm_providers" in str(relative):
            categories["providers"].append(file_path)
        elif "analytics" in str(relative):
            categories["analytics"].append(file_path)
        elif "strategies" in str(relative):
            if file_path.name == "retry.py":
                categories["duplicates"].append(file_path)
            else:
                categories["strategies"].append(file_path)
        elif file_path.name in ["llm.py", "llm_tools.py", "llm_config.py", "scheduled_llm.py", "auto_picker_llm_refactored.py", "builder.py"]:
            categories["core_llm"].append(file_path)
        elif file_path.name in ["rate_limiter.py", "global_rate_tracker.py", "cost_budget.py"]:
            categories["rate_limiting"].append(file_path)
        elif file_path.name in ["http_pool.py", "response_parser.py", "token_estimator.py"]:
            categories["utilities"].append(file_path)
        elif file_path.name == "exceptions.py":
            categories["exceptions"].append(file_path)
        elif file_path.name == "langfuse_logger.py":
            categories["integration"].append(file_path)

    return categories

def generate_migration_plan(categories: Dict[str, List[Path]]) -> str:
    """Generate detailed migration plan."""
    plan = "# File-by-File Migration Plan\n\n"

    for category, files in categories.items():
        plan += f"## {category.replace('_', ' ').title()} ({len(files)} files)\n\n"
        for file_path in sorted(files):
            plan += f"- `{file_path}`\n"
        plan += "\n"

    return plan

if __name__ == "__main__":
    categories = categorize_files()
    plan = generate_migration_plan(categories)

    output_path = Path("docs/US-023_MIGRATION_PLAN.md")
    with open(output_path, 'w') as f:
        f.write(plan)

    print(f"Migration plan written to {output_path}")
```

#### Component 2: Directory Structure Creator

**Responsibility**: Create new directory structure with proper `__init__.py` exports

**Interface**:
```python
# Script: scripts/create_new_structure.py
"""Create new directory structure for module reorganization."""

from pathlib import Path
from typing import List

def create_directory_structure() -> None:
    """Create new directory structure."""
    directories = [
        "coffee_maker/llm",
        "coffee_maker/llm/rate_limiting",
        "coffee_maker/llm/strategies",
        "coffee_maker/llm/providers",
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.touch()

    print("Directory structure created successfully")

def create_init_exports() -> None:
    """Create __init__.py exports for each package."""

    # coffee_maker/llm/__init__.py
    llm_init = '''"""Core LLM abstractions and utilities.

This module provides the main LLM classes, configuration, scheduling,
and provider integrations.
"""

from coffee_maker.llm.llm import LLM
from coffee_maker.llm.llm_config import LLMConfig
from coffee_maker.llm.scheduled_llm import ScheduledLLM
from coffee_maker.llm.auto_picker import AutoPicker
from coffee_maker.llm.builder import LLMBuilder

__all__ = [
    "LLM",
    "LLMConfig",
    "ScheduledLLM",
    "AutoPicker",
    "LLMBuilder",
]
'''

    # coffee_maker/llm/rate_limiting/__init__.py
    rate_limiting_init = '''"""Rate limiting and cost budget management for LLM calls.

This module provides rate limiting, global rate tracking, and cost budget
management to prevent exceeding API quotas and budgets.
"""

from coffee_maker.llm.rate_limiting.rate_limiter import RateLimiter
from coffee_maker.llm.rate_limiting.global_rate_tracker import GlobalRateTracker
from coffee_maker.llm.rate_limiting.cost_budget import CostBudget

__all__ = [
    "RateLimiter",
    "GlobalRateTracker",
    "CostBudget",
]
'''

    # coffee_maker/llm/strategies/__init__.py
    strategies_init = '''"""LLM execution strategies (fallback, scheduling, context, metrics).

This module provides various strategies for LLM execution including
fallback handling, scheduling, context management, and metrics collection.
"""

from coffee_maker.llm.strategies.fallback import FallbackStrategy
from coffee_maker.llm.strategies.scheduling import SchedulingStrategy
from coffee_maker.llm.strategies.context import ContextStrategy
from coffee_maker.llm.strategies.metrics import MetricsStrategy

__all__ = [
    "FallbackStrategy",
    "SchedulingStrategy",
    "ContextStrategy",
    "MetricsStrategy",
]
'''

    # coffee_maker/llm/providers/__init__.py
    providers_init = '''"""LLM provider integrations (OpenAI, Gemini).

This module provides provider-specific implementations for different
LLM services.
"""

from coffee_maker.llm.providers.openai import OpenAIProvider
from coffee_maker.llm.providers.gemini import GeminiProvider

__all__ = [
    "OpenAIProvider",
    "GeminiProvider",
]
'''

    # coffee_maker/observability/__init__.py
    observability_init = '''"""Observability and tracing with Langfuse integration.

This module provides observability tools for tracking LLM calls,
costs, and performance metrics using the @observe decorator.
"""

from coffee_maker.observability.agents import ObservableAgent
from coffee_maker.observability.cost_calculator import CostCalculator
from coffee_maker.observability.retry import retry_with_observe
from coffee_maker.observability.tools import ObservableTools
from coffee_maker.observability.langfuse_logger import LangfuseLogger

__all__ = [
    "ObservableAgent",
    "CostCalculator",
    "retry_with_observe",
    "ObservableTools",
    "LangfuseLogger",
]
'''

    # Write __init__.py files
    init_files = {
        "coffee_maker/llm/__init__.py": llm_init,
        "coffee_maker/llm/rate_limiting/__init__.py": rate_limiting_init,
        "coffee_maker/llm/strategies/__init__.py": strategies_init,
        "coffee_maker/llm/providers/__init__.py": providers_init,
        "coffee_maker/observability/__init__.py": observability_init,
    }

    for file_path, content in init_files.items():
        Path(file_path).write_text(content)

    print("__init__.py exports created successfully")

if __name__ == "__main__":
    create_directory_structure()
    create_init_exports()
```

#### Component 3: Import Updater

**Responsibility**: Update all import statements across codebase (100+ files)

**Interface**:
```python
# Script: scripts/update_imports.py
"""Update all import statements after module reorganization."""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Import mapping: old path -> new path
IMPORT_MAPPING = {
    # Core LLM
    "from coffee_maker.langfuse_observe.llm import": "from coffee_maker.llm import",
    "from coffee_maker.langfuse_observe.llm_tools import": "from coffee_maker.llm.llm_tools import",
    "from coffee_maker.langfuse_observe.llm_config import": "from coffee_maker.llm.llm_config import",
    "from coffee_maker.langfuse_observe.scheduled_llm import": "from coffee_maker.llm.scheduled_llm import",
    "from coffee_maker.langfuse_observe.auto_picker_llm_refactored import": "from coffee_maker.llm.auto_picker import",
    "from coffee_maker.langfuse_observe.builder import": "from coffee_maker.llm.builder import",

    # Rate limiting
    "from coffee_maker.langfuse_observe.rate_limiter import": "from coffee_maker.llm.rate_limiting.rate_limiter import",
    "from coffee_maker.langfuse_observe.global_rate_tracker import": "from coffee_maker.llm.rate_limiting.global_rate_tracker import",
    "from coffee_maker.langfuse_observe.cost_budget import": "from coffee_maker.llm.rate_limiting.cost_budget import",

    # Strategies
    "from coffee_maker.langfuse_observe.strategies.fallback import": "from coffee_maker.llm.strategies.fallback import",
    "from coffee_maker.langfuse_observe.strategies.scheduling import": "from coffee_maker.llm.strategies.scheduling import",
    "from coffee_maker.langfuse_observe.strategies.context import": "from coffee_maker.llm.strategies.context import",
    "from coffee_maker.langfuse_observe.strategies.metrics import": "from coffee_maker.llm.strategies.metrics import",

    # Utilities
    "from coffee_maker.langfuse_observe.http_pool import": "from coffee_maker.utils.http_pool import",
    "from coffee_maker.langfuse_observe.response_parser import": "from coffee_maker.utils.response_parser import",
    "from coffee_maker.langfuse_observe.token_estimator import": "from coffee_maker.utils.token_estimator import",

    # Providers
    "from coffee_maker.langfuse_observe.llm_providers.openai import": "from coffee_maker.llm.providers.openai import",
    "from coffee_maker.langfuse_observe.llm_providers.gemini import": "from coffee_maker.llm.providers.gemini import",

    # Observability
    "from coffee_maker.langfuse_observe.agents import": "from coffee_maker.observability.agents import",
    "from coffee_maker.langfuse_observe.cost_calculator import": "from coffee_maker.observability.cost_calculator import",
    "from coffee_maker.langfuse_observe.retry import": "from coffee_maker.observability.retry import",
    "from coffee_maker.langfuse_observe.tools import": "from coffee_maker.observability.tools import",
    "from coffee_maker.langfuse_observe.langfuse_logger import": "from coffee_maker.observability.langfuse_logger import",

    # Analytics
    "from coffee_maker.langfuse_observe.analytics": "from coffee_maker.observability.analytics",

    # Exceptions
    "from coffee_maker.langfuse_observe.exceptions import": "from coffee_maker.exceptions import",
}

def update_file_imports(file_path: Path) -> Tuple[int, List[str]]:
    """Update imports in a single file.

    Returns:
        Tuple of (number of replacements, list of changes)
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content
        changes = []

        for old_import, new_import in IMPORT_MAPPING.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes.append(f"{old_import} -> {new_import}")

        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            return len(changes), changes

        return 0, []

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return 0, []

def update_all_imports() -> Dict[str, List[str]]:
    """Update imports in all Python files."""
    results = {}

    # Search in coffee_maker/ and tests/
    search_paths = [
        Path("coffee_maker"),
        Path("tests"),
        Path("scripts"),
    ]

    for search_path in search_paths:
        for file_path in search_path.rglob("*.py"):
            num_changes, changes = update_file_imports(file_path)
            if num_changes > 0:
                results[str(file_path)] = changes

    return results

def generate_import_report(results: Dict[str, List[str]]) -> str:
    """Generate report of import changes."""
    report = "# Import Update Report\n\n"
    report += f"Total files updated: {len(results)}\n\n"

    for file_path, changes in sorted(results.items()):
        report += f"## {file_path}\n\n"
        for change in changes:
            report += f"- {change}\n"
        report += "\n"

    return report

if __name__ == "__main__":
    print("Updating imports...")
    results = update_all_imports()

    report = generate_import_report(results)
    report_path = Path("docs/US-023_IMPORT_UPDATE_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Updated {len(results)} files")
    print(f"Report written to {report_path}")
```

#### Component 4: Exception Consolidator

**Responsibility**: Merge `langfuse_observe/exceptions.py` into `coffee_maker/exceptions.py`

**Implementation**:
```python
# Script: scripts/consolidate_exceptions.py
"""Consolidate exception definitions."""

from pathlib import Path
import ast

def extract_exception_classes(file_path: Path) -> str:
    """Extract exception class definitions from file."""
    with open(file_path, 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    exception_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it's an exception class
            for base in node.bases:
                if isinstance(base, ast.Name) and 'Error' in base.id or 'Exception' in base.id:
                    # Extract class definition from content
                    start_line = node.lineno - 1
                    end_line = node.end_lineno
                    lines = content.split('\n')[start_line:end_line]
                    exception_classes.append('\n'.join(lines))
                    break

    return '\n\n'.join(exception_classes)

def consolidate_exceptions() -> None:
    """Consolidate langfuse_observe/exceptions.py into coffee_maker/exceptions.py."""

    # Read exceptions from langfuse_observe
    langfuse_exceptions_path = Path("coffee_maker/langfuse_observe/exceptions.py")
    if not langfuse_exceptions_path.exists():
        print("langfuse_observe/exceptions.py not found")
        return

    langfuse_exceptions = extract_exception_classes(langfuse_exceptions_path)

    # Read main exceptions file
    main_exceptions_path = Path("coffee_maker/exceptions.py")
    with open(main_exceptions_path, 'r') as f:
        main_content = f.read()

    # Add section for LLM exceptions
    llm_section = f'''

# ============================================================
# LLM Exceptions (consolidated from langfuse_observe/exceptions.py)
# ============================================================

{langfuse_exceptions}
'''

    # Append to main exceptions file
    new_content = main_content + llm_section

    with open(main_exceptions_path, 'w') as f:
        f.write(new_content)

    print(f"Consolidated exceptions into {main_exceptions_path}")
    print(f"You can now delete {langfuse_exceptions_path}")

if __name__ == "__main__":
    consolidate_exceptions()
```

### Data Structures

No new data structures required. This is a pure refactoring.

### Key Algorithms

#### Algorithm: Safe File Migration

```
Algorithm: Safe File Migration with History Preservation

Input: source_file, destination_file
Output: migrated file with preserved git history

1. Validate source file exists
   IF NOT exists: ABORT with error

2. Create destination directory if needed
   mkdir -p $(dirname destination_file)

3. Use git mv to preserve history
   git mv source_file destination_file

4. Update imports in migrated file
   FOR EACH import in destination_file:
       IF import references old location:
           Replace with new location

5. Commit change with descriptive message
   git add destination_file
   git commit -m "refactor: Move {source} to {destination}"

6. Run tests to verify
   pytest tests/
   IF tests fail:
       git reset --hard HEAD~1
       ABORT with error

7. Continue to next file

Time Complexity: O(1) per file
Space Complexity: O(1)
Success Rate: 100% with rollback on failure
```

#### Algorithm: Import Dependency Analysis

```
Algorithm: Identify All Files Importing from langfuse_observe

Input: directory (coffee_maker/, tests/, scripts/)
Output: list of (file, import_statements)

1. Initialize results = []

2. FOR EACH .py file in directory:
   a. Read file content
   b. Parse with ast.parse()
   c. FOR EACH node in AST:
      - IF node is Import or ImportFrom:
        - IF module starts with "coffee_maker.langfuse_observe":
          - Add (file, import_statement) to results

3. Sort results by file path

4. Return results

Time Complexity: O(N*M) where N=files, M=avg imports per file
Space Complexity: O(N*M)
Estimated Files: 100+ files with ~200 import statements
```

### API Definitions

No public API changes. This is a pure refactoring maintaining backward compatibility.

**Backward Compatibility Strategy**:

```python
# coffee_maker/langfuse_observe/__init__.py (deprecated module)
"""
DEPRECATED: This module has been reorganized.

Please update your imports:
- Core LLM: coffee_maker.llm
- Observability: coffee_maker.observability
- Utilities: coffee_maker.utils

This compatibility layer will be removed in version 2.0.0.
"""

import warnings

warnings.warn(
    "coffee_maker.langfuse_observe is deprecated. "
    "Please update imports to coffee_maker.llm or coffee_maker.observability",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
from coffee_maker.llm import *  # noqa: F401, F403
from coffee_maker.observability import *  # noqa: F401, F403
```

### Database Schema Changes

No database schema changes required.

### Configuration

No configuration changes required. Module reorganization is transparent to configuration.

---

## Testing Strategy

### Unit Tests

**Test Files**: All existing unit tests (156 tests)

**Validation**:
1. **test_no_breaking_changes()** - All existing tests pass unchanged
2. **test_imports_work()** - New import paths work correctly
3. **test_backward_compatibility()** - Old import paths work with deprecation warning
4. **test_no_duplicate_exceptions()** - Only one exception definition per class
5. **test_all_init_exports()** - All `__init__.py` exports work correctly

**Example**:
```python
# tests/unit/test_module_reorganization.py
"""Tests for module reorganization."""

import pytest
import warnings


def test_llm_imports_work():
    """Test that new LLM imports work correctly."""
    from coffee_maker.llm import LLM, LLMConfig, ScheduledLLM

    assert LLM is not None
    assert LLMConfig is not None
    assert ScheduledLLM is not None


def test_observability_imports_work():
    """Test that new observability imports work correctly."""
    from coffee_maker.observability import ObservableAgent, CostCalculator

    assert ObservableAgent is not None
    assert CostCalculator is not None


def test_backward_compatibility_with_warning():
    """Test that old imports work with deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # This should work but emit deprecation warning
        from coffee_maker.langfuse_observe import LLM

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()


def test_no_duplicate_exceptions():
    """Test that exception classes are not duplicated."""
    from coffee_maker import exceptions

    # Check that there's only one definition of each exception
    exception_names = [name for name in dir(exceptions) if name.endswith('Error')]

    # Count occurrences of each exception in source file
    with open('coffee_maker/exceptions.py', 'r') as f:
        content = f.read()

    for exc_name in exception_names:
        count = content.count(f"class {exc_name}")
        assert count == 1, f"{exc_name} defined {count} times (should be 1)"


def test_all_existing_tests_pass():
    """Meta-test: Ensure all existing tests pass after reorganization."""
    import subprocess

    result = subprocess.run(
        ["pytest", "tests/", "-v"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"
```

### Integration Tests

**Test Files**: `tests/integration/test_module_imports.py`

**Test Cases**:
1. **test_daemon_imports()** - Daemon can import all required modules
2. **test_cli_imports()** - CLI can import all required modules
3. **test_autonomous_agents_imports()** - All agents can import modules
4. **test_no_circular_imports()** - No circular import dependencies
5. **test_import_performance()** - Import times reasonable (<2s)

**Example**:
```python
# tests/integration/test_module_imports.py
"""Integration tests for module imports."""

import time
import pytest


def test_daemon_imports():
    """Test that daemon can import all required modules."""
    from coffee_maker.autonomous.daemon import DaemonOrchestrator

    assert DaemonOrchestrator is not None


def test_cli_imports():
    """Test that CLI can import all required modules."""
    from coffee_maker.cli.roadmap_cli import RoadmapCLI

    assert RoadmapCLI is not None


def test_no_circular_imports():
    """Test that there are no circular import dependencies."""
    # This test passes if it doesn't raise ImportError
    import coffee_maker.llm
    import coffee_maker.observability
    import coffee_maker.utils

    # Try importing in different orders
    import coffee_maker.observability.analytics
    import coffee_maker.llm.rate_limiting
    import coffee_maker.llm.strategies


def test_import_performance():
    """Test that imports complete in reasonable time."""
    start = time.time()

    import coffee_maker.llm
    import coffee_maker.observability
    import coffee_maker.utils

    duration = time.time() - start

    assert duration < 2.0, f"Imports took {duration}s (should be <2s)"
```

### Performance Tests

Not required for this refactoring (no performance impact expected).

### Manual Testing

**Manual Validation Checklist**:

1. **Import Validation**:
   ```bash
   # Test new imports
   python -c "from coffee_maker.llm import LLM; print('LLM import: OK')"
   python -c "from coffee_maker.observability import ObservableAgent; print('Observability import: OK')"
   python -c "from coffee_maker.utils import http_pool; print('Utils import: OK')"
   ```

2. **Backward Compatibility**:
   ```bash
   # Test old imports (should warn but work)
   python -c "import warnings; warnings.simplefilter('always'); from coffee_maker.langfuse_observe import LLM; print('Backward compat: OK')"
   ```

3. **Daemon Execution**:
   ```bash
   # Test that daemon still works
   poetry run code-developer --auto-approve
   # (Let it run for 30 seconds, then Ctrl+C)
   ```

4. **CLI Commands**:
   ```bash
   # Test CLI still works
   poetry run project-manager /roadmap
   poetry run project-manager developer-status
   ```

5. **Test Suite**:
   ```bash
   # Run full test suite
   pytest tests/ -v --cov=coffee_maker
   ```

---

## Rollout Plan

### Phase 1: Analysis & Planning (0.5 days, 4 hours)

**Goal**: Create detailed migration plan and get user approval

**Timeline**: 4 hours

**Tasks**:
1. Run audit script to categorize all 39 files (1 hour)
   ```bash
   python scripts/audit_langfuse_observe.py
   ```
   - Output: `docs/US-023_MIGRATION_PLAN.md`
   - Validates categorization of all files

2. Analyze import dependencies (1 hour)
   ```bash
   python scripts/analyze_imports.py
   ```
   - Output: `docs/US-023_IMPORT_ANALYSIS.md`
   - Lists all 100+ files needing import updates

3. Create detailed migration checklist (1 hour)
   - File-by-file move plan with git commands
   - Import update checklist
   - Test validation plan

4. Get user approval (1 hour)
   - Present migration plan
   - Discuss risks and rollback strategy
   - Get go/no-go decision

**Success Criteria**:
- Migration plan document complete
- Import analysis complete
- User approval obtained
- No blockers identified

**Deliverables**:
- `docs/US-023_MIGRATION_PLAN.md`
- `docs/US-023_IMPORT_ANALYSIS.md`
- `docs/US-023_MIGRATION_CHECKLIST.md`

---

### Phase 2: Core Restructuring (2 days, 16 hours)

**Goal**: Create new structure and move all files

**Timeline**: 2 days (16 hours)

**Day 1 Tasks** (8 hours):

1. **Create new directory structure** (1 hour)
   ```bash
   python scripts/create_new_structure.py
   git add coffee_maker/llm/ coffee_maker/observability/
   git commit -m "refactor: Create new module structure"
   ```

2. **Move core LLM files** (2 hours)
   ```bash
   # Move LLM core
   git mv coffee_maker/langfuse_observe/llm.py coffee_maker/llm/
   git mv coffee_maker/langfuse_observe/llm_tools.py coffee_maker/llm/
   git mv coffee_maker/langfuse_observe/llm_config.py coffee_maker/llm/
   git mv coffee_maker/langfuse_observe/scheduled_llm.py coffee_maker/llm/
   git mv coffee_maker/langfuse_observe/auto_picker_llm_refactored.py coffee_maker/llm/auto_picker.py
   git mv coffee_maker/langfuse_observe/builder.py coffee_maker/llm/

   git commit -m "refactor: Move core LLM files to coffee_maker/llm/"
   ```

3. **Move rate limiting files** (1 hour)
   ```bash
   git mv coffee_maker/langfuse_observe/rate_limiter.py coffee_maker/llm/rate_limiting/
   git mv coffee_maker/langfuse_observe/global_rate_tracker.py coffee_maker/llm/rate_limiting/
   git mv coffee_maker/langfuse_observe/cost_budget.py coffee_maker/llm/rate_limiting/

   git commit -m "refactor: Move rate limiting to coffee_maker/llm/rate_limiting/"
   ```

4. **Move strategy files** (1 hour)
   ```bash
   # Delete duplicate retry.py
   git rm coffee_maker/langfuse_observe/strategies/retry.py

   # Move other strategies
   git mv coffee_maker/langfuse_observe/strategies/fallback.py coffee_maker/llm/strategies/
   git mv coffee_maker/langfuse_observe/strategies/scheduling.py coffee_maker/llm/strategies/
   git mv coffee_maker/langfuse_observe/strategies/context.py coffee_maker/llm/strategies/
   git mv coffee_maker/langfuse_observe/strategies/metrics.py coffee_maker/llm/strategies/

   git commit -m "refactor: Move strategies to coffee_maker/llm/strategies/"
   ```

5. **Move utility files** (1 hour)
   ```bash
   git mv coffee_maker/langfuse_observe/http_pool.py coffee_maker/utils/
   git mv coffee_maker/langfuse_observe/response_parser.py coffee_maker/utils/
   git mv coffee_maker/langfuse_observe/token_estimator.py coffee_maker/utils/

   git commit -m "refactor: Move utilities to coffee_maker/utils/"
   ```

6. **Move provider files** (1 hour)
   ```bash
   git mv coffee_maker/langfuse_observe/llm_providers/openai.py coffee_maker/llm/providers/
   git mv coffee_maker/langfuse_observe/llm_providers/gemini.py coffee_maker/llm/providers/

   git commit -m "refactor: Move providers to coffee_maker/llm/providers/"
   ```

7. **Run tests** (1 hour)
   ```bash
   pytest tests/
   # Expected: Many failures due to import errors (will fix in Phase 3)
   ```

**Day 2 Tasks** (8 hours):

8. **Rename langfuse_observe → observability** (2 hours)
   ```bash
   git mv coffee_maker/langfuse_observe coffee_maker/observability

   git commit -m "refactor: Rename langfuse_observe to observability"
   ```

9. **Consolidate exceptions** (2 hours)
   ```bash
   python scripts/consolidate_exceptions.py
   git add coffee_maker/exceptions.py
   git rm coffee_maker/observability/exceptions.py
   git commit -m "refactor: Consolidate exception definitions"
   ```

10. **Create __init__.py exports** (2 hours)
    ```bash
    python scripts/create_init_exports.py
    git add coffee_maker/llm/__init__.py
    git add coffee_maker/llm/rate_limiting/__init__.py
    git add coffee_maker/llm/strategies/__init__.py
    git add coffee_maker/llm/providers/__init__.py
    git add coffee_maker/observability/__init__.py
    git commit -m "refactor: Add __init__.py exports for new modules"
    ```

11. **Run tests again** (1 hour)
    ```bash
    pytest tests/
    # Expected: Still many failures (imports not updated yet)
    ```

12. **Review and checkpoint** (1 hour)
    - Review all commits
    - Ensure file moves look correct
    - Tag: `git tag wip-us-023-phase-2-complete`

**Success Criteria**:
- All 33 files moved to correct locations
- langfuse_observe renamed to observability
- Exceptions consolidated
- __init__.py exports created
- Git history preserved
- Ready for import updates

**Rollback Plan**:
If major issues discovered:
```bash
git reset --hard HEAD~12  # Reset to before Phase 2
```

---

### Phase 3: Update Imports & Validation (1 day, 8 hours)

**Goal**: Update all imports and validate everything works

**Timeline**: 1 day (8 hours)

**Tasks**:

1. **Update imports automatically** (2 hours)
   ```bash
   python scripts/update_imports.py
   # Updates 100+ files

   git add -u
   git commit -m "refactor: Update imports after module reorganization"
   ```

2. **Run tests continuously** (2 hours)
   ```bash
   pytest tests/ -v
   # Fix any remaining import issues manually
   ```

3. **Manual import fixes** (2 hours)
   - Fix any imports script missed
   - Update relative imports
   - Fix any circular import issues

4. **Add backward compatibility layer** (1 hour)
   ```bash
   # Create deprecated langfuse_observe/__init__.py
   cat > coffee_maker/langfuse_observe/__init__.py << 'EOF'
   """DEPRECATED: Use coffee_maker.llm or coffee_maker.observability"""
   import warnings
   warnings.warn("coffee_maker.langfuse_observe is deprecated", DeprecationWarning)
   from coffee_maker.llm import *
   from coffee_maker.observability import *
   EOF

   git add coffee_maker/langfuse_observe/__init__.py
   git commit -m "refactor: Add backward compatibility for langfuse_observe"
   ```

5. **Final validation** (1 hour)
   - Run full test suite: `pytest tests/ -v --cov`
   - Test daemon: `poetry run code-developer --auto-approve` (30 sec)
   - Test CLI: `poetry run project-manager /roadmap`
   - Validate backward compat: test old imports with warnings

**Success Criteria**:
- All 156 tests pass
- Daemon runs without errors
- CLI commands work
- Backward compatibility works with deprecation warnings
- No circular imports
- Import performance acceptable (<2s)

**Rollback Plan**:
If tests fail after import updates:
```bash
git reset --hard wip-us-023-phase-2-complete
# Investigate issues, fix script, retry Phase 3
```

---

### Phase 4: Documentation & Examples (0.5 days, 4 hours)

**Goal**: Update all documentation and create examples

**Timeline**: 4 hours

**Tasks**:

1. **Update README.md** (1 hour)
   - Add "Getting Started" section with new import examples
   - Document module hierarchy
   - Add visual diagram

2. **Update ARCHITECTURE.md** (1 hour)
   - Document new module structure
   - Add component diagrams
   - Explain organization principles

3. **Create module organization guide** (1 hour)
   - `docs/MODULE_ORGANIZATION_GUIDE.md`
   - Explain where to put new code
   - Decision tree for categorization
   - Examples of good/bad organization

4. **Create migration guide** (1 hour)
   - `docs/US-023_MIGRATION_GUIDE.md`
   - For external users of coffee_maker library
   - Show old vs. new import paths
   - Explain deprecation timeline

**Success Criteria**:
- README updated with new structure
- ARCHITECTURE.md reflects new organization
- MODULE_ORGANIZATION_GUIDE.md complete
- MIGRATION_GUIDE.md ready for external users
- Visual diagrams created

**Deliverables**:
- Updated README.md
- Updated ARCHITECTURE.md
- `docs/MODULE_ORGANIZATION_GUIDE.md`
- `docs/US-023_MIGRATION_GUIDE.md`

---

## Risks & Mitigations

### Risk 1: Breaking External Users

**Description**: External users of coffee_maker library may have code that breaks

**Likelihood**: Medium

**Impact**: High (breaks external users)

**Mitigation**:
- Maintain backward compatibility layer in `langfuse_observe/__init__.py`
- Emit deprecation warnings for 6 months before removing
- Create clear migration guide
- Announce changes in release notes
- Use semantic versioning (bump minor version, not major)

---

### Risk 2: Circular Import Dependencies

**Description**: New structure may introduce circular imports

**Likelihood**: Low

**Impact**: High (imports fail)

**Mitigation**:
- Analyze import dependencies before moving files
- Use dependency injection where possible
- Move circular dependencies to separate modules
- Add test to detect circular imports: `test_no_circular_imports()`

---

### Risk 3: Import Path Conflicts

**Description**: New import paths may conflict with existing modules

**Likelihood**: Low

**Impact**: Medium (import confusion)

**Mitigation**:
- Check for name conflicts before creating new modules
- Use unique, descriptive names (`coffee_maker.llm`, not `coffee_maker.ai`)
- Test imports in isolated environment

---

### Risk 4: Test Suite Failures

**Description**: Tests may fail after reorganization due to import errors

**Likelihood**: High

**Impact**: Medium (delays completion)

**Mitigation**:
- Run tests continuously during migration
- Fix imports incrementally, not all at once
- Use automated import update script
- Have rollback plan ready (git reset)
- Allow extra buffer time (1 day) for fixing test issues

---

### Risk 5: Performance Regression

**Description**: Import times may increase with new structure

**Likelihood**: Low

**Impact**: Low (minor slowdown)

**Mitigation**:
- Measure import times before/after: `python -m timeit "import coffee_maker.llm"`
- Use lazy imports where appropriate
- Keep `__init__.py` exports minimal
- Add performance test: `test_import_performance()`

---

### Risk 6: Git History Loss

**Description**: Using wrong git commands may lose file history

**Likelihood**: Low

**Impact**: Medium (lose authorship info)

**Mitigation**:
- ALWAYS use `git mv` (never delete + create)
- Test git history after first move: `git log --follow coffee_maker/llm/llm.py`
- If history lost, rollback and retry with correct commands

---

## Observability

### Metrics

No new metrics required. Existing Langfuse observability continues working.

**Validation Metrics**:
- Import success rate: 100%
- Test pass rate: 100% (156/156)
- Backward compat rate: 100% (all old imports work with warnings)
- Onboarding time reduction: 60% (3-4h → 1-1.5h)

### Logs

No new logging required. Deprecation warnings logged for old imports.

**Log Example**:
```
DeprecationWarning: coffee_maker.langfuse_observe is deprecated.
Please update imports to coffee_maker.llm or coffee_maker.observability.
This compatibility layer will be removed in version 2.0.0.
```

### Alerts

No alerts required. This is a development-time change.

---

## Documentation

### User Documentation

1. **README.md Updates**:
   - Add "Getting Started" section with import examples
   - Document module structure with visual diagram
   - Add "Module Organization" section

2. **Migration Guide** (`docs/US-023_MIGRATION_GUIDE.md`):
   - For external users of coffee_maker library
   - Show old vs. new import paths
   - Explain deprecation timeline
   - Provide automated migration script

### Developer Documentation

1. **Module Organization Guide** (`docs/MODULE_ORGANIZATION_GUIDE.md`):
   - Where to put new code
   - Decision tree for categorization
   - Examples of good/bad organization
   - Principles for maintainability

2. **ARCHITECTURE.md Updates**:
   - Document new module structure
   - Add component diagrams
   - Explain rationale for organization

3. **Code Comments**:
   - Add docstrings to all `__init__.py` files
   - Document purpose of each module
   - Explain what belongs in each package

---

## Security Considerations

No security implications. This is a pure refactoring with no functional changes.

**Validation**:
- All Langfuse observability continues working (no security data leaks)
- No changes to authentication/authorization
- No changes to data handling

---

## Cost Estimate

### Development Time

| Phase | Task | Hours | Agent |
|-------|------|-------|-------|
| 1 | Analysis & Planning | 4 | code_developer |
| 2 | Core Restructuring | 16 | code_developer |
| 3 | Update Imports & Validation | 8 | code_developer |
| 4 | Documentation & Examples | 4 | code_developer |
| **Total** | | **32 hours** | **(4 days)** |

### Infrastructure Cost

**Zero infrastructure cost**. No new dependencies or services.

### Ongoing Maintenance

**Minimal maintenance**:
- Review new code placements (5 min/week)
- Update documentation as needed (30 min/quarter)
- Remove deprecated compatibility layer after 6 months (2 hours)

---

## Future Enhancements

**Phase 2+ Enhancements** (not in scope for US-023):

1. **Evaluate ai_providers/ vs. llm/providers/**:
   - Investigate overlap between the two provider directories
   - Consolidate if they're duplicates
   - Document differences if they serve different purposes

2. **Create coffee_maker/agents/ module**:
   - Move autonomous agents to dedicated module
   - Clear separation: agents vs. LLM vs. observability

3. **Module organization linter**:
   - Create pre-commit hook to validate file placements
   - Warn if file added to wrong directory
   - Suggest correct location based on content

4. **Auto-import suggestion tool**:
   - IDE plugin for VSCode/PyCharm
   - Suggests correct import path based on module name
   - Reduces import errors for new developers

5. **Module dependency graph visualization**:
   - Generate interactive diagram of module dependencies
   - Help identify potential circular imports
   - Aid in architectural planning

---

## References

- [US-023: Clear, Intuitive Module Hierarchy](../../roadmap/ROADMAP.md#us-023)
- [LANGCHAIN_OBSERVE_ARCHITECTURE_REVIEW.md](../../docs/LANGCHAIN_OBSERVE_ARCHITECTURE_REVIEW.md)
- [Python Module Best Practices](https://docs.python.org/3/tutorial/modules.html)
- [Real Python: Python Modules and Packages](https://realpython.com/python-modules-packages/)
- [PEP 8: Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [.gemini/styleguide.md](../../.gemini/styleguide.md)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created initial spec | architect |
| 2025-10-19 | Status: Draft | architect |

---

## Approval

Who needs to approve this spec?

- [ ] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (strategic alignment)
- [ ] User (final approval)

**Approval Date**: TBD

---

## Appendices

### Appendix A: Complete File Categorization

**Files to Keep in observability/** (12 files):
1. `agents.py` ✅ (uses @observe)
2. `cost_calculator.py` ✅ (uses @observe)
3. `retry.py` ✅ (uses @observe)
4. `tools.py` ✅ (uses @observe)
5. `langfuse_logger.py` (Langfuse integration)
6. `analytics/analyzer.py` ✅ (uses @observe)
7. `analytics/exporter.py`
8. `analytics/exporter_sqlite.py`
9. `analytics/models.py`
10. `analytics/models_sqlite.py`
11. `analytics/db_schema.py`
12. `analytics/config.py`

**Files to Move to llm/** (6 files):
1. `llm.py`
2. `llm_tools.py`
3. `llm_config.py`
4. `scheduled_llm.py`
5. `auto_picker_llm_refactored.py` → `auto_picker.py` (rename)
6. `builder.py`

**Files to Move to llm/rate_limiting/** (3 files):
1. `rate_limiter.py`
2. `global_rate_tracker.py`
3. `cost_budget.py`

**Files to Move to llm/strategies/** (4 files):
1. `strategies/fallback.py`
2. `strategies/scheduling.py`
3. `strategies/context.py`
4. `strategies/metrics.py`

**Files to Move to llm/providers/** (3 files):
1. `llm_providers/openai.py`
2. `llm_providers/gemini.py`
3. `llm_providers/__init__.py`

**Files to Move to utils/** (3 files):
1. `http_pool.py`
2. `response_parser.py`
3. `token_estimator.py`

**Files to Delete** (1 file):
1. `strategies/retry.py` (duplicate of parent `retry.py`)

**Files to Merge** (1 file):
1. `exceptions.py` → merge into `coffee_maker/exceptions.py`

**Total**: 33 files to move/merge/delete

### Appendix B: Import Update Checklist

**Directories to Search** (estimated 100+ files):
- `coffee_maker/` (50+ files)
- `tests/` (40+ files)
- `scripts/` (10+ files)

**Import Patterns to Replace**:
```python
# Core LLM (6 patterns)
from coffee_maker.langfuse_observe.llm import → from coffee_maker.llm import
from coffee_maker.langfuse_observe.llm_tools import → from coffee_maker.llm.llm_tools import
from coffee_maker.langfuse_observe.llm_config import → from coffee_maker.llm.llm_config import
from coffee_maker.langfuse_observe.scheduled_llm import → from coffee_maker.llm.scheduled_llm import
from coffee_maker.langfuse_observe.auto_picker_llm_refactored import → from coffee_maker.llm.auto_picker import
from coffee_maker.langfuse_observe.builder import → from coffee_maker.llm.builder import

# Rate limiting (3 patterns)
from coffee_maker.langfuse_observe.rate_limiter import → from coffee_maker.llm.rate_limiting.rate_limiter import
from coffee_maker.langfuse_observe.global_rate_tracker import → from coffee_maker.llm.rate_limiting.global_rate_tracker import
from coffee_maker.langfuse_observe.cost_budget import → from coffee_maker.llm.rate_limiting.cost_budget import

# Strategies (4 patterns)
from coffee_maker.langfuse_observe.strategies.fallback import → from coffee_maker.llm.strategies.fallback import
from coffee_maker.langfuse_observe.strategies.scheduling import → from coffee_maker.llm.strategies.scheduling import
from coffee_maker.langfuse_observe.strategies.context import → from coffee_maker.llm.strategies.context import
from coffee_maker.langfuse_observe.strategies.metrics import → from coffee_maker.llm.strategies.metrics import

# Utilities (3 patterns)
from coffee_maker.langfuse_observe.http_pool import → from coffee_maker.utils.http_pool import
from coffee_maker.langfuse_observe.response_parser import → from coffee_maker.utils.response_parser import
from coffee_maker.langfuse_observe.token_estimator import → from coffee_maker.utils.token_estimator import

# Providers (2 patterns)
from coffee_maker.langfuse_observe.llm_providers.openai import → from coffee_maker.llm.providers.openai import
from coffee_maker.langfuse_observe.llm_providers.gemini import → from coffee_maker.llm.providers.gemini import

# Observability (5 patterns)
from coffee_maker.langfuse_observe.agents import → from coffee_maker.observability.agents import
from coffee_maker.langfuse_observe.cost_calculator import → from coffee_maker.observability.cost_calculator import
from coffee_maker.langfuse_observe.retry import → from coffee_maker.observability.retry import
from coffee_maker.langfuse_observe.tools import → from coffee_maker.observability.tools import
from coffee_maker.langfuse_observe.langfuse_logger import → from coffee_maker.observability.langfuse_logger import

# Analytics (1 pattern)
from coffee_maker.langfuse_observe.analytics → from coffee_maker.observability.analytics

# Exceptions (1 pattern)
from coffee_maker.langfuse_observe.exceptions import → from coffee_maker.exceptions import
```

**Total**: 28 import patterns to update across 100+ files

### Appendix C: Rollback Procedure

**If Issues Discovered During Phase 2**:
```bash
# Reset to before Phase 2
git reset --hard HEAD~12
git tag -d wip-us-023-phase-2-complete

# Re-evaluate approach
# Fix issues in scripts
# Retry Phase 2
```

**If Issues Discovered During Phase 3**:
```bash
# Reset to end of Phase 2
git reset --hard wip-us-023-phase-2-complete

# Fix import update script
# Retry Phase 3
```

**If Issues Discovered After Completion**:
```bash
# Create hotfix branch
git checkout -b hotfix/us-023-rollback roadmap

# Revert all commits from US-023
git revert HEAD~20..HEAD

# Test rollback
pytest tests/

# Merge hotfix if tests pass
git checkout roadmap
git merge hotfix/us-023-rollback
```

**Maximum Rollback Time**: 30 minutes (all changes are in git history)

---

**Remember**: This is a complex refactoring affecting 100+ files. Take it slow, test continuously, and don't hesitate to rollback if issues arise. The goal is a cleaner structure, not speed!
