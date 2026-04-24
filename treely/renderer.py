"""
treely.renderer
~~~~~~~~~~~~~~~
Converts a ``WalkResult`` into formatted output (terminal / plain text / JSON /
Markdown).  Uses the ``rich`` library for beautiful terminal rendering.

The ``Renderer`` class has two main entry points:

* ``to_console(result)``   — prints richly coloured output directly to the
                             terminal (uses rich internals).
* ``to_string(result)``    — returns a plain-text string (no ANSI) suitable
                             for clipboard copy or file output.

Additionally ``to_json(result)`` and ``to_markdown(result)`` return the
corresponding formatted strings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console

try:
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.tree import Tree as RichTree
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

from .config import TreeConfig
from .theme import Theme, get_theme
from .tree_node import TreeNode, WalkResult
from .utils import (
    estimate_tokens,
    format_token_count,
    get_human_readable_size,
    get_language_tag,
)

# ── Label builder ─────────────────────────────────────────────────────────────

_GIT_SYMBOLS: dict[str, str] = {
    "M": "●",
    "A": "+",
    "?": "?",
    "D": "✗",
    "!": "~",
}


def _make_rich_label(node: TreeNode, config: TreeConfig, theme: Theme) -> Text:
    """Build a rich ``Text`` object for a single tree node."""
    label = Text()

    # ── Git status prefix ─────────────────────────────────────────────────────
    if node.git_status and not config.no_color:
        sym = _GIT_SYMBOLS.get(node.git_status, " ")
        style_map = {
            "M": theme.git_modified,
            "A": theme.git_added,
            "?": theme.git_untracked,
            "D": theme.git_deleted,
            "!": theme.git_ignored,
        }
        git_style = style_map.get(node.git_status, "")
        label.append(sym + " ", style=git_style)

    # ── Entry name ────────────────────────────────────────────────────────────
    display = node.display_name

    if node.error:
        label.append(display, style=theme.error_style)
    elif node.is_dir:
        if node.is_hidden:
            label.append(display, style=theme.hidden_style)
        else:
            label.append(display, style=theme.dir_style)
    elif node.is_symlink:
        label.append(display, style=theme.link_style)
        if node.symlink_target:
            label.append(" → ", style="dim")
            label.append(node.symlink_target, style="dim italic")
    elif node.is_special:
        label.append(display, style=theme.special_style)
    elif node.is_hidden:
        label.append(display, style=theme.hidden_style)
    elif node.is_binary:
        label.append(display, style=theme.binary_style)
        label.append("  [binary]", style="dim")
    else:
        label.append(display, style=theme.file_style)

    # ── Size badge ────────────────────────────────────────────────────────────
    if config.show_size and node.size is not None:
        label.append(
            f"  [{get_human_readable_size(node.size)}]",
            style=theme.size_style,
        )

    return label


def _make_plain_label(node: TreeNode, config: TreeConfig) -> str:
    """Build a plain-text label (no rich markup) for a single tree node."""
    parts: list[str] = []

    if node.git_status:
        sym = _GIT_SYMBOLS.get(node.git_status, " ")
        parts.append(sym + " ")

    parts.append(node.display_name)

    if node.is_symlink and node.symlink_target:
        parts.append(f" → {node.symlink_target}")

    if node.is_binary:
        parts.append("  [binary]")

    if config.show_size and node.size is not None:
        parts.append(f"  [{get_human_readable_size(node.size)}]")

    return "".join(parts)


# ── Plain-text tree renderer (fallback when rich is not available) ─────────────

_CONNECTOR_LAST = "└── "
_CONNECTOR_MID = "├── "
_PREFIX_LAST = "    "
_PREFIX_MID = "│   "


def _render_plain_lines(node: TreeNode, config: TreeConfig, prefix: str = "") -> list[str]:
    """Recursively render *node* to a list of plain-text lines."""
    lines: list[str] = []
    children = node.children
    for idx, child in enumerate(children):
        is_last = idx == len(children) - 1
        connector = _CONNECTOR_LAST if is_last else _CONNECTOR_MID
        ext_prefix = _PREFIX_LAST if is_last else _PREFIX_MID
        lines.append(prefix + connector + _make_plain_label(child, config))
        if child.is_dir and child.children:
            lines.extend(
                _render_plain_lines(child, config, prefix + ext_prefix)
            )
    return lines


# ── Rich-powered tree renderer ────────────────────────────────────────────────

def _populate_rich_tree(
    rich_node: RichTree,
    tree_node: TreeNode,
    config: TreeConfig,
    theme: Theme,
) -> None:
    """Recursively add children of *tree_node* to *rich_node*."""
    for child in tree_node.children:
        label = _make_rich_label(child, config, theme)
        if child.is_dir:
            branch = rich_node.add(label, guide_style=theme.guide_style)
            if child.children:
                _populate_rich_tree(branch, child, config, theme)
        else:
            rich_node.add(label)


def _build_rich_tree(
    root: TreeNode, config: TreeConfig, theme: Theme
) -> RichTree:
    """Build and return a rich ``Tree`` object for *root*."""
    label = _make_rich_label(root, config, theme)
    rich_tree = RichTree(label, guide_style=theme.guide_style)
    _populate_rich_tree(rich_tree, root, config, theme)
    return rich_tree


# ── Code section rendering ────────────────────────────────────────────────────

def _read_file_safe(path: Path) -> str:
    """Read *path* with robust encoding detection (UTF-16 BOM -> UTF-8)."""
    try:
        raw = path.read_bytes()

        # Check for UTF-16 / UTF-32 BOMs
        if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
            content = raw.decode("utf-32", errors="replace")
        elif raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            content = raw.decode("utf-16", errors="replace")
        else:
            content = raw.decode("utf-8", errors="replace")

        # Strip null bytes and replace the unicode replacement character
        # with standard ASCII '?' to prevent Windows cp1252 crash loops.
        return content.replace("\x00", "").replace("\ufffd", "?")
    except MemoryError:
        return "[Error: File too large to read into memory. Use --max-size to skip huge files]"
    except OSError as exc:
        return f"[Error reading file: {exc}]"


def _render_code_to_console(
    code_files: list[Path],
    root_path: Path,
    config: TreeConfig,
    theme: Theme,
    console: Console,
) -> int:
    """Print code sections to *console*. Returns total character count for tokens."""
    if not code_files:
        return 0

    total_chars = 0
    console.print()
    console.rule("FILE CONTENTS", style=theme.header_style)

    for file_path in code_files:
        try:
            rel = file_path.relative_to(root_path)
        except ValueError:
            rel = file_path
        rel_str = str(rel).replace("\\", "/")

        console.print()
        console.rule(f"[b]{rel_str}[/b]", style=theme.file_header_style, align="left")

        content = _read_file_safe(file_path)
        total_chars += len(content)
        ext = file_path.suffix.lower()
        lang = get_language_tag(file_path.name, ext)

        if _RICH_AVAILABLE and lang and not config.no_color:
            syntax = Syntax(
                content,
                lang,
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
            )
            console.print(syntax)
        else:
            console.print(content)

    return total_chars


def _render_code_to_string(
    code_files: list[Path],
    root_path: Path,
    config: TreeConfig,
    for_markdown: bool = False,
) -> tuple[str, int]:
    """Render code sections to a plain string. Returns (text, char_count)."""
    if not code_files:
        return "", 0

    lines: list[str] = []
    total_chars = 0

    lines.append("\n\n--- FILE CONTENTS ---")

    for file_path in code_files:
        try:
            rel = file_path.relative_to(root_path)
        except ValueError:
            rel = file_path
        rel_str = str(rel).replace("\\", "/")

        content = _read_file_safe(file_path)
        total_chars += len(content)
        ext = file_path.suffix.lower()

        if for_markdown:
            lang = get_language_tag(file_path.name, ext)
            lines.append(f"\n\n### `{rel_str}`\n")
            lines.append(f"```{lang}\n{content}\n```")
        else:
            lines.append(f"\n\n--- {rel_str} ---\n{content}")

    return "\n".join(lines), total_chars


# ── JSON serialisation ────────────────────────────────────────────────────────

def _node_to_dict(node: TreeNode, config: TreeConfig) -> dict[str, Any]:
    """Recursively convert a ``TreeNode`` to a JSON-serialisable dict."""
    d: dict[str, Any] = {
        "name": node.name,
        "type": "directory" if node.is_dir else "file",
        "path": str(node.path.resolve()).replace("\\", "/"),
    }
    if not node.is_dir:
        d["extension"] = node.extension
        d["size_bytes"] = node.size
        d["size_human"] = get_human_readable_size(node.size) if node.size is not None else None
        d["is_binary"] = node.is_binary
        d["is_symlink"] = node.is_symlink
        if node.is_symlink:
            d["symlink_target"] = node.symlink_target
    if node.git_status:
        d["git_status"] = node.git_status
    if node.error:
        d["error"] = node.error
    if node.is_dir:
        d["children"] = [_node_to_dict(c, config) for c in node.children]
        if config.code:
            # Inline file contents for dirs at leaf level? No — keep clean.
            pass
    elif config.code and not node.is_binary:
        # Attach content if code mode is on
        from .filters import is_code_file
        if is_code_file(node.name, node.extension):
            d["content"] = _read_file_safe(node.path)
    return d


# ── Main Renderer class ───────────────────────────────────────────────────────

class Renderer:
    """
    High-level rendering façade.  Instantiate with a ``TreeConfig``, then
    call ``to_console(result)`` for terminal output or ``to_string(result)``
    for file/clipboard output.
    """

    def __init__(self, config: TreeConfig) -> None:
        self.config = config
        self.theme = get_theme(config.theme)
        self._root_path: Path | None = None

    # ------------------------------------------------------------------ public

    def to_console(self, result: WalkResult) -> None:
        """Render directly to the terminal with rich colours."""
        self._root_path = result.root.path
        cfg = self.config

        if cfg.format == "json":
            self._console_json(result)
            return
        if cfg.format == "markdown":
            self._console_markdown(result)
            return

        # ── text format ───────────────────────────────────────────────────────
        console = Console(
            no_color=cfg.no_color,
            highlight=False,
            safe_box=True,
        )

        if _RICH_AVAILABLE:
            rich_tree = _build_rich_tree(result.root, cfg, self.theme)
            console.print(rich_tree)
        else:
            # Graceful fallback when rich is somehow unavailable
            print(result.root.display_name)
            for line in _render_plain_lines(result.root, cfg):
                print(line)

        if cfg.summary:
            s = result.stats
            console.print(
                f"\n{s.dirs} directories, {s.files} files",
                style="dim",
            )

        # Code section
        if result.code_files:
            char_count = _render_code_to_console(
                result.code_files,
                result.root.path,
                cfg,
                self.theme,
                console,
            )
            if cfg.token_count:
                tokens = estimate_tokens(char_count)
                console.print(
                    f"\n[dim]Estimated tokens: {format_token_count(tokens)}[/dim]"
                )

    def to_string(self, result: WalkResult) -> str:
        """Render to a plain string (no ANSI codes) for file / clipboard."""
        self._root_path = result.root.path
        cfg = self.config

        if cfg.format == "json":
            return self.to_json(result)
        if cfg.format == "markdown":
            return self.to_markdown(result)

        # ── plain text ────────────────────────────────────────────────────────
        lines: list[str] = [result.root.display_name]
        lines.extend(_render_plain_lines(result.root, cfg))

        if cfg.summary:
            s = result.stats
            lines.append(f"\n{s.dirs} directories, {s.files} files")

        tree_text = "\n".join(lines)

        code_text, char_count = _render_code_to_string(
            result.code_files, result.root.path, cfg, for_markdown=False
        )

        full = tree_text + (("\n" + code_text) if code_text else "")

        if cfg.token_count and code_text:
            tokens = estimate_tokens(full)
            full += f"\n\nEstimated tokens: {format_token_count(tokens)}"

        return full

    def to_json(self, result: WalkResult) -> str:
        """Return a JSON string representing the full directory tree."""
        data = _node_to_dict(result.root, self.config)
        if self.config.summary:
            s = result.stats
            data["_summary"] = {
                "directories": s.dirs,
                "files": s.files,
                "total_bytes": s.total_bytes,
            }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def to_markdown(self, result: WalkResult) -> str:
        """Return a Markdown formatted string."""
        lines: list[str] = [
            f"# `{result.root.display_name}`\n",
            "```",
            result.root.display_name,
        ]
        lines.extend(_render_plain_lines(result.root, self.config))
        lines.append("```")

        if self.config.summary:
            s = result.stats
            lines.append(f"\n_{s.dirs} directories, {s.files} files_")

        code_text, char_count = _render_code_to_string(
            result.code_files,
            result.root.path,
            self.config,
            for_markdown=True,
        )
        if code_text:
            lines.append("\n## File Contents")
            lines.append(code_text)

        if self.config.token_count and code_text:
            full = "\n".join(lines)
            tokens = estimate_tokens(full)
            lines.append(f"\n_Estimated tokens: {format_token_count(tokens)}_")

        return "\n".join(lines)

    # ----------------------------------------------------------------- private

    def _console_json(self, result: WalkResult) -> None:
        data = _node_to_dict(result.root, self.config)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if _RICH_AVAILABLE and not self.config.no_color:
            console = Console(highlight=False, safe_box=True)
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
        else:
            print(json_str)

    def _console_markdown(self, result: WalkResult) -> None:
        md_str = self.to_markdown(result)
        if _RICH_AVAILABLE and not self.config.no_color:
            from rich.markdown import Markdown
            console = Console(safe_box=True)
            console.print(Markdown(md_str))
        else:
            print(md_str)
