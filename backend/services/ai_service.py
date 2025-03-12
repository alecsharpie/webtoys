"""
AI Service for WebToy Generation

This service handles communication with the Claude API to generate WebToy code
based on natural language descriptions.
"""

import logging
import re
from typing import Any

from anthropic.types import (
    TextBlock,
)

# Setup logging
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """
        Initialize the AI service

        Args:
            api_key: Claude API key
            model: Claude model to use
        """
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=api_key)
            self.model = model
            logger.info(f"AI Service initialized with model: {model}")
        except ImportError:
            logger.error(
                "Failed to import Anthropic SDK. Please install with 'pip install anthropic'"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AI Service: {e!s}")
            raise

    async def generate_code(
        self, description: str, parameters: dict[str, Any] | None = None
    ) -> dict[str, str]:
        """
        Generate WebToy code from a description

        Args:
            description: User's description of the desired WebToy
            parameters: Additional parameters like size, colors, complexity

        Returns:
            Dictionary containing HTML, CSS, and JS code
        """
        # Set default parameters if none provided
        if parameters is None:
            parameters = {}

        default_params = {
            "width": 500,
            "height": 500,
            "complexity": "medium",
            "style": "modern",
        }

        # Merge default with provided parameters
        params = {**default_params, **parameters}

        # Generate prompt
        prompt = self._create_prompt(description, params)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system="""You are a creative web developer specializing in interactive HTML5 Canvas toys and visualizations.
                Your goal is to create engaging, visually appealing web toys that run in the browser.
                Always create self-contained code (HTML, CSS, JavaScript) with no external dependencies.
                Focus on creating interactive experiences that respond to user input.
                Use clean, well-commented code that's easy to understand.""",
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content_block = response.content[0]

            # Handle different block types
            if isinstance(content_block, TextBlock):
                return self._parse_response(content_block.text)
            else:
                raise ValueError(
                    f"Unexpected content block type: {type(content_block)}"
                )

        except Exception as e:
            logger.error(f"Claude API error: {e!s}")
            raise RuntimeError(f"AI service error: {e!s}")

    def _create_prompt(self, description: str, parameters: dict[str, Any]) -> str:
        """
        Create a prompt for the AI model

        Args:
            description: User's description
            parameters: WebToy parameters

        Returns:
            Formatted prompt string
        """
        return f"""
        CREATE A WEBTOY WITH THE FOLLOWING DESCRIPTION:
        {description}
        
        PARAMETERS:
        - Canvas Size: {parameters["width"]}x{parameters["height"]}px
        - Complexity Level: {parameters["complexity"]}
        - Visual Style: {parameters["style"]}
        
        REQUIREMENTS:
        1. The code must be entirely self-contained (HTML, CSS, and JavaScript)
        2. Use only the HTML5 Canvas API for visuals - no external libraries or frameworks
        3. Make it interactive - respond to user input (mouse, keyboard, touch)
        4. Optimize for performance - it should run smoothly even on mobile devices
        5. Include clear comments explaining how the code works
        6. Do not include any network requests or external resources
        7. Ensure the code is secure and cannot access browser APIs outside its sandbox
        8. Do not use document.write or eval() for security reasons
        9. Make sure it works on all modern browsers
        
        RESPONSE FORMAT:
        Provide your response in the following format:
        
        <HTML>
        <!-- HTML code here, including the canvas element -->
        </HTML>
        
        <CSS>
        /* CSS code here, including any styles for the canvas and page */
        </CSS>
        
        <JAVASCRIPT>
        // JavaScript code here, including canvas initialization and interaction
        </JAVASCRIPT>
        
        <DESCRIPTION>
        Brief description of the WebToy and how to interact with it
        </DESCRIPTION>
        """

    def _parse_response(self, response_text: str) -> dict[str, str]:
        """
        Parse the AI's response into separate HTML, CSS, and JS components

        Args:
            response_text: Raw text response from the AI

        Returns:
            Dictionary with 'html', 'css', and 'js' keys
        """
        components = {}

        # Extract HTML
        html_match = re.search(r"<HTML>(.*?)</HTML>", response_text, re.DOTALL)
        components["html"] = html_match.group(1).strip() if html_match else ""

        # Extract CSS
        css_match = re.search(r"<CSS>(.*?)</CSS>", response_text, re.DOTALL)
        components["css"] = css_match.group(1).strip() if css_match else ""

        # Extract JavaScript
        js_match = re.search(
            r"<JAVASCRIPT>(.*?)</JAVASCRIPT>", response_text, re.DOTALL
        )
        components["js"] = js_match.group(1).strip() if js_match else ""

        # Extract Description
        desc_match = re.search(
            r"<DESCRIPTION>(.*?)</DESCRIPTION>", response_text, re.DOTALL
        )
        components["description"] = desc_match.group(1).strip() if desc_match else ""

        # Log success or failure
        if all(key in components and components[key] for key in ["html", "css", "js"]):
            logger.info("Successfully extracted code components from AI response")
        else:
            missing = [
                key
                for key in ["html", "css", "js"]
                if key not in components or not components[key]
            ]
            logger.warning(f"Missing or empty code components: {', '.join(missing)}")

            # If missing critical components, provide sensible defaults
            if "html" not in components or not components["html"]:
                components["html"] = (
                    '<canvas id="canvas" width="500" height="500"></canvas>'
                )
            if "css" not in components or not components["css"]:
                components["css"] = "canvas { border: 1px solid #000; }"
            if "js" not in components or not components["js"]:
                components["js"] = "// No JavaScript was generated"

        return components
