# Networking configuration for code_developer daemon

# VPC connector for Cloud Run (if not using Cloud SQL)
resource "google_vpc_access_connector" "code_developer" {
  count   = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name    = "${local.service_name}-vpc-connector"
  region  = var.region
  project = var.project_id

  subnet {
    name       = google_compute_subnetwork.vpc_connector_subnet[0].name
    project_id = var.project_id
  }

  machine_type  = "e2-micro"
  min_instances = 2
  max_instances = 3

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Subnet for VPC connector
resource "google_compute_subnetwork" "vpc_connector_subnet" {
  count         = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name          = "${local.service_name}-vpc-connector-subnet"
  ip_cidr_range = "10.8.0.0/28"
  region        = var.region
  network       = google_compute_network.vpc[0].id
  project       = var.project_id
}

# VPC network (only if not using Cloud SQL VPC)
resource "google_compute_network" "vpc" {
  count                   = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name                    = "${local.service_name}-network"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [
    google_project_service.required_apis,
  ]
}

# Firewall rules for VPC
resource "google_compute_firewall" "allow_internal" {
  count   = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name    = "${local.service_name}-allow-internal"
  network = google_compute_network.vpc[0].name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.8.0.0/28"]
}

# Firewall rule for health checks
resource "google_compute_firewall" "allow_health_check" {
  count   = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name    = "${local.service_name}-allow-health-check"
  network = google_compute_network.vpc[0].name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = [
    "35.191.0.0/16",  # Google Cloud Load Balancer health checks
    "130.211.0.0/22", # Google Cloud Load Balancer health checks
  ]

  target_tags = ["code-developer"]
}

# Firewall rule for SSH (debugging only, remove in production)
resource "google_compute_firewall" "allow_ssh" {
  count   = var.environment == "dev" && var.enable_vpc_connector ? 1 : 0
  name    = "${local.service_name}-allow-ssh"
  network = google_compute_network.vpc[0].name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.allowed_ingress_cidrs

  target_tags = ["code-developer"]
}

# Cloud NAT for outbound internet access (if using VPC)
resource "google_compute_router" "code_developer" {
  count   = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name    = "${local.service_name}-router"
  region  = var.region
  network = google_compute_network.vpc[0].id
  project = var.project_id
}

resource "google_compute_router_nat" "code_developer" {
  count  = var.enable_vpc_connector && !var.enable_cloud_sql ? 1 : 0
  name   = "${local.service_name}-nat"
  router = google_compute_router.code_developer[0].name
  region = var.region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Global load balancer (optional, for production)
# Uncomment if you need a custom domain with SSL
# resource "google_compute_global_address" "code_developer" {
#   name    = "${local.service_name}-ip"
#   project = var.project_id
# }

# resource "google_compute_managed_ssl_certificate" "code_developer" {
#   name    = "${local.service_name}-ssl"
#   project = var.project_id
#
#   managed {
#     domains = ["code-developer.yourdomain.com"]
#   }
# }

# Outputs
output "vpc_connector_name" {
  description = "Name of the VPC connector"
  value       = var.enable_vpc_connector && !var.enable_cloud_sql ? google_vpc_access_connector.code_developer[0].name : null
}

output "vpc_connector_id" {
  description = "ID of the VPC connector"
  value       = var.enable_vpc_connector && !var.enable_cloud_sql ? google_vpc_access_connector.code_developer[0].id : null
}
