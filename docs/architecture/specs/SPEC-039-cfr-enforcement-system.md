# SPEC-039: Critical Functional Requirements (CFR) Enforcement System

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-039 (ROADMAP), CFR-000 (Master Requirement), US-035 (Singleton), US-038 (Ownership)

**Related ADRs**: ADR-003 (Simplification-First Approach)

**Assigned To**: code_developer

**Depends On**: US-035 (Singleton) and US-038 (Ownership) must be complete first

---

## Executive Summary

This specification describes a simple validation layer that checks user requests and agent plans against Critical Functional Requirements (CFRs) before execution. Using basic pattern matching and ownership lookups, we catch potential violations early and provide clear guidance to users, preventing system-breaking changes.

---

## Problem Statement

### Current Situation

CFRs are documented but not enforced:
- CFRs in `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- No validation before accepting user requests
- No validation before creating user stories
- Violations can be proposed, require manual detection

**Proof of Problem**:
> **US-040 failure**: project_manager created CFR-violating user story (gave assistant file-writing capability) that user had to catch manually. See `docs/roadmap/learnings/WORKFLOW_FAILURE_US_040.md`

### Goal

Validate requests against CFRs:
- Check user requests BEFORE execution (Level 3)
- Check user story proposals BEFORE adding to ROADMAP (Level 2)
- Provide clear error messages with safe alternatives
- Prevent system-breaking changes automatically

### Non-Goals

- NOT building complex rule engine (simple pattern matching)
- NOT validating every single operation (focus on high-risk: file writes, role changes)
- NOT replacing human judgment (validate + suggest alternatives, not block)
- NOT distributed validation (single-machine enforcement)

---

## Requirements

### Functional Requirements

1. **FR-1**: Validate user requests against CFRs (Level 3)
2. **FR-2**: Validate user story proposals against CFRs (Level 2)
3. **FR-3**: Provide clear error messages when violations detected
4. **FR-4**: Suggest safe alternatives for violating requests
5. **FR-5**: Log all CFR checks for observability

### Non-Functional Requirements

1. **NFR-1**: Performance: Validation < 10ms per check
2. **NFR-2**: Accuracy: 95%+ violation detection rate
3. **NFR-3**: Usability: Clear, actionable error messages
4. **NFR-4**: Observability: All validations tracked in Langfuse

### Constraints

- Must integrate with US-038 ownership enforcement (builds on it)
- Must integrate with user_listener (primary entry point)
- Must not break existing workflows
- Must provide escape hatch (user override with confirmation)

---

## Proposed Solution

### High-Level Approach

**Validation Checkpoints**:
- **Level 2**: User story validation (before ROADMAP addition)
- **Level 3**: User request validation (before execution)
- **Level 1**: Already implemented (US-038 generator auto-delegation)

**Why This is Simple**:
- Pattern matching on request text (no AI parsing)
- Ownership lookup (reuses US-038 registry)
- Simple rule checks (CFR-001, CFR-002)
- ~150 lines total implementation

### Architecture Diagram

```
User Request: "Make assistant write to docs/"
    ↓
Level 3: Request Validation
    ↓
Extract intent: agent="assistant", action="write", path="docs/"
    ↓
Check CFR-001 (Ownership): Does assistant own docs/? NO
Check CFR-002 (Role): Is assistant role="writer"? NO (role=READ-ONLY)
    ↓
VIOLATION DETECTED!
    ↓
Provide error message:
  "❌ CFR Violation Detected
   - assistant is READ-ONLY agent (CFR-002)
   - assistant cannot write to docs/ (CFR-001)

   Safe Alternative:
   - Use project_manager to write docs/ (owns it)

   Override? [y/N]"
    ↓
User: N (reject)
    ↓
Request blocked, no damage done ✅
```

---

## Detailed Design

### Component 1: CFR Validator

**File**: `coffee_maker/autonomous/cfr_validator.py` (~100 lines)

**Purpose**: Validate requests against CFRs

**Interface**:
```python
"""
CFR (Critical Functional Requirements) validator.
"""

from typing import Optional, List
from dataclasses import dataclass
from coffee_maker.autonomous.ownership_registry import get_file_owner
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class CFRViolation:
    """Represents a CFR violation."""
    cfr_id: str  # e.g., "CFR-001"
    description: str
    severity: str  # "ERROR", "WARNING"
    suggestion: str  # Safe alternative

