# SPEC-064: Code-Searcher Responsibility Migration

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: ADR-009 (Retire code-searcher Agent), SPEC-001 (Advanced Code Search Skills)

---

## Executive Summary

This specification defines the **migration plan** for retiring the `code-searcher` agent and delegating its responsibilities to `architect` and `code_developer` agents via **Claude Code Skills**.

**Key Changes**:
- **Retire code-searcher agent entirely** (6 agents → 5 agents)
- **Delegate deep code analysis to architect** (using skills)
- **Delegate security audits to code_developer** (using skills during implementation)
- **Replace agent workflow with skills** (faster, more accessible)
- **No capability loss** - all functionality preserved via skills

**Impact**:
- **Simpler Architecture**: Fewer agents to coordinate (17% reduction)
- **Better Performance**: Skills execute deterministically (<200ms vs 10-30s with LLM)
- **Broader Access**: ALL agents can use code search skills (not just one dedicated agent)
- **CFR-007 Compliance**: Reduced agent count lowers context budget pressure

---

## Problem Statement

### Current Architecture

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
1. **Deep Codebase Analysis**: Pattern detection, code forensics
2. **Security Audits**: Vulnerability scanning, dependency tracing
3. **Dependency Analysis**: Impact analysis for changes
4. **Refactoring Opportunities**: Identify code duplication, complexity
5. **Architectural Analysis**: Component structure, coupling analysis

**Current Workflow (4 agents involved)**:
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

Total: 4 agents, 10-30 seconds latency
```

### Why Retire code-searcher?

**1. Agent Overhead**
- Singleton enforcement (only one instance can run)
- Status tracking (agent_status.json)
- Langfuse observability overhead
- Complex delegation workflow (4 agents)

**2. Limited Availability**
- Only code-searcher can perform deep analysis
- architect CANNOT directly search code (must delegate)
- code_developer CANNOT use security audits during implementation (must delegate)
- Result: Bottleneck and communication overhead

**3. No Structured Index**
- Searches are ad-hoc and incomplete
- grep/rg searches find keywords, not functional concepts
- No codebase map (categories → components → implementations)
- Repetitive analysis (same searches run multiple times)

**4. Skills Provide BETTER Solution**
- Code Index (3-level hierarchy) enables fast functional searches
- Skills execute deterministically (same results every time)
- ALL agents can use skills (not just one)
- No agent coordination overhead

---

## Proposed Solution

### New Architecture

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
                           │  architect agent    │ ⭐ ADR-010
                           │                     │
                           │ Triggered by:       │
                           │ - Commit reviews    │
                           │ - Git hooks         │
                           └─────────────────────┘
```

### Responsibility Delegation

| Former code-searcher Capability | New Owner | New Approach |
|--------------------------------|-----------|--------------|
| **Code Forensics** | Skill: `code-forensics` | Used by: architect, assistant, code_developer |
| **Security Audit** | Skill: `security-audit` | Used by: architect, code_developer (during implementation) |
| **Dependency Tracer** | Skill: `dependency-tracer` | Used by: architect |
| **Functional Search** | Skill: `functional-search` | Used by: architect, assistant |
| **Code Explanation** | Skill: `code-explainer` | Used by: architect, assistant |
| **Code Index Maintenance** | architect (via commit review) | Git hooks trigger architect + Manual updates (ADR-010) |

**Key Insight**: Skills are NOT owned by any agent. They're infrastructure available to ALL agents.

---

## Migration Plan

### Phase 1: Build Skills System (BEFORE retiring agent)

**Goal**: Ensure skills provide ALL functionality code-searcher had

**Tasks**:
1. **Implement Code Index Infrastructure** (see SPEC-001)
   - 3-level hierarchical index (data/code_index/index.json)
   - Full rebuild algorithm
   - Incremental update algorithm
   - Git hook integration (post-commit, post-merge)
   - Scheduled rebuild (cron job)

2. **Implement 5 Core Skills**:
   - `code-forensics`: Deep pattern analysis
   - `security-audit`: Vulnerability scanning
   - `dependency-tracer`: Dependency analysis
   - `functional-search`: Find code by function
   - `code-explainer`: Explain code in accessible terms

