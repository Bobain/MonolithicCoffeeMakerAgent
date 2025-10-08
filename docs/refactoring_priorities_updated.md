# Refactoring Priorities - Post-Scheduling Implementation

## Date
2025-10-08

## Contexte

Suite à l'implémentation du **ProactiveRateLimitScheduler** et de la **gestion d'erreurs réactive avec règle des 90s**, réévaluons les priorités de refactoring.

## Ce Qui a Déjà Été Fait ✅

### 1. Strategy Pattern pour Scheduling (FAIT)

✅ **SchedulingStrategy** avec:
- `ProactiveRateLimitScheduler` (proactif: N-2, 60/RPM)
- Gestion d'erreurs réactive (backoff exponentiel)
- Règle des 90 secondes
- Interface abstraite extensible

✅ **ScheduledLLM / ScheduledChatModel**:
- Wrappers qui ajoutent scheduling à n'importe quel LLM
- Gestion automatique des erreurs
- Compatible avec toute l'architecture existante

✅ **`get_scheduled_llm()`**:
- Fonction dédiée pour créer des LLMs avec scheduling
- Séparation claire entre LLM brut (`get_llm`) et LLM schedulé

**Impact:**
- Code **déjà plus modulaire**
- Scheduling **testable indépendamment**
- **Pas de breaking changes**

### 2. Séparation des Responsabilités Partiellement Résolue

Avant, `AutoPickerLLM` faisait tout:
- ❌ Rate limiting logic (800 lignes)
- ❌ Retry logic
- ❌ Backoff calculations
- ✅ Model invocation
- ✅ Fallback selection
- ✅ Cost tracking
- ✅ Context management

Maintenant:
- ✅ **Rate limiting** → délégué à `SchedulingStrategy`
- ✅ **Retry logic** → délégué à `SchedulingStrategy.should_retry_after_error()`
- ✅ **Backoff** → délégué à `SchedulingStrategy`
- ✅ **Scheduling** → délégué à `ScheduledLLM`

`AutoPickerLLM` est **déjà beaucoup plus simple** (reste surtout fallback + orchestration).

## Tâches Restantes - Par Priorité

### 🔴 PRIORITÉ HAUTE: Tâches Critiques

#### 1. **Simplifier AutoPickerLLM Davantage**
**Effort:** 3-4 jours
**Impact:** ⭐⭐⭐⭐⭐

Maintenant que le scheduling est extrait, `AutoPickerLLM` peut être simplifié:

```python
class AutoPickerLLM(BaseLLM):
    """Orchestrateur de fallback uniquement.

    Le scheduling est géré par ScheduledLLM.
    AutoPickerLLM gère juste: primary → fallbacks.
    """

    def __init__(
        self,
        primary_llm: ScheduledLLM,      # Déjà wrapped avec scheduling
        fallback_llms: List[ScheduledLLM],  # Idem
        cost_calculator: Optional[CostCalculator] = None,
        langfuse_client: Optional[Any] = None
    ):
        # BEAUCOUP PLUS SIMPLE: juste fallback logic
        self.primary = primary_llm
        self.fallbacks = fallback_llms
        self.cost_calc = cost_calculator
        self.langfuse = langfuse_client

    def invoke(self, input_data):
        """Simple orchestration."""
        # 1. Essaye primary (scheduling géré par ScheduledLLM)
        try:
            return self._invoke_with_cost_tracking(self.primary, input_data)
        except Exception as e:
            if not self._should_fallback(e):
                raise

        # 2. Essaye fallbacks
        for fallback in self.fallbacks:
            try:
                return self._invoke_with_cost_tracking(fallback, input_data)
            except:
                continue

        # 3. Tous échoués
        raise RuntimeError("All models exhausted")
```

**Bénéfices:**
- AutoPickerLLM passe de **780 lignes** à ~**150 lignes**
- Plus besoin de `rate_tracker`, `max_retries`, `backoff_base`, etc.
- Juste: orchestration + cost tracking + fallback
- **Une seule responsabilité claire**

**Blocages potentiels:**
- Besoin de s'assurer que tous les call sites passent des `ScheduledLLM`
- Migration des tests existants

---

