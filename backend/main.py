from fastapi import FastAPI, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from api import auth, chat

app = FastAPI(
    title="CETRI AI OS",
    description="Backend API for CETRI Intelligent AI Operating Assistant",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "CETRI Backend is running", "status": "online"}
