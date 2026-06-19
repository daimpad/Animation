"""Optionale LLM-Anbindung über Ollama (lokal).

Nutzt ausschließlich die Standardbibliothek (``urllib``), damit keine
zusätzlichen Abhängigkeiten nötig sind. Ist Ollama nicht erreichbar oder
liefert keine brauchbare Ausgabe, geben die Funktionen ``None`` zurück und
die aufrufenden Skripte fallen auf ihre Platzhalter-Ausgaben zurück.

Konfiguration über Umgebungsvariablen:
    OLLAMA_URL    Basis-URL des Ollama-Servers (Standard: http://localhost:11434)
    OLLAMA_MODEL  Zu verwendendes Modell (Standard: mistral)
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")


def query_ollama(prompt: str, model: str | None = None, timeout: int = 120) -> str | None:
    """Sendet einen Prompt an Ollama und gibt den Antworttext zurück.

    Gibt ``None`` zurück, wenn der Server nicht erreichbar ist oder die
    Antwort nicht verarbeitet werden kann.
    """
    model = model or OLLAMA_MODEL
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("response")
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def extract_svg(text: str | None) -> str | None:
    """Extrahiert den ersten ``<svg>...</svg>``-Block aus einem Text."""
    if not text:
        return None
    match = re.search(r"<svg\b.*?</svg>", text, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else None


def extract_json(text: str | None) -> dict | None:
    """Extrahiert das erste JSON-Objekt aus einem Text (auch aus Code-Fences)."""
    if not text:
        return None

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fence.group(1) if fence else None

    if candidate is None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]

    if not candidate:
        return None

    try:
        result = json.loads(candidate)
    except ValueError:
        return None
    return result if isinstance(result, dict) else None
