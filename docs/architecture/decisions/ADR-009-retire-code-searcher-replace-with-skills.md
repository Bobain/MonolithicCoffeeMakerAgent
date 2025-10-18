# ADR-009: Retire code-searcher Agent, Replace with Skills System

**Status**: Accepted

**Date**: 2025-10-18

**Author**: architect agent

**Related Issues**: Advanced Code Search Capabilities (PRIORITY TBD)

**Related Specs**: SPEC-001-advanced-code-search-skills.md

---

## Context

The MonolithicCoffeeMakerAgent system currently has **6 autonomous agents**, including **code-searcher** dedicated to deep codebase analysis and forensic examination.

**Current Architecture**:
```
user_listener (UI)
    ├── architect (design)
    ├── code_developer (implementation)
    ├── project_manager (planning)
    ├── assistant (docs + dispatcher + demos)
    ├── code-searcher (code analysis)      ← TO BE RETIRED
    └── ux-design-expert (UI/UX)
```

**code-searcher Current Responsibilities**:
- Deep codebase analysis and pattern detection
- Security audits and vulnerability scanning
- Dependency tracing and impact analysis
- Refactoring opportunity identification
- Architectural analysis of code structure

**Current Workflow**:
```
User: "Find all authentication code"
    ↓
user_listener → code-searcher
    ↓
code-searcher:
  1. Uses Grep/Read tools to search
  2. Analyzes results with LLM reasoning
  3. Prepares findings document
  4. Presents to assistant
    ↓
assistant → project_manager
    ↓
project_manager writes docs/[analysis]_[date].md
```

**Problems with Current Approach**:

1. **Agent Overhead**: code-searcher is a full agent with:
   - Singleton enforcement (only one instance can run)
   - Status tracking (agent_status.json)
   - Langfuse observability overhead
   - Complex delegation workflow (4 agents involved for simple search)

2. **Limited Availability**: Only code-searcher can perform deep analysis
   - architect CANNOT directly search code (must delegate)
   - assistant CANNOT perform complex searches (must delegate)
   - code_developer CANNOT use security audits during implementation (must delegate)
   - Result: Bottleneck and communication overhead

3. **No Code Index**: Searches are ad-hoc and incomplete
   - grep/grep searches find keywords, not functional concepts
   - No structured codebase map (categories → components → implementations)
   - Repetitive analysis (same searches run multiple times)
   - Inefficient for large codebases (55,807 LOC)

4. **Delegation Complexity**: 4-agent workflow for simple tasks
   - code-searcher → assistant → project_manager → final docs
   - High coordination overhead
   - Slow turnaround time
   - Potential for communication errors

5. **Reliability Issues**: LLM-based search is non-deterministic
   - Different results each time for same query
   - May miss code zones (no comprehensive index)
   - Hard to validate completeness

**Forces at Play**:
- **Simplicity**: Fewer agents → simpler system
- **Composability**: Skills can be used by multiple agents
- **Performance**: Code Index + Skills = faster, more reliable
- **Agent Count**: Context budget pressure (CFR-007) → fewer agents better
- **Autonomy**: architect should be able to search code directly

**Constraints**:
- Must maintain ALL existing functionality (no capability loss)
- Cannot break existing workflows
- Must provide BETTER search capabilities than current system
- Solution must work with multi-AI provider support

**User Decision (2025-10-18)**:
> "L'agent code-searcher va disparaître, ses attributions seront remplacées par des skills et le mécanisme de mise à jour que je viens de décrire"

This ADR documents that architectural decision.

---

## Decision

We will **RETIRE the code-searcher agent entirely** and **REPLACE with a Skills-based system** consisting of:

1. **Code Index Infrastructure** (automated, no agent needed)
2. **Skills available to ALL agents** (not just one dedicated agent)

