# Projet 2: Self-Improving Prompt Lab

## 🎯 Vue d'ensemble

### Résumé
Un système d'**optimisation automatique de prompts** qui teste des variantes, mesure leur performance, et converge vers les meilleurs prompts pour chaque tâche. Le système s'améliore continuellement grâce à l'apprentissage des données de production.

### Objectifs
- A/B testing automatisé de prompts
- Évolution génétique de prompts (mutations, sélection)
- Métriques objectives (qualité, coût, latence)
- Apprentissage continu en production
- Convergence vers prompts optimaux

### Bénéfices
- **ROI direct** - Réduction coûts (20-50%) + amélioration qualité
- **Data-driven** - Décisions basées sur métriques réelles
- **Self-improving** - S'améliore avec le temps
- **Scientifique** - Approche rigoureuse du prompt engineering

---

## 🏗️ Architecture

### Structure du module

```
coffee_maker/prompt_lab/
├── __init__.py
├── lab.py                          # PromptLab principal
├── experiment/
│   ├── __init__.py
│   ├── runner.py                   # Exécution expériences
│   ├── test_case.py                # Cas de test
│   └── evaluator.py                # Évaluation qualité
├── evolution/
│   ├── __init__.py
│   ├── mutator.py                  # Mutations de prompts
│   ├── selector.py                 # Sélection des meilleurs
│   └── generator.py                # Génération variantes
├── optimization/
│   ├── __init__.py
│   ├── multi_objective.py          # Optimisation multi-objectifs
│   └── bayesian_optimizer.py      # Optimisation bayésienne
├── production/
│   ├── __init__.py
│   ├── continuous_learner.py      # Apprentissage continu
│   └── deployment_manager.py      # Gestion déploiements
└── storage/
    ├── __init__.py
    ├── variant_store.py            # Stockage variantes
    └── execution_store.py          # Stockage exécutions

scripts/
├── run_experiment.py               # CLI expériences
├── evolve_prompts.py               # Évolution automatique
└── analyze_results.py              # Analyse résultats

tests/
├── unit/test_prompt_lab.py
├── integration/test_experiments.py
└── fixtures/
    └── test_prompts.yaml           # Prompts de test
```

### Diagramme de flux

```
┌─────────────────────────────────────────────────────────┐
│  User: Define Task + Initial Prompts + Test Cases      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────────────┐
         │  PromptLab.register_variants() │
         └────────────────┬───────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │  PromptLab.run_experiment()        │
         │  - Test each variant              │
         │  - On multiple test cases         │
         │  - With multiple models           │
         │  - Repeat for statistical         │
         │    significance                   │
         └────────────────┬───────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
    ┌──────────┐                  ┌──────────────┐
    │ Variant A│                  │  Variant B   │
    │ + GPT-4  │                  │  + Claude    │
    └────┬─────┘                  └──────┬───────┘
         │                               │
         │  Test Case 1                  │  Test Case 1
         │  Test Case 2                  │  Test Case 2
         │  ...                          │  ...
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Evaluator.evaluate()      │
            │  - Quality score (LLM)     │
            │  - Cost tracking           │
            │  - Latency measurement     │
            │  - Success rate            │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Statistical Analysis      │
            │  - Mean + Std Dev          │
            │  - Confidence intervals    │
            │  - Significance tests      │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Report Generation         │
            │  - Best combination        │
            │  - Comparison table        │
            │  - Recommendations         │
            └────────────┬───────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────┐              ┌──────────────────┐
│ Deploy Winner │              │ Continue Evolution│
│ to Production │              │ (Mutation Loop)  │
└───────────────┘              └──────────────────┘
```

---

## 📦 Composants Détaillés

### 1. PromptLab (Core)

**Fichier**: `coffee_maker/prompt_lab/lab.py`

