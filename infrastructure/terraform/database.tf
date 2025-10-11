# Cloud SQL (PostgreSQL) configuration for code_developer daemon

# Random password for database
resource "random_password" "db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

# Cloud SQL instance
resource "google_sql_database_instance" "code_developer" {
  count            = var.enable_cloud_sql ? 1 : 0
  name             = "${local.service_name}-db-${random_id.suffix.hex}"
  database_version = var.database_version
  region           = var.region
  project          = var.project_id

  settings {
    tier              = var.database_tier
    availability_type = var.database_ha_enabled ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.database_disk_size
    disk_autoresize   = true

    # Backup configuration
    backup_configuration {
      enabled                        = var.database_backup_enabled
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7

      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }

    # Maintenance window
    maintenance_window {
      day          = 7 # Sunday
      hour         = 3
      update_track = "stable"
    }

    # IP configuration
    ip_configuration {
      ipv4_enabled    = false # Private IP only
      private_network = google_compute_network.code_developer_vpc[0].id
      require_ssl     = true
    }

    # Database flags for optimization
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    database_flags {
      name  = "shared_buffers"
      value = "32768" # 256MB (in 8KB pages)
    }

    database_flags {
      name  = "work_mem"
      value = "4096" # 4MB (in KB)
    }

    database_flags {
      name  = "maintenance_work_mem"
      value = "65536" # 64MB (in KB)
    }

    # Insights configuration
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }

    # User labels
    user_labels = merge(local.common_labels, var.additional_labels)
  }

  # Deletion protection for production
  deletion_protection = var.environment == "prod" ? true : false

  depends_on = [
    google_project_service.required_apis,
    google_service_networking_connection.private_vpc_connection[0],
  ]
}

# Database
resource "google_sql_database" "code_developer_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "coffee_maker"
  instance = google_sql_database_instance.code_developer[0].name
  project  = var.project_id
}

# Database user
resource "google_sql_user" "code_developer" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "code_developer"
  instance = google_sql_database_instance.code_developer[0].name
  password = random_password.db_password[0].result
  project  = var.project_id
}

# Store database credentials in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = "code-developer-db-password"
  project   = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_secret_manager_secret_version" "db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.db_password[0].id
  secret_data = random_password.db_password[0].result
}

# IAM binding for service account to access database
resource "google_project_iam_member" "code_developer_cloudsql_client" {
  count   = var.enable_cloud_sql ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.code_developer.email}"
}

# VPC for private IP (required for Cloud SQL private IP)
resource "google_compute_network" "code_developer_vpc" {
  count                   = var.enable_cloud_sql ? 1 : 0
  name                    = "${local.service_name}-vpc"
  auto_create_subnetworks = true
  project                 = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Private VPC connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  count         = var.enable_cloud_sql ? 1 : 0
  name          = "${local.service_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.code_developer_vpc[0].id
  project       = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

resource "google_service_networking_connection" "private_vpc_connection" {
  count                   = var.enable_cloud_sql ? 1 : 0
  network                 = google_compute_network.code_developer_vpc[0].id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address[0].name]

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Outputs for database connection
output "database_connection_command" {
  description = "Command to connect to the database via Cloud SQL Proxy"
  value = var.enable_cloud_sql ? (
    "cloud-sql-proxy ${google_sql_database_instance.code_developer[0].connection_name}"
  ) : null
}
