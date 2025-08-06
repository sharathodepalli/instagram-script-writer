# Contributing to Instagram Script-Writer

Thank you for your interest in contributing to the Instagram Script-Writer project! We welcome contributions from the community.

## Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/instagram-script-writer.git
   cd instagram-script-writer
   ```

2. **Set up virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Install pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type annotations for all function parameters and return values
- Include docstrings for all public functions and classes
- Maximum line length: 88 characters (Black formatter default)
- Use meaningful variable and function names

## Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Use pytest for testing
- Mock external API calls (OpenAI, Pinecone) in tests
- Aim for good test coverage

Run tests:

```bash
pytest --maxfail=1 --disable-warnings -q
```

## Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run the test suite**

   ```bash
   pytest
   flake8 src tests
   black src tests
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Ensure CI checks pass

## Commit Message Guidelines

Use conventional commits format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring
- `style:` for formatting changes

## Code Review Process

1. All PRs require at least one review from a maintainer
2. Address all review comments before merging
3. Keep PRs focused and reasonably sized
4. Squash commits before merging if requested

## Issues and Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages/logs

## Questions?

Feel free to open an issue for questions about contributing or reach out to the maintainers.
