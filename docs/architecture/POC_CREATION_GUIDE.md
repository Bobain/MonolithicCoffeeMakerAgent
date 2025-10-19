# POC Creation Guide

**Last Updated**: 2025-10-19
**Owner**: architect agent
**Related**: SPEC-050, US-050

---

## Purpose

This guide explains when and how to create Proof of Concept (POC) implementations for complex features. POCs reduce implementation risk by validating technical approaches before full code_developer implementation.

---

## When to Create a POC

### Decision Matrix

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

---

## POC Structure

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

### README Template

See `docs/architecture/pocs/POC-000-template/README.md` for the complete template.

**Key Sections**:
1. **Purpose**: What specific technical concepts are being validated
2. **What It Proves**: Specific validation points for each concept
3. **How to Run**: Step-by-step instructions
4. **Key Learnings**: What worked well and what needs adjustment
5. **Next Steps**: Guidance for code_developer

---

## How to Create a POC

### Step 1: Evaluate Complexity

Use the decision matrix above to determine if POC is needed:

```python
# Example evaluation
feature = "Multi-Agent Orchestration (US-072)"
effort_hours = 18  # >16 hours = >2 days
complexity = "high"  # Multi-process, IPC, fault tolerance

# Decision: ✅ POC REQUIRED (effort >2 days AND complexity = high)
```

### Step 2: Create POC Directory

```bash
# Extract POC number from priority
poc_number="072"
feature_slug="team-daemon"

# Create directory
mkdir -p docs/architecture/pocs/POC-${poc_number}-${feature_slug}/
cd docs/architecture/pocs/POC-${poc_number}-${feature_slug}/
```

### Step 3: Copy Template

```bash
# Copy README template
cp ../POC-000-template/README.md ./

# Copy Python templates
cp ../POC-000-template/component_template.py ./{your_component}.py
cp ../POC-000-template/test_poc.py ./
```

### Step 4: Fill Out README

Edit `README.md` and replace all placeholders:

- `{number}`: POC number (e.g., "072")
- `{Feature Name}`: Descriptive name (e.g., "Multi-Agent Orchestration")
- `{Date}`: Creation date (YYYY-MM-DD)
- `{X-Y}`: Time budget (e.g., "2-3")
- `{Concept 1}`, `{Concept 2}`, etc.: Specific concepts being validated
- `{main_file}`: Main Python file name
- All other placeholders with actual content

### Step 5: Implement Minimal Code

**Scope**: 20-30% of full feature implementation

**Guidelines**:
- Core logic only (no error handling edge cases)
- Basic logging (print statements OK)
- Simple comments explaining decisions
- Prove the hardest part works

**Example** (from POC-072):
```python
class TeamDaemon:
    """Minimal proof-of-concept for multi-agent orchestration.

    This is NOT production code - it proves the concept works.
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
```

### Step 6: Write Basic Tests

**Scope**: Prove concept works (NOT comprehensive)

**Guidelines**:
- Test core functionality only
- 3-5 tests maximum
- Use unittest or pytest
- No edge cases, no error handling

**Example**:
```python
import unittest
from team_daemon import TeamDaemon

class TestPOC(unittest.TestCase):
    def test_daemon_spawns_agent(self):
        daemon = TeamDaemon()
        daemon.spawn_agent("test_agent")
        self.assertIn("test_agent", daemon.agents)
```

### Step 7: Run and Validate

```bash
# Run the POC
python {main_file}.py

# Expected: Should complete without errors

# Run tests
python test_poc.py
# OR
pytest test_poc.py

# Expected: All tests pass
```

### Step 8: Document Learnings

Update README.md with:
- **What Worked Well**: Successful validations
- **What Needs Adjustment**: Issues discovered
- **Recommendations**: How full implementation should differ

### Step 9: Commit POC

```bash
# From repository root
git add docs/architecture/pocs/POC-{number}-{feature-slug}/
git commit -m "feat: Add POC-{number} for {Feature Name}

Validates:
- {Concept 1}
- {Concept 2}
- {Concept 3}

Time: {X} hours
Next: Create SPEC-{number} referencing this POC

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 10: Reference in Spec

In `SPEC-{number}`, add a reference to the POC:

```markdown
## Proof of Concept

See [POC-{number}](../pocs/POC-{number}-{feature-slug}/) for working proof-of-concept.

**What It Proves**:
- {Concept 1}: ✅ Validated
- {Concept 2}: ✅ Validated
- {Concept 3}: ✅ Validated

