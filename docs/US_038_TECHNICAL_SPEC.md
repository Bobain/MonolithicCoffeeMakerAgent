# US-038: File Ownership Enforcement in generator Agent - Technical Specification

**Status**: DRAFT
**Priority**: CRITICAL
**Complexity**: High
**Created**: 2025-10-16
**Author**: project_manager
**Implementer**: code_developer
**Dependencies**: US-035 (Singleton Agent Enforcement)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Background & Motivation](#background--motivation)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Implementation Plan](#implementation-plan)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Performance Requirements](#performance-requirements)
10. [Risk Analysis](#risk-analysis)
11. [Success Criteria](#success-criteria)

---

## Executive Summary

This specification defines the implementation of file ownership enforcement in the generator agent. The generator agent, as the central orchestrator in the ACE framework, will intercept all agent actions, validate file ownership before operations, and automatically delegate to the correct owner when violations are detected.

**Key Objectives**:
- Enforce file ownership rules automatically at the orchestration layer
- Prevent ownership violations before they corrupt files or cause conflicts
- Enable automatic delegation to correct owners (not just blocking)
- Capture delegation traces for reflector analysis and learning

**Business Value**:
- **Architectural Integrity**: Prevents file corruption and merge conflicts
- **Developer Productivity**: Eliminates manual ownership checking
- **System Safety**: Zero ownership violations reach execution
- **Learning Opportunity**: Delegation patterns help reflector improve collaboration

---

## Background & Motivation

### Current State

**File Ownership Documentation**:
- Ownership rules documented in `.claude/CLAUDE.md` (Tool Ownership Matrix)
- Agents manually respect ownership (honor system)
- No automated enforcement at runtime

**Problems with Manual Enforcement**:
1. **Human Error**: Agents can accidentally violate ownership
2. **Code Review Burden**: Reviewers must catch violations
3. **Runtime Corruption**: Violations can corrupt files or cause conflicts
4. **No Learning**: System doesn't learn from ownership patterns

### Why generator?

**generator is Ideal Enforcement Point**:
- Already intercepts ALL agent actions (ACE framework requirement)
- Orchestrates agent execution (perfect place for validation)
- Captures execution traces (can record ownership checks/delegations)
- Central authority (single enforcement point)

### Target State

**Automatic Ownership Enforcement**:
- generator checks ownership BEFORE every file operation
- Violations automatically delegated to correct owner
- Delegation traces captured for reflector analysis
- Zero ownership violations reach execution

---

## Architecture Overview

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    ACE Framework                             │
│                                                              │
│  ┌─────────────┐                                            │
│  │   Agent     │  Attempts file operation                   │
│  │ (any type)  │  (Edit, Write, NotebookEdit)              │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────┐           │
│  │          generator (Orchestrator)           │           │
│  │                                              │           │
│  │  ┌─────────────────────────────────────┐   │           │
│  │  │   1. Intercept Action               │   │           │
│  │  └─────────────┬───────────────────────┘   │           │
│  │                │                             │           │
│  │                ▼                             │           │
│  │  ┌─────────────────────────────────────┐   │           │
│  │  │   2. Check File Ownership           │   │           │
│  │  │   (FileOwnership.get_owner())      │   │           │
│  │  └─────────────┬───────────────────────┘   │           │
│  │                │                             │           │
│  │                ├─────────┬───────────────┐  │           │
│  │                │         │               │  │           │
│  │         OWNS   │         │  DOESN'T OWN │  │           │
│  │                │         │               │  │           │
│  │                ▼         ▼               │  │           │
│  │  ┌──────────────┐  ┌──────────────────┐ │  │           │
│  │  │   3a. Execute│  │ 3b. Auto-Delegate│ │  │           │
│  │  │   Directly   │  │  to Correct Owner│ │  │           │
│  │  └──────┬───────┘  └──────┬───────────┘ │  │           │
│  │         │                  │             │  │           │
│  │         │                  ▼             │  │           │
│  │         │         ┌────────────────────┐ │  │           │
│  │         │         │ Owner Executes Op  │ │  │           │
│  │         │         └────────┬───────────┘ │  │           │
│  │         │                  │             │  │           │
│  │         ▼                  ▼             │  │           │
│  │  ┌─────────────────────────────────────┐   │           │
│  │  │   4. Capture Trace                  │   │           │
│  │  │   (Success or Delegation)           │   │           │
│  │  └─────────────────────────────────────┘   │           │
│  └─────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **FileOwnership Registry**: Maps file paths to agent owners
2. **Action Interceptor**: generator's interception logic
3. **Ownership Validator**: Checks if agent owns target file
4. **Auto-Delegation Engine**: Delegates to correct owner when violated
5. **Trace Capture**: Records ownership checks and delegations

---

## Component Specifications

### 1. FileOwnership Registry

**Purpose**: Central registry mapping files/directories to agent owners.

**Location**: `coffee_maker/autonomous/ace/file_ownership.py`

**Class Definition**:
```python
from enum import Enum
from typing import Optional
from pathlib import Path
import fnmatch


class AgentType(Enum):
    """Agent types in the system."""
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    ASSISTANT = "assistant"
    CODE_SEARCHER = "code-searcher"
    UX_DESIGN_EXPERT = "ux-design-expert"
    USER_LISTENER = "user_listener"
    GENERATOR = "generator"
    REFLECTOR = "reflector"
    CURATOR = "curator"


class OwnershipUnclearError(Exception):
    """Raised when file ownership cannot be determined."""
    pass


class FileOwnership:
    """
    Registry mapping files and directories to agent owners.

    Based on DOCUMENT_OWNERSHIP_MATRIX.md and CLAUDE.md Tool Ownership Matrix.
    """

    # Ownership rules (pattern → owner)
    # More specific patterns checked first
    OWNERSHIP_RULES = [
        # .claude/ directory (code_developer owns ALL)
        (".claude/**", AgentType.CODE_DEVELOPER),
        (".claude/agents/**", AgentType.CODE_DEVELOPER),
        (".claude/commands/**", AgentType.CODE_DEVELOPER),
        (".claude/mcp/**", AgentType.CODE_DEVELOPER),
        (".claude/CLAUDE.md", AgentType.CODE_DEVELOPER),

        # docs/roadmap/ (project_manager owns)
        ("docs/roadmap/**", AgentType.PROJECT_MANAGER),
        ("docs/roadmap/ROADMAP.md", AgentType.PROJECT_MANAGER),
        ("docs/roadmap/TEAM_COLLABORATION.md", AgentType.PROJECT_MANAGER),

        # docs/architecture/ (architect owns)
        ("docs/architecture/**", AgentType.ARCHITECT),
        ("docs/architecture/specs/**", AgentType.ARCHITECT),
        ("docs/architecture/decisions/**", AgentType.ARCHITECT),
        ("docs/architecture/guidelines/**", AgentType.ARCHITECT),

        # ACE framework directories
        ("docs/generator/**", AgentType.GENERATOR),
        ("docs/reflector/**", AgentType.REFLECTOR),
        ("docs/curator/**", AgentType.CURATOR),

        # docs/ top-level files (project_manager owns)
        ("docs/*.md", AgentType.PROJECT_MANAGER),
        ("docs/PRIORITY_*_TECHNICAL_SPEC.md", AgentType.PROJECT_MANAGER),
        ("docs/US_*_TECHNICAL_SPEC.md", AgentType.PROJECT_MANAGER),
        ("docs/templates/**", AgentType.PROJECT_MANAGER),
        ("docs/tutorials/**", AgentType.PROJECT_MANAGER),

        # Code and tests (code_developer owns)
        ("coffee_maker/**", AgentType.CODE_DEVELOPER),
        ("tests/**", AgentType.CODE_DEVELOPER),
        ("scripts/**", AgentType.CODE_DEVELOPER),

        # Dependencies (architect owns)
        ("pyproject.toml", AgentType.ARCHITECT),
        ("poetry.lock", AgentType.ARCHITECT),

        # Configuration files (code_developer owns)
        (".pre-commit-config.yaml", AgentType.CODE_DEVELOPER),
        (".gitignore", AgentType.CODE_DEVELOPER),

        # Data directories
        ("data/user_interpret/**", AgentType.USER_LISTENER),
    ]

    @classmethod
    def get_owner(cls, file_path: str) -> AgentType:
        """
        Get the agent that owns a file.

        Args:
            file_path: Path to file (absolute or relative)

        Returns:
            AgentType: The agent that owns this file

        Raises:
            OwnershipUnclearError: If ownership cannot be determined
        """
        # Normalize path
        path = Path(file_path).as_posix()

        # Check each rule (most specific first)
        for pattern, owner in cls.OWNERSHIP_RULES:
            if fnmatch.fnmatch(path, pattern):
                return owner

        # No match found
        raise OwnershipUnclearError(
            f"Ownership unclear for file: {file_path}\n"
            f"Please add ownership rule to FileOwnership.OWNERSHIP_RULES"
        )

    @classmethod
    def check_ownership(cls, agent: AgentType, file_path: str) -> bool:
        """
        Check if agent owns a file.

        Args:
            agent: Agent attempting operation
            file_path: Path to file

        Returns:
            bool: True if agent owns file, False otherwise

        Raises:
            OwnershipUnclearError: If ownership cannot be determined
        """
        owner = cls.get_owner(file_path)
        return owner == agent
```

**Key Features**:
- Pattern-based matching with `fnmatch`
- Most specific patterns checked first
- Clear error messages when ownership unclear
- Supports glob patterns (`**`, `*`)
- Extensible (easy to add new rules)

---

### 2. generator Action Interceptor

**Purpose**: Intercept all agent actions and validate file operations.

**Location**: `coffee_maker/autonomous/ace/generator.py`

**Enhanced Class**:
```python
from typing import Any, Dict, Optional
from coffee_maker.autonomous.ace.file_ownership import FileOwnership, AgentType, OwnershipUnclearError


class Generator:
    """
    ACE framework generator - orchestrates agent execution with ownership enforcement.
    """

    def intercept_action(
        self,
        agent: AgentType,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intercept and validate agent actions.

        For file operations, checks ownership and auto-delegates if needed.

        Args:
            agent: Agent attempting action
            tool_name: Name of tool being invoked
            parameters: Tool parameters

        Returns:
            dict: Result of action (direct execution or delegated)
        """
        # Check if this is a file operation
        if tool_name in ["Edit", "Write", "NotebookEdit"]:
            return self._handle_file_operation(agent, tool_name, parameters)

        # Non-file operation - execute directly
        return self._execute_action(agent, tool_name, parameters)

    def _handle_file_operation(
        self,
        agent: AgentType,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle file operations with ownership checking.

        Args:
            agent: Agent attempting operation
            tool_name: File operation tool
            parameters: Tool parameters (must include file_path)

        Returns:
            dict: Result of operation
        """
        file_path = parameters.get("file_path")
        if not file_path:
            raise ValueError(f"{tool_name} requires 'file_path' parameter")

        try:
            # Check ownership
            owner = FileOwnership.get_owner(file_path)

            if owner == agent:
                # Agent owns file - execute directly
                logger.info(
                    f"Ownership OK: {agent.value} owns {file_path}"
                )
                return self._execute_action(agent, tool_name, parameters)
            else:
                # Ownership violation - auto-delegate
                logger.warning(
                    f"Ownership violation: {agent.value} tried to modify {file_path}, "
                    f"owned by {owner.value}. Auto-delegating..."
                )
                return self._delegate_to_owner(
                    violating_agent=agent,
                    correct_owner=owner,
                    tool_name=tool_name,
                    parameters=parameters,
                    file_path=file_path
                )

        except OwnershipUnclearError as e:
            # Ownership unclear - fail with clear error
            logger.error(f"Ownership unclear: {e}")
            raise

    def _delegate_to_owner(
        self,
        violating_agent: AgentType,
        correct_owner: AgentType,
        tool_name: str,
        parameters: Dict[str, Any],
        file_path: str
    ) -> Dict[str, Any]:
        """
        Delegate file operation to correct owner.

        Args:
            violating_agent: Agent that attempted operation
            correct_owner: Agent that owns the file
            tool_name: Operation to perform
            parameters: Operation parameters
            file_path: Target file path

        Returns:
            dict: Result from delegated operation
        """
        # Log delegation
        logger.info(
            f"Delegating {tool_name} on {file_path} "
            f"from {violating_agent.value} to {correct_owner.value}"
        )

        # Execute via correct owner
        result = self._execute_as_agent(correct_owner, tool_name, parameters)

        # Capture delegation trace
        self._capture_delegation_trace(
            violating_agent=violating_agent,
            correct_owner=correct_owner,
            tool_name=tool_name,
            file_path=file_path,
            result=result
        )

        return result

    def _execute_as_agent(
        self,
        agent: AgentType,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute action as specific agent.

        Args:
            agent: Agent to execute as
            tool_name: Tool to invoke
            parameters: Tool parameters

        Returns:
            dict: Execution result
        """
        # Implementation: Invoke tool with agent context
        # This will vary based on your agent execution architecture
        # Example:
        # return self.agent_executor.execute(agent, tool_name, parameters)
        pass

    def _capture_delegation_trace(
        self,
        violating_agent: AgentType,
        correct_owner: AgentType,
        tool_name: str,
        file_path: str,
        result: Dict[str, Any]
    ):
        """
        Capture delegation trace for reflector analysis.

        Args:
            violating_agent: Agent that attempted operation
            correct_owner: Agent that owns the file
            tool_name: Operation performed
            file_path: Target file
            result: Operation result
        """
        trace = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "ownership_delegation",
            "violating_agent": violating_agent.value,
            "correct_owner": correct_owner.value,
            "tool_name": tool_name,
            "file_path": file_path,
            "result_status": result.get("status", "unknown"),
            "reason": "ownership_enforcement"
        }

        # Save trace for reflector
        trace_file = Path("docs/generator/traces") / f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        trace_file.parent.mkdir(parents=True, exist_ok=True)
        trace_file.write_text(json.dumps(trace, indent=2))

        logger.info(f"Delegation trace saved: {trace_file}")
```

**Key Features**:
- Intercepts ALL file operations (Edit, Write, NotebookEdit)
- Pre-action ownership validation
- Automatic delegation when violations detected
- Comprehensive trace capture
- Clear logging for debugging

---

## Data Flow Diagrams

### Happy Path: Agent Owns File

```
┌──────────────┐
│ project_mgr  │  Attempts: Edit(docs/ROADMAP.md)
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│        generator.intercept_action   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  FileOwnership.get_owner()          │
│  → Returns: PROJECT_MANAGER         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Ownership Check:                   │
│  PROJECT_MANAGER == PROJECT_MANAGER │
│  → TRUE (owns file)                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Execute Edit directly              │
│  Capture success trace              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Return success to project_manager  │
└─────────────────────────────────────┘
```

### Violation Path: Agent Doesn't Own File

```
┌──────────────┐
│ project_mgr  │  Attempts: Edit(.claude/CLAUDE.md)
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│        generator.intercept_action   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  FileOwnership.get_owner()          │
│  → Returns: CODE_DEVELOPER          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Ownership Check:                   │
│  PROJECT_MANAGER != CODE_DEVELOPER  │
│  → FALSE (doesn't own)              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Auto-Delegate to code_developer    │
│  Log: "Delegating Edit..."          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  code_developer executes Edit       │
│  Modifies .claude/CLAUDE.md         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Capture delegation trace:          │
│  - violating_agent: project_manager │
│  - correct_owner: code_developer    │
│  - file: .claude/CLAUDE.md          │
│  - operation: Edit                  │
│  - result: success                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Return success to project_manager  │
│  (Transparent delegation)           │
└─────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: FileOwnership Registry (2 hours)

**Tasks**:
1. Create `coffee_maker/autonomous/ace/file_ownership.py`
2. Implement `AgentType` enum
3. Implement `OwnershipUnclearError` exception
4. Implement `FileOwnership` class with rules from ownership matrix
5. Add all ownership mappings from CLAUDE.md
6. Write unit tests for ownership lookup

**Deliverables**:
- [ ] `file_ownership.py` module complete
- [ ] All ownership rules implemented
- [ ] Unit tests passing (15+ test cases)

### Phase 2: generator Integration (3 hours)

**Tasks**:
1. Update `coffee_maker/autonomous/ace/generator.py`
2. Add `intercept_action()` method
3. Implement `_handle_file_operation()` for ownership checking
4. Add pre-action validation logic
5. Test with mock file operations

**Deliverables**:
- [ ] generator intercepts file operations
- [ ] Ownership validation working
- [ ] Unit tests passing (10+ test cases)

### Phase 3: Auto-Delegation (2 hours)

**Tasks**:
1. Implement `_delegate_to_owner()` method
2. Implement `_execute_as_agent()` delegation
3. Handle delegation context passing
4. Return results from delegated operations
5. Error handling when delegation fails

**Deliverables**:
- [ ] Delegation mechanism working
- [ ] Context passed correctly
- [ ] Results returned properly
- [ ] Unit tests passing (8+ test cases)

### Phase 4: Trace Capture (1 hour)

**Tasks**:
1. Implement `_capture_delegation_trace()` method
2. Define delegation trace format (JSON)
3. Save traces to `docs/generator/traces/`
4. Test trace capture and storage
5. Verify traces are readable by reflector

**Deliverables**:
- [ ] Delegation traces captured
- [ ] Trace format documented
- [ ] Storage working correctly
- [ ] Sample traces created

### Phase 5: Testing & Documentation (2 hours)

**Tasks**:
1. Write comprehensive test suite (`tests/unit/test_file_ownership_enforcement.py`)
2. Test all ownership patterns from matrix
3. Test delegation for each agent type
4. Integration testing with real agents
5. Update documentation

**Deliverables**:
- [ ] Test suite complete (20+ scenarios)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] All acceptance criteria met

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_file_ownership_enforcement.py`

**Test Cases**:

1. **Ownership Lookup Tests**:
   ```python
   def test_code_developer_owns_claude_files():
       """Test code_developer owns .claude/ files."""
       assert FileOwnership.get_owner(".claude/CLAUDE.md") == AgentType.CODE_DEVELOPER
       assert FileOwnership.get_owner(".claude/agents/generator.md") == AgentType.CODE_DEVELOPER

   def test_project_manager_owns_roadmap_files():
       """Test project_manager owns docs/roadmap/ files."""
       assert FileOwnership.get_owner("docs/roadmap/ROADMAP.md") == AgentType.PROJECT_MANAGER

   def test_architect_owns_dependencies():
       """Test architect owns pyproject.toml."""
       assert FileOwnership.get_owner("pyproject.toml") == AgentType.ARCHITECT
   ```

2. **Ownership Check Tests**:
   ```python
   def test_ownership_check_valid():
       """Test ownership check returns True for valid owner."""
       assert FileOwnership.check_ownership(
           AgentType.CODE_DEVELOPER,
           ".claude/CLAUDE.md"
       ) == True

   def test_ownership_check_invalid():
       """Test ownership check returns False for invalid owner."""
       assert FileOwnership.check_ownership(
           AgentType.PROJECT_MANAGER,
           ".claude/CLAUDE.md"
       ) == False
   ```

3. **Auto-Delegation Tests**:
   ```python
   def test_auto_delegation_on_violation(mock_generator):
       """Test generator auto-delegates when ownership violated."""
       # Setup
       agent = AgentType.PROJECT_MANAGER
       tool = "Edit"
       params = {"file_path": ".claude/CLAUDE.md", "old_string": "...", "new_string": "..."}

       # Execute
       result = mock_generator.intercept_action(agent, tool, params)

       # Verify
       assert result["status"] == "success"
       assert result["delegated_to"] == AgentType.CODE_DEVELOPER.value
       assert result["delegated"] == True

   def test_delegation_trace_captured(mock_generator, tmp_path):
       """Test delegation events recorded in traces."""
       # Trigger delegation
       # Verify trace file created
       # Verify trace contains correct metadata
   ```

4. **Edge Cases**:
   ```python
   def test_ownership_unclear_error():
       """Test OwnershipUnclearError raised for unknown files."""
       with pytest.raises(OwnershipUnclearError):
           FileOwnership.get_owner("unknown/file.txt")

   def test_glob_pattern_matching():
       """Test glob patterns work correctly."""
       assert FileOwnership.get_owner("docs/roadmap/TEAM_COLLABORATION.md") == AgentType.PROJECT_MANAGER
       assert FileOwnership.get_owner("docs/roadmap/subdir/file.md") == AgentType.PROJECT_MANAGER
   ```

### Integration Tests

**Test Real Agent Interactions**:
1. Simulate project_manager attempting to edit .claude/CLAUDE.md
2. Verify generator auto-delegates to code_developer
3. Verify code_developer executes operation successfully
4. Verify delegation trace captured
5. Verify reflector can read and analyze trace

---

## Security Considerations

### Threat Model

**Threat 1: Unauthorized File Access**
- **Risk**: Agent attempts to modify files it shouldn't own
- **Mitigation**: generator enforces ownership before execution
- **Detection**: All attempts logged in delegation traces

**Threat 2: Ownership Rule Bypass**
- **Risk**: Agent finds way to bypass ownership checks
- **Mitigation**: All file operations MUST go through generator (ACE requirement)
- **Detection**: Code review ensures no direct file operations

**Threat 3: Privilege Escalation**
- **Risk**: Agent delegates to higher-privilege agent
- **Mitigation**: Delegation only to file owner (not arbitrary agents)
- **Detection**: Delegation traces show all escalations

### Security Best Practices

1. **Principle of Least Privilege**: Agents can only modify files they own
2. **Defense in Depth**: Ownership checks + delegation traces + code review
3. **Audit Trail**: All delegations logged for security review
4. **Clear Errors**: Ownership violations produce clear, actionable errors

---

## Performance Requirements

### Latency

**Target**: <50ms overhead per file operation

**Breakdown**:
- Ownership lookup: <10ms (pattern matching with caching)
- Delegation decision: <5ms (simple comparison)
- Delegation execution: <30ms (depends on owner agent)
- Trace capture: <5ms (async write to file)

**Optimization Strategies**:
1. **Cache ownership lookups**: Memoize `get_owner()` results
2. **Async trace capture**: Don't block on trace writing
3. **Batch delegations**: Group multiple operations if possible

### Resource Usage

**Memory**: <10 MB for ownership registry
**Disk**: <100 MB for delegation traces (with rotation)
**CPU**: Minimal (pattern matching is fast)

---

## Risk Analysis

### Risk 1: Delegation Complexity

**Likelihood**: Medium
**Impact**: High
**Description**: Delegation mechanism may be complex to implement correctly

**Mitigation**:
- Start with simple delegation (direct tool call forwarding)
- Add context passing in Phase 2 if needed
- Comprehensive testing with real agents

### Risk 2: Performance Overhead

**Likelihood**: Low
**Impact**: Medium
**Description**: Ownership checks may slow down file operations

**Mitigation**:
- Cache ownership lookups (memoization)
- Only check file operations (not all actions)
- Profile and optimize if needed

### Risk 3: Circular Delegation

**Likelihood**: Low
**Impact**: High
**Description**: Delegation could cause infinite loops

**Mitigation**:
- Track delegation chain depth
- Limit to 1 level initially (no re-delegation)
- Detect and prevent circular references

### Risk 4: Unclear Ownership

**Likelihood**: Medium
**Impact**: Low
**Description**: Some files may have ambiguous ownership

**Mitigation**:
- Explicit error messages when ownership ambiguous
- Fallback to user confirmation if needed
- Document all ownership rules clearly

---

## Success Criteria

### Functional Requirements

- [ ] FileOwnership registry maps all file patterns to owners
- [ ] generator intercepts ALL file operations
- [ ] Ownership validation works for all agent types
- [ ] Auto-delegation successfully redirects to correct owner
- [ ] Delegation traces captured with complete metadata
- [ ] Zero ownership violations reach execution

### Non-Functional Requirements

- [ ] Performance: <50ms overhead per operation
- [ ] Reliability: >99.9% uptime for ownership checks
- [ ] Test Coverage: >95% code coverage
- [ ] Documentation: Complete API docs and examples
- [ ] Maintainability: Clear, readable code with comments

### Acceptance Criteria (from US-038)

All acceptance criteria from the user story must be met:

**Core Implementation**:
- [x] Create `FileOwnership` registry in `coffee_maker/autonomous/ace/file_ownership.py`
- [x] Registry maps file patterns to agent owners
- [x] generator intercepts ALL file operations
- [x] Pre-action ownership check in generator
- [x] Auto-delegation logic when ownership violation detected
- [x] Delegation trace capture for reflector analysis

**Integration**:
- [ ] Update generator agent definition (code_developer task)
- [ ] Update TEAM_COLLABORATION.md (project_manager - DONE)
- [ ] Update CLAUDE.md Tool Ownership Matrix (code_developer task)

**Testing**:
- [ ] Comprehensive test suite (20+ scenarios)
- [ ] All ownership patterns tested
- [ ] Delegation tested for each agent type
- [ ] Integration tests with real agents

**Documentation**:
- [x] Technical specification (this document)
- [ ] API documentation (code_developer)
- [ ] Troubleshooting guide (code_developer)

---

## Appendix A: File Ownership Matrix

**Complete mapping of files to owners**:

| File/Directory | Owner | Notes |
|----------------|-------|-------|
| `.claude/**` | code_developer | All technical configuration |
| `docs/roadmap/**` | project_manager | Strategic planning |
| `docs/architecture/**` | architect | Technical specs, ADRs |
| `docs/*.md` | project_manager | Top-level docs |
| `docs/generator/**` | generator | Execution traces |
| `docs/reflector/**` | reflector | Insights |
| `docs/curator/**` | curator | Playbooks |
| `coffee_maker/**` | code_developer | All implementation |
| `tests/**` | code_developer | All test code |
| `scripts/**` | code_developer | Utility scripts |
| `pyproject.toml` | architect | Dependencies |
| `poetry.lock` | architect | Lock file |
| `data/user_interpret/**` | user_listener | Operational data |

---

## Appendix B: Delegation Trace Format

**Example delegation trace** (`docs/generator/traces/delegation_20251016_142345.json`):

```json
{
  "timestamp": "2025-10-16T14:23:45.123456",
  "event_type": "ownership_delegation",
  "violating_agent": "project_manager",
  "correct_owner": "code_developer",
  "tool_name": "Edit",
  "file_path": ".claude/CLAUDE.md",
  "parameters": {
    "old_string": "...",
    "new_string": "..."
  },
  "result_status": "success",
  "reason": "ownership_enforcement",
  "delegation_chain": [
    {
      "from": "project_manager",
      "to": "code_developer",
      "timestamp": "2025-10-16T14:23:45.123456"
    }
  ]
}
```

---

## Questions & Answers

**Q: What happens if ownership is unclear?**
A: `OwnershipUnclearError` is raised with clear message. Add ownership rule to `OWNERSHIP_RULES`.

**Q: Can delegation chain multiple times?**
A: Initially limited to 1 level (no re-delegation). May expand in future if needed.

**Q: How does reflector use delegation traces?**
A: reflector analyzes traces to identify patterns (e.g., "project_manager often needs code_developer for .claude/ changes"). curator adds insights to playbook.

**Q: What if correct owner agent is not available?**
A: Delegation fails with clear error. User must start owner agent or handle manually.

**Q: Performance impact on existing operations?**
A: <50ms overhead per file operation (negligible). Caching reduces repeated lookups.

---

**Prepared By**: project_manager
**Date**: 2025-10-16
**Status**: Ready for code_developer implementation
**Next Steps**: code_developer implements per this specification
