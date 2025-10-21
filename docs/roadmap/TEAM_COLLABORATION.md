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
  - "Feature US-032 complete, needs demo for documentation"
    ↓
code_developer → user_listener: "Please request demo from assistant"
    ↓
user_listener → assistant: "Create demo for US-032"
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

## Critical Functional Requirements (CFR) Enforcement

### Overview

The system enforces Critical Functional Requirements (CFRs) at ALL levels to prevent boundary violations. CFRs are system invariants documented in docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md.

**Four CFRs**:
- **CFR-001**: Document Ownership Boundaries (each file has EXACTLY ONE owner)
- **CFR-002**: Agent Role Boundaries (each agent has EXACTLY ONE primary role)
- **CFR-003**: No Overlap - Documents (no two agents own same file/directory)
- **CFR-004**: No Overlap - Responsibilities (no two agents have overlapping primary roles)

**Enforcement Levels**:
- **Level 1**: generator auto-delegation for file operations (US-038)
- **Level 2**: User story validation before ROADMAP addition (US-039)
- **Level 3**: User request validation before execution (US-039)
- **Level 4**: Agent self-check before planning work (US-039)

### Level 1: generator Auto-Delegation (US-038)

**Trigger**: Before ANY file operation (Edit, Write, NotebookEdit)

**Process**:
1. generator intercepts file operation tool call
2. generator checks FileOwnership registry
3. If requesting agent OWNS file: Execute directly
4. If requesting agent does NOT own file: Auto-delegate to correct owner
5. Capture delegation trace for reflector analysis
6. Return result to requesting agent transparently

**Example**:
```
project_manager attempts: Edit(.claude/CLAUDE.md)
    ↓
generator intercepts: Check ownership
    ↓
FileOwnership: .claude/ owned by code_developer (NOT project_manager)
    ↓
generator auto-delegates: Delegate to code_developer
    ↓
code_developer: Executes Edit on .claude/CLAUDE.md
    ↓
generator: Captures delegation trace
    ↓
generator: Returns success to project_manager
    ✅ Violation prevented, work completed, ownership respected
```

**Why This Works**:
- Automatic correction (not just blocking)
- Transparent to requesting agent
- Creates learning data for reflector
- Zero ownership violations reach execution

### Level 2: User Story Validation (US-039)

**Trigger**: Before adding user story to ROADMAP

**Process**:
1. project_manager receives user story creation request
2. CFRValidator.validate_user_story() checks:
   - CFR-001: Do assigned agents own target files?
   - CFR-002: Does work match assigned agents' roles?
   - CFR-003: Any ownership overlaps proposed?
   - CFR-004: Any role overlaps proposed?
3. If violations detected:
   - STOP user story creation
   - Expose problem to user with clear explanation
   - Provide 2-3 safe alternatives
   - Wait for user decision
4. If no violations: Proceed with adding to ROADMAP

**Example**:
```
User proposes: "US-040: project_manager refactors CLI code"
    ↓
CFRValidator checks:
  - CFR-001: coffee_maker/ owned by code_developer (NOT project_manager) ❌
  - CFR-002: Implementation is code_developer's role (NOT project_manager) ❌
    ↓
project_manager warns user:
  "⚠️ USER STORY VIOLATION DETECTED

  US-040 proposes: project_manager refactors CLI code

  Violations:
  1. CFR-001: coffee_maker/ owned by code_developer
  2. CFR-002: Implementation is code_developer's role

  Safe Alternatives:
  Option 1: project_manager defines requirements
            → architect designs refactoring
            → code_developer implements

  Option 2: Rewrite US-040 to assign work correctly

  Which approach do you prefer?"
    ↓
User chooses Option 1
    ↓
project_manager creates corrected user story with proper delegation
    ✅ Violation prevented BEFORE addition to ROADMAP
```

**Why This Matters**:
- Prevents bad user stories from being added
- Educates user about boundaries
- Ensures ROADMAP contains only valid work assignments

### Level 3: User Request Validation (US-039)

