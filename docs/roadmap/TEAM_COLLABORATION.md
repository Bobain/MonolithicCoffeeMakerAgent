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
- Creates technical specifications (docs/PRIORITY_*_TECHNICAL_SPEC.md)
- Monitors GitHub (PRs, issues, CI/CD)
- Post-completion DoD verification (when user requests)
- Receives bug reports from assistant
- Adds critical priorities to ROADMAP based on bug reports
- Warns users about blockers

### Architecture & Design

**architect**
- Architectural design BEFORE implementation
- Creates technical specifications (docs/architecture/specs/)
- Documents architectural decisions (ADRs in docs/architecture/decisions/)
- Provides implementation guidelines (docs/architecture/guidelines/)
- ONLY agent that manages dependencies (pyproject.toml, poetry.lock)
- Asks user for approval on important decisions (especially dependencies)
- Interacts with user through user_listener

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

**assistant responsibilities**:

1. **Analyze Bug Thoroughly**
   ```
   What was expected?
   What actually happened?
   Steps to reproduce
   Console errors or visual issues
   Screenshots showing the problem
   Severity assessment
   ```

2. **Document Findings**
   ```
   Title: Clear, concise description
   Description: Detailed analysis
   Steps to reproduce: Exact sequence
   Expected vs actual behavior: Comparison
   Evidence: Screenshots, console logs
   Severity: Critical, High, Medium, Low
   ```

3. **Report to project_manager**
   ```
   Format:
   "I found a bug during demo creation:

   **Title**: [Clear bug description]

   **Description**: [Detailed analysis]

   **Steps to Reproduce**:
   1. [Step 1]
   2. [Step 2]
   3. [Step 3]

   **Expected**: [What should happen]
   **Actual**: [What actually happened]

   **Evidence**: [Screenshots, console logs]
   **Severity**: [Critical/High/Medium/Low]

   **Recommendation**: [Suggested action]"
   ```

4. **project_manager Action**
   ```
   Receives bug report from assistant
   Reviews severity and impact
   Adds critical priority to ROADMAP
   Updates format: US-XXX: Fix [bug description]
   Assigns priority based on severity
   Notifies code_developer if urgent
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

### Example 3: Bug Found During Demo

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
  - Analyzes bug thoroughly
  - Documents with screenshots
  - Reports to project_manager:

    "I found a critical bug during demo:

    **Title**: Password validation allows weak passwords
    **Description**: Registration accepts passwords under 8 characters
    **Steps to Reproduce**: [detailed steps]
    **Expected**: Validation error for weak password
    **Actual**: Form submits successfully
    **Evidence**: [screenshot: weak_password_accepted.png]
    **Severity**: High (security vulnerability)
    **Recommendation**: Add critical priority to ROADMAP"
    ↓
project_manager:
  - Reviews bug report
  - Assesses impact (security issue = critical)
  - Adds to ROADMAP:
    "US-036: Fix password validation in registration
     - Priority: Critical
     - Allows weak passwords (< 8 chars)
     - Security vulnerability"
  - Notifies user via user_listener
    ↓
user_listener: "Bug found and reported. project_manager added US-036 to ROADMAP as critical priority"
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

**Version**: 1.0
**Date**: 2025-10-16
**Changes**: Initial creation with demo creation and bug reporting workflows

---

**Remember**: Successful collaboration depends on clear roles, clean delegation, and respecting boundaries!
