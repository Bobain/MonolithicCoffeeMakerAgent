# US-057: Transform Daemon into Multi-Agent Orchestrator

**Status**: 📋 PLANNED (Blocked by US-056)

**Priority**: HIGH (Foundation for true autonomous team operation)

**Estimated Effort**: 1-2 weeks (major architectural refactor)

**Created**: 2025-10-17

**Prerequisites**: US-056 (CFR-013 enforcement - daemon working on roadmap branch only)

---

## Executive Summary

Transform the current single-agent `code_developer` daemon into a **Multi-Agent Orchestrator** that launches and manages ALL agents working simultaneously as a coordinated autonomous team.

**Current State**:
- Single agent (code_developer only)
- Sequential execution on ROADMAP priorities
- One process, one focus area
- Named: "code_developer daemon"

**Desired State**:
- ALL agents running in parallel (6 simultaneous processes)
- Each agent continuously executing its responsibilities
- Coordinated through shared state and delegation
- Named: "Autonomous Agent Orchestrator" or "Team Daemon"

**Key Benefit**: 3-6x speedup through parallel execution + proactive collaboration

---

## Problem Statement

### Current Bottleneck: Sequential Execution

Today's daemon architecture creates artificial bottlenecks:

```
CURRENT (Sequential):
┌─────────────────────────────────────────────┐
│  code_developer daemon                      │
│                                             │
│  [1. Wait for spec] ──► ⏰ 2 hours          │
│         │                                   │
│         ▼                                   │
│  [2. Implement] ────► ⏰ 4 hours            │
│         │                                   │
│         ▼                                   │
│  [3. Wait for demo] ─► ⏰ 1 hour            │
│         │                                   │
│         ▼                                   │
│  [4. Fix bug] ───────► ⏰ 2 hours           │
│                                             │
│  Total Time: 9 hours                        │
└─────────────────────────────────────────────┘

PROPOSED (Parallel):
┌─────────────────────────────────────────────┐
│  Multi-Agent Orchestrator                   │
│                                             │
│  [architect] ────────► Creating specs       │
│  [code_developer] ───► Implementing         │
│  [assistant] ────────► Creating demos       │
│  [project_manager] ──► Monitoring GitHub    │
│  [assistant (with code analysis skills)] ────► Analyzing codebase   │
│  [ux-design-expert] ─► Reviewing UI/UX      │
│                                             │
│  All running simultaneously!                │
│  Total Time: 4 hours (2.25x faster)         │
└─────────────────────────────────────────────┘
```

### Specific Pain Points

1. **Spec Creation Blocking**: code_developer waits for architect to create specs (CFR-011 violation)
2. **No Continuous QA**: assistant only creates demos when manually requested
3. **Reactive Monitoring**: project_manager only checks status when user asks
4. **Missed Opportunities**: assistant (with code analysis skills) insights delay architecture improvements
5. **Design Feedback Lag**: ux-design-expert only consulted reactively

---

## Vision: The Autonomous Team

### Team Members (6 Agents, All Running Continuously)

#### 1. architect (Proactive Spec Creation)
**Continuous Work Loop**:
```python
while True:
    # Morning: Check ROADMAP coverage (CFR-011)
    roadmap = read_roadmap()
    next_5_priorities = roadmap.get_next_priorities(5)
    missing_specs = identify_missing_specs(next_5_priorities)

    if len(missing_specs) > 2:
        # URGENT: Create specs to unblock code_developer
        for priority in missing_specs[:3]:
            create_technical_spec(priority)
            commit_to_roadmap_branch()  # CFR-013

    # Daily: Read assistant (with code analysis skills) reports
    new_reports = get_new_code_searcher_reports()
    for report in new_reports:
        analyze_findings(report)
        integrate_into_next_specs(report.improvements)

    # Weekly: Analyze codebase directly
    if days_since_last_analysis() >= 7:
        analyze_codebase_for_refactoring()

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()

    sleep(3600)  # Check hourly
```

**Key Responsibilities**:
- Create 3-5 specs AHEAD of code_developer (CFR-011)
- Read assistant (with code analysis skills) reports daily, integrate findings
- Analyze codebase weekly for refactoring opportunities
- Respond to urgent spec requests (CFR-012)