**Trigger**: When user makes request to any agent

**Process**:
1. Agent receives user request
2. CFRValidator.validate_user_request() checks:
   - What actions are required?
   - Which agents would handle these actions?
   - Do these match agent roles and ownerships?
3. If violations detected:
   - STOP execution
   - Explain problem to user
   - Offer safe alternatives (correct delegation paths)
   - Wait for user decision
4. If no violations: Proceed with delegation

**Example**:
```
User to assistant: "Implement the new authentication feature"
    ↓
CFRValidator checks:
  - Required action: Implementation
  - assistant's role: Demos + Documentation + Dispatch
  - CFR-002: assistant cannot implement code ❌
    ↓
assistant explains:
  "I can't implement code directly (CFR-002: Role Boundaries).
   I'll delegate to code_developer who handles implementation.

   Would you like me to:
   1. Delegate to code_developer to implement
   2. Have project_manager create strategic spec first
   3. Show you the current authentication system"
    ↓
User chooses Option 2
    ↓
assistant delegates:
  assistant → project_manager (strategic spec)
  → architect (technical spec)
  → code_developer (implementation)
    ✅ Violation prevented, user educated, correct workflow followed
```

**Why This Matters**:
- Prevents users from accidentally asking wrong agent
- Educates users about agent roles
- Ensures correct delegation from the start

### Level 4: Agent Self-Check (US-039)

**Trigger**: Before agent plans work

**Process**:
1. Agent is about to plan work (modify files, execute tasks)
2. Agent calls CFRValidator.agent_self_check():
   - Do I own the target files? (CFR-001)
   - Does this work match my primary role? (CFR-002)
3. If violations detected:
   - Do NOT execute work
   - Delegate to correct agent instead
   - Report to user if critical
4. If no violations: Proceed with work

**Example**:
```
assistant analyzes codebase and finds critical security bug
    ↓
assistant plans: Add bug to ROADMAP
    ↓
agent_self_check():
  - Target file: docs/roadmap/ROADMAP.md
  - CFR-001: docs/roadmap/ owned by project_manager (NOT assistant) ❌
  - CFR-002: assistant's role is Demos + Documentation + Dispatch ❌
    ↓
assistant decision: Delegate instead of execute
    ↓
assistant action:
  - Prepares comprehensive bug report (root cause, requirements, impact)
  - Delegates to project_manager with full analysis
    ↓
project_manager:
  - Receives bug report from assistant
  - Adds critical priority to ROADMAP
  - Tags architect and code_developer
    ✅ Ownership respected, work completed correctly
```

**Why This Matters**:
- Agents self-enforce boundaries
- Prevents violations before they occur
- Enables autonomous delegation

### Violation Response Workflow

**When CFR violation detected at ANY level**:

1. **STOP** the violating action immediately
2. **ANALYZE** the violation:
   - What was attempted?
   - Who attempted it?
   - Which CFR was violated?
   - Who should handle this instead?
3. **CHOOSE** response path:
   - **Auto-Delegate** (Level 1, Level 4): generator or agent automatically delegates
   - **Expose to User** (Level 2, Level 3): Explain problem, offer alternatives
4. **EXECUTE** safe alternative:
   - Delegate to correct agent
   - Follow multi-agent workflow
   - Review CFRs and reconsider
5. **LEARN** from violation:
   - Capture delegation trace (Level 1)
   - Track violation patterns (all levels)
   - reflector analyzes for improvements

### Safe Alternative Patterns

**Pattern 1: Auto-Delegation** (Level 1, Level 4):
```
Agent A needs to modify file owned by Agent B
    ↓
generator or Agent A delegates to Agent B
    ↓
Agent B modifies file
    ↓
Result returned to Agent A
    ✅ Transparent, automatic, respects ownership
```

**Pattern 2: Multi-Agent Workflow** (Level 2, Level 3):
```
User requests work that spans multiple agent roles
    ↓
Decompose into sub-tasks:
  - project_manager: Strategic requirement (WHAT/WHY)
  - architect: Technical design (HOW)
  - code_developer: Implementation (DOING)
    ↓
Each agent handles their sub-task
    ✅ Each agent in their role
```

