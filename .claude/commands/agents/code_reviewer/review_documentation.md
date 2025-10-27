---
command: code_reviewer.review_documentation
agent: code_reviewer
action: review_documentation
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [git, grep]
estimated_duration_seconds: 20
---

# Command: code_reviewer.review_documentation

## Purpose

Check that docstrings, type hints documentation, and README are complete and accurate. This command ensures code is self-documenting and maintainable.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to check
review_id: string               # Required - link issues to review
check_docstrings: boolean       # Check function/class docstrings (default: true)
check_type_docs: boolean        # Check type hint documentation (default: true)
check_readme: boolean           # Check README updates (default: true)
check_comments: boolean         # Check inline comments (default: true)
docstring_format: string        # "google", "numpy", "sphinx" (default: "google")
severity_threshold: string      # Report: "all", "MEDIUM", "HIGH" (default: "MEDIUM")
```

## Database Operations

**Query: Insert documentation issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Documentation', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Check Docstrings

```bash
# Find functions without docstrings
grep -r "def [a-zA-Z_]" coffee_maker/ --include="*.py" -A 1 |
grep -B 1 "^[^\"]*def " | grep -v '"""' | grep -v "'''" | wc -l

# Verify format compliance (Google style)
pylint --load-plugins pylint.extensions.docparams coffee_maker/ \
  --disable=all --enable=missing-docstring --output-format=json

# Check class docstrings
grep -r "^class " coffee_maker/ --include="*.py" -A 2 |
grep -B 1 -E '""".*"""' | wc -l
```

### Check Comments

```bash
# Count comment ratio
comments=$(grep "^\s*#" coffee_maker/ -r --include="*.py" | wc -l)
code=$(grep -v "^\s*#" coffee_maker/ -r --include="*.py" | wc -l)
ratio=$((comments * 100 / (comments + code)))
echo "Comment ratio: $ratio%"
```

### Check README

```bash
# Verify README covers new features
git show --name-only {commit_sha} | grep -i readme

# Check if README.md exists
test -f README.md && echo "README exists" || echo "README missing"
```

## Documentation Standards

### Docstring Format (Google Style)

**Complete Function Docstring**:
```python
def authenticate(username: str, password: str) -> bool:
    """Authenticate a user with their credentials.

    Validates username and password against the user database.
    Supports both local and LDAP authentication.

    Args:
        username: The user's login name (case-insensitive)
        password: The user's password (plain text, will be hashed)

    Returns:
        bool: True if authentication successful, False otherwise

    Raises:
        ValueError: If username or password is empty
        DatabaseError: If database connection fails
        AuthenticationError: If too many failed attempts

    Examples:
        >>> authenticate("admin", "password123")
        True
        >>> authenticate("invalid", "wrong")
        False

    Note:
        Passwords are hashed using bcrypt before comparison.
        Rate limiting: 5 attempts per minute per user.

    See Also:
        validate_password: Lower-level password validation
        get_user: Retrieve user object by username
    """
    if not username or not password:
        raise ValueError("Username and password required")
    # ... implementation
```

**Complete Class Docstring**:
```python
class UserManager:
    """Manage user accounts and authentication.

    This class provides methods for user registration, authentication,
    profile management, and permission checking. It supports multiple
    authentication backends (local database, LDAP, OAuth).

    Attributes:
        db: Database connection pool
        ldap_client: Optional LDAP client for enterprise auth
        cache: User cache for performance

    Example:
        >>> manager = UserManager()
        >>> manager.authenticate("user", "pass")
        True
        >>> user = manager.get_user("user")
        >>> user.email
        'user@example.com'

    Note:
        Thread-safe operations. All methods are reentrant.
    """
