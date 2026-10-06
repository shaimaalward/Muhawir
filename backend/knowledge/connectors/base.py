from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

_AR_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_WS = re.compile(r"\s+")


def normalize_space(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


def normalize_arabic_for_search(text: str) -> str:
    text = _AR_DIACRITICS.sub("", text or "")
    text = text.replace("ـ", "")
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    return normalize_space(text)


def stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return sha256(raw.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class Chunk:
    text: str
    index: int


def chunk_text(text: str, max_chars: int = 1500, overlap_chars: int = 220) -> list[Chunk]:
    """Paragraph-aware chunking. Keeps chunks readable and deterministic."""
    text = (text or "").replace("\r\n", "\n")
    paragraphs = [normalize_space(p) for p in re.split(r"\n\s*\n+", text) if normalize_space(p)]
    if not paragraphs:
        paragraphs = [normalize_space(text)] if normalize_space(text) else []

    chunks: list[str] = []
    current = ""
    for p in paragraphs:
        if len(p) > max_chars:
            # Hard-split unusually large paragraphs at sentence-ish boundaries.
            pieces = re.split(r"(?<=[.!؟!؛])\s+", p)
        else:
            pieces = [p]
        for piece in pieces:
            piece = normalize_space(piece)
            if not piece:
                continue
            candidate = f"{current}\n{piece}".strip() if current else piece
            if current and len(candidate) > max_chars:
                chunks.append(current)
                tail = current[-overlap_chars:] if overlap_chars else ""
                current = normalize_space(f"{tail} {piece}")
            else:
                current = candidate
    if current:
        chunks.append(current)

    return [Chunk(text=c, index=i) for i, c in enumerate(chunks)]
