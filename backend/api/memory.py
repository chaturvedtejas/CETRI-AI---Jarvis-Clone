"""
Memory API endpoints

Allows users to store and retrieve memories/preferences
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database.models import get_db
from services.memory_service import get_memory_service

router = APIRouter()


class MemoryInput(BaseModel):
    """Memory input model"""
    key: str
    value: Any
    memory_type: Optional[str] = "preference"


class MemoryResponse(BaseModel):
    """Memory response model"""
    key: str
    value: Any
    type: str
    created_at: Optional[str] = None


@router.post("/store")
async def store_memory(
    user_id: str,
    memory: MemoryInput,
    db: Session = Depends(get_db)
):
    """
    Store user memory/preference
    
    Args:
        user_id: User ID
        memory: Memory data (key, value, type)
    
    Example:
        POST /api/memory/store?user_id=user_123
        {
            "key": "favorite_language",
            "value": "Python",
            "memory_type": "preference"
        }
    """
    
    service = get_memory_service(db)
    success = await service.store_memory(
        user_id=user_id,
        key=memory.key,
        value=memory.value,
        memory_type=memory.memory_type
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to store memory")
    
    return {
        "message": "Memory stored successfully",
        "key": memory.key,
        "value": memory.value
    }


@router.get("/retrieve/{memory_key}")
async def retrieve_memory(
    user_id: str,
    memory_key: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve user memory
    
    Args:
        user_id: User ID
        memory_key: Memory key to retrieve
    
    Example:
        GET /api/memory/retrieve/favorite_language?user_id=user_123
    """
    
    service = get_memory_service(db)
    value = await service.retrieve_memory(
        user_id=user_id,
        key=memory_key
    )
    
    if value is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "key": memory_key,
        "value": value
    }


@router.get("/all")
async def get_all_memories(
    user_id: str,
    memory_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all user memories
    
    Args:
        user_id: User ID
        memory_type: Filter by type (optional)
    
    Example:
        GET /api/memory/all?user_id=user_123&memory_type=preference
    """
    
    service = get_memory_service(db)
    memories = await service.get_all_memories(
        user_id=user_id,
        memory_type=memory_type
    )
    
    return {
        "user_id": user_id,
        "count": len(memories),
        "memories": memories
    }


@router.delete("/{memory_key}")
async def delete_memory(
    user_id: str,
    memory_key: str,
    db: Session = Depends(get_db)
):
    """
    Delete a user memory
    
    Args:
        user_id: User ID
        memory_key: Memory key to delete
    """
    
    service = get_memory_service(db)
    success = await service.delete_memory(
        user_id=user_id,
        key=memory_key
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {"message": "Memory deleted successfully", "key": memory_key}


@router.delete("/all")
async def clear_all_memories(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Clear all user memories
    
    CAUTION: This cannot be undone
    """
    
    service = get_memory_service(db)
    success = await service.clear_all_memories(user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear memories")
    
    return {"message": "All memories cleared"}


@router.get("/profile")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete user profile including all memories
    
    Returns comprehensive user data
    """
    
    service = get_memory_service(db)
    profile = await service.build_user_profile(user_id=user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return profile
