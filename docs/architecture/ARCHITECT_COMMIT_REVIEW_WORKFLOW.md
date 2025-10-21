# Architect Commit Review & Skills Maintenance Workflow

**Date**: 2025-10-18
**Related ADRs**: ADR-009 (Skills System), ADR-010 (Commit Review)
**Status**: Approved

---

## Vision Stratégique

> **"La revue de code est la meilleure occasion de mettre à jour les index du code."**

L'architect prend une nouvelle responsabilité cruciale : **revue systématique des commits** du code_developer. Cette revue est le moment idéal pour :
- Valider que l'implémentation suit la spec
- Mettre à jour les skills (Code Index, patterns, dépendances)
- Fournir du feedback de qualité

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW COMPLET                              │
└─────────────────────────────────────────────────────────────────┘

1. code_developer implémente une feature
       │
       ├─ Lit ROADMAP.md (priorité suivante)
       ├─ Lit technical spec (SPEC-XXX.md créée par architect)
       ├─ Écrit le code
       └─ git commit -m "feat: ..."
              │
              ▼
2. Git post-commit hook déclenche architect
       │
       ├─ Hook: .git/hooks/post-commit
       ├─ Action: Invoke architect (asynchrone, non-bloquant)
       └─ Passe commit SHA + fichiers modifiés
              │
              ▼
3. architect ANALYSE le commit
       │
       ├─ Lit git diff (git show <SHA>)
       ├─ Identifie fonctions/classes ajoutées/modifiées
       ├─ Compare avec technical spec (si existe)
       └─ Évalue qualité architecturale
              │
              ▼
4. architect MET À JOUR les SKILLS ⭐ SIMULTANÉMENT
       │
       ├─ Code Index: Ajoute nouvelles fonctions/classes
       ├─ Pattern Library: Extrait patterns efficaces
       ├─ Dependency Graph: Met à jour dépendances
       └─ Complexity Metrics: Recalcule métriques
              │
              ▼
5. architect GÉNÈRE du FEEDBACK
       │
       ├─ DÉCISION: Où router le feedback?
       │   │
       │   ├─ Bug critique / Déviation de spec → code_developer (TACTIQUE)
       │   ├─ Pattern efficace / Anti-pattern → reflector (APPRENTISSAGE)
       │   └─ Refactoring nécessaire → project_manager (STRATÉGIQUE)
       │
       └─ Écrit feedback dans data/architect_feedback/<SHA>.md
              │
              ▼
6. FEEDBACK DELIVERY
       │
       ├─ code_developer: Reçoit feedback tactique (à corriger)
       ├─ reflector: Capture patterns (mémoire long terme)
       └─ project_manager: Reçoit feedback stratégique (nouveau PRIORITY?)
```

---

## Trois Canaux de Feedback

### 1. Feedback TACTIQUE → code_developer

**Quand** : Bug, déviation de spec, problème de performance, vulnérabilité sécurité

**Format** :
```markdown
## Tactical Feedback: US-055 Implementation

**Commit**: a1b2c3d - "feat: Implement Code Index builder"

**Issues Found**:
1. **Bug** (line 45): `index.get_category()` returns None when category missing
   - Expected: Raise KeyError
   - Impact: Silent failures in search queries
   - Fix: Add explicit None check or raise exception

2. **Performance** (line 120): Parsing all files sequentially
   - Current: 60 seconds for 450 files
   - Expected: <30 seconds (per spec)
   - Suggestion: Use ProcessPoolExecutor for parallel parsing

**Action Required**: Fix before next commit
**Priority**: HIGH
```

**Livraison** : Fichier `data/architect_feedback/<SHA>_tactical.md` + notification code_developer

---

### 2. Feedback APPRENTISSAGE → reflector

**Quand** : Pattern efficace découvert, anti-pattern identifié, best practice émergente

**Format** :
```markdown
## Learning Feedback: Effective Pattern for Async File I/O

**Commit**: a1b2c3d - "feat: Async index update"

**Pattern Discovered**:
- **What**: Atomic file writes with temp file + rename
- **Where**: coffee_maker/code_index/updater.py:150-180
- **Why Effective**:
  - Prevents partial writes during crash
  - No file corruption even if process killed
  - Fast (atomic rename is O(1) operation)
- **Reuse Opportunity**: Apply to all config file writes

**Recommendation**: Add to pattern library as "Atomic File Update Pattern"

**Reflector Action**: Store in code_developer's memory for future tasks
```

**Livraison** : Écrit dans reflector's delta items storage (mémoire long terme)

---

### 3. Feedback STRATÉGIQUE → project_manager

**Quand** : Refactoring majeur nécessaire, dette technique critique, problème architectural systémique

**Format** :
```markdown
## Strategic Feedback: Payment Module Needs Refactoring

