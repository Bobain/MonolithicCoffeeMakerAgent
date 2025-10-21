# Skill: ROADMAP Management

**Name**: `roadmap-management`
**Owner**: ALL agents (project_manager, code_developer, architect)
**Purpose**: Fast ROADMAP parsing and manipulation for autonomous agents
**Priority**: CRITICAL - Enables autonomous operation

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ code_developer: Find next priority to implement
- ✅ project_manager: Update priority status, add new priorities
- ✅ architect: Check if priority has technical spec
- ✅ ALL agents: Verify dependencies before starting work
- ✅ ALL agents: Calculate progress metrics

**Example Triggers**:
```python
# code_developer: Get next work item
next_priority = roadmap.get_next_planned_priority()

# architect: Check if spec exists
has_spec = roadmap.has_technical_spec("US-072")

# project_manager: Update status
roadmap.update_priority_status("PRIORITY 11", "In Progress")
```

---

## Skill Execution Steps

### Step 1: Parse ROADMAP.md

**Input**: Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)

**Actions**:
1. Read ROADMAP.md file
2. Extract all priorities with regex pattern: `^## PRIORITY (\d+(?:\.\d+)?): (.+) (📝|🔄|✅|⏸️|🚧)`
3. For each priority, extract:
   - **Number**: "11", "11.5", etc.
   - **Title**: Full priority title
   - **Status**: 📝 Planned, 🔄 In Progress, ✅ Complete, ⏸️ Blocked, 🚧 Manual Review
   - **US ID**: Extract "US-XXX" from title if present
   - **Description**: Content between priority header and next priority
   - **Dependencies**: Search for "Dependencies:" section
   - **Estimated Effort**: Search for "Estimated effort:" or "Time estimate:"
   - **Spec Link**: Search for "SPEC-" references or "docs/architecture/specs/"
   - **Strategic Spec**: Search for "PRIORITY_X_STRATEGIC_SPEC.md"

**Output**: Structured priority list

```python
priorities = [
    {
        "number": "11",
        "title": "US-072 - Design Orchestrator Agent Architecture",
        "status": "📝 Planned",
        "us_id": "US-072",
        "description": "...",
        "dependencies": ["PRIORITY 10"],
        "estimated_effort": "15-20 hours",
        "technical_spec": "docs/architecture/specs/SPEC-072-multi-agent-orchestration-daemon.md",
        "strategic_spec": None,
        "line_number": 111  # For fast updates
    }
]
```

### Step 2: Query Operations

**2.1 Get Next Planned Priority**

Find first priority with status "📝 Planned" whose dependencies are all "✅ Complete":

```python
def get_next_planned_priority():
    """Return next priority ready to implement."""
    for priority in priorities:
        if priority["status"] == "📝 Planned":
            # Check dependencies
            if all_dependencies_complete(priority["dependencies"]):
                return priority
    return None  # No work available
```

**2.2 Check Spec Readiness**

Verify if priority has technical specification:

```python
def check_spec_exists(us_id: str) -> bool:
    """Check if US has technical spec."""
    priority = find_priority_by_us_id(us_id)
    if not priority:
        return False

    # Check if technical_spec field is populated
    if priority["technical_spec"]:
        spec_path = Path(priority["technical_spec"])
        return spec_path.exists()

    # Fallback: Search for SPEC-XXX-*.md
    spec_pattern = f"docs/architecture/specs/SPEC-{us_id.split('-')[1]}-*.md"
    specs = glob(spec_pattern)
    return len(specs) > 0
```

**2.3 Get All Priorities Without Specs**

Find priorities that need specs (estimated effort >2 days, no spec yet):

```python
def get_priorities_without_specs():
    """Return priorities needing specs."""
    needs_specs = []

    for priority in priorities:
        # Skip completed priorities
        if priority["status"] == "✅ Complete":
            continue

        # Check estimated effort
        effort_hours = parse_effort_hours(priority["estimated_effort"])
        if effort_hours and effort_hours > 16:  # >2 days
            # Check if spec exists
            if not check_spec_exists(priority["us_id"]):
                needs_specs.append(priority)

    return needs_specs
```

**2.4 Check Dependencies**

Verify if priority's dependencies are met:

