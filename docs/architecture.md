# Technical Architecture

## Overview

The Autocare360 Chatbot is a RAG (Retrieval-Augmented Generation) powered conversational AI system designed for automotive maintenance and service inquiries. Built with FastAPI and supporting multiple AI providers.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   FastAPI App   │    │   AI Providers  │
│                 │    │                 │    │                 │
│  ┌────────────┐ │    │  ┌────────────┐ │    │  ┌────────────┐ │
│  │   HTML UI  │◄┼────┼─►│  Chat API  │◄┼────┼─►│  OpenAI    │ │
│  └────────────┘ │    │  └────────────┘ │    │  ├────────────┤ │
└─────────────────┘    └─────────────────┘    │  │  Gemini    │ │
                                              │  ├────────────┤ │
                                              │  │   Grok     │ │
                                              │  └────────────┘ │
                                              └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Static Data    │    │  Vector Store   │    │  MySQL Database│
│  (Documents)    │    │  (Embeddings)   │    │  (Dynamic Data) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Web Layer (FastAPI)

**Main Entry Point:** `src/main/main.py`
- FastAPI application setup
- Route definitions for chat and health endpoints
- Jinja2 templating for HTML UI
- Static file serving

**Key Endpoints:**
- `GET /`: Chat interface
- `POST /chat`: Process chat messages
- `GET /health`: System health check
- `POST /invalidate-cache`: Clear data cache

### 2. Configuration Management

**File:** `src/config/config.py`
- Environment variable loading
- Configuration validation
- Support for multiple AI providers
- Database connection settings

### 3. AI Model Abstraction

**File:** `src/model/ai_model.py`
- Abstract base class for AI providers
- Concrete implementations for OpenAI, Gemini, Grok
- Mock model for testing
- Factory pattern for model creation

**Supported Providers:**
- **OpenAI GPT**: gpt-3.5-turbo, gpt-4, etc.
- **Google Gemini**: gemini-pro, gemini-pro-vision
- **Grok (xAI)**: grok-beta
- **Mock**: For development/testing

### 4. Data Management

#### Static Data Loader (`src/data_static/data_static.py`)
- Loads documents from files (.txt, .md, .json, .pdf)
- Text preprocessing and chunking
- In-memory caching

#### Dynamic Database Manager (`src/data_dynamic/data_dynamic.py`)
- MySQL database connectivity
- Query execution for real-time data
- Appointment and service data management

### 5. Chat Service

**File:** `src/services/chat_service.py`
- Orchestrates the conversation flow
- Combines static knowledge with dynamic data
- Context-aware response generation
- Session management

## Data Flow

### Chat Request Processing

1. **User Input** → FastAPI endpoint receives message
2. **Preprocessing** → Input validation and sanitization
3. **Context Retrieval** → Query static docs + database
4. **AI Generation** → Send context + prompt to AI model
5. **Response** → Return formatted response to user

### Detailed Flow:

```
User Message
    ↓
Input Validation
    ↓
ChatService.process_message()
    ↓
├── DataLoader.get_relevant_context()
│   └── File-based knowledge retrieval
    ↓
├── DatabaseManager.query_data()
│   └── Real-time data queries
    ↓
Context Combination
    ↓
AIModel.generate_response()
    ↓
Response Formatting
    ↓
Return to User
```