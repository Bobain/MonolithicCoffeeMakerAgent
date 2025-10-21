---
description: Explain code functionality in accessible terms - files, functions, classes, patterns
---

# Code Explainer Skill

## What This Skill Does

Explain code functionality and structure in clear, accessible terms for architects, developers, and documentation.

**Capabilities**:
- **explain_file**: Summarize what a file does, its purpose, exports, dependencies, and key concepts
- **explain_function**: Detailed explanation of a specific function with parameters, return values, and complexity
- **explain_class**: Detailed explanation of a class with attributes, methods, and purpose
- **explain_pattern**: Explain a code pattern (e.g., "error_handling", "caching")

## When To Use

- Onboarding new team members (understand code structure)
- Creating documentation and architectural guides
- Code reviews (understanding complex functions)
- During refactoring (understanding existing code)
- Generating API documentation

## Instructions

### Explain File
```bash
python scripts/explainer.py explain-file coffee_maker/auth/jwt.py
```

**Output**: Summary, purpose, exports, dependencies, and key concepts for the file

### Explain Function
```bash
python scripts/explainer.py explain-function coffee_maker/auth/jwt.py validate_jwt
```

**Output**: Function summary, parameters, return type, complexity, and exceptions

### Explain Class
```bash
python scripts/explainer.py explain-class coffee_maker/auth/jwt.py JWTValidator
```

**Output**: Class summary, attributes, methods, purpose, and usage

### Explain Pattern
```bash
python scripts/explainer.py explain-pattern error_handling
```

**Output**: Explanation of the error handling pattern used in codebase

## Available Scripts

- `scripts/explainer.py` - Main code explanation engine

## Used By

- **architect**: For understanding and designing around existing code
- **assistant**: For creating documentation and learning resources
- **code_developer**: For understanding existing patterns and best practices

## Example Output

```json
{
  "file": "coffee_maker/auth/jwt.py",
  "summary": "Handles JWT token validation and generation",
  "purpose": "Provides JWT-based authentication mechanisms",
  "exports": [
    {
      "name": "validate_jwt",
      "type": "function",
      "description": "Validates JWT tokens using RS256 algorithm"
    }
  ],
  "dependencies": ["PyJWT", "cryptography"],
  "key_concepts": ["JWT", "Token validation", "RSA signatures"]
}
```
