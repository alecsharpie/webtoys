"""
Unit tests for rate limiting functionality
"""

import pytest
import time
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, MagicMock, patch

# Import rate limiting function for testing
from main import check_rate_limit


@pytest.mark.unit
class TestRateLimit:
    """Test cases for rate limiting functionality"""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request for testing"""
        request = AsyncMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        return request

    @pytest.mark.asyncio
    async def test_rate_limit_first_request(self, mock_request):
        """Test rate limiting for the first request from a client"""
        # Clear rate limits
        from main import rate_limits
        rate_limits.clear()
        
        # Should not raise an exception
        await check_rate_limit(mock_request)
        
        # Verify rate limit entry was created
        assert "127.0.0.1" in rate_limits
        assert rate_limits["127.0.0.1"]["count"] == 1

    @pytest.mark.asyncio
    async def test_rate_limit_multiple_requests(self, mock_request):
        """Test rate limiting for multiple requests from a client"""
        # Clear rate limits
        from main import rate_limits
        rate_limits.clear()
        
        # Make 9 requests (under the limit)
        for _ in range(9):
            await check_rate_limit(mock_request)
            
        # Verify count
        assert rate_limits["127.0.0.1"]["count"] == 9
        
        # Make another request (should be allowed)
        await check_rate_limit(mock_request)
        assert rate_limits["127.0.0.1"]["count"] == 10

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_request):
        """Test rate limiting when limit is exceeded"""
        # Clear rate limits
        from main import rate_limits
        rate_limits.clear()
        
        # Set up a client that has reached the limit
        rate_limits["127.0.0.1"] = {
            "timestamp": time.time(),
            "count": 10  # Already at the limit
        }
        
        # Next request should raise an exception
        with pytest.raises(HTTPException) as exc_info:
            await check_rate_limit(mock_request)
            
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_rate_limit_expiry(self, mock_request):
        """Test rate limit expiry"""
        # Clear rate limits
        from main import rate_limits
        rate_limits.clear()
        
        # Set up a client with an old timestamp
        rate_limits["127.0.0.1"] = {
            "timestamp": time.time() - 3601,  # More than 1 hour ago
            "count": 10  # At the limit
        }
        
        # Should reset the count and allow the request
        await check_rate_limit(mock_request)
        assert rate_limits["127.0.0.1"]["count"] == 1

    @pytest.mark.asyncio
    async def test_rate_limit_cleanup(self, mock_request):
        """Test cleanup of expired rate limit entries"""
        # Clear rate limits
        from main import rate_limits
        rate_limits.clear()
        
        # Add some entries with old timestamps
        rate_limits["192.168.1.1"] = {
            "timestamp": time.time() - 3700,  # Old
            "count": 5
        }
        
        rate_limits["192.168.1.2"] = {
            "timestamp": time.time() - 3600,  # Just expired
            "count": 7
        }
        
        rate_limits["192.168.1.3"] = {
            "timestamp": time.time() - 3000,  # Not expired
            "count": 3
        }
        
        # Make a request with a new client
        await check_rate_limit(mock_request)
        
        # Old entries should be cleaned up
        assert "192.168.1.1" not in rate_limits
        assert "192.168.1.2" not in rate_limits
        assert "192.168.1.3" in rate_limits
        assert "127.0.0.1" in rate_limits