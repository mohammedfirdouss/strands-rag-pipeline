#!/usr/bin/env python3
"""
Strands RAG Pipeline CDK App
A multimodal agentic RAG pipeline built with AWS Strands and CDK.
"""

import aws_cdk as cdk
from infrastructure.rag_pipeline_stack import RagPipelineStack

app = cdk.App()

# Create the RAG pipeline stack
RagPipelineStack(
    app, 
    "StrandsRagPipelineStack",
    description="Multimodal agentic RAG pipeline with Strands agents and AWS services"
)

app.synth()