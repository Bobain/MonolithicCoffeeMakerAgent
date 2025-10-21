# SPEC-045: Fix Daemon Infinite Loop - Architect Delegation Issue

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-16
**Related**: US-045 (CRITICAL), docs/roadmap/ROADMAP.md PRIORITY 9
**Estimated Duration**: 6-8 hours

---

## Executive Summary

The daemon is stuck in an infinite loop when attempting to create technical specifications by delegating to the architect agent. The root cause is that the delegation mechanism uses the Anthropic API's text generation, which does NOT support subagent invocation. The daemon expects architect to create spec files, but the API call simply generates text responses without actually executing any actions.

**Critical Impact**: This blocks ALL autonomous ROADMAP progress, making it the #1 priority.

---

## Problem Statement

### Current Broken Workflow

```
Daemon Loop Iteration N:
1. daemon calls _ensure_technical_spec()
2. Builds architect delegation prompt (lines 203-236 in daemon_spec_manager.py)
3. Calls claude.execute_prompt() with delegation prompt
4. ❌ PROBLEM: execute_prompt() uses Anthropic API text generation
5. ❌ API returns TEXT explaining what should be done, NOT executing actions
6. daemon checks for spec file → NOT FOUND
7. Returns False → daemon tries again
8. ♾️ INFINITE LOOP BEGINS

Daemon keeps retrying because:
- _ensure_technical_spec() returns False (no spec created)
- _implement_priority() skips and moves to next iteration
- Next iteration runs same check → same failure
- Retry counter never increments because implementation never starts
```

### Root Cause Analysis

**The delegation approach is fundamentally flawed:**

1. **Anthropic API Limitation**: The `ClaudeAPI.execute_prompt()` method uses the Anthropic Messages API, which generates text responses. It does NOT:
   - Invoke subagents
   - Execute tool calls
   - Create files
   - Run commands

2. **No Tool Use API Integration**: The current implementation doesn't use Anthropic's Tool Use API, which is required for Claude to actually perform actions like:
   - Creating files
   - Running bash commands
   - Invoking subagents

3. **Architectural Mismatch**:
   - US-045 correctly identifies that architect should own spec creation
   - BUT the implementation tries to "delegate" via a text prompt
   - This creates a conceptual agent hierarchy that doesn't exist in the API

### Why Infinite Loop Occurs

```python
# daemon_spec_manager.py, line 136
result = self.claude.execute_prompt(delegation_prompt, timeout=600)

# This returns APIResult with TEXT content like:
# "To create the technical specification, I would need to..."
# BUT no actual spec file is created!

# daemon_spec_manager.py, lines 143-159
# Checks if spec file exists → NOT FOUND
# Returns False

# daemon.py, line 419
if not self._ensure_technical_spec(next_priority):
    logger.warning("⚠️  Could not ensure technical spec exists - skipping this priority")
    time.sleep(self.sleep_interval)
    continue  # ← Goes back to start of loop, tries same priority again
```

**Result**: Daemon is stuck on PRIORITY 9 indefinitely, cycling through:
- Sync roadmap
- Read PRIORITY 9
- Attempt spec creation (fails)
- Sleep 30s
- Repeat

---

## Proposed Solution

### Solution A: Claude CLI Tool Use Integration (RECOMMENDED)

**Concept**: Use Claude Desktop's Tool Use API to enable actual file creation and command execution.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                         Daemon Process                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. _ensure_technical_spec()                                    │
│     ├─ Check if spec exists                                     │
│     └─ If missing: delegate to architect                        │
│                                                                 │
│  2. Claude CLI with Tool Use API                                │
│     ├─ Build architect delegation prompt                        │
│     ├─ Include Tool Use instructions:                           │
│     │  • Available tools: Write, Read, Bash                     │
│     │  • Expected action: Create spec file in                   │
│     │    docs/architecture/specs/                               │
│     └─ Execute with tools enabled                               │
│                                                                 │
│  3. Claude executes with tools                                  │
│     ├─ Reads ROADMAP context                                    │
│     ├─ Analyzes priority requirements                           │
│     ├─ Uses Write tool to create spec file                      │
│     └─ Returns success                                          │
│                                                                 │
│  4. Daemon verification                                         │
│     ├─ Check if spec file exists                                │
│     ├─ Validate spec content                                    │
│     └─ Return True/False                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Changes**:

