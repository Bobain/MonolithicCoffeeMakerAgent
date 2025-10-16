# Team Collaboration Guide

**MonolithicCoffeeMakerAgent Multi-Agent Collaboration**

This document defines how agents collaborate on the MonolithicCoffeeMakerAgent project.

---

## Agent Roles & Responsibilities

### User Interface

**user_listener**
- **ONLY agent with user interface**
- Interprets user intent
- Delegates to appropriate team members
- Synthesizes results for user
- All user interactions go through user_listener

### Strategic Planning

**project_manager**
- Strategic ROADMAP management
- Creates strategic specifications (docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md - WHAT and WHY)
- Does NOT create technical specifications (that's architect's job - HOW)
- Delegates technical design to architect when needed
- Monitors GitHub (PRs, issues, CI/CD)
- Post-completion DoD verification (when user requests)
- Receives bug reports from assistant
- Adds critical priorities to ROADMAP based on bug reports
- Warns users about blockers

### Architecture & Design

**architect**
- Architectural design BEFORE implementation
- Creates technical specifications:
  - General technical specs: docs/architecture/specs/SPEC-*.md
  - User story technical specs: docs/architecture/user_stories/US_*_TECHNICAL_SPEC.md
- Documents architectural decisions (ADRs in docs/architecture/decisions/)
- Provides implementation guidelines (docs/architecture/guidelines/)
- ONLY agent that manages dependencies (pyproject.toml, poetry.lock)
- Asks user for approval on important decisions (especially dependencies)
- Interacts with user through user_listener

**Key Distinction - Strategic vs Technical Specs**:
- **Strategic Specs** (project_manager): WHAT feature and WHY (business requirements)
  - Example: docs/roadmap/PRIORITY_*_STRATEGIC_SPEC.md (high-level strategic requirements)
  - Owned by: project_manager (strategic planning)
- **Technical Specs** (architect): HOW to implement technically (architecture, design, implementation details)
  - Example: docs/architecture/user_stories/US_*_TECHNICAL_SPEC.md (detailed technical design)
  - Owned by: architect (technical design)
  - Created by: architect based on project_manager's strategic requirements

### Documentation & Demos

**assistant**
- **Documentation Expert**: Profound knowledge of ALL project docs
- **Intelligent Dispatcher**: Routes requests to specialized agents
- **Demo Creator**: Creates visual demos using Puppeteer MCP (ONLY agent that creates demos)
- **Bug Reporter**: Tests features, detects bugs, analyzes them, reports to project_manager
- Handles quick questions directly
- Delegates complex tasks to specialists
- **READ-ONLY** for code/docs (never modifies implementation)
- **ACTIVE** for demo creation and bug reporting

### Implementation

**code_developer**
- Autonomous implementation from ROADMAP
- Writes/modifies ALL code (coffee_maker/, tests/, scripts/)
- Manages technical configurations (.claude/)
- Creates PRs autonomously
- Updates ROADMAP status (Planned → In Progress → Complete)
- DoD verification DURING implementation
- Does NOT monitor project health
- Does NOT make strategic decisions

### Specialized Analysis

**code-searcher**
- Deep codebase analysis
- Security audits
- Dependency tracing
- Refactoring opportunities
- Prepares findings → Reports to assistant → assistant delegates to project_manager
- **READ-ONLY** (never writes docs directly)

