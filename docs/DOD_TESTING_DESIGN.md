# Definition of Done (DOD) Testing Design

**Version**: 1.0
**Date**: 2025-10-10
**Status**: Design Phase

## 1. Overview

### 1.1 Purpose

Enable project_manager to automatically verify that User Stories are truly "Done" before marking them as shipped. This ensures quality and prevents incomplete features from being marked as complete.

### 1.2 Key Requirements (from User)

1. project_manager writes Definition of Done (DOD) for User Stories
2. project_manager tests DOD automatically before telling user story is shipped
3. If DOD tests fail, project_manager updates roadmap with technical details
4. code_developer's highest priority becomes fixing the failed implementation

### 1.3 Workflow

```
User Story Assigned → code_developer Implements → Marks Complete
    ↓
project_manager: Run DOD Tests
    ├─ PASS → ✅ Notify user: "Story shipped!"
    └─ FAIL → ⚠️ Update roadmap with failure details
            → Create PRIORITY X.Y: Fix DOD failure
            → Notify user: "Implementation incomplete, creating fix priority"
```

---

## 2. DOD Structure

### 2.1 Definition of Done Components

Each User Story should have:

```markdown
**Definition of Done**:
- [ ] **Functional**: Feature works as described in acceptance criteria
- [ ] **Tested**: Automated tests exist and pass
- [ ] **Documented**: User-facing docs updated (if needed)
- [ ] **Code Quality**: Passes linting, type checking
- [ ] **Performance**: Meets performance requirements
- [ ] **Reviewed**: Code follows project patterns

**DOD Tests** (Automated):
```yaml
tests:
  - name: "Feature works - basic functionality"
    type: "command"
    command: "poetry run python test_us_001.py"
    expected_exit_code: 0

  - name: "Lint check passes"
    type: "command"
    command: "poetry run black --check coffee_maker/"
    expected_exit_code: 0

  - name: "Type check passes"
    type: "command"
    command: "poetry run mypy coffee_maker/ --strict"
    expected_exit_code: 0

  - name: "Integration test"
    type: "python"
    code: |
      from coffee_maker.module import feature
      result = feature.test_method()
      assert result == expected_value

  - name: "File existence check"
    type: "file_exists"
    files:
      - "coffee_maker/new_module.py"
      - "tests/test_new_module.py"
      - "docs/NEW_FEATURE.md"
\```

**DOD Failure Actions**:
- Create PRIORITY {next_number}: Fix US-XXX DOD Failure
- Status: 🚨 Critical (blocks original story)
- Details: {failure_output}
```

### 2.2 Example User Story with DOD

```markdown
### 🎯 [US-003] Deploy code_developer on GCP

**As a**: System administrator
**I want**: code_developer running on GCP 24/7
**So that**: development continues autonomously without my laptop

**Business Value**: ⭐⭐⭐⭐⭐
**Estimated Effort**: 5 story points (5-7 days)
**Status**: 🚀 In Progress → Testing DOD

**Acceptance Criteria**:
- [ ] code_developer runs continuously on GCP Compute Engine
- [ ] Automatic restart on failure
- [ ] Logs accessible via Cloud Logging
- [ ] project_manager can communicate with GCP instance
- [ ] Cost stays under $50/month

**Definition of Done**:
- [ ] **Functional**: code_developer runs on GCP for 24 hours without stopping
- [ ] **Tested**: Can SSH to instance and verify daemon is running
- [ ] **Documented**: GCP_DEPLOYMENT.md created with setup instructions
- [ ] **Monitored**: Can view logs via Cloud Logging console
- [ ] **Cost-Optimized**: Cost projection < $50/month verified

**DOD Tests**:
\```yaml
tests:
  - name: "Verify GCP instance is running"
    type: "command"
    command: "gcloud compute instances describe coffee-maker-daemon --zone us-central1-a"
    expected_exit_code: 0
    expected_output_contains: "status: RUNNING"

  - name: "SSH to instance and check daemon"
    type: "command"
    command: "gcloud compute ssh coffee-maker-daemon --zone us-central1-a --command 'ps aux | grep run_code_developer.py'"
    expected_exit_code: 0
    expected_output_contains: "python run_code_developer.py"

  - name: "Check logs are accessible"
    type: "command"
    command: "gcloud logging read 'resource.type=gce_instance AND resource.labels.instance_id=coffee-maker-daemon' --limit 10"
    expected_exit_code: 0

  - name: "Verify documentation exists"
    type: "file_exists"
    files:
      - "docs/GCP_DEPLOYMENT.md"
      - "scripts/deploy_to_gcp.sh"
\```

**DOD Failure Actions**:
- If any test fails:
  * Create PRIORITY 4.1: Fix GCP Deployment DOD Failure
  * Status: 🚨 Critical - Blocks US-003
  * Assign to code_developer as TOP PRIORITY
  * Include full failure output in priority description
```

