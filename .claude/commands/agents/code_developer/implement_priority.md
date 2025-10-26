---
command: code_developer.implement_priority
agent: code_developer
action: implement_priority
data_domain: dev_implementations
write_tables: [dev_implementations, dev_commits, dev_test_results]
read_tables: [arch_specs, arch_spec_sections, pm_roadmap, shared_config]
required_skills: [technical_specification_handling, test-failure-analysis, dod-verification]
---

# Command: code_developer.implement_priority

## Purpose
Implement a roadmap priority based on architect's technical specification.

## Input Parameters
- **priority_id**: string (required) - Roadmap priority ID to implement
- **spec_id**: string (required) - Technical specification ID
- **task_id**: string (optional) - Specific implementation task ID
- **auto_commit**: boolean (optional) - Auto-commit changes (default: true)
- **run_tests**: boolean (optional) - Run tests after implementation (default: true)

## Database Operations

### READ Operations
```sql
-- Read specification from architect's domain
SELECT * FROM arch_specs WHERE id = :spec_id;

-- Read spec sections for implementation details
SELECT * FROM arch_spec_sections
WHERE spec_id = :spec_id
ORDER BY section_order;

-- Check priority status
SELECT * FROM pm_roadmap WHERE id = :priority_id;

-- Check for existing implementation attempts
SELECT * FROM dev_implementations
WHERE priority_id = :priority_id
ORDER BY created_at DESC;
```

### WRITE Operations
```sql
-- Track implementation progress
INSERT INTO dev_implementations (
    id,
    priority_id,
    spec_id,
    file_path,
    content,
    status,
    created_at,
    created_by
) VALUES (
    :impl_id,
    :priority_id,
    :spec_id,
    :file_path,
    :content,
    'in_progress',
    :timestamp,
    'code_developer'
);

-- Record commits
INSERT INTO dev_commits (
    commit_hash,
    priority_id,
    message,
    files_changed,
    insertions,
    deletions,
    created_at
) VALUES (
    :commit_hash,
    :priority_id,
    :commit_message,
    :files_json,
    :insertions,
    :deletions,
    :timestamp
);

-- Store test results
INSERT INTO dev_test_results (
    priority_id,
    test_suite,
    passed,
    failed,
    skipped,
    coverage_percent,
    execution_time_ms,
    created_at
) VALUES (
    :priority_id,
    :test_suite,
    :passed,
    :failed,
    :skipped,
    :coverage,
    :exec_time,
    :timestamp
);
```

## Required Skills

### technical_specification_handling
- Read and parse technical specifications
- Extract implementation requirements
- Understand Definition of Done

### test-failure-analysis
- Debug failing tests
- Identify root causes
- Suggest fixes

### dod-verification
- Verify all acceptance criteria met
- Ensure test coverage adequate
- Validate implementation complete

## Execution Steps

1. **Validate Permissions**
   - Verify agent is code_developer
   - Check write access to dev_* tables

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   test_skill = load_skill(SkillNames.TEST_FAILURE_ANALYSIS)
   dod_skill = load_skill(SkillNames.DOD_VERIFICATION)
   ```

3. **Read Technical Specification**
   - Query arch_specs for specification
   - Read all spec sections
   - Extract implementation requirements

4. **Check Priority Status**
   - Verify priority is "Ready for Implementation"
   - Check no other developer is working on it

5. **Plan Implementation**
   - Identify files to create/modify
   - Determine implementation order
   - Set up development environment

6. **Implement Feature**
   - Create/modify code files
   - Follow coding standards
   - Add comprehensive comments
   - Implement error handling

7. **Write Tests**
   - Create unit tests
   - Add integration tests
   - Ensure >80% coverage

8. **Run Test Suite**
   ```python
   result = subprocess.run(['pytest', '--cov'], capture_output=True)
   test_results = parse_test_output(result.stdout)
   ```

9. **Debug Failures** (if any)
   - Use test-failure-analysis skill
   - Fix identified issues
   - Re-run tests until passing

10. **Verify DoD**
    - Use dod-verification skill
    - Check all criteria met
    - Validate implementation complete

11. **Commit Changes**
    ```bash
    git add -A
    git commit -m "feat(priority-{id}): {description}"
    ```

12. **Update Database**
    - Mark implementation as complete
    - Record commit hash
    - Store test results

13. **Request Code Review**
    ```python
    db.cross_domain_notify('code_reviewer', {
        'type': 'review_requested',
        'priority_id': priority_id,
        'commit_hash': commit_hash,
        'files_changed': files_list
    })
    ```

## Error Handling

### SpecNotFoundError
- **Cause**: Technical spec doesn't exist
- **Response**: Notify architect to create spec
- **Recovery**: Wait for spec creation

### TestFailureError
- **Cause**: Tests failing after implementation
- **Response**: Debug using test-failure-analysis
- **Recovery**: Fix issues and retry

### DoDNotMetError
- **Cause**: Acceptance criteria not satisfied
- **Response**: Continue implementation
- **Recovery**: Complete missing requirements

### ConflictError
- **Cause**: Another developer working on same priority
- **Response**: Check with orchestrator
- **Recovery**: Work on different priority

## Success Criteria
- [ ] All code implemented per spec
- [ ] Tests passing with >80% coverage
- [ ] DoD verified complete
- [ ] Changes committed to git
- [ ] Database updated with implementation
- [ ] Code review requested
- [ ] No linting errors
- [ ] Documentation updated

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType
import subprocess
import json

# Initialize database for code_developer
db = DomainDatabase(AgentType.CODE_DEVELOPER)

# Read specification
specs = db.read('arch_specs', {'id': 'SPEC-20251026-001'})
spec = specs[0] if specs else None

if not spec:
    raise ValueError("Specification not found")

# Read spec sections
sections = db.read('arch_spec_sections', {'spec_id': spec['id']})

# Implement based on spec
implementation_files = []
for section in sections:
    if section['section_name'] == 'implementation_plan':
        # Parse and implement based on plan
        files = implement_from_plan(section['content'])
        implementation_files.extend(files)

# Run tests
result = subprocess.run(
    ['pytest', '--cov', '--json-report'],
    capture_output=True,
    text=True
)

# Parse test results
test_data = json.loads(result.stdout)

# Store test results
db.write('dev_test_results', {
    'priority_id': 'PRIORITY-25',
    'test_suite': 'pytest',
    'passed': test_data['passed'],
    'failed': test_data['failed'],
    'skipped': test_data['skipped'],
    'coverage_percent': test_data['coverage'],
    'execution_time_ms': test_data['duration'] * 1000
})

# Commit if tests pass
if test_data['failed'] == 0:
    subprocess.run(['git', 'add', '-A'])
    subprocess.run([
        'git', 'commit', '-m',
        f'feat(priority-25): Implement authentication system'
    ])

# Request review
db.cross_domain_notify('code_reviewer', {
    'type': 'review_requested',
    'priority_id': 'PRIORITY-25',
    'spec_id': 'SPEC-20251026-001'
})
```

## Metrics & Monitoring
- **Implementation velocity**: Features per week
- **Test coverage trend**: Coverage over time
- **Bug introduction rate**: Bugs per implementation
- **First-time pass rate**: Implementations passing DoD first try
- **Average implementation time**: Time from start to completion

## Related Commands
- `code_developer.fix_bug` - Fix reported bugs
- `code_developer.run_tests` - Run test suite
- `code_developer.create_pr` - Create pull request
- `code_developer.update_implementation` - Update existing implementation
