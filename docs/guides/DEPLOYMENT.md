# Deployment Guide

Complete guide for deploying the Strands RAG Pipeline to AWS.

## Prerequisites

Before deploying, ensure you have:

### 1. Required Tools
- **Python 3.8+** - Check with `python --version`
- **Node.js 14+** - Required for AWS CDK CLI
- **AWS CLI** - Configured with appropriate credentials
- **AWS CDK CLI** - Install with `npm install -g aws-cdk`

### 2. AWS Account Setup
- AWS account with appropriate permissions
- IAM user/role with permissions for:
  - Lambda functions
  - API Gateway
  - S3 buckets
  - DynamoDB tables
  - CloudFormation stacks
  - IAM roles

### 3. API Keys (Optional)
- Bedrock API key (recommended) or
- Anthropic/OpenAI/Google API keys

## Quick Start Deployment

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/mohammedfirdouss/strands-rag-pipeline.git
cd strands-rag-pipeline

# Run the setup script
python scripts/setup.py
```

The setup script will:
- Check Python version
- Install dependencies
- Install CDK CLI (if not present)
- Create `.env` file from template

### Step 2: Configure Environment

Edit the `.env` file with your API keys:

```bash
# For Bedrock (recommended)
AWS_BEDROCK_API_KEY=your_bedrock_api_key

# Or use other providers
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### Step 3: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or export credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

### Step 4: Bootstrap CDK (First Time Only)

```bash
# Bootstrap CDK in your account/region
cdk bootstrap aws://ACCOUNT-ID/REGION

# Or use the Makefile
make bootstrap
```

### Step 5: Deploy

```bash
# Option 1: Use the deployment script
python scripts/deploy.py

# Option 2: Use CDK directly
cdk deploy

# Option 3: Use the Makefile
make deploy
```

## Manual Deployment Steps

If you prefer more control, follow these detailed steps:

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 2. Test Locally (Optional)

```bash
# Test the setup
python test_setup.py

# Run the local agent
python agents/rag_agent.py
```

### 3. Synthesize CloudFormation Template

```bash
# Generate the CloudFormation template
cdk synth

# Review the generated template
cat cdk.out/StrandsRagPipelineStack.template.json | jq .
```

### 4. Deploy to AWS

```bash
# Deploy with manual approval
cdk deploy

# Deploy without approval prompts
cdk deploy --require-approval never

# Deploy with specific profile
cdk deploy --profile my-aws-profile
```

### 5. Verify Deployment

After deployment, CDK will output important information:

```
Outputs:
StrandsRagPipelineStack.ApiEndpoint = https://abc123.execute-api.us-west-2.amazonaws.com/prod/
StrandsRagPipelineStack.DocumentBucketName = strands-rag-documents-123456789-us-west-2
StrandsRagPipelineStack.ConversationTableName = strands-rag-conversations
StrandsRagPipelineStack.EmbeddingsTableName = strands-rag-embeddings
```

Save these outputs - you'll need them for testing!

## Testing the Deployment

### Test the Chat Endpoint

```bash
# Get your API endpoint from CDK outputs
API_ENDPOINT="https://your-api-id.execute-api.us-west-2.amazonaws.com/prod"

# Send a test message
curl -X POST $API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is RAG?",
    "conversation_id": "test-conversation"
  }'
```

Expected response:
```json
{
  "message": "RAG (Retrieval-Augmented Generation) is...",
  "conversation_id": "test-conversation",
  "timestamp": "2024-02-03T12:34:56.789Z",
  "status": "success"
}
```

### Test the Document Endpoint

```bash
curl -X POST $API_ENDPOINT/documents \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-doc-1",
    "content": "This is a test document."
  }'
```

## Monitoring Your Deployment

### CloudWatch Logs

View Lambda function logs:

```bash
# View document processor logs
aws logs tail /aws/lambda/strands-rag-document-processor --follow

# View RAG agent logs
aws logs tail /aws/lambda/strands-rag-agent --follow
```

### CloudWatch Metrics

Monitor in AWS Console:
1. Go to CloudWatch → Metrics
2. Select Lambda namespace
3. View metrics for:
   - Invocations
   - Errors
   - Duration
   - Throttles

### Cost Monitoring

1. Go to AWS Cost Explorer
2. Filter by service:
   - Lambda
   - API Gateway
   - DynamoDB
   - S3

## Updating the Stack

### Update Lambda Code

```bash
# After making changes to Lambda functions
cdk deploy

# CDK will automatically update the functions
```

### Update Infrastructure

```bash
# After modifying infrastructure/rag_pipeline_stack.py
cdk diff  # Review changes
cdk deploy  # Apply changes
```

## Troubleshooting

### Common Issues

**1. CDK Bootstrap Failed**
```bash
# Make sure you have the right permissions
aws sts get-caller-identity

# Try bootstrapping with explicit account/region
cdk bootstrap aws://123456789012/us-west-2
```

**2. Deployment Failed - Access Denied**
```bash
# Check IAM permissions
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

**3. Lambda Function Timeout**
```bash
# Check CloudWatch logs for errors
aws logs tail /aws/lambda/strands-rag-agent --follow

# Increase timeout in infrastructure/rag_pipeline_stack.py
# Then redeploy: cdk deploy
```

**4. API Gateway 403 Errors**
```bash
# Check API Gateway logs in CloudWatch
# Verify CORS configuration
# Check Lambda permissions
```

### Getting Help

Check the logs:
```bash
# Recent Lambda errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/strands-rag-agent \
  --filter-pattern "ERROR"
```

## Cleanup

To remove all resources:

```bash
# Option 1: Use CDK
cdk destroy

# Option 2: Use Makefile
make destroy

# Confirm when prompted
```

**Note:** S3 buckets with auto-delete will be emptied and removed. DynamoDB tables will be deleted. This action cannot be undone!

## Production Considerations

For production deployments:

1. **Remove auto-delete from S3 buckets**
   - Change `removal_policy` in `infrastructure/rag_pipeline_stack.py`

2. **Enable DynamoDB backups**
   - Already enabled (point-in-time recovery)

3. **Set up CloudWatch alarms**
   - Monitor Lambda errors
   - Monitor API Gateway 5xx errors
   - Set up SNS notifications

4. **Enable AWS X-Ray**
   - Add to Lambda functions for tracing

5. **Use Secrets Manager**
   - Store API keys securely
   - Don't use environment variables for sensitive data

6. **Set up proper IAM roles**
   - Follow principle of least privilege
   - Use separate roles for different functions

7. **Enable API Gateway throttling**
   - Protect against abuse
   - Set appropriate rate limits

8. **Use custom domain**
   - Set up Route53
   - Add SSL certificate

## Next Steps

After successful deployment:

1. Read the [API Documentation](../API.md)
2. Try the [examples](../../examples/README.md)
3. Configure monitoring and alerts
4. Set up CI/CD pipeline
5. Review security best practices

## Support

- Check [README.md](../../README.md)
- Review [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Open an issue on GitHub