**Pattern 3: Request Decomposition**:
```
User: "Implement feature X and update ROADMAP"
    ↓
Decompose:
  1. code_developer: Implement feature
  2. project_manager: Update ROADMAP
    ↓
Execute separately with correct owners
    ✅ No violations
```

**Pattern 4: Cross-Agent Communication**:
```
Agent A has information for Agent B's files
    ↓
Agent A prepares content
    ↓
Agent A delegates to Agent B
    ↓
Agent B modifies their files with Agent A's input
    ✅ Ownership respected
```

### Integration with US-035 and US-038

**US-035: Singleton Enforcement**:
- Ensures one instance per agent type
- Prevents multiple instances competing
- CFR-004 ensures each singleton has ONE role

**US-038: File Ownership Enforcement**:
- generator auto-delegates file operations
- Level 1 enforcement (foundation)
- CFR-001 and CFR-003 define ownership rules

**US-039: Comprehensive CFR Enforcement**:
- Adds Level 2, 3, 4 enforcement
- Validates user stories and requests
- Enables agent self-check
- Completes CFR architecture

**Together**:
```
US-035 (Singleton) + US-038 (Ownership) + US-039 (Comprehensive CFR)
= Complete system integrity enforcement
```

### Benefits of CFR Enforcement

**For Users**:
- Transparent violations exposed before problems occur
- Clear explanations with safe alternatives
- Educated about agent boundaries
- Confidence in system integrity

**For Agents**:
- Automatic correction of violations
- Clear boundaries prevent confusion
- Safe delegation patterns
- Learning from violation patterns

**For System**:
- Cannot break itself through boundary violations
- Architectural integrity maintained
- Parallel agent operations safe
- Foundation for autonomous operation

### Reference Documents

- **Complete CFR Documentation**: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md
- **User Story**: docs/roadmap/ROADMAP.md (US-039)
- **Technical Spec**: docs/architecture/user_stories/US_039_TECHNICAL_SPEC.md (to be created by architect)
- **Ownership Matrix**: .claude/CLAUDE.md (Agent Tool Ownership & Boundaries section)

---

## Task Delegation Tool Usage

### Overview

All agents use a centralized delegation tool instead of directly calling other agents. This ensures:
- Centralized routing through generator (ACE framework)
- Automatic CFR checking before delegation
- Consistent delegation patterns
- Traceability for learning

### How It Works

```
Agent needs work outside boundaries
    ↓
Agent calls: delegate_task(task, context)
    ↓
Delegation tool → generator
    ↓
generator analyzes task, checks CFRs, decides routing
    ↓
generator delegates to appropriate agent(s)
    ↓
Result returns to requesting agent (transparent)
```

### Usage Examples

**Example 1: project_manager delegates to code_developer**:
```python
# ❌ DON'T: Direct agent call
result = code_developer.implement_feature(feature_spec)

# ✅ DO: Use delegation tool
result = delegate_task(
    task="Implement authentication feature from US-032",
    context={
        "feature_spec": "docs/roadmap/PRIORITY_32_STRATEGIC_SPEC.md",
        "priority": "high",
        "acceptance_criteria": [...]
    },
    requesting_agent="project_manager"
)
# → generator routes to code_developer
# → code_developer implements feature
# → result returned to project_manager
```

**Example 2: assistant delegates code analysis to code-searcher**:
```python
# ❌ DON'T: Direct agent call
analysis = code_searcher.analyze_security_vulnerabilities()

# ✅ DO: Use delegation tool
analysis = delegate_task(
    task="Perform security audit on authentication module",
    context={
        "focus": "authentication",
        "analysis_type": "security",
        "output_format": "detailed_report"
    },
    requesting_agent="assistant"
)
# → generator routes to code-searcher
# → code-searcher performs analysis
# → assistant receives findings
# → assistant delegates documentation to project_manager
```

