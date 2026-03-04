# main.tf
# This file configures the Google Cloud provider

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---
# NOTE: The AI script (ai_terraform_updater.py) will inject new resources below this line
# based on the developer's prompts.
# ---