#### 2. code_developer (Implementation)
**Continuous Work Loop**:
```python
while True:
    # Sync with roadmap branch (CFR-013, US-027)
    git_pull_roadmap_branch()

    # Get next priority
    next_priority = roadmap.get_next_planned_priority()

    if not next_priority:
        # Check for refactoring tasks
        refactoring_tasks = get_refactoring_backlog()
        if refactoring_tasks:
            work_on_refactoring()
        else:
            sleep(300)  # No work, check back in 5 minutes
        continue

    # Ensure spec exists (should be ready due to architect!)
    if not has_technical_spec(next_priority):
        warn_architect_spec_missing()
        sleep(600)  # Wait for architect
        continue

    # Implement priority
    implement_priority(next_priority)
    run_tests()
    commit_to_roadmap_branch()  # CFR-013

    # Notify assistant to create demo
    notify_assistant_demo_needed(next_priority)

    # Merge progress to roadmap (US-024)
    merge_to_roadmap_branch()

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()
```

**Key Responsibilities**:
- Implement priorities from ROADMAP (same as current daemon)
- Stay on roadmap branch (CFR-013, US-056)
- Frequent commits with agent identification
- Notify assistant when features complete

#### 3. project_manager (Monitoring & Coordination)
**Continuous Work Loop**:
```python
while True:
    # Check GitHub for blockers
    open_prs = gh_pr_list()
    failing_prs = [pr for pr in open_prs if pr.checks_failing]

    if failing_prs:
        warn_user_about_failing_prs(failing_prs)
        notify_code_developer_fix_needed()

    # Check ROADMAP health
    roadmap = read_roadmap()
    if roadmap.has_stalled_priorities():
        warn_user_about_stalls()

    # Verify DoD when requested (not continuous)
    pending_dod_requests = get_pending_dod_verifications()
    for request in pending_dod_requests:
        verify_with_puppeteer(request)
        report_results_to_user()

    # Weekly: Generate project status report
    if is_monday_morning():
        generate_weekly_status_report()
        send_to_user()

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()

    sleep(900)  # Check every 15 minutes
```

**Key Responsibilities**:
- Monitor GitHub (PRs, issues, CI/CD status)
- Track ROADMAP health (stalled priorities, velocity)
- Verify DoD when requested (post-completion)
- Generate status reports
- Warn users about blockers proactively

#### 4. assistant (Demos, Bugs, Documentation)
**Continuous Work Loop**:
```python
while True:
    # Check for completed features needing demos
    completed_features = get_features_without_demos()

    for feature in completed_features:
        # Create demo with Puppeteer
        demo_results = create_visual_demo(feature)

        if demo_results.has_bugs:
            # COMPREHENSIVE bug reporting
            bug_report = analyze_bug_comprehensively(
                root_cause=demo_results.root_cause,
                requirements_for_fix=demo_results.fix_requirements,
                expected_behavior=demo_results.expected_behavior,
                reproduction_steps=demo_results.repro_steps
            )

            # Report to project_manager (who adds to ROADMAP)
            report_bug_to_project_manager(bug_report)
        else:
            # Demo successful - mark feature verified
            mark_feature_verified(feature)

    # Answer quick questions (when user asks)
    # This is reactive, not continuous

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()

    sleep(1800)  # Check every 30 minutes
```

**Key Responsibilities**:
- Create demos for completed features (ONLY agent that creates demos)
- Test features, detect bugs during demos
- Provide COMPREHENSIVE bug reports to project_manager
- Answer quick questions when asked
- Keep ROADMAP details in mind at all times

#### 5. assistant (with code analysis skills) (Continuous Analysis)
**Continuous Work Loop**:
```python
while True:
    # Weekly: Deep codebase analysis
    if days_since_last_analysis() >= 7:
        # Security audit
        security_findings = run_security_audit()
        prepare_security_report(security_findings)

        # Dependency tracing
        dependency_graph = analyze_dependencies()
        identify_circular_dependencies()

        # Code reuse opportunities
        duplication = find_code_duplication()
        suggest_refactoring_opportunities()

        # Present findings to assistant → project_manager
        present_findings_to_assistant()

    # Daily: Monitor for patterns
    recent_commits = get_recent_commits()
    analyze_commit_patterns(recent_commits)

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()

    sleep(86400)  # Check daily
```

