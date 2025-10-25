# ACE Framework Implementation - User Stories (US-062 through US-101)

**Created**: 2025-10-18
**Status**: Ready for ROADMAP integration
**Total Stories**: 40 user stories across 7 phases
**Total Estimated Effort**: 185-235 hours (8-12 weeks)

---

## PHASE 1: Foundation - Agent Startup Skills ⭐ HIGHEST PRIORITY

### US-062: Implement code_developer-startup Skill Integration

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST (CFR-007 CRITICAL)

**Estimated Effort**: 10-15 hours (2-3 days)

**User Story**:
As a code_developer agent, I need a startup skill that loads my critical documents automatically, so that I can start work immediately without context budget violations (CFR-007).

**Business Value**:
- **CFR-007 Compliance**: Eliminates 40-60 context budget violations per month
- **Performance**: Reduces startup time from 10-30s to <2s
- **Reliability**: Ensures all required documents loaded before work begins
- **Cost Savings**: Reduces wasted API calls from failed startups

**Technical Spec**: SPEC-063 - Agent Startup Skills Implementation

**Acceptance Criteria**:
- [ ] code_developer automatically executes code_developer-startup skill at initialization
- [ ] Context budget consistently <30% after startup (CFR-007 compliance)
- [ ] Startup completes in <2 seconds
- [ ] All critical documents loaded (ROADMAP, CLAUDE.md, priority specs)
- [ ] Graceful error handling if documents missing or inaccessible
- [ ] Health checks validate API keys, dependencies, file access
- [ ] Unit tests cover normal startup, missing files, large files, permission errors
- [ ] Integration tests verify full daemon startup with skill
- [ ] No regressions in existing daemon functionality

**Deliverables**:
1. Python code in `coffee_maker/autonomous/startup_skills.py`
2. Integration with daemon initialization
3. CFR-007 validation logic
4. Health check system (API keys, dependencies, files)
5. Error diagnostics and logging
6. Unit tests (>90% coverage)
7. Integration tests
8. Documentation in skill markdown file

**Dependencies**:
- code_developer-startup skill exists (.claude/skills/) ✅
- trace-execution skill operational ✅

**Blocked By**: None

**Blocks**:
- US-063 (architect-startup)
- US-064 (project_manager-startup)
- All Phase 2-7 user stories

**architect Code Review**: MANDATORY before deployment

**Related Documents**:
- `.claude/skills/code_developer-startup.md` - Skill definition
- `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` - CFR-007
- `docs/roadmap/ACE_IMPLEMENTATION_PLAN.md` - Phase 1 details
- SPEC-063 - Technical specification

**Success Metrics**:
- CFR-007 violations: 40-60/month → 0/month
- Startup time: 10-30s → <2s
- Context budget at startup: 40-60% → <30%
- Failed startups: 10-15/month → 0/month

---

### US-063: Implement architect-startup Skill Integration

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 10-15 hours (2-3 days)

**User Story**:
As an architect agent, I need a startup skill that loads architectural documentation and specs, so that I can provide informed design decisions immediately without context budget violations.

**Business Value**:
- **CFR-007 Compliance**: Prevents context budget violations
- **Design Quality**: Ensures all relevant specs loaded before architectural decisions
- **Consistency**: Guarantees architect has complete system view
- **Speed**: Faster architectural reviews and spec creation

**Technical Spec**: SPEC-063 - Agent Startup Skills Implementation

**Acceptance Criteria**:
- [ ] architect automatically executes architect-startup skill at initialization
- [ ] Context budget <30% after startup
- [ ] All architectural documents loaded (ADRs, specs, guidelines)
- [ ] Startup completes in <2 seconds
- [ ] Graceful error handling
- [ ] Health checks validate spec directories exist
- [ ] Unit and integration tests
- [ ] No regressions

**Deliverables**:
1. architect startup integration code
2. Document loading logic for architecture docs
3. CFR-007 validation
4. Health checks
5. Tests (unit + integration)
6. Documentation

**Dependencies**:
- US-062 complete (code_developer-startup working)
- architect-startup skill exists ✅

**Blocked By**: US-062

**Blocks**: Phase 3 (US-068, US-069)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Context budget at startup: <30%
- Startup time: <2s
- All specs loaded: 100%

---

### US-064: Implement project_manager-startup Skill Integration

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 10-15 hours (2-3 days)

**User Story**:
As a project_manager agent, I need a startup skill that loads ROADMAP and project status, so that I can provide accurate project insights without context budget violations.

**Business Value**:
- **CFR-007 Compliance**: Prevents violations
- **Accuracy**: Ensures complete ROADMAP context for status reports
- **Speed**: Faster health checks and status queries
- **Reliability**: Consistent project state understanding

**Technical Spec**: SPEC-063 - Agent Startup Skills Implementation

**Acceptance Criteria**:
- [ ] project_manager executes project_manager-startup skill at initialization
- [ ] Context budget <30% after startup
- [ ] ROADMAP, strategic specs, GitHub status loaded
- [ ] Startup completes in <2 seconds
- [ ] Graceful error handling
- [ ] Health checks validate ROADMAP exists and is parseable
- [ ] Unit and integration tests
- [ ] No regressions

**Deliverables**:
1. project_manager startup integration code
2. ROADMAP parsing and loading logic
3. CFR-007 validation
4. Health checks
5. Tests (unit + integration)
6. Documentation

**Dependencies**:
- US-062 complete (code_developer-startup working)
- project_manager-startup skill exists ✅

**Blocked By**: US-062

**Blocks**: Phase 3 (US-070, US-071)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Context budget at startup: <30%
- Startup time: <2s
- ROADMAP load success: 100%

---

## PHASE 2: Core Skills - Developer Support ⭐ HIGHEST PRIORITY

### US-065: Implement test-failure-analysis Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a code_developer agent, I need an automated test failure analysis skill, so that I can quickly categorize pytest failures and get fix recommendations without manual investigation.

**Business Value**:
- **Time Savings**: 20-50 minutes saved per test failure
- **Quality**: 90%+ categorization accuracy
- **Speed**: Faster debugging and fixes
- **Learning**: Builds knowledge base of failure patterns

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <2 minutes for typical pytest output
- [ ] Categorizes failures: syntax error, import error, assertion failure, timeout, etc.
- [ ] Provides fix recommendations for each category
- [ ] 90%+ categorization accuracy on test suite
- [ ] Handles edge cases (no failures, malformed output, etc.)
- [ ] Unit tests cover all failure categories
- [ ] Integration tests with real pytest output
- [ ] Documentation with examples

