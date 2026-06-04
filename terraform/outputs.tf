output "cloud_run_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.api.uri
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.api.repository_id}"
}

output "cloud_run_service_account" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run.email
}

output "ci_service_account" {
  description = "CI/CD service account email"
  value       = google_service_account.ci.email
}

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions (set as GCP_WORKLOAD_IDENTITY_PROVIDER secret)"
  value       = var.github_repo != "" ? google_iam_workload_identity_pool_provider.github[0].name : "Set github_repo variable to enable"
}

output "db_password_secret_id" {
  description = "Secret Manager secret ID for database password"
  value       = google_secret_manager_secret.db_password.secret_id
  sensitive   = true
}

output "jwt_secret_id" {
  description = "Secret Manager secret ID for JWT secret"
  value       = google_secret_manager_secret.jwt_secret.secret_id
  sensitive   = true
}
