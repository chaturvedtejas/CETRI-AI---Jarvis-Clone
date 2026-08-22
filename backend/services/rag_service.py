"""
RAG (Retrieval-Augmented Generation) Service

Combines document retrieval with LLM responses:
1. Documents split into chunks
2. Chunks embedded using sentence-transformers
3. Embeddings stored in ChromaDB vector database
4. On query, retrieve relevant chunks
5. Augment prompt with retrieved context
6. Generate response with context
"""

from typing import Optional, List, Dict, Any, Tuple


class EmbeddingModel:
    """Wraps sentence-transformers for embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
    
    async def load(self):
        """Load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print(f"✓ Loaded embedding model: {self.model_name}")
        except ImportError:
            print("⚠️  sentence-transformers not installed")
    
    async def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.model:
            await self.load()
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    async def embed_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            await self.load()
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return None


class ChromaVectorDB:
    """Wrapper for ChromaDB vector database"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
    
    async def connect(self):
        """Connect to ChromaDB"""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="cetri_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Connected to ChromaDB")
        except ImportError:
            print("⚠️  chromadb not installed")
        except Exception as e:
            print(f"ChromaDB error: {e}")
    
    async def add_chunk(
        self,
        chunk_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """Add chunk to vector database"""
        try:
            if not self.collection:
                await self.connect()
            self.collection.upsert(
                ids=[chunk_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            print(f"Error adding chunk: {e}")
            return False
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            if not self.collection:
                await self.connect()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            chunks = []
            if results["ids"] and len(results["ids"]) > 0:
                for i, chunk_id in enumerate(results["ids"][0]):
                    chunks.append({
                        "id": chunk_id,
                        "content": results["documents"][0][i],
                        "distance": results["distances"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    })
            return chunks
        except Exception as e:
            print(f"Search error: {e}")
            return []


class DocumentChunker:
    """Splits documents into chunks for embedding"""
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period > chunk_size * 0.7:
                    end = start + last_period + 1
            chunks.append(text[start:end].strip())
            start = end - overlap
        return chunks


class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_db = ChromaVectorDB()
        self.chunker = DocumentChunker()
    
    async def initialize(self):
        """Initialize RAG service"""
        await self.embedding_model.load()
        await self.vector_db.connect()
    
    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Add document to RAG system"""
        try:
            chunks = self.chunker.chunk_text(content)
            embeddings = await self.embedding_model.embed_batch(chunks)
            if not embeddings:
                return 0
            added = 0
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_metadata = {
                    **metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                success = await self.vector_db.add_chunk(
                    chunk_id=chunk_id,
                    content=chunk,
                    embedding=embedding,
                    metadata=chunk_metadata
                )
                if success:
                    added += 1
            return added
        except Exception as e:
            print(f"Error adding document: {e}")
            return 0
    
    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Retrieve relevant context for a query"""
        try:
            query_embedding = await self.embedding_model.embed(query)
            if not query_embedding:
                return [], ""
            chunks = await self.vector_db.search(query_embedding, top_k)
            context = "Retrieved Context:\n\n"
            for i, chunk in enumerate(chunks, 1):
                source = chunk["metadata"].get("title", "Unknown")
                content = chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
                context += f"{i}. [From: {source}]\n{content}\n\n"
            return chunks, context
        except Exception as e:
            print(f"Retrieval error: {e}")
            return [], ""


_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create singleton RAG service"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