**Deliverables**:
1. test-failure-analysis skill implementation
2. Categorization logic (regex + pattern matching)
3. Fix recommendation engine
4. Tests (unit + integration)
5. Skill documentation

**Dependencies**: US-062, US-063 (startup skills operational)

**Blocked By**: US-062

**Blocks**: None (parallel with US-066, US-067)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per failure analysis: 20-50 min → 2-3 min
- Categorization accuracy: >90%
- Fix recommendation usefulness: >80% (user survey)

---

### US-066: Implement dod-verification Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a code_developer agent, I need an automated DoD verification skill, so that I can comprehensively check all acceptance criteria before marking priorities complete.

**Business Value**:
- **Time Savings**: 15-35 minutes saved per priority
- **Quality**: 100% DoD coverage, <5% false positives
- **Reliability**: Ensures nothing ships incomplete
- **Documentation**: Generates evidence for completions

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <3 minutes for typical priority
- [ ] Checks all DoD criteria (tests, docs, code quality, security)
- [ ] Generates completion report with evidence
- [ ] <5% false positive rate
- [ ] Handles Puppeteer integration for web testing
- [ ] Unit tests for all criteria types
- [ ] Integration tests with real priorities
- [ ] Documentation with examples

**Deliverables**:
1. dod-verification skill implementation
2. Criteria checking logic (tests, docs, quality, security)
3. Report generation
4. Puppeteer integration
5. Tests (unit + integration)
6. Skill documentation

**Dependencies**: US-062, US-063 (startup skills operational)

**Blocked By**: US-062

**Blocks**: None (parallel with US-065, US-067)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per DoD check: 15-35 min → 2-3 min
- DoD coverage: 100%
- False positives: <5%

---

### US-067: Implement git-workflow-automation Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a code_developer agent, I need automated git workflow skill, so that commits, tags, and PRs follow conventions without manual formatting.

**Business Value**:
- **Time Savings**: 7-12 minutes saved per commit
- **Consistency**: 100% conventional commit compliance
- **Quality**: Automated PR descriptions from commits
- **Traceability**: Links commits to priorities automatically

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <1 minute per commit
- [ ] Generates conventional commit messages (feat:, fix:, docs:, etc.)
- [ ] Creates git tags for milestones (wip-*, dod-verified-*, stable-*)
- [ ] Generates PR descriptions from commit history
- [ ] 100% conventional commit compliance
- [ ] Handles multi-file commits intelligently
- [ ] Unit tests for commit formatting
- [ ] Integration tests with real git repo
- [ ] Documentation with examples

**Deliverables**:
1. git-workflow-automation skill implementation
2. Conventional commit generator
3. Tag creation logic
4. PR description generator
5. Tests (unit + integration)
6. Skill documentation

**Dependencies**: US-062, US-063 (startup skills operational)

**Blocked By**: US-062

**Blocks**: None (parallel with US-065, US-066)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per commit: 7-12 min → <1 min
- Conventional commit compliance: 100%
- PR quality score: >85% (user survey)

---

## PHASE 3: Core Skills - Architect & Project Manager Support ⭐ HIGHEST PRIORITY

### US-068: Implement architecture-reuse-check Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As an architect agent, I need an architecture reuse checking skill, so that I can detect when new specs duplicate existing patterns and suggest reuse.

**Business Value**:
- **Time Savings**: 20-40 minutes saved per spec
- **Consistency**: Encourages pattern reuse
- **Quality**: Reduces architectural drift
- **Documentation**: Automatically links related specs

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <3 minutes for typical spec
- [ ] Detects similar architectural patterns in existing specs
- [ ] Recommends reuse opportunities with confidence scores
- [ ] Generates spec comparison reports
- [ ] >80% detection accuracy for duplicates
- [ ] Unit tests for pattern matching
- [ ] Integration tests with real specs
- [ ] Documentation with examples

**Deliverables**:
1. architecture-reuse-check skill implementation
2. Pattern matching and similarity detection
3. Recommendation engine
4. Comparison report generator
5. Tests (unit + integration)
6. Skill documentation

**Dependencies**: US-063 (architect-startup working)

**Blocked By**: US-063

**Blocks**: None (parallel with US-069, US-070, US-071)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per spec: 20-40 min saved
- Duplicate detection accuracy: >80%
- Reuse adoption rate: >50%

---

### US-069: Implement proactive-refactoring-analysis Skill

**Status**: ✅ Complete

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As an architect agent, I need proactive refactoring analysis skill, so that I can identify code health issues weekly and recommend improvements.

**Business Value**:
- **Code Health**: Weekly automated analysis
- **Proactive**: Catches issues before they become blockers
- **Prioritization**: ROI-scored refactoring recommendations
- **Trending**: Tracks code health over time

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [x] Skill executes in <5 minutes for full codebase
- [x] Analyzes code complexity, duplication, test coverage, dependencies
- [x] Generates weekly health report with scores
- [x] Recommends top 3-5 refactoring priorities with ROI
- [x] Tracks trends week-over-week
- [x] Unit tests for metrics calculation
- [x] Integration tests with real codebase
- [x] Documentation with examples

**Deliverables**:
1. proactive-refactoring-analysis skill implementation
2. Code health metrics (complexity, duplication, coverage)
3. ROI calculation for refactorings
4. Weekly report generator
5. Trend tracking
6. Tests (unit + integration)
7. Skill documentation

**Dependencies**: US-063 (architect-startup working)

**Blocked By**: US-063

**Blocks**: None (parallel with US-068, US-070, US-071)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Analysis time: <5 min/week
- Recommendation accuracy: >80% adoption
- Code health trend: Improving over time

---

### US-070: Implement roadmap-health-check Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As a project_manager agent, I need ROADMAP health check skill, so that I can quickly analyze priorities, velocity, and blockers without manual review.

**Business Value**:
- **Time Savings**: 17-27 minutes saved per health check
- **Proactive**: Daily/weekly automated checks
- **Accuracy**: Consistent metrics calculation
- **Visibility**: Clear health scoring and trends

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <2 minutes for full ROADMAP
- [ ] Calculates health score (0-100)
- [ ] Analyzes velocity (priorities/week)
- [ ] Detects blockers and dependencies
- [ ] Generates actionable recommendations
- [ ] Daily/weekly scheduling
- [ ] Unit tests for metrics
- [ ] Integration tests with real ROADMAP
- [ ] Documentation with examples

**Deliverables**:
1. roadmap-health-check skill implementation
2. Health scoring algorithm
3. Velocity calculation
4. Blocker detection
5. Recommendation engine
6. Scheduling integration
7. Tests (unit + integration)
8. Skill documentation

**Dependencies**: US-064 (project_manager-startup working)

**Blocked By**: US-064

