from __future__ import annotations

import sys
from typing import Iterable, NoReturn


SUPPORTED_MINOR_VERSIONS = (10, 11, 12, 13)


def _format_supported(versions: Iterable[int]) -> str:
    return ", ".join(f"3.{minor}" for minor in versions)


def fail_startup(message: str) -> NoReturn:
    raise SystemExit("\n" + message + "\n")


def ensure_supported_python(
    version_info: tuple[int, ...] | None = None,
    version_string: str | None = None,
) -> None:
    version_info = version_info or sys.version_info
    version_string = version_string or sys.version.split()[0]
    major, minor = version_info[:2]
    if major != 3 or minor not in SUPPORTED_MINOR_VERSIONS:
        supported = _format_supported(SUPPORTED_MINOR_VERSIONS)
        fail_startup(
            (
                "[Startup check] This app supports Python {supported}. Detected: {ver}\n"
                "Install a supported interpreter, activate the project venv:\n"
                "  .venv\\Scripts\\activate\n"
                "Then run:\n"
                "  python -m dcl_editor.app"
            ).format(supported=supported, ver=version_string)
        )
