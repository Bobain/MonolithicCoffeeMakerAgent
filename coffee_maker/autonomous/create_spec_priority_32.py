#!/usr/bin/env python3
"""Create hierarchical technical specification for PRIORITY 32.

This spec defines how architect creates work_sessions for parallel development
through task decomposition and file dependency analysis.
"""

import json
import sqlite3
from datetime import datetime

from coffee_maker.autonomous.unified_database import get_unified_database

# Hierarchical spec content
spec_content = {
    "/overview": """
## Overview

Enable architect to decompose technical specifications into parallelizable work_sessions through:
1. Technical spec analysis and work unit identification
2. File dependency analysis to detect conflicts
3. work_session creation with non-overlapping assigned_files
4. Validation that ensures file independence

**Problem**: architect currently:
- Creates technical specs but doesn't decompose them into work units
- No file dependency analysis to identify parallelizable units
- No work_session creation (blocks code_developer parallelization)
- Cannot enable parallel development without work_sessions

**Solution**: Implement work-session-creator skill so architect can:
- Analyze hierarchical specs and identify natural work boundaries
- Perform static analysis to determine file dependencies
- Create work_sessions with assigned_files (validated no overlaps)
- Enable 2-3 code_developers to work in parallel

**Impact**: Unblocks parallel development pipeline, enables 2-3x velocity increase.
""",
    "/architecture": """
## Architecture

### Current Flow (No work_sessions)

```
architect creates technical spec
    ↓
Stores spec in database
    ↓
code_developer reads entire spec
    ↓
Implements all work sequentially
    ↓
Cannot parallelize (no work_sessions)
```

### New Flow (With work_sessions)

```
architect creates technical spec (SPEC-135)
    ↓
architect analyzes spec structure
    ↓
architect identifies work units:
  - Phase 1: /database_design → files: [unified_database.py]
  - Phase 2: /api_design → files: [api.py]
  - Phase 3: /testing → files: [tests/test_api.py]
    ↓
architect performs file dependency analysis
    ↓
architect validates NO file overlaps ✅
    ↓
architect creates 3 work_sessions in database:
  - WORK-135-1 (assigned_files: [unified_database.py])
  - WORK-135-2 (assigned_files: [api.py])
  - WORK-135-3 (assigned_files: [tests/test_api.py])
    ↓
orchestrator spawns 3 code_developers in parallel
    ↓
Each code_developer claims different work_session
    ↓
Parallel development enabled! ✅
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              architect Agent                                 │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  New Skill: work-session-creator                    │    │
│  │  - analyze_spec_structure(spec_id)                  │    │
│  │  - identify_work_units(spec_content)                │    │
│  │  - analyze_file_dependencies(work_unit)             │    │
│  │  - validate_file_independence(work_units)           │    │
│  │  - create_work_sessions(work_units)                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  Uses existing skills:                                       │
│  - code-searcher (find related code)                        │
│  - dependency-tracer (analyze imports)                      │
│  - unified-spec-skill (read hierarchical specs)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              unified_database.work_sessions                  │
│  Created entries:                                            │
│  - work_id, spec_id, scope, scope_description                │
│  - assigned_files (JSON array) ← KEY: No overlaps!          │
│  - branch_name, status='pending'                             │
└─────────────────────────────────────────────────────────────┘
```

### Work Unit Identification Strategies

#### Strategy 1: Phase-Based Decomposition (Recommended)

Analyze spec phases and create one work_session per phase:

```python
spec_phases = [
    "Phase 1: Database schema",
    "Phase 2: API implementation",
    "Phase 3: Testing"
]

# Map each phase to files
phase_1_files = ["coffee_maker/db/schema.py"]
phase_2_files = ["coffee_maker/api/endpoints.py"]
phase_3_files = ["tests/integration/test_api.py"]

# Validate no overlaps
assert no overlap between phase files

# Create 3 work_sessions
```

#### Strategy 2: Section-Based Decomposition

Analyze hierarchical spec sections:

```python
hierarchical_sections = {
    "/database_design": ["coffee_maker/db/models.py"],
    "/api_design": ["coffee_maker/api/routes.py"],
    "/implementation": ["coffee_maker/core/logic.py"],
    "/testing": ["tests/"]
}

# Create work_session per section
```

#### Strategy 3: Module-Based Decomposition

Analyze independent modules:

```python
modules = [
    {"name": "UserAuth", "files": ["coffee_maker/auth.py"]},
    {"name": "DataStore", "files": ["coffee_maker/storage.py"]},
    {"name": "API", "files": ["coffee_maker/api.py"]}
]

# Create work_session per module
```

### File Dependency Analysis

```python
# For each work unit, determine ALL files that will be touched

def analyze_file_dependencies(work_unit):
    \"\"\"Analyze file dependencies for work unit.

    Returns:
        List[str]: All files this work unit will modify
    \"\"\"
    files = []

    # 1. Explicitly mentioned files in spec
    files.extend(extract_file_mentions_from_spec(work_unit))

    # 2. Related test files
    for impl_file in files:
        test_file = derive_test_file_path(impl_file)
        if test_file:
            files.append(test_file)

    # 3. Files with import dependencies
    for file in files[:]:  # Iterate copy
        imported_files = find_imported_modules(file)
        files.extend(imported_files)

    # 4. Files that import this module
    for file in files[:]:
        reverse_imports = find_reverse_imports(file)
        files.extend(reverse_imports)

    return list(set(files))  # Deduplicate
```

### Conflict Detection Algorithm

```python
def validate_file_independence(work_units):
    \"\"\"Validate no file overlaps between work units.

    Raises:
        FileConflictError: If files overlap
    \"\"\"
    all_file_sets = [set(wu.assigned_files) for wu in work_units]

    # Check pairwise overlaps
    for i, files_1 in enumerate(all_file_sets):
        for j, files_2 in enumerate(all_file_sets):
            if i >= j:
                continue

            overlap = files_1 & files_2
            if overlap:
                raise FileConflictError(
                    f"Work units {i} and {j} have overlapping files: {overlap}"
                )

    return True  # All independent
```
""",
    "/api_design": """
## API Design

### work-session-creator Skill Interface

**Skill Location**: `.claude/skills/architect/work-session-creator/SKILL.md`

**Inputs**:
```json
{
  "spec_id": "SPEC-135",
  "roadmap_item_id": "PRIORITY-35",
  "granularity": "phase"  // or "section" or "module"
}
```

**Outputs**:
```json
{
  "work_sessions_created": 3,
  "work_sessions": [
    {
      "work_id": "WORK-135-1",
      "scope": "phase",
      "scope_description": "Phase 1: Database schema (/database_design)",
      "assigned_files": [
        "coffee_maker/autonomous/unified_database.py",
        "tests/unit/test_unified_database.py"
      ],
      "branch_name": "roadmap-work-135-1"
    },
    {
      "work_id": "WORK-135-2",
      "scope": "phase",
      "scope_description": "Phase 2: API implementation (/api_design, /implementation)",
      "assigned_files": [
        "coffee_maker/api/endpoints.py",
        "tests/unit/test_endpoints.py"
      ],
      "branch_name": "roadmap-work-135-2"
    },
    {
      "work_id": "WORK-135-3",
      "scope": "phase",
      "scope_description": "Phase 3: Testing (/test_strategy)",
      "assigned_files": [
        "tests/integration/test_full_workflow.py"
      ],
      "branch_name": "roadmap-work-135-3"
    }
  ],
  "validation": {
    "file_overlaps_detected": false,
    "parallelizable": true
  }
}
```

### Python API (Helper Functions)

```python
from typing import Dict, List, Any

def create_work_sessions_for_spec(
    spec_id: str,
    roadmap_item_id: str,
    granularity: str = "phase"
) -> Dict[str, Any]:
    \"\"\"Create work_sessions for a technical spec.

    Args:
        spec_id: Technical spec ID (e.g., "SPEC-135")
        roadmap_item_id: Roadmap item ID (e.g., "PRIORITY-35")
        granularity: Decomposition level ("phase", "section", "module")

    Returns:
        Dict with work_sessions created

    Raises:
        FileConflictError: If assigned_files overlap
        SpecNotFoundError: If spec doesn't exist
    \"\"\"

def analyze_spec_work_units(spec_id: str) -> List[Dict[str, Any]]:
    \"\"\"Analyze spec and identify work units.

    Args:
        spec_id: Technical spec ID

    Returns:
        List of work units with metadata:
        [
            {
                "unit_name": "Phase 1",
                "sections": ["/database_design"],
                "estimated_files": ["db.py", "test_db.py"],
                "complexity": "medium"
            },
            ...
        ]
    \"\"\"

def validate_work_session_independence(
    work_sessions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    \"\"\"Validate work_sessions have no file conflicts.

    Args:
        work_sessions: List of work_session dicts with assigned_files

    Returns:
        {
            "valid": True/False,
            "conflicts": [...],  # List of conflicts if any
            "parallelizable": True/False
        }
    \"\"\"

def generate_work_id(spec_id: str, sequence: int) -> str:
    \"\"\"Generate work_id for work_session.

    Args:
        spec_id: Technical spec ID (e.g., "SPEC-135")
        sequence: Sequence number (1, 2, 3...)

    Returns:
        work_id like "WORK-135-1"
    \"\"\"
    return f"WORK-{spec_id.split('-')[1]}-{sequence}"

def generate_branch_name(work_id: str) -> str:
    \"\"\"Generate branch name for work_session.

    Args:
        work_id: Work ID (e.g., "WORK-135-1")

    Returns:
        branch_name like "roadmap-work-135-1"
    \"\"\"
    return f"roadmap-{work_id.lower()}"
```

### Database Operations

```python
def insert_work_session(
    work_id: str,
    spec_id: str,
    roadmap_item_id: str,
    scope: str,
    scope_description: str,
    assigned_files: List[str],
    branch_name: str
) -> None:
    \"\"\"Insert work_session into database.

    Args:
        work_id: Unique work ID
        spec_id: Technical spec ID
        roadmap_item_id: Roadmap item ID
        scope: Decomposition level (phase/section/module)
        scope_description: Human-readable description
        assigned_files: List of files this work touches
        branch_name: Git branch name
    \"\"\"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        \"\"\"
        INSERT INTO work_sessions (
            work_id, spec_id, roadmap_item_id,
            scope, scope_description, assigned_files,
            branch_name, status, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\",
        (
            work_id,
            spec_id,
            roadmap_item_id,
            scope,
            scope_description,
            json.dumps(assigned_files),
            branch_name,
            "pending",
            "architect",
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()
```
""",
    "/data_model": """
## Data Model

### work_sessions Table Schema

```sql
CREATE TABLE work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT NOT NULL UNIQUE,           -- "WORK-135-1"
    spec_id TEXT NOT NULL,                  -- "SPEC-135"
    roadmap_item_id TEXT,                   -- "PRIORITY-35"
    scope TEXT NOT NULL,                    -- "phase", "section", "module"
    scope_description TEXT,                 -- "Phase 1: Database schema (/database_design)"
    assigned_files TEXT,                    -- JSON: ["file1.py", "file2.py"]
    branch_name TEXT NOT NULL UNIQUE,       -- "roadmap-work-135-1"
    worktree_path TEXT,                     -- Path to git worktree (set by orchestrator)
    status TEXT NOT NULL DEFAULT 'pending', -- pending/in_progress/completed/failed
    claimed_by TEXT,                        -- "code_developer" (set when claimed)
    claimed_at TEXT,                        -- ISO timestamp
    started_at TEXT,                        -- When work started
    completed_at TEXT,                      -- When work finished
    commit_sha TEXT,                        -- Final commit SHA
    merged_at TEXT,                         -- When merged to roadmap
    created_by TEXT NOT NULL DEFAULT 'architect',
    created_at TEXT NOT NULL,

    FOREIGN KEY (spec_id) REFERENCES technical_specs(id),
    FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id)
);
```

### Work Unit Data Structure

```python
@dataclass
class WorkUnit:
    \"\"\"Represents a parallelizable unit of work.\"\"\"

    unit_name: str                # "Phase 1: Database schema"
    sections: List[str]           # ["/database_design"]
    assigned_files: List[str]     # ["unified_database.py", "test_db.py"]
    complexity: str               # "low", "medium", "high"
    estimated_hours: float        # 2.5
    dependencies: List[str]       # ["WORK-135-0"] (optional)

    def to_work_session(self, spec_id: str, sequence: int) -> Dict[str, Any]:
        \"\"\"Convert to work_session dict for database insertion.\"\"\"
        work_id = f"WORK-{spec_id.split('-')[1]}-{sequence}"

        return {
            "work_id": work_id,
            "scope": "phase",  # or section/module
            "scope_description": self.unit_name + " (" + ", ".join(self.sections) + ")",
            "assigned_files": self.assigned_files,
            "branch_name": f"roadmap-{work_id.lower()}"
        }
```

### File Dependency Graph

```python
class FileDependencyGraph:
    \"\"\"Tracks file dependencies for conflict detection.\"\"\"

    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}  # file → {dependent_files}

    def add_dependency(self, file: str, depends_on: str):
        \"\"\"Add dependency: file depends on depends_on.\"\"\"
        if file not in self.graph:
            self.graph[file] = set()
        self.graph[file].add(depends_on)

    def get_all_dependencies(self, file: str) -> Set[str]:
        \"\"\"Get transitive closure of dependencies.\"\"\"
        visited = set()
        to_visit = {file}

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            if current in self.graph:
                to_visit.update(self.graph[current])

        return visited - {file}  # Exclude file itself

    def find_conflicts(
        self,
        work_units: List[WorkUnit]
    ) -> Dict[Tuple[int, int], Set[str]]:
        \"\"\"Find file conflicts between work units.

        Returns:
            Dict mapping (unit_i, unit_j) to set of conflicting files
        \"\"\"
        conflicts = {}

        for i, unit_i in enumerate(work_units):
            files_i = set(unit_i.assigned_files)
            deps_i = set()
            for f in files_i:
                deps_i.update(self.get_all_dependencies(f))
            full_i = files_i | deps_i

            for j, unit_j in enumerate(work_units):
                if j <= i:
                    continue

                files_j = set(unit_j.assigned_files)
                deps_j = set()
                for f in files_j:
                    deps_j.update(self.get_all_dependencies(f))
                full_j = files_j | deps_j

                overlap = full_i & full_j
                if overlap:
                    conflicts[(i, j)] = overlap

        return conflicts
```

### assigned_files Validation Rules

1. **No Empty Lists**: Every work_session must have ≥1 assigned file
2. **No Duplicates Within**: assigned_files list has no duplicates
3. **No Overlaps Between**: No file appears in multiple work_sessions
4. **Relative Paths**: All paths relative to repo root
5. **Files Must Exist**: All files should exist or be creatable

```python
def validate_assigned_files(assigned_files: List[str]) -> None:
    \"\"\"Validate assigned_files list.

    Raises:
        ValueError: If validation fails
    \"\"\"
    if not assigned_files:
        raise ValueError("assigned_files cannot be empty")

    if len(assigned_files) != len(set(assigned_files)):
        raise ValueError("assigned_files contains duplicates")

    for file_path in assigned_files:
        if file_path.startswith("/"):
            raise ValueError(f"File path must be relative: {file_path}")
```
""",
    "/implementation": """
## Implementation

### Phase 1: work-session-creator Skill Foundation (3-4 hours)

**File**: `.claude/skills/architect/work-session-creator/SKILL.md` (NEW)

```markdown
# work-session-creator Skill

**Purpose**: Decompose technical specifications into parallelizable work_sessions

**When to Use**: After creating a technical spec, before code_developer starts implementation

**Inputs**:
- spec_id: Technical specification ID (e.g., "SPEC-135")
- roadmap_item_id: Roadmap item ID (e.g., "PRIORITY-35")
- granularity: Decomposition level ("phase", "section", "module")

**Process**:

1. **Read Technical Spec**
   - Load spec from database using unified-spec-skill
   - Parse hierarchical structure (sections)
   - Identify phases or natural work boundaries

2. **Identify Work Units**
   - Phase-based: Group by implementation phases
   - Section-based: Group by hierarchical sections
   - Module-based: Group by independent modules

3. **Analyze File Dependencies**
   - For each work unit, identify ALL files to be touched
   - Use code-searcher to find related code
   - Use dependency-tracer to analyze import chains
   - Include test files for each implementation file

4. **Validate Independence**
   - Check for file overlaps between work units
   - Detect circular dependencies
   - If conflicts found, adjust work unit boundaries

5. **Create work_sessions**
   - Generate work_id for each unit (WORK-{spec_num}-{seq})
   - Generate branch_name (roadmap-work-{id})
   - Insert into work_sessions table
   - Set status='pending', created_by='architect'

**Outputs**:
- Number of work_sessions created
- List of work_sessions with assigned_files
- Validation result (parallelizable: true/false)

**Example**:

Input: spec_id="SPEC-135", granularity="phase"

Analysis:
- Phase 1: Database schema → files: [unified_database.py, test_db.py]
- Phase 2: API → files: [api.py, test_api.py]
- Phase 3: Tests → files: [integration_tests.py]

Validation: No file overlaps ✅

Output: Created 3 work_sessions (WORK-135-1, WORK-135-2, WORK-135-3)
```

**File**: `.claude/skills/architect/work-session-creator/work_session_creator.py` (NEW)

```python
\"\"\"work-session-creator skill implementation.\"\"\"

import json
import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from coffee_maker.autonomous.unified_database import get_unified_database

logger = logging.getLogger(__name__)


class FileConflictError(Exception):
    \"\"\"Raised when work units have overlapping files.\"\"\"


class SpecNotFoundError(Exception):
    \"\"\"Raised when technical spec not found in database.\"\"\"


def create_work_sessions_for_spec(
    spec_id: str,
    roadmap_item_id: str,
    granularity: str = "phase"
) -> Dict[str, Any]:
    \"\"\"Create work_sessions for a technical spec.

    Main entry point for work-session-creator skill.

    Args:
        spec_id: Technical spec ID (e.g., "SPEC-135")
        roadmap_item_id: Roadmap item ID (e.g., "PRIORITY-35")
        granularity: Decomposition level ("phase", "section", "module")

    Returns:
        Dict with work_sessions_created, work_sessions, validation

    Raises:
        FileConflictError: If assigned_files overlap
        SpecNotFoundError: If spec doesn't exist
    \"\"\"
    logger.info(f"Creating work_sessions for {spec_id} (granularity={granularity})")

    # Step 1: Read technical spec
    spec_content = read_technical_spec(spec_id)

    # Step 2: Identify work units
    work_units = identify_work_units(spec_content, granularity)
    logger.info(f"Identified {len(work_units)} work units")

    # Step 3: Analyze file dependencies for each unit
    for unit in work_units:
        unit["assigned_files"] = analyze_file_dependencies(unit, spec_content)

    # Step 4: Validate independence
    validation = validate_work_unit_independence(work_units)

    if not validation["valid"]:
        raise FileConflictError(
            f"File conflicts detected: {validation['conflicts']}"
        )

    # Step 5: Create work_sessions in database
    work_sessions = []
    for i, unit in enumerate(work_units, start=1):
        work_id = generate_work_id(spec_id, i)
        branch_name = generate_branch_name(work_id)

        work_session = {
            "work_id": work_id,
            "spec_id": spec_id,
            "roadmap_item_id": roadmap_item_id,
            "scope": granularity,
            "scope_description": unit["description"],
            "assigned_files": unit["assigned_files"],
            "branch_name": branch_name,
        }

        insert_work_session(work_session)
        work_sessions.append(work_session)

    logger.info(f"✅ Created {len(work_sessions)} work_sessions for {spec_id}")

    return {
        "work_sessions_created": len(work_sessions),
        "work_sessions": work_sessions,
        "validation": validation,
    }


def read_technical_spec(spec_id: str) -> Dict[str, Any]:
    \"\"\"Read technical spec from database.\"\"\"
    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM technical_specs WHERE id = ?",
        (spec_id,)
    )
    spec = cursor.fetchone()
    conn.close()

    if not spec:
        raise SpecNotFoundError(f"Spec {spec_id} not found")

    spec_dict = dict(spec)

    # Parse hierarchical content if applicable
    if spec_dict["spec_type"] == "hierarchical":
        spec_dict["sections"] = json.loads(spec_dict["content"])

    return spec_dict


def identify_work_units(
    spec_content: Dict[str, Any],
    granularity: str
) -> List[Dict[str, Any]]:
    \"\"\"Identify work units from spec.

    Returns:
        List of work units with description and sections
    \"\"\"
    if granularity == "phase":
        return identify_phase_based_units(spec_content)
    elif granularity == "section":
        return identify_section_based_units(spec_content)
    elif granularity == "module":
        return identify_module_based_units(spec_content)
    else:
        raise ValueError(f"Unknown granularity: {granularity}")


def identify_phase_based_units(spec_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    \"\"\"Identify work units by implementation phases.\"\"\"
    # Parse implementation section for phases
    sections = spec_content.get("sections", {})
    implementation = sections.get("/implementation", "")

    # Extract phase markers
    phase_pattern = r"###\\s+Phase\\s+(\\d+):[^\\n]+"
    phases = re.findall(phase_pattern, implementation)

    work_units = []
    for phase_num in phases:
        # Extract phase content
        phase_pattern = f"###\\s+Phase\\s+{phase_num}:([^#]+)"
        phase_match = re.search(phase_pattern, implementation, re.DOTALL)

        if phase_match:
            phase_content = phase_match.group(1).strip()

            # Parse description from first line
            description_match = re.search(r"^([^\\n]+)", phase_content)
            description = description_match.group(1) if description_match else f"Phase {phase_num}"

            work_units.append({
                "description": f"Phase {phase_num}: {description}",
                "sections": ["/implementation"],
                "phase_number": int(phase_num),
                "content": phase_content,
            })

    # Fallback: if no phases found, create single unit
    if not work_units:
        work_units.append({
            "description": "Full implementation",
            "sections": list(sections.keys()),
            "phase_number": 1,
            "content": implementation,
        })

    return work_units


def identify_section_based_units(spec_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    \"\"\"Identify work units by hierarchical sections.\"\"\"
    sections = spec_content.get("sections", {})

    # Define logical groupings
    groupings = [
        {
            "description": "Database design",
            "sections": ["/database_design", "/data_model"],
        },
        {
            "description": "API implementation",
            "sections": ["/api_design", "/implementation"],
        },
        {
            "description": "Testing",
            "sections": ["/test_strategy"],
        },
    ]

    work_units = []
    for group in groupings:
        # Check if any section exists
        existing_sections = [s for s in group["sections"] if s in sections]
        if existing_sections:
            work_units.append({
                "description": group["description"],
                "sections": existing_sections,
                "content": "\n\n".join([sections[s] for s in existing_sections]),
            })

    return work_units


def identify_module_based_units(spec_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    \"\"\"Identify work units by independent modules.\"\"\"
    # Parse implementation for class/module definitions
    sections = spec_content.get("sections", {})
    implementation = sections.get("/implementation", "")

    # Find class definitions
    class_pattern = r"class\\s+(\\w+)"
    classes = re.findall(class_pattern, implementation)

    work_units = []
    for class_name in classes:
        work_units.append({
            "description": f"Module: {class_name}",
            "sections": ["/implementation"],
            "module_name": class_name,
            "content": implementation,
        })

    return work_units if work_units else identify_phase_based_units(spec_content)


def analyze_file_dependencies(
    work_unit: Dict[str, Any],
    spec_content: Dict[str, Any]
) -> List[str]:
    \"\"\"Analyze file dependencies for work unit.

    Returns:
        List of file paths this work unit will touch
    \"\"\"
    files = set()

    # 1. Extract file mentions from work unit content
    content = work_unit.get("content", "")
    file_pattern = r"[a-zA-Z0-9_/]+\\.py"
    mentioned_files = re.findall(file_pattern, content)
    files.update(mentioned_files)

    # 2. Extract file mentions from spec title
    title = spec_content.get("title", "")
    title_files = re.findall(file_pattern, title)
    files.update(title_files)

    # 3. Derive test files
    test_files = set()
    for impl_file in files:
        if not impl_file.startswith("tests/"):
            # Derive test file path
            if impl_file.startswith("coffee_maker/"):
                test_file = impl_file.replace("coffee_maker/", "tests/unit/test_")
                test_files.add(test_file)
    files.update(test_files)

    # 4. Normalize paths (remove coffee_maker prefix if present in code blocks)
    normalized = set()
    for file in files:
        # Remove common code block artifacts
        file = file.strip("`\"'")
        if file and not file.startswith("#"):
            normalized.add(file)

    return sorted(list(normalized))


def validate_work_unit_independence(
    work_units: List[Dict[str, Any]]
) -> Dict[str, Any]:
    \"\"\"Validate work units have no file conflicts.

    Returns:
        {
            "valid": True/False,
            "conflicts": [...],
            "parallelizable": True/False
        }
    \"\"\"
    conflicts = []

    for i, unit_i in enumerate(work_units):
        files_i = set(unit_i.get("assigned_files", []))

        for j, unit_j in enumerate(work_units):
            if j <= i:
                continue

            files_j = set(unit_j.get("assigned_files", []))
            overlap = files_i & files_j

            if overlap:
                conflicts.append({
                    "unit_i": unit_i["description"],
                    "unit_j": unit_j["description"],
                    "overlapping_files": list(overlap),
                })

    return {
        "valid": len(conflicts) == 0,
        "conflicts": conflicts,
        "parallelizable": len(conflicts) == 0,
    }


def generate_work_id(spec_id: str, sequence: int) -> str:
    \"\"\"Generate work_id.\"\"\"
    spec_num = spec_id.split("-")[1]
    return f"WORK-{spec_num}-{sequence}"


def generate_branch_name(work_id: str) -> str:
    \"\"\"Generate branch name.\"\"\"
    return f"roadmap-{work_id.lower()}"


def insert_work_session(work_session: Dict[str, Any]) -> None:
    \"\"\"Insert work_session into database.\"\"\"
    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    cursor.execute(
        \"\"\"
        INSERT INTO work_sessions (
            work_id, spec_id, roadmap_item_id,
            scope, scope_description, assigned_files,
            branch_name, status, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\",
        (
            work_session["work_id"],
            work_session["spec_id"],
            work_session["roadmap_item_id"],
            work_session["scope"],
            work_session["scope_description"],
            json.dumps(work_session["assigned_files"]),
            work_session["branch_name"],
            "pending",
            "architect",
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    logger.info(f"Inserted work_session {work_session['work_id']}")


def main(inputs: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Skill entry point.

    Args:
        inputs: {
            "spec_id": "SPEC-135",
            "roadmap_item_id": "PRIORITY-35",
            "granularity": "phase"
        }

    Returns:
        {
            "work_sessions_created": 3,
            "work_sessions": [...],
            "validation": {...}
        }
    \"\"\"
    return create_work_sessions_for_spec(
        spec_id=inputs["spec_id"],
        roadmap_item_id=inputs["roadmap_item_id"],
        granularity=inputs.get("granularity", "phase"),
    )
```

### Phase 2: Testing & Validation (2 hours)

**File**: `tests/unit/test_work_session_creator.py` (NEW)

```python
def test_identify_phase_based_units():
    \"\"\"Test phase-based work unit identification.\"\"\"
    # Setup: Spec with 3 phases in /implementation
    # Execute: identify_phase_based_units()
    # Assert: Returns 3 work units

def test_analyze_file_dependencies():
    \"\"\"Test file dependency analysis.\"\"\"
    # Setup: Work unit mentioning "daemon.py"
    # Execute: analyze_file_dependencies()
    # Assert: Returns ["daemon.py", "tests/unit/test_daemon.py"]

def test_validate_work_unit_independence_success():
    \"\"\"Test validation with independent units.\"\"\"
    # Setup: 2 work units with different files
    # Execute: validate_work_unit_independence()
    # Assert: valid=True, parallelizable=True

def test_validate_work_unit_independence_conflict():
    \"\"\"Test validation with overlapping files.\"\"\"
    # Setup: 2 work units with overlapping file
    # Execute: validate_work_unit_independence()
    # Assert: valid=False, conflicts detected

def test_create_work_sessions_end_to_end():
    \"\"\"Test full work_session creation.\"\"\"
    # Setup: Create SPEC-TEST in database
    # Execute: create_work_sessions_for_spec()
    # Assert: work_sessions inserted into database
    # Assert: No file overlaps
```

### Phase 3: Integration (1-2 hours)

Integrate skill into architect workflow:

1. After creating technical spec, architect calls work-session-creator skill
2. Skill creates work_sessions in database
3. orchestrator can now spawn parallel code_developers
""",
    "/test_strategy": """
## Test Strategy

### Unit Tests

**Coverage Target**: ≥90% for work_session_creator.py

1. **test_read_technical_spec**
   - Test reading hierarchical spec from database
   - Test SpecNotFoundError for missing spec

2. **test_identify_phase_based_units**
   - Test extracting phases from /implementation section
   - Test fallback when no phases found

3. **test_identify_section_based_units**
   - Test grouping sections (database, API, testing)
   - Test handling missing sections

4. **test_identify_module_based_units**
   - Test extracting class names from implementation
   - Test fallback to phase-based

5. **test_analyze_file_dependencies**
   - Test extracting file mentions from content
   - Test deriving test files from implementation files
   - Test path normalization

6. **test_validate_work_unit_independence**
   - Test success case (no overlaps)
   - Test failure case (file conflicts)
   - Test conflict reporting

7. **test_generate_work_id**
   - Test format: WORK-{spec_num}-{seq}

8. **test_generate_branch_name**
   - Test format: roadmap-work-{id}

### Integration Tests

**File**: `tests/integration/test_work_session_creator_integration.py`

1. **test_create_work_sessions_for_real_spec**
   - Use SPEC-131 (already in database)
   - Create work_sessions
   - Validate work_sessions inserted correctly
   - Validate no file overlaps

2. **test_parallel_spec_decomposition**
   - Create spec with 3 clear phases
   - Call work-session-creator
   - Assert 3 work_sessions created
   - Assert assigned_files are independent

3. **test_file_conflict_detection**
   - Create spec where phases share files
   - Call work-session-creator
   - Assert FileConflictError raised
   - Assert conflicts reported accurately

### Manual Testing

```bash
# Test 1: Create work_sessions for SPEC-131
python3 -c "
from claude.skills.architect.work_session_creator.work_session_creator import create_work_sessions_for_spec

result = create_work_sessions_for_spec(
    spec_id='SPEC-131',
    roadmap_item_id='PRIORITY-31',
    granularity='phase'
)

print(f'Created {result[\"work_sessions_created\"]} work_sessions')
for ws in result['work_sessions']:
    print(f'  {ws[\"work_id\"]}: {len(ws[\"assigned_files\"])} files')
"

# Test 2: Validate work_sessions in database
python3 -c "
from coffee_maker.autonomous.unified_database import get_unified_database
import sqlite3

db = get_unified_database()
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

cursor.execute('SELECT work_id, scope_description, assigned_files FROM work_sessions')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
    print(f'  Files: {row[2]}')

conn.close()
"

# Test 3: Test with real spec (SPEC-131)
python3 .claude/skills/architect/work-session-creator/work_session_creator.py \
    --spec-id SPEC-131 \
    --roadmap-item-id PRIORITY-31 \
    --granularity phase
```
""",
    "/dependencies": """
## Dependencies

### Required (Already Available)

✅ **work_sessions table** (commit 64e78e7)
- Table structure complete with all necessary fields
- Ready for work_session insertion

✅ **technical_specs table with hierarchical specs**
- Stores specs as JSON with section keys
- SPEC-131 already exists as example

✅ **unified_database.py**
- Database access layer
- Connection management

✅ **code-searcher skill** (for file analysis)
- Can find related code in codebase
- Available in `.claude/skills/code-searcher/`

✅ **dependency-tracer skill** (for import analysis)
- Can analyze import chains
- Available in `.claude/skills/dependency-tracer/`

### New Dependencies

**None** - All required infrastructure exists!

### Python Dependencies

All standard library:
- json (parsing hierarchical specs)
- re (regex for file extraction)
- sqlite3 (database operations)
- pathlib (path handling)
- datetime (timestamps)

### Version Compatibility

- Python 3.8+
- SQLite 3.24+
- Compatible with all existing code
""",
    "/success_criteria": """
## Success Criteria

### Functional Requirements

- [ ] **Skill Implementation**: work-session-creator skill implemented in `.claude/skills/architect/work-session-creator/`
- [ ] **Spec Reading**: Skill reads technical specs from database
- [ ] **Phase Identification**: Skill identifies phases from /implementation section
- [ ] **Section Identification**: Skill groups sections logically (database, API, testing)
- [ ] **Module Identification**: Skill extracts classes/modules from implementation
- [ ] **File Analysis**: Skill extracts file mentions from spec content
- [ ] **Test File Derivation**: Skill derives test files from implementation files
- [ ] **Conflict Detection**: Skill detects file overlaps between work units
- [ ] **work_session Creation**: Skill inserts work_sessions into database
- [ ] **work_id Generation**: Format WORK-{spec_num}-{seq}
- [ ] **branch_name Generation**: Format roadmap-work-{id}

### Data Quality Requirements

- [ ] **No Empty assigned_files**: Every work_session has ≥1 file
- [ ] **No File Overlaps**: Validation ensures no file appears in multiple work_sessions
- [ ] **Proper JSON Formatting**: assigned_files stored as valid JSON array
- [ ] **Relative Paths**: All file paths relative to repo root
- [ ] **Status Set Correctly**: All created work_sessions have status='pending'
- [ ] **Timestamps**: created_at set to ISO format timestamp
- [ ] **Attribution**: created_by='architect' for all work_sessions

### Integration Requirements

- [ ] **End-to-End Test**: Create work_sessions for SPEC-131 successfully
- [ ] **Database Insertion**: work_sessions appear in work_sessions table
- [ ] **No SQL Errors**: All database operations succeed
- [ ] **Conflict Detection Test**: FileConflictError raised for overlapping files
- [ ] **Validation Test**: validate_work_unit_independence works correctly

### Performance Requirements

- [ ] **Spec Analysis**: Complete in <5 seconds for typical spec
- [ ] **File Analysis**: Complete in <10 seconds per work unit
- [ ] **Database Insertion**: <100ms per work_session
- [ ] **Total Execution**: <30 seconds for 3-phase spec

### Quality Requirements

- [ ] **Test Coverage**: ≥90% code coverage
- [ ] **Error Handling**: All exceptions handled gracefully
- [ ] **Logging**: All operations logged at INFO level
- [ ] **Type Hints**: All functions have type hints
- [ ] **Documentation**: Skill has comprehensive SKILL.md
- [ ] **Docstrings**: All functions documented

### Example Success Scenario

```python
# Input: SPEC-131 (code_developer work_sessions integration)
result = create_work_sessions_for_spec(
    spec_id="SPEC-131",
    roadmap_item_id="PRIORITY-31",
    granularity="phase"
)

# Expected Output:
# {
#   "work_sessions_created": 3,
#   "work_sessions": [
#     {
#       "work_id": "WORK-131-1",
#       "scope_description": "Phase 1: WorkSessionManager Foundation",
#       "assigned_files": [
#         "coffee_maker/autonomous/work_session_manager.py",
#         "tests/unit/test_work_session_manager.py"
#       ],
#       "branch_name": "roadmap-work-131-1"
#     },
#     {
#       "work_id": "WORK-131-2",
#       "scope_description": "Phase 2: daemon.py Integration",
#       "assigned_files": [
#         "coffee_maker/autonomous/daemon.py",
#         "coffee_maker/autonomous/daemon_implementation.py"
#       ],
#       "branch_name": "roadmap-work-131-2"
#     },
#     {
#       "work_id": "WORK-131-3",
#       "scope_description": "Phase 3: CLI Integration",
#       "assigned_files": [
#         "coffee_maker/autonomous/daemon_cli.py"
#       ],
#       "branch_name": "roadmap-work-131-3"
#     }
#   ],
#   "validation": {
#     "valid": true,
#     "conflicts": [],
#     "parallelizable": true
#   }
# }

# Verify in database:
SELECT * FROM work_sessions WHERE spec_id = 'SPEC-131'
# Returns 3 rows with status='pending', no file overlaps
```
""",
}


