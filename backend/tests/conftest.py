"""
Test fixtures for WebToys application
"""

import os
import tempfile
import shutil
import asyncio
import pytest
from typing import Dict, Any, Generator, AsyncGenerator
from fastapi import FastAPI
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

# Import application components for testing
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from services.ai_service import AIService
from services.validator import WebToyValidator
from services.storage import StorageService
from config import settings


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_app() -> FastAPI:
    """
    Test fixture for creating a FastAPI test application
    """
    return app


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Test fixture for creating a test client for the FastAPI application
    """
    async with LifespanManager(test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client


@pytest.fixture
def temp_storage_dir() -> Generator[str, None, None]:
    """
    Test fixture for creating a temporary storage directory
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_claude_response() -> Dict[str, Any]:
    """
    Test fixture for mock Claude API response
    """
    return {
        "content": [
            {
                "type": "text",
                "text": """```json
{
  "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
  "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
  "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();"
}
```"""
            }
        ],
        "id": "msg_12345abcde",
        "model": "claude-3-opus-20240229",
        "role": "assistant",
        "type": "message"
    }


@pytest.fixture
def sample_webtoy_code() -> Dict[str, str]:
    """
    Test fixture for sample WebToy code
    """
    return {
        "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
        "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
        "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();"
    }


@pytest.fixture
def mock_ai_service(mocker, mock_claude_response):
    """
    Test fixture for mocking the AI service
    """
    mock_service = mocker.patch.object(AIService, 'generate_code')
    mock_service.return_value = {
        "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
        "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
        "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();"
    }
    return mock_service


@pytest.fixture
def test_storage_service(temp_storage_dir):
    """
    Test fixture for creating a test storage service
    """
    return StorageService(
        storage_type="file",
        connection_string=temp_storage_dir
    )


@pytest.fixture
def validator_service():
    """
    Test fixture for creating a validator service
    """
    return WebToyValidator()