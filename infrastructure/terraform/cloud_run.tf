# Cloud Run service configuration for code_developer daemon

# Cloud Run service
resource "google_cloud_run_v2_service" "code_developer" {
  name     = local.service_name
  location = var.region
  labels   = merge(local.common_labels, var.additional_labels)

  template {
    # Service account
    service_account = google_service_account.code_developer.email

    # Scaling configuration
    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }

    # Container configuration
    containers {
      image = var.container_image != "" ? var.container_image : "gcr.io/${var.project_id}/code-developer:latest"

      # Resource limits
      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
      }

      # Environment variables
      env {
        name  = "COFFEE_MAKER_MODE"
        value = "daemon"
      }

      env {
        name  = "COFFEE_MAKER_LOG_LEVEL"
        value = "INFO"
      }

      env {
        name  = "COFFEE_MAKER_AUTO_APPROVE"
        value = "true"
      }

      env {
        name  = "COFFEE_MAKER_CREATE_PRS"
        value = "true"
      }

      env {
        name  = "ROADMAP_PATH"
        value = "/workspace/docs/ROADMAP.md"
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.code_developer_storage.name
      }

      # Database connection (if enabled)
      dynamic "env" {
        for_each = var.enable_cloud_sql ? [1] : []
        content {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.code_developer[0].name}:${random_password.db_password[0].result}@/${google_sql_database.code_developer_db[0].name}?host=/cloudsql/${google_sql_database_instance.code_developer[0].connection_name}"
        }
      }

      # Secrets from Secret Manager
      env {
        name = "ANTHROPIC_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.anthropic_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GITHUB_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.github_token.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.api_key.secret_id
            version = "latest"
          }
        }
      }

      # Startup probe
      startup_probe {
        http_get {
          path = "/api/health"
          port = 8080
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 5
      }

      # Liveness probe
      liveness_probe {
        http_get {
          path = "/api/health"
          port = 8080
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }

      # Ports
      ports {
        container_port = 8080
        name           = "http1"
      }
    }

    # Cloud SQL connection (if enabled)
    dynamic "volumes" {
      for_each = var.enable_cloud_sql ? [1] : []
      content {
        name = "cloudsql"
        cloud_sql_instance {
          instances = [google_sql_database_instance.code_developer[0].connection_name]
        }
      }
    }

    # VPC connector (if enabled)
    dynamic "vpc_access" {
      for_each = var.enable_vpc_connector ? [1] : []
      content {
        connector = var.vpc_connector_name
        egress    = "ALL_TRAFFIC"
      }
    }

    # Timeout
    timeout = "${var.cloud_run_timeout}s"

    # Maximum concurrent requests per instance
    max_instance_request_concurrency = var.cloud_run_concurrency
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_secret_manager_secret_version.anthropic_api_key,
    google_secret_manager_secret_version.github_token,
    google_secret_manager_secret_version.api_key,
  ]
}

# IAM policy to allow public access (customize for production)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.environment == "dev" ? 1 : 0 # Only in dev, use IAM in production

  location = google_cloud_run_v2_service.code_developer.location
  name     = google_cloud_run_v2_service.code_developer.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM policy for authenticated access (production)
resource "google_cloud_run_v2_service_iam_member" "authenticated_access" {
  count = var.environment != "dev" ? 1 : 0

  location = google_cloud_run_v2_service.code_developer.location
  name     = google_cloud_run_v2_service.code_developer.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.code_developer.email}"
}

# Cloud Scheduler job to keep the service warm (prevent cold starts)
resource "google_cloud_scheduler_job" "keep_warm" {
  count = var.cloud_run_min_instances == 0 ? 1 : 0 # Only needed if scaling to zero

  name        = "${local.service_name}-keep-warm"
  description = "Keep Cloud Run service warm by pinging health endpoint"
  schedule    = "*/5 * * * *" # Every 5 minutes
  region      = var.region

  http_target {
    uri         = "${google_cloud_run_v2_service.code_developer.uri}/api/health"
    http_method = "GET"

    oidc_token {
      service_account_email = google_service_account.code_developer.email
    }
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}
