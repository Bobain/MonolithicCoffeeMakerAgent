# SPEC-066: Curator Agent Implementation

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: ACE Framework Phase 5 - Curator Agent

---

## Executive Summary

This specification defines the **Curator Agent**, an autonomous agent that synthesizes delta items from Reflector into evolving playbooks (Claude Code Skills).

**Key Capabilities**:
- **Delta Item Synthesis**: Reads insights from `docs/reflector/` and merges into playbooks
- **Playbook Creation**: Generates/updates skills in `.claude/skills/`
- **ROI Calculation**: Prioritizes playbooks by estimated time savings
- **Skill Recommendations**: Suggests which skills agents should use
- **Evolution Tracking**: Maintains playbook history and effectiveness metrics

**Impact**:
- **Knowledge Codification**: Delta items become actionable skills
- **Continuous Improvement**: Playbooks evolve based on learnings
- **Time Savings**: Agents reuse proven patterns (2-3x speedup)
- **Self-Improving System**: System gets smarter over time

---

## Problem Statement

### Current Limitations

**1. Delta Items Not Actionable**
- Reflector creates delta items (insights)
- But insights sit unused in `docs/reflector/`
- No mechanism to convert insights → skills
- Knowledge doesn't propagate to agents

**2. Manual Skill Creation**
- Humans must manually write skills
- Time-consuming and inconsistent
- Skills become stale quickly
- No systematic evolution

**3. No ROI Prioritization**
- Don't know which insights have highest impact
- No way to prioritize playbook creation
- Waste effort on low-value skills

**4. Missing Feedback Loop**
- No measurement of skill effectiveness
- Don't know if playbooks actually help
- Can't iterate to improve

### User Requirements

From ACE Framework Phase 5:
- **Curator Agent**: Synthesizes delta items → playbooks
- **Playbook Creation**: Generate/update skills in `.claude/skills/`
- **ROI Calculation**: Prioritize by estimated time savings
- **Skill Recommendations**: Suggest which skills to use when
- **Evolution Tracking**: Measure playbook effectiveness over time

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REFLECTOR OUTPUT                              │
│  docs/reflector/delta_items_*.json                               │
│                                                                  │
│  Delta Items (insights):                                         │
│    - DELTA-001: Architecture reuse check improves success       │
│    - DELTA-002: Missing dependencies cause failures             │
│    - DELTA-003: Large PRs slow review                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CURATOR AGENT ⭐ NEW                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Delta Item Synthesizer                             │ │
│  │  - Groups related delta items                              │ │
│  │  - Identifies themes and patterns                          │ │
│  │  - Merges redundant insights                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            ROI Calculator                                  │ │
│  │  - Estimates time savings per playbook                     │ │
│  │  - Calculates implementation cost                          │ │
│  │  - Prioritizes by ROI (savings / cost)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          Playbook Generator                                │ │
│  │  - Creates new skills from delta items                     │ │
│  │  - Updates existing skills with new insights               │ │
│  │  - Generates skill documentation                           │ │
│  │  - Outputs to .claude/skills/{skill-name}.md               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Skill Recommender                                  │ │
│  │  - Suggests which skills for which agents                  │ │
│  │  - When to use skills (triggers, contexts)                 │ │
│  │  - Expected benefits                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Output: .claude/skills/{skill-name}.md (playbooks)              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT USAGE                                │
│  Agents use updated skills during execution                     │
│  → Performance improves based on learnings                       │
│  → Generator captures new traces                                │
│  → Reflector detects improvement                                │
│  → Curator updates playbooks further (continuous loop)          │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: Curator processes delta items from yesterday

```
1. Curator runs (triggered by Reflector completion)

2. Loads delta items:
   docs/reflector/delta_items_2025-10-18.json
   - DELTA-001: Architecture reuse check improves success (HIGH impact)
   - DELTA-002: Missing dependencies cause failures (MEDIUM impact)
   - DELTA-003: Large PRs slow review (MEDIUM impact)

3. Synthesizes insights:
   - Theme 1: "Spec quality improvements" (DELTA-001)
   - Theme 2: "Implementation reliability" (DELTA-002)
   - Theme 3: "PR review efficiency" (DELTA-003)

4. Calculates ROI:
   - DELTA-001: Estimated 3 hours saved per spec × 5 specs/week = 15 hours/week
     Cost: 2 hours to update architect-startup.md skill
     ROI: 15 / 2 = 7.5x (HIGHEST PRIORITY)

   - DELTA-002: Estimated 1 hour saved per implementation × 10 impls/week = 10 hours/week
     Cost: 1 hour to add dependency check skill
     ROI: 10 / 1 = 10x (HIGHEST PRIORITY)

   - DELTA-003: Estimated 5 minutes saved per PR × 20 PRs/week = 1.7 hours/week
     Cost: 3 hours to create PR size checker
     ROI: 1.7 / 3 = 0.57x (LOW PRIORITY)

5. Generates/updates playbooks:
   Priority 1 (ROI: 10x): Create dependency-check-before-implementation.md
   Priority 2 (ROI: 7.5x): Update architect-startup.md to include reuse check

6. Writes skills:
   .claude/skills/dependency-check-before-implementation.md
   .claude/skills/architect-startup.md (updated)

7. Creates recommendations:
   docs/curator/skill_recommendations_2025-10-18.md
   - architect: Use architecture-reuse-check BEFORE all specs (mandatory)
   - code_developer: Use dependency-check-before-implementation at startup
```