---

## 3. Implementation Plan

### 3.1 New Module: `dod_tester.py`

```python
# coffee_maker/cli/dod_tester.py

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


@dataclass
class DODTestResult:
    """Result of a single DOD test."""
    test_name: str
    passed: bool
    output: str
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class DODTestSuite:
    """Complete DOD test suite results."""
    user_story_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[DODTestResult]
    overall_passed: bool
    failure_summary: Optional[str] = None


class DODTester:
    """Execute Definition of Done tests for User Stories.

    This class runs automated tests to verify that a User Story meets
    all acceptance criteria before marking it as complete.
    """

    def __init__(self, roadmap_editor):
        """Initialize DOD Tester.

        Args:
            roadmap_editor: RoadmapEditor instance for reading User Stories
        """
        self.editor = roadmap_editor

    def run_dod_tests(self, user_story_id: str) -> DODTestSuite:
        """Run all DOD tests for a User Story.

        Args:
            user_story_id: User Story ID (e.g., "US-001")

        Returns:
            DODTestSuite with test results

        Example:
            >>> tester = DODTester(editor)
            >>> results = tester.run_dod_tests("US-001")
            >>> if results.overall_passed:
            ...     print("Story is DONE!")
        """
        logger.info(f"Running DOD tests for {user_story_id}")

        # Get User Story content
        content = self.editor.get_user_story_content(user_story_id)
        if not content:
            logger.error(f"{user_story_id} not found")
            return self._create_error_suite(user_story_id, "User Story not found")

        # Parse DOD tests from content
        dod_tests = self._parse_dod_tests(content)
        if not dod_tests:
            logger.warning(f"No DOD tests found for {user_story_id}")
            return self._create_empty_suite(user_story_id)

        # Run each test
        results = []
        for test_spec in dod_tests:
            result = self._run_single_test(test_spec)
            results.append(result)

        # Analyze results
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        overall_passed = failed == 0

        failure_summary = None
        if not overall_passed:
            failure_summary = self._generate_failure_summary(results)

        return DODTestSuite(
            user_story_id=user_story_id,
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            results=results,
            overall_passed=overall_passed,
            failure_summary=failure_summary
        )

    def _parse_dod_tests(self, content: str) -> List[Dict]:
        """Parse DOD test specifications from User Story content.

        Looks for YAML block under **DOD Tests** section.

        Args:
            content: User Story markdown content

        Returns:
            List of test specification dicts
        """
        import re

        # Find DOD Tests section
        pattern = r'\*\*DOD Tests\*\*:\s*```yaml\s*\n(.*?)\n```'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return []

        yaml_content = match.group(1)

        try:
            parsed = yaml.safe_load(yaml_content)
            return parsed.get('tests', [])
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse DOD tests YAML: {e}")
            return []

    def _run_single_test(self, test_spec: Dict) -> DODTestResult:
        """Run a single DOD test.

        Args:
            test_spec: Test specification dict

        Returns:
            DODTestResult
        """
        test_type = test_spec.get('type')
        test_name = test_spec.get('name', 'Unnamed test')

        logger.debug(f"Running test: {test_name} (type: {test_type})")

        try:
            if test_type == 'command':
                return self._run_command_test(test_spec)
            elif test_type == 'python':
                return self._run_python_test(test_spec)
            elif test_type == 'file_exists':
                return self._run_file_exists_test(test_spec)
            else:
                return DODTestResult(
                    test_name=test_name,
                    passed=False,
                    output="",
                    error_message=f"Unknown test type: {test_type}"
                )
        except Exception as e:
            logger.error(f"Test failed with exception: {e}", exc_info=True)
            return DODTestResult(
                test_name=test_name,
                passed=False,
                output="",
                error_message=str(e)
            )

    def _run_command_test(self, test_spec: Dict) -> DODTestResult:
        """Run a shell command test.

        Args:
            test_spec: Test specification with 'command', 'expected_exit_code', etc.

        Returns:
            DODTestResult
        """
        import time

        test_name = test_spec['name']
        command = test_spec['command']
        expected_exit_code = test_spec.get('expected_exit_code', 0)
        expected_output = test_spec.get('expected_output_contains')

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time

            # Check exit code
            if result.returncode != expected_exit_code:
                return DODTestResult(
                    test_name=test_name,
                    passed=False,
                    output=result.stdout + result.stderr,
                    error_message=f"Expected exit code {expected_exit_code}, got {result.returncode}",
                    duration_seconds=duration
                )

            # Check output contains expected string
            if expected_output:
                output = result.stdout + result.stderr
                if expected_output not in output:
                    return DODTestResult(
                        test_name=test_name,
                        passed=False,
                        output=output,
                        error_message=f"Expected output to contain: {expected_output}",
                        duration_seconds=duration
                    )

            return DODTestResult(
                test_name=test_name,
                passed=True,
                output=result.stdout,
                duration_seconds=duration
            )

        except subprocess.TimeoutExpired:
            return DODTestResult(
                test_name=test_name,
                passed=False,
                output="",
                error_message="Test timed out after 5 minutes",
                duration_seconds=300
            )

    def _run_python_test(self, test_spec: Dict) -> DODTestResult:
        """Run a Python code test.

        Args:
            test_spec: Test specification with 'code' field

        Returns:
            DODTestResult
        """
        import time

        test_name = test_spec['name']
        code = test_spec['code']

        start_time = time.time()

        try:
            # Execute Python code in isolated namespace
            namespace = {}
            exec(code, namespace)

            duration = time.time() - start_time

            return DODTestResult(
                test_name=test_name,
                passed=True,
                output="Python test passed",
                duration_seconds=duration
            )

        except AssertionError as e:
            duration = time.time() - start_time
            return DODTestResult(
                test_name=test_name,
                passed=False,
                output="",
                error_message=f"Assertion failed: {str(e)}",
                duration_seconds=duration
            )

    def _run_file_exists_test(self, test_spec: Dict) -> DODTestResult:
        """Check if required files exist.

        Args:
            test_spec: Test specification with 'files' list

        Returns:
            DODTestResult
        """
        test_name = test_spec['name']
        files = test_spec.get('files', [])

        missing_files = []
        for file_path in files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            return DODTestResult(
                test_name=test_name,
                passed=False,
                output="",
                error_message=f"Missing files: {', '.join(missing_files)}"
            )

        return DODTestResult(
            test_name=test_name,
            passed=True,
            output=f"All {len(files)} files exist"
        )

    def _generate_failure_summary(self, results: List[DODTestResult]) -> str:
        """Generate human-readable failure summary.

        Args:
            results: List of test results

        Returns:
            Markdown formatted failure summary
        """
        failed = [r for r in results if not r.passed]

        summary = "## DOD Test Failures\n\n"

        for result in failed:
            summary += f"### ❌ {result.test_name}\n"
            summary += f"**Error**: {result.error_message}\n\n"
            if result.output:
                summary += f"**Output**:\n```\n{result.output[:500]}\n```\n\n"

        return summary

    def _create_error_suite(self, user_story_id: str, error: str) -> DODTestSuite:
        """Create error suite when DOD tests can't run."""
        return DODTestSuite(
            user_story_id=user_story_id,
            total_tests=0,
            passed_tests=0,
            failed_tests=1,
            results=[],
            overall_passed=False,
            failure_summary=f"Error: {error}"
        )

    def _create_empty_suite(self, user_story_id: str) -> DODTestSuite:
        """Create empty suite when no DOD tests defined."""
        return DODTestSuite(
            user_story_id=user_story_id,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            results=[],
            overall_passed=True,  # No tests = assume passed
            failure_summary=None
        )
```

