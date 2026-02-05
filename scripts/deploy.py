#!/usr/bin/env python3
"""
Deployment script for the Strands RAG Pipeline.
Validates and deploys the CDK infrastructure.
"""

import subprocess
import sys
import json
from pathlib import Path


from typing import Optional


def run_command(command: str, description: str, capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command and handle errors.
    
    Args:
        command: Shell command to execute
        description: Human-readable description of the command
        capture_output: Whether to capture command output
        
    Returns:
        CompletedProcess object if successful, None if failed
    """
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=capture_output, 
            text=True
        )
        if capture_output and result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        if capture_output and e.stderr:
            print(f"   Error: {e.stderr}")
        return None


def validate_prerequisites() -> bool:
    """Validate that all prerequisites are met.
    
    Returns:
        True if all prerequisites are met, False otherwise
    """
    print("🔍 Validating prerequisites...")
    
    # Check if CDK is installed
    result = run_command("cdk --version", "Checking CDK installation")
    if not result:
        print("❌ AWS CDK CLI is not installed. Run: npm install -g aws-cdk")
        return False
    
    # Check if AWS credentials are configured
    result = run_command("aws sts get-caller-identity", "Checking AWS credentials")
    if not result:
        print("❌ AWS credentials not configured. Run: aws configure")
        return False
    
    # Check if requirements are installed
    try:
        import aws_cdk
        print("✅ AWS CDK Python library found")
    except ImportError:
        print("❌ AWS CDK Python library not found. Run: pip install -r requirements.txt")
        return False
    
    return True


def synthesize_template() -> bool:
    """Synthesize the CDK template and validate it.
    
    Returns:
        True if synthesis succeeded, False otherwise
    """
    print("\n📋 Synthesizing CDK template...")
    
    result = run_command("cdk synth", "Synthesizing CloudFormation template")
    if not result:
        return False
    
    # Check if template was created
    template_path = Path("cdk.out/StrandsRagPipelineStack.template.json")
    if template_path.exists():
        print(f"✅ Template generated: {template_path}")
        
        # Show template size
        size = template_path.stat().st_size
        print(f"📊 Template size: {size:,} bytes")
        
        return True
    else:
        print("❌ Template file not found")
        return False


def deploy_stack() -> bool:
    """Deploy the CDK stack.
    
    Returns:
        True if deployment succeeded, False otherwise
    """
    print("\n🚀 Deploying infrastructure...")
    
    # Bootstrap CDK if needed
    print("🔧 Bootstrapping CDK (if needed)...")
    run_command("cdk bootstrap", "CDK Bootstrap", capture_output=False)
    
    # Deploy the stack
    result = run_command("cdk deploy --require-approval never", "Deploying stack", capture_output=False)
    if not result:
        return False
    
    print("\n✅ Deployment completed successfully!")
    
    # Try to get stack outputs
    try:
        result = run_command("aws cloudformation describe-stacks --stack-name StrandsRagPipelineStack", "Getting stack outputs")
        if result:
            stack_info = json.loads(result.stdout)
            outputs = stack_info['Stacks'][0].get('Outputs', [])
            
            if outputs:
                print("\n📋 Stack Outputs:")
                for output in outputs:
                    print(f"   {output['OutputKey']}: {output['OutputValue']}")
                    if 'Description' in output:
                        print(f"      {output['Description']}")
    except Exception as e:
        print(f"⚠️  Could not retrieve stack outputs: {e}")
    
    return True


def main() -> bool:
    """Main deployment function.
    
    Returns:
        True if deployment completed successfully, False otherwise
    """
    print("🚀 Strands RAG Pipeline Deployment")
    print("=" * 50)
    
    # Validate prerequisites
    if not validate_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    # Synthesize template
    if not synthesize_template():
        print("\n❌ Template synthesis failed. Please check your CDK code.")
        return False
    
    # Ask for confirmation
    print("\n🤔 Ready to deploy the infrastructure?")
    print("   This will create AWS resources that may incur costs.")
    
    response = input("   Continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Deployment cancelled.")
        return False
    
    # Deploy
    if not deploy_stack():
        print("\n❌ Deployment failed. Check the errors above.")
        return False
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the API endpoints")
    print("2. Upload documents to the S3 bucket")
    print("3. Try the chat functionality")
    print("\n💡 Use 'cdk destroy' to clean up resources when done.")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)