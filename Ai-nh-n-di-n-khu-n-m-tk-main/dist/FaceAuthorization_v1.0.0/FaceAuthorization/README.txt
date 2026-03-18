# Face Authorization System - Standalone Distribution v1.0.0

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