3. **Test Skills Thoroughly**:
   - Validate capabilities match code-searcher
   - Performance benchmarks (target: <200ms for queries)
   - Integration tests with architect, assistant, code_developer

**Success Criteria**:
- [ ] Code Index generated for MonolithicCoffeeMakerAgent codebase
- [ ] 5 core skills implemented and tested
- [ ] Skills match or exceed code-searcher capabilities
- [ ] Performance: Queries <200ms (vs 10-30s before)
- [ ] architect can search and explain code using skills
- [ ] code_developer can run security audits using skills

**Estimated Time**: 2-3 weeks

---

### Phase 2: Gradual Transition

**Goal**: Agents adopt skills instead of delegating to code-searcher

**Tasks**:
1. **architect Adopts Skills**:
   ```python
   # Before: Delegate to code-searcher
   code_searcher.analyze_authentication_code()

   # After: Use skills directly
   from coffee_maker.skills.functional_search import functional_search

   results = functional_search("authentication")
   # Returns hierarchical results instantly
   ```

2. **assistant Uses Skills for Complex Searches**:
   ```python
   # Before: Delegate to code-searcher
   user_listener → code-searcher → assistant → project_manager

   # After: Use skills directly
   user_listener → assistant (uses functional_search) → project_manager
   # Faster, fewer agents involved
   ```

3. **code_developer Uses Security Audit During Implementation**:
   ```python
   # Before: Delegate to code-searcher (blocking)
   code-searcher.run_security_audit()  # Wait for response

   # After: Use skills directly (non-blocking)
   from coffee_maker.skills.security_audit import security_audit

   audit_results = security_audit("coffee_maker/payment/")
   # Instant results, no delegation
   ```

**Monitor Usage**:
- Track skill invocations (Langfuse)
- Compare performance vs code-searcher
- Collect feedback from agents

**Success Criteria**:
- [ ] architect uses skills instead of delegating to code-searcher
- [ ] assistant uses skills for complex searches
- [ ] code_developer uses security-audit during implementation
- [ ] Skill usage metrics tracked in Langfuse
- [ ] No functionality gaps identified

**Estimated Time**: 1 week

---

### Phase 3: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Skills system design, code index structure, skill delegation patterns
  - **Code Quality**: Index generation algorithms, skill implementation patterns, error handling
  - **Security**: File access controls (read-only for searches), no arbitrary code execution in skills
  - **Performance**: Skill execution time (<200ms target), index generation efficiency
  - **CFR Compliance**:
    - CFR-007: Skills don't bloat agent context (<30% budget preserved)
    - CFR-008: Skill boundaries (skills are tools, not agents)
    - CFR-009: Graceful skill failures (fallback to manual grep if index unavailable)
  - **Dependency Approval**: If new packages added for code analysis (e.g., AST parsers)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 4: Retire code-searcher

**Goal**: Remove code-searcher agent completely (AFTER skills proven equivalent)

**Tasks**:
1. **Remove Agent Configuration**:
   ```bash
   rm .claude/agents/code-searcher.md
   rm data/agent_status/code_searcher_status.json
   ```

2. **Update Agent Registry**:
   ```python
   # coffee_maker/autonomous/agent_registry.py

   class AgentType(Enum):
       # ... other agents ...
       # CODE_SEARCHER = "code_searcher"  ← REMOVE THIS LINE
   ```

3. **Update Documentation**:
   - `.claude/CLAUDE.md`: Remove code-searcher from Agent Tool Ownership Matrix
   - `docs/roadmap/ROADMAP.md`: Remove code-searcher from agent list
   - `docs/DOCUMENT_OWNERSHIP_MATRIX.md`: Update delegation workflows

4. **Archive Agent Definition**:
   ```bash
   mkdir -p docs/architecture/archived
   mv .claude/agents/code-searcher.md docs/architecture/archived/code-searcher-agent.md
   ```

