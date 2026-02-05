"""
Common utilities for Lambda functions.
Provides logging, validation, and helper functions.
"""

import os
import logging
from typing import Optional, Dict, Any


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging for Lambda functions.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set level from environment or parameter
    level = os.getenv("LOG_LEVEL", log_level).upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Create handler with formatting
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def validate_environment_variables(required_vars: list) -> Dict[str, str]:
    """Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        Dictionary of validated environment variables
        
    Raises:
        ValueError: If any required variables are missing
    """
    missing_vars = []
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            env_vars[var] = value
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return env_vars


def get_cors_headers() -> Dict[str, str]:
    """Get standard CORS headers for API responses.
    
    Returns:
        Dictionary of CORS headers
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }


def create_response(
    status_code: int,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a standardized API Gateway response.
    
    Args:
        status_code: HTTP status code
        body: Response body dictionary
        headers: Optional additional headers
        
    Returns:
        API Gateway response dictionary
    """
    import json
    
    response_headers = get_cors_headers()
    if headers:
        response_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps(body)
    }


def create_error_response(
    status_code: int,
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        error: Error type/category
        message: User-friendly error message
        details: Optional additional error details
        
    Returns:
        API Gateway error response dictionary
    """
    body = {
        'error': error,
        'message': message
    }
    
    if details:
        body['details'] = details
    
    return create_response(status_code, body)