**New Architecture**:
```
user_listener (UI)
    ├── architect (design) ──────────┐
    ├── code_developer (implementation)  │
    ├── project_manager (planning)       │  All use skills
    ├── assistant (docs + dispatcher + demos)
    └── ux-design-expert (UI/UX)     │
                                     │
                                     ↓
                           ┌─────────────────────┐
                           │   SKILLS SYSTEM     │
                           │                     │
                           │ - Code Index        │
                           │ - Functional Search │
                           │ - Code Explanation  │
                           │ - Security Audit    │
                           │ - Dependency Tracer │
                           └─────────────────────┘
                                     ↑
                           ┌─────────────────────┐
                           │  Skills Maintainer  │
                           │  architect agent    │ ⭐ NEW (ADR-010)
                           │                     │
                           │ Triggered by:       │
                           │ - Commit reviews    │
                           │ - Git hooks         │
                           └─────────────────────┘
```

**Key Decisions**:

### 1. Retire code-searcher Agent Completely

**What**:
- Remove code-searcher from agent roster (6 agents → 5 agents)
- Delete code-searcher agent configuration
- Remove code-searcher from singleton enforcement
- Remove code-searcher status tracking

**Why**:
- Skills provide same capabilities without agent overhead
- Eliminates bottleneck (skills usable by all agents)
- Reduces complexity (fewer agents to coordinate)
- Improves context budget (CFR-007 compliance)

**When**: After Skills system fully implemented and validated

### 2. Replace with Skills System

**New Responsibilities Distribution**:

| Former code-searcher Capability | New Owner | New Approach |
|--------------------------------|-----------|--------------|
| **Code Forensics** | Skill: `code-forensics` | Used by: architect, assistant, code_developer |
| **Security Audit** | Skill: `security-audit` | Used by: architect, code_developer |
| **Dependency Tracer** | Skill: `dependency-tracer` | Used by: architect |
| **Functional Search** | Skill: `functional-search` | Used by: architect, assistant |
| **Code Explanation** | Skill: `code-explainer` | Used by: architect, assistant |
| **Code Index Maintenance** | architect (via commit review) | Git hooks trigger architect + Manual updates (ADR-010) |

**Skills are Claude Code Skills** (executable Python scripts):
- Stored in `.claude/skills/` directory
- Executed deterministically (same code every time)
- Available to ALL agents (not just one)
- Auto-compose for complex tasks
- Thoroughly tested (unit tests in pytest)

### 3. Code Index Infrastructure (architect-Maintained) ⭐ UPDATED (ADR-010)

**What**: 3-level hierarchical codebase index

**Maintained by**: architect agent (via commit review workflow)

**Why architect (not automated)**:
- architect sees commits in architectural context
- Can validate implementation vs specs during review
- Extracts patterns and learnings (not just code structure)
- Provides quality feedback while updating index
- **Best opportunity**: "La revue de code est la meilleure occasion de mettre à jour les index"

```json
{
  "categories": [
    {
      "name": "Authentication & Authorization",
      "components": [
        {
          "name": "Login Flow",
          "implementations": [
            {
              "file": "coffee_maker/auth/login.py",
              "line_start": 45,
              "line_end": 89,
              "complexity": "medium",
              "dependencies": ["jwt_utils", "user_repository"]
            }
          ]
        }
      ]
    }
  ]
}
```

**Why**: Structured index enables fast, comprehensive searches

**Update Mechanism** ⭐ UPDATED (ADR-010 - architect-driven):
1. **Commit Review** (PRIMARY): architect reviews ALL commits → updates skills simultaneously
   - architect sees git diff + architectural context
   - Updates Code Index while providing feedback
   - **Best timing**: Skills updated when code reviewed (one workflow)
2. **Git Hooks** (TRIGGER): Post-commit hook invokes architect review (async, non-blocking)
3. **Manual Trigger**: architect can rebuild index anytime via skill invocation

**Performance**:
- Incremental update: 2-5 seconds (for 1-10 file changes)
- Full rebuild: 30-60 seconds (for entire codebase)
- Query execution: <200ms (fast searches)

### 4. Migration Path

**Phase 1: Build Skills System (BEFORE retiring agent)**
1. Implement Code Index infrastructure
2. Implement 5 core skills (forensics, security, dependency, search, explain)
3. Test thoroughly with architect, assistant, code_developer
4. Validate capabilities match or exceed code-searcher

