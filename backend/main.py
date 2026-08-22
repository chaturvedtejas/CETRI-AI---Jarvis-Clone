from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import auth, chat, memory, tools, documents, rag
from database.models import init_db, engine, Base

# Initialize database on startup
def startup_event():
    """Initialize database on app startup"""
    print("🗄️  Initializing database...")
    init_db()
    print("✓ Database initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle management"""
    # Startup
    startup_event()
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="CETRI AI OS",
    description="Backend API for CETRI Intelligent AI Operating Assistant",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CETRI Backend is running",
        "status": "online",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "memory": "/api/memory",
            "tools": "/api/tools",
            "documents": "/api/documents",
            "rag": "/api/rag",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
