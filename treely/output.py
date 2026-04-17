"""
treely.output
~~~~~~~~~~~~~
Output handling: banner, clipboard, file writing, stdout.
All I/O concerns that aren't filesystem traversal or rendering live here.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

try:
    import pyperclip  # type: ignore[import]
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False


# ── Banner ────────────────────────────────────────────────────────────────────

_BANNER_LINES = [
    "  _______            _       ",
    " |__   __|          | |      ",
    "    | |_ __ ___  ___| |_   _ ",
    "    | | '__/ _ \\/ _ \\ | | | |",
    "    | | | |  __/  __/ | |_| |",
    "    |_|_|  \\___|\\___|_|\\__, |",
    "                        __/ |",
    "                       |___/ ",
]

_GREEN = "\033[32m"
_RESET = "\033[0m"
_BOLD_GREEN = "\033[1;32m"


def print_banner(no_banner: bool = False, no_color: bool = False) -> None:
    """
    Print the treely ASCII art banner with an animated delay.
    Suppressed when *no_banner* is ``True`` (e.g. ``--no-banner`` flag or
    piped output).
    """
    if no_banner:
        return

    color = "" if no_color else _GREEN
    reset = "" if no_color else _RESET

    for line in _BANNER_LINES:
        print(color + line + reset)
        time.sleep(0.01)

    time.sleep(0.3)


# ── Success / error messages ──────────────────────────────────────────────────

def _green(msg: str) -> str:
    return f"\033[32m{msg}\033[0m"


def _red(msg: str) -> str:
    return f"\033[31m{msg}\033[0m"


# ── Clipboard ─────────────────────────────────────────────────────────────────

def copy_to_clipboard(content: str) -> None:
    """
    Copy *content* to the system clipboard using ``pyperclip``.
    Prints a success or error message.  Exits with code 1 on failure.
    """
    if not _PYPERCLIP:
        print(
            _red(
                "Error: 'pyperclip' is not installed. "
                "Run 'pip install pyperclip' to use --copy."
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        pyperclip.copy(content)
        print(_green("✔ Output copied to clipboard."))
    except Exception as exc:  # pyperclip.PyperclipException
        print(_red(f"Error: Could not copy to clipboard: {exc}"), file=sys.stderr)
        sys.exit(1)


# ── File writing ──────────────────────────────────────────────────────────────

def write_to_file(content: str, filename: str) -> None:
    """
    Write *content* to *filename*.
    Prints a success or error message.  Exits with code 1 on failure.
    """
    try:
        Path(filename).write_text(content, encoding="utf-8")
        print(_green(f"✔ Output successfully saved to {filename}"))
    except OSError as exc:
        print(_red(f"Error: Could not write to file '{filename}': {exc}"), file=sys.stderr)
        sys.exit(1)


# ── Validation helpers ────────────────────────────────────────────────────────

def check_pyperclip() -> None:
    """Print an error and exit if pyperclip is not installed."""
    if not _PYPERCLIP:
        print(
            _red(
                "Error: 'pyperclip' is not installed. "
                "Please run 'pip install pyperclip' to use --copy."
            ),
            file=sys.stderr,
        )
        sys.exit(1)


def check_pathspec() -> None:
    """Print an error and exit if pathspec is not installed."""
    try:
        import pathspec  # noqa: F401  # type: ignore[import]
    except ImportError:
        print(
            _red(
                "Error: 'pathspec' is not installed. "
                "Please run 'pip install pathspec' to use --use-gitignore."
            ),
            file=sys.stderr,
        )
        sys.exit(1)
