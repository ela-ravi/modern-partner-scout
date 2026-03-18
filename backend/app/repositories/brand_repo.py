"""
PartnerScout AI - Brand DNA Repository

Repository for managing brand DNA records in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.core.constants import Tables
from app.core.exceptions import BrandDNANotFoundError
from app.db import SupabaseClient


class BrandRepository(BaseRepository[Dict[str, Any]]):
    """
    Repository for brand_dna table operations.
    
    Handles CRUD operations for brand DNA extracted from reference profiles.
    """
    
    @property
    def table_name(self) -> str:
        return Tables.BRAND_DNA
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create(
        self,
        job_id: str,
        hashtags: List[str],
        keywords: List[str],
        visual_themes: Optional[List[str]] = None,
        content_pillars: Optional[List[str]] = None,
        target_audience_description: Optional[str] = None,
        embedding_vector: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Create brand DNA for a job.
        
        Args:
            job_id: ID of the parent discovery job
            hashtags: Extracted hashtags
            keywords: Extracted keywords
            visual_themes: Visual theme descriptions
            content_pillars: Content pillar categories
            target_audience_description: Target audience description
            embedding_vector: 1536-dim embedding vector
            
        Returns:
            Created brand DNA data
        """
        brand_data = {
            "job_id": job_id,
            "hashtags": hashtags,
            "keywords": keywords,
        }
        
        if visual_themes:
            brand_data["visual_themes"] = visual_themes
        
        if content_pillars:
            brand_data["content_pillars"] = content_pillars
        
        if target_audience_description:
            brand_data["target_audience_description"] = target_audience_description
        
        if embedding_vector:
            # Convert to string format for pgvector
            brand_data["embedding_vector"] = embedding_vector
        
        return self.insert(brand_data)
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_job_id(self, job_id: str | UUID) -> Dict[str, Any]:
        """
        Get brand DNA for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Brand DNA data
            
        Raises:
            BrandDNANotFoundError: If not found
        """
        brand_dna = self.get_by_job_id_optional(job_id)
        if not brand_dna:
            raise BrandDNANotFoundError(str(job_id))
        return brand_dna
    
    def get_by_job_id_optional(self, job_id: str | UUID) -> Optional[Dict[str, Any]]:
        """
        Get brand DNA for a job, returning None if not found.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Brand DNA data or None
        """
        response = (
            self._table()
            .select("*")
            .eq("job_id", str(job_id))
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    def exists_for_job(self, job_id: str | UUID) -> bool:
        """
        Check if brand DNA exists for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            True if brand DNA exists
        """
        response = (
            self._table()
            .select("id")
            .eq("job_id", str(job_id))
            .execute()
        )
        data = self._handle_response(response)
        return len(data) > 0
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_by_job_id(
        self,
        job_id: str | UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update brand DNA by job ID.
        
        Args:
            job_id: Job UUID
            data: Fields to update
            
        Returns:
            Updated brand DNA data
        """
        response = (
            self._table()
            .update(data)
            .eq("job_id", str(job_id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(job_id))
    
    def update_hashtags(
        self,
        job_id: str | UUID,
        hashtags: List[str]
    ) -> Dict[str, Any]:
        """
        Update hashtags for a job's brand DNA.
        
        Args:
            job_id: Job UUID
            hashtags: New hashtags list
            
        Returns:
            Updated brand DNA
        """
        return self.update_by_job_id(job_id, {"hashtags": hashtags})
    
    def update_keywords(
        self,
        job_id: str | UUID,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Update keywords for a job's brand DNA.
        
        Args:
            job_id: Job UUID
            keywords: New keywords list
            
        Returns:
            Updated brand DNA
        """
        return self.update_by_job_id(job_id, {"keywords": keywords})
    
    def update_embedding(
        self,
        job_id: str | UUID,
        embedding_vector: List[float]
    ) -> Dict[str, Any]:
        """
        Update the embedding vector for a job's brand DNA.
        
        Args:
            job_id: Job UUID
            embedding_vector: New embedding vector (1536 dimensions)
            
        Returns:
            Updated brand DNA
        """
        return self.update_by_job_id(job_id, {"embedding_vector": embedding_vector})
    
    # =========================================================================
    # Delete Operations
    # =========================================================================
    
    def delete_by_job_id(self, job_id: str | UUID) -> bool:
        """
        Delete brand DNA for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            True if deleted
        """
        response = (
            self._table()
            .delete()
            .eq("job_id", str(job_id))
            .execute()
        )
        data = self._handle_response(response)
        return len(data) > 0
    
    # =========================================================================
    # Specialized Queries
    # =========================================================================
    
    def get_hashtags(self, job_id: str | UUID) -> List[str]:
        """
        Get just the hashtags for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            List of hashtags
        """
        brand_dna = self.get_by_job_id_optional(job_id)
        return brand_dna.get("hashtags", []) if brand_dna else []
    
    def get_keywords(self, job_id: str | UUID) -> List[str]:
        """
        Get just the keywords for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            List of keywords
        """
        brand_dna = self.get_by_job_id_optional(job_id)
        return brand_dna.get("keywords", []) if brand_dna else []
