# 🎭 Face Authorization System with PostgreSQL

A comprehensive face recognition system built with Flask, InsightFace, and PostgreSQL.

## ✨ Features

### 1. **Face Verification (1:1 Comparison)**
- Upload two images and verify if they belong to the same person
- Real-time similarity scoring with visual feedback
- Configurable similarity threshold
- Support for multiple face detection strategies

### 2. **Face Database Management**
- **Register**: Save face embeddings for multiple people in PostgreSQL
- **Search**: Compare a face against all registered faces in the database
- **List**: View all registered people and their statistics
- **Delete**: Remove persons and their data from the database

### 3. **Face Recognition Pipeline**
- Automatic face detection (InsightFace)
- 512-dimensional embedding extraction
- Cosine similarity-based comparison
- Fast mode support for real-time applications

## 🏗️ Architecture

```
├── app.py                          # Flask application
├── config.py                       # Configuration constants
├── requirements.txt                # Python dependencies
│
├── database/
│   ├── config.py                  # PostgreSQL connection & ORM setup
│   ├── models.py                  # SQLAlchemy models (Person, Embedding, Comparison)
│   └── face_db.py                 # Legacy JSON-based database
│
├── modules/
│   ├── face_detector.py           # Face detection (InsightFace)
│   ├── face_embedder.py           # Face embedding generation
│   ├── comparator.py              # Similarity comparison
│   ├── logger.py                  # Logging utilities
│   └── utils.py                   # Helper functions
│
├── services/
│   ├── database_service.py        # ✨ NEW: PostgreSQL CRUD operations
│   ├── vector_search_service.py   # ✨ NEW: Embedding search & comparison
│   ├── face_service.py            # High-level face operations
│   ├── embedding_service.py       # Embedding management
│   └── search_service.py          # FAISS-based search (legacy)
│
├── templates/
│   ├── index.html                 # Face verification UI
│   └── database.html              # ✨ NEW: Database management UI
│
└── .env                           # Environment variables (DATABASE_URL, credentials, etc.)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 14+ (running)
- 2GB+ RAM recommended

### Step 1: Install Python Dependencies

```bash
cd E:\Code\Python\FaceAuthorization\Ai-nh-n-di-n-khu-n-m-tk-main
pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL

Follow the detailed guide: [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)

Or quickly:
```bash
# Create database (if not exists)
psql -U postgres -c "CREATE DATABASE face_auth;"

# Initialize tables
python setup_database.py
```

### Step 3: Start the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## 📱 Web Interface

### Homepage: Face Verification (`/`)
- Upload two face images
- Get instant match/no-match result
- See similarity score and threshold

### Database Manager (`/database`)
- **Register Face Tab**: Register new person with their face
- **Compare Tab**: Compare a face against database
- **People Tab**: View all registered people
- **Stats Tab**: Database statistics

## 🔌 API Endpoints

### Verification (1:1)
```
POST /verify
  image1: file
  image2: file
  threshold?: float (default 0.25)
  multi_face?: "error" | "largest" (default "largest")
→ { match: bool, score: float, result: string, error?: string }
```

### Database Management
```
POST /api/db/register-face
  person_id: string
  name: string
  image: file
→ { status: "success", embedding_id: uuid, message: string }

POST /api/db/compare
  image: file
  threshold?: float (default 0.35)
→ { match: bool, person_id?: string, similarity: float, top_matches: [...] }

GET /api/db/people
→ { people: [...], total: int }

GET /api/db/person/<person_id>
→ { person: { person_id, name, num_embeddings, created_at, updated_at } }

DELETE /api/db/person/<person_id>
→ { status: "success", message: string }

GET /api/db/stats
→ { stats: { total_persons, total_embeddings, total_comparisons, avg_embeddings_per_person } }
```

## 📊 Database Schema

### persons
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| person_id | String (unique) | User-facing identifier |
| name | String | Person's name |
| created_at | DateTime | Registration timestamp |
| updated_at | DateTime | Last update timestamp |