**Blocks**: None (parallel with US-068, US-069, US-071)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per health check: 17-27 min → 2-3 min
- Check frequency: Weekly → Daily
- Blocker detection rate: >90%

---

### US-071: Implement pr-monitoring-analysis Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐⭐ HIGHEST

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As a project_manager agent, I need PR monitoring skill, so that I can track GitHub PRs, CI status, and blockers without manual checking.

**Business Value**:
- **Time Savings**: 12-15 minutes saved per PR check
- **Proactive**: Automated blocker detection
- **Visibility**: Real-time CI/CD status
- **Integration**: Links PRs to ROADMAP priorities

**Technical Spec**: Referenced in SPEC-063

**Acceptance Criteria**:
- [ ] Skill executes in <1 minute per check
- [ ] Monitors open PRs with `gh` CLI
- [ ] Checks CI/CD status (passing/failing)
- [ ] Detects blockers (review needed, tests failing)
- [ ] Links PRs to ROADMAP priorities
- [ ] Generates status report
- [ ] Unit tests for GitHub API integration
- [ ] Integration tests with real PRs
- [ ] Documentation with examples

**Deliverables**:
1. pr-monitoring-analysis skill implementation
2. GitHub CLI integration (`gh pr list`, `gh pr checks`)
3. Blocker detection logic
4. Priority linking
5. Status report generator
6. Tests (unit + integration)
7. Skill documentation

**Dependencies**: US-064 (project_manager-startup working)

**Blocked By**: US-064

**Blocks**: None (parallel with US-068, US-069, US-070)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time per PR check: 12-15 min → <1 min
- Blocker detection accuracy: >95%
- Check frequency: Manual → Hourly automated

---

## PHASE 4: Orchestrator Agent ⭐ HIGH PRIORITY

### US-072: Design Orchestrator Agent Architecture

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 8-10 hours (2 days)

**User Story**:
As a system architect, I need a comprehensive orchestrator agent design, so that we have a clear blueprint for multi-agent coordination.

**Business Value**:
- **Architecture Clarity**: Clear design before implementation
- **Risk Mitigation**: Identifies challenges early
- **Quality**: Ensures thread safety, security, scalability
- **Alignment**: User approval before costly development

**Technical Spec**: SPEC-062 - Orchestrator Agent Architecture

**Acceptance Criteria**:
- [ ] Architecture document created (SPEC-062)
- [ ] Message bus design (pub/sub pattern)
- [ ] Performance monitoring design
- [ ] Workflow optimization design
- [ ] Thread safety analysis
- [ ] Security considerations documented
- [ ] User approval obtained
- [ ] architect code review complete

**Deliverables**:
1. Updated SPEC-062 with detailed design
2. Architecture diagrams (message bus, data flow)
3. API specifications
4. Security analysis
5. Performance requirements
6. Implementation plan

**Dependencies**: Phase 1-3 complete (agents have startup skills)

**Blocked By**: US-062, US-063, US-064

**Blocks**: US-073, US-074, US-075, US-076, US-077

**architect Code Review**: CRITICAL

**Success Metrics**:
- User approval: Yes
- Design completeness: 100%
- Risks identified: All documented

---

### US-073: Implement Message Bus (Pub/Sub Pattern)

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 10-12 hours (2-3 days)

**User Story**:
As an orchestrator agent, I need a message bus for agent coordination, so that agents can communicate asynchronously without tight coupling.

**Business Value**:
- **Coordination**: Enables multi-agent workflows
- **Decoupling**: Reduces inter-agent dependencies
- **Scalability**: Supports parallel agent execution
- **Reliability**: Graceful handling of agent failures

**Technical Spec**: SPEC-062 - Orchestrator Agent Architecture

**Acceptance Criteria**:
- [ ] Message bus implemented with pub/sub pattern
- [ ] Subscribe/publish API for agents
- [ ] Message routing and filtering
- [ ] Message persistence (optional queue)
- [ ] Latency <50ms p95
- [ ] No message loss under normal conditions
- [ ] Thread-safe implementation
- [ ] Unit tests for pub/sub logic
- [ ] Integration tests with multiple agents
- [ ] Documentation with examples

**Deliverables**:
1. Message bus implementation
2. Pub/sub API
3. Message routing logic
4. Persistence layer (optional)
5. Tests (unit + integration)
6. Documentation

**Dependencies**: US-072 (design approved)

**Blocked By**: US-072

**Blocks**: US-074, US-075

**architect Code Review**: CRITICAL (thread safety, security)

**Success Metrics**:
- Message latency: <50ms p95
- Message loss rate: <0.01%
- Agent coupling: Reduced

---

### US-074: Implement Performance Monitor

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As an orchestrator agent, I need performance monitoring, so that I can detect bottlenecks and optimize workflows.

**Business Value**:
- **Visibility**: Real-time workflow metrics
- **Optimization**: Identifies slow agents/tasks
- **Reliability**: Detects degradation early
- **Reporting**: Historical performance data

**Technical Spec**: SPEC-062 - Orchestrator Agent Architecture

**Acceptance Criteria**:
- [ ] Monitors agent response times
- [ ] Tracks message queue metrics
- [ ] Detects bottlenecks (>90% accuracy)
- [ ] Generates performance dashboard
- [ ] Historical data retention (30 days)
- [ ] Unit tests for metrics collection
- [ ] Integration tests with workflows
- [ ] Documentation with examples

**Deliverables**:
1. Performance monitoring implementation
2. Metrics collection (response time, queue depth)
3. Bottleneck detection algorithm
4. Dashboard/reporting
5. Data persistence
6. Tests (unit + integration)
7. Documentation

**Dependencies**: US-073 (message bus working)

**Blocked By**: US-073

**Blocks**: US-075

**architect Code Review**: MANDATORY

**Success Metrics**:
- Bottleneck detection: >90% accuracy
- Monitoring overhead: <5% CPU
- Dashboard load time: <1s

---

### US-075: Implement Workflow Optimizer

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 8-10 hours (2 days)

**User Story**:
As an orchestrator agent, I need workflow optimization, so that I can parallelize independent tasks and reduce total execution time.

**Business Value**:
- **Speed**: 40-50% reduction in workflow time
- **Efficiency**: Maximizes parallel execution
- **Intelligence**: Dependency analysis
- **Cost**: Reduced API usage from faster execution

**Technical Spec**: SPEC-062 - Orchestrator Agent Architecture

**Acceptance Criteria**:
- [ ] Dependency analysis for tasks
- [ ] Parallel execution of independent tasks
- [ ] Workflow time reduced by 40%+
- [ ] No deadlocks or race conditions
- [ ] Graceful degradation on agent failures
- [ ] Unit tests for dependency analysis
- [ ] Integration tests with real workflows
- [ ] Documentation with examples

