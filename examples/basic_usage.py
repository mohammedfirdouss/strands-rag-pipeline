"""
Example: Basic RAG Agent Usage
Demonstrates how to create and use a simple RAG agent locally.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from the agents module
import sys
sys.path.append('..')
from agents.rag_agent import create_local_rag_agent


def main():
    """Run a basic RAG agent example."""
    print("=" * 60)
    print("Basic RAG Agent Example")
    print("=" * 60)
    
    try:
        # Create the agent
        print("\n1. Creating RAG agent...")
        agent = create_local_rag_agent()
        print("Agent created successfully!")
        
        # Example queries
        queries = [
            "What is this project about?",
            "Search for information about Strands",
            "What tools are available?",
        ]
        
        print("\n2. Running example queries...\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'=' * 60}")
            print(f"Query {i}: {query}")
            print("-" * 60)
            
            try:
                response = agent(query)
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        print(f"\n{'=' * 60}")
        print("Example completed successfully!")
        
    except Exception as e:
        print(f"Failed to create agent: {str(e)}")
        print("\nMake sure you have:")
        print("   1. Installed dependencies: pip install -r ../requirements.txt")
        print("   2. Set up API keys in ../.env file")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
