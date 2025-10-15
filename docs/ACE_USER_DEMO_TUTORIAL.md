# ACE Framework Complete User Demo Tutorial

**Complete Implementation of Agentic Context Engineering with Sentiment Analysis**

## Overview

This tutorial demonstrates the complete ACE (Agentic Context Engineering) framework with all capabilities including:

- **Implicit Sentiment Analysis**: Detects frustration, satisfaction, confusion from user messages
- **Explicit Satisfaction Ratings**: User provides 1-5 ratings on completed work
- **Automatic Insight Extraction**: Reflector analyzes traces and identifies patterns
- **Playbook Evolution**: Curator consolidates insights into actionable knowledge
- **End-to-End Learning Loop**: System improves autonomously from user feedback

## Prerequisites

- MonolithicCoffeeMakerAgent installed and configured
- Python 3.9+ environment
- Poetry dependency manager
- (Optional) OpenAI API key for embeddings in semantic de-duplication

## Architecture Quick Reference

```
User Message
    ↓
user_listener (detects sentiment)
    ↓
Delegation to agent (code_developer, project_manager, etc.)
    ↓
Execution Trace (with sentiment data)
    ↓
Reflector (extracts insights)
    ↓
Curator (updates playbook)
    ↓
Playbook (guides future executions)
```

## Part 1: Setup

### 1.1 Enable ACE for user_listener

```bash
# Set environment variable
export ACE_ENABLED_USER_LISTENER=true

# Add to .env file for persistence
echo "ACE_ENABLED_USER_LISTENER=true" >> .env
```

### 1.2 Verify ACE Directories

ACE creates these directories automatically:

```
docs/
├── generator/
│   └── traces/          # Execution traces by date
│       └── 2025-10-15/
│           ├── trace_1729012345.json
│           └── trace_1729012346.json
├── reflector/
│   └── deltas/          # Extracted insights by date
│       └── 2025-10-15/
│           └── deltas_1729012345.json
└── curator/
    └── playbooks/       # Evolved playbooks
        ├── user_listener_playbook.json
        └── code_developer_playbook.json
```

### 1.3 Start user_listener

```bash
poetry run user-listener
```

You should see:

```
✅ ACE enabled for user_listener
   Playbook: docs/curator/playbooks/user_listener_playbook.json
   Sentiment analysis: enabled
```

## Part 2: Implicit Sentiment Analysis Demo

### Scenario 1: Frustration Detection

**User Input**:
```
> Ugh, this feature isn't working again
```

**System Response**:
```
[user_listener] Delegating to code_developer...
[code_developer] Investigating issue...

ACE Observation: 'Ugh, this feature isn't working again' → code_developer
  Sentiment detected: frustration (confidence=0.60, severity=4/5)
  Sentiment detected: annoyance_repetition (confidence=0.70, severity=3/5)
```

**What Happened**:
1. SentimentAnalyzer detected "Ugh" (frustration indicator)
2. SentimentAnalyzer detected "again" (repetition keyword)
3. Trace saved with `implicit_sentiment` data
4. Reflector will later extract this as a failure mode

### Scenario 2: Satisfaction Detection

**User Input**:
```
> Perfect! That's exactly what I needed, thank you
```

**System Response**:
```
[user_listener] Great! I'm glad that worked.

ACE Observation: 'Perfect! That's exactly what I needed' → code_developer
  Sentiment detected: satisfaction (confidence=0.85, severity=4/5)
```

**What Happened**:
1. Detected "Perfect", "exactly what I needed", "thank you"
2. High confidence satisfaction signal
3. Trace saved with positive sentiment
4. Reflector will extract this as a success pattern

### Scenario 3: Confusion Detection

**User Input**:
```
> I don't understand how to use this feature
```

**System Response**:
```
[user_listener] Let me provide clearer documentation...

ACE Observation: 'I don't understand how to use this feature' → assistant
  Sentiment detected: confusion (confidence=0.70, severity=2/5)
```

**What Happened**:
1. Detected "don't understand" pattern
2. Moderate confidence confusion signal
3. Reflector will identify need for better documentation

## Part 3: Explicit Satisfaction Ratings

### 3.1 Provide Feedback After Work Session

After code_developer completes a feature:

```bash
poetry run user-listener feedback --session-summary "Implemented authentication feature"
```

