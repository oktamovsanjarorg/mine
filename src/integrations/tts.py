import structlog
import io
import asyncio
from gtts import gTTS

logger = structlog.get_logger(__name__)

class TTSClient:
    """Text-to-speech using gTTS."""

    async def synthesize(self, text: str, lang: str = "uz") -> bytes:
        try:
            # gTTS is blocking, wrap in asyncio.to_thread
            def _generate():
                tts = gTTS(text=text, lang=lang)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()
            
            audio_bytes = await asyncio.to_thread(_generate)
            return audio_bytes
        except Exception as e:
            logger.error("TTS synthesize failed", error=str(e))
            raise

tts_client = TTSClient()
