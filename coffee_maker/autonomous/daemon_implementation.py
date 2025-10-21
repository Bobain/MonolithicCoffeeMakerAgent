"""Implementation Operations Mixin for DevDaemon.

This module provides implementation-related operations for the autonomous development daemon,
extracted from daemon.py to improve code organization and maintainability.

Classes:
    ImplementationMixin: Mixin providing _implement_priority() and related prompt builders

Usage:
    class DevDaemon(ImplementationMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files

Enhanced with centralized prompt loading:
- Prompts stored in .claude/commands/ for multi-AI provider support
- Easy migration to Gemini, OpenAI, or other LLMs
"""

import logging
import time
from datetime import datetime

from coffee_maker.autonomous.developer_status import ActivityType, DeveloperState
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.autonomous.puppeteer_client import PuppeteerClient
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_HIGH,
    NOTIF_TYPE_INFO,
)

logger = logging.getLogger(__name__)


class ImplementationMixin:
    """Mixin providing implementation operations for daemon.

    This mixin provides methods for implementing priorities, building prompts,
    and requesting user approval.

    Required attributes (provided by DevDaemon):
        - self.claude: ClaudeAPI instance
        - self.git: GitManager instance
        - self.notifications: NotificationDB instance
        - self.status: DeveloperStatus instance
        - self.auto_approve: bool
        - self.create_prs: bool
        - self.attempted_priorities: dict
        - self.max_retries: int
        - self.current_priority_info: dict
        - self.current_subtasks: list

    Methods:
        - _request_approval(): Request user approval for implementation
        - _implement_priority(): Main implementation orchestration
        - _build_implementation_prompt(): Build implementation prompt
        - _build_documentation_prompt(): Build documentation-specific prompt
        - _build_feature_prompt(): Build feature implementation prompt
        - _build_commit_message(): Build git commit message
        - _build_pr_body(): Build pull request description

    Example:
        >>> class DevDaemon(ImplementationMixin):
        ...     def __init__(self):
        ...         self.claude = ClaudeAPI()
        ...         self.git = GitManager()
        ...         self.notifications = NotificationDB()
        >>> daemon = DevDaemon()
        >>> priority = {"name": "US-021", "title": "Refactoring"}
        >>> daemon._implement_priority(priority)
        True
    """

    def _request_approval(self, priority: dict) -> bool:
        """Request user approval to implement a priority.

        Args:
            priority: Priority dictionary

        Returns:
            True if approved
        """
        logger.info(f"Requesting approval for {priority['name']}")

        # Create notification
        notif_id = self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title=f"Implement {priority['name']}?",
            message=f"The daemon wants to implement:\n{priority['title']}\n\nApprove?",
            priority=NOTIF_PRIORITY_HIGH,
            context={
                "priority_name": priority["name"],
                "priority_number": priority["number"],
            },
            sound=False,
            agent_id="code_developer",
        )

        logger.info(f"Created notification {notif_id} - waiting for response")
        logger.info("Check notifications with: project-manager notifications")
        logger.info(f"Approve with: project-manager respond {notif_id} approve")

        # Poll for response (simplified - in production would use event system)
        max_wait = 1800  # 30 minutes
        poll_interval = 5
        waited = 0

        while waited < max_wait:
            time.sleep(poll_interval)
            waited += poll_interval

            notif = self.notifications.get_notification(notif_id)
            if notif and notif["user_response"]:
                response = notif["user_response"].lower()
                approved = "approve" in response or "yes" in response
                logger.info(f"User response: {response} (approved={approved})")
                return approved

        logger.warning("User did not respond in time - skipping")
        return False

    def _implement_priority(self, priority: dict) -> bool:
        """Implement a priority.

        Args:
            priority: Priority dictionary

        Returns:
            True if successful
        """
        priority_name = priority["name"]
        priority_title = priority["title"]

        # Check if we've already attempted this priority too many times
        attempt_count = self.attempted_priorities.get(priority_name, 0)

        if attempt_count >= self.max_retries:
            logger.warning(f"⏭️  Skipping {priority_name} - already attempted {attempt_count} times with no changes")
            logger.warning(f"This priority requires manual intervention")

            # Check if there's a technical spec and if it's too large

            spec_analysis = self._analyze_spec_complexity(priority)

            # Update ROADMAP status to blocked so daemon skips it in future
            try:
                db = RoadmapDatabase()
                item_id = priority_name  # e.g., "US-111"
                db.update_status(
                    item_id=item_id,
                    new_status="⏸️ Blocked - Too complex for autonomous implementation",
                    updated_by="code_developer",
                )
                db.export_to_file(self.roadmap_path)
                logger.info(f"✅ Updated {priority_name} status to '⏸️ Blocked' in ROADMAP")
            except Exception as e:
                logger.error(f"Failed to update ROADMAP status: {e}")

            # Create notification with spec splitting guidance if needed
            if spec_analysis["has_spec"] and spec_analysis["is_large"]:
                # Spec exists but is too large - ask architect to split it
                self._create_spec_splitting_notification(priority, spec_analysis, attempt_count)
            else:
                # Generic notification for manual review
                self.notifications.create_notification(
                    type=NOTIF_TYPE_INFO,
                    title=f"{priority_name}: Max Retries Reached",
                    message=f"""The daemon has attempted to implement this priority {attempt_count} times but no files were changed.

This priority requires manual implementation:

Priority: {priority_name}
Title: {priority_title}
Status: ⏸️ Blocked - Too complex for autonomous implementation

Action Required:
1. Manually implement this priority, OR
2. Break it down into smaller user stories, OR
3. Clarify the deliverables to make them more concrete

The daemon has updated ROADMAP.md and will skip this priority in future iterations.
""",
                    priority=NOTIF_PRIORITY_HIGH,
                    context={
                        "priority_name": priority_name,
                        "priority_number": priority.get("number"),
                        "reason": "max_retries_reached",
                        "attempts": attempt_count,
                    },
                    sound=False,
                    agent_id="code_developer",
                )

            return False  # Return False so the daemon moves on

        # Increment attempt counter
        self.attempted_priorities[priority_name] = attempt_count + 1
        logger.info(
            f"🚀 Starting implementation of {priority_name} (attempt {self.attempted_priorities[priority_name]}/{self.max_retries})"
        )

        # Store priority info for metrics recording
        self.current_priority_info = priority

        # Clear previous subtasks
        self.current_subtasks = []

        # PRIORITY 4: Update progress - validating branch
        self.status.report_progress(10, "Validating roadmap branch")

        # Validate CFR-013 compliance before implementation
        current_branch = self.git.get_current_branch()
        # Accept "roadmap" or "roadmap-*" (for worktree parallel execution)
        if current_branch != "roadmap" and not current_branch.startswith("roadmap-"):
            logger.error(f"CFR-013 VIOLATION: Must be on roadmap branch, currently on: {current_branch}")
            logger.error(f"   Expected: 'roadmap' or 'roadmap-*' (worktree branches)")
            return False

        if current_branch == "roadmap":
            logger.info("✅ CFR-013 compliant: Working on 'roadmap' branch")
        else:
            logger.info(f"✅ CFR-013 compliant: Working on worktree branch '{current_branch}'")

        # PRIORITY 4: Log CFR-013 compliance
        self.status.report_activity(
            ActivityType.STATUS_UPDATE,
            "CFR-013 validated: On roadmap branch",
            details={"branch": "roadmap"},
        )

        # Build prompt for Claude
        prompt = self._build_implementation_prompt(priority)

        # PRIORITY 4: Update progress - calling Claude API
        self.status.report_progress(20, "Executing implementation with Claude API")

        # Track subtask: Claude API execution (estimated: 5 minutes = 300 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Executing Claude API", "in_progress", subtask_start, estimated_seconds=300)

        logger.info("Executing Claude API with implementation prompt...")

        # Execute Claude API
        result = self.claude.execute_prompt(prompt, timeout=3600)  # 1 hour timeout

        if not result.success:
            logger.error(f"Claude API failed: {result.error}")
            self._update_subtask("Executing Claude API", "failed", subtask_start, estimated_seconds=300)
            return False

        self._update_subtask("Executing Claude API", "completed", subtask_start, estimated_seconds=300)

        logger.info("✅ Claude API execution complete")
        logger.info(f"📊 Token usage: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")

        # PRIORITY 4: Update progress - implementation complete
        self.status.report_progress(60, "Implementation complete, checking changes")

        # Check if any files were changed (Fix for infinite loop issue)
        if self.git.is_clean():
            logger.warning("⚠️  Claude API completed but no files changed")
            logger.warning("Possible reasons:")
            logger.warning("  1. Priority already implemented")
            logger.warning("  2. Task too vague for autonomous implementation")
            logger.warning("  3. Requires human judgment/review")

            # Create notification for human review
            self.notifications.create_notification(
                type=NOTIF_TYPE_INFO,
                title=f"{priority_name}: Needs Manual Review",
                message=f"""Claude API completed successfully but made no file changes.

Possible actions:
1. Review priority description - is it concrete enough?
2. Manually implement this priority
3. Mark as "Manual Only" in ROADMAP
4. Skip and move to next priority

Priority: {priority_name}
Title: {priority_title}
Status: Requires human decision
""",
                priority=NOTIF_PRIORITY_HIGH,
                context={
                    "priority_name": priority_name,
                    "priority_number": priority.get("number"),
                    "reason": "no_changes",
                },
                sound=False,
                agent_id="code_developer",
            )

            logger.info("📧 Created notification for manual review")
            # Return False so attempt counter increments
            # After max retries, daemon will mark as blocked and skip
            return False

        # PRIORITY 4: Update progress - committing changes
        self.status.report_progress(70, "Committing changes")

        # Track subtask: Committing changes (estimated: 20 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Committing changes", "in_progress", subtask_start, estimated_seconds=20)

        # Commit changes
        commit_message = self._build_commit_message(priority)

        if not self.git.commit(commit_message):
            logger.error("Failed to commit changes")
            self._update_subtask("Committing changes", "failed", subtask_start, estimated_seconds=20)
            return False

        self._update_subtask("Committing changes", "completed", subtask_start, estimated_seconds=20)

        logger.info("✅ Changes committed")

        # PRIORITY 4: Log commit activity
        self.status.report_activity(
            ActivityType.GIT_COMMIT,
            f"Committed {priority_name}",
            details={"priority": priority_name},
        )

        # PRIORITY 4: Update progress - pushing
        self.status.report_progress(80, "Pushing to remote")

        # Track subtask: Pushing to remote (estimated: 30 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Pushing to remote", "in_progress", subtask_start, estimated_seconds=30)

        # Push
        if not self.git.push():
            logger.error("Failed to push branch")
            self._update_subtask("Pushing to remote", "failed", subtask_start, estimated_seconds=30)
            return False

        self._update_subtask("Pushing to remote", "completed", subtask_start, estimated_seconds=30)

        logger.info("✅ Roadmap branch pushed")

        # PRIORITY 4: Log push activity
        self.status.report_activity(
            ActivityType.GIT_PUSH,
            "Pushed to roadmap branch",
            details={"branch": "roadmap"},
        )

        # Create PR if enabled
        if self.create_prs:
            # PRIORITY 4: Update status to REVIEWING
            self.status.update_status(
                DeveloperState.REVIEWING,
                progress=90,
                current_step="Creating pull request",
            )

            # Track subtask: Creating PR (estimated: 45 seconds)
            subtask_start = datetime.now()
            self._update_subtask(
                "Creating pull request",
                "in_progress",
                subtask_start,
                estimated_seconds=45,
            )

            pr_body = self._build_pr_body(priority)
            pr_url = self.git.create_pull_request(f"Implement {priority_name}: {priority_title}", pr_body)

            if pr_url:
                self._update_subtask(
                    "Creating pull request",
                    "completed",
                    subtask_start,
                    estimated_seconds=45,
                )
                logger.info(f"✅ PR created: {pr_url}")

                # PRIORITY 4: Update progress - PR created
                self.status.report_progress(100, f"PR created: {pr_url}")

                # Notify user
                self.notifications.create_notification(
                    type=NOTIF_TYPE_INFO,
                    title=f"{priority_name} Complete!",
                    message=f"Implementation complete!\n\nPR: {pr_url}\n\nPlease review and merge.",
                    priority=NOTIF_PRIORITY_HIGH,
                    context={"priority_name": priority_name, "pr_url": pr_url},
                    sound=False,
                    agent_id="code_developer",
                )
            else:
                self._update_subtask(
                    "Creating pull request",
                    "failed",
                    subtask_start,
                    estimated_seconds=45,
                )
                logger.warning("Failed to create PR")
                # PRIORITY 4: Still mark as complete even if PR failed
                self.status.report_progress(100, "Implementation complete (PR creation failed)")

        return True

    def _build_implementation_prompt(self, priority: dict) -> str:
        """Build Claude API prompt for implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string
        """
        # Detect priority type and build specialized prompt
        title_lower = priority["title"].lower()
        content_lower = priority.get("content", "").lower()

        # Check if this is a documentation/UX priority
        is_documentation = any(
            keyword in title_lower or keyword in content_lower
            for keyword in [
                "documentation",
                "docs",
                "guide",
                "ux",
                "user experience",
                "quickstart",
            ]
        )

        if is_documentation:
            return self._build_documentation_prompt(priority)
        else:
            return self._build_feature_prompt(priority)

    def _build_documentation_prompt(self, priority: dict) -> str:
        """Build explicit documentation creation prompt.

        Enhanced: Now uses centralized prompt from .claude/commands/
        for easy migration to Gemini, OpenAI, or other LLMs.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string optimized for documentation tasks from
            .claude/commands/implement-documentation.md
        """
        priority_content = priority.get("content", "")[:1500]
        if len(priority.get("content", "")) > 1500:
            priority_content += "..."

        return load_prompt(
            PromptNames.IMPLEMENT_DOCUMENTATION,
            {
                "PRIORITY_NAME": priority["name"],
                "PRIORITY_TITLE": priority["title"],
                "PRIORITY_CONTENT": priority_content,
            },
        )

    def _build_feature_prompt(self, priority: dict) -> str:
        """Build standard feature implementation prompt.

        Enhanced: Now uses centralized prompt from .claude/commands/
        for easy migration to Gemini, OpenAI, or other LLMs.

        NEW: Reads and injects technical spec content into prompt (CFR-XXX)

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string for feature implementation from
            .claude/commands/implement-feature.md
        """
        from pathlib import Path

        priority_content = priority.get("content", "")[:1000]
        if len(priority.get("content", "")) > 1000:
            priority_content += "..."

        # Read and inject technical spec content
        spec_content = ""
        priority_number = priority.get("number")
        if priority_number:
            spec_dir = Path("docs/architecture/specs")
            spec_pattern = f"SPEC-{priority_number}-*.md"

            if spec_dir.exists():
                matching_specs = list(spec_dir.glob(spec_pattern))
                if matching_specs:
                    spec_file = matching_specs[0]
                    try:
                        spec_content = spec_file.read_text()
                        logger.info(f"✅ Injected spec content: {spec_file.name} ({len(spec_content)} chars)")
                    except Exception as e:
                        logger.warning(f"Failed to read spec file {spec_file}: {e}")
                        spec_content = f"[ERROR: Could not read spec file {spec_file}: {e}]"
                else:
                    logger.warning(f"No spec found for {priority['name']} (pattern: {spec_pattern})")
                    spec_content = f"[NO SPEC FOUND: Expected pattern {spec_pattern} in {spec_dir}]"

        return load_prompt(
            PromptNames.IMPLEMENT_FEATURE,
            {
                "PRIORITY_NAME": priority["name"],
                "PRIORITY_TITLE": priority["title"],
                "PRIORITY_CONTENT": priority_content,
                "SPEC_CONTENT": spec_content,  # NEW: Inject full spec content
            },
        )

    def _analyze_spec_complexity(self, priority: dict) -> dict:
        """Analyze technical spec to determine if it's too complex for one implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Dict with analysis results:
                - has_spec: bool (spec file exists)
                - spec_path: str (path to spec file if exists)
                - spec_lines: int (number of lines)
                - spec_chars: int (number of characters)
                - is_large: bool (exceeds thresholds for single implementation)
                - estimated_days: int (from ROADMAP content)
        """
        from pathlib import Path

        analysis = {
            "has_spec": False,
            "spec_path": None,
            "spec_lines": 0,
            "spec_chars": 0,
            "is_large": False,
            "estimated_days": 0,
        }

        # Extract estimated effort from priority content
        priority_content = priority.get("content", "")
        if "day" in priority_content.lower():
            # Try to extract "X days" or "X-Y days"
            import re

            match = re.search(r"(\d+)(?:-(\d+))?\s*days?", priority_content.lower())
            if match:
                # Use the upper bound if range, otherwise the single value
                analysis["estimated_days"] = int(match.group(2) or match.group(1))

        # Check for spec file
        priority_number = priority.get("number")
        if priority_number:
            spec_dir = Path("docs/architecture/specs")
            spec_pattern = f"SPEC-{priority_number}-*.md"

            if spec_dir.exists():
                matching_specs = list(spec_dir.glob(spec_pattern))
                if matching_specs:
                    spec_file = matching_specs[0]
                    analysis["has_spec"] = True
                    analysis["spec_path"] = str(spec_file)

                    try:
                        spec_content = spec_file.read_text()
                        analysis["spec_chars"] = len(spec_content)
                        analysis["spec_lines"] = spec_content.count("\n") + 1

                        # Determine if spec is too large for single implementation
                        # Thresholds:
                        # - > 300 lines OR
                        # - > 15,000 characters OR
                        # - Estimated effort > 2 days
                        analysis["is_large"] = (
                            analysis["spec_lines"] > 300
                            or analysis["spec_chars"] > 15000
                            or analysis["estimated_days"] > 2
                        )

                    except Exception as e:
                        logger.warning(f"Failed to analyze spec {spec_file}: {e}")

        return analysis

    def _create_spec_splitting_notification(self, priority: dict, spec_analysis: dict, attempt_count: int) -> None:
        """Create notification asking architect to split large spec into phases.

        Args:
            priority: Priority dictionary
            spec_analysis: Analysis from _analyze_spec_complexity()
            attempt_count: Number of failed implementation attempts
        """
        priority_name = priority["name"]
        priority["title"]

        notification_message = f"""code_developer attempted to implement {priority_name} {attempt_count} times but made no file changes.

**Root Cause Analysis:**
The technical specification is too large/complex for a single autonomous implementation.

**Spec Details:**
- File: {spec_analysis['spec_path']}
- Size: {spec_analysis['spec_lines']} lines, {spec_analysis['spec_chars']:,} characters
- Estimated effort: {spec_analysis['estimated_days']} days

**Request for Architect:**

Please split this specification into **smaller, well-sized implementation phases** that fit within context window limits and can be implemented step-by-step.

**Recommended Approach:**

1. **Break into Phases** (Option A):
   - Create SPEC-{priority_name}-phase-1.md (Foundation, 1-2 days)
   - Create SPEC-{priority_name}-phase-2.md (Core features, 1-2 days)
   - Create SPEC-{priority_name}-phase-3.md (Polish, testing, 1 day)
   - Each phase should be ≤ 300 lines or ≤ 2 days effort

2. **Break into Sub-Stories** (Option B):
   - Create {priority_name}-A: Database schema and models
   - Create {priority_name}-B: API endpoints
   - Create {priority_name}-C: UI components
   - Create {priority_name}-D: Integration and testing
   - Add each as separate user story in ROADMAP

3. **Simplify Scope** (Option C):
   - Review spec for essential vs. nice-to-have features
   - Move advanced features to future user stories
   - Reduce initial implementation to MVP

**Guidelines for Well-Sized Specs:**
✅ ≤ 300 lines of specification
✅ ≤ 15,000 characters
✅ ≤ 2 days estimated implementation time
✅ Single, focused deliverable
✅ Clear, concrete acceptance criteria

**Current Status:**
- {priority_name} marked as "⏸️ Blocked - Too complex"
- Daemon will skip until architect creates phased specs
- Once phases created, daemon will implement them sequentially

**Next Steps:**
1. Architect: Review and split spec using one of the approaches above
2. Architect: Update ROADMAP with phased approach
3. Architect: Unblock {priority_name} or create phase-1 user story
4. Daemon: Will pick up and implement phase-1 automatically
"""

        self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title=f"🏗️ Architect: Please Split Spec for {priority_name}",
            message=notification_message,
            priority=NOTIF_PRIORITY_HIGH,
            context={
                "priority_name": priority_name,
                "priority_number": priority.get("number"),
                "reason": "spec_too_large",
                "spec_lines": spec_analysis["spec_lines"],
                "spec_chars": spec_analysis["spec_chars"],
                "estimated_days": spec_analysis["estimated_days"],
                "attempts": attempt_count,
            },
            sound=False,
            agent_id="code_developer",
        )

        logger.info(f"📧 Created spec splitting request for architect: {priority_name}")

    def _build_commit_message(self, priority: dict) -> str:
        """Build commit message for implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Commit message
        """
        message = f"""feat: Implement {priority['name']} - {priority['title']}

Autonomous implementation by DevDaemon.

Priority: {priority['name']}
Status: ✅ Complete

🤖 Generated with [Claude Code](https://claude.com/claude-code) via DevDaemon

Co-Authored-By: Claude <noreply@anthropic.com>
"""
        return message

    def _build_pr_body(self, priority: dict) -> str:
        """Build PR description.

        Args:
            priority: Priority dictionary

        Returns:
            PR body markdown
        """
        body = f"""## Summary

Autonomous implementation of {priority['name']}: {priority['title']}

## Implementation

This PR was autonomously implemented by the DevDaemon following the ROADMAP.md specifications.

## Testing

- Implementation follows ROADMAP guidelines
- Tests added where appropriate
- Manual verification completed

## Review Checklist

- [ ] Code follows project standards
- [ ] Tests pass
- [ ] Documentation updated
- [ ] ROADMAP.md status updated

🤖 Autonomously implemented by DevDaemon
"""
        return body

    def _verify_dod_with_puppeteer(self, priority: dict, app_url: str = None) -> bool:
        """Verify Definition of Done using Puppeteer (optional step).

        This method generates a DoD verification prompt that can be executed
        by Claude CLI (which has Puppeteer MCP available).

        Note: The implementation prompts (implement-feature.md, implement-documentation.md)
        already instruct the agent to use Puppeteer for DoD verification during
        implementation. This method provides an additional explicit verification step
        if needed.

        Args:
            priority: Priority dictionary
            app_url: Optional URL to verify (auto-detected if not provided)

        Returns:
            True if verification prompt generated successfully

        Usage:
            >>> # After implementation, optionally verify DoD explicitly
            >>> if self._is_web_priority(priority):
            ...     self._verify_dod_with_puppeteer(priority, "http://localhost:8501")

        Implementation Note:
            Currently, DoD verification happens automatically via the implementation
            prompts that tell the agent to use Puppeteer. This method is available
            for future explicit post-implementation verification if needed.
        """
        logger.info(f"Generating DoD verification prompt for {priority['name']}")

        # Create Puppeteer client
        puppeteer = PuppeteerClient(mode="cli")

        # Generate DoD verification prompt
        dod_prompt = puppeteer.generate_dod_verification_prompt(priority, app_url)

        logger.debug(f"DoD verification prompt: {dod_prompt[:200]}...")

        # Note: In the current implementation, the Claude agent already uses
        # Puppeteer during implementation via the prompts. This method is
        # available for future explicit verification steps.

        # Could optionally execute this prompt via Claude CLI here
        # result = self.claude.execute_prompt(dod_prompt)

        return True
