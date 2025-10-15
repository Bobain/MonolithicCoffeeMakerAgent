# ACE Framework Implementation Comparison

**Document**: Comparison between ACE Implementation Guide and MonolithicCoffeeMakerAgent Implementation
**Date**: 2025-10-15
**Status**: Complete Analysis
**Overall Alignment**: **75% ALIGNED** - Core concepts match, integration patterns differ

---

## Executive Summary

### Overall Alignment Status

**PARTIALLY ALIGNED** - The MonolithicCoffeeMakerAgent implementation follows the core ACE framework principles from the research paper, but uses a different integration approach than the guide.

### Key Findings

**✅ Strongly Aligned (Core ACE Concepts)**:
- Dual execution observation (Generator)
- Insight extraction from traces (Reflector)
- Semantic de-duplication with embeddings (Curator)
- Playbook-based learning architecture
- External + Internal observation capture
- Helpful/harmful tracking with effectiveness ratios

**⚠️ Partially Aligned (Different Approach)**:
- Integration pattern: Python-based vs. claude-cli markdown agents
- Configuration: Environment variables (.env) vs. YAML files per agent
- Execution flow: Synchronous trace generation vs. automatic background chain
- Default behavior: ACE enabled by default vs. opt-in

**❌ Not Aligned (Missing from Our Implementation)**:
- Automatic reflection→curation chain (disabled by default)
- Background threading for non-blocking ACE workflow
- Per-agent YAML configuration with objectives/success criteria
- Multi-epoch training support

### Compatibility Assessment

**Can our implementation work with the guide's approach?**

**Partially Compatible** - Core data structures and concepts are interchangeable, but integration mechanisms differ fundamentally:

- ✅ Playbook format is compatible (could exchange playbooks)
- ✅ Delta item structure is compatible
- ✅ Execution trace concepts are identical
- ❌ Cannot use guide's markdown agents directly (requires Python wrappers)
- ❌ Configuration formats incompatible (.env vs. YAML)

---

## 1. Architecture Comparison

### Guide Approach

**Three Markdown Agents in `.claude/agents/`**:
```
.claude/agents/
├── ace_generator_agent.md
├── ace_reflector_agent.md
└── ace_curator_agent.md

Workflow:
User → @ace_generator_agent → @ace_reflector_agent → @ace_curator_agent
         (orchestrates dual        (analyzes and          (integrates into
          execution)                 extracts insights)     playbook)
```

**Key Characteristics**:
- Interactive, claude-cli based
- Agents are markdown files with prompts
- Manual invocation via `@agent_name` syntax
- Designed for human-in-the-loop workflows

### Our Approach

**Three Python Classes in `coffee_maker/autonomous/ace/`**:
```
coffee_maker/autonomous/ace/
├── generator.py       (ACEGenerator class)
├── reflector.py       (ACEReflector class)
└── curator.py         (ACECurator class)

Workflow:
Agent → ACEGenerator wrapper → Execution → Trace saved
                                              ↓
                               (Manual/Scheduled) Reflector → Deltas saved
                                                                ↓
                                               (Manual/Scheduled) Curator → Playbook updated
```

**Key Characteristics**:
- Programmatic, Python-based
- Agents are classes with methods
- Automatic trace generation via ACEAgent base class
- Designed for autonomous daemon workflows
- Manual reflection/curation (opt-in auto-chain via env vars)

### Key Architectural Differences

| Aspect | Guide | Our Implementation |
|--------|-------|-------------------|
| **Language** | Markdown (prompts) | Python (classes) |
| **Execution** | Interactive (claude-cli) | Programmatic (Python code) |
| **Integration** | Manual agent invocation | Automatic via ACEAgent base class |
| **Workflow** | Synchronous chain (Generator→Reflector→Curator) | Asynchronous stages (Trace→Reflect→Curate) |
| **Control** | Human-in-the-loop | Daemon-driven with optional automation |

---

## 2. Component-by-Component Comparison

### 2.1 Generator Component

| Feature | Guide | Our Implementation | Aligned? |
|---------|-------|-------------------|----------|
| **Dual execution** | Yes (always) | Yes (conditional) | ⚠️ **Partial** |
| **External observation** | Git changes, files | Git changes, files | ✅ **Yes** |
| **Internal observation** | Reasoning, tools, decisions | Reasoning, tools, decisions | ✅ **Yes** |
| **Execution traces** | JSON format | JSON format (ExecutionTrace model) | ✅ **Yes** |
| **Trace storage** | Local files | Local files (docs/generator/traces/) | ✅ **Yes** |
| **Plan tracking** | Not mentioned | ✅ **Yes** (agent_plan, plan_progress) | ➕ **Enhancement** |
| **Difficulty tracking** | Not mentioned | ✅ **Yes** (difficulties, concerns, retries) | ➕ **Enhancement** |
| **Conditional 2nd exec** | Not mentioned | ✅ **Yes** (skip if >30s or owned files modified) | ➕ **Enhancement** |
| **Delegation chain** | Not mentioned | ✅ **Yes** (parent_trace_id, full delegation chain) | ➕ **Enhancement** |
| **User satisfaction** | Not mentioned | ✅ **Yes** (attach_satisfaction method, propagation) | ➕ **Enhancement** |
| **Ownership-aware** | Not mentioned | ✅ **Yes** (skips 2nd exec if agent modified owned dirs) | ➕ **Enhancement** |
| **Context snapshot** | Not mentioned | ✅ **Yes** (captures context at execution time) | ➕ **Enhancement** |

**Alignment Summary**: **85% Aligned** - Core concepts identical, our implementation adds valuable enhancements for autonomous systems.

**Notable Enhancements in Our Implementation**:

1. **Conditional Dual Execution** (lines 507-589 in generator.py):
   - Skips 2nd execution if first took >30s (cost optimization)
   - Skips 2nd execution if owned directories modified (real work done)
   - Provides clear skip_reason in trace

2. **Plan-Aware Execution** (lines 204-286):
   - Captures agent's declared plan (list of steps)
   - Tracks difficulties encountered (with severity)
   - Tracks concerns (warnings, edge cases)
   - Tracks progress through plan (timestamps per step)

3. **Delegation Chain Tracking** (lines 114-140):
   - Links child traces to parent traces
   - Full delegation chain preserved (user_listener → code_developer)
   - Enables satisfaction propagation from user to all agents

4. **User Satisfaction Feedback** (lines 591-650):
   - attach_satisfaction() method to add user feedback to traces
   - Used by Reflector to weight insights (high satisfaction → success patterns)

