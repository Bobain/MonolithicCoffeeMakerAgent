la,# Plan d'amélioration de la documentation pdoc

## Contexte
Le projet utilise **pdoc** (v15+) pour générer automatiquement la documentation API à partir des docstrings Python. L'objectif est d'améliorer la lisibilité et la complétude de cette documentation.

---

## 1. Configuration de pdoc

### 1.1 Créer un fichier de configuration `.pdoc.yml`
**Objectif**: Centraliser les options de génération de la documentation.

```yaml
# .pdoc.yml
docformat: google  # ou 'numpy' selon vos préférences
include-undocumented: false  # Masquer les éléments non documentés
show-source: true  # Afficher le code source
math: true  # Support des formules mathématiques (si nécessaire)
search: true  # Activer la recherche
footer-text: "Coffee Maker Agent v0.1.1 - Documentation"
logo: "./ressources/README/coffee_maker.png"  # Optionnel
edit-url:
  coffee_maker: "https://github.com/Bobain/MonolithicCoffeeMakerAgent/blob/main/coffee_maker/"
```

### 1.2 Script de génération de documentation
**Créer**: `scripts/generate_docs.sh`

```bash
#!/bin/bash
# Generate pdoc documentation

poetry run pdoc \
  --output-directory docs/api \
  --docformat google \
  --footer-text "Coffee Maker Agent - Automated LLM Orchestration" \
  --logo https://raw.githubusercontent.com/Bobain/MonolithicCoffeeMakerAgent/main/ressources/README/coffee_maker.png \
  --edit-url coffee_maker=https://github.com/Bobain/MonolithicCoffeeMakerAgent/blob/main/coffee_maker/ \
  coffee_maker
```

### 1.3 Ajouter au `pyproject.toml`
```toml
[tool.poetry.scripts]
docs = "scripts.generate_docs:main"  # Optionnel: wrapper Python
```

---

## 2. Amélioration des docstrings

### 2.1 Standardiser le format de docstrings
**Choisir un format** (recommandation: **Google Style**)

#### Exemple actuel (à améliorer):
```python
def _try_invoke_model(self, llm, model_name, input_data, is_primary, **kwargs):
    """Try to invoke a specific model, handling context length."""
```

#### Exemple amélioré (Google Style):
```python
def _try_invoke_model(
    self,
    llm: Any,
    model_name: str,
    input_data: dict,
    is_primary: bool,
    **kwargs
) -> Optional[Any]:
    """Try to invoke a specific model with context length validation.

    This method checks if the input fits within the model's context window
    before invocation. If the input is too large, it automatically attempts
    to use a larger-context model.

    Args:
        llm: LLM instance (should be ScheduledLLM)
        model_name: Full model name (e.g., "openai/gpt-4o-mini")
        input_data: Input dictionary containing prompt and parameters
        is_primary: Whether this is the primary model or a fallback
        **kwargs: Additional arguments passed to LLM.invoke()

    Returns:
        LLM response object if successful, None if failed

    Raises:
        ValueError: If input exceeds context limit of all available models
        ContextLengthError: If input is too large for the specified model

    Example:
        >>> llm = get_scheduled_llm("openai", "gpt-4o-mini")
        >>> result = self._try_invoke_model(
        ...     llm,
        ...     "openai/gpt-4o-mini",
        ...     {"input": "Hello world"},
        ...     is_primary=True
        ... )
    """
```

### 2.2 Fichiers prioritaires à documenter

#### **Priorité HAUTE** (modules publics):
1. **`coffee_maker/langchain_observe/auto_picker_llm_refactored.py`**
   - ✅ Déjà bien documenté mais peut être amélioré
   - Ajouter des exemples d'utilisation dans le docstring de classe
   - Documenter les attributs de classe (`stats`, `_tokenizer`, etc.)

2. **`coffee_maker/langchain_observe/builder.py`** ⚠️ (nouveau fichier)
   - Documenter complètement ce nouveau module
   - Ajouter des exemples de "builder pattern"

3. **`coffee_maker/langchain_observe/strategies/fallback.py`**
   - ✅ Base correcte, ajouter des exemples concrets
   - Documenter `SmartFallback` avec cas d'usage

4. **`coffee_maker/langchain_observe/llm.py`**
   - Documenter `get_scheduled_llm()` avec tous les paramètres
   - Ajouter des exemples pour chaque provider

5. **`coffee_maker/langchain_observe/cost_calculator.py`**
   - Documenter la structure des données de coût
   - Ajouter des exemples de calcul

#### **Priorité MOYENNE** (modules internes):
6. **`coffee_maker/langchain_observe/rate_limiter.py`**
7. **`coffee_maker/langchain_observe/scheduled_llm.py`**
8. **`coffee_maker/langchain_observe/strategies/retry.py`**
9. **`coffee_maker/langchain_observe/llm_config.py`**

#### **Priorité BASSE** (utilitaires):
10. **`coffee_maker/utils/`**
11. **`coffee_maker/code_formatter/`**

---

## 3. Enrichir les fichiers `__init__.py`

### 3.1 Module principal: `coffee_maker/__init__.py`
**État actuel**: Vide (1 ligne)

**Proposition**:
```python
"""Coffee Maker Agent: Intelligent LLM orchestration framework.

Coffee Maker is a Python framework for building robust multi-LLM applications
with automatic fallback, rate limiting, cost tracking, and smart scheduling.

Key Features:
    - **Automatic Fallback**: Seamlessly switch between LLMs on errors
    - **Rate Limiting**: Built-in rate limit handling with exponential backoff
    - **Cost Tracking**: Monitor and log API costs across providers
    - **Context Management**: Automatic context length validation and fallback
    - **Smart Scheduling**: Proactive scheduling to optimize API usage

Quick Start:
    >>> from coffee_maker.langchain_observe import create_auto_picker_llm_refactored
    >>> from coffee_maker.langchain_observe.cost_calculator import CostCalculator
    >>>
    >>> cost_calc = CostCalculator()
    >>> llm = create_auto_picker_llm_refactored(
    ...     primary_provider="openai",
    ...     primary_model="gpt-4o-mini",
    ...     fallback_configs=[("gemini", "gemini-2.5-flash")],
    ...     cost_calculator=cost_calc
    ... )
    >>> response = llm.invoke({"input": "Hello, world!"})

Modules:
    langchain_observe: LangChain integration with LLM orchestration
    code_formatter: Code formatting utilities using AI agents
    sec_vuln_helper: Security vulnerability detection tools
    utils: General utility functions

For more information, visit:
https://github.com/Bobain/MonolithicCoffeeMakerAgent
"""

__version__ = "0.1.1"
__author__ = "Bobain and some code agents"

# Public API (si vous voulez exposer certaines fonctions)
# from coffee_maker.langchain_observe import create_auto_picker_llm_refactored
# __all__ = ["create_auto_picker_llm_refactored"]
```

### 3.2 Module `langchain_observe/__init__.py`
**État actuel**: 1 ligne basique

**Proposition**:
```python
"""LangChain integration and LLM orchestration utilities.

This module provides advanced LLM orchestration capabilities including:

- **AutoPickerLLM**: Automatic fallback orchestration between multiple LLMs
- **ScheduledLLM**: Rate-limited LLM wrapper with smart scheduling
- **Strategies**: Pluggable retry, fallback, and scheduling strategies
- **Cost Tracking**: Real-time cost calculation and Langfuse integration
- **Rate Limiting**: Global and per-model rate limit management

Architecture:
    AutoPickerLLM (fallback orchestration)
        └── ScheduledLLM (rate limiting + scheduling)
            └── BaseLLM (OpenAI, Gemini, Anthropic)

Examples:
    Simple usage with fallback:
    >>> from coffee_maker.langchain_observe import create_auto_picker_llm_refactored
    >>> llm = create_auto_picker_llm_refactored(
    ...     primary_provider="openai",
    ...     primary_model="gpt-4o-mini",
    ...     fallback_configs=[("gemini", "gemini-2.5-flash")]
    ... )

    Custom fallback strategy:
    >>> from coffee_maker.langchain_observe.strategies.fallback import SmartFallback
    >>> strategy = SmartFallback()
    >>> llm = create_auto_picker_llm_refactored(
    ...     ...,
    ...     fallback_strategy=strategy
    ... )
"""

from coffee_maker.langchain_observe.auto_picker_llm_refactored import (
    AutoPickerLLMRefactored,
    create_auto_picker_llm_refactored,
)
from coffee_maker.langchain_observe.cost_calculator import CostCalculator
from coffee_maker.langchain_observe.llm import get_scheduled_llm

__all__ = [
    "AutoPickerLLMRefactored",
    "create_auto_picker_llm_refactored",
    "CostCalculator",
    "get_scheduled_llm",
]
```

### 3.3 Module `strategies/__init__.py`
```python
"""Strategies for LLM orchestration.

This module provides pluggable strategies for different aspects of LLM management:

- **Fallback Strategies**: Determine which model to try when one fails
- **Retry Strategies**: Define retry behavior with exponential backoff
- **Scheduling Strategies**: Optimize API call timing and rate limit avoidance
- **Context Strategies**: Handle context length overflow (future)

Available Strategies:
    Fallback:
        - SequentialFallback: Try fallbacks in order
        - SmartFallback: Choose based on error type and model characteristics

    Retry:
        - ExponentialBackoffRetry: Retry with exponential backoff

    Scheduling:
        - ProactiveScheduling: Schedule calls to avoid rate limits

Example:
    >>> from coffee_maker.langchain_observe.strategies.fallback import SmartFallback
    >>> from coffee_maker.langchain_observe.strategies.retry import ExponentialBackoffRetry
    >>>
    >>> fallback = SmartFallback(model_configs={...})
    >>> retry = ExponentialBackoffRetry(max_retries=3)
"""

from coffee_maker.langchain_observe.strategies.fallback import (
    FallbackStrategy,
    SequentialFallback,
    SmartFallback,
)
from coffee_maker.langchain_observe.strategies.retry import (
    ExponentialBackoffRetry,
    RetryStrategy,
)
from coffee_maker.langchain_observe.strategies.scheduling import (
    ProactiveScheduling,
    SchedulingStrategy,
)

__all__ = [
    "FallbackStrategy",
    "SequentialFallback",
    "SmartFallback",
    "RetryStrategy",
    "ExponentialBackoffRetry",
    "SchedulingStrategy",
    "ProactiveScheduling",
]
```

---

## 4. Ajouter des exemples dans les docstrings

### 4.1 Types d'exemples à inclure

#### **Exemples d'utilisation basique**
Dans chaque classe principale:
```python
class AutoPickerLLMRefactored(BaseLLM):
    """...

    Examples:
        Basic usage with OpenAI primary and Gemini fallback:
        >>> from coffee_maker.langchain_observe import create_auto_picker_llm_refactored
        >>>
        >>> llm = create_auto_picker_llm_refactored(
        ...     primary_provider="openai",
        ...     primary_model="gpt-4o-mini",
        ...     fallback_configs=[("gemini", "gemini-2.5-flash")]
        ... )
        >>> response = llm.invoke({"input": "Explain quantum computing"})

        With cost tracking and Langfuse:
        >>> from coffee_maker.langchain_observe.cost_calculator import CostCalculator
        >>> import langfuse
        >>>
        >>> cost_calc = CostCalculator()
        >>> langfuse_client = langfuse.Langfuse()
        >>>
        >>> llm = create_auto_picker_llm_refactored(
        ...     primary_provider="openai",
        ...     primary_model="gpt-4o-mini",
        ...     fallback_configs=[("gemini", "gemini-2.5-flash")],
        ...     cost_calculator=cost_calc,
        ...     langfuse_client=langfuse_client
        ... )

        Check usage statistics:
        >>> stats = llm.get_stats()
        >>> print(f"Primary usage: {stats['primary_usage_percent']:.1f}%")
    """
```

#### **Exemples de cas d'erreur**
```python
def _check_context_length(self, input_data: dict, model_name: str):
    """...

    Examples:
        >>> # Input fits within context
        >>> fits, tokens, max_ctx = self._check_context_length(
        ...     {"input": "Short text"},
        ...     "openai/gpt-4o-mini"
        ... )
        >>> fits
        True

        >>> # Input exceeds context (triggers fallback)
        >>> large_input = {"input": "..." * 100000}
        >>> fits, tokens, max_ctx = self._check_context_length(
        ...     large_input,
        ...     "openai/gpt-4o-mini"
        ... )
        >>> fits
        False
        >>> tokens > max_ctx
        True
    """
```

---

## 5. Organisation de la documentation

### 5.1 Structure proposée
```
docs/
├── api/                    # Documentation pdoc générée
│   ├── index.html
│   └── coffee_maker/
│       ├── langchain_observe/
│       └── ...
├── guides/                 # Guides utilisateur (à créer)
│   ├── getting_started.md
│   ├── fallback_strategies.md
│   ├── cost_tracking.md
│   └── rate_limiting.md
├── architecture/           # Documentation d'architecture
│   ├── system_overview.md
│   └── decision_records/
└── pdoc_improvement_plan.md  # Ce document
```

### 5.2 Créer un README pour la documentation
**Créer**: `docs/README.md`

```markdown
# Coffee Maker Agent - Documentation

## Table des matières

### 📚 API Reference
- [API Documentation (pdoc)](./api/index.html) - Documentation complète générée automatiquement

### 🚀 Guides utilisateur
- [Getting Started](./guides/getting_started.md)
- [Fallback Strategies](./guides/fallback_strategies.md)
- [Cost Tracking with Langfuse](./guides/cost_tracking.md)
- [Rate Limiting Configuration](./guides/rate_limiting.md)

### 🏗️ Architecture
- [System Overview](./architecture/system_overview.md)
- [Implementation Summaries](./IMPLEMENTATION_SUMMARY.md)

### 📋 Plans de développement
- [LLM Rate Limiting & Optimization Plan](./llm_rate_limiting_and_cost_optimization_plan.md)
- [Sprint 1 Refactoring](./sprint1_refactoring_summary.md)

---

## Génération de la documentation

Pour générer la documentation API:
```bash
poetry run pdoc --output-directory docs/api coffee_maker
```

Ou utiliser le script:
```bash
./scripts/generate_docs.sh
```
```

---

## 6. Ajout de métadonnées pour pdoc

### 6.1 Variables spéciales reconnues par pdoc

Ajouter dans chaque module:
```python
"""Module description."""

__docformat__ = "google"  # Indique le format de docstring
__pdoc__ = {
    # Masquer des éléments privés de la documentation
    "AutoPickerLLMRefactored._tokenizer": False,
    "AutoPickerLLMRefactored._large_context_models": False,

    # Ou au contraire, forcer l'affichage avec documentation custom
    "AutoPickerLLMRefactored.stats": """
        Usage statistics dictionary.

        Keys:
            total_requests (int): Total number of requests
            primary_requests (int): Requests handled by primary model
            fallback_requests (int): Requests handled by fallback models
            rate_limit_fallbacks (int): Fallbacks due to rate limits
            context_fallbacks (int): Fallbacks due to context length
    """,
}
```

---

## 7. Tests de la documentation

### 7.1 Vérifier les docstrings avec doctest
Ajouter dans `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--doctest-modules"
doctest_optionflags = "NORMALIZE_WHITESPACE ELLIPSIS"
```

### 7.2 Script de validation
**Créer**: `scripts/validate_docs.py`

```python
"""Validate that all public APIs have docstrings."""
import ast
import sys
from pathlib import Path

def check_docstrings(file_path: Path) -> list[str]:
    """Check if all public functions/classes have docstrings."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith('_'):  # Public API
                if not ast.get_docstring(node):
                    missing.append(f"{file_path}:{node.lineno} - {node.name}")

    return missing

def main():
    """Run validation."""
    coffee_maker = Path("coffee_maker")
    all_missing = []

    for py_file in coffee_maker.rglob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        missing = check_docstrings(py_file)
        all_missing.extend(missing)

    if all_missing:
        print("❌ Missing docstrings:")
        for item in all_missing:
            print(f"  {item}")
        sys.exit(1)
    else:
        print("✅ All public APIs documented!")

if __name__ == "__main__":
    main()
```

---

## 8. Intégration CI/CD

### 8.1 GitHub Actions workflow
**✅ DÉJÀ FAIT** - Le projet dispose déjà d'une GitHub Action complète pour publier la documentation pdoc.

Fichier existant: `.github/workflows/publish-to-github-pages.yml`

Cette action génère automatiquement:
- Documentation API (pdoc) → `/api/`
- Rapports de tests pytest → `/pytest_tests/`
- Rapport de couverture → `/coverage/`
- Rapport pip-audit → `/pip_audit/`
- Page d'accueil avec liens vers tous les rapports

**Action recommandée**: Ajouter seulement la validation des docstrings au workflow existant:

```yaml
# À ajouter dans .github/workflows/publish-to-github-pages.yml
# Après l'étape "Install dependencies"

- name: Validate docstrings (optional check)
  run: poetry run python scripts/validate_docs.py || echo "Warning: Some docstrings are missing"
  continue-on-error: true  # Ne bloque pas le build si des docstrings manquent
```

---

## 9. Checklist d'implémentation

### Phase 1: Configuration (1-2h)
- [ ] Créer `.pdoc.yml`
- [ ] Créer `scripts/generate_docs.sh`
- [ ] Tester la génération de base: `poetry run pdoc coffee_maker`

### Phase 2: Documentation des `__init__.py` (2-3h)
- [ ] `coffee_maker/__init__.py`
- [ ] `coffee_maker/langchain_observe/__init__.py`
- [ ] `coffee_maker/langchain_observe/strategies/__init__.py`
- [ ] `coffee_maker/langchain_observe/llm_providers/__init__.py`

### Phase 3: Documentation des modules prioritaires (5-8h)
- [ ] `auto_picker_llm_refactored.py` - Enrichir exemples
- [ ] `builder.py` ⚠️ NOUVEAU - Documentation complète
- [ ] `strategies/fallback.py` - Ajouter exemples SmartFallback
- [ ] `llm.py` - Documenter `get_scheduled_llm()`
- [ ] `cost_calculator.py` - Structure de données + exemples
- [ ] `scheduled_llm.py` - Paramètres de scheduling

### Phase 4: Métadonnées et exclusions (1-2h)
- [ ] Ajouter `__pdoc__` pour masquer les méthodes privées
- [ ] Documenter les attributs de classe importants
- [ ] Ajouter `__docformat__ = "google"` partout

### Phase 5: Tests et validation (2-3h)
- [ ] Créer `scripts/validate_docs.py`
- [ ] Ajouter doctest dans pytest
- [ ] Vérifier tous les exemples fonctionnent
- [ ] Générer et reviewer la doc HTML

### Phase 6: Publication (30min)
- [x] ~~Créer workflow GitHub Actions~~ (✅ déjà fait)
- [x] ~~Configurer GitHub Pages~~ (✅ déjà fait)
- [ ] Ajouter validation des docstrings au workflow existant (optionnel)
- [ ] Créer `docs/README.md`
- [ ] Mettre à jour le README principal avec lien vers docs

---

## 10. Exemples de "bonnes pratiques" à suivre

