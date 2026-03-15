# 🚀 Complete Setup Guide: Face Authorization System with PostgreSQL

## 📋 Overview

Bạn sẽ xây dựng một hệ thống nhận dạng khuôn mặt hoàn chỉnh:

1. **Đăng ký khuôn mặt**: Lưu hình ảnh + embedding vào PostgreSQL
2. **So sánh với database**: Upload ảnh mới, so sánh với tất cả ảnh đã lưu
3. **Quản lý dữ liệu**: CRUD operations cho người dùng

---

## ⚙️ Step 1: Cài Đặt PostgreSQL (Windows)

### 1.1 Download PostgreSQL

1. Truy cập: https://www.postgresql.org/download/windows/
2. Chọn phiên bản **PostgreSQL 15** (hoặc mới hơn)
3. Download installer

### 1.2 Cài Đặt

**Chạy installer:**
```
PostgreSQL Version: 15 (hoặc mới hơn)
Installation Directory: C:\Program Files\PostgreSQL\15
Port: 5432 (mặc định)
Superuser Password: postgres  ← GHI NHỚ PASSWORD NÀY
Locale: [Default locale] 
```

**Hoàn thành installation:**
- Bỏ chọn "Stack Builder" (không cần thiết)
- Click "Finish"

### 1.3 Xác Minh PostgreSQL Đang Chạy

Mở **PowerShell** (Admin):

```powershell
# Kiểm tra service
Get-Service PostgreSQL*

# Output sẽ hiển thị:
# Status   Name
# ------   ----
# Running  postgresql-x64-15
```

Nếu status là **"Stopped"**, bật nó:

```powershell
Start-Service -Name "postgresql-x64-15"
```

---

## 🗄️ Step 2: Tạo Database

Mở **PowerShell** (không cần Admin):

```powershell
# Kết nối với PostgreSQL
psql -U postgres

# Sau khi nhập password "postgres", bạn sẽ thấy:
# psql (15.x)
# Type "help" for help.
# postgres=#
```

Trong psql, chạy:

```sql
CREATE DATABASE face_auth;
\q
```

**Xác minh database được tạo:**

```powershell
psql -U postgres -l

# Bạn sẽ thấy "face_auth" trong danh sách
```

---

## 📦 Step 3: Setup Python Environment

Mở **PowerShell** ở folder project:

```powershell
cd E:\Code\Python\FaceAuthorization\Ai-nh-n-di-n-khu-n-m-tk-main

# Cập nhật pip
python -m pip install --upgrade pip

# Cài dependencies
pip install -r requirements.txt
```

⏳ Quá trình này sẽ mất 3-5 phút (cài InsightFace, FAISS, etc.)

---

## 🗄️ Step 4: Khởi Tạo Database Tables

Vẫn ở folder project:

```powershell
python setup_database.py
```

**Kết quả thành công:**
```
============================================================
Face Authorization Database Setup
============================================================

[1/2] Testing database connection...
✓ Database connection successful!

[2/2] Creating tables...
✓ Tables created successfully!

============================================================
✓ Database setup complete!
============================================================

You can now run: python app.py
```

**Nếu gặp lỗi:**

```
✗ Database connection failed: ...
```

→ Kiểm tra:
1. PostgreSQL đang chạy? `Get-Service PostgreSQL*`
2. Database `face_auth` tồn tại? `psql -U postgres -l`
3. Passwords trong `.env` đúng không?

---

## 🎮 Step 5: Chạy Ứng Dụng

```powershell
python app.py
```

**Kết quả:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

🎉 **Ứng dụng đang chạy!**

---

## 🌐 Step 6: Truy Cập Web UI

Mở trình duyệt:

### A. Face Verification (So sánh 1:1)
```
http://localhost:5000/
```
- Upload 2 ảnh khuôn mặt
- Hệ thống sẽ cho biết có phải cùng 1 người không
- Xem similarity score

### B. Database Manager (Đăng ký + So sánh)
```
http://localhost:5000/database
```

Có 4 tab:

**1️⃣ Register Face Tab**
- Nhập Person ID (ví dụ: `john_doe`)
- Nhập tên người (ví dụ: `John Doe`)
- Upload ảnh khuôn mặt
- Click "Register Face"

**2️⃣ Compare with Database Tab**
- Upload ảnh khuôn mặt để so sánh
- Hệ thống sẽ tìm kiếm trong tất cả ảnh đã lưu
- Hiển thị kết quả match + top candidates

**3️⃣ Registered People Tab**
- Xem danh sách tất cả người đã đăng ký
- Biết số lượng embeddings (ảnh) cho mỗi người
- Xóa người nếu cần

**4️⃣ Statistics Tab**
- Tổng số người đã đăng ký
- Tổng embeddings
- Tổng số comparisons đã thực hiện
- Thống kê khác

---

## 📝 Workflow Ví Dụ

### Workflow 1: Đăng Ký Một Người