**Interactive Prompt**:
```
[user_listener] Collecting satisfaction feedback...

Please rate your satisfaction (1-5): 5

What worked well? (optional):
> The implementation was clean and well-tested

What could be improved? (optional):
> Documentation could be more detailed

[user_listener] ✅ Thank you! Your feedback (score: 5/5) has been recorded.
  What worked well: The implementation was clean and well-tested
  Could improve: Documentation could be more detailed

[reflector] This feedback will be analyzed during next curation to improve future performance.
```

### 3.2 Automatic Feedback Detection

You can also skip the interactive prompt by providing feedback in the delegation:

```python
from coffee_maker.cli.user_listener_ace import UserListenerACE

ace = UserListenerACE(enabled=True)
ace.observe_delegation(
    user_query="Implement authentication",
    intent="feature_implementation",
    delegated_to="code_developer",
    success=True,
    duration_seconds=45.2,
    user_message="Great work! This looks perfect"  # Sentiment detected automatically
)
```

## Part 4: Reflection and Curation

### 4.1 Trigger Manual Curation

```bash
poetry run user-listener curate user_listener
```

**Output**:
```
[reflector] Analyzing execution traces from last 24 hours...
[reflector] ✅ Extracted 12 insights from traces
  - 5 from satisfaction signals (2 explicit, 3 implicit)
  - 7 from pattern analysis

[curator] Consolidating deltas into playbook...
[curator] ✅ Playbook updated successfully!

[user_listener] Curation complete! Playbook has 47 bullets (effectiveness: 0.82)

💡 Tip: Use 'user-listener playbook user_listener' to view full playbook
```

### 4.2 View Evolved Playbook

```bash
poetry run user-listener playbook user_listener
```

**Output**:
```
╭─ ACE Playbook - user_listener ─╮
│                                  │
│ Version: 1.2                     │
│ Last updated: 2025-10-15T10:30   │
│ Total bullets: 47                │
│ Effectiveness score: 0.82        │
│                                  │
│ Health Metrics:                  │
│   Avg helpful count: 3.2         │
│   Effectiveness ratio: 0.85      │
│   Coverage score: 0.78           │
│   Stale bullets: 2               │
│                                  │
│ Categories:                      │
│                                  │
│   DELEGATION (12 active, 1 deprecated)
│     1. [5 helpful] When user shows frustration, escalate to project_manager...
│     2. [4 helpful] For implementation requests with positive sentiment...
│     3. [3 helpful] Confusion signals indicate need for clarification...
│     ... and 9 more
│                                  │
│   COMMUNICATION (8 active, 0 deprecated)
│     1. [6 helpful] Respond with empathy when frustration detected...
│     2. [5 helpful] Acknowledge satisfaction with brief confirmation...
│     ... and 6 more
│                                  │
│   FAILURE_MODES (5 active, 2 deprecated)
│     1. [MARKED HARMFUL] Delegating complex requests without context...
│     2. [MARKED HARMFUL] Ignoring repeated frustration signals...
│     ... and 3 more
│                                  │
╰──────────────────────────────────╯

💡 Tip: Use --category <name> to see full category details
   Available: delegation, communication, failure_modes, optimization
```

### 4.3 View Specific Category

```bash
poetry run user-listener playbook user_listener --category delegation
```

**Output**:
```
Category: delegation (12 bullets)

1. When user shows frustration (confidence > 0.7), escalate to project_manager
   for immediate review instead of proceeding with delegation.
   Helpful: 5 | Pruned: 0
   Evidence: 3 trace(s)

2. For implementation requests with high satisfaction signals, continue
   delegating to code_developer using current approach.
   Helpful: 4 | Pruned: 0
   Evidence: 4 trace(s)

3. Confusion signals (indicators: "don't understand", "unclear") indicate
   user needs clarification before delegation. Ask followup questions.
   Helpful: 3 | Pruned: 1
   Evidence: 2 trace(s)

... (9 more bullets)
```

## Part 5: Complete Workflow Examples

### Example 1: Frustration → Learning → Improvement

**Day 1 - User Experience**:
```
User: "Ugh, the daemon keeps crashing"
System: [Frustration detected, severity=4]
System: Delegates to code_developer
code_developer: Investigates and fixes crash
```

