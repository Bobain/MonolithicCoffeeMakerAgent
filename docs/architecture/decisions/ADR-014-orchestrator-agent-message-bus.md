# ADR-014: Orchestrator Agent with Message Bus Architecture

**Status**: Accepted

**Date**: 2025-10-19

**Author**: architect agent

**Related Issues**: US-072 - Design Orchestrator Agent Architecture

**Related Specs**: SPEC-062 - Orchestrator Agent Architecture

---

## Context

The MonolithicCoffeeMakerAgent system currently has multiple autonomous agents (architect, code_developer, project_manager, assistant, reflector, curator) that work together to implement features and manage projects. However, the coordination between agents faces several challenges:

### Current Pain Points

**1. Sequential Execution Bottleneck**
```
Current Workflow (Sequential):
User → user_listener → architect (3 min)
                     → code_developer (20 min) ← BLOCKED waiting for architect
                     → project_manager (2 min) ← BLOCKED waiting for code_developer

Total Time: 3 + 20 + 2 = 25 minutes
```
Independent tasks run sequentially, wasting time when they could run in parallel.

**2. No Performance Visibility**
- Users don't know which agent is slow or stuck
- No metrics on agent response times, queue depths, or waiting times
- Can't measure improvement over time
- No way to identify bottlenecks proactively

**3. No Bottleneck Detection**
- Queue pile-ups can occur without warning
- No detection of circular dependencies between agents
- Manual coordination required to optimize workflows

**4. Manual Workflow Optimization**
- user_listener must manually decide which tasks can run in parallel
- No automatic detection of task independence
- Human judgment required for optimization decisions

### Forces at Play

**Performance Requirements**:
- Multi-agent workflows take 15-25 minutes (sequential)
- Target: 40-50% reduction in workflow time through parallelization
- Need real-time visibility into agent health and performance

**Architectural Consistency**:
- Must integrate with existing agent system (AgentRegistry, BaseAgent)
- Should not break existing workflows or require major refactoring
- Must respect agent boundaries and responsibilities

**Simplicity**:
- Avoid external dependencies (no Redis, RabbitMQ)
- File-based or in-memory solutions preferred
- Must be easy to test, debug, and maintain

**Observability**:
- All agent communication should be visible and traceable
- Need dashboards showing agent status, queue depths, bottlenecks
- Performance metrics should be stored for analysis

---

## Decision

We will implement an **Orchestrator Agent** with a message bus architecture to coordinate multi-agent workflows, monitor performance, detect bottlenecks, and optimize execution through parallelization.

### Core Components

**1. Message Bus (Pub/Sub Architecture)**
- In-memory priority queues for fast task routing
- SQLite persistence for crash recovery
- Topic-based routing (e.g., `agent.architect`, `agent.code_developer`)
- Priority support (CRITICAL > HIGH > MEDIUM > LOW)
- No external dependencies (no Redis, RabbitMQ)

**2. Performance Monitor**
- Track agent response times (average, p95, p99)
- Monitor queue depths and wait times
- Detect bottlenecks automatically (queue pile-ups, slow agents)
- Provide real-time dashboard data
- Store historical metrics for analysis

**3. Workflow Optimizer**
- Analyze task dependencies using directed acyclic graphs (DAG)
- Detect independent tasks that can run in parallel
- Create optimized execution plans (batched parallel execution)
- Estimate workflow completion times
- Calculate parallelism factor (speedup vs sequential)

