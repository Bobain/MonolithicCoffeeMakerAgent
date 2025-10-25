# CFR Template

Use this template when creating new CFRs.

## CFR-{NUMBER}: {TITLE}

**Rule**: {Single sentence rule statement}

**Core Principle**:
```
✅ ALLOWED: {What's allowed - action 1}
✅ ALLOWED: {What's allowed - action 2}

❌ FORBIDDEN: {What's forbidden - action 1}
❌ FORBIDDEN: {What's forbidden - action 2}
```

**Why This Is Critical**:

1. **{Reason 1 Title}**: {Detailed explanation of why this matters}
2. **{Reason 2 Title}**: {Detailed explanation}
3. **{Reason 3 Title}**: {Detailed explanation}
4. **{Reason 4 Title}**: {Detailed explanation (optional)}

**Real-World Problem This Solves**:

```
BEFORE CFR-{NUMBER} (chaotic):
- {Problem scenario line 1}
- {Problem scenario line 2}
- {Problem scenario line 3}
→ Result: {Negative outcome 1}
→ Result: {Negative outcome 2}
→ Result: {Negative outcome 3}

AFTER CFR-{NUMBER} (clean):
- {Solution scenario line 1}
- {Solution scenario line 2}
- {Solution scenario line 3}
→ Result: {Positive outcome 1}
→ Result: {Positive outcome 2}
→ Result: {Positive outcome 3}
```

### Enforcement

**{Enforcement Mechanism Title}**:

```{language}
{Code example showing enforcement}
```

**{Another Enforcement Mechanism}**:

{Description of enforcement}

### Acceptance Criteria

1. ✅ {Criterion 1}
2. ✅ {Criterion 2}
3. ✅ {Criterion 3}
4. ✅ {Criterion 4}
5. ✅ {Criterion 5}

### Exceptions

{Are there any exceptions? If yes, list them. If no, state "NONE"}

### Relationship to Other CFRs

**CFR-000**: {How this CFR relates to CFR-000}
**CFR-{OTHER}**: {How this CFR relates to another CFR}

### Success Metrics

- **{Metric 1 Name}**: {How to measure}
- **{Metric 2 Name}**: {How to measure}
- **{Metric 3 Name}**: {How to measure}

**Enforcement**: {code-level | process-level | design-level}
**Monitoring**: {How this CFR is monitored}
**User Story**: {Related user story, e.g., US-XXX}
**Related Spec**: {Related technical spec, e.g., SPEC-XXX (optional)}

---

## Example: CFR-014 Structure

See CFR-014 (All Orchestrator Activities Must Be Traced in Database) for a comprehensive example that includes:

- Clear rule statement
- Core principles with allowed/forbidden actions
- 6 detailed reasons why it's critical
- Before/after scenario showing real problem solved
- Comprehensive enforcement with code examples and database schema
- 10 acceptance criteria
- Clear exceptions
- Relationships to other CFRs
- Measurable success metrics
- Related US and spec

Key elements that made CFR-014 effective:

1. **Specificity**: Not "improve observability" but "ALL activities in database, JSON forbidden"
2. **Real Problem**: Actual bug (706 line JSON with 64 dead agents) that motivated the CFR
3. **Enforcement**: Concrete schema, code examples, migration path
4. **Metrics**: Specific measures (accuracy, query <100ms, 30+ days retention)
5. **Before/After**: Clear contrast showing chaos → order

Use this structure for all new CFRs to ensure consistency and effectiveness.
