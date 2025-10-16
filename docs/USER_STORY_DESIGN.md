# User Story Integration Design

**Version**: 1.0
**Date**: 2025-10-10
**Status**: Design Phase

## 1. Overview

### 1.1 Purpose

Enable the roadmap to manage User Stories as first-class entities, allowing users to:
- Communicate needs through User Stories (not just technical priorities)
- Collaboratively prioritize User Stories with project_manager
- Understand roadmap impact before committing to changes
- Work at a user-centric level rather than technical project level

### 1.2 Key Principles

1. **User-Centric Communication**: Users think in terms of "I want to..." not "Implement system X"
2. **Collaborative Prioritization**: project_manager analyzes and discusses, doesn't dictate
3. **Transparent Impact**: Show how User Stories affect existing roadmap
4. **Natural Dialog**: Ask "Story A or Story B?" not "Project X or Project Y?"
5. **Flexible Assignment**: User Stories can map to existing priorities or create new ones

### 1.3 User Story Definition

A User Story follows the format:
```
As a [role/persona]
I want [feature/capability]
So that [benefit/value]
```

Examples:
- "As a developer, I want to deploy code_developer on GCP so that it runs 24/7"
- "As a project manager, I want to see priority health scores so that I can identify risks"
- "As a user, I want CSV export so that I can analyze data in Excel"

---

## 2. Data Model

### 2.1 User Story Structure

```markdown
### 🎯 [US-XXX] User Story Title

**As a**: [role/persona]
**I want**: [feature description]
**So that**: [benefit/value proposition]

**Business Value**: ⭐⭐⭐⭐⭐ (1-5 stars)
**Estimated Effort**: [Story Points: 1, 2, 3, 5, 8, 13 | or Time: 1-2 days]
**Priority Score**: [High/Medium/Low - calculated from value/effort ratio]
**Status**: 📝 Backlog | 🔄 In Discussion | 📋 Ready | ✅ Assigned to PRIORITY X | 🚀 In Progress | ✅ Complete

**Acceptance Criteria**:
- [ ] Criterion 1: Specific, testable condition
- [ ] Criterion 2: Another measurable outcome
- [ ] Criterion 3: User-visible result

**Technical Notes**:
- Implementation hints
- Dependencies
- Constraints

**Assigned To**: PRIORITY X (if assigned)
**Related Stories**: US-YYY, US-ZZZ (if related)
**Discussion History**:
- [2025-10-10] User: "I need this for quarterly reporting"
- [2025-10-10] PM: "Would real-time export work, or scheduled daily?"
- [2025-10-10] User: "Scheduled daily is perfect"

---
```

### 2.2 Roadmap Structure with User Stories

```markdown
# Coffee Maker Agent - Prioritized Roadmap

[... existing header ...]

---

## 📋 USER STORY BACKLOG

> **What is this section?**
> This is where user needs are captured before being translated into technical priorities.
> User Stories help us understand WHAT users need and WHY, before deciding HOW to implement.

### Backlog Statistics
- **Total Stories**: 15
- **Backlog**: 8
- **In Discussion**: 3
- **Ready**: 2
- **Assigned**: 2
- **Complete**: 0

### Story Prioritization Notes
> User Stories are prioritized collaboratively with the user based on:
> 1. **Business Value**: How important is this to the user?
> 2. **Estimated Effort**: How complex is the implementation?
> 3. **Dependencies**: What must be done first?
> 4. **Strategic Alignment**: How does this fit our vision?
>
> The project_manager will ask you to compare pairs of User Stories to establish priorities.

---

### 🎯 [US-001] Deploy code_developer on GCP
**As a**: System administrator
**I want**: code_developer running on GCP 24/7
**So that**: Development continues autonomously without my laptop

**Business Value**: ⭐⭐⭐⭐⭐
**Estimated Effort**: 5 story points (5-7 days)
**Priority Score**: High (Value: 5, Effort: 5 → Ratio: 1.0)
**Status**: 📋 Ready

**Acceptance Criteria**:
- [ ] code_developer runs continuously on GCP Compute Engine
- [ ] Automatic restart on failure
- [ ] Logs accessible via Cloud Logging
- [ ] project_manager can communicate with GCP instance
- [ ] Cost stays under $50/month

**Technical Notes**:
- Use GCP Compute Engine with appropriate machine type
- Docker container for isolation
- Cloud Storage for logs and state
- VPC for secure communication

**Assigned To**: PRIORITY 4 (GCP Deployment)
**Related Stories**: None
**Discussion History**:
- [2025-10-10] User: "Need high priority for GCP deployment"
- [2025-10-10] PM: "This maps to existing PRIORITY 4. Ready to implement?"
- [2025-10-10] User: "Yes, prioritize after project_manager UI"

---

### 🎯 [US-002] View project health at a glance
**As a**: Product owner
**I want**: A health score for each priority
**So that**: I can quickly identify risks and bottlenecks

**Business Value**: ⭐⭐⭐⭐
**Estimated Effort**: 3 story points (2-3 days)
**Priority Score**: High (Value: 4, Effort: 3 → Ratio: 1.33)
**Status**: ✅ Assigned to PRIORITY 2

**Acceptance Criteria**:
- [ ] Each priority shows health score (0-100)
- [ ] Color-coded health indicators (green/yellow/red)
- [ ] Identifies specific risks (blocked, stale, unclear deliverables)
- [ ] Accessible via `/analyze` command

**Technical Notes**:
- Already implemented in AnalyzeRoadmapCommand
- Health calculation based on progress, momentum, structure
- Generates actionable recommendations

**Assigned To**: PRIORITY 2 (Project Manager CLI - Phase 2)
**Related Stories**: US-003 (Roadmap visualization)
**Discussion History**:
- [2025-10-10] PM: "This functionality already exists in Phase 2 implementation"
- [2025-10-10] User: "Perfect! Mark as assigned"

---

[... more User Stories ...]

---

## 🎯 PRIORITIES (Implementation View)

[... existing priority sections ...]
```

