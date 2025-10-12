# GCP Deployment Guide for code_developer

**Version**: 1.0
**Last Updated**: 2025-10-12
**Estimated Deployment Time**: 2-4 hours (first time), 30 minutes (subsequent deploys)

This guide walks you through deploying the `code_developer` autonomous daemon to Google Cloud Platform (GCP) for 24/7 operation.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Monitoring](#monitoring)
8. [Cost Management](#cost-management)
9. [Next Steps](#next-steps)

---

## Overview

### What You're Deploying

This deployment creates a **fully autonomous, always-on code_developer** running on GCP Cloud Run that:

- ✅ Runs 24/7 without local machine dependency
- ✅ Reads `ROADMAP.md` from your GitHub repository
- ✅ Implements features autonomously using Claude API
- ✅ Creates branches, commits, and pull requests
- ✅ Sends notifications via database (accessible from local `project-manager`)
- ✅ Provides FastAPI control interface for remote management
- ✅ Automatically scales based on load
- ✅ Logs all activity to Cloud Logging

### Why Deploy to GCP?

**Current Limitation**: Running `code-developer` locally means:
- Daemon stops when laptop sleeps
- No work happens when you're away
- Vulnerable to local crashes/network issues

**GCP Solution**:
- **Always available**: Continues working even when you're offline
- **Reliable**: 99.9% uptime with automatic restarts
- **Scalable**: Can run multiple projects simultaneously
- **Observable**: Centralized logging and monitoring
- **Cost-effective**: Pay only for what you use (~$60-95/month)

---

## Prerequisites

### Required Accounts & Services

| Service | Purpose | Cost | Setup Link |
|---------|---------|------|------------|
| **GCP Account** | Infrastructure hosting | ~$60-95/month | [console.cloud.google.com](https://console.cloud.google.com) |
| **Anthropic API** | Claude API for code generation | Variable ($50-200/month) | [console.anthropic.com](https://console.anthropic.com) |
| **GitHub Account** | Repository hosting & authentication | Free (public repos) | [github.com](https://github.com) |

### Local Development Environment

**Required Tools**:
```bash
# Check your versions
python --version          # Need: Python 3.11+
docker --version          # Need: Docker 20.10+
git --version            # Need: Git 2.40+
gcloud --version         # Need: Google Cloud SDK 400.0+
terraform --version      # Need: Terraform 1.5+

# If missing, install:
# macOS (Homebrew)
brew install python@3.11 docker git google-cloud-sdk terraform

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.11 docker.io git
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### API Keys & Credentials

**1. Anthropic API Key**:
```bash
# Get from: https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Verify it works:
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

**2. GitHub Personal Access Token**:
```bash
# Create at: https://github.com/settings/tokens/new
# Required scopes: repo, workflow, write:packages
export GITHUB_TOKEN="ghp_..."

# Verify it works:
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**3. GCP Project**:
```bash
# Create new project or use existing
export GCP_PROJECT_ID="my-code-developer-project"
export GCP_REGION="us-central1"

# Authenticate gcloud
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
```

---

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Local Machine                      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  project_manager CLI                                   │  │
│  │  $ project-manager cloud status                       │  │
│  │  $ project-manager cloud logs                         │  │
│  │  $ project-manager notifications                      │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │ HTTPS (Authenticated)                     │
└──────────────────┼───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Platform (GCP)                     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Run Service                                     │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  code_developer Container                       │ │  │
│  │  │  - FastAPI Control API (port 8080)              │ │  │
│  │  │  - DevDaemon autonomous loop                    │ │  │
│  │  │  - GitManager (commits, PRs)                    │ │  │
│  │  │  - ClaudeAPI (code generation)                  │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                                │  │
│  │  - notifications table (shared with local CLI)        │  │
│  │  - task_metrics table (performance tracking)          │  │
│  │  - developer_status (real-time status)                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Storage                                         │  │
│  │  - ROADMAP.md (synced from GitHub)                    │  │
│  │  - Logs and checkpoints                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Secret Manager                                        │  │
│  │  - ANTHROPIC_API_KEY                                  │  │
│  │  - GITHUB_TOKEN                                       │  │
│  │  - DATABASE_URL                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Logging + Monitoring                            │  │
│  │  - Daemon activity logs                               │  │
│  │  - Performance metrics                                │  │
│  │  - Alerting rules                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### GCP Services Used

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| **Cloud Run** | Serverless container hosting | $20-30/month (1vCPU, 2GB RAM, 24/7) |
| **Cloud SQL** | PostgreSQL database | $25-35/month (db-f1-micro) |
| **Cloud Storage** | File storage | $5-10/month (50GB) |
| **Secret Manager** | Secure credential storage | $1-2/month |
| **Cloud Logging** | Centralized logs | $5-10/month |
| **Cloud Monitoring** | Metrics and alerts | Free tier |
| **Networking** | Data transfer | $5-10/month |
| **Total** | | **~$60-95/month** |

---

## Step-by-Step Deployment

### Phase 1: Local Testing (30 minutes)

**Test the container locally before deploying to GCP**.

#### Step 1.1: Build and Test Container Locally

```bash
# Navigate to project root
cd /path/to/MonolithicCoffeeMakerAgent

# Create .env file with your credentials
cat > coffee_maker/deployment/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-...
GITHUB_TOKEN=ghp_...
COFFEE_MAKER_API_KEY=dev-test-key-12345
EOF

# Build and start services
cd coffee_maker/deployment
docker-compose up -d

# View logs
docker-compose logs -f code-developer

# Expected output:
# code-developer-daemon | 🤖 DevDaemon starting...
# code-developer-daemon | ✅ Claude API available
# code-developer-daemon | ✅ Git repository ready
# code-developer-daemon | ✅ ROADMAP.md found
# code-developer-daemon | 📋 Next priority: PRIORITY X - Title
```

#### Step 1.2: Verify Container Health

```bash
# Check health endpoint
curl http://localhost:8080/api/health

# Expected response:
# {
#   "status": "healthy",
#   "daemon_status": "running",
#   "current_priority": "PRIORITY X",
#   "uptime_seconds": 120
# }

# Check daemon status via API
curl http://localhost:8080/api/daemon/status \
  -H "Authorization: Bearer dev-test-key-12345"

# Test notifications (from local CLI)
poetry run project-manager notifications

# Stop local test
docker-compose down
```

**✅ Checkpoint**: Container runs successfully locally before moving to GCP.

---

### Phase 2: GCP Infrastructure Setup (45-60 minutes)

#### Step 2.1: Enable Required APIs

```bash
# Set project
export GCP_PROJECT_ID="my-code-developer-project"
gcloud config set project $GCP_PROJECT_ID

# Enable APIs (takes 2-3 minutes)
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudbuild.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled
```

#### Step 2.2: Create Secret Manager Secrets

```bash
# Create secrets for sensitive data
echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "$GITHUB_TOKEN" | gcloud secrets create github-token \
  --data-file=- \
  --replication-policy="automatic"

# Generate secure API key for control API
COFFEE_MAKER_API_KEY=$(openssl rand -base64 32)
echo -n "$COFFEE_MAKER_API_KEY" | gcloud secrets create coffee-maker-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Save API key locally for project-manager CLI
mkdir -p ~/.config/coffee-maker
cat > ~/.config/coffee-maker/gcp.yaml << EOF
gcp:
  enabled: true
  api_url: https://code-developer-HASH.run.app  # Update after deployment
  api_key: $COFFEE_MAKER_API_KEY
  project_id: $GCP_PROJECT_ID
  region: us-central1
EOF

# Verify secrets created
gcloud secrets list
```

#### Step 2.3: Create Cloud SQL Database

```bash
# Create PostgreSQL instance (takes 5-10 minutes)
gcloud sql instances create code-developer-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=$(openssl rand -base64 20) \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup \
  --backup-start-time=03:00

# Create database
gcloud sql databases create coffee_maker \
  --instance=code-developer-db

# Create user
gcloud sql users create coffee_maker \
  --instance=code-developer-db \
  --password=$(openssl rand -base64 20)

# Get connection name
export DB_CONNECTION_NAME=$(gcloud sql instances describe code-developer-db \
  --format="value(connectionName)")

echo "Database connection name: $DB_CONNECTION_NAME"

# Store database URL in Secret Manager
DB_PASSWORD=$(gcloud sql users list --instance=code-developer-db \
  --filter="name=coffee_maker" --format="value(password)")

DATABASE_URL="postgresql://coffee_maker:$DB_PASSWORD@/coffee_maker?host=/cloudsql/$DB_CONNECTION_NAME"
echo -n "$DATABASE_URL" | gcloud secrets create database-url \
  --data-file=- \
  --replication-policy="automatic"
```

#### Step 2.4: Create Cloud Storage Bucket

```bash
# Create bucket for logs and state
gsutil mb -p $GCP_PROJECT_ID \
  -c STANDARD \
  -l us-central1 \
  gs://${GCP_PROJECT_ID}-code-developer

# Enable versioning
gsutil versioning set on gs://${GCP_PROJECT_ID}-code-developer

# Set lifecycle policy (delete old logs after 30 days)
cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://${GCP_PROJECT_ID}-code-developer
rm lifecycle.json
```

---

### Phase 3: Deploy to Cloud Run (30 minutes)

#### Step 3.1: Build and Push Container Image

```bash
# Navigate to project root
cd /path/to/MonolithicCoffeeMakerAgent

# Build container using Cloud Build (recommended)
gcloud builds submit \
  --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --dockerfile=coffee_maker/deployment/Dockerfile \
  .

# Alternative: Build locally and push
# docker build -t gcr.io/$GCP_PROJECT_ID/code-developer:latest \
#   -f coffee_maker/deployment/Dockerfile .
# docker push gcr.io/$GCP_PROJECT_ID/code-developer:latest

# Verify image
gcloud container images list --repository=gcr.io/$GCP_PROJECT_ID
```

#### Step 3.2: Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy code-developer \
  --image gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --no-allow-unauthenticated \
  --set-env-vars "COFFEE_MAKER_MODE=daemon,COFFEE_MAKER_LOG_LEVEL=INFO,COFFEE_MAKER_AUTO_APPROVE=true,COFFEE_MAKER_CREATE_PRS=true" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest,GITHUB_TOKEN=github-token:latest,DATABASE_URL=database-url:latest,API_KEY=coffee-maker-api-key:latest" \
  --add-cloudsql-instances $DB_CONNECTION_NAME \
  --service-account code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# Get service URL
export SERVICE_URL=$(gcloud run services describe code-developer \
  --platform managed \
  --region us-central1 \
  --format "value(status.url)")

echo "Service deployed at: $SERVICE_URL"

# Update local config with actual URL
sed -i.bak "s|api_url: https://code-developer-HASH.run.app|api_url: $SERVICE_URL|" \
  ~/.config/coffee-maker/gcp.yaml
```

#### Step 3.3: Configure IAM Permissions

```bash
# Create service account
gcloud iam service-accounts create code-developer \
  --display-name "code_developer autonomous daemon" \
  --description "Service account for code_developer running on Cloud Run"

# Grant permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

# Redeploy with service account
gcloud run services update code-developer \
  --region us-central1 \
  --service-account code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

---

## Configuration

### Environment Variables

The daemon is configured via environment variables set in Cloud Run:

| Variable | Purpose | Example |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude API authentication | `sk-ant-api03-...` (from Secret Manager) |
| `GITHUB_TOKEN` | GitHub API access | `ghp_...` (from Secret Manager) |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` (from Secret Manager) |
| `API_KEY` | Control API authentication | Auto-generated (from Secret Manager) |
| `COFFEE_MAKER_MODE` | Run mode | `daemon` (default) |
| `COFFEE_MAKER_LOG_LEVEL` | Logging verbosity | `INFO` (DEBUG for troubleshooting) |
| `COFFEE_MAKER_AUTO_APPROVE` | Auto-approve priorities | `true` (fully autonomous) |
| `COFFEE_MAKER_CREATE_PRS` | Auto-create PRs | `true` |
| `ROADMAP_PATH` | Path to roadmap | `/workspace/docs/ROADMAP.md` |
| `GCS_BUCKET_NAME` | Cloud Storage bucket | `${GCP_PROJECT_ID}-code-developer` |

### Local project_manager Configuration

**File**: `~/.config/coffee-maker/gcp.yaml`

```yaml
gcp:
  enabled: true
  api_url: https://code-developer-abc123.run.app
  api_key: your-api-key-from-secret-manager
  project_id: my-code-developer-project
  region: us-central1

  # Optional settings
  daemon:
    auto_start: true
    check_interval: 30  # seconds
    notify_on_completion: true
```

**Usage from local CLI**:
```bash
# Check GCP daemon status
poetry run project-manager cloud status

# Stream logs from GCP
poetry run project-manager cloud logs --follow

# View notifications (works with GCP database)
poetry run project-manager notifications

# Respond to daemon questions
poetry run project-manager respond <notification-id> approve
```

---

## Verification

### Step 1: Check Deployment Health

```bash
# Test health endpoint
curl $SERVICE_URL/api/health

# Expected response:
# {
#   "status": "healthy",
#   "daemon_status": "running",
#   "database": "connected",
#   "claude_api": "available",
#   "github": "authenticated"
# }
```

### Step 2: Verify Daemon is Running

```bash
# Check daemon status via API
curl -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/daemon/status

# Expected response:
# {
#   "status": "running",
#   "state": "WORKING",
#   "current_priority": {
#     "name": "PRIORITY 6.5",
#     "title": "GCP Deployment",
#     "progress": 45
#   },
#   "uptime_seconds": 3600,
#   "iteration": 12,
#   "crashes": 0
# }
```

### Step 3: Check Cloud Logging

```bash
# Stream logs from Cloud Run
gcloud run services logs read code-developer \
  --platform managed \
  --region us-central1 \
  --limit 50

# Follow logs in real-time
gcloud run services logs tail code-developer \
  --platform managed \
  --region us-central1

# Look for:
# ✅ DevDaemon starting...
# ✅ Claude API available
# ✅ Git repository ready
# 📋 Next priority: PRIORITY X
```

### Step 4: Verify GitHub Integration

```bash
# Check that daemon can create commits
# Watch your repository for new branches/commits from code_developer

# Check recent commits
gh api repos/YOUR_USERNAME/YOUR_REPO/commits --jq '.[0:3] | .[] | {sha:.sha[0:7], message:.commit.message, author:.commit.author.name}'

# Look for commits from "code_developer"
```

### Step 5: Test Notifications

```bash
# From local machine
poetry run project-manager notifications

# Should show notifications from GCP daemon
# If daemon asked a question, respond:
poetry run project-manager respond <notification-id> approve
```

**✅ Success Criteria**:
- [x] Health endpoint returns "healthy"
- [x] Daemon status shows "running"
- [x] Logs show successful iteration loop
- [x] Can see commits/branches created by daemon
- [x] Notifications work from local CLI
- [x] No errors in Cloud Logging

---

## Monitoring

### Cloud Monitoring Dashboard

**Create monitoring dashboard**:

```bash
# Create dashboard JSON
cat > dashboard.json << 'EOF'
{
  "displayName": "code_developer Daemon Health",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run CPU Utilization",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"code-developer\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF

# Upload dashboard
gcloud monitoring dashboards create --config-from-file dashboard.json
```

### Alerting Rules

**Set up critical alerts**:

```bash
# Alert when daemon crashes
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="code_developer Crash Alert" \
  --condition-display-name="Daemon crashed" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s \
  --condition-expression='
    resource.type="cloud_run_revision"
    AND resource.labels.service_name="code-developer"
    AND severity="ERROR"
    AND textPayload=~"CRASH"'

# Alert when cost exceeds threshold
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="code_developer Cost Alert" \
  --condition-display-name="Daily cost exceeds $50" \
  --condition-threshold-value=50
```

### Key Metrics to Watch

| Metric | Healthy Range | Alert Threshold |
|--------|---------------|-----------------|
| **Uptime** | >99% | <95% |
| **CPU Usage** | 20-60% | >80% for 5 min |
| **Memory Usage** | 30-70% | >85% |
| **API Errors** | <1% | >5% |
| **Iteration Duration** | 2-10 minutes | >30 minutes |
| **Daily Cost** | $3-10 | >$20 |

---

## Cost Management

### Estimated Monthly Costs

**Base Infrastructure**:
```
Cloud Run (1vCPU, 2GB, always-on):    $25-30
Cloud SQL (db-f1-micro):               $25-35
Cloud Storage (50GB):                  $5-10
Secret Manager:                        $1-2
Cloud Logging:                         $5-10
Networking:                            $5-10
────────────────────────────────────────────
GCP Total:                             $66-97/month
```

**Variable Costs**:
```
Anthropic API (Claude 3.5 Sonnet):
  - Per 1M input tokens:  $3
  - Per 1M output tokens: $15
  - Estimated monthly:    $50-200 (depends on usage)

Total Estimated Cost:                  $116-297/month
```

### Cost Optimization Tips

**1. Reduce Anthropic API Costs**:
```bash
# Use smaller model for simple tasks
# Update Cloud Run env var:
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "CLAUDE_MODEL=claude-3-haiku-20240307"

# Haiku pricing: $0.25 per 1M input tokens (12x cheaper)
```

**2. Scale Down During Off-Hours**:
```bash
# Set min-instances to 0 (scale to zero when idle)
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 1

# Trade-off: Cold start delay (~10s) when reactivating
```

**3. Use Committed Use Discounts**:
```bash
# For Cloud SQL, commit to 1 or 3 years for 25-52% discount
# See: https://cloud.google.com/sql/docs/mysql/cud
```

**4. Monitor Costs in Real-Time**:
```bash
# View current month costs
gcloud billing accounts list
gcloud billing projects describe $GCP_PROJECT_ID

# Set up budget alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="code_developer Monthly Budget" \
  --budget-amount=150 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

---

## Next Steps

### After Successful Deployment

**1. Update ROADMAP.md**:
```bash
# Mark PRIORITY 6.5 as complete in docs/ROADMAP.md
```

**2. Configure Continuous Deployment** (Optional):
```bash
# Set up GitHub Actions to auto-deploy on push
# See: .github/workflows/deploy-gcp.yml
```

**3. Enable Streamlit Dashboard** (PRIORITY 5, 5.5, 6):
```bash
# Deploy Streamlit apps to Cloud Run for web-based monitoring
# See: docs/PRIORITY_5_TECHNICAL_SPEC.md
```

**4. Set Up Team Access** (Optional):
```bash
# Grant other team members access to monitor daemon
gcloud run services add-iam-policy-binding code-developer \
  --region us-central1 \
  --member="user:teammate@example.com" \
  --role="roles/run.viewer"
```

### Troubleshooting

For common issues and solutions, see:
- [docs/TROUBLESHOOTING_GCP.md](./TROUBLESHOOTING_GCP.md)
- [docs/OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md)

### Support

- **GitHub Issues**: [MonolithicCoffeeMakerAgent/issues](https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues)
- **Documentation**: [docs/](https://github.com/Bobain/MonolithicCoffeeMakerAgent/tree/main/docs)
- **ROADMAP**: [docs/ROADMAP.md](./ROADMAP.md)

---

## Summary Checklist

**Before deploying**:
- [ ] GCP account with billing enabled
- [ ] Anthropic API key obtained
- [ ] GitHub token with repo permissions
- [ ] Docker and gcloud CLI installed
- [ ] Container tested locally

**After deploying**:
- [ ] Service health endpoint returns "healthy"
- [ ] Daemon visible in Cloud Run console
- [ ] Logs show successful iterations
- [ ] Notifications work from local CLI
- [ ] Monitoring dashboard configured
- [ ] Cost alerts set up
- [ ] ROADMAP.md updated

**Congratulations!** 🎉 Your code_developer daemon is now running 24/7 on GCP!

---

**Document Version**: 1.0
**Last Verified**: 2025-10-12
**Deployment Time**: ~2-4 hours (first time)
