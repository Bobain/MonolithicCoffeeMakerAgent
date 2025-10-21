# ACE Streamlit App - Testing Checklist

## Purpose

This checklist ensures the ACE Streamlit App is production-ready before release. Complete all sections and mark items as you test them.

**Tester**: _________________
**Date**: _________________
**Version**: 1.0.0 (Phase 5)
**Environment**: Local Development / Staging / Production *(circle one)*

---

## Pre-Launch Checks

- [ ] All dependencies installed (`poetry install`)
- [ ] No pending git changes in critical files
- [ ] `.env` file configured (if applicable)
- [ ] Python version: 3.11+ (`python --version`)
- [ ] Port 8501 available

---

## Application Startup

- [ ] App starts without errors (`poetry run ace-ui`)
- [ ] Browser opens automatically
- [ ] URL correct: `http://localhost:8501`
- [ ] No console errors in terminal
- [ ] Streamlit version displayed correctly

---

## Page Loading

### Home Page

- [ ] Home page loads in <2 seconds
- [ ] Title displayed: "ACE Framework Dashboard"
- [ ] Subtitle displayed correctly
- [ ] Custom CSS applied (check gradient header)
- [ ] Quick Status metrics visible
- [ ] All 3 metrics show data (Active Agents, Traces Today, Success Rate)
- [ ] Info box with navigation links present
- [ ] "About ACE" section displayed
- [ ] No error messages

### Monitor Page

- [ ] Monitor page loads from sidebar navigation
- [ ] Page header displays with icon (📊)
- [ ] Custom CSS applied
- [ ] Filters section visible (Agent, Time Range, Auto-refresh)
- [ ] All agent options in dropdown
- [ ] Time range options: 1h, 6h, 24h, 7d
- [ ] Auto-refresh checkbox works
- [ ] Loading spinner shows while fetching traces
- [ ] No error messages on load

### Playbooks Page

- [ ] Playbooks page loads from sidebar navigation
- [ ] Page header displays with icon (📚)
- [ ] Custom CSS applied
- [ ] Agent selector dropdown visible
- [ ] Quick Stats displayed (Total Bullets, Avg Effectiveness, Active, Pending)
- [ ] Filters & Search section visible
- [ ] Loading spinner shows while fetching playbook
- [ ] No error messages on load

### Analytics Page

- [ ] Analytics page loads from sidebar navigation
- [ ] Page header displays with icon (📈)
- [ ] Custom CSS applied
- [ ] Sidebar settings visible (Time Range slider, Agent filter)
- [ ] Loading spinner shows while fetching analytics (may take >5s)
- [ ] No error messages on load

---

## Functional Testing

### Home Page Functionality

- [ ] Quick Status metrics update correctly
- [ ] Metrics show realistic values (not hardcoded mocks)
- [ ] Delta indicators display (percentage or count changes)
- [ ] Sidebar navigation works from Home page

### Monitor Page Functionality

#### Filters

- [ ] Agent filter changes trace display
- [ ] Time range filter updates trace count
- [ ] "All" agent option shows traces from all agents
- [ ] Auto-refresh checkbox enables/disables refresh
- [ ] Auto-refresh actually refreshes page every 5 seconds
- [ ] Refresh indication displayed when auto-refresh enabled

#### Quick Stats

- [ ] Total Traces count accurate
- [ ] Success count accurate
- [ ] Failure count accurate
- [ ] Avg Duration calculated correctly

#### Live Trace Feed

- [ ] Traces display in list format
- [ ] Trace cards show agent name, timestamp, duration
- [ ] Status indicators work:
  - [ ] ✅ Success = green
  - [ ] ❌ Failure = red
  - [ ] ⚠️ Unknown = gray
- [ ] "View Details" expander works
- [ ] Trace JSON displayed when expanded
- [ ] Traces limited to 50 for performance
- [ ] Empty state displayed when no traces ("No traces found")
- [ ] Empty state has helpful suggestion

#### Agent Performance Dashboard

