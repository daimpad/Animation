# Pipeline Guide

## 1. Prompt erstellen
- Erstelle eine `.txt`-Datei in `inputs/prompts/` mit einer klaren Beschreibung der gewünschten Animation.
- Beispiel:
  ```plaintext
  Erstelle eine SVG-Animation: Ein Kreis bewegt sich von links nach rechts.
  ```

## 2. LLM nutzen
- Nutze ein LLM (z. B. Ollama mit Mistral-7B), um aus dem Prompt SVG- oder Lottie-JSON-Code zu generieren.
- Beispiel-Prompt für Ollama:
  ```bash
  ollama run mistral "Erstelle eine SVG-Animation für: [Deine Beschreibung hier einfügen]. Gib den SVG-Code direkt aus."
  ```

## 3. Skript ausführen
- Speichere die LLM-Ausgabe in einer Datei (z. B. `inputs/templates/animation.svg`).
- Führe das passende Skript aus:
  ```bash
  python scripts/generate_svg.py
  ```

## 4. Validieren & Optimieren
- Validieren:
  ```bash
  python scripts/validate_json.py outputs/lottie/animation.json
  ```
- Optimieren:
  ```bash
  python scripts/optimize_svg.py outputs/svg/animation.svg
  ```

## 5. Manuell bearbeiten (optional)
- **SVG:** Öffne die Datei in [Inkscape](https://inkscape.org/).
- **Lottie:** Bearbeite die Datei im [LottieFiles Editor](https://lottiefiles.com/).
