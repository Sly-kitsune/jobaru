import argparse
import os
import json
import time
from src.parser import extract_text_from_file
from src.ollama_client import check_connection
from src.agent import process_job_application
from src.browser import BrowserEngine
from src.platforms.linkedin import LinkedIn

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def interactive_wizard():
    print("\n--- Jobaru Setup Wizard ---")
    config = load_config()
    
    if 'resume_path' not in config:
        path = input("Enter path to your resume (PDF/TXT): ").strip()
        if os.path.exists(path):
            config['resume_path'] = os.path.abspath(path)
            config['resume_text'] = extract_text_from_file(path)
        else:
            print("File not found. Exiting.")
            return None
            
    if 'job_role' not in config:
        config['job_role'] = input("Target Job Role (e.g., Python Developer): ").strip()
        
    if 'location' not in config:
        config['location'] = input("Target Location (e.g., Remote): ").strip()
    
    if 'model' not in config:
        config['model'] = "llama3"

    save_config(config)
    print("Configuration saved!\n")
    return config

def main():
    parser = argparse.ArgumentParser(description="Jobaru - AI Job Application Agent")
    parser.add_argument("--mode", choices=['draft', 'apply'], default='draft', help="Mode: 'draft' applications or 'apply' automatically")
    parser.add_argument("--resume", help="Path to resume file (PDF/TXT)")
    parser.add_argument("--model", default="mistral", help="Ollama model to use (default: mistral)")
    
    args = parser.parse_args()
    
    print("Jobaru - AI Job Application Agent")
    print("---------------------------------")
    
    if not check_connection():
        print("ERROR: Could not connect to Ollama. Make sure it is running at http://localhost:11434")
        return

    # Interactive Mode if no args provided or auto-mode selected
    if args.mode == 'apply':
        config = interactive_wizard()
        if not config: return
        
        print("\nLaunching Browser for Auto-Apply...")
        browser = BrowserEngine(headless=False) # Headless=False so user can see/login
        
        try:
            platform = LinkedIn(browser, config)
            platform.login()
            
            print(f"Searching for {config['job_role']} in {config['location']}...")
            jobs = platform.search_jobs(config['job_role'])
            print(f"Found {len(jobs)} jobs.")
            
            for job_url in jobs:
                print(f"\nProcessing: {job_url}")
                platform.apply_to_job(job_url)
                input("Press Enter to continue to next job (or Ctrl+C to stop)...")
                
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            browser.quit()
            
    else:
        # Legacy Draft Mode
        if not args.resume or not args.job:
            print("For 'draft' mode, please provide --resume and --job args.")
            return
            
        try:
            resume_text = extract_text_from_file(args.resume)
        except Exception as e:
            print(f"ERROR: {e}")
            return
            
        print(f"Processing application using model: {args.model}...")
        # (Existing logic...)
        result = process_job_application(resume_text, args.job, model=args.model)
        if "error" in result:
            print(f"Error: {result['error']}")
            print(f"Details: {result.get('details')}")
            return

        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join("applications", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Cover Letter
        cl_path = os.path.join(output_dir, "cover_letter.md")
        with open(cl_path, "w", encoding="utf-8") as f:
            f.write(result["materials"].get("cover_letter", ""))
            
        # Save Email Draft
        email_path = os.path.join(output_dir, "email_draft.txt")
        with open(email_path, "w", encoding="utf-8") as f:
            f.write(result["materials"].get("intro_email", ""))
            
        # Save Full Data
        json_path = os.path.join(output_dir, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        print(f"\nSuccess! Application materials saved to: {output_dir}")

if __name__ == "__main__":
    main()
