# Main Terraform configuration for code_developer GCP deployment
# Orchestrates all infrastructure components

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Optional: Use GCS backend for state management
  # Uncomment and configure after initial deployment
  # backend "gcs" {
  #   bucket = "code-developer-terraform-state"
  #   prefix = "terraform/state"
  # }
}

# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",              # Cloud Run
    "storage.googleapis.com",          # Cloud Storage
    "sqladmin.googleapis.com",         # Cloud SQL
    "secretmanager.googleapis.com",    # Secret Manager
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",          # Cloud Logging
    "monitoring.googleapis.com",       # Cloud Monitoring
    "cloudbuild.googleapis.com",       # Cloud Build (for CI/CD)
    "artifactregistry.googleapis.com", # Artifact Registry
  ])

  service            = each.key
  disable_on_destroy = false
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# Project-level IAM configurations
locals {
  project_id = var.project_id
  region     = var.region
  zone       = var.zone

  # Common labels for all resources
  common_labels = {
    project     = "code-developer"
    environment = var.environment
    managed_by  = "terraform"
    team        = "autonomous-ai"
  }

  # Service name
  service_name = "code-developer-${var.environment}"
}

# Outputs to be used by other modules
output "project_id" {
  description = "GCP Project ID"
  value       = local.project_id
}

output "region" {
  description = "GCP Region"
  value       = local.region
}

output "service_name" {
  description = "Code Developer service name"
  value       = local.service_name
}

output "common_labels" {
  description = "Common labels for all resources"
  value       = local.common_labels
}
