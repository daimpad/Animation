# 🎬 Animation Pipeline mit LLM & Open-Source-Tools

Eine **halbautomatische Pipeline** zur Erstellung von **Lottie- und SVG-Animationen** aus Textbeschreibungen mit Large Language Models (LLMs) und Open-Source-Tools.

---

## 🛠 Setup

### 1. Repository klonen
```bash
git clone https://github.com/dein-benutzername/animation-pipeline.git
cd animation-pipeline
```

### 2. Python-Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Lokales LLM einrichten (optional)
Installiere [Ollama](https://ollama.com/) und lade ein LLM herunter (z. B. Mistral-7B):
```bash
ollama pull mistral
```

---

## 🚀 Nutzung

### 1. Prompt erstellen
Erstelle eine Textdatei in `inputs/prompts/` mit einer Beschreibung deiner Animation.

Beispiel (`inputs/prompts/circle_to_spiral.txt`):
```plaintext
Erstelle eine SVG-Animation:
- Ein Kreis (Radius: 50px, Position: 100,100) verwandelt sich in eine Spirale (3 Umdrehungen).
- Farbe wechselt von Blau (#0000FF) zu Rot (#FF0000).
- Dauer: 3 Sekunden, 60 FPS.
- Exportiere als SVG.
```

### 2. LLM generiert Code
Füttere den Prompt in dein LLM (z. B. Ollama) und speichere die Ausgabe in `inputs/templates/` oder direkt in `outputs/`.

Beispiel-Prompt für Ollama:
```bash
ollama run mistral "Erstelle eine SVG-Animation für folgende Beschreibung: Ein Kreis (Radius: 50px, Position: 100,100) verwandelt sich in eine Spirale (3 Umdrehungen). Farbe wechselt von Blau (#0000FF) zu Rot (#FF0000). Dauer: 3 Sekunden. Gib den SVG-Code direkt aus."
```

### 3. Skript ausführen
Führe das passende Skript aus, um die Animation zu generieren:
```bash
# Für SVG
python scripts/generate_svg.py

# Für Lottie
python scripts/generate_lottie.py
```

### 4. Validieren & Optimieren
```bash
# Lottie-JSON validieren
python scripts/validate_json.py outputs/lottie/circle_to_spiral.json

# SVG optimieren
python scripts/optimize_svg.py outputs/svg/circle_to_spiral.svg
```

### 5. Manuell bearbeiten (optional)
- **SVG:** Öffne die Datei in [Inkscape](https://inkscape.org/).
- **Lottie:** Bearbeite die Datei im [LottieFiles Editor](https://lottiefiles.com/).

---

## 📂 Verzeichnisstruktur
```
animation-pipeline/
├── inputs/               # Eingabedateien
│   ├── prompts/          # Textdateien mit Animation-Beschreibungen
│   └── templates/        # Vorlagen für SVG/Lottie
├── scripts/              # Python-Skripte
│   ├── generate_svg.py
│   ├── generate_lottie.py
│   ├── validate_json.py
│   └── optimize_svg.py
├── outputs/              # Generierte Animationen
│   ├── svg/
│   └── lottie/
├── docs/                 # Dokumentation
│   ├── pipeline_guide.md
│   └── examples.md
├── README.md
└── requirements.txt
```

---

## 🔗 Nützliche Links
- [Lottie-Web](https://github.com/airbnb/lottie-web) (für Lottie-Animationen)
- [Inkscape](https://inkscape.org/) (für SVG-Bearbeitung)
- [Ollama](https://ollama.com/) (für lokale LLM-Nutzung)
- [SVGOMG](https://jakearchibald.github.io/svgomg/) (für SVG-Optimierung)