**Phase 2: Gradual Transition**
1. architect starts using skills instead of delegating to code-searcher
2. assistant uses skills for simple searches
3. code_developer uses security-audit during implementation
4. Monitor usage, ensure skills work reliably

**Phase 3: Retire code-searcher**
1. Remove code-searcher from .claude/agents/
2. Update .claude/CLAUDE.md (remove code-searcher references)
3. Update docs/roadmap/ROADMAP.md
4. Remove code-searcher from AgentRegistry
5. Clean up code-searcher status files

**Phase 4: Cleanup**
1. Remove any remaining code-searcher references
2. Update all documentation
3. Archive code-searcher agent definition for historical reference

**Timeline**: 2-3 weeks (non-disruptive, gradual)

### 5. Agent Tool Ownership Matrix Updates

**BEFORE** (with code-searcher):
```
| Tool/Capability | Owner | Usage |
|----------------|-------|-------|
| Code search (simple) | assistant | 1-2 files |
| Code search (complex) | code-searcher | Deep analysis |
| Code analysis docs | project_manager | Creates docs |
```

**AFTER** (with skills):
```
| Tool/Capability | Owner | Usage |
|----------------|-------|-------|
| Code search (ALL) | Skill: functional-search | architect, assistant, code_developer |
| Security audit | Skill: security-audit | architect, code_developer |
| Dependency analysis | Skill: dependency-tracer | architect |
| Code forensics | Skill: code-forensics | architect, assistant |
| Code explanation | Skill: code-explainer | architect, assistant |
| Code Index maintenance | Infrastructure (auto-update) | Git hooks, cron (no agent) |
| Code analysis docs | project_manager | Creates docs (data from skills) |
```

**Key Insight**: Skills are NOT owned by any agent. They're infrastructure available to ALL agents.

---

## Consequences

### Positive Consequences

- **Fewer Agents = Simpler System**
  - 6 agents → 5 agents (17% reduction)
  - Less coordination overhead (no 4-agent delegation chain)
  - Lower context budget pressure (CFR-007 compliance)
  - Fewer singleton conflicts to manage

- **Skills Usable by ALL Agents**
  - architect can search code directly (no delegation)
  - assistant can perform deep searches (not just simple grep)
  - code_developer can run security audits during implementation
  - No bottleneck (parallel usage by multiple agents)

- **Better Performance**
  - Code Index enables fast searches (<200ms vs 10-30s)
  - Incremental updates keep index fresh (2-5s)
  - Deterministic results (skills execute same code every time)
  - No LLM overhead for search operations

- **More Reliable**
  - Skills are pre-tested Python code (not generated each time)
  - Comprehensive coverage (3-level index captures all code)
  - Reproducible results (same query = same results)
  - Automated updates (no manual maintenance)

- **Reduced Complexity**
  - No delegation workflow (architect uses skill directly)
  - No agent status tracking for code-searcher
  - No singleton enforcement for code-searcher
  - Simpler mental model (skills as tools, not agents)

- **Always Up-to-Date**
  - Git hooks update index after every commit
  - Nightly rebuild ensures freshness
  - No stale analysis (index max 24 hours old)

- **Better Integration**
  - architect can use skills while creating specs
  - code_developer can use skills during implementation
  - assistant can use skills for user queries
  - No context switching between agents

### Negative Consequences

- **Loss of "Agent Expertise" Mental Model**
  - code-searcher was conceptually a "specialist" in code analysis
  - Skills are "just tools" (less anthropomorphic)
  - Mitigated by: Skills provide BETTER capabilities than agent did

- **Initial Implementation Effort**
  - Building Code Index infrastructure: ~15 hours
  - Building 5 core skills: ~11 hours
  - Testing and validation: ~5 hours
  - Total: ~31 hours
  - Mitigated by: Gradual rollout, incremental value

