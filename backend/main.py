from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from contextlib import asynccontextmanager
from backend.models.room_models import RoomData, RoomDataResponse
from backend.database.database import create_db, dispose_db, create_room
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    print("Database created")
    yield
    dispose_db()
    print("Connection closed")

app = FastAPI(lifespan=lifespan)

# @app.websocket("/ws/{room_id}")
# async def websocket_endpoint(websocket: WebSocket, roomname: str):
#     await websocket.accept()
#     if room_id not in rooms:
#         rooms[room_id] = set()
#     rooms[room_id].add(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             parsed_data = json.loads(data)
#             if parsed_data.get('type') == 'join':
#                 username = parsed_data.get('username')
#                 dumped_data_join = json.dumps(parsed_data)
#                 for client in rooms[room_id]:
#                     if client is websocket:
#                         continue         
#                     await client.send_text(dumped_data_join)
#             elif parsed_data.get('type') == 'message':
#                 dumped_data_message = json.dumps(parsed_data)
#                 for client in rooms[room_id]:
#                     if client is websocket:
#                         continue
#                     await client.send_text(dumped_data_message)
#     except WebSocketDisconnect:
#         rooms[room_id].discard(websocket)
#     if not rooms[room_id]:
#         del rooms[room_id]

@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    result = create_room(room_data.roomname, room_data.password, room_data.username)
    return result