1. **Add Tool Use API Integration to ClaudeAPI**:
```python
class ClaudeAPI:
    def execute_prompt_with_tools(
        self,
        prompt: str,
        tools: list[dict],  # Tool definitions
        system_prompt: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> APIResult:
        """Execute prompt with tool use enabled.

        This allows Claude to actually perform actions like:
        - Creating files (Write tool)
        - Running commands (Bash tool)
        - Reading files (Read tool)
        """
        # Use Anthropic Tool Use API
        # https://docs.anthropic.com/en/docs/tool-use
        pass
```

2. **Update _ensure_technical_spec() to use tools**:
```python
def _ensure_technical_spec(self, priority: dict) -> bool:
    # ... existing spec check logic ...

    # Define available tools for architect
    tools = [
        {
            "name": "write_file",
            "description": "Create or overwrite a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "read_file",
            "description": "Read file contents",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    ]

    # Build delegation prompt (enhanced)
    prompt = self._build_architect_delegation_prompt_with_tools(priority, spec_prefix)

    # Execute WITH tools enabled
    result = self.claude.execute_prompt_with_tools(
        prompt=prompt,
        tools=tools,
        timeout=600
    )

    # Verify spec was created
    return self._verify_spec_created(spec_prefix)
```

3. **Enhanced Delegation Prompt**:
```python
def _build_architect_delegation_prompt_with_tools(self, priority: dict, spec_prefix: str) -> str:
    return f"""You are the architect agent. Create a technical specification for:

**Priority**: {priority['name']}
**Title**: {priority['title']}

**Your Task**:
1. Analyze the priority requirements
2. Create a comprehensive technical specification
3. Use the write_file tool to create: docs/architecture/specs/{spec_prefix}-<name>.md
4. Follow the SPEC template format

**Specification Requirements**:
- Problem Statement: What are we solving?
- Proposed Solution: High-level architecture
- Components: Detailed component design
- Data Structures: Key data models
- APIs: Interface definitions
- Testing Strategy: How to test
- Rollout Plan: Phased approach
- Risks & Mitigations: What could go wrong

**IMPORTANT**: You MUST use the write_file tool to actually create the spec file.
Simply describing the spec is not sufficient - you must create it.

**Context from ROADMAP**:
{priority.get('content', 'No content provided')}

Create the specification file now using the write_file tool.
"""
```

### Solution B: Direct Spec Creation in Daemon (FALLBACK)

**Concept**: If Tool Use API is not available, daemon creates specs directly using templates.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                         Daemon Process                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. _ensure_technical_spec()                                    │
│     ├─ Check if spec exists                                     │
│     └─ If missing: create spec from template                    │
│                                                                 │
│  2. Template-based spec generation                              │
│     ├─ Load SPEC-000-template.md                                │
│     ├─ Fill in priority details:                                │
│     │  • Priority name, title                                   │
│     │  • Problem statement from ROADMAP                         │
│     │  • Basic component structure                              │
│     ├─ Write to docs/architecture/specs/                        │
│     └─ Mark with TODO for architect review                      │
│                                                                 │
│  3. Daemon proceeds with implementation                         │
│     ├─ Basic spec exists (even if incomplete)                   │
│     └─ Can be refined by architect later                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Pros**: Simple, always works, unblocks daemon immediately
**Cons**: Specs may be lower quality, doesn't leverage architect agent

---

## Recommended Approach: Hybrid Solution

**Phase 1: Immediate Fix (1 hour)**
- Implement Solution B (template-based) to unblock daemon NOW
- Add clear TODOs for architect to review and enhance
- Daemon can continue autonomous work

**Phase 2: Proper Integration (5-7 hours)**
- Implement Solution A (Tool Use API)
- Enable true architect delegation with file creation
- Migrate existing template specs to architect-created ones

### Why Hybrid?

1. **Immediate Relief**: Unblock daemon within 1 hour
2. **Long-term Quality**: Proper architecture with architect involvement
3. **Risk Mitigation**: Fallback mechanism if Tool Use has issues
4. **Incremental**: Can be deployed in stages

---

## Component Design

### 1. SpecTemplateManager (NEW)

**Purpose**: Generate basic specs from templates when architect delegation unavailable.

**Location**: `coffee_maker/autonomous/spec_template_manager.py`

