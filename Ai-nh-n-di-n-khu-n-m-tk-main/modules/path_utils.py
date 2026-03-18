"""
path_utils.py
-------------
Utility functions for handling paths in bundled/frozen applications.
"""

import os
import sys
from pathlib import Path


def is_frozen():
    """Check if running as a PyInstaller bundle."""
    return getattr(sys, 'frozen', False)


def get_bundle_dir():
    """Get the directory containing bundled resources (PyInstaller _MEIPASS)."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


def get_app_dir():
    """Get the application directory (where the exe is located)."""
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def get_models_root():
    """
    Get the root directory for InsightFace models.

    In frozen mode: uses bundled models_data directory
    In normal mode: uses ~/.insightface (default InsightFace location)
    """
    if is_frozen():
        # Use bundled models
        bundle_models = get_bundle_dir() / "models_data"
        if bundle_models.exists():
            return str(bundle_models)

    # Check for local models_data directory
    local_models = get_app_dir() / "models_data"
    if local_models.exists():
        return str(local_models)

    # Fall back to default InsightFace location
    return "~/.insightface"


def get_data_dir():
    """Get the data directory for storing embeddings, index, etc."""
    return get_app_dir() / "data"


def get_index_dir():
    """Get the index directory for FAISS index."""
    return get_app_dir() / "index"


def get_uploads_dir():
    """Get the uploads directory."""
    return get_app_dir() / "uploads"


def get_results_dir():
    """Get the results directory."""
    return get_app_dir() / "results"


def get_logs_dir():
    """Get the logs directory."""
    return get_app_dir() / "logs"


def ensure_directories():
    """Create all required directories if they don't exist."""
    dirs = [
        get_data_dir(),
        get_data_dir() / "embeddings",
        get_index_dir(),
        get_uploads_dir(),
        get_results_dir(),
        get_logs_dir(),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to a resource, works for dev and PyInstaller.

    Parameters
    ----------
    relative_path : str
        Path relative to the application root

    Returns
    -------
    Path
        Absolute path to the resource
    """
    base = get_bundle_dir() if is_frozen() else get_app_dir()
    return base / relative_path


# Initialize directories when module is loaded
ensure_directories()