```

### Docstring Quality Checks

**Required Elements** (HIGH severity if missing):
- [x] One-line summary (first line)
- [x] Blank line after summary (if description exists)
- [x] Detailed description (for complex functions)
- [x] Args section with parameter descriptions
- [x] Returns section with type and description
- [x] Raises section if function raises exceptions
- [x] Examples section for public APIs

**Recommended Elements** (MEDIUM if missing):
- [x] Usage examples
- [x] Cross-references (See Also)
- [x] Notes about performance or special behavior
- [x] Links to related functions

## Success Criteria

- ✅ Identifies all missing docstrings
- ✅ Checks docstring format compliance
- ✅ Verifies type hints are documented
- ✅ Checks comment-to-code ratio
- ✅ Verifies README updated
- ✅ Creates issues for gaps
- ✅ Completes in <20 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "documentation_check_duration_seconds": 14.2,
  "documentation_summary": {
    "total_functions": 45,
    "documented_functions": 42,
    "documentation_coverage": 93.3,
    "documentation_status": "GOOD"
  },
  "docstring_analysis": {
    "missing_docstrings": 3,
    "incomplete_docstrings": 2,
    "format_violations": 1
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Documentation",
      "file_path": "coffee_maker/auth.py",
      "line_number": 42,
      "function_name": "authenticate",
      "issue_type": "missing_docstring",
      "description": "Function 'authenticate' is missing docstring",
      "recommendation": "Add comprehensive docstring with Args, Returns, Raises sections",
      "template": "def authenticate(username: str, password: str) -> bool:\n    \"\"\"Authenticate a user.\n\n    Args:\n        username: User login name\n        password: User password\n\n    Returns:\n        bool: True if authenticated\n\n    Raises:\n        ValueError: If credentials invalid\n    \"\"\""
    },
    {
      "id": "ISS-2",
      "severity": "MEDIUM",
      "category": "Documentation",
      "file_path": "coffee_maker/database.py",
      "line_number": 88,
      "function_name": "query",
      "issue_type": "incomplete_docstring",
      "description": "Docstring missing Returns section",
      "recommendation": "Add Returns section describing return value",
      "current_docstring": "\"\"\"Execute database query.\n\n    Args:\n        sql: SQL query string\n    \"\"\""
    },
    {
      "id": "ISS-3",
      "severity": "MEDIUM",
      "category": "Documentation",
      "file_path": "README.md",
      "line_number": null,
      "issue_type": "readme_not_updated",
      "description": "README.md not updated for new features",
      "recommendation": "Update README with new authentication methods",
      "changed_files": ["coffee_maker/auth.py", "coffee_maker/ldap.py"],
      "public_api_changes": ["authenticate()", "get_ldap_client()"]
    }
  ],
  "type_documentation": {
    "fully_typed": 38,
    "partially_typed": 5,
    "untyped": 2,
    "typing_coverage": 93.3
  },
  "code_comments": {
    "total_comment_lines": 285,
    "total_code_lines": 1840,
    "comment_ratio": 15.5,
    "comment_quality": "GOOD",
    "missing_comments": [
      "Complex algorithm at line 156 needs explanation"
    ]
  },
  "public_api_coverage": {
    "public_functions": 8,
    "documented": 8,
    "coverage": 100.0,
    "status": "EXCELLENT"
  },
  "readme_analysis": {
    "exists": true,
    "updated": true,
    "covers_new_features": true,
    "has_examples": true,
    "has_installation": true,
    "has_usage": true
  },
  "summary": {
    "total_issues": 3,
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 2,
    "documentation_health": "GOOD"
  }
}
```

## Documentation Scoring

| Coverage | Rating | Status |
|----------|--------|--------|
| 95-100% | A | Excellent |
| 90-95% | B | Good |
| 80-90% | C | Acceptable |
| 70-80% | D | Needs Work |
| <70% | F | Critical |

## Error Handling

**Perfect Documentation**:
```json
{
  "status": "success",
  "documentation_summary": {
    "documentation_coverage": 100.0,
    "documentation_status": "EXCELLENT"
  },
  "issues": [],
  "message": "Perfect documentation - all functions documented"
}
```

**Missing Documentation**:
```json
{
  "status": "warning",
  "issues": [
    {
      "severity": "HIGH",
      "description": "5 functions missing docstrings"
    }
  ],
  "message": "Add docstrings for all public functions"
}
```

## Examples

### Example 1: Full documentation check

```bash
code_reviewer.review_documentation(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_docstrings=true,
  check_type_docs=true,
  check_readme=true,
  check_comments=true,
  docstring_format="google"
)
```

### Example 2: Docstring only

```bash
code_reviewer.review_documentation(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_docstrings=true,
  check_type_docs=false,
  check_readme=false,
  check_comments=false
)
```

## Implementation Notes

- Public APIs require complete docstrings
- Private functions can have minimal docstrings
- Google style is standard (not NumPy or Sphinx)
- Examples section highly recommended for public APIs
- Comment-to-code ratio: 15-20% is ideal
- README critical for user-facing features
- Cross-references help with navigation

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.check_style_compliance` - Code quality checks
- `code_reviewer.validate_type_hints` - Type hint validation

---

**Version**: 1.0
**Last Updated**: 2025-10-26
