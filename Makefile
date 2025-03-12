.PHONY: setup setup-dev build run run-dev run-detached stop test test-unit test-integration test-coverage lint format check ci deploy-dev deploy-prod clean help

# Colors for better readability
COLOR_RESET=\033[0m
COLOR_GREEN=\033[32m
COLOR_YELLOW=\033[33m
COLOR_BLUE=\033[34m

# Default target
.DEFAULT_GOAL := help

# Development environment
setup: ## Set up environment variables for API keys from 1Password
	@echo "${COLOR_BLUE}Setting up environment variables...${COLOR_RESET}"
	@./setup-secrets.sh
	@uv sync
	@echo "${COLOR_GREEN}Setup complete!${COLOR_RESET}"

# Set up development environment with uv
setup-dev: ## Set up development environment with uv
	@echo "${COLOR_BLUE}Setting up development environment...${COLOR_RESET}"
	@uv venv
	@uv sync
	@echo "${COLOR_GREEN}Development environment setup complete!${COLOR_RESET}"
	@echo "${COLOR_YELLOW}No need to activate the virtual environment with uv!${COLOR_RESET}"

# Build the application
build: ## Build Docker images
	@echo "${COLOR_BLUE}Building Docker images...${COLOR_RESET}"
	@docker-compose build --no-cache
	@echo "${COLOR_GREEN}Build complete!${COLOR_RESET}"

# Build the application with cache (faster)
build-cached: ## Build Docker images with cache
	@echo "${COLOR_BLUE}Building Docker images with cache...${COLOR_RESET}"
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

# Rebuild and run the application 
run-rebuild: build ## Rebuild and run the application
	@echo "${COLOR_BLUE}Starting application with freshly built images...${COLOR_RESET}"
	@if [ ! -f .env ] || ! grep -q "^CLAUDE_API_KEY=" .env; then \
		echo "${COLOR_YELLOW}Environment not set up. Running setup...${COLOR_RESET}"; \
		./setup-secrets.sh; \
	fi
	@docker-compose up --force-recreate
	@echo "${COLOR_GREEN}Application running at http://localhost:8000${COLOR_RESET}"

# Run the application in development mode
run-dev: ## Run development server locally with uvicorn
	@echo "${COLOR_BLUE}Starting development server...${COLOR_RESET}"
	@cd backend && uv run uvicorn main:app --reload
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
	@cd backend && uv run python -m pytest
	@echo "${COLOR_GREEN}Tests complete!${COLOR_RESET}"

# Run test in Docker
test-docker: ## Run all tests in Docker container
	@echo "${COLOR_BLUE}Running all tests in container...${COLOR_RESET}"
	@docker-compose run --rm webtoys python -m pytest
	@echo "${COLOR_GREEN}Tests complete!${COLOR_RESET}"

# Run unit tests only
test-unit: ## Run unit tests only
	@echo "${COLOR_BLUE}Running unit tests...${COLOR_RESET}"
	@cd backend && uv run python -m pytest tests/unit -v
	@echo "${COLOR_GREEN}Unit tests complete!${COLOR_RESET}"

# Run integration tests only
test-integration: ## Run integration tests only
	@echo "${COLOR_BLUE}Running integration tests...${COLOR_RESET}"
	@cd backend && uv run python -m pytest tests/integration -v
	@echo "${COLOR_GREEN}Integration tests complete!${COLOR_RESET}"

# Generate test coverage report
test-coverage: ## Generate test coverage report
	@echo "${COLOR_BLUE}Generating test coverage report...${COLOR_RESET}"
	@cd backend && uv run python -m pytest --cov=. --cov-report=term --cov-report=html
	@echo "${COLOR_GREEN}HTML coverage report in backend/htmlcov/${COLOR_RESET}"

# Lint code using uv
lint: ## Lint code with uv (ruff, mypy)
	@echo "${COLOR_BLUE}Linting code...${COLOR_RESET}"
	@cd backend && uv run ruff check .
	@cd backend && uv run mypy backend
	@echo "${COLOR_GREEN}Linting complete!${COLOR_RESET}"

# Fix linting errors automatically
lint-fix: ## Fix linting errors automatically with ruff
	@echo "${COLOR_BLUE}Fixing linting errors...${COLOR_RESET}"
	@cd backend && uv run ruff check --fix .
	@echo "${COLOR_GREEN}Linting fixes applied!${COLOR_RESET}"

# Format code using uv
format: ## Format code with uv (ruff format)
	@echo "${COLOR_BLUE}Formatting code...${COLOR_RESET}"
	@cd backend && uv run ruff format .
	@echo "${COLOR_GREEN}Formatting complete!${COLOR_RESET}"

# CI pipeline
ci: lint format test ## Run CI checks (format, lint, test)
	@echo "${COLOR_GREEN}CI pipeline complete!${COLOR_RESET}"

# Build optimized Docker image for deployment
build-prod: ## Build optimized Docker image for deployment
	@echo "${COLOR_BLUE}Building optimized Docker image for deployment...${COLOR_RESET}"
	@docker-compose build --no-cache
	@docker tag webtoys_webtoys:latest webtoys:$(shell date +%Y%m%d-%H%M%S)
	@echo "${COLOR_GREEN}Production build complete!${COLOR_RESET}"

# Deploy to development environment
deploy-dev: build-prod ## Deploy to development environment
	@echo "${COLOR_BLUE}Deploying to development environment...${COLOR_RESET}"
	@echo "${COLOR_YELLOW}This is a placeholder. Implement your deployment logic here.${COLOR_RESET}"
	@# Example: docker push webtoys:latest to your dev registry
	@echo "${COLOR_GREEN}Deployment complete!${COLOR_RESET}"

# Deploy to production environment
deploy-prod: build-prod ## Deploy to production environment
	@echo "${COLOR_BLUE}Deploying to production environment...${COLOR_RESET}"
	@echo "${COLOR_YELLOW}This is a placeholder. Implement your production deployment logic here.${COLOR_RESET}"
	@# Example: docker push webtoys:$(shell date +%Y%m%d-%H%M%S) to your prod registry
	@echo "${COLOR_GREEN}Deployment complete!${COLOR_RESET}"

# Clean temporary and generated files
clean: ## Clean pycache, coverage reports and other temporary files
	@echo "${COLOR_BLUE}Cleaning temporary files...${COLOR_RESET}"
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .pytest_cache -exec rm -rf {} +
	@find . -type d -name htmlcov -exec rm -rf {} +
	@find . -type d -name .mypy_cache -exec rm -rf {} +
	@find . -type d -name .ruff_cache -exec rm -rf {} +
	@find . -type f -name .coverage -delete
	@find . -type f -name *.pyc -delete
	@find . -type f -name *.pyo -delete
	@find . -type f -name *.pyd -delete
	@find . -type f -name .DS_Store -delete
	@rm -rf .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache
	@echo "${COLOR_GREEN}Clean complete!${COLOR_RESET}"

# Clean Docker resources
clean-docker: ## Clean Docker resources (containers, images, volumes)
	@echo "${COLOR_BLUE}Cleaning Docker resources...${COLOR_RESET}"
	@docker-compose down --volumes --remove-orphans
	@docker image prune -f
	@echo "${COLOR_GREEN}Docker clean complete!${COLOR_RESET}"

# Full cleanup - code and Docker
clean-all: clean clean-docker ## Full cleanup of code and Docker resources
	@echo "${COLOR_GREEN}All clean complete!${COLOR_RESET}"

# Show help
help: ## Show this help message
	@echo "WebToys Development Workflow"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-15s\033[0m %s\n", $$1, $$2}'