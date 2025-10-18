# GUIDELINE-006: ACE Curator Role in Skill Evolution

**Status**: Active
**Created**: 2025-10-18
**Author**: architect
**Purpose**: Define how ACE curator guides skill creation, modification, and deprecation

---

## Overview

The **ACE (Agent Context Evolving) framework** uses three agents to create a continuous improvement loop:
- **Generator**: Captures execution traces
- **Reflector**: Analyzes traces, extracts insights (delta items)
- **Curator**: Maintains evolving playbooks based on insights

This guideline defines how the **curator participates in skill evolution** - guiding which skills to create, modify, or deprecate based on observed agent behavior.

---

## ACE Framework in MonolithicCoffeeMakerAgent

### Current ACE Implementation

**1. Generator** (`docs/generator/`)
- Captures all agent executions as traces
- Records: Task, duration, files accessed, decisions made, outcomes
- Output: Execution trace files (timestamped)

**2. Reflector** (`docs/reflector/`)
- Analyzes execution traces
- Identifies patterns, inefficiencies, bottlenecks
- Extracts delta items (insights about what worked/didn't)
- Output: Delta items (insights files)

**3. Curator** (`docs/curator/`)
- Synthesizes delta items into playbooks
- Maintains evolving best practices
- Recommends process improvements
- Output: Playbooks (actionable patterns)

---

## Curator's Role in Skill Evolution

### The Skill Evolution Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     SKILL EVOLUTION LOOP                         │
└─────────────────────────────────────────────────────────────────┘

1. OBSERVE (Generator)
   ├─ Agent executes task (e.g., architect creates spec)
   ├─ Generator captures execution trace
   └─ Records: Time spent (117 min), steps taken, files accessed

2. REFLECT (Reflector)
   ├─ Analyzes execution traces over time
   ├─ Identifies pattern: "Spec creation always takes 90-150 min"
   ├─ Compares to similar tasks: "Code search: 15-30 min of spec time"
   └─ Creates delta item: "BOTTLENECK: Spec creation - code search is manual and repetitive"

3. CURATE (Curator)
   ├─ Synthesizes multiple delta items
   ├─ Identifies skill opportunity: "Automate code discovery for specs"
   ├─ Creates playbook entry:
   │  "When creating technical spec, use code-discovery skill to find
   │   relevant files automatically. Reduces spec time by 78%."
   └─ Recommends: "Create spec-creation-automation skill"

4. PROPOSE (project_manager)
   ├─ Reads curator playbooks
   ├─ Identifies top recommendations
   ├─ Collaborates with architect to design skill
   └─ Proposes skill to user for approval

5. IMPLEMENT (code_developer)
   ├─ Reads technical spec (from architect)
   ├─ Implements skill
   └─ Deploys skill for agent use

6. MEASURE (Generator)
   ├─ Agent uses new skill
   ├─ Generator captures execution trace with skill usage
   ├─ Records: Time saved (92 min), accuracy (90%+)
   └─ Loop continues (measure effectiveness, refine skill)
```

---

## Curator Responsibilities in Skill Lifecycle

### 1. Skill Identification (Proactive)

**Input**: Delta items from reflector
**Process**: Synthesize patterns across multiple executions
**Output**: Skill recommendation in playbook

**Example**:
```markdown
## Playbook Entry: Spec Creation Bottleneck

**Observed Pattern**: 15-20 specs created per month, 90-150 min each
**Delta Items Analyzed**: 23 delta items over 2 months
**Bottleneck Identified**: Code discovery (manual grepping: 15-30 min per spec)

**Recommendation**: Create skill "spec-creation-automation"
**Expected Impact**: Reduce spec creation from 117 min → 25 min (78% reduction)
**Priority**: HIGH (23-30.7 hours/month saved)
**Confidence**: HIGH (consistent pattern across all specs)
```

---

### 2. Skill Modification (Reactive)

**Input**: Delta items showing skill inefficiency
**Process**: Analyze skill usage data, identify improvement areas
**Output**: Skill modification recommendation

**Example**:
```markdown
## Playbook Entry: test-failure-analysis Skill Improvement

**Observed Pattern**: Skill used 45 times, accuracy 85% (target: 90%+)
**Delta Items Analyzed**: 12 delta items showing false positives
**Issue Identified**: Skill incorrectly categorizes timeout errors as "assertion failures"

**Recommendation**: Modify test-failure-analysis skill
**Change Needed**: Add timeout error category, improve error classification
**Expected Impact**: Accuracy 85% → 92%
**Priority**: MEDIUM (improves existing skill)
```

---

### 3. Skill Deprecation (Data-Driven)

**Input**: Delta items showing low skill usage or negative impact
**Process**: Analyze skill adoption, measure ROI
**Output**: Deprecation recommendation

**Example**:
```markdown
## Playbook Entry: legacy-code-analysis Skill Deprecation

**Observed Pattern**: Skill used 2 times in 3 months (expected: 10-15 times)
**Delta Items Analyzed**: 8 delta items showing preference for manual analysis
**Issue Identified**: Skill too slow (12 min vs 8 min manual), output not actionable

**Recommendation**: Deprecate legacy-code-analysis skill
**Reason**: Low adoption, negative time savings, better alternatives exist
**Migration**: Use code-searcher agent directly instead
**Priority**: LOW (cleanup)
```

---

### 4. Skill Prioritization (Strategic)

**Input**: Multiple skill recommendations
**Process**: Rank by impact × frequency × confidence
**Output**: Prioritized skill implementation roadmap

**Example**:
```markdown
## Playbook: Skill Implementation Priority (Q4 2025)

**High Priority** (Implement immediately):
1. context-budget-optimizer (saves 26.7-40 hrs/month, confidence: HIGH)
2. spec-creation-automation (saves 23-30.7 hrs/month, confidence: HIGH)

**Medium Priority** (Implement next sprint):
3. dependency-conflict-resolver (saves 3.3-5 hrs/month, confidence: MEDIUM)
4. async-workflow-coordinator (saves 5-10 hrs/month, confidence: MEDIUM)

**Low Priority** (Backlog):
5. langfuse-prompt-sync (saves 3.7-5.6 hrs/month, confidence: LOW - not yet needed)

**Total Expected Savings**: 61.7-91.3 hours/month
**Implementation Effort**: 58 hours over 8 weeks
**ROI**: 12-19x in first year
```

---

## Integration with Project Manager

### How project_manager Uses Curator Playbooks

**Step 1: Regular Playbook Review**
```python
# project_manager daily routine
def review_curator_playbooks(self):
    """Review curator playbooks for skill recommendations."""
    playbooks = read_playbooks("docs/curator/playbooks/")

    skill_recommendations = extract_skill_recommendations(playbooks)

    for recommendation in skill_recommendations:
        if recommendation["priority"] == "HIGH":
            self.propose_skill_to_user(recommendation)
```

**Step 2: Collaborate with Architect**
```python
def propose_skill_to_user(self, recommendation):
    """Propose skill to user after architect validation."""
    # Step 1: Request architect create technical spec
    architect_spec = request_architect_spec(recommendation)

    # Step 2: Calculate ROI
    roi = calculate_roi(
        time_saved=recommendation["time_saved"],
        implementation_effort=architect_spec["estimated_effort"]
    )

    # Step 3: Present to user
    proposal = f"""
    ## Skill Recommendation (from ACE Curator)

    **Skill**: {recommendation["skill_name"]}
    **Bottleneck Identified**: {recommendation["bottleneck"]}
    **Expected Savings**: {recommendation["time_saved"]} hours/month
    **Implementation Effort**: {architect_spec["estimated_effort"]} hours
    **ROI**: {roi}x in first year
    **Confidence**: {recommendation["confidence"]}

    **Curator's Recommendation**: {recommendation["rationale"]}

    Do you approve implementation?
    """

    await user.ask(proposal)
```

---

## Curator Playbook Structure

### Playbook Format

**File**: `docs/curator/playbooks/YYYY-MM-skill-evolution.md`

**Structure**:
```markdown
# Skill Evolution Playbook - October 2025

**Generated**: 2025-10-18
**Delta Items Analyzed**: 47 items (2025-09-01 to 2025-10-18)
**Execution Traces Reviewed**: 312 traces across all agents

---

## Executive Summary

- Bottlenecks Identified: 6
- Skills Recommended: 5 new, 2 modifications, 1 deprecation
- Expected Monthly Savings: 108 hours
- Implementation Effort: 58 hours
- ROI: 12-19x in first year

---

## Skill Recommendations

### 1. CREATE: spec-creation-automation

**Priority**: HIGH
**Agent**: architect
**Bottleneck**: Spec creation (117 min avg)
**Solution**: Automate code discovery, template population, time estimation
**Expected Savings**: 23-30.7 hours/month
**Confidence**: HIGH (based on 23 spec creations observed)
**Delta Items**: #12, #18, #24, #29, #31 (pattern: "manual code search repetitive")

**Curator's Rationale**:
Observed consistent pattern across all spec creations: architect spends
15-30 min manually grepping for relevant code. This is automatable with
high confidence. Recommendation: Create skill to automate code discovery
and template population. Expected 78% time reduction.

---

### 2. CREATE: context-budget-optimizer

**Priority**: CRITICAL
**Agent**: ALL
**Bottleneck**: CFR-007 violations (48 min each, 40-60 times/month)
**Solution**: Proactive context budget checking, intelligent summarization
**Expected Savings**: 26.7-40 hours/month
**Confidence**: HIGH (CFR-007 violations observed 47 times in 6 weeks)
**Delta Items**: #3, #7, #15, #22, #28, #35, #41 (pattern: "context overflow, manual reduction")

**Curator's Rationale**:
CFR-007 violations are THE most frequent bottleneck observed. Every agent
experiences context overflow multiple times per week. Manual reduction is
trial-and-error, wasting 30-60 min per occurrence. Agent startup skills
partially solve this, but a general context optimizer is critical for
all agents. Recommendation: HIGHEST PRIORITY.

---

### 3. MODIFY: test-failure-analysis

**Priority**: MEDIUM
**Current Performance**: 85% accuracy (target: 90%+)
**Issue**: Timeout errors misclassified as assertion failures
**Solution**: Add timeout category, improve error classification algorithm
**Expected Improvement**: 85% → 92% accuracy
**Confidence**: MEDIUM (based on 12 false positive observations)
**Delta Items**: #19, #25, #33 (pattern: "test-failure-analysis incorrect category")

**Curator's Rationale**:
Skill is valuable (used 45 times) but accuracy below target. Delta items
show consistent misclassification of timeout errors. Fix: Add explicit
timeout detection logic. Low effort (2 hours), high impact on user trust.

---

### 4. DEPRECATE: legacy-code-analysis

**Priority**: LOW
**Usage**: 2 times in 3 months (expected: 10-15 times)
**Issue**: Slower than manual (12 min vs 8 min), output not actionable
**Recommendation**: Remove skill, use code-searcher agent instead
**Migration Path**: code-searcher provides better analysis in less time
**Confidence**: HIGH (clear usage pattern: agents avoid this skill)
**Delta Items**: #11, #17 (pattern: "prefer manual analysis over skill")

**Curator's Rationale**:
Skill created 6 months ago, never adopted. Agents consistently choose
manual analysis or code-searcher over this skill. Performance data shows
skill is actually slower than alternatives. Recommendation: Deprecate,
free up maintenance effort, direct users to better alternatives.

---

## Metrics & Trends

### Skill Usage (Last 30 Days)

| Skill | Invocations | Avg Time Saved | Accuracy | Satisfaction |
|-------|-------------|----------------|----------|--------------|
| test-failure-analysis | 45 | 38 min | 85% | ⭐⭐⭐⭐ |
| dod-verification | 18 | 27 min | 92% | ⭐⭐⭐⭐⭐ |
| git-workflow-automation | 22 | 9 min | 98% | ⭐⭐⭐⭐⭐ |
| roadmap-health-check | 8 | 22 min | 88% | ⭐⭐⭐⭐ |
| pr-monitoring-analysis | 6 | 14 min | 90% | ⭐⭐⭐⭐ |
| legacy-code-analysis | 2 | -4 min (slower!) | 60% | ⭐⭐ |

**Observations**:
- Git-workflow-automation: Highest satisfaction (98% accuracy, fast)
- test-failure-analysis: High usage but accuracy needs improvement
- legacy-code-analysis: Negative time savings, low satisfaction → deprecate

### Bottleneck Trends

**Top 3 Time Wasters** (hours/month):
1. Context budget management (CFR-007): 26.7-40 hours
2. Spec creation: 23-30.7 hours
3. Manual dependency analysis: 3.3-5 hours

**Total**: 53-75.7 hours/month wasted on automatable tasks

---

## Implementation Roadmap

Based on curator analysis, recommended implementation priority:

**Phase 1** (Weeks 1-3): CRITICAL skills
- context-budget-optimizer (12 hours effort, 26.7-40 hrs/month saved)
- spec-creation-automation (10 hours effort, 23-30.7 hrs/month saved)

**Phase 2** (Weeks 4-6): HIGH impact skills
- dependency-conflict-resolver (8 hours effort, 3.3-5 hrs/month saved)
- async-workflow-coordinator (10 hours effort, 5-10 hrs/month saved)

**Phase 3** (Week 7): Improvements
- Modify test-failure-analysis (2 hours effort, +7% accuracy)
- Deprecate legacy-code-analysis (1 hour effort, cleanup)

**Total**: 43 hours effort, 58-86 hours/month savings = 13-24x ROI in Year 1
```

---

## Benefits of Curator-Driven Skill Evolution

### 1. **Data-Driven Decisions**
- Skills based on observed patterns, not hunches
- Quantified impact (time savings, frequency, confidence)
- Evidence-based prioritization

### 2. **Continuous Improvement**
- Feedback loop: Create → Measure → Refine → Improve
- Skills evolve based on actual usage data
- Low-performing skills identified and fixed/deprecated

### 3. **Proactive Bottleneck Detection**
- Curator identifies inefficiencies before they become critical
- Early warning system for emerging patterns
- Strategic skill planning (roadmap of skills to create)

### 4. **Objective ROI Analysis**
- Curator calculates expected savings vs implementation effort
- Tracks actual savings post-implementation
- Validates skill value with real data

### 5. **Agent Learning**
- Playbooks capture best practices
- New agents learn from curator's accumulated knowledge
- Skill usage patterns shared across agent types

---

## Measurement & Success Criteria

### Curator Effectiveness Metrics

**1. Skill Recommendation Accuracy**
- **Goal**: 90%+ of curator-recommended skills show positive ROI
- **Measure**: (Skills with ROI >1) / (Total recommended skills)
- **Current**: TBD (track post-implementation)

**2. Bottleneck Detection Speed**
- **Goal**: Identify bottlenecks within 2 weeks of emergence
- **Measure**: Time from "pattern appears" to "curator recommends skill"
- **Current**: TBD (track detection latency)

**3. Skill Adoption Rate**
- **Goal**: 80%+ of high-priority curator-recommended skills implemented within 3 months
- **Measure**: (Skills implemented) / (Skills recommended as HIGH priority)
- **Current**: TBD (track implementation rate)

**4. Time Savings Validation**
- **Goal**: Actual savings ≥ 80% of curator-estimated savings
- **Measure**: Compare curator estimate vs actual measured savings
- **Current**: TBD (track post-implementation)

---

## Integration Examples

### Example 1: Curator Identifies Spec Creation Bottleneck

```
1. Generator observes (over 6 weeks):
   - 23 spec creations by architect
   - Average time: 117 minutes
   - Consistent steps: code search (20 min), template fill (15 min), dependency analysis (25 min)

2. Reflector analyzes:
   - Creates delta item: "BOTTLENECK: Spec creation - code search repetitive (20 min avg)"
   - Creates delta item: "PATTERN: Template population manual (15 min avg)"
   - Creates delta item: "OPPORTUNITY: Dependency analysis automatable (25 min avg)"

3. Curator synthesizes:
   - Combines 3 delta items into playbook entry
   - Recommends: "Create spec-creation-automation skill"
   - Calculates: 20+15+25 = 60 min automatable (out of 117 min total) = 51% reduction
   - Adjusts for skill overhead: 117 min → 25 min (78% reduction realistic)
   - Priority: HIGH (23 specs/month × 92 min saved = 35 hours/month)

4. project_manager reads playbook:
   - Identifies top recommendation
   - Collaborates with architect to create SPEC-061
   - Proposes to user for approval

5. User approves → code_developer implements → Generator measures impact
```

---

## Related Guidelines

- **GUIDELINE-001**: Error Handling Patterns (curator tracks error handling inefficiencies)
- **GUIDELINE-002**: Logging Best Practices (curator identifies logging bottlenecks)
- **GUIDELINE-004**: Git Tagging (curator tracks git workflow efficiency)
- **GUIDELINE-005**: Testing Strategies (curator analyzes test creation time)

---

## Conclusion

The **ACE curator is the intelligence** behind skill evolution. By continuously observing agent behavior, identifying patterns, and recommending improvements, the curator ensures the skill system evolves to meet actual agent needs - not just hypothetical use cases.

**Key Principle**: **"Observe, Reflect, Curate, Improve"** - The curator closes the loop between agent execution and system evolution.

---

**Created**: 2025-10-18
**Author**: architect
**Status**: Active
**Next Review**: 2025-11-18 (30 days) - Validate curator-driven skill evolution effectiveness
