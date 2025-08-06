# Treely 🌳

A modern, beautiful, and powerful command-line directory tree generator. `treely` goes beyond a simple `tree` command by offering smart filtering, automatic `.gitignore` parsing, and a killer feature: the ability to output the contents of your code files, ready to be saved, shared, or copied directly to your clipboard.

It's the perfect tool for scaffolding a project's structure for documentation, preparing context for AI/LLM prompts, or getting a high-level overview of a new codebase.

[![PyPI version](https://img.shields.io/pypi/v/treely.svg)](https://pypi.org/project/treely/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/treely.svg)](https://pypi.org/project/treely/)
![GitHub stars](https://img.shields.io/github/stars/rudra-mondal/treely)

![Treely Demo GIF](https://github.com/user-attachments/assets/bdba702c-5786-4a12-9c93-10c48b2b1577)

*(Note: The demo GIF shows an older version!)*

## 🌟 Key Features

*   **Elegant Tree Structure:** Generates a clean, easy-to-read directory tree with colorful output.
*   **Powerful Code Context:** Use `--code` to print all relevant code, and then use the `--exclude` flag to surgically remove files, directories, or patterns (like `lib/*` or `*.log`) from the code output without hiding them from the tree.
*   **Automatic `.gitignore` Support:** The `--use-gitignore` flag intelligently and automatically excludes files and directories specified in your `.gitignore` file. No more manual `--ignore` flags for `node_modules` or `dist`!
*   **Export & Share:**
    *   **Copy to Clipboard (`-c`):** Instantly copy the entire tree and code output to your clipboard, perfect for pasting into LLM prompts (like GPT), GitHub issues, or pull requests.
    *   **Save to File (`-o`):** Save the clean, colorless output directly to a file for documentation or artifacts.
*   **Advanced Filtering & Display:**
    *   Limit the tree depth (`-L`).
    *   Filter by glob patterns (`--pattern`).
    *   Ignore files and directories from the tree (`--ignore`).
    *   Display file sizes (`--show-size`).
    *   Get a project summary (`-s`).
*   **Cross-Platform:** Works seamlessly on Windows, macOS, and Linux.

## 📦 Installation

You can install `treely` directly from PyPI. The necessary dependencies (`pyperclip` and `pathspec`) will be installed automatically.

```bash
pip install treely
```

Ensure that your Python scripts directory is in your system's `PATH` to run `treely` from anywhere.

## 🚀 Usage

### Basic Command

To generate a tree for the current directory:
```bash
treely
```

For a specific directory:
```bash
treely /path/to/your/project
```

### Command-line Options

This is the output from `treely --help`, showing the new, simplified flags.

```
usage: treely [-h] [-a] [-L LEVEL] [--pattern PATTERN] [--ignore PATTERNS] [--code] [--exclude PATTERNS] [--use-gitignore] [-s] [--show-size] [-o [FILENAME]] [-c] [root_path]

A beautiful and professional directory tree generator.

positional arguments:
  root_path             The starting folder for the tree. Uses current folder if not specified.

options:
  -h, --help            show this help message and exit
  -a, --all             Show all items, including hidden ones (e.g., '.git').
  -L LEVEL, --level LEVEL
                        How many folders deep to look (e.g., -L 2).
  --pattern PATTERN     Show only files/folders that match a pattern (e.g., "*.py").
  --ignore PATTERNS     Don't show items matching a pattern in the tree. Use '|' to separate.
  --code                Display the content of all detected code files after the tree.
  --exclude PATTERNS    When using --code, exclude files/folders from the code output.
                        Use '|' to separate patterns (e.g., "lib/*|*.log|file.js").
  --use-gitignore       Automatically ignore files/dirs from the tree listed in .gitignore.
  -s, --summary         Print a summary of the number of directories and files.
  --show-size           Display the size of each file.
  -o [FILENAME], --output [FILENAME]
                        Save output to a file. Defaults to 'treely_output.txt'. Banner/colors are excluded.
  -c, --copy            Copy output to the clipboard. Banner/colors are excluded.

Examples:
  # Generate a tree for the current folder
  treely

  # Use the project's .gitignore to automatically exclude files from the tree
  treely --use-gitignore

  # Show the tree and the content of all code files
  treely --code

  # Show code content, but exclude all files in 'lib' and 'custom' directories
  treely --code --exclude "lib/*|custom/*"

  # Show code, but exclude all HTML files and a specific JS file
  treely --code --exclude "*.html|panel.js"
```

## ✨ Workflow Examples

### 1. The Smart Default: Using `.gitignore`

This is the recommended way to get a clean overview of any project. `treely` will read your `.gitignore` and automatically exclude `node_modules/` and `.env` from the tree.

**Command:**
```bash
treely my-web-app --use-gitignore
```

**Output:**
```
my-web-app/
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   └── index.js
├── .gitignore
└── package.json
```
Notice how `.git` and `node_modules` are all gone with one simple flag!

### 2. Create Project Documentation

Generate a complete project overview with file sizes and a summary, and save it directly to a Markdown file.

**Command:**
```bash
treely my-web-app --use-gitignore --show-size -s -o project_structure.md
```

**Console Message:**
```
... (banner) ...
✔ Output successfully saved to project_structure.md
```

### 3. Prepare a Basic AI/LLM Prompt

This is `treely`'s superpower. Generate a complete project context (structure and all relevant code) and copy it directly to your clipboard. You are now ready to paste it into ChatGPT, Claude, or any other LLM.

**Command:**
```bash
treely my-web-app --use-gitignore --code -c
```

**Console Message:**
```
... (banner) ...
✔ Tree structure copied to clipboard.
```
Your clipboard now contains the full tree and the contents of `index.html`, `App.js`, `index.js`, `.gitignore`, and `package.json`, perfectly formatted.

### 4. Advanced Prompting with Exclusions

Imagine you want to provide context about a project, but you want to exclude boilerplate, libraries, or irrelevant files from the code output to save tokens and focus the AI's attention. This is where `--exclude` shines.

Let's use this structure:
```
Silence Cutter/
├── CSXS/
│   └── manifest.xml
├── custom/
│   └── Mp3.epr
├── lib/
│   ├── CSInterface.js
│   └── Vulcan.js
├── .debug
└── panel.js
```

**Goal:** Get the code for the project, but exclude the entire `lib` directory and the specific `Mp3.epr` file.

**Command:**
```bash
treely "Silence Cutter/" --code --exclude "lib/*|custom/Mp3.epr"
```

**Result:**
The output will show the complete directory tree, including `lib/` and `custom/`. However, the `--- FILE CONTENTS ---` section will intelligently skip the code for `CSInterface.js`, `Vulcan.js`, and `Mp3.epr`, giving you a cleaner, more focused result.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/rudra-mondal/treely/issues).

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.