**Interface**:
```python
class SpecTemplateManager:
    """Generate technical specifications from templates.

    This provides a fallback mechanism when architect agent
    delegation is not available or fails.
    """

    def __init__(self, template_path: str = "docs/architecture/specs/SPEC-000-template.md"):
        self.template_path = Path(template_path)

    def create_spec_from_template(
        self,
        priority: dict,
        spec_filename: str,
        output_dir: str = "docs/architecture/specs"
    ) -> bool:
        """Create a basic technical spec from template.

        Args:
            priority: Priority dict with name, title, content
            spec_filename: Output filename (e.g., "SPEC-045-daemon-fix.md")
            output_dir: Where to write spec

        Returns:
            True if spec created successfully

        Steps:
            1. Load template
            2. Extract priority details
            3. Fill template placeholders
            4. Add architect review TODO
            5. Write to output_dir
        """
        pass

    def _extract_problem_statement(self, priority: dict) -> str:
        """Extract problem statement from priority content."""
        pass

    def _generate_basic_architecture(self, priority: dict) -> str:
        """Generate basic architecture outline."""
        pass
```

**Template Variables**:
- `{PRIORITY_NAME}`: e.g., "US-045"
- `{PRIORITY_TITLE}`: e.g., "Fix Daemon Infinite Loop"
- `{PROBLEM_STATEMENT}`: Extracted from ROADMAP content
- `{DATE}`: Current date
- `{BASIC_ARCHITECTURE}`: Auto-generated outline based on priority type

### 2. Enhanced ClaudeAPI (UPDATED)

**Purpose**: Add Tool Use API support for true subagent delegation.

**Location**: `coffee_maker/autonomous/claude_api_interface.py`

**New Methods**:
```python
class ClaudeAPI:
    """Enhanced with Tool Use API support."""

    def execute_prompt_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        system_prompt: Optional[str] = None,
        timeout: Optional[int] = None,
        max_tool_iterations: int = 5,
    ) -> APIResult:
        """Execute prompt with tool use enabled.

        Args:
            prompt: User prompt
            tools: List of tool definitions (Anthropic format)
            system_prompt: Optional system context
            timeout: Request timeout
            max_tool_iterations: Max tool call cycles

        Returns:
            APIResult with tool use information

        Implementation:
            1. Send initial message with tools
            2. Loop while stop_reason == "tool_use":
               a. Extract tool calls from response
               b. Execute tools (file ops, bash, etc.)
               c. Send tool results back
               d. Get next response
            3. Return final result
        """
        pass

    def _execute_tool_call(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a single tool call.

        Args:
            tool_name: Name of tool (write_file, read_file, bash)
            tool_input: Tool-specific parameters

        Returns:
            Tool execution result
        """
        pass

    def _define_standard_tools(self) -> list[dict]:
        """Define standard tools for architect work.

        Returns:
            List of tool definitions:
            - write_file: Create/overwrite files
            - read_file: Read file contents
            - bash: Execute bash commands
            - glob: Find files by pattern
        """
        pass
```

**Tool Execution**:
```python
def _execute_tool_call(self, tool_name: str, tool_input: dict) -> dict:
    """Execute tool and return result."""

    if tool_name == "write_file":
        path = Path(tool_input["path"])
        content = tool_input["content"]
        path.write_text(content)
        return {"success": True, "path": str(path)}

    elif tool_name == "read_file":
        path = Path(tool_input["path"])
        if not path.exists():
            return {"success": False, "error": "File not found"}
        return {"success": True, "content": path.read_text()}

    elif tool_name == "bash":
        import subprocess
        result = subprocess.run(
            tool_input["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool_input.get("timeout", 30)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
```

### 3. Updated SpecManagerMixin (UPDATED)

**Purpose**: Use hybrid approach - try Tool Use, fall back to template.

**Location**: `coffee_maker/autonomous/daemon_spec_manager.py`