- **Documentation Updates Needed**
  - Update .claude/CLAUDE.md (remove code-searcher)
  - Update all agent documentation
  - Update ROADMAP.md
  - Update decision framework diagrams
  - Mitigated by: Part of migration plan (Phase 3)

- **Existing docs/code-searcher/ Directory**
  - Old code analysis docs reference code-searcher agent
  - Need to clarify that analysis now done via skills
  - Mitigated by: Add README explaining transition

- **Potential Confusion During Transition**
  - Users may ask for code-searcher (force of habit)
  - user_listener must redirect to skills system
  - Mitigated by: Clear communication, gradual transition

### Neutral Consequences

- **File Count Changes**
  - Remove: .claude/agents/code-searcher.md
  - Remove: data/agent_status/code_searcher_status.json
  - Add: .claude/skills/code-forensics/, security-audit/, etc.
  - Add: data/code_index/index.json

- **Agent Count Change**
  - 6 agents → 5 agents
  - Not inherently better or worse, just simpler

- **Workflow Changes**
  - BEFORE: architect → code-searcher → assistant → project_manager
  - AFTER: architect → skill → (optional) project_manager for docs
  - Shorter workflow, but different pattern

---

## Alternatives Considered

### Alternative 1: Keep code-searcher Agent, Add Skills Too

**Description**: Maintain code-searcher agent AND add skills system.

**Pros**:
- No disruption (backward compatible)
- Users can choose agent or skills
- Gradual transition (no forced migration)

**Cons**:
- Redundancy (same capabilities in two places)
- More complexity (agent + skills to maintain)
- Doesn't solve bottleneck problem (agent still singleton)
- Doesn't reduce agent count (CFR-007 pressure remains)
- Confusion (which approach to use?)

**Why Rejected**: Skills provide ALL functionality code-searcher did, but better. Keeping both adds complexity without benefit. User explicitly decided to retire code-searcher.

### Alternative 2: Enhance code-searcher Agent (No Skills)

**Description**: Improve code-searcher with better search algorithms, but keep it as an agent.

**Pros**:
- No new infrastructure (simpler)
- Familiar pattern (agent-based)
- Less implementation effort

**Cons**:
- Doesn't solve bottleneck (still only one agent can search)
- Doesn't solve delegation overhead (still 4-agent workflow)
- Doesn't solve performance (LLM-based search still slow)
- Doesn't solve reliability (non-deterministic results)
- Doesn't reduce agent count (CFR-007 pressure)

**Why Rejected**: Doesn't address fundamental problems. Skills system is superior architecture for code search functionality.

### Alternative 3: Merge code-searcher into assistant Agent

**Description**: Give assistant agent the code-searcher capabilities (no separate agent).

**Pros**:
- Reduces agent count (6 → 5)
- assistant already does dispatching
- No new infrastructure

**Cons**:
- assistant becomes bloated (too many responsibilities)
- Doesn't solve bottleneck (still one agent)
- Doesn't enable parallel usage by multiple agents
- Doesn't provide Code Index benefits
- Mixing concerns (assistant is docs expert, not code analyst)

**Why Rejected**: Violates single responsibility principle. Skills system enables ALL agents to use code search, not just one.

### Alternative 4: Custom Code Index with Agent Wrapper

**Description**: Build Code Index, but keep code-searcher agent as "index maintainer".

**Pros**:
- Clear ownership (code-searcher maintains index)
- Agent can coordinate updates
- Familiar agent-based pattern

**Cons**:
- Agent not needed (git hooks + cron can maintain index)
- Adds complexity (agent overhead for simple task)
- Doesn't solve bottleneck (searches still delegated to agent)
- Doesn't enable multi-agent usage

**Why Rejected**: Index maintenance is infrastructure, not agent work. Git hooks + cron are simpler and more reliable than agent coordination.

---

## Implementation Notes

### Implementation Phases

**Phase 1: Build Skills Infrastructure (2-3 weeks)**

Week 1: Code Index Infrastructure
- Implement 3-level hierarchical index (data/code_index/index.json)
- Implement full rebuild algorithm
- Implement incremental update algorithm
- Git hook integration (post-commit, post-merge)
- Scheduled rebuild (cron job)
- Unit tests (>80% coverage)