**Key Responsibilities**:
- Weekly codebase security audits
- Dependency tracing and analysis
- Code reuse identification
- Refactoring opportunity suggestions
- Present findings to assistant (who delegates to project_manager for docs)

#### 6. ux-design-expert (Design Guidance)
**Continuous Work Loop**:
```python
while True:
    # Review recent UI/UX changes
    recent_ui_changes = get_recent_ui_changes()

    for change in recent_ui_changes:
        # Analyze design quality
        design_review = review_ui_ux(change)

        if design_review.has_improvements:
            # Provide feedback
            provide_design_feedback(
                component=change.component,
                improvements=design_review.improvements,
                tailwind_suggestions=design_review.tailwind
            )

    # Check for design requests (reactive)
    # Most work is reactive when delegated

    # Check for urgent requests (CFR-012)
    if has_urgent_request():
        interrupt_background_work()
        handle_request()

    sleep(3600)  # Check hourly
```

**Key Responsibilities**:
- Review UI/UX changes
- Provide design feedback proactively
- Answer design questions when delegated
- Tailwind CSS guidance

---

## Architecture

### Multi-Process Orchestration

```python
# orchestrator/daemon.py

class AutonomousTeamOrchestrator:
    """Multi-agent orchestrator managing all agents in parallel."""

    def __init__(self):
        self.agents = {
            AgentType.ARCHITECT: ArchitectAgent(),
            AgentType.CODE_DEVELOPER: CodeDeveloperAgent(),
            AgentType.PROJECT_MANAGER: ProjectManagerAgent(),
            AgentType.ASSISTANT: AssistantAgent(),
            AgentType.ASSISTANT: CodeSearcherAgent(),
            AgentType.UX_DESIGN_EXPERT: UXDesignExpertAgent(),
        }

        self.processes = {}  # {agent_type: subprocess}
        self.status_dir = Path("data/agent_status/")

    def run(self):
        """Launch all agents in separate subprocesses."""
        logger.info("🚀 Starting Autonomous Team Orchestrator...")

        # Launch each agent in subprocess
        for agent_type, agent in self.agents.items():
            process = self._launch_agent_subprocess(agent_type, agent)
            self.processes[agent_type] = process
            logger.info(f"✅ {agent_type.value} started (PID: {process.pid})")

        # Monitor agent health
        while self.running:
            self._check_agent_health()
            self._handle_crashes()
            time.sleep(30)

    def _launch_agent_subprocess(self, agent_type, agent):
        """Launch agent in separate subprocess with singleton enforcement."""
        def agent_runner():
            # CFR-000: Singleton enforcement
            with AgentRegistry.register(agent_type):
                agent.run_continuous()

        process = multiprocessing.Process(
            target=agent_runner,
            name=f"agent_{agent_type.value}"
        )
        process.start()
        return process

    def _check_agent_health(self):
        """Monitor agent health via status files."""
        for agent_type, process in self.processes.items():
            status_file = self.status_dir / f"{agent_type.value}_status.json"

            if not process.is_alive():
                logger.error(f"❌ {agent_type.value} crashed! Restarting...")
                self._restart_agent(agent_type)

            # Check last heartbeat
            if status_file.exists():
                status = json.loads(status_file.read_text())
                last_heartbeat = datetime.fromisoformat(status["last_heartbeat"])

                if (datetime.now() - last_heartbeat).seconds > 300:
                    logger.warning(f"⚠️  {agent_type.value} stalled! Restarting...")
                    self._restart_agent(agent_type)

    def _restart_agent(self, agent_type):
        """Restart crashed agent."""
        # Kill old process
        old_process = self.processes[agent_type]
        old_process.terminate()
        old_process.join(timeout=5)
        if old_process.is_alive():
            old_process.kill()

        # Launch new process
        agent = self.agents[agent_type]
        new_process = self._launch_agent_subprocess(agent_type, agent)
        self.processes[agent_type] = new_process
        logger.info(f"✅ {agent_type.value} restarted (PID: {new_process.pid})")
```

