"""
treely.theme
~~~~~~~~~~~~
Theme definitions for the rich-powered rendering engine.
Each Theme is a frozen dataclass that maps semantic roles to rich style strings.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Theme:
    """Maps semantic tree roles to rich style strings."""

    name: str

    # Directory / file names
    dir_style: str
    file_style: str
    hidden_style: str
    special_style: str      # .env, Dockerfile, Makefile, etc.
    binary_style: str       # binary files
    link_style: str         # symlinks
    error_style: str

    # Size badge
    size_style: str

    # Git status
    git_modified: str
    git_added: str
    git_untracked: str
    git_deleted: str
    git_ignored: str

    # Rich Tree guide lines
    guide_style: str

    # Code section header
    header_style: str
    file_header_style: str


# ── Built-in themes ───────────────────────────────────────────────────────────

THEMES: Dict[str, Theme] = {
    "default": Theme(
        name="default",
        dir_style="bold blue",
        file_style="white",
        hidden_style="dim italic",
        special_style="bold yellow",
        binary_style="dim",
        link_style="cyan",
        error_style="bold red",
        size_style="dim",
        git_modified="yellow",
        git_added="green",
        git_untracked="dim white",
        git_deleted="red",
        git_ignored="dim",
        guide_style="dim",
        header_style="bold cyan",
        file_header_style="bold blue",
    ),
    "dark": Theme(
        name="dark",
        dir_style="bold bright_blue",
        file_style="bright_white",
        hidden_style="dim italic",
        special_style="bold bright_yellow",
        binary_style="dim",
        link_style="bright_cyan",
        error_style="bold bright_red",
        size_style="dim",
        git_modified="bright_yellow",
        git_added="bright_green",
        git_untracked="dim white",
        git_deleted="bright_red",
        git_ignored="dim",
        guide_style="dim blue",
        header_style="bold bright_cyan",
        file_header_style="bold bright_blue",
    ),
    "light": Theme(
        name="light",
        dir_style="bold blue",
        file_style="black",
        hidden_style="dim",
        special_style="bold magenta",
        binary_style="dim",
        link_style="dark_cyan",
        error_style="bold red",
        size_style="dim",
        git_modified="dark_orange3",
        git_added="green4",
        git_untracked="grey50",
        git_deleted="red3",
        git_ignored="grey50",
        guide_style="grey50",
        header_style="bold dark_cyan",
        file_header_style="bold blue",
    ),
    "minimal": Theme(
        name="minimal",
        dir_style="bold",
        file_style="",
        hidden_style="dim",
        special_style="bold",
        binary_style="dim",
        link_style="italic",
        error_style="bold",
        size_style="dim",
        git_modified="bold",
        git_added="bold",
        git_untracked="dim",
        git_deleted="bold",
        git_ignored="dim",
        guide_style="dim",
        header_style="bold",
        file_header_style="bold",
    ),
    # Nord colour palette  (https://www.nordtheme.com/docs/colors-and-palettes)
    "nord": Theme(
        name="nord",
        dir_style="bold #81a1c1",       # Nord9 — frost blue
        file_style="#d8dee9",           # Nord4 — snow storm
        hidden_style="dim #4c566a",     # Nord3 — polar night
        special_style="bold #ebcb8b",   # Nord13 — aurora yellow
        binary_style="dim #4c566a",
        link_style="#88c0d0",           # Nord8 — frost
        error_style="bold #bf616a",     # Nord11 — aurora red
        size_style="dim #4c566a",
        git_modified="#ebcb8b",         # Nord13
        git_added="#a3be8c",            # Nord14 — aurora green
        git_untracked="#4c566a",        # Nord3
        git_deleted="#bf616a",          # Nord11
        git_ignored="dim #4c566a",
        guide_style="dim #4c566a",
        header_style="bold #88c0d0",
        file_header_style="bold #81a1c1",
    ),
}


def get_theme(name: str) -> Theme:
    """Return the named theme, falling back to 'default' if unknown."""
    return THEMES.get(name, THEMES["default"])


THEME_NAMES = list(THEMES.keys())
