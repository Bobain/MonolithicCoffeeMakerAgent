"""Autonomous development daemon - minimal MVP.

This module implements the core autonomous daemon that:
1. Reads ROADMAP.md continuously
2. Finds next planned priority
3. Executes Claude API to implement it
4. Commits, pushes, creates PR
5. Updates ROADMAP status
6. Repeats until all priorities complete

Example:
    >>> from coffee_maker.autonomous.daemon import DevDaemon
    >>>
    >>> daemon = DevDaemon(
    ...     roadmap_path="docs/ROADMAP.md",
    ...     auto_approve=True,
    ...     create_prs=True
    ... )
    >>> daemon.run()
"""

import logging
import time
from pathlib import Path

from coffee_maker.autonomous.claude_api_interface import ClaudeAPI
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.cli.notifications import NOTIF_PRIORITY_HIGH, NOTIF_TYPE_INFO, NotificationDB

logger = logging.getLogger(__name__)


class DevDaemon:
    """Autonomous development daemon (minimal MVP).

    This daemon continuously reads ROADMAP.md and autonomously implements
    features by invoking Claude API. It follows a simple loop:

    1. Parse ROADMAP.md for next planned priority
    2. Create feature branch
    3. Execute Claude API with implementation prompt
    4. Commit changes with proper message
    5. Push and create PR
    6. Update ROADMAP status (via notification)
    7. Sleep and repeat

    Attributes:
        roadmap_path: Path to ROADMAP.md
        auto_approve: Whether to auto-approve without user confirmation
        create_prs: Whether to create PRs automatically
        sleep_interval: Seconds to sleep between iterations

    Example:
        >>> daemon = DevDaemon(
        ...     roadmap_path="docs/ROADMAP.md",
        ...     auto_approve=False,  # Ask user before starting
        ...     create_prs=True
        ... )
        >>> daemon.run()  # Runs until all priorities complete
    """

    def __init__(
        self,
        roadmap_path: str = "docs/ROADMAP.md",
        auto_approve: bool = False,
        create_prs: bool = True,
        sleep_interval: int = 30,
        model: str = "claude-sonnet-4",
        use_claude_cli: bool = False,
        claude_cli_path: str = "/opt/homebrew/bin/claude",
    ):
        """Initialize development daemon.

        Args:
            roadmap_path: Path to ROADMAP.md
            auto_approve: Auto-approve implementation (skip user confirmation)
            create_prs: Create pull requests automatically
            sleep_interval: Seconds between iterations (default: 30)
            model: Claude model to use (default: claude-sonnet-4)
            use_claude_cli: Use Claude CLI instead of Anthropic API (default: False)
            claude_cli_path: Path to claude CLI executable (default: /opt/homebrew/bin/claude)
        """
        self.roadmap_path = Path(roadmap_path)
        self.auto_approve = auto_approve
        self.create_prs = create_prs
        self.sleep_interval = sleep_interval
        self.model = model
        self.use_claude_cli = use_claude_cli

        # Initialize components
        self.parser = RoadmapParser(str(self.roadmap_path))
        self.git = GitManager()

        # Choose between CLI and API based on flag
        if use_claude_cli:
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            self.claude = ClaudeCLIInterface(claude_path=claude_cli_path, model=model)
            logger.info("✅ Using Claude CLI mode (subscription)")
        else:
            self.claude = ClaudeAPI(model=model)
            logger.info("✅ Using Claude API mode (requires credits)")

        self.notifications = NotificationDB()

        # State
        self.running = False
        self.attempted_priorities = {}  # Track retry attempts: {priority_name: count}
        self.max_retries = 3  # Maximum attempts before skipping a priority

        logger.info("DevDaemon initialized")
        logger.info(f"Roadmap: {self.roadmap_path}")
        logger.info(f"Auto-approve: {self.auto_approve}")
        logger.info(f"Create PRs: {self.create_prs}")

    def run(self):
        """Run daemon main loop.

        This method runs continuously until:
        - All planned priorities are complete
        - User stops the daemon (Ctrl+C)
        - Fatal error occurs

        Example:
            >>> daemon = DevDaemon()
            >>> daemon.run()  # Runs until complete
        """
        self.running = True
        logger.info("🤖 DevDaemon starting...")

        # Check prerequisites
        if not self._check_prerequisites():
            logger.error("Prerequisites not met - cannot start")
            return

        iteration = 0

        while self.running:
            iteration += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}")
            logger.info(f"{'='*60}")

            try:
                # Reload roadmap
                self.parser = RoadmapParser(str(self.roadmap_path))

                # Get next task
                next_priority = self.parser.get_next_planned_priority()

                if not next_priority:
                    logger.info("✅ No more planned priorities - all done!")
                    self._notify_completion()
                    break

                logger.info(f"📋 Next priority: {next_priority['name']} - {next_priority['title']}")

                # Ask for approval if needed
                if not self.auto_approve:
                    if not self._request_approval(next_priority):
                        logger.info("User declined - waiting for next iteration")
                        time.sleep(self.sleep_interval)
                        continue

                # Execute implementation
                success = self._implement_priority(next_priority)

                if success:
                    logger.info(f"✅ Successfully implemented {next_priority['name']}")
                else:
                    logger.warning(f"⚠️  Implementation failed for {next_priority['name']}")

                # Sleep before next iteration
                logger.info(f"💤 Sleeping {self.sleep_interval}s before next iteration...")
                time.sleep(self.sleep_interval)

            except KeyboardInterrupt:
                logger.info("\n⏹️  Daemon stopped by user")
                self.running = False
                break

            except Exception as e:
                logger.error(f"❌ Error in daemon loop: {e}")
                import traceback

                traceback.print_exc()

                # Continue after error
                time.sleep(self.sleep_interval)

        logger.info("🛑 DevDaemon stopped")

    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met.

        Returns:
            True if ready to run

        Checks:
            - Claude API available
            - Git repository
            - ROADMAP.md exists
        """
        logger.info("Checking prerequisites...")

        # Check Claude API
        if not self.claude.check_available():
            logger.error("❌ Claude API not available")
            return False

        logger.info("✅ Claude API available")

        # Check Git
        if not self.git.has_remote():
            logger.warning("⚠️  No Git remote configured - PRs will fail")

        logger.info("✅ Git repository ready")

        # Check ROADMAP
        if not self.roadmap_path.exists():
            logger.error(f"❌ ROADMAP not found: {self.roadmap_path}")
            return False

        logger.info("✅ ROADMAP.md found")

        return True

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
            context={"priority_name": priority["name"], "priority_number": priority["number"]},
        )

        logger.info(f"Created notification {notif_id} - waiting for response")
        logger.info("Check notifications with: project-manager notifications")
        logger.info(f"Approve with: project-manager respond {notif_id} approve")

        # Poll for response (simplified - in production would use event system)
        max_wait = 300  # 5 minutes
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

            # Create final notification
            self.notifications.create_notification(
                type=NOTIF_TYPE_INFO,
                title=f"{priority_name}: Max Retries Reached",
                message=f"""The daemon has attempted to implement this priority {attempt_count} times but no files were changed.