### Coordination Mechanisms

#### 1. Shared State (File-Based)
```
data/agent_status/
├── architect_status.json          # Architect current work
├── code_developer_status.json     # Code developer progress
├── project_manager_status.json    # Project health metrics
├── assistant_status.json          # Demo queue
├── code_searcher_status.json      # Analysis progress
└── ux_design_expert_status.json   # Design review queue
```

**Status File Format**:
```json
{
  "agent": "architect",
  "state": "working",
  "current_task": "Creating SPEC-057-001.md",
  "progress": 0.6,
  "last_heartbeat": "2025-10-17T10:30:00",
  "next_check": "2025-10-17T11:30:00",
  "metrics": {
    "specs_created_today": 2,
    "specs_pending": 1
  }
}
```

#### 2. Inter-Agent Messaging (Delegation)
```
data/agent_messages/
├── architect_inbox/
│   └── urgent_spec_request_20251017_103000.json
├── code_developer_inbox/
│   └── bug_fix_request_20251017_103100.json
└── assistant_inbox/
    └── demo_request_20251017_103200.json
```

**Message Format**:
```json
{
  "from": "code_developer",
  "to": "assistant",
  "type": "demo_request",
  "priority": "normal",
  "timestamp": "2025-10-17T10:32:00",
  "content": {
    "feature": "US-045",
    "title": "Daemon delegates spec creation to architect",
    "acceptance_criteria": [
      "Daemon detects missing spec",
      "Daemon notifies architect",
      "Architect creates spec"
    ]
  }
}
```

#### 3. CFR-000 File Ownership (Prevent Conflicts)
Each agent ONLY modifies files it owns:

| Agent | Owned Files |
|-------|-------------|
| architect | docs/architecture/specs/, docs/architecture/decisions/, pyproject.toml |
| code_developer | coffee_maker/, tests/, scripts/, .claude/ |
| project_manager | docs/roadmap/, docs/*.md (top-level) |
| assistant | (READ-ONLY for code/docs, ACTIVE for demos/bugs) |
| assistant (with code analysis skills) | (READ-ONLY everywhere) |
| ux-design-expert | (Provides specs, doesn't implement) |

#### 4. CFR-012 Interrupt Handling
All agents check for urgent requests every loop iteration:

```python
def run_continuous(self):
    """Agent continuous work loop with interruption handling."""
    while True:
        # CFR-012: Check for urgent requests FIRST
        urgent_message = self._check_inbox_urgent()
        if urgent_message:
            self._handle_urgent_request(urgent_message)
            continue  # Skip background work this iteration

        # Normal background work
        self._do_background_work()

        # Update status
        self._write_status()

        # Sleep
        time.sleep(self.check_interval)
```

#### 5. CFR-013 Roadmap Branch (All Agents)
**CRITICAL**: ALL agents work on roadmap branch ONLY.

```python
# orchestrator/agent_base.py

class BaseAgent:
    """Base class for all agents with CFR-013 enforcement."""

    def __init__(self):
        self.git = GitManager()
        self._enforce_roadmap_branch()

    def _enforce_roadmap_branch(self):
        """Ensure agent is on roadmap branch (CFR-013)."""
        current_branch = self.git.get_current_branch()

        if current_branch != "roadmap":
            raise CFR013ViolationError(
                f"CFR-013 VIOLATION: Agent {self.agent_type.value} "
                f"not on roadmap branch!\n\n"
                f"Current: {current_branch}\n"
                f"Required: roadmap\n\n"
                f"All agents MUST work on roadmap branch only."
            )

    def commit_changes(self, message: str):
        """Commit changes with agent identification."""
        # Agent identification in commit message
        full_message = (
            f"{message}\n\n"
            f"🤖 Agent: {self.agent_type.value}\n"
            f"🤖 Generated with Claude Code\n\n"
            f"Co-Authored-By: Claude <noreply@anthropic.com>"
        )

        self.git.commit(full_message)
        self.git.push("roadmap")  # Always push to roadmap branch
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

#### 1.1 Create Orchestrator Base (2 days)
- [ ] Create `orchestrator/` module
- [ ] Implement `AutonomousTeamOrchestrator` class
- [ ] Multi-process management with subprocess
- [ ] Agent health monitoring
- [ ] Crash recovery and restart logic

#### 1.2 Create Agent Base Classes (2 days)
- [ ] Create `orchestrator/agent_base.py`
- [ ] Implement `BaseAgent` with CFR-013 enforcement
- [ ] Implement continuous work loop with CFR-012 interruption
- [ ] Status file writing (heartbeat, progress)
- [ ] Inbox checking for messages

#### 1.3 Shared State Infrastructure (1 day)
- [ ] Create `data/agent_status/` directory
- [ ] Create `data/agent_messages/` directory structure
- [ ] Implement status file schemas
- [ ] Implement message queue system

### Phase 2: Agent Migration (Week 2)

#### 2.1 Migrate code_developer (2 days)
- [ ] Extract daemon logic into `CodeDeveloperAgent`
- [ ] Inherit from `BaseAgent`
- [ ] Implement continuous work loop
- [ ] Test in orchestrator

#### 2.2 Create architect Agent (2 days)
- [ ] Implement `ArchitectAgent` with CFR-011 logic
- [ ] Morning ROADMAP check for spec coverage
- [ ] Daily assistant (with code analysis skills) report reading
- [ ] Weekly codebase analysis
- [ ] Test in orchestrator

#### 2.3 Create project_manager Agent (1 day)
- [ ] Implement `ProjectManagerAgent`
- [ ] GitHub monitoring loop
- [ ] ROADMAP health checks
- [ ] DoD verification on request
- [ ] Test in orchestrator

#### 2.4 Create assistant Agent (2 days)
- [ ] Implement `AssistantAgent`
- [ ] Demo creation loop
- [ ] Bug detection and comprehensive reporting
- [ ] Test in orchestrator

#### 2.5 Create assistant (with code analysis skills) & ux-design-expert Agents (1 day)
- [ ] Implement `CodeSearcherAgent` (weekly analysis)
- [ ] Implement `UXDesignExpertAgent` (reactive + review)
- [ ] Test in orchestrator

---

## Success Metrics

### Performance Metrics

**Baseline (Current - Sequential)**:
- Average priority completion time: 4-6 hours
- Specs created: Reactive (after blocking)
- Demos created: Manual request only
- Bug detection: Ad-hoc
- Code analysis: Manual request only

**Target (Multi-Agent - Parallel)**:
- Average priority completion time: 1.5-2 hours (3x faster)
- Specs created: Proactive (3-5 ahead)
- Demos created: Automatic within 30 minutes
- Bug detection: Within 1 hour of completion
- Code analysis: Weekly automatically

### Quality Metrics

**Collaboration Quality**:
- CFR-011 compliance: 100% (specs always ready)
- CFR-012 compliance: <2 minute response time
- CFR-013 compliance: 100% (all on roadmap branch)
- Zero merge conflicts (CFR-000 file ownership)

**Team Coordination**:
- architect unblocking code_developer: Proactive
- assistant QA coverage: 100% of features
- project_manager visibility: Real-time
- assistant (with code analysis skills) insights: Weekly integration

---

## Benefits

### 1. Speed (3-6x Faster)
**Parallel Execution**: Multiple agents working simultaneously instead of sequentially.

**Example**:
```
Sequential (Today):
- Spec creation: 2 hours (blocking)
- Implementation: 4 hours (blocked waiting for spec)
- Demo: 1 hour (manual request)
- Bug fix: 2 hours (blocked waiting for demo)
Total: 9 hours

Parallel (US-057):
- Spec creation: 2 hours (architect) │
- Implementation: 4 hours (developer) ├─ All happening
- Demo: 1 hour (assistant)           │  simultaneously!
- Monitoring: Continuous (PM)        │
Total: 4 hours (architect finishes first, developer starts immediately)
```

### 2. Quality (Proactive QA)
**Continuous Testing**: assistant creates demos automatically, catches bugs early.

**Example**:
- Feature X implemented at 10am
- assistant creates demo at 10:30am
- Bug detected at 10:45am
- Bug reported to project_manager at 11am
- architect designs fix at 11:30am
- code_developer fixes at 12pm
- Verified by 12:30pm

**Result**: Bug fixed same day instead of weeks later.

### 3. Autonomy (True Self-Management)
**Proactive Architecture**: architect creates specs BEFORE code_developer blocks (CFR-011).

**Example**:
- Monday morning: architect reads ROADMAP
- Sees US-058, US-059, US-060 have no specs
- Creates all 3 specs by noon
- code_developer never blocks waiting for specs

**Result**: Developer flow uninterrupted, maximum velocity.

### 4. Visibility (Real-Time Monitoring)
**Continuous Monitoring**: project_manager tracks everything, warns proactively.

**Example**:
- PR checks failing? Warn immediately
- Priority stalled 3 days? Alert user
- Velocity declining? Flag trend

**Result**: Issues caught early, no surprises.

### 5. Learning (Continuous Improvement)
**Weekly Analysis**: assistant (with code analysis skills) provides regular insights.

**Example**:
- Every Monday: Security audit
- Every Wednesday: Dependency analysis
- Every Friday: Refactoring opportunities
- architect integrates findings into specs

**Result**: Codebase quality improves continuously.

---

## Risks & Mitigations

### Risk 1: Process Complexity
**Risk**: Managing 6 subprocesses is complex, more failure points.

**Mitigation**:
- Robust health monitoring (heartbeat every 30 seconds)
- Automatic restart on crash
- Status dashboard showing all agents
- Comprehensive logging

### Risk 2: File Conflicts
**Risk**: Multiple agents modifying same files → merge conflicts.

**Mitigation**:
- Strict CFR-000 file ownership enforcement
- Each agent owns specific directories
- READ-ONLY access for non-owners
- Runtime checks prevent violations

### Risk 3: Message Queue Overload
**Risk**: Too many messages between agents → performance degradation.

**Mitigation**:
- Priority-based message queuing
- Inbox size limits (max 100 messages)
- Automatic cleanup of old messages
- CFR-012 ensures urgent messages processed first

### Risk 4: Cost (API Usage)
**Risk**: 6 agents running continuously → high API costs.

**Mitigation**:
- Smart sleep intervals (not all agents check every second)
- Batch operations where possible
- Cache frequently accessed data
- Use Claude CLI for some agents (subscription vs. API)

### Risk 5: Debugging Difficulty
**Risk**: Bugs in multi-agent system harder to debug than single agent.

**Mitigation**:
- Comprehensive Langfuse observability for all agents
- Detailed logging with agent identification
- Status files capture full agent state
- Crash history tracked per agent

---

## Migration Strategy

### Backward Compatibility

**Option 1: Gradual Migration** (Recommended)
```bash
# Week 1: Launch orchestrator with 2 agents
poetry run orchestrator --agents=architect,code_developer

# Week 2: Add assistant
poetry run orchestrator --agents=architect,code_developer,assistant

# Week 3: Add project_manager
poetry run orchestrator --agents=architect,code_developer,assistant,project_manager

# Week 4: Full team
poetry run orchestrator  # All agents
```

**Option 2: Keep Legacy Mode**
```bash
# Old way (single agent)
poetry run code-developer --auto-approve

# New way (multi-agent)
poetry run orchestrator --auto-approve
```

### CLI Interface

```bash
# Start full team
poetry run orchestrator

# Start specific agents
poetry run orchestrator --agents=architect,code_developer

# View agent status
poetry run orchestrator status

# Stop all agents
poetry run orchestrator stop

# Restart specific agent
poetry run orchestrator restart architect

# View agent logs
poetry run orchestrator logs architect
```

---

## Testing Plan

### Unit Tests
```python
# tests/unit/orchestrator/test_orchestrator.py

def test_orchestrator_launches_all_agents():
    """Test orchestrator launches all 6 agents."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    assert len(orchestrator.processes) == 6
    assert all(p.is_alive() for p in orchestrator.processes.values())

def test_orchestrator_restarts_crashed_agent():
    """Test orchestrator restarts crashed agent."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Simulate crash
    architect_process = orchestrator.processes[AgentType.ARCHITECT]
    architect_process.terminate()

    # Wait for restart
    time.sleep(60)

    # Verify restarted
    new_process = orchestrator.processes[AgentType.ARCHITECT]
    assert new_process.is_alive()
    assert new_process.pid != architect_process.pid

def test_agent_enforces_cfr_013():
    """Test agent enforces CFR-013 (roadmap branch only)."""
    agent = ArchitectAgent()

    # Switch to wrong branch
    agent.git.checkout("main")

    # Should raise violation
    with pytest.raises(CFR013ViolationError):
        agent._enforce_roadmap_branch()
```

### Integration Tests
```python
# tests/integration/orchestrator/test_multi_agent_coordination.py

def test_architect_creates_spec_before_code_developer_needs_it():
    """Test architect creates specs proactively (CFR-011)."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Wait for architect to check ROADMAP
    time.sleep(3600)  # 1 hour

    # Verify specs created
    roadmap = RoadmapParser("docs/roadmap/ROADMAP.md")
    next_5 = roadmap.get_next_priorities(5)

    for priority in next_5:
        spec_path = f"docs/architecture/specs/SPEC-{priority['number']}-001.md"
        assert Path(spec_path).exists()

def test_assistant_creates_demo_after_code_developer_completes():
    """Test assistant creates demo automatically."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Wait for code_developer to complete priority
    time.sleep(7200)  # 2 hours

    # Verify assistant created demo
    demo_log = Path("data/demos/US-057_demo.json")
    assert demo_log.exists()

    demo_data = json.loads(demo_log.read_text())
    assert demo_data["status"] == "success"
```

---

## Documentation Updates

### Files to Update

1. **/.claude/CLAUDE.md**
   - Update daemon architecture section
   - Document multi-agent orchestration
   - Explain agent responsibilities