**Updated Logic**:
```python
class SpecManagerMixin:
    """Enhanced spec management with hybrid approach."""

    def _ensure_technical_spec(self, priority: dict) -> bool:
        """Ensure spec exists using hybrid approach.

        Strategy:
            1. Check if spec already exists → return True
            2. Try architect delegation with Tool Use API
            3. If fails: Fall back to template generation
            4. Verify spec was created

        Returns:
            True if spec exists or was created
        """
        # Check existing
        if self._spec_exists(spec_prefix):
            return True

        logger.info("Attempting architect delegation with Tool Use API...")

        # Try Solution A: Tool Use API
        if self._has_tool_use_support():
            if self._create_spec_with_architect_tools(priority, spec_prefix):
                logger.info("✅ Spec created via architect (Tool Use API)")
                return True
            else:
                logger.warning("⚠️  Architect delegation failed, falling back to template")
        else:
            logger.info("Tool Use API not available, using template fallback")

        # Fallback: Solution B - Template
        if self._create_spec_from_template(priority, spec_prefix):
            logger.info("✅ Spec created from template (architect review needed)")
            return True

        logger.error("❌ Failed to create spec using any method")
        return False

    def _has_tool_use_support(self) -> bool:
        """Check if ClaudeAPI supports Tool Use."""
        return hasattr(self.claude, 'execute_prompt_with_tools')

    def _create_spec_with_architect_tools(self, priority: dict, spec_prefix: str) -> bool:
        """Create spec using architect with Tool Use API."""
        # Build prompt with tool instructions
        prompt = self._build_architect_delegation_prompt_with_tools(priority, spec_prefix)

        # Define tools
        tools = self.claude._define_standard_tools()

        # Execute with tools
        result = self.claude.execute_prompt_with_tools(
            prompt=prompt,
            tools=tools,
            timeout=600
        )

        if not result.success:
            return False

        # Verify spec was created
        return self._verify_spec_created(spec_prefix)

    def _create_spec_from_template(self, priority: dict, spec_prefix: str) -> bool:
        """Create spec from template as fallback."""
        from coffee_maker.autonomous.spec_template_manager import SpecTemplateManager

        manager = SpecTemplateManager()
        spec_filename = f"{spec_prefix}-{priority['name'].lower().replace(' ', '-')}.md"

        return manager.create_spec_from_template(
            priority=priority,
            spec_filename=spec_filename
        )
```

---

## Data Structures

### Tool Definition Format (Anthropic API)

```json
{
  "name": "write_file",
  "description": "Create or overwrite a file with content",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "File path relative to project root"
      },
      "content": {
        "type": "string",
        "description": "File contents to write"
      }
    },
    "required": ["path", "content"]
  }
}
```

### Enhanced APIResult

```python
@dataclass
class APIResult:
    content: str
    model: str
    usage: dict
    stop_reason: str
    error: Optional[str] = None

    # NEW: Tool use information
    tool_calls: Optional[list[dict]] = None  # Tool calls made during execution
    tool_results: Optional[list[dict]] = None  # Results from tool executions

    @property
    def used_tools(self) -> bool:
        """Check if response used any tools."""
        return self.tool_calls is not None and len(self.tool_calls) > 0
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/unit/test_spec_template_manager.py`

```python
def test_create_spec_from_template():
    """Test basic spec creation from template."""
    manager = SpecTemplateManager()

    priority = {
        "name": "US-999",
        "title": "Test Priority",
        "content": "Test implementation details"
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-999-test.md",
            output_dir=tmpdir
        )

        assert result == True
        assert Path(tmpdir, "SPEC-999-test.md").exists()

        # Verify content
        spec = Path(tmpdir, "SPEC-999-test.md").read_text()
        assert "US-999" in spec
        assert "Test Priority" in spec
        assert "TODO: Review by architect" in spec
```

**Test File**: `tests/unit/test_claude_api_tool_use.py`

```python
def test_execute_prompt_with_tools_writes_file():
    """Test Tool Use API creates files."""
    api = ClaudeAPI()

    # Mock Anthropic client to return tool_use response
    with patch.object(api, 'client') as mock_client:
        # Configure mock to return tool call
        mock_client.messages.create.return_value = Mock(
            stop_reason="tool_use",
            content=[{
                "type": "tool_use",
                "name": "write_file",
                "input": {
                    "path": "test.txt",
                    "content": "Hello"
                }
            }]
        )

        # Execute
        result = api.execute_prompt_with_tools(
            prompt="Create test.txt",
            tools=[...]
        )

        # Verify file was created
        assert Path("test.txt").exists()
        assert Path("test.txt").read_text() == "Hello"
```

### Integration Tests

**Test File**: `tests/ci_tests/test_daemon_spec_creation.py`

