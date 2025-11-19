from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.room_models import RoomData, JoinRoomData, RoomDataResponse , ChatMessage
from backend.database.database import (
    create_db, 
    dispose_db, 
    create_room, 
    delete_room,
    delete_rooms_table_content, 
    delete_users_table_content, 
    delete_messages_table_content, 
    delete_all_tables_content,
    check_if_room_exists,
    check_if_password_is_correct,
    delete_db,
    db_path
)
import json
from typing import Set

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    print("Database created")
    yield
    dispose_db()
    print("Connection closed")

app = FastAPI(lifespan=lifespan)

# origins = [
#     "http://localhost:8000",
#     "http://localhost:5173",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = {}

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    join_data = await websocket.receive_text()
    join_data_pydantic = JoinRoomData.model_validate_json(join_data)
    room_check = check_if_room_exists(join_data_pydantic.roomname)
    if (room_check is True):
        password_check = check_if_password_is_correct(join_data_pydantic.roomname, join_data_pydantic.password)
        if (password_check is True):
            rooms[join_data_pydantic.roomname].add(websocket)
            try:
                while True:
                    received_message = await websocket.receive_text()
                    for client in rooms[join_data_pydantic.roomname]:
                        if (client is websocket):
                            continue
                        await client.send_text(received_message)
            except WebSocketDisconnect:
                rooms[join_data_pydantic.roomname].discard(websocket)
            if not rooms[join_data_pydantic.roomname]:
                del rooms[join_data_pydantic.roomname]
        else:
            password_error_data = {
                "type": "password_error",
                "error_message": "Wrong password! Please try again"
            }
            await websocket.send_json(password_error_data)
    else:
        room_error_data = {
            "type": "room_error",
            "error_message": "This room does not exist!"
        }
        await websocket.send_json(room_error_data)

@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    rooms[room_data.roomname] = set()
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

@app.delete("/delete_all_tables_content")
async def delete_all_tables_content_():
    result = delete_all_tables_content()
    return result

@app.delete("/delete_db")
async def delete_db_():
    result = delete_db(db_path)
    return result