---

## 3. User Story Lifecycle

### 3.1 States

```
📝 Backlog → 🔄 In Discussion → 📋 Ready → ✅ Assigned → 🚀 In Progress → ✅ Complete
```

**State Descriptions**:

| State | Description | Who Acts | Next Step |
|-------|-------------|----------|-----------|
| 📝 Backlog | User Story captured but not yet evaluated | PM + User | Prioritize & discuss |
| 🔄 In Discussion | PM analyzing impact, asking clarifying questions | PM + User | Refine acceptance criteria, estimate effort |
| 📋 Ready | Story refined and prioritized, ready for assignment | PM | Map to existing priority or create new one |
| ✅ Assigned | Story assigned to a technical priority | Developer | Implementation |
| 🚀 In Progress | Actively being implemented | Developer | Complete implementation |
| ✅ Complete | Implementation done, acceptance criteria met | PM | Close story |

### 3.2 Workflow

```
1. User submits User Story (natural language or /user-story command)
   ↓
2. PM captures story in backlog with "📝 Backlog" status
   ↓
3. PM asks clarifying questions, estimates effort
   Status: 🔄 In Discussion
   ↓
4. PM shows roadmap impact analysis:
   - Could fit in existing PRIORITY X
   - Or requires new PRIORITY Y
   - Would delay PRIORITY Z by N weeks
   - Dependencies on PRIORITY A, B
   ↓
5. User and PM prioritize against other stories
   PM: "Between US-001 (GCP Deploy) and US-005 (CSV Export), which is more urgent?"
   Status: 📋 Ready (once prioritized)
   ↓
6. PM assigns story to priority
   Status: ✅ Assigned to PRIORITY X
   ↓
7. code_developer implements
   Status: 🚀 In Progress
   ↓
8. PM verifies acceptance criteria, closes story
   Status: ✅ Complete
```

---

## 4. Integration with RoadmapEditor

### 4.1 New Methods

