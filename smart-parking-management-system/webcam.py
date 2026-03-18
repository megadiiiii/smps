import warnings
warnings.filterwarnings("ignore")

import function.utils_rotate as utils_rotate
import function.helper as helper


import cv2
import torch
import time
import os

# ================== LOAD MODEL ==================
yolo_LP_detect = torch.hub.load(
    'yolov5',
    'custom',
    path='model/LP_detector_nano_61.pt',
    source='local'
)

yolo_LP_ocr = torch.hub.load(
    'yolov5',
    'custom',
    path='model/LP_ocr_nano_62.pt',
    source='local'
)

yolo_LP_ocr.conf = 0.6

# ================== SET CONFIDENCE THRESHOLD CHO DETECTOR ==================
yolo_LP_detect.conf = 0.25  # Hạ threshold để detect dễ hơn

# ================== CAMERA ==================
CAMERA_INDEX = 2  # Đổi thành 1 hoặc 2 nếu camera không mở được
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ================== CHECK CAMERA ==================
if not cap.isOpened():
    print(f"[ERROR] Không mở được camera index {CAMERA_INDEX}. Thử đổi CAMERA_INDEX thành 0, 1, hoặc 2")
    exit(1)
else:
    print(f"[OK] Camera {CAMERA_INDEX} đã mở thành công!")
    print(f"[INFO] LP_detect conf threshold: {yolo_LP_detect.conf}")

SAVE_INTERVAL = 2
last_saved_time = 0

os.makedirs("plates", exist_ok=True)

# ================== MAIN LOOP ==================
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Không đọc được frame từ camera!")
        break

    h0, w0 = frame.shape[:2]

    # ===== Detect =====
    results = yolo_LP_detect(frame, size=640)
    detections = results.xyxy[0]

    # ===== DEBUG LOG =====
    frame_count += 1
    if frame_count % 30 == 0:  # In mỗi 30 frame (~1 giây)
        print(f"[DEBUG] Frame {frame_count}: Detected {len(detections)} biển số")

    for det in detections:
        x1, y1, x2, y2, conf, cls = det.tolist()

        # ✅ YOLOv5 xyxy đã theo ảnh gốc -> chỉ cần int + clamp
        x1 = int(x1);
        y1 = int(y1);
        x2 = int(x2);
        y2 = int(y2)

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w0, x2), min(h0, y2)

        if x2 <= x1 or y2 <= y1:
            continue

        crop = frame[y1:y2, x1:x2]

        # ===== OCR =====
        plate_text = "unknown"
        for cc in range(2):
            for ct in range(2):
                plate_text = helper.read_plate(
                    yolo_LP_ocr,
                    utils_rotate.deskew(crop, cc, ct)
                )
                if plate_text != "unknown":
                    break
            if plate_text != "unknown":
                break

        # ===== DRAW =====
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, plate_text, (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # ===== DRAW =====
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            plate_text,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        # ===== SAVE =====
        if plate_text != "unknown":
            now = time.time()
            if now - last_saved_time >= SAVE_INTERVAL:
                ts = time.strftime("%Y%m%d_%H%M%S")
                filename = f"plates/{plate_text}_{ts}.jpg".replace(" ", "_")
                cv2.imwrite(filename, crop)
                print(f"[OK] {plate_text} -> {filename}")
                last_saved_time = now

    cv2.imshow("License Plate Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ================== CLEAN ==================
cap.release()
cv2.destroyAllWindows()
