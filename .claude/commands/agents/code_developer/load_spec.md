---
command: code_developer.load_spec
agent: code_developer
action: load_spec
tables:
  read: [specs_specification, specs_task]
required_skills: [technical_specification_handling]
required_tools: [database]
---

# Command: code_developer.load_spec

## Purpose
Load specification content for current implementation phase using progressive disclosure to respect context budget (CFR-007).

## Input Parameters

```yaml
spec_id: string          # Required - Spec to load (e.g., "SPEC-131")
task_id: string          # Optional - Specific task (loads only needed sections)
phase: string            # Optional - Specific phase (for hierarchical specs)
full_content: boolean    # Load entire spec (default: false, CFR-007)
```

## Database Operations

### 1. Read Spec from Database
```python
import json
from datetime import datetime

def load_spec(db: DomainWrapper, params: dict):
    spec_id = params["spec_id"]

    # Get spec from database (NOT from files)
    specs = db.read("specs_specification", {"id": spec_id})
    if not specs:
        return {"success": False, "error": f"Spec {spec_id} not found"}

    spec = specs[0]

    # Parse spec content from database
    if isinstance(spec["content"], str):
        content_json = json.loads(spec["content"])
    else:
        content_json = spec["content"]
```

### 2. Determine Content to Load (Progressive Disclosure)
```python
    # Determine what to load based on parameters
    if params.get("full_content", False):
        # Load everything (use sparingly - CFR-007 violation!)
        loaded_sections = list(content_json.keys())
        content = content_json

    elif params.get("task_id"):
        # Load sections needed for specific task only
        tasks = db.read("specs_task", {"id": params["task_id"]})
        if not tasks:
            return {"success": False, "error": f"Task {params['task_id']} not found"}

        task = tasks[0]
        spec_sections = json.loads(task.get("spec_sections", "[]"))

        # Always include overview + requested sections
        loaded_sections = ["overview"] + spec_sections
        content = {
            k: content_json[k]
            for k in loaded_sections
            if k in content_json
        }

    elif params.get("phase"):
        # Load specific phase (for hierarchical specs)
        if spec.get("spec_type") == "hierarchical":
            phases = content_json.get("phases", [])
            phase_data = next(
                (p for p in phases if p.get("name") == params["phase"]),
                None
            )

            if not phase_data:
                return {
                    "success": False,
                    "error": f"Phase {params['phase']} not found"
                }

            # Load overview + architecture + specific phase
            loaded_sections = ["overview", "architecture", params["phase"]]
            content = {
                "overview": content_json.get("overview", ""),
                "architecture": content_json.get("architecture", ""),
                "phase_content": phase_data.get("content", "")
            }
        else:
            return {
                "success": False,
                "error": "Phase loading only for hierarchical specs"
            }

    else:
        # Default: Load overview + first phase only
        loaded_sections = ["overview"]
        content = {"overview": content_json.get("overview", "")}
```

### 3. Calculate Context Tokens
```python
    # Estimate context tokens used (rough calculation)
    content_str = json.dumps(content)
    context_tokens = len(content_str) // 4  # Rough estimate: ~4 chars per token

    # Verify CFR-007 compliance (should be <30% of context budget)
    # 200k tokens * 30% = 60k tokens max
    if context_tokens > 60000:
        return {
            "success": False,
            "error": f"Content too large for context budget: {context_tokens} tokens",
            "recommendation": "Load specific sections or reduce scope"
        }
```

### 4. Extract Reuse Components
```python
    # Extract reuse components from spec for efficiency
    reuse_components = content_json.get("reuse_components", [])
```

### 5. Return Results
```python
    return {
        "success": True,
        "spec_id": spec_id,
        "spec_type": spec.get("spec_type", "monolithic"),
        "loaded_sections": loaded_sections,
        "content": content,
        "context_tokens": context_tokens,
        "estimated_hours": spec.get("estimated_hours", 0),
        "reuse_components": reuse_components,
        "loaded_at": datetime.now().isoformat()
    }
```

## Output

```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "spec_type": "hierarchical",
  "loaded_sections": ["overview", "implementation", "phase_1"],
  "content": {
    "overview": "...",
    "implementation": "...",
    "phase_1": "..."
  },
  "context_tokens": 2500,
  "estimated_hours": 8.0,
  "reuse_components": [
    {
      "component": "ConfigManager",
      "location": "SPEC-120",
      "fitness": 85
    }
  ]
}
```

## Success Criteria

- ✅ Only needed sections loaded (CFR-007)
- ✅ Context budget <30% (verified in function)
- ✅ Hierarchical specs load progressively
- ✅ Reuse components highlighted
- ✅ Dependencies documented
- ✅ Spec read from DATABASE (not files)

## Critical Notes

### Database-First Implementation
- ALWAYS read specs from `specs_specification` table
- NEVER read spec files directly from filesystem
- Spec content stored in `content` column as JSON
- Content may be monolithic (single file) or hierarchical (phases)

### Progressive Disclosure (CFR-007)
- Default load: overview only (~500 tokens)
- Task-specific: overview + required sections (~1500 tokens)
- Full load: entire spec (avoid except debugging)
- Context budget: <30% of 200k = 60k tokens max per task

### Hierarchical Spec Format
```json
{
  "overview": "Executive summary",
  "architecture": "System design",
  "phases": [
    {
      "name": "database",
      "content": "Database schema design",
      "estimated_hours": 4
    },
    {
      "name": "implementation",
      "content": "Implementation tasks",
      "estimated_hours": 8
    }
  ]
}
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| SpecNotFoundError | Spec doesn't exist | Verify spec ID |
| InvalidPhaseError | Phase doesn't exist | Check phase names |
| TaskNotFoundError | Task ID invalid | Verify task ID |
| ContextBudgetExceeded | Content too large | Load sections instead |

## Usage Examples

### Load Overview Only (Default)
```python
result = load_spec(db, {
    "spec_id": "SPEC-131"
})
# Returns: overview section only (~500 tokens)
```

### Load Sections for Specific Task
```python
result = load_spec(db, {
    "spec_id": "SPEC-131",
    "task_id": "TASK-31-1"
})
# Returns: overview + task's required sections (~1500 tokens)
```

### Load Specific Phase
```python
result = load_spec(db, {
    "spec_id": "SPEC-131",
    "phase": "implementation"
})
# Returns: overview + architecture + implementation phase (~2000 tokens)
```

### Load Everything (Full Spec)
```python
result = load_spec(db, {
    "spec_id": "SPEC-131",
    "full_content": True
})
# Returns: entire spec (use sparingly!)
```

## Integration with Code Developer

After loading spec, code_developer:
1. Reviews loaded sections to understand scope
2. Creates implementation plan based on content
3. Writes code following spec requirements
4. Tests against spec acceptance criteria
5. Requests review when complete

This progressive loading enables code_developer to stay within CFR-007 context budget while maintaining complete implementation details.
