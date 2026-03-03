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

    def organize_by_type(self, dest_dir: Path = None) -> int:
        """
        Organize files by their type/extension.

        Args:
            dest_dir: Destination directory (default: source_dir)

        Returns:
            Number of files moved
        """
        if dest_dir is None:
            dest_dir = self.source_dir

        moved_count = 0

        for file_path in self.source_dir.rglob('*'):
            if not file_path.is_file():
                continue

            # Get file extension
            extension = file_path.suffix.lower()
            if not extension:
                extension = 'no_extension'
            else:
                extension = extension[1:]  # Remove the dot

            # Create category folder
            category_folder = dest_dir / extension
            category_folder.mkdir(parents=True, exist_ok=True)

            # Move file
            dest_path = category_folder / file_path.name

            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                dest_path = category_folder / f"{stem}_{counter}{file_path.suffix}"
                counter += 1

            try:
                file_path.rename(dest_path)
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path}: {e}")

        return moved_count

    def organize_by_date(self, dest_dir: Path = None, date_format: str = "%Y/%m") -> int:
        """
        Organize files by their creation/modification date.

        Args:
            dest_dir: Destination directory (default: source_dir)
            date_format: Date format for folder structure (default: "%Y/%m")

        Returns:
            Number of files moved
        """
        if dest_dir is None:
            dest_dir = self.source_dir

        moved_count = 0

        for file_path in self.source_dir.rglob('*'):
            if not file_path.is_file():
                continue

            # Get file modification time
            from datetime import datetime
            mtime = file_path.stat().st_mtime
            date_obj = datetime.fromtimestamp(mtime)

            # Create date folder
            date_folder = dest_dir / date_obj.strftime(date_format)
            date_folder.mkdir(parents=True, exist_ok=True)

            # Move file
            dest_path = date_folder / file_path.name

            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                dest_path = date_folder / f"{stem}_{counter}{file_path.suffix}"
                counter += 1

            try:
                file_path.rename(dest_path)
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path}: {e}")

        return moved_count

    def get_statistics(self) -> dict:
        """
        Get statistics about files in the source directory.

        Returns:
            Dictionary with file statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'total_size_mb': 0.0,
            'total_size_gb': 0.0,
            'file_types': {},
            'files_by_type': {},
            'largest_files': [],
            'total_dirs': 0,
            'size_distribution': {
                '< 1 MB': 0,
                '1-10 MB': 0,
                '10-100 MB': 0,
                '100-500 MB': 0,
                '> 500 MB': 0
            }
        }

        all_files = []

        for item in self.source_dir.rglob('*'):
            if item.is_file():
                stats['total_files'] += 1
                file_size = item.stat().st_size
                stats['total_size'] += file_size

                # Track by extension
                ext = item.suffix.lower() or 'no_extension'
                if ext not in stats['file_types']:
                    stats['file_types'][ext] = {'count': 0, 'size': 0}
                stats['file_types'][ext]['count'] += 1
                stats['file_types'][ext]['size'] += file_size

                # Track count by type for files_by_type
                if ext not in stats['files_by_type']:
                    stats['files_by_type'][ext] = 0
                stats['files_by_type'][ext] += 1

                # Size distribution
                size_mb = file_size / (1024 * 1024)
                if size_mb < 1:
                    stats['size_distribution']['< 1 MB'] += 1
                elif size_mb < 10:
                    stats['size_distribution']['1-10 MB'] += 1
                elif size_mb < 100:
                    stats['size_distribution']['10-100 MB'] += 1
                elif size_mb < 500:
                    stats['size_distribution']['100-500 MB'] += 1
                else:
                    stats['size_distribution']['> 500 MB'] += 1

                # Store for largest files
                all_files.append((item, file_size))

            elif item.is_dir():
                stats['total_dirs'] += 1

        # Convert total size to MB and GB
        stats['total_size_mb'] = stats['total_size'] / (1024 * 1024)
        stats['total_size_gb'] = stats['total_size'] / (1024 * 1024 * 1024)

        # Get top 10 largest files
        all_files.sort(key=lambda x: x[1], reverse=True)
        stats['largest_files'] = all_files[:10]

        return stats

    def find_duplicates(self) -> dict:
        """
        Find duplicate files based on MD5 hash.
        Returns dictionary with hash as key and list of duplicate files as value.
        """
        from src.duplicate_finder import DuplicateFinder

        finder = DuplicateFinder()
        finder.scan_directory(self.source_dir, recursive=True)

        # Get duplicates from DuplicateFinder
        duplicates = finder.find_duplicates()

        return duplicates

    def remove_duplicates(self) -> int:
        """
        Remove duplicate files, keeping only the first occurrence.
        Returns number of removed files.
        """
        from src.duplicate_finder import DuplicateFinder

        finder = DuplicateFinder()
        finder.scan_directory(self.source_dir, recursive=True)

        # Delete duplicates and return count
        deleted_count = finder.delete_duplicates(keep_first=True)

        return deleted_count