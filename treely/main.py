import os
import time
import sys
import argparse
import fnmatch

# --- Constants ---
CODE_EXTENSIONS = {'.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.hpp',
                   '.go', '.rs', '.php', '.rb', '.md', '.json', '.xml', '.yml', '.yaml',
                   '.sh', '.bat', '.ps1', '.sql', '.ts'}
PRINT_ALL_CODE = "___PRINT_ALL_CODE___"

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

def print_file_contents(file_list):
    if not file_list:
        return
    print("\n" * 2 + "\033[1;36m" + "--- FILE CONTENTS ---" + "\033[0m")
    for file_path in file_list:
        relative_path = os.path.relpath(file_path)
        print("\n\n" + "\033[1;34m" + f"--- {relative_path} ---" + "\033[0m")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
        except Exception as e:
            print("\033[31m" + f"[Error reading file: {e}]" + "\033[0m")

def generate_directory_tree(config):
    files_to_print_code = [] if config.code is not None else None
    code_ignore_patterns = []
    if config.code is not None and config.code != PRINT_ALL_CODE:
        code_ignore_patterns = config.code.split('|')

    time.sleep(1)
    print(f"{os.path.basename(config.root_path)}/")

    _walk_directory(
        path=config.root_path,
        prefix="",
        config=config,
        files_to_print_code=files_to_print_code,
        code_ignore_patterns=code_ignore_patterns,
        current_depth=0
    )

    if files_to_print_code:
        print_file_contents(files_to_print_code)

def _walk_directory(path, prefix, config, files_to_print_code, code_ignore_patterns, current_depth):
    if config.level != -1 and current_depth >= config.level:
        return

    try:
        entries = os.listdir(path)
    except PermissionError:
        print(prefix + "└── " + "\033[31m[Permission Denied]\033[0m")
        return

    filtered_entries = []
    ignore_patterns = config.ignore.split('|') if config.ignore else []

    for entry in entries:
        full_path = os.path.join(path, entry)
        if any(fnmatch.fnmatch(entry, pat) for pat in ignore_patterns):
            continue
        if config.pattern and not fnmatch.fnmatch(entry, config.pattern):
            continue
        if not config.all and os.path.isdir(full_path) and entry.startswith('.'):
            continue
        filtered_entries.append(entry)

    dirs = sorted([e for e in filtered_entries if os.path.isdir(os.path.join(path, e))])
    files = sorted([e for e in filtered_entries if not os.path.isdir(os.path.join(path, e))])
    combined = dirs + files

    for index, entry in enumerate(combined):
        full_path = os.path.join(path, entry)
        is_last_entry = (index == len(combined) - 1)
        name = entry + ("/" if os.path.isdir(full_path) else "")
        print(prefix + ("└── " if is_last_entry else "├── ") + name)

        if files_to_print_code is not None and os.path.isfile(full_path):
            if os.path.splitext(entry)[1] in CODE_EXTENSIONS:
                if not any(fnmatch.fnmatch(entry, pat) for pat in code_ignore_patterns):
                    files_to_print_code.append(full_path)
        
        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if is_last_entry else "│   ")
            _walk_directory(
                path=full_path,
                prefix=new_prefix,
                config=config,
                files_to_print_code=files_to_print_code,
                code_ignore_patterns=code_ignore_patterns,
                current_depth=current_depth + 1
            )

def main():
    parser = argparse.ArgumentParser(
        description="A beautiful and professional directory tree generator.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Generate a tree for the current folder
  treely

  # Generate a tree for a specific project, 2 levels deep
  treely ./my-project -L 2

  # Show the tree and the content of all code files, but ignore the 'node_modules' folder
  treely --ignore "node_modules" --code

  # Show a tree of only python files and print their contents, except for 'config.py'
  treely --pattern "*.py" --code "config.py"
"""
    )

    parser.add_argument('root_path', nargs='?', default=os.getcwd(), help="The starting folder for the tree. Uses the current folder if not specified.")
    parser.add_argument('-a', '--all', action='store_true', help="Show all items, including hidden directories (e.g., '.git', '.vscode').")
    parser.add_argument('-L', '--level', type=int, default=-1, metavar='LEVEL', help="How many folders deep to look. e.g., '-L 2' shows two levels.")
    parser.add_argument('--pattern', type=str, metavar='PATTERN', help="Show only files/folders that match a pattern. e.g., \"*.py\".")
    parser.add_argument('--ignore', type=str, metavar='PATTERNS', help="Don't show files/folders that match a pattern.\nUse '|' to separate multiple patterns. e.g., \"__pycache__|*.tmp\".")
    parser.add_argument('--code', nargs='?', const=PRINT_ALL_CODE, default=None, metavar='IGNORE_PATTERNS', help="Display the content of code files after the tree.\n- Use '--code' alone to show all detected code files.\n- Use '--code \"file1.py|file2.js\"' to show code but skip specific files.")
    
    args = parser.parse_args()
    
    print_banner()
    generate_directory_tree(args)

if __name__ == "__main__":
    main()