---

## Component Design

### 1. Delta Item Synthesizer

**Purpose**: Group and merge related delta items

```python
# coffee_maker/curator/delta_item_synthesizer.py

from dataclasses import dataclass
from typing import List, Dict
import json
from pathlib import Path

@dataclass
class DeltaItemCluster:
    """Group of related delta items."""
    theme: str                 # Common theme
    delta_items: List[Dict]    # Delta item objects
    priority: str              # "HIGH", "MEDIUM", "LOW"
    estimated_impact: str      # Combined impact

class DeltaItemSynthesizer:
    """
    Synthesizes delta items into themes.

    Groups related insights for playbook creation.
    """

    def load_delta_items(self, file_path: str) -> List[Dict]:
        """Load delta items from file."""
        with open(file_path) as f:
            data = json.load(f)
        return data["delta_items"]

    def synthesize(self, delta_items: List[Dict]) -> List[DeltaItemCluster]:
        """
        Group delta items by theme.

        Themes:
        - Spec quality
        - Implementation reliability
        - Performance optimization
        - Error handling
        - Testing practices
        """
        clusters = {}

        for item in delta_items:
            theme = self._determine_theme(item)

            if theme not in clusters:
                clusters[theme] = DeltaItemCluster(
                    theme=theme,
                    delta_items=[],
                    priority="MEDIUM",
                    estimated_impact="MEDIUM"
                )

            clusters[theme].delta_items.append(item)

        # Calculate cluster priority (highest impact wins)
        for theme, cluster in clusters.items():
            impacts = [item["impact"] for item in cluster.delta_items]
            if "CRITICAL" in impacts:
                cluster.priority = "CRITICAL"
            elif "HIGH" in impacts:
                cluster.priority = "HIGH"
            elif "MEDIUM" in impacts:
                cluster.priority = "MEDIUM"
            else:
                cluster.priority = "LOW"

        return list(clusters.values())

    def _determine_theme(self, delta_item: Dict) -> str:
        """Determine theme for delta item."""
        title = delta_item["title"].lower()
        description = delta_item["description"].lower()

        if "spec" in title or "architecture" in title:
            return "Spec Quality"
        elif "implementation" in title or "dependency" in title or "missing" in title:
            return "Implementation Reliability"
        elif "slow" in title or "performance" in title or "bottleneck" in title:
            return "Performance Optimization"
        elif "error" in title or "failure" in title:
            return "Error Handling"
        elif "test" in title:
            return "Testing Practices"
        else:
            return "General Improvements"
```

### 2. ROI Calculator

**Purpose**: Prioritize playbooks by ROI

