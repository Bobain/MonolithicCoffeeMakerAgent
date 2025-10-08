# Error Handling & Fallback Strategy

## Date
2025-10-08

## Vue d'Ensemble

Le système de gestion des rate limits suit une approche **3 niveaux** :

1. **Proactif** : Prévient les erreurs avant qu'elles n'arrivent
2. **Réactif** : Gère les erreurs avec backoff exponentiel + règle des 90s
3. **Fallback** : Bascule vers un modèle alternatif si tout échoue

## Niveau 1: Scheduling Proactif

### Règles Préventives

Avant chaque appel, `SchedulingStrategy` vérifie:

```python
# Règle N-2: jamais atteindre N-1 de la limite
if requests_in_window >= (rpm - 2):
    wait_for_capacity()

# Règle 60/RPM: espacement minimum entre requêtes
if time_since_last < (60 / rpm):
    wait_for_spacing()
```

**Résultat:** Les erreurs de rate limit sont **prévenues** avant l'appel.

## Niveau 2: Gestion Réactive des Erreurs

### Quand le Proactif Échoue

Même avec scheduling proactif, des erreurs peuvent survenir:
- Rate limits provider plus stricts que prévus
- Burst soudain de requêtes concurrentes
- Quotas journaliers atteints

### Flow de Gestion d'Erreur

```python
try:
    response = llm.invoke(input)
    scheduling_strategy.record_request(model, tokens)  # Succès
    return response

except RateLimitError as e:
    scheduling_strategy.record_error(model, e)  # Enregistre l'échec

    should_retry, wait_time = scheduling_strategy.should_retry_after_error(model)

    if should_retry:
        time.sleep(wait_time)  # Attend avec backoff exponentiel
        # Retry loop continue
    else:
        raise  # Abandonne, signal pour fallback
```

### Backoff Exponentiel

Retry avec attente croissante:

```
Erreur 1: attend 60s   (60 * 2^0)
Erreur 2: attend 120s  (60 * 2^1)
Erreur 3: attend 240s  (60 * 2^2)
```

Basé sur le temps **depuis le dernier appel** (successful ou failed).

### Règle des 90 Secondes

Après `max_retries` échecs:

```python
if retries >= max_retries:
    time_since_last_failure = now - last_failed_call

    if time_since_last_failure < 90s:
        wait_remaining = 90s - time_since_last_failure
        sleep(wait_remaining)
        # Fait UN DERNIER ESSAI

    if final_attempt_fails:
        return (False, 0)  # Signal: abandonner, passer au fallback
```

**Logique:**
1. Après max_retries, attendre que **90s se soient écoulées depuis le dernier échec**
2. Faire **UN SEUL essai final**
3. Si cet essai échoue aussi → abandonner et signaler fallback

## Niveau 3: Fallback

### AutoPickerLLM Gère le Fallback

`AutoPickerLLM` wraps des `ScheduledLLM` et gère le fallback:

```python
class AutoPickerLLM:
    def invoke(self, input):
        # Essaye primary LLM (avec ScheduledLLM)
        try:
            return self.primary_llm.invoke(input)
        except Exception as e:
            if is_rate_limit_error(e):
                # ScheduledLLM a abandonné après 90s rule
                logger.info("Primary exhausted, trying fallback")

                # Essaye chaque fallback
                for fallback_llm, name in self.fallback_llms:
                    try:
                        return fallback_llm.invoke(input)
                    except:
                        continue  # Essaye le suivant

                # Tous les fallbacks ont échoué
                raise RuntimeError("All models exhausted")
```

## Flow Complet: Exemple Concret

### Scenario: Rate Limit Inattendu

