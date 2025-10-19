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

### ✅ {Concept 3} Works
- {Specific validation point}
- {Specific validation point}

---

## How to Run

### 1. Install Dependencies (if any)

```bash
cd docs/architecture/pocs/POC-{number}-{feature-slug}/
pip install -r requirements.txt  # Only if requirements.txt exists
```

### 2. Run the POC

```bash
python {main_file}.py
```

**Expected Output**:
```
{Sample output showing POC works}
```

### 3. Run Tests

```bash
python test_poc.py
# OR
pytest test_poc.py
```

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
- `{ClassName}`: {Purpose}
- `{function_name}()`: {Purpose}

### {component2}.py
{Brief description of what this component does}

**Key Classes/Functions**:
- `{ClassName}`: {Purpose}

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
