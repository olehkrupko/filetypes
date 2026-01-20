import os
import typing

class FileInfo(typing.NamedTuple):
    path: str
    extension: str
    size_bytes: int
    last_modified: float

def scan_directory(path: str) -> typing.Generator[FileInfo, None, None]:
    """
    Recursively scans a directory and yields FileInfo.
    Uses os.scandir for memory efficiency on large directories.
    """
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.'):
                    # Skip hidden files/dirs
                    continue
                    
                if entry.is_dir(follow_symlinks=False):
                    yield from scan_directory(entry.path)
                    
                elif entry.is_file(follow_symlinks=False):
                    try:
                        stat = entry.stat()
                        # Normalize extension to lowercase and remove leading dot
                        # os.path.splitext returns (root, .ext)
                        _, ext = os.path.splitext(entry.name)
                        extension = ext.lower().lstrip('.')
                        if not extension:
                            extension = 'no_extension'
                            
                        yield FileInfo(
                            path=entry.path,
                            extension=extension,
                            size_bytes=stat.st_size,
                            last_modified=stat.st_mtime
                        )
                    except OSError:
                        # Skip files we cannot stat
                        continue
    except OSError:
        # Skip directories we cannot access
        return
