"""
download_models.py
------------------
Download all required models before building the executable.
This ensures models are bundled with the installer.
"""

import os
import sys
import zipfile
import shutil
import urllib.request
from pathlib import Path


def get_models_dir():
    """Get the models directory path."""
    # Use local models directory for bundling
    base_dir = Path(__file__).parent
    return base_dir / "models_data"


def download_file(url: str, dest: Path, desc: str = ""):
    """Download a file with progress indicator."""
    print(f"Downloading {desc or url}...")

    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size) if total_size > 0 else 0
        sys.stdout.write(f"\r  Progress: {percent}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest, progress_hook)
    print()


def download_insightface_buffalo_l():
    """Download InsightFace buffalo_l model."""
    models_dir = get_models_dir()
    buffalo_dir = models_dir / "buffalo_l"

    if buffalo_dir.exists() and len(list(buffalo_dir.glob("*.onnx"))) >= 4:
        print("InsightFace buffalo_l model already exists, skipping...")
        return buffalo_dir

    # Create directories
    models_dir.mkdir(parents=True, exist_ok=True)

    # Download URL
    url = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
    zip_path = models_dir / "buffalo_l.zip"

    try:
        download_file(url, zip_path, "InsightFace buffalo_l model")

        # Extract
        print("Extracting buffalo_l.zip...")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(models_dir)

        # Remove zip file
        zip_path.unlink()

        print(f"InsightFace buffalo_l model downloaded to: {buffalo_dir}")
        return buffalo_dir

    except Exception as e:
        print(f"Error downloading InsightFace model: {e}")
        raise


def verify_models():
    """Verify all required models exist."""
    models_dir = get_models_dir()
    buffalo_dir = models_dir / "buffalo_l"

    required_files = [
        "det_10g.onnx",      # Face detection
        "w600k_r50.onnx",    # Face recognition (ArcFace)
        "2d106det.onnx",     # 2D landmarks
        "1k3d68.onnx",       # 3D landmarks
        "genderage.onnx",    # Gender/age detection
    ]

    missing = []
    for f in required_files:
        fpath = buffalo_dir / f
        if not fpath.exists():
            missing.append(f)

    if missing:
        print(f"WARNING: Missing model files: {missing}")
        return False

    print("All InsightFace models verified!")
    return True


def copy_models_to_insightface_cache():
    """Copy models to InsightFace cache for local testing."""
    models_dir = get_models_dir()
    buffalo_dir = models_dir / "buffalo_l"

    # InsightFace default cache location
    home = Path.home()
    insightface_dir = home / ".insightface" / "models" / "buffalo_l"

    if not buffalo_dir.exists():
        print("Local models not found. Run download first.")
        return False

    if insightface_dir.exists():
        print(f"InsightFace cache already exists: {insightface_dir}")
        return True

    print(f"Copying models to InsightFace cache: {insightface_dir}")
    insightface_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(buffalo_dir, insightface_dir)
    print("Models copied to InsightFace cache!")
    return True


def main():
    print("=" * 60)
    print("Model Downloader for Face Authorization System")
    print("=" * 60)
    print()

    # Download InsightFace model
    print("[1/3] Downloading InsightFace buffalo_l model...")
    download_insightface_buffalo_l()
    print()

    # Verify models
    print("[2/3] Verifying models...")
    if not verify_models():
        print("Some models are missing. Please check and re-download.")
        sys.exit(1)
    print()

    # Copy to cache for testing
    print("[3/3] Setting up InsightFace cache...")
    copy_models_to_insightface_cache()
    print()

    print("=" * 60)
    print("All models downloaded and verified successfully!")
    print("You can now build the executable with: python build.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
