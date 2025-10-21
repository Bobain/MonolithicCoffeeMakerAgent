# Code Duplication Analysis - US-021 Phase 1

**Date**: 2025-10-11
**Analysis Scope**: Coffee Maker Agent codebase
**Focus**: Exact duplication + Similar patterns with same goals

## Executive Summary

This analysis identifies code duplication and similar patterns across the codebase that can be aggregated and factorized into more maintainable components. Following the principle: "not only code duplication, but similar goals pieces of code."

### Key Findings

1. **Configuration Management**: Scattered across 6+ files with similar goals
2. **Status File I/O**: Duplicated JSON read/write patterns in 5+ files
3. **Error Handling**: Inconsistent patterns across modules
4. **LLM Initialization**: Partially centralized but with scattered fallbacks

---

## 1. Configuration Management Duplication

### Problem: API Key Loading Scattered Across Files

**Similar Goal**: Load API keys from environment variables with validation

#### Pattern A: ANTHROPIC_API_KEY (5 occurrences)

**Files**:
- `coffee_maker/cli/ai_service.py:129` - Load with error message
- `coffee_maker/cli/roadmap_cli.py:478` - Boolean check
- `coffee_maker/cli/assistant_bridge.py:121` - Conditional check
- `coffee_maker/autonomous/claude_api_interface.py:97` - Load with fallback
- `coffee_maker/autonomous/daemon_cli.py:137` - Validation check

**Example Duplication**:
```python
# Pattern repeated 5 times with variations:
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")
```

#### Pattern B: GEMINI_API_KEY (3 variations)

**Files**:
- `coffee_maker/langchain_observe/agents.py:83-86` - Multi-name resolution
- `coffee_maker/auto_gemini_styleguide.py:65-74` - Custom env var name
- `coffee_maker/langchain_observe/llm.py` - Embedded in LLM creation

**Complexity**: Multiple environment variable names for same purpose:
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `COFFEE_MAKER_GEMINI_API_KEY`

#### Pattern C: GITHUB_TOKEN (2 occurrences)

**Files**:
- `coffee_maker/utils/github.py:30-33` - Load and validate
- `coffee_maker/code_formatter/main.py:15` - Documentation reference

### Proposed Solution: Unified ConfigManager

**Create**: `coffee_maker/config/manager.py`

```python
class ConfigManager:
    """Centralized configuration management for all API keys and env vars."""

    @staticmethod
    def get_anthropic_api_key(required: bool = True) -> Optional[str]:
        """Get ANTHROPIC_API_KEY with consistent validation."""

    @staticmethod
    def get_gemini_api_key(required: bool = True) -> str:
        """Resolve Gemini API key from multiple possible names."""

    @staticmethod
    def get_github_token(required: bool = True) -> str:
        """Get GITHUB_TOKEN with consistent validation."""
```

**Benefits**:
- Single source of truth for configuration
- Consistent error messages
- Easy to add caching, validation schemas, defaults
- Testable with mock environment variables

**Estimated Impact**: Eliminate 15+ duplicated code blocks

---

## 2. Status File I/O Duplication

### Problem: JSON File Read/Write Repeated in 5+ Files

**Similar Goal**: Read/write JSON status files with error handling

#### Files with Duplicate Patterns:

1. **coffee_maker/cli/roadmap_cli.py:92, 176**
   ```python
   with open(status_file, "r") as f:
       status = json.load(f)
   ```

2. **coffee_maker/cli/chat_interface.py:234, 245, 304**
   ```python
   with open(self.session_file, "r") as f:
       session_data = json.load(f)
   # ... later ...
   with open(self.session_file, "w") as f:
       json.dump(session_data, f, indent=2)
   ```

3. **coffee_maker/cli/developer_status_display.py:93**
   ```python
   with open(self.status_file) as f:
       status = json.load(f)
   ```

4. **coffee_maker/process_manager.py:265, 340, 348**
   ```python
   with open(self.status_file) as f:
       data = json.load(f)
   # ... later ...
   with open(self.status_file, "w") as f:
       json.dump(data, f, indent=2)
   ```

5. **coffee_maker/autonomous/daemon.py:1172**
   ```python
   with open(status_file, "w") as f:
       json.dump(status_data, f, indent=2)
   ```

### Pattern Analysis

**Common Steps**:
1. Open file
2. Load JSON
3. Handle errors (inconsistently)
4. Optional: Validate schema
5. Return data

**Variations**:
- Some use `encoding="utf-8"`, others don't
- Error handling varies (some try/except, some assume file exists)
- Indent level varies (some use 2, some use 4, some don't specify)
- Some validate schema, others don't

### Proposed Solution: Unified File Utilities

**Create**: `coffee_maker/utils/file_io.py`

```python
def read_json_file(file_path: Path, default: Optional[Dict] = None) -> Dict:
    """Read JSON file with consistent error handling and encoding."""

def write_json_file(file_path: Path, data: Dict, indent: int = 2) -> None:
    """Write JSON file with consistent formatting and error handling."""

def atomic_write_json(file_path: Path, data: Dict) -> None:
    """Write JSON file atomically to prevent corruption."""
```

**Benefits**:
- Consistent error handling
- Atomic writes prevent corruption
- Standard encoding and formatting
- Easy to add validation, backups, migrations

**Estimated Impact**: Eliminate 10+ duplicated code blocks

---

## 3. Error Handling Inconsistencies

### Problem: No Standardized Exception Hierarchy

**Files with Custom Error Handling**:
- `coffee_maker/utils/github.py` - ValueError for missing token
- `coffee_maker/langchain_observe/agents.py` - RuntimeError for missing API key
- `coffee_maker/autonomous/claude_api_interface.py` - Generic Exception
- `coffee_maker/cli/ai_service.py` - ValueError for missing API key

**Issues**:
- Different exception types for same error (configuration error)
- Inconsistent error messages
- Hard to catch specific errors in calling code
- No structured error context

### Proposed Solution: Custom Exception Hierarchy

**Create**: `coffee_maker/exceptions.py`

```python
class CoffeeMakerError(Exception):
    """Base exception for all Coffee Maker errors."""

class ConfigurationError(CoffeeMakerError):
    """Configuration or environment variable errors."""

class APIKeyMissingError(ConfigurationError):
    """Specific API key not found in environment."""

    def __init__(self, key_name: str, suggested_names: Optional[List[str]] = None):
        self.key_name = key_name
        self.suggested_names = suggested_names or []
        super().__init__(f"API key '{key_name}' not found in environment")

class FileOperationError(CoffeeMakerError):
    """File read/write errors."""

class LLMError(CoffeeMakerError):
    """LLM initialization or invocation errors."""
```

**Benefits**:
- Consistent error handling across codebase
- Easy to catch specific error types
- Better error messages with context
- Structured error information for logging

**Estimated Impact**: Standardize 20+ error handling blocks

---

## 4. LLM Initialization Patterns

### Current State: Partially Centralized

**Good**: `coffee_maker/langchain_observe/llm.py` provides centralized LLM creation

**Issues**:
- Some files bypass this and initialize LLMs directly
- Fallback/stub LLM logic duplicated in `agents.py`
- Inconsistent error handling for missing API keys

**Files with Direct LLM Initialization**:
- `coffee_maker/cli/assistant_bridge.py:121-128` - Direct ChatAnthropic/ChatOpenAI
- `coffee_maker/autonomous/claude_api_interface.py:97` - Direct Anthropic()

### Recommendation: Enforce Centralized Pattern

**Action**: Refactor direct initializations to use `get_llm()` from `langchain_observe/llm.py`

**Benefits**:
- Consistent LLM initialization
- Centralized instrumentation with Langfuse
- Single place to add caching, rate limiting, fallbacks

**Estimated Impact**: Eliminate 3-4 direct initialization blocks

---

## 5. Priority Recommendations

### High Priority (Immediate Impact)

1. **Create ConfigManager** (2-3 hours)
   - Consolidate all API key loading
   - Biggest duplication reduction
   - Foundation for other refactoring

2. **Create File I/O Utilities** (1-2 hours)
   - Standardize JSON read/write
   - Prevent file corruption bugs
   - Easy wins with clear benefits

3. **Custom Exception Hierarchy** (1-2 hours)
   - Foundation for consistent error handling
   - Improves debugging experience
   - Easy to implement incrementally

### Medium Priority (Quality of Life)

4. **Refactor Direct LLM Initializations** (1 hour)
   - Enforce centralized pattern
   - Reduce complexity

5. **Status File Schema Validation** (2 hours)
   - Add pydantic models for status files
   - Prevent schema drift
   - Better error messages

### Low Priority (Nice to Have)

6. **Logging Standardization** (2-3 hours)
   - Consistent log levels and formats
   - Structured logging with context

---

## Implementation Plan

### Phase 1: Foundation (Day 1)
1. Create `coffee_maker/config/manager.py`
2. Create `coffee_maker/utils/file_io.py`
3. Create `coffee_maker/exceptions.py`
4. Add comprehensive unit tests

### Phase 2: Migration (Day 2)
5. Migrate API key loading to ConfigManager (15+ files)
6. Migrate JSON I/O to file utilities (10+ files)
7. Replace generic exceptions with custom hierarchy

### Phase 3: Validation (Day 3)
8. Run full test suite
9. Manual testing of critical flows
10. Update documentation

---

## Metrics

**Current State**:
- Duplicated API key loading: 15+ blocks
- Duplicated JSON I/O: 10+ blocks
- Inconsistent error handling: 20+ locations
- Direct LLM initialization: 3-4 locations

**Target State**:
- API key loading: 1 central location (ConfigManager)
- JSON I/O: 1 central location (file_io utilities)
- Error handling: Standardized with custom exceptions
- LLM initialization: All through `get_llm()`

**Expected Reduction**: ~50 duplicated/similar code blocks → ~4 reusable utilities

---

## Notes

This analysis follows the guidance: "not only code duplication, but similar goals pieces of code." The identified patterns show multiple files trying to achieve the same goals (load config, read JSON, handle errors) with slightly different implementations. Aggregating these into reusable utilities will significantly improve maintainability.
