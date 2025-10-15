# Coffee Maker Agent - Roadmap Overview

**Last Updated**: 2025-10-10
**Version**: 0.1.1
**Status**: Active Development - 60% Complete

---

## 🎯 Vision

Build an **autonomous AI development team** that collaborates like human professionals:

- **code_developer** (AI Developer): Implements features autonomously from roadmap
- **project-manager** (AI PM): Manages roadmap, translates user needs, coordinates work
- **User** (Product Owner): Provides requirements, makes decisions, approves deliverables

**Goal**: Create a professional software development workflow where AI agents handle implementation while users focus on product vision and strategic decisions.

---

## 📊 Current Progress

### Overall Status

| Category | Progress | Status |
|----------|----------|--------|
| **Core Infrastructure** | 90% | ✅ Complete |
| **Autonomous Development** | 75% | 🔄 In Progress |
| **Project Management CLI** | 85% | ✅ Phase 2 Complete |
| **User Interface** | 40% | 🔄 Partial |
| **Documentation** | 70% | ✅ Strong Foundation |
| **Cloud Deployment** | 0% | 📝 Planned |

### Priorities Completed: 6/15

**Completed** ✅:
- PRIORITY 1: Analytics & Observability
- PRIORITY 2: Project Manager CLI (Phase 2)
- PRIORITY 2.5: UX Documentation Suite
- PRIORITY 3: code_developer daemon
- PRIORITY 6: Streamlit Agent UI
- PRIORITY 7: Professional Documentation

**In Progress** 🔄:
- US-004: Claude CLI Integration (Critical - blocking daemon)

**Planned** 📝:
- PRIORITY 2.6-2.7: Daemon stability improvements
- PRIORITY 5-5.5-6: Streamlit dashboards
- PRIORITY 6.5: GCP Deployment
- PRIORITY 8-9: Multi-provider support & enhanced communication

---

## 🚀 Key Components

### 1. code_developer (Autonomous Development Daemon)

**What it does**:
- Reads ROADMAP.md continuously
- Implements features autonomously using Claude AI
- Creates branches, commits, pushes code
- Opens pull requests automatically
- Updates roadmap status

**Status**: ✅ **Operational** (requires Claude CLI integration for production use)

**Command**:
```bash
poetry run code-developer --auto-approve
```

**Current Blocker**: Requires API credits. Working on Claude CLI integration (US-004) to use subscription instead.

---

### 2. project-manager (AI Project Manager CLI)

**What it does**:
- Interactive CLI for roadmap management
- Natural language understanding via Claude AI
- User Story management (capture, prioritize, assign)
- Roadmap health analysis and recommendations
- PR tracking and DOD (Definition of Done) testing

**Status**: ✅ **Phase 2 Complete** - Fully functional with User Stories

**Commands**:
```bash
# Interactive chat mode
poetry run user-listener

# View roadmap
poetry run user-listener view

# Manage User Stories
poetry run user-listener user-story list
poetry run user-listener user-story add

# Analyze roadmap health
poetry run user-listener analyze
```

**Recent Features**:
- ✅ User Story backlog management
- ✅ AI-powered story extraction from natural language
- ✅ DOD testing framework (YAML-based test specifications)
- ✅ PR tracking with status indicators
- ✅ Claude AI integration for intelligent recommendations

---

### 3. User Story System

**What it is**:
A first-class entity system for capturing user needs before technical implementation.

**Workflow**:
1. **User** describes need in natural language: "I want to deploy on GCP so it runs 24/7"
2. **project-manager** extracts User Story components (role, want, so_that)
3. **project-manager** analyzes roadmap impact and asks prioritization questions
4. **User** provides business priority feedback
5. **project-manager** assigns story to appropriate technical priority
6. **code_developer** implements when priority becomes active
7. **project-manager** runs DOD tests before marking complete

**Status**: ✅ **Complete** with 4 User Stories in backlog

**Example User Stories**:
- **US-001**: Deploy code_developer on GCP (⭐⭐⭐⭐⭐, 5 points) - Assigned to PRIORITY 6.5
- **US-002**: View project health at a glance (⭐⭐⭐⭐, 3 points) - Backlog
- **US-003**: Track development via pull requests (⭐⭐⭐⭐⭐, 5 points) - Backlog
- **US-004**: Use Claude CLI instead of API (🚨 Critical, 3 points) - **BLOCKING**

---

### 4. Definition of Done (DOD) Testing

**What it is**:
Automated testing framework that validates User Stories are truly complete.

