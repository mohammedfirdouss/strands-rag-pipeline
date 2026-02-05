# Troubleshooting Guide

Common issues and solutions for the Strands RAG Pipeline.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Deployment Issues](#deployment-issues)
- [Runtime Issues](#runtime-issues)
- [API Issues](#api-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)

## Installation Issues

### Python Version Error

**Problem:** `Python 3.8 or higher is required`

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.8+ if needed
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3.11

# On macOS:
brew install python@3.11
```

### Module Not Found Errors

**Problem:** `ModuleNotFoundError: No module named 'strands'`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# If still failing, try upgrading pip
pip install --upgrade pip
pip install -r requirements.txt
```

### CDK CLI Not Found

**Problem:** `command not found: cdk`

**Solution:**
```bash
# Install Node.js first
# Then install CDK CLI globally
npm install -g aws-cdk

# Verify installation
cdk --version
```

## Deployment Issues

### CDK Bootstrap Failed

**Problem:** `This stack uses assets, so the toolkit stack must be deployed`

**Solution:**
```bash
# Bootstrap CDK for your account/region
cdk bootstrap aws://ACCOUNT-ID/REGION

# Replace ACCOUNT-ID and REGION with your values
# Find them with:
aws sts get-caller-identity
```

### Deployment Access Denied

**Problem:** `User is not authorized to perform: cloudformation:CreateStack`

**Solution:**
1. Check your AWS credentials:
```bash
aws sts get-caller-identity
```

2. Ensure you have required permissions:
   - CloudFormation: Full access
   - Lambda: Create/update functions
   - API Gateway: Create/update APIs
   - S3: Create/manage buckets
   - DynamoDB: Create/manage tables
   - IAM: Create/manage roles

3. Ask your AWS administrator for appropriate permissions

### Stack Already Exists

**Problem:** `Stack already exists`

**Solution:**
```bash
# Update the existing stack
cdk deploy

# Or destroy and recreate
cdk destroy
cdk deploy
```

### Lambda Deployment Package Too Large

**Problem:** `Unzipped size must be smaller than X bytes`

**Solution:**
1. Use Lambda layers for large dependencies
2. Optimize package size:
```bash
# Remove unnecessary files
# Update lambda/requirements.txt to include only needed packages
```

## Runtime Issues

### Lambda Function Timeout

**Problem:** Lambda function times out before completing

**Solution:**
1. Check CloudWatch logs:
```bash
aws logs tail /aws/lambda/strands-rag-agent --follow
```

2. Increase timeout in `infrastructure/rag_pipeline_stack.py`:
```python
self.rag_agent = _lambda.Function(
    ...
    timeout=Duration.minutes(10),  # Increase from 5 to 10
)
```

3. Redeploy:
```bash
cdk deploy
```

### Environment Variables Not Set

**Problem:** `KeyError: 'DOCUMENT_BUCKET'`

**Solution:**
1. Check if variables are set in the stack:
```python
# In infrastructure/rag_pipeline_stack.py
environment={
    "DOCUMENT_BUCKET": self.document_bucket.bucket_name,
    ...
}
```

2. Verify after deployment:
```bash
aws lambda get-function-configuration \
  --function-name strands-rag-agent \
  --query 'Environment.Variables'
```

### DynamoDB Access Denied

**Problem:** `User is not authorized to perform: dynamodb:PutItem`

**Solution:**
1. Check Lambda execution role has permissions
2. Verify in `infrastructure/rag_pipeline_stack.py`:
```python
self.conversation_table.grant_read_write_data(self.lambda_role)
```

3. Redeploy if needed

### Memory Limit Exceeded

**Problem:** `Process exited before completing request`

**Solution:**
Increase memory in `infrastructure/rag_pipeline_stack.py`:
```python
self.rag_agent = _lambda.Function(
    ...
    memory_size=3008,  # Increase from 2048
)
```

## API Issues

### 403 Forbidden Error

**Problem:** `{"message":"Forbidden"}`

**Solutions:**

1. **CORS Issue:**
   - Check if browser is blocking due to CORS
   - Verify CORS is enabled in API Gateway

2. **IAM Authorization:**
```bash
# If using IAM auth, sign your requests
aws sts get-caller-identity
```

3. **API Key Missing:**
   - Check if API key is required
   - Include `x-api-key` header if needed

### 502 Bad Gateway Error

**Problem:** API Gateway returns 502

**Solution:**
1. Check Lambda function logs:
```bash
aws logs tail /aws/lambda/strands-rag-agent --follow
```

2. Common causes:
   - Lambda function crashing
   - Invalid response format from Lambda
   - Lambda timeout

3. Fix response format in Lambda:
```python
return {
    'statusCode': 200,
    'headers': {...},
    'body': json.dumps({...})
}
```

### 400 Bad Request

**Problem:** `{"error": "invalid_json", "message": "..."}`

**Solution:**
Ensure request body is valid JSON:
```bash
# Good
curl -X POST $API/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'

# Bad (missing quotes)
curl -X POST $API/chat \
  -d '{message:Hello}'
```

### Rate Limiting / Throttling

**Problem:** `Rate exceeded` or `TooManyRequestsException`

**Solution:**
1. Check Lambda concurrency limits
2. Implement exponential backoff:
```python
import time

def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)
```

## Performance Issues

### Slow Response Times

**Problem:** API responses are slow

**Solutions:**

1. **Check Lambda cold starts:**
   - Enable Lambda provisioned concurrency
   - Keep Lambda functions warm with ping

2. **Optimize code:**
   - Profile Lambda function
   - Reduce dependencies
   - Use caching where possible

3. **Check DynamoDB:**
   - Monitor read/write capacity
   - Add indexes if needed
   - Use batch operations

### High Costs

**Problem:** AWS bill is higher than expected

**Solution:**
1. Check CloudWatch metrics:
   - Lambda invocations
   - DynamoDB read/write units
   - S3 storage and requests
   - API Gateway requests

2. Optimize:
   - Set up CloudWatch alarms
   - Use reserved capacity for predictable loads
   - Enable S3 lifecycle policies
   - Clean up old data

3. Monitor with AWS Cost Explorer

## Security Issues

### API Keys Exposed

**Problem:** API keys committed to Git

**Solution:**
1. Immediately rotate all exposed keys
2. Remove from Git history:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

3. Use AWS Secrets Manager for production:
```python
import boto3

secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='my-api-key')
```

### Unauthorized Access

**Problem:** Suspicious activity in CloudWatch logs

**Solution:**
1. Review CloudWatch logs for unusual patterns
2. Check API Gateway access logs
3. Enable AWS CloudTrail for auditing
4. Implement rate limiting
5. Add IP whitelisting if needed

### Data Leakage

**Problem:** Error messages exposing sensitive data

**Solution:**
Already handled in the code:
- Generic error messages for clients
- Detailed errors only in logs
- No sensitive data in responses

## Debugging Tips

### Enable Debug Logging

Set environment variable:
```bash
# In .env file
LOG_LEVEL=DEBUG

# Or in Lambda environment
aws lambda update-function-configuration \
  --function-name strands-rag-agent \
  --environment Variables={LOG_LEVEL=DEBUG,...}
```

### Use CloudWatch Insights

Query logs efficiently:
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

### Test Locally

```bash
# Test Lambda functions locally
cd examples
python lambda_testing.py

# Test with specific inputs
python -c "
from lambda.rag_agent import handler
event = {'body': '{\"message\":\"test\"}'}
print(handler(event, None))
"
```

### Monitor with X-Ray

Enable X-Ray tracing for detailed insights:
```python
# In Lambda function
import aws_xray_sdk
from aws_xray_sdk.core import patch_all
patch_all()
```

## Getting Additional Help

### Check Logs

```bash
# Lambda logs
aws logs tail /aws/lambda/FUNCTION-NAME --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/FUNCTION-NAME \
  --filter-pattern "ERROR"
```

### Verify Configuration

```bash
# Check Lambda function
aws lambda get-function-configuration \
  --function-name strands-rag-agent

# Check API Gateway
aws apigateway get-rest-apis

# Check DynamoDB tables
aws dynamodb list-tables
```

### Contact Support

- Review [README.md](../../README.md)
- Check [API Documentation](../API.md)
- Review [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Open an issue on GitHub with:
  - Detailed error messages
  - Steps to reproduce
  - Environment details
  - Relevant logs
