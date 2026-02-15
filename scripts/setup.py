#!/usr/bin/env python3
"""
Setup script for the Strands RAG Pipeline project.
Installs dependencies and sets up the development environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and handle errors.
    
    Args:
        command: Shell command to execute
        description: Human-readable description of the command
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible.
    
    Returns:
        True if Python version is 3.8 or higher, False otherwise
    """
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def setup_environment() -> bool:
    """Set up the development environment.
    
    Returns:
        True if setup succeeded, False otherwise
    """
    print("Setting up Strands RAG Pipeline Development Environment")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install main requirements
    if not run_command("pip install -r requirements.txt", "Installing main dependencies"):
        return False
    
    # Install Lambda requirements (for local testing)
    lambda_req_path = Path("lambda/requirements.txt")
    if lambda_req_path.exists():
        if not run_command(f"pip install -r {lambda_req_path}", "Installing Lambda dependencies"):
            return False
    
    # Install CDK CLI if not present
    try:
        subprocess.run("cdk --version", shell=True, check=True, capture_output=True)
        print("AWS CDK CLI already installed")
    except subprocess.CalledProcessError:
        print("Installing AWS CDK CLI...")
        if not run_command("npm install -g aws-cdk", "Installing AWS CDK CLI"):
            print("Warning: CDK CLI installation failed. You may need to install Node.js first.")
            print("   Visit: https://nodejs.org/")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("Created .env file - please add your API keys")
        except Exception as e:
            print(f"Failed to create .env file: {e}")
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Add your API keys to the .env file")
    print("2. Test the local agent: python agents/rag_agent.py")
    print("3. Deploy infrastructure: cdk deploy")
    print("\nFor Bedrock setup, visit: https://console.aws.amazon.com/bedrock")
    
    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
