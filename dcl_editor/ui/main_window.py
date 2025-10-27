from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QHBoxLayout,
    QSplitter,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..core.models import DclBlock, DclType
from ..io.indexer import DclIndexer
from ..io.loader import LogLoader
from .dialogs import DetailDialog
from .theme import ThemeMode, apply_theme, build_stylesheet
from .widgets import BlockTableModel, CallsignFilter, ResultsView, ScenarioInput


AVAILABLE_SCENARIOS: set[DclType] = {"RCD", "CLD", "CDA", "FSM", "UNKNOWN"}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DCL Exchange Viewer")
        self.resize(1200, 720)

        self.loader = LogLoader()
        self.indexer = DclIndexer()
        self.blocks: list[DclBlock] = []
        self.filtered: list[DclBlock] = []

        self._current_path: Path | None = None
        self._follow_mode = False
        self._follow_timer = QTimer(self)
        self._follow_timer.setInterval(2000)
        self._follow_timer.timeout.connect(self._refresh_from_disk)
        self._theme_mode = ThemeMode.LIGHT
        self._theme_button: QToolButton | None = None
        self._scenario_types: set[DclType] | None = None

        self._create_ui()

    # UI creation -----------------------------------------------------
    def _create_ui(self) -> None:
        container = QWidget(self)
        container.setObjectName("CentralWrapper")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = QWidget(self)
        top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 18, 24, 18)
        top_layout.setSpacing(16)

        title = QLabel("DCL Exchange Viewer", top_bar)
        title.setObjectName("AppTitle")
        top_layout.addWidget(title)
        top_layout.addStretch(1)

        top_layout.addWidget(
            self._create_action_button(
                "Open Log",
                QStyle.SP_DialogOpenButton,
                callback=self._open_file_dialog,
            )
        )
        top_layout.addWidget(
            self._create_action_button(
                "Refresh",
                QStyle.SP_BrowserReload,
                callback=self._refresh_from_disk,
            )
        )
        top_layout.addWidget(
            self._create_action_button(
                "Follow",
                QStyle.SP_MediaPlay,
                toggled=self._toggle_follow,
                checkable=True,
            )
        )
        self._theme_button = self._create_action_button(
            "Light Mode",
            QStyle.SP_DialogApplyButton,
            toggled=self._toggle_light_mode,
            checkable=True,
            checked=self._theme_mode is ThemeMode.LIGHT,
        )
        top_layout.addWidget(self._theme_button)

        layout.addWidget(top_bar)

        quick_strip = QWidget(self)
        quick_strip.setObjectName("ActionStrip")
        quick_layout = QHBoxLayout(quick_strip)
        quick_layout.setContentsMargins(24, 10, 24, 10)
        quick_layout.setSpacing(12)

        quick_label = QLabel("Quick Actions", quick_strip)
        quick_label.setObjectName("SectionTitle")
        quick_layout.addWidget(quick_label)
        quick_layout.addStretch(1)

        quick_layout.addWidget(
            self._create_quick_button(
                "Copy Text",
                QStyle.SP_FileDialogContentsView,
                lambda: self._invoke_on_current(self._copy_text),
            )
        )
        quick_layout.addWidget(
            self._create_quick_button(
                "Copy JSON",
                QStyle.SP_FileDialogDetailedView,
                lambda: self._invoke_on_current(self._copy_json),
            )
        )

        layout.addWidget(quick_strip)

        self.model = BlockTableModel()
        self.results = ResultsView(self)
        self.results.setObjectName("ResultsView")
        self.results.setProperty("compact", False)
        self.results.setModel(self.model)
        self.results.doubleClicked.connect(self._open_detail)
        self.results.register_action("Copy as Text", self._copy_text)
        self.results.register_action("Copy as JSON", self._copy_json)

        self.callsign_filter = CallsignFilter(self)
        self.callsign_filter.setObjectName("CallsignFilter")
        self.callsign_filter.input.setObjectName("CallsignInput")
        self.callsign_filter.input.textChanged.connect(self._on_filter_changed)

        self.scenario_input = ScenarioInput(self)
        self.scenario_input.setObjectName("ScenarioFilter")
        self.scenario_input.input.setObjectName("ScenarioInputField")
        self.scenario_input.input.textChanged.connect(self._on_scenario_changed)

        filter_panel = QWidget(self)
        filter_panel.setObjectName("FilterPanel")
        filter_layout = QVBoxLayout(filter_panel)
        filter_layout.setContentsMargins(20, 20, 20, 20)
        filter_layout.setSpacing(16)

        callsign_label = QLabel("Callsign", self)
        callsign_label.setObjectName("FilterLabel")
        filter_layout.addWidget(callsign_label)
        filter_layout.addWidget(self.callsign_filter)

        scenario_label = QLabel("Scenario", self)
        scenario_label.setObjectName("FilterLabel")
        filter_layout.addWidget(scenario_label)
        filter_layout.addWidget(self.scenario_input)

        scenario_hint = QLabel(
            "Accepted codes: RCD, CLD, CDA, FSM, UNKNOWN",
            self,
        )
        scenario_hint.setObjectName("FilterHint")
        filter_layout.addWidget(scenario_hint)

        clear_filters = QToolButton(self)
        clear_filters.setObjectName("FilterButton")
        clear_filters.setText("Clear Filters")
        clear_filters.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        clear_filters.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        clear_filters.setCursor(Qt.PointingHandCursor)
        clear_filters.clicked.connect(self._clear_filters)
        filter_layout.addWidget(clear_filters)

        filter_layout.addStretch(1)

        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(filter_panel)
        splitter.addWidget(self.results)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        central = QWidget(self)
        central.setObjectName("CentralWidget")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(splitter)

        layout.addWidget(central, 1)
        self.setCentralWidget(container)
        self._apply_styles(self._theme_mode)

    def _create_action_button(
        self,
        text: str,
        icon: QStyle.StandardPixmap,
        callback: callable | None = None,
        *,
        toggled: callable | None = None,
        checkable: bool = False,
        checked: bool = False,
    ) -> QToolButton:
        button = QToolButton(self)
        button.setObjectName("ActionButton")
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setIcon(self.style().standardIcon(icon))
        button.setIconSize(QSize(28, 28))
        button.setText(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setCheckable(checkable)
        if checkable:
            button.setChecked(checked)
        if callback:
            button.clicked.connect(callback)  # type: ignore[arg-type]
        if toggled:
            button.toggled.connect(toggled)  # type: ignore[arg-type]
        return button

    def _create_quick_button(
        self,
        text: str,
        icon: QStyle.StandardPixmap,
        callback: callable,
    ) -> QToolButton:
        button = QToolButton(self)
        button.setObjectName("QuickAction")
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setIcon(self.style().standardIcon(icon))
        button.setIconSize(QSize(24, 24))
        button.setText(text)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)  # type: ignore[arg-type]
        return button

    def _invoke_on_current(self, handler: callable) -> None:
        index = self.results.currentIndex()
        if index.isValid():
            handler(index)

    def _apply_styles(self, mode: ThemeMode) -> None:
        self.setStyleSheet(build_stylesheet(mode))
        if self._theme_button and bool(self._theme_button.isChecked()) != (
            mode is ThemeMode.LIGHT
        ):
            self._theme_button.blockSignals(True)
            self._theme_button.setChecked(mode is ThemeMode.LIGHT)
            self._theme_button.blockSignals(False)
        self._update_theme_button_text()

    def _clear_filters(self) -> None:
        self.callsign_filter.input.clear()
        self.scenario_input.input.clear()
        self._scenario_types = None

    def _toggle_compact_mode(self, enabled: bool) -> None:
        header = self.results.header()
        if enabled:
            self.results.setProperty("compact", True)
            self.results.setAlternatingRowColors(False)
            header.setDefaultAlignment(Qt.AlignCenter)
        else:
            self.results.setProperty("compact", False)
            self.results.setAlternatingRowColors(True)
            header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.results.style().unpolish(self.results)
        self.results.style().polish(self.results)
        self.results.viewport().update()

    def _toggle_light_mode(self, enabled: bool) -> None:
        self._theme_mode = ThemeMode.LIGHT if enabled else ThemeMode.DARK
        apply_theme(QApplication.instance(), self._theme_mode)
        self._apply_styles(self._theme_mode)
        self._update_theme_button_text()

    def _update_theme_button_text(self) -> None:
        if not self._theme_button:
            return
        self._theme_button.setText("Light Mode" if self._theme_mode is ThemeMode.LIGHT else "Dark Mode")

    # Actions ---------------------------------------------------------
    def _open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open DEBUG.log", str(Path.home()), "Log files (*.log *.txt *.*)")
        if path:
            self._load_path(Path(path))

    def _load_path(self, path: Path) -> None:
        try:
            blocks = self.loader.load(path)
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{exc}")
            return
        self._current_path = path
        self._update_blocks(blocks)

    def _refresh_from_disk(self) -> None:
        if not self._current_path:
            return
        blocks = self.loader.reload()
        self._update_blocks(blocks)

    def _update_blocks(self, blocks: Iterable[DclBlock]) -> None:
        self.blocks = list(blocks)
        self.indexer.rebuild(self.blocks)
        self._apply_filters()

    def _apply_filters(self) -> None:
        callsign = self.callsign_filter.input.text().strip().upper()
        scenario_types = self._scenario_types

        if scenario_types is not None and not scenario_types:
            self.filtered = []
            self.model.set_blocks(self.filtered)
            return

        allowed_types = scenario_types if scenario_types else None
        self.filtered = self.indexer.filter(callsign or None, allowed_types)
        self.model.set_blocks(self.filtered)
        self.results.sortByColumn(0, Qt.AscendingOrder)

    def _on_filter_changed(self, _text: str) -> None:
        self._apply_filters()

    def _on_scenario_changed(self, text: str) -> None:
        self._scenario_types = self._parse_scenario_text(text)
        self._apply_filters()

    def _parse_scenario_text(self, text: str) -> set[DclType] | None:
        raw = [segment.strip().upper() for segment in text.replace(";", ",").split(",") if segment.strip()]
        if not raw:
            return None
        valid = {token for token in raw if token in AVAILABLE_SCENARIOS}
        return valid

    def _open_detail(self, index) -> None:
        block = self.model.block_at(index)
        if not block:
            return
        dialog = DetailDialog(block.full_block_text, self)
        dialog.exec()

    def _copy_text(self, index) -> None:
        block = self.model.block_at(index)
        if not block:
            return
        QApplication.clipboard().setText(block.full_block_text)

    def _copy_json(self, index) -> None:
        block = self.model.block_at(index)
        if not block:
            return
        payload = block.metadata_json or ""
        QApplication.clipboard().setText(payload)

    def _toggle_follow(self, enabled: bool) -> None:
        self._follow_mode = enabled
        if enabled:
            self._follow_timer.start()
        else:
            self._follow_timer.stop()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._follow_timer.isActive():
            self._follow_timer.stop()
        super().closeEvent(event)