```python
def check_dependencies(priority_number: str) -> dict:
    """Check if dependencies are met.

    Returns:
        {
            "all_met": bool,
            "blocking": [list of blocking priorities],
            "pending": [list of pending priorities]
        }
    """
    priority = find_priority_by_number(priority_number)
    if not priority or not priority["dependencies"]:
        return {"all_met": True, "blocking": [], "pending": []}

    blocking = []
    pending = []

    for dep in priority["dependencies"]:
        dep_priority = find_priority_by_number(dep)
        if dep_priority:
            if dep_priority["status"] == "⏸️ Blocked":
                blocking.append(dep)
            elif dep_priority["status"] != "✅ Complete":
                pending.append(dep)

    return {
        "all_met": len(blocking) == 0 and len(pending) == 0,
        "blocking": blocking,
        "pending": pending
    }
```

**2.5 Calculate Progress**

Get completion metrics:

```python
def get_progress() -> dict:
    """Calculate ROADMAP progress."""
    total = len(priorities)
    completed = sum(1 for p in priorities if p["status"] == "✅ Complete")
    in_progress = sum(1 for p in priorities if p["status"] == "🔄 In Progress")
    planned = sum(1 for p in priorities if p["status"] == "📝 Planned")
    blocked = sum(1 for p in priorities if p["status"] == "⏸️ Blocked")

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "planned": planned,
        "blocked": blocked,
        "completion_percentage": (completed / total * 100) if total > 0 else 0
    }
```

### Step 3: Update Operations

**3.1 Update Priority Status**

Change priority status (Planned → In Progress → Complete):

```python
def update_priority_status(priority_number: str, new_status: str):
    """Update priority status in ROADMAP.md.

    Args:
        priority_number: "11", "11.5", etc.
        new_status: "📝 Planned", "🔄 In Progress", "✅ Complete", etc.

    Process:
        1. Read ROADMAP.md
        2. Find line with "## PRIORITY {number}:"
        3. Replace status emoji
        4. Write back to file (atomic write)
    """
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    content = roadmap_path.read_text(encoding="utf-8")

    # Regex to find and replace status
    pattern = rf"(## PRIORITY {re.escape(priority_number)}:.*?)(📝|🔄|✅|⏸️|🚧)"
    replacement = rf"\1{new_status}"

    updated_content = re.sub(pattern, replacement, content)

    # Atomic write
    from coffee_maker.utils.file_io import atomic_write
    atomic_write(roadmap_path, updated_content)
```

**3.2 Add New Priority**

Insert new priority in correct order:

```python
def add_new_priority(
    number: str,
    title: str,
    description: str,
    dependencies: list = None,
    estimated_effort: str = None,
    status: str = "📝 Planned"
):
    """Add new priority to ROADMAP.

    Args:
        number: "20", "19.5", etc.
        title: "US-XXX - Feature Name"
        description: Full priority description
        dependencies: ["PRIORITY 18", "PRIORITY 19"]
        estimated_effort: "10-15 hours"
        status: "📝 Planned" (default)

    Process:
        1. Find insertion point (after lower-numbered priorities)
        2. Generate priority section
        3. Insert into ROADMAP.md
        4. Write back to file
    """
    priority_section = f"""
## PRIORITY {number}: {title} {status}

**Estimated effort**: {estimated_effort or "TBD"}
**Status**: {status}

{description}
"""

    if dependencies:
        dep_str = ", ".join(dependencies)
        priority_section += f"\n**Dependencies**: {dep_str}\n"

    # Find insertion point
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    content = roadmap_path.read_text(encoding="utf-8")

    # Insert after last priority with number < new number
    insertion_point = find_insertion_point(content, number)
    updated_content = content[:insertion_point] + priority_section + content[insertion_point:]

    # Atomic write
    from coffee_maker.utils.file_io import atomic_write
    atomic_write(roadmap_path, updated_content)
```

### Step 4: Search Operations

**4.1 Find Priority by US ID**

```python
def find_priority_by_us_id(us_id: str) -> dict:
    """Find priority by US-XXX identifier."""
    for priority in priorities:
        if priority["us_id"] == us_id:
            return priority
    return None
```

**4.2 Find Priority by Number**

```python
def find_priority_by_number(number: str) -> dict:
    """Find priority by number (e.g., "11", "11.5")."""
    for priority in priorities:
        if priority["number"] == number:
            return priority
    return None
```

**4.3 Search Priorities by Keyword**

