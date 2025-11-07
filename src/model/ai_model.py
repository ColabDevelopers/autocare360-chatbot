"""
AI model abstraction for pluggable AI providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AIModel(ABC):
    """Abstract base class for AI model providers."""

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the AI model."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI model is available and configured."""
        pass


class OpenAIModel(AIModel):
    """OpenAI GPT model implementation."""

    def __init__(
        self, api_key: str, model: str = "gpt-3.5-turbo", max_tokens: int = 500
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.client = None

        if api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=api_key)
            except ImportError:
                logger.error("OpenAI package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        if not self.client:
            return "AI model not available. Please configure your OpenAI API key."

        try:
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            temperature = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return (
                content.strip()
                if content
                else "I apologize, but I couldn't generate a response. Please try again."
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"I apologize, but I'm having trouble connecting to my AI service right now. Please try again in a moment."

    def is_available(self) -> bool:
        """Check if OpenAI is configured and available."""
        return self.client is not None and bool(self.api_key)


class GeminiModel(AIModel):
    """Google Gemini AI model implementation."""

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self.client = None

        if api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model)
            except ImportError:
                logger.error("google-generativeai package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Google Gemini API."""
        if not self.client:
            return "AI model not available. Please configure your Gemini API key."

        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 800)

            from google.generativeai.types import GenerationConfig

            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = self.client.generate_content(
                prompt, generation_config=generation_config
            )

            # Handle complex responses with multiple parts
            try:
                return response.text.strip()
            except AttributeError:
                # If response has multiple parts, concatenate them
                if hasattr(response, "parts") and response.parts:
                    text_parts = []
                    for part in response.parts:
                        if hasattr(part, "text"):
                            text_parts.append(part.text)
                    return " ".join(text_parts).strip()
                elif hasattr(response, "candidates") and response.candidates:
                    text_parts = []
                    for candidate in response.candidates:
                        if hasattr(candidate, "content") and hasattr(
                            candidate.content, "parts"
                        ):
                            for part in candidate.content.parts:
                                if hasattr(part, "text"):
                                    text_parts.append(part.text)
                    return " ".join(text_parts).strip()
                else:
                    return str(response).strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"I apologize, but I'm having trouble connecting to my AI service right now. Please try again in a moment."

    def is_available(self) -> bool:
        """Check if Gemini is configured and available."""
        return self.client is not None and bool(self.api_key)


class GrokModel(AIModel):
    """Grok (xAI) model implementation."""

    def __init__(self, api_key: str, model: str = "grok-beta"):
        self.api_key = api_key
        self.model = model
        self.client = None

        if api_key:
            try:
                from openai import OpenAI

                # Grok uses OpenAI-compatible API
                self.client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Grok client: {e}")

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Grok API."""
        if not self.client:
            return "AI model not available. Please configure your Grok API key."

        try:
            max_tokens = kwargs.get("max_tokens", 800)
            temperature = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return (
                content.strip()
                if content
                else "I apologize, but I couldn't generate a response. Please try again."
            )
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return f"I apologize, but I'm having trouble connecting to my AI service right now. Please try again in a moment."

    def is_available(self) -> bool:
        """Check if Grok is configured and available."""
        return self.client is not None and bool(self.api_key)


class MockAIModel(AIModel):
    """Mock AI model for testing and development."""

    def __init__(self):
        pass

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Return a mock response that simulates a real AI."""
        import re
        from datetime import datetime

        # Simple keyword-based responses for demonstration
        prompt_lower = prompt.lower()

        if (
            "appointment" in prompt_lower
            or "slot" in prompt_lower
            or "available" in prompt_lower
        ):
            # Try to extract date from the prompt/dynamic context
            date_display = "Today (November 6th, 2025)"  # default

            # Look for date patterns in the prompt
            # Check for APPOINTMENT SLOTS FOR YYYY-MM-DD pattern
            date_match = re.search(r"APPOINTMENT SLOTS FOR (\d{4}-\d{2}-\d{2})", prompt)
            if date_match:
                date_str = date_match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    date_display = date_obj.strftime("%A, %B %d, %Y")
                except ValueError:
                    pass

            return f"""Certainly! I can help you with appointment slots. Based on my database, here are the available times:

**{date_display}:**

🌅 **Morning Slots:**
• 9:00 AM - 9:30 AM
• 10:00 AM - 10:30 AM
• 11:30 AM - 12:00 PM

🌞 **Afternoon Slots:**
• 1:30 PM - 2:00 PM
• 3:00 PM - 3:30 PM
• 4:30 PM - 5:00 PM

Would any of these times work for you? I can also check availability for other dates if you'd like! 😊"""

        elif "hi" in prompt_lower or "hello" in prompt_lower or "hey" in prompt_lower:
            return "Hi there! 👋 Welcome to AutoCare! How can I assist you today with your vehicle service needs?"

        elif "tomorrow" in prompt_lower:
            return """I'd be happy to check tomorrow's availability for you!

**Tomorrow (November 7th, 2025):**

🌅 **Morning Slots:**
• 8:30 AM - 9:00 AM
• 9:30 AM - 10:00 AM
• 10:30 AM - 11:00 AM
• 11:30 AM - 12:00 PM

🌞 **Afternoon Slots:**
• 1:00 PM - 1:30 PM
• 2:00 PM - 2:30 PM
• 3:30 PM - 4:00 PM
• 4:00 PM - 4:30 PM

Let me know which time works best for you, and I'll help you book it! 🚗"""

        else:
            return f"I understand you're asking about: {prompt[:100]}... This is a mock AI response. In production, a real AI model (OpenAI GPT, Google Gemini, or Grok) would provide intelligent, context-aware responses based on your autocare knowledge base and real-time database information."

    def is_available(self) -> bool:
        """Mock model is always available."""
        return True


class AIModelFactory:
    """Factory for creating AI model instances."""

    @staticmethod
    def create_model(provider: str = "openai", **kwargs) -> AIModel:
        """
        Create an AI model instance.

        Args:
            provider: The AI provider ('openai', 'gemini', 'grok', 'mock')
            **kwargs: Provider-specific configuration

        Returns:
            AIModel: Configured AI model instance
        """
        provider = provider.lower()

        if provider == "openai":
            return OpenAIModel(
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "gpt-3.5-turbo"),
                max_tokens=kwargs.get("max_tokens", 200),
            )
        elif provider == "gemini":
            return GeminiModel(
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "gemini-pro"),
            )
        elif provider == "grok":
            return GrokModel(
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "grok-beta"),
            )
        elif provider == "mock":
            return MockAIModel()
        else:
            logger.warning(f"Unknown AI provider: {provider}, using mock")
            return MockAIModel()
