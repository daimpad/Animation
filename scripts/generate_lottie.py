import sys
from pathlib import Path
import json


def generate_lottie_from_prompt(prompt_file: str, output_file: str) -> None:
    """
    Liest einen Prompt aus einer Datei und generiert eine Lottie-JSON-Datei.
    (In der Praxis: Hier würde das LLM den Lottie-JSON-Code generieren.)
    """
    # Beispiel: Lottie-JSON-Struktur
    lottie_data = {
        "v": "5.12.2",
        "fr": 60,
        "ip": 0,
        "op": 180,
        "w": 200,
        "h": 200,
        "nm": "Circle to Spiral",
        "layers": [
            {
                "ty": 4,  # Shape Layer
                "nm": "Circle",
                "ip": 0,
                "op": 180,
                "st": 0,
                "shapes": [
                    {
                        "ty": "gr",
                        "it": [
                            {
                                "ty": "el",
                                "p": {"a": 0, "k": [100, 100, 0]},
                                "s": {"a": 0, "k": [50, 50]},
                                "c": {"a": 0, "k": [0, 0, 1, 1]},
                            },
                            {
                                "ty": "fl",
                                "c": {"a": 0, "k": [0, 0, 1, 1]},
                            },
                            {
                                "ty": "tr",
                                "o": {"a": 0, "k": 100},
                                "r": {"a": 0, "k": 0},
                                "p": {"a": 0, "k": [100, 100, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 0, "k": [100, 100, 100]},
                            },
                        ],
                    }
                ],
            }
        ],
    }

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(lottie_data, f, indent=2)
    print(f"✅ Lottie-JSON generiert und gespeichert unter: {output_path}")


if __name__ == "__main__":
    # Pfade aus den Argumenten oder Standardwerte verwenden
    if len(sys.argv) == 3:
        generate_lottie_from_prompt(sys.argv[1], sys.argv[2])
    else:
        generate_lottie_from_prompt(
            prompt_file="inputs/prompts/circle_to_spiral.txt",
            output_file="outputs/lottie/circle_to_spiral.json",
        )
