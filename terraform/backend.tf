# backend.tf

# Using GCS (Google Cloud Storage) for remote state management.
terraform {
  backend "gcs" {
    # The bucket name will be passed in via CLI or backend config during initialization, 
    # e.g.: terraform init -backend-config="bucket=<YOUR_GCS_BUCKET>" -backend-config="prefix=terraform/state"
    # This allows the same config to be dynamically mapped to dev/prod buckets if needed,
    # or you can use Terraform Workspaces to separate dev/prod environments within the same bucket.
  }
}
