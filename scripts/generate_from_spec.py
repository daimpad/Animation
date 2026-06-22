"""Erzeugt eine Animation aus einer Spezifikationsdatei (YAML oder JSON).

Beispiel:
    python scripts/generate_from_spec.py inputs/specs/bounce.yaml outputs/svg/bounce.svg
    python scripts/generate_from_spec.py inputs/specs/spinner.json outputs/lottie/spinner.json

Das Ausgabeformat ergibt sich aus dem Spec-Feld ``format`` oder – falls nicht
gesetzt – aus der Endung der Ausgabedatei (.svg -> SVG, .json -> Lottie).
"""
import sys
import json
from pathlib import Path

# scripts/ in den Importpfad (direkter Aufruf wie auch Import)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from templates import build_svg, build_lottie  # noqa: E402


def load_spec(spec_file: str) -> dict:
    """Lädt eine Spec aus YAML (.yaml/.yml) oder JSON (.json)."""
    path = Path(spec_file)
    text = path.read_text()
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - nur ohne PyYAML
            raise SystemExit(
                "PyYAML wird für YAML-Specs benötigt: 'pip install pyyaml' "
                "(oder eine JSON-Spec verwenden)."
            ) from exc
        return yaml.safe_load(text)
    return json.loads(text)


def _infer_format(spec: dict, output_file: str | None) -> str:
    fmt = (spec.get("format") or "").lower()
    if fmt in ("svg", "lottie"):
        return fmt
    if output_file:
        suffix = Path(output_file).suffix.lower()
        if suffix == ".svg":
            return "svg"
        if suffix == ".json":
            return "lottie"
    raise SystemExit(
        "Format unbekannt: bitte 'format: svg|lottie' in der Spec setzen "
        "oder eine Ausgabedatei mit .svg/.json angeben."
    )


def generate_from_spec(spec_file: str, output_file: str | None = None) -> str:
    """Generiert die Animation und schreibt sie. Gibt den Ausgabepfad zurück."""
    spec = load_spec(spec_file)
    fmt = _infer_format(spec, output_file)

    if output_file is None:
        stem = Path(spec_file).stem
        output_file = (
            f"outputs/svg/{stem}.svg" if fmt == "svg" else f"outputs/lottie/{stem}.json"
        )

    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "svg":
        out.write_text(build_svg(spec))
    else:
        out.write_text(json.dumps(build_lottie(spec), indent=2))

    print(f"✅ {fmt.upper()} aus Spec generiert: {out}")
    return str(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_from_spec.py <spec_file> [output_file]")
        sys.exit(1)
    generate_from_spec(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
