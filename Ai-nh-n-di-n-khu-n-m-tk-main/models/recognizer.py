"""
Face embedding generator built on InsightFace ArcFace.
"""

from __future__ import annotations

import ctypes
import os
import numpy as np
from insightface.app import FaceAnalysis

from config import EMBEDDING_DIM
from models.detector import FaceDetector
from modules.path_utils import get_models_root


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


def _select_insightface_providers() -> tuple[list[str], int]:
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


class FaceRecognizer:
    """Compute L2-normalised face embeddings."""

    def __init__(self, ctx_id: int = -1) -> None:
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
        self.app.prepare(ctx_id=selected_ctx, det_size=(640, 640))

    def embed(
        self,
        image_bgr: np.ndarray,
        face_obj=None,
        landmarks: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        Generate an embedding for a face image.

        Priority:
        1) Use precomputed normed_embedding from provided face_obj (fast path).
        2) If landmarks are provided, align then embed.
        3) Fallback: run detection internally and embed the best face.
        """
        if face_obj is not None and getattr(face_obj, "normed_embedding", None) is not None:
            emb = face_obj.normed_embedding
            return self._normalize(emb)

        if landmarks is not None:
            aligned = FaceDetector.align(image_bgr, landmarks)
            faces = self.app.get(aligned)
            if not faces:
                raise ValueError("No face found during alignment embedding.")
            emb = faces[0].normed_embedding
            return self._normalize(emb)

        faces = self.app.get(image_bgr)
        if not faces:
            raise ValueError("No face detected for embedding.")
        emb = faces[0].normed_embedding
        return self._normalize(emb)

    @staticmethod
    def _normalize(embedding: np.ndarray) -> np.ndarray:
        """L2-normalise embedding to ensure unit length for cosine/IP search."""
        vec = embedding.astype(np.float32)
        norm = np.linalg.norm(vec) + 1e-10
        vec = vec / norm
        # Ensure expected dimensionality for FAISS
        if vec.shape[0] != EMBEDDING_DIM:
            raise ValueError(f"Unexpected embedding dim {vec.shape[0]}, expected {EMBEDDING_DIM}")
        return vec
