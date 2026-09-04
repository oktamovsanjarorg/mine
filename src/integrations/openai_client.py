import structlog
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from src.config import settings
import io

logger = structlog.get_logger(__name__)

class OpenAIIntegration:
    """Client for OpenAI API."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def chat_completion(self, messages: List[Dict[str, Any]], model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("OpenAI chat_completion failed", error=str(e))
            raise

    async def vision(self, image_bytes: bytes, prompt: str) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        import base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("OpenAI vision failed", error=str(e))
            raise

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.ogg"
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return response.text
        except Exception as e:
            logger.error("OpenAI transcribe_audio failed", error=str(e))
            raise

    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice, # type: ignore
                input=text
            )
            return response.read()
        except Exception as e:
            logger.error("OpenAI text_to_speech failed", error=str(e))
            raise

openai_client = OpenAIIntegration()
