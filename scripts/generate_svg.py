import sys
from pathlib import Path

# scripts/ liegt im Importpfad (sowohl bei direktem Aufruf als auch beim Import)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import query_ollama, extract_svg  # noqa: E402

# Platzhalter-Ausgabe, falls kein LLM verfügbar ist oder keine SVG geliefert wird.
PLACEHOLDER_SVG = """\
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="50" fill="blue">
    <animate attributeName="r" from="50" to="100" dur="3s" repeatCount="indefinite" />
    <animate attributeName="fill" from="blue" to="red" dur="3s" repeatCount="indefinite" />
  </circle>
</svg>
"""


def _read_prompt(prompt_file: str) -> str | None:
    try:
        return Path(prompt_file).read_text()
    except OSError:
        return None


def generate_svg_from_prompt(prompt_file: str, output_file: str, use_llm: bool = True) -> None:
    """
    Liest einen Prompt aus einer Datei und generiert eine SVG-Datei.

    Ist ``use_llm`` aktiv und ein lokales Ollama erreichbar, wird der SVG-Code
    vom LLM generiert. Andernfalls (kein Prompt, kein LLM, keine verwertbare
    Antwort) wird auf eine Platzhalter-SVG zurückgegriffen.
    """
    svg_content = None
    prompt = _read_prompt(prompt_file)

    if use_llm and prompt:
        instruction = (
            f"{prompt}\n\n"
            "Gib ausschließlich gültigen SVG-Code aus, beginnend mit <svg> und "
            "endend mit </svg>. Keine Erklärungen, kein Markdown."
        )
        svg_content = extract_svg(query_ollama(instruction))
        if svg_content:
            print("🧠 SVG vom LLM (Ollama) generiert.")

    if not svg_content:
        svg_content = PLACEHOLDER_SVG
        print("ℹ️  Platzhalter-SVG verwendet (kein LLM / keine verwertbare Ausgabe).")

    if not svg_content.endswith("\n"):
        svg_content += "\n"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content)
    print(f"✅ SVG generiert und gespeichert unter: {output_path}")


if __name__ == "__main__":
    # Pfade aus den Argumenten oder Standardwerte verwenden
    if len(sys.argv) == 3:
        generate_svg_from_prompt(sys.argv[1], sys.argv[2])
    else:
        generate_svg_from_prompt(
            prompt_file="inputs/prompts/circle_to_spiral.txt",
            output_file="outputs/svg/circle_to_spiral.svg",
        )
