"""
Unit tests for AI service
"""

from typing import Any
from unittest.mock import AsyncMock, patch

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
        self, ai_service: AIService, mock_claude_response: dict[str, Any]
    ) -> None:
        """Test successful code generation"""
        # Mock the Anthropic client response
        with patch("services.ai_service.httpx.AsyncClient") as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_claude_response
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Call the generate_code method
            result = await ai_service.generate_code(
                description="Create a simple canvas animation"
            )

            # Verify the result
            assert "html" in result
            assert "css" in result
            assert "js" in result
            assert "<canvas" in result["html"]
            assert "fillStyle" in result["js"]

            # Verify the API was called with the right parameters
            called_json = mock_post.call_args[1]["json"]

            assert "messages" in called_json
            assert called_json["messages"][0]["role"] == "user"
            assert (
                "Create a simple canvas animation"
                in called_json["messages"][0]["content"]
            )
            assert called_json["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_generate_code_api_error(self, ai_service: AIService) -> None:
        """Test handling of API errors during code generation"""
        # Mock the Anthropic client to simulate an API error
        with patch("services.ai_service.httpx.AsyncClient") as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Should raise an exception
            with pytest.raises(Exception) as exc_info:
                await ai_service.generate_code(
                    description="Create a simple canvas animation"
                )

            assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_code_with_parameters(
        self, ai_service: AIService, mock_claude_response: dict[str, Any]
    ) -> None:
        """Test code generation with additional parameters"""
        # Mock the Anthropic client response
        with patch("services.ai_service.httpx.AsyncClient") as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_claude_response
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Call with parameters
            parameters = {
                "complexity": "high",
                "theme": "space",
                "colors": ["blue", "purple"],
            }

            await ai_service.generate_code(
                description="Create a complex space animation", parameters=parameters
            )

            # Verify parameters were included in the prompt
            called_json = mock_post.call_args[1]["json"]
            prompt_content = called_json["messages"][0]["content"]

            assert "complexity" in prompt_content
            assert "high" in prompt_content
            assert "theme" in prompt_content
            assert "space" in prompt_content
            assert "blue" in prompt_content
            assert "purple" in prompt_content

    @pytest.mark.asyncio
    async def test_parse_response(
        self, ai_service: AIService, mock_claude_response: dict[str, Any]
    ) -> None:
        """Test parsing Claude API response"""
        # Test the helper method directly
        response_text = mock_claude_response["content"][0]["text"]
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