Week 2: Core Skills
- Skill: `code-forensics` (deep pattern analysis)
- Skill: `security-audit` (vulnerability scanning)
- Skill: `dependency-tracer` (dependency analysis)
- Skill: `functional-search` (find code by function)
- Skill: `code-explainer` (explain code in accessible terms)
- Integration tests with architect, assistant, code_developer

Week 3: Validation & Documentation
- Test all skills with real-world queries
- Performance benchmarking
- Documentation (user guides, API reference)
- Compare capabilities vs code-searcher (ensure parity)

**Phase 2: Gradual Transition (1 week)**

- architect adopts skills (instead of delegating to code-searcher)
- assistant uses skills for complex searches
- code_developer uses security-audit during implementation
- Monitor usage, collect feedback
- Fix any issues discovered

**Phase 3: Retire code-searcher (1 day)**

- Remove .claude/agents/code-searcher.md
- Update .claude/CLAUDE.md (Agent Tool Ownership Matrix)
- Update docs/roadmap/ROADMAP.md
- Remove code-searcher from AgentRegistry
- Remove data/agent_status/code_searcher_status.json
- Git commit: "feat: Retire code-searcher agent, replace with skills system"

**Phase 4: Cleanup & Documentation (2 days)**

- Update all documentation references to code-searcher
- Add README to docs/code-searcher/ explaining transition
- Archive code-searcher agent definition
- Update decision framework diagrams
- Final validation (all tests pass)

### Code Changes Required

**Files to Remove**:
- `.claude/agents/code-searcher.md`
- `data/agent_status/code_searcher_status.json`

**Files to Update**:
- `.claude/CLAUDE.md` (remove code-searcher from Agent Tool Ownership Matrix)
- `docs/roadmap/ROADMAP.md` (update agent list)
- `coffee_maker/autonomous/agent_registry.py` (remove AgentType.CODE_SEARCHER)
- All agent documentation (remove code-searcher delegation workflows)

**Files to Add**:
- `.claude/skills/code-forensics/` (skill implementation)
- `.claude/skills/security-audit/` (skill implementation)
- `.claude/skills/dependency-tracer/` (skill implementation)
- `.claude/skills/functional-search/` (skill implementation)
- `.claude/skills/code-explainer/` (skill implementation)
- `data/code_index/index.json` (auto-generated)
- `.git/hooks/post-commit` (git hook for index update)
- `.git/hooks/post-merge` (git hook for index rebuild)

### Migration Checklist

**Pre-Migration (Skills System Ready)**:
- [ ] Code Index infrastructure implemented
- [ ] 5 core skills implemented
- [ ] Skills tested with architect, assistant, code_developer
- [ ] Performance validated (queries <200ms)
- [ ] Documentation complete

**Migration (Retire code-searcher)**:
- [ ] Remove .claude/agents/code-searcher.md
- [ ] Update .claude/CLAUDE.md
- [ ] Update docs/roadmap/ROADMAP.md
- [ ] Remove code-searcher from AgentRegistry
- [ ] Remove code_searcher_status.json
- [ ] All tests pass

**Post-Migration (Cleanup)**:
- [ ] Update all documentation
- [ ] Add README to docs/code-searcher/
- [ ] Archive code-searcher agent definition
- [ ] No code references to code-searcher remain
- [ ] User communication (skills system live)

### Dependencies

**No New Python Dependencies Required**:
- Code Index: Uses stdlib (ast, json, pathlib)
- Skills: Use existing tools (Grep, Read, Glob)
- Git hooks: Bash scripts (no dependencies)

**Rationale**: Keeping dependencies minimal reduces complexity and maintenance burden.

---

## Risks and Mitigations

### Risk 1: Skills Don't Match code-searcher Capabilities

**Risk**: Skills system provides LESS functionality than code-searcher agent.

**Impact**: Users lose capabilities, migration fails.

**Probability**: LOW (with proper validation)