```python
class RoadmapEditor:
    # ... existing methods ...

    def add_user_story(
        self,
        story_id: str,  # e.g., "US-001"
        title: str,
        role: str,
        want: str,
        so_that: str,
        business_value: int = 3,  # 1-5 stars
        estimated_effort: str = "TBD",
        acceptance_criteria: List[str] = None,
        technical_notes: str = "",
        status: str = "📝 Backlog"
    ) -> bool:
        """Add new User Story to backlog section."""

    def update_user_story(
        self,
        story_id: str,
        field: str,  # status, business_value, estimated_effort, etc.
        value: str
    ) -> bool:
        """Update User Story field."""

    def assign_user_story_to_priority(
        self,
        story_id: str,
        priority_number: str
    ) -> bool:
        """Assign User Story to a priority."""

    def get_user_story_summary(self) -> Dict:
        """Get summary of all User Stories.

        Returns:
            {
                'total': 15,
                'backlog': 8,
                'in_discussion': 3,
                'ready': 2,
                'assigned': 2,
                'complete': 0,
                'stories': [
                    {
                        'id': 'US-001',
                        'title': 'Deploy on GCP',
                        'status': '📋 Ready',
                        'business_value': 5,
                        'estimated_effort': '5 story points',
                        'priority_score': 'High'
                    },
                    ...
                ]
            }
        """

    def get_user_story_content(self, story_id: str) -> Optional[str]:
        """Get full content of a User Story."""

    def analyze_roadmap_impact(self, story_id: str) -> Dict:
        """Analyze how adding this User Story would impact roadmap.

        Returns:
            {
                'can_fit_in_existing': ['PRIORITY 2', 'PRIORITY 4'],
                'requires_new_priority': False,
                'estimated_delay': {
                    'PRIORITY 5': '1-2 weeks',
                    'PRIORITY 6': '1-2 weeks'
                },
                'dependencies': ['PRIORITY 1', 'PRIORITY 3'],
                'risks': ['May conflict with US-005', 'Requires GCP account'],
                'recommendations': 'Assign to PRIORITY 4 (GCP Deployment) - natural fit'
            }
        """
```

### 4.2 User Story Section Detection

The editor needs to detect the User Story Backlog section:

```python
# In RoadmapEditor class
def _find_user_story_section(self) -> Tuple[int, int]:
    """Find start and end line numbers of USER STORY BACKLOG section.

    Returns:
        (start_line, end_line) or (-1, -1) if not found
    """
    content = self.roadmap_path.read_text()
    lines = content.split('\n')

    start = -1
    end = -1

    for i, line in enumerate(lines):
        if '## 📋 USER STORY BACKLOG' in line:
            start = i
        elif start != -1 and line.startswith('## ') and 'PRIORITIES' in line:
            end = i
            break

    return (start, end)
```

---

## 5. AI Service Integration

### 5.1 New Intent: `user_story`

```python
# In AIService class
def classify_intent(self, user_input: str) -> str:
    """Classify user intent.

    Existing intents:
    - add_priority
    - update_priority
    - view_roadmap
    - analyze_roadmap
    - suggest_next

    New intent:
    - user_story: User describing a need/feature request
    """

    # Example classification logic
    if any(keyword in user_input.lower() for keyword in
           ['as a', 'i want', 'i need', 'user story', 'feature request']):
        return 'user_story'
    # ... existing logic ...
```

### 5.2 User Story Extraction

```python
# In AIService class
def extract_user_story(self, user_input: str) -> Optional[Dict]:
    """Extract User Story components from natural language.

    Args:
        user_input: Natural language description

    Returns:
        {
            'role': 'developer',
            'want': 'deploy on GCP',
            'so_that': 'runs 24/7',
            'title': 'Deploy code_developer on GCP'
        }
        or None if can't extract
    """

    prompt = f"""Extract User Story from this input:

{user_input}

Respond in this format:
<user_story>
<role>system administrator</role>
<want>deploy code_developer on GCP</want>
<so_that>it runs 24/7 autonomously</so_that>
<title>Deploy code_developer on GCP</title>
</user_story>

If this is not a User Story, respond with: NOT_A_USER_STORY
"""
    # ... call Claude API and parse response ...
```

### 5.3 Prioritization Dialog

```python
# In AIService class
def generate_prioritization_question(
    self,
    story1: Dict,
    story2: Dict
) -> str:
    """Generate natural question asking user to prioritize between two stories.

    Args:
        story1: First User Story dict
        story2: Second User Story dict

    Returns:
        Natural language question

    Example:
        "Between these two User Stories, which is more urgent for you?

        A) Deploy code_developer on GCP (5-7 days, enables 24/7 operation)
        B) CSV Export feature (2-3 days, enables data analysis in Excel)

        Your business priorities will help me organize the roadmap effectively."
    """
```

---

## 6. Chat Interface Updates

### 6.1 User Story Flow