### 3.2 Integration with RoadmapEditor

Add methods to RoadmapEditor:

```python
def mark_user_story_complete(self, story_id: str, run_dod_tests: bool = True) -> Dict:
    """Mark User Story as complete with optional DOD testing.

    Args:
        story_id: User Story ID
        run_dod_tests: Whether to run DOD tests before marking complete

    Returns:
        Result dict with:
        - success: bool
        - dod_passed: bool (if tests run)
        - dod_results: DODTestSuite (if tests run)
        - message: str
    """
    if not run_dod_tests:
        self.update_user_story(story_id, 'status', '✅ Complete')
        return {'success': True, 'message': 'Marked complete without DOD tests'}

    # Run DOD tests
    from coffee_maker.cli.dod_tester import DODTester
    tester = DODTester(self)
    results = tester.run_dod_tests(story_id)

    if results.overall_passed:
        # All tests passed - mark as complete
        self.update_user_story(story_id, 'status', '✅ Complete')
        return {
            'success': True,
            'dod_passed': True,
            'dod_results': results,
            'message': f'DOD tests passed ({results.passed_tests}/{results.total_tests})'
        }
    else:
        # Tests failed - DO NOT mark as complete
        self.update_user_story(story_id, 'status', '⚠️ DOD Failed')

        # Create fix priority
        self._create_dod_fix_priority(story_id, results)

        return {
            'success': False,
            'dod_passed': False,
            'dod_results': results,
            'message': f'DOD tests failed ({results.failed_tests}/{results.total_tests})'
        }

def _create_dod_fix_priority(self, story_id: str, dod_results: DODTestSuite):
    """Create priority to fix DOD test failures.

    Args:
        story_id: Failed User Story ID
        dod_results: DOD test results
    """
    # Get next priority number (insert as X.Y sub-priority)
    # ...

    priority_title = f"Fix {story_id} DOD Failures"
    priority_description = f"""
## 🚨 CRITICAL: Fix DOD Test Failures for {story_id}

The implementation of {story_id} failed Definition of Done tests.
This is now the **TOP PRIORITY** until fixed.

{dod_results.failure_summary}

**Action Required**:
1. Review failure output above
2. Fix the failing tests
3. Re-run DOD tests: `project-manager test-dod {story_id}`
4. Verify all tests pass before marking complete

**Original User Story**: {story_id}
**Failed Tests**: {dod_results.failed_tests}/{dod_results.total_tests}
"""

    self.add_priority(
        priority_number=f"PRIORITY {next_number}",
        title=priority_title,
        duration="1-2 days",
        impact="⭐⭐⭐⭐⭐",
        status="🚨 Critical - DOD Fix Required",
        description=priority_description,
        deliverables=[
            f"Fix all {dod_results.failed_tests} failing DOD tests",
            f"Re-run DOD tests and verify 100% pass",
            f"Update {story_id} status to Complete"
        ]
    )
```

