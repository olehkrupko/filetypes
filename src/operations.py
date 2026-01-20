import shutil
import logging
from pathlib import Path


def get_unique_path(dest_dir: Path, filename: str) -> Path:
    """
    Handle name collisions by appending a counter.
    e.g. file.txt -> file_1.txt -> file_2.txt
    """
    target = dest_dir / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1

    while True:
        target = dest_dir / f"{stem}_{counter}{suffix}"
        if not target.exists():
            return target
        counter += 1


def copy_files(files: list[str], destination: str, base_path: str = "/scan") -> None:
    dest_path = Path(destination)
    base_path_obj = Path(base_path)

    for file_path in files:
        src = Path(file_path)
        if not src.exists():
            logging.warning(f"File not found, skipping: {file_path}")
            continue

        try:
            # Calculate path relative to scan root
            relative_path = src.relative_to(base_path_obj)
            target = dest_path / relative_path

            # Ensure parent directories exist
            target.parent.mkdir(parents=True, exist_ok=True)

            # Note: We use unique path for the filename part if needed,
            # but usually for structure restoration we want exact matches.
            # However, to avoid overwriting if something exists:
            if target.exists():
                target = get_unique_path(target.parent, target.name)

            shutil.copy2(src, target)
        except ValueError:
            # If file is not under base_path, fallback to flat copy
            target = get_unique_path(dest_path, src.name)
            shutil.copy2(src, target)
        except Exception as e:
            logging.error(f"Failed to copy {src}: {e}")


def move_files(files: list[str], destination: str, base_path: str = "/scan") -> None:
    dest_path = Path(destination)
    base_path_obj = Path(base_path)

    for file_path in files:
        src = Path(file_path)
        if not src.exists():
            logging.warning(f"File not found, skipping: {file_path}")
            continue

        try:
            # Calculate path relative to scan root
            relative_path = src.relative_to(base_path_obj)
            target = dest_path / relative_path

            # Ensure parent directories exist
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                target = get_unique_path(target.parent, target.name)

            shutil.move(src, target)
        except ValueError:
            # Fallback for files outside base_path
            target = get_unique_path(dest_path, src.name)
            shutil.move(src, target)
        except Exception as e:
            logging.error(f"Failed to move {src}: {e}")
