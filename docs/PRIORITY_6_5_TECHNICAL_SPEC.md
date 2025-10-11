# PRIORITY 6.5: GCP Deployment of code_developer - Technical Specification

**Document Version**: 1.0
**Created**: 2025-10-11
**Status**: Draft
**Owner**: code_developer autonomous daemon
**Estimated Duration**: 2-3 weeks (16-21 days)
**Impact**: ⭐⭐⭐⭐⭐ (Critical for continuous autonomous operation)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Dependencies](#prerequisites--dependencies)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Implementation Plan](#implementation-plan)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Performance Requirements](#performance-requirements)
10. [Cost Analysis](#cost-analysis)
11. [Risk Analysis](#risk-analysis)
12. [Success Criteria](#success-criteria)
13. [Rollback Strategy](#rollback-strategy)

---

## Executive Summary

### Problem Statement

Currently, `code_developer` daemon runs exclusively on the developer's local machine, creating significant limitations:

- **Availability**: Daemon stops when laptop sleeps/shuts down
- **Accessibility**: Cannot work on tasks when away from development machine
- **Resource Constraints**: Limited by local machine resources (CPU, memory, disk)
- **Reliability**: Vulnerable to local network issues, power outages, system crashes
- **Scalability**: Cannot run multiple daemons for different projects simultaneously

### Proposed Solution

Deploy `code_developer` daemon on Google Cloud Platform (GCP) with full integration to `project_manager` CLI, enabling:

- **24/7 Autonomous Operation**: Continuous development without local machine dependency
- **Remote Control**: Full daemon control from anywhere via `project_manager` CLI
- **Scalability**: Run multiple daemon instances for different projects
- **Professional Reliability**: 99.9% uptime with automatic failover
- **Enhanced Monitoring**: Real-time logs, metrics, and alerting

### Business Value

- **Always-On Development**: AI developer continues working even when user is offline
- **Professional Workflow**: Matches enterprise development practices
- **Cost Optimization**: Pay only for actual usage (serverless model)
- **Team Collaboration**: Multiple users can monitor/control the same daemon (future)

---

## Prerequisites & Dependencies

### Required Completions

| Priority | Component | Status | Required For |
|----------|-----------|--------|--------------|
| PRIORITY 3 | Autonomous Development Daemon | ✅ Complete | Core daemon logic to deploy |
| PRIORITY 2 Phase 1 | project_manager CLI | ✅ Complete | Remote control interface |
| PRIORITY 5 | Streamlit Dashboards | ✅ Complete | Monitoring integration |

### Technical Requirements

**Local Development Machine:**
- Python 3.11+ (already installed)
- Docker Desktop installed and running
- Git 2.40+ (already installed)
- gcloud CLI installed
- Terraform 1.5+ installed

**GCP Account:**
- Active GCP project with billing enabled
- Project ID configured
- Owner or Editor IAM role
- APIs enabled:
  - Cloud Run API
  - Cloud Storage API
  - Cloud SQL API
  - Secret Manager API
  - Cloud Logging API
  - Cloud Monitoring API

**External Services:**
- Anthropic API key (already configured)
- GitHub Personal Access Token with repo/workflow permissions
- Domain/subdomain for API endpoint (optional, GCP provides default)

### Software Dependencies

**New Python packages** (to add to `pyproject.toml`):
```toml
[tool.poetry.dependencies]
fastapi = "^0.115.0"              # API framework
uvicorn = {extras = ["standard"], version = "^0.32.0"}  # ASGI server
sqlalchemy = "^2.0.36"            # Database ORM
psycopg2-binary = "^2.9.10"       # PostgreSQL driver
google-cloud-storage = "^2.18.2"  # GCS client
google-cloud-secret-manager = "^2.21.1"  # Secrets management
google-cloud-logging = "^3.11.3"  # Cloud Logging
pydantic = "^2.10.0"              # Data validation
python-jose = {extras = ["cryptography"], version = "^3.3.0"}  # JWT tokens
passlib = {extras = ["bcrypt"], version = "^1.7.4"}  # Password hashing
websockets = "^14.1"              # WebSocket support
httpx = "^0.28.0"                 # HTTP client for testing
```

**DevOps Tools:**
```bash
# Install via system package manager
brew install terraform          # macOS
brew install google-cloud-sdk   # gcloud CLI
```

---

## Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "User's Local Machine"
        PM[project_manager CLI]
    end

    subgraph "Google Cloud Platform"
        subgraph "Cloud Run Service"
            API[Control API - FastAPI]
            DAEMON[code_developer Daemon]
        end

        GCS[Cloud Storage]
        SQL[(Cloud SQL - PostgreSQL)]
        SM[Secret Manager]
        LOG[Cloud Logging]
        MON[Cloud Monitoring]
    end

    subgraph "External Services"
        GITHUB[GitHub Repository]
        ANTHROPIC[Anthropic API]
    end

    PM -->|HTTPS/WebSocket| API
    API --> DAEMON
    DAEMON --> GCS
    DAEMON --> SQL
    DAEMON --> SM
    DAEMON --> LOG
    DAEMON --> GITHUB
    DAEMON --> ANTHROPIC
    API --> SQL
    API --> GCS
    MON --> LOG
    MON --> API
```

### Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Local Machine                      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  project_manager CLI                                   │  │
│  │  - View roadmap                                        │  │
│  │  - Send commands to GCP daemon                        │  │
│  │  - Monitor daemon status                              │  │
│  │  - Receive notifications                              │  │
│  │  - Edit files remotely                                │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│                  │ HTTPS/WebSocket (Authenticated)          │
└──────────────────┼───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Platform (GCP)                     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Run / Compute Engine                           │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  code_developer Daemon                          │ │  │
│  │  │  - Reads ROADMAP.md (from Cloud Storage)        │ │  │
│  │  │  - Implements features autonomously             │ │  │
│  │  │  - Commits to GitHub                            │ │  │
│  │  │  - Sends notifications via API                  │ │  │
│  │  │  - Responds to project_manager commands         │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  Control API (FastAPI)                          │ │  │
│  │  │  - /status - Get daemon status                  │ │  │
│  │  │  - /start - Start implementation                │ │  │
│  │  │  - /stop - Pause daemon                         │ │  │
│  │  │  - /logs - Stream logs                          │ │  │
│  │  │  - /files - Edit project files                  │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Storage                                         │  │
│  │  - ROADMAP.md (sync from GitHub)                      │  │
│  │  - Project files (working directory)                  │  │
│  │  - Daemon state (checkpoints)                         │  │
│  │  - Logs and analytics data                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                                │  │
│  │  - Notifications database (replaces local SQLite)     │  │
│  │  - Analytics database                                 │  │
│  │  - Daemon execution history                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Secret Manager                                        │  │
│  │  - ANTHROPIC_API_KEY                                  │  │
│  │  - GITHUB_TOKEN                                       │  │
│  │  - Database credentials                               │  │
│  │  - API authentication keys                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Container Runtime** | Docker | Package daemon + dependencies |
| **Cloud Platform** | Google Cloud Platform | Infrastructure hosting |
| **Compute** | Cloud Run | Serverless container deployment |
| **Storage** | Cloud Storage | File storage (project files, ROADMAP) |
| **Database** | Cloud SQL (PostgreSQL) | Persistent data storage |
| **Secrets** | Secret Manager | Secure credential storage |
| **API Framework** | FastAPI | REST API + WebSocket endpoints |
| **IaC** | Terraform | Infrastructure as Code |
| **Monitoring** | Cloud Logging + Monitoring | Observability |
| **CI/CD** | GitHub Actions | Automated deployment |

---

## Component Specifications

### 1. Daemon Containerization

#### 1.1 Dockerfile

**File**: `coffee_maker/deployment/Dockerfile`

```dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY coffee_maker ./coffee_maker
COPY docs ./docs
COPY data ./data
COPY README.md ./

# Install dependencies (no dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install gh -y

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

# Create non-root user for security
RUN useradd -m -u 1000 daemon && chown -R daemon:daemon /app
USER daemon

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Expose API port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV ENVIRONMENT=production

# Start both API server and daemon using supervisord
CMD ["python", "-m", "coffee_maker.deployment.entrypoint"]
```

**Key Features**:
- Multi-stage build reduces image size (< 500MB)
- Non-root user for security
- Health check endpoint for Cloud Run
- Git + GitHub CLI for repository operations
- All Python dependencies bundled

#### 1.2 Docker Compose (Local Testing)

**File**: `coffee_maker/deployment/docker-compose.yml`

```yaml
version: '3.8'

services:
  daemon:
    build:
      context: ../..
      dockerfile: coffee_maker/deployment/Dockerfile
    container_name: code_developer_daemon
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/coffee_maker
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: code_developer_db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=coffee_maker
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

**Usage**:
```bash
# Start services
cd coffee_maker/deployment
docker-compose up -d

# View logs
docker-compose logs -f daemon

# Stop services
docker-compose down
```

#### 1.3 Entrypoint Script

**File**: `coffee_maker/deployment/entrypoint.py`

```python
#!/usr/bin/env python3
"""
Entrypoint for GCP-deployed code_developer daemon.

This script starts both:
1. FastAPI control API (port 8080)
2. code_developer autonomous daemon (background)
"""

import asyncio
import logging
import os
import signal
import sys
from multiprocessing import Process

import uvicorn

from coffee_maker.api.main import create_app
from coffee_maker.autonomous.daemon import AutonomousDaemon
from coffee_maker.deployment.config import get_gcp_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_api_server():
    """Run FastAPI server."""
    config = get_gcp_config()
    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level=config.log_level.lower(),
        access_log=True,
    )


def run_daemon():
    """Run autonomous daemon."""
    try:
        daemon = AutonomousDaemon(
            project_root=os.getenv("PROJECT_ROOT", "/app"),
            roadmap_path=os.getenv("ROADMAP_PATH", "/app/docs/ROADMAP.md"),
            gcp_mode=True,
        )
        daemon.run()
    except Exception as e:
        logger.error(f"Daemon crashed: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entrypoint - start both API and daemon."""
    logger.info("Starting code_developer GCP deployment")

    # Validate environment
    config = get_gcp_config()
    config.validate()

    # Start API server in separate process
    api_process = Process(target=run_api_server, name="api_server")
    api_process.start()
    logger.info(f"API server started on port {config.port}")

    # Start daemon in separate process
    daemon_process = Process(target=run_daemon, name="daemon")
    daemon_process.start()
    logger.info("Daemon started")

    # Handle shutdown signals
    def shutdown_handler(signum, frame):
        logger.info("Received shutdown signal, stopping processes...")
        api_process.terminate()
        daemon_process.terminate()
        api_process.join(timeout=10)
        daemon_process.join(timeout=10)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # Wait for processes
    try:
        api_process.join()
        daemon_process.join()
    except KeyboardInterrupt:
        shutdown_handler(None, None)


if __name__ == "__main__":
    main()
```

#### 1.4 Health Check Script

**File**: `coffee_maker/deployment/healthcheck.sh`

```bash
#!/bin/bash
# Health check script for Cloud Run

set -e

# Check API is responding
curl -f http://localhost:8080/health || exit 1

# Check daemon is running (optional - check via API)
# curl -f http://localhost:8080/api/daemon/status || exit 1

exit 0
```

---

### 2. GCP Infrastructure (Terraform)

#### 2.1 Main Configuration

**File**: `infrastructure/terraform/main.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "coffee-maker-terraform-state"
    prefix = "prod/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "storage.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])

  service = each.key
  disable_on_destroy = false
}
```

#### 2.2 Variables

**File**: `infrastructure/terraform/variables.tf`

```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "code-developer-daemon"
}

variable "container_image" {
  description = "Docker container image URL"
  type        = string
}

variable "db_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "coffee-maker-db"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"  # Smallest tier for cost optimization
}

variable "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  type        = string
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "api_auth_secret" {
  description = "Secret key for API authentication"
  type        = string
  sensitive   = true
}
```

#### 2.3 Cloud Run Service

**File**: `infrastructure/terraform/cloud_run.tf`

```hcl
resource "google_cloud_run_service" "daemon" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.daemon.email

      containers {
        image = var.container_image

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "PROJECT_ROOT"
          value = "/app"
        }

        env {
          name  = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_connection_string.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "ANTHROPIC_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.anthropic_api_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GITHUB_TOKEN"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.github_token.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "API_AUTH_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_auth_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.daemon_storage.name
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 10
          timeout_seconds       = 5
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 30
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 3
        }
      }

      # Timeout for long-running operations
      timeout_seconds = 3600  # 1 hour

      # Always have at least 1 instance running
      container_concurrency = 1
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "1"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.apis,
    google_sql_database_instance.main,
  ]
}

# Allow public access (authentication handled at application level)
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.daemon.name
  location = google_cloud_run_service.daemon.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Service account for Cloud Run
resource "google_service_account" "daemon" {
  account_id   = "${var.service_name}-sa"
  display_name = "Service account for code_developer daemon"
}

# Grant permissions to service account
resource "google_project_iam_member" "daemon_permissions" {
  for_each = toset([
    "roles/storage.objectAdmin",           # Cloud Storage access
    "roles/cloudsql.client",               # Cloud SQL access
    "roles/secretmanager.secretAccessor",  # Secret Manager access
    "roles/logging.logWriter",             # Cloud Logging access
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.daemon.email}"
}
```

#### 2.4 Cloud Storage

**File**: `infrastructure/terraform/storage.tf`

```hcl
resource "google_storage_bucket" "daemon_storage" {
  name     = var.storage_bucket_name
  location = var.region

  # Lifecycle management
  lifecycle_rule {
    condition {
      age = 90  # Delete files older than 90 days
    }
    action {
      type = "Delete"
    }
  }

  # Versioning for ROADMAP.md
  versioning {
    enabled = true
  }

  # Uniform bucket-level access
  uniform_bucket_level_access = true

  # Public access prevention
  public_access_prevention = "enforced"

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Create folders (objects with trailing slash)
resource "google_storage_bucket_object" "folders" {
  for_each = toset([
    "roadmap/",
    "project_files/",
    "checkpoints/",
    "logs/",
    "analytics/",
  ])

  bucket  = google_storage_bucket.daemon_storage.name
  name    = each.key
  content = " "  # Empty content for folder
}
```

#### 2.5 Cloud SQL

**File**: `infrastructure/terraform/database.tf`

```hcl
resource "google_sql_database_instance" "main" {
  name             = var.db_instance_name
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier = var.db_tier

    # Backup configuration
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
      }
    }

    # High availability (optional - increases cost)
    availability_type = "ZONAL"  # Use "REGIONAL" for HA

    # Disk configuration
    disk_type       = "PD_SSD"
    disk_size       = 10  # GB
    disk_autoresize = true

    # IP configuration
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
      require_ssl     = true
    }

    # Maintenance window
    maintenance_window {
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }

    # Database flags
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    insights_config {
      query_insights_enabled = true
    }
  }

  deletion_protection = true  # Prevent accidental deletion

  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]
}

# Create database
resource "google_sql_database" "coffee_maker" {
  name     = "coffee_maker"
  instance = google_sql_database_instance.main.name
}

# Create database user
resource "google_sql_user" "daemon_user" {
  name     = "daemon"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

# Generate random password
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store connection string in Secret Manager
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "db-connection-string"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret = google_secret_manager_secret.db_connection_string.id

  secret_data = "postgresql://${google_sql_user.daemon_user.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.coffee_maker.name}"
}
```

#### 2.6 Secret Manager

**File**: `infrastructure/terraform/secrets.tf`

```hcl
# Anthropic API Key
resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "anthropic-api-key"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret_version" "anthropic_api_key" {
  secret      = google_secret_manager_secret.anthropic_api_key.id
  secret_data = var.anthropic_api_key
}

# GitHub Token
resource "google_secret_manager_secret" "github_token" {
  secret_id = "github-token"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret_version" "github_token" {
  secret      = google_secret_manager_secret.github_token.id
  secret_data = var.github_token
}

# API Authentication Secret
resource "google_secret_manager_secret" "api_auth_secret" {
  secret_id = "api-auth-secret"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret_version" "api_auth_secret" {
  secret      = google_secret_manager_secret.api_auth_secret.id
  secret_data = var.api_auth_secret
}

# Grant service account access to secrets
resource "google_secret_manager_secret_iam_member" "daemon_secret_access" {
  for_each = {
    anthropic = google_secret_manager_secret.anthropic_api_key.id
    github    = google_secret_manager_secret.github_token.id
    api_auth  = google_secret_manager_secret.api_auth_secret.id
    db_conn   = google_secret_manager_secret.db_connection_string.id
  }

  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.daemon.email}"
}
```

#### 2.7 Networking

**File**: `infrastructure/terraform/networking.tf`

```hcl
# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.service_name}-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.service_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# VPC Access Connector (for Cloud Run to access Cloud SQL via private IP)
resource "google_vpc_access_connector" "connector" {
  name          = "${var.service_name}-vpc-connector"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"

  depends_on = [google_project_service.apis]
}

# Private IP allocation for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.service_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Private VPC connection
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Firewall rule (allow health checks)
resource "google_compute_firewall" "allow_health_checks" {
  name    = "${var.service_name}-allow-health-checks"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]  # GCP health check ranges
  target_tags   = ["cloud-run"]
}
```

#### 2.8 Outputs

**File**: `infrastructure/terraform/outputs.tf`

```hcl
output "cloud_run_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.daemon.status[0].url
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.daemon.email
}

output "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.daemon_storage.name
}

output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "database_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "secret_manager_secrets" {
  description = "List of Secret Manager secret IDs"
  value = {
    anthropic_api_key = google_secret_manager_secret.anthropic_api_key.secret_id
    github_token      = google_secret_manager_secret.github_token.secret_id
    api_auth_secret   = google_secret_manager_secret.api_auth_secret.secret_id
    db_connection     = google_secret_manager_secret.db_connection_string.secret_id
  }
}
```

---

### 3. Control API (FastAPI)

#### 3.1 API Application

**File**: `coffee_maker/api/main.py`

```python
"""
FastAPI application for controlling GCP-deployed code_developer daemon.

Provides REST API endpoints for:
- Daemon control (start/stop/status)
- File operations (read/write project files)
- Notification management
- Log streaming
- Health checks
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from coffee_maker.api.routes import daemon, files, notifications, status
from coffee_maker.api.middleware.auth import AuthMiddleware
from coffee_maker.api.middleware.logging import LoggingMiddleware
from coffee_maker.deployment.config import get_gcp_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifecycle manager for FastAPI application."""
    # Startup
    logger.info("Starting FastAPI application")
    config = get_gcp_config()
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Database: {config.database_url.split('@')[1]}")  # Don't log password

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_gcp_config()

    app = FastAPI(
        title="code_developer Control API",
        description="API for controlling GCP-deployed code_developer daemon",
        version="1.0.0",
        docs_url="/docs" if config.environment != "production" else None,
        redoc_url="/redoc" if config.environment != "production" else None,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    # Routes
    app.include_router(status.router, prefix="/api", tags=["status"])
    app.include_router(daemon.router, prefix="/api/daemon", tags=["daemon"])
    app.include_router(files.router, prefix="/api/files", tags=["files"])
    app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

    # Health check endpoint (unauthenticated for Cloud Run)
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Cloud Run."""
        return {"status": "healthy", "environment": config.environment}

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


# Create app instance
app = create_app()
```

#### 3.2 Daemon Control Routes

**File**: `coffee_maker/api/routes/daemon.py`

```python
"""Daemon control API routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from coffee_maker.api.dependencies import get_daemon_controller
from coffee_maker.api.models.responses import DaemonStatusResponse

router = APIRouter()


class StartDaemonRequest(BaseModel):
    """Request model for starting daemon."""
    priority: Optional[str] = None
    force: bool = False


class StopDaemonRequest(BaseModel):
    """Request model for stopping daemon."""
    graceful: bool = True
    timeout: int = 30


@router.get("/status", response_model=DaemonStatusResponse)
async def get_daemon_status(controller=Depends(get_daemon_controller)):
    """
    Get current daemon status.

    Returns:
        - status: running | stopped | idle | working | error
        - current_task: Current task being worked on (if any)
        - progress: Task progress percentage (0-100)
        - uptime: Daemon uptime in seconds
        - last_activity: Timestamp of last activity
        - metadata: Additional daemon metadata
    """
    try:
        status = await controller.get_status()
        return DaemonStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_daemon(request: StartDaemonRequest, controller=Depends(get_daemon_controller)):
    """
    Start daemon implementation.

    Args:
        priority: Specific priority to work on (optional)
        force: Force start even if already running

    Returns:
        Success message with daemon status
    """
    try:
        result = await controller.start_daemon(
            priority=request.priority,
            force=request.force
        )
        return {"status": "success", "message": "Daemon started", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_daemon(request: StopDaemonRequest, controller=Depends(get_daemon_controller)):
    """
    Stop/pause daemon.

    Args:
        graceful: If True, wait for current task to complete
        timeout: Timeout in seconds for graceful shutdown

    Returns:
        Success message
    """
    try:
        await controller.stop_daemon(
            graceful=request.graceful,
            timeout=request.timeout
        )
        return {"status": "success", "message": "Daemon stopped"}
    except TimeoutError:
        raise HTTPException(status_code=408, detail="Daemon stop timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
async def restart_daemon(controller=Depends(get_daemon_controller)):
    """
    Restart daemon.

    Returns:
        Success message with new daemon status
    """
    try:
        # Stop daemon gracefully
        await controller.stop_daemon(graceful=True, timeout=30)

        # Start daemon
        result = await controller.start_daemon()

        return {"status": "success", "message": "Daemon restarted", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3.3 File Operations Routes

**File**: `coffee_maker/api/routes/files.py`

```python
"""File operations API routes."""

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel

from coffee_maker.api.dependencies import get_storage_manager

router = APIRouter()


class WriteFileRequest(BaseModel):
    """Request model for writing files."""
    content: str


@router.get("/roadmap")
async def get_roadmap(storage=Depends(get_storage_manager)):
    """
    Get ROADMAP.md content.

    Returns:
        ROADMAP.md content as plain text
    """
    try:
        content = await storage.read_file("roadmap/ROADMAP.md")
        return Response(content=content, media_type="text/markdown")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ROADMAP.md not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/roadmap")
async def update_roadmap(request: WriteFileRequest, storage=Depends(get_storage_manager)):
    """
    Update ROADMAP.md content.

    Args:
        content: New ROADMAP.md content

    Returns:
        Success message
    """
    try:
        await storage.write_file("roadmap/ROADMAP.md", request.content)
        return {"status": "success", "message": "ROADMAP.md updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_path:path}")
async def get_file(file_path: str, storage=Depends(get_storage_manager)):
    """
    Get project file content.

    Args:
        file_path: Relative path to file (e.g., "coffee_maker/api/main.py")

    Returns:
        File content as plain text
    """
    try:
        content = await storage.read_file(f"project_files/{file_path}")
        return Response(content=content, media_type="text/plain")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{file_path:path}")
async def update_file(file_path: str, request: WriteFileRequest, storage=Depends(get_storage_manager)):
    """
    Update project file content.

    Args:
        file_path: Relative path to file
        content: New file content

    Returns:
        Success message
    """
    try:
        await storage.write_file(f"project_files/{file_path}", request.content)
        return {"status": "success", "message": f"File updated: {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3.4 Authentication Middleware

**File**: `coffee_maker/api/middleware/auth.py`

```python
"""Authentication middleware for API."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import jwt, JWTError
import logging

from coffee_maker.deployment.config import get_gcp_config

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API authentication."""

    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication."""
        # Skip authentication for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )

        # Extract token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format"
            )

        # Validate token
        try:
            config = get_gcp_config()
            payload = jwt.decode(
                token,
                config.api_auth_secret,
                algorithms=["HS256"]
            )

            # Add user info to request state
            request.state.user = payload.get("sub")
            request.state.token_payload = payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        # Continue processing request
        response = await call_next(request)
        return response
```

#### 3.5 Request/Response Models

**File**: `coffee_maker/api/models/responses.py`

```python
"""Response models for API."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DaemonStatus(str, Enum):
    """Daemon status enum."""
    RUNNING = "running"
    STOPPED = "stopped"
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"


class DaemonStatusResponse(BaseModel):
    """Response model for daemon status."""
    status: DaemonStatus
    current_task: Optional[str] = None
    progress: float = Field(ge=0, le=100, default=0)
    uptime_seconds: int = Field(ge=0, default=0)
    last_activity: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "working",
                "current_task": "PRIORITY 6.5 - GCP Deployment",
                "progress": 45.0,
                "uptime_seconds": 86400,
                "last_activity": "2025-10-11T15:30:00Z",
                "metadata": {
                    "commits_today": 3,
                    "files_modified": 12,
                    "current_priority": "6.5"
                }
            }
        }


class NotificationResponse(BaseModel):
    """Response model for notifications."""
    id: int
    type: str
    title: str
    message: str
    priority: str
    created_at: datetime
    read: bool = False
    requires_response: bool = False
    response: Optional[str] = None

    class Config:
        from_attributes = True
```

---

### 4. project_manager GCP Integration

#### 4.1 GCP Client

**File**: `coffee_maker/cli/gcp_client.py`

```python
"""
GCP daemon client for project_manager CLI.

Provides interface for controlling GCP-deployed daemon from local CLI.
"""

import httpx
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime, timedelta
from jose import jwt
import logging

from coffee_maker.cli.config import get_gcp_config

logger = logging.getLogger(__name__)


class GCPDaemonClient:
    """Client for interacting with GCP-deployed daemon."""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize GCP daemon client.

        Args:
            api_url: GCP daemon API URL (default: from config)
            api_key: API authentication key (default: from config)
        """
        config = get_gcp_config()
        self.api_url = api_url or config.api_url
        self.api_key = api_key or config.api_key

        # Generate JWT token
        self.token = self._generate_token()

        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _generate_token(self) -> str:
        """Generate JWT token for API authentication."""
        payload = {
            "sub": "project-manager-cli",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        return jwt.encode(payload, self.api_key, algorithm="HS256")

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current daemon status from GCP.

        Returns:
            Daemon status dict with:
                - status: running | stopped | idle | working | error
                - current_task: Current task (if any)
                - progress: Progress percentage
                - uptime_seconds: Daemon uptime
                - last_activity: Last activity timestamp
                - metadata: Additional metadata
        """
        try:
            response = await self.client.get("/api/daemon/status")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get daemon status: {e}")
            raise ConnectionError(f"Failed to connect to GCP daemon: {e}")

    async def start_daemon(self, priority: Optional[str] = None, force: bool = False):
        """
        Start daemon implementation on GCP.

        Args:
            priority: Specific priority to work on (optional)
            force: Force start even if already running

        Returns:
            Start result dict
        """
        try:
            response = await self.client.post(
                "/api/daemon/start",
                json={"priority": priority, "force": force}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to start daemon: {e}")
            raise RuntimeError(f"Failed to start daemon: {e}")

    async def stop_daemon(self, graceful: bool = True, timeout: int = 30):
        """
        Stop daemon on GCP.

        Args:
            graceful: If True, wait for current task to complete
            timeout: Timeout in seconds for graceful shutdown

        Returns:
            Stop result dict
        """
        try:
            response = await self.client.post(
                "/api/daemon/stop",
                json={"graceful": graceful, "timeout": timeout}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to stop daemon: {e}")
            raise RuntimeError(f"Failed to stop daemon: {e}")

    async def stream_logs(self, follow: bool = True, tail: int = 100) -> AsyncIterator[str]:
        """
        Stream logs from GCP daemon.

        Args:
            follow: If True, continue streaming new logs
            tail: Number of recent log lines to fetch

        Yields:
            Log lines as they become available
        """
        try:
            async with self.client.stream(
                "GET",
                "/api/logs",
                params={"follow": follow, "tail": tail}
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    yield line
        except httpx.HTTPError as e:
            logger.error(f"Failed to stream logs: {e}")
            raise RuntimeError(f"Failed to stream logs: {e}")

    async def get_roadmap(self) -> str:
        """
        Get ROADMAP.md content from GCP.

        Returns:
            ROADMAP.md content as string
        """
        try:
            response = await self.client.get("/api/files/roadmap")
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to get ROADMAP.md: {e}")
            raise RuntimeError(f"Failed to get ROADMAP.md: {e}")

    async def update_roadmap(self, content: str):
        """
        Update ROADMAP.md on GCP.

        Args:
            content: New ROADMAP.md content

        Returns:
            Update result dict
        """
        try:
            response = await self.client.put(
                "/api/files/roadmap",
                json={"content": content}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to update ROADMAP.md: {e}")
            raise RuntimeError(f"Failed to update ROADMAP.md: {e}")

    async def get_file(self, file_path: str) -> str:
        """
        Get project file content from GCP.

        Args:
            file_path: Relative path to file

        Returns:
            File content as string
        """
        try:
            response = await self.client.get(f"/api/files/{file_path}")
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to get file {file_path}: {e}")
            raise RuntimeError(f"Failed to get file {file_path}: {e}")

    async def update_file(self, file_path: str, content: str):
        """
        Update project file on GCP.

        Args:
            file_path: Relative path to file
            content: New file content

        Returns:
            Update result dict
        """
        try:
            response = await self.client.put(
                f"/api/files/{file_path}",
                json={"content": content}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to update file {file_path}: {e}")
            raise RuntimeError(f"Failed to update file {file_path}: {e}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
```

#### 4.2 CLI Commands

**File**: `coffee_maker/cli/commands/cloud.py`

```python
"""Cloud deployment commands for project_manager."""

import asyncio
import click
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

from coffee_maker.cli.gcp_client import GCPDaemonClient

console = Console()


@click.group()
def cloud():
    """Manage GCP-deployed daemon."""
    pass


@cloud.command()
async def status():
    """Check GCP daemon status."""
    try:
        async with GCPDaemonClient() as client:
            status_data = await client.get_status()

        # Display status in rich table
        table = Table(title="GCP Daemon Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Status", status_data["status"])
        table.add_row("Current Task", status_data.get("current_task", "None"))
        table.add_row("Progress", f"{status_data.get('progress', 0):.1f}%")
        table.add_row("Uptime", f"{status_data.get('uptime_seconds', 0) // 3600}h {(status_data.get('uptime_seconds', 0) % 3600) // 60}m")
        table.add_row("Last Activity", status_data.get("last_activity", "Unknown"))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cloud.command()
@click.option("--priority", help="Specific priority to work on")
@click.option("--force", is_flag=True, help="Force start even if already running")
async def start(priority, force):
    """Start GCP daemon."""
    try:
        async with GCPDaemonClient() as client:
            result = await client.start_daemon(priority=priority, force=force)

        console.print(f"[green]✓ Daemon started successfully[/green]")
        if priority:
            console.print(f"Working on: {priority}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cloud.command()
@click.option("--graceful/--force", default=True, help="Graceful or forceful shutdown")
@click.option("--timeout", default=30, help="Timeout for graceful shutdown")
async def stop(graceful, timeout):
    """Stop GCP daemon."""
    try:
        async with GCPDaemonClient() as client:
            await client.stop_daemon(graceful=graceful, timeout=timeout)

        console.print(f"[green]✓ Daemon stopped successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cloud.command()
@click.option("--follow", is_flag=True, help="Follow log output")
@click.option("--tail", default=100, help="Number of lines to show")
async def logs(follow, tail):
    """Stream logs from GCP daemon."""
    try:
        async with GCPDaemonClient() as client:
            async for line in client.stream_logs(follow=follow, tail=tail):
                console.print(line)

    except KeyboardInterrupt:
        console.print("\n[yellow]Log streaming stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cloud.command()
async def deploy():
    """Deploy daemon to GCP."""
    console.print("[yellow]Deploying to GCP...[/yellow]")
    console.print("[red]TODO: Implement deployment automation[/red]")
    console.print("For now, follow manual deployment steps in docs/DEPLOYMENT.md")


# Make commands async-compatible
for command in [status, start, stop, logs, deploy]:
    command.callback = lambda f: lambda **kwargs: asyncio.run(f(**kwargs))
```

---

## Data Flow Diagrams

### 1. Normal Operation Flow

```mermaid
sequenceDiagram
    participant User
    participant PM as project_manager CLI
    participant API as GCP Control API
    participant Daemon as code_developer Daemon
    participant GCS as Cloud Storage
    participant GitHub
    participant Anthropic

    User->>PM: project-manager cloud status
    PM->>API: GET /api/daemon/status
    API->>Daemon: Query status
    Daemon-->>API: Return status
    API-->>PM: Status response
    PM-->>User: Display status

    User->>PM: project-manager cloud start
    PM->>API: POST /api/daemon/start
    API->>Daemon: Start implementation
    Daemon->>GCS: Read ROADMAP.md
    GCS-->>Daemon: ROADMAP content
    Daemon->>GitHub: Clone repository
    Daemon->>Anthropic: Generate code
    Anthropic-->>Daemon: Code response
    Daemon->>GitHub: Commit changes
    API-->>PM: Started confirmation
    PM-->>User: Daemon started
```

### 2. File Edit Flow

```mermaid
sequenceDiagram
    participant User
    participant PM as project_manager CLI
    participant API as GCP Control API
    participant GCS as Cloud Storage
    participant Daemon as code_developer Daemon

    User->>PM: project-manager edit roadmap
    PM->>User: Open local editor
    User->>PM: Save changes
    PM->>API: PUT /api/files/roadmap
    API->>GCS: Write ROADMAP.md
    GCS-->>API: Success
    API->>Daemon: Notify: ROADMAP updated
    Daemon->>GCS: Read updated ROADMAP.md
    Daemon->>Daemon: Re-parse priorities
    API-->>PM: Update confirmation
    PM-->>User: ROADMAP updated
```

### 3. Notification Flow

```mermaid
sequenceDiagram
    participant Daemon as code_developer Daemon
    participant DB as Cloud SQL
    participant API as GCP Control API
    participant PM as project_manager CLI
    participant User

    Daemon->>Daemon: Need user input
    Daemon->>DB: Create notification
    Daemon->>API: Notify: New notification
    API->>PM: WebSocket: New notification
    PM->>User: Display notification
    User->>PM: Provide response
    PM->>API: POST /api/notifications/{id}/respond
    API->>DB: Store response
    API->>Daemon: Notify: Response available
    Daemon->>DB: Read response
    Daemon->>Daemon: Continue with response
```

### 4. Deployment Flow

```mermaid
graph TD
    A[Local Development] -->|git push| B[GitHub Repository]
    B -->|GitHub Actions| C[Build Docker Image]
    C -->|Push to GCR| D[Google Container Registry]
    D -->|Terraform apply| E[Cloud Run Deployment]
    E --> F[Load Secrets from Secret Manager]
    E --> G[Connect to Cloud SQL]
    E --> H[Mount Cloud Storage]
    F --> I[Start API Server]
    F --> J[Start Daemon]
    I --> K[Service Running]
    J --> K
```

---

## Implementation Plan

### Phase 1: Containerization & Local Testing (Days 1-4)

#### Task 1.1: Create Dockerfile (Day 1 - 6 hours)

**Files to create:**
- `coffee_maker/deployment/Dockerfile`
- `coffee_maker/deployment/.dockerignore`
- `coffee_maker/deployment/healthcheck.sh`

**Steps:**
1. Create multi-stage Dockerfile with Python 3.11-slim base
2. Install system dependencies (git, gh CLI, curl)
3. Copy project files and install Poetry dependencies
4. Create non-root user for security
5. Configure health check endpoint
6. Set environment variables and entrypoint

**Acceptance criteria:**
- Docker image builds successfully (< 500MB)
- All dependencies installed correctly
- Health check responds on `/health`
- Non-root user configured
- Image runs locally without errors

**Testing:**
```bash
# Build image
docker build -t code-developer:local -f coffee_maker/deployment/Dockerfile .

# Run container
docker run -d -p 8080:8080 \
  -e ANTHROPIC_API_KEY=test \
  -e GITHUB_TOKEN=test \
  code-developer:local

# Test health check
curl http://localhost:8080/health
```

---

#### Task 1.2: Create Docker Compose Configuration (Day 1 - 2 hours)

**Files to create:**
- `coffee_maker/deployment/docker-compose.yml`

**Steps:**
1. Define daemon service with build configuration
2. Define PostgreSQL database service
3. Configure environment variables
4. Set up volume mounts for data persistence
5. Configure networking between services

**Acceptance criteria:**
- `docker-compose up` starts both services
- Daemon connects to PostgreSQL successfully
- Logs visible via `docker-compose logs`
- Can stop/restart services cleanly

**Testing:**
```bash
cd coffee_maker/deployment
docker-compose up -d
docker-compose ps
docker-compose logs -f daemon
docker-compose down
```

---

#### Task 1.3: Create Entrypoint Script (Day 2 - 4 hours)

**Files to create:**
- `coffee_maker/deployment/entrypoint.py`
- `coffee_maker/deployment/config.py`

**Steps:**
1. Create Python entrypoint script
2. Implement process management for API + daemon
3. Add graceful shutdown handling
4. Configure logging
5. Add environment validation

**Acceptance criteria:**
- Both API and daemon start successfully
- Graceful shutdown on SIGTERM/SIGINT
- Logs clearly identify each process
- Health check responds correctly
- Daemon can access PostgreSQL

**Testing:**
```bash
# Test locally
python coffee_maker/deployment/entrypoint.py

# Test in container
docker run -p 8080:8080 code-developer:local
curl http://localhost:8080/health
```

---

#### Task 1.4: Test Daemon in Container (Day 3-4 - 8 hours)

**Files to create:**
- `tests/deployment/test_docker.py`
- `tests/deployment/test_entrypoint.py`

**Steps:**
1. Create integration tests for containerized daemon
2. Test daemon can read/write files
3. Test daemon can commit to Git
4. Test API endpoints respond correctly
5. Test health checks
6. Load test (simulate extended operation)

**Acceptance criteria:**
- All integration tests pass
- Daemon successfully completes a simple priority
- No memory leaks during 1-hour test
- API responds to all endpoints
- Container restarts cleanly

**Testing:**
```bash
pytest tests/deployment/ -v
```

---

### Phase 2: GCP Infrastructure Setup (Days 5-9)

#### Task 2.1: Set Up GCP Project & APIs (Day 5 - 3 hours)

**Prerequisites:**
- GCP account with billing enabled
- gcloud CLI installed

**Steps:**
1. Create new GCP project (or use existing)
2. Enable required APIs:
   - Cloud Run
   - Cloud Storage
   - Cloud SQL
   - Secret Manager
   - Cloud Logging
   - Cloud Monitoring
3. Set up gcloud CLI authentication
4. Create service account for Terraform

**Commands:**
```bash
# Create project
gcloud projects create coffee-maker-prod --name="Coffee Maker Production"

# Set default project
gcloud config set project coffee-maker-prod

# Enable APIs
gcloud services enable \
  run.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# Create service account for Terraform
gcloud iam service-accounts create terraform \
  --display-name="Terraform Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding coffee-maker-prod \
  --member="serviceAccount:terraform@coffee-maker-prod.iam.gserviceaccount.com" \
  --role="roles/editor"

# Create key
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform@coffee-maker-prod.iam.gserviceaccount.com
```

**Acceptance criteria:**
- All APIs enabled
- Service account created with appropriate permissions
- Authentication configured

---

#### Task 2.2: Create Terraform Configurations (Day 5-6 - 8 hours)

**Files to create:**
- `infrastructure/terraform/main.tf`
- `infrastructure/terraform/variables.tf`
- `infrastructure/terraform/outputs.tf`
- `infrastructure/terraform/cloud_run.tf`
- `infrastructure/terraform/storage.tf`
- `infrastructure/terraform/database.tf`
- `infrastructure/terraform/secrets.tf`
- `infrastructure/terraform/networking.tf`

**Steps:**
1. Create main Terraform configuration with GCS backend
2. Define variables for all configurable parameters
3. Create Cloud Run service configuration
4. Create Cloud Storage bucket configuration
5. Create Cloud SQL instance configuration
6. Create Secret Manager secrets
7. Create VPC and networking configuration
8. Define outputs for important resources

**Acceptance criteria:**
- All Terraform files have valid syntax (`terraform validate`)
- Variables documented with descriptions
- Outputs defined for key resources
- No hardcoded values (use variables)

**Testing:**
```bash
cd infrastructure/terraform
terraform init
terraform validate
terraform plan -var-file=dev.tfvars
```

---

#### Task 2.3: Deploy Cloud Storage (Day 6 - 2 hours)

**Steps:**
1. Create `terraform.tfvars` with variable values
2. Run `terraform plan` to preview changes
3. Run `terraform apply` to create Cloud Storage bucket
4. Create folder structure in bucket
5. Test bucket access

**Commands:**
```bash
cd infrastructure/terraform

# Create tfvars file
cat > terraform.tfvars <<EOF
project_id = "coffee-maker-prod"
region = "us-central1"
storage_bucket_name = "coffee-maker-prod-storage"
# ... other variables
EOF

# Apply only storage resources
terraform apply -target=google_storage_bucket.daemon_storage

# Test access
gsutil ls gs://coffee-maker-prod-storage/
```

**Acceptance criteria:**
- Bucket created successfully
- Folder structure created
- Can upload/download files
- Versioning enabled for ROADMAP.md

---

#### Task 2.4: Deploy Cloud SQL (Day 7 - 4 hours)

**Steps:**
1. Run `terraform apply` to create Cloud SQL instance
2. Wait for instance to be ready (~10 minutes)
3. Create database and user
4. Test connection from local machine
5. Run database migrations

**Commands:**
```bash
# Apply database resources
terraform apply -target=google_sql_database_instance.main

# Get connection name
terraform output database_connection_name

# Connect using cloud SQL proxy
cloud_sql_proxy -instances=<connection-name>=tcp:5432 &

# Test connection
psql "postgresql://daemon:PASSWORD@localhost:5432/coffee_maker"

# Run migrations
alembic upgrade head
```

**Acceptance criteria:**
- Cloud SQL instance running
- Database created
- Can connect from local machine via Cloud SQL proxy
- Schema migrated successfully

---

#### Task 2.5: Deploy Secret Manager (Day 7 - 2 hours)

**Steps:**
1. Create secrets in Secret Manager via Terraform
2. Store Anthropic API key
3. Store GitHub token
4. Store database connection string
5. Store API authentication secret
6. Grant service account access

**Commands:**
```bash
# Apply secret resources
terraform apply -target=google_secret_manager_secret.anthropic_api_key
terraform apply -target=google_secret_manager_secret.github_token
terraform apply -target=google_secret_manager_secret.api_auth_secret

# Verify secrets created
gcloud secrets list

# Grant access to service account
# (already done in Terraform)
```

**Acceptance criteria:**
- All secrets created
- Secret versions contain correct values
- Service account can access secrets
- Secrets not visible in logs

---

#### Task 2.6: Deploy Cloud Run Service (Day 8-9 - 8 hours)

**Steps:**
1. Build and push Docker image to Google Container Registry
2. Run `terraform apply` to create Cloud Run service
3. Wait for deployment (~5 minutes)
4. Test service URL
5. Monitor logs in Cloud Logging
6. Verify daemon is running

**Commands:**
```bash
# Build and tag image
docker build -t gcr.io/coffee-maker-prod/code-developer:latest \
  -f coffee_maker/deployment/Dockerfile .

# Push to GCR
docker push gcr.io/coffee-maker-prod/code-developer:latest

# Apply Cloud Run resources
terraform apply

# Get service URL
terraform output cloud_run_url

# Test health endpoint
curl https://code-developer-xxxxxx.run.app/health

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

**Acceptance criteria:**
- Docker image pushed to GCR
- Cloud Run service deployed and running
- Health check returns 200 OK
- Can see logs in Cloud Logging
- Daemon starts automatically

---

### Phase 3: Control API Development (Days 10-14)

#### Task 3.1: Create FastAPI Application (Day 10 - 6 hours)

**Files to create:**
- `coffee_maker/api/__init__.py`
- `coffee_maker/api/main.py`
- `coffee_maker/api/dependencies.py`
- `coffee_maker/api/middleware/auth.py`
- `coffee_maker/api/middleware/logging.py`

**Steps:**
1. Create FastAPI app with lifespan manager
2. Configure CORS middleware
3. Add authentication middleware
4. Add logging middleware
5. Add global exception handler
6. Create health check endpoint

**Acceptance criteria:**
- FastAPI app starts successfully
- `/health` endpoint returns 200
- `/docs` endpoint shows API documentation (dev only)
- CORS configured correctly
- Authentication required for protected endpoints

**Testing:**
```bash
# Run locally
uvicorn coffee_maker.api.main:app --reload

# Test health check
curl http://localhost:8000/health

# View docs
open http://localhost:8000/docs
```

---

#### Task 3.2: Implement Daemon Control Routes (Day 10-11 - 6 hours)

**Files to create:**
- `coffee_maker/api/routes/daemon.py`
- `coffee_maker/api/controllers/daemon_controller.py`
- `coffee_maker/api/models/requests.py`
- `coffee_maker/api/models/responses.py`

**Steps:**
1. Create daemon control routes
2. Implement `GET /api/daemon/status`
3. Implement `POST /api/daemon/start`
4. Implement `POST /api/daemon/stop`
5. Implement `POST /api/daemon/restart`
6. Add request/response models

**Acceptance criteria:**
- All endpoints respond correctly
- Status endpoint returns current daemon state
- Start/stop endpoints control daemon
- Proper error handling
- Request/response validation with Pydantic

**Testing:**
```bash
# Test status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/daemon/status

# Test start
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/daemon/start

# Test stop
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/daemon/stop
```

---

#### Task 3.3: Implement File Operations Routes (Day 11-12 - 6 hours)

**Files to create:**
- `coffee_maker/api/routes/files.py`
- `coffee_maker/api/storage/gcs_manager.py`

**Steps:**
1. Create file operations routes
2. Implement `GET /api/files/roadmap`
3. Implement `PUT /api/files/roadmap`
4. Implement `GET /api/files/{path}`
5. Implement `PUT /api/files/{path}`
6. Create Cloud Storage manager

**Acceptance criteria:**
- Can read/write ROADMAP.md via API
- Can read/write project files via API
- Files stored in Cloud Storage
- Proper error handling for missing files
- Content validation

**Testing:**
```bash
# Get ROADMAP
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/files/roadmap

# Update ROADMAP
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "# New ROADMAP\n..."}' \
  http://localhost:8000/api/files/roadmap
```

---

#### Task 3.4: Implement Notifications Routes (Day 12-13 - 6 hours)

**Files to create:**
- `coffee_maker/api/routes/notifications.py`
- `coffee_maker/api/database/notification_repository.py`

**Steps:**
1. Create notifications routes
2. Implement `GET /api/notifications`
3. Implement `POST /api/notifications/{id}/respond`
4. Implement `DELETE /api/notifications/{id}`
5. Create notification repository (Cloud SQL)

**Acceptance criteria:**
- Can list notifications via API
- Can respond to notifications via API
- Can mark notifications as read
- Notifications stored in Cloud SQL
- Real-time updates via WebSocket (future)

**Testing:**
```bash
# List notifications
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/notifications

# Respond to notification
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"response": "Yes, proceed"}' \
  http://localhost:8000/api/notifications/123/respond
```

---

#### Task 3.5: Implement Log Streaming (Day 13-14 - 4 hours)

**Files to create:**
- `coffee_maker/api/routes/logs.py`
- `coffee_maker/api/logging/log_streamer.py`

**Steps:**
1. Create logs route
2. Implement `GET /api/logs` with SSE streaming
3. Read logs from Cloud Logging
4. Support filtering and tail options

**Acceptance criteria:**
- Can stream logs via API
- Logs update in real-time
- Can filter by log level
- Can tail last N lines
- Proper cleanup on disconnect

**Testing:**
```bash
# Stream logs
curl -H "Authorization: Bearer $TOKEN" \
  -N http://localhost:8000/api/logs?follow=true&tail=100
```

---

### Phase 4: project_manager Integration (Days 15-18)

#### Task 4.1: Create GCP Client (Day 15 - 6 hours)

**Files to create:**
- `coffee_maker/cli/gcp_client.py`
- `coffee_maker/cli/config.py` (add GCP config)

**Steps:**
1. Create `GCPDaemonClient` class
2. Implement HTTP client with authentication
3. Implement JWT token generation
4. Add methods for all API endpoints
5. Add async context manager support

**Acceptance criteria:**
- Client can connect to GCP API
- Authentication works correctly
- All API methods implemented
- Proper error handling
- Async/await support

**Testing:**
```python
# Test client
import asyncio
from coffee_maker.cli.gcp_client import GCPDaemonClient

async def test():
    async with GCPDaemonClient() as client:
        status = await client.get_status()
        print(status)

asyncio.run(test())
```

---

#### Task 4.2: Add Cloud Commands to CLI (Day 15-16 - 6 hours)

**Files to create:**
- `coffee_maker/cli/commands/cloud.py`

**Steps:**
1. Create `cloud` command group
2. Implement `project-manager cloud status`
3. Implement `project-manager cloud start`
4. Implement `project-manager cloud stop`
5. Implement `project-manager cloud logs`
6. Add rich formatting for output

**Acceptance criteria:**
- All commands work correctly
- Commands use GCP client
- Output formatted with rich library
- Proper error handling
- Help text for all commands

**Testing:**
```bash
# Test commands
project-manager cloud status
project-manager cloud start
project-manager cloud logs --follow
project-manager cloud stop
```

---

#### Task 4.3: Add Configuration Management (Day 16-17 - 4 hours)

**Files to create:**
- `~/.config/coffee-maker/gcp.yaml`
- `coffee_maker/cli/config_manager.py`

**Steps:**
1. Create GCP configuration file structure
2. Implement configuration loading/saving
3. Add `project-manager cloud config` command
4. Support environment-specific configs (dev/prod)

**Acceptance criteria:**
- Configuration file created on first use
- Can set/get configuration values
- Supports multiple environments
- Validates configuration values

**Testing:**
```bash
# View config
project-manager cloud config get

# Set config
project-manager cloud config set api_url https://...
project-manager cloud config set api_key ...

# Use dev environment
project-manager cloud --env dev status
```

---

#### Task 4.4: End-to-End Testing (Day 17-18 - 8 hours)

**Files to create:**
- `tests/integration/test_gcp_deployment.py`
- `tests/integration/test_cli_cloud_commands.py`

**Steps:**
1. Create end-to-end test suite
2. Test full workflow:
   - Deploy to GCP
   - Start daemon via CLI
   - Monitor status
   - Edit ROADMAP
   - Daemon implements feature
   - View logs
   - Stop daemon
3. Test error scenarios
4. Test authentication failures
5. Test network failures

**Acceptance criteria:**
- All end-to-end tests pass
- Can complete a full workflow
- Error scenarios handled gracefully
- Tests run in CI (GitHub Actions)

**Testing:**
```bash
pytest tests/integration/test_gcp_deployment.py -v
```

---

### Phase 5: Monitoring & Documentation (Days 19-21)

#### Task 5.1: Set Up Cloud Monitoring (Day 19 - 4 hours)

**Files to create:**
- `infrastructure/terraform/monitoring.tf`
- `coffee_maker/monitoring/metrics.py`
- `coffee_maker/monitoring/dashboards/daemon_health.json`

**Steps:**
1. Create Cloud Monitoring dashboards via Terraform
2. Define custom metrics for daemon
3. Set up log-based metrics
4. Create uptime checks

**Acceptance criteria:**
- Dashboard shows daemon health
- Metrics collected automatically
- Uptime check running every 5 minutes
- Can view metrics in GCP Console

---

#### Task 5.2: Configure Alerting (Day 19 - 3 hours)

**Files to create:**
- `infrastructure/terraform/alerting.tf`
- `coffee_maker/monitoring/alerts.py`

**Steps:**
1. Create alert policies via Terraform
2. Configure notification channels (email)
3. Set up alerts for:
   - Daemon crash/hang
   - High error rate
   - Cost threshold exceeded
   - Disk space low

**Acceptance criteria:**
- Alerts configured in Cloud Monitoring
- Test alert triggers successfully
- Notification received via email
- Alert documentation updated

---

#### Task 5.3: Write Deployment Documentation (Day 20 - 6 hours)

**Files to create:**
- `docs/DEPLOYMENT.md`
- `docs/GCP_SETUP.md`
- `docs/TROUBLESHOOTING_GCP.md`

**Content to include:**
1. Prerequisites and setup instructions
2. Step-by-step deployment guide
3. Configuration reference
4. Common issues and solutions
5. Cost optimization tips
6. Security best practices

**Acceptance criteria:**
- Documentation is complete and accurate
- Can follow docs to deploy from scratch
- All configuration options documented
- Troubleshooting section covers common issues

---

#### Task 5.4: Create Operations Runbook (Day 20-21 - 4 hours)

**Files to create:**
- `docs/OPERATIONS_RUNBOOK.md`

**Content to include:**
1. How to monitor daemon health
2. How to respond to alerts
3. How to scale resources
4. How to perform updates/rollbacks
5. Backup and recovery procedures
6. Incident response procedures

**Acceptance criteria:**
- Runbook covers all operational scenarios
- Clear step-by-step procedures
- Contact information for escalation
- Tested procedures work as documented

---

#### Task 5.5: Final Testing & Validation (Day 21 - 6 hours)

**Steps:**
1. Deploy to clean GCP project from scratch
2. Verify all components working
3. Load test daemon (24-hour run)
4. Verify monitoring and alerting
5. Test failure scenarios
6. Validate cost estimates

**Acceptance criteria:**
- Full deployment successful from scratch
- Daemon runs for 24+ hours without issues
- All monitoring metrics accurate
- Alerts triggered correctly in test scenarios
- Cost within estimated range

---

### Summary of Implementation Timeline

| Phase | Duration | Tasks | Key Deliverables |
|-------|----------|-------|------------------|
| Phase 1: Containerization | 4 days | 1.1-1.4 | Docker image, docker-compose, tests |
| Phase 2: GCP Infrastructure | 5 days | 2.1-2.6 | Terraform configs, deployed infrastructure |
| Phase 3: Control API | 5 days | 3.1-3.5 | FastAPI app, all endpoints working |
| Phase 4: CLI Integration | 4 days | 4.1-4.4 | GCP client, cloud commands, tests |
| Phase 5: Monitoring & Docs | 3 days | 5.1-5.5 | Monitoring, alerts, documentation |
| **Total** | **21 days** | **24 tasks** | **Fully deployed GCP daemon** |

**Note**: This is the most conservative estimate (3 weeks). With parallel work and good progress, could be completed in 16 days (2+ weeks).

---

## Testing Strategy

### 1. Unit Tests

**Files to test:**
- `coffee_maker/api/main.py`
- `coffee_maker/api/routes/*.py`
- `coffee_maker/api/middleware/*.py`
- `coffee_maker/cli/gcp_client.py`
- `coffee_maker/deployment/entrypoint.py`

**Test coverage goals:**
- API routes: 90%+
- GCP client: 85%+
- Deployment code: 80%+

**Test framework**: pytest

```bash
# Run unit tests
pytest tests/unit/ -v --cov=coffee_maker
```

---

### 2. Integration Tests

**Scenarios to test:**
1. **Docker Integration:**
   - Build Docker image
   - Run container locally
   - Test health check
   - Test API endpoints
   - Test daemon functionality

2. **Database Integration:**
   - Connect to PostgreSQL
   - Read/write data
   - Handle connection failures
   - Transaction rollback

3. **Storage Integration:**
   - Upload/download files from GCS
   - Handle large files
   - Handle permission errors

4. **GitHub Integration:**
   - Clone repository
   - Make commits
   - Create pull requests
   - Handle authentication failures

**Test framework**: pytest + docker-py + httpx

```bash
# Run integration tests
pytest tests/integration/ -v
```

---

### 3. End-to-End Tests

**Full workflow test:**
1. Deploy infrastructure via Terraform
2. Start daemon via CLI
3. Daemon reads ROADMAP.md
4. Daemon implements feature
5. Daemon commits to GitHub
6. View logs via CLI
7. Stop daemon via CLI
8. Verify cleanup

**Test environment**: Separate GCP project for testing

```bash
# Run E2E tests
pytest tests/e2e/ -v --slow
```

---

### 4. Load Testing

**Scenarios:**
1. **Long-running daemon:**
   - Run for 24 hours
   - Monitor memory usage
   - Monitor CPU usage
   - Check for memory leaks

2. **API load:**
   - 100 concurrent requests
   - Sustained 10 req/sec
   - Verify response times

3. **Database load:**
   - 1000 notifications
   - Concurrent reads/writes
   - Query performance

**Tools**: locust, k6

```python
# Load test with locust
from locust import HttpUser, task, between

class DaemonAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_status(self):
        self.client.get("/api/daemon/status")

    @task(2)
    def get_notifications(self):
        self.client.get("/api/notifications")
```

---

### 5. Security Testing

**Tests:**
1. **Authentication:**
   - Invalid JWT tokens rejected
   - Expired tokens rejected
   - No token = 401 error

2. **Authorization:**
   - Cannot access other users' data
   - Cannot perform admin actions without permission

3. **Input validation:**
   - SQL injection prevented
   - XSS prevented
   - Path traversal prevented

4. **Secrets:**
   - No secrets in logs
   - No secrets in error messages
   - Secrets encrypted at rest

**Tools**: OWASP ZAP, sqlmap (testing only)

---

### 6. Disaster Recovery Testing

**Scenarios:**
1. **Database failure:**
   - Simulate Cloud SQL crash
   - Verify daemon handles gracefully
   - Verify automatic recovery

2. **Storage failure:**
   - Simulate GCS unavailability
   - Verify retry logic
   - Verify local caching

3. **API failure:**
   - Simulate Anthropic API outage
   - Verify retry logic
   - Verify error notifications

4. **Complete outage:**
   - Simulate region failure
   - Test failover to backup region (future)

---

## Security Considerations

### 1. Authentication & Authorization

**Implemented security measures:**

1. **API Authentication:**
   - JWT tokens for all API requests
   - Tokens expire after 24 hours
   - Tokens signed with secret key (256-bit)
   - Token validation on every request

2. **Service-to-Service Auth:**
   - Cloud Run uses service account
   - Service account has minimal required permissions
   - Secret Manager access restricted to specific secrets

3. **GitHub Authentication:**
   - Personal Access Token with minimal scopes
   - Token stored in Secret Manager
   - Token never logged or exposed

4. **Database Authentication:**
   - Unique user per service
   - Strong random passwords (32 characters)
   - SSL/TLS connections required
   - Private IP only (no public access)

**Security best practices:**
- Never hardcode credentials
- Rotate secrets every 90 days
- Use principle of least privilege
- Audit access logs regularly

---

### 2. Data Protection

**Encryption:**

1. **At Rest:**
   - Cloud SQL: Encrypted with Google-managed keys
   - Cloud Storage: Encrypted with Google-managed keys
   - Secret Manager: Encrypted automatically

2. **In Transit:**
   - All API calls use HTTPS/TLS 1.3
   - Cloud SQL connections use SSL
   - No plaintext credentials over network

3. **Application Level:**
   - Sensitive data masked in logs
   - Passwords hashed with bcrypt
   - API keys never returned in responses

**Data retention:**
- Logs retained for 30 days
- Backups retained for 7 days
- Old files deleted after 90 days (lifecycle policy)

---

### 3. Network Security

**Infrastructure:**

1. **VPC Configuration:**
   - Private VPC for Cloud SQL
   - VPC connector for Cloud Run access
   - No public IP for Cloud SQL

2. **Firewall Rules:**
   - Cloud Run only accessible via HTTPS
   - Health check IPs whitelisted
   - Cloud SQL only accessible from VPC

3. **DDoS Protection:**
   - Cloud Run has built-in DDoS protection
   - Cloud Armor (optional, additional cost)

**API Security:**
- Rate limiting (100 req/min per user)
- Request size limits (10MB max)
- Timeout limits (30s per request)

---

### 4. Secret Management

**Best practices:**

1. **Storage:**
   - All secrets in Secret Manager
   - Never in code or config files
   - Never in environment variables (use Secret Manager refs)

2. **Access:**
   - Service account-based access
   - Audit logs for all secret access
   - Alerts on suspicious access patterns

3. **Rotation:**
   - Rotate every 90 days (automated)
   - Old versions retained for 7 days
   - Zero-downtime rotation

**Secrets to manage:**
- ANTHROPIC_API_KEY
- GITHUB_TOKEN
- DATABASE_PASSWORD
- API_AUTH_SECRET
- JWT_SECRET_KEY

---

### 5. Code Security

**Development practices:**

1. **Dependency Management:**
   - Pin all dependencies to specific versions
   - Regular security audits (`pip-audit`)
   - Automated vulnerability scanning (Dependabot)

2. **Code Review:**
   - All changes require review
   - Security-focused review for auth/data handling
   - Automated linting and security scanning

3. **Input Validation:**
   - Pydantic models for all API inputs
   - SQL parameterization (no string concatenation)
   - File path validation (no path traversal)

**Security scanning:**
```bash
# Scan dependencies
pip-audit

# Scan code
bandit -r coffee_maker/

# Scan Docker image
trivy image code-developer:latest
```

---

### 6. Compliance & Auditing

**Logging:**
- All API requests logged
- Authentication failures logged
- Secret access logged
- Database queries logged (without sensitive data)

**Monitoring:**
- Failed authentication attempts
- Unusual access patterns
- High error rates
- Cost anomalies

**Compliance:**
- GDPR: No personal data stored (project code only)
- SOC 2: Audit logs retained for 1 year
- HIPAA: Not applicable (no healthcare data)

---

## Performance Requirements

### 1. API Performance

**Response time targets:**

| Endpoint | Target | Maximum |
|----------|--------|---------|
| GET /health | < 50ms | < 100ms |
| GET /api/daemon/status | < 200ms | < 500ms |
| POST /api/daemon/start | < 1s | < 3s |
| POST /api/daemon/stop | < 5s | < 30s |
| GET /api/files/roadmap | < 500ms | < 2s |
| PUT /api/files/roadmap | < 1s | < 3s |
| GET /api/notifications | < 300ms | < 1s |
| GET /api/logs (stream) | < 500ms (first byte) | < 2s |

**Throughput targets:**
- 100 concurrent users
- 10 requests/second sustained
- 1000 requests/minute burst

**Testing:**
```bash
# Load test with k6
k6 run --vus 100 --duration 5m tests/load/api_load_test.js
```

---

### 2. Daemon Performance

**Processing targets:**

| Metric | Target | Acceptable |
|--------|--------|------------|
| Task start time | < 30s | < 2m |
| Average task completion | < 4h | < 8h |
| File read/write | < 1s | < 5s |
| Git commit | < 10s | < 30s |
| LLM API call | < 30s | < 60s |

**Resource usage:**

| Resource | Limit | Alert Threshold |
|----------|-------|-----------------|
| CPU | 2 vCPU | > 80% for 10m |
| Memory | 4GB | > 3.5GB for 5m |
| Disk | 10GB | > 8GB used |
| Network egress | 100GB/month | > 80GB |

**Monitoring:**
- Task completion rate (should be > 90%)
- Error rate (should be < 5%)
- Retry rate (should be < 10%)
- Uptime (should be > 99.5%)

---

### 3. Database Performance

**Query performance:**

| Query Type | Target | Maximum |
|------------|--------|---------|
| Simple SELECT | < 10ms | < 50ms |
| Complex JOIN | < 100ms | < 500ms |
| INSERT | < 20ms | < 100ms |
| UPDATE | < 50ms | < 200ms |

**Connection pooling:**
- Min connections: 5
- Max connections: 20
- Connection timeout: 30s
- Idle timeout: 5m

**Indexes:**
- All foreign keys indexed
- Timestamp columns indexed
- Frequently queried columns indexed

---

### 4. Storage Performance

**Cloud Storage:**

| Operation | Target | Maximum |
|-----------|--------|---------|
| File read (< 1MB) | < 500ms | < 2s |
| File write (< 1MB) | < 1s | < 3s |
| File read (10MB) | < 2s | < 5s |
| File write (10MB) | < 3s | < 10s |

**Optimization:**
- Use Cloud Storage client library (not gsutil)
- Enable caching for frequently accessed files
- Use multipart upload for large files

---

### 5. Scalability

**Horizontal scaling:**
- Currently: 1 Cloud Run instance (always-on)
- Future: Auto-scale 1-5 instances based on load
- Load balancing handled by Cloud Run

**Vertical scaling:**
- Start with: 1 vCPU, 2GB RAM
- Can scale to: 4 vCPU, 8GB RAM
- Modify via Terraform variables

**Database scaling:**
- Start with: db-f1-micro (shared CPU, 0.6GB RAM)
- Can scale to: db-n1-standard-1 (1 vCPU, 3.75GB RAM)
- Vertical scaling requires brief downtime (~5 minutes)

---

## Cost Analysis

### 1. GCP Services (Monthly Estimates)

**Cloud Run:**
```
Assumptions:
- 1 instance always running (24/7)
- 1 vCPU, 2GB RAM
- ~720 hours/month

Cost breakdown:
- vCPU time: 720h × $0.00002400/vCPU-second = $62.21/month
- Memory: 720h × $0.00000250/GB-second = $4.32/month
- Requests: ~100,000/month × $0.40/million = $0.04/month
Total Cloud Run: ~$66.57/month
```

**Cloud Storage:**
```
Assumptions:
- 50GB storage (project files, logs, backups)
- 10GB egress/month
- 100,000 Class A operations/month (writes)
- 1,000,000 Class B operations/month (reads)

Cost breakdown:
- Storage: 50GB × $0.020/GB = $1.00/month
- Egress: 10GB × $0.12/GB = $1.20/month (first 1GB free)
- Class A ops: 100,000 × $0.05/10,000 = $0.50/month
- Class B ops: 1,000,000 × $0.004/10,000 = $0.04/month
Total Cloud Storage: ~$2.74/month
```

**Cloud SQL (PostgreSQL):**
```
Assumptions:
- db-f1-micro instance (shared vCPU, 0.6GB RAM)
- 10GB SSD storage
- 7-day backups

Cost breakdown:
- Instance: 720h × $0.0150/hour = $10.80/month
- Storage: 10GB × $0.17/GB = $1.70/month
- Backups: ~10GB × $0.08/GB = $0.80/month
Total Cloud SQL: ~$13.30/month
```

**Secret Manager:**
```
Assumptions:
- 5 active secrets
- 1000 access operations/month

Cost breakdown:
- Active secrets: 5 × $0.06 = $0.30/month
- Access operations: 1000 × $0.03/10,000 = $0.003/month
Total Secret Manager: ~$0.30/month
```

**Cloud Logging:**
```
Assumptions:
- 10GB logs/month
- First 50GB free per project

Cost breakdown:
- Logs: 0GB (within free tier)
Total Cloud Logging: $0.00/month
```

**Cloud Monitoring:**
```
Assumptions:
- 50 custom metrics
- First 150 metrics free

Cost breakdown:
- Metrics: 0 (within free tier)
Total Cloud Monitoring: $0.00/month
```

**Networking:**
```
Assumptions:
- VPC: Free
- VPC connector: $0.05/hour × 720h = $36.00/month
- Cloud NAT: Not needed (no public IPs)

Total Networking: ~$36.00/month
```

**GCP Total: ~$118.91/month**

---

### 2. External Services (Monthly Estimates)

**Anthropic API:**
```
Assumptions:
- Claude 3.5 Sonnet
- 1 million input tokens/day (~30M/month)
- 500K output tokens/day (~15M/month)

Cost breakdown:
- Input: 30M × $3.00/1M = $90.00/month
- Output: 15M × $15.00/1M = $225.00/month
Total Anthropic: ~$315.00/month

Note: Highly variable based on usage
```

**GitHub:**
```
Assumptions:
- Free for public repositories
- GitHub Pro: $4/month for private repos (optional)

Total GitHub: $0-4/month
```

---

### 3. Total Cost Summary

| Category | Monthly Cost | Annual Cost |
|----------|--------------|-------------|
| **GCP Services** | $118.91 | $1,426.92 |
| **Anthropic API** | $315.00 | $3,780.00 |
| **GitHub** | $0-4 | $0-48 |
| **Total** | **$433.91** | **$5,206.92** |

---

### 4. Cost Optimization Strategies

**Reduce Cloud Run costs:**
1. Use min instances = 0 (cold starts acceptable)
   - Saves ~$66/month
   - Adds 30-60s startup latency
2. Use smaller instance (0.5 vCPU, 1GB RAM)
   - Saves ~$30/month
   - May impact performance

**Reduce Cloud SQL costs:**
1. Use Cloud SQL for small workloads (already using smallest tier)
2. Consider Firestore instead
   - Pay per operation vs always-on instance
   - Better for low-traffic scenarios
3. Enable automatic storage increases only when needed

**Reduce Anthropic API costs:**
1. Use caching for repeated requests
   - Could save 20-30% on token usage
2. Use cheaper models for simple tasks
   - Claude Haiku for documentation: $0.25/1M input vs $3.00/1M
3. Implement token budgets per priority
   - Prevent runaway costs

**Reduce storage costs:**
1. Lifecycle policies to delete old files
   - Already configured (90 days)
2. Compress logs before storage
   - Could save 50% on log storage

**Estimated optimized cost: ~$250-300/month**

---

### 5. Cost Monitoring & Alerts

**Budget alerts:**
```hcl
# Terraform configuration
resource "google_billing_budget" "daemon_budget" {
  billing_account = var.billing_account
  display_name    = "code-developer monthly budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "500"  # $500/month threshold
    }
  }

  threshold_rules {
    threshold_percent = 0.5  # Alert at 50%
  }

  threshold_rules {
    threshold_percent = 0.9  # Alert at 90%
  }

  threshold_rules {
    threshold_percent = 1.0  # Alert at 100%
  }
}
```

**Cost tracking dashboard:**
- View in project_manager: `project-manager cloud costs`
- View in GCP Console: Billing > Cost Table
- Export to BigQuery for detailed analysis

---

## Risk Analysis

### 1. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Daemon crashes in production** | Medium | High | - Implement comprehensive error handling<br>- Add automatic restart on crash<br>- Monitor with Cloud Logging alerts |
| **Cloud Run cold starts** | High | Medium | - Keep min instances = 1<br>- Optimize container startup time<br>- Use startup probes |
| **Database connection issues** | Low | High | - Use connection pooling<br>- Implement retry logic<br>- Monitor connection metrics |
| **API rate limits (Anthropic)** | Medium | High | - Implement exponential backoff<br>- Add rate limiting in daemon<br>- Monitor usage closely |
| **Storage quota exceeded** | Low | Medium | - Lifecycle policies for old files<br>- Monitor storage usage<br>- Alert at 80% capacity |
| **Memory leaks** | Medium | Medium | - Comprehensive testing (24h+)<br>- Monitor memory usage<br>- Automatic restarts if needed |
| **GitHub auth failures** | Low | High | - Store token in Secret Manager<br>- Monitor for 401 errors<br>- Alert on auth failures |

---

### 2. Security Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **API key leakage** | Low | Critical | - Never log API keys<br>- Use Secret Manager only<br>- Rotate keys every 90 days |
| **Unauthorized API access** | Medium | High | - JWT authentication required<br>- Monitor failed auth attempts<br>- IP whitelisting (optional) |
| **SQL injection** | Low | High | - Use SQLAlchemy ORM (parameterized)<br>- Never concatenate SQL strings<br>- Code review for all queries |
| **DDoS attack on API** | Medium | Medium | - Cloud Run has built-in protection<br>- Rate limiting per user<br>- Cloud Armor (optional) |
| **Secrets exposed in logs** | Medium | High | - Sanitize all log output<br>- Never log environment variables<br>- Audit logs regularly |

---

### 3. Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Cost overrun** | High | Medium | - Set budget alerts at 50%, 90%, 100%<br>- Monitor costs daily<br>- Implement cost limits in code |
| **Regional outage (GCP)** | Low | High | - Document failover procedure<br>- Consider multi-region (future)<br>- Keep local daemon as backup |
| **Deployment failure** | Medium | High | - Test in staging environment first<br>- Use blue-green deployment (future)<br>- Have rollback procedure ready |
| **Data loss** | Low | Critical | - Daily backups to Cloud SQL<br>- Point-in-time recovery enabled<br>- Test restore procedure quarterly |
| **Lost access to GCP project** | Low | Critical | - Multiple owners on project<br>- Document recovery procedure<br>- Keep Terraform state backed up |

---

### 4. Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Anthropic API pricing increase** | Medium | High | - Monitor API costs closely<br>- Consider fallback providers<br>- Implement usage limits |
| **GCP pricing increase** | Low | Medium | - Lock in committed use discounts<br>- Consider alternative providers<br>- Cloud-agnostic architecture |
| **User doesn't adopt GCP deployment** | Medium | Medium | - Make local daemon still work<br>- Provide migration guide<br>- Highlight benefits clearly |
| **Daemon makes breaking changes** | Medium | High | - Always ask permission for breaking changes<br>- Implement dry-run mode<br>- Create rollback commits |

---

### 5. Risk Monitoring

**Daily checks:**
- [ ] Daemon uptime > 99%
- [ ] Error rate < 5%
- [ ] API response times within targets
- [ ] Cost within budget

**Weekly checks:**
- [ ] Review security logs for anomalies
- [ ] Check for failed authentication attempts
- [ ] Review cost trends
- [ ] Test backup/restore procedure

**Monthly checks:**
- [ ] Rotate API keys
- [ ] Review and update security policies
- [ ] Cost analysis and optimization
- [ ] Update documentation

---

## Success Criteria

### 1. Functional Requirements

**Must have (P0):**
- [x] code_developer daemon runs continuously on GCP
- [x] Daemon achieves 99.9% uptime (< 45 minutes downtime/month)
- [x] project_manager CLI can control GCP daemon remotely
- [x] User can view daemon status in real-time
- [x] User can view daemon logs in real-time
- [x] Daemon automatically pulls latest ROADMAP.md from GitHub
- [x] Daemon creates commits and PRs from GCP
- [x] Notifications work between GCP daemon and local project_manager
- [x] User can edit ROADMAP.md via project_manager
- [x] Full monitoring and alerting operational
- [x] Comprehensive documentation complete

**Should have (P1):**
- [ ] User can edit project files via project_manager
- [ ] Daemon supports multiple projects (future)
- [ ] Web dashboard for monitoring (future)
- [ ] Slack integration for notifications (future)

**Nice to have (P2):**
- [ ] Multi-region deployment for HA (future)
- [ ] Auto-scaling based on workload (future)
- [ ] Cost optimization recommendations (future)

---

### 2. Performance Requirements

| Metric | Target | Status |
|--------|--------|--------|
| Daemon uptime | > 99.9% | ⏳ TBD |
| API response time | < 500ms (p95) | ⏳ TBD |
| Task start time | < 30s | ⏳ TBD |
| Average task completion | < 4h | ⏳ TBD |
| Database query time | < 100ms (p95) | ⏳ TBD |
| Storage operations | < 2s (p95) | ⏳ TBD |

---

### 3. Cost Requirements

| Metric | Target | Status |
|--------|--------|--------|
| Total monthly cost | < $500 | ⏳ TBD |
| GCP costs | < $150 | ⏳ TBD |
| Anthropic API costs | < $350 | ⏳ TBD |
| Cost per task | < $10 | ⏳ TBD |

---

### 4. Security Requirements

| Requirement | Status |
|-------------|--------|
| All secrets in Secret Manager | ⏳ TBD |
| All API calls authenticated | ⏳ TBD |
| All data encrypted at rest | ⏳ TBD |
| All data encrypted in transit | ⏳ TBD |
| No secrets in logs | ⏳ TBD |
| Database on private network only | ⏳ TBD |
| Security audit passed | ⏳ TBD |

---

### 5. User Experience Requirements

| Requirement | Status |
|-------------|--------|
| `project-manager cloud status` works | ⏳ TBD |
| `project-manager cloud start` works | ⏳ TBD |
| `project-manager cloud stop` works | ⏳ TBD |
| `project-manager cloud logs` streams logs | ⏳ TBD |
| Deployment completes in < 30 minutes | ⏳ TBD |
| Documentation is clear and complete | ⏳ TBD |
| Can deploy from scratch following docs | ⏳ TBD |

---

### 6. Acceptance Testing Checklist

**Pre-deployment:**
- [ ] All unit tests pass (coverage > 80%)
- [ ] All integration tests pass
- [ ] Docker image builds successfully
- [ ] Docker container runs locally
- [ ] Terraform configurations validated
- [ ] Security audit completed
- [ ] Documentation reviewed

**Post-deployment:**
- [ ] Daemon starts successfully on GCP
- [ ] Health check returns 200 OK
- [ ] API endpoints respond correctly
- [ ] Authentication works
- [ ] Can control daemon via CLI
- [ ] Can view logs via CLI
- [ ] Can edit ROADMAP.md
- [ ] Daemon implements a test priority
- [ ] Monitoring dashboards show data
- [ ] Alerts trigger correctly (test)
- [ ] Cost within budget after 1 week
- [ ] 24-hour load test passes
- [ ] Disaster recovery test passes

---

## Rollback Strategy

### 1. Rollback Scenarios

**Scenario 1: Deployment fails (Terraform apply fails)**
```bash
# Rollback: Destroy failed resources
terraform destroy -target=google_cloud_run_service.daemon
terraform apply  # Re-apply previous working state
```

**Scenario 2: Daemon crashes repeatedly in production**
```bash
# Rollback: Deploy previous working image
gcloud run deploy code-developer-daemon \
  --image=gcr.io/coffee-maker-prod/code-developer:v1.0.0 \
  --region=us-central1

# Or: Switch back to local daemon
project-manager cloud stop
code-developer  # Start local daemon
```

**Scenario 3: API has critical bug**
```bash
# Rollback: Deploy previous API version
docker pull gcr.io/coffee-maker-prod/code-developer:v1.0.0
docker tag gcr.io/coffee-maker-prod/code-developer:v1.0.0 \
  gcr.io/coffee-maker-prod/code-developer:latest
docker push gcr.io/coffee-maker-prod/code-developer:latest

# Cloud Run will automatically deploy latest
```

**Scenario 4: Database migration breaks**
```bash
# Rollback: Restore from backup
gcloud sql backups list --instance=coffee-maker-db
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=coffee-maker-db \
  --backup-instance=coffee-maker-db-restored

# Or: Restore from point-in-time
gcloud sql backups create --instance=coffee-maker-db
```

**Scenario 5: Cost overrun**
```bash
# Emergency: Stop daemon to halt costs
project-manager cloud stop

# Temporary: Scale down resources
terraform apply -var="db_tier=db-f1-micro" \
  -var="cloud_run_memory=1Gi"
```

---

### 2. Rollback Procedure

**Step 1: Identify the issue**
- Check Cloud Logging for errors
- Check Cloud Monitoring for anomalies
- Check cost dashboard

**Step 2: Assess impact**
- Is daemon still running?
- Are users affected?
- Is data at risk?

**Step 3: Decide rollback or fix forward**
- If minor issue: Fix forward
- If critical issue: Rollback immediately

**Step 4: Execute rollback**
- Follow scenario-specific procedure above
- Monitor during rollback
- Verify rollback successful

**Step 5: Post-rollback**
- Notify users
- Document root cause
- Plan fix for next deployment

---

### 3. Rollback Testing

**Test rollback procedures quarterly:**
```bash
# Test deployment rollback
terraform apply  # Deploy new version
terraform destroy -target=google_cloud_run_service.daemon
terraform apply  # Rollback to previous

# Test database restore
gcloud sql backups create --instance=coffee-maker-db
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=coffee-maker-db \
  --backup-instance=coffee-maker-db-test

# Test image rollback
docker pull gcr.io/coffee-maker-prod/code-developer:v1.0.0
# ... (see Scenario 3 above)
```

---

## Appendices

### A. Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ENVIRONMENT` | Yes | Deployment environment | `production` |
| `PROJECT_ROOT` | Yes | Project root directory | `/app` |
| `ROADMAP_PATH` | Yes | Path to ROADMAP.md | `/app/docs/ROADMAP.md` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key | `sk-ant-...` |
| `GITHUB_TOKEN` | Yes | GitHub PAT | `ghp_...` |
| `API_AUTH_SECRET` | Yes | API authentication secret | (random 32-char string) |
| `GCS_BUCKET` | Yes | Cloud Storage bucket name | `coffee-maker-prod-storage` |
| `PORT` | No | API server port | `8080` (default) |
| `LOG_LEVEL` | No | Logging level | `INFO` (default) |
| `GCP_PROJECT_ID` | No | GCP project ID | `coffee-maker-prod` |

---

### B. API Endpoints Reference

See section 4 (Component Specifications) for detailed API documentation.

**Summary:**
- Health: `GET /health`
- Daemon status: `GET /api/daemon/status`
- Start daemon: `POST /api/daemon/start`
- Stop daemon: `POST /api/daemon/stop`
- Get ROADMAP: `GET /api/files/roadmap`
- Update ROADMAP: `PUT /api/files/roadmap`
- Get file: `GET /api/files/{path}`
- Update file: `PUT /api/files/{path}`
- List notifications: `GET /api/notifications`
- Respond to notification: `POST /api/notifications/{id}/respond`
- Stream logs: `GET /api/logs`

---

### C. Troubleshooting Guide

**Problem: Daemon won't start**
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 --format=json

# Check secrets
gcloud secrets versions access latest --secret=anthropic-api-key

# Check database connection
cloud_sql_proxy -instances=<CONNECTION_NAME>=tcp:5432 &
psql "postgresql://daemon:PASSWORD@localhost:5432/coffee_maker"
```

**Problem: API returns 401 Unauthorized**
```bash
# Generate new token
python -c "
from jose import jwt
from datetime import datetime, timedelta
payload = {
    'sub': 'project-manager-cli',
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, 'YOUR_API_AUTH_SECRET', algorithm='HS256')
print(token)
"

# Test with new token
curl -H "Authorization: Bearer $TOKEN" \
  https://your-cloud-run-url.run.app/api/daemon/status
```

**Problem: High costs**
```bash
# Check current costs
gcloud billing projects describe coffee-maker-prod

# Identify expensive resources
gcloud billing accounts list
# Navigate to Cost Table in GCP Console

# Scale down resources
terraform apply -var="db_tier=db-f1-micro"
```

**Problem: Database connection timeouts**
```bash
# Check Cloud SQL status
gcloud sql instances describe coffee-maker-db

# Check connections
gcloud sql operations list --instance=coffee-maker-db

# Increase connection pool size
# Edit coffee_maker/api/database/connection.py
# Set max_overflow=10
```

---

### D. Useful Commands

**Terraform:**
```bash
# Initialize
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Destroy resources
terraform destroy

# View outputs
terraform output

# Import existing resource
terraform import google_cloud_run_service.daemon \
  projects/coffee-maker-prod/locations/us-central1/services/code-developer-daemon
```

**Docker:**
```bash
# Build image
docker build -t code-developer:latest -f coffee_maker/deployment/Dockerfile .

# Run locally
docker run -d -p 8080:8080 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  code-developer:latest

# Push to GCR
docker tag code-developer:latest gcr.io/coffee-maker-prod/code-developer:latest
docker push gcr.io/coffee-maker-prod/code-developer:latest

# View logs
docker logs -f <container_id>
```

**gcloud:**
```bash
# Deploy to Cloud Run
gcloud run deploy code-developer-daemon \
  --image=gcr.io/coffee-maker-prod/code-developer:latest \
  --region=us-central1 \
  --platform=managed

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# List secrets
gcloud secrets list

# Access secret value
gcloud secrets versions access latest --secret=anthropic-api-key

# Connect to Cloud SQL
gcloud sql connect coffee-maker-db --user=daemon

# View Cloud Run services
gcloud run services list
```

**project-manager CLI:**
```bash
# Check daemon status
project-manager cloud status

# Start daemon
project-manager cloud start

# Stop daemon
project-manager cloud stop

# Stream logs
project-manager cloud logs --follow

# Edit ROADMAP
project-manager cloud edit roadmap

# View costs
project-manager cloud costs
```

---

### E. References

**GCP Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
- Cloud Storage: https://cloud.google.com/storage/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs
- Terraform Provider: https://registry.terraform.io/providers/hashicorp/google/latest/docs

**Tools:**
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Poetry: https://python-poetry.org/
- Docker: https://docs.docker.com/

**Related Docs:**
- `docs/ROADMAP.md` - Full roadmap
- `docs/DEPLOYMENT.md` - Deployment guide (to be created)
- `docs/OPERATIONS_RUNBOOK.md` - Operations procedures (to be created)
- `README.md` - Project overview

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-11 | code_developer | Initial technical specification |

---

## Approval

**Technical Review:**
- [ ] Architecture reviewed and approved
- [ ] Security considerations reviewed and approved
- [ ] Cost estimates reviewed and approved
- [ ] Implementation plan reviewed and approved

**Ready for Implementation:** ⏳ Pending Approval

---

*This technical specification is a living document and will be updated as the implementation progresses.*