**Behind the Scenes**:
- Trace saved with frustration sentiment (confidence=0.80)
- Reflector extracts: "Daemon crashes cause high user frustration"
- Curator adds to playbook: "High-priority bugs require immediate escalation"

**Day 2 - After Learning**:
```
User: "The API isn't responding"
System: [Detects potential frustration context]
System: Immediately escalates to project_manager
project_manager: "I'll prioritize this. Investigating now..."
User: "Thanks!" [Satisfaction detected]
```

### Example 2: Success Pattern Reinforcement

**Multiple Sessions**:
```
Session 1:
User: "Implement feature X"
System: Delegates to code_developer
User: "Perfect! Well done" [Satisfaction=0.90]

Session 2:
User: "Add feature Y"
System: Delegates to code_developer (same pattern)
User: "Excellent work!" [Satisfaction=0.85]

Session 3:
User: "Create feature Z"
System: [Playbook says: This delegation pattern has 0.87 success rate]
System: Confidently delegates to code_developer
User: "Great!" [Satisfaction=0.88]
```

**Learning**:
- Reflector identifies delegation to code_developer for features → high satisfaction
- Curator adds bullet: "Feature implementation → code_developer is reliable pattern"
- Future delegations use this knowledge with high confidence

### Example 3: Confusion → Documentation Improvement

**Initial Confusion**:
```
User: "How do I use the dashboard?"
System: [Confusion detected]
System: Provides basic help
User: "Still don't understand" [Confusion repeated, severity=4]
```

**Reflection**:
- Reflector identifies: Dashboard usage causes confusion
- Insight type: missing_knowledge
- Recommendation: "Create dashboard user guide"

**After Improvement**:
```
User: "How do I use the dashboard?"
System: [Playbook suggests proactive documentation]
System: "I'll walk you through it with examples..."
User: "That's clear, thanks!" [Satisfaction detected]
```

## Part 6: Advanced Features

### 6.1 Satisfaction Propagation

When you provide satisfaction to user_listener, it propagates to all delegated agents:

```
user_listener (trace_123, satisfaction=4/5)
    ↓ delegates to
code_developer (trace_124)
    ↓ delegates to
assistant (trace_125)

All three traces receive satisfaction=4/5!
```

This ensures that real work quality feedback reaches the agents that performed it.

### 6.2 Semantic De-duplication

Curator uses semantic similarity to avoid duplicate insights:

```
Delta 1: "User frustration when authentication fails"
Delta 2: "Authentication failures cause user annoyance"

→ Curator detects similarity (0.95)
→ Merges into single bullet with combined evidence
```

### 6.3 Playbook Health Monitoring

```bash
poetry run user-listener playbook user_listener
```

Watch these metrics:
- **Effectiveness Ratio**: Helpful bullets / Total bullets (aim for > 0.80)
- **Coverage Score**: How well playbook covers different scenarios (aim for > 0.75)
- **Stale Bullets**: Bullets not used in 30 days (should be < 5% of total)

## Part 7: Verification and Testing

### 7.1 Verify Sentiment Detection

```python
from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
signals = analyzer.analyze("Ugh, this isn't working again")

for signal in signals:
    print(f"{signal.sentiment}: {signal.confidence:.2f} (severity={signal.severity})")
```

Expected output:
```
frustration: 0.60 (severity=4)
annoyance_repetition: 0.70 (severity=3)
```

### 7.2 Verify Trace Capture

```bash
# Check latest traces
ls -la docs/generator/traces/$(date +%Y-%m-%d)/

# View trace content
cat docs/generator/traces/$(date +%Y-%m-%d)/trace_*.json | jq '.user_satisfaction'
```

Expected output:
```json
{
  "implicit_sentiment": [
    {
      "sentiment": "frustration",
      "confidence": 0.6,
      "indicators": ["ugh", "not working"],
      "severity": 4
    }
  ],
  "timestamp": "2025-10-15T10:45:23.123456"
}
```

### 7.3 Verify Reflection

```bash
# Trigger reflection manually
poetry run user-listener curate user_listener

# Check delta files
ls -la docs/reflector/deltas/$(date +%Y-%m-%d)/

# View deltas
cat docs/reflector/deltas/$(date +%Y-%m-%d)/deltas_*.json | jq '.deltas[] | select(.insight_type == "failure_mode")'
```

## Part 8: Troubleshooting

### Problem: No Sentiment Detected

