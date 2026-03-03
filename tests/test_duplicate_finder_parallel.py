import pytest
from pathlib import Path
from src.duplicate_finder_parallel import DuplicateFinderParallel


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory with test files."""
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


def test_parallel_scan_directory(temp_test_dir):
    """Test parallel directory scanning."""
    finder = DuplicateFinderParallel(num_processes=2)
    finder.scan_directory(temp_test_dir, recursive=True, show_progress=False)

    # Should find 4 files total
    total_files = sum(len(paths) for paths in finder.file_hashes.values())
    assert total_files == 4


def test_parallel_find_duplicates(temp_test_dir):
    """Test parallel duplicate detection."""
    finder = DuplicateFinderParallel(num_processes=2)
    finder.scan_directory(temp_test_dir, recursive=True, show_progress=False)

    duplicates = finder.find_duplicates()

    # Should find 1 group of duplicates
    assert len(duplicates) == 1

    # That group should contain 3 files
    duplicate_group = list(duplicates.values())[0]
    assert len(duplicate_group) == 3


def test_parallel_stats(temp_test_dir):
    """Test statistics with parallel processing."""
    finder = DuplicateFinderParallel(num_processes=2)
    finder.scan_directory(temp_test_dir, recursive=True, show_progress=False)

    stats = finder.get_duplicate_stats()

    assert stats['duplicate_groups'] == 1
    assert stats['total_duplicate_files'] == 2
    assert stats['wasted_space_bytes'] > 0


def test_dry_run_delete(temp_test_dir):
    """Test dry run deletion."""
    finder = DuplicateFinderParallel(num_processes=2)
    finder.scan_directory(temp_test_dir, recursive=True, show_progress=False)

    # Dry run should not actually delete files
    deleted = finder.delete_duplicates(keep_first=True, dry_run=True)

    # Should report 2 files would be deleted
    assert deleted == 2

    # But files should still exist
    remaining_files = list(temp_test_dir.rglob('*.txt'))
    assert len(remaining_files) == 4