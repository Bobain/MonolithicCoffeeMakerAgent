---
command: architect.update_cfrs
agent: architect
action: update_cfrs
data_domain: shared_governance
write_tables: [system_audit]
read_tables: []
required_skills: []
---

# Command: architect.update_cfrs

## Purpose
Create, update, or deprecate Critical Functional Requirements (CFRs) that define non-negotiable architectural standards.

## Input Parameters
- **cfr_number**: integer (required) - CFR number (e.g., 16)
- **action**: string (required) - "create", "update", "deprecate"
- **title**: string (required) - CFR title (e.g., "Singleton Agent Enforcement")
- **description**: string (required) - Detailed requirement description
- **rationale**: string (required) - Why this is critical to the system
- **enforcement**: string (required) - How this requirement is enforced (tools, tests, etc.)
- **impact_area**: string (optional) - Area affected (scalability|security|performance|maintainability)
- **related_specs**: array (optional) - Related specification numbers

## File Operations

### READ Operations
```
File: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md

Reads current CFRs to:
- Find next available CFR number
- Verify uniqueness
- Check for conflicts
```

### WRITE Operations
```
File: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md

Content Structure:
- YAML frontmatter with metadata
- Table of CFRs with status
- Detailed description for each CFR
- Enforcement methods
- Related specifications
```

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to roadmap directory

2. **Validate Inputs**
   - CFR number must be positive integer
   - Action must be "create", "update", or "deprecate"
   - Title must be non-empty string
   - Description must be non-empty string
   - Rationale must be non-empty string
   - Enforcement must be non-empty string

3. **Read Current CFR Document**
   - Load docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md
   - Parse existing CFRs
   - Find all current CFR numbers

4. **Validate CFR Number**
   - If create: verify number not already used
   - If update or deprecate: verify number exists
   - If create and number=auto: find next available number

5. **Process Based on Action**

   **CREATE**:
   - Create new CFR entry
   - Add to CFR table
   - Add detailed section
   - Set status to "Active"

   **UPDATE**:
   - Find existing CFR
   - Update description/rationale/enforcement
   - Keep status as is
   - Record update in version history

   **DEPRECATE**:
   - Find existing CFR
   - Set status to "Deprecated"
   - Add deprecation note
   - Reference superseding CFR if applicable

6. **Validate CFR Content**
   - Title must be clear and specific
   - Description must explain requirement clearly
   - Rationale must explain criticality
   - Enforcement must be specific (tools, tests, code review)

7. **Generate CFR Entry**
   - CFR ID = f"CFR-{cfr_number}"
   - Create markdown section
   - Include all fields
   - Format with proper markdown

8. **Update CFR Document**
   - Update CFR table
   - Add/update detailed section
   - Maintain alphabetical/numerical order
   - Update table of contents if needed

9. **Create Audit Trail**
   - Record CFR change in system_audit
   - Item: cfr_id
   - Action: create/update/deprecate
   - Document what changed

10. **Return CFR Details**
    - Confirm action
    - Return CFR ID
    - Return status

## Error Handling

### DuplicateCFRError
- **Cause**: CFR number already exists
- **Response**: Return error with existing CFR details
- **Recovery**: Use different number or update existing

### InvalidCFRNumberError
- **Cause**: CFR number invalid or negative
- **Response**: Return error with valid number range
- **Recovery**: Use valid positive integer

### CFRNotFoundError
- **Cause**: CFR doesn't exist (for update/deprecate)
- **Response**: Return error with CFR number
- **Recovery**: Verify CFR number is correct

### InvalidActionError
- **Cause**: Action not in allowed list
- **Response**: Return error with valid actions
- **Recovery**: Use "create", "update", or "deprecate"

### ValidationError
- **Cause**: Missing or invalid required fields
- **Response**: Return error with missing fields
- **Recovery**: Provide all required fields

## Success Criteria
- [ ] CFR document updated
- [ ] CFR number unique
- [ ] Enforcement method documented
- [ ] Audit log created
- [ ] Status set correctly

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Create new CFR
result = db.execute_command('architect.update_cfrs', {
    'cfr_number': 16,
    'action': 'create',
    'title': 'Centralized Database Storage',
    'description': """
ALL database files MUST be stored in data/ directory ONLY.
- No database files in root directory
- No database files in .claude/ directory
- No database files in other locations
- Applies to all .db, .sqlite, .sqlite3 files
    """,
    'rationale': """
Centralized database storage ensures:
- Organization and discoverability
- Simplified backup and deployment
- Security isolation from code
- Easy cleanup and maintenance
    """,
    'enforcement': """
- Linter check in pre-commit hooks
- pytest fixtures validate database location
- code_reviewer checks new database files
- Database schema enforces path constraints
    """,
    'impact_area': 'maintainability',
    'related_specs': [100, 101]
})

# Update existing CFR
result = db.execute_command('architect.update_cfrs', {
    'cfr_number': 15,
    'action': 'update',
    'title': 'Database Tracing',
    'description': 'Updated enforcement methods...',
    'rationale': 'Updated rationale...',
    'enforcement': 'Updated enforcement...'
})

# Deprecate CFR
result = db.execute_command('architect.update_cfrs', {
    'cfr_number': 10,
    'action': 'deprecate',
    'title': 'Old Requirement'
})

# Returns
{
    'success': True,
    'cfr_id': 'CFR-016',
    'action': 'create',
    'file_updated': True
}
```

## Output Format

```json
{
  "success": true,
  "cfr_id": "CFR-016",
  "title": "Centralized Database Storage",
  "action": "create",
  "status": "Active",
  "file_updated": true,
  "updated_at": "2025-10-26T12:34:56Z"
}
```

## CFR Status Values

- **Active**: Currently enforced requirement
- **Deprecated**: No longer enforced, superseded by new CFR
- **Proposed**: Under review, not yet enforced
- **Experimental**: Optional/experimental requirement

## CFR Document Structure

```markdown
# Critical Functional Requirements (CFRs)

## CFR Table

| Number | Title | Impact Area | Status |
|--------|-------|-------------|--------|
| CFR-000 | Singleton Agent Enforcement | Maintainability | Active |
| CFR-007 | Context Budget | Performance | Active |
| CFR-015 | Centralized Database Storage | Maintainability | Active |

## Detailed CFRs

### CFR-000: Singleton Agent Enforcement

**Status**: Active
**Impact Area**: Maintainability
**Related Specs**: SPEC-001

**Requirement**:
Each agent type MUST have only ONE running instance at a time.

**Rationale**:
[Why this is critical]

**Enforcement**:
- AgentRegistry class in coffee_maker/autonomous/agent_registry.py
- Tests in tests/unit/test_agent_registry.py
- Code review checks for AgentRegistry.register() usage
- Pre-commit hooks validate singleton pattern

**Related Specifications**:
- SPEC-001: Agent Architecture

---

[Additional CFRs...]
```

## Impact Areas

- **Scalability**: Affects system's ability to handle growth
- **Security**: Affects system security and data protection
- **Performance**: Affects speed, memory, or resource usage
- **Maintainability**: Affects code quality and long-term maintenance
- **Reliability**: Affects system uptime and reliability

## Related Commands
- `architect.generate_adr` - Create architectural decision record
- `architect.update_guidelines` - Create implementation guidelines
- `architect.approve_dependency` - Document dependency decisions
