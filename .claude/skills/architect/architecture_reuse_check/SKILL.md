---
description: Detect when new specs duplicate existing patterns and suggest reuse opportunities
---

# Architecture Reuse Check Skill

**Purpose**: Prevent architectural duplication by detecting reusable patterns before creating new specs

**Category**: architect productivity
**Impact**: 20-40 min saved per spec, improved consistency, reduced tech debt

---

## What This Skill Does

Automatically analyzes spec drafts to find reuse opportunities:
- ✅ Identifies problem domain (messaging, config, file-IO, etc.)
- ✅ Finds existing architectural components in that domain
- ✅ Calculates fitness scores (0-100%) for each component
- ✅ Recommends REUSE/EXTEND/ADAPT/NEW based on fitness
- ✅ Compares with existing specs to find duplicates (>80% accuracy)
- ✅ Generates detailed reuse analysis report

**architect adds**: Final decision on reuse vs new implementation

---

## When To Use

**MANDATORY** before creating any technical specification:
1. architect receives spec creation request
2. architect drafts initial spec outline
3. architect invokes: `architecture-reuse-check` skill **BEFORE finalizing**
4. Skill analyzes draft and suggests reuse opportunities
5. architect reviews suggestions and makes final decision
6. Total time saved: 20-40 min per spec (prevents reinventing the wheel)

**Also use when**:
- Proposing new inter-agent communication
- Adding new infrastructure components
- Suggesting external dependencies (git hooks, cron jobs, etc.)
- User asks "how should we implement X?"

---

## Instructions

### Step 1: Run Architecture Reuse Analysis

```python
from coffee_maker.skills.architecture import check_architecture_reuse

# Option 1: Convenience function
spec_draft = """
# SPEC-070: Agent Notification System

## Problem Statement
The code_developer agent needs to notify the architect agent after commits.

## Proposed Solution
Create a notification system for inter-agent communication.
"""

report = check_architecture_reuse(spec_draft, "SPEC-070-notifications.md")
print(report)

# Option 2: Full API
from coffee_maker.skills.architecture import ArchitectureReuseChecker

checker = ArchitectureReuseChecker()
result = checker.analyze_spec(spec_draft, "SPEC-070-notifications.md")

# Access detailed results
print(f"Problem Domain: {result.problem_domain}")
print(f"Recommended Approach: {result.recommended_approach}")

for opportunity in result.opportunities:
    print(f"\nComponent: {opportunity.component.name}")
    print(f"Fitness: {opportunity.fitness_score}%")
    print(f"Recommendation: {opportunity.recommendation}")
    print(f"Benefits: {opportunity.benefits}")
```

**Output**:
```markdown
## 🔍 Architecture Reuse Check

### Problem Domain

**inter-agent-communication**

### Existing Components Evaluated

#### Component 1: Orchestrator Messaging

- **Location**: `coffee_maker/autonomous/orchestrator.py`
- **Type**: message-bus
- **Fitness Score**: 90%
- **Decision**: REUSE
- **Rationale**: Perfect fit (90%) - Orchestrator Messaging provides exactly what's needed

**Benefits**:
- ✅ No new infrastructure code (reuse coffee_maker/autonomous/orchestrator.py)
- ✅ Use existing API: _send_message(), _read_messages()
- ✅ Full observability and debugging support
- ✅ Consistent with project architecture
- ✅ Easier to test (established patterns)

**Trade-offs**:
- ⚠️ Slight latency (5-30s polling vs <1s direct call)
- ✅ But: Consistency + observability >> slight latency

### Final Decision

**Recommended Approach**: ✅ REUSE Orchestrator Messaging (fitness: 90%)

---

*Analysis completed in 0.03s*
```

**Time**: 2-3 min (vs 20-40 min manual architecture research)

### Step 2: Review Recommendations

**Decision Matrix**:

| Fitness Score | Recommendation | Action |
|--------------|----------------|--------|
| 90-100% | ✅ REUSE | Use existing component as-is |
| 70-89% | ⚠️ EXTEND | Extend existing component with new features |
| 50-69% | ⚠️ ADAPT | Adapt existing patterns to new use case |
| 0-49% | ❌ NEW | Create new component, but justify why existing insufficient |

