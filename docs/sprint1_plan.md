# Sprint 1: Simplification AutoPickerLLM & Context Strategy

## Date de Début
2025-10-08

## Objectif
Simplifier drastiquement `AutoPickerLLM` en extrayant la logique restante dans des strategies dédiées.

## État Actuel

### Ce qui a déjà été extrait ✅
- ✅ **Rate limiting** → `ProactiveRateLimitScheduler`
- ✅ **Retry logic** → `SchedulingStrategy.should_retry_after_error()`
- ✅ **Backoff exponentiel** → `SchedulingStrategy`
- ✅ **90s rule** → `SchedulingStrategy`
- ✅ **Scheduling proactif** → `ScheduledLLM`

### Ce qui reste dans AutoPickerLLM
- ❌ Context length checking (~100 lignes)
- ❌ Large context model selection
- ✅ Fallback orchestration (à garder)
- ✅ Cost tracking (à garder)
- ✅ Statistics (à garder)

### Métrique Actuelle
- `AutoPickerLLM`: **780 lignes**
- Responsabilités: **8 concerns différents**

## Objectif du Sprint

### Cible
- `AutoPickerLLM`: **~150 lignes** (réduction de 80%)
- Responsabilités: **2 concerns** (fallback + cost tracking)
- Tout le reste → strategies dédiées

## Tâches

### Jour 1-2: Créer ContextStrategy (8h)

#### Task 1.1: Définir l'interface (1h)
```python
# coffee_maker/langchain_observe/strategies/context.py

class ContextStrategy(ABC):
    """Strategy for managing context length constraints."""

    @abstractmethod
    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits in model's context.

        Returns:
            (fits, estimated_tokens, max_context)
        """
        pass

    @abstractmethod
    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Get models that can handle required tokens.

        Returns:
            List of model names sorted by context size (smallest first)
        """
        pass

    @abstractmethod
    def estimate_tokens(self, input_data: Any, model_name: str) -> int:
        """Estimate tokens for input."""
        pass
```

#### Task 1.2: Implémenter LargeContextFallback (3h)
```python
class LargeContextFallback(ContextStrategy):
    """Strategy for handling context length with large model fallback.

    Extracts current logic from AutoPickerLLM:
    - Token estimation (tiktoken for OpenAI, char-based for others)
    - Context limit checking
    - Large context model discovery
    """

    def __init__(self, model_limits: Dict[str, int], tokenizers: Dict[str, Any]):
        self.model_limits = model_limits
        self.tokenizers = tokenizers

    def check_fits(self, input_data, model_name):
        estimated = self.estimate_tokens(input_data, model_name)
        max_ctx = self.model_limits.get(model_name, float('inf'))
        fits = estimated <= max_ctx * 0.9  # 90% safety margin
        return (fits, estimated, max_ctx)

    def get_larger_context_models(self, required_tokens):
        # Extract from AutoPickerLLM._get_large_context_models()
        suitable = [
            name for name, limit in self.model_limits.items()
            if limit >= required_tokens
        ]
        return sorted(suitable, key=lambda n: self.model_limits[n])

    def estimate_tokens(self, input_data, model_name):
        # Extract from AutoPickerLLM._estimate_tokens()
        # Use tokenizer if available, else char-based
        pass
```

#### Task 1.3: Tests unitaires pour ContextStrategy (2h)
```python
# tests/unit/test_context_strategy.py

class TestLargeContextFallback:
    def test_check_fits_within_limit(self):
        strategy = LargeContextFallback(
            model_limits={"openai/gpt-4o-mini": 128000},
            tokenizers={}
        )
        fits, tokens, max_ctx = strategy.check_fits("short text", "openai/gpt-4o-mini")
        assert fits is True
        assert tokens < max_ctx

    def test_check_fits_exceeds_limit(self):
        strategy = LargeContextFallback(
            model_limits={"openai/gpt-4o-mini": 100},
            tokenizers={}
        )
        long_text = "word " * 1000  # ~1000 tokens
        fits, tokens, max_ctx = strategy.check_fits(long_text, "openai/gpt-4o-mini")
        assert fits is False
        assert tokens > max_ctx

    def test_get_larger_context_models(self):
        strategy = LargeContextFallback(
            model_limits={
                "openai/gpt-4o-mini": 128000,
                "gemini/gemini-2.5-pro": 2000000,
                "openai/gpt-4o": 128000
            },
            tokenizers={}
        )
        larger = strategy.get_larger_context_models(200000)
        assert "gemini/gemini-2.5-pro" in larger
        assert "openai/gpt-4o-mini" not in larger
```

#### Task 1.4: Intégrer dans ScheduledLLM (2h)
```python
# scheduled_llm.py

class ScheduledLLM(BaseLLM):
    def __init__(
        self,
        llm: Any,
        model_name: str,
        scheduling_strategy: SchedulingStrategy,
        context_strategy: Optional[ContextStrategy] = None,  # NEW
        max_wait_seconds: float = 300.0
    ):
        self.llm = llm
        self.model_name = model_name
        self.scheduling_strategy = scheduling_strategy
        self.context_strategy = context_strategy  # NEW
        self.max_wait_seconds = max_wait_seconds

    def _generate(self, prompts, **kwargs):
        # 1. Check context FIRST (before scheduling)
        if self.context_strategy:
            fits, tokens, max_ctx = self.context_strategy.check_fits(
                prompts, self.model_name
            )
            if not fits:
                raise ContextLengthExceededError(
                    f"Input requires {tokens} tokens but {self.model_name} "
                    f"supports max {max_ctx}"
                )

        # 2. Then scheduling (existing code)
        can_proceed, wait_time = self.scheduling_strategy.can_proceed(...)
        # ...
```

---

### Jour 3-4: Simplifier AutoPickerLLM (12h)

#### Task 2.1: Créer nouvelle exception ContextLengthExceededError (0.5h)
```python
# coffee_maker/langchain_observe/exceptions.py

class ContextLengthExceededError(Exception):
    """Raised when input exceeds model's context length.

    This signals to AutoPickerLLM that it should try a larger context model.
    """
    def __init__(self, message: str, required_tokens: int, max_tokens: int):
        super().__init__(message)
        self.required_tokens = required_tokens
        self.max_tokens = max_tokens
```

#### Task 2.2: Refactorer AutoPickerLLM - Retirer logique de scheduling (3h)

**AVANT (780 lignes):**
```python
class AutoPickerLLM(BaseLLM):
    # 21 fields
    rate_tracker: RateLimitTracker
    max_retries: int
    backoff_base: float
    min_wait_before_fallback: float
    retry_strategy: RetryStrategy
    # ...

    def _try_invoke_model(self, llm, model_name, input_data, is_primary, **kwargs):
        # 250+ lignes de rate limiting, retry, backoff logic
        # ...
```

**APRÈS (~150 lignes):**
```python
class AutoPickerLLM(BaseLLM):
    """Orchestrator for fallback model selection.

    This class is now MUCH simpler - it only handles:
    1. Trying primary model
    2. Catching errors and selecting appropriate fallback
    3. Cost tracking

    All scheduling, rate limiting, and retry logic is now in ScheduledLLM.
    """

    # Only 8 fields now (was 21)
    primary_llm: ScheduledLLM  # Already has scheduling
    primary_model_name: str
    fallback_llms: List[Tuple[ScheduledLLM, str]]  # Already have scheduling
    cost_calculator: Optional[CostCalculator]
    langfuse_client: Optional[Any]
    enable_context_fallback: bool
    stats: Dict[str, int]
    _large_context_models: Optional[List[Tuple[ScheduledLLM, str, int]]]

    def invoke(self, input_data: dict, **kwargs) -> Any:
        """Main invocation - much simpler now!"""
        self.stats["total_requests"] += 1

        # Try primary
        response = self._try_model(self.primary_llm, self.primary_model_name,
                                   input_data, is_primary=True, **kwargs)
        if response is not None:
            return response

        # Try fallbacks
        for fallback_llm, model_name in self.fallback_llms:
            response = self._try_model(fallback_llm, model_name, input_data,
                                      is_primary=False, **kwargs)
            if response is not None:
                return response

        # All failed
        raise RuntimeError("All models exhausted after trying primary and all fallbacks")

    def _try_model(self, llm: ScheduledLLM, model_name: str,
                   input_data: dict, is_primary: bool, **kwargs) -> Optional[Any]:
        """Try a single model. Returns None if should fallback.

        This is now MUCH simpler - just handles:
        - Invoking the ScheduledLLM (which handles all scheduling/retry)
        - Catching errors and deciding if should fallback
        - Cost tracking
        - Context length fallback
        """
        try:
            # ScheduledLLM handles all scheduling, rate limiting, retry logic
            response = llm.invoke(input_data, **kwargs)

            # Track cost
            if self.cost_calculator:
                self._track_cost(response, model_name)

            # Update stats
            if is_primary:
                self.stats["primary_requests"] += 1
            else:
                self.stats["fallback_requests"] += 1

            logger.info(f"Successfully invoked {model_name}")
            return response

        except ContextLengthExceededError as e:
            # Input too large for this model
            if self.enable_context_fallback:
                logger.info(f"Context exceeded for {model_name}, trying larger model")
                return self._try_large_context_model(input_data, e.required_tokens, **kwargs)
            else:
                logger.warning(f"Context exceeded for {model_name}, no fallback enabled")
                return None

        except Exception as e:
            # ScheduledLLM already did retries with 90s rule
            # If we're here, it means it gave up after final attempt
            error_msg = str(e).lower()
            if self._is_rate_limit_error(error_msg):
                logger.warning(f"Rate limit exhausted for {model_name} after retries, using fallback")
                self.stats["rate_limit_fallbacks"] += 1
                return None  # Signal to try next fallback
            else:
                # Other error, propagate
                logger.error(f"Error from {model_name}: {e}")
                raise

    def _try_large_context_model(self, input_data: dict, required_tokens: int,
                                  **kwargs) -> Optional[Any]:
        """Try a model with larger context window."""
        if self._large_context_models is None:
            # Lazy load
            self._large_context_models = self._get_large_context_models()

        for llm, model_name, max_ctx in self._large_context_models:
            if max_ctx >= required_tokens:
                logger.info(f"Trying large context model: {model_name} (max: {max_ctx})")
                response = self._try_model(llm, model_name, input_data,
                                         is_primary=False, **kwargs)
                if response is not None:
                    return response

        logger.error(f"No model found with sufficient context for {required_tokens} tokens")
        return None
```

**Changements clés:**
- ❌ **Supprimé:** Toute la logique de rate limiting (~150 lignes)
- ❌ **Supprimé:** Toute la logique de retry/backoff (~100 lignes)
- ❌ **Supprimé:** Logique de 90s rule (~50 lignes)
- ❌ **Supprimé:** Fields: `rate_tracker`, `max_retries`, `backoff_base`, etc.
- ✅ **Gardé:** Fallback orchestration
- ✅ **Gardé:** Cost tracking
- ✅ **Gardé:** Context length fallback (mais simplifié)
- ✅ **Simplifié:** `_try_invoke_model` → `_try_model` (250 lignes → 50 lignes)

#### Task 2.3: Mettre à jour create_auto_picker_llm (2h)
```python
# create_auto_picker.py

def create_auto_picker_llm(
    tier: str = "tier1",
    primary_provider: str = "openai",
    primary_model: str = "gpt-4o-mini",
    streaming: bool = False,
) -> AutoPickerLLM:
    """Create AutoPickerLLM with scheduled LLMs.

    Much simpler now - just creates ScheduledLLMs and passes them.
    """
    from coffee_maker.langchain_observe.llm import get_scheduled_llm
    from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

    # Get rate tracker for context limits
    rate_tracker = get_global_rate_tracker(tier)

    # Create primary LLM (already has scheduling + context checking)
    primary_llm = get_scheduled_llm(
        provider=primary_provider,
        model=primary_model,
        tier=tier,
        streaming=streaming
    )
    primary_model_name = f"{primary_provider}/{primary_model}"

    # Create fallback LLMs (already have scheduling + context checking)
    fallback_configs = get_fallback_models()
    fallback_llms = []

    for provider, model in fallback_configs:
        if provider == primary_provider and model == primary_model:
            continue

        full_name = f"{provider}/{model}"
        if full_name not in rate_tracker.model_limits:
            continue

        try:
            fallback_llm = get_scheduled_llm(
                provider=provider,
                model=model,
                tier=tier,
                streaming=streaming
            )
            fallback_llms.append((fallback_llm, full_name))
        except Exception as e:
            logger.warning(f"Could not create fallback {full_name}: {e}")

    # Create cost calculator
    pricing_info = {}
    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            full_name = f"{provider}/{model_name}"
            pricing_info[full_name] = config.get("pricing", {})

    cost_calculator = CostCalculator(pricing_info)

    # Get Langfuse client
    try:
        langfuse_client = langfuse.get_client()
    except:
        langfuse_client = None

    # Create AutoPickerLLM (MUCH simpler constructor now)
    auto_picker = AutoPickerLLM(
        primary_llm=primary_llm,
        primary_model_name=primary_model_name,
        fallback_llms=fallback_llms,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        enable_context_fallback=True
    )

    logger.info(f"Created AutoPickerLLM with {len(fallback_llms)} fallbacks")
    return auto_picker
```

#### Task 2.4: Mettre à jour get_scheduled_llm pour inclure context strategy (2h)
```python
# llm.py

def get_scheduled_llm(
    langfuse_client: langfuse.Langfuse = None,
    provider: str = None,
    model: str = None,
    tier: str = "tier1",
    max_wait_seconds: float = 300.0,
    enable_context_checking: bool = True,  # NEW
    **llm_kwargs
):
    """Get LLM with scheduling and context checking."""
    from coffee_maker.langchain_observe.strategies.context import LargeContextFallback

    # Get base LLM
    llm = get_llm(langfuse_client=langfuse_client, provider=provider,
                  model=model, **llm_kwargs)

    # Get rate tracker and scheduler
    rate_tracker = get_global_rate_tracker(tier)
    model_full_name = f"{provider}/{model}"

    scheduler = ProactiveRateLimitScheduler(
        rate_tracker=rate_tracker,
        safety_margin=2
    )

    # Create context strategy if enabled
    context_strategy = None
    if enable_context_checking:
        # Extract context limits from rate tracker
        model_limits = {
            name: limits.get("max_context_tokens", 128000)
            for name, limits in rate_tracker.model_limits.items()
        }

        # Create tokenizers dict (reuse existing logic)
        tokenizers = {
            model_full_name: _get_tokenizer_static(model_full_name)
        }

        context_strategy = LargeContextFallback(
            model_limits=model_limits,
            tokenizers=tokenizers
        )

    # Wrap with scheduled LLM
    if isinstance(llm, BaseChatModel):
        scheduled_llm = ScheduledChatModel(
            llm=llm,
            model_name=model_full_name,
            scheduling_strategy=scheduler,
            context_strategy=context_strategy,  # NEW
            max_wait_seconds=max_wait_seconds
        )
    else:
        scheduled_llm = ScheduledLLM(
            llm=llm,
            model_name=model_full_name,
            scheduling_strategy=scheduler,
            context_strategy=context_strategy,  # NEW
            max_wait_seconds=max_wait_seconds
        )

    return scheduled_llm
```

#### Task 2.5: Tests de régression (4h)
```python
# tests/integration/test_auto_picker_simplified.py

class TestSimplifiedAutoPickerLLM:
    """Tests pour vérifier que AutoPickerLLM simplifié fonctionne comme avant."""

    def test_primary_success(self):
        """Test que primary model fonctionne normalement."""
        auto_picker = create_auto_picker_llm(tier="tier1")
        response = auto_picker.invoke({"input": "Hello"})
        assert response is not None

    def test_fallback_on_rate_limit(self):
        """Test que fallback fonctionne quand primary rate limited."""
        # Mock primary to always raise rate limit
        # Verify fallback is used
        pass

    def test_context_length_fallback(self):
        """Test que large context model est utilisé pour gros input."""
        auto_picker = create_auto_picker_llm(tier="tier1")
        large_input = {"input": "word " * 50000}  # ~50k tokens
        response = auto_picker.invoke(large_input)
        # Should use gemini-2.5-pro (2M context) instead of gpt-4o-mini (128k)
        assert response is not None

    def test_cost_tracking_still_works(self):
        """Test que cost tracking fonctionne toujours."""
        auto_picker = create_auto_picker_llm(tier="tier1")
        auto_picker.invoke({"input": "Hello"})
        stats = auto_picker.get_stats()
        assert "total_cost" in stats

    def test_all_models_exhausted(self):
        """Test que RuntimeError levée si tous les modèles échouent."""
        # Mock tous les LLMs pour échouer
        # Verify RuntimeError raised
        pass
```

---

### Jour 5: Documentation & Polish (6h)

#### Task 3.1: Mettre à jour architecture docs (2h)
```markdown
# docs/architecture_post_sprint1.md

## New Architecture

### Before Sprint 1
```
AutoPickerLLM (780 lines)
├── Rate limiting logic
├── Retry logic
├── Backoff calculations
├── Context checking
├── Token estimation
├── Fallback orchestration
├── Cost tracking
└── Statistics
```

### After Sprint 1
```
AutoPickerLLM (150 lines)
├── Fallback orchestration
├── Cost tracking
└── Statistics

ScheduledLLM (300 lines)
├── Scheduling (proactive)
├── Retry logic (reactive)
├── Context checking
└── Error handling

ProactiveRateLimitScheduler (400 lines)
├── N-2 safety margin
├── 60/RPM spacing
├── Error tracking
├── 90s rule
└── Backoff exponential

LargeContextFallback (150 lines)
├── Token estimation
├── Context limit checking
└── Large model discovery
```

### Benefits
- Each class has ONE clear responsibility
- Testable in isolation
- Easy to extend
- Much simpler to understand
```

#### Task 3.2: Créer migration guide (1h)
```markdown
# docs/migration_guide_sprint1.md

## For Users

### No Changes Required! ✅

The public API remains the same:

```python
# This still works exactly as before
from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm

llm = create_auto_picker_llm(tier="tier1")
response = llm.invoke({"input": "Hello"})
```

### What Changed Internally

1. **AutoPickerLLM is simpler**
   - No longer manages rate limiting (delegated to ScheduledLLM)
   - No longer manages retries (delegated to SchedulingStrategy)
   - Just handles fallback orchestration

2. **ScheduledLLM gained context checking**
   - Now checks context before making request
   - Raises ContextLengthExceededError if too large
   - AutoPickerLLM catches this and tries larger model

3. **New ContextStrategy**
   - Handles all context-related logic
   - Testable independently
   - Easy to customize

## For Developers

### Running Tests

```bash
# Run all tests
poetry run pytest tests/

# Run specific test suites
poetry run pytest tests/unit/test_context_strategy.py
poetry run pytest tests/integration/test_auto_picker_simplified.py
```

### Extending

To add a custom context strategy:

```python
from coffee_maker.langchain_observe.strategies.context import ContextStrategy

class MyContextStrategy(ContextStrategy):
    def check_fits(self, input_data, model_name):
        # Custom logic
        pass
```
```

