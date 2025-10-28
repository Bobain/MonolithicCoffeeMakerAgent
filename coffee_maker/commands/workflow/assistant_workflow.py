"""Assistant Workflow Command - Ultra-Consolidated."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from coffee_maker.commands.consolidated.assistant_commands import AssistantCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class AssistType(Enum):
    AUTO = "auto"
    DOCS = "docs"
    DEMO = "demo"
    BUG = "bug"
    DELEGATE = "delegate"


@dataclass
class AssistResult:
    request: str
    status: str = "success"
    result_data: Any = None
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssistantWorkflow:
    def __init__(self, db_path: Optional[str] = None):
        self.commands = AssistantCommands(db_path)
        self.logger = logger

    def assist(self, request: str, type: str = "auto") -> Any:
        datetime.now()
        try:
            if type == "auto":
                classification = self.commands.delegate(action="classify", request_text=request)
                type = classification.get("intent", "delegate") if isinstance(classification, dict) else "delegate"

            if type == "docs":
                return self.commands.docs(action="generate", component=request)
            elif type == "demo":
                return self.commands.demo(action="create", feature=request)
            elif type == "bug":
                return self.commands.bug(action="track", description=request)
            else:
                return self.commands.delegate(action="route", request_text=request)
        except Exception:
            return AssistResult(request=request, status="failed")
