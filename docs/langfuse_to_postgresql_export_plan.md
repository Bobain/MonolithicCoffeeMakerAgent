# Plan: Export Langfuse Traces vers Base de Données Locale

## 🎯 Objectif

Créer un système d'export automatique des métriques Langfuse (traces LLM, coûts, métadonnées) vers une base de données locale (SQLite par défaut, PostgreSQL optionnel) pour :
- **Analyse de performance des LLMs** - Comparer latence, coûts, qualité entre modèles
- **Analyse de performance des prompts** - Mesurer l'efficacité de différentes formulations
- **Analyse de performance des agents** - Mesurer la réussite des tâches assignées
- **Reporting personnalisé** - Créer des dashboards et rapports adaptés
- **Archivage local** - Conserver l'historique sans dépendre du cloud
- **Requêtes SQL optimisées** - Analyses complexes sans impacter Langfuse

### Pourquoi SQLite (par défaut) ?
- ✅ **Zero configuration** - Un simple fichier `.db`, pas de serveur à configurer
- ✅ **Portable** - La base suit le projet (commit dans Git si petit volume)
- ✅ **Léger** - Parfait pour projets individuels et petites équipes
- ✅ **Migration facile** - Passage vers PostgreSQL simple si besoin de scale

### Quand utiliser PostgreSQL ?
- Grande volumétrie (>100k traces)
- Accès concurrent multiple
- Intégration avec outils BI enterprise
- Déploiement multi-serveur

---

## 📊 Contexte: Données Langfuse actuelles

### Données disponibles dans Langfuse

D'après l'intégration actuelle (voir `auto_picker_llm_refactored.py`, `langfuse_cost_queries.md`), le projet log déjà vers Langfuse :

#### 1. **Generations** (appels LLM)
```python
langfuse_client.generation(
    name=f"llm_call_{model_name.replace('/', '_')}",
    model=model_name,
    usage={
        "input": input_tokens,
        "output": output_tokens,
        "total": input_tokens + output_tokens,
    },
    metadata={
        "cost_usd": cost_info["total_cost"],
        "input_cost_usd": cost_info["input_cost"],
        "output_cost_usd": cost_info["output_cost"],
        "is_primary": is_primary,
        "latency_seconds": latency,
    },
)
```

#### 2. **Events** (fallbacks, erreurs)
```python
# Rate limit fallback
langfuse_client.event(
    name="rate_limit_fallback",
    metadata={
        "original_model": self.primary_model_name,
        "fallback_model": next_fallback_name,
        "reason": str(error),
    },
)

# Context length fallback
langfuse_client.event(
    name="context_length_fallback",
    metadata={
        "original_model": model_name,
        "fallback_model": large_model_name,
        "estimated_tokens": estimated_tokens,
        "original_max_context": max_context,
        "fallback_max_context": fallback_max_context,
    },
)
```

#### 3. **Traces** (stack d'appel complet)
- Langfuse trace automatiquement la stack d'appel complète
- Inclut les `trace_id`, `observation_id`, `parent_observation_id`
- Relie les generations aux événements

---

## 🗄️ Architecture de la solution

### Composants

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Python                       │
│              (AutoPickerLLM, Agents, etc.)                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │    Langfuse     │  ◄─── Stockage primaire (Cloud)
        │   (Cloud SaaS)  │
        └────────┬───────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │ Langfuse Export Service │  ◄─── Notre nouveau module
        │   (Scheduled job)       │
        └────────┬────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │   SQLite Database      │  ◄─── Base locale pour analytics
        │ (llm_metrics.db)       │       (PostgreSQL optionnel)
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────────────┐
        │  Analytics & Performance       │
        │  - LLM benchmarking            │
        │  - Prompt A/B testing          │
        │  - Agent task success rate     │
        │  - Cost optimization           │
        └────────────────────────────────┘
```

---

## 📁 Structure du module

### Nouveau package: `coffee_maker/langchain_observe/analytics/`

```
coffee_maker/langchain_observe/analytics/
├── __init__.py
├── exporter.py                # Export Langfuse → SQLite/PostgreSQL
├── db_schema.py               # Schémas SQL et modèles SQLAlchemy
├── performance_analyzer.py    # Analyse de performance (LLM, prompts, agents)
├── config.py                  # Configuration de connexion
└── metrics/
    ├── __init__.py
    ├── llm_metrics.py         # Métriques de performance LLM
    ├── prompt_metrics.py      # Métriques d'efficacité des prompts
    └── agent_metrics.py       # Métriques de succès des agents