**Commit**: a1b2c3d - "feat: Add PayPal integration"

**Critical Issue**:
- Payment gateway code duplicated across 3 modules (Stripe, PayPal, Square)
- 80% code duplication detected (450 LOC duplicated)
- Each module has slightly different error handling (inconsistent)
- High risk: Bug fixes must be applied 3 times manually

**Recommendation**: Create PRIORITY X - Refactor Payment Gateways
- Extract common logic to AbstractPaymentGateway
- Implement gateway-specific code in subclasses
- Estimated effort: 8-12 hours
- Benefit: Reduce 450 LOC to ~150 LOC, consistent behavior

**Impact**: Current implementation works but creates technical debt
**Urgency**: MEDIUM (not blocking, but should address within 2 weeks)

**Action Required**: project_manager to add new priority to ROADMAP
```

**Livraison** : Notification project_manager + potentiel nouveau PRIORITY dans ROADMAP.md

---

## Décision de Routage (Arbre de Décision)

```python
def route_feedback(commit_analysis: CommitAnalysis) -> FeedbackRoute:
    """Décide où envoyer le feedback basé sur l'analyse."""

    # Bugs critiques / Sécurité → code_developer (URGENT)
    if commit_analysis.has_critical_issues():
        return FeedbackRoute.CODE_DEVELOPER  # TACTIQUE

    # Déviation de spec → code_developer (HIGH priority)
    if commit_analysis.deviates_from_spec():
        return FeedbackRoute.CODE_DEVELOPER  # TACTIQUE

    # Refactoring majeur nécessaire → project_manager (stratégique)
    if commit_analysis.requires_rewrite():
        return FeedbackRoute.PROJECT_MANAGER  # STRATÉGIQUE

    # Dette technique élevée → project_manager (priorisation)
    if commit_analysis.technical_debt_score > 80:
        return FeedbackRoute.PROJECT_MANAGER  # STRATÉGIQUE

    # Nouveau pattern découvert → reflector (apprentissage)
    if commit_analysis.has_new_patterns():
        return FeedbackRoute.REFLECTOR  # APPRENTISSAGE

    # Solution efficace → reflector (best practice)
    if commit_analysis.quality_score > 90:
        return FeedbackRoute.REFLECTOR  # APPRENTISSAGE

    # Améliorations mineures → code_developer (low priority)
    if commit_analysis.has_minor_issues():
        return FeedbackRoute.CODE_DEVELOPER  # TACTIQUE

    # Aucun problème → juste mettre à jour skills (pas de feedback)
    return FeedbackRoute.SKILLS_ONLY
```

**Niveaux de Priorité** :

| Priority | Description | Temps de réponse | Livraison |
|----------|-------------|------------------|-----------|
| **CRITICAL** | Sécurité, bugs critiques | Immédiat (bloque next commit) | Slack alert + fichier |
| **HIGH** | Déviation spec, performance | Dans 1 jour | Fichier + notification |
| **MEDIUM** | Refactoring, dette technique | Dans 1 semaine | Fichier seulement |
| **LOW** | Suggestions, best practices | Optionnel | Reflector delta items |

---

## Mise à Jour des Skills (Simultanée avec Revue)

### Étapes de Mise à Jour

```
architect reçoit commit SHA
       │
       ├─ 1. ANALYSE GIT DIFF
       │      - Fichiers modifiés : [file1.py, file2.py]
       │      - Fonctions ajoutées : [new_func_1(), new_func_2()]
       │      - Classes modifiées : [ClassA, ClassB]
       │      - Lignes de code : +150 LOC, -50 LOC
       │
       ├─ 2. MET À JOUR CODE INDEX
       │      - Ajoute new_func_1() à category "Payment Processing"
       │      - Met à jour line_end de ClassA (était 120, maintenant 145)
       │      - Rafraîchit "last_modified" timestamps
       │      - Recalcule complexity metrics
       │
       ├─ 3. EXTRAIT PATTERNS
       │      - Pattern détecté : "Repository Pattern" in file1.py
       │      - Anti-pattern : "God Class" in ClassB (trop de responsabilités)
       │      → Ajoute à Pattern Library
       │
       ├─ 4. MET À JOUR DÉPENDANCES
       │      - Nouvelle dépendance : import redis
       │      - Ajoute "redis" au dependency graph
       │      - Vérifie circular dependencies (aucune trouvée)
       │
       └─ 5. SAUVEGARDE INDEX
              - Écrit data/code_index/index.json (mise à jour atomique)
              - Durée : 2-5 secondes (incremental update)
