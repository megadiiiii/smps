# -*- coding: utf-8 -*-
"""
check_gpu.py - Kiem tra GPU va CUDA cho Face Recognition
"""
import os
import sys

def check_gpu():
    print("="*60)
    print("KIEM TRA CAU HINH GPU CHO FACE RECOGNITION")
    print("="*60)

    # 1. Kiem tra CUDA co san khong (qua PyTorch)
    print("\n[1/5] Kiem tra PyTorch CUDA...")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"  [OK] PyTorch CUDA co san: {torch.version.cuda}")
            print(f"  [OK] GPU phat hien: {torch.cuda.get_device_name(0)}")
            print(f"  [OK] So luong GPU: {torch.cuda.device_count()}")
        else:
            print("  [!] PyTorch KHONG phat hien CUDA")
            print("    (Co the ban cai pytorch CPU-only)")
    except ImportError:
        print("  [!] PyTorch chua duoc cai dat")
    except Exception as e:
        print(f"  [!] Loi khi kiem tra PyTorch: {e}")

    # 2. Kiem tra ONNX Runtime providers
    print("\n[2/5] Kiem tra ONNX Runtime providers...")
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        print(f"  [OK] ONNX Runtime version: {ort.__version__}")
        print(f"  [OK] Providers co san: {providers}")

        if "CUDAExecutionProvider" in providers:
            print("  [SUCCESS] CUDAExecutionProvider CO SAN - GPU se duoc dung!")
        else:
            print("  [FAIL] CUDAExecutionProvider KHONG CO - Chi dung CPU")
            print("     -> Nguyen nhan: Thieu CUDA/cuDNN hoac cai onnxruntime CPU-only")
    except ImportError:
        print("  [FAIL] ONNX Runtime chua duoc cai dat")
        print("     -> Chay: pip install onnxruntime-gpu==1.23.2")
    except Exception as e:
        print(f"  [!] Loi khi kiem tra ONNX Runtime: {e}")

    # 3. Kiem tra file DLL can thiet (Windows)
    print("\n[3/5] Kiem tra file CUDA/cuDNN DLL...")
    if sys.platform == "win32":
        try:
            import onnxruntime
            ort_dir = os.path.dirname(onnxruntime.__file__)
            capi_dir = os.path.join(ort_dir, "capi")

            required_dlls = [
                "cublasLt64_12.dll",
                "cublas64_12.dll",
                "cudart64_12.dll",
                "cudnn64_8.dll",
            ]

            missing_dlls = []
            for dll in required_dlls:
                dll_path = os.path.join(capi_dir, dll)
                if os.path.exists(dll_path):
                    print(f"  [OK] {dll}")
                else:
                    print(f"  [FAIL] {dll} - THIEU")
                    missing_dlls.append(dll)

            if missing_dlls:
                print("\n  [!] CO FILE DLL BI THIEU!")
                print("     -> Doc GPU_SETUP.md de cai dat cuDNN")
            else:
                print("\n  [SUCCESS] Tat ca file DLL can thiet da co!")

        except Exception as e:
            print(f"  [!] Khong the kiem tra DLL: {e}")
    else:
        print("  [i] He dieu hanh khong phai Windows, bo qua kiem tra DLL")

    # 4. Kiem tra FAISS
    print("\n[4/5] Kiem tra FAISS...")
    try:
        import faiss
        print(f"  [OK] FAISS version: {faiss.__version__}")

        # Thu tao index tren GPU
        try:
            res = faiss.StandardGpuResources()
            index_flat = faiss.IndexFlatL2(128)
            gpu_index = faiss.index_cpu_to_gpu(res, 0, index_flat)
            print("  [SUCCESS] FAISS GPU co san va hoat dong!")
        except Exception as e:
            print(f"  [!] FAISS chi dung CPU: {e}")
            print("     -> De dung FAISS GPU: pip uninstall faiss-cpu -y && pip install faiss-gpu")
    except ImportError:
        print("  [!] FAISS chua duoc cai dat")
    except Exception as e:
        print(f"  [!] Loi khi kiem tra FAISS: {e}")

    # 5. Kiem tra InsightFace
    print("\n[5/5] Kiem tra InsightFace...")
    try:
        import insightface
        print(f"  [OK] InsightFace version: {insightface.__version__}")

        # Thu khoi tao model voi CUDA
        try:
            import onnxruntime as ort
            if "CUDAExecutionProvider" in ort.get_available_providers():
                print("  [SUCCESS] InsightFace co the dung GPU qua ONNX Runtime")
            else:
                print("  [!] InsightFace se dung CPU (CUDA provider khong co)")
        except Exception as e:
            print(f"  [!] Khong the kiem tra InsightFace providers: {e}")

    except ImportError:
        print("  [!] InsightFace chua duoc cai dat")
    except Exception as e:
        print(f"  [!] Loi khi kiem tra InsightFace: {e}")

    # Tong ket
    print("\n" + "="*60)
    print("TONG KET")
    print("="*60)

    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()

        if "CUDAExecutionProvider" in providers:
            print("[SUCCESS] HE THONG DA SAN SANG DUNG GPU!")
            print("   -> Face recognition se chay tren GPU")
            print("   -> Hieu nang du kien: 30-50 FPS")
        else:
            print("[FAIL] HE THONG DANG DUNG CPU")
            print("   -> Hieu nang bi gioi han: 5-10 FPS")
            print("   -> Doc GPU_SETUP.md de kich hoat GPU")

            # Goi y fix
            print("\nCACH KHAC PHUC:")
            print("   1. Cai cuDNN v8.9 cho CUDA 12.x")
            print("   2. Copy file *.dll vao thu muc onnxruntime/capi")
            print("   3. Chay lai script nay de kiem tra")
            print("\n   Chi tiet: Xem file GPU_SETUP.md")
    except:
        print("[?] KHONG THE XAC DINH TRANG THAI GPU")
        print("   -> Cai dat: pip install onnxruntime-gpu==1.23.2")

    print("="*60)


if __name__ == "__main__":
    check_gpu()
