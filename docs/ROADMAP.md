# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-09 🚨 **PRIORITIES REORGANIZED** | Critical daemon fixes applied ✅
**Current Branch**: `feature/priority-1.5`
**Status**: Refactoring phase completed ✅ | PRIORITY 2 MVP Phase 1 (80%) | PRIORITY 3 MVP (90% - critical fixes applied)
**Quick-Start**: ⚡ Daemon runnable now via `python run_daemon.py` (see PRIORITY 3 for details) 🚨 **Run from separate terminal**
**New Priority**: 🤖 **DAEMON FIRST** - Build autonomous daemon immediately, let it implement everything else!

## 🎯 Long-Term Vision

**Human-AI Team Collaboration**: In later phases, `code_developer` and `project-manager` will interact with the user just like a very-focused developer, their project manager, and the product's end user would collaborate in a professional team setting:

- 🤖 **code_developer (AI Developer)**: Autonomous coder who implements features, asks clarifying questions, provides progress updates, and demonstrates completed work
- 👔 **project-manager (AI PM)**: Facilitates communication, manages roadmap, prioritizes work, asks for user decisions, and keeps everyone aligned
- 👤 **User (Product Owner)**: Provides requirements, makes decisions, approves features, and gives feedback

**Professional Team Dynamics**:
- Developer asks PM: "Should I use Option A or B for this implementation?"
- PM asks User: "The developer needs approval for dependency X. Approve?"
- Developer shows User: "Feature complete! Here's a demo: [link]"
- User provides feedback: "Great! But can you adjust the color scheme?"
- PM updates roadmap: "Marking Feature Y as ✅ COMPLETED"

This creates a **natural, professional workflow** where AI agents collaborate just like human teams, but with the efficiency and consistency of automation.

---

## 🔄 Meta-Pattern: How We're Working NOW is the Blueprint

**CRITICAL INSIGHT**: The way we (User + Claude) are collaborating RIGHT NOW to build this project **IS THE MODEL** for how `project-manager` and `code-developer` will work together in the future.

### Current Workflow (User + Claude)

**What's happening now**:
```
User: "Add a daily recurring task about checking security vulnerabilities"
  ↓
Claude (as PM): "Got it! I'll add Section 12 with:
  - Daily security monitoring
  - GitHub Dependabot integration
  - Fix workflow by severity
  Should I also add automation scripts?"
  ↓
User: "Yes, and add a refactoring review task too"
  ↓
Claude (as Developer): *Implements both sections in ROADMAP.md*
  ↓
Claude (as PM): "Done! Added Section 12 (Security) and Section 13 (Refactoring).
  Committed and pushed. Here's the summary..."
```

### Future Workflow (project-manager + code-developer)

**What will happen after PRIORITY 3**:
```
User: "Add CSV export feature"
  ↓
project-manager (AI PM): "Got it! Clarifying questions:
  - All fields or specific ones?
  - Button in UI or CLI command?
  - Size limits?"
  ↓
User: "All fields, button in settings, no limit"
  ↓
project-manager: "Perfect! Adding to ROADMAP.md:
  PRIORITY 5: CSV Data Export
  - Export button in settings page
  - All user fields included
  - Pagination for large datasets"
  ↓
project-manager → code-developer: "New task: PRIORITY 5 from ROADMAP.md"
  ↓
code-developer (AI Developer): *Implements the feature autonomously*
  ↓
code-developer → project-manager: "Feature complete! PR #123, all tests passing"
  ↓
project-manager → User: "CSV export is done! Demo: demos/priority_5/demo.py
  Ready to review?"
```

### The Pattern is Identical

| Current (User + Claude) | Future (User + PM + Developer) |
|------------------------|--------------------------------|
| User gives requirements | User gives requirements |
| Claude clarifies as PM | project-manager clarifies |
| Claude implements | code-developer implements |
| Claude reports back | project-manager reports back |
| User reviews and approves | User reviews and approves |

### Why This Matters

**Documentation from Real Experience**:
- Every interaction we have NOW informs the design
- Every clarification question I ask → PM should ask
- Every progress update I give → Developer should give
- Every demo I create → Developer should create

**We're Dogfooding Before Building**:
1. **Now**: User + Claude build the system
2. **Next**: User uses the system we built
3. **Meta**: The system replicates how we built it

**Living Documentation**:
This ROADMAP is being created through the exact workflow that the binaries will automate:
- ✅ User requests feature → I clarify → I implement → I commit → I report
- 🔄 Future: User requests feature → PM clarifies → Developer implements → Developer commits → PM reports

### Examples from This Session

**User Request**: "Add security monitoring task"
- **I acted as PM**: Clarified scope, asked about workflow
- **I acted as Developer**: Implemented Section 12, committed, pushed
- **I acted as PM again**: Provided summary with details

**User Request**: "Add refactoring review task"
- **I acted as PM**: Confirmed understanding
- **I acted as Developer**: Implemented Section 13
- **I acted as PM again**: Summarized what was built

**User Request**: "Add PyPI package & binaries priority"
- **I acted as PM**: Confirmed placement (PRIORITY 3)
- **I acted as Developer**: Created 700+ line specification
- **I acted as PM again**: Explained what was delivered

**User Insight**: "The way we work NOW is the blueprint"
- **I acted as PM**: "Absolutely! Let me document this pattern"
- **I acted as Developer**: *Writing this section right now*
- **I acted as PM again**: Will provide summary after

### Implementation Implications

**For PRIORITY 1 (code-developer)**:
- Must ask clarifying questions (like I do)
- Must report progress (like I do)
- Must create demos (like I do)
- Must provide summaries (like I do)

**For PRIORITY 2 (project-manager)**:
- Must translate user requests to technical specs (like I do)
- Must update ROADMAP.md (like I do)
- Must relay developer questions to user (like I will)
- Must validate completeness before delivery (like I should)

**For PRIORITY 4 (Developer Status Dashboard)**:
- Must show what developer is doing (like I explain my steps)
- Must show progress (like I say "Step 1 of 3")
- Must show blockers (like I say "waiting for your input")

### The Meta-Loop

```
┌─────────────────────────────────────────────────────────────┐
│ 1. We collaborate (User + Claude) to build the system       │
│    └─> This workflow is documented in ROADMAP.md            │
│                                                              │
│ 2. The system replicates our workflow                        │
│    └─> project-manager + code-developer mimic us            │
│                                                              │
│ 3. Users get the same experience we had building it         │
│    └─> Natural collaboration, just automated                │
│                                                              │
│ 4. Improvements to the system come from using it            │
│    └─> We learn by building, users learn by using           │
└─────────────────────────────────────────────────────────────┘
```

### Success Metrics

**The binaries are successful if**:
- Users feel like they're working with us RIGHT NOW
- Same level of clarity in questions
- Same level of detail in implementations
- Same level of transparency in progress
- Same level of professionalism in delivery

**The ultimate validation**:
> "Working with project-manager and code-developer feels EXACTLY like
> working with User and Claude to build this roadmap."

---

**This is self-replicating software development** - We build a system that automates the way we built it. 🔄🤖

---

## 🚨 Priority Reorganization (2025-10-09)

**What Changed**: Daemon moved from PRIORITY 3 → **PRIORITY 1**

**New Strategy**: Build minimal autonomous daemon FIRST, then let daemon implement remaining priorities autonomously!

**New Priority Order**:
1. 🤖 **Autonomous Development Daemon** (minimal MVP, 3-5 days) - **YOU ARE HERE**
2. 🎯 **Project Manager UI** (single interface for user, 1-2 days) - **HIGH PRIORITY**
   - View roadmap + daemon status in one place
   - See pending notifications (daemon questions)
   - Respond to daemon (approve dependencies, answer questions)
   - Simple terminal UI (TUI with `rich` library)
   - **User's single interface for everything**
3. 📦 **PyPI Package & Binaries** (package for distribution, 1 day) - **CRITICAL TECHNICAL**
   - Configure pyproject.toml with binary entry points
   - Create `project-manager` and `code-developer` CLI commands
   - Package as installable PyPI package (pip install coffee-maker)
   - Test installation and binary execution
   - Publish to PyPI (or TestPyPI first)
   - **User can install and use the binaries system-wide**
4. 📊 **Developer Status Dashboard** (enhance PM UI, 1-2 days) - **HIGH PRIORITY**
   - Display code_developer real-time status (idle, working, blocked, testing)
   - Show current task progress (percentage, elapsed time, ETA)
   - Display developer questions waiting for PM/user response
   - Show recent activity log (commits, tests, errors)
   - Real-time updates via shared status file or database
   - **User always knows what developer is doing**
5. 🗃️ **Database Synchronization** (daemon implements this with PM UI oversight!)
6. 📊 **Analytics & Observability** (daemon implements this!)
7. 📱 **Streamlit Dashboards** (daemon implements this!)
8. 🚀 **Advanced PM Features** (AI chat, Slack integration - daemon implements!)

**Rationale**: Get daemon working ASAP → Daemon autonomously implements everything else → Faster delivery!

**Reference**: `docs/PRIORITY_REORGANIZATION_2025_10_09.md` (detailed rationale and timeline)

---

## 🔧 Project Binaries (PyPI Package)

When published on PyPI, the `coffee-maker` package will provide **two command-line tools**:

### 1. `project-manager` - User Interface 👤

**Purpose**: Single interface for user to interact with roadmap and daemon

**Commands**:
```bash
# View roadmap and daemon status
project-manager status

# View pending notifications from daemon
project-manager notifications

# Respond to daemon questions
project-manager respond <msg_id> <answer>

# Manage roadmap
project-manager view
project-manager edit

# Control daemon
project-manager start-daemon
project-manager stop-daemon
project-manager pause-daemon
```

**Configuration** (`pyproject.toml`):
```toml
[project.scripts]
project-manager = "coffee_maker.cli.project_manager:main"
```

**User Experience**:
- Terminal UI with `rich` library
- Real-time daemon status display
- Interactive notification system
- Roadmap viewer/editor
- One command to rule them all!

---

### 2. `code-developer` - Autonomous Daemon 🤖

**Purpose**: Autonomous development daemon that implements roadmap (runs underlying Claude CLI)

**Commands**:
```bash
# Start daemon (runs continuously)
code-developer start

# Start in foreground (for debugging)
code-developer start --foreground

# Stop daemon
code-developer stop

# Check status
code-developer status

# View logs
code-developer logs --tail 100

# Pause daemon (finish current task, then wait)
code-developer pause

# Resume daemon
code-developer resume
```

**Configuration** (`pyproject.toml`):
```toml
[project.scripts]
code-developer = "coffee_maker.autonomous.daemon_cli:main"
```

**Daemon Behavior**:
- Runs as background process (daemon mode)
- Wraps Claude CLI (`claude code`) in subprocess
- Reads `docs/ROADMAP.md` continuously
- Implements priorities autonomously
- **ALWAYS asks permission** (core principle!)
- Creates demos after completion
- Notifies user via `project-manager`
- Never stops without user command

---

### 🔄 How They Work Together

```
User             Project Manager           Code Developer (wraps Claude CLI)
 │                    │                              │
 ├──────────────────►│                              │
 │  project-manager  │                              │
 │    start-daemon   │                              │
 │                   │                              │
 │                   ├────────────────────────────► │
 │                   │  Start daemon process        │
 │                   │                              │
 │                   │                              ├─ Read ROADMAP.md
 │                   │                              ├─ Call: claude code -p "implement PRIORITY 1"
 │                   │                              │
 │                   │ ◄────────────────────────────┤
 │                   │  Need dependency approval    │
 │                   │                              │
 │ ◄─────────────────┤                              │
 │  Notification:    │                              │
 │  "Daemon asks..." │                              │
 │                   │                              │
 ├──────────────────►│                              │
 │  project-manager  │                              │
 │  respond msg_001  │                              │
 │  approve          │                              │
 │                   │                              │
 │                   ├────────────────────────────► │
 │                   │  User approved               │
 │                   │                              │
 │                   │                              ├─ Install dependency
 │                   │                              ├─ Continue Claude CLI
 │                   │                              ├─ Create demo
 │                   │                              │
 │                   │ ◄────────────────────────────┤
 │                   │  PRIORITY complete!          │
 │                   │                              │
 │ ◄─────────────────┤                              │
 │  Notification:    │                              │
 │  "✅ PRIORITY 1   │                              │
 │   complete! 🎬"   │                              │
```

**Key Points**:
- User interacts ONLY with `project-manager`
- `code-developer` runs in background, wrapping Claude CLI
- `code-developer` calls `claude code` subprocess for each task
- All communication through file-based notifications
- User always has control (permission-first!)

---

### 📦 Installation & Setup

```bash
# Install from PyPI
pip install coffee-maker

# Verify binaries available
project-manager --version
claude-coder --version

# First-time setup
project-manager setup
# → Creates data/ directory
# → Initializes ROADMAP.md
# → Configures notification system

# Start daemon
project-manager start-daemon
# or directly:
claude-coder start

# Monitor status
project-manager status
```

---

### 🛡️ Safety Features (Built into MVP)

Both binaries enforce safety from day one:

