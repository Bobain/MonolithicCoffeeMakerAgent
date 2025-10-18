# SPEC-050: Architect POC Creation Framework

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: US-050
**Estimated Duration**: 1-2 days (8-16 hours framework setup + ongoing POC creation)

---

## Executive Summary

Create a standardized framework for architect to create Proof of Concept (POC) implementations for complex features. POCs reduce implementation risk by validating technical approaches before full code_developer implementation.

**Key Innovation**: POC serves as **working reference implementation** that proves feasibility and guides code_developer.

---

## 🔍 Architecture Reuse Check (MANDATORY)

### Problem Domain
**Documentation + Code organization** - Need standardized directory structure and documentation templates for POCs.

### Existing Components Evaluated

#### 1. POC-072 Structure (Existing Example)
- **Location**: `docs/architecture/pocs/POC-072-team-daemon/`
- **Functionality**: Working POC with README, Python files, tests
- **Fitness**: 100% (perfect template for POC structure)
- **Decision**: ✅ **REUSE** this structure as standard
- **Rationale**:
  - Already exists and works well
  - Clear README format
  - Includes working code + tests
  - Scoped appropriately (20-30% of full implementation)

#### 2. Template Pattern (From SPEC-000-template.md)
- **Location**: `docs/architecture/specs/SPEC-000-template.md`
- **Functionality**: Template for creating specs
- **Fitness**: 90% (same pattern for POC README template)
- **Decision**: ✅ **ADAPT** for POC README template
- **Rationale**:
  - Proven template pattern in project
  - Easy to create POC-000-template/
  - Consistent with existing conventions