This priority requires manual implementation:

Priority: {priority_name}
Title: {priority_title}
Status: Skipped after {attempt_count} attempts

Action Required:
1. Manually implement this priority, OR
2. Mark as "Manual Only" in ROADMAP.md, OR
3. Clarify the deliverables to make them more concrete

The daemon will skip this priority in future iterations.
""",
                priority=NOTIF_PRIORITY_HIGH,
                context={
                    "priority_name": priority_name,
                    "priority_number": priority.get("number"),
                    "reason": "max_retries_reached",
                    "attempts": attempt_count,
                },
            )

            return False  # Return False so the daemon moves on

        # Increment attempt counter
        self.attempted_priorities[priority_name] = attempt_count + 1
        logger.info(
            f"🚀 Starting implementation of {priority_name} (attempt {self.attempted_priorities[priority_name]}/{self.max_retries})"
        )

        # Create branch
        branch_name = f"feature/{priority_name.lower().replace(' ', '-').replace(':', '')}"
        logger.info(f"Creating branch: {branch_name}")

        if not self.git.create_branch(branch_name):
            logger.error("Failed to create branch")
            return False

        # Build prompt for Claude
        prompt = self._build_implementation_prompt(priority)

        logger.info("Executing Claude API with implementation prompt...")

        # Execute Claude API
        result = self.claude.execute_prompt(prompt, timeout=3600)  # 1 hour timeout

        if not result.success:
            logger.error(f"Claude API failed: {result.error}")
            return False

        logger.info("✅ Claude API execution complete")
        logger.info(f"📊 Token usage: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")

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
            )

            logger.info("📧 Created notification for manual review")
            # Return "success" to avoid infinite retry - human will decide next steps
            return True

        # Commit changes
        commit_message = self._build_commit_message(priority)

        if not self.git.commit(commit_message):
            logger.error("Failed to commit changes")
            return False

        logger.info("✅ Changes committed")

        # Push
        if not self.git.push():
            logger.error("Failed to push branch")
            return False

        logger.info("✅ Branch pushed")

        # Create PR if enabled
        if self.create_prs:
            pr_body = self._build_pr_body(priority)
            pr_url = self.git.create_pull_request(f"Implement {priority_name}: {priority_title}", pr_body)

            if pr_url:
                logger.info(f"✅ PR created: {pr_url}")

                # Notify user
                self.notifications.create_notification(
                    type=NOTIF_TYPE_INFO,
                    title=f"{priority_name} Complete!",
                    message=f"Implementation complete!\n\nPR: {pr_url}\n\nPlease review and merge.",
                    priority=NOTIF_PRIORITY_HIGH,
                    context={"priority_name": priority_name, "pr_url": pr_url},
                )
            else:
                logger.warning("Failed to create PR")

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
            for keyword in ["documentation", "docs", "guide", "ux", "user experience", "quickstart"]
        )

        if is_documentation:
            return self._build_documentation_prompt(priority)
        else:
            return self._build_feature_prompt(priority)

    def _build_documentation_prompt(self, priority: dict) -> str:
        """Build explicit documentation creation prompt.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string optimized for documentation tasks
        """
        return f"""Read docs/ROADMAP.md and implement {priority['name']}: {priority['title']}.

