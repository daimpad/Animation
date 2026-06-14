# Beispiele

Diese Seite sammelt Beispiel-Prompts und die dazugehörigen erwarteten Ausgaben.

## Beispiel 1: Kreis zu Spirale (SVG)

**Prompt** (`inputs/prompts/circle_to_spiral.txt`):
```plaintext
Erstelle eine SVG-Animation:
- Ein Kreis (Radius: 50px, Position: 100,100) verwandelt sich in eine Spirale (3 Umdrehungen).
- Farbe wechselt von Blau (#0000FF) zu Rot (#FF0000).
- Dauer: 3 Sekunden, 60 FPS.
- Exportiere als SVG.
```

**Erzeugen:**
```bash
python scripts/generate_svg.py
```

**Ausgabe:** `outputs/svg/circle_to_spiral.svg`

---

## Beispiel 2: Farb-Morph (Lottie)

**Prompt** (`inputs/prompts/color_morph.txt`):
```plaintext
Erstelle eine Lottie-Animation:
- Ein Quadrat (100x100px, Position: 50,50) ändert die Farbe von Grün (#00FF00) zu Gelb (#FFFF00).
- Gleichzeitig rotiert es um 360 Grad.
- Dauer: 2 Sekunden, 60 FPS.
- Exportiere als Lottie-JSON.
```

**Erzeugen:**
```bash
python scripts/generate_lottie.py
```

**Ausgabe:** `outputs/lottie/circle_to_spiral.json`

**Validieren:**
```bash
python scripts/validate_json.py outputs/lottie/circle_to_spiral.json
```
