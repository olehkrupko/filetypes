# AI Rules & Project Context

## Project Overview
This is a Python-based file scanning service designed to run in Docker. It scans large directory structures, groups files by type, and provides reporting or file operations (copy/move).

## Core Constraints
1.  **Memory Efficiency**: NEVER use `os.walk` or `glob.glob` on the target directory. fast recursive scanning MUST use `os.scandir` generators.
2.  **No Web UI**: This is a pure Console/CLI application.
3.  **Caching**: Use SQLite for caching. Do not introduce persistent services like Redis.
4.  **Docker First**: The app runs via `docker compose`.
5.  **Python Version**: 3.13+

## Coding Style
-   Use Python Type Hints.
-   Use `pathlib` where convenient, but be mindful of performance in tighter loops if `os.path` is significantly faster (though `pathlib` in 3.13 is quite fast).
-   Docstrings for all public functions.

## Feature Specifics
-   **Scanning**: Recursive generator.
-   **Storage**: `files` table with `path`, `extension`, `size_bytes`, `last_modified`.
-   **Operations**: `move` and `copy` must handle name collisions safely (or at least fail loudly/skip).