def main():
    """Insert SPEC-132 into database."""
    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    spec_id = "SPEC-132"
    spec_number = 132
    title = "architect work_session Creation & Task Decomposition for Parallel Development"
    roadmap_item_id = "PRIORITY-32"

    # Check if spec already exists
    cursor.execute("SELECT id FROM technical_specs WHERE id = ?", (spec_id,))
    exists = cursor.fetchone()

    if exists:
        print(f"⚠️  Spec {spec_id} already exists, updating...")
        cursor.execute(
            """
            UPDATE technical_specs
            SET content = ?,
                updated_at = ?,
                updated_by = 'architect',
                title = ?,
                roadmap_item_id = ?,
                status = 'approved',
                spec_type = 'hierarchical',
                estimated_hours = 8
            WHERE id = ?
        """,
            (
                json.dumps(spec_content),
                datetime.now().isoformat(),
                title,
                roadmap_item_id,
                spec_id,
            ),
        )
        print(f"✅ Updated {spec_id}")
    else:
        # Insert new spec
        cursor.execute(
            """
            INSERT INTO technical_specs (
                id, spec_number, title, roadmap_item_id,
                status, spec_type, content,
                estimated_hours, updated_at, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                spec_id,
                spec_number,
                title,
                roadmap_item_id,
                "approved",
                "hierarchical",
                json.dumps(spec_content),
                8,  # estimated_hours
                datetime.now().isoformat(),
                "architect",
            ),
        )
        print(f"✅ Created {spec_id}: {title}")

    conn.commit()
    conn.close()

    print(f"\n📋 Spec sections:")
    for section_key in spec_content.keys():
        section_length = len(spec_content[section_key])
        print(f"  {section_key}: {section_length} chars")

    print(f"\n🎯 Total spec size: {len(json.dumps(spec_content))} chars")


if __name__ == "__main__":
    main()
