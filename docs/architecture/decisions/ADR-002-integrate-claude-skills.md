# ADR-002: Integrate Claude Skills as Complement to Prompts

**Status**: Proposed

**Date**: 2025-10-17

**Author**: architect agent

**Related Issues**: Multi-AI Provider Support (PRIORITY 8)

**Related Specs**: SPEC-001-claude-skills-integration.md

---

## Context

The MonolithicCoffeeMakerAgent system currently uses a **prompt-based architecture** for agent interactions:
- Centralized prompts in `.claude/commands/`
- PromptLoader utility for multi-AI provider support
- Prompts contain text instructions that LLMs execute
- All agent logic relies on LLM reasoning

**Current Limitations**:
1. **No executable code**: Prompts are text-only, LLM must generate code each time
2. **Reliability issues**: LLM-generated code may contain errors or inconsistencies
3. **Limited composition**: Prompts don't stack or compose automatically
4. **Manual selection**: Agents must explicitly choose which prompt to use
5. **No task-relevance detection**: System can't auto-select prompts based on task

**Example Problem**: architect agent evaluating package security
- **Current**: Prompt instructs LLM to "check for CVEs, analyze licenses"
  - LLM generates Python code to query CVE databases
  - Code may have bugs, miss edge cases, or use wrong APIs
  - Different results each time (non-deterministic)
- **Desired**: Pre-tested Python script reliably checks CVEs
  - Same code every time (deterministic)
  - Thoroughly tested, handles edge cases
  - Faster execution (no code generation step)

**Forces at Play**:
- **Technical**: Need reliable execution for critical operations (security scans, dependency checks)
- **Maintainability**: Pre-tested code easier to maintain than prompt-generated code
- **Composability**: Multiple skills should auto-compose for complex tasks
- **Backward Compatibility**: Can't break existing prompt-based system
- **Multi-AI Provider**: Solution must work with Claude, Gemini, OpenAI

**Constraints**:
- Must maintain 100% backward compatibility with PromptLoader
- Cannot require agents to rewrite existing logic
- Must integrate with Langfuse observability (Phase 2)
- Team already familiar with prompt-based system

---

## Decision

We will integrate **Claude Skills** as a **complement** to the existing prompt system, not a replacement.

**Key Decisions**:

### 1. Skills Complement Prompts (Not Replace)

Skills and prompts serve different purposes:

| Capability | Use | Technology |
|------------|-----|------------|
| **Reliable execution** | Security scans, calculations, API calls | **Skills** (executable code) |
| **Creative reasoning** | ADR writing, design discussions, analysis | **Prompts** (LLM reasoning) |
| **Data + Interpretation** | Scan data with skill → Interpret with prompt | **Hybrid** (both) |

**Example**: architect evaluating Redis dependency
- **Skill** (`dependency-analysis`): Queries PyPI, checks CVEs, validates license → JSON output
- **Prompt** (`evaluate-dependency`): Interprets JSON, writes recommendation → Natural language
- **Result**: Reliable data + thoughtful analysis

### 2. Directory Structure: `.claude/skills/`

Skills stored in `.claude/skills/` alongside existing `.claude/commands/`:

```
.claude/
├── skills/           # NEW: Claude Skills
│   ├── shared/       # Skills available to ALL agents
│   ├── architect/    # architect-specific skills
│   ├── code_developer/
│   └── ...
├── commands/         # EXISTING: Prompts (unchanged)
└── mcp/              # EXISTING: MCP configs
```

**Rationale**: Separate directories maintain clear separation of concerns. Skills are executable code, prompts are text templates.

### 3. Unified Execution Controller

New `ExecutionController` class decides when to use skills vs. prompts:

```python
controller = ExecutionController(agent_type=AgentType.ARCHITECT)

# Use skill for reliable execution
result = controller.execute(
    task="check redis security",
    mode=ExecutionMode.SKILL_ONLY
)

# Use prompt for creative reasoning
result = controller.execute(
    task="write ADR justification",
    mode=ExecutionMode.PROMPT_ONLY
)

# Use both (hybrid)
result = controller.execute(
    task="evaluate redis dependency",
    mode=ExecutionMode.HYBRID  # Skill + Prompt
)
```

**Rationale**: Unified interface simplifies agent code. Agents don't need to know implementation details.

### 4. Agent-Specific Skills

Each agent gets:
- **Shared skills**: Available to ALL agents (e.g., git-operations, testing-automation)
- **Agent-specific skills**: Tailored to agent's role (e.g., architect/dependency-analysis)

**Skill Discovery**: Automatic via `SkillRegistry`
- Agent describes task: "analyze redis security"
- Registry finds matching skills via trigger phrases
- Skills auto-compose if multiple match

**Rationale**: Automatic discovery reduces boilerplate. Agents focus on "what" not "how".

### 5. Gradual Migration (Not Big Bang)

**Phase 1 (Pilot)**: 3 skills to validate approach
- `architect/dependency-analysis`
- `assistant (using code analysis skills)/security-audit`
- `assistant/demo-creator`

**Phase 2 (Expansion)**: Add skills where beneficial (2-3 per agent)

**Phase 3 (Coexistence)**: Skills and prompts work together indefinitely

**No Prompt Deprecation**: Existing prompts remain in `.claude/commands/` forever.

**Rationale**: Gradual rollout reduces risk. No forced migration preserves backward compatibility.

### 6. Langfuse Integration (Phase 2)

Skills and prompts both tracked in Langfuse:
- Skill execution time, success rate, error patterns
- Prompt usage, token costs, latency
- Hybrid execution analysis

**Rationale**: Unified observability across both systems enables data-driven optimization.

---

## Consequences

### Positive Consequences

- **Reliability**: Critical operations (security scans, dependency checks) use pre-tested code
  - architect dependency analysis: 100% reliable CVE lookup
  - assistant (using code analysis skills) security audits: Consistent vulnerability detection
  - assistant demos: Reproducible Puppeteer scripts

- **Composability**: Multiple skills auto-compose for complex tasks
  - Task: "Full security audit" → skills compose: security-scan + dependency-check + license-validation
  - No manual orchestration needed

- **Maintainability**: Skill code easier to test and maintain than prompt-generated code
  - Skills have unit tests (pytest)
  - Prompts rely on LLM behavior (harder to test)

- **Performance**: Skills execute faster than prompting LLM to generate code
  - Skill execution: ~2-5 seconds (direct execution)
  - Prompt-based: ~10-30 seconds (LLM generates code → executes)

- **Portability**: Skills work across Claude platforms (Desktop, Code, API)
  - Same skill code on all platforms
  - Prompts may behave differently across providers

- **Backward Compatible**: Existing prompt system unchanged
  - Agents can ignore skills (opt-in via config)
  - No breaking changes to PromptLoader API

### Negative Consequences

- **Increased Complexity**: Two systems to maintain (skills + prompts)
  - Developers must understand when to use each
  - Mitigated by: Clear decision framework, documentation

- **Initial Development Cost**: Building skill infrastructure takes time
  - SkillLoader, SkillRegistry, SkillInvoker classes
  - 2-3 weeks initial development
  - Mitigated by: Gradual rollout, pilot skills first

- **Skill Proliferation Risk**: Too many skills → maintenance burden
  - Each agent could accumulate 20+ skills
  - Mitigated by: Strict creation criteria, monthly audits

- **Sandboxing Overhead**: Secure skill execution adds complexity
  - Need to prevent malicious code execution
  - Mitigated by: Start without sandbox, add if needed

- **Learning Curve**: Team must learn skill creation process
  - New workflow (SKILL.md metadata, Python scripts, etc.)
  - Mitigated by: Documentation, examples, templates

### Neutral Consequences

