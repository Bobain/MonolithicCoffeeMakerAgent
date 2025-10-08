# Projet 4: Cost-Aware Smart Router

## 🎯 Vue d'ensemble

Un routeur intelligent qui **choisit dynamiquement le modèle optimal** pour chaque requête selon des contraintes de budget, latence, et qualité. Apprend des patterns historiques pour améliorer ses décisions.

### Objectifs
- Routing optimal basé sur contraintes (coût, latence, qualité)
- Apprentissage des patterns de tâches
- Budget management en temps réel
- Load balancing entre providers
- ROI direct mesurable

---

## 🏗️ Architecture

```
coffee_maker/smart_router/
├── __init__.py
├── router.py                    # Smart router principal
├── prediction/
│   ├── complexity_predictor.py  # ML pour prédire complexité
│   └── cost_predictor.py        # Prédiction de coût
├── optimization/
│   ├── optimizer.py             # Sélection optimale
│   └── budget_manager.py        # Gestion budgets
├── learning/
│   ├── pattern_learner.py       # Apprentissage patterns
│   └── model_ranker.py          # Ranking de modèles
└── monitoring/
    ├── metrics_collector.py     # Collecte métriques
    └── performance_tracker.py   # Tracking performances
```

---

## 📦 Composants Clés

### 1. SmartRouter (Core)

