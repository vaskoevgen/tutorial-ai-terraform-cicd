# variables.tf

variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID to deploy resources into."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The default region for GCP resources."
}

# Add any base variables needed for your infrastructure here.
