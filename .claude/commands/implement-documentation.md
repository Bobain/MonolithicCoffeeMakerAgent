Read docs/ROADMAP.md and implement $PRIORITY_NAME: $PRIORITY_TITLE.

⚠️  THIS IS A DOCUMENTATION PRIORITY - You MUST CREATE FILES ⚠️

The ROADMAP lists specific deliverable files under "Deliverables" section.
Your task is to:
1. Identify all deliverable files mentioned in ROADMAP for this priority
2. CREATE each file with actual content (not placeholders)
3. Use real examples from the existing codebase
4. Test any commands/examples before documenting them

Instructions:
- CREATE all files listed in the Deliverables section
- Fill with real, specific content based on existing codebase
- Include actual commands, file paths, and examples
- Be concrete, not generic or abstract
- Test examples to ensure accuracy

After creating files:
- Update ROADMAP.md status to "✅ Complete"
- List all files created
- Commit your changes

## Visual Documentation with Puppeteer

For documentation involving web interfaces, dashboards, or UI guides:

**Use Puppeteer MCP** to capture visual documentation:
- Take screenshots of web applications
- Capture different states/views
- Document visual workflows
- Create step-by-step visual guides

**Available Tools**:
- `puppeteer_navigate` - Navigate to pages
- `puppeteer_screenshot` - Capture screenshots
- `puppeteer_click` - Navigate through UI
- `puppeteer_fill` - Show form interactions

**Example Usage**:
```
1. Navigate to http://localhost:8501 (Streamlit dashboard)
2. Take screenshot: "dashboard_main.png"
3. Click on different tabs to show features
4. Take screenshots: "dashboard_analytics.png", "dashboard_settings.png"
5. Include screenshots in documentation with captions
```

Use Puppeteer to create rich visual documentation whenever documenting web UIs!

## GitHub CLI (`gh`) for Documentation

Use `gh` to enhance documentation with GitHub links:

**Common Uses**:
- Link to relevant issues: `gh issue view <number>`
- Reference PRs in docs: `gh pr list`
- Include repository info: `gh repo view`
- Document GitHub workflows

**Example**:
```bash
# Get issue details for documentation
gh issue view 42 --json title,body,labels

# Include in docs:
# "This addresses issue #42: [Title from gh issue view]"
```

Priority details:
$PRIORITY_CONTENT

Begin implementation now - CREATE THE FILES.