```python
"""Cost-aware smart router."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class RoutingConstraints:
    """Constraints for routing decision."""
    max_cost_usd: Optional[float] = None
    max_latency_sec: Optional[float] = None
    min_quality: Optional[float] = None
    preferred_providers: Optional[list] = None


@dataclass
class RoutingDecision:
    """Router decision."""
    provider: str
    model: str
    estimated_cost: float
    estimated_latency: float
    estimated_quality: float
    confidence: float
    reasoning: str


class SmartRouter:
    """Intelligent model router with cost awareness.

    Features:
    - Dynamic model selection based on task complexity
    - Budget management (hourly, daily, per-request)
    - Load balancing across providers
    - Learning from historical performance
    - Real-time pricing awareness

    Example:
        >>> router = SmartRouter("llm_metrics.db")
        >>>
        >>> # Route with constraints
        >>> provider, model = router.route(
        ...     task="Translate 'Hello' to French",
        ...     constraints=RoutingConstraints(
        ...         max_cost_usd=0.0001,
        ...         max_latency_sec=5,
        ...     )
        ... )
        >>> # Returns: ("openai", "gpt-4o-mini")
    """

    def __init__(
        self,
        db_path: str = "llm_metrics.db",
        enable_learning: bool = True,
    ):
        """Initialize smart router.

        Args:
            db_path: Path to metrics database
            enable_learning: Enable learning from history
        """
        self.db_path = db_path
        self.enable_learning = enable_learning

        # Components
        from coffee_maker.smart_router.prediction import ComplexityPredictor, CostPredictor
        from coffee_maker.smart_router.optimization import Optimizer, BudgetManager
        from coffee_maker.smart_router.learning import PatternLearner

        self.complexity_predictor = ComplexityPredictor()
        self.cost_predictor = CostPredictor()
        self.optimizer = Optimizer()
        self.budget_manager = BudgetManager(db_path)

        if enable_learning:
            self.pattern_learner = PatternLearner(db_path)
            self.pattern_learner.train()  # Train on historical data

        # Model catalog with pricing
        self.model_catalog = self._load_model_catalog()

        # Routing statistics
        self.stats = {
            "total_routes": 0,
            "routes_by_model": {},
            "avg_cost": 0.0,
            "budget_exceeded_count": 0,
        }

        logger = logging.getLogger(__name__)
        logger.info(f"SmartRouter initialized with learning={enable_learning}")

    def route(
        self,
        task: str,
        constraints: Optional[RoutingConstraints] = None,
    ) -> Tuple[str, str]:
        """Route task to optimal model.

        Args:
            task: Task description or prompt
            constraints: Optional routing constraints

        Returns:
            (provider, model) tuple

        Raises:
            ValueError: If no model satisfies constraints
        """
        if constraints is None:
            constraints = RoutingConstraints()

        # 1. Predict task complexity
        complexity = self.complexity_predictor.predict(task)

        # 2. Get historical performance for similar tasks
        similar_tasks_perf = self._query_similar_tasks(task, complexity)

        # 3. Check budget constraints
        if not self.budget_manager.can_proceed(constraints.max_cost_usd):
            # Budget exceeded → use cheapest model
            return self._get_cheapest_model()

        # 4. Optimize selection
        decision = self.optimizer.select_best(
            task=task,
            complexity=complexity,
            historical_performance=similar_tasks_perf,
            constraints=constraints,
            catalog=self.model_catalog,
        )

        # 5. Update statistics
        self._update_stats(decision)

        return decision.provider, decision.model

    def get_routing_stats(self) -> Dict:
        """Get routing statistics."""
        return self.stats

    def set_budget(
        self,
        hourly_limit: Optional[float] = None,
        daily_limit: Optional[float] = None,
        per_request_limit: Optional[float] = None,
    ):
        """Set budget limits.

        Args:
            hourly_limit: Max $ per hour
            daily_limit: Max $ per day
            per_request_limit: Max $ per request
        """
        self.budget_manager.set_limits(
            hourly=hourly_limit,
            daily=daily_limit,
            per_request=per_request_limit,
        )

    def update_pricing(self, provider: str, pricing: Dict):
        """Update pricing for a provider.

        Args:
            provider: Provider name
            pricing: Pricing dict {model: {input: X, output: Y}}
        """
        if provider not in self.model_catalog:
            self.model_catalog[provider] = {}

        self.model_catalog[provider].update(pricing)

    def _load_model_catalog(self) -> Dict:
        """Load model catalog with pricing."""
        return {
            "openai": {
                "gpt-4o": {
                    "input_price_per_1m": 2.50,
                    "output_price_per_1m": 10.00,
                    "avg_latency": 2.5,
                    "quality_score": 0.95,
                },
                "gpt-4o-mini": {
                    "input_price_per_1m": 0.15,
                    "output_price_per_1m": 0.60,
                    "avg_latency": 1.2,
                    "quality_score": 0.87,
                },
            },
            "anthropic": {
                "claude-3-5-sonnet-20241022": {
                    "input_price_per_1m": 3.00,
                    "output_price_per_1m": 15.00,
                    "avg_latency": 2.0,
                    "quality_score": 0.96,
                },
                "claude-3-5-haiku-20241022": {
                    "input_price_per_1m": 0.80,
                    "output_price_per_1m": 4.00,
                    "avg_latency": 0.9,
                    "quality_score": 0.89,
                },
            },
            "gemini": {
                "gemini-2.5-flash": {
                    "input_price_per_1m": 0.35,
                    "output_price_per_1m": 1.05,
                    "avg_latency": 1.0,
                    "quality_score": 0.84,
                },
                "gemini-2.5-flash-lite": {
                    "input_price_per_1m": 0.0,  # Free tier
                    "output_price_per_1m": 0.0,
                    "avg_latency": 0.8,
                    "quality_score": 0.78,
                },
            },
        }

    def _query_similar_tasks(self, task: str, complexity: float) -> Dict:
        """Query historical performance for similar tasks."""
        if not self.enable_learning:
            return {}

        return self.pattern_learner.get_similar_task_performance(
            task=task,
            complexity=complexity,
        )

    def _get_cheapest_model(self) -> Tuple[str, str]:
        """Get cheapest available model."""
        cheapest = ("gemini", "gemini-2.5-flash-lite")  # Free tier
        return cheapest

    def _update_stats(self, decision: RoutingDecision):
        """Update routing statistics."""
        self.stats["total_routes"] += 1

        model_key = f"{decision.provider}/{decision.model}"
        self.stats["routes_by_model"][model_key] = (
            self.stats["routes_by_model"].get(model_key, 0) + 1
        )
```

---

### 2. Complexity Predictor

```python
"""Task complexity prediction."""

from typing import Dict
import re

class ComplexityPredictor:
    """Predicts task complexity using ML or heuristics.

    Features extracted:
    - Task length (tokens)
    - Question marks (indicates questions)
    - Code blocks (technical complexity)
    - Technical terms (domain complexity)
    - Context requirements
    """

    def __init__(self):
        self.model = None  # TODO: Train ML model

    def predict(self, task: str) -> float:
        """Predict complexity score (0.0-1.0).

        Args:
            task: Task description

        Returns:
            Complexity score
        """
        # Simple heuristic for now
        score = 0.0

        # Length
        tokens = len(task.split())
        score += min(tokens / 1000, 0.3)

        # Questions
        questions = task.count('?')
        score += min(questions * 0.05, 0.2)

        # Code blocks
        code_blocks = len(re.findall(r'```[\s\S]*?```', task))
        score += min(code_blocks * 0.1, 0.3)

        # Technical terms
        technical_terms = ['algorithm', 'optimize', 'architecture', 'design', 'implement']
        term_count = sum(1 for term in technical_terms if term in task.lower())
        score += min(term_count * 0.05, 0.2)

        return min(score, 1.0)
```

