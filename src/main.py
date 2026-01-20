import argparse
import sys
import os
from pathlib import Path
from .scanner import scan_directory
from .storage import Storage
from .operations import copy_files, move_files
import time
from datetime import datetime

# Optional: use tqdm for progress if available, else no-op
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

# Default paths
SCAN_PATH = "/scan"

def get_unique_report_path(report_dir: Path) -> Path:
    """Generate a unique report filename using timestamp."""
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"report-{timestamp}"
    report_path = report_dir / f"{base_name}.txt"
    
    # Ensure uniqueness by appending counter if file exists
    counter = 1
    while report_path.exists():
        report_path = report_dir / f"{base_name}_{counter}.txt"
        counter += 1
    
    return report_path

def main():
    parser = argparse.ArgumentParser(description="File Scanner Service")
    parser.add_argument("--force-cache", action="store_true", help="Use cache only")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")
    parser.add_argument("--action", choices=["report", "move", "copy"], default="report", help="Action to perform")
    parser.add_argument("--type", help="File extension filter (required for move/copy)")
    parser.add_argument("--dest", help="Destination directory (required for move/copy)")
    parser.add_argument("--report", action="store_true", help="Save report to file")
    parser.add_argument("--report-dir", default="/data/reports", help="Directory to save report files")

    args = parser.parse_args()
    
    # Validation
    if args.action in ["move", "copy"]:
        if not args.type:
            parser.error(f"--type is required for {args.action}")
        if not args.dest:
            parser.error(f"--dest is required for {args.action}")

    storage = Storage()
    
    # Determine mode
    should_scan = True
    if args.force_cache:
        should_scan = False
    else:
        # Default behavior: if cache exists/is populated, maybe ask? 
        # But per requirements/simplicity, let's say default is to scan 
        # unless we want to implement a smart check.
        # However, for big folders, auto-scanning might be annoying.
        # Let's assume default is scan, but we can verify later.
        pass

    if should_scan and not args.force_cache:
        print(f"Scanning {SCAN_PATH}...")
        start_time = time.time()
        
        # Batch insert
        # We wrap generator in list if we need to count, but that kills memory.
        # So we pass generator to storage.
        # But to show progress, we might want to wrap it.
        # Since we don't know total, tqdm will just show rate.
        
        scanner_gen = scan_directory(SCAN_PATH)
        # Clear cache before new scan? 
        # If we want to mirror the folder, we probably should clear old entries 
        # or use UPSERT and then maybe cleanup deleted?
        # For this version, let's clear cache on force-scan or fresh scan 
        # to avoid stale entries of deleted files.
        if not args.force_cache:
            print("Clearing cache...")
            storage.clear_cache()
            
        print("Indexing files...")
        storage.upsert_files(tqdm(scanner_gen, unit="files"))
        
        duration = time.time() - start_time
        print(f"Scan completed in {duration:.2f} seconds.")

    # Reporting
    if args.action == "report":
        stats = storage.get_stats()
        
        # Build report content
        lines = []
        lines.append("File Type Report")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Scanned path: {SCAN_PATH}")
        lines.append("")
        lines.append(f"{'Extension':<15} | {'Count':<10} | {'Total Size':<15}")
        lines.append("-" * 46)
        
        total_files = 0
        total_size = 0
        
        for ext, count, size in stats:
            lines.append(f"{ext or 'no_ext':<15} | {count:<10} | {format_size(size):<15}")
            total_files += count
            total_size += size
            
        lines.append("-" * 46)
        lines.append(f"{'TOTAL':<15} | {total_files:<10} | {format_size(total_size):<15}")
        
        report_content = "\n".join(lines)
        
        # Print to stdout
        print("\n" + report_content)
        
        # Save to file only if --report flag is used
        if args.report:
            report_dir = Path(args.report_dir)
            report_path = get_unique_report_path(report_dir)
            report_path.write_text(report_content)
            print(f"\nReport saved to: {report_path}")
        
        # If --type is specified, list all files of that type
        if args.type:
            ext = args.type.lower().lstrip('.')
            files = storage.get_files_by_extension(ext)
            if files:
                print(f"\nFiles with extension '{ext}' ({len(files)} files):")
                print("-" * 60)
                for f in files:
                    print(f)
            else:
                print(f"\nNo files found with extension '{ext}'")

    # Operations
    elif args.action in ["move", "copy"]:
        ext = args.type.lower().lstrip('.')
        files = storage.get_files_by_extension(ext)
        if not files:
            print(f"No files found with extension '{ext}'")
            return

        print(f"Found {len(files)} files of type '{ext}'.")
        print(f"Destination: {args.dest}")
        
        if args.action == "copy":
            copy_files(files, args.dest)
        elif args.action == "move":
            move_files(files, args.dest)
            # Update cache after move?
            # For now, let's recommend rescan.
            print("Note: Cache may be stale after move. Run scanner again to update.")
            
        print("Operation complete.")

if __name__ == "__main__":
    main()

