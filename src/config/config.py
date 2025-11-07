"""
Configuration management for the chatbot application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # AI Provider Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai").lower()

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))

    # Google Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")

    # Grok (xAI) Configuration
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-beta")

    # Database Configuration
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Configuration
    STATIC_DATA_DIR: str = os.getenv("STATIC_DATA_DIR", "data")
    SUPPORTED_EXTENSIONS: list = [".txt", ".md", ".json", ".pdf"]

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration and return list of missing items."""
        missing = []

        # Check AI provider API key
        if cls.AI_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        elif cls.AI_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        elif cls.AI_PROVIDER == "grok" and not cls.GROK_API_KEY:
            missing.append("GROK_API_KEY")

        # Check database configuration
        if not cls.MYSQL_USER:
            missing.append("MYSQL_USER")
        if not cls.MYSQL_PASSWORD:
            missing.append("MYSQL_PASSWORD")
        return missing