- **Directory Structure Change**: New `.claude/skills/` directory
  - Not inherently good or bad
  - Team will adapt

- **Two Execution Paths**: Skills vs. Prompts
  - Adds decision overhead
  - Mitigated by: ExecutionController abstracts decision

---

## Alternatives Considered

### Alternative 1: Replace Prompts Entirely with Skills

**Description**: Deprecate prompt system, migrate everything to skills.

**Pros**:
- Simpler architecture (one system instead of two)
- All execution is reliable (pre-tested code)
- Easier to reason about

**Cons**:
- Breaks backward compatibility (major disruption)
- Skills can't handle creative tasks (ADR writing, design discussions)
- Huge migration effort (rewrite all prompts as skills)
- Loses flexibility (prompts adapt to new tasks, skills are fixed)

**Why Rejected**: Skills and prompts solve different problems. Creative reasoning requires LLM flexibility. Forcing everything into skills loses that capability. Backward compatibility is critical.

### Alternative 2: Keep Prompts Only (No Skills)

**Description**: Don't add skills, improve prompts instead (better templates, more examples).

**Pros**:
- No new infrastructure (simpler)
- Team already familiar with prompts
- No migration needed

**Cons**:
- Doesn't solve reliability problem (LLM-generated code still error-prone)
- Can't achieve deterministic execution (LLMs are non-deterministic)
- No composability (prompts don't stack)
- Performance remains slow (LLM code generation overhead)

**Why Rejected**: Prompts alone can't provide the reliability needed for critical operations like security scans. Claude Skills specifically address this gap.

### Alternative 3: Custom Script System (Reinvent Skills)

**Description**: Build our own skill-like system (Python scripts in `scripts/` directory).

**Pros**:
- Full control over design
- Tailored to our exact needs
- No Claude-specific dependencies

**Cons**:
- Reinventing the wheel (Claude Skills already exist)
- No cross-platform portability (won't work on Claude Desktop/API)
- More development effort (2-3 months vs. 2-3 weeks)
- No automatic task-relevance detection (we'd have to build it)

**Why Rejected**: Claude Skills provide exactly what we need. Building from scratch wastes time and loses portability benefits.

### Alternative 4: MCP Tools Only (No Skills)

**Description**: Use Model Context Protocol (MCP) tools instead of skills.

**Pros**:
- Already integrated (Puppeteer MCP working)
- Standardized protocol
- Cross-provider support

**Cons**:
- MCP tools are external servers (more complex deployment)
- Less portable than skills (need server setup)
- Harder to version control (code not in repo)
- No automatic task-relevance detection

**Why Rejected**: MCP tools are great for external integrations (browsers, databases) but overkill for simple Python scripts. Skills are lighter weight for agent-internal operations.

---

## Implementation Notes

### Implementation Phases

**Phase 1: Infrastructure (2 weeks)**
1. Implement SkillLoader, SkillRegistry, SkillInvoker
2. Implement ExecutionController
3. Add AgentSkillController to each agent
4. Unit tests (>80% coverage)

**Phase 2: Pilot Skills (2 weeks)**
1. Create `architect/dependency-analysis`
2. Create `assistant (using code analysis skills)/security-audit`
3. Create `assistant/demo-creator`
4. Integration tests, production validation

**Phase 3: Documentation (1 week)**
1. User guide, developer guide, migration guide
2. Per-agent skill catalogs
3. ADR-002 (this document)

**Phase 4: Gradual Expansion (1-2 months)**
1. Add 2-3 skills per agent (15-20 total)
2. Monitor usage via Langfuse
3. Refine based on feedback

### Code Examples

**Agent Integration** (architect):
```python
class ArchitectAgent:
    def __init__(self):
        self.skill_controller = AgentSkillController(AgentType.ARCHITECT)

    def evaluate_dependency(self, package: str, version: str):
        # Hybrid: Skill for data, prompt for reasoning
        result = self.skill_controller.execute_task(
            "analyze dependency security",
            context={"package_name": package, "version": version}
        )
        # result.output contains reliable security data
        # Now use prompt to interpret and recommend
```

**Skill Structure** (dependency-analysis):
```
.claude/skills/architect/dependency-analysis/
├── SKILL.md              # Metadata (triggers, version)
├── check_security.py     # CVE lookup script
├── check_license.py      # License validation
├── cve_database.json     # CVE data (bundled)
└── examples/
    └── redis_analysis.json
```

### Dependencies

**New Python Dependencies**:
- `pyyaml` (for parsing SKILL.md frontmatter)
- No other dependencies (skills use stdlib where possible)

**User Approval Required**: architect must request approval for `pyyaml` before implementation.

---

## Validation

### Success Metrics

**Pilot Phase (Month 1)**:
- ✅ 3 pilot skills implemented and tested
- ✅ Skills execute successfully (>95% success rate)
- ✅ Agents adopt skills (>10 uses per skill)
- ✅ No production incidents

**Expansion Phase (Month 2-3)**:
- ✅ 15-20 skills across all agents
- ✅ Skill usage grows 20% month-over-month
- ✅ Developer satisfaction (survey: >8/10)

**Maturity Phase (Month 6+)**:
- ✅ Skills integral to workflows
- ✅ Langfuse dashboards show performance
- ✅ Skill library stable (low churn)

### Reevaluation Triggers

Reassess this decision if:
1. **Skill failure rate >10%**: Skills become unreliable
2. **Maintenance burden >4 hours/week**: Too much overhead
3. **Team resistance**: Developers reject skill system
4. **Performance regression**: Skills slower than prompts

If triggered, consider:
- Simplifying skill system
- Reducing skill count
- Reverting to prompt-only (if critical)

---

## References

- [Claude Skills Announcement](https://www.anthropic.com/news/skills)
- [SPEC-001: Claude Skills Integration](../specs/SPEC-001-claude-skills-integration.md)
- [ADR-001: Use Mixins Pattern](./ADR-001-use-mixins-pattern.md)
- [PromptLoader Implementation](../../coffee_maker/autonomous/prompt_loader.py)
- [PRIORITY 8: Multi-AI Provider Support](../../docs/roadmap/ROADMAP.md)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created | architect |
| 2025-10-17 | Status: Proposed | architect |

---

## Notes

**Risks and Mitigations**:

1. **Risk**: Skills proliferate uncontrollably
   - **Mitigation**: Strict creation criteria, monthly audits
   - **Status**: Creation criteria defined in SPEC-001

2. **Risk**: Prompt-skill confusion
   - **Mitigation**: Clear decision framework, documentation
   - **Status**: Decision tree in SPEC-001 Appendix B

3. **Risk**: Sandbox complexity
   - **Mitigation**: Start without sandbox, add if needed
   - **Status**: Deferred to security review

4. **Risk**: Team unfamiliar with skills
   - **Mitigation**: Documentation, examples, training
   - **Status**: Docs planned in Phase 3

**Open Questions**:
1. Sandbox technology choice (firejail, docker, pypy)?
   - **Answer**: Deferred until security concerns arise
2. Skill sharing across projects?
   - **Answer**: Keep project-specific for now
3. Skill marketplace?
   - **Answer**: Not in scope (revisit in 6 months)

**Future Work**:
- Langfuse integration for skill tracking (Phase 2)
- Skill versioning and compatibility matrix
- Public skill library (if skills prove valuable)
- Cross-project skill sharing

---

**Conclusion**: Integrating Claude Skills as a complement to prompts provides the best of both worlds: reliable execution for critical operations (skills) and creative flexibility for reasoning (prompts). This decision preserves backward compatibility while enabling new capabilities, making it a low-risk, high-reward architectural enhancement.

**Recommendation**: Accept this ADR and proceed with implementation (SPEC-001).
