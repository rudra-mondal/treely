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
*   **Intelligent Code Printing:** Use the `--code` flag to display the full contents of all relevant code files directly after the tree structure.
*   **Automatic `.gitignore` Support:** The `--use-gitignore` flag intelligently and automatically excludes files and directories specified in your `.gitignore` file. No more manual `--ignore` flags for `node_modules` or `dist`!
*   **Export & Share:**
    *   **Copy to Clipboard (`-c`):** Instantly copy the entire tree and code output to your clipboard, perfect for pasting into LLM prompts (like GPT), GitHub issues, or pull requests.
    *   **Save to File (`-o`):** Save the clean, colorless output directly to a file for documentation or artifacts.
*   **Advanced Filtering & Display:**
    *   Limit the tree depth (`-L`).
    *   Filter by glob patterns (`--pattern`).
    *   Manually ignore files and directories (`--ignore`).
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

```
usage: treely [-h] [-a] [-L LEVEL] [--pattern PATTERN] [--ignore PATTERNS] [--code [IGNORE_PATTERNS]] [--use-gitignore] [-s]
              [--show-size] [-o [FILENAME]] [-c]
              [root_path]

A beautiful and professional directory tree generator.

positional arguments:
  root_path             The starting folder for the tree. Uses current folder if not specified.

options:
  -h, --help            show this help message and exit
  -a, --all             Show all items, including hidden ones (e.g., '.git').
  -L LEVEL, --level LEVEL
                        How many folders deep to look (e.g., -L 2).
  --pattern PATTERN     Show only files/folders that match a pattern (e.g., "*.py").
  --ignore PATTERNS     Don't show items matching a pattern. Use '|' to separate (e.g., "__pycache__|*.tmp").
  --code [IGNORE_PATTERNS]
                        Display code file content after the tree. Use alone for all code, or with patterns to exclude (e.g., --code
                        "file1.py|file2.js").
  --use-gitignore       Automatically ignore files and directories listed in .gitignore.
  -s, --summary         Print a summary of the number of directories and files.
  --show-size           Display the size of each file.
  -o [FILENAME], --output [FILENAME]
                        Save the output to a file. Defaults to 'treely_output.txt' if no name is given. Banner and colors are excluded.
  -c, --copy            Copy the output to the clipboard. Banner and colors are excluded.

Examples:
  # Generate a tree for the current folder
  treely

  # Use the project's .gitignore to automatically exclude files
  treely --use-gitignore

  # Generate a tree 2 levels deep and save it to a file
  treely -L 2 -o my_project_tree.md

  # Show file sizes and a summary of contents
  treely --show-size -s

  # Show tree and copy all code content to clipboard, ignoring 'node_modules'
  treely --ignore "node_modules" --code -c

  # Show only python files, print their content (except config.py), and copy
  treely --pattern "*.py" --code "config.py" -c
```

## ✨ Workflow Examples

Let's use the following project structure for our examples. The `.gitignore` file contains `node_modules/` and `.env`.

```
my-web-app/
├── .git/
├── node_modules/
│   └── ... (many files)
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   └── index.js
├── .env
├── .gitignore
└── package.json
```

### 1. The Smart Default: Using `.gitignore`

This is the recommended way to get a clean overview of any project. `treely` will read your `.gitignore` and automatically exclude `node_modules/` and `.env`.

**Command:**
```bash
treely my-web-app --use-gitignore
```

**Output:**
```
... (banner) ...
my-web-app/
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   └── index.js
├── .gitignore
└── package.json
```
Notice how `.git`, `node_modules`, and `.env` are all gone with one simple flag!

### 2. Create Project Documentation

Generate a complete project overview with file sizes and a summary, and save it directly to a Markdown file. This is perfect for a `README` or project wiki.

**Command:**
```bash
treely my-web-app --use-gitignore --show-size -s -o project_structure.md
```

**Console Message:**
```
... (banner) ...
✔ Output successfully saved to project_structure.md
```

**Contents of `project_structure.md`:**
```
my-web-app/
├── public/
│   └── index.html  [345B]
├── src/
│   ├── App.js  [512B]
│   └── index.js  [230B]
├── .gitignore  [15B]
└── package.json  [780B]

2 directories, 5 files
```

### 3. Prepare an AI/LLM Prompt

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

Your clipboard now contains the full tree and the contents of `index.html`, `App.js`, `index.js`, and `package.json`, perfectly formatted.

### 4. Advanced Filtering and Code View

Generate a tree showing only JavaScript files and print their contents, but exclude `index.js` from the code output.

**Command:**
```bash
treely my-web-app --pattern "*.js" --code "index.js"
```

**Output:**
This will show a tree with only `App.js` and `index.js`, but the `--- FILE CONTENTS ---` section will only contain the code for `App.js`.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/rudra-mondal/treely/issues).

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.