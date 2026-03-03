import hashlib
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

class DuplicateFinder:
    """
        Finds duplicate files based on their content (hash).
    """

    def __init__(self, hash_algorithm: str = 'md5'):
        """
            Initialize DuplicateFinder.
            :param hash_algorithm: Hash algorithm to use (default: 'md5').
        """

        self.hash_algorithm = hash_algorithm
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)

    def calculate_hash(self, file_path: Path) -> str:
        """
            Calculate the hash of a file.
            :param file_path: Path to the file.
            :return: Hash string.
        """

        if self.hash_algorithm == 'md5':
            hash_obj = hashlib.md5()
        elif self.hash_algorithm == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

        # Read file in chunks to handle large files
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def scan_directory(self, directory: Path, recursive: bool = True) -> None:
        """
            Scan a directory for duplicate files.
            :param directory: Path to the directory to scan.
            :param recursive: Whether to scan subdirectories (default: True).
        """

        self.file_hashes.clear()

        if recursive:
            files = directory.rglob('*')
        else:
            files = directory.glob('*')

        for file_path in files:
            if file_path.is_file():
                try:
                    file_hash = self.calculate_hash(file_path)
                    self.file_hashes[file_hash].append(file_path)
                except (PermissionError, OSError) as e:
                    print(f"Cannot read file {file_path}: {e}")

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """
            Find duplicate files based on their hashes.
            :return: Dictionary with hash as key and list of duplicate file paths as value.
        """

        # return only hashes that have more than one file
        return {
            hash_val: paths
            for hash_val, paths in self.file_hashes.items()
            if len(paths) > 1
        }

    def get_duplicate_stats(self) -> Dict[str, any]:
        """
            Get statistics about duplicate files.
            :return: Dictionary with statistics.
        """

        duplicates = self.find_duplicates()

        total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())
        total_wasted_space = 0

        for paths in duplicates.values():
            # Keep one original, count others as wasted space
            file_size = paths[0].stat().st_size
            total_wasted_space += file_size * (len(paths) - 1)

        return {
            'duplicate_groups': len(duplicates),
            'total_duplicate_files': total_duplicates,
            'wasted_space_bytes': total_wasted_space,
            'wasted_space_mb': total_wasted_space / (1024 * 1024)
        }

    def delete_duplicates(self, keep_first: bool = True) -> int:
        """
            Delete duplicate files, keeping one original.
            :param keep_first: Whether to keep the first file in each duplicate group (default: True).
            :return: Number of deleted files.
        """

        duplicates = self.find_duplicates()
        deleted_count = 0

        for paths in duplicates.values():
            # Keep the first file, delete the rest
            files_to_delete = paths[1:] if keep_first else paths[:-1]

            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"Deleted duplicate file: {file_path}")
                except (PermissionError, OSError) as e:
                    print(f"Cannot delete file {file_path}: {e}")

        return deleted_count

    def move_duplicates(self, destination: Path, keep_first: bool = True) -> int:
        """
            Move duplicate files to a specified destination, keeping one original.
            :param destination: Path to the destination directory.
            :param keep_first: Whether to keep the first file in each duplicate group (default: True).
            :return: Number of moved files.
        """

        duplicates = self.find_duplicates()
        moved_count = 0

        for paths in duplicates.values():
            """
                Keep the first file, move the rest to the destination directory.
                :param destination: Path to the destination directory.
                :param keep_first: Whether to keep the first file in each duplicate group (default: True).
                :return: Number of moved files.
            """

            destination.mkdir(parents=True, exist_ok=True)
            duplicates = self.find_duplicates()
            moved_count = 0

            for paths in duplicates.values():
                files_to_move = paths[1:] if keep_first else paths[:-1]

                for file_path in files_to_move:
                    try:
                        new_path = destination / file_path.name

                        counter = 1
                        while new_path.exists():
                            new_path = destination / f"{file_path.stem}_{counter}{file_path.suffix}"
                            counter += 1

                        file_path.rename(new_path)
                        moved_count += 1
                        print(f"Moved duplicate file: {file_path} to {new_path}")
                    except (PermissionError, OSError) as e:
                        print(f"Cannot move file {file_path}: {e}")

        return moved_count