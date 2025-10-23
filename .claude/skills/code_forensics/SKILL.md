---
description: Deep code pattern analysis, complexity metrics, duplication detection, and architectural structure analysis
---

# Code Forensics Skill

## What This Skill Does

Deep pattern analysis for understanding code structure, complexity, and architectural patterns throughout the codebase.

**Capabilities**:
- **find_patterns**: Identify specific patterns (error handling, caching, validation, logging, async, database, API, testing, security, performance)
- **analyze_complexity**: Measure cyclomatic complexity, lines of code, function/class counts, and average function length
- **identify_duplication**: Find duplicate code patterns and suggest refactoring opportunities
- **architectural_analysis**: Analyze component relationships, dependencies, and imports

## When To Use

- Finding code patterns across the codebase (e.g., "where is error handling implemented?")
- Measuring code complexity and identifying hot spots
- Detecting code duplication for refactoring
- Understanding architectural structure and component dependencies
- Code quality assessments and technical debt analysis
- Pattern enforcement (ensuring consistent approaches)

## Instructions

### Find Patterns
```bash
python scripts/code_forensics.py find_patterns --pattern error_handling
```

Supported patterns: `error_handling`, `caching`, `validation`, `logging`, `async`, `database`, `api`, `testing`, `security`, `performance`

**Output**: Shows count, file locations, and code examples for each pattern

### Analyze Complexity
```bash
python scripts/code_forensics.py analyze_complexity [--file path/to/file.py]
```

**Output**: Complexity metrics per file or entire codebase

### Identify Duplication
```bash
python scripts/code_forensics.py identify_duplication
```

**Output**: Groups of similar code snippets that could be refactored

### Architectural Analysis
```bash
python scripts/code_forensics.py architectural_analysis
```

**Output**: Component structure, functions, classes, and dependencies per component

## Available Scripts

- `scripts/code_forensics.py` - Main forensics analysis engine

## Used By

- **architect**: For code quality assessments and pattern validation
- **code_developer**: For identifying where to add new code and finding patterns to follow
- **assistant**: For code quality documentation and recommendations

## Example Output

```json
{
  "patterns_found": {
    "error_handling": {
      "count": 156,
      "files": ["coffee_maker/auth/jwt.py", "coffee_maker/api/routes.py"],
      "examples": [
        {
          "file": "coffee_maker/auth/jwt.py",
          "line": 45,
          "snippet": "try:\n    token = jwt.decode(...)\nexcept InvalidTokenError:\n    ..."
        }
      ]
    }
  }
}
```
