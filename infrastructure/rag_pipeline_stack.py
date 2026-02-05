"""
RAG Pipeline Stack
Creates AWS infrastructure for a multimodal agentic RAG pipeline using Strands agents.
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    Tags,
    CfnOutput,
)
from constructs import Construct


class RagPipelineStack(Stack):
    """Stack for the Strands RAG Pipeline infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Add stack-level tags
        Tags.of(self).add("Project", "StrandsRAGPipeline")
        Tags.of(self).add("Environment", "Development")
        Tags.of(self).add("ManagedBy", "CDK")

        # S3 bucket for document storage
        self.document_bucket = s3.Bucket(
            self,
            "DocumentBucket",
            bucket_name=f"strands-rag-documents-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,  # For development
            auto_delete_objects=True,  # For development
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=Duration.days(30),
                    enabled=True,
                )
            ],
        )
        Tags.of(self.document_bucket).add("Purpose", "DocumentStorage")

        # DynamoDB table for conversation history and metadata
        self.conversation_table = dynamodb.Table(
            self,
            "ConversationTable",
            table_name="strands-rag-conversations",
            partition_key=dynamodb.Attribute(
                name="conversation_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development
            point_in_time_recovery=True,
            time_to_live_attribute="ttl",
        )
        Tags.of(self.conversation_table).add("Purpose", "ConversationHistory")

        # DynamoDB table for document embeddings metadata
        self.embeddings_table = dynamodb.Table(
            self,
            "EmbeddingsTable",
            table_name="strands-rag-embeddings",
            partition_key=dynamodb.Attribute(
                name="document_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development
            point_in_time_recovery=True,
        )
        Tags.of(self.embeddings_table).add("Purpose", "EmbeddingsMetadata")

        # IAM role for Lambda functions
        self.lambda_role = iam.Role(
            self,
            "RagLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="IAM role for Strands RAG Pipeline Lambda functions",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        Tags.of(self.lambda_role).add("Purpose", "LambdaExecution")

        # Grant permissions to Lambda role
        self.document_bucket.grant_read_write(self.lambda_role)
        self.conversation_table.grant_read_write_data(self.lambda_role)
        self.embeddings_table.grant_read_write_data(self.lambda_role)

        # Add Bedrock permissions
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        # Lambda function for document processing
        self.document_processor = _lambda.Function(
            self,
            "DocumentProcessor",
            function_name="strands-rag-document-processor",
            description="Processes uploaded documents and creates embeddings",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="document_processor.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "DOCUMENT_BUCKET": self.document_bucket.bucket_name,
                "EMBEDDINGS_TABLE": self.embeddings_table.table_name,
                "LOG_LEVEL": "INFO",
            },
            reserved_concurrent_executions=10,
        )
        Tags.of(self.document_processor).add("Purpose", "DocumentProcessing")

        # Lambda function for RAG agent
        self.rag_agent = _lambda.Function(
            self,
            "RagAgent",
            function_name="strands-rag-agent",
            description="Main Strands RAG agent for handling queries with conversation context",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="rag_agent.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=2048,
            environment={
                "DOCUMENT_BUCKET": self.document_bucket.bucket_name,
                "CONVERSATION_TABLE": self.conversation_table.table_name,
                "EMBEDDINGS_TABLE": self.embeddings_table.table_name,
                "LOG_LEVEL": "INFO",
            },
            reserved_concurrent_executions=20,
        )
        Tags.of(self.rag_agent).add("Purpose", "RAGAgent")

        # API Gateway for the RAG pipeline
        self.api = apigateway.RestApi(
            self,
            "RagPipelineApi",
            rest_api_name="Strands RAG Pipeline API",
            description="API for the multimodal agentic RAG pipeline",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # API endpoints
        documents_resource = self.api.root.add_resource("documents")
        documents_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.document_processor),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    },
                )
            ],
        )

        chat_resource = self.api.root.add_resource("chat")
        chat_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.rag_agent),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    },
                )
            ],
        )

        # Output important values
        self.add_outputs()

    def add_outputs(self):
        """Add CloudFormation outputs for important resources."""
        CfnOutput(
            self,
            "DocumentBucketName",
            value=self.document_bucket.bucket_name,
            description="S3 bucket for document storage",
            export_name="StrandsRAGDocumentBucket",
        )

        CfnOutput(
            self,
            "ApiEndpoint",
            value=self.api.url,
            description="API Gateway endpoint URL",
            export_name="StrandsRAGApiEndpoint",
        )

        CfnOutput(
            self,
            "ConversationTableName",
            value=self.conversation_table.table_name,
            description="DynamoDB table for conversation history",
            export_name="StrandsRAGConversationTable",
        )

        CfnOutput(
            self,
            "EmbeddingsTableName",
            value=self.embeddings_table.table_name,
            description="DynamoDB table for document embeddings metadata",
            export_name="StrandsRAGEmbeddingsTable",
        )
        
        CfnOutput(
            self,
            "DocumentProcessorArn",
            value=self.document_processor.function_arn,
            description="ARN of the document processor Lambda function",
            export_name="StrandsRAGDocumentProcessorArn",
        )
        
        CfnOutput(
            self,
            "RagAgentArn",
            value=self.rag_agent.function_arn,
            description="ARN of the RAG agent Lambda function",
            export_name="StrandsRAGAgentArn",
        )