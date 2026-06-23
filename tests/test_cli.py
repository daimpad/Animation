import sys
import json
import xml.dom.minidom as minidom
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

typer = pytest.importorskip("typer")
from typer.testing import CliRunner  # noqa: E402

import cli  # noqa: E402
import validate_json  # noqa: E402

runner = CliRunner()


def test_new_svg(tmp_path):
    out = tmp_path / "demo.svg"
    result = runner.invoke(
        cli.app,
        ["new", "--shape", "circle", "--move", "20,100", "--color-to", "#ff0000",
         "--duration", "3", "-o", str(out)],
    )
    assert result.exit_code == 0, result.output
    minidom.parseString(out.read_text())
    assert "translate" in out.read_text()


def test_new_lottie(tmp_path):
    out = tmp_path / "demo.json"
    result = runner.invoke(
        cli.app,
        ["new", "--shape", "rect", "--size", "80x60", "--rotate", "360",
         "--format", "lottie", "-o", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert validate_json.validate_lottie_json(str(out)) is True


def test_new_requires_an_animation(tmp_path):
    out = tmp_path / "x.svg"
    result = runner.invoke(cli.app, ["new", "-o", str(out)])
    assert result.exit_code != 0  # BadParameter


def test_new_defaults_to_svg_without_output_or_format(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli.app, ["new", "--rotate", "90"])
    assert result.exit_code == 0, result.output
    out = tmp_path / "outputs" / "svg" / "animation.svg"
    assert out.exists()
    minidom.parseString(out.read_text())


def test_new_image_embeds_data_url(tmp_path):
    img = tmp_path / "pic.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)  # Dummy-PNG-Bytes
    out = tmp_path / "img.svg"
    result = runner.invoke(
        cli.app, ["new", "--image", str(img), "--rotate", "360", "--fade", "0.2", "-o", str(out)]
    )
    assert result.exit_code == 0, result.output
    text = out.read_text()
    minidom.parseString(text)
    assert "<image" in text
    assert "data:image/png;base64," in text


def test_new_image_rejects_lottie(tmp_path):
    img = tmp_path / "pic.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    out = tmp_path / "img.json"
    result = runner.invoke(
        cli.app, ["new", "--image", str(img), "--rotate", "90", "--format", "lottie", "-o", str(out)]
    )
    assert result.exit_code != 0  # BadParameter: Bild nur als SVG


def test_from_spec_command(tmp_path):
    spec = tmp_path / "s.json"
    spec.write_text(json.dumps({
        "format": "svg",
        "shape": {"type": "circle", "size": 20, "color": "#fff"},
        "animations": [{"type": "rotate", "by": 90}],
    }))
    out = tmp_path / "s.svg"
    result = runner.invoke(cli.app, ["from-spec", str(spec), "-o", str(out)])
    assert result.exit_code == 0, result.output
    minidom.parseString(out.read_text())


def test_validate_command_pass_and_fail(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({
        "v": "5", "fr": 60, "ip": 0, "op": 60, "w": 10, "h": 10, "layers": []
    }))
    assert runner.invoke(cli.app, ["validate", str(good)]).exit_code == 0

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"v": "5"}))
    assert runner.invoke(cli.app, ["validate", str(bad)]).exit_code == 1


def test_optimize_command(tmp_path):
    src = tmp_path / "in.svg"
    src.write_text("<svg></svg>")
    out = tmp_path / "out.svg"
    result = runner.invoke(cli.app, ["optimize", str(src), "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.read_text() == "<svg></svg>"