#### 2. **Extraire Context Management Strategy**
**Effort:** 2-3 jours
**Impact:** ⭐⭐⭐⭐

Le context checking est encore dans `AutoPickerLLM`:

```python
# Actuellement dans AutoPickerLLM._try_invoke_model()
if self.enable_context_fallback:
    fits, estimated_tokens, max_context = self._check_context_length(...)
    if not fits:
        logger.info("Input too large, finding larger context model")
        return None  # Trigger fallback
```

**Proposé:**

```python
# strategies/context.py
class ContextStrategy(ABC):
    @abstractmethod
    def check_fits(self, input_data: dict, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits in model context."""
        pass

    @abstractmethod
    def get_alternative_models(self, required_tokens: int) -> List[str]:
        """Get models with larger context."""
        pass

class LargeContextFallback(ContextStrategy):
    """Current logic extracted to strategy."""

    def __init__(self, model_limits: Dict[str, int]):
        self.limits = model_limits

    def check_fits(self, input_data, model_name):
        estimated = self._estimate_tokens(input_data)
        max_ctx = self.limits.get(model_name, float('inf'))
        fits = estimated < max_ctx
        return (fits, estimated, max_ctx)

    def get_alternative_models(self, required_tokens):
        # Sort models by context size
        suitable = [
            (name, limit)
            for name, limit in self.limits.items()
            if limit >= required_tokens
        ]
        return sorted(suitable, key=lambda x: x[1])
```

**Intégration dans ScheduledLLM:**

```python
class ScheduledLLM(BaseLLM):
    def __init__(
        self,
        llm: Any,
        model_name: str,
        scheduling_strategy: SchedulingStrategy,
        context_strategy: Optional[ContextStrategy] = None,  # NEW
        max_wait_seconds: float = 300.0
    ):
        self.context_checker = context_strategy

    def _generate(self, prompts, **kwargs):
        # 1. Check context FIRST
        if self.context_checker:
            fits, tokens, max_ctx = self.context_checker.check_fits(prompts, self.model_name)
            if not fits:
                raise ContextLengthError(
                    f"Input {tokens} tokens exceeds {max_ctx} for {self.model_name}"
                )

        # 2. Then scheduling
        # ... existing code
```

**Bénéfices:**
- Context logic **testable indépendamment**
- Facile d'ajouter d'autres strategies (truncation, summarization, etc.)
- `AutoPickerLLM` encore plus simple

---

### 🟡 PRIORITÉ MOYENNE: Améliorations Importantes

#### 3. **Créer FallbackStrategy Interface**
**Effort:** 2 jours
**Impact:** ⭐⭐⭐

Actuellement, la logique de fallback est hardcodée dans `AutoPickerLLM`. On pourrait avoir différentes strategies:

```python
class FallbackStrategy(ABC):
    @abstractmethod
    def select_fallback(
        self,
        failed_model: str,
        available_fallbacks: List[str],
        error: Exception
    ) -> Optional[str]:
        """Select next fallback to try."""
        pass

class SequentialFallback(FallbackStrategy):
    """Try fallbacks in order (current behavior)."""

    def select_fallback(self, failed_model, available, error):
        return available[0] if available else None

class SmartFallback(FallbackStrategy):
    """Select fallback based on error type and model characteristics."""

    def select_fallback(self, failed_model, available, error):
        if isinstance(error, ContextLengthError):
            # Choose fallback with larger context
            return max(available, key=lambda m: self.get_context_limit(m))
        elif isinstance(error, RateLimitError):
            # Choose fallback from different provider
            return self._choose_different_provider(failed_model, available)
        else:
            # Default: first available
            return available[0]

class CostOptimizedFallback(FallbackStrategy):
    """Select cheapest available fallback."""

    def select_fallback(self, failed_model, available, error):
        return min(available, key=lambda m: self.get_cost_per_token(m))
```

**Intégration:**

