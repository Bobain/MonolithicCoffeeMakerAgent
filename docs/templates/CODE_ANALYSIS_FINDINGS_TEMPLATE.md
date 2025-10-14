# [Analysis Type] - [Date]

**Conducted by**: code-searcher agent
**Date**: YYYY-MM-DD
**Scope**: [Brief description of analysis scope]
**Methodology**: [Standard/Chain of Draft]

---

## Executive Summary

[High-level overview of findings - 2-3 sentences]

**Key Metrics**:
- Total items analyzed: [number]
- Critical findings: [number]
- High-priority findings: [number]
- Medium-priority findings: [number]
- Low-priority findings: [number]

**Overall Assessment**: [CRITICAL/HIGH/MEDIUM/LOW risk/concern]

---

## Methodology

**Analysis Approach**:
1. [Step 1 - e.g., "Scanned all files in coffee_maker/ directory"]
2. [Step 2 - e.g., "Searched for specific patterns using Grep"]
3. [Step 3 - e.g., "Analyzed dependencies and relationships"]
4. [Step 4 - e.g., "Prioritized findings by severity and impact"]

**Tools Used**:
- Glob: [Pattern searches conducted]
- Grep: [Regular expressions used]
- Read: [Files examined in detail]
- [Other tools]

**Coverage**:
- Files analyzed: [number]
- Lines of code examined: [approximate count]
- Modules covered: [list major modules]

---

## Key Findings

### Finding 1: [Descriptive Title]

**Severity**: CRITICAL/HIGH/MEDIUM/LOW

**Location**:
- File: `path/to/file.py`
- Lines: 123-145
- Additional locations: [if applicable]

**Description**:
[What was found? Be specific and clear.]

**Impact**:
[Why does this matter? What are the consequences?]

**Evidence**:
```python
# Code snippet showing the issue
def example_function():
    # Problematic code here
    pass
```

**Recommendation**:
[What should be done to address this?]

**Priority**: [1-5, with 1 being highest]

**Estimated Effort**: [hours/days]

---

### Finding 2: [Descriptive Title]

[Repeat structure from Finding 1]

---

## Detailed Analysis

### Category 1: [e.g., Security Vulnerabilities]

[In-depth examination of all findings in this category]

#### Subcategory 1.1: [e.g., SQL Injection Risks]

**Locations Identified**:
1. `coffee_maker/database/queries.py:45-67` - Direct string concatenation in SQL
2. `coffee_maker/api/endpoints.py:123` - Unsanitized user input
3. [Additional locations]

**Pattern Analysis**:
[Common patterns observed across these findings]

**Root Cause**:
[Why is this happening? Architectural issue? Coding practice?]

**Recommended Solution**:
[High-level approach to fix all instances]

---

### Category 2: [e.g., Code Duplication]

[Repeat structure from Category 1]

---

## Implementation Plan

### Phase 1: Critical Fixes (Week 1)

**Priority**: Address all CRITICAL and HIGH severity findings

1. **Task 1.1**: [Specific task]
   - **Owner**: code_developer
   - **Effort**: [hours]
   - **Dependencies**: None
   - **Acceptance Criteria**:
     - [ ] [Criterion 1]
     - [ ] [Criterion 2]

2. **Task 1.2**: [Specific task]
   - [Same structure as Task 1.1]

---

### Phase 2: Medium Priority Improvements (Week 2-3)

[Same structure as Phase 1]

---

### Phase 3: Low Priority Enhancements (Week 4+)

[Same structure as Phase 1]

---

## Metrics and Quantitative Analysis

### Code Quality Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Duplication % | X% | <5% | -Y% |
| Avg. Function Length | X lines | <50 lines | -Y lines |
| Cyclomatic Complexity | X | <10 | -Y |
| Test Coverage | X% | >80% | +Y% |
| Security Score | X/100 | >90/100 | +Y |

### Dependency Analysis

**Critical Dependencies** (high impact if changed):
- `module.submodule` - Used by X files
- `other.module` - Used by Y files

**Circular Dependencies**: [Number found, list if any]

**Unused Dependencies**: [List if any]

---

## Risk Assessment

### High-Risk Areas

1. **Area**: [e.g., Authentication Module]
   - **Risk Level**: HIGH
   - **Reason**: [Why is this risky?]
   - **Mitigation**: [How to reduce risk?]

2. **Area**: [Another high-risk area]
   - [Same structure]

---

## Recommendations Summary

### Immediate Actions (This Week)

1. [Action 1]
2. [Action 2]
3. [Action 3]

### Short-Term Actions (This Month)

1. [Action 1]
2. [Action 2]

### Long-Term Actions (This Quarter)

1. [Action 1]
2. [Action 2]

---

## Appendix

### Appendix A: Complete File List

[List all files analyzed, if helpful]

### Appendix B: Patterns Detected

[Document common patterns found]

### Appendix C: Tools and Commands

```bash
# Example Grep commands used
grep -r "pattern" coffee_maker/

# Example Glob patterns
**/*.py
**/*_test.py
```

### Appendix D: References

- [Link to related technical spec, if any]
- [Link to coding standards]
- [External documentation]

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial analysis | code-searcher |
| YYYY-MM-DD | Updated with implementation progress | project_manager |

---

**Document Status**: [DRAFT/FINAL]
**Next Review Date**: YYYY-MM-DD
**Related Documents**:
- [Link to related analysis]
- [Link to implementation PR]