#### 3. Decision Matrix (New Component)
- **Location**: N/A (needs to be created)
- **Functionality**: Decide when POC needed vs just spec
- **Fitness**: 0% (doesn't exist)
- **Decision**: ✅ **CREATE** decision matrix
- **Rationale**:
  - Core requirement of US-050
  - Simple table-based decision (effort + complexity)
  - No reusable component exists

### Final Decision

**Chosen Approach**: ✅ **REUSE POC-072 structure + ADAPT template pattern + CREATE decision matrix**

**Reuse Benefits**:
- ✅ POC-072 already proves structure works
- ✅ No new directory conventions needed
- ✅ Template pattern consistent with project
- ✅ Only new component is decision matrix (simple table)

**Trade-offs Accepted**:
- ⚠️ Manual decision (architect evaluates effort + complexity)
- ✅ But: Simple and explicit (no complex automation)

---

## Problem Statement

### Current Situation
architect creates comprehensive technical specs, but for complex features:
- **No working code reference**: code_developer must figure out implementation from scratch
- **Higher risk**: Hidden complexity not discovered until implementation
- **Longer time**: code_developer explores approaches architect could validate upfront
- **Ambiguity**: Specs may be unclear without concrete examples

**Example**: POC-072 validated that multi-process orchestration works BEFORE code_developer spent 15-20 hours implementing it.

### Goal
Standardize when and how architect creates POCs:
1. Clear criteria for when POC needed
2. Standard POC structure (directory, files, documentation)
3. Documentation templates (README format)
4. Integration with spec creation workflow

### Non-Goals
- ❌ POCs for every spec (only complex features)
- ❌ Production-ready POC code (minimal implementation only)
- ❌ Full test coverage in POC (just prove it works)

---

## POC Decision Matrix

### When to Create a POC

| Estimated Effort | Technical Complexity | Create POC? | Rationale |
|------------------|----------------------|-------------|-----------|
| <1 day (< 8 hours) | Low | ❌ NO | Straightforward, spec sufficient |
| <1 day (< 8 hours) | Medium | ❌ NO | Spec with code examples sufficient |
| <1 day (< 8 hours) | High | ⚠️ MAYBE | If novel pattern, consider POC |
| 1-2 days (8-16 hours) | Low | ❌ NO | Spec sufficient |
| 1-2 days (8-16 hours) | Medium | ⚠️ MAYBE | If integration risks, consider POC |
| 1-2 days (8-16 hours) | High | ✅ YES | POC recommended |
| >2 days (>16 hours) | Low | ❌ NO | Spec sufficient |
| >2 days (>16 hours) | Medium | ⚠️ MAYBE | If integration risks, consider POC |
| >2 days (>16 hours) | High | ✅ YES | **POC REQUIRED** |

### Complexity Factors

**Technical Complexity = High** if ANY of these apply:
- ✅ Novel architectural pattern (not used in project before)
- ✅ External system integration (GitHub API, Puppeteer, databases)
- ✅ Multi-process or async complexity
- ✅ Performance-critical (caching, rate limiting, optimization)
- ✅ Security-sensitive (authentication, authorization, data protection)
- ✅ Cross-cutting concerns (affects multiple agents)

**Technical Complexity = Medium** if SOME of these apply:
- ⚠️ Uses existing patterns but combines them in new ways
- ⚠️ Moderate integration (file I/O, CLI commands)
- ⚠️ Some testing complexity
- ⚠️ Multiple components but straightforward

**Technical Complexity = Low** if NONE of these apply:
- ℹ️ Simple refactor or code cleanup
- ℹ️ Uses well-established patterns
- ℹ️ Single component, no integration
- ℹ️ Easy to test

### Examples

| Feature | Effort | Complexity | POC Needed? |
|---------|--------|------------|-------------|
| Multi-Agent Orchestration (US-072) | 15-20 hours | **High** (multi-process, IPC) | ✅ **YES** (POC-072 created) |
| Claude Skills Phase 1 (US-055) | 84-104 hours | **Very High** (new infrastructure, 5+ components) | ✅ **YES** (POC-055 required) |
| Architect-Only Spec Creation (US-047) | 16-24 hours | **Medium** (workflow changes) | ❌ NO (spec sufficient) |
| Silent Background Agents (US-048) | 4-6 hours | **Low** (parameter change) | ❌ NO (spec overkill) |
| POC Creation Framework (US-050) | 8-16 hours | **Low** (documentation + templates) | ❌ NO (this spec sufficient) |

---

## Standard POC Structure

### Directory Layout

```
docs/architecture/pocs/POC-{number}-{feature-slug}/
├── README.md              # POC overview (REQUIRED)
├── {component1}.py        # Minimal implementation (REQUIRED)
├── {component2}.py        # Additional components (if needed)
├── test_poc.py            # Basic tests proving it works (REQUIRED)
├── requirements.txt       # POC-specific dependencies (OPTIONAL)
└── data/                  # Sample data files (OPTIONAL)
```

### README.md Template

```markdown
# POC-{number}: {Feature Name}

**Created**: {Date}
**Author**: architect agent
**Status**: Proof of Concept
**Time Budget**: {X-Y} hours
**Related**: SPEC-{number}

---

## Purpose

This POC proves {specific technical concepts} work correctly:

1. **{Concept 1}**: {What we're validating}
2. **{Concept 2}**: {What we're validating}
3. **{Concept 3}**: {What we're validating}

**What This POC Does NOT Prove**:
- {Out of scope item 1}
- {Out of scope item 2}
- {Out of scope item 3}

**Scope**: {X}% of full SPEC-{number} implementation

---

## What It Proves

### ✅ {Concept 1} Works
- {Specific validation point}
- {Specific validation point}

### ✅ {Concept 2} Works
- {Specific validation point}
- {Specific validation point}

---

## How to Run

### 1. Install Dependencies (if any)

\`\`\`bash
cd docs/architecture/pocs/POC-{number}-{feature-slug}/
pip install -r requirements.txt  # Only if requirements.txt exists
\`\`\`

### 2. Run the POC

\`\`\`bash
python {main_file}.py
\`\`\`

**Expected Output**:
\`\`\`
{Sample output showing POC works}
\`\`\`

### 3. Run Tests

\`\`\`bash
python test_poc.py
# OR
pytest test_poc.py
\`\`\`

**Expected**: All tests pass

---

## Key Learnings

### What Worked Well
- {Finding 1}
- {Finding 2}

### What Needs Adjustment
- {Finding 1} → {Recommended change for full implementation}
- {Finding 2} → {Recommended change for full implementation}

### Recommendations for Full Implementation
1. {Recommendation 1}
2. {Recommendation 2}
3. {Recommendation 3}

---

## Code Structure

### {component1}.py
{Brief description of what this component does}

**Key Classes/Functions**:
- \`{ClassName}\`: {Purpose}
- \`{function_name}()\`: {Purpose}

### {component2}.py
{Brief description of what this component does}

**Key Classes/Functions**:
- \`{ClassName}\`: {Purpose}

---

## Time Spent

- Planning: {X} hours
- Implementation: {Y} hours
- Testing: {Z} hours
- **Total**: {X+Y+Z} hours

**Estimated Full Implementation**: {Total hours for SPEC-{number}}

---

## Next Steps (for code_developer)

1. Read this POC to understand approach
2. Review SPEC-{number} for full requirements
3. Implement full version with:
   - Production error handling
   - Complete test coverage (>80%)
   - Logging and observability
   - Documentation
4. Reference POC code for architectural decisions
5. **Do NOT copy-paste POC code** (it's minimal, not production-ready)

---

**End of POC-{number} README**
```

### Python File Guidelines

**Minimal Implementation**:
- 20-30% of full feature scope
- Core logic only (no error handling edge cases)
- Basic logging (print statements OK)
- Simple comments explaining decisions

**Example** (from POC-072):
```python
class TeamDaemon:
    """Minimal proof-of-concept for multi-agent orchestration.

    This is NOT production code - it proves the concept works.
    Full implementation needs:
    - Better error handling
    - Resource limits
    - Configuration
    - Full logging
    """

    def __init__(self):
        self.agents = {}
        self.queue = MessageQueue()  # Simple SQLite queue

    def spawn_agent(self, agent_name: str):
        """Spawn agent subprocess (minimal version)."""
        process = subprocess.Popen(
            ["python", f"{agent_name}.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.agents[agent_name] = process
        print(f"✅ {agent_name} started (PID: {process.pid})")

    # ... rest of minimal implementation
```

**Test File Guidelines**:
```python
import unittest
from {component1} import {ClassName}

class TestPOC(unittest.TestCase):
    """Basic tests proving POC works (NOT comprehensive)."""

    def test_{concept}_works(self):
        """Test that {concept} works as expected."""
        # Arrange
        obj = ClassName()

        # Act
        result = obj.do_something()

        # Assert
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
```

---

## Integration with architect Workflow

### Updated Spec Creation Process

```python
# coffee_maker/autonomous/agents/architect_agent.py

class ArchitectAgent(BaseAgent):
    def create_technical_spec(self, priority_name: str):
        """Create technical spec for priority.

        NEW: Check if POC needed and create it.
        """
        # 1. Run architecture-reuse-check skill (MANDATORY)
        reuse_analysis = self._run_architecture_reuse_check(priority_name)

        # 2. Extract requirements
        requirements = self._extract_requirements(priority_name)

        # 3. Evaluate if POC needed
        effort_hours = requirements["estimated_effort_hours"]
        complexity = requirements["technical_complexity"]  # "low", "medium", "high"

        needs_poc = self._should_create_poc(effort_hours, complexity)

        if needs_poc:
            logger.info(f"POC needed for {priority_name} (effort: {effort_hours}h, complexity: {complexity})")

            # 4. Create POC first
            poc_dir = self._create_poc(priority_name, requirements)

            logger.info(f"POC created: {poc_dir}")
            logger.info("Testing POC before creating full spec...")

            # 5. Validate POC works
            if not self._validate_poc(poc_dir):
                logger.error("POC validation failed - approach may not work!")
                # Ask user before proceeding
                return

        # 6. Create full spec (references POC if created)
        spec = self._generate_spec(priority_name, requirements, poc_dir if needs_poc else None)

        logger.info(f"Spec created: {spec}")

    def _should_create_poc(self, effort_hours: float, complexity: str) -> bool:
        """Decision matrix for POC creation."""
        # Effort > 2 days (16 hours) AND complexity = High → POC REQUIRED
        if effort_hours > 16 and complexity == "high":
            return True

        # Effort > 2 days AND complexity = Medium → MAYBE (ask user)
        if effort_hours > 16 and complexity == "medium":
            # TODO: Ask user via user_listener
            return False  # Default to no for now

        # All other cases → No POC
        return False

    def _create_poc(self, priority_name: str, requirements: dict) -> Path:
        """Create POC directory and files from template."""
        # Extract POC number from priority
        poc_number = self._extract_us_number(priority_name)
        feature_slug = self._slugify(requirements["title"])

        # Create directory
        poc_dir = Path(f"docs/architecture/pocs/POC-{poc_number}-{feature_slug}")
        poc_dir.mkdir(parents=True, exist_ok=True)

        # Generate README from template
        readme = self._generate_poc_readme(poc_number, requirements)
        (poc_dir / "README.md").write_text(readme, encoding="utf-8")

        # TODO: Generate skeleton Python files (future)
        # For now, architect creates them manually

        logger.info(f"POC directory created: {poc_dir}")
        logger.info("Please implement POC code manually")

        return poc_dir
```

---

## Implementation Plan

### Phase 1: Template Creation (2-3 hours)

**Tasks**:
1. Create POC-000-template/ directory
   - Copy POC-072 structure
   - Create README template
   - Add template Python files
   - Add template test file
2. Document POC creation guide
   - File: `docs/architecture/POC_CREATION_GUIDE.md`
   - Include decision matrix
   - Include examples

### Phase 2: architect Integration (3-4 hours)

**Tasks**:
1. Add `_should_create_poc()` method to ArchitectAgent
2. Add `_create_poc()` method to ArchitectAgent
3. Update `create_technical_spec()` workflow
4. Test POC creation for new spec

### Phase 3: Documentation (2-3 hours)

**Tasks**:
1. Update architect.md with POC workflow
2. Update CLAUDE.md with POC conventions
3. Create examples (reference POC-072)

---

## Success Criteria

**Functional**:
- [ ] POC-000-template/ directory created
- [ ] README template comprehensive and clear
- [ ] Decision matrix documented
- [ ] architect can create POC directories automatically
- [ ] POCs referenced in specs (link to POC directory)

**Quality**:
- [ ] POC structure consistent (POC-072 model)
- [ ] README template easy to fill out
- [ ] Decision matrix clear and actionable
- [ ] Documentation complete (POC_CREATION_GUIDE.md)

**User Experience**:
- [ ] architect knows when to create POC (decision matrix)
- [ ] POC README makes it clear what's proven
- [ ] code_developer can use POC as reference

---

## Examples

### Example 1: US-072 (POC Created)

**Decision**:
- Effort: 15-20 hours (>2 days)
- Complexity: HIGH (multi-process, IPC, fault tolerance)
- **Result**: ✅ **POC REQUIRED**

**POC Created**: `docs/architecture/pocs/POC-072-team-daemon/`

**What It Proved**:
- ✅ Subprocess spawning works
- ✅ Message passing works
- ✅ Health monitoring works
- ✅ Graceful shutdown works

**Time Saved**: 3-4 hours (validated approach before 15-20 hour implementation)

### Example 2: US-055 (POC Required)

**Decision**:
- Effort: 84-104 hours (>2 days)
- Complexity: VERY HIGH (new infrastructure, Code Execution Tool, 5+ components)
- **Result**: ✅ **POC REQUIRED**

**POC Should Create**: `docs/architecture/pocs/POC-055-claude-skills/`

**What It Should Prove**:
- ✅ Code Execution Tool integration works
- ✅ SkillLoader can discover and load skills
- ✅ ExecutionController API design sound
- ✅ Security sandboxing effective

**Estimated POC Time**: 4-6 hours
**Time Savings**: 8-12 hours (avoid costly mistakes in 84-104 hour implementation)

---

## Risk Analysis

**Risks**:
1. **architect skips POC creation**: MITIGATION: Decision matrix makes it clear when required
2. **POC takes too long**: MITIGATION: Time-box to 20-30% of full implementation
3. **POC code copied into production**: MITIGATION: Clear README warnings

**Assumptions**:
- architect follows decision matrix
- POC scoped appropriately (20-30%)
- code_developer uses POC as reference (not copy-paste)

---

## Appendix: POC Creation Checklist

**Before Creating POC**:
- [ ] Estimated effort >2 days (16+ hours)?
- [ ] Technical complexity = High?
- [ ] Novel pattern OR external integration OR performance-critical?
- [ ] Decision matrix says POC required?

**During POC Creation**:
- [ ] Create POC directory: `docs/architecture/pocs/POC-{number}-{slug}/`
- [ ] Write README from template
- [ ] Implement minimal code (20-30% scope)
- [ ] Write basic tests (prove it works)
- [ ] Run and validate POC
- [ ] Document learnings and recommendations

**After POC Creation**:
- [ ] Reference POC in technical spec
- [ ] Commit POC to git
- [ ] Link POC in spec: "See POC-{number} for proof-of-concept"
- [ ] Inform code_developer POC available

---

**End of SPEC-050**
