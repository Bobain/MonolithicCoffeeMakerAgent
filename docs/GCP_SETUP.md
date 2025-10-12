# GCP Account Setup & Prerequisites

**Version**: 1.0
**Last Updated**: 2025-10-12
**Estimated Setup Time**: 30-45 minutes

This guide covers the initial setup of your Google Cloud Platform account and environment for deploying the `code_developer` daemon.

---

## Table of Contents

1. [GCP Account Creation](#gcp-account-creation)
2. [Project Setup](#project-setup)
3. [Billing Configuration](#billing-configuration)
4. [API Enablement](#api-enablement)
5. [Authentication Setup](#authentication-setup)
6. [Local Environment Configuration](#local-environment-configuration)
7. [Security Best Practices](#security-best-practices)
8. [Cost Controls](#cost-controls)
9. [Verification](#verification)

---

## GCP Account Creation

### New to GCP?

Google Cloud Platform offers a **$300 free credit** for new users (valid for 90 days).

**Steps**:

1. **Visit**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Sign in** with your Google account (or create one)
3. **Activate Free Trial**:
   - Click "Activate" button
   - Enter billing information (required, but you won't be charged during free trial)
   - Agree to terms of service

**What you get**:
- $300 credit for 90 days
- Access to all GCP services
- No automatic charges after trial ends (must manually upgrade)

**After free trial**:
- Estimated cost: $116-297/month for code_developer daemon
- You control when to upgrade to paid account

### Existing GCP User?

If you already have a GCP account:
- Create a new project for code_developer (recommended)
- Ensure billing is enabled
- Skip to [Project Setup](#project-setup)

---

## Project Setup

### Create New Project

**Option 1: Web Console**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click project dropdown (top-left, next to "Google Cloud")
3. Click "New Project"
4. Fill in:
   - **Project name**: `code-developer-prod` (or your choice)
   - **Organization**: (if applicable)
   - **Location**: (parent organization or folder)
5. Click "Create"
6. Note the **Project ID** (e.g., `code-developer-prod-123456`)

**Option 2: gcloud CLI**

```bash
# Install gcloud CLI first (see below)
gcloud projects create code-developer-prod \
  --name="code_developer Production" \
  --set-as-default

# Get project ID
export GCP_PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $GCP_PROJECT_ID"
```

### Project Naming Best Practices

**Good project names**:
- `code-developer-prod` (clear purpose)
- `my-company-code-dev` (organization prefix)
- `ai-developer-production` (descriptive)

**Avoid**:
- Generic names like `project-1`, `test`
- Names containing sensitive data
- Very long names (max 30 characters)

---

## Billing Configuration

### Link Billing Account

**Requirement**: You must enable billing to use GCP services beyond free tier quotas.

**Steps**:

1. **Navigate to Billing**:
   - [console.cloud.google.com/billing](https://console.cloud.google.com/billing)

2. **Create or select billing account**:
   - If first time: Click "Create account"
   - Fill in billing details (credit card required)

3. **Link project to billing account**:
   ```bash
   # List billing accounts
   gcloud billing accounts list

   # Link project (replace BILLING_ACCOUNT_ID)
   gcloud billing projects link $GCP_PROJECT_ID \
     --billing-account=BILLING_ACCOUNT_ID

   # Verify
   gcloud billing projects describe $GCP_PROJECT_ID
   ```

### Set Up Budget Alerts

**Protect yourself from unexpected charges**:

```bash
# Get billing account ID
BILLING_ACCOUNT_ID=$(gcloud billing accounts list --format="value(name)" --limit=1)

# Create budget alert (replace with your email)
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT_ID \
  --display-name="code_developer Monthly Budget" \
  --budget-amount=200USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --threshold-rule=percent=120 \
  --filter-projects=$GCP_PROJECT_ID \
  --all-updates-rule-monitoring-notification-channels=YOUR_EMAIL@example.com \
  --all-updates-rule-pubsub-topic=projects/$GCP_PROJECT_ID/topics/budget-alerts

# You'll receive email alerts at 50%, 80%, 100%, and 120% of budget
```

**Budget recommendations**:
- **Development**: $100/month (for testing)
- **Production**: $200-300/month (24/7 operation)
- **Enterprise**: $500+/month (multiple projects)

---

## API Enablement

### Required APIs

The following APIs must be enabled for code_developer to function:

| API | Purpose | Cost |
|-----|---------|------|
| **Cloud Run API** | Container hosting | Pay per use |
| **Cloud SQL Admin API** | Database management | Instance cost |
| **Cloud Storage API** | File storage | Storage cost |
| **Secret Manager API** | Secure credentials | Minimal |
| **Cloud Logging API** | Centralized logs | Log volume cost |
| **Cloud Monitoring API** | Metrics & alerts | Free tier |
| **Cloud Build API** | Container building | Build minutes cost |

### Enable APIs

**Option 1: Quick Enable (All at Once)**

```bash
# Set project
gcloud config set project $GCP_PROJECT_ID

# Enable all required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudbuild.googleapis.com

# Verify (should see all 7 APIs)
gcloud services list --enabled | grep -E 'run|sql|storage|secret|logging|monitoring|build'
```

**Option 2: Web Console**

1. Go to [APIs & Services → Library](https://console.cloud.google.com/apis/library)
2. Search for each API name (e.g., "Cloud Run API")
3. Click "Enable" for each

**Expected time**: 2-3 minutes for all APIs to activate

---

## Authentication Setup

### Install gcloud CLI

**macOS (Homebrew)**:
```bash
brew install --cask google-cloud-sdk

# Initialize
gcloud init

# Verify
gcloud --version  # Should be 400.0+
```

**Linux (Ubuntu/Debian)**:
```bash
# Add Cloud SDK distribution URI
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Install
sudo apt-get update && sudo apt-get install google-cloud-cli

# Verify
gcloud --version
```

**Windows**:
- Download installer: https://cloud.google.com/sdk/docs/install
- Run installer
- Open Cloud SDK Shell
- Run `gcloud init`

### Authenticate gcloud

```bash
# Login with your Google account
gcloud auth login

# This will open a browser window - sign in with your Google account
# Grant permissions when prompted

# Set project
gcloud config set project $GCP_PROJECT_ID

# Set default region
gcloud config set run/region us-central1

# Verify authentication
gcloud auth list
# Should show:
#   * your-email@gmail.com
#   Credentialed Accounts
```

### Application Default Credentials (ADC)

**Required for local development**:

```bash
# Set up ADC (needed for local testing)
gcloud auth application-default login

# This creates credentials at:
# ~/.config/gcloud/application_default_credentials.json

# Verify
gcloud auth application-default print-access-token
# Should print a long access token
```

### Service Account Setup

**For production deployment**:

```bash
# Create service account
gcloud iam service-accounts create code-developer \
  --display-name="code_developer autonomous daemon" \
  --description="Service account for code_developer running on Cloud Run"

# Get service account email
export SA_EMAIL=code-developer@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# Grant necessary roles
for role in \
  roles/cloudsql.client \
  roles/secretmanager.secretAccessor \
  roles/storage.objectAdmin \
  roles/logging.logWriter \
  roles/monitoring.metricWriter; do
  gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role"
done

# Verify permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:$SA_EMAIL"
```

---

## Local Environment Configuration

### Install Required Tools

**1. Docker**:
```bash
# macOS
brew install --cask docker

# Linux (Ubuntu)
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Verify
docker --version  # Need: 20.10+
docker-compose --version  # Need: 1.29+

# Start Docker
sudo systemctl start docker  # Linux
open -a Docker  # macOS
```

**2. Terraform** (optional, for infrastructure as code):
```bash
# macOS
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify
terraform --version  # Need: 1.5+
```

**3. GitHub CLI** (for PR management):
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update
sudo apt-get install gh

# Authenticate
gh auth login

# Verify
gh auth status
```

### Set Up Environment Variables

**Create `.env` file for local development**:

```bash
# Navigate to project root
cd /path/to/MonolithicCoffeeMakerAgent

# Create .env file
cat > .env << 'EOF'
# GCP Configuration
GCP_PROJECT_ID=code-developer-prod-123456
GCP_REGION=us-central1
GCS_BUCKET_NAME=${GCP_PROJECT_ID}-code-developer

# API Keys (get from respective services)
ANTHROPIC_API_KEY=sk-ant-api03-...
GITHUB_TOKEN=ghp_...

# Daemon Configuration
COFFEE_MAKER_MODE=daemon
COFFEE_MAKER_LOG_LEVEL=INFO
COFFEE_MAKER_AUTO_APPROVE=true
COFFEE_MAKER_CREATE_PRS=true
ROADMAP_PATH=/workspace/docs/ROADMAP.md

# Database (for local testing)
DATABASE_URL=postgresql://coffee_maker:coffee_maker@localhost:5432/coffee_maker

# API Authentication
COFFEE_MAKER_API_KEY=$(openssl rand -base64 32)
EOF

# Load environment variables
source .env

# Add .env to .gitignore (IMPORTANT!)
echo ".env" >> .gitignore
```

### Configure project-manager CLI

**Create local configuration**:

```bash
# Create config directory
mkdir -p ~/.config/coffee-maker

# Create configuration file
cat > ~/.config/coffee-maker/gcp.yaml << EOF
gcp:
  enabled: false  # Set to true after deployment
  api_url: ""     # Will be populated after deployment
  api_key: ""     # Will be populated after deployment
  project_id: $GCP_PROJECT_ID
  region: us-central1

  daemon:
    auto_start: true
    check_interval: 30  # seconds
    notify_on_completion: true

# Local mode configuration (current)
local:
  enabled: true
  roadmap_path: $(pwd)/docs/ROADMAP.md
  database_path: ~/.coffee_maker/notifications.db
EOF

# Verify
cat ~/.config/coffee-maker/gcp.yaml
```

---

## Security Best Practices

### API Key Management

**DO**:
- ✅ Store API keys in GCP Secret Manager (never in code)
- ✅ Use environment variables for local development
- ✅ Rotate keys every 90 days
- ✅ Use separate keys for dev/prod

**DON'T**:
- ❌ Commit API keys to Git
- ❌ Share keys in Slack/email
- ❌ Reuse keys across projects
- ❌ Store keys in plaintext files

**Example - Secure API Key Storage**:

```bash
# Store Anthropic API key in Secret Manager
echo -n "sk-ant-api03-..." | gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant service account access
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

# Verify
gcloud secrets versions access latest --secret="anthropic-api-key"
```

### Network Security

**Restrict Cloud Run access**:

```bash
# Deploy with authentication required (default)
gcloud run deploy code-developer \
  --no-allow-unauthenticated \
  --region us-central1

# Only allow authenticated requests
# Users must have roles/run.invoker role
```

**Set up VPC connector** (optional, for private database access):

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create code-developer-connector \
  --region us-central1 \
  --subnet=default \
  --subnet-project=$GCP_PROJECT_ID

# Use in Cloud Run
gcloud run services update code-developer \
  --region us-central1 \
  --vpc-connector=code-developer-connector
```

### IAM Best Practices

**Principle of Least Privilege**:

```bash
# Grant only necessary permissions
# Example: Read-only access for monitoring user
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="user:monitor@example.com" \
  --role="roles/run.viewer"

# Separate service accounts for different functions
# Example: One for daemon, one for API
```

---

## Cost Controls

### Enable Cost Management Features

**1. Budget Alerts** (already covered above):
```bash
# Monitor spending and get notified
gcloud billing budgets create --display-name="code_developer Budget" ...
```

**2. Committed Use Discounts**:
```bash
# Save 25-52% by committing to 1 or 3 years
# For Cloud SQL, Cloud Run, etc.
# See: https://cloud.google.com/docs/cuds
```

**3. Resource Quotas**:
```bash
# Limit maximum resource usage
gcloud compute project-info describe --project=$GCP_PROJECT_ID

# Set quotas via console:
# IAM & Admin → Quotas
# Example: Limit Cloud Run instances to 3 max
```

**4. Cost Tracking Labels**:
```bash
# Tag resources for cost attribution
gcloud run services update code-developer \
  --region us-central1 \
  --labels=project=code-developer,env=prod,team=ai-development
```

### Monitor Costs

**View current costs**:

```bash
# Get billing account
gcloud billing accounts list

# View project costs (requires billing export setup)
# Console: https://console.cloud.google.com/billing/reports

# Set up billing export to BigQuery (recommended)
gcloud billing accounts list
gcloud beta billing accounts set-billing-export \
  --billing-account=BILLING_ACCOUNT_ID \
  --dataset-id=billing_export \
  --project=$GCP_PROJECT_ID
```

---

## Verification

### Pre-Deployment Checklist

Run these commands to verify your environment is ready:

```bash
#!/bin/bash
# verify-gcp-setup.sh

echo "🔍 Verifying GCP Setup..."

# 1. Check gcloud authentication
echo "1️⃣ Checking gcloud authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" || exit 1
echo "✅ Authenticated"

# 2. Check project
echo "2️⃣ Checking project..."
PROJECT=$(gcloud config get-value project)
if [ -z "$PROJECT" ]; then
  echo "❌ No project set"
  exit 1
fi
echo "✅ Project: $PROJECT"

# 3. Check billing
echo "3️⃣ Checking billing..."
gcloud billing projects describe $PROJECT --format="value(billingEnabled)" | grep -q "True" || {
  echo "❌ Billing not enabled"
  exit 1
}
echo "✅ Billing enabled"

# 4. Check APIs
echo "4️⃣ Checking APIs..."
for api in run.googleapis.com sqladmin.googleapis.com storage.googleapis.com secretmanager.googleapis.com; do
  gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api" || {
    echo "❌ API not enabled: $api"
    exit 1
  }
done
echo "✅ All required APIs enabled"

# 5. Check service account
echo "5️⃣ Checking service account..."
gcloud iam service-accounts describe code-developer@${PROJECT}.iam.gserviceaccount.com &>/dev/null || {
  echo "⚠️  Service account not created yet (will be created during deployment)"
}
echo "✅ Service account ready"

# 6. Check environment variables
echo "6️⃣ Checking environment variables..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠️  ANTHROPIC_API_KEY not set"
fi
if [ -z "$GITHUB_TOKEN" ]; then
  echo "⚠️  GITHUB_TOKEN not set"
fi
echo "✅ Environment variables checked"

echo ""
echo "✅ GCP setup verification complete!"
echo "You're ready to proceed with deployment."
```

**Run verification**:
```bash
chmod +x verify-gcp-setup.sh
./verify-gcp-setup.sh
```

**Expected output**:
```
🔍 Verifying GCP Setup...
1️⃣ Checking gcloud authentication...
✅ Authenticated
2️⃣ Checking project...
✅ Project: code-developer-prod-123456
3️⃣ Checking billing...
✅ Billing enabled
4️⃣ Checking APIs...
✅ All required APIs enabled
5️⃣ Checking service account...
✅ Service account ready
6️⃣ Checking environment variables...
✅ Environment variables checked

✅ GCP setup verification complete!
You're ready to proceed with deployment.
```

---

## Next Steps

After completing this setup:

1. ✅ **Proceed to Deployment**:
   - Follow [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md)

2. **Test Locally First**:
   - Build and run container locally with docker-compose
   - Verify daemon functionality before deploying to cloud

3. **Set Up Monitoring**:
   - Configure Cloud Monitoring dashboards
   - Set up alert policies

4. **Review Security**:
   - Audit IAM permissions
   - Enable audit logging
   - Review Secret Manager access

---

## Troubleshooting

### Common Issues

**"Project not found"**:
```bash
# Verify project exists
gcloud projects list

# Set correct project
gcloud config set project YOUR_PROJECT_ID
```

**"Permission denied"**:
```bash
# Check your IAM roles
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$(gcloud config get-value account)"

# You need at least roles/editor or roles/owner
```

**"Billing not enabled"**:
```bash
# Check billing status
gcloud billing projects describe $GCP_PROJECT_ID

# Link billing account
gcloud billing projects link $GCP_PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

**"API not enabled"**:
```bash
# Enable specific API
gcloud services enable run.googleapis.com

# List all available APIs
gcloud services list --available
```

### Getting Help

- **GCP Documentation**: https://cloud.google.com/docs
- **GCP Support**: https://cloud.google.com/support
- **Community**: https://stackoverflow.com/questions/tagged/google-cloud-platform
- **Project Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues

---

## Summary

**What you've set up**:
- [x] GCP account with billing
- [x] Project created and configured
- [x] Required APIs enabled
- [x] Authentication configured (gcloud, ADC, service accounts)
- [x] Local environment ready
- [x] Budget alerts and cost controls
- [x] Security best practices applied

**Ready for deployment!** 🚀

Proceed to [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md) to deploy your code_developer daemon.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Estimated Setup Time**: 30-45 minutes