```python
"""Main Prompt Lab orchestrator."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

from coffee_maker.langchain_observe.analytics.db_schema import Base
from coffee_maker.langchain_observe.builder import LLMBuilder
from coffee_maker.prompt_lab.experiment import ExperimentRunner, TestCase, Evaluator
from coffee_maker.prompt_lab.evolution import PromptMutator, PromptSelector
from coffee_maker.prompt_lab.storage import VariantStore, ExecutionStore

logger = logging.getLogger(__name__)


@dataclass
class PromptVariant:
    """A prompt variant to test."""

    prompt_id: str
    variant_name: str
    template: str
    variables: List[str]
    description: str = ""
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True
    is_default: bool = False
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of a prompt execution."""

    execution_id: str
    prompt_id: str
    test_case_id: str
    model: str

    # Timing
    executed_at: str
    latency_seconds: float

    # Tokens & Cost
    input_tokens: int
    output_tokens: int
    cost_usd: float

    # Quality
    success: bool
    quality_score: float  # 0.0-1.0
    user_feedback: Optional[float] = None

    # Output
    output_text: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class ExperimentReport:
    """Report from a prompt experiment."""

    experiment_id: str
    task_name: str
    variants_tested: List[str]
    models_tested: List[str]
    test_cases_count: int
    iterations: int

    # Results per variant
    results: Dict[str, Dict]  # {variant_name: {metrics}}

    # Best combination
    best_variant: str
    best_model: str
    best_quality: float
    best_cost: float
    best_latency: float

    # Statistics
    confidence_level: float
    significant: bool

    # Timestamp
    started_at: str
    completed_at: str
    duration_seconds: float


class PromptLab:
    """Experimental prompt optimization laboratory.

    This class provides tools for:
    - Registering prompt variants
    - Running A/B tests
    - Evolutionary prompt optimization
    - Continuous learning in production
    - Multi-objective optimization

    Example:
        >>> lab = PromptLab(task_name="code_summarization")
        >>>
        >>> # Register variants
        >>> lab.register_prompt_variant(
        ...     variant_name="v1_simple",
        ...     template="Summarize this code: {code}",
        ... )
        >>>
        >>> # Run experiment
        >>> report = await lab.run_experiment(
        ...     test_cases=[...],
        ...     variants=["v1_simple", "v2_structured"],
        ...     models=["gpt-4o-mini", "claude-3-5-haiku"],
        ... )
        >>>
        >>> print(report.best_variant)
    """

    def __init__(
        self,
        task_name: str,
        db_path: str = "llm_metrics.db",
        cost_calculator = None,
        langfuse_client = None,
    ):
        """Initialize Prompt Lab.

        Args:
            task_name: Name of the task (e.g., "code_summarization")
            db_path: Path to SQLite database
            cost_calculator: Optional cost calculator
            langfuse_client: Optional Langfuse client
        """
        self.task_name = task_name
        self.db_path = db_path
        self.cost_calculator = cost_calculator
        self.langfuse_client = langfuse_client

        # Storage
        self.variant_store = VariantStore(db_path)
        self.execution_store = ExecutionStore(db_path)

        # Components
        self.experiment_runner = ExperimentRunner(self)
        self.evaluator = Evaluator()
        self.mutator = PromptMutator()
        self.selector = PromptSelector()

        # LLM cache
        self._llm_cache: Dict[str, any] = {}

        logger.info(f"Initialized PromptLab for task: {task_name}")

    def register_prompt_variant(
        self,
        variant_name: str,
        template: str,
        description: str = "",
        variables: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Register a new prompt variant.

        Args:
            variant_name: Unique name for variant
            template: Prompt template with {variables}
            description: Human-readable description
            variables: List of variable names (auto-detected if None)
            tags: Optional tags for categorization

        Returns:
            prompt_id
        """
        # Auto-detect variables if not provided
        if variables is None:
            import re
            variables = re.findall(r'\{(\w+)\}', template)

        # Create variant
        prompt_id = f"{self.task_name}_{variant_name}_{uuid.uuid4().hex[:8]}"

        variant = PromptVariant(
            prompt_id=prompt_id,
            variant_name=variant_name,
            template=template,
            variables=variables,
            description=description,
            tags=tags or [],
        )

        # Store
        self.variant_store.save(variant)

        logger.info(f"Registered prompt variant: {variant_name} (ID: {prompt_id})")

        return prompt_id

    async def run_experiment(
        self,
        test_cases: List[TestCase],
        variants: List[str],
        models: List[str],
        n_iterations: int = 10,
        evaluation_criteria: Optional[List[str]] = None,
    ) -> ExperimentReport:
        """Run A/B test experiment.

        Args:
            test_cases: List of test cases to run
            variants: List of variant names to test
            models: List of model names to test
            n_iterations: Repetitions for statistical significance
            evaluation_criteria: Criteria for quality evaluation

        Returns:
            Experiment report with results
        """
        experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now().isoformat()

        logger.info(
            f"Starting experiment {experiment_id}: "
            f"{len(variants)} variants × {len(models)} models × "
            f"{len(test_cases)} test cases × {n_iterations} iterations"
        )

        # Run experiment
        results = await self.experiment_runner.run(
            experiment_id=experiment_id,
            test_cases=test_cases,
            variants=variants,
            models=models,
            n_iterations=n_iterations,
            evaluation_criteria=evaluation_criteria or ["accuracy", "relevance"],
        )

        # Analyze results
        best_combo = self._find_best_combination(results)

        completed_at = datetime.now().isoformat()
        duration = (
            datetime.fromisoformat(completed_at) -
            datetime.fromisoformat(started_at)
        ).total_seconds()

        # Create report
        report = ExperimentReport(
            experiment_id=experiment_id,
            task_name=self.task_name,
            variants_tested=variants,
            models_tested=models,
            test_cases_count=len(test_cases),
            iterations=n_iterations,
            results=results,
            best_variant=best_combo["variant"],
            best_model=best_combo["model"],
            best_quality=best_combo["quality"],
            best_cost=best_combo["cost"],
            best_latency=best_combo["latency"],
            confidence_level=best_combo["confidence"],
            significant=best_combo["significant"],
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
        )

        logger.info(
            f"Experiment {experiment_id} complete: "
            f"Best = {report.best_variant} + {report.best_model} "
            f"(quality: {report.best_quality:.3f}, cost: ${report.best_cost:.4f})"
        )

        return report

    async def evolve_prompts(
        self,
        seed_variant: str,
        test_cases: List[TestCase],
        generations: int = 5,
        population_size: int = 10,
        mutation_strategies: Optional[List[str]] = None,
    ) -> List[str]:
        """Evolve prompts using genetic algorithm.

        Args:
            seed_variant: Starting prompt variant
            test_cases: Test cases for evaluation
            generations: Number of generations to evolve
            population_size: Population size per generation
            mutation_strategies: Mutation strategies to use

        Returns:
            List of best variant IDs
        """
        if mutation_strategies is None:
            mutation_strategies = [
                "rephrase",
                "add_structure",
                "add_examples",
                "change_persona",
                "simplify",
                "elaborate",
            ]

        logger.info(
            f"Starting prompt evolution: {generations} generations, "
            f"population {population_size}"
        )

        # Get seed prompt
        seed_prompt = self.variant_store.get(seed_variant)

        # Initial population
        population = [seed_prompt]

        for gen in range(generations):
            logger.info(f"Generation {gen + 1}/{generations}")

            # Mutate current population
            offspring = []
            for parent in population:
                for strategy in mutation_strategies:
                    mutant = await self.mutator.mutate(
                        parent.template,
                        strategy=strategy,
                    )

                    # Register mutant
                    variant_name = f"{parent.variant_name}_gen{gen}_{strategy}"
                    prompt_id = self.register_prompt_variant(
                        variant_name=variant_name,
                        template=mutant,
                        description=f"Mutated from {parent.variant_name} using {strategy}",
                        tags=["evolved", f"gen{gen}", strategy],
                    )

                    offspring.append(self.variant_store.get(prompt_id))

            # Evaluate offspring
            variant_names = [v.variant_name for v in offspring]
            report = await self.run_experiment(
                test_cases=test_cases,
                variants=variant_names,
                models=["gpt-4o-mini"],  # Use cheap model for evolution
                n_iterations=3,
            )

            # Select best performers
            population = self.selector.select_best(
                offspring,
                report.results,
                k=population_size,
            )

            logger.info(f"Generation {gen + 1} complete: selected {len(population)} best")

        # Return IDs of final population
        return [p.prompt_id for p in population]

    def optimize(
        self,
        objectives: Dict[str, Tuple[float, str]],
        constraints: Optional[Dict[str, str]] = None,
        test_cases: Optional[List[TestCase]] = None,
    ):
        """Multi-objective optimization.

        Args:
            objectives: {metric: (weight, direction)}
                e.g., {"quality": (1.0, "maximize"), "cost": (0.5, "minimize")}
            constraints: {metric: constraint_expression}
                e.g., {"quality": ">= 0.85", "cost": "<= $0.005"}
            test_cases: Test cases for evaluation

        Example:
            >>> lab.optimize(
            ...     objectives={
            ...         "quality": (1.0, "maximize"),
            ...         "cost": (0.5, "minimize"),
            ...         "latency": (0.3, "minimize"),
            ...     },
            ...     constraints={
            ...         "quality": ">= 0.85",
            ...         "cost": "<= $0.005",
            ...     }
            ... )
        """
        from coffee_maker.prompt_lab.optimization import MultiObjectiveOptimizer

        optimizer = MultiObjectiveOptimizer(self)

        best_variant = optimizer.optimize(
            objectives=objectives,
            constraints=constraints,
            test_cases=test_cases,
        )

        return best_variant

    def enable_production_mode(
        self,
        baseline_variant: str,
        exploration_rate: float = 0.1,
        evaluation_window: str = "1 day",
        auto_promote_threshold: float = 0.95,
    ):
        """Enable continuous learning in production.

        Args:
            baseline_variant: Current production variant
            exploration_rate: % of requests to test new variants (0.0-1.0)
            evaluation_window: Time window for evaluation ("1 hour", "1 day")
            auto_promote_threshold: Auto-promote if 95% CI > baseline

        Example:
            >>> lab.enable_production_mode(
            ...     baseline_variant="v2_structured",
            ...     exploration_rate=0.1,  # 10% exploration
            ...     auto_promote_threshold=0.95,
            ... )
        """
        from coffee_maker.prompt_lab.production import ContinuousLearner

        learner = ContinuousLearner(
            lab=self,
            baseline_variant=baseline_variant,
            exploration_rate=exploration_rate,
            evaluation_window=evaluation_window,
            auto_promote_threshold=auto_promote_threshold,
        )

        learner.start()

        logger.info(
            f"Production mode enabled: baseline={baseline_variant}, "
            f"exploration={exploration_rate:.0%}"
        )

    def deploy_winner(self, variant_name: str, model: str):
        """Deploy a variant as the default.

        Args:
            variant_name: Variant to deploy
            model: Model to use
        """
        from coffee_maker.prompt_lab.production import DeploymentManager

        manager = DeploymentManager(self.variant_store)
        manager.deploy(variant_name, model)

        logger.info(f"Deployed {variant_name} with {model} as default")

    def get_llm(self, provider: str, model: str):
        """Get or create LLM instance."""
        key = f"{provider}/{model}"

        if key not in self._llm_cache:
            builder = LLMBuilder()
            llm = (
                builder
                .with_primary(provider, model)
                .with_fallback("gemini", "gemini-2.5-flash")
                .with_cost_tracking(self.cost_calculator, self.langfuse_client)
                .build()
            )
            self._llm_cache[key] = llm

        return self._llm_cache[key]

    def _find_best_combination(self, results: Dict) -> Dict:
        """Find best variant + model combination."""
        import numpy as np

        best = {
            "variant": None,
            "model": None,
            "quality": 0.0,
            "cost": float('inf'),
            "latency": float('inf'),
            "confidence": 0.0,
            "significant": False,
        }

        for variant_name, variant_results in results.items():
            for model_name, metrics in variant_results.items():
                # Weighted score
                score = (
                    metrics["mean_quality"] * 1.0 +
                    (1.0 / max(metrics["mean_cost"], 0.0001)) * 0.3 +
                    (1.0 / max(metrics["mean_latency"], 0.1)) * 0.2
                )

                if score > (
                    best["quality"] * 1.0 +
                    (1.0 / max(best["cost"], 0.0001)) * 0.3 +
                    (1.0 / max(best["latency"], 0.1)) * 0.2
                ):
                    best = {
                        "variant": variant_name,
                        "model": model_name,
                        "quality": metrics["mean_quality"],
                        "cost": metrics["mean_cost"],
                        "latency": metrics["mean_latency"],
                        "confidence": metrics.get("confidence_level", 0.95),
                        "significant": metrics.get("significant", True),
                    }

        return best
```