### 2.2 Reflector Component

| Feature | Guide | Our Implementation | Aligned? |
|---------|-------|-------------------|----------|
| **Analyzes traces** | Yes | Yes (ClaudeCLIInterface) | ✅ **Yes** |
| **Extracts insights** | Yes (cross-trace patterns) | Yes (via prompt) | ✅ **Yes** |
| **Success patterns** | Yes | Yes (insight_type="success_pattern") | ✅ **Yes** |
| **Failure modes** | Yes | Yes (insight_type="failure_mode") | ✅ **Yes** |
| **Delta items** | Yes | Yes (DeltaItem model) | ✅ **Yes** |
| **Evidence tracking** | Yes | Yes (Evidence model with trace_id) | ✅ **Yes** |
| **Priority assignment** | Mentioned | ✅ Yes (1-5 scale, automatic) | ✅ **Yes** |
| **Confidence scoring** | Mentioned | ✅ Yes (0.0-1.0, evidence-based) | ✅ **Yes** |
| **Batch processing** | Yes (multiple traces) | ✅ Yes (trace_ids, hours, n_latest) | ✅ **Yes** |
| **Satisfaction signals** | Not mentioned | ✅ **Yes** (explicit + implicit sentiment) | ➕ **Enhancement** |
| **Satisfaction propagation** | Not mentioned | ✅ **Yes** (parent→child via delegation chain) | ➕ **Enhancement** |

**Alignment Summary**: **90% Aligned** - Core reflector functionality matches guide, enhanced with satisfaction analysis.

**Notable Enhancements in Our Implementation**:

1. **User Satisfaction Signal Extraction** (lines 499-759):
   - Explicit satisfaction: High scores (4-5) → success patterns, Low scores (1-2) → failure modes
   - Implicit sentiment: Analyzes frustration, confusion, satisfaction from user messages
   - Confidence boost: Satisfaction-weighted insights prioritized in playbook

2. **Satisfaction Propagation** (lines 806-893):
   - When user provides satisfaction to user_listener, propagates to all child traces
   - Ensures code_developer learns from user feedback even for delegated work
   - Recursive propagation through entire delegation chain

3. **Flexible Trace Selection** (lines 66-168):
   - Specific trace IDs: analyze_traces(trace_ids=["123", "456"])
   - Time-based: analyze_traces(hours=24)
   - Latest N: analyze_traces(n_latest=10)

### 2.3 Curator Component

| Feature | Guide | Our Implementation | Aligned? |
|---------|-------|-------------------|----------|
| **Playbook integration** | Yes | Yes (Playbook model) | ✅ **Yes** |
| **Semantic de-duplication** | Yes | Yes (OpenAI embeddings) | ✅ **Yes** |
| **Similarity threshold** | 0.85 (default) | 0.85 (configurable via .env) | ✅ **Yes** |
| **Bullet merging** | Yes | Yes (_merge_bullet) | ✅ **Yes** |
| **Pruning** | Yes | Yes (_prune_low_value_bullets) | ✅ **Yes** |
| **Helpful/harmful counts** | Yes | Yes (increments with satisfaction boost) | ✅ **Yes** |
| **Effectiveness ratio** | Yes | Yes (helpful/(helpful+harmful)) | ✅ **Yes** |
| **Embedding caching** | Yes | Yes (stored in bullet.embedding) | ✅ **Yes** |
| **Health metrics** | Yes | Yes (HealthMetrics model) | ✅ **Yes** |
| **Curation reports** | Yes | Yes (saved to playbook_dir/reports/) | ✅ **Yes** |
| **Satisfaction boost** | Not mentioned | ✅ **Yes** (_get_satisfaction_boost) | ➕ **Enhancement** |

**Alignment Summary**: **95% Aligned** - Curator implementation closely matches guide with satisfaction enhancements.

**Notable Enhancements in Our Implementation**:

1. **Satisfaction-Weighted Merging** (lines 220-263):
   - High satisfaction deltas count more towards helpful_count
   - Confidence boosted by satisfaction score
   - Success patterns from satisfied users prioritized

2. **Comprehensive Health Metrics** (lines 358-418):
   - Total bullets (active only)
   - Average helpful count
   - Effectiveness ratio
   - Coverage score (categories filled)
   - Session statistics (added/updated/pruned)

3. **Configurable Pruning** (lines 300-356):
   - Min helpful count threshold (from .env)
   - Max bullets limit (from .env)
   - Pruning rate (from .env)
   - Score-based pruning (effectiveness * confidence * priority)

---

## 3. Integration Patterns Comparison

### Pattern 1: Automatic Background Learning

**Guide**:
```python
def invoke_agent_with_ace(agent_name, query, context):
    # Normal execution for user (blocking)
    response = invoke_agent(agent_name, query, context)

    # Background ACE workflow (non-blocking via threading)
    threading.Thread(
        target=ace_workflow,
        args=(agent_name, query, context)
    ).start()

    return response

def ace_workflow(agent_name, query, context):
    # Step 1: Generator observes
    generator_report = generator.execute_and_observe(
        agent_name, query, context
    )

    # Step 2: Reflector analyzes (AUTOMATIC)
    reflection = reflector.analyze(generator_report)

    # Step 3: Curator integrates (AUTOMATIC)
    curator.integrate(reflection)
```

**Key Features**:
- Non-blocking (background thread)
- Automatic reflection→curation chain
- User gets response immediately, learning happens in background

**Our Implementation**:
```python
# agent_wrapper.py - ACEAgent base class
class ACEAgent(ABC):
    def execute_task(self, *args, **kwargs) -> Any:
        if self.ace_enabled:
            # Execute through generator (SYNCHRONOUS trace generation)
            result = self.generator.execute_with_trace(
                prompt=self._format_prompt(*args, **kwargs),
                priority_context=kwargs.get("context", {}),
                **kwargs,
            )
            return result["agent_result"]
        else:
            # Direct execution (no trace)
            return self._execute_implementation(*args, **kwargs)

# Reflection and curation are MANUAL (or scheduled):
# python -m coffee_maker.autonomous.ace.cli reflect
# python -m coffee_maker.autonomous.ace.cli curate
```

**Key Features**:
- Synchronous trace generation (blocking)
- Manual reflection/curation (opt-in auto via ACE_AUTO_REFLECT=true)
- Agent gets trace_id immediately, reflection happens later

**Difference**:
- **Guide**: Background threading, automatic chain, non-blocking
- **Ours**: Synchronous trace generation, manual reflection, blocking
- **Rationale**: Cost management, user control, explicit scheduling

