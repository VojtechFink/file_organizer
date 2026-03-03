import pytest
from pathlib import Path
from src.duplicate_finder import DuplicateFinder


@pytest.fixture
def temp_test_dir(tmp_path):
    """
        Create a temporary directory with test files.
    """

    # Create some duplicate files
    file1 = tmp_path / "file1.txt"
    file1.write_text("Hello World")

    file2 = tmp_path / "file2.txt"
    file2.write_text("Hello World")  # Duplicate of file1

    file3 = tmp_path / "file3.txt"
    file3.write_text("Different content")

    # Create subdirectory with another duplicate
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file4 = subdir / "file4.txt"
    file4.write_text("Hello World")  # Another duplicate

    return tmp_path


def test_calculate_hash(temp_test_dir):
    """Test hash calculation."""
    finder = DuplicateFinder()

    file1 = temp_test_dir / "file1.txt"
    file2 = temp_test_dir / "file2.txt"
    file3 = temp_test_dir / "file3.txt"

    hash1 = finder.calculate_hash(file1)
    hash2 = finder.calculate_hash(file2)
    hash3 = finder.calculate_hash(file3)

    # file1 and file2 should have same hash (same content)
    assert hash1 == hash2
    # file3 should have different hash
    assert hash1 != hash3


def test_scan_directory(temp_test_dir):
    """Test directory scanning."""
    finder = DuplicateFinder()
    finder.scan_directory(temp_test_dir, recursive=True)

    # Should find 4 files total
    total_files = sum(len(paths) for paths in finder.file_hashes.values())
    assert total_files == 4


def test_find_duplicates(temp_test_dir):
    """Test duplicate detection."""
    finder = DuplicateFinder()
    finder.scan_directory(temp_test_dir, recursive=True)

    duplicates = finder.find_duplicates()

    # Should find 1 group of duplicates (3 files with "Hello World")
    assert len(duplicates) == 1

    # That group should contain 3 files
    duplicate_group = list(duplicates.values())[0]
    assert len(duplicate_group) == 3


def test_get_duplicate_stats(temp_test_dir):
    """Test statistics calculation."""
    finder = DuplicateFinder()
    finder.scan_directory(temp_test_dir, recursive=True)

    stats = finder.get_duplicate_stats()

    assert stats['duplicate_groups'] == 1
    assert stats['total_duplicate_files'] == 2  # 3 files, 2 are duplicates
    assert stats['wasted_space_bytes'] > 0


def test_delete_duplicates(temp_test_dir):
    """Test duplicate deletion."""
    finder = DuplicateFinder()
    finder.scan_directory(temp_test_dir, recursive=True)

    deleted = finder.delete_duplicates(keep_first=True)

    # Should delete 2 duplicate files
    assert deleted == 2

    # Should have 2 files remaining
    remaining_files = list(temp_test_dir.rglob('*.txt'))
    assert len(remaining_files) == 2


def test_move_duplicates(temp_test_dir):
    """Test moving duplicates."""
    finder = DuplicateFinder()
    finder.scan_directory(temp_test_dir, recursive=True)

    duplicates_folder = temp_test_dir / "Duplicates"
    moved = finder.move_duplicates(duplicates_folder, keep_first=True)

    # Should move 2 duplicate files
    assert moved == 2

    # Duplicates folder should exist and contain 2 files
    assert duplicates_folder.exists()
    moved_files = list(duplicates_folder.glob('*.txt'))
    assert len(moved_files) == 2


def test_sha256_algorithm(temp_test_dir):
    """Test using SHA256 instead of MD5."""
    finder = DuplicateFinder(hash_algorithm='sha256')

    file1 = temp_test_dir / "file1.txt"
    hash1 = finder.calculate_hash(file1)

    # SHA256 hash should be 64 characters long
    assert len(hash1) == 64