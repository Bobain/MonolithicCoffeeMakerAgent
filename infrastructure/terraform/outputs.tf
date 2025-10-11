# Terraform outputs for code_developer GCP deployment
# These values are displayed after deployment and can be used by other tools

# Cloud Run outputs
output "cloud_run_service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.code_developer.uri
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.code_developer.name
}

output "cloud_run_service_id" {
  description = "ID of the Cloud Run service"
  value       = google_cloud_run_v2_service.code_developer.id
}

# Storage outputs
output "storage_bucket_name" {
  description = "Name of the Cloud Storage bucket for project files"
  value       = google_storage_bucket.code_developer_storage.name
}

output "storage_bucket_url" {
  description = "URL of the Cloud Storage bucket"
  value       = google_storage_bucket.code_developer_storage.url
}

# Database outputs
output "database_instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = var.enable_cloud_sql ? google_sql_database_instance.code_developer[0].name : null
}

output "database_connection_name" {
  description = "Connection name for Cloud SQL (used by Cloud Run)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.code_developer[0].connection_name : null
}

output "database_private_ip" {
  description = "Private IP address of the database"
  value       = var.enable_cloud_sql ? google_sql_database_instance.code_developer[0].private_ip_address : null
  sensitive   = true
}

output "database_name" {
  description = "Name of the database"
  value       = var.enable_cloud_sql ? google_sql_database.code_developer_db[0].name : null
}

# Secret Manager outputs
output "secret_anthropic_api_key_id" {
  description = "Secret Manager ID for Anthropic API key"
  value       = google_secret_manager_secret.anthropic_api_key.secret_id
}

output "secret_github_token_id" {
  description = "Secret Manager ID for GitHub token"
  value       = google_secret_manager_secret.github_token.secret_id
}

output "secret_api_key_id" {
  description = "Secret Manager ID for Coffee Maker API key"
  value       = google_secret_manager_secret.api_key.secret_id
}

# IAM outputs
output "service_account_email" {
  description = "Email of the Cloud Run service account"
  value       = google_service_account.code_developer.email
}

output "service_account_id" {
  description = "ID of the Cloud Run service account"
  value       = google_service_account.code_developer.id
}

# Monitoring outputs
output "log_sink_name" {
  description = "Name of the Cloud Logging sink"
  value       = var.enable_logging ? google_logging_project_sink.code_developer_logs[0].name : null
}

output "monitoring_dashboard_url" {
  description = "URL to the Cloud Monitoring dashboard"
  value       = var.enable_monitoring ? "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.code_developer_dashboard[0].id}?project=${var.project_id}" : null
}

# Connection strings and commands
output "api_url" {
  description = "Full API URL for the control API"
  value       = "${google_cloud_run_v2_service.code_developer.uri}/api"
}

output "health_check_url" {
  description = "Health check endpoint URL"
  value       = "${google_cloud_run_v2_service.code_developer.uri}/api/health"
}

# Useful commands
output "curl_health_check" {
  description = "Command to check service health"
  value       = "curl -H 'Authorization: Bearer $(gcloud auth print-identity-token)' ${google_cloud_run_v2_service.code_developer.uri}/api/health"
}

output "curl_daemon_status" {
  description = "Command to check daemon status"
  value       = "curl -H 'Authorization: Bearer $(gcloud auth print-identity-token)' ${google_cloud_run_v2_service.code_developer.uri}/api/daemon/status"
}

output "gcloud_logs_command" {
  description = "Command to stream Cloud Run logs"
  value       = "gcloud run services logs read ${google_cloud_run_v2_service.code_developer.name} --region=${var.region} --project=${var.project_id} --limit=50"
}

output "gcloud_deploy_command" {
  description = "Command to deploy a new version"
  value       = "gcloud run services update ${google_cloud_run_v2_service.code_developer.name} --region=${var.region} --project=${var.project_id} --image=NEW_IMAGE_URL"
}

# Configuration for project-manager CLI
output "gcp_config_yaml" {
  description = "Configuration for ~/.config/coffee-maker/gcp.yaml"
  value = yamlencode({
    gcp = {
      enabled    = true
      api_url    = google_cloud_run_v2_service.code_developer.uri
      project_id = var.project_id
      region     = var.region
      daemon = {
        auto_start            = true
        check_interval        = 30
        notify_on_completion  = true
      }
    }
  })
}

# Summary
output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    project_id      = var.project_id
    region          = var.region
    environment     = var.environment
    service_url     = google_cloud_run_v2_service.code_developer.uri
    service_name    = google_cloud_run_v2_service.code_developer.name
    storage_bucket  = google_storage_bucket.code_developer_storage.name
    database_active = var.enable_cloud_sql
  }
}
