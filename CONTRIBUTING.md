# Contributing to KeyPy

Thank you for your interest in contributing to KeyPy! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, KeyPy version)
- Any relevant logs or screenshots

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and benefits
- Any relevant examples or mockups

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** by running `pytest`
6. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/KeyPy.git
cd KeyPy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install dependencies
pip install -r requirements.txt
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=keypy --cov-report=html

# Run specific test file
pytest tests/test_database.py

# Run specific test
pytest tests/test_database.py::test_create_database
```

### Code Style

We follow PEP 8 style guidelines with some modifications:

```bash
# Format code with black
black src/

# Check style with flake8
flake8 src/
```

### Code Organization

```
KeyPy/
├── src/keypy/
│   ├── core/          # Core functionality (database, password gen)
│   ├── cli/           # Command-line interface
│   ├── gui/           # Graphical user interface
│   └── utils/         # Utility modules
├── tests/             # Test suite
├── docs/              # Documentation (future)
└── examples/          # Example scripts (future)
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and concise
- Prefer composition over inheritance

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    More detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests liberally

Example:
```
Add password strength indicator

- Implement entropy calculation
- Add visual strength meter
- Update tests

Fixes #123
```

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Ensure tests are isolated and independent
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Example:
```python
def test_generate_password_with_length():
    """Test password generation with custom length."""
    # Arrange
    generator = PasswordGenerator()
    length = 32
    
    # Act
    password = generator.generate(length=length)
    
    # Assert
    assert len(password) == length
    assert isinstance(password, str)
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Test both success and failure paths

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in docstrings
- Explain complex algorithms
- Document security considerations

### User Documentation

- Update README.md for major features
- Add examples to EXAMPLES.md
- Keep documentation in sync with code

## Security Considerations

KeyPy is a security-focused application. Please consider:

### Security Best Practices

1. **Never log sensitive data** (passwords, keys, etc.)
2. **Use secure random number generation**
3. **Follow cryptographic best practices**
4. **Validate and sanitize all inputs**
5. **Handle errors without leaking information**

### Reporting Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email the maintainers directly
3. Provide detailed information
4. Allow time for a fix before disclosure

## Feature Development

### Adding New Features

When adding major features:

1. **Open an issue first** to discuss the feature
2. **Get feedback** from maintainers
3. **Break into smaller PRs** if possible
4. **Document thoroughly**
5. **Add comprehensive tests**

### Feature Checklist

- [ ] Feature implementation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation
- [ ] Examples
- [ ] Backward compatibility check
- [ ] Security review

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- Browser integration
- Auto-type functionality
- Entry attachments
- Database import/export
- Password health reports

### Medium Priority
- Improved GUI features
- Additional password generators
- SSH agent integration
- HIBP (Have I Been Pwned) integration
- Keyboard shortcuts

### Documentation
- User guides
- Video tutorials
- API documentation
- Translations

### Testing
- Additional test cases
- Performance tests
- Security tests
- Cross-platform testing

## Release Process

(For maintainers)

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create and test release branch
4. Tag release
5. Build and publish to PyPI
6. Create GitHub release with notes

## Questions?

If you have questions:
- Check existing issues and discussions
- Open a new issue with the "question" label
- Reach out to maintainers

## License

By contributing to KeyPy, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to KeyPy! Your efforts help make password management more accessible and secure for everyone.
