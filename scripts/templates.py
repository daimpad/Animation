"""Parametrische Animations-Vorlagen – ganz ohne LLM.

Erzeugt aus einer einfachen Spezifikation (dict) deterministisch valides
SVG (SMIL-Animation) bzw. Lottie-JSON. Gedacht für *einfache* Standard-
animationen: bewegen, drehen, skalieren/pulsieren, Farbe wechseln, ein-/
ausblenden.

Spec-Modell (eine Form + eine Liste von Animationen):

    {
      "format": "svg",            # svg | lottie (optional, sonst aus Endung)
      "width": 200, "height": 200,
      "duration": 3,               # Sekunden (auch "3s"/"500ms")
      "fps": 60,                    # nur Lottie
      "loop": true,
      "background": "#0f0f1e",     # nur SVG (optional)
      "shape": {
        "type": "circle",          # circle | rect
        "size": 50,                 # circle: Radius; rect: [w,h] oder Zahl
        "color": "#0000FF",
        "position": [100, 100]      # Mittelpunkt
      },
      "animations": [
        {"type": "move",   "to": [180, 100]},
        {"type": "color",  "to": "#FF0000"},
        {"type": "rotate", "by": 360},
        {"type": "scale",  "to": 2.0},
        {"type": "fade",   "to": 0.0}
      ]
    }
"""
from __future__ import annotations

ANIMATION_TYPES = ("move", "color", "rotate", "scale", "fade")
SHAPE_TYPES = ("circle", "rect", "image")


# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #
def duration_seconds(value) -> float:
    """Normalisiert eine Dauer (Zahl, '3s', '500ms') auf Sekunden (float)."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().lower()
    if s.endswith("ms"):
        return float(s[:-2]) / 1000.0
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


def _num(x) -> str:
    """Formatiert eine Zahl knapp (ohne überflüssige Nullen)."""
    return f"{float(x):g}"


def hex_to_rgb01(color: str) -> list[float]:
    """'#RRGGBB' -> [r, g, b] im Bereich 0..1."""
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError(f"Ungültige Hex-Farbe: {color!r}")
    r = int(c[0:2], 16) / 255.0
    g = int(c[2:4], 16) / 255.0
    b = int(c[4:6], 16) / 255.0
    return [r, g, b]


def _shape_size(shape: dict):
    """Gibt für circle den Radius, für rect (w, h) zurück."""
    stype = shape.get("type", "circle")
    size = shape.get("size", 50 if stype == "circle" else [100, 100])
    if stype == "circle":
        if isinstance(size, (list, tuple)):
            return float(size[0])
        return float(size)
    # rect
    if isinstance(size, (list, tuple)):
        return float(size[0]), float(size[1])
    return float(size), float(size)


def _by_type(animations: list[dict]) -> dict:
    """Mappt animation-type -> Definition (letzte gewinnt bei Duplikaten)."""
    out = {}
    for a in animations or []:
        t = a.get("type")
        if t not in ANIMATION_TYPES:
            raise ValueError(
                f"Unbekannter Animationstyp: {t!r}. Erlaubt: {ANIMATION_TYPES}"
            )
        out[t] = a
    return out


# --------------------------------------------------------------------------- #
# SVG (SMIL)
# --------------------------------------------------------------------------- #
def _svg_animate(attr: str, a: str, b: str, dur: str, loop: bool) -> str:
    if loop:
        return (
            f'<animate attributeName="{attr}" values="{a};{b};{a}" '
            f'dur="{dur}" repeatCount="indefinite"/>'
        )
    return (
        f'<animate attributeName="{attr}" from="{a}" to="{b}" '
        f'dur="{dur}" fill="freeze" repeatCount="1"/>'
    )


def _svg_animate_transform(ttype: str, a: str, b: str, dur: str, loop: bool) -> str:
    common = (
        f'attributeName="transform" attributeType="XML" type="{ttype}" '
        f'additive="sum" dur="{dur}"'
    )
    if loop:
        return f'<animateTransform {common} values="{a};{b};{a}" repeatCount="indefinite"/>'
    return f'<animateTransform {common} from="{a}" to="{b}" fill="freeze" repeatCount="1"/>'


def build_svg(spec: dict) -> str:
    """Baut aus der Spec ein vollständiges, animiertes SVG-Dokument (SMIL)."""
    width = spec.get("width", 200)
    height = spec.get("height", 200)
    secs = duration_seconds(spec.get("duration", 3))
    dur = f"{_num(secs)}s"
    loop = spec.get("loop", True)
    bg = spec.get("background")

    shape = spec.get("shape", {})
    stype = shape.get("type", "circle")
    if stype not in SHAPE_TYPES:
        raise ValueError(f"Unbekannter Form-Typ: {stype!r}. Erlaubt: {SHAPE_TYPES}")
    cx, cy = shape.get("position", [width / 2, height / 2])
    color = shape.get("color", "#3498db")
    anims = _by_type(spec.get("animations", []))

    # Form zentriert am Ursprung (0,0) – Transforme wirken so um die Mitte.
    # Farbwechsel (fill) gilt nur für Formen, nicht für Bilder.
    shape_children = []
    if "color" in anims and stype != "image":
        shape_children.append(
            _svg_animate("fill", color, anims["color"].get("to", color), dur, loop)
        )
    if "fade" in anims:
        to = anims["fade"].get("to", 0.0)
        shape_children.append(_svg_animate("opacity", "1", _num(to), dur, loop))
    inner = "".join(shape_children)

    if stype == "circle":
        r = _shape_size(shape)
        shape_el = f'<circle cx="0" cy="0" r="{_num(r)}" fill="{color}">{inner}</circle>'
    elif stype == "image":
        w, h = _shape_size(shape)
        src = shape.get("src", "")
        shape_el = (
            f'<image href="{src}" x="{_num(-w / 2)}" y="{_num(-h / 2)}" '
            f'width="{_num(w)}" height="{_num(h)}" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</image>'
        )
    else:
        w, h = _shape_size(shape)
        shape_el = (
            f'<rect x="{_num(-w / 2)}" y="{_num(-h / 2)}" '
            f'width="{_num(w)}" height="{_num(h)}" fill="{color}">{inner}</rect>'
        )

    # Innere Gruppe: Rotation + Skalierung (um den Ursprung = Formmitte).
    inner_transforms = []
    if "rotate" in anims:
        by = anims["rotate"].get("by", 360)
        inner_transforms.append(
            _svg_animate_transform("rotate", "0 0 0", f"{_num(by)} 0 0", dur, loop)
        )
    if "scale" in anims:
        to = anims["scale"].get("to", 2.0)
        frm = anims["scale"].get("from", 1.0)
        inner_transforms.append(
            _svg_animate_transform("scale", _num(frm), _num(to), dur, loop)
        )
    inner_group = f'<g>{"".join(inner_transforms)}{shape_el}</g>'

    # Äußere Gruppe: Basisposition + Bewegung (Translation).
    outer_anim = ""
    if "move" in anims:
        to = anims["move"].get("to", [cx, cy])
        dx, dy = float(to[0]) - float(cx), float(to[1]) - float(cy)
        outer_anim = _svg_animate_transform(
            "translate", "0 0", f"{_num(dx)} {_num(dy)}", dur, loop
        )
    outer_group = (
        f'<g transform="translate({_num(cx)},{_num(cy)})">{outer_anim}{inner_group}</g>'
    )

    bg_rect = f'<rect width="{_num(width)}" height="{_num(height)}" fill="{bg}"/>' if bg else ""

    return (
        f'<svg width="{_num(width)}" height="{_num(height)}" '
        f'viewBox="0 0 {_num(width)} {_num(height)}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f"  {bg_rect}\n"
        f"  {outer_group}\n"
        f"</svg>\n"
    )


# --------------------------------------------------------------------------- #
# Lottie
# --------------------------------------------------------------------------- #
def _kf(t0: int, t1: int, s0, s1):
    """Zwei Keyframes (Start/Ende) mit sanftem Easing."""
    return [
        {"t": t0, "s": s0, "i": {"x": [0.6], "y": [1]}, "o": {"x": [0.4], "y": [0]}},
        {"t": t1, "s": s1},
    ]


def build_lottie(spec: dict) -> dict:
    """Baut aus der Spec ein gültiges Lottie-JSON (als dict)."""
    width = int(spec.get("width", 200))
    height = int(spec.get("height", 200))
    fps = int(spec.get("fps", 60))
    secs = duration_seconds(spec.get("duration", 3))
    op = max(1, round(secs * fps))

    shape = spec.get("shape", {})
    stype = shape.get("type", "circle")
    if stype not in SHAPE_TYPES:
        raise ValueError(f"Unbekannter Form-Typ: {stype!r}. Erlaubt: {SHAPE_TYPES}")
    if stype == "image":
        raise ValueError(
            "Bild-Animationen werden derzeit nur als SVG unterstützt (nicht Lottie)."
        )
    cx, cy = shape.get("position", [width / 2, height / 2])
    color = shape.get("color", "#3498db")
    anims = _by_type(spec.get("animations", []))

    # Transform (Layer) -------------------------------------------------------
    if "move" in anims:
        to = anims["move"].get("to", [cx, cy])
        p = {"a": 1, "k": _kf(0, op, [float(cx), float(cy), 0], [float(to[0]), float(to[1]), 0])}
    else:
        p = {"a": 0, "k": [float(cx), float(cy), 0]}

    if "rotate" in anims:
        by = anims["rotate"].get("by", 360)
        r = {"a": 1, "k": _kf(0, op, [0], [float(by)])}
    else:
        r = {"a": 0, "k": 0}

    if "scale" in anims:
        to = float(anims["scale"].get("to", 2.0)) * 100.0
        frm = float(anims["scale"].get("from", 1.0)) * 100.0
        s = {"a": 1, "k": _kf(0, op, [frm, frm, 100], [to, to, 100])}
    else:
        s = {"a": 0, "k": [100, 100, 100]}

    if "fade" in anims:
        to = float(anims["fade"].get("to", 0.0)) * 100.0
        o = {"a": 1, "k": _kf(0, op, [100], [to])}
    else:
        o = {"a": 0, "k": 100}

    # Form-Element ------------------------------------------------------------
    if stype == "circle":
        r_px = _shape_size(shape)
        geom = {
            "ty": "el",
            "nm": "Ellipse",
            "p": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [2 * r_px, 2 * r_px]},
        }
    else:
        w, h = _shape_size(shape)
        geom = {
            "ty": "rc",
            "nm": "Rect",
            "d": 1,
            "p": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [w, h]},
            "r": {"a": 0, "k": 0},
        }

    # Füllung (ggf. animierte Farbe) -----------------------------------------
    if "color" in anims:
        c0 = hex_to_rgb01(color) + [1]
        c1 = hex_to_rgb01(anims["color"].get("to", color)) + [1]
        fill_c = {"a": 1, "k": _kf(0, op, c0, c1)}
    else:
        fill_c = {"a": 0, "k": hex_to_rgb01(color) + [1]}
    fill = {"ty": "fl", "nm": "Fill", "o": {"a": 0, "k": 100}, "r": 1, "c": fill_c}

    transform = {
        "ty": "tr",
        "o": {"a": 0, "k": 100},
        "r": {"a": 0, "k": 0},
        "p": {"a": 0, "k": [0, 0]},
        "a": {"a": 0, "k": [0, 0]},
        "s": {"a": 0, "k": [100, 100]},
    }

    layer = {
        "ddd": 0,
        "ind": 1,
        "ty": 4,
        "nm": spec.get("name", "Shape"),
        "sr": 1,
        "ks": {"o": o, "r": r, "p": p, "a": {"a": 0, "k": [0, 0, 0]}, "s": s},
        "ao": 0,
        "shapes": [{"ty": "gr", "nm": "Group", "it": [geom, fill, transform]}],
        "ip": 0,
        "op": op,
        "st": 0,
        "bm": 0,
    }

    return {
        "v": "5.12.2",
        "fr": fps,
        "ip": 0,
        "op": op,
        "w": width,
        "h": height,
        "nm": spec.get("name", "Animation"),
        "ddd": 0,
        "assets": [],
        "layers": [layer],
        "markers": [],
    }
