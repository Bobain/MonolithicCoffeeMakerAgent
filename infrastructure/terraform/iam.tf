# IAM configuration for code_developer daemon

# Service account for Cloud Run
resource "google_service_account" "code_developer" {
  account_id   = "${local.service_name}-sa"
  display_name = "Code Developer Daemon Service Account"
  description  = "Service account for code_developer autonomous daemon running on Cloud Run"
  project      = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Storage permissions
resource "google_project_iam_member" "code_developer_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Logging permissions
resource "google_project_iam_member" "code_developer_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Monitoring permissions
resource "google_project_iam_member" "code_developer_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Error reporting permissions
resource "google_project_iam_member" "code_developer_error_writer" {
  project = var.project_id
  role    = "roles/errorreporting.writer"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Cloud Trace permissions (for distributed tracing)
resource "google_project_iam_member" "code_developer_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Service account token creator (for authenticated API calls)
resource "google_service_account_iam_member" "code_developer_token_creator" {
  service_account_id = google_service_account.code_developer.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.code_developer.email}"
}

# Cloud Build permissions (if using Cloud Build for deployment)
resource "google_project_iam_member" "code_developer_cloud_build" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Artifact Registry permissions (for container images)
resource "google_project_iam_member" "code_developer_artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# Cloud Run admin (for self-deployment capabilities)
# Uncomment if daemon needs to deploy itself
# resource "google_project_iam_member" "code_developer_run_admin" {
#   project = var.project_id
#   role    = "roles/run.admin"
#   member  = "serviceAccount:${google_service_account.code_developer.email}"
# }

# Service account for GitHub Actions (CI/CD)
resource "google_service_account" "github_actions" {
  account_id   = "${local.service_name}-github-actions"
  display_name = "GitHub Actions Service Account"
  description  = "Service account for GitHub Actions to deploy code_developer"
  project      = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

# GitHub Actions permissions
resource "google_project_iam_member" "github_actions_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_artifact_registry_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Workload Identity Federation for GitHub Actions (recommended)
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Workload Identity Pool for GitHub Actions"
  project                   = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"
  description                        = "Workload Identity Pool Provider for GitHub Actions"
  project                            = var.project_id

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Bind GitHub Actions service account to Workload Identity
resource "google_service_account_iam_member" "github_workload_identity" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/Bobain/MonolithicCoffeeMakerAgent"
}

# Custom role for fine-grained daemon permissions (optional)
resource "google_project_iam_custom_role" "code_developer_daemon" {
  role_id     = "codeDeveloperDaemon"
  title       = "Code Developer Daemon"
  description = "Custom role with minimum permissions for code_developer daemon"
  project     = var.project_id

  permissions = [
    "storage.buckets.get",
    "storage.buckets.list",
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",
    "storage.objects.update",
    "logging.logEntries.create",
    "monitoring.timeSeries.create",
    "cloudsql.instances.connect",
    "cloudsql.instances.get",
  ]
}

# Outputs
output "service_account_key_command" {
  description = "Command to create a service account key (for local testing)"
  value       = "gcloud iam service-accounts keys create key.json --iam-account=${google_service_account.code_developer.email}"
}

output "github_actions_service_account_email" {
  description = "GitHub Actions service account email"
  value       = google_service_account.github_actions.email
}

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}