---

### 2. Experiment Runner

**Fichier**: `coffee_maker/prompt_lab/experiment/runner.py`

```python
"""Experiment execution engine."""

import asyncio
import logging
from typing import Dict, List
import time

from coffee_maker.prompt_lab.experiment.test_case import TestCase
from coffee_maker.prompt_lab.experiment.evaluator import Evaluator

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Runs experiments with statistical rigor."""

    def __init__(self, lab):
        """Initialize runner.

        Args:
            lab: PromptLab instance
        """
        self.lab = lab
        self.evaluator = Evaluator()

    async def run(
        self,
        experiment_id: str,
        test_cases: List[TestCase],
        variants: List[str],
        models: List[str],
        n_iterations: int,
        evaluation_criteria: List[str],
    ) -> Dict:
        """Run complete experiment.

        Returns:
            Results dictionary: {variant_name: {model_name: metrics}}
        """
        results = {}

        # For each variant
        for variant_name in variants:
            variant = self.lab.variant_store.get(variant_name)
            results[variant_name] = {}

            # For each model
            for model in models:
                logger.info(f"Testing {variant_name} + {model}")

                # Run multiple iterations
                execution_results = []

                for iteration in range(n_iterations):
                    # For each test case
                    for test_case in test_cases:
                        result = await self._execute_single_test(
                            experiment_id=experiment_id,
                            variant=variant,
                            model=model,
                            test_case=test_case,
                            evaluation_criteria=evaluation_criteria,
                        )

                        execution_results.append(result)

                # Aggregate results
                metrics = self._aggregate_results(execution_results)
                results[variant_name][model] = metrics

        return results

    async def _execute_single_test(
        self,
        experiment_id: str,
        variant,
        model: str,
        test_case: TestCase,
        evaluation_criteria: List[str],
    ):
        """Execute single test case."""
        # Build prompt from template
        prompt = variant.template.format(**test_case.inputs)

        # Get LLM
        provider, model_name = model.split("/") if "/" in model else ("openai", model)
        llm = self.lab.get_llm(provider, model_name)

        # Execute
        start_time = time.time()

        try:
            response = await llm.ainvoke({"input": prompt})
            latency = time.time() - start_time

            output_text = response.content

            # Extract tokens
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                input_tokens = getattr(usage, "input_tokens", 0)
                output_tokens = getattr(usage, "output_tokens", 0)

            # Calculate cost
            cost = 0.0
            if self.lab.cost_calculator:
                cost_info = self.lab.cost_calculator.calculate_cost(
                    f"{provider}/{model_name}",
                    input_tokens,
                    output_tokens
                )
                cost = cost_info["total_cost"]

            # Evaluate quality
            quality_score = await self.evaluator.evaluate(
                output=output_text,
                expected_output=test_case.expected_output,
                criteria=evaluation_criteria,
                llm=llm,
            )

            success = quality_score >= test_case.min_quality_threshold

            # Store execution
            from coffee_maker.prompt_lab.multi_model_reviewer import ExecutionResult
            import uuid
            from datetime import datetime

            execution = ExecutionResult(
                execution_id=f"exec_{uuid.uuid4().hex[:8]}",
                prompt_id=variant.prompt_id,
                test_case_id=test_case.test_case_id,
                model=model,
                executed_at=datetime.now().isoformat(),
                latency_seconds=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                success=success,
                quality_score=quality_score,
                output_text=output_text,
                metadata={
                    "experiment_id": experiment_id,
                    "variant_name": variant.variant_name,
                },
            )

            self.lab.execution_store.save(execution)

            return execution

        except Exception as e:
            logger.error(f"Execution failed: {e}")

            # Return failed execution
            from coffee_maker.prompt_lab.multi_model_reviewer import ExecutionResult
            import uuid
            from datetime import datetime

            return ExecutionResult(
                execution_id=f"exec_{uuid.uuid4().hex[:8]}",
                prompt_id=variant.prompt_id,
                test_case_id=test_case.test_case_id,
                model=model,
                executed_at=datetime.now().isoformat(),
                latency_seconds=time.time() - start_time,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                success=False,
                quality_score=0.0,
                output_text="",
                metadata={"error": str(e)},
            )

    def _aggregate_results(self, execution_results: List) -> Dict:
        """Aggregate execution results into metrics."""
        import numpy as np
        from scipy import stats

        qualities = [r.quality_score for r in execution_results if r.success]
        costs = [r.cost_usd for r in execution_results]
        latencies = [r.latency_seconds for r in execution_results]

        if not qualities:
            return {
                "mean_quality": 0.0,
                "std_quality": 0.0,
                "mean_cost": np.mean(costs) if costs else 0.0,
                "mean_latency": np.mean(latencies) if latencies else 0.0,
                "success_rate": 0.0,
                "count": len(execution_results),
            }

        # Calculate statistics
        mean_quality = np.mean(qualities)
        std_quality = np.std(qualities)
        mean_cost = np.mean(costs)
        mean_latency = np.mean(latencies)
        success_rate = len(qualities) / len(execution_results)

        # Confidence interval (95%)
        if len(qualities) > 1:
            ci = stats.t.interval(
                0.95,
                len(qualities) - 1,
                loc=mean_quality,
                scale=std_quality / np.sqrt(len(qualities))
            )
            ci_lower, ci_upper = ci
        else:
            ci_lower = ci_upper = mean_quality

        return {
            "mean_quality": mean_quality,
            "std_quality": std_quality,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "mean_cost": mean_cost,
            "mean_latency": mean_latency,
            "success_rate": success_rate,
            "count": len(execution_results),
            "confidence_level": 0.95,
            "significant": (ci_upper - ci_lower) < 0.1,  # Tight interval
        }
```