**Deliverables**:
1. Workflow optimizer implementation
2. Dependency analysis algorithm
3. Parallel execution engine
4. Deadlock prevention
5. Failure handling
6. Tests (unit + integration)
7. Documentation

**Dependencies**: US-073, US-074 (message bus + monitoring)

**Blocked By**: US-073, US-074

**Blocks**: US-076

**architect Code Review**: CRITICAL (race conditions, deadlocks)

**Success Metrics**:
- Workflow time reduction: >40%
- Parallelization efficiency: >80%
- Deadlocks: 0

---

### US-076: Create orchestrator-startup Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As an orchestrator agent, I need a startup skill, so that I can load system state and agent configurations efficiently.

**Business Value**:
- **CFR-007 Compliance**: Prevents context violations
- **Reliability**: Ensures complete system view at startup
- **Speed**: Fast orchestrator initialization
- **Consistency**: Repeatable startup process

**Technical Spec**: SPEC-063 (adapted for orchestrator)

**Acceptance Criteria**:
- [ ] orchestrator-startup skill created
- [ ] Loads agent registry, message bus state, workflows
- [ ] Context budget <30% after startup
- [ ] Startup time <2 seconds
- [ ] Health checks for all agents
- [ ] Unit and integration tests
- [ ] Documentation

**Deliverables**:
1. orchestrator-startup skill
2. State loading logic
3. Health check system
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-072, US-073, US-074, US-075

**Blocked By**: US-075

**Blocks**: US-077

**architect Code Review**: MANDATORY

**Success Metrics**:
- Startup time: <2s
- Context budget: <30%
- Health check coverage: 100%

---

### US-077: Integrate Orchestrator with Existing Agents

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As a system integrator, I need orchestrator integration with existing agents, so that multi-agent workflows work seamlessly.

**Business Value**:
- **Coordination**: Enables complex multi-agent tasks
- **Reliability**: Ensures graceful failures
- **Performance**: Validates 40% time reduction
- **Quality**: No regressions in existing functionality

**Technical Spec**: SPEC-062 - Orchestrator Agent Architecture

**Acceptance Criteria**:
- [ ] All agents register with orchestrator
- [ ] Message bus communication working
- [ ] Workflows execute with 40%+ time reduction
- [ ] No regressions in existing agent functionality
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] User acceptance testing

**Deliverables**:
1. Integration code for all agents
2. Registration logic
3. Migration guide
4. Integration tests
5. Documentation updates
6. User acceptance test results

**Dependencies**: US-076 (orchestrator-startup ready)

**Blocked By**: US-076

**Blocks**: None (Phase 4 complete)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Workflow time reduction: >40%
- Integration test pass rate: 100%
- User satisfaction: >85%

---

## PHASE 5A: ACE Framework - Reflector Agent ⭐ HIGH PRIORITY

### US-078: Design Reflector Agent Architecture

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As an architect, I need Reflector agent architecture design, so that we have a clear blueprint for trace analysis and insight extraction.

**Business Value**:
- **Architecture Clarity**: Clear design before implementation
- **ACE Vision**: Brings us closer to full ACE framework
- **Quality**: Ensures robust pattern detection
- **Alignment**: User approval before development

**Technical Spec**: SPEC-065 - Reflector Agent Implementation

**Acceptance Criteria**:
- [ ] Architecture document created/updated (SPEC-065)
- [ ] Trace analysis design
- [ ] Pattern detection algorithm design
- [ ] Delta item creation workflow
- [ ] Scheduling mechanism design
- [ ] User approval obtained
- [ ] architect code review complete

**Deliverables**:
1. Updated SPEC-065 with detailed design
2. Architecture diagrams
3. API specifications
4. Algorithm descriptions
5. Implementation plan

**Dependencies**: Phase 1 complete (trace-execution skill generating traces)

**Blocked By**: US-062 (trace-execution needs startup skills)

**Blocks**: US-079, US-080, US-081, US-082, US-083

**architect Code Review**: MANDATORY

**Success Metrics**:
- User approval: Yes
- Design completeness: 100%

---

### US-079: Implement Trace Analysis Logic

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a Reflector agent, I need trace analysis logic, so that I can process execution traces and extract structured data.

**Business Value**:
- **Automation**: Analyzes 24 hours of traces in <2 minutes
- **Scalability**: Handles growing trace volumes
- **Quality**: Structured data for pattern detection
- **Foundation**: Enables insight extraction

**Technical Spec**: SPEC-065 - Reflector Agent Implementation

**Acceptance Criteria**:
- [ ] Parses trace files from docs/generator/
- [ ] Extracts agent, action, duration, outcome, context
- [ ] Handles malformed traces gracefully
- [ ] Processes 24 hours in <2 minutes
- [ ] Unit tests for parsing logic
- [ ] Integration tests with real traces
- [ ] Documentation

**Deliverables**:
1. Trace parsing implementation
2. Data extraction logic
3. Error handling
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-078 (design approved)

**Blocked By**: US-078

**Blocks**: US-080

**architect Code Review**: MANDATORY

**Success Metrics**:
- Processing time: <2 min for 24 hours
- Parse success rate: >95%

---

### US-080: Implement Pattern Detection Algorithms

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As a Reflector agent, I need pattern detection algorithms, so that I can identify successful patterns, failures, bottlenecks, and anti-patterns.

**Business Value**:
- **Intelligence**: 85%+ detection accuracy
- **Insights**: Discovers optimization opportunities
- **Learning**: Builds organizational knowledge
- **Actionable**: Generates specific recommendations

**Technical Spec**: SPEC-065 - Reflector Agent Implementation

**Acceptance Criteria**:
- [ ] Detects 4 pattern types: success, failure, bottleneck, anti-pattern
- [ ] Confidence scoring (0-100)
- [ ] Evidence tracking (trace references)
- [ ] 85%+ detection accuracy
- [ ] Unit tests for each pattern type
- [ ] Integration tests with real traces
- [ ] Documentation with examples

**Deliverables**:
1. Pattern detection algorithms (4 types)
2. Confidence scoring logic
3. Evidence collection
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-079 (trace analysis working)

**Blocked By**: US-079

**Blocks**: US-081

**architect Code Review**: MANDATORY (algorithm quality)

**Success Metrics**:
- Detection accuracy: >85%
- False positive rate: <15%

---

### US-081: Implement Delta Item Creation

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As a Reflector agent, I need delta item creation, so that I can document insights in structured format for Curator.

