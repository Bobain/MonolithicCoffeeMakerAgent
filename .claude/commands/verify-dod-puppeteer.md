# Definition of Done Verification with Puppeteer

Verify Definition of Done for **$PRIORITY_NAME: $PRIORITY_TITLE**

## Acceptance Criteria to Verify

$ACCEPTANCE_CRITERIA

## Testing Instructions

Use Puppeteer MCP tools to thoroughly verify each criterion:

### Step 1: Navigate to Application
```
Navigate to $APP_URL using puppeteer_navigate
Wait 3-5 seconds for page to fully load
```

### Step 2: Initial Page Load Check
- Verify page loads without errors
- Check for JavaScript console errors using puppeteer_evaluate
- Take initial screenshot: `dod_initial_$PRIORITY_NAME.png`

### Step 3: Verify Each Acceptance Criterion

For each criterion listed above:
1. **Visual Check**: Verify the UI element or feature exists
2. **Functional Check**: Test that it works correctly (click, fill, submit, etc.)
3. **Evidence**: Take a screenshot showing the criterion is met
4. **Notes**: Document any issues or observations

### Step 4: Comprehensive Testing

Use all available Puppeteer tools:
- `puppeteer_navigate` - Navigate to pages
- `puppeteer_screenshot` - Capture evidence
- `puppeteer_click` - Test interactive elements
- `puppeteer_fill` - Test input fields
- `puppeteer_select` - Test dropdowns
- `puppeteer_hover` - Test hover states
- `puppeteer_evaluate` - Check JavaScript console, run validation code

### Step 5: Generate Report

## DoD Verification Report

### Summary
[✅ PASSED or ❌ FAILED] - X/Y criteria met

### Priority Information
- **Priority**: $PRIORITY_NAME
- **Title**: $PRIORITY_TITLE
- **App URL**: $APP_URL
- **Verification Date**: [Current date/time]

### Detailed Results

#### Criterion 1: [Name]
- **Status**: ✅ PASSED or ❌ FAILED
- **Evidence**: [Screenshot filename]
- **Testing Method**: [What you tested and how]
- **Notes**: [Observations, issues, or recommendations]

#### Criterion 2: [Name]
- **Status**: ✅ PASSED or ❌ FAILED
- **Evidence**: [Screenshot filename]
- **Testing Method**: [What you tested and how]
- **Notes**: [Observations, issues, or recommendations]

[Continue for all criteria...]

### Screenshots Captured
- `dod_initial_$PRIORITY_NAME.png` - Initial page load
- `dod_criterion_1_$PRIORITY_NAME.png` - Evidence for criterion 1
- `dod_criterion_2_$PRIORITY_NAME.png` - Evidence for criterion 2
- [Additional screenshots as needed]

### Console Errors
[List any JavaScript errors found, or "None detected"]

### Performance Observations
- Page load time: [X seconds]
- Responsiveness: [Good/Fair/Poor]
- Visual rendering: [Any issues or notes]

### Final Recommendation

**Definition of Done Status**: [MET or NOT MET]

**Justification**: [Clear explanation of why DoD is met or not met based on evidence]

**Next Steps** (if failed):
1. [Specific action needed]
2. [Specific action needed]
3. [Specific action needed]

**Approval**: [Ready for merge/deploy if all criteria passed]

---

## Important Notes

- Be **thorough and objective** - test everything systematically
- Provide **clear evidence** for each criterion (screenshots, console logs, etc.)
- Document **any anomalies** even if they don't cause failure
- If a criterion is **ambiguous**, interpret it reasonably and note your interpretation
- If you **cannot verify** a criterion with Puppeteer, note this and explain why
- Take **enough screenshots** to prove all criteria are met

Your verification will be used to decide whether this priority can be:
- ✅ Marked as complete in ROADMAP
- ✅ Merged to main branch
- ✅ Deployed to production

Be as rigorous as a QA engineer!