2. **/.claude/agents/README.md**
   - Document orchestrator usage
   - Explain continuous work loops
   - Show CLI commands

3. **/docs/roadmap/TEAM_COLLABORATION.md**
   - Update collaboration workflows
   - Document inter-agent messaging
   - Explain coordination mechanisms

4. **/docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md**
   - Add CFR-014: Multi-Agent Orchestration Rules
   - Update CFR-011 with orchestrator context
   - Update CFR-012 with orchestrator examples

---

## Open Questions

1. **Agent Priority**: If multiple agents need attention, which gets priority?
   - **Proposal**: CFR-012 urgent requests always first, then by agent order (architect → developer → assistant → PM → searcher → UX)

2. **Resource Limits**: Should we limit how many agents can run simultaneously?
   - **Proposal**: Start with all 6, add `--max-agents` flag if performance issues

3. **Cost Control**: How do we prevent runaway API costs?
   - **Proposal**: Add `--daily-budget` flag, pause agents when budget exceeded

4. **User Override**: How does user manually control agents?
   - **Proposal**: CLI commands: `orchestrator pause architect`, `orchestrator resume architect`

5. **Error Propagation**: If one agent fails, should others stop?
   - **Proposal**: No, each agent independent. Orchestrator just restarts failed agent.

---

