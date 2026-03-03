import pytest
import os
from pathlib import Path
from src.file_organizer import FileOrganizer

@pytest.fixture
def temp_dir(tmp_path):
    # Create a temporary directory and some test files
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    return test_dir

def test_organize_files(temp_dir):
    """
        Test the organize method of the FileOrganizer class.
        :param temp_dir:
        :return:
    """
    # Create some test files with different extensions
    (temp_dir / "document.txt").touch()
    (temp_dir / "picture.jpg").touch()
    (temp_dir / "video.mp4").touch()
    (temp_dir / "document2.txt").touch()

    # Start organizing the files
    organizer = FileOrganizer(temp_dir)
    organizer.organize()

    # Check if folders for each extension are created
    assert (temp_dir / "txt").exists()
    assert (temp_dir / "jpg").exists()
    assert (temp_dir / "mp4").exists()

    # Check if files are moved to the correct folders
    assert (temp_dir / "txt" / "document.txt").exists()
    assert (temp_dir / "txt" / "document2.txt").exists()
    assert (temp_dir / "jpg" / "picture.jpg").exists()
    assert (temp_dir / "mp4" / "video.mp4").exists()