```

### Scripts associés:

```
scripts/
├── export_langfuse_data.py    # Script CLI pour export manuel
├── setup_metrics_db.py        # Setup initial de la DB (SQLite par défaut)
├── analyze_llm_performance.py # Analyse de performance des LLMs
└── benchmark_prompts.py       # Comparaison de prompts
```

---

## 🗃️ Schéma de Base de Données (SQLite/PostgreSQL)

### Vue d'ensemble

La base de données sert **deux objectifs complémentaires** :
1. **📊 Analytics** - Stocker l'historique des traces Langfuse pour analyse
2. **⏱️ Rate Limiting** - Stocker les compteurs pour le scheduling temps réel des LLMs

### 1. Table `llm_generations`
Stocke tous les appels LLM avec leurs métriques (Analytics).

```sql
CREATE TABLE llm_generations (
    -- Identifiants
    id UUID PRIMARY KEY,
    trace_id UUID NOT NULL,
    observation_id UUID,
    parent_observation_id UUID,

    -- Timing
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    latency_seconds DECIMAL(10, 4),

    -- Modèle et version
    model VARCHAR(255) NOT NULL,
    model_version VARCHAR(100),
    provider VARCHAR(50),  -- openai, gemini, anthropic

    -- Tokens
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,

    -- Coûts
    cost_usd DECIMAL(12, 6),
    input_cost_usd DECIMAL(12, 6),
    output_cost_usd DECIMAL(12, 6),

    -- Contexte d'exécution
    is_primary BOOLEAN DEFAULT true,
    tier VARCHAR(50),  -- tier1, tier2, etc.

    -- Prompt & Output
    prompt_text TEXT,
    prompt_tokens_estimate INTEGER,
    completion_text TEXT,

    -- Métadonnées (JSONB pour flexibilité)
    metadata JSONB,

    -- Indexation
    INDEX idx_trace_id (trace_id),
    INDEX idx_created_at (created_at),
    INDEX idx_model (model),
    INDEX idx_provider (provider),
    INDEX idx_cost (cost_usd),
    INDEX idx_metadata_gin (metadata) USING GIN
);
```

### 2. Table `llm_traces`
Représente une trace complète (stack d'appel).

```sql
CREATE TABLE llm_traces (
    -- Identifiants
    id UUID PRIMARY KEY,
    trace_id UUID UNIQUE NOT NULL,

    -- Timing
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Attribution
    user_id VARCHAR(255),
    session_id VARCHAR(255),

    -- Context
    name VARCHAR(255),  -- Nom de la trace (ex: "code_review_agent")
    tags TEXT[],

    -- Métriques agrégées
    total_cost_usd DECIMAL(12, 6),
    total_tokens INTEGER,
    total_generations INTEGER,
    total_events INTEGER,

    -- Métadonnées
    metadata JSONB,

    -- Indexation
    INDEX idx_trace_id (trace_id),
    INDEX idx_created_at (created_at),
    INDEX idx_name (name),
    INDEX idx_tags_gin (tags) USING GIN
);
```

### 3. Table `llm_events`
Stocke les événements (fallbacks, erreurs, etc.).

```sql
CREATE TABLE llm_events (
    -- Identifiants
    id UUID PRIMARY KEY,
    trace_id UUID,
    observation_id UUID,

    -- Timing
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Type d'événement
    event_name VARCHAR(100) NOT NULL,  -- rate_limit_fallback, context_length_fallback, etc.
    event_type VARCHAR(50),  -- fallback, error, info, etc.

    -- Contexte de fallback
    original_model VARCHAR(255),
    fallback_model VARCHAR(255),
    fallback_reason TEXT,

    -- Contexte spécifique
    estimated_tokens INTEGER,
    original_max_context INTEGER,
    fallback_max_context INTEGER,

    -- Métadonnées complètes
    metadata JSONB,

    -- Indexation
    INDEX idx_trace_id (trace_id),
    INDEX idx_event_name (event_name),
    INDEX idx_created_at (created_at),
    INDEX idx_original_model (original_model)
);
```

### 4. Table `export_metadata`
Tracking de l'état des exports (Analytics).

```sql
CREATE TABLE export_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SERIAL → INTEGER AUTOINCREMENT pour SQLite
    export_run_id TEXT UNIQUE NOT NULL,    -- UUID → TEXT pour SQLite
    export_started_at TIMESTAMP NOT NULL,
    export_completed_at TIMESTAMP,

    -- Période exportée
    data_start_time TIMESTAMP,
    data_end_time TIMESTAMP,

    -- Statistiques
    generations_exported INTEGER DEFAULT 0,
    traces_exported INTEGER DEFAULT 0,
    events_exported INTEGER DEFAULT 0,

    -- Statut
    status VARCHAR(50),  -- running, completed, failed
    error_message TEXT,

    -- Configuration
    langfuse_project_id VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_export_run_id ON export_metadata(export_run_id);
