# SPEC-054: Agent Context Budget Enforcement (CFR-007)

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CFR-007, US-050
**Estimated Duration**: 2-3 days (SIMPLIFIED)

---

## Executive Summary

Implement CFR-007: Enforce that each agent's core materials (prompt + owned critical documents + tools) consume ≤30% of context window, leaving 70% for actual work.

**Key Principle**: Agents must have room to work. Context budget enforcement prevents agent ineffectiveness from oversized core materials.

---

## Problem Statement

### Current Situation
- **No measurement**: We don't know how much context agents consume
- **No enforcement**: Nothing prevents core materials from growing to 100%
- **Agent ineffectiveness**: Some agents may already be context-constrained
- **No monitoring**: No visibility into context usage trends
- **No remediation**: No process to fix overages

### Root Cause
No system to:
1. Measure agent core context consumption
2. Enforce 30% budget limit
3. Monitor trends over time
4. Guide remediation when budget exceeded

### Goal
Create a lightweight context budget enforcement system with measurement, enforcement, monitoring, and remediation guidance.

### Non-Goals
- ❌ Automatic document compression (requires human judgment)
- ❌ Real-time context tracking during execution (only startup validation)
- ❌ Dynamic context window sizing (fixed 200K window)
- ❌ AI-powered document optimization (future enhancement)

---

## Proposed Solution: SIMPLIFIED APPROACH

### Core Concept
1. **Measure**: Count tokens in agent core materials (prompt + critical docs + tools)
2. **Enforce**: Block agent startup if >30% of context window
3. **Monitor**: Monthly reports showing usage trends
4. **Remediate**: Provide clear guidance when budget exceeded

### Architecture (SIMPLE)
```
Agent Startup
    ↓
Context Budget Check:
    - Count tokens in .claude/agents/{agent}.md
    - Count tokens in "Always Read" owned docs
    - Count tokens in tool descriptions
    ↓
Total > 30% of window?
    - YES: Block startup, show remediation steps
    - NO: Allow startup, log metrics
    ↓
Monthly Report:
    - Show all agent context usage
    - Highlight warnings (>70%)
    - Recommend optimizations
```

**NO complex systems, just token counting + validation!**

---

## Implementation Plan: PHASED & SIMPLE

### Phase 1: Context Measurement (Day 1 - 6 hours)

**Goal**: Measure how much context each agent consumes.

**Files to Create**:

