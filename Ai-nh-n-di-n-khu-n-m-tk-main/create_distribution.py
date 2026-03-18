#!/usr/bin/env python
"""
Distribution builder for Face Authorization System
Creates a standalone distribution package
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_dist():
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist" / "FaceAuthorization"

    if dist_dir.exists():
        shutil.rmtree(dist_dir.parent)

    dist_dir.mkdir(parents=True, exist_ok=True)

    print("Creating distribution...")

    # Copy files
    files = ['app.py', 'config.py', 'requirements.txt', 'run_app.bat', 'BUILD_GUIDE.md', 'download_models.py']
    for f in files:
        src = project_root / f
        if src.exists():
            shutil.copy2(src, dist_dir / f)

    # Copy directories
    for d in ['templates', 'static', 'modules', 'services', 'models_data']:
        src = project_root / d
        if src.exists():
            shutil.copytree(src, dist_dir / d)

    # Create data dirs
    for d in ['data', 'data/embeddings', 'index', 'logs', 'uploads', 'results']:
        (dist_dir / d).mkdir(parents=True, exist_ok=True)

    # Create README
    readme = """# Face Authorization System - Standalone Distribution v1.0.0

## Requirements
- Windows 10/11 (64-bit)
- Python 3.8+ (must be installed separately)
- 8GB RAM recommended
- ~4GB disk space free

## Quick Start
1. Ensure Python is installed and in PATH
2. Double-click `run_app.bat`
3. App launches at http://localhost:5000
4. Models download automatically on first run (~340MB)

## Manual Setup
```bash
python -m pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## Structure
- app.py: Flask application
- modules/: Face detection/recognition modules
- services/: Background services
- templates/: Web UI
- static/: Assets
- models_data/: AI models (downloaded on first run)
- data/: User embeddings

## Features
- 1:1 face verification
- 1:N face recognition
- Web-based interface
- Real-time processing
"""
    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme)

    # ZIP it
    zip_path = project_root / "dist/FaceAuthorization_v1.0.0.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zf.write(file_path, arcname)

    size_mb = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file()) / (1024*1024)

    print()
    print("=" * 60)
    print("Distribution created successfully!")
    print("=" * 60)
    print(f"Location: {dist_dir}")
    print(f"ZIP: {zip_path}")
    print(f"Size: {size_mb:.1f} MB")
    print()

if __name__ == "__main__":
    create_dist()
