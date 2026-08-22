"""
Memory Service Layer

Stores and retrieves user preferences, context, and learned behaviors.
Enables CETRI to remember information across conversations.

Example:
    User: "My favorite language is Python"
    CETRI: "Got it, I'll remember that"
    
    Later:
    User: "What's my favorite language?"
    CETRI: "Your favorite language is Python"
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import UserMemory, User


class MemoryService:
    """
    Manages user memory and preferences
    
    Types of memory:
    - Preferences (favorite language, timezone, etc)
    - Context (current project, role, goals)
    - Facts (name, location, company)
    - History (past conversations, preferences, patterns)
    """

    def __init__(self, db: Session):
        self.db = db

    async def store_memory(
        self,
        user_id: str,
        key: str,
        value: Any,
        memory_type: str = "preference"
    ) -> bool:
        """
        Store a user memory
        
        Args:
            user_id: User ID
            key: Memory key (e.g., "favorite_language")
            value: Memory value (e.g., "Python")
            memory_type: Type of memory ("preference", "fact", "context", "history")
        
        Returns:
            True if stored successfully
        """
        try:
            # Check if memory already exists
            existing = self.db.query(UserMemory).filter(
                UserMemory.user_id == user_id,
                UserMemory.key == key
            ).first()
            
            memory_value = {
                "value": value,
                "type": memory_type,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            if existing:
                # Update existing memory
                existing.value = memory_value
            else:
                # Create new memory
                import shortuuid
                memory = UserMemory(
                    id=f"mem_{shortuuid.uuid()}",
                    user_id=user_id,
                    key=key,
                    value=memory_value
                )
                self.db.add(memory)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error storing memory: {e}")
            return False

    async def retrieve_memory(
        self,
        user_id: str,
        key: str
    ) -> Optional[Any]:
        """
        Retrieve a user memory
        
        Args:
            user_id: User ID
            key: Memory key
        
        Returns:
            Memory value or None
        """
        try:
            memory = self.db.query(UserMemory).filter(
                UserMemory.user_id == user_id,
                UserMemory.key == key
            ).first()
            
            if memory:
                value_dict = memory.value
                return value_dict.get("value")
            return None
            
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None

    async def get_all_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all memories for a user
        
        Args:
            user_id: User ID
            memory_type: Filter by type (optional)
        
        Returns:
            Dictionary of all memories
        """
        try:
            query = self.db.query(UserMemory).filter(
                UserMemory.user_id == user_id
            )
            
            if memory_type:
                # Note: This requires JSON filtering support in the DB
                # For now, filter in Python
                memories = {}
                for mem in query.all():
                    if mem.value.get("type") == memory_type:
                        memories[mem.key] = mem.value.get("value")
                return memories
            else:
                memories = {}
                for mem in query.all():
                    memories[mem.key] = mem.value.get("value")
                return memories
                
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return {}

    async def delete_memory(
        self,
        user_id: str,
        key: str
    ) -> bool:
        """Delete a user memory"""
        try:
            memory = self.db.query(UserMemory).filter(
                UserMemory.user_id == user_id,
                UserMemory.key == key
            ).first()
            
            if memory:
                self.db.delete(memory)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting memory: {e}")
            return False

    async def clear_all_memories(self, user_id: str) -> bool:
        """Clear all memories for a user"""
        try:
            self.db.query(UserMemory).filter(
                UserMemory.user_id == user_id
            ).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error clearing memories: {e}")
            return False

    async def build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive user profile from memories
        
        Returns:
        {
            "name": "John",
            "role": "AI Engineer",
            "preferences": {...},
            "context": {...},
            "facts": {...}
        }
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            profile = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "memories": {}
            }
            
            # Organize memories by type
            memories = await self.get_all_memories(user_id)
            profile["memories"] = memories
            
            return profile
            
        except Exception as e:
            print(f"Error building profile: {e}")
            return {}


def get_memory_service(db: Session) -> MemoryService:
    """Get memory service instance"""
    return MemoryService(db)
