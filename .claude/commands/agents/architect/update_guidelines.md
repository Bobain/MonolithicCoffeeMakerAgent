---
command: architect.update_guidelines
agent: architect
action: update_guidelines
data_domain: shared_governance
write_tables: [system_audit]
read_tables: []
required_skills: []
---

# Command: architect.update_guidelines

## Purpose
Create or update architecture guidelines for consistent implementation patterns across the codebase.

## Input Parameters
- **guideline_number**: integer (required) - Guideline number (sequential, e.g., 7)
- **title**: string (required) - Guideline title
- **category**: string (required) - "Design Pattern", "Best Practice", "Anti-Pattern", "Code Standard"
- **when_to_use**: string (required) - When to apply this guideline
- **how_to_implement**: string (required) - Implementation details and steps
- **anti_patterns**: string (required) - What NOT to do (common mistakes)
- **examples**: array (required) - Code examples
  - `good`: string - Example of correct implementation
  - `bad`: string - Example of incorrect implementation
  - `description`: string - Explanation of example
- **related_guidelines**: array (optional) - Related guideline numbers
- **related_specs**: array (optional) - Related specification numbers

## File Operations

### WRITE Operations
```
File: docs/architecture/guidelines/GUIDELINE-{num:03d}-{slug}.md

Content Structure:
- YAML frontmatter with metadata
- Guideline number and title
- Category section
- When to Use section
- How to Implement section (with steps)
- Anti-Patterns section
- Examples section (good/bad)
- Related Documents section
```

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to guidelines directory

2. **Validate Inputs**
   - Guideline number must be positive integer
   - Title must be non-empty string
   - Category must be one of valid categories
   - All required sections must be non-empty strings

3. **Validate Category**
   - "Design Pattern" - Pattern for solving recurring problems
   - "Best Practice" - Recommended approach
   - "Anti-Pattern" - Pattern to avoid
   - "Code Standard" - Mandatory coding conventions

4. **Generate Guideline ID and Slug**
   - guideline_id = f"GUIDELINE-{guideline_number:03d}"
   - slug = convert title to slug format
   - filename = f"GUIDELINE-{guideline_number:03d}-{slug}.md"

5. **Check for Existing Guideline**
   - Check if file already exists
   - If exists, return DuplicateGuidelineError (or prompt for update)

6. **Validate Examples**
   - Each example must have: good, bad, description
   - Good example should demonstrate correct usage
   - Bad example should demonstrate common mistake
   - Description should explain the difference

7. **Generate Guideline Content**
   - Create markdown document
   - Populate all sections from input
   - Include code examples with syntax highlighting
   - Format related items as links

8. **Create Directory if Needed**
   - Ensure docs/architecture/guidelines/ exists
   - Create if missing

9. **Write Guideline File**
   - Write to docs/architecture/guidelines/{filename}
   - Ensure proper markdown formatting
   - Line length <100 chars (soft limit)

10. **Create Audit Trail**
    - Record guideline creation in system_audit
    - Item: guideline_id
    - Action: create
    - File path in new_value

11. **Return Guideline Details**
    - Confirm creation
    - Return file path
    - Return guideline ID

## Error Handling

### InvalidGuidelineNumberError
- **Cause**: Guideline number invalid or already used
- **Response**: Return error with valid number range
- **Recovery**: Use next available guideline number

### InvalidCategoryError
- **Cause**: Category not in allowed list
- **Response**: Return error with valid categories
- **Recovery**: Use valid category

### InvalidExamplesError
- **Cause**: Examples missing required fields
- **Response**: Return error specifying what's missing
- **Recovery**: Provide good, bad, and description for each example

### ValidationError
- **Cause**: Missing or invalid required fields
- **Response**: Return error with missing fields
- **Recovery**: Provide all required fields

## Success Criteria
- [ ] Guideline file created in correct location
- [ ] Category set correctly
- [ ] Examples provided for good/bad
- [ ] Anti-patterns documented
- [ ] Audit log created

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Create guideline
result = db.execute_command('architect.update_guidelines', {
    'guideline_number': 7,
    'title': 'Command Pattern Implementation',
    'category': 'Design Pattern',
    'when_to_use': 'When creating reusable commands for agents with consistent interface',
    'how_to_implement': """
1. Create markdown file with YAML frontmatter
2. Define command, agent, and action in frontmatter
3. Document input parameters and output format
4. Include database operations (read/write)
5. List required skills
6. Provide execution steps
7. Include error handling
8. Add example usage
    """,
    'anti_patterns': 'Do not hardcode command logic. Do not use global state.',
    'examples': [
        {
            'description': 'Correct command with proper structure',
            'good': '''---
command: agent.action
agent: agent_name
action: action_name
---

# Command: agent.action

## Purpose
[Purpose]
            ''',
            'bad': '''# Some Agent Action

def do_action():
    # Hardcoded logic
    pass
            '''
        }
    ],
    'related_guidelines': [6],
    'related_specs': [100, 101]
})

# Returns
{
    'success': True,
    'guideline_id': 'GUIDELINE-007',
    'file_path': 'docs/architecture/guidelines/GUIDELINE-007-command-pattern-implementation.md',
    'category': 'Design Pattern'
}
```

## Output Format

```json
{
  "success": true,
  "guideline_id": "GUIDELINE-007",
  "title": "Command Pattern Implementation",
  "category": "Design Pattern",
  "file_path": "docs/architecture/guidelines/GUIDELINE-007-command-pattern-implementation.md",
  "created_at": "2025-10-26T12:34:56Z"
}
```

## Guideline Markdown Template

```markdown
---
category: Design Pattern
related_guidelines: []
related_specs: []
status: Active
---

# GUIDELINE-007: Command Pattern Implementation

## Category

Design Pattern

## When to Use

[When to apply this guideline]

## How to Implement

### Step 1: [First step]
[Details]

### Step 2: [Second step]
[Details]

### Step 3: [Third step]
[Details]

## Anti-Patterns

### Don't Do This
[Example of what not to do]

**Why?** [Explanation]

### Don't Do That Either
[Another bad example]

**Why?** [Explanation]

## Examples

### Good Example
\`\`\`python
[Correct implementation code]
\`\`\`

**Explanation**: [Why this is correct]

### Bad Example
\`\`\`python
[Incorrect implementation code]
\`\`\`

**Problem**: [What's wrong and how to fix it]

## Related Guidelines
- GUIDELINE-006: [Related guideline]
- GUIDELINE-008: [Related guideline]

## Related Specifications
- SPEC-100: [Related spec]
- SPEC-101: [Related spec]

## FAQ

**Q: When should I use X instead of Y?**

A: Use X when [condition]. Use Y when [condition].

**Q: What if I have special case Z?**

A: In special case Z, you can [approach].
```

## Guideline Categories

### Design Pattern
- Recurring solution to a problem
- Reusable across multiple contexts
- Examples: Command pattern, Observer pattern, Singleton

### Best Practice
- Recommended approach for common tasks
- Improves code quality, maintainability, or performance
- Examples: Error handling, logging, testing

### Anti-Pattern
- Common mistake or bad practice to avoid
- Documents pitfalls and why to avoid them
- Examples: God objects, tight coupling, magic numbers

### Code Standard
- Mandatory coding conventions
- Enforced by linters, type checkers, formatters
- Examples: Black formatting, type hints, naming conventions

## Related Commands
- `architect.generate_adr` - Create architectural decision record
- `architect.update_cfrs` - Document critical functional requirements
