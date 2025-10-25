# BUG-003: Intent Classification Returns First Pattern Match Instead of Best Match

**Reporter**: assistant agent (during US-046 demo)
**Date**: 2025-10-16
**Severity**: Medium
**Status**: Open
**Component**: coffee_maker/cli/agent_router.py (user-listener intent classification)

---

## Summary

The user-listener's intent classification uses keyword pattern matching to route user requests to specialized agents. However, when multiple agents' patterns match a request, the router returns the first match from dictionary iteration order rather than finding the most specific or best match.

This causes misrouting in edge cases where requests could be handled by multiple agents.

---

## Steps to Reproduce

### Test Case 1: Code-Searcher Misrouting

**Input**: "Where is authentication implemented"

**Pattern Matches** (in order):
1. `code_developer`: "implement" matches ✓
2. `code_searcher`: "where is" matches ✓

**Current Behavior**:
```
Intent: code_developer (confidence: 0.90)
Delegated to: CODE_DEVELOPER
```

**Expected Behavior**:
```
Intent: code_searcher (confidence: 0.90)
Delegated to: ASSISTANT
```

**Why**: "Where is X" is a more specific 2-word pattern that should take priority over the generic "implement" keyword.

### Test Case 2: UX-Design-Expert Misrouting

**Input**: "Improve the dashboard UI"

**Pattern Matches** (in order):
1. `code_developer`: "dashboard" contains "pr" (false positive) or other keyword
2. `ux_design_expert`: "ui", "dashboard" match ✓

**Current Behavior**: May route to code_developer

**Expected Behavior**:
```
Intent: ux_design_expert (confidence: 0.90)
Delegated to: UX_DESIGN_EXPERT
```

---

## Root Cause Analysis

**File**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/agent_router.py`

**Function**: `AgentDelegationRouter.classify_intent()` (lines 115-138)

**Problematic Code**:
```python
def classify_intent(self, user_input: str) -> Tuple[AgentType, float]:
    """Classify user intent to determine appropriate agent."""
    lower_input = user_input.lower()
    for agent_type, keywords in self.patterns.items():
        if any(keyword in lower_input for keyword in keywords):
            self.logger.info(f"Intent classified: {agent_type.value} (pattern match)")
            return (agent_type, 0.9)  # ← BUG: Returns on FIRST match, not BEST match

    # Fallback to AI classification
    return self._classify_with_ai(user_input)
```

**Why This Is a Bug**:

1. **Dictionary Iteration Order**: The `patterns` dict is iterated in insertion order (Python 3.7+), but this order is arbitrary from a logical perspective:
   ```python
   self.patterns: Dict[AgentType, List[str]] = {
       AgentType.ARCHITECT: [...],         # Checked first
       AgentType.PROJECT_MANAGER: [...],   # Checked second
       AgentType.CODE_DEVELOPER: [...],    # Checked third (problematic!)
       AgentType.ASSISTANT: [...],         # Checked fourth
       AgentType.ASSISTANT: [...],     # Checked fifth (should be earlier!)
       AgentType.UX_DESIGN_EXPERT: [...],  # Checked sixth
   }
   ```

2. **No Specificity Ranking**: All keywords are treated equally:
   - "implement" (generic, 9 chars) same priority as "where is" (specific, 8 chars + multi-word)
   - "code" (generic) same priority as "find in code" (specific multi-word pattern)

3. **No Match Scoring**: Returns immediately on first match instead of:
   - Counting how many keywords match
   - Weighting keyword specificity (length, multi-word vs single-word)
   - Returning the agent with highest score

---

## Technical Impact

**Affected Functionality**:
- Requests for code analysis may route to code_developer instead of assistant (with code analysis skills)
- UI/UX design requests may route to code_developer instead of ux-design-expert
- Any request matching multiple patterns will route incorrectly

**User Impact**:
- Wrong agent receives the request
- User gets generic developer guidance instead of specialized code analysis
- Degrades user experience and agent effectiveness

**Severity Justification**:
- Not critical: AI fallback (0.8 confidence threshold) can catch these
- But high-confidence misroutes (0.90) bypass fallback
- Affects user satisfaction and routing accuracy

---

## Solution Requirements

### Requirement 1: Implement Pattern Priority Scoring

Create a scoring system that evaluates match quality:

```python
def _score_pattern_match(self, user_input: str, keywords: List[str]) -> float:
    """Score how well keywords match the user input.

    Scoring factors:
    - Number of keywords matched (more matches = higher score)
    - Keyword specificity (longer keywords = higher score)
    - Multi-word patterns (higher score than single words)
    - Position in text (matching at start = higher score)
    """
    score = 0.0
    lower_input = user_input.lower()

    for keyword in keywords:
        if keyword in lower_input:
            # Base points for match
            score += 1.0

            # Bonus for specificity (longer keywords)
            score += (len(keyword) / 20.0)  # Normalized to 0.05 per char

            # Bonus for multi-word patterns
            if ' ' in keyword:
                score += 0.5

            # Bonus for matching at start
            if lower_input.startswith(keyword):
                score += 0.5

    return score
