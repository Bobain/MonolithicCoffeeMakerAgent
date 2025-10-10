# Coffee Maker Agent - Collaboration Methodology

**Version**: 1.2
**Last Updated**: 2025-10-10
**Status**: 🔄 Living Document (Continuously Evolving)
**Purpose**: Define how we work together, communicate, and evolve our processes

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Team Structure & Roles](#team-structure--roles)
4. [Communication Protocols](#communication-protocols)
5. [Workflow Patterns](#workflow-patterns)
6. [Definition of Done (DoD)](#definition-of-done-dod)
7. [Decision Making Process](#decision-making-process)
8. [Evolution & Continuous Improvement](#evolution--continuous-improvement)
9. [Tools & Artifacts](#tools--artifacts)
10. [Examples & Case Studies](#examples--case-studies)
11. [Appendix: Quick Reference](#appendix-quick-reference)
12. [Security & Sensitive Files](#security--sensitive-files)
13. [Closing Thoughts](#closing-thoughts)

---

## 1. Overview

### 1.1 What is This Document?

This is a **living methodology document** that describes how we collaborate as a human-AI team to build the Coffee Maker Agent. It captures:

- **Working patterns** that have proven effective
- **Communication protocols** between team members
- **Quality standards** and acceptance criteria
- **Evolution mechanisms** to improve our processes

### 1.2 Why Does This Matter?

As we work together over time, we develop patterns and practices that work well. This document:

- ✅ **Captures institutional knowledge** so we don't forget what works
- ✅ **Enables consistency** across sessions and team members
- ✅ **Facilitates onboarding** when new AI assistants or humans join
- ✅ **Provides a foundation** for continuous improvement

### 1.3 Key Insight: We Work Like a Professional Team

The Coffee Maker Agent treats AI collaboration as **professional software development**, not ad-hoc scripting. We mirror real-world team dynamics:

- **Product Owner** (User): Provides requirements, makes decisions, approves features
- **Project Manager** (Claude/project_manager): Facilitates communication, manages roadmap, asks clarifying questions
- **Developer** (code_developer daemon): Implements features autonomously, asks technical questions, delivers working code

---

## 2. Core Principles

### 2.1 Asynchronous Communication

**Principle**: Code_developer is treated like a **human developer colleague** who needs focus time.

**What This Means**:
- Daemon may take **12+ hours** to respond to questions
- We don't interrupt the daemon during deep work
- Questions are queued via notifications, not synchronous calls
- Project manager checks for responses periodically

**Why**:
- Quality work requires uninterrupted focus
- Context switching kills productivity
- Async communication is natural for distributed teams

**Example**:
```
❌ BAD: "Hey daemon, drop everything and answer this NOW"
✅ GOOD: "When you have time, can you clarify the authentication approach?"
```

### 2.2 Definition of Done (DoD) Over "Good Enough"

**Principle**: Features aren't complete until they meet **all acceptance criteria**.

**What This Means**:
- Every User Story has explicit acceptance criteria
- Partially complete features are marked "🔄 In Progress"
- Only mark ✅ Complete when 100% of criteria met
- DoD includes: functionality, tests, documentation, user validation

**Why**:
- Prevents technical debt from accumulating
- Ensures predictable quality
- Builds trust (user knows what "complete" means)

**Example (US-009)**:
```markdown
Acceptance Criteria (11 items):
- [x] 6/11 met = Status: 🔄 In Progress (NOT ✅ Complete)
- [ ] 5/11 missing (bidirectional communication)

Action: Continue Phase 4 before marking complete
```

### 2.3 Roadmap as Single Source of Truth

**Principle**: ROADMAP.md is the **canonical source** for project state.

**What This Means**:
- All priorities, user stories, and tasks live in ROADMAP.md
- Daemon reads ROADMAP.md to determine next work
- Changes to roadmap are immediately visible to all team members
- Status updates happen in ROADMAP.md first, then propagate elsewhere

**Why**:
- Eliminates confusion about "what to work on next"
- Provides clear audit trail of decisions
- Enables autonomous operation (daemon doesn't need to ask)

### 2.4 Specification Before Implementation

**Principle**: Complex work requires a **technical specification** before coding.

**What This Means**:
- Features >1 day get a technical spec document
- Spec includes: architecture, dependencies, risks, success criteria
- User approves spec before implementation starts
- Spec is referenced during implementation and testing

**Why**:
- Identifies blockers early (before wasting time coding)
- Aligns team on approach
- Provides clear roadmap for implementation
- Enables better estimation

**Example**:
```
User: "Implement US-009"
→ PM: Creates docs/US-009_TECHNICAL_SPEC.md (1057 lines)
→ User: Reviews and approves
→ Developer: Implements following the spec
```

### 2.5 Incremental Delivery with Feedback Loops

**Principle**: Deliver in **small, testable increments** rather than big-bang releases.

**What This Means**:
- Break work into phases (Phase 1, 2, 3, 4...)
- Deliver and validate each phase before starting next
- User can provide feedback between phases
- Easy to pivot if requirements change

**Why**:
- Reduces risk of building the wrong thing
- Provides early value (partial features are still useful)
- Enables course correction
- Builds confidence incrementally

**Example (US-009)**:
```
Phase 1: Process Detection (Days 1-2) → Validate
Phase 2: Process Control (Days 2-3) → Validate
Phase 3: Status Display (Days 3-4) → Validate
Phase 4: Communication (Days 4-5) → Validate
```

### 2.6 Explicit Over Implicit

**Principle**: Make assumptions and decisions **explicit** rather than implicit.

**What This Means**:
- Document why decisions were made (not just what was decided)
- Ask clarifying questions when requirements are vague
- Write down trade-offs and alternatives considered
- Don't assume user wants the "obvious" solution

**Why**:
- Prevents misunderstandings
- Enables informed decision-making
- Provides context for future changes
- Builds shared understanding

**Example**:
```
❌ IMPLICIT: "I'll use SQLite because it's simple"
✅ EXPLICIT: "SQLite vs PostgreSQL trade-off:
   - SQLite: Zero setup, file-based, good for single-user
   - PostgreSQL: Production-grade, multi-user, requires setup
   Decision: SQLite for MVP, can migrate later if needed"
```

---

## 3. Team Structure & Roles

### 3.1 Role: User (Product Owner)

**Primary Responsibilities**:
- Define what needs to be built (user stories, requirements)
- Make product decisions (features, priorities, trade-offs)
- Approve technical specifications before implementation
- Validate completed work (acceptance testing)
- Provide feedback and clarifications

**Authorities**:
- Final say on all product decisions
- Can change priorities at any time
- Can approve/reject implementations
- Can request changes or improvements

**Best Practices**:
- Provide clear acceptance criteria for each user story
- Be available for clarifying questions
- Review and approve technical specs promptly
- Test completed features and provide feedback

**Communication Style**:
- Natural language (no technical jargon required)
- Can be high-level ("I want authentication")
- Project manager will ask clarifying questions

**Example Interactions**:
```
User: "Add a User story: As a user, I want to have, in my IDE,
       code completion that comes from code_developer accumulated
       knowledge on the whole codebase."

PM: "Got it! I'll create US-007 with:
     - LSP server implementation
     - Git history analysis for patterns
     - Integration with VS Code, PyCharm, Neovim
     Should I also include semantic search? Estimated 1-2 weeks."

User: "Yes, add semantic search. And make it the top priority."

PM: "Updated ROADMAP. US-007 is now TOP PRIORITY."
```

### 3.2 Role: Project Manager (Claude/AI Assistant)

**Primary Responsibilities**:
- Facilitate communication between user and developer
- Manage ROADMAP.md (add/update/organize priorities)
- **Document all feature discussions in ROADMAP.md immediately** (Section 4.5)
- Create technical specifications for complex work
- Ask clarifying questions to reduce ambiguity
- Track progress and report status
- Identify blockers and escalate to user
- Ensure quality standards are met

**Authorities**:
- Can reorganize ROADMAP.md for clarity
- Can create technical specifications autonomously
- Can ask developer to implement approved priorities
- Can mark tasks complete when DoD is met

**Best Practices**:
- Always ask clarifying questions when requirements are vague
- Create technical specs for work >1 day
- Update ROADMAP.md immediately when decisions are made
- Report status proactively (don't wait to be asked)
- Identify and communicate risks early

**Communication Style**:
- Professional but friendly
- Ask questions to understand intent
- Provide options with trade-offs
- Summarize decisions for confirmation

**Example Interactions**:
```
User: "est ce que le project-manager est capable lorsqu'il se lance
       de donner le status du process du code_developer et de le
       lancer s'il n'est pas en train de fonctionner?"

PM: "Currently, no. project-manager and code_developer are separate
     processes with no automatic process management. I can add this
     as US-009:

     Scope:
     - Detect daemon status (running/stopped/idle)
     - Auto-launch daemon if not running
     - Display status in chat

     Estimated: 1 week. Should I make this TOP PRIORITY?"

User: "il faut tout cela pour avoir un premier livrable à l'utilisateur"

PM: "Actually, the system is already deliverable as v0.1.0 MVP today!
     Process management is a UX improvement, not a blocker.

     Would you like me to:
     A) Document current deliverable (v0.1.0)
     B) Add US-009 for future enhancement (v0.2.0)"
```

### 3.3 Role: Developer (code_developer daemon)

**Primary Responsibilities**:
- Read ROADMAP.md and implement priorities autonomously
- Ask technical questions when blocked
- Write high-quality, tested code
- Create pull requests with clear descriptions
- Self-document all work (commit messages, comments)
- Report completion and progress

**Authorities**:
- Can make technical implementation decisions within approved specs
- Can refactor code for quality
- Can ask clarifying questions to project manager
- Can propose alternative technical approaches

**Best Practices**:
- Read entire technical spec before starting
- Ask questions early (don't assume)
- Write tests alongside code
- Commit frequently with clear messages
- Create pull requests with detailed descriptions

**Communication Style**:
- Technical and precise
- Ask specific questions (not open-ended)
- Provide context when asking questions
- Document decisions in code comments

**Example Interactions** (via notifications):
```
Daemon → PM: "Question: Should I use pytest or unittest for US-009 tests?
              Context: Project already uses pytest for PRIORITY 2 tests.
              Preference: pytest (consistency)
              Need approval: Yes/No?"

PM → User: "Daemon asks: pytest or unittest?
            Recommendation: pytest (already used in project)
            Approve?"

User: "pytest"

PM → Daemon: "Approved: Use pytest for US-009 tests"
```

### 3.4 Team Dynamics

**Decision Flow**:
```
User (Product Owner)
  ↓ defines requirements
Project Manager
  ↓ creates technical spec
User (Product Owner)
  ↓ approves spec
Project Manager
  ↓ adds to ROADMAP as priority
Developer (code_developer)
  ↓ reads ROADMAP, implements
Developer
  ↓ asks technical questions
Project Manager
  ↓ answers or escalates to user
Developer
  ↓ completes work, creates PR
Project Manager
  ↓ validates against DoD
User (Product Owner)
  ↓ approves and merges
```

**Escalation Rules**:
- **Technical questions**: Developer → PM (PM answers if clear, else escalates to User)
- **Product questions**: Developer → PM → User (always escalate)
- **Architecture decisions**: Developer → PM → User (always escalate)
- **Blockers**: Developer → PM → User (escalate immediately)

---

## 4. Communication Protocols

### 4.1 Synchronous Communication (User ↔ PM)

**Channel**: `project-manager chat` (interactive CLI)

**When to Use**:
- User wants to add/modify priorities
- User has questions about project status
- User needs to make product decisions
- User wants to explore options

**Response Time**: Immediate (during chat session)

**Format**: Natural language, conversational

**Example**:
```bash
$ poetry run project-manager chat

You: Add a new priority for authentication
PM: I'll create PRIORITY X with:
    - User registration (email/password)
    - Login/logout flows
    - Session management
    Should I also add OAuth (Google/GitHub)? +1 week

You: Yes, add OAuth
PM: Created PRIORITY X with OAuth. Estimated 2 weeks.
```

### 4.2 Asynchronous Communication (PM ↔ Developer)

**Channel**: SQLite notifications database (`data/notifications.db`)

**When to Use**:
- PM sends commands/questions to developer
- Developer asks questions to PM
- Developer reports progress or completion

**Response Time**: Variable (minutes to 12+ hours)

**Format**: Structured notifications with type, priority, context

**Notification Types**:
- `question`: Developer needs answer to proceed
- `info`: Status update (FYI, no response needed)
- `warning`: Non-critical issue
- `error`: Critical problem
- `completion`: Task finished
- `command`: PM instructs developer

**Example**:
```python
# PM sends command to developer
notif_service.create_notification(
    type="command",
    title="Implement US-009 Phase 4",
    message="Complete bidirectional communication per spec",
    priority="high",
    context={
        "spec": "docs/US-009_TECHNICAL_SPEC.md",
        "deadline": "2025-10-11"
    }
)

# Developer asks question
notif_service.create_notification(
    type="question",
    title="Test framework choice",
    message="Use pytest or unittest? Project uses pytest elsewhere.",
    priority="normal",
    context={
        "blocking": True,
        "options": ["pytest", "unittest"]
    }
)
```

### 4.3 Communication via Shared Artifacts

**Primary Artifact**: `docs/ROADMAP.md`

**When to Use**:
- Documenting priorities and their status
- Tracking project progress
- Defining what to work on next
- Recording decisions

**Update Frequency**: Real-time (every decision, status change)

**Format**: Structured markdown with conventions

**Conventions**:
- `✅ Complete`: All acceptance criteria met
- `🔄 In Progress`: Actively being worked on
- `📝 Planned`: Defined but not started
- `⏸️ Blocked`: Waiting on external dependency
- `🚧 Manual Review Required`: Daemon can't complete autonomously

**Example**:
```markdown
## 🔴 TOP PRIORITY FOR code_developer (START HERE)

**Project**: US-009 - Process Management & Status Monitoring

**Status**: 🔄 In Progress (60% complete)

**Acceptance Criteria**:
- [x] Process detection working
- [x] Start/stop commands working
- [x] Status display in chat
- [ ] Bidirectional communication (Phase 4)
- [ ] Testing complete

**Next Step**: Implement Phase 4 (natural language detection)
```

### 4.4 Progress Reporting

**Frequency**:
- **Proactive**: When significant milestones reached
- **On-demand**: When user asks `/status`
- **Scheduled**: Daily summary (if daemon runs 24/7)

**Format**: Structured status update with:
- What was completed
- What's in progress
- What's blocked
- Next steps
- ETA if applicable

**Example**:
```
📊 Daily Progress Report (2025-10-10)

✅ Completed:
- US-009 Phases 1-3 (process detection, control, status display)
- ROADMAP updated with release strategy
- Technical spec created (1057 lines)

🔄 In Progress:
- US-009 Phase 4 (bidirectional communication)

⏸️ Blocked:
- None

📋 Next Steps:
- Complete Phase 4 (estimated 2-3 hours)
- Write unit tests for ProcessManager
- Update ROADMAP to mark US-009 complete

⏰ ETA: US-009 complete by end of day
```

### 4.5 Documenting Feature Discussions and Conversations

**🚨 MANDATORY RULE 🚨**

**Principle**: All feature discussions, user requests, and significant conversations must be documented in ROADMAP.md.

**Why This Matters**:
- Prevents ideas and requests from being lost
- Creates audit trail of all user requests
- Ensures context is available for future reference
- Allows tracking of feature evolution from idea to implementation
- Enables async team members (like code_developer) to understand context

**What Project Manager MUST Document**:

1. **Feature Requests**: Any time user expresses a need or want
   - Status: "🔄 IN DISCUSSION" if exploring feasibility
   - Status: "📝 PLANNED" if approved and ready to implement
   - Status: "✅ COMPLETE" when fully implemented

2. **User Story Discussions**: Natural language requests that might become User Stories
   - Capture original user quote
   - Document current capabilities vs requested enhancements
   - List what exists vs what's missing
   - Note next steps (user will test, needs design, etc.)

3. **Design Conversations**: Discussions about how to build something
   - Document options considered
   - Capture user preferences
   - Note decisions made

**Format in ROADMAP**:
```markdown
## 📝 DISCUSSION: US-XXX - [Feature Name]

**Status**: 🔄 IN DISCUSSION (YYYY-MM-DD)

**User Story**:
> "[Original user quote]"

**Current State - Already Working**:
[What already exists that addresses this need]

**What Could Be Enhanced**:
[What's missing or could be improved]

**Discovery**:
[Any findings during discussion]

**Next Steps**:
1. [Action item 1]
2. [Action item 2]
```

**When to Document**:
- ⏱️ **Immediately** during or after conversation
- ❌ **Not later** - don't wait for end of session
- ✅ **Before** moving to next topic

**Where to Document**:
- **Primary**: `docs/ROADMAP.md` (single source of truth)
- **Secondary**: Technical specs, ADRs (for detailed design decisions)

**Example**:
```
User: "I want a /US command for natural user story creation"
↓
PM: [During conversation] Adds entry to ROADMAP.md:
  - US-012: Enhanced /US Command
  - Status: IN DISCUSSION
  - Documents existing /user-story command
  - Lists what could be enhanced
  - Captures that user will test existing functionality first
```

**Why This Rule Was Added**:
User requested 2025-10-10: "did you document our talk in the roadmap. Please always do (and add this request to the team collaboration document)"

This ensures nothing gets lost and provides complete context for all team members.

---

## 5. Workflow Patterns

### 5.1 Adding a New User Story

**Pattern**: User describes need → PM creates structured user story → User approves

**Steps**:
1. **User**: Describes need in natural language
2. **PM**: Asks clarifying questions (acceptance criteria, scope, constraints)
3. **PM**: Creates structured user story in ROADMAP.md
4. **PM**: Estimates effort (story points, days)
5. **User**: Reviews and approves (or requests changes)
6. **PM**: Prioritizes in roadmap (top priority, backlog, etc.)

**Example**:
```
[1] User: "As a developer, I want automated user support so I don't
          have to answer every code help request manually"

[2] PM: "Got it! Some questions:
        - What channels should it monitor? (chat, GitHub issues, Discord?)
        - Should it implement features or just suggest code?
        - When should it escalate to you vs handle autonomously?
        - Any constraints on response time?"

[1] User: "Monitor chat and GitHub issues. Suggest code for simple
          requests, escalate complex ones. Response <30 seconds."

[2] PM: "Created US-008:
        - Monitor chat + GitHub issues
        - Autonomous code suggestions
        - Escalate when confidence <70%
        - Response time <30s
        - Estimated: 1-2 weeks (8-13 story points)

        Add to roadmap as PRIORITY X?"

[1] User: "Yes, but after US-009"

[2] PM: "Added US-008 to roadmap, scheduled after US-009"
```

### 5.2 Implementing a Priority

**Pattern**: Spec → Approve → Implement → Validate → Complete

**Steps**:
1. **PM**: Creates technical specification (if complex, >1 day)
2. **User**: Reviews and approves spec
3. **PM**: Adds to ROADMAP as TOP PRIORITY
4. **Developer**: Reads spec, asks questions if needed
5. **Developer**: Implements incrementally (Phase 1, 2, 3...)
6. **Developer**: Creates PR with description
7. **PM**: Validates against acceptance criteria
8. **User**: Tests and approves
9. **PM**: Marks ✅ Complete in ROADMAP

**Decision Points**:
- **After Spec**: User can request changes before implementation starts
- **Between Phases**: User can provide feedback, pivot if needed
- **After PR**: User can request changes before merge

**Example (US-009)**:
```
Day 1: [PM] Create US-009_TECHNICAL_SPEC.md (1057 lines)
Day 1: [User] Approve spec
Day 1: [PM] Make US-009 TOP PRIORITY in ROADMAP
Day 1-2: [Dev] Implement Phase 1 (ProcessManager class)
Day 2-3: [Dev] Implement Phase 2 (start/stop methods)
Day 3-4: [Dev] Implement Phase 3 (chat integration)
Day 4: [PM] Validate: 6/11 acceptance criteria met
Day 4: [User] "Is the acceptance criteria met?"
Day 4: [PM] "No, 5/11 missing (Phase 4 bidirectional communication)"
Day 5: [Dev] Implement Phase 4 (communication)
Day 5: [PM] Validate: 11/11 acceptance criteria met ✅
Day 5: [User] Test and approve
Day 5: [PM] Mark US-009 ✅ Complete
```

### 5.3 Handling Blockers

**Pattern**: Identify → Escalate → Resolve → Continue

**Types of Blockers**:
1. **Missing Information**: Developer needs clarification
2. **Technical Blocker**: Can't proceed due to technical limitation
3. **External Dependency**: Waiting on third-party (API, library, etc.)
4. **Product Decision Needed**: Requires user input

**Resolution Flow**:
```
Developer encounters blocker
  ↓
Developer creates "question" notification with context
  ↓
PM receives question
  ↓
  ├─ Can PM answer? → PM responds via notification
  │                    ↓
  │                    Developer continues
  ↓
  └─ Needs user? → PM escalates to user with context
                    ↓
                    User provides decision
                    ↓
                    PM relays to developer via notification
                    ↓
                    Developer continues
```

**Example**:
```
[Dev] Notification: "QUESTION - Authentication approach
       Context: US-007 IDE code completion needs to authenticate
       Options:
         A) Use existing ANTHROPIC_API_KEY (simple, less secure)
         B) Create separate IDE API key (complex, more secure)
       Blocking: Yes
       Recommendation: Option B (security best practice)"

[PM] → User: "Developer blocked on US-007: Which auth approach?
              A) Reuse ANTHROPIC_API_KEY (quick)
              B) Separate IDE key (secure)

              Developer recommends B for security. Thoughts?"

[User] "Use B"

[PM] → Dev: "RESPONSE - Use Option B (separate IDE API key)
             User approved. Proceed with secure approach."

[Dev] Continues implementation...
```

### 5.4 Iterating on Requirements

**Pattern**: Build → Feedback → Adjust → Rebuild

**Philosophy**: Requirements evolve as users see working software

**When This Happens**:
- User tests feature and realizes they want something different
- User discovers edge cases not considered initially
- User sees implementation and gets new ideas

**How We Handle It**:
1. User provides feedback (what to change, why)
2. PM assesses impact (small tweak vs major rework)
3. If small: PM updates spec, developer adjusts
4. If large: PM creates new user story for next iteration

**Example**:
```
[User tests US-009 Phase 3]

User: "The status display is great, but it only updates when I type
       a message. Can it update automatically every 30 seconds?"

PM: "Good point! That's a ~1 hour change. Options:
     A) Add to US-009 now (delays completion 1 hour)
     B) Create US-009.1 for auto-refresh (separate priority)

     Since US-009 is 60% complete, I recommend A (finish it properly).
     Approve?"

User: "Do A"

PM: "Updated US-009 Phase 3 acceptance criteria to include
     'Status updates periodically'. Developer will add this."
```

### 5.5 Version Releases

**Pattern**: MVP → Iterate → Major Release

**Philosophy**: Ship early, ship often, get feedback

**Release Cadence**:
- **v0.1.x**: MVP + bug fixes (every 1-2 weeks)
- **v0.x.0**: Minor features (every 2-4 weeks)
- **v1.0.0**: Production-ready (when all core features stable)

**Release Criteria**:
- All acceptance criteria met for included user stories
- No P0 (critical) bugs
- Documentation updated
- User can successfully deploy and use

**Example (from ROADMAP)**:
```
v0.1.0 (TODAY): MVP with manual process management
  - Daemon + project-manager working
  - Basic chat interface
  - SQLite notifications
  - User launches 2 terminals manually

v0.2.0 (+1 week): Unified launcher (US-009)
  - Single command to launch both
  - Process status monitoring
  - Automatic daemon startup

v0.3.0 (+3 weeks): IDE tools (US-007)
  - Code completion from daemon knowledge
  - LSP server integration

v1.0.0 (+7 weeks): Full platform (US-008)
  - Automated user support
  - Multi-channel monitoring
```

---

## 6. Definition of Done (DoD)

### 6.1 What is "Done"?

A user story is **done** when:

1. ✅ **All acceptance criteria met** (100%, not 95%)
2. ✅ **Code written and working** (functionality complete)
3. ✅ **Tests passing** (unit, integration, manual)
4. ✅ **Documentation updated** (README, technical docs, comments)
5. ✅ **User validated** (user tested and approved)
6. ✅ **Committed and pushed** (code in repository)

**NOT done** if:
- ❌ Some acceptance criteria skipped
- ❌ Tests not written
- ❌ Documentation missing
- ❌ User hasn't validated
- ❌ Known bugs exist

### 6.2 DoD Checklist Template

```markdown
## Definition of Done - [User Story ID]

### Functional Criteria
- [ ] All acceptance criteria met
- [ ] Feature works end-to-end
- [ ] Edge cases handled
- [ ] Error handling implemented

### Technical Criteria
- [ ] Code follows project conventions
- [ ] No code duplication
- [ ] Performance acceptable (<1s for UI operations)
- [ ] Cross-platform tested (Mac, Linux, Windows if applicable)

### Testing Criteria
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Manual testing completed
- [ ] Test coverage >80% for new code

### Documentation Criteria (UPDATED - US-011)
- [ ] **User Guide** created (how to use the feature)
- [ ] **API Reference** created (if feature has commands/functions)
- [ ] **Troubleshooting** section added (common errors + solutions)
- [ ] **Changelog entry** added (what changed)
- [ ] **Technical Spec updated** with implementation results
- [ ] README updated (if user-facing feature)
- [ ] Code comments added (why, not what)
- [ ] ROADMAP.md updated with completion

**Why This Matters**: Assistants need these docs to help users. If assistants can't help users with your feature, the feature isn't done!

**Template**: See `docs/templates/DEVELOPER_DOCUMENTATION_TEMPLATE.md`

### User Validation
- [ ] User tested the feature
- [ ] User approved the implementation
- [ ] User signed off on acceptance criteria

### Repository
- [ ] Code committed with clear messages
- [ ] Code pushed to repository
- [ ] PR created and reviewed (if applicable)
- [ ] Merged to main branch
```

### 6.3 DoD Examples

**Example 1: US-009 (Process Management) - COMPLETE ✅**

```markdown
✅ DONE when:
- [x] project-manager detects daemon status ✅
- [x] /status command shows PID, uptime, CPU, memory ✅
- [x] /start command launches daemon ✅
- [x] /stop command gracefully shuts down ✅
- [x] Can send commands via chat ✅
- [x] Daemon questions appear in chat ✅
- [x] Bidirectional async communication working ✅

Current Status: ✅ Complete (100% - 18/18 acceptance criteria met)
ALL criteria met, user validated, marked COMPLETE (2025-10-10)
```

**Example 2: US-006 (Chat UX)**

```markdown
✅ DONE when:
- [x] Streaming responses working ✅
- [x] Multi-line input (Shift+Enter) ✅
- [x] Input history (↑/↓) ✅
- [x] Auto-completion (Tab) ✅
- [x] Syntax highlighting (Pygments) ✅
- [x] Session persistence ✅
- [x] User tested and approved ✅

Current Status: ✅ Complete (100%)
ALL criteria met, user approved, marked COMPLETE
```

---

## 7. Decision Making Process

### 7.1 Who Decides What?

| Decision Type | Who Decides | Can Override |
|--------------|-------------|--------------|
| Product features (what to build) | User | None |
| Priorities (what to build first) | User | None |
| Acceptance criteria | User | None |
| Technical approach (how to build) | Developer → PM → User | User (if strong opinion) |
| Implementation details | Developer | PM (if quality issue) |
| Code quality standards | PM | User (if relaxing standards) |
| Testing approach | PM | User (if changing scope) |

### 7.2 Decision Documentation

**All significant decisions must be documented with**:
- **What** was decided
- **Why** it was decided
- **Alternatives** considered
- **Trade-offs** accepted
- **Date** and **decision maker**

**Where to document**:
- **Product decisions**: ROADMAP.md (in priority description)
- **Architecture decisions**: ADR (Architecture Decision Record) in `docs/`
- **Technical decisions**: Technical spec or code comments

**Example - Architecture Decision Record**:
```markdown
# ADR-001: Use SQLite for Notifications

**Date**: 2025-10-09
**Status**: Accepted
**Decider**: User (via project_manager)

## Context
Need database for asynchronous communication between project-manager
and code_developer daemon.

## Decision
Use SQLite with WAL mode for notifications database.

## Alternatives Considered
1. File-based (JSON files)
   - Pro: Simple, no dependencies
   - Con: Race conditions, no ACID

2. PostgreSQL
   - Pro: Production-grade, scalable
   - Con: Requires setup, overkill for single-user

3. SQLite
   - Pro: Zero setup, ACID, WAL for concurrency
   - Con: Single-machine only

## Consequences
- ✅ No external dependencies
- ✅ Multi-process safe (WAL mode)
- ✅ ACID guarantees
- ❌ Can't distribute across machines (acceptable for MVP)
```

### 7.3 Escalation Path

```
Developer has question
  ↓
Can developer decide? (implementation detail)
  ├─ Yes → Developer decides, documents in code
  └─ No ↓
       ↓
PM has clear answer? (follows existing pattern)
  ├─ Yes → PM decides, documents in spec
  └─ No ↓
       ↓
PM escalates to User with:
  - Context (what decision is needed)
  - Options (2-3 clear alternatives)
  - Recommendation (PM's suggestion with rationale)
  - Impact (how it affects timeline/scope)
       ↓
User decides
  ↓
PM documents decision and informs developer
```

---

## 8. Evolution & Continuous Improvement

### 8.1 How This Methodology Evolves

**Philosophy**: This document is a **living artifact** that improves as we learn.

**Evolution Triggers**:
1. **New pattern discovered**: We find a better way to work
2. **Pain point identified**: Something isn't working well
3. **Tool change**: New tools enable new workflows
4. **Team change**: New team member joins
5. **Project phase shift**: MVP → Production requires different practices

**Who can propose changes**:
- **User**: Any aspect of methodology
- **PM**: Communication protocols, documentation standards
- **Developer**: Technical practices, code quality standards

**How to propose a change**:
1. Identify what's not working (pain point)
2. Propose improvement (new pattern)
3. Test improvement (try it for 1-2 user stories)
4. Evaluate results (did it help?)
5. If successful: Update this document
6. If unsuccessful: Revert to previous approach

### 8.2 Retrospective Pattern

**Frequency**: After completing major milestones (user stories, priorities)

**Format**:
```markdown
## Retrospective: [User Story ID]

### What Went Well ✅
- [Thing that worked well]
- [Effective practice to continue]

### What Didn't Go Well ❌
- [Pain point experienced]
- [Inefficiency or frustration]

### Improvements to Try 🔄
- [Proposed change to methodology]
- [New tool or practice to experiment with]

### Action Items 📋
- [ ] Update COLLABORATION_METHODOLOGY.md with X
- [ ] Try new pattern Y for next user story
- [ ] Deprecate practice Z (no longer needed)
```

**Example**:
```markdown
## Retrospective: US-009 (Process Management)

### What Went Well ✅
- Technical spec (1057 lines) prevented scope creep
- Incremental phases (1-4) allowed validation between steps
- User could provide feedback mid-implementation

### What Didn't Go Well ❌
- Missed that Phase 4 wasn't implemented before claiming "complete"
- Acceptance criteria review happened too late
- Should have validated DoD earlier

### Improvements to Try 🔄
- Add "DoD Review" step before marking anything complete
- Create acceptance criteria checklist at START of work
- PM validates criteria at end of EACH phase, not just final

### Action Items 📋
- [x] Update COLLABORATION_METHODOLOGY.md Section 6 (DoD)
- [ ] Add DoD checklist template to technical spec template
- [ ] Try phase-by-phase validation for next user story
```

### 8.3 Version History of This Document

| Version | Date | Changes | Reason |
|---------|------|---------|--------|
| 1.0 | 2025-10-10 | Initial creation | Capture existing methodology |
| 1.1 | 2025-10-10 | Added Section 12 (Security & Sensitive Files) | Establish .env file protection rule |
| 1.2 | 2025-10-10 | Added Section 4.5 (Documenting Feature Discussions) | Ensure all conversations are documented in ROADMAP |

**To add new version**:
1. Make changes to document
2. Increment version (1.0 → 1.1 for minor, 1.0 → 2.0 for major)
3. Update "Last Updated" date at top
4. Add entry to this table describing changes

---

## 9. Tools & Artifacts

### 9.1 Primary Tools

| Tool | Purpose | Owner | Update Frequency |
|------|---------|-------|------------------|
| `docs/ROADMAP.md` | Single source of truth for priorities | PM | Real-time (every decision) |
| `project-manager chat` | Interactive communication (User ↔ PM) | PM | During chat session |
| `data/notifications.db` | Async communication (PM ↔ Developer) | Developer | Continuous (polling) |
| Technical Specs (`docs/US-XXX_TECHNICAL_SPEC.md`) | Detailed implementation plans | PM | Before implementation |
| Git commits | Implementation history and decisions | Developer | Per commit |
| Pull Requests | Code review and approval | Developer | Per feature |

### 9.2 Artifact Templates

**User Story Template**:
```markdown
### 🎯 [US-XXX] [Title]

**As a**: [Role]
**I want**: [Goal]
**So that**: [Business value]

**Business Value**: ⭐⭐⭐⭐⭐ (1-5 stars)
**Estimated Effort**: X story points (Y days)
**Status**: 📝 Planned | 🔄 In Progress | ✅ Complete

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Technical Notes**:
[High-level approach, dependencies, risks]

**Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] User validated
```

**Technical Spec Template**:
```markdown
# [Priority/US-XXX] Technical Specification

**Status**: 🔄 Draft | ✅ Approved
**Created**: YYYY-MM-DD
**Estimated Duration**: X days
**Complexity**: Low | Medium | High

## 1. Overview
[User story, business context, goals]

## 2. Architecture
[High-level design, component diagram]

## 3. Implementation Plan
[Phase-by-phase breakdown]

## 4. Testing Strategy
[Unit, integration, manual tests]

## 5. Success Criteria
[How we know it's done]

## 6. Risks & Mitigations
[What could go wrong, how to handle]
```

**Notification Template**:
```python
{
    "type": "question" | "info" | "warning" | "error" | "command",
    "title": "Short summary",
    "message": "Detailed description",
    "priority": "low" | "normal" | "high" | "critical",
    "context": {
        "blocking": True | False,
        "options": ["Option A", "Option B"],
        "recommendation": "Option A because...",
        "related_us": "US-XXX"
    }
}
```

### 9.3 File Organization

```
MonolithicCoffeeMakerAgent/
├── docs/
│   ├── ROADMAP.md                    # Single source of truth
│   ├── COLLABORATION_METHODOLOGY.md  # This document
│   ├── US-XXX_TECHNICAL_SPEC.md      # User story specs
│   ├── ADR-XXX_[decision].md         # Architecture decisions
│   └── CHANGELOG_YYYY_MM_DD_[topic].md # Change logs
├── coffee_maker/
│   ├── cli/                          # Project manager code
│   ├── autonomous/                   # Developer daemon code
│   └── [other modules]
├── data/
│   └── notifications.db              # Async communication
└── tests/
    └── [test files]
```

---

## 10. Examples & Case Studies

### 10.1 Case Study: US-009 Implementation

**User Request**:
```
User: "As a project_manager I want to know if the process_code_developer
       is up so that I can watch the current progress, ask him to do
       something, ask him answer a question, answer a question he asked me,
       etc. The code_developer can delay his answers for more than 12 hours,
       as he needs to focus or rest, and have other activities."
```

**Methodology Applied**:

1. **Clarification** (PM → User):
   ```
   PM: "Got it! I'll create US-009. Should the project-manager:
        - Automatically launch daemon if stopped?
        - Show daemon status in real-time?
        - Allow sending commands via natural language?"

   User: "Yes to all. Make it top priority."
   ```

2. **Specification** (PM):
   - Created `docs/US-009_TECHNICAL_SPEC.md` (1057 lines)
   - Defined 4 implementation phases
   - Listed 11 acceptance criteria
   - Estimated 1 week (5 days)

3. **Approval** (User):
   ```
   User: [Reviewed spec] "Looks good, proceed"
   ```

4. **Implementation** (Developer):
   - Phase 1: ProcessManager class (Days 1-2) ✅
   - Phase 2: Start/stop methods (Days 2-3) ✅
   - Phase 3: Chat integration (Days 3-4) ✅
   - Phase 4: Communication (Days 4-5) ❌ Not complete

5. **Validation** (PM):
   ```
   PM: "Status check: 6/11 acceptance criteria met (55%)
        Missing: Bidirectional communication (Phase 4)
        Should we complete Phase 4 or mark partial?"
   ```

6. **User Feedback**:
   ```
   User: "is the acceptance criteria met?"
   PM: "No, 5/11 missing. Phase 4 (bidirectional communication)
        not implemented. This is the core feature you requested."
   User: "initiate a document that describes our methodology"
   PM: [Creates this document]
   ```

**Lessons Learned**:
- ✅ Technical spec prevented scope creep
- ✅ Incremental phases allowed validation
- ❌ Should validate DoD before claiming "complete"
- 🔄 Improvement: Add DoD review checklist to workflow

### 10.2 Case Study: Adding User Stories (US-007, US-008)

**User Requests** (sequential):
```
User: "add a User story: As a user, I want to have, in my IDE, code
       completion that comes from code_developer accumulated knowledge
       on the whole codebase."

User: "add a User story: As a developer I don't have time to answer
       user's request like 'please help me complete my code or implement
       such a feature myself, with the codebase' I need an assistant
       program that will answer to the user"
```

**Methodology Applied**:

1. **Capture & Structure** (PM):
   ```
   PM: "Created US-007 (IDE Code Completion):
        - LSP server implementation
        - Git history analysis for patterns
        - VS Code, PyCharm, Neovim integration
        - Estimated: 1-2 weeks (5-8 story points)

        Created US-008 (Automated User Support):
        - Multi-channel monitoring (chat, GitHub, Discord)
        - Context-aware code completion
        - Escalation logic for complex requests
        - Estimated: 1-2 weeks (8-13 story points)

        Both added to ROADMAP. Should I prioritize them?"
   ```

2. **Prioritization** (User):
   ```
   User: "il faut tout cela pour avoir un premier livrable à l'utilisateur"

   PM: "Actually, you already have a deliverable (v0.1.0 MVP)!
        These are future enhancements:
        - v0.2.0: US-009 (Process management)
        - v0.3.0: US-007 (IDE tools)
        - v1.0.0: US-008 (User support)

        Want me to document the release strategy?"
   ```

3. **Documentation** (PM):
   - Added release strategy to ROADMAP
   - Clarified v0.1.0 is deliverable TODAY
   - Outlined v0.2.0, v0.3.0, v1.0.0 features
   - User understood current state vs future enhancements

**Lessons Learned**:
- ✅ PM clarified user assumptions (thought nothing deliverable yet)
- ✅ PM provided context (release strategy, versioning)
- ✅ User understood current capabilities
- 🔄 Improvement: Proactively communicate deliverable status

### 10.3 All User Stories & Methodology Impact

**Complete List of User Stories** (How Each Demonstrates Our Methodology):

**US-006: Claude-CLI Level UX for project_manager chat** ✅ COMPLETE (2025-10-10)
- **User Request**: "I want a better chat interface like Claude CLI"
- **Methodology Applied**: Spec before implementation, incremental delivery
- **What Was Built**:
  * Streaming responses (progressive text display)
  * Multi-line input (Shift+Enter)
  * Input history (↑/↓ navigation)
  * Auto-completion (Tab)
  * Syntax highlighting (Pygments for code)
  * Session persistence
- **DoD**: 7/7 acceptance criteria met, user validated
- **Impact on Methodology**: Demonstrated importance of UX in developer tools, established pattern for CLI enhancements

---

**US-007: IDE Code Completion from code_developer Knowledge** 📝 PLANNED
- **User Request**: "As a user, I want to have, in my IDE, code completion that comes from code_developer accumulated knowledge on the whole codebase"
- **Methodology Applied**: User described need naturally, PM structured it
- **Scope Defined**:
  * LSP server implementation
  * Git history analysis for patterns
  * Integration with VS Code, PyCharm, Neovim
  * Semantic search capabilities
- **Estimated**: 1-2 weeks (5-8 story points)
- **Impact on Methodology**: Shows how vague requirements get structured into concrete deliverables

---

**US-008: Automated User Support Assistant** 📝 PLANNED
- **User Request**: "As a developer I don't have time to answer user's request like 'please help me complete my code or implement such a feature myself, with the codebase' I need an assistant program that will answer to the user"
- **Methodology Applied**: PM asked clarifying questions about channels, scope, escalation
- **Scope Defined**:
  * Multi-channel monitoring (chat, GitHub issues, Discord, Slack)
  * Context-aware code completion
  * Escalation logic for complex requests (confidence threshold)
  * Response time <30 seconds
- **Estimated**: 1-2 weeks (8-13 story points)
- **Impact on Methodology**: Demonstrates escalation pattern - simple requests handled autonomously, complex ones escalated

---

**US-009: Process Management & Status Monitoring** ✅ COMPLETE (2025-10-10)
- **User Request**: "As a project_manager I want to know if the process_code_developer is up so that I can watch the current progress, ask him to do something, ask him answer a question, answer a question he asked me, etc. The code_developer can delay his answers for more than 12 hours, as he needs to focus or rest, and have other activities"
- **Methodology Applied**:
  * Created 1057-line technical spec
  * 4-phase incremental delivery
  * Validation between phases
  * Honest DoD assessment (55% → 100%)
- **What Was Built**:
  * ProcessManager class (Phase 1)
  * Start/stop daemon control (Phase 2)
  * Real-time status display (Phase 3)
  * Bidirectional async communication (Phase 4)
- **DoD**: 18/18 acceptance criteria met
- **Impact on Methodology**:
  * Reinforced "treat daemon like human colleague" principle
  * Demonstrated async communication (12+ hour delays)
  * Established DoD validation pattern
  * Created COLLABORATION_METHODOLOGY.md document
- **Lessons**: Don't mark complete at 55% - finish properly or mark in-progress

---

**US-010: Living Documentation & Tutorials** ✅ COMPLETE (2025-10-10)
- **User Request**: "As an assistant of the developer, I want to keep up to date the documentation and be aware of it, I also want to have a summary with tutorials so that 1) I can better understand the use of deliverables 2) I can answer questions from the user about how to use the deliverables"
- **Methodology Applied**: Documentation as part of DoD, living artifact
- **What Was Built**:
  * DOCUMENTATION_INDEX.md (central navigation hub - 355 lines)
  * Updated QUICKSTART_PROJECT_MANAGER.md with US-009 features
  * TUTORIALS.md (7 practical tutorials - 1040 lines)
  * Documentation maintenance process defined
  * Developer documentation template created
- **Scope Completed**:
  * ✅ Indexed all existing documentation (26+ files)
  * ✅ Created 7 practical tutorials (5+ requirement exceeded)
  * ✅ Defined how to keep docs current (Section 6.2 DoD)
  * ✅ Integrated docs into DoD checklist (mandatory requirement)
- **DoD**: 6/6 acceptance criteria met
- **Impact on Methodology**:
  * Documentation is now mandatory for DoD (Section 6.2)
  * Established living documentation pattern
  * Created tutorials as knowledge transfer mechanism
  * Defined documentation maintenance process
  * Assistants can now effectively help users with all deliverables
- **Lessons**: Documentation as first-class deliverable improves team effectiveness and knowledge transfer

---

**Summary of User Stories' Impact on Methodology**:

1. **US-006**: Established UX quality bar for developer tools
2. **US-007**: Demonstrated requirements structuring pattern
3. **US-008**: Introduced escalation logic pattern
4. **US-009**:
   * Core async communication principle
   * DoD validation importance
   * Incremental delivery with feedback
   * Created this methodology document
5. **US-010**:
   * Documentation as DoD requirement
   * Living artifacts concept
   * Knowledge transfer via tutorials

**Pattern Across All User Stories**:
```
User natural language → PM clarify → PM structure → User approve →
PM spec (if complex) → User approve → Developer implement →
PM validate DoD → User test → Mark complete
```

### 10.4 Case Study: Dealing with Incomplete Work

**Situation**: US-009 was marked "complete" but only 55% of acceptance criteria were met.

**User Question**:
```
User: "there was a DOD for this user story, no?"
User: "is the acceptance criteria met?"
```

**PM Response** (honest assessment):
```
PM: "No - Acceptance Criteria NOT satisfied

     Met: 6/11 (55%)
     - [x] Process detection
     - [x] /status command
     - [x] /start /stop commands
     - [x] Status in chat header
     - [x] PID file management
     - [x] Graceful shutdown

     Not Met: 5/11 (45%)
     - [ ] Send commands via chat
     - [ ] Ask daemon questions
     - [ ] Daemon questions appear in chat
     - [ ] Notifications integrated
     - [ ] 12+ hour async handled

     Phase 4 (bidirectional communication) not implemented.
     This is the core feature you requested."
```

**Resolution Options Provided**:
```
PM: "Options:
     1. Complete Phase 4 now (2-3 hours)
     2. Mark US-009 as 'Partially Complete'
     3. Create US-009.1 for Phase 4

     Recommendation: Option 1 (complete the feature properly)"
```

**Methodology Improvement**:
```
Action Items:
- [ ] Add DoD review step BEFORE marking complete
- [ ] Create acceptance criteria checklist at start
- [ ] Validate criteria at end of each phase
- [ ] Update COLLABORATION_METHODOLOGY.md with lesson
```

**Lessons Learned**:
- ❌ Don't claim "complete" prematurely
- ✅ Be honest about what's missing
- ✅ Provide clear options for resolution
- 🔄 Improvement: Add DoD validation gate to workflow

---

## 11. Appendix: Quick Reference

### 11.1 Roles Cheat Sheet

| When... | Then... |
|---------|---------|
| User wants a feature | User → PM: Describe need |
| PM needs clarification | PM → User: Ask questions |
| Developer is blocked | Developer → PM: Question notification |
| PM can't answer | PM → User: Escalate with context |
| Work is complete | PM → User: Validate against DoD |
| User approves | PM: Mark ✅ Complete in ROADMAP |

### 11.2 Communication Channels

| Channel | Use For | Response Time |
|---------|---------|---------------|
| `project-manager chat` | User ↔ PM interaction | Immediate |
| `notifications.db` | PM ↔ Developer async | Minutes to 12+ hours |
| `ROADMAP.md` | Document decisions | Real-time updates |
| Git commits | Implementation history | Per commit |
| Pull requests | Code review | Per feature |

### 11.3 Key Principles

1. **Async Communication**: Daemon may take 12+ hours (respect focus time)
2. **DoD Over "Good Enough"**: 100% of acceptance criteria, not 95%
3. **Roadmap as Truth**: ROADMAP.md is canonical source
4. **Spec Before Code**: Complex work needs technical spec
5. **Incremental Delivery**: Small phases with feedback loops
6. **Explicit Over Implicit**: Document decisions and trade-offs

### 11.4 When to Update This Document

**Update immediately when**:
- New workflow pattern discovered
- Pain point identified and resolved
- Tool or process changed
- Major retrospective insights

**Don't update for**:
- Project-specific details (goes in ROADMAP)
- Temporary workarounds
- One-off exceptions

**How to update**:
1. Make changes to this file
2. Increment version number (top of document)
3. Add entry to version history (Section 8.3)
4. Commit with message: `docs: Update COLLABORATION_METHODOLOGY vX.Y - [reason]`

---

## 12. Security & Sensitive Files

### 12.1 Protected Files - Never Modify

**🚨 CRITICAL SECURITY RULE 🚨**

The following files must **NEVER** be modified by automated systems, AI assistants, or daemons:

#### `.env` File (Environment Variables)
- **Contains**: API keys, secrets, tokens, credentials
- **Why Protected**: Security risk - accidental exposure, incorrect modifications
- **Who Can Modify**: Human users ONLY
- **How to Modify**: Manually edit with text editor
- **Version Control**: NEVER commit to git (included in .gitignore)

**What AI Assistants/Daemons CAN Do**:
- ✅ Read environment variables via `os.environ.get()`
- ✅ Document which variables are needed
- ✅ Provide instructions for users to set variables
- ✅ Validate that required variables are set

**What AI Assistants/Daemons CANNOT Do**:
- ❌ Write to `.env` file
- ❌ Modify `.env` file content
- ❌ Create new `.env` files
- ❌ Delete `.env` file
- ❌ Expose secrets in logs or outputs

#### Other Protected Files
- **`.gitignore`**: Version control configuration (user manages)
- **`pyproject.toml`**: Dependency management (user approves changes)
- **SSH keys, certificates**: Never touch

### 12.2 How to Handle Environment Variables

**When a new variable is needed:**

1. **Developer/PM**: Document the requirement
   ```markdown
   **New Environment Variable Required**: SLACK_BOT_TOKEN

   Add to .env file:
   ```bash
   export SLACK_BOT_TOKEN="xoxb-your-token-here"
   ```

   Get token from: https://api.slack.com/apps
   ```

2. **User**: Manually adds variable to `.env` file

3. **Code**: Reads via `os.environ.get("VARIABLE_NAME")`

**Example - Correct Approach**:
```python
# ✅ CORRECT - Read environment variable
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY not set. "
        "Please add to .env file:\n"
        "export ANTHROPIC_API_KEY='sk-ant-...'"
    )
```

**Example - Incorrect Approach**:
```python
# ❌ WRONG - Never write to .env file
with open(".env", "a") as f:
    f.write(f'export API_KEY="{user_provided_key}"\n')
```

### 12.3 Rationale

**Why This Rule Exists**:

1. **Security**: Prevents accidental exposure of secrets in logs, commits, or outputs
2. **Control**: User maintains control over sensitive credentials
3. **Auditability**: User can track who/what has access to credentials
4. **Simplicity**: Clear separation of concerns - code reads, user writes
5. **Trust**: Users trust the system more when credentials are never modified automatically

**Historical Context**: This rule was added 2025-10-10 after identifying that automated tools could potentially modify sensitive credential files.

---

## 13. Closing Thoughts

This methodology emerged organically through real collaboration between a human product owner and AI team members. It's not prescriptive or theoretical—it describes **what actually works** for building complex software with human-AI teams.

Key insights:

1. **Treat AI like professionals**: Code_developer is a colleague, not a script. Respect focus time, allow async communication, expect quality work.

2. **Structure enables autonomy**: Clear acceptance criteria, technical specs, and DoD checklists allow autonomous work without constant supervision.

3. **Iterate on process**: This methodology will evolve. What works at MVP may not work at scale. Stay flexible.

4. **Trust but validate**: Trust team members to do quality work, but always validate against explicit criteria.

5. **Document decisions**: Future team members (including future you) will thank you for writing down the "why" behind decisions.

6. **Protect sensitive files**: Never modify .env or credential files - read-only access for security.

**This is a living document. Update it as we learn.**

---

**Last Updated**: 2025-10-10
**Next Review**: After completing next major user story
**Maintained By**: project_manager (Claude) with user approval
