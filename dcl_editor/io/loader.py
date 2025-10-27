from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from ..core.classifier import classify_block
from ..core.extractor import extract_fields
from ..core.models import DclBlock, DclType
from ..core.normalizer import normalize_block
from ..core.tokenizer import tokenize_blocks


class LogLoader:
    """Load DCL log blocks from an ASMGCS DEBUG.log file."""

    def __init__(self) -> None:
        self._source: Path | None = None
        self._raw_cache: str = ""

    def load(self, path: str | Path) -> List[DclBlock]:
        self._source = Path(path)
        data = self._source.read_text(encoding="utf-8", errors="ignore")
        self._raw_cache = data
        return self._build_blocks(data)

    def reload(self) -> List[DclBlock]:
        if not self._source:
            return []
        data = self._source.read_text(encoding="utf-8", errors="ignore")
        self._raw_cache = data
        return self._build_blocks(data)

    def _build_blocks(self, data: str) -> List[DclBlock]:
        blocks: List[DclBlock] = []
        raw_blocks = tokenize_blocks(data)
        search_pos = 0
        for raw in raw_blocks:
            start = data.find(raw, search_pos)
            if start == -1:
                start = search_pos
            end = start + len(raw)
            search_pos = end
            clean = normalize_block(raw)
            lines = clean.split("\n") if clean else []
            block_type: DclType = classify_block(lines)
            fields = extract_fields(lines)
            summary = fields.get("summary") or (lines[0] if lines else "")
            preview = fields.get("preview_text") or clean
            block = DclBlock(
                start_offset=start,
                end_offset=end,
                ts=fields.get("ts"),
                type=block_type,
                callsign=fields.get("callsign"),
                summary=summary,
                preview_text=preview,
                full_block_text=clean,
                metadata_json=fields.get("json"),
            )
            blocks.append(block)
        return blocks


def load_blocks_from_stream(stream: Iterable[str] | str) -> List[DclBlock]:
    data = stream.read() if hasattr(stream, "read") else str(stream)
    loader = LogLoader()
    return loader._build_blocks(data)
