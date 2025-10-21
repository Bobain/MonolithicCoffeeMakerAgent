# SPEC-XXX: [Skill Name] Skill

**Status**: Draft
**Author**: architect agent
**Date**: YYYY-MM-DD
**Related**: [Related priorities, ADRs, specs]
**User Story**: [US-XXX]

---

## Executive Summary

This specification defines the **[Skill Name] Skill**, a Claude Code Skill that [one-sentence description of skill purpose].

**Key Capabilities**:
- **Capability 1**: [Brief description]
- **Capability 2**: [Brief description]
- **Capability 3**: [Brief description]

**Impact**:
- **Time Savings**: [X-Y hrs/month saved]
- **Success Rate**: [X% improvement]
- **Speedup**: [Xx faster than manual approach]

---

## Problem Statement

### Current Pain Points

**1. [Pain Point 1 Name]**
```
Current Process (Manual):
1. Step 1 (X min)
2. Step 2 (X min)
3. Step 3 (X min)

Total: X-Y min
```

**Problem**: [What makes this painful]

**2. [Pain Point 2 Name]**
[Description with evidence]

### User Requirements

From [Related Priority/ADR]:
- **Requirement 1**: [Description]
- **Requirement 2**: [Description]
- **Requirement 3**: [Description]

---

## Proposed Solution

### High-Level Architecture

```
SKILL WORKFLOW

1. Input
   [Description of inputs]
         ↓
2. Processing Phase 1
   [Description]
         ↓
3. Processing Phase 2
   [Description]
         ↓
4. Output
   [Description of outputs]

Total Time: X-Y min (vs X-Y min manual)
```

### Workflow Example

**Scenario**: [Concrete example use case]

```
Step 1: [Action]
----------------------------
Input: [Example input]

Skill Output: [Example output]

Step 2: [Action]
----------------------------
[Details]

Result: [Outcome]

Time Saved: X min manual → Y min automated (Xx faster)
```

---

## Component Design

### 1. [Component Name 1] (Main Logic)

**Responsibility**: [What this component does]

**Interface**:
```python
class ComponentName:
    """[Docstring]"""

    def __init__(self, ...):
        """Initialize component."""
        pass

    def main_method(self, ...) -> Result:
        """
        [Method description]

        Args:
            param1: [Description]

        Returns:
            [Return value description]
        """
        pass
```

**Algorithms**:
1. **Algorithm 1**: [Description, complexity]
2. **Algorithm 2**: [Description, complexity]

### 2. [Component Name 2]

**Responsibility**: [What this component does]

[Similar structure to Component 1]

---

## Technical Details

### Data Structures

```python
@dataclass
class SkillInput:
    """Input to skill."""
    field1: str
    field2: int

@dataclass
class SkillOutput:
    """Output from skill."""
    result1: str
    result2: List[str]
    success: bool
```

### Algorithms

#### 1. [Algorithm Name]
```python
def algorithm_name(input: Data) -> Result:
    """
    [Algorithm description]

    Complexity: O(n) time, O(1) space
    """
    pass
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/skills/test_[skill_name].py

def test_component_basic_functionality():
    """Test basic skill functionality."""
    skill = SkillName()
    result = skill.execute(input_data)

    assert result.success is True
    assert len(result.output) > 0

def test_edge_case_handling():
    """Test edge cases."""
    # Test with empty input, invalid data, etc.
```

### Integration Tests

```python
# tests/ci_tests/test_[skill_name]_integration.py

def test_end_to_end_workflow():
    """Test complete skill workflow."""
    # Full workflow test
```

---

## Rollout Plan

### Phase 1: Core Implementation (Week 1)
- [ ] Implement [Component 1]
- [ ] Implement [Component 2]
- [ ] Unit tests (>80% coverage)

### Phase 2: Integration (Week 2)
- [ ] Integrate with [Agent/System]
- [ ] Integration tests
- [ ] Performance testing

### Phase 3: Validation (Week 3)
- [ ] Test on real use cases
- [ ] Measure time savings
- [ ] User feedback

### Phase 4: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - Architectural compliance
  - Code quality
  - Security
  - Performance
  - CFR compliance
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback
- [ ] architect gives final approval

---

## Success Metrics

| Metric | Baseline (Manual) | Target (Automated) | Measurement |
|--------|-------------------|-------------------|-------------|
| **Time per Execution** | X-Y min | A-B min | Timed execution |
| **Success Rate** | X% | Y% | Successful runs / total |
| **Speedup** | 1x | Xx | Baseline / automated time |
| **Monthly Savings** | 0 hrs | X-Y hrs | Cumulative time savings |

---

## Risks & Mitigations

### Risk 1: [Risk Name]
**Impact**: [What could go wrong]
**Probability**: LOW/MEDIUM/HIGH

**Mitigation**:
- Strategy 1
- Strategy 2

---

## Conclusion

The [Skill Name] Skill provides:

1. **Speed**: Xx faster than manual approach
2. **Consistency**: Same process every time
3. **Reliability**: X% success rate
4. **Savings**: X-Y hrs/month

**Recommendation**: Approve and implement in [Timeline]

---

**Files to Create**:
- `.claude/skills/[skill-name]/SKILL.md`
- `coffee_maker/skills/[skill_name].py`
- `tests/unit/skills/test_[skill_name].py`

**Next Steps**:
1. Review and approve this spec
2. Assign implementation to code_developer
3. Begin Phase 1 implementation
4. Integrate and validate

---

**Author**: architect agent
**Date**: YYYY-MM-DD
**Status**: Ready for user approval