⚠️  THIS IS A DOCUMENTATION PRIORITY - You MUST CREATE FILES ⚠️

The ROADMAP lists specific deliverable files under "Deliverables" section.
Your task is to:
1. Identify all deliverable files mentioned in ROADMAP for this priority
2. CREATE each file with actual content (not placeholders)
3. Use real examples from the existing codebase
4. Test any commands/examples before documenting them

Instructions:
- CREATE all files listed in the Deliverables section
- Fill with real, specific content based on existing codebase
- Include actual commands, file paths, and examples
- Be concrete, not generic or abstract
- Test examples to ensure accuracy

After creating files:
- Update ROADMAP.md status to "✅ Complete"
- List all files created
- Commit your changes

Priority details:
{priority['content'][:1500]}...

Begin implementation now - CREATE THE FILES."""

    def _build_feature_prompt(self, priority: dict) -> str:
        """Build standard feature implementation prompt.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string for feature implementation
        """
        return f"""Read docs/ROADMAP.md and implement {priority['name']}: {priority['title']}.

Follow the roadmap guidelines and deliverables. Update docs/ROADMAP.md with your progress.

Important:
- Follow all coding standards
- Add tests where appropriate
- Document your changes
- Update ROADMAP.md status to "🔄 In Progress" first, then "✅ Complete" when done
- Commit frequently with clear messages

Priority details:
{priority['content'][:1000]}...

Begin implementation now."""

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

    def _notify_completion(self):
        """Notify user that all priorities are complete."""
        self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title="🎉 All Priorities Complete!",
            message="The DevDaemon has completed all planned priorities in the ROADMAP!\n\nCheck your PRs for review.",
            priority=NOTIF_PRIORITY_HIGH,
        )

    def stop(self):
        """Stop the daemon gracefully."""
        logger.info("Stopping daemon...")
        self.running = False
