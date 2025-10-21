---
description: Find all code related to a specific functional area using 3-level hierarchical code index
---

# Functional Search Skill

## What This Skill Does

Search and browse code by functional area using a 3-level hierarchical index:
- **Level 1**: Functional Categories (Authentication, Database, API, Payment, etc.)
- **Level 2**: Components (JWT Validation, Rate Limiting, etc.)
- **Level 3**: Implementations (specific files, line ranges, code snippets)

**Capabilities**:
- **search**: Find code by functional keyword
- **browse_category**: Browse all components in a functional category
- **browse_component**: View all implementations of a specific component

## When To Use

- Architect designing new features (need to understand existing related code)
- Code_developer implementing features (finding similar code patterns)
- Assistant creating documentation or demos (gathering related code)
- Understanding codebase structure and organization
- Finding where specific functionality is implemented

## Instructions

### Search by Keyword
```bash
python scripts/searcher.py search "authentication"
```

Returns all code related to authentication across all categories and components.

### Browse Category
```bash
python scripts/searcher.py browse-category "Authentication"
```

Lists all components within the Authentication category.

### Browse Component
```bash
python scripts/searcher.py browse-component "Authentication" "JWT Validation"
```

Shows all implementations of JWT Validation component.

## Available Scripts

- `scripts/searcher.py` - Main functional search engine

## Used By

- **architect**: Finding existing code for architectural decisions
- **code_developer**: Locating similar patterns and implementations
- **assistant**: Gathering code for documentation and demos

## Functional Categories

- **Authentication**: JWT, OAuth, tokens, login, credentials
- **Database**: SQLAlchemy, ORM, queries, migrations
- **API**: Endpoints, routes, requests, responses, REST
- **Payment**: Stripe, transactions, billing, invoices
- **Notifications**: Email, alerts, messages, Slack, webhooks
- **Logging**: Observability, tracing, debug logs, Langfuse
- **Configuration**: Settings, environment variables, .env
- **Testing**: Pytest, mocks, fixtures, test utilities
- **Utilities**: Helpers, common code, base classes
- **CLI**: Commands, argument parsing, CLI tools
- **Autonomous**: Daemons, agents, workflows, orchestration

## Example Output

```json
{
  "query": "authentication",
  "results_count": 15,
  "categories": {
    "Authentication": {
      "component_count": 3,
      "implementation_count": 8,
      "components": {
        "JWT Validation": {
          "implementations": [
            {
              "file": "coffee_maker/auth/jwt.py",
              "line_start": 45,
              "line_end": 89,
              "name": "validate_jwt",
              "type": "function"
            }
          ]
        }
      }
    }
  }
}
```