## Prerequisites

**US-056 MUST be complete before starting US-057**.

**Why**:
- US-056 enforces CFR-013 (roadmap branch only)
- Multi-agent orchestrator REQUIRES all agents on roadmap branch
- Without CFR-013 enforcement, agents will create chaos with feature branches

**Verification**:
```bash
# Check US-056 complete
poetry run code-developer --auto-approve

# Should stay on roadmap branch throughout
git branch --show-current  # Should always show "roadmap"
```

---

## Acceptance Criteria

### Functional Requirements

- [ ] Orchestrator launches all 6 agents in separate subprocesses
- [ ] Each agent runs continuous work loop with CFR-012 interruption handling
- [ ] Agent health monitoring with automatic restart on crash
- [ ] Status files written by all agents (heartbeat every 30 seconds)
- [ ] Inter-agent messaging works (delegation)
- [ ] CFR-000 file ownership enforced (no conflicts)
- [ ] CFR-013 enforced (all agents on roadmap branch)
- [ ] CLI interface for orchestrator control
- [ ] Graceful shutdown of all agents

### Performance Requirements

- [ ] architect creates 3-5 specs ahead of code_developer (CFR-011)
- [ ] code_developer implementation time unchanged (~4 hours/priority)
- [ ] assistant creates demo within 30 minutes of completion
- [ ] project_manager checks GitHub every 15 minutes
- [ ] assistant (with code analysis skills) runs weekly analysis automatically
- [ ] Overall priority completion time reduced by 50% (3-6x speedup)