### 3.3 CLI Command: `/test-dod`

Add new command to run DOD tests manually:

```python
# coffee_maker/cli/commands/test_dod.py

@register_command
class TestDODCommand(BaseCommand):
    """Run Definition of Done tests for a User Story.

    Usage:
        /test-dod <story_id>  - Run DOD tests
        /test-dod US-001
    """

    @property
    def name(self) -> str:
        return "test-dod"

    @property
    def description(self) -> str:
        return "Run Definition of Done tests for a User Story"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        if len(args) < 1:
            return self.format_error("Missing story ID\nUsage: /test-dod <story_id>")

        story_id = args[0]
        if not story_id.upper().startswith("US-"):
            story_id = f"US-{story_id}"

        # Run DOD tests
        from coffee_maker.cli.dod_tester import DODTester
        tester = DODTester(editor)

        self.console.print(f"\n[cyan]Running DOD tests for {story_id}...[/]")

        results = tester.run_dod_tests(story_id)

        # Display results
        return self._format_results(results)

    def _format_results(self, results: DODTestSuite) -> str:
        if results.overall_passed:
            output = f"## ✅ DOD Tests PASSED\n\n"
            output += f"**{results.passed_tests}/{results.total_tests} tests passed**\n\n"
            output += "Story meets Definition of Done criteria.\n"
            return self.format_success(output)
        else:
            output = f"## ❌ DOD Tests FAILED\n\n"
            output += f"**{results.failed_tests}/{results.total_tests} tests failed**\n\n"
            output += results.failure_summary
            return self.format_error(output)
```

