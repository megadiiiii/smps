"""
build.py
--------
Automated build script for Face Authorization System.

This script:
1. Downloads required models
2. Installs dependencies
3. Builds the executable with PyInstaller
4. (Optionally) Creates an installer with Inno Setup

Usage:
    python build.py              # Build executable only
    python build.py --installer  # Build executable + create installer
    python build.py --gpu        # Build with GPU support
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


# Configuration
PROJECT_NAME = "FaceAuthorization"
VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).parent


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(f" {text}")
    print("=" * 60)


def run_command(cmd, cwd=None, env=None):
    """Run a shell command and handle errors."""
    print(f"  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        env=env,
        shell=isinstance(cmd, str),
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  ERROR: Command failed with code {result.returncode}")
        return False
    return True


def check_requirements():
    """Check if required tools are installed."""
    print_header("Checking Requirements")

    # Check Python version
    py_version = sys.version_info
    print(f"  Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        print("  ERROR: Python 3.8+ is required")
        return False

    # Check pip
    try:
        import pip
        print(f"  pip version: {pip.__version__}")
    except ImportError:
        print("  ERROR: pip is not installed")
        return False

    return True


def install_dependencies(gpu=False):
    """Install Python dependencies."""
    print_header("Installing Dependencies")

    # Install PyInstaller first
    if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
        return False

    # Install requirements
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        if not run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]):
            return False

    # Install GPU-specific packages if requested
    if gpu:
        print("  Installing GPU support packages...")
        # Replace faiss-cpu with faiss-gpu
        run_command([sys.executable, "-m", "pip", "uninstall", "-y", "faiss-cpu"])
        run_command([sys.executable, "-m", "pip", "install", "faiss-gpu"])

        # Install onnxruntime-gpu
        run_command([sys.executable, "-m", "pip", "uninstall", "-y", "onnxruntime"])
        run_command([sys.executable, "-m", "pip", "install", "onnxruntime-gpu"])

    return True


def download_models():
    """Download required models."""
    print_header("Downloading Models")

    download_script = PROJECT_ROOT / "download_models.py"
    if download_script.exists():
        return run_command([sys.executable, str(download_script)])
    else:
        print("  WARNING: download_models.py not found, skipping model download")
        return True


def create_directories():
    """Create required directories."""
    print_header("Creating Directories")

    dirs = [
        "models_data",
        "data",
        "data/embeddings",
        "index",
        "uploads",
        "results",
        "logs",
    ]

    for dir_name in dirs:
        dir_path = PROJECT_ROOT / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")

    return True


def build_executable(gpu=False):
    """Build the executable with PyInstaller."""
    print_header("Building Executable")

    spec_file = PROJECT_ROOT / "FaceAuthorization.spec"
    if not spec_file.exists():
        print("  ERROR: FaceAuthorization.spec not found")
        return False

    # Set environment variable for GPU build
    env = os.environ.copy()
    if gpu:
        env["BUILD_GPU"] = "1"

    # Clean previous build
    for cleanup_dir in ["build", "dist"]:
        cleanup_path = PROJECT_ROOT / cleanup_dir
        if cleanup_path.exists():
            shutil.rmtree(cleanup_path)
            print(f"  Cleaned: {cleanup_path}")

    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
    return run_command(cmd, env=env)


def create_installer():
    """Create Windows installer using Inno Setup."""
    print_header("Creating Installer")

    # Check if Inno Setup is installed
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    iscc_path = None
    for path in inno_paths:
        if os.path.exists(path):
            iscc_path = path
            break

    if not iscc_path:
        print("  WARNING: Inno Setup not found. Please install Inno Setup 6")
        print("  Download from: https://jrsoftware.org/isdl.php")
        print("  Skipping installer creation...")
        return True

    iss_file = PROJECT_ROOT / "installer.iss"
    if not iss_file.exists():
        print("  ERROR: installer.iss not found")
        return False

    return run_command([iscc_path, str(iss_file)])


def verify_build():
    """Verify the build was successful."""
    print_header("Verifying Build")

    dist_dir = PROJECT_ROOT / "dist" / PROJECT_NAME
    exe_path = dist_dir / f"{PROJECT_NAME}.exe"

    if not exe_path.exists():
        print(f"  ERROR: Executable not found at {exe_path}")
        return False

    print(f"  Executable found: {exe_path}")
    print(f"  Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")

    # Check for models
    models_dir = dist_dir / "models_data" / "buffalo_l"
    if models_dir.exists():
        model_files = list(models_dir.glob("*.onnx"))
        print(f"  Models found: {len(model_files)} ONNX files")
    else:
        print("  WARNING: Models directory not found in distribution")

    return True


def main():
    parser = argparse.ArgumentParser(description="Build Face Authorization System")
    parser.add_argument("--installer", action="store_true", help="Create installer after build")
    parser.add_argument("--gpu", action="store_true", help="Build with GPU support")
    parser.add_argument("--skip-models", action="store_true", help="Skip model download")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()

    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║      Face Authorization System - Build Script              ║")
    print(f"║      Version: {VERSION:<43}  ║")
    print("╚════════════════════════════════════════════════════════════╝")

    steps = [
        ("Checking requirements", check_requirements),
    ]

    if not args.skip_deps:
        steps.append(("Installing dependencies", lambda: install_dependencies(args.gpu)))

    steps.append(("Creating directories", create_directories))

    if not args.skip_models:
        steps.append(("Downloading models", download_models))

    steps.append(("Building executable", lambda: build_executable(args.gpu)))

    if args.installer:
        steps.append(("Creating installer", create_installer))

    steps.append(("Verifying build", verify_build))

    # Execute steps
    for step_name, step_func in steps:
        if not step_func():
            print()
            print(f"BUILD FAILED at step: {step_name}")
            sys.exit(1)

    print()
    print_header("BUILD COMPLETED SUCCESSFULLY!")
    print()
    print(f"  Executable: {PROJECT_ROOT / 'dist' / PROJECT_NAME / f'{PROJECT_NAME}.exe'}")
    if args.installer:
        print(f"  Installer: {PROJECT_ROOT / 'installer' / f'{PROJECT_NAME}_Setup.exe'}")
    print()


if __name__ == "__main__":
    main()
