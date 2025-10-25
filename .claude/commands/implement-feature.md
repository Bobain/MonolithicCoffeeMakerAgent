Implement $PRIORITY_NAME: $PRIORITY_TITLE.

## Technical Specification

$SPEC_CONTENT

---

## CRITICAL: Follow the Technical Spec Above!

**The technical spec above was created by the architect** and contains:
- Complete architecture and design decisions
- Detailed implementation steps
- Testing strategy
- Definition of Done criteria
- Integration points with existing code

**You MUST**:
1. **Read the FULL spec above** carefully
2. **Follow the spec exactly** - it was designed by architect for optimal implementation
3. **Use the implementation steps** provided in the spec
4. **Verify all DoD criteria** before marking complete
5. **If spec is missing or wrong**: STOP and create notification for architect

**Why specs matter**:
- architect has reviewed FULL ROADMAP and designed for reuse
- Specs identify simplification opportunities you might miss
- Following spec ensures architectural consistency
- Specs target 2-4 day timelines (not weeks)

## Implementation Steps

1. **Update Status**: Mark priority as "🔄 In Progress" in ROADMAP.md
2. **Implement**: Follow spec's implementation plan exactly (see Technical Specification above)
3. **Test**: Add tests as specified in spec's testing strategy
4. **Document**: Update docs as specified in spec
5. **Verify DoD**: Use Puppeteer to verify Definition of Done (if web-based)
6. **Commit**: Commit with clear messages
7. **Complete**: Update ROADMAP.md to "✅ Complete"

## Important Guidelines

- Follow all coding standards
- Add tests where appropriate
- Document your changes
- Commit frequently with clear messages

## Puppeteer DoD Verification (For Web Features)

If this priority involves web applications, UI, or deployments:

**Use Puppeteer MCP** to verify Definition of Done:
- Navigate to the application URL
- Take screenshots showing features working
- Test interactive elements (click, fill, etc.)
- Check for console errors
- Verify all acceptance criteria are met

**Available Puppeteer Tools**:
- `puppeteer_navigate` - Navigate to pages
- `puppeteer_screenshot` - Capture evidence
- `puppeteer_click` - Test buttons/links
- `puppeteer_fill` - Test input fields
- `puppeteer_evaluate` - Check JavaScript console

**Example DoD Verification**:
```
1. Navigate to http://localhost:8501
2. Take screenshot: "feature_initial.png"
3. Test feature functionality with clicks/fills
4. Take screenshot: "feature_working.png"
5. Check console for errors using evaluate
6. Report: "✅ All acceptance criteria verified with Puppeteer"
```

ALWAYS verify DoD with Puppeteer for web-based features before marking complete!

## GitHub CLI (`gh`) Integration

Use `gh` command for GitHub-related tasks:

**Common Use Cases**:
- Link priority to GitHub issue: `gh issue view <number>`
- Create PR after implementation: `gh pr create --title "..." --body "..."`
- Check CI status: `gh pr checks`
- Reference existing issues/PRs in commit messages

**Example Workflow**:
```bash
# Check if there's a related GitHub issue
gh issue list --search "$PRIORITY_NAME"

# After implementation, create PR
gh pr create --title "Implement $PRIORITY_NAME: $PRIORITY_TITLE" \
  --body "Closes #<issue-number>\n\nImplementation details..."
```

Use `gh` to connect your work with GitHub issues and PRs!

## Priority Details

$PRIORITY_CONTENT

Begin implementation now.
