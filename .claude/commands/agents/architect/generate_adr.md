---
command: architect.generate_adr
agent: architect
action: generate_adr
data_domain: shared_governance
write_tables: [system_audit]
read_tables: []
required_skills: []
---

# Command: architect.generate_adr

## Purpose
Generate an Architectural Decision Record (ADR) document following RFC2119 decision format.

## Input Parameters
- **adr_number**: integer (required) - ADR number (sequential, e.g., 15)
- **title**: string (required) - ADR title (e.g., "Use Command Architecture for Agents")
- **context**: string (required) - Problem context and constraints
- **decision**: string (required) - Decision made and why
- **consequences**: object (required)
  - `positive`: array of strings - Benefits of decision
  - `negative`: array of strings - Drawbacks of decision
- **alternatives**: array (optional) - Alternative options considered
  - `option`: string - Alternative name
  - `reason_rejected`: string - Why rejected
- **status**: string (optional, default: "Proposed") - "Proposed", "Accepted", "Deprecated", "Superseded"

## File Operations

### WRITE Operations
```
File: docs/architecture/decisions/ADR-{num:03d}-{slug}.md

Content Structure:
- YAML frontmatter with metadata
- ADR number and title
- Status section
- Context section
- Decision section
- Consequences subsections (positive/negative)
- Alternatives section
- Related ADRs
```

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to decisions directory

2. **Validate Inputs**
   - ADR number must be integer > 0
   - Title must be non-empty string
   - Context must be non-empty string
   - Decision must be non-empty string
   - Status must be one of: Proposed, Accepted, Deprecated, Superseded

3. **Generate ADR ID and Slug**
   - adr_id = f"ADR-{adr_number:03d}"
   - slug = convert title to lowercase slug (replace spaces/special chars with hyphens)
   - filename = f"ADR-{adr_number:03d}-{slug}.md"

4. **Check for Existing ADR**
   - Check if file already exists
   - If exists, return DuplicateADRError

5. **Generate ADR Content**
   - Create markdown with proper structure
   - Populate all sections from input
   - Format alternatives as table
   - Format consequences as bullet lists

6. **Create Directory if Needed**
   - Ensure docs/architecture/decisions/ exists
   - Create if missing

7. **Write ADR File**
   - Write to docs/architecture/decisions/{filename}
   - Ensure proper formatting
   - Line length <100 chars (soft limit)
   - Proper markdown syntax

8. **Create Audit Trail**
   - Record ADR creation in system_audit
   - Item: adr_id
   - Action: create
   - File path in new_value

9. **Return ADR Details**
   - Confirm creation
   - Return file path
   - Return ADR ID

## Error Handling

### InvalidADRNumberError
- **Cause**: ADR number invalid or already used
- **Response**: Return error with valid number range
- **Recovery**: Use next available ADR number

### InvalidStatusError
- **Cause**: Status not in allowed list
- **Response**: Return error with valid statuses
- **Recovery**: Use "Proposed", "Accepted", "Deprecated", or "Superseded"

### ValidationError
- **Cause**: Missing or invalid required fields
- **Response**: Return error with missing fields
- **Recovery**: Provide all required fields

### FileWriteError
- **Cause**: Cannot write to file system
- **Response**: Return error with file path
- **Recovery**: Check file permissions

## Success Criteria
- [ ] ADR file created in correct location
- [ ] Status set appropriately
- [ ] Alternatives documented
- [ ] Audit log created
- [ ] Valid markdown syntax

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Generate ADR
result = db.execute_command('architect.generate_adr', {
    'adr_number': 15,
    'title': 'Use Command Architecture for Agents',
    'context': 'Agents need flexible, extensible way to execute actions...',
    'decision': 'Implement command pattern with yaml frontmatter...',
    'consequences': {
        'positive': [
            'Flexible and extensible',
            'Clear separation of concerns',
            'Easy to add new commands'
        ],
        'negative': [
            'More files to maintain',
            'Complexity in loader'
        ]
    },
    'alternatives': [
        {
            'option': 'Monolithic Agent Class',
            'reason_rejected': 'Not extensible, hard to test'
        },
        {
            'option': 'REST API Endpoints',
            'reason_rejected': 'Not suitable for local commands'
        }
    ],
    'status': 'Accepted'
})

# Returns
{
    'success': True,
    'adr_id': 'ADR-015',
    'file_path': 'docs/architecture/decisions/ADR-015-use-command-architecture-for-agents.md',
    'status': 'Accepted'
}
```

## Output Format

```json
{
  "success": true,
  "adr_id": "ADR-015",
  "title": "Use Command Architecture for Agents",
  "file_path": "docs/architecture/decisions/ADR-015-use-command-architecture-for-agents.md",
  "status": "Accepted",
  "created_at": "2025-10-26T12:34:56Z"
}
```

## ADR Markdown Template

```markdown
---
status: Proposed
date: YYYY-MM-DD
author: architect
---

# ADR-015: Use Command Architecture for Agents

## Status

Proposed

## Context

[Problem context here]

## Decision

[Decision statement here]

## Consequences

### Positive
- Benefit 1
- Benefit 2
- Benefit 3

### Negative
- Drawback 1
- Drawback 2

## Alternatives Considered

### Option 1: [Name]
[Description]

**Reason Rejected**: [Why not chosen]

### Option 2: [Name]
[Description]

**Reason Rejected**: [Why not chosen]

## Related ADRs
- ADR-014: Previous decision this relates to
- ADR-016: Future decision this enables

## Implementation Notes
[Any additional notes about implementation]
```

## ADR Status Lifecycle

- **Proposed**: New ADR under consideration
- **Accepted**: ADR approved and implemented
- **Deprecated**: ADR superseded by new decision
- **Superseded**: ADR replaced by newer decision (reference new ADR)

## Related Commands
- `architect.update_guidelines` - Create implementation guidelines
- `architect.update_cfrs` - Document CFR changes
- `architect.approve_dependency` - Create ADR for major dependencies
