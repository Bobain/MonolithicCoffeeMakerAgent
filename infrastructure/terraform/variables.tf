# Terraform variables for code_developer GCP deployment

# Project configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Project ID must be 6-30 characters, start with letter, contain only lowercase letters, numbers, and hyphens"
  }
}

variable "region" {
  description = "GCP Region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

# Cloud Run configuration
variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run (e.g., '1', '2', '4')"
  type        = string
  default     = "2"
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run (e.g., '512Mi', '1Gi', '2Gi')"
  type        = string
  default     = "2Gi"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 3
}

variable "cloud_run_min_instances" {
  description = "Minimum number of Cloud Run instances (0 = scale to zero)"
  type        = number
  default     = 1
}

variable "cloud_run_timeout" {
  description = "Request timeout for Cloud Run (in seconds)"
  type        = number
  default     = 3600 # 1 hour for long-running tasks
}

variable "cloud_run_concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 1 # Daemon should handle one task at a time
}

# Container configuration
variable "container_image" {
  description = "Container image URL (e.g., gcr.io/PROJECT_ID/code-developer:latest)"
  type        = string
  default     = ""
}

# Database configuration
variable "database_tier" {
  description = "Cloud SQL database tier"
  type        = string
  default     = "db-f1-micro"
}

variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_16"
}

variable "database_backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "database_ha_enabled" {
  description = "Enable high availability (regional)"
  type        = bool
  default     = false
}

variable "database_disk_size" {
  description = "Database disk size in GB"
  type        = number
  default     = 10
}

# Storage configuration
variable "storage_location" {
  description = "Cloud Storage bucket location"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Cloud Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)"
  type        = string
  default     = "STANDARD"
}

variable "storage_lifecycle_days" {
  description = "Days before moving to coldline storage (0 = disabled)"
  type        = number
  default     = 90
}

# Secret Manager configuration
variable "secret_replication_policy" {
  description = "Secret replication policy (automatic or user-managed)"
  type        = string
  default     = "automatic"
}

# API Keys and tokens (stored in Secret Manager)
variable "anthropic_api_key" {
  description = "Anthropic API key (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_token" {
  description = "GitHub personal access token (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "api_key" {
  description = "Coffee Maker API key for authentication (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

# Monitoring configuration
variable "alert_email" {
  description = "Email address for monitoring alerts"
  type        = string
  default     = ""
}

variable "alert_slack_webhook" {
  description = "Slack webhook URL for alerts"
  type        = string
  sensitive   = true
  default     = ""
}

# Cost control
variable "daily_cost_limit" {
  description = "Daily cost limit in USD (for alerts)"
  type        = number
  default     = 50.0
}

variable "monthly_cost_limit" {
  description = "Monthly cost limit in USD (for alerts)"
  type        = number
  default     = 1500.0
}

# Networking
variable "allowed_ingress_cidrs" {
  description = "List of CIDR ranges allowed to access the service"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Allow all by default, restrict in production
}

variable "enable_vpc_connector" {
  description = "Enable VPC connector for Cloud Run"
  type        = bool
  default     = false
}

variable "vpc_connector_name" {
  description = "VPC connector name (if enabled)"
  type        = string
  default     = ""
}

# Feature flags
variable "enable_cloud_sql" {
  description = "Enable Cloud SQL (disable to use SQLite for testing)"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring dashboards and alerts"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable structured logging to Cloud Logging"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable auto-scaling for Cloud Run"
  type        = bool
  default     = true
}

# Labels
variable "additional_labels" {
  description = "Additional labels to apply to all resources"
  type        = map(string)
  default     = {}
}
