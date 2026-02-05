"""
Document Processor Lambda Function
Processes uploaded documents and creates embeddings for RAG pipeline.
"""

import json
import boto3
import os
from typing import Dict, Any

# Import utilities
from utils import setup_logging, validate_environment_variables, create_response, create_error_response

# Configure logging
logger = setup_logging()

# Validate and get environment variables
try:
    env_vars = validate_environment_variables([
        'DOCUMENT_BUCKET',
        'EMBEDDINGS_TABLE'
    ])
    DOCUMENT_BUCKET = env_vars['DOCUMENT_BUCKET']
    EMBEDDINGS_TABLE = env_vars['EMBEDDINGS_TABLE']
    
    # Initialize AWS clients
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    embeddings_table = dynamodb.Table(EMBEDDINGS_TABLE)
    
    logger.info(f"Initialized with bucket: {DOCUMENT_BUCKET}, table: {EMBEDDINGS_TABLE}")
    
except ValueError as e:
    logger.error(f"Environment validation failed: {str(e)}")
    # Set to None to handle in handler
    DOCUMENT_BUCKET = None
    EMBEDDINGS_TABLE = None
    s3_client = None
    dynamodb = None
    embeddings_table = None


def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for document processing.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Check environment variables
    if DOCUMENT_BUCKET is None or EMBEDDINGS_TABLE is None:
        logger.error("Environment variables not properly configured")
        return create_error_response(
            500,
            'configuration_error',
            'Service configuration error. Please contact support.'
        )
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate input
        if not body:
            return create_error_response(
                400,
                'invalid_request',
                'Request body is required'
            )
        
        logger.info(f"Processing document request: {body.get('document_id', 'unknown')}")
        
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
        
        return create_response(200, response_body)
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return create_error_response(
            400,
            'invalid_json',
            'The request body must be valid JSON'
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return create_error_response(
            500,
            'internal_error',
            'An error occurred while processing your document. Please try again later.'
        )