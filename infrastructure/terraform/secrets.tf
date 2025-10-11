# Secret Manager configuration for code_developer daemon
# Securely stores API keys and credentials

# Anthropic API key
resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "code-developer-anthropic-api-key"
  project   = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_secret_manager_secret_version" "anthropic_api_key" {
  secret = google_secret_manager_secret.anthropic_api_key.id
  secret_data = var.anthropic_api_key != "" ? var.anthropic_api_key : (
    "PLACEHOLDER_SET_THIS_AFTER_DEPLOYMENT"
  )
}

# GitHub personal access token
resource "google_secret_manager_secret" "github_token" {
  secret_id = "code-developer-github-token"
  project   = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_secret_manager_secret_version" "github_token" {
  secret      = google_secret_manager_secret.github_token.id
  secret_data = var.github_token != "" ? var.github_token : "PLACEHOLDER_SET_THIS_AFTER_DEPLOYMENT"
}

# Coffee Maker API key (for project-manager CLI authentication)
resource "google_secret_manager_secret" "api_key" {
  secret_id = "code-developer-api-key"
  project   = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Generate random API key if not provided
resource "random_password" "api_key" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = var.api_key != "" ? var.api_key : random_password.api_key.result
}

# Slack webhook URL (optional, for notifications)
resource "google_secret_manager_secret" "slack_webhook" {
  count     = var.alert_slack_webhook != "" ? 1 : 0
  secret_id = "code-developer-slack-webhook"
  project   = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_secret_manager_secret_version" "slack_webhook" {
  count       = var.alert_slack_webhook != "" ? 1 : 0
  secret      = google_secret_manager_secret.slack_webhook[0].id
  secret_data = var.alert_slack_webhook
}

# IAM bindings for service account to access secrets
resource "google_secret_manager_secret_iam_member" "anthropic_api_key_accessor" {
  secret_id = google_secret_manager_secret.anthropic_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.code_developer.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "github_token_accessor" {
  secret_id = google_secret_manager_secret.github_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.code_developer.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_key_accessor" {
  secret_id = google_secret_manager_secret.api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.code_developer.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "slack_webhook_accessor" {
  count     = var.alert_slack_webhook != "" ? 1 : 0
  secret_id = google_secret_manager_secret.slack_webhook[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.code_developer.email}"
  project   = var.project_id
}

# Database password access (if Cloud SQL enabled)
resource "google_secret_manager_secret_iam_member" "db_password_accessor" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = google_secret_manager_secret.db_password[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.code_developer.email}"
  project   = var.project_id
}

# Output commands to update secrets after deployment
output "update_secrets_commands" {
  description = "Commands to update secrets after deployment"
  value = {
    anthropic_api_key = "echo -n 'YOUR_API_KEY' | gcloud secrets versions add ${google_secret_manager_secret.anthropic_api_key.secret_id} --data-file=-"
    github_token      = "echo -n 'YOUR_GITHUB_TOKEN' | gcloud secrets versions add ${google_secret_manager_secret.github_token.secret_id} --data-file=-"
    api_key           = "echo -n 'YOUR_API_KEY' | gcloud secrets versions add ${google_secret_manager_secret.api_key.secret_id} --data-file=-"
  }
  sensitive = true
}
