# Face Comparison Module - For Smart Parking Management System

## Quick Overview

The **Face Comparison Module** (`face_comparison.py`) from `Ai-nh-n-di-n-khu-n-m-tk-main` provides face matching and verification functions for use in Smart Parking Management System.

## What It Does

- Compare two face embeddings (1:1 verification)
- Find best match in a list of embeddings (1:N recognition)
- Batch process multiple comparisons
- Calculate similarity scores with configurable thresholds

## Installation

1. Keep both folders in same parent directory:
   ```
   FaceAuthorization/
   ├── Ai-nh-n-di-n-khu-n-m-tk-main/    <- Module source
   │   ├── face_comparison.py
   │   └── ...
   └── smart-parking-management-system/  <- Main system
       ├── face_engine.py
       └── ...
   ```

2. No pip installation needed - just import directly

## Usage Examples

### 1. Simple Face Comparison (1:1 Verification)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Ai-nh-n-di-n-khu-n-m-tk-main'))

from face_comparison import compare_faces

# Get embeddings from InsightFace
emb1 = face1.normed_embedding  # 512-dim vector
emb2 = face2.normed_embedding

# Compare them
result = compare_faces(emb1, emb2, threshold=0.4)

print(f"Result: {result['result']}")  # "MATCH" or "NOT MATCH"
print(f"Confidence: {result['score_pct']}%")  # e.g., 95.23%
```

### 2. Find Best Match from Database (1:N Recognition)

```python
from face_comparison import find_best_match
import pickle

# Load stored embeddings
with open('face_embeddings.pkl', 'rb') as f:
    person_ids, embeddings = pickle.load(f)

# Find who this person is
unknown_emb = new_face.normed_embedding
best_idx, best_result = find_best_match(unknown_emb, embeddings, threshold=0.4)

if best_idx >= 0:
    person_id = person_ids[best_idx]
    confidence = best_result['score_pct']
    print(f"Recognized: Person {person_id} ({confidence}% confidence)")
else:
    print("Unknown person")
```

### 3. Batch Processing Multiple Faces

```python
from face_comparison import batch_compare

reference = unknown_face.normed_embedding
known_faces = [emb1, emb2, emb3, ...]

results = batch_compare(reference, known_faces, threshold=0.4)
matches = [i for i, r in enumerate(results) if r['match']]

print(f"Found {len(matches)} matches: {matches}")
```

## Integration with Existing Code

### In `face_engine.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Ai-nh-n-di-n-khu-n-m-tk-main'))

from face_comparison import find_best_match, COMPARISON_THRESHOLD

class FaceEngine:
    def recognize(self, frame_bgr):
        # ... existing detection code ...

        # Get embedding from InsightFace
        emb = face.normed_embedding

        # Find best match using face_comparison module
        best_id, result = find_best_match(
            emb,
            self.embeddings_list,
            threshold=0.4
        )

        if best_id >= 0:
            label = f"Person {best_id} ({result['score_pct']}%)"
            color = (0, 255, 0)  # Green
        else:
            label = "UNKNOWN"
            color = (0, 0, 255)  # Red

        return ((x, y, w, h), label, color)
```

## API Reference

### `compare_faces(emb1, emb2, threshold=0.4)`
Compare two embeddings and return match result.
- **Args**: Two numpy arrays (512-dim) and optional threshold
- **Returns**: dict with `match`, `score`, `score_pct`, `result`

### `find_best_match(reference_emb, query_embs, threshold=0.4)`
Find best matching embedding from a list.
- **Args**: Reference embedding, list of embeddings, threshold
- **Returns**: `(best_index, best_result)` or `(-1, None)`

### `batch_compare(reference_emb, query_embs, threshold=0.4)`
Compare one embedding against many.
- **Args**: Reference embedding, list of embeddings, threshold
- **Returns**: List of comparison results

### `cosine_similarity(emb1, emb2)`
Calculate raw cosine similarity.
- **Args**: Two numpy arrays
- **Returns**: float in range [-1, 1]

## Threshold Configuration

Different use cases require different thresholds:

| Threshold | Use Case | False Match Rate |
|-----------|----------|-----------------|
| 0.3 | Lenient, high recall | Higher |
| 0.4 | **Balanced (default)** | Moderate |
| 0.5 | Strict, high precision | Lower |
| 0.6 | Very strict | Minimal |

```python
# Strict matching (security-critical)
result = compare_faces(emb1, emb2, threshold=0.5)

# Balanced (recommended)
result = compare_faces(emb1, emb2, threshold=0.4)

# Lenient (speed-optimized)
result = compare_faces(emb1, emb2, threshold=0.3)
```

## Performance

- **compare_faces()**: < 1 millisecond
- **find_best_match()**: Proportional to number of embeddings (O(n))
- **batch_compare()**: O(n) where n = number of embeddings

No GPU/ML model loading needed.

## Dependencies

Only requires:
- `numpy` (already in both projects)

No additional pip packages needed!

## Testing

Run tests to verify module works correctly:

```bash
python test_face_comparison.py
```

Expected output shows all 5 tests passing with confidence percentages.

## Common Issues

### Import Error
```python
# Make sure path is correct for your structure
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Ai-nh-n-di-n-khu-n-m-tk-main'))
```

### Threshold Too Strict (Missing Matches)
```python
# Reduce threshold
result = compare_faces(emb1, emb2, threshold=0.35)
```

### Threshold Too Lenient (False Matches)
```python
# Increase threshold
result = compare_faces(emb1, emb2, threshold=0.45)
```

## Version

- **face_comparison.py v1.0.0**
- Python 3.8+
- NumPy required

## Files Included

```
Ai-nh-n-di-n-khu-n-m-tk-main/
├── face_comparison.py                    <- Main module to import
├── test_face_comparison.py               <- Test suite
├── FACE_COMPARISON_INTEGRATION.md        <- Detailed integration guide
└── modules/comparator.py                 <- Original implementation
```

## Support

For integration issues, refer to:
- `FACE_COMPARISON_INTEGRATION.md` - Detailed integration guide
- `test_face_comparison.py` - Usage examples
- `face_comparison.py` - Fully documented source code

---

**Summary**: Use `face_comparison.py` to add 1:1 and 1:N face matching to smart-parking-management-system. No additional setup needed beyond sys.path configuration.
