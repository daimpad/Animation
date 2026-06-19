# Beispiele

Diese Seite verlinkt die mitgelieferten **Referenz-Animationen** im Ordner
`outputs/` und zeigt, wie sie aus den Prompts in `inputs/prompts/` entstehen.

> Hinweis: Ohne erreichbares LLM erzeugen die Skripte eine generische
> Platzhalter-Ausgabe. Die hier eingecheckten Dateien sind kuratierte
> Beispiel-Outputs, die exakt zu den jeweiligen Prompts passen – damit
> `outputs/` nicht leer ist und die [Browser-Vorschau](../preview/index.html)
> direkt etwas zeigt.

---

## Beispiel 1: Kreis zu Spirale (SVG)

- **Prompt:** [`inputs/prompts/circle_to_spiral.txt`](../inputs/prompts/circle_to_spiral.txt)
- **Output:** [`outputs/svg/circle_to_spiral.svg`](../outputs/svg/circle_to_spiral.svg)
  (optimiert: [`circle_to_spiral_optimized.svg`](../outputs/svg/circle_to_spiral_optimized.svg))

Eine echte Archimedische Spirale (3 Umdrehungen) wird per
`stroke-dashoffset` „gezeichnet", während die Farbe zwischen Blau (`#0000FF`)
und Rot (`#FF0000`) wechselt – Dauer 3 s, in Endlosschleife.

```bash
# So wurde die Pipeline für diesen Prompt aufgerufen:
python scripts/generate_svg.py inputs/prompts/circle_to_spiral.txt outputs/svg/circle_to_spiral.svg
python scripts/optimize_svg.py outputs/svg/circle_to_spiral.svg outputs/svg/circle_to_spiral_optimized.svg
```

---

## Beispiel 2: Farb-Morph (Lottie)

- **Prompt:** [`inputs/prompts/color_morph.txt`](../inputs/prompts/color_morph.txt)
- **Output:** [`outputs/lottie/color_morph.json`](../outputs/lottie/color_morph.json)

Ein Quadrat (100×100 px) rotiert in 2 s (60 FPS → 120 Frames) um 360° und
morpht dabei seine Füllfarbe von Grün (`#00FF00`) zu Gelb (`#FFFF00`).

```bash
python scripts/generate_lottie.py inputs/prompts/color_morph.txt outputs/lottie/color_morph.json
python scripts/validate_json.py outputs/lottie/color_morph.json
```

---

## Anschauen

Öffne [`preview/index.html`](../preview/index.html) im Browser und lade eine der
Dateien (Datei-Auswahl, Drag & Drop oder – bei lokalem Server – per Pfad).
Für das Pfad-Laden:

```bash
python -m http.server 8000
# -> http://localhost:8000/preview/
```
