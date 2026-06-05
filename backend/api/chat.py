from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Parse the incoming message
            try:
                message_data = json.loads(data)
                user_msg = message_data.get("message", "")
            except:
                user_msg = data
            
            # Simulate an AI typing delay and streaming response
            response = f"I am CETRI, your AI assistant. You said: {user_msg}"
            
            # Streaming simulation
            for word in response.split(" "):
                await websocket.send_json({
                    "type": "stream",
                    "content": word + " "
                })
                await asyncio.sleep(0.05) # Simulated typing delay
                
            await websocket.send_json({
                "type": "end",
                "content": ""
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
