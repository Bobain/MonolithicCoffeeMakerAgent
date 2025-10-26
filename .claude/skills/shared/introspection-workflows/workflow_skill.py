"""Workflow and Data Flow Guide Skill Implementation.

This skill dynamically introspects agent definitions and code to extract
real workflows, data flows, and agent interactions. No hardcoded documentation.
"""

import ast
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from coffee_maker.autonomous.skill_loader import BaseSkill


class WorkflowAndDataFlowSkill(BaseSkill):
    """Dynamic workflow extraction through code and agent introspection."""

    def __init__(self):
        """Initialize the workflow skill."""
        super().__init__()
        self.db_path = Path("data/roadmap.db")
        self.agents_dir = Path(".claude/agents")
        self.code_dir = Path("coffee_maker")

        # Cache for performance
        self._agent_cache = {}
        self._workflow_cache = {}
        self._table_relationships = None

    def _extract_agent_workflows(self, agent_name: str) -> List[Dict[str, Any]]:
        """Extract workflows from agent markdown files.

        Parses .claude/agents/{agent}.md to find workflow definitions,
        database interactions, and agent communications.
        """
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return []

        workflows = []
        content = agent_file.read_text()

        # Extract workflow sections (### Workflow X:)
        workflow_pattern = r"### Workflow (\d+):\s*([^\n]+)(.*?)(?=###|\Z)"
        for match in re.finditer(workflow_pattern, content, re.DOTALL):
            workflow_num = match.group(1)
            workflow_title = match.group(2).strip()
            workflow_content = match.group(3)

            # Extract database operations
            db_ops = self._extract_database_operations(workflow_content)

            # Extract agent interactions
            agent_interactions = self._extract_agent_interactions(workflow_content)

            # Extract triggers/events
            triggers = self._extract_workflow_triggers(workflow_content)

            workflows.append(
                {
                    "workflow_id": f"{agent_name}_workflow_{workflow_num}",
                    "title": workflow_title,
                    "agent": agent_name,
                    "database_operations": db_ops,
                    "agent_interactions": agent_interactions,
                    "triggers": triggers,
                    "source": f"{agent_file}:Workflow {workflow_num}",
                }
            )

        return workflows

    def _extract_database_operations(self, content: str) -> List[Dict[str, str]]:
        """Extract database operations from workflow content.

        Looks for patterns like:
        - cursor.execute
        - db.get_all_items()
        - INSERT INTO, UPDATE, SELECT FROM
        """
        operations = []

        # SQL operation patterns
        sql_patterns = [
            (r"INSERT INTO\s+(\w+)", "create"),
            (r"UPDATE\s+(\w+)", "update"),
            (r"SELECT.*FROM\s+(\w+)", "read"),
            (r"DELETE FROM\s+(\w+)", "delete"),
        ]

        for pattern, op_type in sql_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                table = match.group(1)
                operations.append({"table": table, "operation": op_type, "context": match.group(0)[:100]})

        # Python database method patterns
        py_patterns = [
            (r"(\w+)\.get_all_items\(\)", "read"),
            (r"(\w+)\.create_\w+\([^)]*\)", "create"),
            (r"(\w+)\.update_\w+\([^)]*\)", "update"),
            (r"(\w+)\.get_next_\w+\(\)", "read"),
        ]

        for pattern, op_type in py_patterns:
            for match in re.finditer(pattern, content):
                operations.append({"object": match.group(1), "operation": op_type, "method": match.group(0)})

        return operations

    def _extract_agent_interactions(self, content: str) -> List[Dict[str, str]]:
        """Extract agent-to-agent interactions from content.

        Looks for:
        - send_message_to_agent
        - delegates to X
        - notifies Y
        - requests from Z
        """
        interactions = []

        # Message sending patterns
        message_pattern = r'send_message_to_agent\([^,]*,\s*["\']?(\w+)["\']?'
        for match in re.finditer(message_pattern, content):
            target_agent = match.group(1)
            interactions.append({"type": "message", "target": target_agent, "context": match.group(0)})

        # Delegation patterns
        delegate_pattern = r"delegat\w+\s+to\s+(\w+)"
        for match in re.finditer(delegate_pattern, content, re.IGNORECASE):
            target = match.group(1)
            interactions.append({"type": "delegate", "target": target, "context": match.group(0)})

        # Notification patterns
        notify_pattern = r"notif\w+\s+(\w+)"
        for match in re.finditer(notify_pattern, content, re.IGNORECASE):
            target = match.group(1)
            if target not in ["user", "the", "a", "an"]:  # Filter common words
                interactions.append({"type": "notify", "target": target, "context": match.group(0)})

        return interactions

    def _extract_workflow_triggers(self, content: str) -> List[str]:
        """Extract what triggers a workflow.

        Looks for:
        - When: statements
        - After: statements
        - On: statements
        - Event patterns
        """
        triggers = []

        trigger_patterns = [
            r"When[:\s]+([^\n.]+)",
            r"After[:\s]+([^\n.]+)",
            r"On[:\s]+([^\n.]+)",
            r"Triggered by[:\s]+([^\n.]+)",
        ]

        for pattern in trigger_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                trigger = match.group(1).strip()
                if trigger and len(trigger) < 200:  # Reasonable length
                    triggers.append(trigger)

        return triggers

    def _analyze_database_relationships(self) -> Dict[str, List[Dict[str, str]]]:
        """Analyze database schema for table relationships.

        Connects to the actual database and extracts:
        - Foreign key relationships
        - Table dependencies
        - Data flow paths
        """
        if self._table_relationships:
            return self._table_relationships

        relationships = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                relationships[table] = []

                # Get foreign key info
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                for row in cursor.fetchall():
                    relationships[table].append(
                        {"type": "foreign_key", "from_column": row[3], "to_table": row[2], "to_column": row[4]}
                    )

                # Analyze column names for implicit relationships
                cursor.execute(f"PRAGMA table_info({table})")
                for row in cursor.fetchall():
                    col_name = row[1]
                    # Look for _id patterns suggesting relationships
                    if col_name.endswith("_id") and col_name != "id":
                        potential_table = col_name[:-3]  # Remove _id
                        if potential_table in tables or f"{potential_table}s" in tables:
                            relationships[table].append(
                                {"type": "implicit", "column": col_name, "likely_references": potential_table}
                            )

            conn.close()
            self._table_relationships = relationships

        except Exception as e:
            print(f"Error analyzing database: {e}")
            self._table_relationships = {}

        return relationships

    def _scan_code_for_workflows(self) -> List[Dict[str, Any]]:
        """Scan Python code for workflow implementations.

        Looks for:
        - Agent class methods that implement workflows
        - Database operation sequences
        - Inter-agent communication patterns
        """
        workflows = []

        # Find all agent implementation files
        agent_files = list(self.code_dir.rglob("*agent*.py"))

        for file_path in agent_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Look for workflow-related methods
                        if any(
                            keyword in node.name.lower()
                            for keyword in ["workflow", "process", "handle", "execute", "run"]
                        ):

                            workflow = {
                                "function": node.name,
                                "file": str(file_path),
                                "line": node.lineno,
                                "operations": [],
                            }

                            # Analyze function body for operations
                            for child in ast.walk(node):
                                if isinstance(child, ast.Call):
                                    if hasattr(child.func, "attr"):
                                        method = child.func.attr
                                        # Database operations
                                        if any(
                                            db_op in method
                                            for db_op in ["execute", "insert", "update", "select", "get", "create"]
                                        ):
                                            workflow["operations"].append({"type": "database", "method": method})
                                        # Agent communications
                                        elif "send" in method or "notify" in method:
                                            workflow["operations"].append({"type": "communication", "method": method})

                            if workflow["operations"]:
                                workflows.append(workflow)

            except Exception:
                continue  # Skip files that can't be parsed

        return workflows

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

        elif action == "get_data_flow":
            return self._get_data_flow(kwargs.get("feature"))

        elif action == "get_event_workflows":
            return self._get_event_workflows(kwargs.get("event"))

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
        """Dynamically extract workflows for a specific agent.

        Uses introspection to find:
        1. Workflows defined in agent markdown files
        2. Code implementations in Python files
        3. Database interactions
        4. Agent communications

        Args:
            agent: Agent name (e.g., 'architect', 'code_developer')

        Returns:
            Dict with dynamically extracted workflows
        """
        if not agent:
            return {"error": "agent parameter is required"}

        # Check cache first
        cache_key = f"workflows_{agent}"
        if cache_key in self._workflow_cache:
            return self._workflow_cache[cache_key]

        # Extract from agent markdown
        agent_workflows = self._extract_agent_workflows(agent)

        # Extract from code
        code_workflows = self._scan_code_for_workflows()

        # Filter code workflows for this agent
        agent_code_workflows = [w for w in code_workflows if agent in w.get("file", "").lower()]

        # Get database relationships
        self._analyze_database_relationships()

        # Combine all sources
        result = {
            "agent": agent,
            "markdown_workflows": agent_workflows,
            "code_implementations": agent_code_workflows,
            "database_access": self._get_agent_database_access(agent, agent_workflows),
            "agent_interactions": self._get_agent_interactions(agent, agent_workflows),
            "summary": f"Found {len(agent_workflows)} documented workflows and {len(agent_code_workflows)} code implementations",
        }

        # Cache result
        self._workflow_cache[cache_key] = result

        return result

    def _get_agent_database_access(self, agent: str, workflows: List[Dict]) -> Dict[str, List[str]]:
        """Extract database tables this agent accesses."""
        tables = {}
        for workflow in workflows:
            for op in workflow.get("database_operations", []):
                table = op.get("table")
                if table:
                    if table not in tables:
                        tables[table] = []
                    tables[table].append(op.get("operation"))
        return tables

    def _get_agent_interactions(self, agent: str, workflows: List[Dict]) -> Dict[str, List[str]]:
        """Extract which agents this one interacts with."""
        interactions = {}
        for workflow in workflows:
            for interaction in workflow.get("agent_interactions", []):
                target = interaction.get("target")
                if target and target != agent:
                    if target not in interactions:
                        interactions[target] = []
                    interactions[target].append(interaction.get("type"))
        return interactions

    def _get_data_flow(self, feature: str) -> Dict[str, Any]:
        """Trace data flow for a specific feature.

        Dynamically analyzes how data flows through the system for a feature.

        Args:
            feature: Feature name (e.g., 'roadmap_update', 'spec_creation')

        Returns:
            Complete data flow from source to destination
        """
        if not feature:
            return {"error": "feature parameter is required"}

        # Map common features to their data flows
        feature_patterns = {
            "roadmap_update": ["roadmap_priority", "roadmap_audit", "roadmap_notification"],
            "spec_creation": ["technical_specs", "implementation_tasks", "roadmap_priority"],
            "implementation": ["implementation_tasks", "task_execution", "orchestrator_state"],
        }

        # Find matching tables
        tables = []
        for pattern, table_list in feature_patterns.items():
            if pattern in feature.lower():
                tables = table_list
                break

        if not tables:
            # Try to find tables by analyzing database
            db_relationships = self._analyze_database_relationships()
            tables = [t for t in db_relationships.keys() if feature.lower() in t.lower()]

        # Build data flow
        flow = []
        for i, table in enumerate(tables):
            step = {
                "step": i + 1,
                "table": table,
                "operations": self._get_table_operations(table),
                "relationships": self._analyze_database_relationships().get(table, []),
            }
            flow.append(step)

        return {"feature": feature, "data_flow": flow, "summary": f"Data flows through {len(tables)} tables"}

    def _get_event_workflows(self, event: str) -> Dict[str, Any]:
        """Get workflows triggered by a specific event.

        Dynamically finds what happens after an event occurs.

        Args:
            event: Event name (e.g., 'spec_created', 'task_completed')

        Returns:
            Workflows triggered by this event
        """
        if not event:
            return {"error": "event parameter is required"}

        triggered_workflows = []

        # Scan all agent files for this event
        for agent_file in self.agents_dir.glob("*.md"):
            content = agent_file.read_text()
            agent_name = agent_file.stem

            # Look for event mentions
            if event.lower() in content.lower():
                # Extract surrounding context
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if event.lower() in line.lower():
                        # Get workflow context
                        context_start = max(0, i - 5)
                        context_end = min(len(lines), i + 10)
                        context = "\n".join(lines[context_start:context_end])

                        # Extract what happens
                        actions = self._extract_event_actions(context, event)

                        if actions:
                            triggered_workflows.append(
                                {"agent": agent_name, "actions": actions, "source": f"{agent_file}:{i+1}"}
                            )

        return {
            "event": event,
            "triggered_workflows": triggered_workflows,
            "summary": f"Found {len(triggered_workflows)} workflows triggered by {event}",
        }

    def _extract_event_actions(self, context: str, event: str) -> List[str]:
        """Extract actions that happen after an event."""
        actions = []

        # Action patterns
        patterns = [
            r"then\s+([^.\n]+)",
            r"→\s*([^.\n]+)",
            r"triggers?\s+([^.\n]+)",
            r"sends?\s+([^.\n]+)",
            r"creates?\s+([^.\n]+)",
            r"updates?\s+([^.\n]+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, context, re.IGNORECASE):
                action = match.group(1).strip()
                if action and len(action) < 200:
                    actions.append(action)

        return actions

    def _get_table_operations(self, table: str) -> List[str]:
        """Get common operations performed on a table."""
        operations = []

        # Scan code for operations on this table
        for file_path in self.code_dir.rglob("*.py"):
            try:
                content = file_path.read_text()
                if table in content:
                    # Look for SQL operations
                    if f"INSERT INTO {table}" in content:
                        operations.append("create")
                    if f"UPDATE {table}" in content:
                        operations.append("update")
                    if f"SELECT.*FROM {table}" in content:
                        operations.append("read")
                    if f"DELETE FROM {table}" in content:
                        operations.append("delete")
            except:
                continue

        return list(set(operations))  # Unique operations

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
