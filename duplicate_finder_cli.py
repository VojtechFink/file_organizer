from pathlib import Path
from src.file_organizer import FileOrganizer


def main():
    """Interactive duplicate finder CLI."""
    print("=" * 60)
    print("🔍 DUPLICATE FILE FINDER")
    print("=" * 60)

    # Get directory from user
    while True:
        dir_input = input("\nEnter directory path to scan: ").strip()
        source_dir = Path(dir_input)

        if source_dir.exists() and source_dir.is_dir():
            break
        else:
            print("Invalid directory! Please try again.")

    # Create organizer
    organizer = FileOrganizer(source_dir)

    # Show menu
    while True:
        print("\n" + "=" * 60)
        print("What do you want to do?")
        print("=" * 60)
        print("1. Report duplicates (just show them)")
        print("2. Delete duplicates (keep one copy)")
        print("3. Move duplicates to 'Duplicates' folder")
        print("4. Exit")
        print("=" * 60)

        choice = input("\nYour choice (1-4): ").strip()

        if choice == '1':
            organizer.find_and_handle_duplicates(action='report')

        elif choice == '2':
            organizer.find_and_handle_duplicates(action='delete')

        elif choice == '3':
            organizer.find_and_handle_duplicates(action='move')

        elif choice == '4':
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice! Please enter 1-4.")


if __name__ == "__main__":
    main()