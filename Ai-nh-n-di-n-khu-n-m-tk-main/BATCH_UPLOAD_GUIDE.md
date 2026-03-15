# 📁 Batch Upload Guide

Hướng dẫn tải lên hàng loạt ảnh vào hệ thống Face Authorization.

## 🎯 3 Cách Tải Lên

### 1️⃣ **Giao Diện Web (Dễ Nhất)**

Truy cập: **http://localhost:5000/batch-upload**

**Tính năng:**
- ✓ Kéo thả hoặc click chọn ảnh
- ✓ Hiển thị danh sách tập tin
- ✓ Xem tiến độ tải lên real-time
- ✓ Xem nhật ký chi tiết

**Bước:**
1. Mở http://localhost:5000/batch-upload trong trình duyệt
2. Kéo thả ảnh hoặc click chọn folder
3. Click nút "Tải lên"
4. Chờ hoàn thành

### 2️⃣ **Python Script (Dành Cho Batch Lớn)**

```bash
python test_batch_upload.py [folder_path]
```

**Ví dụ:**
```bash
# Tải từ folder hiện tại
python test_batch_upload.py ./my_faces

# Tải từ uploads folder
python test_batch_upload.py uploads
```

**Output mẫu:**
```
📁 Found 100 images to upload
🎯 Uploading to: http://localhost:5000/api/batch_embed

[  1/100] Uploading face1.jpg... ✓ Success (dim: 512)
[  2/100] Uploading face2.jpg... ✓ Success (dim: 512)
[  3/100] Uploading face3.jpg... ✗ Failed (400): File format not supported

======================================================================
✓ SUCCESS: 98/100
✗ FAILED:  2/100
⏱️  TIME:    245.3s (2.5s per image)
======================================================================
```

### 3️⃣ **cURL / HTTP Client**

**Tải lên 1 ảnh:**
```bash
curl -X POST http://localhost:5000/api/batch_embed \
  -F "image=@/path/to/image.jpg"
```

**Response:**
```json
{
  "status": "success",
  "filename": "image.jpg",
  "embedding_dim": 512
}
```

**Tải lên nhiều ảnh với metadata (database):**
```bash
curl -X POST http://localhost:5000/api/batch_register \
  -H "Content-Type: application/json" \
  -d '[
    {
      "person_id": "person_001",
      "name": "John Doe",
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    },
    {
      "person_id": "person_002",
      "name": "Jane Smith",
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]'
```

---

## 📊 API Endpoints

### `POST /api/batch_embed`
Chỉ extract embedding, không lưu vào database.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `image` (required)

**Response:**
```json
{
  "status": "success|error",
  "filename": "string",
  "embedding_dim": 512,
  "error": "string (if failed)"
}
```

### `POST /api/batch_register`
Extract embedding + lưu vào database với metadata.

**Request:**
- Content-Type: `application/json`
- Body: JSON array

```json
[
  {
    "person_id": "unique_id",
    "name": "Person Name",
    "image_base64": "base64_encoded_image"
  }
]
```

**Response:**
```json
{
  "status": "success|partial|error",
  "results": [
    {
      "person_id": "person_001",
      "success": true,
      "message": "✓ John registered successfully"
    },
    {
      "person_id": "person_002",
      "success": false,
      "message": "Error: No face detected"
    }
  ],
  "summary": {
    "total": 2,
    "success": 1,
    "failed": 1
  }
}
```

---

## 📋 Yêu Cầu & Định Dạng

### Định Dạng Hỗ Trợ
- ✓ JPG / JPEG
- ✓ PNG
- ✓ BMP
- ✓ GIF

### Kích Thước
- Mỗi file: Max 16 MB
- Recommended: 1-5 MB per image

### Chất Lượng Ảnh
- **Tối thiểu:** Khuôn mặt >= 50x50 pixels
- **Tối ưu:** Khuôn mặt >= 100x100 pixels
- Hướng mặt: Chính diện hoặc giơ lên một chút
- Ánh sáng: Tốt (tránh quá tối hoặc quá sáng)
- Background: Bất kỳ (không ảnh hưởng)

