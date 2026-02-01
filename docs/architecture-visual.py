#!/usr/bin/env python3
"""
AWS Architecture Diagram Generator for Strands RAG Pipeline
Creates a visual representation using diagrams library with AWS icons.

Install dependencies:
pip install diagrams
"""

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import Lambda
    from diagrams.aws.network import APIGateway, CloudFront
    from diagrams.aws.storage import S3
    from diagrams.aws.database import DynamodbTable
    from diagrams.aws.security import IAM
    from diagrams.aws.ml import Bedrock
    from diagrams.aws.management import Clo