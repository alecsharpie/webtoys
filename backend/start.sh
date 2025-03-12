#!/bin/bash

# Check for required environment variables
if [ -z "$CLAUDE_API_KEY" ]; then
  echo "ERROR: CLAUDE_API_KEY environment variable is not set"
  exit 1
fi

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 