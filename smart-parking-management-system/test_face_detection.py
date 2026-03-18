"""
Test script de kiem tra face detection
"""
import sys
import os

# Add path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "Ai-nh-n-di-n-khu-n-m-tk-main"))
sys.path.insert(0, AI_DIR)

print(f"AI_DIR: {AI_DIR}")
print(f"AI_DIR exists: {os.path.isdir(AI_DIR)}")

# Test 1: Import onnxruntime
try:
    import onnxruntime as ort
    print(f"[OK] onnxruntime {ort.__version__}")
    print(f"  Available providers: {ort.get_available_providers()}")
except Exception as e:
    print(f"[FAIL] onnxruntime error: {e}")

# Test 2: Import InsightFace
try:
    from insightface.app import FaceAnalysis
    print("[OK] InsightFace import")
except Exception as e:
    print(f"[FAIL] InsightFace error: {e}")

# Test 3: Load face_embedder
try:
    import importlib.util
    embedder_path = os.path.join(AI_DIR, "modules", "face_embedder.py")
    print(f"\nface_embedder path: {embedder_path}")
    print(f"face_embedder exists: {os.path.exists(embedder_path)}")

    spec = importlib.util.spec_from_file_location("face_embedder_ai", embedder_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("[OK] face_embedder loaded")
except Exception as e:
    print(f"[FAIL] face_embedder load failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Load detector and recognizer from AI project
try:
    import importlib.util

    # Load config
    config_path = os.path.join(AI_DIR, "config.py")
    spec_cfg = importlib.util.spec_from_file_location("config", config_path)
    config_module = importlib.util.module_from_spec(spec_cfg)
    sys.modules['config'] = config_module
    spec_cfg.loader.exec_module(config_module)
    print("\n[OK] config loaded")

    # Load detector
    detector_path = os.path.join(AI_DIR, "models", "detector.py")
    spec_det = importlib.util.spec_from_file_location("detector_module", detector_path)
    detector_module = importlib.util.module_from_spec(spec_det)
    spec_det.loader.exec_module(detector_module)
    FaceDetector = detector_module.FaceDetector
    print("[OK] FaceDetector loaded")

    # Load recognizer
    recognizer_path = os.path.join(AI_DIR, "models", "recognizer.py")
    spec_rec = importlib.util.spec_from_file_location("recognizer_module", recognizer_path)
    recognizer_module = importlib.util.module_from_spec(spec_rec)
    spec_rec.loader.exec_module(recognizer_module)
    FaceRecognizer = recognizer_module.FaceRecognizer
    print("[OK] FaceRecognizer loaded")

    # Create detector instance
    print("\nCreating detector instance (this may take a while)...")
    detector = FaceDetector(det_size=(640, 640), ctx_id=-1)  # CPU
    print("[OK] FaceDetector instance created")

    # Create recognizer instance
    print("Creating recognizer instance (this may take a while)...")
    recognizer = FaceRecognizer(ctx_id=-1)  # CPU
    print("[OK] FaceRecognizer instance created")

except Exception as e:
    print(f"[FAIL] AI models load failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[DONE] All tests completed!")
