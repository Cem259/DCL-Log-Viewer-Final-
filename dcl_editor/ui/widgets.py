from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMenu,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ..core.models import DclBlock, DclType


@dataclass
class FilterState:
    callsign: str = ""
    types: set[DclType] | None = None


class BlockTableModel(QAbstractTableModel):
    columns = ("Time", "Type", "Callsign", "Summary")

    def __init__(self, blocks: Iterable[DclBlock] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._blocks: List[DclBlock] = list(blocks or [])

    def rowCount(self, parent: QModelIndex | None = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent and parent.isValid() else len(self._blocks)

    def columnCount(self, parent: QModelIndex | None = QModelIndex()) -> int:  # type: ignore[override]
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        block = self._blocks[index.row()]
        if role == Qt.DisplayRole:
            column = index.column()
            if column == 0:
                return block.ts or ""
            if column == 1:
                return block.type
            if column == 2:
                return block.callsign or ""
            if column == 3:
                return block.summary
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section]
        return super().headerData(section, orientation, role)

    def block_at(self, index: QModelIndex) -> DclBlock | None:
        if not index.isValid():
            return None
        row = index.row()
        if 0 <= row < len(self._blocks):
            return self._blocks[row]
        return None

    def set_blocks(self, blocks: Iterable[DclBlock]) -> None:
        self.beginResetModel()
        self._blocks = list(blocks)
        self.endResetModel()


class CallsignFilter(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Filter by callsign (e.g. THY1QN)")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input)


class ScenarioInput(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Enter scenario code (e.g. RCD)")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input)


class TypeChips(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._buttons: dict[DclType, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        for t in ("RCD", "CLD", "CDA", "FSM"):
            button = QPushButton(t, self)
            button.setCheckable(True)
            button.setChecked(True)
            button.clicked.connect(self._emit_state_change)  # type: ignore[arg-type]
            layout.addWidget(button)
            self._buttons[t] = button  # type: ignore[index]
        layout.addStretch(1)
        self._callbacks: List[callable[[set[DclType]], None]] = []

    def set_all_checked(self, checked: bool) -> None:
        for button in self._buttons.values():
            button.setChecked(checked)
        self._emit_state_change()

    def _emit_state_change(self) -> None:
        active = {dtype for dtype, btn in self._buttons.items() if btn.isChecked()}
        for callback in self._callbacks:
            callback(active)

    def on_changed(self, callback: callable[[set[DclType]], None]) -> None:
        self._callbacks.append(callback)


class ResultsView(QTreeView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setUniformRowHeights(True)
        self.setRootIsDecorated(False)
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        header = self.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self._context_actions: list[tuple[str, callable]] = []

    def register_action(self, title: str, callback: callable) -> None:
        self._context_actions.append((title, callback))

    def _show_context_menu(self, pos) -> None:
        index = self.indexAt(pos)
        if not index.isValid():
            return
        menu = QMenu(self)
        for title, callback in self._context_actions:
            action = QAction(title, self)
            action.triggered.connect(lambda _=False, cb=callback: cb(index))  # type: ignore[arg-type]
            menu.addAction(action)
        menu.exec(self.viewport().mapToGlobal(pos))