**Business Value**:
- **Documentation**: Preserves insights permanently
- **Curator Input**: Feeds Curator agent
- **Traceability**: Links insights to evidence
- **Knowledge**: Builds organizational memory

**Technical Spec**: SPEC-065 - Reflector Agent Implementation

**Acceptance Criteria**:
- [ ] Creates delta items in docs/reflector/
- [ ] Structured format: pattern type, confidence, evidence, recommendation
- [ ] Unique IDs for tracking
- [ ] Timestamps for chronology
- [ ] Unit tests for item creation
- [ ] Integration tests with pattern detection
- [ ] Documentation

**Deliverables**:
1. Delta item creation logic
2. File writing and formatting
3. ID generation
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-080 (pattern detection working)

**Blocked By**: US-080

**Blocks**: US-082

**architect Code Review**: MANDATORY

**Success Metrics**:
- Items created: 100% of patterns
- Format compliance: 100%

---

### US-082: Create Reflector Scheduling Mechanism

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 3-5 hours (0.5-1 day)

**User Story**:
As a Reflector agent, I need automated scheduling, so that I run daily without manual intervention.

**Business Value**:
- **Automation**: Daily analysis without human input
- **Consistency**: Regular insight generation
- **Reliability**: Cron-based scheduling
- **Scalability**: Handles growing trace volumes

**Technical Spec**: SPEC-065 - Reflector Agent Implementation

**Acceptance Criteria**:
- [ ] Cron job configured (daily 2am)
- [ ] Runs automatically via scheduler
- [ ] Logs execution results
- [ ] Error notifications on failures
- [ ] Unit tests for scheduling logic
- [ ] Integration tests with cron
- [ ] Documentation

**Deliverables**:
1. Cron configuration
2. Scheduler integration
3. Logging and notifications
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-081 (delta item creation working)

**Blocked By**: US-081

**Blocks**: US-083

**architect Code Review**: MANDATORY

**Success Metrics**:
- Daily execution: 100%
- Failures: <1%

---

### US-083: Create reflector-startup Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 3-5 hours (0.5-1 day)

**User Story**:
As a Reflector agent, I need a startup skill, so that I can load trace history and configuration efficiently.

**Business Value**:
- **CFR-007 Compliance**: Prevents context violations
- **Reliability**: Ensures complete data at startup
- **Speed**: Fast Reflector initialization
- **Consistency**: Repeatable startup

**Technical Spec**: SPEC-063 (adapted for Reflector)

**Acceptance Criteria**:
- [ ] reflector-startup skill created
- [ ] Loads trace files, delta items, configuration
- [ ] Context budget <30% after startup
- [ ] Startup time <2 seconds
- [ ] Health checks for trace directory
- [ ] Unit and integration tests
- [ ] Documentation

**Deliverables**:
1. reflector-startup skill
2. Data loading logic
3. Health checks
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-082 (scheduling working)

**Blocked By**: US-082

**Blocks**: None (Phase 5A complete)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Startup time: <2s
- Context budget: <30%

---

## PHASE 5B: ACE Framework - Curator Agent ⭐ HIGH PRIORITY

### US-084: Design Curator Agent Architecture

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As an architect, I need Curator agent architecture design, so that we have a clear blueprint for delta synthesis and playbook evolution.

**Business Value**:
- **Architecture Clarity**: Clear design before implementation
- **ACE Vision**: Completes core ACE framework
- **Quality**: Ensures robust synthesis logic
- **Alignment**: User approval before development

**Technical Spec**: SPEC-066 - Curator Agent Implementation

**Acceptance Criteria**:
- [ ] Architecture document created/updated (SPEC-066)
- [ ] Delta synthesis design
- [ ] ROI calculation design
- [ ] Playbook generation workflow
- [ ] Skill recommendation engine design
- [ ] User approval obtained
- [ ] architect code review complete

**Deliverables**:
1. Updated SPEC-066 with detailed design
2. Architecture diagrams
3. API specifications
4. Algorithm descriptions
5. Implementation plan

**Dependencies**: Phase 5A complete (Reflector generating delta items)

**Blocked By**: US-083

**Blocks**: US-085, US-086, US-087, US-088, US-089

**architect Code Review**: MANDATORY

**Success Metrics**:
- User approval: Yes
- Design completeness: 100%

---

### US-085: Implement Delta Item Synthesis

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As a Curator agent, I need delta synthesis logic, so that I can combine related insights into cohesive themes.

**Business Value**:
- **Intelligence**: Discovers meta-patterns
- **Efficiency**: Processes 100 deltas in <5 minutes
- **Quality**: 80%+ theme clustering accuracy
- **Foundation**: Enables playbook generation

**Technical Spec**: SPEC-066 - Curator Agent Implementation

**Acceptance Criteria**:
- [ ] Reads delta items from docs/reflector/
- [ ] Clusters related insights by theme
- [ ] 80%+ clustering accuracy
- [ ] Processes 100 items in <5 minutes
- [ ] Unit tests for clustering
- [ ] Integration tests with real deltas
- [ ] Documentation

**Deliverables**:
1. Delta synthesis implementation
2. Clustering algorithm
3. Theme detection
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-084 (design approved)

**Blocked By**: US-084

**Blocks**: US-086

**architect Code Review**: MANDATORY

**Success Metrics**:
- Processing time: <5 min for 100 items
- Clustering accuracy: >80%

---

### US-086: Implement ROI Calculation Engine

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a Curator agent, I need ROI calculation, so that I can prioritize skill recommendations by business value.

**Business Value**:
- **Prioritization**: Focus on high-impact skills
- **Justification**: Data-driven decisions
- **Accuracy**: ROI estimates within 20% of actual
- **Alignment**: Links skills to business goals

**Technical Spec**: SPEC-066 - Curator Agent Implementation

**Acceptance Criteria**:
- [ ] Calculates time savings from delta items
- [ ] Estimates implementation cost
- [ ] Computes ROI (savings / cost)
- [ ] Accuracy within 20% of manual estimates
- [ ] Unit tests for ROI logic
- [ ] Integration tests with real deltas
- [ ] Documentation

**Deliverables**:
1. ROI calculation implementation
2. Time savings estimation
3. Cost estimation
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-085 (synthesis working)

**Blocked By**: US-085

**Blocks**: US-087

**architect Code Review**: MANDATORY (algorithm quality)

**Success Metrics**:
- ROI accuracy: Within 20% of manual
- Calculation time: <1 min

---

### US-087: Implement Playbook Generation

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As a Curator agent, I need playbook generation, so that I can create actionable documentation for skill creation.

**Business Value**:
- **Actionable**: Clear steps for skill implementation
- **Knowledge**: Preserves organizational learning
- **Evolution**: Playbooks evolve over time
- **Guidance**: Informs future development

