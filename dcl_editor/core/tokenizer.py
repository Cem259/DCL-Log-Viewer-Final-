from __future__ import annotations

from typing import Iterable, List


START_TOKEN = "<STX>"
END_TOKEN = "<ETX>"


def _coerce_to_text(stream: Iterable[str] | str) -> str:
    if isinstance(stream, str):
        return stream
    if hasattr(stream, "read"):
        return stream.read()
    return "".join(stream)


def tokenize_blocks(stream: Iterable[str] | str) -> List[str]:
    """Return all <STX> .. <ETX> blocks found in *stream*.

    The function is resilient to partial noise outside of the control tokens and
    simply ignores dangling <STX> without a matching <ETX>.
    """

    text = _coerce_to_text(stream)
    blocks: List[str] = []
    search_pos = 0

    while True:
        start = text.find(START_TOKEN, search_pos)
        if start == -1:
            break
        end = text.find(END_TOKEN, start + len(START_TOKEN))
        if end == -1:
            break
        end += len(END_TOKEN)
        block = text[start:end]
        blocks.append(block)
        search_pos = end

    return blocks
