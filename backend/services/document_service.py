"""
File Upload and Document Processing System

Handles:
- PDF files
- Images (JPG, PNG, GIF, WEBP)
- Text files (TXT, MD)
- Office documents (DOCX, XLSX)

Stores files in local directory or S3.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from enum import Enum
import os
import uuid
from pydantic import BaseModel
from database.models import DocumentModel


class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    CODE = "code"
    OTHER = "other"


class FileUploadResponse(BaseModel):
    """Response from file upload"""
    file_id: str
    filename: str
    file_type: str
    file_size: int
    upload_time: str
    extracted_text_preview: Optional[str] = None


class DocumentProcessor:
    """Processes uploaded documents"""
    
    # File type mappings
    MIME_TYPES = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".json": "application/json",
    }
    
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    def get_file_type(self, filename: str) -> FileType:
        """Determine file type from extension"""
        ext = Path(filename).suffix.lower()
        
        if ext == ".pdf":
            return FileType.PDF
        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return FileType.IMAGE
        elif ext in [".txt", ".md"]:
            return FileType.TEXT
        elif ext in [".docx", ".xlsx"]:
            return FileType.DOCUMENT
        elif ext in [".py", ".js", ".json"]:
            return FileType.CODE
        else:
            return FileType.OTHER
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        ext = Path(filename).suffix.lower()
        return self.MIME_TYPES.get(ext, "application/octet-stream")
    
    def generate_storage_path(self, user_id: str, filename: str) -> Path:
        """Generate secure storage path for uploaded file"""
        # Create user directory
        user_dir = self.upload_dir / user_id
        user_dir.mkdir(exist_ok=True)
        
        # Use UUID to prevent filename conflicts
        file_id = str(uuid.uuid4())
        ext = Path(filename).suffix
        stored_filename = f"{file_id}{ext}"
        
        return user_dir / stored_filename
    
    async def extract_text(self, file_path: Path, file_type: FileType) -> Optional[str]:
        """Extract text from document"""
        try:
            if file_type == FileType.PDF:
                return await self._extract_text_from_pdf(file_path)
            elif file_type == FileType.TEXT:
                return await self._extract_text_from_txt(file_path)
            elif file_type == FileType.DOCUMENT:
                return await self._extract_text_from_docx(file_path)
            elif file_type == FileType.IMAGE:
                return await self._extract_text_from_image(file_path)
            return None
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    async def _extract_text_from_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text[:10000] if text else None
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    async def _extract_text_from_txt(self, file_path: Path) -> Optional[str]:
        """Extract text from plain text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return text[:10000] if text else None
        except Exception as e:
            print(f"TXT extraction error: {e}")
            return None
    
    async def _extract_text_from_docx(self, file_path: Path) -> Optional[str]:
        """Extract text from DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text[:10000] if text else None
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return None
    
    async def _extract_text_from_image(self, file_path: Path) -> Optional[str]:
        """Extract text from image (OCR)"""
        try:
            # TODO: Integrate with Tesseract or cloud OCR
            # For now, return None
            return None
        except Exception as e:
            print(f"Image extraction error: {e}")
            return None


class DocumentService:
    """Service for managing documents"""
    
    def __init__(self, upload_dir: str = "./uploads"):
        self.processor = DocumentProcessor(upload_dir)
    
    async def save_document(
        self,
        user_id: str,
        file_content: bytes,
        filename: str,
        db = None
    ) -> Optional[str]:
        """
        Save uploaded document
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            # Generate storage path
            file_path = self.processor.generate_storage_path(user_id, filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Get file metadata
            file_type = self.processor.get_file_type(filename)
            mime_type = self.processor.get_mime_type(filename)
            file_size = len(file_content)
            
            # Extract text
            extracted_text = await self.processor.extract_text(file_path, file_type)
            
            # Save to database if provided
            if db:
                doc_id = f"doc_{uuid.uuid4()}"
                document = DocumentModel(
                    id=doc_id,
                    user_id=user_id,
                    original_filename=filename,
                    stored_filename=file_path.name,
                    file_type=file_type.value,
                    file_size=file_size,
                    file_path=str(file_path),
                    mime_type=mime_type,
                    extracted_text=extracted_text,
                    is_processed=True
                )
                db.add(document)
                db.commit()
                db.refresh(document)
                return document.id
            
            return str(file_path)
            
        except Exception as e:
            print(f"Error saving document: {e}")
            return None
    
    async def get_document(self, doc_id: str, db = None) -> Optional[DocumentModel]:
        """Retrieve document metadata"""
        if db:
            return db.query(DocumentModel).filter(
                DocumentModel.id == doc_id
            ).first()
        return None
    
    async def list_documents(self, user_id: str, db = None) -> List[DocumentModel]:
        """List all documents for a user"""
        if db:
            return db.query(DocumentModel).filter(
                DocumentModel.user_id == user_id
            ).all()
        return []
    
    async def delete_document(self, doc_id: str, db = None) -> bool:
        """Delete a document"""
        try:
            if db:
                doc = await self.get_document(doc_id, db)
                if doc:
                    # Delete file
                    file_path = Path(doc.file_path)
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Delete from DB
                    db.delete(doc)
                    db.commit()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False


def get_document_service() -> DocumentService:
    """Get document service instance"""
    return DocumentService()
