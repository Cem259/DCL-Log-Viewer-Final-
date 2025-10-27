from __future__ import annotations

import json
import re
from typing import Iterable

CALLSIGN_PATTERN = re.compile(r"\b[A-Z]{2,4}\d[A-Z0-9]{1,3}\b")
TIMESTAMP_PATTERN = re.compile(r"\b\d{6}\b")
PRIORITY_KEYWORDS = ("CLRD", "RCD", "CDA", "FSM", "REQ", "CLR", "CLEAR")
TYPE_TOKENS = {"RCD", "CLD", "CDA", "FSM"}


def _find_callsign(lines: Iterable[str]) -> str | None:
    candidates: list[str] = []
    for line in lines:
        matches = CALLSIGN_PATTERN.findall(line)
        if not matches:
            continue
        if any(keyword in line for keyword in PRIORITY_KEYWORDS):
            return matches[0]
        candidates.extend(matches)
    return candidates[0] if candidates else None


def _find_timestamp(lines: Iterable[str]) -> str | None:
    for line in lines:
        match = TIMESTAMP_PATTERN.search(line)
        if match:
            return match.group(0)
    return None


def extract_fields(clean_lines: list[str]) -> dict:
    """Extract callsign, timestamp and helper snippets for UI rendering."""

    callsign = _find_callsign(clean_lines)
    ts = _find_timestamp(clean_lines[:2]) or _find_timestamp(clean_lines)

    primary_text = ""
    for line in clean_lines:
        if callsign and callsign in line:
            primary_text = line.strip()
            break
    if not primary_text:
        primary_text = next((line.strip() for line in clean_lines if line.strip()), "")

    preview_lines: list[str] = []
    for line in clean_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not preview_lines and stripped in TYPE_TOKENS:
            continue
        preview_lines.append(stripped)
        if len(preview_lines) == 4:
            break
    preview_text = "\n".join(preview_lines)

    summary = primary_text
    if callsign and callsign not in summary:
        summary = f"{callsign} — {summary}" if summary else callsign

    metadata = {
        "callsign": callsign,
        "ts": ts,
        "summary": summary,
        "preview_text": preview_text or summary,
    }

    metadata["json"] = json.dumps(
        {
            "callsign": callsign,
            "timestamp": ts,
            "lines": clean_lines,
        },
        ensure_ascii=False,
        indent=2,
    )

    return metadata
