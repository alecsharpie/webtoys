# WebToys

Create and share interactive HTML5 Canvas experiments with AI.

## About

WebToys is a platform that allows you to create interactive canvas-based web "toys" by simply describing what you want. Using AI, WebToys generates the code for you, runs it in a secure sandbox, and provides a shareable link to your creation.

## Features

- **AI-powered creation**: Just describe what you want, and AI will generate the code
- **Secure sandbox**: All WebToys run in a secure environment
- **Shareable links**: Share your creations with a simple URL
- **No coding required**: Create interactive web experiments without writing code

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Anthropic API key](https://www.anthropic.com/) for Claude AI
- [1Password CLI](https://1password.com/downloads/command-line/) (for dev setup)

### Quick Start with Docker

```bash
# Set up your environment (requires 1Password CLI)
make setup

# Build and run the application
make build
make run

# Application will be available at http://localhost:8000
```

### Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/webtoys.git
cd webtoys
```

2. **Set up environment and dependencies**

```bash
# Set up API keys and environment variables
make setup

# Set up development environment
make setup-dev
source .venv/bin/activate
```

3. **Run the development server**

```bash
make run-dev
```

4. **Access the application**

Open your browser and go to:
```
http://localhost:8000
```

## Development Workflow

WebToys uses a Make-based workflow for consistent development experience:

```bash
# Run development server
make run-dev

# Format, lint, and test (fast development cycle)
make dev-loop

# Run tests
make test
make test-unit
make test-integration

# Format and lint
make format
make lint

# Run in Docker
make build
make run
```

See [CLAUDE.md](CLAUDE.md) for a complete list of development commands.

## Project Structure

```
webtoys/
├── backend/              # FastAPI application
│   ├── main.py           # Application entry point
│   ├── services/         # Core services
│   │   ├── ai_service.py # Claude API integration
│   │   ├── validator.py  # Code validation
│   │   └── storage.py    # Storage service
│   ├── static/           # Frontend files
│   └── tests/            # Test suite
├── .github/              # CI/CD workflows
├── docker-compose.yml    # Docker configuration
├── Makefile              # Development workflow
└── CLAUDE.md             # Developer guide
```

## Production Deployment

For production deployment, the project includes CI/CD workflows:

1. **CI Pipeline** automatically runs on pull requests and commits to main:
   - Linting with ruff
   - Type checking with mypy
   - Unit and integration tests
   - Code coverage reporting

2. **CD Pipeline** deploys to environments:
   - Automatic deployment to development on merge to main
   - Manual triggered deployment to production via GitHub Actions
   - Uses Docker Hub for container registry

## Security Considerations

WebToys implements multiple layers of security:

1. **Server-side validation**: All generated code is checked for security issues
2. **Sandboxed execution**: WebToys run in restricted iframes
3. **Content Security Policy**: Strict CSP rules to prevent external resources
4. **Isolated execution**: Each WebToy runs in its own isolated environment

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our [development workflow](CLAUDE.md)
4. Run tests and linting (`make dev-loop`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

[MIT License](LICENSE)

## Acknowledgments

- Anthropic's Claude API for AI-powered code generation
- The FastAPI framework
- All the creative people who inspire web experiments