---

### 3. Prompt Evolution

**Fichier**: `coffee_maker/prompt_lab/evolution/mutator.py`

```python
"""Prompt mutation engine."""

import logging
from typing import List

logger = logging.getLogger(__name__)


class PromptMutator:
    """Mutates prompts using various strategies.

    Mutation strategies:
    - rephrase: Rephrase the prompt
    - add_structure: Add structure (numbered lists, sections)
    - add_examples: Add few-shot examples
    - change_persona: Change the persona/role
    - simplify: Make more concise
    - elaborate: Add more detail
    - add_constraints: Add explicit constraints
    - change_format: Change output format
    """

    MUTATION_PROMPTS = {
        "rephrase": """Rephrase this prompt to be clearer while keeping the same intent:

Original prompt:
{prompt}

Rephrased prompt:""",

        "add_structure": """Add structure to this prompt using numbered lists or sections:

Original prompt:
{prompt}

Structured prompt:""",

        "add_examples": """Add 2-3 concrete examples to this prompt:

Original prompt:
{prompt}

Prompt with examples:""",

        "change_persona": """Rewrite this prompt with a different expert persona (e.g., senior engineer, architect, teacher):

Original prompt:
{prompt}

Prompt with new persona:""",

        "simplify": """Simplify this prompt to be more concise while keeping core intent:

Original prompt:
{prompt}

Simplified prompt:""",

        "elaborate": """Elaborate on this prompt with more detail and context:

Original prompt:
{prompt}

Elaborated prompt:""",
    }

    def __init__(self, mutator_llm=None):
        """Initialize mutator.

        Args:
            mutator_llm: LLM to use for mutations (default: gpt-4o-mini)
        """
        self.mutator_llm = mutator_llm

        if self.mutator_llm is None:
            from coffee_maker.langchain_observe.builder import LLMBuilder

            self.mutator_llm = (
                LLMBuilder()
                .with_primary("openai", "gpt-4o-mini")
                .with_fallback("gemini", "gemini-2.5-flash")
                .build()
            )

    async def mutate(
        self,
        prompt: str,
        strategy: str,
    ) -> str:
        """Mutate a prompt using specified strategy.

        Args:
            prompt: Original prompt
            strategy: Mutation strategy name

        Returns:
            Mutated prompt
        """
        if strategy not in self.MUTATION_PROMPTS:
            raise ValueError(f"Unknown mutation strategy: {strategy}")

        mutation_prompt = self.MUTATION_PROMPTS[strategy].format(prompt=prompt)

        try:
            response = await self.mutator_llm.ainvoke({"input": mutation_prompt})
            mutated = response.content.strip()

            logger.info(f"Mutated prompt using '{strategy}' strategy")

            return mutated

        except Exception as e:
            logger.error(f"Mutation failed: {e}")
            return prompt  # Return original on failure
```