**How it works**:
- Each User Story has YAML-based test specifications
- Tests run automatically when story marked complete
- If tests fail, project-manager creates fix priority automatically
- Tests include: functional tests, command existence, file existence, integration tests

**Status**: ✅ **Design Complete** (documented in `docs/DOD_TESTING_DESIGN.md`)

**Example DOD Test**:
```yaml
tests:
  - name: "code_developer command exists"
    type: "command"
    command: "poetry run code-developer --help"
    expected_exit_code: 0
    expected_output_contains: "Code Developer Daemon"
```

---

## 🎯 User Story Backlog (4 Stories)

### 🚨 Critical Priority

**US-004**: Use Claude CLI instead of Anthropic API for code_developer
- **Status**: 🚨 Critical - Blocking daemon operation
- **Business Value**: ⭐⭐⭐⭐⭐
- **Effort**: 3 story points (2-3 days)
- **Why Critical**: User pays €200/month for Claude subscription but daemon requires separate API credits
- **Solution**: Implement ClaudeCLIInterface to use subscription via Claude CLI
- **Technical Feasibility**: ✅ Confirmed - `claude -p` (print mode) works programmatically

---

### ⭐ High Priority

**US-001**: Deploy code_developer on GCP
- **Status**: ✅ Assigned to PRIORITY 6.5
- **Business Value**: ⭐⭐⭐⭐⭐
- **Effort**: 5 story points (5-7 days)
- **Goal**: code_developer runs 24/7 on GCP for continuous autonomous development
- **Benefits**: Development continues without user's laptop running

**US-003**: Track development progress via pull requests
- **Status**: 📝 Backlog
- **Business Value**: ⭐⭐⭐⭐⭐
- **Effort**: 5 story points (4-6 days)
- **Goal**: project-manager understands what's being developed, what needs review, what needs testing
- **Features**: `/pr list`, `/pr review`, automatic DOD test runs

---

### 📋 Backlog

**US-002**: View project health at a glance
- **Status**: 📝 Backlog
- **Business Value**: ⭐⭐⭐⭐
- **Effort**: 3 story points (2-3 days)
- **Goal**: Health score for each priority to quickly identify risks and bottlenecks

---

## 📈 Prioritized Roadmap (High-Level)

### Phase 1: Foundation ✅ Complete

**PRIORITY 1**: Analytics & Observability
- Langfuse → SQLite export
- Performance analysis
- Multi-process rate limiting
- **Status**: ✅ 90% Complete

**PRIORITY 3**: code_developer Daemon
- Autonomous development loop
- Roadmap parsing and execution
- Git operations (branch, commit, push, PR)
- Notification system
- **Status**: ✅ Complete (needs US-004 for production)

---

### Phase 2: Project Management ✅ Complete

**PRIORITY 2**: Project Manager CLI
- Interactive roadmap management
- Claude AI integration
- Natural language understanding
- User Story system
- DOD testing framework
- **Status**: ✅ Complete (Phase 2)

**PRIORITY 2.5**: UX Documentation
- Complete documentation suite
- User guides, API docs, architecture docs
- Troubleshooting guides
- **Status**: ✅ Complete

**PRIORITY 7**: Professional Documentation
- Code review agent
- Multi-model support
- Documentation generation
- **Status**: ✅ Complete

---

### Phase 3: User Interfaces 🔄 Partial

**PRIORITY 6**: Streamlit Agent UI
- Web interface for agent interaction
- Real-time conversation
- File upload/download
- **Status**: ✅ Complete

**PRIORITY 5**: Streamlit Analytics Dashboard
- Performance metrics visualization
- Cost tracking
- Usage analytics
- **Status**: 📝 Planned

**PRIORITY 5.5**: Streamlit Error Dashboard
- Error monitoring and analysis
- Debug tools
- **Status**: 📝 Planned

---

### Phase 4: Stability & Monitoring 📝 Planned

**PRIORITY 2.6**: Daemon Fix Verification
- Verify daemon crash fixes
- Stability testing
- **Status**: 📝 Planned

**PRIORITY 2.7**: Daemon Crash Recovery
- Automatic recovery mechanisms
- State persistence
- **Status**: 📝 Planned

---

### Phase 5: Cloud Deployment ☁️ Planned

**PRIORITY 6.5**: GCP Deployment of code_developer
- Deploy daemon to Google Cloud Platform
- 24/7 autonomous operation
- Cloud Logging integration
- Cost optimization (<$50/month)
- **Status**: 📝 Planned (after Streamlit dashboards)
- **Linked to**: US-001

---

### Phase 6: Advanced Features 🚀 Future

