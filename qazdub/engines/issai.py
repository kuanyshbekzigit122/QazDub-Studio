import os
import sys
import json
import wave
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download
from piper import PiperVoice
from piper.config import SynthesisConfig
from .base import BaseTTS

class ISSAIEngine(BaseTTS):
    """
    Назарбаев Университетінің ISSAI (Institute of Smart Systems and Artificial Intelligence)
    жобасы негізіндегі оффлайн студиялық қазақша TTS моделі.
    """
    REPO_ID = "speaches-ai/piper-kk_KZ-issai-high"
    
    VOICE_MAP = {
        "m2": 0,
        "iseke": 1,
        "m1": 1,
        "f3": 2,
        "raya": 3,
        "f1": 3,
        "f1_alt": 4,
        "f2": 5
    }

    def __init__(self, model_dir: str = "models/issai_piper"):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "model.onnx")
        self.config_path = os.path.join(model_dir, "model.onnx.json")
        self._ensure_model()
        self._setup_espeak()
        self.voice = PiperVoice.load(
            self.model_path,
            config_path=self.config_path,
            espeak_data_dir=self.espeak_dir
        )

    def _ensure_model(self):
        os.makedirs(self.model_dir, exist_ok=True)
        if not os.path.exists(self.model_path):
            print(f"[ISSAI] Модельді Hugging Face ({self.REPO_ID}) сервисінен жүктеу...")
            m = hf_hub_download(repo_id=self.REPO_ID, filename="model.onnx", local_dir=self.model_dir)
            c = hf_hub_download(repo_id=self.REPO_ID, filename="config.json", local_dir=self.model_dir)
            shutil.copyfile(c, self.config_path)
        elif not os.path.exists(self.config_path):
            cfg_orig = os.path.join(self.model_dir, "config.json")
            if os.path.exists(cfg_orig):
                shutil.copyfile(cfg_orig, self.config_path)

    def _setup_espeak(self):
        # Windows-та кириллица жолдарында libespeak ақауы болмас үшін ASCII жолына бағыттаймыз
        if sys.platform == "win32":
            dst = Path(r"C:\piper_espeak\espeak-ng-data")
            if dst.exists():
                self.espeak_dir = str(dst)
                return
            try:
                import piper
                site_pkg = Path(piper.__file__).parent / "espeak-ng-data"
                if site_pkg.exists():
                    os.makedirs(r"C:\piper_espeak", exist_ok=True)
                    shutil.copytree(site_pkg, dst)
                    self.espeak_dir = str(dst)
                    return
            except Exception:
                pass
        self.espeak_dir = None

    def synthesize(self, text: str, out_path: str, voice: str | None = "iseke") -> bool:
        spk_id = self.VOICE_MAP.get(str(voice).lower(), 1)
        syn_config = SynthesisConfig(speaker_id=spk_id)
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with wave.open(out_path, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file, syn_config=syn_config)
        return os.path.exists(out_path)

    def list_voices(self) -> list[str]:
        return ["iseke (ер адам дауысы, M1)", "raya (әйел адам дауысы, F1)", "m2", "f3", "f2"]
