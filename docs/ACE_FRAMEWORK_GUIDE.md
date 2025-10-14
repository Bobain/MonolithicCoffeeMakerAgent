# ACE Framework Guide

**Version**: 1.0
**Date**: 2025-10-14
**Reference**: https://www.arxiv.org/abs/2510.04618

---

## Table of Contents

1. [What is ACE Framework?](#what-is-ace-framework)
2. [Architecture Overview](#architecture-overview)
3. [Components](#components)
4. [How It Works](#how-it-works)
5. [Enabling ACE for an Agent](#enabling-ace-for-an-agent)
6. [Reviewing Execution Traces](#reviewing-execution-traces)
7. [Managing Playbooks](#managing-playbooks)
8. [Curator Health Metrics](#curator-health-metrics)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## What is ACE Framework?

**ACE (Agentic Context Engineering)** is a system for continuous agent improvement through:
- **Execution observation** - Capturing detailed traces from every agent run
- **Cross-execution analysis** - Reflector identifies patterns across multiple traces over time
- **Insight extraction** - Analyzing traces to find what works and what fails
- **Playbook curation** - Maintaining evolving best practices

### Key Benefits

1. **Continuous Improvement**: Agents learn from every execution
2. **Failure Prevention**: Captures and addresses failure modes
3. **Best Practice Evolution**: Builds library of proven strategies
4. **Context Relevance**: Keeps agent context current and accurate
5. **No Manual Updates**: Automated learning loop

### Research Foundation

Based on the paper "Agentic Context Engineering" (arXiv:2510.04618), ACE enables agents to:
- Observe their own execution
- Reflect on successes and failures
- Curate evolving playbooks
- Prevent context collapse through semantic de-duplication

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ACE Framework                            │
│                                                                   │
│  User Request                                                     │
│       ↓                                                           │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  GENERATOR (Execution Observation)                      │     │
│  │                                                          │     │
│  │  1. Capture pre-execution state (git, files)            │     │
│  │  2. Execute target agent                                │     │
│  │  3. Capture external observation (git changes, files)   │     │
│  │  4. Capture internal observation (reasoning, tools)     │     │
│  │  5. Save comprehensive trace to docs/generator/traces/ │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                               │
│                   ↓ Execution Traces                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  REFLECTOR (Insight Extraction)                        │     │
│  │                                                          │     │
│  │  1. Load execution traces                               │     │
│  │  2. Analyze what worked / what failed                   │     │
│  │  3. Identify patterns and missing knowledge             │     │
│  │  4. Extract actionable insights (deltas)                │     │
│  │  5. Assign priority and confidence levels               │     │
│  │  6. Save deltas to docs/reflector/deltas/              │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                               │
│                   ↓ Delta Items (Insights)                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  CURATOR (Playbook Consolidation)                      │     │
│  │                                                          │     │
│  │  1. Load new deltas from Reflector                      │     │
│  │  2. Load existing playbook                              │     │
│  │  3. Perform semantic de-duplication                     │     │
│  │  4. Merge/update/add insights                           │     │
│  │  5. Prune low-value or harmful bullets                  │     │
│  │  6. Update health metrics                               │     │
│  │  7. Save playbook to docs/curator/playbooks/           │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                               │
│                   ↓ Updated Playbook                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  GENERATOR (Next Execution)                            │     │
│  │                                                          │     │
│  │  Uses updated playbook as context for next request      │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Generator

**Role**: Orchestrates execution and captures detailed traces with conditional dual execution for comparison

**Location**: `.claude/agents/generator.md`

**Responsibilities**:
- Execute target agent once per user request (always fully observed)
- Conditionally run second execution for comparison (cost optimization)
- Capture pre-execution state (git status, file tree)
- Capture external observation (git changes, files created/modified/deleted)
- Capture internal observation (reasoning steps, tools called, decisions made, context usage)
- Capture post-execution state and results
- Save comprehensive trace to `docs/generator/traces/YYYY-MM-DD/trace_<timestamp>.json`

**Conditional Second Execution**:
- Runs ONLY IF: duration < 30 seconds AND no owned files modified
- Rationale: Quick, informational queries benefit from comparison; expensive implementations do not
- Cost savings: Avoids duplicating expensive feature implementations

**Key Prompt**: `.claude/commands/ace-generator-observe.md`

### 2. Reflector

**Role**: Analyzes traces and extracts actionable insights

**Location**: `.claude/agents/reflector.md`

**Responsibilities**:
- Load and analyze execution traces from multiple agent runs over time
- Compare traces to identify patterns (what consistently works, what consistently fails)
- Extract concrete, specific insights (not generic advice)
- Assign priority (1-5) and confidence (0.0-1.0) levels based on evidence strength
- Generate delta items for Curator
- Save deltas to `docs/reflector/deltas/YYYY-MM-DD/deltas_<timestamp>.json`

**Key Insight**: Reflector performs cross-execution comparison - it analyzes MULTIPLE traces from different runs to identify patterns, not just a single trace.

**Key Prompt**: `.claude/commands/ace-reflector-extract.md`

**Insight Types**:
- `success_pattern` - Strategy that consistently leads to success
- `failure_mode` - Pattern that consistently leads to failure
- `optimization` - Way to improve efficiency or performance
- `best_practice` - General guideline for better outcomes
- `tool_usage` - Specific guidance on using tools effectively
- `domain_concept` - Domain knowledge that should be captured

### 3. Curator

**Role**: Maintains playbooks with semantic de-duplication

**Location**: `.claude/agents/curator.md`

**Responsibilities**:
- Load new deltas from Reflector
- Load existing playbook
- Perform semantic de-duplication (cosine similarity of embeddings)
- Merge/update/add insights based on similarity
- Prune low-value or harmful bullets
- Track playbook health metrics
- Save playbook to `docs/curator/playbooks/<agent>_playbook.json`

**Key Prompt**: `.claude/commands/ace-curator-consolidate.md`

**De-duplication Rules**:
- Similarity > 0.90: Merge as identical
- Similarity > 0.85: Consolidate if same category
- Similarity > 0.75: Update if delta more specific
- Similarity < 0.75: Keep separate

---

## How It Works

### Step-by-Step Flow

#### Phase 1: Execution with Observation (Generator)

```bash
# User makes a request to code_developer
User: "Implement the authentication feature"

# Generator wraps the execution
Generator:
  1. Capture pre-execution state (git status, file tree)
  2. Execute code_developer(request, current_playbook) - FIRST EXECUTION (always runs)
  3. Observe during and after execution:
     - External: git diff, files created, files modified
     - Internal: reasoning trace, tools called, decisions made
     - Context usage: which playbook bullets were referenced
     - Duration: 180 seconds (3 minutes)
  4. Evaluate for second execution:
     - Duration: 180s > 30s threshold → TOO LONG
     - Files modified: 5 files created → REAL WORK DONE
     - Decision: SKIP second execution (expensive to duplicate, low comparison value)
  5. Note in trace: "Second execution skipped: Long execution (180s) and files modified (5 created)"
  6. Save comprehensive trace to docs/generator/traces/2025-10-14/trace_1728925234.json

# Example where second execution WOULD run:
User: "What's the status of PRIORITY 5?"

Generator:
  1. Capture pre-execution state
  2. Execute code_developer (informational query) - FIRST EXECUTION
     - Duration: 12 seconds
     - Files modified: 0 (just querying status)
  3. Evaluate for second execution:
     - Duration: 12s < 30s threshold → QUICK ✓
     - Files modified: 0 → NO REAL WORK ✓
     - Decision: RUN second execution (cheap to duplicate, valuable comparison)
  4. Execute code_developer (same query) - SECOND EXECUTION
  5. Compare both executions for consistency and strategy variance
  6. Save trace with both executions
```

**Trace Example** (`trace_1728925234.json`):
```json
{
  "trace_id": "trace_1728925234",
  "timestamp": "2025-10-14T10:30:00Z",
  "agent_identity": {
    "target_agent": "code_developer",
    "agent_objective": "Implement features from ROADMAP",
    "success_criteria": "Code runs, tests pass, DoD verified"
  },
  "user_query": "Implement the authentication feature",
  "execution": {
    "execution_id": "trace_1728925234",
    "pre_execution_state": {
      "git_status": "clean",
      "relevant_files": ["coffee_maker/app.py"]
    },
    "external_observation": {
      "files_created": ["coffee_maker/auth/login.py", "coffee_maker/auth/__init__.py"],
      "files_modified": ["coffee_maker/app.py"],
      "git_changes": ["+150, -10"]
    },
    "internal_observation": {
      "reasoning_steps": [
        "Read authentication spec",
        "Create auth module structure",
        "Implement login function with bcrypt"
      ],
      "tools_called": [
        {"tool": "Read", "params": {"file": "docs/AUTH_SPEC.md"}},
        {"tool": "Write", "params": {"file": "coffee_maker/auth/login.py"}}
      ],
      "context_used": ["bullet_023", "bullet_045"],
      "context_ignored": ["bullet_012"]
    },
    "result_status": "success",
    "duration_seconds": 45,
    "token_usage": 3200
  },
  "observations_for_reflector": {
    "strategies_used": ["Read spec first", "Used bcrypt for hashing"],
    "helpful_context": ["bullet_023 (use bcrypt)", "bullet_045 (read spec first)"],
    "missing_knowledge": ["No guidance on where to place auth module"]
  }
}
```

#### Phase 2: Insight Extraction (Reflector)

```bash
# Reflector analyzes MULTIPLE traces over time
Reflector:
  1. Load traces from docs/generator/traces/2025-10-14/ (may include 10-20 traces)
  2. Compare traces to identify patterns:
     - Cross-trace analysis: What strategy appears in multiple successful traces?
     - What strategies appear in failed traces?
     - What's consistently missing across traces?
  3. Example pattern detection:
     - Trace 1 (auth): Read spec first → success
     - Trace 2 (dashboard): Read spec first → success
     - Trace 3 (api): Skipped reading spec → failure
     - Pattern: "Read spec first" consistently correlates with success
  4. Extract insights with evidence:
     - "Always read technical spec before implementation" (confidence: 0.85, evidence: 3 traces)
     - "For authentication, use bcrypt" (confidence: 0.95, evidence: 2 traces)
  5. Assign priority and confidence based on evidence strength
  6. Save to docs/reflector/deltas/2025-10-14/deltas_1728925300.json
```

**Key Point**: Reflector doesn't analyze a single trace in isolation. It compares MULTIPLE traces to find what consistently works or fails.

**Delta Example** (`deltas_1728925300.json`):
```json
{
  "metadata": {
    "agent_name": "code_developer",
    "num_traces_analyzed": 1,
    "analysis_timestamp": "2025-10-14T10:35:00Z"
  },
  "deltas": [
    {
      "delta_id": "delta_1728925300_001",
      "insight_type": "best_practice",
      "title": "Read technical spec before implementation",
      "description": "Always use Read tool to review the technical spec before starting implementation. This ensures understanding of requirements and DoD criteria.",
      "recommendation": "Before writing any code, call Read(docs/PRIORITY_X_TECHNICAL_SPEC.md) to understand the full context.",
      "evidence": [
        {
          "trace_id": "trace_1728925234",
          "execution_id": 1,
          "example": "Read docs/AUTH_SPEC.md as first step, led to correct implementation"
        }
      ],
      "applicability": "All feature implementations from ROADMAP",
      "priority": 4,
      "confidence": 0.85,
      "action": "add_new",
      "related_bullets": []
    },
    {
      "delta_id": "delta_1728925300_002",
      "insight_type": "domain_concept",
      "title": "Use bcrypt for password hashing",
      "description": "For authentication features, always use bcrypt library for secure password hashing. Never store passwords in plain text.",
      "recommendation": "Import bcrypt and use bcrypt.hashpw(password, bcrypt.gensalt()) for hashing.",
      "evidence": [
        {
          "trace_id": "trace_1728925234",
          "execution_id": 1,
          "example": "Used bcrypt correctly in auth/login.py"
        }
      ],
      "applicability": "Any feature involving user authentication or password storage",
      "priority": 5,
      "confidence": 0.95,
      "action": "add_new",
      "related_bullets": []
    }
  ]
}
```

#### Phase 3: Playbook Consolidation (Curator)

```bash
# Curator integrates insights
Curator:
  1. Load deltas from docs/reflector/deltas/2025-10-14/
  2. Load existing playbook docs/curator/playbooks/code_developer_playbook.json
  3. For each delta:
     a. Compute semantic similarity with existing bullets
     b. If similarity > 0.90: Merge (increment helpful_count)
     c. If similarity > 0.85: Consolidate if same category
     d. If similarity < 0.75: Add as new bullet
  4. Prune low-value bullets (helpful_count < 2, age > 30 days)
  5. Update health metrics
  6. Save playbook
```

**Playbook Example** (`code_developer_playbook.json`):
```json
{
  "playbook_version": "1.2.5",
  "agent_name": "code_developer",
  "agent_objective": "Implement features from ROADMAP autonomously",
  "last_updated": "2025-10-14T10:40:00Z",
  "total_bullets": 52,

  "categories": {
    "core_strategies": {
      "high_priority_high_confidence": [
        {
          "bullet_id": "bullet_001",
          "content": "Always read technical spec (docs/PRIORITY_X_TECHNICAL_SPEC.md) before implementation to understand requirements and DoD criteria.",
          "helpful_count": 15,
          "harmful_count": 0,
          "priority": 4,
          "confidence": 0.85,
          "created_at": "2025-10-01T10:00:00Z",
          "last_updated": "2025-10-14T10:40:00Z"
        }
      ]
    },
    "domain_concepts": [
      {
        "bullet_id": "bullet_023",
        "content": "For authentication features, use bcrypt library for secure password hashing (bcrypt.hashpw). Never store passwords in plain text.",
        "helpful_count": 1,
        "harmful_count": 0,
        "priority": 5,
        "confidence": 0.95,
        "created_at": "2025-10-14T10:40:00Z",
        "last_updated": "2025-10-14T10:40:00Z"
      }
    ]
  },

  "health_metrics": {
    "total_bullets": 52,
    "avg_helpful_count": 3.2,
    "effectiveness_ratio": 0.94,
    "bullets_added_this_session": 1,
    "bullets_updated_this_session": 1,
    "coverage_score": 0.82
  }
}
```

#### Phase 4: Next Execution

```bash
# Next user request uses updated playbook
User: "Implement user registration feature"

Generator:
  # Loads playbook with new bullets about reading specs and bcrypt
  # Passes playbook to code_developer as context
  # code_developer uses bullets to guide implementation
  # Cycle repeats...
```

---

## Enabling ACE for an Agent

### Prerequisites

1. Agent must be configured in `.claude/agents/<agent>.md`
2. Agent must have clear objective and success criteria
3. Directory structure must exist:
   ```bash
   mkdir -p docs/generator/traces
   mkdir -p docs/reflector/deltas
   mkdir -p docs/curator/playbooks
   mkdir -p docs/curator/reports
   ```

### Integration Steps

#### Step 1: Modify Agent Invocation

**Before** (direct invocation):
```python
result = agent.execute(user_query)
```

**After** (ACE-wrapped):
```python
from coffee_maker.ace import Generator

generator = Generator(
    target_agent=agent,
    agent_objective="Implement features from ROADMAP",
    success_criteria="Code runs, tests pass, DoD verified"
)

result = generator.execute_with_observation(user_query)
```

#### Step 2: Schedule Reflection

Set up periodic reflection (e.g., after every 10 executions or daily):

```python
from coffee_maker.ace import Reflector

reflector = Reflector(agent_name="code_developer")

# Analyze last 24 hours of traces
deltas = reflector.analyze_recent_traces(hours=24)

# Save deltas
reflector.save_deltas(deltas)
```

#### Step 3: Schedule Curation

Set up periodic curation (e.g., daily or weekly):

```python
from coffee_maker.ace import Curator

curator = Curator(agent_name="code_developer")

# Load recent deltas
deltas = curator.load_recent_deltas(days=1)

# Consolidate into playbook
playbook = curator.consolidate(deltas)

# Save playbook
curator.save_playbook(playbook)
```

#### Step 4: Automation (Recommended)

Add to daemon or cron job:

```bash
# .github/workflows/ace-curation.yml
name: ACE Curation

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am

jobs:
  curate:
    runs-on: ubuntu-latest
    steps:
      - name: Run Reflector
        run: poetry run ace-reflector --agent code_developer

      - name: Run Curator
        run: poetry run ace-curator --agent code_developer
```

---

## Reviewing Execution Traces

### Trace Location

All traces are stored in:
```
docs/generator/traces/YYYY-MM-DD/trace_<timestamp>.json
```

### Viewing Traces

**CLI Command** (future):
```bash
poetry run ace-traces --agent code_developer --date 2025-10-14
```

**Manual Review**:
```bash
cd docs/generator/traces/2025-10-14
ls -lah
cat trace_1728925234.json | jq '.executions[] | .internal_observation.reasoning_steps'
```

### Trace Analysis

**What to Look For**:
1. **Consistency**: Did both executions reach same conclusion?
2. **Efficiency**: Which execution was faster/better?
3. **Context Usage**: Which bullets were referenced?
4. **Errors**: Were there any failures or exceptions?
5. **Tool Usage**: Were tools used appropriately?

**Example Analysis**:
```bash
# Show all tools used
jq '.executions[].internal_observation.tools_called[].tool' trace_*.json | sort | uniq -c

# Show context bullets used
jq '.executions[].internal_observation.context_used[]' trace_*.json | sort | uniq -c

# Show errors
jq '.executions[] | select(.result_status=="failure") | .errors' trace_*.json
```

---

## Managing Playbooks

### Playbook Location

Playbooks are stored in:
```
docs/curator/playbooks/<agent>_playbook.json
```

### Viewing Playbooks

**CLI Command** (future):
```bash
poetry run ace-playbook --agent code_developer --show
```

**Manual Review**:
```bash
cat docs/curator/playbooks/code_developer_playbook.json | jq '.categories'
```

### Playbook Operations

#### View All Bullets
```bash
jq '.categories | to_entries[] | .value[]' code_developer_playbook.json
```

#### View Top Bullets (by helpful_count)
```bash
jq '[.categories | to_entries[] | .value[] | select(.helpful_count > 5)] | sort_by(.helpful_count) | reverse | .[0:10]' code_developer_playbook.json
```

#### View Harmful Bullets
```bash
jq '[.categories | to_entries[] | .value[] | select(.harmful_count > .helpful_count)]' code_developer_playbook.json
```

#### View Recent Additions
```bash
jq '[.categories | to_entries[] | .value[] | select(.created_at > "2025-10-10")]' code_developer_playbook.json
```

### Manual Playbook Editing

**When to Edit**:
- Remove clearly incorrect bullets
- Merge redundant bullets
- Update outdated domain concepts
- Add critical missing knowledge

**How to Edit**:
1. Edit `docs/curator/playbooks/<agent>_playbook.json`
2. Update `last_updated` timestamp
3. Increment `playbook_version`
4. Document change in git commit

**Example**:
```bash
# Edit playbook
vim docs/curator/playbooks/code_developer_playbook.json

# Commit change
git add docs/curator/playbooks/code_developer_playbook.json
git commit -m "playbook: Remove outdated bullet_045 (deprecated library)"
```

---

## Curator Health Metrics

### Key Metrics

**Effectiveness Ratio**:
```
effectiveness_ratio = total_helpful_actions / (total_helpful_actions + total_harmful_actions)
```

Target: > 0.85

**Coverage Score**:
Estimate of strategy space coverage (0.0-1.0)
- 0.0-0.3: Very sparse coverage
- 0.3-0.6: Moderate coverage
- 0.6-0.8: Good coverage
- 0.8-1.0: Comprehensive coverage

**Update Frequency**:
```
update_frequency = bullets_updated / total_bullets
```

Target: 20-30% per week

**Pruning Rate**:
```
pruning_rate = bullets_pruned / total_bullets
```

Target: 5-10% per month

### Health Dashboard (Future)

```bash
poetry run ace-health --agent code_developer
```

Output:
```
ACE Health Dashboard - code_developer

Playbook Version: 1.2.5
Last Updated: 2025-10-14 10:40:00
Total Bullets: 52

Effectiveness Ratio: 0.94 ✓ (Target: > 0.85)
Coverage Score: 0.82 ✓ (Target: > 0.60)
Update Frequency: 0.25 ✓ (Target: 0.20-0.30)
Pruning Rate: 0.08 ✓ (Target: 0.05-0.10)

Recent Activity (Last 7 Days):
- Bullets Added: 5
- Bullets Updated: 12
- Bullets Pruned: 2

Top Bullets (by helpful_count):
1. bullet_007: "Read technical spec before implementation" (15)
2. bullet_012: "Use pytest for all test cases" (12)
3. bullet_023: "Use bcrypt for password hashing" (10)

Problematic Bullets (harmful > helpful):
(None)

Recommendations:
- Playbook health is excellent
- Continue current curation strategy
```

### Alerts

**Warning**: If effectiveness ratio drops below 0.80
**Action**: Review recent deltas for quality, increase Reflector precision

**Warning**: If total bullets > 150
**Action**: Aggressive pruning, consolidate redundant bullets

**Warning**: If coverage score < 0.60
**Action**: Focus Reflector on underrepresented domains

---

## Examples

### Example 1: code_developer ACE Integration

**Scenario**: Enable ACE for code_developer to learn implementation patterns

**Setup**:
```python
# coffee_maker/autonomous/daemon.py

from coffee_maker.ace import Generator, Reflector, Curator

class Daemon:
    def __init__(self):
        self.generator = Generator(
            target_agent="code_developer",
            agent_objective="Implement features from ROADMAP",
            success_criteria="Code runs, tests pass, DoD verified"
        )

    def process_priority(self, priority):
        # Wrap execution with ACE observation
        result = self.generator.execute_with_observation(
            user_query=f"Implement {priority.name}",
            current_playbook=self._load_playbook()
        )

        # Trigger reflection after every execution
        self._trigger_reflection()

        return result

    def _trigger_reflection(self):
        # Run reflector on recent traces
        reflector = Reflector(agent_name="code_developer")
        deltas = reflector.analyze_recent_traces(hours=1)
        reflector.save_deltas(deltas)

        # Run curator on recent deltas
        curator = Curator(agent_name="code_developer")
        recent_deltas = curator.load_recent_deltas(hours=1)
        playbook = curator.consolidate(recent_deltas)
        curator.save_playbook(playbook)
```

**Result**:
- Every priority implementation is observed
- Patterns are extracted automatically
- Playbook evolves with each execution
- code_developer improves over time

### Example 2: Analyzing Failure Modes

**Scenario**: code_developer keeps failing on file path issues

**Trace Shows**:
```json
{
  "execution_id": 1,
  "result_status": "failure",
  "errors": [
    "FileNotFoundError: coffee_maker/auth/login.py"
  ],
  "internal_observation": {
    "reasoning_steps": [
      "Assume coffee_maker/auth directory exists",
      "Write to coffee_maker/auth/login.py"
    ]
  }
}
```

**Reflector Extracts**:
```json
{
  "delta_id": "delta_001",
  "insight_type": "failure_mode",
  "title": "File path assumption leads to FileNotFoundError",
  "description": "Assuming directory exists before writing file causes failures. Always check or create directory first.",
  "recommendation": "Use os.makedirs(os.path.dirname(file_path), exist_ok=True) before Write tool.",
  "priority": 5,
  "confidence": 0.95,
  "action": "add_new"
}
```

**Curator Adds**:
```json
{
  "bullet_id": "bullet_053",
  "content": "Before writing to any file, ensure parent directory exists using os.makedirs(os.path.dirname(file_path), exist_ok=True). This prevents FileNotFoundError.",
  "helpful_count": 1,
  "priority": 5,
  "confidence": 0.95
}
```

**Next Execution**:
- code_developer uses bullet_053 as guidance
- Creates directory before writing file
- Success! No FileNotFoundError

---

## Troubleshooting

### Issue: Traces Not Being Generated

**Symptoms**:
- `docs/generator/traces/` is empty
- No trace files after agent execution

**Diagnosis**:
```bash
# Check generator is wrapping execution
grep -r "Generator" coffee_maker/autonomous/daemon.py

# Check directory exists
ls -lah docs/generator/traces/

# Check permissions
ls -ld docs/generator/traces/
```

**Solutions**:
1. Ensure Generator is wrapping agent execution
2. Create directory: `mkdir -p docs/generator/traces`
3. Check file permissions: `chmod 755 docs/generator/traces`

### Issue: Deltas Not Being Created

**Symptoms**:
- Traces exist but no deltas in `docs/reflector/deltas/`

**Diagnosis**:
```bash
# Check if Reflector is running
ps aux | grep reflector

# Check trace file format
cat docs/generator/traces/2025-10-14/trace_*.json | jq '.'
```

**Solutions**:
1. Ensure Reflector is scheduled (cron/GitHub Actions)
2. Validate trace JSON format
3. Check Reflector logs for errors

### Issue: Playbook Not Updating

**Symptoms**:
- Deltas exist but playbook unchanged

**Diagnosis**:
```bash
# Check playbook last_updated timestamp
jq '.last_updated' docs/curator/playbooks/code_developer_playbook.json

# Check Curator logs
tail -f logs/curator.log

# Check if deltas are being loaded
ls -lah docs/reflector/deltas/2025-10-14/
```

**Solutions**:
1. Ensure Curator is scheduled
2. Check semantic similarity threshold (may be too high)
3. Verify delta format matches expected schema

### Issue: Context Collapse

**Symptoms**:
- Playbook bullets becoming generic
- Loss of domain-specific terminology
- Effectiveness ratio declining

**Diagnosis**:
```bash
# Check average content length
jq '[.categories | to_entries[] | .value[] | .content | length] | add / length' playbook.json

# Check effectiveness ratio trend
jq '.health_metrics.effectiveness_ratio' playbook.json
```

**Solutions**:
1. Lower pruning rate (reduce from 10% to 5%)
2. Increase minimum content length requirement
3. Require domain-specific terms in new bullets
4. Manual playbook review and restoration

### Issue: Too Many Bullets

**Symptoms**:
- Playbook has > 150 bullets
- Coverage score not improving
- Redundant bullets

**Diagnosis**:
```bash
# Count total bullets
jq '.total_bullets' playbook.json

# Find semantically similar bullets
# (requires embeddings analysis script)
```

**Solutions**:
1. Increase semantic similarity threshold (0.75 → 0.80)
2. Run aggressive pruning session
3. Manual consolidation of redundant bullets
4. Adjust Reflector to be more selective

---

## Best Practices

### For Operators

1. **Monitor Health Metrics Weekly**
   - Check effectiveness ratio
   - Review coverage score
   - Identify problematic bullets

2. **Review Traces Regularly**
   - Look for failure patterns
   - Identify missing knowledge
   - Validate context usage

3. **Curate Playbooks Manually**
   - Remove obviously incorrect bullets
   - Merge redundant bullets monthly
   - Update outdated domain concepts

4. **Adjust Thresholds**
   - Tune semantic similarity based on results
   - Adjust pruning rate based on growth
   - Balance growth vs. refinement phases

### For Developers

1. **Write Clear Success Criteria**
   - Makes failure detection accurate
   - Helps Reflector extract relevant insights

2. **Maintain Trace Quality**
   - Capture comprehensive observations
   - Include reasoning steps
   - Log all tool calls

3. **Test ACE Integration**
   - Unit test Generator wrapper
   - Validate trace JSON schema
   - Test de-duplication logic

4. **Document Domain Concepts**
   - Add domain-specific tags
   - Include applicability conditions
   - Provide clear examples

---

## Future Enhancements

### Phase 2: Langfuse Integration

- Store all traces in Langfuse
- Track prompt versions
- A/B test playbook variations
- Advanced analytics dashboard

### Phase 3: Multi-Agent Playbooks

- Shared playbooks across agents
- Cross-agent pattern detection
- Agent collaboration insights

### Phase 4: Automated Tuning

- Self-adjusting similarity thresholds
- Automated pruning schedule optimization
- Predictive coverage analysis

---

## References

- **Research Paper**: [Agentic Context Engineering (arXiv:2510.04618)](https://www.arxiv.org/abs/2510.04618)
- **Agent Definitions**: `.claude/agents/generator.md`, `reflector.md`, `curator.md`
- **Prompt Templates**: `.claude/commands/ace-*.md`
- **Technical Spec**: `docs/PRIORITY_6_ACE_INTEGRATION_TECHNICAL_SPEC.md`
- **ROADMAP**: `docs/roadmap/ROADMAP.md`

---

**Last Updated**: 2025-10-14
**Version**: 1.0
**Status**: Documentation Complete, Implementation Pending
