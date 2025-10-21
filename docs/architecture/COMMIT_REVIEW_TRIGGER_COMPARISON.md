# Commit Review Trigger: Git Hooks vs Orchestrator Messaging

**Date**: 2025-10-18
**Purpose**: Compare two approaches for triggering architect's commit review
**Decision**: **Orchestrator Messaging** (ADR-011) - Superior to Git Hooks

---

## Résumé Exécutif

**Question initiale**: Comment déclencher la revue de commits par architect après que code_developer commit du code?

**Deux approches considérées**:
1. **Git Hooks** (ADR-010 initial) - Utiliser `.git/hooks/post-commit` pour invoquer architect
2. **Orchestrator Messaging** (ADR-011) - Utiliser la communication inter-agents existante

**Décision**: **Orchestrator Messaging** est supérieur car:
- ✅ Intégration native (pas de dépendance externe)
- ✅ Visibilité complète (orchestrator dashboard)
- ✅ Tests faciles (pas besoin de repo git)
- ✅ Platform-agnostic (même comportement partout)
- ✅ Priorisation (CRITICAL avant NORMAL)

---

## Tableau Comparatif Détaillé

| Critère | Git Hooks | Orchestrator Messaging | Gagnant |
|---------|-----------|------------------------|---------|
| **🏗️ Architecture** | | | |
| Intégration | Externe (git infrastructure) | Native (Python agent system) | **Orchestrator** |
| Dépendances | Git hooks (platform-specific) | Aucune (pure Python) | **Orchestrator** |
| Complexité | Hook bash + subprocess Python | Message JSON simple | **Orchestrator** |
| | | | |
| **👀 Observabilité** | | | |
| Visibilité | Cachée (subprocess) | Visible (orchestrator dashboard) | **Orchestrator** |
| Debugging | Difficile (logs subprocess) | Facile (inspecter fichiers messages) | **Orchestrator** |
| Monitoring | Limité (logs git only) | Complet (status orchestrator) | **Orchestrator** |
| Traçabilité | Logs éparpillés | Tous messages dans `data/agent_messages/` | **Orchestrator** |
| | | | |
| **🧪 Testabilité** | | | |
| Tests unitaires | Dur (besoin repo git) | Facile (mock messages) | **Orchestrator** |
| Tests intégration | Complexe (setup git) | Simple (fichiers JSON) | **Orchestrator** |
| CI/CD | Nécessite git config | Pas de setup spécial | **Orchestrator** |
| | | | |
| **🌍 Portabilité** | | | |
| Cross-platform | Non (bash vs cmd.exe) | Oui (Python pur) | **Orchestrator** |
| Windows | Nécessite Git Bash ou WSL | Fonctionne nativement | **Orchestrator** |
| macOS | OK (bash natif) | OK | **Égalité** |
| Linux | OK (bash natif) | OK | **Égalité** |
| | | | |
| **⚙️ Installation** | | | |
| Setup initial | Manuel (copier hook) | Aucun (déjà intégré) | **Orchestrator** |
| Par développeur | Chaque dev installe hook | Automatique | **Orchestrator** |
| Mise à jour | Redistribuer hook | Aucune action | **Orchestrator** |
| | | | |
| **📊 Prioritisation** | | | |
| Ordre d'exécution | FIFO (first-come-first-serve) | CRITICAL avant NORMAL | **Orchestrator** |
| Queue management | Non (subprocess séquentiel) | Oui (inbox avec priorités) | **Orchestrator** |
| Backlog handling | Non géré | architect traite batches intelligents | **Orchestrator** |
| | | | |
| **⚡ Performance** | | | |
| Latence trigger | Immédiate (<1s) | 5-30s (polling interval) | **Git Hooks** |
| Throughput | Séquentiel (bloquant) | Parallèle (non-bloquant) | **Orchestrator** |
| Scalabilité | Limité (subprocess par commit) | Excellente (queue + batching) | **Orchestrator** |
| | | | |
| **🛡️ Fiabilité** | | | |
| Error handling | Basique (exit code) | Riche (agent crash recovery) | **Orchestrator** |
| Retry logic | Non (hook échoue = perdu) | Oui (message reste jusqu'à traité) | **Orchestrator** |
| Crash recovery | Non | Oui (orchestrator restart agents) | **Orchestrator** |
| | | | |
| **🔧 Maintenance** | | | |
| Code à maintenir | Hook bash + Python subprocess | Messages JSON uniquement | **Orchestrator** |
| Documentation | Git hook docs nécessaires | Déjà documenté (orchestrator) | **Orchestrator** |
| Évolution | Modifier hook (redistribuer) | Modifier message handler | **Orchestrator** |

**Score Final**: Orchestrator **18** - Git Hooks **1** - Égalité **2**

**Gagnant**: **Orchestrator Messaging** (écrasante victoire)

---

## Visualisation des Deux Approches

### Approche 1 : Git Hooks (ADR-010 Initial)

```
┌─────────────────────────────────────────────────────────────┐
│                    GIT HOOKS APPROACH                        │
└─────────────────────────────────────────────────────────────┘

code_developer
    │
    ├─ git commit -m "feat: ..."
    │
    └─ git push
         ↓
    .git/hooks/post-commit (bash script)
         │
         ├─ Détecte commit
         ├─ Parse commit SHA
         └─ Spawn subprocess Python
              │
              └─ python -m coffee_maker.architect.review --sha=a1b2c3d
                   ↓
              architect subprocess
                   │
                   ├─ Review commit
                   ├─ Update skills
                   └─ Write feedback files
                        ↓
                   Exit subprocess

❌ Problèmes:
- Hook externe au système d'agents
- Subprocess non managé par orchestrator
- Pas de visibilité dans dashboard
- Platform-specific (bash vs cmd)
- Difficile à tester
```

### Approche 2 : Orchestrator Messaging (ADR-011)

```
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR MESSAGING APPROACH                 │
└─────────────────────────────────────────────────────────────┘

code_developer (agent géré par orchestrator)
    │
    ├─ git commit -m "feat: ..."
    ├─ git push
    │
    └─ _after_commit_success()
         │
         └─ Écrit message JSON:
              data/agent_messages/architect_inbox/commit_review_a1b2c3d.json
              {
                "type": "commit_review_request",
                "priority": "CRITICAL",
                "content": { "commit_sha": "a1b2c3d", ... }
              }
                   ↓
orchestrator (poll toutes les 30s)
    │
    └─ Détecte nouveau message dans architect_inbox/
         ↓
architect (agent géré par orchestrator)
    │
    ├─ Poll inbox (toutes les 5-30s selon priorité)
    ├─ Lit message commit_review_request
    │
    └─ _process_commit_review()
         │
         ├─ Review commit
         ├─ Update skills
         │
         └─ Écrit feedback messages:
              - data/agent_messages/code_developer_inbox/feedback_a1b2c3d.json
              - data/agent_messages/reflector_inbox/pattern_a1b2c3d.json
              - data/agent_messages/project_manager_inbox/refactor_a1b2c3d.json

✅ Avantages:
- Tout géré par orchestrator
- Visibilité complète (dashboard)
- Messages = fichiers (facile à inspecter)
- Platform-agnostic (Python pur)
- Testable (unit tests sur messages)
```

---

## Analyse Détaillée

### 1. Intégration avec le Système Existant

#### Git Hooks
```bash
# .git/hooks/post-commit (nouveau fichier à créer)
#!/bin/bash

COMMIT_SHA=$(git rev-parse HEAD)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Spawn architect subprocess
python -m coffee_maker.architect.review \
    --commit-sha=$COMMIT_SHA \
    --files="$FILES_CHANGED" \
    --priority=NORMAL
```

**Problèmes**:
- Fichier bash (platform-specific)
- Subprocess non managé par orchestrator
- architect ne reçoit pas message via inbox normale
- Pas de status tracking dans orchestrator

#### Orchestrator Messaging
```python
# coffee_maker/autonomous/agents/code_developer_agent.py
class CodeDeveloperAgent(BaseAgent):
    def _after_commit_success(self, commit_sha: str, files: List[str]):
        """Send commit review request to architect."""
        self._send_message("architect", {
            "type": "commit_review_request",
            "priority": self._determine_priority(commit_sha),
            "content": {
                "commit_sha": commit_sha,
                "files_changed": files,
                ...
            }
        })
```

**Avantages**:
- Python pur (pas de bash)
- Utilise méthode existante `_send_message()` (déjà dans BaseAgent)
- Message visible dans orchestrator dashboard
- Status tracked automatiquement

### 2. Observabilité et Debugging

#### Git Hooks

**Visibilité**: Faible
- Logs dans git output (mélangé avec autres logs)
- Subprocess PID non tracké
- Pas de monitoring orchestrator

**Debugging**:
```bash
# Comment débugger un hook qui échoue?
1. Vérifier logs git (where?)
2. Reproduire manuellement:
   $ bash .git/hooks/post-commit
3. Ajouter echo debug dans hook bash
4. Vérifier si subprocess Python démarre
5. Inspecter logs subprocess (where?)
```

**Complexité**: HAUTE (5 étapes, logs éparpillés)

#### Orchestrator Messaging

**Visibilité**: Excellente
- Tous messages dans `data/agent_messages/`
- orchestrator dashboard montre:
  - Messages envoyés/reçus
  - Inbox size (backlog)
  - Processing time par message
  - Agent status (reviewing, idle, crashed)

**Debugging**:
```bash
# Comment débugger un message qui échoue?
1. Inspecter message fichier:
   $ cat data/agent_messages/architect_inbox/commit_review_a1b2c3d.json
2. Vérifier orchestrator status:
   $ cat data/agent_status/orchestrator_status.json
3. Vérifier architect status:
   $ cat data/agent_status/architect_status.json
4. Consulter logs architect:
   $ tail -f logs/architect.log
```

**Complexité**: FAIBLE (4 étapes, tout centralisé)

### 3. Testabilité

#### Git Hooks

**Setup de test**:
```python
# tests/test_commit_review.py

def test_commit_review_triggered():
    # Setup: Create git repo
    repo = git.Repo.init("/tmp/test_repo")

    # Setup: Install git hook
    hook_path = repo.git_dir / "hooks/post-commit"
    shutil.copy(".git/hooks/post-commit", hook_path)
    os.chmod(hook_path, 0o755)

    # Setup: Create test file
    test_file = repo.working_dir / "test.py"
    test_file.write_text("print('hello')")

    # Action: Commit
    repo.index.add([str(test_file)])
    repo.index.commit("test commit")

    # Assert: architect review triggered?
    # ??? Comment vérifier?
    # - Vérifier subprocess spawned? (comment?)
    # - Vérifier logs? (where?)
    # - Vérifier feedback files? (path?)
```

**Problèmes**:
- Nécessite créer git repo (slow)
- Nécessite installer hook (setup complexe)
- Difficile d'asserter résultat (subprocess externe)
- Tests lents (git ops + subprocess)

#### Orchestrator Messaging

**Setup de test**:
```python
# tests/test_commit_review.py

def test_commit_review_triggered():
    # Setup: Create code_developer agent (no git needed!)
    agent = CodeDeveloperAgent()

    # Action: Simulate commit
    agent._after_commit_success(
        commit_sha="a1b2c3d",
        files_changed=["test.py"]
    )

    # Assert: Message sent to architect
    inbox = Path("data/agent_messages/architect_inbox")
    messages = list(inbox.glob("commit_review_*.json"))

    assert len(messages) == 1
    message = json.loads(messages[0].read_text())
    assert message["type"] == "commit_review_request"
    assert message["content"]["commit_sha"] == "a1b2c3d"
```

**Avantages**:
- Pas besoin de git repo (fast)
- Pas besoin d'installer hook
- Assertions simples (inspect message file)
- Tests rapides (pure Python, no git)

### 4. Performance et Latence

#### Git Hooks

**Latence**: Immédiate (<1s)
```
commit completes → hook triggers → subprocess starts → review begins
     0ms              50ms             200ms              250ms
```

**Total**: 250ms (très rapide)

**Mais**:
- Bloquant si hook lent (retarde git push)
- Pas de batching (1 subprocess par commit)
- Pas de prioritization (FIFO)

#### Orchestrator Messaging

**Latence**: 5-30s (polling interval)
```
commit completes → message written → architect polls → review begins
     0ms               10ms             5-30s             5-30s
```

**Total**: 5-30s (légèrement plus lent)

**Mais**:
- Non-bloquant (git push immédiat)
- Batching intelligent (3 NORMAL reviews par iteration)
- Prioritization (CRITICAL first, then NORMAL)

**Trade-off Acceptable**:
- CRITICAL reviews: <5min (poll every 5s) ✅
- NORMAL reviews: <30min (poll every 30s) ✅
- Benefit: Better integration + observability >> slight latency

### 5. Évolution et Maintenance

#### Git Hooks

**Ajouter une feature**:
```bash
# 1. Modifier .git/hooks/post-commit
vim .git/hooks/post-commit
# 2. Tester localement
bash .git/hooks/post-commit
# 3. Distribuer aux autres devs
git commit .git/hooks/post-commit  # ❌ hooks NOT tracked by git!
# 4. Chaque dev doit copier manuellement
cp hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

**Complexité**: HAUTE (distribution manuelle)

#### Orchestrator Messaging

**Ajouter une feature**:
```python
# 1. Modifier code_developer_agent.py
# 2. Commit et push
git commit -m "feat: Add priority detection to commit messages"
git push origin roadmap
# 3. Tous les agents reçoivent update automatiquement (pull + restart)
```

**Complexité**: FAIBLE (distribution automatique via git)

---

## Cas d'Usage Concrets

### Cas 1 : Commit de Sécurité (CRITICAL)

#### Git Hooks
```
T+0s:   code_developer commits security fix
        git commit -m "fix: Hash passwords with bcrypt"
T+0.2s: Git hook triggers subprocess
T+0.3s: architect subprocess starts review
        ❌ Subprocess PID not tracked by orchestrator
        ❌ No way to see review status in dashboard
T+15m:  Review completes, feedback written to files
        ❌ code_developer must check files manually
```

#### Orchestrator Messaging
```
T+0s:   code_developer commits security fix
        git commit -m "fix: Hash passwords with bcrypt"
T+0.01s: code_developer sends message (priority: CRITICAL)
        ✅ Message visible in orchestrator dashboard
T+5s:   architect polls inbox, sees CRITICAL message
        ✅ Prioritized BEFORE any NORMAL reviews
T+5s:   architect starts review
        ✅ Status updated: "reviewing commit a1b2c3d"
        ✅ Visible in orchestrator dashboard
T+15m:  Review completes, feedback message sent
        ✅ code_developer inbox has new message
        ✅ Notification sent to code_developer
```

**Winner**: **Orchestrator Messaging** (full visibility, prioritization)

### Cas 2 : Backlog de Commits (High Volume)

#### Git Hooks
```
code_developer commits 10 times in 1 hour:

T+0m:  Commit 1 → Hook spawns subprocess 1
T+5m:  Commit 2 → Hook spawns subprocess 2
       ⚠️  Subprocess 1 still running (conflicts?)
T+10m: Commit 3 → Hook spawns subprocess 3
       ⚠️  Subprocess 1 & 2 still running
...
T+50m: Commit 10 → Hook spawns subprocess 10
       🚨 10 subprocesses running in parallel!
       🚨 Resource contention, race conditions
```

**Problème**: Pas de queue management, processes parallèles non coordonnés

#### Orchestrator Messaging
```
code_developer commits 10 times in 1 hour:

T+0m:  Commit 1 → Message sent to architect_inbox
T+5m:  Commit 2 → Message sent to architect_inbox
...
T+50m: Commit 10 → Message sent to architect_inbox
       ✅ 10 messages in inbox (visible in dashboard)

architect processing:
T+0m:  Process commit 1 (15 min)
T+15m: Process commits 2, 3, 4 (batch of 3, 30 min)
T+45m: Process commits 5, 6, 7 (batch of 3, 30 min)
T+75m: Process commits 8, 9, 10 (batch of 3, 30 min)

✅ Sequential processing (no race conditions)
✅ Batching for efficiency
✅ Full visibility into queue
```

**Winner**: **Orchestrator Messaging** (queue management, no race conditions)

---

## Conclusion Finale

### Recommendation: **Orchestrator Messaging** (ADR-011)

**Raisons**:

1. **Intégration Native**: Fait partie du système d'agents (pas d'infrastructure externe)
2. **Observabilité Complète**: Tous messages visibles dans orchestrator dashboard
3. **Testabilité Facile**: Tests unitaires simples (mock messages JSON)
4. **Platform-Agnostic**: Python pur (Windows, macOS, Linux identiques)
5. **Queue Management**: Prioritization (CRITICAL first), batching intelligent
6. **Crash Recovery**: orchestrator restart agents automatiquement
7. **Évolution Facile**: Updates distribuées via git (pas de redistribution manuelle)
8. **Debugging Simple**: Inspecter fichiers messages directement

**Trade-off Accepté**: Légère latence (5-30s vs <1s), **largement compensée** par tous les avantages ci-dessus.

### Impact de la Décision

**Code à Écrire**:
- Git Hooks: ~200 LOC (bash + Python subprocess handling)
- Orchestrator Messaging: ~150 LOC (Python message handling only)

**Temps d'Implémentation**:
- Git Hooks: ~15 heures (hook + subprocess + tests + distribution)
- Orchestrator Messaging: ~12 heures (message handling + tests)

**Économie**: **3 heures** + **architecture plus simple** + **meilleure maintenabilité**

### Prochaines Étapes

1. ✅ Accepter ADR-011 (orchestrator messaging)
2. ✅ Mettre à jour ADR-010 (référencer ADR-011)
3. 📝 Implémenter `code_developer._after_commit_success()` (send message)
4. 📝 Implémenter `architect._process_commit_review()` (poll inbox)
5. 📝 Tester end-to-end workflow avec sample commits
6. 📝 Mesurer latencies et ajuster poll intervals si nécessaire

**Timeline**: 2-3 jours pour implémentation complète

---

## Annexe: Exemples de Code

### Git Hooks Approach (Rejected)

```bash
# .git/hooks/post-commit
#!/bin/bash

COMMIT_SHA=$(git rev-parse HEAD)
FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Spawn architect subprocess (not managed by orchestrator)
python -m coffee_maker.architect.review \
    --commit-sha="$COMMIT_SHA" \
    --files="$FILES" &

exit 0  # Don't block git commit
```

### Orchestrator Messaging Approach (Accepted)

```python
# coffee_maker/autonomous/agents/code_developer_agent.py

class CodeDeveloperAgent(BaseAgent):
    def _after_commit_success(self, commit_sha: str, files: List[str]):
        """Send commit review request to architect via orchestrator."""

        # Determine priority
        priority = "CRITICAL" if self._is_security_commit(files) else "NORMAL"

        # Send message to architect
        self._send_message("architect", {
            "type": "commit_review_request",
            "priority": priority,
            "content": {
                "commit_sha": commit_sha,
                "files_changed": files,
                "priority_name": self.current_priority,
                "commit_message": self.git.get_commit_message(commit_sha),
            }
        })

        logger.info(f"✉️  Sent commit review request to architect ({commit_sha[:7]})")
```

```python
# coffee_maker/autonomous/agents/architect_agent.py

class ArchitectAgent(BaseAgent):
    def _do_background_work(self):
        """Background work: process commit review requests."""

        # Poll inbox for review requests
        messages = self._read_messages(type_filter="commit_review_request")

        # Prioritize CRITICAL first
        critical = [m for m in messages if m["priority"] == "CRITICAL"]
        normal = [m for m in messages if m["priority"] == "NORMAL"]

        # Process CRITICAL reviews immediately
        for msg in critical:
            self._process_commit_review(msg)

        # Process up to 3 NORMAL reviews per iteration
        for msg in normal[:3]:
            self._process_commit_review(msg)

    def _process_commit_review(self, message: Dict):
        """Process a single commit review request."""
        commit_sha = message["content"]["commit_sha"]

        logger.info(f"📋 Reviewing commit {commit_sha[:7]}...")

        # Review, update skills, generate feedback
        ...

        logger.info(f"✅ Commit {commit_sha[:7]} reviewed")
```

**Clean, Simple, Observable** ✨
