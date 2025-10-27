---
command: code_reviewer.analyze_complexity
agent: code_reviewer
action: analyze_complexity
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [radon, git]
estimated_duration_seconds: 15
---

# Command: code_reviewer.analyze_complexity

## Purpose

Use radon to analyze code complexity metrics including cyclomatic complexity, cognitive complexity, and maintainability index. This command identifies overly complex functions that are hard to understand and test.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to analyze
review_id: string               # Required - link issues to review
check_cyclomatic: boolean       # Check cyclomatic complexity (default: true)
check_cognitive: boolean        # Check cognitive complexity (default: true)
check_maintainability: boolean  # Check maintainability index (default: true)
complexity_threshold: number    # Warn if >threshold (default: 15)
mi_threshold: number            # Warn if <threshold (default: 60)
exclude_tests: boolean          # Skip test files (default: false)
show_detailed: boolean          # Include complexity breakdown (default: true)
```

## Database Operations

**Query: Insert complexity issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Complexity', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Radon Cyclomatic Complexity

```bash
# Check cyclomatic complexity with JSON output
radon cc coffee_maker/ -a -j 2>&1

# JSON Output Format:
# {
#   "path/to/file.py": {
#     "path/to/file.py.ClassName.method_name": {
#       "classname": "ClassName",
#       "is_method": true,
#       "lineno": 42,
#       "col_offset": 0,
#       "endline": 60,
#       "complexity": 5
#     }
#   }
# }
```

**Complexity Scale**:
- 1-5: Low (simple, easy to maintain)
- 6-10: Medium (moderate, still readable)
- 11-15: High (complex, harder to test)
- 16+: Very High (very complex, refactor needed)

### Radon Maintainability Index

```bash
# Check maintainability index with JSON output
radon mi coffee_maker/ -j 2>&1

# JSON Output Format:
# {
#   "path/to/file.py": 85.3
# }
```

**Maintainability Scale**:
- 80-100: A (Excellent, highly maintainable)
- 60-79: B (Good, fairly maintainable)
- 40-59: C (Fair, some issues)
- 20-39: D (Poor, significant issues)
- 0-19: F (Very Poor, refactor urgently)

### Radon Raw Metrics

```bash
# Get raw metrics for detailed analysis
radon raw coffee_maker/ -j 2>&1

# JSON Output Format:
# {
#   "path/to/file.py": {
#     "loc": 245,
#     "lloc": 180,
#     "sloc": 200,
#     "comments": 15,
#     "multi": 10,
#     "blank": 20
#   }
# }
```

**Metrics**:
- `loc`: Lines of Code (total)
- `lloc`: Logical Lines of Code (actual logic)
- `sloc`: Source Lines of Code (code + comments)
- `comments`: Comment lines
- `multi`: Multi-line strings
- `blank`: Blank lines

## Success Criteria

- ✅ Analyzes cyclomatic complexity for all functions
- ✅ Calculates maintainability index per file
- ✅ Identifies functions exceeding complexity threshold
- ✅ Creates review_issue records for high-complexity code
- ✅ Provides refactoring recommendations
- ✅ Compares with historical data (if available)
- ✅ Completes in <15 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "analysis_duration_seconds": 11.2,
  "complexity_summary": {
    "average_complexity": 3.8,
    "max_complexity": 18,
    "high_complexity_functions": 2,
    "very_high_complexity_functions": 0
  },
  "maintainability_summary": {
    "average_mi": 82.5,
    "rating": "A",
    "files_excellent": 30,
    "files_good": 10,
    "files_fair": 3,
    "files_poor": 0
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Complexity",
      "file_path": "coffee_maker/orchestrator.py",
      "line_number": 42,
      "function_name": "execute_workflow",
      "metric": "cyclomatic_complexity",
      "current_value": 18,
      "threshold": 15,
      "description": "Function 'execute_workflow' has cyclomatic complexity of 18 (exceeds threshold of 15)",
      "recommendation": "Extract conditional logic into separate functions or use strategy pattern",
      "suggested_refactor": "Break into 3-4 smaller functions with single responsibility"
    },
    {
      "id": "ISS-2",
      "severity": "MEDIUM",
      "category": "Complexity",
      "file_path": "coffee_maker/database.py",
      "line_number": null,
      "metric": "maintainability_index",
      "current_value": 58.2,
      "threshold": 60,
      "description": "File maintainability index is 58.2 (slightly below ideal 60)",
      "recommendation": "Review complex functions and add documentation",
      "estimated_fix_time": "1-2 hours"
    }
  ],
  "complexity_distribution": {
    "complexity_1_5": 150,
    "complexity_6_10": 35,
    "complexity_11_15": 8,
    "complexity_16_plus": 2
  },
  "top_complex_functions": [
    {
      "function": "orchestrator.execute_workflow",
      "complexity": 18,
      "location": "coffee_maker/orchestrator.py:42"
    },
    {
      "function": "daemon_implementation.process_task",
      "complexity": 14,
      "location": "coffee_maker/autonomous/daemon_implementation.py:88"
    }
  ]
}
```