- [ ] Agent performance section displayed
- [ ] Agents sorted by total traces (descending)
- [ ] Success rate progress bar displays
- [ ] Progress bar color matches rate (green ≥90%, orange ≥70%, red <70%)
- [ ] Metrics show: traces, success/failure counts, avg duration
- [ ] Trend indicator matches success rate

### Playbooks Page Functionality

#### Agent Selection

- [ ] Agent dropdown lists all agents
- [ ] Selecting agent loads corresponding playbook
- [ ] Loading spinner shows during playbook load

#### Quick Stats

- [ ] Total Bullets count accurate
- [ ] Avg Effectiveness calculated correctly
- [ ] Active count accurate
- [ ] Pending Review count accurate

#### Filters & Search

- [ ] Category filter dropdown populated
- [ ] "All" category shows all bullets
- [ ] Specific category filters correctly
- [ ] Status filter works (All, active, pending, archived)
- [ ] Effectiveness slider filters correctly (min/max range)
- [ ] Search box filters bullets by content
- [ ] Sort options work:
  - [ ] Effectiveness (High to Low)
  - [ ] Effectiveness (Low to High)
  - [ ] Date Added (Newest)
  - [ ] Date Added (Oldest)

#### Bullet Display

- [ ] Filtered bullet count displayed
- [ ] Bullets displayed in expanders
- [ ] Effectiveness color coding correct:
  - [ ] 🟢 Green (≥0.7)
  - [ ] 🟡 Yellow (0.3-0.7)
  - [ ] 🔴 Red (<0.3)
- [ ] Status badges display:
  - [ ] ✅ Active
  - [ ] ⏳ Pending
  - [ ] 🗄️ Archived
- [ ] Bullet content displayed (truncated to 80 chars in preview)
- [ ] Expanding bullet shows full content
- [ ] Metadata displayed (category, effectiveness, usage count, added date, status)

#### Pagination

- [ ] Pagination controls visible (when >20 bullets)
- [ ] "Previous" button works
- [ ] "Next" button works
- [ ] Current page displayed
- [ ] Total pages calculated correctly
- [ ] "Previous" disabled on page 1
- [ ] "Next" disabled on last page

#### Bullet Actions

- [ ] "Approve" button visible for non-active bullets
- [ ] "Reject" button visible for non-archived bullets
- [ ] Approve action works (bullet status changes)
- [ ] Reject action works (bullet status changes)
- [ ] Success message displayed after action
- [ ] Page refreshes after action
- [ ] Bullet ID displayed in actions section

#### Bulk Actions

- [ ] "Enable bulk actions" checkbox works
- [ ] Bulk mode info displayed
- [ ] Selection checkboxes appear on bullets
- [ ] Multiple bullets can be selected
- [ ] "Bulk Approve Selected" button visible
- [ ] "Bulk Reject Selected" button visible
- [ ] Bulk approve works (multiple bullets approved)
- [ ] Bulk reject works (multiple bullets rejected)
- [ ] Success message shows count (e.g., "Approved 5 bullets, 0 failed")
- [ ] Warning shown if no bullets selected

#### Visualizations

- [ ] **Category Distribution** tab loads
- [ ] Pie chart renders with correct data
- [ ] Chart shows all categories
- [ ] Hover shows percentage
- [ ] **Effectiveness Distribution** tab loads
- [ ] Histogram renders with correct bins
- [ ] Threshold lines shown (0.7 green, 0.3 orange)
- [ ] Effectiveness stats displayed (High, Medium, Low counts)
- [ ] **Status Breakdown** tab loads
- [ ] Bar chart renders (active, pending, archived)
- [ ] Colors match status (green, orange, gray)

#### Curation Queue

- [ ] Curation Queue section displayed
- [ ] Pending bullets count accurate
- [ ] "No bullets pending" message when queue empty
- [ ] First 10 pending bullets shown
- [ ] Quick Approve/Reject buttons work
- [ ] Success message after quick action
- [ ] Page refreshes after action
- [ ] "Showing 10 of X" message when >10 pending

#### Help Section

- [ ] "About Playbook Management" expander present
- [ ] Help text comprehensive
- [ ] Formatting correct (markdown)