---

## 4. Workflow Example

### 4.1 Happy Path (DOD Passes)

```
1. code_developer implements US-001
2. code_developer marks US-001 as "🚀 Implementation Complete"
3. project_manager detects status change
4. project_manager runs DOD tests automatically
5. All tests pass ✅
6. project_manager marks US-001 as "✅ Complete"
7. project_manager notifies user: "US-001 shipped! All DOD tests passed."
```

### 4.2 Failure Path (DOD Fails)

```
1. code_developer implements US-001
2. code_developer marks US-001 as "🚀 Implementation Complete"
3. project_manager detects status change
4. project_manager runs DOD tests automatically
5. 2/5 tests fail ❌
6. project_manager:
   - Updates US-001 status to "⚠️ DOD Failed"
   - Creates PRIORITY 4.1: "Fix US-001 DOD Failures"
   - Updates roadmap with failure details
   - Marks PRIORITY 4.1 as "🚨 Critical - TOP PRIORITY"
7. project_manager notifies user:
   "US-001 implementation incomplete. DOD tests failed (2/5).
    Created PRIORITY 4.1 to fix failures.
    code_developer will fix as TOP PRIORITY."
8. code_developer sees PRIORITY 4.1 as next task
9. code_developer fixes issues
10. code_developer re-runs DOD tests: `project-manager test-dod US-001`
11. All tests pass ✅
12. project_manager marks US-001 as "✅ Complete"
13. project_manager marks PRIORITY 4.1 as "✅ Complete"
14. project_manager notifies user: "US-001 NOW shipped! DOD fixes complete."
```

---

## 5. Integration Points

### 5.1 User Story Status Transitions

```
📝 Backlog → 🔄 In Discussion → 📋 Ready → ✅ Assigned →
🚀 Implementation Complete → [DOD Tests Run] →
    ├─ PASS → ✅ Complete
    └─ FAIL → ⚠️ DOD Failed → (Fix Priority Created)
```

### 5.2 Automatic Trigger

Add hook in RoadmapEditor or ChatSession to automatically run DOD tests when:
- User Story status changes to "🚀 Implementation Complete"
- User executes `/complete <story-id>` command

---

## 6. Success Criteria

- [ ] DOD tests can be defined in YAML format within User Stories
- [ ] DOD tests execute automatically when story marked complete
- [ ] Failed DOD tests prevent story from being marked complete
- [ ] Failed DOD automatically creates fix priority with details
- [ ] code_developer sees fix priority as TOP PRIORITY
- [ ] Manual DOD testing available via `/test-dod` command
- [ ] DOD test results clearly show which tests failed and why

---

**End of Design Document**