**Technical Spec**: SPEC-066 - Curator Agent Implementation

**Acceptance Criteria**:
- [ ] Generates playbooks in docs/curator/
- [ ] Structured format: theme, insights, recommendations, ROI
- [ ] Links to supporting delta items
- [ ] Versioned playbooks (track evolution)
- [ ] Unit tests for generation logic
- [ ] Integration tests with real deltas
- [ ] Documentation

**Deliverables**:
1. Playbook generation implementation
2. Template system
3. Versioning logic
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-086 (ROI calculation working)

**Blocked By**: US-086

**Blocks**: US-088

**architect Code Review**: MANDATORY

**Success Metrics**:
- Playbooks generated: 3-5/month
- Quality score: >85% (user survey)

---

### US-088: Implement Skill Recommendation Engine

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 5-7 hours (1-1.5 days)

**User Story**:
As a Curator agent, I need skill recommendations, so that I can suggest high-ROI skills for implementation.

**Business Value**:
- **Strategic**: Prioritizes skill development
- **Data-Driven**: Based on actual execution data
- **ROI-Focused**: Maximizes business value
- **Actionable**: Clear next steps

**Technical Spec**: SPEC-066 - Curator Agent Implementation

**Acceptance Criteria**:
- [ ] Recommends 3-5 skills per playbook
- [ ] Each with ROI, priority, implementation plan
- [ ] Categorizes: create new, modify existing, deprecate old
- [ ] ROI accuracy within 20%
- [ ] Unit tests for recommendation logic
- [ ] Integration tests with playbooks
- [ ] Documentation

**Deliverables**:
1. Recommendation engine implementation
2. Prioritization algorithm
3. Implementation plan generator
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-087 (playbook generation working)

**Blocked By**: US-087

**Blocks**: US-089

**architect Code Review**: MANDATORY

**Success Metrics**:
- Recommendations per month: 3-5
- ROI accuracy: Within 20%
- Adoption rate: >50%

---

### US-089: Create curator-startup Skill

**Status**: 📝 Planned

**Priority Level**: ⭐⭐ HIGH

**Estimated Effort**: 3-5 hours (0.5-1 day)

**User Story**:
As a Curator agent, I need a startup skill, so that I can load delta items and playbook history efficiently.

**Business Value**:
- **CFR-007 Compliance**: Prevents context violations
- **Reliability**: Ensures complete data at startup
- **Speed**: Fast Curator initialization
- **Consistency**: Repeatable startup

**Technical Spec**: SPEC-063 (adapted for Curator)

**Acceptance Criteria**:
- [ ] curator-startup skill created
- [ ] Loads delta items, playbooks, configuration
- [ ] Context budget <30% after startup
- [ ] Startup time <2 seconds
- [ ] Health checks for data directories
- [ ] Unit and integration tests
- [ ] Documentation

**Deliverables**:
1. curator-startup skill
2. Data loading logic
3. Health checks
4. Tests (unit + integration)
5. Documentation

**Dependencies**: US-088 (recommendations working)

**Blocked By**: US-088

**Blocks**: None (Phase 5B complete)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Startup time: <2s
- Context budget: <30%

---

## PHASE 6: Code-Searcher Migration 🔄 MEDIUM PRIORITY

### US-090: Create 5 Code Analysis Skills

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 12-15 hours (2.5-3 days)

**User Story**:
As an architect and code_developer, I need 5 code analysis skills (code-forensics, security-audit, dependency-tracer, functional-search, code-explainer), so that I can perform code analysis 50-150x faster than the assistant agent (with code analysis skills).

**Business Value**:
- **Performance**: 10-30s agent time → 200ms skill time
- **Scalability**: No context budget overhead
- **Reliability**: Consistent, repeatable results
- **Foundation**: Enables assistant (with code analysis skills) retirement

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] 5 skills created: code-forensics, security-audit, dependency-tracer, functional-search, code-explainer
- [ ] Each skill executes in <200ms
- [ ] Code index built for fast lookups
- [ ] Quality matches or exceeds assistant (with code analysis skills)
- [ ] Unit tests for each skill
- [ ] Integration tests with real codebase
- [ ] Documentation with examples

**Deliverables**:
1. 5 skill implementations
2. Code index (AST-based, full-text search)
3. Sub-second lookup system
4. Tests (unit + integration) for each skill
5. Documentation

**Dependencies**: Phase 1-3 complete (skills system operational)

**Blocked By**: US-062, US-063, US-064

**Blocks**: US-091, US-092, US-093

**architect Code Review**: MANDATORY (skills design)

**Success Metrics**:
- Execution time: <200ms per skill
- Quality: ≥assistant (with code analysis skills)
- Coverage: 100% of assistant (with code analysis skills) capabilities

---

### US-091: Build Code Index for Fast Skill Execution

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 4-6 hours (1 day)

**User Story**:
As a skills developer, I need a code index, so that code analysis skills can perform sub-second lookups.

**Business Value**:
- **Performance**: Enables <200ms skill execution
- **Scalability**: Handles large codebases
- **Quality**: AST-based for accuracy
- **Maintenance**: Incremental updates

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] Index built from codebase (AST + full-text)
- [ ] Sub-second lookups
- [ ] Incremental updates on file changes
- [ ] Persistent storage
- [ ] Unit tests for indexing logic
- [ ] Integration tests with skills
- [ ] Documentation

**Deliverables**:
1. Code indexing implementation
2. AST parser integration
3. Full-text search index
4. Incremental update system
5. Persistence layer
6. Tests (unit + integration)
7. Documentation

**Dependencies**: US-090 (skills created)

**Blocked By**: US-090

**Blocks**: US-092, US-093

**architect Code Review**: MANDATORY

**Success Metrics**:
- Lookup time: <200ms
- Index build time: <30s for full codebase
- Update time: <1s per file change

---

### US-092: Migrate assistant (with code analysis skills) Responsibilities to architect

**Status**: �v Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 3-5 hours (0.5-1 day)

**User Story**:
As an architect agent, I need assistant (with code analysis skills) responsibilities migrated to me, so that I can perform architectural code analysis using skills.

**Business Value**:
- **Clarity**: Clear ownership boundaries
- **Performance**: Uses fast skills instead of agent
- **Simplicity**: Fewer agents to orchestrate
- **Maintainability**: Single agent for architecture

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] architect.md updated with code analysis responsibilities
- [ ] architect uses code analysis skills
- [ ] All architectural use cases covered
- [ ] Integration tests with architect
- [ ] Documentation updated
- [ ] No regressions