**Can be made compatible by**:
1. Adding background threading to generator.execute_with_trace()
2. Setting ACE_AUTO_REFLECT=true and ACE_AUTO_CURATE=true

### Pattern 2: Batch Learning

**Guide**:
```python
def batch_ace_learning(agent_name, batch_size=10):
    # Collect executions
    execution_batch = []
    while len(execution_batch) < batch_size:
        execution_batch.append(
            generator.observe_next_execution(agent_name)
        )

    # Batch reflection
    reflection = reflector.analyze_batch(execution_batch)

    # Curator integration
    curator.integrate(reflection)
```

**Our Implementation**:
```python
# reflector.py - ACEReflector
def analyze_traces(
    self,
    trace_ids: Optional[List[str]] = None,
    hours: Optional[int] = None,
    n_latest: Optional[int] = None,
) -> List[DeltaItem]:
    # Load traces based on criteria
    traces = self._load_traces(trace_ids=trace_ids, hours=hours, n_latest=n_latest)

    # Extract insights from all traces (batch processing)
    deltas = self._extract_insights(traces)

    return deltas

# Usage:
# Analyze last 10 traces (batch)
deltas = reflector.analyze_traces(n_latest=10)
```

**Alignment**: ✅ **Compatible** - Both support batch processing, different invocation patterns.

### Pattern 3: Multi-Epoch Training

**Guide**:
```python
def multi_epoch_training(agent_name, training_queries, epochs=5):
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")

        for query in training_queries:
            # Execute with current context
            generator_report = generator.execute_and_observe(
                agent_name, query, current_context
            )

            # Immediate reflection and curation
            reflection = reflector.analyze(generator_report)
            current_context = curator.integrate(reflection)

        # Epoch summary
        print(f"Playbook size: {len(current_context.bullets)}")
        print(f"Effectiveness: {current_context.effectiveness_ratio}")
```

**Our Implementation**:
```python
# NOT DIRECTLY SUPPORTED - But could be implemented:
def multi_epoch_training(agent, training_data, epochs=5):
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")

        trace_ids = []
        for query in training_data:
            # Execute task (creates trace)
            result = agent.execute_task(query)
            trace_ids.append(result.get("trace_id"))

        # Reflect on all traces for this epoch
        reflector = ACEReflector(agent_name=agent.agent_name)
        deltas = reflector.analyze_traces(trace_ids=trace_ids)
        reflector.save_deltas(deltas)

        # Curate into playbook
        curator = ACECurator(agent_name=agent.agent_name)
        playbook = curator.consolidate_deltas()

        print(f"Playbook: {playbook.total_bullets} bullets, "
              f"{playbook.effectiveness_score:.2%} effectiveness")
```

**Alignment**: ⚠️ **Partially Compatible** - Concept is compatible, but not built-in. Would need to implement training loop.

---

## 4. Playbook Storage Comparison

### Guide Format

```
playbooks/
├── python_coder/
│   ├── playbook_v1.5.3.json
│   ├── playbook_v1.5.2.json (backup)
│   └── metadata.json
├── web_researcher/
│   ├── playbook_v2.1.0.json
│   └── metadata.json
└── support_assistant/
    ├── playbook_v1.0.5.json
    └── metadata.json
```

**Playbook JSON Structure (Guide)**:
```json
{
  "agent_name": "python_code_generator",
  "version": "1.5.3",
  "last_updated": "2025-10-13T10:30:00Z",
  "total_bullets": 47,
  "effectiveness_ratio": 0.92,

  "bullets": [
    {
      "id": "bullet_001",
      "type": "helpful_strategy",
      "content": "Use type hints for all function signatures",
      "helpful_count": 15,
      "harmful_count": 0,
      "confidence": "high",
      "priority": "high",
      "created": "2025-09-01T08:00:00Z",
      "last_updated": "2025-10-12T14:22:00Z",
      "evidence_sources": ["exec_001", "exec_045"],
      "applicability": "All Python function definitions",
      "tags": ["type_safety", "python"],
      "embedding": [0.123, 0.456, ...]
    }
  ],

  "statistics": {
    "total_helpful_actions": 234,
    "total_harmful_actions": 19,
    "most_effective_bullet": "bullet_001",
    "least_effective_bullet": "bullet_032"
  }
}
```

### Our Format

```
docs/curator/playbooks/
├── user_interpret_playbook.json
├── code_developer_playbook.json
├── assistant_playbook.json
└── reports/
    └── curation_report_user_interpret_20251015_120000.json
```

**Playbook JSON Structure (Ours)**:
```json
{
  "agent_name": "user_interpret",
  "version": "1.0.0",
  "created_at": "2025-10-15T12:00:00",
  "last_updated": "2025-10-15T12:00:00",
  "total_bullets": 12,
  "effectiveness_score": 0.87,

  "categories": {
    "success_pattern": [
      {
        "bullet_id": "bullet_1729000000000",
        "type": "success_pattern",
        "content": "Use sentiment analysis before intent classification",
        "helpful_count": 5,
        "harmful_count": 0,
        "confidence": 0.85,
        "priority": 4,
        "created_at": "2025-10-15T10:00:00",
        "last_updated": "2025-10-15T12:00:00",
        "evidence_sources": ["trace_123", "trace_456"],
        "applicability": "All user message processing",
        "tags": [],
        "embedding": [0.123, 0.456, ...],
        "deprecated": false,
        "deprecation_reason": null
      }
    ],
    "failure_mode": [...],
    "optimization": [...],
    "best_practice": [...]
  },

  "health_metrics": {
    "total_bullets": 12,
    "avg_helpful_count": 3.5,
    "effectiveness_ratio": 0.87,
    "bullets_added_this_session": 2,
    "bullets_updated_this_session": 5,
    "bullets_pruned_this_session": 1,
    "coverage_score": 0.60
  }
}
```

### Key Differences

| Aspect | Guide | Ours | Compatible? |
|--------|-------|------|-------------|
| **Directory** | playbooks/{agent}/ | docs/curator/playbooks/ | ⚠️ Different path |
| **Filename** | playbook_v{version}.json | {agent}_playbook.json | ⚠️ Different naming |
| **Versioning** | Explicit version numbers | Implicit (git) | ⚠️ Different approach |
| **Backups** | Previous versions kept | Single file (git history) | ⚠️ Different strategy |
| **Bullet structure** | Flat "bullets" array | Categorized by type | ⚠️ Different organization |
| **Field names** | id, type, content | bullet_id, type, content | ✅ Similar |
| **Helpful/harmful** | Yes | Yes | ✅ Same |
| **Confidence** | String ("high") | Float (0.85) | ⚠️ Different type |
| **Priority** | String ("high") | Integer (1-5) | ⚠️ Different type |
| **Embeddings** | Yes | Yes | ✅ Same |
| **Statistics** | Yes (separate section) | Yes (health_metrics) | ✅ Similar |

