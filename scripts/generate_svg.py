import sys
from pathlib import Path


def generate_svg_from_prompt(prompt_file: str, output_file: str) -> None:
    """
    Liest einen Prompt aus einer Datei und generiert eine SVG-Datei.
    (In der Praxis: Hier würde das LLM den SVG-Code generieren.)
    """
    # Beispiel: SVG-Code direkt aus einer Datei oder LLM-Ausgabe
    svg_content = """\
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="50" fill="blue">
    <animate attributeName="r" from="50" to="100" dur="3s" repeatCount="indefinite" />
    <animate attributeName="fill" from="blue" to="red" dur="3s" repeatCount="indefinite" />
  </circle>
</svg>
"""

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
