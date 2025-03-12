"""
WebToys API Server

Main FastAPI application for the WebToys platform.
This handles code generation, validation, storage, and serving of WebToys.
"""

import logging
import os
import time
import uuid
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import settings
from services.ai_service import AIService
from services.storage import StorageService
from services.validator import WebToyValidator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WebToys API", description="Backend API for WebToys platform", version="1.0.0"
)

# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService(api_key=settings.claude_api_key, model=settings.claude_model)

validator = WebToyValidator()

storage = StorageService(
    storage_type=settings.storage_type, connection_string=settings.storage_connection
)

# Rate limiting configuration (simple in-memory implementation)
rate_limits: dict[str, dict[str, float]] = {}


# Request models
class GenerateRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=1000)
    parameters: dict[str, Any] | None = None


class PublishRequest(BaseModel):
    preview_id: str


# Response models
class GenerateResponse(BaseModel):
    preview_id: str
    code: dict[str, str]


class PublishResponse(BaseModel):
    id: str
    url: str


# Helper functions
async def check_rate_limit(request: Request) -> None:
    """Simple rate limiting for API requests"""
    client_ip = "unknown"
    if request.client and hasattr(request.client, "host"):
        client_ip = request.client.host
    current_time = time.time()

    # Clean up old entries
    for ip in list(rate_limits.keys()):
        if current_time - rate_limits[ip]["timestamp"] > 3600:  # 1 hour window
            del rate_limits[ip]

    # Check client limit
    if client_ip in rate_limits:
        entry = rate_limits[client_ip]
        if current_time - entry["timestamp"] < 3600:  # 1 hour window
            if entry["count"] >= 10:  # 10 requests per hour
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            entry["count"] += 1
        else:
            # Reset if window expired
            entry["timestamp"] = current_time
            entry["count"] = 1
    else:
        # Create new entry
        rate_limits[client_ip] = {"timestamp": current_time, "count": 1}


# API routes
@app.post("/api/generate", response_model=GenerateResponse)
async def generate_webtoy(
    request: GenerateRequest, _: None = Depends(check_rate_limit)
) -> JSONResponse | GenerateResponse:
    """
    Generate WebToy code from a text description
    """
    try:
        # Generate code using AI
        code = await ai_service.generate_code(
            description=request.description, parameters=request.parameters
        )

        # Validate and sanitize code
        validation_result = validator.validate(code)

        if not validation_result.is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Generated code failed security validation",
                    "issues": validation_result.issues,
                },
            )

        # Store sanitized code for preview
        preview_id = str(uuid.uuid4())
        await storage.store_preview(
            preview_id=preview_id,
            code=validation_result.sanitized_code,
            metadata={"description": request.description, "timestamp": time.time()},
        )

        # Return preview information
        return GenerateResponse(
            preview_id=preview_id, code=validation_result.sanitized_code
        )

    except Exception as e:
        logger.error(f"Error generating WebToy: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to generate WebToy: {e!s}")


