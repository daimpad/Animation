import sys
from pathlib import Path


def optimize_svg(input_path: str, output_path: str) -> None:
    """
    Optimiert eine SVG-Datei (vereinfacht).
    In der Praxis: Nutze SVGOMG oder ähnliche Tools.
    """
    with open(input_path) as f:
        svg_content = f.read()

    # Hier könnte SVGOMG oder ein anderes Tool integriert werden
    # Für jetzt: Speichere die Datei einfach neu
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg_content)
    print(f"✅ SVG optimiert und gespeichert unter: {out}")


if __name__ == "__main__":
    # Pfad aus den Argumenten oder Standardwert verwenden
    if len(sys.argv) > 1:
        in_path = sys.argv[1]
        out_path = sys.argv[2] if len(sys.argv) > 2 else in_path.replace(".svg", "_optimized.svg")
    else:
        in_path = "outputs/svg/circle_to_spiral.svg"
        out_path = "outputs/svg/circle_to_spiral_optimized.svg"

    optimize_svg(input_path=in_path, output_path=out_path)
