# Strands RAG Pipeline - AWS Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Strands RAG Pipeline Architecture                      │
│                                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │   Client Apps   │    │   Development    │    │      AWS Cloud             │ │
│  │                 │    │   Environment    │    │                             │ │
│  │ • Web Frontend  │    │                  │    │                             │ │
│  │ • Mobile App    │◄──►│ • Local Agent    │◄──►│  ┌─────────────────────────┐ │ │
│  │ • API Clients   │    │ • Testing Tools  │    │  │     API Gateway         │ │ │
│  │ • Slack Bot     │    │ • CDK Deployment │    │  │   (REST Endpoints)      │ │ │
│  └─────────────────┘    └──────────────────┘    │  └─────────────────────────┘ │ │
│                                                 │              │               │ │
│                                                 │              ▼               │ │
│                                                 │  ┌─────────────────────────┐ │ │
│                                                 │  │    Lambda Functions     │ │ │
│                                                 │  │                         │ │ │
│                                                 │  │ ┌─────────────────────┐ │ │ │
│                                                 │  │ │ Document Processor  │ │ │ │
│                                                 │  │ │ • PDF/Text Extract  │ │ │ │
│                                                 │  │ │ • Embedding Gen     │ │ │ │
│                                                 │  │ │ • Metadata Storage  │ │ │ │
│                                                 │  │ └─────────────────────┘ │ │ │
│                                                 │  │                         │ │ │
│                                                 │  │ ┌─────────────────────┐ │ │ │
│                                                 │  │ │   RAG Agent         │ │ │ │
│                                                 │  │ │ • Strands Framework │ │ │ │
│                                                 │  │ │ • Multi-LLM Support │ │ │ │
│                                                 │  │ │ • Tool Integration  │ │ │ │
│                                                 │  │ │ • Context Memory    │ │ │ │
│                                                 │  │ └─────────────────────┘ │ │ │
│                                                 │  └─────────────────────────┘ │ │
│                                                 │              │               │ │
│                                                 │              ▼               │ │
│                                                 │  ┌─────────────────────────┐ │ │
│                                                 │  │      Storage Layer      │ │ │
│                                                 │  │                         │ │ │
│                                                 │  │ ┌─────────┐ ┌─────────┐ │ │ │
│                                                 │  │ │   S3    │ │DynamoDB │ │ │ │
│                                                 │  │ │Documents│ │Tables   │ │ │ │
│                                                 │  │ └─────────┘ └─────────┘ │ │ │
│                                                 │  └─────────────────────────┘ │ │
│                                                 │              │               │ │
│                                                 │              ▼               │ │
│                                                 │  ┌─────────────────────────┐ │ │
│                                                 │  │    External Services    │ │ │
│                                                 │  │                         │ │ │
│                                                 │  │ • Amazon Bedrock        │ │ │
│                                                 │  │ • Anthropic Claude      │ │ │
│                                                 │  │ • OpenAI GPT           │ │ │
│                                                 │  │ • Google Gemini        │ │ │
│                                                 │  └─────────────────────────┘ │ │
│                                                 └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Detailed Component Architecture

### 1. API Gateway Layer
```
┌─────────────────────────────────────────────────────────────┐
│                    Amazon API Gateway                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POST /documents                                            │
│  ├─ Content-Type: multipart/form-data                       │
│  ├─ Authentication: API Key / IAM                           │
│  └─ Target: Document Processor Lambda                       │
│                                                             │
│  POST /chat                                                 │
│  ├─ Content-Type: application/json                          │
│  ├─ Body: { message, conversation_id }                      │
│  └─ Target: RAG Agent Lambda                                │
│                                                             │
│  Features:                                                  │
│  • CORS enabled for web clients                             │
│  • Request/Response validation                              │
│  • Rate limiting and throttling                             │
│  • CloudWatch logging                                       │
└─────────────────────────────────────────────────────────────┘
```

