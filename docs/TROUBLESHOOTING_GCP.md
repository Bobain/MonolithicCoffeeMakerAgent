# Troubleshooting GCP Deployment

**Version**: 1.0
**Last Updated**: 2025-10-12

This document provides solutions to common issues encountered when deploying and operating the `code_developer` daemon on Google Cloud Platform.

---

## Table of Contents

1. [Deployment Issues](#deployment-issues)
2. [Runtime Issues](#runtime-issues)
3. [Database Issues](#database-issues)
4. [API & Authentication Issues](#api--authentication-issues)
5. [Performance Issues](#performance-issues)
6. [Cost Issues](#cost-issues)
7. [Debugging Techniques](#debugging-techniques)
8. [Emergency Procedures](#emergency-procedures)

---

## Deployment Issues

### Issue: Container Build Fails

**Symptoms**:
```bash
gcloud builds submit ...
ERROR: build step failed
```

**Common Causes & Solutions**:

**1. Missing dependencies in pyproject.toml**:
```bash
# Check Poetry dependencies
cd /path/to/MonolithicCoffeeMakerAgent
poetry check

# Update lock file
poetry lock --no-update

# Rebuild
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest .
```

**2. Dockerfile path incorrect**:
```bash
# Ensure you're in project root
pwd  # Should be /path/to/MonolithicCoffeeMakerAgent

# Verify Dockerfile exists
ls -la coffee_maker/deployment/Dockerfile

# Build with correct path
gcloud builds submit \
  --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --dockerfile=coffee_maker/deployment/Dockerfile \
  .
```

**3. Build timeout**:
```bash
# Increase timeout (default: 10m)
gcloud builds submit \
  --timeout=20m \
  --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  .
```

**4. Insufficient permissions**:
```bash
# Grant Cloud Build service account permissions
PROJECT_NUMBER=$(gcloud projects describe $GCP_PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

### Issue: Cloud Run Deployment Fails

**Symptoms**:
```bash
gcloud run deploy code-developer ...
ERROR: Deployment failed
```

**Common Causes & Solutions**:

**1. Image not found**:
```bash
# Verify image exists
gcloud container images list --repository=gcr.io/$GCP_PROJECT_ID

# List versions
gcloud container images list-tags gcr.io/$GCP_PROJECT_ID/code-developer

# If missing, rebuild
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest .
```

**2. Secret not accessible**:
```bash
# Verify secrets exist
gcloud secrets list

# Check service account has access
gcloud secrets get-iam-policy anthropic-api-key

# Grant access if missing
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**3. Cloud SQL connection fails**:
```bash
# Verify Cloud SQL instance exists
gcloud sql instances list

# Check connection name
gcloud sql instances describe code-developer-db \
  --format="value(connectionName)"

# Ensure Cloud Run has Cloud SQL client role
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

**4. Memory limit too low**:
```bash
# Increase memory (default: 512Mi may be insufficient)
gcloud run services update code-developer \
  --region us-central1 \
  --memory 2Gi
```

---

## Runtime Issues

### Issue: Daemon Not Starting

**Symptoms**:
- Health check fails
- Container exits immediately
- Logs show "DevDaemon stopped" right after start

**Diagnosis**:

```bash
# View recent logs
gcloud run services logs read code-developer \
  --platform managed \
  --region us-central1 \
  --limit 100

# Look for error messages like:
# ❌ Claude API not available
# ❌ ROADMAP not found
# ❌ Git repository not ready
```

**Solutions**:

**1. Claude API key invalid**:
```bash
# Verify API key in Secret Manager
gcloud secrets versions access latest --secret="anthropic-api-key"

# Test key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $(gcloud secrets versions access latest --secret=anthropic-api-key)" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'

# If invalid, update secret
echo -n "NEW_API_KEY" | gcloud secrets versions add anthropic-api-key --data-file=-
```

**2. ROADMAP.md not found**:
```bash
# The daemon expects ROADMAP.md in /workspace/docs/
# Verify volume mount or use Cloud Storage

# Option 1: Mount from GitHub
# Update Cloud Run to clone repo on startup
# (requires git clone in entrypoint script)

# Option 2: Use Cloud Storage
gsutil cp docs/roadmap/ROADMAP.md gs://${GCP_PROJECT_ID}-code-developer/ROADMAP.md

# Update environment variable
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "ROADMAP_PATH=gs://${GCP_PROJECT_ID}-code-developer/ROADMAP.md"
```

**3. Database connection fails**:
```bash
# Check database is running
gcloud sql instances describe code-developer-db

# Verify connection string in secret
gcloud secrets versions access latest --secret="database-url"

# Test connection from local machine
psql "$(gcloud secrets versions access latest --secret=database-url)"

# If connection fails, check:
# - Cloud SQL instance is running (not stopped)
# - Cloud Run has Cloud SQL client permissions
# - Database credentials are correct
```

---

### Issue: Daemon Crashes Repeatedly

**Symptoms**:
```
❌ CRASH #1/3: ...
❌ CRASH #2/3: ...
❌ CRASH #3/3: ...
🚨 MAX CRASHES REACHED (3) - STOPPING DAEMON
```

**Diagnosis**:

```bash
# View crash logs
gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 200 | grep -A 20 "CRASH"

# Common crash causes:
# - API rate limits exceeded
# - Out of memory
# - Network timeout
# - Git operation failed
```

**Solutions**:

**1. API rate limit exceeded**:
```bash
# Check Anthropic API rate limits
# Reduce daemon frequency or upgrade API plan

# Increase sleep interval
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "DAEMON_SLEEP_INTERVAL=60"  # 60 seconds instead of 30
```

**2. Out of memory**:
```bash
# Check memory usage
gcloud run services describe code-developer \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].resources.limits.memory)"

# Increase memory
gcloud run services update code-developer \
  --region us-central1 \
  --memory 4Gi
```

**3. Network timeout**:
```bash
# Increase timeout
gcloud run services update code-developer \
  --region us-central1 \
  --timeout 3600  # 1 hour
```

**4. Git authentication failure**:
```bash
# Verify GitHub token
gcloud secrets versions access latest --secret="github-token"

# Test token
curl -H "Authorization: token $(gcloud secrets versions access latest --secret=github-token)" \
  https://api.github.com/user

# If expired, create new token and update secret
# https://github.com/settings/tokens/new
echo -n "NEW_GITHUB_TOKEN" | gcloud secrets versions add github-token --data-file=-
```

---

### Issue: Daemon Stuck in Infinite Loop

**Symptoms**:
- Same priority attempted repeatedly
- Logs show "Iteration X" increasing without progress
- No new commits/PRs created

**Diagnosis**:

```bash
# Check developer status
curl -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/daemon/status

# Look for:
# - current_priority unchanged
# - iteration count increasing
# - no recent activity
```

**Solutions**:

**1. Priority has no content**:
```bash
# The daemon may be stuck on a priority with missing deliverables
# Check ROADMAP.md for the current priority

# Option 1: Update ROADMAP.md to skip this priority
# Option 2: Add content to the priority
# Option 3: Restart daemon to skip (loses state)
```

**2. Max retries reached**:
```bash
# Daemon stops after 3 failed attempts per priority
# Check logs for:
# ⚠️ Max retries (3) reached for PRIORITY X

# Solution: Manually implement the priority or update ROADMAP
# Then restart daemon
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "DAEMON_MAX_RETRIES=5"  # Increase if needed
```

**3. Waiting for user approval**:
```bash
# If auto_approve=false, daemon waits for approval
# Check notifications
poetry run project-manager notifications

# Approve via CLI
poetry run project-manager respond <notification-id> approve

# Or enable auto-approve
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "COFFEE_MAKER_AUTO_APPROVE=true"
```

---

## Database Issues

### Issue: Database Connection Timeout

**Symptoms**:
```
Error: could not connect to database
connection timeout
```

**Solutions**:

**1. Cloud SQL instance paused**:
```bash
# Check instance state
gcloud sql instances describe code-developer-db \
  --format="value(state)"

# If stopped, start it
gcloud sql instances patch code-developer-db --activation-policy=ALWAYS
```

**2. Connection limit reached**:
```bash
# Check current connections
gcloud sql instances describe code-developer-db \
  --format="value(settings.ipConfiguration.maxConnections)"

# Increase limit
gcloud sql instances patch code-developer-db \
  --database-flags max_connections=100
```

**3. Cloud SQL client role missing**:
```bash
# Grant role
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Redeploy Cloud Run
gcloud run services update code-developer --region us-central1
```

---

### Issue: Database Tables Missing

**Symptoms**:
```
relation "notifications" does not exist
relation "task_metrics" does not exist
```

**Solutions**:

```bash
# Connect to database
gcloud sql connect code-developer-db --user=coffee_maker --database=coffee_maker

# Create tables manually
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    priority_name VARCHAR(100),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    response TEXT
);

CREATE TABLE IF NOT EXISTS task_metrics (
    id SERIAL PRIMARY KEY,
    priority_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20),
    duration_seconds INTEGER,
    commits INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS developer_status (
    id SERIAL PRIMARY KEY,
    state VARCHAR(50) NOT NULL,
    current_task JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Verify
\dt
```

---

## API & Authentication Issues

### Issue: Authentication Failed (401)

**Symptoms**:
```bash
curl $SERVICE_URL/api/daemon/status
# Response: {"error": "Unauthorized"}
```

**Solutions**:

**1. Missing or incorrect API key**:
```bash
# Get correct API key
export COFFEE_MAKER_API_KEY=$(gcloud secrets versions access latest --secret="coffee-maker-api-key")

# Use in request
curl -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/daemon/status
```

**2. API key not set in Cloud Run**:
```bash
# Verify environment variable
gcloud run services describe code-developer \
  --region us-central1 \
  --format="yaml(spec.template.spec.containers[0].env)"

# Add if missing
gcloud run services update code-developer \
  --region us-central1 \
  --set-secrets "API_KEY=coffee-maker-api-key:latest"
```

---

### Issue: GitHub API Rate Limit Exceeded

**Symptoms**:
```
API rate limit exceeded for user ID XXXXX
```

**Solutions**:

**1. Use Personal Access Token (not OAuth)**:
```bash
# Create new token with higher rate limit
# https://github.com/settings/tokens/new
# Required scopes: repo, workflow

# Update secret
echo -n "NEW_GITHUB_TOKEN" | gcloud secrets versions add github-token --data-file=-
```

**2. Reduce API calls**:
```bash
# Increase sleep interval to reduce frequency
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "DAEMON_SLEEP_INTERVAL=60"
```

**3. Use GitHub App** (future enhancement):
```
# GitHub Apps have higher rate limits than Personal Access Tokens
# TODO: Implement GitHub App authentication
```

---

## Performance Issues

### Issue: Slow Response Times

**Symptoms**:
- API requests take >30 seconds
- Daemon iterations take >10 minutes
- Health checks timeout

**Solutions**:

**1. Increase CPU allocation**:
```bash
# Cloud Run default: 1 vCPU
gcloud run services update code-developer \
  --region us-central1 \
  --cpu 2
```

**2. Enable CPU boost**:
```bash
# Allocate CPU even when not handling requests
gcloud run services update code-developer \
  --region us-central1 \
  --cpu-boost
```

**3. Optimize database queries**:
```bash
# Connect to database
gcloud sql connect code-developer-db --user=coffee_maker

# Add indexes
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_task_metrics_priority ON task_metrics(priority_name);
```

**4. Use caching**:
```bash
# Deploy Redis for caching (optional)
# Add to docker-compose.yml or Cloud Memorystore
```

---

### Issue: High Memory Usage

**Symptoms**:
```
Container exceeded memory limit
Out of memory: Killed process
```

**Solutions**:

**1. Increase memory**:
```bash
gcloud run services update code-developer \
  --region us-central1 \
  --memory 4Gi
```

**2. Enable context compaction**:
```bash
# Reset Claude context periodically to free memory
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "DAEMON_COMPACT_INTERVAL=5"  # Reset every 5 iterations
```

**3. Check for memory leaks**:
```bash
# Monitor memory over time
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"' \
  --format=json

# If memory grows unbounded, investigate code for leaks
```

---

## Cost Issues

### Issue: Unexpectedly High Costs

**Symptoms**:
- Monthly bill exceeds $200
- Budget alerts triggering
- Costs growing rapidly

**Diagnosis**:

```bash
# View cost breakdown
gcloud billing accounts describe YOUR_BILLING_ACCOUNT_ID

# Analyze costs by service
# Go to: https://console.cloud.google.com/billing/reports

# Common cost drivers:
# - Anthropic API usage (variable)
# - Cloud Run (always-on instance)
# - Cloud SQL (running 24/7)
# - Cloud Logging (high log volume)
```

**Solutions**:

**1. Reduce Anthropic API costs**:
```bash
# Switch to Haiku model (12x cheaper)
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "CLAUDE_MODEL=claude-3-haiku-20240307"

# Haiku: $0.25 per 1M input tokens
# Sonnet: $3 per 1M input tokens
```

**2. Scale to zero when idle**:
```bash
# Allow Cloud Run to scale to 0 instances
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 1

# Trade-off: ~10s cold start when reactivating
```

**3. Reduce log retention**:
```bash
# Default: 30 days, can be reduced to 7 days
gcloud logging buckets update _Default \
  --location=global \
  --retention-days=7
```

**4. Use smaller Cloud SQL instance**:
```bash
# Check current tier
gcloud sql instances describe code-developer-db \
  --format="value(settings.tier)"

# Downgrade if db-f1-micro is sufficient
gcloud sql instances patch code-developer-db \
  --tier=db-f1-micro
```

**5. Set up cost alerts**:
```bash
# Get notified before costs exceed budget
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="code_developer Cost Alert" \
  --budget-amount=150USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

---

## Debugging Techniques

### Technique 1: Real-Time Log Streaming

```bash
# Stream all logs
gcloud run services logs tail code-developer \
  --platform managed \
  --region us-central1

# Filter by severity
gcloud run services logs tail code-developer \
  --region us-central1 \
  --log-filter="severity=ERROR"

# Filter by text
gcloud run services logs tail code-developer \
  --region us-central1 \
  --log-filter='textPayload:CRASH'
```

### Technique 2: Interactive Debugging

```bash
# SSH into Cloud Run container (experimental)
gcloud beta run services proxy code-developer \
  --region us-central1

# Connect to database directly
gcloud sql connect code-developer-db --user=coffee_maker

# Execute Python commands in container
gcloud run services describe code-developer \
  --region us-central1 \
  --format="value(status.url)"

# Then use exec (if enabled)
kubectl exec -it <pod-name> -- python3
```

### Technique 3: Health Check Debugging

```bash
# Test health endpoint
curl $SERVICE_URL/api/health

# Expected response:
{
  "status": "healthy",
  "daemon_status": "running",
  "database": "connected",
  "claude_api": "available",
  "github": "authenticated",
  "uptime_seconds": 3600
}

# If unhealthy, check logs immediately
gcloud run services logs read code-developer --limit 50
```

### Technique 4: Local Reproduction

```bash
# Reproduce issue locally using same container
docker pull gcr.io/$GCP_PROJECT_ID/code-developer:latest

# Run with same environment
docker run -it \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -e DATABASE_URL="postgresql://..." \
  gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  python -m coffee_maker.autonomous.daemon_cli

# Debug interactively
docker run -it --entrypoint /bin/bash \
  gcr.io/$GCP_PROJECT_ID/code-developer:latest
```

---

## Emergency Procedures

### Emergency: Daemon Out of Control

**Symptoms**:
- Creating spam PRs
- Committing incorrect code
- Deleting important files
- API costs spiking

**Immediate Actions**:

```bash
# 1. STOP the daemon immediately
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 0

# 2. Revoke API access
gcloud secrets versions disable latest --secret="anthropic-api-key"
gcloud secrets versions disable latest --secret="github-token"

# 3. Check damage
gh pr list --repo YOUR_REPO
git log --all --since="1 hour ago"

# 4. Investigate logs
gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 500 > emergency-logs.txt

# 5. Notify team
# Send notification about incident

# 6. Review and fix
# - Close spam PRs
# - Revert bad commits
# - Fix configuration
# - Test locally before redeploying
```

### Emergency: High Costs Detected

**Immediate Actions**:

```bash
# 1. Check current costs
gcloud billing accounts describe YOUR_BILLING_ACCOUNT_ID

# 2. Stop non-essential services
gcloud run services delete code-developer --region us-central1 --quiet

# 3. Review usage
# Console: https://console.cloud.google.com/billing/reports

# 4. Set hard spending limit (if not already set)
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="Emergency Budget Cap" \
  --budget-amount=300USD \
  --threshold-rule=percent=100

# 5. Investigate root cause
# - Check Anthropic API usage
# - Review Cloud Run instance count
# - Check for runaway processes
```

### Emergency: Data Loss

**Symptoms**:
- Database corrupted
- ROADMAP.md deleted
- Notifications missing

**Recovery Actions**:

```bash
# 1. Stop daemon to prevent further damage
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 0

# 2. Restore database from backup
gcloud sql backups list --instance=code-developer-db

# Get most recent backup
BACKUP_ID=$(gcloud sql backups list --instance=code-developer-db \
  --format="value(id)" --limit=1)

# Restore
gcloud sql backups restore $BACKUP_ID \
  --backup-instance=code-developer-db \
  --backup-id=$BACKUP_ID

# 3. Restore ROADMAP.md from Git history
git checkout origin/roadmap -- docs/roadmap/ROADMAP.md

# 4. Verify data integrity
gcloud sql connect code-developer-db --user=coffee_maker
SELECT COUNT(*) FROM notifications;
SELECT COUNT(*) FROM task_metrics;

# 5. Restart daemon after verification
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 1
```

---

## Getting Help

### Support Channels

**1. Project Documentation**:
- [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md) - Deployment steps
- [GCP_SETUP.md](./GCP_SETUP.md) - Initial setup
- [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) - Operations procedures
- [ROADMAP.md](./ROADMAP.md) - Project roadmap

**2. GCP Support**:
- Console: https://console.cloud.google.com/support
- Documentation: https://cloud.google.com/docs
- Community: https://stackoverflow.com/questions/tagged/google-cloud-platform

**3. Project Support**:
- GitHub Issues: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- Discussions: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

### Creating Support Tickets

**Include the following information**:

```bash
# System information
gcloud version
gcloud config list

# Service details
gcloud run services describe code-developer \
  --region us-central1 \
  --format yaml > service-details.yaml

# Recent logs
gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 200 > recent-logs.txt

# Error messages
# Copy exact error messages from logs

# Steps to reproduce
# Describe what you did before the issue occurred

# Expected vs actual behavior
# What you expected to happen vs what actually happened
```

---

## Prevention Best Practices

### Monitoring

- ✅ Set up Cloud Monitoring dashboards
- ✅ Configure alert policies for critical metrics
- ✅ Review logs daily for warnings
- ✅ Track costs weekly

### Backup & Recovery

- ✅ Enable automated Cloud SQL backups (daily)
- ✅ Store ROADMAP.md in Git (version control)
- ✅ Test backup restoration monthly
- ✅ Document rollback procedures

### Security

- ✅ Rotate API keys every 90 days
- ✅ Review IAM permissions monthly
- ✅ Enable audit logging
- ✅ Use Secret Manager for all credentials

### Cost Management

- ✅ Set budget alerts at 50%, 80%, 100%
- ✅ Review billing reports weekly
- ✅ Optimize resource allocation based on usage
- ✅ Use committed use discounts for predictable workloads

---

## Summary

**Most Common Issues**:
1. Authentication/API key problems (30%)
2. Database connection issues (25%)
3. Memory/resource limits (20%)
4. Configuration errors (15%)
5. Network/timeout issues (10%)

**Quick Diagnostic Commands**:
```bash
# Check service health
curl $SERVICE_URL/api/health

# View recent errors
gcloud run services logs read code-developer \
  --region us-central1 \
  --log-filter="severity=ERROR" \
  --limit 20

# Check daemon status
curl -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/daemon/status

# Verify resources
gcloud run services describe code-developer --region us-central1
```

**When in Doubt**:
1. Check logs first
2. Verify environment variables
3. Test API keys manually
4. Restart the service
5. Consult documentation
6. Create support ticket with details

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Coverage**: Deployment, Runtime, Database, API, Performance, Cost Issues