1. **`coffee_maker/validation/context_budget.py`** (~200 lines)
   - Measure agent core context consumption
   - Validate against 30% budget
   - Generate context usage reports

   ```python
   """Context budget enforcement for CFR-007.

   Ensures agent core materials fit in ≤30% of context window.
   """

   from pathlib import Path
   from typing import Dict, List, NamedTuple
   import tiktoken

   # Constants
   CONTEXT_WINDOW_SIZE = 200_000  # tokens
   MAX_BUDGET_PERCENT = 0.30
   MAX_BUDGET_TOKENS = int(CONTEXT_WINDOW_SIZE * MAX_BUDGET_PERCENT)  # 60K

   class AgentContextUsage(NamedTuple):
       """Agent context usage breakdown."""
       agent_name: str
       prompt_tokens: int
       owned_docs_tokens: int
       tools_tokens: int
       total_tokens: int
       budget_percent: float
       status: str  # "OK" | "WARNING" | "CRITICAL" | "VIOLATION"

   class ContextBudgetEnforcer:
       """Enforce CFR-007 context budget limits."""

       def __init__(self):
           self.encoding = tiktoken.get_encoding("cl100k_base")
           self._agent_critical_docs = self._load_critical_docs_map()

       def _load_critical_docs_map(self) -> Dict[str, List[Path]]:
           """Load mapping of agents to their critical owned documents.

           Returns:
               Dict mapping agent name to list of "Always Read" document paths

           Example:
               {
                   "architect": [
                       Path("docs/architecture/decisions/ADR-003-simplification-first.md"),
                       Path("docs/DOCUMENT_OWNERSHIP_MATRIX.md")
                   ],
                   "project_manager": [
                       Path("docs/roadmap/ROADMAP.md"),
                       Path("docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md")
                   ]
               }
           """
           # Map from agent definitions (marked as "Always Read")
           return {
               "architect": [
                   Path("docs/roadmap/ROADMAP.md"),
                   Path(".claude/CLAUDE.md"),
                   Path(".claude/agents/architect.md"),
                   Path("docs/DOCUMENT_OWNERSHIP_MATRIX.md"),
               ],
               "code_developer": [
                   Path("docs/roadmap/ROADMAP.md"),
                   Path(".claude/CLAUDE.md"),
               ],
               "project_manager": [
                   Path("docs/roadmap/ROADMAP.md"),
                   Path("docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md"),
               ],
               "assistant": [
                   Path("docs/roadmap/ROADMAP.md"),
                   Path(".claude/CLAUDE.md"),
               ],
               "user_listener": [
                   Path(".claude/CLAUDE.md"),
               ],
               "code-searcher": [
                   # Code-searcher owns no documents
               ],
           }

       def count_tokens(self, text: str) -> int:
           """Count tokens in text using tiktoken."""
           return len(self.encoding.encode(text))

       def count_file_tokens(self, file_path: Path) -> int:
           """Count tokens in a file."""
           if not file_path.exists():
               return 0
           try:
               content = file_path.read_text(encoding="utf-8")
               return self.count_tokens(content)
           except Exception as e:
               print(f"Warning: Could not read {file_path}: {e}")
               return 0

       def measure_agent_context(self, agent_name: str) -> AgentContextUsage:
           """Measure total context consumption for an agent.

           Args:
               agent_name: Agent identifier (e.g., "architect")

           Returns:
               AgentContextUsage with breakdown and status
           """
           # 1. Agent prompt/role definition
           agent_file = Path(f".claude/agents/{agent_name}.md")
           prompt_tokens = self.count_file_tokens(agent_file)

           # 2. Critical owned documents (marked as "Always Read")
           owned_docs_tokens = 0
           critical_docs = self._agent_critical_docs.get(agent_name, [])
           for doc in critical_docs:
               owned_docs_tokens += self.count_file_tokens(doc)

           # 3. Tools (estimate ~3K tokens - rough average)
           # TODO: Measure actual tool descriptions if needed
           tools_tokens = 3000

           # Total
           total_tokens = prompt_tokens + owned_docs_tokens + tools_tokens
           budget_percent = (total_tokens / CONTEXT_WINDOW_SIZE) * 100

           # Status
           if total_tokens > MAX_BUDGET_TOKENS:
               status = "VIOLATION"
           elif budget_percent > 90:
               status = "CRITICAL"
           elif budget_percent > 70:
               status = "WARNING"
           else:
               status = "OK"

           return AgentContextUsage(
               agent_name=agent_name,
               prompt_tokens=prompt_tokens,
               owned_docs_tokens=owned_docs_tokens,
               tools_tokens=tools_tokens,
               total_tokens=total_tokens,
               budget_percent=budget_percent,
               status=status
           )

       def check_budget(self, agent_name: str) -> bool:
           """Check if agent complies with 30% budget.

           Args:
               agent_name: Agent to check

           Returns:
               True if compliant, False if violation

           Raises:
               ContextBudgetViolationError: If budget exceeded
           """
           usage = self.measure_agent_context(agent_name)

           if usage.status == "VIOLATION":
               raise ContextBudgetViolationError(
                   f"Agent '{agent_name}' violates CFR-007 context budget!\n"
                   f"\n"
                   f"Context Usage:\n"
                   f"  Prompt:      {usage.prompt_tokens:>8,} tokens\n"
                   f"  Owned Docs:  {usage.owned_docs_tokens:>8,} tokens\n"
                   f"  Tools:       {usage.tools_tokens:>8,} tokens\n"
                   f"  ─────────────────────────\n"
                   f"  TOTAL:       {usage.total_tokens:>8,} tokens ({usage.budget_percent:.1f}%)\n"
                   f"\n"
                   f"Budget Limit:  {MAX_BUDGET_TOKENS:>8,} tokens (30%)\n"
                   f"Overage:       {usage.total_tokens - MAX_BUDGET_TOKENS:>8,} tokens\n"
                   f"\n"
                   f"ACTION REQUIRED:\n"
                   f"1. Sharpen owned documents (remove verbosity)\n"
                   f"2. Split into main + detail documents\n"
                   f"3. Use line number references instead of full text\n"
                   f"4. Compress examples\n"
                   f"\n"
                   f"See: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md (CFR-007)\n"
               )

           return True

       def generate_monthly_report(self) -> str:
           """Generate monthly context budget report for all agents.

           Returns:
               Markdown report showing all agent context usage
           """
           agents = ["architect", "code_developer", "project_manager",
                    "assistant", "user_listener", "code-searcher"]

           usages = [self.measure_agent_context(a) for a in agents]

           report = "# Agent Context Budget Report\n\n"
           report += f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
           report += "## Summary\n\n"

           # Table
           report += "| Agent | Core Context | Max Allowed | Usage | Status |\n"
           report += "|-------|--------------|-------------|-------|--------|\n"

           for usage in usages:
               status_emoji = {
                   "OK": "✅",
                   "WARNING": "⚠️",
                   "CRITICAL": "❌",
                   "VIOLATION": "🚨"
               }[usage.status]

               report += (
                   f"| {usage.agent_name:<20} | "
                   f"{usage.total_tokens:>7,} | "
                   f"{MAX_BUDGET_TOKENS:>7,} | "
                   f"{usage.budget_percent:>5.1f}% | "
                   f"{status_emoji} {usage.status} |\n"
               )

           # Warnings
           warnings = [u for u in usages if u.status in ("WARNING", "CRITICAL", "VIOLATION")]
           if warnings:
               report += "\n## ⚠️ WARNINGS\n\n"
               for usage in warnings:
                   report += f"- **{usage.agent_name}**: {usage.budget_percent:.1f}% "
                   report += f"({usage.total_tokens:,} / {MAX_BUDGET_TOKENS:,} tokens)\n"
                   if usage.status == "VIOLATION":
                       report += f"  - 🚨 VIOLATION - Agent cannot start!\n"
                       report += f"  - Overage: {usage.total_tokens - MAX_BUDGET_TOKENS:,} tokens\n"
                   elif usage.status == "CRITICAL":
                       report += f"  - ❌ CRITICAL - Approaching limit\n"
                   else:
                       report += f"  - ⚠️ WARNING - Plan optimization\n"

           # Thresholds
           report += "\n## Thresholds\n\n"
           report += "- **0-70%**: ✅ Healthy (green zone)\n"
           report += "- **71-90%**: ⚠️ Warning (yellow zone) - plan remediation\n"
           report += "- **91-100%**: ❌ Critical (red zone) - immediate action\n"
           report += "- **>100%**: 🚨 VIOLATION - agent blocked from starting\n"

           return report

   class ContextBudgetViolationError(Exception):
       """Raised when agent exceeds 30% context budget."""
       pass
   ```

