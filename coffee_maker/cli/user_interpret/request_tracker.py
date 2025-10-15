"""Track user requests (features, bugs, etc.) for proactive updates."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RequestTracker:
    """Track pending user requests and their status.

    This tracker maintains:
    - Feature requests
    - Bug reports
    - Documentation requests
    - Questions and their answers

    It enables proactive notifications when work is completed.

    Example:
        tracker = RequestTracker()
        request_id = tracker.add_request(
            request_type="feature",
            description="Login feature",
            user_message="add a login feature",
            delegated_to="code_developer"
        )
        tracker.mark_completed(request_id, result_location="/docs/login_tutorial.md")
    """

    def __init__(self, docs_dir: str = "docs/user_interpret"):
        """Initialize request tracker.

        Args:
            docs_dir: Directory for storing request data
        """
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.requests_file = self.docs_dir / "user_requests.json"
        self._load_requests()

    def _load_requests(self):
        """Load requests from file."""
        if self.requests_file.exists():
            with open(self.requests_file, "r") as f:
                self.requests = json.load(f)
        else:
            self.requests = {
                "feature_requests": [],
                "bug_reports": [],
                "documentation_requests": [],
                "questions": [],
            }

    def _save_requests(self):
        """Save requests to file."""
        with open(self.requests_file, "w") as f:
            json.dump(self.requests, f, indent=2)

    def add_request(
        self, request_type: str, description: str, user_message: str, delegated_to: str
    ) -> str:
        """Add new request.

        Args:
            request_type: "feature", "bug", "documentation", "question"
            description: Short description
            user_message: Original user message
            delegated_to: Agent handling the request

        Returns:
            Request ID
        """
        request_id = f"{request_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        request = {
            "id": request_id,
            "type": request_type,
            "description": description,
            "user_message": user_message,
            "delegated_to": delegated_to,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
        }

        # Add to appropriate list
        key = f"{request_type}_requests"
        if key not in self.requests:
            key = "questions"  # Fallback

        self.requests[key].append(request)
        self._save_requests()

        logger.info(f"Added request: {request_id}")
        return request_id

    def mark_completed(self, request_id: str, result_location: Optional[str] = None):
        """Mark request as completed.

        Args:
            request_id: Request ID
            result_location: Optional path to result (docs, tutorial, etc.)
        """
        for category in self.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["id"] == request_id:
                        req["status"] = "completed"
                        req["completed_at"] = datetime.now().isoformat()
                        req["updated_at"] = datetime.now().isoformat()
                        if result_location:
                            req["result_location"] = result_location
                        self._save_requests()
                        logger.info(f"Marked completed: {request_id}")
                        return

        logger.warning(f"Request not found: {request_id}")

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending requests.

        Returns:
            List of pending requests
        """
        pending = []
        for category in self.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["status"] == "pending":
                        pending.append(req)
        return pending

    def get_recently_completed(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recently completed requests.

        Args:
            hours: Hours to look back

        Returns:
            List of completed requests, sorted by completion time
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        completed = []

        for category in self.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["status"] == "completed" and req["completed_at"]:
                        completed_at = datetime.fromisoformat(req["completed_at"])
                        if completed_at > cutoff:
                            completed.append(req)

        return sorted(completed, key=lambda x: x["completed_at"], reverse=True)

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get specific request by ID.

        Args:
            request_id: Request ID

        Returns:
            Request dict or None if not found
        """
        for category in self.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["id"] == request_id:
                        return req
        return None

    def update_status(self, request_id: str, status: str, notes: Optional[str] = None):
        """Update request status.

        Args:
            request_id: Request ID
            status: New status (pending, in_progress, completed, blocked)
            notes: Optional status notes
        """
        for category in self.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["id"] == request_id:
                        req["status"] = status
                        req["updated_at"] = datetime.now().isoformat()
                        if notes:
                            if "notes" not in req:
                                req["notes"] = []
                            req["notes"].append(
                                {"timestamp": datetime.now().isoformat(), "text": notes}
                            )
                        self._save_requests()
                        logger.info(f"Updated status for {request_id}: {status}")
                        return

        logger.warning(f"Request not found: {request_id}")
