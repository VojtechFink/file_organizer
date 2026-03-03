"""
Main entry point for File Organizer application.
"""

from pathlib import Path
from src.file_organizer import FileOrganizer
from src.duplicate_finder_parallel import DuplicateFinderParallel


def print_main_menu():
    """Print main menu."""
    print("\n" + "=" * 60)
    print("FILE ORGANIZER & DUPLICATE FINDER")
    print("=" * 60)
    print("1. Organize files by type")
    print("2. Organize files by date")
    print("3. Find and manage duplicates")
    print("4. Show directory statistics")
    print("5. Exit")
    print("=" * 60)


def organize_by_type():
    """Organize files by their type/extension."""
    print("\n" + "=" * 60)
    print("ORGANIZE FILES BY TYPE")
    print("=" * 60)

    source = input("Enter source directory: ").strip()
    if not source:
        print("No directory provided!")
        return

    source_path = Path(source)
    if not source_path.exists():
        print(f"Directory does not exist: {source}")
        return

    dest = input("Enter destination directory (press Enter for same): ").strip()
    dest_path = Path(dest) if dest else source_path

    organizer = FileOrganizer(source_path)

    print(f"\nOrganizing files from {source_path} to {dest_path}...")
    moved = organizer.organize_by_type(dest_path)

    print(f"\nSuccessfully organized {moved} files!")


def organize_by_date():
    """Organize files by their creation/modification date."""
    print("\n" + "=" * 60)
    print("ORGANIZE FILES BY DATE")
    print("=" * 60)

    source = input("Enter source directory: ").strip()
    if not source:
        print("No directory provided!")
        return

    source_path = Path(source)
    if not source_path.exists():
        print(f"Directory does not exist: {source}")
        return

    dest = input("Enter destination directory (press Enter for same): ").strip()
    dest_path = Path(dest) if dest else source_path

    print("\nDate format options:")
    print("1. Year/Month (2024/01)")
    print("2. Year/Month/Day (2024/01/15)")
    print("3. Year only (2024)")

    format_choice = input("Choose format (1-3, default: 1): ").strip() or "1"

    format_map = {
        "1": "%Y/%m",
        "2": "%Y/%m/%d",
        "3": "%Y"
    }

    date_format = format_map.get(format_choice, "%Y/%m")

    organizer = FileOrganizer(source_path)

    print(f"\nOrganizing files by date...")
    moved = organizer.organize_by_date(dest_path, date_format)

    print(f"\nSuccessfully organized {moved} files!")


