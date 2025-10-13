# Module Organization Guide

**Purpose**: Guidelines for organizing code in the MonolithicCoffeeMakerAgent codebase
**Created**: 2025-10-13
**Status**: Active

---

## Core Principles

### 1. Purpose-Based Organization
**Principle**: Organize code by WHAT it does, not WHERE it came from

**Examples**:
- ✅ `coffee_maker/llm/` - Core LLM abstractions
- ✅ `coffee_maker/observability/` - Langfuse tracing and observability
- ❌ `coffee_maker/langfuse_observe/llm.py` - Mixing concerns

**Rationale**: Developers should know where to find code based on its purpose, not its history.

---

### 2. Clear Separation of Concerns
**Principle**: Each directory should have ONE primary responsibility

**Examples**:
- ✅ `llm/` - LLM creation, configuration, and management
- ✅ `observability/` - Tracing and monitoring
- ✅ `utils/` - General-purpose utilities
- ❌ `langfuse_observe/` containing both tracing AND core LLM logic

**Test**: If you can't describe a directory's purpose in one sentence, it's too broad.

---

### 3. Avoid Redundant Prefixes
**Principle**: Don't repeat the directory name in file names

**Examples**:
- ✅ `llm/factory.py` - Creates LLM instances
- ✅ `llm/rate_limiting/limiter.py` - Rate limiter for LLMs
- ❌ `llm/llm_factory.py` - Redundant "llm_" prefix
- ❌ `utils/utils_helper.py` - Double utility naming

**Rationale**: The directory provides context, so file names can be shorter and clearer.

---

### 4. Public API Through __init__.py
**Principle**: Every package should expose a clear public API via `__init__.py`

**Example**:
```python
# coffee_maker/llm/__init__.py
"""LLM abstraction layer."""

from coffee_maker.llm.factory import get_llm, LLMFactory
from coffee_maker.llm.builder import SmartLLM, LLMBuilder

__all__ = ["get_llm", "LLMFactory", "SmartLLM", "LLMBuilder"]
```

**Benefits**:
- Clear entry points for users
- Hides internal implementation details
- Enables `from coffee_maker.llm import get_llm`

---

### 5. Single Source of Truth
**Principle**: No duplicate files or definitions

**Examples**:
- ✅ One `exceptions.py` in `coffee_maker/`
- ✅ One `retry.py` per use case (observability, strategies, utils)
- ❌ Two `exceptions.py` files (coffee_maker/ and langfuse_observe/)
- ❌ Three `retry.py` files doing the same thing

**Action**: Consolidate duplicates or clarify distinct purposes.

---

## Directory Structure

### Top-Level Directories

```
coffee_maker/
├── ai_providers/        # AI provider wrappers (Claude, OpenAI, Gemini)
├── autonomous/          # Autonomous agent system (daemon, status)
├── cli/                 # Command-line interface (Chat, Roadmap, AI service)
├── config/              # Configuration management (ConfigManager, settings)
├── llm/                 # LLM abstractions (factory, rate limiting, strategies)
├── observability/       # Observability and tracing (Langfuse, analytics)
├── utils/               # General utilities (logging, time, file I/O)
├── streamlit_apps/      # Streamlit applications (analytics, chat, agent UI)
├── code_formatter/      # Code formatting tools
├── langfuse_observe/    # DEPRECATED (use observability/)
└── exceptions.py        # Central exception hierarchy
```

---

### Directory Guidelines

#### coffee_maker/llm/
**Purpose**: Core LLM abstractions and management

**Contains**:
- LLM factory and creation logic
- LLM builder pattern
- Configuration management
- Rate limiting
- Scheduling strategies
- Fallback strategies
- Provider-specific wrappers

**Example files**:
- `factory.py` - LLM creation (`get_llm()`)
- `builder.py` - Builder pattern (`SmartLLM`)
- `config.py` - LLM configuration
- `rate_limiting/limiter.py` - Rate limiter
- `strategies/retry.py` - Retry strategies

**Public API**:
```python
from coffee_maker.llm import get_llm, SmartLLM, LLMBuilder
```

**When to use**:
- Creating or configuring LLMs
- Rate limiting LLM calls
- Implementing LLM strategies (retry, fallback)
- Managing LLM state

**When NOT to use**:
- Observability (use `observability/`)
- General utilities (use `utils/`)
- Provider implementations (use `ai_providers/`)

---

#### coffee_maker/observability/
**Purpose**: Observability, tracing, and monitoring using Langfuse

**Contains**:
- Files using `@observe` decorator
- Langfuse integration
- Cost tracking
- Analytics and metrics
- Tracing utilities

