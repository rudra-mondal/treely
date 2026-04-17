"""
treely.config_file
~~~~~~~~~~~~~~~~~~
TOML-based configuration file and profile system.

Resolution order (highest → lowest priority):
  1. CLI flags (handled in main.py)
  2. Named profile from config file (``--profile <name>``)
  3. ``[defaults]`` section of config file
  4. Built-in defaults in ``TreeConfig``

Config file search order:
  1. Path given via ``--config <path>``
  2. ``treely.toml`` or ``.treely.toml`` in the current working directory
  3. ``~/.config/treely/config.toml`` on Linux / macOS
  4. ``%APPDATA%\\treely\\config.toml`` on Windows
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .config import TreeConfig

# ── TOML parser import ────────────────────────────────────────────────────────

if sys.version_info >= (3, 11):
    import tomllib  # built-in on Python 3.11+
    _HAS_TOML = True
else:
    try:
        import tomllib  # type: ignore[no-redef]
        _HAS_TOML = True
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
            _HAS_TOML = True
        except ImportError:
            tomllib = None  # type: ignore[assignment]
            _HAS_TOML = False


# ── Config file discovery ─────────────────────────────────────────────────────

def _default_config_paths() -> list[Path]:
    """Return candidate config file paths in priority order."""
    cwd = Path.cwd()
    candidates = [
        cwd / "treely.toml",
        cwd / ".treely.toml",
    ]
    # Platform-specific user config dir
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            candidates.append(Path(appdata) / "treely" / "config.toml")
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg:
            candidates.append(Path(xdg) / "treely" / "config.toml")
        candidates.append(Path.home() / ".config" / "treely" / "config.toml")
    return candidates


def find_config_file(explicit_path: Optional[str] = None) -> Optional[Path]:
    """
    Return the first existing config file path, or ``None`` if no config file
    is found.
    """
    if explicit_path:
        p = Path(explicit_path)
        return p if p.is_file() else None
    for path in _default_config_paths():
        if path.is_file():
            return path
    return None


# ── Reading ───────────────────────────────────────────────────────────────────

def load_config_file(path: Path) -> Dict[str, Any]:
    """
    Parse a TOML config file and return its contents as a dict.
    Returns an empty dict if TOML support is unavailable or parsing fails.
    """
    if not _HAS_TOML:
        return {}
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except Exception:
        return {}


# ── Applying to TreeConfig ────────────────────────────────────────────────────

# Fields in TreeConfig that the config file is allowed to set.
# Excluded: root_path, profile, config_path (these are always CLI-only).
_SETTABLE_FIELDS = {
    "all", "level", "sort", "dirs_only", "files_only", "full_path",
    "follow_symlinks", "show_size", "summary",
    "pattern", "ignore", "use_gitignore",
    "code", "exclude", "max_size", "token_count",
    "no_git",
    "theme", "no_color", "no_banner", "format",
    "output", "copy",
}


def _apply_section(config: TreeConfig, section: Dict[str, Any]) -> TreeConfig:
    """
    Copy keys from *section* into *config*'s matching fields.
    Keys not in ``_SETTABLE_FIELDS`` are silently ignored.
    """
    mapping: Dict[str, Any] = {}
    for key, value in section.items():
        # Normalise dashes to underscores (e.g. no-color → no_color)
        field = key.replace("-", "_")
        if field in _SETTABLE_FIELDS:
            mapping[field] = value

    for field_name, value in mapping.items():
        if hasattr(config, field_name):
            setattr(config, field_name, value)
    return config


def apply_config_file(
    config: TreeConfig,
    file_data: Dict[str, Any],
    profile: Optional[str] = None,
) -> TreeConfig:
    """
    Apply ``[defaults]`` and optionally a named ``[profiles.<name>]`` section
    from *file_data* to *config*.

    Profile values override defaults; CLI values (applied later) override both.
    """
    if not file_data:
        return config

    # Apply [defaults] section
    defaults = file_data.get("defaults", {})
    if defaults:
        config = _apply_section(config, defaults)

    # Apply named profile (overrides defaults)
    if profile:
        profiles = file_data.get("profiles", {})
        if profile in profiles:
            config = _apply_section(config, profiles[profile])
        else:
            # Non-fatal: unknown profile
            sys.stderr.write(
                f"Warning: Profile '{profile}' not found in config file.\n"
            )

    return config


def list_profiles(file_data: Dict[str, Any]) -> list[str]:
    """Return the list of profile names defined in *file_data*."""
    return list(file_data.get("profiles", {}).keys())