**Example 3: code_developer delegates ROADMAP update**:
```python
# ❌ DON'T: Modify ROADMAP directly (violates CFR-001)
# Edit(docs/roadmap/ROADMAP.md, ...)

# ✅ DO: Use delegation tool
result = delegate_task(
    task="Mark US-040 complete in ROADMAP",
    context={
        "priority": "US-040",
        "status": "complete",
        "completion_date": "2025-10-16"
    },
    requesting_agent="code_developer"
)
# → generator routes to project_manager (owns docs/roadmap/)
# → project_manager updates ROADMAP.md
# → result returned to code_developer
```

### Benefits

**For Agents**:
- No need to know which agent handles what
- Automatic ownership violation prevention
- Transparent delegation (works like direct call)
- Clear context passing

**For System**:
- Centralized routing through generator
- All delegations respect CFRs automatically
- Delegation traces captured for learning
- Consistent patterns across all agents

**For Debugging**:
- Complete delegation trace available
- Can analyze delegation patterns
- Can optimize routing based on history
- Can identify bottlenecks

### Integration Points

- **generator**: Central orchestrator, routes all delegations
- **CFR Validator**: Checks ownership/role boundaries before delegation
- **reflector**: Analyzes delegation traces for insights
- **curator**: Learns optimal delegation patterns

---

## Complexity Escalation Workflow

### Overview

When an agent faces complexity that makes it hard to respect CFRs, they escalate through a defined chain for guidance and simplification.

### Escalation Chain

```
Agent (complexity detected)
    ↓
    "I can't do this without violating CFRs"
    ↓
project_manager (strategic simplification)
    ↓
    Analyzes complexity, provides strategic guidance
    ↓
    If still complex → Escalate to architect
    ↓
architect (technical simplification)
    ↓
    Creates technical spec or guidelines
    ↓
    If still complex → Escalate to user
    ↓
User (final decision)
    ↓
    Reviews options, makes informed decision
    ↓
    Approves CFR change OR chooses alternative
```

### When to Escalate

**✅ DO Escalate When**:
- Cannot complete task without violating CFR
- Multiple approaches all violate CFRs
- Unclear which agent owns responsibility
- Fundamental conflict between CFRs and requirements
- Need architectural or strategic guidance

**❌ DON'T Escalate When**:
- Simply don't want to delegate (use delegation tool)
- Solution is obvious (just needs proper delegation)
- Haven't tried to find CFR-respecting approach
- Trying to shortcut proper workflows

### Escalation Examples

**Example 1: code_developer escalates to project_manager**:
```
code_developer:
"COMPLEXITY ESCALATION

From: code_developer
To: project_manager

Task: Implementing US-040 requires updating ROADMAP.md to mark completion

Complexity: ROADMAP.md owned by you (CFR-001), but I need synchronized updates

CFRs Involved:
- CFR-001: Document Ownership (I don't own docs/roadmap/)

Options I've Considered:
1. Modify ROADMAP directly - Violates CFR-001
2. Delegate to you after implementation - Respects CFR-001 but adds delay
3. Create separate status file - Adds complexity, duplicate tracking

Request: How should I handle ROADMAP updates while respecting CFR-001?"

project_manager response:
"Use delegation approach (Option 2):
1. Implement feature
2. Commit code
3. Delegate ROADMAP update to me
4. I update ROADMAP.md
5. I commit change

This respects CFR-001 and is simple. Proceed with implementation."

Result: ✅ Complexity resolved at project_manager level
```

**Example 2: project_manager escalates to architect**:
```
project_manager:
"COMPLEXITY ESCALATION

From: project_manager
To: architect

Task: US-041 (multi-tenant architecture) needs implementation guidance

Complexity: code_developer unsure how to structure code while respecting role boundaries

CFRs Involved:
- CFR-002: Role Boundaries (implementation is their role, design is yours)

Options I've Considered:
1. I provide design guidance - Violates CFR-002 (not my role)
2. code_developer guesses design - Risk of poor architecture
3. You create technical spec - Respects CFR-002

Request: Can you create technical spec with architectural design?"

architect response:
"I'll create docs/architecture/user_stories/US_041_TECHNICAL_SPEC.md with:
- Clear architectural design (my role)
- Implementation guidelines for code_developer
- Respects CFR-002

Spec ready in 2 hours."

Result: ✅ Complexity resolved at architect level
```