1. Truy cập: `http://localhost:5000/database`
2. Chọn tab "Register Face"
3. Nhập:
   - **Person ID**: `alice`
   - **Full Name**: `Alice Johnson`
   - **Face Image**: Chọn ảnh Alice
4. Click "Register Face"
5. Kết quả: ✓ Embedding được lưu vào database

### Workflow 2: Đăng Ký Thêm Một Người

Lặp lại workflow 1 với:
- **Person ID**: `bob`
- **Full Name**: `Bob Smith`
- Chọn ảnh khác của Bob

### Workflow 3: So Sánh Ảnh Mới Với Database

1. Truy cập: `http://localhost:5000/database`
2. Chọn tab "Compare with Database"
3. Upload ảnh khuôn mặt (ảnh mới hoặc của Alice/Bob)
4. Kết quả:
   - Nếu khớp: ✓ MATCH FOUND + tên người + similarity %
   - Nếu không: ✗ NO MATCH + top candidates gần nhất
5. Xem "Top Matches" để biết người nào giống nhất

### Workflow 4: Xem Danh Sách Người

1. Truy cập: `http://localhost:5000/database`
2. Chọn tab "Registered People"
3. Click "Refresh List"
4. Xem:
   - Tên từng người
   - Person ID
   - Số lượng embeddings (ảnh) cho mỗi người
   - Nút "Delete" để xóa

---

## 🧪 Kiểm Tra Hệ Thống (Optional)

Chạy test suite:

```powershell
python test_database_integration.py
```

Nếu tất cả pass, bạn sẽ thấy:
```
============================================================
Results: 6/6 tests passed
============================================================

✓ All tests passed! System is ready to use.
```

---

## 📊 Xem Dữ Liệu PostgreSQL Trực Tiếp

Mở PowerShell:

```powershell
# Kết nối
psql -U postgres -d face_auth

# Xem tất cả người
SELECT person_id, name, num_embeddings FROM persons;

# Xem lịch sử so sánh
SELECT * FROM comparisons ORDER BY created_at DESC LIMIT 10;

# Thoát
\q
```

---

## 🔧 Troubleshooting

### ❌ "Connection refused on 127.0.0.1:5432"

**Nguyên nhân**: PostgreSQL không chạy

**Giải quyết**:
```powershell
Get-Service PostgreSQL*
Start-Service -Name "postgresql-x64-15"  # Thay x64-15 nếu phiên bản khác
```

### ❌ "FATAL: database 'face_auth' does not exist"

**Nguyên nhân**: Database chưa được tạo

**Giải quyết**:
```powershell
psql -U postgres -c "CREATE DATABASE face_auth;"
python setup_database.py
```

### ❌ "FATAL: password authentication failed"

**Nguyên nhân**: Password trong `.env` sai

**Giải quyết**:
1. Mở `.env`
2. Sửa `DB_PASSWORD` thành password bạn đã chọn khi cài PostgreSQL
3. Lưu file
4. Chạy lại `python setup_database.py`

### ❌ "ModuleNotFoundError: No module named 'database'"

**Nguyên nhân**: Dependencies không cài đủ

**Giải quyết**:
```powershell
pip install -r requirements.txt
pip install psycopg2-binary sqlalchemy alembic python-dotenv
```

### ❌ App chạy nhưng database UI không hoạt động

**Nguyên nhân**: Database service không khởi động

**Giải quyết**:
1. Kiểm tra PostgreSQL: `Get-Service PostgreSQL*`
2. Kiểm tra console Flask có error không
3. Chạy `python setup_database.py` lại
4. Restart ứng dụng: Ctrl+C rồi `python app.py`

---

## 📚 Tài Liệu Thêm

- **Database Schema**: Xem `DATABASE_GUIDE.md`
- **API Documentation**: Xem `DATABASE_GUIDE.md` → API Endpoints
- **PostgreSQL Setup Chi Tiết**: Xem `POSTGRESQL_SETUP.md`

---

## 🎯 Bây Giờ Bạn Có Thể:

✅ Đăng ký khuôn mặt (Person + Embedding)
✅ Lưu vào PostgreSQL
✅ So sánh ảnh mới với database
✅ Xem kết quả match/no-match
✅ Quản lý danh sách người
✅ Xem thống kê database

---

## 💡 Hints Sử Dụng

1. **Upload ảnh rõ**: Ảnh rõ sẽ được detect face tốt hơn
2. **Nhiều ảnh cho mỗi người**: Càng nhiều embeddings, match sẽ chính xác hơn
3. **Threshold mặc định**: 0.35 là tốt cho hầu hết trường hợp
4. **Fast mode**: Hệ thống tự dùng fast mode khi so sánh (nhanh hơn 3-4x)

---

**🎉 Chúc mừng! Hệ thống của bạn đã sẵn sàng. Bắt đầu thử ngay!**

Câu hỏi? Kiểm tra lại các troubleshooting steps trên!
