# SPEC-065: Reflector Agent Implementation

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: ACE Framework Phase 5 - Reflector Agent

---

## Executive Summary

This specification defines the **Reflector Agent**, an autonomous agent that analyzes execution traces from the Generator to extract patterns, insights, and learnings (delta items).

**Key Capabilities**:
- **Trace Analysis**: Parses execution traces from `docs/generator/` directory
- **Pattern Detection**: Identifies successful patterns, common failures, bottlenecks
- **Delta Item Creation**: Generates insights in structured format
- **Automated Scheduling**: Runs daily/weekly to analyze recent traces
- **Improvement Suggestions**: Provides actionable recommendations

**Impact**:
- **Continuous Learning**: System learns from past executions automatically
- **Pattern Recognition**: Identifies what works well (and what doesn't)
- **Knowledge Base**: Delta items feed into Curator for playbook creation
- **Proactive Improvement**: Suggests optimizations before problems occur

---

## Problem Statement

### Current Limitations

**1. No Automated Learning**
- Execution traces exist (`docs/generator/`) but aren't analyzed
- No systematic extraction of learnings
- Agents don't learn from past successes/failures
- Same mistakes repeated

**2. Manual Pattern Detection**
- Humans must manually review traces to find patterns
- Time-consuming and error-prone
- Insights get lost or forgotten
- No cumulative knowledge base

**3. No Feedback Loop**
- Agents execute tasks but don't reflect on outcomes
- No mechanism to improve from experience
- Missing ACE framework's reflection layer

### User Requirements

From ACE Framework Phase 5:
- **Reflector Agent**: Analyzes traces → extracts delta items
- **Pattern Detection**: Identify successful patterns, common failures
- **Automated Scheduling**: Daily/weekly analysis of recent traces
- **Delta Items**: Structured insights for Curator consumption
- **Integration**: Seamless connection to Generator and Curator

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GENERATOR LAYER                             │
│  (Captures all agent executions in trace files)                  │
│                                                                  │
│  docs/generator/                                                 │
│    ├── architect_2025-10-18_10-30-00.json                       │
│    ├── code_developer_2025-10-18_11-15-00.json                  │
│    └── project_manager_2025-10-18_12-00-00.json                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REFLECTOR AGENT ⭐ NEW                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Trace Analyzer                                  │ │
│  │  - Loads trace files from docs/generator/                 │ │
│  │  - Parses execution steps, timing, results                │ │
│  │  - Groups traces by agent type, task type                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          Pattern Detector                                  │ │
│  │  - Successful patterns (what worked well)                 │ │
│  │  - Failure patterns (what went wrong)                     │ │
│  │  - Bottleneck patterns (what was slow)                    │ │
│  │  - Anti-patterns (what to avoid)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Delta Item Creator                                 │ │
│  │  - Generates structured insights                          │ │
│  │  - Categorizes by type (pattern, failure, bottleneck)     │ │
│  │  - Assigns confidence score                               │ │
│  │  - Provides context and examples                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Output: docs/reflector/delta_items_2025-10-18.json              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CURATOR AGENT                                 │
│  (Synthesizes delta items → playbooks)                           │
│                                                                  │
│  Reads: docs/reflector/delta_items_*.json                        │
│  Creates: .claude/skills/{skill-name}.md (playbooks)             │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: Reflector analyzes yesterday's traces

```
1. Reflector runs daily (scheduled at 2am)

2. Loads recent traces:
   - architect_2025-10-17_*.json (5 executions)
   - code_developer_2025-10-17_*.json (12 executions)
   - project_manager_2025-10-17_*.json (8 executions)

3. Analyzes patterns:
   - SUCCESS: architect created 5 specs, all approved
     → Pattern: "Specs with architecture-reuse-check get approved faster"
   - FAILURE: code_developer failed 2 implementations due to missing dependencies
     → Pattern: "Missing poetry add step causes failures"
   - BOTTLENECK: project_manager took 10+ minutes on PR reviews
     → Pattern: "Large PRs (>500 LOC) slow down review"

4. Creates delta items:
   {
     "delta_items": [
       {
         "id": "DELTA-001",
         "type": "successful_pattern",
         "title": "Architecture Reuse Check Improves Spec Approval Rate",
         "description": "Specs that run architecture-reuse-check skill get approved 2x faster",
         "confidence": 0.85,
         "evidence": ["architect_2025-10-17_10-30-00.json", ...],
         "recommendation": "Make architecture-reuse-check mandatory in architect-startup.md",
         "impact": "HIGH"
       },
       {
         "id": "DELTA-002",
         "type": "failure_pattern",
         "title": "Missing Dependency Steps Cause Implementation Failures",
         "description": "code_developer forgets to run 'poetry add' before implementing",
         "confidence": 0.90,
         "evidence": ["code_developer_2025-10-17_14-15-00.json", ...],
         "recommendation": "Add dependency check step to code-developer-startup.md",
         "impact": "MEDIUM"
       }
     ]
   }

5. Writes delta items:
   docs/reflector/delta_items_2025-10-18.json

6. Notifies curator:
   "New delta items available for synthesis"
```

---

## Component Design

### 1. Trace Analyzer

**Purpose**: Load and parse execution traces

```python
# coffee_maker/reflector/trace_analyzer.py

from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import json
from datetime import datetime, timedelta

@dataclass
class ExecutionTrace:
    """Parsed execution trace."""
    agent_type: str              # "architect", "code_developer", etc.
    task_type: str               # "create_spec", "implement_feature", etc.
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    status: str                  # "success", "failure", "timeout"
    steps: List[Dict]            # Execution steps
    result: Dict                 # Final result
    error: str = None            # Error message if failed
    trace_file: str = None       # Original trace file path

class TraceAnalyzer:
    """
    Analyzes execution traces from Generator.

    Traces stored in: docs/generator/{agent}_{timestamp}.json
    """

    def __init__(self, traces_dir: str = "docs/generator"):
        self.traces_dir = Path(traces_dir)

    def load_recent_traces(self, hours: int = 24) -> List[ExecutionTrace]:
        """
        Load traces from last N hours.

        Args:
            hours: Time window (default: 24 hours)

        Returns:
            List of ExecutionTrace objects
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        traces = []

        # Find all trace files
        for trace_file in self.traces_dir.glob("*.json"):
            # Parse timestamp from filename
            # Format: {agent}_{YYYY-MM-DD}_{HH-MM-SS}.json
            parts = trace_file.stem.split("_")
            if len(parts) >= 4:
                try:
                    date_str = f"{parts[-2]} {parts[-1].replace('-', ':')}"
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

                    # Check if within time window
                    if timestamp >= cutoff_time:
                        trace = self._parse_trace_file(trace_file)
                        traces.append(trace)
                except (ValueError, IndexError):
                    continue

        return sorted(traces, key=lambda t: t.started_at)

    def _parse_trace_file(self, trace_file: Path) -> ExecutionTrace:
        """Parse trace file into ExecutionTrace object."""
        with open(trace_file) as f:
            data = json.load(f)

        return ExecutionTrace(
            agent_type=data.get("agent_type"),
            task_type=data.get("task_type"),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]),
            duration_seconds=data["duration_seconds"],
            status=data["status"],
            steps=data.get("steps", []),
            result=data.get("result", {}),
            error=data.get("error"),
            trace_file=str(trace_file)
        )

    def group_by_agent(self, traces: List[ExecutionTrace]) -> Dict[str, List[ExecutionTrace]]:
        """Group traces by agent type."""
        grouped = {}
        for trace in traces:
            if trace.agent_type not in grouped:
                grouped[trace.agent_type] = []
            grouped[trace.agent_type].append(trace)
        return grouped

    def group_by_task_type(self, traces: List[ExecutionTrace]) -> Dict[str, List[ExecutionTrace]]:
        """Group traces by task type."""
        grouped = {}
        for trace in traces:
            if trace.task_type not in grouped:
                grouped[trace.task_type] = []
            grouped[trace.task_type].append(trace)
        return grouped

    def get_success_rate(self, traces: List[ExecutionTrace]) -> float:
        """Calculate success rate for traces."""
        if not traces:
            return 0.0
        successful = sum(1 for t in traces if t.status == "success")
        return (successful / len(traces)) * 100

    def get_average_duration(self, traces: List[ExecutionTrace]) -> float:
        """Calculate average duration for traces."""
        if not traces:
            return 0.0
        total_duration = sum(t.duration_seconds for t in traces)
        return total_duration / len(traces)
```

### 2. Pattern Detector

**Purpose**: Identify patterns in execution traces

```python
# coffee_maker/reflector/pattern_detector.py

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class PatternType(Enum):
    SUCCESSFUL_PATTERN = "successful_pattern"
    FAILURE_PATTERN = "failure_pattern"
    BOTTLENECK_PATTERN = "bottleneck_pattern"
    ANTI_PATTERN = "anti_pattern"

@dataclass
class Pattern:
    """Detected pattern in execution traces."""
    type: PatternType
    title: str
    description: str
    confidence: float           # 0.0-1.0 (how confident we are)
    occurrences: int            # How many times observed
    evidence: List[str]         # Trace file paths
    recommendation: str         # What to do about it
    impact: str                 # "LOW", "MEDIUM", "HIGH", "CRITICAL"

class PatternDetector:
    """
    Detects patterns in execution traces.

    Patterns:
    - Successful: What works well
    - Failure: What goes wrong
    - Bottleneck: What is slow
    - Anti-pattern: What to avoid
    """

    def detect_patterns(self, traces: List[ExecutionTrace]) -> List[Pattern]:
        """
        Detect all patterns in traces.

        Returns:
            List of Pattern objects
        """
        patterns = []

        # Detect successful patterns
        patterns.extend(self._detect_successful_patterns(traces))

        # Detect failure patterns
        patterns.extend(self._detect_failure_patterns(traces))

        # Detect bottleneck patterns
        patterns.extend(self._detect_bottleneck_patterns(traces))

        # Detect anti-patterns
        patterns.extend(self._detect_anti_patterns(traces))

        return patterns

    def _detect_successful_patterns(self, traces: List[ExecutionTrace]) -> List[Pattern]:
        """Detect what works well."""
        patterns = []

        # Pattern: architect using architecture-reuse-check
        architect_traces = [t for t in traces if t.agent_type == "architect"]
        with_reuse_check = [t for t in architect_traces
                             if self._uses_skill(t, "architecture-reuse-check")]

        if len(with_reuse_check) >= 3:
            # Calculate success rate difference
            reuse_success = sum(1 for t in with_reuse_check if t.status == "success") / len(with_reuse_check)
            without_reuse = [t for t in architect_traces if t not in with_reuse_check]
            if without_reuse:
                no_reuse_success = sum(1 for t in without_reuse if t.status == "success") / len(without_reuse)

                if reuse_success > no_reuse_success + 0.2:  # 20% improvement
                    patterns.append(Pattern(
                        type=PatternType.SUCCESSFUL_PATTERN,
                        title="Architecture Reuse Check Improves Success Rate",
                        description=f"Specs using architecture-reuse-check have {reuse_success*100:.0f}% success vs {no_reuse_success*100:.0f}% without",
                        confidence=0.85,
                        occurrences=len(with_reuse_check),
                        evidence=[t.trace_file for t in with_reuse_check],
                        recommendation="Make architecture-reuse-check mandatory in architect workflow",
                        impact="HIGH"
                    ))

        return patterns

    def _detect_failure_patterns(self, traces: List[ExecutionTrace]) -> List[Pattern]:
        """Detect common failures."""
        patterns = []

        # Pattern: Missing dependencies
        failed_traces = [t for t in traces if t.status == "failure"]
        dependency_failures = [t for t in failed_traces
                                if self._is_dependency_error(t)]

        if len(dependency_failures) >= 2:
            patterns.append(Pattern(
                type=PatternType.FAILURE_PATTERN,
                title="Missing Dependencies Cause Frequent Failures",
                description=f"{len(dependency_failures)} failures due to missing 'poetry add' step",
                confidence=0.90,
                occurrences=len(dependency_failures),
                evidence=[t.trace_file for t in dependency_failures],
                recommendation="Add dependency verification to startup skills",
                impact="MEDIUM"
            ))

        # Pattern: Missing API keys
        api_key_failures = [t for t in failed_traces
                             if self._is_api_key_error(t)]

        if len(api_key_failures) >= 2:
            patterns.append(Pattern(
                type=PatternType.FAILURE_PATTERN,
                title="Missing API Keys Block Agent Startup",
                description=f"{len(api_key_failures)} failures due to missing ANTHROPIC_API_KEY",
                confidence=0.95,
                occurrences=len(api_key_failures),
                evidence=[t.trace_file for t in api_key_failures],
                recommendation="Improve API key validation in startup skills",
                impact="HIGH"
            ))

        return patterns

    def _detect_bottleneck_patterns(self, traces: List[ExecutionTrace]) -> List[Pattern]:
        """Detect slow operations."""
        patterns = []

        # Pattern: Slow spec creation
        architect_traces = [t for t in traces
                             if t.agent_type == "architect" and t.task_type == "create_spec"]

        if architect_traces:
            avg_duration = sum(t.duration_seconds for t in architect_traces) / len(architect_traces)

            if avg_duration > 600:  # >10 minutes
                slow_specs = [t for t in architect_traces if t.duration_seconds > 600]

                patterns.append(Pattern(
                    type=PatternType.BOTTLENECK_PATTERN,
                    title="Spec Creation Takes Excessive Time",
                    description=f"Average spec creation: {avg_duration/60:.1f} minutes (target: <5 min)",
                    confidence=0.80,
                    occurrences=len(slow_specs),
                    evidence=[t.trace_file for t in slow_specs],
                    recommendation="Profile LLM calls, optimize prompts, reduce context size",
                    impact="MEDIUM"
                ))

        return patterns

    def _detect_anti_patterns(self, traces: List[ExecutionTrace]) -> List[Pattern]:
        """Detect patterns to avoid."""
        patterns = []

        # Pattern: Repeated failures on same task
        failure_counts = {}
        for trace in traces:
            if trace.status == "failure":
                key = (trace.agent_type, trace.task_type)
                failure_counts[key] = failure_counts.get(key, 0) + 1

        for (agent, task), count in failure_counts.items():
            if count >= 3:
                patterns.append(Pattern(
                    type=PatternType.ANTI_PATTERN,
                    title=f"Repeated Failures on {agent} {task}",
                    description=f"{count} consecutive failures on same task type",
                    confidence=0.75,
                    occurrences=count,
                    evidence=[],
                    recommendation="Review task requirements, add validation, improve error handling",
                    impact="HIGH" if count >= 5 else "MEDIUM"
                ))

        return patterns

    def _uses_skill(self, trace: ExecutionTrace, skill_name: str) -> bool:
        """Check if trace uses a specific skill."""
        for step in trace.steps:
            if skill_name in step.get("description", "").lower():
                return True
        return False

    def _is_dependency_error(self, trace: ExecutionTrace) -> bool:
        """Check if failure was due to missing dependency."""
        if trace.error:
            return "ModuleNotFoundError" in trace.error or "ImportError" in trace.error
        return False

    def _is_api_key_error(self, trace: ExecutionTrace) -> bool:
        """Check if failure was due to missing API key."""
        if trace.error:
            return "ANTHROPIC_API_KEY" in trace.error or "APIKeyMissingError" in trace.error
        return False
```

### 3. Delta Item Creator

**Purpose**: Convert patterns into structured delta items

```python
# coffee_maker/reflector/delta_item_creator.py

from dataclasses import dataclass, asdict
from typing import List, Dict
import json
from pathlib import Path
from datetime import datetime

@dataclass
class DeltaItem:
    """Structured insight from trace analysis."""
    id: str                    # DELTA-XXX
    type: str                  # Pattern type
    title: str
    description: str
    confidence: float          # 0.0-1.0
    evidence: List[str]        # Trace file paths
    recommendation: str
    impact: str                # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    created_at: str            # ISO timestamp
    occurrences: int

class DeltaItemCreator:
    """
    Creates delta items from detected patterns.

    Output: docs/reflector/delta_items_{date}.json
    """

    def __init__(self, output_dir: str = "docs/reflector"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_delta_items(self, patterns: List[Pattern]) -> List[DeltaItem]:
        """
        Convert patterns into delta items.

        Args:
            patterns: Detected patterns

        Returns:
            List of DeltaItem objects
        """
        delta_items = []

        for i, pattern in enumerate(patterns, start=1):
            delta_item = DeltaItem(
                id=f"DELTA-{i:03d}",
                type=pattern.type.value,
                title=pattern.title,
                description=pattern.description,
                confidence=pattern.confidence,
                evidence=pattern.evidence,
                recommendation=pattern.recommendation,
                impact=pattern.impact,
                created_at=datetime.now().isoformat(),
                occurrences=pattern.occurrences
            )
            delta_items.append(delta_item)

        return delta_items

    def write_delta_items(self, delta_items: List[DeltaItem]):
        """
        Write delta items to file.

        Output: docs/reflector/delta_items_{date}.json
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_file = self.output_dir / f"delta_items_{date_str}.json"

        data = {
            "generated_at": datetime.now().isoformat(),
            "total_items": len(delta_items),
            "delta_items": [asdict(item) for item in delta_items]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Created {len(delta_items)} delta items: {output_file}")

        return output_file
```

### 4. Reflector Agent

**Purpose**: Main orchestration logic

```python
# coffee_maker/reflector/reflector_agent.py

from coffee_maker.reflector.trace_analyzer import TraceAnalyzer
from coffee_maker.reflector.pattern_detector import PatternDetector
from coffee_maker.reflector.delta_item_creator import DeltaItemCreator
from coffee_maker.langfuse_observe import observe

class ReflectorAgent:
    """
    Reflector Agent: Analyzes execution traces and extracts learnings.

    Responsibilities:
    - Load recent execution traces
    - Detect patterns (successful, failure, bottleneck, anti-pattern)
    - Create delta items for Curator
    """

    def __init__(self):
        self.trace_analyzer = TraceAnalyzer()
        self.pattern_detector = PatternDetector()
        self.delta_item_creator = DeltaItemCreator()

    @observe(name="reflector_analyze_traces")
    def analyze_recent_traces(self, hours: int = 24):
        """
        Analyze traces from last N hours.

        Args:
            hours: Time window (default: 24 hours)

        Returns:
            Path to delta items file
        """
        # 1. Load recent traces
        traces = self.trace_analyzer.load_recent_traces(hours=hours)
        print(f"📊 Loaded {len(traces)} traces from last {hours} hours")

        if not traces:
            print("⚠️ No traces found, skipping analysis")
            return None

        # 2. Detect patterns
        patterns = self.pattern_detector.detect_patterns(traces)
        print(f"🔍 Detected {len(patterns)} patterns")

        for pattern in patterns:
            print(f"   - {pattern.title} ({pattern.impact} impact, {pattern.confidence:.0%} confidence)")

        # 3. Create delta items
        delta_items = self.delta_item_creator.create_delta_items(patterns)

        # 4. Write delta items
        output_file = self.delta_item_creator.write_delta_items(delta_items)

        return output_file

    def run_daily_analysis(self):
        """Run daily analysis (scheduled at 2am)."""
        print("🌙 Running daily reflection analysis...")
        output_file = self.analyze_recent_traces(hours=24)

        if output_file:
            print(f"✅ Daily analysis complete: {output_file}")
        else:
            print("⚠️ No traces to analyze")

    def run_weekly_analysis(self):
        """Run weekly analysis (scheduled on Mondays)."""
        print("📅 Running weekly reflection analysis...")
        output_file = self.analyze_recent_traces(hours=168)  # 7 days

        if output_file:
            print(f"✅ Weekly analysis complete: {output_file}")
        else:
            print("⚠️ No traces to analyze")
```

---

## Scheduling

### Daily Analysis (2am)

```python
# coffee_maker/reflector/scheduler.py

import schedule
import time
from coffee_maker.reflector.reflector_agent import ReflectorAgent

def schedule_reflector():
    """Schedule reflector agent runs."""
    reflector = ReflectorAgent()

    # Daily at 2am
    schedule.every().day.at("02:00").do(reflector.run_daily_analysis)

    # Weekly on Monday at 2am
    schedule.every().monday.at("02:00").do(reflector.run_weekly_analysis)

    print("🕐 Reflector scheduler started")
    print("   - Daily analysis: 2:00 AM")
    print("   - Weekly analysis: Monday 2:00 AM")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    schedule_reflector()
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_reflector.py

def test_trace_analyzer_loads_recent_traces():
    """Test trace analyzer loads traces from last 24 hours."""
    analyzer = TraceAnalyzer()
    traces = analyzer.load_recent_traces(hours=24)

    assert len(traces) > 0
    assert all(isinstance(t, ExecutionTrace) for t in traces)

def test_pattern_detector_finds_successful_patterns():
    """Test pattern detector identifies successful patterns."""
    detector = PatternDetector()

    # Mock traces with successful pattern
    traces = [
        ExecutionTrace(..., status="success", uses_skill("architecture-reuse-check")),
        ExecutionTrace(..., status="success", uses_skill("architecture-reuse-check")),
        ExecutionTrace(..., status="failure", no_skill)
    ]

    patterns = detector.detect_patterns(traces)

    successful_patterns = [p for p in patterns if p.type == PatternType.SUCCESSFUL_PATTERN]
    assert len(successful_patterns) > 0
    assert "architecture-reuse-check" in successful_patterns[0].title.lower()

def test_delta_item_creator_writes_file():
    """Test delta item creator writes file correctly."""
    creator = DeltaItemCreator()

    delta_items = [
        DeltaItem(
            id="DELTA-001",
            type="successful_pattern",
            title="Test Pattern",
            ...
        )
    ]

    output_file = creator.write_delta_items(delta_items)

    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert len(data["delta_items"]) == 1
    assert data["delta_items"][0]["id"] == "DELTA-001"
```

---

## Rollout Plan

### Phase 1: Core Components (Week 1)
- [ ] Implement TraceAnalyzer
- [ ] Implement PatternDetector
- [ ] Implement DeltaItemCreator
- [ ] Implement ReflectorAgent
- [ ] Unit tests (>80% coverage)

### Phase 2: Scheduling & Integration (Week 2)
- [ ] Implement scheduler (daily/weekly)
- [ ] Create reflector-startup.md skill
- [ ] Integration tests
- [ ] Test with real traces

### Phase 3: Pattern Refinement (Week 3)
- [ ] Tune pattern detection thresholds
- [ ] Add more pattern types
- [ ] Improve confidence scoring
- [ ] User validation

### Phase 4: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Trace analysis patterns, delta item structure, reflector autonomy
  - **Code Quality**: Pattern detection algorithms, confidence scoring logic, error handling
  - **Security**: Trace file access (read-only), no sensitive data leakage in delta items
  - **Performance**: Trace parsing speed (target: <2min for 24hrs of traces), memory usage
  - **CFR Compliance**:
    - CFR-007: Reflector context budget (<30%)
    - CFR-008: Reflector independence (no blocking other agents)
    - CFR-009: Graceful failure (if no traces found, exit cleanly)
  - **Dependency Approval**: If new packages added (unlikely for this feature)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 5: Production Deployment (Week 4)
- [ ] Deploy to production
- [ ] Monitor delta item quality
- [ ] Iterate based on feedback

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Patterns Detected** | >5 per day |
| **Confidence Accuracy** | >80% |
| **Delta Item Quality** | Curator accepts >90% |
| **Analysis Time** | <2 minutes |
| **False Positives** | <10% |

---

## Conclusion

The Reflector Agent provides automated learning from execution traces, extracting patterns and insights that feed into the Curator for playbook creation.

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/reflector/trace_analyzer.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/reflector/pattern_detector.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/reflector/delta_item_creator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/reflector/reflector_agent.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/reflector/scheduler.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/reflector-startup.md`
