"""
RAG Agent Lambda Function
Main Strands agent for handling RAG queries with conversation context.
"""

import json
import boto3
import os
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

# Initialize DynamoDB tables
conversation_table = dynamodb.Table(CONVERSATION_TABLE)
embeddings_table = dynamodb.Table(EMBEDDINGS_TABLE)


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


def save_conversation_message(conversation_id: str, role: str, content: str, timestamp: str):
    """Save a conversation message to DynamoDB."""
    try:
        conversation_table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'role': role,
                'content': content
            }
        )
    except Exception as e:
        logger.error(f"Error saving conversation message: {str(e)}")


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
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Message is required'
                })
            }
        
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
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }