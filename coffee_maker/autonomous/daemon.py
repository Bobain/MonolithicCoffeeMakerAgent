"""Autonomous development daemon - minimal MVP.

This module implements the core autonomous daemon that:
1. Reads ROADMAP.md continuously
2. Finds next planned priority
3. Executes Claude CLI to implement it
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

from coffee_maker.autonomous.claude_cli_interface import ClaudeCLI
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.cli.notifications import NOTIF_PRIORITY_HIGH, NOTIF_TYPE_INFO, NotificationDB

logger = logging.getLogger(__name__)


class DevDaemon:
    """Autonomous development daemon (minimal MVP).

    This daemon continuously reads ROADMAP.md and autonomously implements
    features by invoking Claude CLI. It follows a simple loop:

    1. Parse ROADMAP.md for next planned priority
    2. Create feature branch
    3. Execute Claude CLI with implementation prompt
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
    ):
        """Initialize development daemon.

        Args:
            roadmap_path: Path to ROADMAP.md
            auto_approve: Auto-approve implementation (skip user confirmation)
            create_prs: Create pull requests automatically
            sleep_interval: Seconds between iterations (default: 30)
            model: Claude model to use (default: claude-sonnet-4)
        """
        self.roadmap_path = Path(roadmap_path)
        self.auto_approve = auto_approve
        self.create_prs = create_prs
        self.sleep_interval = sleep_interval
        self.model = model

        # Initialize components
        self.parser = RoadmapParser(str(self.roadmap_path))
        self.git = GitManager()
        self.claude = ClaudeCLI()
        self.notifications = NotificationDB()

        # State
        self.running = False

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
            - Claude CLI available
            - Git repository
            - ROADMAP.md exists
        """
        logger.info("Checking prerequisites...")

        # Check Claude CLI
        if not self.claude.check_available():
            logger.error("❌ Claude CLI not available")
            return False

        logger.info("✅ Claude CLI available")

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

        logger.info(f"🚀 Starting implementation of {priority_name}")

        # Create branch
        branch_name = f"feature/{priority_name.lower().replace(' ', '-').replace(':', '')}"
        logger.info(f"Creating branch: {branch_name}")

        if not self.git.create_branch(branch_name):
            logger.error("Failed to create branch")
            return False

        # Build prompt for Claude
        prompt = self._build_implementation_prompt(priority)

        logger.info("Executing Claude CLI with implementation prompt...")

        # Execute Claude CLI
        result = self.claude.execute_prompt(prompt, timeout=3600)  # 1 hour timeout

        if not result.success:
            logger.error(f"Claude CLI failed: {result.stderr}")
            return False

        logger.info("✅ Claude CLI execution complete")

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
        """Build Claude CLI prompt for implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string
        """
        prompt = f"""Read docs/ROADMAP.md and implement {priority['name']}: {priority['title']}.

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

        return prompt

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
