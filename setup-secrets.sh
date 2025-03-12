#!/bin/bash

# Check if 1Password CLI is installed
if ! command -v op &> /dev/null; then
    echo "1Password CLI is not installed. Please install it first."
    echo "Visit: https://developer.1password.com/docs/cli/get-started"
    exit 1
fi

# Ensure user is authenticated with 1Password
if ! op account list &> /dev/null; then
    echo "Please sign in to 1Password CLI first using 'op signin'"
    exit 1
fi

# Get the vault name
VAULT_NAME=$(op vault list --format=json | jq -r '.[0].name')
if [ -z "$VAULT_NAME" ]; then
    echo "Could not determine vault name. Using direct item get method."
    CLAUDE_API_KEY=$(op item get "WEBTOY_CLAUDE_API_KEY" --fields credential)
else
    # Try to get Claude API key from 1Password using proper secret reference format
    echo "Attempting to read API key from vault: $VAULT_NAME"
    CLAUDE_API_KEY=$(op read "op://$VAULT_NAME/WEBTOY_CLAUDE_API_KEY/credential")
    
    # If the above fails, try direct item get
    if [ -z "$CLAUDE_API_KEY" ] || [[ "$CLAUDE_API_KEY" == op://* ]]; then
        echo "Trying alternative method to get API key..."
        CLAUDE_API_KEY=$(op item get "WEBTOY_CLAUDE_API_KEY" --fields credential)
    fi
fi

# Verify we got a valid API key (not starting with op://)
if [[ "$CLAUDE_API_KEY" == op://* ]]; then
    echo "Error: Could not resolve the API key from 1Password. Got a reference instead of a value."
    echo "Please check your 1Password setup and try again."
    exit 1
fi

# Create or update .env file
echo "Creating/updating .env file with Claude API key..."

# Create a temporary file
TEMP_ENV=$(mktemp)

# If .env exists, copy its contents to the temp file, excluding the API key line
if [ -f .env ]; then
    grep -v "^CLAUDE_API_KEY=" .env > "$TEMP_ENV"
fi

# Add the API key to the temp file
echo "CLAUDE_API_KEY=$CLAUDE_API_KEY" >> "$TEMP_ENV"

# Make sure other environment variables are present
if ! grep -q "^CLAUDE_MODEL=" "$TEMP_ENV"; then
    echo "CLAUDE_MODEL=claude-3-7-sonnet-20250219" >> "$TEMP_ENV"
fi

if ! grep -q "^STORAGE_TYPE=" "$TEMP_ENV"; then
    echo "STORAGE_TYPE=file" >> "$TEMP_ENV"
fi

if ! grep -q "^STORAGE_CONNECTION=" "$TEMP_ENV"; then
    echo "STORAGE_CONNECTION=./storage" >> "$TEMP_ENV"
fi

if ! grep -q "^BASE_URL=" "$TEMP_ENV"; then
    echo "BASE_URL=http://localhost:8000" >> "$TEMP_ENV"
fi

# Replace the .env file with our updated version
mv "$TEMP_ENV" .env

# Set appropriate permissions
chmod 600 .env

echo "Secrets setup complete!" 