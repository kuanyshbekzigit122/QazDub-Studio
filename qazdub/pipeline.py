import os
import sys
import json
import subprocess
from deep_translator import GoogleTranslator
import whisper

from .normalizer import normalize_kazakh_text
from .sync import get_audio_duration, make_silence, time_stretch_audio, concatenate_audio_files
from .engines import ISSAIEngine, EdgeTTSEngine, SonioxEngine, BaseTTS

class DubbingPipeline:
    """
    QazDub Studio толық автоматтандырылған дубляж құбыры.
    """
    def __init__(self, engine: str = "issai", voice: str | None = None, whisper_model: str = "base"):
        self.engine_name = engine.lower()
        self.voice = voice
        self.whisper_model_name = whisper_model
        
        if self.engine_name == "issai":
            self.tts: BaseTTS = ISSAIEngine()
        elif self.engine_name == "edge":
            self.tts: BaseTTS = EdgeTTSEngine()
        elif self.engine_name == "soniox":
            self.tts: BaseTTS = SonioxEngine()
        else:
            raise ValueError(f"Белгісіз TTS қозғалтқышы: {engine}. 'issai', 'edge', немесе 'soniox' таңдаңыз.")
            
        self.translator = GoogleTranslator(source='auto', target='kk')
        self._whisper = None

    def _get_whisper(self):
        if self._whisper is None:
            print(f"[Whisper] '{self.whisper_model_name}' моделін жүктеу...")
            self._whisper = whisper.load_model(self.whisper_model_name)
        return self._whisper

    def transcribe(self, audio_path: str) -> list[dict]:
        """Аудионы танып, уақыт белгілері бар сегменттерге бөледі."""
        print(f"[Whisper] Аудио транскрипциялануда...")
        model = self._get_whisper()
        res = model.transcribe(audio_path)
        segments = []
        for s in res.get("segments", []):
            segments.append({
                "id": s["id"],
                "start": float(s["start"]),
                "end": float(s["end"]),
                "text": s["text"].strip()
            })
        print(f"[Whisper] {len(segments)} сөйлеу сегменті табылды.")
        return segments

    def process(
        self,
        video_path: str,
        output_path: str,
        subtitles_json: str | None = None,
        bg_audio_path: str | None = None,
        custom_dictionary: dict[int, str] | None = None,
        orig_volume: float = 0.10,
        voice_volume: float = 1.35
    ):
        """
        Бейнені бастан-аяқ қазақшаға дубляждайды:
        Транскрипция -> Аудару -> Қазақша TTS -> Синхронизация -> Микширлеу.
        """
        os.makedirs("temp/segments", exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        total_video_duration = get_audio_duration(video_path)
        print(f"🎬 Бейне ұзақтығы: {total_video_duration:.2f} сек")
        
        # 1. Сегменттерді анықтау немесе жүктеу
        if subtitles_json and os.path.exists(subtitles_json):
            print(f"[Субтитр] Дайын файлдан жүктелуде: {subtitles_json}")
            with open(subtitles_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            segments = data.get("segments", [])
        else:
            extracted_audio = "temp/extracted_audio.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path,
                "-vn", "-ar", "16000", "-ac", "1",
                "-c:a", "pcm_s16le", extracted_audio
            ], capture_output=True, check=True)
            segments = self.transcribe(extracted_audio)
            
        if not segments:
            raise RuntimeError("Дыбысталатын сөйлеу сегменттері табылмады!")

        # 2. Аудару, дыбыстау және синхрондау
        concat_list = []
        current_time = 0.0
        
        print(f"\n🎙️ Қазақ тіліне синтездеу (Қозғалтқыш: {self.engine_name.upper()}, Дауыс: {self.voice or 'әдепкі'})...")
        for idx, seg in enumerate(segments):
            seg_id = seg["id"]
            start = seg["start"]
            end = seg["end"]
            target_duration = max(0.2, end - start)
            orig_text = seg["text"]
            
            # Қазақшаға аудару (сөздік немесе Google Translator)
            if custom_dictionary and seg_id in custom_dictionary:
                kk_text = custom_dictionary[seg_id]
            else:
                try:
                    kk_text = self.translator.translate(orig_text)
                except Exception:
                    kk_text = orig_text
                    
            normalized_kk = normalize_kazakh_text(kk_text)
            
            # Арасындағы бос орынға тыныштық (silence) қосу
            if start > current_time + 0.02:
                gap = start - current_time
                silence_file = f"temp/segments/gap_{idx}.wav"
                make_silence(gap, silence_file)
                concat_list.append(silence_file)
                current_time = start
                
            # TTS арқылы дыбыстау
            raw_audio = f"temp/segments/seg_{seg_id}_raw.wav"
            self.tts.synthesize(normalized_kk, raw_audio, voice=self.voice)
            
            # FFmpeg atempo арқылы уақытқа дәл сыйғызу
            timed_audio = f"temp/segments/seg_{seg_id}_timed.wav"
            timed_dur = time_stretch_audio(raw_audio, timed_audio, target_duration)
            
            concat_list.append(timed_audio)
            current_time += timed_dur
            print(f"[{start:05.2f}s -> {end:05.2f}s] Seg {idx+1:02d} | '{normalized_kk}'")

        # Соңындағы бос орынды толтыру
        if total_video_duration > current_time + 0.02:
            rem = total_video_duration - current_time
            end_gap = "temp/segments/gap_end.wav"
            make_silence(rem, end_gap)
            concat_list.append(end_gap)

        # 3. Барлық сегменттерді біріктіру
        full_vocals = "temp/full_kazakh_vocals.wav"
        concatenate_audio_files(concat_list, full_vocals)
        print(f"\n✅ Қазақша вокалдық жол дайын: {full_vocals} ({get_audio_duration(full_vocals):.2f}s)")

        # 4. Фондық дыбыспен немесе бейнемен біріктіру (Muxing)
        print("\n🎛️ Бейнемен біріктіру және дыбысты микширлеу (FFmpeg)...")
        if bg_audio_path and os.path.exists(bg_audio_path):
            audio_input = bg_audio_path
        else:
            audio_input = video_path

        cmd_final = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", full_vocals,
            "-filter_complex",
            f"[0:a]volume={orig_volume:.2f}[orig];[1:a]volume={voice_volume:.2f}[vox];[orig][vox]amix=inputs=2:duration=first:dropout_transition=0:weights=1.0 1.5[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd_final, capture_output=True, check=True)
        print(f"\n🎉 МҮЛТІКСІЗ ДАЙЫН БОЛДЫ: {output_path}")
        return output_path
