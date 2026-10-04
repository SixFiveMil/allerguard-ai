import base64
import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.core.sentry_tracing import AgentSpan

logger = logging.getLogger("allerguard.elevenlabs")

class ElevenLabsTool:
    """
    Hands-free voice accessibility tool powered by ElevenLabs.
    Converts critical safety alerts into spoken audio for grocery shopping and cooking.
    """

    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id

    async def generate_speech(self, text: str) -> Dict[str, Any]:
        """Converts concise clinical summary to speech audio."""
        # Shorten text to key safety takeaways for audio
        summary_text = text[:300] if len(text) > 300 else text

        with AgentSpan("elevenlabs.tts", "ElevenLabs speech generation", {"voice_id": self.voice_id}) as span:
            if self.api_key:
                try:
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                    headers = {
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": summary_text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.post(url, json=payload, headers=headers)
                        # If voice ID is restricted on free tier, retry with default premade voice (George: JBFqnCBsd6RMkjVDRZzb)
                        if resp.status_code == 402 or (resp.status_code == 400 and "voice" in resp.text.lower()):
                            fallback_url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb"
                            resp = await client.post(fallback_url, json=payload, headers=headers)

                        if resp.status_code == 200:
                            audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                            span.data["status"] = "success"
                            span.data["audio_bytes"] = len(resp.content)
                            return {
                                "available": True,
                                "engine": "ElevenLabs Neural Voice Synthesis",
                                "audio_base64": f"data:audio/mp3;base64,{audio_b64}",
                                "text": summary_text
                            }
                except Exception as e:
                    logger.warning(f"ElevenLabs TTS failed: {e}. Falling back to browser audio.")

            span.data["engine"] = "Browser SpeechSynthesis Native Audio"
            return {
                "available": True,
                "engine": "Browser SpeechSynthesis Native Audio (Offline Capable)",
                "audio_base64": None,
                "text": summary_text
            }

elevenlabs_tool = ElevenLabsTool()
