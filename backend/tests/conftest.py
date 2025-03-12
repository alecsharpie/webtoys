"""
Test fixtures for WebToys application
"""

import os
import shutil

# Import application components for testing
import sys
import tempfile
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

from services.ai_service import AIService
from services.storage import StorageService
from services.validator import WebToyValidator

# Define the event loop policy globally so pytest-asyncio can use its automatic handling
# We don't need to define our own event_loop fixture anymore since we're using asyncio_mode="auto"


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
    # Set up lifespan manager to handle startup/shutdown events
    async with LifespanManager(test_app):
        # Create client with the correct base URL
        # HTTPX AsyncClient doesn't accept 'app' parameter directly
        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport, base_url="http://test", follow_redirects=True
        ) as client:
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
def mock_claude_response() -> Any:
    """
    Test fixture for mock Claude API response

    This creates a structure that mimics Anthropic's Messages API response
    """
    # Create a proper TextBlock that matches the Anthropic API
    text_content = """<HTML>
<canvas id='myCanvas' width='500' height='500'></canvas>
</HTML>

<CSS>
body { margin: 0; overflow: hidden; background: #f0f0f0; }
</CSS>

<JAVASCRIPT>
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'blue';
  ctx.fillRect(50, 50, 100, 100);
  requestAnimationFrame(draw);
}

draw();
</JAVASCRIPT>

<DESCRIPTION>
A simple blue square animation
</DESCRIPTION>
"""

    # Create a TextBlock class that properly mimics the Anthropic API structure
    class TextBlock:
        def __init__(self, text: str):
            self.text = text
            self.type = "text"

    # Create a MockResponse class that has the right structure
    class MockResponse:
        def __init__(self):
            self.content = [TextBlock(text_content)]
            self.id = "msg_12345abcde"
            self.model = "claude-3-opus-20240229"
            self.role = "assistant"

    return MockResponse()


@pytest.fixture
def sample_webtoy_code() -> dict[str, str]:
    """
    Test fixture for sample WebToy code
    """
    return {
        "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
        "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
        "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();",
    }


@pytest.fixture
def mock_ai_service(
    mocker: MockerFixture, mock_claude_response: dict[str, Any]
) -> MagicMock:
    """
    Test fixture for mocking the AI service
    """
    mock_service = mocker.patch.object(AIService, "generate_code")
    mock_service.return_value = {
        "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
        "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
        "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();",
    }
    return mock_service


@pytest.fixture
def test_storage_service(temp_storage_dir: str) -> StorageService:
    """
    Test fixture for creating a test storage service
    """
    return StorageService(storage_type="file", connection_string=temp_storage_dir)


@pytest.fixture
def validator_service() -> WebToyValidator:
    """
    Test fixture for creating a validator service
    """
    return WebToyValidator()