```python
# In ChatSession class
def _handle_user_story_submission(self, user_input: str) -> str:
    """Handle User Story submission from natural language.

    Flow:
    1. Extract User Story components using AI
    2. Present extracted story back to user for confirmation
    3. Ask clarifying questions (acceptance criteria, effort estimate)
    4. Analyze roadmap impact
    5. Discuss priority with user
    6. Add to backlog or assign to priority
    7. Summarize action taken
    """

    # Step 1: Extract
    story = self.ai_service.extract_user_story(user_input)

    if not story:
        return "I couldn't identify a clear User Story. Could you rephrase using 'As a [role], I want [feature], so that [benefit]'?"

    # Step 2: Confirm
    confirmation = self.console.input(
        f"\n[yellow]I understood this User Story:[/]\n"
        f"  As a: {story['role']}\n"
        f"  I want: {story['want']}\n"
        f"  So that: {story['so_that']}\n\n"
        f"[yellow]Is this correct? [y/n]:[/] "
    )

    if confirmation.lower() not in ['y', 'yes']:
        return "Let's try again. Please describe your User Story."

    # Step 3: Clarify
    response = self._ask_clarifying_questions(story)

    # Step 4: Analyze impact
    impact = self.editor.analyze_roadmap_impact(story['id'])

    # Step 5: Discuss priority
    priority_discussion = self._prioritization_dialog(story, impact)

    # Step 6: Add to backlog or assign
    self.editor.add_user_story(**story)

    # Step 7: Summarize
    return f"✅ Added {story['id']}: {story['title']}\n\n{priority_discussion}"
```

### 6.2 Prioritization Dialog

```python
# In ChatSession class
def _prioritization_dialog(self, new_story: Dict, impact: Dict) -> str:
    """Interactive dialog to prioritize User Story.

    Flow:
    1. Show impact analysis
    2. Get existing backlog stories
    3. Ask pairwise comparison questions
    4. Calculate priority score
    5. Suggest assignment
    """

    output = "## 📊 Roadmap Impact Analysis\n\n"

    # Show where it could fit
    if impact['can_fit_in_existing']:
        output += f"**Could fit in existing priorities**: {', '.join(impact['can_fit_in_existing'])}\n"

    # Show delays
    if impact['estimated_delay']:
        output += f"\n**Potential delays**:\n"
        for priority, delay in impact['estimated_delay'].items():
            output += f"  - {priority}: delayed by {delay}\n"

    # Show dependencies
    if impact['dependencies']:
        output += f"\n**Dependencies**: {', '.join(impact['dependencies'])}\n"

    # Ask prioritization questions
    backlog_stories = self.editor.get_user_story_summary()['stories']
    backlog_stories = [s for s in backlog_stories if s['status'] == '📝 Backlog']

    if backlog_stories:
        output += "\n\n**Let's prioritize this story...**\n\n"

        for existing_story in backlog_stories[:3]:  # Compare with top 3
            question = self.ai_service.generate_prioritization_question(
                new_story, existing_story
            )

            self.console.print(question)
            response = self.console.input("[yellow]Your choice (A/B):[/] ")

            # Update priority scores based on response
            # ... priority calculation logic ...

    return output
```

---

## 7. Command Handler: `/user-story`

### 7.1 Command Structure

```python
# In coffee_maker/cli/commands/user_story.py

@register_command
class UserStoryCommand(BaseCommand):
    """Manage User Stories in roadmap backlog.

    Usage:
        /user-story add          - Guided User Story creation
        /user-story list         - List all User Stories
        /user-story view <id>    - View specific User Story
        /user-story update <id>  - Update User Story
        /user-story assign <id> <priority>  - Assign to priority
    """

    @property
    def name(self) -> str:
        return "user-story"

    @property
    def description(self) -> str:
        return "Manage User Stories in backlog"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        if not args:
            return self.get_usage()

        subcommand = args[0].lower()

        if subcommand == "add":
            return self._add_user_story(editor)
        elif subcommand == "list":
            return self._list_user_stories(editor)
        elif subcommand == "view" and len(args) > 1:
            return self._view_user_story(args[1], editor)
        elif subcommand == "update" and len(args) > 1:
            return self._update_user_story(args[1], editor)
        elif subcommand == "assign" and len(args) > 2:
            return self._assign_user_story(args[1], args[2], editor)
        else:
            return self.format_error(f"Unknown subcommand: {subcommand}\\n{self.get_usage()}")
```

---

## 8. Implementation Plan

