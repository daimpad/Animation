# Beitragen zur Animation Pipeline

Danke, dass du beitragen möchtest! 🎬 Diese Anleitung fasst die wichtigsten
Schritte zusammen.

## Entwicklungsumgebung einrichten

```bash
git clone https://github.com/daimpad/Animation.git
cd Animation
pip install -r requirements-dev.txt   # enthält Laufzeit- + Test-Abhängigkeiten
```

Für die optionale LLM-Anbindung lokal [Ollama](https://ollama.com/) installieren:

```bash
ollama pull mistral
```

## Tests ausführen

```bash
pytest -v
```

Alle Tests müssen grün sein, bevor ein Pull Request gemerged wird. Die GitHub
Actions in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) führen die
Testsuite und einen Pipeline-Smoke-Test bei jedem Push und Pull Request aus.

## Projektstruktur (Kurzüberblick)

| Pfad | Zweck |
|------|-------|
| `inputs/prompts/` | Text-Prompts, die eine Animation beschreiben |
| `scripts/` | Pipeline-Skripte (`generate_*`, `validate_json`, `optimize_svg`, `llm`) |
| `outputs/` | Generierte SVG-/Lottie-Dateien (inkl. Beispiele) |
| `preview/` | Browser-Viewer für SVG/Lottie |
| `tests/` | pytest-Tests |
| `docs/` | Dokumentation |

## Richtlinien

- **Stil:** Code an den vorhandenen Skripten orientieren (Type-Hints, kurze
  Docstrings, deutschsprachige Kommentare/Ausgaben).
- **Keine schweren Abhängigkeiten** für Kernfunktionen: Die LLM-Anbindung nutzt
  bewusst nur die Standardbibliothek (`urllib`). Neue Abhängigkeiten gehören in
  `requirements.txt` (Laufzeit) bzw. `requirements-dev.txt` (Entwicklung) und
  sollten begründet sein.
- **Tests:** Neue Funktionen mit Tests absichern – inklusive der Fehlerfälle.
- **Fallback bewahren:** Die Skripte müssen auch ohne erreichbares LLM
  funktionieren (Platzhalter-Ausgabe).

## Neuen Prompt / neue Animation hinzufügen

1. Prompt-Datei in `inputs/prompts/<name>.txt` anlegen.
2. Lokal generieren und prüfen:
   ```bash
   python scripts/generate_svg.py inputs/prompts/<name>.txt outputs/svg/<name>.svg
   python scripts/generate_lottie.py inputs/prompts/<name>.txt outputs/lottie/<name>.json
   python scripts/validate_json.py outputs/lottie/<name>.json
   ```
3. Ergebnis in `preview/index.html` ansehen.
4. Wird der Prompt nach `main` gepusht, erzeugt der Workflow
   [`generate.yml`](.github/workflows/generate.yml) die Outputs automatisch.

## Pull Requests

- Branch von `main` abzweigen, Änderungen committen, PR mit klarer Beschreibung
  öffnen.
- Sicherstellen, dass CI grün ist.

## Lizenz

Mit deinem Beitrag stimmst du zu, dass er unter der
[MIT-Lizenz](LICENSE) veröffentlicht wird.
