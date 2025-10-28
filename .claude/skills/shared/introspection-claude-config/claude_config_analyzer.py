"""Claude Configuration Analyzer Skill.

Dynamically analyzes the .claude directory to extract:
- All agents and their configurations
- Skills actually used by each agent
- Agent roles and responsibilities
- Agent interactions and dependencies

This is pure introspection - no hardcoded documentation.
"""

import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.skill_loader import BaseSkill


class ClaudeConfigAnalyzer(BaseSkill):
    """Dynamic analyzer for Claude configuration and agent setup."""

    def __init__(self):
        """Initialize the analyzer."""
        super().__init__()
        self.claude_dir = Path(".claude")
        self.agents_dir = self.claude_dir / "agents"
        self.skills_dir = self.claude_dir / "skills"
        self.commands_dir = self.claude_dir / "commands"

        # Cache for performance
        self._agent_cache = {}
        self._skill_cache = {}
        self._command_cache = {}

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute analyzer action.

        Available actions:
        - get_all_agents: List all agents with their metadata
        - get_agent_details: Detailed analysis of specific agent
        - get_agent_skills: Skills actually used by an agent
        - get_agent_responsibilities: Extract role and responsibilities
        - get_skill_usage: Which agents use which skills
        - get_agent_interactions: How agents communicate
        - get_claude_overview: Complete .claude directory analysis
        """
        if action == "get_all_agents":
            return self._get_all_agents()
        elif action == "get_agent_details":
            return self._get_agent_details(kwargs.get("agent"))
        elif action == "get_agent_skills":
            return self._get_agent_skills(kwargs.get("agent"))
        elif action == "get_agent_responsibilities":
            return self._get_agent_responsibilities(kwargs.get("agent"))
        elif action == "get_skill_usage":
            return self._get_skill_usage()
        elif action == "get_agent_interactions":
            return self._get_agent_interactions(kwargs.get("agent"))
        elif action == "get_claude_overview":
            return self._get_claude_overview()
        else:
            return {"error": f"Unknown action: {action}"}

    def _get_all_agents(self) -> Dict[str, Any]:
        """Extract all agents from .claude/agents/ directory."""
        agents = {}

        if not self.agents_dir.exists():
            return {"error": "No .claude/agents directory found"}

        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem

            # Skip non-agent files
            if agent_name in ["README", "ARCHITECT_PROGRESSIVE_WORKFLOW"]:
                continue

            # Extract agent metadata
            content = agent_file.read_text()
            metadata = self._extract_agent_metadata(content)

            agents[agent_name] = {
                "file": str(agent_file),
                "metadata": metadata,
                "summary": self._extract_agent_summary(content),
                "active": self._is_agent_active(content),
            }

        return {"agents": agents, "total": len(agents), "active": sum(1 for a in agents.values() if a["active"])}

    def _extract_agent_metadata(self, content: str) -> Dict[str, str]:
        """Extract YAML frontmatter from agent file."""
        metadata = {}

        # Look for YAML frontmatter
        yaml_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if yaml_match:
            try:
                yaml_content = yaml_match.group(1)
                metadata = yaml.safe_load(yaml_content) or {}
            except:
                pass

        return metadata

    def _extract_agent_summary(self, content: str) -> str:
        """Extract the first meaningful description of the agent."""
        # Look for mission/role statement
        patterns = [
            r"You are[^.]+\.",
            r"Your mission is[^.]+\.",
            r"\*\*Role\*\*:[^.]+\.",
            r"## Agent Identity\n\n([^.]+\.)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                summary = match.group(0) if "(" not in pattern else match.group(1)
                return summary.strip()

        return "No summary found"

    def _is_agent_active(self, content: str) -> bool:
        """Check if agent is marked as active."""
        return "Status**: Active" in content or "status: active" in content.lower()

    def _get_agent_details(self, agent: str) -> Dict[str, Any]:
        """Get comprehensive details about a specific agent."""
        if not agent:
            return {"error": "agent parameter required"}

        agent_file = self.agents_dir / f"{agent}.md"
        if not agent_file.exists():
            return {"error": f"Agent '{agent}' not found"}

        content = agent_file.read_text()

        details = {
            "name": agent,
            "file": str(agent_file),
            "metadata": self._extract_agent_metadata(content),
            "summary": self._extract_agent_summary(content),
            "skills": self._extract_skills_from_content(content),
            "workflows": self._extract_workflows_from_content(content),
            "responsibilities": self._extract_responsibilities(content),
            "dependencies": self._extract_dependencies(content),
            "commands": self._extract_commands(content),
            "database_tables": self._extract_database_usage(content),
            "file_ownership": self._extract_file_ownership(content),
            "interactions": self._extract_agent_interactions_from_content(content),
        }

        return details

    def _extract_skills_from_content(self, content: str) -> List[Dict[str, str]]:
        """Extract skills actually mentioned/used in agent prompt."""
        skills = []

        # Pattern 1: load_skill(SkillNames.XXX)
        skill_load_pattern = r"load_skill\((?:SkillNames\.)?([A-Z_]+)\)"
        for match in re.finditer(skill_load_pattern, content):
            skill_name = match.group(1)
            skills.append({"name": skill_name, "type": "loaded", "context": match.group(0)})

        # Pattern 2: skill references in .claude/skills/
        skill_ref_pattern = r"\.claude/skills/(?:shared/)?([a-z_-]+)"
        for match in re.finditer(skill_ref_pattern, content):
            skill_name = match.group(1)
            if skill_name not in ["shared", "architect", "project_manager"]:
                skills.append({"name": skill_name, "type": "referenced", "path": match.group(0)})

        # Pattern 3: execute_skill or skill.execute
        execute_pattern = r'(?:execute_skill|skill\.execute)\(["\']?([a-z_-]+)'
        for match in re.finditer(execute_pattern, content):
            skill_name = match.group(1)
            skills.append({"name": skill_name, "type": "executed", "context": match.group(0)})

        # Deduplicate by name
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill["name"] not in seen:
                seen.add(skill["name"])
                unique_skills.append(skill)

        return unique_skills

    def _extract_workflows_from_content(self, content: str) -> List[Dict[str, str]]:
        """Extract workflow definitions from agent content."""
        workflows = []

        # Find workflow sections
        workflow_pattern = r"### Workflow (\d+):\s*([^\n]+)"
        for match in re.finditer(workflow_pattern, content):
            workflow_num = match.group(1)
            workflow_title = match.group(2).strip()
            workflows.append({"number": workflow_num, "title": workflow_title, "type": "documented"})

        # Find workflow methods in code examples
        method_pattern = r"def\s+(\w*workflow\w+)\("
        for match in re.finditer(method_pattern, content, re.IGNORECASE):
            method_name = match.group(1)
            workflows.append({"name": method_name, "type": "code_example"})

        return workflows

    def _extract_responsibilities(self, content: str) -> List[str]:
        """Extract agent responsibilities from content."""
        responsibilities = []

        # Look for responsibility sections
        patterns = [
            r"Your mission is to:\n((?:^\d+\..*$\n?)+)",
            r"Responsibilities:\n((?:^[-*].*$\n?)+)",
            r"You are responsible for:\n((?:^[-*].*$\n?)+)",
            r"Core responsibilities:\n((?:^[-*].*$\n?)+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                resp_text = match.group(1)
                # Extract individual items
                items = re.findall(r"^[\d\-\*]+\.?\s*(.+)$", resp_text, re.MULTILINE)
                responsibilities.extend(items)

        # Also look for numbered lists after "mission" or "role"
        mission_pattern = r"(?:mission|role)[^\n]*:\n+((?:^\d+\..*$\n?)+)"
        match = re.search(mission_pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            items = re.findall(r"^\d+\.\s*(.+)$", match.group(1), re.MULTILINE)
            responsibilities.extend(items)

        # Deduplicate and clean
        unique_responsibilities = []
        seen = set()
        for resp in responsibilities:
            clean_resp = resp.strip()
            if clean_resp and clean_resp not in seen:
                seen.add(clean_resp)
                unique_responsibilities.append(clean_resp)

        return unique_responsibilities

    def _extract_dependencies(self, content: str) -> Dict[str, List[str]]:
        """Extract what this agent depends on."""
        dependencies = {"agents": [], "skills": [], "databases": [], "files": []}

        # Agent dependencies
        agent_pattern = r"(?:delegates? to|receives? from|waits? for|depends? on)\s+([a-z_]+)"
        for match in re.finditer(agent_pattern, content, re.IGNORECASE):
            agent_name = match.group(1)
            if agent_name not in ["the", "a", "an"] and "_" in agent_name:
                dependencies["agents"].append(agent_name)

        # Database dependencies
        db_pattern = r"(?:reads? from|writes? to|queries?)\s+(\w+)(?:_\w+)*\s+(?:table|database)"
        for match in re.finditer(db_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            dependencies["databases"].append(table_name)

        # File dependencies
        file_pattern = r"(?:reads?|loads?|parses?)\s+([/\w]+\.\w+)"
        for match in re.finditer(file_pattern, content, re.IGNORECASE):
            file_path = match.group(1)
            dependencies["files"].append(file_path)

        # Deduplicate
        for key in dependencies:
            dependencies[key] = list(set(dependencies[key]))

        return dependencies

    def _extract_commands(self, content: str) -> List[str]:
        """Extract commands this agent responds to."""
        commands = []

        # Look for command patterns
        command_patterns = [
            r"/([a-z-]+)",  # Slash commands
            r"poetry run ([a-z-]+)",  # Poetry commands
            r'command["\']:\s*["\']([a-z-]+)',  # Command definitions
        ]

        for pattern in command_patterns:
            for match in re.finditer(pattern, content):
                command = match.group(1)
                if command and len(command) > 2:  # Filter out short matches
                    commands.append(command)

        return list(set(commands))

    def _extract_database_usage(self, content: str) -> List[str]:
        """Extract database tables this agent uses."""
        tables = []

        # SQL patterns
        sql_patterns = [
            r"(?:FROM|INTO|UPDATE)\s+(\w+)",
            r"(\w+_\w+)\s+table",
            r'table["\']:\s*["\'](\w+)',
        ]

        for pattern in sql_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                table = match.group(1)
                if table.lower() not in ["the", "a", "an", "table"]:
                    tables.append(table)

        return list(set(tables))

    def _extract_file_ownership(self, content: str) -> Dict[str, List[str]]:
        """Extract files/directories this agent owns."""
        ownership = {"writes": [], "reads": [], "owns": []}

        # Ownership patterns
        own_pattern = r"(?:owns?|modifies?|creates?)\s+([/\w]+(?:/\w+)*)"
        for match in re.finditer(own_pattern, content, re.IGNORECASE):
            path = match.group(1)
            if "/" in path:
                ownership["owns"].append(path)

        # Document ownership section
        doc_pattern = r"Document Ownership.*?\n((?:^[-*\d].*$\n?)+)"
        match = re.search(doc_pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            items = re.findall(r"`([^`]+)`", match.group(1))
            ownership["owns"].extend(items)

        # Deduplicate
        for key in ownership:
            ownership[key] = list(set(ownership[key]))

        return ownership

    def _extract_agent_interactions_from_content(self, content: str) -> Dict[str, List[str]]:
        """Extract how this agent interacts with others."""
        interactions = {"sends_to": [], "receives_from": [], "delegates_to": [], "notifies": []}

        # Interaction patterns
        patterns = {
            "sends_to": r"send(?:s|ing)?\s+(?:message\s+)?to\s+(\w+)",
            "receives_from": r"receiv(?:es?|ing)\s+(?:from\s+)?(\w+)",
            "delegates_to": r"delegat(?:es?|ing)\s+to\s+(\w+)",
            "notifies": r"notif(?:y|ies|ying)\s+(\w+)",
        }

        for interaction_type, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                agent = match.group(1)
                if agent not in ["the", "user", "it"] and "_" in agent:
                    interactions[interaction_type].append(agent)

        # Deduplicate
        for key in interactions:
            interactions[key] = list(set(interactions[key]))

        return interactions

    def _get_agent_skills(self, agent: str) -> Dict[str, Any]:
        """Get skills actually used by a specific agent."""
        if not agent:
            return {"error": "agent parameter required"}

        details = self._get_agent_details(agent)
        if "error" in details:
            return details

        skills = details["skills"]

        # Verify skills actually exist
        verified_skills = []
        for skill in skills:
            skill_name = skill["name"].lower().replace("_", "-")
            skill_paths = [
                self.skills_dir / "shared" / skill_name,
                self.skills_dir / agent / skill_name,
                self.skills_dir / f"{skill_name}.md",
            ]

            exists = any(path.exists() for path in skill_paths)
            skill["exists"] = exists
            verified_skills.append(skill)

        return {
            "agent": agent,
            "skills": verified_skills,
            "total": len(verified_skills),
            "verified": sum(1 for s in verified_skills if s["exists"]),
        }

    def _get_agent_responsibilities(self, agent: str) -> Dict[str, Any]:
        """Extract role and responsibilities for an agent."""
        if not agent:
            return {"error": "agent parameter required"}

        details = self._get_agent_details(agent)
        if "error" in details:
            return details

        return {
            "agent": agent,
            "role": details["summary"],
            "responsibilities": details["responsibilities"],
            "workflows": details["workflows"],
            "file_ownership": details["file_ownership"],
            "database_access": details["database_tables"],
        }

    def _get_skill_usage(self) -> Dict[str, Any]:
        """Map which agents use which skills."""
        skill_usage = {}

        # Get all agents
        all_agents = self._get_all_agents()

        for agent_name in all_agents["agents"]:
            agent_skills = self._get_agent_skills(agent_name)

            for skill in agent_skills.get("skills", []):
                skill_name = skill["name"]

                if skill_name not in skill_usage:
                    skill_usage[skill_name] = {
                        "agents": [],
                        "type": skill["type"],
                        "exists": skill.get("exists", False),
                    }

                skill_usage[skill_name]["agents"].append(agent_name)

        return {
            "skills": skill_usage,
            "total_skills": len(skill_usage),
            "summary": {
                "most_used": max(skill_usage.items(), key=lambda x: len(x[1]["agents"]))[0] if skill_usage else None
            },
        }

    def _get_agent_interactions(self, agent: Optional[str] = None) -> Dict[str, Any]:
        """Map agent-to-agent interactions."""
        if agent:
            # Get interactions for specific agent
            details = self._get_agent_details(agent)
            if "error" in details:
                return details

            return {
                "agent": agent,
                "interactions": details["interactions"],
                "dependencies": details["dependencies"]["agents"],
            }
        else:
            # Get all agent interactions
            all_interactions = {}
            all_agents = self._get_all_agents()

            for agent_name in all_agents["agents"]:
                details = self._get_agent_details(agent_name)
                interactions = details["interactions"]

                for interaction_type, targets in interactions.items():
                    for target in targets:
                        key = f"{agent_name} -> {target}"
                        if key not in all_interactions:
                            all_interactions[key] = []
                        all_interactions[key].append(interaction_type)

            return {"interactions": all_interactions, "total": len(all_interactions)}

    def _get_claude_overview(self) -> Dict[str, Any]:
        """Get complete overview of .claude configuration."""
        overview = {
            "agents": self._get_all_agents(),
            "skills": self._get_all_skills(),
            "commands": self._get_all_commands(),
            "skill_usage": self._get_skill_usage(),
            "interactions": self._get_agent_interactions(),
            "summary": {},
        }

        # Calculate summary statistics
        overview["summary"] = {
            "total_agents": overview["agents"]["total"],
            "active_agents": overview["agents"]["active"],
            "total_skills": overview["skills"]["total"],
            "total_commands": overview["commands"]["total"],
            "total_interactions": overview["interactions"]["total"],
            "most_connected_agent": self._find_most_connected_agent(overview["interactions"]),
        }

        return overview

    def _get_all_skills(self) -> Dict[str, Any]:
        """List all skills in .claude/skills/."""
        skills = {}

        if not self.skills_dir.exists():
            return {"skills": {}, "total": 0}

        # Find all skill directories and files
        for skill_path in self.skills_dir.rglob("*"):
            if skill_path.is_dir() and skill_path.name not in ["__pycache__", "."]:
                skill_name = skill_path.name
                skills[skill_name] = {
                    "path": str(skill_path),
                    "type": "directory",
                    "has_skill_md": (skill_path / "SKILL.md").exists(),
                    "has_python": any(skill_path.glob("*.py")),
                }
            elif skill_path.suffix == ".md" and skill_path.stem != "README":
                skill_name = skill_path.stem
                skills[skill_name] = {"path": str(skill_path), "type": "markdown"}

        return {"skills": skills, "total": len(skills)}

    def _get_all_commands(self) -> Dict[str, Any]:
        """List all commands in .claude/commands/."""
        commands = {}

        if not self.commands_dir.exists():
            return {"commands": {}, "total": 0}

        for command_file in self.commands_dir.glob("*.md"):
            command_name = command_file.stem
            content = command_file.read_text()

            # Extract command description if available
            first_line = content.split("\n")[0] if content else ""

            commands[command_name] = {"file": str(command_file), "description": first_line.strip("#").strip()}

        return {"commands": commands, "total": len(commands)}

    def _find_most_connected_agent(self, interactions: Dict) -> str:
        """Find the agent with most connections."""
        connection_count = {}

        for connection in interactions.get("interactions", {}):
            agents = connection.split(" -> ")
            for agent in agents:
                agent = agent.strip()
                connection_count[agent] = connection_count.get(agent, 0) + 1

        if connection_count:
            return max(connection_count.items(), key=lambda x: x[1])[0]
        return "None"