**Testing**:
- Measure each agent's context consumption
- Verify architect < 30% (currently should be OK)
- Verify project_manager (might be high due to ROADMAP + CFRs)
- Generate monthly report

**Acceptance Criteria**:
- ✅ Token counting works with tiktoken
- ✅ All agents measured accurately
- ✅ Budget validation raises error when exceeded
- ✅ Monthly report generated

---

### Phase 2: CLI Integration (Day 2 - 4 hours)

**Goal**: Add CLI commands for context budget checking.

**Files to Modify**:

1. **`coffee_maker/cli/roadmap_cli.py`** (~30 lines added)
   - Add command: `project-manager context-budget`
   - Add command: `project-manager context-budget <agent>`
   - Route to ContextBudgetEnforcer

   ```python
   # Add to roadmap_cli.py

   @chat_group.command("context-budget")
   @click.argument("agent", required=False)
   def context_budget_command(agent: Optional[str]):
       """Check agent context budget (CFR-007).

       Examples:
           project-manager context-budget              # All agents
           project-manager context-budget architect    # Specific agent
       """
       from coffee_maker.validation.context_budget import ContextBudgetEnforcer

       enforcer = ContextBudgetEnforcer()

       if agent:
           # Check specific agent
           try:
               usage = enforcer.measure_agent_context(agent)
               console.print(f"\n[bold]Agent:[/bold] {usage.agent_name}")
               console.print(f"  Prompt:      {usage.prompt_tokens:>8,} tokens")
               console.print(f"  Owned Docs:  {usage.owned_docs_tokens:>8,} tokens")
               console.print(f"  Tools:       {usage.tools_tokens:>8,} tokens")
               console.print(f"  ─────────────────────────")
               console.print(f"  TOTAL:       {usage.total_tokens:>8,} tokens ({usage.budget_percent:.1f}%)")
               console.print(f"\nBudget Limit:  {enforcer.MAX_BUDGET_TOKENS:>8,} tokens (30%)")
               console.print(f"Status:        {usage.status}\n")

               if usage.status != "OK":
                   console.print("[yellow]⚠️ Remediation recommended[/yellow]")
           except Exception as e:
               console.print(f"[red]Error:[/red] {e}", style="bold red")
       else:
           # Show monthly report
           report = enforcer.generate_monthly_report()
           console.print(Markdown(report))
   ```

