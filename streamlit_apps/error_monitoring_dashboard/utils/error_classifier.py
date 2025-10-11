"""Error classification logic for categorizing and analyzing errors.

This module provides error categorization based on error messages from Langfuse traces.
It classifies errors by type, severity, category, and provides actionable recommendations.

Example:
    >>> from error_classifier import ErrorClassifier
    >>> error = ErrorClassifier.classify("RateLimitError: Rate limit exceeded for model gpt-4")
    >>> print(error['severity'])
    'HIGH'
"""

from typing import Dict, List, Optional
import re


class ErrorClassifier:
    """Categorizes errors from Langfuse traces.

    This classifier analyzes error messages and categorizes them by:
    - Error type (RateLimitError, ContextLengthExceededError, etc.)
    - Severity (CRITICAL, HIGH, MEDIUM, LOW)
    - Category (API Limits, Network, Input Validation, etc.)
    - Actionable recommendations
    """

    ERROR_CATEGORIES = {
        "RateLimitError": {
            "severity": "HIGH",
            "category": "API Limits",
            "actionable": "Implement rate limiting or exponential backoff strategy",
            "keywords": ["rate limit", "ratelimit", "too many requests", "429"],
        },
        "ContextLengthExceededError": {
            "severity": "MEDIUM",
            "category": "Input Validation",
            "actionable": "Reduce prompt size or use truncation strategy",
            "keywords": ["context length", "maximum context", "token limit", "context window"],
        },
        "APIConnectionError": {
            "severity": "CRITICAL",
            "category": "Network",
            "actionable": "Check network connectivity and API status",
            "keywords": ["connection error", "connection failed", "network error", "timeout"],
        },
        "InvalidRequestError": {
            "severity": "MEDIUM",
            "category": "Request Validation",
            "actionable": "Validate request parameters before sending",
            "keywords": ["invalid request", "invalid parameter", "bad request", "400"],
        },
        "TimeoutError": {
            "severity": "HIGH",
            "category": "Performance",
            "actionable": "Increase timeout or optimize prompt complexity",
            "keywords": ["timeout", "timed out", "request timeout", "deadline exceeded"],
        },
        "AuthenticationError": {
            "severity": "CRITICAL",
            "category": "Authentication",
            "actionable": "Check API keys and authentication credentials",
            "keywords": ["authentication", "unauthorized", "401", "invalid api key", "api key"],
        },
        "PermissionError": {
            "severity": "HIGH",
            "category": "Authorization",
            "actionable": "Verify API permissions and access rights",
            "keywords": ["permission denied", "forbidden", "403", "access denied"],
        },
        "ModelNotFoundError": {
            "severity": "HIGH",
            "category": "Configuration",
            "actionable": "Verify model name and availability",
            "keywords": ["model not found", "unknown model", "invalid model", "404"],
        },
        "ServiceUnavailableError": {
            "severity": "CRITICAL",
            "category": "Service",
            "actionable": "Wait for service recovery or use fallback model",
            "keywords": ["service unavailable", "503", "server error", "500", "internal server"],
        },
        "ContentFilterError": {
            "severity": "MEDIUM",
            "category": "Content Policy",
            "actionable": "Review and modify prompt content to comply with policies",
            "keywords": ["content filter", "content policy", "filtered", "safety"],
        },
    }

    # Severity order for sorting (highest to lowest)
    SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}

    @staticmethod
    def classify(error_message: str) -> Dict[str, str]:
        """Extract error type and severity from error message.

        Args:
            error_message: Error message from trace

        Returns:
            Dictionary with type, severity, category, and recommendation

        Example:
            >>> error = ErrorClassifier.classify("RateLimitError: Too many requests")
            >>> print(error['type'])
            'RateLimitError'
        """
        if not error_message:
            return {
                "type": "UnknownError",
                "severity": "UNKNOWN",
                "category": "Other",
                "recommendation": "No error message provided",
            }

        error_message_lower = error_message.lower()

        # Check each error category
        for error_type, metadata in ErrorClassifier.ERROR_CATEGORIES.items():
            # Check if error type is in message
            if error_type.lower() in error_message_lower:
                return {
                    "type": error_type,
                    "severity": metadata["severity"],
                    "category": metadata["category"],
                    "recommendation": metadata["actionable"],
                }

            # Check keywords
            for keyword in metadata["keywords"]:
                if keyword.lower() in error_message_lower:
                    return {
                        "type": error_type,
                        "severity": metadata["severity"],
                        "category": metadata["category"],
                        "recommendation": metadata["actionable"],
                    }

        # No match found
        return {
            "type": "UnknownError",
            "severity": "MEDIUM",
            "category": "Other",
            "recommendation": "Manual investigation required",
        }

    @staticmethod
    def classify_batch(error_messages: List[str]) -> List[Dict[str, str]]:
        """Classify a batch of error messages.

        Args:
            error_messages: List of error messages

        Returns:
            List of classification dictionaries

        Example:
            >>> errors = ["RateLimitError", "TimeoutError"]
            >>> results = ErrorClassifier.classify_batch(errors)
        """
        return [ErrorClassifier.classify(msg) for msg in error_messages]

    @staticmethod
    def get_severity_order(severity: str) -> int:
        """Get numeric order for severity (for sorting).

        Args:
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN)

        Returns:
            Numeric order (0 = highest severity)

        Example:
            >>> order = ErrorClassifier.get_severity_order("CRITICAL")
            >>> print(order)
            0
        """
        return ErrorClassifier.SEVERITY_ORDER.get(severity, 99)

    @staticmethod
    def get_severity_color(severity: str) -> str:
        """Get color code for severity level.

        Args:
            severity: Severity level

        Returns:
            Hex color code

        Example:
            >>> color = ErrorClassifier.get_severity_color("CRITICAL")
            >>> print(color)
            '#dc3545'
        """
        colors = {
            "CRITICAL": "#dc3545",  # Red
            "HIGH": "#fd7e14",  # Orange
            "MEDIUM": "#ffc107",  # Yellow
            "LOW": "#28a745",  # Green
            "UNKNOWN": "#6c757d",  # Gray
        }
        return colors.get(severity, "#6c757d")

    @staticmethod
    def get_severity_emoji(severity: str) -> str:
        """Get emoji for severity level.

        Args:
            severity: Severity level

        Returns:
            Emoji string

        Example:
            >>> emoji = ErrorClassifier.get_severity_emoji("CRITICAL")
            >>> print(emoji)
            '🔴'
        """
        emojis = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "UNKNOWN": "⚪",
        }
        return emojis.get(severity, "⚪")

    @staticmethod
    def extract_model_from_error(error_message: str) -> Optional[str]:
        """Extract model name from error message if present.

        Args:
            error_message: Error message

        Returns:
            Model name if found, None otherwise

        Example:
            >>> model = ErrorClassifier.extract_model_from_error(
            ...     "Rate limit exceeded for model gpt-4"
            ... )
            >>> print(model)
            'gpt-4'
        """
        # Common model patterns
        patterns = [
            r"model\s+([a-zA-Z0-9\-_/]+)",
            r"gpt-[34](?:-\w+)?",
            r"claude-[0-9]-[\w-]+",
            r"gemini-[\w-]+",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                if pattern.startswith("model"):
                    return match.group(1)
                else:
                    return match.group(0)

        return None

    @staticmethod
    def get_error_summary(error_classifications: List[Dict[str, str]]) -> Dict[str, any]:
        """Get summary statistics for a list of error classifications.

        Args:
            error_classifications: List of classification dictionaries

        Returns:
            Dictionary with summary statistics

        Example:
            >>> errors = [ErrorClassifier.classify(msg) for msg in messages]
            >>> summary = ErrorClassifier.get_error_summary(errors)
            >>> print(summary['total_errors'])
        """
        if not error_classifications:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_category": {},
                "by_type": {},
            }

        # Count by severity
        by_severity = {}
        for error in error_classifications:
            severity = error["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count by category
        by_category = {}
        for error in error_classifications:
            category = error["category"]
            by_category[category] = by_category.get(category, 0) + 1

        # Count by type
        by_type = {}
        for error in error_classifications:
            error_type = error["type"]
            by_type[error_type] = by_type.get(error_type, 0) + 1

        return {
            "total_errors": len(error_classifications),
            "by_severity": by_severity,
            "by_category": by_category,
            "by_type": by_type,
        }

    @staticmethod
    def get_all_error_types() -> List[str]:
        """Get list of all known error types.

        Returns:
            List of error type names

        Example:
            >>> types = ErrorClassifier.get_all_error_types()
            >>> print(types)
        """
        return list(ErrorClassifier.ERROR_CATEGORIES.keys())

    @staticmethod
    def get_all_severities() -> List[str]:
        """Get list of all severity levels.

        Returns:
            List of severity levels

        Example:
            >>> severities = ErrorClassifier.get_all_severities()
            >>> print(severities)
        """
        return ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]

    @staticmethod
    def get_all_categories() -> List[str]:
        """Get list of all error categories.

        Returns:
            List of category names

        Example:
            >>> categories = ErrorClassifier.get_all_categories()
            >>> print(categories)
        """
        categories = set()
        for metadata in ErrorClassifier.ERROR_CATEGORIES.values():
            categories.add(metadata["category"])
        return sorted(list(categories))
