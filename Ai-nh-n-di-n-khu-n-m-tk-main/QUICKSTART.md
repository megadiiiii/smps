# 🎭 Face Authorization System - Quick Start

## ⚡ 3-Step Startup (10 minutes)

### Step 1️⃣: Install PostgreSQL
- Download: https://www.postgresql.org/download/windows/
- Use defaults (user: `postgres`, password: `postgres`, port: `5432`)
- Verify: `Get-Service PostgreSQL*` in PowerShell

### Step 2️⃣: Create Database & Install Dependencies
```powershell
# Create database
psql -U postgres -c "CREATE DATABASE face_auth;"

# Install Python packages
pip install -r requirements.txt

# Initialize database tables
python setup_database.py
```

✅ Should see: `✓ Database setup complete!`

### Step 3️⃣: Run Application
```powershell
python app.py
```

Open browser: **http://localhost:5000/database**

---

## 🎮 What You Can Do

1. **Register Face Tab**
   - Person ID: `john_doe`
   - Name: `John Doe`
   - Upload face photo
   - Click "Register Face" ✓

2. **Compare Tab**
   - Upload face image
   - System searches database
   - Shows match + top candidates

3. **People Tab**
   - See all registered faces
   - Delete if needed

4. **Statistics Tab**
   - View database stats

---

## 🔗 Important Files

| File | Purpose |
|------|---------|
| `SETUP_COMPLETE.md` | Detailed Vietnamese guide |
| `DATABASE_GUIDE.md` | Full API documentation |
| `POSTGRESQL_SETUP.md` | PostgreSQL setup troubleshooting |

---

## 🚨 Troubleshooting

**❌ "Connection refused" or "database does not exist"**
→ Run: `python setup_database.py`

**❌ "ModuleNotFoundError"**
→ Run: `pip install -r requirements.txt`

**❌ PostgreSQL not running**
→ Run: `Start-Service -Name "postgresql-x64-15"`

---

## 📊 Architecture

```
Upload Image 1
     ↓
Face Detection (InsightFace)
     ↓
Extract Embedding (512-dim vector)
     ↓
PostgreSQL Database
     ↓
Compare with other embeddings
     ↓
Return Match Results
```

---

## 🎯 API Examples

```bash
# Register face
curl -X POST http://localhost:5000/api/db/register-face \
  -F person_id=alice -F name="Alice" -F image=@photo.jpg

# Compare with database
curl -X POST http://localhost:5000/api/db/compare \
  -F image=@test.jpg

# Get statistics
curl http://localhost:5000/api/db/stats

# List all people
curl http://localhost:5000/api/db/people
```

---

## ✨ New Features Added

✅ PostgreSQL database integration
✅ Register & save face embeddings
✅ Compare against database
✅ Web UI for management (database.html)
✅ REST API endpoints
✅ Statistics & reporting
✅ Audit trail (comparison history)

---

**Ready to go! 🚀 Start with `python app.py`**

For help, see: `SETUP_COMPLETE.md` (Vietnamese) or `DATABASE_GUIDE.md` (English)