**Example files**:
- `agents.py` - Traceable agents
- `cost_calculator.py` - Cost tracking with @observe
- `retry.py` - Retry logic with tracing
- `analytics/analyzer.py` - Analytics with @observe

**Public API**:
```python
from coffee_maker.observability import TraceableAgent, CostCalculator
```

**When to use**:
- Adding Langfuse tracing to code
- Tracking LLM costs
- Analyzing agent performance
- Exporting trace data

**When NOT to use**:
- Core LLM logic (use `llm/`)
- General logging (use `utils/logging.py`)
- Provider integration (use `ai_providers/`)

**Key Rule**: **ONLY files using `@observe` belong here**

---

#### coffee_maker/utils/
**Purpose**: General-purpose utilities used across the codebase

**Contains**:
- Logging utilities
- Time/date utilities
- File I/O utilities
- HTTP utilities
- Token estimation
- Response parsing

**Example files**:
- `logging.py` - Logging helpers
- `time.py` - Time utilities
- `file_io.py` - File operations
- `http_pool.py` - HTTP connection pooling
- `token_estimator.py` - Token counting

**Public API**:
```python
from coffee_maker.utils.logging import get_logger
from coffee_maker.utils.file_io import read_json, write_json
```

**When to use**:
- General-purpose functionality
- Utilities used by multiple modules
- Cross-cutting concerns (logging, I/O)

**When NOT to use**:
- Domain-specific logic (use domain directories)
- LLM-specific utilities (use `llm/`)
- Observability (use `observability/`)

---

#### coffee_maker/ai_providers/
**Purpose**: AI provider wrappers and implementations

**Contains**:
- Claude provider (Anthropic API)
- OpenAI provider
- Gemini provider
- Provider base classes
- Provider-specific utilities

**Example files**:
- `claude_provider.py` - Claude API wrapper
- `openai_provider.py` - OpenAI API wrapper
- `gemini_provider.py` - Gemini API wrapper

**Public API**:
```python
from coffee_maker.ai_providers import ClaudeProvider, OpenAIProvider
```

**When to use**:
- Implementing provider-specific logic
- API client wrappers
- Provider authentication

**When NOT to use**:
- Generic LLM logic (use `llm/`)
- Rate limiting (use `llm/rate_limiting/`)
- Observability (use `observability/`)

---

#### coffee_maker/autonomous/
**Purpose**: Autonomous agent system (daemon, status tracking)

**Contains**:
- Daemon orchestrator
- Task execution
- Status tracking
- Notification system
- Claude CLI interface

**Example files**:
- `daemon.py` - Main daemon
- `daemon_mixins/` - Daemon mixins (git, specs, implementation)
- `developer_status.py` - Status tracking
- `claude_cli_interface.py` - CLI integration

**Public API**:
```python
from coffee_maker.autonomous import DevDaemon, DeveloperStatus
```

**When to use**:
- Autonomous execution logic
- Daemon management
- Status tracking

**When NOT to use**:
- General CLI commands (use `cli/`)
- Observability (use `observability/`)

---

#### coffee_maker/cli/
**Purpose**: Command-line interface and user-facing tools

**Contains**:
- Chat interface
- Roadmap editor
- AI service
- Notification system
- CLI utilities

**Example files**:
- `chat_interface.py` - Chat UI
- `roadmap_editor.py` - Roadmap management
- `ai_service.py` - AI-powered CLI service
- `notifications.py` - User notifications

**Public API**:
```python
# Usually invoked via CLI, not imported
# poetry run coffee-maker chat
```

**When to use**:
- User-facing commands
- Interactive tools
- CLI utilities

**When NOT to use**:
- Autonomous execution (use `autonomous/`)
- Core logic (use domain directories)

---

#### coffee_maker/config/
**Purpose**: Configuration management

**Contains**:
- ConfigManager (centralized config)
- Settings management
- Environment variable handling
- API key management

**Example files**:
- `manager.py` - ConfigManager class
- `settings.py` - Application settings
- `validation.py` - Config validation

**Public API**:
```python
from coffee_maker.config import ConfigManager
config = ConfigManager()
api_key = config.get_anthropic_api_key()
```

**When to use**:
- Loading configuration
- Managing API keys
- Environment variables

**When NOT to use**:
- LLM configuration (use `llm/config.py`)
- Analytics configuration (use `observability/analytics/config.py`)

---

#### coffee_maker/exceptions.py
**Purpose**: Central exception hierarchy

**Contains**:
- Base `CoffeeMakerError` exception
- Domain-specific exceptions (ConfigError, ProviderError, etc.)
- All custom exceptions

**Public API**:
```python
from coffee_maker.exceptions import ConfigError, ProviderError
```

**When to use**:
- ALWAYS use for exceptions (single source of truth)

