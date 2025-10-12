from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect

app = FastAPI()

rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept() 
    rooms[room_id] = websocket
    try:
        data = await websocket.receive_text()
        await websocket.send_text(data)
    except WebSocketDisconnect:
        del rooms[room_id]

