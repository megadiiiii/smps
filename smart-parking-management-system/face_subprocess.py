"""
face_subprocess.py
-------------------
Isolated subprocess for real-time face detection/recognition.
This file is intentionally kept separate from the GUI module to avoid
importing PyQt6 in the child process (Windows 'spawn' would re-import
the entire module, causing DLL conflicts with onnxruntime).
"""

import os
import sys
import time
import logging
import ctypes

import cv2

log = logging.getLogger("parking.face_sub")


def _can_use_cuda_provider() -> bool:
    """Return True only when CUDA EP exists and required runtime DLLs are loadable."""
    capi_dir = ""
    try:
        import onnxruntime as ort
        if "CUDAExecutionProvider" not in ort.get_available_providers():
            return False
        capi_dir = os.path.join(os.path.dirname(ort.__file__), "capi")
    except Exception:
        return False

    if os.name != "nt":
        return True

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

    for dll in ("cublasLt64_12.dll", "cublas64_12.dll"):
        if not _load_dll(dll):
            return False

    if not _load_dll("cudnn64_9.dll") and not _load_dll("cudnn64_8.dll"):
        return False
    return True


def face_process_main(in_q, out_q,
                      ai_dir: str,
                      smps_dir: str,
                      det_size=(320, 320),
                      det_scale=0.5,
                      sim_threshold=0.4):
    """Face detection/recognition loop running in a spawned subprocess."""
    import pickle, json, importlib.util

    # Defensive normalization for process args from callers.
    if not isinstance(ai_dir, (str, bytes, os.PathLike)):
        raise TypeError(f"ai_dir must be a path-like value, got {type(ai_dir).__name__}")
    if not isinstance(smps_dir, (str, bytes, os.PathLike)):
        smps_dir = os.getcwd()
    ai_dir = os.fspath(ai_dir)
    smps_dir = os.fspath(smps_dir)

    # Ensure both project dirs are on sys.path
    for d in (ai_dir, smps_dir):
        if d and d not in sys.path:
            sys.path.insert(0, d)

    try:
        # Load config module
        config_path = os.path.join(ai_dir, "config.py")
        spec_cfg = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec_cfg)
        sys.modules['config'] = config_module
        spec_cfg.loader.exec_module(config_module)

        # Load detector module
        detector_path = os.path.join(ai_dir, "models", "detector.py")
        spec_det = importlib.util.spec_from_file_location("detector_module", detector_path)
        detector_module = importlib.util.module_from_spec(spec_det)
        spec_det.loader.exec_module(detector_module)
        FaceDetector = detector_module.FaceDetector

        # Load recognizer module
        recognizer_path = os.path.join(ai_dir, "models", "recognizer.py")
        spec_rec = importlib.util.spec_from_file_location("recognizer_module", recognizer_path)
        recognizer_module = importlib.util.module_from_spec(spec_rec)
        spec_rec.loader.exec_module(recognizer_module)
        FaceRecognizer = recognizer_module.FaceRecognizer
    except Exception as e:
        print(f"[face_subprocess] INIT ERROR: {e}", flush=True)
        while True:
            item = in_q.get()
            if item is None:
                break
            out_q.put({"bbox": None, "label": None, "emb": None, "err": str(e)})
        return

    # Auto-detect CUDA (safe fallback to CPU when runtime DLLs are missing)
    _ctx = 0 if _can_use_cuda_provider() else -1

    detector = FaceDetector(det_size=det_size, ctx_id=_ctx)
    recognizer = FaceRecognizer(ctx_id=_ctx)

    emb_file    = os.path.join(ai_dir, "data", "embeddings", "embeddings.pkl")
    facedb_file = os.path.join(ai_dir, "data", "embeddings", "face_db.json")

    person_names: dict = {}

    # FAISS index
    from faiss_index import FaissIndex
    faiss_idx = FaissIndex(dim=512, use_gpu=(_ctx >= 0))

    def reload_db():
        nonlocal person_names
        all_ids = []
        all_embs = []
        if os.path.isfile(emb_file):
            try:
                with open(emb_file, "rb") as f:
                    person_embs_raw = pickle.load(f)
                for pid, emb_list in person_embs_raw.items():
                    for emb_vec in emb_list:
                        all_ids.append(pid)
                        all_embs.append(emb_vec)
            except Exception:
                pass
        if os.path.isfile(facedb_file):
            try:
                with open(facedb_file, "r", encoding="utf-8") as f:
                    db = json.load(f)
                person_names = {pid: info.get("name", pid) for pid, info in db.items()}
            except Exception:
                pass
        faiss_idx.rebuild(all_ids, all_embs)

    reload_db()
    last_reload = time.time()
    print("[face_subprocess] Ready, waiting for frames...", flush=True)

    while True:
        frame = in_q.get()
        if frame is None:
            break

        # Reload DB every 30s
        if time.time() - last_reload > 30:
            reload_db()
            last_reload = time.time()

        try:
            import numpy as np
            h0, w0 = frame.shape[:2]
            s = det_scale if 0 < det_scale <= 1 else 0.5
            small = cv2.resize(frame, (int(w0 * s), int(h0 * s)), interpolation=cv2.INTER_LINEAR)

            detections = detector.detect(small)
            if not detections:
                out_q.put({"bbox": None, "label": None, "emb": None})
                continue

            best_det = detections[0]
            emb = recognizer.embed(small, face_obj=best_det["face_obj"])

            # Scale bbox back to original resolution
            inv = 1.0 / s
            x1, y1, x2, y2 = best_det["bbox"]
            x1, y1 = int(x1 * inv), int(y1 * inv)
            x2, y2 = int(x2 * inv), int(y2 * inv)
            x1 = max(0, min(w0 - 1, x1))
            y1 = max(0, min(h0 - 1, y1))
            x2 = max(0, min(w0,     x2))
            y2 = max(0, min(h0,     y2))
            bbox = (x1, y1, x2 - x1, y2 - y1)

            # FAISS search
            label = "UNKNOWN"
            best_id, best_score = faiss_idx.search(emb, sim_threshold)
            if best_id is not None:
                label = person_names.get(best_id, best_id)

            out_q.put({"bbox": bbox, "label": label, "emb": emb})
        except Exception as e:
            print(f"[face_subprocess] DETECT ERROR: {e}", flush=True)
            out_q.put({"bbox": None, "label": None, "emb": None, "err": str(e)})
