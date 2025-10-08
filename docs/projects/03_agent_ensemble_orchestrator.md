# Projet 3: Agent Ensemble Orchestrator

## 🎯 Vue d'ensemble

Un meta-agent qui **coordonne plusieurs agents spécialisés** pour résoudre des problèmes complexes. Chaque agent a une expertise (architecture, code, tests, docs) et le orchestrator décompose les tâches et synthétise les résultats.

### Objectifs
- Coordination multi-agents avec patterns (séquentiel, parallèle, débat)
- Décomposition automatique de tâches complexes
- Routing intelligent vers agents spécialisés
- Métriques de collaboration

---

## 🏗️ Architecture

```
coffee_maker/agent_ensemble/
├── __init__.py
├── orchestrator.py              # Meta-agent principal
├── agents/
│   ├── base_agent.py            # Agent de base
│   ├── architect_agent.py       # Design & architecture
│   ├── coder_agent.py           # Implémentation
│   ├── tester_agent.py          # Tests
│   ├── reviewer_agent.py        # Review
│   └── documenter_agent.py      # Documentation
├── patterns/
│   ├── sequential.py            # Pipeline séquentiel
│   ├── parallel.py              # Exécution parallèle
│   ├── debate.py                # Consensus par débat
│   └── router.py                # Routing vers spécialistes
└── coordination/
    ├── task_decomposer.py       # Décomposition tâches
    └── result_synthesizer.py    # Synthèse résultats
```

---

## 📦 Composants Clés

### 1. AgentEnsemble (Core)

```python
"""Agent ensemble orchestrator."""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Task:
    """Task to be solved."""
    description: str
    context: Dict
    constraints: Dict = None
    priority: int = 0

@dataclass
class SubTask:
    """Subtask assigned to specific agent."""
    agent_type: str  # architect, coder, tester, etc.
    description: str
    inputs: Dict
    depends_on: List[str] = None

@dataclass
class Solution:
    """Complete solution from ensemble."""
    task_id: str
    subtask_results: List[Dict]
    final_output: str
    agents_used: List[str]
    total_cost: float
    total_time: float
    quality_score: float


class AgentEnsemble:
    """Orchestrates multiple specialized agents.

    Example:
        >>> ensemble = AgentEnsemble()
        >>> task = Task(
        ...     description="Add user authentication",
        ...     context={"framework": "FastAPI"}
        ... )
        >>> solution = await ensemble.solve(task)
    """

    def __init__(self):
        from coffee_maker.langchain_observe.builder import LLMBuilder

        # Initialize specialized agents
        self.agents = {
            "architect": ArchitectAgent(
                llm=LLMBuilder()
                    .with_primary("anthropic", "claude-3-5-sonnet-20241022")
                    .with_fallback("openai", "gpt-4o")
                    .build()
            ),
            "coder": CoderAgent(
                llm=LLMBuilder()
                    .with_primary("openai", "gpt-4o")
                    .with_fallback("anthropic", "claude-3-5-sonnet-20241022")
                    .build()
            ),
            "tester": TesterAgent(
                llm=LLMBuilder()
                    .with_primary("gemini", "gemini-2.0-flash-exp")
                    .build()
            ),
            "reviewer": ReviewerAgent(
                llm=LLMBuilder()
                    .with_primary("anthropic", "claude-3-5-haiku-20241022")
                    .build()
            ),
            "documenter": DocumenterAgent(
                llm=LLMBuilder()
                    .with_primary("openai", "gpt-4o-mini")
                    .build()
            ),
        }

        # Orchestrator (meta-agent)
        self.orchestrator = OrchestratorAgent(
            llm=LLMBuilder()
                .with_primary("anthropic", "claude-3-5-sonnet-20241022")
                .build()
        )

    async def solve(self, task: Task) -> Solution:
        """Solve task using agent ensemble.

        Steps:
        1. Orchestrator decomposes task into subtasks
        2. Execute subtasks (sequential/parallel based on dependencies)
        3. Synthesize results
        """
        # 1. Decompose
        plan = await self.orchestrator.plan(task)

        # 2. Execute subtasks
        results = []
        for subtask in plan.subtasks:
            agent = self.agents[subtask.agent_type]
            result = await agent.execute(subtask)
            results.append(result)

        # 3. Synthesize
        solution = await self.orchestrator.synthesize(task, results)

        return solution
```

### 2. Base Agent

```python
"""Base agent class."""

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for specialized agents."""

    def __init__(self, llm, agent_name: str):
        self.llm = llm
        self.agent_name = agent_name
        self.stats = {"executions": 0, "cost": 0.0}

    @abstractmethod
    async def execute(self, subtask: SubTask) -> Dict:
        """Execute a subtask."""
        pass

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return self.stats
```

### 3. Architect Agent

```python
"""Architecture design agent."""

class ArchitectAgent(BaseAgent):
    """Specialized in software architecture."""

    SYSTEM_PROMPT = """You are a senior software architect.
    Design clean, maintainable architecture following SOLID principles.
    Focus on: modularity, scalability, testability."""

    def __init__(self, llm):
        super().__init__(llm, "architect")

    async def execute(self, subtask: SubTask) -> Dict:
        """Design architecture for given requirements."""
        prompt = f"{self.SYSTEM_PROMPT}\n\n{subtask.description}"

        response = await self.llm.ainvoke({"input": prompt})

        return {
            "agent": self.agent_name,
            "output": response.content,
            "subtask_id": subtask.description[:50],
        }
```