**Deliverables**:
1. Updated .claude/agents/architect.md
2. Integration code for skills
3. Migration guide
4. Integration tests
5. Documentation updates

**Dependencies**: US-090, US-091 (skills + index ready)

**Blocked By**: US-090, US-091

**Blocks**: US-094

**architect Code Review**: MANDATORY

**Success Metrics**:
- architect speed: 50-150x faster
- Quality: No regressions
- Coverage: 100% of use cases

---

### US-093: Migrate assistant (with code analysis skills) Responsibilities to code_developer

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 3-5 hours (0.5-1 day)

**User Story**:
As a code_developer agent, I need assistant (with code analysis skills) responsibilities migrated to me, so that I can perform implementation code analysis using skills.

**Business Value**:
- **Performance**: Uses fast skills
- **Ownership**: Clear implementation boundaries
- **Simplicity**: Fewer agent handoffs
- **Speed**: Faster debugging and implementation

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] code_developer.md updated with code analysis responsibilities
- [ ] code_developer uses code analysis skills
- [ ] All implementation use cases covered
- [ ] Integration tests with code_developer
- [ ] Documentation updated
- [ ] No regressions

**Deliverables**:
1. Updated .claude/agents/code_developer.md
2. Integration code for skills
3. Migration guide
4. Integration tests
5. Documentation updates

**Dependencies**: US-090, US-091 (skills + index ready)

**Blocked By**: US-090, US-091

**Blocks**: US-094

**architect Code Review**: MANDATORY

**Success Metrics**:
- code_developer speed: 50-150x faster
- Quality: No regressions
- Coverage: 100% of use cases

---

### US-094: Transition Period - Validate Migration (3 Weeks)

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 2-4 hours monitoring (spread over 3 weeks)

**User Story**:
As a project_manager, I need a 3-week transition period, so that we can validate skills work correctly before retiring assistant (with code analysis skills).

**Business Value**:
- **Risk Mitigation**: Catch issues before permanent retirement
- **Rollback Option**: Can revert if problems found
- **Validation**: Ensures no functionality loss
- **Confidence**: User acceptance before completion

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] 3 weeks elapsed since migration
- [ ] All code analysis use cases tested
- [ ] Skills performance validated (50-150x faster)
- [ ] No quality regressions detected
- [ ] User acceptance obtained
- [ ] Rollback plan ready (if needed)

**Deliverables**:
1. Transition monitoring reports (weekly)
2. Issue log (if any)
3. Performance benchmarks
4. User acceptance sign-off
5. Rollback plan (documented, not executed)

**Dependencies**: US-092, US-093 (migrations complete)

**Blocked By**: US-092, US-093

**Blocks**: US-095, US-096

**architect Code Review**: Not required (monitoring activity)

**Success Metrics**:
- Issues found: 0 critical
- Performance: 50-150x improvement confirmed
- User satisfaction: >90%

---

### US-095: Retire assistant (with code analysis skills) Agent

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 2-3 hours (0.5 day)

**User Story**:
As a project_manager, I need to retire assistant agent (with code analysis skills), so that we reduce agent count from 6 to 5 and simplify the system.

**Business Value**:
- **Simplicity**: 6 agents → 5 agents
- **Clarity**: Clear responsibility boundaries
- **Performance**: All analysis now 50-150x faster
- **Maintainability**: Fewer agents to orchestrate

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] assistant (with code analysis skills).md moved to archive
- [ ] Agent registry updated (remove assistant (with code analysis skills))
- [ ] All references to assistant (with code analysis skills) updated
- [ ] Documentation reflects retirement
- [ ] No broken workflows
- [ ] User announcement

**Deliverables**:
1. Archive .claude/agents/assistant (with code analysis skills).md
2. Update agent registry
3. Update all documentation
4. Retirement announcement
5. Final validation

**Dependencies**: US-094 (transition period complete)

**Blocked By**: US-094

**Blocks**: US-096

**architect Code Review**: MANDATORY (ensure complete)

**Success Metrics**:
- Agent count: 6 → 5
- Broken workflows: 0
- User acceptance: Yes

---

### US-096: Archive assistant (with code analysis skills).md

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 1 hour

**User Story**:
As a project_manager, I need assistant (with code analysis skills).md archived properly, so that we preserve history and rationale.

**Business Value**:
- **History**: Preserves agent evolution
- **Learning**: Future reference for agent-to-skill patterns
- **Compliance**: Maintains documentation completeness
- **Knowledge**: Why and how decisions were made

**Technical Spec**: SPEC-064 - Code-Searcher Responsibility Migration

**Acceptance Criteria**:
- [ ] assistant (with code analysis skills).md moved to .claude/agents/archive/
- [ ] Archive README explains retirement
- [ ] Retirement date and rationale documented
- [ ] Links to replacement skills
- [ ] Git history preserved

**Deliverables**:
1. .claude/agents/archive/assistant (with code analysis skills).md
2. Archive README with context
3. Documentation links updated
4. Git commit with clear message

**Dependencies**: US-095 (retirement complete)

**Blocked By**: US-095

**Blocks**: None (Phase 6 complete)

**architect Code Review**: Not required (documentation)

**Success Metrics**:
- Archive complete: Yes
- Documentation quality: High
- Discoverability: Easy to find

---

## PHASE 7: Advanced Skills 📈 MEDIUM PRIORITY

### US-097: Implement spec-creation-automation Skill

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM-HIGH

**Estimated Effort**: 8-10 hours (2 days)

**User Story**:
As an architect agent, I need spec creation automation skill, so that I can generate 80% of spec content automatically from priorities and requirements.

**Business Value**:
- **Time Savings**: 23-30.7 hours saved per month
- **Quality**: Consistent spec structure and completeness
- **Speed**: Faster spec turnaround
- **ROI**: 12-19x in first year

**Technical Spec**: SPEC-061 - Spec Creation Automation (already exists)

**Acceptance Criteria**:
- [ ] Skill executes in <3 minutes per spec
- [ ] Generates 80%+ of spec content
- [ ] Follows spec template structure
- [ ] Includes architecture diagrams (placeholder)
- [ ] Unit tests for generation logic
- [ ] Integration tests with real priorities
- [ ] Documentation with examples

**Deliverables**:
1. spec-creation-automation skill implementation
2. Template system
3. Content generation logic
4. Diagram placeholder system
5. Tests (unit + integration)
6. Documentation

**Dependencies**: Phase 1-3 complete, US-063 (architect-startup)

**Blocked By**: US-063

**Blocks**: None (parallel with US-098, US-099)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time savings: 23-30.7 hrs/month
- Content coverage: >80%
- Quality score: >85% (user survey)

---

