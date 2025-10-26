---
command: architect.validate_spec_completeness
agent: architect
action: validate_spec_completeness
data_domain: arch_specs
write_tables: []
read_tables: [arch_specs, arch_spec_sections]
required_skills: [technical_specification_handling]
---

# Command: architect.validate_spec_completeness

## Purpose
Check if a specification has all required sections and is ready for implementation.

## Input Parameters
- **spec_id**: string (required) - Specification to validate (e.g., "SPEC-131")
- **strict_mode**: boolean (optional, default: false) - Fail on warnings instead of warnings only

## Database Operations

### READ Operations
```sql
-- Get specification
SELECT * FROM arch_specs WHERE id = :spec_id;

-- Get all sections for this spec
SELECT section_name, content, section_order
FROM arch_spec_sections
WHERE spec_id = :spec_id
ORDER BY section_order;
```

## Required Skills

### technical_specification_handling
- Validates specification structure and completeness
- Assesses content quality
- Identifies missing or weak sections

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check read access to arch_specs domain

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   ```

3. **Fetch Specification**
   - Query arch_specs for spec_id
   - If not found, return SpecNotFoundError

4. **Fetch All Sections**
   - Query arch_spec_sections for this spec
   - Organize by section_order

5. **Check Required Sections**
   - problem_statement (required)
   - proposed_solution (required)
   - technical_design (required)
   - implementation_plan (required)
   - testing_strategy (required)
   - definition_of_done (required)

6. **Validate Section Content**
   - Each section must have content
   - Content must meet minimum length (>100 chars)
   - Content must be well-formed markdown

7. **Assess Quality**
   - Check for code examples in technical_design
   - Check for test cases in testing_strategy
   - Check for measurable DoD criteria

8. **Identify Warnings**
   - Test strategy could be more detailed
   - Missing edge cases in implementation plan
   - Unclear error handling in technical design
   - Missing performance requirements

9. **Calculate Validation Score**
   - 100: All required sections, all quality checks pass
   - 90-99: All required sections, minor quality issues
   - 75-89: All sections present, moderate quality issues
   - <75: Missing sections or major quality issues

10. **Return Validation Results**
    - List all sections found
    - List missing sections
    - List warnings identified
    - Return validation score

## Error Handling

### SpecNotFoundError
- **Cause**: Specification doesn't exist
- **Response**: Return error with spec_id
- **Recovery**: Verify spec_id is correct

### MissingRequiredSectionError
- **Cause**: One or more required sections missing
- **Response**: Return error with list of missing sections
- **Recovery**: Create missing sections via architect.update_spec

### InvalidSectionContentError
- **Cause**: Section content is invalid or too short
- **Response**: Return warning for specific section
- **Recovery**: Improve section content

### StrictModeFailure
- **Cause**: Warnings present and strict_mode=true
- **Response**: Return failure status
- **Recovery**: Fix warnings and revalidate

## Success Criteria
- [ ] All required sections present
- [ ] Content quality assessed
- [ ] Warnings identified
- [ ] Validation score calculated (0-100)
- [ ] Detailed report provided

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Validate spec completeness
result = db.execute_command('architect.validate_spec_completeness', {
    'spec_id': 'SPEC-131',
    'strict_mode': False
})

# Returns
{
    'success': True,
    'spec_id': 'SPEC-131',
    'is_complete': True,
    'missing_sections': [],
    'warnings': [
        'Test strategy could be more detailed',
        'Missing performance requirements'
    ],
    'validation_score': 85,
    'sections_found': [
        'problem_statement',
        'proposed_solution',
        'technical_design',
        'implementation_plan',
        'testing_strategy',
        'definition_of_done'
    ]
}
```

## Output Format

```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "is_complete": true,
  "missing_sections": [],
  "warnings": [
    "Test strategy could be more detailed"
  ],
  "validation_score": 95,
  "sections_found": 6,
  "total_required_sections": 6
}
```

## Quality Assessment Criteria

### Excellent (90-100)
- All sections present and detailed
- Code examples included
- Test cases documented
- Clear error handling
- Performance considerations addressed

### Good (75-89)
- All sections present
- Most sections detailed
- Some examples included
- Basic error handling described
- Testing strategy adequate

### Fair (60-74)
- All sections present but sparse
- Limited examples
- Basic testing described
- Minimal quality assurance details

### Poor (<60)
- Missing sections
- Insufficient detail
- Unclear requirements
- Incomplete testing strategy

## Related Commands
- `architect.create_spec` - Create new specification
- `architect.update_spec` - Add missing sections or improve content
- `architect.approve_spec` - Move spec from draft to approved