def find_duplicates():
    """Find and manage duplicate files."""
    print("\n" + "=" * 60)
    print("DUPLICATE FILE FINDER (Multiprocessing)")
    print("=" * 60)

    # Initialize finder with multiprocessing
    finder = DuplicateFinderParallel()
    print(f"⚡ Using {finder.num_processes} CPU cores for processing")

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

    # Hash algorithm
    print("\nChoose hash algorithm:")
    print("1. MD5 (faster)")
    print("2. SHA256 (more secure)")
    algo_choice = input("Your choice (1/2, default: 1): ").strip() or "1"

    if algo_choice == "2":
        finder.hash_algorithm = 'sha256'
        print("Using SHA256")
    else:
        finder.hash_algorithm = 'md5'
        print("Using MD5")

    # Scan directory
    print(f"\n🔍 Scanning: {dir_path}")
    finder.scan_directory(dir_path, recursive=recursive, show_progress=True)

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
    print(f"Duplicate groups:      {stats['duplicate_groups']}")
    print(f"Total duplicate files: {stats['total_duplicate_files']}")
    print(f"Wasted space:          {stats['wasted_space_mb']:.2f} MB")
    print(f"                       {stats['wasted_space_gb']:.2f} GB")

    # Show duplicates
    print("\n" + "=" * 60)
    print("DUPLICATE FILES")
    print("=" * 60)

    show_all = input("\n👀 Show all duplicate files? (y/n, default: n): ").lower() == 'y'

    for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
        print(f"\n🔸 Group {i} ({len(paths)} files):")

        if show_all or i <= 5:
            for path in paths:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"   - {path} ({size_mb:.2f} MB)")
        else:
            # Show only first 2 files
            for path in paths[:2]:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"   - {path} ({size_mb:.2f} MB)")
            print(f"   ... and {len(paths) - 2} more files")

        if not show_all and i >= 5:
            remaining = len(duplicates) - 5
            if remaining > 0:
                print(f"\n... and {remaining} more duplicate groups")
            break

    # Action menu
    while True:
        print("\n" + "=" * 60)
        print(" ACTIONS")
        print("=" * 60)
        print("1. Delete duplicates (keep first)")
        print("2. Move duplicates to folder")
        print("3. Dry run (show what would be deleted)")
        print("4. Show detailed statistics")
        print("5. Back to main menu")

        action = input("\nChoose action (1-5): ").strip()

        if action == "1":
            print("\n WARNING: This will permanently DELETE files!")
            print(f"Files to be deleted: {stats['total_duplicate_files']}")
            print(f"Space to be freed: {stats['wasted_space_mb']:.2f} MB")

            confirm = input("\n Type 'DELETE' to confirm: ")
            if confirm == "DELETE":
                print("\n️ Deleting duplicates...")
                deleted = finder.delete_duplicates(keep_first=True, dry_run=False)
                print(f"\nSuccessfully deleted {deleted} duplicate files")
                print(f"Freed {stats['wasted_space_mb']:.2f} MB of space")
                break
            else:
                print("Cancelled - no files were deleted")

        elif action == "2":
            dest = input("\nEnter destination folder path: ").strip()
            if dest:
                dest_path = Path(dest)
                print(f"\nMoving duplicates to: {dest_path}")
                moved = finder.move_duplicates(dest_path, keep_first=True)
                print(f"\nSuccessfully moved {moved} duplicate files")
                break
            else:
                print("No destination provided")

        elif action == "3":
            print("\nDRY RUN - No files will be deleted")
            print("=" * 60)
            would_delete = finder.delete_duplicates(keep_first=True, dry_run=True)
            print("\n" + "=" * 60)
            print(f"Summary:")
            print(f"   - Would delete: {would_delete} files")
            print(f"   - Would free: {stats['wasted_space_mb']:.2f} MB")
            print("=" * 60)

        elif action == "4":
            print("\n" + "=" * 60)
            print("DETAILED STATISTICS")
            print("=" * 60)
            print(f"Total files scanned:   {sum(len(paths) for paths in finder.file_hashes.values())}")
            print(f"Unique files:          {len(finder.file_hashes)}")
            print(f"Duplicate groups:      {stats['duplicate_groups']}")
            print(f"Total duplicates:      {stats['total_duplicate_files']}")
            print(f"\nWasted space:")
            print(f"  - Bytes:  {stats['wasted_space_bytes']:,}")
            print(f"  - MB:     {stats['wasted_space_mb']:.2f}")
            print(f"  - GB:     {stats['wasted_space_gb']:.4f}")

            # Show largest duplicate groups
            print("\n🔝 Top 5 largest duplicate groups:")
            sorted_duplicates = sorted(
                duplicates.items(),
                key=lambda x: x[1][0].stat().st_size * len(x[1]),
                reverse=True
            )

            for i, (hash_val, paths) in enumerate(sorted_duplicates[:5], 1):
                size_mb = paths[0].stat().st_size / (1024 * 1024)
                total_wasted = size_mb * (len(paths) - 1)
                print(f"   {i}. {len(paths)} files × {size_mb:.2f} MB = {total_wasted:.2f} MB wasted")

        elif action == "5":
            break

        else:
            print("Invalid choice. Please choose 1-5.")


def show_statistics():
    """Show directory statistics."""
    print("\n" + "=" * 60)
    print("DIRECTORY STATISTICS")
    print("=" * 60)

    directory = input("📁 Enter directory path: ").strip()
    if not directory:
        print("No directory provided!")
        return

    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Directory does not exist: {directory}")
        return

    organizer = FileOrganizer(dir_path)
    stats = organizer.get_statistics()

    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(f"Total files:     {stats['total_files']}")
    print(f"Total size:      {stats['total_size_mb']:.2f} MB")
    print(f"                 {stats['total_size_gb']:.2f} GB")

    print("\nFiles by type:")
    for file_type, count in sorted(stats['files_by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {file_type}: {count}")

    print("\nSize distribution:")
    for size_range, count in stats['size_distribution'].items():
        print(f"   {size_range}: {count}")


def main():
    """Main application loop."""
    print("\nWelcome to File Organizer & Duplicate Finder!")

    while True:
        print_main_menu()
        choice = input("\nYour choice (1-5): ").strip()

        if choice == "1":
            organize_by_type()

        elif choice == "2":
            organize_by_date()

        elif choice == "3":
            find_duplicates()

        elif choice == "4":
            show_statistics()

        elif choice == "5":
            print("\nThank you for using File Organizer! Goodbye!")
            break

        else:
            print("\nInvalid choice. Please choose 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()