### 10.1 Structure d'une bonne docstring de classe
```python
class AutoPickerLLMRefactored(BaseLLM):
    """One-line summary (mandatory).

    More detailed description explaining what the class does,
    why it exists, and how it fits in the architecture.

    This class delegates X to Y, and handles Z.

    Attributes:
        primary_llm: Description of this attribute
        primary_model_name: Description with type info
        stats: Dictionary containing usage statistics:
            - total_requests (int): Total count
            - primary_requests (int): Primary model count

    Note:
        Important notes about thread safety, performance, etc.

    Warning:
        Things users should be careful about.

    See Also:
        - :class:`ScheduledLLM`: For rate limiting
        - :class:`FallbackStrategy`: For fallback selection

    Examples:
        Basic usage:
        >>> llm = AutoPickerLLMRefactored(...)
        >>> response = llm.invoke({"input": "..."})

        Advanced usage with custom strategy:
        >>> from strategies.fallback import SmartFallback
        >>> llm = AutoPickerLLMRefactored(..., fallback_strategy=SmartFallback())

    References:
        - Design pattern: https://...
        - Related issue: #123
    """
```

### 10.2 Structure d'une bonne docstring de fonction
```python
def create_auto_picker_llm_refactored(
    primary_provider: str,
    primary_model: str,
    fallback_configs: List[Tuple[str, str]],
    **kwargs
) -> AutoPickerLLMRefactored:
    """Create a fully configured AutoPickerLLM instance.

    This is a convenience factory function that creates and wires together
    all the necessary components (ScheduledLLM, strategies, trackers).

    Args:
        primary_provider: LLM provider name. Must be one of:
            - "openai": OpenAI GPT models
            - "gemini": Google Gemini models
            - "anthropic": Anthropic Claude models
        primary_model: Model identifier (e.g., "gpt-4o-mini")
        fallback_configs: List of (provider, model) tuples for fallback chain.
            Example: [("gemini", "gemini-2.5-flash"), ("anthropic", "claude-3-5-haiku")]
        tier: API tier for rate limiting. Default: "tier1"
        cost_calculator: Optional CostCalculator instance
        langfuse_client: Optional Langfuse client for observability
        **kwargs: Additional arguments passed to AutoPickerLLMRefactored

    Returns:
        Fully configured AutoPickerLLMRefactored instance ready to use

    Raises:
        ValueError: If provider is not supported
        ImportError: If required provider library is not installed

    Example:
        >>> llm = create_auto_picker_llm_refactored(
        ...     primary_provider="openai",
        ...     primary_model="gpt-4o-mini",
        ...     fallback_configs=[("gemini", "gemini-2.5-flash")]
        ... )
        >>> response = llm.invoke({"input": "Hello!"})

    See Also:
        - :func:`get_scheduled_llm`: Create individual scheduled LLMs
        - :class:`AutoPickerLLMRefactored`: The returned class
    """
```

---

## 11. Estimation du temps total

| Phase | Tâches | Temps estimé |
|-------|--------|--------------|
| 1 | Configuration pdoc | 1-2h |
| 2 | `__init__.py` files | 2-3h |
| 3 | Modules prioritaires | 5-8h |
| 4 | Métadonnées | 1-2h |
| 5 | Tests & validation | 2-3h |
| 6 | Publication | 30min |
| **TOTAL** | | **11-18h** |

---

## 12. Ressources utiles

- [pdoc Documentation](https://pdoc.dev/)
- [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [NumPy Style Docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Example pdoc project](https://github.com/mitmproxy/pdoc/tree/main/pdoc)

---

## Conclusion

Ce plan fournit une roadmap complète pour améliorer significativement la documentation pdoc du projet Coffee Maker Agent. En suivant ces étapes, vous obtiendrez:

1. ✅ Documentation API complète et navigable
2. ✅ Exemples d'utilisation pour chaque composant
3. ✅ Validation automatique de la documentation
4. ✅ Publication automatique sur GitHub Pages
5. ✅ Meilleure expérience développeur

**Prochaine étape recommandée**: Commencer par la Phase 1 (configuration) pour valider l'approche, puis itérer sur les modules un par un.
