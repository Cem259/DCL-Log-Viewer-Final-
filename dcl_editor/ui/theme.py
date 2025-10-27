from __future__ import annotations

from enum import Enum

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


class ThemeMode(str, Enum):
    DARK = "dark"
    LIGHT = "light"


_DARK_PRIMARY = QColor(138, 92, 255)
_DARK_ACCENT = QColor(255, 98, 146)
_DARK_BACKGROUND = QColor(8, 10, 24)
_DARK_SURFACE = QColor(18, 22, 40)
_DARK_TEXT = QColor(233, 235, 255)
_DARK_MUTED = QColor(130, 134, 166)

_LIGHT_PRIMARY = QColor(92, 63, 211)
_LIGHT_ACCENT = QColor(255, 113, 172)
_LIGHT_BACKGROUND = QColor(242, 244, 255)
_LIGHT_SURFACE = QColor(255, 255, 255)
_LIGHT_TEXT = QColor(34, 38, 58)
_LIGHT_MUTED = QColor(110, 118, 156)


def apply_theme(app: QApplication | None, mode: ThemeMode = ThemeMode.LIGHT) -> None:
    if app is None:
        return

    palette = QPalette()

    if mode is ThemeMode.LIGHT:
        palette.setColor(QPalette.Window, _LIGHT_BACKGROUND)
        palette.setColor(QPalette.WindowText, _LIGHT_TEXT)
        palette.setColor(QPalette.Base, _LIGHT_SURFACE)
        palette.setColor(QPalette.AlternateBase, QColor(230, 232, 255))
        palette.setColor(QPalette.ToolTipBase, _LIGHT_SURFACE)
        palette.setColor(QPalette.ToolTipText, _LIGHT_TEXT)
        palette.setColor(QPalette.Text, _LIGHT_TEXT)
        palette.setColor(QPalette.Button, QColor(226, 224, 248))
        palette.setColor(QPalette.ButtonText, _LIGHT_TEXT)
        palette.setColor(QPalette.Highlight, _LIGHT_PRIMARY)
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        palette.setColor(QPalette.BrightText, QColor("black"))
        palette.setColor(QPalette.PlaceholderText, _LIGHT_MUTED)
        palette.setColor(QPalette.Link, _LIGHT_ACCENT)
    else:
        palette.setColor(QPalette.Window, _DARK_BACKGROUND)
        palette.setColor(QPalette.WindowText, _DARK_TEXT)
        palette.setColor(QPalette.Base, _DARK_SURFACE)
        palette.setColor(QPalette.AlternateBase, QColor(28, 32, 58))
        palette.setColor(QPalette.ToolTipBase, _DARK_SURFACE)
        palette.setColor(QPalette.ToolTipText, _DARK_TEXT)
        palette.setColor(QPalette.Text, _DARK_TEXT)
        palette.setColor(QPalette.Button, QColor(32, 28, 62))
        palette.setColor(QPalette.ButtonText, _DARK_TEXT)
        palette.setColor(QPalette.Highlight, _DARK_PRIMARY)
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        palette.setColor(QPalette.BrightText, QColor("white"))
        palette.setColor(QPalette.PlaceholderText, _DARK_MUTED)
        palette.setColor(QPalette.Link, _DARK_ACCENT)

    app.setPalette(palette)