```python
def search_priorities(keyword: str) -> list:
    """Search priorities by keyword in title or description."""
    results = []
    keyword_lower = keyword.lower()

    for priority in priorities:
        if (keyword_lower in priority["title"].lower() or
            keyword_lower in priority["description"].lower()):
            results.append(priority)

    return results
```

---

## Integration with Agents

### code_developer Agent

```python
# coffee_maker/autonomous/agents/code_developer_agent.py

from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

class CodeDeveloperAgent(BaseAgent):
    def get_next_work_item(self):
        """Get next priority to implement."""
        skill = load_skill(SkillNames.ROADMAP_MANAGEMENT)

        # Use skill to find next planned priority
        next_priority = skill.get_next_planned_priority()

        if not next_priority:
            logger.info("No planned priorities available")
            return None

        # Check if spec exists
        if not skill.check_spec_exists(next_priority["us_id"]):
            logger.warning(f"Priority {next_priority['number']} missing spec, delegating to architect")
            self._delegate_to_architect(next_priority)
            return None

        # Update status to In Progress
        skill.update_priority_status(next_priority["number"], "🔄 In Progress")

        return next_priority
```

### architect Agent

```python
# coffee_maker/autonomous/agents/architect_agent.py

from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

class ArchitectAgent(BaseAgent):
    def find_priorities_needing_specs(self):
        """Find priorities that need technical specs."""
        skill = load_skill(SkillNames.ROADMAP_MANAGEMENT)

        # Get all priorities without specs
        needs_specs = skill.get_priorities_without_specs()

        logger.info(f"Found {len(needs_specs)} priorities needing specs")

        for priority in needs_specs:
            logger.info(f"  - {priority['number']}: {priority['title']}")

        return needs_specs

    def create_spec_for_priority(self, priority_number: str):
        """Create technical spec for priority."""
        skill = load_skill(SkillNames.ROADMAP_MANAGEMENT)

        priority = skill.find_priority_by_number(priority_number)
        if not priority:
            logger.error(f"Priority {priority_number} not found")
            return

        # Create spec using architect's normal workflow
        spec_content = self._generate_technical_spec(priority)
        spec_filename = f"docs/architecture/specs/SPEC-{priority['us_id'].split('-')[1]}-{priority['title']}.md"

        # Write spec file
        Path(spec_filename).write_text(spec_content, encoding="utf-8")

        logger.info(f"Created spec: {spec_filename}")
```

### project_manager Agent

```python
# coffee_maker/autonomous/agents/project_manager_agent.py

from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

class ProjectManagerAgent(BaseAgent):
    def get_roadmap_status(self):
        """Get ROADMAP progress metrics."""
        skill = load_skill(SkillNames.ROADMAP_MANAGEMENT)

        progress = skill.get_progress()

        status_report = f"""
ROADMAP Status:
  Total priorities: {progress['total']}
  Completed: {progress['completed']} ({progress['completion_percentage']:.1f}%)
  In Progress: {progress['in_progress']}
  Planned: {progress['planned']}
  Blocked: {progress['blocked']}
"""

        logger.info(status_report)
        return progress

    def add_critical_priority(self, title: str, description: str, urgent: bool = False):
        """Add new critical priority to ROADMAP."""
        skill = load_skill(SkillNames.ROADMAP_MANAGEMENT)

        # Find next available number
        all_priorities = skill.get_all_priorities()
        max_number = max(float(p["number"]) for p in all_priorities)
        new_number = str(int(max_number) + 1)

        # Add priority
        skill.add_new_priority(
            number=new_number,
            title=title,
            description=description,
            status="📝 Planned",
            estimated_effort="TBD"
        )

        logger.info(f"Added PRIORITY {new_number}: {title}")

        if urgent:
            # Notify user
            from coffee_maker.cli.notifications import NotificationSystem
            NotificationSystem.send_notification(
                "Critical Priority Added",
                f"PRIORITY {new_number}: {title}"
            )
```

---

## Skill Checklist (ALL Agents Must Complete)

Before starting work on a priority:

- [ ] ✅ Parse ROADMAP.md to get all priorities
- [ ] ✅ Find next planned priority (code_developer)
- [ ] ✅ Check if technical spec exists (architect)
- [ ] ✅ Verify dependencies are met
- [ ] ✅ Update status to "🔄 In Progress"
- [ ] ✅ After completion: Update status to "✅ Complete"
- [ ] ✅ If blocked: Update status to "⏸️ Blocked" with reason