**PRIORITY 8**: Multi-AI Provider Support
- Support for multiple AI providers (OpenAI, Google, etc.)
- Provider switching and fallback
- **Status**: 📝 Planned

**PRIORITY 9**: Enhanced Communication
- Improved agent-to-agent communication
- Better user notifications
- **Status**: 📝 Planned

---

## 🎨 Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│         (Product Owner / Developer / Stakeholder)            │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             │ Natural Language               │ Reviews/Approvals
             ↓                                ↓
┌─────────────────────────┐         ┌──────────────────────────┐
│   project-manager       │←───────→│   GitHub Pull Requests   │
│   (AI Project Manager)  │         │   (Code Review)          │
│                         │         └──────────────────────────┘
│ • Roadmap management    │
│ • User Story extraction │                    ↑
│ • DOD testing          │                     │
│ • PR tracking          │         Implementation/Commits
│ • Health analysis      │                     │
└────────────┬────────────┘                    │
             │                                 │
             │ Task Assignment         ┌───────┴──────────────┐
             ↓                         │   code_developer     │
┌─────────────────────────┐           │   (AI Developer)     │
│   ROADMAP.md            │←─────────→│                      │
│   (Source of Truth)     │           │ • Read ROADMAP       │
│                         │           │ • Implement features │
│ • Priorities            │           │ • Git operations     │
│ • User Stories          │           │ • Create PRs         │
│ • Technical specs       │           │ • Update status      │
└─────────────────────────┘           └──────────────────────┘
             │                                 │
             │                                 │
             └────────────────┬────────────────┘
                              │
                              ↓
                    ┌──────────────────────┐
                    │   Claude AI          │
                    │   (Brain)            │
                    │                      │
                    │ • API Mode           │
                    │ • CLI Mode (US-004)  │
                    └──────────────────────┘
