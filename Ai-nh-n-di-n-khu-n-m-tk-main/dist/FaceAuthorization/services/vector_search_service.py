"""Vector search service for comparing embeddings."""

from typing import List, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from services.database_service import DatabaseService


class VectorSearchService:
    """Search for similar embeddings in the database."""
    
    def __init__(self):
        """Initialize with database service."""
        self.db = DatabaseService()
    
    def search_similar(self, embedding: np.ndarray, k: int = 5, 
                      threshold: float = 0.35) -> List[Tuple[str, float]]:
        """
        Search for similar embeddings in database.
        
        Args:
            embedding: Query embedding (512-dim vector)
            k: Number of top results to return
            threshold: Minimum similarity score to consider a match
        
        Returns:
            List of (person_id, similarity_score) tuples, sorted by score descending
        """
        # Get all embeddings from database
        all_embeddings = self.db.get_all_embeddings()
        
        if not all_embeddings:
            return []
        
        # Prepare data for comparison
        person_ids = [person_id for person_id, _ in all_embeddings]
        embedding_vectors = np.array([emb for _, emb in all_embeddings])
        
        # Reshape query embedding if needed
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Calculate similarity (cosine similarity returns values in [-1, 1], we use abs)
        similarities = cosine_similarity(embedding, embedding_vectors)[0]
        
        # Sort by similarity descending
        sorted_indices = np.argsort(similarities)[::-1]
        
        # Return top-k results that meet threshold
        results = []
        for idx in sorted_indices[:k]:
            score = float(similarities[idx])
            if score >= threshold:
                results.append((person_ids[idx], score))
        
        return results
    
    def compare_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate similarity between two embeddings.
        
        Returns:
            Similarity score (0.0 to 1.0, higher = more similar)
        """
        # Handle different shapes
        if emb1.ndim == 1:
            emb1 = emb1.reshape(1, -1)
        if emb2.ndim == 1:
            emb2 = emb2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0, 0]
        return float(similarity)
    
    def find_best_match(self, embedding: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Find the best matching person for an embedding.
        
        Returns:
            (person_id, similarity_score) or None if no database embeddings
        """
        results = self.search_similar(embedding, k=1, threshold=0.0)
        return results[0] if results else None
    
    def batch_search(self, embeddings: List[np.ndarray], k: int = 5, 
                    threshold: float = 0.35) -> List[List[Tuple[str, float]]]:
        """
        Search for multiple embeddings.
        
        Returns:
            List of results for each embedding
        """
        return [self.search_similar(emb, k=k, threshold=threshold) for emb in embeddings]
