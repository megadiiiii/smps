# Smart Parking Management System (SPMS)

Hệ thống quản lý bãi đỗ xe thông minh ứng dụng **Computer Vision** và **AI** để tự động nhận diện phương tiện, quản lý ra/vào, và xác thực danh tính.

---

## ✨ Tính năng chính

- **Đăng nhập người dùng** - Phân quyền Admin/Nhân viên
- **Nhận diện khuôn mặt** - Sử dụng InsightFace với độ chính xác cao
- **Nhận diện biển số xe** - YOLOv5 + OCR
- **Xác thực Vào/Ra** - So sánh khuôn mặt để kiểm tra danh tính
- **Quản lý bãi đỗ** - Theo dõi trạng thái xe (Vào/Ra)
- **Xem lịch sử** - Lịch ra/vào phương tiện
- **Chế độ Dev Mode** - Upload ảnh test thay vì dùng camera (tùy chọn)

---

## 🚀 Cài đặt nhanh

### Với Embedded Python Distribution

**Không cần cài Python! Mọi thứ đã sẵn sàng.**

```bash
# 1. Chạy launcher (cách dễ nhất)
python launcher.py

# Hoặc: Chạy batch script
run_parking.bat

# Hoặc: Chạy trực tiếp (yêu cầu Python embedded trong thư mục python/)
python\python.exe login.py
```

### Với Hệ thống Python được cài sẵn

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Chạy ứng dụng
python login.py
```

---

## 📋 Yêu cầu hệ thống

**Với Embedded Distribution:**
- Windows 10 / 11 (64-bit)
- 4 GB RAM (8 GB khuyến nghị)
- 3-4 GB dung lượng ổ cứng
- **Không cần cài Python**

**Với Hệ thống Python:**
- Python 3.10+
- Windows 10 / 11 (64-bit)
- Các thư viện trong `requirements.txt`

**Tùy chọn (nếu có GPU):**
- NVIDIA GPU + CUDA 11.x + cuDNN 8.x (tăng tốc xử lý)

---

## 🔐 Thông tin đăng nhập

| Tài khoản | Username | Password | Quyền |
|-----------|----------|----------|-------|
| Admin | `admin` | `admin` | Quản lý toàn hệ thống |
| Nhân viên | `user` | `user` | Thực thi ra/vào |

---

## 📁 Cấu trúc thư mục

```
smart-parking-management-system/
├── login.py                    # Điểm khởi động
├── launcher.py                 # Launcher Python (khuyến nghị)
├── run_parking.bat             # Launcher Batch
├── requirements.txt            # Dependencies
├── db.py                       # Cấu hình database
├── models/                     # Yolo, Face, Plate models
├── modules/                    # Core modules (detector, recognizer)
├── ui/                         # Giao diện PyQt6
├── yolov5/                     # YOLOv5 framework
├── result/                     # Kết quả xử lý ảnh (tự tạo)
│   ├── face/                   # Ảnh mặt đã cắt
│   ├── plate/                  # Ảnh biển đã cắt
│   └── fullface/               # Ảnh mặt đầy đủ
├── test_images/                # Ảnh test (tùy chọn)
└── README.md                   # File này