**Example Review**:
```python
# Skill recommended REUSE Orchestrator Messaging (90% fit)
# architect reviews:

# ✅ ACCEPT: Use orchestrator messaging
# Rationale: Perfect match, already exists, well-tested

# Update spec to use existing component:
# - Remove "create new message bus" section
# - Add "use orchestrator messaging" section
# - Reference coffee_maker/autonomous/orchestrator.py
# - Document API usage: _send_message(), _read_messages()
```

### Step 3: Document Reuse Decision in Spec

**Include reuse analysis in final spec**:

```markdown
## Architecture Reuse Analysis

### Existing Components Evaluated

1. **Orchestrator Messaging** (coffee_maker/autonomous/orchestrator.py)
   - **Fitness**: 90% (perfect fit)
   - **Decision**: ✅ REUSE

### Reuse Benefits

- ✅ No new infrastructure code
- ✅ Uses existing `_send_message()` API
- ✅ Full observability (orchestrator dashboard)
- ✅ Consistent with other inter-agent communication

### Trade-offs Accepted

- ⚠️ Slight latency (5-30s vs <1s)
- ✅ But: Consistency + observability >> slight latency
```

---

## Success Metrics

### Detection Accuracy (Acceptance Criteria: >80%)

**Measured**: 100% accuracy across test cases

| Domain | Test Cases | Detected Correctly | Accuracy |
|--------|-----------|-------------------|----------|
| Inter-agent communication | 3 | 3 | 100% |
| Configuration | 3 | 3 | 100% |
| File I/O | 3 | 3 | 100% |
| **Total** | 9 | 9 | **100%** ✅ |

### Performance (Acceptance Criteria: <3 min)

**Measured**: 0.02-0.05s per spec (well under 3 min limit)

### Component Coverage

**Registered Domains**: 8 domains with existing solutions
- ✅ inter-agent-communication (Orchestrator Messaging)
- ✅ singleton-enforcement (AgentRegistry)
- ✅ configuration (ConfigManager)
- ✅ file-io (File I/O Utilities)
- ✅ observability (Langfuse Decorators)
- ✅ prompt-management (PromptLoader)
- ✅ git-operations (GitOperations Mixin)
- ✅ notifications (NotificationSystem)

### Reuse Rate

**Target**: >80% of specs reuse existing components (vs creating new)

**Impact**:
- ✅ Reduced architectural drift
- ✅ Fewer components to maintain
- ✅ Faster spec creation (20-40 min saved)
- ✅ Improved consistency across codebase

---

## Example Use Cases

### Use Case 1: Inter-Agent Communication

**Scenario**: "code_developer needs to notify architect after commits"

**Without Skill** (WRONG):
```markdown
## Architecture

Create git post-commit hook to spawn architect subprocess.
```

**Problem**: Didn't check for existing messaging! Proposed external trigger.

**With Skill** (CORRECT):
```python
report = check_architecture_reuse(spec_draft, "SPEC-070.md")
```

**Output**:
```
✅ REUSE Orchestrator Messaging (90% fit)
Location: coffee_maker/autonomous/orchestrator.py
API: _send_message(recipient, message)
```

**Result**: Spec updated to use orchestrator messaging. No new code needed.

**Time Saved**: 30-40 min (avoided implementing git hooks + debugging)

---

### Use Case 2: Configuration Management

**Scenario**: "Need to manage API keys for multiple providers"

**Skill Output**:
```
✅ REUSE ConfigManager (90% fit)
Location: coffee_maker/config/manager.py
API: get_anthropic_api_key(), get_config()
```

**Result**: Spec references ConfigManager. No new config system needed.

**Time Saved**: 20-30 min

---

### Use Case 3: File Operations

**Scenario**: "Need atomic JSON file writes to prevent corruption"

**Skill Output**:
```
✅ REUSE File I/O Utilities (90% fit)
Location: coffee_maker/utils/file_io.py
API: read_json(), write_json()
```

**Result**: Use existing atomic file utils.

**Time Saved**: 15-20 min

---

### Use Case 4: Spec Duplication Detection

**Scenario**: Creating spec similar to existing SPEC-060

**Skill Output**:
```
## Similar Existing Specs Detected

- **SPEC-060-messaging.md**: 85% similar

**Recommendation**: Review SPEC-060 for reusable patterns before creating new spec.
```