### 2. Lambda Functions Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                  Document Processor Lambda                  │
├─────────────────────────────────────────────────────────────┤
│  Runtime: Python 3.11                                      │
│  Memory: 1024 MB                                            │
│  Timeout: 5 minutes                                         │
│                                                             │
│  Responsibilities:                                          │
│  ├─ Extract text from uploaded documents                    │
│  ├─ Generate embeddings using Bedrock                       │
│  ├─ Store documents in S3                                   │
│  ├─ Save metadata to DynamoDB                               │
│  └─ Handle multiple file formats (PDF, DOCX, TXT)          │
│                                                             │
│  Dependencies:                                              │
│  • boto3 (AWS SDK)                                          │
│  • PyPDF2 (PDF processing)                                  │
│  • langchain (Text processing)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    RAG Agent Lambda                         │
├─────────────────────────────────────────────────────────────┤
│  Runtime: Python 3.11                                      │
│  Memory: 2048 MB                                            │
│  Timeout: 5 minutes                                         │
│                                                             │
│  Core Components:                                           │
│  ├─ Strands Agent Framework                                 │
│  ├─ Multi-LLM Provider Support                              │
│  ├─ Built-in Tool Integration                               │
│  └─ Conversation Context Management                         │
│                                                             │
│  Available Tools:                                           │
│  ├─ search_documents() - Vector similarity search           │
│  ├─ get_conversation_history() - Context retrieval          │
│  ├─ calculator() - Mathematical operations                  │
│  ├─ python_repl() - Code execution                          │
│  └─ http_request() - External API calls                     │
│                                                             │
│  LLM Providers:                                             │
│  • Amazon Bedrock (Claude 4 Sonnet) - Default              │
│  • Anthropic Claude (Direct API)                           │
│  • OpenAI GPT (Direct API)                                 │
│  • Google Gemini (Direct API)                              │
│  • Meta Llama (Direct API)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 3. Storage Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Amazon S3 Bucket                      │
├─────────────────────────────────────────────────────────────┤
│  Bucket: strands-rag-documents-{account}-{region}          │
│                                                             │
│  Structure:                                                 │
│  ├─ /raw-documents/                                         │
│  │  ├─ {document-id}.pdf                                    │
│  │  ├─ {document-id}.docx                                   │
│  │  └─ {document-id}.txt                                    │
│  │                                                          │
│  ├─ /processed-text/                                        │
│  │  ├─ {document-id}.json                                   │
│  │  └─ {document-id}-chunks.json                            │
│  │                                                          │
│  └─ /embeddings/                                            │
│     ├─ {document-id}-vectors.json                           │
│     └─ {document-id}-metadata.json                          │
│                                                             │
│  Security:                                                  │
│  • Server-side encryption (SSE-S3)                          │
│  • Versioning enabled                                       │
│  • Block public access                                      │
│  • IAM-based access control                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    DynamoDB Tables                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Table: strands-rag-conversations                           │
│  ├─ Partition Key: conversation_id (String)                 │
│  ├─ Sort Key: timestamp (String)                            │
│  ├─ Attributes: role, content, metadata                     │
│  └─ Billing: Pay-per-request                                │
│                                                             │
│  Table: strands-rag-embeddings                              │
│  ├─ Partition Key: document_id (String)                     │
│  ├─ Attributes: s3_key, embedding_model, chunk_count       │
│  ├─ GSI: embedding_model-index                              │
│  └─ Billing: Pay-per-request                                │
│                                                             │
│  Features:                                                  │
│  • Point-in-time recovery                                   │
│  • Encryption at rest                                       │
│  • CloudWatch monitoring                                    │
│  • Auto-scaling (if needed)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 4. Security & IAM Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    IAM Roles & Policies                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Lambda Execution Role: RagLambdaRole                       │
│  ├─ AWSLambdaBasicExecutionRole (Managed)                   │
│  ├─ S3 Permissions:                                         │
│  │  ├─ s3:GetObject, s3:PutObject                           │
│  │  └─ s3:DeleteObject (document bucket)                    │
│  ├─ DynamoDB Permissions:                                   │
│  │  ├─ dynamodb:GetItem, dynamodb:PutItem                   │
│  │  ├─ dynamodb:Query, dynamodb:Scan                        │
│  │  └─ dynamodb:UpdateItem, dynamodb:DeleteItem             │
│  └─ Bedrock Permissions:                                    │
│     ├─ bedrock:InvokeModel                                  │
│     └─ bedrock:InvokeModelWithResponseStream                │
│                                                             │
│  API Gateway Permissions:                                   │
│  ├─ lambda:InvokeFunction (for Lambda integration)          │
│  └─ logs:CreateLogGroup, logs:CreateLogStream               │
│                                                             │
│  Security Best Practices:                                   │
│  • Least privilege access                                   │
│  • Resource-specific permissions                            │
│  • No wildcard (*) permissions                              │
│  • Regular permission audits                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

### Document Processing Flow
```
1. Client Upload
   ├─ POST /documents
   └─ Multipart file upload

2. API Gateway
   ├─ Request validation
   ├─ Authentication check
   └─ Route to Document Processor

3. Document Processor Lambda
   ├─ Extract text content
   ├─ Generate embeddings (Bedrock)
   ├─ Store original in S3
   ├─ Store processed text in S3
   ├─ Save metadata to DynamoDB
   └─ Return processing status

4. Storage
   ├─ S3: Raw + processed documents
   └─ DynamoDB: Document metadata
```

### RAG Query Flow
```
1. Client Query
   ├─ POST /chat
   └─ { message, conversation_id }

2. API Gateway
   ├─ Request validation
   └─ Route to RAG Agent

3. RAG Agent Lambda
   ├─ Load conversation history
   ├─ Initialize Strands Agent
   ├─ Process query with tools:
   │  ├─ search_documents()
   │  ├─ calculator()
   │  ├─ python_repl()
   │  └─ http_request()
   ├─ Generate response (LLM)
   ├─ Save conversation to DynamoDB
   └─ Return response

4. LLM Integration
   ├─ Amazon Bedrock (Primary)
   ├─ Anthropic Claude
   ├─ OpenAI GPT
   ├─ Google Gemini
   └─ Meta Llama
```

