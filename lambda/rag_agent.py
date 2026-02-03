"""
RAG Agent Lambda Function
Main Strands agent for handling RAG queries with conversation context.
"""

import json
import boto3
import os
import re
from typing import Dict, Any
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
DOCUMENT_BUCKET = os.environ['DOCUMENT_BUCKET']
CONVERSATION_TABLE = os.environ['CONVERSATION_TABLE']
EMBEDDINGS_TABLE = os.environ['EMBEDDINGS_TABLE']

# Constants
MAX_MESSAGE_LENGTH = 10000
MAX_SANITIZE_LENGTH = 50000
MAX_CONVERSATION_ID_LENGTH = 256

# Initialize DynamoDB tables
conversation_table = dynamodb.Table(CONVERSATION_TABLE)
embeddings_table = dynamodb.Table(EMBEDDINGS_TABLE)


def sanitize_input(text: str, max_length: int = MAX_SANITIZE_LENGTH) -> str:
    """Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove any control characters except newlines
    # Note: Tabs are excluded for security - they can cause issues with downstream processing
    sanitized = ''.join(char for char in text if char.isprintable() or char == '\n')
    
    # Limit length to prevent resource exhaustion
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_conversation_id(conversation_id: str) -> bool:
    """Validate conversation ID format.
    
    Args:
        conversation_id: Conversation ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not conversation_id or not isinstance(conversation_id, str):
        return False
    
    # Allow alphanumeric, hyphens, and underscores only
    if not re.match(r'^[a-zA-Z0-9_-]+$', conversation_id):
        return False
    
    # Check length
    if len(conversation_id) > MAX_CONVERSATION_ID_LENGTH:
        return False
    
    return True


def create_rag_agent():
    """Create and configure the Strands RAG agent."""
    try:
        from strands import Agent, tool
        from strands_tools import calculator, python_repl, http_request
        
        @tool
        def search_documents(query: str) -> str:
            """Search through uploaded documents for relevant information.
            
            Args:
                query: The search query to find relevant documents
                
            Returns:
                Relevant document excerpts or information
            """
            # In a full implementation, this would:
            # 1. Create embeddings for the query
            # 2. Search vector database for similar documents
            # 3. Return relevant excerpts
            
            return f"Document search results for '{query}': This is a placeholder. In the full implementation, this would return relevant document excerpts based on semantic similarity."
        
        @tool
        def get_conversation_history(conversation_id: str) -> str:
            """Retrieve conversation history for context.
            
            Args:
                conversation_id: Unique identifier for the conversation
                
            Returns:
                Previous conversation messages
            """
            try:
                response = conversation_table.query(
                    KeyConditionExpression='conversation_id = :cid',
                    ExpressionAttributeValues={':cid': conversation_id},
                    ScanIndexForward=True,  # Sort by timestamp ascending
                    Limit=10  # Last 10 messages
                )
                
                messages = []
                for item in response.get('Items', []):
                    messages.append(f"{item['role']}: {item['content']}")
                
                return "\n".join(messages) if messages else "No previous conversation history."
                
            except Exception as e:
                logger.error(f"Error retrieving conversation history: {str(e)}")
                return "Error retrieving conversation history."
        
        # Create the agent with custom RAG tools
        agent = Agent(
            tools=[search_documents, get_conversation_history, calculator, python_repl, http_request],
            system_prompt="""You are an intelligent RAG (Retrieval-Augmented Generation) assistant built with Strands agents. 

Your capabilities include:
- Searching through uploaded documents to find relevant information
- Maintaining conversation context across multiple interactions
- Performing calculations and running Python code when needed
- Making HTTP requests to external APIs when necessary

When users ask questions:
1. First search through the available documents for relevant information
2. Use the conversation history to maintain context
3. Provide comprehensive, accurate answers based on the retrieved information
4. If you need to perform calculations or analysis, use the appropriate tools

Always be helpful, accurate, and cite your sources when referencing document content."""
        )
        
        return agent
        
    except ImportError as e:
        logger.error(f"Error importing Strands: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        return None


def save_conversation_message(conversation_id: str, role: str, content: str, timestamp: str) -> bool:
    """Save a conversation message to DynamoDB.
    
    Args:
        conversation_id: Unique identifier for the conversation
        role: Role of the message sender (user/assistant)
        content: Message content
        timestamp: ISO format timestamp
        
    Returns:
        True if save succeeded, False otherwise
    """
    try:
        conversation_table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'role': role,
                'content': content
            }
        )
        return True
    except Exception as e:
        logger.error(f"Error saving conversation message: {str(e)}", exc_info=True)
        return False


def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for RAG agent queries.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        conversation_id = body.get('conversation_id', 'default')
        
        # Sanitize inputs (includes stripping)
        user_message = sanitize_input(user_message)
        
        # Validate input
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Message is required and cannot be empty'
                })
            }
        
        # Validate message length
        if len(user_message) > MAX_MESSAGE_LENGTH:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Message is too long (max {MAX_MESSAGE_LENGTH} characters)'
                })
            }
        
        # Validate conversation_id format
        if not validate_conversation_id(conversation_id):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid conversation_id format (use alphanumeric, hyphens, and underscores only)'
                })
            }
        
        logger.info(f"Processing message from conversation {conversation_id}")
        
        # Create timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        
        # Save user message
        save_conversation_message(conversation_id, 'user', user_message, timestamp)
        
        # Create and use the RAG agent
        agent = create_rag_agent()
        
        if agent is None:
            # Fallback response if agent creation fails
            response_message = f"RAG Agent is initializing. Your message was: '{user_message}'. This is a basic response while the full Strands agent is being set up."
        else:
            # Use the agent to process the message
            response_message = agent(user_message)
        
        # Save agent response
        save_conversation_message(conversation_id, 'assistant', response_message, timestamp)
        
        response_body = {
            'message': response_message,
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'status': 'success'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid JSON in request body',
                'message': 'The request body must be valid JSON'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}", exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'An error occurred while processing your request. Please try again later.'
            })
        }