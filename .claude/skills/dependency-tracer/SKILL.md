---
description: Trace dependencies, analyze impact of changes, and detect circular imports
---

# Dependency Tracer Skill

## What This Skill Does

Analyze dependency relationships to understand code coupling and predict impact of changes.

**Capabilities**:
- **trace_imports**: Find all imports in a specific file (standard library, third-party, internal)
- **find_dependents**: Find all files that depend on/import a module
- **impact_analysis**: Predict what breaks if a file/module is changed
- **circular_dependencies**: Detect circular import chains
- **dependency_graph**: Generate complete dependency graph for the codebase

## When To Use

- Before refactoring code (understand impact)
- During architectural design (identify coupling)
- Code reviews (check dependency health)
- When planning large changes
- Identifying files that can be safely modified

## Instructions

### Trace Imports
```bash
python scripts/tracer.py trace-imports coffee_maker/auth/jwt.py
```

Shows all imports in a file, categorized by type (stdlib, third-party, internal).

### Find Dependents
```bash
python scripts/tracer.py find-dependents coffee_maker/auth/jwt.py
```

Shows all files that import/use the specified module.

### Impact Analysis
```bash
python scripts/tracer.py impact-analysis coffee_maker/auth/jwt.py
```

Predicts what breaks if you change this file.

### Circular Dependencies
```bash
python scripts/tracer.py circular-dependencies
```

Detects circular import chains (should be zero).

### Dependency Graph
```bash
python scripts/tracer.py dependency-graph
```

Generates complete dependency map for the codebase.

## Available Scripts

- `scripts/tracer.py` - Main dependency tracing engine

## Used By

- **architect**: For impact analysis and design decisions
- **code_developer**: For understanding code relationships before refactoring
- **project_manager**: For dependency health monitoring

## Example Output

```json
{
  "file": "coffee_maker/auth/jwt.py",
  "imports": {
    "standard_library": ["os", "sys", "json"],
    "third_party": ["PyJWT", "cryptography"],
    "internal": ["coffee_maker.config", "coffee_maker.utils"]
  },
  "import_details": [
    {
      "module": "PyJWT",
      "imported_as": "jwt",
      "type": "third_party",
      "line": 3
    }
  ]
}
```