---

## 🔄 Patterns de Coordination

### Sequential Pattern (Pipeline)

```python
"""Sequential execution pattern."""

class SequentialPattern:
    """Execute agents in sequence."""

    async def execute(self, agents: List, task: Task) -> List:
        """Run agents one after another."""
        results = []
        current_input = task.context

        for agent in agents:
            result = await agent.execute(SubTask(
                agent_type=agent.agent_name,
                description=task.description,
                inputs=current_input,
            ))
            results.append(result)
            current_input = result  # Chain output → input

        return results

# Usage
pattern = SequentialPattern()
result = await pattern.execute(
    agents=[architect, coder, tester],
    task=task
)
```

### Parallel Pattern (Fan-out/Fan-in)

```python
"""Parallel execution pattern."""

class ParallelPattern:
    """Execute agents in parallel."""

    async def execute(self, agents: List, task: Task) -> List:
        """Run agents concurrently."""
        tasks = [
            agent.execute(SubTask(
                agent_type=agent.agent_name,
                description=task.description,
                inputs=task.context,
            ))
            for agent in agents
        ]

        results = await asyncio.gather(*tasks)
        return results

# Usage
pattern = ParallelPattern()
results = await pattern.execute(
    agents=[security_agent, performance_agent, quality_agent],
    task=task
)
```

### Debate Pattern (Consensus)

```python
"""Debate pattern for consensus."""

class DebatePattern:
    """Agents debate until consensus."""

    async def execute(
        self,
        agents: List,
        task: Task,
        max_rounds: int = 3
    ) -> Dict:
        """Run debate rounds."""
        proposals = [await agent.propose(task) for agent in agents]

        for round_num in range(max_rounds):
            # Each agent critiques others' proposals
            critiques = [
                await agent.critique(proposals)
                for agent in agents
            ]

            # Agents revise based on critiques
            proposals = [
                await agent.revise(proposal, critiques)
                for agent, proposal in zip(agents, proposals)
            ]

            # Check consensus
            if self._has_consensus(proposals):
                break

        # Select best proposal
        best = await self._select_best(proposals, agents)
        return best
```

---

## 📊 Métriques

### Collaboration Metrics

```python
ensemble.get_collaboration_metrics()
# {
#     "total_tasks": 150,
#     "avg_agents_per_task": 3.2,
#     "most_used_agent": "coder",
#     "best_pair": ("architect", "coder"),
#     "agent_specialization": {
#         "architect": {"precision": 0.93, "calls": 120},
#         "coder": {"precision": 0.88, "calls": 145},
#     }
# }
```

---

## 🚀 Exemples d'Utilisation

### Exemple 1: Build Feature

```python
ensemble = AgentEnsemble()

task = Task(
    description="Add OAuth authentication",
    context={"framework": "FastAPI", "db": "PostgreSQL"}
)

solution = await ensemble.solve(task)

print(f"Solution: {solution.final_output}")
print(f"Agents used: {solution.agents_used}")
print(f"Cost: ${solution.total_cost:.2f}")
```

### Exemple 2: Code Review Pipeline

```python
# Sequential: architect → reviewer → documenter
pattern = SequentialPattern()

results = await pattern.execute(
    agents=[
        ensemble.agents["architect"],
        ensemble.agents["reviewer"],
        ensemble.agents["documenter"],
    ],
    task=Task(description="Review auth module")
)
```

### Exemple 3: Parallel Analysis

```python
# Parallel: security + performance + quality
pattern = ParallelPattern()

analyses = await pattern.execute(
    agents=[security, performance, quality],
    task=Task(description="Analyze API endpoint")
)

# Merge analyses
combined = merge_analyses(analyses)
```

---

## 📈 Roadmap

### Phase 1: Core (1 semaine)
- [ ] AgentEnsemble base
- [ ] 3 agents de base (architect, coder, tester)
- [ ] Sequential pattern
- [ ] Basic orchestrator

### Phase 2: Patterns (1 semaine)
- [ ] Parallel pattern
- [ ] Debate pattern
- [ ] Router pattern
- [ ] Task decomposer

### Phase 3: Advanced (1 semaine)
- [ ] Dynamic agent selection
- [ ] Learning from history
- [ ] Cost optimization
- [ ] Métriques de collaboration

### Phase 4: Integration (1 semaine)
- [ ] CLI
- [ ] Web dashboard
- [ ] Git integration
- [ ] Documentation complète

---

## 🔧 Configuration

```yaml
# agent_ensemble_config.yaml
agents:
  architect:
    model: anthropic/claude-3-5-sonnet-20241022
    enabled: true

  coder:
    model: openai/gpt-4o
    enabled: true

  tester:
    model: gemini/gemini-2.0-flash-exp
    enabled: true

orchestrator:
  model: anthropic/claude-3-5-sonnet-20241022
  max_subtasks: 10
  parallel_execution: true

patterns:
  default: sequential
  allow_parallel: true
  allow_debate: false
  max_debate_rounds: 3
```

---

**Status**: 📝 Documentation Complete
**Estimated Development Time**: 3-4 weeks
**Priority**: ⭐⭐⭐⭐