CREATE INDEX IF NOT EXISTS idx_export_started_at ON export_metadata(export_started_at);
```

---

## 🔢 Schéma Rate Limiting (Temps Réel)

### 5. Table `rate_limit_counters`
Compteurs pour respecter les limites d'API (Rate Limiting).

**🔐 Partage multi-process** : Cette table utilise SQLite comme source unique de vérité.
Tous les process qui instancient le même modèle partageront les mêmes compteurs grâce au verrouillage de fichier SQLite (WAL mode recommandé).

```sql
CREATE TABLE rate_limit_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider VARCHAR(50) NOT NULL,      -- openai, gemini, anthropic
    model VARCHAR(255) NOT NULL,        -- gpt-4o-mini, gemini-2.5-flash, etc.
    tier VARCHAR(50) NOT NULL,          -- tier1, tier2, tier3

    -- Fenêtre de temps
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    window_type VARCHAR(20),            -- minute, hour, day

    -- Compteurs (mis à jour atomiquement via transactions)
    request_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,

    -- Limites configurées
    request_limit INTEGER,
    token_limit INTEGER,

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Index composé pour recherche rapide
    UNIQUE(provider, model, tier, window_type, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_lookup
    ON rate_limit_counters(provider, model, tier, window_type, window_start);
CREATE INDEX IF NOT EXISTS idx_rate_limit_window_end
    ON rate_limit_counters(window_end);

-- Active le mode WAL pour meilleures performances en multi-process
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;  -- Attend 5s si DB verrouillée
```

**Exemple d'utilisation atomique** :
```python
# Incrémenter le compteur de manière thread-safe
with transaction():
    counter = session.query(RateLimitCounter).filter_by(
        provider="openai",
        model="gpt-4o-mini",
        tier="tier1",
        window_type="minute",
        window_start=current_minute_start
    ).with_for_update().first()  # Lock pessimiste

    if counter.request_count < counter.request_limit:
        counter.request_count += 1
        counter.token_count += estimated_tokens
        counter.updated_at = datetime.now()
        session.commit()
        return True  # OK, request autorisée
    else:
        return False  # Rate limit atteint
```

### 6. Table `scheduled_requests`
File d'attente des requêtes LLM plannifiées (Rate Limiting).

```sql
CREATE TABLE scheduled_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT UNIQUE NOT NULL,

    -- LLM cible
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(255) NOT NULL,
    tier VARCHAR(50) NOT NULL,

    -- Timing
    scheduled_time TIMESTAMP NOT NULL,
    actual_execution_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Priorité
    priority INTEGER DEFAULT 0,

    -- Statut
    status VARCHAR(50) DEFAULT 'pending',  -- pending, executing, completed, failed

    -- Estimation
    estimated_tokens INTEGER,

    -- Résultat
    execution_result TEXT,
    error_message TEXT,

    INDEX idx_scheduled_time (scheduled_time),
    INDEX idx_status (status),
    INDEX idx_provider_model (provider, model, tier)
);

CREATE INDEX IF NOT EXISTS idx_scheduled_lookup
    ON scheduled_requests(provider, model, tier, status, scheduled_time);
```

### 7. Table `agent_task_results`
Résultats des tâches agents pour mesurer la performance (Analytics + Rate Limiting).

```sql
CREATE TABLE agent_task_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    trace_id TEXT,  -- Lien vers llm_traces

    -- Agent info
    agent_name VARCHAR(255) NOT NULL,
    agent_version VARCHAR(50),

    -- Task info
    task_type VARCHAR(100),
    task_description TEXT,

    -- Timing
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds REAL,

    -- Performance
    success BOOLEAN,
    quality_score REAL,           -- Note de qualité (0-1)
    confidence_score REAL,        -- Confiance dans le résultat (0-1)

    -- Ressources utilisées
    total_cost_usd REAL,
    total_tokens INTEGER,
    llm_calls_count INTEGER,
    fallback_count INTEGER,

    -- Résultat
    result_data TEXT,             -- JSON avec résultat détaillé
    error_message TEXT,

    -- Métadonnées
    metadata TEXT,                -- JSON pour flexibilité

    INDEX idx_agent_name (agent_name),
    INDEX idx_task_type (task_type),
    INDEX idx_success (success),
    INDEX idx_started_at (started_at)
);

CREATE INDEX IF NOT EXISTS idx_agent_performance
    ON agent_task_results(agent_name, task_type, success, started_at);
```

### 8. Table `prompt_variants`
Versions de prompts pour A/B testing (Analytics).

```sql
CREATE TABLE prompt_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id TEXT UNIQUE NOT NULL,

    -- Identification
    prompt_name VARCHAR(255) NOT NULL,
    variant_name VARCHAR(100),    -- "v1", "v2", "control", "experiment_a", etc.
    version INTEGER,

    -- Contenu
    prompt_template TEXT NOT NULL,
    prompt_variables TEXT,        -- JSON avec liste des variables

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    description TEXT,
    tags TEXT,                    -- JSON array

    -- Statut
    is_active BOOLEAN DEFAULT 1,
    is_default BOOLEAN DEFAULT 0,

    INDEX idx_prompt_name (prompt_name),
    INDEX idx_variant_name (variant_name),
    INDEX idx_active (is_active)
);
```

### 9. Table `prompt_executions`
Exécutions de prompts pour mesurer leur efficacité (Analytics).

```sql
CREATE TABLE prompt_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE NOT NULL,
    prompt_id TEXT NOT NULL,      -- FK vers prompt_variants
    trace_id TEXT,                -- FK vers llm_traces

    -- LLM utilisé
    provider VARCHAR(50),
    model VARCHAR(255),

    -- Timing
    executed_at TIMESTAMP NOT NULL,
    latency_seconds REAL,

    -- Tokens & Coûts
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL,

    -- Performance
    success BOOLEAN,
    quality_score REAL,           -- Évaluation de qualité de la réponse
    user_feedback REAL,           -- Feedback utilisateur (optionnel)

    -- Résultat
    output_text TEXT,
    metadata TEXT,                -- JSON

    INDEX idx_prompt_id (prompt_id),
    INDEX idx_executed_at (executed_at),
    INDEX idx_success (success),
    FOREIGN KEY (prompt_id) REFERENCES prompt_variants(prompt_id)
);

