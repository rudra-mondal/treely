"""
treely.main
~~~~~~~~~~~
Thin CLI entry point.  Parses arguments, loads the config file, assembles
a ``TreeConfig``, drives walking + rendering, and routes output.

All heavy logic lives in the other modules; this file should stay ~100 lines.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .config import TreeConfig
from .config_file import apply_config_file, find_config_file, load_config_file
from .filters import parse_size
from .git import get_git_info
from .output import (
    check_pathspec,
    check_pyperclip,
    copy_to_clipboard,
    print_banner,
    write_to_file,
)
from .renderer import Renderer
from .theme import THEME_NAMES
from .walker import walk

DEFAULT_OUTPUT_FILENAME = "treely_output.txt"


# ── Argument parser ────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="treely",
        description="A beautiful and professional directory tree generator.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  treely                                   # tree for current directory
  treely --use-gitignore                   # auto-exclude .gitignore'd files
  treely --code --copy                     # dump code to clipboard for LLM
  treely --code --exclude "lib/*|*.log"    # code output with exclusions
  treely --format json                     # machine-readable JSON output
  treely --format markdown -o STRUCTURE.md # save markdown
  treely --profile llm                     # run a saved profile from config
  treely --theme nord                      # use the Nord colour theme
""",
    )

    # ── Positional ────────────────────────────────────────────────────────────
    parser.add_argument(
        "root_path",
        nargs="?",
        default=os.getcwd(),
        help="Starting directory (defaults to current directory).",
    )

    # ── Version ───────────────────────────────────────────────────────────────
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # ── Tree display ──────────────────────────────────────────────────────────
    parser.add_argument("-a", "--all", action="store_true",
                        help="Show hidden files and directories (e.g. '.git').")
    parser.add_argument("-L", "--level", type=int, default=-1, metavar="LEVEL",
                        help="Maximum depth to recurse (e.g. -L 2).")
    parser.add_argument("--sort", choices=["name", "size", "mtime", "ext"],
                        default="name", metavar="MODE",
                        help="Sort order: name|size|mtime|ext (default: name).")
    parser.add_argument("--dirs-only", action="store_true",
                        help="Show only directories in the tree.")
    parser.add_argument("--files-only", action="store_true",
                        help="Show only files in the tree.")
    parser.add_argument("--full-path", action="store_true",
                        help="Print the full absolute path of each entry.")
    parser.add_argument("--follow-symlinks", action="store_true",
                        help="Follow symbolic links when recursing.")
    parser.add_argument("--show-size", action="store_true",
                        help="Display the size of each file.")
    parser.add_argument("-s", "--summary", action="store_true",
                        help="Print a count of directories and files.")

    # ── Filtering ─────────────────────────────────────────────────────────────
    parser.add_argument("--pattern", type=str, metavar="GLOB",
                        help="Show only files matching a glob pattern (e.g. \"*.py\").")
    parser.add_argument("--ignore", type=str, metavar="PATTERNS",
                        help="Exclude entries matching pattern(s). Separate with '|'.")
    parser.add_argument("--use-gitignore", action="store_true",
                        help="Auto-exclude entries listed in .gitignore (including nested).")

    # ── Code output ───────────────────────────────────────────────────────────
    parser.add_argument("--code", action="store_true",
                        help="Print the content of detected code files after the tree.")
    parser.add_argument("--exclude", type=str, metavar="PATTERNS",
                        help="When using --code, exclude paths from code output.\n"
                             "Separate patterns with '|' (e.g. \"lib/*|*.log\").")
    parser.add_argument("--max-size", type=str, metavar="SIZE",
                        help="Skip files larger than SIZE in code output (e.g. 1M, 500K).")
    parser.add_argument("--token-count", action="store_true",
                        help="Estimate LLM token count of the full code output.")

    # ── Git ───────────────────────────────────────────────────────────────────
    parser.add_argument("--no-git", action="store_true",
                        help="Disable git status annotations even inside a git repo.")

    # ── Rendering ─────────────────────────────────────────────────────────────
    parser.add_argument("--theme", choices=THEME_NAMES, default="default",
                        metavar="THEME",
                        help=f"Colour theme: {', '.join(THEME_NAMES)} (default: default).")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable all colour output (auto-detected when piping).")
    parser.add_argument("--no-banner", action="store_true",
                        help="Suppress the startup banner and delay.")
    parser.add_argument("--format", choices=["text", "json", "markdown"],
                        default="text", metavar="FORMAT",
                        help="Output format: text|json|markdown (default: text).")

    # ── Output ────────────────────────────────────────────────────────────────
    parser.add_argument("-o", "--output", nargs="?", const=DEFAULT_OUTPUT_FILENAME,
                        default=None, metavar="FILENAME",
                        help=f"Save output to a file (default name: {DEFAULT_OUTPUT_FILENAME}).")
    parser.add_argument("-c", "--copy", action="store_true",
                        help="Copy output to clipboard.")

    # ── Config / profile ─────────────────────────────────────────────────────
    parser.add_argument("--config", type=str, metavar="PATH",
                        help="Path to a TOML config file.")
    parser.add_argument("--profile", type=str, metavar="NAME",
                        help="Run a named profile from the config file.")

    return parser


