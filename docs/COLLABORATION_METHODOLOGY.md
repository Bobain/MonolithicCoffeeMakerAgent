# Coffee Maker Agent - Collaboration Methodology

**Version**: 2.0
**Last Updated**: 2025-10-11
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

### 2.4 Specification Before Implementation (Enhanced - US-016)

**🚨 MANDATORY RULE 🚨**

**Principle**: Complex work requires a **detailed technical specification with task-level time estimates** before coding. PM **CANNOT** provide delivery estimates without creating a spec first.

**What This Means**:
- Features >1 day get a technical spec document
- Spec MUST include **task-level breakdown** with time estimates (not just phases)
- Each task estimated in hours (0.5h - 4h granularity)
- User approves spec before implementation starts
- Spec is referenced during implementation and testing
- **PM must refuse to estimate without spec**

**When Spec is Created**:
1. User describes need → PM creates user story
2. User approves user story
3. **PM creates detailed technical spec** (task-level estimates)
4. User approves spec
5. Implementation begins

**Task-Level Requirements** (US-016):
Each phase in the spec must break down into specific tasks:
```markdown
**Phase 1: Database Schema** (Total: 6 hours)
- [ ] Design tables (1.5h)
- [ ] Write migration scripts (2h)
- [ ] Add indexes (1h)
- [ ] Write tests for schema (1.5h)

**Phase 2: API Implementation** (Total: 8 hours)
- [ ] Create endpoint routes (2h)
- [ ] Implement business logic (3h)
- [ ] Add error handling (1h)
- [ ] Write integration tests (2h)

**Total Estimated Delivery**: 14 hours (1.75 days)
```

**PM Must Refuse to Estimate Without Spec**:

❌ **BAD** (What PM must NOT do):
```
User: "How long will feature X take?"
PM: "Probably 3-4 days"  ← WRONG! No spec created!
```

✅ **GOOD** (What PM MUST do):
```
User: "How long will feature X take?"

PM: "I need to create a technical specification first to give you an accurate estimate.

Without a detailed spec with task-level breakdown, any estimate would be a guess
and could be off by 2-3x.

I can create a technical spec in about 15-30 minutes that will give us a much
more accurate delivery estimate.

Should I proceed with creating the spec?"

User: "Yes"

PM: [Creates detailed spec with task-level estimates]

PM: "Based on the detailed task breakdown in docs/US-XXX_TECHNICAL_SPEC.md:

**Phase 1**: 6 hours
**Phase 2**: 8 hours
**Phase 3**: 4 hours

**Total Estimated Delivery**: 18 hours (2.25 days)

Would you like to review the technical spec before I proceed?"
```

**Why This is Critical**:
- **Accurate estimation**: Task-level breakdown reveals hidden complexity
- **Prevents scope creep**: All work identified upfront
- **Enables tracking**: Can track actual vs estimated per task (US-015 metrics)
- **Improves over time**: Historical task data improves future estimates
- **Identifies blockers early**: Before wasting time coding

**Quality Requirements**:
- No "misc" or "other" tasks without detail
- Testing time explicitly included per phase
- Documentation time explicitly included
- Dependencies between tasks documented
- Risks identified per phase

**Example (US-009)**:
```
User: "Implement US-009"

PM: "I'll create a detailed technical specification first."

→ PM: Creates docs/US-009_TECHNICAL_SPEC.md (1057 lines)
  - Phase 1: Process Detection (6h) - 4 tasks detailed
  - Phase 2: Process Control (4h) - 3 tasks detailed
  - Phase 3: Status Display (6h) - 5 tasks detailed
  - Phase 4: Communication (8h) - 6 tasks detailed
  - Total: 24 hours (3 days)

→ User: Reviews and approves spec

→ PM: "Based on the spec, delivery estimate is 3-5 days including testing."

→ Developer: Implements following the task-by-task spec
```

**See Also**:
- **US-016** in ROADMAP.md for complete specification
- **US-015** for tracking estimated vs actual task times
- **Section 9.2** for Technical Spec Template

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

### 2.7 Code References Methodology Document (US-017)

**🚨 IMPLEMENTATION REQUIREMENT 🚨**

**Principle**: Code implementing project_manager and code_developer must **read and reference** this COLLABORATION_METHODOLOGY.md document to understand processes, rules, and behavioral requirements.

**What This Means**:
- PM and developer code should load this document at startup
- Code should validate actions against documented processes
- Mandatory rules (like "spec before estimate") should be enforced in code
- Process changes in this document should automatically affect code behavior

**Why**:
- **Single source of truth**: Methodology defined once, used everywhere
- **Consistency**: Code behavior matches documented process
- **Maintainability**: Update methodology document instead of modifying code
- **Auditability**: Clear link between process and implementation
- **Validation**: Code can enforce mandatory rules automatically

**Examples of Code Referencing Methodology**:

**Example 1: Enforcing "Spec Before Estimate" (Section 2.4)**
```python
class ProjectManager:
    def __init__(self):
        # Load methodology document
        self.methodology = self.load_methodology_doc()
        self.mandatory_rules = self.parse_mandatory_rules()

    def estimate_delivery(self, user_story_id: str) -> str:
        """Provide delivery estimate for a user story"""

        # Check Section 2.4 rule: spec must exist before estimate
        if not self.has_technical_spec(user_story_id):
            # Mandatory rule enforcement (from Section 2.4)
            return (
                "I need to create a technical specification first to give "
                "you an accurate estimate.\n\n"
                "Without a detailed spec with task-level breakdown, any "
                "estimate would be a guess and could be off by 2-3x.\n\n"
                "Should I proceed with creating the spec?"
            )

        # Spec exists, can provide estimate
        spec = self.load_technical_spec(user_story_id)
        total_hours = self.calculate_total_hours(spec)
        return f"Estimated delivery: {total_hours / 8:.1f} days"
```

**Example 2: Progress Reporting Format (Section 4.4)**
```python
class StatusReportGenerator:
    def __init__(self):
        # Load methodology Section 4.4 for report format
        self.methodology = self.load_methodology_doc()
        self.report_format = self.get_section("4.4")

    def generate_progress_report(self) -> str:
        """Generate progress report following Section 4.4 format"""

        # Use format from Section 4.4
        report = f"""📊 Daily Progress Report ({date.today()})

✅ Completed:
{self.format_completed_items()}

🔄 In Progress:
{self.format_in_progress_items()}

⏸️ Blocked:
{self.format_blocked_items()}

📋 Next Steps:
{self.format_next_steps()}

⏰ ETA: {self.calculate_eta()}
"""
        return report
```

**Example 3: User Story Validation (US-017 requirement)**
```python
class SummaryCalendarGenerator:
    def __init__(self):
        # Load methodology document
        self.methodology = self.load_methodology_doc()

    def generate_summary(self, days: int = 14) -> str:
        """Generate recent completions summary

        References Section 4.4 (Progress Reporting) and US-017
        for format requirements.
        """

        completions = self.get_recent_completions(days)

        # Follow executive summary format (US-017)
        summary = f"📊 Recent Completions (Last {days} Days)\n\n"

        for story in completions:
            # Format per US-017 spec: business value + key features
            summary += f"""✅ {story.title} ({story.id})
   Completed: {story.completion_date}

   Business Value: {story.business_value}

   Key Features:
{self.format_key_features(story)}

   Impact: {story.impact}

---
"""
        return summary
```