5. **Add README to docs/code-searcher/**:
   ```markdown
   # Code-Searcher Analysis Documents

   **IMPORTANT**: The code-searcher agent has been retired (2025-10-18).

   These documents were created by the code-searcher agent before its retirement.
   They remain as historical reference.

   ## Migration

   Code search functionality is now provided by **Claude Code Skills**:
   - `code-forensics`: Deep pattern analysis
   - `security-audit`: Vulnerability scanning
   - `dependency-tracer`: Dependency analysis
   - `functional-search`: Find code by function
   - `code-explainer`: Explain code

   See `.claude/skills/` for skill definitions.

   ## New Workflow

   Instead of delegating to code-searcher, use skills directly:

   \`\`\`python
   from coffee_maker.skills.functional_search import functional_search

   results = functional_search("authentication")
   \`\`\`

   For more information, see:
   - ADR-009: Retire code-searcher Agent
   - SPEC-001: Advanced Code Search Skills Architecture
   ```

6. **Git Commit**:
   ```bash
   git add .
   git commit -m "feat: Retire code-searcher agent, replace with skills system

   - Remove .claude/agents/code-searcher.md
   - Remove AgentType.CODE_SEARCHER from AgentRegistry
   - Update .claude/CLAUDE.md (Agent Tool Ownership Matrix)
   - Update docs/roadmap/ROADMAP.md (agent list)
   - Archive code-searcher agent definition
   - Add README to docs/code-searcher/ explaining transition

   Skills system provides all code-searcher functionality:
   - code-forensics, security-audit, dependency-tracer
   - functional-search, code-explainer
   - Faster (<200ms vs 10-30s), accessible to all agents

   See ADR-009 and SPEC-001 for details.

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Success Criteria**:
- [ ] code-searcher removed from .claude/agents/
- [ ] .claude/CLAUDE.md updated (no code-searcher references)
- [ ] docs/roadmap/ROADMAP.md updated
- [ ] AgentRegistry updated (no AgentType.CODE_SEARCHER)
- [ ] All tests pass
- [ ] No production incidents

**Estimated Time**: 1 day

---

### Phase 5: Cleanup & Documentation

**Goal**: Finalize transition and update all references

**Tasks**:
1. **Update All Documentation**:
   - Search for "code-searcher" in all docs
   - Replace with skill references where appropriate
   - Update delegation workflow diagrams

2. **Update Decision Framework**:
   ```markdown
   # Before
   "Who should handle X?"
       ↓
   Is it about code internals? → code-searcher

   # After
   "Who should handle X?"
       ↓
   Is it about code internals? → Use skills (code-forensics, functional-search)
   ```

3. **Final Validation**:
   - Run all integration tests
   - Verify no code references to code-searcher remain
   - Check agent status files (no orphaned code_searcher_status.json)

4. **User Communication**:
   - Announce transition in changelog
   - Update quickstart guide
   - Provide migration examples

**Success Criteria**:
- [ ] No code-searcher references in docs (except archives and historical context)
- [ ] All integration tests passing
- [ ] User documentation updated
- [ ] Migration guide created

**Estimated Time**: 2 days

---

## Skill Implementation Details

### 1. code-forensics

**Location**: `.claude/skills/code-forensics.md`

**Purpose**: Deep pattern analysis and code structure examination

**Capabilities**:
- Detect code duplication (>20% similar blocks)
- Identify large files (>500 LOC)
- Find god classes (>15 methods)
- Locate TODO/FIXME comments
- Analyze cyclomatic complexity

**Usage**:
```python
from coffee_maker.skills.code_forensics import code_forensics

results = code_forensics("coffee_maker/autonomous/")
# Returns:
# {
#   "duplicated_blocks": [...],
#   "large_files": [...],
#   "god_classes": [...],
#   "todos": [...],
#   "complexity_hotspots": [...]
# }
```

### 2. security-audit

**Location**: `.claude/skills/security-audit.md`

**Purpose**: Vulnerability scanning and security analysis

**Capabilities**:
- Detect hardcoded secrets (API keys, passwords)
- Find SQL injection risks (f-strings in queries)
- Identify XSS vulnerabilities (unescaped HTML)
- Check file permission issues
- Scan for known CVEs in dependencies

**Usage**:
```python
from coffee_maker.skills.security_audit import security_audit

results = security_audit("coffee_maker/payment/")
# Returns:
# {
#   "critical": [...],  # Immediate fixes required
#   "high": [...],
#   "medium": [...],
#   "low": [...],
#   "summary": "..."
# }
```

### 3. dependency-tracer

**Location**: `.claude/skills/dependency-tracer.md`

**Purpose**: Dependency analysis and impact assessment

**Capabilities**:
- Trace all code that depends on a module
- Find circular dependencies
- Identify unused imports
- Calculate dependency graph depth
- Estimate refactoring impact

**Usage**:
```python
from coffee_maker.skills.dependency_tracer import dependency_tracer

results = dependency_tracer("coffee_maker/auth/login.py")
# Returns:
# {
#   "direct_dependents": [...],
#   "indirect_dependents": [...],
#   "circular_deps": [...],
#   "impact_score": 75,  # 0-100 (how many files affected)
#   "refactoring_risk": "HIGH"
# }
```

### 4. functional-search

**Location**: `.claude/skills/functional-search.md`

**Purpose**: Find code by functional area (not keywords)

**Capabilities**:
- Search Code Index by category
- Find all code related to a feature
- Filter by complexity, dependencies
- Return hierarchical results (category → component → implementation)

**Usage** (already detailed in SPEC-001):
```python
from coffee_maker.skills.functional_search import functional_search

results = functional_search("authentication")
# Returns hierarchical results with file:line locations
```

### 5. code-explainer

**Location**: `.claude/skills/code-explainer.md`

**Purpose**: Explain code in accessible terms

**Capabilities**:
- Multi-level summaries (executive, technical, implementation)
- Complexity analysis
- Pattern detection
- Issue identification
- Improvement suggestions

**Usage** (already detailed in SPEC-001):
```python
from coffee_maker.skills.code_explainer import code_explainer

explanation = code_explainer("coffee_maker/auth/login.py:45:89", level="technical")
# Returns detailed explanation with patterns, issues, suggestions
```

---

## Agent Ownership Matrix Updates

### Before (with code-searcher)

| Tool/Capability | Owner | Usage |
|----------------|-------|-------|
| Code search (simple) | assistant | 1-2 files |
| Code search (complex) | code-searcher | Deep analysis |
| Code analysis docs | project_manager | Creates docs |

### After (with skills)

| Tool/Capability | Owner | Usage |
|----------------|-------|-------|
| Code search (ALL) | Skill: functional-search | architect, assistant, code_developer |
| Security audit | Skill: security-audit | architect, code_developer |
| Dependency analysis | Skill: dependency-tracer | architect |
| Code forensics | Skill: code-forensics | architect, assistant |
| Code explanation | Skill: code-explainer | architect, assistant |
| Code Index maintenance | architect (commit review) | Git hooks, manual (ADR-010) |
| Code analysis docs | project_manager | Creates docs (data from skills) |

---

## Testing Strategy

### Capability Parity Tests

**Goal**: Ensure skills provide ALL functionality code-searcher had

```python
# tests/integration/test_code_searcher_migration.py

def test_functional_search_matches_code_searcher_results():
    """Test functional-search skill returns same results as code-searcher."""
    # code-searcher result (baseline)
    code_searcher_result = {
        "authentication": [
            "coffee_maker/auth/login.py:45-89",
            "coffee_maker/auth/jwt_utils.py:15-50",
            "coffee_maker/auth/oauth_login.py:20-60"
        ]
    }

    # functional-search skill result
    from coffee_maker.skills.functional_search import functional_search

    skill_result = functional_search("authentication")
    skill_files = [impl.file for impl in skill_result.implementations]

    # Verify all code-searcher results found by skill
    for file_location in code_searcher_result["authentication"]:
        assert any(file_location.startswith(f) for f in skill_files), \
            f"Skill missed file: {file_location}"

def test_security_audit_detects_same_issues():
    """Test security-audit skill detects same issues as code-searcher."""
    from coffee_maker.skills.security_audit import security_audit

    results = security_audit("coffee_maker/")

    # Verify known issues detected
    assert len(results["critical"]) > 0  # Should find at least one critical issue
    assert any("hardcoded secret" in issue["description"].lower()
               for issue in results["critical"] + results["high"])
```

### Performance Tests

```python
def test_skill_performance_faster_than_code_searcher():
    """Test skills are faster than code-searcher delegation."""
    import time

    # Baseline: code-searcher delegation time (~10-30 seconds)
    code_searcher_baseline = 15.0  # seconds

    # Measure skill execution time
    start = time.time()
    from coffee_maker.skills.functional_search import functional_search
    results = functional_search("payment")
    elapsed = time.time() - start

    # Skill should be at least 10x faster
    assert elapsed < (code_searcher_baseline / 10), \
        f"Skill too slow: {elapsed}s (expected <1.5s)"
```

---

## Rollout Checklist

### Pre-Migration (Skills System Ready)

- [ ] Code Index infrastructure implemented
- [ ] 5 core skills implemented (code-forensics, security-audit, dependency-tracer, functional-search, code-explainer)
- [ ] Skills tested with architect, assistant, code_developer
- [ ] Performance validated (queries <200ms)
- [ ] Capability parity tests passing
- [ ] Documentation complete (SPEC-001, ADR-009)

### Migration (Retire code-searcher)

- [ ] architect using skills instead of code-searcher
- [ ] assistant using skills for complex searches
- [ ] code_developer using security-audit during implementation
- [ ] Skill usage metrics tracked in Langfuse
- [ ] All capability parity tests passing

### Post-Migration (Cleanup)

- [ ] code-searcher removed from .claude/agents/
- [ ] .claude/CLAUDE.md updated
- [ ] docs/roadmap/ROADMAP.md updated
- [ ] AgentRegistry updated (no AgentType.CODE_SEARCHER)
- [ ] code-searcher agent definition archived
- [ ] README added to docs/code-searcher/
- [ ] All tests passing
- [ ] User communication sent
- [ ] No production incidents

---

## Success Metrics

| Metric | Baseline (Before) | Target (After) | Measurement |
|--------|-------------------|----------------|-------------|
| **Agent Count** | 6 agents | 5 agents | 17% reduction |
| **Code Search Time** | 10-30 seconds (code-searcher) | <200ms (skills) | 50-150x faster |
| **Search Availability** | 1 agent (code-searcher) | ALL agents (via skills) | 5x accessibility |
| **Context Budget** | Higher (6 agents) | Lower (5 agents) | CFR-007 compliance |
| **Capability Coverage** | 100% (code-searcher) | 100% (skills) | No functionality lost |

---

## Risks & Mitigations

### Risk 1: Skills Don't Match code-searcher Capabilities
**Impact**: Users lose functionality
**Probability**: LOW (with proper validation)
**Mitigation**:
- Capability parity tests ensure 100% coverage
- Parallel testing during Phase 2
- User validation before retirement
- Rollback plan (re-enable code-searcher if needed)

### Risk 2: Performance Regression
**Impact**: Skills slower than expected
**Probability**: LOW (with optimization)
**Mitigation**:
- Performance benchmarks (<200ms target)
- Caching strategies for repeated queries
- Index optimization
- Fallback to manual grep if index stale

### Risk 3: User Confusion During Transition
**Impact**: Users still ask for code-searcher
**Probability**: MEDIUM (during Phase 2-3)
**Mitigation**:
- Clear communication before transition
- user_listener updated to explain skills system
- Gradual transition (Phase 2)
- Migration guide with examples

---

## Conclusion

Retiring the code-searcher agent and replacing it with a skills system provides:

1. **Simpler Architecture**: 6 agents → 5 agents (17% reduction)
2. **Better Performance**: Skills execute <200ms (50-150x faster than code-searcher)
3. **Broader Access**: ALL agents can use code search (not just one dedicated agent)
4. **CFR-007 Compliance**: Reduced agent count lowers context budget pressure
5. **No Capability Loss**: Skills provide ALL functionality code-searcher had

This specification provides the roadmap for Phase 6 of the ACE Framework implementation.

---

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/code-forensics.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/security-audit.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/dependency-tracer.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/functional-search.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/code-explainer.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/code-searcher/README.md`

**Next Steps**:
1. Review and approve this spec
2. Ensure ADR-009 is accepted
3. Assign implementation to code_developer
4. Begin Phase 1 (Skills System) implementation
5. Monitor transition during Phase 2
6. Retire code-searcher in Phase 3