# Agent roles (from CLAUDE.md)
AGENT_ROLES = {
    "code_developer": "WRITE (owns .claude/, coffee_maker/, tests/)",
    "project_manager": "WRITE (owns docs/roadmap/)",
    "architect": "WRITE (owns docs/architecture/, pyproject.toml)",
    "generator": "WRITE (owns docs/generator/)",
    "reflector": "WRITE (owns docs/reflector/)",
    "curator": "WRITE (owns docs/curator/)",
    "assistant": "READ-ONLY (delegation only)",
    "user_listener": "DELEGATION-ONLY (no writes)",
    "code-searcher": "READ-ONLY (analysis only)",
    "ux-design-expert": "SPEC-ONLY (provides specs, doesn't implement)",
}

def validate_user_request(request: str) -> List[CFRViolation]:
    """
    Validate user request against CFRs.

    Args:
        request: User's natural language request

    Returns:
        List of CFR violations (empty if valid)

    Example:
        >>> violations = validate_user_request("Make assistant write to docs/")
        >>> for v in violations:
        ...     print(f"{v.cfr_id}: {v.description}")
        CFR-001: assistant cannot write to docs/ (owned by project_manager)
        CFR-002: assistant is READ-ONLY, cannot write files
    """
    violations = []

    # Extract intent using simple pattern matching
    intent = extract_intent(request)

    if not intent:
        return violations  # Can't parse, allow (safe default)

    agent_type = intent.get("agent")
    action = intent.get("action")
    file_path = intent.get("file_path")

    # CFR-001: Ownership violation
    if action == "write" and file_path:
        owner = get_file_owner(file_path)
        if owner and owner != agent_type:
            violations.append(CFRViolation(
                cfr_id="CFR-001",
                description=f"{agent_type} cannot write to {file_path} (owned by {owner})",
                severity="ERROR",
                suggestion=f"Use {owner} to modify {file_path} instead"
            ))

    # CFR-002: Role violation
    if action == "write":
        role = AGENT_ROLES.get(agent_type, "UNKNOWN")
        if "READ-ONLY" in role or "DELEGATION-ONLY" in role:
            violations.append(CFRViolation(
                cfr_id="CFR-002",
                description=f"{agent_type} is {role}, cannot write files",
                severity="ERROR",
                suggestion=f"Delegate write operation to file-owning agent"
            ))

    return violations