```python
class AutoPickerLLM(BaseLLM):
    def __init__(
        self,
        primary_llm: ScheduledLLM,
        fallback_llms: List[ScheduledLLM],
        fallback_strategy: FallbackStrategy = None  # NEW
    ):
        self.fallback_selector = fallback_strategy or SequentialFallback()

    def invoke(self, input_data):
        try:
            return self.primary.invoke(input_data)
        except Exception as e:
            # Use strategy to select next fallback
            next_fallback = self.fallback_selector.select_fallback(
                self.primary.model_name,
                [fb.model_name for fb in self.fallbacks],
                e
            )
            # ...
```

**Bénéfices:**
- Fallback logic **pluggable**
- Facile d'optimiser pour coût, latence, ou fiabilité
- Tests plus simples

---

#### 4. **Builder Pattern pour Construction**
**Effort:** 3 jours
**Impact:** ⭐⭐⭐

La construction actuelle est verbeuse:

```python
# Actuellement
from coffee_maker.langchain_observe.llm import get_scheduled_llm
from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

rate_tracker = get_global_rate_tracker("tier1")
primary = get_scheduled_llm(provider="openai", model="gpt-4o-mini", tier="tier1")
fallback1 = get_scheduled_llm(provider="gemini", model="gemini-2.5-flash", tier="tier1")

auto_picker = AutoPickerLLM(
    primary_llm=primary,
    primary_model_name="openai/gpt-4o-mini",
    fallback_llms=[(fallback1, "gemini/gemini-2.5-flash")],
    rate_tracker=rate_tracker,
    cost_calculator=...,
    langfuse_client=...
)
```

**Proposé avec Builder:**

```python
from coffee_maker.langchain_observe.builder import LLMBuilder

llm = (LLMBuilder()
    .with_tier("tier1")
    .with_primary("openai", "gpt-4o-mini")
    .with_fallback("gemini", "gemini-2.5-flash")
    .with_cost_tracking()
    .with_context_fallback()
    .build())
```

**Ou version ultra-simple:**

```python
from coffee_maker.langchain_observe import SmartLLM

# Pour 80% des cas
llm = SmartLLM.for_tier("tier1")

# Pour cas avancés
llm = SmartLLM.for_tier("tier1", primary=("openai", "gpt-4o-mini"))
```

**Bénéfices:**
- **Beaucoup plus simple** pour utilisateurs
- API fluide et découvrable
- Validation au build time
- Valeurs par défaut sensées

---

### 🟢 PRIORITÉ BASSE: Nice to Have

#### 5. **Extraire Cost Tracking Strategy**
**Effort:** 1-2 jours
**Impact:** ⭐⭐

Cost tracking est déjà dans `CostCalculator`, mais on pourrait avoir une strategy interface:

```python
class CostTrackingStrategy(ABC):
    @abstractmethod
    def track_usage(self, model: str, input_tokens: int, output_tokens: int):
        pass

    @abstractmethod
    def get_total_cost(self) -> float:
        pass

class LangfuseCostTracker(CostTrackingStrategy):
    """Track costs to Langfuse."""

class LocalCostTracker(CostTrackingStrategy):
    """Track costs locally only."""

class BudgetEnforcingTracker(CostTrackingStrategy):
    """Enforce daily budget limits."""

    def track_usage(self, model, in_tokens, out_tokens):
        cost = self._calculate(model, in_tokens, out_tokens)
        if self.daily_cost + cost > self.budget:
            raise BudgetExceededError()
        self.daily_cost += cost
```

**Bénéfices:**
- Différents backends de tracking
- Budgets enforçables
- Testable indépendamment

---

#### 6. **Metrics & Observability Strategy**
**Effort:** 2-3 jours
**Impact:** ⭐⭐

Ajouter observabilité structurée:

```python
class MetricsStrategy(ABC):
    @abstractmethod
    def record_latency(self, model: str, latency_ms: float):
        pass

    @abstractmethod
    def record_error(self, model: str, error_type: str):
        pass

    @abstractmethod
    def record_fallback(self, from_model: str, to_model: str):
        pass

class PrometheusMetrics(MetricsStrategy):
    """Export metrics to Prometheus."""

class DatadogMetrics(MetricsStrategy):
    """Export to Datadog."""

class LocalMetrics(MetricsStrategy):
    """Store metrics locally (current stats dict)."""
```

**Bénéfices:**
- Monitoring en production
- Alertes sur anomalies
- Performance tracking

---

