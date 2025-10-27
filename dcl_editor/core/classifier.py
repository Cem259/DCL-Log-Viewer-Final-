from __future__ import annotations

from typing import Iterable

from .models import DclType


KNOWN_TYPES: tuple[DclType, ...] = ("RCD", "CLD", "CDA", "FSM")


def classify_block(clean_lines: Iterable[str]) -> DclType:
    """Classify a normalized block using its leading tokens."""

    lines = [line.strip() for line in clean_lines if line.strip()]
    if not lines:
        return "UNKNOWN"

    first_line = lines[0]
    first_token = first_line.split()[0].upper()
    if first_token in KNOWN_TYPES:
        return first_token  # type: ignore[return-value]

    header_scope = " ".join(lines[:2]).upper()
    for candidate in KNOWN_TYPES:
        if f"/{candidate}" in header_scope or f" {candidate} " in header_scope:
            return candidate

    return "UNKNOWN"
