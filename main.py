from src.file_organizer import FileOrganizer

def main():
    """
        Main function to run the file organizer.
    """
    print("=" * 50)
    print("File Organizer")
    print("=" * 50)

    # Get the source directory from the user
    folder_path = input("\nEnter the path of the directory to organize: ")

    try:
        organizer = FileOrganizer(folder_path)
        print("\nOrganizing files...")
        organizer.organize()
        print("\nFiles organized successfully!")

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
