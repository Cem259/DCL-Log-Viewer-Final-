from __future__ import annotations

import pytest

from dcl_editor.startup import ensure_supported_python


def test_ensure_supported_python_accepts_supported_versions():
    # Should not raise for supported interpreters.
    ensure_supported_python(version_info=(3, 10, 0), version_string="3.10.0")
    ensure_supported_python(version_info=(3, 12, 5), version_string="3.12.5")
    ensure_supported_python(version_info=(3, 13, 1), version_string="3.13.1")


@pytest.mark.parametrize(
    "version_info, version_string",
    [
        ((3, 9, 0), "3.9.0"),
        ((3, 15, 0), "3.15.0"),
        ((2, 7, 0), "2.7.0"),
    ],
)
def test_ensure_supported_python_rejects_unsupported_versions(version_info, version_string):
    with pytest.raises(SystemExit) as excinfo:
        ensure_supported_python(version_info=version_info, version_string=version_string)

    message = str(excinfo.value)
    assert "supports Python" in message
    assert version_string in message
