from __future__ import annotations

import re

CRLF_TOKEN = "<CR><LF>"
LF_TOKEN = "<LF>"
CR_TOKEN = "<CR>"
SPACE_TOKEN = "<SP>"
CONTROL_PATTERN = re.compile(r"<(?:STX|ETX|CR|LF|SP)>")
ANGLE_PATTERN = re.compile(r"[<>]")


def normalize_block(raw: str) -> str:
    """Convert control tokens in *raw* to a readable multi-line string."""

    if not raw:
        return ""

    text = raw
    text = text.replace(CRLF_TOKEN, "\n")
    text = text.replace(LF_TOKEN, "\n")
    text = text.replace(CR_TOKEN, "\n")
    text = text.replace(SPACE_TOKEN, " ")
    text = CONTROL_PATTERN.sub("", text)
    text = ANGLE_PATTERN.sub("", text)
    lines = [line.rstrip() for line in text.splitlines()]
    normalized_lines: list[str] = []
    for line in lines:
        if not line:
            continue
        if line.startswith("-") or line.startswith("/"):
            line = line[1:].lstrip()
        if not line:
            continue
        normalized_lines.append(line)
    return "\n".join(normalized_lines).strip()
