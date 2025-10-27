from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence

from ..core.models import DclBlock, DclType


class DclIndexer:
    """Maintain indices to filter DCL blocks efficiently."""

    def __init__(self) -> None:
        self.blocks: List[DclBlock] = []
        self.callsign_index: Dict[str, List[int]] = defaultdict(list)
        self.type_index: Dict[DclType, List[int]] = defaultdict(list)

    def rebuild(self, blocks: Sequence[DclBlock]) -> None:
        self.blocks = list(blocks)
        self.callsign_index.clear()
        self.type_index.clear()
        for idx, block in enumerate(self.blocks):
            if block.callsign:
                self.callsign_index[block.callsign.upper()].append(idx)
            self.type_index[block.type].append(idx)

    def filter(self, callsign: str | None, allowed_types: Iterable[DclType] | None) -> List[DclBlock]:
        if not self.blocks:
            return []

        normalized_callsign = callsign.upper() if callsign else None
        allowed_set = set(allowed_types) if allowed_types else None

        if normalized_callsign:
            matching_indices = [
                idx
                for key, indices in self.callsign_index.items()
                if key.startswith(normalized_callsign)
                for idx in indices
            ]
        else:
            matching_indices = list(range(len(self.blocks)))

        filtered: List[DclBlock] = []
        for idx in matching_indices:
            block = self.blocks[idx]
            if allowed_set and block.type not in allowed_set:
                continue
            filtered.append(block)
        return filtered

    def types_present(self) -> Dict[DclType, int]:
        return {key: len(indices) for key, indices in self.type_index.items()}
