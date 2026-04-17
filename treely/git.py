"""
treely.git
~~~~~~~~~~
Git integration: detect whether a path is inside a git repository and parse
``git status --porcelain`` output into a lightweight status map.

All operations are best-effort — any failure returns empty/False so the rest
of treely continues to work in non-git environments.
"""
from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional, Tuple


# Status characters used in the tree (subset of git's XY codes)
GIT_STATUS_MODIFIED = "M"
GIT_STATUS_ADDED = "A"
GIT_STATUS_UNTRACKED = "?"
GIT_STATUS_DELETED = "D"
GIT_STATUS_IGNORED = "!"


def _run(args: List[str], cwd: str, timeout: int = 5) -> Optional[str]:
    """Run a git sub-command and return stdout on success, else None."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout if result.returncode == 0 else None
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def get_git_root(path: str) -> Optional[str]:
    """
    Return the absolute git root directory for *path*, or ``None`` if *path*
    is not inside a git repository.
    """
    out = _run(["git", "-C", path, "rev-parse", "--show-toplevel"], cwd=path)
    return out.strip() if out else None


def is_git_repo(path: str) -> bool:
    """Return ``True`` if *path* is inside a git repository."""
    return get_git_root(path) is not None


def _parse_porcelain(output: str) -> Dict[str, str]:
    """
    Parse ``git status --porcelain`` output into a ``{path: status_char}`` map.

    XY codes are collapsed to a single character:
    - ``?`` untracked
    - ``!`` ignored
    - ``D`` deleted (either index or working tree)
    - ``A`` added / staged new file
    - ``M`` everything else (modified, renamed, copied, …)
    """
    status_map: Dict[str, str] = {}
    for line in output.splitlines():
        if len(line) < 4:
            continue
        xy = line[:2]
        path_part = line[3:].strip()

        # Renames are reported as "old -> new"
        if " -> " in path_part:
            path_part = path_part.split(" -> ")[-1]

        # Strip optional surrounding quotes (git uses them for special chars)
        path_part = path_part.strip('"').replace("\\\\", "/").replace("\\", "/")

        if "?" in xy:
            char = GIT_STATUS_UNTRACKED
        elif "!" in xy:
            char = GIT_STATUS_IGNORED
        elif "D" in xy:
            char = GIT_STATUS_DELETED
        elif xy.strip() in ("A", "AA"):
            char = GIT_STATUS_ADDED
        else:
            char = GIT_STATUS_MODIFIED

        status_map[path_part] = char
    return status_map


def get_git_info(root_path: str) -> Tuple[bool, Dict[str, str]]:
    """
    Return ``(is_inside_repo, status_dict)`` for *root_path*.

    ``status_dict`` maps paths **relative to root_path** to a status character.
    When *root_path* is not the git root (e.g. a subdirectory), paths are
    automatically adjusted so they are always relative to *root_path*.
    """
    git_root = get_git_root(root_path)
    if not git_root:
        return False, {}

    # git status shows paths relative to git root — adjust if needed
    raw_output = _run(
        ["git", "-C", root_path, "status", "--porcelain", "-u", "--ignored=matching"],
        cwd=root_path,
        timeout=10,
    )
    if raw_output is None:
        return True, {}

    raw_map = _parse_porcelain(raw_output)

    # Compute the prefix: path from git_root → our scan root
    try:
        rel = os.path.relpath(os.path.abspath(root_path), os.path.abspath(git_root))
        prefix = rel.replace("\\", "/")
        if prefix == ".":
            prefix = ""
    except ValueError:
        # Different drives on Windows — cannot relativize
        prefix = ""

    adjusted: Dict[str, str] = {}
    for path, char in raw_map.items():
        if prefix:
            if path.startswith(prefix + "/"):
                local_path = path[len(prefix) + 1:]
            else:
                continue  # outside our scan root
        else:
            local_path = path
        adjusted[local_path] = char

    return True, adjusted
