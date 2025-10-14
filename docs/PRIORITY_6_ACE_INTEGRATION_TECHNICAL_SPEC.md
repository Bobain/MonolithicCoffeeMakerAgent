# PRIORITY 6: ACE Framework Integration - Technical Specification

**Version**: 1.0
**Date**: 2025-10-14
**Status**: Planning
**Reference**: https://www.arxiv.org/abs/2510.04618

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [Integration Points](#integration-points)
5. [File Storage Structure](#file-storage-structure)
6. [Configuration Options](#configuration-options)
7. [Implementation Phases](#implementation-phases)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)
10. [Risks and Mitigations](#risks-and-mitigations)

---

## Overview

### Goal

Implement the **ACE (Agentic Context Engineering)** framework to enable continuous agent improvement through:
1. **Conditional dual execution observation with comprehensive trace capture** (Generator - cost optimized)
2. **Cross-execution pattern analysis and insight extraction** (Reflector compares multiple traces over time)
3. **Playbook curation with semantic de-duplication** (Curator)

### Scope

**In Scope**:
- Generator: Conditional dual execution wrapper with comprehensive observation capture (pre/post state, internal/external observations)
- Second execution runs ONLY IF: duration < 30s AND no owned files modified (cost optimization)
- Reflector: Cross-trace pattern analysis and delta extraction (compares multiple traces over time)
- Curator: Playbook consolidation with semantic de-duplication
- File-based storage for traces, deltas, playbooks
- Integration with `code_developer` daemon

**Out of Scope** (Future Work):
- Langfuse integration for trace storage
- Web-based playbook editor
- Real-time ACE dashboard
- Multi-agent shared playbooks

### References

- **Research Paper**: [Agentic Context Engineering (arXiv:2510.04618)](https://www.arxiv.org/abs/2510.04618)
- **Agent Definitions**: `.claude/agents/generator.md`, `reflector.md`, `curator.md`
- **User Guide**: `docs/ACE_FRAMEWORK_GUIDE.md`

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACE Framework Components                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Generator (coffee_maker/ace/generator.py)                │  │
│  │                                                            │  │
│  │  • Wraps target agent execution                           │  │
│  │  • ALWAYS executes agent once (fully observed)            │  │
│  │  • CONDITIONALLY executes second time for comparison:     │  │
│  │    - IF duration < 30s AND no owned files modified        │  │
│  │    - Cost optimization: Avoid duplicating expensive work  │  │
│  │  • Captures pre-execution state (git, files)              │  │
│  │  • Captures external observation (git changes, files)     │  │
│  │  • Captures internal observation (reasoning, tools)       │  │
│  │  • Captures post-execution state and results              │  │
│  │  • Saves comprehensive trace to docs/generator/traces/   │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │ Execution Traces (JSON)                 │
│                        ↓                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Reflector (coffee_maker/ace/reflector.py)                │  │
│  │                                                            │  │
│  │  • Loads MULTIPLE execution traces over time              │  │
│  │  • Performs cross-trace comparison and pattern analysis   │  │
│  │  • Identifies what consistently works or fails            │  │
│  │  • Identifies missing knowledge across traces             │  │
│  │  • Extracts actionable insights (deltas) with evidence    │  │
│  │  • Assigns priority and confidence based on evidence      │  │
│  │  • Saves deltas to docs/reflector/deltas/                │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │ Delta Items (JSON)                      │
│                        ↓                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Curator (coffee_maker/ace/curator.py)                    │  │
│  │                                                            │  │
│  │  • Loads new deltas from Reflector                        │  │
│  │  • Loads existing playbook                                │  │
│  │  • Computes semantic embeddings                           │  │
│  │  • Performs de-duplication (cosine similarity)            │  │
│  │  • Merges/updates/adds insights                           │  │
│  │  • Prunes low-value or harmful bullets                    │  │
│  │  • Updates health metrics                                 │  │
│  │  • Saves playbook to docs/curator/playbooks/             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User Request
    ↓
┌───────────────────────────────────────────┐
│ Daemon (coffee_maker/autonomous/daemon.py)│
│                                            │
│ • Receives priority from ROADMAP          │
│ • Wraps execution with Generator          │
└───────────────────┬───────────────────────┘
                    ↓
┌───────────────────────────────────────────┐
│ Generator                                  │
│                                            │
│ execute_with_observation(query):           │
│   1. Load current playbook                 │
│   2. Capture pre-execution state           │
│   3. Execute agent (FIRST, always runs)    │
│      - Capture external observations       │
│      - Capture internal observations       │
│      - Record duration and file changes    │
│   4. Evaluate conditional second execution:│
│      IF duration < 30s AND no files:       │
│        - Execute agent (SECOND)            │
│        - Compare both executions           │
│      ELSE:                                 │
│        - Skip second (note reason in trace)│
│   5. Capture post-execution state          │
│   6. Package comprehensive trace           │
│   7. Save trace JSON                       │
│   8. Return result                         │
└───────────────────┬───────────────────────┘
                    ↓
                  Result
                    ↓
┌───────────────────────────────────────────┐
│ Scheduled Task (cron/GitHub Actions)      │
│                                            │
│ • Trigger Reflector (daily)               │
│ • Trigger Curator (daily)                 │
└───────────────────┬───────────────────────┘
                    ↓
┌───────────────────────────────────────────┐
│ Reflector                                  │
│                                            │
│ analyze_recent_traces(hours=24):           │
│   1. Load traces from last 24h            │
│   2. Analyze each trace                   │
│   3. Extract insights (deltas)            │
│   4. Assign priority/confidence           │
│   5. Save deltas JSON                     │
│   6. Return deltas                        │
└───────────────────┬───────────────────────┘
                    ↓
┌───────────────────────────────────────────┐
│ Curator                                    │
│                                            │
│ consolidate(deltas):                       │
│   1. Load deltas                          │
│   2. Load existing playbook               │
│   3. For each delta:                      │
│      a. Compute embedding                 │
│      b. Calculate similarity              │
│      c. Merge/update/add                  │
│   4. Prune low-value bullets              │
│   5. Update health metrics                │
│   6. Save playbook                        │
│   7. Save curation report                 │
└───────────────────────────────────────────┘
                    ↓
              Updated Playbook
                    ↓
    (Used in next Generator execution)
```

---

## Data Models

### ExecutionTrace

**File**: `coffee_maker/ace/models.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class ExternalObservation:
    """External observation of agent execution (git, files, commands)"""
    git_changes: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)

@dataclass
class InternalObservation:
    """Internal observation of agent execution (reasoning, tools, decisions)"""
    reasoning_steps: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    tools_called: List[Dict[str, Any]] = field(default_factory=list)
    context_used: List[str] = field(default_factory=list)  # bullet IDs
    context_ignored: List[str] = field(default_factory=list)  # bullet IDs

@dataclass
class Execution:
    """Single execution run"""
    execution_id: int
    external_observation: ExternalObservation
    internal_observation: InternalObservation
    result_status: str  # "success" or "failure"
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    token_usage: int = 0

@dataclass
class ComparativeObservations:
    """Comparison between two executions"""
    consistency: str  # "same_outcome" or "different_outcomes"
    strategy_variance: str  # Description of differences
    effectiveness_comparison: str  # Which was better and why
    patterns_identified: List[str] = field(default_factory=list)

@dataclass
class ExecutionTrace:
    """Complete execution trace for ACE framework"""
    trace_id: str
    timestamp: datetime
    agent_identity: Dict[str, str]  # target_agent, agent_objective, success_criteria
    user_query: str
    current_context: str  # Playbook snapshot
    executions: List[Execution] = field(default_factory=list)
    comparative_observations: Optional[ComparativeObservations] = None
    helpful_context_elements: List[str] = field(default_factory=list)
    problematic_context_elements: List[str] = field(default_factory=list)
    new_insights_surfaced: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_identity": self.agent_identity,
            "user_query": self.user_query,
            "current_context": self.current_context,
            "executions": [
                {
                    "execution_id": e.execution_id,
                    "external_observation": {
                        "git_changes": e.external_observation.git_changes,
                        "files_created": e.external_observation.files_created,
                        "files_modified": e.external_observation.files_modified,
                        "files_deleted": e.external_observation.files_deleted,
                        "commands_executed": e.external_observation.commands_executed,
                    },
                    "internal_observation": {
                        "reasoning_steps": e.internal_observation.reasoning_steps,
                        "decisions_made": e.internal_observation.decisions_made,
                        "tools_called": e.internal_observation.tools_called,
                        "context_used": e.internal_observation.context_used,
                        "context_ignored": e.internal_observation.context_ignored,
                    },
                    "result_status": e.result_status,
                    "errors": e.errors,
                    "duration_seconds": e.duration_seconds,
                    "token_usage": e.token_usage,
                }
                for e in self.executions
            ],
            "comparative_observations": {
                "consistency": self.comparative_observations.consistency,
                "strategy_variance": self.comparative_observations.strategy_variance,
                "effectiveness_comparison": self.comparative_observations.effectiveness_comparison,
                "patterns_identified": self.comparative_observations.patterns_identified,
            } if self.comparative_observations else None,
            "helpful_context_elements": self.helpful_context_elements,
            "problematic_context_elements": self.problematic_context_elements,
            "new_insights_surfaced": self.new_insights_surfaced,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionTrace":
        """Load from dictionary"""
        # Implementation details...
        pass
```

### DeltaItem

**File**: `coffee_maker/ace/models.py`

```python
@dataclass
class Evidence:
    """Evidence for a delta item"""
    trace_id: str
    execution_id: int
    example: str

@dataclass
class DeltaItem:
    """Actionable insight extracted from traces"""
    delta_id: str
    insight_type: str  # success_pattern, failure_mode, optimization, etc.
    title: str
    description: str
    recommendation: str
    evidence: List[Evidence] = field(default_factory=list)
    applicability: str = ""
    priority: int = 3  # 1-5
    confidence: float = 0.5  # 0.0-1.0
    action: str = "add_new"  # add_new, update_existing, mark_harmful
    related_bullets: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "delta_id": self.delta_id,
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "evidence": [
                {
                    "trace_id": e.trace_id,
                    "execution_id": e.execution_id,
                    "example": e.example,
                }
                for e in self.evidence
            ],
            "applicability": self.applicability,
            "priority": self.priority,
            "confidence": self.confidence,
            "action": self.action,
            "related_bullets": self.related_bullets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeltaItem":
        """Load from dictionary"""
        # Implementation details...
        pass
```

### PlaybookBullet

**File**: `coffee_maker/ace/models.py`

```python
@dataclass
class PlaybookBullet:
    """Single bullet in agent playbook"""
    bullet_id: str
    type: str  # success_pattern, failure_mode, etc.
    content: str
    helpful_count: int = 0
    harmful_count: int = 0
    confidence: float = 0.5
    priority: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    evidence_sources: List[str] = field(default_factory=list)  # trace IDs
    applicability: str = ""
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    deprecated: bool = False
    deprecation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "bullet_id": self.bullet_id,
            "type": self.type,
            "content": self.content,
            "helpful_count": self.helpful_count,
            "harmful_count": self.harmful_count,
            "confidence": self.confidence,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "evidence_sources": self.evidence_sources,
            "applicability": self.applicability,
            "tags": self.tags,
            "embedding": self.embedding,
            "deprecated": self.deprecated,
            "deprecation_reason": self.deprecation_reason,
        }
```

### Playbook

**File**: `coffee_maker/ace/models.py`

```python
@dataclass
class HealthMetrics:
    """Playbook health metrics"""
    total_bullets: int = 0
    avg_helpful_count: float = 0.0
    effectiveness_ratio: float = 0.0
    bullets_added_this_session: int = 0
    bullets_updated_this_session: int = 0
    bullets_pruned_this_session: int = 0
    coverage_score: float = 0.0

@dataclass
class Playbook:
    """Agent playbook with categorized bullets"""
    playbook_version: str
    agent_name: str
    agent_objective: str
    success_criteria: str
    last_updated: datetime
    total_bullets: int
    effectiveness_score: float
    categories: Dict[str, List[PlaybookBullet]] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    health_metrics: Optional[HealthMetrics] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "playbook_version": self.playbook_version,
            "agent_name": self.agent_name,
            "agent_objective": self.agent_objective,
            "success_criteria": self.success_criteria,
            "last_updated": self.last_updated.isoformat(),
            "total_bullets": self.total_bullets,
            "effectiveness_score": self.effectiveness_score,
            "categories": {
                cat: [bullet.to_dict() for bullet in bullets]
                for cat, bullets in self.categories.items()
            },
            "statistics": self.statistics,
            "health_metrics": self.health_metrics.__dict__ if self.health_metrics else None,
            "history": self.history,
        }
```

---

## Integration Points

### 1. Daemon Integration

**File**: `coffee_maker/autonomous/daemon.py`

**Changes**:
```python
from coffee_maker.ace import Generator

class Daemon:
    def __init__(self, auto_approve: bool = False):
        # ... existing code ...

        # ACE integration
        self.ace_enabled = ConfigManager.get("ace_enabled", default=False)
        if self.ace_enabled:
            self.generator = Generator(
                target_agent="code_developer",
                agent_objective="Implement features from ROADMAP autonomously",
                success_criteria="Code runs, tests pass, DoD verified, PR created"
            )

    def process_next_priority(self):
        """Process next priority with ACE observation"""
        priority = self._get_next_priority()

        if self.ace_enabled:
            # Wrap execution with ACE observation
            result = self.generator.execute_with_observation(
                user_query=f"Implement {priority.name}: {priority.description}",
                context_provider=lambda: self._load_current_playbook()
            )
        else:
            # Standard execution
            result = self._execute_priority(priority)

        return result

    def _load_current_playbook(self) -> str:
        """Load current ACE playbook for code_developer"""
        from coffee_maker.ace import PlaybookLoader

        loader = PlaybookLoader(agent_name="code_developer")
        playbook = loader.load()

        # Convert to markdown format for context
        return loader.to_markdown(playbook)
```

### 2. Claude CLI Interface Integration

**File**: `coffee_maker/autonomous/claude_cli_interface.py`

**Changes**:
```python
class ClaudeCLIInterface:
    def send_message_with_observation(
        self,
        message: str,
        context: str,
        execution_id: int,
        observer_callback: Callable
    ) -> Dict[str, Any]:
        """
        Send message with observation callback

        Args:
            message: User query
            context: Playbook context
            execution_id: 1 or 2 (for dual execution)
            observer_callback: Function to capture observations

        Returns:
            Response with observations
        """
        # Start git tracking
        initial_git_status = self._get_git_status()

        # Execute
        response = self.send_message(message, context)

        # Capture observations
        final_git_status = self._get_git_status()
        observations = {
            "external": self._compute_external_observation(
                initial_git_status,
                final_git_status
            ),
            "internal": self._parse_internal_observation(response),
            "result_status": self._determine_result_status(response),
            "errors": self._extract_errors(response),
            "duration_seconds": response.get("duration", 0),
            "token_usage": response.get("token_usage", 0),
        }

        # Call observer callback
        observer_callback(execution_id, observations)

        return response

    def _compute_external_observation(self, before, after):
        """Compute external observation from git diff"""
        # Implementation...
        pass

    def _parse_internal_observation(self, response):
        """Parse internal observation from response"""
        # Implementation...
        pass
```

### 3. Scheduled Tasks

**File**: `.github/workflows/ace-curation.yml`

```yaml
name: ACE Curation

on:
  schedule:
    # Run daily at 2am UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  reflect-and-curate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run Reflector
        run: |
          poetry run ace-reflector \
            --agent code_developer \
            --hours 24 \
            --output docs/reflector/deltas/

      - name: Run Curator
        run: |
          poetry run ace-curator \
            --agent code_developer \
            --input docs/reflector/deltas/ \
            --output docs/curator/playbooks/

      - name: Commit updated playbook
        run: |
          git config --local user.email "ace@monolithiccoffeemaker.com"
          git config --local user.name "ACE Curator"
          git add docs/curator/playbooks/
          git commit -m "chore: ACE daily curation [skip ci]" || echo "No changes"
          git push
```

---

## File Storage Structure

```
MonolithicCoffeeMakerAgent/
├── docs/
│   ├── generator/
│   │   ├── README.md           ✅ (already exists)
│   │   └── traces/
│   │       ├── 2025-10-14/
│   │       │   ├── trace_1728925234.json
│   │       │   ├── trace_1728925456.json
│   │       │   └── ...
│   │       ├── 2025-10-15/
│   │       └── ...
│   │
│   ├── reflector/
│   │   ├── README.md           ✅ (already exists)
│   │   └── deltas/
│   │       ├── 2025-10-14/
│   │       │   ├── deltas_1728925300.json
│   │       │   └── ...
│   │       ├── 2025-10-15/
│   │       └── ...
│   │
│   ├── curator/
│   │   ├── README.md           ✅ (already exists)
│   │   ├── playbooks/
│   │   │   ├── code_developer_playbook.json
│   │   │   ├── assistant_playbook.json
│   │   │   └── ...
│   │   └── reports/
│   │       ├── 2025-10-14/
│   │       │   ├── curation_1728925400.json
│   │       │   └── ...
│   │       └── ...
│   │
│   ├── ACE_FRAMEWORK_GUIDE.md      ✅ (this file)
│   └── PRIORITY_6_ACE_INTEGRATION_TECHNICAL_SPEC.md  ✅ (this file)
│
└── coffee_maker/
    └── ace/
        ├── __init__.py
        ├── models.py              # Data models
        ├── generator.py           # Generator component
        ├── reflector.py           # Reflector component
        ├── curator.py             # Curator component
        ├── embeddings.py          # Embedding utilities
        ├── playbook_loader.py     # Playbook loading/saving
        └── cli.py                 # CLI commands (ace-reflector, ace-curator)
```

---

## Configuration Options

### Environment Variables

```bash
# Enable ACE framework
ACE_ENABLED=true

# Semantic similarity threshold for de-duplication
ACE_SIMILARITY_THRESHOLD=0.85

# Pruning rate (percentage of bullets to consider for pruning)
ACE_PRUNING_RATE=0.10

# Minimum helpful count to avoid pruning
ACE_MIN_HELPFUL_COUNT=2

# Maximum playbook size
ACE_MAX_BULLETS=150

# Embedding model
ACE_EMBEDDING_MODEL=text-embedding-ada-002
```

### Config File

**File**: `.claude/ace_config.json`

```json
{
  "enabled": true,
  "agents": {
    "code_developer": {
      "enabled": true,
      "objective": "Implement features from ROADMAP autonomously",
      "success_criteria": "Code runs, tests pass, DoD verified, PR created",
      "playbook_path": "docs/curator/playbooks/code_developer_playbook.json"
    },
    "assistant": {
      "enabled": false,
      "objective": "Answer user questions and delegate tasks",
      "success_criteria": "User question answered accurately or delegated to correct agent",
      "playbook_path": "docs/curator/playbooks/assistant_playbook.json"
    }
  },
  "generator": {
    "dual_execution": true,
    "save_traces": true,
    "trace_dir": "docs/generator/traces"
  },
  "reflector": {
    "schedule": "daily",
    "hours_to_analyze": 24,
    "min_confidence": 0.5,
    "delta_dir": "docs/reflector/deltas"
  },
  "curator": {
    "schedule": "daily",
    "similarity_threshold": 0.85,
    "pruning_rate": 0.10,
    "min_helpful_count": 2,
    "max_bullets": 150,
    "playbook_dir": "docs/curator/playbooks",
    "report_dir": "docs/curator/reports"
  },
  "embeddings": {
    "provider": "openai",
    "model": "text-embedding-ada-002"
  }
}
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Deliverables**:
- [ ] Data models (`coffee_maker/ace/models.py`)
- [ ] File storage structure
- [ ] Configuration system
- [ ] Unit tests for models

**Estimated Effort**: 2-3 days

### Phase 2: Generator Implementation (Week 1-2)

**Deliverables**:
- [ ] Generator class (`coffee_maker/ace/generator.py`)
- [ ] Dual execution wrapper
- [ ] External observation capture (git diff)
- [ ] Internal observation capture (parsing Claude response)
- [ ] Trace saving to JSON
- [ ] Integration with daemon.py
- [ ] Unit tests for Generator

**Estimated Effort**: 3-4 days

### Phase 3: Reflector Implementation (Week 2)

**Deliverables**:
- [ ] Reflector class (`coffee_maker/ace/reflector.py`)
- [ ] Trace loading and analysis
- [ ] Insight extraction logic
- [ ] Delta item generation
- [ ] Priority and confidence assignment
- [ ] Delta saving to JSON
- [ ] CLI command (`ace-reflector`)
- [ ] Unit tests for Reflector

**Estimated Effort**: 3-4 days

### Phase 4: Curator Implementation (Week 2-3)

**Deliverables**:
- [ ] Curator class (`coffee_maker/ace/curator.py`)
- [ ] Embedding utilities (`coffee_maker/ace/embeddings.py`)
- [ ] Semantic similarity calculation (cosine)
- [ ] De-duplication logic
- [ ] Playbook merging/updating/adding
- [ ] Pruning logic
- [ ] Health metrics calculation
- [ ] Playbook saving to JSON
- [ ] CLI command (`ace-curator`)
- [ ] Unit tests for Curator

**Estimated Effort**: 4-5 days

### Phase 5: Automation & Integration (Week 3)

**Deliverables**:
- [ ] GitHub Actions workflow (`.github/workflows/ace-curation.yml`)
- [ ] Daemon integration (enable/disable ACE)
- [ ] Playbook loader integration
- [ ] Documentation updates
- [ ] Integration tests
- [ ] End-to-end testing

**Estimated Effort**: 2-3 days

**Total Estimated Effort**: 2-3 weeks

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/ace/test_generator.py`
```python
def test_generator_dual_execution():
    """Test that generator executes agent twice"""
    # Setup mock agent
    # Execute with observation
    # Assert two executions recorded
    pass

def test_generator_external_observation():
    """Test external observation capture (git diff)"""
    # Setup git repo
    # Execute agent (creates file)
    # Assert file creation captured in observation
    pass

def test_generator_trace_saving():
    """Test trace is saved to correct location"""
    # Execute with observation
    # Assert trace file exists
    # Assert trace file has correct format
    pass
```

**File**: `tests/unit/ace/test_reflector.py`
```python
def test_reflector_trace_loading():
    """Test reflector loads traces correctly"""
    # Create sample trace files
    # Load traces
    # Assert correct number loaded
    pass

def test_reflector_insight_extraction():
    """Test reflector extracts insights"""
    # Load trace with success pattern
    # Analyze
    # Assert delta extracted with correct type
    pass

def test_reflector_priority_assignment():
    """Test reflector assigns appropriate priority"""
    # Load trace with critical failure
    # Analyze
    # Assert priority 5 assigned
    pass
```

**File**: `tests/unit/ace/test_curator.py`
```python
def test_curator_semantic_deduplication():
    """Test semantic de-duplication works"""
    # Create two similar deltas
    # Consolidate
    # Assert deltas merged
    pass

def test_curator_playbook_merging():
    """Test playbook merging logic"""
    # Load playbook with bullet
    # Add delta with high similarity
    # Consolidate
    # Assert helpful_count incremented
    pass

def test_curator_pruning():
    """Test pruning removes low-value bullets"""
    # Load playbook with low-value bullet
    # Consolidate
    # Assert bullet pruned
    pass
```

### Integration Tests

**File**: `tests/integration/test_ace_e2e.py`
```python
def test_ace_end_to_end():
    """Test complete ACE workflow"""
    # 1. Execute agent with Generator
    # 2. Verify trace saved
    # 3. Run Reflector
    # 4. Verify deltas saved
    # 5. Run Curator
    # 6. Verify playbook updated
    # 7. Execute agent again
    # 8. Verify playbook used
    pass
```

### Manual Testing

1. **Generator**: Run daemon with ACE enabled, verify traces created
2. **Reflector**: Run `ace-reflector` manually, review deltas
3. **Curator**: Run `ace-curator` manually, review playbook
4. **Health Metrics**: Check health metrics make sense
5. **De-duplication**: Add similar deltas, verify merging works

---

## Success Criteria

### Definition of Done

- [ ] All three components (Generator, Reflector, Curator) implemented
- [ ] Unit tests pass with > 80% coverage
- [ ] Integration tests pass
- [ ] Documentation complete (Guide + Technical Spec)
- [ ] ACE enabled for `code_developer` agent
- [ ] Scheduled tasks running (GitHub Actions)
- [ ] Playbook evolving after each execution
- [ ] Health metrics tracked and reporting

### Acceptance Criteria

1. **Generator**:
   - ✅ Executes agent twice for same query
   - ✅ Captures external observation (git changes)
   - ✅ Captures internal observation (reasoning, tools)
   - ✅ Saves trace to JSON in correct location
   - ✅ Trace includes comparative analysis

2. **Reflector**:
   - ✅ Loads traces from last 24 hours
   - ✅ Extracts at least 3-5 insights per trace
   - ✅ Assigns appropriate priority and confidence
   - ✅ Saves deltas to JSON in correct location
   - ✅ Provides recommendations for Curator

3. **Curator**:
   - ✅ Loads deltas and existing playbook
   - ✅ Performs semantic de-duplication (cosine similarity)
   - ✅ Merges/updates/adds insights correctly
   - ✅ Prunes low-value bullets
   - ✅ Updates health metrics
   - ✅ Saves playbook to JSON
   - ✅ Creates curation report

4. **Integration**:
   - ✅ Daemon uses ACE when enabled
   - ✅ Playbook used as context in next execution
   - ✅ Scheduled tasks run daily
   - ✅ Playbook evolves over time
   - ✅ No context collapse observed

5. **Observability**:
   - ✅ Can view traces via CLI or file browser
   - ✅ Can view deltas via CLI or file browser
   - ✅ Can view playbook health metrics
   - ✅ Can manually review and edit playbook

---

## Risks and Mitigations

### Risk 1: Context Collapse

**Description**: Playbook bullets become too generic over time, losing domain-specific detail.

**Likelihood**: Medium
**Impact**: High

**Mitigation**:
- Enforce minimum content length (20 words)
- Require domain-specific terms in new bullets
- Limit pruning rate to 10% per session
- Monitor average content length metric
- Manual playbook review monthly

### Risk 2: Over-Deduplication

**Description**: Semantic similarity threshold too high, merging distinct insights.

**Likelihood**: Medium
**Impact**: Medium

**Mitigation**:
- Start with conservative threshold (0.85)
- Monitor merge decisions in curation reports
- Add manual review for similarity 0.80-0.90
- Allow manual rollback if incorrect merge

### Risk 3: Trace Storage Growth

**Description**: Trace files accumulate rapidly, consuming disk space.

**Likelihood**: High
**Impact**: Low

**Mitigation**:
- Compress old traces (> 30 days)
- Archive to S3 or delete traces > 90 days
- Implement trace retention policy
- Monitor disk usage

### Risk 4: Embedding API Costs

**Description**: Computing embeddings for all deltas and bullets is expensive.

**Likelihood**: Medium
**Impact**: Low

**Mitigation**:
- Cache embeddings in playbook JSON
- Use cheaper embedding model (e.g., text-embedding-ada-002)
- Batch embedding requests
- Only recompute when content changes

### Risk 5: Incorrect Insight Extraction

**Description**: Reflector extracts misleading or incorrect insights.

**Likelihood**: Medium
**Impact**: High

**Mitigation**:
- Require high confidence (> 0.7) for critical insights
- Manual review of priority 5 deltas
- Track harmful_count in playbook
- Deprecate bullets with harmful > helpful

### Risk 6: Conditional Execution Logic Complexity

**Description**: Conditional second execution logic adds complexity and edge cases.

**Likelihood**: Low
**Impact**: Low

**Mitigation**:
- Clear, simple conditions: duration < 30s AND no files modified
- Comprehensive testing of both execution paths (second runs vs. second skipped)
- Trace always notes why second execution was skipped
- Monitor distribution of skipped vs. run second executions
- Adjust threshold (30s) based on real-world data

**Benefits**:
- Cost Savings: Avoid duplicating expensive feature implementations (3+ minute executions)
- Comparison Value: Still get dual execution for quick queries where comparison is valuable
- Example savings: 50% cost reduction on feature implementations, 0% reduction on quick queries

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

### Phase 4: Real-time ACE Dashboard

- Web-based playbook editor
- Real-time health metrics
- Trace visualization
- Manual curation UI

### Phase 5: Automated Tuning

- Self-adjusting similarity thresholds
- Automated pruning schedule optimization
- Predictive coverage analysis

---

## Appendix

### Example Trace JSON

See `docs/ACE_FRAMEWORK_GUIDE.md` section "How It Works" for complete example.

### Example Delta JSON

See `docs/ACE_FRAMEWORK_GUIDE.md` section "How It Works" for complete example.

### Example Playbook JSON

See `docs/ACE_FRAMEWORK_GUIDE.md` section "How It Works" for complete example.

### References

- Research Paper: https://www.arxiv.org/abs/2510.04618
- Agent Definitions: `.claude/agents/*.md`
- User Guide: `docs/ACE_FRAMEWORK_GUIDE.md`

---

**Last Updated**: 2025-10-14
**Version**: 1.0
**Status**: Ready for Implementation
