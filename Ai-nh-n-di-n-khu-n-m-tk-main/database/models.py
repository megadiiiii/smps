"""SQLAlchemy models for face database."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.config import Base


class Person(Base):
    """Person record with metadata."""
    
    __tablename__ = "persons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(String(255), unique=True, nullable=False, index=True)  # User-facing ID
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    embeddings = relationship("Embedding", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(person_id='{self.person_id}', name='{self.name}', embeddings={len(self.embeddings)})>"


class Embedding(Base):
    """Face embedding vector stored as array."""
    
    __tablename__ = "embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False, index=True)
    
    # Vector embedding (512-dim by default from InsightFace)
    embedding = Column(ARRAY(Float), nullable=False)
    
    # Metadata
    image_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="embeddings")
    
    def __repr__(self):
        return f"<Embedding(person_id={self.person_id}, dim={len(self.embedding) if self.embedding else 0})>"


class Comparison(Base):
    """Log of face comparisons for audit trail."""
    
    __tablename__ = "comparisons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reference to compared person (can be null if no match)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True, index=True)
    
    # Comparison result
    query_embedding_id = Column(UUID(as_uuid=True), ForeignKey("embeddings.id"), nullable=True)
    matched_embedding_id = Column(UUID(as_uuid=True), ForeignKey("embeddings.id"), nullable=True)
    
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    is_match = Column(Integer, default=0, nullable=False)  # Boolean: 1=match, 0=no match
    threshold = Column(Float, nullable=False)  # Threshold used for comparison
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)  # Additional context (e.g., source, user)
    
    def __repr__(self):
        return f"<Comparison(person_id={self.person_id}, score={self.similarity_score:.4f}, match={bool(self.is_match)})>"
