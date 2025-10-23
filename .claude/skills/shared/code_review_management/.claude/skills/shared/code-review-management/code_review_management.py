"""Code Review Management Skill.

Enables code-reviewer and architect to collaborate on managing code reviews,
tracking findings, and coordinating improvements.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("code-review-management")
    result = skill.execute(action="list_reviews", status="pending")
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class CodeReviewManagementSkill:
    """Code review management skill for code-reviewer and architect collaboration."""

    def __init__(self):
        """Initialize the skill."""
        self.reviews_dir = Path("docs/code-reviews")
        self.index_file = self.reviews_dir / "INDEX.md"
        self.state_file = Path("data/code-reviews/state.json")

        # Ensure directories exist
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a code review management action.

        Args:
            action: Action to perform (list_reviews, extract_action_items, etc.)
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <result>, "error": <error_message>}
        """
        try:
            if action == "list_reviews":
                return self._list_reviews(
                    status=kwargs.get("status"),
                    priority=kwargs.get("priority"),
                    limit=kwargs.get("limit", 50),
                    date_from=kwargs.get("date_from"),
                    date_to=kwargs.get("date_to"),
                )

            elif action == "get_review":
                review_id = kwargs.get("review_id")
                commit_hash = kwargs.get("commit")
                if not review_id and not commit_hash:
                    return {"result": None, "error": "Must provide review_id or commit"}
                return self._get_review(review_id=review_id, commit=commit_hash)

            elif action == "extract_action_items":
                review_path = kwargs.get("review_path")
                if not review_path:
                    return {"result": None, "error": "Missing review_path parameter"}
                return self._extract_action_items(Path(review_path))

            elif action == "update_status":
                review_id = kwargs.get("review_id")
                status = kwargs.get("status")
                if not review_id or not status:
                    return {"result": None, "error": "Missing review_id or status"}
                return self._update_status(review_id, status)

            elif action == "get_unread_reviews":
                agent = kwargs.get("agent", "architect")
                return self._get_unread_reviews(agent)

            elif action == "mark_as_read":
                review_id = kwargs.get("review_id")
                agent = kwargs.get("agent", "architect")
                if not review_id:
                    return {"result": None, "error": "Missing review_id"}
                return self._mark_as_read(review_id, agent)

            elif action == "mark_integrated":
                review_id = kwargs.get("review_id")
                spec_ref = kwargs.get("spec_ref")
                if not review_id or not spec_ref:
                    return {"result": None, "error": "Missing review_id or spec_ref"}
                return self._mark_integrated(review_id, spec_ref)

            elif action == "get_refactoring_opportunities":
                min_priority = kwargs.get("min_priority", 5)
                return self._get_refactoring_opportunities(min_priority)

            elif action == "archive_old_reviews":
                days_old = kwargs.get("days", 90)
                return self._archive_old_reviews(days_old)

            else:
                return {"result": None, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"result": None, "error": str(e)}

    def _list_reviews(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List code reviews with optional filters."""
        if not self.reviews_dir.exists():
            return {"result": {"reviews": [], "total": 0, "pending": 0, "addressed": 0, "closed": 0}, "error": None}

        reviews = []
        status_counts = {"pending": 0, "addressed": 0, "closed": 0}

        for review_file in sorted(self.reviews_dir.glob("REVIEW-*.md"), reverse=True):
            if review_file.name == "INDEX.md":
                continue

            review_data = self._parse_review_file(review_file)
            if not review_data:
                continue

            # Apply filters
            if status and review_data["status"] != status:
                continue
            if priority and review_data.get("priority") != priority:
                continue
            if date_from and review_data["date"] < date_from:
                continue
            if date_to and review_data["date"] > date_to:
                continue

            reviews.append(review_data)
            status_counts[review_data["status"]] += 1

            if len(reviews) >= limit:
                break

        return {
            "result": {
                "reviews": reviews,
                "total": len(reviews),
                "pending": status_counts["pending"],
                "addressed": status_counts["addressed"],
                "closed": status_counts["closed"],
            },
            "error": None,
        }

    def _get_review(self, review_id: Optional[str] = None, commit: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific review by ID or commit hash."""
        if review_id:
            review_file = self.reviews_dir / f"{review_id}.md"
            if not review_file.exists():
                return {"result": None, "error": f"Review {review_id} not found"}
            return {"result": self._parse_review_file(review_file), "error": None}

        # Search by commit hash
        for review_file in self.reviews_dir.glob("REVIEW-*.md"):
            if review_file.name == "INDEX.md":
                continue
            review_data = self._parse_review_file(review_file)
            if review_data and review_data.get("commit") == commit:
                return {"result": review_data, "error": None}

        return {"result": None, "error": f"Review for commit {commit} not found"}

    def _extract_action_items(self, review_path: Path) -> Dict[str, Any]:
        """Extract action items from a review file."""
        if not review_path.exists():
            return {"result": None, "error": f"Review file not found: {review_path}"}

        content = review_path.read_text()
        action_items = []
        summary = {"bugs": 0, "refactoring": 0, "optimization": 0, "security": 0, "other": 0}

        # Patterns to extract action items
        patterns = {
            "bug": r"(?:BUG|ISSUE|ERROR):\s*(.+)",
            "refactoring": r"(?:REFACTOR|REFACTORING|IMPROVE):\s*(.+)",
            "optimization": r"(?:OPTIMIZE|OPTIMIZATION|PERFORMANCE):\s*(.+)",
            "security": r"(?:SECURITY|VULNERABILITY|CVE):\s*(.+)",
            "todo": r"TODO:\s*(.+)",
            "fixme": r"FIXME:\s*(.+)",
        }

        for line_num, line in enumerate(content.splitlines(), 1):
            for item_type, pattern in patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()

                    # Extract file and line if present (format: file.py:123)
                    file_match = re.search(r"(\w+\.py):(\d+)", description)
                    file_name = file_match.group(1) if file_match else None
                    file_line = int(file_match.group(2)) if file_match else None

                    # Estimate severity (1-10)
                    severity = self._estimate_severity(item_type, description)

                    action_item = {
                        "type": item_type if item_type not in ["todo", "fixme"] else "other",
                        "severity": severity,
                        "description": description,
                        "file": file_name,
                        "line": file_line,
                        "estimated_effort": self._estimate_effort(severity),
                    }

                    action_items.append(action_item)

                    # Update summary
                    item_category = action_item["type"]
                    summary[item_category] += 1

        return {"result": {"action_items": action_items, "summary": summary}, "error": None}

    def _update_status(self, review_id: str, status: str) -> Dict[str, Any]:
        """Update the status of a review."""
        valid_statuses = ["pending", "addressed", "closed"]
        if status not in valid_statuses:
            return {"result": None, "error": f"Invalid status. Must be one of: {valid_statuses}"}

        review_file = self.reviews_dir / f"{review_id}.md"
        if not review_file.exists():
            return {"result": None, "error": f"Review {review_id} not found"}

        content = review_file.read_text()

        # Update status in frontmatter
        updated_content = re.sub(
            r"(status:\s*)(pending|addressed|closed)", f"\\g<1>{status}", content, flags=re.IGNORECASE
        )

        # Add status change log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_log = f"\n\n**Status Updated**: {status} ({timestamp})\n"
        updated_content += status_log

        review_file.write_text(updated_content)

        return {"result": {"review_id": review_id, "new_status": status, "updated_at": timestamp}, "error": None}

    def _get_unread_reviews(self, agent: str) -> Dict[str, Any]:
        """Get reviews that haven't been read by the specified agent."""
        # Load state
        state = self._load_state()
        agent_state = state.get(agent, {"last_read": {}, "integrated": []})
        last_read_map = agent_state.get("last_read", {})

        unread = []
        for review_file in sorted(self.reviews_dir.glob("REVIEW-*.md"), reverse=True):
            if review_file.name == "INDEX.md":
                continue

            review_data = self._parse_review_file(review_file)
            if not review_data:
                continue

            review_id = review_data["id"]
            review_date = review_data["date"]

            # Check if read
            last_read = last_read_map.get(review_id)
            if not last_read or review_date > last_read:
                unread.append(review_data)

        return {"result": {"unread": unread, "count": len(unread)}, "error": None}

    def _mark_as_read(self, review_id: str, agent: str) -> Dict[str, Any]:
        """Mark a review as read by an agent."""
        state = self._load_state()

        if agent not in state:
            state[agent] = {"last_read": {}, "integrated": []}

        state[agent]["last_read"][review_id] = datetime.now().strftime("%Y-%m-%d")

        self._save_state(state)

        return {
            "result": {"review_id": review_id, "agent": agent, "marked_at": state[agent]["last_read"][review_id]},
            "error": None,
        }

    def _mark_integrated(self, review_id: str, spec_ref: str) -> Dict[str, Any]:
        """Mark a review as integrated into a spec."""
        state = self._load_state()

        if "integrations" not in state:
            state["integrations"] = []

        integration = {
            "review_id": review_id,
            "spec_ref": spec_ref,
            "integrated_at": datetime.now().strftime("%Y-%m-%d"),
        }

        state["integrations"].append(integration)

        self._save_state(state)

        return {"result": integration, "error": None}

    def _get_refactoring_opportunities(self, min_priority: int) -> Dict[str, Any]:
        """Identify refactoring opportunities from reviews."""
        opportunities = []
        pattern_counts = {}

        for review_file in self.reviews_dir.glob("REVIEW-*.md"):
            if review_file.name == "INDEX.md":
                continue

            content = review_file.read_text()

            # Look for refactoring patterns
            refactoring_patterns = [
                (r"duplicat(?:e|ed|ion)", "Duplicated code"),
                (r"complexity", "High complexity"),
                (r"(?:extract|move|split)\s+(?:method|function|class)", "Method extraction"),
                (r"(?:long|large)\s+(?:method|function|class)", "Long method/class"),
                (r"(?:tight|high)\s+coupling", "Tight coupling"),
            ]

            for pattern, description in refactoring_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    if description not in pattern_counts:
                        pattern_counts[description] = {"count": 0, "files": set()}
                    pattern_counts[description]["count"] += len(matches)
                    pattern_counts[description]["files"].add(review_file.name)

        # Convert to opportunities list
        for pattern, data in pattern_counts.items():
            priority = min(10, data["count"] * 2)  # Priority based on occurrences
            if priority >= min_priority:
                opportunities.append(
                    {
                        "pattern": pattern,
                        "occurrences": data["count"],
                        "reviews": sorted(list(data["files"])),
                        "priority": priority,
                        "recommended_action": self._get_recommended_action(pattern),
                    }
                )

        # Sort by priority
        opportunities.sort(key=lambda x: x["priority"], reverse=True)

        return {"result": {"opportunities": opportunities, "total": len(opportunities)}, "error": None}

    def _archive_old_reviews(self, days: int) -> Dict[str, Any]:
        """Archive reviews older than specified days."""
        archive_dir = self.reviews_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        archived = []

        for review_file in self.reviews_dir.glob("REVIEW-*.md"):
            if review_file.name == "INDEX.md":
                continue

            review_data = self._parse_review_file(review_file)
            if review_data and review_data["date"] < cutoff_date and review_data["status"] == "closed":
                # Move to archive
                archive_path = archive_dir / review_file.name
                review_file.rename(archive_path)
                archived.append(review_data["id"])

        return {"result": {"archived": archived, "count": len(archived)}, "error": None}

    # Helper methods
    def _parse_review_file(self, review_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a review file and extract metadata."""
        try:
            content = review_file.read_text()

            # Extract metadata from frontmatter or content
            review_id = review_file.stem
            date_match = re.search(r"REVIEW-(\d{4}-\d{2}-\d{2})", review_id)
            date = date_match.group(1) if date_match else "unknown"

            commit_match = re.search(r"Commit:\s*`?([a-f0-9]+)`?", content, re.IGNORECASE)
            commit = commit_match.group(1) if commit_match else None

            status_match = re.search(r"Status:\s*(\w+)", content, re.IGNORECASE)
            status = status_match.group(1).lower() if status_match else "pending"

            priority_match = re.search(r"Priority:\s*([\w-]+)", content, re.IGNORECASE)
            priority = priority_match.group(1) if priority_match else None

            # Count findings
            findings_count = len(
                re.findall(r"^#+\s+(?:Issue|Finding|Bug|Problem)", content, re.MULTILINE | re.IGNORECASE)
            )

            return {
                "id": review_id,
                "date": date,
                "commit": commit,
                "status": status,
                "priority": priority,
                "findings_count": findings_count,
                "path": str(review_file),
            }
        except Exception:
            return None

    def _estimate_severity(self, item_type: str, description: str) -> int:
        """Estimate severity of an action item (1-10)."""
        severity_keywords = {
            10: ["critical", "severe", "security vulnerability", "data loss"],
            8: ["major", "important", "memory leak", "performance"],
            6: ["moderate", "should", "refactor"],
            4: ["minor", "nice to have", "cleanup"],
            2: ["trivial", "cosmetic", "formatting"],
        }

        description_lower = description.lower()

        for severity, keywords in severity_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return severity

        # Default severities by type
        defaults = {"bug": 8, "security": 10, "refactoring": 5, "optimization": 6, "other": 4}

        return defaults.get(item_type, 5)

    def _estimate_effort(self, severity: int) -> str:
        """Estimate effort based on severity."""
        if severity >= 8:
            return "8h+"
        elif severity >= 6:
            return "4-8h"
        elif severity >= 4:
            return "2-4h"
        else:
            return "<2h"

    def _get_recommended_action(self, pattern: str) -> str:
        """Get recommended action for a refactoring pattern."""
        actions = {
            "Duplicated code": "Extract common logic into shared utility or mixin",
            "High complexity": "Break down into smaller, focused functions",
            "Method extraction": "Extract large methods into separate functions",
            "Long method/class": "Split into smaller, single-responsibility components",
            "Tight coupling": "Introduce interfaces or dependency injection",
        }
        return actions.get(pattern, "Review and refactor as needed")

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if not self.state_file.exists():
            return {}

        import json

        try:
            return json.loads(self.state_file.read_text())
        except Exception:
            return {}

    def _save_state(self, state: Dict[str, Any]):
        """Save state to file."""
        import json

        self.state_file.write_text(json.dumps(state, indent=2))


# Skill entry point
def run(action: str, **kwargs) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        action: Action to perform
        **kwargs: Action-specific parameters

    Returns:
        dict: {"result": <result>, "error": <error_message>}
    """
    skill = CodeReviewManagementSkill()
    return skill.execute(action, **kwargs)