CREATE INDEX IF NOT EXISTS idx_prompt_performance
    ON prompt_executions(prompt_id, success, executed_at);
```

---

## 🔧 Implémentation

### 1. Configuration (`config.py`)

```python
"""Configuration for Langfuse → PostgreSQL export."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class ExportConfig:
    """Configuration for Langfuse export."""

    # Langfuse credentials
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str = "https://cloud.langfuse.com"

    # PostgreSQL connection
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "llm_metrics"
    postgres_user: str
    postgres_password: str

    # Export settings
    export_batch_size: int = 1000
    export_interval_minutes: int = 30
    lookback_hours: int = 24

    @classmethod
    def from_env(cls) -> "ExportConfig":
        """Load configuration from environment variables."""
        return cls(
            langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_database=os.getenv("POSTGRES_DATABASE", "llm_metrics"),
            postgres_user=os.getenv("POSTGRES_USER"),
            postgres_password=os.getenv("POSTGRES_PASSWORD"),
            export_batch_size=int(os.getenv("EXPORT_BATCH_SIZE", "1000")),
            export_interval_minutes=int(os.getenv("EXPORT_INTERVAL_MINUTES", "30")),
            lookback_hours=int(os.getenv("EXPORT_LOOKBACK_HOURS", "24")),
        )

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        )
```

### 2. Schéma SQLAlchemy (`postgres_schema.py`)

```python
"""SQLAlchemy models for LLM metrics warehouse."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LLMGeneration(Base):
    """LLM generation record."""

    __tablename__ = "llm_generations"

    # Identifiants
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    trace_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    observation_id = Column(PG_UUID(as_uuid=True))
    parent_observation_id = Column(PG_UUID(as_uuid=True))

    # Timing
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    latency_seconds = Column(Numeric(10, 4))

    # Modèle
    model = Column(String(255), nullable=False, index=True)
    model_version = Column(String(100))
    provider = Column(String(50), index=True)

    # Tokens
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)

    # Coûts
    cost_usd = Column(Numeric(12, 6), index=True)
    input_cost_usd = Column(Numeric(12, 6))
    output_cost_usd = Column(Numeric(12, 6))

    # Contexte
    is_primary = Column(Boolean, default=True)
    tier = Column(String(50))

    # Contenu
    prompt_text = Column(Text)
    prompt_tokens_estimate = Column(Integer)
    completion_text = Column(Text)

    # Métadonnées
    metadata = Column(JSONB)

    __table_args__ = (
        Index("idx_metadata_gin", "metadata", postgresql_using="gin"),
    )


class LLMTrace(Base):
    """LLM trace (complete call stack)."""

    __tablename__ = "llm_traces"

    # Identifiants
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    trace_id = Column(PG_UUID(as_uuid=True), unique=True, nullable=False)

    # Timing
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True))

    # Attribution
    user_id = Column(String(255))
    session_id = Column(String(255))

    # Context
    name = Column(String(255), index=True)
    tags = Column(ARRAY(Text))

    # Métriques agrégées
    total_cost_usd = Column(Numeric(12, 6))
    total_tokens = Column(Integer)
    total_generations = Column(Integer)
    total_events = Column(Integer)

    # Métadonnées
    metadata = Column(JSONB)

    __table_args__ = (
        Index("idx_tags_gin", "tags", postgresql_using="gin"),
    )


class LLMEvent(Base):
    """LLM event (fallback, error, etc.)."""

    __tablename__ = "llm_events"

    # Identifiants
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    trace_id = Column(PG_UUID(as_uuid=True), index=True)
    observation_id = Column(PG_UUID(as_uuid=True))

    # Timing
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Type
    event_name = Column(String(100), nullable=False, index=True)
    event_type = Column(String(50))

    # Fallback context
    original_model = Column(String(255), index=True)
    fallback_model = Column(String(255))
    fallback_reason = Column(Text)

    # Context spécifique
    estimated_tokens = Column(Integer)
    original_max_context = Column(Integer)
    fallback_max_context = Column(Integer)

    # Métadonnées
    metadata = Column(JSONB)


class ExportMetadata(Base):
    """Export run metadata."""

    __tablename__ = "export_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    export_run_id = Column(PG_UUID(as_uuid=True), unique=True, nullable=False)
    export_started_at = Column(DateTime(timezone=True), nullable=False)
    export_completed_at = Column(DateTime(timezone=True))

    # Période
    data_start_time = Column(DateTime(timezone=True))
    data_end_time = Column(DateTime(timezone=True))

    # Stats
    generations_exported = Column(Integer, default=0)
    traces_exported = Column(Integer, default=0)
    events_exported = Column(Integer, default=0)

    # Status
    status = Column(String(50))
    error_message = Column(Text)

    # Config
    langfuse_project_id = Column(String(255))
