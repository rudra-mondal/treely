
# 🌳 Treely

[![PyPI version](https://badge.fury.io/py/treely.svg)](https://badge.fury.io/py/treely)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/treely.svg)](https://pypi.org/project/treely/)

A beautiful and powerful command-line directory tree generator with advanced filtering and code-viewing capabilities.

![Treely Demo GIF](https://github.com/user-attachments/assets/bdba702c-5786-4a12-9c93-10c48b2b1577)


---

## 🎯 Core Features

*   **Beautiful Output**: Generates clean, colorful, and readable directory trees.
*   **Depth Limiting**: Control how many levels deep the tree goes (`-L`).
*   **Advanced Filtering**: Ignore or include specific files/folders using powerful patterns (`--ignore`, `--pattern`).
*   **Code Viewer**: Display the contents of all detected code files right in your terminal (`--code`).
*   **Fine-Grained Control**: Exclude specific files from the code viewer, even while showing others.

---

## 🚀 Installation

Install `treely` globally using `pip`. Python 3.7+ is required.

```bash
pip install treely
```

---

## ⚙️ Usage

After installation, the `treely` command will be available in your terminal.

#### **Basic Examples**

```bash
# Generate a simple tree for the current folder
treely

# Generate a tree for a specific project, only 2 levels deep
treely ./my-project -L 2
```

#### **Advanced Filtering**

```bash
# Ignore common clutter like 'node_modules' and '__pycache__'
treely --ignore "node_modules|__pycache__"

# Show only Python and Markdown files in your project
treely --pattern "*.py|*.md"
```

#### **Using the Code Viewer**

```bash
# Show the tree AND the content of all detected code files
# (This is great for sharing a project's context)
treely --code

# Show code, but specifically exclude configuration and lock files from the output
treely --ignore "node_modules" --code "package.json|package-lock.json"
```

---
This tool was created as a fun and educational project. Enjoy!