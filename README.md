# FileTypes Scanner

A Dockerized Python service that recursively scans directories, groups files by type, and provides reporting with optional file operations.

## Features

- **Recursive Scanning** — Memory-efficient scanning using generators (`os.scandir`)
- **File Grouping** — Groups files by extension with count and total size
- **Caching** — SQLite-based caching for fast subsequent queries
- **File Operations** — Copy or move files by type to a destination
- **Report Export** — Saves reports to timestamped files (no overwrites)

## Quick Start

```bash
# one-liner
docker compose up --build --remove-orphans --force-recreate

# Build the container
docker compose build

# Scan a directory and generate a report
docker compose run --remove-orphans scanner

# Use cached results only (no filesystem scan)
docker compose run --remove-orphans scanner --force-cache --type mp4

# Use cached results only (no filesystem scan)
docker compose run --remove-orphans scanner --force-cache --type mp4 --action copy --dest /data/mp4
```

## CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--force-cache` | `false` | Use cache only, skip scanning |
| `--verbose` | `false` | Show detailed output |
| `--action` | `report` | Action: `report`, `copy`, or `move` |
| `--type` | — | File extension filter (required for copy/move) |
| `--dest` | — | Destination directory (required for copy/move) |
| `--report-dir` | `/data/reports` | Directory to save report files |

## Examples

### Generate a Report

```bash
docker compose run scanner --verbose
```

Reports are saved to `/data/reports/report-YYYYMMDD_HHMMSS.txt`

### Copy All PDFs to a Folder

```bash
docker compose run scanner --action copy --type pdf --dest /data/pdfs
```

### Move All Images

```bash
docker compose run scanner --action move --type jpg --dest /data/images
```

## Project Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── AI_RULES.md
└── src/
    ├── __init__.py
    ├── main.py          # CLI entry point
    ├── scanner.py       # Recursive directory scanner
    ├── storage.py       # SQLite caching layer
    ├── operations.py    # File copy/move operations
    └── tests/
        └── test_core.py # Unit tests
```

## Running Tests

```bash
docker compose run --entrypoint pytest scanner src/tests/test_core.py
```

## Volumes

The `docker-compose.yml` mounts two volumes:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/data` | Directory to scan |
| `cache_data` | `/app/cache` | SQLite database |

## Requirements

- Docker
- Docker Compose

## License

MIT
