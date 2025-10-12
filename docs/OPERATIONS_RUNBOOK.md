# Operations Runbook for GCP code_developer

**Version**: 1.0
**Last Updated**: 2025-10-12
**Owner**: DevOps / Platform Engineering
**On-Call**: [Slack: #code-developer-ops]

This runbook provides step-by-step procedures for operating and maintaining the `code_developer` daemon running on Google Cloud Platform.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Monthly Tasks](#monthly-tasks)
4. [Common Procedures](#common-procedures)
5. [Incident Response](#incident-response)
6. [Escalation Procedures](#escalation-procedures)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Deployment Procedures](#deployment-procedures)

---

## Daily Operations

### Morning Health Check (5 minutes)

**Performed by**: On-call engineer or automation
**Frequency**: Every morning at 9:00 AM local time
**Estimated time**: 5 minutes

**Procedure**:

```bash
#!/bin/bash
# daily-health-check.sh

echo "🔍 Daily Health Check - $(date)"
echo "================================"

# 1. Check service status
echo "1. Checking Cloud Run service..."
STATUS=$(gcloud run services describe code-developer \
  --region us-central1 \
  --format="value(status.conditions[0].status)")

if [ "$STATUS" != "True" ]; then
  echo "❌ Service unhealthy: $STATUS"
  exit 1
fi
echo "✅ Service healthy"

# 2. Check daemon status via API
echo "2. Checking daemon status..."
DAEMON_STATUS=$(curl -s -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/daemon/status | jq -r '.status')

if [ "$DAEMON_STATUS" != "running" ]; then
  echo "⚠️  Daemon not running: $DAEMON_STATUS"
else
  echo "✅ Daemon running"
fi

# 3. Check recent errors
echo "3. Checking for errors in last 24h..."
ERROR_COUNT=$(gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 1000 \
  --log-filter="severity=ERROR AND timestamp>=\"$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)Z\"" \
  | wc -l)

echo "Errors found: $ERROR_COUNT"
if [ "$ERROR_COUNT" -gt 10 ]; then
  echo "⚠️  High error rate!"
fi

# 4. Check database connectivity
echo "4. Checking database..."
DB_CHECK=$(curl -s -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" \
  $SERVICE_URL/api/health | jq -r '.database')

if [ "$DB_CHECK" != "connected" ]; then
  echo "❌ Database not connected"
  exit 1
fi
echo "✅ Database connected"

# 5. Check recent activity
echo "5. Checking recent activity..."
LAST_COMMIT=$(gh api repos/YOUR_REPO/commits \
  --jq '.[0] | {sha: .sha[0:7], message: .commit.message, date: .commit.author.date}')
echo "Last commit: $LAST_COMMIT"

# 6. Check costs
echo "6. Checking yesterday's costs..."
# Note: Billing data has ~1 day delay
# Implement using Cloud Billing API or BigQuery export

echo ""
echo "✅ Daily health check complete"
echo "================================"
```

**Run**:
```bash
chmod +x daily-health-check.sh
./daily-health-check.sh
```

**Expected output**:
```
🔍 Daily Health Check - 2025-10-12 09:00:00
================================
1. Checking Cloud Run service...
✅ Service healthy
2. Checking daemon status...
✅ Daemon running
3. Checking for errors in last 24h...
Errors found: 2
4. Checking database...
✅ Database connected
5. Checking recent activity...
Last commit: {...}
6. Checking yesterday's costs...

✅ Daily health check complete
================================
```

**On failure**: Follow [Incident Response](#incident-response) procedures.

---

### Review Daemon Activity (10 minutes)

**Procedure**:

```bash
# 1. Check daemon status
poetry run project-manager cloud status

# Expected output:
# Daemon Status: RUNNING
# Current Priority: PRIORITY X.Y
# Progress: 45%
# Uptime: 24h 32m
# Iterations: 48
# Crashes: 0

# 2. Review recent notifications
poetry run project-manager notifications

# Look for:
# - Questions requiring approval
# - Error notifications
# - Completion notifications

# 3. Check recent commits/PRs
gh pr list --repo YOUR_REPO --limit 5
gh api repos/YOUR_REPO/commits --jq '.[0:5] | .[] | {sha:.sha[0:7], message:.commit.message, author:.commit.author.name}'

# 4. Review ROADMAP.md progress
git pull origin roadmap
less docs/ROADMAP.md
# Check for status changes (📝 → 🔄 → ✅)
```

**Action items**:
- [ ] Respond to any pending notifications
- [ ] Review and merge completed PRs
- [ ] Update ROADMAP.md if priorities changed
- [ ] Document any issues in incident log

---

## Weekly Maintenance

### Monday: Weekly Review (30 minutes)

**Performed by**: Team lead or on-call engineer
**Frequency**: Every Monday at 10:00 AM
**Estimated time**: 30 minutes

**Procedure**:

```bash
#!/bin/bash
# weekly-review.sh

echo "📊 Weekly Review - Week of $(date +%Y-%m-%d)"
echo "============================================="

# 1. Performance metrics
echo "1. Performance Metrics (Last 7 days):"
echo "-------------------------------------"

# Iteration count
echo "Total iterations: $(gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 10000 \
  --log-filter='textPayload:\"Iteration\"' \
  | grep -c Iteration)"

# Crash count
echo "Total crashes: $(gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 10000 \
  --log-filter='textPayload:CRASH' \
  | grep -c CRASH)"

# Average uptime
echo "Service uptime: $(gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/instance_count"' \
  --format='value(point.value.doubleValue)' \
  | awk '{sum+=$1; count++} END {print sum/count*100"%"}')"

# 2. Completed work
echo ""
echo "2. Completed Work:"
echo "-------------------------------------"
gh pr list --repo YOUR_REPO --state merged --limit 10 \
  --json number,title,createdAt,mergedAt \
  --jq '.[] | "PR #\(.number): \(.title) (merged \(.mergedAt))"'

# 3. Cost analysis
echo ""
echo "3. Cost Analysis (Last 7 days):"
echo "-------------------------------------"
# Implement using Cloud Billing API
# Estimated costs by service

# 4. Error summary
echo ""
echo "4. Error Summary:"
echo "-------------------------------------"
gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 5000 \
  --log-filter='severity=ERROR' \
  | grep -oP 'ERROR:.*' | sort | uniq -c | sort -rn | head -10

echo ""
echo "✅ Weekly review complete"
echo "============================================="
```

**Action items**:
- [ ] Review performance trends
- [ ] Identify recurring errors
- [ ] Optimize resource allocation if needed
- [ ] Update team on progress

---

### Wednesday: Database Maintenance (20 minutes)

**Procedure**:

```bash
# 1. Connect to database
gcloud sql connect code-developer-db --user=coffee_maker --database=coffee_maker

# 2. Check database size
SELECT
  pg_size_pretty(pg_database_size('coffee_maker')) as database_size;

# 3. Check table sizes
SELECT
  relname as table_name,
  pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

# 4. Clean old notifications (older than 90 days)
DELETE FROM notifications
WHERE created_at < NOW() - INTERVAL '90 days'
AND status = 'completed';

# Record count deleted
SELECT COUNT(*) FROM notifications;  -- Before and after

# 5. Clean old task metrics (older than 180 days)
DELETE FROM task_metrics
WHERE start_time < NOW() - INTERVAL '180 days';

# 6. Vacuum and analyze
VACUUM ANALYZE notifications;
VACUUM ANALYZE task_metrics;
VACUUM ANALYZE developer_status;

# 7. Check slow queries (if enabled)
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

# 8. Verify backup schedule
\q  # Exit psql
gcloud sql backups list --instance=code-developer-db --limit 10
```

**Action items**:
- [ ] Document database size growth rate
- [ ] Optimize slow queries if found
- [ ] Verify backups are successful
- [ ] Update capacity plans if needed

---

### Friday: Log Review & Cleanup (15 minutes)

**Procedure**:

```bash
# 1. Review log retention
gcloud logging buckets describe _Default --location=global

# 2. Check log volume (last 7 days)
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=code-developer" \
  --limit 10 \
  --format="table(timestamp,severity,textPayload)" \
  --freshness=7d

# 3. Archive important logs to Cloud Storage
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 1000 \
  --format=json \
  --freshness=7d \
  > error-logs-$(date +%Y-%m-%d).json

gsutil cp error-logs-*.json gs://${GCP_PROJECT_ID}-code-developer/logs/archive/

# 4. Review logging costs
gcloud billing accounts list
# Then check billing console for logging costs

# 5. Optimize logging if costs are high
# Reduce log level from DEBUG to INFO
gcloud run services update code-developer \
  --region us-central1 \
  --set-env-vars "COFFEE_MAKER_LOG_LEVEL=INFO"
```

**Action items**:
- [ ] Archive error logs to Cloud Storage
- [ ] Review and adjust log retention policy
- [ ] Optimize logging if costs exceed $20/month
- [ ] Document any critical errors for investigation

---

## Monthly Tasks

### First Monday: Security Audit (1 hour)

**Procedure**:

```bash
# 1. Review IAM permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --format=json > iam-policy-$(date +%Y-%m).json

# Review for:
# - Unnecessary permissions
# - Overly broad roles (Owner, Editor)
# - Inactive users

# 2. Audit Secret Manager access
for secret in anthropic-api-key github-token database-url coffee-maker-api-key; do
  echo "Secret: $secret"
  gcloud secrets get-iam-policy $secret
done

# 3. Review service account keys
gcloud iam service-accounts keys list \
  --iam-account=code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# 4. Check for expiring credentials
# Anthropic API key: Check console.anthropic.com
# GitHub token: Check github.com/settings/tokens

# 5. Rotate secrets (every 90 days)
# See: Secret Rotation procedure below

# 6. Review Cloud Run security settings
gcloud run services describe code-developer \
  --region us-central1 \
  --format="yaml(spec.template.spec.containers[0].securityContext)"

# 7. Check for vulnerabilities in container image
gcloud container images describe gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --format="value(image_summary.vulnerability_summary)"

# If vulnerabilities found, rebuild with updated base image
```

**Action items**:
- [ ] Remove unused IAM permissions
- [ ] Rotate secrets if >90 days old
- [ ] Update container base image if vulnerabilities found
- [ ] Document findings in security log

---

### Mid-Month: Cost Optimization Review (1 hour)

**Procedure**:

```bash
# 1. Analyze cost trends
# Go to: https://console.cloud.google.com/billing/reports
# Filter by: Project = code-developer-prod
# Time range: Last 30 days

# 2. Break down costs by service
# Expected distribution:
# - Anthropic API: 40-60% (variable)
# - Cloud Run: 15-25%
# - Cloud SQL: 20-30%
# - Cloud Storage: 5-10%
# - Other: <5%

# 3. Identify optimization opportunities
echo "Cost Optimization Analysis"
echo "=========================="

# Check Cloud Run CPU/memory utilization
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/cpu/utilizations"' \
  --format=json

# If utilization <30%, consider downsizing:
# gcloud run services update code-developer \
#   --region us-central1 \
#   --cpu 1 \
#   --memory 1Gi

# Check database utilization
gcloud sql instances describe code-developer-db \
  --format="value(settings.tier)"

# If database is over-provisioned, downgrade tier

# 4. Review Claude API usage
# Check Anthropic console for token usage
# Consider switching to Haiku model if Sonnet is overkill

# 5. Optimize storage
gsutil du -s gs://${GCP_PROJECT_ID}-code-developer
# Clean up old logs and checkpoints if >100GB

# 6. Review committed use discounts
# If usage is consistent, commit to 1 or 3 years for 25-52% savings

# 7. Set up cost anomaly alerts
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Cost Anomaly Alert" \
  --condition-threshold-value=200 \
  --condition-threshold-duration=86400s
```

**Action items**:
- [ ] Implement identified optimizations
- [ ] Project next month's costs
- [ ] Update budget alerts if needed
- [ ] Report cost trends to management

---

### End of Month: Backup Verification (30 minutes)

**Procedure**:

```bash
# 1. List all backups
gcloud sql backups list --instance=code-developer-db --limit 30

# 2. Verify backup schedule
gcloud sql instances describe code-developer-db \
  --format="value(settings.backupConfiguration)"

# Expected:
# - Enabled: True
# - Start time: 03:00 (local time)
# - Point-in-time recovery: Enabled

# 3. Test backup restoration (quarterly, but document monthly)
# Create test instance from backup
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=code-developer-db \
  --backup-id=<BACKUP_ID> \
  --target-instance=code-developer-db-test

# Verify data integrity
gcloud sql connect code-developer-db-test --user=coffee_maker --database=coffee_maker
SELECT COUNT(*) FROM notifications;
SELECT COUNT(*) FROM task_metrics;
\q

# Delete test instance
gcloud sql instances delete code-developer-db-test --quiet

# 4. Backup ROADMAP.md to Cloud Storage
git pull origin roadmap
gsutil cp docs/ROADMAP.md gs://${GCP_PROJECT_ID}-code-developer/backups/ROADMAP-$(date +%Y-%m-%d).md

# 5. Document backup metrics
echo "Backup Report - $(date +%Y-%m)" > backup-report.txt
echo "================================" >> backup-report.txt
gcloud sql backups list --instance=code-developer-db --limit 30 >> backup-report.txt

# 6. Verify backup retention (keep 30 days)
gcloud sql instances patch code-developer-db \
  --backup-count=30
```

**Action items**:
- [ ] Verify all backups successful
- [ ] Test restoration quarterly
- [ ] Document backup metrics
- [ ] Update disaster recovery plan

---

## Common Procedures

### Procedure: Deploy New Version

**Trigger**: New code merged to main branch
**Estimated time**: 15 minutes

**Steps**:

```bash
# 1. Verify code is tested
git pull origin main
pytest tests/

# 2. Build new container image
gcloud builds submit \
  --tag gcr.io/$GCP_PROJECT_ID/code-developer:$(git rev-parse --short HEAD) \
  --tag gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --dockerfile=coffee_maker/deployment/Dockerfile \
  .

# 3. Deploy to Cloud Run
gcloud run deploy code-developer \
  --image gcr.io/$GCP_PROJECT_ID/code-developer:latest \
  --platform managed \
  --region us-central1

# 4. Verify deployment
sleep 30  # Wait for deployment to stabilize
curl $SERVICE_URL/api/health

# 5. Monitor for errors
gcloud run services logs tail code-developer \
  --region us-central1 \
  --log-filter="severity>=WARNING"

# 6. Rollback if issues detected
# gcloud run services update code-developer \
#   --image gcr.io/$GCP_PROJECT_ID/code-developer:PREVIOUS_COMMIT_SHA \
#   --region us-central1
```

**Success criteria**:
- [x] Health check returns "healthy"
- [x] No ERROR logs in first 5 minutes
- [x] Daemon status shows "running"

---

### Procedure: Rotate API Keys

**Trigger**: Every 90 days (automated reminder)
**Estimated time**: 20 minutes

**Steps**:

```bash
# 1. Create new Anthropic API key
# Visit: https://console.anthropic.com/settings/keys
# Click "Create Key"
# Copy new key: sk-ant-api03-NEW_KEY

# 2. Add new key to Secret Manager (as new version)
echo -n "sk-ant-api03-NEW_KEY" | gcloud secrets versions add anthropic-api-key \
  --data-file=-

# 3. Test new key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $(gcloud secrets versions access latest --secret=anthropic-api-key)" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'

# 4. Deploy update (Cloud Run will pick up latest secret version)
gcloud run services update code-developer --region us-central1

# 5. Verify daemon still works
curl $SERVICE_URL/api/health
gcloud run services logs tail code-developer --region us-central1

# 6. Disable old key version (after 24h grace period)
OLD_VERSION=$(gcloud secrets versions list anthropic-api-key \
  --format="value(name)" --limit=1 --sort-by="~createTime" --offset=1)
gcloud secrets versions disable $OLD_VERSION --secret=anthropic-api-key

# 7. Revoke old key in Anthropic console
# Visit: https://console.anthropic.com/settings/keys
# Find old key and click "Revoke"

# 8. Repeat for GitHub token
# Create new token: https://github.com/settings/tokens/new
# Update secret: github-token
# Test: gh auth status
# Revoke old token

# 9. Document rotation
echo "$(date): Rotated anthropic-api-key and github-token" >> secret-rotation.log
```

**Success criteria**:
- [x] New keys work correctly
- [x] Old keys revoked
- [x] No service interruption
- [x] Rotation documented

---

### Procedure: Scale Up Resources

**Trigger**: Performance degradation or increased load
**Estimated time**: 10 minutes

**Steps**:

```bash
# 1. Check current resource allocation
gcloud run services describe code-developer \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].resources.limits)"

# Current: memory=2Gi, cpu=1

# 2. Analyze metrics to determine bottleneck
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/cpu/utilizations"' \
  --format=json

gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"' \
  --format=json

# 3. Scale up as needed
# If CPU >80%:
gcloud run services update code-developer \
  --region us-central1 \
  --cpu 2

# If memory >85%:
gcloud run services update code-developer \
  --region us-central1 \
  --memory 4Gi

# If need more instances (not typical for this workload):
gcloud run services update code-developer \
  --region us-central1 \
  --max-instances 3

# 4. Monitor performance after scaling
# Wait 10 minutes for metrics to stabilize
sleep 600

# Check utilization again
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/cpu/utilizations"' \
  --format=json

# 5. Update cost projections
# New resources will increase monthly cost
# Document in cost tracking spreadsheet
```

**Success criteria**:
- [x] Resource utilization <70%
- [x] Response times improved
- [x] Cost impact documented

---

### Procedure: Emergency Shutdown

**Trigger**: Critical incident (e.g., runaway costs, security breach)
**Estimated time**: 5 minutes

**Steps**:

```bash
# 1. STOP ALL TRAFFIC immediately
gcloud run services update code-developer \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 0

# 2. Revoke API access
gcloud secrets versions disable latest --secret=anthropic-api-key
gcloud secrets versions disable latest --secret=github-token

# 3. Capture current state for investigation
gcloud run services describe code-developer \
  --region us-central1 \
  --format=yaml > incident-state-$(date +%Y%m%d-%H%M%S).yaml

gcloud run services logs read code-developer \
  --region us-central1 \
  --limit 5000 > incident-logs-$(date +%Y%m%d-%H%M%S).txt

# 4. Notify stakeholders
# Send alert to Slack/email/PagerDuty

# 5. Assess damage
# Check recent commits
gh api repos/YOUR_REPO/commits --jq '.[0:20] | .[] | {sha:.sha[0:7], message:.commit.message, date:.commit.author.date}'

# Check recent PRs
gh pr list --repo YOUR_REPO --limit 20

# Check database for anomalies
gcloud sql connect code-developer-db --user=coffee_maker --database=coffee_maker
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50;
\q

# 6. Document incident
cat > incident-$(date +%Y%m%d-%H%M%S).md << 'EOF'
# Incident Report

**Date**: $(date)
**Severity**: CRITICAL
**Status**: INVESTIGATING

## Timeline
- HH:MM - Incident detected
- HH:MM - Emergency shutdown initiated
- HH:MM - API access revoked

## Impact
- [Describe impact]

## Root Cause
- [To be determined]

## Recovery Plan
- [To be defined]
EOF

# 7. Begin investigation and recovery
# See: Incident Response procedures
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| **P0 - Critical** | Service down, data loss, security breach | Immediate | CTO, CEO |
| **P1 - High** | Degraded performance, high costs | 1 hour | Engineering Manager |
| **P2 - Medium** | Non-critical errors, warnings | 4 hours | Team Lead |
| **P3 - Low** | Minor issues, improvements | 1 day | Assigned engineer |

### P0 - Critical Incident Response

**Examples**: Service completely down, database corrupted, security breach

**Immediate actions** (within 5 minutes):

1. **Assess**: Determine severity and impact
   ```bash
   curl $SERVICE_URL/api/health
   gcloud run services describe code-developer --region us-central1
   ```

2. **Contain**: Stop daemon if causing damage
   ```bash
   gcloud run services update code-developer --region us-central1 --min-instances 0 --max-instances 0
   ```

3. **Notify**: Alert on-call and management
   ```
   Slack: @channel CRITICAL: code_developer service down
   Email: engineering@company.com
   PagerDuty: Trigger P0 alert
   ```

4. **Investigate**: Gather logs and state
   ```bash
   gcloud run services logs read code-developer --region us-central1 --limit 1000 > incident-logs.txt
   ```

5. **Recover**: Follow recovery procedures
   - Database: Restore from backup
   - Service: Deploy previous known-good version
   - Secrets: Rotate if compromised

6. **Document**: Create incident report
   - Use template in tickets/INCIDENT_TEMPLATE.md
   - Document timeline, impact, root cause, remediation

**Post-incident**:
- [ ] Conduct blameless postmortem
- [ ] Implement preventive measures
- [ ] Update runbook with learnings

---

## Monitoring & Alerts

### Critical Alerts (PagerDuty / On-Call)

**Alert 1: Service Down**
```yaml
Condition: Health check fails for >5 minutes
Action: Page on-call immediately
Priority: P0
Runbook: Emergency Shutdown procedure
```

**Alert 2: High Error Rate**
```yaml
Condition: Error rate >5% over 10 minutes
Action: Notify on-call
Priority: P1
Runbook: Check logs for root cause
```

**Alert 3: Cost Spike**
```yaml
Condition: Daily cost >$50 (2x normal)
Action: Notify on-call and finance
Priority: P1
Runbook: Cost optimization review
```

**Alert 4: Database Connection Lost**
```yaml
Condition: Cannot connect to Cloud SQL for >3 minutes
Action: Notify on-call
Priority: P1
Runbook: Database troubleshooting
```

### Warning Alerts (Slack / Email)

**Alert 5: High CPU Usage**
```yaml
Condition: CPU >80% for >15 minutes
Action: Slack notification
Priority: P2
Runbook: Scale up resources
```

**Alert 6: High Memory Usage**
```yaml
Condition: Memory >85% for >15 minutes
Action: Slack notification
Priority: P2
Runbook: Investigate memory leak or scale up
```

**Alert 7: Slow Performance**
```yaml
Condition: Average iteration time >10 minutes
Action: Email notification
Priority: P2
Runbook: Performance optimization
```

---

## Escalation Procedures

### Escalation Path

1. **Level 1**: On-call engineer (primary)
2. **Level 2**: Team lead / Engineering manager
3. **Level 3**: CTO / VP Engineering
4. **Level 4**: CEO (for business-critical issues)

### When to Escalate

| Scenario | Escalate To | Timeframe |
|----------|-------------|-----------|
| Cannot resolve in 1 hour | Team lead | Immediately |
| Data loss or corruption | Engineering manager | Immediately |
| Security breach | CTO + Security team | Immediately |
| Cost exceeds $500/day | Finance + CTO | Same day |
| Extended outage (>4 hours) | CTO | Immediately |

### Contact Information

```yaml
On-Call:
  Primary: [Phone] [Email] [Slack]
  Secondary: [Phone] [Email] [Slack]

Team Lead:
  Name: [Name]
  Phone: [Phone]
  Email: [Email]
  Slack: @team-lead

Engineering Manager:
  Name: [Name]
  Phone: [Phone]
  Email: [Email]
  Slack: @eng-manager

CTO:
  Name: [Name]
  Phone: [Phone]
  Email: [Email]
  Slack: @cto

External Support:
  GCP Support: https://console.cloud.google.com/support
  Anthropic Support: support@anthropic.com
  GitHub Support: https://support.github.com
```

---

## Deployment Procedures

### Standard Deployment (Low Risk)

**Trigger**: Non-critical features, documentation updates
**Approval**: Team lead
**Rollback**: Automatic if health checks fail

```bash
# See: Procedure: Deploy New Version above
```

### Blue-Green Deployment (Medium Risk)

**Trigger**: Significant changes, database migrations
**Approval**: Engineering manager
**Rollback**: Manual switch to blue

```bash
# 1. Deploy to green environment
gcloud run deploy code-developer-green \
  --image gcr.io/$GCP_PROJECT_ID/code-developer:NEW_VERSION \
  --region us-central1

# 2. Run smoke tests on green
curl https://code-developer-green-HASH.run.app/api/health

# 3. Switch traffic to green (gradual)
gcloud run services update-traffic code-developer \
  --to-revisions=code-developer-green=10 \
  --region us-central1

# Monitor for issues...

# 4. If good, increase to 100%
gcloud run services update-traffic code-developer \
  --to-revisions=code-developer-green=100 \
  --region us-central1

# 5. If issues, rollback to blue
gcloud run services update-traffic code-developer \
  --to-revisions=code-developer-blue=100 \
  --region us-central1
```

### Emergency Hotfix

**Trigger**: Critical bug in production
**Approval**: Verbal approval from team lead
**Process**: Fast-track deployment

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug-fix main

# 2. Fix bug and test locally
# ... make changes ...
pytest tests/ -k test_critical_feature

# 3. Commit and push
git commit -m "hotfix: Fix critical bug"
git push origin hotfix/critical-bug-fix

# 4. Build and deploy immediately
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/code-developer:hotfix-$(date +%Y%m%d-%H%M) .
gcloud run deploy code-developer \
  --image gcr.io/$GCP_PROJECT_ID/code-developer:hotfix-$(date +%Y%m%d-%H%M) \
  --region us-central1

# 5. Verify fix
curl $SERVICE_URL/api/health
gcloud run services logs tail code-developer --region us-central1

# 6. Merge hotfix to main
gh pr create --title "Hotfix: Critical bug fix" --body "Emergency fix for production issue"
gh pr merge --auto --squash
```

---

## Appendix

### Useful Commands

```bash
# Quick status check
alias gcp-status='curl -H "Authorization: Bearer $COFFEE_MAKER_API_KEY" $SERVICE_URL/api/daemon/status | jq'

# Stream logs
alias gcp-logs='gcloud run services logs tail code-developer --region us-central1'

# Check costs
alias gcp-costs='gcloud billing accounts list && echo "See: https://console.cloud.google.com/billing/reports"'

# Emergency stop
alias gcp-stop='gcloud run services update code-developer --region us-central1 --min-instances 0 --max-instances 0'

# Restart daemon
alias gcp-restart='gcloud run services update code-developer --region us-central1 --min-instances 1'
```

### Checklists

**Pre-Deployment Checklist**:
- [ ] Code reviewed and approved
- [ ] Tests passing locally
- [ ] Database migrations tested
- [ ] Secrets updated if needed
- [ ] Rollback plan documented
- [ ] Team notified of deployment

**Post-Deployment Checklist**:
- [ ] Health checks passing
- [ ] No errors in logs (first 10 minutes)
- [ ] Daemon status confirmed running
- [ ] Performance metrics normal
- [ ] Team notified of completion

**End-of-Day Checklist**:
- [ ] All alerts acknowledged
- [ ] Critical issues resolved or escalated
- [ ] Incident log updated
- [ ] Handoff notes written for next on-call

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Review Schedule**: Quarterly
**Owner**: DevOps Team
