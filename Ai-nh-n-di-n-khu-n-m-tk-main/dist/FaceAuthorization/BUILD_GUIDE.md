# Hướng dẫn Build Face Authorization System thành Executable

## Yêu cầu hệ thống

- Windows 10/11 (64-bit)
- Python 3.8+ (khuyến nghị 3.10 hoặc 3.11)
- 8GB RAM (tối thiểu 4GB)
- 5GB dung lượng ổ đĩa trống

## Các bước build

### 1. Chuẩn bị môi trường

```bash
# Tạo và kích hoạt virtual environment
python -m venv venv
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements-build.txt
```

### 2. Download models

```bash
python download_models.py
```

Script này sẽ tải InsightFace buffalo_l model (~340MB) vào thư mục `models_data/`.

### 3. Build executable

```bash
# Build cơ bản (CPU only)
python build.py

# Build với GPU support (cần CUDA)
python build.py --gpu

# Build và tạo installer
python build.py --installer

# Skip download models (nếu đã có)
python build.py --skip-models
```

### 4. Kết quả build

Sau khi build thành công:
- Executable: `dist/FaceAuthorization/FaceAuthorization.exe`
- Installer (nếu có): `installer/FaceAuthorization_Setup_1.0.0.exe`

## Cấu trúc thư mục sau build

```
dist/FaceAuthorization/
├── FaceAuthorization.exe    # Main executable
├── models_data/             # InsightFace models
│   └── buffalo_l/
│       ├── det_10g.onnx
│       ├── w600k_r50.onnx
│       └── ...
├── templates/               # HTML templates
├── static/                  # CSS, images
├── data/                    # Data directory
├── index/                   # FAISS index
└── [các thư viện .dll/.pyd]
```

## Tạo Installer với Inno Setup

### Yêu cầu
- [Inno Setup 6](https://jrsoftware.org/isdl.php) - Download và cài đặt

### Cách tạo
1. Cài đặt Inno Setup 6
2. Chạy: `python build.py --installer`

   Hoặc thủ công:
   - Mở file `installer.iss` bằng Inno Setup Compiler
   - Nhấn Ctrl+F9 hoặc Build > Compile

### Kết quả
- File installer: `installer/FaceAuthorization_Setup_1.0.0.exe`

## Troubleshooting

### Lỗi "No module named 'xxx'"
```bash
pip install pyinstaller --upgrade
pip install -r requirements-build.txt --force-reinstall
```

### Lỗi model không tìm thấy
Đảm bảo thư mục `models_data/buffalo_l/` chứa các file:
- det_10g.onnx
- w600k_r50.onnx
- 2d106det.onnx
- 1k3d68.onnx
- genderage.onnx

Nếu thiếu, chạy lại: `python download_models.py`

### Lỗi "Failed to load DLL"
Cài đặt Visual C++ Redistributable:
- [VC++ 2019/2022 Redistributable x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Build với GPU (CUDA)
Yêu cầu:
- NVIDIA GPU với CUDA support
- CUDA Toolkit 11.x hoặc 12.x
- cuDNN 8.x hoặc 9.x

```bash
# Cài đặt GPU packages
pip uninstall faiss-cpu onnxruntime
pip install faiss-gpu onnxruntime-gpu

# Build
python build.py --gpu
```

## Cấu hình sau cài đặt

### Database (PostgreSQL)
Nếu sử dụng tính năng database:
1. Cài đặt PostgreSQL
2. Tạo file `.env` trong thư mục cài đặt:
```
DATABASE_URL=postgresql://user:password@localhost:5432/faceauth
FLASK_SECRET_KEY=your-secret-key
```

### Chạy ứng dụng
- Double-click `FaceAuthorization.exe`
- Hoặc chạy từ command line để xem logs

Mặc định ứng dụng chạy tại: http://localhost:5000

## Ghi chú

- File exe đầu tiên chạy có thể mất 10-30 giây để load models
- Các lần chạy sau sẽ nhanh hơn
- Dữ liệu người dùng (embeddings, index) được lưu trong thư mục cài đặt
