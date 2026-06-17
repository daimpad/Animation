import sys
from pathlib import Path
import json

# scripts/ liegt im Importpfad (sowohl bei direktem Aufruf als auch beim Import)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import query_ollama, extract_json  # noqa: E402

REQUIRED_KEYS = ["v", "fr", "ip", "op", "w", "h", "layers"]

# Platzhalter-Ausgabe, falls kein LLM verfügbar ist oder keine Lottie geliefert wird.
PLACEHOLDER_LOTTIE = {
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


def _read_prompt(prompt_file: str) -> str | None:
    try:
        return Path(prompt_file).read_text()
    except OSError:
        return None


def generate_lottie_from_prompt(prompt_file: str, output_file: str, use_llm: bool = True) -> None:
    """
    Liest einen Prompt aus einer Datei und generiert eine Lottie-JSON-Datei.

    Ist ``use_llm`` aktiv und ein lokales Ollama erreichbar, wird das
    Lottie-JSON vom LLM generiert (sofern es alle Pflichtfelder enthält).
    Andernfalls wird auf eine Platzhalter-Struktur zurückgegriffen.
    """
    lottie_data = None
    prompt = _read_prompt(prompt_file)

    if use_llm and prompt:
        instruction = (
            f"{prompt}\n\n"
            "Gib ausschließlich gültiges Lottie-JSON aus (ein einzelnes "
            "JSON-Objekt). Keine Erklärungen."
        )
        candidate = extract_json(query_ollama(instruction))
        if isinstance(candidate, dict) and all(key in candidate for key in REQUIRED_KEYS):
            lottie_data = candidate
            print("🧠 Lottie-JSON vom LLM (Ollama) generiert.")

    if lottie_data is None:
        lottie_data = PLACEHOLDER_LOTTIE
        print("ℹ️  Platzhalter-Lottie verwendet (kein LLM / keine verwertbare Ausgabe).")

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
