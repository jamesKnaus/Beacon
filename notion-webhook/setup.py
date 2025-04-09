#!/usr/bin/env python
"""
Setup script for local testing of the Notion webhook server.

This script:
1. Creates a virtual environment if it doesn't exist
2. Installs the required dependencies
3. Provides instructions for testing locally
"""

import os
import sys
import subprocess
import platform

def run_command(cmd):
    """Run a command and print the output"""
    print(f"\n> {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Setting up Notion webhook server for local testing...")
    
    # Determine OS-specific commands
    is_windows = platform.system() == "Windows"
    python_cmd = "python" if is_windows else "python3"
    venv_dir = "venv"
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print("\nCreating virtual environment...")
        if not run_command([python_cmd, "-m", "venv", venv_dir]):
            print("Failed to create virtual environment. Please install venv with:")
            print("  pip install virtualenv")
            return False
    
    # Activate virtual environment
    if is_windows:
        activate_cmd = os.path.join(venv_dir, "Scripts", "activate")
    else:
        activate_cmd = f"source {os.path.join(venv_dir, 'bin', 'activate')}"
    
    # Install dependencies
    print("\nInstalling dependencies...")
    pip_cmd = [
        os.path.join(venv_dir, "Scripts" if is_windows else "bin", "pip"),
        "install", "-r", os.path.join("api", "requirements.txt")
    ]
    if not run_command(pip_cmd):
        print("Failed to install dependencies.")
        return False
    
    # Success message and next steps
    print("\n✅ Setup completed successfully!")
    print("\nTo test locally:")
    print(f"  1. {activate_cmd}")
    print("  2. Set environment variables:")
    if is_windows:
        print("     set NOTION_TOKEN=your_notion_token")
        print("     set NOTION_PAGE_ID=your_page_id")
        print("     set WEBHOOK_SECRET=your_webhook_secret")
    else:
        print("     export NOTION_TOKEN=your_notion_token")
        print("     export NOTION_PAGE_ID=your_page_id")
        print("     export WEBHOOK_SECRET=your_webhook_secret")
    print("  3. Run the Flask app:")
    if is_windows:
        print("     flask --app api.index run --port 5002")
    else:
        print("     FLASK_APP=api.index flask run --port 5002")
    print("\nFor public access (testing webhooks):")
    print("  - Install ngrok or localtunnel")
    print("  - Run: npx localtunnel --port 5002")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 