```python
# coffee_maker/curator/roi_calculator.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class PlaybookROI:
    """ROI analysis for a playbook."""
    theme: str
    estimated_time_savings_per_week: float  # hours
    implementation_cost: float              # hours
    roi_ratio: float                        # savings / cost
    priority: str                           # Based on ROI

class ROICalculator:
    """
    Calculates ROI for playbooks.

    Formula:
    ROI = (estimated_time_savings_per_week) / implementation_cost
    """

    def calculate_roi(self, cluster: DeltaItemCluster) -> PlaybookROI:
        """Calculate ROI for a delta item cluster."""
        # Estimate time savings
        time_savings = self._estimate_time_savings(cluster)

        # Estimate implementation cost
        implementation_cost = self._estimate_implementation_cost(cluster)

        # Calculate ROI
        roi_ratio = time_savings / implementation_cost if implementation_cost > 0 else 0

        # Determine priority
        if roi_ratio >= 5.0:
            priority = "CRITICAL"  # 5x+ ROI
        elif roi_ratio >= 3.0:
            priority = "HIGH"      # 3-5x ROI
        elif roi_ratio >= 1.5:
            priority = "MEDIUM"    # 1.5-3x ROI
        else:
            priority = "LOW"       # <1.5x ROI

        return PlaybookROI(
            theme=cluster.theme,
            estimated_time_savings_per_week=time_savings,
            implementation_cost=implementation_cost,
            roi_ratio=roi_ratio,
            priority=priority
        )

    def _estimate_time_savings(self, cluster: DeltaItemCluster) -> float:
        """
        Estimate weekly time savings.

        Factors:
        - How many times this issue occurs per week
        - How much time lost each occurrence
        - Confidence in delta items
        """
        total_savings = 0.0

        for item in cluster.delta_items:
            # Occurrences per week (estimate from cluster data)
            occurrences_per_week = self._estimate_weekly_occurrences(item)

            # Time lost per occurrence
            time_per_occurrence = self._estimate_time_loss(item)

            # Adjust by confidence
            confidence = item.get("confidence", 0.5)

            savings = occurrences_per_week * time_per_occurrence * confidence
            total_savings += savings

        return total_savings

    def _estimate_weekly_occurrences(self, delta_item: Dict) -> int:
        """Estimate how many times this occurs per week."""
        occurrences = delta_item.get("occurrences", 1)

        # Assume occurrences are from last 24 hours
        # Scale to weekly
        return occurrences * 7

    def _estimate_time_loss(self, delta_item: Dict) -> float:
        """Estimate time lost per occurrence (hours)."""
        impact = delta_item["impact"]

        # Time loss estimates by impact
        time_loss_map = {
            "CRITICAL": 4.0,  # 4 hours lost
            "HIGH": 2.0,      # 2 hours lost
            "MEDIUM": 1.0,    # 1 hour lost
            "LOW": 0.5        # 30 minutes lost
        }

        return time_loss_map.get(impact, 1.0)

    def _estimate_implementation_cost(self, cluster: DeltaItemCluster) -> float:
        """Estimate cost to implement playbook (hours)."""
        theme = cluster.theme

        # Cost estimates by theme
        cost_map = {
            "Spec Quality": 2.0,              # Update startup skill
            "Implementation Reliability": 1.0, # Add dependency check
            "Performance Optimization": 3.0,   # Profile and optimize
            "Error Handling": 2.0,            # Update error handling
            "Testing Practices": 2.0,         # Create test guideline
            "General Improvements": 1.5
        }

        return cost_map.get(theme, 2.0)
```

### 3. Playbook Generator

**Purpose**: Create/update skills from delta items

