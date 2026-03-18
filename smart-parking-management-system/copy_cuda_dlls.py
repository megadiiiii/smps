"""
copy_cuda_dlls.py - Copy CUDA DLL from PyTorch to ONNX Runtime
"""
import os
import shutil
import torch
import onnxruntime

# Thu muc nguon (PyTorch)
torch_lib = os.path.join(os.path.dirname(torch.__file__), 'lib')

# Thu muc dich (ONNX Runtime)
onnx_capi = os.path.join(os.path.dirname(onnxruntime.__file__), 'capi')

print(f"Nguon: {torch_lib}")
print(f"Dich: {onnx_capi}")
print()

# Danh sach file can copy
dll_files = [
    'cublasLt64_12.dll',
    'cublas64_12.dll',
    'cudart64_12.dll',
    'cudnn64_9.dll',
    'cudnn_ops64_9.dll',
    'cudnn_cnn64_9.dll',
]

# Copy files
copied = 0
for dll in dll_files:
    src = os.path.join(torch_lib, dll)
    dst = os.path.join(onnx_capi, dll)

    if os.path.exists(src):
        try:
            shutil.copy2(src, dst)
            print(f"[OK] Copy: {dll}")
            copied += 1
        except Exception as e:
            print(f"[FAIL] Loi khi copy {dll}: {e}")
    else:
        print(f"[SKIP] Khong tim thay: {dll}")

print()

# Tao compatibility files cho cuDNN v8
compat_files = [
    ('cudnn64_9.dll', 'cudnn64_8.dll'),
    ('cudnn_ops64_9.dll', 'cudnn_ops64_8.dll'),
    ('cudnn_cnn64_9.dll', 'cudnn_cnn64_8.dll'),
]

for src_name, dst_name in compat_files:
    src = os.path.join(onnx_capi, src_name)
    dst = os.path.join(onnx_capi, dst_name)

    if os.path.exists(src):
        try:
            shutil.copy2(src, dst)
            print(f"[OK] Tao compat: {dst_name}")
            copied += 1
        except Exception as e:
            print(f"[FAIL] Loi khi tao {dst_name}: {e}")

print()
print(f"Tong cong da copy: {copied} files")
print("\nChay 'python check_gpu.py' de kiem tra!")
