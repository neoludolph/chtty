from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect

app = FastAPI()

rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = set()
    else:
        rooms[room_id].add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        del rooms[room_id].discard(websocket)
    if not rooms[room_id]:
        del rooms[room_id]