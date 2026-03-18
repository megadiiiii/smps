"""
FAISS-based similarity search utilities.

GPU acceleration is used automatically when faiss-gpu is installed and a CUDA
device is available.  Falls back to faiss-cpu transparently.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, Iterable, List, Optional, Tuple

import faiss
import numpy as np

from config import EMBEDDING_DIM, FAISS_INDEX_PATH

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GPU helper utilities
# ---------------------------------------------------------------------------

def _init_gpu_resources(device: int = 0) -> Optional[faiss.GpuResourcesProvider]:
    """
    Try to allocate FAISS GPU resources on *device*.
    Returns a GpuResources object on success, None otherwise.
    """
    try:
        ngpu = faiss.get_num_gpus()
        if ngpu == 0:
            logger.info("FAISS: no GPU detected, using CPU.")
            return None
        res = faiss.StandardGpuResources()
        logger.info("FAISS: GPU resources initialised on device %d (%d GPU(s) available).", device, ngpu)
        return res
    except (AttributeError, RuntimeError) as exc:
        logger.info("FAISS: GPU init failed (%s), falling back to CPU.", exc)
        return None


def _index_to_gpu(cpu_index: faiss.Index, res: faiss.GpuResourcesProvider, device: int = 0) -> faiss.Index:
    """Move a CPU index to GPU. Returns GPU index, or the original CPU index on failure."""
    try:
        gpu_index = faiss.index_cpu_to_gpu(res, device, cpu_index)
        logger.debug("FAISS index moved to GPU.")
        return gpu_index
    except Exception as exc:  # pragma: no cover
        logger.warning("FAISS: failed to move index to GPU (%s), staying on CPU.", exc)
        return cpu_index


def _index_to_cpu(index: faiss.Index) -> faiss.Index:
    """Convert a GPU index back to a CPU index (no-op if already on CPU)."""
    try:
        return faiss.index_gpu_to_cpu(index)
    except Exception:
        return index


class SearchService:
    """Manages FAISS index build/load/search operations with optional GPU acceleration."""

    def __init__(
        self,
        index_path: str = FAISS_INDEX_PATH,
        embedding_dim: int = EMBEDDING_DIM,
        gpu_device: int = 0,
    ) -> None:
        self.index_path = index_path
        self.meta_path = f"{index_path}.meta.json"
        self.embedding_dim = embedding_dim
        self._gpu_device = gpu_device

        self._gpu_res: Optional[faiss.GpuResourcesProvider] = _init_gpu_resources(gpu_device)
        self._use_gpu: bool = self._gpu_res is not None

        # Internal state – always keep a CPU copy for serialisation;
        # _index may point to a GPU index during runtime.
        self._cpu_index: Optional[faiss.Index] = None
        self._index: Optional[faiss.Index] = None
        self._id_map: Optional[List[str]] = None

    # ------------------------------------------------------------------ #
    # Index management
    # ------------------------------------------------------------------ #

    def build_faiss_index(self, embeddings: Dict[str, List[np.ndarray]]) -> faiss.Index:
        """Build an IndexFlatIP over all embeddings and optionally move to GPU."""
        vectors: List[np.ndarray] = []
        ids: List[str] = []
        for person_id, embs in embeddings.items():
            for emb in embs:
                vectors.append(self._normalize(emb))
                ids.append(person_id)

        if not vectors:
            raise ValueError("No embeddings available to build FAISS index.")

        mat = np.vstack(vectors).astype("float32")
        cpu_index = faiss.IndexFlatIP(self.embedding_dim)
        cpu_index.add(mat)

        self._cpu_index = cpu_index
        self._id_map = ids

        # Move to GPU when available
        if self._use_gpu:
            self._index = _index_to_gpu(cpu_index, self._gpu_res, self._gpu_device)
        else:
            self._index = cpu_index

        self.save_index()
        return self._index

    def save_index(self, index: Optional[faiss.Index] = None, id_map: Optional[Iterable[str]] = None) -> None:
        """Persist index (always as CPU index) and id_map to disk."""
        dir_path = os.path.dirname(self.index_path) or "."
        os.makedirs(dir_path, exist_ok=True)

        save_index = index if index is not None else self._cpu_index
        save_map = list(id_map) if id_map is not None else self._id_map

        if save_index is None or save_map is None:
            return

        # Ensure we write a CPU-compatible index
        cpu_index = _index_to_cpu(save_index)
        faiss.write_index(cpu_index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"ids": save_map, "dim": self.embedding_dim}, f)

    def load_faiss_index(self) -> Optional[faiss.Index]:
        """Load index + metadata from disk and optionally move to GPU."""
        if self._index is not None:
            return self._index
        if not os.path.isfile(self.index_path) or not os.path.isfile(self.meta_path):
            return None

        cpu_index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self._cpu_index = cpu_index
        self._id_map = meta.get("ids", [])

        if self._use_gpu:
            self._index = _index_to_gpu(cpu_index, self._gpu_res, self._gpu_device)
        else:
            self._index = cpu_index

        mode = "GPU" if self._use_gpu else "CPU"
        logger.info("FAISS index loaded (%s, %d vectors).", mode, cpu_index.ntotal)
        return self._index

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #

    def search_similar(self, embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """Return top-k (person_id, score) pairs sorted by cosine similarity."""
        if self._index is None:
            self.load_faiss_index()
        if self._index is None or not self._id_map:
            raise ValueError("FAISS index not built or empty.")

        query = self._normalize(embedding)
        distances, indices = self._index.search(np.array([query]).astype("float32"), k)

        results: List[Tuple[str, float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            if idx >= len(self._id_map):
                continue
            person_id = self._id_map[idx]
            # Re-rank with explicit cosine on the CPU index for safety
            candidate = self._cpu_index.reconstruct(int(idx))
            score = float(np.dot(query, candidate) / (np.linalg.norm(candidate) + 1e-10))
            results.append((person_id, score))

        results.sort(key=lambda item: item[1], reverse=True)
        return results

    # ------------------------------------------------------------------ #
    # Properties / info
    # ------------------------------------------------------------------ #

    @property
    def is_using_gpu(self) -> bool:
        """True when the active index lives on a GPU."""
        return self._use_gpu and self._index is not self._cpu_index

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize(vec: np.ndarray) -> np.ndarray:
        v = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(v) + 1e-10
        return v / norm