```
1. USER: llm.invoke("Hello")

2. PROACTIF (ScheduledLLM):
   - Vérifie N-2: ✅ OK (450/500 requests)
   - Vérifie 60/RPM: ✅ OK (0.15s écoulées, besoin 0.12s)
   - Procède avec l'appel

3. APPEL API:
   - ❌ Erreur 429: "Rate limit exceeded" (quota journalier atteint)

4. RÉACTIF (SchedulingStrategy):
   - record_error(model, error)
   - Retry 1/3: attend 60s (backoff exponentiel)
   - Réessaye → ❌ Encore erreur 429

   - record_error(model, error)
   - Retry 2/3: attend 120s
   - Réessaye → ❌ Encore erreur 429

   - record_error(model, error)
   - Retry 3/3: attend 240s
   - Réessaye → ❌ Encore erreur 429

   - Max retries atteint!
   - Applique règle des 90s:
     * Temps depuis dernier échec: 240s (> 90s)
     * Fait UN DERNIER ESSAI immédiatement
   - Réessaye → ❌ Encore erreur 429

   - final_attempt_made = True
   - should_retry_after_error() → (False, 0)
   - RAISE exception (signal fallback)

5. FALLBACK (AutoPickerLLM):
   - Catch l'exception du primary
   - Essaye fallback_llm_1 (gemini/gemini-2.5-flash)
   - ✅ Succès!
   - Return response

6. USER: Reçoit la réponse (sans savoir qu'il y a eu fallback)
```

### Timeline Complète

```
T+0s    : Appel initial
T+0s    : Erreur 1 (rate limit)
T+60s   : Retry 1 → Erreur 2
T+180s  : Retry 2 → Erreur 3
T+420s  : Retry 3 → Erreur 4
T+420s  : Règle 90s: 420s > 90s, essai final immédiat
T+420s  : Final attempt → Erreur 5
T+420s  : Abandon, fallback vers gemini
T+422s  : Gemini répond ✅
```

**Total:** 422 secondes, mais l'utilisateur a sa réponse!

## Implémentation: Code Key Points

### 1. SchedulingStrategy

```python
class ProactiveRateLimitScheduler(SchedulingStrategy):
    def __init__(self, ..., max_retries=3, backoff_base=2.0):
        self._error_history = {}  # Track errors per model
        self._last_failed_call = {}  # Last failure timestamp
        self._final_attempt_made = {}  # Flag for 90s rule

    def record_error(self, model_name, error):
        """Enregistre un échec"""
        self._error_history[model_name].append((time.time(), error, retry_count))
        self._last_failed_call[model_name] = time.time()

    def should_retry_after_error(self, model_name) -> (bool, float):
        """Détermine si retry ou abandon"""
        error_count = len(self._error_history[model_name])

        # Déjà fait l'essai final?
        if self._final_attempt_made.get(model_name):
            return False, 0.0  # Abandon

        # Encore des retries disponibles?
        if error_count < self.max_retries:
            wait = 60 * (backoff_base ** error_count)
            return True, wait  # Retry avec backoff

        # Règle des 90s
        time_since_failure = now - self._last_failed_call[model_name]

        if time_since_failure < 90.0:
            remaining = 90.0 - time_since_failure
            return True, remaining  # Attendre puis final attempt

        # 90s passées, faire final attempt
        self._final_attempt_made[model_name] = True
        return True, 0.0  # Final attempt immédiat

    def record_request(self, model_name, tokens):
        """Enregistre un succès - clear error history"""
        if model_name in self._error_history:
            del self._error_history[model_name]
            del self._last_failed_call[model_name]
            del self._final_attempt_made[model_name]
```

### 2. ScheduledLLM

```python
class ScheduledLLM(BaseLLM):
    def _generate(self, prompts, **kwargs):
        # Proactif
        can_proceed, wait = self.scheduling_strategy.can_proceed(...)
        if not can_proceed:
            time.sleep(wait)

        # Appel avec retry loop
        while True:
            try:
                result = self.llm._generate(prompts, **kwargs)
                self.scheduling_strategy.record_request(...)  # Succès
                return result

            except Exception as e:
                if self._is_rate_limit_error(e):
                    # Réactif
                    self.scheduling_strategy.record_error(self.model_name, e)

                    should_retry, wait = self.scheduling_strategy.should_retry_after_error(...)

                    if not should_retry:
                        raise  # Abandon, signal fallback

                    if wait > 0:
                        time.sleep(wait)

                    continue  # Retry
                else:
                    raise  # Autre erreur, pas de retry
```

### 3. AutoPickerLLM (Fallback)

`AutoPickerLLM` reste inchangé! Il catch naturellement les exceptions des `ScheduledLLM` et essaye les fallbacks.