### US-098: Implement context-budget-optimizer Skill

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM-HIGH

**Estimated Effort**: 10-12 hours (2-3 days)

**User Story**:
As any agent, I need context budget optimization skill, so that I can automatically select critical documents and stay under 30% context budget (CFR-007).

**Business Value**:
- **Time Savings**: 26.7-40 hours saved per month
- **CFR-007**: Ensures compliance automatically
- **Intelligence**: Learns document importance over time
- **ROI**: 12-19x in first year

**Technical Spec**: SPEC-102 - Context Budget Optimizer (to be created)

**Acceptance Criteria**:
- [ ] Skill executes in <1 minute
- [ ] Selects documents to stay <30% budget
- [ ] Prioritizes by relevance and frequency
- [ ] Learns from usage patterns
- [ ] Integration with all agents
- [ ] Unit tests for selection logic
- [ ] Integration tests with agents
- [ ] Documentation

**Deliverables**:
1. SPEC-102 technical specification
2. context-budget-optimizer skill implementation
3. Document selection algorithm
4. Learning system (usage tracking)
5. Agent integration
6. Tests (unit + integration)
7. Documentation

**Dependencies**: Phase 1 complete (startup skills operational)

**Blocked By**: US-062, US-063, US-064

**Blocks**: None (parallel with US-097, US-099)

**architect Code Review**: MANDATORY (algorithm quality)

**Success Metrics**:
- Time savings: 26.7-40 hrs/month
- CFR-007 compliance: 100%
- Selection accuracy: >90%

---

### US-099: Implement dependency-conflict-resolver Skill

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As an architect agent, I need dependency conflict resolution skill, so that I can automatically detect and resolve poetry dependency conflicts.

**Business Value**:
- **Time Savings**: 3.3-5 hours saved per month
- **Reliability**: Prevents dependency hell
- **Automation**: No manual conflict resolution
- **ROI**: 12-19x in first year

**Technical Spec**: SPEC-103 - Dependency Conflict Resolver (to be created)

**Acceptance Criteria**:
- [ ] Skill executes in <2 minutes
- [ ] Detects conflicts in pyproject.toml
- [ ] Proposes resolution strategies
- [ ] Tests resolutions before applying
- [ ] Unit tests for conflict detection
- [ ] Integration tests with poetry
- [ ] Documentation

**Deliverables**:
1. SPEC-103 technical specification
2. dependency-conflict-resolver skill implementation
3. Conflict detection logic
4. Resolution strategies
5. Testing system
6. Tests (unit + integration)
7. Documentation

**Dependencies**: US-063 (architect-startup)

**Blocked By**: US-063

**Blocks**: None (parallel with US-097, US-098)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time savings: 3.3-5 hrs/month
- Conflict resolution success: >90%
- False positives: <10%

---

### US-100: Implement async-workflow-coordinator Skill

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 8-10 hours (2 days)

**User Story**:
As an orchestrator agent, I need async workflow coordination skill, so that I can optimize parallel task execution across multiple agents.

**Business Value**:
- **Time Savings**: 5-10 hours saved per month
- **Performance**: 30-50% faster multi-agent workflows
- **Intelligence**: Learns optimal task scheduling
- **ROI**: 12-19x in first year

**Technical Spec**: SPEC-104 - Async Workflow Coordinator (to be created)

**Acceptance Criteria**:
- [ ] Skill executes in <30 seconds for workflow analysis
- [ ] Identifies parallelization opportunities
- [ ] Schedules tasks optimally
- [ ] 30-50% workflow time reduction
- [ ] Unit tests for scheduling logic
- [ ] Integration tests with orchestrator
- [ ] Documentation

**Deliverables**:
1. SPEC-104 technical specification
2. async-workflow-coordinator skill implementation
3. Parallelization detection
4. Task scheduling algorithm
5. Orchestrator integration
6. Tests (unit + integration)
7. Documentation

**Dependencies**: Phase 4 complete (orchestrator operational)

**Blocked By**: US-077 (orchestrator integrated)

**Blocks**: None (parallel with US-101)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time savings: 5-10 hrs/month
- Workflow speedup: 30-50%
- Scheduling accuracy: >85%

---

### US-101: Implement langfuse-prompt-sync Skill

**Status**: 📝 Planned

**Priority Level**: ⭐ MEDIUM

**Estimated Effort**: 6-8 hours (1.5-2 days)

**User Story**:
As any agent, I need Langfuse prompt sync skill, so that prompts automatically sync between local cache and Langfuse source of truth.

**Business Value**:
- **Time Savings**: 3.7-5.6 hours saved per month
- **Consistency**: Single source of truth for prompts
- **Observability**: Full prompt version tracking
- **ROI**: 12-19x in first year

**Technical Spec**: SPEC-105 - Langfuse Prompt Sync (to be created)

**Acceptance Criteria**:
- [ ] Skill executes in <1 minute for full sync
- [ ] Syncs .claude/commands/ ↔ Langfuse
- [ ] Detects conflicts and prompts user
- [ ] Version tracking in Langfuse
- [ ] Unit tests for sync logic
- [ ] Integration tests with Langfuse API
- [ ] Documentation

**Deliverables**:
1. SPEC-105 technical specification
2. langfuse-prompt-sync skill implementation
3. Bidirectional sync logic
4. Conflict resolution
5. Version tracking
6. Tests (unit + integration)
7. Documentation

**Dependencies**: Langfuse integration exists

**Blocked By**: None (standalone)

**Blocks**: None (Phase 7 complete)

**architect Code Review**: MANDATORY

**Success Metrics**:
- Time savings: 3.7-5.6 hrs/month
- Sync reliability: 100%
- Conflicts detected: 100%

---

## Summary

**Total User Stories**: 40 (US-062 through US-101)
**Total Estimated Effort**: 185-235 hours (37-47 days, 8-12 weeks)
**Phases**: 7 phases from foundation to advanced optimization

**Priority Breakdown**:
- **HIGHEST PRIORITY** (Phase 1-3): US-062 through US-071 (30 stories, 85-125 hrs)
- **HIGH PRIORITY** (Phase 4-5): US-072 through US-089 (18 stories, 75-95 hrs)
- **MEDIUM PRIORITY** (Phase 6-7): US-090 through US-101 (12 stories, 65-80 hrs)

**Expected Outcomes**:
- CFR-007 violations: 40-60/month → 0/month
- Agent velocity: +30% from skills
- Workflow time: -40% from orchestrator
- Code analysis speed: 50-150x faster
- Total time savings: 60-90 hours/month from advanced skills
- ROI: 12-19x in first year

**Next Action**: code_developer starts with US-062 (code_developer-startup skill integration)