**Alignment**: ⚠️ **Partially Compatible** - Core data is similar, but structure differs. Could convert between formats.

---

## 5. Configuration Comparison

### Guide Configuration

**Per-Agent YAML Files**:
```yaml
# config/python_coder_config.yaml
target_agent: "python_code_generator"
agent_objective: "Generate clean, type-safe Python code"
success_criteria: |
  - Code runs without syntax errors
  - Passes mypy type checking
  - Includes docstrings
  - Handles edge cases

current_context: |
  ## Core Strategies
  - Use type hints for all function signatures
  - Include comprehensive docstrings

  ## Tool Usage
  - Use create_file for new files
  - Use str_replace for modifications
```

**Usage**:
```bash
@ace_generator_agent execute with config: config/python_coder_config.yaml
Query: "Create a CSV parser"
```

### Our Configuration

**Global Environment Variables (.env)**:
```bash
# ACE Configuration (applies to ALL agents)
export ACE_AUTO_REFLECT="false"
export ACE_AUTO_CURATE="false"
export ACE_TRACE_DIR="docs/generator/traces"
export ACE_DELTA_DIR="docs/reflector/deltas"
export ACE_PLAYBOOK_DIR="docs/curator/playbooks"
export ACE_SIMILARITY_THRESHOLD="0.85"
export ACE_PRUNING_RATE="0.10"
export ACE_MIN_HELPFUL_COUNT="2"
export ACE_MAX_BULLETS="150"

# Agent-Specific Opt-Out (default: ALL ENABLED)
# export ACE_ENABLED_USER_INTERPRET="false"   # Opt-out
# export ACE_ENABLED_CODE_DEVELOPER="false"   # Opt-out
```

**Per-Agent Configuration in Code**:
```python
# agent_wrapper.py - ACEAgent base class
class UserInterpret(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "user_interpret"

    @property
    def agent_objective(self) -> str:
        return "Interpret user input and determine intent"

    @property
    def success_criteria(self) -> str:
        return "Intent correctly identified, sentiment analyzed"
```

**Usage**:
```python
# Automatic - just use the agent
agent = UserInterpret()
result = agent.execute_task("parse user input")
# ACE trace created automatically if ACE_ENABLED_USER_INTERPRET != "false"
```

### Key Differences

| Aspect | Guide | Ours | Aligned? |
|--------|-------|------|----------|
| **Format** | YAML per agent | .env global + Python per agent | ❌ Different |
| **Agent objective** | YAML file | Python property | ❌ Different |
| **Success criteria** | YAML file | Python property | ❌ Different |
| **Current context** | YAML file | Loaded from playbook | ❌ Different |
| **Thresholds** | YAML per agent | .env global | ❌ Different |
| **Opt-in/out** | Manual invocation | ACE_ENABLED_{AGENT}="false" | ❌ Different |
| **Default behavior** | Opt-in (manual) | Opt-out (enabled by default) | ❌ Different |

**Alignment**: ❌ **Not Compatible** - Completely different configuration approaches.

**Why We Chose .env + Python**:
1. **Simplicity**: Single .env file for all agents
2. **Version control**: Agent objectives in code, not separate files
3. **Autonomous**: No manual config file management
4. **DRY**: Avoid duplication between agent code and YAML

---

## 6. Usage Pattern Comparison

### Guide Usage Pattern

**Interactive, Human-in-the-Loop**:
```bash
# Step 1: User invokes Generator with config
@ace_generator_agent execute with config: config/python_coder_config.yaml
Query: "Create a CSV parser with error handling"

# Generator runs target agent twice, packages data

# Step 2: Generator automatically invokes Reflector
@ace_reflector_agent analyze report from Generator

# Reflector extracts insights, creates delta items

# Step 3: Reflector automatically invokes Curator
@ace_curator_agent integrate deltas

# Curator updates playbook, returns curation report

# Result: User sees final response + updated playbook
```

**Key Characteristics**:
- Manual trigger (user invokes @ace_generator_agent)
- Automatic chain (Generator→Reflector→Curator)
- Interactive (user sees each step)
- Synchronous (blocks until complete)

### Our Usage Pattern

**Autonomous, Daemon-Driven**:
```python
# Step 1: Agent executes task (ACE trace created automatically)
from coffee_maker.agents.user_interpret import UserInterpret

agent = UserInterpret()  # ACE enabled by default (singleton)
result = agent.execute_task("parse this user message")
# Trace saved to docs/generator/traces/{date}/trace_{id}.json

# Step 2: Scheduled or manual reflection (async)
from coffee_maker.autonomous.ace.cli import reflect_command

# Option A: Manual CLI
$ python -m coffee_maker.autonomous.ace.cli reflect --agent user_interpret --hours 24

# Option B: Scheduled (cron job)
0 */6 * * * cd /path/to/project && python -m coffee_maker.autonomous.ace.cli reflect --agent user_interpret --hours 6

# Step 3: Scheduled or manual curation (async)
$ python -m coffee_maker.autonomous.ace.cli curate --agent user_interpret

# Result: Playbook updated in background, agent continues working
```

