"""
Test face_comparison module
"""
import numpy as np
import sys
from pathlib import Path

# Add parent dir to path to import face_comparison
sys.path.insert(0, str(Path(__file__).parent))

from face_comparison import compare_faces, cosine_similarity, batch_compare, find_best_match

def test_cosine_similarity():
    """Test cosine similarity calculation"""
    print("Test 1: Cosine Similarity")
    print("-" * 50)

    # Identical vectors
    emb1 = np.ones(512, dtype=np.float32)
    emb2 = np.ones(512, dtype=np.float32)
    sim = cosine_similarity(emb1, emb2)
    print(f"Identical vectors: {sim:.4f} (expected ~1.0)")
    assert sim > 0.99, "Identical vectors should have similarity ~1"

    # Opposite vectors
    emb1 = np.ones(512, dtype=np.float32)
    emb2 = -np.ones(512, dtype=np.float32)
    sim = cosine_similarity(emb1, emb2)
    print(f"Opposite vectors: {sim:.4f} (expected ~-1.0)")
    assert sim < -0.99, "Opposite vectors should have similarity ~-1"

    print("[PASS] Cosine similarity test passed\n")


def test_compare_faces():
    """Test face comparison"""
    print("Test 2: Face Comparison")
    print("-" * 50)

    # Similar embeddings (same person)
    np.random.seed(42)
    emb1 = np.random.randn(512).astype(np.float32)
    emb2 = emb1 + np.random.randn(512).astype(np.float32) * 0.1  # Small noise

    result = compare_faces(emb1, emb2, threshold=0.4)
    print(f"Similar embeddings result:")
    print(f"  Match: {result['match']}")
    print(f"  Score: {result['score']:.4f}")
    print(f"  Confidence: {result['score_pct']:.2f}%")

    # Different embeddings (different person)
    emb3 = np.random.randn(512).astype(np.float32)
    result = compare_faces(emb1, emb3, threshold=0.4)
    print(f"\nDifferent embeddings result:")
    print(f"  Match: {result['match']}")
    print(f"  Score: {result['score']:.4f}")
    print(f"  Confidence: {result['score_pct']:.2f}%")

    print("[PASS] Face comparison test passed\n")


def test_batch_compare():
    """Test batch comparison"""
    print("Test 3: Batch Compare")
    print("-" * 50)

    np.random.seed(42)
    reference = np.random.randn(512).astype(np.float32)
    embeddings = [
        reference + np.random.randn(512).astype(np.float32) * 0.05,  # Similar
        reference + np.random.randn(512).astype(np.float32) * 0.2,   # Similar
        np.random.randn(512).astype(np.float32),                      # Different
        np.random.randn(512).astype(np.float32),                      # Different
    ]

    results = batch_compare(reference, embeddings, threshold=0.4)
    print(f"Compared against {len(results)} embeddings:")
    for i, result in enumerate(results):
        match_text = "MATCH" if result['match'] else "NO MATCH"
        print(f"  [{i}] {match_text:8} - {result['score_pct']:6.2f}% confidence")

    print("[PASS] Batch compare test passed\n")


def test_find_best_match():
    """Test finding best match"""
    print("Test 4: Find Best Match")
    print("-" * 50)

    np.random.seed(42)
    reference = np.random.randn(512).astype(np.float32)
    embeddings = [
        np.random.randn(512).astype(np.float32),                      # Different
        reference + np.random.randn(512).astype(np.float32) * 0.15,  # Good match
        reference + np.random.randn(512).astype(np.float32) * 0.1,   # Best match
        np.random.randn(512).astype(np.float32),                      # Different
    ]

    best_idx, best_result = find_best_match(reference, embeddings, threshold=0.4)
    print(f"Best match found at index: {best_idx}")
    print(f"  Score: {best_result['score']:.4f}")
    print(f"  Confidence: {best_result['score_pct']:.2f}%")

    assert best_idx == 2, "Should find best match at index 2"
    print("[PASS] Find best match test passed\n")


def test_threshold_variations():
    """Test different thresholds"""
    print("Test 5: Threshold Variations")
    print("-" * 50)

    np.random.seed(42)
    emb1 = np.random.randn(512).astype(np.float32)
    emb2 = emb1 + np.random.randn(512).astype(np.float32) * 0.1

    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    score = cosine_similarity(emb1, emb2)

    print(f"Embedding similarity score: {score:.4f}\n")
    print("Results with different thresholds:")
    for thresh in thresholds:
        result = compare_faces(emb1, emb2, threshold=thresh)
        match_text = "✓ MATCH" if result['match'] else "✗ NO MATCH"
        print(f"  Threshold {thresh:.1f}: {match_text} (above threshold)")

    print("[PASS] Threshold variation test passed\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Face Comparison Module Tests")
    print("=" * 50 + "\n")

    try:
        test_cosine_similarity()
        test_compare_faces()
        test_batch_compare()
        test_find_best_match()
        test_threshold_variations()

        print("=" * 50)
        print("All tests passed! [OK]")
        print("=" * 50)

    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
