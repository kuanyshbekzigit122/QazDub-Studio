import os
import sys
import time
import uuid
import random
import json
import re
from urllib.parse import quote
from curl_cffi import requests
from .base import BaseTTS

class SonioxEngine(BaseTTS):
    """
    Soniox қызметі негізіндегі қазақша TTS модулі.
    Ер адам (Daniel) және әйел адам (Emma т.б.) дауыстары қолжетімді.
    """
    VOICES = {
        "female": ["Emma", "Isla", "Arabella", "Freya", "Grace", "Harper", "Hazel", "Iris", "Lucia", "Mina", "Nora", "Piper", "Reese", "Ruby", "Sloane", "Victoria"],
        "male": ["Daniel", "Adrian", "Arthur", "Bennett", "Cooper", "Dominic", "Elliot", "Emerson", "Evan", "Logan", "Mason", "Mateo", "Miles", "Nathan", "Oliver", "Owen", "Sebastian", "Silas", "Wesley"]
    }

    def __init__(self, cookie_file: str = "temp/soniox_cookies.json", default_voice: str = "Daniel"):
        self.cookie_file = cookie_file
        self.default_voice = default_voice
        self._init_session()

    def _init_session(self):
        cert_path = r"C:\piper_espeak\cacert.pem" if (sys.platform == "win32" and os.path.exists(r"C:\piper_espeak\cacert.pem")) else True
        self.session = requests.Session(impersonate="chrome124", verify=cert_path)
        
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                if cookies and isinstance(cookies, dict):
                    self.session.cookies.update(cookies)
                    return
            except Exception:
                pass
                
        # Generate fresh cookies
        now = int(time.time())
        rand_id = random.randint(100000000, 999999999)
        device_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        current_ts = int(time.time() * 1000)
        
        posthog_data = {
            "$device_id": device_id,
            "distinct_id": device_id,
            "$sesid": [current_ts, session_id, current_ts],
            "$initial_person_info": {"r": "$direct", "u": "https://soniox.com/text-to-speech"},
            "$user_state": "anonymous"
        }
        
        generated_cookies = {
            "_ga": f"GA1.1.{rand_id}.{now}",
            "_gcl_au": f"1.1.{random.randint(100000000, 999999999)}.{now}",
            "ph_phc_E9iQnU37rxu5s5zEKzcN3DiutrWifYRwcwR4axY3SwK_posthog": quote(json.dumps(posthog_data, separators=(',', ':')))
        }
        self.session.cookies.update(generated_cookies)
        os.makedirs(os.path.dirname(os.path.abspath(self.cookie_file)), exist_ok=True)
        try:
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(dict(self.session.cookies.get_dict()), f, ensure_ascii=False)
        except Exception:
            pass

    def _speak_chunk(self, chunk: str, voice: str) -> bytes | None:
        url = "https://soniox.com/api/text-to-speech"
        params = {"text": chunk, "language": "kk", "voice": voice}
        headers = {
            "accept": "*/*",
            "accept-language": "ru,kk;q=0.9,en;q=0.8",
            "referer": "https://soniox.com/text-to-speech",
            "sec-fetch-dest": "audio",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "same-origin",
        }
        resp = self.session.get(url, params=params, headers=headers)
        return resp.content if resp.status_code == 200 else None

    def synthesize(self, text: str, out_path: str, voice: str | None = None) -> bool:
        v = voice if voice else self.default_voice
        # Split text into chunks if longer than 200 chars
        chunks = [text.strip()] if len(text.strip()) <= 200 else [s.strip() for s in re.split(r'([.!?\n]+)', text) if s.strip()]
        
        combined_audio = bytearray()
        for chunk in chunks:
            data = self._speak_chunk(chunk, v)
            if data:
                combined_audio.extend(data)
            else:
                return False
                
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(combined_audio)
        return os.path.exists(out_path) and os.path.getsize(out_path) > 0

    def list_voices(self) -> list[str]:
        return [f"male: {', '.join(self.VOICES['male'][:5])}...", f"female: {', '.join(self.VOICES['female'][:5])}..."]