../Ai-nh-n-di-n-khu-n-m-tk-main/   # Face comparison module
├── face_comparison.py          # So sánh mặt 1:1 và 1:N
├── models/                     # Model face embedding
└── modules/                    # Face detector & embedder
```

---

## 🎮 Hướng dẫn sử dụng

### Bước 1: Khởi động ứng dụng
```bash
python launcher.py
```

### Bước 2: Đăng nhập
- **Admin**: Username `admin`, Password `admin`
- **Nhân viên**: Username `user`, Password `user`

### Bước 3: Thực thi ra/vào

#### Với Camera thực:
1. Bật camera
2. Nhấn **"Chụp mặt (Cam1)"** hoặc phím `1` để chụp khuôn mặt
3. Nhấn **"Chụp biển (Cam2)"** hoặc phím `2` để chụp biển số
4. Hệ thống tự động xác thực và lưu vào database

#### Với Chế độ Dev Mode (upload ảnh):
1. Tích **"🔧 Chế độ Dev Mode (Upload ảnh)"**
2. Nhấn **"📁 Nạp ảnh (Dev)"** hoặc kéo thả ảnh vào
3. Nhấn phím `1` (mặt) hoặc `2` (biển) để xử lý

### Bước 4: Xem lịch sử (nếu có quyền Admin)
- Vào Trang **Quản lý** để xem đầy đủ lịch sử

---

## ⌨️ Phím tắt

| Phím | Chức năng |
|------|----------|
| `1` | Chụp mặt (Camera 1) |
| `2` | Chụp biển (Camera 2) |
| `0` | Reset panels |
| `Alt+1` | Load ảnh cho Camera 1 (Dev Mode) |
| `Alt+2` | Load ảnh cho Camera 2 (Dev Mode) |
| `Ctrl+L` | Đăng xuất |
| `Ctrl+R` | Reset giao diện |

---

## 🔧 Cài đặt nâng cao

### Thay đổi database
Sửa file `db.py`:
```python
DATABASE = 'parking.db'  # Đặt đường dẫn hoặc tên database khác
```

### Chế độ GPU (nếu có)
CUDA sẽ tự động được sử dụng nếu có. Kiểm tra:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Thay đổi ngưỡng so sánh mặt
Sửa `login.py` hoặc `config.py`:
```python
FACE_SIMILARITY_THRESHOLD = 0.40  # Điều chỉnh độ nhạy (0.0-1.0)
```

---

## 📊 Dữ liệu & Database

Ứng dụng sử dụng **SQLite** (`parking.db`). Dữ liệu bảo gồm:
- **Lịch ra/vào**: Thời gian, biển số, mặt của người, trạng thái
- **Ảnh**: Lưu tại thư mục `result/`

---

## ⚠️ Lưu ý quan trọng

1. **Cần camera**: Sử dụng camera USB hoặc webcam tích hợp
2. **Điều kiện ánh sáng**: Chất lượng nhận diện tùy thuộc vào điều kiện ánh sáng
3. **Chất lượng ảnh**: Hình ảnh mặt rõ nét tăng độ chính xác
4. **GPU tùy chọn**: Ngay cả không có GPU cũng hoạt động, chỉ chậm hơn
5. **Quyền Administrator**: Cần cho một số quá trình cài đặt lần đầu

---

## 🐛 Troubleshooting

| Vấn đề | Giải pháp |
|-------|----------|
| Camera không hoạt động | Kiểm tra cổng USB, cấp quyền camera trong System Settings |
| Nhận diện khuôn mặt thất bại | Cải thiện điều kiện ánh sáng, chụp lại |
| Nhận diện biển số sai | Thực hiện nhập thủ công biển số |
| Ứng dụng chạy chậm | Nâng cấp RAM, sử dụng GPU nếu có, giảm độ phân giải camera |
| Database error | Xóa `parking.db` (mất dữ liệu cũ), chạy lại ứng dụng |

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra terminal/console để xem chi tiết lỗi
2. Xem các `.log` files trong thư mục ứng dụng
3. Thử chế độ Dev Mode để test mà không cần camera

---

## 📄 License & Ghi nhận

Dự án fork từ: [License-Plate-Recognition](https://github.com/trungdinh22/License-Plate-Recognition)

**Công nghệ sử dụng:**
- PyQt6 - Giao diện trên nền tảng Python
- YOLOv5 - Nhận diện biển số
- InsightFace - Nhận diện và so sánh khuôn mặt
- OpenCV - Xử lý ảnh
- SQLite - Cơ sở dữ liệu
- NumPy/OpenCV - Tính toán toán học

---

**Phiên bản:** 1.0.0
**Cập nhật lần cuối:** 2026-03-18
