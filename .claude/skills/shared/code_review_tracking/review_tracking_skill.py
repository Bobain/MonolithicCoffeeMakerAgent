"""Code Review Tracking Skill - Shared by code_developer and code_reviewer.

This skill manages the code review workflow:
1. code_developer links commits to technical specs and requests review
2. code_reviewer finds pending reviews with associated specs
3. code_reviewer marks reviews as complete

Database Table: commit_reviews
- Links commits to technical specifications
- Tracks review status and feedback
- Maintains audit trail

Access Control:
- code_developer: Can create review requests, update own commits
- code_reviewer: Can update review status, add feedback
- All agents: Can read review status

Integration:
- Links to technical_specs table for spec context
- Enables spec-based code reviews
- Tracks which commits implement which specs

Example Usage:

For code_developer:
    >>> review_skill = CodeReviewTrackingSkill(agent_name="code_developer")
    >>> # After making commits for a spec
    >>> review_skill.request_review(
    ...     commit_sha="abc123",
    ...     spec_id="SPEC-115",
    ...     description="Implemented API endpoints",
    ...     files_changed=["api/endpoints.py", "api/models.py"]
    ... )

For code_reviewer:
    >>> review_skill = CodeReviewTrackingSkill(agent_name="code_reviewer")
    >>> # Find commits needing review
    >>> pending = review_skill.get_pending_reviews()
    >>> for review in pending:
    ...     spec = review_skill.get_spec_for_review(review['id'])
    ...     # Read spec to understand context
    ...     # Perform review
    ...     review_skill.complete_review(review['id'], status='approved', feedback='...')
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeReviewTrackingSkill:
    """Unified skill for code review tracking between code_developer and code_reviewer.

    Manages the review workflow with spec integration for context-aware reviews.
    """

    def __init__(self, agent_name: str = "unknown"):
        """Initialize code review tracking skill.

        Args:
            agent_name: Name of agent using skill (for access control)
        """
        self.agent_name = agent_name
        self.can_request_review = agent_name == "code_developer"
        self.can_perform_review = agent_name == "code_reviewer"

        # Use unified database for integration with specs
        self.db_path = Path("data/unified_roadmap_specs.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_review_tables()

        logger.info(f"CodeReviewTrackingSkill initialized for {agent_name}")

    def _init_review_tables(self) -> None:
        """Initialize commit review tracking tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")

            # Commit reviews table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS commit_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_sha TEXT NOT NULL,               -- Git commit SHA
                    spec_id TEXT,                          -- Links to technical_specs.id
                    branch TEXT NOT NULL DEFAULT 'roadmap', -- Git branch
                    description TEXT,                      -- What was implemented
                    files_changed TEXT,                    -- JSON array of file paths
                    requested_by TEXT NOT NULL,            -- code_developer
                    requested_at TEXT NOT NULL,            -- When review requested
                    review_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'approved', 'changes_requested'
                    reviewer TEXT,                         -- code_reviewer who took it
                    claimed_at TEXT,                       -- When review was claimed (for timeout)
                    reviewed_at TEXT,                      -- When review completed
                    review_feedback TEXT,                  -- Feedback from reviewer
                    related_pr TEXT,                       -- Optional PR link
                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                )
            """
            )

            # Review comments table (for detailed feedback)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS review_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,              -- Which file
                    line_number INTEGER,                  -- Line number (if specific)
                    comment_type TEXT,                    -- 'issue', 'suggestion', 'praise'
                    comment TEXT NOT NULL,                -- The feedback
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE
                )
            """
            )

            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_status ON commit_reviews(review_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_spec ON commit_reviews(spec_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_sha ON commit_reviews(commit_sha)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_review ON review_comments(review_id)")

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing review tables: {e}")
            raise

    # ==================== CODE_DEVELOPER METHODS ====================

    def request_review(
        self,
        commit_sha: str,
        spec_id: str,
        description: str,
        files_changed: List[str],
        branch: str = "roadmap",
        related_pr: Optional[str] = None,
    ) -> int:
        """Request code review for a commit (code_developer only).

        Links the commit to a technical spec so reviewer knows the context.

        Args:
            commit_sha: Git commit SHA
            spec_id: Technical spec this commit implements
            description: What was implemented in this commit
            files_changed: List of files modified
            branch: Git branch (default: roadmap)
            related_pr: Optional PR URL if created

        Returns:
            Review request ID

        Raises:
            PermissionError: If not code_developer
        """
        if not self.can_request_review:
            raise PermissionError(f"Only code_developer can request reviews, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO commit_reviews (
                    commit_sha, spec_id, branch, description, files_changed,
                    requested_by, requested_at, review_status, related_pr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    commit_sha,
                    spec_id,
                    branch,
                    description,
                    json.dumps(files_changed),
                    self.agent_name,
                    datetime.now().isoformat(),
                    "pending",
                    related_pr,
                ),
            )

            review_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"✅ Review requested for {commit_sha} implementing {spec_id}")
            self._notify_code_reviewer(review_id, spec_id, description)

            return review_id

        except sqlite3.Error as e:
            logger.error(f"Error requesting review: {e}")
            raise

    def get_my_reviews(self) -> List[Dict]:
        """Get review requests created by current agent (code_developer).

        Returns:
            List of review requests with status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM commit_reviews
                WHERE requested_by = ?
                ORDER BY requested_at DESC
            """,
                (self.agent_name,),
            )

            rows = cursor.fetchall()
            conn.close()

            reviews = []
            for row in rows:
                review = dict(row)
                if review.get("files_changed"):
                    review["files_changed"] = json.loads(review["files_changed"])
                reviews.append(review)

            return reviews

        except sqlite3.Error as e:
            logger.error(f"Error getting my reviews: {e}")
            return []

    # ==================== CODE_REVIEWER METHODS ====================

    def get_pending_reviews(self) -> List[Dict]:
        """Get commits awaiting review (code_reviewer only).

        Returns commits with linked specs for context.

        Returns:
            List of pending review requests with spec info
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # JOIN with technical_specs to get spec context
            cursor.execute(
                """
                SELECT
                    cr.*,
                    ts.title as spec_title,
                    ts.spec_type,
                    ts.estimated_hours
                FROM commit_reviews cr
                LEFT JOIN technical_specs ts ON cr.spec_id = ts.id
                WHERE cr.review_status = 'pending'
                ORDER BY cr.requested_at ASC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            reviews = []
            for row in rows:
                review = dict(row)
                if review.get("files_changed"):
                    review["files_changed"] = json.loads(review["files_changed"])
                reviews.append(review)

            return reviews

        except sqlite3.Error as e:
            logger.error(f"Error getting pending reviews: {e}")
            return []

    def claim_review(self, review_id: int) -> bool:
        """Claim a review for processing (code_reviewer only).

        Marks the review as 'in_progress' and sets claimed_at timestamp.
        Reviews in_progress for >24 hours will be automatically reset to pending.

        Args:
            review_id: ID of review to claim

        Returns:
            True if successfully claimed

        Raises:
            PermissionError: If not code_reviewer
        """
        if not self.can_perform_review:
            raise PermissionError(f"Only code_reviewer can claim reviews, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Set review to in_progress with claimed timestamp
            cursor.execute(
                """
                UPDATE commit_reviews
                SET review_status = 'in_progress',
                    reviewer = ?,
                    claimed_at = ?
                WHERE id = ? AND review_status = 'pending'
            """,
                (self.agent_name, datetime.now().isoformat(), review_id),
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.info(f"📋 Claimed review #{review_id} - marked as in_progress")
            else:
                logger.warning(f"Could not claim review #{review_id} - may already be in_progress")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error claiming review: {e}")
            return False

    def get_spec_for_review(self, review_id: int) -> Optional[Dict]:
        """Get the technical spec associated with a review.

        This allows code_reviewer to understand what was supposed to be implemented.

        Args:
            review_id: Review ID

        Returns:
            Spec details including content, or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get spec_id from review
            cursor.execute(
                """
                SELECT spec_id FROM commit_reviews WHERE id = ?
            """,
                (review_id,),
            )

            result = cursor.fetchone()
            if not result or not result["spec_id"]:
                conn.close()
                return None

            spec_id = result["spec_id"]

            # Get full spec details
            cursor.execute(
                """
                SELECT * FROM technical_specs WHERE id = ?
            """,
                (spec_id,),
            )

            spec_row = cursor.fetchone()
            conn.close()

            if spec_row:
                spec = dict(spec_row)
                # Parse JSON fields
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                return spec

            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting spec for review: {e}")
            return None

    def add_review_comment(
        self,
        review_id: int,
        file_path: str,
        comment: str,
        comment_type: str = "suggestion",
        line_number: Optional[int] = None,
    ) -> bool:
        """Add a comment to a code review (code_reviewer only).

        Args:
            review_id: Review ID
            file_path: File the comment applies to
            comment: The feedback
            comment_type: 'issue', 'suggestion', or 'praise'
            line_number: Optional specific line number

        Returns:
            True if successful

        Raises:
            PermissionError: If not code_reviewer
        """
        if not self.can_perform_review:
            raise PermissionError(f"Only code_reviewer can add comments, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO review_comments (
                    review_id, file_path, line_number, comment_type,
                    comment, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (review_id, file_path, line_number, comment_type, comment, self.agent_name, datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()

            logger.info(f"💬 Added {comment_type} comment to review #{review_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error adding comment: {e}")
            return False

    def complete_review(self, review_id: int, status: str, feedback: str) -> bool:
        """Complete a code review (code_reviewer only).

        Args:
            review_id: Review ID
            status: 'approved' or 'changes_requested'
            feedback: Overall review feedback

        Returns:
            True if successful

        Raises:
            PermissionError: If not code_reviewer
        """
        if not self.can_perform_review:
            raise PermissionError(f"Only code_reviewer can complete reviews, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE commit_reviews
                SET review_status = ?, review_feedback = ?, reviewed_at = ?
                WHERE id = ? AND reviewer = ?
            """,
                (status, feedback, datetime.now().isoformat(), review_id, self.agent_name),
            )

            success = cursor.rowcount > 0
            conn.commit()

            if success:
                # Get review details for notification
                cursor.execute("SELECT * FROM commit_reviews WHERE id = ?", (review_id,))
                review = dict(cursor.fetchone())
                self._notify_developer_review_complete(review, status, feedback)

            conn.close()

            if success:
                logger.info(f"✅ Review #{review_id} marked as {status}")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error completing review: {e}")
            return False

    # ==================== SHARED METHODS ====================

    def reset_stale_reviews(self) -> int:
        """Reset reviews that have been in_progress for >24 hours back to pending.

        This is a recurring maintenance task that should be run periodically
        to handle interrupted reviews. Reviews stuck in 'in_progress' for more
        than 24 hours are reset to 'pending' so another reviewer can claim them.

        Can be called by any agent, but typically run by code_reviewer or orchestrator.

        Returns:
            Number of reviews reset
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate 24 hours ago
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()

            # Find stale reviews before updating (for logging)
            cursor.execute(
                """
                SELECT id, commit_sha, reviewer
                FROM commit_reviews
                WHERE review_status = 'in_progress'
                AND claimed_at < ?
            """,
                (cutoff_time,),
            )

            stale_reviews = cursor.fetchall()

            # Reset stale in_progress reviews back to pending
            cursor.execute(
                """
                UPDATE commit_reviews
                SET review_status = 'pending',
                    reviewer = NULL,
                    claimed_at = NULL
                WHERE review_status = 'in_progress'
                AND claimed_at < ?
            """,
                (cutoff_time,),
            )

            reset_count = cursor.rowcount
            conn.commit()
            conn.close()

            if reset_count > 0:
                logger.info(f"🔄 Reset {reset_count} stale reviews back to pending")
                for review in stale_reviews:
                    logger.info(f"  - Review #{review[0]} (commit {review[1][:8]}) was abandoned by {review[2]}")

            return reset_count

        except sqlite3.Error as e:
            logger.error(f"Error resetting stale reviews: {e}")
            return 0

    def get_review_status(self, commit_sha: str) -> Optional[Dict]:
        """Get review status for a commit (all agents).

        Args:
            commit_sha: Git commit SHA

        Returns:
            Review details or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM commit_reviews
                WHERE commit_sha = ?
            """,
                (commit_sha,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                review = dict(row)
                if review.get("files_changed"):
                    review["files_changed"] = json.loads(review["files_changed"])
                return review

            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting review status: {e}")
            return None

    def get_reviews_for_spec(self, spec_id: str) -> List[Dict]:
        """Get all reviews for a specific spec (all agents).

        Args:
            spec_id: Technical spec ID

        Returns:
            List of reviews for this spec
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM commit_reviews
                WHERE spec_id = ?
                ORDER BY requested_at DESC
            """,
                (spec_id,),
            )

            rows = cursor.fetchall()
            conn.close()

            reviews = []
            for row in rows:
                review = dict(row)
                if review.get("files_changed"):
                    review["files_changed"] = json.loads(review["files_changed"])
                reviews.append(review)

            return reviews

        except sqlite3.Error as e:
            logger.error(f"Error getting spec reviews: {e}")
            return []

    # ==================== PRIVATE NOTIFICATION METHODS ====================

    def _notify_code_reviewer(self, review_id: int, spec_id: str, description: str) -> None:
        """Notify code_reviewer about new review request."""
        try:
            from coffee_maker.autonomous.unified_database import get_unified_database

            db = get_unified_database()
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()

            message = (
                f"NEW CODE REVIEW REQUEST\n"
                f"- Review ID: #{review_id}\n"
                f"- Spec: {spec_id}\n"
                f"- Description: {description}\n"
                f"\nUse review_skill.claim_review({review_id}) to start"
            )

            cursor.execute(
                """
                INSERT INTO notifications (
                    target_agent, source_agent, notification_type,
                    item_id, message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    "code_reviewer",
                    "code_developer",
                    "review_request",
                    str(review_id),
                    message,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"📬 Notified code_reviewer about review #{review_id}")

        except Exception as e:
            logger.warning(f"Could not notify code_reviewer: {e}")

    def _notify_developer_review_complete(self, review: Dict, status: str, feedback: str) -> None:
        """Notify code_developer that review is complete."""
        try:
            from coffee_maker.autonomous.unified_database import get_unified_database

            db = get_unified_database()
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()

            message = (
                f"CODE REVIEW COMPLETE\n"
                f"- Commit: {review['commit_sha'][:8]}\n"
                f"- Status: {status.upper()}\n"
                f"- Feedback: {feedback}\n"
            )

            cursor.execute(
                """
                INSERT INTO notifications (
                    target_agent, source_agent, notification_type,
                    item_id, message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    review["requested_by"],
                    "code_reviewer",
                    "review_complete",
                    str(review["id"]),
                    message,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"📬 Notified {review['requested_by']} about review completion")

        except Exception as e:
            logger.warning(f"Could not notify developer: {e}")


# ==================== SKILL FACTORY ====================


def get_code_review_skill(agent_name: str) -> CodeReviewTrackingSkill:
    """Factory function to get code review tracking skill.

    Args:
        agent_name: Name of agent requesting skill

    Returns:
        CodeReviewTrackingSkill instance with appropriate permissions
    """
    return CodeReviewTrackingSkill(agent_name)


# ==================== USAGE DOCUMENTATION ====================

CODE_REVIEW_SKILL_USAGE = """
## Code Review Tracking Skill Usage

### For code_developer (Requesting Reviews):
```python
import sys
sys.path.insert(0, '.claude/skills/shared/code_review_tracking')
from review_tracking_skill import CodeReviewTrackingSkill

# Initialize skill
review_skill = CodeReviewTrackingSkill(agent_name="code_developer")

# After committing code for a spec
review_id = review_skill.request_review(
    commit_sha="abc123def456",
    spec_id="SPEC-115",  # Links to technical spec
    description="Implemented database schema and API endpoints",
    files_changed=[
        "coffee_maker/models/database.py",
        "coffee_maker/api/endpoints.py",
        "tests/test_api.py"
    ],
    branch="roadmap"
)

print(f"Review requested: #{review_id}")

# Check status of your reviews
my_reviews = review_skill.get_my_reviews()
for review in my_reviews:
    print(f"Review #{review['id']}: {review['review_status']}")
```

### For code_reviewer (Performing Reviews):
```python
# Initialize skill
review_skill = CodeReviewTrackingSkill(agent_name="code_reviewer")

# Find pending reviews
pending = review_skill.get_pending_reviews()
for review in pending:
    print(f"Review #{review['id']} for {review['spec_id']}")
    print(f"  Spec: {review['spec_title']}")
    print(f"  Files: {', '.join(review['files_changed'])}")

# Claim a review
review_id = pending[0]['id']
review_skill.claim_review(review_id)

# Get the spec to understand context
spec = review_skill.get_spec_for_review(review_id)
if spec:
    # Read spec to understand what should have been implemented
    print(f"Reviewing against spec: {spec['title']}")

# Add comments during review
review_skill.add_review_comment(
    review_id=review_id,
    file_path="coffee_maker/api/endpoints.py",
    comment="Consider adding error handling for null inputs",
    comment_type="suggestion",
    line_number=42
)

# Complete the review
review_skill.complete_review(
    review_id=review_id,
    status="approved",  # or "changes_requested"
    feedback="Well implemented, follows spec correctly. Minor suggestions added."
)
```

### Review Workflow:
1. code_developer implements spec and commits
2. code_developer requests review, linking to spec
3. code_reviewer gets notified
4. code_reviewer reads spec to understand requirements
5. code_reviewer reviews code against spec
6. code_reviewer provides feedback and status
7. code_developer gets notified of results

### Key Benefits:
- Spec-aware reviews (reviewer knows the requirements)
- Traceable commits to specs
- Clear review workflow
- Notification system for updates
- Audit trail of all reviews
"""
