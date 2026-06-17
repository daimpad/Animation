import sys
import json
from pathlib import Path

# scripts/ zum Importpfad hinzufügen (kein Package)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import generate_svg  # noqa: E402
import generate_lottie  # noqa: E402
import validate_json  # noqa: E402
import optimize_svg  # noqa: E402
import llm  # noqa: E402


def test_generate_svg_creates_valid_svg(tmp_path):
    out = tmp_path / "anim.svg"
    generate_svg.generate_svg_from_prompt("inputs/prompts/circle_to_spiral.txt", str(out))
    assert out.exists()
    content = out.read_text()
    assert "<svg" in content
    assert "</svg>" in content


def test_generate_svg_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "deep" / "anim.svg"
    generate_svg.generate_svg_from_prompt("prompt.txt", str(out))
    assert out.exists()


def test_generate_lottie_creates_valid_json(tmp_path):
    out = tmp_path / "anim.json"
    generate_lottie.generate_lottie_from_prompt("inputs/prompts/circle_to_spiral.txt", str(out))
    data = json.loads(out.read_text())
    for key in ["v", "fr", "ip", "op", "w", "h", "layers"]:
        assert key in data


def test_validate_json_accepts_generated_lottie(tmp_path):
    out = tmp_path / "anim.json"
    generate_lottie.generate_lottie_from_prompt("prompt.txt", str(out))
    assert validate_json.validate_lottie_json(str(out)) is True


def test_validate_json_rejects_missing_keys(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"v": "5.12.2"}))
    assert validate_json.validate_lottie_json(str(bad)) is False


def test_validate_json_rejects_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ das ist kein json")
    assert validate_json.validate_lottie_json(str(bad)) is False


def test_validate_json_rejects_missing_file(tmp_path):
    assert validate_json.validate_lottie_json(str(tmp_path / "gibtsnicht.json")) is False


def test_optimize_svg_preserves_content(tmp_path):
    src = tmp_path / "in.svg"
    src.write_text("<svg><circle r='1'/></svg>")
    dst = tmp_path / "out.svg"
    optimize_svg.optimize_svg(str(src), str(dst))
    assert dst.exists()
    assert dst.read_text() == "<svg><circle r='1'/></svg>"


# --- LLM-Hilfsfunktionen (ohne Netzwerk) ---


def test_extract_svg_from_text():
    text = "Hier ist dein SVG:\n<svg width='1'><rect/></svg>\nViel Spaß!"
    assert llm.extract_svg(text) == "<svg width='1'><rect/></svg>"


def test_extract_svg_returns_none_without_svg():
    assert llm.extract_svg("kein svg hier") is None
    assert llm.extract_svg(None) is None


def test_extract_json_from_code_fence():
    text = "```json\n{\"a\": 1, \"b\": [2, 3]}\n```"
    assert llm.extract_json(text) == {"a": 1, "b": [2, 3]}


def test_extract_json_from_plain_text():
    text = "Antwort: {\"x\": true} -- fertig"
    assert llm.extract_json(text) == {"x": True}


def test_extract_json_returns_none_on_garbage():
    assert llm.extract_json("kein json") is None
    assert llm.extract_json(None) is None


def test_query_ollama_unreachable_returns_none(monkeypatch):
    # Aufruf gegen einen sicher geschlossenen Port -> None statt Exception
    monkeypatch.setattr(llm, "OLLAMA_URL", "http://127.0.0.1:1")
    assert llm.query_ollama("test", timeout=2) is None


def test_generate_lottie_falls_back_without_llm(tmp_path):
    out = tmp_path / "fallback.json"
    generate_lottie.generate_lottie_from_prompt("kein-prompt.txt", str(out), use_llm=False)
    data = json.loads(out.read_text())
    assert data == generate_lottie.PLACEHOLDER_LOTTIE