**Symptoms**: Traces don't have `implicit_sentiment` field

**Solutions**:
1. Verify ACE is enabled:
   ```bash
   echo $ACE_ENABLED_USER_LISTENER  # Should be "true"
   ```

2. Check user_listener logs:
   ```bash
   poetry run user-listener 2>&1 | grep "Sentiment detected"
   ```

3. Test sentiment analyzer directly:
   ```python
   from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer
   analyzer = SentimentAnalyzer()
   signals = analyzer.analyze("Ugh, broken")
   print(len(signals))  # Should be > 0
   ```

### Problem: No Deltas Generated

**Symptoms**: Reflector finds no insights

**Solutions**:
1. Verify traces exist:
   ```bash
   ls -R docs/generator/traces/
   ```

2. Check trace timestamps (must be within 24 hours):
   ```bash
   find docs/generator/traces/ -name "*.json" -mtime -1
   ```

3. Run reflector with debug logging:
   ```bash
   ACE_LOG_LEVEL=DEBUG poetry run user-listener curate user_listener
   ```

### Problem: Playbook Not Updating

**Symptoms**: Curation completes but playbook unchanged

**Solutions**:
1. Check delta files exist:
   ```bash
   ls -la docs/reflector/deltas/$(date +%Y-%m-%d)/
   ```

2. Verify curator is processing deltas:
   ```bash
   poetry run user-listener curate user_listener 2>&1 | grep "Consolidating"
   ```

3. Check playbook file permissions:
   ```bash
   ls -la docs/curator/playbooks/
   ```

## Part 9: Best Practices

### 9.1 Feedback Timing

- **Provide feedback immediately** after work completion for highest accuracy
- **Wait 30+ seconds** before rating to see full results
- **Use explicit ratings** (1-5) for major milestones
- **Let implicit sentiment** handle routine interactions

### 9.2 Sentiment Clarity

**Good Examples** (clear signals):
- ✅ "Ugh, this is broken again" (frustration)
- ✅ "Perfect! Exactly what I needed" (satisfaction)
- ✅ "I don't understand this" (confusion)

**Ambiguous Examples** (weak signals):
- ⚠️ "Okay" (neutral, no learning)
- ⚠️ "Fine I guess" (unclear sentiment)
- ⚠️ "Sure" (no emotional signal)

### 9.3 Curation Frequency

- **Daily**: For active development (lots of traces)
- **Weekly**: For maintenance mode (few traces)
- **After major changes**: To capture new patterns
- **Before important work**: To benefit from latest learning

### 9.4 Playbook Maintenance

- **Review stale bullets monthly**: Remove outdated knowledge
- **Merge similar bullets**: Avoid duplication
- **Monitor effectiveness**: Aim for > 0.80
- **Prune low-confidence bullets**: Remove confidence < 0.4

## Part 10: Expected Outcomes

After running the ACE framework for 1-2 weeks, you should see:

### Quantitative Improvements
- **Delegation accuracy**: 85% → 95%
- **User satisfaction**: 3.5/5 → 4.5/5
- **Response quality**: Measured by fewer followup questions
- **Playbook size**: ~50 bullets with 0.80+ effectiveness

### Qualitative Improvements
- Faster frustration detection and escalation
- Proactive clarification when confusion likely
- Reinforcement of successful patterns
- Automatic avoidance of failure modes

### Playbook Evolution
```
Week 1: 15 bullets (mostly generic)
Week 2: 35 bullets (specific patterns emerging)
Week 3: 50 bullets (mature playbook, high effectiveness)
Week 4: 55 bullets (incremental improvements, pruning stale content)
```

## Conclusion

The ACE framework creates a **self-improving system** that learns from both explicit satisfaction ratings and implicit sentiment signals. Over time, the playbooks accumulate knowledge that makes agents:

1. **More accurate** in delegation decisions
2. **More empathetic** in user communication
3. **More proactive** in preventing frustration
4. **More consistent** in delivering satisfaction

The system operates **autonomously** - just enable ACE and let it learn from your natural interactions!

---

**For More Information**:
- ACE Framework Paper: https://www.arxiv.org/abs/2510.04618
- Technical Spec: `docs/PRIORITY_6_ACE_INTEGRATION_TECHNICAL_SPEC.md`
- Implementation Guide: `docs/ACE_FRAMEWORK_GUIDE.md`
