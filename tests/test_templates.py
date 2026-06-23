import sys
import json
import xml.dom.minidom as minidom
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import templates  # noqa: E402
import generate_from_spec  # noqa: E402
import validate_json  # noqa: E402

REQUIRED_LOTTIE_KEYS = ["v", "fr", "ip", "op", "w", "h", "layers"]


# --- Hilfsfunktionen ------------------------------------------------------- #
def test_duration_seconds_parsing():
    assert templates.duration_seconds(3) == 3.0
    assert templates.duration_seconds("3s") == 3.0
    assert templates.duration_seconds("500ms") == 0.5


def test_hex_to_rgb01():
    assert templates.hex_to_rgb01("#000000") == [0.0, 0.0, 0.0]
    assert templates.hex_to_rgb01("#ffffff") == [1.0, 1.0, 1.0]
    assert templates.hex_to_rgb01("#f00") == [1.0, 0.0, 0.0]  # Kurzform


# --- SVG ------------------------------------------------------------------- #
def _spec_svg(animations, shape_type="circle"):
    return {
        "format": "svg",
        "width": 200,
        "height": 200,
        "duration": 2,
        "shape": {"type": shape_type, "size": 30, "color": "#0000FF", "position": [100, 100]},
        "animations": animations,
    }


def test_build_svg_is_wellformed_xml():
    svg = templates.build_svg(_spec_svg([{"type": "move", "to": [180, 100]}]))
    # Wirft bei Fehlern -> Test schlägt fehl
    minidom.parseString(svg)
    assert svg.strip().startswith("<svg")
    assert "</svg>" in svg


def test_build_svg_contains_expected_animations():
    svg = templates.build_svg(
        _spec_svg(
            [
                {"type": "move", "to": [180, 100]},
                {"type": "rotate", "by": 360},
                {"type": "scale", "to": 2.0},
                {"type": "color", "to": "#FF0000"},
                {"type": "fade", "to": 0.0},
            ]
        )
    )
    assert 'type="translate"' in svg
    assert 'type="rotate"' in svg
    assert 'type="scale"' in svg
    assert 'attributeName="fill"' in svg
    assert 'attributeName="opacity"' in svg


def test_build_svg_rect_and_background():
    svg = templates.build_svg(
        {
            "format": "svg",
            "background": "#101010",
            "shape": {"type": "rect", "size": [50, 80], "color": "#00ff00"},
            "animations": [{"type": "rotate", "by": 90}],
        }
    )
    minidom.parseString(svg)
    assert "<rect" in svg
    assert "#101010" in svg


def test_build_svg_unknown_animation_raises():
    import pytest

    with pytest.raises(ValueError):
        templates.build_svg(_spec_svg([{"type": "explode"}]))


def test_build_svg_image_embeds_src_and_skips_fill():
    svg = templates.build_svg(
        {
            "format": "svg",
            "shape": {"type": "image", "size": [120, 80], "src": "cat.png", "position": [100, 100]},
            "animations": [{"type": "rotate", "by": 360}, {"type": "color", "to": "#fff"}, {"type": "fade", "to": 0.2}],
        }
    )
    minidom.parseString(svg)
    assert "<image" in svg
    assert 'href="cat.png"' in svg
    assert 'type="rotate"' in svg
    assert 'attributeName="opacity"' in svg
    # Farbwechsel (fill) gilt nicht für Bilder
    assert 'attributeName="fill"' not in svg


def test_build_lottie_rejects_image():
    import pytest

    with pytest.raises(ValueError):
        templates.build_lottie(
            {"shape": {"type": "image", "src": "x.png"}, "animations": [{"type": "move", "to": [1, 1]}]}
        )


# --- Lottie ---------------------------------------------------------------- #
def test_build_lottie_has_required_keys_and_validates(tmp_path):
    data = templates.build_lottie(
        {
            "format": "lottie",
            "fps": 60,
            "duration": 2,
            "shape": {"type": "rect", "size": [80, 80], "color": "#2ecc71"},
            "animations": [{"type": "rotate", "by": 360}, {"type": "color", "to": "#f1c40f"}],
        }
    )
    for key in REQUIRED_LOTTIE_KEYS:
        assert key in data
    assert data["op"] == 120  # 2s * 60fps

    out = tmp_path / "anim.json"
    out.write_text(json.dumps(data))
    assert validate_json.validate_lottie_json(str(out)) is True


def test_build_lottie_move_creates_animated_position():
    data = templates.build_lottie(
        {
            "shape": {"type": "circle", "size": 20, "color": "#fff", "position": [10, 10]},
            "animations": [{"type": "move", "to": [90, 90]}],
        }
    )
    pos = data["layers"][0]["ks"]["p"]
    assert pos["a"] == 1  # animiert
    assert pos["k"][0]["s"] == [10.0, 10.0, 0]
    assert pos["k"][-1]["s"] == [90.0, 90.0, 0]


# --- Generator (JSON-Spec, ohne PyYAML-Abhängigkeit) ----------------------- #
def test_generate_from_spec_json_svg(tmp_path):
    spec = tmp_path / "s.json"
    spec.write_text(json.dumps(_spec_svg([{"type": "move", "to": [180, 100]}])))
    out = tmp_path / "out.svg"
    generate_from_spec.generate_from_spec(str(spec), str(out))
    minidom.parseString(out.read_text())


def test_generate_from_spec_infers_format_from_extension(tmp_path):
    spec_data = {
        "shape": {"type": "circle", "size": 20, "color": "#fff"},
        "animations": [{"type": "fade", "to": 0}],
    }
    spec = tmp_path / "s.json"
    spec.write_text(json.dumps(spec_data))
    out = tmp_path / "out.json"  # -> Lottie aus Endung
    generate_from_spec.generate_from_spec(str(spec), str(out))
    assert validate_json.validate_lottie_json(str(out)) is True


def test_generate_from_spec_yaml_if_available(tmp_path):
    import pytest

    yaml = pytest.importorskip("yaml")
    spec = tmp_path / "s.yaml"
    spec.write_text(
        yaml.safe_dump(
            {
                "format": "svg",
                "shape": {"type": "circle", "size": 20, "color": "#fff"},
                "animations": [{"type": "rotate", "by": 180}],
            }
        )
    )
    out = tmp_path / "out.svg"
    generate_from_spec.generate_from_spec(str(spec), str(out))
    assert "rotate" in out.read_text()
