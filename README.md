\# 🔍 File Organizer \& Duplicate Finder



Advanced file organization tool with multiprocessing duplicate detection.



\## ✨ Features



\- 📁 \*\*File Organization\*\* - Organize files by type, date, or custom rules

\- 🔍 \*\*Duplicate Detection\*\* - Fast multiprocessing duplicate finder

\- ⚡ \*\*Performance\*\* - Utilizes all CPU cores for maximum speed

\- 📊 \*\*Statistics\*\* - Detailed reports on duplicates and wasted space

\- 🛡️ \*\*Safe Operations\*\* - Dry run mode to preview changes

\- 📈 \*\*Progress Tracking\*\* - Real-time progress bars



\## 🚀 Quick Start



\### Installation



```bash

\# Clone repository

git clone <your-repo-url>

cd file\_organizer



\# Create virtual environment

python -m venv .venv



\# Activate virtual environment

\# Windows:

.venv\\Scripts\\activate

\# Linux/Mac:

source .venv/bin/activate



\# Install dependencies

pip install -r requirements.txt

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

Usage

Find Duplicates (CLI)



&nbsp;   

python duplicate\_finder\_cli.py

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

Features:



⚡ Automatic multiprocessing (uses all CPU cores)

📊 Progress bar during scanning

🔐 Choice of MD5 or SHA256 hashing

🗑️ Delete or move duplicates

🔍 Dry run mode

Benchmark Performance



&nbsp;   

python benchmark\_duplicates.py

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

Compare single-process vs multiprocessing performance.



📊 Example Output

🔍 DUPLICATE FILE FINDER (Multiprocessing)

============================================================

⚡ Using 8 CPU cores for processing



📂 Enter directory path to scan: C:\\MyFiles

🔄 Scan subdirectories? (y/n, default: y): y



🔐 Choose hash algorithm:

1\. MD5 (faster)

2\. SHA256 (more secure)

Your choice (1/2, default: 1): 1

✅ Using MD5



🔍 Scanning: C:\\MyFiles

🔍 Hashing files: 100%|████████████████| 1500/1500 \[00:03<00:00, 450.23file/s]

✅ Processed 1500 files



============================================================

📊 DUPLICATE STATISTICS

============================================================

Duplicate groups:      45

Total duplicate files: 120

Wasted space:          2,450.50 MB

&nbsp;                      2.39 GB

🧪 Testing



&nbsp;   

\# Run all tests

pytest



\# Run with coverage

pytest --cov=src



\# Run specific test file

pytest tests/test\_duplicate\_finder\_parallel.py -v

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

📦 Project Structure

file\_organizer/

├── src/

│   ├── duplicate\_finder.py          # Single-process version

│   ├── duplicate\_finder\_parallel.py # Multiprocessing version

│   └── file\_organizer.py            # File organization

├── tests/

│   ├── test\_duplicate\_finder.py

│   └── test\_duplicate\_finder\_parallel.py

├── duplicate\_finder\_cli.py          # Main CLI

├── benchmark\_duplicates.py          # Performance benchmark

├── requirements.txt

└── README.md

⚙️ Configuration

Number of CPU Cores

By default, uses all available CPU cores. To customize:





&nbsp;   

from src.duplicate\_finder\_parallel import DuplicateFinderParallel



\# Use 4 cores

finder = DuplicateFinderParallel(num\_processes=4)

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

Hash Algorithm

Choose between MD5 (faster) or SHA256 (more secure):





&nbsp;   

finder = DuplicateFinderParallel(hash\_algorithm='sha256')

ⓘ

For code that is intended to be used in Siemens products or services, the code generation features of our AI Services may only be used after prior approval of your responsible organizational unit.

🔒 Safety Features

Dry Run Mode - Preview what would be deleted

Confirmation Required - Must type 'DELETE' to confirm deletion

Keep Original - Always keeps one copy of each file

Error Handling - Graceful handling of permission errors

📈 Performance

Typical speedup with multiprocessing:



Small datasets (< 100 files): 1.5-2x faster

Medium datasets (100-1000 files): 3-4x faster

Large datasets (> 1000 files): 5-8x faster

Results vary based on CPU cores, disk speed, and file sizes.



🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.



📄 License

MIT License - feel free to use in your projects!



🐛 Known Issues

Very large files (> 1GB) may slow down processing

Network drives may have slower performance

Windows: Some system files may be inaccessible

🔮 Future Features

GUI interface

Cloud storage support

Image similarity detection

Scheduled automatic scans

Email reports

📞 Support

For issues or questions, please open an issue on GitHub.



---