**Mitigation**:
1. **Capability Matrix**: Document all code-searcher capabilities, ensure skills cover 100%
2. **Parallel Testing**: Run code-searcher and skills in parallel during Phase 2
3. **User Validation**: Get user approval BEFORE retiring code-searcher
4. **Rollback Plan**: If skills insufficient, keep code-searcher temporarily

**Fallback**: Re-enable code-searcher agent if skills prove inadequate.

### Risk 2: Code Index Becomes Stale

**Risk**: Git hooks fail or index update doesn't run, index becomes outdated.

**Impact**: architect works with stale data, creates incorrect specs.

**Probability**: LOW (with scheduled rebuild)

**Mitigation**:
1. **Scheduled Rebuild**: Nightly cron job ensures freshness (max 24 hours stale)
2. **Freshness Indicator**: Index includes "generated_at" timestamp
3. **Warning System**: architect sees warning if index >24 hours old
4. **Manual Trigger**: architect can rebuild index anytime

**Fallback**: Manual grep/search if index is stale.

### Risk 3: Performance Degradation

**Risk**: Index updates slow down git commits or queries become slow.

**Impact**: Developers frustrated by slow commits or searches.

**Probability**: LOW (with optimization)

**Mitigation**:
1. **Async Updates**: Git hooks run in background (non-blocking)
2. **Incremental Updates**: Only update changed files (2-5s)
3. **Performance Monitoring**: Track update times, optimize if >5s
4. **Caching**: Query results cached for repeated searches

**Fallback**: Disable git hooks, rely on scheduled rebuild.

### Risk 4: Confusion During Transition

**Risk**: Users still ask for code-searcher agent (force of habit).

**Impact**: user_listener must explain transition, potential frustration.

**Probability**: MEDIUM (during Phase 2-3)

**Mitigation**:
1. **Clear Communication**: Announce transition before Phase 2
2. **user_listener Training**: Update user_listener to explain skills system
3. **Gradual Transition**: Phase 2 allows users to adapt
4. **Documentation**: Clear guide on how to use skills instead

**Fallback**: user_listener redirects gracefully, no capabilities lost.

### Risk 5: Index Accuracy Issues

**Risk**: Clustering algorithm misclassifies code into wrong categories.

**Impact**: architect gets incomplete or incorrect search results.

**Probability**: MEDIUM (ML clustering is not perfect)

**Mitigation**:
1. **Manual Review**: Allow architect to override categorization
2. **Feedback Loop**: architect reports issues, index improves
3. **Hybrid Approach**: Combine ML clustering with rule-based heuristics
4. **Incremental Improvement**: Index accuracy improves over time

**Fallback**: architect can use manual grep as backup.

---

## Validation

### Success Metrics

**Phase 1 Success (Infrastructure Complete)**:
- [ ] Code Index generated for MonolithicCoffeeMakerAgent codebase
- [ ] 3-level hierarchy (categories, components, implementations)
- [ ] All Python files indexed with line numbers
- [ ] Complexity and dependencies captured
- [ ] Full rebuild completes in <60 seconds
- [ ] Incremental update completes in <5 seconds

**Phase 2 Success (Skills Working)**:
- [ ] architect can query by functional area
- [ ] assistant can perform deep searches
- [ ] code_developer can run security audits
- [ ] Search returns hierarchical results (<200ms)
- [ ] Code explanation generates technical summaries
- [ ] Skills match or exceed code-searcher capabilities

**Phase 3 Success (code-searcher Retired)**:
- [ ] code-searcher removed from .claude/agents/
- [ ] .claude/CLAUDE.md updated (no code-searcher references)
- [ ] docs/roadmap/ROADMAP.md updated
- [ ] AgentRegistry updated
- [ ] All tests pass
- [ ] No production incidents

**Overall Success**:
- [ ] 5 agents (down from 6) ✅
- [ ] architect creates 50% more detailed specs (data-driven)
- [ ] Code search <5 minutes (vs 30+ minutes before)
- [ ] Index stays current (freshness <5 minutes)
- [ ] No capabilities lost vs code-searcher agent
- [ ] User satisfaction (skills easier to use than delegation)

