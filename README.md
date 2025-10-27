# DCL V2

A Qt-based desktop viewer that extracts and filters DCL-related ATC exchanges from ASMGCS `DEBUG.log` files.

## Features

- Tokenizes `<STX>…<ETX>` blocks and converts tagged whitespace/control tokens into readable text.
- Classifies messages as `RCD`, `CLD`, `CDA`, `FSM`, or `UNKNOWN` using header hints.
- Extracts callsigns, timestamps, and summary lines for quick scanning.
- Ribbon-style main window with callsign and message-type filters, live tailing, and context menu copy actions.
- Double-click a row to view the entire cleaned message block.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m dcl_editor.app
```

## Run on Python 3.13 (Windows)
1) scripts\win_bootstrap.bat
2) .\\.venv\Scripts\activate
3) python -m dcl_editor.app

If you see 'PySide6 is not importable', you're likely outside the venv or missing wheels for your Python version; rerun bootstrap after installing a supported interpreter from the 3.10–3.13 range.

## Running tests

```bash
pytest
```
