# Integration Tests

This directory contains integration tests that interact with real external services like GitHub API.

## GitHub Integration Tests

The `test_github_integration.py` file contains tests to verify:

1. **GitHub Authentication** - Tests that current credentials are valid
2. **Repository Access** - Tests ability to read repository information
3. **Pull Request Access** - Tests ability to read PR data
4. **PR Suggestion Posting** - Tests ability to post code suggestions (disabled by default)
5. **File Reading** - Tests ability to read file content from PRs
6. **Commit Access** - Tests ability to read commit information

## Running Integration Tests

### Prerequisites

You need a valid GitHub token with the following permissions:
- `repo` - Full control of private repositories
- Ability to read pull requests
- Ability to post review comments

### Setup

1. Ensure your `.env` file contains a valid `GITHUB_TOKEN`:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

2. The tests will automatically load environment variables from `.env`

### Running the Tests

**Run all integration tests:**
```bash
python -m pytest tests/integration_tests/test_github_integration.py -v -m integration
```

**Run specific test:**
```bash
python -m pytest tests/integration_tests/test_github_integration.py::TestGitHubIntegration::test_github_authentication -v
```

**Run all tests except integration tests (for CI):**
```bash
python -m pytest -m "not integration"
```

### Test Details

#### Safe Tests (Always Enabled)
- `test_github_authentication` - Verifies GitHub token is valid
- `test_github_repo_access` - Verifies repository can be accessed
- `test_github_pr_access` - Verifies pull requests can be read
- `test_can_read_pr_files` - Verifies files in PRs can be listed
- `test_can_read_file_content` - Verifies file content can be read
- `test_can_get_pr_commits` - Verifies commits can be accessed

#### Destructive Tests (Disabled by Default)
- `test_post_pr_suggestion` - **POSTS A REAL COMMENT** to a PR
  - This test is marked with `@pytest.mark.skip` by default
  - Remove the skip marker only when you want to test posting comments
  - It will post a test comment to the first open PR in the repository

### Expected Behavior

When GITHUB_TOKEN is not available:
- Tests will be **skipped** with message: "GITHUB_TOKEN environment variable not set"
- This is normal and expected in environments without credentials

When GITHUB_TOKEN is valid:
- Tests will execute and verify GitHub API operations
- Output includes confirmation messages for each successful operation

### Troubleshooting

**Tests are skipped:**
- Verify `.env` file exists in project root
- Verify `GITHUB_TOKEN` is set in `.env` file
- The tests use `python-dotenv` via the main application code

**Authentication fails:**
- Check token permissions in GitHub settings
- Ensure token has not expired
- Verify token has `repo` scope

**No open PRs found:**
- Some tests require at least one open PR in the repository
- These tests will be skipped if no open PRs exist