**When NOT to use**:
- Never create separate `exceptions.py` files

---

## File Naming Conventions

### General Rules

1. **Use snake_case**: `my_module.py`, not `MyModule.py`
2. **Be descriptive**: `rate_limiter.py`, not `rl.py`
3. **Avoid abbreviations**: `configuration.py`, not `cfg.py` (unless widely known)
4. **No redundant prefixes**: `llm/factory.py`, not `llm/llm_factory.py`

### Package Files

- `__init__.py` - Package initialization and public API
- `_internal.py` - Private/internal utilities (prefix with `_`)
- `base.py` - Base classes for inheritance
- `types.py` - Type definitions and protocols

### Test Files

- `test_*.py` - Unit tests (mirror source structure)
- `*_test.py` - Alternative test naming
- `conftest.py` - Pytest configuration and fixtures

---

## Import Guidelines

### Internal Imports

**Use absolute imports**:
```python
# ✅ Good
from coffee_maker.llm.factory import get_llm
from coffee_maker.observability.agents import TraceableAgent

# ❌ Bad
from ..llm.factory import get_llm  # Relative import
```

**Rationale**: Absolute imports are clearer and more maintainable.

---

### Public API Imports

**Import from package `__init__.py`**:
```python
# ✅ Good (using public API)
from coffee_maker.llm import get_llm, SmartLLM

# ⚠️ Okay (direct import, but less flexible)
from coffee_maker.llm.factory import get_llm

# ❌ Bad (importing from internal module)
from coffee_maker.llm._internal import _helper_function
```

**Rationale**: Public API imports are stable, internal imports may change.

---

### Circular Dependency Prevention

**Use lazy imports**:
```python
# ✅ Good (lazy import inside function)
def get_llm():
    from coffee_maker.ai_providers import ClaudeProvider  # Lazy import
    return ClaudeProvider()

# ❌ Bad (circular dependency risk)
from coffee_maker.ai_providers import ClaudeProvider  # Top-level import
```

**Rationale**: Lazy imports break circular dependencies.

---

### Import Ordering

**Follow PEP 8**:
```python
# 1. Standard library imports
import os
from typing import Dict, List

# 2. Third-party imports
import pytest
from langfuse import Langfuse

# 3. Local imports
from coffee_maker.llm import get_llm
from coffee_maker.config import ConfigManager
```

---

## Module Size Guidelines

### File Size

- **Target**: < 500 lines per file
- **Warning**: > 500 lines (consider splitting)
- **Critical**: > 1000 lines (MUST split)

### Function Size

- **Target**: < 50 lines per function
- **Warning**: > 50 lines (consider extracting helpers)
- **Critical**: > 100 lines (MUST refactor)

### Class Size

- **Target**: < 300 lines per class
- **Warning**: > 300 lines (consider mixins or composition)
- **Critical**: > 500 lines (MUST refactor)

---

## When to Create a New Directory

### Create a new directory when:

1. **Distinct domain**: Code has a clear, focused purpose
2. **Multiple files**: At least 3+ related files
3. **Growth expected**: Will likely add more files
4. **Clear boundaries**: Can define in one sentence

**Examples**:
- `coffee_maker/llm/` - LLM abstractions (distinct domain)
- `coffee_maker/observability/` - Tracing (clear purpose)
- `coffee_maker/autonomous/` - Autonomous agents (distinct domain)

### DON'T create a new directory when:

1. **One file**: Just one or two files (use existing directory)
2. **Unclear purpose**: Can't describe it clearly
3. **Overlapping concerns**: Duplicates existing directory

**Examples**:
- ❌ `coffee_maker/helpers/` - Too generic, use `utils/`
- ❌ `coffee_maker/misc/` - No clear purpose
- ❌ `coffee_maker/stuff/` - Unclear naming

---

## When to Consolidate

### Consolidate files when:

1. **Duplicates**: Same functionality in multiple files
2. **Small files**: Many tiny files (< 50 lines) with related logic
3. **Unclear separation**: Can't explain why files are separate

**Examples**:
- Merge `exceptions.py` files into one central file
- Merge small utility files into a single `utils.py`
- Consolidate `retry.py` variants into one with clear separation

### DON'T consolidate when:

1. **Distinct purposes**: Files serve different use cases
2. **Large result**: Would create a >500 line file
3. **Different domains**: Files belong to different concerns

**Examples**:
- ✅ Keep `observability/retry.py` (uses @observe) separate from `llm/strategies/retry.py` (LLM-specific)
- ✅ Keep `utils/logging.py` separate from `observability/langfuse_logger.py`

---

## Checklist: Where Does This File Belong?

When adding or moving a file, ask:

