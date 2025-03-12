# WebToys

Create and share interactive HTML5 Canvas experiments with AI.

## About

WebToys is a platform that allows you to create interactive canvas-based web "toys" by simply describing what you want. Using AI, WebToys generates the code for you, runs it in a secure sandbox, and provides a shareable link to your creation.

## Features

- **AI-powered creation**: Just describe what you want, and AI will generate the code
- **Secure sandbox**: All WebToys run in a secure environment
- **Shareable links**: Share your creations with a simple URL
- **No coding required**: Create interactive web experiments without writing code

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Anthropic API key](https://www.anthropic.com/) for Claude AI

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/webtoys.git
cd webtoys
```

2. **Set up environment variables**

Edit the `backend/.env` file:

```
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-opus-20240229
```

3. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

4. **Access the application**

Open your browser and go to:
```
http://localhost:8000
```

## Local Development Setup (without Docker)

If you prefer to run without Docker:

1. **Set up a Python environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the backend**

```bash
uvicorn main:app --reload
```

3. **Access the application**

Open your browser and go to:
```
http://localhost:8000
```

## Production Deployment

For production deployment, consider these additional steps:

1. **Use a production-ready server**
   - Replace the default Uvicorn server with Gunicorn + Uvicorn workers

2. **Set up a reverse proxy**
   - Use Nginx or Traefik in front of the application

3. **Configure SSL**
   - Set up SSL certificates (Let's Encrypt)

4. **Set proper security headers**
   - Content Security Policy
   - X-Frame-Options
   - X-Content-Type-Options

5. **Regular backups**
   - Set up automated backups of the WebToys database

## Project Structure

```
webtoys/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py          # Claude API integration
│   │   ├── validator.py           # Code validation and sanitization
│   │   └── storage.py             # Storage service
│   └── static/                    # Frontend static files
│       ├── index.html             # Main page
│       ├── styles.css             # CSS styles
│       ├── app.js                 # Frontend logic
│       └── sandbox.js             # WebToy sandbox implementation
├── docker-compose.yml             # For local development
└── README.md                      # Project documentation
```

## Security Considerations

WebToys implements multiple layers of security:

1. **Server-side validation**: All generated code is checked for security issues
2. **Sandboxed execution**: WebToys run in restricted iframes
3. **Content Security Policy**: Strict CSP rules to prevent external resources
4. **Isolated execution**: Each WebToy runs in its own isolated environment

## License

This project is licensed under the MIT License - see the LICENSE file for details.

##