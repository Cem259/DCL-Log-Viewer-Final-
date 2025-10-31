from __future__ import annotations

import sys

from .startup import ensure_supported_python, fail_startup


ensure_supported_python()

try:
    import PySide6  # noqa: F401
except Exception:  # pragma: no cover - guard path
    fail_startup(
        "[Startup check] 'PySide6' is not importable under this interpreter.\n"
        "Fix:\n"
        "  .venv\\Scripts\\activate\n"
        "  python -m pip install -r requirements.txt\n"
        f"(Python exe: {sys.executable})"
    )

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.splash_intro import SplashIntro
from .ui.theme import ThemeMode, apply_theme


def main() -> int:
    """Run the DCL Editor application and return the exit status."""

    app = QApplication(sys.argv)
    apply_theme(app, ThemeMode.LIGHT)

    window = MainWindow()

    splash = SplashIntro()

    def _launch_main() -> None:
        window.show()

    splash.finished.connect(_launch_main)
    splash.start()

    return app.exec()
