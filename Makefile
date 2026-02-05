.PHONY: help install install-dev test lint format clean deploy synth bootstrap

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "Development environment ready!"

test:  ## Run tests
	python test_setup.py

lint:  ## Run linting checks
	@echo "Running flake8..."
	flake8 agents/ lambda/ scripts/ infrastructure/ --max-line-length=120 --exclude=__pycache__,.venv,venv || true
	@echo "Running pylint..."
	pylint agents/ lambda/ scripts/ infrastructure/ --disable=C0111,C0103,R0913 || true

format:  ## Format code with black
	black agents/ lambda/ scripts/ infrastructure/ --line-length=120

clean:  ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
	rm -rf cdk.out/ 2>/dev/null || true
	@echo "Cleaned build artifacts and cache"

synth:  ## Synthesize CDK stack
	cdk synth

bootstrap:  ## Bootstrap CDK (run once per account/region)
	cdk bootstrap

deploy:  ## Deploy CDK stack
	python scripts/deploy.py

destroy:  ## Destroy CDK stack
	cdk destroy

setup:  ## Run initial setup
	python scripts/setup.py

validate:  ## Validate all Python files
	@echo "Validating Python syntax..."
	@python -m py_compile agents/rag_agent.py
	@python -m py_compile lambda/rag_agent.py
	@python -m py_compile lambda/document_processor.py
	@python -m py_compile scripts/setup.py
	@python -m py_compile scripts/deploy.py
	@python -m py_compile infrastructure/rag_pipeline_stack.py
	@python -m py_compile app.py
	@echo "✅ All Python files are valid"

local-agent:  ## Run local RAG agent
	python agents/rag_agent.py

check: validate test lint  ## Run all checks (validate, test, lint)

.DEFAULT_GOAL := help