### Analytics Page Functionality

#### Settings

- [ ] Time range slider works (7-90 days)
- [ ] Agent filter dropdown works
- [ ] "All Agents" option shows all data
- [ ] Specific agent filter works
- [ ] Settings info displayed

#### Executive Summary

- [ ] Total Traces metric displayed
- [ ] Total Cost metric displayed
- [ ] Avg Effectiveness metric displayed
- [ ] Top Agent metric displayed
- [ ] Metrics formatted correctly (commas, currency, percentage)
- [ ] Help tooltips show on hover
- [ ] Key Insights section displayed (if available)
- [ ] Insights alternate between info (💡) and success (✨) styling

#### Cost Analytics

- [ ] Cost Analytics section loads
- [ ] Total Cost metric displayed
- [ ] Avg Cost/Trace metric displayed
- [ ] Most Expensive agent displayed
- [ ] Trend indicator shown
- [ ] **Cost by Agent** pie chart renders
- [ ] Chart shows percentages and labels
- [ ] **Daily Cost Trend** line chart renders
- [ ] Chart has markers and hover data
- [ ] Empty state shown when no cost data

#### Effectiveness Analytics

- [ ] Effectiveness section loads
- [ ] Success Rate metric displayed
- [ ] Error Rate metric displayed
- [ ] Avg Effectiveness metric displayed
- [ ] Problem Areas count displayed
- [ ] **Success vs Error Rate** bar chart renders
- [ ] Chart colors correct (green for success, red for error)
- [ ] **Effectiveness by Agent** horizontal bar chart renders
- [ ] Chart colored by effectiveness (red-yellow-green scale)
- [ ] **Effectiveness Trend Over Time** line chart renders (if data available)
- [ ] Target line shown at 80%
- [ ] Problem areas listed (if any)
- [ ] Empty state shown when no effectiveness data

#### Performance Analytics

- [ ] Performance section loads
- [ ] Avg Duration metric displayed
- [ ] Avg Tokens metric displayed
- [ ] Optimization Opportunities count displayed
- [ ] **Avg Duration by Agent** bar chart renders
- [ ] Chart colored by duration (red scale)
- [ ] **Avg Tokens by Agent** bar chart renders
- [ ] Chart colored by tokens (blue scale)
- [ ] **Slowest Operations** table displayed (if data available)
- [ ] Table shows agent, task, duration columns
- [ ] Optimization opportunities listed (if any)
- [ ] Empty state shown when no performance data

#### Recommendations

- [ ] Recommendations section displayed
- [ ] Recommendations numbered
- [ ] Recommendations actionable
- [ ] "System operating optimally" message when no recommendations

#### Advanced Analytics (Expander)

- [ ] "Advanced Analytics" expander present
- [ ] **Cost vs Effectiveness Scatter Plot** renders
- [ ] Scatter plot shows agent labels
- [ ] Quadrant lines displayed (average cost, average effectiveness)
- [ ] Quadrant analysis text displayed
- [ ] Colors match effectiveness (red-yellow-green)
- [ ] **Agent Performance Heatmap** renders
- [ ] Heatmap shows normalized scores (0-1)
- [ ] Metrics displayed: Cost, Effectiveness, Duration
- [ ] Color scale correct (red-yellow-green)
- [ ] Hover shows agent, metric, score
- [ ] Heatmap info text displayed

---

## Error Handling

### Expected Errors

- [ ] No traces → Empty state with suggestion (Monitor)
- [ ] No bullets match filters → Empty state with suggestion (Playbooks)
- [ ] No cost data → Info message (Analytics)
- [ ] No effectiveness data → Info message (Analytics)
- [ ] No performance data → Info message (Analytics)

### Error Messages

- [ ] Failed to load status → Error message with details (Home)
- [ ] Failed to load traces → Error message with details (Monitor)
- [ ] Failed to load playbook → Error message with details (Playbooks)
- [ ] Failed to load analytics → Error message with details (Analytics)
- [ ] API errors show user-friendly messages
- [ ] Error messages styled correctly (red, with icon)

---

## Performance

