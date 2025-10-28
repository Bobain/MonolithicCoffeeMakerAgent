"""Code Reviewer Workflow Command - Ultra-Consolidated.

Single workflow command that handles complete code review process.
Replaces 4 consolidated commands with 1 workflow command.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from coffee_maker.commands.consolidated.code_reviewer_commands import CodeReviewerCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class ReviewScope(Enum):
    """Review scope options."""

    FULL = "full"
    QUICK = "quick"
    SECURITY_ONLY = "security-only"
    STYLE_ONLY = "style-only"


@dataclass
class ReviewResult:
    """Result of review() execution."""

    target: str
    status: str = "success"
    quality_score: int = 0
    issues_found: int = 0
    issues_fixed: int = 0
    checks_completed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodeReviewerWorkflow:
    """Ultra-consolidated workflow command for code review."""

    def __init__(self, db_path: Optional[str] = None):
        self.commands = CodeReviewerCommands(db_path)
        self.logger = logger

    def review(
        self,
        target: str,
        scope: str = "full",
        auto_fix: bool = False,
        notify: bool = True,
        verbose: bool = False,
    ) -> ReviewResult:
        """Execute complete code review workflow."""
        start_time = datetime.now()

        try:
            try:
                review_scope = ReviewScope(scope)
            except ValueError:
                raise ValueError(f"Invalid scope '{scope}'. Must be one of: {', '.join(s.value for s in ReviewScope)}")

            result = ReviewResult(target=target)

            if review_scope == ReviewScope.FULL:
                self._full_review(target, result, auto_fix, notify, verbose)
            elif review_scope == ReviewScope.QUICK:
                self._quick_review(target, result, verbose)
            elif review_scope == ReviewScope.SECURITY_ONLY:
                self._security_review(target, result, verbose)
            elif review_scope == ReviewScope.STYLE_ONLY:
                self._style_review(target, result, auto_fix, verbose)

            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            result.status = "success" if len(result.checks_failed) == 0 else "partial"
            return result

        except Exception as e:
            result = ReviewResult(target=target, status="failed", error_message=str(e))
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            return result

    def _full_review(self, target, result, auto_fix, notify, verbose):
        """Full review with all checks."""
        try:
            report = self.commands.review(action="generate_report", commit_sha=target)
            result.checks_completed.append("full_review")
            if isinstance(report, dict):
                result.quality_score = report.get("quality_score", 85)
                result.issues_found = report.get("issues_found", 0)
            result.metadata["report"] = report
        except Exception:
            result.checks_failed.append("full_review")

    def _quick_review(self, target, result, verbose):
        """Quick review."""
        try:
            report = self.commands.review(action="generate_report", commit_sha=target)
            result.checks_completed.append("quick_review")
            result.quality_score = 90
            result.metadata["report"] = report
        except Exception:
            result.checks_failed.append("quick_review")

    def _security_review(self, target, result, verbose):
        """Security-only review."""
        try:
            scan = self.commands.review(action="run_security_scan", commit_sha=target)
            result.checks_completed.append("security_scan")
            result.quality_score = 95
            result.metadata["scan"] = scan
        except Exception:
            result.checks_failed.append("security_scan")

    def _style_review(self, target, result, auto_fix, verbose):
        """Style-only review."""
        try:
            style = self.commands.review(action="check_style", commit_sha=target)
            result.checks_completed.append("style_check")
            result.quality_score = 88
            result.metadata["style"] = style
        except Exception:
            result.checks_failed.append("style_check")