```

### 3. Exporter principal (`langfuse_exporter.py`)

```python
"""Export Langfuse data to PostgreSQL warehouse."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import langfuse
from langfuse.model import Trace, Generation, Event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from coffee_maker.langchain_observe.exporters.config import ExportConfig
from coffee_maker.langchain_observe.exporters.postgres_schema import (
    Base,
    LLMGeneration,
    LLMTrace,
    LLMEvent,
    ExportMetadata,
)

logger = logging.getLogger(__name__)


class LangfuseExporter:
    """Export Langfuse traces to PostgreSQL."""

    def __init__(self, config: ExportConfig):
        """Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config

        # Initialize Langfuse client
        self.langfuse_client = langfuse.Langfuse(
            public_key=config.langfuse_public_key,
            secret_key=config.langfuse_secret_key,
            host=config.langfuse_host,
        )

        # Initialize PostgreSQL connection
        self.engine = create_engine(config.postgres_url)
        self.Session = sessionmaker(bind=self.engine)

    def setup_database(self):
        """Create database tables if they don't exist."""
        logger.info("Setting up database schema...")
        Base.metadata.create_all(self.engine)
        logger.info("Database schema created successfully")

    def export_traces(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Export traces from Langfuse to PostgreSQL.

        Args:
            start_time: Start of time range (default: 24h ago)
            end_time: End of time range (default: now)

        Returns:
            Dictionary with export statistics
        """
        # Default time range
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=self.config.lookback_hours)

        # Create export run metadata
        export_run_id = uuid.uuid4()
        logger.info(f"Starting export run {export_run_id}")
        logger.info(f"Time range: {start_time} → {end_time}")

        session = self.Session()
        export_meta = ExportMetadata(
            export_run_id=export_run_id,
            export_started_at=datetime.now(),
            data_start_time=start_time,
            data_end_time=end_time,
            status="running",
            langfuse_project_id=self.config.langfuse_public_key[:8],
        )
        session.add(export_meta)
        session.commit()

        try:
            # Fetch traces from Langfuse
            logger.info("Fetching traces from Langfuse...")
            traces = self._fetch_traces(start_time, end_time)
            logger.info(f"Fetched {len(traces)} traces")

            # Export traces
            traces_count = self._export_traces_batch(session, traces)
            logger.info(f"Exported {traces_count} traces")

            # Fetch and export generations
            logger.info("Fetching generations from Langfuse...")
            generations = self._fetch_generations(start_time, end_time)
            logger.info(f"Fetched {len(generations)} generations")

            generations_count = self._export_generations_batch(session, generations)
            logger.info(f"Exported {generations_count} generations")

            # Fetch and export events
            logger.info("Fetching events from Langfuse...")
            events = self._fetch_events(start_time, end_time)
            logger.info(f"Fetched {len(events)} events")

            events_count = self._export_events_batch(session, events)
            logger.info(f"Exported {events_count} events")

            # Update export metadata
            export_meta.export_completed_at = datetime.now()
            export_meta.traces_exported = traces_count
            export_meta.generations_exported = generations_count
            export_meta.events_exported = events_count
            export_meta.status = "completed"
            session.commit()

            stats = {
                "traces": traces_count,
                "generations": generations_count,
                "events": events_count,
            }
            logger.info(f"Export completed successfully: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Export failed: {e}")
            export_meta.status = "failed"
            export_meta.error_message = str(e)
            session.commit()
            raise
        finally:
            session.close()

    def _fetch_traces(
        self, start_time: datetime, end_time: datetime
    ) -> List[Trace]:
        """Fetch traces from Langfuse."""
        # Note: Langfuse API methods might differ, adapt as needed
        traces = self.langfuse_client.get_traces(
            from_timestamp=start_time,
            to_timestamp=end_time,
            limit=10000,  # Adjust based on API limits
        )
        return traces

    def _fetch_generations(
        self, start_time: datetime, end_time: datetime
    ) -> List[Generation]:
        """Fetch generations from Langfuse."""
        generations = self.langfuse_client.get_generations(
            from_timestamp=start_time,
            to_timestamp=end_time,
            limit=10000,
        )
        return generations

    def _fetch_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[Event]:
        """Fetch events from Langfuse."""
        # Filter for our custom events
        events = self.langfuse_client.get_events(
            from_timestamp=start_time,
            to_timestamp=end_time,
            limit=10000,
        )
        # Filter for fallback events
        return [
            e for e in events
            if e.name in ("rate_limit_fallback", "context_length_fallback", "fallback_success")
        ]

    def _export_traces_batch(
        self, session, traces: List[Trace]
    ) -> int:
        """Export a batch of traces to PostgreSQL."""
        count = 0
        for trace in traces:
            # Check if trace already exists (upsert)
            existing = session.query(LLMTrace).filter_by(
                trace_id=trace.id
            ).first()

            if existing:
                # Update existing trace
                self._update_trace_record(existing, trace)
            else:
                # Create new trace
                trace_record = self._convert_trace(trace)
                session.add(trace_record)

            count += 1

        session.commit()
        return count

    def _export_generations_batch(
        self, session, generations: List[Generation]
    ) -> int:
        """Export a batch of generations to PostgreSQL."""
        count = 0
        for gen in generations:
            # Check if generation already exists
            existing = session.query(LLMGeneration).filter_by(
                id=gen.id
            ).first()

            if existing:
                self._update_generation_record(existing, gen)
            else:
                gen_record = self._convert_generation(gen)
                session.add(gen_record)

            count += 1

        session.commit()
        return count

    def _export_events_batch(
        self, session, events: List[Event]
    ) -> int:
        """Export a batch of events to PostgreSQL."""
        count = 0
        for event in events:
            # Check if event already exists
            existing = session.query(LLMEvent).filter_by(
                id=event.id
            ).first()

            if not existing:
                event_record = self._convert_event(event)
                session.add(event_record)
                count += 1

        session.commit()
        return count

    def _convert_trace(self, trace: Trace) -> LLMTrace:
        """Convert Langfuse Trace to LLMTrace model."""
        return LLMTrace(
            id=trace.id,
            trace_id=trace.id,
            created_at=trace.timestamp,
            updated_at=getattr(trace, "updated_at", None),
            user_id=getattr(trace, "user_id", None),
            session_id=getattr(trace, "session_id", None),
            name=getattr(trace, "name", None),
            tags=getattr(trace, "tags", []),
            metadata=getattr(trace, "metadata", {}),
            # Aggregate stats will be computed via SQL views
        )

    def _convert_generation(self, gen: Generation) -> LLMGeneration:
        """Convert Langfuse Generation to LLMGeneration model."""
        metadata = gen.metadata or {}
        usage = gen.usage or {}

        # Extract provider from model name
        provider = None
        if gen.model:
            if "/" in gen.model:
                provider = gen.model.split("/")[0]

        return LLMGeneration(
            id=gen.id,
            trace_id=gen.trace_id,
            observation_id=getattr(gen, "observation_id", None),
            parent_observation_id=getattr(gen, "parent_observation_id", None),
            created_at=gen.start_time or gen.timestamp,
            updated_at=getattr(gen, "updated_at", None),
            start_time=gen.start_time,
            end_time=gen.end_time,
            latency_seconds=metadata.get("latency_seconds"),
            model=gen.model,
            model_version=getattr(gen, "model_version", None),
            provider=provider,
            input_tokens=usage.get("input"),
            output_tokens=usage.get("output"),
            total_tokens=usage.get("total"),
            cost_usd=metadata.get("cost_usd"),
            input_cost_usd=metadata.get("input_cost_usd"),
            output_cost_usd=metadata.get("output_cost_usd"),
            is_primary=metadata.get("is_primary", True),
            tier=metadata.get("tier"),
            prompt_text=getattr(gen, "input", None),
            completion_text=getattr(gen, "output", None),
            metadata=metadata,
        )

    def _convert_event(self, event: Event) -> LLMEvent:
        """Convert Langfuse Event to LLMEvent model."""
        metadata = event.metadata or {}

        return LLMEvent(
            id=event.id,
            trace_id=event.trace_id,
            observation_id=getattr(event, "observation_id", None),
            created_at=event.timestamp,
            event_name=event.name,
            event_type="fallback" if "fallback" in event.name else "info",
            original_model=metadata.get("original_model"),
            fallback_model=metadata.get("fallback_model"),
            fallback_reason=metadata.get("reason"),
            estimated_tokens=metadata.get("estimated_tokens"),
            original_max_context=metadata.get("original_max_context"),
            fallback_max_context=metadata.get("fallback_max_context"),
            metadata=metadata,
        )

    def _update_trace_record(self, record: LLMTrace, trace: Trace):
        """Update existing trace record."""
        record.updated_at = datetime.now()
        record.metadata = getattr(trace, "metadata", {})
        # Update other mutable fields as needed

    def _update_generation_record(self, record: LLMGeneration, gen: Generation):
        """Update existing generation record."""
        record.updated_at = datetime.now()
        # Update mutable fields if needed
```

### 4. Script CLI (`scripts/export_langfuse_data.py`)

```python
#!/usr/bin/env python3
"""CLI script to export Langfuse data to PostgreSQL."""

import argparse
import logging
from datetime import datetime, timedelta

from coffee_maker.langchain_observe.exporters.config import ExportConfig
from coffee_maker.langchain_observe.exporters.langfuse_exporter import LangfuseExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Run export."""
    parser = argparse.ArgumentParser(
        description="Export Langfuse data to PostgreSQL"
    )
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Setup database schema (run once)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)",
    )
    parser.add_argument(
        "--start-time",
        type=str,
        help="Start time (ISO format: 2025-01-01T00:00:00)",
    )
    parser.add_argument(
        "--end-time",
        type=str,
        help="End time (ISO format: 2025-01-01T23:59:59)",
    )

    args = parser.parse_args()

    # Load configuration
    config = ExportConfig.from_env()
    exporter = LangfuseExporter(config)

    # Setup database if requested
    if args.setup_db:
        logger.info("Setting up database...")
        exporter.setup_database()
        logger.info("Database setup complete")
        return

    # Parse time range
    if args.start_time:
        start_time = datetime.fromisoformat(args.start_time)
    else:
        start_time = datetime.now() - timedelta(hours=args.hours)

    if args.end_time:
        end_time = datetime.fromisoformat(args.end_time)
    else:
        end_time = datetime.now()

    # Run export
    logger.info(f"Exporting data from {start_time} to {end_time}")
    stats = exporter.export_traces(start_time, end_time)
    logger.info(f"Export complete: {stats}")