# ── Config assembly (precedence: CLI > profile > defaults > built-ins) ─────────

def _build_config(args: argparse.Namespace) -> TreeConfig:
    """Convert parsed CLI args + config file into a final TreeConfig."""
    # Start from built-in defaults
    config = TreeConfig()

    # Load config file (if any)
    config_path = find_config_file(args.config)
    file_data = load_config_file(config_path) if config_path else {}

    # Apply file defaults + profile FIRST (CLI args override these below)
    config = apply_config_file(config, file_data, profile=args.profile)

    # Map every CLI arg that was explicitly provided onto the config object.
    # We do this by checking if the value differs from the parser's default.
    _parser_defaults = vars(_build_parser().parse_args([]))
    cli_ns = vars(args)
    for key, value in cli_ns.items():
        if value != _parser_defaults.get(key):
            field = key.replace("-", "_")
            if hasattr(config, field) and field not in ("root_path", "profile", "config_path"):
                setattr(config, field, value)

    # root_path is always taken from CLI (positional arg)
    config.root_path = args.root_path

    # Auto-detect no-color when output is not a TTY
    if not sys.stdout.isatty():
        config.no_color = True
        config.no_banner = True

    return config


# ── Validation ────────────────────────────────────────────────────────────────

def _validate(config: TreeConfig, parser: argparse.ArgumentParser) -> None:
    """Run pre-flight validation checks. Calls parser.error() on failure."""
    if config.exclude and not config.code:
        parser.error("--exclude can only be used together with --code.")

    if config.token_count and not config.code:
        parser.error("--token-count can only be used together with --code.")

    if config.max_size:
        try:
            parse_size(config.max_size)
        except ValueError as exc:
            parser.error(f"--max-size: {exc}")

    if config.dirs_only and config.files_only:
        parser.error("--dirs-only and --files-only cannot be used together.")

    if not os.path.exists(config.root_path):
        sys.stderr.write(
            f"\033[31mError: The path '{config.root_path}' does not exist.\033[0m\n"
        )
        sys.exit(1)

    if not os.path.isdir(config.root_path):
        sys.stderr.write(
            f"\033[31mError: '{config.root_path}' is not a directory.\033[0m\n"
        )
        sys.exit(1)

    if config.copy:
        check_pyperclip()

    if config.use_gitignore:
        check_pathspec()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    config = _build_config(args)
    _validate(config, parser)

    # ── Banner ────────────────────────────────────────────────────────────────
    print_banner(no_banner=config.no_banner, no_color=config.no_color)

    # ── Git status ────────────────────────────────────────────────────────────
    git_status: dict = {}
    if not config.no_git:
        import contextlib
        with contextlib.suppress(Exception):
            _in_repo, git_status = get_git_info(config.root_path)

    # ── Walk ──────────────────────────────────────────────────────────────────
    root = Path(config.root_path)
    result = walk(root, config, git_status)

    # ── Render & Output ───────────────────────────────────────────────────────
    renderer = Renderer(config)

    if config.copy or config.output:
        content = renderer.to_string(result)
        if config.copy:
            copy_to_clipboard(content)
        if config.output:
            write_to_file(content, config.output)
    else:
        renderer.to_console(result)


if __name__ == "__main__":
    main()