---

## 🚀 Guide d'Utilisation

### Installation

```bash
poetry install
```

### Exemple Complet

```python
import asyncio
from coffee_maker.prompt_lab import PromptLab
from coffee_maker.prompt_lab.experiment import TestCase

async def main():
    # Créer le lab
    lab = PromptLab(task_name="code_summarization")

    # Enregistrer des variantes
    lab.register_prompt_variant(
        variant_name="v1_simple",
        template="Summarize this code: {code}",
        description="Baseline simple prompt"
    )

    lab.register_prompt_variant(
        variant_name="v2_structured",
        template="""Analyze this code and provide:
1. Purpose: What it does
2. Key logic: Main algorithm
3. Edge cases: Important conditions

Code:
{code}""",
        description="Structured output prompt"
    )

    # Définir cas de test
    test_cases = [
        TestCase(
            test_case_id="tc1",
            inputs={"code": "def factorial(n):\n    return 1 if n == 0 else n * factorial(n-1)"},
            expected_output="Recursive factorial function",
            min_quality_threshold=0.7,
        ),
        # ... plus de cas
    ]

    # Lancer l'expérience
    report = await lab.run_experiment(
        test_cases=test_cases,
        variants=["v1_simple", "v2_structured"],
        models=["openai/gpt-4o-mini", "anthropic/claude-3-5-haiku"],
        n_iterations=10,
    )

    # Afficher résultats
    print(f"Best: {report.best_variant} + {report.best_model}")
    print(f"Quality: {report.best_quality:.3f}")
    print(f"Cost: ${report.best_cost:.4f}")

asyncio.run(main())
```

