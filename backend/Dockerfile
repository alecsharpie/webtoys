# Use the official Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Copy only dependency definition files
COPY pyproject.toml /app/

# Create an empty README.md file to satisfy the build requirements
RUN touch README.md

# Install dependencies in a separate stage for better caching
# Set UV_NO_EDITABLE=1 to prevent editable installs
ENV UV_NO_EDITABLE=1
RUN uv sync --compile-bytecode

# Production image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Set path to include the virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code from backend directory
COPY backend/ /app/

# Create storage directory
RUN mkdir -p /app/storage/previews /app/storage/webtoys

# Add a health check script that verifies environment variables at runtime
COPY <<EOF /app/healthcheck.sh
#!/bin/bash
if [ -z "\$CLAUDE_API_KEY" ]; then
  echo "ERROR: CLAUDE_API_KEY environment variable is not set"
  exit 1
fi
curl -f http://localhost:8000/health
EOF

RUN chmod +x /app/healthcheck.sh /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]