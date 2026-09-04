import structlog
import google.generativeai as genai
from typing import List, Dict, Any
from src.config import settings

logger = structlog.get_logger(__name__)

class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")
        self.vision_model = genai.GenerativeModel("gemini-pro-vision")

    async def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.7) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text
        except Exception as e:
            logger.error("Gemini generate_text failed", error=str(e))
            raise

    async def generate_with_history(self, messages: List[Dict[str, Any]], system_prompt: str = "") -> str:
        try:
            history = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            chat = self.model.start_chat(history=history)
            response = await chat.send_message_async(system_prompt) # Simplistic approach
            return response.text
        except Exception as e:
            logger.error("Gemini generate_with_history failed", error=str(e))
            raise

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        try:
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ]
            response = await self.vision_model.generate_content_async([prompt, image_parts[0]])
            return response.text
        except Exception as e:
            logger.error("Gemini analyze_image failed", error=str(e))
            raise

    async def count_tokens(self, text: str) -> int:
        try:
            response = await self.model.count_tokens_async(text)
            return response.total_tokens
        except Exception as e:
            logger.error("Gemini count_tokens failed", error=str(e))
            return len(text) // 4  # Fallback approximation

gemini_client = GeminiClient()
