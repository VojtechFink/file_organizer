import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


class DuplicateFinderParallel:
    """Finds duplicate files using multiprocessing for better performance."""

    def __init__(self, hash_algorithm: str = 'md5', num_processes: int = None):
        """
        Initialize DuplicateFinderParallel.

        Args:
            hash_algorithm: Hash algorithm to use ('md5' or 'sha256')
            num_processes: Number of processes to use (None = auto-detect)
        """
        self.hash_algorithm = hash_algorithm
        self.num_processes = num_processes or cpu_count()
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)

    @staticmethod
    def _calculate_hash_worker(args: Tuple[Path, str]) -> Tuple[Path, str]:
        """
        Worker function to calculate hash of a file.
        Must be static for multiprocessing.

        Args:
            args: Tuple of (file_path, hash_algorithm)

        Returns:
            Tuple of (file_path, hash_string)
        """
        file_path, hash_algorithm = args

        try:
            if hash_algorithm == 'md5':
                hash_obj = hashlib.md5()
            elif hash_algorithm == 'sha256':
                hash_obj = hashlib.sha256()
            else:
                raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

            # Read file in chunks to handle large files
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)

            return (file_path, hash_obj.hexdigest())

        except (PermissionError, OSError) as e:
            print(f"Cannot read file {file_path}: {e}")
            return (file_path, None)

    def scan_directory(self, directory: Path, recursive: bool = True,
                       show_progress: bool = True) -> None:
        """
        Scan directory for files and calculate their hashes using multiprocessing.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            show_progress: Whether to show progress bar
        """
        self.file_hashes.clear()

        # Collect all files first
        print(f"Collecting files from: {directory}")
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))

        # Filter only files (not directories)
        files = [f for f in files if f.is_file()]

        if not files:
            print("No files found!")
            return

        print(f"Found {len(files)} files")
        print(f"Using {self.num_processes} CPU cores")

        # Prepare arguments for workers
        args_list = [(file_path, self.hash_algorithm) for file_path in files]

        # Process files in parallel
        with Pool(processes=self.num_processes) as pool:
            if show_progress:
                # With progress bar
                results = list(tqdm(
                    pool.imap(self._calculate_hash_worker, args_list),
                    total=len(files),
                    desc="Hashing files",
                    unit="file"
                ))
            else:
                # Without progress bar
                results = pool.map(self._calculate_hash_worker, args_list)

        # Organize results by hash
        for file_path, file_hash in results:
            if file_hash is not None:
                self.file_hashes[file_hash].append(file_path)

        print(f"Processed {len(results)} files")

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """
        Find all duplicate files.

        Returns:
            Dictionary with hash as key and list of duplicate file paths as value
        """
        return {
            hash_val: paths
            for hash_val, paths in self.file_hashes.items()
            if len(paths) > 1
        }

    def get_duplicate_stats(self) -> Dict[str, any]:
        """
        Get statistics about duplicates.

        Returns:
            Dictionary with statistics
        """
        duplicates = self.find_duplicates()

        total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())
        total_wasted_space = 0

        for paths in duplicates.values():
            file_size = paths[0].stat().st_size
            total_wasted_space += file_size * (len(paths) - 1)

        return {
            'duplicate_groups': len(duplicates),
            'total_duplicate_files': total_duplicates,
            'wasted_space_bytes': total_wasted_space,
            'wasted_space_mb': total_wasted_space / (1024 * 1024),
            'wasted_space_gb': total_wasted_space / (1024 * 1024 * 1024)
        }

    def delete_duplicates(self, keep_first: bool = True, dry_run: bool = False) -> int:
        """
        Delete duplicate files, keeping only one copy.

        Args:
            keep_first: If True, keeps the first file found, deletes others
            dry_run: If True, only simulate deletion without actually deleting

        Returns:
            Number of files deleted (or would be deleted in dry_run mode)
        """
        duplicates = self.find_duplicates()
        deleted_count = 0

        for paths in duplicates.values():
            files_to_delete = paths[1:] if keep_first else paths[:-1]

            for file_path in files_to_delete:
                try:
                    if dry_run:
                        print(f"[DRY RUN] Would delete: {file_path}")
                        deleted_count += 1
                    else:
                        file_path.unlink()
                        deleted_count += 1
                        print(f"Deleted: {file_path}")
                except (PermissionError, OSError) as e:
                    print(f"Cannot delete {file_path}: {e}")

        return deleted_count

    def move_duplicates(self, destination: Path, keep_first: bool = True) -> int:
        """
        Move duplicate files to a destination folder.

        Args:
            destination: Folder to move duplicates to
            keep_first: If True, keeps the first file, moves others

        Returns:
            Number of files moved
        """
        destination.mkdir(parents=True, exist_ok=True)
        duplicates = self.find_duplicates()
        moved_count = 0

        for paths in duplicates.values():
            files_to_move = paths[1:] if keep_first else paths[:-1]

            for file_path in files_to_move:
                try:
                    new_path = destination / file_path.name

                    # Handle name conflicts
                    counter = 1
                    while new_path.exists():
                        new_path = destination / f"{file_path.stem}_{counter}{file_path.suffix}"
                        counter += 1

                    file_path.rename(new_path)
                    moved_count += 1
                    print(f"Moved: {file_path} → {new_path}")
                except (PermissionError, OSError) as e:
                    print(f"Cannot move {file_path}: {e}")

        return moved_count