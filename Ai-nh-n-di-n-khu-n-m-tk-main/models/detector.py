"""
Wrapper around InsightFace detector with quality checks and alignment helpers.
"""

from __future__ import annotations

import ctypes
import os
import cv2
import numpy as np
import skimage.transform as trans
from insightface.app import FaceAnalysis

from config import FACE_DETECTION_THRESHOLD, FACE_SIZE_MIN
from modules.path_utils import get_models_root

# Standard ArcFace alignment template for 112x112 faces
ARCFACE_SRC = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


def _cuda_runtime_ready() -> bool:
    """Return True only when CUDA runtime DLLs required by ORT are loadable on Windows."""
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
    # Accept either cuDNN 8 or 9 based on local runtime.
    if not _load_dll("cudnn64_9.dll") and not _load_dll("cudnn64_8.dll"):
        return False
    return True


def _select_insightface_providers() -> tuple[list[str], int]:
    """Select providers + ctx_id safely to avoid CUDA spam when runtime libs are missing."""
    force_cpu = os.getenv("INSIGHTFACE_FORCE_CPU", "0") == "1"
    if force_cpu:
        return ["CPUExecutionProvider"], -1
    try:
        import onnxruntime as ort

        has_cuda_ep = "CUDAExecutionProvider" in ort.get_available_providers()
        if has_cuda_ep and _cuda_runtime_ready():
            return ["CUDAExecutionProvider", "CPUExecutionProvider"], 0
    except Exception:
        pass
    return ["CPUExecutionProvider"], -1


class FaceDetector:
    """Detect faces and provide aligned crops suitable for recognition."""

    def __init__(self, det_size: tuple[int, int] = (640, 640), ctx_id: int = -1) -> None:
        providers, auto_ctx = _select_insightface_providers()
        if ctx_id == -1:
            selected_ctx = -1
        elif ctx_id == 0 and auto_ctx == 0:
            selected_ctx = 0
        else:
            selected_ctx = auto_ctx
        if selected_ctx < 0:
            providers = ["CPUExecutionProvider"]
        self.app = FaceAnalysis(name="buffalo_l", root=get_models_root(), providers=providers)
        self.app.prepare(ctx_id=selected_ctx, det_size=det_size, det_thresh=FACE_DETECTION_THRESHOLD)

    def detect(self, image_bgr: np.ndarray) -> list[dict]:
        """
        Detect faces in a BGR image and filter by size/score.

        Returns
        -------
        list of dict with keys:
            - bbox: list[int, int, int, int]
            - kps: np.ndarray shape (5, 2)
            - score: float
            - face_obj: original InsightFace face object (for embeddings)
        """
        faces = self.app.get(image_bgr)
        results: list[dict] = []

        for face in faces:
            x1, y1, x2, y2 = [int(v) for v in face.bbox]
            w, h = x2 - x1, y2 - y1
            if min(w, h) < FACE_SIZE_MIN:
                continue
            if float(face.det_score) < FACE_DETECTION_THRESHOLD:
                continue
            results.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "kps": face.kps.astype(np.float32) if face.kps is not None else None,
                    "score": float(face.det_score),
                    "face_obj": face,
                }
            )

        # Highest confidence first
        results.sort(key=lambda f: f["score"], reverse=True)
        return results

    @staticmethod
    def align(image_bgr: np.ndarray, landmarks: np.ndarray, output_size: int = 112) -> np.ndarray:
        """
        Align a face crop using 5-point landmarks.
        """
        if landmarks is None or landmarks.shape != (5, 2):
            raise ValueError("Cannot align face: invalid landmarks")

        tform = trans.SimilarityTransform()
        tform.estimate(landmarks, ARCFACE_SRC)
        aligned = cv2.warpAffine(
            image_bgr,
            tform.params[0:2, :],
            (output_size, output_size),
            borderValue=0.0,
        )
        return aligned
