"""
Example: AWS Lambda Handler Testing
Demonstrates how to test Lambda handlers locally.
"""

import json
import os
import sys

# Add parent directory to path
sys.path.append('..')


def test_document_processor():
    """Test the document processor Lambda handler."""
    print("=" * 60)
    print("Testing Document Processor Lambda")
    print("=" * 60)
    
    # Import the handler
    from lambda.document_processor import handler
    
    # Create a mock event
    event = {
        'body': json.dumps({
            'document_id': 'test-doc-123',
            'content': 'This is a test document for processing.'
        })
    }
    
    # Mock context
    class MockContext:
        function_name = 'document_processor'
        memory_limit_in_mb = 1024
        invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789:function:test'
        aws_request_id = 'test-request-id'
    
    print("\n1. Calling document processor handler...")
    
    try:
        # Note: This will fail without AWS credentials and DynamoDB tables
        # This is for demonstration purposes
        response = handler(event, MockContext())
        
        print(f"✅ Response received:")
        print(f"   Status Code: {response['statusCode']}")
        print(f"   Body: {response['body']}")
        
    except Exception as e:
        print(f"⚠️  Expected error (missing AWS resources): {str(e)}")
        print("   This is normal when running locally without AWS setup")


def test_rag_agent_handler():
    """Test the RAG agent Lambda handler."""
    print("\n" + "=" * 60)
    print("Testing RAG Agent Lambda")
    print("=" * 60)
    
    # Create a mock event
    event = {
        'body': json.dumps({
            'message': 'What is RAG?',
            'conversation_id': 'test-conversation-123'
        })
    }
    
    # Mock context
    class MockContext:
        function_name = 'rag_agent'
        memory_limit_in_mb = 2048
        invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789:function:test'
        aws_request_id = 'test-request-id'
    
    print("\n1. Calling RAG agent handler...")
    
    # Set mock environment variables
    os.environ['DOCUMENT_BUCKET'] = 'test-bucket'
    os.environ['CONVERSATION_TABLE'] = 'test-conversations'
    os.environ['EMBEDDINGS_TABLE'] = 'test-embeddings'
    
    try:
        from lambda.rag_agent import handler
        
        # Note: This will fail without AWS credentials and DynamoDB tables
        response = handler(event, MockContext())
        
        print(f"✅ Response received:")
        print(f"   Status Code: {response['statusCode']}")
        print(f"   Body: {response['body']}")
        
    except Exception as e:
        print(f"⚠️  Expected error (missing AWS resources): {str(e)}")
        print("   This is normal when running locally without AWS setup")


def main():
    """Run all Lambda handler tests."""
    print("\n" + "=" * 80)
    print("AWS Lambda Handler Testing Examples")
    print("=" * 80)
    print("\nNote: These tests demonstrate the structure but will fail without AWS resources.")
    print("Use this as a starting point for writing proper unit tests with mocks.\n")
    
    test_document_processor()
    test_rag_agent_handler()
    
    print("\n" + "=" * 80)
    print("Testing completed!")
    print("\n💡 For proper testing, use pytest with mocked AWS services (boto3 moto library)")
    print("=" * 80)


if __name__ == "__main__":
    main()
