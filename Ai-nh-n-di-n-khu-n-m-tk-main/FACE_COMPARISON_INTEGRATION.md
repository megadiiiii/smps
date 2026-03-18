"""
Face Comparison Module - Integration Guide

This guide explains how to use the Face Comparison Module from smart-parking-management-system.
"""

# Integration with smart-parking-management-system
# =================================================

## 1. Basic Usage in smart-parking-management-system

In your code (e.g., face_engine.py or any other file):

```python
import sys
sys.path.insert(0, '../Ai-nh-n-di-n-khu-n-m-tk-main')
from face_comparison import compare_faces, find_best_match, COMPARISON_THRESHOLD

# Example: Compare two face embeddings
emb1 = face_obj1.normed_embedding  # From InsightFace
emb2 = face_obj2.normed_embedding

result = compare_faces(emb1, emb2, threshold=0.4)
print(result)
# Output: {
#     'match': True,
#     'score': 0.8523,
#     'score_pct': 85.23,
#     'result': 'MATCH',
#     'threshold': 0.4
# }

if result['match']:
    print(f"Same person! Confidence: {result['score_pct']}%")
```

## 2. Finding Best Match from Database

```python
from face_comparison import find_best_match

# You have a list of stored embeddings
known_embeddings = [emb_person1, emb_person2, emb_person3, ...]

# Find who this unknown person is
unknown_embedding = new_face.normed_embedding
best_idx, best_result = find_best_match(unknown_embedding, known_embeddings, threshold=0.4)

if best_idx >= 0:
    print(f"Identified as person {best_idx}")
    print(f"Confidence: {best_result['score_pct']}%")
else:
    print("Unknown person")
```

## 3. Batch Comparison

```python
from face_comparison import batch_compare

reference = unknown_face.normed_embedding
database = [emb1, emb2, emb3, ...]

results = batch_compare(reference, database, threshold=0.4)
matches = [(i, r) for i, r in enumerate(results) if r['match']]

print(f"Found {len(matches)} matches")
for person_id, result in matches:
    print(f"  Person {person_id}: {result['score_pct']}% match")
```

## 4. Custom Threshold

Different security levels:

```python
# Strict: Only perfect matches (security-critical)
result = compare_faces(emb1, emb2, threshold=0.5)

# Balanced: Good accuracy (default)
result = compare_faces(emb1, emb2, threshold=0.4)

# Lenient: Accept more matches (speed over accuracy)
result = compare_faces(emb1, emb2, threshold=0.3)
```

## 5. Integration with Existing face_engine.py

```python
# In smart-parking-management-system/face_engine.py

import sys
sys.path.insert(0, '../Ai-nh-n-di-n-khu-n-m-tk-main')
from face_comparison import find_best_match

class FaceEngine:
    def recognize(self, frame_bgr):
        # ... existing code to detect faces and get embedding ...
        emb = face.normed_embedding

        # Use face comparison module for matching
        best_id, result = find_best_match(
            emb,
            self.stored_embeddings,
            threshold=0.4
        )

        if best_id >= 0:
            return ((x1, y1, x2-x1, y2-y1), f"ID {best_id}", (0, 255, 0))
        else:
            return ((x1, y1, x2-x1, y2-y1), "UNKNOWN", (0, 0, 255))
```

## Dependencies

The face_comparison module requires:
- numpy (already in both projects)

That's it! No additional dependencies.

## File Structure

```
Ai-nh-n-di-n-khu-n-m-tk-main/
├── face_comparison.py          <- Module to import
├── modules/
│   └── comparator.py           <- Original implementation (if needed)
└── ...

smart-parking-management-system/
├── face_engine.py
├── admin_gui.py
└── ... (imports face_comparison from Ai-nh)
```

## Performance

- compare_faces(): < 1ms (just math operations)
- batch_compare(): O(n) where n = number of embeddings
- find_best_match(): O(n) with early stopping

No ML model loading needed - the module only does similarity calculations.

## Functions Reference

### compare_faces(emb1, emb2, threshold=0.4) -> dict
Main function for 1:1 verification.
- Quick check if two faces are the same person
- Returns: match (bool), score, score_pct, result, threshold

### find_best_match(reference_emb, query_embs, threshold=0.4) -> (int, dict)
Find best matching embedding from a list.
- Returns: (best_index, best_result) or (-1, None)

### batch_compare(reference_emb, query_embs, threshold=0.4) -> list
Compare reference against all queries.
- Returns: list of comparison results

### cosine_similarity(emb1, emb2) -> float
Raw similarity calculation.
- Returns: float in range [-1, 1]

## Version

face_comparison module v1.0.0
- Standalone, no Flask dependencies
- Pure math-based (NumPy only)
- Production-ready
