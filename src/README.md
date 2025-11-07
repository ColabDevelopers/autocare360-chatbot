# Autocare360 Chatbot - Source Code

This directory contains the source code for the Autocare360 AI-powered chatbot system.

## Project Structure

```
src/
├── config/              # Configuration management
│   └── config.py       # Environment variables and settings
├── data_static/        # Static knowledge base loading
│   └── data_static.py  # Document processing and retrieval
├── data_dynamic/       # Database operations
│   └── data_dynamic.py # MySQL database manager
├── model/              # AI model abstractions
│   └── ai_model.py     # OpenAI, Gemini, Grok implementations
├── services/           # Business logic layer
│   └── chat_service.py # Main chat processing service
└── main/               # Application entry point
    └── main.py         # FastAPI application
```

## Key Components

### Configuration (`config/`)
Handles all application configuration through environment variables. Supports multiple AI providers and database connections.

### Data Management
- **Dynamic Data**: Real-time database queries for appointments and service history
- **Static Data**: Knowledge base from documents (PDF, text, markdown)

### Main Application (`main/`)
FastAPI web application with:
- REST API endpoints
- Web UI with Jinja2 templates
- Health check endpoints

### AI Models (`model/`)
Pluggable architecture supporting:
- OpenAI GPT models
- Google Gemini
- Grok (xAI)
- Mock model for testing

### Services (`services/`)
Business logic layer that orchestrates data retrieval and AI response generation.

## Documentation

For detailed information, see the documentation in the `docs/` folder:

- **[Architecture](../docs/architecture.md)**: Technical architecture and system design

