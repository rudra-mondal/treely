## 2025-02-14 - Improve Error Handling for Invalid Paths in CLI Tool
**Learning:** For CLI tools that parse paths from users, throwing raw stack traces like `FileNotFoundError` degrades the user experience significantly. Instead of relying on `os.listdir` deeper down to fail when scanning, early validation should happen immediately after CLI args parsing.
**Action:** Always validate input directory paths before invoking main processing functions to present a clean, clear message (`Error: The path 'x' does not exist...`) and exit cleanly with `sys.exit(1)`.
## 2024-08-24 - Pluralization in Summary
**Learning:** Hardcoded strings like "directories" and "files" can feel unpolished when counts are 1. The UX improvement of checking exact counts for singular forms applies to command-line interfaces as well as graphical ones.
**Action:** Always verify if count-based output strings handle pluralization correctly (e.g. 1 directory vs 2 directories).
