import structlog
from src.integrations.openai_client import openai_client

logger = structlog.get_logger(__name__)

class STTClient:
    """Speech-to-text using OpenAI Whisper or Google Speech."""

    async def transcribe(self, audio_bytes: bytes, lang: str = "uz") -> str:
        try:
            # Using OpenAI Whisper as default
            text = await openai_client.transcribe_audio(audio_bytes)
            return text
        except Exception as e:
            logger.error("STT transcribe failed", error=str(e))
            raise

stt_client = STTClient()
