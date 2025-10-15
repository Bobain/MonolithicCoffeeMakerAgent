"""Curator suggests feedback questions to user_listener.

The curator analyzes playbook effectiveness and suggests targeted questions
to ask the user. This allows the ACE framework to gather high-signal feedback
on specific bullets that need validation or improvement.

Philosophy:
- Curator is ALLOWED to suggest feedback questions
- user_listener asks these questions to the user
- Feedback is used to update playbook bullet helpfulness scores
- Focus on bullets with low confidence or high pruned count

Example Flow:
    1. Curator analyzes playbook
    2. Finds bullet: "Always check for edge cases" (helpful: 2, pruned: 5)
    3. Suggests question: "Was edge case checking helpful in recent task?"
    4. user_listener asks user after task completion
    5. User responds: "Yes, it caught a bug!"
    6. Curator updates bullet: (helpful: 3, pruned: 5)
    7. Effectiveness improves over time
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FeedbackSuggestor:
    """Suggests feedback questions based on playbook analysis.

    The curator uses this class to identify which bullets need user feedback
    and generate targeted questions to improve playbook quality.

    Attributes:
        playbook_dir: Directory containing agent playbooks
        feedback_history_dir: Directory to store feedback responses
    """

    def __init__(
        self,
        playbook_dir: str = "docs/curator/playbooks",
        feedback_history_dir: str = "docs/curator/feedback_history",
    ):
        """Initialize feedback suggestor.

        Args:
            playbook_dir: Directory with playbook JSON files
            feedback_history_dir: Directory to store feedback responses
        """
        self.playbook_dir = Path(playbook_dir)
        self.feedback_history_dir = Path(feedback_history_dir)

        # Create directories if they don't exist
        self.playbook_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_history_dir.mkdir(parents=True, exist_ok=True)

    def get_suggested_questions(self, agent_name: str, max_questions: int = 3) -> List[Dict[str, Any]]:
        """Get feedback questions suggested by curator.

        Analyzes playbook to identify bullets that need user feedback.
        Prioritizes bullets with:
        - Low helpful count (< 3)
        - High pruned count (> helpful count)
        - Low effectiveness ratio (helpful / (helpful + pruned))

        Args:
            agent_name: Agent to get questions for
            max_questions: Maximum number of questions to return (default: 3)

        Returns:
            List of suggested questions with context

        Example:
            >>> suggestor = FeedbackSuggestor()
            >>> questions = suggestor.get_suggested_questions("user_interpret")
            >>> for q in questions:
            ...     print(f"{q['question']} (bullet: {q['bullet_id']})")
        """
        questions = []

        # Load playbook
        playbook_file = self.playbook_dir / f"{agent_name}_playbook.json"
        if not playbook_file.exists():
            logger.debug(f"No playbook found for {agent_name}")
            return questions

        try:
            with open(playbook_file, "r") as f:
                playbook = json.load(f)

            # Analyze each category for bullets needing feedback
            for category, bullets in playbook.get("categories", {}).items():
                for bullet in bullets:
                    # Skip deprecated bullets
                    if bullet.get("deprecated", False):
                        continue

                    bullet_id = bullet.get("id", "unknown")
                    bullet_text = bullet.get("text", "")
                    helpful = bullet.get("helpful_count", 0)
                    pruned = bullet.get("pruned_count", 0)

                    # Calculate effectiveness ratio
                    total = helpful + pruned
                    effectiveness = helpful / total if total > 0 else 0.0

                    # Prioritize bullets that need feedback
                    needs_feedback = (
                        helpful < 3  # Low helpful count
                        or pruned > helpful  # More pruned than helpful
                        or effectiveness < 0.5  # Low effectiveness
                    )

                    if needs_feedback:
                        # Generate question based on category
                        question = self._generate_question(agent_name, category, bullet_text)

                        questions.append(
                            {
                                "question": question,
                                "context": f"Checking effectiveness of: {bullet_text[:60]}...",
                                "bullet_id": bullet_id,
                                "category": category,
                                "current_helpful": helpful,
                                "current_pruned": pruned,
                                "effectiveness": effectiveness,
                            }
                        )

            # Sort by effectiveness (lowest first) and limit
            questions.sort(key=lambda q: q["effectiveness"])
            return questions[:max_questions]

        except Exception as e:
            logger.error(f"Failed to load playbook for {agent_name}: {e}")
            return []

    def _generate_question(self, agent_name: str, category: str, bullet_text: str) -> str:
        """Generate a targeted feedback question.

        Args:
            agent_name: Agent name
            category: Playbook category
            bullet_text: Bullet text

        Returns:
            Feedback question string
        """
        # Generate question based on category
        question_templates = {
            "intent_interpretation": "Was the intent interpretation accurate?",
            "sentiment_detection": "Was sentiment detection helpful?",
            "agent_delegation": "Was the chosen agent appropriate?",
            "implementation": "Did the implementation approach work well?",
            "testing": "Were the tests comprehensive?",
            "documentation": "Was the documentation clear?",
            "error_handling": "Did error handling work as expected?",
        }

        # Use category-specific template or generic
        base_question = question_templates.get(category, "Was this guidance helpful?")

        return f"{base_question}"

    def record_feedback(self, agent_name: str, bullet_id: str, helpful: bool, comment: str = "") -> bool:
        """Record user feedback for specific bullet.

        This updates both:
        1. Playbook bullet helpfulness counters
        2. Feedback history for future analysis

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID from playbook
            helpful: Whether user found bullet helpful
            comment: Optional user comment

        Returns:
            True if feedback recorded successfully

        Example:
            >>> suggestor = FeedbackSuggestor()
            >>> suggestor.record_feedback(
            ...     "user_interpret",
            ...     "intent_interpretation_001",
            ...     helpful=True,
            ...     comment="Caught my frustration"
            ... )
        """
        try:
            # Load current playbook
            playbook_file = self.playbook_dir / f"{agent_name}_playbook.json"
            if not playbook_file.exists():
                logger.error(f"Playbook not found: {playbook_file}")
                return False

            with open(playbook_file, "r") as f:
                playbook = json.load(f)

            # Find and update bullet
            bullet_found = False
            for category, bullets in playbook.get("categories", {}).items():
                for bullet in bullets:
                    if bullet.get("id") == bullet_id:
                        # Update counters
                        if helpful:
                            bullet["helpful_count"] = bullet.get("helpful_count", 0) + 1
                        else:
                            bullet["pruned_count"] = bullet.get("pruned_count", 0) + 1

                        bullet["last_updated"] = datetime.now().isoformat()
                        bullet_found = True
                        break
                if bullet_found:
                    break

            if not bullet_found:
                logger.warning(f"Bullet not found: {bullet_id}")
                return False

            # Write updated playbook
            with open(playbook_file, "w") as f:
                json.dump(playbook, f, indent=2)

            # Save feedback history
            self._save_feedback_history(agent_name, bullet_id, helpful, comment)

            logger.info(f"Recorded feedback: {agent_name}/{bullet_id} = {helpful}")
            return True

        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def _save_feedback_history(self, agent_name: str, bullet_id: str, helpful: bool, comment: str):
        """Save feedback to history for analysis.

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID
            helpful: Whether helpful
            comment: User comment
        """
        try:
            # Create history file if doesn't exist
            history_file = self.feedback_history_dir / f"{agent_name}_feedback_history.jsonl"

            # Append feedback entry
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "bullet_id": bullet_id,
                "helpful": helpful,
                "comment": comment,
            }

            with open(history_file, "a") as f:
                f.write(json.dumps(feedback_entry) + "\n")

            logger.debug(f"Saved feedback history: {history_file}")

        except Exception as e:
            logger.error(f"Failed to save feedback history: {e}")

    def get_feedback_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get summary of feedback received for agent.

        Args:
            agent_name: Agent name

        Returns:
            Summary with helpful/pruned counts and recent feedback

        Example:
            >>> suggestor = FeedbackSuggestor()
            >>> summary = suggestor.get_feedback_summary("user_interpret")
            >>> print(f"Total helpful: {summary['total_helpful']}")
        """
        history_file = self.feedback_history_dir / f"{agent_name}_feedback_history.jsonl"

        if not history_file.exists():
            return {
                "total_helpful": 0,
                "total_pruned": 0,
                "recent_feedback": [],
            }

        try:
            helpful_count = 0
            pruned_count = 0
            recent_feedback = []

            with open(history_file, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry["helpful"]:
                        helpful_count += 1
                    else:
                        pruned_count += 1
                    recent_feedback.append(entry)

            # Keep only last 10
            recent_feedback = recent_feedback[-10:]

            return {
                "total_helpful": helpful_count,
                "total_pruned": pruned_count,
                "recent_feedback": recent_feedback,
            }

        except Exception as e:
            logger.error(f"Failed to load feedback summary: {e}")
            return {
                "total_helpful": 0,
                "total_pruned": 0,
                "recent_feedback": [],
            }