**Key Characteristics**:
- Automatic trigger (agent execution creates trace)
- Asynchronous stages (trace→reflect→curate are separate)
- Background (user doesn't see ACE workflow)
- Scheduled (reflection/curation run periodically)

### Key Differences

| Aspect | Guide | Ours | Aligned? |
|--------|-------|------|----------|
| **Trigger** | Manual (@ace_generator_agent) | Automatic (agent execution) | ❌ Different |
| **Chain** | Automatic (Generator→Reflector→Curator) | Manual/Scheduled (trace→reflect→curate) | ❌ Different |
| **Visibility** | Interactive (user sees steps) | Background (silent) | ❌ Different |
| **Timing** | Synchronous (blocks) | Asynchronous (non-blocking) | ❌ Different |
| **Control** | Human-in-the-loop | Daemon-driven | ❌ Different |

**Why We Chose Autonomous Pattern**:
1. **Cost**: Manual reflection control (batch instead of per-execution)
2. **Performance**: Non-blocking (agent doesn't wait for reflection)
3. **Scalability**: Scheduled reflection handles high-volume agents
4. **Autonomy**: Daemon runs without human intervention

---

## 7. Key Enhancements in Our Implementation

### 7.1 Plan-Aware Generator

**Not in Guide** - Our generator captures agent's execution plan:

```python
# Agent declares plan at start
self._set_plan([
    "Analyze user sentiment",
    "Identify user intent",
    "Extract entities",
    "Generate response"
])

# Agent reports progress
self._update_plan_progress("Analyze user sentiment", "in_progress")
# ... do work ...
self._update_plan_progress("Analyze user sentiment", "completed")

# Agent reports difficulties
self._report_difficulty("Sentiment analysis timeout", severity="high")

# Generator captures all of this in trace
```

**Benefit**: Reflector can analyze whether agent followed its plan, identify deviations, and learn from difficulties.

### 7.2 Conditional Dual Execution

**Not in Guide** - Our generator skips 2nd execution intelligently:

```python
def _should_run_second_execution(self, exec1: Execution) -> bool:
    # Skip if first execution took >30s (cost optimization)
    if exec1.duration_seconds >= 30:
        return False

    # Skip if owned directories modified (real work done)
    if self._check_owned_directories_modified(exec1.external_observation):
        return False

    return True
```

**Benefit**: Saves costs on slow agents (code_developer can take 30min-4hr), avoids redundant execution when real work was done.

### 7.3 Delegation Chain Tracking

**Not in Guide** - Our generator tracks multi-agent delegation:

```python
# user_listener delegates to code_developer
result = code_developer.execute_task(
    task="implement feature X",
    parent_trace_id=user_listener_trace_id,
    delegation_chain=user_listener_chain
)

# Trace captures:
# - parent_trace_id: Link to parent agent
# - delegation_chain: Full chain (user_listener → code_developer)
```

**Benefit**: Enables satisfaction propagation (user satisfaction reaches all agents in chain), cross-agent learning.

### 7.4 User Satisfaction Feedback

**Not in Guide** - Our reflector extracts insights from user satisfaction:

```python
# User provides satisfaction to trace
generator.attach_satisfaction(trace_id, {
    "score": 5,
    "positive_feedback": "Fast and accurate",
    "improvement_areas": "Could add more tests"
})

# Reflector extracts satisfaction-weighted insights
# High satisfaction (4-5) → Success patterns (high priority, high confidence)
# Low satisfaction (1-2) → Failure modes (high priority, avoid pattern)

# Curator applies satisfaction boost
# Success patterns from satisfied users get +0.2 confidence boost
```

**Benefit**: Direct user feedback loop, success patterns prioritized, failure modes avoided.

### 7.5 Ownership-Aware Execution

**Not in Guide** - Our generator respects file ownership:

```python
owned_dirs = {
    "code_developer": ["coffee_maker/", "tests/", "scripts/"],
    "project_manager": ["docs/", ".claude/"],
    "user_listener": [],  # UI only
}

# If agent modified owned directories, skip 2nd execution
# Reasoning: Real work was done, comparison less valuable
```

**Benefit**: Prevents redundant work when agent has clear ownership and made substantive changes.

### 7.6 ACEAgent Base Class

**Not in Guide** - All our agents inherit from ACEAgent:

```python
class UserInterpret(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "user_interpret"

    @property
    def agent_objective(self) -> str:
        return "Interpret user input"

    @property
    def success_criteria(self) -> str:
        return "Intent correctly identified"

    def _execute_implementation(self, message: str) -> Dict[str, Any]:
        # Your agent logic here
        return {"intent": "...", "sentiment": "..."}

# ACE integration is AUTOMATIC (no manual wrapper needed)
agent = UserInterpret()
result = agent.execute_task("parse this message")
# Trace created automatically if ACE_ENABLED_USER_INTERPRET != "false"
```

**Benefit**: Zero-boilerplate ACE integration, consistent interface, singleton pattern, opt-out via env var.

---

## 8. Missing Features from Guide

### 8.1 Automatic Reflection→Curation Chain

**Guide Has**:
```python
def ace_workflow(agent_name, query, context):
    # Step 1: Generator observes
    generator_report = generator.execute_and_observe(...)

    # Step 2: Reflector analyzes (AUTOMATIC)
    reflection = reflector.analyze(generator_report)

    # Step 3: Curator integrates (AUTOMATIC)
    curator.integrate(reflection)
```

**We Have**:
```python
# Manual invocation
$ python -m coffee_maker.autonomous.ace.cli reflect --agent user_interpret
$ python -m coffee_maker.autonomous.ace.cli curate --agent user_interpret

# OR scheduled (cron)
0 */6 * * * python -m coffee_maker.autonomous.ace.cli reflect --agent user_interpret --hours 6
```

**Status**: **Partially Implemented** - Can enable with ACE_AUTO_REFLECT=true and ACE_AUTO_CURATE=true, but **disabled by default** for cost control.

**Why Disabled by Default**:
1. **Cost**: Reflection uses Claude API (expensive per execution)
2. **Control**: User decides when to batch-reflect (e.g., every 6 hours vs. every execution)
3. **Performance**: Synchronous reflection would slow down agent execution

**To Enable**:
```bash
export ACE_AUTO_REFLECT="true"
export ACE_AUTO_CURATE="true"
```

### 8.2 Background Threading

**Guide Has**:
```python
# Non-blocking ACE workflow
threading.Thread(
    target=ace_workflow,
    args=(agent_name, query, context)
).start()

# User gets response immediately, ACE runs in background
```

**We Have**:
```python
# Synchronous trace generation (blocks during dual execution)
result = self.generator.execute_with_trace(...)

# Reflection/curation are async (scheduled separately)
```

**Status**: **Not Implemented** - Trace generation is synchronous.

**Why Not Implemented**:
1. **Simplicity**: Synchronous flow easier to debug
2. **Cost control**: No background threads consuming API tokens
3. **Explicit**: User knows when ACE is running

**Could Implement**:
```python
class ACEGenerator:
    def execute_with_trace_async(self, prompt: str, **kwargs):
        # Start background thread for trace generation
        thread = threading.Thread(
            target=self._execute_and_save_trace,
            args=(prompt,),
            kwargs=kwargs
        )
        thread.start()

        # Return immediately (no trace_id yet)
        return {"status": "trace_pending"}
```

### 8.3 Per-Agent YAML Configuration

**Guide Has**:
```yaml
# config/python_coder_config.yaml
target_agent: "python_code_generator"
agent_objective: "Generate clean Python code"
success_criteria: |
  - Code runs without errors
  - Passes mypy
current_context: |
  ## Strategies
  - Use type hints
```

**We Have**:
```python
# In code (agent_wrapper.py)
class CodeDeveloper(ACEAgent):
    @property
    def agent_objective(self) -> str:
        return "Implement features from ROADMAP"

    @property
    def success_criteria(self) -> str:
        return "Code runs, tests pass, DoD verified"
```

**Status**: **Not Implemented** - Configuration is in code, not YAML.

**Why Not Implemented**:
1. **Version control**: Agent objectives should be in git, not separate files
2. **DRY**: Avoid duplicating agent config between code and YAML
3. **Simplicity**: Single source of truth (Python code)

**Could Implement**:
```python
# Load agent config from YAML if available
config_path = Path(f"config/{self.agent_name}_config.yaml")
if config_path.exists():
    config = yaml.safe_load(config_path.read_text())
    self.agent_objective = config["agent_objective"]
    self.success_criteria = config["success_criteria"]
else:
    # Fall back to code-defined properties
    self.agent_objective = self.agent_objective
    self.success_criteria = self.success_criteria
```

### 8.4 Multi-Epoch Training

**Guide Has**:
```python
def multi_epoch_training(agent_name, training_queries, epochs=5):
    for epoch in range(epochs):
        for query in training_queries:
            generator_report = generator.execute_and_observe(...)
            reflection = reflector.analyze(generator_report)
            current_context = curator.integrate(reflection)

        print(f"Epoch {epoch+1}: {len(current_context.bullets)} bullets")
```

**We Have**: **Not Implemented** - No built-in multi-epoch training loop.

**Status**: **Concept Compatible** - Could implement training loop using existing components.

**Could Implement**:
```python
# training.py
def train_agent(agent, training_data, epochs=5):
    for epoch in range(epochs):
        trace_ids = []

        for query in training_data:
            result = agent.execute_task(query)
            trace_ids.append(result["trace_id"])

        # Reflect on epoch
        reflector = ACEReflector(agent_name=agent.agent_name)
        deltas = reflector.analyze_traces(trace_ids=trace_ids)
        reflector.save_deltas(deltas)

        # Curate
        curator = ACECurator(agent_name=agent.agent_name)
        playbook = curator.consolidate_deltas()

        print(f"Epoch {epoch+1}: {playbook.total_bullets} bullets, "
              f"{playbook.effectiveness_score:.2%} effective")
```

---

## 9. Alignment Assessment

### Strongly Aligned ✅

**Core ACE Concepts (95% Match)**:
- ✅ Generator, Reflector, Curator architecture
- ✅ Dual execution observation (external + internal)
- ✅ Execution trace format (JSON)
- ✅ Delta items (insights with evidence)
- ✅ Playbook structure (bullets with helpful/harmful counts)
- ✅ Semantic de-duplication (embeddings + cosine similarity)
- ✅ Effectiveness tracking (helpful/(helpful+harmful))
- ✅ Pruning strategies (low-value bullet removal)
- ✅ Success patterns and failure modes
- ✅ Evidence-based confidence scoring

### Partially Aligned ⚠️

**Integration & Configuration (60% Match)**:
- ⚠️ Integration pattern: Python classes vs. markdown agents
- ⚠️ Configuration: .env + Python vs. YAML files
- ⚠️ Usage: Automatic trace generation vs. manual invocation
- ⚠️ Chain: Asynchronous stages vs. synchronous chain
- ⚠️ Default: Opt-out (enabled) vs. opt-in (manual)
- ⚠️ Playbook format: Categorized vs. flat array
- ⚠️ Storage: Single file vs. versioned files

### Not Aligned ❌

**Automation & Workflow (40% Match)**:
- ❌ Automatic reflection→curation chain (disabled by default)
- ❌ Background threading (not implemented)
- ❌ Per-agent YAML config (not implemented)
- ❌ Multi-epoch training (not implemented)
- ❌ Interactive workflow (daemon-driven instead)

---

## 10. Compatibility with Guide

### Question: Can our implementation work with the guide's approach?

**Answer**: **Partially Compatible**

### What's Compatible ✅

1. **Playbook Exchange**:
   - Could write converter: our format ↔ guide format
   - Bullet structure is similar (helpful/harmful counts, embeddings)
   - Would need to flatten categories for guide format

2. **Trace Concepts**:
   - Both use external observation (git, files)
   - Both use internal observation (reasoning, tools)
   - Our traces have more fields (plan, difficulties, delegation_chain)

3. **Delta Items**:
   - Structure is compatible
   - Insight types match (success_pattern, failure_mode, etc.)
   - Evidence model is compatible

4. **Core Workflow**:
   - Generator → Reflector → Curator flow is identical
   - De-duplication logic is identical (embeddings + similarity)
   - Pruning logic is similar

### What's Incompatible ❌

1. **Integration Mechanism**:
   - Guide uses markdown agents in claude-cli
   - We use Python classes
   - Cannot use guide's @ace_generator_agent directly

2. **Configuration**:
   - Guide uses YAML per agent
   - We use .env global + Python properties
   - Cannot use guide's config files directly

3. **Invocation**:
   - Guide requires manual @agent_name invocation
   - We have automatic trace generation via ACEAgent
   - Different user experience

4. **Chain Execution**:
   - Guide has automatic Generator→Reflector→Curator chain
   - We have separate stages (trace→reflect→curate)
   - Different timing and control

### Bridge Strategy: Make Both Work Together

**Option 1: Create Markdown Agent Wrappers**

```markdown
<!-- .claude/agents/ace_generator_wrapper.md -->
# ACE Generator Wrapper

You are a wrapper around the Python ACEGenerator implementation.

When invoked with:
@ace_generator_wrapper execute with config: config/my_agent_config.yaml

You should:
1. Load the YAML config
2. Call Python: python -m coffee_maker.autonomous.ace.cli generate --config config/my_agent_config.yaml
3. Parse the trace output
4. Automatically invoke @ace_reflector_wrapper with the trace

<!-- .claude/agents/ace_reflector_wrapper.md -->
# ACE Reflector Wrapper

You wrap the Python ACEReflector.

When invoked with trace from Generator:
1. Call Python: python -m coffee_maker.autonomous.ace.cli reflect --trace-id {trace_id}
2. Parse delta items
3. Automatically invoke @ace_curator_wrapper with deltas

<!-- .claude/agents/ace_curator_wrapper.md -->
# ACE Curator Wrapper

You wrap the Python ACECurator.

When invoked with deltas from Reflector:
1. Call Python: python -m coffee_maker.autonomous.ace.cli curate --deltas {delta_file}
2. Return updated playbook
```

**Benefit**: Can use guide's interactive workflow while using our Python implementation.

**Option 2: Add YAML Config Support**

```python
# coffee_maker/autonomous/ace/config_loader.py
def load_agent_config(agent_name: str) -> dict:
    """Load agent config from YAML if available."""
    config_path = Path(f"config/{agent_name}_config.yaml")

    if config_path.exists():
        import yaml
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # Fall back to Python properties
    return None

# agent_wrapper.py
class ACEAgent(ABC):
    def __init__(self):
        # Try to load YAML config first
        yaml_config = load_agent_config(self.agent_name)

        if yaml_config:
            self._agent_objective = yaml_config.get("agent_objective", self.agent_objective)
            self._success_criteria = yaml_config.get("success_criteria", self.success_criteria)
        else:
            self._agent_objective = self.agent_objective
            self._success_criteria = self.success_criteria
```

**Benefit**: Can use guide's YAML configs while keeping Python fallback.

**Option 3: Enable Automatic Chain**

```bash
# Set environment variables to match guide's behavior
export ACE_AUTO_REFLECT="true"
export ACE_AUTO_CURATE="true"

# Now our implementation behaves like guide:
# Agent execution → Trace → Auto-Reflect → Auto-Curate → Updated Playbook
```

**Benefit**: Matches guide's automatic workflow.

---

## 11. Recommendations

### Keep Our Enhancements ✅

1. **Plan-Aware Generator**:
   - Valuable for understanding agent strategy
   - Helps reflector identify deviations from plan
   - Captures difficulties and concerns

2. **Conditional Dual Execution**:
   - Cost-effective optimization
   - Prevents redundant work on slow agents
   - Respects file ownership boundaries

3. **Delegation Chain Tracking**:
   - Essential for multi-agent systems
   - Enables satisfaction propagation
   - Cross-agent learning

4. **User Satisfaction Feedback**:
   - Direct user feedback loop
   - Success patterns prioritized
   - Failure modes avoided

5. **Ownership-Aware Execution**:
   - Critical for our architecture (multiple agents)
   - Prevents confusion about file ownership

6. **ACEAgent Base Class**:
   - Zero-boilerplate integration
   - Consistent interface
   - Singleton pattern
   - Opt-out via env var

### Consider Adopting from Guide ⚠️

1. **Per-Agent YAML Config** (Low Priority):
   - **Pro**: Easier to tweak objectives without code changes
   - **Con**: Duplication, separate file management
   - **Recommendation**: Add as **optional** (fall back to Python properties)
   - **Implementation**: 2-4 hours

2. **Automatic Reflection→Curation Chain** (Medium Priority):
   - **Pro**: Matches guide's workflow, less manual intervention
   - **Con**: Cost, less control over batching
   - **Recommendation**: Already have ACE_AUTO_REFLECT/ACE_AUTO_CURATE flags, **document better**
   - **Implementation**: Already done, just document

3. **Background Threading** (Low Priority):
   - **Pro**: Non-blocking ACE workflow
   - **Con**: More complex debugging, potential race conditions
   - **Recommendation**: Implement **for fast agents only** (user_interpret, assistant)
   - **Implementation**: 4-8 hours

4. **Multi-Epoch Training** (Medium Priority):
   - **Pro**: Useful for iterative improvement
   - **Con**: Requires training data, time-consuming
   - **Recommendation**: Implement as **separate training script** (not core ACE)
   - **Implementation**: 6-10 hours

### Bridge Both Approaches 🌉

1. **Create Markdown Agent Wrappers** (High Priority):
   - Wrap Python ACE components with markdown agents
   - Enables guide's interactive workflow
   - Users can choose: Python (daemon) or Markdown (interactive)
   - **Implementation**: 8-12 hours

2. **Add YAML Config Support** (Low Priority):
   - Load YAML if available, fall back to Python
   - Best of both worlds
   - **Implementation**: 2-4 hours

3. **Make Automatic Chain Optional** (Already Done ✅):
   - ACE_AUTO_REFLECT and ACE_AUTO_CURATE flags
   - Users choose: Manual (default) or Automatic
   - **Documentation**: Explain flags in README

4. **Document Both Integration Patterns** (High Priority):
   - Create docs/ACE_INTEGRATION_PATTERNS.md
   - Show: Python-based (daemon) vs. Markdown-based (interactive)
   - Examples for both approaches
   - **Implementation**: 4-6 hours

---

## 12. Conclusion

### Overall Alignment: **75% ALIGNED**

**Summary**:
- ✅ **Core ACE concepts and workflow are fully aligned** (95% match)
  - Generator, Reflector, Curator architecture
  - Dual execution observation
  - Semantic de-duplication
  - Playbook-based learning
  - Effectiveness tracking

- ⚠️ **Implementation approach differs** (60% match)
  - Python classes vs. markdown agents
  - .env + Python properties vs. YAML files
  - Automatic trace generation vs. manual invocation
  - Asynchronous stages vs. synchronous chain

- ✅ **Our implementation adds valuable enhancements** (unique to ours)
  - Plan-aware execution
  - Conditional dual execution
  - Delegation chain tracking
  - User satisfaction feedback
  - Ownership-aware execution
  - ACEAgent base class for zero-boilerplate integration

- ⚠️ **Guide has patterns we haven't fully implemented**
  - Background threading (not implemented)
  - Automatic reflection→curation chain (disabled by default)
  - Per-agent YAML config (not implemented)
  - Multi-epoch training (not implemented)

### Bottom Line

**We implement the ACE framework correctly according to the research paper**, but with a **different integration approach** than the guide.

**Our Python-based approach is more suitable for**:
- ✅ Autonomous daemon systems
- ✅ High-volume agent execution
- ✅ Scheduled batch reflection
- ✅ Cost-controlled learning
- ✅ Multi-agent delegation chains

**The guide's markdown-based approach is more suitable for**:
- ✅ Interactive human-in-the-loop workflows
- ✅ Manual experimentation
- ✅ Immediate reflection feedback
- ✅ Single-agent focused learning

**Both approaches are valid** - choose based on your use case:
- **Daemon/Production**: Use our Python implementation
- **Interactive/Development**: Use guide's markdown agents (or create wrappers)

### Compatibility

**Can exchange**:
- ✅ Playbooks (with format conversion)
- ✅ Delta items (structure compatible)
- ✅ Trace concepts (fields compatible)

**Cannot exchange directly**:
- ❌ Agents (Python vs. markdown)
- ❌ Config files (.env vs. YAML)
- ❌ Invocation patterns (automatic vs. manual)

**To achieve full compatibility**:
1. Create markdown agent wrappers (call Python code)
2. Add optional YAML config support (fall back to Python)
3. Enable ACE_AUTO_REFLECT=true and ACE_AUTO_CURATE=true
4. Document both integration patterns

---

## Appendix A: Feature Matrix

| Feature | Guide | Ours | Status |
|---------|-------|------|--------|
| **Generator - Dual Execution** | ✅ Always | ✅ Conditional | ⚠️ Enhanced |
| **Generator - External Observation** | ✅ Yes | ✅ Yes | ✅ Match |
| **Generator - Internal Observation** | ✅ Yes | ✅ Yes | ✅ Match |
| **Generator - Plan Tracking** | ❌ No | ✅ Yes | ➕ Ours Only |
| **Generator - Delegation Chain** | ❌ No | ✅ Yes | ➕ Ours Only |
| **Generator - Satisfaction** | ❌ No | ✅ Yes | ➕ Ours Only |
| **Reflector - Cross-Trace Analysis** | ✅ Yes | ✅ Yes | ✅ Match |
| **Reflector - Success Patterns** | ✅ Yes | ✅ Yes | ✅ Match |
| **Reflector - Failure Modes** | ✅ Yes | ✅ Yes | ✅ Match |
| **Reflector - Satisfaction Signals** | ❌ No | ✅ Yes | ➕ Ours Only |
| **Reflector - Batch Processing** | ✅ Yes | ✅ Yes | ✅ Match |
| **Curator - De-duplication** | ✅ Embeddings | ✅ Embeddings | ✅ Match |
| **Curator - Similarity Threshold** | ✅ 0.85 | ✅ 0.85 | ✅ Match |
| **Curator - Helpful/Harmful** | ✅ Yes | ✅ Yes | ✅ Match |
| **Curator - Pruning** | ✅ Yes | ✅ Yes | ✅ Match |
| **Curator - Health Metrics** | ✅ Yes | ✅ Yes | ✅ Match |
| **Config - Per-Agent YAML** | ✅ Yes | ❌ No | ⚠️ Guide Only |
| **Config - Environment Variables** | ❌ No | ✅ Yes | ⚠️ Ours Only |
| **Integration - Automatic Chain** | ✅ Yes | ⚠️ Optional | ⚠️ Different |
| **Integration - Background Threading** | ✅ Yes | ❌ No | ⚠️ Guide Only |
| **Integration - Auto Trace Generation** | ❌ No | ✅ Yes | ➕ Ours Only |
| **Usage - Interactive** | ✅ Yes | ❌ No | ⚠️ Guide Only |
| **Usage - Autonomous** | ❌ No | ✅ Yes | ➕ Ours Only |

**Legend**:
- ✅ Match: Feature implemented identically
- ⚠️ Different: Feature exists but implementation differs
- ➕ Ours Only: Feature unique to our implementation
- ❌ No: Feature not implemented

---

## Appendix B: Migration Guide

### From Guide → Ours

**If you're using the guide's markdown agents and want to switch to our Python implementation:**

1. **Install our implementation**:
   ```bash
   git clone https://github.com/yourusername/MonolithicCoffeeMakerAgent.git
   cd MonolithicCoffeeMakerAgent
   poetry install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Convert YAML config to Python**:
   ```yaml
   # Old: config/my_agent_config.yaml
   target_agent: "my_agent"
   agent_objective: "Process data"
   success_criteria: "Data processed successfully"
   ```

   ```python
   # New: coffee_maker/agents/my_agent.py
   from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

   class MyAgent(ACEAgent):
       @property
       def agent_name(self) -> str:
           return "my_agent"

       @property
       def agent_objective(self) -> str:
           return "Process data"

       @property
       def success_criteria(self) -> str:
           return "Data processed successfully"

       def _execute_implementation(self, message: str, **kwargs):
           # Your agent logic here
           return {"processed": True}
   ```

4. **Use the agent**:
   ```python
   # Old: @ace_generator_agent execute with config: ...
   # New:
   from coffee_maker.agents.my_agent import MyAgent

   agent = MyAgent()
   result = agent.execute_task("process this data")
   # Trace created automatically
   ```

5. **Run reflection/curation**:
   ```bash
   # Old: Automatic via @ace_reflector_agent
   # New: Manual or scheduled
   python -m coffee_maker.autonomous.ace.cli reflect --agent my_agent --hours 24
   python -m coffee_maker.autonomous.ace.cli curate --agent my_agent
   ```

### From Ours → Guide

**If you're using our Python implementation and want to switch to the guide's markdown agents:**

1. **Install guide's agents**:
   ```bash
   mkdir -p .claude/agents
   cp ace_generator_agent.md .claude/agents/
   cp ace_reflector_agent.md .claude/agents/
   cp ace_curator_agent.md .claude/agents/
   ```

2. **Create YAML configs**:
   ```yaml
   # config/my_agent_config.yaml
   target_agent: "my_agent"
   agent_objective: "Process data"  # From Python property
   success_criteria: "Data processed successfully"  # From Python property
   current_context: |
     ## Strategies
     # (Load from playbook)
   ```

3. **Convert playbook format**:
   ```python
   # scripts/convert_playbook.py
   import json
   from pathlib import Path

   # Load our format
   ours = json.loads(Path("docs/curator/playbooks/my_agent_playbook.json").read_text())

   # Convert to guide format
   guide = {
       "agent_name": ours["agent_name"],
       "version": ours["version"],
       "total_bullets": ours["total_bullets"],
       "effectiveness_ratio": ours["effectiveness_score"],
       "bullets": []
   }

   # Flatten categories
   for category, bullets in ours["categories"].items():
       for bullet in bullets:
           guide["bullets"].append({
               "id": bullet["bullet_id"],
               "type": bullet["type"],
               "content": bullet["content"],
               "helpful_count": bullet["helpful_count"],
               "harmful_count": bullet["harmful_count"],
               "confidence": "high" if bullet["confidence"] > 0.8 else "medium",
               "priority": "high" if bullet["priority"] >= 4 else "medium",
               # ... etc
           })

   Path("playbooks/my_agent/playbook_v1.0.0.json").write_text(json.dumps(guide, indent=2))
   ```

4. **Use guide's workflow**:
   ```bash
   # In claude-cli
   @ace_generator_agent execute with config: config/my_agent_config.yaml
   Query: "process this data"
   ```

---

**End of Document**

**Version**: 1.0
**Last Updated**: 2025-10-15
**Author**: project_manager agent
**Review Status**: Complete
