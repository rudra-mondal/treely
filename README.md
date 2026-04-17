<div align="center">

<img src="https://github.com/user-attachments/assets/bdba702c-5786-4a12-9c93-10c48b2b1577" alt="Treely Demo" width="700"/>

# 🌳 Treely

**A modern, beautiful, and industrial-grade command-line directory tree generator.**

*Go beyond `tree`. Visualize, filter, share, and understand any codebase in seconds.*

[![PyPI version](https://img.shields.io/pypi/v/treely.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/treely/)
[![Python Versions](https://img.shields.io/pypi/pyversions/treely.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/treely/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/github/actions/workflow/status/rudra-mondal/treely/ci.yml?style=flat-square&label=CI&logo=github)](https://github.com/rudra-mondal/treely/actions)
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen?style=flat-square)](https://github.com/rudra-mondal/treely)
[![PyPI Downloads](https://img.shields.io/pypi/dm/treely.svg?style=flat-square)](https://pypi.org/project/treely/)
[![GitHub Stars](https://img.shields.io/github/stars/rudra-mondal/treely?style=flat-square&logo=github)](https://github.com/rudra-mondal/treely)

</div>

---

## Table of Contents

- [What is Treely?](#-what-is-treely)
- [Feature Overview](#-feature-overview)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Complete CLI Reference](#-complete-cli-reference)
  - [Positional Arguments](#positional-arguments)
  - [Tree Display](#tree-display-flags)
  - [Filtering](#filtering-flags)
  - [Code Output](#code-output-flags)
  - [Git Integration](#git-integration-flags)
  - [Rendering & Themes](#rendering--theme-flags)
  - [Output Destination](#output-destination-flags)
  - [Configuration & Profiles](#configuration--profile-flags)
- [Workflow Examples](#-workflow-examples)
  - [1. Overview of Any Project](#1-overview-of-any-project)
  - [2. Preparing LLM / AI Context](#2-preparing-llm--ai-context)
  - [3. Advanced Code Dump with Exclusions](#3-advanced-code-dump-with-exclusions)
  - [4. Generate Project Documentation](#4-generate-project-documentation)
  - [5. Machine-Readable JSON Output](#5-machine-readable-json-output)
  - [6. Markdown for READMEs & GitHub](#6-markdown-for-readmes--github)
  - [7. Git Status Awareness](#7-git-status-awareness)
  - [8. Deep-Dive with Sorting & Filtering](#8-deep-dive-with-sorting--filtering)
- [Configuration File (`treely.toml`)](#-configuration-file-treelytoml)
- [Profile System](#-profile-system)
- [Themes](#-themes)
- [Git Integration](#-git-integration)
- [Output Formats](#-output-formats)
- [Programmatic Python API](#-programmatic-python-api)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🤔 What is Treely?

Treely is a **Python-powered replacement for the classic `tree` command** that understands your codebase. It was built to solve three real-world developer problems:

1. **Visualize** — See any project's directory structure with beautiful, colour-coded output powered by [Rich](https://github.com/Textualize/rich).
2. **Understand** — See git status at a glance, detect binary files, handle `.gitignore` rules (including nested ones), and filter intelligently.
3. **Share** — Dump your entire project structure *and* all its source code to clipboard in one command, ready to paste into ChatGPT, Claude, Gemini, or any other LLM.

```
my-web-app/
├── src/
│   ├── main.py          ● [3.2K]
│   ├── utils.py         + [1.1K]
│   └── config.py          [892.0B]
├── tests/
│   └── test_main.py       [2.4K]
├── .gitignore
├── pyproject.toml       ● [2.9K]
└── README.md              [12.1K]

2 directories, 6 files
```
*`●` = modified, `+` = staged — live git status in your tree.*

---

## ✨ Feature Overview

| Feature | Details |
|---|---|
| 🎨 **Rich Rendering** | Beautiful, colour-coded output via the Rich library. No raw ANSI codes. |
| 🖼️ **5 Built-in Themes** | `default`, `dark`, `light`, `minimal`, `nord` |
| 🔴 **Git Status** | Annotates files with `●` (modified), `+` (added), `?` (untracked), `✗` (deleted) |
| 📄 **Nested `.gitignore`** | Respects `.gitignore` files at every directory level, per the git spec |
| 💻 **Code Dump** | `--code` prints all source files; `--exclude` surgically removes files from it |
| 📋 **Clipboard** | `-c` copies everything instantly — tree + code — perfect for LLM prompts |
| 💾 **File Output** | `-o` saves clean, colourless output to any file |
| 📊 **Output Formats** | `--format text` (default), `--format json`, `--format markdown` |
| 🔢 **Token Counter** | `--token-count` estimates LLM token cost of code output |
| ⚙️ **Config File** | `treely.toml` for persistent defaults and named profiles |
| 👤 **Profiles** | `--profile llm`, `--profile docs` — one flag to set them all |
| 🔀 **Sorting** | `--sort name\|size\|mtime\|ext` |
| 📏 **Size Filter** | `--max-size 1M` to skip large files from code output |
| 🔗 **Symlinks** | Detects and displays symlinks with `→ target` annotation |
| 🚫 **Binary Detection** | Automatically skips binary files from code output |
| 🌍 **Cross-platform** | Windows, macOS, Linux — consistent behavior everywhere |
| 🐍 **Programmatic API** | Use `from treely import walk, TreeConfig, Renderer` in your scripts |

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install treely
```

This installs `treely` along with its three required dependencies: `rich`, `pyperclip`, and `pathspec`.

### With TOML Config File Support (Python < 3.11)

On Python 3.11+, TOML is built into the standard library. For older versions, install the optional extra:

```bash
pip install "treely[config]"
```

### For Development

```bash
git clone https://github.com/rudra-mondal/treely.git
cd treely
pip install -e ".[dev]"
```

### Verify Installation

```bash
treely --version
# treely 2.0.0
```

> **Note:** Ensure your Python `Scripts` directory is on your system `PATH`. On Windows this is typically `C:\Users\<You>\AppData\Local\Programs\Python\Python3xx\Scripts`.

---

## 🚀 Quick Start

```bash
# Tree for the current directory
treely

# Tree for a specific directory
treely /path/to/project

# Use .gitignore to auto-clean the output (most common usage)
treely --use-gitignore

# Copy full project context to clipboard for an LLM prompt
treely --use-gitignore --code -c

# Get a full JSON snapshot of a project
treely --format json

# See everything about a project at once
treely --use-gitignore --show-size --summary
```

---

## 📖 Complete CLI Reference

```
usage: treely [-h] [--version] [-a] [-L LEVEL] [--sort MODE]
              [--dirs-only] [--files-only] [--full-path]
              [--follow-symlinks] [--show-size] [-s]
              [--pattern GLOB] [--ignore PATTERNS] [--use-gitignore]
              [--code] [--exclude PATTERNS] [--max-size SIZE]
              [--token-count] [--no-git]
              [--theme THEME] [--no-color] [--no-banner]
              [--format FORMAT] [-o [FILENAME]] [-c]
              [--config PATH] [--profile NAME]
              [root_path]
```

---

### Positional Arguments

| Argument | Description |
|---|---|
| `root_path` | The starting directory. Defaults to the current working directory (`.`). |

**Examples:**
```bash
treely                          # current directory
treely my-project/              # relative path
treely /home/user/repos/myapp   # absolute path
treely "My Project With Spaces" # paths with spaces (use quotes)
```

---

### Tree Display Flags

| Flag | Short | Default | Description |
|---|---|---|---|
| `--all` | `-a` | off | Show hidden files and directories (anything starting with `.`). |
| `--level LEVEL` | `-L` | unlimited | Maximum depth to recurse into. `-L 1` shows only the top level. |
| `--sort MODE` | | `name` | Sort order: `name`, `size`, `mtime`, `ext`. |
| `--dirs-only` | | off | Show only directories, no files. |
| `--files-only` | | off | Show only files, no subdirectories. |
| `--full-path` | | off | Print the full absolute path of each entry instead of just the name. |
| `--follow-symlinks` | | off | Follow symbolic links when recursing into directories. |
| `--show-size` | | off | Display the size of each file as a badge (e.g. `[3.2K]`). |
| `--summary` | `-s` | off | Print a count of total directories and files after the tree. |
| `--version` | | | Print the installed version and exit. |

**Examples:**

```bash
# Show only 2 levels deep
treely my-project -L 2

# Show hidden files (like .env, .gitignore) in the tree
treely my-project -a

# Show only directories (great for a structural overview)
treely my-project --dirs-only

# Show only files in the current directory (no dirs)
treely my-project --files-only

# Sort by file size (largest first)
treely my-project --sort size --show-size

# Sort by most recently modified
treely my-project --sort mtime

# Sort by file extension (groups all .py, .js, etc. together)
treely my-project --sort ext

# Show file sizes and a summary count
treely my-project --show-size -s

# Show full absolute paths for every entry
treely my-project --full-path

# Follow symlinks into directories
treely my-project --follow-symlinks
```

---

### Filtering Flags

| Flag | Default | Description |
|---|---|---|
| `--pattern GLOB` | none | Show **only files** matching a glob pattern. Directories are always shown. |
| `--ignore PATTERNS` | none | Exclude entries whose name matches these patterns. Separate with `\|`. |
| `--use-gitignore` | off | Parse and honour `.gitignore` files throughout the tree, including nested ones. |

**Examples:**

```bash
# Show only Python files
treely my-project --pattern "*.py"

# Show only JavaScript and TypeScript files
treely my-project --pattern "*.ts"

# Ignore the node_modules and dist directories
treely my-project --ignore "node_modules|dist"

# Ignore log files and test directories
treely my-project --ignore "*.log|tests"

# Use the project's .gitignore to automatically exclude all ignored files
treely my-project --use-gitignore

# Combine: gitignore + also ignore docs
treely my-project --use-gitignore --ignore docs

# Show only Python files that are not ignored by .gitignore
treely my-project --use-gitignore --pattern "*.py"
```

> **Nested `.gitignore` support:** Unlike the classic `tree` command and many alternatives, Treely reads *every* `.gitignore` file it encounters while recursing — not just the root one. Subdirectory-level `.gitignore` rules are applied correctly within their own scope, exactly as git does.

---

### Code Output Flags

| Flag | Default | Description |
|---|---|---|
| `--code` | off | After printing the tree, print the contents of all detected code files. |
| `--exclude PATTERNS` | none | When using `--code`, exclude files/paths from the content section. Separate with `\|`. |
| `--max-size SIZE` | none | Skip files larger than `SIZE` from code output. Accepts `B`, `K`, `M`, `G` suffixes. |
| `--token-count` | off | After the code section, print an estimated LLM token count (≈4 chars/token). |

**Supported code file types** (auto-detected by extension): Python, JavaScript, TypeScript, JSX/TSX, HTML, CSS/SCSS/Less, Java, C/C++, C#, Go, Rust, PHP, Ruby, Kotlin, Swift, Dart, Scala, Lua, Perl, Shell, PowerShell, SQL, XML, JSON, YAML, TOML, INI, Markdown, Svelte, Vue, Astro, Terraform, Protobuf, GraphQL, and more.

**Binary files** (PDFs, images, executables, etc.) are always automatically skipped.

**Examples:**

```bash
# Print the tree and all source code
treely my-project --code

# Print code but exclude the entire lib/ directory
treely my-project --code --exclude "lib/*"

# Exclude multiple patterns (library files AND specific files)
treely my-project --code --exclude "lib/*|*.min.js|vendor/*"

# Skip files larger than 500KB (useful for large auto-generated files)
treely my-project --code --max-size 500K

# Combine: gitignore + code + 1MB size limit
treely my-project --use-gitignore --code --max-size 1M

# Estimate how many LLM tokens the code output will consume
treely my-project --use-gitignore --code --token-count

# The ultimate LLM context command:
# gitignore + code + max size + token count + copy to clipboard
treely my-project --use-gitignore --code --max-size 500K --token-count -c
```

---

### Git Integration Flags

| Flag | Default | Description |
|---|---|---|
| `--no-git` | off | Disable git status annotations even when inside a git repository. |

Git status is **automatically enabled** when Treely detects that the scanned path is inside a git repository. No flag is needed to enable it.

**Git Status Symbols:**

| Symbol | Colour | Meaning |
|---|---|---|
| `●` | Yellow | Modified (tracked file with uncommitted changes) |
| `+` | Green | Added / staged (new file staged for commit) |
| `?` | Dim | Untracked (new file not yet staged) |
| `✗` | Red | Deleted (tracked file deleted but not yet committed) |
| `~` | Dim | Ignored (by .gitignore) |

**Examples:**

```bash
# Git status is on by default — just run treely in any git repo
treely my-project

# Disable git annotations (useful for very large repos where git is slow)
treely my-project --no-git

# Combine git status with --show-size for a powerful at-a-glance view
treely my-project --show-size
```

---

### Rendering & Theme Flags

| Flag | Default | Description |
|---|---|---|
| `--theme THEME` | `default` | Colour theme. Choices: `default`, `dark`, `light`, `minimal`, `nord`. |
| `--no-color` | off | Disable all colour output. **Auto-enabled** when stdout is not a TTY (e.g. pipe). |
| `--no-banner` | off | Suppress the startup ASCII art banner and its accompanying delay. |
| `--format FORMAT` | `text` | Output format. Choices: `text`, `json`, `markdown`. |

**Examples:**

```bash
# Use the Nord colour theme
treely my-project --theme nord

# Use the dark theme
treely my-project --theme dark

# Minimal (no colours, just structure)
treely my-project --theme minimal

# Disable colours entirely (plain text)
treely my-project --no-color

# Skip the banner (useful in scripts or CI)
treely my-project --no-banner

# Output as JSON (machine-readable)
treely my-project --format json

# Output as Markdown
treely my-project --format markdown

# Combined: no banner + no colour + json, pipe to jq
treely my-project --no-banner --format json | jq '.children[].name'
```

---

### Output Destination Flags

| Flag | Short | Default | Description |
|---|---|---|---|
| `--output [FILENAME]` | `-o` | — | Save output to a file. Colours/ANSI are stripped. Default filename: `treely_output.txt`. |
| `--copy` | `-c` | off | Copy output to clipboard. Colours/ANSI are stripped. |

> **Note:** `--output` and `--copy` can be used together. When either is active, the tree is **not** printed to the terminal — only the success message is shown.

**Examples:**

```bash
# Copy tree to clipboard
treely my-project -c

# Copy tree + code to clipboard (the LLM workflow)
treely my-project --use-gitignore --code -c

# Save to default filename (treely_output.txt)
treely my-project -o

# Save to a specific file
treely my-project -o project_structure.txt

# Save as Markdown
treely my-project --format markdown -o STRUCTURE.md

# Save JSON snapshot
treely my-project --format json -o snapshot.json

# Both copy AND save to file at the same time
treely my-project --use-gitignore --code -c -o context.txt
```

---

### Configuration & Profile Flags

| Flag | Default | Description |
|---|---|---|
| `--config PATH` | auto | Path to a TOML config file. Overrides automatic discovery. |
| `--profile NAME` | none | Activate a named profile from the config file. |

See the [Configuration File](#-configuration-file-treelytoml) section for full details.

```bash
# Use a specific config file
treely my-project --config /path/to/my-treely.toml

# Activate the 'llm' profile defined in treely.toml
treely my-project --profile llm

# Profile + CLI flag override (CLI always wins)
treely my-project --profile llm --no-copy
```

---

## 🏗️ Workflow Examples

### 1. Overview of Any Project

The fastest way to understand a new codebase:

```bash
# Auto-exclude .gitignored files, show sizes and a file count
treely my-project --use-gitignore --show-size -s
```

**Output:**
```
my-project/
├── src/
│   ├── main.py   [3.2K]
│   └── utils.py  [1.1K]
├── tests/
│   └── test_main.py  [2.4K]
├── .gitignore  [892.0B]
└── pyproject.toml  [2.9K]

2 directories, 5 files
```

---

### 2. Preparing LLM / AI Context

Treely's most powerful use case. Dump your entire project **structure + code** directly to your clipboard and paste it straight into ChatGPT, Claude, Gemini, etc.

```bash
treely my-project --use-gitignore --code --token-count -c
```

After this command, your clipboard contains:
- The complete directory tree (with gitignore'd files removed)
- The contents of every source file, each preceded by its relative path
- An estimated token count at the bottom

**Pro tip — set it up to work with a single alias:**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias ctx='treely --use-gitignore --code --max-size 500K --token-count -c --no-banner'

# Now just run:
ctx my-project
```

---

### 3. Advanced Code Dump with Exclusions

You want project context but need to omit boilerplate/libraries:

```bash
# Exclude the entire lib/ directory AND minified JS files from code output
# (they still appear in the tree — just not in the code section)
treely my-project --use-gitignore --code --exclude "lib/*|*.min.js" -c
```

```bash
# For an Adobe CEP panel project: exclude the SDK and compiled files
treely "Silence Cutter/" --code --exclude "lib/*|custom/Mp3.epr|*.debug" -c
```

```bash
# For a Django project: skip migrations and static files from code
treely my-django-app --use-gitignore --code \
  --exclude "*/migrations/*|static/*|media/*" \
  --max-size 100K -c
```

---

### 4. Generate Project Documentation

Create a `STRUCTURE.md` file you can commit directly to your repo:

```bash
treely my-project --use-gitignore --show-size -s --format markdown -o STRUCTURE.md
```

**Output in `STRUCTURE.md`:**
````markdown
# `my-project/`

```
my-project/
├── src/
│   ├── main.py   [3.2K]
│   └── utils.py  [1.1K]
...
```

_2 directories, 5 files_
````

---

### 5. Machine-Readable JSON Output

Perfect for CI pipelines, scripts, or integrations:

```bash
# Get a JSON snapshot of the project
treely my-project --use-gitignore --format json --no-banner -o snapshot.json
```

**Or pipe to `jq` for instant querying:**
```bash
# List all top-level filenames
treely my-project --format json --no-banner | jq '[.children[].name]'

# Find all Python files recursively
treely my-project --format json --no-banner | jq '.. | objects | select(.extension == ".py") | .name'

# Get total byte count of all files
treely my-project --format json --no-banner | jq '[.. | objects | select(.type == "file") | .size_bytes // 0] | add'
```

**JSON Schema for a file node:**
```json
{
  "name": "main.py",
  "type": "file",
  "path": "/absolute/path/to/main.py",
  "extension": ".py",
  "size_bytes": 3276,
  "size_human": "3.2K",
  "is_binary": false,
  "is_symlink": false,
  "git_status": "M"
}
```

**JSON Schema for a directory node:**
```json
{
  "name": "src",
  "type": "directory",
  "path": "/absolute/path/to/src",
  "git_status": null,
  "children": [ ... ]
}
```

---

### 6. Markdown for READMEs & GitHub

```bash
# Generate markdown and save to a file
treely my-project --use-gitignore --format markdown -o STRUCTURE.md

# With code content — great for documenting a small library
treely my-lib --use-gitignore --code --format markdown -o docs/structure.md

# Generate and copy for pasting into a GitHub issue or PR description
treely my-project --format markdown --no-banner -c
```

---

### 7. Git Status Awareness

```bash
# See which files you've changed at a glance (auto-enabled in git repos)
treely src/

# Disable git status if you just want the plain tree
treely src/ --no-git
```

```
src/
├── api/
│   ├── routes.py    ● [4.1K]   ← modified, not yet committed
│   └── models.py      [2.8K]
├── core/
│   ├── engine.py    + [1.9K]   ← staged for commit
│   └── utils.py     ? [512.0B] ← new, untracked file
└── main.py            [1.2K]
```

---

### 8. Deep-Dive with Sorting & Filtering

```bash
# Find the largest files in a project (sorted by size)
treely my-project --use-gitignore --sort size --show-size --files-only -L 3

# See which files were most recently changed (great after a build)
treely build/ --sort mtime --show-size -L 2

# Inspect only a specific file type, sorted by extension
treely my-project --use-gitignore --pattern "*.ts" --sort ext

# Show only the top-level directory structure (for a quick map)
treely my-project -L 1 --dirs-only

# Show all hidden config files at the root
treely my-project -a -L 1 --files-only
```

---

## ⚙️ Configuration File (`treely.toml`)

Tired of typing the same flags every time? Create a `treely.toml` in your project root (or globally) to set persistent defaults.

### File Discovery Order

Treely searches for a config file in this order:

1. Path given via `--config <path>` (explicit override)
2. `treely.toml` in the current working directory
3. `.treely.toml` in the current working directory
4. `~/.config/treely/config.toml` (Linux / macOS)
5. `%APPDATA%\treely\config.toml` (Windows)

### Full `treely.toml` Example

```toml
# treely.toml — Project-local configuration

[defaults]
# Always use the project's .gitignore
use_gitignore = true

# Always show file sizes
show_size = true

# Always print a directory/file count
summary = true

# Use the Nord theme
theme = "nord"

# Suppress the startup banner for faster runs
no_banner = false

# Default sort order
sort = "name"

# ─────────────────────────────────────────────────────────────────────────────
# Profiles — activate with: treely --profile <name>
# ─────────────────────────────────────────────────────────────────────────────

[profiles.llm]
# treely --profile llm
# Optimised for pasting project context into an LLM (ChatGPT, Claude, etc.)
use_gitignore = true
code          = true
copy          = true
no_banner     = true
max_size      = "500K"
token_count   = true
exclude       = "*.lock|dist/*|build/*|*.min.js|vendor/*"

[profiles.docs]
# treely --profile docs
# Generate Markdown documentation for the project
use_gitignore = true
show_size     = true
summary       = true
format        = "markdown"
output        = "STRUCTURE.md"
no_banner     = true

[profiles.ci]
# treely --profile ci
# Clean, colourless output for CI pipelines and scripts
use_gitignore = true
no_color      = true
no_banner     = true
summary       = true
format        = "text"

[profiles.snapshot]
# treely --profile snapshot
# Save a full JSON snapshot for scripting / auditing
use_gitignore = true
format        = "json"
output        = "project_snapshot.json"
no_banner     = true
summary       = true

[profiles.review]
# treely --profile review
# For code-reviewing a PR: show git status + code of changed files
use_gitignore = true
show_size     = true
summary       = true
theme         = "dark"
```

### Available Configuration Keys

All configuration keys match their corresponding CLI flag names (with hyphens converted to underscores):

| Key | Type | Description |
|---|---|---|
| `all` | bool | Show hidden files |
| `level` | int | Max recursion depth |
| `sort` | string | `name` \| `size` \| `mtime` \| `ext` |
| `dirs_only` | bool | Show only directories |
| `files_only` | bool | Show only files |
| `full_path` | bool | Print absolute paths |
| `follow_symlinks` | bool | Follow symlinks |
| `show_size` | bool | Show file sizes |
| `summary` | bool | Print file/dir count |
| `pattern` | string | File glob filter |
| `ignore` | string | Pipe-separated ignore patterns |
| `use_gitignore` | bool | Honour `.gitignore` files |
| `code` | bool | Print code content |
| `exclude` | string | Pipe-separated code-exclude patterns |
| `max_size` | string | Max file size for code output (e.g. `"1M"`) |
| `token_count` | bool | Estimate LLM token count |
| `no_git` | bool | Disable git status annotations |
| `theme` | string | `default` \| `dark` \| `light` \| `minimal` \| `nord` |
| `no_color` | bool | Disable colour output |
| `no_banner` | bool | Suppress startup banner |
| `format` | string | `text` \| `json` \| `markdown` |
| `output` | string | Output filename |
| `copy` | bool | Copy to clipboard |

---

## 👤 Profile System

Profiles let you save a complete set of flags under a name and activate them with a single `--profile` argument.

**Precedence order (highest → lowest):**
```
CLI flags  >  Profile values  >  [defaults] values  >  Built-in defaults
```

```bash
# Use the 'llm' profile (code + copy + gitignore + token count)
treely my-project --profile llm

# Use the 'docs' profile (markdown + save to STRUCTURE.md)
treely my-project --profile docs

# Use a profile but override one setting with a CLI flag
# (CLI flags always win over profiles)
treely my-project --profile llm --no-banner

# Use a custom config file with a profile
treely my-project --config ../shared-treely.toml --profile llm
```

---

## 🎨 Themes

Treely ships with 5 carefully designed colour themes. Select with `--theme <name>`.

| Theme | Best For | Highlights |
|---|---|---|
| `default` | Most terminals | Bold blue dirs, white files, yellow git-modified |
| `dark` | Dark terminal backgrounds | Bright colours, blue guide lines |
| `light` | Light terminal backgrounds | Muted colours, works on white backgrounds |
| `minimal` | No colour preference | Bold only, no colour — focuses on structure |
| `nord` | [Nord color palette](https://www.nordtheme.com/) fans | `#81a1c1` dirs, Aurora colours for git status |

```bash
treely my-project --theme default   # default
treely my-project --theme dark      # vibrant on dark backgrounds
treely my-project --theme light     # muted on light backgrounds
treely my-project --theme minimal   # structure only, no colour
treely my-project --theme nord      # Nord palette
```

**Automatic colour detection:** When you pipe output to another command or redirect to a file, Treely automatically disables colour output and the banner.

```bash
# Colours automatically disabled when piping
treely my-project | cat
treely my-project > output.txt
```

---

## 🔴 Git Integration

Treely automatically detects whether the scanned directory is inside a git repository and annotates the tree with live status from `git status --porcelain`.

**No flag needed — just run `treely` inside any git repo.**

```
project/
├── src/
│   ├── api.py        ●   ← modified working tree
│   ├── models.py     +   ← staged (added to index)
│   └── database.py       ← clean
├── tests/
│   └── new_test.py   ?   ← untracked (new file)
├── old_module.py     ✗   ← deleted but not committed
└── README.md             ← clean
```

**In subdirectories of a repo** — Treely correctly adjusts git paths even when you scan a subdirectory of a larger repository.

**Disable git annotations:**
```bash
treely my-project --no-git
```

**Performance tip:** On very large git repositories, `git status` can take a moment. Use `--no-git` in those cases for instant output.

---

## 📊 Output Formats

### `text` (Default)

Human-readable tree with Unicode box-drawing characters. Coloured when outputting to a terminal.

```bash
treely my-project
treely my-project --format text
```

### `json`

Fully structured, machine-readable JSON. Every node includes its type, path, extension, size, binary flag, symlink flag, and git status. File content is embedded when `--code` is used.

```bash
treely my-project --format json
treely my-project --format json | jq .
treely my-project --format json -o snapshot.json
```

### `markdown`

A fenced code block containing the tree, with an H1 heading and per-file code blocks (with language identifiers) when `--code` is used. Ideal for READMEs, GitHub issues, and PR descriptions.

```bash
treely my-project --format markdown
treely my-project --format markdown -o STRUCTURE.md
treely my-project --code --format markdown -c
```

---

## 🐍 Programmatic Python API

Starting in v2.0.0, Treely exposes a stable public API for use in Python scripts and tools.

```python
from pathlib import Path
from treely import TreeConfig, Renderer, walk

# 1. Configure
config = TreeConfig(
    root_path="/path/to/my-project",
    use_gitignore=True,
    code=True,
    show_size=True,
    summary=True,
    exclude="lib/*|*.min.js",
    max_size="500K",
    theme="nord",
)

# 2. Walk the directory tree
result = walk(Path(config.root_path), config, git_status={})

# 3. Render
renderer = Renderer(config)

# Print to terminal (with colour)
renderer.to_console(result)

# Get plain text (for file/clipboard)
plain_text = renderer.to_string(result)

# Get JSON
import json
data = json.loads(renderer.to_json(result))
print(f"Total files: {result.stats.files}")
print(f"Total dirs:  {result.stats.dirs}")
print(f"Total bytes: {result.stats.total_bytes:,}")

# Get Markdown
md = renderer.to_markdown(result)
Path("STRUCTURE.md").write_text(md)
```

**Working with git status:**
```python
from treely.git import get_git_info

in_repo, git_status = get_git_info("/path/to/project")
if in_repo:
    result = walk(Path("/path/to/project"), config, git_status)
```

**Custom filtering with TreeNode:**
```python
from treely import TreeConfig, walk
from treely.tree_node import TreeNode
from pathlib import Path

config = TreeConfig(root_path=".")
result = walk(Path("."), config, {})

def find_large_files(node: TreeNode, threshold: int = 100_000):
    """Recursively find files larger than threshold bytes."""
    for child in node.children:
        if not child.is_dir and child.size and child.size > threshold:
            yield child
        if child.is_dir:
            yield from find_large_files(child, threshold)

for node in find_large_files(result.root):
    print(f"{node.path}  ({node.size:,} bytes)")
```

---

## 🤝 Contributing

Contributions are warmly welcome! Here's how to get started:

### Development Setup

```bash
# Fork & clone the repository
git clone https://github.com/your-fork/treely.git
cd treely

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux / macOS
.venv\Scripts\activate        # Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev,config]"
```

### Running Tests

```bash
# Run the full test suite
pytest tests/

# Run with coverage report
pytest tests/ --cov=treely --cov-report=term-missing

# Run a specific test file
pytest tests/test_walker.py -v

# Run a specific test
pytest tests/test_filters.py::TestGitignoreStack::test_nested_gitignore_applies_only_within_dir -v
```

### Code Quality

```bash
# Lint
ruff check treely/

# Format check
ruff format --check treely/

# Auto-fix formatting
ruff format treely/
```

### Release Workflow

```
1. Edit code in treely/
2. Bump __version__ in treely/__init__.py  AND  version in pyproject.toml
3. Add an entry to CHANGELOG.md
4. Update README.md if new features were added
5. Run: pytest tests/ --cov=treely
6. Run: ruff check treely/
7. Build: python -m build
8. Publish: twine upload dist/*
   — OR — push a git tag vX.Y.Z to trigger the automated publish workflow
```

### Pull Request Guidelines

1. Fork the repository and create a feature branch: `git checkout -b feature/my-feature`
2. Write tests for any new functionality
3. Ensure all 128+ tests pass and coverage doesn't drop significantly
4. Run `ruff check treely/` and `ruff format treely/` before committing
5. Open a pull request with a clear description of the change

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
Copyright (c) 2025 Rudra Mondal
```

---

<div align="center">

Made with ❤️ by [Rudra Mondal](https://github.com/rudra-mondal)

**[⬆ Back to Top](#-treely)**

</div>