```python
def test_daemon_creates_spec_for_priority():
    """Test daemon can create spec and proceed with implementation."""

    # Create test ROADMAP with priority needing spec
    roadmap_content = """
    ### PRIORITY 999: Test Feature 📝 Planned
    Test priority for integration testing.
    """
    Path("docs/roadmap/ROADMAP.md").write_text(roadmap_content)

    # Run daemon for one iteration
    daemon = DevDaemon(auto_approve=True)

    # Patch _implement_priority to avoid actual implementation
    with patch.object(daemon, '_implement_priority', return_value=True):
        # Run one iteration
        daemon._run_one_iteration()

    # Verify spec was created
    specs = list(Path("docs/architecture/specs").glob("SPEC-999-*.md"))
    assert len(specs) == 1

    # Verify daemon didn't get stuck
    # (check it moved past spec creation)
    assert daemon.attempted_priorities.get("PRIORITY 999", 0) > 0
```

### Manual Testing

**Test Scenario 1: Daemon with Tool Use API**
```bash
# Prerequisites: Anthropic API key configured

# 1. Add test priority to ROADMAP
cat >> docs/roadmap/ROADMAP.md << 'EOF'
### PRIORITY 999: Test Tool Use 📝 Planned
Test priority to verify Tool Use API spec creation.
This should create a spec via architect agent using Tool Use API.
EOF

# 2. Run daemon
poetry run code-developer --auto-approve

# 3. Verify spec created
ls docs/architecture/specs/SPEC-999-*

# 4. Check spec quality
cat docs/architecture/specs/SPEC-999-test-tool-use.md
# Should contain: Problem Statement, Architecture, Components, etc.

# 5. Verify daemon progressed
tail -20 logs/daemon.log
# Should show: "✅ Spec created via architect (Tool Use API)"
```

**Test Scenario 2: Template Fallback**
```bash
# Prerequisites: Disable Tool Use API temporarily

# 1. Add test priority
cat >> docs/roadmap/ROADMAP.md << 'EOF'
### PRIORITY 998: Test Template Fallback 📝 Planned
Test priority to verify template-based spec creation.
EOF

# 2. Run daemon with Tool Use disabled
export DISABLE_TOOL_USE=1
poetry run code-developer --auto-approve

# 3. Verify spec created from template
cat docs/architecture/specs/SPEC-998-test-template-fallback.md
# Should contain: "TODO: Review by architect"

# 4. Verify daemon progressed
tail -20 logs/daemon.log
# Should show: "✅ Spec created from template (architect review needed)"
```

**Test Scenario 3: Verify No Infinite Loop**
```bash
# Test that daemon doesn't get stuck

# 1. Add priority requiring spec
cat >> docs/roadmap/ROADMAP.md << 'EOF'
### PRIORITY 997: Loop Prevention Test 📝 Planned
Priority to verify daemon doesn't loop infinitely.
EOF

# 2. Run daemon for 5 minutes
timeout 300 poetry run code-developer --auto-approve

# 3. Check iteration count
grep "Iteration" logs/daemon.log | tail -10

# 4. Verify multiple iterations occurred (not stuck)
# Should see iteration numbers incrementing
```

---

## Rollout Plan

### Phase 1: Immediate Fix (1 hour) - PRIORITY

**Goal**: Unblock daemon NOW with template-based fallback

**Steps**:
1. Create `SpecTemplateManager` class (30 min)
   - Load template
   - Fill placeholders
   - Write spec file

2. Update `SpecManagerMixin` with fallback logic (20 min)
   - Add `_create_spec_from_template()` method
   - Update `_ensure_technical_spec()` to use fallback
   - Add logging

3. Test with PRIORITY 9 (10 min)
   - Run daemon
   - Verify spec created
   - Confirm daemon progresses

**Success Criteria**:
- Daemon creates basic spec from template
- PRIORITY 9 has spec file
- Daemon moves to implementation phase
- No infinite loop

### Phase 2: Tool Use API Integration (5-7 hours)

**Goal**: Enable true architect delegation with file creation

**Steps**:
1. Add Tool Use API to ClaudeAPI (3 hours)
   - Implement `execute_prompt_with_tools()`
   - Add `_execute_tool_call()` method
   - Define standard tools
   - Add tool execution loop
   - Handle tool errors gracefully

