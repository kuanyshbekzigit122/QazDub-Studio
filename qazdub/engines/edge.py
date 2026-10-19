import os
import asyncio
from .base import BaseTTS

try:
    import edge_tts
except ImportError:
    edge_tts = None

class EdgeTTSEngine(BaseTTS):
    """
    Microsoft Edge-TTS бұлтты тегін қазақша дауыстары (Дәулет және Айгүл).
    Өте жылдам, сервер қуатын қажет етпейді, табиғи интонация.
    """
    VOICE_MAP = {
        "daulet": "kk-KZ-DauletNeural",
        "male": "kk-KZ-DauletNeural",
        "aigul": "kk-KZ-AigulNeural",
        "female": "kk-KZ-AigulNeural",
    }

    def __init__(self, default_voice: str = "daulet"):
        self.default_voice = self.VOICE_MAP.get(default_voice.lower(), "kk-KZ-DauletNeural")

    async def _synth_async(self, text: str, out_path: str, voice_name: str):
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(out_path)

    def synthesize(self, text: str, out_path: str, voice: str | None = None) -> bool:
        if edge_tts is None:
            raise ImportError("Edge-TTS қолдану үшін 'pip install edge-tts' орнатыңыз.")
        v = self.VOICE_MAP.get(str(voice).lower(), self.default_voice) if voice else self.default_voice
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        try:
            asyncio.run(self._synth_async(text, out_path, v))
            return os.path.exists(out_path)
        except Exception as e:
            print(f"[Edge-TTS Қатесі]: {e}")
            return False

    def list_voices(self) -> list[str]:
        return ["daulet (ер адам, kk-KZ-DauletNeural)", "aigul (әйел адам, kk-KZ-AigulNeural)"]
