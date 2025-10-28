---
name: claude-config-analyzer
version: 1.0.0
agent: shared
scope: shared
description: Dynamic analyzer that introspects .claude directory to extract agent configurations, skills, roles, and responsibilities - no hardcoded documentation
triggers:
  - "understanding agent setup"
  - "analyzing claude configuration"
  - "finding agent responsibilities"
  - "mapping agent interactions"
  - "discovering available skills"
requires: []
---

# Claude Configuration Analyzer Skill

This skill dynamically analyzes the `.claude` directory to provide real-time insights about agent configurations, skills, roles, and interactions through pure introspection.

## Purpose

**No hardcoded documentation** - This skill extracts information directly from:
- Agent markdown files in `.claude/agents/`
- Skill definitions in `.claude/skills/`
- Command definitions in `.claude/commands/`
- Actual code patterns and usage

## Key Features

### 1. Agent Discovery
- Lists all agents with their metadata
- Identifies active vs inactive agents
- Extracts agent summaries and descriptions

### 2. Skill Analysis
- Finds skills actually mentioned in agent prompts
- Verifies skill existence
- Maps skill usage across agents

### 3. Responsibility Extraction
- Parses agent mission statements
- Identifies numbered responsibility lists
- Extracts workflow definitions

### 4. Interaction Mapping
- Discovers agent-to-agent communications
- Maps delegation patterns
- Identifies dependencies

## Usage

```python
from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

# Load the analyzer
analyzer = load_skill(SkillNames.CLAUDE_CONFIG_ANALYZER)

# Get overview of all agents
agents = analyzer.execute(action="get_all_agents")
# Returns: List of agents with metadata, summaries, and active status

# Analyze specific agent
details = analyzer.execute(action="get_agent_details", agent="architect")
# Returns: Complete analysis including:
# - Skills used (with verification)
# - Workflows defined
# - Responsibilities
# - Database tables accessed
# - File ownership
# - Agent interactions

# Get agent's actual skills
skills = analyzer.execute(action="get_agent_skills", agent="architect")
# Returns: Skills mentioned in prompt with existence verification

# Extract responsibilities
resp = analyzer.execute(action="get_agent_responsibilities", agent="code_developer")
# Returns: Role, responsibilities, workflows, file ownership, database access

# Map skill usage across agents
usage = analyzer.execute(action="get_skill_usage")
# Returns: Which agents use which skills

# Analyze agent interactions
interactions = analyzer.execute(action="get_agent_interactions", agent="architect")
# Returns: Who agent communicates with and how

# Get complete Claude configuration overview
overview = analyzer.execute(action="get_claude_overview")
# Returns: Complete analysis of agents, skills, commands, and interactions
```

## Available Actions

### `get_all_agents`
Lists all agents found in `.claude/agents/` with metadata.

**Returns:**
```python
{
    "agents": {
        "architect": {
            "file": ".claude/agents/architect.md",
            "metadata": {...},
            "summary": "You are architect, the technical design authority...",
            "active": True
        },
        ...
    },
    "total": 7,
    "active": 6
}
```

### `get_agent_details`
Comprehensive analysis of a specific agent.

**Parameters:**
- `agent` (required): Agent name

**Returns:**
```python
{
    "name": "architect",
    "skills": [
        {"name": "DATABASE_SCHEMA_GUIDE", "type": "loaded", "exists": True},
        {"name": "architecture-reuse-check", "type": "referenced", "exists": True}
    ],
    "workflows": [
        {"number": "1", "title": "Creating Technical Specifications"},
        {"number": "2", "title": "Analyzing Dependencies"}
    ],
    "responsibilities": [
        "Create technical specifications BEFORE code_developer implements",
        "Document architectural decisions in ADRs",
        "Manage dependencies with user approval"
    ],
    "database_tables": ["roadmap_priority", "technical_specs"],
    "interactions": {
        "sends_to": ["code_developer"],
        "receives_from": ["project_manager"],
        "delegates_to": [],
        "notifies": ["assistant"]
    }
}
```

### `get_agent_skills`
Skills actually used by an agent (not just documented).

**Parameters:**
- `agent` (required): Agent name

**Returns:**
```python
{
    "agent": "architect",
    "skills": [
        {
            "name": "DATABASE_SCHEMA_GUIDE",
            "type": "loaded",  # loaded/referenced/executed
            "context": "load_skill(SkillNames.DATABASE_SCHEMA_GUIDE)",
            "exists": True  # Verified to exist in .claude/skills/
        }
    ],
    "total": 5,
    "verified": 4  # How many actually exist
}
```

### `get_agent_responsibilities`
Extract role and responsibilities.

**Parameters:**
- `agent` (required): Agent name

**Returns:**
```python
{
    "agent": "code_developer",
    "role": "You are code_developer, the autonomous implementation agent...",
    "responsibilities": [
        "Implement priorities from ROADMAP.md autonomously",
        "Run tests and ensure code quality",
        "Commit changes to roadmap branch"
    ],
    "workflows": [...],
    "file_ownership": {
        "owns": ["coffee_maker/", "tests/"],
        "writes": [],
        "reads": ["docs/architecture/specs/"]
    },
    "database_access": ["roadmap_priority", "implementation_tasks"]
}
```

### `get_skill_usage`
Map which agents use which skills.

**Returns:**
```python
{
    "skills": {
        "DATABASE_SCHEMA_GUIDE": {
            "agents": ["architect", "code_developer"],
            "type": "loaded",
            "exists": True
        },
        ...
    },
    "total_skills": 15,
    "summary": {
        "most_used": "DATABASE_SCHEMA_GUIDE"
    }
}
```

### `get_agent_interactions`
How agents communicate with each other.

**Parameters:**
- `agent` (optional): Specific agent or all interactions

**Returns:**
```python
{
    "agent": "architect",
    "interactions": {
        "sends_to": ["code_developer", "project_manager"],
        "receives_from": ["user_listener"],
        "delegates_to": [],
        "notifies": ["assistant"]
    },
    "dependencies": ["project_manager", "user_listener"]
}
```

### `get_claude_overview`
Complete analysis of `.claude` configuration.

**Returns:**
```python
{
    "agents": {...},      # All agents
    "skills": {...},      # All skills
    "commands": {...},    # All commands
    "skill_usage": {...}, # Skill-to-agent mapping
    "interactions": {...}, # Agent interactions
    "summary": {
        "total_agents": 7,
        "active_agents": 6,
        "total_skills": 25,
        "total_commands": 10,
        "total_interactions": 15,
        "most_connected_agent": "architect"
    }
}
```

## Use Cases for Architect

1. **Before creating specs**: Understand which agents will implement
2. **Designing workflows**: See current agent interactions
3. **Adding features**: Check which skills are available
4. **Refactoring**: Identify unused skills or duplicate responsibilities

## Use Cases for Code Developer

1. **Finding examples**: See which agents use similar patterns
2. **Understanding context**: Know who depends on your code
3. **Testing**: Understand agent interactions to test

## Benefits

- **Always current**: Reads actual files, not documentation
- **No maintenance**: Automatically discovers changes
- **Comprehensive**: Combines metadata, content analysis, and pattern matching
- **Verified**: Checks if referenced skills actually exist
