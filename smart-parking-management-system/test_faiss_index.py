"""
Test script cho FaissIndex module.
Chạy: python test_faiss_index.py
"""
import sys
import numpy as np
from faiss_index import FaissIndex

PASSED = 0
FAILED = 0


def check(name, condition):
    global PASSED, FAILED
    if condition:
        print(f"  ✅ {name}")
        PASSED += 1
    else:
        print(f"  ❌ {name}")
        FAILED += 1


def test_basic_search():
    """Test thêm vectors và search đúng ID."""
    print("\n[1] Basic search")
    idx = FaissIndex(dim=512, use_gpu=True)

    # Tạo 100 random normalized vectors
    rng = np.random.RandomState(42)
    ids = [f"person_{i}" for i in range(100)]
    embs = []
    for _ in range(100):
        v = rng.randn(512).astype(np.float32)
        v /= np.linalg.norm(v)
        embs.append(v)

    idx.rebuild(ids, embs)
    check("count == 100", idx.count == 100)

    # Search chính xác vector đầu tiên → phải trả về "person_0"
    best_id, score = idx.search(embs[0], threshold=0.5)
    check(f"search(embs[0]) → person_0  (got {best_id}, score={score:.4f})", best_id == "person_0")
    check(f"score ≈ 1.0  (got {score:.4f})", score > 0.99)

    # Search vector 50
    best_id, score = idx.search(embs[50], threshold=0.5)
    check(f"search(embs[50]) → person_50  (got {best_id})", best_id == "person_50")


def test_threshold():
    """Test ngưỡng threshold."""
    print("\n[2] Threshold filtering")
    idx = FaissIndex(dim=512, use_gpu=True)

    rng = np.random.RandomState(123)
    ids = ["only_one"]
    embs = [rng.randn(512).astype(np.float32)]
    embs[0] /= np.linalg.norm(embs[0])

    idx.rebuild(ids, embs)

    # Random query vector → score thấp → threshold 0.99 sẽ không match
    query = rng.randn(512).astype(np.float32)
    query /= np.linalg.norm(query)

    best_id, score = idx.search(query, threshold=0.99)
    check(f"high threshold → None  (got {best_id}, score={score:.4f})", best_id is None)


def test_add_one():
    """Test thêm incremental bằng add_one."""
    print("\n[3] Incremental add_one")
    idx = FaissIndex(dim=512, use_gpu=True)
    idx.rebuild([], [])
    check("empty index count == 0", idx.count == 0)

    rng = np.random.RandomState(99)
    v = rng.randn(512).astype(np.float32)
    v /= np.linalg.norm(v)

    idx.add_one("new_person", v)
    check("count == 1 after add_one", idx.count == 1)

    best_id, score = idx.search(v, threshold=0.5)
    check(f"search added vector → new_person  (got {best_id})", best_id == "new_person")


def test_rebuild_clears():
    """Test rebuild xoá index cũ."""
    print("\n[4] Rebuild clears old data")
    idx = FaissIndex(dim=512, use_gpu=True)

    rng = np.random.RandomState(7)
    v1 = rng.randn(512).astype(np.float32)
    v1 /= np.linalg.norm(v1)
    v2 = rng.randn(512).astype(np.float32)
    v2 /= np.linalg.norm(v2)

    idx.rebuild(["a", "b"], [v1, v2])
    check("count == 2", idx.count == 2)

    idx.rebuild(["c"], [v2])
    check("count == 1 after rebuild", idx.count == 1)

    best_id, _ = idx.search(v2, threshold=0.5)
    check(f"search v2 → c  (got {best_id})", best_id == "c")

    best_id, _ = idx.search(v1, threshold=0.99)
    check(f"search v1 high threshold → None (old data cleared)  (got {best_id})", best_id is None)


def test_empty_index():
    """Test search trên index rỗng."""
    print("\n[5] Empty index")
    idx = FaissIndex(dim=512, use_gpu=True)
    idx.rebuild([], [])

    rng = np.random.RandomState(1)
    q = rng.randn(512).astype(np.float32)

    best_id, score = idx.search(q, threshold=0.5)
    check("empty search → None", best_id is None)
    check("empty search score == 0.0", score == 0.0)


def test_gpu_status():
    """Report GPU status."""
    print("\n[6] GPU status")
    idx = FaissIndex(dim=512, use_gpu=True)
    gpu_str = "GPU ✅" if idx.is_gpu else "CPU (fallback)"
    print(f"  ℹ️  FAISS backend: {gpu_str}")
    # This is informational, not a pass/fail test
    check("index created without crash", True)


if __name__ == "__main__":
    print("=" * 50)
    print("  FAISS Index Test Suite")
    print("=" * 50)

    test_basic_search()
    test_threshold()
    test_add_one()
    test_rebuild_clears()
    test_empty_index()
    test_gpu_status()

    print("\n" + "=" * 50)
    print(f"  Results: {PASSED} passed, {FAILED} failed")
    print("=" * 50)

    sys.exit(1 if FAILED > 0 else 0)
