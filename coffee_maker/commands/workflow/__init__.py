"""Workflow-based command architecture.

Ultra-consolidated commands that handle complete workflows, not individual steps.
Each command represents one agent's primary workflow.

Design Principles:
- Workflow-first: Complete workflows, not steps
- Smart defaults: Works with minimal parameters
- Progressive disclosure: Simple by default, powerful when needed
- CFR-007 compliant: Minimal context usage (<5%)

Commands:
    CodeDeveloperWorkflow.work() - Full implementation workflow
    ArchitectWorkflow.spec() - Full design workflow
    ProjectManagerWorkflow.manage() - Project operations
    CodeReviewerWorkflow.review() - Full review workflow
    OrchestratorWorkflow.coordinate() - Team coordination
    UserListenerWorkflow.interact() - Full UI workflow
    AssistantWorkflow.assist() - Help workflow
    UXDesignWorkflow.design() - Full design workflow
"""

from .code_developer_workflow import CodeDeveloperWorkflow
from .architect_workflow import ArchitectWorkflow
from .project_manager_workflow import ProjectManagerWorkflow
from .code_reviewer_workflow import CodeReviewerWorkflow
from .orchestrator_workflow import OrchestratorWorkflow
from .user_listener_workflow import UserListenerWorkflow
from .assistant_workflow import AssistantWorkflow
from .ux_design_workflow import UXDesignWorkflow

__all__ = [
    "CodeDeveloperWorkflow",
    "ArchitectWorkflow",
    "ProjectManagerWorkflow",
    "CodeReviewerWorkflow",
    "OrchestratorWorkflow",
    "UserListenerWorkflow",
    "AssistantWorkflow",
    "UXDesignWorkflow",
]
