.PHONY: setup setup-dev build run run-dev run-detached stop test test-unit test-integration test-coverage lint format check ci deploy-dev deploy-prod help

# Colors for better readability
COLOR_RESET=\033[0m
COLOR_GREEN=\033[32m
COLOR_YELLOW=\033[33m
COLOR_BLUE=\033[34m

# Default target
.DEFAULT_GOAL := help

# Setup environment variables from 1Password
setup: ## Set up environment variables for API keys
	@echo "${COLOR_BLUE}Setting up environment variables...${COLOR_RESET}"
	@./setup-secrets.sh
	@echo "${COLOR_GREEN}Setup complete!${COLOR_RESET}"

# Setup development environment
setup-dev: ## Set up development environment with uv
	@echo "${COLOR_BLUE}Setting up development environment...${COLOR_RESET}"
	@python -m venv .venv
	@. .venv/bin/activate && pip install --upgrade pip uv
	@. .venv/bin/activate && uv pip install -e .
	@. .venv/bin/activate && uv pip install --group dev --group lint --group pre-commit
	@. .venv/bin/activate && pre-commit install
	@echo "${COLOR_GREEN}Setup complete! Activate your virtual environment with: source .venv/bin/activate${COLOR_RESET}"

# Build the application
build: ## Build Docker images
	@echo "${COLOR_BLUE}Building Docker images...${COLOR_RESET}"
	@docker-compose build
	@echo "${COLOR_GREEN}Build complete!${COLOR_RESET}"

# Run the application in Docker
run: ## Run the application in Docker
	@echo "${COLOR_BLUE}Starting application...${COLOR_RESET}"
	@if [ ! -f .env ] || ! grep -q "^CLAUDE_API_KEY=" .env; then \
		echo "${COLOR_YELLOW}Environment not set up. Running setup...${COLOR_RESET}"; \
		./setup-secrets.sh; \
	fi
	@docker-compose up
	@echo "${COLOR_GREEN}Application running at http://localhost:8000${COLOR_RESET}"

# Run the application in development mode
run-dev: ## Run development server locally with uvicorn
	@echo "${COLOR_BLUE}Starting development server...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uvicorn main:app --reload
	@echo "${COLOR_GREEN}Development server running at http://localhost:8000${COLOR_RESET}"

# Run the application in detached mode
run-detached: ## Run the application in background
	@echo "${COLOR_BLUE}Starting application in background...${COLOR_RESET}"
	@if [ ! -f .env ] || ! grep -q "^CLAUDE_API_KEY=" .env; then \
		echo "${COLOR_YELLOW}Environment not set up. Running setup...${COLOR_RESET}"; \
		./setup-secrets.sh; \
	fi
	@docker-compose up -d
	@echo "${COLOR_GREEN}Application running in background at http://localhost:8000${COLOR_RESET}"

# Stop the application
stop: ## Stop the application
	@echo "${COLOR_BLUE}Stopping application...${COLOR_RESET}"
	@docker-compose down
	@echo "${COLOR_GREEN}Application stopped.${COLOR_RESET}"

# Run tests - supports local and containerized
test: ## Run all tests locally with uv
	@echo "${COLOR_BLUE}Running all tests...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run python -m pytest
	@echo "${COLOR_GREEN}Tests complete!${COLOR_RESET}"

# Run test in Docker
test-docker: ## Run all tests in Docker container
	@echo "${COLOR_BLUE}Running all tests in container...${COLOR_RESET}"
	@docker-compose run --rm webtoys python -m pytest
	@echo "${COLOR_GREEN}Tests complete!${COLOR_RESET}"

# Run unit tests only
test-unit: ## Run unit tests only
	@echo "${COLOR_BLUE}Running unit tests...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run python -m pytest tests/unit -v
	@echo "${COLOR_GREEN}Unit tests complete!${COLOR_RESET}"

# Run integration tests only
test-integration: ## Run integration tests only
	@echo "${COLOR_BLUE}Running integration tests...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run python -m pytest tests/integration -v
	@echo "${COLOR_GREEN}Integration tests complete!${COLOR_RESET}"

# Generate test coverage report
test-coverage: ## Generate test coverage report
	@echo "${COLOR_BLUE}Generating test coverage report...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run python -m pytest --cov=. --cov-report=term --cov-report=html
	@echo "${COLOR_GREEN}HTML coverage report in backend/htmlcov/${COLOR_RESET}"

# Fast development loop
dev-loop: lint format test-unit ## Fast development loop - format, lint, test
	@echo "${COLOR_GREEN}Development cycle complete!${COLOR_RESET}"

# Lint code using uv
lint: ## Lint code with uv (ruff, mypy)
	@echo "${COLOR_BLUE}Linting code...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run ruff check .
	@. .venv/bin/activate && uv run mypy backend
	@echo "${COLOR_GREEN}Linting complete!${COLOR_RESET}"

# Fix linting errors automatically
lint-fix: ## Fix linting errors automatically with ruff
	@echo "${COLOR_BLUE}Fixing linting errors...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run ruff check --fix .
	@echo "${COLOR_GREEN}Linting fixes applied!${COLOR_RESET}"

# Format code using uv
format: ## Format code with uv (ruff format)
	@echo "${COLOR_BLUE}Formatting code...${COLOR_RESET}"
	@. .venv/bin/activate && cd backend && uv run ruff format .
	@echo "${COLOR_GREEN}Formatting complete!${COLOR_RESET}"

# CI pipeline
ci: ## Run CI checks (format, lint, test)
	@echo "${COLOR_BLUE}Running CI pipeline...${COLOR_RESET}"
	@uv pip install -e .
	@uv pip install --group dev --group lint
	@cd backend && uv run ruff check .
	@uv run mypy backend
	@cd backend && uv run python -m pytest --cov=. --cov-report=xml
	@echo "${COLOR_GREEN}CI pipeline complete!${COLOR_RESET}"

# Deploy to development environment
deploy-dev: ## Deploy to development environment
	@echo "${COLOR_BLUE}Deploying to development environment...${COLOR_RESET}"
	@echo "${COLOR_YELLOW}This is a placeholder. Implement your deployment logic here.${COLOR_RESET}"
	@# Add your deployment commands here
	@echo "${COLOR_GREEN}Deployment complete!${COLOR_RESET}"

# Deploy to production environment
deploy-prod: ## Deploy to production environment
	@echo "${COLOR_BLUE}Deploying to production environment...${COLOR_RESET}"
	@echo "${COLOR_YELLOW}This is a placeholder. Implement your production deployment logic here.${COLOR_RESET}"
	@# Add your production deployment commands here
	@echo "${COLOR_GREEN}Deployment complete!${COLOR_RESET}"

# Show help
help: ## Show this help message
	@echo "WebToys Development Workflow"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-15s\033[0m %s\n", $$1, $$2}'