**Failure to use ROADMAP management = Duplicate work, missed dependencies**

---

## Success Metrics

### Time Savings

**Before** (Manual ROADMAP parsing):
- Parse ROADMAP: 5-10 minutes
- Find next priority: 2-3 minutes
- Check dependencies: 3-5 minutes
- Update status: 1-2 minutes
- **Total**: 11-20 minutes per operation

**After** (With skill):
- Parse ROADMAP: <1 second
- Find next priority: <1 second
- Check dependencies: <1 second
- Update status: <1 second
- **Total**: <5 seconds per operation

**Savings**: 11-20 minutes → 5 seconds = 99.5% reduction

### Quality Improvements

- ✅ No manual errors (wrong priority, missed dependencies)
- ✅ Atomic updates (no file corruption)
- ✅ Consistent status tracking
- ✅ Fast dependency validation

---

## API Reference

### Core Functions

```python
# Query Operations
get_next_planned_priority() -> dict  # Find next work item
check_spec_exists(us_id: str) -> bool  # Check if spec exists
get_priorities_without_specs() -> list  # Find priorities needing specs
check_dependencies(priority_number: str) -> dict  # Verify dependencies
get_progress() -> dict  # Calculate completion metrics

# Update Operations
update_priority_status(priority_number: str, new_status: str)  # Change status
add_new_priority(number: str, title: str, description: str, ...)  # Add priority

# Search Operations
find_priority_by_us_id(us_id: str) -> dict  # Find by US-XXX
find_priority_by_number(number: str) -> dict  # Find by number
search_priorities(keyword: str) -> list  # Search by keyword

# Utility Operations
get_all_priorities() -> list  # Get all priorities
parse_effort_hours(effort_str: str) -> float  # Parse "10-15 hours" → 12.5
```

---

## Example Usage Scenarios

### Scenario 1: code_developer Starting Work

```python
# 1. Get next work item
roadmap = load_skill(SkillNames.ROADMAP_MANAGEMENT)
next_priority = roadmap.get_next_planned_priority()

if not next_priority:
    logger.info("No work available, sleeping...")
    return

# 2. Check if spec exists
if not roadmap.check_spec_exists(next_priority["us_id"]):
    logger.warning(f"Missing spec for {next_priority['us_id']}, delegating to architect")
    self._delegate_to_architect(next_priority)
    return

# 3. Update status
roadmap.update_priority_status(next_priority["number"], "🔄 In Progress")

# 4. Start implementation
self._implement_priority(next_priority)

# 5. After completion
roadmap.update_priority_status(next_priority["number"], "✅ Complete")
```

### Scenario 2: architect Identifying Work

```python
# 1. Find priorities without specs
roadmap = load_skill(SkillNames.ROADMAP_MANAGEMENT)
needs_specs = roadmap.get_priorities_without_specs()

# 2. Prioritize by effort (highest effort first)
needs_specs.sort(key=lambda p: parse_effort_hours(p["estimated_effort"]), reverse=True)

# 3. Create specs
for priority in needs_specs[:3]:  # Top 3
    logger.info(f"Creating spec for {priority['number']}: {priority['title']}")
    self.create_technical_spec(priority)
```

### Scenario 3: project_manager Adding Critical Priority

```python
# 1. Parse ROADMAP
roadmap = load_skill(SkillNames.ROADMAP_MANAGEMENT)

# 2. Add critical bug fix
roadmap.add_new_priority(
    number="20",
    title="US-104 - Fix Critical Authentication Bug",
    description="Users cannot log in after OAuth token expires...",
    estimated_effort="4-6 hours",
    dependencies=["PRIORITY 19"],
    status="📝 Planned"
)

# 3. Notify team
NotificationSystem.send_notification(
    "Critical Priority Added",
    "PRIORITY 20: Fix Critical Authentication Bug"
)
```

---

## Related Skills

- **roadmap-health-check**: project_manager analyzes ROADMAP health
- **architecture-reuse-check**: architect ensures quality specs
- **proactive-refactoring-analysis**: architect identifies technical debt

---

**Remember**: ROADMAP is the single source of truth for autonomous agents! 📋

**All Agents' Mantra**: "Read ROADMAP first, update ROADMAP always!"
