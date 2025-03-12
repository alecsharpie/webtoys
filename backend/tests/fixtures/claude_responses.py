"""
Mock Claude API responses for testing
"""

from typing import Dict, Any


def simple_webtoy_response() -> Dict[str, Any]:
    """
    A simple mock response from Claude API for a basic WebToy
    """
    return {
        "content": [
            {
                "type": "text",
                "text": """I've created a simple bouncing ball animation for you. Here's the code:

```json
{
  "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
  "css": "body { margin: 0; overflow: hidden; background: #f0f0f0; }",
  "js": "const canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\nlet x = 250;\nlet y = 250;\nlet dx = 3;\nlet dy = 2;\nlet radius = 20;\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  \n  ctx.beginPath();\n  ctx.arc(x, y, radius, 0, Math.PI * 2);\n  ctx.fillStyle = 'blue';\n  ctx.fill();\n  ctx.closePath();\n  \n  x += dx;\n  y += dy;\n  \n  if (x + radius > canvas.width || x - radius < 0) {\n    dx = -dx;\n  }\n  \n  if (y + radius > canvas.height || y - radius < 0) {\n    dy = -dy;\n  }\n  \n  requestAnimationFrame(draw);\n}\n\ndraw();"
}
```

This creates a simple animation with a blue ball that bounces around the canvas. The ball changes direction when it hits any of the edges."""
            }
        ],
        "id": "msg_01abcdef1234567890",
        "model": "claude-3-opus-20240229",
        "role": "assistant",
        "type": "message"
    }


def complex_webtoy_response() -> Dict[str, Any]:
    """
    A more complex mock response from Claude API for a WebToy with controls
    """
    return {
        "content": [
            {
                "type": "text",
                "text": """I've created an interactive particle system simulation for you. Here's the code:

```json
{
  "html": "<canvas id='canvas' width='800' height='600'></canvas>\\n<div id='controls'>\\n  <label>Particles: <span id='particleCount'>100</span></label>\\n  <input type='range' id='particleSlider' min='10' max='500' value='100'>\\n</div>",
  "css": "body { margin: 0; padding: 0; overflow: hidden; background: #111; }\\n\\ncanvas { display: block; margin: 0 auto; }\\n\\n#controls { position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; color: white; }\\n\\ninput[type='range'] { width: 100px; margin-left: 10px; }",
  "js": "const canvas = document.getElementById('canvas');\\nconst ctx = canvas.getContext('2d');\\nconst particleSlider = document.getElementById('particleSlider');\\nconst particleCount = document.getElementById('particleCount');\\n\\nlet particles = [];\\nlet particleNum = 100;\\n\\nfunction initParticles() {\\n  particles = [];\\n  for (let i = 0; i < particleNum; i++) {\\n    particles.push({\\n      x: Math.random() * canvas.width,\\n      y: Math.random() * canvas.height,\\n      size: Math.random() * 5 + 1,\\n      color: 'hsl(' + Math.random() * 360 + ', 100%, 50%)',\\n      speedX: Math.random() * 6 - 3,\\n      speedY: Math.random() * 6 - 3\\n    });\\n  }\\n}\\n\\nfunction updateParticles() {\\n  for (let i = 0; i < particles.length; i++) {\\n    const p = particles[i];\\n    \\n    p.x += p.speedX;\\n    p.y += p.speedY;\\n    \\n    if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;\\n    if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;\\n    \\n    ctx.beginPath();\\n    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);\\n    ctx.fillStyle = p.color;\\n    ctx.fill();\\n    \\n    for (let j = i + 1; j < particles.length; j++) {\\n      const p2 = particles[j];\\n      const dx = p.x - p2.x;\\n      const dy = p.y - p2.y;\\n      const distance = Math.sqrt(dx * dx + dy * dy);\\n      \\n      if (distance < 100) {\\n        ctx.beginPath();\\n        ctx.strokeStyle = 'rgba(255,255,255,' + (1 - distance/100) * 0.5 + ')';\\n        ctx.lineWidth = 1;\\n        ctx.moveTo(p.x, p.y);\\n        ctx.lineTo(p2.x, p2.y);\\n        ctx.stroke();\\n      }\\n    }\\n  }\\n}\\n\\nfunction animate() {\\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\\n  updateParticles();\\n  requestAnimationFrame(animate);\\n}\\n\\nparticleSlider.addEventListener('input', () => {\\n  particleNum = parseInt(particleSlider.value);\\n  particleCount.textContent = particleNum;\\n  initParticles();\\n});\\n\\ninitParticles();\\nanimate();"
}
```

This creates an interactive particle system with colorful particles that bounce around and form connections with nearby particles. You can adjust the number of particles using the slider control at the bottom of the screen."
            }
        ],
        "id": "msg_02abcdef1234567890",
        "model": "claude-3-opus-20240229",
        "role": "assistant",
        "type": "message"
    }


def invalid_syntax_response() -> Dict[str, Any]:
    """
    A mock Claude API response with invalid JSON syntax
    """
    return {
        "content": [
            {
                "type": "text",
                "text": """I've created a simple animation for you:

```json
{
  "html": "<canvas id='myCanvas' width='500' height='500'></canvas>",
  "css": "body { margin: 0; background: #f0f0f0; }",
  "js": "const canvas = document.getElementById('myCanvas');
  const ctx = canvas.getContext('2d');
  
  function draw() {
    // This has invalid syntax - missing closing brace
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'blue';
    ctx.fillRect(50, 50, 100, 100;
    
    requestAnimationFrame(draw);
  }
  
  draw();"
}
```

This creates a simple blue square animation."""
            }
        ],
        "id": "msg_03abcdef1234567890",
        "model": "claude-3-opus-20240229",
        "role": "assistant",
        "type": "message"
    }


def malformed_response() -> Dict[str, Any]:
    """
    A malformed response that doesn't contain JSON code block
    """
    return {
        "content": [
            {
                "type": "text",
                "text": """I'm sorry, but I'm not able to create the animation you requested. 
The specific effect you're asking for would require external libraries or APIs that aren't available in this sandbox environment.

Instead, I could create something similar using just standard Canvas API functions. Would you like me to try a different approach?"""
            }
        ],
        "id": "msg_04abcdef1234567890",
        "model": "claude-3-opus-20240229",
        "role": "assistant",
        "type": "message"
    }