### Phase 1: Foundation (4-6 hours)
- [ ] Add User Story Backlog section to ROADMAP.md
- [ ] Extend RoadmapEditor with User Story methods:
  - `add_user_story()`
  - `get_user_story_summary()`
  - `get_user_story_content()`
- [ ] Add test User Stories (US-001, US-002) to roadmap
- [ ] Test CRUD operations

### Phase 2: AI Integration (3-4 hours)
- [ ] Add `user_story` intent to AIService
- [ ] Implement `extract_user_story()` method
- [ ] Implement `generate_prioritization_question()` method
- [ ] Test User Story extraction from natural language

### Phase 3: Command Handler (2-3 hours)
- [ ] Create UserStoryCommand class
- [ ] Implement `/user-story add` with guided wizard
- [ ] Implement `/user-story list` with summary table
- [ ] Implement `/user-story view <id>`
- [ ] Register command in command registry

### Phase 4: Prioritization Dialog (4-5 hours)
- [ ] Implement `analyze_roadmap_impact()` in RoadmapEditor
- [ ] Create prioritization dialog flow in ChatSession
- [ ] Implement pairwise comparison logic
- [ ] Test full workflow: submit → analyze → prioritize → assign

### Phase 5: Advanced Features (3-4 hours)
- [ ] Implement `update_user_story()` in RoadmapEditor
- [ ] Implement `assign_user_story_to_priority()`
- [ ] Add status transitions (backlog → discussion → ready → assigned)
- [ ] Add User Story statistics to roadmap summary

### Phase 6: Testing & Documentation (2-3 hours)
- [ ] End-to-end test: Natural language → User Story → Priority assignment
- [ ] Update CLI help text
- [ ] Add examples to ROADMAP.md
- [ ] Update PRIORITY_2_STRATEGIC_SPEC.md

**Total Estimated Time**: 18-25 hours (2.5-3 days)

---

## 9. Success Criteria

### 9.1 User Can Submit Stories Naturally

```
User: "As a developer, I want to deploy on GCP so it runs 24/7"
  ↓
PM: "Got it! I understood this User Story:
     As a: developer
     I want: deploy on GCP
     So that: it runs 24/7

     Is this correct?"
  ↓
User: "Yes"
  ↓
PM: "Great! This could fit in PRIORITY 4 (GCP Deployment).
     Let me ask a few questions to help prioritize..."
```

### 9.2 Prioritization is Intuitive

```
PM: "Between these two User Stories, which is more urgent?

     A) Deploy on GCP (5-7 days, enables 24/7 operation)
     B) CSV Export (2-3 days, enables Excel analysis)

     Your choice?"
  ↓
User: "A"
  ↓
PM: "Got it! Prioritizing GCP deployment first."
```

### 9.3 Roadmap Impact is Transparent

```
PM: "Adding this User Story would:
     ✅ Fit naturally in PRIORITY 4 (GCP Deployment)
     ⚠️  Delay PRIORITY 5 (Analytics Dashboard) by 1-2 weeks
     📋 Requires PRIORITY 3 (code_developer) to be complete

     Should I assign this to PRIORITY 4?"
```

### 9.4 User Stories Drive Priorities

Instead of:
```
PRIORITY 4: GCP Deployment (vague, technical)
```

We have:
```
PRIORITY 4: GCP Deployment
Implements: US-001, US-007, US-012
  - US-001: Deploy code_developer 24/7
  - US-007: Automatic restart on failure
  - US-012: Cost monitoring and alerts
```

---

## 10. Example Interaction

