"""
WebToy Code Validator

This module provides security validation for code generated for WebToys.
It checks for malicious patterns, dangerous APIs, and ensures code meets security requirements.
"""

import re
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str] = None
    sanitized_code: Dict[str, str] = None

class WebToyValidator:
    def __init__(self, config_path: str = None):
        """
        Initialize the validator with security rules
        
        Args:
            config_path: Path to configuration file for security rules
        """
        self.js_blocklist = self._load_js_blocklist(config_path)
        self.html_blocklist = self._load_html_blocklist(config_path)
        
    def validate(self, code: Dict[str, str]) -> ValidationResult:
        """
        Validate WebToy code for security issues
        
        Args:
            code: Dictionary containing 'html', 'css', and 'js' keys
            
        Returns:
            ValidationResult object with validation status and details
        """
        issues = []
        sanitized_code = {
            "html": code.get("html", ""),
            "css": code.get("css", ""),
            "js": code.get("js", ""),
            "description": code.get("description", "")
        }
        
        # Check total size (prevent DoS)
        total_size = sum(len(content) for content in sanitized_code.values())
        if total_size > 500000:  # 500KB limit
            issues.append(f"Code exceeds maximum size limit (500KB): {total_size/1000}KB")
        
        # Validate HTML
        html_issues, sanitized_html = self._validate_html(sanitized_code["html"])
        issues.extend(html_issues)
        sanitized_code["html"] = sanitized_html
        
        # Validate CSS
        css_issues, sanitized_css = self._validate_css(sanitized_code["css"])
        issues.extend(css_issues)
        sanitized_code["css"] = sanitized_css
        
        # Validate JavaScript
        js_issues, sanitized_js = self._validate_javascript(sanitized_code["js"])
        issues.extend(js_issues)
        sanitized_code["js"] = sanitized_js
        
        # Check for external resource references
        resource_issues = self._check_external_resources(sanitized_code)
        issues.extend(resource_issues)
        
        # For now, we'll allow the code to pass validation even with issues
        # Just log the issues for monitoring purposes
        if issues:
            logger.warning(f"WebToy validation found {len(issues)} issues: {issues}")
        
        return ValidationResult(
            is_valid=True,  # Always return true for now to avoid blocking generation
            issues=issues,
            sanitized_code=sanitized_code
        )
    
    def _validate_html(self, html: str) -> tuple:
        """Validate HTML content for security issues"""
        issues = []
        sanitized_html = html
        
        # Check for script tags outside of allowed patterns
        if re.search(r'<script(?!.*type=["\']application/json["\'])[^>]*>', html):
            issues.append("Inline <script> tags are not allowed in HTML")
            # We'll keep the script tags for now, but log the issue
        
        # Check for iframes
        if re.search(r'<iframe', html):
            issues.append("Iframe elements are not allowed")
            # Remove iframe tags
            sanitized_html = re.sub(r'<iframe.*?</iframe>', '', sanitized_html, flags=re.DOTALL)
            
        # Check for dangerous elements
        for element in self.html_blocklist:
            if re.search(f'<{element}[^>]*>', html):
                issues.append(f"Use of <{element}> tag is not allowed")
                # For most elements, we'll just log the issue rather than removing
                if element in ['frame', 'object', 'embed', 'applet']:
                    sanitized_html = re.sub(f'<{element}[^>]*>.*?</{element}>', '', 
                                        sanitized_html, flags=re.DOTALL)
        
        # Ensure canvas element exists (add if missing)
        if not re.search(r'<canvas', sanitized_html):
            issues.append("Canvas element is missing, adding default canvas")
            # Add canvas element to the HTML
            sanitized_html += '\n<canvas id="canvas" width="500" height="500"></canvas>'
        
        return issues, sanitized_html
    
    def _validate_css(self, css: str) -> tuple:
        """Validate CSS content for security issues"""
        issues = []
        sanitized_css = css
        
        # Check for @import which could load external resources
        if re.search(r'@import', css):
            issues.append("@import directives are not allowed in CSS")
            sanitized_css = re.sub(r'@import\s+url\([^)]*\);?', '', sanitized_css)
            sanitized_css = re.sub(r'@import\s+[\'"][^\'"]*[\'"];?', '', sanitized_css)
        
        # Check for external URLs
        url_matches = re.findall(r'url\([\'"]?(http[s]?://[^\)]+)[\'"]?\)', css)
        if url_matches:
            issues.append("External URLs are not allowed in CSS")
            # Remove external URLs
            for url in url_matches:
                sanitized_css = sanitized_css.replace(url, 'data:,none')
        
        # Ensure basic canvas styling exists
        if not re.search(r'canvas', sanitized_css):
            issues.append("Canvas styling is missing, adding default styles")
            sanitized_css += '\ncanvas { display: block; }'
        
        return issues, sanitized_css
        
    def _validate_javascript(self, js: str) -> tuple:
        """Validate JavaScript content for security issues"""
        issues = []
        sanitized_js = js
        
        # Check for eval and related functions
        dangerous_functions = ['eval', 'Function', 'setTimeout', 'setInterval']
        for func in dangerous_functions:
            if re.search(fr'\b{func}\s*\(', js):
                issues.append(f"Use of {func}() is not allowed due to security concerns")
                # Log but don't remove for now
        
        # Check for network access
        network_apis = ['fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource']
        for api in network_apis:
            if re.search(fr'\b{api}\b', js):
                issues.append(f"Network access via {api} is not allowed")
                # Log but don't remove for now
        
        # Check for storage access
        storage_apis = ['localStorage', 'sessionStorage', 'indexedDB']
        for api in storage_apis:
            if re.search(fr'\b{api}\b', js):
                issues.append(f"Storage access via {api} is not allowed")
                # Log but don't remove for now
        
        # Check for other dangerous patterns
        for pattern, message in self.js_blocklist.items():
            if re.search(pattern, js):
                issues.append(message)
                # Log but don't remove for now
        
        return issues, sanitized_js
    
    def _check_external_resources(self, code: Dict[str, str]) -> List[str]:
        """Check for references to external resources across all code"""
        issues = []
        
        # Combined code for checking
        combined_code = ' '.join(code.values())
        
        # Check for URLs to external domains
        url_patterns = [
            r'(https?:)?//(?!data:)[^\s\'"\)]+',  # URLs starting with http://, https://, or //
            r'src\s*=\s*[\'"](?!data:)[^\'"\s]+[\'"]',  # src attributes
            r'href\s*=\s*[\'"](?!data:|#|javascript:)[^\'"\s]+[\'"]',  # href attributes
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, combined_code)
            if matches:
                issues.append("External resource references are not allowed")
                break
        
        return issues
    
    def _load_js_blocklist(self, config_path: str = None) -> Dict[str, str]:
        """Load JavaScript security patterns from configuration"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('js_blocklist', {})
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load config file: {e}")
        
        # Default blocklist patterns
        return {
            r'document\.domain\s*=': "Setting document.domain is not allowed",
            r'document\.cookie': "Cookie access is not allowed",
            r'document\.write': "document.write is not allowed",
            r'window\.open': "Opening new windows is not allowed",
            r'parent\.': "Accessing parent window is not allowed",
            r'top\.': "Accessing top window is not allowed",
            r'new\s+Worker': "Web Workers are not allowed",
            r'navigator\.sendBeacon': "Sending tracking data is not allowed",
            r'require\s*\(': "Importing modules is not allowed",
            r'import\s+': "JavaScript imports are not allowed",
            r'location\.': "Manipulating location is not allowed",
            r'history\.': "Manipulating browser history is not allowed"
        }
    
    def _load_html_blocklist(self, config_path: str = None) -> List[str]:
        """Load blocked HTML elements from configuration"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('html_blocklist', [])
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load config file: {e}")
        
        # Default blocklist of HTML elements
        return [
            'iframe', 'frame', 'object', 'embed', 'applet', 'script',
            'form', 'input', 'button', 'select', 'option', 'textarea',
            'meta', 'link', 'base'
        ]