# Cloud Storage configuration for code_developer daemon

# Main storage bucket for project files and daemon state
resource "google_storage_bucket" "code_developer_storage" {
  name          = "${var.project_id}-code-developer-${random_id.suffix.hex}"
  location      = var.storage_location
  storage_class = var.storage_class
  project       = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  # Uniform bucket-level access
  uniform_bucket_level_access {
    enabled = true
  }

  # Versioning for critical files
  versioning {
    enabled = true
  }

  # Lifecycle rules
  lifecycle_rule {
    condition {
      age = var.storage_lifecycle_days
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = var.storage_lifecycle_days * 2
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  # Delete old versions after 30 days
  lifecycle_rule {
    condition {
      days_since_noncurrent_time = 30
      with_state                 = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  # CORS configuration (if needed for web access)
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

# IAM binding for service account to access storage
resource "google_storage_bucket_iam_member" "code_developer_storage_admin" {
  bucket = google_storage_bucket.code_developer_storage.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.code_developer.email}"
}

# Bucket for logs (separate from main storage)
resource "google_storage_bucket" "code_developer_logs" {
  name          = "${var.project_id}-code-developer-logs-${random_id.suffix.hex}"
  location      = var.storage_location
  storage_class = "STANDARD"
  project       = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  uniform_bucket_level_access {
    enabled = true
  }

  # Logs don't need versioning
  versioning {
    enabled = false
  }

  # Lifecycle: Delete logs after 90 days
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  # Move to coldline after 30 days
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

# IAM binding for logs bucket
resource "google_storage_bucket_iam_member" "code_developer_logs_writer" {
  bucket = google_storage_bucket.code_developer_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.code_developer.email}"
}

# Bucket for backups (checkpoints, database dumps)
resource "google_storage_bucket" "code_developer_backups" {
  name          = "${var.project_id}-code-developer-backups-${random_id.suffix.hex}"
  location      = var.storage_location
  storage_class = "NEARLINE" # Cost-effective for backups
  project       = var.project_id

  labels = merge(local.common_labels, var.additional_labels)

  uniform_bucket_level_access {
    enabled = true
  }

  versioning {
    enabled = true
  }

  # Lifecycle: Move to archive after 180 days
  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  # Delete backups older than 1 year
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [
    google_project_service.required_apis,
  ]
}

# IAM binding for backups bucket
resource "google_storage_bucket_iam_member" "code_developer_backups_admin" {
  bucket = google_storage_bucket.code_developer_backups.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.code_developer.email}"
}

# Create initial directory structure in main bucket
resource "google_storage_bucket_object" "workspace_readme" {
  name    = "workspace/README.md"
  bucket  = google_storage_bucket.code_developer_storage.name
  content = <<-EOT
    # Code Developer Workspace

    This directory contains the working copy of project files.

    ## Structure
    - `docs/roadmap/ROADMAP.md` - Project roadmap (synced from GitHub)
    - `coffee_maker/` - Application source code
    - `data/` - Daemon state and checkpoints

    ## Access
    - Service Account: ${google_service_account.code_developer.email}
    - Region: ${var.region}
    - Environment: ${var.environment}
  EOT
}

resource "google_storage_bucket_object" "checkpoints_readme" {
  name    = "checkpoints/README.md"
  bucket  = google_storage_bucket.code_developer_storage.name
  content = <<-EOT
    # Daemon Checkpoints

    This directory stores daemon state checkpoints for crash recovery.

    Checkpoints are automatically created:
    - Before starting each priority
    - After completing each priority
    - Every 30 minutes during long-running tasks
  EOT
}
