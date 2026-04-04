"""
Narzędzia do upraszczania outputu Jana i normalizacji benchmarku.
"""

from __future__ import annotations

import json
import random
import re
from typing import Any

LIGHT_GREETINGS = (
    "Jan poprawił tekst:",
    "Jan proponuje taką wersję:",
    "Wedle Jana najlepsza wersja brzmi:",
)

CORRECTED_TEXT_KEYS = (
    "corrected_text",
    "corrected",
    "final_text",
    "revised_text",
)

SECTION_LABELS = (
    "Tekst poprawiony",
    "Poprawiony tekst",
    "Ulepszony tekst",
)

EXPLANATION_SECTION_LABELS = (
    "Najważniejsze zmiany",
    "Lista zmian",
    "Raport korekty",
    "Cytat z polskiej literatury",
    "Wyjaśnienie zmian",
)

EXPLANATION_BULLET_STOP_LABELS = (
    "Uzasadnienie",
    "Zasada",
    "Ocena",
    "Ortografia",
    "Interpunkcja",
    "Gramatyka",
    "Styl",
)


def choose_light_greeting() -> str:
    """Zwraca krótką, jednozdaniową linię Jana dla trybu workplace."""

    return random.choice(LIGHT_GREETINGS)


def strip_full_code_fence(text: str) -> str:
    """Zdejmuje zewnętrzny fenced code block, jeśli obejmuje cały tekst."""

    stripped = text.strip()
    match = re.fullmatch(r"```(?:[\w+-]+)?\s*(.*?)\s*```", stripped, flags=re.S)
    if match:
        return match.group(1).strip()
    return stripped


def strip_wrapping_quotes(text: str) -> str:
    """Usuwa jedną parę zewnętrznych cudzysłowów lub backticków."""

    stripped = text.strip()
    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("“", "”"),
        ("„", "”"),
        ("`", "`"),
    ]
    for left, right in quote_pairs:
        if stripped.startswith(left) and stripped.endswith(right) and len(stripped) >= 2:
            return stripped[len(left) : -len(right)].strip()
    return stripped


def clean_inline_markdown(text: str) -> str:
    """Usuwa lekkie wrappery markdownowe z tekstu."""

    cleaned = strip_full_code_fence(text)
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("`", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return strip_wrapping_quotes(cleaned).strip()


def extract_json_payload(text: str) -> dict[str, Any] | None:
    """Próbuje wydobyć obiekt JSON z odpowiedzi modelu."""

    stripped = text.strip()
    try:
        payload = json.loads(stripped)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", stripped)
    if not match:
        return None

    try:
        payload = json.loads(match.group())
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        return None
    return None


def extract_corrected_text_from_json(payload: Any) -> str | None:
    """Szuka poprawionego tekstu w strukturze JSON."""

    if isinstance(payload, dict):
        for key in CORRECTED_TEXT_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            candidate = extract_corrected_text_from_json(value)
            if candidate:
                return candidate
    elif isinstance(payload, list):
        for value in payload:
            candidate = extract_corrected_text_from_json(value)
            if candidate:
                return candidate
    return None


def extract_labeled_text_block(text: str) -> str | None:
    """Wyciąga finalny tekst z typowych legacy wrapperów Jana."""

    normalized = text.replace("\r\n", "\n").strip()
    for label in SECTION_LABELS:
        label_pattern = re.escape(label)

        fenced_match = re.search(
            rf"(?is)(?:^|\n)(?:#+\s*)?(?:\*\*)?{label_pattern}(?:\*\*)?\s*:?\s*```(?:[\w+-]+)?\s*(.*?)\s*```",
            normalized,
        )
        if fenced_match:
            return fenced_match.group(1).strip()

        quoted_match = re.search(
            rf'(?is)(?:^|\n)(?:#+\s*)?(?:\*\*)?{label_pattern}(?:\*\*)?\s*:?\s*["“](.*?)["”](?=\n|$)',
            normalized,
        )
        if quoted_match:
            return quoted_match.group(1).strip()

        paragraph_match = re.search(
            rf"(?is)(?:^|\n)(?:#+\s*)?(?:\*\*)?{label_pattern}(?:\*\*)?\s*:?\s*(.+?)(?=\n(?:###|##|####|\*\*|Najważniejsze zmiany|Lista zmian|Raport korekty|Cytat z polskiej literatury)|\Z)",
            normalized,
        )
        if paragraph_match:
            return paragraph_match.group(1).strip()
    return None


def extract_change_bullets(text: str, limit: int = 5) -> list[str]:
    """Wyciąga skróconą listę zmian z verbose outputu modelu."""

    normalized = text.replace("\r\n", "\n")
    section_text = normalized
    for label in EXPLANATION_SECTION_LABELS:
        match = re.search(
            rf"(?is)(?:^|\n)(?:#+\s*)?(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:?\s*(.+)",
            normalized,
        )
        if match:
            section_text = match.group(1)
            break

    bullets: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        marker_match = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", stripped)
        if not marker_match:
            continue
        bullet = clean_inline_markdown(marker_match.group(1))
        if not bullet:
            continue
        if any(bullet.startswith(label) for label in EXPLANATION_BULLET_STOP_LABELS):
            continue
        bullets.append(re.sub(r":\s*$", "", bullet))
        if len(bullets) >= limit:
            break
    return bullets


def extract_primary_text(text: str) -> str:
    """Zwraca najbardziej prawdopodobny finalny tekst użytkowy."""

    stripped = text.strip()
    if not stripped:
        return ""

    payload = extract_json_payload(stripped)
    if payload:
        corrected = extract_corrected_text_from_json(payload)
        if corrected:
            return clean_inline_markdown(corrected)

    labeled = extract_labeled_text_block(stripped)
    if labeled:
        return clean_inline_markdown(labeled)

    for label in EXPLANATION_SECTION_LABELS:
        marker = re.search(rf"(?is)(.+?)\n(?:#+\s*)?(?:\*\*)?{re.escape(label)}", stripped)
        if marker:
            return clean_inline_markdown(marker.group(1))

    return clean_inline_markdown(stripped)


def format_compact_explainer(text: str, include_greeting: bool = False) -> str:
    """Buduje zwięzły explain mode dla outputu correction tools."""

    primary = extract_primary_text(text)
    bullets = extract_change_bullets(text)

    parts: list[str] = []
    if include_greeting:
        parts.append(choose_light_greeting())
    if primary:
        parts.append(primary)
    if bullets:
        bullet_lines = ["Najważniejsze zmiany:"]
        bullet_lines.extend(f"- {bullet}" for bullet in bullets)
        parts.append("\n".join(bullet_lines))
    return "\n\n".join(part for part in parts if part).strip()


def normalize_benchmark_output(system: str, text: str) -> str:
    """Tworzy diagnostyczny, wrapper-stripped view outputu systemu."""

    if system == "Jan":
        return extract_primary_text(text)
    return clean_inline_markdown(text)