2. Update delegation prompts (1 hour)
   - Create `_build_architect_delegation_prompt_with_tools()`
   - Add clear tool usage instructions
   - Include spec format requirements

3. Integration testing (2 hours)
   - Test with PRIORITY 9
   - Test with various priority types
   - Verify spec quality
   - Test fallback when Tool Use fails

4. Documentation (1 hour)
   - Update CLAUDE.md
   - Add Tool Use examples
   - Document fallback behavior

**Success Criteria**:
- Tool Use API creates high-quality specs
- Specs match architect template format
- Fallback works if Tool Use unavailable
- All tests pass

### Phase 3: Migration & Cleanup (Optional)

**Goal**: Clean up template specs, migrate to architect-created

**Steps**:
1. Review template-created specs
2. Re-create with Tool Use API if quality issues
3. Remove template fallback (optional)

---

## Risks & Mitigations

### Risk 1: Tool Use API Quota/Rate Limits

**Impact**: High
**Probability**: Medium

**Mitigation**:
- Keep template fallback as backup
- Add rate limit detection
- Implement exponential backoff
- Cache specs once created

### Risk 2: Tool Use API Bugs/Issues

**Impact**: High
**Probability**: Low

**Mitigation**:
- Extensive integration testing
- Keep template fallback
- Monitor error rates
- Quick rollback plan

### Risk 3: Spec Quality Issues

**Impact**: Medium
**Probability**: Medium

**Mitigation**:
- Use detailed prompts for Tool Use
- Add spec validation
- Human review for critical priorities
- Iterate on prompt quality

### Risk 4: File Permission Issues

**Impact**: Medium
**Probability**: Low

**Mitigation**:
- Check write permissions before tool execution
- Add clear error messages
- Fall back to template if permissions fail
- Document required permissions

### Risk 5: Long Spec Creation Time

**Impact**: Low
**Probability**: Medium

**Mitigation**:
- Set reasonable timeouts (10 min)
- Show progress in status
- Allow async spec creation in future
- Cache created specs

---

## Success Criteria

### Phase 1 Success (Immediate Fix)

1. Daemon creates spec from template for PRIORITY 9
2. Spec file exists: `docs/architecture/specs/SPEC-009-enhanced-communication.md`
3. Daemon proceeds to implementation phase
4. No infinite loop detected (>3 iterations with progress)
5. Template specs marked for architect review

### Phase 2 Success (Tool Use Integration)

1. Tool Use API successfully creates specs
2. Specs include all required sections:
   - Problem Statement
   - Proposed Solution
   - Architecture diagrams
   - Component design
   - Testing strategy
   - Rollout plan
3. Fallback to template works when Tool Use unavailable
4. All unit and integration tests pass
5. Daemon completes PRIORITY 9 end-to-end

### Overall Success

1. No more infinite loops
2. Daemon progresses through ROADMAP autonomously
3. Specs created automatically before implementation
4. architect agent properly invoked via Tool Use API
5. System is resilient (fallback works)

---

## Appendix A: Tool Use API Reference

### Anthropic Tool Use Documentation

**URL**: https://docs.anthropic.com/en/docs/tool-use

**Key Concepts**:
- Tools are defined in request with JSON schema
- Claude decides when to use tools
- stop_reason "tool_use" indicates tool call
- Send tool results back to continue conversation

**Example Request**:
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[{
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }],
    messages=[{
        "role": "user",
        "content": "Create spec.md with content 'Hello'"
    }]
)

# Response includes tool_use
# Extract and execute tool call
# Send result back for final response
```

---

## Appendix B: Template Spec Format

**Location**: `docs/architecture/specs/SPEC-000-template.md`

**Template Structure**:
```markdown
# SPEC-{NUMBER}: {TITLE}

**Status**: Draft
**Author**: architect agent (via template)
**Date**: {DATE}
**Related**: {PRIORITY_NAME}

⚠️ **TODO: This spec was auto-generated from template. Architect review recommended.**

## Problem Statement

{EXTRACTED_FROM_ROADMAP}

## Proposed Solution

{BASIC_OUTLINE}

## Architecture

TODO: Add architecture diagrams and component design

## Components

TODO: Define key components and their responsibilities

## Technical Details

TODO: Add data structures, APIs, algorithms

## Testing Strategy

