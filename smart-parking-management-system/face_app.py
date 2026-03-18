import cv2
import os
import time
import logging
import numpy as np
from insightface.app import FaceAnalysis
from faiss_index import FaissIndex

log = logging.getLogger(__name__)

# ================== CONFIG ==================
DB_DIR = "face_db"
os.makedirs(DB_DIR, exist_ok=True)

DETECT_EVERY_N_FRAMES = 5
SIM_THRESHOLD = 0.5
CAMERA_INDEX = 0

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
# ============================================


class FaceSystem:
    def __init__(self, use_gpu=True):
        providers = _PROVIDERS if use_gpu else ["CPUExecutionProvider"]
        print(f"[INIT] Loading InsightFace model... providers={providers}")
        self.app = FaceAnalysis(
            name="buffalo_s",
            providers=providers
        )
        self.app.prepare(ctx_id=0)

        # FAISS index thay cho list brute-force
        self.faiss_index = FaissIndex(dim=512, use_gpu=use_gpu)
        self.load_db()

        self.last_face = None   # (bbox, emb)
        self.last_result = None # (bbox, label, color)

        print(f"[DB] Loaded {self.faiss_index.count} identities into FAISS "
              f"({'GPU' if self.faiss_index.is_gpu else 'CPU'})")

    def load_db(self):
        ids = []
        embs = []
        for f in os.listdir(DB_DIR):
            if f.endswith(".npy"):
                ids.append(f.replace(".npy", ""))
                embs.append(np.load(os.path.join(DB_DIR, f)))
        self.faiss_index.rebuild(ids, embs)

    def detect_and_recognize(self, frame):
        faces = self.app.get(frame)
        if not faces:
            self.last_face = None
            self.last_result = None
            return None

        # lấy mặt to nhất
        face = max(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
        )

        x1, y1, x2, y2 = face.bbox.astype(int)
        emb = face.normed_embedding
        self.last_face = ((x1, y1, x2, y2), emb)

        # FAISS search thay cho vòng lặp cosine
        best_id, best_score = self.faiss_index.search(emb, SIM_THRESHOLD)

        if best_id is not None:
            label = f"ID {best_id}"
            color = (0, 255, 0)
        else:
            label = "UNKNOWN"
            color = (0, 0, 255)

        self.last_result = ((x1, y1, x2, y2), label, color)
        return self.last_result

    def register_last_face(self):
        if self.last_face is None:
            return None

        _, emb = self.last_face
        new_id = str(int(time.time()))[-8:]
        np.save(os.path.join(DB_DIR, f"{new_id}.npy"), emb)

        # Thêm trực tiếp vào FAISS index (không cần rebuild)
        self.faiss_index.add_one(new_id, emb)

        print(f"[REGISTER] New face ID = {new_id} "
              f"(total: {self.faiss_index.count})")
        return new_id


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Không mở được camera")
        return

    face_sys = FaceSystem()
    frame_count = 0

    print("\n=== FACE SYSTEM STARTED (FAISS-GPU) ===")
    print("[R] Register UNKNOWN face")
    print("[Q] Quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        frame_count += 1

        # detect mỗi N frame
        if frame_count % DETECT_EVERY_N_FRAMES == 0:
            face_sys.detect_and_recognize(frame)

        # vẽ cache
        if face_sys.last_result:
            (x1, y1, x2, y2), label, color = face_sys.last_result
            cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                display, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )

        cv2.imshow("Face Recognition", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        if key == ord('r'):
            if face_sys.last_result and face_sys.last_result[1] == "UNKNOWN":
                new_id = face_sys.register_last_face()
                if new_id:
                    face_sys.last_result = (
                        face_sys.last_result[0],
                        f"ID {new_id}",
                        (0, 255, 0)
                    )

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
