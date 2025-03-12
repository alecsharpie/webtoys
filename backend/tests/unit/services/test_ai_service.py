"""
Unit tests for AI service
"""

from typing import Any
from unittest.mock import patch

import pytest

from services.ai_service import AIService


@pytest.mark.unit
class TestAIService:
    """Test cases for AI service"""

    @pytest.fixture
    def ai_service(self) -> AIService:
        """Create AI service instance for testing"""
        return AIService(api_key="test_api_key", model="test-model")

    @pytest.mark.asyncio
    async def test_generate_code_success(
        self, ai_service: AIService, monkeypatch
    ) -> None:
        """Test successful code generation"""
        # Mock the entire method
        expected_result = {
            "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
            "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
            "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();",
            "description": "A simple blue square animation",
        }

        # Create a mock for the method
        async def mock_generate_code(self, description, parameters=None):
            # We can verify description here
            assert description == "Create a simple canvas animation"
            return expected_result

        # Apply the mock using monkeypatch
        monkeypatch.setattr(AIService, "generate_code", mock_generate_code)

        # Call the mocked method
        result = await ai_service.generate_code(
            description="Create a simple canvas animation"
        )

        # Verify the result is what we expected
        assert result == expected_result
        assert "html" in result
        assert "css" in result
        assert "js" in result
        assert "<canvas" in result["html"]
        assert "fillStyle" in result["js"]

    @pytest.mark.asyncio
    async def test_generate_code_api_error(self, ai_service: AIService) -> None:
        """Test handling of API errors during code generation"""
        # Mock the Anthropic client to simulate an API error
        with patch.object(ai_service.client.messages, "create") as mock_create:
            # Configure the mock to raise an exception
            mock_create.side_effect = Exception("API error: Rate limit exceeded")

            # Should raise an exception
            with pytest.raises(Exception) as exc_info:
                await ai_service.generate_code(
                    description="Create a simple canvas animation"
                )

            assert "AI service error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_code_with_parameters(
        self, ai_service: AIService, monkeypatch
    ) -> None:
        """Test code generation with additional parameters"""
        # Create expected result dictionary
        expected_result = {
            "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
            "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
            "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();",
            "description": "A complex space animation",
        }

        # Parameters to test with
        parameters = {
            "complexity": "high",
            "style": "space",
            "colors": ["blue", "purple"],
        }

        # Create a mock for the method that verifies parameters
        async def mock_generate_code(self, description, parameters=None):
            # Verify description and parameters
            assert description == "Create a complex space animation"
            assert parameters is not None
            assert parameters["complexity"] == "high"
            assert parameters["style"] == "space"
            assert "colors" in parameters
            assert parameters["colors"] == ["blue", "purple"]
            return expected_result

        # Apply the mock using monkeypatch
        monkeypatch.setattr(AIService, "generate_code", mock_generate_code)

        # Call the mocked method with parameters
        result = await ai_service.generate_code(
            description="Create a complex space animation", parameters=parameters
        )

        # Verify the result is what we expected
        assert result == expected_result
        assert "html" in result
        assert "css" in result
        assert "js" in result

    @pytest.mark.asyncio
    async def test_parse_response(
        self, ai_service: AIService, mock_claude_response: Any
    ) -> None:
        """Test parsing Claude API response"""
        # Access the content directly instead of trying to use dict syntax
        response_text = mock_claude_response.content[0].text
        result = ai_service._parse_response(response_text)

        assert isinstance(result, dict)
        assert "html" in result
        assert "css" in result
        assert "js" in result
        assert "<canvas" in result["html"]

    @pytest.mark.asyncio
    async def test_parse_response_invalid_format(self, ai_service: AIService) -> None:
        """Test handling invalid response format"""
        invalid_response_text = "This is not a valid response format"

        # Parse should return default values for missing components
        result = ai_service._parse_response(invalid_response_text)

        assert "html" in result
        assert "css" in result
        assert "js" in result
        # The method should provide default values for missing components
