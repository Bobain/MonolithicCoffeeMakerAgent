# Skill: Trace Execution (ACE Generator)

**Name**: `trace-execution`
**Owner**: ALL agents (universal skill)
**Purpose**: Capture execution traces automatically for ACE framework (Agent Context Evolving)
**Priority**: CRITICAL - Foundation of ACE observability loop

---

## Overview

This skill is used by **ALL agents** to automatically capture execution traces. It replaces the need for a separate "generator" agent by embedding trace generation directly into each agent's workflow.

**ACE Framework Context**:
- **trace-execution** (this skill): Captures execution traces
- **Reflector** (agent): Analyzes traces, creates delta items
- **Curator** (agent): Synthesizes delta items into playbooks

**Why a Skill, Not an Agent?**
- ✅ Execution context already available (agent knows what it's doing)
- ✅ More accurate traces (captured at moment of execution, not observed later)
- ✅ Simpler architecture (no IPC, no coordination overhead)
- ✅ Better performance (direct writes, no polling)
- ✅ Easier integration (agents just use the skill)

---

## When to Use This Skill

**MANDATORY** for ALL agents:
- ✅ At agent startup (start execution trace)
- ✅ During agent work (log trace events)
- ✅ At agent shutdown (end execution trace)

**Automatic Integration**:
- Embedded in agent startup skills (architect-startup, code-developer-startup, project-manager-startup)
- Agents don't need to explicitly invoke - it runs automatically

---

## Trace File Format

**Storage Location**: `docs/generator/`

**File Naming**: `trace_{agent}_{task_type}_{timestamp}.json`
- Example: `trace_code_developer_implement_priority_2025-10-18T10-30-00.json`

**File Structure**:
```json
{
  "trace_id": "uuid-here",
  "agent": "code_developer",
  "task_type": "implement_priority",
  "context": {
    "priority": "PRIORITY 10",
    "priority_name": "User Authentication"
  },
  "start_time": "2025-10-18T10:30:00Z",
  "end_time": "2025-10-18T11:57:03Z",
  "duration_seconds": 5223,
  "duration_human": "1h 27m 03s",
  "events": [
    {
      "timestamp": "2025-10-18T10:30:00Z",
      "event_type": "task_started",
      "data": {
        "priority": "PRIORITY 10",
        "expected_time": "25 hours (from spec)"
      }
    },
    {
      "timestamp": "2025-10-18T10:30:15Z",
      "event_type": "file_read",
      "data": {
        "file": "docs/roadmap/ROADMAP.md",
        "section": "PRIORITY 10",
        "tokens": 2143
      }
    },
    {
      "timestamp": "2025-10-18T10:32:30Z",
      "event_type": "code_discovery_started",
      "data": {
        "total_files_scanned": 247
      }
    },
    {
      "timestamp": "2025-10-18T10:35:12Z",
      "event_type": "code_discovery_completed",
      "data": {
        "relevant_files_found": 15,
        "time_spent": "2m 42s"
      }
    },
    {
      "timestamp": "2025-10-18T11:00:00Z",
      "event_type": "file_modified",
      "data": {
        "file": "coffee_maker/auth/authentication.py",
        "lines_added": 150,
        "lines_deleted": 0
      }
    },
    {
      "timestamp": "2025-10-18T11:45:00Z",
      "event_type": "tests_run",
      "data": {
        "total_tests": 23,
        "passing": 23,
        "failing": 0,
        "time": "12s"
      }
    },
    {
      "timestamp": "2025-10-18T11:57:03Z",
      "event_type": "task_completed",
      "data": {
        "outcome": "success",
        "files_modified": 5,
        "tests_passing": true,
        "committed": true,
        "commit_hash": "abc123"
      }
    }
  ],
  "outcome": "success",
  "metrics": {
    "total_files_read": 18,
    "total_files_modified": 5,
    "total_tokens_consumed": 45000,
    "total_llm_calls": 12,
    "total_cost_usd": 0.23
  },
  "bottlenecks": [
    {
      "stage": "code_discovery",
      "time_spent": "2m 42s",
      "percentage_of_total": 3.1
    },
    {
      "stage": "implementation",
      "time_spent": "45m 00s",
      "percentage_of_total": 51.6
    }
  ]
}
```

---

## Skill Execution Steps

### Step 1: Start Execution Trace

**When**: Agent startup (automatically called by startup skills)

**Input**:
- `agent`: Agent name (e.g., "code_developer", "architect", "project_manager")
- `task_type`: Type of task (e.g., "implement_priority", "create_spec", "health_check")
- `context`: Task-specific context (e.g., {"priority": "PRIORITY 10"})

**Process**:
```python
def start_execution_trace(agent: str, task_type: str, context: dict) -> str:
    """Start execution trace and return trace_id."""
    import uuid
    from datetime import datetime

    trace_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    trace = {
        "trace_id": trace_id,
        "agent": agent,
        "task_type": task_type,
        "context": context,
        "start_time": timestamp,
        "events": []
    }

    # Write initial trace file
    trace_file = f"docs/generator/trace_{agent}_{task_type}_{timestamp.replace(':', '-')}.json"
    with open(trace_file, 'w') as f:
        json.dump(trace, f, indent=2)

    # Store trace_id in agent's session state
    return trace_id
```

**Output**: `trace_id` (UUID string)

---

### Step 2: Log Trace Events

**When**: Throughout agent execution (automatic at key points)

**Input**:
- `trace_id`: UUID from Step 1
- `event_type`: Type of event (see Event Types below)
- `data`: Event-specific data

**Event Types**:

1. **task_started** - Task begins
   ```python
   log_trace_event(trace_id, "task_started", {
       "priority": "PRIORITY 10",
       "expected_time": "25 hours"
   })
   ```

2. **file_read** - File read operation
   ```python
   log_trace_event(trace_id, "file_read", {
       "file": "docs/roadmap/ROADMAP.md",
       "section": "PRIORITY 10",
       "tokens": 2143
   })
   ```

3. **code_discovery_started** - Code search begins
   ```python
   log_trace_event(trace_id, "code_discovery_started", {
       "total_files_scanned": 247
   })
   ```

4. **code_discovery_completed** - Code search finishes
   ```python
   log_trace_event(trace_id, "code_discovery_completed", {
       "relevant_files_found": 15,
       "time_spent": "2m 42s"
   })
   ```

5. **file_modified** - File write/edit operation
   ```python
   log_trace_event(trace_id, "file_modified", {
       "file": "coffee_maker/auth/authentication.py",
       "lines_added": 150,
       "lines_deleted": 0
   })
   ```

6. **tests_run** - Tests executed
   ```python
   log_trace_event(trace_id, "tests_run", {
       "total_tests": 23,
       "passing": 23,
       "failing": 0,
       "time": "12s"
   })
   ```

7. **skill_invoked** - Another skill used
   ```python
   log_trace_event(trace_id, "skill_invoked", {
       "skill": "test-failure-analysis",
       "reason": "3 tests failing",
       "outcome": "fixes identified"
   })
   ```

8. **llm_call** - LLM invoked
   ```python
   log_trace_event(trace_id, "llm_call", {
       "model": "claude-sonnet-3.5",
       "prompt_tokens": 5000,
       "completion_tokens": 1200,
       "cost_usd": 0.018,
       "purpose": "generate authentication logic"
   })
   ```

9. **bottleneck_detected** - Performance issue identified
   ```python
   log_trace_event(trace_id, "bottleneck_detected", {
       "stage": "code_discovery",
       "time_spent": "15m",
       "reason": "manual grepping across 247 files"
   })
   ```

10. **task_completed** - Task finishes
    ```python
    log_trace_event(trace_id, "task_completed", {
        "outcome": "success",
        "files_modified": 5,
        "tests_passing": true,
        "committed": true
    })
    ```

**Process**:
```python
def log_trace_event(trace_id: str, event_type: str, data: dict):
    """Append event to trace file."""
    from datetime import datetime

    # Find trace file by trace_id
    trace_file = find_trace_file(trace_id)

    # Load current trace
    with open(trace_file, 'r') as f:
        trace = json.load(f)

    # Append event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "data": data
    }
    trace["events"].append(event)

    # Write back
    with open(trace_file, 'w') as f:
        json.dump(trace, f, indent=2)
```

---

### Step 3: End Execution Trace

**When**: Agent shutdown (automatically called)

**Input**:
- `trace_id`: UUID from Step 1
- `outcome`: "success" | "failure" | "partial"
- `metrics`: Final metrics (optional)

**Process**:
```python
def end_execution_trace(trace_id: str, outcome: str, metrics: dict = None):
    """Finalize trace with outcome and metrics."""
    from datetime import datetime

    # Find trace file
    trace_file = find_trace_file(trace_id)

    # Load trace
    with open(trace_file, 'r') as f:
        trace = json.load(f)

    # Add end time
    end_time = datetime.utcnow()
    trace["end_time"] = end_time.isoformat()

    # Calculate duration
    start_time = datetime.fromisoformat(trace["start_time"])
    duration = (end_time - start_time).total_seconds()
    trace["duration_seconds"] = duration
    trace["duration_human"] = format_duration(duration)

    # Add outcome
    trace["outcome"] = outcome

    # Add metrics
    if metrics:
        trace["metrics"] = metrics
    else:
        # Calculate metrics from events
        trace["metrics"] = calculate_metrics_from_events(trace["events"])

    # Identify bottlenecks
    trace["bottlenecks"] = identify_bottlenecks(trace["events"], duration)

    # Write final trace
    with open(trace_file, 'w') as f:
        json.dump(trace, f, indent=2)
```

**Output**: Final trace file written to `docs/generator/`

---

## Integration with Agent Startup Skills

### architect-startup.md Integration
```python
# In architect-startup skill execution

# Step 1: Start trace
trace_id = start_execution_trace(
    agent="architect",
    task_type="create_spec",  # or "review_code", "approve_dependency"
    context={
        "priority": "PRIORITY 10",
        "spec_name": "SPEC-062-user-authentication.md"
    }
)

# Step 2: Log events as architect works
log_trace_event(trace_id, "file_read", {
    "file": "docs/roadmap/ROADMAP.md",
    "section": "PRIORITY 10",
    "tokens": 2000
})

log_trace_event(trace_id, "code_discovery_started", {
    "total_files_scanned": 100
})

# ... architect creates spec ...

log_trace_event(trace_id, "file_modified", {
    "file": "docs/architecture/specs/SPEC-062-user-authentication.md",
    "lines_added": 800
})

# Step 3: End trace
end_execution_trace(trace_id, outcome="success", metrics={
    "total_files_read": 8,
    "total_files_modified": 1,
    "total_tokens_consumed": 25000,
    "spec_lines": 800
})
```

### code-developer-startup.md Integration
```python
# In code_developer-startup skill execution

# Step 1: Start trace
trace_id = start_execution_trace(
    agent="code_developer",
    task_type="implement_priority",  # or "fix_tests", "create_pr"
    context={
        "priority": "PRIORITY 10",
        "priority_name": "User Authentication"
    }
)

# Step 2: Log events as code_developer works
log_trace_event(trace_id, "file_read", {
    "file": "docs/architecture/specs/SPEC-062-user-authentication.md",
    "tokens": 8000
})

log_trace_event(trace_id, "skill_invoked", {
    "skill": "test-failure-analysis",
    "reason": "3 tests failing",
    "outcome": "fixes identified"
})

log_trace_event(trace_id, "tests_run", {
    "total_tests": 23,
    "passing": 23,
    "failing": 0
})

# Step 3: End trace
end_execution_trace(trace_id, outcome="success", metrics={
    "total_files_modified": 5,
    "total_tests": 23,
    "total_commits": 1
})
```

### project-manager-startup.md Integration
```python
# In project_manager-startup skill execution

# Step 1: Start trace
trace_id = start_execution_trace(
    agent="project_manager",
    task_type="health_check",  # or "roadmap_query", "pr_monitoring"
    context={}
)

# Step 2: Log events
log_trace_event(trace_id, "file_read", {
    "file": "docs/roadmap/ROADMAP.md",
    "format": "ultra-compact summary",
    "tokens": 3000
})

log_trace_event(trace_id, "skill_invoked", {
    "skill": "roadmap-health-check",
    "outcome": "health score: 87"
})

# Step 3: End trace
end_execution_trace(trace_id, outcome="success", metrics={
    "health_score": 87,
    "priorities_analyzed": 15
})
```

---

## Benefits of trace-execution Skill

### 1. **Accurate Traces**
- Agent knows exactly what it's doing (no inference needed)
- Timestamps are precise (captured at moment of action)
- Context is complete (all data available)

### 2. **Simple Architecture**
- No separate generator agent process
- No IPC (inter-process communication) overhead
- Fewer moving parts = fewer failure points

### 3. **Better Performance**
- Direct writes to trace file (no delays)
- No polling or observation loops
- Minimal overhead (<1% of agent time)

### 4. **Easy Integration**
- Agents just call 3 functions: start, log, end
- Automatic via startup skills (no manual work)
- Works with any agent (universal)

### 5. **Rich Data for Reflector**
- Reflector gets complete, accurate traces
- Bottlenecks clearly identified
- Time spent at each stage tracked
- LLM costs and token usage captured

---

## Example: Complete Trace Lifecycle

```python
# Agent: code_developer
# Task: implement_priority (PRIORITY 10)

# === STARTUP (automatic via code-developer-startup skill) ===
trace_id = start_execution_trace(
    agent="code_developer",
    task_type="implement_priority",
    context={
        "priority": "PRIORITY 10",
        "priority_name": "User Authentication"
    }
)

# === DURING WORK (automatic at key points) ===

# Read ROADMAP
log_trace_event(trace_id, "file_read", {
    "file": "docs/roadmap/ROADMAP.md",
    "section": "PRIORITY 10",
    "tokens": 2143
})

# Read spec
log_trace_event(trace_id, "file_read", {
    "file": "docs/architecture/specs/SPEC-062-user-authentication.md",
    "tokens": 8000
})

# Code discovery
log_trace_event(trace_id, "code_discovery_started", {
    "total_files_scanned": 247
})

log_trace_event(trace_id, "code_discovery_completed", {
    "relevant_files_found": 15,
    "time_spent": "2m 42s"
})

# Implementation
log_trace_event(trace_id, "file_modified", {
    "file": "coffee_maker/auth/authentication.py",
    "lines_added": 150
})

log_trace_event(trace_id, "file_modified", {
    "file": "tests/unit/test_authentication.py",
    "lines_added": 80
})

# Tests fail
log_trace_event(trace_id, "tests_run", {
    "total_tests": 23,
    "passing": 20,
    "failing": 3,
    "time": "12s"
})

# Use skill to fix tests
log_trace_event(trace_id, "skill_invoked", {
    "skill": "test-failure-analysis",
    "reason": "3 tests failing",
    "outcome": "fixes identified",
    "time_saved": "20 minutes"
})

# Tests now pass
log_trace_event(trace_id, "tests_run", {
    "total_tests": 23,
    "passing": 23,
    "failing": 0,
    "time": "12s"
})

# Commit
log_trace_event(trace_id, "git_commit", {
    "commit_hash": "abc123",
    "files_committed": 5,
    "message": "feat: Implement PRIORITY 10 - User Authentication"
})

# === SHUTDOWN (automatic) ===
end_execution_trace(trace_id, outcome="success", metrics={
    "total_files_read": 18,
    "total_files_modified": 5,
    "total_tokens_consumed": 45000,
    "total_llm_calls": 12,
    "total_cost_usd": 0.23,
    "tests_passing": 23
})

# Result: Complete trace written to:
# docs/generator/trace_code_developer_implement_priority_2025-10-18T10-30-00.json
```

---

## How Reflector Uses Traces

**Reflector Agent** reads traces from `docs/generator/` and analyzes:

1. **Time Spent Analysis**
   - Which stages take longest? (code_discovery, implementation, testing)
   - Are there consistent bottlenecks?

2. **Pattern Detection**
   - Same task type always takes X minutes?
   - Certain files always slow things down?

3. **Skill Effectiveness**
   - Did test-failure-analysis save time?
   - What's the accuracy of dod-verification?

4. **Delta Item Creation**
   - "BOTTLENECK: Code discovery (15-30 min per spec) - repetitive manual grepping"
   - "PATTERN: Specs always 90-150 min - code search is 20% of time"
   - "OPPORTUNITY: Automate template population - saves 15 min per spec"

**Output**: Delta items written to `docs/reflector/`

---

## How Curator Uses Delta Items

**Curator Agent** reads delta items and creates playbooks:

1. **Synthesize Patterns**
   - Multiple delta items about same bottleneck → High-priority skill recommendation

2. **Calculate ROI**
   - Time wasted × frequency = monthly hours lost
   - Implementation effort estimation
   - ROI = savings / effort

3. **Recommend Skills**
   - "Create spec-creation-automation skill (saves 23-30.7 hrs/month)"
   - "Create context-budget-optimizer skill (saves 26.7-40 hrs/month)"

4. **Track Skill Effectiveness**
   - After skill deployed, measure actual savings vs. estimate
   - Recommend modifications if skill underperforming

**Output**: Playbooks written to `docs/curator/`

---

## Success Metrics

**Trace Capture Rate**:
- **Goal**: 100% of agent executions have traces
- **Measure**: (Traces created) / (Agent executions)
- **Current**: TBD (track after implementation)

**Trace Accuracy**:
- **Goal**: <5% discrepancy between traced time and actual time
- **Measure**: Compare trace duration vs. wall-clock time
- **Current**: TBD

**Reflector Effectiveness**:
- **Goal**: 80%+ of curator recommendations come from reflector delta items
- **Measure**: (Recommendations from delta items) / (Total recommendations)
- **Current**: TBD

**Skill ROI Validation**:
- **Goal**: Actual savings ≥ 80% of estimated savings
- **Measure**: Compare trace data pre/post skill deployment
- **Current**: TBD

---

## Related Components

- **architect-startup**: Uses trace-execution for architect tasks
- **code-developer-startup**: Uses trace-execution for code_developer tasks
- **project-manager-startup**: Uses trace-execution for project_manager tasks
- **Reflector Agent**: Analyzes traces, creates delta items
- **Curator Agent**: Uses delta items to recommend skills

---

**Remember**: Every agent action is a data point! Trace everything, analyze patterns, evolve continuously! 🔍

**ACE Mantra**: "Observe, Reflect, Curate, Improve"
