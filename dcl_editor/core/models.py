from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


DclType = Literal["RCD", "CLD", "CDA", "FSM", "UNKNOWN"]


@dataclass(slots=True)
class DclBlock:
    """Represents a cleaned and classified DCL exchange extracted from the log."""

    start_offset: int
    end_offset: int
    ts: Optional[str]
    type: DclType
    callsign: Optional[str]
    summary: str
    preview_text: str
    full_block_text: str
    metadata_json: str | None = None

    def matches_callsign(self, callsign: str | None) -> bool:
        if not callsign:
            return True
        if not self.callsign:
            return False
        return self.callsign.upper().startswith(callsign.upper())

    def matches_type(self, allowed_types: set[DclType] | None) -> bool:
        if not allowed_types:
            return True
        return self.type in allowed_types
