"""
Runtime hook for Face Authorization System.
This runs before the main application starts.
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Set up environment variables and paths for bundled application."""

    # Determine if running as frozen (PyInstaller bundle)
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = sys._MEIPASS
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running in normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = bundle_dir

    # Set environment variables
    os.environ['BUNDLE_DIR'] = bundle_dir
    os.environ['APP_DIR'] = app_dir

    # Set InsightFace model path to bundled models
    models_dir = os.path.join(bundle_dir, 'models_data')
    if os.path.exists(models_dir):
        # Create symlink or copy to InsightFace cache location
        home = Path.home()
        insightface_cache = home / ".insightface" / "models"

        # Ensure the directory exists
        insightface_cache.mkdir(parents=True, exist_ok=True)

        # Link buffalo_l model
        buffalo_src = Path(models_dir) / "buffalo_l"
        buffalo_dst = insightface_cache / "buffalo_l"

        if buffalo_src.exists() and not buffalo_dst.exists():
            try:
                # Try to create symlink (may require admin on Windows)
                buffalo_dst.symlink_to(buffalo_src)
            except (OSError, NotImplementedError):
                # Fall back to copying
                import shutil
                shutil.copytree(str(buffalo_src), str(buffalo_dst))

    # Set ONNX Runtime to use bundled providers
    os.environ.setdefault('ORT_TENSORRT_DISABLED', '1')

    # Suppress TensorFlow warnings if present
    os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')

    # Set OpenCV headless mode
    os.environ.setdefault('OPENCV_VIDEOIO_PRIORITY_MSMF', '0')

    # Add bundle directory to Python path
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

    # Create required directories in app_dir
    for dir_name in ['uploads', 'results', 'logs', 'data', 'index', 'data/embeddings']:
        dir_path = os.path.join(app_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)


# Run setup when module is loaded
setup_environment()
