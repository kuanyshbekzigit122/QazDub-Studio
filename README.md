# 🎬 QazDub Studio (Қаздаб Студия)

**QazDub Studio** — кез келген бейнені автоматты түрде түпнұсқа уақытына дәл синхрондап, қазақ тіліне жоғары сапада дубляждауға арналған ашық бастапқы (Open-Source) ЖИ-құралы.

---

## ✨ Негізгі мүмкіндіктері

- 🎯 **Уақытқа дәл синхронизация (Frame-accurate Time-stretching):** Сөйлемдердің түпнұсқа видеоның кадрлары мен кейіпкердің ерін қимылына дәл келуі үшін `FFmpeg atempo` фильтрімен дыбысты созу немесе жылдамдату.
- 🗣️ **3 түрлі қуатты қазақша TTS қозғалтқышы:**
  1. 🏢 **ISSAI KazakhTTS (Офлайн, студиялық сапа):** Назарбаев Университетінің ISSAI институты әзірлеген кәсіби дикторлық дауыстар (`Исеке` ер адам дауысы, `Рая` әйел адам дауысы). Компьютеріңізде GPU-сіз, жеңіл CPU-де лезде жұмыс істейді.
  2. ☁️ **Microsoft Edge-TTS (Бұлтты, тегін):** Тұрақты бұлтты қазақша дауыстар (`Дәулет` және `Айгүл`). Серверге салмақ түсірмейді, интонациясы өте табиғи.
  3. 🎙️ **Soniox TTS (Бұлтты, заманауи):** Ерлер мен әйелдердің қазіргі заманғы көптеген дауыстары (`Daniel`, `Emma` т.б.).
- 🌐 **Кез келген тілден қазақшаға аудару:** Ағылшын, орыс, араб, түрік т.б. тілдердегі бейнелерді автоматты түрде қазақшалайды.
- 🎚️ **Фондық дыбысты сақтау (Audio Ducking):** Түпнұсқадағы фондық музыка немесе атмосфералық дыбыстарды өшірмей, жаңа қазақша дауыстың астында әдемі үндестіріп микширлейді.

---

## 🛠️ Ортаны орнату

### 1. Жүйелік талаптар
Жүйеде **FFmpeg** орнатылған болуы шарт.
```bash
# Windows (winget арқылы):
winget install Gyan.FFmpeg

# Linux (Ubuntu/Debian):
sudo apt update && sudo apt install ffmpeg
```

### 2. Python тәуелділіктерін орнату
```bash
pip install -r requirements.txt
```

---

## 🚀 Қолдану тәсілдері

### А. Командалық жол (CLI) арқылы бір командамен дубляждау:

```bash
# 1. ISSAI «Исеке» ер адам дауысымен дубляждау (әдепкі):
python cli.py --video "video.mp4" --engine issai --voice iseke --output "output/dubbed.mp4"

# 2. ISSAI «Рая» әйел адам дауысымен дубляждау:
python cli.py --video "video.mp4" --engine issai --voice raya --output "output/dubbed.mp4"

# 3. Edge-TTS «Дәулет» дауысымен бұлтты дубляждау:
python cli.py --video "video.mp4" --engine edge --voice daulet --output "output/dubbed.mp4"

# 4. Soniox «Daniel» ер адам дауысымен дубляждау:
python cli.py --video "video.mp4" --engine soniox --voice Daniel --output "output/dubbed.mp4"
```

### Ә. Python коды ішінде қолдану:

```python
from qazdub import DubbingPipeline

# Құбырды қалаған қозғалтқышпен іске қосу
pipeline = DubbingPipeline(engine="issai", voice="iseke")

# Бейнені дубляждау
output_video = pipeline.process(
    video_path="input_video.mp4",
    output_path="output/kazakh_video.mp4"
)
print("Дайын бейне:", output_video)
```

---

## 📁 Жоба құрылымы

```text
QazDub Studio/
├── qazdub/                  # Негізгі модульдер бумасы
│   ├── engines/             # TTS қозғалтқыштары (ISSAI, Edge, Soniox)
│   ├── normalizer.py        # Қазақша сандар мен мәтінді нормализатор
│   ├── sync.py              # Уақытты созу және синхронизация
│   └── pipeline.py          # Бастан-аяқ автоматтандырылған құбыр
├── cli.py                   # Командалық жол интерфейсі
├── requirements.txt         # Қажетті кітапханалар
├── .gitignore               # Артық медиа/модель файлдарын жасыру ережелері
└── README.md                # Жоба құжаттамасы
```

---

## 📄 Лицензия және Алғыс

- **Лицензия:** [MIT License](LICENSE)
- **Модельдер құқығы:**
  - ISSAI KazakhTTS моделі Назарбаев Университетінің [ISSAI](https://issai.nu.edu.kz/) институтына тиесілі.
  - Edge-TTS қызметі Microsoft корпорациясының ашық дауыстық технологиясына негізделген.
  - Soniox қызметі Soniox Speech AI платформасына негізделген.
