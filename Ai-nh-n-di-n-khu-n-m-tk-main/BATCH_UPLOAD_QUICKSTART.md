# 🚀 Quick Start - Batch Upload Feature

Đã thêm tính năng **tải lên hàng loạt ảnh** vào hệ thống Face Authorization!

## 📦 Những Gì Được Thêm

| File | Mục Đích |
|------|----------|
| `templates/batch_upload.html` | Giao diện web tải lên batch (kéo thả, real-time progress) |
| `test_batch_upload.py` | Script Python test/upload từ command line |
| `generate_test_images.py` | Tạo ảnh mẫu để test (50-100 ảnh fake) |
| `BATCH_UPLOAD_GUIDE.md` | Hướng dẫn chi tiết (yêu cầu, troubleshooting, etc.) |
| `app.py` (updated) | Thêm 3 endpoint API mới |

## 🎯 Cách Sử Dụng (3 Lựa Chọn)

### ✨ **OPTION 1: Giao Diện Web (Dễ Nhất)**

```
http://localhost:5000/batch-upload
```

**Làm gì:**
1. Mở link trên trong Chrome/Firefox
2. Kéo thả 100 ảnh vào → hoặc click chọn folder
3. Xem danh sách tập tin
4. Click "Tải lên"
5. Chờ xem tiến độ real-time
6. Xem kết quả (success/failed count)

✅ Lợi ích: Dễ dùng, không cần terminal, giao diện đẹp

---

### 💻 **OPTION 2: Python Script (Cho Batch Lớn)**

```bash
# Đơn giản nhất
python test_batch_upload.py uploads

# Hoặc chỉ định folder
python test_batch_upload.py ./my_faces

# Với metadata (cần PostgreSQL)
python test_batch_upload.py --metadata metadata.json
```

**Ví dụ output:**
```
📁 Found 100 images to upload
[  1/100] face_001.jpg... ✓ Success (dim: 512)
[  2/100] face_002.jpg... ✓ Success (dim: 512)
[100/100] face_100.jpg... ✓ Success (dim: 512)

======================================================================
✓ SUCCESS: 99/100
✗ FAILED:  1/100
⏱️  TIME:    245s (2.5s per image)
======================================================================
```

✅ Lợi ích: Nhanh, chi tiết log, support batch metadata

---

### 🔧 **OPTION 3: cURL / HTTP API (Cho Integration)**

**1 ảnh:**
```bash
curl -X POST http://localhost:5000/api/batch_embed \
  -F "image=@face.jpg"
```

**Nhiều ảnh với metadata:**
```bash
curl -X POST http://localhost:5000/api/batch_register \
  -H "Content-Type: application/json" \
  -d '[
    {"person_id": "p1", "name": "Alice", "image_base64": "..."},
    {"person_id": "p2", "name": "Bob", "image_base64": "..."}
  ]'
```

✅ Lợi ích: Tích hợp vào hệ thống khác, automatable

---

## 🏃 Quick Test (Chạy Ngay Bây Giờ)

**Bước 1: Tạo 50 ảnh mẫu**
```bash
python generate_test_images.py --count 50 --output test_faces
```

**Bước 2: Tải lên**

*Cách A (Web):*
```
http://localhost:5000/batch-upload
→ kéo thả folder test_faces
→ click Tải lên
```

*Cách B (Script):*
```bash
python test_batch_upload.py test_faces
```

**Bước 3: Xem kết quả**
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/db/stats  # nếu có DB
```

---

## 📊 3 API Endpoints

### 1. `/api/batch_embed` (Chỉ extract)
```
POST /api/batch_embed
Content-Type: multipart/form-data
Body: image file

Response: {status, filename, embedding_dim}
```
✅ Không cần database, chỉ extract embedding

### 2. `/api/batch_register` (Extract + lưu DB)
```
POST /api/batch_register
Content-Type: application/json
Body: [{person_id, name, image_base64}, ...]

Response: {status, results, summary}
```
✅ Cần PostgreSQL, lưu metadata + embedding

### 3. `/batch-upload` (Giao diện web)
```
GET /batch-upload
→ HTML form với drag-drop + progress bar
```
✅ Gọi /api/batch_embed backend

---

## ⚡ Performance

| Tốc độ | Thiết Bị | Ghi Chú |
|--------|---------|--------|
| 2-3s/ảnh | CPU | Standard (đủ tốt) |
| 0.5-1s/ảnh | GPU | Cần CUDA/PyTorch |

**100 ảnh:**
- CPU: ~4-5 phút ✓
- GPU: ~1-1.5 phút ✓✓

---

## 🎁 Bonus Features

✅ Progress tracking real-time
✅ Drag-drop UI
✅ Error handling (detailed log)
✅ Batch metadata support
✅ Database integration (optional)
✅ Image validation
✅ Timeout handling

---

## 📝 File Structure

```
├── app.py (+ 3 new endpoints)
├── templates/
│   ├── batch_upload.html (NEW)
│   ├── index.html (existing)
│   └── database.html (existing)
├── test_batch_upload.py (NEW)
├── generate_test_images.py (NEW)
├── BATCH_UPLOAD_GUIDE.md (NEW - detailed docs)
└── BATCH_UPLOAD_QUICKSTART.md (THIS FILE)
```

---

## 🔗 Links

- 🌐 **Web Interface:** http://localhost:5000/batch-upload
- 📚 **Detailed Guide:** `BATCH_UPLOAD_GUIDE.md`
- 📺 **Test Script:** `test_batch_upload.py`
- 🎨 **Generate Test Images:** `python generate_test_images.py`

---

## ❓ FAQ

**Q: Chạy được ngay không?**
A: ✅ Có! `python app.py` rồi vào http://localhost:5000/batch-upload

**Q: 100 ảnh mất bao lâu?**
A: ~4-5 phút (CPU) hoặc 1-2 phút (GPU)

**Q: Có giới hạn số ảnh?**
A: Không, nhưng ~100-500/batch là tối ưu

**Q: Database bắt buộc không?**
A: ❌ Không. `/api/batch_embed` chỉ extract, không cần DB

**Q: Muốn test với ảnh thật?**
A: Download từ: http://thispersondoesnotexist.com (1000s ảnh AI-generated)

---

## 📞 Support

Nếu có lỗi:
1. Kiểm tra `logs/` folder
2. Xem `BATCH_UPLOAD_GUIDE.md` phần Troubleshooting
3. Chạy `curl http://localhost:5000/api/health` để kiểm tra server

---

**Ready to upload?** 🚀 Go to http://localhost:5000/batch-upload