**Recommendations from POC**:
1. {Recommendation 1}
2. {Recommendation 2}
```

---

## Examples

### Example 1: US-072 (Multi-Agent Orchestration)

**Decision**:
- Effort: 15-20 hours (>2 days)
- Complexity: HIGH (multi-process, IPC, fault tolerance)
- **Result**: ✅ **POC REQUIRED**

**POC Created**: `docs/architecture/pocs/POC-072-team-daemon/`

**What It Proved**:
- ✅ Subprocess spawning works
- ✅ Message passing works (SQLite queue)
- ✅ Health monitoring works
- ✅ Graceful shutdown works

**Time**: 2-3 hours POC, saved 3-4 hours in full implementation

### Example 2: US-055 (Claude Skills Phase 1)

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

### Example 3: US-048 (Silent Background Agents)

**Decision**:
- Effort: 4-6 hours (<1 day)
- Complexity: LOW (parameter change)
- **Result**: ❌ **NO POC** (spec sufficient)

**Rationale**: Simple change, no novel patterns, straightforward implementation

---

## Common Mistakes to Avoid

### ❌ Making POC Too Complex
**Problem**: POC takes too long (>30% of full implementation time)
**Solution**: Keep it minimal - 20-30% scope only

### ❌ Skipping Tests
**Problem**: Can't prove POC works without tests
**Solution**: Always include `test_poc.py` with basic tests

### ❌ Production-Ready Code
**Problem**: Spending time on error handling, edge cases, etc.
**Solution**: Prove concept only - full implementation adds production concerns

### ❌ Copy-Pasting POC into Production
**Problem**: POC code lacks production quality
**Solution**: POC is reference only - code_developer implements fresh

### ❌ Not Documenting Learnings
**Problem**: Insights from POC lost
**Solution**: Always update README with "Key Learnings" section

---

## Integration with architect Workflow

### Updated Spec Creation Process

```python
# Simplified workflow
def create_technical_spec(priority_name: str):
    """Create technical spec for priority."""
    # 1. Run architecture-reuse-check (MANDATORY)
    reuse_analysis = run_architecture_reuse_check(priority_name)

    # 2. Extract requirements
    requirements = extract_requirements(priority_name)
    effort_hours = requirements["estimated_effort_hours"]
    complexity = requirements["technical_complexity"]

    # 3. Evaluate if POC needed
    needs_poc = should_create_poc(effort_hours, complexity)

    if needs_poc:
        # 4. Create POC first
        poc_dir = create_poc(priority_name, requirements)

        # 5. Validate POC works
        if not validate_poc(poc_dir):
            logger.error("POC validation failed!")
            return

    # 6. Create full spec (references POC if created)
    spec = generate_spec(priority_name, requirements, poc_dir if needs_poc else None)
```

---

## Success Criteria

**Before POC**:
- [ ] Estimated effort >2 days OR complexity = High?
- [ ] Decision matrix consulted?
- [ ] Time budget set (20-30% of full implementation)?

**During POC**:
- [ ] Directory structure follows template?
- [ ] README filled out completely?
- [ ] Minimal code (20-30% scope)?
- [ ] Basic tests included?
- [ ] POC runs successfully?
- [ ] Tests pass?

**After POC**:
- [ ] README documents learnings?
- [ ] POC committed to git?
- [ ] Spec references POC?
- [ ] code_developer informed POC available?

---

## Quick Reference

### Command Cheat Sheet

```bash
# Create POC directory
mkdir -p docs/architecture/pocs/POC-{number}-{feature-slug}/

# Copy template
cp docs/architecture/pocs/POC-000-template/README.md \
   docs/architecture/pocs/POC-{number}-{feature-slug}/

# Run POC
cd docs/architecture/pocs/POC-{number}-{feature-slug}/
python {main_file}.py

# Run tests
pytest test_poc.py

# Commit
git add docs/architecture/pocs/POC-{number}-{feature-slug}/
git commit -m "feat: Add POC-{number} for {Feature Name}"
```

### Template Locations

- **README Template**: `docs/architecture/pocs/POC-000-template/README.md`
- **Component Template**: `docs/architecture/pocs/POC-000-template/component_template.py`
- **Test Template**: `docs/architecture/pocs/POC-000-template/test_poc.py`

---

## Additional Resources

- **SPEC-050**: Full technical specification for POC creation framework
- **US-050**: User story for this feature
- **POC-072**: Example POC (multi-agent orchestration)
- **SPEC-000-template.md**: Template pattern this follows

---

**End of POC Creation Guide**