**4. Orchestrator Agent**
- Single entry point for task submission
- Routes tasks to appropriate agents via message bus
- Aggregates results from multiple agents
- Provides health monitoring and bottleneck alerts
- Background worker for continuous monitoring

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐                                                │
│  │user_listener │  (PRIMARY UI - routes ALL user requests)      │
│  └──────┬───────┘                                                │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT ⭐ NEW                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Message Bus                               │ │
│  │  - Task Queue (FIFO + Priority)                            │ │
│  │  - Pub/Sub Topics (agent.architect, agent.code_developer) │ │
│  │  - Request Routing                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Performance Monitor                             │ │
│  │  - Response Time Tracker                                   │ │
│  │  - Queue Depth Analyzer                                    │ │
│  │  - Bottleneck Detector                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Workflow Optimizer                               │ │
│  │  - Dependency Analyzer (detect independence)               │ │
│  │  - Parallel Executor (run concurrent tasks)                │ │
│  │  - Priority Scheduler (critical-first execution)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
│  ┌────────────┐ ┌────────────────┐ ┌───────────────────┐       │
│  │ architect  │ │ code_developer │ │ project_manager   │       │
│  └────────────┘ └────────────────┘ └───────────────────┘       │
│  ┌────────────┐ ┌────────────────┐ ┌───────────────────┐       │
│  │ assistant  │ │ reflector      │ │ curator           │       │
│  └────────────┘ └────────────────┘ └───────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Before Orchestrator (Sequential)**:
```
user_listener → architect (create spec)      [3 minutes]
             → project_manager (check PRs)   [2 minutes]  ← BLOCKED
Total: 5 minutes
```

**After Orchestrator (Parallel)**:
```
user_listener → orchestrator
             → architect (create spec)       [3 minutes] ┐
             → project_manager (check PRs)   [2 minutes] ┴→ PARALLEL
Total: 3 minutes (40% faster)
```

---

## Consequences

### Positive Consequences

- **Faster Workflows**: 40-50% reduction in workflow time through parallel execution of independent tasks
- **Performance Visibility**: Real-time metrics on agent response times, queue depths, and bottlenecks
- **Proactive Bottleneck Detection**: Automatic alerts when queues back up or agents slow down
- **Better User Experience**: Users see progress across multiple agents simultaneously
- **Optimized Scheduling**: Priority-based execution ensures critical tasks run first
- **No External Dependencies**: In-memory + SQLite approach avoids Redis/RabbitMQ complexity
- **Easy Testing**: Message bus can be tested with unit tests, no need for integration test infrastructure
- **Full Observability**: All task routing and agent communication visible in orchestrator dashboard
- **Crash Recovery**: SQLite persistence ensures tasks not lost if orchestrator crashes
- **Scalable Architecture**: Foundation for future enhancements (distributed agents, load balancing)

### Negative Consequences

- **Added Complexity**: New layer of coordination between user_listener and agents
- **Performance Overhead**: Message bus adds latency to task submission (<100ms target)
- **Integration Burden**: All agents need updates to consume from message bus
- **Learning Curve**: Developers must understand message bus, topics, priorities
- **State Management**: Need to track pending/completed tasks across system
- **Dependency on networkx**: Requires networkx library for dependency graph analysis (needs approval via ADR-013)
- **Migration Risk**: Gradual rollout required to avoid breaking existing workflows

### Neutral Consequences

- **File Structure Changes**: New directory `coffee_maker/orchestrator/` with 4 new modules
- **Database Addition**: New SQLite database `data/orchestrator/message_bus.db` for task persistence
- **Agent Interface Changes**: Agents need to subscribe to topics and consume tasks from message bus

---

## Alternatives Considered

### Alternative 1: Direct Agent-to-Agent Communication

**Description**: Allow agents to call each other directly without orchestrator

**Pros**:
- Simpler architecture (no message bus)
- Lower latency (direct function calls)
- Easier to implement initially

**Cons**:
- No centralized visibility into agent communication
- Hard to detect bottlenecks or measure performance
- Tight coupling between agents (violates separation of concerns)
- No support for parallel execution
- Difficult to add priority scheduling or queue management

**Why Rejected**: Doesn't provide the performance monitoring, bottleneck detection, or workflow optimization capabilities required by US-072.

### Alternative 2: External Message Queue (Redis, RabbitMQ)

**Description**: Use production-grade message queue like Redis or RabbitMQ

**Pros**:
- Battle-tested, production-ready
- Advanced features (clustering, replication)
- Industry-standard patterns

