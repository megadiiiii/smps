"""Database service for face operations."""

from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import numpy as np

from database.config import get_db_session, create_tables
from database.models import Person, Embedding, Comparison


class DatabaseService:
    """Handle all database operations for face recognition."""
    
    def __init__(self):
        """Initialize and ensure tables exist."""
        create_tables()
    
    # ──────────────────────────────────────────────────────────────────
    # Person Management
    # ──────────────────────────────────────────────────────────────────
    
    def register_person(self, person_id: str, name: str) -> Person:
        """Register a new person."""
        session = get_db_session()
        try:
            # Check if already exists
            existing = session.query(Person).filter_by(person_id=person_id).first()
            if existing:
                return existing
            
            person = Person(person_id=person_id, name=name)
            session.add(person)
            session.commit()
            return person
        finally:
            session.close()
    
    def get_person(self, person_id: str) -> Optional[Person]:
        """Get person by person_id."""
        session = get_db_session()
        try:
            return session.query(Person).filter_by(person_id=person_id).first()
        finally:
            session.close()
    
    def get_person_by_uuid(self, person_uuid: UUID) -> Optional[Person]:
        """Get person by UUID."""
        session = get_db_session()
        try:
            return session.query(Person).filter_by(id=person_uuid).first()
        finally:
            session.close()
    
    def get_all_persons(self) -> List[Person]:
        """Get all registered persons."""
        session = get_db_session()
        try:
            return session.query(Person).all()
        finally:
            session.close()
    
    def delete_person(self, person_id: str) -> bool:
        """Delete a person and their embeddings."""
        session = get_db_session()
        try:
            person = session.query(Person).filter_by(person_id=person_id).first()
            if person:
                session.delete(person)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # ──────────────────────────────────────────────────────────────────
    # Embedding Management
    # ──────────────────────────────────────────────────────────────────
    
    def save_embedding(self, person_id: str, embedding: np.ndarray, 
                       image_path: Optional[str] = None) -> Embedding:
        """Save an embedding for a person."""
        session = get_db_session()
        try:
            # Get or create person
            person = session.query(Person).filter_by(person_id=person_id).first()
            if not person:
                raise ValueError(f"Person '{person_id}' not found. Register first.")
            
            # Convert numpy array to list for PostgreSQL
            emb_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            emb_record = Embedding(
                person_id=person.id,
                embedding=emb_list,
                image_path=image_path
            )
            session.add(emb_record)
            session.commit()
            return emb_record
        finally:
            session.close()
    
    def get_embeddings_for_person(self, person_id: str) -> List[Embedding]:
        """Get all embeddings for a person."""
        session = get_db_session()
        try:
            person = session.query(Person).filter_by(person_id=person_id).first()
            if not person:
                return []
            return session.query(Embedding).filter_by(person_id=person.id).all()
        finally:
            session.close()
    
    def get_all_embeddings(self) -> List[Tuple[str, np.ndarray]]:
        """Get all embeddings as list of (person_id, embedding) tuples."""
        session = get_db_session()
        try:
            embeddings = session.query(Embedding, Person).join(Person).all()
            return [
                (emb_record.person.person_id, np.array(emb_record.embedding))
                for emb_record, person in embeddings
            ]
        finally:
            session.close()
    
    def get_all_embeddings_dict(self) -> dict:
        """Get all embeddings organized by person_id."""
        session = get_db_session()
        try:
            people = session.query(Person).all()
            result = {}
            for person in people:
                embeddings = [np.array(e.embedding) for e in person.embeddings]
                if embeddings:
                    result[person.person_id] = embeddings
            return result
        finally:
            session.close()
    
    # ──────────────────────────────────────────────────────────────────
    # Comparison Logging
    # ──────────────────────────────────────────────────────────────────
    
    def log_comparison(self, person_id: Optional[str], score: float, 
                      is_match: bool, threshold: float, 
                      notes: Optional[str] = None) -> Comparison:
        """Log a face comparison."""
        session = get_db_session()
        try:
            person_uuid = None
            if person_id:
                person = session.query(Person).filter_by(person_id=person_id).first()
                if person:
                    person_uuid = person.id
            
            comparison = Comparison(
                person_id=person_uuid,
                similarity_score=score,
                is_match=1 if is_match else 0,
                threshold=threshold,
                notes=notes
            )
            session.add(comparison)
            session.commit()
            return comparison
        finally:
            session.close()
    
    def get_comparison_history(self, person_id: Optional[str] = None, 
                               limit: int = 100) -> List[Comparison]:
        """Get comparison history, optionally filtered by person."""
        session = get_db_session()
        try:
            query = session.query(Comparison)
            if person_id:
                person = session.query(Person).filter_by(person_id=person_id).first()
                if person:
                    query = query.filter_by(person_id=person.id)
            return query.order_by(Comparison.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    # ──────────────────────────────────────────────────────────────────
    # Statistics & Maintenance
    # ──────────────────────────────────────────────────────────────────
    
    def count_persons(self) -> int:
        """Count total registered persons."""
        session = get_db_session()
        try:
            return session.query(Person).count()
        finally:
            session.close()
    
    def count_embeddings(self, person_id: Optional[str] = None) -> int:
        """Count embeddings, optionally for a specific person."""
        session = get_db_session()
        try:
            query = session.query(Embedding)
            if person_id:
                person = session.query(Person).filter_by(person_id=person_id).first()
                if person:
                    query = query.filter_by(person_id=person.id)
            return query.count()
        finally:
            session.close()
    
    def get_database_stats(self) -> dict:
        """Get comprehensive database statistics."""
        session = get_db_session()
        try:
            total_persons = session.query(Person).count()
            total_embeddings = session.query(Embedding).count()
            total_comparisons = session.query(Comparison).count()
            
            return {
                "total_persons": total_persons,
                "total_embeddings": total_embeddings,
                "total_comparisons": total_comparisons,
                "avg_embeddings_per_person": (
                    total_embeddings / total_persons if total_persons > 0 else 0
                )
            }
        finally:
            session.close()