```

### Data Flow

1. **User Input** → project-manager (natural language)
2. **project-manager** → ROADMAP.md (structured priorities)
3. **code_developer** → ROADMAP.md (read next task)
4. **code_developer** → Claude AI (implementation)
5. **code_developer** → GitHub (PR creation)
6. **GitHub** → User (review notification)
7. **User** → project-manager (approval/feedback)
8. **project-manager** → ROADMAP.md (status update)

---

## 💡 Key Design Principles

### 1. Roadmap as Source of Truth
- Single `ROADMAP.md` file controls all development
- Both AI agents and humans read/write to it
- Clear priority ordering (sequential execution)
- Status tracking (Planned → In Progress → Complete)

### 2. Human-AI Collaboration
- AI agents augment, don't replace, human decision-making
- User provides vision and priorities
- project-manager translates to technical work
- code_developer executes implementation
- User reviews and approves deliverables

### 3. User Stories First
- Capture user needs before technical specifications
- Natural language → structured format (role, want, so_that)
- Business value drives prioritization
- DOD tests ensure quality

### 4. Autonomous Yet Controllable
- code_developer can run fully autonomous (--auto-approve)
- OR require approval for each priority (interactive mode)
- Emergency stop always available (Ctrl+C)
- Notifications keep user informed

### 5. Professional Workflow
- Git branching strategy
- Pull requests for all changes
- Code review process
- Documentation requirements
- Testing standards (DOD)

---

## 🚧 Current Limitations & Known Issues

### Critical Blockers

1. **US-004 - API Credits Required**
   - **Issue**: code_developer requires Anthropic API credits
   - **User Impact**: Cannot run daemon despite €200/month Claude subscription
   - **Solution**: Implement Claude CLI integration (in progress)
   - **Timeline**: 2-3 days (3 story points)

### Performance Considerations

1. **Daemon Retry Logic**
   - Max 3 retries per priority before manual intervention required
   - Prevents infinite loops on vague/impossible priorities
   - Status: ✅ Implemented

2. **Rate Limiting**
   - Claude API/CLI rate limits apply
   - WAL-mode SQLite for multi-process coordination
   - Status: ✅ Implemented

### Future Improvements

1. **Parallel Processing**: Currently sequential priority execution
2. **Multi-Repository Support**: Currently single repo only
3. **Advanced PR Analytics**: Currently basic PR tracking
4. **Cost Optimization**: Need usage analytics and budgeting

---

## 📅 Sprint Demo Schedule

> **Sprint Cadence**: 2-week cycles with end-of-sprint demos
> **Current Sprint**: Sprint 7 (2025-10-10 to 2025-10-24)
> **Velocity**: 1 priority per 2-3 days (autonomous, post US-004)

---

### Sprint 7 - Claude CLI Integration & Enhanced UX
**Demo Date**: 📅 **October 24, 2025** (2 weeks)
**Status**: 🔄 In Progress
**Priorities**: US-004 (Claude CLI), US-006 (Chat UX), PRIORITY 2.6

**Deliverables**:
- ✅ code_developer runs with Claude CLI (no API credits needed)
- ✅ Daemon stability verification
- ✅ ClaudeCLIInterface implementation
- ✅ `--use-cli` flag functional
- 🎨 user-listener UI at claude-cli quality level
- 🎨 Streaming responses + syntax highlighting
- 🎨 Multi-line input + command history + auto-completion
- 🎨 Session persistence

**Demo Preview**:
- **Part 1 - Daemon**: code_developer autonomously implements a feature using Claude CLI
  - Show cost savings: €200/month subscription vs API credits
  - End-to-end workflow: ROADMAP → Implementation → PR → Merge

- **Part 2 - UI Polish**: user-listener with professional UX
  - Streaming responses (text appears word-by-word like claude-cli)
  - Multi-line input (Shift+Enter for complex commands)
  - Command auto-completion (Tab key)
  - Syntax highlighting for code blocks
  - Typing indicators ("Claude is thinking...")
  - Session restoration (previous conversation loaded)

---

### Sprint 8 - Daemon Stability & Analytics Dashboard
**Demo Date**: 📅 **November 7, 2025** (4 weeks)
**Status**: 📝 Planned
**Priorities**: PRIORITY 2.7, PRIORITY 5

**Deliverables**:
- Daemon crash recovery mechanisms
- State persistence across restarts
- Streamlit Analytics Dashboard (performance metrics, cost tracking)
- 24/7 operation validation

**Demo Preview**:
- Show daemon recovering from intentional crash
- Analytics dashboard: token usage, costs, performance trends
- Live metrics: requests/minute, average latency, error rates

---

### Sprint 9 - Advanced Dashboards & PR Tracking
**Demo Date**: 📅 **November 21, 2025** (6 weeks)
**Status**: 📝 Planned
**Priorities**: PRIORITY 5.5, US-003

**Deliverables**:
- Streamlit Error Dashboard (debugging tools)
- PR tracking with DOD tests (`/pr list`, `/pr review`)
- Automatic DOD test execution on PR completion
- Complete observability suite

**Demo Preview**:
- Error dashboard: trace errors, debug sessions, fix suggestions
- PR workflow: list open PRs, review status, run DOD tests
- DOD test automation: story marked complete → tests run → create fix priority if fails

---

### Sprint 10 - GCP Deployment (Cloud Migration)
**Demo Date**: 📅 **December 5, 2025** (8 weeks)
**Status**: 📝 Planned
**Priorities**: PRIORITY 6.5, US-001

**Deliverables**:
- code_developer running on GCP Compute Engine
- 24/7 autonomous operation (no laptop required)
- Cloud Logging integration
- Cost optimization: <$50/month target

**Demo Preview**:
- Show code_developer running in cloud
- Logs from Cloud Logging
- Autonomous PR creation from GCP instance
- Cost breakdown: compute, networking, storage

---

### Sprint 11 - Multi-Provider Support & Health Dashboard
**Demo Date**: 📅 **December 19, 2025** (10 weeks)
**Status**: 📝 Planned
**Priorities**: PRIORITY 8, US-002

**Deliverables**:
- Multi-AI provider support (OpenAI, Google, Anthropic)
- Provider fallback logic (if one fails, try next)
- Project health dashboard (per-priority health scores)
- Cost optimization across providers

**Demo Preview**:
- Switch between providers dynamically
- Fallback demonstration: disable Anthropic → fallback to OpenAI
- Health dashboard: identify risks, bottlenecks, blockers
- Cost comparison: provider pricing analysis

---

### Sprint 12 - Enhanced Communication (Production Ready)
**Demo Date**: 📅 **January 9, 2026** (12 weeks)
**Status**: 📝 Planned
**Priorities**: PRIORITY 9

**Deliverables**:
- Improved agent-to-agent communication
- Slack/Discord integration for notifications
- Real-time status updates
- Full production-ready system

**Demo Preview**:
- Slack bot: get roadmap updates, approve priorities, view PRs
- Agent coordination: project-manager ↔ code_developer messages
- Live notifications: priority started, PR created, tests passed
- Complete end-to-end system demonstration

---

## 📋 Next Steps

### Immediate (This Week)

1. **Implement US-004**: Claude CLI integration
   - Unblock daemon for production use
   - Enable €200/month subscription usage
   - Eliminate API credit dependency

2. **Test Daemon Stability**: Run extended test with US-004
   - Monitor for crashes/errors
   - Validate retry logic
   - Verify PR creation works end-to-end

### Short-Term (Next 2 Weeks)

1. **Complete PRIORITY 2.6-2.7**: Daemon stability
   - Crash recovery mechanisms
   - State persistence
   - Better error handling

2. **Implement Streamlit Dashboards** (PRIORITY 5, 5.5)
   - Analytics dashboard for performance metrics
   - Error dashboard for debugging
   - Cost tracking and optimization

### Medium-Term (Next Month)

1. **US-003**: PR tracking and review
   - `/pr list` and `/pr review` commands
   - Automatic DOD test execution
   - Status indicators for approval stages

2. **GCP Deployment** (PRIORITY 6.5)
   - Deploy code_developer to cloud
   - 24/7 autonomous operation
   - Cost: <$50/month target

### Long-Term (Next Quarter)

1. **US-001**: Full GCP production deployment
   - Monitoring and alerting
   - Auto-scaling if needed
   - Integration with project-manager

2. **Multi-Provider Support** (PRIORITY 8)
   - OpenAI, Google, Anthropic
   - Provider fallback logic
   - Cost optimization across providers

3. **Enhanced Communication** (PRIORITY 9)
   - Better agent coordination
   - Slack/Discord integration
   - Real-time status updates

---

## 🎯 Success Metrics

### Development Velocity
- **Target**: 1 priority implemented per 2-3 days (autonomous)
- **Current**: Manual implementation required (blocked by US-004)
- **Measurement**: PRs created per week by code_developer

### Code Quality
- **Target**: 90% of PRs require minimal changes
- **Current**: Not yet measured (daemon not fully operational)
- **Measurement**: PR approval rate, review comment count

### User Satisfaction
- **Target**: User spends <1 hour/day on project management
- **Current**: ~2-3 hours/day (manual development)
- **Measurement**: Time tracking, user feedback

### Cost Efficiency
- **Target**: <$100/month total AI costs (API + subscription)
- **Current**: €200/month Claude subscription (not fully utilized)
- **Measurement**: Monthly billing, token usage analytics

---

## 📚 Documentation

### For Users
- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [UX_GUIDE.md](UX_GUIDE.md) - Complete user experience guide
- [USER_STORY_GUIDE.md](USER_STORY_GUIDE.md) - How to write User Stories

### For Developers
- [ROADMAP.md](ROADMAP.md) - Complete technical roadmap (detailed)
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### For Decision Makers
- [ROADMAP_OVERVIEW.md](ROADMAP_OVERVIEW.md) - This document
- [DOD_TESTING_DESIGN.md](DOD_TESTING_DESIGN.md) - Quality assurance strategy
- [USER_STORY_DESIGN.md](USER_STORY_DESIGN.md) - Product management approach

---

## 🤝 Team & Collaboration

### Current Team
- **Development**: AI agents (code_developer) + User guidance
- **Project Management**: AI (project-manager) + User decisions
- **Product Ownership**: User (strategic vision)

### Collaboration Model
```
User defines WHAT and WHY
   ↓
