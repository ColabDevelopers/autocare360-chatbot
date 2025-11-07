"""
Chat service that combines data loading, database queries, and AI generation.
"""
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from data_static import DataLoader
from data_dynamic import DatabaseManager
from model import AIModel

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with RAG capabilities."""

    def __init__(
        self, data_loader: DataLoader, db_manager: DatabaseManager, ai_model: AIModel
    ):
        self.data_loader = data_loader
        self.db_manager = db_manager
        self.ai_model = ai_model

        # Cache static data to avoid reloading on every request
        self._static_data_cache: Optional[str] = None

        # Conversation history per session (in production, use Redis or similar)
        self._conversation_history: Dict[str, List[Dict[str, str]]] = {}

    def process_message(self, message: str, session_id: str = "default") -> str:
        """
        Process a user message and generate a response.

        Args:
            message: The user's message
            session_id: Session identifier for conversation history

        Returns:
            str: AI-generated response
        """
        try:
            # Initialize conversation history for new sessions
            if session_id not in self._conversation_history:
                self._conversation_history[session_id] = []

            # Load static data (cached)
            static_context = self._get_static_context()

            # Get dynamic data based on message content
            dynamic_context = self._get_dynamic_context(message)

            # Get conversation history
            conversation_history = self._conversation_history[session_id][
                -5:
            ]  # Last 5 exchanges

            # Build prompt with enhanced context
            prompt = self._build_enhanced_prompt(
                message, static_context, dynamic_context, conversation_history
            )

            # Generate response
            response = self.ai_model.generate_response(prompt, max_tokens=800)

            # Store in conversation history
            self._conversation_history[session_id].append(
                {"role": "user", "content": message}
            )
            self._conversation_history[session_id].append(
                {"role": "assistant", "content": response}
            )

            # Limit history size
            if len(self._conversation_history[session_id]) > 20:
                self._conversation_history[session_id] = self._conversation_history[
                    session_id
                ][-20:]

            logger.info(f"Processed message: {message[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Sorry, I encountered an error while processing your request."

    def _get_static_context(self) -> str:
        """
        Load static context, with optional force reload.
        """
        # For now, always reload to pick up new files (remove caching)
        # In production, add a flag or endpoint to force reload
        self._static_data_cache = self.data_loader.load_all_documents()
        return self._static_data_cache

    def _get_dynamic_context(self, message: str) -> str:
        """
        Extract dynamic data based on message content with enhanced NLP understanding.
        """
        message_lower = message.lower()
        context_parts = []

        # Enhanced date extraction for appointment queries
        if any(
            word in message_lower
            for word in ["appointment", "book", "schedule", "available", "slot", "time"]
        ):
            target_date = self._extract_date_from_message(message_lower)

            if target_date:
                slots_info = self.db_manager.get_available_appointment_slots(
                    target_date
                )
                context_parts.append(
                    f"APPOINTMENT SLOTS FOR {target_date}:\n{slots_info}"
                )
            else:
                # Default to today if no date specified
                today = datetime.now().strftime("%Y-%m-%d")
                slots_info = self.db_manager.get_available_appointment_slots(today)
                context_parts.append(
                    f"APPOINTMENT SLOTS FOR TODAY ({today}):\n{slots_info}"
                )

        # Check for vehicle-specific queries
        if any(
            word in message_lower
            for word in ["vehicle", "car", "history", "service record"]
        ):
            # Look for vehicle ID patterns
            vehicle_id_match = re.search(r"\b([A-Z]{2,6}\d{3,6})\b", message)
            if vehicle_id_match:
                vehicle_id = vehicle_id_match.group(1)
                vehicle_info = self.db_manager.get_vehicle_history(vehicle_id)
                context_parts.append(f"VEHICLE HISTORY:\n{vehicle_info}")

        # Check for service type queries
        service_keywords = [
            "oil",
            "tire",
            "brake",
            "maintenance",
            "repair",
            "inspection",
            "diagnostic",
        ]
        for service in service_keywords:
            if service in message_lower:
                service_info = self.db_manager.search_services_by_type(service)
                context_parts.append(f"SERVICE INFORMATION:\n{service_info}")
                break

        # If no specific query detected, provide general context
        if not context_parts:
            recent_records = self.db_manager.get_recent_service_records()
            if recent_records:
                context_parts.append(f"RECENT SERVICE RECORDS:\n{recent_records}")

        return (
            "\n\n".join(context_parts)
            if context_parts
            else "No specific dynamic data available."
        )

    def _extract_date_from_message(self, message_lower: str) -> Optional[str]:
        """
        Extract date from message with natural language understanding.

        Returns:
            Date string in YYYY-MM-DD format or None
        """
        # Check for relative dates
        if "today" in message_lower:
            return datetime.now().strftime("%Y-%m-%d")
        elif (
            "tomorrow" in message_lower
            or "tommorow" in message_lower
            or "tomorow" in message_lower
        ):
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in message_lower:
            return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        elif "this weekend" in message_lower or "saturday" in message_lower:
            # Find next Saturday
            days_ahead = 5 - datetime.now().weekday()  # 5 = Saturday
            if days_ahead <= 0:
                days_ahead += 7
            return (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        # Check for month names (e.g., "november 12", "December 25th", "jan 15")
        month_names = {
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
        }

        for month_name, month_num in month_names.items():
            # Match patterns like "november 12", "nov 12", "november 12th", "nov 12th"
            pattern = rf"\b{month_name}\s+(\d{{1,2}})(?:st|nd|rd|th)?\b"
            match = re.search(pattern, message_lower)
            if match:
                day = match.group(1).zfill(2)
                current_year = datetime.now().year
                try:
                    # Create date and validate it exists
                    date_str = f"{current_year}-{month_num}-{day}"
                    datetime.strptime(date_str, "%Y-%m-%d")  # Validate date
                    return date_str
                except ValueError:
                    continue  # Invalid date, try next match

        # Check for specific date formats
        # YYYY-MM-DD
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", message_lower)
        if date_match:
            return date_match.group(1)

        # MM/DD/YYYY or DD/MM/YYYY
        date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b", message_lower)
        if date_match:
            date_str = date_match.group(1).replace("/", "-")
            parts = date_str.split("-")
            if len(parts) == 3 and len(parts[2]) == 4:
                try:
                    # Try MM/DD/YYYY format first
                    date_obj = datetime.strptime(date_str, "%m-%d-%Y")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        # Try DD/MM/YYYY format
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                        return date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        pass

        return None

    def _build_enhanced_prompt(
        self,
        message: str,
        static_context: str,
        dynamic_context: str,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """
        Build an enhanced prompt for truly generative AI responses.
        """
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "PREVIOUS CONVERSATION:\n"
            for entry in conversation_history[-6:]:  # Last 3 exchanges
                role = "Customer" if entry["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {entry['content']}\n"
            conversation_context += "\n"

        # Get current date context
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A, %B %d, %Y")
        current_time = now.strftime("%I:%M %p")

        # Enhanced system prompt for generative AI
        system_prompt = f"""You are an intelligent AI assistant for AutoCare, an automobile service center. Your role is to help customers with their vehicle service needs in a natural, conversational, and helpful manner.