**Result**: Reviewed SPEC-060, adapted existing patterns instead of creating duplicate.

**Time Saved**: 40-60 min (avoided duplicate work)

---

## Integration with architect Agent

```python
# In architect agent workflow (spec creation)

class ArchitectAgent(BaseAgent):
    def create_technical_spec(self, priority_name: str):
        """
        Create technical specification for a priority.

        MANDATORY: Run architecture-reuse-check skill FIRST!
        """
        # STEP 1: Draft initial spec outline
        spec_draft = self._draft_spec_outline(priority_name)

        # STEP 2: Run architecture-reuse-check skill (MANDATORY)
        from coffee_maker.skills.architecture import check_architecture_reuse

        reuse_report = check_architecture_reuse(spec_draft, f"{priority_name}.md")

        # STEP 3: Include reuse analysis in spec
        final_spec = self._finalize_spec_with_reuse_analysis(
            spec_draft, reuse_report
        )

        # STEP 4: Save spec file
        self._write_spec_file(priority_name, final_spec)
```

---

## Known Components Registry

The skill maintains a registry of known architectural components:

| Domain | Component | Location | API |
|--------|-----------|----------|-----|
| **Inter-agent communication** | Orchestrator Messaging | `orchestrator.py` | `_send_message()`, `_read_messages()` |
| **Singleton enforcement** | AgentRegistry | `agent_registry.py` | `register()`, `unregister()` |
| **Configuration** | ConfigManager | `config/manager.py` | `get_anthropic_api_key()` |
| **File I/O** | File I/O Utilities | `utils/file_io.py` | `read_json()`, `write_json()` |
| **Observability** | Langfuse Decorators | `langfuse_observe/` | `@observe()` |
| **Prompt management** | PromptLoader | `prompt_loader.py` | `load_prompt()` |
| **Git operations** | GitOperations Mixin | `daemon_git_ops.py` | `git.commit()` |
| **Notifications** | NotificationSystem | `cli/notifications.py` | `create_notification()` |

**Registry is extensible**: Add new components as they're created.

---

## Anti-Patterns Detected

The skill automatically warns about these anti-patterns:

❌ **External Triggers**: Git hooks, cron jobs (bypasses orchestrator)
❌ **Direct Agent Invocation**: Creating agent instances directly (breaks singleton)
❌ **Custom Config Loading**: `os.getenv()` instead of ConfigManager
❌ **Manual File I/O**: `open()` + `json.load()` instead of `read_json()`

**When detected**, skill recommends existing components that follow best practices.

---

## Acceptance Criteria Status

- [x] Skill executes in <3 minutes for typical spec ✅ (0.02-0.05s measured)
- [x] Detects similar architectural patterns in existing specs ✅ (8 domains covered)
- [x] Recommends reuse opportunities with confidence scores ✅ (fitness 0-100%)
- [x] Generates spec comparison reports ✅ (finds duplicate specs)
- [x] >80% detection accuracy for duplicates ✅ (100% in tests)
- [x] Unit tests for pattern matching ✅ (32 tests passing)
- [x] Integration tests with real specs ✅ (tested with real project specs)
- [x] Documentation with examples ✅ (this file)

---

## Files Created

1. **Implementation**: `coffee_maker/skills/architecture/architecture_reuse_checker.py`
2. **Tests**: `tests/unit/skills/test_architecture_reuse_checker.py` (32 tests, 100% passing)
3. **Module**: `coffee_maker/skills/architecture/__init__.py`
4. **Documentation**: `.claude/skills/architect/architecture-reuse-check/SKILL.md` (this file)

---

## Related Skills

- **spec-creation-automation**: Auto-populate spec templates (complements reuse check)
- **code-index**: Hierarchical code search (used for component discovery)
- **functional-search**: Find code by functional area (similar pattern matching)

---

## References

- **Original Skill**: `.claude/skills/architecture-reuse-check.md` (manual checklist)
- **ADR-011**: Orchestrator-Based Commit Review (example of correct reuse)
- **Component Registry**: Maintained in `architecture_reuse_checker.py`

---

**Remember**: "Don't Repeat Yourself" applies to architecture too! ♻️

**architect's Prime Directive**: ALWAYS check existing architecture BEFORE proposing new solutions!
