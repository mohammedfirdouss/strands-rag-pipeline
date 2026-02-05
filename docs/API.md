# API Documentation

This document describes the REST API endpoints provided by the Strands RAG Pipeline.

## Base URL

After deployment, your API will be available at:
```
https://<api-id>.execute-api.<region>.amazonaws.com/prod/
```

You can find this URL in the CloudFormation outputs as `ApiEndpoint`.

## Authentication

Currently, the API uses AWS IAM authorization. For development, CORS is enabled for all origins.

## Endpoints

### 1. POST /documents

Upload and process documents for the RAG pipeline.

**Request:**
```http
POST /documents
Content-Type: application/json

{
  "document_id": "unique-doc-id",
  "content": "Document content to process",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name"
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Document processing endpoint ready",
  "bucket": "strands-rag-documents-...",
  "table": "strands-rag-embeddings",
  "status": "success"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request body or missing required fields
- `500 Internal Server Error` - Server-side processing error

### 2. POST /chat

Send a message to the RAG agent.

**Request:**
```http
POST /chat
Content-Type: application/json

{
  "message": "What is RAG?",
  "conversation_id": "optional-conversation-id"
}
```

**Parameters:**
- `message` (required): The user's message/query (max 10,000 characters)
- `conversation_id` (optional): Unique identifier for the conversation (alphanumeric, hyphens, and underscores only)

**Response (200 OK):**
```json
{
  "message": "RAG (Retrieval-Augmented Generation) combines...",
  "conversation_id": "conversation-123",
  "timestamp": "2024-02-03T12:34:56.789Z",
  "status": "success"
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "invalid_input",
  "message": "Message is required and cannot be empty"
}
```

```json
{
  "error": "message_too_long",
  "message": "Message is too long (max 10000 characters)"
}
```

```json
{
  "error": "invalid_conversation_id",
  "message": "Invalid conversation_id format (use alphanumeric, hyphens, and underscores only)"
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "An error occurred while processing your request. Please try again later."
}
```

## Example Usage

### Using cURL

**Send a chat message:**
```bash
curl -X POST https://your-api-id.execute-api.us-west-2.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this project about?",
    "conversation_id": "my-conversation"
  }'
```

**Upload a document:**
```bash
curl -X POST https://your-api-id.execute-api.us-west-2.amazonaws.com/prod/documents \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc-123",
    "content": "This is my document content..."
  }'
```

### Using Python

```python
import requests
import json

API_BASE_URL = "https://your-api-id.execute-api.us-west-2.amazonaws.com/prod"

def send_chat_message(message, conversation_id="default"):
    """Send a message to the RAG agent."""
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={
            "message": message,
            "conversation_id": conversation_id
        }
    )
    return response.json()

# Example usage
result = send_chat_message("What is RAG?")
print(f"Response: {result['message']}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const API_BASE_URL = 'https://your-api-id.execute-api.us-west-2.amazonaws.com/prod';

async function sendChatMessage(message, conversationId = 'default') {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      message: message,
      conversation_id: conversationId
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
sendChatMessage('What is RAG?')
  .then(result => console.log('Response:', result.message))
  .catch(error => console.error('Failed:', error));
```

## Rate Limits

Lambda functions have reserved concurrency:
- Document Processor: 10 concurrent executions
- RAG Agent: 20 concurrent executions

## Error Handling

All error responses follow this structure:
```json
{
  "error": "error_type",
  "message": "Human-readable error message"
}
```

Common error types:
- `invalid_input` - Invalid or missing required parameters
- `invalid_json` - Malformed JSON in request body
- `message_too_long` - Message exceeds maximum length
- `invalid_conversation_id` - Invalid conversation ID format
- `configuration_error` - Server configuration issue
- `internal_error` - Unexpected server error

## Best Practices

1. **Always validate input** before sending to the API
2. **Handle errors gracefully** with appropriate retry logic
3. **Use conversation IDs** to maintain context across multiple messages
4. **Keep messages under 10,000 characters** for optimal performance
5. **Monitor your usage** to stay within concurrency limits

## Support

For issues or questions:
- Check the [README](../README.md)
- Review [CONTRIBUTING.md](../CONTRIBUTING.md)
- Open an issue on GitHub
