"""JARVIS Pro - Contributing Guidelines"""

# Contributing to JARVIS Pro

Thank you for your interest in contributing to JARVIS Pro!

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Provide a clear description
3. Include steps to reproduce
4. Add relevant logs from `logs/` directory
5. Specify your Python version and OS

### Suggesting Features

1. Check if feature is already suggested
2. Provide clear use case
3. Explain expected behavior
4. Consider backward compatibility

### Code Contributions

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write tests for new features
5. Run `make lint` and `make format`
6. Run `make test` to ensure tests pass
7. Commit with clear message: `git commit -m 'Add amazing feature'`
8. Push to branch: `git push origin feature/amazing-feature`
9. Open Pull Request

## Code Standards

- **Python Version**: 3.12+
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all modules and functions
- **Testing**: Aim for >80% coverage
- **Code Style**: Follow PEP 8 (use `black` for formatting)
- **Linting**: Pass `flake8` checks

## Testing

```bash
# Run tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/test_jarvis.py::TestMemoryManager -v
```

## Code Review Process

1. Ensure all CI checks pass
2. Address review comments
3. Keep commits clean and organized
4. One approval required before merge

## Development Setup

```bash
# Clone and setup
git clone <your-fork>
cd jarvis
make dev

# Create .env file
cp .env.example .env
# Add your API keys

# Run with debug
make run-debug
```

## Pull Request Process

1. Update README if needed
2. Add tests for new features
3. Update CHANGELOG if applicable
4. Ensure backward compatibility
5. Follow commit message guidelines

## Commit Message Guidelines

```
type: subject

body

footer
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Code style
- **refactor**: Code refactoring
- **test**: Tests
- **chore**: Build/CI

### Example
```
feat: Add voice command learning

Implement ML-based voice command recognition
to reduce false positives.

Closes #123
```

## Recognition

All contributors will be acknowledged in:
- README.md contributors section
- Release notes
- GitHub contributors graph

## Questions?

- Check GitHub Discussions
- Open an issue with [QUESTION] prefix
- Review existing documentation

Thank you for contributing! 🙏
