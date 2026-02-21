import os
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


def _get_ext_subfolder(file_path: str) -> str:
    """Extract extension for subfolder grouping."""
    _, ext = os.path.splitext(file_path)
    return ext.lower().lstrip(".") or "no_extension"


def copy_files(files: list[str], destination: str, base_path: str = "/scan", group_by_ext: bool = False) -> None:
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
            file_dest = dest_path / _get_ext_subfolder(file_path) if group_by_ext else dest_path
            target = file_dest / relative_path

            # Ensure parent directories exist
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                target = get_unique_path(target.parent, target.name)

            shutil.copy2(src, target)
        except ValueError:
            # If file is not under base_path, fallback to flat copy
            file_dest = dest_path / _get_ext_subfolder(file_path) if group_by_ext else dest_path
            target = get_unique_path(file_dest, src.name)
            file_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        except Exception as e:
            logging.error(f"Failed to copy {src}: {e}")


def move_files(files: list[str], destination: str, base_path: str = "/scan", group_by_ext: bool = False) -> None:
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
            file_dest = dest_path / _get_ext_subfolder(file_path) if group_by_ext else dest_path
            target = file_dest / relative_path

            # Ensure parent directories exist
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                target = get_unique_path(target.parent, target.name)

            shutil.move(src, target)
        except ValueError:
            # Fallback for files outside base_path
            file_dest = dest_path / _get_ext_subfolder(file_path) if group_by_ext else dest_path
            target = get_unique_path(file_dest, src.name)
            file_dest.mkdir(parents=True, exist_ok=True)
            shutil.move(src, target)
        except Exception as e:
            logging.error(f"Failed to move {src}: {e}")