---

## 📊 Schéma SQLite

```sql
-- Variantes de prompts
CREATE TABLE prompt_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id TEXT UNIQUE NOT NULL,
    prompt_name VARCHAR(255) NOT NULL,
    variant_name VARCHAR(100),
    version INTEGER,
    prompt_template TEXT NOT NULL,
    prompt_variables TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    description TEXT,
    tags TEXT,  -- JSON
    is_active BOOLEAN DEFAULT 1,
    is_default BOOLEAN DEFAULT 0
);

-- Exécutions
CREATE TABLE prompt_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE NOT NULL,
    prompt_id TEXT NOT NULL,
    test_case_id TEXT,
    trace_id TEXT,
    provider VARCHAR(50),
    model VARCHAR(255),
    executed_at TIMESTAMP NOT NULL,
    latency_seconds REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL,
    success BOOLEAN,
    quality_score REAL,
    user_feedback REAL,
    output_text TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (prompt_id) REFERENCES prompt_variants(prompt_id)
);

CREATE INDEX idx_prompt_performance
    ON prompt_executions(prompt_id, success, executed_at);
```

---

## 📈 Roadmap

### Phase 1: Core (1 semaine)
- [x] Architecture
- [ ] PromptLab core
- [ ] ExperimentRunner
- [ ] Basic evaluator
- [ ] SQLite storage

### Phase 2: Evolution (1 semaine)
- [ ] PromptMutator
- [ ] Evolutionary loop
- [ ] Selector
- [ ] CLI pour évolution

### Phase 3: Production (1 semaine)
- [ ] Continuous learner
- [ ] A/B testing en prod
- [ ] Auto-promotion
- [ ] Monitoring

### Phase 4: Advanced (1 semaine)
- [ ] Multi-objective optimization
- [ ] Bayesian optimization
- [ ] Dashboard web
- [ ] Analytics avancées

---

**Status**: 📝 Documentation Complete - Ready for Implementation
**Estimated Development Time**: 3-4 weeks
**Priority**: ⭐⭐⭐⭐⭐ (Highest)
