import os
import time
import sys
import argparse
import fnmatch
import re

# --- Constants ---
CODE_EXTENSIONS = {
    '.py',    # Python
    '.js',    # JavaScript
    '.ts',    # TypeScript
    '.jsx',   # React JSX
    '.tsx',   # React TSX
    '.html',  # HTML
    '.htm',   # HTML (alternate)
    '.css',   # CSS
    '.scss',  # Sass
    '.less',  # Less CSS
    '.java',  # Java
    '.c',     # C
    '.cpp',   # C++
    '.h',     # C Header
    '.hpp',   # C++ Header
    '.cs',    # C#
    '.go',    # Go
    '.rs',    # Rust
    '.php',   # PHP
    '.rb',    # Ruby
    '.kt',    # Kotlin
    '.swift', # Swift
    '.m',     # Objective-C
    '.mm',    # Objective-C++
    '.dart',  # Dart (Flutter)
    '.scala', # Scala
    '.lua',   # Lua
    '.pl',    # Perl
    '.sh',    # Shell script
    '.bash',  # Bash script
    '.bat',   # Batch (Windows)
    '.ps1',   # PowerShell
    '.sql',   # SQL
    '.xml',   # XML
    '.json',  # JSON
    '.yaml',  # YAML
    '.yml',   # YAML (alternate)
    '.toml',  # TOML
    '.ini',   # INI config
    '.env',   # Env config
    '.md',    # Markdown
    '.rst',   # reStructuredText
    '.tex',   # LaTeX
    '.cfg',   # Config file
    '.conf',  # Config file
    '.make',  # Makefile
    '.mk',    # Makefile (alt)
    '.dockerfile',  # Dockerfile (if saved as extension)
    '.gradle',      # Gradle build
    '.tsbuildinfo', # TypeScript build info
    '.gitignore',   # Special case for dotfiles
    '.debug',       # For Debuging files
}

PRINT_ALL_CODE = "___PRINT_ALL_CODE___"
DEFAULT_OUTPUT_FILENAME = "treely_output.txt"

# Optional dependency handling
try:
    import pyperclip
except ImportError:
    pyperclip = None
try:
    import pathspec
except ImportError:
    pathspec = None

def print_banner():
    banner_lines = [
        "  _______            _       ",
        " |__   __|          | |      ",
        "    | |_ __ ___  ___| |_   _ ",
        "    | | '__/ _ \\/ _ \\ | | | |",
        "    | | | |  __/  __/ | |_| |",
        "    |_|_|  \\___|\\___|_|\\__, |",
        "                        __/ |",
        "                       |___/ "
    ]
    for line in banner_lines:
        print("\033[32m" + line + "\033[0m")
        time.sleep(0.01)

