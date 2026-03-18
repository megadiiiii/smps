#!/usr/bin/env python
"""
Build embedded distribution for Smart Parking Management System
Includes both smart-parking-management-system and Ai-nh module
Entry point: login.py
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_parking_distribution():
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist" / "SmartParking"

    print("=" * 70)
    print("Smart Parking Management System - Distribution Builder")
    print("=" * 70)
    print()

    # Clean previous dist
    if dist_dir.exists():
        print(f"Removing previous distribution: {dist_dir}")
        shutil.rmtree(dist_dir.parent)

    # Create distribution directory
    print(f"Creating distribution directory: {dist_dir}")
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Copy smart-parking folder
    print("Copying smart-parking-management-system...")
    src = project_root / "smart-parking-management-system"
    dst = dist_dir / "smart-parking-management-system"
    shutil.copytree(src, dst, dirs_exist_ok=True)

    # Copy Ai-nh module folder
    print("Copying Ai-nh face comparison module...")
    src = project_root / "Ai-nh-n-di-n-khu-n-m-tk-main"
    dst = dist_dir / "Ai-nh-n-di-n-khu-n-m-tk-main"
    shutil.copytree(src, dst, dirs_exist_ok=True)

    # Copy launcher script
    print("Copying launcher script...")
    launcher_src = project_root / "run_parking.bat"
    if launcher_src.exists():
        shutil.copy2(launcher_src, dist_dir / "run_parking.bat")

    # Create README
    readme = """# Smart Parking Management System - Standalone Distribution

## Quick Start

### Windows:
1. Double-click `run_parking.bat`
2. Login with credentials (demo: admin/admin)
3. System launches

### Manual:
```bash
python -m pip install -r smart-parking-management-system/requirements.txt
cd smart-parking-management-system
python login.py
```

## What's Included

- **smart-parking-management-system/** - Main parking management application
- **Ai-nh-n-di-n-khu-n-m-tk-main/** - Face comparison module (for face recognition)
- **run_parking.bat** - Windows launcher script

## Requirements

- Python 3.8+
- Windows 10/11 (64-bit)
- 8GB RAM minimum
- Webcam/camera for face detection

## Entry Point

The system starts with `login.py` from smart-parking-management-system folder.
This provides the login UI and full parking management interface.

## Features

- Face recognition at entry/exit
- License plate detection
- Parking space management
- Database logging
- Real-time camera feeds
- Modern GUI interface

## Face Comparison Module

The system uses `Ai-nh-n-di-n-khu-n-m-tk-main/face_comparison.py` for:
- 1:1 face verification
- 1:N face recognition
- Batch face matching
- Similarity scoring

See `Ai-nh-n-di-n-khu-n-m-tk-main/MODULE_README.md` for integration details.

## Troubleshooting

### "Python not found"
Install Python 3.8+ from https://python.org (check "Add python.exe to PATH")

### Models not loading
First run will download AI models (~340MB) - be patient

### Port/Camera issues
Check `smart-parking-management-system/config.py` for settings

## Version

1.0.0 (March 2026)

Embedded Python Distribution Format
"""
    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme)

    # Create data directories
    print("Creating data directories...")
    for folder in ["result/face", "result/plate", "result/fullface", "parking_data", "logs"]:
        (dist_dir / folder).mkdir(parents=True, exist_ok=True)

    # Create ZIP
    print("\nCreating distribution ZIP...")
    zip_path = project_root / f"dist/SmartParking_v1.0.0.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zf.write(file_path, arcname)

    size_mb = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file()) / (1024*1024)

    print()
    print("=" * 70)
    print("Distribution created successfully!")
    print("=" * 70)
    print(f"Location: {dist_dir}")
    print(f"ZIP: {zip_path}")
    print(f"Size: {size_mb:.1f} MB")
    print()
    print("To use:")
    print(f"1. Extract {zip_path.name}")
    print("2. Double-click run_parking.bat")
    print("3. Or: cd smart-parking-management-system && python login.py")
    print()

if __name__ == "__main__":
    create_parking_distribution()
