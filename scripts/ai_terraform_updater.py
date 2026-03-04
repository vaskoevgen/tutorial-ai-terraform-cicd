import os
import sys
from google import genai
from google.genai import types

def main():
    # Ensure arguments are passed
    if len(sys.argv) < 2:
        print("Usage: python scripts/ai_terraform_updater.py '<developer_prompt>'")
        sys.exit(1)

    developer_prompt = sys.argv[1]

    # The GitHub Action steps will configure GCP Authentication (e.g., via Workload Identity 
    # or Service Account Key), so the SDK will automatically pick up the credentials from the environment.
    try:
        # Initialize the GenAI client (Vertex AI)
        client = genai.Client(vertexai=True)
    except Exception as e:
        print(f"Failed to initialize Vertex AI client. Ensure GCP authentication is set up. Error: {e}")
        sys.exit(1)

    # We will read the existing main.tf file to give the AI context.
    terraform_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "terraform")
    main_tf_path = os.path.join(terraform_dir, "main.tf")

    if not os.path.exists(main_tf_path):
        print(f"Error: {main_tf_path} not found.")
        sys.exit(1)

    with open(main_tf_path, 'r') as f:
        existing_terraform_code = f.read()

    # Define our system prompt instructing Gemini how to act.
    system_instruction = """
    You are an expert DevOps engineer who writes production-ready Terraform code for Google Cloud Platform (GCP).
    The user will provide you with an existing `main.tf` file and a REQUEST.
    Your goal is to output the FULL updated `main.tf` file fulfilling the request.

    Wait... ALWAYS return ONLY the raw Terraform code (no markdown code block syntax ````terraform`, ```` as wrappers). 
    Do NOT output any conversational text or explanations. 
    Just output the final file contents cleanly.
    """

    user_message = f"""
    EXISTING main.tf:
    {existing_terraform_code}

    REQUEST:
    {developer_prompt}
    """

    # We use a Gemini model capable of coding
    model_name = "gemini-2.5-pro" # or gemini-2.5-flash

    print(f"Sending prompt to Vertex AI ({model_name})...")

    response = client.models.generate_content(
        model=model_name,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2, # Keep hallucination low for infrastructure code
        )
    )

    new_terraform_code = response.text.strip()

    # Sometimes the AI still includes markdown ticks despite instructions; let's aggressively strip them.
    if new_terraform_code.startswith("```terraform"):
        new_terraform_code = new_terraform_code[12:]
    if new_terraform_code.startswith("```"):
        new_terraform_code = new_terraform_code[3:]
    if new_terraform_code.endswith("```"):
        new_terraform_code = new_terraform_code[:-3]
    
    new_terraform_code = new_terraform_code.strip()

    # Write the updated code back to the file
    with open(main_tf_path, 'w') as f:
        f.write(new_terraform_code)

    print("Successfully updated terraform/main.tf!")

if __name__ == "__main__":
    main()