if __name__ == "__main__":
    main()
```

---

## 📊 Requêtes SQL utiles

### 1. Coût total par modèle (derniers 7 jours)
```sql
SELECT
    provider,
    model,
    COUNT(*) as total_calls,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(cost_usd) as total_cost_usd,
    AVG(latency_seconds) as avg_latency_sec
FROM llm_generations
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY provider, model
ORDER BY total_cost_usd DESC;
```

### 2. Taux de fallback par modèle
```sql
WITH fallback_counts AS (
    SELECT
        original_model,
        COUNT(*) as fallback_count
    FROM llm_events
    WHERE event_name IN ('rate_limit_fallback', 'context_length_fallback')
        AND created_at >= NOW() - INTERVAL '7 days'
    GROUP BY original_model
),
total_calls AS (
    SELECT
        model,
        COUNT(*) as total_count
    FROM llm_generations
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY model
)
SELECT
    t.model,
    t.total_count,
    COALESCE(f.fallback_count, 0) as fallback_count,
    ROUND(COALESCE(f.fallback_count, 0)::NUMERIC / t.total_count * 100, 2) as fallback_rate_pct
FROM total_calls t
LEFT JOIN fallback_counts f ON t.model = f.original_model
ORDER BY fallback_rate_pct DESC;
```

### 3. Stack trace complète avec coûts
```sql
SELECT
    t.name as trace_name,
    t.created_at,
    COUNT(g.id) as generation_count,
    SUM(g.cost_usd) as total_cost,
    ARRAY_AGG(DISTINCT g.model) as models_used,
    COUNT(e.id) as event_count