**Cons**:
- External dependency (violates simplicity requirement)
- Harder to install, configure, and maintain
- Overkill for single-machine agent system
- More complex testing (need to run Redis in CI)
- Platform-specific installation (harder on Windows)

**Why Rejected**: Adds unnecessary complexity for a single-machine system. In-memory + SQLite provides sufficient reliability without external dependencies.

### Alternative 3: Event-Driven Architecture (asyncio)

**Description**: Use Python asyncio for event-driven agent coordination

**Pros**:
- Native Python support (no dependencies)
- Non-blocking I/O for high concurrency
- Modern async/await syntax

**Cons**:
- Requires refactoring all agents to async
- Harder to debug (async stack traces are complex)
- No built-in persistence (still need DB)
- Steeper learning curve for developers
- Async code is harder to test

**Why Rejected**: Too invasive (requires refactoring entire agent system). Message bus approach allows gradual migration without breaking existing code.

---

## Implementation Notes

### Files to Create

1. `coffee_maker/orchestrator/message_bus.py`
   - MessageBus class with pub/sub functionality
   - Task, TaskResult dataclasses
   - Priority enum (CRITICAL, HIGH, MEDIUM, LOW)
   - SQLite persistence for crash recovery

2. `coffee_maker/orchestrator/performance_monitor.py`
   - PerformanceMonitor class
   - AgentMetrics, BottleneckReport dataclasses
   - Percentile calculations (p95, p99)
   - Dashboard data aggregation

3. `coffee_maker/orchestrator/workflow_optimizer.py`
   - WorkflowOptimizer class
   - WorkflowPlan dataclass
   - Dependency graph analysis (using networkx)
   - Parallel batch execution planning

4. `coffee_maker/orchestrator/orchestrator_agent.py`
   - OrchestratorAgent class (inherits from BaseAgent)
   - Task submission API
   - Workflow submission API
   - Background worker thread

5. `.claude/skills/orchestrator-startup.md`
   - Claude Skill for orchestrator initialization
   - Health checks
   - Crash recovery procedures

### Implementation Steps

**Phase 1: Infrastructure (Week 1)**
1. Implement MessageBus with SQLite persistence
2. Implement PerformanceMonitor
3. Implement WorkflowOptimizer
4. Unit tests (>80% coverage)

**Phase 2: Orchestrator Agent (Week 2)**
1. Implement OrchestratorAgent class
2. Create orchestrator-startup.md skill
3. Integration tests
4. Performance benchmarks

**Phase 3: Agent Integration (Week 3)**
1. Update architect to consume from message bus
2. Update code_developer to consume from message bus
3. Update project_manager to consume from message bus
4. Update user_listener to submit via orchestrator

**Phase 4: Architect Code Review (Mandatory)**
1. architect reviews implementation for:
   - Architectural compliance (message bus patterns, agent coordination)
   - Code quality (singleton enforcement, thread safety)
   - Security (agent isolation, safe task routing)
   - Performance (queue latency <100ms, bottleneck detection accuracy)
   - CFR compliance (CFR-007 context budget, CFR-008 agent boundaries)
2. architect approves or requests changes
3. code_developer addresses feedback
4. architect gives final approval

**Phase 5: Dashboard & Monitoring (Week 4)**
1. Create health dashboard UI
2. Add bottleneck alerts
3. Performance visualization
4. User documentation

### Dependency Approval

**New Dependency Required**: `networkx`
- **Purpose**: Dependency graph analysis for workflow optimization
- **Approval Status**: NEEDS_REVIEW (not in pre-approved list)
- **Action**: Request architect to evaluate via ADR-013 process

---

## Validation

### Success Metrics

| Metric | Baseline (Before) | Target (After) | Measurement |
|--------|-------------------|----------------|-------------|
| **Average Workflow Time** | 15-25 minutes | 8-12 minutes | 40-50% reduction |
| **Queue Wait Time (p95)** | Unknown | <1 minute | Real-time monitoring |
| **Bottleneck Detection** | Manual | Automatic (<30s) | Proactive alerts |
| **Parallel Execution Rate** | 0% | 40-60% | Workflow analysis |
| **Message Bus Latency** | N/A | <100ms | Performance benchmarks |