### Reevaluation Triggers

Reassess this decision if:
1. **Skills failure rate >10%**: Skills become unreliable
2. **Index staleness >24 hours regularly**: Update mechanism fails
3. **Performance regression**: Searches slower than code-searcher
4. **User dissatisfaction**: Team prefers code-searcher agent
5. **Capability gap**: Skills can't do what code-searcher could

If triggered, consider:
- Re-enabling code-searcher agent temporarily
- Improving skills system
- Hybrid approach (agent + skills)

---

## References

- [SPEC-001: Advanced Code Search Skills Architecture](../specs/SPEC-001-advanced-code-search-skills.md)
- [ADR-002: Integrate Claude Skills as Complement to Prompts](./ADR-002-integrate-claude-skills.md)
- [.claude/CLAUDE.md: Agent Tool Ownership Matrix](../../.claude/CLAUDE.md)
- [docs/roadmap/ROADMAP.md: Project Priorities](../../roadmap/ROADMAP.md)
- [CFR-007: Context Budget Management](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
- [User Decision: 2025-10-18 Conversation](context)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created | architect |
| 2025-10-18 | Status: Accepted | architect |

---

## Notes

**Decision Rationale**:

This decision is based on the user's explicit directive:
> "L'agent code-searcher va disparaître, ses attributions seront remplacées par des skills et le mécanisme de mise à jour que je viens de décrire"

**Why This is the Right Decision**:

1. **Skills > Agent for Code Search**
   - Deterministic execution (skills run same code every time)
   - Faster performance (no LLM overhead)
   - Reusable by ALL agents (not just one)
   - No delegation overhead (direct usage)

2. **Code Index = Game Changer**
   - 3-level hierarchy (concepts → components → code)
   - Comprehensive coverage (all code indexed)
   - Auto-updates (git hooks + cron)
   - Fast queries (<200ms)

3. **Simpler System**
   - 6 agents → 5 agents (17% reduction)
   - Less coordination overhead
   - Better context budget (CFR-007)
   - Fewer singleton conflicts

4. **Better User Experience**
   - architect can search directly (no delegation)
   - Faster results (<5 minutes vs 30+ minutes)
   - More reliable (deterministic, comprehensive)
   - Always up-to-date (auto-updates)

**Trade-offs Accepted**:

1. **Loss of "Agent Expertise" Mental Model**
   - code-searcher was conceptually a "specialist"
   - Skills are "just tools"
   - Accepted because: Skills provide BETTER functionality

2. **Implementation Effort**
   - ~31 hours to build skills system
   - Accepted because: Long-term benefits outweigh cost

3. **Documentation Updates**
   - Must update all docs referencing code-searcher
   - Accepted because: Part of normal evolution

**Open Questions**:

1. Should we archive code-searcher agent definition for historical reference?
   - **Answer**: YES - Keep in docs/architecture/archived/code-searcher-agent.md

2. What happens to existing docs/code-searcher/ analysis documents?
   - **Answer**: Add README explaining transition, keep docs as historical reference

3. Should we create a "migration guide" for users?
   - **Answer**: YES - Include in skills documentation

**Future Work**:

- Semantic search with code embeddings (Phase 2)
- Dependency graph visualization (Phase 3)
- AI-powered categorization (Phase 4)
- Multi-language support (Python + JavaScript + TypeScript)

---

**Conclusion**: Retiring code-searcher agent and replacing with a skills system is the right architectural decision. It simplifies the system (fewer agents), improves performance (Code Index + skills), enables broader usage (all agents can search), and reduces complexity (no delegation). This decision aligns with the user's directive and provides significant long-term benefits.

**Recommendation**: Accept this ADR and proceed with implementation according to the phased plan outlined above.

**Next Steps**:
1. Update SPEC-001-advanced-code-search-skills.md to reflect code-searcher retirement
2. Create migration plan document (MIGRATION-code-searcher-to-skills.md)
3. Begin Phase 1 implementation (Code Index infrastructure)
