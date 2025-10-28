# US-039: Critical Functional Requirements (CFR) Enforcement System - Technical Specification

**Status**: ✅ Ready for Implementation
**Type**: Architecture / Safety / System Integrity
**Complexity**: High
**Priority**: CRITICAL
**Created**: 2025-10-20
**Author**: architect
**Assigned To**: code_developer

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Requirements](#requirements)
4. [Architecture](#architecture)
5. [Implementation Details](#implementation-details)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Plan](#deployment-plan)
8. [Success Metrics](#success-metrics)
9. [References](#references)

---

## Executive Summary

This technical specification defines the implementation of a comprehensive Critical Functional Requirements (CFR) enforcement system that prevents system integrity violations at multiple levels. The system validates user requests, user stories, and agent actions against documented CFRs before execution, providing clear error messages and safe alternatives when violations are detected.

### Key Components

1. **CFR Validator Module** (`coffee_maker/autonomous/ace/cfr_validator.py`) - Core validation logic
2. **Safe Alternatives Generator** (`coffee_maker/autonomous/ace/safe_alternatives.py`) - Suggests safe alternatives
3. **User Listener Integration** - Level 3 validation (user requests)
4. **Project Manager Integration** - Level 2 validation (user stories)
5. **Base Agent Self-Check** - Level 4 validation (agent planning)

### Validation Levels

| Level | When | What | Where |
|-------|------|------|-------|
| **Level 1** | File write operations | Ownership enforcement | `generator` (US-038 - Already Implemented ✅) |
| **Level 2** | Before ROADMAP addition | User story validation | `project_manager` |
| **Level 3** | Before request execution | User request validation | `user_listener` |
| **Level 4** | Before agent work | Agent self-check | `base_agent` (optional enhancement) |

### Implementation Size

- **New Code**: ~400 lines total
  - `cfr_validator.py`: ~200 lines
  - `safe_alternatives.py`: ~100 lines
  - Integration code: ~100 lines
- **Test Code**: ~300 lines
- **Estimated Time**: 2-3 days

---

## Problem Statement

### Current Situation

**CFRs are documented but not enforced proactively**:
- CFRs exist in `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- No validation before accepting user requests
- No validation before creating user stories
- Violations can be proposed and require manual detection
- System relies on human vigilance to catch violations

**Proof of Problem - US-040 Failure**:
> In US-040, `project_manager` created a user story that violated CFR-002 by giving `assistant` file-writing capabilities. The user had to manually catch this violation. See `docs/roadmap/learnings/WORKFLOW_FAILURE_US_040.md` for complete analysis.

This failure demonstrates:
1. Agents can propose CFR-violating work
2. No automated prevention exists
3. User must manually validate every proposal
4. Risk of system integrity violations

### Goal

**Prevent CFR violations through automated validation**:
- Validate BEFORE violations occur (not after)
- Provide clear, actionable error messages
- Suggest safe alternatives automatically
- Allow user override with explicit confirmation
- Create learning opportunities from violation patterns

### Non-Goals

- NOT building complex AI-powered rule engine (use simple pattern matching)
- NOT validating every operation (focus on high-risk: ownership, roles)
- NOT blocking without explanation (always provide alternatives)
- NOT replacing human judgment (assist, don't dictate)

---

## Requirements

### Functional Requirements

#### FR-1: User Request Validation (Level 3)
**Description**: Validate user requests against CFRs before execution
**Actors**: user_listener, user
**Input**: User's natural language request
**Output**: Validation result with violations (if any) and safe alternatives
**Example**:
```
User Request: "Make assistant write to docs/ROADMAP.md"
↓
Validation: CFR-001, CFR-002 violations detected
↓
Output:
  ❌ CFR Violations Detected:

  CFR-001: assistant cannot write to docs/ (owned by project_manager)
  CFR-002: assistant is READ-ONLY (cannot write files)

  Safe Alternative:
  • Delegate to project_manager to write docs/ROADMAP.md

  Override? [y/N]
```

#### FR-2: User Story Validation (Level 2)
**Description**: Validate user story proposals against CFRs before ROADMAP addition
**Actors**: project_manager, user
**Input**: User story text (markdown)
**Output**: Validation result with violations (if any)
**Example**:
```
User Story: "As a developer, I want assistant to create technical specs..."
↓
Validation: CFR-002, CFR-008 violations detected
↓
Output:
  ❌ CFR Violations Detected:

  CFR-002: assistant is READ-ONLY (cannot create files)
  CFR-008: Only architect creates technical specs

  Safe Alternative:
  • Change user story to have architect create specs
  • assistant can DELEGATE to architect

  Override? [y/N]
```

#### FR-3: Clear Error Messages
**Description**: Provide actionable error messages that explain the violation
**Requirements**:
- State which CFR was violated (e.g., "CFR-001")
- Explain WHY it's a violation
- Provide specific safe alternative
- Include override option

#### FR-4: Safe Alternatives Generation
**Description**: Automatically generate safe alternatives for violating requests
**Algorithm**:
1. Identify violation type (ownership, role, etc.)
2. Look up correct owner/agent from ownership matrix
3. Generate alternative that respects CFRs
4. Format as actionable suggestion

#### FR-5: Observability
**Description**: Log all CFR validation checks for analysis
**Tracking**:
- Langfuse trace for every validation
- Record: request, violations detected, user decision, timestamp
- Enable reflector to analyze violation patterns
- Support future CFR improvements

### Non-Functional Requirements

#### NFR-1: Performance
**Requirement**: Validation completes in < 10ms
**Justification**: User requests must not be slowed by validation
**Implementation**: Simple pattern matching (no AI), in-memory lookups

#### NFR-2: Accuracy
**Requirement**: 95%+ true positive rate, < 5% false positives
**Justification**: Must catch real violations without blocking legitimate work
**Testing**: Comprehensive test suite with 30+ scenarios

#### NFR-3: Usability
**Requirement**: Error messages must be clear and actionable
**Justification**: Users must understand violations and know what to do
**Testing**: User testing with 5+ sample violation scenarios

#### NFR-4: Maintainability
**Requirement**: Adding new CFR checks requires < 10 lines of code
**Justification**: System must scale as CFRs evolve
**Implementation**: Table-driven validation rules

### Constraints

1. **Must integrate with US-038** - Builds on ownership enforcement
2. **Must not break existing workflows** - All current valid operations must pass
3. **Must provide escape hatch** - User can override (with warning logged)
4. **Must work offline** - No external API dependencies

---

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                    MonolithicCoffeeMakerAgent                   │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ User         │                                              │
│  └──────┬───────┘                                              │
│         │                                                       │
│         │ Request                                              │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ user_listener (Level 3 Validation)                   │    │
│  │ ┌────────────────────────────────────────────────┐  │    │
│  │ │ CFR Validator                                   │  │    │
│  │ │  • Parses intent                                │  │    │
│  │ │  • Checks ownership (CFR-001)                   │  │    │
│  │ │  • Checks roles (CFR-002)                       │  │    │
│  │ │  • Returns violations                           │  │    │
│  │ └────────────┬───────────────────────────────────┘  │    │
│  │              │                                        │    │
│  │              ↓                                        │    │
│  │ ┌────────────────────────────────────────────────┐  │    │
│  │ │ Safe Alternatives Generator                     │  │    │
│  │ │  • Identifies correct agent                     │  │    │
│  │ │  • Generates actionable suggestion              │  │    │
│  │ └────────────┬───────────────────────────────────┘  │    │
│  │              │                                        │    │
│  │              ↓                                        │    │
│  │       [Violations?] ──Yes→ [Show message + override] │    │
│  │              │                                        │    │
│  │              No                                       │    │
│  │              ↓                                        │    │
│  │       [Execute request]                               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ project_manager (Level 2 Validation)                 │    │
│  │                                                       │    │
│  │  [New user story] → [CFR Validator] → [Violations?] │    │
│  │                           ↓               ↓          │    │
│  │                          No              Yes          │    │
│  │                           ↓               ↓          │    │
│  │                   [Add to ROADMAP]   [Block + Alt]  │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ generator (Level 1 Enforcement - US-038)             │    │
│  │                                                       │    │
│  │  [File write] → [Check owner] → [Auto-delegate]     │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
coffee_maker/autonomous/ace/
├── cfr_validator.py          # Core validation logic
│   ├── CFRViolation (dataclass)
│   ├── validate_user_request()
│   ├── validate_user_story()
│   ├── extract_intent()
│   └── AGENT_ROLES (constants)
│
├── safe_alternatives.py      # Alternatives generator
│   ├── generate_alternative()
│   ├── identify_correct_agent()
│   └── format_suggestion()
│
└── ownership_registry.py     # From US-038 (reused)
    ├── get_file_owner()
    └── FileOwnership (dataclass)
```

### Data Flow

#### Level 3: User Request Validation

```
User Request String
    ↓
extract_intent() - Parse with regex patterns
    ↓
{agent: str, action: str, file_path: str}
    ↓
validate_user_request() - Check against CFRs
    ↓
Check CFR-001: Does agent own file_path?
    ├── Yes: Continue
    └── No: Add violation
    ↓
Check CFR-002: Can agent perform action?
    ├── Yes: Continue
    └── No: Add violation
    ↓
List[CFRViolation]
    ↓
generate_alternative() - Create safe alternative
    ↓
format_cfr_violations() - Format for user
    ↓
Display + Override prompt
    ↓
User Decision (accept/reject)
```

#### Level 2: User Story Validation

```
User Story Markdown
    ↓
Extract mentions of agents
    ↓
Extract action verbs (write, modify, create)
    ↓
Cross-reference with AGENT_ROLES
    ↓
Detect role violations
    ↓
List[CFRViolation]
    ↓
Display + Override prompt
```

---

## Implementation Details

### Component 1: CFR Validator (`cfr_validator.py`)

#### File: `coffee_maker/autonomous/ace/cfr_validator.py`

**Purpose**: Core validation logic for all CFR checks

**Key Classes**:
```python
@dataclass
class CFRViolation:
    """Represents a detected CFR violation."""
    cfr_id: str          # e.g., "CFR-001", "CFR-002"
    description: str     # Human-readable explanation
    severity: str        # "ERROR", "WARNING"
    agent: str           # Agent involved in violation
    action: str          # Action that would violate (e.g., "write")
    file_path: Optional[str]  # File involved (if applicable)
    suggestion: str      # Safe alternative
```

**Key Functions**:

##### `validate_user_request(request: str) -> List[CFRViolation]`
**Purpose**: Validate user request against CFRs
**Algorithm**:
1. Parse request with `extract_intent()`
2. If parseable:
   - Check CFR-001 (ownership) if file_path present
   - Check CFR-002 (roles) for all write operations
3. Return list of violations (empty if valid)

**Example**:
```python
request = "Make assistant write to docs/ROADMAP.md"
violations = validate_user_request(request)
# Returns:
# [
#   CFRViolation(
#     cfr_id="CFR-001",
#     description="assistant cannot write to docs/ (owned by project_manager)",
#     severity="ERROR",
#     agent="assistant",
#     action="write",
#     file_path="docs/ROADMAP.md",
#     suggestion="Delegate to project_manager to write docs/ROADMAP.md"
#   ),
#   CFRViolation(
#     cfr_id="CFR-002",
#     description="assistant is READ-ONLY (cannot write files)",
#     severity="ERROR",
#     agent="assistant",
#     action="write",
#     file_path=None,
#     suggestion="assistant can only READ files and DELEGATE work"
#   )
# ]
```

##### `extract_intent(request: str) -> Optional[Dict[str, str]]`
**Purpose**: Parse user request to extract intent
**Algorithm**: Regex pattern matching
**Patterns**:
```python
PATTERNS = [
    r"make\s+(\w+)\s+(write|modify|edit|create)\s+(?:to\s+)?(.+)",
    r"have\s+(\w+)\s+(write|modify|edit|create)\s+(?:to\s+)?(.+)",
    r"(\w+)\s+should\s+(write|modify|edit|create)\s+(.+)",
    r"ask\s+(\w+)\s+to\s+(write|modify|edit|create)\s+(.+)",
]
```

**Returns**:
```python
{
    "agent": str,      # e.g., "assistant", "code_developer"
    "action": str,     # e.g., "write", "modify"
    "file_path": str   # e.g., "docs/ROADMAP.md"
}
# or None if unparseable
```

##### `validate_user_story(user_story_text: str) -> List[CFRViolation]`
**Purpose**: Validate user story against CFRs
**Algorithm**:
1. Search for agent names in user story text
2. Search for action verbs (write, modify, create, edit)
3. Cross-reference agent with AGENT_ROLES
4. If READ-ONLY agent + write action → Violation
5. Return list of violations

**Constants**:
```python
AGENT_ROLES = {
    "code_developer": {
        "role": "IMPLEMENTATION",
        "can_write": True,
        "owns": [".claude/", "coffee_maker/", "tests/", "scripts/"],
    },
    "project_manager": {
        "role": "STRATEGIC_PLANNING",
        "can_write": True,
        "owns": ["docs/roadmap/", "docs/*.md"],
    },
    "architect": {
        "role": "TECHNICAL_DESIGN",
        "can_write": True,
        "owns": ["docs/architecture/", "pyproject.toml", "poetry.lock"],
    },
    "assistant": {
        "role": "DOCUMENTATION_EXPERT",
        "can_write": False,  # READ-ONLY
        "owns": [],
    },
    "user_listener": {
        "role": "USER_INTERFACE",
        "can_write": False,  # DELEGATION-ONLY
        "owns": [],
    },
    "assistant (using code analysis skills)": {
        "role": "CODE_ANALYSIS",
        "can_write": False,  # READ-ONLY
        "owns": [],
    },
    "ux-design-expert": {
        "role": "DESIGN_GUIDANCE",
        "can_write": False,  # SPEC-ONLY
        "owns": [],
    },
}
```

### Component 2: Safe Alternatives Generator (`safe_alternatives.py`)

#### File: `coffee_maker/autonomous/ace/safe_alternatives.py`

**Purpose**: Generate actionable safe alternatives for violations

**Key Functions**:

##### `generate_alternative(violation: CFRViolation) -> str`
**Purpose**: Generate safe alternative for a violation
**Algorithm**:
```python
if violation.cfr_id == "CFR-001":  # Ownership violation
    correct_owner = get_file_owner(violation.file_path)
    return f"Delegate to {correct_owner} to {violation.action} {violation.file_path}"

elif violation.cfr_id == "CFR-002":  # Role violation
    if violation.file_path:
        correct_owner = get_file_owner(violation.file_path)
        return f"Use {correct_owner} (owns {violation.file_path})"
    else:
        return f"{violation.agent} can only READ and DELEGATE (not {violation.action})"

else:
    return "Consult docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md"
```

##### `identify_correct_agent(action: str, file_path: Optional[str]) -> str`
**Purpose**: Identify which agent should handle this action
**Algorithm**:
```python
if file_path:
    return get_file_owner(file_path)  # Use US-038 ownership registry

elif action == "strategic_planning":
    return "project_manager"
elif action == "technical_design":
    return "architect"
elif action == "implementation":
    return "code_developer"
else:
    return "user_listener"  # Delegate further
```

##### `format_suggestion(agent: str, action: str, file_path: Optional[str]) -> str`
**Purpose**: Format suggestion as actionable message
**Example**:
```python
agent = "project_manager"
action = "write"
file_path = "docs/ROADMAP.md"

# Returns:
"Delegate to project_manager to write docs/ROADMAP.md"
```

### Component 3: Integration Points

#### Integration 1: user_listener (Level 3)

**File**: `coffee_maker/autonomous/agents/user_listener.py`

**Add**:
```python
from coffee_maker.autonomous.ace.cfr_validator import validate_user_request, CFRViolation
from coffee_maker.autonomous.ace.safe_alternatives import generate_alternative

def handle_user_request(self, request: str) -> str:
    """Handle user request with Level 3 CFR validation."""

    # Level 3: Validate request against CFRs
    violations = validate_user_request(request)

    if violations:
        # Format violation message
        message = self._format_cfr_violations(violations)

        # Ask user if they want to override
        self.warn_user(message, sound=True)  # CFR-009: user_listener uses sound
        override = self._ask_user_override()

        if not override:
            logger.info("🚫 Request blocked due to CFR violations")
            return "Request blocked to prevent CFR violation."

        # User overrode - log warning and proceed
        logger.warning(f"⚠️ CFR violation overridden by user: {request}")

    # Proceed with request execution
    return self._execute_request(request)

def _format_cfr_violations(self, violations: List[CFRViolation]) -> str:
    """Format violations as user-friendly message."""
    lines = ["", "❌ CFR Violation Detected", ""]

    for v in violations:
        lines.append(f"{v.cfr_id}: {v.description}")

    lines.append("")
    lines.append("Safe Alternative:")
    for v in violations:
        lines.append(f"  • {v.suggestion}")

    lines.append("")
    lines.append("This request would violate system ownership boundaries.")

    return "\n".join(lines)

def _ask_user_override(self) -> bool:
    """Ask user if they want to override CFR violation."""
    response = self.get_user_input("Override? [y/N]: ").strip().lower()
    return response == "y"
```

#### Integration 2: project_manager (Level 2)

**File**: `coffee_maker/autonomous/agents/project_manager.py`

**Add**:
```python
from coffee_maker.autonomous.ace.cfr_validator import validate_user_story

def add_user_story_to_roadmap(self, user_story: dict) -> str:
    """Add user story to ROADMAP with Level 2 CFR validation."""

    # Level 2: Validate user story against CFRs
    us_text = self._format_user_story_as_text(user_story)
    violations = validate_user_story(us_text)

    if violations:
        # Log violations
        for v in violations:
            logger.warning(f"CFR violation in user story: {v.cfr_id} - {v.description}")

        # Format message
        message = self._format_cfr_violations(violations)

        # Notify user (project_manager can warn user via notifications)
        self._create_notification(
            title="CFR Violation in User Story",
            message=message,
            severity="ERROR"
        )

        return f"User story blocked due to CFR violations: {[v.cfr_id for v in violations]}"

    # No violations - proceed with adding to ROADMAP
    return self._add_to_roadmap(user_story)
```

#### Integration 3: base_agent (Level 4 - Optional)

**File**: `coffee_maker/autonomous/agents/base_agent.py`

**Add**:
```python
def check_cfr_compliance_before_work(self, planned_actions: List[dict]) -> List[CFRViolation]:
    """
    Level 4: Agent self-check before starting work.

    Args:
        planned_actions: List of actions agent plans to take
                        [{"action": "write", "file_path": "...", ...}, ...]

    Returns:
        List of CFR violations (empty if compliant)
    """
    violations = []

    for action in planned_actions:
        if action["action"] == "write":
            file_path = action.get("file_path")
            if file_path:
                owner = get_file_owner(file_path)
                if owner != self.agent_type:
                    violations.append(CFRViolation(
                        cfr_id="CFR-001",
                        description=f"{self.agent_type} cannot write to {file_path} (owned by {owner})",
                        severity="ERROR",
                        agent=self.agent_type,
                        action="write",
                        file_path=file_path,
                        suggestion=f"Delegate to {owner} to write {file_path}"
                    ))

    return violations
```

---

## Testing Strategy

### Unit Tests

#### File: `tests/unit/test_cfr_enforcement.py`

**Test Cases** (30+ tests):

##### Validation Tests (10 tests)
1. `test_validate_read_only_write_violation()` - assistant write → CFR-002 violation
2. `test_validate_ownership_violation()` - project_manager write .claude/ → CFR-001 violation
3. `test_validate_read_allowed()` - Any agent read → No violation
4. `test_validate_owner_write_allowed()` - code_developer write .claude/ → No violation
5. `test_validate_delegation_only_write()` - user_listener write → CFR-002 violation
6. `test_validate_spec_only_implement()` - ux-design-expert implement → CFR-002 violation
7. `test_validate_multiple_violations()` - Request violates CFR-001 + CFR-002
8. `test_validate_strategic_technical_overlap()` - project_manager create tech spec → CFR-008
9. `test_validate_unknown_agent()` - Unknown agent → No false positives
10. `test_validate_empty_request()` - Empty string → No violations

##### Intent Extraction Tests (10 tests)
11. `test_extract_intent_make_write()` - "Make assistant write to docs/" → Parsed
12. `test_extract_intent_have_modify()` - "Have code_developer modify .claude/" → Parsed
13. `test_extract_intent_should_create()` - "assistant should create file.md" → Parsed
14. `test_extract_intent_ask_to_edit()` - "Ask architect to edit spec.md" → Parsed
15. `test_extract_intent_no_file_path()` - "Make assistant write" → Parsed (no path)
16. `test_extract_intent_no_match()` - "Please help me" → None
17. `test_extract_intent_complex_path()` - Path with spaces → Parsed correctly
18. `test_extract_intent_agent_with_dash()` - "assistant (using code analysis skills)" → Normalized
19. `test_extract_intent_case_insensitive()` - "MAKE ASSISTANT WRITE" → Parsed
20. `test_extract_intent_punctuation()` - Request with punctuation → Parsed

##### User Story Validation Tests (5 tests)
21. `test_validate_user_story_read_only_write()` - US gives assistant write → CFR-002
22. `test_validate_user_story_no_violation()` - Valid US → No violations
23. `test_validate_user_story_technical_spec_non_architect()` - US gives code_developer spec creation → CFR-008
24. `test_validate_user_story_multiple_agents()` - US mentions multiple agents → Correct violations
25. `test_validate_user_story_implicit_action()` - Implicit write action → Detected

##### Safe Alternatives Tests (5 tests)
26. `test_generate_alternative_ownership()` - CFR-001 → Correct owner suggested
27. `test_generate_alternative_role()` - CFR-002 → Role explanation
28. `test_identify_correct_agent_by_file()` - File path → Correct owner
29. `test_identify_correct_agent_by_action()` - Action type → Correct agent
30. `test_format_suggestion()` - Suggestion formatting → User-friendly

### Integration Tests

#### File: `tests/integration/test_cfr_enforcement_integration.py`

**Test Cases** (10 tests):

1. `test_user_listener_blocks_violation()` - user_listener detects and blocks CFR violation
2. `test_user_listener_allows_override()` - User override works correctly
3. `test_user_listener_logs_override()` - Override logged to Langfuse
4. `test_project_manager_blocks_us_violation()` - project_manager blocks violating user story
5. `test_project_manager_allows_valid_us()` - Valid user story passes
6. `test_no_false_positives_code_developer()` - code_developer valid writes pass
7. `test_no_false_positives_architect()` - architect valid writes pass
8. `test_level_1_level_3_interaction()` - Level 1 and Level 3 work together
9. `test_safe_alternatives_correctness()` - Safe alternatives are actually safe
10. `test_observability_tracking()` - All validations tracked in Langfuse

### Manual Testing Checklist

```bash
# Test 1: Level 3 Validation - Ownership Violation
# Start user_listener
poetry run user-listener

# Try: "Make assistant write to docs/ROADMAP.md"
# Expected:
#   ❌ CFR Violation Detected
#
#   CFR-001: assistant cannot write to docs/ (owned by project_manager)
#   CFR-002: assistant is READ-ONLY (cannot write files)
#
#   Safe Alternative:
#     • Delegate to project_manager to write docs/ROADMAP.md
#
#   Override? [y/N]

# Test 2: Level 3 Validation - Valid Request
# Try: "Make code_developer write to coffee_maker/cli/test.py"
# Expected: No violations, request proceeds

# Test 3: Level 2 Validation - User Story Violation
# Create user story that gives assistant write capability
poetry run project-manager
# Try: Add user story with description mentioning "assistant writes docs"
# Expected: CFR-002 violation, user story blocked

# Test 4: Override Mechanism
# Try: "Make assistant write to docs/test.md"
# Type: y (override)
# Expected: Warning logged, request proceeds

# Test 5: Multiple Violations
# Try: "Make user_listener create files in coffee_maker/"
# Expected: Multiple violations listed (CFR-001, CFR-002)
```

---

## Deployment Plan

### Phase 1: Core Implementation (Day 1 - 6 hours)

**Goal**: Implement validation modules

**Tasks**:
1. Create `coffee_maker/autonomous/ace/` directory
2. Implement `cfr_validator.py` (~200 lines)
   - `CFRViolation` dataclass
   - `validate_user_request()`
   - `validate_user_story()`
   - `extract_intent()`
   - `AGENT_ROLES` constants
3. Implement `safe_alternatives.py` (~100 lines)
   - `generate_alternative()`
   - `identify_correct_agent()`
   - `format_suggestion()`
4. Write unit tests (~200 lines)
5. Run tests, fix bugs

**Success Criteria**:
- All 30 unit tests pass
- Coverage > 90%
- Intent extraction works for common patterns
- Violation detection accurate

**Verification**:
```bash
pytest tests/unit/test_cfr_enforcement.py -v
pytest tests/unit/test_cfr_enforcement.py --cov=coffee_maker/autonomous/ace
```

### Phase 2: Integration (Day 2 - 4 hours)

**Goal**: Integrate with user_listener and project_manager

**Tasks**:
1. Update `user_listener.py` (~50 lines)
   - Add `handle_user_request()` validation
   - Add `_format_cfr_violations()`
   - Add `_ask_user_override()`
2. Update `project_manager.py` (~50 lines)
   - Add `add_user_story_to_roadmap()` validation
   - Add CFR violation notification
3. Write integration tests (~100 lines)
4. Manual testing with real requests

**Success Criteria**:
- Level 3 validation works in user_listener
- Level 2 validation works in project_manager
- Override mechanism works
- All integration tests pass
- No false positives on valid requests

**Verification**:
```bash
pytest tests/integration/test_cfr_enforcement_integration.py -v
# Manual testing (see checklist above)
```

### Phase 3: Documentation & Polish (Day 2-3 - 2 hours)

**Goal**: Complete documentation and polish

**Tasks**:
1. Update `.claude/CLAUDE.md` with CFR enforcement section
2. Add examples to `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
3. Update `docs/roadmap/TEAM_COLLABORATION.md` with CFR workflows
4. Add docstrings to all public functions
5. Create this technical spec document

**Success Criteria**:
- All documentation complete
- Examples clear and helpful
- Docstrings comprehensive

**Verification**:
```bash
# Check documentation exists
ls -la docs/architecture/user_stories/US_039_TECHNICAL_SPEC.md
grep -r "CFR enforcement" .claude/CLAUDE.md
```

### Phase 4: Deployment (Day 3 - 1 hour)

**Goal**: Deploy to production

**Tasks**:
1. Run full test suite
2. Commit changes with proper message
3. Update ROADMAP status to ✅ Complete
4. Notify user of completion

**Success Criteria**:
- All tests pass (unit + integration)
- Coverage > 85%
- ROADMAP updated
- Commit follows conventions

**Verification**:
```bash
pytest
pytest --cov=coffee_maker/autonomous/ace
git log -1 --format='%s%n%b'
grep "US-039" docs/roadmap/ROADMAP.md | grep "✅ Complete"
```

---

## Success Metrics

### Primary Metrics

1. **Violation Detection Rate**: 95%+ of actual violations caught
2. **False Positive Rate**: < 5% of legitimate requests blocked
3. **Performance**: Validation completes in < 10ms
4. **User Override Rate**: < 10% of violations overridden (indicates good UX)

### Secondary Metrics

1. **Test Coverage**: > 85% for CFR enforcement modules
2. **Documentation Completeness**: All public functions have docstrings
3. **User Satisfaction**: Manual testing passes all scenarios
4. **Observability**: All validations tracked in Langfuse

### Long-Term Metrics (Post-Deployment)

1. **Violation Trends**: Monitor violations over time (should decrease as agents learn)
2. **Override Patterns**: Analyze what users override (improve detection)
3. **False Positive Reduction**: Track and eliminate false positives
4. **System Integrity**: Zero file conflicts caused by CFR violations

---

## Risk Analysis

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| False positives block legitimate work | Medium | High | Comprehensive test suite + override mechanism |
| Pattern matching misses violations | Low | Medium | Start simple, expand patterns based on real usage |
| Performance degradation | Low | Low | Simple regex + in-memory lookups (< 10ms) |
| Integration breaks existing workflows | Low | High | Integration tests + manual testing before deploy |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users always override (defeats purpose) | Low | Medium | Clear error messages + safe alternatives |
| CFRs evolve, validation lags | Medium | Medium | Table-driven rules, easy to update |
| Observability gaps | Low | Low | Langfuse tracking for all validations |

---

## References

### Related User Stories
- **US-035**: Implement Singleton Agent Enforcement (prevents same-agent conflicts)
  - Location: `docs/roadmap/ROADMAP.md`
  - Status: ✅ Complete
  - Integration: CFR enforcement builds on singleton checks

- **US-038**: Implement File Ownership Enforcement (prevents cross-agent conflicts)
  - Location: `docs/roadmap/ROADMAP.md`
  - Status: ✅ Complete
  - Integration: CFR enforcement reuses `get_file_owner()` from US-038

- **US-040**: Workflow failure that exposed need for CFR enforcement
  - Location: `docs/roadmap/learnings/WORKFLOW_FAILURE_US_040.md`
  - Status: Documented
  - Relevance: Proof of problem - project_manager created CFR-violating user story

### Related Specifications
- **SPEC-035**: Singleton Agent Enforcement
  - Location: `docs/architecture/specs/SPEC-035-singleton-agent-enforcement.md`

- **SPEC-038**: File Ownership Enforcement
  - Location: `docs/architecture/specs/SPEC-038-file-ownership-enforcement.md`

- **SPEC-039**: CFR Enforcement System (Implementation Spec)
  - Location: `docs/architecture/specs/SPEC-039-cfr-enforcement-system.md`

### Related Documents
- **Critical Functional Requirements**
  - Location: `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
  - Contains: All CFR definitions (CFR-000 through CFR-014)

- **Agent Ownership Matrix**
  - Location: `docs/AGENT_OWNERSHIP.md`
  - Contains: File ownership and role definitions

- **CLAUDE.md**
  - Location: `.claude/CLAUDE.md`
  - Contains: Quick reference for CFRs and agent boundaries

### Architecture Decision Records
- **ADR-003**: Simplification-First Approach
  - Relevance: Guides simple pattern matching over complex AI parsing

### Code References
- `coffee_maker/autonomous/agent_registry.py` - Singleton enforcement (US-035)
  - See: `AgentRegistry.register()` context manager
  - Line: 100-150

- `coffee_maker/autonomous/ownership_registry.py` - Ownership lookups (US-038)
  - See: `get_file_owner()` function
  - Line: 50-80

---

## Appendix A: CFR Quick Reference

### CFR-000: PREVENT FILE CONFLICTS AT ALL COSTS (Master Requirement)
**Rule**: At any moment, EXACTLY ZERO or ONE agent writing to any file.
**Why**: File conflicts cause data corruption, inconsistencies, lost work, system failure.
**Enforcement**: All other CFRs exist to prevent this.

### CFR-001: Document Ownership Boundaries
**Rule**: Each file has EXACTLY ONE owner agent. Only owner can modify.
**Why**: Prevents two different agents writing to same file.
**Enforcement**: US-038 (Level 1), This spec (Level 2, 3)

### CFR-002: Agent Role Boundaries
**Rule**: Each agent has EXACTLY ONE primary role. NO overlaps allowed.
**Why**: Prevents role confusion leading to concurrent modifications.
**Enforcement**: This spec (Level 2, 3, 4)

### CFR-003: No Overlap - Documents
**Rule**: No two agents can own same directory/file.
**Why**: Prevents ambiguous ownership leading to conflicts.
**Enforcement**: Ownership matrix in CFR-001, validated by this spec

### CFR-004: No Overlap - Responsibilities
**Rule**: No two agents can have overlapping primary responsibilities.
**Why**: Prevents responsibility confusion leading to concurrent work.
**Enforcement**: Role matrix in CFR-002, validated by this spec

### Other CFRs (CFR-005 through CFR-014)
See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` for complete definitions.

---

## Appendix B: Example Violations and Resolutions

### Example 1: assistant Write Attempt (CFR-002)
**Violation**:
```
User: "Make assistant write to docs/NEW_FEATURE.md"
```

**Detection**:
```python
intent = extract_intent("Make assistant write to docs/NEW_FEATURE.md")
# → {"agent": "assistant", "action": "write", "file_path": "docs/NEW_FEATURE.md"}

violations = validate_user_request(...)
# → [CFRViolation(cfr_id="CFR-002", ...)]
```

**User Message**:
```
❌ CFR Violation Detected

CFR-002: assistant is READ-ONLY (cannot write files)

Safe Alternative:
  • assistant can DELEGATE to project_manager to write docs/NEW_FEATURE.md
  • project_manager owns docs/*.md files

Override? [y/N]
```

**Resolution**: User types 'N', request blocked, no damage done. ✅

---

### Example 2: User Story Giving assistant Write Capability (CFR-002)
**Violation**:
```markdown
## US-XXX: assistant Creates Documentation

**As a**: Developer
**I want**: assistant to automatically create and update documentation
**So that**: Docs stay current

**Description**: assistant should write documentation files...
```

**Detection**:
```python
violations = validate_user_story(user_story_text)
# → [CFRViolation(cfr_id="CFR-002", description="User story gives assistant write capability...")]
```

**project_manager Action**:
```
🚫 User Story Blocked

CFR-002: User story gives assistant write capability, but assistant is READ-ONLY

Safe Alternative:
  • Change user story to have assistant IDENTIFY what docs need updates
  • assistant DELEGATES to project_manager to write docs
  • project_manager actually creates/updates files
```

**Resolution**: User story revised to respect CFR-002. ✅

---

### Example 3: Cross-Ownership Write (CFR-001)
**Violation**:
```
User: "Have project_manager modify .claude/CLAUDE.md"
```

**Detection**:
```python
intent = {"agent": "project_manager", "action": "write", "file_path": ".claude/CLAUDE.md"}
owner = get_file_owner(".claude/CLAUDE.md")  # → "code_developer"
# project_manager != code_developer → CFR-001 violation
```

**User Message**:
```
❌ CFR Violation Detected

CFR-001: project_manager cannot write to .claude/CLAUDE.md (owned by code_developer)

Safe Alternative:
  • Delegate to code_developer to modify .claude/CLAUDE.md
  • code_developer owns all .claude/ files

Override? [y/N]
```

**Resolution**: User types 'N', delegates to code_developer instead. ✅

---

## Appendix C: Testing Scenarios

### Scenario 1: Read Operations (Should Pass)
```python
# All agents can READ any file
test_requests = [
    "Have assistant read docs/ROADMAP.md",
    "Make assistant (using code analysis skills) analyze coffee_maker/",
    "Ask architect to review pyproject.toml",
]

for request in test_requests:
    violations = validate_user_request(request)
    assert len(violations) == 0, f"False positive: {request}"
```

### Scenario 2: Ownership Violations (Should Fail)
```python
test_cases = [
    ("Make assistant write docs/test.md", ["CFR-001", "CFR-002"]),
    ("Have project_manager modify .claude/CLAUDE.md", ["CFR-001"]),
    ("Ask architect to edit docs/roadmap/ROADMAP.md", ["CFR-001"]),
]

for request, expected_cfrs in test_cases:
    violations = validate_user_request(request)
    actual_cfrs = [v.cfr_id for v in violations]
    assert set(actual_cfrs) == set(expected_cfrs), f"Missed violation: {request}"
```

### Scenario 3: Valid Writes (Should Pass)
```python
test_cases = [
    "Make code_developer write to coffee_maker/cli/new_feature.py",
    "Have project_manager update docs/roadmap/ROADMAP.md",
    "Ask architect to modify docs/architecture/specs/SPEC-XXX.md",
]

for request in test_cases:
    violations = validate_user_request(request)
    assert len(violations) == 0, f"False positive: {request}"
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-20 | Created initial technical specification | architect |

---

## Approval Checklist

- [ ] **architect** (author) - Technical design complete and implementable
- [ ] **code_developer** (implementer) - Can implement in 2-3 days as specified
- [ ] **project_manager** (strategic alignment) - Meets US-039 strategic goals
- [ ] **User** (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (13 hours total)

**Breakdown**:
- Phase 1: Core Implementation (6 hours)
- Phase 2: Integration (4 hours)
- Phase 3: Documentation (2 hours)
- Phase 4: Deployment (1 hour)

**Depends On**:
- ✅ US-035 (Singleton) - Complete
- ✅ US-038 (Ownership) - Complete

**Blocks**: None (standalone enhancement)

**Result**: Comprehensive CFR enforcement prevents system integrity violations! 🛡️