## 🌐 Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VPC (Optional)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Public Subnets (Multi-AZ)                                  │
│  ├─ API Gateway (Regional)                                  │
│  └─ NAT Gateways                                            │
│                                                             │
│  Private Subnets (Multi-AZ)                                 │
│  ├─ Lambda Functions                                        │
│  ├─ VPC Endpoints:                                          │
│  │  ├─ S3 Gateway Endpoint                                  │
│  │  ├─ DynamoDB Gateway Endpoint                            │
│  │  └─ Bedrock Interface Endpoint                           │
│  └─ Security Groups:                                        │
│     ├─ Lambda SG (HTTPS outbound)                           │
│     └─ VPC Endpoint SG (HTTPS inbound)                      │
│                                                             │
│  Network ACLs:                                              │
│  ├─ Allow HTTPS (443)                                       │
│  ├─ Allow HTTP (80) for redirects                           │
│  └─ Deny all other traffic                                  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                   CloudWatch Integration                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Metrics:                                                   │
│  ├─ API Gateway: Request count, latency, errors             │
│  ├─ Lambda: Duration, memory usage, errors                  │
│  ├─ DynamoDB: Read/write capacity, throttles                │
│  └─ S3: Request metrics, storage metrics                    │
│                                                             │
│  Logs:                                                      │
│  ├─ API Gateway access logs                                 │
│  ├─ Lambda function logs                                    │
│  ├─ Application logs (Strands agent)                        │
│  └─ Error logs and stack traces                             │
│                                                             │
│  Alarms:                                                    │
│  ├─ High error rates (>5%)                                  │
│  ├─ High latency (>30s)                                     │
│  ├─ Lambda timeout errors                                   │
│  └─ DynamoDB throttling                                     │
│                                                             │
│  Dashboards:                                                │
│  ├─ System health overview                                  │
│  ├─ Performance metrics                                     │
│  ├─ Cost tracking                                           │
│  └─ User activity patterns                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CDK Deployment Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Infrastructure as Code:                                    │
│  ├─ RagPipelineStack (Python CDK)                           │
│  ├─ Environment-specific configs                            │
│  ├─ Resource tagging strategy                               │
│  └─ Cross-stack references                                  │
│                                                             │
│  Deployment Pipeline:                                       │
│  ├─ 1. CDK Synth (CloudFormation)                           │
│  ├─ 2. Template validation                                  │
│  ├─ 3. Security compliance check                            │
│  ├─ 4. Deploy to staging                                    │
│  ├─ 5. Integration tests                                    │
│  ├─ 6. Deploy to production                                 │
│  └─ 7. Post-deployment validation                           │
│                                                             │
│  Environments:                                              │
│  ├─ Development: Single AZ, smaller instances               │
│  ├─ Staging: Production-like, limited scale                 │
│  └─ Production: Multi-AZ, auto-scaling                      │
└─────────────────────────────────────────────────────────────┘
```

## 💰 Cost Optimization Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cost Management                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Compute Costs:                                             │
│  ├─ Lambda: Pay-per-request, auto-scaling                   │
│  ├─ API Gateway: Pay-per-request                            │
│  └─ No idle compute costs                                   │
│                                                             │
│  Storage Costs:                                             │
│  ├─ S3: Standard tier for active documents                  │
│  ├─ S3: IA tier for older documents                         │
│  ├─ DynamoDB: On-demand billing                             │
│  └─ Lifecycle policies for cost optimization                │
│                                                             │
│  LLM Costs:                                                 │
│  ├─ Bedrock: Pay-per-token                                  │
│  ├─ Response caching for common queries                     │
│  ├─ Prompt optimization                                     │
│  └─ Model selection based on complexity                     │
│                                                             │
│  Monitoring:                                                │
│  ├─ Cost allocation tags                                    │
│  ├─ Budget alerts                                           │
│  ├─ Usage analytics                                         │
│  └─ Right-sizing recommendations                            │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Protection:                                           │
│  ├─ Encryption in transit (TLS 1.2+)                        │
│  ├─ Encryption at rest (S3, DynamoDB)                       │
│  ├─ Key management (AWS KMS)                                │
│  └─ Data classification and handling                        │
│                                                             │
│  Access Control:                                            │
│  ├─ IAM roles and policies                                  │
│  ├─ API Gateway authentication                              │
│  ├─ Resource-based policies                                 │
│  └─ Least privilege principle                               │
│                                                             │
│  Network Security:                                          │
│  ├─ VPC isolation (optional)                                │
│  ├─ Security groups                                         │
│  ├─ NACLs                                                   │
│  └─ VPC endpoints for AWS services                          │
│                                                             │
│  Compliance:                                                │
│  ├─ CloudTrail logging                                      │
│  ├─ Config rules                                            │
│  ├─ Security Hub integration                                │
│  └─ Regular security assessments                            │
└─────────────────────────────────────────────────────────────┘
```

This architecture provides a comprehensive, scalable, and secure foundation for the Strands RAG Pipeline, leveraging AWS best practices and the powerful Strands Agents SDK for intelligent document processing and conversational AI capabilities.