- [ ] Home page loads in <2 seconds
- [ ] Monitor page loads in <3 seconds
- [ ] Playbooks page loads in <10 seconds (150+ bullets)
- [ ] Analytics page loads in <10 seconds (90 days, all agents)
- [ ] Charts render smoothly (no lag)
- [ ] Auto-refresh doesn't slow down UI
- [ ] Pagination doesn't cause lag
- [ ] Bulk actions complete in <5 seconds (for 10-20 bullets)

---

## Responsive Design

### Desktop (1920x1080)

- [ ] All pages display correctly
- [ ] Charts use full width
- [ ] Metrics fit in columns
- [ ] No horizontal scrolling

### Laptop (1366x768)

- [ ] All pages display correctly
- [ ] Charts resize appropriately
- [ ] Metrics fit in columns
- [ ] Sidebar works correctly

### Tablet (768x1024)

- [ ] All pages accessible
- [ ] Charts visible (may be smaller)
- [ ] Metrics stack vertically if needed
- [ ] Sidebar collapsible

### Mobile (375x667)

- [ ] Pages load (basic functionality)
- [ ] Navigation works
- [ ] Critical info visible
- [ ] Charts may not be interactive (acceptable)

---

## Cross-Browser Testing

### Chrome (Latest)

- [ ] All pages load
- [ ] Charts render
- [ ] Interactions work
- [ ] No console errors

### Firefox (Latest)

- [ ] All pages load
- [ ] Charts render
- [ ] Interactions work
- [ ] No console errors

### Safari (Latest)

- [ ] All pages load
- [ ] Charts render
- [ ] Interactions work
- [ ] No console errors

### Edge (Latest)

- [ ] All pages load
- [ ] Charts render
- [ ] Interactions work
- [ ] No console errors

---

## Security & Data Validation

- [ ] No sensitive data exposed in traces (check for API keys, passwords)
- [ ] No PII (Personal Identifiable Information) in traces
- [ ] File paths don't expose internal system structure
- [ ] Error messages don't leak stack traces to users
- [ ] API calls validate input parameters
- [ ] SQL injection not possible (N/A - no SQL)
- [ ] XSS (Cross-Site Scripting) not possible (Streamlit handles this)

---

## Accessibility

- [ ] All interactive elements keyboard-accessible
- [ ] Tab order logical
- [ ] Focus indicators visible
- [ ] Alt text on charts (Plotly default)
- [ ] Contrast ratios acceptable (WCAG AA)
- [ ] Screen reader compatible (basic support)

---

## Documentation

- [ ] User Guide complete (`docs/ACE_STREAMLIT_USER_GUIDE.md`)
- [ ] README updated with ACE UI section
- [ ] Technical Spec updated (`docs/STREAMLIT_ACE_APP_SPEC.md`)
- [ ] All screenshots referenced (even if placeholder)
- [ ] FAQ section comprehensive
- [ ] Troubleshooting section helpful

---

## Final Checks

- [ ] No TODO comments in code
- [ ] No debug print statements
- [ ] No hardcoded mock data (except fallbacks)
- [ ] All imports used (no unused imports)
- [ ] Code formatted with Black
- [ ] Type hints present (where applicable)
- [ ] Docstrings complete
- [ ] Pre-commit hooks pass

---

## Sign-Off

### Testing Complete

- [ ] All sections above completed
- [ ] Critical issues resolved
- [ ] Minor issues documented
- [ ] App ready for production

### Tester Signature

**Name**: _________________
**Date**: _________________

### Reviewer Signature (if applicable)

**Name**: _________________
**Date**: _________________

---

## Notes & Issues Found

*(Use this section to document any issues discovered during testing)*

**Issue 1**:
- **Severity**: Critical / High / Medium / Low
- **Description**:
- **Steps to Reproduce**:
- **Status**: Open / Fixed / Won't Fix

**Issue 2**:
- **Severity**: Critical / High / Medium / Low
- **Description**:
- **Steps to Reproduce**:
- **Status**: Open / Fixed / Won't Fix

*(Add more as needed)*

---

**End of Checklist**
