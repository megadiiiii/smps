# faiss_index.py — FAISS GPU/CPU wrapper cho face embedding search
"""
Module đóng gói FAISS index để tìm kiếm embedding khuôn mặt.
- Sử dụng IndexFlatIP (Inner Product) — tương đương cosine similarity
  cho các vector đã normalized (normed_embedding từ InsightFace).
- Tự động dùng GPU nếu có, fallback CPU nếu không.
"""

import logging
import numpy as np

log = logging.getLogger(__name__)

try:
    import faiss

    _FAISS_OK = True
except ImportError:
    _FAISS_OK = False
    log.warning("faiss chưa cài — sẽ dùng brute-force numpy fallback")


class FaissIndex:
    """
    Wrapper quản lý FAISS index cho face embeddings.

    Parameters
    ----------
    dim : int
        Chiều của embedding vector (mặc định 512 cho InsightFace).
    use_gpu : bool
        Nếu True, cố gắng dùng GPU. Nếu GPU không có sẽ fallback CPU.
    gpu_id : int
        ID của GPU cần dùng (mặc định 0).
    """

    def __init__(self, dim: int = 512, use_gpu: bool = True, gpu_id: int = 0):
        self.dim = dim
        self._ids: list[str] = []  # mapping: faiss row → user id
        self._gpu_active = False

        # numpy fallback matrix (used when faiss not installed)
        self._emb_matrix = np.empty((0, dim), dtype=np.float32)

        if not _FAISS_OK:
            self._index = None
            log.info("FaissIndex: chạy ở chế độ numpy fallback (không có faiss)")
            return

        # Tạo flat inner-product index (cosine sim cho normalized vectors)
        cpu_index = faiss.IndexFlatIP(dim)

        if use_gpu:
            try:
                gpu_count = faiss.get_num_gpus()
                if gpu_count > 0:
                    res = faiss.StandardGpuResources()
                    self._index = faiss.index_cpu_to_gpu(res, gpu_id, cpu_index)
                    self._gpu_active = True
                    log.info("FaissIndex: ✅ FAISS GPU (device %d, %d GPUs)", gpu_id, gpu_count)
                else:
                    self._index = cpu_index
                    log.info("FaissIndex: không tìm thấy GPU → dùng FAISS CPU")
            except Exception as e:
                self._index = cpu_index
                log.warning("FaissIndex: GPU init thất bại (%s) → fallback CPU", e)
        else:
            self._index = cpu_index
            log.info("FaissIndex: FAISS CPU (use_gpu=False)")

    # ------------------------------------------------------------------
    @property
    def count(self) -> int:
        """Số lượng vectors trong index."""
        if self._index is not None:
            return self._index.ntotal
        return len(self._ids)

    @property
    def is_gpu(self) -> bool:
        return self._gpu_active

    # ------------------------------------------------------------------
    def rebuild(self, ids: list[str], embeddings: list[np.ndarray]):
        """
        Xoá index cũ, build lại từ danh sách ids + embeddings.

        Parameters
        ----------
        ids : list[str]
            Danh sách user/person IDs.
        embeddings : list[np.ndarray]
            Danh sách embedding vectors (phải normalized).
        """
        self._ids = list(ids)

        if self._index is not None:
            self._index.reset()
            if embeddings:
                matrix = np.stack(embeddings).astype(np.float32)
                # Đảm bảo normalized cho inner product = cosine
                norms = np.linalg.norm(matrix, axis=1, keepdims=True)
                norms = np.where(norms < 1e-8, 1.0, norms)
                matrix = matrix / norms
                self._index.add(matrix)
            log.debug("FaissIndex.rebuild: %d vectors", len(self._ids))
        else:
            # numpy fallback
            if embeddings:
                self._emb_matrix = np.stack(embeddings).astype(np.float32)
                norms = np.linalg.norm(self._emb_matrix, axis=1, keepdims=True)
                norms = np.where(norms < 1e-8, 1.0, norms)
                self._emb_matrix = self._emb_matrix / norms
            else:
                self._emb_matrix = np.empty((0, self.dim), dtype=np.float32)

    def add_one(self, user_id: str, embedding: np.ndarray):
        """
        Thêm 1 embedding vào index (không rebuild lại toàn bộ).
        """
        emb = embedding.astype(np.float32).reshape(1, -1)
        norm = np.linalg.norm(emb)
        if norm > 1e-8:
            emb = emb / norm

        self._ids.append(user_id)

        if self._index is not None:
            self._index.add(emb)
        else:
            if hasattr(self, "_emb_matrix") and self._emb_matrix.shape[0] > 0:
                self._emb_matrix = np.vstack([self._emb_matrix, emb])
            else:
                self._emb_matrix = emb.copy()

    # ------------------------------------------------------------------
    def search(self, query_emb: np.ndarray, threshold: float = 0.5):
        """
        Tìm top-1 match trong index.

        Parameters
        ----------
        query_emb : np.ndarray
            Embedding query (đã normalized hoặc chưa — sẽ tự normalize).
        threshold : float
            Ngưỡng similarity tối thiểu.

        Returns
        -------
        tuple[str | None, float]
            (best_id, best_score) nếu score >= threshold,
            (None, 0.0) nếu không tìm thấy hoặc dưới ngưỡng.
        """
        if not self._ids:
            return None, 0.0

        q = query_emb.astype(np.float32).reshape(1, -1)
        norm = np.linalg.norm(q)
        if norm > 1e-8:
            q = q / norm

        if self._index is not None:
            # FAISS search
            scores, indices = self._index.search(q, 1)
            score = float(scores[0][0])
            idx = int(indices[0][0])
            if idx < 0 or idx >= len(self._ids):
                return None, 0.0
            if score >= threshold:
                return self._ids[idx], score
            return None, score
        else:
            # numpy fallback
            similarities = self._emb_matrix @ q.T  # (N, 1)
            similarities = similarities.flatten()
            idx = int(np.argmax(similarities))
            score = float(similarities[idx])
            if score >= threshold:
                return self._ids[idx], score
            return None, score
