"""
RAG (Retrieval-Augmented Generation) API endpoints

Enables document-based question answering
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.models import get_db
from services.rag_service import get_rag_service
from typing import Optional

router = APIRouter()


@router.post("/index-document")
async def index_document(
    document_id: str,
    content: str,
    title: str = "Unknown",
    source: str = "uploaded",
    db: Session = Depends(get_db)
):
    """
    Index a document for RAG
    
    Args:
        document_id: Unique document ID
        content: Document text content
        title: Document title
        source: Document source
    """
    try:
        rag_service = get_rag_service()
        await rag_service.initialize()
        
        metadata = {
            "title": title,
            "source": source,
            "document_id": document_id
        }
        
        chunks_added = await rag_service.add_document(
            document_id=document_id,
            content=content,
            metadata=metadata
        )
        
        return {
            "message": "Document indexed successfully",
            "document_id": document_id,
            "chunks_added": chunks_added
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}"
        )


@router.post("/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Search documents using RAG
    
    Args:
        query: Search query
        top_k: Number of results to return
    
    Returns:
        Retrieved context and relevant chunks
    """
    try:
        rag_service = get_rag_service()
        await rag_service.initialize()
        
        chunks, context = await rag_service.retrieve_context(
            query=query,
            top_k=top_k
        )
        
        return {
            "query": query,
            "results_count": len(chunks),
            "retrieved_context": context,
            "chunks": [
                {
                    "id": chunk["id"],
                    "content": chunk["content"],
                    "similarity": 1 - chunk["distance"],  # Convert distance to similarity
                    "source": chunk["metadata"].get("title", "Unknown")
                }
                for chunk in chunks
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/ask")
async def ask_about_documents(
    question: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Ask a question about uploaded documents
    
    Args:
        question: Question to ask
        top_k: Number of relevant chunks to retrieve
    
    Returns:
        Augmented prompt ready for LLM
    """
    try:
        rag_service = get_rag_service()
        await rag_service.initialize()
        
        # Retrieve context
        chunks, context = await rag_service.retrieve_context(
            query=question,
            top_k=top_k
        )
        
        if not chunks:
            return {
                "question": question,
                "has_context": False,
                "message": "No relevant documents found"
            }
        
        return {
            "question": question,
            "has_context": True,
            "retrieved_chunks": len(chunks),
            "context": context,
            "sources": list(set([
                chunk["metadata"].get("title", "Unknown")
                for chunk in chunks
            ]))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )
