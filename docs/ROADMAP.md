# Coffee Maker Agent - Roadmap Globale Priorisée

**Dernière mise à jour**: 2025-10-09
**Branche actuelle**: `feature/rateLimits-fallbacksModels-specializedModels`
**Status**: Phase de refactoring terminée ✅
**Nouveauté**: 2 nouveaux projets Streamlit ajoutés (Analytics Dashboard + Agent UI) ⚡

---

## 🎯 Vision Globale

Transformer **Coffee Maker Agent** en un framework complet d'orchestration LLM avec:
- ✅ **Infrastructure solide** (refactoring terminé)
- 📊 **Analytics avancés** (export Langfuse → SQLite/PostgreSQL)
- 📚 **Documentation professionnelle** (pdoc amélioré)
- 🤖 **Agents intelligents** (5 projets innovants)

---

## 📋 État des Projets

### ✅ Projets Terminés

#### 1. **Refactoring Core Architecture**
**Status**: ✅ **TERMINÉ** (Sprint 1 & 2)
**Date de fin**: 2025-10-08
**Résultats**:
- AutoPickerLLM simplifié (780 → 350 lignes, -55%)
- ContextStrategy extractée
- FallbackStrategy avec 3 implémentations (Sequential, Smart, Cost-optimized)
- Builder Pattern (LLMBuilder + SmartLLM)
- 72 tests, 100% passing
- 100% backward compatible
- Migration complète de la codebase

**Documentation**:
- `docs/refactoring_complete_summary.md`
- `docs/sprint1_refactoring_summary.md`
- `docs/sprint2_refactoring_summary.md`
- `docs/migration_to_refactored_autopicker.md`

---

## 🚀 Roadmap Priorisée

### 🔴 **PRIORITÉ 1: Refactoring Final** (optionnel mais recommandé)

**Durée estimée**: 1 semaine
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planifié (optionnel)

Le refactoring Sprint 1 & 2 est **terminé et fonctionnel**, mais des améliorations sont possibles:

