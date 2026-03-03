"""
Benchmark script to compare performance of single vs multiprocessing duplicate finder.
"""

import time
from pathlib import Path
from src.duplicate_finder import DuplicateFinder
from src.duplicate_finder_parallel import DuplicateFinderParallel


def create_test_files(directory: Path, num_files: int = 100):
    """
    Create test files for benchmarking.

    Args:
        directory: Directory to create files in
        num_files: Number of files to create
    """
    directory.mkdir(parents=True, exist_ok=True)

    print(f"Creating {num_files} test files...")

    # Create files with some duplicates
    for i in range(num_files):
        file_path = directory / f"file_{i}.txt"

        # Every 3rd file is a duplicate
        if i % 3 == 0:
            content = "Duplicate content A" * 1000
        elif i % 3 == 1:
            content = "Duplicate content B" * 1000
        else:
            content = f"Unique content {i}" * 1000

        file_path.write_text(content)

    print(f"Created {num_files} files in {directory}")


def benchmark_single_process(directory: Path):
    """Benchmark single-process duplicate finder."""
    print("\n" + "=" * 60)
    print("SINGLE PROCESS BENCHMARK")
    print("=" * 60)

    finder = DuplicateFinder()

    start_time = time.time()
    finder.scan_directory(directory, recursive=True)
    duplicates = finder.find_duplicates()
    end_time = time.time()

    elapsed = end_time - start_time

    print(f"\n️  Time: {elapsed:.2f} seconds")
    print(f"Found {len(duplicates)} duplicate groups")

    stats = finder.get_duplicate_stats()
    print(f"Wasted space: {stats['wasted_space_mb']:.2f} MB")

    return elapsed


def benchmark_multiprocess(directory: Path, num_processes: int = None):
    """Benchmark multiprocess duplicate finder."""
    print("\n" + "=" * 60)
    print(f"⚡ MULTIPROCESS BENCHMARK ({num_processes or 'auto'} cores)")
    print("=" * 60)

    finder = DuplicateFinderParallel(num_processes=num_processes)

    start_time = time.time()
    finder.scan_directory(directory, recursive=True, show_progress=True)
    duplicates = finder.find_duplicates()
    end_time = time.time()

    elapsed = end_time - start_time

    print(f"\n️  Time: {elapsed:.2f} seconds")
    print(f"Found {len(duplicates)} duplicate groups")

    stats = finder.get_duplicate_stats()
    print(f"Wasted space: {stats['wasted_space_mb']:.2f} MB")

    return elapsed


def main():
    """Run benchmarks."""
    print("DUPLICATE FINDER BENCHMARK")
    print("=" * 60)

    # Create test directory
    test_dir = Path("benchmark_test_files")

    # Ask user for number of files
    try:
        num_files = int(input("\nHow many test files to create? (default: 100): ") or "100")
    except ValueError:
        num_files = 100

    # Create test files
    create_test_files(test_dir, num_files)

    # Run benchmarks
    time_single = benchmark_single_process(test_dir)
    time_multi = benchmark_multiprocess(test_dir)

    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Single process:  {time_single:.2f}s")
    print(f"Multiprocess:    {time_multi:.2f}s")

    if time_multi < time_single:
        speedup = time_single / time_multi
        print(f"\nSpeedup: {speedup:.2f}x faster with multiprocessing!")
    else:
        print(f"\nSingle process was faster (small dataset)")

    # Cleanup
    cleanup = input("\nDelete test files? (y/n): ").lower()
    if cleanup == 'y':
        import shutil
        shutil.rmtree(test_dir)
        print("Test files deleted")
    else:
        print(f"Test files kept in: {test_dir}")


if __name__ == "__main__":
    main()