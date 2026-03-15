# PostgreSQL Setup Guide for Face Authorization System

## 📋 Prerequisites

- Windows 10/11
- PostgreSQL 14 hoặc mới hơn
- Python 3.8+

## 🚀 Quick Setup

### Step 1: Install PostgreSQL

1. Download PostgreSQL từ https://www.postgresql.org/download/windows/
2. Chạy installer với các settings mặc định:
   - **Username**: `postgres`
   - **Password**: `postgres` (hoặc ghi nhớ password của bạn)
   - **Port**: `5432`
3. Hoàn thành installation

### Step 2: Verify PostgreSQL is Running

```powershell
# PowerShell
Get-Service PostgreSQL*
```

Bạn sẽ thấy một service như `postgresql-x64-15` với status `Running`

### Step 3: Create Database

```powershell
# PowerShell - Mở Command Prompt as Administrator
psql -U postgres -c "CREATE DATABASE face_auth;"
```

Hoặc sử dụng pgAdmin GUI (được cài kèm PostgreSQL)

### Step 4: Update .env (nếu cần)

Mở `.env` và cập nhật credentials:

```env
DB_USER=postgres
DB_PASSWORD=postgres        # Thay bằng password bạn đã chọn
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_auth
```

### Step 5: Run Setup Script

```powershell
cd E:\Code\Python\FaceAuthorization\Ai-nh-n-di-n-khu-n-m-tk-main
python setup_database.py
```

Nếu thành công, bạn sẽ thấy:
```
✓ Database connection successful!
✓ Tables created successfully!
✓ Database setup complete!
```

### Step 6: Start the Application

```powershell
python app.py
```

Truy cập: http://localhost:5000

---

## 🔧 Database Commands

### Connect to Database

```powershell
psql -U postgres -d face_auth
```

### Useful psql Commands

```sql
-- List all tables
\dt

-- Show table structure
\d persons
\d embeddings
\d comparisons

-- View data
SELECT * FROM persons;
SELECT COUNT(*) FROM embeddings;

-- Exit
\q
```

### Reset Database (⚠️ Deletes all data)

```powershell
python -c "from database.config import drop_tables; drop_tables(); print('Database reset!')"
```

---

## 📊 Database Schema

### persons
```sql
id (UUID) - Primary key
person_id (String, unique) - User-facing ID
name (String) - Person's name
created_at (DateTime)
updated_at (DateTime)
```

### embeddings
```sql
id (UUID) - Primary key
person_id (UUID) - Foreign key to persons
embedding (Float array) - 512-dimensional vector
image_path (String) - Path to source image
created_at (DateTime)
```

### comparisons
```sql
id (UUID) - Primary key
person_id (UUID) - Matched person (nullable)
similarity_score (Float) - 0.0 to 1.0
is_match (Boolean) - Whether match exceeded threshold
threshold (Float) - Threshold used
created_at (DateTime)
notes (Text) - Additional context
```

---

## 🐛 Troubleshooting

### "Connection refused on 127.0.0.1:5432"

**Solution**: PostgreSQL is not running
```powershell
# Check service status
Get-Service PostgreSQL*

# Start the service
Start-Service -Name "postgresql-x64-15"  # Replace with your version
```

### "FATAL: database 'face_auth' does not exist"

**Solution**: Create the database
```powershell
psql -U postgres -c "CREATE DATABASE face_auth;"
```

### "FATAL: role 'postgres' does not exist"

**Solution**: Reinstall PostgreSQL or check the username (use `postgres` as default)

### Connection string not working

Check `.env`:
- Ensure `DB_HOST=localhost` (not 127.0.0.1 sometimes causes issues on Windows)
- Verify `DB_PORT=5432`
- Confirm database name with `psql -l`

---

## 🎯 API Endpoints for Database Operations

After setup, these endpoints are available:

### Register a Face
```bash
POST /api/db/register-face
Content-Type: multipart/form-data

person_id=john_doe&name=John%20Doe&image=<file>
```

### Compare with Database
```bash
POST /api/db/compare
Content-Type: multipart/form-data

image=<file>
```

### List All People
```bash
GET /api/db/people
```

### Get Person Details
```bash
GET /api/db/person/<person_id>
```

### Delete Person
```bash
DELETE /api/db/person/<person_id>
```

### Database Statistics
```bash
GET /api/db/stats
```

---

## ✅ Next Steps

1. Run `python setup_database.py` to initialize database
2. Start the app: `python app.py`
3. Test the endpoints using the web UI or cURL commands above
4. Register some faces and test comparison

Good luck! 🚀
