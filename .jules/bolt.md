## 2024-05-15 - os.path.relpath Bottleneck in Directory Traversal
**Learning:** Calling `os.path.relpath` inside a hot loop (like a recursive directory walker) is a significant performance bottleneck. In `treely`, it was called for every single file to check against `.gitignore` and exclude patterns, taking up a large portion of the execution time.
**Action:** When walking a directory recursively, pass the current relative path down as a string parameter and use simple string concatenation (e.g., `current_relative_path + "/" + entry`) instead of repeatedly calling `os.path.relpath(full_path, root)`.

## 2026-04-24 - os.scandir is faster than os.listdir + Path.stat()
**Learning:** `os.listdir()` followed by repeatedly fetching attributes for filtering using `pathlib.Path.is_dir()`, `Path.stat()`, and `os.path.islink()` incurs a huge performance penalty in tight recursive traversal loops. It generates a 30x performance hit in dummy benchmarks.
**Action:** Use `os.scandir()` instead of `os.listdir()`. `os.scandir()` provides an iterator of `os.DirEntry` objects which inherently cache `name`, `is_dir()`, `is_symlink()`, and `stat()` attributes, bypassing additional system calls to the OS. Use it strictly for performance-critical directory traversal.