#### 7. **Token Estimation Strategy**
**Effort:** 1 jour
**Impact:** ⭐

Extraction mineure mais propre:

```python
class TokenEstimator(ABC):
    @abstractmethod
    def estimate(self, text: str, model: str) -> int:
        pass

class TiktokenEstimator(TokenEstimator):
    """Use tiktoken for OpenAI models."""

class CharacterBasedEstimator(TokenEstimator):
    """Fallback: 4 chars = 1 token."""
```

---

## Plan d'Action Recommandé

### Sprint 1 (1 semaine): Simplification Critique
**Focus:** Rendre le code **vraiment simple**

1. ✅ **Jour 1-2:** Simplifier AutoPickerLLM
   - Retirer toute la logique de scheduling/retry
   - Ne garder que fallback + cost tracking
   - Tests de régression

2. ✅ **Jour 3-4:** Extraire ContextStrategy
   - Créer interface + implémentation
   - Intégrer dans ScheduledLLM
   - Tests unitaires

3. ✅ **Jour 5:** Documentation
   - Mettre à jour architecture docs
   - Exemples d'utilisation
   - Migration guide

**Résultat:** Code **beaucoup plus simple**, chaque classe fait **une seule chose**.

### Sprint 2 (1 semaine): Améliorer UX
**Focus:** Rendre l'utilisation **ultra-simple**

1. **Jour 1-3:** Builder Pattern
   - LLMBuilder avec API fluide
   - SmartLLM facade
   - Exemples

2. **Jour 4-5:** FallbackStrategy
   - Interface abstraite
   - Implémentations (Sequential, Smart, Cost-optimized)
   - Tests

**Résultat:** API **beaucoup plus facile** à utiliser.

### Sprint 3 (optionnel): Polish
**Focus:** Features avancées

1. Cost tracking strategy
2. Metrics/observability
3. Token estimation

**Résultat:** Système **production-grade** avec monitoring.

## Estimation Totale

| Phase | Effort | Impact | Priorité |
|-------|--------|--------|----------|
| Simplifier AutoPickerLLM | 3-4 jours | ⭐⭐⭐⭐⭐ | 🔴 HAUTE |
| Context Strategy | 2-3 jours | ⭐⭐⭐⭐ | 🔴 HAUTE |
| Builder Pattern | 3 jours | ⭐⭐⭐ | 🟡 MOYENNE |
| Fallback Strategy | 2 jours | ⭐⭐⭐ | 🟡 MOYENNE |
| Cost Strategy | 1-2 jours | ⭐⭐ | 🟢 BASSE |
| Metrics Strategy | 2-3 jours | ⭐⭐ | 🟢 BASSE |
| Token Estimator | 1 jour | ⭐ | 🟢 BASSE |
| **TOTAL** | **14-18 jours** (~3 semaines) | | |

## Recommandation

**Je recommande de faire uniquement Sprint 1 maintenant:**

### Pourquoi Sprint 1 Seulement?

1. **Impact Maximum**
   - AutoPickerLLM simplifié = **code beaucoup plus maintenable**
   - ContextStrategy = **séparation claire des responsabilités**
   - **80% des bénéfices** avec 20% de l'effort

2. **Risque Minimum**
   - Pas de breaking changes
   - Tests existants continuent de passer
   - Migration progressive possible

3. **Quick Wins**
   - 1 semaine de travail
   - Résultats immédiatement visibles
   - Base solide pour futures améliorations

### Sprint 2 & 3: Plus Tard

Builder Pattern et autres sont **nice to have** mais pas critiques:
- Le code actuel marche bien
- `create_auto_picker_llm()` est déjà assez simple
- Peut attendre d'avoir plus de feedback utilisateurs

## Décision?

**Option A: Faire Sprint 1 maintenant** ✅ Recommandé
- 1 semaine
- Simplifie significativement le code
- Prépare pour futures améliorations

**Option B: Faire Sprint 1 + 2**
- 2 semaines
- UX beaucoup meilleure
- Mais plus de risque

**Option C: Ne rien faire et passer aux features**
- Le code actuel **fonctionne bien**
- Refactoring = investissement pour le futur
- Peut être reporté

**Que préfères-tu?**
