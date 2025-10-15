# ACE Framework: Complete Workflow Documentation

**Version**: 1.0
**Date**: 2025-10-15
**Reference**: https://www.arxiv.org/abs/2510.04618

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Workflow Diagram](#complete-workflow-diagram)
3. [Artifacts Created](#artifacts-created)
4. [Agent Execution Flow](#agent-execution-flow)
5. [Workflow Triggers](#workflow-triggers)
6. [Agent Responsibilities](#agent-responsibilities)
7. [Success Metrics](#success-metrics)
8. [Examples](#examples)

---

## Overview

This document describes the complete ACE (Agentic Context Engineering) workflow, from agent execution through trace creation, reflection, curation, and feedback loops.

**Key Concept**: ACE enables agents to learn from their execution history by capturing detailed traces, analyzing patterns, and maintaining evolving playbooks of best practices.

### Three Core Components

1. **Generator**: Observes agent executions and creates comprehensive traces
2. **Reflector**: Analyzes traces to extract insights and identify patterns
3. **Curator**: Consolidates insights into evolving playbooks with semantic de-duplication

### Learning Loop

```
Execute → Observe → Reflect → Curate → Improve → Execute (with better context)
```

---

## Complete Workflow Diagram

```
User Request
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INTERFACE (user_listener)                               │
├─────────────────────────────────────────────────────────────────┤
│ • Displays Rich console UI (ONLY agent with UI)                 │
│ • Gets user input                                                │
│ • Shows progress indicators                                      │
│ • Asks curator feedback questions                               │
│ • Shows proactive suggestions from user_interpret               │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. INTENT INTERPRETATION (user_interpret)                       │
├─────────────────────────────────────────────────────────────────┤
│ • Analyzes user sentiment (frustration, satisfaction, etc.)     │
│ • Interprets user intent (add_feature, ask_how_to, etc.)       │
│ • Chooses appropriate agent for delegation                      │
│ • Logs conversation (docs/user_interpret/)                      │
│ • Tracks user requests (docs/user_interpret/user_requests.json)│
│ • Generates proactive suggestions                               │
│ • LEARNS from feedback via ACE                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
              Delegates to appropriate agent
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. AGENT EXECUTION (with ACE Generator wrapping)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ PRE-EXECUTION                                              │ │
│ │ • Generator initializes observation                        │ │
│ │ • Loads current playbook for agent                         │ │
│ │ • Captures git status, file tree                           │ │
│ │ • Records timestamp                                        │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ EXECUTION 1 (ALWAYS RUNS)                                  │ │
│ │ • Agent receives: user_query + current_playbook            │ │
│ │ • Agent executes task                                      │ │
│ │ • During execution, agent calls:                           │ │
│ │   - _set_plan([steps])        # Declare planned steps     │ │
│ │   - _update_plan_progress()   # Mark step status          │ │
│ │   - _report_difficulty()      # Flag issues               │ │
│ │   - _report_concern()         # Raise warnings            │ │
│ │ • Generator captures:                                      │ │
│ │   - External: git diff, files created/modified/deleted    │ │
│ │   - Internal: reasoning, tools, decisions, context usage  │ │
│ │   - Result: success/failure, duration, token usage        │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ CONDITIONAL EXECUTION 2 (Cost Optimization)                │ │
│ │ • Evaluate conditions:                                     │ │
│ │   IF duration < 30s AND no owned files modified:          │ │
│ │      ✅ RUN second execution (comparison valuable)        │ │
│ │      • Execute agent again with same query                │ │
│ │      • Capture observations again                         │ │
│ │      • Compare both executions for consistency            │ │
│ │   ELSE:                                                    │ │
│ │      ❌ SKIP second execution (too expensive to duplicate)│ │
│ │      • Note reason in trace (long duration or real work)  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ POST-EXECUTION                                             │ │
│ │ • Capture final git status                                 │ │
│ │ • Package comprehensive trace                              │ │
│ │ • Assign trace_id (timestamp-based)                       │ │
│ │ • Save to:                                                 │ │
│ │   docs/generator/traces/YYYY-MM-DD/trace_<id>.md          │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
              Trace JSON/Markdown saved
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. REFLECTION (Reflector analyzes patterns)                     │
├─────────────────────────────────────────────────────────────────┤
│ • Triggered: Manual OR Scheduled (batch of 5 traces)            │
│ • Command: poetry run reflector analyze [agent_name]            │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ CROSS-EXECUTION PATTERN ANALYSIS                           │ │
│ │ • Load recent traces (batch of 5-10)                       │ │
│ │ • Compare MULTIPLE traces over time                        │ │
│ │ • Identify patterns:                                       │ │
│ │   - Success patterns: What consistently works?            │ │
│ │   - Failure modes: What consistently fails?               │ │
│ │   - Optimizations: What could be better?                  │ │
│ │   - Plan deviations: Did agent follow plan?               │ │
│ │   - Missing knowledge: What's not in playbook?            │ │
│ │ • Assign priority (1-5) based on evidence strength        │ │
│ │ • Assign confidence (0.0-1.0) based on consistency        │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ DELTA GENERATION                                           │ │
│ │ • Extract actionable insights (delta items)                │ │
│ │ • Each delta contains:                                     │ │
│ │   - insight_type: success_pattern, failure_mode, etc.     │ │
│ │   - title: Brief description                              │ │
│ │   - description: Full explanation                         │ │
│ │   - recommendation: Actionable guidance                   │ │
│ │   - evidence: List of trace IDs + examples                │ │
│ │   - priority: 1-5 (based on impact)                       │ │
│ │   - confidence: 0.0-1.0 (based on consistency)            │ │
│ │ • Save to:                                                 │ │
│ │   docs/reflector/deltas/[agent]/YYYY-MM-DD_batch_N.json   │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
            Delta items (insights) saved
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. CURATION (Curator maintains playbook)                        │
├─────────────────────────────────────────────────────────────────┤
│ • Triggered: Manual OR Scheduled OR user_listener /curate       │
│ • Command: poetry run curator curate [agent_name]               │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ PLAYBOOK CONSOLIDATION                                     │ │
│ │ • Load existing playbook (if exists)                       │ │
│ │ • Load new delta items from reflector                      │ │
│ │ • For each delta:                                          │ │
│ │   1. Generate semantic embedding (OpenAI)                 │ │
│ │   2. Calculate cosine similarity with existing bullets    │ │
│ │   3. De-duplication decision:                             │ │
│ │      • Similarity > 0.90: Merge (increment helpful_count) │ │
│ │      • Similarity > 0.85: Consolidate if same category    │ │
│ │      • Similarity > 0.75: Update if delta more specific   │ │
│ │      • Similarity < 0.75: Add as new bullet               │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ PRUNING & HEALTH                                           │ │
│ │ • Prune low-value bullets:                                 │ │
│ │   - helpful_count < 2 AND pruned_count > 3                │ │
│ │ • Enforce max size (150 bullets)                           │ │
│ │ • Update health metrics:                                   │ │
│ │   - effectiveness_ratio = helpful / (helpful + harmful)   │ │
│ │   - coverage_score (0-1)                                   │ │
│ │   - avg_helpful_count                                      │ │
│ │ • Save playbook to:                                        │ │
│ │   docs/curator/playbooks/[agent]_playbook.json            │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
              Updated playbook saved
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. FEEDBACK LOOP (Curator → user_listener → User)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ FEEDBACK SUGGESTIONS                                       │ │
│ │ • Curator analyzes playbook effectiveness                  │ │
│ │ • FeedbackSuggestor.get_suggested_questions()              │ │
│ │ • Generates questions like:                                │ │
│ │   - "Was the intent interpretation accurate?"             │ │
│ │   - "Did the agent choose the right approach?"            │ │
│ │   - "Was the response helpful?"                           │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ USER FEEDBACK                                              │ │
│ │ • user_listener asks questions in UI                       │ │
│ │ • User responds (yes/no/rating)                            │ │
│ │ • FeedbackSuggestor.record_feedback()                      │ │
│ │ • Updates playbook bullet counters:                        │ │
│ │   - Positive feedback → helpful_count++                   │ │
│ │   - Negative feedback → harmful_count++                   │ │
│ │ • Saves to feedback history:                               │ │
│ │   docs/curator/feedback/[agent]_feedback.jsonl            │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ CONTINUOUS IMPROVEMENT                                     │ │
│ │ • Next curation uses feedback                              │ │
│ │ • Prunes bullets with low helpful_count                    │ │
│ │ • Promotes bullets with high helpful_count                 │ │
│ │ • Evolves playbook based on real usage                     │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
              Feedback incorporated
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. NEXT EXECUTION (Improved with evolved playbook)              │
├─────────────────────────────────────────────────────────────────┤
│ • Generator loads updated playbook                               │
│ • Agent receives enhanced context                                │
│ • Improved performance due to learned best practices             │
│ • Cycle continues...                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Artifacts Created

### 1. Traces (Generator)

**Location**: `docs/generator/traces/YYYY-MM-DD/trace_<timestamp>.md`

**Purpose**: Comprehensive record of agent execution

**Structure**:
```markdown
# Execution Trace: <timestamp>

**Timestamp**: 2025-10-15T08:47:30.655276
**Agent**: user_interpret
**Query**: Show me the ROADMAP

## Delegation Chain

1. **user_interpret** (trace: `1760510850655276`, time: 2025-10-15T08:47:30.655276)

## Agent Identity

- **Objective**: Interpret user intent and delegate appropriately
- **Success Criteria**: Correct intent interpretation, accurate sentiment, appropriate delegation

## Executions

### Execution 1

**Status**: success
**Duration**: 0.03s
**Tokens**: 0

**External Observation**:
- Files created: 0
- Files modified: 0
- Commands: 0

**Internal Observation**:
- Reasoning steps: 0
- Decisions made: 0
- Tools called: 0

### Execution 2 (if ran)

**Status**: success
**Duration**: 0.01s
**Tokens**: 0

**External Observation**:
- Files created: 0
- Files modified: 0
- Commands: 0

**Internal Observation**:
- Reasoning steps: 0
- Decisions made: 0
- Tools called: 0

## Comparative Analysis

**Consistency**: same_outcome
**Strategy Variance**: Both executions followed similar approach
**Effectiveness**: Execution 2 was faster (0.01s vs 0.03s)

**Patterns Identified**:
- Consistent result: success
```

**JSON Equivalent** (`trace_<timestamp>.json`):
```json
{
  "trace_id": "1760510850655276",
  "agent_name": "user_interpret",
  "prompt": "Show me the ROADMAP",
  "created_at": "2025-10-15T08:47:30.655276Z",
  "agent_identity": {
    "target_agent": "user_interpret",
    "agent_objective": "Interpret user intent and delegate appropriately",
    "success_criteria": "Correct intent, accurate sentiment, appropriate delegation"
  },
  "executions": [
    {
      "execution_id": 1,
      "agent_plan": [
        "Analyze user sentiment",
        "Interpret user intent",
        "Choose appropriate agent",
        "Generate response"
      ],
      "plan_progress": {
        "Analyze user sentiment": {"status": "completed", "timestamp": "2025-10-15T08:47:30.001Z"},
        "Interpret user intent": {"status": "completed", "timestamp": "2025-10-15T08:47:30.015Z"},
        "Choose appropriate agent": {"status": "completed", "timestamp": "2025-10-15T08:47:30.020Z"},
        "Generate response": {"status": "completed", "timestamp": "2025-10-15T08:47:30.655Z"}
      },
      "difficulties": [],
      "concerns": [],
      "external_observation": {
        "git_changes": [],
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
        "commands_executed": []
      },
      "internal_observation": {
        "reasoning_steps": [
          "User asked to see ROADMAP",
          "Intent: view_roadmap",
          "Sentiment: neutral",
          "Delegate to: project_manager"
        ],
        "decisions_made": [
          "Classified as view_roadmap intent",
          "Selected project_manager agent"
        ],
        "tools_called": [],
        "context_used": ["bullet_023", "bullet_045"],
        "context_ignored": []
      },
      "result_status": "success",
      "duration_seconds": 0.03,
      "token_usage": 0
    },
    {
      "execution_id": 2,
      "external_observation": {
        "git_changes": [],
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
        "commands_executed": []
      },
      "internal_observation": {
        "reasoning_steps": [
          "User asked to see ROADMAP",
          "Intent: view_roadmap",
          "Sentiment: neutral",
          "Delegate to: project_manager"
        ],
        "decisions_made": [
          "Classified as view_roadmap intent",
          "Selected project_manager agent"
        ],
        "tools_called": [],
        "context_used": ["bullet_023", "bullet_045"],
        "context_ignored": []
      },
      "result_status": "success",
      "duration_seconds": 0.01,
      "token_usage": 0
    }
  ],
  "comparative_observations": {
    "consistency": "same_outcome",
    "strategy_variance": "Both executions followed similar approach",
    "effectiveness_comparison": "Execution 2 was faster (0.01s vs 0.03s)",
    "patterns_identified": [
      "Consistent result: success"
    ]
  },
  "second_execution_reason": "Duration < 30s AND no files modified",
  "helpful_context_elements": ["bullet_023", "bullet_045"],
  "problematic_context_elements": [],
  "new_insights_surfaced": [
    "Intent interpretation for view_roadmap is accurate"
  ]
}
```

**When Second Execution Skipped**:
```json
{
  "executions": [
    {
      "execution_id": 1,
      "duration_seconds": 180,
      "files_modified": ["coffee_maker/app.py", "tests/test_app.py"],
      ...
    }
  ],
  "second_execution_reason": "SKIPPED: Long execution (180s > 30s threshold) and files modified (2 files)",
  "comparative_observations": null
}
```

### 2. Delta Items (Reflector)

**Location**: `docs/reflector/deltas/[agent_name]/YYYY-MM-DD_batch_N.json`

**Purpose**: Actionable insights extracted from traces

**Structure**:
```json
{
  "delta_id": "delta_20251015_001",
  "agent_name": "user_interpret",
  "generated_at": "2025-10-15T10:00:00Z",
  "traces_analyzed": [
    "1760510850655276",
    "1760510893409321",
    "1760510893465998"
  ],
  "insights": {
    "success_patterns": [
      {
        "delta_id": "delta_20251015_001_sp1",
        "insight_type": "success_pattern",
        "title": "View ROADMAP intent interpretation",
        "description": "When user says 'show roadmap', 'view roadmap', or similar, interpret as view_roadmap intent with high confidence",
        "recommendation": "For queries containing 'roadmap' + 'show'/'view'/'display', classify as view_roadmap and delegate to project_manager",
        "evidence": [
          {
            "trace_id": "1760510850655276",
            "execution_id": 1,
            "example": "User said 'Show me the ROADMAP' → Correctly interpreted as view_roadmap"
          }
        ],
        "applicability": "All roadmap-related queries",
        "priority": 4,
        "confidence": 0.95,
        "action": "add_new",
        "related_bullets": []
      }
    ],
    "failure_modes": [
      {
        "delta_id": "delta_20251015_001_fm1",
        "insight_type": "failure_mode",
        "title": "Sentiment analysis timeout on long messages",
        "description": "Sentiment analysis times out on messages longer than 500 characters",
        "recommendation": "For messages > 500 chars, use simpler sentiment detection or skip sentiment analysis",
        "evidence": [
          {
            "trace_id": "1760510893409321",
            "execution_id": 1,
            "example": "500+ char message caused sentiment analysis to timeout after 5s"
          }
        ],
        "applicability": "Long user messages (> 500 chars)",
        "priority": 3,
        "confidence": 0.85,
        "action": "add_new",
        "related_bullets": []
      }
    ],
    "optimizations": [
      {
        "delta_id": "delta_20251015_001_opt1",
        "insight_type": "optimization",
        "title": "Cache sentiment analysis results",
        "description": "Sentiment analysis for similar phrases is repeated unnecessarily",
        "recommendation": "Implement caching for sentiment analysis results keyed by message hash",
        "evidence": [
          {
            "trace_id": "1760510893465998",
            "execution_id": 1,
            "example": "Phrase 'show me' analyzed 15 times with same result"
          }
        ],
        "applicability": "All sentiment analysis calls",
        "priority": 2,
        "confidence": 0.80,
        "action": "add_new",
        "related_bullets": []
      }
    ]
  }
}
```

### 3. Playbooks (Curator)

**Location**: `docs/curator/playbooks/[agent_name]_playbook.json`

**Purpose**: Evolving best practices for agent

**Structure**:
```json
{
  "agent_name": "user_interpret",
  "last_updated": "2025-10-15T10:30:00Z",
  "size": 47,
  "max_size": 150,
  "effectiveness": 0.92,
  "bullets": [
    {
      "id": "bullet_001",
      "category": "Intent Interpretation",
      "content": "When user says 'implement' or 'add feature', interpret as add_feature intent with high confidence (0.95+). Delegate to code_developer.",
      "confidence": 0.95,
      "helpful_count": 25,
      "unhelpful_count": 2,
      "pruned_count": 0,
      "source_traces": ["trace_001", "trace_012", "trace_045"],
      "created_at": "2025-10-01T00:00:00Z",
      "last_updated": "2025-10-15T10:30:00Z",
      "embedding": [0.012, 0.045, ...]
    },
    {
      "id": "bullet_002",
      "category": "Sentiment Analysis",
      "content": "For messages > 500 chars, use simpler sentiment detection or skip sentiment analysis to avoid timeout",
      "confidence": 0.85,
      "helpful_count": 8,
      "unhelpful_count": 0,
      "pruned_count": 0,
      "source_traces": ["trace_023", "trace_034"],
      "created_at": "2025-10-15T10:30:00Z",
      "last_updated": "2025-10-15T10:30:00Z",
      "embedding": [0.023, 0.067, ...]
    }
  ],
  "health_metrics": {
    "total_bullets": 47,
    "avg_helpful_count": 5.3,
    "effectiveness_ratio": 0.92,
    "bullets_added_this_session": 1,
    "bullets_updated_this_session": 3,
    "bullets_pruned_this_session": 0,
    "coverage_score": 0.78
  }
}
```

### 4. Feedback History (Curator)

**Location**: `docs/curator/feedback/[agent_name]_feedback.jsonl`

**Purpose**: Track user feedback on playbook effectiveness

**Structure** (JSONL - one JSON object per line):
```jsonl
{"timestamp": "2025-10-15T08:50:00Z", "bullet_id": "bullet_001", "helpful": true, "user_comment": "Yes, intent was correct"}
{"timestamp": "2025-10-15T09:15:00Z", "bullet_id": "bullet_002", "helpful": true, "user_comment": "Timeout avoided"}
{"timestamp": "2025-10-15T10:00:00Z", "bullet_id": "bullet_012", "helpful": false, "user_comment": "Wrong agent selected"}
```

### 5. Conversation History (user_interpret)

**Location**: `docs/user_interpret/conversation_history.jsonl`

**Purpose**: Log all user interactions for proactive suggestions

**Structure** (JSONL):
```jsonl
{"timestamp": "2025-10-15T08:47:30Z", "user_message": "Show me the ROADMAP", "intent": "view_roadmap", "sentiment": "neutral", "delegated_to": "project_manager", "satisfaction": null}
{"timestamp": "2025-10-15T09:30:00Z", "user_message": "Implement login feature", "intent": "add_feature", "sentiment": "neutral", "delegated_to": "code_developer", "satisfaction": 5}
{"timestamp": "2025-10-15T10:15:00Z", "user_message": "Where is auth code?", "intent": "code_search", "sentiment": "neutral", "delegated_to": "code-searcher", "satisfaction": 4}
```

### 6. User Requests (user_interpret)

**Location**: `docs/user_interpret/user_requests.json`

**Purpose**: Track all user requests and their status

**Structure**:
```json
{
  "feature_requests": [
    {
      "id": "feature_20251015_093000",
      "description": "Login feature",
      "status": "in_progress",
      "created_at": "2025-10-15T09:30:00Z",
      "delegated_to": "code_developer",
      "estimated_completion": "2025-10-16T00:00:00Z",
      "result_location": null
    }
  ],
  "bug_reports": [
    {
      "id": "bug_20251015_101500",
      "description": "Tests failing",
      "status": "completed",
      "created_at": "2025-10-15T10:15:00Z",
      "delegated_to": "code_developer",
      "completed_at": "2025-10-15T11:00:00Z",
      "result_location": "/tests/test_auth.py"
    }
  ],
  "questions": [
    {
      "id": "question_20251015_084730",
      "question": "Show me the ROADMAP",
      "status": "completed",
      "created_at": "2025-10-15T08:47:30Z",
      "delegated_to": "project_manager",
      "answered_at": "2025-10-15T08:47:35Z"
    }
  ]
}
```

---

## Agent Execution Flow

### Standard Execution (with ACE)

```python
# Simplified execution flow

# 1. user_listener gets user input
user_input = user_listener.get_input()  # "Implement login feature"

# 2. user_interpret analyzes intent
interpretation = user_interpret.analyze(user_input)
# Result: {
#   "intent": "add_feature",
#   "sentiment": "neutral",
#   "delegate_to": "code_developer"
# }

# 3. user_listener delegates to agent (wrapped by ACE)
result = ace_generator.execute_with_trace(
    agent=code_developer,
    query="Implement login feature",
    playbook=load_playbook("code_developer")
)

# 4. ACE Generator captures execution
# - PRE: git status, file tree
# - EXECUTION 1: Run agent, capture observations
# - CONDITIONAL EXECUTION 2: If fast and no files, run again
# - POST: Save trace

# 5. Trace saved to docs/generator/traces/

# 6. (Later) Reflector analyzes traces
deltas = reflector.analyze_batch(agent_name="code_developer", batch_size=5)

# 7. Curator consolidates deltas
playbook = curator.curate(agent_name="code_developer", deltas=deltas)

# 8. Next execution uses updated playbook
# Cycle repeats...
```

### Plan Progress Tracking (During Execution)

Agents can report their progress during execution:

```python
# Inside agent implementation

# 1. Declare plan
self._set_plan([
    "Read technical spec",
    "Create auth module",
    "Write tests",
    "Verify DoD"
])

# 2. Update progress as you work
self._update_plan_progress("Read technical spec", "completed")
self._update_plan_progress("Create auth module", "in_progress")

# 3. Report difficulties
self._report_difficulty("Authentication library not found", severity="medium")

# 4. Report concerns
self._report_concern("Tests may fail due to missing fixtures")

# 5. Continue execution
self._update_plan_progress("Create auth module", "completed")
self._update_plan_progress("Write tests", "in_progress")
```

This tracking is captured in the trace and used by Reflector to identify patterns.

---

## Workflow Triggers

### Automatic Triggers

1. **Trace Generation**: Every agent execution (if ACE enabled)
   - Happens automatically when agent runs
   - No manual intervention needed

2. **Feedback Suggestions**: Every user_listener session
   - user_listener checks for pending feedback questions
   - Displays to user at appropriate time

### Manual Triggers

1. **Reflection**:
   ```bash
   poetry run reflector analyze code_developer
   poetry run reflector analyze user_interpret
   ```

2. **Curation**:
   ```bash
   poetry run curator curate code_developer
   poetry run curator curate user_interpret
   ```

3. **View Playbook** (via user_listener):
   ```bash
   poetry run user-listener
   # In UI: /playbook code_developer
   ```

4. **Trigger Curation** (via user_listener):
   ```bash
   poetry run user-listener
   # In UI: /curate code_developer
   ```

### Scheduled Triggers (Future)

Configurable via environment variables:

- **Auto-Reflect**: `ACE_AUTO_REFLECT=true` (runs after N executions)
- **Auto-Curate**: `ACE_AUTO_CURATE=true` (runs daily/weekly)

Example GitHub Action:
```yaml
# .github/workflows/ace-curation.yml
name: ACE Daily Curation

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am

jobs:
  curate:
    runs-on: ubuntu-latest
    steps:
      - run: poetry run reflector analyze --all
      - run: poetry run curator curate --all
```

---

## Agent Responsibilities

### user_interpret
- **Owned Docs**: `docs/user_interpret/`
- **Creates**:
  - `conversation_history.jsonl`: All user interactions
  - `user_requests.json`: Feature requests, bugs, questions
  - `conversation_summaries.json`: Daily summaries
  - `proactive_context.json`: Context for suggestions
- **Reads**: Own docs for context, playbook for guidance
- **ACE Learning**: High volume, fast feedback

### user_listener
- **Owned Docs**: None (UI only)
- **Creates**: Nothing (displays UI)
- **Reads**: All (for display purposes)
- **Delegates**: To all other agents
- **Shows**: Feedback questions from curator
- **ACE Learning**: Disabled (UI only)

### code_developer
- **Owned Docs**: None (creates code, not docs)
- **Creates**: Python code, tests, configuration files
- **Reads**: ROADMAP, technical specs, playbook
- **Updates**: ROADMAP status (Planned → In Progress → Complete)
- **ACE Learning**: Learns implementation patterns
- **Trace Examples**: "Created authentication module", "Fixed bug in CLI"

### project_manager
- **Owned Docs**: `docs/` (all documentation)
- **Creates**: Technical specs, ROADMAP updates, analysis docs
- **Reads**: All code and docs (for context)
- **ACE Learning**: Strategic decision patterns
- **Trace Examples**: "Created technical spec", "Updated ROADMAP"

### Generator (ACE)
- **Owned Docs**: `docs/generator/traces/`
- **Creates**: Trace JSON/Markdown files
- **Reads**: Agent execution context
- **ACE Role**: Observes all agents

### Reflector (ACE)
- **Owned Docs**: `docs/reflector/deltas/`
- **Creates**: Delta item JSON files
- **Reads**: Generator traces
- **ACE Role**: Extracts insights

### Curator (ACE)
- **Owned Docs**: `docs/curator/playbooks/`, `docs/curator/feedback/`
- **Creates**: Playbook JSON, feedback JSONL, curation reports
- **Reads**: Reflector deltas, feedback history
- **ACE Role**: Maintains evolving playbooks

---

## Success Metrics

### Trace Coverage
- **Target**: 100% of agent executions traced
- **Current**: Check `docs/generator/traces/` vs. total executions

### Reflection Frequency
- **Target**: Batch of 5 traces analyzed together
- **Frequency**: Manual OR after every 5 executions

### Playbook Growth
- **Target**: 5-10 new bullets per week
- **Limit**: Max 150 bullets per agent
- **Pruning**: 5-10% pruned per month

### Feedback Rate
- **Target**: User feedback for 50%+ of sessions
- **Method**: curator suggests questions, user_listener asks

### Effectiveness Score
- **Target**: > 0.85 (helpful / (helpful + harmful))
- **Current**: Check playbook health metrics

### Coverage Score
- **Target**: > 0.70 (strategy space coverage)
- **Calculation**: Based on bullet diversity and applicability

---

## Examples

### Example 1: Feature Request

**User**: "Implement login feature"

**Flow**:
1. **user_listener** displays UI, gets input
2. **user_interpret** analyzes (ACE observes):
   - Intent: add_feature
   - Sentiment: neutral
   - Delegate to: code_developer
3. **user_listener** delegates to **code_developer** (ACE observes):
   - Generator wraps execution
   - code_developer implements feature
   - Trace saved: `trace_1760520000000000.json`
4. **Reflector** (later) analyzes trace:
   - Pattern: "Read spec first" → success
   - Delta: "Always read technical spec before implementation"
5. **Curator** consolidates delta:
   - Checks similarity with existing bullets
   - Adds to playbook as `bullet_048`
6. **Next execution**: code_developer uses updated playbook

**Trace Result**:
```
Duration: 180s
Files modified: 5 (coffee_maker/auth/*.py)
Second execution: SKIPPED (too long, files modified)
Result: success
```

### Example 2: Quick Question

**User**: "Show me the ROADMAP"

**Flow**:
1. **user_listener** displays UI, gets input
2. **user_interpret** analyzes (ACE observes):
   - Intent: view_roadmap
   - Sentiment: neutral
   - Delegate to: project_manager
3. **user_listener** delegates to **project_manager** (ACE observes):
   - Generator wraps execution
   - project_manager displays ROADMAP
   - Duration: 2s, no files modified
   - **Second execution runs**: Compares consistency
   - Trace saved: `trace_1760520001000000.json`
4. **Reflector** analyzes both executions:
   - Pattern: "Both executions consistent"
   - Delta: "view_roadmap intent is accurate"
5. **Curator** updates playbook:
   - Increments helpful_count for `bullet_001`

**Trace Result**:
```
Duration: 2s (execution 1), 1.5s (execution 2)
Files modified: 0
Second execution: RAN (fast query, valuable comparison)
Result: success (both executions)
Consistency: same_outcome
```

### Example 3: Feedback Loop

**Scenario**: curator detects low effectiveness for bullet_012

**Flow**:
1. **Curator** generates feedback question:
   - "Was the agent selection correct for your last request?"
2. **user_listener** shows question during next session:
   - User: "Yes, code_developer was correct"
3. **FeedbackSuggestor** records feedback:
   - `bullet_012.helpful_count++`
   - Saves to `docs/curator/feedback/code_developer_feedback.jsonl`
4. **Next curation**: bullet_012 has higher helpful_count, not pruned

---

## Appendix: File Structure

```
MonolithicCoffeeMakerAgent/
├── docs/
│   ├── generator/
│   │   └── traces/
│   │       ├── 2025-10-15/
│   │       │   ├── trace_1760510850655276.md
│   │       │   ├── trace_1760510850655276.json
│   │       │   └── ...
│   │       └── 2025-10-16/
│   │
│   ├── reflector/
│   │   └── deltas/
│   │       ├── code_developer/
│   │       │   ├── 2025-10-15_batch_1.json
│   │       │   └── ...
│   │       ├── user_interpret/
│   │       │   ├── 2025-10-15_batch_1.json
│   │       │   └── ...
│   │       └── ...
│   │
│   ├── curator/
│   │   ├── playbooks/
│   │   │   ├── code_developer_playbook.json
│   │   │   ├── user_interpret_playbook.json
│   │   │   └── ...
│   │   └── feedback/
│   │       ├── code_developer_feedback.jsonl
│   │       ├── user_interpret_feedback.jsonl
│   │       └── ...
│   │
│   └── user_interpret/
│       ├── conversation_history.jsonl
│       ├── user_requests.json
│       ├── conversation_summaries.json
│       └── proactive_context.json
│
└── coffee_maker/
    └── autonomous/
        └── ace/
            ├── generator.py
            ├── reflector.py
            ├── curator.py
            └── ...
```

---

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Complete workflow documentation
