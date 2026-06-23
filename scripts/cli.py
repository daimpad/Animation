"""Animation Pipeline – Kommandozeilen-Tool (Typer).

Beispiele:
    # Animation aus Parametern erzeugen (ohne LLM):
    python scripts/cli.py new --shape circle --position 20,100 --move 180,100 \\
        --color-to "#ff0000" --duration 3 -o outputs/svg/demo.svg

    # Aus einer Spec-Datei:
    python scripts/cli.py from-spec inputs/specs/bounce.yaml -o outputs/svg/bounce.svg

    # Lottie validieren / SVG optimieren:
    python scripts/cli.py validate outputs/lottie/spinner.json
    python scripts/cli.py optimize outputs/svg/bounce.svg
"""
from pathlib import Path
import base64
import mimetypes
import sys

import typer

# scripts/ in den Importpfad
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_from_spec as gfs  # noqa: E402
import validate_json as vj  # noqa: E402
import optimize_svg as osvg  # noqa: E402

app = typer.Typer(
    add_completion=False,
    help="Animation Pipeline – einfache SVG/Lottie-Animationen erstellen, validieren, optimieren.",
)


# --------------------------------------------------------------------------- #
# Parser-Hilfen
# --------------------------------------------------------------------------- #
def _xy(value: str) -> list[float]:
    """'120,80' -> [120.0, 80.0]"""
    parts = value.replace(" ", "").split(",")
    if len(parts) != 2:
        raise typer.BadParameter(f"Erwarte 'x,y', bekam: {value!r}")
    return [float(parts[0]), float(parts[1])]


def _size(value: str):
    """'40' -> 40.0 ; '80x60' -> [80.0, 60.0]"""
    if "x" in value.lower():
        w, h = value.lower().split("x", 1)
        return [float(w), float(h)]
    return float(value)


def _data_url(path: Path) -> str:
    """Liest eine Bilddatei und bettet sie als Data-URL ein (self-contained SVG)."""
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = Path(path).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


# --------------------------------------------------------------------------- #
# Befehle
# --------------------------------------------------------------------------- #
@app.command()
def new(
    shape: str = typer.Option("circle", help="Form: circle | rect"),
    size: str = typer.Option("40", help="Radius (circle) bzw. Zahl/'BxH' (rect)"),
    color: str = typer.Option("#3498db", help="Füllfarbe (Hex)"),
    image: Path = typer.Option(None, "--image", help="Eigenes Bild (PNG/JPG/SVG) animieren statt Form"),
    position: str = typer.Option("100,100", help="Mittelpunkt 'x,y'"),
    duration: float = typer.Option(2.0, help="Dauer in Sekunden"),
    loop: bool = typer.Option(True, "--loop/--no-loop", help="Endlosschleife"),
    width: int = typer.Option(200, help="Szenenbreite"),
    height: int = typer.Option(200, help="Szenenhöhe"),
    background: str = typer.Option(None, help="Hintergrundfarbe (nur SVG)"),
    move: str = typer.Option(None, help="Bewegen nach 'x,y'"),
    rotate: float = typer.Option(None, help="Drehen um N Grad"),
    scale: float = typer.Option(None, help="Skalieren auf Faktor"),
    color_to: str = typer.Option(None, "--color-to", help="Farbe wechseln zu (Hex)"),
    fade: float = typer.Option(None, help="Ausblenden auf Deckkraft 0..1"),
    fmt: str = typer.Option(None, "--format", help="Ausgabeformat: svg | lottie"),
    output: Path = typer.Option(None, "--output", "-o", help="Ausgabedatei"),
):
    """Erzeugt eine Animation aus Parametern – ganz ohne LLM."""
    animations = []
    if move:
        animations.append({"type": "move", "to": _xy(move)})
    if rotate is not None:
        animations.append({"type": "rotate", "by": rotate})
    if scale is not None:
        animations.append({"type": "scale", "to": scale})
    if color_to:
        animations.append({"type": "color", "to": color_to})
    if fade is not None:
        animations.append({"type": "fade", "to": fade})

    if not animations:
        raise typer.BadParameter(
            "Mindestens eine Animation angeben (--move/--rotate/--scale/--color-to/--fade)."
        )

    shape_dict = {
        "type": shape,
        "size": _size(size),
        "color": color,
        "position": _xy(position),
    }
    if image is not None:
        if (fmt or "").lower() == "lottie" or (output and str(output).endswith(".json")):
            raise typer.BadParameter("Bild-Animationen werden nur als SVG unterstützt.")
        shape_dict["type"] = "image"
        shape_dict["src"] = _data_url(image)

    spec = {
        "width": width,
        "height": height,
        "duration": duration,
        "loop": loop,
        "background": background,
        "shape": shape_dict,
        "animations": animations,
    }
    # Ohne Ausgabe/Format-Angabe standardmäßig SVG erzeugen.
    if not fmt and not output:
        fmt = "svg"
    gfs.render_spec(spec, str(output) if output else None, fmt)


@app.command(name="from-spec")
def from_spec(
    spec_file: Path = typer.Argument(..., help="YAML/JSON-Spec-Datei"),
    output: Path = typer.Option(None, "--output", "-o", help="Ausgabedatei"),
):
    """Erzeugt eine Animation aus einer Spec-Datei."""
    gfs.generate_from_spec(str(spec_file), str(output) if output else None)


@app.command()
def validate(file: Path = typer.Argument(..., help="Lottie-JSON-Datei")):
    """Validiert eine Lottie-JSON-Datei."""
    ok = vj.validate_lottie_json(str(file))
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def optimize(
    file: Path = typer.Argument(..., help="SVG-Datei"),
    output: Path = typer.Option(None, "--output", "-o", help="Zieldatei"),
):
    """Optimiert/speichert eine SVG-Datei."""
    out = str(output) if output else str(file).replace(".svg", "_optimized.svg")
    osvg.optimize_svg(str(file), out)


if __name__ == "__main__":
    app()