```

### Granularité des Mises à Jour

| Type de Changement | Stratégie | Durée | Exemple |
|--------------------|-----------|-------|---------|
| **Minor edit** (1-10 lignes) | Incremental | <2s | Fix typo in docstring |
| **Function refactor** (10-50 lignes) | Partial rebuild | 2-5s | Refactor login() function |
| **New module** (50+ lignes) | Full rebuild category | 10-20s | New payment gateway module |
| **Architectural change** | Full rebuild + spec review | 30-60s | Switch to async architecture |

---

## Performance & SLA

### Temps de Revue

| Type de Commit | Temps de Revue | SLA |
|----------------|----------------|-----|
| **Routine** (bug fix, feature simple) | 5-15 minutes | < 2 heures |
| **Complex** (nouvelle feature, refactoring) | 15-30 minutes | < 4 heures |
| **Critical** (bug sécurité, déviation majeure) | Immédiat | < 30 minutes |

### Temps de Mise à Jour Skills

| Opération | Temps | Mode |
|-----------|-------|------|
| **Incremental update** (5 fichiers) | 2-5 secondes | Asynchrone |
| **Partial rebuild** (1 module) | 10-20 secondes | Asynchrone |
| **Full rebuild** (toute la codebase) | 30-60 secondes | Nightly cron |

### Fraîcheur du Code Index

**Objectif** : <5 minutes après commit (95th percentile)

**Comment** :
- Git hook déclenche architect immédiatement après commit
- architect met à jour skills pendant la revue (même workflow)
- Index sauvegardé avec atomic write (pas de corruption)

---

## Exemples Concrets

### Exemple 1 : Bug Détecté (Feedback Tactique)

```
1. code_developer commit: "feat: Add user registration"
2. architect review:
   - Détecte : Pas de validation email
   - Détecte : Password stocké en plaintext (CRITIQUE)
3. architect update skills:
   - Ajoute register_user() au Code Index
   - Note vulnerability dans security metrics
4. architect génère feedback TACTIQUE:
   - Priority: CRITICAL
   - Route: code_developer
   - Content: "Password must be hashed with bcrypt before storing"
5. code_developer reçoit notification:
   - Corrige immédiatement (bloquant)
   - Nouveau commit: "fix: Hash passwords with bcrypt"
```

### Exemple 2 : Pattern Efficace (Feedback Apprentissage)

```
1. code_developer commit: "feat: Implement retry logic with exponential backoff"
2. architect review:
   - Analyse : Excellent pattern pour resilience
   - Qualité score : 95/100
3. architect update skills:
   - Ajoute retry_with_backoff() au Code Index
   - Extrait "Exponential Backoff Pattern" vers Pattern Library
4. architect génère feedback APPRENTISSAGE:
   - Priority: LOW
   - Route: reflector
   - Content: "Effective pattern for API resilience, reuse for all external calls"
5. reflector capture pattern:
   - Stocke dans delta items (mémoire long terme)
   - code_developer le réutilisera automatiquement pour futures APIs
```

### Exemple 3 : Dette Technique (Feedback Stratégique)

```
1. code_developer commit: "feat: Add third payment gateway (Square)"
2. architect review:
   - Analyse : 80% de code dupliqué avec Stripe et PayPal
   - Dette technique score : 85/100 (HIGH)
3. architect update skills:
   - Ajoute square_gateway.py au Code Index
   - Note code duplication dans metrics
4. architect génère feedback STRATÉGIQUE:
   - Priority: MEDIUM
   - Route: project_manager
   - Content: "Need PRIORITY X - Refactor payment gateways (estimated 8-12h)"
5. project_manager reçoit feedback:
   - Évalue impact vs effort
   - Ajoute nouveau PRIORITY au ROADMAP.md
   - Notifie user de la dette technique
```

---

## Avantages du Workflow

### 1. Boucle de Feedback Fermée

**Avant** :
```
architect créé spec → code_developer implémente → ??? (aucune vérification)
```

**Après** :
```
architect créé spec → code_developer implémente → architect review → feedback
                         ↑                                              │
                         └──────────────────────────────────────────────┘