FROM llm_traces t
LEFT JOIN llm_generations g ON t.trace_id = g.trace_id
LEFT JOIN llm_events e ON t.trace_id = e.trace_id
WHERE t.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY t.id, t.name, t.created_at
ORDER BY total_cost DESC
LIMIT 20;
```

---

## 🔄 Automatisation

### Service de synchronisation périodique

**Créer**: `scripts/export_service.py`

```python
#!/usr/bin/env python3
"""Background service to continuously export Langfuse data."""

import logging
import time
from datetime import datetime, timedelta

from coffee_maker.langchain_observe.exporters.config import ExportConfig
from coffee_maker.langchain_observe.exporters.langfuse_exporter import LangfuseExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_export_service():
    """Run continuous export service."""
    config = ExportConfig.from_env()
    exporter = LangfuseExporter(config)

    logger.info("Starting Langfuse export service")
    logger.info(f"Export interval: {config.export_interval_minutes} minutes")

    # Track last export time
    last_export = datetime.now() - timedelta(hours=config.lookback_hours)

    while True:
        try:
            # Export since last run
            end_time = datetime.now()
            start_time = last_export

            logger.info(f"Running export: {start_time} → {end_time}")
            stats = exporter.export_traces(start_time, end_time)
            logger.info(f"Export completed: {stats}")

            # Update last export time
            last_export = end_time

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)

        # Sleep until next run
        sleep_seconds = config.export_interval_minutes * 60
        logger.info(f"Sleeping for {sleep_seconds}s until next export")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    run_export_service()
```

### Docker Compose pour déploiement

**Créer**: `docker-compose.langfuse-export.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: llm_metrics
      POSTGRES_USER: llm_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U llm_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  langfuse_exporter:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DATABASE: llm_metrics
      POSTGRES_USER: llm_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      EXPORT_INTERVAL_MINUTES: 30
      EXPORT_LOOKBACK_HOURS: 1
    depends_on:
      postgres:
        condition: service_healthy
    command: python scripts/export_service.py
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 📦 Dépendances à ajouter

### Dans `pyproject.toml`:

```toml
[tool.poetry.dependencies]
# ... existing dependencies ...
sqlalchemy = "^2.0"  # Already installed
psycopg2-binary = "^2.9"  # PostgreSQL adapter
alembic = "^1.13"  # Database migrations (optional)

[tool.poetry.group.dev.dependencies]
# ... existing dependencies ...
```

### Variables d'environnement (`.env.example`):

```bash
# Langfuse credentials
export LANGFUSE_PUBLIC_KEY="pk-lf-xxx"
export LANGFUSE_SECRET_KEY="sk-lf-xxx"
export LANGFUSE_HOST="https://cloud.langfuse.com"

# PostgreSQL warehouse
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DATABASE="llm_metrics"
export POSTGRES_USER="llm_user"
export POSTGRES_PASSWORD="your_secure_password"

# Export configuration
export EXPORT_BATCH_SIZE="1000"
export EXPORT_INTERVAL_MINUTES="30"
export EXPORT_LOOKBACK_HOURS="24"
```

---

## 🧪 Tests

### Test unitaire pour l'exporter

**Créer**: `tests/unit/test_langfuse_exporter.py`

