# Contributing to Sensei

Thank you for your interest in contributing to Sensei! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain code quality and documentation

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/devadigapratham/sensei.git
   cd sensei
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Coding Standards

### Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write comprehensive docstrings in Google style
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Type Hints

Always include type hints:

```python
def process_paper(paper: Paper, max_tokens: int = 3000) -> Optional[PaperAnalysis]:
    """
    Process a paper and extract limitations.
    
    Args:
        paper: Paper object to process
        max_tokens: Maximum tokens to process
        
    Returns:
        PaperAnalysis object or None if processing fails
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
class MyClass:
    """
    Brief description of the class.
    
    Longer description if needed, explaining the purpose and usage
    of the class.
    
    Attributes:
        attribute1: Description of attribute1
        attribute2: Description of attribute2
    """
```

### Prompts

- **CRITICAL**: All LLM prompts must be verbose and specific
- Never use placeholder prompts like "Analyze this"
- Include detailed instructions and examples
- Maintain the exact evaluation framework scoring rubric

## Testing

Before submitting a pull request:

1. Test your changes locally
2. Ensure all existing functionality still works
3. Check for linting errors:
   ```bash
   # If using pylint or similar
   pylint *.py
   ```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git commit -m "Add: description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

### PR Guidelines

- Write clear, descriptive commit messages
- Reference any related issues
- Include a description of what changed and why
- Ensure all tests pass (if applicable)
- Update documentation if needed

## Areas for Contribution

- **Bug Fixes**: Fix issues reported in the issue tracker
- **Documentation**: Improve README, docstrings, or add examples
- **Features**: Add new functionality (discuss in issues first)
- **Performance**: Optimize existing code
- **Testing**: Add unit tests or integration tests

## Questions?

Open an issue for questions, bug reports, or feature requests.

Thank you for contributing to Sensei!

