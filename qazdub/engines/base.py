from abc import ABC, abstractmethod

class BaseTTS(ABC):
    """QazDub Studio үшін бірыңғай TTS интерфейсі."""
    
    @abstractmethod
    def synthesize(self, text: str, out_path: str, voice: str | None = None) -> bool:
        """Мәтінді қазақша дыбыстап, out_path файлына сақтайды."""
        pass

    @abstractmethod
    def list_voices(self) -> list[str]:
        """Қолжетімді дауыстар тізімін қайтарады."""
        pass
