# WebToys Development Guide

This guide outlines the development workflow for the WebToys project.

## Development Workflow

### Setup

```bash
# Set up environment variables (requires 1Password CLI)
make setup

# Set up development environment with uv
make setup-dev
# No need to activate virtual environment with uv
```

### Build & Run Commands

```bash
# Run locally with hot-reload
make run-dev

# Build and run with Docker
make build        # Clean build (no cache)
make build-cached # Faster build with cache
make run          # Run application
make run-rebuild  # Rebuild and run with fresh images

# Run in detached mode
make run-detached

# Stop running containers
make stop
```

### Development Loop

```bash
# Run the fast development loop (format, lint, test)
make ci

# Individual commands
make format  # Format code with ruff
make lint    # Lint code with ruff and mypy
make test    # Run all tests
```

### Test Commands

```bash
# Run all tests locally with uv
make test

# Run all tests in Docker
make test-docker

# Run specific test suites
make test-unit
make test-integration

# Generate coverage report
make test-coverage
```

### Code Quality

```bash
# Format code with Ruff
make format

# Lint code with Ruff and mypy
make lint

# Fix auto-fixable linting errors
make lint-fix

# Run CI pipeline checks (same as development loop)
make ci
```

### Deployment

```bash
# Build optimized Docker image for deployment with date-tagged version
make build-prod

# Deploy to development environment
make deploy-dev

# Deploy to production environment
make deploy-prod

# Clean up Docker resources when done
make clean-docker
make clean-all    # Full cleanup (code and Docker)
```

## Code Style Guidelines

- **Python Version**: >=3.12
- **Linting & Formatting**: Ruff is used for both linting and formatting
- **Imports**: Standard library first, then third-party, then local modules (alphabetical), automatically sorted by Ruff
- **Variables**: Snake_case for variables, UPPERCASE for constants
- **Functions**: Use type annotations for parameters and return types
- **Error Handling**: Use appropriate try/except blocks with specific exceptions (never use bare `except:`)
- **Documentation**: Docstrings for all functions/classes using triple quotes
- **Security**: Be vigilant about sanitizing user inputs and setting proper CSP rules
- **Frontend JS**: ES6 standard with clear variable names and JSDoc comments
- **HTML/CSS**: Follow semantic HTML5 with class-based styling
- **Tests**: Follow AAA pattern (Arrange, Act, Assert) and use descriptive names

For full linting rules, see the Ruff configuration in `pyproject.toml`.

## Project Dependencies

- **Backend**: FastAPI, Uvicorn, Pydantic, Anthropic API
- **Development**: uv, ruff, mypy, pytest
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, Docker Compose

This project is a platform for creating and sharing interactive HTML5 Canvas experiments using AI.