from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from contextlib import asynccontextmanager
from backend.models.room_models import (
    RoomData, 
    JoinRoomData, 
    RoomDataResponse , 
    CheckResult,
    ChatMessage,
    LoginData
)
from backend.database.database import (
    create_db, 
    dispose_db, 
    create_db_room, 
    delete_db_room,
    delete_rooms_table_content, 
    delete_users_table_content, 
    delete_messages_table_content, 
    delete_all_tables_content,
    check_if_db_room_exists,
    check_if_password_is_correct,
    delete_db,
    db_path,
    save_message_in_db,
    save_user_in_db,
    delete_user_from_db,
    check_if_user_exists_in_db,
    get_messages_from_db,
    get_users_in_room
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

async def broadcast_active_users(roomname: str):
    active_users = get_users_in_room(roomname)
    payload = {
        "type": "active_users",
        "users": active_users
    }
    for client in rooms.get(roomname, set()):
        await client.send_json(payload)

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    join_data = await websocket.receive_text()
    join_data_pydantic = JoinRoomData.model_validate_json(join_data)
    room_check = check_if_db_room_exists(join_data_pydantic.roomname)
    if (room_check):
        password_check = check_if_password_is_correct(join_data_pydantic.roomname, join_data_pydantic.password)
        if (password_check is True):
            if (join_data_pydantic.roomname not in rooms):
                rooms[join_data_pydantic.roomname] = set()
            rooms[join_data_pydantic.roomname].add(websocket)
            save_user_in_db(join_data_pydantic.roomname, join_data_pydantic.username)
            result = get_messages_from_db(join_data_pydantic.roomname)
            chat_history = [dict(rows._mapping) for rows in result]
            for row_dict in chat_history:
                row_dict["timestamp"] = str(row_dict["timestamp"])
            await websocket.send_json({
                "type": "chat_history_type",
                "chat_history": chat_history
            })
            for client in rooms[join_data_pydantic.roomname]:
                if (client is websocket):
                    continue
                await client.send_json({
                    "type": "join",
                    "username": join_data_pydantic.username
                })
            await broadcast_active_users(join_data_pydantic.roomname)
            try:
                while True:
                    received_message = await websocket.receive_text()
                    received_message_parsed = ChatMessage.model_validate_json(received_message)
                    for client in rooms[join_data_pydantic.roomname]:
                        if (client is websocket):
                            continue
                        await client.send_text(received_message)
                    save_message_in_db(join_data_pydantic.roomname, received_message_parsed.chat_message, received_message_parsed.username)
            except WebSocketDisconnect:
                rooms[join_data_pydantic.roomname].discard(websocket)
                delete_user_from_db(join_data_pydantic.username)
                for client in rooms[join_data_pydantic.roomname]:
                    if (client is websocket):
                        continue
                    await client.send_json({
                        "type": "leave",
                        "username": join_data_pydantic.username
                    })
                await broadcast_active_users(join_data_pydantic.roomname)
            if not rooms[join_data_pydantic.roomname]:
                del rooms[join_data_pydantic.roomname]

@app.post("/get_checks", response_model=CheckResult)
async def get_checks(room_data: LoginData):
    check_room = check_if_db_room_exists(room_data.roomname)
    check_password = check_if_password_is_correct(room_data.roomname, room_data.password)
    check_user = check_if_user_exists_in_db(room_data.username)
    if (check_room is True and check_password is True):
        if (check_user):
            username_already_taken = "Your entered username is already taken by someone else!"
            response = CheckResult(result=False, error_message=username_already_taken)
            return response
        else:
            response = CheckResult(result=True)
            return response
    elif (check_room is True and check_password is False):
        wrong_password = "The entered password is wrong!"
        response = CheckResult(result=False, error_message=wrong_password)
        return response
    else:
        no_room = "Room does not exist!"
        response = CheckResult(result=False, error_message=no_room)
        return response

@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    if (check_if_db_room_exists(room_data.roomname)):
        raise HTTPException(status_code=400, detail="Room already exists!")
    rooms[room_data.roomname] = set()
    result = create_db_room(room_data.roomname, room_data.password)
    return result

@app.delete("/delete-room", response_model=RoomDataResponse)
async def delete_db_room_(room_data: RoomData):
    result = delete_db_room(room_data.roomname, room_data.password)
    return result

@app.delete("/delete_rooms_table_content")
async def delete_rooms_table_content_():
    result = delete_rooms_table_content()
    return result

@app.delete("/delete_users_table_content")
async def delete_users_table_content_():
    result = delete_users_table_content()
    return result

@app.delete("/delete_messages_table_content")
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
