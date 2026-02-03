"""
Document Processor Lambda Function
Processes uploaded documents and creates embeddings for RAG pipeline.
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
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DOCUMENT_BUCKET = os.environ['DOCUMENT_BUCKET']
EMBEDDINGS_TABLE = os.environ['EMBEDDINGS_TABLE']

# Initialize DynamoDB table
embeddings_table = dynamodb.Table(EMBEDDINGS_TABLE)


def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for document processing.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate input
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Request body is required'
                })
            }
        
        logger.info(f"Processing document request: {body}")
        
        # For now, return a simple response
        # In a full implementation, this would:
        # 1. Extract text from uploaded documents
        # 2. Create embeddings using Bedrock
        # 3. Store embeddings metadata in DynamoDB
        # 4. Store processed documents in S3
        
        response_body = {
            'message': 'Document processing endpoint ready',
            'bucket': DOCUMENT_BUCKET,
            'table': EMBEDDINGS_TABLE,
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
                'message': str(e)
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'An error occurred while processing your document. Please try again later.'
            })
        }