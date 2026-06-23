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

### 2a. Ohne LLM: Animationen aus einer Spec (Vorlagen)
Für **einfache Standardanimationen** (bewegen, drehen, skalieren/pulsieren,
Farbe wechseln, ein-/ausblenden) brauchst du kein LLM. Beschreibe die Animation
in einer kleinen YAML- oder JSON-**Spec** und erzeuge daraus deterministisch
valides SVG bzw. Lottie:

```yaml
# inputs/specs/bounce.yaml
format: svg
duration: 2
shape: { type: circle, size: 30, color: "#3498db", position: [40, 100] }
animations:
  - { type: move,  to: [160, 100] }
  - { type: scale, to: 1.6 }
  - { type: color, to: "#e74c3c" }
```

```bash
python scripts/generate_from_spec.py inputs/specs/bounce.yaml outputs/svg/bounce.svg
python scripts/generate_from_spec.py inputs/specs/spinner.json outputs/lottie/spinner.json
```

**Animationstypen:** `move`, `rotate`, `scale`, `color`, `fade` (beliebig
kombinierbar). **Formen:** `circle`, `rect`. Das Ausgabeformat ergibt sich aus
`format:` in der Spec oder aus der Dateiendung (`.svg`/`.json`). Die Bausteine
stecken in [`scripts/templates.py`](scripts/templates.py).