```python
# coffee_maker/curator/playbook_generator.py

from pathlib import Path
from typing import List, Dict

class PlaybookGenerator:
    """
    Generates playbooks (skills) from delta items.

    Output: .claude/skills/{skill-name}.md
    """

    def __init__(self, skills_dir: str = ".claude/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def generate_playbook(self, cluster: DeltaItemCluster, roi: PlaybookROI) -> Path:
        """
        Generate playbook from delta item cluster.

        Returns:
            Path to generated skill file
        """
        # Determine skill name
        skill_name = self._create_skill_name(cluster.theme)

        # Check if skill exists
        skill_path = self.skills_dir / f"{skill_name}.md"

        if skill_path.exists():
            # Update existing skill
            return self._update_skill(skill_path, cluster, roi)
        else:
            # Create new skill
            return self._create_skill(skill_path, cluster, roi)

    def _create_skill_name(self, theme: str) -> str:
        """Create skill name from theme."""
        return theme.lower().replace(" ", "-")

    def _create_skill(self, skill_path: Path, cluster: DeltaItemCluster, roi: PlaybookROI) -> Path:
        """Create new skill file."""
        content = self._generate_skill_content(cluster, roi)

        with open(skill_path, "w") as f:
            f.write(content)

        print(f"✅ Created new skill: {skill_path}")
        return skill_path

    def _update_skill(self, skill_path: Path, cluster: DeltaItemCluster, roi: PlaybookROI) -> Path:
        """Update existing skill file."""
        existing_content = skill_path.read_text()

        # Append new insights
        new_insights = self._generate_insights_section(cluster)

        updated_content = existing_content + "\n\n" + new_insights

        with open(skill_path, "w") as f:
            f.write(updated_content)

        print(f"✅ Updated skill: {skill_path}")
        return skill_path

    def _generate_skill_content(self, cluster: DeltaItemCluster, roi: PlaybookROI) -> str:
        """Generate skill markdown content."""
        content = f"""# {cluster.theme} Skill

**Purpose**: {self._generate_purpose(cluster)}

**ROI**: {roi.roi_ratio:.1f}x (saves {roi.estimated_time_savings_per_week:.1f} hours/week)

**Priority**: {roi.priority}

---

## When to Use

{self._generate_when_to_use(cluster)}

## Steps

{self._generate_steps(cluster)}

## Expected Benefits

{self._generate_benefits(cluster)}

## Evidence

Based on analysis of {len(cluster.delta_items)} delta items:

{self._generate_evidence_list(cluster)}

---

**Generated by Curator Agent** on {datetime.now().strftime("%Y-%m-%d")}
"""
        return content

    def _generate_purpose(self, cluster: DeltaItemCluster) -> str:
        """Generate purpose statement."""
        if cluster.theme == "Spec Quality":
            return "Improve technical specification quality and approval rate"
        elif cluster.theme == "Implementation Reliability":
            return "Prevent common implementation failures"
        elif cluster.theme == "Performance Optimization":
            return "Identify and fix performance bottlenecks"
        else:
            return f"Improve {cluster.theme.lower()}"

    def _generate_when_to_use(self, cluster: DeltaItemCluster) -> str:
        """Generate when-to-use section."""
        recommendations = []
        for item in cluster.delta_items:
            recommendations.append(f"- {item['recommendation']}")
        return "\n".join(recommendations)

    def _generate_steps(self, cluster: DeltaItemCluster) -> str:
        """Generate steps section."""
        steps = []
        for i, item in enumerate(cluster.delta_items, start=1):
            steps.append(f"{i}. {item['title']}")
            steps.append(f"   - {item['description']}")
        return "\n".join(steps)

    def _generate_benefits(self, cluster: DeltaItemCluster) -> str:
        """Generate benefits section."""
        benefits = []
        for item in cluster.delta_items:
            impact = item["impact"]
            confidence = item.get("confidence", 0.5)
            benefits.append(f"- {impact} impact ({confidence*100:.0f}% confidence): {item['title']}")
        return "\n".join(benefits)

    def _generate_evidence_list(self, cluster: DeltaItemCluster) -> str:
        """Generate evidence list."""
        evidence = []
        for item in cluster.delta_items:
            evidence.append(f"- **{item['id']}**: {item['title']}")
            evidence.append(f"  - Occurrences: {item['occurrences']}")
            evidence.append(f"  - Confidence: {item.get('confidence', 0.5)*100:.0f}%")
        return "\n".join(evidence)

    def _generate_insights_section(self, cluster: DeltaItemCluster) -> str:
        """Generate insights section for skill update."""
        return f"""## New Insights ({datetime.now().strftime("%Y-%m-%d")})

{self._generate_steps(cluster)}

{self._generate_evidence_list(cluster)}
"""
```

### 4. Curator Agent

**Purpose**: Main orchestration logic

