"""
face_embedder.py
----------------
Generate a normalised 512-dimensional face embedding using InsightFace.
"""

import ctypes
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import skimage.transform as trans

from modules.path_utils import get_models_root


# Reuse the same model app used by face_detector if already loaded
_app = None

# Standard face alignment template for 112x112 face
ARCFACE_SRC = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041]
], dtype=np.float32)


def normalize_lighting(image_bgr: np.ndarray) -> np.ndarray:
    """
    Normalize lighting conditions to improve embedding consistency.
    
    Parameters
    ----------
    image_bgr : np.ndarray
        Input BGR image
    
    Returns
    -------
    np.ndarray
        Lighting-normalized BGR image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply moderate CLAHE for better normalization
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_equalized = clahe.apply(l)
    
    # Blend with original (30% original, 70% equalized) for stronger effect
    l_blended = cv2.addWeighted(l, 0.5, l_equalized, 0.5, 0)
    
    # Merge channels back
    lab_equalized = cv2.merge([l_blended, a, b])
    
    # Convert back to BGR
    normalized = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)
    
    return normalized


def _get_ctx_id() -> int:
    """Trả về 0 (GPU) nếu onnxruntime-gpu + CUDA khả dụng, ngược lại -1 (CPU)."""
    force_cpu = os.getenv("INSIGHTFACE_FORCE_CPU", "0") == "1"
    if force_cpu:
        return -1
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers and _cuda_runtime_ready():
            return 0
    except Exception:
        pass
    return -1


def _cuda_runtime_ready() -> bool:
    if os.name != "nt":
        return True
    capi_dir = ""
    try:
        import onnxruntime as ort
        capi_dir = os.path.join(os.path.dirname(ort.__file__), "capi")
    except Exception:
        capi_dir = ""

    def _load_dll(name: str) -> bool:
        try:
            if capi_dir:
                full = os.path.join(capi_dir, name)
                if os.path.isfile(full):
                    ctypes.WinDLL(full)
                    return True
            ctypes.WinDLL(name)
            return True
        except OSError:
            return False

    required = ("cublasLt64_12.dll", "cublas64_12.dll")
    for dll in required:
        if not _load_dll(dll):
            return False
    if not _load_dll("cudnn64_9.dll") and not _load_dll("cudnn64_8.dll"):
        return False
    return True


def _get_app():
    global _app
    if _app is None:
        ctx = _get_ctx_id()
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if ctx >= 0 else ["CPUExecutionProvider"]
        models_root = get_models_root()
        _app = FaceAnalysis(
            name="buffalo_l",
            root=models_root,
            providers=providers,
        )
        # Lower detection threshold for better sensitivity
        _app.prepare(ctx_id=ctx, det_size=(640, 640), det_thresh=0.3)
    return _app


def align_face(image_bgr: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
    """
    Align face to a standard template using 5-point landmarks.
    This helps normalize pose/angle variations.
    
    Parameters
    ----------
    image_bgr : np.ndarray
        Input face image
    landmarks : np.ndarray
        5 facial landmarks (left_eye, right_eye, nose, left_mouth, right_mouth)
    
    Returns
    -------
    np.ndarray
        Aligned face image (112x112)
    """
    tform = trans.SimilarityTransform()
    tform.estimate(landmarks, ARCFACE_SRC)
    aligned = cv2.warpAffine(
        image_bgr,
        tform.params[0:2, :],
        (112, 112),
        borderValue=0.0
    )
    return aligned


def get_embedding(image_bgr: np.ndarray, fast_mode: bool = False) -> np.ndarray:
    """
    Generate a normalised face embedding from a cropped face image.

    Parameters
    ----------
    image_bgr : np.ndarray
        BGR image (e.g. from cv2.imread or the output of face_detector).
        Should already be cropped to a single face, but detection is run
        again to extract the embedding vector properly.
    fast_mode : bool
        If True, skip some preprocessing steps for faster embedding.
        Use for image 2 to get results quickly. Default False.

    Returns
    -------
    np.ndarray
        Normalised 512-dimensional embedding vector.

    Raises
    ------
    ValueError
        If no face is found in the provided crop.
    """
    app = _get_app()
    h, w = image_bgr.shape[:2]
    
    # Strategy 1: Ensure minimum size for better detection
    working_img = image_bgr
    if h < 160 or w < 160:
        target_size = 256
        working_img = cv2.resize(image_bgr, (target_size, target_size))
    
    faces = app.get(working_img)

    # Fallback 1: Try with even larger size
    if len(faces) == 0:
        large = cv2.resize(image_bgr, (320, 320))
        faces = app.get(large)
    
    # Fallback 2: Try with lower threshold
    if len(faces) == 0:
        temp_app = FaceAnalysis(name="buffalo_l", root=get_models_root(), providers=["CPUExecutionProvider"])
        temp_app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.2)
        faces = temp_app.get(working_img)
    
    # Fallback 3: Try with lighting normalization
    if len(faces) == 0:
        normalized = normalize_lighting(image_bgr)
        if h < 160 or w < 160:
            normalized = cv2.resize(normalized, (256, 256))
        faces = app.get(normalized)
    
    # Fallback 4: Ultra-low threshold
    if len(faces) == 0:
        temp_app = FaceAnalysis(name="buffalo_l", root=get_models_root(), providers=["CPUExecutionProvider"])
        temp_app.prepare(ctx_id=-1, det_size=(320, 320), det_thresh=0.1)
        faces = temp_app.get(working_img)

    if len(faces) == 0:
        raise ValueError("Could not generate embedding: no face found in cropped region.")

    # Use the first (or largest) face
    if len(faces) > 1:
        faces = sorted(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
            reverse=True,
        )

    face = faces[0]
    
    # Use embedding directly from the model
    embedding = face.normed_embedding
    
    return embedding.astype(np.float32)
