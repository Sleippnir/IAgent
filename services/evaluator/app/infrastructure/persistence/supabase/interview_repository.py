"""
Supabase repository implementation for Interview entities.
"""
from typing import Optional, List
from supabase import create_client, Client
from ...config import get_settings
from ....domain.entities.interview import Interview


class SupabaseInterviewRepository:
    """Repository for managing Interview entities in Supabase."""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_ANON_KEY
        )
        self.table_name = "interviews"
    
    async def create(self, interview: Interview) -> Interview:
        """Create a new interview record in Supabase."""
        try:
            data = interview.to_dict()
            result = self.supabase.table(self.table_name).insert(data).execute()
            
            if result.data:
                return Interview.from_dict(result.data[0])
            else:
                raise Exception("Failed to create interview record")
                
        except Exception as e:
            raise Exception(f"Error creating interview in Supabase: {e}")
    
    async def get_by_id(self, interview_id: str) -> Optional[Interview]:
        """Retrieve an interview by ID from Supabase."""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("interview_id", interview_id).execute()
            
            if result.data:
                return Interview.from_dict(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving interview from Supabase: {e}")
    
    async def update(self, interview: Interview) -> Interview:
        """Update an existing interview record in Supabase."""
        try:
            data = interview.to_dict()
            result = self.supabase.table(self.table_name).update(data).eq("interview_id", interview.interview_id).execute()
            
            if result.data:
                return Interview.from_dict(result.data[0])
            else:
                raise Exception("Failed to update interview record")
                
        except Exception as e:
            raise Exception(f"Error updating interview in Supabase: {e}")
    
    async def delete(self, interview_id: str) -> bool:
        """Delete an interview record from Supabase."""
        try:
            result = self.supabase.table(self.table_name).delete().eq("interview_id", interview_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            raise Exception(f"Error deleting interview from Supabase: {e}")
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Interview]:
        """List all interviews with pagination."""
        try:
            result = self.supabase.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            
            return [Interview.from_dict(data) for data in result.data]
            
        except Exception as e:
            raise Exception(f"Error listing interviews from Supabase: {e}")
    
    async def get_by_status(self, has_evaluations: bool = None) -> List[Interview]:
        """Get interviews filtered by evaluation status."""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if has_evaluations is True:
                # Get interviews that have at least one evaluation
                query = query.not_.is_("evaluation_1", "null")
            elif has_evaluations is False:
                # Get interviews that have no evaluations
                query = query.is_("evaluation_1", "null").is_("evaluation_2", "null").is_("evaluation_3", "null")
            
            result = query.execute()
            return [Interview.from_dict(data) for data in result.data]
            
        except Exception as e:
            raise Exception(f"Error filtering interviews from Supabase: {e}")


# Example usage and helper functions
async def save_interview_to_supabase(interview: Interview) -> Interview:
    """Helper function to save an interview to Supabase."""
    repo = SupabaseInterviewRepository()
    
    # Check if interview already exists
    existing = await repo.get_by_id(interview.interview_id)
    
    if existing:
        # Update existing interview
        return await repo.update(interview)
    else:
        # Create new interview
        return await repo.create(interview)


async def load_interview_from_supabase(interview_id: str) -> Optional[Interview]:
    """Helper function to load an interview from Supabase."""
    repo = SupabaseInterviewRepository()
    return await repo.get_by_id(interview_id)