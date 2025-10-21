# GCP Deployment Guide for code_developer

**Comprehensive guide to deploying code_developer daemon on Google Cloud Platform**

Version: 1.0
Last Updated: 2025-10-11
Status: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Initial Setup](#initial-setup)
5. [Deployment Steps](#deployment-steps)
6. [Configuration](#configuration)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)
9. [Cost Estimation](#cost-estimation)
10. [Security Best Practices](#security-best-practices)

---

## Overview

This guide walks through deploying the `code_developer` autonomous daemon on Google Cloud Platform, enabling 24/7 autonomous development operation.

### Why GCP Deployment?

Currently, `code_developer` runs locally, with significant limitations:

- **Availability**: Stops when laptop sleeps/shuts down
- **Accessibility**: Can't work remotely
- **Resources**: Limited by local machine
- **Reliability**: Vulnerable to local network issues
- **Scalability**: Can't run multiple instances

**GCP deployment solves all these issues**, providing:
- ✅ 24/7 uptime (99.9% SLA)
- ✅ Remote access from anywhere
- ✅ Scalable resources
- ✅ Professional reliability
- ✅ Multi-project support

### Services Used

- **Cloud Run**: Serverless container deployment
- **Cloud Storage**: Project files and state
- **Cloud SQL**: PostgreSQL database
- **Secret Manager**: Secure credential storage
- **Cloud Monitoring**: Metrics and alerting
- **Cloud Logging**: Centralized logging

---

## Prerequisites

### 1. GCP Account & Project

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Create new project (or use existing)
export PROJECT_ID="code-developer-prod"
gcloud projects create $PROJECT_ID --name="Code Developer"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required)
gcloud beta billing accounts list
gcloud beta billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

### 2. Required Tools

```bash
# Install Terraform
brew install terraform  # macOS
# OR
# Download from https://www.terraform.io/downloads

# Verify installation
terraform version  # Should be >= 1.5.0

# Install Docker
brew install docker  # macOS
# OR download from https://www.docker.com/products/docker-desktop

# Verify Docker
docker --version
```

### 3. API Keys

You'll need:

1. **Anthropic API Key**
   - Get from: https://console.anthropic.com/
   - Export: `export ANTHROPIC_API_KEY="sk-ant-..."`

2. **GitHub Personal Access Token**
   - Create at: https://github.com/settings/tokens
   - Scopes needed: `repo`, `workflow`
   - Export: `export GITHUB_TOKEN="ghp_..."`

3. **Coffee Maker API Key** (generated during setup)
   - Used for project-manager CLI authentication

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Local Machine                      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  project-manager CLI                                   │  │
│  │  $ project-manager cloud status                       │  │
│  │  $ project-manager cloud logs                         │  │
│  │  $ project-manager cloud deploy                       │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │ HTTPS/gRPC                              │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Platform (GCP)                     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Run Service                                     │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  code_developer Daemon (Container)              │ │  │
│  │  │  - Reads ROADMAP.md                             │ │  │
│  │  │  - Implements features                          │ │  │
│  │  │  - Commits to GitHub                            │ │  │
│  │  │  - Sends notifications                          │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  FastAPI Control API                            │ │  │
│  │  │  - /api/daemon/start                            │ │  │
│  │  │  - /api/daemon/status                           │ │  │
│  │  │  - /api/files/roadmap                           │ │  │
│  │  │  - /api/logs (WebSocket)                        │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Storage Buckets                                 │  │
│  │  - project-files/              (ROADMAP, code)        │  │
│  │  - logs/                       (daemon logs)          │  │
│  │  - backups/                    (checkpoints)          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                                │  │
│  │  - notifications                                       │  │
│  │  - analytics                                           │  │
│  │  - execution_history                                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Secret Manager                                        │  │
│  │  - ANTHROPIC_API_KEY                                  │  │
│  │  - GITHUB_TOKEN                                       │  │
│  │  - DB_PASSWORD                                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Initial Setup

### Step 1: Clone Repository

```bash
cd /path/to/your/workspace
git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent
```

### Step 2: Configure Terraform Variables

Create `infrastructure/terraform/terraform.tfvars`:

```hcl
# Project configuration
project_id  = "code-developer-prod"
region      = "us-central1"
environment = "prod"

# Cloud Run configuration
cloud_run_cpu           = "2"
cloud_run_memory        = "2Gi"
cloud_run_min_instances = 1
cloud_run_max_instances = 3

# Database configuration
enable_cloud_sql       = true
database_tier          = "db-f1-micro"
database_backup_enabled = true

# Cost limits
daily_cost_limit   = 50.0
monthly_cost_limit = 1500.0

# Monitoring
alert_email = "your-email@example.com"

# Secrets (optional - can be set after deployment)
# anthropic_api_key = "sk-ant-..."
# github_token      = "ghp_..."
```

### Step 3: Initialize Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Preview changes
terraform plan
```

---

## Deployment Steps

### Method 1: Automated Deployment (Recommended)

We provide a deployment script that handles everything:

```bash
# From project root
./scripts/deploy-gcp.sh

# The script will:
# 1. Build Docker image
# 2. Push to Google Container Registry
# 3. Apply Terraform configuration
# 4. Configure secrets
# 5. Deploy to Cloud Run
# 6. Run smoke tests
```

### Method 2: Manual Deployment

#### Step 1: Build and Push Docker Image

```bash
# Set variables
export PROJECT_ID="code-developer-prod"
export IMAGE_NAME="code-developer"
export IMAGE_TAG="latest"
export IMAGE_URL="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"

# Configure Docker for GCP
gcloud auth configure-docker

# Build image
docker build -t $IMAGE_URL \
  -f coffee_maker/deployment/Dockerfile \
  .

# Push to GCR
docker push $IMAGE_URL

# Verify
gcloud container images list --repository=gcr.io/$PROJECT_ID
```

#### Step 2: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Apply Terraform configuration
terraform apply

# Save outputs
terraform output -json > outputs.json

# Get Cloud Run URL
export SERVICE_URL=$(terraform output -raw cloud_run_service_url)
echo "Service URL: $SERVICE_URL"
```

#### Step 3: Configure Secrets

```bash
# Set Anthropic API key
echo -n "$ANTHROPIC_API_KEY" | gcloud secrets versions add code-developer-anthropic-api-key --data-file=-

# Set GitHub token
echo -n "$GITHUB_TOKEN" | gcloud secrets versions add code-developer-github-token --data-file=-

# API key is auto-generated, retrieve it:
export API_KEY=$(gcloud secrets versions access latest --secret=code-developer-api-key)
echo "API Key: $API_KEY"
```

#### Step 4: Sync Project Files to Cloud Storage

```bash
# Get bucket name from Terraform
export BUCKET_NAME=$(terraform output -raw storage_bucket_name)

# Sync ROADMAP.md
gsutil cp docs/roadmap/ROADMAP.md gs://${BUCKET_NAME}/workspace/docs/

# Sync entire project (optional)
gsutil -m rsync -r -x '.git|__pycache__|*.pyc|venv' \
  . gs://${BUCKET_NAME}/workspace/
```

#### Step 5: Verify Deployment

```bash
# Check service health
curl ${SERVICE_URL}/api/health

# Check daemon status
curl -H "Authorization: Bearer ${API_KEY}" \
  ${SERVICE_URL}/api/daemon/status

# View logs
gcloud run services logs read code-developer-prod \
  --region=us-central1 --limit=50
```

---

## Configuration

### 1. Configure project-manager CLI

Create `~/.config/coffee-maker/gcp.yaml`:

```yaml
gcp:
  enabled: true
  api_url: https://code-developer-prod-xxxxxx.run.app
  api_key_env: COFFEE_MAKER_API_KEY
  project_id: code-developer-prod
  region: us-central1

  daemon:
    auto_start: true
    check_interval: 30
    notify_on_completion: true
```

Set API key in environment:

```bash
# Add to ~/.zshrc or ~/.bashrc
export COFFEE_MAKER_API_KEY="your-api-key-here"
```

### 2. Test CLI Integration

```bash
# Check daemon status
project-manager cloud status

# View logs
project-manager cloud logs

# Start daemon
project-manager cloud start

# Deploy new version
project-manager cloud deploy
```

---

## Monitoring & Observability

### 1. Cloud Monitoring Dashboards

Access dashboards at:
- **Overview**: https://console.cloud.google.com/monitoring/dashboards/custom/code-developer-overview
- **Costs**: https://console.cloud.google.com/monitoring/dashboards/custom/code-developer-costs

Or deploy from config:

```bash
gcloud monitoring dashboards create \
  --config-from-file=coffee_maker/monitoring/dashboards/daemon_health.json
```

### 2. Metrics to Monitor

- **daemon_uptime**: Daemon uptime percentage
- **tasks_completed_total**: Total tasks completed
- **tasks_failed_total**: Total tasks failed
- **anthropic_api_cost_usd**: Anthropic API costs
- **task_duration_seconds**: Task completion time

### 3. Alerting

Configure alerts in Cloud Monitoring:

```bash
# Create alert for daemon crash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Daemon Crash Alert" \
  --condition-display-name="Daemon Not Healthy" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
```

### 4. Log Streaming

```bash
# Stream logs in real-time
gcloud run services logs tail code-developer-prod --region=us-central1

# Search logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=code-developer-prod" --limit=100
```

---

## Troubleshooting

### Common Issues

#### 1. Container won't start

**Symptoms**: Cloud Run shows "Service Unavailable"

**Solution**:
```bash
# Check logs
gcloud run services logs read code-developer-prod --limit=100

# Common causes:
# - Missing environment variables
# - Secret access denied
# - Database connection failed

# Verify secrets
gcloud secrets versions access latest --secret=code-developer-anthropic-api-key

# Check IAM permissions
gcloud projects get-iam-policy $PROJECT_ID
```

#### 2. Daemon not responding

**Symptoms**: API returns 503 or times out

**Solution**:
```bash
# Check Cloud Run status
gcloud run services describe code-developer-prod --region=us-central1

# Scale up if needed
gcloud run services update code-developer-prod \
  --region=us-central1 \
  --min-instances=1

# Restart service
gcloud run services update code-developer-prod \
  --region=us-central1 \
  --update-env-vars=RESTART_TIMESTAMP=$(date +%s)
```

#### 3. High costs

**Symptoms**: Bill higher than expected

**Solution**:
```bash
# Check Cloud Run usage
gcloud run services describe code-developer-prod --region=us-central1 --format="value(status.traffic)"

# Reduce min instances
gcloud run services update code-developer-prod \
  --region=us-central1 \
  --min-instances=0

# Check API usage
curl -H "Authorization: Bearer $API_KEY" \
  ${SERVICE_URL}/api/status/metrics
```

#### 4. Database connection errors

**Symptoms**: "Could not connect to database"

**Solution**:
```bash
# Test Cloud SQL connection
gcloud sql connect code-developer-db-xxxx --user=code_developer

# Check Cloud SQL status
gcloud sql instances describe code-developer-db-xxxx

# Verify service account has cloudsql.client role
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/cloudsql.client"
```

### Debug Commands

```bash
# Get service details
gcloud run services describe code-developer-prod --region=us-central1

# Check recent deployments
gcloud run revisions list --service=code-developer-prod --region=us-central1

# View environment variables
gcloud run services describe code-developer-prod \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"

# Test health endpoint
curl $(gcloud run services describe code-developer-prod \
  --region=us-central1 --format="value(status.url)")/api/health
```

---

## Cost Estimation

### Monthly Cost Breakdown

#### Scenario 1: Light Usage (Dev/Testing)
- **Cloud Run**: $5-10/month (0 min instances, low traffic)
- **Cloud Storage**: $1-2/month (10GB storage)
- **Cloud SQL**: $0 (can disable, use SQLite)
- **Anthropic API**: $50-100/month
- **Total**: ~$60-120/month

#### Scenario 2: Production Usage (24/7)
- **Cloud Run**: $30-50/month (1 min instance, 2GB memory)
- **Cloud Storage**: $2-5/month (50GB storage)
- **Cloud SQL**: $10-15/month (db-f1-micro)
- **Cloud Logging**: $5-10/month
- **Anthropic API**: $200-500/month (heavy usage)
- **Total**: ~$250-600/month

### Cost Optimization Tips

1. **Scale to zero** for dev environments:
   ```bash
   gcloud run services update code-developer-prod --min-instances=0
   ```

2. **Use Cloud Storage lifecycle policies** (auto-configured):
   - Move old logs to Coldline after 30 days
   - Delete after 90 days

3. **Monitor Anthropic API costs**:
   ```bash
   project-manager cloud metrics --costs
   ```

4. **Set budget alerts** in GCP Console:
   - Go to Billing > Budgets & Alerts
   - Set threshold at $500/month

---

## Security Best Practices

### 1. IAM Principles

- ✅ Use service accounts (not user accounts)
- ✅ Grant minimum necessary permissions
- ✅ Rotate secrets every 90 days
- ✅ Enable audit logging

### 2. Network Security

- ✅ Use VPC connector for Cloud SQL
- ✅ Enable Cloud Armor (DDoS protection)
- ✅ Restrict ingress to known IPs (production)

### 3. Secret Management

```bash
# Rotate Anthropic API key
echo -n "$NEW_ANTHROPIC_API_KEY" | \
  gcloud secrets versions add code-developer-anthropic-api-key --data-file=-

# Disable old version
gcloud secrets versions disable 1 --secret=code-developer-anthropic-api-key
```

### 4. Backup & Disaster Recovery

Automated backups:
- **Database**: Daily backups (7-day retention)
- **Storage**: Versioning enabled
- **Code**: Git repository

Manual backup:

```bash
# Backup Cloud SQL
gcloud sql backups create --instance=code-developer-db-xxxx

# Backup Cloud Storage
gsutil -m rsync -r gs://${BUCKET_NAME}/ ./backups/$(date +%Y%m%d)/
```

---

## Next Steps

After successful deployment:

1. **Test end-to-end workflow**:
   ```bash
   # Edit ROADMAP.md locally
   # Push to GitHub
   # Daemon automatically syncs and starts implementation
   ```

2. **Set up GitHub webhook** (optional):
   - Trigger daemon on ROADMAP.md push
   - See `docs/GITHUB_WEBHOOKS.md`

3. **Configure Slack notifications**:
   - See `coffee_maker/monitoring/README.md`

4. **Enable continuous deployment**:
   - GitHub Actions auto-deploy on merge to main
   - See `.github/workflows/deploy-gcp.yml`

5. **Monitor and optimize**:
   - Review Cloud Monitoring dashboards daily
   - Adjust resource limits based on usage
   - Optimize costs

---

## Support

- **Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Documentation**: `docs/` directory
- **Discussions**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

---

**Deployment Checklist:**

- [ ] GCP project created and billing enabled
- [ ] Terraform initialized and applied successfully
- [ ] Docker image built and pushed to GCR
- [ ] Secrets configured (Anthropic API key, GitHub token)
- [ ] Cloud Run service deployed and healthy
- [ ] project-manager CLI configured and tested
- [ ] Monitoring dashboards deployed
- [ ] Alert policies configured
- [ ] Initial test run completed successfully
- [ ] Documentation reviewed and team trained

**Congratulations! Your code_developer daemon is now running 24/7 on GCP! 🎉**
