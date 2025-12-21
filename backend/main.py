# Imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.room_models import (
    RoomData, 
    JoinRoomData, 
    RoomDataResponse , 
    CheckResult,
    ChatMessage,
    LoginData
)
from database.database import (
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

# Anwendungs-Lebenszyklus
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verwaltet Startup und Shutdown der Anwendung"""
    # Startup: Datenbank erstellen
    create_db()
    print("Database created")
    yield
    # Shutdown: Datenbankverbindung schließen
    dispose_db()
    print("Connection closed")

# FastAPI-Anwendung initialisieren
app = FastAPI(lifespan=lifespan)

# CORS-Middleware konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globale Variablen
rooms = {}  # Dictionary für aktive Räume


# Hilfsfunktionen
def _validate_non_empty(value: str, field_name: str) -> str:
    """Validiert, dass ein String nicht leer ist"""
    if value is None or not value.strip():
        raise HTTPException(status_code=422, detail=f"{field_name} cannot be empty.")
    return value.strip()

async def broadcast_active_users(roomname: str):
    """Sendet die Liste der aktiven Benutzer an alle Clients im Raum"""
    active_users = get_users_in_room(roomname)
    payload = {
        "type": "active_users",
        "users": active_users
    }
    for client in rooms.get(roomname, set()):
        await client.send_json(payload)

# WebSocket-Endpunkt
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    """WebSocket-Endpunkt für Chat-Kommunikation"""
    await websocket.accept()
    
    # Beitrittsdaten empfangen und validieren
    join_data = await websocket.receive_text()
    join_data_pydantic = JoinRoomData.model_validate_json(join_data)
    
    # Raum- und Passwortüberprüfung
    room_check = check_if_db_room_exists(join_data_pydantic.roomname)
    if (room_check):
        password_check = check_if_password_is_correct(join_data_pydantic.roomname, join_data_pydantic.password)
        
        if (password_check is True):
            # Raum initialisieren und Client hinzufügen
            if (join_data_pydantic.roomname not in rooms):
                rooms[join_data_pydantic.roomname] = set()
            rooms[join_data_pydantic.roomname].add(websocket)
            save_user_in_db(join_data_pydantic.roomname, join_data_pydantic.username)
            
            # Chat-Verlauf abrufen und senden
            result = get_messages_from_db(join_data_pydantic.roomname)
            chat_history = [dict(rows._mapping) for rows in result]
            for row_dict in chat_history:
                row_dict["timestamp"] = str(row_dict["timestamp"])
            await websocket.send_json({
                "type": "chat_history_type",
                "chat_history": chat_history
            })
            
            # Beitritt speichern und andere Clients benachrichtigen
            save_message_in_db(join_data_pydantic.roomname, "entered the chat!", join_data_pydantic.username)
            for client in rooms[join_data_pydantic.roomname]:
                if (client is websocket):
                    continue
                await client.send_json({
                    "type": "join",
                    "username": join_data_pydantic.username
                })
            await broadcast_active_users(join_data_pydantic.roomname)
            
            # Nachrichtenschleife
            try:
                while True:
                    # Nachricht empfangen und an andere Clients weiterleiten
                    received_message = await websocket.receive_text()
                    received_message_parsed = ChatMessage.model_validate_json(received_message)
                    for client in rooms[join_data_pydantic.roomname]:
                        if (client is websocket):
                            continue
                        await client.send_text(received_message)
                    save_message_in_db(join_data_pydantic.roomname, received_message_parsed.chat_message, received_message_parsed.username)
            
            # Verbindungsabbruch behandeln
            except WebSocketDisconnect:
                rooms[join_data_pydantic.roomname].discard(websocket)
                save_message_in_db(join_data_pydantic.roomname, "left the chat!", join_data_pydantic.username)
                delete_user_from_db(join_data_pydantic.username)
                
                # Andere Clients über Verlassen benachrichtigen
                for client in rooms[join_data_pydantic.roomname]:
                    if (client is websocket):
                        continue
                    await client.send_json({
                        "type": "leave",
                        "username": join_data_pydantic.username
                    })
                await broadcast_active_users(join_data_pydantic.roomname)
            
            # Raum löschen, wenn leer
            if not rooms[join_data_pydantic.roomname]:
                del rooms[join_data_pydantic.roomname]


# REST-API-Endpunkte
@app.post("/get_checks", response_model=CheckResult)
async def get_checks(room_data: LoginData):
    """Überprüft Raum, Passwort und Benutzername vor dem Beitritt"""
    # Eingaben validieren
    username = _validate_non_empty(room_data.username, "Username")
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    password = _validate_non_empty(room_data.password, "Password")

    # Raum- und Passwortüberprüfung
    if not check_if_db_room_exists(roomname):
        raise HTTPException(status_code=404, detail="Room does not exist!")

    if not check_if_password_is_correct(roomname, password):
        raise HTTPException(status_code=401, detail="The entered password is wrong!")

    # Benutzernamen-Verfügbarkeit prüfen
    if check_if_user_exists_in_db(username):
        raise HTTPException(
            status_code=409,
            detail="Your entered username is already taken by someone else!",
        )

    return CheckResult(result=True)

@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    """Erstellt einen neuen Raum"""
    # Eingaben validieren
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    password = _validate_non_empty(room_data.password, "Password")

    # Prüfen, ob Raum bereits existiert
    if check_if_db_room_exists(roomname):
        raise HTTPException(status_code=400, detail="Room already exists!")

    # Raum erstellen
    rooms[roomname] = set()
    result = create_db_room(roomname, password)
    return result

@app.delete("/delete-room", response_model=RoomDataResponse)
async def delete_db_room_(room_data: RoomData):
    """Löscht einen Raum"""
    # Eingaben validieren
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    password = _validate_non_empty(room_data.password, "Password")

    # Raum- und Passwortüberprüfung
    if not check_if_db_room_exists(roomname):
        raise HTTPException(status_code=404, detail="Room does not exist!")

    if not check_if_password_is_correct(roomname, password):
        raise HTTPException(status_code=401, detail="The entered password is wrong!")

    # Raum löschen
    result = delete_db_room(roomname, password)
    rooms.pop(roomname, None)
    return result

# Debug-Endpunkte zum Löschen von Daten
@app.delete("/delete_rooms_table_content")
async def delete_rooms_table_content_():
    """Löscht alle Räume aus der Datenbank"""
    result = delete_rooms_table_content()
    return result

@app.delete("/delete_users_table_content")
async def delete_users_table_content_():
    """Löscht alle Benutzer aus der Datenbank"""
    result = delete_users_table_content()
    return result

@app.delete("/delete_messages_table_content")
async def delete_messages_table_content_():
    """Löscht alle Nachrichten aus der Datenbank"""
    result = delete_messages_table_content()
    return result

@app.delete("/delete_all_tables_content")
async def delete_all_tables_content_():
    """Löscht alle Daten aus allen Tabellen"""
    result = delete_all_tables_content()
    return result

@app.delete("/delete_db")
async def delete_db_():
    """Löscht die Datenbankdatei"""
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database does not exist!")
    result = delete_db(db_path)
    return result