## Error Handling

**No Complexity Issues Found**:
```json
{
  "status": "success",
  "complexity_summary": {
    "high_complexity_functions": 0
  },
  "message": "All functions within acceptable complexity limits",
  "analysis_duration_seconds": 8.5
}
```

**Radon Not Installed**:
```json
{
  "status": "error",
  "error_type": "TOOL_NOT_FOUND",
  "message": "radon not installed",
  "installation": "pip install radon",
  "exit_code": 1
}
```

**File Parse Error**:
```json
{
  "status": "warning",
  "error": "Could not analyze some files",
  "unparseable_files": ["coffee_maker/generated.py"],
  "analyzed_files": 44,
  "skipped_files": 1
}
```

## Examples

### Example 1: Full complexity analysis

```bash
code_reviewer.analyze_complexity(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_cyclomatic=true,
  check_cognitive=true,
  check_maintainability=true,
  complexity_threshold=15
)
```

### Example 2: Cyclomatic only

```bash
code_reviewer.analyze_complexity(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_cyclomatic=true,
  check_cognitive=false,
  check_maintainability=false
)
```

### Example 3: Strict standards

```bash
code_reviewer.analyze_complexity(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  complexity_threshold=10,  # Lower threshold
  mi_threshold=75          # Higher MI standard
)
```

## Implementation Notes

- Complexity thresholds can be adjusted per project needs
- Historical comparisons (if available) help identify regressions
- Store function-level complexity for trend analysis
- Consider language-specific complexity metrics
- Extract complex logic into separate, testable functions
- High complexity often correlates with bugs and maintenance issues

## Refactoring Recommendations

### Pattern 1: Extract Method

**Before** (complexity = 8):
```python
def process_user(user_id):
    if user.is_admin:
        if user.is_active:
            if user.has_permission("edit"):
                # ... complex logic
            else:
                # ... other logic
        else:
            # ... inactive logic
    else:
        # ... non-admin logic
```

**After** (complexity = 4):
```python
def process_user(user_id):
    if can_edit_user(user_id):
        do_edit(user_id)
    elif is_active_user(user_id):
        do_active_user_processing(user_id)
    else:
        do_inactive_user_processing(user_id)
```

### Pattern 2: Strategy Pattern

**Before** (complexity = 12):
```python
def calculate_price(item, customer_type):
    if customer_type == "PREMIUM":
        price = item.price * 0.8
        if item.qty > 10:
            price *= 0.95
    elif customer_type == "REGULAR":
        price = item.price
        if item.qty > 50:
            price *= 0.9
    elif customer_type == "BULK":
        price = item.price * 0.5
    # ... more conditions
```

**After** (complexity = 3):
```python
class PricingStrategy:
    def calculate(self, item): raise NotImplementedError

class PremiumStrategy(PricingStrategy):
    def calculate(self, item):
        return (item.price * 0.8) * (0.95 if item.qty > 10 else 1)

def calculate_price(item, strategy):
    return strategy.calculate(item)
```

### Pattern 3: Guard Clauses

**Before** (complexity = 5):
```python
def process(user):
    if user is not None:
        if user.is_active:
            if user.has_permission("edit"):
                return do_edit(user)
            else:
                return error("No permission")
        else:
            return error("Inactive user")
    else:
        return error("No user")
```

**After** (complexity = 2):
```python
def process(user):
    if not user:
        return error("No user")
    if not user.is_active:
        return error("Inactive user")
    if not user.has_permission("edit"):
        return error("No permission")
    return do_edit(user)
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.check_style_compliance` - Style analysis
- `code_reviewer.validate_type_hints` - Type safety

---

**Version**: 1.0
**Last Updated**: 2025-10-26
