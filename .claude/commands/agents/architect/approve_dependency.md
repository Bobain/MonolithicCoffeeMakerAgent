---
command: architect.approve_dependency
agent: architect
action: approve_dependency
data_domain: shared_governance
write_tables: [system_audit]
read_tables: []
required_skills: [dependency_conflict_resolver]
---

# Command: architect.approve_dependency

## Purpose
Review and approve a dependency request from code_developer following SPEC-070 three-tier approval system.

## Input Parameters
- **package_name**: string (required) - Package to evaluate (e.g., "redis")
- **version**: string (optional) - Specific version (e.g., "5.0.0")
- **reason**: string (required) - Why this dependency is needed
- **tier**: string (optional) - Force tier level (1|2|3), auto-detected if omitted
- **approved**: boolean (required) - Approval decision
- **rejection_reason**: string (optional) - If rejected, why
- **security_check**: boolean (optional, default: true) - Run security audit
- **create_adr**: boolean (optional, default: true) - Create ADR documenting decision

## Database Operations

### READ Operations
```sql
-- Check for existing dependency entries
SELECT * FROM system_audit
WHERE table_name = 'dependencies'
  AND item_id = :package_name;

-- Check current pyproject.toml dependencies
-- (via shell command)
```

### WRITE Operations
```sql
-- Create audit trail
INSERT INTO system_audit (
    table_name, item_id, action, field_changed,
    old_value, new_value, changed_by, changed_at, notes
) VALUES (
    'dependencies', :package_name, 'approve', 'status',
    'pending', :status, 'architect', :timestamp, :notes
);
```

## External Tool Usage

```bash
# Check package for security issues
poetry add {package_name}=={version} --dry-run

# Run security checks
poetry check
poetry show --outdated
safety check

# Update lock file (if approved)
poetry add {package_name}=={version}
poetry lock

# Verify compatibility
poetry install --dry-run
```

## Required Skills

### dependency_conflict_resolver
- Analyzes dependency conflicts
- Checks for transitive dependency issues
- Validates security and licensing

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to governance domain

2. **Load Required Skills**
   ```python
   conflict_skill = load_skill(SkillNames.DEPENDENCY_CONFLICT_RESOLVER)
   ```

3. **Validate Inputs**
   - package_name must be non-empty string
   - approved must be boolean
   - reason must be non-empty string

4. **Detect Tier** (if tier not specified)
   - Read SPEC-070 tier matrix
   - Match package to tier:
     - **Tier 1** (auto-approve): Common, pre-approved packages
       - pytest, black, requests, pydantic, sqlalchemy, etc.
     - **Tier 2** (review): Moderate risk, needs architect review
       - redis, celery, aiohttp, websockets, etc.
     - **Tier 3** (user approval): High-risk, experimental, niche packages
     - Check if package_name in Tier 1 list

5. **Run Conflict Analysis** (if approved=true)
   ```python
   conflict_result = conflict_skill.execute({
       'package': package_name,
       'version': version,
       'current_dependencies': read_pyproject_toml()
   })
   ```

6. **Run Security Check** (if security_check=true and approved=true)
   ```bash
   poetry add {package}=={version} --dry-run
   poetry check
   ```

7. **Handle Tier 1 (Auto-Approve)**
   - No additional review needed
   - Add to pyproject.toml immediately
   - Create audit trail
   - Notify code_developer

8. **Handle Tier 2 (Architect Review)**
   - Architect reviews:
     - Security profile
     - Maintenance status
     - Licensing
     - Conflict analysis results
   - If approved:
     - Create ADR documenting decision
     - Add to pyproject.toml
     - Create audit trail
   - If rejected:
     - Notify code_developer with reason
     - Suggest alternatives

9. **Handle Tier 3 (User Approval Required)**
   - Architect reviews
   - Sends notification to user_listener
   - Waits for user approval (via notification response)
   - If user approves:
     - Create ADR
     - Add to pyproject.toml
   - If user rejects:
     - Notify code_developer

10. **Create ADR** (if create_adr=true and approved=true)
    ```python
    adr_num = get_next_adr_number()
    generate_adr(db, {
        'adr_number': adr_num,
        'title': f'Use {package_name} for {reason}',
        'context': f'Need {package_name} {reason}',
        'decision': f'Approve {package_name} (Tier {tier}) and add to pyproject.toml',
        'consequences': {
            'positive': [
                'Solves immediate need',
                'Well-maintained package' if tier <= 2 else 'Experimental but solves need'
            ],
            'negative': [
                'Additional dependency',
                'Maintenance overhead',
                'Potential security surface'
            ]
        },
        'alternatives': [],
        'status': 'Accepted'
    })
    ```