project-manager defines HOW (high-level)
   ↓
code_developer implements HOW (low-level)
   ↓
User reviews and approves
   ↓
Cycle repeats
```

### Communication Channels
- **Roadmap Updates**: ROADMAP.md (single source of truth)
- **Daily Progress**: Git commits + PR descriptions
- **Urgent Issues**: Notifications (project-manager notifications)
- **Strategic Decisions**: User Stories + prioritization questions

---

## 📞 Support & Contact

### Getting Help
- **Documentation**: Start with [QUICKSTART.md](QUICKSTART.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues**: GitHub Issues tracker
- **Questions**: Create User Story via `project-manager user-story add`

### Project Links
- **Repository**: [github.com/Bobain/MonolithicCoffeeMakerAgent](https://github.com/Bobain/MonolithicCoffeeMakerAgent)
- **Documentation**: `docs/` directory
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

---

## 🎉 Conclusion

**Coffee Maker Agent** is building toward a future where:
- AI agents handle routine development work autonomously
- Users focus on product vision and strategic decisions
- Quality is maintained through automated testing (DOD)
- Collaboration feels natural and professional

**Current Status**: 60% complete, with core infrastructure operational and critical User Story (US-004) in progress to unlock full autonomous capability.

**Next Milestone**: Complete US-004 and achieve fully operational autonomous development with cost-effective Claude CLI integration.

---

**Questions? Feedback? New User Stories?**

Run: `poetry run user-listener`
