"""
QazDub Studio: Автоматты түрде бейнелерді қазақ тіліне дубляждау жүйесі.
Қолдау көрсетілетін қозғалтқыштар: ISSAI KazakhTTS, Edge-TTS, Soniox.
"""

from .pipeline import DubbingPipeline
from .engines import ISSAIEngine, EdgeTTSEngine, SonioxEngine

__version__ = "1.0.0"
__all__ = ["DubbingPipeline", "ISSAIEngine", "EdgeTTSEngine", "SonioxEngine"]