TODO: Define unit, integration, and E2E test plans

## Rollout Plan

TODO: Define phased rollout approach

## Risks & Mitigations

TODO: Identify risks and mitigation strategies
```

---

## Appendix C: Current vs. Fixed Workflow

### Current (BROKEN):

```
┌──────────────────────────────────────┐
│         Daemon Iteration N           │
├──────────────────────────────────────┤
│ 1. Read PRIORITY 9                   │
│ 2. Check for spec → NOT FOUND        │
│ 3. Build delegation prompt           │
│ 4. Call execute_prompt()             │
│    ├─ Anthropic API returns TEXT     │
│    ├─ No actual file creation!       │
│    └─ Returns APIResult with text    │
│ 5. Check for spec → STILL NOT FOUND  │
│ 6. Return False                      │
│ 7. Skip implementation                │
│ 8. Sleep 30s                          │
│ 9. Go to step 1 ♾️ INFINITE LOOP     │
└──────────────────────────────────────┘
```

### Fixed (Phase 1 - Template):

```
┌──────────────────────────────────────┐
│         Daemon Iteration N           │
├──────────────────────────────────────┤
│ 1. Read PRIORITY 9                   │
│ 2. Check for spec → NOT FOUND        │
│ 3. Try Tool Use API                  │
│    └─ Not available/fails            │
│ 4. FALLBACK: Use template            │
│    ├─ Load SPEC-000-template.md      │
│    ├─ Fill with priority details     │
│    ├─ Write to specs/SPEC-009-*.md   │
│    └─ Mark for architect review      │
│ 5. Check for spec → ✅ FOUND         │
│ 6. Return True                       │
│ 7. Proceed to implementation         │
│ 8. Complete priority                 │
│ 9. Move to next priority ✅ PROGRESS │
└──────────────────────────────────────┘
```

### Fixed (Phase 2 - Tool Use):

```
┌──────────────────────────────────────┐
│         Daemon Iteration N           │
├──────────────────────────────────────┤
│ 1. Read PRIORITY 9                   │
│ 2. Check for spec → NOT FOUND        │
│ 3. Try Tool Use API                  │
│    ├─ Build architect prompt         │
│    ├─ Define tools (write, read)     │
│    ├─ Execute with tools enabled     │
│    ├─ Claude analyzes priority       │
│    ├─ Claude calls write_file tool   │
│    ├─ Tool creates spec file         │
│    └─ Return success                 │
│ 4. Check for spec → ✅ FOUND         │
│ 5. Verify spec quality → ✅ GOOD     │
│ 6. Return True                       │
│ 7. Proceed to implementation         │
│ 8. Complete priority                 │
│ 9. Move to next priority ✅ PROGRESS │
└──────────────────────────────────────┘
```

---

## Appendix D: Time Estimates

### Development Time Breakdown

**Phase 1: Immediate Fix (1 hour)**
- SpecTemplateManager class: 30 min
- Update SpecManagerMixin: 20 min
- Testing with PRIORITY 9: 10 min

**Phase 2: Tool Use API (5-7 hours)**
- ClaudeAPI Tool Use methods: 3 hours
  - execute_prompt_with_tools: 1.5 hours
  - Tool execution logic: 1 hour
  - Error handling: 0.5 hours
- Enhanced delegation prompts: 1 hour
- Integration testing: 2 hours
- Documentation: 1 hour

**Total**: 6-8 hours

### Risk Buffer

Add 20% buffer for:
- Unexpected API issues
- Testing edge cases
- Documentation refinement
- Code review iterations

**Conservative Estimate**: 8-10 hours

---

## Conclusion

This specification provides a comprehensive solution to fix the daemon infinite loop issue (US-045). The hybrid approach ensures:

1. **Immediate relief** (Phase 1): Daemon unblocked within 1 hour using template fallback
2. **Long-term quality** (Phase 2): Proper architect integration via Tool Use API
3. **Resilience**: Fallback mechanism if Tool Use has issues
4. **Incremental deployment**: Can be rolled out in stages

The root cause is clear: text-based delegation doesn't work because the Anthropic API doesn't execute actions. The solution uses Tool Use API to enable actual file creation, with template fallback for reliability.

**Recommended Action**: Implement Phase 1 immediately to unblock daemon, then proceed with Phase 2 for proper long-term solution.
