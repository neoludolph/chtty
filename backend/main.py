from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect

app = FastAPI()

active_connections = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept() 
    active_connections[user_id] = websocket
    try:
        data = await websocket.receive_text()
        await websocket.send_text(f"Du: {data}")
    except WebSocketDisconnect:
        del active_connections[user_id]





