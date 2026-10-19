import argparse
import sys
import os

if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from qazdub import DubbingPipeline

def main():
    parser = argparse.ArgumentParser(
        description="QazDub Studio: Кез келген бейнені қазақ тіліне автоматты түрде дубляждау құралы."
    )
    parser.add_argument("--video", "-v", required=True, help="Дубляждалатын бастапқы бейне файлы (mp4, mkv, avi)")
    parser.add_argument("--output", "-o", default="output/dubbed_video.mp4", help="Шығарылатын дайын бейне жолы")
    parser.add_argument("--engine", "-e", choices=["issai", "edge", "soniox"], default="issai", help="TTS қозғалтқышы (issai, edge, soniox)")
    parser.add_argument("--voice", help="Таңдалған қозғалтқыштың дауысы (мысалы: iseke, raya, daulet, aigul, Daniel, Emma)")
    parser.add_argument("--subtitles", "-s", help="Егер дайын субтитр файлы (.json) болса, соның жолы")
    parser.add_argument("--bg-music", "-m", help="Егер бөлек фондық музыка (.wav) болса, соның жолы")
    parser.add_argument("--whisper-model", default="base", help="Whisper моделі (tiny, base, small, medium, large)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"[ҚАТЕ] Бейне файлы табылмады: {args.video}")
        sys.exit(1)
        
    print("=" * 60)
    print("🚀 QAZDUB STUDIO: ҚАЗАҚША ДУБЛЯЖ ІСКЕ ҚОСЫЛДЫ")
    print("=" * 60)
    print(f"🎬 Бейне: {args.video}")
    print(f"🎙️ Қозғалтқыш: {args.engine.upper()}")
    print(f"🗣️ Дауыс: {args.voice or 'Әдепкі'}")
    print(f"💾 Шығатын файл: {args.output}")
    print("=" * 60)
    
    pipeline = DubbingPipeline(engine=args.engine, voice=args.voice, whisper_model=args.whisper_model)
    pipeline.process(
        video_path=args.video,
        output_path=args.output,
        subtitles_json=args.subtitles,
        bg_audio_path=args.bg_music
    )

if __name__ == "__main__":
    main()
