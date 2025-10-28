# docs

## Purpose
Generate comprehensive documentation: analyze code, create/update README files, generate API docs, maintain architecture documentation.

## Parameters
```yaml
target: str  # Required: "readme" | "api" | "architecture" | "guide"
scope: str = "."  # Path to document (file/directory)
format: str = "markdown"  # "markdown" | "html" | "pdf"
update_existing: bool = true  # Update existing docs
auto_commit: bool = false  # Commit documentation changes
```

## Workflow
1. Analyze target scope (files, modules, architecture)
2. Extract relevant information:
   - **readme**: Project overview, setup, usage
   - **api**: Function signatures, parameters, examples
   - **architecture**: System design, patterns, decisions
   - **guide**: Step-by-step tutorials
3. Generate documentation in specified format
4. Update or create documentation files
5. Commit if auto_commit=True
6. Return DocsResult

## Documentation Patterns
```markdown
# README Template
## Overview
## Installation
## Quick Start
## Configuration
## Architecture
## Contributing

# API Doc Template
## Module: {name}
### Function: {name}
**Parameters**: ...
**Returns**: ...
**Example**: ...

# Architecture Doc Template
## System Overview
## Key Components
## Data Flow
## Patterns Used
## ADRs
```

## Database Operations
```sql
-- Track documentation generation
INSERT INTO documentation_tracker (
    doc_id, doc_type, target_path, generated_at,
    lines_generated, status
) VALUES (?, ?, ?, datetime('now'), ?, 'completed')

-- Link to priority/spec
UPDATE documentation_tracker
SET related_priority_id = ?, related_spec_id = ?
WHERE doc_id = ?
```

## Result Object
```python
@dataclass
class DocsResult:
    doc_type: str
    files_created: List[str]
    files_updated: List[str]
    lines_generated: int
    commit_created: bool
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| ScopeNotFound | Invalid path | Check target exists |
| ParseError | Can't analyze code | Review code syntax |
| FileWriteError | Can't save docs | Check permissions |
| CommitFailed | Git error | Review changes manually |

## Example
```python
result = docs(target="readme", scope="coffee_maker/commands/", update_existing=True)
# DocsResult(
#   doc_type="readme",
#   files_created=[],
#   files_updated=["coffee_maker/commands/README.md"],
#   lines_generated=142,
#   commit_created=False,
#   status="success"
# )
```

## Related Commands
- demo() - Create visual demos
- delegate() - Route documentation requests

---
Estimated: 60 lines | Context: ~4% | Examples: docs_examples.md
