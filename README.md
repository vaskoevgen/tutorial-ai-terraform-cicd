# 🤖 AI-Driven Terraform CI/CD Tutorial

Welcome to the **AI-Driven Infrastructure as Code** tutorial! 

This repository demonstrates how to build a fully automated CI/CD pipeline using **GitHub Actions**, **Terraform**, and **Google Cloud Platform (GCP)**—all powered by **Vertex AI (Gemini)**.

By the end of this tutorial, you will be able to type a plain-English prompt like `"Add a new Pub/Sub topic for order processing"` in a GitHub Issue, and an AI agent will automatically write the Terraform code and open a Pull Request for you to review and deploy!

---

## 🏗 Architecture Overview

1. **The Prompt**: A developer opens a GitHub Issue and types a comment starting with `/ai-terraform <prompt>`.
2. **AI Action**: A GitHub Action (`ai-prompter.yml`) triggers. It runs a Python script that asks **Google Gemini 2.5 Pro** (via Vertex AI) to read the existing `main.tf` and rewrite it to fulfill the prompt.
3. **Pull Request**: The AI creates a branch (e.g., `feature/ai-issue-1`) and opens a Pull Request back to `main`.
4. **Code Review & Plan**: Another GitHub Action (`terraform-plan.yml`) runs `terraform plan` and posts exactly what will happen into the PR comments. A human developer reviews the code.
5. **Dev Deployment**: When the PR is updated/created, `terraform apply` runs automatically into a `dev` workspace (isolated environment).
6. **Prod Deployment**: When the PR is merged to `main`, a final GitHub Action (`terraform-apply.yml`) runs. It pauses and waits for **Explicit Manual Approval** in the GitHub UI before applying to production.

---

## 📋 Prerequisites

Before using this repository, you must set up your Google Cloud environment and GitHub repository secrets.

### 1. Google Cloud Setup
You need a GCP Project with the following APIs enabled:
* Compute Engine API (or whichever resources you plan to deploy)
* **Vertex AI API** (Required for the Gemini Python script)
* Cloud Storage API (Required for Terraform remote state)

You must create a Google Cloud Storage Bucket for your Terraform State:
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_STATE_BUCKET_NAME
# Enable versioning (highly recommended for Terraform)
gsutil versioning set on gs://YOUR_STATE_BUCKET_NAME
```

### 2. Service Account & Authentication Configuration
The safest way to authenticate GitHub Actions with GCP is using **Workload Identity Federation**.

1. Create a Service Account in GCP designed for Terraform (e.g., `github-tf-deployer@your-project.iam.gserviceaccount.com`).
2. Grant this Service Account the `Owner` or `Editor` role on your project (so it can deploy resources), along with `Vertex AI User` so it can call the Gemini API.
3. Configure a Workload Identity Pool and Provider in GCP connected to your GitHub Repository.
4. Grant the Workload Identity Principal access to impersonate your Service Account.

*(If you are setting this up for a quick demo and want to take a shortcut, you can generate a JSON Service Account Key instead and modify the GitHub Actions workflows to use `credentials_json`.)*

### 3. GitHub Secrets Configure
Go to your Repository Settings -> **Secrets and variables** -> **Actions**. Add the following repository secrets:

* `GCP_PROJECT_ID`: Your Google Cloud Project ID.
* `GCP_TF_STATE_BUCKET`: The name of the GCS bucket you created (e.g., `my-company-tf-state`).
* `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full path to your Workload Identity Provider (e.g., `projects/12345/locations/global/workloadIdentityPools/my-pool/providers/my-provider`).
* `GCP_SERVICE_ACCOUNT`: The email of your GCP Service Account.

### 4. GitHub Environments Setup
To enforce the Manual Approval step for Production:
1. Go to Repository Settings -> **Environments**.
2. Click **New Environment** and name it `production`.
3. Check the box for **Required reviewers** and select yourself (or your team).

---

## 🚀 How to Use the Pipeline

### Option 1: Trigger via GitHub Issue (Recommended)
1. Open a new Issue in this repository.
2. In the description or as a comment, type:
   `/ai-terraform Create a Google Cloud Storage bucket named 'my-awesome-demo-bucket'`
3. Watch the Actions tab! The AI will run and open a Pull Request.
4. Review the PR, check the Terraform Plan comment, and merge it to deploy to Prod.

### Option 2: Trigger Manually
1. Go to the **Actions** tab.
2. Select **1. AI Terraform Prompter**.
3. Click **Run workflow**.
4. Type your prompt into the input box and click Run.

---

## 👨‍💻 Local Development

If you want to edit the AI Python script locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Authenticate your local machine to GCP (so Vertex AI can find credentials):
   ```bash
   gcloud auth application-default login
   ```
3. Run the script:
   ```bash
   python scripts/ai_terraform_updater.py "Add a compute engine instance"
   ```

## ⚠️ Security Warning
This repository is an educational skeleton. Allowing an AI to directly rewrite infrastructure code is highly experimental. **Always** maintain the explicit manual code review (PRs) and environment approval steps provided in these workflows. Do not give the Terraform service account more permissions than it strictly needs in a production environment.