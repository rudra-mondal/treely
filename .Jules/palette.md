## 2025-02-14 - Improve Error Handling for Invalid Paths in CLI Tool
**Learning:** For CLI tools that parse paths from users, throwing raw stack traces like `FileNotFoundError` degrades the user experience significantly. Instead of relying on `os.listdir` deeper down to fail when scanning, early validation should happen immediately after CLI args parsing.
**Action:** Always validate input directory paths before invoking main processing functions to present a clean, clear message (`Error: The path 'x' does not exist...`) and exit cleanly with `sys.exit(1)`.