**ux-design-expert**
- UI/UX design guidance
- Tailwind CSS specifications
- Design decisions
- Provides specs (doesn't implement)

### ACE Framework (Agentic Context Engineering)

**generator**
- **Ownership Enforcement**: Central enforcement point for file ownership rules
- **Action Interception**: Intercepts ALL agent actions before execution
- **Auto-Delegation**: Automatically delegates file operations to correct owner when violations detected
- **Trace Capture**: Records execution traces for reflector analysis
- Orchestrates target agent execution
- Validates ownership before file operations (Edit, Write, NotebookEdit)
- Captures delegation traces when ownership violations occur
- Owns docs/generator/ for execution traces
- **NEVER modifies files directly** - Orchestrates other agents to do the work

**reflector**
- Insight extraction from execution traces
- Analyzes patterns and strategies
- Generates delta items for curator
- Owns docs/reflector/ for insights

**curator**
- Maintains evolving playbooks
- Semantic de-duplication of insights
- Playbook effectiveness tracking
- Owns docs/curator/ for playbooks

---

## Demo Creation & Bug Reporting Workflow

### Overview

```
User Request → user_listener → assistant (creates demo)
                                    ↓
                            Bug detected? YES
                                    ↓
                            assistant (analyzes bug)
                                    ↓
                            assistant → project_manager (reports bug)
                                    ↓
                            project_manager (adds critical priority to ROADMAP)
```

### Demo Creation Flow

#### Trigger Events

1. **User requests demo**
   - User to user_listener: "Show me how X works"
   - user_listener delegates to assistant

2. **Feature completion**
   - code_developer completes feature
   - user_listener asks assistant to create demo
   - Demo showcases new functionality

3. **Feature testing request**
   - User to user_listener: "Test feature Y"
   - user_listener delegates to assistant
   - assistant creates interactive test demo

#### Demo Creation Process

**assistant executes**:

1. **Navigate to Feature**
   ```
   Use Puppeteer MCP to access application
   Navigate to relevant pages/components
   ```

2. **Capture Interactions**
   ```
   Click buttons, fill forms, navigate workflows
   Take screenshots at each step
   Record interactions and behaviors
   ```

3. **Document Demo**
   ```
   Create step-by-step visual tutorial
   Annotate screenshots with explanations
   Highlight key features and functionality
   ```

4. **Test Functionality**
   ```
   Validate features work as expected
   Monitor console for errors
   Check visual appearance
   Test edge cases
   ```

5. **Deliver Demo**
   ```
   Present demo to user via user_listener
   Include screenshots and explanations
   Note any observations or concerns
   ```

### Bug Reporting Flow

#### When Bug Detected During Demo

**CRITICAL**: assistant must provide comprehensive bug reports with root cause analysis and requirements so architect and code_developer can fix the problem before assistant tries the demo again.

**assistant responsibilities**:

1. **Analyze Bug Comprehensively**
   ```
   What was expected behavior?
   What actually happened?
   ROOT CAUSE ANALYSIS: What went wrong technically?
     - Which component/function is failing?
     - Why is it failing?
     - What assumptions were violated?
     - Are there missing validations/checks?
   Steps to reproduce (exact sequence)
   Console errors, network issues, visual problems
   Screenshots/videos showing the problem
   Environment details (browser, version, OS)
   Impact assessment (which features affected)
   ```

2. **Document Findings Using Template**
   ```markdown
   ## Bug Report from assistant

   **Summary**: [One-line description]

   **Severity**: [Critical/High/Medium/Low]

   **Steps to Reproduce**:
   1. [Step 1 with specific details]
   2. [Step 2 with specific details]
   3. [Step 3 with specific details]

   **Expected Behavior**:
   [What should happen based on requirements]

   **Actual Behavior**:
   [What actually happens - be specific]

   **Root Cause Analysis**:
   [Technical analysis of what went wrong:
    - Which component/function is failing?
    - Why is it failing?
    - What assumptions were violated?
    - Are there missing validations/checks?]

   **Requirements for Fix**:
   - [Requirement 1: Specific change needed]
   - [Requirement 2: Specific change needed]
   - [Requirement 3: Dependencies or prerequisites]

   **Expected Behavior Once Corrected**:
   [Detailed description of how feature should work after fix:
    - User interactions that should work
    - Validations that should trigger
    - Error handling that should occur
    - Visual feedback that should appear]

   **Environment**:
   - Browser: [Chrome 120 / Firefox 115 / etc]
   - Version: [Application version]
   - OS: [macOS 14.4 / Windows 11 / etc]

   **Impact Assessment**:
   [Which features are affected:
    - Primary feature broken: [name]
    - Related features impacted: [list]
    - User impact: [severity description]
    - Business impact: [if applicable]]

   **Screenshots/Videos**:
   [Puppeteer screenshots showing:
    - Before action (initial state)
    - During action (problem occurring)
    - After action (failed state)
    - Console errors (if any)]
   ```

3. **Report to project_manager**
   ```
   "I found a bug during demo creation. Here's my comprehensive analysis:

   [Include full bug report template above]

   This provides all the information architect and code_developer need to:
   1. Understand the root cause
   2. Design the fix
   3. Implement the solution
   4. Verify the fix works

   **Recommendation**: Add critical priority to ROADMAP so the team can
   fix this before I retry the demo."
   ```

4. **project_manager Action**
   ```
   Receives comprehensive bug report from assistant
   Reviews severity, impact, and requirements
   Adds critical priority to ROADMAP with bug details
   Includes assistant's root cause analysis and requirements in priority description
   Tags architect and code_developer if urgent
   ```

5. **Fix & Verify Loop**
   ```
   architect designs fix based on assistant's analysis
   code_developer implements fix using architect's design and assistant's requirements
   assistant tries demo again to verify fix
   If still broken: assistant provides updated analysis
   Loop continues until demo passes
   ```

#### Severity Guidelines

**Critical**:
- Security vulnerabilities
- Data loss risks
- Complete feature failure
- Blocks other work

**High**:
- Major functionality broken
- Poor user experience
- Workaround exists but difficult

**Medium**:
- Minor functionality issues
- Visual inconsistencies
- Easy workaround available

**Low**:
- Cosmetic issues
- Edge cases
- Nice-to-have improvements

---

## Collaboration Examples

### Example 1: User Requests Demo

**Flow**:
```
User: "Show me the analytics dashboard"
    ↓
user_listener: "I'll have assistant create a demo for you"
    ↓
assistant:
  - Navigates to http://localhost:8501
  - Takes screenshots of dashboard
  - Tests interactive features
  - Creates visual tutorial
  - Reports back to user_listener
    ↓
user_listener: "Here's the demo [presents assistant's work]"
```

### Example 2: Feature Complete, Demo Requested

**Flow**:
```
code_developer: "Feature US-032 complete" (via status update)
    ↓
User to user_listener: "Can I see a demo of US-032?"
    ↓
user_listener: "Let me have assistant demonstrate it"
    ↓
assistant:
  - Creates demo of US-032 features
  - Tests all functionality
  - Presents visual walkthrough
    ↓
user_listener: "Here's the demo [shows to user]"
```

### Example 3: Bug Found During Demo (COMPREHENSIVE REPORT)

**Flow**:
```
User: "Test the user registration flow"
    ↓
user_listener: "I'll have assistant test it"
    ↓
assistant:
  - Navigates to /register
  - Tests form validation
  - BUG DETECTED: Accepts weak passwords (< 8 chars)
  - Analyzes bug comprehensively (root cause, requirements, impact)
  - Documents with comprehensive template
  - Reports to project_manager:

    "I found a critical bug during demo. Here's my comprehensive analysis:

    ## Bug Report from assistant

    **Summary**: Password validation allows weak passwords in registration

    **Severity**: High (security vulnerability)

    **Steps to Reproduce**:
    1. Navigate to http://localhost:8501/register
    2. Enter email: test@example.com
    3. Enter password: 'short' (5 characters)
    4. Click 'Create Account' button
    5. Observe form submission succeeds without validation error

    **Expected Behavior**:
    Form should display validation error: 'Password must be at least 8 characters'
    and prevent form submission until password meets minimum length.

    **Actual Behavior**:
    Form submits successfully with 5-character password. No validation error
    displayed. User account created with weak password.

    **Root Cause Analysis**:
    - Client-side validation missing password length check
    - validateRegistrationForm() does not include length requirement
    - HTML input lacks minlength attribute
    - Backend API accepts any password length without validation
    - No validation middleware on /api/register endpoint

    **Requirements for Fix**:
    1. Add client-side validation in validateRegistrationForm():
       - Check password.length >= 8
       - Display error message if validation fails
       - Prevent form submission if invalid
    2. Add HTML5 validation: <input type='password' minlength='8'>
    3. Add backend validation middleware to /api/register:
       - Validate password length >= 8
       - Return 400 error with message if invalid
    4. Add password requirements to UI with real-time feedback
    5. Add unit tests for password validation (client and server)
    6. Add integration test for registration with weak password

    **Expected Behavior Once Corrected**:
    1. User navigates to registration page
    2. UI displays: 'Minimum 8 characters'
    3. User enters < 8 characters
    4. Real-time feedback shows 'Too short'
    5. Submit button disabled until valid
    6. If client validation bypassed, server returns 400 error
    7. Clear error message displayed
    8. Form only submits with password >= 8 characters

    **Environment**:
    - Browser: Chrome 120.0.6099.129
    - Version: v1.0.0 (commit: abc123)
    - OS: macOS 14.4
    - Backend: Python 3.11, FastAPI 0.104.1

    **Impact Assessment**:
    - Primary feature broken: User Registration
    - Related features impacted: Password reset flow, Account security
    - User impact: Compromised account security, credential stuffing risk
    - Business impact: Security vulnerability, potential compliance violation

    **Screenshots/Videos**:
    - weak_password_form.png
    - weak_password_submitted.png
    - console_no_errors.png
    - network_201_response.png

    This provides architect and code_developer with:
    - Root cause: Missing validation at all levels
    - Requirements: Specific changes needed
    - Expected behavior: Exactly how fix should work
    - Test plan: What tests to add

    **Recommendation**: Add critical priority to ROADMAP immediately.
    I'll retry the demo after the fix to verify it works correctly."
    ↓
project_manager:
  - Reviews comprehensive bug report
  - Assesses impact (security issue = critical)
  - Adds to ROADMAP with full details:
    "US-036: Fix password validation security vulnerability in registration
     - Priority: Critical
     - Root Cause: Missing validation at client/HTML/server levels
     - Requirements: [includes assistant's 6 requirements]
     - Expected Fix Behavior: [includes assistant's corrected flow]
     - Blocks: Production deployment
     - Assigned: architect (design) + code_developer (implement)"
  - Tags architect and code_developer for urgent fix
    ↓
architect:
  - Reviews assistant's root cause analysis
  - Designs fix based on assistant's requirements
  - Creates technical specification for implementation
  - Approves design with user (if needed)
    ↓
code_developer:
  - Reviews architect's design and assistant's requirements
  - Implements fix (client validation + HTML + backend + tests)
  - Runs tests to verify fix
  - Creates PR and marks US-036 complete
    ↓
user_listener: "US-036 fix is complete. assistant, please retry the demo."
    ↓
assistant:
  - Retries registration flow demo
  - Verifies weak password now rejected with clear error message
  - Tests corrected behavior matches expected behavior from bug report
  - Reports success: "Demo now passes! Password validation working correctly."
    ↓
user_listener: "Bug fixed and verified! Demo complete."
```

### Example 4: Code Developer Needs Demo Created

**Flow**:
```
code_developer: (after completing feature)
  - "Feature US-040 complete, needs demo for documentation"
    ↓
code_developer → user_listener: "Please request demo from assistant"
    ↓
user_listener → assistant: "Create demo for US-040"
    ↓
assistant:
  - Creates comprehensive demo
  - Tests all features
  - If bugs found: Reports to project_manager
  - If all good: Delivers demo
    ↓
user_listener: "Demo ready" (shares with team)
```

### Example 5: Ownership Enforcement & Auto-Delegation

**Flow**:
```
project_manager attempts to modify .claude/CLAUDE.md:
    ↓
generator intercepts Edit tool call:
  - Checks FileOwnership registry
  - Finds: .claude/ owned by code_developer (NOT project_manager)
  - Logs: "Ownership violation detected"
    ↓
generator auto-delegates to code_developer:
  - "Delegating Edit(.claude/CLAUDE.md) from project_manager to code_developer"
  - Passes Edit parameters to code_developer
    ↓
code_developer executes Edit on .claude/CLAUDE.md:
  - Modifies file successfully
  - Returns success status
    ↓
generator captures delegation trace:
  - Violating agent: project_manager
  - Correct owner: code_developer
  - File: .claude/CLAUDE.md
  - Operation: Edit
  - Result: Success
  - Timestamp: 2025-10-16 14:23:45
  - Reason: ownership_enforcement
    ↓
generator returns success to project_manager:
  - project_manager receives result as if it did the edit itself
  - Transparent delegation (project_manager doesn't need to know)
    ↓
reflector analyzes delegation trace later:
  - Learns: "project_manager often needs code_developer for .claude/ changes"
  - Adds insight: "Pattern detected: Strategic docs → Technical config updates"
  - curator adds to playbook for future optimization
```

**Why This Works**:
- **Centralized enforcement**: generator is ideal interception point
- **Automatic correction**: Violations fixed, not just blocked
- **Transparent**: Agents don't need manual ownership checks
- **Learning opportunity**: reflector identifies delegation patterns
- **Zero violations**: No file operations execute with wrong owner

---

## Key Principles

### 1. Single Responsibility

Each agent has ONE primary responsibility:
- **user_listener**: User interface (ONLY)
- **project_manager**: Strategic planning
- **architect**: Architectural design
- **assistant**: Documentation + Dispatch + Demos + Bug Reports
- **code_developer**: Implementation (ONLY)

### 2. Clear Delegation

Agents delegate outside their domain:
- **user_listener** delegates ALL work to team
- **assistant** delegates implementation to code_developer
- **assistant** delegates bug fixes to project_manager → code_developer
- **code-searcher** delegates documentation to project_manager

### 3. No Overlap

Agents NEVER do another agent's work:
- **assistant** NEVER writes code
- **project_manager** NEVER creates PRs
- **code_developer** NEVER makes strategic ROADMAP decisions
- **user_listener** NEVER creates demos directly (delegates to assistant)

### 4. READ-ONLY vs WRITE

**READ-ONLY** (for code/docs):
- assistant
- code-searcher
- ux-design-expert

**WRITE** (specific domains):
- code_developer (code)
- project_manager (strategic docs)
- architect (architectural docs, dependencies)

**SPECIAL** (assistant):
- READ-ONLY for code/docs
- WRITE for demos (creates visual demonstrations)
- WRITE for bug reports (reports to project_manager)

---

## Anti-Patterns

### What NOT to Do

**DON'T**:
- assistant tries to fix bugs directly
  - INSTEAD: Report to project_manager

- project_manager tries to create demos
  - INSTEAD: Delegate to assistant

- user_listener tries to create demos directly
  - INSTEAD: Delegate to assistant

- assistant tries to add bugs to ROADMAP
  - INSTEAD: Report to project_manager, who adds to ROADMAP

- code_developer tries to create demos
  - INSTEAD: Request demo from assistant via user_listener

- Multiple agents doing the same task
  - INSTEAD: Clear single ownership

---

## Success Metrics

### Demo Creation

- Demos created within reasonable time
- Visual clarity and completeness
- Feature coverage
- User satisfaction with demos

### Bug Reporting

- Bugs detected during demos
- Quality of bug analysis
- Completeness of bug reports
- Timely addition to ROADMAP
- Bug fix success rate

### Collaboration

- Clear delegation paths
- No role confusion
- Efficient handoffs
- User satisfaction with team coordination

---

## Version History

**Version**: 1.1
**Date**: 2025-10-16
**Changes**:
- Added ACE Framework agents (generator, reflector, curator)
- Added generator's ownership enforcement role
- Added Example 5: Ownership Enforcement & Auto-Delegation
- Documented generator as central enforcement point for file ownership

**Version**: 1.0
**Date**: 2025-10-16
**Changes**: Initial creation with demo creation and bug reporting workflows

---

**Remember**: Successful collaboration depends on clear roles, clean delegation, and respecting boundaries!