---

## ⚡ Performance Tips

### Tốc Độ Xử Lý
- ~2-3s per image (CPU)
- ~0.5-1s per image (GPU, nếu có CUDA)

### Để Tải Nhanh Hơn
1. **Giảm độ phân giải ảnh** (resize về 1024px max)
2. **Dùng GPU** (NVIDIA CUDA):
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. **Chạy batch lớn** (100+ ảnh một lúc)

### Nếu Server Quá Tải
- Giảm số ảnh upload cùng lúc
- Tách thành batch nhỏ (50 ảnh mỗi lần)
- Chạy trên server mạnh hơn

---

## 🐛 Troubleshooting

### ❌ "No face detected"
- Ảnh phải có khuôn mặt rõ ràng
- Khuôn mặt phải >= 50x50 pixels
- Thử xoay ảnh hoặc cắt lại

### ❌ "File format not supported"
- Chỉ hỗ trợ: JPG, PNG, BMP, GIF
- Kiểm tra phần mở rộng tập tin

### ❌ "Timeout / Connection refused"
- Đảm bảo Flask server đang chạy
- `python app.py`
- Kiểm tra port 5000 có libre không

### ⚠️ "Database service not available"
- Nếu dùng batch_register: cần PostgreSQL chạy
- Nếu chỉ dùng batch_embed: không cần database

---

## 📝 Metadata File Format

Nếu muốn tải lên 100+ ảnh với thông tin người, tạo `metadata.json`:

```json
[
  {
    "person_id": "emp_001",
    "name": "Alice Johnson",
    "filename": "alice.jpg"
  },
  {
    "person_id": "emp_002",
    "name": "Bob Smith",
    "filename": "bob.jpg"
  },
  {
    "person_id": "emp_003",
    "name": "Carol White",
    "filename": "carol.jpg"
  }
]
```

Sau đó dùng:
```bash
python test_batch_upload.py --metadata metadata.json
```

---

## 🚀 Ví Dụ Thực Tế

### Tải 100 ảnh nhân viên

**Cách 1: Web Interface (đơn giản)**
1. http://localhost:5000/batch-upload
2. Kéo thả folder `employees/`
3. Chọn 100 ảnh → Click Tải lên
4. Chờ ~5 phút

**Cách 2: Script (nhanh + chi tiết)**
```bash
python test_batch_upload.py ./employees
```

**Cách 3: Với metadata (cần database)**
```python
# Tạo metadata.json
# Chạy upload_with_metadata() từ script
```

---

## ✅ Kiểm Tra Kết Quả

Sau khi tải lên, kiểm tra:

```bash
# API health check
curl http://localhost:5000/api/health

# Liệt kê người đã đăng ký
curl http://localhost:5000/api/db/people

# Xem thống kê database
curl http://localhost:5000/api/db/stats
```

---

## 💡 Q&A

**Q: Có thể upload cùng lúc bao nhiêu ảnh?**
A: Không có giới hạn lý thuyết, nhưng tính thực tế ~100-500 ảnh/batch là tối ưu.

**Q: Embedding được lưu ở đâu?**
A: 
- Nếu chỉ dùng `/api/batch_embed`: không lưu (chỉ extract)
- Nếu dùng `/api/batch_register`: lưu vào PostgreSQL database

**Q: Có thể xóa ảnh đã upload không?**
A: Hiện tại không có UI xóa batch. Dùng API:
```bash
curl -X DELETE http://localhost:5000/api/db/person/{person_id}
```

**Q: Thế nào là ảnh "tốt"?**
A: 
- Khuôn mặt rõ ràng, chính diện
- Ánh sáng đủ (không quá tối/sáng)
- Độ phân giải >= 100x100px
- Không bị mờ hoặc tư cách

---

**Need help?** Check logs:
```bash
cat logs/comparison_log.csv  # Lịch sử so sánh
```