**Example 4: Request Categorization (Section 3.2.1)**
```python
class RequestClassifier:
    def __init__(self):
        # Load Section 3.2.1 classification rules
        self.methodology = self.load_methodology_doc()
        self.classification_rules = self.get_section("3.2.1")

    def categorize_user_input(self, user_input: str) -> str:
        """Categorize user input per Section 3.2.1

        Returns: "feature", "methodology", or "both"
        """

        # Use keywords from Section 3.2.1
        feature_indicators = self.classification_rules["feature_indicators"]
        methodology_indicators = self.classification_rules["methodology_indicators"]

        feature_score = self.calculate_keyword_match(
            user_input, feature_indicators
        )
        methodology_score = self.calculate_keyword_match(
            user_input, methodology_indicators
        )

        # Apply confidence thresholds from Section 3.2.1
        if feature_score > 0.8 and methodology_score < 0.3:
            return "feature"  # Route to ROADMAP.md
        elif methodology_score > 0.8 and feature_score < 0.3:
            return "methodology"  # Route to COLLABORATION_METHODOLOGY.md
        elif feature_score > 0.5 and methodology_score > 0.5:
            return "both"  # Route to both documents
        else:
            return "ambiguous"  # Ask clarifying questions
```

**Implementation Guidelines**:

1. **Load Methodology at Startup**:
   ```python
   # In project_manager initialization
   self.methodology_path = "docs/COLLABORATION_METHODOLOGY.md"
   self.methodology = self.load_and_parse_methodology()
   ```

2. **Parse Mandatory Rules**:
   ```python
   def parse_mandatory_rules(self) -> Dict[str, Any]:
       """Extract all 🚨 MANDATORY RULE 🚨 sections"""
       rules = {}
       for section in self.methodology.sections:
           if "MANDATORY RULE" in section.heading:
               rules[section.id] = section.content
       return rules
   ```

3. **Validate Actions**:
   ```python
   def validate_action(self, action: str, context: Dict) -> bool:
       """Check if action complies with methodology"""
       if action == "provide_estimate":
           # Check Section 2.4 rule
           if not context.get("has_technical_spec"):
               self.refuse_with_reason("Section 2.4")
               return False
       return True
   ```

4. **Generate Reports from Templates**:
   ```python
   def generate_report(self, report_type: str) -> str:
       """Generate report using methodology templates"""
       template = self.methodology.get_template(report_type)
       return template.format(**self.get_report_data())
   ```

**Benefits**:

1. **Automatic Enforcement**: Mandatory rules enforced by code, not manual checks
2. **Consistency**: PM behavior always matches documented methodology
3. **Easy Updates**: Change methodology document → code behavior updates
4. **Auditability**: Trace PM actions back to specific methodology sections
5. **Documentation**: Code references specific sections (e.g., "per Section 2.4")

**See Also**:
- **US-017** in ROADMAP.md for summary/calendar feature that uses this pattern
- **Section 3.2.1** for request categorization implementation
- **Section 2.4** for mandatory spec-before-estimate rule
- **Section 4.4** for progress reporting format

**User Request Context** (2025-10-10):
> "and this document should be referenced by the code, so that project_manager uses it."

This ensures the methodology document is not just documentation, but an **active specification** that drives code behavior.

### 2.8 Documentation and Roadmap Versioning Policy

**User Story**: "As a user I want documentation and roadmap in the branch to always be the most up-to-date version of roadmap and documentation"

**Principle**: Documentation and ROADMAP.md must always reflect the **current, accurate state** of the project. Outdated documentation is worse than no documentation.

**What This Means**:

1. **Every Bug Fix or Feature Update**:
   - Update ROADMAP.md with "Recent Bug Fixes" or "Recent Completions" section
   - Update relevant documentation (QUICKSTART, TUTORIALS, etc.)
   - Update COLLABORATION_METHODOLOGY.md if processes changed
   - All updates committed in the same PR/branch as the code fix

2. **Documentation is Part of Definition of Done**:
   - Code changes without documentation updates are INCOMPLETE
   - Bug fixes must document the problem, solution, and user impact
   - Features must update user guides, API references, troubleshooting
   - Cannot mark task complete until documentation is updated

3. **Living Documents Over Static Docs**:
   - ROADMAP.md: Updated continuously as priorities change
   - COLLABORATION_METHODOLOGY.md: Updated when processes evolve
   - QUICKSTART guides: Updated when user workflows change
   - TUTORIALS: Updated when features change behavior

4. **Version Control Best Practices**:
   - Feature branches include documentation updates
   - Documentation committed alongside code changes
   - PR reviews include documentation review
   - Main branch always has current documentation

**Example: CLI Nesting Fix (2025-10-11)**

When fixing the CLI nesting detection bug in `project-manager chat`:

✅ **Complete Implementation**:
```
Branch: fix/cli-nesting-detection

Commits:
1. fix: Add CLI nesting detection to project-manager chat
   - Code changes in coffee_maker/cli/roadmap_cli.py

2. docs: Document CLI nesting detection fix
   - ROADMAP.md: Added "Recent Bug Fixes" section
   - QUICKSTART_PROJECT_MANAGER.md: Added troubleshooting section
   - COLLABORATION_METHODOLOGY.md: Version 1.8 update
```

❌ **Incomplete** (What NOT to do):
```
Branch: fix/cli-nesting-detection

Commits:
1. fix: Add CLI nesting detection to project-manager chat
   - Only code changes, no documentation
   - User doesn't know bug was fixed
   - No explanation of behavior change
```

**Bug Fix Documentation Template**:

When fixing a bug, document it in ROADMAP.md:
```markdown
**Recent Bug Fixes** (YYYY-MM-DD):
🔧 **[Short Title]**: [2-3 sentence description of problem, solution, and impact]
   - Branch: [branch-name]
   - Files modified: [key files]
   - Impact: [how this affects users]
```

And update relevant user guides with troubleshooting information.

**Why This Matters**:

1. **User Confidence**: Users can trust documentation is current
2. **Knowledge Transfer**: New team members see accurate state
3. **Debugging**: Users can find solutions to known issues
4. **Audit Trail**: Clear history of what changed and why
5. **Professional Standards**: Documentation quality reflects code quality

**See Also**:
- **Section 6.2** - Documentation Criteria in Definition of Done
- **Section 8.3** - Version History of this document
- **US-010** - Living Documentation & Tutorials (completed case study)

---

## 3. Team Structure & Roles

### 3.1 Role: User (Product Owner)

**Overview**: The User acts as the Product Owner - the ultimate decision-maker for what gets built, when, and how it should work. You define requirements, validate implementations, and ensure the product meets your needs.

---

#### 3.1.1 **Responsibilities Matrix** (Enhanced - US-018)

| # | Responsibility | What This Means | Example | Frequency |
|---|---------------|------------------|---------|-----------|
| 1 | **Define Requirements** | Describe what you need in natural language | "I want email notifications when daemon completes tasks" | As needed |
| 2 | **Approve User Stories** | Review and validate PM's structured user stories | Review US-018 specification, approve or request changes | Per feature |
| 3 | **Approve Technical Specs** | Review technical approach before implementation | Approve US-018 technical spec with 6 phases | Per complex feature (>1 day) |
| 4 | **Set Priorities** | Decide what to build first | "Make US-014 TOP PRIORITY, then US-016" | When changes needed |
| 5 | **Validate Implementations** | Test completed features against acceptance criteria | Test `/my-role` command, verify it works as expected | When feature complete |
| 6 | **Provide Feedback** | Give clear feedback on what works and what doesn't | "The feature works but I'd like to add..." | During testing |
| 7 | **Make Product Decisions** | Choose between options when PM presents alternatives | "Option A - enhance existing feature" | When escalated |
| 8 | **Answer Clarifying Questions** | Respond to PM's questions about requirements | Clarify scope, answer "both feature and methodology" | When asked |
| 9 | **Review Documentation** | Validate that documentation is clear and useful | Review enhanced COLLABORATION_METHODOLOGY.md sections | Per deliverable |
| 10 | **Accept/Reject Deliverables** | Final approval before marking features complete | "Yes, US-018 meets all acceptance criteria - approve" | Per deliverable |

---

#### 3.1.2 **Authority Matrix** (What You Can Decide vs Must Delegate)

**🟢 YOU DECIDE** (No approval needed):