1. **What is its primary purpose?**
   - LLM logic → `llm/`
   - Observability → `observability/`
   - General utility → `utils/`
   - Provider-specific → `ai_providers/`

2. **Does it use `@observe`?**
   - Yes → `observability/`
   - No → Probably NOT `observability/`

3. **Is it specific to one domain?**
   - Yes → Domain directory (`llm/`, `autonomous/`, etc.)
   - No → `utils/` or top-level

4. **Does it depend on external services?**
   - LLM provider → `ai_providers/`
   - Langfuse → `observability/`
   - GitHub → `cli/github.py` or `autonomous/github_ops.py`

5. **Is it user-facing?**
   - Yes → `cli/` or `streamlit_apps/`
   - No → Internal directory

6. **Is it a base class or interface?**
   - Yes → Domain directory or top-level (e.g., `llm/base.py`)

---

## Examples

### Example 1: Where does rate_limiter.py belong?

**Analysis**:
- Purpose: Rate limiting for LLM calls
- Uses @observe: No
- Domain-specific: Yes (LLMs)
- User-facing: No

**Decision**: `coffee_maker/llm/rate_limiting/limiter.py`

---

### Example 2: Where does cost_calculator.py belong?

**Analysis**:
- Purpose: Calculate and track LLM costs
- Uses @observe: Yes (traces cost calculations)
- Domain-specific: Yes (observability)
- User-facing: No

**Decision**: `coffee_maker/observability/cost_calculator.py`

---

### Example 3: Where does http_pool.py belong?

**Analysis**:
- Purpose: HTTP connection pooling
- Uses @observe: No
- Domain-specific: No (general utility)
- User-facing: No

**Decision**: `coffee_maker/utils/http_pool.py`

---

### Example 4: Where does claude_provider.py belong?

**Analysis**:
- Purpose: Claude API wrapper
- Uses @observe: No (provider logic)
- Domain-specific: Yes (AI provider)
- User-facing: No

**Decision**: `coffee_maker/ai_providers/claude_provider.py`

---

## Anti-Patterns to Avoid

### 1. Dumping Ground Directories
**Problem**: Directories become catch-all for unrelated code

**Examples**:
- ❌ `utils/` containing 50+ files
- ❌ `misc/` or `helpers/` directories
- ❌ `langfuse_observe/` containing non-observability code

**Solution**: Create specific directories for distinct domains

---

### 2. Redundant Naming
**Problem**: File names repeat directory names

**Examples**:
- ❌ `llm/llm_factory.py`
- ❌ `utils/utils_helper.py`
- ❌ `observability/observability_config.py`

**Solution**: Remove redundant prefixes

---

### 3. Duplicate Files
**Problem**: Same functionality in multiple files

**Examples**:
- ❌ Two `exceptions.py` files
- ❌ Three `retry.py` files doing the same thing
- ❌ Multiple `config.py` files

**Solution**: Consolidate or clarify distinct purposes

---

### 4. Unclear Boundaries
**Problem**: Can't explain why code is in a directory

**Examples**:
- ❌ LLM logic in `observability/`
- ❌ Observability logic in `utils/`
- ❌ Mixed concerns in one directory

**Solution**: Reorganize by clear purpose

---

### 5. God Modules
**Problem**: Single file doing too much

**Examples**:
- ❌ 1500-line `daemon.py`
- ❌ 1200-line `chat_interface.py`
- ❌ 900-line `ai_service.py`

**Solution**: Split into smaller, focused modules (use mixins, extract helpers)

---

## Migration Workflow

When reorganizing code:

1. **Create migration plan**: Document what moves where and why
2. **Move in phases**: Don't move everything at once
3. **Test incrementally**: Test after each move
4. **Update imports**: Update imports file-by-file
5. **Update documentation**: Keep docs in sync
6. **Commit frequently**: Small, logical commits
7. **Verify tests**: Run full test suite

**Example**: US-023 Migration Plan (docs/US-023_MIGRATION_PLAN.md)

---

## Summary

**Key Principles**:
1. Organize by purpose, not history
2. One responsibility per directory
3. Avoid redundant prefixes
4. Expose clear public APIs
5. Single source of truth

**Decision Framework**:
- What is its purpose? → Directory
- Does it use @observe? → `observability/`
- Is it domain-specific? → Domain directory
- Is it general? → `utils/`

**Anti-Patterns**:
- Dumping ground directories
- Redundant naming
- Duplicate files
- Unclear boundaries
- God modules

---

**Remember**: Good organization makes code discoverable, maintainable, and extensible. When in doubt, ask: "Where would a new developer look for this code?"

---

**Status**: Active
**Created**: 2025-10-13
**Last Updated**: 2025-10-13