**`claude-coder` Safety**:
- ✅ Permission-first architecture (ALWAYS asks)
- ✅ File lock on ROADMAP.md (no conflicts)
- ✅ Automatic rollback on test failures
- ✅ Timeout limits (won't run forever)
- ✅ Graceful shutdown (CTRL+C safe)

**`project-manager` Safety**:
- ✅ Input validation (no malformed responses)
- ✅ File lock enforcement (no concurrent edits)
- ✅ Audit log (all user responses logged)
- ✅ Emergency stop (can kill daemon immediately)

**Together**: Permission-first + Single interface = Safe autonomous development

---

**This architecture is the foundation for version 0.1.0 and all future versions.** 🚀

---

## 🎯 Global Vision

### Phase 1: Self-Implementing System (Current)

Transform **Coffee Maker Agent** into a **self-implementing LLM orchestration framework** with:
- ✅ **Solid infrastructure** (refactoring completed)
- 🔄 **Ongoing cleanup** (codebase simplification in progress by parallel Claude instance)
- 🤖 **Autonomous development** (Claude implements the roadmap itself) ⚡ **NEW PARADIGM**
- 📊 **Advanced analytics** (Langfuse → SQLite/PostgreSQL export)
- 📚 **Professional documentation** (enhanced pdoc)
- 🤖 **Intelligent agents** (5 innovative projects)

**Revolutionary approach**: After implementing Priority 1 (Autonomous Daemon), you only plan features in the roadmap - Claude builds them autonomously!

**Current Status**: Building minimal autonomous daemon to prove the self-implementing concept.

---

### Phase 2: Universal Python Library 🌍 **FUTURE VISION**

**Transform into**: `roadmap-driven-dev` - A Python library that enables **ANY project** to be coded through roadmap-based conversations on top of user's existing code.

**Vision**: What we're building for ourselves becomes a product that helps thousands of developers build software through natural conversation instead of manual coding.

#### The Future Product

```python
# Any developer can use this in their project:
from roadmap_driven_dev import AutonomousDaemon

# Initialize in any Python project
daemon = AutonomousDaemon(
    roadmap_path="docs/ROADMAP.md",
    codebase_root=".",
    model="claude-sonnet-4",
    user_involvement="review_prs"  # or "approve_each_step", "full_autonomy"
)

# Daemon reads YOUR roadmap, understands YOUR codebase, implements YOUR features
daemon.run()

# Developer just:
# 1. Writes roadmap in natural language
# 2. Reviews PRs
# 3. Merges when satisfied
```

#### Key Features (Future)

1. **Language-Agnostic**: Works with any programming language (Python, TypeScript, Rust, Go, etc.)
2. **Codebase-Aware**: Understands existing patterns, follows project conventions
3. **Roadmap-Driven**: Natural language planning → Automatic implementation
4. **Human-in-the-Loop**: Configurable supervision levels (full autonomy ↔ approve each step)
5. **Git-Native**: Branches, commits, PRs follow Git best practices
6. **Test-Driven**: Automatically runs tests, rolls back on failure
7. **Cost-Optimized**: Uses cheaper models for simple tasks, advanced models for complex work
8. **Team-Ready**: Multiple developers + daemon collaborate via PRs

#### Example Use Cases

**Startup Building MVP**:
```markdown
# startup-roadmap.md
PRIORITY 1: User authentication with JWT
PRIORITY 2: PostgreSQL schema for users, products, orders
PRIORITY 3: REST API endpoints (CRUD for all entities)
PRIORITY 4: React frontend with authentication flow
```
→ Daemon implements all 4 priorities in 2 weeks while founders focus on customers

**Open Source Project**:
```markdown
# roadmap.md
PRIORITY 1: Add TypeScript support (currently JavaScript only)
PRIORITY 2: Migrate from Webpack to Vite
PRIORITY 3: Add comprehensive test coverage (currently 30%)
```
→ Daemon implements while maintainer reviews PRs

**Enterprise Migration**:
```markdown
# migration-roadmap.md
PRIORITY 1: Audit all Python 2 code (10,000+ files)
PRIORITY 2: Migrate to Python 3.11 (automated refactoring)
PRIORITY 3: Update all dependencies to latest versions
PRIORITY 4: Add type hints to all public APIs
```
→ Daemon handles tedious migration work

#### Architecture (Future)

```
roadmap-driven-dev/
├── core/
│   ├── daemon.py                 # Universal daemon (works with any project)
│   ├── roadmap_parser.py         # Parse any roadmap format (Markdown, YAML, JSON)
│   ├── codebase_analyzer.py      # Understand any codebase structure
│   └── pattern_detector.py       # Learn project conventions automatically
│
├── integrations/
│   ├── claude_cli.py             # Claude Code CLI integration
│   ├── openai.py                 # OpenAI API integration (fallback)
│   ├── local_llm.py              # Local model support (Ollama, etc.)
│   └── git_provider.py           # GitHub, GitLab, Bitbucket support
│
├── languages/
│   ├── python.py                 # Python-specific patterns
│   ├── typescript.py             # TypeScript-specific patterns
│   ├── rust.py                   # Rust-specific patterns
│   └── generic.py                # Generic language support
│
└── templates/
    ├── roadmap_templates/        # Roadmap templates for common use cases
    ├── project_templates/        # Project structure templates
    └── pr_templates/             # PR description templates
```

#### Monetization Strategy (Future)

1. **Open Source Core**: Free forever (like this project)
2. **Pro Features** ($49/month):
   - Team collaboration (multiple developers + daemon)
   - Advanced analytics (cost tracking, velocity metrics)
   - Priority support
   - Custom model fine-tuning on your codebase
3. **Enterprise** ($499/month):
   - Self-hosted deployment
   - Security audits
   - SLA guarantees
   - Dedicated support

#### Path to Product

**Phase 1** (Current - 2025 Q1):
- Build autonomous daemon for this project
- Prove the concept works end-to-end
- Document everything thoroughly

**Phase 2** (2025 Q2):
- Extract core components into separate library
- Add configuration system (works with any project)
- Test on 3-5 different project types (web app, CLI tool, library, etc.)

**Phase 3** (2025 Q3):
- Polish API, write documentation
- Create website + marketing materials
- Beta release to select developers

**Phase 4** (2025 Q4):
- Public launch on GitHub + PyPI
- Build community (Discord, tutorials, examples)
- Iterate based on user feedback

**Phase 5** (2026):
- Pro tier launch
- Enterprise partnerships
- Scale to 1000+ projects using the library

#### Success Metrics (Future Product)

- **Adoption**: 1000+ GitHub stars, 100+ projects using it
- **Quality**: >80% of daemon PRs merged without major changes
- **Impact**: Developers ship features 3-5x faster
- **Revenue**: $10K+ MRR from Pro/Enterprise tiers
- **Community**: Active Discord with 500+ developers

#### Competitive Advantage

**vs GitHub Copilot**: We implement entire features, not just autocomplete
**vs Cursor AI**: We work autonomously, not just assistance
**vs Devin AI**: We're open source, transparent, and extensible
**vs Junior Developers**: We're 24/7, consistent, and cost-effective

**Our Moat**:
- Roadmap-driven approach (natural language → full implementation)
- Human-in-the-loop flexibility (configurable supervision)
- Built on battle-tested patterns (this project is the proof!)
- Open source core (community trust + contributions)

---

### Why This Vision Matters

**Current Problem**: Software development is slow because:
- Writing code is tedious (boilerplate, tests, docs)
- Onboarding new developers takes weeks
- Maintaining legacy code is painful
- Simple features take days instead of hours

**Our Solution**:
```
Natural Language Roadmap → Autonomous Implementation → Human Review → Merge
```

**Impact**:
- 🚀 Ship features 3-5x faster
- 💰 Reduce development costs by 50-70%
- 🧠 Developers focus on architecture, not typing
- 📈 Startups compete with bigger teams
- 🌍 More software gets built, faster

**This is the future of software development. We're building it now.** 🤖

---

### Phase 3+: Human-Like Development Team Interaction 👥 **ADVANCED VISION**

**Vision**: `code-developer` and `project-manager` interact with the user like a real, highly-focused development team would:

```
User (Product Owner)  ←→  project-manager (PM)  ←→  code-developer (Developer)
```

#### Three-Role Interaction Model

**User's Role** (Product Owner/End User):
- Defines features in natural language
- Reviews results and gives feedback
- Makes business decisions
- Tests features as end user

**`project-manager`'s Role** (Project Manager):
- Clarifies requirements with user
- Breaks down features into technical tasks
- Prioritizes work (critical bugs before new features)
- Reports progress and blockers
- Shields developer from constant interruptions
- Validates deliverables before showing to user

**`code-developer`'s Role** (Focused Developer):
- Implements features autonomously
- Asks PM technical questions (not the user directly)
- Reports completion to PM (not the user)
- Focuses on code quality and tests
- Works in deep focus without context switching

#### Example Conversation Flow

**1. Feature Request** (User → PM):
```
User: "I want users to be able to export their data to CSV"

project-manager: "Got it! Let me clarify a few things:
  - What data should be exported? (All fields or specific ones?)
  - Should this be a button in the UI or a CLI command?
  - Any size limits? (Some exports could be huge)
  - Format: headers, date format, encoding?"

User: "All user data, button in settings page, no size limit (pagination if needed), standard CSV with headers"

project-manager: "Perfect! I'll add this to the roadmap:

PRIORITY 5: CSV Data Export
- Add export button to settings page
- Include all user fields (name, email, created_at, etc.)
- Paginate for large datasets (>10k rows)
- Standard CSV: UTF-8, headers, ISO date format

I'll assign this to code-developer. ETA: 4-6 hours.
I'll notify you when it's ready for testing."
```

**2. Implementation** (PM → Developer):
```
project-manager → code-developer:
"New task from user: PRIORITY 5 - CSV Data Export
See ROADMAP.md for details.
User wants this in settings page with pagination.
Let me know if you have questions."

code-developer:
"Acknowledged. Starting implementation.
Question: Should CSV download trigger immediately or generate in background?"

project-manager:
"Good question. Let me check with user..."
→ [asks user, gets answer]
→ "User says immediate download is fine (<1s is acceptable)"

code-developer:
"Got it. Implementing now..."
→ [2 hours later]
→ "Feature complete. All tests passing.
   Created PR #123. Ready for PM review."
```

**3. Review & Delivery** (PM → User):
```
project-manager: "CSV export feature is complete! 🎉

Demo: demos/priority_5_csv_export/demo.py
PR: #123 (all tests passing ✅)

New Features:
  ✅ Export button in settings page
  ✅ All user data included
  ✅ Handles large datasets (tested with 50k rows)
  ✅ Standard CSV format

Please test and let me know if any changes needed."

User: "Looks great! But can we add a timestamp to the filename?"

project-manager → code-developer:
"User feedback: Add timestamp to CSV filename
Example: user_export_2025_10_09_14_30.csv"

code-developer:
"Done. Updated PR #123."

project-manager → User:
"Updated! Filename now includes timestamp. Ready to merge?"

User: "Perfect, merge it!"

project-manager: "Merged ✅. Feature is now live."
```

#### Advanced Interactions (Future)

**Developer Asking for Design Decisions**:
```
code-developer → project-manager:
"Implementing user authentication. Which approach:
  A) JWT tokens (stateless, scales well)
  B) Sessions (stateful, simpler, more secure)

Current codebase has no auth, so we can choose."

project-manager → User:
"code-developer needs decision on authentication:
  - JWT: Better for mobile apps, microservices
  - Sessions: Better for web-only, simpler

Which fits your use case better?"

User: "We're web-only, keep it simple"

project-manager → code-developer:
"User chose sessions (web-only, prioritize simplicity)"

code-developer: "Acknowledged. Implementing session-based auth."
```

**PM Shielding Developer from Noise**:
```
User: "Hey, can you add dark mode?"
User: "Also, the logo should be bigger"
User: "And can we have user profiles?"
User: "Oh, and email notifications would be nice"

project-manager:
"Got all your requests! Let me organize them:

CURRENT (In Progress):
  - PRIORITY 5: CSV Export (code-developer working on it)

BACKLOG (After current task):
  - PRIORITY 6: Dark mode
  - PRIORITY 7: User profiles
  - PRIORITY 8: Email notifications
  - PRIORITY 9: Bigger logo (quick win)

I'll batch these so code-developer can focus without context switching.
Sound good?"

User: "Yes, perfect!"

→ PM only interrupts developer for critical bugs, not every feature request
```

**PM Prioritizing Critical Bugs**:
```
User: "URGENT: Users can't login!"

project-manager → code-developer:
"🚨 CRITICAL BUG: Login broken
Pausing current work (PRIORITY 5).
Investigate immediately."

code-developer:
"Checking... Found issue: session timeout too short.
Fixed and deployed. Testing now."
→ [10 minutes later]
→ "Login working. Tests passing. Resumed PRIORITY 5."

project-manager → User:
"✅ Login fixed! Root cause: session timeout.
Increased to 24h. All users can login now.
code-developer back to CSV export feature."
```

#### Benefits of This Model

**For User**:
- Single point of contact (`project-manager`)
- Don't need to know technical details
- Can focus on business requirements
- Get progress updates without asking
- Feel like managing a real team

**For Project Manager**:
- Understand user's business needs
- Translate to technical requirements
- Prioritize work effectively
- Manage multiple tasks in backlog
- Shield developer from constant interruptions

**For Code Developer**:
- Deep focus without context switching
- Clear, technical requirements (not vague requests)
- Ask PM questions, not interrupt user
- Work autonomously on implementation
- Deliver to PM, not directly to user

#### Implementation Phases

**Phase 3A** (Month 3-4): PM-Developer Separation
- `project-manager` maintains ROADMAP.md
- `code-developer` reads ROADMAP.md, implements tasks
- PM reviews PRs before showing to user
- Communication via shared notification system

**Phase 3B** (Month 5-6): Natural Language Understanding
- PM understands vague requests ("make it faster", "improve UX")
- PM asks clarifying questions like a human PM
- Developer asks technical questions to PM
- PM translates between business and technical language

**Phase 3C** (Month 7-8): Context-Aware Collaboration
- PM knows when to interrupt developer (critical bugs)
- PM batches small requests to avoid context switching
- Developer proactively asks for design decisions
- PM tracks developer's focus time and productivity

**Phase 3D** (Month 9-12): Team Dynamics
- PM negotiates timelines ("User wants feature tomorrow" → "Realistically 3 days")
- Developer pushes back on unclear requirements
- PM advocates for technical debt paydown
- Team learns user's communication style and adapts

#### Success Criteria

- User feels like they have a **real development team**
- User never needs to think about "Claude CLI" or "technical implementation"
- PM handles all complexity, user just describes what they want
- Developer stays in deep focus 80%+ of the time
- Features get delivered 3-5x faster than human teams
- User trust increases (team is reliable, professional, predictable)

**This creates the illusion of a small, highly-efficient software team - but it's just two AI agents collaborating.** 👥🤖

---

**Current Status**: Phase 1 (Self-Implementing System) - Building the foundation by having the system implement itself first.

---

## 📦 PRIORITY 3: PyPI Package & Binaries

**Goal**: Package coffee-maker as installable PyPI package with `project-manager` and `code-developer` command-line tools

**Duration**: 1 day (4-8 hours)
**Dependencies**: PRIORITY 1 (Daemon core), PRIORITY 2 (PM CLI core)
**Status**: 📝 Planned

### Why This Is Critical

After implementing PRIORITY 1 & 2, we have:
- ✅ Daemon core logic (code-developer functionality)
- ✅ Project Manager CLI logic (project-manager functionality)

**But users can't install and use them yet!**
- ❌ No `pip install coffee-maker` command
- ❌ No system-wide `project-manager` binary
- ❌ No system-wide `code-developer` binary
- ❌ Can't distribute to others

**This priority makes the binaries installable and distributable!**

### ⚡ Quick-Start Option Available Now

**While waiting for PRIORITY 3**, you can run the daemon using the temporary convenience script:

⚠️  **CRITICAL REQUIREMENT**: The daemon MUST run from a **separate terminal**, NOT from within Claude Code!

**Why?** The daemon spawns Claude CLI sessions to implement features. Running it from within an existing Claude Code session creates a nested/recursive conflict that causes it to hang indefinitely.

**Correct Usage:**

1. **Exit Claude Code** (if currently in a session)
2. **Open a NEW terminal** (completely separate)
3. **Navigate to project and activate environment:**
   ```bash
   cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent
   source /Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/activate
   ```
4. **Run the daemon:**
   ```bash
   # Interactive mode (asks for approval)
   python run_daemon.py

   # Autonomous mode (auto-approve)
   python run_daemon.py --auto-approve

   # See all options
   python run_daemon.py --help
   ```

The script includes runtime detection and will warn you if it detects a Claude session.

---

### Core Requirements

#### 1. Configure pyproject.toml

**Binary Entry Points**:
```toml
[project.scripts]
project-manager = "coffee_maker.cli.project_manager:main"
code-developer = "coffee_maker.autonomous.daemon_cli:main"
```

**Package Metadata**:
```toml
[project]
name = "coffee-maker"
version = "0.1.0"
description = "Autonomous AI development team: project-manager + code-developer"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"

dependencies = [
    "rich>=13.0.0",        # Terminal UI
    "click>=8.0.0",        # CLI framework
    "langfuse>=2.0.0",     # LLM observability
    "requests>=2.31.0",    # HTTP requests
    "python-dotenv>=1.0.0" # Environment variables
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0"
]

[project.urls]
Homepage = "https://github.com/Bobain/MonolithicCoffeeMakerAgent"
Documentation = "https://bobain.github.io/MonolithicCoffeeMakerAgent/"
Repository = "https://github.com/Bobain/MonolithicCoffeeMakerAgent"
```

#### 2. Create CLI Entry Point Modules

**File**: `coffee_maker/cli/project_manager.py`
```python
"""Project Manager CLI - User interface for autonomous development team."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Coffee Maker Project Manager - Manage your autonomous development team."""
    pass


@main.command()
def status():
    """Display daemon and roadmap status."""
    console.print("[bold green]🎯 Project Manager Status[/]")
    # Implementation from PRIORITY 2
    pass


@main.command()
def notifications():
    """View pending notifications from daemon."""
    console.print("[bold yellow]📬 Pending Notifications[/]")
    # Implementation from PRIORITY 2
    pass


@main.command()
@click.argument("message_id")
@click.argument("response")
def respond(message_id: str, response: str):
    """Respond to daemon question."""
    console.print(f"[green]✅ Responded to {message_id}: {response}[/]")
    # Implementation from PRIORITY 2
    pass


@main.command()
@click.argument("version")
@click.option("--test", is_flag=True, help="Publish to TestPyPI instead of PyPI")
@click.option("--dry-run", is_flag=True, help="Build without publishing")
def release(version: str, test: bool, dry_run: bool):
    """Release the project to PyPI.

    Example:
        project-manager release 0.1.0
        project-manager release 0.2.0 --test
        project-manager release 0.1.1 --dry-run
    """
    console.print(f"[bold cyan]📦 Releasing coffee-maker v{version}...[/]")

    # Step 1: Update version in pyproject.toml
    console.print("[yellow]1/6 Updating version...[/]")

    # Step 2: Run tests
    console.print("[yellow]2/6 Running tests...[/]")

    # Step 3: Build package
    console.print("[yellow]3/6 Building package...[/]")

    # Step 4: Git tag
    console.print(f"[yellow]4/6 Creating git tag v{version}...[/]")

    if dry_run:
        console.print("[green]✅ Dry run complete (no publish)[/]")
        return

    # Step 5: Publish
    if test:
        console.print("[yellow]5/6 Publishing to TestPyPI...[/]")
    else:
        console.print("[yellow]5/6 Publishing to PyPI...[/]")

    # Step 6: Push tags
    console.print("[yellow]6/6 Pushing to GitHub...[/]")

    console.print(f"[bold green]✅ Released coffee-maker v{version} successfully![/]")


if __name__ == "__main__":
    main()
```

**File**: `coffee_maker/autonomous/daemon_cli.py`
```python
"""Code Developer Daemon CLI - Autonomous development agent."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Coffee Maker Code Developer - Autonomous development daemon."""
    pass


@main.command()
@click.option("--foreground", is_flag=True, help="Run in foreground (not as daemon)")
def start(foreground: bool):
    """Start the autonomous development daemon."""
    console.print("[bold green]🤖 Starting Code Developer Daemon...[/]")
    # Implementation from PRIORITY 1
    pass


@main.command()
def stop():
    """Stop the running daemon."""
    console.print("[yellow]⏹️  Stopping Code Developer Daemon...[/]")
    # Implementation from PRIORITY 1
    pass


@main.command()
def status():
    """Check daemon status."""
    console.print("[cyan]📊 Code Developer Status[/]")
    # Implementation from PRIORITY 1
    pass


if __name__ == "__main__":
    main()
```

#### 3. Build and Test Package

**Build Commands**:
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Output:
# dist/coffee_maker-0.1.0-py3-none-any.whl
# dist/coffee_maker-0.1.0.tar.gz
```

**Test Installation (Local)**:
```bash
# Install locally in editable mode
pip install -e .

# Test binaries
project-manager --version
code-developer --version

# Test commands
project-manager status
code-developer start --foreground
```

**Test Installation (From Built Package)**:
```bash
# Install from wheel
pip install dist/coffee_maker-0.1.0-py3-none-any.whl

# Test binaries work
project-manager status
code-developer status
```

#### 4. Publish to PyPI

**Publish to TestPyPI (First)**:
```bash
# Create ~/.pypirc with credentials
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ coffee-maker
```

**Publish to PyPI (Production)**:
```bash
# Upload to PyPI
twine upload dist/*

# Users can now install:
# pip install coffee-maker
```

#### 5. Documentation

**Update README.md** with installation instructions:
```markdown
## Installation

Install coffee-maker from PyPI:

```bash
pip install coffee-maker
```

This installs two command-line tools:
- `project-manager` - User interface for managing your autonomous team
- `code-developer` - Autonomous development daemon

## Quick Start

### 1. Start the autonomous developer:
```bash
code-developer start
```

### 2. Check status:
```bash
project-manager status
```

### 3. View notifications:
```bash
project-manager notifications
```

### 4. Respond to daemon questions:
```bash
project-manager respond msg_123 approve
```

## Usage

See [Documentation](https://bobain.github.io/MonolithicCoffeeMakerAgent/) for detailed usage.
```

---

### File Structure

After PRIORITY 3, the project structure will be:

```
MonolithicCoffeeMakerAgent/
├── coffee_maker/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── project_manager.py      # ⚡ Entry point for project-manager binary
│   ├── autonomous/
│   │   ├── __init__.py
│   │   ├── daemon_cli.py            # ⚡ Entry point for code-developer binary
│   │   └── minimal_daemon.py        # Daemon core logic
│   └── ...
├── pyproject.toml                   # ⚡ Configured with entry points
├── README.md                        # ⚡ Updated with installation instructions
├── dist/                            # ⚡ Built packages
│   ├── coffee_maker-0.1.0-py3-none-any.whl
│   └── coffee_maker-0.1.0.tar.gz
└── ...
```

---

### Implementation Steps

**Step 1: Configure pyproject.toml** (1 hour)
1. Add [project.scripts] entry points
2. Update metadata (version, description, authors)
3. List dependencies and optional dev dependencies
4. Add project URLs (homepage, docs, repo)

**Step 2: Create CLI Entry Points** (2 hours)
5. Create `coffee_maker/cli/project_manager.py` with click commands
6. Create `coffee_maker/autonomous/daemon_cli.py` with click commands
7. Import and call existing logic from PRIORITY 1 & 2
8. Add --version options, help text, command documentation

**Step 3: Build Package** (1 hour)
9. Install build tools (pip install build twine)
10. Run `python -m build` to create wheel and sdist
11. Verify dist/ directory contains .whl and .tar.gz files

**Step 4: Test Installation** (2 hours)
12. Install in fresh virtual environment
13. Test `project-manager` command works
14. Test `code-developer` command works
15. Test all subcommands (status, start, stop, notifications, respond)
16. Verify binaries are accessible from any directory

**Step 5: Publish (Optional for MVP)** (1 hour)
17. Create PyPI account (if not exists)
18. Configure ~/.pypirc with credentials
19. Upload to TestPyPI first: `twine upload --repository testpypi dist/*`
20. Test installation from TestPyPI
21. Upload to PyPI: `twine upload dist/*`

**Step 6: Documentation** (1 hour)
22. Update README.md with installation instructions
23. Add quick start guide
24. Document both binaries (project-manager, code-developer)
25. Add troubleshooting section

---

### Success Criteria

✅ **Package builds successfully**:
- `python -m build` creates wheel and sdist
- No build errors or warnings

✅ **Binaries are installable**:
- `pip install coffee-maker` works
- Installs in site-packages correctly

✅ **Commands are accessible**:
- `project-manager` command available in PATH
- `code-developer` command available in PATH
- Both work from any directory

✅ **All commands work**:
- `project-manager status` - displays status
- `project-manager notifications` - lists notifications
- `project-manager respond` - responds to daemon
- `code-developer start` - starts daemon
- `code-developer stop` - stops daemon
- `code-developer status` - shows daemon status

✅ **Published to PyPI** (optional for MVP):
- Package visible on pypi.org
- Anyone can `pip install coffee-maker`
- Installation instructions in README

---

### Testing Checklist

```bash
# 1. Build package
python -m build
ls dist/  # Should show .whl and .tar.gz

# 2. Install in clean environment
python -m venv test_env
source test_env/bin/activate
pip install dist/coffee_maker-0.1.0-py3-none-any.whl

# 3. Test project-manager binary
project-manager --version  # Should show 0.1.0
project-manager status
project-manager notifications
project-manager respond test_msg approve

# 4. Test code-developer binary
code-developer --version  # Should show 0.1.0
code-developer start --foreground  # Should start in foreground
code-developer status
code-developer stop

# 5. Test from different directory
cd /tmp
project-manager status  # Should still work

# 6. Uninstall
pip uninstall coffee-maker

# 7. Test from TestPyPI (optional)
pip install --index-url https://test.pypi.org/simple/ coffee-maker
```

---

### Release Command Implementation

**Command**: `project-manager release <version> [--test] [--dry-run]`

**Purpose**: Automate the release process from version bump to PyPI publication

**Workflow**:
```
1. Update version → 2. Run tests → 3. Build → 4. Git tag → 5. Publish → 6. Push
```

**Implementation**:
```python
# File: coffee_maker/cli/project_manager.py

import subprocess
import tomli
import tomli_w
from pathlib import Path


def update_version_in_pyproject(version: str):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)

    data["project"]["version"] = version

    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)

    console.print(f"[green]✅ Updated version to {version}[/]")


def run_tests():
    """Run test suite before release."""
    result = subprocess.run(["pytest", "tests/", "-v"], capture_output=True)

    if result.returncode != 0:
        console.print("[red]❌ Tests failed! Aborting release.[/]")
        raise click.Abort()

    console.print("[green]✅ All tests passed[/]")


def build_package():
    """Build wheel and sdist."""
    subprocess.run(["python", "-m", "build"], check=True)
    console.print("[green]✅ Package built successfully[/]")


def create_git_tag(version: str):
    """Create and push git tag."""
    subprocess.run(["git", "add", "pyproject.toml"], check=True)
    subprocess.run(["git", "commit", "-m", f"Release v{version}"], check=True)
    subprocess.run(["git", "tag", f"v{version}"], check=True)
    console.print(f"[green]✅ Created git tag v{version}[/]")


def publish_to_pypi(test: bool = False):
    """Publish to PyPI or TestPyPI."""
    if test:
        subprocess.run(
            ["twine", "upload", "--repository", "testpypi", "dist/*"],
            check=True
        )
        console.print("[green]✅ Published to TestPyPI[/]")
    else:
        subprocess.run(["twine", "upload", "dist/*"], check=True)
        console.print("[green]✅ Published to PyPI[/]")


def push_to_github():
    """Push commits and tags to GitHub."""
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    console.print("[green]✅ Pushed to GitHub[/]")


@main.command()
@click.argument("version")
@click.option("--test", is_flag=True, help="Publish to TestPyPI")
@click.option("--dry-run", is_flag=True, help="Build without publishing")
def release(version: str, test: bool, dry_run: bool):
    """Release the project to PyPI."""
    try:
        # 1. Update version
        update_version_in_pyproject(version)

        # 2. Run tests
        run_tests()

        # 3. Build package
        build_package()

        # 4. Git tag
        create_git_tag(version)

        if dry_run:
            console.print("[yellow]Dry run - stopping before publish[/]")
            return

        # 5. Publish
        publish_to_pypi(test=test)

        # 6. Push to GitHub
        push_to_github()

        console.print(f"[bold green]✅ Released v{version} successfully![/]")

        if test:
            console.print("\n[cyan]Install from TestPyPI:[/]")
            console.print(f"pip install --index-url https://test.pypi.org/simple/ coffee-maker=={version}")
        else:
            console.print("\n[cyan]Users can now install:[/]")
            console.print(f"pip install coffee-maker=={version}")

    except Exception as e:
        console.print(f"[red]❌ Release failed: {e}[/]")
        raise click.Abort()
```

**Usage Examples**:
```bash
# Dry run (build but don't publish)
project-manager release 0.1.0 --dry-run

# Publish to TestPyPI (test first)
project-manager release 0.1.0 --test

# Publish to production PyPI
project-manager release 0.1.0

# Publish new version
project-manager release 0.2.0
```

**Checklist Before Release**:
- [ ] All tests passing (`pytest tests/`)
- [ ] All code formatted (`black coffee_maker/`)
- [ ] All linting passed (`ruff check coffee_maker/`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with changes
- [ ] Version number follows semver (MAJOR.MINOR.PATCH)

**Release Steps Automated**:
1. ✅ Update version in pyproject.toml
2. ✅ Run full test suite (blocks if tests fail)
3. ✅ Build wheel and sdist packages
4. ✅ Create git commit and tag (v{version})
5. ✅ Upload to PyPI/TestPyPI via twine
6. ✅ Push commit and tags to GitHub

**Safety Features**:
- Tests must pass or release aborts
- Git tag prevents re-releasing same version
- --dry-run option to test without publishing
- --test option to publish to TestPyPI first
- Clear error messages if any step fails

**What Users See After Release**:
```bash
$ project-manager release 0.1.0

📦 Releasing coffee-maker v0.1.0...

[1/6] Updating version...
✅ Updated version to 0.1.0

[2/6] Running tests...
================================ test session starts =================================
collected 45 items

tests/test_daemon.py ..................                                      [ 40%]
tests/test_project_manager.py .................                             [ 77%]
tests/test_integration.py ..........                                        [100%]

================================ 45 passed in 12.3s ==================================
✅ All tests passed

[3/6] Building package...
✅ Package built successfully

[4/6] Creating git tag v0.1.0...
✅ Created git tag v0.1.0

[5/6] Publishing to PyPI...
Uploading distributions to https://upload.pypi.org/legacy/
coffee_maker-0.1.0-py3-none-any.whl 100% ━━━━━━━━━━━━━━━━━━━━━━━
coffee_maker-0.1.0.tar.gz 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Published to PyPI

[6/6] Pushing to GitHub...
✅ Pushed to GitHub

✅ Released v0.1.0 successfully!

Users can now install:
  pip install coffee-maker==0.1.0
```

---

### Future Enhancements (Post-PRIORITY 3)

- **Auto-update**: Check for new versions on startup
- **Shell completion**: Add bash/zsh completion scripts
- **Configuration file**: ~/.coffee-maker/config.toml
- **Multiple installations**: Support multiple project installations
- **Version management**: `coffee-maker upgrade` command
- **GitHub Release**: Create GitHub Release with changelog automatically
- **Rollback**: `project-manager rollback` if release has issues

---

**This makes coffee-maker installable and distributable - users can now `pip install coffee-maker` and get both binaries system-wide!** 📦🚀

---

## 📊 PRIORITY 4: Developer Status Dashboard

**Goal**: Enhance `project-manager` to display real-time `code-developer` status, progress, and questions

**Duration**: 1-2 days (6-12 hours)
**Dependencies**: PRIORITY 1 (Daemon), PRIORITY 2 (PM CLI), PRIORITY 3 (Package & Binaries)
**Status**: 📝 Planned

### Why This Is Critical

After implementing PRIORITY 1 (Daemon) and PRIORITY 2 (PM UI), the user has:
- ✅ Autonomous developer working 24/7
- ✅ Simple CLI to view roadmap and notifications

**But the user doesn't know**:
- ❓ What is the developer doing RIGHT NOW?
- ❓ Is it stuck? Is it making progress?
- ❓ How long until current task is done?
- ❓ Are there questions waiting for me?

**This priority solves visibility gap**: User always knows developer status without asking!

---

### Core Features

#### 1. Real-Time Developer Status Display

**Command**: `project-manager developer-status`

**Output**:
```
🤖 CODE DEVELOPER STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: 🟢 WORKING
Current Task: PRIORITY 3 - Developer Status Dashboard
Progress: ████████████░░░░░░░░ 60% complete

Started: 2025-10-09 10:30:00 (2h 15m ago)
Elapsed: 2h 15m
ETA: ~1h 30m remaining

Current Step: Writing status dashboard UI
Last Activity: 2 minutes ago - Committed status display logic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recent Activity (last 30 min):
  • 10:45 - Created status.py module
  • 10:52 - Implemented real-time status tracking
  • 11:05 - Added progress calculation logic
  • 11:20 - Committed changes (3 files modified)
  • 11:30 - Running tests (pytest in progress...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions Waiting for Response: 0
Pending Notifications: 0

Next: Run tests → Create PR → Move to next priority
```

#### 2. Developer States

**Possible States**:
- 🟢 **WORKING**: Actively implementing current task
- 🟡 **TESTING**: Running tests, waiting for results
- 🔴 **BLOCKED**: Waiting for user response (dependency approval, design decision)
- ⚪ **IDLE**: Between tasks, reading roadmap
- 🔵 **THINKING**: Analyzing codebase, planning implementation
- 🟣 **REVIEWING**: Creating PR, writing documentation
- ⚫ **STOPPED**: Daemon not running

**State Transitions**:
```
IDLE → THINKING → WORKING → TESTING → REVIEWING → IDLE
                    ↓
                 BLOCKED (if needs user input)
                    ↓
                 WORKING (after user responds)
```

#### 3. Progress Tracking

**Progress Indicators**:
```python
# Developer reports progress at key milestones
progress_milestones = {
    0: "Starting task",
    10: "Read requirements",
    20: "Analyzed codebase",
    30: "Designed solution",
    40: "Implementing core logic",
    50: "Half done",
    60: "Core functionality complete",
    70: "Adding tests",
    80: "Tests passing",
    90: "Creating documentation",
    95: "Creating PR",
    100: "Task complete"
}
```

**ETA Calculation**:
```python
# Based on historical task completion times
avg_time_per_priority = {
    "PRIORITY 1": 8 hours,
    "PRIORITY 2": 6 hours,
    "PRIORITY 3": 4 hours
}

# Adjusts dynamically based on actual progress
elapsed_time = now - started_at
progress_rate = current_progress / elapsed_time
estimated_remaining = (100 - current_progress) / progress_rate
```

#### 4. Activity Log

**Tracked Activities**:
- File modifications (which files, how many lines changed)
- Git operations (commits, branch creation, pushes)
- Test runs (passed, failed, skipped)
- Questions asked (to PM or user)
- Dependency requests
- Errors encountered

**Log Format**:
```json
{
  "timestamp": "2025-10-09T11:30:00Z",
  "activity_type": "git_commit",
  "description": "Committed status display logic",
  "details": {
    "files_modified": 3,
    "lines_added": 145,
    "lines_deleted": 12,
    "commit_hash": "abc1234"
  }
}
```

#### 5. Questions Dashboard

**Display Pending Questions**:
```
❓ QUESTIONS WAITING FOR RESPONSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Q1] Dependency Approval - WAITING 15 minutes
  Package: pandas>=2.0.0
  Reason: Required for CSV export with advanced filtering
  Options: approve, reject
  Command: project-manager respond q1 approve

[Q2] Design Decision - WAITING 5 minutes
  Question: Use REST API or GraphQL for data export?
  Context: REST is simpler, GraphQL is more flexible
  Options: rest, graphql
  Command: project-manager respond q2 rest

Total waiting: 2 questions
Developer is BLOCKED until you respond!
```

---

### Architecture

#### Status File (`data/developer_status.json`)

```json
{
  "status": "working",
  "current_task": {
    "priority": 3,
    "name": "Developer Status Dashboard",
    "started_at": "2025-10-09T10:30:00Z",
    "progress": 60,
    "eta_seconds": 5400
  },
  "current_step": "Writing status dashboard UI",
  "last_activity": {
    "timestamp": "2025-10-09T11:30:00Z",
    "type": "git_commit",
    "description": "Committed status display logic"
  },
  "questions": [
    {
      "id": "q1",
      "type": "dependency_approval",
      "message": "May I install 'pandas>=2.0.0'?",
      "created_at": "2025-10-09T11:15:00Z",
      "status": "pending"
    }
  ],
  "activity_log": [
    {
      "timestamp": "2025-10-09T10:45:00Z",
      "type": "file_created",
      "description": "Created status.py module"
    },
    {
      "timestamp": "2025-10-09T10:52:00Z",
      "type": "code_change",
      "description": "Implemented real-time status tracking"
    }
  ],
  "metrics": {
    "tasks_completed_today": 0,
    "total_commits_today": 4,
    "tests_passed_today": 12,
    "tests_failed_today": 0
  }
}
```

#### Integration with code-developer

**Developer reports status**:
```python
# In code-developer daemon
class DeveloperStatus:
    def __init__(self):
        self.status_file = Path("data/developer_status.json")

    def update_status(self, status: str, task: Dict, progress: int):
        """Update status file with current state."""
        status_data = {
            "status": status,
            "current_task": task,
            "progress": progress,
            "last_activity": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "status_update"
            }
        }

        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

    def report_activity(self, activity_type: str, description: str):
        """Add activity to log."""
        # Read current status
        status = self._load_status()

        # Add activity
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": activity_type,
            "description": description
        }
        status["activity_log"].append(activity)

        # Keep only last 50 activities
        status["activity_log"] = status["activity_log"][-50:]

        # Save
        self._save_status(status)

    def report_progress(self, progress: int, current_step: str):
        """Update progress percentage."""
        status = self._load_status()
        status["current_task"]["progress"] = progress
        status["current_step"] = current_step

        # Calculate ETA
        elapsed = datetime.utcnow() - datetime.fromisoformat(
            status["current_task"]["started_at"].replace("Z", "")
        )
        if progress > 0:
            total_estimated = elapsed.total_seconds() * (100 / progress)
            remaining = total_estimated - elapsed.total_seconds()
            status["current_task"]["eta_seconds"] = int(remaining)

        self._save_status(status)
```

#### Integration with project-manager

**PM CLI displays status**:
```python
# In project-manager CLI
class DeveloperStatusDisplay:
    def show_status(self):
        """Display developer status in terminal."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.progress import Progress

        console = Console()
        status = self._load_status()

        # Status indicator with emoji
        status_emoji = {
            "working": "🟢",
            "testing": "🟡",
            "blocked": "🔴",
            "idle": "⚪",
            "thinking": "🔵"
        }

        # Progress bar
        progress = status["current_task"]["progress"]

        # Format output
        console.print(Panel(
            f"{status_emoji[status['status']]} {status['status'].upper()}\n"
            f"Task: {status['current_task']['name']}\n"
            f"Progress: {progress}%\n"
            f"ETA: {self._format_eta(status['current_task']['eta_seconds'])}",
            title="🤖 CODE DEVELOPER STATUS"
        ))
```

---

### Implementation Steps

**Day 1** (4-6 hours):
1. Create `data/developer_status.json` schema
2. Add status reporting to `code-developer` daemon:
   - `update_status()` method
   - `report_activity()` method
   - `report_progress()` method
3. Add status display to `project-manager`:
   - `developer-status` command
   - Rich terminal formatting
   - Real-time refresh option

**Day 2** (2-4 hours):
4. Add activity log tracking (last 50 activities)
5. Add questions dashboard integration
6. Add metrics tracking (commits, tests, etc.)
7. Test full workflow:
   - Start daemon → Check status → See progress
   - Developer asks question → Shows in PM
   - Respond → Developer unblocks

---

### Success Criteria

✅ **User can always see developer status**:
- Run `project-manager developer-status` → See current state
- Know if developer is working, blocked, or idle

✅ **User knows progress**:
- See percentage complete (0-100%)
- See ETA (estimated time remaining)
- See recent activities (last 30 min)

✅ **User sees questions immediately**:
- Questions show up in status view
- Clear call-to-action (respond command)
- Developer unblocks after response

✅ **Updates are real-time**:
- Status file updates every minute (or on state change)
- PM CLI shows fresh data
- Optional: `--watch` mode for continuous updates

---

### Future Enhancements (Post-PRIORITY 3)

- **Web UI**: Browser-based status dashboard (instead of terminal)
- **Push Notifications**: Desktop/mobile alerts when developer asks questions
- **Historical Tracking**: Graph of progress over time
- **Multi-Developer**: Track multiple developers working in parallel
- **Slack Integration**: Developer status posts to Slack channel

---

**This gives the user complete visibility into what the autonomous developer is doing, removing the "black box" feeling and building trust!** 📊🤖

---

## 🔄 Recurring Best Practices

**Philosophy**: Every new feature implementation is an opportunity to improve the entire codebase. These practices should be applied **continuously** throughout development, not as separate tasks.

### 1. 🗃️ Database Synchronization Review ⚡ **CRITICAL**

**When**: Before implementing ANY feature that touches the database
**Why**: Daemon runs in isolated Docker environment - data must be accessible to both daemon and user

**Checklist**:
- [ ] Does this feature write to database? → Verify write goes to shared database path
- [ ] Does this feature read from database? → Verify read comes from shared database path
- [ ] Will daemon need this data? → Ensure it's in shared `/project/data/` directory
- [ ] Will user's tools need this data? → Ensure notifications/analytics are synced
- [ ] Are there concurrent writes? → Apply `@with_retry` decorator + WAL mode
- [ ] New database table? → Update Data Ownership Matrix in PRIORITY 1.5 design doc

**Common Pitfall**: Creating database in daemon's isolated `/daemon-env/data/` instead of shared `/project/data/`

**Reference**: `docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`

---

### 2. 🧹 Code Refactoring & Simplification

**When**: After implementing any feature, before marking it complete
**Why**: Technical debt accumulates quickly - clean as you build

**Sprint 1 Example** (Real work done):
- ✅ 800+ lines removed (deprecated code)
- ✅ 27 lines duplication eliminated (time threshold calculations)
- ✅ Manual retry loops → `@with_retry` decorator (11 methods)
- ✅ Missing observability → `@observe` decorator (11 methods)

**Refactoring Opportunities to Look For**:

**A. Manual Retry Loops → Centralized Utilities**
```python
# BEFORE (18 lines, repeated 3x):
attempt = 0
while attempt < 3:
    try:
        return self.invoke(**kwargs)
    except RateLimitError as e:
        print("Rate limit reached...")
        time.sleep(2**attempt)
        attempt += 1

# AFTER (cleaner, observable):
@with_retry(
    max_attempts=3,
    backoff_base=2.0,
    retriable_exceptions=(RateLimitError,),
)
def _invoke_with_retry():
    return self.invoke(**kwargs)
```

**B. Duplicate Calculations → Reusable Utilities**
```python
# BEFORE (9 lines, repeated 3x = 27 lines):
now = time.time()
if timeframe == "day":
    threshold = now - 86400
elif timeframe == "hour":
    threshold = now - 3600
# ... etc

# AFTER (1 line):
threshold = get_timestamp_threshold(timeframe)
```

**C. Missing Observability → Add `@observe` Decorator**
```python
# Add to all database queries, analytics methods, cost tracking
@observe
@with_retry(
    max_attempts=3,
    retriable_exceptions=(OperationalError, TimeoutError),
)
def get_llm_performance(self, days: int = 7) -> Dict:
    """Get LLM performance metrics."""
    # ... existing logic
```

**Checklist**:
- [ ] Search for repeated code patterns (copy-paste duplication)
- [ ] Identify manual retry/backoff logic → replace with `@with_retry`
- [ ] Find missing `@observe` decorators on critical methods
- [ ] Look for hard-coded magic numbers → extract to constants
- [ ] Check for orphaned/commented-out code → delete it
- [ ] Verify type hints on all public functions
- [ ] Run `ruff check` and `mypy` - fix all issues

**Reference**: `docs/sprint1_improvements_summary.md`

---

### 3. 📝 Documentation Updating

**When**: Immediately after changing any public API or adding features
**Why**: Stale documentation is worse than no documentation

**What to Update**:
- [ ] **Docstrings**: Update function/class docstrings with new parameters
- [ ] **ROADMAP.md**: Mark features complete, update status
- [ ] **README.md**: Add new CLI commands, update examples
- [ ] **Type hints**: Add/update return types and parameter types
- [ ] **Architecture docs**: Update diagrams if structure changed
- [ ] **Migration guides**: Document breaking changes

**Example**:
```python
# Update docstrings with type hints
def calculate_cost(
    self,
    timeframe: Literal["minute", "hour", "day", "all"] = "all",
    model: Optional[str] = None,
) -> Dict[str, float]:
    """Calculate LLM usage cost for a timeframe.

    Args:
        timeframe: Time window for cost calculation
        model: Optional model filter

    Returns:
        Dictionary with total_cost, input_cost, output_cost

    Example:
        >>> calc.calculate_cost(timeframe="day", model="gpt-4")
        {'total_cost': 5.23, 'input_cost': 2.10, 'output_cost': 3.13}
    """
```

**Tools**:
- Run `pdoc` to regenerate API docs: `python scripts/generate_docs.py`
- Check for TODO/FIXME comments: `grep -r "TODO\|FIXME" coffee_maker/`

---

### 4. 🧪 Test Coverage Maintenance

**When**: Before committing any changes
**Why**: Tests are living documentation and prevent regressions

**Checklist**:
- [ ] New feature → Add unit tests
- [ ] Bug fix → Add regression test
- [ ] Refactoring → Ensure existing tests still pass
- [ ] Database changes → Add integration tests
- [ ] API changes → Update API tests

**Test Philosophy**:
```python
# Test BEHAVIOR, not implementation
# GOOD:
def test_retry_exhaustion_returns_none():
    """When retries exhausted, should return None."""

# BAD:
def test_retry_calls_sleep_three_times():
    """Should call time.sleep() exactly 3 times."""
```

**Sprint 1 Results**: 112 tests passing (retry + time + analytics)

**Commands**:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=coffee_maker --cov-report=html

# Run specific test file
pytest tests/unit/test_analytics.py -v
```

---

### 5. 🎨 Code Formatting & Linting

**When**: Before every commit (automated via pre-commit hooks)
**Why**: Consistent style improves readability and reduces diff noise

**Tools** (already configured):
- **black**: Code formatting
- **ruff**: Fast linting
- **mypy**: Type checking
- **isort**: Import sorting

**Commands**:
```bash
# Format all code
black coffee_maker/ tests/

# Lint and auto-fix
ruff check coffee_maker/ tests/ --fix

# Type check
mypy coffee_maker/

# Run all pre-commit hooks
pre-commit run --all-files
```

**Pre-commit Integration**: Hooks run automatically on `git commit`

---

### 6. 🔍 Performance Profiling

**When**: After implementing compute-intensive features
**Why**: LLM operations are expensive - optimize early

**What to Profile**:
- [ ] Database queries (use `EXPLAIN QUERY PLAN`)
- [ ] LLM token usage (via Langfuse analytics)
- [ ] Retry/timeout settings (too aggressive?)
- [ ] Connection pool size (too small/large?)

**Example**:
```python
# Profile database query performance
import time
start = time.time()
results = conn.execute("SELECT * FROM traces WHERE ...").fetchall()
print(f"Query took {time.time() - start:.2f}s")

# Use Langfuse to track LLM costs
@observe(capture_input=False, capture_output=False)
def expensive_llm_call():
    # Langfuse automatically tracks tokens, cost, latency
    pass
```

**Tools**:
- Langfuse dashboard for LLM metrics
- `cProfile` for Python profiling
- SQLite `EXPLAIN QUERY PLAN` for queries

---

### 7. 🔐 Security Review

**When**: Before releasing features that touch external APIs or user data
**Why**: LLM systems handle sensitive data - security first

**Checklist**:
- [ ] API keys stored in environment variables (not code)
- [ ] Database paths don't leak sensitive info
- [ ] User inputs sanitized before database queries
- [ ] Error messages don't expose internal details
- [ ] Logs don't contain API keys or secrets

**Example**:
```python
# GOOD:
api_key = os.environ.get("OPENAI_API_KEY")
logger.info("API request completed")

# BAD:
api_key = "sk-..."  # Hard-coded
logger.info(f"API request with key {api_key}")
```

---

### 8. 📊 Analytics & Observability

**When**: For all critical operations (LLM calls, database queries, external APIs)
**Why**: Can't optimize what you can't measure

**Add Observability**:
```python
# LLM operations
@observe
def call_llm(prompt: str) -> str:
    # Langfuse tracks: tokens, cost, latency, model
    pass

# Database operations
@observe
@with_retry(retriable_exceptions=(OperationalError,))
def get_traces(days: int) -> List[Dict]:
    # Track query performance and retries
    pass

# Critical business logic
@observe(capture_input=True, capture_output=True)
def process_roadmap_update(changes: Dict) -> bool:
    # Track input/output for debugging
    pass
```

**Sprint 1 Results**: 11 critical methods now observable in Langfuse

---

### 9. 🗂️ Dependency Management

**When**: Monthly review or when adding new dependencies
**Why**: Outdated dependencies have security vulnerabilities

**Commands**:
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade langchain

# Update all packages (carefully!)
pip install --upgrade -r requirements.txt

# Security audit
pip-audit
```

**Best Practices**:
- Pin major versions: `langchain>=0.1.0,<0.2.0`
- Use `requirements-dev.txt` for dev dependencies
- Keep virtual environment clean

#### 🤖 DAEMON REQUIREMENT: New Dependency Approval ⚡ **CRITICAL**

**Rule**: The autonomous daemon **MUST ask for user permission** before adding any new dependency.

**Why This Is Critical**:

1. **Security** 🔐 - Dependencies can contain malicious code (supply chain attacks)
2. **License Compliance** ⚖️ - GPL in proprietary code = legal violation
3. **Cost Management** 💰 - Some dependencies have API usage costs
4. **Codebase Bloat** 📦 - `pandas` (200MB) when `csv` suffices
5. **Maintenance Burden** 🔧 - More dependencies = more updates, more breaking changes
6. **Version Conflicts** ⚠️ - New dependency may conflict with existing ones

**Implementation Pattern**:
```python
def request_dependency_approval(self, package: str, reason: str) -> bool:
    """Request user approval before installing dependency."""
    notification = f"""
🤖 DAEMON REQUEST: New Dependency Approval

Package: {package}
Reason: {reason}

Please review:
- Check package on PyPI (security, license, maintainers)
- Verify license compatibility
- Approve: /approve-dependency {package}
- Reject: /reject-dependency {package}
"""
    self.send_notification(notification)
    return self.wait_for_user_response(timeout=3600)  # 1 hour
```

**Example**:
```
🤖 DAEMON: May I install 'psycopg2-binary>=2.9.9'?
Reason: Required for PostgreSQL connection (PRIORITY 2)
License: LGPL-3.0
Size: ~5MB

👤 USER: /reject-dependency psycopg2-binary
Reason: We're using SQLite MVP, not PostgreSQL yet.

🤖 DAEMON: Acknowledged. Using sqlite3 (standard library).
```

**Pre-Approved Dependencies** (no permission needed):
- Standard library modules (no install)
- Already in `requirements.txt`
- Testing/linting (dev dependencies)

**This protects users from**:
- ✅ Malicious packages
- ✅ License violations
- ✅ Unexpected costs
- ✅ Bloat/conflicts
- ✅ Maintenance burden

**Non-negotiable for autonomous systems.** 🔐

---

### 10. 🎯 Roadmap Synchronization

**When**: After completing any feature or making architectural decisions
**Why**: ROADMAP.md is the source of truth for the autonomous daemon

**What to Update**:
- [ ] Mark completed priorities with ✅
- [ ] Update timelines based on actual effort
- [ ] Add new priorities discovered during implementation
- [ ] Update dependency chains (PRIORITY X → PRIORITY Y)
- [ ] Document architectural decisions (ADRs)
- [ ] Update estimates based on learnings

**Tool**: Use `coffee-roadmap` CLI (PRIORITY 2) for all roadmap updates

---

### 11. 🔄 GitHub CI/CD Monitoring (Daily Task)

**When**: Daily, after pushing to GitHub
**Why**: Catch CI failures early before they block development

**Daily Checklist**:
- [ ] Check if branch is pushed to remote (`git status`, `git branch -r`)
- [ ] Verify GitHub Actions are passing
- [ ] Review any failing tests or linting errors
- [ ] Fix issues immediately (don't let them accumulate)
- [ ] Ensure PR status checks are green before merging

**Commands**:
```bash
# Check remote branch status
git status
git branch -r | grep feature/your-branch

# Push if not synced
git push origin feature/your-branch

# Check GitHub Actions via CLI (requires gh CLI)
gh run list --branch feature/your-branch --limit 5

# View specific workflow run
gh run view <run-id>

# View logs for failed run
gh run view <run-id> --log-failed
```

**GitHub Actions to Monitor**:
- ✅ **Tests**: All pytest tests passing
- ✅ **Linting**: black, ruff, mypy checks
- ✅ **Type Checking**: mypy strict mode
- ✅ **Security**: pip-audit for vulnerabilities
- ✅ **Build**: Package builds successfully

**If CI Fails**:

1. **Read the error logs**:
   ```bash
   gh run view <run-id> --log-failed
   ```

2. **Reproduce locally**:
   ```bash
   # Run the same checks that GitHub Actions runs
   pytest tests/ -v
   black --check coffee_maker/ tests/
   ruff check coffee_maker/ tests/
   mypy coffee_maker/
   ```

3. **Fix the issue**:
   - Fix failing tests
   - Fix linting/formatting errors
   - Fix type errors
   - Update dependencies if needed

4. **Push the fix**:
   ```bash
   git add .
   git commit -m "fix: Resolve CI failures - <brief description>"
   git push
   ```

5. **Verify fix**:
   ```bash
   gh run list --branch feature/your-branch --limit 1
   ```

**Automation Tips**:
```bash
# Add alias to check CI status
alias ci-status='gh run list --branch $(git branch --show-current) --limit 5'

# Check CI in watch mode (updates every 10s)
watch -n 10 'gh run list --branch $(git branch --show-current) --limit 1'
```

**🤖 DAEMON REQUIREMENT**:
The autonomous daemon **MUST** check CI status after every push and fix any failures before moving to next task. If CI fails:
1. Read error logs
2. Fix the issue
3. Push fix
4. Wait for CI to pass
5. Only then proceed to next task

**Example Workflow**:
```
Daemon pushes code → GitHub Actions run → CI fails (test failure)
↓
Daemon detects failure via `gh run list`
↓
Daemon reads logs via `gh run view --log-failed`
↓
Daemon fixes the test
↓
Daemon pushes fix
↓
Daemon waits for CI to pass (polls every 30s)
↓
CI passes ✅ → Daemon continues to next task
```

**Why This Matters**:
- **Prevents broken main**: Don't merge PRs with failing CI
- **Fast feedback**: Fix issues while context is fresh
- **Professional quality**: Passing CI is minimum bar
- **Team productivity**: Broken CI blocks everyone

---

### 12. 🔐 Security Vulnerability Monitoring (Daily Task)

**When**: Daily, first thing in the morning
**Why**: Security vulnerabilities can be exploited - fix immediately

**Priority**: 🚨 **TOP PRIORITY** - Security issues block all other work

**Daily Checklist**:
- [ ] Check GitHub Security tab for Dependabot alerts
- [ ] Review severity (Critical > High > Moderate > Low)
- [ ] For each vulnerability: Assess impact and create fix plan
- [ ] Fix vulnerabilities or document reason for delay
- [ ] Update dependencies with security patches

#### 🚨 Current Active Vulnerabilities (as of 2025-10-09)

**Status**: 5 vulnerabilities detected on default branch (main)
**Link**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/security/dependabot

**Action Required**:
- [ ] **1 HIGH severity vulnerability** - Fix immediately (today)
- [ ] **4 MODERATE severity vulnerabilities** - Fix within 24 hours

**TODO**:
1. [ ] Access GitHub Security tab to identify specific packages and CVEs
2. [ ] For HIGH severity:
   - [ ] Identify affected package and vulnerable version
   - [ ] Check if we're using the vulnerable functionality
   - [ ] Update to patched version or apply mitigation
   - [ ] Run full test suite to verify fix
   - [ ] Commit with security prefix: `security: Fix CVE-XXXX in <package>`
3. [ ] For MODERATE severity (repeat for each):
   - [ ] Identify package and assess impact
   - [ ] Update to patched versions
   - [ ] Test and commit fixes
4. [ ] Verify all alerts resolved on GitHub Security tab
5. [ ] Document any mitigations or reasons for delay

**Priority**: 🚨 **HIGH severity must be fixed before any new feature work**

**Commands**:
```bash
# View security alerts via GitHub web UI
open https://github.com/Bobain/MonolithicCoffeeMakerAgent/security

# Check for vulnerable dependencies (local scan)
pip-audit

# Check specific package for vulnerabilities
pip-audit | grep <package-name>

# Update vulnerable package
pip install --upgrade <package-name>

# Check if update breaks anything
pytest tests/ -v
```

**Workflow for Security Alerts**:

1. **Identify Alert**:
   - Go to GitHub → Security → Dependabot alerts
   - Note severity, affected package, vulnerable version range
   - Read CVE details and impact assessment

2. **Assess Impact**:
   ```bash
   # Check where vulnerable package is used
   grep -r "import <package>" coffee_maker/ tests/

   # Check if we're affected by the vulnerability
   # (some CVEs only affect specific use cases)
   ```

3. **Determine Action**:
   - **Critical/High severity**: Fix immediately (drop everything)
   - **Moderate severity**: Fix within 24 hours
   - **Low severity**: Fix within 1 week

4. **Fix Options**:

   **Option A: Update Dependency** (Preferred)
   ```bash
   # Update to patched version
   pip install --upgrade <package>==<safe-version>

   # Update requirements.txt
   pip freeze | grep <package> >> requirements.txt

   # Test everything
   pytest tests/ -v
   black coffee_maker/ tests/
   mypy coffee_maker/
   ```

   **Option B: Wait for Third-Party Fix**
   If vulnerability is in a dependency we can't easily update:
   ```markdown
   # Create tracking issue
   Title: [SECURITY] Waiting for <package> security patch

   Description:
   - CVE: CVE-2024-XXXXX
   - Severity: High
   - Affected package: <package> <version>
   - Our mitigation: <describe workaround>
   - Tracking: <link to upstream issue>
   - ETA: <expected patch date>
   ```

   **Option C: Replace Dependency**
   If patch isn't available and risk is high:
   ```bash
   # Find alternative package
   pip search <alternative>

   # Ask user permission to replace dependency
   # (DAEMON MUST ASK PERMISSION - Section 9)
   ```

   **Option D: Mitigate Risk**
   If we can't update immediately:
   ```python
   # Add input validation
   # Disable vulnerable feature
   # Add rate limiting
   # Add monitoring/alerts
   ```

5. **Test Fix**:
   ```bash
   # Run full test suite
   pytest tests/ -v --cov=coffee_maker

   # Check for breaking changes
   python -m coffee_maker.cli.project_manager --version

   # Manual smoke test of critical features
   ```

6. **Document Fix**:
   ```bash
   git add requirements.txt
   git commit -m "security: Fix CVE-2024-XXXXX in <package>

   - Updated <package> from <old> to <new>
   - CVE severity: <High/Moderate/Low>
   - Impact: <describe what was vulnerable>
   - Tests: All passing

   Fixes: #<issue-number>"

   git push
   ```

7. **Verify on GitHub**:
   - GitHub Security tab should show alert as resolved
   - Dependabot should close the alert automatically
   - If not, manually dismiss with explanation

**🤖 DAEMON REQUIREMENT**:
The autonomous daemon **MUST** check security alerts daily and prioritize fixes:

1. **Every morning (00:00 UTC)**:
   - Check GitHub Security tab (via GitHub API)
   - Count alerts by severity
   - If Critical/High alerts exist: **PAUSE ALL OTHER WORK**

2. **Security-First Priority**:
   ```
   Critical/High vulnerability detected → STOP current task
   ↓
   Assess vulnerability impact
   ↓
   IF fix available: Apply update + test + commit + push
   IF no fix: Document mitigation + notify user
   ↓
   Verify alert resolved on GitHub
   ↓
   Resume previous task
   ```

3. **User Notification**:
   ```
   🚨 SECURITY ALERT: Critical vulnerability detected

   Package: requests==2.28.0
   CVE: CVE-2024-12345
   Severity: HIGH (8.5/10)

   Impact: Server-Side Request Forgery (SSRF)
   Fix available: requests==2.31.0

   Action: Updating dependency and running tests...
   [Progress bar]
   ✅ Fixed and verified. All tests passing.

   Commit: abc1234
   Branch: security/fix-requests-ssrf
   PR: #456
   ```

**Automation Script** (Future):
```python
# File: scripts/check_security_alerts.py
"""
Daily security alert checker.
Run: python scripts/check_security_alerts.py
"""

import requests
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "Bobain/MonolithicCoffeeMakerAgent"

def check_security_alerts():
    """Check GitHub Dependabot alerts."""
    url = f"https://api.github.com/repos/{REPO}/dependabot/alerts"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    alerts = response.json()

    # Filter by severity
    critical = [a for a in alerts if a['security_advisory']['severity'] == 'critical']
    high = [a for a in alerts if a['security_advisory']['severity'] == 'high']

    if critical or high:
        print(f"🚨 {len(critical)} critical, {len(high)} high severity alerts!")
        return False
    else:
        print("✅ No critical/high security alerts")
        return True

if __name__ == "__main__":
    check_security_alerts()
```

**Example: Current Alerts (2025-10-09)**:
As of the last push, GitHub reported:
- 1 High severity vulnerability
- 4 Moderate severity vulnerabilities

**Next actions**:
1. Review: https://github.com/Bobain/MonolithicCoffeeMakerAgent/security/dependabot
2. Fix high severity issue immediately
3. Schedule moderate severity fixes within 24 hours

**Why This Matters**:
- **Prevents exploits**: Unpatched vulnerabilities = attack surface
- **Compliance**: Many organizations require <24h fix for high severity
- **Reputation**: Security issues damage trust
- **Legal risk**: Data breaches have legal consequences
- **Supply chain security**: Dependencies can be compromised

**Golden Rule**: When in doubt, fix security issues before features 🔐

---

### 13. 🔄 Daily Refactoring Opportunity Review

**When**: Daily, after completing any feature or update
**Why**: Small, incremental refactoring prevents technical debt accumulation

**Philosophy**: "Leave code cleaner than you found it" - Every change is an opportunity to improve

**Daily Questions to Ask**:

1. **Does this update create duplication?**
   ```python
   # BAD: Duplicated logic in two places
   def process_user_data(data):
       if data.get('name'):
           cleaned_name = data['name'].strip().lower()
           # ... 20 more lines ...

   def process_admin_data(data):
       if data.get('name'):
           cleaned_name = data['name'].strip().lower()  # DUPLICATE!
           # ... 20 more lines ...

   # GOOD: Extract common logic
   def clean_name(name: str) -> str:
       return name.strip().lower()

   def process_user_data(data):
       if data.get('name'):
           cleaned_name = clean_name(data['name'])
   ```

2. **Can this logic be simplified?**
   ```python
   # BAD: Overly complex
   def is_valid_user(user):
       if user is not None:
           if user.get('active'):
               if user.get('verified'):
                   return True
       return False

   # GOOD: Simplified
   def is_valid_user(user):
       return (user is not None
               and user.get('active', False)
               and user.get('verified', False))
   ```

3. **Are there new patterns that could be utilities?**
   ```python
   # If you find yourself writing similar code 3+ times:
   # → Extract to utility function or decorator

   # Example: Retry pattern repeated across multiple functions
   # → Already extracted to @with_retry decorator ✅
   ```

4. **Do function/variable names clearly communicate intent?**
   ```python
   # BAD: Unclear names
   def f(d):
       r = []
       for x in d:
           if x['s'] == 'active':
               r.append(x)
       return r

   # GOOD: Clear names
   def filter_active_users(users: List[Dict]) -> List[Dict]:
       active_users = []
       for user in users:
           if user['status'] == 'active':
               active_users.append(user)
       return active_users

   # EVEN BETTER: Using comprehension
   def filter_active_users(users: List[Dict]) -> List[Dict]:
       return [u for u in users if u['status'] == 'active']
   ```

5. **Could this be more type-safe?**
   ```python
   # BAD: Weak typing
   def process_data(data):
       return data.get('value', 0) * 2

   # GOOD: Strong typing
   from typing import Dict, Any

   def process_data(data: Dict[str, Any]) -> float:
       value = data.get('value', 0.0)
       return float(value) * 2.0
   ```

6. **Is there dead code or commented-out code?**
   ```python
   # BAD: Leaving commented code "just in case"
   def process_order(order):
       # Old implementation (keeping for reference)
       # result = old_way(order)
       # if result:
       #     return result

       # New implementation
       return new_way(order)

   # GOOD: Remove old code (it's in git history!)
   def process_order(order):
       return new_way(order)
   ```

**Daily Workflow**:

1. **Review Today's Changes**:
   ```bash
   # What did we change today?
   git diff HEAD~1 --stat

   # View actual changes
   git diff HEAD~1
   ```

2. **Identify Opportunities**:
   ```bash
   # Find potential duplication
   ruff check coffee_maker/ --select UP  # pyupgrade suggestions

   # Find code complexity issues
   ruff check coffee_maker/ --select C90  # McCabe complexity

   # Find overly long functions
   ruff check coffee_maker/ --select PLR0915  # too many statements
   ```

3. **Apply Boy Scout Rule**:
   > "Always leave the campground cleaner than you found it"

   If you touch a file:
   - Fix nearby code smells
   - Improve nearby variable names
   - Add missing type hints
   - Add missing docstrings
   - Remove unused imports

4. **Document Refactoring in Commit**:
   ```bash
   git commit -m "refactor: Simplify user validation logic

   - Extracted clean_name() utility (removes duplication)
   - Simplified is_valid_user() (reduced complexity)
   - Added type hints to process_data()
   - Removed commented-out dead code

   No functional changes, all tests passing."
   ```

**🤖 DAEMON REQUIREMENT**:
After implementing any feature, the daemon **MUST** review code for refactoring opportunities:

```
Implement feature → Tests pass → Daemon analyzes changes
↓
Questions:
- Is there duplication? (>2 similar blocks)
- Is there complexity? (functions >50 lines, nested >3 levels)
- Are there unclear names? (single letter variables, abbreviations)
- Is typing incomplete? (missing type hints)
↓
IF opportunities found:
  Create refactoring subtask
  Apply Boy Scout Rule
  Test again
  Commit refactoring separately
↓
Move to next task
```

**Example: Sprint 1 Refactoring Success** ✅

After implementing analytics features, we reviewed and found:
- **Duplication**: Retry logic repeated 5 times → Extracted `@with_retry` decorator
- **Complexity**: 800+ lines of deprecated code → Removed
- **Naming**: Unclear function names → Renamed for clarity
- **Result**: Cleaner codebase, easier maintenance

**Metrics to Track**:
```bash
# Code complexity (aim for <10 per function)
radon cc coffee_maker/ -s

# Maintainability index (aim for A/B grade)
radon mi coffee_maker/ -s

# Lines of code (should not grow unnecessarily)
cloc coffee_maker/
```

**When NOT to Refactor**:
- ❌ Right before a deadline
- ❌ When changing external API contracts (breaking changes)
- ❌ Large-scale refactoring without planning
- ❌ "Clever" optimizations without profiling

**When TO Refactor**:
- ✅ After adding a feature (clean up while context is fresh)
- ✅ When you notice duplication (3rd occurrence → extract)
- ✅ When tests are green (safe to refactor)
- ✅ Small, incremental improvements (not big rewrites)

**Tools**:
- `ruff check` - Find code quality issues
- `radon` - Measure complexity and maintainability
- `black` - Auto-format (eliminates style debates)
- `mypy` - Type checking (catch errors early)

**Golden Rules**:
1. 🔒 **Never refactor without tests** - Tests are safety net
2. 🔬 **One refactoring at a time** - Small, focused changes
3. 📝 **Separate refactoring commits** - Don't mix with features
4. ✅ **Tests must stay green** - No functional changes during refactor
5. 🎯 **Boy Scout Rule** - Always leave code cleaner

**This prevents technical debt accumulation** - 10 minutes daily saves hours later! ⏰

---

## Summary: Apply These Every Implementation Cycle

1. **Before starting**: Review database sync strategy (PRIORITY 1.5)
2. **During implementation**: Add `@observe` and `@with_retry` decorators
3. **During implementation**: Extract duplicated code to utilities
4. **After implementation**: Update documentation and type hints
5. **Before commit**: Run tests, linting, formatting
6. **After commit**: Update ROADMAP.md status
7. **After push**: Check GitHub Actions CI status and fix any failures ⚡ **NEW**
8. **After feature/update**: Review for refactoring opportunities (Section 13) 🔄 ⚡ **NEW**
9. **After PRIORITY completion**: Create demo + notify user ⚡ **NEW**
10. **Weekly**: Review for refactoring opportunities
11. **Monthly**: Dependency updates and security audit
12. **Daily (TOP PRIORITY)**: Check security vulnerabilities and fix immediately (Section 12) 🔐 ⚡ **NEW**
13. **Daily**: Monitor GitHub CI/CD status (Section 11) ⚡ **NEW**
14. **Daily**: Review if last update adds refactoring opportunities (Section 13) 🔄 ⚡ **NEW**

**🤖 For Autonomous Daemon** (Critical - Non-Negotiable):
- ⚠️ **NEVER STOP ASKING PERMISSION** - This is the CORE PRINCIPLE ⚡
- ⚠️ **ALWAYS ask permission before adding new dependencies**
- ⚠️ **ALWAYS ask permission before making architectural changes**
- ⚠️ **ALWAYS ask permission before breaking changes**
- ⚠️ **ALWAYS ask permission before external API calls**
- Explain why the action is needed
- Provide alternatives when possible
- Wait for user approval (1 hour timeout)
- Never proceed without explicit approval
- ⚠️ **ALWAYS create demo after completing a PRIORITY**

**🔴 CORE PRINCIPLE**: Permission-First Architecture
- This MUST be in MVP (version 0.1.0)
- This MUST be in every published version
- This is NON-NEGOTIABLE for ethical AI
- Daemon is powerful assistant, NOT autonomous overlord

**Goal**: Every feature leaves the codebase cleaner than before ✨

---

### 🎬 Demo & Notification After Priority Completion ⚡ **REQUIRED**

**When**: After completing ANY PRIORITY (before moving to next)

**Why**: User needs to understand what was built and how to use it

**What to Create**:

#### Option A: Interactive Demo (Preferred) 🌟
Create a runnable demonstration showing the new feature in action.

**Format**:
- Jupyter notebook (`.ipynb`) with code + explanations
- Python script with rich terminal output
- Video recording (screen capture with narration)
- GIF animations showing key interactions

**Example** (PRIORITY 2: Project Manager UI):
```bash
# File: demos/priority_2_project_manager_demo.py
"""
Interactive Demo: Project Manager UI

This demo shows how to use the new Project Manager UI to:
1. View roadmap and daemon status
2. Respond to daemon notifications
3. Approve/reject dependency requests

Run: python demos/priority_2_project_manager_demo.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Demo 1: View Roadmap
console.print(Panel("[bold cyan]Demo 1: Viewing Roadmap[/]"))
# ... runnable code ...

# Demo 2: Respond to Notification
console.print(Panel("[bold cyan]Demo 2: Responding to Daemon[/]"))
# ... runnable code ...
```

#### Option B: Documentation (Minimum) 📝
If interactive demo isn't feasible, create comprehensive documentation.

**Format**: Markdown file with:
- Overview of what was built
- Key features and capabilities
- Usage examples (code snippets)
- Screenshots/GIFs of UI
- Troubleshooting tips

**Template**:
```markdown
# PRIORITY X: [Name] - Completion Summary

**Completion Date**: YYYY-MM-DD
**Status**: ✅ Complete
**PR**: #123

## What Was Built

[2-3 paragraph overview]

## Key Features

1. **Feature 1**: Description
   - Sub-feature A
   - Sub-feature B

2. **Feature 2**: Description

## How to Use

### Example 1: Basic Usage
\`\`\`python
# Code example showing how to use
\`\`\`

### Example 2: Advanced Usage
\`\`\`python
# Advanced code example
\`\`\`

## Visual Guide

![Screenshot 1](path/to/screenshot1.png)
*Caption explaining what this shows*

## Testing It Yourself

\`\`\`bash
# Commands to try the new feature
coffee-manager view
coffee-manager status
\`\`\`

## What's Next

This enables PRIORITY X+1...
```

**Storage Location**:
```
demos/
├── priority_1_daemon/
│   ├── README.md                    # Summary document
│   ├── demo.py                      # Interactive demo script
│   ├── demo.ipynb                   # Jupyter notebook
│   └── screenshots/
│       ├── daemon_running.png
│       └── notification_received.png
│
├── priority_2_project_manager/
│   ├── README.md
│   ├── demo.py
│   └── demo.gif                     # Animated GIF
│
└── priority_3_database_sync/
    └── README.md
```

---

### 📬 User Notification

**When**: Immediately after demo is created

**Format**: Send notification through Project Manager UI

```python
# In daemon after completing priority
def notify_completion(priority_name: str, demo_path: str):
    """Notify user that priority is complete with demo link."""

    notification = {
        "type": "priority_completed",
        "priority": priority_name,
        "message": f"✅ {priority_name} is complete!",
        "demo_link": demo_path,
        "pr_link": f"https://github.com/user/repo/pull/{pr_number}",
        "summary": generate_summary(priority_name),
        "next_priority": get_next_priority()
    }

    send_notification(notification)
```

**User sees**:
```
🎉 PRIORITY COMPLETED!

✅ PRIORITY 2: Project Manager UI is complete!

📊 Summary:
   - Built terminal UI with rich library
   - Integrated daemon status display
   - Added notification response system
   - Created 15 new files, 800+ LOC
   - All tests passing (25/25)

🎬 Interactive Demo:
   → demos/priority_2_project_manager/demo.py
   → Run: python demos/priority_2_project_manager/demo.py

📝 Documentation:
   → demos/priority_2_project_manager/README.md

🔗 Pull Request:
   → https://github.com/user/repo/pull/456

⏭️  Next: PRIORITY 3 - Database Synchronization
   Estimated: 2-3 days

[View Demo] [Review PR] [Start Next Priority]
```

---

### 🤖 Daemon Implementation

**Step-by-Step Process**:

```python
# In coffee_maker/autonomous/minimal_daemon.py

async def complete_priority(self, priority_name: str):
    """Complete a priority with demo and notification."""

    # 1. Run final tests
    self.run_tests()

    # 2. Create demo
    demo_path = self.create_demo(priority_name)

    # 3. Generate summary
    summary = self.generate_priority_summary(
        priority_name=priority_name,
        files_changed=self.get_changed_files(),
        lines_added=self.count_lines_added(),
        tests_passing=self.count_tests()
    )

    # 4. Create PR
    pr_url = self.create_pull_request(
        title=f"feat: Complete {priority_name}",
        body=summary + f"\n\nDemo: {demo_path}"
    )

    # 5. Notify user
    self.notify_user_completion(
        priority_name=priority_name,
        demo_path=demo_path,
        pr_url=pr_url,
        summary=summary
    )

    # 6. Update ROADMAP.md
    self.update_roadmap_status(priority_name, "✅ Completed")

    # 7. Wait for user to review before starting next priority
    response = self.wait_for_user_approval(
        message=f"{priority_name} complete. Review PR and demo. Start next priority?",
        timeout=86400  # 24 hours
    )

    if response == "approved":
        self.move_to_next_priority()
    else:
        self.pause_daemon(reason="Waiting for user feedback on completed priority")
```

**Demo Creation**:

```python
def create_demo(self, priority_name: str) -> str:
    """Create demo for completed priority."""

    demo_dir = Path(f"demos/{self.sanitize_name(priority_name)}")
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Generate README with summary
    readme = self.generate_demo_readme(priority_name)
    (demo_dir / "README.md").write_text(readme)

    # Try to create interactive demo
    try:
        demo_script = self.generate_demo_script(priority_name)
        (demo_dir / "demo.py").write_text(demo_script)
    except Exception as e:
        logger.warning(f"Could not generate interactive demo: {e}")

    # Capture screenshots if UI changes
    if self.has_ui_changes(priority_name):
        self.capture_screenshots(demo_dir / "screenshots")

    return str(demo_dir / "README.md")
```

---

### ✅ Checklist for Completion

Before marking PRIORITY as complete, verify:

- [ ] All features implemented
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed and cleaned
- [ ] **Demo created** (interactive or document) ⚡
- [ ] **User notified** with demo link ⚡
- [ ] PR created with demo reference
- [ ] ROADMAP.md updated to ✅ Completed

**If demo is missing**: PRIORITY is NOT complete!

---

### 📊 Demo Quality Standards

**Good Demo Has**:
- ✅ Clear explanation of what was built
- ✅ Runnable examples (not just screenshots)
- ✅ Step-by-step instructions
- ✅ Visual aids (screenshots, GIFs, or video)
- ✅ Troubleshooting section
- ✅ Link to detailed documentation

**Poor Demo** (Don't do this):
- ❌ Just code without explanation
- ❌ "It works, trust me"
- ❌ Broken examples that don't run
- ❌ No visual aids
- ❌ Assumes too much knowledge

---

### 🎯 Benefits

**For User**:
- ✅ Immediately understands what was built
- ✅ Can try the feature hands-on
- ✅ Has reference material for future use
- ✅ Can share demo with others

**For Daemon**:
- ✅ Forces clear documentation of work
- ✅ Validates feature actually works end-to-end
- ✅ Creates knowledge base for future priorities
- ✅ Builds user trust (transparency)

**For Project**:
- ✅ Professional documentation
- ✅ Easier onboarding for new contributors
- ✅ Demo can become part of marketing
- ✅ Creates portfolio of work accomplished

---

### 📚 Examples from Other Projects

**Good Demo Examples to Learn From**:
- [Rich library demos](https://github.com/Textualize/rich/tree/master/examples) - Interactive Python scripts
- [Textual demos](https://github.com/Textualize/textual/tree/main/examples) - TUI demonstrations
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) - Progressive examples
- [Streamlit gallery](https://streamlit.io/gallery) - Visual demonstrations

**This is non-negotiable for professional autonomous development.** 🎬

---

## 📋 Project Status

### ✅ Completed Projects

#### 1. **Core Architecture Refactoring**
**Status**: ✅ **COMPLETED** (Sprint 1 & 2)
**Completion Date**: 2025-10-08
**Results**:
- Simplified AutoPickerLLM (780 → 350 lines, -55%)
- Extracted ContextStrategy
- FallbackStrategy with 3 implementations (Sequential, Smart, Cost-optimized)
- Builder Pattern (LLMBuilder + SmartLLM)
- 72 tests, 100% passing
- 100% backward compatible
- Complete codebase migration

**Documentation**:
- `docs/refactoring_complete_summary.md`
- `docs/sprint1_refactoring_summary.md`
- `docs/sprint2_refactoring_summary.md`
- `docs/migration_to_refactored_autopicker.md`

---

### 🔄 In Progress

#### 2. **Code Improvements Sprints 1-5** ⚡
**Status**: ✅ **ALL SPRINTS COMPLETED** (7 sprints: 1, 2, 3, 4, 4.5, 4.6, 5)
**Started**: 2025-01-09
**Completed**: 2025-10-09
**Branch**: `feature/rateLimits-fallbacksModels-specializedModels`
**Lead**: Parallel Claude Instance
**Sprint 1 Commit**: `e79a90f` (2025-01-09)
**Sprint 2 Commit**: `88b6d9e` (2025-01-09)
**Sprint 3 Commit**: `8431b96` (2025-10-09)
**Sprint 4 Commit**: `026807d` (2025-10-09)
**Sprint 4.5 Commit**: `8827dac` (2025-10-09)
**Sprint 4.6 Commit**: `e5c6bc7` (2025-10-09)
**Sprint 5 Commits**: `2e27b24` (Part 1), `12020f5` (Part 2, 2025-10-09) - ✅ COMPLETED
**Documentation Commits**: `6eb5b3c`, `e64387c`, `cda502b`, `45bf34e`, `601d631`, `3d9e858`

**Sprint 1 Results** ✅ **COMPLETED**:
- ✅ **800+ lines removed** (deprecated code + duplication)
- ✅ **27 lines of duplication eliminated** (time threshold calculations)
- ✅ **11 critical methods** now observable in Langfuse
- ✅ **10+ flaky operations** now have retry protection
- ✅ **112 tests passing** (retry + time + analytics)
- ✅ **Type safety improved** with 15+ new type annotations

**Changes Completed**:
1. ✅ OpenAI Provider: Replaced manual retry with `@with_retry` decorator
2. ✅ Time Utils: Added `get_timestamp_threshold()` function (eliminated 27 lines duplication)
3. ✅ Cost Calculator: Added `@observe` to 4 methods, eliminated duplication
4. ✅ Analytics Analyzer: Added `@with_retry` + `@observe` to 7 database methods
5. ✅ Deprecated Code: Deleted 800 lines from `_deprecated/` directory

**Sprint 2 Results** ✅ **COMPLETED**:
- ✅ **Created centralized exceptions module** (4 exception classes)
- ✅ **Extracted 3 hard-coded constants** (self-documenting code)
- ✅ **Fixed duplicate provider definition** (environment-configurable)
- ✅ **Added type hints to 5 key functions** (better IDE support)
- ✅ **All 112 tests passing** (no regressions)

**Sprint 2 Changes**:
1. ✅ Exceptions Module: Created `exceptions.py` with ContextLengthError, BudgetExceededError, ModelNotAvailableError, RateLimitExceededError
2. ✅ Timing Constants: Extracted PORT_RELEASE_WAIT_SECONDS, SERVER_POLL_INTERVAL_SECONDS, DEFAULT_SERVER_TIMEOUT_SECONDS
3. ✅ LLM Configuration: Fixed duplicate __DEFAULT_PROVIDER, now uses os.getenv("DEFAULT_LLM_PROVIDER", "openai")
4. ✅ Type Hints: Added to make_func_a_tool(), get_llm(), enable_sqlite_wal()
5. ✅ Code Organization: Consolidated ContextLengthError from 2 locations to single module

**Sprint 3 Results** ✅ **COMPLETED**:
- ✅ **72 lines removed** from AutoPickerLLM (545 → 478 lines, 13% reduction)
- ✅ **ContextStrategy pattern integrated** (strategy-based context management)
- ✅ **4 methods removed** (_check_context_length, _get_large_context_models, _initialize_large_context_models, _estimate_tokens)
- ✅ **Removed lazy-initialization logic** and private state (_large_context_models field)
- ✅ **Removed enable_context_fallback flag** (always enabled via strategy)
- ✅ **18/18 analytics tests passing** (smoke test successful)

**Sprint 3 Changes**:
1. ✅ Context Strategy Integration: Added context_strategy parameter to AutoPickerLLM.__init__
2. ✅ Refactored Context Checking: Replaced _check_context_length() with context_strategy.check_fits()
3. ✅ Refactored Model Selection: Replaced _get_large_context_models() with context_strategy.get_larger_context_models()
4. ✅ Simplified Architecture: Removed 4 methods and 1 private field
5. ✅ Better Separation of Concerns: Context management now fully delegated to ContextStrategy

**Sprint 3 Commit**: `8431b96`
**Date**: 2025-10-09

**Sprint 4 Results** ✅ **COMPLETED**:
- ✅ **Quota/ResourceExhausted error handling** implemented
- ✅ **QuotaExceededError exception** added with structured metadata
- ✅ **Automatic fallback** to alternative models when quota hit
- ✅ **Quota vs Rate Limit distinction** - separate detection and handling
- ✅ **Langfuse observability** for quota errors with ERROR level
- ✅ **Retry time extraction** from error messages (e.g., "retry in 31.94s")
- ✅ **18/18 analytics tests passing** (no regressions)

**Sprint 4 Changes**:
1. ✅ New Exception: `QuotaExceededError` with provider, model, quota_type, message_detail, retry_after
2. ✅ Error Detection: `is_quota_exceeded_error()` - extracts quota metadata from exceptions
3. ✅ Rate Limit Refinement: `is_rate_limit_error()` - now excludes quota keywords
4. ✅ AutoPickerLLM: Added `quota_fallbacks` stat and intelligent fallback logic
5. ✅ Langfuse Logging: `log_quota_error()` - tracks quota errors with full context

**Sprint 4 Commit**: `026807d`
**Date**: 2025-10-09
**Addresses**: TODO in coffee_maker/langchain_observe/llm.py:3

**Sprint 4.5 Results** ✅ **COMPLETED**:
- ✅ **Removed completed TODO** in llm.py (quota handling now implemented)
- ✅ **Migrated to Pydantic V2 ConfigDict** (4 model classes updated)
- ✅ **Eliminated 3 deprecation warnings** (Pydantic V2 compliance)
- ✅ **18/18 analytics tests passing** (no regressions)

**Sprint 4.5 Changes**:
1. ✅ TODO Removal: Removed llm.py:3 TODO, added reference to Sprint 4 implementation
2. ✅ Pydantic V2: Migrated `AutoPickerLLMRefactored` from Config to ConfigDict
3. ✅ Pydantic V2: Migrated `ScheduledLLM` and `ScheduledChatModel` to ConfigDict
4. ✅ Pydantic V2: Migrated `_StubChatModel` in agents.py to ConfigDict

**Sprint 4.5 Commit**: `8827dac`
**Date**: 2025-10-09

**Sprint 4.6 Results** ✅ **COMPLETED**:
- ✅ **SQLAlchemy 2.0 migration** (declarative_base import updated)
- ✅ **Zero deprecation warnings** (full library compliance)
- ✅ **18/18 analytics tests passing** (clean test output)

**Sprint 4.6 Changes**:
1. ✅ SQLAlchemy 2.0: Updated import from `sqlalchemy.ext.declarative` to `sqlalchemy.orm`

**Sprint 4.6 Commit**: `e5c6bc7`
**Date**: 2025-10-09

**Sprint 5 Results** ✅ **COMPLETED**:
- ✅ **Created models_sqlite.py** (dataclass + sqlite3, 430 lines)
- ✅ **Created exporter_sqlite.py** (Langfuse export, 340 lines)
- ✅ **Created analyzer_sqlite.py** (Performance analysis, 235 lines)
- ✅ **Zero external dependencies** (stdlib only)
- ✅ **5 database tables** with indexes (traces, generations, spans, metrics, rate_limits)
- ✅ **Updated scripts** (export_langfuse_data.py, analyze_performance.py)
- ✅ **Manual testing passed** (CRUD operations verified)
- 🔄 **Remove SQLAlchemy dependency** (pending - next step)

**Sprint 5 Changes** (Part 1 - Models):
1. ✅ Models: Dataclass-based Trace, Generation, Span (vs SQLAlchemy ORM)
2. ✅ SQL Schema: Native CREATE TABLE statements with indexes
3. ✅ Serialization: to_db_row() / from_db_row() methods
4. ✅ JSON Support: json.dumps/loads for metadata fields
5. ✅ WAL Mode: Enabled for better concurrency

**Sprint 5 Changes** (Part 2 - Exporter & Analyzer):
1. ✅ Exporter: LangfuseExporter using native sqlite3 queries
2. ✅ Analyzer: PerformanceAnalyzer using native sqlite3 queries
3. ✅ Context Managers: __enter__/__exit__ for resource cleanup
4. ✅ Retry Decorators: @with_retry for resilience
5. ✅ Scripts: Updated imports to use new sqlite3 modules

**Sprint 5 Commits**:
- Part 1: `2e27b24` (models_sqlite.py)
- Part 2: `12020f5` (exporter_sqlite.py, analyzer_sqlite.py, scripts)

**Date**: 2025-10-09
**Decision**: Option 2 - Replace SQLAlchemy with sqlite3 (user approved)
**Rationale**: Analytics module is isolated, sqlite3 sufficient, removes ~2MB dependency

**Sprint 5 Cleanup** (Completed):
- ✅ Updated __init__.py to export sqlite3 modules (exporter_sqlite, analyzer_sqlite)
- ✅ Added deprecation warnings to all SQLAlchemy modules
- ✅ Updated module docstrings to reference sqlite3 implementation
- ✅ Backward compatibility maintained (old modules still work)

**Sprint 5 Complete**: All modules migrated to native sqlite3, zero external dependencies

**Commits**:
- Part 1: `2e27b24` (models_sqlite.py)
- Part 2: `12020f5` (exporter_sqlite.py, analyzer_sqlite.py, scripts)
- Cleanup: `7d3492e` (deprecation warnings, __init__.py update)

**Combined Impact (Sprint 1 + 2 + 3 + 4 + 4.5 + 4.6 + 5 + PRIORITY 2 & 3)**:
- **Code Quality**: Net -354 lines from refactoring + ~3,200 new lines for PRIORITY 2 & 3
- **AutoPickerLLM**: Simplified from 545 → 478 lines (13% reduction)
- **Dependencies**: Removed SQLAlchemy (~2MB + sub-dependencies) → stdlib only (Sprint 5)
- **Duplication**: 28 instances eliminated
- **Type Safety**: 20+ type hints added
- **Reliability**: Database queries resilient, 10+ ops with retry + WAL mode for concurrent access
- **Observability**: 11 methods tracked in Langfuse + quota error tracking
- **Organization**: 8 refactored modules + 7 new modules (cli/, autonomous/ directories)
  - **PRIORITY 2**: notifications.py, roadmap_cli.py (801 lines + 236 test lines)
  - **PRIORITY 3**: daemon.py, roadmap_parser.py, claude_cli_interface.py, git_manager.py (1,148 lines + 375 test lines)
- **Architecture**: Strategy pattern applied + new autonomous daemon architecture
- **Error Handling**: Quota vs rate limit distinction, automatic fallback, retry logic for all DB ops
- **Deprecations**: Pydantic V2 + SQLAlchemy 2.0 complete, zero warnings
- **Maintainability**: Cleaner, more consistent, better separated concerns, lighter dependencies
- **Foundation**: ✅ **Autonomous daemon operational** (90% complete with critical fixes)
- **Tests**: 112/112 passing + 18/18 analytics + 27/27 PRIORITY 2&3 (159 tests total, 0 regressions)

**Documentation**:
- ✅ `docs/code_improvements_2025_01.md` - Complete analysis (40+ opportunities, 923 lines)
- ✅ `docs/retry_patterns.md` - Retry utilities guide (508 lines)
- ✅ `docs/sprint1_improvements_summary.md` - Sprint 1 report (380 lines)
- ✅ `docs/sprint2_improvements_summary.md` - Sprint 2 report (400 lines)
- ✅ `docs/SPRINT_SUMMARY_2025_10_09.md` - Sprint 5 + PRIORITY 2 & 3 (350 lines)
- ✅ `docs/DAEMON_USAGE.md` - Complete daemon usage guide (540 lines)
- ✅ `coffee_maker/autonomous/README.md` - Daemon architecture docs (220 lines)
- ✅ Total new documentation: 3,321 lines

**Coordination**:
- ✅ Sprint 1 & 2 completed before PRIORITY 1 begins
- ✅ Clean, reliable codebase foundation established
- ✅ Sprint 5 completed (SQLAlchemy removal, native sqlite3)
- ✅ PRIORITY 2 MVP Phase 1 implemented (80% complete - notifications, basic CLI)
- ✅ PRIORITY 3 MVP implemented (90% complete - autonomous daemon core)
- ✅ Critical daemon fixes applied (session detection, CLI non-interactive mode, branch handling)

---

## 🚀 Prioritized Roadmap

### 🔴 **PRIORITY 1: Analytics & Observability** ⚡ FOUNDATION FOR AUTONOMOUS DAEMON

**Estimated Duration**: 2-3 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 🔄 **MOSTLY COMPLETE** (Core analytics done via Sprint 5, advanced features remaining)
**Why First**: Required for autonomous daemon to track its own work and errors

#### Project: Langfuse → SQLite Export & Analysis

**Core Features** ✅ **COMPLETED via Sprint 5**:
- ✅ Langfuse trace export to SQLite (exporter_sqlite.py)
- ✅ Performance analytics (analyzer_sqlite.py)
- ✅ Native sqlite3 implementation (zero dependencies)
- ✅ 5 database tables (traces, generations, spans, metrics, rate_limits)
- ✅ WAL mode enabled (multi-process safe)
- ✅ Export scripts (export_langfuse_data.py, analyze_performance.py)
- ✅ Configuration module (config.py)

**Remaining Features** 📝 **Planned**:
- [ ] Advanced metrics module (llm_metrics.py, prompt_metrics.py, agent_metrics.py)
- [ ] A/B testing for prompts (benchmark_prompts.py)
- [ ] Additional analytics queries (percentiles, trends, optimization insights)
- [ ] Dashboard integration (when PRIORITY 3+ implemented)

**Current Implementation**:
```
coffee_maker/langchain_observe/analytics/
├── exporter_sqlite.py         # ✅ Export Langfuse → SQLite
├── analyzer_sqlite.py         # ✅ Performance analysis
├── models_sqlite.py           # ✅ Dataclass models
├── config.py                  # ✅ Configuration
├── exporter.py                # ⚠️ DEPRECATED (SQLAlchemy)
├── analyzer.py                # ⚠️ DEPRECATED (SQLAlchemy)
├── models.py                  # ⚠️ DEPRECATED (SQLAlchemy)
└── db_schema.py               # ⚠️ DEPRECATED (SQLAlchemy)

scripts/
├── export_langfuse_data.py    # ✅ Manual export CLI
└── analyze_performance.py     # ✅ LLM performance analysis
```

**Benefits** ✅ **ACHIEVED**:
- ✅ Measure LLM ROI (cost vs quality)
- ✅ Optimize prompts with quantitative data
- ✅ Monitor agent performance
- ✅ Reliable multi-process rate limiting (WAL mode)
- ✅ Local archiving without cloud dependency
- ✅ **Foundation for daemon to track its own work** ⚡
- ✅ Zero external dependencies (stdlib only)

**Sprint 5 Commits**:
- Part 1: `2e27b24` (models_sqlite.py)
- Part 2: `12020f5` (exporter_sqlite.py, analyzer_sqlite.py)
- Cleanup: `7d3492e` (deprecation warnings)

**Remaining Work**:
- Advanced metrics modules (if needed)
- Integration with Streamlit dashboards (PRIORITY 3+)
- A/B testing framework (if needed)

---

### 🔴 **PRIORITY 1.5: Database Synchronization Architecture** ✅ **COMPLETE**

**Estimated Duration**: 2-3 days (design phase only)
**Impact**: ⭐⭐⭐⭐⭐ (Critical infrastructure)
**Status**: ✅ **COMPLETE** - Implemented in PRIORITY 2 & 3
**Completed**: 2025-10-09
**Type**: Design-only priority (no implementation, integrated into other priorities)
**Decision**: Hybrid Shared SQLite (Option D) - See ADR_001

**Summary of Completion**:
- ✅ Analyzed database synchronization problem for daemon ↔ user communication
- ✅ Evaluated 4 architecture options (Shared SQLite, Sync, PostgreSQL, Hybrid)
- ✅ **Decision**: Hybrid Shared SQLite with WAL mode for concurrent access
- ✅ Documented in ADR_001_DATABASE_SYNC_STRATEGY.md (431 lines)
- ✅ Implemented in PRIORITY 2 (NotificationDB with WAL, @with_retry)
- ✅ Validated with 27 tests (11 unit + 16 integration)
- ✅ Migration path defined for future PostgreSQL scaling

**Key Implementation Details**:
- Shared SQLite databases in `data/` directory
- WAL (Write-Ahead Logging) mode enabled for multi-process safety
- 30-second busy_timeout for lock handling
- @with_retry decorator for transient failure recovery
- Data ownership matrix defined for all tables
- Concurrency strategy with lock scenario analysis

**Documentation**:
- `docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md` - Problem analysis (450+ lines)
- `docs/ADR_001_DATABASE_SYNC_STRATEGY.md` - Architecture Decision Record (431 lines)

#### The Problem 🚨

We will have **two separate database instances**:

```
User's Project Environment          Daemon's Isolated Docker Environment
─────────────────────────           ─────────────────────────────────────
/project/data/                      /daemon-env/data/
  ├── langfuse_traces.db     ≠≠≠      ├── langfuse_traces.db
  ├── notifications.db       ≠≠≠      ├── notifications.db
  └── analytics.db           ≠≠≠      └── analytics.db

CONFLICT: Two separate databases with potentially overlapping/conflicting data!
```

**Specific Issues**:
1. **Notifications**: Daemon writes → Slack bot reads from user's DB (doesn't see it!)
2. **Analytics**: Daemon generates traces → User dashboard reads from user's DB (doesn't see them!)
3. **Roadmap State**: User updates roadmap → Daemon reads from daemon's DB (stale data!)

#### Architecture Options (4 Strategies)

**Option A: Shared SQLite via Docker Volume** ✅ **Recommended for MVP**
- Docker volume mounts user's data directory
- Single source of truth, real-time updates
- ⚠️ SQLite locking issues with concurrent writes
- Simple, good enough for single-developer local use

**Option B: Separate DBs + Unidirectional Sync**
- Daemon writes to isolated DB, periodically syncs to user DB
- Clean isolation, easy cleanup
- ❌ Sync complexity, data lag, storage duplication

**Option C: Network-Accessible PostgreSQL**
- Both connect to shared PostgreSQL instance
- True concurrent access, scales to teams
- ❌ Complex setup, heavier, overkill for local dev

**Option D: Hybrid (Split by Data Type)**
- Shared: analytics, notifications (Docker volume)
- Isolated: daemon internal state (isolated SQLite)
- Best of both worlds but more complex

#### Recommended Phased Approach

**Phase 1: MVP - Shared SQLite** (PRIORITY 1-3)
```yaml
# docker-compose.yml
services:
  daemon:
    volumes:
      - ./data:/project/data:rw  # Share data directory
    environment:
      - ANALYTICS_DB=/project/data/analytics.db
      - NOTIFICATIONS_DB=/project/data/notifications.db
```

**Database Guardrails for MVP**:
1. **WAL Mode**: Enable Write-Ahead Logging for SQLite (`PRAGMA journal_mode=WAL`)
2. **Timeout**: Set busy timeout to 5000ms (`PRAGMA busy_timeout=5000`)
3. **Retry Logic**: Wrap all writes with `@with_retry` decorator
4. **Connection Pooling**: Use SQLAlchemy connection pool (max 5 connections)
5. **Read-Heavy Pattern**: Daemon mostly reads, user mostly writes

**Phase 2: PostgreSQL Migration** (PRIORITY 4+ or later)
- Migrate when scaling to team collaboration or production
- Proper concurrent access with row-level security
- Migration script: SQLite → PostgreSQL

#### Deliverables (Design Phase) ✅ **ALL COMPLETE**

- [x] **Problem Analysis Document** ✅ (`docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`)
- [x] **Architecture Decision Record (ADR)** ✅ (`docs/ADR_001_DATABASE_SYNC_STRATEGY.md`)
- [x] **Data Ownership Matrix** ✅ (in ADR_001 - section "Data Ownership Matrix")
- [x] **Concurrency Strategy** ✅ (in ADR_001 - section "Concurrency Strategy")
- [x] **Implementation Guidelines** ✅ (implemented in PRIORITY 2 & 3: NotificationDB, WAL mode, @with_retry)
- [x] **Testing Strategy** ✅ (in ADR_001 + 27 tests: 11 unit + 16 integration)
- [x] **Migration Plan** ✅ (in ADR_001 - section "Migration Path (Phase 2)")

#### Timeline

**Day 1: Problem Analysis + Requirements** (4-6h)
- Document all use cases (local dev, team, production)
- List all database tables and sync requirements
- Create data ownership matrix (draft)

**Day 2: Architecture Evaluation** (6-8h)
- Prototype architectural options with code
- Test concurrent access scenarios
- Benchmark SQLite vs PostgreSQL performance
- Make recommendation

**Day 3: Decision + Documentation** (4-6h)
- Finalize architecture decision (with approval)
- Write ADR and implementation guidelines
- Document migration path (if phased)
- Review and sign-off

**Total**: 14-20h (2-3 days) - **Design only, implementation in other priorities**

#### Integration with Other Priorities

This is a **design-only priority**. Implementation happens in:
- **PRIORITY 1** (Analytics): Define DB schema with sync strategy
- **PRIORITY 2** (Roadmap CLI): Follow decided database access pattern
- **PRIORITY 3** (Daemon): Follow decided database access pattern
- **All notification priorities**: Use decided sync mechanism

**Reference**: `docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md` (comprehensive 450+ line design document)

---

### 🔴 **PRIORITY 2: Roadmap Management CLI** ⚡ NEW 🎯 **FOUNDATION**

**Estimated Duration**: 2-3 days
**Impact**: ⭐⭐⭐⭐⭐ (Critical foundation)
**Status**: 🔄 **MVP PHASE 1 IN PROGRESS** (Basic CLI + Notification DB implemented)
**Started**: 2025-10-09
**Current Phase**: MVP Phase 1 (Database guardrails + basic commands)
**Dependency**: None (must be built BEFORE autonomous daemon)
**Why First**: Single source of truth for ROADMAP.md - simplifies daemon implementation

**MVP Phase 1 Progress** ✅ **80% COMPLETE**:
- ✅ Created `coffee_maker/cli/` directory structure
- ✅ Implemented `notifications.py` (NotificationDB with WAL mode, retry logic, 435 lines)
- ✅ Implemented `roadmap_cli.py` (project-manager CLI, 366 lines)
- ✅ Added CLI entry point to pyproject.toml (`project-manager` command)
- ✅ Implemented basic commands:
  * `view` - View roadmap (full or specific priority)
  * `notifications` - List pending notifications
  * `respond` - Respond to daemon questions
  * `status` - Daemon status (placeholder for MVP)
  * `sync` - Sync with daemon environment (placeholder for MVP)
- ✅ Database guardrails: WAL mode, 30s timeout, @with_retry decorator
- ✅ Unit tests: 11/11 passing (test_notifications.py, 236 lines)
- ⏳ Documentation (final step for MVP Phase 1)

**Commits**:
- Phase 1 Implementation: `18699eb`
- Phase 1 Tests: (next commit)

#### Project: AI-Powered Project Manager CLI (coffee-roadmap)

**Vision**: Create a dedicated **`coffee-roadmap` CLI tool** - an AI-powered project manager that provides an interactive chat interface for managing ROADMAP.md. This is the **ONLY way** to update the roadmap - both user and daemon use it.

---

#### 🎯 MVP Approach: Start Simple, Scale Smart

**Implementation Strategy**: Build in **two phases** to establish database guardrails first:

**Phase 1: MVP - Basic CLI with Database Guardrails** (2-3 days) ⚡ **START HERE**
- ✅ Shared SQLite via Docker volume (Option A from PRIORITY 1.5)
- ✅ Basic CLI commands (`view`, `status`, `notify`, `sync`)
- ✅ Notification database with proper retry logic
- ✅ WAL mode + timeout configuration
- ✅ `@with_retry` decorator on all writes
- ❌ NO Claude AI yet (too complex for MVP)
- ❌ NO rich terminal UI (basic text is fine)
- ❌ NO roadmap editing (read-only for MVP)

**Phase 2: Full AI Integration** (2-3 days) - After MVP validated
- Add Claude AI for natural language understanding
- Add rich terminal UI with `rich` library
- Add roadmap editing capabilities
- Add Slack integration
- Add history/undo functionality

**Why This Approach?**
1. ✅ **Database guardrails** established early (prevents future sync issues)
2. ✅ **Quick validation** (can test database patterns in 2-3 days)
3. ✅ **Risk mitigation** (complex AI features don't block daemon work)
4. ✅ **Foundation first** (proper patterns before fancy features)

**Reference**: `docs/PROJECT_MANAGER_MVP_DESIGN.md` (comprehensive MVP design with database patterns)

---

**Full Vision**: **Claude AI as Project Manager** 🤖 (Phase 2)
- ✅ Natural language understanding of roadmap requests
- ✅ Intelligent roadmap editing and suggestions
- ✅ Context-aware priority recommendations
- ✅ Auto-generates well-structured priority sections
- ✅ Validates changes before applying

**Revolutionary Simplification**: Instead of complex file sync mechanisms, all roadmap updates go through ONE AI-powered interface:
- ✅ **User**: Chats with Claude AI to plan features, update requirements
- ✅ **Daemon**: Uses same tool programmatically to update status
- ✅ **Zero conflicts**: Single tool = single source of truth

**Key Features**:
- 🤖 **Claude AI-Powered**: All roadmap operations powered by Claude's intelligence
- 💬 **Interactive Chat**: Natural language conversations for roadmap management
- 🎯 **Internal Commands**: Rich command system (slash commands + natural language)
- 📝 **Smart Editor**: AI understands intent and suggests improvements
- 🔄 **Live Sync**: Changes propagate to daemon's isolated environment instantly
- 📊 **Intelligent Analysis**: Claude analyzes roadmap health and suggests optimizations
- 🎨 **Rich Terminal UI**: Beautiful formatting with colors and progress bars
- 🤖 **API Mode**: Daemon can call it programmatically for status updates

**Minimal Architecture**:
```
coffee_maker/cli/
├── __init__.py
├── roadmap_cli.py                # Main CLI entry point
├── chat_interface.py             # Interactive chat with Claude
├── roadmap_editor.py             # Roadmap manipulation logic
├── sync_manager.py               # Sync to daemon's environment
└── commands/
    ├── add_priority.py           # Add new priority
    ├── update_status.py          # Update task status
    ├── view_roadmap.py           # Display roadmap
    └── export_roadmap.py         # Export to different formats

# Binary entry point
pyproject.toml:
[project.scripts]
coffee-roadmap = "coffee_maker.cli.roadmap_cli:main"
```

**Internal Commands** (Slash Commands + Natural Language):

The CLI supports both **slash commands** and **natural language** - Claude AI interprets both:

```bash
# Slash Commands (explicit)
/add <priority_name>           # Add new priority
/update <priority> <status>    # Update status
/view [priority]               # View roadmap or specific priority
/analyze                       # AI analyzes roadmap health
/suggest                       # AI suggests improvements
/export <format>               # Export roadmap (md, json, html, pdf)
/search <query>                # Search roadmap
/metrics                       # Show roadmap metrics
/history                       # View change history
/undo                          # Undo last change
/help                          # Show all commands

# Natural Language (flexible)
"Add a priority for rate limiting"
"Mark priority 3 as in progress"
"Show me what's completed"
"How healthy is our roadmap?"
"What should we work on next?"
```

**User Experience** (AI-Powered Conversation):

```bash
$ coffee-roadmap

╔════════════════════════════════════════════════════════════╗
║       🤖 Coffee Maker - AI Project Manager CLI            ║
║                                                             ║
║  Powered by Claude AI - Your intelligent roadmap assistant ║
║  Type /help for commands or just chat naturally            ║
╚════════════════════════════════════════════════════════════╝

Claude: Hello! I'm your AI project manager. I've loaded your roadmap with 7
priorities. How can I help you today?

You: Add a new priority for implementing rate limiting

Claude: I'll add a new priority for rate limiting. Let me analyze the current
roadmap to determine the best priority number and placement.

📊 Analysis:
- Current priorities: 1-7
- Last priority: PRIORITY 7 (Innovative Projects)
- Suggested placement: PRIORITY 8
- Estimated impact: ⭐⭐⭐⭐ (High)

Here's my proposed priority:

╔════════════════════════════════════════════════════════════╗
║ 🔴 PRIORITY 8: Advanced Rate Limiting                      ║
╠════════════════════════════════════════════════════════════╣
║ Duration: 1-2 weeks                                        ║
║ Impact: ⭐⭐⭐⭐                                               ║
║ Status: 📝 Planned                                          ║
║                                                             ║
║ Objectives:                                                 ║
║ • Token-based rate limiting per model                      ║
║ • Sliding window rate limit enforcement                    ║
║ • Multi-process shared rate limit counters                 ║
║ • Graceful degradation when limits exceeded                ║
╚════════════════════════════════════════════════════════════╝

Would you like me to add this? [yes/no/edit]

You: yes

Claude: ✅ Added PRIORITY 8 to ROADMAP.md
✅ Synced to daemon's environment at /daemon-env/ROADMAP.md
✅ Daemon will see this new priority on next poll (5s)

💡 Tip: The autonomous daemon will pick up this priority after completing
PRIORITY 7. You can track progress with `/metrics` command.

You: /update PRIORITY 3 in-progress

Claude: ✅ Updated PRIORITY 3: Streamlit Analytics Dashboard
   Status: 📝 Planned → 🔄 In Progress
   Updated by: User (manual)
   Timestamp: 2025-10-09 14:23:45
✅ Synced to daemon's environment

You: /view

Claude: 📋 Current Roadmap Summary (8 priorities):

┌─────────────┬──────────────────────────────────────┬────────────┐
│ Priority    │ Name                                  │ Status     │
├─────────────┼──────────────────────────────────────┼────────────┤
│ PRIORITY 1  │ Analytics & Observability             │ ✅ DONE    │
│ PRIORITY 2  │ Roadmap Management CLI                │ 🔄 60%     │
│ PRIORITY 3  │ Autonomous Development Daemon         │ 🔄 NEW     │
│ PRIORITY 4  │ Streamlit Analytics Dashboard         │ 📝 PLANNED │
│ PRIORITY 5  │ Error Monitoring Dashboard            │ 📝 PLANNED │
│ PRIORITY 6  │ Agent Interaction UI                  │ 📝 PLANNED │
│ PRIORITY 7  │ Professional Documentation            │ 📝 PLANNED │
│ PRIORITY 8  │ Advanced Rate Limiting                │ 📝 PLANNED │
└─────────────┴──────────────────────────────────────┴────────────┘

Overall Progress: ██████░░░░░░░░░░░░░░ 25% (2/8 priorities completed)

You: analyze the roadmap health

Claude: 🔍 Roadmap Health Analysis:

📊 Overall Health: 85/100 (Very Good)

Strengths:
✅ Clear priority order with logical dependencies
✅ Realistic time estimates (2-3 weeks per priority)
✅ Good balance of infrastructure vs features (40/60)
✅ All priorities have clear objectives

Concerns:
⚠️  PRIORITY 3 (Autonomous Daemon) is critical path - 60% complete
⚠️  5 priorities waiting on PRIORITY 3 completion
💡 Consider parallelizing PRIORITY 4 & 5 (both Streamlit dashboards)

Recommendations:
1. Focus resources on completing PRIORITY 3 (unblocks 5 priorities)
2. Plan PRIORITY 4 & 5 implementation in parallel (no dependencies)
3. Add time buffers for PRIORITY 8 (new, estimation uncertain)

You: What should we work on next?

Claude: 🎯 Recommendation: **PRIORITY 3 - Autonomous Development Daemon**

Reasoning:
1. **Critical Path**: Blocks 5 downstream priorities
2. **High Impact**: Enables self-implementing system (game-changer)
3. **Already 60% Complete**: Momentum is there, finish it!
4. **Foundation**: Required before daemon can implement PRIORITY 4-8

Next Steps:
1. Complete remaining 40% of PRIORITY 3 (estimated 1-2 days)
2. Run full integration tests
3. Document daemon usage
4. Mark PRIORITY 3 as ✅ COMPLETED
5. Let daemon autonomously implement PRIORITY 4 & 5 in parallel

Estimated completion: 2025-10-11 (2 days from now)

You: /metrics

Claude: 📊 Roadmap Metrics:

Development Velocity:
• Avg time per priority: 2.5 weeks
• Priorities completed: 2/8 (25%)
• Current sprint: PRIORITY 3 (60% done)
• Projected completion: 2025-12-15 (10 weeks)

Workload Distribution:
Infrastructure: ████████░░░░ 40% (3 priorities)
Features:       ████████████ 60% (5 priorities)

Priority Impact Analysis:
⭐⭐⭐⭐⭐ (5-star): 6 priorities (75%)
⭐⭐⭐⭐   (4-star): 2 priorities (25%)

Dependencies:
• PRIORITY 1 → blocks 0 (completed)
• PRIORITY 2 → blocks 1 (PRIORITY 3)
• PRIORITY 3 → blocks 5 (critical path!)

You: /history

Claude: 📜 Recent Changes:

2025-10-09 14:23:45 | UPDATE    | PRIORITY 3 status → In Progress
2025-10-09 14:20:12 | ADD       | PRIORITY 8: Advanced Rate Limiting
2025-10-09 12:15:33 | COMPLETE  | PRIORITY 2: Roadmap CLI (60% → 100%)
2025-10-08 16:45:21 | UPDATE    | PRIORITY 2 status → In Progress
2025-10-08 09:30:55 | COMPLETE  | PRIORITY 1: Analytics (100%)

Type /undo to revert last change, or /undo <n> for nth change

You: exit

Claude: 👋 Goodbye! Your roadmap has been saved and synced.

Summary of this session:
• Added 1 new priority (PRIORITY 8)
• Updated 1 status (PRIORITY 3)
• Analyzed roadmap health (85/100)
• All changes synced to daemon environment

Next time: Run `/analyze` to see updated health metrics!
```

**Daemon Integration** (Programmatic API):

```python
from coffee_maker.cli.roadmap_editor import RoadmapEditor

# Daemon uses the same tool programmatically
editor = RoadmapEditor(roadmap_path="docs/ROADMAP.md")

# Update status when daemon completes a task
editor.update_status(
    priority="PRIORITY 3",
    status="🔄 In Progress",
    notes="Implemented overview page and cost charts"
)

# Daemon adds completion details
editor.mark_completed(
    priority="PRIORITY 3",
    completion_date="2025-10-15",
    deliverables=[
        "Multi-page Streamlit dashboard",
        "Interactive Plotly charts",
        "PDF/CSV export functionality"
    ],
    metrics={
        "lines_of_code": 847,
        "files_modified": 12,
        "tests_added": 23
    }
)
```

**Simplified Sync Mechanism** ⚡ **MUCH SIMPLER**:

Instead of complex file watchers and Git-based sync, we now have:

```python
class RoadmapSync:
    """Dead simple sync - just copy the file"""

    def __init__(self, roadmap_path: str, daemon_env_path: str):
        self.roadmap_path = roadmap_path
        self.daemon_env = daemon_env_path

    def sync_to_daemon(self):
        """Copy ROADMAP.md to daemon's isolated environment"""
        shutil.copy(self.roadmap_path, f"{self.daemon_env}/ROADMAP.md")
        logger.info("Synced roadmap to daemon environment")

    def sync_from_daemon(self):
        """Copy daemon's updates back to user roadmap"""
        shutil.copy(f"{self.daemon_env}/ROADMAP.md", self.roadmap_path)
        logger.info("Synced daemon updates to user roadmap")
```

**Benefits of This Approach**:
- ✅ **Single source of truth**: One tool controls all roadmap updates
- ✅ **Zero conflicts**: No concurrent writes (CLI serializes all updates)
- ✅ **Natural language editing**: Use Claude to modify complex roadmap
- ✅ **Daemon simplification**: No need for file watchers or Git sync
- ✅ **User-friendly**: Chat interface instead of manual YAML/Markdown editing
- ✅ **Validation**: CLI validates all changes before applying
- ✅ **Rollback**: CLI maintains history, easy undo
- ✅ **API for daemon**: Daemon uses same logic programmatically

**Deliverables**:

**Core Components**:
- [ ] `coffee-roadmap` CLI binary (installable via pip)
- [ ] Claude AI integration (via Anthropic API)
- [ ] Interactive chat interface with streaming responses
- [ ] Roadmap parser and AST-based editor
- [ ] Sync manager for daemon environment
- [ ] Programmatic API for daemon use
- [ ] Rich terminal UI (using `rich` library)
- [ ] Input validation and error handling
- [ ] Change history and rollback/undo functionality

**Internal Commands** (11 slash commands):
- [ ] `/add` - Add new priority (AI-assisted)
- [ ] `/update` - Update priority status/fields
- [ ] `/view` - Display roadmap (summary or detail)
- [ ] `/analyze` - AI roadmap health analysis
- [ ] `/suggest` - AI improvement suggestions
- [ ] `/export` - Export to multiple formats (md, json, html, pdf)
- [ ] `/search` - Search across roadmap
- [ ] `/metrics` - Development velocity and progress metrics
- [ ] `/history` - View change history with timestamps
- [ ] `/undo` - Revert changes
- [ ] `/help` - Interactive help system

**AI Intelligence Features**:
- [ ] Natural language understanding (parse user intent)
- [ ] Context-aware suggestions (analyze dependencies, timeline)
- [ ] Auto-generation of priority sections (objectives, architecture, timeline)
- [ ] Roadmap health scoring (dependencies, estimates, balance)
- [ ] Smart recommendations (what to work on next)
- [ ] Validation and consistency checks (status transitions, dependencies)
- [ ] Session summaries and insights

**Terminal UI Components**:
- [ ] Formatted tables (priority lists)
- [ ] Progress bars (roadmap completion)
- [ ] Syntax highlighting (code blocks, markdown)
- [ ] Rich formatting (colors, borders, boxes)
- [ ] Interactive prompts (yes/no/edit)
- [ ] Status indicators (✅ ✓ ⚠️  📝 🔄)

**Data Management**:
- [ ] Change tracking (all edits logged with timestamps)
- [ ] History storage (SQLite or JSON log)
- [ ] Rollback system (undo last N changes)
- [ ] Sync mechanism (copy to daemon environment)
- [ ] Conflict detection (warn if daemon modified roadmap)

**Documentation**:
- [ ] CLI usage guide
- [ ] Command reference
- [ ] Natural language examples
- [ ] API documentation for daemon integration
- [ ] Configuration guide

**Timeline** (Updated for expanded scope):
- **Day 1**: CLI framework + Claude AI integration + Chat interface (8-10h)
  - Setup `rich` for terminal UI
  - Anthropic API integration
  - Basic chat loop with streaming responses
  - Session management

- **Day 2**: Roadmap parser + Editor + Core commands (8-10h)
  - Markdown/YAML parser for ROADMAP.md
  - AST-based editor (add, update, delete sections)
  - Commands: `/add`, `/update`, `/view`
  - Input validation

- **Day 3**: AI Intelligence + Analytics commands (8-10h)
  - Natural language understanding
  - Commands: `/analyze`, `/suggest`, `/metrics`
  - Roadmap health scoring
  - Dependency analysis

- **Day 4**: History + Export + Sync (6-8h)
  - Change history tracking (SQLite)
  - Commands: `/history`, `/undo`, `/export`
  - Sync manager (daemon environment)
  - Conflict detection

- **Day 5**: Programmatic API + Tests + Documentation (6-8h)
  - Python API for daemon integration
  - Unit tests (pytest)
  - Integration tests
  - CLI documentation and examples

- **Total**: 36-46h (4-5 days) ⚡ UPDATED for AI-powered features

---

### 🔴 **PRIORITY 3: Basic Autonomous Development Daemon** ⚡ NEW 🤖 **TOP PRIORITY**

**Estimated Duration**: 3-5 days
**Impact**: ⭐⭐⭐⭐⭐ (Game-changing)
**Status**: 🔄 **MVP NEARLY COMPLETE** (Implementation and docs done, E2E testing remaining - 90% complete)
**Started**: 2025-10-09
**Dependency**: PRIORITY 2 (Roadmap Management CLI) - uses notification system
**Note**: Previously PRIORITY 2, renumbered after adding Roadmap CLI

**MVP Progress** ✅ **90% COMPLETE**:
- ✅ Created `coffee_maker/autonomous/` directory structure
- ✅ Implemented `roadmap_parser.py` (281 lines) - Parse ROADMAP.md for priorities
- ✅ Implemented `claude_cli_interface.py` (189 lines) - Subprocess wrapper for Claude CLI
- ✅ Implemented `git_manager.py` (271 lines) - Git operations (branch, commit, push, PR)
- ✅ Implemented `daemon.py` (407 lines) - Core autonomous daemon loop
- ✅ Created `run_dev_daemon.py` (146 lines) - Daemon launcher script with CLI args
- ✅ Integration tests: 16/16 passing (test_daemon_integration.py, 229 lines)
- ✅ Usage documentation: DAEMON_USAGE.md (340 lines) - Complete guide
- ✅ Component README: coffee_maker/autonomous/README.md (220 lines) - Architecture docs
- ⏳ End-to-end testing with real Claude CLI (final step)

**Key Features Implemented**:
- 🤖 Autonomous loop: Continuously reads ROADMAP.md for planned priorities
- 📋 Parser: Extracts priorities, status, deliverables from markdown
- 🔧 CLI wrapper: Executes Claude CLI programmatically with prompts
- 🌳 Git automation: Creates branches, commits, pushes, creates PRs via gh CLI
- 💬 Notifications: Requests user approval, sends completion notices
- 🔄 Continuous operation: Runs until all priorities complete or user stops

**Commits**:
- MVP Implementation: `6bdf475` - Core daemon modules (roadmap_parser, claude_cli_interface, git_manager, daemon)
- Launcher & Tests: `5282042` - run_dev_daemon.py + 16 integration tests (all passing)
- Documentation: `4b5265e` - DAEMON_USAGE.md (340 lines) + README.md (220 lines)
- Status Update: `ab12131` - Updated PRIORITY 3 to 90% complete
- Critical Fixes: `ef45ed6`, `e50b1e6`, `26ad812` - Daemon CLI execution and session warnings

**Recent Improvements** (2025-10-09):
- ✅ **Critical session conflict fix**: Added runtime detection to prevent daemon from running inside Claude Code sessions
  - Problem: Running daemon from within Claude Code caused hangs due to nested CLI calls
  - Solution: Daemon now detects `CLAUDE_CODE_SESSION` env var and warns user with instructions
  - Impact: Prevents common user error that caused daemon to become unresponsive
- ✅ **Claude CLI non-interactive execution**: Fixed daemon to use `claude -p` flag for non-interactive prompts
  - Problem: Daemon was calling Claude CLI without proper non-interactive flags
  - Solution: Updated to use `claude code -p "prompt"` for programmatic execution
  - Impact: Daemon can now execute Claude CLI reliably without manual intervention
- ✅ **Branch handling improvements**: Fixed Git branch creation and checkout logic
  - Problem: Branch switching sometimes failed in daemon context
  - Solution: Enhanced error handling and branch existence checks
  - Impact: More reliable Git operations during autonomous development

**Critical Usage Requirements** 🚨:
1. **MUST run from separate terminal**: Never run daemon from within Claude Code session
2. **Terminal detection**: Daemon will warn and exit if it detects Claude Code environment
3. **Recommended setup**: Open new terminal window/tab outside Claude Code to run daemon

#### Project: Minimal Self-Implementing AI System with Roadmap-Driven Development

**Vision**: Create a **simple, always-running** Python daemon that continuously reads ROADMAP.md and autonomously implements features via Claude CLI.

**Core Philosophy**: **Keep it minimal and focused** - just enough to autonomously implement features. Advanced features (monitoring, isolated environments) come later.

**Simplified Architecture** (thanks to PRIORITY 2):
- ✅ **No file watchers needed**: Daemon reads ROADMAP.md from its environment
- ✅ **No Git sync needed**: Uses `coffee-roadmap` API for status updates
- ✅ **No conflict resolution**: `coffee-roadmap` CLI handles all updates

**Two-Tier Architecture**:
1. **User → `coffee-roadmap` CLI**: User plans roadmap via interactive chat
2. **Daemon → `coffee-roadmap` API**: Daemon updates status programmatically

**Objectives**:
- Create a **minimal** Python daemon that supervises Claude Code CLI execution
- Enable Claude to read ROADMAP.md and autonomously implement features
- Automatic branch creation, implementation, PR creation, and progress tracking
- Simple Git-based safety with rollback capabilities
- **Daemon runs continuously** without stopping until all roadmap priorities are completed

**Key Features** (minimal set):
- 🤖 **Autonomous Implementation**: Claude reads roadmap and implements features
- 🔁 **Continuous Loop**: Daemon never stops, always looking for next task
- 🌳 **Basic Git Automation**: Auto-creates branches, commits, pushes, creates PRs
- 📊 **Simple Progress Tracking**: Updates ROADMAP.md with completion status
- 🔧 **CLI Integration**: Python subprocess wrapper for Claude CLI
- 🛡️ **Basic Safety**: Git-based versioning, all changes reversible
- 📝 **Self-Documentation**: Claude documents its own work in the roadmap

**Minimal Architecture** (keep it simple):
```
coffee_maker/autonomous/
├── __init__.py
├── daemon.py                      # Main daemon (single file, ~300-500 LOC)
├── roadmap_parser.py              # Parses ROADMAP.md for tasks
├── claude_cli_interface.py        # Subprocess wrapper for Claude CLI
├── git_manager.py                 # Basic Git operations (branch, commit, PR)
└── config.py                      # Simple configuration

scripts/
└── run_dev_daemon.py              # Daemon launcher (infinite loop)
```

**Deliverables** (minimal set):
- [ ] **RoadmapParser**: Extract tasks/priorities from ROADMAP.md (simple regex/markdown parsing)
- [ ] **ClaudeCLIInterface**: Basic subprocess wrapper for Claude CLI
- [ ] **GitManager**: Create branches, commit, push, create PRs via gh CLI
- [ ] **ProgressTracker**: Uses `coffee-roadmap` API to update status ⚡ SIMPLIFIED
- [ ] **DevDaemon**: Main loop that continuously reads roadmap and executes next task
- [ ] **Basic error handling**: Retry logic and simple logging
- [ ] **Setup documentation**: Quick start guide

**Example Workflow**:
```python
# User updates ROADMAP.md with new priority
# Then starts the daemon:

from coffee_maker.autonomous.daemon import DevDaemon

# Initialize autonomous development daemon
daemon = DevDaemon(
    roadmap_path="docs/ROADMAP.md",
    auto_approve=True,
    create_prs=True,
    model="claude-sonnet-4"
)

# Daemon reads ROADMAP.md and finds:
# "PRIORITY 2: Analytics & Observability - Status: 📝 Planned"

# Autonomous execution:
# 1. Creates branch: feature/analytics-export-langfuse
# 2. Prompts Claude: "Read docs/ROADMAP.md, implement PRIORITY 2"
# 3. Claude implements feature following roadmap guidelines
# 4. Claude commits with proper messages (following Git guidelines)
# 5. Runs tests automatically
# 6. Updates ROADMAP.md: Status: ✅ COMPLETED
# 7. Pushes branch and creates PR
# 8. Notifies user: "PRIORITY 2 completed, PR #123 ready for review"

# User reviews PR, merges if satisfied
# Daemon automatically moves to PRIORITY 3
```

**Interactive Messaging System** ⚡ NEW:

The daemon includes an intelligent message handler that intercepts Claude CLI's questions and can either:
1. **Auto-respond** based on predefined rules and roadmap context
2. **Notify user** for critical decisions requiring human judgment

```python
from coffee_maker.autonomous.claude_cli import MessageHandler

# Message handler configuration
handler = MessageHandler(
    auto_respond_rules={
        # Questions the daemon can answer automatically
        "continue?": lambda ctx: "yes" if ctx.tests_passed else "no",
        "commit now?": lambda ctx: "yes" if ctx.changes_valid else "no",
        "run tests?": lambda ctx: "yes",  # Always run tests
        "create PR?": lambda ctx: "yes" if ctx.branch_ready else "no",
    },
    notify_user_patterns=[
        # Questions that require user input
        r"API key",
        r"credentials",
        r"delete.*production",
        r"breaking change",
        r"merge to main",
    ],
    log_all_interactions=True,  # Log everything for traceability
    interaction_log_dir="coffee_maker/autonomous/interaction_logs/"
)

# Example interaction flow:
# 1. Claude asks: "Tests passed. Should I commit these changes?"
# 2. MessageHandler intercepts the question
# 3. Checks auto_respond_rules → matches "commit now?"
# 4. Evaluates lambda: ctx.changes_valid is True
# 5. Automatically responds: "yes"
# 6. Logs interaction to interaction_logs/2025-10-09_14-23-45.json

# For questions requiring user input:
# 1. Claude asks: "I found API key in .env. Should I commit it?"
# 2. MessageHandler detects pattern "API key" in notify_user_patterns
# 3. Logs the question
# 4. Pauses execution
# 5. Sends notification to user: "⚠️ Claude needs input: [question]"
# 6. Waits for user response
# 7. Forwards response to Claude
# 8. Logs the complete exchange
# 9. Resumes execution
```

**Interaction Logging**:

All Claude ↔ Python exchanges are logged with full context:

```json
{
  "timestamp": "2025-10-09T14:23:45Z",
  "priority": "PRIORITY 2: Analytics & Observability",
  "phase": "implementation",
  "interaction_type": "auto_response",
  "question_from_claude": "Tests passed. Should I commit these changes?",
  "context": {
    "tests_passed": true,
    "changes_valid": true,
    "files_modified": ["coffee_maker/analytics/exporter.py"],
    "branch": "feature/analytics-export-langfuse"
  },
  "response_from_python": "yes",
  "response_method": "auto_respond_rule: commit now?",
  "user_notified": false
}
```

**Benefits of Interactive Messaging**:
- ✅ **Full traceability**: Every interaction logged with context
- ✅ **Intelligent automation**: Python answers routine questions automatically
- ✅ **Human-in-the-loop**: Critical decisions escalated to user
- ✅ **Debugging**: Complete audit trail of all Claude ↔ Python exchanges
- ✅ **Safety**: Prevents dangerous actions without explicit approval
- ✅ **Transparency**: User can review all interactions post-execution

---

**User Notification & Input Handling System** ⚡ NEW:

The daemon includes a **two-way (bidirectional) messaging system** that both alerts users and collects their input when needed. The underlying notification object is capable of both sending messages to users and receiving responses back, enabling true interactive communication between the autonomous daemon and the user.

**Notification Channels**:

1. **Terminal/CLI** (default, always enabled):
   ```
   ╔════════════════════════════════════════════════════════════╗
   ║ 🤖 CLAUDE CLI - USER INPUT REQUIRED                       ║
   ╠════════════════════════════════════════════════════════════╣
   ║ Priority: PRIORITY 2 - Analytics & Observability           ║
   ║ Phase: Implementation                                      ║
   ║ Time: 2025-10-09 14:23:45                                 ║
   ╠════════════════════════════════════════════════════════════╣
   ║ Question from Claude:                                      ║
   ║ I found an API key in .env file. Should I commit it?      ║
   ║                                                            ║
   ║ Options: [yes/no/skip]                                    ║
   ║ Timeout: 5 minutes                                        ║
   ╚════════════════════════════════════════════════════════════╝
   Your answer: _
   ```

2. **Desktop Notifications** (macOS, Linux, Windows):
   - Uses native notification APIs
   - Click notification to open input prompt
   - Configurable sound/priority

3. **Webhooks** (Slack, Discord, Teams, etc.):
   - POST notification to configured webhook URL
   - Supports interactive buttons (Slack/Discord)
   - Reply via webhook or terminal

4. **Email** (optional, for long-running tasks):
   - Send email with question
   - Reply to email or via web link
   - Useful for overnight/weekend executions

**Configuration Example**:

```python
from coffee_maker.autonomous.notifications import Notifier, InputHandler

# Configure notification channels
notifier = Notifier(
    channels={
        "terminal": {"enabled": True, "priority": "high"},
        "desktop": {
            "enabled": True,
            "platforms": ["macos", "linux"],  # Auto-detect platform
            "sound": True,
            "urgency": "critical"
        },
        "webhook": {
            "enabled": True,
            "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "type": "slack",  # or "discord", "teams", "generic"
            "mention_user": "@developer"  # Slack/Discord mention
        },
        "email": {
            "enabled": False,  # Optional
            "smtp_server": "smtp.gmail.com",
            "to": "developer@example.com",
            "from": "claude-daemon@example.com"
        }
    },
    fallback_order=["terminal", "desktop", "webhook", "email"]
)

# Configure input handler
input_handler = InputHandler(
    timeout=300,  # 5 minutes default
    validation_rules={
        "yes/no": lambda x: x.lower() in ["yes", "no", "y", "n"],
        "continue": lambda x: x.lower() in ["continue", "stop", "skip"],
    },
    retry_on_invalid=True,
    max_retries=3
)
```

**End-to-End Flow with Notifications**:

```python
# 1. Claude encounters a question requiring user input
claude_question = "I found API key in .env. Should I commit it?"

# 2. MessageHandler detects it needs user input
if message_handler.requires_user_input(claude_question):

    # 3. Create notification
    notification = {
        "title": "🤖 Claude CLI - Input Required",
        "priority": "PRIORITY 2: Analytics & Observability",
        "phase": "implementation",
        "question": claude_question,
        "options": ["yes", "no", "skip"],
        "timeout": 300,  # 5 minutes
        "context": {
            "file": ".env",
            "branch": "feature/analytics-export-langfuse",
            "severity": "critical"
        }
    }

    # 4. Send notifications via all enabled channels
    notifier.send(notification)
    # → Terminal: Rich formatted prompt
    # → Desktop: Native notification
    # → Slack: Interactive message with buttons

    # 5. Wait for user input (blocking or async)
    user_response = input_handler.wait_for_input(
        notification_id=notification["id"],
        timeout=300,
        validation="yes/no"
    )

    # 6. Handle response
    if user_response.timed_out:
        # Use default safe action
        response = "no"  # Don't commit sensitive data by default
        notifier.send_timeout_alert(notification)
    elif user_response.valid:
        response = user_response.value
    else:
        response = "skip"  # Invalid input

    # 7. Log the interaction
    interaction_logger.log({
        "question": claude_question,
        "notification_sent_to": ["terminal", "desktop", "slack"],
        "user_response": response,
        "response_time_seconds": user_response.elapsed_time,
        "timed_out": user_response.timed_out
    })

    # 8. Forward response to Claude
    message_handler.respond_to_claude(response)
```

**Notification Queue Management**:

For multiple concurrent questions:

```python
# Queue manages multiple pending notifications
queue = NotificationQueue()

# Add notifications
queue.add(notification1, priority="high")
queue.add(notification2, priority="medium")
queue.add(notification3, priority="low")

# Process in priority order
while not queue.empty():
    notification = queue.get_next()
    user_response = input_handler.wait_for_input(notification)
    queue.mark_complete(notification.id, user_response)
```

**Unified Slack Integration** ⚡ NEW - Dual Interface:

Slack notifications can interact with **BOTH** the daemon and the project manager CLI:

```python
# Slack receives interactive message with dual routing:
{
  "text": "🤖 *Coffee Maker - Input Required*",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*From:* Autonomous Daemon\n*Priority:* PRIORITY 2 - Analytics & Observability\n*Phase:* Implementation"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Question from Claude:*\nI found an API key in .env file. Should I commit it?"
      }
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "✅ Yes"}, "value": "daemon:yes"},
        {"type": "button", "text": {"type": "plain_text", "text": "❌ No"}, "value": "daemon:no"},
        {"type": "button", "text": {"type": "plain_text", "text": "⏭️ Skip"}, "value": "daemon:skip"}
      ]
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "💬 *Or interact with Project Manager:*"
      }
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "📝 Update Roadmap"}, "value": "pm:/update"},
        {"type": "button", "text": {"type": "plain_text", "text": "📊 View Status"}, "value": "pm:/view"},
        {"type": "button", "text": {"type": "plain_text", "text": "📈 Show Metrics"}, "value": "pm:/metrics"}
      ]
    }
  ]
}

# User interaction routing:
# 1. Click "No" button → Routes to daemon: daemon.respond("no")
# 2. Click "Update Roadmap" → Routes to PM: coffee_roadmap.execute("/update PRIORITY 2 status in-progress")
# 3. Type message in thread → Routes to PM chat: coffee_roadmap.chat("Add priority for...")
```

**Dual-Routing Architecture**:

```python
from coffee_maker.notifications import UnifiedNotificationHub

# Unified notification hub routes messages to daemon OR project manager
hub = UnifiedNotificationHub(
    daemon=daemon,
    project_manager=coffee_roadmap_cli,
    notification_db="data/notifications.db"  # Store all notifications
)

# Slack webhook receives user action
@app.route("/slack/actions", methods=["POST"])
def slack_actions():
    payload = request.json
    action_value = payload["actions"][0]["value"]

    # Route based on prefix
    if action_value.startswith("daemon:"):
        # Route to daemon
        response = action_value.split(":", 1)[1]  # "yes", "no", "skip"
        hub.route_to_daemon(response)

    elif action_value.startswith("pm:"):
        # Route to project manager CLI
        command = action_value.split(":", 1)[1]  # "/update", "/view", etc.
        result = hub.route_to_project_manager(command)

        # Post result back to Slack
        return jsonify({
            "text": f"✅ Project Manager: {result}"
        })

# User can also chat directly in Slack thread
@app.route("/slack/events", methods=["POST"])
def slack_events():
    event = request.json["event"]

    if event["type"] == "message":
        user_message = event["text"]

        # Determine routing (daemon vs PM)
        if "roadmap" in user_message.lower() or any(cmd in user_message for cmd in ["/add", "/update", "/view"]):
            # Route to project manager
            response = hub.route_to_project_manager(user_message)
        else:
            # Route to daemon
            response = hub.route_to_daemon(user_message)

        # Post AI response to Slack
        post_to_slack(event["channel"], response)
```

**Notification Database Schema** ⚡ NEW:

```sql
-- Store all notifications for both daemon and PM
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,  -- 'daemon' or 'project_manager'
    type TEXT NOT NULL,    -- 'question', 'status', 'alert', 'info'
    title TEXT,
    message TEXT NOT NULL,
    context JSON,          -- Additional context (priority, phase, etc.)
    channels JSON,         -- Channels sent to ['slack', 'terminal', 'desktop']
    status TEXT DEFAULT 'pending',  -- 'pending', 'answered', 'timeout', 'dismissed'
    user_response TEXT,
    response_time_seconds FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Slack interactions log
CREATE TABLE slack_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER REFERENCES notifications(id),
    user_id TEXT,          -- Slack user ID
    action TEXT,           -- Button clicked or message sent
    routed_to TEXT,        -- 'daemon' or 'project_manager'
    result TEXT,           -- Response from daemon/PM
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Slack as Project Manager Interface** ⚡ NEW USE CASE:

Users can **fully interact with project manager via Slack**:

```
# Slack conversation:

User (in #coffee-maker channel):
@coffee-bot add a priority for implementing webhooks

Coffee Bot (Project Manager AI):
📋 I'll add a new priority for webhooks. Analyzing current roadmap...

Current priorities: 1-8
Suggested placement: PRIORITY 9
Estimated impact: ⭐⭐⭐⭐

╔════════════════════════════════════════════╗
║ 🔴 PRIORITY 9: Webhook System             ║
╠════════════════════════════════════════════╣
║ Duration: 1-2 weeks                        ║
║ Impact: ⭐⭐⭐⭐                               ║
║ Status: 📝 Planned                          ║
║                                             ║
║ Objectives:                                 ║
║ • Incoming webhook support                 ║
║ • Outgoing webhook notifications           ║
║ • Retry and failure handling               ║
╚════════════════════════════════════════════╝

[✅ Add to Roadmap] [✏️ Edit] [❌ Cancel]

User: (clicks "Add to Roadmap")

Coffee Bot:
✅ Added PRIORITY 9 to ROADMAP.md
✅ Synced to daemon environment
✅ Daemon will pick this up after PRIORITY 8

---

User: /view PRIORITY 2

Coffee Bot:
📋 PRIORITY 2: Roadmap Management CLI

Status: 🔄 In Progress (60% complete)
Started: 2025-10-09
Estimated completion: 2025-10-11

Completed deliverables:
✅ CLI framework
✅ Claude AI integration
✅ Chat interface
🔄 Roadmap parser (in progress)
📝 Commands (pending)

---

User: /metrics

Coffee Bot:
📊 Roadmap Metrics:

Development Velocity:
• Avg time per priority: 2.5 weeks
• Priorities completed: 2/9 (22%)
• Current sprint: PRIORITY 2 (60% done)
• Projected completion: 2025-12-20 (11 weeks)

[View Full Report] [Export PDF]
```

**Benefits of Unified Notification System**:
- ✅ **Slack as full interface**: Manage roadmap from Slack
- ✅ **Database-backed**: All notifications stored and queryable
- ✅ **Dual routing**: Same Slack bot talks to daemon AND project manager
- ✅ **Mobile-friendly**: Manage project from phone via Slack app
- ✅ **Async collaboration**: Team can interact with project manager
- ✅ **Audit trail**: All interactions logged in database
- ✅ **Flexible**: Terminal, desktop, Slack, email - all work together

**Benefits of Notification System**:
- ✅ **Multi-channel flexibility**: Choose notification method that fits workflow
- ✅ **Non-blocking**: User can work on other tasks while daemon waits
- ✅ **Mobile-friendly**: Webhook notifications work on phone (Slack/Discord apps)
- ✅ **Timeout handling**: Safe defaults when user unavailable
- ✅ **Input validation**: Ensures valid responses, prevents errors
- ✅ **Queue management**: Handles multiple concurrent questions
- ✅ **Audit trail**: All notifications and responses logged

---

**Observability & Logging for Notifications** ⚡ NEW:

The entire notification and autonomous daemon system is instrumented with **Langfuse** and **structured logging**.

**Updated Architecture with Unified Notifications** ⚡ NEW:

```
coffee_maker/
├── autonomous/
│   └── notifications/
│       ├── __init__.py
│       ├── unified_hub.py             # ⚡ NEW - Routes to daemon OR PM
│       ├── notifier.py                # Multi-channel notifications
│       ├── input_handler.py           # User input collection
│       ├── queue.py                   # Notification queue
│       ├── channels/
│       │   ├── terminal.py
│       │   ├── desktop.py
│       │   ├── webhook.py             # Slack, Discord, Teams
│       │   └── email.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── schema.py              # ⚡ NEW - notifications + slack_interactions tables
│       │   └── models.py              # ⚡ NEW - SQLAlchemy models
│       └── observability/
│           ├── langfuse_tracker.py
│           ├── logger.py
│           └── metrics.py

├── cli/
│   ├── roadmap_cli.py                 # Project Manager CLI
│   └── slack_integration.py           # ⚡ NEW - Slack bot interface

# Slack Bot Server (Flask/FastAPI)
slack_bot/
├── app.py                             # ⚡ NEW - Slack webhook server
├── routes/
│   ├── actions.py                     # Button click handlers
│   └── events.py                      # Message handlers
└── routing.py                         # ⚡ NEW - Route to daemon or PM
```

**Langfuse Integration Example**:

```python
from langfuse import Langfuse
from coffee_maker.autonomous.notifications import Notifier

# All daemon operations traced in Langfuse
langfuse = Langfuse()

# Main trace for autonomous implementation session
trace = langfuse.trace(
    name="autonomous-implementation",
    metadata={
        "priority": "PRIORITY 2: Analytics & Observability",
        "branch": "feature/analytics-export-langfuse"
    }
)

# Span for user notification
notification_span = trace.span(
    name="user-notification-required",
    input={
        "question": "Found API key in .env. Commit it?",
        "channels": ["terminal", "desktop", "slack"],
        "timeout": 300
    }
)

# Log user response
notification_span.end(
    output={
        "user_response": "no",
        "response_time_seconds": 45.2,
        "channel_used": "slack",
        "timed_out": False
    }
)
```

**Structured Logging**:

```python
import structlog

logger = structlog.get_logger()

# Log notification sent
logger.info(
    "notification_sent",
    notification_id="notif-001",
    question_type="security_check",
    channels=["terminal", "desktop", "slack"],
    severity="critical"
)

# Log user response
logger.info(
    "user_response_received",
    notification_id="notif-001",
    response="no",
    response_time_ms=45200,
    channel="slack",
    valid=True
)
```

**Metrics Tracked**:
- Notifications sent per hour/day
- Average user response time per channel
- Timeout rate by question type
- Most common questions requiring user input
- Channel effectiveness (response rate)
- Daemon blocking time waiting for user

**Benefits of Observability**:
- ✅ **Full traceability**: Every notification in Langfuse
- ✅ **Performance insights**: Identify slow response patterns
- ✅ **Trend analysis**: Track autonomous vs manual decisions
- ✅ **Debugging**: Correlate notifications with Claude actions
- ✅ **Cost tracking**: Monitor LLM usage during autonomous execution

**Safety Guarantees**:
- ✅ **All changes in Git**: Complete version history, easy rollback
- ✅ **Follows roadmap guidelines**: Git conventions, commit messages, tests
- ✅ **PR-based workflow**: Human review before merging to main
- ✅ **Test validation**: Auto-runs tests, blocks commits on failures
- ✅ **Branch isolation**: Each priority in separate branch
- ✅ **Progress transparency**: All changes documented in ROADMAP.md

**Benefits**:
- 🚀 **Accelerated development**: Claude implements while you plan
- 🤖 **Self-improving system**: Framework builds itself
- 📊 **Full traceability**: Every change documented and versioned
- 🎯 **Roadmap-driven**: Ensures alignment with project vision
- 💰 **Cost-effective**: Automation of repetitive implementation tasks
- 🧪 **Quality assured**: Tests run automatically before commits
- 🔄 **Continuous delivery**: Features implemented as soon as planned

**Real-Time ROADMAP.md Update Mechanism** ⚡ NEW:

The daemon needs to **safely update** the user's ROADMAP.md while avoiding conflicts. Here's the robust architecture:

**Challenge**: Both user and daemon modify ROADMAP.md simultaneously
- User adds new priorities, updates requirements
- Daemon updates task statuses, adds completion notes

**Solution: File Watcher + Git-Based Conflict Resolution**

```python
from coffee_maker.autonomous.roadmap import RoadmapSync

# Real-time bidirectional sync
sync = RoadmapSync(
    roadmap_path="docs/ROADMAP.md",
    sync_strategy="git-based",  # or "file-lock", "event-driven"
    conflict_resolution="user-wins",  # User changes always take precedence
    update_interval=5,  # Check for changes every 5 seconds
)

# Daemon workflow:
# 1. Daemon reads ROADMAP.md
# 2. Daemon implements feature
# 3. Before updating ROADMAP.md, daemon checks for user changes
# 4. If user modified ROADMAP.md → merge changes intelligently
# 5. Daemon updates only its designated sections (Status, Progress)
# 6. User modifications preserved (Requirements, Objectives)
```

**Architecture Options**:

### **Option 1: Git-Based Sync** ✅ **RECOMMENDED**

Use Git as the single source of truth:

```python
class GitBasedRoadmapSync:
    """Git-based real-time ROADMAP.md synchronization"""

    def __init__(self, roadmap_path: str):
        self.roadmap_path = roadmap_path
        self.daemon_branch = "daemon/roadmap-updates"
        self.user_branch = "main"

    def update_roadmap(self, updates: Dict[str, str]):
        """Safely update ROADMAP.md with daemon progress"""

        # 1. Fetch latest changes from user
        subprocess.run(["git", "fetch", "origin", self.user_branch])

        # 2. Check if user modified ROADMAP.md since last read
        result = subprocess.run(
            ["git", "diff", "HEAD", f"origin/{self.user_branch}", "--", self.roadmap_path],
            capture_output=True
        )

        if result.stdout:  # User made changes
            # 3. Pull user changes first
            subprocess.run(["git", "pull", "origin", self.user_branch])

            # 4. Re-read roadmap with user updates
            roadmap = self._read_roadmap()

        # 5. Apply daemon updates to specific sections only
        updated_roadmap = self._apply_daemon_updates(roadmap, updates)

        # 6. Write updated roadmap
        self._write_roadmap(updated_roadmap)

        # 7. Commit daemon changes
        subprocess.run(["git", "add", self.roadmap_path])
        subprocess.run([
            "git", "commit", "-m",
            f"chore(roadmap): update progress - {updates['priority']}"
        ])

        # 8. Push to remote
        subprocess.run(["git", "push", "origin", self.daemon_branch])

        # 9. Create PR for user review (optional, auto-merge if safe)
        if self._is_safe_to_merge():
            subprocess.run(["git", "merge", self.daemon_branch])
        else:
            self._create_pr_for_review()
```

**Benefits**:
- ✅ Git tracks all changes (full audit trail)
- ✅ User can review daemon updates via PRs
- ✅ Easy rollback if daemon makes mistakes
- ✅ Works with existing Git workflow

### **Option 2: File Lock with Retry** (Simpler, less robust)

```python
import fcntl
import time

class FileLockRoadmapSync:
    """File lock-based synchronization (simpler but less robust)"""

    def update_roadmap(self, updates: Dict[str, str]):
        """Update ROADMAP.md with file locking"""

        max_retries = 5
        for attempt in range(max_retries):
            try:
                # 1. Acquire exclusive lock
                with open(self.roadmap_path, "r+") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                    # 2. Read current roadmap
                    content = f.read()

                    # 3. Apply updates
                    updated_content = self._apply_updates(content, updates)

                    # 4. Write back
                    f.seek(0)
                    f.write(updated_content)
                    f.truncate()

                    # 5. Release lock (automatic on close)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                    logger.info("Roadmap updated successfully")
                    return

            except BlockingIOError:
                # User is currently editing the file
                logger.warning(f"Roadmap locked, retry {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)  # Exponential backoff

        logger.error("Failed to acquire roadmap lock after retries")
```

**Benefits**:
- ✅ Simple implementation
- ✅ Prevents concurrent writes
- ❌ No version history
- ❌ Can't detect user changes after daemon reads

### **Option 3: Event-Driven with File Watcher** ⚡ **BEST FOR REAL-TIME**

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RoadmapWatcher(FileSystemEventHandler):
    """Watch for user changes to ROADMAP.md in real-time"""

    def __init__(self, daemon):
        self.daemon = daemon
        self.last_modified_by = None

    def on_modified(self, event):
        if event.src_path.endswith("ROADMAP.md"):
            # 1. Check who modified (user or daemon)
            if self.last_modified_by == "daemon":
                # Daemon just updated, ignore
                self.last_modified_by = None
                return

            # 2. User modified the roadmap
            logger.info("User modified ROADMAP.md, reloading tasks")

            # 3. Re-parse roadmap for new tasks
            new_tasks = self.daemon.roadmap_parser.parse()

            # 4. Update daemon's task queue
            self.daemon.task_queue.update(new_tasks)

            # 5. Notify daemon of changes
            self.daemon.on_roadmap_updated(new_tasks)

# Usage:
observer = Observer()
observer.schedule(RoadmapWatcher(daemon), path="docs/", recursive=False)
observer.start()

# Daemon updates roadmap:
def update_roadmap_status(priority: str, status: str):
    watcher.last_modified_by = "daemon"  # Mark as daemon update

    # Apply update
    roadmap = read_roadmap()
    roadmap = update_status(roadmap, priority, status)
    write_roadmap(roadmap)

    # Watcher will ignore this change (last_modified_by = "daemon")
```

**Benefits**:
- ✅ **True real-time** updates (< 1 second latency)
- ✅ Daemon instantly aware of user changes
- ✅ User sees daemon progress updates immediately
- ✅ Works with any editor (VS Code, vim, etc.)

### **Option 4: Section-Based Locking** (Most Precise)

```python
class SectionBasedRoadmapSync:
    """Update only specific sections, avoid conflicts"""

    DAEMON_SECTIONS = [
        "## 📋 Project Status",
        "### 🔄 In Progress",
        "### ✅ Completed Projects"
    ]

    USER_SECTIONS = [
        "## 🚀 Prioritized Roadmap",
        "**Objectives**:",
        "**Key Features**:"
    ]

    def update_roadmap(self, section: str, updates: str):
        """Update only daemon-owned sections"""

        if section not in self.DAEMON_SECTIONS:
            raise ValueError(f"Daemon cannot modify {section}")

        # 1. Read roadmap
        roadmap = self._read_roadmap()

        # 2. Parse into sections
        sections = self._parse_sections(roadmap)

        # 3. Update only daemon section
        sections[section] = updates

        # 4. Preserve user sections unchanged
        for user_section in self.USER_SECTIONS:
            # Don't touch user sections
            pass

        # 5. Reconstruct roadmap
        updated_roadmap = self._reconstruct_roadmap(sections)

        # 6. Write back
        self._write_roadmap(updated_roadmap)
```

**Example Section Ownership**:

```markdown
## 📋 Project Status  ← DAEMON OWNS (can update status)

### ✅ Completed Projects
**Status**: ✅ COMPLETED  ← Daemon updates this
**Completion Date**: 2025-10-10  ← Daemon updates this

## 🚀 Prioritized Roadmap  ← USER OWNS (daemon read-only)

### 🔴 PRIORITY 2: Analytics
**Objectives**:  ← User defines this
- Export Langfuse traces  ← User defines this
**Status**: 🔄 In Progress  ← Daemon updates this
```

**Benefits**:
- ✅ Clear ownership boundaries
- ✅ Zero conflicts (daemon/user edit different sections)
- ✅ User can update requirements while daemon works
- ✅ Daemon can update status while user plans

### **Recommended Implementation: Hybrid Approach** ⚡

Combine the best of all approaches:

```python
class HybridRoadmapSync:
    """Best of all worlds: Git + File Watcher + Section Locking"""

    def __init__(self):
        self.git_sync = GitBasedRoadmapSync()
        self.file_watcher = RoadmapWatcher(self)
        self.section_lock = SectionBasedRoadmapSync()

    def start(self):
        # 1. Start file watcher for real-time user changes
        self.file_watcher.start()

        # 2. Use Git for daemon updates (audit trail)
        # 3. Use section locking to prevent conflicts

    def update_progress(self, priority: str, status: str, notes: str):
        """Daemon updates progress safely"""

        # 1. Check for user changes (via file watcher)
        if self.file_watcher.user_modified:
            # 2. Pull latest user changes from Git
            self.git_sync.pull_user_changes()

        # 3. Update only daemon-owned section
        updates = {
            "section": "### 🔄 In Progress",
            "priority": priority,
            "status": status,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }

        # 4. Apply section-locked update
        self.section_lock.update_roadmap(updates["section"], updates)

        # 5. Commit to Git for audit trail
        self.git_sync.commit_daemon_update(updates)

        # 6. Mark as daemon update (file watcher ignores)
        self.file_watcher.last_modified_by = "daemon"
```

**Complete Flow Example**:

```
User Action                          Daemon Action
────────────────────────────────────────────────────────────
User opens ROADMAP.md
User adds new PRIORITY 8
User saves file                      → File watcher detects change
                                     → Daemon reloads roadmap
                                     → Daemon adds PRIORITY 8 to queue
                                     → Daemon starts PRIORITY 8

User continues editing               → Daemon implements feature
User updates PRIORITY 9 objectives   → Daemon runs tests
User saves file                      → File watcher detects change
                                     → Daemon reloads (sees PRIORITY 9 update)

                                     → Daemon completes PRIORITY 8
                                     → Daemon updates "In Progress" section
                                     → File watcher marks as daemon update
User sees status change ← ────────── → Daemon saves ROADMAP.md
User reviews daemon update           → Daemon commits to Git
User merges daemon PR                → Daemon moves to PRIORITY 9
```

**Deliverables** (added to PRIORITY 2):
- [ ] `RoadmapSync` - Base synchronization interface
- [ ] `GitBasedRoadmapSync` - Git-based sync with audit trail
- [ ] `RoadmapWatcher` - File watcher for real-time user changes
- [ ] `SectionBasedRoadmapSync` - Section ownership and locking
- [ ] `HybridRoadmapSync` - Combined best-of-breed approach
- [ ] Integration tests for concurrent user/daemon updates
- [ ] Documentation on conflict resolution

**Timeline**:
- Week 1: Claude CLI integration + Roadmap parser + Sync mechanism (25-30h)
  - Day 1-2: ClaudeCLIInterface with auto-approval (8-10h)
  - Day 3-4: RoadmapParser + TaskExecutor (8-10h)
  - Day 5: RoadmapSync + File Watcher (6-8h) ⚡ NEW
  - Day 6: ProgressTracker with safe updates (3-4h) ⚡ UPDATED
- Week 2: Git automation + Safety + Daemon (20-25h)
  - Day 1-2: BranchManager + PRCreator (8-10h)
  - Day 3: Safety validation + rollback (6-8h)
  - Day 4-5: DevDaemon orchestration + tests (6-7h)
- **Total**: 45-55h (1-2 weeks) ⚡ UPDATED

---

**Claude CLI Agent Integration with Two-Way Messaging System** ⚡ NEW:

The Claude CLI agent leverages the two-way messaging system (described above) to interact with the project manager when it needs input or wants to report important milestones.

**Use Cases**:

1. **Questions Requiring Project Manager Input**:
   - "I found an API key in .env. Should I commit it?" (security decision)
   - "Test XYZ is failing. Should I fix it or skip it?" (scope decision)
   - "I found duplicate code. Should I refactor now or defer?" (priority decision)
   - "Should I use library X or Y for this feature?" (architecture decision)
   - "The current branch is behind main by 5 commits. Should I rebase?" (git workflow decision)

2. **Important Milestone Notifications**:
   - "✅ PRIORITY 2 implementation complete - 112/112 tests passing"
   - "📝 Pull request #123 created and ready for review"
   - "⚠️ Rate limit reached on OpenAI API - waiting 60 seconds"
   - "🎉 All deliverables for Sprint 1 completed"
   - "🔄 Started working on PRIORITY 3 - Streamlit Dashboard"
   - "❌ Build failed - 3 type errors found in module X"

**Implementation Architecture**:

```python
from coffee_maker.autonomous.notifications import Notifier, InputHandler
from coffee_maker.autonomous.claude_cli import ClaudeCLIInterface

class ClaudeAgentMessenger:
    """Enables Claude CLI agent to ask questions and notify project manager"""

    def __init__(self, notifier: Notifier, input_handler: InputHandler):
        self.notifier = notifier
        self.input_handler = input_handler
        self.claude_cli = ClaudeCLIInterface()

    def ask_project_manager(self, question: str, options: List[str] = None,
                           priority: str = "high", timeout: int = 300) -> str:
        """Claude agent asks project manager a question and waits for response

        Args:
            question: The question to ask
            options: Valid response options (e.g., ["yes", "no", "skip"])
            priority: Urgency level ("low", "medium", "high", "critical")
            timeout: Seconds to wait before using default safe action

        Returns:
            Project manager's response or safe default if timeout
        """
        # Create notification
        notification = {
            "id": f"claude-question-{datetime.now().timestamp()}",
            "title": "🤖 Claude CLI Agent - Input Required",
            "priority": priority,
            "question": question,
            "options": options or ["yes", "no"],
            "timeout": timeout,
            "context": {
                "current_task": self.claude_cli.current_task,
                "branch": self.claude_cli.current_branch,
                "severity": self._assess_severity(question)
            }
        }

        # Send via all enabled channels (terminal, desktop, Slack, etc.)
        self.notifier.send(notification)

        # Wait for project manager response (blocking or async)
        response = self.input_handler.wait_for_input(
            notification_id=notification["id"],
            timeout=timeout,
            validation=options  # Ensures valid response
        )

        # Handle timeout with safe default
        if response.timed_out:
            safe_default = self._get_safe_default(question)
            logger.warning(f"No response from project manager, using safe default: {safe_default}")
            return safe_default

        return response.value

    def notify_milestone(self, milestone: str, level: str = "info",
                        details: Dict[str, Any] = None):
        """Claude agent notifies project manager of important milestone

        Args:
            milestone: The milestone message
            level: Notification level ("info", "success", "warning", "error")
            details: Additional context (tests passed, files changed, etc.)
        """
        notification = {
            "id": f"claude-milestone-{datetime.now().timestamp()}",
            "title": f"🤖 Claude CLI Agent - {self._get_emoji(level)} Milestone",
            "level": level,
            "message": milestone,
            "details": details or {},
            "context": {
                "current_task": self.claude_cli.current_task,
                "branch": self.claude_cli.current_branch,
                "timestamp": datetime.now().isoformat()
            },
            "requires_response": False  # One-way notification
        }

        # Send via all enabled channels
        self.notifier.send(notification)

        # Log to Langfuse for full traceability
        langfuse_client.trace(
            name="claude-milestone-notification",
            input={"milestone": milestone},
            output={"notification_sent": True}
        )

# Integration with ClaudeCLIInterface
class EnhancedClaudeCLIInterface(ClaudeCLIInterface):
    """Claude CLI with two-way messaging capabilities"""

    def __init__(self, messenger: ClaudeAgentMessenger):
        super().__init__()
        self.messenger = messenger

    def execute_task(self, task: str):
        """Execute task with automatic project manager interaction"""

        # Notify start
        self.messenger.notify_milestone(
            f"Started: {task}",
            level="info",
            details={"task": task}
        )

        try:
            # Execute task (may internally ask questions)
            result = super().execute_task(task)

            # Notify success
            self.messenger.notify_milestone(
                f"Completed: {task}",
                level="success",
                details={"result": result}
            )

            return result

        except Exception as e:
            # Ask project manager how to handle error
            response = self.messenger.ask_project_manager(
                f"Task '{task}' failed with error: {e}. How should I proceed?",
                options=["retry", "skip", "abort"],
                priority="high"
            )

            if response == "retry":
                return self.execute_task(task)  # Recursive retry
            elif response == "skip":
                return None
            else:
                raise
```

**Example Flow**:

```python
# Autonomous daemon working on PRIORITY 2
daemon = AutonomousDaemon()
claude = EnhancedClaudeCLIInterface(messenger)

# Claude starts implementing feature
claude.execute_task("Implement Langfuse export functionality")

# Claude encounters decision point
response = claude.messenger.ask_project_manager(
    "Should I add rate limiting to the export API?",
    options=["yes", "no", "defer"],
    priority="medium",
    timeout=300
)

if response == "yes":
    claude.execute_task("Add rate limiting to export API")

# Claude completes milestone
claude.messenger.notify_milestone(
    "✅ Export functionality complete - 45/45 tests passing",
    level="success",
    details={
        "tests_passed": 45,
        "files_changed": 8,
        "lines_added": 320
    }
)
```

**Benefits**:
- ✅ **Autonomous with oversight**: Claude works independently but asks when uncertain
- ✅ **Milestone visibility**: Project manager always knows current progress
- ✅ **Smart escalation**: Only critical questions interrupt project manager
- ✅ **Multi-channel**: Notifications reach project manager wherever they are
- ✅ **Audit trail**: All questions and responses logged in Langfuse
- ✅ **Safe defaults**: Timeout handling prevents Claude from making risky assumptions

**Deliverables** (added to PRIORITY 3):
- [ ] `ClaudeAgentMessenger` - Two-way messaging for Claude agent
- [ ] `EnhancedClaudeCLIInterface` - Claude CLI with messaging capabilities
- [ ] Question classification logic (critical vs routine)
- [ ] Safe default determination for timeout scenarios
- [ ] Milestone detection and notification triggers
- [ ] Integration tests for Claude ↔ Project Manager interaction
- [ ] Documentation on question patterns and safe defaults

**Timeline**: 1-2 days (8-12h) - to be added to PRIORITY 3 timeline

---

**Phase 1: Console Messaging Implementation** ⚡ NEW (REQUIRED):

This project implements the two-way messaging system with **console-based notifications** for the project manager UI. This is the foundational messaging channel that supports bidirectional communication for questions and milestone notifications.

**Objectives**:
- Implement console-based messaging for local project manager interaction
- Support rich formatting (colors, emojis, code blocks, panels)
- Enable interactive prompts with validation
- Provide base abstractions for future channel implementations (Phase 2)

**Architecture**:

```
coffee_maker/autonomous/notifications/
├── __init__.py
├── base.py                      # ⚡ NEW - Abstract base classes
│   ├── NotificationChannel (ABC)
│   ├── MessageFormatter (ABC)
│   └── InputCollector (ABC)
├── channels/
│   ├── __init__.py
│   └── console_channel.py       # ⚡ NEW - Console/terminal notifications
├── formatters/
│   ├── __init__.py
│   └── console_formatter.py     # ⚡ NEW - Rich text formatting for terminal
├── notifier.py                  # ⚡ NEW - Main Notifier class
├── input_handler.py             # ⚡ NEW - InputHandler class (waits for responses)
└── config.py                    # ⚡ NEW - Channel configuration
```

**Implementation Details**:

### 1. Console Channel (Project Manager UI)

```python
from coffee_maker.autonomous.notifications.base import NotificationChannel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import threading

class ConsoleChannel(NotificationChannel):
    """Console-based notification channel for local project manager"""

    def __init__(self, config: dict):
        self.console = Console()
        self.enabled = config.get("enabled", True)
        self.use_rich_formatting = config.get("rich_formatting", True)
        self.response_queue = {}  # {notification_id: response}

    def send_notification(self, notification: dict) -> bool:
        """Display notification in console with rich formatting"""

        if not self.enabled:
            return False

        # Format notification with rich styling
        title = notification["title"]
        message = notification.get("question") or notification.get("message")
        options = notification.get("options", [])
        priority = notification.get("priority", "medium")

        # Color based on priority
        color_map = {
            "low": "blue",
            "medium": "yellow",
            "high": "orange",
            "critical": "red"
        }
        border_style = color_map.get(priority, "blue")

        # Display notification panel
        panel = Panel(
            f"[bold]{message}[/bold]\n\n"
            f"Options: {', '.join(options)}\n"
            f"Priority: {priority}\n"
            f"Timeout: {notification.get('timeout', 300)}s",
            title=f"🤖 {title}",
            border_style=border_style,
            padding=(1, 2)
        )

        self.console.print(panel)

        return True

    def collect_input(self, notification: dict) -> str:
        """Collect input from console (blocking)"""

        options = notification.get("options", [])
        notification_id = notification["id"]

        # Prompt for input with validation
        while True:
            response = Prompt.ask(
                "[bold cyan]Your response[/bold cyan]",
                choices=options if options else None
            )

            if not options or response in options:
                self.response_queue[notification_id] = response
                return response

            self.console.print(f"[red]Invalid option. Choose from: {', '.join(options)}[/red]")

    def send_milestone(self, notification: dict) -> bool:
        """Display milestone notification (no input required)"""

        level = notification.get("level", "info")
        message = notification.get("message")
        details = notification.get("details", {})

        # Emoji based on level
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        emoji = emoji_map.get(level, "ℹ️")

        # Color based on level
        color_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        color = color_map.get(level, "blue")

        self.console.print(
            f"[{color}]{emoji} {message}[/{color}]"
        )

        # Show details if present
        if details:
            self.console.print(f"[dim]{details}[/dim]")

        return True
```

### 2. Console Notifier Class

```python
from coffee_maker.autonomous.notifications.channels.console_channel import ConsoleChannel
from typing import Optional

class ConsoleNotifier:
    """Simple console-only notifier for Phase 1"""

    def __init__(self, config: dict = None):
        config = config or {}
        self.console_channel = ConsoleChannel(config.get("console", {"enabled": True}))

    def send_notification(self, notification: dict) -> bool:
        """Send notification to console"""
        return self.console_channel.send_notification(notification)

    def send_milestone(self, notification: dict) -> bool:
        """Send milestone to console"""
        return self.console_channel.send_milestone(notification)

    def collect_input(self, notification: dict, timeout: int = 300) -> Optional[str]:
        """Collect input from console"""
        return self.console_channel.collect_input(notification)
```

**Configuration Example**:

```python
# config/notifications.yaml
notifications:
  console:
    enabled: true
    rich_formatting: true

# Usage
from coffee_maker.autonomous.notifications import ConsoleNotifier

notifier = ConsoleNotifier(config["notifications"])

# Send question to console
notification = {
    "id": "q-001",
    "title": "Claude CLI Agent - Input Required",
    "question": "Should I commit the API key in .env?",
    "options": ["yes", "no", "skip"],
    "priority": "high",
    "timeout": 300
}

notifier.send_notification(notification)
response = notifier.collect_input(notification, timeout=300)

# Send milestone to console
milestone = {
    "id": "m-001",
    "title": "Claude CLI Agent - Milestone",
    "message": "✅ PRIORITY 2 implementation complete",
    "level": "success",
    "details": {
        "tests_passed": "112/112",
        "files_changed": 8,
        "duration": "2.5 hours"
    }
}

notifier.send_milestone(milestone)
```

**Key Features**:

1. **Console Channel**:
   - Rich text formatting with colors and borders
   - Priority-based styling (blue/yellow/orange/red)
   - Interactive prompts with validation
   - Immediate local feedback
   - Emoji support for visual clarity

2. **Extensible Design**:
   - Abstract base classes for future channel implementations (Phase 2)
   - Clean separation of concerns (channel, formatter, input collector)
   - Easy to add new channels without modifying existing code

**Deliverables**:
- [ ] `NotificationChannel` abstract base class
- [ ] `MessageFormatter` abstract base class
- [ ] `InputCollector` abstract base class
- [ ] `ConsoleChannel` implementation with Rich formatting
- [ ] `ConsoleNotifier` orchestrator
- [ ] Configuration system for channel settings
- [ ] Unit tests for console channel
- [ ] Integration tests with mock Claude CLI interactions
- [ ] Documentation on usage and configuration
- [ ] Example configurations for common use cases

**Timeline**: 1.5-2 days (12-16h)
- Day 1: Base classes and console channel (8-10h)
- Day 2: Notifier orchestration, testing, and documentation (4-6h)

**Dependencies**:
```bash
pip install rich
```

**Benefits of Phase 1**:
- ✅ **Immediate value**: Console notifications work out of the box
- ✅ **Foundation for Phase 2**: Clean architecture ready for Slack integration
- ✅ **No external dependencies**: Works without internet or Slack account
- ✅ **Simple setup**: Zero configuration required for basic usage

---

**Phase 2: Slack Integration** ⚡ NEW (OPTIONAL):

This project extends the messaging system with **Slack integration**, enabling remote/mobile notifications and responses. Built on top of Phase 1's abstractions, this allows the project manager to interact with Claude from anywhere via Slack.

**Objectives**:
- Implement Slack channel using Slack SDK and Block Kit
- Add interactive buttons for quick responses
- Set up webhook handler for button click events
- Provide comprehensive setup documentation for Slack app configuration
- Enable multi-channel orchestration (console + Slack simultaneously)
- Support "first response wins" pattern (project manager can respond via any channel)

**Architecture Extension**:

```
coffee_maker/autonomous/notifications/
├── channels/
│   ├── console_channel.py       # ✅ Phase 1
│   └── slack_channel.py         # ⚡ NEW - Slack notifications
├── formatters/
│   ├── console_formatter.py     # ✅ Phase 1
│   └── slack_formatter.py       # ⚡ NEW - Slack Block Kit formatting
├── notifier.py                  # ⚡ UPDATED - Multi-channel support
├── webhook/
│   ├── __init__.py              # ⚡ NEW
│   ├── slack_handler.py         # ⚡ NEW - Handle Slack button clicks
│   └── server.py                # ⚡ NEW - Flask/FastAPI webhook server
└── docs/
    └── slack_setup_guide.md     # ⚡ NEW - Complete Slack setup instructions
```

**Implementation: Slack Channel**

```python
from coffee_maker.autonomous.notifications.base import NotificationChannel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

class SlackChannel(NotificationChannel):
    """Slack-based notification channel for remote project manager"""

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", False)
        self.bot_token = config.get("bot_token")  # From env: SLACK_BOT_TOKEN
        self.channel_id = config.get("channel_id")  # e.g., "#claude-notifications"
        self.client = WebClient(token=self.bot_token) if self.bot_token else None
        self.response_queue = {}  # {notification_id: response}

        if not self.bot_token:
            logger.warning("Slack bot token not configured, channel disabled")
            self.enabled = False

    def send_notification(self, notification: dict) -> bool:
        """Send notification to Slack with interactive buttons"""

        if not self.enabled or not self.client:
            return False

        try:
            blocks = self._build_question_blocks(notification)
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=notification["title"],  # Fallback text
                blocks=blocks
            )

            notification["slack_ts"] = response["ts"]
            logger.info(f"Sent Slack notification: {notification['id']}")
            return True

        except SlackApiError as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

    def _build_question_blocks(self, notification: dict) -> list:
        """Build Slack Block Kit blocks with interactive buttons"""

        message = notification.get("question") or notification.get("message")
        options = notification.get("options", [])
        priority = notification.get("priority", "medium")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🤖 {notification['title']}", "emoji": True}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{message}*"}
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Priority: `{priority}` | Timeout: {notification.get('timeout', 300)}s"}
                ]
            }
        ]

        # Add interactive buttons
        if options:
            actions = {
                "type": "actions",
                "block_id": f"question_{notification['id']}",
                "elements": []
            }

            for option in options:
                style = "primary" if option == "yes" else ("danger" if option in ["abort", "no"] else None)
                button = {
                    "type": "button",
                    "text": {"type": "plain_text", "text": option.capitalize(), "emoji": True},
                    "value": option,
                    "action_id": f"response_{option}"
                }
                if style:
                    button["style"] = style
                actions["elements"].append(button)

            blocks.append(actions)

        return blocks

    def send_milestone(self, notification: dict) -> bool:
        """Send milestone notification to Slack"""

        if not self.enabled or not self.client:
            return False

        try:
            level = notification.get("level", "info")
            message = notification.get("message")
            details = notification.get("details", {})

            emoji_map = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
            emoji = emoji_map.get(level, "ℹ️")

            fields = [{"type": "mrkdwn", "text": f"*{k}:*\n{v}"} for k, v in details.items()]

            blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"{emoji} *{message}*"}}]
            if fields:
                blocks.append({"type": "section", "fields": fields})

            self.client.chat_postMessage(channel=self.channel_id, text=message, blocks=blocks)
            return True

        except SlackApiError as e:
            logger.error(f"Failed to send Slack milestone: {e}")
            return False

    def handle_interaction(self, payload: dict):
        """Handle Slack button click (called by webhook)"""

        action = payload["actions"][0]
        response_value = action["value"]
        notification_id = action["block_id"].replace("question_", "")

        self.response_queue[notification_id] = response_value

        # Update Slack message to show response
        self.client.chat_update(
            channel=payload["channel"]["id"],
            ts=payload["message"]["ts"],
            text=f"✅ Response received: {response_value}",
            blocks=[
                {"type": "section", "text": {"type": "mrkdwn", "text": f"✅ *Response received:* `{response_value}`"}}
            ]
        )

        logger.info(f"Received Slack response for {notification_id}: {response_value}")
```

**Implementation: Multi-Channel Notifier**

```python
from coffee_maker.autonomous.notifications.channels.console_channel import ConsoleChannel
from coffee_maker.autonomous.notifications.channels.slack_channel import SlackChannel
from typing import Optional
import threading

class MultiChannelNotifier:
    """Unified notifier supporting console + Slack"""

    def __init__(self, config: dict):
        self.channels = []

        # Console channel (always available)
        if config.get("console", {}).get("enabled", True):
            self.channels.append(ConsoleChannel(config.get("console", {})))

        # Slack channel (optional)
        if config.get("slack", {}).get("enabled", False):
            self.channels.append(SlackChannel(config["slack"]))

    def send_notification(self, notification: dict) -> bool:
        """Send to all enabled channels"""
        results = [ch.send_notification(notification) for ch in self.channels]
        return any(results)

    def send_milestone(self, notification: dict) -> bool:
        """Send milestone to all channels"""
        results = [ch.send_milestone(notification) for ch in self.channels]
        return any(results)

    def collect_input(self, notification: dict, timeout: int = 300) -> Optional[str]:
        """Collect from first responding channel (race condition)"""

        responses = []
        threads = []

        for channel in self.channels:
            thread = threading.Thread(
                target=lambda ch: responses.append(ch.collect_input(notification)),
                args=(channel,)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # Wait for first response
        for thread in threads:
            thread.join(timeout=timeout)

        return responses[0] if responses else None
```

**Slack Webhook Handler**

```python
from flask import Flask, request, jsonify
from coffee_maker.autonomous.notifications.channels.slack_channel import SlackChannel

app = Flask(__name__)
slack_channel = SlackChannel(config["slack"])  # Global instance

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack interactive events"""

    payload = request.json

    # Verify Slack challenge (initial setup)
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload["challenge"]})

    # Handle button click
    if payload.get("type") == "block_actions":
        slack_channel.handle_interaction(payload)
        return jsonify({"status": "ok"})

    return jsonify({"status": "ignored"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**Configuration Example**

```yaml
# config/notifications.yaml
notifications:
  console:
    enabled: true
    rich_formatting: true

  slack:
    enabled: true
    bot_token: ${SLACK_BOT_TOKEN}
    channel_id: "#claude-notifications"
    webhook_url: "https://your-domain.com/slack/events"
```

**Comprehensive Slack Setup Documentation** (`docs/slack_setup_guide.md`):

```markdown
# Slack Integration Setup Guide

## Overview

This guide walks you through setting up Slack integration for Claude CLI notifications.
Follow these steps carefully to enable remote notifications and interactive responses.

## Prerequisites

- Slack workspace where you have admin permissions
- Public URL for webhook endpoint (use ngrok for development)
- Python environment with `slack-sdk` and `flask` installed

## Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. App Name: "Claude CLI Notifications"
5. Workspace: Select your workspace
6. Click "Create App"

## Step 2: Configure Bot Permissions

1. In your app settings, go to "OAuth & Permissions"
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add the following scopes:
   - `chat:write` - Send messages
   - `chat:write.public` - Send to public channels
   - `channels:read` - List channels
   - `groups:read` - List private channels

4. Scroll up and click "Install to Workspace"
5. Click "Allow"
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

## Step 3: Save Bot Token

Add token to your `.env` file:

```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL_ID=#claude-notifications
```

## Step 4: Create Notification Channel

1. In Slack, create a new channel: `#claude-notifications`
2. Invite the bot: Type `/invite @Claude CLI Notifications` in the channel

## Step 5: Set Up Webhook Endpoint

### For Development (using ngrok):

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start webhook server
python coffee_maker/autonomous/notifications/webhook/server.py

# In another terminal, expose it
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### For Production:

Deploy webhook server to your hosting provider (Heroku, AWS, etc.)
Ensure HTTPS is enabled.

## Step 6: Configure Interactive Components

1. Go back to your Slack app settings
2. Navigate to "Interactivity & Shortcuts"
3. Toggle "Interactivity" ON
4. Set "Request URL" to: `https://your-domain.com/slack/events`
5. Click "Save Changes"

## Step 7: Test the Integration

```python
from coffee_maker.autonomous.notifications import MultiChannelNotifier

config = {
    "console": {"enabled": True},
    "slack": {
        "enabled": True,
        "bot_token": "xoxb-your-token",
        "channel_id": "#claude-notifications"
    }
}

notifier = MultiChannelNotifier(config)

# Send test notification
notifier.send_notification({
    "id": "test-001",
    "title": "Test Notification",
    "question": "Is Slack integration working?",
    "options": ["yes", "no"],
    "priority": "medium",
    "timeout": 300
})

# Check Slack channel for the message with buttons
```

## Step 8: Verify Button Responses

1. Click a button in Slack
2. Check webhook server logs for incoming request
3. Message should update to show "✅ Response received: yes"

## Troubleshooting

### "Bot not found" error
- Make sure bot is invited to the channel: `/invite @Claude CLI Notifications`

### Buttons not working
- Verify webhook URL in "Interactivity & Shortcuts"
- Check webhook server logs for errors
- Ensure HTTPS is used (not HTTP)

### Messages not sent
- Verify bot token is correct
- Check bot has `chat:write` scope
- Ensure channel ID is correct (starts with # or C)

## Security Best Practices

1. **Never commit tokens**: Use `.env` file, add to `.gitignore`
2. **Verify requests**: Add Slack signature verification in webhook handler
3. **Use HTTPS only**: No HTTP in production
4. **Rotate tokens**: If compromised, regenerate in Slack app settings

## Advanced: Signature Verification

```python
import hmac
import hashlib

def verify_slack_request(request):
    """Verify request is from Slack"""

    slack_signature = request.headers.get("X-Slack-Signature")
    slack_timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    # Verify timestamp (prevent replay attacks)
    if abs(time.time() - int(slack_timestamp)) > 60 * 5:
        return False

    # Compute signature
    sig_basestring = f"v0:{slack_timestamp}:{request.get_data().decode()}"
    computed_signature = "v0=" + hmac.new(
        slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, slack_signature)
```

## Support

For issues, see:
- Slack API docs: https://api.slack.com/docs
- Slack SDK docs: https://slack.dev/python-slack-sdk/
```

**Deliverables**:
- [ ] `SlackChannel` implementation with Block Kit
- [ ] `MultiChannelNotifier` orchestrator (console + Slack)
- [ ] Slack webhook handler (Flask/FastAPI)
- [ ] Signature verification for security
- [ ] `slack_setup_guide.md` with step-by-step instructions
- [ ] Configuration templates and examples
- [ ] Unit tests for Slack channel
- [ ] Integration tests for multi-channel scenarios
- [ ] Troubleshooting documentation
- [ ] Example deployment configs (Heroku, AWS, etc.)

**Timeline**: 2-3 days (16-20h)
- Day 1: Slack channel implementation and Block Kit formatting (8-10h)
- Day 2: Webhook handler and multi-channel orchestration (5-7h)
- Day 3: Comprehensive documentation and testing (3-4h)

**Dependencies**:
```bash
pip install slack-sdk flask requests
```

**Environment Variables**:
```bash
# .env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL_ID=#claude-notifications
SLACK_WEBHOOK_URL=https://your-domain.com/slack/events
SLACK_SIGNING_SECRET=your-signing-secret  # For signature verification
```

**Benefits of Phase 2**:
- ✅ **Mobile access**: Respond to Claude from phone via Slack app
- ✅ **Remote work**: No need to be at console
- ✅ **Persistent history**: All notifications logged in Slack
- ✅ **Team visibility**: Other team members can see Claude's progress
- ✅ **Quick responses**: Interactive buttons for instant replies
- ✅ **Multi-channel flexibility**: Use console or Slack, whichever is convenient

---

**Implementation Decision Questions & Work-Around Strategy** ⚡ **INTELLIGENT BLOCKING**

**Problem**: Sometimes Claude encounters decisions that require human judgment (e.g., "Should we use SQLAlchemy or sqlite3?"). The daemon should:
1. **Ask the question intelligently** (with analysis and recommendations)
2. **Continue working on other tasks** while waiting for an answer
3. **Resume blocked task** once decision is made

**Solution: Question Queue + Task Dependency Tracking**

```python
from coffee_maker.autonomous.decision_queue import DecisionQueue, TaskDependency

class IntelligentDaemon:
    """Daemon that asks questions and works around blocked tasks"""

    def __init__(self):
        self.decision_queue = DecisionQueue()
        self.task_graph = TaskDependency()

    def encounter_decision_point(self, question: str, context: dict):
        """Claude encounters a decision that needs user input"""

        # 1. Create decision request with full analysis
        decision = self.decision_queue.create_decision(
            question=question,
            priority="PRIORITY_1",  # Current task
            context=context,
            analysis={
                "options": [
                    {
                        "name": "Option 1: Keep SQLAlchemy",
                        "pros": ["Elegant queries", "Type safety", "PostgreSQL migration"],
                        "cons": ["Heavy dependency", "Complexity"],
                        "recommendation_score": 6  # out of 10
                    },
                    {
                        "name": "Option 2: Use native sqlite3",
                        "pros": ["Zero dependencies", "Lighter", "Sufficient for use case"],
                        "cons": ["Manual SQL", "Less type safety"],
                        "recommendation_score": 8  # out of 10
                    }
                ],
                "recommended": "Option 2",
                "reasoning": "Analytics module is isolated, sqlite3 is sufficient"
            },
            estimated_impact="4-6 hours to implement chosen option"
        )

        # 2. Notify user with structured decision request
        self.notifier.send_decision_request(decision)

        # 3. Mark current task as blocked
        self.task_graph.mark_blocked(
            task="PRIORITY_1: Analytics Module",
            blocked_by=decision.id,
            blocking_since=datetime.now()
        )

        # 4. Find work-around tasks (tasks that don't depend on this decision)
        independent_tasks = self.task_graph.find_independent_tasks(
            blocked_task="PRIORITY_1"
        )

        # 5. Continue working on independent tasks
        logger.info(f"Task blocked on decision {decision.id}")
        logger.info(f"Found {len(independent_tasks)} independent tasks to work on")

        for task in independent_tasks:
            logger.info(f"Working on: {task.name}")
            self.execute_task(task)

        # 6. Periodically check if decision is answered
        while not decision.is_answered():
            time.sleep(60)  # Check every minute

            # Continue working on other things
            if independent_tasks:
                next_task = independent_tasks.pop(0)
                self.execute_task(next_task)

        # 7. Resume blocked task once decision is made
        user_decision = decision.get_answer()
        logger.info(f"Decision received: {user_decision}")

        self.task_graph.unblock(task="PRIORITY_1")
        self.resume_task("PRIORITY_1", decision=user_decision)
```

**Decision Request Notification Format**:

```markdown
╔════════════════════════════════════════════════════════════╗
║ 🤖 CLAUDE - IMPLEMENTATION DECISION REQUIRED               ║
╠════════════════════════════════════════════════════════════╣
║ Priority: PRIORITY 1 - Analytics & Observability           ║
║ Task: Implement Langfuse export module                     ║
║ Decision Point: Database library choice                    ║
║ Time: 2025-10-09 14:45:00                                  ║
╠════════════════════════════════════════════════════════════╣
║ QUESTION:                                                   ║
║ Should we use SQLAlchemy or native sqlite3 for the        ║
║ analytics module?                                          ║
║                                                            ║
║ ANALYSIS:                                                   ║
║                                                            ║
║ Option 1: Keep SQLAlchemy ⭐⭐⭐⭐⭐⭐ (6/10)                  ║
║ Pros:                                                       ║
║   • Elegant ORM with relationship mapping                 ║
║   • Type-safe database operations                         ║
║   • Easy PostgreSQL migration path                        ║
║ Cons:                                                       ║
║   • Heavy dependency (~2MB + sub-dependencies)            ║
║   • Only used in analytics module (isolated)              ║
║   • Adds complexity for simple CRUD operations            ║
║                                                            ║
║ Option 2: Use native sqlite3 ⭐⭐⭐⭐⭐⭐⭐⭐ (8/10) ✅ RECOMMENDED ║
║ Pros:                                                       ║
║   • Zero external dependencies (stdlib)                   ║
║   • Lighter weight solution                               ║
║   • Sufficient for analytics use case                     ║
║   • Simpler for isolated module                           ║
║ Cons:                                                       ║
║   • Manual SQL query writing                              ║
║   • Less type safety                                      ║
║   • Need to rewrite ~500 lines                            ║
║                                                            ║
║ RECOMMENDATION: Option 2 (Use sqlite3)                    ║
║ Reasoning: The analytics module is only used by           ║
║ standalone scripts, not core application. sqlite3         ║
║ provides sufficient functionality without the weight      ║
║ of SQLAlchemy.                                             ║
║                                                            ║
║ ESTIMATED EFFORT: 4-6 hours                                ║
╠════════════════════════════════════════════════════════════╣
║ YOUR DECISION:                                              ║
║                                                            ║
║ [1] Option 1: Keep SQLAlchemy                             ║
║ [2] Option 2: Use sqlite3 (recommended)                   ║
║ [3] Option 3: Defer decision, continue with other work    ║
║ [4] Custom: (type alternative approach)                   ║
╠════════════════════════════════════════════════════════════╣
║ WHILE YOU DECIDE:                                           ║
║ I'll continue working on these independent tasks:          ║
║   • PRIORITY 2: Project Manager CLI (Phase 1 - MVP)       ║
║   • PRIORITY 2.5: UX Documentation                         ║
║   • Code refactoring (Sprints 5-6)                        ║
║                                                            ║
║ The blocked task (Analytics module) will resume once      ║
║ you provide your decision.                                ║
╚════════════════════════════════════════════════════════════╝

Enter choice [1-4]: _
```

**Task Dependency Graph**:

```python
class TaskDependency:
    """Tracks task dependencies and finds independent work"""

    def __init__(self):
        # Task dependency graph
        self.dependencies = {
            "PRIORITY_1": {
                "depends_on": [],  # No dependencies
                "blocked_by": None,  # Can be decision ID
                "sub_tasks": [
                    "analytics_db_schema",
                    "analytics_exporter",
                    "analytics_analyzer",
                    "analytics_tests"
                ]
            },
            "PRIORITY_2": {
                "depends_on": [],  # Independent
                "sub_tasks": ["cli_framework", "roadmap_parser", "notification_db"]
            },
            "PRIORITY_2.5": {
                "depends_on": ["PRIORITY_2.cli_framework"],  # Needs CLI first
                "sub_tasks": ["ux_audit", "documentation", "setup_wizard"]
            },
            "PRIORITY_3": {
                "depends_on": ["PRIORITY_2"],  # Needs project manager CLI
                "sub_tasks": ["daemon_core", "claude_interface", "git_manager"]
            }
        }

    def find_independent_tasks(self, blocked_task: str) -> List[str]:
        """Find tasks that don't depend on the blocked task"""
        independent = []

        for task, info in self.dependencies.items():
            # Skip the blocked task itself
            if task == blocked_task:
                continue

            # Check if task depends on blocked task
            depends_on_blocked = any(
                blocked_task in dep for dep in info["depends_on"]
            )

            if not depends_on_blocked and not info.get("blocked_by"):
                # This task can be worked on!
                independent.append(task)

                # Also add sub-tasks that are independent
                for sub_task in info.get("sub_tasks", []):
                    independent.append(f"{task}.{sub_task}")

        return independent
```

**Example Workflow**:

```python
# Daemon is working on PRIORITY 1 (Analytics)
daemon.start_task("PRIORITY_1")

# Claude encounters decision point while implementing analytics module
decision = daemon.encounter_decision_point(
    question="Should we use SQLAlchemy or native sqlite3?",
    context={
        "current_code_size": "~500 lines using SQLAlchemy",
        "usage": "Only in standalone scripts",
        "current_dependencies": ["sqlalchemy==2.0.x"]
    }
)

# Daemon creates structured decision request with analysis
# Notifies user via Slack/terminal
# Marks PRIORITY_1 as blocked

# Meanwhile, daemon finds independent work:
independent_tasks = [
    "PRIORITY_2: Project Manager CLI",
    "PRIORITY_2.5: UX Documentation",
    "Code refactoring: Sprint 5"
]

# Daemon starts working on PRIORITY 2 while waiting for decision
daemon.start_task("PRIORITY_2")

# ... hours later, user responds: "Option 2"
decision.set_answer("Option 2: Use sqlite3")

# Daemon is notified of decision
daemon.on_decision_answered(decision)

# Daemon completes current task (PRIORITY 2.cli_framework)
# Then returns to blocked task (PRIORITY_1) with user's decision
daemon.resume_task("PRIORITY_1", decision="Option 2")

# Continues implementing analytics module with sqlite3
```

**Decision Database Schema**:

```sql
CREATE TABLE decision_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority TEXT NOT NULL,           -- Which priority this affects
    task TEXT NOT NULL,                -- Specific task blocked
    question TEXT NOT NULL,            -- Question for user
    context JSON,                      -- Context/analysis data
    options JSON,                      -- Array of options with pros/cons
    recommended_option TEXT,           -- Claude's recommendation
    reasoning TEXT,                    -- Why this recommendation
    estimated_impact TEXT,             -- Time/effort estimate
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    answered_at DATETIME,
    user_answer TEXT,                  -- User's choice
    status TEXT DEFAULT 'pending',     -- pending/answered/expired
    workaround_tasks JSON              -- Tasks daemon worked on while waiting
);

CREATE TABLE blocked_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    blocked_by_decision_id INTEGER REFERENCES decision_queue(id),
    blocked_since DATETIME DEFAULT CURRENT_TIMESTAMP,
    resumed_at DATETIME,
    total_blocked_duration_seconds INTEGER
);
```

**Benefits**:
- ✅ **Intelligent blocking**: Daemon doesn't waste time waiting
- ✅ **Structured decisions**: User gets full analysis, not just raw question
- ✅ **Work continuity**: Other tasks progress while blocked task waits
- ✅ **Audit trail**: All decisions logged with context
- ✅ **Resumable**: Daemon seamlessly resumes blocked task with user's decision
- ✅ **Transparency**: User sees what daemon is doing while waiting
- ✅ **Efficiency**: Maximizes productive time, minimizes idle time

**Integration with Notification System**:

Decision requests use the same notification infrastructure (Slack, terminal, email) but with specialized formatting that includes:
- Full analysis with pros/cons
- Recommendation with reasoning
- Impact estimate
- While-you-decide status (what daemon is working on)

This transforms the daemon from a **sequential executor** into an **intelligent parallel worker** that maximizes productivity even when blocked.

---

### 🔴 **PRIORITY 2.5: New User Experience & Documentation** ⚡ **UX FOCUS**

**Estimated Duration**: 3-5 days
**Impact**: ⭐⭐⭐⭐⭐ (Critical for adoption)
**Status**: 📝 Planned
**Dependency**: Should be done after PRIORITY 2 (Project Manager CLI) MVP is complete
**Why Important**: New users need clear onboarding - we're too close to the code to see friction points

#### Project: Put yourself in new user's shoes - UX audit & improvements

**Core Philosophy**: Act as a first-time user trying to understand and use the project_manager and Slack notification system. Identify gaps, confusion points, and documentation needs.

**Key Questions to Answer**:
1. How does a new user discover project_manager exists?
2. What does project_manager do? (Clear value proposition)
3. How do I set it up for the first time?
4. How do I use it day-to-day?
5. How do I connect it to Slack?
6. What notifications will I receive and why?
7. How do I troubleshoot common issues?
8. What are the core workflows?

#### Deliverables

**1. User Journey Map** (`docs/USER_JOURNEY_PROJECT_MANAGER.md`)
```markdown
# New User Journey - Project Manager

## Discovery Phase (0-5 minutes)
- How user finds project_manager (README? Docs? CLI help?)
- First impression - what does this tool do?
- Value proposition - why should I use this?

## Setup Phase (5-15 minutes)
- Prerequisites (Python version, dependencies)
- Installation steps (pip install? poetry?)
- Configuration (environment variables, database setup)
- First run experience
- Slack setup (if desired)

## Daily Usage Phase (ongoing)
- Core workflows (view roadmap, update status, check notifications)
- Common commands and their outputs
- Slack integration experience
- Error handling and recovery

## Power User Phase (advanced)
- Advanced features
- Customization options
- Integration with other tools
```

**2. Quick Start Guide** (`docs/QUICKSTART_PROJECT_MANAGER.md`)
```markdown
# Project Manager - Quick Start (5 minutes)

## What is Project Manager?
One-sentence description + 30-second video demo or GIF

## Installation
```bash
# 3-4 commands max
pip install coffee-maker
coffee-roadmap init
coffee-roadmap view
```

## Your First Task
Step-by-step walkthrough of ONE simple task
Example: "View current roadmap and check progress"

## Next Steps
- Link to full documentation
- Link to Slack setup guide
- Link to common workflows
```

**3. Slack Integration Guide** (`docs/SLACK_SETUP_GUIDE.md`)
```markdown
# Slack Integration - Step by Step

## Prerequisites
- Project Manager installed and working
- Slack workspace admin access (or know who to ask)

## Setup Steps (15 minutes)
1. Create Slack app
2. Configure bot permissions
3. Install to workspace
4. Get bot token
5. Configure project_manager
6. Test notification
7. Customize notification preferences

## What You'll Receive
- Examples of each notification type with screenshots
- When notifications are triggered
- How to respond to interactive notifications

## Troubleshooting
- Common issues and fixes
- How to verify setup
- Where to get help
```

**4. Feature Documentation** (`docs/PROJECT_MANAGER_FEATURES.md`)
```markdown
# Project Manager - Complete Feature Reference

## Core Commands
For each command:
- Purpose (what problem does it solve?)
- Usage (syntax + examples)
- Output (what to expect)
- Common options/flags
- Related commands

Examples:
- `coffee-roadmap view` - See current roadmap status
- `coffee-roadmap status <priority>` - Update priority status
- `coffee-roadmap notify` - Send Slack notification
- `coffee-roadmap sync` - Sync with daemon
```

**5. UX Improvements Implementation**

Based on audit findings, implement:

**A. Better CLI Help**
```python
# Current (if it exists):
$ coffee-roadmap --help
Usage: coffee-roadmap [OPTIONS] COMMAND [ARGS]...

# Improved:
$ coffee-roadmap --help

Coffee Maker Project Manager - AI-powered roadmap management

QUICK START:
  coffee-roadmap view              View current roadmap
  coffee-roadmap status            Update priority status
  coffee-roadmap notify "message"  Send Slack notification

COMMON WORKFLOWS:
  Check project status:
    $ coffee-roadmap view
    $ coffee-roadmap metrics

  Update roadmap:
    $ coffee-roadmap status PRIORITY_1 completed
    $ coffee-roadmap notify "Sprint 1 done!"

MORE INFO:
  - Full docs: https://docs.coffee-maker.dev/project-manager
  - Quick start: coffee-roadmap quickstart
  - Slack setup: coffee-roadmap slack-setup
```

**B. Interactive Setup Wizard**
```python
# coffee_maker/cli/setup.py
def interactive_setup():
    """Guide new users through first-time setup."""
    print("🎉 Welcome to Coffee Maker Project Manager!")
    print()
    print("This wizard will help you get started (5 minutes)")
    print()

    # Step 1: Check prerequisites
    check_python_version()
    check_dependencies()

    # Step 2: Configure database
    setup_database()

    # Step 3: Slack integration (optional)
    if prompt_yes_no("Set up Slack notifications?"):
        setup_slack_interactive()

    # Step 4: Verify setup
    verify_setup()

    # Step 5: Show next steps
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("  1. View roadmap: coffee-roadmap view")
    print("  2. Read docs: coffee-roadmap docs")
    print("  3. Try tutorial: coffee-roadmap tutorial")
```

**C. Better Error Messages**
```python
# Before:
# Error: Database connection failed

# After:
# ❌ Error: Cannot connect to database
#
# Possible causes:
#   1. Database not initialized (run: coffee-roadmap init)
#   2. Wrong database path in .env file
#   3. Missing WAL mode support
#
# Quick fix:
#   $ coffee-roadmap init --reset
#
# Need help? Run: coffee-roadmap diagnose
```

**D. In-app Tutorial**
```python
# coffee-roadmap tutorial
# Interactive walkthrough of common tasks with real commands
```

**E. Self-diagnosis Tool**
```python
# coffee-roadmap diagnose
# Checks:
# - Python version
# - Dependencies installed
# - Database accessible
# - Slack token valid (if configured)
# - ROADMAP.md readable
# - Git repository valid
#
# Output: Clear report with specific fixes for any issues
```

#### Success Metrics

**User Onboarding**:
- Time to first successful command: < 5 minutes
- Setup completion rate: > 90%
- Common errors encountered: < 2 per new user

**Documentation Quality**:
- New user can complete setup without external help: > 80%
- Find answer to common question in < 2 minutes: > 90%
- Documentation rated "helpful" or better: > 85%

**Usability**:
- Core workflows can be completed without referring to docs: > 70%
- Error messages lead to successful resolution: > 80%
- Slack integration setup success rate: > 85%

#### Implementation Plan

**Phase 1: Discovery & Audit** (1 day)
- Install project fresh (clean environment)
- Try to use project_manager as new user
- Document every friction point
- Note missing documentation
- List confusing terminology
- Identify gaps in error handling

**Phase 2: Documentation** (2 days)
- Write all 4 core documents (Quick Start, Slack Setup, Features, Journey Map)
- Create examples and screenshots
- Record demo videos/GIFs
- Review with fresh eyes (ideally external reviewer)

**Phase 3: UX Improvements** (2 days)
- Implement CLI help improvements
- Add interactive setup wizard
- Improve error messages (top 10 most common)
- Add self-diagnosis tool
- Add tutorial mode

**Phase 4: Validation** (half day)
- Test with new user (friend/colleague)
- Gather feedback
- Iterate on confusing parts
- Final polish

#### Benefits

- ✅ **Faster adoption**: New users productive in minutes, not hours
- ✅ **Reduced support burden**: Self-service documentation and diagnosis
- ✅ **Better first impression**: Professional, polished experience
- ✅ **Increased confidence**: Clear guidance reduces frustration
- ✅ **Scalability**: Documentation enables team adoption
- ✅ **Community growth**: Easy onboarding → more contributors
- ✅ **Foundation for daemon**: Good UX patterns established before AI takes over

**Note**: This priority can be completed BEFORE daemon implementation. It establishes UX patterns that the daemon can follow when autonomously working on future features.

---

### 🔴 **PRIORITY 3: Streamlit Analytics Dashboard** ⚡ NEW

**Estimated Duration**: 1-2 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: Requires PRIORITY 1 (Analytics & Observability) completed
**Note**: Can be implemented by autonomous daemon (PRIORITY 2) once it's complete! 🤖

#### Project: Streamlit Dashboard for LLM & Cost Analysis

**Objectives**:
- Interactive dashboard to analyze LLM usage
- Cost visualization by model, agent, and task
- Performance graphs and trends
- Custom report exports

**Key Features**:
- 📊 **Overview**: Global metrics (total costs, tokens, requests)
- 📈 **Trends**: Temporal graphs of usage and costs
- 🔍 **Model Analysis**: Comparison of GPT-4, Claude, Gemini, etc.
- 🤖 **Agent Analysis**: Performance and costs per agent
- 💰 **Budget tracking**: Alerts and overage predictions
- 📥 **Export**: PDF, CSV, custom reports

**Architecture**:
```
streamlit_apps/
├── analytics_dashboard/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_overview.py        # Overview
│   │   ├── 02_cost_analysis.py   # Detailed cost analysis
│   │   ├── 03_model_comparison.py # Model comparison
│   │   ├── 04_agent_performance.py # Agent performance
│   │   └── 05_exports.py         # Report exports
│   ├── components/
│   │   ├── charts.py             # Chart components
│   │   ├── metrics.py            # Metrics widgets
│   │   └── filters.py            # Temporal/agent filters
│   └── queries/
│       └── analytics_queries.py  # SQLite/PostgreSQL queries
```

**Deliverables**:
- [ ] Multi-page Streamlit dashboard
- [ ] Connection to analytics database (SQLite/PostgreSQL)
- [ ] Interactive visualizations (Plotly/Altair)
- [ ] Dynamic filters (dates, agents, models)
- [ ] Report exports (PDF, CSV)
- [ ] Configuration and authentication
- [ ] User documentation

**Benefits**:
- ✅ Immediate visibility into LLM costs
- ✅ Quick identification of expensive agents
- ✅ Optimization based on real data
- ✅ Demonstration of framework ROI
- ✅ Accessible interface (non-technical users)

**Timeline**:
- Week 1: Setup + Main pages + Charts (8-12h)
- Week 2: Filters + Export + Tests + Documentation (6-10h)
- **Total**: 14-22h

---

### 🔴 **PRIORITY 3.5: Streamlit Error Monitoring Dashboard** ⚡ NEW

**Estimated Duration**: 3-5 days
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: Requires PRIORITY 1 (Analytics & Observability) completed
**Note**: Can be implemented by autonomous daemon (PRIORITY 2) once it's complete! 🤖

#### Project: Real-Time Error Dashboard from Langfuse Traces

**Objectives**:
- Visualize runtime execution errors from Langfuse traces stored in SQLite
- Real-time error monitoring and alerting
- Error trend analysis and categorization
- Root cause identification through trace inspection

**Key Features**:
- 🚨 **Error Overview**: Real-time error counts, severity distribution, error rate trends
- 📊 **Error Analysis**: Group errors by type, model, agent, and trace
- 🔍 **Trace Explorer**: Deep dive into failed traces with full context
- 📈 **Trend Analysis**: Error frequency over time, model failure rates
- 🎯 **Root Cause Detection**: Identify patterns in failed executions
- 🔔 **Alerts**: Configurable alerts for critical errors and error rate spikes
- 📥 **Export**: Error reports (CSV, JSON) for offline analysis

**Architecture**:
```
streamlit_apps/
├── error_monitoring_dashboard/
│   ├── app.py                      # Main Streamlit app
│   ├── pages/
│   │   ├── 01_error_overview.py    # Error metrics overview
│   │   ├── 02_trace_explorer.py    # Failed trace inspector
│   │   ├── 03_error_trends.py      # Temporal error analysis
│   │   ├── 04_model_failures.py    # Model-specific errors
│   │   └── 05_alerts_config.py     # Alert configuration
│   ├── components/
│   │   ├── error_cards.py          # Error summary cards
│   │   ├── error_charts.py         # Error visualization charts
│   │   ├── trace_viewer.py         # Trace detail viewer
│   │   └── alert_widget.py         # Alert notification widget
│   ├── queries/
│   │   ├── error_queries.py        # Error extraction from traces
│   │   └── trace_queries.py        # Trace detail queries
│   └── utils/
│       ├── error_classifier.py     # Error categorization logic
│       └── alert_manager.py        # Alert triggering logic
```

**Data Schema** (from Langfuse export):

The dashboard queries the `traces` and `events` tables in SQLite:

```python
# Example query structure
"""
SELECT
    traces.id,
    traces.name,
    traces.timestamp,
    traces.metadata,
    traces.status_message,  -- Error messages
    events.level,           -- 'ERROR', 'WARNING', etc.
    events.message,
    events.body,           -- Full error details
    generations.model,
    generations.model_parameters,
    generations.prompt_tokens,
    generations.completion_tokens,
    generations.total_cost
FROM traces
LEFT JOIN events ON traces.id = events.trace_id
LEFT JOIN generations ON traces.id = generations.trace_id
WHERE events.level IN ('ERROR', 'WARNING')
   OR traces.status_message IS NOT NULL
ORDER BY traces.timestamp DESC
"""
```

**Dashboard Pages**:

#### 1. **Error Overview** (`01_error_overview.py`)
```python
# Metrics displayed:
- Total errors (last 24h, 7d, 30d)
- Error rate (errors/total traces %)
- Top 5 error types
- Error severity distribution (Critical, High, Medium, Low)
- Recent errors list (last 10)

# Charts:
- Error timeline (hourly/daily)
- Errors by model (pie chart)
- Errors by agent (bar chart)
- Error severity heatmap
```

#### 2. **Trace Explorer** (`02_trace_explorer.py`)
```python
# Features:
- Search traces by ID, model, date range
- Filter by error type, severity, agent
- View full trace details:
  - Input prompt
  - Model response
  - Error message and stack trace
  - Execution metadata (tokens, cost, latency)
  - Related events in trace

# Interactive trace viewer:
{
  "trace_id": "trace-abc123",
  "timestamp": "2025-10-09T14:23:45Z",
  "name": "autonomous-implementation",
  "status": "ERROR",
  "error_message": "Rate limit exceeded for model gpt-4",
  "metadata": {
    "priority": "PRIORITY 2: Analytics",
    "branch": "feature/analytics-export"
  },
  "events": [
    {
      "level": "INFO",
      "message": "Starting task execution"
    },
    {
      "level": "ERROR",
      "message": "RateLimitError: Rate limit exceeded",
      "body": {
        "error_type": "RateLimitError",
        "model": "gpt-4",
        "retry_after": 60
      }
    }
  ],
  "generation": {
    "model": "gpt-4",
    "prompt_tokens": 1234,
    "completion_tokens": 0,
    "total_cost": 0.05
  }
}
```

#### 3. **Error Trends** (`03_error_trends.py`)
```python
# Visualizations:
- Error frequency over time (line chart)
- Error rate percentage (errors/total traces)
- Error type distribution trends
- Day-of-week error patterns
- Hour-of-day error patterns

# Filters:
- Date range selector
- Error type selector
- Model filter
- Agent filter
```

#### 4. **Model Failures** (`04_model_failures.py`)
```python
# Model-specific error analysis:
- Errors by model (GPT-4, Claude, Gemini)
- Model failure rate comparison
- Common errors per model
- Model-specific error trends

# Example insights:
"GPT-4: Rate limit errors increased 40% this week"
"Claude: Context length errors on 5% of requests"
"Gemini: 0 errors in last 7 days"
```

#### 5. **Alerts Configuration** (`05_alerts_config.py`)
```python
# Configurable alert rules:
alerts = {
    "high_error_rate": {
        "condition": "error_rate > 10%",
        "window": "1 hour",
        "action": "send_notification"
    },
    "critical_error": {
        "condition": "error_level == 'CRITICAL'",
        "action": "send_notification"
    },
    "model_degradation": {
        "condition": "model_error_rate > 15%",
        "window": "30 minutes",
        "action": "send_notification"
    }
}

# Notification channels:
- Terminal/CLI notification
- Desktop notification
- Webhook (Slack/Discord)
- Email (optional)
```

**Example Dashboard UI**:

```
╔══════════════════════════════════════════════════════════════╗
║                   Error Monitoring Dashboard                  ║
╠══════════════════════════════════════════════════════════════╣
║  Last 24 Hours                                               ║
║  ┌─────────────┬─────────────┬─────────────┬─────────────┐  ║
║  │ Total Errors│ Error Rate  │ Critical    │ Models Down │  ║
║  │     42      │    3.2%     │      5      │      0      │  ║
║  └─────────────┴─────────────┴─────────────┴─────────────┘  ║
║                                                               ║
║  Error Timeline (Last 24 Hours)                              ║
║  Errors                                                       ║
║    10│     ╭─╮                                               ║
║     8│     │ │   ╭─╮                                         ║
║     6│ ╭─╮ │ │   │ │                                         ║
║     4│ │ │ │ │ ╭─│ │─╮                                       ║
║     2│─│ │─│ │─│ │ │ │───────────                           ║
║     0└─┴─┴─┴─┴─┴─┴─┴─┴───────────────────────>Time          ║
║                                                               ║
║  Top 5 Error Types                                           ║
║  1. RateLimitError (GPT-4)           15 occurrences         ║
║  2. ContextLengthExceededError       12 occurrences         ║
║  3. APIConnectionError                8 occurrences         ║
║  4. InvalidRequestError               5 occurrences         ║
║  5. TimeoutError                      2 occurrences         ║
║                                                               ║
║  Recent Errors                                               ║
║  🔴 14:45 | RateLimitError | gpt-4 | trace-xyz123          ║
║  🟡 14:32 | ContextLength  | claude-3 | trace-abc456        ║
║  🔴 14:15 | APIConnection  | gpt-4 | trace-def789           ║
╚══════════════════════════════════════════════════════════════╝
```

**Error Classification Logic**:

```python
# error_classifier.py
class ErrorClassifier:
    """Categorizes errors from Langfuse traces"""

    ERROR_CATEGORIES = {
        "RateLimitError": {
            "severity": "HIGH",
            "category": "API Limits",
            "actionable": "Implement rate limiting or backoff strategy"
        },
        "ContextLengthExceededError": {
            "severity": "MEDIUM",
            "category": "Input Validation",
            "actionable": "Reduce prompt size or use truncation strategy"
        },
        "APIConnectionError": {
            "severity": "CRITICAL",
            "category": "Network",
            "actionable": "Check network connectivity and API status"
        },
        "InvalidRequestError": {
            "severity": "MEDIUM",
            "category": "Request Validation",
            "actionable": "Validate request parameters before sending"
        },
        "TimeoutError": {
            "severity": "HIGH",
            "category": "Performance",
            "actionable": "Increase timeout or optimize prompt complexity"
        }
    }

    @staticmethod
    def classify(error_message: str) -> dict:
        """Extract error type and severity from error message"""
        for error_type, metadata in ErrorClassifier.ERROR_CATEGORIES.items():
            if error_type in error_message:
                return {
                    "type": error_type,
                    "severity": metadata["severity"],
                    "category": metadata["category"],
                    "recommendation": metadata["actionable"]
                }
        return {
            "type": "UnknownError",
            "severity": "MEDIUM",
            "category": "Other",
            "recommendation": "Manual investigation required"
        }
```

**Deliverables**:
- [ ] Multi-page Streamlit error monitoring dashboard
- [ ] Connection to analytics SQLite database
- [ ] Error extraction queries from Langfuse traces
- [ ] Interactive error visualization (Plotly/Altair)
- [ ] Trace detail viewer with full context
- [ ] Error classification and categorization logic
- [ ] Alert configuration and notification system
- [ ] Real-time error metrics and trends
- [ ] Dynamic filters (date range, error type, model, severity)
- [ ] Error report exports (CSV, JSON)
- [ ] User documentation and setup guide

**Benefits**:
- ✅ **Real-time visibility**: Immediate awareness of runtime errors
- ✅ **Root cause analysis**: Full trace context for debugging
- ✅ **Proactive monitoring**: Alerts prevent issues from escalating
- ✅ **Pattern detection**: Identify recurring error types
- ✅ **Model comparison**: See which models are most reliable
- ✅ **Cost optimization**: Reduce wasted costs from failed requests
- ✅ **Quality improvement**: Data-driven error reduction
- ✅ **Accessible interface**: Non-technical users can monitor errors

**Integration with Langfuse Export**:

The dashboard reads directly from the SQLite database populated by the Langfuse exporter (PRIORITY 2):

```python
# Connection to analytics database
import sqlite3
from sqlalchemy import create_engine

# SQLite connection
db_path = "data/analytics/langfuse_traces.db"
engine = create_engine(f"sqlite:///{db_path}")

# Query for errors
query = """
SELECT
    t.id as trace_id,
    t.name,
    t.timestamp,
    t.status_message as error_message,
    e.level,
    e.message,
    e.body,
    g.model,
    g.total_cost,
    g.prompt_tokens,
    g.completion_tokens
FROM traces t
LEFT JOIN events e ON t.id = e.trace_id
LEFT JOIN generations g ON t.id = g.trace_id
WHERE (e.level = 'ERROR' OR t.status_message IS NOT NULL)
  AND t.timestamp >= datetime('now', '-24 hours')
ORDER BY t.timestamp DESC
"""

# Execute and display in Streamlit
import pandas as pd
errors_df = pd.read_sql(query, engine)
st.dataframe(errors_df)
```

**Timeline**:
- Day 1: Setup + Database connection + Error queries (4-6h)
- Day 2: Error overview page + Metrics cards + Charts (6-8h)
- Day 3: Trace explorer + Detail viewer (6-8h)
- Day 4: Error trends + Model failures pages (4-6h)
- Day 5: Alerts + Export + Documentation (4-6h)
- **Total**: 24-34h (3-5 days)

**Success Metrics**:
- ✅ Dashboard loads in < 2 seconds
- ✅ Displays errors from last 24h, 7d, 30d
- ✅ Error classification accuracy > 90%
- ✅ Trace detail viewer shows full error context
- ✅ Alerts trigger within 1 minute of error occurrence
- ✅ Export functionality works for CSV and JSON
- ✅ User can identify top error types and trends

---

### 🔴 **PRIORITY 4: Streamlit Agent Interaction UI** ⚡ NEW

**Estimated Duration**: 1-2 weeks (or autonomous implementation via daemon 🤖)
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: Requires PRIORITY 2 (Autonomous Development Daemon) completed
**Note**: Can be implemented autonomously by the daemon once PRIORITY 2 is complete! 🤖

#### Project: Streamlit Interface for Agent Interaction

**Objectives**:
- Graphical interface to interact with Coffee Maker agents
- Interactive chat with streaming responses
- Dynamic agent configuration (models, strategies)
- Conversation history and export
- Demo and testing of agent capabilities

**Key Features**:
- 💬 **Chat interface**: Fluid conversation with agents
- 🔄 **Streaming**: Real-time response display
- ⚙️ **Configuration**: Choice of model, temperature, strategies
- 📝 **History**: Save and reload conversations
- 🎯 **Predefined agents**: Templates for different use cases
- 📊 **Live metrics**: Tokens, cost, latency per request
- 🎨 **Multi-agents**: Support for multi-agent conversations

**Architecture**:
```
streamlit_apps/
├── agent_interface/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_chat.py            # Chat interface
│   │   ├── 02_agent_config.py    # Agent configuration
│   │   ├── 03_history.py         # Conversation history
│   │   └── 04_playground.py      # Testing & experimentation
│   ├── components/
│   │   ├── chat_interface.py     # Chat component
│   │   ├── agent_selector.py     # Agent selection
│   │   ├── model_config.py       # Model configuration
│   │   └── metrics_display.py    # Metrics display
│   ├── agents/
│   │   ├── agent_manager.py      # Agent instance management
│   │   └── agent_templates.py    # Predefined templates
│   └── storage/
│       └── conversation_storage.py # Conversation save
```

**Deliverables**:
- [ ] Chat interface with streaming
- [ ] Dynamic agent configuration
- [ ] Support for multiple agents (code reviewer, architect, etc.)
- [ ] Persistent conversation history
- [ ] Real-time metrics (tokens, cost, latency)
- [ ] Conversation exports (Markdown, JSON)
- [ ] Predefined agent templates
- [ ] User documentation

**Benefits**:
- ✅ Facilitates agent usage (non-developers)
- ✅ Interactive demo of framework capabilities
- ✅ Fast testing of prompts and configurations
- ✅ Modern and intuitive user experience
- ✅ Accelerates framework adoption
- ✅ Collects user feedback

**Timeline**:
- Week 1: Chat interface + Streaming + Config (10-14h)
- Week 2: History + Export + Templates + Tests (8-12h)
- **Total**: 18-26h

---

### 🔴 **PRIORITY 5: Professional Documentation**

**Estimated Duration**: 1-2 weeks
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planned
**Note**: Can be implemented by autonomous daemon (PRIORITY 2) once it's complete! 🤖

#### Project: pdoc Documentation Enhancement

**Objectives**:
- Complete and navigable API documentation
- Usage examples for each component
- Automatic documentation validation
- Automatic publication to GitHub Pages ✅ (already in place)

**Deliverables**:
- [ ] pdoc configuration (`.pdoc.yml`)
- [ ] Enriched `__init__.py` with complete docstrings
- [ ] Google Style docstrings for all public modules
- [ ] Usage examples in each class/function
- [ ] `__pdoc__` variables to hide/document attributes
- [ ] Validation script (`scripts/validate_docs.py`)

**Priority Modules**:
1. `auto_picker_llm_refactored.py` ✅ (already well documented, enrich)
2. `builder.py` ⚠️ (new, to be fully documented)
3. `strategies/fallback.py` ✅ (add concrete examples)
4. `llm.py`, `cost_calculator.py`, `scheduled_llm.py`

**Reference**: `docs/pdoc_improvement_plan.md`

**Timeline**:
- Phase 1: Configuration (1-2h)
- Phase 2: `__init__.py` files (2-3h)
- Phase 3: Priority modules (5-8h)
- Phase 4: Metadata (1-2h)
- Phase 5: Tests & validation (2-3h)
- **Total**: 11-18h

**Note**: GitHub Action already in place ✅, just need to enrich docstrings.

---

### 🟡 **PRIORITY 6: Innovative Projects** (choose based on interest)

**Estimated Duration**: 3-4 weeks **per project**
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Complete documentation created
**Dependency**: Recommended after Streamlit apps (Priorities 3 & 4)
**Note**: Can be implemented by autonomous daemon (PRIORITY 2) once it's complete! 🤖

Choose **1 project** to implement first, based on interest and needs:

---

#### Option A: **Multi-Model Code Review Agent** ⭐ TOP RECOMMENDATION

**Pitch**: Agent that reviews code with **multiple LLMs simultaneously**, each with different expertise (bugs, architecture, performance, security).

**Use Cases**:
- Automated code review before merge
- Multi-perspective analysis of file/PR
- Detection of recurring bug patterns
- Performance improvement suggestions

**Deliverables**:
```
coffee_maker/code_reviewer/
├── reviewer.py                 # MultiModelCodeReviewer
├── perspectives/
│   ├── bug_hunter.py           # GPT-4 for bugs
│   ├── architect_critic.py     # Claude for architecture
│   ├── performance_analyst.py  # Gemini for performance
│   └── security_auditor.py     # Security agent
├── report_generator.py         # HTML report generation
└── git_integration.py          # Git hooks
```

**Business Impact**:
- ⚡ Code review time reduction (30-50%)
- 🐛 Early bug detection (-40% bugs in prod)
- 📈 Code quality improvement
- 💰 Direct measurable ROI

**Reference**: `docs/projects/01_multi_model_code_review_agent.md`

**Timeline**: 3-4 weeks

---

#### Option B: **Self-Improving Prompt Lab**

**Pitch**: Automatic prompt optimization system with A/B testing, evolutionary algorithms, and continuous learning.

**Use Cases**:
- A/B testing of prompt variants
- Automatic optimization via genetic algorithm
- Performance tracking for each prompt
- Continuous improvement without manual intervention

**Deliverables**:
```
coffee_maker/prompt_lab/
├── lab.py                      # PromptLab orchestrator
├── experiments/
│   ├── ab_tester.py            # A/B testing
│   ├── genetic_optimizer.py   # Genetic algorithm
│   └── experiment_runner.py   # Experiment execution
├── mutators/
│   └── prompt_mutator.py      # Prompt mutations
└── reporting/
    └── experiment_report.py   # Experiment reports
```

**Business Impact**:
- 📈 Response quality improvement (+15-30%)
- 💰 Cost reduction (shorter, more efficient prompts)
- 🤖 Automatic continuous improvement
- 📊 Quantitative data for decisions

**Reference**: `docs/projects/02_self_improving_prompt_lab.md`

**Timeline**: 3-4 weeks

---

#### Option C: **Agent Ensemble Orchestrator**

**Pitch**: Meta-agent that coordinates multiple specialized agents (architect, coder, tester, reviewer) with collaboration patterns (sequential, parallel, debate).

**Use Cases**:
- Development of complex features
- Automatic review pipelines
- Multi-perspective analysis
- Problem solving by consensus

**Deliverables**:
```
coffee_maker/agent_ensemble/
├── orchestrator.py             # Meta-agent
├── agents/
│   ├── architect_agent.py      # Design
│   ├── coder_agent.py          # Implementation
│   ├── tester_agent.py         # Tests
│   └── reviewer_agent.py       # Review
├── patterns/
│   ├── sequential.py           # Pipeline
│   ├── parallel.py             # Fan-out/fan-in
│   └── debate.py               # Consensus
└── coordination/
    ├── task_decomposer.py      # Decomposition
    └── result_synthesizer.py   # Synthesis
```

**Business Impact**:
- 🚀 Complex task resolution (+40% productivity)
- 🤝 Optimal multi-model collaboration
- 🎯 Better quality through consensus
- 📊 Collaboration metrics

**Reference**: `docs/projects/03_agent_ensemble_orchestrator.md`

**Timeline**: 3-4 weeks

---

#### Option D: **Cost-Aware Smart Router**

**Pitch**: Intelligent router that dynamically chooses the best model for each request based on budget, latency, and quality constraints.

**Use Cases**:
- Automatic cost/quality optimization
- Real-time budget management
- Load balancing between providers
- Task pattern learning

**Deliverables**:
```
coffee_maker/smart_router/
├── router.py                   # SmartRouter
├── prediction/
│   ├── complexity_predictor.py # ML complexity prediction
│   └── cost_predictor.py       # Cost prediction
├── optimization/
│   ├── optimizer.py            # Optimal selection
│   └── budget_manager.py       # Budget management
└── learning/
    ├── pattern_learner.py      # Pattern learning
    └── model_ranker.py         # Model ranking
```

**Business Impact**:
- 💰 Cost reduction (-30-50%)
- ⚡ Latency/quality optimization
- 📊 Real-time budget enforcement
- 🎯 Direct measurable ROI

**Reference**: `docs/projects/04_cost_aware_smart_router.md`

**Timeline**: 3-4 weeks

---

#### Option E: **LLM Performance Profiler**

**Pitch**: Automated profiling tool that precisely measures LLM performance across different dimensions and generates detailed comparative reports.

**Use Cases**:
- Automated and reproducible benchmarking
- Model comparison (cost, latency, quality)
- Stress testing and context window testing
- Interactive HTML report generation

**Deliverables**:
```
coffee_maker/llm_profiler/
├── profiler.py                 # LLMProfiler
├── benchmarks/
│   ├── code_gen_benchmark.py   # Code generation
│   ├── summarization_benchmark.py
│   └── translation_benchmark.py
├── metrics/
│   ├── latency_meter.py        # Latency measurement
│   ├── quality_evaluator.py   # Quality evaluation
│   └── cost_calculator.py      # Cost calculation
└── reporting/
    ├── html_reporter.py        # HTML reports
    └── comparison_generator.py # Comparisons
```

**Business Impact**:
- 📊 Data-driven decisions
- 💰 Cost/quality optimization
- ⚡ Identification of fastest models
- 🎯 Reproducible benchmarks

**Reference**: `docs/projects/05_llm_performance_profiler.md`

**Timeline**: 3-4 weeks

---

### 🟡 **PRIORITY 7: Optional Final Refactoring** (if needed)

**Estimated Duration**: 1 week
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planned (optional)
**Dependency**: To be done **AFTER** all other priorities
**Note**: Can be implemented by autonomous daemon (PRIORITY 2) if needed! 🤖

Sprint 1 & 2 refactoring is **complete and functional**, but improvements are possible:

#### Phase 1.1: Additional Refactoring (optional)
- [ ] Extract additional ContextStrategy (if future truncation/summarization needed)
- [ ] Implement CostTrackingStrategy (if enforceable budgets needed)
- [ ] Implement MetricsStrategy (if Prometheus/Datadog needed)
- [ ] Implement TokenEstimatorStrategy (if improved precision needed)

**Reference**: `docs/refactoring_priorities_updated.md`

**Decision**: Current code is **already clean and functional**. Only implement if specific needs arise.

---

### 🔴 **PRIORITY 8: Multi-AI Provider Support** 🌍 **USER ADOPTION**

**Estimated Duration**: 2-3 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: Should be done after PRIORITY 3 (Autonomous Development Daemon) is stable
**Strategic Goal**: **Increase user adoption** by supporting multiple AI providers
**Note**: Can be implemented by autonomous daemon (PRIORITY 3) once it's complete! 🤖

#### Why This Is Critical

Currently, the `code-developer` daemon is tightly coupled to Claude via the Claude CLI. While Claude is excellent, **this creates barriers to adoption**:

1. **Cost Flexibility**: Users may want to use cheaper models for simple tasks
2. **Feature Availability**: Some users may not have access to Claude in their region
3. **Model Preferences**: Different developers prefer different AI tools
4. **Competitive Landscape**: By the time this is implemented, new models may emerge
5. **Risk Mitigation**: Dependency on a single provider creates business risk

**Business Impact**: Supporting OpenAI, Gemini, and emerging models can **significantly increase user adoption** and make the tool more accessible globally.

#### Project: AI Provider Abstraction Layer

**Goal**: Allow `code-developer` to work with multiple AI providers while maintaining the same high-quality autonomous development experience.

#### Supported Providers (Initial)

1. **Claude** (Anthropic) - Current, remains default ✅
   - Via Claude CLI or API
   - Best for complex reasoning and code generation

2. **OpenAI** (GPT-4, GPT-4 Turbo, o1, o3) 🆕
   - Via OpenAI API
   - Widest adoption, familiar to most developers

3. **Gemini** (Google) 🆕
   - Via Gemini API
   - Competitive pricing, strong code capabilities

4. **Future-Proof Design** 🔮
   - Pluggable architecture to easily add new providers
   - Monitor AI developer community for emerging popular models
   - Examples: DeepSeek, Mistral, Llama (via Ollama), etc.

#### Architecture

```
coffee_maker/ai_providers/
├── __init__.py
├── base.py                      # BaseAIProvider abstract class
├── claude_provider.py           # Claude implementation (current)
├── openai_provider.py           # OpenAI implementation
├── gemini_provider.py           # Google Gemini implementation
├── provider_factory.py          # Factory for provider selection
├── provider_config.py           # Configuration management
└── fallback_strategy.py         # Fallback/retry logic

# Example usage in daemon:
from coffee_maker.ai_providers import get_provider

# Get configured provider
provider = get_provider()  # Reads from config

# Execute code development task
response = provider.complete_task(
    prompt="Implement PRIORITY 5 from ROADMAP.md",
    context={"files": [...], "roadmap": "..."}
)
```

#### Core Features

##### 1. Provider Abstraction

```python
# base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def complete_task(
        self,
        prompt: str,
        context: Dict,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Execute a code development task."""
        pass

    @abstractmethod
    def stream_response(self, prompt: str, context: Dict):
        """Stream response for real-time feedback."""
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str, context: Dict) -> float:
        """Estimate cost for the request."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'claude', 'openai', 'gemini')."""
        pass

    @property
    @abstractmethod
    def supports_tools(self) -> bool:
        """Whether provider supports function calling/tools."""
        pass
```

##### 2. Configuration System

```yaml
# config/ai_providers.yaml
default_provider: claude

providers:
  claude:
    enabled: true
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-5-20250929
    use_cli: true  # Use Claude CLI instead of API
    max_tokens: 8000
    temperature: 0.7

  openai:
    enabled: true
    api_key_env: OPENAI_API_KEY
    model: gpt-4-turbo
    fallback_models:
      - gpt-4
      - gpt-3.5-turbo
    max_tokens: 8000
    temperature: 0.7

  gemini:
    enabled: true
    api_key_env: GOOGLE_API_KEY
    model: gemini-1.5-pro
    max_tokens: 8000
    temperature: 0.7

# Fallback strategy
fallback:
  enabled: true
  retry_attempts: 3
  fallback_order:
    - claude
    - openai
    - gemini

# Cost limits
cost_controls:
  daily_limit: 50.0  # USD
  per_task_limit: 5.0  # USD
  warn_threshold: 0.8  # Warn at 80% of limit
```

##### 3. Smart Fallback Strategy

```python
# fallback_strategy.py
class FallbackStrategy:
    """Handles provider failures and automatic fallback."""

    def execute_with_fallback(
        self,
        task: str,
        context: Dict,
        providers: List[str] = None
    ) -> str:
        """
        Try primary provider, fall back to alternatives if needed.

        Fallback triggers:
        - Rate limit errors
        - API unavailability
        - Cost limit exceeded
        - Model-specific errors
        """
        providers = providers or self.config.fallback_order
        errors = []

        for provider_name in providers:
            try:
                provider = get_provider(provider_name)

                # Check cost before executing
                estimated_cost = provider.estimate_cost(task, context)
                if not self.check_cost_limit(estimated_cost):
                    self.log(f"{provider_name}: Cost limit exceeded, trying next...")
                    continue

                # Execute task
                result = provider.complete_task(task, context)
                self.log(f"✅ Success with {provider_name}")
                return result

            except RateLimitError as e:
                errors.append(f"{provider_name}: Rate limited")
                self.log(f"⚠️  {provider_name} rate limited, trying next...")

            except ProviderUnavailable as e:
                errors.append(f"{provider_name}: Unavailable")
                self.log(f"❌ {provider_name} unavailable, trying next...")

        # All providers failed
        raise AllProvidersFailedError(
            f"All providers failed. Errors: {errors}"
        )
```

##### 4. Provider-Specific Implementations

**Claude Provider** (current, enhanced):
```python
# claude_provider.py
class ClaudeProvider(BaseAIProvider):
    """Claude implementation via CLI or API."""

    def __init__(self, use_cli: bool = True):
        self.use_cli = use_cli
        if use_cli:
            self.interface = ClaudeCLIInterface()
        else:
            self.client = anthropic.Anthropic()

    def complete_task(self, prompt: str, context: Dict, **kwargs) -> str:
        if self.use_cli:
            return self.interface.execute_with_context(prompt, context)
        else:
            # Use API directly
            message = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return message.content[0].text

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_tools(self) -> bool:
        return True  # Claude supports tool use
```

**OpenAI Provider**:
```python
# openai_provider.py
class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 implementation."""

    def __init__(self):
        self.client = openai.OpenAI()
        self.model = self.config.model

    def complete_task(self, prompt: str, context: Dict, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert software developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 8000)
        )
        return response.choices[0].message.content

    def estimate_cost(self, prompt: str, context: Dict) -> float:
        """Estimate cost based on OpenAI pricing."""
        # GPT-4 Turbo: $10/1M input tokens, $30/1M output tokens
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
        input_cost = (estimated_tokens / 1_000_000) * 10
        output_cost = (4000 / 1_000_000) * 30  # Assume 4K output
        return input_cost + output_cost

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supports_tools(self) -> bool:
        return True  # Supports function calling
```

**Gemini Provider**:
```python
# gemini_provider.py
class GeminiProvider(BaseAIProvider):
    """Google Gemini implementation."""

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(self.config.model)

    def complete_task(self, prompt: str, context: Dict, **kwargs) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config={
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 8000)
            }
        )
        return response.text

    def estimate_cost(self, prompt: str, context: Dict) -> float:
        """Estimate cost based on Gemini pricing."""
        # Gemini 1.5 Pro: $7/1M input tokens, $21/1M output tokens
        estimated_tokens = len(prompt.split()) * 1.3
        input_cost = (estimated_tokens / 1_000_000) * 7
        output_cost = (4000 / 1_000_000) * 21
        return input_cost + output_cost

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def supports_tools(self) -> bool:
        return True  # Gemini supports function calling
```

##### 5. Integration with Daemon

```python
# In coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import get_provider, FallbackStrategy

class CodeDeveloperDaemon:
    def __init__(self):
        # Use configured provider with fallback
        self.fallback_strategy = FallbackStrategy()
        self.provider = get_provider()  # Gets default from config

    def execute_priority(self, priority: str):
        """Execute a priority from the roadmap."""
        prompt = f"Read docs/ROADMAP.md and implement {priority}"

        try:
            # Try primary provider with automatic fallback
            result = self.fallback_strategy.execute_with_fallback(
                task=prompt,
                context=self.get_context()
            )

            # Log which provider succeeded
            self.log(f"Completed {priority} using {self.provider.name}")

        except AllProvidersFailedError as e:
            # Notify user if all providers fail
            self.notify_user(
                "⚠️ All AI providers failed",
                str(e),
                priority="high"
            )
```

#### User Experience

##### Setup Wizard
```bash
# First-time setup
$ project-manager init

? Select default AI provider:
  ▸ Claude (Anthropic) - Recommended for best code quality
    OpenAI (GPT-4) - Widely available
    Google Gemini - Cost-effective

? Enter your Anthropic API key (or press Enter to use Claude CLI):
✓ Claude configured successfully

? Would you like to configure fallback providers? (Y/n): y

? Select fallback providers (space to select):
  ▸ ☑ OpenAI
    ☑ Google Gemini

? Enter your OpenAI API key: sk-...
✓ OpenAI configured

? Enter your Google API key: AIza...
✓ Gemini configured

✓ Multi-provider setup complete!

Fallback order: Claude → OpenAI → Gemini
```

##### Runtime Provider Switching
```bash
# Check current provider
$ project-manager provider status
Current: claude (via CLI)
Fallback enabled: yes
Fallback order: claude → openai → gemini

# Switch provider temporarily
$ code-developer --provider openai

# Update default provider
$ project-manager config set default_provider openai

# View cost comparison
$ project-manager provider costs
┌──────────┬───────────┬────────────┬──────────┐
│ Provider │ Tasks Run │ Total Cost │ Avg Cost │
├──────────┼───────────┼────────────┼──────────┤
│ Claude   │ 45        │ $23.50     │ $0.52    │
│ OpenAI   │ 12        │ $8.20      │ $0.68    │
│ Gemini   │ 3         │ $1.80      │ $0.60    │
└──────────┴───────────┴────────────┴──────────┘
```

#### Implementation Steps

1. **Week 1: Abstraction Layer**
   - [ ] Design and implement `BaseAIProvider` interface
   - [ ] Refactor existing Claude integration to use provider pattern
   - [ ] Create provider factory and configuration system
   - [ ] Add provider selection logic to daemon

2. **Week 2: OpenAI & Gemini Integration**
   - [ ] Implement `OpenAIProvider`
   - [ ] Implement `GeminiProvider`
   - [ ] Add API key management and validation
   - [ ] Implement cost estimation for each provider
   - [ ] Add unit tests for each provider

3. **Week 2-3: Fallback & UX**
   - [ ] Implement `FallbackStrategy` with retry logic
   - [ ] Add cost tracking per provider
   - [ ] Create setup wizard for multi-provider configuration
   - [ ] Add provider status and switching commands
   - [ ] Update documentation with provider comparison

4. **Week 3: Testing & Polish**
   - [ ] Integration tests with all providers
   - [ ] Test fallback scenarios (rate limits, failures)
   - [ ] Performance comparison across providers
   - [ ] Cost analysis and optimization
   - [ ] User acceptance testing

#### Success Criteria

- ✅ User can configure any supported provider as default
- ✅ Automatic fallback works seamlessly when primary provider fails
- ✅ Cost tracking accurate for all providers
- ✅ Setup wizard makes configuration easy (<5 minutes)
- ✅ Provider switching takes <30 seconds
- ✅ All existing daemon features work with any provider
- ✅ Performance within 10% across providers for similar tasks
- ✅ Documentation includes provider comparison and recommendations

#### Provider Comparison Matrix

| Feature                  | Claude          | OpenAI (GPT-4)  | Gemini 1.5 Pro  |
|-------------------------|-----------------|-----------------|-----------------|
| Code Quality            | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐        | ⭐⭐⭐⭐        |
| Context Window          | 200K tokens     | 128K tokens     | 1M tokens       |
| Cost (per 1M tokens)    | $15/$75         | $10/$30         | $7/$21          |
| Tool/Function Support   | Excellent       | Good            | Good            |
| Availability            | Most regions    | Global          | Most regions    |
| CLI Integration         | ✅ Native       | ❌ API only     | ❌ API only     |
| Reasoning Quality       | Excellent       | Very Good       | Very Good       |
| **Recommended For**     | Complex tasks   | General use     | High volume     |

#### Future Enhancements (Post-PRIORITY 8)

- **Model Router**: Automatically select best provider based on task type
- **Hybrid Execution**: Use different providers for different subtasks
- **Local Models**: Support Ollama for offline/private development
- **Cost Optimizer**: Suggest cheaper provider for simple tasks
- **A/B Testing**: Compare output quality across providers
- **Custom Providers**: Plugin system for proprietary models

#### Strategic Impact

**User Adoption Benefits**:
1. ✅ **Removes Claude-only barrier** - Users can start with familiar tools (GPT-4)
2. ✅ **Cost flexibility** - Choose based on budget
3. ✅ **Geographic availability** - Work around regional restrictions
4. ✅ **Risk mitigation** - Not dependent on single provider
5. ✅ **Future-proof** - Easy to add emerging models as they gain popularity

**Marketing Angle**:
> "Use **your preferred AI** - whether it's Claude, GPT-4, Gemini, or the next big model. Our autonomous developer works with all major AI providers, with smart fallback to ensure you never get blocked."

---

## 📅 Recommended Timeline

### **Month 1: Foundation + Game-Changing Autonomous System** 🤖

#### Week 1-3: Analytics & Observability 🔴 PRIORITY 1
- SQLite database setup + Langfuse export
- Performance analytics
- Multi-process rate limiting
- **Deliverable**: Operational analytics system (foundation for daemon)

#### Week 4: Basic Autonomous Development Daemon 🔴 PRIORITY 2 ⚡ **GAME CHANGER** 🤖
- **Minimal, always-running** Python daemon
- Claude CLI integration (subprocess wrapper)
- Roadmap parser and task executor
- Basic Git automation (branches, commits, PRs)
- Simple progress tracking
- **Deliverable**: **Self-implementing AI system that never stops working**
- **Impact**: After this, Claude implements the rest of the roadmap autonomously! 🚀

---

### **Month 2: Streamlit User Interfaces** ⚡ (Implemented by Daemon 🤖)

#### Week 1-2: Analytics Dashboard 🔴 PRIORITY 3
- **Implemented by autonomous daemon** ✨
- Streamlit dashboard for LLM & cost visualization
- Connection to analytics database
- Interactive charts (Plotly/Altair)
- Report export (PDF, CSV)
- **Deliverable**: Operational analytics dashboard

#### Week 2-3: Error Monitoring Dashboard 🔴 PRIORITY 3.5
- **Implemented by autonomous daemon** ✨
- Real-time error monitoring from Langfuse traces
- Error classification and trend analysis
- Configurable alerts
- **Deliverable**: Error monitoring dashboard

#### Week 3-4: Agent Interaction UI 🔴 PRIORITY 4
- **Implemented by autonomous daemon** ✨
- Chat interface with agents via Claude CLI
- Real-time response streaming
- Dynamic agent configuration
- Conversation history and export
- **Deliverable**: Web interface to interact with agents

---

### **Month 3: Documentation & First Innovative Project** (Implemented by Daemon 🤖)

#### Week 1: Documentation 🔴 PRIORITY 5
- **Implemented by autonomous daemon** ✨
- pdoc enhancement
- Docstring validation
- **Deliverable**: Professional API documentation

#### Week 2-4: First Innovative Project (optional) 🔴 PRIORITY 6
- **Implemented by autonomous daemon** ✨

Choose **1 project** among the 5 options based on business priority:

**Recommended option**: **Multi-Model Code Review Agent** ⭐

- Core reviewer + Perspectives
- Report generation + Git integration
- Tests + Documentation

---

### **Month 4+: Expansion (based on needs)**

Possible choices:
- Implement a 2nd innovative project (Agent Ensemble, Prompt Lab, etc.)
- Improve Streamlit apps with user feedback
- Additional refactoring (ContextStrategy, MetricsStrategy)
- Advanced features based on feedback

---

## 🌳 Git Strategy and Versioning

**Objective**: Maintain a clean and traceable Git history throughout the roadmap.

### 📋 Branch Structure

```
main (main branch, always stable)
│
├── feature/analytics-export-langfuse        (Priority 2)
│   ├── feat/db-schema                       (subtask)
│   ├── feat/exporter-core                   (subtask)
│   └── feat/analytics-queries               (subtask)
│
├── feature/claude-cli-integration           (Priority 3) ⚡ NEW
│   ├── feat/cli-interface                   (subtask)
│   ├── feat/streaming-support               (subtask)
│   └── feat/config-management               (subtask)
│
├── feature/streamlit-analytics-dashboard    (Priority 4)
│   ├── feat/dashboard-overview-page         (subtask)
│   ├── feat/cost-analysis-page             (subtask)
│   └── feat/charts-components              (subtask)
│
├── feature/streamlit-agent-ui              (Priority 5)
│   ├── feat/chat-interface                 (subtask)
│   ├── feat/agent-config                   (subtask)
│   └── feat/conversation-history           (subtask)
│
└── feature/documentation-pdoc              (Priority 6)
```

### 🏷️ Semantic Versioning Convention

Follow [Semantic Versioning 2.0.0](https://semver.org/):

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR** (v1.0.0 → v2.0.0): Breaking changes incompatible with existing API
- **MINOR** (v1.0.0 → v1.1.0): New backward-compatible features
- **PATCH** (v1.0.0 → v1.0.1): Backward-compatible bug fixes

**Recommended tags for this roadmap**:

```bash
# Current state (refactoring completed)
v0.9.0  # Pre-release with complete refactoring

# After Priority 2: Analytics
v1.0.0  # First major release with analytics

# After Priority 3: Claude CLI Integration ⚡ NEW
v1.1.0  # Minor release - Claude CLI Python integration

# After Priority 4: Streamlit Analytics Dashboard
v1.2.0  # Minor release - analytics dashboard

# After Priority 5: Streamlit Agent UI
v1.3.0  # Minor release - agent interaction UI

# After Priority 6: Documentation
v1.3.1  # Patch release - documentation improvement

# After Priority 7: First innovative project
v1.4.0  # Minor release - major new feature
```

### 📝 Commit Message Convention

**Conventional Commits Format**:
```
<type>(<scope>): <short description>

[optional message body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Refactoring (no functional change)
- `docs`: Documentation only
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks (build, CI, etc.)
- `perf`: Performance improvement
- `style`: Formatting (no code change)

**Scopes** (examples):
- `analytics`, `exporter`, `dashboard`, `agent-ui`, `llm`, `fallback`, `tests`, etc.

**Examples**:
```bash
feat(analytics): implement SQLite exporter for Langfuse traces
fix(dashboard): correct cost calculation for multi-model queries
refactor(llm): simplify AutoPickerLLM initialization logic
docs(analytics): add usage examples to exporter module
test(dashboard): add integration tests for chart components
chore(ci): update GitHub Actions workflow for pdoc
```

### 🔄 Git Workflow per Project

#### Phase 1: Project Start
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/project-name

# First commit (initial structure)
git commit -m "chore(project): initialize [project name] structure"
```

#### Phase 2: Iterative Development
```bash
# Regular commits (at least daily)
# 1 commit = 1 feature or 1 coherent fix

git add [files related to a feature]
git commit -m "feat(scope): feature description"

# Regular push for backup
git push origin feature/project-name
```

#### Phase 3: Continuous Improvement (after each project)
```bash
# Separate refactoring commits
git commit -m "refactor(scope): simplify complex function X"
git commit -m "docs(scope): add docstrings to module Y"
git commit -m "test(scope): improve coverage to 85%"
git commit -m "chore(scope): remove dead code and unused imports"
```

#### Phase 4: Finalization and Merge
```bash
# Ensure all tests pass
pytest

# Merge into main
git checkout main
git pull origin main
git merge feature/project-name

# Create version tag
git tag -a v1.x.0 -m "Release: [Project name] completed"

# Push main and tags
git push origin main --tags

# Optional: delete feature branch (if merged)
git branch -d feature/project-name
git push origin --delete feature/project-name
```

### 📊 CHANGELOG.md

Maintain an up-to-date `CHANGELOG.md` file at project root:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [Work in progress items]

## [1.2.0] - 2025-XX-XX

### Added
- Streamlit Agent Interaction UI with chat interface
- Real-time streaming support for agent responses
- Conversation history and export functionality

### Changed
- Improved analytics dashboard performance
- Updated documentation with new examples

### Fixed
- Fixed rate limiting issue in multi-process scenarios

## [1.1.0] - 2025-XX-XX

### Added
- Streamlit Analytics Dashboard for LLM cost visualization
- Interactive charts for model comparison
- PDF/CSV export functionality

## [1.0.0] - 2025-XX-XX

### Added
- Analytics & Observability: Langfuse to SQLite/PostgreSQL export
- Rate limiting shared across multiple processes
- Performance analytics for LLMs, prompts, and agents

### Changed
- Refactored AutoPickerLLM (780 → 350 lines, -55%)
- Extracted FallbackStrategy with 3 implementations
- Implemented Builder Pattern (LLMBuilder + SmartLLM)

## [0.9.0] - 2025-10-08

### Changed
- Complete refactoring of core architecture (Sprint 1 & 2)
- 100% backward compatible migration
```

### 🎯 Git Best Practices

1. **Atomic commits**: 1 commit = 1 logical change
2. **Descriptive messages**: Explain the "why", not the "what"
3. **Daily push**: Backup and visibility on progress
4. **Short branches**: Merge regularly (< 1 week of work)
5. **Tags on milestones**: Facilitates rollback and tracking
6. **Up-to-date CHANGELOG**: Document changes for users
7. **Review before merge**: Verify tests pass and code is clean

### 🚨 What to Avoid

- ❌ Too large commits (> 500 lines modified)
- ❌ Vague messages ("fix bug", "update code")
- ❌ Direct commits on main (always use a branch)
- ❌ Forgetting to push (risk of work loss)
- ❌ Merging untested code
- ❌ Keeping feature branches open too long

---

## 📦 Technology Selection Guidelines

**Principle**: Before implementing any new project, carefully evaluate the technology stack to ensure faster, shorter, and more reliable implementation.

### 🎯 Core Philosophy

**Prioritize well-known, massively-used, open-source projects** that:
- Have large, active communities
- Are battle-tested in production
- Have extensive documentation and examples
- Are actively maintained
- Have stable APIs

### 📋 Pre-Implementation Checklist

Before starting any new priority, **MANDATORY** analysis:

#### 1. **Evaluate Current Stack** (30min-1h)
- [ ] Review existing dependencies in `requirements.txt` / `pyproject.toml`
- [ ] Identify which existing libraries can be reused
- [ ] Check if current stack already provides the needed functionality
- [ ] Avoid adding new dependencies if existing ones can solve the problem

#### 2. **Research Best Practices** (1-2h)
- [ ] Search for industry-standard solutions for the problem domain
- [ ] Consult GitHub trending, PyPI stats, and community recommendations
- [ ] Read recent blog posts and tutorials (last 1-2 years)
- [ ] Check StackOverflow for common patterns and gotchas

#### 3. **Dependency Evaluation Criteria**

For each potential new dependency, evaluate:

| Criterion | Threshold | Why It Matters |
|-----------|-----------|----------------|
| **GitHub Stars** | > 5,000 | Community adoption indicator |
| **Weekly Downloads** | > 100,000 (PyPI) | Production usage indicator |
| **Last Commit** | < 6 months | Active maintenance |
| **Open Issues** | < 500 unresolved | Maintainer responsiveness |
| **Documentation** | Comprehensive + examples | Ease of implementation |
| **License** | MIT, Apache 2.0, BSD | Commercial-friendly |
| **Python Version** | Supports 3.10+ | Modern compatibility |
| **Dependencies** | Minimal transitive deps | Reduced complexity |

#### 4. **Preferred Technologies by Domain**

**Web Frameworks & APIs**:
- ✅ **FastAPI** (REST APIs, async)
- ✅ **Streamlit** (data dashboards, simple UIs)
- ✅ **Flask** (lightweight services)
- ❌ Django (too heavy for this project)

**Database & ORM**:
- ✅ **SQLAlchemy** (ORM, already in use)
- ✅ **SQLite** (default, zero config)
- ✅ **PostgreSQL** (production, high volume)
- ✅ **Alembic** (migrations)

**Data Visualization**:
- ✅ **Plotly** (interactive charts)
- ✅ **Altair** (declarative charts)
- ✅ **Matplotlib** (static charts, if needed)

**CLI & Subprocess**:
- ✅ **subprocess** (built-in, reliable)
- ✅ **click** (CLI creation)
- ✅ **rich** (terminal formatting)

**Testing**:
- ✅ **pytest** (already in use)
- ✅ **pytest-cov** (coverage)
- ✅ **pytest-asyncio** (async tests)

**Code Quality**:
- ✅ **black** (formatting)
- ✅ **isort** (import sorting)
- ✅ **mypy** (type checking)
- ✅ **pylint** (linting)
- ✅ **radon** (complexity analysis)

**Async & Concurrency**:
- ✅ **asyncio** (built-in)
- ✅ **aiofiles** (async file I/O)
- ✅ **httpx** (async HTTP client)

**Git Automation**:
- ✅ **GitPython** (Git operations)
- ✅ **gh** CLI (GitHub automation via subprocess)

**LLM Integration** (already in use):
- ✅ **langchain** (LLM orchestration)
- ✅ **openai** (OpenAI API)
- ✅ **anthropic** (Claude API)
- ✅ **google-generativeai** (Gemini API)
- ✅ **langfuse** (observability)

### 🚫 What to Avoid

- ❌ **Niche libraries** with < 1,000 stars
- ❌ **Abandoned projects** (no commits in 12+ months)
- ❌ **One-person projects** without backup maintainers
- ❌ **Alpha/Beta software** for production features
- ❌ **Reinventing the wheel** when standard solutions exist
- ❌ **Framework lock-in** (prefer composable libraries)
- ❌ **Excessive dependencies** (each adds maintenance burden)

### 📝 Technology Decision Document

For **each new priority**, create a brief tech analysis in `docs/tech_decisions/`:

```markdown
# Technology Decision: [Priority Name]

**Date**: YYYY-MM-DD
**Decision Maker**: Claude / User

## Problem Statement
Brief description of what needs to be implemented.

## Technology Options Evaluated

### Option 1: [Library Name]
- **GitHub Stars**: X
- **Weekly Downloads**: Y
- **Pros**: ...
- **Cons**: ...
- **Verdict**: ✅ Recommended / ❌ Rejected

### Option 2: [Alternative]
...

## Final Decision

**Selected**: [Library Name]

**Justification**:
- Industry standard for this use case
- Used by [examples: Streamlit, FastAPI, etc.]
- Excellent documentation with examples
- Active community support

**Implementation Plan**:
1. Install: `pip install [library]`
2. Configuration: ...
3. Integration points: ...
```

### ✅ Benefits

- 🚀 **Faster implementation**: Leverage battle-tested libraries
- 📚 **Better documentation**: Popular libraries have extensive guides
- 🐛 **Fewer bugs**: Community has already found and fixed common issues
- 🔒 **Security**: Well-maintained projects patch vulnerabilities quickly
- 💡 **Best practices**: Learn from production-proven patterns
- 🤝 **Community support**: Easy to find help on StackOverflow/GitHub

### 🤖 For Autonomous Daemon

The autonomous development daemon (Priority 3) **MUST**:
1. Read this section before implementing any priority
2. Create a technology decision document in `docs/tech_decisions/`
3. Justify each new dependency with evaluation criteria
4. Prefer existing dependencies over new ones
5. Update this section if new standard technologies emerge

---

## 🔄 Continuous Improvement Practice (Between Each Project)

**Principle**: After each completed project, take time to improve existing code before starting the next one.

### 📋 Continuous Improvement Checklist

To do **systematically** between each project:

#### 0. **Technology Stack Review** (30min-1h) ⚡ NEW
- [ ] Review dependencies added during the project
- [ ] Verify all new dependencies meet the criteria in "Technology Selection Guidelines"
- [ ] Document technology decisions in `docs/tech_decisions/`
- [ ] Check for unused dependencies and remove them
- [ ] Update dependency versions to latest stable releases (if safe)
- [ ] Ensure all dependencies are properly documented in requirements

**Reference**: See **Technology Selection Guidelines** section above

#### 1. **Refactoring Analysis** (2-4h)
- [ ] Identify refactoring opportunities in recently written code
- [ ] Look for code duplications (DRY violations)
- [ ] Detect functions/classes that are too long or complex
- [ ] Spot circular dependencies or tight couplings
- [ ] Verify consistency of patterns used

**Tools**:
```bash
# Complexity analysis
radon cc coffee_maker/ -a -nb

# Duplication detection
pylint coffee_maker/ --disable=all --enable=duplicate-code

# Static analysis
mypy coffee_maker/
```

**Best Practice - Parallel Claude Instance for Deep Refactoring** ⚡ NEW:

For major refactoring work, consider using a **parallel Claude instance** dedicated to simplification:

```
User Workflow:
1. Main Claude instance: Works on feature implementation
2. Parallel Claude instance: Simultaneously simplifies and removes redundancies
3. Coordination: Merge simplification work before starting next priority

Benefits:
- ✅ Continuous code quality improvement
- ✅ No interruption to feature development
- ✅ Deeper analysis and more thorough refactoring
- ✅ Fresh perspective on code organization
- ✅ Parallel work = faster overall progress

Example:
- Instance A (this conversation): Planning PRIORITY 2 (Autonomous Daemon)
- Instance B (parallel): Simplifying codebase, removing redundancies
- Result: Clean foundation ready for autonomous daemon to work with
```

**Real-World Example: Sprint 1 Improvements** ⚡ ACTUAL WORK DONE:

Sprint 1 (completed 2025-01-09) demonstrates the type of refactoring opportunities to look for:

**1. Replace Manual Retry Logic with Centralized Utilities**:
```python
# BEFORE (18 lines, repeated pattern):
def set_api_limits(providers_fallback):
    def _run_with_api_limits(self, **kwargs):
        attempt = 0
        while attempt < 3:
            try:
                return self.invoke(**kwargs)
            except openai.error.RateLimitError as e:
                print("Rate limit reached, waiting before retrying...")
                time.sleep(2**attempt)  # exponential backoff
                attempt += 1
        return providers_fallback("openai", self, **kwargs)

# AFTER (cleaner, observable, 21 lines but better structure):
@with_retry(
    max_attempts=3,
    backoff_base=2.0,
    retriable_exceptions=(openai.error.RateLimitError,),
)
def _invoke_with_retry():
    return self.invoke(**kwargs)

try:
    return _invoke_with_retry()
except RetryExhausted as e:
    logger.warning(f"Rate limit retry exhausted: {e.original_error}")
    return providers_fallback("openai", self, **kwargs)
```

**Benefits**: Langfuse observability, proper logging, type safety, consistent with codebase

**2. Extract Duplicate Code to Reusable Utilities**:
```python
# BEFORE (9 lines repeated 3x = 27 lines total across cost_calculator.py):
now = time.time()
if timeframe == "day":
    threshold = now - 86400  # 24 hours
elif timeframe == "hour":
    threshold = now - 3600  # 1 hour
elif timeframe == "minute":
    threshold = now - 60  # 1 minute
else:  # "all"
    threshold = 0

# AFTER (1 line, reusable utility in time_utils.py):
threshold = get_timestamp_threshold(timeframe)

# New utility function:
def get_timestamp_threshold(
    timeframe: str,
    reference_time: Optional[float] = None,
) -> float:
    """Get Unix timestamp threshold for a timeframe.

    Args:
        timeframe: One of "minute", "hour", "day", or "all"
        reference_time: Reference Unix timestamp (default: current time)

    Returns:
        Unix timestamp threshold

    Raises:
        ValueError: If timeframe is invalid
    """
    # Implementation...
```

**Savings**: 27 lines → 3 lines (24 lines eliminated)

**3. Add Retry Protection to Flaky Database Operations**:
```python
# BEFORE (no retry protection, vulnerable to deadlocks/timeouts):
def get_llm_performance(self, days: int = 7, model: Optional[str] = None) -> Dict:
    """Get LLM performance metrics."""
    # Database query...

# AFTER (retry + observability):
@observe
@with_retry(
    max_attempts=3,
    backoff_base=1.5,
    retriable_exceptions=(OperationalError, TimeoutError),
)
def get_llm_performance(self, days: int = 7, model: Optional[str] = None) -> Dict:
    """Get LLM performance metrics."""
    # Same query, now resilient to transient failures
```

**Impact**: Added to 7 database query methods in analytics/analyzer.py
- Handles database deadlocks automatically
- Handles connection pool exhaustion
- All operations tracked in Langfuse

**4. Delete Deprecated Code**:
```python
# DELETED FILES (800 lines removed):
- coffee_maker/langchain_observe/_deprecated/auto_picker_llm.py (739 lines)
- coffee_maker/langchain_observe/_deprecated/create_auto_picker.py (61 lines)
- coffee_maker/langchain_observe/_deprecated/ (entire directory)
```

**Rationale**: Keeping deprecated code causes confusion and maintenance burden

**Sprint 1 Metrics**:
- ✅ **800+ lines removed** (deprecated code + duplication)
- ✅ **27 lines of duplication eliminated**
- ✅ **11 critical methods** now observable in Langfuse
- ✅ **10+ flaky operations** now have retry protection
- ✅ **15+ new type annotations** added
- ✅ **112 tests passing** (no regressions)

**Key Refactoring Opportunities to Look For**:
1. **Manual retry loops** → Replace with `@with_retry` decorator
2. **Duplicate calculations** → Extract to reusable utility functions
3. **Missing observability** → Add `@observe` decorator to critical methods
4. **Flaky database operations** → Add retry protection with proper exceptions
5. **Print statements** → Replace with proper logging (`logger.warning()`, etc.)
6. **Missing type hints** → Add type annotations for better IDE support
7. **Deprecated/dead code** → Delete unused files and functions
8. **Hard-coded values** → Extract to named constants
9. **Complex conditions** → Simplify with early returns and guard clauses
10. **Long functions** → Split into smaller, focused functions

**Documentation**: See `docs/sprint1_improvements_summary.md` for complete Sprint 1 report

#### 2. **Complexity Reduction** (1-3h)
- [ ] Extract long methods into smaller functions
- [ ] Simplify complex conditions (early returns, guard clauses)
- [ ] Reduce cyclomatic complexity (< 10 per function)
- [ ] Replace magic numbers with named constants
- [ ] Improve readability (variable names, structure)

**Quality Criteria**:
- Cyclomatic complexity < 10
- Function length < 50 lines
- Class length < 300 lines
- Indentation depth < 4 levels

#### 3. **Documentation** (1-2h)
- [ ] Add/complete missing docstrings
- [ ] Enrich usage examples
- [ ] Update README if necessary
- [ ] Document architecture decisions (ADR if relevant)
- [ ] Verify type hints are present and correct

**Validation Script**:
```bash
python scripts/validate_docs.py  # Create if doesn't exist
```

#### 4. **Tests and Coverage** (1-2h)
- [ ] Verify test coverage (target: > 80%)
- [ ] Add tests for missing edge cases
- [ ] Refactor duplicated tests
- [ ] Verify tests are readable and maintainable

**Commands**:
```bash
pytest --cov=coffee_maker --cov-report=html
coverage report --fail-under=80
```

#### 5. **Performance and Optimization** (1-2h - if relevant)
- [ ] Identify potential bottlenecks
- [ ] Check for unnecessary imports
- [ ] Optimize DB queries if applicable
- [ ] Check memory usage for high volumes

#### 6. **Cleanup** (30min-1h)
- [ ] Remove dead code (unused functions/classes)
- [ ] Clean unused imports
- [ ] Remove obsolete comments
- [ ] Format code (black, isort)
- [ ] Check TODOs and handle or document them

**Commands**:
```bash
# Automatic cleanup
black coffee_maker/
isort coffee_maker/
autoflake --remove-all-unused-imports --in-place --recursive coffee_maker/
```

#### 7. **Git Management and Versioning** (30min-1h)
- [ ] Create atomic and well-named commits
- [ ] Use feature branches for each subtask
- [ ] Make regular commits (at least daily)
- [ ] Write descriptive commit messages
- [ ] Create tags for important milestones

**Git Best Practices**:
```bash
# Branch naming convention
feature/analytics-exporter
feature/streamlit-dashboard
fix/rate-limiting-bug
refactor/simplify-fallback-strategy

# Commit message convention
# Format: <type>(<scope>): <description>
# Types: feat, fix, refactor, docs, test, chore, perf

git commit -m "feat(analytics): add Langfuse to SQLite exporter"
git commit -m "refactor(llm): reduce complexity of AutoPickerLLM"
git commit -m "docs(analytics): add usage examples to exporter"
git commit -m "test(analytics): add integration tests for exporter"

# Tags for milestones
git tag -a v1.0.0-analytics -m "Analytics & Observability completed"
git tag -a v1.1.0-streamlit-dashboard -m "Streamlit Analytics Dashboard completed"
```

**Recommended Git Workflow**:
1. **Project start**: Create feature branch
   ```bash
   git checkout -b feature/project-name
   ```

2. **During development**: Regular commits
   ```bash
   # Atomic commits per feature
   git add coffee_maker/analytics/exporter.py
   git commit -m "feat(analytics): implement basic exporter structure"

   git add tests/test_exporter.py
   git commit -m "test(analytics): add unit tests for exporter"
   ```

3. **End of subtask**: Push and potential PR (if team work)
   ```bash
   git push origin feature/project-name
   ```

4. **Continuous improvement**: Separate refactoring commits
   ```bash
   git commit -m "refactor(analytics): simplify exporter error handling"
   git commit -m "docs(analytics): add docstrings to exporter methods"
   git commit -m "test(analytics): improve test coverage to 85%"
   ```

5. **Project end**: Merge into main and tag
   ```bash
   git checkout main
   git merge feature/project-name
   git tag -a v1.x.0-project-name -m "Project completed description"
   git push origin main --tags
   ```

**Git Checklist Before Finalizing a Project**:
- [ ] All modified files are committed
- [ ] Commit messages are clear and descriptive
- [ ] Commits are atomic (1 commit = 1 feature/fix)
- [ ] Feature branch is merged into main
- [ ] Version tag is created
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Tests pass on main branch after merge

### 📊 Improvement Documentation

Create tracking document in `docs/improvements/`:
- `improvement_after_analytics.md`
- `improvement_after_streamlit_dashboard.md`
- `improvement_after_agent_ui.md`
- etc.

**Document Template**:
```markdown
# Improvements after [Project Name]

**Date**: YYYY-MM-DD
**Time spent**: Xh

## Refactorings performed
- [List of refactorings with affected files]

## Complexity reduced
- Before: [metrics]
- After: [metrics]

## Documentation added
- [List of documented modules]

## Tests added
- Coverage before: X%
- Coverage after: Y%

## Code removed
- X lines of dead code removed
- Y unused imports cleaned

## Impact
- Maintenance: [maintainability improvement]
- Performance: [performance gains if applicable]
- Readability: [readability improvement]
```

### ⏱️ Estimated Time per Continuous Improvement Session

| Task | Simple Project | Medium Project | Complex Project |
|------|----------------|----------------|-----------------|
| 0. Technology Stack Review | 30min | 30min-1h | 1h |
| 1. Refactoring Analysis | 2h | 2-3h | 3-4h |
| 1b. Parallel Claude for Deep Refactoring (optional) ⚡ NEW | 0h (parallel) | 0h (parallel) | 0h (parallel) |
| 2. Complexity Reduction | 1h | 1-2h | 2-3h |
| 3. Documentation | 1h | 1-2h | 1-2h |
| 4. Tests and Coverage | 1h | 1-2h | 2h |
| 5. Performance | 0-1h | 1h | 1-2h |
| 6. Cleanup | 30min | 30min-1h | 1h |
| 7. Git Management | 30min | 30min-1h | 1h |
| **TOTAL** | **7-8h** | **8-11h** | **12-16h** |

**Note**: Using a parallel Claude instance for refactoring (1b) adds **0 extra time** since it runs concurrently with your other work!

**Examples**:
- **Streamlit apps**: ~7-8h continuous improvement
- **Analytics**: ~8-11h continuous improvement
- **Innovative projects**: ~12-16h continuous improvement
- **With parallel Claude refactoring**: Same time + higher quality code! ✨

### 🎯 Benefits

- ✅ **Controlled technical debt**: Avoids debt accumulation
- ✅ **Consistent quality**: Maintains high quality level
- ✅ **Maintainability**: Code easier to modify and extend
- ✅ **Learning**: Fast feedback on patterns to improve
- ✅ **Momentum**: Natural transition between projects

### 🚨 Important

This practice is **non-negotiable** and is an integral part of each project. Continuous improvement time must be **included** in each project estimate.

**New estimate per project**:
- Initial project: X weeks
- Continuous improvement: +0.5-1 week
- **Realistic total**: X + 0.5-1 weeks

---

## 🎯 Success Metrics

### Analytics & Observability (Priority 1) ✅ MOSTLY COMPLETE
- ✅ Automatic Langfuse → SQLite export functional
- ✅ Usable SQL analysis queries
- ✅ Reliable multi-process rate limiting
- ✅ 0 duplicates in exports
- ✅ Native sqlite3 implementation (SQLAlchemy removed)

### Roadmap Management CLI (Priority 2) ⚡ NEW 🎯 80% COMPLETE
- ✅ NotificationDB with SQLite + WAL mode
- ✅ Multi-process safe with retry logic (@with_retry decorator)
- ✅ `project-manager` CLI with basic commands (view, notifications, respond, status, sync)
- ✅ Notification system for daemon ↔ user communication
- ✅ Support for questions, info, warnings, errors, completions
- ✅ Unit tests: 11/11 passing
- ⏳ Claude AI integration for interactive roadmap chat (Phase 2)

### Basic Autonomous Development Daemon (Priority 3) ⚡ NEW 🤖 90% COMPLETE
- ✅ ClaudeCLIInterface with subprocess wrapper functional
- ✅ RoadmapParser successfully extracts tasks from ROADMAP.md (regex-based)
- ✅ GitManager handles branches, commits, pushes, PRs via gh CLI
- ✅ DevDaemon orchestrates full autonomous workflow
- ✅ Notification system for user approval and completion notices
- ✅ Integration tests: 16/16 passing
- ✅ Comprehensive documentation and usage guide complete (DAEMON_USAGE.md)
- ✅ **Critical fixes applied**: Session detection, non-interactive CLI execution, branch handling
- ✅ **Session conflict prevention**: Runtime detection of Claude Code environment
- ✅ **Claude CLI non-interactive mode**: Using `claude -p` flag for programmatic execution
- ⏳ End-to-end testing with real Claude CLI (final 10%)

### Streamlit Analytics Dashboard (Priority 4)
- ✅ Dashboard accessible via browser
- ✅ Functional cost and trend charts
- ✅ Operational dynamic filters (dates, agents, models)
- ✅ PDF/CSV report export
- ✅ Loading time < 3 seconds

### Streamlit Error Monitoring Dashboard (Priority 3.5)
- ✅ Real-time error monitoring from Langfuse traces
- ✅ Error classification accuracy > 90%
- ✅ Trace detail viewer with full context
- ✅ Configurable alerts trigger within 1 minute
- ✅ Dashboard loads in < 2 seconds

### Streamlit Agent Interaction UI (Priority 4)
- ✅ Responsive chat interface with streaming
- ✅ Functional agent configuration using Claude CLI
- ✅ Persistent conversation history
- ✅ Support for multiple simultaneous agents
- ✅ Real-time metrics displayed

### Documentation (Priority 5)
- ✅ 100% of public functions documented
- ✅ Automatic validation (CI/CD)
- ✅ Usage examples for each module
- ✅ GitHub Pages updated

### Innovative Projects (Priority 6) (example: Code Review Agent)
- ✅ Multi-model review functional
- ✅ HTML reports generated
- ✅ Git hooks integration
- ✅ Review time reduction measured (-30%)

---

## 🚫 Anti-Priorities (to avoid for now)

- ❌ **Complete rewrite** - Sprint 1 & 2 refactoring is sufficient
- ❌ **Premature optimizations** - Focus on business features
- ❌ **Support for all LLM providers** - Stick to current 3 (OpenAI, Gemini, Anthropic)
- ❌ **Complex UI/Frontend** - Streamlit is sufficient, no need for React/Vue.js for now

---

## 🔄 Flexibility and Adaptation

This roadmap is **flexible** and can be adjusted based on:
- User feedback
- Business priorities
- New technological opportunities
- Time/resource constraints

**Recommended review**: Every month, re-evaluate priorities.

---

## 📚 Associated Documentation

### Completed Projects
- `docs/refactoring_complete_summary.md` - Complete refactoring summary
- `docs/sprint1_refactoring_summary.md` - Sprint 1 detailed
- `docs/sprint2_refactoring_summary.md` - Sprint 2 detailed
- `docs/migration_to_refactored_autopicker.md` - Migration guide

### Planned Projects
- `docs/langfuse_to_postgresql_export_plan.md` - Analytics & Export
- `docs/pdoc_improvement_plan.md` - Documentation
- `docs/projects/01_multi_model_code_review_agent.md` - Code Review Agent
- `docs/projects/02_self_improving_prompt_lab.md` - Prompt Lab
- `docs/projects/03_agent_ensemble_orchestrator.md` - Agent Ensemble
- `docs/projects/04_cost_aware_smart_router.md` - Smart Router
- `docs/projects/05_llm_performance_profiler.md` - Performance Profiler

### Architecture & Planning
- `docs/refactoring_priorities_updated.md` - Additional refactoring (optional)
- `docs/feature_ideas_analysis.md` - Analysis of 5 innovative projects

---

## ✅ Recommended Decision

**To start immediately**:

### **The New Paradigm: Build the Self-Building System First** 🤖

1. ✅ **Week 1-3** (Month 1): Implement **Analytics & Langfuse Export** 🔴 PRIORITY 1
   - **Why first**: Foundation for daemon to track its own work
   - Immediate business impact (ROI measurement)
   - Critical multi-process rate limiting
   - **Timeline**: 2-3 weeks

2. ✅ **Week 4** (Month 1): **Basic Autonomous Development Daemon** 🔴 PRIORITY 2 ⚡ **GAME CHANGER** 🤖
   - **Revolutionary**: Self-implementing AI system that NEVER stops
   - **Minimal and focused**: Just enough to autonomously implement features
   - Claude reads ROADMAP.md and implements priorities continuously
   - Automatic branch creation, commits, PRs, progress tracking
   - **Timeline**: 3-5 days (~20-30h)
   - **Impact**: After this, **YOU ONLY PLAN - CLAUDE BUILDS EVERYTHING** 🚀

### **After PRIORITY 2: You Stop Coding** ✨

3. 🤖 **Week 1-2** (Month 2): **Streamlit Analytics Dashboard** 🔴 PRIORITY 3
   - **Implemented by autonomous daemon** ✨
   - You update ROADMAP.md with requirements
   - Daemon reads it and implements autonomously
   - **You just review the PR!**

4. 🤖 **Week 2-3** (Month 2): **Error Monitoring Dashboard** 🔴 PRIORITY 3.5
   - **Implemented by autonomous daemon** ✨
   - Real-time error monitoring from Langfuse traces

5. 🤖 **Week 3-4** (Month 2): **Streamlit Agent Interaction UI** 🔴 PRIORITY 4
   - **Implemented by autonomous daemon** ✨
   - Chat interface with streaming responses

6. 🤖 **Week 1** (Month 3): **Professional Documentation** 🔴 PRIORITY 5
   - **Implemented by autonomous daemon** ✨
   - pdoc enhancement, docstrings, validation

7. 🤖 **Week 2-4** (Month 3): **First Innovative Project** 🔴 PRIORITY 6 (optional)
   - **Implemented by autonomous daemon** ✨
   - Recommendation: **Multi-Model Code Review Agent**

8. 🤖 **When needed**: **Optional Refactoring** 🔴 PRIORITY 7 (optional)
   - **Implemented by autonomous daemon if needed** ✨

**Revolutionary Impact**: After PRIORITY 2, your role shifts from **coder** to **architect** - you plan features in the roadmap, and Claude implements them autonomously while you do other work! 🎯

---

**Ready to start? Which project do you want to begin with?** 🚀
