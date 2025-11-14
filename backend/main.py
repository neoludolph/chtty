from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.room_models import RoomData, RoomDataResponse, DeleteRoom
from backend.database.database import create_db, dispose_db, create_room, delete_room, delete_rooms_table_content, delete_users_table_content, delete_messages_table_content
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    print("Database created")
    yield
    dispose_db()
    print("Connection closed")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# @app.websocket("")
# async def chat():

# @app.post("/join")
# async def join_room_():

@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    result = create_room(room_data.roomname, room_data.password)
    return result

@app.delete("/delete-room", response_model=RoomDataResponse)
async def delete_room_(room_data: RoomData):
    result = delete_room(room_data.roomname, room_data.password)
    return result

@app.delete("/delete_rooms_table")
async def delete_rooms_table_content_():
    result = delete_rooms_table_content()
    return result

@app.delete("/delete_users_table")
async def delete_users_table_content_():
    result = delete_users_table_content()
    return result

@app.delete("/delete_messages_table")
async def delete_messages_table_content_():
    result = delete_messages_table_content()
    return result