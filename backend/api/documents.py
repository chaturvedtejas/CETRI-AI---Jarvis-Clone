"""
Documents/Files API endpoints

Handles file uploads and document management for RAG
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.models import get_db
from services.document_service import get_document_service, DocumentModel
from typing import List, Optional

router = APIRouter()

document_service = get_document_service()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload a document for RAG
    
    Supported formats:
    - PDF
    - TXT, MD
    - DOCX, XLSX
    - Images (JPG, PNG, GIF, WEBP)
    - Code (PY, JS, JSON)
    """
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Save document
        doc_id = await document_service.save_document(
            user_id=user_id,
            file_content=content,
            filename=file.filename,
            db=db
        )
        
        if not doc_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document"
            )
        
        # Get document info
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        
        return {
            "message": "Document uploaded successfully",
            "file_id": doc_id,
            "filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "extracted_text_preview": doc.extracted_text[:100] if doc.extracted_text else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/list")
async def list_documents(
    user_id: str,
    db: Session = Depends(get_db)
):
    """List all documents for a user"""
    try:
        documents = db.query(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).all()
        
        return {
            "user_id": user_id,
            "count": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "is_processed": doc.is_processed,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """Get document details"""
    try:
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "id": doc.id,
            "filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "is_processed": doc.is_processed,
            "extracted_text_preview": doc.extracted_text[:500] if doc.extracted_text else None,
            "created_at": doc.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    try:
        success = await document_service.delete_document(doc_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document deleted successfully", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
