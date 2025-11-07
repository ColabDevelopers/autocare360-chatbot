"""
Main entry point for the chatbot application.
"""
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from data_static import DataLoader
from data_dynamic import DatabaseManager
from model import AIModelFactory
from services import ChatService


def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("chatbot.log")
            if not Config.DEBUG
            else logging.NullHandler(),
        ],
    )


def create_app():
    """Create and configure the FastAPI application."""
    import logging

    logger = logging.getLogger(__name__)

    from fastapi import FastAPI, Request, Form, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.templating import Jinja2Templates
    from fastapi.staticfiles import StaticFiles

    # Validate configuration
    missing_config = Config.validate()
    if missing_config:
        raise ValueError(f"Missing required configuration: {', '.join(missing_config)}")

    # Initialize components
    data_loader = DataLoader(Config.STATIC_DATA_DIR)
    db_manager = DatabaseManager(
        Config.MYSQL_HOST,
        Config.MYSQL_USER,
        Config.MYSQL_PASSWORD,
        Config.MYSQL_DATABASE,
    )
    # Initialize AI model based on configuration
    if Config.AI_PROVIDER == "openai":
        ai_model = AIModelFactory.create_model(
            Config.AI_PROVIDER,
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            max_tokens=Config.OPENAI_MAX_TOKENS,
        )
        logger.info(f"Initialized OpenAI model: {Config.OPENAI_MODEL}")
    elif Config.AI_PROVIDER == "gemini":
        ai_model = AIModelFactory.create_model(
            Config.AI_PROVIDER, api_key=Config.GEMINI_API_KEY, model=Config.GEMINI_MODEL
        )
        logger.info(f"Initialized Gemini model: {Config.GEMINI_MODEL}")
    elif Config.AI_PROVIDER == "grok":
        ai_model = AIModelFactory.create_model(
            Config.AI_PROVIDER, api_key=Config.GROK_API_KEY, model=Config.GROK_MODEL
        )
        logger.info(f"Initialized Grok model: {Config.GROK_MODEL}")
    else:
        # Default to mock for unknown providers
        ai_model = AIModelFactory.create_model("mock")
        logger.warning(
            "Using mock AI model. Set AI_PROVIDER and API key for production use."
        )
    chat_service = ChatService(data_loader, db_manager, ai_model)

    # Create FastAPI app
    app = FastAPI(
        title="Autocare AI Chatbot",
        description="RAG-powered chatbot for automotive maintenance",
        version="2.0.0",
    )

    # Mount static files
    # app.mount("/static", StaticFiles(directory="static"), name="static")

    # Templates
    templates = Jinja2Templates(directory="chatbot")

    @app.get("/", response_class=HTMLResponse)
    async def chat_ui(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.post("/chat")
    async def chat(message: str = Form(...), session_id: str = Form(default="default")):
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        try:
            response = chat_service.process_message(message.strip(), session_id)
            return {"response": response}
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Chat endpoint error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "ai_available": ai_model.is_available(),
            "config_valid": len(missing_config) == 0,
        }

    @app.post("/invalidate-cache")
    async def invalidate_cache():
        """Invalidate static data cache (development endpoint)."""
        chat_service.invalidate_cache()
        return {"message": "Cache invalidated"}

    return app


def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        import uvicorn

        logger.info("Starting chatbot server...")
        if Config.DEBUG:
            # For reload, run uvicorn with import string
            import sys
            import os

            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            uvicorn.run(
                "src.main.main:create_app", host="0.0.0.0", port=8000, reload=True
            )
        else:
            app = create_app()
            uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
