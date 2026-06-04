variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "parksmart"
}

variable "cloud_run_image" {
  description = "Container image URL for Cloud Run (set by CI/CD after first build)"
  type        = string
  default     = ""
}

variable "cloud_run_min_instances" {
  description = "Minimum Cloud Run instances"
  type        = number
  default     = 0
}

variable "cloud_run_max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 10
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 10
}

variable "cors_origins" {
  description = "Allowed CORS origins for the API"
  type        = list(string)
  default     = ["*"]
}

variable "github_repo" {
  description = "GitHub repository in format owner/repo for Workload Identity Federation"
  type        = string
  default     = ""
}
