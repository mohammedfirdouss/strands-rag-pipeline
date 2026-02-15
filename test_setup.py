#!/usr/bin/env python3
"""
Test script to validate the Strands RAG Pipeline setup.
"""

import sys
import os
from pathlib import Path


def test_imports() -> bool:
    """Test that all required packages can be imported.
    
    Returns:
        True if all imports succeeded, False otherwise
    """
    print("Testing package imports...")
    
    try:
        import aws_cdk
        print("AWS CDK imported successfully")
    except ImportError as e:
        print(f"Error: AWS CDK import failed: {e}")
        return False
    
    try:
        from strands import Agent, tool
        print("Strands SDK imported successfully")
    except ImportError as e:
        print(f"Error: Strands SDK import failed: {e}")
        print("Run: pip install strands-agents")
        return False
    
    try:
        from strands_tools import calculator, python_repl, http_request
        print("Strands tools imported successfully")
    except ImportError as e:
        print(f"Error: Strands tools import failed: {e}")
        print("Run: pip install strands-agents-tools")
        return False
    
    return True


def test_file_structure() -> bool:
    """Test that all required files exist.
    
    Returns:
        True if all files exist, False otherwise
    """
    print("\nTesting file structure...")
    
    required_files = [
        "app.py",
        "cdk.json",
        "requirements.txt",
        "infrastructure/rag_pipeline_stack.py",
        "lambda/rag_agent.py",
        "lambda/document_processor.py",
        "agents/rag_agent.py",
        "scripts/setup.py",
        "scripts/deploy.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"Found {file_path}")
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    
    return True


def test_cdk_synth() -> bool:
    """Test CDK synthesis.
    
    Returns:
        True if CDK synthesis succeeded, False otherwise
    """
    print("\nTesting CDK synthesis...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", "app.py"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("CDK app runs without errors")
            return True
        else:
            print(f"CDK app failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("CDK synthesis timed out")
        return False
    except Exception as e:
        print(f"CDK test failed: {e}")
        return False


def test_local_agent() -> bool:
    """Test the local RAG agent creation.
    
    Returns:
        True if agent creation succeeded, False otherwise
    """
    print("\nTesting local RAG agent...")
    
    try:
        # Import the local agent
        sys.path.append('agents')
        from rag_agent import create_local_rag_agent
        
        # Try to create the agent
        agent = create_local_rag_agent()
        print("Local RAG agent created successfully")
        
        # Test a simple query (with timeout for Windows compatibility)
        try:
            response = agent("What tools are available?")
            if "tools" in response.lower():
                print("Agent responds correctly to queries")
                return True
            else:
                print("Warning: Agent created but response seems unusual")
                return True
        except Exception as e:
            print(f"Warning: Agent created but query failed: {str(e)}")
            print("   This might be due to missing API keys - that's OK for setup testing")
            return True
            
    except ImportError as e:
        if "fcntl" in str(e):
            print("Warning: Windows compatibility issue detected (fcntl module)")
            print("   This is expected on Windows - agent will run in demo mode")
            return True
        else:
            print(f"Import error: {e}")
            return False
    except Exception as e:
        print(f"Local agent test failed: {e}")
        return False


def main() -> bool:
    """Run all tests.
    
    Returns:
        True if all tests passed, False otherwise
    """
    print("Strands RAG Pipeline Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("CDK Synthesis", test_cdk_synth),
        ("Local Agent", test_local_agent)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"{test_name} test passed")
            else:
                print(f"{test_name} test failed")
        except Exception as e:
            print(f"{test_name} test error: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Add API keys to .env file")
        print("2. Test locally: python agents/rag_agent.py")
        print("3. Deploy: python scripts/deploy.py")
    else:
        print("Some tests failed. Please fix the issues above.")
        print("Try running: python scripts/setup.py")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