```
User: "I need the agent to run on GCP so it works while I'm offline"

PM: "I understand! Let me capture this as a User Story:

     As a: system administrator
     I want: code_developer running on GCP 24/7
     So that: development continues even when my laptop is off

     Is this correct? [y/n]"

User: "y"

PM: "Great! A few questions to help me prioritize:

     1. What's the business impact if we don't have this?
        [High/Medium/Low]"

User: "High"

PM: "2. How soon do you need this?
        [This week / This month / This quarter]"

User: "This month"

PM: "Perfect! Let me analyze the roadmap impact...

     📊 Impact Analysis:
     ✅ Could fit in existing PRIORITY 4 (GCP Deployment) - natural fit!
     📋 Depends on PRIORITY 3 (code_developer) being complete ✅ (it is!)
     ⚠️  Would delay PRIORITY 5 (Analytics Dashboard) by 1-2 weeks
     💰 Estimated effort: 5-7 days

     I have 3 other stories in the backlog. Let's prioritize:

     Between these two, which is more urgent?
     A) Deploy on GCP (5-7 days, enables 24/7 operation) ← Your new story
     B) CSV Export (2-3 days, enables Excel analysis)

     Your choice?"

User: "A"

PM: "Great! One more:

     Between these two, which is more urgent?
     A) Deploy on GCP (5-7 days, enables 24/7 operation) ← Your new story
     C) Email Notifications (1-2 days, get alerts on completion)

     Your choice?"

User: "A"

PM: "Perfect! Based on our discussion:

     ✅ Added US-003: Deploy code_developer on GCP
     📊 Priority Score: High (Business Value: 5/5, Effort: 5-7 days)
     📋 Status: Ready
     ✅ Assigned to: PRIORITY 4 (GCP Deployment)

     This story is now linked to PRIORITY 4. When code_developer
     implements PRIORITY 4, it will use this User Story to guide
     the implementation.

     Summary:
     - Total User Stories: 4
     - Your story ranks #1 in backlog
     - Next steps: code_developer will implement after completing PRIORITY 2-3

     Anything else you'd like to add or adjust?"
```

---

## 11. Integration Points

### 11.1 ROADMAP.md Structure

```
# Coffee Maker Agent - Prioritized Roadmap
[... header ...]

## 📋 USER STORY BACKLOG
[... User Stories ...]

## 🎯 PRIORITIES (Implementation View)
[... Priorities with "Implements: US-XXX" links ...]
```

### 11.2 Command Integration

| Command | Handles User Stories? | Example |
|---------|---------------------|---------|
| `/user-story add` | ✅ Primary | Guided wizard for User Story creation |
| `/user-story list` | ✅ Primary | Show all User Stories with status |
| `/user-story view <id>` | ✅ Primary | Show full User Story details |
| `/analyze` | ✅ Enhanced | Show User Story → Priority mapping |
| `/view` | ✅ Enhanced | Show which User Stories each priority implements |
| Natural language | ✅ Enhanced | Detect User Story intent, extract components |

### 11.3 File Structure

```
coffee_maker/
├── cli/
│   ├── roadmap_editor.py       ← Extended with User Story methods
│   ├── ai_service.py            ← Extended with User Story extraction
│   ├── chat_interface.py        ← Extended with prioritization dialog
│   └── commands/
│       ├── user_story.py        ← NEW: User Story command handler
│       ├── analyze_roadmap.py   ← Updated: Show User Story links
│       └── view_roadmap.py      ← Updated: Show User Story links
docs/
├── ROADMAP.md                   ← Extended with User Story Backlog section
├── USER_STORY_DESIGN.md         ← THIS FILE
└── PRIORITY_X_TECHNICAL_SPEC.md ← Future specs reference User Stories
```

---

## 12. Future Enhancements

### Phase 2: Story Mapping
- Visual story map showing user journey
- Epics grouping related User Stories
- Release planning with story grouping

### Phase 3: Metrics & Tracking
- Velocity tracking (story points completed per sprint)
- Burndown charts
- Story cycle time (backlog → complete)

### Phase 4: Advanced Prioritization
- MoSCoW method (Must/Should/Could/Won't)
- RICE scoring (Reach, Impact, Confidence, Effort)
- Value vs. Effort matrix visualization

---

## 13. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| User Stories duplicate priorities | Medium | Medium | Show existing priorities during submission, suggest assignment |
| Too many User Stories overwhelm backlog | Medium | High | Auto-archive completed stories, limit backlog size |
| Prioritization dialog too long | Low | Medium | Limit pairwise comparisons to top 3 stories |
| User Stories not specific enough | High | Medium | Mandatory acceptance criteria, AI validation of specificity |
| Roadmap becomes too complex | Medium | Low | Keep User Stories in separate section, clear visual separation |

---

## Appendix A: References

- **User Story Format**: https://www.mountaingoatsoftware.com/agile/user-stories
- **INVEST Criteria**: Independent, Negotiable, Valuable, Estimable, Small, Testable
- **Story Mapping**: https://www.jpattonassociates.com/user-story-mapping/
- **PRIORITY 2 Technical Spec**: docs/roadmap/PRIORITY_2_STRATEGIC_SPEC.md (current implementation base)

---

**End of Design Document**
