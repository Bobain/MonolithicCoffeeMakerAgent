# code-navigation Skill

**Agents**: user_listener, assistant, assistant (with code analysis skills), architect, code_developer
**Purpose**: Fast, intelligent codebase navigation and symbol lookup
**Location**: `.claude/skills/shared/code-navigation/`

## Overview

Provides efficient navigation capabilities for exploring codebases, finding definitions, locating usages, and understanding code structure. Optimized for speed and accuracy.

## Capabilities

1. **File Finding**: Locate files by name pattern (glob support)
2. **Symbol Search**: Find classes, functions, methods by name
3. **Definition Lookup**: Jump to where symbols are defined
4. **Reference Finder**: Find all usages of a symbol
5. **File Structure**: Analyze file contents (classes, methods, imports)
6. **Smart Suggestions**: Context-aware navigation hints

## Input

```python
{
    "action": "find_file" | "find_symbol" | "get_definition" | "find_references" | "analyze_file",
    "query": "search term or pattern",
    "file_pattern": "*.py" (optional, default: "*.py"),
    "context": "additional context" (optional)
}
```

## Output

### find_file
```python
{
    "files": [
        {"path": "coffee_maker/cli/foo.py", "score": 95},
        {"path": "tests/unit/test_foo.py", "score": 85}
    ],
    "count": 2
}
```

### find_symbol
```python
{
    "symbols": [
        {
            "name": "MyClass",
            "type": "class",
            "file": "coffee_maker/utils/foo.py",
            "line": 42,
            "signature": "class MyClass(BaseClass):"
        }
    ],
    "count": 1
}
```

### get_definition
```python
{
    "definition": {
        "name": "my_function",
        "type": "function",
        "file": "coffee_maker/cli/bar.py",
        "line": 123,
        "signature": "def my_function(arg1: str, arg2: int) -> bool:",
        "docstring": "Does something useful..."
    }
}
```

### find_references
```python
{
    "references": [
        {"file": "coffee_maker/cli/foo.py", "line": 45, "context": "result = my_function(...)"},
        {"file": "tests/test_bar.py", "line": 12, "context": "assert my_function(...) == True"}
    ],
    "count": 2
}
```

### analyze_file
```python
{
    "structure": {
        "imports": ["from pathlib import Path", "import logging"],
        "classes": [
            {"name": "MyClass", "line": 42, "methods": ["__init__", "run"]}
        ],
        "functions": [
            {"name": "helper_func", "line": 15, "signature": "def helper_func(x: int):"}
        ],
        "globals": ["CONSTANT_VALUE = 42"]
    }
}
```

## Usage

```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("code-navigation")

# Find files
result = skill.execute(action="find_file", query="foo.py")

# Find symbol
result = skill.execute(action="find_symbol", query="MyClass")

# Get definition
result = skill.execute(action="get_definition", query="my_function")

# Find all references
result = skill.execute(action="find_references", query="MyClass", file="coffee_maker/utils/foo.py")

# Analyze file structure
result = skill.execute(action="analyze_file", file="coffee_maker/cli/foo.py")
```

## Performance

- **Target**: <2s for most operations
- **Acceptable**: <5s for complex searches
- **Unacceptable**: >10s

## Related

- **assistant agent (with code-forensics and security-audit skills)**: Uses this for deep code analysis
- **assistant agent**: Uses this for quick lookups
- **architect agent**: Uses this for dependency analysis