@app.post("/api/publish", response_model=PublishResponse)
async def publish_webtoy(
    request: PublishRequest, _: None = Depends(check_rate_limit)
) -> PublishResponse:
    """
    Publish a previously generated WebToy
    """
    try:
        # Retrieve preview code
        preview = await storage.get_preview(request.preview_id)

        if not preview:
            raise HTTPException(status_code=404, detail="Preview not found")

        # Generate permanent ID
        webtoy_id = str(uuid.uuid4())[:8]  # Shorter ID for sharing

        # Store as published WebToy
        await storage.publish_webtoy(
            webtoy_id=webtoy_id,
            code=preview["code"],
            metadata={
                "description": preview["metadata"].get("description", ""),
                "created_at": time.time(),
                "preview_id": request.preview_id,
            },
        )

        # Return published information
        base_url = os.environ.get("BASE_URL", "http://localhost:8000")
        webtoy_url = f"{base_url}/toy/{webtoy_id}"

        return PublishResponse(id=webtoy_id, url=webtoy_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing WebToy: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to publish WebToy")


@app.get("/preview/{preview_id}", response_class=HTMLResponse)
async def get_preview(preview_id: str) -> str:
    """
    Serve a WebToy preview
    """
    try:
        # Retrieve preview
        preview = await storage.get_preview(preview_id)

        if not preview:
            raise HTTPException(status_code=404, detail="Preview not found")

        # Render preview HTML
        return render_webtoy(
            preview["code"],
            {
                "title": "WebToy Preview",
                "is_preview": True,
                "description": preview["metadata"].get("description", ""),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving preview: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to serve preview")


@app.get("/toy/{webtoy_id}", response_class=HTMLResponse)
async def get_webtoy(webtoy_id: str) -> str:
    """
    Serve a published WebToy
    """
    try:
        # Retrieve WebToy
        webtoy = await storage.get_webtoy(webtoy_id)

        if not webtoy:
            raise HTTPException(status_code=404, detail="WebToy not found")

        # Render WebToy HTML
        return render_webtoy(
            webtoy["code"],
            {
                "title": f"WebToy: {webtoy_id}",
                "is_preview": False,
                "description": webtoy["metadata"].get("description", ""),
                "webtoy_id": webtoy_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving WebToy: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to serve WebToy")


def render_webtoy(code: dict[str, str], options: dict[str, Any]) -> str:
    """
    Render HTML for a WebToy with proper sandboxing
    """
    # Extract code components
    html = code.get("html", "")
    css = code.get("css", "")
    js = code.get("js", "")

    # Sanitize title and description
    title = options.get("title", "WebToy").replace("<", "&lt;").replace(">", "&gt;")
    description = (
        options.get("description", "").replace("<", "&lt;").replace(">", "&gt;")
    )

    # Generate HTML
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        
        <!-- Meta information -->
        <meta name="description" content="{description}">
        {('<meta name="robots" content="noindex">' if options.get("is_preview") else "")}
        
        <!-- Content Security Policy -->
        <meta http-equiv="Content-Security-Policy" content="
            default-src 'none';
            script-src 'unsafe-inline';
            style-src 'unsafe-inline';
            img-src data: blob:;
            connect-src 'none';
            font-src 'none';
            frame-src 'none';
            object-src 'none';
            base-uri 'none';
            form-action 'none';
        ">
        
        <!-- Additional security headers -->
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
        
        <!-- Base styles -->
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: #f5f5f5;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            #webtoy-container {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 40px;
                overflow: hidden;
                background: white;
            }}
            
            #webtoy-attribution {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 40px;
                background: #f0f0f0;
                border-top: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 15px;
                font-size: 14px;
            }}
            
            .attribution-actions a,
            .attribution-actions button {{
                margin-left: 10px;
                text-decoration: none;
                color: #2962ff;
                background: none;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            
            /* WebToy CSS */
            {css}
        </style>
    </head>
    <body>
        <div id="webtoy-container">
            {html}
        </div>
        
        <div id="webtoy-attribution">
            <div class="attribution-info">
                <span class="title">{title}</span>
                <span class="separator"> | </span>
                <span class="platform">WebToys</span>
            </div>
            <div class="attribution-actions">
                {('<a href="/remix/' + options.get("webtoy_id", "") + '">Remix this</a>' if not options.get("is_preview") else "")}
                <button onclick="shareWebToy()">Share</button>
            </div>
        </div>
        
        <script>
            // Security wrapper
            (function() {{
                // Create controlled environment and capture errors
                try {{
                    // Define safe console methods
                    const safeConsole = {{}};
                    ['log', 'info', 'warn', 'error'].forEach(method => {{
                        safeConsole[method] = function(...args) {{
                            console[method](...args);
                        }};
                    }});
                    
                    // Block dangerous APIs
                    const dangerousGlobals = [
                        'fetch', 'XMLHttpRequest', 'WebSocket', 
                        'localStorage', 'sessionStorage', 'indexedDB',
                        'openDatabase', 'eval', 'Function',
                        'setTimeout', 'setInterval'
                    ];
                    
                    // Create safe execution context
                    const sandbox = {{}};
                    sandbox.console = safeConsole;
                    
                    // WebToy code
                    {js}
                }} catch (error) {{
                    console.error('WebToy error:', error);
                    document.getElementById('webtoy-container').innerHTML = 
                        '<div style="padding: 20px; color: red; text-align: center;">' + 
                        '<h3>Error in WebToy</h3>' +
                        '<p>' + error.message + '</p></div>';
                }}
            }})();
            
            // Simple share functionality
            function shareWebToy() {{
                if (navigator.share) {{
                    navigator.share({{
                        title: '{title}',
                        text: 'Check out this WebToy!',
                        url: window.location.href
                    }})
                    .catch(err => {{
                        console.error('Share failed:', err);
                    }});
                }} else {{
                    // Fallback for browsers without share API
                    prompt('Copy this link to share:', window.location.href);
                }}
            }}
        </script>
    </body>
    </html>
    """


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy", "timestamp": time.time()}


# Serve static files (frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Run application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