def build_stylesheet(mode: ThemeMode) -> str:
    if mode is ThemeMode.LIGHT:
        return """
            QMainWindow {
                background-color: #f2f4ff;
                color: #22263a;
            }
            QWidget#TopBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                              stop:0 rgba(255, 255, 255, 0.95),
                              stop:1 rgba(210, 214, 255, 0.95));
                border-bottom: 1px solid rgba(110, 118, 156, 0.2);
            }
            QLabel#AppTitle {
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 1px;
                color: #4b2fd8;
            }
            QWidget#ActionStrip {
                background: rgba(255, 255, 255, 0.92);
                border-bottom: 1px solid rgba(110, 118, 156, 0.18);
            }
            QLabel#SectionTitle {
                text-transform: uppercase;
                font-size: 12px;
                color: #5a4fee;
                letter-spacing: 1.4px;
            }
            QToolButton#ActionButton {
                background: rgba(92, 63, 211, 0.14);
                border: 1px solid rgba(92, 63, 211, 0.3);
                border-radius: 16px;
                padding: 10px 18px;
                font-weight: 600;
                color: #332d7a;
            }
            QToolButton#ActionButton:hover {
                background: rgba(92, 63, 211, 0.24);
            }
            QToolButton#ActionButton:checked {
                background: rgba(255, 113, 172, 0.35);
                border-color: rgba(255, 113, 172, 0.6);
                color: #2a1f4a;
            }
            QToolButton#QuickAction {
                background: rgba(255, 113, 172, 0.22);
                border: 1px solid rgba(255, 113, 172, 0.4);
                border-radius: 14px;
                padding: 9px 16px;
                font-weight: 600;
                color: #4f154f;
            }
            QToolButton#QuickAction:hover {
                background: rgba(255, 113, 172, 0.35);
            }
            QWidget#FilterPanel {
                background: rgba(255, 255, 255, 0.86);
                border-right: 1px solid rgba(110, 118, 156, 0.18);
            }
            QLabel#FilterLabel {
                text-transform: uppercase;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.6px;
                color: #5a4fee;
            }
            QLabel#FilterHint {
                color: #6c78a0;
                font-size: 11px;
            }
            QToolButton#FilterButton {
                margin-top: 8px;
                background: rgba(92, 63, 211, 0.12);
                border: 1px solid rgba(92, 63, 211, 0.28);
                border-radius: 14px;
                padding: 8px 14px;
                color: #2f2f6f;
            }
            QToolButton#FilterButton:hover {
                background: rgba(92, 63, 211, 0.2);
            }
            QLineEdit#CallsignInput, QLineEdit#ScenarioInputField {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(92, 63, 211, 0.35);
                border-radius: 12px;
                padding: 10px 14px;
                color: #22263a;
            }
            QLineEdit#CallsignInput:focus, QLineEdit#ScenarioInputField:focus {
                border: 1px solid rgba(255, 113, 172, 0.7);
                box-shadow: 0 0 0 3px rgba(255, 113, 172, 0.35);
            }
            QTreeView#ResultsView {
                background: rgba(255, 255, 255, 0.93);
                alternate-background-color: rgba(210, 214, 255, 0.4);
                border: none;
                color: #22263a;
                gridline-color: rgba(110, 118, 156, 0.25);
            }
            QTreeView#ResultsView::item {
                padding: 12px 10px;
            }
            QTreeView#ResultsView[compact="true"]::item {
                padding: 6px 6px;
            }
            QTreeView#ResultsView::item:selected {
                background: rgba(92, 63, 211, 0.35);
                color: #1a1033;
            }
            QHeaderView::section {
                background: rgba(92, 63, 211, 0.18);
                color: #332d7a;
                border: none;
                padding: 8px 10px;
            }
        """

    return """
        QMainWindow {
            background-color: #080a18;
            color: #e9ebff;
        }
        QWidget#TopBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                          stop:0 rgba(26, 20, 52, 0.9),
                          stop:1 rgba(12, 18, 42, 0.95));
            border-bottom: 1px solid rgba(130, 134, 166, 0.22);
        }
        QLabel#AppTitle {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 1px;
            color: #c7b6ff;
        }
        QWidget#ActionStrip {
            background: rgba(18, 22, 40, 0.88);
            border-bottom: 1px solid rgba(130, 134, 166, 0.2);
        }
        QLabel#SectionTitle {
            text-transform: uppercase;
            font-size: 12px;
            color: #ff76c0;
            letter-spacing: 1.4px;
        }
        QToolButton#ActionButton {
            background: rgba(138, 92, 255, 0.22);
            border: 1px solid rgba(138, 92, 255, 0.35);
            border-radius: 16px;
            padding: 10px 18px;
            font-weight: 600;
            color: #f0edff;
        }
        QToolButton#ActionButton:hover {
            background: rgba(138, 92, 255, 0.35);
        }
        QToolButton#ActionButton:checked {
            background: rgba(255, 98, 146, 0.4);
            border-color: rgba(255, 98, 146, 0.6);
            color: #1c102d;
        }
        QToolButton#QuickAction {
            background: rgba(255, 98, 146, 0.3);
            border: 1px solid rgba(255, 98, 146, 0.45);
            border-radius: 14px;
            padding: 9px 16px;
            font-weight: 600;
            color: #ffe4f0;
        }
        QToolButton#QuickAction:hover {
            background: rgba(255, 98, 146, 0.45);
        }
        QWidget#FilterPanel {
            background: rgba(18, 22, 40, 0.92);
            border-right: 1px solid rgba(130, 134, 166, 0.25);
        }
        QLabel#FilterLabel {
            text-transform: uppercase;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.6px;
            color: #9f8cff;
        }
        QLabel#FilterHint {
            color: #9ba3ce;
            font-size: 11px;
        }
        QToolButton#FilterButton {
            margin-top: 8px;
            background: rgba(138, 92, 255, 0.24);
            border: 1px solid rgba(138, 92, 255, 0.35);
            border-radius: 14px;
            padding: 8px 14px;
            color: #f1f2ff;
        }
        QToolButton#FilterButton:hover {
            background: rgba(138, 92, 255, 0.4);
        }
        QLineEdit#CallsignInput, QLineEdit#ScenarioInputField {
            background: rgba(8, 10, 24, 0.75);
            border: 1px solid rgba(138, 92, 255, 0.45);
            border-radius: 12px;
            padding: 10px 14px;
            color: #f5f7ff;
        }
        QLineEdit#CallsignInput:focus, QLineEdit#ScenarioInputField:focus {
            border: 1px solid rgba(255, 98, 146, 0.7);
            box-shadow: 0 0 0 3px rgba(255, 98, 146, 0.35);
        }
        QTreeView#ResultsView {
            background: rgba(8, 10, 24, 0.86);
            alternate-background-color: rgba(62, 44, 126, 0.45);
            border: none;
            color: #f5f7ff;
            gridline-color: rgba(130, 134, 166, 0.25);
        }
        QTreeView#ResultsView::item {
            padding: 12px 10px;
        }
        QTreeView#ResultsView[compact="true"]::item {
            padding: 6px 6px;
        }
        QTreeView#ResultsView::item:selected {
            background: rgba(138, 92, 255, 0.5);
            color: #0b041a;
        }
        QHeaderView::section {
            background: rgba(138, 92, 255, 0.3);
            color: #f5f1ff;
            border: none;
            padding: 8px 10px;
        }
    """
