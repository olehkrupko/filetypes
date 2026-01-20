import pytest
import tempfile
from pathlib import Path
from ..scanner import scan_directory
from ..storage import Storage


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        # Create structure
        (path / "file1.txt").touch()
        (path / "file2.log").touch()
        (path / "sub").mkdir()
        (path / "sub" / "file3.txt").touch()
        yield path


def test_scanner_counts(temp_dir):
    files = list(scan_directory(str(temp_dir)))
    assert len(files) == 3
    extensions = sorted([f.extension for f in files])
    assert extensions == ["log", "txt", "txt"]


def test_storage_stats(tmp_path):
    # Use temp file db for testing (avoid memory db persistence issues)
    db_file = tmp_path / "test.db"
    storage = Storage(str(db_file))

    # Mock data
    class MockFile:
        def __init__(self, path, ext, size):
            self.path = path
            self.extension = ext
            self.size_bytes = size
            self.last_modified = 0.0

    mock_files = [
        MockFile("a.txt", "txt", 100),
        MockFile("b.txt", "txt", 200),
        MockFile("c.jpg", "jpg", 500),
    ]

    storage.upsert_files(mock_files)

    stats = storage.get_stats()
    # stats returned as (ext, count, total_size) ordered by count desc
    assert len(stats) == 2

    # txt: 2 files, 300 bytes
    assert stats[0] == ("txt", 2, 300)
    # jpg: 1 file, 500 bytes
    assert stats[1] == ("jpg", 1, 500)


def test_storage_clear(tmp_path):
    db_file = tmp_path / "test_clear.db"
    storage = Storage(str(db_file))
    storage.upsert_files(
        [
            type(
                "obj",
                (object,),
                {"path": "a", "extension": "e", "size_bytes": 1, "last_modified": 0},
            )
        ]
    )
    assert len(storage.get_stats()) == 1

    storage.clear_cache()
    assert len(storage.get_stats()) == 0