### Quality Requirements

- [ ] Zero merge conflicts between agents
- [ ] All commits include agent identification
- [ ] All agents respond to urgent requests within 2 minutes (CFR-012)
- [ ] Status dashboard shows all agent states in real-time
- [ ] Langfuse tracking for all agent executions
- [ ] Comprehensive logging with agent identification

---

## Definition of Done

**Code Complete**:
- [ ] All agent classes implemented
- [ ] Orchestrator with multi-process management
- [ ] Status file infrastructure
- [ ] Inter-agent messaging system
- [ ] CFR enforcement in all agents
- [ ] CLI interface for orchestrator

**Tests Pass**:
- [ ] Unit tests: 100% coverage for orchestrator
- [ ] Integration tests: Multi-agent coordination scenarios
- [ ] CFR enforcement tests
- [ ] Crash recovery tests
- [ ] Performance benchmarks

**Documentation**:
- [ ] CLAUDE.md updated with orchestrator architecture
- [ ] Agent README with usage examples
- [ ] TEAM_COLLABORATION.md updated
- [ ] CFR document updated with CFR-014
- [ ] Migration guide written

**Deployment**:
- [ ] Orchestrator deployed and running
- [ ] All 6 agents operational
- [ ] Status dashboard showing all agents
- [ ] Monitoring and alerting configured
- [ ] User notified of new multi-agent system

**Validation**:
- [ ] Orchestrator runs for 24 hours without crashes
- [ ] architect creates specs proactively (no blocking)
- [ ] assistant creates demos automatically
- [ ] project_manager monitors GitHub continuously
- [ ] All agents respect CFR-013 (roadmap branch only)
- [ ] Zero merge conflicts observed
- [ ] Priority completion time reduced by 50%

---

## Related Work

**Prerequisites**:
- US-056: Enforce CFR-013 (Daemon on roadmap branch only) 🚨 CRITICAL

**Builds On**:
- US-045: Daemon delegates spec creation to architect
- US-027: Roadmap branch as single source of truth
- US-024: Frequent roadmap sync
- US-035: Agent singleton enforcement (CFR-000)
- CFR-011: Architect proactive spec creation
- CFR-012: Agent responsiveness priority

**Enables**:
- US-058+: Future priorities implemented 3-6x faster
- Continuous QA with automatic demos
- Proactive architecture with specs always ready
- Real-time project monitoring
- Weekly codebase improvements

---

## Estimated Timeline

**Week 1: Foundation**
- Day 1-2: Orchestrator base with multi-process management
- Day 3-4: Agent base classes with CFR enforcement
- Day 5: Shared state infrastructure

**Week 2: Agent Migration**
- Day 1-2: Migrate code_developer agent
- Day 3-4: Create architect agent
- Day 5: Create project_manager agent

**Week 3: Completion**
- Day 1-2: Create assistant agent
- Day 3: Create assistant (with code analysis skills) & ux-design-expert agents
- Day 4-5: Integration testing, documentation, deployment

**Total**: 15 working days (3 weeks)

---

## Success Criteria

**The multi-agent orchestrator will be considered successful when**:

1. **All 6 agents running continuously** in parallel subprocesses
2. **architect creates specs proactively** (CFR-011 compliance: 3-5 ahead)
3. **code_developer never blocks** waiting for specs
4. **assistant creates demos automatically** within 30 minutes
5. **project_manager monitors GitHub** continuously
6. **Zero merge conflicts** between agents (CFR-000 compliance)
7. **All agents on roadmap branch** (CFR-013 compliance)
8. **Priority completion time reduced by 50%** (3-6x speedup)
9. **System runs 24 hours without intervention**
10. **User feedback: "This feels like a real team working together"**

---

**Created by**: project_manager agent
**Date**: 2025-10-17
**Status**: 📋 PLANNED (Blocked by US-056)
**Estimated Effort**: 3 weeks
**Expected Impact**: 🚀 TRANSFORMATIONAL (3-6x speedup, true team autonomy)
