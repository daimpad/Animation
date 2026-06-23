import sys
import json


def validate_lottie_json(file_path: str) -> bool:
    """
    Validiert eine Lottie-JSON-Datei auf grundlegende Struktur.
    """
    required_keys = ["v", "fr", "ip", "op", "w", "h", "layers"]

    try:
        with open(file_path) as f:
            data = json.load(f)

        if not all(key in data for key in required_keys):
            raise ValueError("Fehlende Pflichtfelder in der Lottie-JSON-Datei.")

        print(f"✅ {file_path} ist eine valide Lottie-JSON-Datei.")
        return True
    except FileNotFoundError:
        print(f"❌ {file_path} wurde nicht gefunden.")
        return False
    except json.JSONDecodeError:
        print(f"❌ {file_path} ist keine valide JSON-Datei.")
        return False
    except Exception as e:
        print(f"❌ Fehler in {file_path}: {e}")
        return False


if __name__ == "__main__":
    # Pfad aus den Argumenten oder Standardwert verwenden
    target = sys.argv[1] if len(sys.argv) > 1 else "outputs/lottie/circle_to_spiral.json"
    valid = validate_lottie_json(target)
    sys.exit(0 if valid else 1)
