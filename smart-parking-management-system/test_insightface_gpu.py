# -*- coding: utf-8 -*-
"""
test_insightface_gpu.py - Test InsightFace GPU
"""
import cv2
import numpy as np
from insightface.app import FaceAnalysis

print("="*60)
print("TEST INSIGHTFACE GPU")
print("="*60)

# Khoi tao InsightFace
print("\n[1/3] Khoi tao InsightFace buffalo_l...")
try:
    app = FaceAnalysis(
        name='buffalo_l',
        providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
    )
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("[OK] InsightFace da khoi tao thanh cong!")

    # Kiem tra provider dang dung
    if hasattr(app.models, 'recognition'):
        model = app.models['recognition']
        if hasattr(model, 'session'):
            providers = model.session.get_providers()
            print(f"[OK] Providers dang dung: {providers}")

            if 'CUDAExecutionProvider' in providers:
                print("[SUCCESS] InsightFace DANG DUNG GPU!")
            else:
                print("[!] InsightFace dang dung CPU")
    else:
        print("[!] Khong the kiem tra providers")

except Exception as e:
    print(f"[FAIL] Loi khi khoi tao InsightFace: {e}")
    exit(1)

# Tao anh test gia
print("\n[2/3] Tao anh test...")
test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
print("[OK] Da tao anh test 640x480")

# Test nhan dien mat
print("\n[3/3] Test nhan dien mat...")
try:
    import time
    start = time.time()

    # Chay 10 lan de do toc do
    for i in range(10):
        faces = app.get(test_img)

    elapsed = time.time() - start
    fps = 10 / elapsed

    print(f"[OK] Test hoan thanh!")
    print(f"[OK] Thoi gian: {elapsed:.2f}s cho 10 frame")
    print(f"[OK] Toc do: {fps:.1f} FPS")

    if fps > 20:
        print("[SUCCESS] TU TUNG! GPU dang hoat dong tot!")
    elif fps > 10:
        print("[OK] Hieu nang kha, co the GPU dang hoat dong")
    else:
        print("[!] Hieu nang thap, co the van dung CPU")

except Exception as e:
    print(f"[FAIL] Loi khi test: {e}")
    exit(1)

print("\n" + "="*60)
print("TEST HOAN THANH!")
print("="*60)
