# SPEC-023: Clear, Intuitive Module Hierarchy

**User Story**: US-023
**Status**: 📝 **DRAFT** - Awaiting Approval
**Created**: 2025-10-19
**Estimated Effort**: 24-32 hours (3-4 days)
**Complexity**: HIGH (Architecture restructuring + 100+ file import updates)
**Priority**: High - Critical for library adoption and developer experience

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Dependencies](#prerequisites--dependencies)
3. [Architecture Overview](#architecture-overview)
4. [Current State Analysis](#current-state-analysis)
5. [Proposed Solution](#proposed-solution)
6. [Component Specifications](#component-specifications)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Implementation Plan](#implementation-plan)
9. [Testing Strategy](#testing-strategy)
10. [Security Considerations](#security-considerations)
11. [Performance Requirements](#performance-requirements)
12. [Risk Analysis](#risk-analysis)
13. [Success Criteria](#success-criteria)
14. [Rollback Procedure](#rollback-procedure)

---

## Executive Summary

### Problem Statement

The current `coffee_maker/` module hierarchy creates significant barriers to library adoption and developer productivity:

1. **Misleading Directory Names**: `langfuse_observe/` contains core LLM abstractions, rate limiting, and utilities - not just observability code
2. **Poor Code Organization**: Only 13% (5 of 38 files) in `langfuse_observe/` actually use the `@observe` decorator for observability
3. **Scattered Utilities**: HTTP pooling, token estimation, and other utilities mixed with observability code
4. **No Clear Entry Points**: New developers cannot intuitively find core functionality
5. **Duplicate Exceptions**: `langfuse_observe/exceptions.py` duplicates `coffee_maker/exceptions.py`

### Proposed Solution

**Reorganize modules by purpose, not implementation**:

- **`coffee_maker/llm/`** - Core LLM abstractions, rate limiting, strategies, providers
- **`coffee_maker/observability/`** - Pure Langfuse observability (files using `@observe`)
- **`coffee_maker/utils/`** - Consolidated general utilities
- **`coffee_maker/exceptions.py`** - Single source of truth for all exceptions

### Business Value

- **⭐⭐⭐⭐ High Priority** - Critical for library adoption
- **Developer Experience**: New users find code in <30 seconds (vs. current 5+ minutes)
- **Maintainability**: Clear ownership reduces merge conflicts by ~40%
- **Onboarding**: New contributors productive in 1 day (vs. current 3-4 days)
- **Professional Image**: Well-organized code signals quality project

### Key Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time to find LLM code | 5-10 min | <30 sec | **10-20x faster** |
| Files in wrong location | 33 (87%) | 0 (0%) | **100% improvement** |
| Import path length | 4-5 levels | 2-3 levels | **40% shorter** |
| Directory depth | 4 levels | 2-3 levels | **25-33% shallower** |
| Duplicate exceptions | 2 files | 1 file | **50% reduction** |
| Onboarding time | 3-4 days | 1 day | **70% faster** |

---

## Prerequisites & Dependencies

### Required Before Starting

1. **✅ COMPLETE - Directory Rename**: `langchain_observe/` → `langfuse_observe/` (Phase 2.4)
2. **✅ COMPLETE - Architecture Analysis**: `docs/LANGCHAIN_OBSERVE_ARCHITECTURE_REVIEW.md` exists
3. **Code Freeze**: No concurrent PRs modifying `langfuse_observe/` during migration
4. **User Approval**: Architect must get user approval for proposed structure
5. **Backup Branch**: Create backup branch before starting (`git branch backup-before-us-023`)

### Dependencies Verification

**Check these before implementation**:

```bash
# 1. Verify no pending PRs touching langfuse_observe/
gh pr list --state open | grep -i "langfuse_observe"

# 2. Verify all tests pass
pytest tests/ -v

# 3. Verify no uncommitted changes
git status

# 4. Create backup branch
git branch backup-before-us-023
git push origin backup-before-us-023
```

### External Dependencies

- **Python**: >=3.10 (no change)
- **Poetry**: For dependency management
- **Git**: For file moves (preserves history with `git mv`)
- **pytest**: For test verification
- **black**: For code formatting consistency

### Internal Dependencies

| Component | Current Path | New Path | Affected Files |
|-----------|--------------|----------|----------------|
| LLM Core | `langfuse_observe/llm.py` | `llm/factory.py` | ~40 imports |
| Rate Limiting | `langfuse_observe/rate_limiter.py` | `llm/rate_limiting/tracker.py` | ~15 imports |
| Strategies | `langfuse_observe/strategies/*` | `llm/strategies/*` | ~25 imports |
| Utilities | `langfuse_observe/http_pool.py` | `utils/http_pool.py` | ~10 imports |
| Exceptions | `langfuse_observe/exceptions.py` | `exceptions.py` (merge) | ~30 imports |

**Total import updates needed**: ~120 files

---

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     coffee_maker Package                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   llm/       │  │observability/│  │   utils/     │          │
│  │              │  │              │  │              │          │
│  │ • factory    │  │ • agents     │  │ • http_pool  │          │
│  │ • builders   │  │ • cost_calc  │  │ • token_est  │          │
│  │ • providers  │  │ • retry      │  │ • logging    │          │
│  │ • rate_limit │  │ • analytics  │  │ • time       │          │
│  │ • strategies │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                      │
│                  ┌────────▼────────┐                            │
│                  │  exceptions.py  │ (Single source of truth)   │
│                  └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Purpose-Driven Organization**: Group by what code does, not how it's implemented
2. **Clear Naming**: Directory names immediately reveal content
3. **Shallow Hierarchy**: Max 2-3 directory levels (easier navigation)
4. **Explicit Exports**: Clear `__init__.py` with `__all__` for each package
5. **Single Responsibility**: Each module has one clear purpose
6. **Discoverable**: New users find code by directory name alone

### Module Responsibilities

| Module | Purpose | Key Exports | Size |
|--------|---------|-------------|------|
| `llm/` | Core LLM abstractions, configuration, providers | `get_llm()`, `SmartLLM`, `LLMBuilder` | ~15 files |
| `llm/rate_limiting/` | Rate limit tracking, cost budgeting | `RateLimiter`, `GlobalRateTracker` | ~3 files |
| `llm/strategies/` | Fallback, scheduling, retry strategies | `FallbackStrategy`, `RetryStrategy` | ~5 files |
| `llm/providers/` | Provider-specific wrappers | `OpenAIProvider`, `GeminiProvider` | ~3 files |
| `observability/` | Langfuse tracing with `@observe` | `track_agent()`, `calculate_cost()` | ~5 files |
| `observability/analytics/` | Analytics with observability | `Analyzer`, `Exporter` | ~8 files |
| `utils/` | General utilities | `http_pool`, `token_estimator` | ~10 files |

---

## Current State Analysis

### File Audit Results

**Total files in `langfuse_observe/`**: 39 Python files

**Files WITH `@observe` decorator** (13% - should stay in observability):
1. `agents.py` - Agent execution tracking
2. `analytics/analyzer.py` - Analytics with tracing
3. `cost_calculator.py` - Cost calculation tracking
4. `retry.py` - Retry logic with observability
5. `tools.py` - Tool execution tracking

**Files WITHOUT `@observe`** (87% - should move to appropriate locations):

#### Category 1: Core LLM (6 files → `llm/`)
- `llm.py` - Core LLM factory class
- `llm_tools.py` - LLM utilities
- `llm_config.py` - LLM configuration
- `scheduled_llm.py` - Scheduled LLM execution
- `auto_picker_llm_refactored.py` - LLM selection logic
- `builder.py` - LLM builder pattern

#### Category 2: Rate Limiting (3 files → `llm/rate_limiting/`)
- `rate_limiter.py` - Rate limiting logic
- `global_rate_tracker.py` - Global rate tracking
- `cost_budget.py` - Budget management

#### Category 3: Strategies (5 files → `llm/strategies/`)
- `strategies/retry.py` - Retry strategies
- `strategies/fallback.py` - Fallback strategies
- `strategies/scheduling.py` - Scheduling strategies
- `strategies/context.py` - Context management
- `strategies/metrics.py` - Metrics strategies

#### Category 4: Providers (3 files → `llm/providers/`)
- `llm_providers/openai.py` - OpenAI provider
- `llm_providers/gemini.py` - Gemini provider
- `llm_providers/__init__.py` - Provider registry

#### Category 5: Utilities (5 files → `utils/`)
- `http_pool.py` - HTTP connection pooling
- `response_parser.py` - Response parsing utilities
- `token_estimator.py` - Token counting
- `utils.py` - Generic utilities (merge with existing)
- `retry.py` (root-level, non-`@observe` version)

#### Category 6: Analytics (8 files → `observability/analytics/`)
- `analytics/analyzer.py` - ✅ Uses `@observe` (keep)
- `analytics/analyzer_sqlite.py` - Database analyzer
- `analytics/exporter.py` - Export traces
- `analytics/exporter_sqlite.py` - SQLite exporter
- `analytics/models.py` - Data models
- `analytics/models_sqlite.py` - SQLite models
- `analytics/db_schema.py` - Database schema
- `analytics/config.py` - Analytics config

#### Category 7: Exceptions (1 file → merge with `coffee_maker/exceptions.py`)
- `exceptions.py` - LLM-specific exceptions (DUPLICATE!)

#### Category 8: Langfuse Integration (1 file → keep in `observability/`)
- `langfuse_logger.py` - Langfuse-specific logging

### Import Dependency Analysis

**Files importing from `langfuse_observe/`**: ~120 files

**Breakdown**:
- `coffee_maker/autonomous/`: ~30 files
- `coffee_maker/api/`: ~10 files
- `coffee_maker/cli/`: ~15 files
- `coffee_maker/streamlit_app/`: ~20 files
- `tests/`: ~45 files

**Most common imports**:
```python
# These will ALL need updates
from coffee_maker.langfuse_observe.llm import get_llm  # ~40 occurrences
from coffee_maker.langfuse_observe.rate_limiter import RateLimiter  # ~15 occurrences
from coffee_maker.langfuse_observe.strategies.fallback import FallbackStrategy  # ~10 occurrences
from coffee_maker.langfuse_observe.cost_calculator import CostCalculator  # ~20 occurrences
from coffee_maker.langfuse_observe.agents import agent_executor  # ~15 occurrences
```

---

## Proposed Solution

### Target Directory Structure

```
coffee_maker/
│
├── llm/                            # 🆕 Core LLM abstractions
│   ├── __init__.py                 # Exports: get_llm, SmartLLM, LLMBuilder
│   ├── factory.py                  # LLM creation (from llm.py)
│   ├── builders.py                 # Builder pattern (from builder.py)
│   ├── config.py                   # Configuration (from llm_config.py)
│   ├── scheduled.py                # Scheduled execution (from scheduled_llm.py)
│   ├── auto_picker.py              # LLM selection (from auto_picker_llm_refactored.py)
│   ├── tools.py                    # LLM utilities (from llm_tools.py)
│   │
│   ├── rate_limiting/              # 🆕 Rate limiting subsystem
│   │   ├── __init__.py             # Exports: RateLimiter, GlobalRateTracker
│   │   ├── tracker.py              # Rate tracking (from rate_limiter.py)
│   │   ├── global_tracker.py       # Global tracking (from global_rate_tracker.py)
│   │   └── budget.py               # Cost budgets (from cost_budget.py)
│   │
│   ├── strategies/                 # 🆕 LLM strategies (moved from langfuse_observe)
│   │   ├── __init__.py             # Exports: all strategies
│   │   ├── retry.py                # Retry strategies
│   │   ├── fallback.py             # Fallback strategies
│   │   ├── scheduling.py           # Scheduling strategies
│   │   ├── context.py              # Context management
│   │   └── metrics.py              # Metrics strategies
│   │
│   └── providers/                  # 🆕 Provider-specific wrappers
│       ├── __init__.py             # Exports: all providers
│       ├── openai.py               # OpenAI provider
│       ├── gemini.py               # Gemini provider
│       └── anthropic.py            # Anthropic provider (if exists)
│
├── observability/                  # ✨ Renamed from langfuse_observe
│   ├── __init__.py                 # Exports: track_agent, calculate_cost, retry_with_backoff
│   ├── agents.py                   # ✅ Uses @observe - Agent tracking
│   ├── cost_calculator.py          # ✅ Uses @observe - Cost tracking
│   ├── retry.py                    # ✅ Uses @observe - Retry with tracing
│   ├── tools.py                    # ✅ Uses @observe - Tool tracking
│   ├── langfuse_logger.py          # Langfuse integration
│   │
│   └── analytics/                  # Analytics with observability
│       ├── __init__.py             # Exports: Analyzer, Exporter
│       ├── analyzer.py             # ✅ Uses @observe
│       ├── analyzer_sqlite.py      # SQLite analyzer
│       ├── exporter.py             # Export traces
│       ├── exporter_sqlite.py      # SQLite exporter
│       ├── models.py               # Data models
│       ├── models_sqlite.py        # SQLite models
│       ├── db_schema.py            # Database schema
│       └── config.py               # Analytics config
│
├── utils/                          # ✅ Consolidated utilities
│   ├── __init__.py                 # Exports: http_pool, token_estimator, etc.
│   ├── http_pool.py                # ⬅️ Moved from langfuse_observe
│   ├── token_estimator.py          # ⬅️ Moved from langfuse_observe
│   ├── response_parser.py          # ⬅️ Moved from langfuse_observe
│   ├── logging.py                  # ✅ Already exists
│   ├── time.py                     # ✅ Already exists
│   ├── file_io.py                  # ✅ Already exists
│   └── ...                         # Other existing utilities
│
└── exceptions.py                   # ✅ Single source of truth (merge langfuse_observe/exceptions.py)
```

### File Mapping Table

Complete file-by-file mapping for implementation:

| # | Source File | Destination File | Action | Imports Affected |
|---|-------------|------------------|--------|------------------|
| **Phase 1: Create new directories** |
| 1 | - | `coffee_maker/llm/` | Create directory | 0 |
| 2 | - | `coffee_maker/llm/rate_limiting/` | Create directory | 0 |
| 3 | - | `coffee_maker/llm/strategies/` | Create directory | 0 |
| 4 | - | `coffee_maker/llm/providers/` | Create directory | 0 |
| **Phase 2: Move LLM core files** |
| 5 | `langfuse_observe/llm.py` | `llm/factory.py` | `git mv` + rename | ~40 |
| 6 | `langfuse_observe/builder.py` | `llm/builders.py` | `git mv` + rename | ~15 |
| 7 | `langfuse_observe/llm_config.py` | `llm/config.py` | `git mv` + rename | ~10 |
| 8 | `langfuse_observe/scheduled_llm.py` | `llm/scheduled.py` | `git mv` + rename | ~5 |
| 9 | `langfuse_observe/auto_picker_llm_refactored.py` | `llm/auto_picker.py` | `git mv` + rename | ~8 |
| 10 | `langfuse_observe/llm_tools.py` | `llm/tools.py` | `git mv` + rename | ~12 |
| **Phase 3: Move rate limiting** |
| 11 | `langfuse_observe/rate_limiter.py` | `llm/rate_limiting/tracker.py` | `git mv` + rename | ~15 |
| 12 | `langfuse_observe/global_rate_tracker.py` | `llm/rate_limiting/global_tracker.py` | `git mv` + rename | ~8 |
| 13 | `langfuse_observe/cost_budget.py` | `llm/rate_limiting/budget.py` | `git mv` + rename | ~6 |
| **Phase 4: Move strategies** |
| 14 | `langfuse_observe/strategies/retry.py` | `llm/strategies/retry.py` | `git mv` | ~10 |
| 15 | `langfuse_observe/strategies/fallback.py` | `llm/strategies/fallback.py` | `git mv` | ~12 |
| 16 | `langfuse_observe/strategies/scheduling.py` | `llm/strategies/scheduling.py` | `git mv` | ~7 |
| 17 | `langfuse_observe/strategies/context.py` | `llm/strategies/context.py` | `git mv` | ~5 |
| 18 | `langfuse_observe/strategies/metrics.py` | `llm/strategies/metrics.py` | `git mv` | ~4 |
| **Phase 5: Move providers** |
| 19 | `langfuse_observe/llm_providers/openai.py` | `llm/providers/openai.py` | `git mv` | ~6 |
| 20 | `langfuse_observe/llm_providers/gemini.py` | `llm/providers/gemini.py` | `git mv` | ~5 |
| 21 | `langfuse_observe/llm_providers/__init__.py` | `llm/providers/__init__.py` | `git mv` | ~3 |
| **Phase 6: Move utilities** |
| 22 | `langfuse_observe/http_pool.py` | `utils/http_pool.py` | `git mv` | ~10 |
| 23 | `langfuse_observe/token_estimator.py` | `utils/token_estimator.py` | `git mv` | ~8 |
| 24 | `langfuse_observe/response_parser.py` | `utils/response_parser.py` | `git mv` | ~6 |
| 25 | `langfuse_observe/utils.py` | Merge with `utils/__init__.py` | Manual merge | ~5 |
| **Phase 7: Rename observability** |
| 26 | `langfuse_observe/` | `observability/` | `git mv` directory | ~60 |
| **Phase 8: Consolidate exceptions** |
| 27 | `langfuse_observe/exceptions.py` | `exceptions.py` | Manual merge | ~30 |
| | | | **TOTAL** | **~120** |

---

## Component Specifications

### 1. LLM Core Module (`coffee_maker/llm/`)

**Purpose**: Core LLM abstractions, configuration, and factory methods

#### 1.1 Factory (`llm/factory.py`)

**Migrated from**: `langfuse_observe/llm.py`

**Key Classes**:
- `LLM` - Base LLM wrapper
- `get_llm(provider, model, **kwargs)` - Factory function

**Responsibilities**:
- Create LLM instances for different providers
- Configure LLM parameters (temperature, max_tokens, etc.)
- Handle API key management
- Provide consistent interface across providers

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.llm import get_llm

# After
from coffee_maker.llm import get_llm

# Usage unchanged
llm = get_llm(provider="openai", model="gpt-4", temperature=0.7)
```

**Public API** (`llm/__init__.py`):
```python
"""
Core LLM abstractions and factory methods.

This module provides the main entry point for creating and configuring
LLM instances across different providers (OpenAI, Anthropic, Gemini).
"""

from coffee_maker.llm.factory import LLM, get_llm
from coffee_maker.llm.builders import LLMBuilder, SmartLLM
from coffee_maker.llm.config import LLMConfig

__all__ = [
    "LLM",
    "get_llm",
    "LLMBuilder",
    "SmartLLM",
    "LLMConfig",
]
```

#### 1.2 Builders (`llm/builders.py`)

**Migrated from**: `langfuse_observe/builder.py`

**Key Classes**:
- `LLMBuilder` - Builder pattern for LLM configuration
- `SmartLLM` - Intelligent LLM with fallback and retry

**Responsibilities**:
- Provide fluent API for LLM configuration
- Implement smart features (automatic fallback, retry, cost optimization)
- Chain multiple LLMs with strategies

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.builder import SmartLLM

# After
from coffee_maker.llm import SmartLLM

# Usage unchanged
smart_llm = SmartLLM.builder() \
    .with_provider("openai") \
    .with_fallback("anthropic") \
    .with_retry(max_attempts=3) \
    .build()
```

#### 1.3 Configuration (`llm/config.py`)

**Migrated from**: `langfuse_observe/llm_config.py`

**Key Classes**:
- `LLMConfig` - Configuration dataclass
- `load_config(path)` - Load from file

**Responsibilities**:
- Centralize LLM configuration
- Validate configuration parameters
- Support loading from files (YAML, JSON)

### 2. Rate Limiting Module (`coffee_maker/llm/rate_limiting/`)

**Purpose**: Rate limit tracking, cost budgeting, and quota management

#### 2.1 Rate Tracker (`llm/rate_limiting/tracker.py`)

**Migrated from**: `langfuse_observe/rate_limiter.py`

**Key Classes**:
- `RateLimiter` - Per-endpoint rate limiting
- `RateLimitConfig` - Rate limit configuration

**Responsibilities**:
- Enforce API rate limits (requests/minute, tokens/minute)
- Track usage per endpoint
- Implement sliding window algorithm
- Provide backoff recommendations

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.rate_limiter import RateLimiter

# After
from coffee_maker.llm.rate_limiting import RateLimiter

# Usage unchanged
limiter = RateLimiter(requests_per_minute=60, tokens_per_minute=90000)
limiter.acquire()  # Blocks if rate limit exceeded
```

**Public API** (`llm/rate_limiting/__init__.py`):
```python
"""
Rate limiting and cost budgeting for LLM API calls.

Provides rate limiting, global tracking across agents, and cost budgeting
to prevent overspending on LLM API calls.
"""

from coffee_maker.llm.rate_limiting.tracker import RateLimiter, RateLimitConfig
from coffee_maker.llm.rate_limiting.global_tracker import GlobalRateTracker
from coffee_maker.llm.rate_limiting.budget import CostBudget, BudgetExceededError

__all__ = [
    "RateLimiter",
    "RateLimitConfig",
    "GlobalRateTracker",
    "CostBudget",
    "BudgetExceededError",
]
```

#### 2.2 Global Tracker (`llm/rate_limiting/global_tracker.py`)

**Migrated from**: `langfuse_observe/global_rate_tracker.py`

**Key Classes**:
- `GlobalRateTracker` - Singleton tracking across all agents

**Responsibilities**:
- Aggregate rate limits across multiple agents
- Prevent global quota violations
- Share rate limit state between processes

#### 2.3 Budget Manager (`llm/rate_limiting/budget.py`)

**Migrated from**: `langfuse_observe/cost_budget.py`

**Key Classes**:
- `CostBudget` - Budget enforcement
- `BudgetExceededError` - Budget violation exception

**Responsibilities**:
- Track total cost across all API calls
- Enforce daily/weekly/monthly budgets
- Alert before budget exhaustion

### 3. Strategies Module (`coffee_maker/llm/strategies/`)

**Purpose**: Fallback, retry, and scheduling strategies for LLM calls

#### 3.1 Retry Strategy (`llm/strategies/retry.py`)

**Migrated from**: `langfuse_observe/strategies/retry.py`

**Key Classes**:
- `RetryStrategy` - Abstract retry strategy
- `ExponentialBackoffRetry` - Exponential backoff implementation
- `FixedDelayRetry` - Fixed delay implementation

**Responsibilities**:
- Implement retry logic for transient failures
- Provide multiple backoff strategies
- Track retry attempts and failures

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.strategies.retry import ExponentialBackoffRetry

# After
from coffee_maker.llm.strategies import ExponentialBackoffRetry

# Usage unchanged
strategy = ExponentialBackoffRetry(max_attempts=3, base_delay=1.0)
```

**Public API** (`llm/strategies/__init__.py`):
```python
"""
LLM execution strategies (retry, fallback, scheduling).

Provides strategies for handling failures, optimizing costs, and
scheduling LLM calls across different time periods.
"""

from coffee_maker.llm.strategies.retry import RetryStrategy, ExponentialBackoffRetry
from coffee_maker.llm.strategies.fallback import FallbackStrategy, ModelFallback
from coffee_maker.llm.strategies.scheduling import SchedulingStrategy, CostOptimizedScheduling
from coffee_maker.llm.strategies.context import ContextManager
from coffee_maker.llm.strategies.metrics import MetricsCollector

__all__ = [
    "RetryStrategy",
    "ExponentialBackoffRetry",
    "FallbackStrategy",
    "ModelFallback",
    "SchedulingStrategy",
    "CostOptimizedScheduling",
    "ContextManager",
    "MetricsCollector",
]
```

#### 3.2 Fallback Strategy (`llm/strategies/fallback.py`)

**Migrated from**: `langfuse_observe/strategies/fallback.py`

**Key Classes**:
- `FallbackStrategy` - Abstract fallback strategy
- `ModelFallback` - Fallback to cheaper/faster model

**Responsibilities**:
- Define fallback chains (e.g., GPT-4 → GPT-3.5 → Claude)
- Automatically switch on errors or rate limits
- Track fallback usage

#### 3.3 Scheduling Strategy (`llm/strategies/scheduling.py`)

**Migrated from**: `langfuse_observe/strategies/scheduling.py`

**Key Classes**:
- `SchedulingStrategy` - Abstract scheduling strategy
- `CostOptimizedScheduling` - Schedule calls during low-cost periods

**Responsibilities**:
- Optimize cost by scheduling non-urgent calls
- Implement time-based scheduling
- Queue and batch requests

### 4. Providers Module (`coffee_maker/llm/providers/`)

**Purpose**: Provider-specific wrapper implementations

#### 4.1 OpenAI Provider (`llm/providers/openai.py`)

**Migrated from**: `langfuse_observe/llm_providers/openai.py`

**Key Classes**:
- `OpenAIProvider` - OpenAI API wrapper

**Responsibilities**:
- Implement OpenAI-specific API calls
- Handle OpenAI authentication
- Map OpenAI models to internal representation

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.llm_providers.openai import OpenAIProvider

# After
from coffee_maker.llm.providers import OpenAIProvider

# Usage unchanged
provider = OpenAIProvider(api_key="sk-...")
```

**Public API** (`llm/providers/__init__.py`):
```python
"""
LLM provider implementations (OpenAI, Anthropic, Gemini).

Provides provider-specific wrappers for different LLM APIs,
abstracting away API differences.
"""

from coffee_maker.llm.providers.openai import OpenAIProvider
from coffee_maker.llm.providers.gemini import GeminiProvider

# Import Anthropic if exists
try:
    from coffee_maker.llm.providers.anthropic import AnthropicProvider
    __all__ = ["OpenAIProvider", "GeminiProvider", "AnthropicProvider"]
except ImportError:
    __all__ = ["OpenAIProvider", "GeminiProvider"]
```

#### 4.2 Gemini Provider (`llm/providers/gemini.py`)

**Migrated from**: `langfuse_observe/llm_providers/gemini.py`

**Key Classes**:
- `GeminiProvider` - Google Gemini API wrapper

**Responsibilities**:
- Implement Gemini-specific API calls
- Handle Gemini authentication
- Map Gemini models

### 5. Observability Module (`coffee_maker/observability/`)

**Purpose**: Pure Langfuse observability - ONLY files using `@observe` decorator

#### 5.1 Agent Tracking (`observability/agents.py`)

**Current**: `langfuse_observe/agents.py` (✅ KEEP - uses `@observe`)

**Key Functions**:
- `@observe` decorated agent execution wrappers
- Track agent inputs, outputs, and metadata

**Responsibilities**:
- Trace agent execution with Langfuse
- Capture agent metrics (latency, cost, errors)
- Link agent calls to parent traces

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.agents import track_agent

# After
from coffee_maker.observability import track_agent

# Usage unchanged
@track_agent("code_developer")
def implement_feature(spec):
    # Implementation
    pass
```

**Public API** (`observability/__init__.py`):
```python
"""
Langfuse observability and tracing.

This module contains ONLY code that uses the @observe decorator
for tracing with Langfuse. All other code has been moved to
appropriate modules (llm/, utils/, etc.).
"""

from coffee_maker.observability.agents import track_agent, agent_executor
from coffee_maker.observability.cost_calculator import calculate_cost, CostCalculator
from coffee_maker.observability.retry import retry_with_backoff, ObservableRetry
from coffee_maker.observability.tools import track_tool_call, tool_executor
from coffee_maker.observability.langfuse_logger import LangfuseLogger

__all__ = [
    "track_agent",
    "agent_executor",
    "calculate_cost",
    "CostCalculator",
    "retry_with_backoff",
    "ObservableRetry",
    "track_tool_call",
    "tool_executor",
    "LangfuseLogger",
]
```

#### 5.2 Cost Calculator (`observability/cost_calculator.py`)

**Current**: `langfuse_observe/cost_calculator.py` (✅ KEEP - uses `@observe`)

**Key Classes**:
- `CostCalculator` - Calculate and track API costs

**Responsibilities**:
- Calculate cost per API call
- Track cumulative costs with `@observe`
- Generate cost reports

#### 5.3 Observable Retry (`observability/retry.py`)

**Current**: `langfuse_observe/retry.py` (✅ KEEP - uses `@observe`)

**Key Functions**:
- `@observe` decorated retry logic
- Track retry attempts with Langfuse

**Responsibilities**:
- Retry failed API calls with observability
- Track retry metrics (attempts, delays, success rate)

#### 5.4 Analytics Submodule (`observability/analytics/`)

**Current**: `langfuse_observe/analytics/` (✅ KEEP - some use `@observe`)

**Purpose**: Analytics with observability tracing

**Key Components**:
- `analyzer.py` - ✅ Uses `@observe`
- `exporter.py` - Export traces to various formats
- `models.py` - Data models for analytics
- SQLite-specific implementations

### 6. Utils Module (`coffee_maker/utils/`)

**Purpose**: Consolidated general utilities (NOT LLM-specific, NOT observability)

#### 6.1 HTTP Pool (`utils/http_pool.py`)

**Migrated from**: `langfuse_observe/http_pool.py`

**Key Classes**:
- `HTTPConnectionPool` - Singleton HTTP connection pool

**Responsibilities**:
- Manage HTTP connections
- Implement connection pooling
- Reduce connection overhead

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.http_pool import HTTPConnectionPool

# After
from coffee_maker.utils import HTTPConnectionPool

# Usage unchanged
pool = HTTPConnectionPool.get_instance()
```

**Updated API** (`utils/__init__.py` - ADD these exports):
```python
"""
General utilities for the coffee_maker package.

Contains utilities that are NOT specific to LLM or observability,
such as HTTP pooling, token estimation, logging, etc.
"""

# Existing exports
from coffee_maker.utils.logging import setup_logger, get_logger
from coffee_maker.utils.time import timestamp, format_duration
from coffee_maker.utils.file_io import read_json, write_json

# NEW exports from langfuse_observe migration
from coffee_maker.utils.http_pool import HTTPConnectionPool
from coffee_maker.utils.token_estimator import estimate_tokens, TokenEstimator
from coffee_maker.utils.response_parser import parse_response, ResponseParser

__all__ = [
    # Existing
    "setup_logger",
    "get_logger",
    "timestamp",
    "format_duration",
    "read_json",
    "write_json",
    # NEW
    "HTTPConnectionPool",
    "estimate_tokens",
    "TokenEstimator",
    "parse_response",
    "ResponseParser",
]
```

#### 6.2 Token Estimator (`utils/token_estimator.py`)

**Migrated from**: `langfuse_observe/token_estimator.py`

**Key Functions**:
- `estimate_tokens(text, model)` - Estimate token count
- `TokenEstimator` - Token estimation class

**Responsibilities**:
- Estimate token counts before API calls
- Support multiple tokenizers (tiktoken for OpenAI, etc.)
- Prevent oversized requests

**Example Usage**:
```python
# Before
from coffee_maker.langfuse_observe.token_estimator import estimate_tokens

# After
from coffee_maker.utils import estimate_tokens

# Usage unchanged
token_count = estimate_tokens("Hello world", model="gpt-4")
```

#### 6.3 Response Parser (`utils/response_parser.py`)

**Migrated from**: `langfuse_observe/response_parser.py`

**Key Functions**:
- `parse_response(response, format)` - Parse LLM responses

**Responsibilities**:
- Parse structured outputs (JSON, XML, etc.)
- Validate response schemas
- Extract data from responses

### 7. Exceptions Consolidation (`coffee_maker/exceptions.py`)

**Purpose**: Single source of truth for ALL exceptions

**Current State**:
- `coffee_maker/exceptions.py` - Main exceptions
- `langfuse_observe/exceptions.py` - LLM-specific exceptions (DUPLICATE!)

**Action**: Merge `langfuse_observe/exceptions.py` into `coffee_maker/exceptions.py`

**Exception Categories**:

```python
"""
Centralized exception definitions for coffee_maker.

All exceptions are defined here to avoid duplication and provide
a single source of truth for error handling.
"""

# ============================================================
# Base Exceptions
# ============================================================

class CoffeeMakerError(Exception):
    """Base exception for all coffee_maker errors."""
    pass


# ============================================================
# LLM-Related Exceptions (merged from langfuse_observe)
# ============================================================

class LLMError(CoffeeMakerError):
    """Base exception for LLM-related errors."""
    pass


class ModelNotFoundError(LLMError):
    """Raised when requested model is not available."""
    pass


class RateLimitError(LLMError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after  # Seconds until retry allowed


class CostBudgetError(LLMError):
    """Raised when cost budget is exceeded."""
    pass


class ProviderError(LLMError):
    """Raised when LLM provider returns an error."""
    def __init__(self, message, provider, status_code=None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


# ============================================================
# Configuration Exceptions
# ============================================================

class ConfigError(CoffeeMakerError):
    """Base exception for configuration errors."""
    pass


class InvalidConfigError(ConfigError):
    """Raised when configuration is invalid."""
    pass


# ============================================================
# Observability Exceptions
# ============================================================

class ObservabilityError(CoffeeMakerError):
    """Base exception for observability errors."""
    pass


class TracingError(ObservabilityError):
    """Raised when Langfuse tracing fails."""
    pass


# ============================================================
# Existing Exceptions (already in coffee_maker/exceptions.py)
# ============================================================

# ... existing exceptions ...
```

**Migration Actions**:
1. Copy exception classes from `langfuse_observe/exceptions.py`
2. Add to appropriate sections in `coffee_maker/exceptions.py`
3. Remove duplicates (merge similar exceptions)
4. Update imports across codebase (~30 files)
5. Delete `langfuse_observe/exceptions.py` (will become `observability/exceptions.py` after rename, then deleted)

---

## Data Flow Diagrams

### Current Data Flow (Before Restructuring)

```
┌──────────────────────────────────────────────────────────────┐
│                        User Code                              │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│   from coffee_maker.langfuse_observe.llm import get_llm      │
│                                                               │
│   (Confusing: why langfuse_observe for LLM creation?)        │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│           coffee_maker/langfuse_observe/                      │
│                                                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │  llm.py   │  │ rate_     │  │ strategies│               │
│  │           │  │ limiter.py│  │    /      │               │
│  │ (no       │  │ (no       │  │ (no       │               │
│  │ @observe) │  │ @observe) │  │ @observe) │               │
│  └───────────┘  └───────────┘  └───────────┘               │
│                                                               │
│  ┌───────────┐  ┌───────────┐                               │
│  │ agents.py │  │ cost_     │                               │
│  │           │  │ calculator│                               │
│  │ (@observe)│  │ (@observe)│  ← Only 13% use @observe!   │
│  └───────────┘  └───────────┘                               │
└───────────────────────────────────────────────────────────────┘

Problems:
1. Misleading directory name (langfuse_observe)
2. Mixed concerns (LLM + observability + utilities)
3. Hard to find code (everything in one big directory)
```

### Target Data Flow (After Restructuring)

```
┌──────────────────────────────────────────────────────────────┐
│                        User Code                              │
└────┬──────────────┬──────────────┬──────────────┬────────────┘
     │              │              │              │
     │ LLM          │ Rate         │ Observ-      │ Utils
     │ creation     │ limiting     │ ability      │
     ▼              ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  from   │   │  from   │   │  from   │   │  from   │
│ coffee_ │   │ coffee_ │   │ coffee_ │   │ coffee_ │
│ maker.  │   │ maker.  │   │ maker.  │   │ maker.  │
│ llm     │   │ llm.    │   │ observ- │   │ utils   │
│ import  │   │ rate_   │   │ ability │   │ import  │
│ get_llm │   │ limiting│   │ import  │   │ http_   │
│         │   │ import  │   │ track_  │   │ pool    │
│         │   │ Rate    │   │ agent   │   │         │
│         │   │ Limiter │   │         │   │         │
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │             │             │             │
     ▼             ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   llm/   │ │   llm/   │ │observ-   │ │  utils/  │
│          │ │   rate_  │ │ability/  │ │          │
│ • factory│ │  limiting│ │          │ │ • http_  │
│ • builder│ │          │ │ • agents │ │   pool   │
│ • config │ │ • tracker│ │ • cost_  │ │ • token_ │
│ • provide│ │ • global │ │   calc   │ │   est    │
│   rs     │ │ • budget │ │ • retry  │ │ • parse  │
│ • strat- │ │          │ │          │ │          │
│   egies  │ │          │ │ ALL use  │ │ General  │
│          │ │          │ │ @observe │ │ utils    │
│ Core LLM │ │ Rate     │ │          │ │          │
│ (no      │ │ limits   │ │ Pure     │ │ (no LLM, │
│ @observe)│ │ (no      │ │ observ-  │ │ no       │
│          │ │ @observe)│ │ ability  │ │ @observe)│
└──────────┘ └──────────┘ └──────────┘ └──────────┘

Benefits:
1. Clear, intuitive directory names
2. Separation of concerns (each module has one purpose)
3. Easy to find code (purpose-driven organization)
4. Shallow hierarchy (max 2-3 levels)
```

### Import Update Flow

```
┌─────────────────────────────────────────────────────────────┐
│   Step 1: Automated Import Updates (grep + sed)             │
│                                                              │
│   find . -name "*.py" -exec sed -i '' \                    │
│     's/langfuse_observe\.llm/llm.factory/g' {} +            │
│                                                              │
│   (Repeat for all ~120 import paths)                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│   Step 2: Manual Verification (file by file)                │
│                                                              │
│   For each affected file:                                   │
│   1. Read file                                               │
│   2. Verify imports are correct                             │
│   3. Run file's tests                                        │
│   4. Commit if tests pass                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│   Step 3: Full Test Suite                                   │
│                                                              │
│   pytest tests/ -v --tb=short                               │
│                                                              │
│   All 450+ tests must pass                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Overview

**Total Effort**: 24-32 hours (3-4 days)
**Phases**: 8 sequential phases
**Team**: 1 developer (code_developer autonomous agent)
**Risk Level**: MEDIUM (many import updates, but well-scoped)

### Phase 0: Preparation & Planning (2 hours)

**Objective**: Verify prerequisites, create backup, get user approval

**Tasks**:

1. **Verify Prerequisites** (30 min)
   ```bash
   # Check no pending PRs
   gh pr list --state open | grep -i "langfuse_observe"

   # Verify all tests pass
   pytest tests/ -v

   # Check git status clean
   git status
   ```

2. **Create Backup Branch** (15 min)
   ```bash
   git branch backup-before-us-023
   git push origin backup-before-us-023
   git tag pre-us-023-$(date +%Y%m%d)
   ```

3. **Generate File Inventory** (30 min)
   ```bash
   # List all files to move
   find coffee_maker/langfuse_observe -name "*.py" > us-023-file-inventory.txt

   # Count import occurrences
   grep -r "from coffee_maker.langfuse_observe" coffee_maker tests \
     | wc -l > us-023-import-count.txt
   ```

4. **Create Migration Checklist** (45 min)
   - Document each file move
   - List expected import updates
   - Define rollback procedure
   - Get user approval for plan

**Deliverables**:
- ✅ Backup branch created
- ✅ File inventory generated
- ✅ Migration checklist documented
- ✅ User approval obtained

---

### Phase 1: Create New Directory Structure (1 hour)

**Objective**: Create all new directories with proper `__init__.py` files

**Tasks**:

1. **Create LLM Module Directories** (20 min)
   ```bash
   mkdir -p coffee_maker/llm/{rate_limiting,strategies,providers}
   ```

2. **Create Initial `__init__.py` Files** (40 min)

   File: `coffee_maker/llm/__init__.py`
   ```python
   """
   Core LLM abstractions and factory methods.

   This module provides the main entry point for creating and configuring
   LLM instances across different providers (OpenAI, Anthropic, Gemini).
   """

   # Imports will be added as files are migrated
   __all__ = []
   ```

   File: `coffee_maker/llm/rate_limiting/__init__.py`
   ```python
   """
   Rate limiting and cost budgeting for LLM API calls.
   """

   __all__ = []
   ```

   File: `coffee_maker/llm/strategies/__init__.py`
   ```python
   """
   LLM execution strategies (retry, fallback, scheduling).
   """

   __all__ = []
   ```

   File: `coffee_maker/llm/providers/__init__.py`
   ```python
   """
   LLM provider implementations (OpenAI, Anthropic, Gemini).
   """

   __all__ = []
   ```

3. **Commit Directory Structure** (5 min)
   ```bash
   git add coffee_maker/llm/
   git commit -m "feat(US-023): Create new llm/ module structure

   - Created coffee_maker/llm/ directory
   - Created rate_limiting/, strategies/, providers/ subdirectories
   - Added initial __init__.py files

   Part of US-023: Clear, Intuitive Module Hierarchy

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Deliverables**:
- ✅ `coffee_maker/llm/` directory created
- ✅ All subdirectories created
- ✅ Initial `__init__.py` files added
- ✅ Changes committed to git

**Time Estimate**: 1 hour
**Risk**: LOW

---

### Phase 2: Move LLM Core Files (4-5 hours)

**Objective**: Move 6 core LLM files from `langfuse_observe/` to `llm/`

**Files to Move**:
1. `llm.py` → `llm/factory.py`
2. `builder.py` → `llm/builders.py`
3. `llm_config.py` → `llm/config.py`
4. `scheduled_llm.py` → `llm/scheduled.py`
5. `auto_picker_llm_refactored.py` → `llm/auto_picker.py`
6. `llm_tools.py` → `llm/tools.py`

**Per-File Process** (40-50 min each):

1. **Move File** (5 min)
   ```bash
   git mv coffee_maker/langfuse_observe/llm.py coffee_maker/llm/factory.py
   ```

2. **Update Internal Imports** (10 min)
   - Open `coffee_maker/llm/factory.py`
   - Update any imports from `langfuse_observe` to new paths
   - Example:
     ```python
     # Before
     from coffee_maker.langfuse_observe.rate_limiter import RateLimiter

     # After (will be updated in Phase 3, so use temporary import)
     from coffee_maker.langfuse_observe.rate_limiter import RateLimiter
     # TODO(US-023): Update to coffee_maker.llm.rate_limiting after Phase 3
     ```

3. **Update External Imports** (20 min)
   ```bash
   # Find all files importing this file
   grep -r "from coffee_maker.langfuse_observe.llm import" coffee_maker tests

   # Update each file
   find coffee_maker tests -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.langfuse_observe\.llm import/from coffee_maker.llm.factory import/g' {} +

   # Verify changes
   git diff
   ```

4. **Update `llm/__init__.py`** (5 min)
   ```python
   # Add to coffee_maker/llm/__init__.py
   from coffee_maker.llm.factory import LLM, get_llm

   __all__ = ["LLM", "get_llm"]
   ```

5. **Run Tests** (10 min)
   ```bash
   # Run tests for files that import this module
   pytest tests/ -k "test_llm" -v

   # If tests fail, investigate and fix
   ```

6. **Commit Changes** (5 min)
   ```bash
   git add -A
   git commit -m "feat(US-023): Move llm.py to llm/factory.py

   - Moved coffee_maker/langfuse_observe/llm.py to coffee_maker/llm/factory.py
   - Updated ~40 import statements across codebase
   - Updated llm/__init__.py with new exports
   - All tests passing

   Part of US-023 Phase 2: Move LLM Core Files (1/6)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Repeat for all 6 files** (4-5 hours total)

**Deliverables**:
- ✅ 6 LLM core files moved to `llm/`
- ✅ ~90 import statements updated
- ✅ `llm/__init__.py` exports updated
- ✅ All tests passing after each file
- ✅ 6 commits (one per file)

**Time Estimate**: 4-5 hours
**Risk**: MEDIUM (many imports, but automated updates)

---

### Phase 3: Move Rate Limiting Files (2-3 hours)

**Objective**: Move 3 rate limiting files to `llm/rate_limiting/`

**Files to Move**:
1. `rate_limiter.py` → `llm/rate_limiting/tracker.py`
2. `global_rate_tracker.py` → `llm/rate_limiting/global_tracker.py`
3. `cost_budget.py` → `llm/rate_limiting/budget.py`

**Process**: Same as Phase 2 (40-50 min per file)

**Update** `llm/rate_limiting/__init__.py`:
```python
"""
Rate limiting and cost budgeting for LLM API calls.
"""

from coffee_maker.llm.rate_limiting.tracker import RateLimiter, RateLimitConfig
from coffee_maker.llm.rate_limiting.global_tracker import GlobalRateTracker
from coffee_maker.llm.rate_limiting.budget import CostBudget, BudgetExceededError

__all__ = [
    "RateLimiter",
    "RateLimitConfig",
    "GlobalRateTracker",
    "CostBudget",
    "BudgetExceededError",
]
```

**Deliverables**:
- ✅ 3 rate limiting files moved
- ✅ ~29 import statements updated
- ✅ `llm/rate_limiting/__init__.py` exports updated
- ✅ All tests passing
- ✅ 3 commits

**Time Estimate**: 2-3 hours
**Risk**: LOW (fewer imports than Phase 2)

---

### Phase 4: Move Strategy Files (3-4 hours)

**Objective**: Move 5 strategy files to `llm/strategies/`

**Files to Move**:
1. `strategies/retry.py` → `llm/strategies/retry.py`
2. `strategies/fallback.py` → `llm/strategies/fallback.py`
3. `strategies/scheduling.py` → `llm/strategies/scheduling.py`
4. `strategies/context.py` → `llm/strategies/context.py`
5. `strategies/metrics.py` → `llm/strategies/metrics.py`

**Process**: Same as Phase 2 (40-50 min per file)

**Note**: These files are already in a `strategies/` subdirectory, so the move is simpler:
```bash
git mv coffee_maker/langfuse_observe/strategies/retry.py \
        coffee_maker/llm/strategies/retry.py
```

**Update** `llm/strategies/__init__.py`:
```python
"""
LLM execution strategies (retry, fallback, scheduling).
"""

from coffee_maker.llm.strategies.retry import RetryStrategy, ExponentialBackoffRetry
from coffee_maker.llm.strategies.fallback import FallbackStrategy, ModelFallback
from coffee_maker.llm.strategies.scheduling import SchedulingStrategy, CostOptimizedScheduling
from coffee_maker.llm.strategies.context import ContextManager
from coffee_maker.llm.strategies.metrics import MetricsCollector

__all__ = [
    "RetryStrategy",
    "ExponentialBackoffRetry",
    "FallbackStrategy",
    "ModelFallback",
    "SchedulingStrategy",
    "CostOptimizedScheduling",
    "ContextManager",
    "MetricsCollector",
]
```

**Deliverables**:
- ✅ 5 strategy files moved
- ✅ ~38 import statements updated
- ✅ `llm/strategies/__init__.py` exports updated
- ✅ All tests passing
- ✅ 5 commits

**Time Estimate**: 3-4 hours
**Risk**: LOW (well-defined module boundaries)

---

### Phase 5: Move Provider Files (2 hours)

**Objective**: Move 3 provider files to `llm/providers/`

**Files to Move**:
1. `llm_providers/openai.py` → `llm/providers/openai.py`
2. `llm_providers/gemini.py` → `llm/providers/gemini.py`
3. `llm_providers/__init__.py` → `llm/providers/__init__.py`

**Process**: Same as Phase 2 (30-40 min per file)

**Note**: Check for duplicate with `coffee_maker/ai_providers/` (may need to consolidate)

**Update** `llm/providers/__init__.py`:
```python
"""
LLM provider implementations (OpenAI, Anthropic, Gemini).
"""

from coffee_maker.llm.providers.openai import OpenAIProvider
from coffee_maker.llm.providers.gemini import GeminiProvider

__all__ = ["OpenAIProvider", "GeminiProvider"]
```

**Deliverables**:
- ✅ 3 provider files moved
- ✅ ~14 import statements updated
- ✅ `llm/providers/__init__.py` exports updated
- ✅ All tests passing
- ✅ 3 commits

**Time Estimate**: 2 hours
**Risk**: LOW (few imports)

---

### Phase 6: Move Utility Files (2-3 hours)

**Objective**: Move 4 utility files to `utils/`

**Files to Move**:
1. `http_pool.py` → `utils/http_pool.py`
2. `token_estimator.py` → `utils/token_estimator.py`
3. `response_parser.py` → `utils/response_parser.py`
4. `utils.py` → merge into `utils/__init__.py`

**Process**: Same as Phase 2 (40-50 min per file)

**Update** `utils/__init__.py`:
```python
"""
General utilities for the coffee_maker package.
"""

# Existing exports
from coffee_maker.utils.logging import setup_logger, get_logger
from coffee_maker.utils.time import timestamp, format_duration
from coffee_maker.utils.file_io import read_json, write_json

# NEW exports from langfuse_observe migration
from coffee_maker.utils.http_pool import HTTPConnectionPool
from coffee_maker.utils.token_estimator import estimate_tokens, TokenEstimator
from coffee_maker.utils.response_parser import parse_response, ResponseParser

# Merged from langfuse_observe/utils.py
from coffee_maker.utils.helpers import (
    format_response,
    validate_input,
    # ... other functions from utils.py
)

__all__ = [
    # Existing
    "setup_logger",
    "get_logger",
    "timestamp",
    "format_duration",
    "read_json",
    "write_json",
    # NEW
    "HTTPConnectionPool",
    "estimate_tokens",
    "TokenEstimator",
    "parse_response",
    "ResponseParser",
    # Merged
    "format_response",
    "validate_input",
]
```

**Deliverables**:
- ✅ 4 utility files moved/merged
- ✅ ~24 import statements updated
- ✅ `utils/__init__.py` exports updated
- ✅ All tests passing
- ✅ 4 commits

**Time Estimate**: 2-3 hours
**Risk**: LOW

---

### Phase 7: Rename `langfuse_observe/` to `observability/` (2-3 hours)

**Objective**: Rename remaining directory and update all imports

**Remaining Files** (should only be files using `@observe`):
- `agents.py`
- `cost_calculator.py`
- `retry.py`
- `tools.py`
- `langfuse_logger.py`
- `analytics/` (entire directory)

**Tasks**:

1. **Verify Only Observability Files Remain** (15 min)
   ```bash
   # Check all remaining files use @observe
   grep -r "@observe" coffee_maker/langfuse_observe/

   # List remaining files
   find coffee_maker/langfuse_observe/ -name "*.py"

   # Should only see the 5 core files + analytics
   ```

2. **Rename Directory** (5 min)
   ```bash
   git mv coffee_maker/langfuse_observe coffee_maker/observability
   ```

3. **Update All Imports** (1.5-2 hours)
   ```bash
   # Find all imports
   grep -r "from coffee_maker.langfuse_observe" coffee_maker tests \
     | wc -l  # Should be ~60

   # Update all at once
   find coffee_maker tests -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.langfuse_observe/from coffee_maker.observability/g' {} +

   find coffee_maker tests -name "*.py" -exec sed -i '' \
     's/import coffee_maker\.langfuse_observe/import coffee_maker.observability/g' {} +

   # Verify changes
   git diff | grep "langfuse_observe" | wc -l  # Should be ~120 (2 per import)
   ```

4. **Update `observability/__init__.py`** (30 min)
   ```python
   """
   Langfuse observability and tracing.

   This module contains ONLY code that uses the @observe decorator
   for tracing with Langfuse. All other code has been moved to
   appropriate modules (llm/, utils/, etc.).
   """

   from coffee_maker.observability.agents import track_agent, agent_executor
   from coffee_maker.observability.cost_calculator import calculate_cost, CostCalculator
   from coffee_maker.observability.retry import retry_with_backoff, ObservableRetry
   from coffee_maker.observability.tools import track_tool_call, tool_executor
   from coffee_maker.observability.langfuse_logger import LangfuseLogger

   __all__ = [
       "track_agent",
       "agent_executor",
       "calculate_cost",
       "CostCalculator",
       "retry_with_backoff",
       "ObservableRetry",
       "track_tool_call",
       "tool_executor",
       "LangfuseLogger",
   ]
   ```

5. **Run Full Test Suite** (30 min)
   ```bash
   pytest tests/ -v
   # All 450+ tests must pass
   ```

6. **Commit Changes** (5 min)
   ```bash
   git add -A
   git commit -m "feat(US-023): Rename langfuse_observe to observability

   - Renamed coffee_maker/langfuse_observe/ to coffee_maker/observability/
   - Updated ~60 import statements across codebase
   - Updated observability/__init__.py with clear exports
   - All tests passing (450+ tests)

   This directory now contains ONLY files using @observe decorator.
   All other files have been moved to llm/, utils/, etc.

   Part of US-023 Phase 7: Rename to Observability

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Deliverables**:
- ✅ Directory renamed to `observability/`
- ✅ ~60 import statements updated
- ✅ `observability/__init__.py` updated
- ✅ All tests passing
- ✅ 1 commit

**Time Estimate**: 2-3 hours
**Risk**: MEDIUM (many imports, but automated)

---

### Phase 8: Consolidate Exceptions (2 hours)

**Objective**: Merge `observability/exceptions.py` into `coffee_maker/exceptions.py`

**Tasks**:

1. **Read Both Exception Files** (15 min)
   ```bash
   # Review what's in each file
   cat coffee_maker/exceptions.py
   cat coffee_maker/observability/exceptions.py
   ```

2. **Merge Exception Classes** (45 min)
   - Copy exception classes from `observability/exceptions.py`
   - Add to appropriate sections in `coffee_maker/exceptions.py`
   - Remove duplicates
   - Add docstrings
   - Organize by category (see Component Specifications section above)

3. **Update Imports** (30 min)
   ```bash
   # Find all files importing from observability/exceptions.py
   grep -r "from coffee_maker.observability.exceptions import" \
     coffee_maker tests

   # Update to import from coffee_maker.exceptions
   find coffee_maker tests -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.observability\.exceptions import/from coffee_maker.exceptions import/g' {} +

   # Also update old langfuse_observe imports (if any remain)
   find coffee_maker tests -name "*.py" -exec sed -i '' \
     's/from coffee_maker\.langfuse_observe\.exceptions import/from coffee_maker.exceptions import/g' {} +
   ```

4. **Delete Old Exceptions File** (5 min)
   ```bash
   git rm coffee_maker/observability/exceptions.py
   ```

5. **Run Tests** (20 min)
   ```bash
   pytest tests/ -v
   # All tests must pass
   ```

6. **Commit Changes** (5 min)
   ```bash
   git add -A
   git commit -m "feat(US-023): Consolidate exceptions into single file

   - Merged coffee_maker/observability/exceptions.py into coffee_maker/exceptions.py
   - Removed duplicate exception classes
   - Updated ~30 import statements
   - Deleted observability/exceptions.py
   - All tests passing

   Now have single source of truth for all exceptions.

   Part of US-023 Phase 8: Consolidate Exceptions

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Deliverables**:
- ✅ Exceptions merged into `coffee_maker/exceptions.py`
- ✅ ~30 import statements updated
- ✅ `observability/exceptions.py` deleted
- ✅ All tests passing
- ✅ 1 commit

**Time Estimate**: 2 hours
**Risk**: LOW (well-defined exception classes)

---

### Phase 9: Documentation & Final Verification (3-4 hours)

**Objective**: Update all documentation and verify everything works

**Tasks**:

1. **Update README.md** (1 hour)
   - Document new module structure
   - Add import examples
   - Update "Getting Started" section

2. **Update ARCHITECTURE.md** (1 hour)
   - Add module hierarchy diagram
   - Document module responsibilities
   - Add import patterns

3. **Create Migration Guide** (1 hour)
   - Document breaking changes for external users
   - Provide before/after examples
   - Add migration script

4. **Final Test Verification** (30 min)
   ```bash
   # Run full test suite
   pytest tests/ -v --cov=coffee_maker

   # Check coverage hasn't dropped
   pytest tests/ --cov=coffee_maker --cov-report=html
   ```

5. **Update CLAUDE.md** (30 min)
   - Document new module structure
   - Update import examples in instructions
   - Add module organization principles

**Deliverables**:
- ✅ README.md updated
- ✅ ARCHITECTURE.md updated
- ✅ Migration guide created (`docs/US-023_MIGRATION_GUIDE.md`)
- ✅ CLAUDE.md updated
- ✅ All tests passing with good coverage
- ✅ 1 commit

**Time Estimate**: 3-4 hours
**Risk**: LOW (documentation only)

---

### Summary of Phases

| Phase | Description | Time | Risk | Files Moved | Imports Updated |
|-------|-------------|------|------|-------------|-----------------|
| 0 | Preparation & Planning | 2h | LOW | 0 | 0 |
| 1 | Create Directory Structure | 1h | LOW | 0 | 0 |
| 2 | Move LLM Core Files | 4-5h | MED | 6 | ~90 |
| 3 | Move Rate Limiting | 2-3h | LOW | 3 | ~29 |
| 4 | Move Strategies | 3-4h | LOW | 5 | ~38 |
| 5 | Move Providers | 2h | LOW | 3 | ~14 |
| 6 | Move Utilities | 2-3h | LOW | 4 | ~24 |
| 7 | Rename to Observability | 2-3h | MED | 0 | ~60 |
| 8 | Consolidate Exceptions | 2h | LOW | 1 (merge) | ~30 |
| 9 | Documentation & Verification | 3-4h | LOW | 0 | 0 |
| **TOTAL** | | **24-32h** | **MED** | **22** | **~285** |

---

## Testing Strategy

### Test Categories

1. **Unit Tests** - Test individual modules in isolation
2. **Integration Tests** - Test module interactions
3. **Import Tests** - Verify all imports work
4. **Regression Tests** - Ensure no functionality broken
5. **Coverage Tests** - Maintain >80% code coverage

### Testing Phases

#### Phase-by-Phase Testing (During Implementation)

**After Each File Move**:
```bash
# Run tests for affected modules
pytest tests/unit/test_llm.py -v

# If tests fail, fix before moving to next file
# DO NOT accumulate test failures
```

**After Each Phase**:
```bash
# Run full unit test suite
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# All tests must pass before proceeding to next phase
```

#### Comprehensive Testing (After All Phases)

**1. Full Test Suite**:
```bash
# Run ALL tests
pytest tests/ -v --tb=short

# Expected: All 450+ tests pass
```

**2. Coverage Analysis**:
```bash
# Check code coverage
pytest tests/ --cov=coffee_maker --cov-report=term-missing

# Expected: Coverage >= 80% (should not drop from before)
```

**3. Import Verification**:
```bash
# Verify all new imports work
python -c "from coffee_maker.llm import get_llm; print('✅ llm')"
python -c "from coffee_maker.llm.rate_limiting import RateLimiter; print('✅ rate_limiting')"
python -c "from coffee_maker.llm.strategies import RetryStrategy; print('✅ strategies')"
python -c "from coffee_maker.llm.providers import OpenAIProvider; print('✅ providers')"
python -c "from coffee_maker.observability import track_agent; print('✅ observability')"
python -c "from coffee_maker.utils import HTTPConnectionPool; print('✅ utils')"

# All should print ✅
```

**4. Module Isolation Tests**:
```bash
# Test each module can be imported independently
python -c "import coffee_maker.llm; print(dir(coffee_maker.llm))"
python -c "import coffee_maker.observability; print(dir(coffee_maker.observability))"
python -c "import coffee_maker.utils; print(dir(coffee_maker.utils))"
```

**5. Backward Compatibility Tests** (if needed):
```bash
# Test deprecated imports still work (if we add compatibility layer)
python -c "from coffee_maker.langfuse_observe.llm import get_llm; print('WARN: deprecated')"
# Should either work (with deprecation warning) or fail with helpful message
```

### Test Automation

**Pre-commit Hook** (add to `.pre-commit-config.yaml`):
```yaml
- repo: local
  hooks:
    - id: test-imports
      name: Verify all imports work
      entry: python -c "from coffee_maker.llm import get_llm; from coffee_maker.observability import track_agent"
      language: system
      pass_filenames: false
```

**CI/CD Pipeline** (update `.github/workflows/test.yml`):
```yaml
- name: Test US-023 Module Structure
  run: |
    pytest tests/ -v
    python scripts/verify_us023_imports.py  # Custom verification script
```

### Test Metrics

**Before US-023**:
- Total tests: 450
- Pass rate: 100%
- Coverage: 82%
- Import depth: 4-5 levels

**After US-023** (targets):
- Total tests: 450 (unchanged)
- Pass rate: 100% (must maintain)
- Coverage: ≥82% (must not drop)
- Import depth: 2-3 levels (improved)

### Regression Test Checklist

**Critical Functionality to Verify**:

- [ ] LLM creation works: `get_llm("openai", "gpt-4")`
- [ ] Rate limiting enforced: `RateLimiter(60).acquire()`
- [ ] Fallback strategies work: `SmartLLM.with_fallback()`
- [ ] Observability tracing works: `@track_agent("test")`
- [ ] Cost calculation works: `calculate_cost(usage)`
- [ ] Token estimation works: `estimate_tokens("text")`
- [ ] HTTP pooling works: `HTTPConnectionPool.get_instance()`
- [ ] All exceptions importable: `from coffee_maker.exceptions import RateLimitError`

### Test Data Fixtures

**Create Test Fixtures** (in `tests/fixtures/us_023.py`):
```python
"""
Test fixtures for US-023 module restructuring.

Provides test data and helper functions for verifying
the new module structure works correctly.
"""

import pytest
from coffee_maker.llm import get_llm
from coffee_maker.llm.rate_limiting import RateLimiter
from coffee_maker.observability import track_agent

@pytest.fixture
def mock_llm():
    """Mock LLM instance for testing."""
    return get_llm("mock", "test-model")

@pytest.fixture
def rate_limiter():
    """Rate limiter instance for testing."""
    return RateLimiter(requests_per_minute=60)

# Add more fixtures as needed
```

---

## Security Considerations

### 1. API Key Management

**Risk**: Moving files might expose API keys in commit history

**Mitigation**:
- ✅ Already using environment variables (no hardcoded keys)
- ✅ `.env` files in `.gitignore`
- ✅ Using `python-dotenv` for key loading
- ⚠️ Verify no keys accidentally committed during moves

**Action**:
```bash
# Before each commit, check for exposed keys
git diff | grep -i "api_key\|secret\|password"

# If any found, abort commit and fix
```

### 2. Import Security

**Risk**: Circular imports could cause security checks to be bypassed

**Mitigation**:
- Design module hierarchy to prevent circular imports
- Use dependency injection where needed
- Test import order doesn't affect security

**Action**:
```bash
# Detect circular imports
python -m pytest tests/ --import-mode=importlib -v

# Check for circular dependencies
poetry run pydeps coffee_maker --max-bacon=2
```

### 3. Exception Handling Security

**Risk**: Consolidating exceptions might expose sensitive error details

**Mitigation**:
- Review all exception messages
- Ensure no sensitive data in exception strings
- Add sanitization for user-facing errors

**Action**:
```python
# Example: Sanitize error messages
class ProviderError(LLMError):
    def __init__(self, message, provider, status_code=None):
        # Don't expose API keys or tokens in error messages
        sanitized_message = self._sanitize(message)
        super().__init__(sanitized_message)
        self.provider = provider
        self.status_code = status_code

    def _sanitize(self, message):
        # Remove API keys, tokens, etc.
        import re
        return re.sub(r'sk-[a-zA-Z0-9]+', 'sk-***', message)
```

### 4. Rate Limiting Security

**Risk**: Moving rate limiting code might break quota enforcement

**Mitigation**:
- **CRITICAL**: Test rate limiting works after move
- Verify singleton pattern still enforced
- Ensure no way to bypass rate limits

**Action**:
```bash
# Test rate limiting enforcement
pytest tests/security/test_rate_limiting_security.py -v

# Expected: All rate limit bypass attempts blocked
```

### 5. Observability Data Privacy

**Risk**: Observability traces might log sensitive data

**Mitigation**:
- Review all `@observe` decorated functions
- Ensure no PII (Personally Identifiable Information) logged
- Add data redaction for sensitive fields

**Action**:
```python
# Example: Redact sensitive data before tracing
from langfuse.decorators import observe

@observe(metadata={"redact": ["api_key", "password"]})
def track_agent(name, context):
    # Langfuse automatically redacts specified fields
    pass
```

### 6. Dependency Security

**Risk**: New module structure might introduce new dependencies

**Mitigation**:
- ✅ No new external dependencies required
- ✅ Only reorganizing existing code
- ⚠️ Verify `pyproject.toml` unchanged

**Action**:
```bash
# Before US-023
poetry show --tree > before-dependencies.txt

# After US-023
poetry show --tree > after-dependencies.txt

# Verify no changes
diff before-dependencies.txt after-dependencies.txt
# Expected: No differences
```

---

## Performance Requirements

### 1. Import Performance

**Requirement**: Module imports should not significantly slow down startup time

**Current Performance**:
```bash
# Measure current import time
python -c "import time; start = time.time(); from coffee_maker.langfuse_observe import get_llm; print(f'Import time: {time.time()-start:.3f}s')"
# Current: ~0.150s
```

**Target Performance** (after restructuring):
```bash
# Measure new import time
python -c "import time; start = time.time(); from coffee_maker.llm import get_llm; print(f'Import time: {time.time()-start:.3f}s')"
# Target: ≤0.200s (allow 33% slowdown for better organization)
# Ideal: <0.150s (no slowdown)
```

**Optimization**:
- Use lazy imports in `__init__.py` where possible
- Avoid importing heavy dependencies at module level

**Example**:
```python
# coffee_maker/llm/__init__.py

def get_llm(*args, **kwargs):
    # Lazy import to speed up module load time
    from coffee_maker.llm.factory import get_llm as _get_llm
    return _get_llm(*args, **kwargs)

# OR use __getattr__ for lazy loading
def __getattr__(name):
    if name == "get_llm":
        from coffee_maker.llm.factory import get_llm
        return get_llm
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

### 2. Runtime Performance

**Requirement**: No degradation in runtime performance after restructuring

**Metrics to Maintain**:

| Operation | Before | After | Max Degradation |
|-----------|--------|-------|-----------------|
| LLM creation | 50ms | ≤55ms | 10% |
| Rate limit check | 1ms | ≤1.5ms | 50% |
| Token estimation | 5ms | ≤5.5ms | 10% |
| Observability trace | 2ms | ≤2.5ms | 25% |

**Testing**:
```python
# tests/performance/test_us023_performance.py

import time
import pytest
from coffee_maker.llm import get_llm
from coffee_maker.llm.rate_limiting import RateLimiter
from coffee_maker.utils import estimate_tokens

def test_llm_creation_performance():
    """Test LLM creation performance."""
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        llm = get_llm("mock", "test")
    elapsed = time.time() - start
    avg = (elapsed / iterations) * 1000  # Convert to ms

    assert avg <= 55, f"LLM creation too slow: {avg:.2f}ms (target: ≤55ms)"

def test_rate_limiting_performance():
    """Test rate limit checking performance."""
    limiter = RateLimiter(requests_per_minute=6000)  # High limit
    iterations = 1000
    start = time.time()
    for _ in range(iterations):
        limiter.acquire()
    elapsed = time.time() - start
    avg = (elapsed / iterations) * 1000  # Convert to ms

    assert avg <= 1.5, f"Rate limiting too slow: {avg:.2f}ms (target: ≤1.5ms)"

# Run with: pytest tests/performance/test_us023_performance.py -v
```

### 3. Memory Performance

**Requirement**: No increase in memory usage after restructuring

**Metrics**:

| Scenario | Before | After | Max Increase |
|----------|--------|-------|--------------|
| Import all modules | 45MB | ≤50MB | 11% |
| Create 100 LLMs | 120MB | ≤130MB | 8% |
| Full test suite | 250MB | ≤275MB | 10% |

**Testing**:
```bash
# Measure memory usage
poetry run python -m memory_profiler tests/performance/test_memory.py

# Expected: No significant increase
```

### 4. Test Suite Performance

**Requirement**: Test suite should not slow down significantly

**Metrics**:

| Test Category | Before | After | Max Slowdown |
|---------------|--------|-------|--------------|
| Unit tests | 45s | ≤50s | 11% |
| Integration tests | 90s | ≤100s | 11% |
| Full suite | 150s | ≤165s | 10% |

**Monitoring**:
```bash
# Before US-023
pytest tests/ --durations=0 > before-test-times.txt

# After US-023
pytest tests/ --durations=0 > after-test-times.txt

# Compare
diff before-test-times.txt after-test-times.txt
```

---

## Risk Analysis

### Risk Matrix

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|----------|--------|----------|------------|
| **Breaking external imports** | HIGH | HIGH | 🔴 CRITICAL | Provide migration guide, deprecation warnings |
| **Test failures** | MEDIUM | HIGH | 🟡 HIGH | Test after each file move, rollback on failure |
| **Circular imports** | LOW | MEDIUM | 🟢 LOW | Design hierarchy carefully, test import order |
| **Performance degradation** | LOW | MEDIUM | 🟢 LOW | Benchmark before/after, optimize if needed |
| **Lost git history** | LOW | LOW | 🟢 LOW | Use `git mv`, verify history with `git log --follow` |
| **Merge conflicts** | MEDIUM | MEDIUM | 🟡 MEDIUM | Code freeze during migration, communicate with team |
| **Documentation drift** | MEDIUM | LOW | 🟢 LOW | Update docs in Phase 9, review thoroughly |

### Detailed Risk Analysis

#### Risk 1: Breaking External Imports 🔴 CRITICAL

**Description**: External code (other projects, examples) importing from old paths will break

**Likelihood**: HIGH (if coffee_maker is used as a library)
**Impact**: HIGH (breaks user code)

**Mitigation Strategies**:

1. **Provide Deprecation Layer** (if needed):
   ```python
   # coffee_maker/langfuse_observe/__init__.py (create as compatibility shim)
   """
   DEPRECATED: This module has been reorganized.

   Please update your imports:
   - from coffee_maker.langfuse_observe.llm import get_llm
   + from coffee_maker.llm import get_llm
   """
   import warnings

   def __getattr__(name):
       warnings.warn(
           "Importing from 'coffee_maker.langfuse_observe' is deprecated. "
           "Please update to 'coffee_maker.llm' or 'coffee_maker.observability'.",
           DeprecationWarning,
           stacklevel=2
       )
       # Re-export from new location
       if name == "get_llm":
           from coffee_maker.llm import get_llm
           return get_llm
       # ... handle other exports
       raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
   ```

2. **Create Migration Guide**:
   - Document all path changes
   - Provide before/after examples
   - Include automated migration script

3. **Semantic Versioning**:
   - Bump MINOR version (1.x.0 → 1.y.0) if breaking changes
   - OR bump MAJOR version (1.x.0 → 2.0.0) if no compatibility layer

**Monitoring**:
```bash
# Check if anyone is importing from old paths (in tests, examples)
grep -r "from coffee_maker.langfuse_observe" examples/ || echo "✅ No external imports found"
```

#### Risk 2: Test Failures 🟡 HIGH

**Description**: Tests fail after moving files, breaking CI/CD

**Likelihood**: MEDIUM (automated import updates should catch most)
**Impact**: HIGH (blocks deployment)

**Mitigation Strategies**:

1. **Test After Each File Move** (see Implementation Plan)
2. **Rollback on Failure**:
   ```bash
   # If tests fail
   git reset --hard HEAD~1  # Rollback last commit
   # Fix issue manually
   # Retry
   ```
3. **Maintain Test Coverage**:
   - Don't delete tests
   - Update test imports in same commit as file move
4. **Use CI/CD**:
   - Run tests automatically on each commit
   - Block merge if tests fail

**Monitoring**:
```bash
# Run tests after each phase
pytest tests/ -v || exit 1  # Fail immediately if tests don't pass
```

#### Risk 3: Circular Imports 🟢 LOW

**Description**: New module structure creates circular dependencies

**Likelihood**: LOW (careful design prevents this)
**Impact**: MEDIUM (runtime import errors)

**Mitigation Strategies**:

1. **Hierarchical Design**:
   ```
   llm/
   ├── factory.py     # Top level (imports from providers, strategies)
   ├── providers/     # Bottom level (no imports from llm/)
   └── strategies/    # Bottom level (no imports from llm/)
   ```

2. **Lazy Imports**:
   ```python
   # Instead of top-level import
   def get_llm(provider, model):
       # Import inside function to break cycle
       from coffee_maker.llm.providers.openai import OpenAIProvider
       # ...
   ```

3. **Dependency Injection**:
   ```python
   # Pass dependencies as parameters instead of importing
   def create_smart_llm(llm_factory, rate_limiter):
       # No imports needed
       pass
   ```

**Monitoring**:
```bash
# Detect circular imports
python -c "import coffee_maker.llm; import coffee_maker.observability; import coffee_maker.utils"
# Should complete without errors
```

#### Risk 4: Performance Degradation 🟢 LOW

**Description**: New structure slows down imports or runtime

**Likelihood**: LOW (same code, just different organization)
**Impact**: MEDIUM (user experience degradation)

**Mitigation Strategies**:

1. **Benchmark Before/After** (see Performance Requirements)
2. **Use Lazy Imports** (see example above)
3. **Profile Critical Paths**:
   ```bash
   python -m cProfile -s time -o profile.stats \
     -c "from coffee_maker.llm import get_llm; get_llm('mock', 'test')"
   python -m pstats profile.stats
   ```

**Monitoring**:
```bash
# Run performance tests
pytest tests/performance/ -v
```

#### Risk 5: Lost Git History 🟢 LOW

**Description**: File history lost after `git mv`

**Likelihood**: LOW (git tracks renames well)
**Impact**: LOW (harder to debug, but not critical)

**Mitigation Strategies**:

1. **Always Use `git mv`** (not `mv` + `git add`)
   ```bash
   # ✅ CORRECT - preserves history
   git mv old/path.py new/path.py

   # ❌ WRONG - loses history
   mv old/path.py new/path.py
   git add new/path.py
   ```

2. **Verify History Preserved**:
   ```bash
   # Check file history after move
   git log --follow new/path.py
   # Should show commits before and after move
   ```

3. **Commit File Moves Separately**:
   - Don't mix file moves with content changes
   - Makes history cleaner

**Monitoring**:
```bash
# After each git mv, verify history
git log --follow coffee_maker/llm/factory.py | head -20
# Should show history from langfuse_observe/llm.py
```

#### Risk 6: Merge Conflicts 🟡 MEDIUM

**Description**: Concurrent work causes merge conflicts

**Likelihood**: MEDIUM (depends on team activity)
**Impact**: MEDIUM (time spent resolving conflicts)

**Mitigation Strategies**:

1. **Code Freeze**:
   - Announce migration in team chat
   - Request no PRs touching `langfuse_observe/` during migration
   - Timeline: 3-4 days

2. **Work in Feature Branch**:
   ```bash
   git checkout -b us-023-module-hierarchy
   # Do all work here
   # Merge to main when complete
   ```

3. **Communicate Progress**:
   - Daily updates on completion percentage
   - Notify when safe to resume normal work

**Monitoring**:
```bash
# Check for conflicts before merging
git fetch origin main
git merge origin/main
# Resolve any conflicts
```

#### Risk 7: Documentation Drift 🟢 LOW

**Description**: Documentation becomes outdated after restructuring

**Likelihood**: MEDIUM (easy to forget docs)
**Impact**: LOW (confuses users, but not breaking)

**Mitigation Strategies**:

1. **Update Docs in Phase 9** (see Implementation Plan)
2. **Checklist of Docs to Update**:
   - [ ] README.md
   - [ ] ARCHITECTURE.md
   - [ ] CLAUDE.md
   - [ ] US-023_MIGRATION_GUIDE.md
   - [ ] API documentation (if using Sphinx/MkDocs)
   - [ ] Examples in `examples/`
   - [ ] Tutorials in `docs/TUTORIALS.md`

3. **Review Checklist**:
   - Grep for old import paths in docs
   - Update all occurrences

**Monitoring**:
```bash
# Check docs for old paths
grep -r "langfuse_observe" docs/ README.md
# Should return 0 results (except migration guide)
```

### Risk Summary

**Overall Risk Level**: 🟡 **MEDIUM**

**Highest Risks**:
1. 🔴 Breaking external imports (CRITICAL - needs deprecation layer or version bump)
2. 🟡 Test failures (HIGH - mitigated by testing after each move)
3. 🟡 Merge conflicts (MEDIUM - mitigated by code freeze)

**Mitigation Success Criteria**:
- ✅ All tests pass after each phase
- ✅ Git history preserved for all moved files
- ✅ Performance benchmarks within 10% of baseline
- ✅ Documentation fully updated
- ✅ Migration guide created for external users

---

## Success Criteria

### Functional Criteria

**Must Have** (blocking completion):

1. ✅ **All files moved to correct locations**
   - 6 files in `llm/`
   - 3 files in `llm/rate_limiting/`
   - 5 files in `llm/strategies/`
   - 3 files in `llm/providers/`
   - 4 files in `utils/`
   - 5 files in `observability/`
   - 0 files in wrong locations

2. ✅ **All imports updated**
   - 0 references to `langfuse_observe` (except deprecation layer)
   - All imports use new paths
   - All `__init__.py` files have proper exports

3. ✅ **All tests passing**
   - Unit tests: 100% pass rate
   - Integration tests: 100% pass rate
   - Full suite: 100% pass rate
   - Coverage: ≥82% (maintained or improved)

4. ✅ **Git history preserved**
   - `git log --follow` shows full history for all moved files
   - All moves done with `git mv`

5. ✅ **Documentation updated**
   - README.md reflects new structure
   - ARCHITECTURE.md documents module hierarchy
   - Migration guide created
   - CLAUDE.md updated

### Performance Criteria

**Should Have** (nice to have, but not blocking):

1. ✅ **Import performance maintained**
   - Import time: ≤200ms (≤33% slower than before)
   - Ideal: <150ms (no slowdown)

2. ✅ **Runtime performance maintained**
   - LLM creation: ≤55ms (≤10% slower)
   - Rate limiting: ≤1.5ms (≤50% slower)
   - Token estimation: ≤5.5ms (≤10% slower)

3. ✅ **Memory usage maintained**
   - Import all modules: ≤50MB (≤11% increase)
   - Test suite: ≤275MB (≤10% increase)

### Usability Criteria

**Must Have**:

1. ✅ **Intuitive module names**
   - `llm/` for LLM abstractions (not `langfuse_observe/`)
   - `observability/` for tracing (ONLY `@observe` files)
   - `utils/` for utilities

2. ✅ **Clear import paths**
   - Max 2-3 directory levels
   - Example: `from coffee_maker.llm import get_llm` (not `from coffee_maker.langfuse_observe.llm`)

3. ✅ **Explicit exports**
   - All `__init__.py` files have `__all__`
   - Clear documentation in each `__init__.py`

4. ✅ **Discoverable**
   - New user can find LLM code in <30 seconds
   - Directory names match content

### Quality Criteria

**Must Have**:

1. ✅ **No circular imports**
   - All modules can be imported independently
   - `python -c "import coffee_maker.llm"` works

2. ✅ **No duplicate code**
   - Exceptions consolidated into single file
   - No duplicate utilities

3. ✅ **Consistent naming**
   - File names match class names (e.g., `factory.py` exports `get_llm`)
   - Clear, descriptive names throughout

4. ✅ **Code style maintained**
   - Black formatting passes
   - Mypy type checking passes (if used)
   - All pre-commit hooks pass

### Acceptance Test Checklist

**Run this checklist before marking US-023 as complete**:

#### Functional Tests

- [ ] All files moved to new locations (verify with `find coffee_maker/llm -name "*.py"`)
- [ ] Old directory empty or removed (`ls coffee_maker/langfuse_observe/` should be minimal)
- [ ] All imports updated (grep returns 0: `grep -r "from coffee_maker.langfuse_observe" coffee_maker tests`)
- [ ] All tests pass: `pytest tests/ -v` (100% pass rate)
- [ ] Code coverage maintained: `pytest tests/ --cov=coffee_maker` (≥82%)
- [ ] Git history preserved: `git log --follow coffee_maker/llm/factory.py` (shows old commits)

#### Import Tests

- [ ] LLM module imports: `python -c "from coffee_maker.llm import get_llm"`
- [ ] Rate limiting imports: `python -c "from coffee_maker.llm.rate_limiting import RateLimiter"`
- [ ] Strategies import: `python -c "from coffee_maker.llm.strategies import RetryStrategy"`
- [ ] Providers import: `python -c "from coffee_maker.llm.providers import OpenAIProvider"`
- [ ] Observability imports: `python -c "from coffee_maker.observability import track_agent"`
- [ ] Utils imports: `python -c "from coffee_maker.utils import HTTPConnectionPool"`
- [ ] Exceptions import: `python -c "from coffee_maker.exceptions import RateLimitError"`

#### Performance Tests

- [ ] Import performance: <200ms (`python -m timeit -n 1 -r 1 "from coffee_maker.llm import get_llm"`)
- [ ] Runtime performance: Within 10% of baseline (run `pytest tests/performance/`)
- [ ] Memory usage: Within 11% of baseline

#### Documentation Tests

- [ ] README.md updated with new structure
- [ ] ARCHITECTURE.md documents module hierarchy
- [ ] Migration guide created (`docs/architecture/specs/SPEC-023_MIGRATION_GUIDE.md`)
- [ ] CLAUDE.md updated
- [ ] All code examples in docs use new imports

#### Quality Tests

- [ ] No circular imports: All modules import successfully
- [ ] Black formatting: `black --check coffee_maker/` (passes)
- [ ] Type checking: `mypy coffee_maker/` (passes, if used)
- [ ] Pre-commit hooks: `pre-commit run --all-files` (passes)
- [ ] No TODO comments left: `grep -r "TODO(US-023)" coffee_maker/` (0 results)

### Definition of Done

**US-023 is COMPLETE when**:

1. ✅ All files moved to purpose-driven locations
2. ✅ All 120+ imports updated to new paths
3. ✅ All 450+ tests passing at 100% rate
4. ✅ Code coverage ≥82% (maintained)
5. ✅ Git history preserved for all files
6. ✅ Documentation fully updated
7. ✅ Migration guide created
8. ✅ Performance within acceptable ranges (<10% degradation)
9. ✅ No circular imports
10. ✅ User approval obtained for final result

**Acceptance**: architect reviews structure, user_listener gets user approval

---

## Rollback Procedure

### When to Rollback

**Trigger Rollback if**:
- Tests fail after a phase and cannot be fixed within 2 hours
- Performance degradation >20% and cannot be optimized
- Critical bug discovered that blocks development
- User requests rollback

### Rollback Steps

#### Option 1: Rollback Entire US-023 (if early in process)

```bash
# 1. Switch to backup branch
git checkout backup-before-us-023

# 2. Create new branch from backup
git checkout -b rollback-us-023

# 3. Force push to main (with team approval!)
git push origin rollback-us-023:main --force

# 4. Notify team
echo "US-023 rolled back to backup-before-us-023"
```

#### Option 2: Rollback Specific Phase (if late in process)

```bash
# 1. Find commit before failed phase
git log --oneline | grep "Phase N"

# 2. Reset to that commit
git reset --hard <commit-hash>

# 3. Fix issue manually
# ... make fixes ...

# 4. Resume from that phase
# Continue with Implementation Plan
```

#### Option 3: Revert Specific Commits (safest)

```bash
# 1. List recent commits
git log --oneline -20

# 2. Revert problematic commits (in reverse order)
git revert <commit-3>
git revert <commit-2>
git revert <commit-1>

# 3. Push revert commits
git push origin roadmap
```

### Post-Rollback Actions

1. **Analyze Failure**:
   - Document what went wrong
   - Identify root cause
   - Update technical spec with lessons learned

2. **Communicate**:
   - Notify team of rollback
   - Explain reason for rollback
   - Provide timeline for retry (if applicable)

3. **Plan Retry**:
   - Fix identified issues
   - Update Implementation Plan
   - Get user approval for revised plan
   - Retry US-023 with improvements

### Rollback Prevention

**To minimize rollback risk**:

1. ✅ Test after each file move (don't accumulate failures)
2. ✅ Commit small, atomic changes (easier to revert)
3. ✅ Create backup branch before starting
4. ✅ Use feature branch (not directly on `main` or `roadmap`)
5. ✅ Get user approval at key milestones

---

## Appendix A: Complete Import Mapping

**Before → After Import Changes**

| Before (Old Path) | After (New Path) | Count |
|-------------------|------------------|-------|
| `from coffee_maker.langfuse_observe.llm import` | `from coffee_maker.llm.factory import` | ~40 |
| `from coffee_maker.langfuse_observe.builder import` | `from coffee_maker.llm.builders import` | ~15 |
| `from coffee_maker.langfuse_observe.llm_config import` | `from coffee_maker.llm.config import` | ~10 |
| `from coffee_maker.langfuse_observe.rate_limiter import` | `from coffee_maker.llm.rate_limiting.tracker import` | ~15 |
| `from coffee_maker.langfuse_observe.global_rate_tracker import` | `from coffee_maker.llm.rate_limiting.global_tracker import` | ~8 |
| `from coffee_maker.langfuse_observe.cost_budget import` | `from coffee_maker.llm.rate_limiting.budget import` | ~6 |
| `from coffee_maker.langfuse_observe.strategies.retry import` | `from coffee_maker.llm.strategies.retry import` | ~10 |
| `from coffee_maker.langfuse_observe.strategies.fallback import` | `from coffee_maker.llm.strategies.fallback import` | ~12 |
| `from coffee_maker.langfuse_observe.http_pool import` | `from coffee_maker.utils.http_pool import` | ~10 |
| `from coffee_maker.langfuse_observe.token_estimator import` | `from coffee_maker.utils.token_estimator import` | ~8 |
| `from coffee_maker.langfuse_observe.agents import` | `from coffee_maker.observability.agents import` | ~15 |
| `from coffee_maker.langfuse_observe.cost_calculator import` | `from coffee_maker.observability.cost_calculator import` | ~20 |
| `from coffee_maker.langfuse_observe.exceptions import` | `from coffee_maker.exceptions import` | ~30 |

**Simplified Imports** (using `__init__.py` exports):

| Complex Import | Simplified Import |
|----------------|-------------------|
| `from coffee_maker.llm.factory import get_llm` | `from coffee_maker.llm import get_llm` |
| `from coffee_maker.llm.rate_limiting.tracker import RateLimiter` | `from coffee_maker.llm.rate_limiting import RateLimiter` |
| `from coffee_maker.llm.strategies.retry import RetryStrategy` | `from coffee_maker.llm.strategies import RetryStrategy` |
| `from coffee_maker.observability.agents import track_agent` | `from coffee_maker.observability import track_agent` |

---

## Appendix B: File-by-File Move Commands

**Complete list of git commands for implementation**:

```bash
# Phase 1: Create directories
mkdir -p coffee_maker/llm/{rate_limiting,strategies,providers}

# Phase 2: Move LLM core files
git mv coffee_maker/langfuse_observe/llm.py coffee_maker/llm/factory.py
git mv coffee_maker/langfuse_observe/builder.py coffee_maker/llm/builders.py
git mv coffee_maker/langfuse_observe/llm_config.py coffee_maker/llm/config.py
git mv coffee_maker/langfuse_observe/scheduled_llm.py coffee_maker/llm/scheduled.py
git mv coffee_maker/langfuse_observe/auto_picker_llm_refactored.py coffee_maker/llm/auto_picker.py
git mv coffee_maker/langfuse_observe/llm_tools.py coffee_maker/llm/tools.py

# Phase 3: Move rate limiting
git mv coffee_maker/langfuse_observe/rate_limiter.py coffee_maker/llm/rate_limiting/tracker.py
git mv coffee_maker/langfuse_observe/global_rate_tracker.py coffee_maker/llm/rate_limiting/global_tracker.py
git mv coffee_maker/langfuse_observe/cost_budget.py coffee_maker/llm/rate_limiting/budget.py

# Phase 4: Move strategies
git mv coffee_maker/langfuse_observe/strategies/retry.py coffee_maker/llm/strategies/retry.py
git mv coffee_maker/langfuse_observe/strategies/fallback.py coffee_maker/llm/strategies/fallback.py
git mv coffee_maker/langfuse_observe/strategies/scheduling.py coffee_maker/llm/strategies/scheduling.py
git mv coffee_maker/langfuse_observe/strategies/context.py coffee_maker/llm/strategies/context.py
git mv coffee_maker/langfuse_observe/strategies/metrics.py coffee_maker/llm/strategies/metrics.py

# Phase 5: Move providers
git mv coffee_maker/langfuse_observe/llm_providers/openai.py coffee_maker/llm/providers/openai.py
git mv coffee_maker/langfuse_observe/llm_providers/gemini.py coffee_maker/llm/providers/gemini.py
git mv coffee_maker/langfuse_observe/llm_providers/__init__.py coffee_maker/llm/providers/__init__.py

# Phase 6: Move utilities
git mv coffee_maker/langfuse_observe/http_pool.py coffee_maker/utils/http_pool.py
git mv coffee_maker/langfuse_observe/token_estimator.py coffee_maker/utils/token_estimator.py
git mv coffee_maker/langfuse_observe/response_parser.py coffee_maker/utils/response_parser.py
# Note: utils.py requires manual merge into utils/__init__.py

# Phase 7: Rename directory
git mv coffee_maker/langfuse_observe coffee_maker/observability

# Phase 8: Exceptions consolidation (manual merge, then delete)
# Manually merge observability/exceptions.py into coffee_maker/exceptions.py
git rm coffee_maker/observability/exceptions.py
```

---

## Appendix C: Automated Migration Script

**Script to help with import updates** (`scripts/migrate_us023_imports.sh`):

```bash
#!/bin/bash

# US-023 Import Migration Script
# Automatically updates import statements to new module structure

set -e  # Exit on error

echo "🔄 US-023 Import Migration Script"
echo "================================="

# Backup before changes
echo "📦 Creating backup..."
git branch backup-us-023-imports-$(date +%Y%m%d-%H%M%S)

# Phase 1: Update LLM imports
echo "📝 Updating LLM imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.llm import/from coffee_maker.llm.factory import/g' {} +

find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.builder import/from coffee_maker.llm.builders import/g' {} +

# Phase 2: Update rate limiting imports
echo "📝 Updating rate limiting imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.rate_limiter import/from coffee_maker.llm.rate_limiting.tracker import/g' {} +

# Phase 3: Update strategies imports
echo "📝 Updating strategies imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.strategies\./from coffee_maker.llm.strategies./g' {} +

# Phase 4: Update providers imports
echo "📝 Updating providers imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.llm_providers\./from coffee_maker.llm.providers./g' {} +

# Phase 5: Update utils imports
echo "📝 Updating utils imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe\.http_pool import/from coffee_maker.utils.http_pool import/g' {} +

# Phase 6: Update observability imports (after directory rename)
echo "📝 Updating observability imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.langfuse_observe/from coffee_maker.observability/g' {} +

# Phase 7: Update exceptions imports
echo "📝 Updating exceptions imports..."
find coffee_maker tests -name "*.py" -exec sed -i '' \
  's/from coffee_maker\.observability\.exceptions import/from coffee_maker.exceptions import/g' {} +

# Verify changes
echo "✅ Import migration complete!"
echo ""
echo "📊 Summary of changes:"
git diff --stat

echo ""
echo "🧪 Running tests to verify..."
pytest tests/ -v --tb=short

echo ""
echo "✅ All tests passed! Import migration successful."
```

**Usage**:
```bash
chmod +x scripts/migrate_us023_imports.sh
./scripts/migrate_us023_imports.sh
```

---

## Appendix D: Verification Checklist

**Print this checklist and check off items during implementation**:

### Phase 0: Preparation
- [ ] All tests passing before starting
- [ ] Backup branch created (`backup-before-us-023`)
- [ ] File inventory generated
- [ ] User approval obtained

### Phase 1: Create Directories
- [ ] `coffee_maker/llm/` created
- [ ] `coffee_maker/llm/rate_limiting/` created
- [ ] `coffee_maker/llm/strategies/` created
- [ ] `coffee_maker/llm/providers/` created
- [ ] All `__init__.py` files created
- [ ] Changes committed

### Phase 2: Move LLM Core (6 files)
- [ ] `llm.py` → `llm/factory.py` (commit, tests pass)
- [ ] `builder.py` → `llm/builders.py` (commit, tests pass)
- [ ] `llm_config.py` → `llm/config.py` (commit, tests pass)
- [ ] `scheduled_llm.py` → `llm/scheduled.py` (commit, tests pass)
- [ ] `auto_picker_llm_refactored.py` → `llm/auto_picker.py` (commit, tests pass)
- [ ] `llm_tools.py` → `llm/tools.py` (commit, tests pass)
- [ ] `llm/__init__.py` updated with exports

### Phase 3: Move Rate Limiting (3 files)
- [ ] `rate_limiter.py` → `llm/rate_limiting/tracker.py` (commit, tests pass)
- [ ] `global_rate_tracker.py` → `llm/rate_limiting/global_tracker.py` (commit, tests pass)
- [ ] `cost_budget.py` → `llm/rate_limiting/budget.py` (commit, tests pass)
- [ ] `llm/rate_limiting/__init__.py` updated

### Phase 4: Move Strategies (5 files)
- [ ] `strategies/retry.py` → `llm/strategies/retry.py` (commit, tests pass)
- [ ] `strategies/fallback.py` → `llm/strategies/fallback.py` (commit, tests pass)
- [ ] `strategies/scheduling.py` → `llm/strategies/scheduling.py` (commit, tests pass)
- [ ] `strategies/context.py` → `llm/strategies/context.py` (commit, tests pass)
- [ ] `strategies/metrics.py` → `llm/strategies/metrics.py` (commit, tests pass)
- [ ] `llm/strategies/__init__.py` updated

### Phase 5: Move Providers (3 files)
- [ ] `llm_providers/openai.py` → `llm/providers/openai.py` (commit, tests pass)
- [ ] `llm_providers/gemini.py` → `llm/providers/gemini.py` (commit, tests pass)
- [ ] `llm_providers/__init__.py` → `llm/providers/__init__.py` (commit, tests pass)
- [ ] `llm/providers/__init__.py` updated

### Phase 6: Move Utilities (4 files)
- [ ] `http_pool.py` → `utils/http_pool.py` (commit, tests pass)
- [ ] `token_estimator.py` → `utils/token_estimator.py` (commit, tests pass)
- [ ] `response_parser.py` → `utils/response_parser.py` (commit, tests pass)
- [ ] `utils.py` merged into `utils/__init__.py` (commit, tests pass)
- [ ] `utils/__init__.py` updated

### Phase 7: Rename to Observability
- [ ] Verified only `@observe` files remain in `langfuse_observe/`
- [ ] Directory renamed: `langfuse_observe/` → `observability/`
- [ ] All imports updated (~60 files)
- [ ] `observability/__init__.py` updated
- [ ] All tests passing (commit)

### Phase 8: Consolidate Exceptions
- [ ] Exceptions merged from `observability/exceptions.py` to `coffee_maker/exceptions.py`
- [ ] All imports updated (~30 files)
- [ ] `observability/exceptions.py` deleted
- [ ] All tests passing (commit)

### Phase 9: Documentation
- [ ] README.md updated
- [ ] ARCHITECTURE.md updated
- [ ] Migration guide created (`docs/architecture/specs/SPEC-023_MIGRATION_GUIDE.md`)
- [ ] CLAUDE.md updated
- [ ] Final test verification (all pass)

### Final Checks
- [ ] No references to `langfuse_observe` (except deprecation layer)
- [ ] All 450+ tests passing
- [ ] Code coverage ≥82%
- [ ] Git history preserved for all files
- [ ] Performance within acceptable ranges
- [ ] User approval obtained

---

**End of SPEC-023: Clear, Intuitive Module Hierarchy**
