import os
import shutil
from pathlib import Path

class FileOrganizer:
    """A class to organize files in a specified directory based on their extensions."""

    def __init__(self, source_dir):
        """
            Inicialize the FileOrganizer with the source directory.
            :param source_dir:
        """

        self.source_dir = Path(source_dir)

    def organize(self):
        """
            Organize files in the source directory into subdirectories based on their extensions.
        """

        if not self.source_dir.exists():
            raise ValueError(f"The directory {self.source_dir} does not exist.")

        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                self._move_file(file_path)

    def _move_file(self, file_path):
        """
            Move a file to a subdirectory based on its extension.
        """
        # get the file extension (like .txt, .jpg, etc.)
        extension = file_path.suffix.lower()

        if not extension:
            extension = 'no_extension'
        else:
            extension = extension[1:]  # Remove the dot from the extension

        # Create the target directory if it doesn't exist
        target_dir = self.source_dir / extension
        target_dir.mkdir(exist_ok=True)

        # Move the file to the target directory
        target_path = target_dir / file_path.name
        shutil.move(str(file_path), str(target_path))
        print(f"Moved {file_path} to {target_path}")