#### Task 3.3: Créer exemples (1h)
```python
# examples/simplified_autopicker.py

"""Examples showing AutoPickerLLM after Sprint 1 simplification."""

from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm

# Example 1: Basic usage (unchanged)
def example_basic():
    llm = create_auto_picker_llm(tier="tier1")
    response = llm.invoke({"input": "Hello, how are you?"})
    print(response)

# Example 2: Large input (context fallback)
def example_large_input():
    llm = create_auto_picker_llm(tier="tier1", enable_context_fallback=True)

    # This is too large for gpt-4o-mini (128k tokens)
    # AutoPickerLLM will automatically use gemini-2.5-pro (2M tokens)
    large_text = " ".join(["word"] * 100000)  # ~100k tokens
    response = llm.invoke({"input": large_text})
    print(f"Handled large input successfully")

# Example 3: Check stats
def example_stats():
    llm = create_auto_picker_llm(tier="tier1")

    for i in range(5):
        llm.invoke({"input": f"Request {i}"})

    stats = llm.get_stats()
    print(f"Primary requests: {stats['primary_requests']}")
    print(f"Fallback requests: {stats['fallback_requests']}")
    print(f"Rate limit fallbacks: {stats['rate_limit_fallbacks']}")

if __name__ == "__main__":
    example_basic()
    example_large_input()
    example_stats()
```

#### Task 3.4: Update README (1h)
- Mettre à jour architecture diagram
- Ajouter exemples simplifiés
- Documenter les strategies

#### Task 3.5: Code review & cleanup (1h)
- Vérifier tous les imports
- Nettoyer code mort
- Formatter avec black
- Linter avec ruff

---

## Critères de Succès

### Métriques
- [ ] AutoPickerLLM: **< 200 lignes** (actuellement 780)
- [ ] ContextStrategy créée et testée
- [ ] **Tous les tests passent** (0 régression)
- [ ] Coverage: **> 90%** sur nouveau code

### Fonctionnel
- [ ] Fallback fonctionne comme avant
- [ ] Context fallback fonctionne
- [ ] Cost tracking fonctionne
- [ ] Statistics fonctionnent
- [ ] Rate limiting fonctionne (via ScheduledLLM)
- [ ] Retry + 90s rule fonctionnent (via SchedulingStrategy)

### Qualité
- [ ] Documentation complète
- [ ] Migration guide écrit
- [ ] Exemples fournis
- [ ] Code review fait
- [ ] Pas de breaking changes

## Risques & Mitigation

### Risque 1: Breaking Changes
**Probabilité:** Faible
**Impact:** Élevé
**Mitigation:**
- Garder même API publique
- Tests de régression complets
- Migration guide détaillé

### Risque 2: Performance Regression
**Probabilité:** Très faible
**Impact:** Moyen
**Mitigation:**
- Benchmarks avant/après
- Monitoring en test

### Risque 3: Tests Cassés
**Probabilité:** Moyenne
**Impact:** Moyen
**Mitigation:**
- Mise à jour incrémentale des tests
- Tests de régression d'abord

## Timeline

| Jour | Tâches | Heures |
|------|--------|--------|
| Jour 1 | Task 1.1-1.2: Créer ContextStrategy | 4h |
| Jour 1 | Task 1.3: Tests unitaires | 2h |
| Jour 2 | Task 1.4: Intégrer dans ScheduledLLM | 2h |
| Jour 2 | Task 2.1-2.2: Simplifier AutoPickerLLM | 3.5h |
| Jour 3 | Task 2.2: Simplifier AutoPickerLLM (suite) | 4h |
| Jour 3 | Task 2.3: Mettre à jour create_auto_picker | 2h |
| Jour 4 | Task 2.4: Mettre à jour get_scheduled_llm | 2h |
| Jour 4 | Task 2.5: Tests de régression | 4h |
| Jour 5 | Task 3.1-3.5: Documentation & polish | 6h |
| **TOTAL** | | **~30h** (5 jours à 6h/jour) |

## Démarrage

**Prêt à commencer!** 🚀

Commençons par **Task 1.1: Définir l'interface ContextStrategy**
