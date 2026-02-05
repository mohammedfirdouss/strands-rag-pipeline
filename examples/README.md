# Examples Directory

This directory contains example scripts demonstrating how to use the Strands RAG Pipeline.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)
Demonstrates how to create and use a simple RAG agent locally.

```bash
cd examples
python basic_usage.py
```

**What it shows:**
- Creating a local RAG agent
- Running example queries
- Handling responses

### 2. Custom Tools (`custom_tools.py`)
Shows how to create and integrate custom tools with the RAG agent.

```bash
cd examples
python custom_tools.py
```

**What it shows:**
- Defining custom tools with the `@tool` decorator
- Creating agents with custom tools
- Using multiple tools together

### 3. Lambda Testing (`lambda_testing.py`)
Demonstrates how to test Lambda handlers locally (for development).

```bash
cd examples
python lambda_testing.py
```

**What it shows:**
- Testing Lambda handlers locally
- Mocking AWS context
- Understanding handler structure

## Prerequisites

Make sure you have:
1. Installed dependencies: `pip install -r ../requirements.txt`
2. Set up API keys in the `../.env` file
3. For Bedrock: AWS credentials configured

## Running Examples

```bash
# From the examples directory
cd examples

# Run basic usage
python basic_usage.py

# Run custom tools example
python custom_tools.py

# Run Lambda testing example
python lambda_testing.py
```

## Creating Your Own Examples

Feel free to create your own examples! Follow the pattern:

```python
"""
Example: Your Example Name
Description of what this example demonstrates.
"""

def main():
    print("Your example code here")
    return 0

if __name__ == "__main__":
    exit(main())
```

## Need Help?

- Check the main [README](../README.md)
- Review [CONTRIBUTING.md](../CONTRIBUTING.md)
- Open an issue on GitHub