```python
"""Tests for Langfuse exporter."""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from coffee_maker.langchain_observe.exporters.config import ExportConfig
from coffee_maker.langchain_observe.exporters.langfuse_exporter import LangfuseExporter
from coffee_maker.langchain_observe.exporters.postgres_schema import Base


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture
def mock_config():
    """Mock export configuration."""
    return ExportConfig(
        langfuse_public_key="test_pk",
        langfuse_secret_key="test_sk",
        postgres_user="test",
        postgres_password="test",
    )


def test_convert_generation(mock_config):
    """Test generation conversion."""
    exporter = LangfuseExporter(mock_config)

    # Mock Langfuse Generation object
    mock_gen = Mock()
    mock_gen.id = uuid.uuid4()
    mock_gen.trace_id = uuid.uuid4()
    mock_gen.timestamp = datetime.now()
    mock_gen.start_time = datetime.now()
    mock_gen.end_time = None
    mock_gen.model = "openai/gpt-4o-mini"
    mock_gen.usage = {"input": 100, "output": 50, "total": 150}
    mock_gen.metadata = {
        "cost_usd": 0.0012,
        "is_primary": True,
        "latency_seconds": 1.5,
    }

    # Convert
    result = exporter._convert_generation(mock_gen)

    # Assertions
    assert result.id == mock_gen.id
    assert result.model == "openai/gpt-4o-mini"
    assert result.provider == "openai"
    assert result.input_tokens == 100
    assert result.output_tokens == 50
    assert float(result.cost_usd) == 0.0012
    assert result.is_primary is True
```

---

## ✅ Checklist d'implémentation

### Phase 1: Setup (2-3h)
- [ ] Créer le package `coffee_maker/langchain_observe/exporters/`
- [ ] Implémenter `config.py` avec `ExportConfig`
- [ ] Implémenter `postgres_schema.py` avec les modèles SQLAlchemy
- [ ] Ajouter dépendances au `pyproject.toml`
- [ ] Mettre à jour `.env.example`

### Phase 2: Core Exporter (4-6h)
- [ ] Implémenter `langfuse_exporter.py`
- [ ] Tester connexion Langfuse
- [ ] Tester connexion PostgreSQL
- [ ] Implémenter conversion Trace → LLMTrace
- [ ] Implémenter conversion Generation → LLMGeneration
- [ ] Implémenter conversion Event → LLMEvent
- [ ] Gérer les upserts (éviter doublons)

### Phase 3: Scripts & Automatisation (2-3h)
- [ ] Créer `scripts/setup_warehouse_db.py`
- [ ] Créer `scripts/export_langfuse_data.py` (CLI)
- [ ] Créer `scripts/export_service.py` (daemon)
- [ ] Tester export manuel
- [ ] Tester export en continu

### Phase 4: Docker & Déploiement (1-2h)
- [ ] Créer `Dockerfile` pour le service
- [ ] Créer `docker-compose.langfuse-export.yml`
- [ ] Tester déploiement Docker
- [ ] Documenter déploiement

### Phase 5: Tests & Validation (3-4h)
- [ ] Tests unitaires pour conversion de données
- [ ] Tests d'intégration avec PostgreSQL de test
- [ ] Tests de bout en bout (Langfuse mock → PostgreSQL)
- [ ] Valider intégrité des données exportées
- [ ] Tester requêtes SQL d'analytics

### Phase 6: Documentation (1-2h)
- [ ] Documenter configuration dans README
- [ ] Ajouter exemples de requêtes SQL
- [ ] Documenter procédure de déploiement
- [ ] Créer dashboard Metabase/Grafana (optionnel)

---

## 📈 Estimation du temps total

| Phase | Description | Temps estimé |
|-------|-------------|--------------|
| 1 | Setup configuration et schémas | 2-3h |
| 2 | Core exporter implementation | 4-6h |
| 3 | Scripts et automatisation | 2-3h |
| 4 | Docker et déploiement | 1-2h |
| 5 | Tests et validation | 3-4h |
| 6 | Documentation | 1-2h |
| **TOTAL** | | **13-20h** |

---

## 🔮 Extensions futures

### Phase 2 (après implémentation de base):
1. **Alerting SQL** - Créer des alertes sur budget dépassé, taux de fallback élevé
2. **Dashboards Metabase** - Dashboards visuels prêts à l'emploi
3. **Aggregated views** - Vues matérialisées pour analytics rapides
4. **Data retention** - Politique d'archivage/suppression automatique
5. **Multi-project support** - Gérer plusieurs projets Langfuse
6. **Real-time streaming** - Webhooks Langfuse → PostgreSQL en temps réel

---

## 📚 Ressources

- [Langfuse API Documentation](https://langfuse.com/docs/api)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [Metabase](https://www.metabase.com/) - Open-source BI tool
- Fichier existant: `docs/langfuse_cost_queries.md`

---

## 🎯 Prochaines étapes

1. **Valider l'architecture** avec l'équipe
2. **Choisir la stratégie de déploiement** (Docker, service systemd, cron, etc.)
3. **Commencer par Phase 1** (configuration et schémas)
4. **Itérer** avec des exports manuels avant d'automatiser