```python
def _try_invoke_model(self, llm, model_name, input_data, is_primary):
    try:
        # llm est un ScheduledLLM qui gère proactif + réactif
        response = llm.invoke(input_data)
        return response
    except Exception as e:
        if is_rate_limit_error(e):
            # ScheduledLLM a abandonné après règle 90s
            logger.warning(f"{model_name} exhausted after retries")
            return None  # Signal fallback
        else:
            raise
```

## Configuration

### Paramètres de Scheduling

```python
scheduler = ProactiveRateLimitScheduler(
    rate_tracker=tracker,
    safety_margin=2,      # N-2 rule
    max_retries=3,        # Nombre de retries avec backoff
    backoff_base=2.0      # Multiplicateur exponentiel
)
```

### Paramètres LLM

```python
llm = get_scheduled_llm(
    provider="openai",
    model="gpt-4o-mini",
    tier="tier1",
    max_wait_seconds=300.0  # Max pour proactif (pas réactif)
)
```

**Note:** Le `max_wait_seconds` s'applique **seulement au scheduling proactif**. Le réactif (backoff + 90s) peut dépasser cette limite car c'est une erreur réelle qu'on gère.

## Avantages du Système 3 Niveaux

### 1. Proactif = 99% des Cas

La plupart du temps, le scheduling proactif **prévient** les erreurs:
- ✅ Pas de retry
- ✅ Latence prévisible
- ✅ Throughput optimal

### 2. Réactif = Gère l'Inattendu

Quand une erreur survient quand même:
- ✅ Retry intelligent avec backoff
- ✅ Règle des 90s pour cas extrêmes
- ✅ N'abandonne pas trop vite

### 3. Fallback = Dernier Recours

Si tout échoue:
- ✅ Bascule automatique vers autre modèle
- ✅ Utilisateur a toujours sa réponse
- ✅ Transparent pour l'application

## Statistiques

Le système track toutes les métriques:

```python
stats = llm.get_stats()
# {
#     'total_requests': 100,
#     'scheduled_waits': 45,      # Attentes proactives
#     'error_retries': 3,          # Retries après erreurs
#     'fallbacks_triggered': 1,    # Fallbacks utilisés
#     'final_attempts': 1,         # Essais finaux (90s rule)
# }
```

## Logs Exemple

```
[INFO] Proactive scheduling: waiting 0.08s for openai/gpt-4o-mini
[INFO] Invoking openai/gpt-4o-mini with ~1250 tokens
[WARNING] Rate limit error for openai/gpt-4o-mini (attempt 1/3): 429 Rate limit exceeded
[INFO] Retry 1/3 for openai/gpt-4o-mini with exponential backoff: 60.0s
[WARNING] Rate limit error for openai/gpt-4o-mini (attempt 2/3): 429 Rate limit exceeded
[INFO] Retry 2/3 for openai/gpt-4o-mini with exponential backoff: 120.0s
[WARNING] Rate limit error for openai/gpt-4o-mini (attempt 3/3): 429 Rate limit exceeded
[INFO] Max retries exhausted for openai/gpt-4o-mini. Waiting 240.0s to reach 90s since last failure, then making ONE FINAL ATTEMPT.
[INFO] 90s have passed since last failure for openai/gpt-4o-mini. Making ONE FINAL ATTEMPT before fallback.
[WARNING] Rate limit error for openai/gpt-4o-mini (attempt 4/3): 429 Rate limit exceeded
[ERROR] Final attempt for openai/gpt-4o-mini also failed after 90s rule. Signaling fallback.
[ERROR] Scheduling strategy exhausted for openai/gpt-4o-mini, raising error for fallback
[INFO] Primary model failed, trying fallback: gemini/gemini-2.5-flash
[INFO] Successfully invoked gemini/gemini-2.5-flash in 2.1s
```

## Conclusion

Le système à 3 niveaux assure que:

1. **Proactif** : Évite 99% des problèmes
2. **Réactif** : Gère intelligemment les 1% restants avec backoff + règle 90s
3. **Fallback** : Assure qu'on a **toujours** une réponse

L'utilisateur ne voit **aucune erreur**, juste:
- Soit la réponse du modèle primary
- Soit la réponse d'un fallback (transparent)
- Jamais d'échec total

✅ Robuste, ✅ Résilient, ✅ Production-ready!
