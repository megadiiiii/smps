"""
Face Comparison Module
======================

Standalone face comparison library for the Face Authorization System.
Provides functions to compare face embeddings and verify identity matches.

Usage:
    from face_comparison import compare_faces, cosine_similarity

Example:
    import numpy as np
    from face_comparison import compare_faces

    # Two face embeddings (512-dim vectors from InsightFace)
    emb1 = np.random.randn(512).astype(np.float32)
    emb2 = np.random.randn(512).astype(np.float32)

    # Compare
    result = compare_faces(emb1, emb2, threshold=0.4)
    print(result['result'])  # "MATCH" or "NOT MATCH"
    print(result['score_pct'])  # 95.23 (confidence %)
"""

__version__ = "1.0.0"
__all__ = ['compare_faces', 'cosine_similarity', 'COMPARISON_THRESHOLD']

import numpy as np
from typing import Dict, Tuple

# Default threshold for face comparison
# 0.4 = good balance between precision and recall
# Adjust based on your security requirements:
#   - 0.3 = stricter (fewer false matches)
#   - 0.5 = lenient (more matches)
COMPARISON_THRESHOLD = 0.4


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """
    Compute cosine similarity between two face embeddings.

    Works with L2-normalized vectors (standard for InsightFace).
    Result range: [-1, 1], where 1 = identical faces.

    Args:
        emb1: Face embedding vector (shape: (512,) for buffalo_l)
        emb2: Face embedding vector (shape: (512,))

    Returns:
        float: Cosine similarity score in range [-1, 1]
    """
    # Normalize embeddings
    emb1 = emb1 / (np.linalg.norm(emb1) + 1e-10)
    emb2 = emb2 / (np.linalg.norm(emb2) + 1e-10)

    # Cosine similarity = dot product of normalized vectors
    return float(np.dot(emb1, emb2))


def compare_faces(
    emb1: np.ndarray,
    emb2: np.ndarray,
    threshold: float = COMPARISON_THRESHOLD,
) -> Dict:
    """
    Compare two face embeddings and determine if they match.

    This is the main function for 1:1 face verification.
    Uses cosine similarity with configurable threshold.

    Args:
        emb1: First face embedding (from InsightFace model)
        emb2: Second face embedding (from InsightFace model)
        threshold: Minimum similarity to consider a match (default: 0.4)

    Returns:
        dict with keys:
            - 'match' (bool): Whether faces match above threshold
            - 'score' (float): Raw similarity score (-1 to 1)
            - 'score_pct' (float): Similarity as percentage (0-100)
            - 'result' (str): "MATCH" or "NOT MATCH"
            - 'threshold' (float): The threshold used

    Example:
        result = compare_faces(embedding1, embedding2, threshold=0.4)
        if result['match']:
            print(f"Same person! ({result['score_pct']}% match)")
        else:
            print(f"Different people ({result['score_pct']}% match)")
    """
    # Calculate similarity
    score = cosine_similarity(emb1, emb2)

    # Check if above threshold
    match = score >= threshold

    # Convert to percentage (for human readability)
    # Note: cosine similarity for faces is typically 0-1 range
    score_pct = round(max(0.0, min(1.0, score)) * 100, 2)

    return {
        'match': match,
        'score': round(score, 4),
        'score_pct': score_pct,
        'result': 'MATCH' if match else 'NOT MATCH',
        'threshold': threshold,
    }


def batch_compare(
    reference_emb: np.ndarray,
    query_embs: list,
    threshold: float = COMPARISON_THRESHOLD,
) -> list:
    """
    Compare one reference embedding against multiple query embeddings.

    Useful for 1:N recognition (find who this person is).

    Args:
        reference_emb: The embedding to search for
        query_embs: List of embeddings to search against
        threshold: Minimum similarity threshold

    Returns:
        List of comparison results (same dict format as compare_faces)

    Example:
        reference = embedding_of_unknown_person
        known_faces = [emb1, emb2, emb3, ...]
        results = batch_compare(reference, known_faces)
        matches = [r for r in results if r['match']]
    """
    results = []
    for query_emb in query_embs:
        result = compare_faces(reference_emb, query_emb, threshold)
        results.append(result)
    return results


def find_best_match(
    reference_emb: np.ndarray,
    query_embs: list,
    threshold: float = COMPARISON_THRESHOLD,
) -> Tuple[int, Dict]:
    """
    Find the best matching embedding from a list.

    Returns the highest scoring match above threshold.

    Args:
        reference_emb: The embedding to search for
        query_embs: List of embeddings to search against
        threshold: Minimum similarity threshold

    Returns:
        Tuple of (best_index, best_result) or (-1, None) if no match

    Example:
        idx, result = find_best_match(unknown_emb, database_embs, threshold=0.4)
        if idx >= 0:
            print(f"Best match: person {idx} with {result['score_pct']}% confidence")
    """
    if not query_embs:
        return -1, None

    results = batch_compare(reference_emb, query_embs, threshold)

    # Find highest scoring match
    best_idx = -1
    best_score = -1

    for i, result in enumerate(results):
        if result['match'] and result['score'] > best_score:
            best_idx = i
            best_score = result['score']

    if best_idx >= 0:
        return best_idx, results[best_idx]

    return -1, None


# For backward compatibility with old code
def verify(
    emb1: np.ndarray,
    emb2: np.ndarray,
    threshold: float = COMPARISON_THRESHOLD,
) -> Dict:
    """Legacy function name - use compare_faces() instead."""
    return compare_faces(emb1, emb2, threshold)
