# Contributing to Strands RAG Pipeline

Thank you for your interest in contributing to the Strands RAG Pipeline project! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Node.js (for CDK CLI)
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/strands-rag-pipeline.git
   cd strands-rag-pipeline
   ```

2. **Run the setup script:**
   ```bash
   python scripts/setup.py
   ```

3. **Configure your environment:**
   - Copy `.env.example` to `.env`
   - Add your API keys and credentials

4. **Test your setup:**
   ```bash
   python test_setup.py
   ```

## 🔧 Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, readable code
   - Follow the existing code style
   - Add docstrings to functions and classes
   - Include type hints where appropriate

3. **Test your changes:**
   ```bash
   # Test locally
   python agents/rag_agent.py
   
   # Run setup tests
   python test_setup.py
   
   # Test CDK synthesis
   cdk synth
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Keep functions focused and concise
- Add docstrings to all public functions and classes

### Docstring Format

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when this is raised
    """
    pass
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import List, Dict, Optional

def process_data(items: List[str], config: Optional[Dict] = None) -> bool:
    """Process a list of items."""
    pass
```

## 🧪 Testing

### Local Testing

Before submitting a pull request:

1. Test the local RAG agent:
   ```bash
   python agents/rag_agent.py
   ```

2. Run the setup tests:
   ```bash
   python test_setup.py
   ```

3. Verify CDK synthesis works:
   ```bash
   cdk synth
   ```

### Writing Tests

When adding new features, consider adding tests to `test_setup.py` or creating new test files.

## 🏗️ Project Structure

```
strands-rag-pipeline/
├── agents/              # Local development agents
├── infrastructure/      # CDK infrastructure code
├── lambda/             # AWS Lambda functions
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── app.py              # CDK app entry point
├── test_setup.py       # Setup validation tests
└── requirements.txt    # Python dependencies
```

## 📋 Pull Request Guidelines

### Before Submitting

- Ensure your code follows the project's coding standards
- Test your changes thoroughly
- Update documentation if needed
- Keep your PR focused on a single feature or fix

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe how you tested your changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs

### Feature Requests

When requesting features, include:

- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Any relevant examples

## 💡 Areas for Contribution

We welcome contributions in these areas:

### Features
- Enhanced document processing capabilities
- Additional RAG tools and integrations
- Improved conversation management
- Advanced embedding strategies

### Documentation
- Tutorial improvements
- API documentation
- Architecture diagrams
- Use case examples

### Testing
- Unit tests
- Integration tests
- Performance benchmarks
- Test coverage improvements

### Infrastructure
- CDK improvements
- Security enhancements
- Cost optimization
- Monitoring and logging

## 🤝 Code Review Process

1. All PRs require review before merging
2. Address review comments promptly
3. Keep discussions focused and professional
4. Be open to feedback and suggestions

## 📞 Getting Help

If you need help or have questions:

- Check existing documentation
- Search for existing issues
- Create a new issue with the `question` label
- Reach out to maintainers

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Your contributions help make this project better for everyone. We appreciate your time and effort!
