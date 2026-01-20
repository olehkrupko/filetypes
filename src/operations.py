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

def copy_files(files: list[str], destination: str) -> None:
    dest_dir = Path(destination)
    if not dest_dir.exists():
        os.makedirs(dest_dir, exist_ok=True)
        
    for file_path in files:
        src = Path(file_path)
        if not src.exists():
            logging.warning(f"File not found, skipping: {file_path}")
            continue
            
        target = get_unique_path(dest_dir, src.name)
        try:
            shutil.copy2(src, target)
        except Exception as e:
            logging.error(f"Failed to copy {src} to {target}: {e}")

def move_files(files: list[str], destination: str) -> None:
    dest_dir = Path(destination)
    if not dest_dir.exists():
        os.makedirs(dest_dir, exist_ok=True)
        
    for file_path in files:
        src = Path(file_path)
        if not src.exists():
            logging.warning(f"File not found, skipping: {file_path}")
            continue
            
        target = get_unique_path(dest_dir, src.name)
        try:
            shutil.move(src, target)
        except Exception as e:
            logging.error(f"Failed to move {src} to {target}: {e}")