```python
# coffee_maker/curator/curator_agent.py

from coffee_maker.curator.delta_item_synthesizer import DeltaItemSynthesizer
from coffee_maker.curator.roi_calculator import ROICalculator
from coffee_maker.curator.playbook_generator import PlaybookGenerator
from coffee_maker.langfuse_observe import observe
from pathlib import Path

class CuratorAgent:
    """
    Curator Agent: Synthesizes delta items into evolving playbooks.

    Responsibilities:
    - Load delta items from Reflector
    - Group into themes
    - Calculate ROI
    - Generate/update skills
    - Create recommendations
    """

    def __init__(self):
        self.synthesizer = DeltaItemSynthesizer()
        self.roi_calculator = ROICalculator()
        self.playbook_generator = PlaybookGenerator()

    @observe(name="curator_process_delta_items")
    def process_delta_items(self, delta_items_file: str):
        """
        Process delta items and create playbooks.

        Args:
            delta_items_file: Path to delta items JSON

        Returns:
            List of created/updated skill files
        """
        # 1. Load delta items
        delta_items = self.synthesizer.load_delta_items(delta_items_file)
        print(f"📊 Loaded {len(delta_items)} delta items")

        if not delta_items:
            print("⚠️ No delta items to process")
            return []

        # 2. Synthesize into clusters
        clusters = self.synthesizer.synthesize(delta_items)
        print(f"🔍 Identified {len(clusters)} themes")

        # 3. Calculate ROI for each cluster
        roi_results = []
        for cluster in clusters:
            roi = self.roi_calculator.calculate_roi(cluster)
            roi_results.append((cluster, roi))
            print(f"   - {cluster.theme}: ROI {roi.roi_ratio:.1f}x ({roi.priority} priority)")

        # 4. Sort by ROI (highest first)
        roi_results.sort(key=lambda x: x[1].roi_ratio, reverse=True)

        # 5. Generate playbooks
        created_skills = []
        for cluster, roi in roi_results:
            if roi.roi_ratio >= 1.5:  # Only create if ROI >= 1.5x
                skill_path = self.playbook_generator.generate_playbook(cluster, roi)
                created_skills.append(skill_path)

        print(f"✅ Created/updated {len(created_skills)} skills")

        # 6. Create recommendations
        self._create_recommendations(roi_results)

        return created_skills

    def _create_recommendations(self, roi_results: List):
        """Create skill recommendation document."""
        output_dir = Path("docs/curator")
        output_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        output_file = output_dir / f"skill_recommendations_{date_str}.md"

        content = f"""# Skill Recommendations

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Total Themes**: {len(roi_results)}

---

## High-Priority Skills (ROI >= 3x)

"""

        high_priority = [r for r in roi_results if r[1].roi_ratio >= 3.0]

        for cluster, roi in high_priority:
            content += f"""### {cluster.theme}

- **ROI**: {roi.roi_ratio:.1f}x
- **Estimated Savings**: {roi.estimated_time_savings_per_week:.1f} hours/week
- **Implementation Cost**: {roi.implementation_cost:.1f} hours
- **Recommendation**: {cluster.delta_items[0]['recommendation']}

"""

        content += f"""## Medium-Priority Skills (ROI 1.5-3x)

"""

        medium_priority = [r for r in roi_results if 1.5 <= r[1].roi_ratio < 3.0]

        for cluster, roi in medium_priority:
            content += f"- **{cluster.theme}**: ROI {roi.roi_ratio:.1f}x\n"

        with open(output_file, "w") as f:
            f.write(content)

        print(f"✅ Created recommendations: {output_file}")
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_curator.py

def test_delta_item_synthesizer_groups_by_theme():
    """Test synthesizer groups delta items by theme."""
    synthesizer = DeltaItemSynthesizer()

    delta_items = [
        {"title": "Spec quality improved", "impact": "HIGH"},
        {"title": "Spec approval faster", "impact": "MEDIUM"},
        {"title": "Implementation failed due to missing dep", "impact": "MEDIUM"}
    ]

    clusters = synthesizer.synthesize(delta_items)

    assert len(clusters) == 2  # Spec Quality + Implementation Reliability
    assert any(c.theme == "Spec Quality" for c in clusters)

def test_roi_calculator_prioritizes_correctly():
    """Test ROI calculator prioritizes by ROI ratio."""
    calculator = ROICalculator()

    cluster_high = DeltaItemCluster(
        theme="Test",
        delta_items=[{"impact": "HIGH", "occurrences": 10, "confidence": 0.9}],
        priority="HIGH",
        estimated_impact="HIGH"
    )

    roi = calculator.calculate_roi(cluster_high)

    assert roi.roi_ratio > 3.0  # High ROI
    assert roi.priority in ["HIGH", "CRITICAL"]
```

---

## Rollout Plan

### Phase 1: Core Components (Week 1)
- [ ] Implement DeltaItemSynthesizer
- [ ] Implement ROICalculator
- [ ] Implement PlaybookGenerator
- [ ] Implement CuratorAgent
- [ ] Unit tests (>80% coverage)

### Phase 2: Integration (Week 2)
- [ ] Integrate with Reflector
- [ ] Create curator-startup.md skill
- [ ] Test end-to-end workflow
- [ ] Validate playbook quality

### Phase 3: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Delta item synthesis logic, ROI calculation model, playbook generation
  - **Code Quality**: Theme clustering algorithms, skill file generation, error handling
  - **Security**: File write permissions (.claude/skills/ writable), no arbitrary code in playbooks
  - **Performance**: Delta processing time (<5min for 100 items), ROI calculation accuracy
  - **CFR Compliance**:
    - CFR-007: Curator context budget (<30%)
    - CFR-008: Curator independence (runs autonomously after Reflector)
    - CFR-009: Graceful failure (if ROI too low, skip playbook creation)
  - **Dependency Approval**: If new packages added (unlikely for this feature)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 4: Evolution Tracking (Week 3)
- [ ] Track playbook usage metrics
- [ ] Measure time savings
- [ ] Iterate based on feedback

---

## Conclusion

The Curator Agent closes the ACE framework loop by converting delta items into actionable playbooks that improve agent performance over time.

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/curator/delta_item_synthesizer.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/curator/roi_calculator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/curator/playbook_generator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/curator/curator_agent.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/curator-startup.md`
