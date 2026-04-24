"""
treely.utils
~~~~~~~~~~~~
Shared utility helpers that don't belong to any specific module.
"""
from __future__ import annotations

import re

# ── Size formatting ───────────────────────────────────────────────────────────

def get_human_readable_size(size_bytes: int, precision: int = 1) -> str:
    """Convert a byte count to a human-readable string (e.g. 1.4K, 3.2M)."""
    suffixes = ["B", "K", "M", "G", "T"]
    idx = 0
    value = float(size_bytes)
    while value >= 1024 and idx < len(suffixes) - 1:
        idx += 1
        value /= 1024.0
    return f"{value:.{precision}f}{suffixes[idx]}"


# ── Language tag inference ────────────────────────────────────────────────────

_EXT_TO_LANG: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".mts": "typescript",
    ".jsx": "jsx", ".tsx": "tsx",
    ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "scss", ".less": "less",
    ".java": "java",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".kt": "kotlin",
    ".swift": "swift",
    ".dart": "dart",
    ".scala": "scala",
    ".lua": "lua",
    ".pl": "perl",
    ".sh": "bash", ".bash": "bash",
    ".bat": "batch", ".cmd": "batch",
    ".ps1": "powershell",
    ".sql": "sql",
    ".xml": "xml",
    ".json": "json", ".jsonc": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini", ".cfg": "ini", ".conf": "ini",
    ".env": "dotenv",
    ".md": "markdown", ".mdx": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".r": "r",
    ".jl": "julia",
    ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang", ".hrl": "erlang",
    ".clj": "clojure", ".cljs": "clojure",
    ".hs": "haskell",
    ".elm": "elm",
    ".fs": "fsharp", ".fsx": "fsharp",
    ".ml": "ocaml", ".mli": "ocaml",
    ".nim": "nim",
    ".zig": "zig",
    ".tf": "terraform", ".hcl": "hcl",
    ".proto": "protobuf",
    ".graphql": "graphql", ".gql": "graphql",
    ".svelte": "svelte",
    ".vue": "vue",
    ".astro": "astro",
    ".gradle": "gradle",
    ".dockerfile": "dockerfile",
    ".make": "makefile", ".mk": "makefile",
}

_NAME_TO_LANG: dict[str, str] = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile", "makefile": "makefile", "GNUmakefile": "makefile",
    ".gitignore": "gitignore",
    ".dockerignore": "gitignore",
    ".env": "dotenv",
}


def get_language_tag(filename: str, extension: str) -> str:
    """
    Infer a Markdown fenced-code-block language identifier from a filename
    and its extension.  Returns an empty string if unknown.
    """
    # Exact name match first (e.g. 'Dockerfile')
    if filename in _NAME_TO_LANG:
        return _NAME_TO_LANG[filename]
    return _EXT_TO_LANG.get(extension.lower(), "")


# ── ANSI stripping ────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove all ANSI colour escape sequences from *text*."""
    return _ANSI_RE.sub("", text)


# ── Token estimation ─────────────────────────────────────────────────────────

def estimate_tokens(text_or_count: str | int) -> int:
    """
    Estimate the number of LLM tokens in a string or character count.
    Uses the widely-cited rule of thumb: ~4 characters per token.
    """
    count = text_or_count if isinstance(text_or_count, int) else len(text_or_count)
    return max(0, count // 4)


def format_token_count(count: int) -> str:
    """Return a human-readable token count string (e.g. '~12,450 tokens')."""
    return f"~{count:,} tokens"