| Decision Type | Examples | When to Use |
|--------------|----------|-------------|
| **Product Features** | Add email notifications, remove unused feature | Anytime |
| **Priorities** | Make US-016 next priority, pause US-017 | Anytime |
| **Acceptance Criteria** | "Feature must respond in <1 second" | During user story creation |
| **Business Requirements** | "Must support 1000 concurrent users" | During spec approval |
| **Feature Scope Changes** | "Add OAuth to authentication feature" | During implementation (ideally early) |
| **Deliverable Acceptance** | Approve feature, request changes, reject | After testing |
| **Budget/Timeline Trade-offs** | "Cut feature X to ship faster" | When PM presents options |

**🔴 YOU MUST DELEGATE** (Let PM/Developer decide):

| Decision Type | Examples | Who Decides | Why |
|--------------|----------|-------------|-----|
| **Technical Implementation** | Use SQLite vs PostgreSQL | Developer → PM → You (if escalated) | Technical expertise required |
| **Code Structure** | Class names, file organization | Developer | Implementation detail |
| **Testing Approach** | pytest vs unittest | Developer/PM | Technical decision |
| **Documentation Format** | Markdown vs reStructuredText | PM | Process decision |
| **Commit Message Format** | Conventional commits vs free-form | PM | Team standard |

**⚠️ CONSULT BEFORE DECIDING** (Get PM input first):

| Decision Type | Why Consult | Example |
|--------------|-------------|---------|
| **Major Scope Changes** | Impact on timeline/resources | "Let's add 5 more features to current user story" |
| **Technical Constraints** | May not be feasible | "Must work offline with no internet" |
| **Priority Changes Mid-Implementation** | Wastes work already done | Changing priority when 50% complete |
| **Relaxing Quality Standards** | May cause technical debt | "Skip tests for this feature" |

---

#### 3.1.3 **Workflow Diagrams** (Common Scenarios)

**Scenario 1: Adding a New Feature**

```
[1] User: "I want feature X"
     ↓
[2] PM: Asks clarifying questions
     • What should it do?
     • Who will use it?
     • What's the success criteria?
     ↓
[1] User: Answers questions
     ↓
[2] PM: Creates user story in ROADMAP.md
     • Structured format
     • Estimated effort
     • Acceptance criteria
     ↓
[1] User: Reviews user story
     ├─ Approve → Continue
     └─ Request changes → PM updates → Re-review
          ↓
[2] PM: Creates technical spec (if >1 day work)
     • Phases
     • Tasks with time estimates
     • Architecture
     ↓
[1] User: Reviews technical spec
     ├─ Approve → PM marks TOP PRIORITY
     └─ Request changes → PM updates → Re-review
          ↓
[3] Developer: Implements feature
     ↓
[2] PM: Validates against DoD
     ↓
[1] User: Tests feature
     ├─ Approve → PM marks ✅ Complete
     └─ Request changes → Back to Developer
```

**Scenario 2: Changing Priorities**

```
[1] User: "I want to change priorities"
     ↓
[2] PM: Shows current priorities and impact
     • Current: US-014 (3 days remaining)
     • Next: US-016, US-015, US-017
     • Changing now will:
       - Pause current work (waste 2 days)
       - Delay delivery by 1 week
     ↓
[1] User: Makes decision
     ├─ Option A: "Finish US-014 first" → No change
     ├─ Option B: "Pause US-014, start US-015" → PM updates ROADMAP
     └─ Option C: "Add new urgent feature" → PM creates new TOP PRIORITY
          ↓
[2] PM: Updates ROADMAP.md with new priorities
     ↓
[3] Developer: Reads updated ROADMAP, switches to new TOP PRIORITY
```

**Scenario 3: Responding to Daemon Question**

```
[3] Developer (via notification): "Question: Use SQLite or PostgreSQL?"
     ↓
[2] PM: Receives question, analyzes
     ├─ Can PM answer? (technical decision with clear precedent)
     │    └─ Yes → PM responds directly
     ├─ Needs user input? (product/business decision)
     │    ↓
     │   [2] PM: Escalates to user with context
     │        • What the question is
     │        • Options (A, B, C)
     │        • PM's recommendation
     │        • Impact on timeline/quality
     │    ↓
     │   [1] User: Provides decision
     │        ↓
     │   [2] PM: Relays to Developer via notification
     └─ [3] Developer: Continues work
```

**Scenario 4: Validating Completed Feature**

```
[3] Developer: Marks feature complete, creates notification
     ↓
[2] PM: Validates against DoD checklist
     • All acceptance criteria met?
     • Tests passing?
     • Documentation updated?
     ├─ No → PM reports missing items to Developer
     └─ Yes ↓
          [2] PM: Notifies User for validation
               "US-018 is complete. Ready for testing."
          ↓
          [1] User: Tests feature
               ├─ Test `/my-role` command
               ├─ Test `/help` command
               ├─ Test `/what-next` command
               ├─ Review enhanced methodology sections
               └─ Verify all acceptance criteria met
          ↓
          [1] User: Provides feedback
               ├─ Option A: "Approve - all good" → PM marks ✅ Complete
               ├─ Option B: "Minor changes needed" → List changes → Developer fixes
               └─ Option C: "Major issues" → Detailed feedback → Developer reworks
```

---

#### 3.1.4 **Communication Protocol** (How to Work with PM)

**When You Need Something**:

1. **Describe Your Need in Natural Language**
   - ✅ GOOD: "I want email notifications when daemon completes tasks"
   - ✅ GOOD: "I need to know what my responsibilities are"
   - ✅ GOOD: "Make feature X the top priority"
   - ❌ AVOID: Technical jargon (unless you're technical)

2. **Answer PM's Clarifying Questions Promptly**
   - PM will ask 3-6 questions to understand scope
   - Answer all questions in one message if possible
   - If unsure, say "I don't know yet" - PM will help you figure it out

3. **Review Proposals Thoroughly**
   - User stories (structure of what will be built)
   - Technical specs (how it will be built)
   - Take time to review - don't rush approval

4. **Provide Clear Feedback**
   - ✅ GOOD: "The feature works but email should include PR link"
   - ✅ GOOD: "Approve - meets all my needs"
   - ❌ AVOID: Vague feedback like "something feels off"

5. **Use Commands When Helpful** (US-018)
   - `/my-role` - See your responsibilities and authorities
   - `/help [topic]` - Get guidance on specific topics
   - `/what-next` - See suggested next actions

**What Information to Provide**:

| When PM Asks... | Provide... | Example |
|-----------------|------------|---------|
| "What should this feature do?" | Concrete examples | "Send email with task name, status, PR link, and completion time" |
| "Who will use this?" | User personas/roles | "Me (product owner) and other developers on the team" |
| "What's the success criteria?" | How you'll know it works | "I receive email within 1 minute of daemon completing task" |
| "Any constraints?" | Technical/business limits | "Must work with our existing email system (Gmail)" |
| "How important is this?" | Priority relative to other work | "Critical - blocks my workflow" OR "Nice to have - not urgent" |

**Response Times** (Guidelines):

| Type of Request | Expected Response Time | Why |
|-----------------|------------------------|-----|
| **Urgent Blocker** | <2 hours | Developer is blocked, waiting |
| **Spec Approval** | <1 business day | Delays implementation |
| **Feature Validation** | <2 business days | Delays completion |
| **Clarifying Questions** | <1 business day | PM can't proceed without |
| **Priority Changes** | Anytime (no deadline) | You decide when |

---

#### 3.1.5 **Success Criteria** (How to Know You're Effective)

**✅ You're Doing Great If**:

1. **Requirements Are Clear**
   - PM rarely asks "What did you mean by..."
   - User stories match your intent on first try
   - Developers rarely come back with clarifying questions

2. **Priorities Are Stable**
   - Top priority stays consistent for 3-5 days
   - Few mid-stream priority changes
   - Work flows smoothly without interruptions

3. **Acceptance Criteria Are Met**
   - Features work as you expected
   - Rare surprises when testing ("This isn't what I wanted")
   - 90%+ of features approved on first validation

4. **Response Times Are Good**
   - You respond to PM questions within 1 business day
   - Spec approvals happen within 24 hours
   - Daemon doesn't wait >2 days for decisions

5. **Feedback Is Actionable**
   - Developers know exactly what to change
   - Few back-and-forth iterations
   - Features improve with each iteration

6. **Team Velocity Is High**
   - 1-2 user stories completed per week
   - Minimal wasted work
   - Steady progress toward goals

**❌ Warning Signs** (Areas to Improve):

1. **Unclear Requirements**
   - PM asks 10+ clarifying questions per feature
   - User stories require multiple revisions
   - Developers frequently ask "What did you mean?"

2. **Priority Churn**
   - Priorities change every 1-2 days
   - Developer context-switches frequently
   - Work gets abandoned mid-stream

3. **Acceptance Rejection**
   - <70% of features approved on first try
   - Frequent "This isn't what I wanted"
   - Lots of rework required

4. **Slow Response Times**
   - PM waits 3+ days for answers
   - Specs sit unapproved for a week
   - Daemon is idle waiting for decisions

5. **Vague Feedback**
   - "Something's not right but I can't say what"
   - Developer doesn't know what to change
   - Multiple iterations with no progress

**📊 Metrics to Track** (Optional):

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Feature Approval Rate** | >85% first-try approval | Features approved / Features validated |
| **Average Response Time** | <1 business day | Time from PM question to your answer |
| **Priority Stability** | >3 days | Average time TOP PRIORITY stays unchanged |
| **Clarifying Questions** | <5 per feature | Questions PM asks per user story |
| **Rework Rate** | <15% | Features requiring changes / Total features |

---

#### 3.1.6 **Example Interactions** (Expanded Scenarios)

**Example 1: Adding a New Feature (Simple)**
```
User: "I want email notifications when daemon completes tasks"

PM: "Got it! Some questions to clarify scope:
     1. What should the email include? (task name, status, results, PR link?)
     2. Who should receive emails? (you only, or other team members?)
     3. When should emails be sent? (only on success, or also on failure?)
     4. Any preferences for email format? (plain text, HTML, both?)
     5. Should users be able to configure this? (enable/disable, frequency?)"

User: "1. task name, status, PR link, completion time
       2. me only for now
       3. both success and failure
       4. HTML preferred
       5. yes - let me enable/disable per task type"

PM: "Perfect! I'll create US-019:

     **Email Notifications for Task Completion**

     Scope:
     - Send HTML email on task completion (success/failure)
     - Include: task name, status, PR link, completion time
     - User can configure: enable/disable per task type
     - Email sent to user's configured address

     Estimated: 3-4 days

     Acceptance Criteria:
     - [ ] Email sent within 1 minute of task completion
     - [ ] Email includes all 4 required fields
     - [ ] User can enable/disable per task type
     - [ ] Both success and failure emails work
     - [ ] HTML format with readable styling

     Does this match what you want?"

User: "Yes, perfect"

PM: "Added to ROADMAP. Where should I prioritize it?
     - TOP PRIORITY (implement immediately)
     - After US-016 (next in queue)
     - Backlog (future)"

User: "After US-016"

PM: "Done! It's now scheduled after the technical spec generation feature."
```

**Example 2: Changing Priorities Mid-Stream**
```
User: "I want to pause US-014 and work on email notifications instead"

PM: "I understand you want to prioritize email notifications.

     Current situation:
     - US-014 (Request Categorization) is 60% complete (Day 2 of 3-5)
     - 3 of 5 phases implemented
     - 2-3 days remaining to finish

     Impact of changing now:
     - 2 days of work on US-014 will pause (not wasted, but delayed)
     - Email notifications will take 3-4 days
     - US-014 completion delayed by 3-4 days total
     - Overall delivery: Same timeline, different order

     Options:
     A) Finish US-014 first (2-3 days), then email notifications (3-4 days)
        Total: 5-7 days for both features
     B) Pause US-014 now, do email first (3-4 days), resume US-014 (2-3 days)
        Total: 5-7 days for both features, but context-switch overhead

     My recommendation: Option A (finish US-014 first)
     Reason: Avoid context-switch overhead, cleaner workflow

     What would you like to do?"

User: "You're right, finish US-014 first"

PM: "Great! US-014 remains TOP PRIORITY. I'll add email notifications as the
     next priority after US-014 completes."
```

**Example 3: Validating a Completed Feature**
```
PM: "US-018 (Role Clarity System) is complete and ready for validation!

     What was implemented:
     - `/my-role` command (shows your responsibilities)
     - `/help [topic]` command (context-aware help)
     - `/what-next` command (suggests next actions)
     - Enhanced methodology sections 3.1, 3.2, 3.3
     - Responsibility matrices and workflow diagrams

     All 12 acceptance criteria met ✅

     Please test:
     1. Try `/my-role` - does it clearly show your role?
     2. Try `/help` - does it provide useful guidance?
     3. Try `/what-next` - are suggestions actionable?
     4. Review enhanced COLLABORATION_METHODOLOGY.md sections 3.1-3.3
     5. Confirm: 'I now know what I should and can do'

     Let me know when you've tested!"

User: [Tests all commands and reviews documentation]

User: "Tested all commands - they work great! The `/my-role` command is
       especially helpful. The enhanced methodology sections are much clearer.

       One small thing: Can the `/what-next` command show estimated time for
       each suggestion?"

PM: "Great feedback! Yes, I can add estimated time to suggestions.

     This is a small change (~30 minutes). Options:
     A) Add it now before marking US-018 complete
     B) Create US-018.1 for this enhancement

     Recommendation: Option A (add it now - keeps feature complete)

     Approve?"

User: "Do A"

PM: "Added to US-018 Phase 3. Developer will implement today.
     I'll notify you when ready for re-validation."

[30 minutes later]

PM: "Updated `/what-next` command now shows estimated time per suggestion.
     Please re-test!"

User: [Tests] "Perfect! Approve US-018"

PM: "✅ Marked US-018 complete in ROADMAP. Next priority: US-016"
```

**Example 4: Responding to a Daemon Question**
```
PM: "The daemon has a question that needs your input:

     **Question**: Should the `/my-role` command show different information
                  for different roles (User, PM, Developer)?

     **Context**: Currently implementing role detection. Developer wants to know
                 if each role should see role-specific content or generic content.

     **Options**:
     A) Role-specific content (User sees User responsibilities, PM sees PM responsibilities)
        - Pro: More relevant, less cognitive load
        - Con: Slightly more complex, takes +1 hour
     B) Generic content (everyone sees all 3 roles)
        - Pro: Simpler, faster to implement
        - Con: More information to parse, less focused

     **Developer's Recommendation**: Option A (role-specific)
     **Reason**: Better UX, worth the extra hour

     **Impact**: +1 hour if Option A, no impact if Option B

     What would you like?"

User: "Option A - I agree role-specific is better"

PM: "Got it! I've relayed your decision to the developer.
     The `/my-role` command will show role-specific content.
     Estimated completion: today"
```

**Example 5: Using Commands for Guidance (US-018)**
```
User: "/my-role"

PM: "🎯 Your Role: User (Product Owner)

     📋 Key Responsibilities (10):
     1. Define requirements in natural language
     2. Approve user stories and technical specs
     3. Set and change priorities
     4. Validate completed implementations
     5. Provide clear, actionable feedback
     6. Answer clarifying questions promptly
     7. Make product decisions
     8. Review and approve documentation
     9. Test features against acceptance criteria
     10. Accept or reject final deliverables

     ⚡ Your Authorities (YOU DECIDE):
     • All product features and priorities
     • All acceptance criteria and business requirements
     • Feature scope changes (ideally early)
     • Deliverable acceptance (approve/reject)
     • Budget and timeline trade-offs

     ⚠️ You Must Delegate (LET TEAM DECIDE):
     • Technical implementation details
     • Code structure and organization
     • Testing approaches
     • Documentation format
     • Commit message conventions

     ⭐ Success Criteria:
     • Requirements are clear (few clarifying questions)
     • Priorities are stable (>3 days per priority)
     • 85%+ features approved first-try
     • Response time <1 business day
     • Feedback is actionable

     📖 Learn More: COLLABORATION_METHODOLOGY.md Section 3.1
     💡 Need help? Type `/help` or `/what-next`"

User: "/what-next"

PM: "📋 Suggested Next Actions (Your Role: Product Owner)

     1. ⭐ HIGH PRIORITY: Review US-018 technical spec
        Rationale: Developer is waiting for your approval to start
        Time: 20-25 minutes
        Action: Read docs/US-018_TECHNICAL_SPEC.md and approve
        Why now: Blocking developer's progress

     2. ✅ VALIDATION: Test completed US-017 feature
        Rationale: Feature marked complete, needs user validation
        Time: 15 minutes
        Action: Test `/summary` and `/calendar` commands
        Why now: Finalize completion of US-017

     3. 📝 PLANNING: Decide on US-019 priority
        Rationale: Email notifications feature is defined, needs prioritization
        Time: 5 minutes
        Action: Choose: TOP PRIORITY, After US-016, or Backlog
        Why now: Clarifies roadmap for next 2 weeks

     My recommendation: Start with #1 (unblock developer), then #2 (validate US-017)

     Want details? Ask 'Why #1?' or 'Tell me more about #2'"
```

---

#### 3.1.7 **Related Methodology Sections**

- **Section 2.3** - Roadmap as Single Source of Truth (your priorities are documented here)
- **Section 2.4** - Specification Before Implementation (what you approve before coding)
- **Section 3.4** - Team Dynamics (how decisions flow through the team)
- **Section 4.1** - Synchronous Communication (how you talk to PM)
- **Section 5.1** - Adding a New User Story (workflow for your feature requests)
- **Section 5.3** - Implementing a Priority (what happens after you approve)
- **Section 6.1** - Definition of Done (what you validate before accepting)
- **Section 7.1** - Who Decides What (complete decision matrix)

**See Also**:
- **US-018** in ROADMAP.md for role clarity commands (`/my-role`, `/help`, `/what-next`)
- **Section 11.1** - Roles Cheat Sheet (quick reference)

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
- **Use plain language, NOT technical shorthand** (Section 4.6)

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

#### 3.2.1 Request Categorization and Document Routing (US-014)

**🚨 MANDATORY PRACTICE 🚨**

**Principle**: PM must intelligently categorize user input and route information to the correct documents.

**Why This Matters**:
- Feature requests belong in `ROADMAP.md` (what to build)
- Process/methodology changes belong in `COLLABORATION_METHODOLOGY.md` (how we work)
- Some requests affect both documents
- Misrouting leads to lost information or confused documentation

**Three Categories of User Input**:

1. **Feature Request** → Route to `ROADMAP.md`
   - Keywords: "I want", "add feature", "build", "implement", "create"
   - Intent: Something to build/develop
   - Action: Create user story in roadmap

2. **Methodology Change** → Route to `COLLABORATION_METHODOLOGY.md`
   - Keywords: "PM should", "always do", "process", "workflow", "methodology", "team should"
   - Intent: Change how team works
   - Action: Update methodology document

3. **Both** → Route to both documents
   - Keywords: "PM needs capability to", "PM should be able to"
   - Intent: Build feature AND change process
   - Action: Create user story + update methodology

**PM Workflow**:

**Step 1: Analyze user input**
```
User: "I want email notifications"
→ Classification: FEATURE REQUEST
→ Confidence: HIGH (90%)
→ Action: Route to ROADMAP.md
```

**Step 2: Ask clarifying questions if ambiguous (confidence < 80%)**
```
User: "I need better documentation"

PM: "I want to make sure I understand correctly.

Is this:
A) A feature request to auto-generate documentation (→ ROADMAP.md)?
B) A process change for how I should document things (→ COLLABORATION_METHODOLOGY.md)?
C) Both - build auto-doc feature AND change documentation process?

Understanding this helps me know which documents to update."
```

**Step 3: Explicitly state which documents will be updated**
```
PM: "Got it! This is a feature request, so I'll:
1. Create a user story in ROADMAP.md
2. Document it as the email notifications feature

Proceeding..."
```

**Examples**:

**Example 1: Clear Feature Request**
```
User: "I want the daemon to send me Slack messages when tasks complete"

PM Analysis:
- Type: FEATURE REQUEST
- Confidence: 95%
- Reasoning: "I want" + specific functionality to build

PM Response:
"I've detected this as a feature request.

I'll create a user story in ROADMAP.md for Slack notifications.

Proceeding with user story creation..."
```

**Example 2: Clear Methodology Change**
```
User: "PM should always confirm which documents will be updated before making changes"

PM Analysis:
- Type: METHODOLOGY CHANGE
- Confidence: 98%
- Reasoning: "PM should" + describes process behavior

PM Response:
"I've detected this as a methodology change.

I'll update COLLABORATION_METHODOLOGY.md Section 3.2.1 to require:
- Explicit document routing statements
- Confirmation before updates

Proceeding with methodology update..."
```

**Example 3: Hybrid (Both)**
```
User: "PM needs to be able to detect when I'm describing a feature vs a methodology change"

PM Analysis:
- Type: BOTH
- Confidence: 92%
- Reasoning: "PM needs capability" = build feature + "PM should behave this way" = process

PM Response:
"I've detected this affects both feature development and methodology.

I'll:
1. Create user story in ROADMAP.md for request categorization capability (US-014)
2. Update COLLABORATION_METHODOLOGY.md Section 3.2.1 with categorization process
3. Cross-reference the two documents

Proceeding..."
```

**Example 4: Ambiguous (Requires Clarification)**
```
User: "I need status updates"

PM Analysis:
- Type: AMBIGUOUS
- Confidence: 45%
- Reasoning: Could mean build feature OR change report format

PM Response:
"I want to make sure I understand correctly.

Is this:
A) A feature request - build automated status reports (→ ROADMAP.md)?
B) A process change - different format for my status messages (→ COLLABORATION_METHODOLOGY.md)?
C) Both?

This helps me know which documents to update."

User: "A - build the feature"

PM: "Perfect! I'll create a user story in ROADMAP.md for automated status reports.

Proceeding..."
```

**Classification Keywords**:

**Feature Indicators**:
- "I want", "I need", "add", "build", "implement", "create"
- "feature", "functionality", "capability" (when referring to software)
- Describes specific output or behavior to implement

**Methodology Indicators**:
- "PM should", "always", "never", "must", "process", "workflow"
- "methodology", "how we work", "team practice"
- Describes behavioral rules or team practices

**Both Indicators**:
- "PM needs to be able to" (implies building + behavior)
- "PM should have capability to" (build + process)
- Explicitly mentions affecting multiple documents

**Confidence Thresholds**:
- **> 80%**: Proceed with routing automatically
- **50-80%**: Lean toward classification but mention it: "I've detected this as X, let me know if I misunderstood"
- **< 50%**: Ask clarifying questions before proceeding

**Why This Rule Was Added**:
User feedback 2025-10-10: "As a project manager, I need to be able to interpret the user's context: what part of what he is saying are user stories, and what parts concerns the collaboration methodologies, or both. I can ask him to make sure I understood as I need to get sure which documents should be updated (roadmap, collaboration methodology, etc)"

This ensures information is routed correctly and nothing gets lost or misplaced.

**See Also**:
- US-014 in ROADMAP.md for complete feature specification
- Section 4.5 for documenting feature discussions
- Section 5.2 for `/US` command workflow

---

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

### 4.6 Plain Language Communication (No Technical Shorthand)

**🚨 MANDATORY RULE 🚨**

**Principle**: Project Manager must communicate **TO USERS** in **complete sentences and plain language**, NOT technical IDs or shorthand.

**Direction**: This rule applies **PM → User only** (one-way):
- ✅ Users CAN use shorthand ("US-012", "PRIORITY 2", etc.) when talking to PM
- ✅ Team members CAN use shorthand among themselves
- ❌ PM CANNOT use shorthand when talking to users

**Why This Matters**:
- Users don't understand technical references like "US-012" without context
- Plain language ensures everyone understands the conversation
- Reduces cognitive load (user doesn't need to remember what "US-012" means)
- Makes conversations natural and accessible

**What Project Manager MUST Do**:

❌ **DON'T SAY**:
- "US-012 is ready for implementation"
- "I found a conflict with US-008"
- "This relates to PRIORITY 2.5"
- "Similar to US-007 requirements"

✅ **DO SAY**:
- "The feature for natural language user story creation is ready for implementation"
- "I found a conflict with the automated user support feature"
- "This relates to the UX documentation priority"
- "Similar to the IDE code completion requirements"

**How to Reference Features**:
1. **First mention**: Use descriptive name
   - "The `/US` command for creating user stories conversationally"
2. **Subsequent mentions**: Use shortened descriptive name
   - "The `/US` command" or "this feature"
3. **Never**: Use only the technical ID (US-XXX, PRIORITY X)

**Examples**:

**Bad Example** ❌:
```
PM: "I found that US-012 conflicts with US-008. Should I update
     US-008 or create US-013?"
```
User: "I don't understand what US-012 or US-008 are"

**Good Example** ✅:
```
PM: "I found that the natural language user story feature
     conflicts with the automated user support feature.

     Should I:
     A) Update the automated support feature to include this
     B) Create a new separate feature

     For reference:
     - Natural language user story = the /US command we discussed
     - Automated support = helping users with code requests"
```
User: "Ah yes, update the automated support feature"

**When Technical IDs Are OK**:
- In parentheses after the descriptive name: "The email notification feature (US-XXX)"
- In documentation for cross-reference
- When explicitly requested by user
- In commit messages and technical specs

**Why This Rule Was Added**:
User feedback 2025-10-10: "As a user I don't understand things like 'US-012': I need the project_manager to talk to me with complete sentence. He can explicit the user story but not just give its number"

This ensures conversations are natural, accessible, and don't require the user to memorize technical identifiers.

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

### 5.2 Adding a New User Story via `/US` Command (US-012, US-013)

**Pattern**: `/US` command → Similarity check → User story validation → DoD inference → DoD validation → Propagate

**What This Is**:
The `/US` command provides a streamlined, conversational way to create user stories with automatic:
- Similarity detection (avoiding duplicates)
- Status checking (is it already done?)
- Definition of Done inference (PM suggests DoD based on description)
- Collaborative validation (user approves before adding to roadmap)

**Steps**:
1. **User**: Types `/US [description]` in project-manager chat
2. **PM**: Searches for similar existing user stories
3. **PM**: Checks if already shipped or partially done
4. **PM**: Presents findings with options (new, enhance existing, or already done)
5. **User**: Validates the user story structure
6. **PM**: ONLY THEN infers Definition of Done from validated description
7. **PM**: Presents DoD for validation
8. **User**: Validates and refines DoD
9. **PM**: Propagates to ROADMAP.md with complete DoD

**Example**:
```
User: "/US I want email notifications when daemon finishes tasks"

[Step 1-4: Similarity Check & Options]
PM: "I'm checking if this already exists or is similar to something we have...

Found: The process management feature (US-009) includes a notification
system, but no email support.

I see three options:
A) Enhance the process management feature to add email notifications
   (it's already 60% done)
B) Create new user story for email-specific notifications
C) This is complete - email is already working (please test)

Which approach would you prefer?"

User: "Create new user story, separate from process management"

[Step 5: User Story Validation]
PM: "Got it! Here's the user story I've extracted:

**Email Notifications on Task Completion**

**As a**: User
**I want**: Email notifications when code_developer completes tasks
**So that**: I stay informed without checking manually

**Business Value**: ⭐⭐⭐⭐ (High - reduces manual monitoring)
**Estimated Effort**: 3-5 days (email service, templates, config)

Is this user story correct? Any changes?"

User: "Yes, and also when daemon asks questions"

PM: "Updated user story:

**Email & Question Notifications**

**As a**: User
**I want**: Email notifications when code_developer completes tasks OR
asks questions
**So that**: I stay informed and can respond quickly

**Business Value**: ⭐⭐⭐⭐⭐ (Critical - enables async workflow)
**Estimated Effort**: 4-6 days (notification triggers, email templates,
config)

Is this correct?"

User: "Yes"

[Step 6-8: DoD Inference & Validation]
PM: "Now let me infer the Definition of Done...

**Definition of Done** (inferred from your description):
- [ ] Email sent when code_developer completes a task
- [ ] Email sent when code_developer asks a question
- [ ] Email includes task summary and results
- [ ] Email includes question context and link
- [ ] User can configure notification preferences (frequency, types)
- [ ] Email delivered within 1 minute of event
- [ ] Tests verify email sending works
- [ ] Documentation shows how to configure

Does this Definition of Done look good, or do you have different
criteria?"

User: "Add: Email should include link to PR when task completes"

PM: "Updated DoD:
- [ ] Email sent when code_developer completes a task
- [ ] Email includes PR link when task completes ← Added
- [ ] Email sent when code_developer asks a question
- [ ] Email includes task summary and results
- [ ] Email includes question context and link
- [ ] User can configure notification preferences
- [ ] Email delivered within 1 minute of event
- [ ] Tests verify email sending works
- [ ] Documentation shows how to configure

Is this correct now?"

User: "Yes, perfect"

[Step 9: Propagation]
PM: "✅ Added the email and question notifications feature to ROADMAP
with complete Definition of Done.

Where should I prioritize it?
- TOP PRIORITY (implement immediately)
- After current work (next in queue)
- Backlog (future consideration)"

User: "After current work"

PM: "Done! Added after the process management feature in the roadmap."
```

**Key Differences from Manual Workflow (Section 5.1)**:
- **Automatic similarity detection**: Prevents duplicates and identifies related work
- **Status awareness**: Checks if feature already exists or is partially done
- **DoD inference**: PM suggests Definition of Done based on description
- **Two-phase validation**: User story THEN DoD (not simultaneously)
- **Streamlined**: Single command instead of multi-step conversation

**Why This Matters**:
- **Reduces duplication**: Similar user stories are detected before creation
- **Saves time**: PM infers DoD automatically from description
- **Improves quality**: Every user story has complete DoD before implementation
- **Better planning**: User validates US before investing time in DoD discussion
- **Leverages existing work**: Suggests enhancing existing features instead of duplicating

**Implementation Status**:
- 📝 **Planned** (US-012, US-013)
- See `docs/ROADMAP.md` for complete specification
- Estimated: 12-17 hours total implementation time

---

### 5.3 Implementing a Priority

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

### 5.4 Handling Blockers

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

### 5.5 Iterating on Requirements

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

### 5.6 Version Releases

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
| 1.3 | 2025-10-10 | Added Section 4.6 (Plain Language Communication) | PM must use descriptive names, not technical IDs like "US-012" |
| 1.4 | 2025-10-10 | Added Section 5.2 (`/US` Command Workflow) | Document US-012/US-013 features: similarity check, DoD inference, validation workflow |
| 1.5 | 2025-10-10 | Added Section 3.2.1 (Request Categorization and Document Routing) | Implement US-014: PM categorizes user input as feature/methodology/both and routes to correct documents |
| 1.6 | 2025-10-10 | Enhanced Section 2.4 - Specification Before Implementation (US-016) | PM MUST create detailed technical spec with task-level estimates before providing delivery estimates. PM must refuse to estimate without spec. |
| 1.7 | 2025-10-10 | Added Section 2.7 - Code References Methodology Document (US-017) | Code implementing PM and code_developer must read and reference COLLABORATION_METHODOLOGY.md to understand processes, rules, and behavioral requirements. Ensures methodology is active specification driving code behavior. |
| 1.8 | 2025-10-11 | Added Section 2.8 - Documentation and Roadmap Versioning Policy | Documentation and ROADMAP.md must always be up-to-date. Every bug fix or feature must update relevant docs in the same PR. Includes CLI nesting detection fix documentation (fix/cli-nesting-detection branch). User story: "Documentation in branch must always be most up-to-date version." |
| 1.9 | 2025-10-11 | Added Section 9.1.1 - project-manager chat Modes | Documented CLI vs API modes, nesting detection, mode selection logic, user decision matrix. Addresses CLI nesting prevention feature. |
| 2.0 | 2025-10-11 | Added Section 9.3 - Updating Roadmap Branch on GitHub | **MAJOR VERSION**: Complete automated workflow for updating 'roadmap' branch on GitHub using Python script (scripts/merge_roadmap_pr.py). Addresses user stories: "main branch always up to date" and "roadmap branch in github always current so developer can see what to achieve". Includes setup instructions, integration examples for all team members (project_manager, code_developer, assistant), safety guarantees, and error handling. Branch strategy documented. |

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

#### 9.1.1 `project-manager chat` Modes (Added 2025-10-11)

**Overview**: `project-manager chat` supports two operational modes with automatic detection to prevent CLI nesting issues.

**Mode Selection Logic**:

The system automatically chooses the appropriate mode based on the environment:

```python
# Detection logic (coffee_maker/cli/roadmap_cli.py:275)
inside_claude_cli = bool(
    os.environ.get("CLAUDECODE") or
    os.environ.get("CLAUDE_CODE_ENTRYPOINT")
)

if inside_claude_cli:
    # Force API mode to prevent CLI nesting
    use_claude_cli = False
elif has_claude_cli:
    # Use CLI mode (free with subscription)
    use_claude_cli = True
elif has_api_key:
    # Fallback to API mode
    use_claude_cli = False
```

**1. CLI Mode** (Default - Recommended)

**When**: Running from regular terminal (not Claude Code)
**Cost**: Free with Claude subscription
**How**: Uses `claude` CLI executable

```bash
# From regular terminal
cd /path/to/MonolithicCoffeeMakerAgent
poetry run project-manager chat
```

**Advantages**:
- ✅ Free (included with Claude subscription)
- ✅ No API credits needed
- ✅ Same quality as Claude API
- ✅ Recommended for daily use

**2. API Mode** (Requires Credits)

**When**:
- Running inside Claude Code (automatic detection)
- ANTHROPIC_API_KEY is set and no CLI available
- User explicitly configured API mode

**Cost**: Uses Anthropic API credits
**How**: Uses Anthropic Python SDK

```bash
# From Claude Code (automatic API mode)
poetry run project-manager chat

# Or set API key explicitly
export ANTHROPIC_API_KEY='your-key-here'
poetry run project-manager chat
```

**Advantages**:
- ✅ Works inside Claude Code (prevents nesting)
- ✅ Works when Claude CLI not installed
- ⚠️ Requires API credits

**3. CLI Nesting Prevention**

**Problem**: Running `project-manager chat` inside Claude Code would cause CLI nesting (Claude CLI calling Claude CLI), which can lead to unexpected behavior.

**Solution**: Automatic detection via environment variables:
- `CLAUDECODE`: Set by Claude Code
- `CLAUDE_CODE_ENTRYPOINT`: Alternative detection

**Behavior**:
```
Running inside Claude Code:
→ Detects nesting risk
→ Forces API mode
→ Shows clear message to user:
  "ℹ️  Detected: Running inside Claude Code"
  "🔄 Using Anthropic API to avoid CLI nesting"
  "💡 TIP: CLI nesting is not recommended"
```

**User Options**:

| Scenario | Recommendation | Command |
|----------|---------------|---------|
| Daily usage | CLI Mode (free) | Run from regular terminal |
| Inside Claude Code (with API key) | API Mode (costs credits) | Run from Claude Code |
| Inside Claude Code (no API key) | CLI Mode (free) | Run from regular terminal |
| CI/CD pipeline | API Mode | Set ANTHROPIC_API_KEY |

**Error Messages**:

If running inside Claude Code without API key:
```
❌ ERROR: Running inside Claude Code without API key

You're running project-manager chat from within Claude Code.
To avoid CLI nesting, we need to use API mode.

🔧 SOLUTION:
  1. Get your API key from: https://console.anthropic.com/
  2. Set the environment variable:
     export ANTHROPIC_API_KEY='your-api-key-here'
  3. Or add it to your .env file

💡 ALTERNATIVE: Run from a regular terminal (not Claude Code)
```

**Documentation References**:
- **QUICKSTART_PROJECT_MANAGER.md**: Troubleshooting section
- **US-006**: CLI nesting detection feature
- **ROADMAP.md**: Recent Bug Fixes (2025-10-11)

---

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

### 9.3 Updating Roadmap Branch on GitHub

**🚨 CRITICAL PROCESS: For project_manager, code_developer, and assistant 🚨**

**User Stories**:
- "As a user: I always want the main branch to always be up to date as regards to the roadmap"
- "As a developer I need the roadmap to be always up to date in the branch roadmap in github so that I can see what I will achieve"

#### Problem

GitHub has a dedicated `roadmap` branch that must always reflect the current state of `docs/ROADMAP.md` and `docs/COLLABORATION_METHODOLOGY.md`. Team members (project_manager, code_developer, assistant) need to update this branch frequently, but manual PR process creates overhead.

#### When To Use This Process

✅ **ALWAYS use this automated merge process when updating**:
- `docs/ROADMAP.md` - Single source of truth for priorities
- `docs/COLLABORATION_METHODOLOGY.md` - Team processes and methodology
- `docs/*.md` - Any documentation files
- Changes made by project_manager agent
- Changes made by code_developer daemon
- Documentation updates by assistant

❌ **NEVER use this automated merge for**:
- Code changes (`coffee_maker/**/*.py`)
- Dependency changes (`pyproject.toml`)
- Configuration changes (`config.yaml`, `.env`)
- CI/CD changes (`.github/**`)
- Any non-documentation changes

**Why**: Code changes require manual review for quality, security, and correctness. Documentation changes are lower risk and need to stay current for the team to function effectively.

#### Setup (One-Time per Team Member)

Each team member needs a GitHub token to use the automated process:

**1. Create GitHub Personal Access Token**:
```
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "roadmap-automation" (or similar)
4. Select scope: ✅ repo (full control of private repositories)
5. Click "Generate token"
6. Copy token (starts with "ghp_")
```

**2. Set Token in Environment**:
```bash
# Add to .env file (recommended - persistent)
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

# Or export in shell (temporary - current session only)
export GITHUB_TOKEN=ghp_your_token_here
```

**3. Install PyGithub** (if not already installed):
```bash
poetry add PyGithub
```

#### Automated Process Using Script

**Location**: `scripts/merge_roadmap_pr.py`

**Usage**:
```bash
# After making roadmap changes on a feature branch:
git checkout -b feature/roadmap-update-$(date +%Y%m%d-%H%M%S)
git add docs/ROADMAP.md docs/COLLABORATION_METHODOLOGY.md
git commit -m "docs: Update roadmap with latest priorities"
git push -u origin HEAD

# Use automated script to create and merge PR to 'roadmap' branch
python scripts/merge_roadmap_pr.py feature/roadmap-update-YYYYMMDD-HHMMSS --base roadmap

# Output:
# ✅ All changes are in docs/ (2 files)
# ✅ PR created targeting 'roadmap' branch: https://github.com/.../pull/123
# ⏳ Attempting auto-merge...
# ✅ PR merged successfully to 'roadmap'!
# 🎉 Success!
```

**Script Features**:
- ✅ **Validation**: Only merges if ALL changes are in `docs/`
- ✅ **Safety**: Detects merge conflicts, fails if non-doc files changed
- ✅ **Auto-merge**: Automatically merges if safe
- ⚠️ **Fallback**: Outputs PR URL for manual review if auto-merge fails

**Script Options**:
```bash
# Target different branch (default: roadmap)
python scripts/merge_roadmap_pr.py feature/branch-name --base roadmap

# Target main branch instead
python scripts/merge_roadmap_pr.py feature/branch-name --base main

# Create PR but don't auto-merge (manual review)
python scripts/merge_roadmap_pr.py feature/branch-name --no-merge
```

#### Manual Process (Alternative)

If the script is unavailable or you prefer manual control:

```python
from github import Github
import os

# Initialize
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo("Bobain/MonolithicCoffeeMakerAgent")

# Create PR
pr = repo.create_pull(
    title="docs: Update roadmap and documentation",
    body="""## Summary
Automated roadmap update.

## Changes
- Updated ROADMAP.md
- Updated COLLABORATION_METHODOLOGY.md

🤖 Auto-generated via team member
    """,
    head="feature/your-branch",
    base="roadmap"  # Target roadmap branch, not main
)

print(f"✅ PR: {pr.html_url}")

# Auto-merge if safe
if pr.mergeable:
    pr.merge(merge_method="squash")
    print("✅ Merged!")
else:
    print(f"⚠️ Manual review: {pr.html_url}")
```

#### Integration in project_manager

The `project_manager` should use this process automatically when updating roadmap:

```python
# In coffee_maker/cli/roadmap_editor.py

def save_and_update_main(self):
    """Save roadmap changes and update main branch automatically."""
    import subprocess
    from datetime import datetime

    # Create timestamped branch
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    branch = f"roadmap-update-{timestamp}"

    # Commit and push
    subprocess.run(["git", "checkout", "-b", branch])
    subprocess.run(["git", "add", "docs/ROADMAP.md", "docs/COLLABORATION_METHODOLOGY.md"])
    subprocess.run(["git", "commit", "-m", "docs: Update roadmap"])
    subprocess.run(["git", "push", "-u", "origin", branch])

    # Auto-merge via script to 'roadmap' branch
    result = subprocess.run(
        ["python", "scripts/merge_roadmap_pr.py", branch, "--base", "roadmap"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Roadmap updated on GitHub 'roadmap' branch!")
        # Clean up
        subprocess.run(["git", "checkout", "main"])
        subprocess.run(["git", "pull", "origin", "roadmap"])  # Sync local roadmap branch
        subprocess.run(["git", "branch", "-d", branch])
    else:
        print(f"⚠️ Manual review needed:\n{result.stdout}")
```

#### Integration in code_developer

The `code_developer` daemon should use this when completing features that update roadmap:

```python
# In coffee_maker/autonomous/daemon.py

def update_roadmap_status(self, priority_name: str, new_status: str):
    """Update priority status in roadmap and push to main."""
    # Update roadmap
    self.parser.update_priority_status(priority_name, new_status)

    # Use automated script
    branch = f"roadmap-{priority_name.lower().replace(' ', '-')}-{new_status}"
    subprocess.run(["git", "checkout", "-b", branch])
    subprocess.run(["git", "add", "docs/ROADMAP.md"])
    subprocess.run(["git", "commit", "-m", f"docs: Mark {priority_name} as {new_status}"])
    subprocess.run(["git", "push", "-u", "origin", branch])

    # Auto-merge to roadmap branch
    subprocess.run(["python", "scripts/merge_roadmap_pr.py", branch, "--base", "roadmap"])
```

#### Integration for assistant

When assistant helps user update roadmap:

```python
# In assistant workflow

def help_update_roadmap(user_changes: str):
    """Help user update roadmap and sync to main."""
    print("I'll update the roadmap and sync it to main for you.")

    # Make changes to ROADMAP.md
    # ... (update logic here)

    # Use automated process
    print("📝 Creating automated PR...")
    branch = f"roadmap-user-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    subprocess.run(["git", "checkout", "-b", branch])
    subprocess.run(["git", "add", "docs/ROADMAP.md"])
    subprocess.run(["git", "commit", "-m", "docs: User-requested roadmap update"])
    subprocess.run(["git", "push", "-u", "origin", branch])
    subprocess.run(["python", "scripts/merge_roadmap_pr.py", branch, "--base", "roadmap"])

    print("✅ Roadmap is now up-to-date on GitHub 'roadmap' branch!")
```

#### Safety Guarantees

The automated script includes these safety checks:

1. ✅ **Documentation-only validation**: Fails if ANY non-docs/ file is changed
2. ✅ **Conflict detection**: Fails if branch has merge conflicts with main
3. ✅ **Branch protection respect**: Works within GitHub's protection rules
4. ⚠️ **Manual fallback**: If unsafe, provides PR URL for manual review
5. ✅ **Audit trail**: All changes tracked in PR history

#### Error Handling

**If script fails**:
```
❌ Non-documentation files detected: coffee_maker/cli/roadmap_cli.py

⚠️  This script is ONLY for docs/ updates!
```

**Solution**: Create separate PRs - one for docs, one for code.

**If merge blocked**:
```
⚠️  PR has merge conflicts - manual review required
   Please review and merge manually: https://github.com/.../pull/123
```

**Solution**: Manually resolve conflicts on GitHub or locally.

#### Example Complete Workflow

```bash
# 1. project_manager updates roadmap during chat
$ poetry run project-manager chat
You: Mark US-020 as complete
Claude: ✅ Updated ROADMAP.md to mark US-020 complete
        📝 Creating automated PR to 'roadmap' branch...
        ✅ PR created: https://github.com/.../pull/124
        ✅ PR merged successfully to 'roadmap'!
        🎉 Roadmap branch is now current!

# 2. Verify roadmap branch is updated
$ git fetch origin roadmap
$ git checkout roadmap
$ git pull origin roadmap
From github.com:Bobain/MonolithicCoffeeMakerAgent
 * branch            main       -> FETCH_HEAD
Updating abc1234..def5678
Fast-forward
 docs/ROADMAP.md | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

# 3. View updated roadmap
$ cat docs/ROADMAP.md
# Shows US-020 marked as ✅ Complete

# 4. Continue working on main
$ git checkout main
```

#### Verification

After automated merge, verify `roadmap` branch is current:

```bash
# Check latest commit on roadmap branch
git log origin/roadmap -1 --oneline

# Should show your roadmap update commit
# Example: abc1234 docs: Update roadmap with US-020 completion

# View roadmap on GitHub
# https://github.com/Bobain/MonolithicCoffeeMakerAgent/tree/roadmap/docs
```

#### Branch Strategy

- **`main` branch**: Stable production code + documentation
- **`roadmap` branch**: Always current roadmap and methodology docs
  - Updated frequently by team members
  - Reflects latest planning and priorities
  - Used by developer to see what to achieve next
- **Feature branches**: Individual changes (merged to roadmap for docs, to main for code)

**Why separate roadmap branch?**
- ✅ Roadmap updates don't trigger CI/CD pipelines on main
- ✅ Developers can easily view current roadmap without switching to feature branches
- ✅ Clear separation: `roadmap` = planning, `main` = implementation
- ✅ Roadmap can be updated without affecting stable main branch

```

#### Documentation References

- **Script**: `scripts/merge_roadmap_pr.py` (implementation)
- **Contributing Guide**: `CONTRIBUTING.md` (external contributor process)
- **Section 2.8**: Documentation Versioning Policy (why this matters)

---

### 9.4 File Organization

```
MonolithicCoffeeMakerAgent/
├── docs/
│   ├── ROADMAP.md                    # Single source of truth
│   ├── COLLABORATION_METHODOLOGY.md  # This document
│   ├── US-XXX_TECHNICAL_SPEC.md      # User story specs
│   ├── ADR-XXX_[decision].md         # Architecture decisions
│   └── CHANGELOG_YYYY_MM_DD_[topic].md # Change logs
├── scripts/
│   └── merge_roadmap_pr.py           # Automated PR merge for roadmap
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