### embeddings
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| person_id | UUID | FK to persons |
| embedding | Float[] | 512-dimensional vector |
| image_path | String | Source image path |
| created_at | DateTime | Timestamp |

### comparisons
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| person_id | UUID | FK to persons (matched) |
| similarity_score | Float | 0.0 to 1.0 |
| is_match | Boolean | Exceeded threshold? |
| threshold | Float | Threshold used |
| created_at | DateTime | Timestamp |
| notes | Text | Additional context |

## ⚙️ Configuration

Edit `.env` to customize:

```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_auth

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# Face Recognition
RECOGNITION_THRESHOLD=0.35        # Similarity threshold for matching
FACE_DETECTION_THRESHOLD=0.5      # Detection confidence threshold
```

## 🔧 Common Tasks

### Check Database Connection
```bash
python -c "from database.config import engine; print(engine.execute('SELECT 1'))"
```

### Reset Database (⚠️ Deletes all data)
```bash
python -c "from database.config import drop_tables; drop_tables(); print('Reset complete')"
```

### View Database Contents
```bash
psql -U postgres -d face_auth

# List all people
SELECT * FROM persons;

# Count embeddings
SELECT person_id, COUNT(*) FROM embeddings GROUP BY person_id;

# View comparisons
SELECT * FROM comparisons ORDER BY created_at DESC LIMIT 10;
```

### Export Database to CSV
```bash
psql -U postgres -d face_auth -c "COPY persons TO STDOUT CSV HEADER" > persons.csv
psql -U postgres -d face_auth -c "COPY comparisons TO STDOUT CSV HEADER" > comparisons.csv
```

## 📈 Performance Notes

- **Embedding generation**: ~50-100ms per image (CPU)
- **Database search**: ~10-50ms for 100 registered people
- **Comparison**: Instant (in-memory cosine similarity)
- **Concurrency**: SQLAlchemy connection pooling handles up to 10 concurrent requests

## 🐛 Troubleshooting

### "Connection refused on port 5432"
- PostgreSQL is not running
- Check: `Get-Service PostgreSQL*` (PowerShell)
- Start: `Start-Service -Name "postgresql-x64-15"`

### "Database face_auth does not exist"
- Run: `psql -U postgres -c "CREATE DATABASE face_auth;"`

### "No module named 'database.models'"
- Reinstall dependencies: `pip install -r requirements.txt`

### "Embedding dimensions don't match"
- All embeddings must be 512-dimensional (InsightFace standard)
- Check configuration in `config.py`

## 📚 Project Structure Explanation

**Why PostgreSQL?**
- Persistent storage across restarts
- SQL queries for analytics
- ARRAY type for vectors
- Better for multi-user scenarios

**Why Cosine Similarity?**
- Industry standard for embedding comparison
- Values in [-1, 1], normalized similarity
- Computationally efficient
- Works well with normalized embeddings

**Why InsightFace?**
- State-of-the-art face detection & embedding
- Multiple model options (Buffalo, ArcFace)
- Fast and accurate
- Open-source

## 🔒 Security Notes

- Never commit `.env` with real credentials
- Use strong PostgreSQL passwords in production
- Validate file uploads (MIME type, size)
- HTTPS recommended for production
- Rate limiting recommended for API endpoints

## 📝 Logging

Logs are saved to:
- Application logs: `logs/app.log`
- Verification results: `logs/comparisons.csv`
- Database activity: Set `echo=True` in `database/config.py` for SQL logs

## 🎯 Next Steps

1. ✅ Setup PostgreSQL and create database
2. ✅ Install dependencies
3. ✅ Start the application
4. ✅ Register some faces through `/database`
5. ✅ Test comparison functionality
6. ✅ Explore API endpoints

## 📞 Support

For issues:
1. Check [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)
2. Review error messages in Flask console
3. Check database logs: `SELECT * FROM comparisons LIMIT 10;`

## 📄 License

This project uses InsightFace which is under Apache 2.0 license.

---

**Built with ❤️ using Flask, PostgreSQL, and InsightFace**
