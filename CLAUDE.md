# WebToys Development Guide

This guide outlines the development workflow for the WebToys project.

## Development Workflow

### Setup

```bash
# Set up environment variables (requires 1Password CLI)
make setup

# Set up development environment with uv
make setup-dev
source .venv/bin/activate
```

### Build & Run Commands

```bash
# Run locally with hot-reload
make run-dev

# Build and run with Docker
make build
make run

# Run in detached mode
make run-detached

# Stop running containers
make stop
```

### Development Loop

```bash
# Run the fast development loop (format, lint, test-unit)
make dev-loop

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
# Format code
make format

# Lint code
make lint

# Run CI pipeline checks
make ci
```

### Deployment

```bash
# Deploy to development environment
make deploy-dev

# Deploy to production environment
make deploy-prod
```

## Code Style Guidelines

- **Python Version**: >=3.12
- **Imports**: Standard library first, then third-party, then local modules (alphabetical)
- **Variables**: Snake_case for variables, UPPERCASE for constants
- **Functions**: Use type annotations for parameters and return types
- **Error Handling**: Use appropriate try/except blocks with specific exceptions
- **Documentation**: Docstrings for all functions/classes using triple quotes
- **Security**: Be vigilant about sanitizing user inputs and setting proper CSP rules
- **Frontend JS**: ES6 standard with clear variable names and JSDoc comments
- **HTML/CSS**: Follow semantic HTML5 with class-based styling
- **Tests**: Follow AAA pattern (Arrange, Act, Assert) and use descriptive names

## Project Dependencies

- **Backend**: FastAPI, Uvicorn, Pydantic, Anthropic API
- **Development**: uv, ruff, mypy, pytest
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, Docker Compose

This project is a platform for creating and sharing interactive HTML5 Canvas experiments using AI.