### 2a-CLI: Komfortables Kommandozeilen-Tool
Statt Skripte einzeln aufzurufen, bündelt das **CLI** (`scripts/cli.py`, auf Basis
von [Typer](https://typer.tiangolo.com/)) Erstellen, Validieren und Optimieren:

```bash
# Animation aus Parametern (ohne LLM)
python scripts/cli.py new --shape circle --position 20,100 --move 180,100 \
    --color-to "#ff0000" --duration 3 -o outputs/svg/demo.svg

# aus einer Spec-Datei
python scripts/cli.py from-spec inputs/specs/bounce.yaml -o outputs/svg/bounce.svg

# validieren / optimieren
python scripts/cli.py validate outputs/lottie/spinner.json
python scripts/cli.py optimize outputs/svg/bounce.svg

python scripts/cli.py --help   # alle Befehle/Optionen
```

`new` unterstützt die Animationen `--move x,y`, `--rotate GRAD`, `--scale FAKTOR`,
`--color-to HEX`, `--fade DECKKRAFT` (kombinierbar) für `--shape circle|rect`.

### 2b. LLM generiert Code
Die `generate_*`-Skripte sprechen automatisch ein **lokales Ollama** an: Sie lesen den
Prompt aus der Datei, schicken ihn an das Modell und extrahieren den SVG- bzw.
Lottie-Code aus der Antwort. Ist Ollama **nicht erreichbar** (oder liefert keine
verwertbare Ausgabe), wird transparent auf eine Platzhalter-Ausgabe zurückgegriffen –
die Pipeline läuft also auch ohne LLM durch.

Konfiguration über Umgebungsvariablen:

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `OLLAMA_URL` | `http://localhost:11434` | Basis-URL des Ollama-Servers |
| `OLLAMA_MODEL` | `mistral` | Zu verwendendes Modell |

```bash
# Beispiel: anderes Modell verwenden
OLLAMA_MODEL=llama3 python scripts/generate_svg.py inputs/prompts/circle_to_spiral.txt outputs/svg/circle_to_spiral.svg
```

Alternativ kannst du das LLM auch manuell ansprechen und die Ausgabe selbst ablegen:
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

### 5. Vorschau im Browser
Im Ordner `preview/` liegt ein eigenständiger Viewer (`index.html`), der SVG- und
Lottie-Animationen rendert (Lottie via `lottie-web` vom CDN).

- **Schnell:** `preview/index.html` direkt im Browser öffnen und eine `.svg`- oder
  `.json`-Datei wählen bzw. per Drag & Drop ablegen.
- **Mit Pfad-Laden:** Repo lokal ausliefern und `/preview/` öffnen, dann lassen sich
  Dateien direkt über ihren Pfad laden:
  ```bash
  python -m http.server 8000
  # -> http://localhost:8000/preview/
  ```
  (Der direkte `file://`-Aufruf kann das Laden per Pfad aus Sicherheitsgründen
  blockieren; die Datei-Auswahl funktioniert aber immer.)

### 6. Manuell bearbeiten (optional)
- **SVG:** Öffne die Datei in [Inkscape](https://inkscape.org/).
- **Lottie:** Bearbeite die Datei im [LottieFiles Editor](https://lottiefiles.com/).

---

## 📂 Verzeichnisstruktur
```
animation-pipeline/
├── inputs/               # Eingabedateien
│   ├── prompts/          # Textdateien mit Animation-Beschreibungen
│   ├── specs/            # YAML/JSON-Specs für Vorlagen-Animationen (ohne LLM)
│   └── templates/        # Vorlagen für SVG/Lottie
├── scripts/              # Python-Skripte
│   ├── cli.py            # Kommandozeilen-Tool (Typer): new/from-spec/validate/optimize
│   ├── templates.py      # Parametrische Vorlagen (SVG/Lottie, ohne LLM)
│   ├── generate_from_spec.py  # Animation aus einer Spec erzeugen
│   ├── llm.py            # Optionale Ollama-Anbindung (nur stdlib)
│   ├── generate_svg.py
│   ├── generate_lottie.py
│   ├── validate_json.py
│   └── optimize_svg.py
├── tests/                # pytest-Tests
│   └── test_pipeline.py
├── preview/              # Browser-Viewer für SVG/Lottie
│   └── index.html
├── pages/                # Galerie/Landing-Seite für GitHub Pages
│   └── index.html
├── outputs/              # Generierte Animationen
│   ├── svg/
│   └── lottie/
├── docs/                 # Dokumentation
│   ├── pipeline_guide.md
│   └── examples.md
├── .github/workflows/    # CI- und Generate-Workflows
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

---

## 🌐 Live-Demo (GitHub Pages)

Eine Galerie mit den Beispiel-Animationen und dem interaktiven Viewer wird per
GitHub Actions auf GitHub Pages veröffentlicht:

**➡️ https://daimpad.github.io/Animation/** (Galerie) ·
**https://daimpad.github.io/Animation/builder.html** (No-Code-Builder) ·
**https://daimpad.github.io/Animation/preview/** (Viewer)

Der **No-Code-Builder** (`pages/builder.html`) erzeugt einfache SVG-Animationen
per Formular (Form, Farbe, Bewegung, Drehung, Skalierung, Farbwechsel,
Ausblenden), zeigt eine Live-Vorschau, bietet **SVG-Download** und gibt die
passende **YAML-Spec** aus – die SVG-Logik ist identisch zu `scripts/templates.py`
(per Test abgesichert).

Die Galerie zeigt die SVG-Animation direkt eingebettet und rendert das
Lottie-Beispiel über `lottie-web`.

> **Aktivierung:** Der Workflow [`pages.yml`](.github/workflows/pages.yml)
> aktiviert GitHub Pages automatisch (`configure-pages` mit `enablement: true`)
> und deployt bei jedem Push auf `main`. Sollte das in deiner Org durch
> Richtlinien unterbunden sein, Pages einmalig manuell aktivieren:
> **Settings → Pages → Build and deployment → Source: „GitHub Actions"**.

---

## 🤖 Automatisierung (GitHub Actions)

Das Repository enthält folgende Workflows unter `.github/workflows/`:

- **`ci.yml`** – führt bei jedem Push/PR die pytest-Suite und einen Pipeline-Smoke-Test aus.
- **`generate.yml`** – wird ausgelöst, sobald Dateien in `inputs/prompts/` geändert werden. Er generiert für jeden Prompt automatisch SVG/Lottie, validiert/optimiert die Ergebnisse und committet sie zurück nach `outputs/`.
- **`pages.yml`** – deployt die Galerie + Viewer auf GitHub Pages (Push auf `main`).

> Hinweis: Für `generate.yml` werden Schreibrechte benötigt. Diese sind im Workflow über `permissions: contents: write` gesetzt; alternativ unter **Settings → Actions → General → Workflow permissions** *Read and write permissions* aktivieren.

---

## 🔗 Nützliche Links
- [Lottie-Web](https://github.com/airbnb/lottie-web) (für Lottie-Animationen)
- [Inkscape](https://inkscape.org/) (für SVG-Bearbeitung)
- [Ollama](https://ollama.com/) (für lokale LLM-Nutzung)
- [SVGOMG](https://jakearchibald.github.io/svgomg/) (für SVG-Optimierung)

---

## 🤝 Beitragen
Beiträge sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Setup,
Tests und Richtlinien.

## 📄 Lizenz
Veröffentlicht unter der [MIT-Lizenz](LICENSE).
