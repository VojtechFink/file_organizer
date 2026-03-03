📁 File Organizer



Automatic file organizer by extension - Python project for organizing files in folders.



📋 Description



File Organizer is a Python application that automatically organizes files in a folder based on their extensions. The program creates subfolders for each file type and moves files into the corresponding folders.



✨ Features



✅ Automatic file type detection by extension

✅ Creation of subfolders based on extensions

✅ Moving files to corresponding folders

✅ Error handling and input validation

✅ Complete test coverage (91%)



🚀 Installation



Requirements



Python 3.7 or newer

pip (package manager)



\### Installation Steps



1. Clone the repository

git clone https://github.com/VojtechFink/file_organizer.git

cd file\_organizer

2. Install dependencies

pip install -r requirements.txt

Example
====================================================
FILE ORGANIZER - File Organization Tool
====================================================

Enter the path to the folder you want to organize: C:\Users\User\Downloads

Starting file organization...
✅ Organization completed!

Usage in Code

    
from src.file_organizer import FileOrganizer

# Create organizer instance
organizer = FileOrganizer("/path/to/folder")

# Run organization
organizer.organize()

🧪 Testing
Running Tests

    
pytest tests/ -v
ⓘ
For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.
Running Tests with Coverage

    
pytest tests/ --cov=src --cov-report=term-missing
ⓘ
For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.
Expected Output
collected 2 items

tests/test_file_organizer.py::test_organize_files PASSED
tests/test_file_organizer.py::test_nonexistent_directory PASSED

====== 2 passed in 0.XX s ======
📁 Project Structure
file_organizer/
├── src/
│   ├── __init__.py
│   └── file_organizer.py      # Main logic
├── tests/
│   ├── __init__.py
│   └── test_file_organizer.py # Tests
├── .venv/                      # Virtual environment
├── .gitignore                  # Git ignore file
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
└── main.py                     # Entry point
🔧 Technologies
Python 3.11 - Programming language
pytest - Testing framework
pytest-cov - Code coverage
pathlib - Path operations
shutil - File operations
📝 Organization Example
Before:

Downloads/
├── document.txt
├── image.jpg
├── video.mp4
├── presentation.pdf
└── another_document.txt
After:

Downloads/
├── txt/
│   ├── document.txt
│   └── another_document.txt
├── jpg/
│   └── image.jpg
├── mp4/
│   └── video.mp4
└── pdf/
    └── presentation.pdf
⚠️ Warnings
The program moves files, not copies them
Make sure you have a backup of important data
The program ignores hidden files and folders
Only files are organized, not folders
🐛 Troubleshooting
Error: "Directory does not exist"
Check that the folder path is correct
Make sure the folder exists
Error: "Permission denied"
Check that you have write permissions to the folder
Close all files in the folder
🤝 Contributing
Contributions are welcome! If you want to contribute:

Fork the repository
Create a new branch (git checkout -b feature/new-feature)
Commit your changes (git commit -m 'Add new feature')
Push to the branch (git push origin feature/new-feature)
Create a Pull Request
📄 License
This project is open-source and available under the MIT License.

👤 Author
Created as an educational project for learning Python.
Vojtěch Fink

📧 Contact
Have questions or suggestions? Feel free to reach out!
vojtechfink11@gmail.com
