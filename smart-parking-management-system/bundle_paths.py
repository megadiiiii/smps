"""
Utility module cho PyInstaller bundled app.
Tu dong phat hien va tra ve duong dan chinh xac cho:
- Models (YOLOv5, InsightFace)
- Data files
- Resources
"""
import os
import sys

def is_frozen():
    """Kiem tra app co dang chay tu PyInstaller bundle khong."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_base_path():
    """
    Tra ve duong dan goc cua app.
    - Neu frozen: _MEIPASS (temp folder chua extracted files)
    - Neu script: thu muc chua file .py
    """
    if is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_app_dir():
    """
    Tra ve thu muc chua file exe (hoac file .py khi dev).
    Dung cho cac file can ghi (database, logs, user data).
    """
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_model_path(relative_path):
    """
    Tra ve duong dan day du toi model file.

    Args:
        relative_path: Duong dan tuong doi, vd: 'model/LP_detector.pt'

    Returns:
        Duong dan tuyet doi toi file
    """
    base = get_base_path()
    return os.path.join(base, relative_path)


def get_yolov5_path():
    """Tra ve duong dan toi thu muc yolov5."""
    return get_model_path('yolov5')


def get_insightface_root():
    """
    Tra ve duong dan root cho InsightFace models.
    InsightFace tim model tai: {root}/models/{model_name}/
    """
    return get_model_path('insightface_models')


def get_face_db_path():
    """Tra ve duong dan toi thu muc face_db (cho embeddings)."""
    # face_db nam trong app dir de co the ghi them
    return os.path.join(get_app_dir(), 'face_db')


def get_result_dir():
    """Tra ve thu muc luu ket qua (screenshots, logs)."""
    result_dir = os.path.join(get_app_dir(), 'result')
    os.makedirs(result_dir, exist_ok=True)
    return result_dir


def setup_paths():
    """
    Cai dat cac environment variables va paths can thiet.
    Goi ham nay o dau file entry point.
    """
    base = get_base_path()

    # Them yolov5 vao sys.path de torch.hub.load hoat dong
    yolov5_path = get_yolov5_path()
    if os.path.isdir(yolov5_path) and yolov5_path not in sys.path:
        sys.path.insert(0, yolov5_path)

    # Dat INSIGHTFACE_HOME de InsightFace tim model dung cho
    insightface_root = get_insightface_root()
    if os.path.isdir(insightface_root):
        os.environ['INSIGHTFACE_HOME'] = insightface_root

    # Tao cac thu muc can thiet
    os.makedirs(get_face_db_path(), exist_ok=True)
    os.makedirs(get_result_dir(), exist_ok=True)

    return base


# Thong tin debug
if __name__ == '__main__':
    print(f"Is frozen: {is_frozen()}")
    print(f"Base path: {get_base_path()}")
    print(f"App dir: {get_app_dir()}")
    print(f"YOLOv5 path: {get_yolov5_path()}")
    print(f"InsightFace root: {get_insightface_root()}")
    print(f"Face DB path: {get_face_db_path()}")
    print(f"Result dir: {get_result_dir()}")
