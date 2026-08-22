from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import asyncio
from typing import Optional, Dict, Any
from services.ai_service import get_ai_service
from utils.auth_utils import verify_token

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.post("/message")
async def send_message(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    token: Optional[str] = None,
    use_rag: bool = False,
    tool_id: Optional[str] = None,
    tool_args: Optional[Dict[str, Any]] = None
):
    """
    Send a message and get AI response (HTTP endpoint)
    
    Args:
        user_id: User ID
        message: User message
        conversation_id: Optional conversation ID
        token: JWT token for auth
        use_rag: Use RAG retrieval from uploaded documents
        tool_id: Execute a specific tool
        tool_args: Arguments for the tool
    """
    
    # Verify token if provided
    if token:
        decoded = verify_token(token)
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    ai_service = get_ai_service()
    result = await ai_service.generate_response(
        user_id=user_id,
        message=message,
        conversation_id=conversation_id,
        use_rag=use_rag,
        tool_id=tool_id,
        tool_args=tool_args
    )
    
    return JSONResponse(content=result)


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50
):
    """
    Get conversation history
    
    Args:
        conversation_id: Conversation ID
        limit: Number of messages to retrieve
    """
    ai_service = get_ai_service()
    messages = await ai_service.get_conversation_history(
        conversation_id=conversation_id,
        limit=limit
    )
    
    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "count": len(messages)
    }


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat
    
    Expects JSON:
    {
        "message": "user message",
        "conversation_id": "optional_conv_id",
        "user_id": "user_123"
    }
    """
    await manager.connect(websocket)
    ai_service = get_ai_service()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                user_msg = message_data.get("message") or message_data.get("text", "")
                user_id = message_data.get("user_id") or client_id
                conversation_id = message_data.get("conversation_id")
                use_rag = bool(message_data.get("use_rag", False))
                tool_id = message_data.get("tool_id")
                tool_args = message_data.get("tool_args")
            except Exception:
                user_msg = data
                user_id = client_id
                conversation_id = None
                use_rag = False
                tool_id = None
                tool_args = None
            
            if not user_msg:
                await websocket.send_json({
                    "type": "error",
                    "content": "Empty message"
                })
                continue
            
            # Generate response using AI Service
            result = await ai_service.generate_response(
                user_id=user_id,
                message=user_msg,
                conversation_id=conversation_id,
                use_rag=use_rag,
                tool_id=tool_id,
                tool_args=tool_args
            )
            
            response = result.get("response", "")
            conv_id = result.get("conversation_id", "")
            
            # Stream response word by word
            for word in response.split(" "):
                await websocket.send_json({
                    "type": "stream",
                    "content": word + " ",
                    "conversation_id": conv_id
                })
                await asyncio.sleep(0.05)  # Typing effect
            
            # Send completion signal
            await websocket.send_json({
                "type": "end",
                "conversation_id": conv_id,
                "metadata": result.get("metadata", {})
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
        manager.disconnect(websocket)