```

### Requirement 2: Use Best Match Instead of First Match

Modify `classify_intent()` to:

```python
def classify_intent(self, user_input: str) -> Tuple[AgentType, float]:
    """Classify by returning best pattern match, not first."""
    lower_input = user_input.lower()

    # Score all agents
    best_agent = None
    best_score = 0.0

    for agent_type, keywords in self.patterns.items():
        score = self._score_pattern_match(lower_input, keywords)
        if score > best_score:
            best_agent = agent_type
            best_score = score

    # Return best match if any patterns matched
    if best_agent is not None:
        self.logger.info(f"Intent classified: {best_agent.value} (pattern match, score: {best_score:.2f})")
        return (best_agent, 0.9)

    # Fallback to AI classification
    return self._classify_with_ai(user_input)
```

### Requirement 3: Add Comprehensive Test Coverage

Add unit tests in `tests/unit/test_agent_router.py`:

```python
def test_classify_intent_prefers_code_searcher_over_code_developer():
    """Test that 'where is' pattern routes to assistant (with code analysis skills), not code-developer."""
    router = AgentDelegationRouter(mock_ai_service)
    agent_type, confidence = router.classify_intent("Where is authentication implemented")
    assert agent_type == AgentType.ASSISTANT
    assert confidence == 0.9

def test_classify_intent_prefers_ux_expert_for_ui_questions():
    """Test that UI questions route to ux-design-expert."""
    router = AgentDelegationRouter(mock_ai_service)
    agent_type, confidence = router.classify_intent("Improve the dashboard UI")
    assert agent_type == AgentType.UX_DESIGN_EXPERT
    assert confidence == 0.9

def test_pattern_scoring_rewards_specificity():
    """Test that scoring rewards more specific patterns."""
    router = AgentDelegationRouter(mock_ai_service)

    # "find in code" (specific) should score higher than "code" (generic)
    score1 = router._score_pattern_match("find authentication in code", ["find in code"])
    score2 = router._score_pattern_match("find authentication in code", ["code"])
    assert score1 > score2

def test_pattern_scoring_rewards_multiple_matches():
    """Test that scoring rewards multiple keyword matches."""
    router = AgentDelegationRouter(mock_ai_service)

    # Input with both "ui" and "dashboard" should score higher than just one
    score1 = router._score_pattern_match("Make the dashboard look better with UI improvements",
                                         ["ui", "dashboard"])
    score2 = router._score_pattern_match("Make the dashboard look better with UI improvements",
                                         ["dashboard"])
    assert score1 > score2
```

### Requirement 4: Preserve Backward Compatibility

- No API changes to `classify_intent()` - still returns `(AgentType, float)`
- Confidence remains 0.9 for pattern matches
- AI fallback threshold (0.8) remains unchanged
- User-facing behavior same, just more accurate

### Requirement 5: Update Documentation

- Update `.claude/agents/user_listener.md` with improved pattern matching logic
- Document the scoring system
- Update example classifications
- Add notes about specificity and multi-word patterns

---

## Expected Behavior Once Fixed

### Case 1: Code-Searcher Query
```
Input: "Where is authentication implemented"
Pattern matches: code_developer (score: 1.0), code_searcher (score: 3.5)
Result: ASSISTANT (highest score: 3.5)
Confidence: 0.90
Delegate to: assistant (with code analysis skills) ✓
```

### Case 2: UX-Design-Expert Query
```
Input: "Improve the dashboard UI"
Pattern matches: code_developer (score: 1.0), ux_design_expert (score: 2.5)
Result: UX_DESIGN_EXPERT (highest score: 2.5)
Confidence: 0.90
Delegate to: ux-design-expert ✓
```

### Case 3: Multi-Word Pattern Preference
```
Input: "Find where config is loaded"
Pattern matches: code_developer (score: 1.0), code_searcher (score: 4.0)
Result: ASSISTANT (multi-word pattern "find in code" gets bonus)
Confidence: 0.90
Delegate to: assistant (with code analysis skills) ✓
```

---

## Implementation Timeline

**Estimated Effort**: 4-5 hours

1. **Design & Planning** (30 min)
   - Review pattern scoring requirements
   - Design scoring algorithm

2. **Implementation** (2 hours)
   - Add `_score_pattern_match()` method
   - Modify `classify_intent()` to use best match
   - Update logging to show scoring

3. **Testing** (1.5 hours)
   - Add unit tests for all edge cases
   - Run integration tests
   - Manual testing with example queries

4. **Documentation** (30 min)
   - Update `.claude/agents/user_listener.md`
   - Add scoring examples
   - Document pattern preferences

5. **Review & Merge** (30 min)
   - Code review
   - Pre-commit hook checks
   - Merge to main branch

---

## Files to Modify

| File | Changes |
|------|---------|
| `coffee_maker/cli/agent_router.py` | Add scoring logic, update classify_intent() |
| `tests/unit/test_agent_router.py` | Add comprehensive test coverage |
| `.claude/agents/user_listener.md` | Document improved pattern matching |

---

## References

- **Demo Report**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/demos/user-listener-demo.md`
- **Implementation**: US-046 (Complete)
- **Next Priority**: Pattern matching enhancement for Phase 2

---

## Sign-Off

**Found During**: US-046 demo and testing
**Reporter**: assistant (Demo Creator + Bug Reporter)
**Status**: Ready for project_manager review and ROADMAP prioritization
**Recommendation**: Fix before next major release or mark as Phase 2+ enhancement