11. **Update pyproject.toml** (if approved=true and tier <= 2)
    ```bash
    poetry add {package}=={version}
    poetry lock
    ```

12. **Create Audit Trail**
    - Record approval in system_audit
    - Include tier, reason, security check results
    - Reference ADR if created

13. **Notify code_developer**
    ```python
    if approved:
        notify('code_developer', {
            'type': 'dependency_approved',
            'package': package_name,
            'version': version,
            'tier': tier,
            'message': f'{package_name} approved and added to dependencies'
        })
    else:
        notify('code_developer', {
            'type': 'dependency_rejected',
            'package': package_name,
            'reason': rejection_reason,
            'message': f'{package_name} rejected'
        })
    ```

## Error Handling

### DependencyConflictError
- **Cause**: New dependency conflicts with existing ones
- **Response**: Return error with conflict details
- **Recovery**: Resolve conflicts manually or choose different version

### SecurityIssueError
- **Cause**: Package has known security vulnerabilities
- **Response**: Return error with vulnerability details
- **Recovery**: Use different version or package

### InvalidVersionError
- **Cause**: Specified version doesn't exist
- **Response**: Return error with available versions
- **Recovery**: Specify valid version

### LicensingConflictError
- **Cause**: Package license incompatible with project
- **Response**: Return error with license details
- **Recovery**: Choose compatible package

### TierDetectionError
- **Cause**: Cannot determine tier for package
- **Response**: Default to Tier 3 (conservative)
- **Recovery**: Explicitly specify tier parameter

## Success Criteria
- [ ] Dependency evaluated (security, licensing, conflicts)
- [ ] User approval requested if tier 2/3
- [ ] Package added via poetry if approved
- [ ] ADR created documenting decision
- [ ] Audit trail created
- [ ] code_developer notified

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Request dependency (Tier 1 - auto-approve)
result = db.execute_command('architect.approve_dependency', {
    'package_name': 'pytest',
    'version': '8.0.0',
    'reason': 'Testing framework for unit tests',
    'approved': True,
    'security_check': True
})

# Request dependency (Tier 2 - architect review)
result = db.execute_command('architect.approve_dependency', {
    'package_name': 'redis',
    'version': '5.0.0',
    'reason': 'Caching layer for performance',
    'approved': True,
    'security_check': True,
    'create_adr': True
})

# Reject dependency
result = db.execute_command('architect.approve_dependency', {
    'package_name': 'some-experimental-lib',
    'reason': 'Experimental feature',
    'approved': False,
    'rejection_reason': 'Tier 3 experimental package, too risky for production'
})

# Returns
{
    'success': True,
    'package_name': 'redis',
    'version': '5.0.0',
    'tier': 2,
    'approved': True,
    'security_check_passed': True,
    'adr_created': 'ADR-016-use-redis-for-caching.md',
    'added_to_pyproject': True
}
```

## Output Format

```json
{
  "success": true,
  "package_name": "redis",
  "version": "5.0.0",
  "tier": 2,
  "approved": true,
  "security_check_passed": true,
  "conflict_analysis_passed": true,
  "adr_created": "ADR-016-use-redis.md",
  "added_to_pyproject": true,
  "approved_at": "2025-10-26T12:34:56Z"
}
```

## Three-Tier Dependency System (SPEC-070)

### Tier 1: Auto-Approve
- Common, pre-approved packages
- Low risk, well-maintained
- Auto-added without architect review
- Examples: pytest, black, requests, pydantic, sqlalchemy

### Tier 2: Architect Review
- Moderate risk, needs review
- Architect checks security, licensing, conflicts
- If approved, added automatically
- Examples: redis, celery, aiohttp, websockets

### Tier 3: User Approval
- High-risk, experimental, niche
- Requires both architect and user approval
- User must explicitly approve in UI
- Examples: Experimental libs, private packages, beta versions

## Related Commands
- `architect.generate_adr` - Create ADR documenting decision
- `architect.update_cfrs` - Document dependency policies
- `architect.update_guidelines` - Create dependency guidelines