**Testing**:
- Run `project-manager context-budget` → see all agents
- Run `project-manager context-budget architect` → see architect details
- Verify fast (<1 second)

**Acceptance Criteria**:
- ✅ CLI commands work
- ✅ Reports are clear and actionable
- ✅ Fast feedback

---

### Phase 3: Startup Validation (Day 3 - 4 hours)

**Goal**: Enforce budget at agent startup (block if violation).

**Files to Create**:

1. **`coffee_maker/validation/__init__.py`** (~20 lines)
   - Export ContextBudgetEnforcer, validate_agent_context_budget

2. **`coffee_maker/autonomous/agent_startup.py`** (~100 lines)
   - Pre-startup validation for all agents
   - Check context budget before allowing agent to start
   - Log all validations

   ```python
   """Agent startup validation.

   Validates agent compliance with CFRs before startup.
   """

   from coffee_maker.validation.context_budget import ContextBudgetEnforcer
   from coffee_maker.utils.logging import get_logger

   logger = get_logger(__name__)

   def validate_agent_startup(agent_name: str) -> bool:
       """Validate agent can start (all CFRs compliant).

       Args:
           agent_name: Agent to validate

       Returns:
           True if all validations pass

       Raises:
           ContextBudgetViolationError: If CFR-007 violated
           AgentAlreadyRunningError: If singleton violated (US-035)
       """
       logger.info(f"Validating startup for agent: {agent_name}")

       # CFR-007: Context budget check
       enforcer = ContextBudgetEnforcer()
       enforcer.check_budget(agent_name)
       logger.info(f"  ✅ Context budget OK for {agent_name}")

       # US-035: Singleton check (future)
       # ... check singleton enforcement

       # All validations passed
       logger.info(f"✅ Agent {agent_name} validated, startup allowed")
       return True
   ```

**Integration**:
- Modify daemon startup to call `validate_agent_startup("code_developer")`
- Modify CLI to call validation before agent operations
- Log all validations to Langfuse

**Testing**:
- Start daemon → verify context budget checked
- Simulate budget violation → verify blocked
- Check logs → verify validations recorded

**Acceptance Criteria**:
- ✅ Agent startup validates context budget
- ✅ Violations block startup with clear error
- ✅ All validations logged

---

## Component Design

### ContextBudgetEnforcer

**Responsibility**: Measure and enforce CFR-007 context budget limits.

