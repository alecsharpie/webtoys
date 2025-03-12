"""
Integration tests for WebToys API
"""

import pytest
import uuid
import json
from httpx import AsyncClient
from fastapi import FastAPI

# Import application components for testing
from main import app, ai_service, validator, storage


@pytest.mark.integration
class TestAPIEndpoints:
    """Test cases for API endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client: AsyncClient):
        """Test health check endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_generate_endpoint_success(self, test_client: AsyncClient, mock_ai_service):
        """Test successful code generation endpoint"""
        # Create test request
        request_data = {
            "description": "Create a simple bouncing ball animation",
            "parameters": {
                "complexity": "medium",
                "colors": ["red", "blue"]
            }
        }
        
        response = await test_client.post("/api/generate", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "preview_id" in data
        assert "code" in data
        assert "html" in data["code"]
        assert "css" in data["code"]
        assert "js" in data["code"]
        
        # Verify preview was stored
        preview = await storage.get_preview(data["preview_id"])
        assert preview is not None
        assert preview["metadata"]["description"] == request_data["description"]

    @pytest.mark.asyncio
    async def test_generate_endpoint_invalid_input(self, test_client: AsyncClient):
        """Test generate endpoint with invalid input"""
        # Missing required description
        invalid_request = {
            "parameters": {"complexity": "medium"}
        }
        
        response = await test_client.post("/api/generate", json=invalid_request)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_publish_endpoint_success(self, test_client: AsyncClient, sample_webtoy_code):
        """Test successful publish endpoint"""
        # First create a preview
        preview_id = str(uuid.uuid4())
        metadata = {
            "description": "Test WebToy",
            "timestamp": 1234567890
        }
        
        await storage.store_preview(
            preview_id=preview_id,
            code=sample_webtoy_code,
            metadata=metadata
        )
        
        # Now publish it
        request_data = {
            "preview_id": preview_id
        }
        
        response = await test_client.post("/api/publish", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "url" in data
        
        # Verify webtoy was published
        webtoy = await storage.get_webtoy(data["id"])
        assert webtoy is not None
        assert webtoy["code"] == sample_webtoy_code
        assert webtoy["metadata"]["description"] == metadata["description"]

    @pytest.mark.asyncio
    async def test_publish_endpoint_nonexistent_preview(self, test_client: AsyncClient):
        """Test publish endpoint with non-existent preview"""
        request_data = {
            "preview_id": "non-existent-preview"
        }
        
        response = await test_client.post("/api/publish", json=request_data)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_preview_endpoint(self, test_client: AsyncClient, sample_webtoy_code):
        """Test preview retrieval endpoint"""
        # Create a preview
        preview_id = str(uuid.uuid4())
        metadata = {
            "description": "Test Preview WebToy",
            "timestamp": 1234567890
        }
        
        await storage.store_preview(
            preview_id=preview_id,
            code=sample_webtoy_code,
            metadata=metadata
        )
        
        # Request the preview
        response = await test_client.get(f"/preview/{preview_id}")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        
        # Check content
        content = response.text
        assert "<canvas" in content
        assert "WebToy Preview" in content
        assert "Test Preview WebToy" in content
        assert "meta name=\"robots\" content=\"noindex\"" in content

    @pytest.mark.asyncio
    async def test_get_preview_nonexistent(self, test_client: AsyncClient):
        """Test retrieval of non-existent preview"""
        response = await test_client.get("/preview/non-existent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_webtoy_endpoint(self, test_client: AsyncClient, sample_webtoy_code):
        """Test webtoy retrieval endpoint"""
        # Create a webtoy
        webtoy_id = "test-toy-123"
        metadata = {
            "description": "Published Test WebToy",
            "timestamp": 1234567890
        }
        
        await storage.publish_webtoy(
            webtoy_id=webtoy_id,
            code=sample_webtoy_code,
            metadata=metadata
        )
        
        # Request the webtoy
        response = await test_client.get(f"/toy/{webtoy_id}")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        
        # Check content
        content = response.text
        assert "<canvas" in content
        assert f"WebToy: {webtoy_id}" in content
        assert "Published Test WebToy" in content
        assert "meta name=\"robots\" content=\"noindex\"" not in content

    @pytest.mark.asyncio
    async def test_get_webtoy_nonexistent(self, test_client: AsyncClient):
        """Test retrieval of non-existent webtoy"""
        response = await test_client.get("/toy/non-existent")
        assert response.status_code == 404