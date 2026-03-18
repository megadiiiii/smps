# face_engine.py (GPU-optimized với FAISS)
import os
import sys
import time
import logging
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from faiss_index import FaissIndex

# Import bundle_paths de ho tro PyInstaller
try:
    from bundle_paths import get_face_db_path, get_insightface_root, is_frozen
except ImportError:
    def get_face_db_path():
        return "face_db"
    def get_insightface_root():
        return os.path.expanduser("~/.insightface")
    def is_frozen():
        return getattr(sys, 'frozen', False)

log = logging.getLogger(__name__)

DB_DIR = get_face_db_path()
SIM_THRESHOLD = 0.5

# Auto-detect ONNX provider
try:
    import onnxruntime as _ort
    _PROVIDERS = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if "CUDAExecutionProvider" in _ort.get_available_providers()
        else ["CPUExecutionProvider"]
    )
except Exception:
    _PROVIDERS = ["CPUExecutionProvider"]


class FaceEngine:
    """
    GPU-accelerated face recognition engine:
    - FAISS-GPU cho vector search (fallback CPU tự động)
    - InsightFace với CUDAExecutionProvider nếu có
    - resize trước khi detect để nhẹ hơn
    - chỉ detect mỗi min_interval seconds
    - cache kết quả trong cache_ttl seconds
    """

    def __init__(
        self,
        model_name="buffalo_s",
        det_scale=0.5,         # 0.5 = giảm kích thước frame 1/2
        min_interval=0.25,     # detect tối đa 4 lần/giây
        cache_ttl=1.5,         # dùng lại bbox/label trong 1.5s
        use_gpu=True           # dùng FAISS GPU + CUDA provider
    ):
        self.det_scale = float(det_scale)
        self.min_interval = float(min_interval)
        self.cache_ttl = float(cache_ttl)

        providers = _PROVIDERS if use_gpu else ["CPUExecutionProvider"]
        log.info("FaceEngine: providers=%s", providers)

        # Xac dinh root path cho InsightFace models
        insightface_root = get_insightface_root()
        log.info("FaceEngine: insightface_root=%s", insightface_root)

        self.app = FaceAnalysis(
            name=model_name,
            root=insightface_root,
            providers=providers
        )
        self.app.prepare(ctx_id=0)

        # FAISS index thay cho list brute-force
        self.faiss_index = FaissIndex(dim=512, use_gpu=use_gpu)
        self.load_db()

        # cache
        self._last_run_time = 0.0
        self._cache_time = 0.0
        self._cache_result = None  # (bbox, label, color)

    def load_db(self):
        ids = []
        embs = []
        if not os.path.isdir(DB_DIR):
            os.makedirs(DB_DIR, exist_ok=True)
        else:
            for f in os.listdir(DB_DIR):
                if f.endswith(".npy"):
                    ids.append(f.replace(".npy", ""))
                    embs.append(np.load(os.path.join(DB_DIR, f)))

        self.faiss_index.rebuild(ids, embs)
        log.info("FaceEngine: loaded %d faces into FAISS (%s)",
                 len(ids), "GPU" if self.faiss_index.is_gpu else "CPU")

    def recognize(self, frame_bgr):
        """
        Return:
          None
          OR ((x, y, w, h), label, (b,g,r))
        """
        now = time.time()

        # dùng cache nếu còn hạn
        if self._cache_result is not None and (now - self._cache_time) < self.cache_ttl:
            return self._cache_result

        # hạn chế tần suất chạy model
        if (now - self._last_run_time) < self.min_interval:
            return self._cache_result  # có thể None

        self._last_run_time = now

        if frame_bgr is None:
            return None

        h, w = frame_bgr.shape[:2]
        scale = self.det_scale
        if scale <= 0 or scale > 1.0:
            scale = 0.5

        # resize để nhẹ hơn
        small = cv2.resize(frame_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)

        faces = self.app.get(small)
        if not faces:
            self._cache_result = None
            self._cache_time = now
            return None

        # lấy mặt to nhất
        face = max(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
        )

        emb = face.normed_embedding

        # bbox trên ảnh small -> scale lại về ảnh gốc
        x1, y1, x2, y2 = face.bbox.astype(np.float32)
        inv = 1.0 / scale
        x1 = int(x1 * inv)
        y1 = int(y1 * inv)
        x2 = int(x2 * inv)
        y2 = int(y2 * inv)

        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w, x2))
        y2 = max(0, min(h, y2))

        # FAISS search thay cho vòng lặp cosine
        best_id, best_score = self.faiss_index.search(emb, SIM_THRESHOLD)

        if best_id is not None:
            result = ((x1, y1, x2 - x1, y2 - y1), f"ID {best_id}", (0, 255, 0))
        else:
            result = ((x1, y1, x2 - x1, y2 - y1), "UNKNOWN", (0, 0, 255))

        self._cache_result = result
        self._cache_time = now
        return result
