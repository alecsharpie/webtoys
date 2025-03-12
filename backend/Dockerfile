FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml and other files needed for dependency resolution
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system --no-cache-dir .

# Copy application code
COPY . .

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

RUN chmod +x /app/healthcheck.sh

COPY start.sh /app/
RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]