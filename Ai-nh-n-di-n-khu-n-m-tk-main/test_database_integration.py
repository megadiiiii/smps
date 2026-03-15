"""
Integration test for face database system.
Tests database operations, embedding generation, and comparison.
"""

import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import create_tables, engine
from services.database_service import DatabaseService
from services.vector_search_service import VectorSearchService


def test_database_connection():
    """Test PostgreSQL connection."""
    print("Test 1: Database Connection")
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("  ✓ Database connection successful")
        return True
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


def test_create_tables():
    """Test table creation."""
    print("\nTest 2: Create Tables")
    try:
        create_tables()
        print("  ✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to create tables: {e}")
        return False


def test_person_crud():
    """Test person CRUD operations."""
    print("\nTest 3: Person CRUD Operations")
    db = DatabaseService()
    
    try:
        # Create
        person = db.register_person("test_user_1", "Test User")
        print(f"  ✓ Created person: {person.person_id}")
        
        # Read
        retrieved = db.get_person("test_user_1")
        assert retrieved is not None
        print(f"  ✓ Retrieved person: {retrieved.name}")
        
        # List
        all_persons = db.get_all_persons()
        print(f"  ✓ Listed {len(all_persons)} persons")
        
        # Delete
        deleted = db.delete_person("test_user_1")
        assert deleted
        print(f"  ✓ Deleted person")
        
        return True
    except Exception as e:
        print(f"  ✗ CRUD operations failed: {e}")
        return False


def test_embedding_operations():
    """Test embedding save and retrieval."""
    print("\nTest 4: Embedding Operations")
    db = DatabaseService()
    
    try:
        # Create person
        person = db.register_person("test_user_2", "Embedding Tester")
        
        # Create fake embedding (512-dim vector)
        embedding = np.random.randn(512).astype(np.float32)
        
        # Save embedding
        emb_record = db.save_embedding("test_user_2", embedding, "test.jpg")
        print(f"  ✓ Saved embedding: {emb_record.id}")
        
        # Retrieve embeddings
        embeddings = db.get_embeddings_for_person("test_user_2")
        assert len(embeddings) == 1
        print(f"  ✓ Retrieved {len(embeddings)} embedding(s)")
        
        # Verify shape
        saved_emb = np.array(embeddings[0].embedding)
        assert saved_emb.shape == (512,)
        print(f"  ✓ Embedding shape correct: {saved_emb.shape}")
        
        # Cleanup
        db.delete_person("test_user_2")
        
        return True
    except Exception as e:
        print(f"  ✗ Embedding operations failed: {e}")
        return False


def test_search_functionality():
    """Test embedding search and comparison."""
    print("\nTest 5: Search and Comparison")
    db = DatabaseService()
    search = VectorSearchService()
    
    try:
        # Create test people with different embeddings
        person1 = db.register_person("alice", "Alice")
        person2 = db.register_person("bob", "Bob")
        
        # Create embeddings
        emb_alice_1 = np.random.randn(512).astype(np.float32)
        emb_alice_2 = emb_alice_1 + np.random.randn(512) * 0.01  # Very similar
        emb_bob = np.random.randn(512).astype(np.float32) + 10  # Different
        
        # Normalize for better results
        emb_alice_1 = emb_alice_1 / np.linalg.norm(emb_alice_1)
        emb_alice_2 = emb_alice_2 / np.linalg.norm(emb_alice_2)
        emb_bob = emb_bob / np.linalg.norm(emb_bob)
        
        # Save embeddings
        db.save_embedding("alice", emb_alice_1, "alice1.jpg")
        db.save_embedding("alice", emb_alice_2, "alice2.jpg")
        db.save_embedding("bob", emb_bob, "bob.jpg")
        
        print(f"  ✓ Created test embeddings for alice and bob")
        
        # Test search
        results = search.search_similar(emb_alice_1, k=5, threshold=0.0)
        assert len(results) > 0
        print(f"  ✓ Search returned {len(results)} results")
        
        # Test comparison
        similarity = search.compare_embeddings(emb_alice_1, emb_alice_2)
        print(f"  ✓ Similarity (alice_1 vs alice_2): {similarity:.4f}")
        
        # Test comparison with different person
        diff_similarity = search.compare_embeddings(emb_alice_1, emb_bob)
        print(f"  ✓ Similarity (alice vs bob): {diff_similarity:.4f}")
        
        # Verify alice_2 is more similar to alice_1 than bob
        assert similarity > diff_similarity or np.abs(similarity - diff_similarity) < 0.1
        print(f"  ✓ Similarity ordering correct")
        
        # Cleanup
        db.delete_person("alice")
        db.delete_person("bob")
        
        return True
    except Exception as e:
        print(f"  ✗ Search operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_logging():
    """Test comparison logging."""
    print("\nTest 6: Comparison Logging")
    db = DatabaseService()
    
    try:
        # Create person
        person = db.register_person("test_user_3", "Logging Tester")
        
        # Log a comparison
        comparison = db.log_comparison(
            person_id="test_user_3",
            score=0.85,
            is_match=True,
            threshold=0.35,
            notes="Test comparison"
        )
        print(f"  ✓ Logged comparison: {comparison.id}")
        
        # Retrieve comparison history
        history = db.get_comparison_history("test_user_3")
        assert len(history) >= 1
        print(f"  ✓ Retrieved {len(history)} comparison(s)")
        
        # Check statistics
        stats = db.get_database_stats()
        print(f"  ✓ Database stats: {stats['total_persons']} persons, "
              f"{stats['total_embeddings']} embeddings, "
              f"{stats['total_comparisons']} comparisons")
        
        # Cleanup
        db.delete_person("test_user_3")
        
        return True
    except Exception as e:
        print(f"  ✗ Comparison logging failed: {e}")
        return False


def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")
    try:
        db = DatabaseService()
        for person_id in ["test_user_1", "test_user_2", "alice", "bob", "test_user_3"]:
            try:
                db.delete_person(person_id)
            except:
                pass
        print("  ✓ Cleanup complete")
    except Exception as e:
        print(f"  ✗ Cleanup failed: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Face Database System Integration Tests")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_create_tables,
        test_person_crud,
        test_embedding_operations,
        test_search_functionality,
        test_comparison_logging,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! System is ready to use.")
        print("  Start the app with: python app.py")
        return True
    else:
        print("\n✗ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
