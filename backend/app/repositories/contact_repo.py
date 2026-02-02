"""
PartnerScout AI - Contact Repository

Repository for managing profile contact information in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.core.constants import Tables
from app.core.exceptions import NotFoundError
from app.db import SupabaseClient


class ContactRepository(BaseRepository[Dict[str, Any]]):
    """
    Repository for profile_contacts table operations.
    
    Handles CRUD operations for extracted contact information.
    """
    
    @property
    def table_name(self) -> str:
        return Tables.PROFILE_CONTACTS
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create(
        self,
        profile_id: str,
        email: Optional[str] = None,
        email_source: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        other_contacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create contact info for a profile.
        
        Args:
            profile_id: ID of the profile
            email: Contact email
            email_source: Where email was found ('bio', 'business_email', 'website', 'extracted')
            phone: Phone number
            website: Website URL
            other_contacts: Additional contact methods (e.g., linktree, twitter)
            
        Returns:
            Created contact data
        """
        contact_data = {
            "profile_id": profile_id,
        }
        
        if email:
            contact_data["email"] = email
        if email_source:
            contact_data["email_source"] = email_source
        if phone:
            contact_data["phone"] = phone
        if website:
            contact_data["website"] = website
        if other_contacts:
            contact_data["other_contacts"] = other_contacts
        
        return self.insert(contact_data)
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_profile_id(self, profile_id: str | UUID) -> Dict[str, Any]:
        """
        Get contact info for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Contact data
            
        Raises:
            NotFoundError: If contact not found
        """
        contact = self.get_by_profile_id_optional(profile_id)
        if not contact:
            raise NotFoundError(
                f"Contact info not found for profile: {profile_id}",
                resource_type="profile_contact",
                resource_id=str(profile_id)
            )
        return contact
    
    def get_by_profile_id_optional(self, profile_id: str | UUID) -> Optional[Dict[str, Any]]:
        """
        Get contact info for a profile, returning None if not found.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Contact data or None
        """
        response = (
            self._table()
            .select("*")
            .eq("profile_id", str(profile_id))
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    def exists_for_profile(self, profile_id: str | UUID) -> bool:
        """
        Check if contact info exists for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if contact exists
        """
        return self.get_by_profile_id_optional(profile_id) is not None
    
    def has_email(self, profile_id: str | UUID) -> bool:
        """
        Check if a profile has an email address.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if email exists
        """
        contact = self.get_by_profile_id_optional(profile_id)
        return contact is not None and contact.get("email") is not None
    
    def get_email(self, profile_id: str | UUID) -> Optional[str]:
        """
        Get just the email for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Email address or None
        """
        contact = self.get_by_profile_id_optional(profile_id)
        return contact.get("email") if contact else None
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_by_profile_id(
        self,
        profile_id: str | UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update contact info by profile ID.
        
        Args:
            profile_id: Profile UUID
            data: Fields to update
            
        Returns:
            Updated contact data
        """
        response = (
            self._table()
            .update(data)
            .eq("profile_id", str(profile_id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(profile_id))
    
    def update_email(
        self,
        profile_id: str | UUID,
        email: str,
        source: str = "extracted"
    ) -> Dict[str, Any]:
        """
        Update or set the email for a profile.
        
        Args:
            profile_id: Profile UUID
            email: Email address
            source: Email source
            
        Returns:
            Updated contact data
        """
        return self.update_by_profile_id(
            profile_id,
            {"email": email, "email_source": source}
        )
    
    def upsert(
        self,
        profile_id: str,
        email: Optional[str] = None,
        email_source: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        other_contacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create or update contact info for a profile.
        
        Args:
            profile_id: Profile UUID
            email: Contact email
            email_source: Where email was found
            phone: Phone number
            website: Website URL
            other_contacts: Additional contact methods
            
        Returns:
            Contact data
        """
        existing = self.get_by_profile_id_optional(profile_id)
        
        if existing:
            update_data = {}
            if email is not None:
                update_data["email"] = email
            if email_source is not None:
                update_data["email_source"] = email_source
            if phone is not None:
                update_data["phone"] = phone
            if website is not None:
                update_data["website"] = website
            if other_contacts is not None:
                update_data["other_contacts"] = other_contacts
            
            if update_data:
                return self.update_by_profile_id(profile_id, update_data)
            return existing
        else:
            return self.create(
                profile_id=profile_id,
                email=email,
                email_source=email_source,
                phone=phone,
                website=website,
                other_contacts=other_contacts
            )
    
    # =========================================================================
    # Delete Operations
    # =========================================================================
    
    def delete_by_profile_id(self, profile_id: str | UUID) -> bool:
        """
        Delete contact info for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if deleted
        """
        response = (
            self._table()
            .delete()
            .eq("profile_id", str(profile_id))
            .execute()
        )
        return len(self._handle_response(response)) > 0
    
    # =========================================================================
    # Bulk Queries
    # =========================================================================
    
    def list_profiles_with_email_for_job(
        self,
        job_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all contacts with emails for profiles in a job.
        
        Args:
            job_id: Job UUID
            limit: Maximum results
            
        Returns:
            List of contacts with emails
        """
        # Join with profiles to filter by job
        response = (
            self._table()
            .select("*, discovered_profiles!inner(job_id, username, full_name)")
            .eq("discovered_profiles.job_id", job_id)
            .not_.is_("email", "null")
            .limit(limit)
            .execute()
        )
        return self._handle_response(response)
    
    def count_with_email_for_job(self, job_id: str) -> int:
        """
        Count profiles with emails for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Count of profiles with emails
        """
        contacts = self.list_profiles_with_email_for_job(job_id, limit=1000)
        return len(contacts)
