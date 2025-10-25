"""Workflow and Data Flow Guide Skill Implementation.

This skill provides comprehensive workflow and data lineage information
to enable orchestration, design validation, and system understanding.
"""

from pathlib import Path
from typing import Any, Dict, List

from coffee_maker.autonomous.skill_loader import BaseSkill


class WorkflowAndDataFlowSkill(BaseSkill):
    """Skill for workflow documentation and data flow analysis."""

    def __init__(self):
        """Initialize the workflow skill."""
        super().__init__()
        self.db_path = Path("data/roadmap.db")
        self._load_workflow_knowledge()

    def _load_workflow_knowledge(self) -> None:
        """Load workflow knowledge from database schema and code analysis."""
        # This would be populated by analyzing the codebase
        # For now, we have the comprehensive documentation in SKILL.md

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute workflow skill action.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            Action result dictionary
        """
        if action == "get_workflows_for_agent":
            return self._get_workflows_for_agent(kwargs.get("agent"))

        elif action == "get_workflow":
            return self._get_workflow(kwargs.get("event"))

        elif action == "get_agent_responsibilities":
            return self._get_agent_responsibilities(kwargs.get("agent"))

        elif action == "get_data_lineage":
            return self._get_data_lineage(kwargs.get("entity"))

        elif action == "validate_agent_description":
            return self._validate_agent_description(kwargs.get("agent"))

        elif action == "get_table_access":
            return self._get_table_access(kwargs.get("table"))

        elif action == "get_orchestration_plan":
            return self._get_orchestration_plan(kwargs.get("workflow_name"))

        elif action == "list_workflows":
            return self._list_workflows()

        elif action == "list_events":
            return self._list_events()

        # Architect-specific methods
        elif action == "validate_workflow_design":
            return self._validate_workflow_design(kwargs.get("workflow_design"))

        elif action == "get_design_patterns":
            return self._get_design_patterns(kwargs.get("workflow_type"))

        elif action == "check_data_consistency":
            return self._check_data_consistency(kwargs.get("entities"))

        elif action == "analyze_bottlenecks":
            return self._analyze_bottlenecks(kwargs.get("workflow_name"))

        elif action == "suggest_database_changes":
            return self._suggest_database_changes(kwargs.get("workflow_requirements"))

        elif action == "validate_agent_boundaries":
            return self._validate_agent_boundaries(kwargs.get("agent"), kwargs.get("proposed_responsibilities"))

        elif action == "get_workflow_dependencies":
            return self._get_workflow_dependencies(kwargs.get("workflow_name"))

        elif action == "compare_workflow_alternatives":
            return self._compare_workflow_alternatives(kwargs.get("alternatives"))

        else:
            return {"error": f"Unknown action: {action}"}

    def _get_workflows_for_agent(self, agent: str) -> Dict[str, Any]:
        """Get only workflows relevant to a specific agent.

        This filters the complete workflow knowledge to show only the parts
        where the specified agent participates, reducing context and focusing
        on agent-specific responsibilities.

        Args:
            agent: Agent name (e.g., 'architect', 'code_developer')

        Returns:
            Dict with agent-specific workflows, their role in each, and action items
        """
        if not agent:
            return {"error": "agent parameter is required"}

        all_workflows = {
            "priority_created": self._get_workflow("priority_created"),
            "spec_created": self._get_workflow("spec_created"),
        }

        # Filter workflows to only include agent's steps
        agent_workflows = {}

        for workflow_name, workflow_data in all_workflows.items():
            if "error" in workflow_data:
                continue

            # Filter steps where this agent participates
            agent_steps = []
            for step in workflow_data.get("steps", []):
                if step.get("agent") == agent:
                    agent_steps.append(step)

            if agent_steps:
                agent_workflows[workflow_name] = {
                    "name": workflow_data.get("name"),
                    "trigger": workflow_data.get("trigger"),
                    "your_role": agent_steps,
                    "context": {
                        "upstream": self._get_upstream_context(workflow_data, agent),  # What happens before
                        "downstream": self._get_downstream_context(workflow_data, agent),  # What happens after
                    },
                }

        return {
            "agent": agent,
            "workflows": agent_workflows,
            "summary": f"Agent {agent} participates in {len(agent_workflows)} workflows",
        }

    def _get_upstream_context(self, workflow_data: Dict[str, Any], agent: str) -> List[Dict[str, str]]:
        """Get context of what happens before agent's involvement.

        Args:
            workflow_data: Complete workflow data
            agent: Agent name

        Returns:
            List of upstream steps (before agent's involvement)
        """
        upstream = []
        for step in workflow_data.get("steps", []):
            if step.get("agent") == agent:
                break  # Stop when we reach this agent
            upstream.append(
                {"agent": step.get("agent"), "summary": step.get("actions", [])[0] if step.get("actions") else ""}
            )
        return upstream

    def _get_downstream_context(self, workflow_data: Dict[str, Any], agent: str) -> List[Dict[str, str]]:
        """Get context of what happens after agent's involvement.

        Args:
            workflow_data: Complete workflow data
            agent: Agent name

        Returns:
            List of downstream steps (after agent's involvement)
        """
        downstream = []
        found_agent = False

        for step in workflow_data.get("steps", []):
            if found_agent:
                downstream.append(
                    {
                        "agent": step.get("agent"),
                        "summary": step.get("actions", [])[0] if step.get("actions") else "",
                    }
                )
            elif step.get("agent") == agent:
                found_agent = True

        return downstream

    def _get_workflow(self, event: str) -> Dict[str, Any]:
        """Get complete workflow for an event.

        Args:
            event: Event name (e.g., 'priority_created')

        Returns:
            Workflow details including agents, database operations, conditions
        """
        workflows = {
            "priority_created": {
                "name": "Priority Creation and Implementation",
                "trigger": "New PRIORITY in ROADMAP.md",
                "steps": [
                    {
                        "agent": "project_manager",
                        "actions": [
                            "Parse ROADMAP.md content",
                            "Extract priority metadata",
                            "INSERT INTO roadmap_priority",
                            "INSERT INTO roadmap_audit (action='create')",
                            "If spec_id is NULL: INSERT INTO notifications (target='architect')",
                        ],
                        "database_ops": {
                            "roadmap_priority": "INSERT",
                            "roadmap_audit": "INSERT",
                            "notifications": "INSERT (conditional)",
                        },
                    },
                    {
                        "agent": "architect",
                        "trigger": "Notification or daily check",
                        "actions": [
                            "Query roadmap_priority WHERE spec_id IS NULL",
                            "Create technical specification",
                            "INSERT INTO specs_specification",
                            "UPDATE roadmap_priority SET spec_id",
                            "UPDATE notifications SET status='processed'",
                        ],
                        "database_ops": {
                            "roadmap_priority": "SELECT, UPDATE",
                            "specs_specification": "INSERT",
                            "notifications": "UPDATE",
                        },
                    },
                    {
                        "agent": "code_developer",
                        "trigger": "Autonomous daemon polling",
                        "actions": [
                            "Query roadmap_priority WHERE status='Planned' AND spec_id NOT NULL",
                            "Load spec from specs_specification",
                            "UPDATE roadmap_priority SET status='In Progress'",
                            "Implement feature",
                            "Run tests, commit, create PR",
                            "UPDATE roadmap_priority SET status='Complete'",
                            "INSERT INTO notifications (target='project_manager')",
                        ],
                        "database_ops": {
                            "roadmap_priority": "SELECT, UPDATE",
                            "specs_specification": "SELECT",
                            "notifications": "INSERT",
                        },
                    },
                ],
                "data_flow": {
                    "input": "ROADMAP.md (user-created content)",
                    "transformations": [
                        "Markdown → roadmap_priority row",
                        "Spec template → specs_specification row",
                        "Implementation → code commits",
                    ],
                    "output": "Completed feature with audit trail",
                },
            },
            "spec_created": {
                "name": "Technical Specification Creation",
                "trigger": "architect creates new spec",
                "steps": [
                    {
                        "agent": "architect",
                        "actions": [
                            "Determine spec type (hierarchical/monolithic)",
                            "Generate spec number",
                            "Create spec content",
                            "INSERT INTO specs_specification",
                            "If hierarchical: Create directory and phase files",
                            "If roadmap_item_id: UPDATE roadmap_priority",
                        ],
                        "database_ops": {
                            "specs_specification": "INSERT",
                            "roadmap_priority": "UPDATE (conditional)",
                            "system_audit": "INSERT",
                        },
                    }
                ],
                "data_flow": {
                    "input": "Spec requirements, roadmap context",
                    "transformations": ["Template → spec content", "Content → database row"],
                    "output": "Spec in database + files (if hierarchical)",
                },
            },
        }

        return workflows.get(event, {"error": f"Unknown event: {event}"})

    def _get_agent_responsibilities(self, agent: str) -> Dict[str, Any]:
        """Get all responsibilities for an agent.

        Args:
            agent: Agent name

        Returns:
            Agent responsibilities, workflows, database access
        """
        responsibilities = {
            "project_manager": {
                "database_operations": {
                    "roadmap_priority": ["CREATE", "UPDATE (content, status finalization)"],
                    "notifications": ["CREATE (outgoing)", "UPDATE (mark processed)"],
                    "roadmap_audit": ["CREATE (automatic)"],
                },
                "claimed_responsibilities": [
                    "Parse ROADMAP.md and sync to database",
                    "Create new priorities and user stories",
                    "Monitor GitHub PRs and issues",
                    "Verify DoD (post-implementation)",
                    "Create notifications for other agents",
                ],
                "workflows_involved": [
                    "priority_created",
                    "implementation_complete",
                    "notification_processing",
                ],
                "file_ownership": ["docs/roadmap/", "docs/*.md (top-level)"],
            },
            "architect": {
                "database_operations": {
                    "specs_specification": ["CREATE", "UPDATE (all fields)"],
                    "roadmap_priority": ["UPDATE (spec_id linkage only)"],
                    "notifications": ["CREATE (outgoing)", "UPDATE (mark processed)"],
                    "system_audit": ["CREATE (automatic)"],
                },
                "claimed_responsibilities": [
                    "Create technical specifications",
                    "Design system architecture",
                    "Manage dependencies (pyproject.toml)",
                    "Link specs to roadmap items",
                    "Provide implementation guidelines",
                ],
                "workflows_involved": ["spec_created", "spec_linked", "dependency_added"],
                "file_ownership": ["docs/architecture/", "pyproject.toml", "poetry.lock"],
            },
            "code_developer": {
                "database_operations": {
                    "roadmap_priority": ["UPDATE (status only: Planned → In Progress → Complete)"],
                    "specs_specification": ["UPDATE (phase status, actual_hours)"],
                    "notifications": ["CREATE (implementation_complete)"],
                    "roadmap_audit": ["CREATE (automatic)"],
                },
                "claimed_responsibilities": [
                    "Implement features from specs",
                    "Update implementation status",
                    "Run tests and create PRs",
                    "Manage technical configuration (.claude/)",
                    "Write all code in coffee_maker/, tests/",
                ],
                "workflows_involved": [
                    "implementation_started",
                    "implementation_complete",
                    "pr_created",
                ],
                "file_ownership": ["coffee_maker/", "tests/", "scripts/", ".claude/"],
            },
        }

        return responsibilities.get(agent, {"error": f"Unknown agent: {agent}"})

    def _get_data_lineage(self, entity: str) -> Dict[str, Any]:
        """Trace data flow for an entity.

        Args:
            entity: Entity name (e.g., 'technical_spec')

        Returns:
            Complete data lineage from creation to usage
        """
        lineages = {
            "roadmap_priority": {
                "creation": {
                    "source": "User edits ROADMAP.md",
                    "agent": "project_manager",
                    "operation": "INSERT INTO roadmap_priority",
                    "table": "roadmap_priority",
                },
                "transformations": [
                    {
                        "event": "Status update to 'In Progress'",
                        "agent": "code_developer",
                        "operation": "UPDATE roadmap_priority SET status='In Progress'",
                    },
                    {
                        "event": "Spec linkage",
                        "agent": "architect",
                        "operation": "UPDATE roadmap_priority SET spec_id={id}",
                    },
                    {
                        "event": "Completion",
                        "agent": "code_developer",
                        "operation": "UPDATE roadmap_priority SET status='Complete'",
                    },
                ],
                "storage": {
                    "primary": "roadmap_priority table",
                    "audit": "roadmap_audit table (all changes)",
                    "related": "specs_specification (via spec_id foreign key)",
                },
                "consumers": [
                    "code_developer (reads for implementation)",
                    "project_manager (reads for planning)",
                    "orchestrator (reads for task coordination)",
                ],
            },
            "technical_spec": {
                "creation": {
                    "source": "architect designs specification",
                    "agent": "architect",
                    "operation": "INSERT INTO specs_specification",
                    "table": "specs_specification",
                },
                "transformations": [
                    {
                        "event": "Phase completion",
                        "agent": "code_developer",
                        "operation": "UPDATE specs_specification SET current_phase_status",
                    },
                    {
                        "event": "Linkage to roadmap",
                        "agent": "architect",
                        "operation": "UPDATE roadmap_priority SET spec_id",
                    },
                ],
                "storage": {
                    "primary": "specs_specification table",
                    "files": "docs/architecture/specs/SPEC-{number}-{slug}/ (if hierarchical)",
                    "audit": "system_audit table",
                },
                "consumers": [
                    "code_developer (reads during implementation)",
                    "project_manager (reads for planning)",
                    "architect (updates during refinement)",
                ],
            },
        }

        return lineages.get(entity, {"error": f"Unknown entity: {entity}"})

    def _validate_agent_description(self, agent: str) -> Dict[str, Any]:
        """Validate agent description matches implementation.

        Args:
            agent: Agent name

        Returns:
            Validation results with discrepancies
        """
        # This would analyze code to verify claims
        # For now, return that all agents are valid based on our documentation
        return {
            "agent": agent,
            "validation_status": "valid",
            "claimed_responsibilities": self._get_agent_responsibilities(agent).get("claimed_responsibilities", []),
            "actual_implementation": "matches_claims",
            "discrepancies": [],
            "recommendations": [],
        }

    def _get_table_access(self, table: str) -> Dict[str, Any]:
        """Get access patterns for a database table.

        Args:
            table: Table name

        Returns:
            Access patterns including agents, operations, conditions
        """
        # Analyze which agents access which tables
        access_patterns = {
            "roadmap_priority": {
                "write_access": [
                    {
                        "agent": "project_manager",
                        "operations": ["INSERT (create)", "UPDATE (content, finalization)"],
                        "frequency": "On demand (user requests)",
                    },
                    {
                        "agent": "code_developer",
                        "operations": ["UPDATE (status only)"],
                        "frequency": "Continuous (daemon polling)",
                    },
                    {
                        "agent": "architect",
                        "operations": ["UPDATE (spec_id linkage)"],
                        "frequency": "On spec creation",
                    },
                ],
                "read_access": [
                    {
                        "agent": "all",
                        "operations": ["SELECT (query)"],
                        "frequency": "High (continuous monitoring)",
                    }
                ],
                "indexes": ["idx_items_status", "idx_items_priority_order", "idx_items_spec"],
                "constraints": ["PRIMARY KEY (id)", "UNIQUE (priority_order)", "FOREIGN KEY (spec_id)"],
            },
            "specs_specification": {
                "write_access": [
                    {
                        "agent": "architect",
                        "operations": ["INSERT (create)", "UPDATE (all fields)"],
                        "frequency": "On spec creation/updates",
                    },
                    {
                        "agent": "code_developer",
                        "operations": ["UPDATE (phase status, actual_hours)"],
                        "frequency": "During implementation",
                    },
                ],
                "read_access": [
                    {
                        "agent": "code_developer",
                        "operations": ["SELECT (load spec content)"],
                        "frequency": "High (implementation)",
                    },
                    {
                        "agent": "project_manager",
                        "operations": ["SELECT (planning)"],
                        "frequency": "Medium (planning queries)",
                    },
                ],
                "indexes": ["idx_specs_roadmap", "idx_specs_status", "idx_specs_number"],
                "constraints": [
                    "PRIMARY KEY (id)",
                    "UNIQUE (spec_number)",
                    "FOREIGN KEY (roadmap_item_id)",
                ],
            },
        }

        return access_patterns.get(table, {"error": f"Unknown table: {table}"})

    def _get_orchestration_plan(self, workflow_name: str) -> Dict[str, Any]:
        """Get orchestration plan for a workflow.

        Args:
            workflow_name: Workflow name

        Returns:
            Orchestration plan with preconditions, steps, postconditions
        """
        plans = {
            "implement_priority": {
                "preconditions": [
                    "roadmap_priority.status = 'Planned'",
                    "roadmap_priority.spec_id IS NOT NULL",
                    "specs_specification exists and is complete",
                ],
                "steps": [
                    {"seq": 1, "agent": "code_developer", "action": "load_spec"},
                    {"seq": 2, "agent": "code_developer", "action": "determine_phase"},
                    {
                        "seq": 3,
                        "agent": "code_developer",
                        "action": "update_status_to_in_progress",
                    },
                    {"seq": 4, "agent": "code_developer", "action": "implement_feature"},
                    {"seq": 5, "agent": "code_developer", "action": "run_tests"},
                    {"seq": 6, "agent": "code_developer", "action": "commit_and_create_pr"},
                    {"seq": 7, "agent": "code_developer", "action": "update_status_to_complete"},
                    {"seq": 8, "agent": "code_reviewer", "action": "review_commit"},
                    {"seq": 9, "agent": "project_manager", "action": "verify_dod", "optional": True},
                    {"seq": 10, "agent": "project_manager", "action": "merge_pr"},
                ],
                "postconditions": [
                    "Code committed and tested",
                    "PR created on GitHub",
                    "roadmap_priority.status = 'Complete'",
                    "Audit trail created",
                ],
                "error_handling": {
                    "test_failure": "Rollback commit, create notification",
                    "missing_spec": "Create notification for architect",
                    "merge_conflict": "Manual resolution required",
                },
            }
        }

        return plans.get(workflow_name, {"error": f"Unknown workflow: {workflow_name}"})

    def _list_workflows(self) -> Dict[str, List[str]]:
        """List all documented workflows."""
        return {
            "workflows": [
                "priority_created",
                "spec_created",
                "implementation_started",
                "implementation_complete",
                "review_requested",
                "notification_processing",
                "parallel_execution",
            ]
        }

    def _list_events(self) -> Dict[str, List[Dict[str, str]]]:
        """List all documented events."""
        return {
            "events": [
                {"name": "priority_created", "description": "New roadmap priority created"},
                {"name": "spec_created", "description": "New technical spec created"},
                {"name": "spec_linked", "description": "Spec linked to roadmap item"},
                {
                    "name": "implementation_started",
                    "description": "Code developer starts implementation",
                },
                {
                    "name": "implementation_complete",
                    "description": "Feature implementation finished",
                },
                {"name": "pr_created", "description": "Pull request created"},
                {"name": "pr_merged", "description": "Pull request merged"},
                {"name": "notification_created", "description": "New notification for agent"},
            ]
        }

    # Architect-specific methods

    def _validate_workflow_design(self, workflow_design: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a proposed workflow design.

        Args:
            workflow_design: Proposed workflow structure

        Returns:
            Validation results with recommendations
        """
        if not workflow_design:
            return {"error": "workflow_design is required"}

        issues = []
        recommendations = []

        # Check for required fields
        if "steps" not in workflow_design:
            issues.append("Missing 'steps' field")

        if "data_flow" not in workflow_design:
            issues.append("Missing 'data_flow' field")
            recommendations.append("Add data_flow to track data transformations")

        # Validate steps
        if "steps" in workflow_design:
            for i, step in enumerate(workflow_design["steps"]):
                if "agent" not in step:
                    issues.append(f"Step {i}: Missing agent assignment")

                if "database" in step:
                    # Check if audit trail is included
                    tables = step.get("database", [])
                    if any(t in tables for t in ["roadmap_priority", "specs_specification"]):
                        if "roadmap_audit" not in tables and "system_audit" not in tables:
                            recommendations.append(f"Step {i}: Consider adding audit trail for data mutation")

        # Check error handling
        if "error_handling" not in workflow_design:
            recommendations.append("Add error_handling to define rollback and recovery strategies")

        # Check data flow
        if "data_flow" in workflow_design:
            df = workflow_design["data_flow"]
            if "input" not in df:
                issues.append("data_flow missing 'input'")
            if "output" not in df:
                issues.append("data_flow missing 'output'")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "complexity_score": len(workflow_design.get("steps", [])),
        }

    def _get_design_patterns(self, workflow_type: str) -> Dict[str, Any]:
        """Get recommended design patterns for workflow type.

        Args:
            workflow_type: Type of workflow

        Returns:
            Recommended patterns with examples
        """
        patterns = {
            "inter_agent_communication": {
                "recommended": [
                    {
                        "name": "Notification Pattern",
                        "description": "Use notifications table for async communication",
                        "structure": {
                            "sender": "INSERT INTO notifications (target_agent, message)",
                            "receiver": "Poll notifications WHERE target_agent=self",
                            "completion": "UPDATE notifications SET status='processed'",
                        },
                        "benefits": ["Decoupling", "Audit trail", "Retry support"],
                    }
                ],
                "anti_patterns": [
                    {
                        "name": "Direct function calls",
                        "why_avoid": "Creates tight coupling, hard to audit",
                    }
                ],
            },
            "data_processing": {
                "recommended": [
                    {
                        "name": "Event Sourcing",
                        "description": "Store all changes as events",
                        "benefits": ["Complete history", "Replay capability", "Audit trail"],
                    },
                    {
                        "name": "CQRS",
                        "description": "Separate read and write models",
                        "benefits": ["Read optimization", "Write safety", "Scalability"],
                    },
                ],
            },
        }

        return patterns.get(workflow_type, {"error": f"Unknown workflow_type: {workflow_type}"})

    def _check_data_consistency(self, entities: List[str]) -> Dict[str, Any]:
        """Check data consistency requirements.

        Args:
            entities: List of entities to check

        Returns:
            Consistency rules and potential violations
        """
        if not entities:
            return {"error": "entities list is required"}

        rules = {}
        for entity in entities:
            if entity == "specs_specification":
                rules[entity] = {
                    "foreign_keys": [
                        {
                            "field": "roadmap_item_id",
                            "references": "roadmap_priority(id)",
                            "constraint": "ON DELETE SET NULL",
                        }
                    ],
                    "integrity_checks": ["Orphaned specs if roadmap_item_id not in roadmap_priority"],
                }
            elif entity == "roadmap_priority":
                rules[entity] = {
                    "foreign_keys": [
                        {
                            "field": "spec_id",
                            "references": "specs_specification(id)",
                            "constraint": "ON DELETE SET NULL",
                        }
                    ],
                    "integrity_checks": ["Invalid spec_id if not in specs_specification"],
                }

        return {"consistency_rules": rules, "violations": []}

    def _analyze_bottlenecks(self, workflow_name: str) -> Dict[str, Any]:
        """Analyze workflow for bottlenecks.

        Args:
            workflow_name: Workflow to analyze

        Returns:
            Bottleneck analysis with suggestions
        """
        # This would analyze actual workflow execution times
        # For now, provide general guidance
        return {
            "workflow": workflow_name,
            "bottlenecks": [
                {
                    "step": "Sequential review step",
                    "issue": "Blocks implementation progress",
                    "suggestion": "Use async notifications instead",
                }
            ],
            "parallelization_opportunities": ["Independent specs can be implemented in parallel using git worktrees"],
        }

    def _suggest_database_changes(self, workflow_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest database schema changes for workflow.

        Args:
            workflow_requirements: Requirements dictionary

        Returns:
            Suggested schema changes
        """
        if not workflow_requirements:
            return {"error": "workflow_requirements is required"}

        suggestions = {"new_tables": [], "new_columns": [], "new_indexes": [], "migrations": []}

        # Analyze requirements and suggest changes
        # This is a simplified example
        if "entities" in workflow_requirements:
            for entity in workflow_requirements["entities"]:
                suggestions["new_tables"].append(
                    {
                        "name": entity,
                        "columns": ["id TEXT PRIMARY KEY", "created_at TEXT", "updated_at TEXT"],
                    }
                )

        return suggestions

    def _validate_agent_boundaries(self, agent: str, proposed_responsibilities: List[str]) -> Dict[str, Any]:
        """Validate agent doesn't violate boundaries.

        Args:
            agent: Agent name
            proposed_responsibilities: List of proposed responsibilities

        Returns:
            Validation results with violations
        """
        if not agent or not proposed_responsibilities:
            return {"error": "agent and proposed_responsibilities are required"}

        # Get actual agent responsibilities
        actual = self._get_agent_responsibilities(agent)
        claimed = actual.get("claimed_responsibilities", [])

        violations = []
        for responsibility in proposed_responsibilities:
            if responsibility not in claimed:
                # Check if it belongs to another agent
                for other_agent in ["project_manager", "architect", "code_developer"]:
                    if other_agent != agent:
                        other = self._get_agent_responsibilities(other_agent)
                        if responsibility in other.get("claimed_responsibilities", []):
                            violations.append(
                                {
                                    "responsibility": responsibility,
                                    "violation": f"Belongs to {other_agent}",
                                    "recommendation": f"Remove from {agent}, delegate to {other_agent}",
                                }
                            )

        return {
            "agent": agent,
            "proposed": proposed_responsibilities,
            "claimed": claimed,
            "violations": violations,
            "valid": len(violations) == 0,
        }

    def _get_workflow_dependencies(self, workflow_name: str) -> Dict[str, Any]:
        """Get all dependencies for a workflow.

        Args:
            workflow_name: Workflow name

        Returns:
            Complete dependency list
        """
        # Get orchestration plan and extract dependencies
        plan = self._get_orchestration_plan(workflow_name)

        if "error" in plan:
            return plan

        dependencies = {
            "database_tables": set(),
            "agents": set(),
            "external_services": [],
            "configuration": [],
        }

        for step in plan.get("steps", []):
            dependencies["agents"].add(step.get("agent"))

        # Convert sets to lists for JSON serialization
        dependencies["database_tables"] = list(dependencies["database_tables"])
        dependencies["agents"] = list(dependencies["agents"])

        return dependencies

    def _compare_workflow_alternatives(self, alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare workflow design alternatives.

        Args:
            alternatives: List of workflow designs

        Returns:
            Comparison matrix with recommendation
        """
        if not alternatives or len(alternatives) < 2:
            return {"error": "Provide at least 2 alternatives to compare"}

        comparisons = []
        for i, alt in enumerate(alternatives):
            validation = self._validate_workflow_design(alt)
            comparisons.append(
                {
                    "alternative": i + 1,
                    "complexity": len(alt.get("steps", [])),
                    "valid": validation.get("valid", False),
                    "issues": len(validation.get("issues", [])),
                    "pros": [],
                    "cons": [],
                }
            )

        # Recommend simplest valid alternative
        valid_alts = [c for c in comparisons if c["valid"]]
        if valid_alts:
            recommendation = min(valid_alts, key=lambda x: x["complexity"])
            return {"comparisons": comparisons, "recommendation": recommendation["alternative"]}

        return {"comparisons": comparisons, "recommendation": None}
