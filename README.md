# Strands RAG Pipeline

A multimodal agentic RAG (Retrieval-Augmented Generation) pipeline built with AWS Strands Agents SDK and CDK infrastructure.

## 🚀 Overview

This project combines the power of **Strands Agents SDK** with **AWS cloud infrastructure** to create an intelligent RAG system that can:

- 🤖 **Intelligent Agents**: Multi-LLM support (Bedrock, Anthropic, OpenAI, Gemini, Meta Llama)
- 📚 **Document Processing**: Upload and process documents for semantic search
- 💬 **Conversational AI**: Maintain context across conversations
- ☁️ **Scalable Infrastructure**: AWS-native with S3, DynamoDB, Lambda, and API Gateway
- 🛠️ **Built-in Tools**: Calculator, Python REPL, HTTP requests, and custom tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend/API  │───▶│   API Gateway    │───▶│  Lambda Functions│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             │
                       │   Strands Agent  │◀────────────┘
                       │  (RAG + Tools)   │
                       └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
        │  S3 Bucket   │ │  DynamoDB   │ │  DynamoDB  │
        │ (Documents)  │ │(Conversations)│ │(Embeddings)│
        └──────────────┘ └─────────────┘ └────────────┘
```

## 🛠️ Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <your-repo>
cd strands-rag-pipeline

# Run setup script
python scripts/setup.py
```

### 2. Configure API Keys

Edit `.env` file with your API keys:

```bash
# For Bedrock (recommended for AWS integration)
AWS_BEDROCK_API_KEY=your_bedrock_api_key

# Or use other providers
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### 3. Test Locally

```bash
# Test the local RAG agent
python agents/rag_agent.py
```

### 4. Deploy Infrastructure

```bash
# Deploy to AWS
python scripts/deploy.py
```

## 🧪 Local Development

### Test the RAG Agent

```bash
python agents/rag_agent.py
```

Example interaction:
```
You: What is this project about?
🤖 Agent: This is the Strands RAG Pipeline project - a multimodal agentic RAG system...

You: Search for information about Strands
🤖 Agent: Found relevant information:
[doc1] Strands is an AI agent framework that supports multiple LLM providers...
```

### Available Tools

The agent comes with these built-in tools:
- 🔍 **Document Search**: Search through uploaded documents
- 📋 **Project Info**: Get project details and capabilities  
- 🧮 **Calculator**: Perform mathematical calculations
- 🐍 **Python REPL**: Execute Python code for analysis
- 🌐 **HTTP Requests**: Make external API calls

## ☁️ AWS Infrastructure

### Components

- **S3 Bucket**: Document storage with versioning and encryption
- **DynamoDB Tables**: 
  - Conversation history with timestamps
  - Document embeddings metadata
- **Lambda Functions**:
  - Document processor for uploads and embeddings
  - RAG agent for query processing
- **API Gateway**: RESTful endpoints for frontend integration

### API Endpoints

```
POST /documents  - Upload and process documents
POST /chat       - Send messages to RAG agent
```

### Deployment

```bash
# Synthesize CloudFormation template
cdk synth

# Deploy infrastructure
cdk deploy

# Clean up resources
cdk destroy
```

## 🔧 Configuration

### Model Providers

**Amazon Bedrock (Default)**
```python
# Uses Claude 4 Sonnet by default
agent = Agent(tools=[...])

# Or specify model
agent = Agent(
    model="anthropic.claude-sonnet-4-20250514-v1:0",
    tools=[...]
)
```

**Anthropic Direct**
```python
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-sonnet-4-20250514",
    max_tokens=1028
)
agent = Agent(model=model, tools=[...])
```

**OpenAI**
```python
from strands.models.openai import OpenAIModel

model = OpenAIModel(model_id="gpt-5-mini")
agent = Agent(model=model, tools=[...])
```

### Custom Tools

```python
from strands import tool

@tool
def custom_search(query: str) -> str:
    """Custom search functionality.
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    # Your implementation
    return f"Results for: {query}"

agent = Agent(tools=[custom_search, ...])
```

## 📚 Project Structure

```
strands-rag-pipeline/
├── agents/                 # Local development agents
│   └── rag_agent.py       # Main RAG agent for testing
├── infrastructure/         # CDK infrastructure code
│   └── rag_pipeline_stack.py
├── lambda/                # AWS Lambda functions
│   ├── document_processor.py
│   ├── rag_agent.py
│   └── requirements.txt
├── scripts/               # Utility scripts
│   ├── setup.py          # Environment setup
│   └── deploy.py         # Deployment script
├── app.py                # CDK app entry point
├── cdk.json              # CDK configuration
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```

## 🔍 Using the Powers

This project leverages two Kiro Powers:

### AWS Infrastructure as Code Power
- CDK best practices and documentation
- CloudFormation template validation
- Security compliance checking
- Deployment troubleshooting

### Strands Agents Power  
- Multi-LLM agent framework
- Tool integration and custom tools
- Conversation context management
- Documentation and examples

## 🚨 Troubleshooting

### Common Issues

**"Module 'strands' not found"**
```bash
pip install strands-agents strands-agents-tools
```

**"Access denied to model"**
- Enable model access in Bedrock console
- Check IAM permissions

**"AWS credentials not found"**
```bash
# For development
export AWS_BEDROCK_API_KEY=your_key

# For production
aws configure
```

**CDK deployment fails**
```bash
# Bootstrap CDK
cdk bootstrap

# Check AWS credentials
aws sts get-caller-identity
```

## 📖 Documentation

- [Strands Agents SDK](https://docs.strands.ai/)
- [AWS CDK Guide](https://docs.aws.amazon.com/cdk/)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `python agents/rag_agent.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