def _strip_ansi_codes(text):
    """Removes ANSI escape sequences from a string."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def _get_human_readable_size(size, precision=1):
    """Converts a size in bytes to a human-readable format (K, M, G)."""
    suffixes = ['B', 'K', 'M', 'G', 'T']
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1
        size /= 1024.0
    return f"{size:.{precision}f}{suffixes[suffix_index]}"

def _add_file_contents_to_lines(file_list, output_lines):
    """Appends formatted file contents to the output lines list."""
    if not file_list:
        return
    output_lines.append("\n" * 2 + "\033[1;36m" + "--- FILE CONTENTS ---" + "\033[0m")
    for file_path in file_list:
        relative_path = os.path.relpath(file_path)
        output_lines.append("\n\n" + "\033[1;34m" + f"--- {relative_path} ---" + "\033[0m")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                output_lines.append(f.read())
        except Exception as e:
            output_lines.append("\033[31m" + f"[Error reading file: {e}]" + "\033[0m")

def generate_directory_tree(config):
    """
    Generates the complete output string for the directory tree and file contents.
    """
    output_lines = []
    files_to_print_code = [] if config.code is not None else None
    code_ignore_patterns = []
    if config.code is not None and config.code != PRINT_ALL_CODE:
        code_ignore_patterns = config.code.split('|')
    
    stats = {'dirs': 0, 'files': 0}
    
    gitignore_spec = None
    if config.use_gitignore:
        gitignore_path = os.path.join(config.root_path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', f)

    output_lines.append(f"{os.path.basename(config.root_path)}/")

    _walk_directory(
        path=config.root_path,
        prefix="",
        config=config,
        output_lines=output_lines,
        files_to_print_code=files_to_print_code,
        code_ignore_patterns=code_ignore_patterns,
        current_depth=0,
        stats=stats,
        gitignore_spec=gitignore_spec
    )
    
    if config.summary:
        output_lines.append("")
        output_lines.append(f"{stats['dirs']} directories, {stats['files']} files")

    if files_to_print_code:
        _add_file_contents_to_lines(files_to_print_code, output_lines)
    
    return "\n".join(output_lines)

def _walk_directory(path, prefix, config, output_lines, files_to_print_code, code_ignore_patterns, current_depth, stats, gitignore_spec):
    """Recursively walks the directory and appends formatted lines to output_lines."""
    if config.level != -1 and current_depth >= config.level:
        return

    try:
        entries = os.listdir(path)
    except PermissionError:
        output_lines.append(prefix + "└── " + "\033[31m[Permission Denied]\033[0m")
        return

    filtered_entries = []
    ignore_patterns = config.ignore.split('|') if config.ignore else []

    for entry in entries:
        full_path = os.path.join(path, entry)
        
        if gitignore_spec:
            relative_path = os.path.relpath(full_path, config.root_path)
            if gitignore_spec.match_file(relative_path.replace(os.sep, '/')):
                continue
        
        if any(fnmatch.fnmatch(entry, pat) for pat in ignore_patterns):
            continue
        if config.pattern and not fnmatch.fnmatch(entry, config.pattern):
            continue
            
        if not config.all and ((os.path.isdir(full_path) and entry.startswith('.')) or entry == '__pycache__'):
            continue
            
        filtered_entries.append(entry)

    dirs = sorted([e for e in filtered_entries if os.path.isdir(os.path.join(path, e))])
    files = sorted([e for e in filtered_entries if not os.path.isdir(os.path.join(path, e))])
    combined = dirs + files

    for index, entry in enumerate(combined):
        full_path = os.path.join(path, entry)
        is_last_entry = (index == len(combined) - 1)
        connector = "└── " if is_last_entry else "├── "
        
        if os.path.isdir(full_path):
            stats['dirs'] += 1
            name = entry + "/"
        else:
            stats['files'] += 1
            name = entry
        
        line = f"{prefix}{connector}{name}"

        if os.path.isfile(full_path) and config.show_size:
            try:
                size = os.path.getsize(full_path)
                line += f"  \033[38;5;240m[{_get_human_readable_size(size)}]\033[0m"
            except OSError:
                pass 
        
        output_lines.append(line)

        if files_to_print_code is not None and os.path.isfile(full_path):
            ## FIX ##: This is the new, more robust logic for identifying code files.
            is_code_file = False
            ext = os.path.splitext(entry)[1]
            
            # 1. Standard check for extensions like '.py', '.js'
            if ext in CODE_EXTENSIONS:
                is_code_file = True
            # 2. Check for exact filenames like '.gitignore', '.env' which are in the set
            elif entry in CODE_EXTENSIONS:
                is_code_file = True
            # 3. Check for extension-less files like 'Dockerfile' by comparing against the set
            elif not ext and f".{entry.lower()}" in CODE_EXTENSIONS:
                is_code_file = True

            if is_code_file:
                if not any(fnmatch.fnmatch(entry, pat) for pat in code_ignore_patterns):
                    files_to_print_code.append(full_path)
        
        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if is_last_entry else "│   ")
            _walk_directory(
                path=full_path,
                prefix=new_prefix,
                config=config,
                output_lines=output_lines,
                files_to_print_code=files_to_print_code,
                code_ignore_patterns=code_ignore_patterns,
                current_depth=current_depth + 1,
                stats=stats,
                gitignore_spec=gitignore_spec
            )

def main():
    parser = argparse.ArgumentParser(
        description="A beautiful and professional directory tree generator.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
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
"""
    )

    parser.add_argument('root_path', nargs='?', default=os.getcwd(), help="The starting folder for the tree. Uses current folder if not specified.")
    parser.add_argument('-a', '--all', action='store_true', help="Show all items, including hidden ones (e.g., '.git').")
    parser.add_argument('-L', '--level', type=int, default=-1, metavar='LEVEL', help="How many folders deep to look (e.g., -L 2).")
    parser.add_argument('--pattern', type=str, metavar='PATTERN', help="Show only files/folders that match a pattern (e.g., \"*.py\").")
    parser.add_argument('--ignore', type=str, metavar='PATTERNS', help="Don't show items matching a pattern. Use '|' to separate (e.g., \"__pycache__|*.tmp\").")
    parser.add_argument('--code', nargs='?', const=PRINT_ALL_CODE, default=None, metavar='IGNORE_PATTERNS', help="Display code file content after the tree. Use alone for all code, or with patterns to exclude (e.g., --code \"file1.py|file2.js\").")
    
    parser.add_argument('--use-gitignore', action='store_true', help="Automatically ignore files and directories listed in .gitignore.")
    parser.add_argument('-s', '--summary', action='store_true', help="Print a summary of the number of directories and files.")
    parser.add_argument('--show-size', action='store_true', help="Display the size of each file.")
    parser.add_argument('-o', '--output', nargs='?', const=DEFAULT_OUTPUT_FILENAME, default=None, metavar='FILENAME', help="Save the output to a file. Defaults to 'treely_output.txt' if no name is given. Banner and colors are excluded.")
    parser.add_argument('-c', '--copy', action='store_true', help="Copy the output to the clipboard. Banner and colors are excluded.")
    
    args = parser.parse_args()
    
    if args.copy and not pyperclip:
        print("\033[31mError: 'pyperclip' is not installed. Please run 'pip install pyperclip' to use the --copy feature.\033[0m", file=sys.stderr)
        sys.exit(1)
    if args.use_gitignore and not pathspec:
        print("\033[31mError: 'pathspec' is not installed. Please run 'pip install pathspec' to use the --use-gitignore feature.\033[0m", file=sys.stderr)
        sys.exit(1)

    print_banner()
    time.sleep(0.5)

    final_output = generate_directory_tree(args)

    if args.copy:
        clean_output = _strip_ansi_codes(final_output)
        try:
            pyperclip.copy(clean_output)
            print("\033[32m✔ Tree structure copied to clipboard.\033[0m")
        except pyperclip.PyperclipException as e:
            print(f"\033[31mError: Could not copy to clipboard: {e}\033[0m", file=sys.stderr)
            sys.exit(1)
    elif args.output:
        filename = args.output
        clean_output = _strip_ansi_codes(final_output)
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(clean_output)
            print(f"\033[32m✔ Output successfully saved to {filename}\033[0m")
        except IOError as e:
            print(f"\033[31mError: Could not write to file {filename}: {e}\033[0m", file=sys.stderr)
            sys.exit(1)
    else:
        print(final_output)

if __name__ == "__main__":
    main()