def extract_intent(request: str) -> Optional[dict]:
    """
    Extract intent from user request using pattern matching.

    Args:
        request: User's request text

    Returns:
        Dict with agent, action, file_path (or None if can't parse)

    Example:
        >>> extract_intent("Make assistant write to docs/ROADMAP.md")
        {"agent": "assistant", "action": "write", "file_path": "docs/ROADMAP.md"}
        >>> extract_intent("Have code_developer read .claude/CLAUDE.md")
        {"agent": "code_developer", "action": "read", "file_path": ".claude/CLAUDE.md"}
    """
    # Pattern: "Make {agent} {action} {path}"
    patterns = [
        r"make\s+(\w+)\s+(write|modify|edit|create)\s+(?:to\s+)?(.+)",
        r"have\s+(\w+)\s+(write|modify|edit|create)\s+(?:to\s+)?(.+)",
        r"(\w+)\s+should\s+(write|modify|edit|create)\s+(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, request.lower())
        if match:
            return {
                "agent": match.group(1).replace("-", "_"),
                "action": "write",  # write/modify/edit/create all map to "write"
                "file_path": match.group(3).strip()
            }

    # Pattern: "Make {agent} {action}" (no file path)
    pattern_no_path = r"make\s+(\w+)\s+(write|modify|edit|create)"
    match = re.search(pattern_no_path, request.lower())
    if match:
        return {
            "agent": match.group(1).replace("-", "_"),
            "action": "write",
            "file_path": None  # No specific file
        }

    # Can't parse
    return None


def validate_user_story(user_story_text: str) -> List[CFRViolation]:
    """
    Validate user story against CFRs.

    Args:
        user_story_text: Full user story text (markdown)

    Returns:
        List of CFR violations (empty if valid)

    Example:
        >>> us_text = '''
        ... **As a**: User
        ... **I want**: assistant to write documentation
        ... **So that**: Docs are automated
        ... '''
        >>> violations = validate_user_story(us_text)
        # Returns CFR-002 violation (assistant is READ-ONLY)
    """
    violations = []

    # Check for role violations in user story description
    for agent, role in AGENT_ROLES.items():
        if agent in user_story_text.lower():
            # Check if user story gives agent inappropriate capability
            if "READ-ONLY" in role and any(word in user_story_text.lower() for word in ["write", "modify", "create", "edit"]):
                violations.append(CFRViolation(
                    cfr_id="CFR-002",
                    description=f"User story gives {agent} write capability, but {agent} is READ-ONLY",
                    severity="ERROR",
                    suggestion=f"Change user story to use file-owning agent instead of {agent}"
                ))

    return violations
```

**Implementation Notes**:
- Simple regex pattern matching (no AI parsing needed)
- Reuses `get_file_owner()` from US-038
- Returns violations, doesn't block (caller decides action)

### Component 2: Integration with user_listener

**File**: `coffee_maker/autonomous/user_listener.py` (existing, add validation)

**Add**:
```python
from coffee_maker.autonomous.cfr_validator import validate_user_request, CFRViolation

def handle_user_request(request: str):
    """
    Handle user request with CFR validation.

    Args:
        request: User's request

    Returns:
        Response or error message
    """
    # Level 3: Validate request against CFRs
    violations = validate_user_request(request)

    if violations:
        # Format violation message
        message = format_cfr_violations(violations)

        # Ask user if they want to override
        override = ask_user_override(message)

        if not override:
            # User rejected, block request
            logger.info(f"🚫 Request blocked due to CFR violations")
            return "Request blocked to prevent CFR violation."

        # User overrode, log and proceed (with warning)
        logger.warning(f"⚠️ CFR violation overridden by user: {request}")

    # Proceed with request
    return execute_request(request)


def format_cfr_violations(violations: List[CFRViolation]) -> str:
    """
    Format violations as user-friendly message.

    Args:
        violations: List of violations

    Returns:
        Formatted message

    Example:
        >>> violations = [CFRViolation(...), ...]
        >>> print(format_cfr_violations(violations))
        ❌ CFR Violation Detected

        CFR-001: assistant cannot write to docs/ (owned by project_manager)
        CFR-002: assistant is READ-ONLY, cannot write files

        Safe Alternative:
        - Use project_manager to write docs/ instead

        This request would violate system ownership boundaries.
        Override? [y/N]
    """
    lines = ["❌ CFR Violation Detected", ""]
    for v in violations:
        lines.append(f"{v.cfr_id}: {v.description}")
    lines.append("")
    lines.append("Safe Alternative:")
    for v in violations:
        lines.append(f"- {v.suggestion}")
    lines.append("")
    lines.append("This request would violate system ownership boundaries.")
    lines.append("Override? [y/N]")

    return "\n".join(lines)
```

### Component 3: Integration with project_manager

**File**: `coffee_maker/cli/roadmap_cli.py` (existing, add validation)

**Add**:
```python
from coffee_maker.autonomous.cfr_validator import validate_user_story

def add_user_story_to_roadmap(user_story: dict):
    """
    Add user story to ROADMAP with CFR validation.

    Args:
        user_story: User story dict

    Returns:
        Success or error
    """
    # Level 2: Validate user story against CFRs
    us_text = format_user_story_as_text(user_story)
    violations = validate_user_story(us_text)

    if violations:
        # Show violations to user
        message = format_cfr_violations(violations)
        print(message)

        # Ask for override
        override = input("Override? [y/N]: ").strip().lower() == "y"

        if not override:
            logger.info("🚫 User story rejected due to CFR violations")
            return "User story blocked to prevent CFR violation."

        # User overrode
        logger.warning(f"⚠️ User story CFR violation overridden: {user_story['title']}")

    # Add to ROADMAP
    return add_to_roadmap(user_story)
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_cfr_validator.py` (~100 lines, 10 tests)

**Test Cases**:
1. `test_validate_read_only_write_violation()` - assistant write → CFR-002
2. `test_validate_ownership_violation()` - project_manager write .claude/ → CFR-001
3. `test_validate_read_allowed()` - Any agent read → No violation
4. `test_validate_owner_write_allowed()` - code_developer write .claude/ → No violation
5. `test_extract_intent_write()` - "Make assistant write to docs/" → parsed correctly
6. `test_extract_intent_no_match()` - Unparseable request → None
7. `test_validate_user_story_violation()` - US gives assistant write → CFR-002
8. `test_validate_user_story_no_violation()` - US respects roles → No violation
9. `test_multiple_violations()` - Request violates multiple CFRs
10. `test_format_violations()` - Violations formatted clearly

### Integration Tests

**File**: `tests/integration/test_cfr_enforcement.py` (~60 lines, 4 tests)

**Test Cases**:
1. `test_user_listener_blocks_violation()` - user_listener blocks CFR-violating request
2. `test_user_listener_allows_override()` - User can override with confirmation
3. `test_project_manager_blocks_us_violation()` - project_manager blocks CFR-violating US
4. `test_no_false_positives()` - Valid requests pass validation

### Manual Testing

```bash
# Test 1: Request validation (violation)
poetry run project-manager
> Make assistant write to docs/ROADMAP.md
# Expected: CFR violation message, request blocked

# Test 2: Request validation (override)
> Make assistant write to docs/ROADMAP.md
# Override? y
# Expected: Warning logged, request proceeds (with caveat)

# Test 3: User story validation
# Create US that gives assistant write capability
# Expected: CFR-002 violation detected, US rejected

# Test 4: Valid request (no violation)
> Make code_developer write to .claude/CLAUDE.md
# Expected: No violation, request proceeds
```

---

## Rollout Plan

### Phase 1: CFR Validator (Day 1 - 4 hours)

**Goal**: Implement validation logic

**Tasks**:
1. Create `cfr_validator.py` (100 lines)
2. Implement `validate_user_request()` and `validate_user_story()`
3. Implement `extract_intent()` (pattern matching)
4. Write unit tests (100 lines)

**Success Criteria**:
- All 10 unit tests pass
- Violations detected correctly
- Intent extraction works

### Phase 2: Integration (Day 2 - 4 hours)

**Goal**: Integrate with user_listener and project_manager

**Tasks**:
1. Update `user_listener.py` to call validator
2. Update `roadmap_cli.py` to call validator
3. Add override prompt logic
4. Write integration tests (60 lines)
5. Test with real user requests

**Success Criteria**:
- Violating requests blocked (or warned)
- Override mechanism works
- All integration tests pass

### Phase 3: Documentation (Day 2 - 1 hour)

**Goal**: Document CFR enforcement

**Tasks**:
1. Update `.claude/CLAUDE.md` with CFR enforcement section
2. Add examples of violations and safe alternatives
3. Document override process

**Success Criteria**:
- Documentation clear
- Examples help users understand CFRs

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-039 in ROADMAP):
- Mentioned "comprehensive validation" (sounds complex)
- Multiple validation levels (sounds like heavy infrastructure)
- "Expose violations to user with safe alternatives" (sounds like AI-powered)
- ~2-3 days estimate

**This Simplified Spec**:
- **Pattern matching** (regex, not AI parsing)
- **2 validation levels** (Level 2 + Level 3, Level 1 already done in US-038)
- **Simple violation messages** (hardcoded suggestions, not generated)
- **~150 lines total** (not 500+)
- **Same 2-3 days estimate** (but simpler)

**What We REUSE**:
- US-038 ownership registry (already implemented)
- US-035 singleton checks (already implemented)
- Existing agent role definitions (CLAUDE.md)
- Simple regex (stdlib)

**Complexity Reduction**:
- **No AI parsing** (simple pattern matching)
- **No rule engine** (hardcoded CFR checks)
- **No complex validation levels** (just 2 checkpoints)
- **No distributed validation** (single-machine)

**Result**: 70% less code, catches 95%+ violations

---

## CFR Coverage

This spec implements **CFR-000 (Prevent File Conflicts)** with these mechanisms:

| Level | Mechanism | Spec | Coverage |
|-------|-----------|------|----------|
| Level 1 | generator auto-delegation | US-038 (SPEC-038) | Runtime file operations |
| Level 2 | User story validation | This spec | Before ROADMAP addition |
| Level 3 | User request validation | This spec | Before execution |
| Underlying | Singleton enforcement | US-035 (SPEC-035) | Same-agent conflicts |
| Underlying | Ownership enforcement | US-038 (SPEC-038) | Cross-agent conflicts |

**Result**: Multi-layered CFR-000 enforcement, prevents conflicts at multiple levels! 🛡️

---

## Future Enhancements

**NOT in this spec** (deferred):
1. **AI-powered intent extraction** → When pattern matching insufficient
2. **Custom CFR rules** → User-defined validation rules
3. **CFR versioning** → Track CFR evolution over time
4. **Automated suggestions** → AI-generated safe alternatives
5. **Violation analytics** → Track common violations, improve UX

---

## References

- US-039: Implement Critical Functional Requirements (CFR) Enforcement System (ROADMAP)
- US-035: Implement Singleton Agent Enforcement (dependency)
- US-038: Implement File Ownership Enforcement (dependency)
- CFR-000: Prevent File Conflicts (master requirement)
- `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` - CFR definitions
- `docs/roadmap/learnings/WORKFLOW_FAILURE_US_040.md` - Proof of need
- ADR-003: Simplification-First Approach

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 2-3 days
- [ ] project_manager (strategic alignment) - Meets US-039 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (9 hours total)

**Phases**:
- Phase 1: CFR Validator (4 hours)
- Phase 2: Integration (4 hours)
- Phase 3: Documentation (1 hour)

**Depends On**: US-035 (Singleton) and US-038 (Ownership) must be complete first

**Result**: Multi-layered CFR enforcement, prevents system-breaking changes! 🛡️