---

### 3. Budget Manager

```python
"""Budget management."""

from datetime import datetime, timedelta
from typing import Optional

class BudgetManager:
    """Manages API usage budgets."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.limits = {
            "hourly": None,
            "daily": None,
            "per_request": None,
        }

    def set_limits(
        self,
        hourly: Optional[float],
        daily: Optional[float],
        per_request: Optional[float],
    ):
        """Set budget limits."""
        self.limits = {
            "hourly": hourly,
            "daily": daily,
            "per_request": per_request,
        }

    def can_proceed(self, estimated_cost: float) -> bool:
        """Check if request can proceed within budget.

        Args:
            estimated_cost: Estimated cost for request

        Returns:
            True if within budget
        """
        # Check per-request limit
        if self.limits["per_request"] and estimated_cost > self.limits["per_request"]:
            return False

        # Check hourly limit
        if self.limits["hourly"]:
            hourly_usage = self._get_usage(timedelta(hours=1))
            if hourly_usage + estimated_cost > self.limits["hourly"]:
                return False

        # Check daily limit
        if self.limits["daily"]:
            daily_usage = self._get_usage(timedelta(days=1))
            if daily_usage + estimated_cost > self.limits["daily"]:
                return False

        return True

    def _get_usage(self, period: timedelta) -> float:
        """Get total usage in period."""
        # Query database for costs in period
        # TODO: Implement
        return 0.0
```

---

## 🚀 Exemples d'Utilisation

### Exemple 1: Basic Routing

```python
router = SmartRouter()

# Simple task → cheap model
provider, model = router.route(
    task="Translate 'Hello' to French",
    constraints=RoutingConstraints(max_cost_usd=0.0001),
)
# Returns: ("openai", "gpt-4o-mini")

# Complex task → powerful model
provider, model = router.route(
    task="Design a distributed cache system with CAP theorem considerations",
    constraints=RoutingConstraints(min_quality=0.95),
)
# Returns: ("anthropic", "claude-3-5-sonnet-20241022")
```

### Exemple 2: Budget Management

```python
router = SmartRouter()

# Set budgets
router.set_budget(
    hourly_limit=1.00,  # $1/hour
    daily_limit=10.00,  # $10/day
    per_request_limit=0.05,  # $0.05/request
)

# Router automatically switches to cheaper models when approaching limits
```

### Exemple 3: Load Balancing

```python
router = SmartRouter()

# Configure load balancing
router.set_load_balancing(
    strategy="round_robin",
    providers=["openai", "anthropic", "gemini"],
)

# Requests distributed across providers
```

---

## 📊 Métriques

```python
stats = router.get_routing_stats()
# {
#     "total_routes": 10000,
#     "routes_by_model": {
#         "openai/gpt-4o-mini": 6500,
#         "anthropic/claude-3-5-haiku": 2000,
#         "gemini/gemini-2.5-flash": 1500,
#     },
#     "avg_cost_per_request": 0.0008,
#     "total_cost": 8.00,
#     "cost_savings_vs_always_gpt4": 17.00,  # $25 → $8
#     "quality_maintained": 0.89,
# }
```

---

## 📈 Roadmap

### Phase 1: Core (1 semaine)
- [ ] SmartRouter base
- [ ] Complexity predictor (heuristics)
- [ ] Budget manager
- [ ] Basic optimizer

### Phase 2: Learning (1 semaine)
- [ ] Pattern learner
- [ ] ML-based complexity predictor
- [ ] Historical performance tracking
- [ ] Model ranking

### Phase 3: Advanced (1 semaine)
- [ ] Load balancing
- [ ] Real-time pricing updates
- [ ] A/B testing of routing strategies
- [ ] Multi-objective optimization

### Phase 4: Production (1 semaine)
- [ ] Monitoring dashboard
- [ ] Alerting
- [ ] Cost reports
- [ ] Integration tests

---

**Status**: 📝 Documentation Complete
**Estimated Development Time**: 3-4 weeks
**Priority**: ⭐⭐⭐⭐