#### Phase 1.1: Refactoring additionnel (optionnel)
- [ ] Extraire ContextStrategy additionelle (si besoin futur de truncation/summarization)
- [ ] Implémenter CostTrackingStrategy (si besoin de budgets enforçables)
- [ ] Implémenter MetricsStrategy (si besoin de Prometheus/Datadog)
- [ ] Implémenter TokenEstimatorStrategy (si besoin d'améliorer précision)

**Référence**: `docs/refactoring_priorities_updated.md`

**Décision**: À faire **APRÈS** les projets prioritaires 2 et 3 (analytics et documentation), car le code actuel est **déjà propre et fonctionnel**.

---

### 🔴 **PRIORITÉ 2: Analytics & Observabilité** ⚡ RECOMMANDÉ EN PREMIER

**Durée estimée**: 2-3 semaines
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planifié

#### Projet: Export Langfuse → SQLite/PostgreSQL

**Objectifs**:
- Export automatique des traces Langfuse vers base locale
- Analytics de performance (LLM, prompts, agents)
- Rate limiting partagé multi-process via SQLite
- Requêtes SQL optimisées pour reporting

**Architecture**:
- Base par défaut: **SQLite** (simple, zero config)
- Option avancée: PostgreSQL (si grande volumétrie)
- **9 tables**: generations, traces, events, rate_limit_counters, scheduled_requests, agent_task_results, prompt_variants, prompt_executions, export_metadata
- Mode WAL pour SQLite (multi-process safe)

**Livrables**:
```
coffee_maker/langchain_observe/analytics/
├── exporter.py                # Export Langfuse → DB
├── db_schema.py               # Schémas SQLAlchemy
├── performance_analyzer.py    # Analyse de performance
├── config.py                  # Configuration
└── metrics/
    ├── llm_metrics.py         # Métriques LLM
    ├── prompt_metrics.py      # Métriques prompts
    └── agent_metrics.py       # Métriques agents

scripts/
├── export_langfuse_data.py    # CLI export manuel
├── setup_metrics_db.py        # Setup initial DB
├── analyze_llm_performance.py # Analyse perf LLMs
└── benchmark_prompts.py       # A/B testing prompts
```

**Bénéfices**:
- ✅ Mesurer ROI des LLMs (coût vs qualité)
- ✅ Optimiser les prompts avec données quantitatives
- ✅ Monitoring de performance des agents
- ✅ Rate limiting multi-process fiable
- ✅ Archivage local sans dépendre du cloud

**Référence**: `docs/langfuse_to_postgresql_export_plan.md`

**Timeline**:
- Semaine 1: Setup DB + Exporter core (13-20h)
- Semaine 2: Analytics + Métriques (8-12h)
- Semaine 3: Tests + Documentation (5-8h)

---

### 🔴 **PRIORITÉ 3: Streamlit Analytics Dashboard** ⚡ NOUVEAU

**Durée estimée**: 1-2 semaines
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planifié
**Dépendance**: Requiert PRIORITÉ 2 (Analytics & Observabilité) complété

#### Projet: Dashboard Streamlit pour Analyse LLM & Coûts

**Objectifs**:
- Dashboard interactif pour analyser l'utilisation des LLMs
- Visualisation des coûts par modèle, agent, et tâche
- Graphiques de performance et tendances
- Export de rapports personnalisés

**Fonctionnalités clés**:
- 📊 **Vue d'ensemble**: Métriques globales (coûts totaux, tokens, requêtes)
- 📈 **Tendances**: Graphiques temporels d'utilisation et coûts
- 🔍 **Analyse par modèle**: Comparaison GPT-4, Claude, Gemini, etc.
- 🤖 **Analyse par agent**: Performances et coûts par agent
- 💰 **Budget tracking**: Alertes et prédictions de dépassement
- 📥 **Export**: PDF, CSV, rapports personnalisés

**Architecture**:
```
streamlit_apps/
├── analytics_dashboard/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_overview.py        # Vue d'ensemble
│   │   ├── 02_cost_analysis.py   # Analyse coûts détaillée
│   │   ├── 03_model_comparison.py # Comparaison modèles
│   │   ├── 04_agent_performance.py # Performance agents
│   │   └── 05_exports.py         # Export rapports
│   ├── components/
│   │   ├── charts.py             # Composants graphiques
│   │   ├── metrics.py            # Widgets métriques
│   │   └── filters.py            # Filtres temporels/agents
│   └── queries/
│       └── analytics_queries.py  # Requêtes SQLite/PostgreSQL
```

**Livrables**:
- [ ] Dashboard Streamlit multi-pages
- [ ] Connexion à la base analytics (SQLite/PostgreSQL)
- [ ] Visualisations interactives (Plotly/Altair)
- [ ] Filtres dynamiques (dates, agents, modèles)
- [ ] Export de rapports (PDF, CSV)
- [ ] Configuration et authentification
- [ ] Documentation utilisateur

**Bénéfices**:
- ✅ Visibilité immédiate sur les coûts LLM
- ✅ Identification rapide des agents coûteux
- ✅ Optimisation basée sur données réelles
- ✅ Démonstration du ROI du framework
- ✅ Interface accessible (non-technique)

**Timeline**:
- Semaine 1: Setup + Pages principales + Graphiques (8-12h)
- Semaine 2: Filtres + Export + Tests + Documentation (6-10h)
- **Total**: 14-22h

---

### 🔴 **PRIORITÉ 4: Streamlit Agent Interaction UI** ⚡ NOUVEAU

**Durée estimée**: 1-2 semaines
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planifié
**Dépendance**: Aucune (peut être fait en parallèle)

#### Projet: Interface Streamlit pour Interaction avec les Agents

**Objectifs**:
- Interface graphique pour interagir avec les agents Coffee Maker
- Chat interactif avec streaming des réponses
- Configuration dynamique des agents (modèles, stratégies)
- Historique de conversations et export
- Démo et testing des capacités des agents

**Fonctionnalités clés**:
- 💬 **Chat interface**: Conversation fluide avec agents
- 🔄 **Streaming**: Affichage en temps réel des réponses
- ⚙️ **Configuration**: Choix du modèle, température, stratégies
- 📝 **Historique**: Sauvegarde et rechargement de conversations
- 🎯 **Agents prédéfinis**: Templates pour différents use cases
- 📊 **Métriques live**: Tokens, coût, latence par requête
- 🎨 **Multi-agents**: Support de conversations multi-agents

**Architecture**:
```
streamlit_apps/
├── agent_interface/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_chat.py            # Interface de chat
│   │   ├── 02_agent_config.py    # Configuration agents
│   │   ├── 03_history.py         # Historique conversations
│   │   └── 04_playground.py      # Testing & expérimentation
│   ├── components/
│   │   ├── chat_interface.py     # Composant chat
│   │   ├── agent_selector.py     # Sélection d'agent
│   │   ├── model_config.py       # Configuration modèle
│   │   └── metrics_display.py    # Affichage métriques
│   ├── agents/
│   │   ├── agent_manager.py      # Gestion instances d'agents
│   │   └── agent_templates.py    # Templates prédéfinis
│   └── storage/
│       └── conversation_storage.py # Sauvegarde conversations
```

**Livrables**:
- [ ] Interface de chat avec streaming
- [ ] Configuration dynamique des agents
- [ ] Support de multiples agents (code reviewer, architect, etc.)
- [ ] Historique persistant des conversations
- [ ] Métriques en temps réel (tokens, coût, latence)
- [ ] Export de conversations (Markdown, JSON)
- [ ] Templates d'agents prédéfinis
- [ ] Documentation utilisateur

**Bénéfices**:
- ✅ Facilite l'utilisation des agents (non-développeurs)
- ✅ Démo interactive des capacités du framework
- ✅ Testing rapide de prompts et configurations
- ✅ Expérience utilisateur moderne et intuitive
- ✅ Accélération de l'adoption du framework
- ✅ Collecte de feedback utilisateur

**Timeline**:
- Semaine 1: Chat interface + Streaming + Config (10-14h)
- Semaine 2: Historique + Export + Templates + Tests (8-12h)
- **Total**: 18-26h

---

### 🔴 **PRIORITÉ 5: Documentation Professionnelle**

**Durée estimée**: 1-2 semaines
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planifié

#### Projet: Amélioration Documentation pdoc

**Objectifs**:
- Documentation API complète et navigable
- Exemples d'utilisation pour chaque composant
- Validation automatique de la documentation
- Publication automatique sur GitHub Pages ✅ (déjà en place)

**Livrables**:
- [ ] Configuration pdoc (`.pdoc.yml`)
- [ ] `__init__.py` enrichis avec docstrings complets
- [ ] Docstrings Google Style pour tous les modules publics
- [ ] Exemples d'utilisation dans chaque classe/fonction
- [ ] Variables `__pdoc__` pour masquer/documenter attributs
- [ ] Script de validation (`scripts/validate_docs.py`)

**Modules prioritaires**:
1. `auto_picker_llm_refactored.py` ✅ (déjà bien documenté, enrichir)
2. `builder.py` ⚠️ (nouveau, à documenter complètement)
3. `strategies/fallback.py` ✅ (ajouter exemples concrets)
4. `llm.py`, `cost_calculator.py`, `scheduled_llm.py`

**Référence**: `docs/pdoc_improvement_plan.md`

**Timeline**:
- Phase 1: Configuration (1-2h)
- Phase 2: `__init__.py` files (2-3h)
- Phase 3: Modules prioritaires (5-8h)
- Phase 4: Métadonnées (1-2h)
- Phase 5: Tests & validation (2-3h)
- **Total**: 11-18h

**Note**: GitHub Action déjà en place ✅, il suffit d'enrichir les docstrings.

---

### 🟡 **PRIORITÉ 6: Projets Innovants** (à choisir selon intérêt)

**Durée estimée**: 3-4 semaines **par projet**
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Documentation complète créée
**Dépendance**: Recommandé après les Streamlit apps (Priorités 3 & 4)

Choisir **1 projet** à implémenter en premier, selon l'intérêt et les besoins:

---

#### Option A: **Multi-Model Code Review Agent** ⭐ TOP RECOMMANDATION

**Pitch**: Agent qui review du code avec **plusieurs LLMs simultanément**, chacun avec une expertise différente (bugs, architecture, performance, sécurité).

**Cas d'usage**:
- Code review automatisé avant merge
- Analyse multi-perspective d'un fichier/PR
- Détection de patterns de bugs récurrents
- Suggestions d'amélioration de performance

**Livrables**:
```
coffee_maker/code_reviewer/
├── reviewer.py                 # MultiModelCodeReviewer
├── perspectives/
│   ├── bug_hunter.py           # GPT-4 pour bugs
│   ├── architect_critic.py     # Claude pour architecture
│   ├── performance_analyst.py  # Gemini pour performance
│   └── security_auditor.py     # Agent sécurité
├── report_generator.py         # Génération rapports HTML
└── git_integration.py          # Hooks Git
```

**Impact business**:
- ⚡ Réduction du temps de code review (30-50%)
- 🐛 Détection précoce de bugs (-40% bugs en prod)
- 📈 Amélioration de la qualité du code
- 💰 ROI direct mesurable

**Référence**: `docs/projects/01_multi_model_code_review_agent.md`

**Timeline**: 3-4 semaines

---

#### Option B: **Self-Improving Prompt Lab**

**Pitch**: Système d'optimisation automatique de prompts avec A/B testing, algorithmes évolutifs, et apprentissage continu.

**Cas d'usage**:
- A/B testing de variantes de prompts
- Optimisation automatique par algorithme génétique
- Tracking de performance de chaque prompt
- Amélioration continue sans intervention manuelle

**Livrables**:
```
coffee_maker/prompt_lab/
├── lab.py                      # PromptLab orchestrator
├── experiments/
│   ├── ab_tester.py            # A/B testing
│   ├── genetic_optimizer.py   # Algorithme génétique
│   └── experiment_runner.py   # Exécution expériences
├── mutators/
│   └── prompt_mutator.py      # Mutations de prompts
└── reporting/
    └── experiment_report.py   # Rapports d'expériences
```

**Impact business**:
- 📈 Amélioration de qualité des réponses (+15-30%)
- 💰 Réduction des coûts (prompts plus courts et efficaces)
- 🤖 Amélioration continue automatique
- 📊 Données quantitatives pour décisions

**Référence**: `docs/projects/02_self_improving_prompt_lab.md`

**Timeline**: 3-4 semaines

---

#### Option C: **Agent Ensemble Orchestrator**

**Pitch**: Meta-agent qui coordonne plusieurs agents spécialisés (architect, coder, tester, reviewer) avec patterns de collaboration (séquentiel, parallèle, débat).

**Cas d'usage**:
- Développement de features complexes
- Pipelines de review automatiques
- Analyse multi-perspective
- Résolution de problèmes par consensus

**Livrables**:
```
coffee_maker/agent_ensemble/
├── orchestrator.py             # Meta-agent
├── agents/
│   ├── architect_agent.py      # Design
│   ├── coder_agent.py          # Implementation
│   ├── tester_agent.py         # Tests
│   └── reviewer_agent.py       # Review
├── patterns/
│   ├── sequential.py           # Pipeline
│   ├── parallel.py             # Fan-out/fan-in
│   └── debate.py               # Consensus
└── coordination/
    ├── task_decomposer.py      # Décomposition
    └── result_synthesizer.py   # Synthèse
```

**Impact business**:
- 🚀 Résolution de tâches complexes (+40% productivité)
- 🤝 Collaboration multi-modèles optimale
- 🎯 Meilleure qualité par consensus
- 📊 Métriques de collaboration

**Référence**: `docs/projects/03_agent_ensemble_orchestrator.md`

**Timeline**: 3-4 semaines

---

#### Option D: **Cost-Aware Smart Router**

**Pitch**: Routeur intelligent qui choisit dynamiquement le meilleur modèle pour chaque requête selon des contraintes de budget, latence, et qualité.

**Cas d'usage**:
- Optimisation coût/qualité automatique
- Budget management en temps réel
- Load balancing entre providers
- Apprentissage des patterns de tâches

**Livrables**:
```
coffee_maker/smart_router/
├── router.py                   # SmartRouter
├── prediction/
│   ├── complexity_predictor.py # ML prédiction complexité
│   └── cost_predictor.py       # Prédiction coût
├── optimization/
│   ├── optimizer.py            # Sélection optimale
│   └── budget_manager.py       # Gestion budgets
└── learning/
    ├── pattern_learner.py      # Apprentissage patterns
    └── model_ranker.py         # Ranking modèles
```

**Impact business**:
- 💰 Réduction coûts (-30-50%)
- ⚡ Optimisation latence/qualité
- 📊 Budget enforcement en temps réel
- 🎯 ROI direct et mesurable

**Référence**: `docs/projects/04_cost_aware_smart_router.md`

**Timeline**: 3-4 semaines

---

#### Option E: **LLM Performance Profiler**

**Pitch**: Outil de profiling automatisé qui mesure finement les performances des LLMs sur différentes dimensions et génère des rapports comparatifs détaillés.

**Cas d'usage**:
- Benchmark automatisé et reproductible
- Comparaison de modèles (coût, latence, qualité)
- Stress testing et context window testing
- Génération de rapports HTML interactifs

**Livrables**:
```
coffee_maker/llm_profiler/
├── profiler.py                 # LLMProfiler
├── benchmarks/
│   ├── code_gen_benchmark.py   # Code generation
│   ├── summarization_benchmark.py
│   └── translation_benchmark.py
├── metrics/
│   ├── latency_meter.py        # Mesure latence
│   ├── quality_evaluator.py   # Évaluation qualité
│   └── cost_calculator.py      # Calcul coûts
└── reporting/
    ├── html_reporter.py        # Rapports HTML
    └── comparison_generator.py # Comparaisons
```

**Impact business**:
- 📊 Décisions basées sur données quantitatives
- 💰 Optimisation coût/qualité
- ⚡ Identification des modèles les plus rapides
- 🎯 Benchmarks reproductibles

**Référence**: `docs/projects/05_llm_performance_profiler.md`

**Timeline**: 3-4 semaines

---

## 📅 Calendrier Recommandé

### **Mois 1: Fondations Solides**

#### Semaine 1-3: Analytics & Observabilité 🔴 PRIORITÉ
- Setup base SQLite + Export Langfuse
- Analytics de performance
- Rate limiting multi-process
- **Deliverable**: Système d'analytics opérationnel

---

### **Mois 2: Interfaces Utilisateur Streamlit** ⚡ NOUVEAU

#### Semaine 1-2: Analytics Dashboard 🔴 PRIORITÉ
- Dashboard Streamlit pour visualisation LLM & coûts
- Connexion à la base analytics
- Graphiques interactifs (Plotly/Altair)
- Export de rapports (PDF, CSV)
- **Deliverable**: Dashboard analytics opérationnel

#### Semaine 3-4: Agent Interaction UI 🔴 PRIORITÉ
- Interface de chat avec agents
- Streaming de réponses en temps réel
- Configuration dynamique des agents
- Historique et export de conversations
- **Deliverable**: Interface web pour interagir avec les agents

---

### **Mois 3: Documentation & Premier Projet Innovant**

#### Semaine 1: Documentation 🔴 PRIORITÉ
- Amélioration pdoc
- Validation docstrings
- **Deliverable**: Documentation API professionnelle

#### Semaine 2-4: Premier Projet Innovant (optionnel)

Choisir **1 projet** parmi les 5 options selon priorité business:

**Option recommandée**: **Multi-Model Code Review Agent** ⭐

- Core reviewer + Perspectives
- Report generation + Git integration
- Tests + Documentation

---

### **Mois 4+: Expansion (selon besoins)**

Choix possibles:
- Implémenter un 2ème projet innovant (Agent Ensemble, Prompt Lab, etc.)
- Améliorer les Streamlit apps avec feedback utilisateurs
- Refactoring additionnel (ContextStrategy, MetricsStrategy)
- Features avancées selon feedback

---

## 🎯 Métriques de Succès

### Analytics & Observabilité
- ✅ Export automatique Langfuse → SQLite fonctionnel
- ✅ Requêtes SQL d'analyse utilisables
- ✅ Rate limiting multi-process fiable
- ✅ 0 doublons dans les exports

### Streamlit Analytics Dashboard
- ✅ Dashboard accessible via navigateur
- ✅ Graphiques de coûts et tendances fonctionnels
- ✅ Filtres dynamiques opérationnels (dates, agents, modèles)
- ✅ Export de rapports PDF/CSV
- ✅ Temps de chargement < 3 secondes

### Streamlit Agent Interaction UI
- ✅ Chat interface réactive avec streaming
- ✅ Configuration d'agents fonctionnelle
- ✅ Historique de conversations persistant
- ✅ Support de multiple agents simultanés
- ✅ Métriques en temps réel affichées

### Documentation
- ✅ 100% des fonctions publiques documentées
- ✅ Validation automatique (CI/CD)
- ✅ Exemples d'utilisation pour chaque module
- ✅ GitHub Pages mis à jour

### Projets Innovants (exemple Code Review Agent)
- ✅ Review multi-modèle fonctionnel
- ✅ Rapports HTML générés
- ✅ Intégration Git hooks
- ✅ Réduction temps de review mesurée (-30%)

---

## 🚫 Anti-Priorités (à éviter pour l'instant)

- ❌ **Réécriture complète** - Le refactoring Sprint 1 & 2 est suffisant
- ❌ **Optimisations prématurées** - Focus sur features business
- ❌ **Support de tous les LLM providers** - Stick aux 3 actuels (OpenAI, Gemini, Anthropic)
- ❌ **UI/Frontend complexe** - Streamlit suffit, pas besoin de React/Vue.js pour le moment

---

## 🔄 Flexibilité et Adaptation

Cette roadmap est **flexible** et peut être ajustée selon:
- Feedback utilisateurs
- Priorités business
- Nouvelles opportunités technologiques
- Contraintes de temps/ressources

**Revue recommandée**: Tous les mois, réévaluer les priorités.

---

## 📚 Documentation Associée

### Projets Terminés
- `docs/refactoring_complete_summary.md` - Résumé complet du refactoring
- `docs/sprint1_refactoring_summary.md` - Sprint 1 détaillé
- `docs/sprint2_refactoring_summary.md` - Sprint 2 détaillé
- `docs/migration_to_refactored_autopicker.md` - Guide de migration

### Projets Planifiés
- `docs/langfuse_to_postgresql_export_plan.md` - Analytics & Export
- `docs/pdoc_improvement_plan.md` - Documentation
- `docs/projects/01_multi_model_code_review_agent.md` - Code Review Agent
- `docs/projects/02_self_improving_prompt_lab.md` - Prompt Lab
- `docs/projects/03_agent_ensemble_orchestrator.md` - Agent Ensemble
- `docs/projects/04_cost_aware_smart_router.md` - Smart Router
- `docs/projects/05_llm_performance_profiler.md` - Performance Profiler

### Architecture & Planification
- `docs/refactoring_priorities_updated.md` - Refactoring additionnel (optionnel)
- `docs/feature_ideas_analysis.md` - Analyse des 5 projets innovants

---

## ✅ Décision Recommandée

**Pour commencer immédiatement**:

1. ✅ **Semaine 1-3** (Mois 1): Implémenter **Analytics & Export Langfuse** 🔴
   - Impact business immédiat (mesure de ROI)
   - Fondation pour tous les autres projets
   - Rate limiting multi-process critique

2. ✅ **Semaine 1-2** (Mois 2): **Streamlit Analytics Dashboard** 🔴 ⚡ NOUVEAU
   - Visualisation immédiate des coûts LLM
   - Interface accessible pour non-techniques
   - Démo du ROI du framework
   - **Dépend de**: Analytics & Export Langfuse complété

3. ✅ **Semaine 3-4** (Mois 2): **Streamlit Agent Interaction UI** 🔴 ⚡ NOUVEAU
   - Facilite l'utilisation des agents
   - Testing rapide et démo interactive
   - Accélère l'adoption du framework
   - **Peut être fait en parallèle** avec Analytics Dashboard si besoin

4. ✅ **Semaine 1** (Mois 3): Améliorer **Documentation pdoc** 🔴
   - Quick win (11-18h)
   - Améliore l'expérience développeur
   - GitHub Action déjà en place

5. ⭐ **Semaine 2-4** (Mois 3) - **Optionnel**: Premier **Projet Innovant**
   - Recommandation: **Multi-Model Code Review Agent**
   - ROI direct et mesurable
   - Cas d'usage concret et utile

**Ensuite**: Réévaluer selon feedback et besoins business.

---

**Prêt à commencer ? Par quel projet veux-tu commencer ?** 🚀
