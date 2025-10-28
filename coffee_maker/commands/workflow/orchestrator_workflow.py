"""Orchestrator Workflow Command - Ultra-Consolidated."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from coffee_maker.commands.consolidated.orchestrator_commands import OrchestratorCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class CoordinateAction(Enum):
    AGENTS = "agents"
    WORK = "work"
    MESSAGES = "messages"
    WORKTREES = "worktrees"


@dataclass
class CoordinateResult:
    action: str
    status: str = "success"
    agents_managed: int = 0
    tasks_assigned: int = 0
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestratorWorkflow:
    def __init__(self, db_path: Optional[str] = None):
        self.commands = OrchestratorCommands(db_path)
        self.logger = logger

    def coordinate(self, action: str, **params) -> CoordinateResult:
        start_time = datetime.now()
        try:
            coord_action = CoordinateAction(action)
            result = CoordinateResult(action=action)

            if coord_action == CoordinateAction.AGENTS:
                result.metadata["agents"] = self.commands.agents(**params)
            elif coord_action == CoordinateAction.WORK:
                result.metadata["work"] = self.commands.orchestrate(action="find_work", **params)
            elif coord_action == CoordinateAction.MESSAGES:
                result.metadata["messages"] = self.commands.messages(**params)
            elif coord_action == CoordinateAction.WORKTREES:
                result.metadata["worktrees"] = self.commands.worktree(**params)

            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            return result
        except Exception:
            return CoordinateResult(
                action=action, status="failed", duration_seconds=(datetime.now() - start_time).total_seconds()
            )
