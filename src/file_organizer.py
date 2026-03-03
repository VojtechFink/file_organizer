import os
import shutil
from pathlib import Path
from src.duplicate_finder import DuplicateFinder

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

    def find_and_handle_duplicates(self, action: str = 'report') -> None:
        """
        Find and handle duplicate files.

        Args:
            action: What to do with duplicates:
                   'report' - just show them
                   'delete' - delete duplicates
                   'move' - move to Duplicates folder
        """
        print(f"\nScanning for duplicates in: {self.source_dir}")

        finder = DuplicateFinder()
        finder.scan_directory(self.source_dir, recursive=True)

        duplicates = finder.find_duplicates()

        if not duplicates:
            print("No duplicates found!")
            return

        # Show statistics
        stats = finder.get_duplicate_stats()
        print(f"\nDuplicate Statistics:")
        print(f"   • Duplicate groups: {stats['duplicate_groups']}")
        print(f"   • Total duplicate files: {stats['total_duplicate_files']}")
        print(f"   • Wasted space: {stats['wasted_space_mb']:.2f} MB")

        # Show duplicates
        print(f"\nFound {len(duplicates)} group(s) of duplicates:\n")
        for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
            print(f"Group {i} ({len(paths)} files):")
            for path in paths:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"   • {path} ({size_mb:.2f} MB)")
            print()

        # Handle based on action
        if action == 'delete':
            confirm = input("Delete duplicates? (yes/no): ").lower()
            if confirm == 'yes':
                deleted = finder.delete_duplicates(keep_first=True)
                print(f"Deleted {deleted} duplicate files!")
            else:
                print("Deletion cancelled.")

        elif action == 'move':
            duplicates_folder = self.source_dir / "Duplicates"
            confirm = input(f"Move duplicates to {duplicates_folder}? (yes/no): ").lower()
            if confirm == 'yes':
                moved = finder.move_duplicates(duplicates_folder, keep_first=True)
                print(f"Moved {moved} duplicate files!")
            else:
                print("Move cancelled.")
