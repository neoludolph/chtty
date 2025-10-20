from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
import json
import sqlite3

app = FastAPI()

rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)
            if parsed_data.get('type') == 'join':
                username = parsed_data.get('user_name')
                dumped_data_join = json.dumps(parsed_data)
                for client in rooms[room_id]:
                    if client is websocket:
                        continue
                    await client.send_text(dumped_data_join)
            elif parsed_data.get('type') == 'message':
                dumped_data_message = json.dumps(parsed_data)
                for client in rooms[room_id]:
                    if client is websocket:
                        continue
                    await client.send_text(dumped_data_message)
    except WebSocketDisconnect:
        rooms[room_id].discard(websocket)
    if not rooms[room_id]:
        del rooms[room_id]