```

### 2. Skills Toujours à Jour

- **Avant** : Code Index mis à jour nightly (24h de lag possible)
- **Après** : Code Index mis à jour pendant la revue (<5 min après commit)

### 3. Feedback Multi-Niveaux

- **Tactique** : code_developer corrige bugs immédiatement
- **Apprentissage** : reflector capture patterns pour futur
- **Stratégique** : project_manager priorise refactoring

### 4. Contexte Architectural

- architect voit le code dans son contexte architectural
- Peut valider que l'implémentation suit la spec
- Extrait patterns qui ont du sens architecturalement (pas juste syntaxe)

---

## Métriques de Succès

### Quantitatives

| Métrique | Baseline | Target | Mesure |
|----------|----------|--------|--------|
| **Skills Freshness** | N/A | <5 min après commit | Temps entre commit et skills update |
| **Review Latency** | N/A | <2h (routine), <30min (critical) | Temps commit → feedback delivery |
| **Feedback Acceptance** | N/A | >70% | % de feedback qui résulte en code changes |
| **Routing Accuracy** | N/A | >90% | % de feedback correctement routé |
| **Critical Issues Caught** | 0 | >80% avant production | % de critical issues trouvés en review |

### Qualitatives

**code_developer** :
- ✅ Feedback timely et actionnable
- ✅ Bugs critiques détectés avant merge
- ✅ Apprentissage des patterns efficaces
- ✅ Pas submergé par feedback

**architect** :
- ✅ Revues complétées dans SLA
- ✅ Skills restent précis et utiles
- ✅ Architecture alignment maintenu
- ✅ Dette technique en décroissance

**project_manager** :
- ✅ Reçoit feedback stratégique sur refactoring
- ✅ Peut prioriser réduction dette technique
- ✅ Visibilité sur santé architecturale

**reflector** :
- ✅ Capture patterns efficaces
- ✅ Documente anti-patterns à éviter
- ✅ Construit mémoire institutionnelle

---

## Risques & Mitigations

### Risque 1 : architect Devient Bottleneck

**Risque** : Queue de revues grandit plus vite que architect peut traiter

**Mitigation** :
1. **Priority Queue** : CRITICAL commits reviewed first (<30 min)
2. **Automated Pre-Filtering** : Outils automatiques gèrent 80% des checks routiniers
3. **Batch Processing** : Groupe commits similaires pour revue efficace
4. **Time Limits** : Max 15 min par commit routine

**Fallback** : Désactiver reviews temporairement, focus sur skills updates seulement

### Risque 2 : Feedback Overload pour code_developer

**Risque** : Trop de feedback → démotivation

**Mitigation** :
1. **Clear Priorities** : Seulement CRITICAL est urgent
2. **Actionable Feedback** : Focus sur issues spécifiques et fixables
3. **Positive Feedback** : Highlight good patterns (pas juste problèmes)
4. **Volume Limits** : Max 3 feedback items par commit

**Fallback** : Réduire fréquence feedback, seulement CRITICAL issues

### Risque 3 : Skills Update Accuracy

**Risque** : Skills mis à jour incorrectement (mauvais line numbers, code manquant)

**Mitigation** :
1. **Automated Tests** : Valide logique skills update sur sample commits
2. **Incremental Updates** : Seulement update code changé (réduit risque)
3. **Full Rebuild** : Weekly full rebuild pour corriger drift
4. **Manual Spot Checks** : architect valide 10% des updates manuellement

**Fallback** : Manual skills update pour critical priorities

---

## Prochaines Étapes

### Phase 1 : Infrastructure (Semaine 1)
- [ ] Implémenter `coffee_maker/code_architect/commit_reviewer.py`
- [ ] Implémenter `coffee_maker/code_architect/feedback_router.py`
- [ ] Implémenter `coffee_maker/code_architect/skills_updater.py`
- [ ] Étendre `.git/hooks/post-commit` pour invoquer architect

### Phase 2 : Skills Maintenance (Semaine 2)
- [ ] Code Index updater (incremental)
- [ ] Pattern extractor
- [ ] Dependency graph updater
- [ ] Complexity metrics calculator

### Phase 3 : Workflow Integration (Semaine 3)
- [ ] architect dashboard (pending reviews, feedback sent/received)
- [ ] Notification system (Slack optionnel, fichiers mandatory)
- [ ] Feedback tracking (acknowledged, addressed, ignored)

### Phase 4 : Testing & Documentation (Semaine 4)
- [ ] Integration tests (end-to-end workflow)
- [ ] Documentation (architect agent guide, process docs)
- [ ] Metrics & monitoring (review queue, latency, routing accuracy)

**Total Effort** : 40 heures (5 jours full-time ou 2 semaines part-time)

---

## Conclusion

Ce workflow transforme architect d'un rôle "design-only" à "design + supervision + learning capture".

**L'insight clé** : La revue de code est le moment parfait pour mettre à jour les skills car architect :
1. Voit exactement ce qui a changé (git diff)
2. Comprend le contexte architectural (a écrit la spec)
3. Peut valider l'implémentation vs spec
4. Extrait patterns pendant qu'il analyse le code

**Résultat** : Skills toujours à jour, feedback de qualité, boucle fermée, apprentissage continu.

**Prochain Commit** : architect review ce document et fournit feedback ! 😊
