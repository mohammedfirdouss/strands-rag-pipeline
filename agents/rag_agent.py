"""
Local RAG Agent for Development and Testing
A Strands agent for RAG queries that can be run locally.
"""

import os
import sys
from typing import List, Dict, Any

# Handle Windows compatibility
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Environment variables from .env file won't be loaded.")
    pass

def create_local_rag_agent():
    """Create a local RAG agent for development and testing."""
    from strands import Agent, tool
    from strands_tools import calculator, python_repl, http_request
    
    # Sample document store (in production, this would be a vector database)
    sample_documents = {
        "doc1": "Strands is an AI agent framework that supports multiple LLM providers including Bedrock, Anthropic, OpenAI, Gemini, and Meta Llama.",
        "doc2": "RAG (Retrieval-Augmented Generation) combines information retrieval with language generation to provide more accurate and contextual responses.",
        "doc3": "AWS CDK (Cloud Development Kit) allows you to define cloud infrastructure using familiar programming languages like Python, TypeScript, and Java.",
        "doc4": "Vector databases store high-dimensional vectors and enable efficient similarity search for applications like semantic search and recommendation systems."
    }
    
    @tool
    def search_documents(query: str) -> str:
        """Search through available documents for relevant information.
        
        Args:
            query: The search query to find relevant documents
            
        Returns:
            Relevant document excerpts
        """
        # Simple keyword-based search (in production, use semantic similarity)
        query_lower = query.lower()
        relevant_docs = []
        
        for doc_id, content in sample_documents.items():
            if any(word in content.lower() for word in query_lower.split()):
                relevant_docs.append(f"[{doc_id}] {content}")
        
        if relevant_docs:
            return "Found relevant information:\n" + "\n\n".join(relevant_docs)
        else:
            return f"No documents found matching '{query}'. Available topics include: Strands framework, RAG systems, AWS CDK, and vector databases."
    
    @tool
    def get_project_info() -> str:
        """Get information about the current Strands RAG pipeline project.
        
        Returns:
            Project information and capabilities
        """
        return """This is the Strands RAG Pipeline project - a multimodal agentic RAG system built with:

🤖 **Strands Agents SDK**: Multi-LLM agent framework with tool support
☁️ **AWS Infrastructure**: CDK-based cloud infrastructure with S3, DynamoDB, Lambda, and API Gateway
🔍 **RAG Capabilities**: Document search, embedding storage, and conversation context
🛠️ **Built-in Tools**: Calculator, Python REPL, HTTP requests, and custom document search

Current status: Development environment ready for testing and expansion."""
    
    @tool
    def list_available_tools() -> str:
        """List all available tools and their capabilities.
        
        Returns:
            Description of available tools
        """
        return """Available tools in this RAG agent:

🔍 **search_documents**: Search through uploaded documents for relevant information
📋 **get_project_info**: Get information about this Strands RAG pipeline project  
🧮 **calculator**: Perform mathematical calculations
🐍 **python_repl**: Execute Python code for data analysis and processing
🌐 **http_request**: Make HTTP requests to external APIs
📚 **list_available_tools**: Show this list of available tools

You can ask me to use any of these tools to help with your queries!"""
    
    # Create the agent
    agent = Agent(
        tools=[
            search_documents, 
            get_project_info, 
            list_available_tools,
            calculator, 
            python_repl, 
            http_request
        ],
        system_prompt="""You are an intelligent RAG assistant for the Strands RAG Pipeline project. You have access to:

1. **Document Search**: Search through available documents and knowledge base
2. **Project Information**: Details about the current Strands RAG pipeline implementation  
3. **Computational Tools**: Calculator and Python REPL for analysis
4. **External Access**: HTTP requests for additional information

**Your role:**
- Help users understand and work with the Strands RAG pipeline
- Search documents to provide accurate, source-based answers
- Perform calculations and data analysis when needed
- Explain the project architecture and capabilities
- Assist with development and testing

**Guidelines:**
- Always search documents first when users ask factual questions
- Cite your sources when referencing document content
- Use tools proactively to provide comprehensive answers
- Be helpful, accurate, and educational
- Explain technical concepts clearly

Ready to help with your RAG pipeline questions!"""
    )
    
    return agent


def demo_mode():
    """Run a simple demo mode without Strands agent."""
    print("📋 Demo Mode - Simulating RAG Pipeline")
    print("Available commands: 'project', 'search <query>', 'tools', 'quit'")
    
    sample_responses = {
        "project": """This is the Strands RAG Pipeline project - a multimodal agentic RAG system built with:

🤖 **Strands Agents SDK**: Multi-LLM agent framework with tool support
☁️ **AWS Infrastructure**: CDK-based cloud infrastructure with S3, DynamoDB, Lambda, and API Gateway
🔍 **RAG Capabilities**: Document search, embedding storage, and conversation context
🛠️ **Built-in Tools**: Calculator, Python REPL, HTTP requests, and custom document search""",
        
        "tools": """Available tools in this RAG agent:

🔍 **search_documents**: Search through uploaded documents for relevant information
📋 **get_project_info**: Get information about this Strands RAG pipeline project  
🧮 **calculator**: Perform mathematical calculations
🐍 **python_repl**: Execute Python code for data analysis and processing
🌐 **http_request**: Make HTTP requests to external APIs""",
        
        "strands": "Strands is an AI agent framework that supports multiple LLM providers including Bedrock, Anthropic, OpenAI, Gemini, and Meta Llama.",
        
        "rag": "RAG (Retrieval-Augmented Generation) combines information retrieval with language generation to provide more accurate and contextual responses.",
        
        "cdk": "AWS CDK (Cloud Development Kit) allows you to define cloud infrastructure using familiar programming languages like Python, TypeScript, and Java."
    }
    
    while True:
        try:
            user_input = input("\nDemo> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break
            
        if user_input in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
            
        if user_input == 'project':
            print("🤖 Demo:", sample_responses["project"])
        elif user_input == 'tools':
            print("🤖 Demo:", sample_responses["tools"])
        elif user_input.startswith('search '):
            query = user_input[7:]
            found = False
            for key, response in sample_responses.items():
                if key in query:
                    print(f"🤖 Demo: Found information about '{key}':")
                    print(response)
                    found = True
                    break
            if not found:
                print(f"🤖 Demo: No documents found matching '{query}'. Try: 'search strands', 'search rag', or 'search cdk'")
        else:
            print("🤖 Demo: Available commands: 'project', 'search <query>', 'tools', 'quit'")


def main():
    """Main function to run the local RAG agent interactively."""
    print("🤖 Strands RAG Pipeline Agent")
    print("=" * 50)
    print("Welcome to your local RAG agent! Type 'quit' to exit.\n")
    
    try:
        agent = create_local_rag_agent()
        print("✅ Agent initialized successfully!")
        print("💡 Try asking: 'What is this project about?' or 'Search for information about Strands'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                print("🤖 Agent: ", end="")
                response = agent(user_input)
                print(response)
                print()
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("💡 This might be due to missing API keys. Check your .env file.")
                print()
                
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("💡 Make sure you have:")
        print("   1. Installed requirements: pip install strands-agents strands-agents-tools")
        print("   2. Set up API keys in .env file")
        print("   3. For Bedrock: AWS_BEDROCK_API_KEY or AWS credentials")
        
        # Provide fallback demo mode
        print("\n🔧 Running in demo mode without Strands agent...")
        demo_mode()


if __name__ == "__main__":
    main()