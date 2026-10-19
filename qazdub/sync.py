import os
import subprocess
from pathlib import Path

def get_audio_duration(file_path: str) -> float:
    """Аудио немесе бейне файлының ұзақтығын (секунд) анықтайды."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def make_silence(duration: float, out_path: str, sample_rate: int = 44100):
    """Берілген ұзақтықтағы бос дыбыс (тыныштық / silence) файлын жасайды."""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r={sample_rate}:cl=stereo",
        "-t", f"{max(0.01, duration):.4f}",
        "-c:a", "pcm_s16le", out_path
    ], capture_output=True, check=True)

def time_stretch_audio(in_path: str, out_path: str, target_duration: float, sample_rate: int = 44100) -> float:
    """
    Аудионы тональдігін өзгертпей (atempo фильтрі арқылы)
    дәл көрсетілген уақыт аралығына созады немесе жылдамдатады.
    """
    actual_duration = get_audio_duration(in_path)
    if target_duration <= 0.05:
        target_duration = 0.05
        
    speed_ratio = actual_duration / target_duration
    # atempo filters only support 0.5 to 2.0 per filter instance
    speed_ratio = max(0.5, min(2.0, speed_ratio))
    
    cmd = [
        "ffmpeg", "-y", "-i", in_path,
        "-filter:a", f"atempo={speed_ratio:.3f}",
        "-ar", str(sample_rate), "-ac", "2",
        "-c:a", "pcm_s16le",
        out_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return get_audio_duration(out_path)

def concatenate_audio_files(file_list: list[str], out_path: str, temp_list_txt: str = "temp/concat.txt"):
    """Аудио сегменттерінің тізімін біртұтас аудиофайлға біріктіреді."""
    os.makedirs(os.path.dirname(os.path.abspath(temp_list_txt)), exist_ok=True)
    with open(temp_list_txt, "w", encoding="utf-8") as f:
        for fpath in file_list:
            abs_p = os.path.abspath(fpath).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
            
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", temp_list_txt,
        "-c:a", "pcm_s16le",
        out_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
