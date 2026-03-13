from __future__ import annotations

import re
from typing import Literal


DetectedLanguage = Literal["zh", "en", "mixed"]

_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_primary_language(text: str | None) -> DetectedLanguage:
    normalized = (text or "").strip()
    if not normalized:
        return "mixed"

    chinese_count = len(_CJK_RE.findall(normalized))
    english_count = len(_LATIN_RE.findall(normalized))

    if chinese_count and not english_count:
        return "zh"
    if english_count and not chinese_count:
        return "en"
    if chinese_count and english_count:
        return "zh" if chinese_count >= english_count else "en"
    return "mixed"


def build_language_instruction(text: str | None) -> str:
    language = detect_primary_language(text)
    if language == "zh":
        return (
            "The user's input is primarily Simplified Chinese. "
            "You must answer entirely in Simplified Chinese. "
            "Do not switch to English unless the user explicitly asks for it or a fixed brand name must be preserved."
        )
    if language == "en":
        return (
            "The user's input is primarily English. "
            "You must answer entirely in English. "
            "Do not switch to Chinese unless the user explicitly asks for it or a fixed brand name must be preserved."
        )
    return (
        "You must follow the primary language used in the user's input. "
        "Do not translate or switch languages unless the user explicitly asks for it."
    )