### Testing Strategy

**Unit Tests**:
- MessageBus publish/consume functionality
- Priority ordering (CRITICAL before MEDIUM)
- Workflow optimizer parallel detection
- Performance monitor metrics calculations
- Bottleneck detection logic

**Integration Tests**:
- End-to-end parallel workflow execution
- Agent subscription and message consumption
- Crash recovery from SQLite persistence
- Performance monitoring across agents

**Performance Tests**:
- Message bus throughput (tasks/second)
- Queue latency under load
- Memory usage with large task queues
- Bottleneck detection accuracy

### Reevaluation Timeline

- **1 Month**: Check workflow time reduction metrics
- **3 Months**: Review bottleneck detection effectiveness
- **6 Months**: Decide if external message queue needed for scale

---

## References

- [SPEC-062: Orchestrator Agent Architecture](../specs/SPEC-062-orchestrator-agent-architecture.md)
- [US-072: Design Orchestrator Agent Architecture](../../roadmap/ROADMAP.md)
- [ADR-013: Dependency Pre-Approval Matrix](./ADR-013-dependency-pre-approval-matrix.md)
- [ADR-011: Orchestrator-Based Commit Review](./ADR-011-orchestrator-based-commit-review.md) (Different orchestrator - file-based messaging)
- [CFR-007: Context Budget Management](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
- [CFR-008: Agent Boundaries](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
- [networkx Documentation](https://networkx.org/documentation/stable/)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created | architect |
| 2025-10-19 | Status: Accepted | architect |

---

## Notes

### Risks and Mitigations

**Risk 1: Performance Overhead**
- **Impact**: Message bus adds latency to task submission
- **Probability**: MEDIUM
- **Mitigation**:
  - Measure overhead with benchmarks (<100ms target)
  - Optimize hot paths (in-memory queue operations)
  - Consider direct delegation for single-task workflows

**Risk 2: Integration Complexity**
- **Impact**: All agents need updates to consume from message bus
- **Probability**: HIGH
- **Mitigation**:
  - Gradual rollout (one agent at a time)
  - Backward compatibility with direct delegation
  - Comprehensive integration tests

**Risk 3: Message Bus Reliability**
- **Impact**: Tasks could be lost if message bus fails
- **Probability**: LOW
- **Mitigation**:
  - SQLite persistence for crash recovery
  - Atomic writes for message files
  - Retry logic for failed task submissions

**Risk 4: networkx Dependency**
- **Impact**: New dependency needs approval (not pre-approved)
- **Probability**: LOW (likely to be approved)
- **Mitigation**:
  - Request architect approval via ADR-013 process
  - If rejected, implement simple dependency graph without networkx
  - Alternative: Use adjacency lists instead of networkx

### Open Questions

1. **How to handle agent failures during task execution?**
   - Current answer: Background worker detects timeouts, moves tasks to dead letter queue
   - Future: Add retry logic with exponential backoff

2. **Should orchestrator support distributed agents (across machines)?**
   - Current answer: No (single-machine system)
   - Future: Could add gRPC/REST API for remote agents

3. **How to handle very long-running tasks (>1 hour)?**
   - Current answer: Increase timeout for specific task types
   - Future: Add task checkpointing for resume after crash

### Future Work

- **Dashboard UI**: Real-time visualization of agent status and bottlenecks
- **Load Balancing**: Distribute tasks across multiple agent instances
- **Distributed Orchestrator**: Support agents running on different machines
- **Advanced Scheduling**: ML-based task time estimation, adaptive priority adjustment
- **Metrics Export**: Prometheus/Grafana integration for production monitoring

---

**Remember**: This ADR documents the architectural decision for US-072. The implementation details are in SPEC-062. If requirements change significantly, this ADR may be superseded by a future ADR.
