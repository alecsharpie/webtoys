"""
Unit tests for WebToy rendering functionality
"""

import pytest

# Import the render function for testing
from main import render_webtoy


@pytest.mark.unit
class TestRenderWebToy:
    """Test cases for WebToy rendering"""

    @pytest.fixture
    def sample_code(self):
        """Sample WebToy code for testing"""
        return {
            "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
            "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
            "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = 'blue';\n  ctx.fillRect(50, 50, 100, 100);\n  requestAnimationFrame(draw);\n}\n\ndraw();",
        }

    def test_render_basic_webtoy(self, sample_code):
        """Test rendering a basic WebToy"""
        options = {
            "title": "Basic WebToy",
            "description": "A simple canvas test",
            "is_preview": False,
        }

        result = render_webtoy(sample_code, options)

        # Check for basic structure
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result

        # Check for title and description
        assert "<title>Basic WebToy</title>" in result
        assert 'content="A simple canvas test"' in result

        # Check for code injection
        assert sample_code["html"] in result
        assert sample_code["css"] in result
        assert sample_code["js"] in result

        # Check for important elements
        assert "webtoy-container" in result
        assert "webtoy-attribution" in result

        # Not a preview, so shouldn't have noindex
        assert "noindex" not in result

    def test_render_preview_webtoy(self, sample_code):
        """Test rendering a preview WebToy"""
        options = {
            "title": "Preview WebToy",
            "description": "A preview canvas test",
            "is_preview": True,
        }

        result = render_webtoy(sample_code, options)

        # Should have noindex
        assert 'meta name="robots" content="noindex"' in result

        # Shouldn't have remix link
        assert "Remix this" not in result

    def test_render_published_webtoy(self, sample_code):
        """Test rendering a published WebToy"""
        options = {
            "title": "Published WebToy",
            "description": "A published canvas test",
            "is_preview": False,
            "webtoy_id": "abc123",
        }

        result = render_webtoy(sample_code, options)

        # Should have remix link
        assert "Remix this" in result
        assert "remix/abc123" in result

        # Should have share button
        assert "shareWebToy()" in result

    def test_content_security_policy(self, sample_code):
        """Test that CSP headers are included"""
        result = render_webtoy(sample_code, {"title": "CSP Test"})

        # Check for CSP headers
        assert "Content-Security-Policy" in result
        assert "default-src 'none'" in result
        assert "script-src 'unsafe-inline'" in result
        assert "style-src 'unsafe-inline'" in result

        # Security headers
        assert "X-Content-Type-Options" in result
        assert "X-Frame-Options" in result

    def test_html_sanitization(self):
        """Test HTML sanitization in rendering"""
        code = {
            "html": "<canvas></canvas>",
            "css": "body { margin: 0; }",
            "js": "console.log('test');",
        }

        options = {
            "title": "Test <script>alert('XSS')</script>",
            "description": "Description <img src=x onerror=alert('XSS')>",
            "is_preview": False,
        }

        result = render_webtoy(code, options)

        # Title and description should be sanitized
        assert "Test &lt;script&gt;alert('XSS')&lt;/script&gt;" in result
        assert "Description &lt;img src=x onerror=alert('XSS')&gt;" in result

        # Scripts shouldn't execute
        assert "<script>alert('XSS')</script>" not in result

    def test_sandbox_environment(self, sample_code):
        """Test the JavaScript sandbox environment"""
        result = render_webtoy(sample_code, {"title": "Sandbox Test"})

        # Should have sandbox wrapper
        assert "(function() {" in result

        # Should have safe console
        assert "safeConsole" in result

        # Should have dangerous API blocking
        assert "dangerousGlobals" in result
        assert "'fetch', 'XMLHttpRequest', 'WebSocket'" in result

        # Should have error handling
        assert "catch (error)" in result
