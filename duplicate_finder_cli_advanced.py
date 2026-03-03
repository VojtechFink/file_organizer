"""
Advanced CLI for duplicate file finder with multiprocessing support.
"""

from pathlib import Path
from src.duplicate_finder import DuplicateFinder
from src.duplicate_finder_parallel import DuplicateFinderParallel


def print_header():
    """Print CLI header."""
    print("\n" + "=" * 60)
    print("ADVANCED DUPLICATE FILE FINDER")
    print("=" * 60)


def choose_mode():
    """Let user choose between single and multiprocess mode."""
    print("\n⚡ Choose processing mode:")
    print("1. Single process (slower, less CPU usage)")
    print("2. Multiprocess (faster, uses all CPU cores)")

    choice = input("\nYour choice (1/2, default: 2): ").strip() or "2"

    if choice == "1":
        return DuplicateFinder(), "Single Process"
    else:
        return DuplicateFinderParallel(), "Multiprocess"


def main():
    """Main CLI function."""
    print_header()

    # Choose mode
    finder, mode_name = choose_mode()
    print(f"Using: {mode_name}")

    # Get directory
    directory = input("\nEnter directory path to scan: ").strip()

    if not directory:
        print("No directory provided!")
        return

    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Directory does not exist: {directory}")
        return

    # Scan options
    recursive = input("Scan subdirectories? (y/n, default: y): ").lower() != 'n'

    # Scan directory
    print(f"\nScanning: {dir_path}")

    if isinstance(finder, DuplicateFinderParallel):
        finder.scan_directory(dir_path, recursive=recursive, show_progress=True)
    else:
        finder.scan_directory(dir_path, recursive=recursive)

    # Find duplicates
    duplicates = finder.find_duplicates()

    if not duplicates:
        print("\nNo duplicates found!")
        return

    # Show statistics
    stats = finder.get_duplicate_stats()

    print("\n" + "=" * 60)
    print("DUPLICATE STATISTICS")
    print("=" * 60)
    print(f"Duplicate groups:     {stats['duplicate_groups']}")
    print(f"Total duplicate files: {stats['total_duplicate_files']}")
    print(f"Wasted space:         {stats['wasted_space_mb']:.2f} MB")
    print(f"                      {stats['wasted_space_gb']:.2f} GB")

    # Show duplicates
    print("\n" + "=" * 60)
    print("DUPLICATE FILES")
    print("=" * 60)

    for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
        print(f"\n🔸 Group {i} ({len(paths)} files):")
        for path in paths:
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"   - {path} ({size_mb:.2f} MB)")

    # Action menu
    print("\n" + "=" * 60)
    print("ACTIONS")
    print("=" * 60)
    print("1. Delete duplicates (keep first)")
    print("2. Move duplicates to folder")
    print("3. Dry run (show what would be deleted)")
    print("4. Exit")

    action = input("\nChoose action (1-4): ").strip()

    if action == "1":
        confirm = input("Are you sure? This will DELETE files! (yes/no): ")
        if confirm.lower() == "yes":
            deleted = finder.delete_duplicates(keep_first=True)
            print(f"\nDeleted {deleted} duplicate files")
        else:
            print("Cancelled")

    elif action == "2":
        dest = input("Enter destination folder: ").strip()
        if dest:
            moved = finder.move_duplicates(Path(dest), keep_first=True)
            print(f"\nMoved {moved} duplicate files to {dest}")

    elif action == "3":
        if isinstance(finder, DuplicateFinderParallel):
            would_delete = finder.delete_duplicates(keep_first=True, dry_run=True)
            print(f"\nWould delete {would_delete} files")
        else:
            print("Dry run only available in multiprocess mode")

    else:
        print("Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
