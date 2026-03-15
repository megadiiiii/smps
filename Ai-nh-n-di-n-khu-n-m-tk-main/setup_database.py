"""
Test database connection and create tables.
Run this after PostgreSQL is installed and running.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import create_tables, engine
from database.models import Person, Embedding, Comparison

def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✓ Database connection successful!")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def create_tables_db():
    """Create all tables."""
    try:
        create_tables()
        print("✓ Tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False

def main():
    print("=" * 60)
    print("Face Authorization Database Setup")
    print("=" * 60)
    
    print("\n[1/2] Testing database connection...")
    if not test_connection():
        print("\n⚠️  Please ensure PostgreSQL is running with these credentials:")
        print("   User: postgres")
        print("   Password: postgres")
        print("   Database: face_auth")
        print("\nYou can change these in the .env file")
        return False
    
    print("\n[2/2] Creating tables...")
    if not create_tables_db():
        return False
    
    print("\n" + "=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)
    print("\nYou can now run: python app.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