**Example 3: architect escalates to user**:
```
architect:
"COMPLEXITY ESCALATION

From: architect
To: user (via project_manager)

Task: US-042 requires documentation spanning strategic and technical boundaries

Complexity: Cannot avoid ownership overlap without fundamental changes

CFRs Involved:
- CFR-003: No Overlap - Documents (docs/roadmap/ vs docs/architecture/)

Options I've Considered:
1. Split docs across boundaries - Complex coordination, fragmented
2. Create shared directory - VIOLATES CFR-003
3. Assign all docs to one owner - One agent outside typical role
4. Redesign feature - Major scope change

Request: Which approach do you prefer?"

User decision:
"Choose Option 3: Assign to architect (primarily technical docs).
Update CFR-001 ownership matrix accordingly."

Result: ✅ Complexity resolved with user decision, CFRs maintained
```

### Escalation Message Format

All escalations must follow this template:

```
COMPLEXITY ESCALATION

From: [Agent Name]
To: [project_manager or architect or user]

Task: [Clear description of what you're trying to do]

Complexity: [Why it's hard to respect CFRs]

CFRs Involved: [Which CFRs are at risk - use CFR numbers]

Options I've Considered:
1. [Option 1] - [Why it violates or doesn't work]
2. [Option 2] - [Why it violates or doesn't work]
3. [Option 3] - [Why it violates or doesn't work]

Request: [Specific guidance or decision needed]
```

### Benefits of Escalation Workflow

**For Agents**:
- Clear path when stuck
- No need to violate CFRs
- Expert guidance available at each level
- Can focus on their role

**For project_manager**:
- Visibility into complexity issues
- Opportunity to simplify strategically
- Control over CFR exceptions
- Can escalate further if needed

**For architect**:
- Can provide technical guidance
- Ensures clean architectural decisions
- Prevents technical debt from workarounds
- Can escalate to user if fundamental

**For Users**:
- Only involved when truly needed
- Clear options presented with pros/cons
- Final authority on CFR changes
- Informed decision making

### Integration with CFR Enforcement

The escalation workflow is part of the comprehensive CFR enforcement system:

```
Level 1: generator auto-delegation (US-038)
    ↓
Level 2: User story validation (US-039)
    ↓
Level 3: User request validation (US-039)
    ↓
Level 4: Agent self-check (US-039)
    ↓
Escalation: When complexity exceeds agent capability
    ↓
project_manager → architect → user
```

Each level provides increasing authority and decision-making power to resolve complexity while maintaining CFR integrity.

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

**Version**: 1.4
**Date**: 2025-10-16
**Changes**:
- REMOVED Project Planner Mode section (US-040 - CFR incompatible)
- US-040 violated CFR-001 (user cannot directly edit project_manager's files)

**Version**: 1.3
**Date**: 2025-10-16
**Changes**:
- Added Task Delegation Tool Usage section with examples
- Added Complexity Escalation Workflow section with detailed examples
- Documented delegation tool integration with generator
- Documented escalation chain (Agent → project_manager → architect → user)
- Added escalation message format template
- Enhanced collaboration patterns with delegation and escalation

**Version**: 1.2
**Date**: 2025-10-16
**Changes**:
- Added Critical Functional Requirements (CFR) Enforcement section
- Documented 4 enforcement levels (generator auto-delegation, user story validation, user request validation, agent self-check)
- Added violation response workflow and safe alternative patterns
- Documented integration with US-035, US-038, US-039
- Added reference to CRITICAL_FUNCTIONAL_REQUIREMENTS.md

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