CURRENT CONTEXT:
- Today is {current_day}
- Current time: {current_time}
- Date reference: {current_date}

YOUR CAPABILITIES:
1. Answer questions about vehicle maintenance and services
2. Check and provide available appointment slots
3. Retrieve vehicle service history
4. Provide information about different service types
5. Engage in natural, contextual conversations

APPOINTMENT SLOT INTERPRETATION:
- When you see "Available appointment slots for [date]:" followed by time slots, these are OPEN and AVAILABLE times
- Present these slots in a clear, attractive format grouped by morning/afternoon
- If no slots are available, clearly state that and suggest alternatives
- Always be helpful and suggest next steps

COMMUNICATION GUIDELINES:
- Be friendly, professional, and conversational
- Use natural language, not templated responses
- Remember previous messages in this conversation
- When showing appointment slots, format them clearly and attractively
- Interpret date references naturally (today, tomorrow, next week, etc.)
- If information is missing, ask clarifying questions politely
- Personalize responses based on conversation context
- Use emojis occasionally to make responses warmer (🚗, ⏰, ✅, etc.)
- NEVER cut off responses mid-sentence - complete your thoughts fully

{conversation_context}

KNOWLEDGE BASE (Static Information):
{static_context[:20000]}  

DATABASE INFORMATION (Dynamic Real-time Data):
{dynamic_context}

CUSTOMER'S CURRENT MESSAGE: {message}

INSTRUCTIONS:
Generate a natural, helpful, and contextually appropriate response. Be conversational and engaging. Use the database information to provide accurate, real-time data. If showing appointment slots, present them in an easy-to-read format with clear time groupings. Complete your response fully without cutting off."""

        return system_prompt.strip()

    def _build_prompt(
        self, message: str, static_context: str, dynamic_context: str
    ) -> str:
        """
        Legacy prompt builder (kept for backward compatibility).
        """
        return self._build_enhanced_prompt(message, static_context, dynamic_context, [])

    def invalidate_cache(self):
        """Invalidate the static data cache (useful for development)."""
        self._static_data_cache = None
        logger.info("Static data cache invalidated")
