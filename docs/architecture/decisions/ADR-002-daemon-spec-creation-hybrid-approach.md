# ADR-002: Daemon Spec Creation - Hybrid Approach (Template + Tool Use API)

**Status**: Accepted
**Date**: 2025-10-16
**Author**: architect agent
**Related**: US-045, SPEC-045-daemon-architect-delegation-fix.md

---

## Context

The daemon is stuck in an infinite loop when attempting to create technical specifications for ROADMAP priorities. The current implementation tries to "delegate" spec creation to the architect agent by calling `claude.execute_prompt()` with a delegation prompt. However, this approach is fundamentally flawed because:

1. **Anthropic API Limitation**: The `execute_prompt()` method uses the Anthropic Messages API for text generation. It does NOT:
   - Invoke subagents
   - Execute tool calls
   - Create files
   - Run commands

2. **No Actual File Creation**: The API returns text responses like "To create the specification, I would need to..." but no actual spec file is created.

3. **Infinite Loop Result**: The daemon checks for the spec file, doesn't find it, returns False, sleeps, and tries again indefinitely.

This blocks ALL autonomous ROADMAP progress, making it a CRITICAL blocker (Priority #1).

### Why This Matters

- **Autonomous Development Blocked**: The daemon cannot progress past any priority requiring a technical spec
- **PRIORITY 9 Stuck**: Current priority needs a spec, daemon loops forever
- **Architectural Consistency**: US-045 correctly identifies that architect should own spec creation, but the implementation doesn't work

### Alternatives Considered

We evaluated several approaches to fix this issue:

#### Alternative A: Pure Text Generation (Current - REJECTED)
- Continue using `execute_prompt()` for delegation
- **Rejected**: Doesn't work - no file creation capability

#### Alternative B: Direct Spec Creation in Daemon
- Daemon creates specs itself without architect involvement
- Uses simple templates filled with priority details
- **Pros**: Simple, always works, immediate fix
- **Cons**: Lower quality specs, violates ownership boundaries

#### Alternative C: Tool Use API Only
- Use Anthropic's Tool Use API to enable actual file creation
- Claude can call tools like write_file, read_file, bash
- **Pros**: True architect delegation, high-quality specs
- **Cons**: Takes longer to implement, potential API issues

#### Alternative D: Hybrid Approach (SELECTED)
- **Phase 1**: Template-based fallback for immediate relief
- **Phase 2**: Tool Use API for long-term quality
- **Pros**: Immediate fix + proper architecture
- **Cons**: More complex, two code paths to maintain

---

## Decision

We will implement a **Hybrid Approach** with two phases:

### Phase 1: Immediate Fix (1 hour) - Template Fallback

Create `SpecTemplateManager` that generates basic specs from templates when architect delegation is unavailable or fails. This unblocks the daemon NOW.

**Key Components**:
```python
class SpecTemplateManager:
    def create_spec_from_template(
        self,
        priority: dict,
        spec_filename: str
    ) -> bool:
        """Generate basic spec from SPEC-000-template.md."""
        # Load template
        # Fill with priority details
        # Add "TODO: Architect review needed"
        # Write to docs/architecture/specs/
        pass
```

**Fallback Logic**:
```python
def _ensure_technical_spec(self, priority: dict) -> bool:
    # Check if spec exists
    if spec_exists:
        return True

    # Try architect delegation (Phase 2)
    if has_tool_use and create_with_tools():
        return True

    # FALLBACK: Use template
    return create_from_template()
```

### Phase 2: Proper Integration (5-7 hours) - Tool Use API

Enhance `ClaudeAPI` with Tool Use API support to enable true architect delegation with actual file creation.

**Key Components**:
```python
class ClaudeAPI:
    def execute_prompt_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        timeout: Optional[int] = None
    ) -> APIResult:
        """Execute with Tool Use API enabled.

        Allows Claude to:
        - Create files (write_file tool)
        - Read files (read_file tool)
        - Run commands (bash tool)
        """
        # Use Anthropic Tool Use API
        # Loop while stop_reason == "tool_use"
        # Execute tool calls
        # Return results
        pass
```

**Tool Definitions**:
```python
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
    # read_file, bash, glob tools...
]
```

---

## Consequences

### Positive

1. **Immediate Relief**: Daemon unblocked within 1 hour (Phase 1)
2. **Long-term Quality**: Proper architect integration via Tool Use API (Phase 2)
3. **Resilience**: Fallback mechanism if Tool Use has issues
4. **Incremental Deployment**: Can be rolled out in stages
5. **Risk Mitigation**: Template fallback ensures daemon always makes progress
6. **Maintains Separation**: architect still owns specs (even template-based ones marked for review)

### Negative

1. **Complexity**: Two code paths to maintain (template + Tool Use)
2. **Technical Debt**: Template specs may need architect refinement later
3. **Implementation Time**: Total 6-8 hours vs. 1 hour for template-only
4. **API Dependency**: Phase 2 depends on Anthropic Tool Use API availability
5. **Testing Overhead**: Need to test both template and Tool Use paths

### Mitigations

1. **Clear Documentation**: Document when each path is used
2. **Automated Tests**: Test both template and Tool Use scenarios
3. **Monitoring**: Track which path is used, spec quality metrics
4. **Gradual Migration**: Can disable Tool Use if issues arise
5. **Template Quality**: Make templates comprehensive enough for basic work

---

## Implementation Notes

### Phase 1: Template Fallback

**Files to Create**:
- `coffee_maker/autonomous/spec_template_manager.py` (new)
- `tests/unit/test_spec_template_manager.py` (new)

**Files to Update**:
- `coffee_maker/autonomous/daemon_spec_manager.py` (add fallback logic)

**Timeline**: 1 hour

### Phase 2: Tool Use API

**Files to Create**:
- `tests/unit/test_claude_api_tool_use.py` (new)
- `tests/ci_tests/test_daemon_tool_use.py` (new)

**Files to Update**:
- `coffee_maker/autonomous/claude_api_interface.py` (add Tool Use methods)
- `coffee_maker/autonomous/daemon_spec_manager.py` (add Tool Use logic)
- `.claude/CLAUDE.md` (document Tool Use approach)

**Timeline**: 5-7 hours

### Success Criteria

**Phase 1**:
- Daemon creates spec from template
- PRIORITY 9 has spec file
- Daemon progresses to implementation
- No infinite loop (>3 iterations with progress)

**Phase 2**:
- Tool Use API creates high-quality specs
- Specs include all required sections
- Fallback to template works
- All tests pass

---

## References

- **US-045**: Fix Daemon to Delegate Spec Creation to architect
- **SPEC-045**: Technical specification for daemon fix
- **Anthropic Tool Use Docs**: https://docs.anthropic.com/en/docs/tool-use
- **DOCUMENT_OWNERSHIP_MATRIX.md**: architect owns docs/architecture/specs/

---

## Decision Rationale

The hybrid approach balances:

1. **Urgency**: Phase 1 unblocks daemon immediately (CRITICAL)
2. **Quality**: Phase 2 enables proper architect delegation
3. **Reliability**: Template fallback ensures system always works
4. **Architecture**: Maintains proper separation of concerns

**Why Not Template-Only?**
- Violates architect ownership (even if marked for review)
- Lower quality specs for complex features
- Misses opportunity for true subagent delegation

**Why Not Tool Use-Only?**
- Takes 5-7 hours to implement (daemon blocked meanwhile)
- Single point of failure if Tool Use API has issues
- No fallback mechanism

**Why Hybrid?**
- Immediate fix (1 hour) + proper solution (5-7 hours)
- Resilient to Tool Use API issues
- Incremental deployment reduces risk
- Best of both worlds

---

## Review & Approval

**Reviewed By**: architect agent (self-review)
**Approved By**: Awaiting user approval
**Date**: 2025-10-16

**Approval Required For**:
- Phase 1 implementation (immediate)
- Phase 2 implementation (after Phase 1 proves stable)
- Any deviations from this plan

---

## Future Considerations

1. **Langfuse Integration**: Track which path (template vs. Tool Use) is used, measure spec quality
2. **Spec Quality Metrics**: Automated checks for spec completeness
3. **Architect Review Queue**: System for architect to review/enhance template specs
4. **Alternative Tools**: Explore other file creation mechanisms beyond Tool Use API
5. **Async Spec Creation**: Create specs in background while daemon works on other tasks

---

## Version History

- **v1.0** (2025-10-16): Initial decision - hybrid approach with template fallback + Tool Use API
