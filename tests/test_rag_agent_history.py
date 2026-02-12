import importlib
import os

import pytest
from boto3.dynamodb.conditions import Equals

# Ensure required environment variables are present before importing the module
os.environ.setdefault("DOCUMENT_BUCKET", "test-bucket")
os.environ.setdefault("CONVERSATION_TABLE", "test-conversation-table")
os.environ.setdefault("EMBEDDINGS_TABLE", "test-embeddings-table")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

rag_agent = importlib.import_module("lambda.rag_agent")


class DummyTable:
    def __init__(self, items=None, exc: Exception | None = None):
        self.items = items or []
        self.exc = exc
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        if self.exc:
            raise self.exc
        return {"Items": self.items}


def test_fetch_conversation_history_formats_messages(monkeypatch):
    table = DummyTable(
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
    )
    monkeypatch.setattr(rag_agent, "conversation_table", table)

    result = rag_agent.fetch_conversation_history("conversation-1")

    assert "user: Hello" in result
    assert "assistant: Hi there" in result
    assert table.calls
    call = table.calls[0]
    assert isinstance(call["KeyConditionExpression"], Equals)
    assert call["ScanIndexForward"] is True
    assert call["Limit"] == 10


def test_fetch_conversation_history_handles_errors(monkeypatch):
    table = DummyTable(exc=Exception("boom"))
    monkeypatch.setattr(rag_agent, "conversation_table", table)

    result = rag_agent.fetch_conversation_history("conversation-2")

    assert result == "Error retrieving conversation history."
