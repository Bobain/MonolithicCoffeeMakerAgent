# Refactoring Best Practices

**Purpose**: Proven refactoring patterns and best practices for the MonolithicCoffeeMakerAgent codebase, with real examples from production code.

**Audience**: architect (planning refactorings) and code_developer (executing refactorings)

**Related**: US-044, ARCHITECT_WORKFLOW.md, CODE_DEVELOPER_WORKFLOW.md

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Refactoring Patterns](#refactoring-patterns)
3. [Real Examples from Codebase](#real-examples-from-codebase)
4. [Common Pitfalls](#common-pitfalls)
5. [Testing Strategies](#testing-strategies)
6. [Code Review Checklist](#code-review-checklist)

---

## Core Principles

### 1. Preserve Functionality

**Golden Rule**: Refactoring MUST NOT change external behavior.

```python
# ✅ GOOD: Same inputs produce same outputs
def calculate_total_before(items: List[Item]) -> Decimal:
    total = Decimal("0")
    for item in items:
        total += item.price * item.quantity
    return total

def calculate_total_after(items: List[Item]) -> Decimal:
    """Refactored for clarity - same behavior"""
    return sum(item.price * item.quantity for item in items, start=Decimal("0"))

# ❌ BAD: Changed behavior during refactoring
def calculate_total_broken(items: List[Item]) -> Decimal:
    # ERROR: Changed to float, loses precision!
    return sum(float(item.price) * item.quantity for item in items)
```

### 2. Make Small, Incremental Changes

**Why**: Easier to test, review, and rollback if needed.

```bash
# ✅ GOOD: Incremental commits
git commit -m "Extract price calculation to separate method"
git commit -m "Add type hints to price calculation"
git commit -m "Add unit tests for price calculation"
git commit -m "Extract to separate module"

# ❌ BAD: One massive commit
git commit -m "Refactor entire pricing system"  # 50 files changed
```

### 3. Test After Each Step

Run tests continuously during refactoring:

```bash
# Run tests after EVERY significant change
pytest tests/unit/test_pricing.py -v

# If tests fail, revert immediately
git checkout -- file.py

# Fix the issue, then continue
```

### 4. Use Type Hints

Type hints catch errors during refactoring:

```python
# ✅ GOOD: Type hints catch errors
def process_items(items: List[Item]) -> Dict[str, Decimal]:
    result: Dict[str, Decimal] = {}
    for item in items:
        # MyPy will catch if item doesn't have .name or .price
        result[item.name] = item.price
    return result

# ❌ BAD: No type hints
def process_items(items):  # items could be anything!
    result = {}
    for item in items:
        result[item.name] = item.price  # Runtime error if wrong type
    return result
```

### 5. Follow the Style Guide

Always follow `.gemini/styleguide.md`:

```python
# ✅ GOOD: Follows style guide
def calculate_price(
    base_price: Decimal,
    discount: Decimal,
    tax_rate: Decimal,
) -> Decimal:
    """Calculate final price with discount and tax.

    Args:
        base_price: Original price before adjustments
        discount: Discount amount to subtract
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Final price after discount and tax
    """
    discounted = base_price - discount
    return discounted * (Decimal("1") + tax_rate)

# ❌ BAD: Violates style guide
def calc_price(bp, d, tr):  # No docstring, unclear names
    return (bp - d) * (1 + tr)  # No type hints
```

---

## Refactoring Patterns

### Pattern 1: Extract Method

**When to use**: Function is too long or does multiple things.

**Real Example from chat_interface.py**:

```python
# ❌ BEFORE: get_formatted_status() is complexity D (22)
class DeveloperStatusMonitor:
    def get_formatted_status(self) -> str:
        """1612 lines total, complexity 22 - needs refactoring"""
        # Check daemon status
        # Check git status
        # Check ROADMAP status
        # Format output with colors
        # Add timing information
        # Add progress bars
        # ... 200+ lines of logic mixed together
        pass

# ✅ AFTER: Extract methods
class DeveloperStatusMonitor:
    def get_formatted_status(self) -> str:
        """Main orchestration - complexity reduced to 5"""
        daemon_status = self._get_daemon_status()
        git_status = self._get_git_status()
        roadmap_status = self._get_roadmap_status()
        return self._format_status(daemon_status, git_status, roadmap_status)

    def _get_daemon_status(self) -> DaemonStatus:
        """Focused on daemon - complexity 3"""
        # Only daemon-related logic
        pass

    def _get_git_status(self) -> GitStatus:
        """Focused on git - complexity 2"""
        # Only git-related logic
        pass

    def _get_roadmap_status(self) -> RoadmapStatus:
        """Focused on roadmap - complexity 3"""
        # Only roadmap-related logic
        pass

    def _format_status(
        self,
        daemon: DaemonStatus,
        git: GitStatus,
        roadmap: RoadmapStatus,
    ) -> str:
        """Focused on formatting - complexity 4"""
        # Only formatting logic
        pass
```

**Benefits**:
- Main method now easy to understand (shows "what" not "how")
- Each helper testable in isolation
- Complexity reduced from 22 → 5 for main method
- Can reuse helpers in other contexts

### Pattern 2: Extract Class/Module

**When to use**: Class is too large (>500 lines) or has too many responsibilities.

**Real Example from ai_service.py** (1269 lines):

```python
# ❌ BEFORE: AIService does everything
class AIService:
    """1269 lines - handles conversation, prompts, analysis, streaming, ..."""

    def send_message(self, ...):
        pass

    def stream_message(self, ...):
        pass

    def analyze_code(self, ...):
        pass

    def generate_summary(self, ...):
        pass

    def load_prompt(self, ...):
        pass

    def format_response(self, ...):
        pass

    # ... 30+ more methods

# ✅ AFTER: Split into focused modules
# coffee_maker/ai/conversation.py
class ConversationManager:
    """Handles message sending and streaming"""
    def send_message(self, ...): pass
    def stream_message(self, ...): pass

# coffee_maker/ai/code_analyzer.py
class CodeAnalyzer:
    """Handles code analysis tasks"""
    def analyze_code(self, ...): pass
    def generate_summary(self, ...): pass

# coffee_maker/ai/prompt_manager.py
class PromptManager:
    """Handles prompt loading and formatting"""
    def load_prompt(self, ...): pass
    def format_response(self, ...): pass

# coffee_maker/ai/service.py
class AIService:
    """Orchestrates AI services - now ~200 lines"""
    def __init__(self):
        self.conversation = ConversationManager()
        self.analyzer = CodeAnalyzer()
        self.prompts = PromptManager()
```

**Benefits**:
- Each class has single responsibility
- Easier to test each component
- Can swap implementations
- Clearer boundaries and ownership

### Pattern 3: Replace Conditionals with Polymorphism

**When to use**: Long if/elif chains or complex conditionals.

**Example from project**:

```python
# ❌ BEFORE: Complex conditionals
def handle_command(self, command: str) -> str:
    if command.startswith("/roadmap"):
        return self._handle_roadmap(command)
    elif command.startswith("/status"):
        return self._handle_status(command)
    elif command.startswith("/daemon"):
        return self._handle_daemon(command)
    elif command.startswith("/git"):
        return self._handle_git(command)
    # ... 20+ more elif branches
    else:
        return self._handle_unknown(command)

# ✅ AFTER: Command pattern with registry
class Command(ABC):
    @abstractmethod
    def execute(self, args: List[str]) -> str:
        pass

class RoadmapCommand(Command):
    def execute(self, args: List[str]) -> str:
        # Roadmap logic
        pass

class StatusCommand(Command):
    def execute(self, args: List[str]) -> str:
        # Status logic
        pass

class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, Command] = {
            "/roadmap": RoadmapCommand(),
            "/status": StatusCommand(),
            "/daemon": DaemonCommand(),
            "/git": GitCommand(),
            # ... register all commands
        }

    def execute(self, command_str: str) -> str:
        cmd_name = command_str.split()[0]
        command = self._commands.get(cmd_name)
        if command is None:
            return self._handle_unknown(command_str)
        args = command_str.split()[1:]
        return command.execute(args)
```

**Benefits**:
- Each command is isolated and testable
- Easy to add new commands without modifying existing code
- Follows Open/Closed Principle
- Complexity reduced from 15+ to 3-5 per method

### Pattern 4: Introduce Parameter Object

**When to use**: Functions have too many parameters (>4).

```python
# ❌ BEFORE: Too many parameters
def create_notification(
    agent_id: str,
    message: str,
    priority: str,
    sound: bool,
    timestamp: datetime,
    metadata: Dict[str, Any],
    expiry: Optional[datetime],
    retry_count: int,
) -> None:
    pass

# ✅ AFTER: Parameter object
@dataclass
class NotificationConfig:
    """Configuration for creating a notification"""
    agent_id: str
    message: str
    priority: str = "normal"
    sound: bool = False
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None
    retry_count: int = 0

def create_notification(config: NotificationConfig) -> None:
    """Now takes single parameter object"""
    timestamp = config.timestamp or datetime.now()
    # Use config.agent_id, config.message, etc.
    pass

# Usage is clearer
config = NotificationConfig(
    agent_id="architect",
    message="Refactoring plan ready",
    priority="high",
    sound=False,
)
create_notification(config)
```

### Pattern 5: Replace Magic Numbers with Constants

```python
# ❌ BEFORE: Magic numbers everywhere
def check_complexity(file_path: str) -> bool:
    complexity = calculate_complexity(file_path)
    if complexity > 20:  # What's 20?
        return False
    if len(read_file(file_path)) > 2000:  # What's 2000?
        return False
    return True

# ✅ AFTER: Named constants
class CodeQualityThresholds:
    """Thresholds for code quality metrics (from CFR-007)"""
    MAX_COMPLEXITY_SCORE = 20
    MAX_FILE_LINES = 2000
    MAX_FUNCTION_LINES = 100
    MIN_TEST_COVERAGE = 0.8
    MIN_PYLINT_SCORE = 7.0

def check_complexity(file_path: str) -> bool:
    """Check if file meets complexity thresholds"""
    complexity = calculate_complexity(file_path)
    if complexity > CodeQualityThresholds.MAX_COMPLEXITY_SCORE:
        return False

    line_count = len(read_file(file_path))
    if line_count > CodeQualityThresholds.MAX_FILE_LINES:
        return False

    return True
```

---

## Real Examples from Codebase

### Example 1: chat_interface.py (1612 lines)

**Issue**: File too large, multiple responsibilities.

**Current State**:
- `DeveloperStatusMonitor` class: 134 lines, complexity D (22)
- `ProjectManagerCompleter` class: handles completions
- `ChatSession` class: 1100+ lines, multiple commands

**Refactoring Plan**:

```
Priority: MEDIUM (File >1500 lines)

Tasks:
1. Extract DeveloperStatusMonitor to coffee_maker/monitoring/status_monitor.py
   - Reduces chat_interface.py by ~134 lines
   - Makes monitoring logic reusable

2. Extract ProjectManagerCompleter to coffee_maker/cli/completers.py
   - Reduces chat_interface.py by ~100 lines
   - Allows other CLI tools to reuse completers

3. Split ChatSession._handle_command() method
   - Extract command registry pattern
   - Reduce complexity from 11 to <5

Target: Reduce from 1612 lines to <800 lines
```

### Example 2: continuous_work_loop.py (1248 lines)

**Issue**: Large file, single module with multiple concerns.

**Current State**:
- ContinuousWorkLoop class handles orchestration
- Also contains coordinator logic, state management, metrics

**Refactoring Plan**:

```
Priority: MEDIUM

Tasks:
1. Extract WorkLoopState to coffee_maker/orchestrator/state/work_loop_state.py
   - Separate state management from business logic

2. Extract metrics tracking to coffee_maker/orchestrator/metrics.py
   - Isolate metrics calculation and reporting

3. Extract coordinators to separate modules:
   - coffee_maker/orchestrator/coordinators/architect_coordinator.py
   - coffee_maker/orchestrator/coordinators/developer_coordinator.py

Target: Reduce from 1248 lines to <500 lines for main module
```

### Example 3: status_report_generator.py (1093 lines)

**Issue**: Report generator does too much.

**Refactoring Approach**:

```python
# ✅ Split into focused modules

# coffee_maker/reports/data_collectors/git_collector.py
class GitDataCollector:
    """Collects git statistics"""
    def collect_commit_stats(self) -> GitStats: pass
    def collect_branch_info(self) -> BranchInfo: pass

# coffee_maker/reports/data_collectors/roadmap_collector.py
class RoadmapDataCollector:
    """Collects ROADMAP statistics"""
    def collect_priority_stats(self) -> PriorityStats: pass
    def collect_completion_metrics(self) -> CompletionMetrics: pass

# coffee_maker/reports/formatters/markdown_formatter.py
class MarkdownReportFormatter:
    """Formats reports as Markdown"""
    def format_report(self, data: ReportData) -> str: pass

# coffee_maker/reports/status_report_generator.py (now ~200 lines)
class StatusReportGenerator:
    """Orchestrates report generation"""
    def __init__(self):
        self.git_collector = GitDataCollector()
        self.roadmap_collector = RoadmapDataCollector()
        self.formatter = MarkdownReportFormatter()

    def generate_report(self) -> str:
        git_data = self.git_collector.collect_commit_stats()
        roadmap_data = self.roadmap_collector.collect_priority_stats()
        return self.formatter.format_report(git_data, roadmap_data)
```

---

## Common Pitfalls

### Pitfall 1: Changing Behavior During Refactoring

```python
# ❌ DANGER: Behavior changed during refactoring
def process_items_before(items):
    """Returns None if items empty"""
    if not items:
        return None
    return sum(item.price for item in items)

def process_items_after(items):
    """ERROR: Now returns 0 instead of None!"""
    return sum(item.price for item in items)  # sum([]) = 0

# ✅ CORRECT: Preserve exact behavior
def process_items_after(items):
    """Returns None if items empty - behavior preserved"""
    if not items:
        return None
    return sum(item.price for item in items)
```

### Pitfall 2: Breaking Public API

```python
# ❌ DANGER: Breaking change
class OldAPI:
    def get_status(self) -> str:  # Old signature
        return "status"

class NewAPI:
    def get_status(self, include_details: bool) -> str:  # BREAKING!
        # Callers will get TypeError: missing required argument
        return "status"

# ✅ CORRECT: Preserve backward compatibility
class NewAPI:
    def get_status(self, include_details: bool = False) -> str:
        # Default parameter = backward compatible
        if include_details:
            return "detailed status"
        return "status"
```

### Pitfall 3: Over-Engineering

```python
# ❌ BAD: Over-engineered for simple case
class PriceCalculationStrategyFactoryBuilder:
    """Unnecessarily complex for simple price calculation"""
    def create_builder(self): pass
    def with_strategy(self): pass
    def build_factory(self): pass

# ✅ GOOD: Simple solution for simple problem
def calculate_price(base_price: Decimal, tax_rate: Decimal) -> Decimal:
    """Simple function for simple calculation"""
    return base_price * (Decimal("1") + tax_rate)
```

### Pitfall 4: Forgetting to Update Tests

```python
# After refactoring, ALWAYS update tests

# Old test
def test_process_items():
    from old_module import process_items
    assert process_items([item1]) == 10

# ✅ Update imports and test logic
def test_process_items():
    from new_module.processor import ItemProcessor  # Updated import
    processor = ItemProcessor()  # New interface
    assert processor.process([item1]) == 10  # Updated usage
```

### Pitfall 5: Not Running Full Test Suite

```bash
# ❌ BAD: Only run one test
pytest tests/unit/test_pricing.py  # Passes, but...

# Other tests might be broken!
# pytest tests/integration/test_checkout.py  # FAILS!

# ✅ GOOD: Always run full suite
pytest  # Run ALL tests
pytest --cov=coffee_maker  # Verify coverage maintained
```

---

## Testing Strategies

### 1. Test Before Refactoring

```bash
# Capture baseline - all tests must pass
pytest --tb=short > tests_before.txt
echo $?  # Must be 0 (success)

# If tests fail BEFORE refactoring, fix them first!
```

### 2. Test After Each Change

```bash
# After extracting method
pytest tests/unit/test_module.py::test_extracted_method

# After moving class
pytest tests/unit/test_new_location.py

# After updating imports
pytest tests/unit/test_original_module.py
```

### 3. Test Coverage

```bash
# Coverage MUST NOT decrease
pytest --cov=coffee_maker/module.py --cov-report=term

# Before: 93.2%
# After:  93.2% or higher ✅
# After:  91.0% ❌ ROLLBACK - coverage dropped!
```

### 4. Integration Tests

```bash
# Unit tests pass, but integration?
pytest tests/integration/  # Must also pass

# End-to-end workflow tests
pytest tests/e2e/test_daemon_workflow.py
```

### 5. Manual Testing

For user-facing changes:

```bash
# Test CLI still works
poetry run project-manager /roadmap

# Test daemon still starts
poetry run code-developer --help

# Test real workflow
poetry run code-developer --auto-approve --max-iterations 1
```

---

## Code Review Checklist

When reviewing refactored code (architect's responsibility):

### Functionality
- [ ] All existing tests pass
- [ ] No behavior changes (unless documented)
- [ ] Edge cases still handled
- [ ] Error handling preserved

### Code Quality
- [ ] Complexity reduced (verify with radon)
- [ ] Line count reduced or same
- [ ] Follows style guide (.gemini/styleguide.md)
- [ ] Type hints present and correct
- [ ] Documentation updated

### Testing
- [ ] Test coverage maintained or improved
- [ ] New methods have unit tests
- [ ] Integration tests updated if needed
- [ ] Manual testing performed

### Architecture
- [ ] Follows project patterns (mixins, singletons, etc.)
- [ ] No circular dependencies introduced
- [ ] Imports organized correctly
- [ ] CFRs still satisfied (especially CFR-000, CFR-007)

### Documentation
- [ ] Docstrings updated
- [ ] Comments explain "why" not "what"
- [ ] CHANGELOG.md updated if user-facing
- [ ] Related docs updated (WORKFLOWS.md, etc.)

### Performance
- [ ] No performance regression
- [ ] Resource usage same or better
- [ ] No memory leaks introduced

### Git
- [ ] Commits are logical and incremental
- [ ] Commit messages clear and descriptive
- [ ] No unrelated changes mixed in

---

## Quick Reference

### When to Refactor

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Complexity | >40 | CRITICAL - Refactor this week |
| Complexity | 30-40 | HIGH - Refactor this week |
| Complexity | 20-30 | MEDIUM - Refactor this month |
| File lines | >2000 | HIGH - Split file |
| File lines | 1500-2000 | MEDIUM - Consider splitting |
| Function lines | >100 | MEDIUM - Extract methods |
| Duplication | >3 instances | MEDIUM - Extract common code |
| Test coverage | <80% | HIGH - Add tests |

### Refactoring Commands

```bash
# Check complexity
radon cc coffee_maker/ -a -s | grep -E " [D-F] \("

# Find large files
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10

# Check test coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Run full test suite
pytest

# Check style compliance
black --check coffee_maker/
mypy coffee_maker/
pylint coffee_maker/ --score=y
```

---

## Related Documents

- [ARCHITECT_WORKFLOW.md](./ARCHITECT_WORKFLOW.md) - How to create refactoring plans
- [CODE_DEVELOPER_WORKFLOW.md](./CODE_DEVELOPER_WORKFLOW.md) - How to execute refactorings
- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - Interpreting code quality metrics
- [US-044](../../roadmap/ROADMAP.md#us-044) - Refactoring workflow user story
- [.gemini/styleguide.md](../../../.gemini/styleguide.md) - Project style guide

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Status**: Production ✅