**Interface**:
```python
class ContextBudgetEnforcer:
    """Enforce CFR-007: Agent context budget ≤30%."""

    def measure_agent_context(self, agent_name: str) -> AgentContextUsage:
        """Measure agent's core context consumption."""
        pass

    def check_budget(self, agent_name: str) -> bool:
        """Validate agent complies with 30% budget.

        Raises:
            ContextBudgetViolationError: If budget exceeded
        """
        pass

    def generate_monthly_report(self) -> str:
        """Generate monthly context budget report."""
        pass
```

---

## Testing Strategy

### Unit Tests (~2 hours)

**`tests/unit/validation/test_context_budget.py`**:
```python
def test_count_tokens():
    """Test token counting."""
    enforcer = ContextBudgetEnforcer()
    text = "Hello world"
    tokens = enforcer.count_tokens(text)
    assert tokens > 0

def test_measure_agent_context():
    """Test measuring agent context."""
    enforcer = ContextBudgetEnforcer()
    usage = enforcer.measure_agent_context("architect")
    assert usage.total_tokens > 0
    assert usage.budget_percent < 100

def test_check_budget_violation():
    """Test budget violation detection."""
    # Mock an agent with oversized context
    enforcer = ContextBudgetEnforcer()
    # ... simulate violation
    with pytest.raises(ContextBudgetViolationError):
        enforcer.check_budget("oversized_agent")

def test_monthly_report():
    """Test report generation."""
    enforcer = ContextBudgetEnforcer()
    report = enforcer.generate_monthly_report()
    assert "Agent Context Budget Report" in report
    assert "architect" in report
```

### Integration Tests (~1 hour)

**Manual Testing**:
1. Run `project-manager context-budget` → verify all agents shown
2. Run `project-manager context-budget architect` → verify details
3. Start daemon → verify validation runs
4. Check logs → verify no errors

---

## Rollout Plan

### Day 1 (6 hours)
- Create ContextBudgetEnforcer class
- Implement token counting with tiktoken
- Implement budget validation
- Test with all agents

### Day 2 (4 hours)
- Add CLI commands
- Test CLI integration
- Generate first monthly report

### Day 3 (4 hours)
- Integrate with agent startup validation
- Add logging
- Write unit tests
- Documentation

**Total: 2-3 days (14 hours)**

---

## Success Criteria

### Must Have (P0)
- ✅ Token counting accurate
- ✅ Budget validation works (raises error if >30%)
- ✅ Monthly report generated
- ✅ CLI commands functional
- ✅ Startup validation integrated

### Should Have (P1)
- ✅ All agents measured
- ✅ Remediation guidance in error messages
- ✅ Unit tests for enforcer

### Could Have (P2) - DEFERRED
- ⚪ Automatic document compression
- ⚪ Real-time context tracking during execution
- ⚪ AI-powered optimization recommendations

---

## Why This is SIMPLE

### What We REUSE
✅ **tiktoken**: Existing library for token counting
✅ **Existing CLI**: Just add commands
✅ **Existing logging**: Use standard logger
✅ **Existing file system**: Read existing files

**New code**: ~350 lines total (ContextBudgetEnforcer + CLI + startup validation)

---

## Risks & Mitigations

### Risk 1: Token counting inaccurate

**Impact**: Medium
**Mitigation**:
- Use official tiktoken library (same as OpenAI uses)
- Test against known examples
- Add safety margin (enforce 30% but warn at 25%)

### Risk 2: Large ROADMAP causes violations

**Impact**: High
**Mitigation**:
- Provide clear remediation steps in error
- Document sharpening strategies (CFR-007)
- Consider splitting ROADMAP if needed

### Risk 3: Agent startup blocked unexpectedly

**Impact**: High
**Mitigation**:
- Clear error messages with remediation steps
- Provide override flag for emergencies (--skip-context-check)
- Log all violations for analysis

---

## Future Enhancements (NOT NOW)

Phase 2+ (if needed):
1. Automatic document compression
2. Real-time context tracking
3. Dynamic context window sizing
4. AI-powered optimization

**But**: Start simple with measurement + enforcement!

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending
- [ ] User (final approval) - Approval pending

---

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements (2-3 days)
