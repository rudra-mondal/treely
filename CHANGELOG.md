# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-04-17

### ⚠️ Breaking Changes
- Minimum Python version raised from 3.7 → **3.8** (required by rich).
- Added `rich>=13.0.0` as a mandatory dependency (replaces manually-written ANSI codes).
- Internal package structure is now modular (`walker`, `renderer`, `filters`, `git`, `theme`, `config`, `output`, `config_file`). The `treely` package now has a stable **public Python API** (`from treely import walk, TreeConfig, Renderer`).

### Added
#### Rendering
- **Rich library** integration: directories are bold blue, hidden files dim italic, special files highlighted, binary files marked `[binary]`.  Full TTY auto-detection (colors disabled when piping).
- **5 built-in themes**: `default`, `dark`, `light`, `minimal`, `nord` — selectable with `--theme <name>`.
- `--no-color` flag: disable all colour output.
- `--no-banner` flag: suppress startup ASCII art and delay.
- `--version` flag: print installed version and exit.

#### Git Status Integration
- Automatic git repository detection.
- Files annotated with `●` (modified), `+` (added), `?` (untracked), `✗` (deleted) symbols from `git status --porcelain`.
- `--no-git` flag to disable git annotations.

#### Filtering
- **Nested `.gitignore` support**: subdirectory `.gitignore` files are now respected within their directory scope.
- `--dirs-only`: show only directories in the tree.
- `--files-only`: show only files in the tree.
- `--sort name|size|mtime|ext`: control entry sort order (previously always alphabetical, dirs-first).
- `--max-size <SIZE>`: skip large files from `--code` output (e.g. `--max-size 1M`).
- `--full-path`: print absolute paths instead of just filenames.
- `--follow-symlinks`: opt in to recursing into symlinked directories.
- Symbolic links now shown with `→ target` annotation.
- `--pattern` now always descends into directories (previously skipped dirs whose names didn't match).

#### Output Formats
- `--format json`: structured, machine-readable JSON output of the full directory tree.
- `--format markdown`: Markdown-formatted tree in a fenced code block, with per-file code blocks using language identifiers.
- `--token-count`: estimate LLM token count of code output (rule of thumb: 4 chars ≈ 1 token).
- Code blocks now include language tags inferred from file extension (e.g. ` ```python `).

#### Configuration & Profiles
- `treely.toml` / `.treely.toml` project-local config file.
- `~/.config/treely/config.toml` (Linux/macOS) / `%APPDATA%\treely\config.toml` (Windows).
- `[defaults]` section: set any flag as a persistent default.
- `[profiles.<name>]` sections: named run configurations.
- `--profile <name>`: activate a named profile.
- `--config <path>`: use a custom config file path.
- Requires `tomli` on Python < 3.11 (optional; `pip install treely[config]`).

#### Testing & CI
- Full test suite: `tests/` with `pytest` covering filters, walker, renderer, config file, and CLI.
- GitHub Actions CI matrix: Python 3.8–3.12 × Ubuntu, Windows, macOS.
- GitHub Actions publish workflow: automated PyPI publishing on git tag.
- `ruff` configured for linting and import sorting.

#### Dev Experience
- `CHANGELOG.md` following Keep-a-Changelog format.
- `update.txt` reflects updated release workflow.
- `pyproject.toml` optional dependency groups: `[dev]`, `[config]`, `[completion]`.

### Changed
- `treely/main.py` reduced from 345 lines to ~160 lines (thin CLI entry point only).
- All logic extracted to purpose-built modules — each independently testable.
- `--ignore` and `--exclude` now also match against the full relative path (not just the basename), making `--ignore "src/*.log"` work correctly.

### Fixed
- `--pattern` no longer prevents descending into subdirectories.
- Binary files are now silently skipped in `--code` output instead of printing garbage.
- Files larger than `--max-size` are skipped from code output.

---

## [1.1.1] — 2025-xx-xx

### Fixed
- Added graceful error handling for invalid root paths (no more raw stack traces).

### Performance
- Replaced `os.path.relpath` calls inside the hot recursive loop with string concatenation, significantly improving performance on large projects.

---

## [1.1.0] — 2025-xx-xx

### Added
- `--use-gitignore` flag using `pathspec`.
- `--code` and `--exclude` flags.
- Clipboard copy (`-c`) and file output (`-o`).
- `--show-size` flag.
- `-s` / `--summary` flag.

---

## [1.0.1] — 2025-xx-xx

### Fixed
- Updated dependencies in `pyproject.toml` to allow compatible versions.

---

## [1.0.0] — 2025-xx-xx

### Added
- Initial release with basic directory tree generation.
