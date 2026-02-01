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
)
from constructs import Construct


class RagPipelineStack(Stack):
    """Stack for the Strands RAG Pipeline infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
        )

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
        )

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
        )

        # IAM role for Lambda functions
        self.lambda_role = iam.Role(
            self,
            "RagLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

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
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="document_processor.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "DOCUMENT_BUCKET": self.document_bucket.bucket_name,
                "EMBEDDINGS_TABLE": self.embeddings_table.table_name,
            },
        )

        # Lambda function for RAG agent
        self.rag_agent = _lambda.Function(
            self,
            "RagAgent",
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
            },
        )

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
        from aws_cdk import CfnOutput

        CfnOutput(
            self,
            "DocumentBucketName",
            value=self.document_bucket.bucket_name,
            description="S3 bucket for document storage",
        )

        CfnOutput(
            self,
            "ApiEndpoint",
            value=self.api.url,
            description="API Gateway endpoint URL",
        )

        CfnOutput(
            self,
            "ConversationTableName",
            value=self.conversation_table.table_name,
            description="DynamoDB table for conversation history",
        )

        CfnOutput(
            self,
            "EmbeddingsTableName",
            value=self.embeddings_table.table_name,
            description="DynamoDB table for document embeddings metadata",
        )