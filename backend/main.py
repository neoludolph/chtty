# Importiert FastAPI und WebSocket für die Webanwendung
from fastapi import FastAPI, WebSocket
# Importiert WebSocketDisconnect für Verbindungsabbrüche
from fastapi import WebSocketDisconnect
# Importiert CORSMiddleware für Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware
# Importiert HTTPException für Fehlerbehandlung
from fastapi import HTTPException
# Importiert asynccontextmanager für Lebenszyklus-Management
from contextlib import asynccontextmanager
# Importiert Datenmodelle aus room_models
from models.room_models import (
    RoomData, 
    JoinRoomData, 
    RoomDataResponse , 
    CheckResult,
    ChatMessage,
    LoginData
)
# Importiert Datenbankfunktionen aus database
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
# Importiert json für JSON-Verarbeitung
import json
# Importiert Set für Typ-Hinweise
from typing import Set

# Definiert den Lebenszyklus der Anwendung
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Erstellt die Datenbank beim Start
    create_db()
    # Gibt eine Meldung aus
    print("Database created")
    # Übergibt die Kontrolle an die Anwendung
    yield
    # Schließt die Datenbankverbindung beim Beenden
    dispose_db()
    # Gibt eine Meldung aus
    print("Connection closed")

# Initialisiert die FastAPI-Anwendung mit dem Lebenszyklus
app = FastAPI(lifespan=lifespan)

# Fügt CORS-Middleware hinzu
app.add_middleware(
    CORSMiddleware,
    # Erlaubt alle Ursprünge
    allow_origins=["*"],
    # Erlaubt Anmeldeinformationen
    allow_credentials=True,
    # Erlaubt alle Methoden
    allow_methods=["*"],
    # Erlaubt alle Header
    allow_headers=["*"],
)

# Initialisiert ein Dictionary für aktive Räume
rooms = {}


# Validiert, dass ein String nicht leer ist
def _validate_non_empty(value: str, field_name: str) -> str:
    # Überprüft, ob der Wert None oder leer ist
    if value is None or not value.strip():
        # Wirft eine Ausnahme, wenn der Wert ungültig ist
        raise HTTPException(status_code=422, detail=f"{field_name} cannot be empty.")
    # Gibt den bereinigten String zurück
    return value.strip()

# Sendet die Liste der aktiven Benutzer an alle Clients im Raum
async def broadcast_active_users(roomname: str):
    # Holt die aktiven Benutzer aus der Datenbank
    active_users = get_users_in_room(roomname)
    # Erstellt das Payload-Objekt
    payload = {
        "type": "active_users",
        "users": active_users
    }
    # Sendet das Payload an alle verbundenen Clients
    for client in rooms.get(roomname, set()):
        await client.send_json(payload)

# Definiert den WebSocket-Endpunkt für den Chat
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    # Akzeptiert die WebSocket-Verbindung
    await websocket.accept()
    # Empfängt die Beitrittsdaten
    join_data = await websocket.receive_text()
    # Validiert die Beitrittsdaten
    join_data_pydantic = JoinRoomData.model_validate_json(join_data)
    # Überprüft, ob der Raum existiert
    room_check = check_if_db_room_exists(join_data_pydantic.roomname)
    # Wenn der Raum existiert
    if (room_check):
        # Überprüft das Passwort
        password_check = check_if_password_is_correct(join_data_pydantic.roomname, join_data_pydantic.password)
        # Wenn das Passwort korrekt ist
        if (password_check is True):
            # Erstellt den Raum im Speicher, falls er nicht existiert
            if (join_data_pydantic.roomname not in rooms):
                rooms[join_data_pydantic.roomname] = set()
            # Fügt den Client zum Raum hinzu
            rooms[join_data_pydantic.roomname].add(websocket)
            # Speichert den Benutzer in der Datenbank
            save_user_in_db(join_data_pydantic.roomname, join_data_pydantic.username)
            # Holt den Chat-Verlauf aus der Datenbank
            result = get_messages_from_db(join_data_pydantic.roomname)
            # Konvertiert die Ergebnisse in Dictionaries
            chat_history = [dict(rows._mapping) for rows in result]
            # Konvertiert Zeitstempel in Strings
            for row_dict in chat_history:
                row_dict["timestamp"] = str(row_dict["timestamp"])
            # Sendet den Chat-Verlauf an den neuen Client
            await websocket.send_json({
                "type": "chat_history_type",
                "chat_history": chat_history
            })
            # Speichert die Beitrittsnachricht in der Datenbank
            save_message_in_db(join_data_pydantic.roomname, "entered the chat!", join_data_pydantic.username)
            # Benachrichtigt andere Clients über den Beitritt
            for client in rooms[join_data_pydantic.roomname]:
                # Überspringt den sendenden Client
                if (client is websocket):
                    continue
                # Sendet die Beitrittsnachricht
                await client.send_json({
                    "type": "join",
                    "username": join_data_pydantic.username
                })
            # Aktualisiert die Liste der aktiven Benutzer
            await broadcast_active_users(join_data_pydantic.roomname)
            # Startet die Nachrichtenschleife
            try:
                while True:
                    # Empfängt eine Nachricht vom Client
                    received_message = await websocket.receive_text()
                    # Validiert die Nachricht
                    received_message_parsed = ChatMessage.model_validate_json(received_message)
                    # Sendet die Nachricht an alle anderen Clients im Raum
                    for client in rooms[join_data_pydantic.roomname]:
                        # Überspringt den sendenden Client
                        if (client is websocket):
                            continue
                        # Sendet die Nachricht
                        await client.send_text(received_message)
                    # Speichert die Nachricht in der Datenbank
                    save_message_in_db(join_data_pydantic.roomname, received_message_parsed.chat_message, received_message_parsed.username)
            # Behandelt Verbindungsabbrüche
            except WebSocketDisconnect:
                # Entfernt den Client aus dem Raum
                rooms[join_data_pydantic.roomname].discard(websocket)
                # Speichert die Verlassensnachricht in der Datenbank
                save_message_in_db(join_data_pydantic.roomname, "left the chat!", join_data_pydantic.username)
                # Löscht den Benutzer aus der Datenbank
                delete_user_from_db(join_data_pydantic.username)
                # Benachrichtigt andere Clients über das Verlassen
                for client in rooms[join_data_pydantic.roomname]:
                    # Überspringt den sendenden Client
                    if (client is websocket):
                        continue
                    # Sendet die Verlassensnachricht
                    await client.send_json({
                        "type": "leave",
                        "username": join_data_pydantic.username
                    })
                # Aktualisiert die Liste der aktiven Benutzer
                await broadcast_active_users(join_data_pydantic.roomname)
            # Löscht den Raum, wenn er leer ist
            if not rooms[join_data_pydantic.roomname]:
                del rooms[join_data_pydantic.roomname]

# Definiert den Endpunkt für Überprüfungen
@app.post("/get_checks", response_model=CheckResult)
async def get_checks(room_data: LoginData):
    # Validiert den Benutzernamen
    username = _validate_non_empty(room_data.username, "Username")
    # Validiert den Raumnamen
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    # Validiert das Passwort
    password = _validate_non_empty(room_data.password, "Password")

    # Überprüft, ob der Raum existiert
    if not check_if_db_room_exists(roomname):
        # Wirft Fehler, wenn Raum nicht existiert
        raise HTTPException(status_code=404, detail="Room does not exist!")

    # Überprüft das Passwort
    if not check_if_password_is_correct(roomname, password):
        # Wirft Fehler, wenn Passwort falsch ist
        raise HTTPException(status_code=401, detail="The entered password is wrong!")

    # Überprüft, ob der Benutzername bereits vergeben ist
    if check_if_user_exists_in_db(username):
        # Wirft Fehler, wenn Benutzername vergeben ist
        raise HTTPException(
            status_code=409,
            detail="Your entered username is already taken by someone else!",
        )

    # Gibt Erfolg zurück
    return CheckResult(result=True)

# Definiert den Endpunkt zum Erstellen eines Raums
@app.post("/create-room", response_model=RoomDataResponse)
async def create_room_(room_data: RoomData):
    # Validiert den Raumnamen
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    # Validiert das Passwort
    password = _validate_non_empty(room_data.password, "Password")

    # Überprüft, ob der Raum bereits existiert
    if check_if_db_room_exists(roomname):
        # Wirft Fehler, wenn Raum existiert
        raise HTTPException(status_code=400, detail="Room already exists!")

    # Initialisiert den Raum im Speicher
    rooms[roomname] = set()
    # Erstellt den Raum in der Datenbank
    result = create_db_room(roomname, password)
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen eines Raums
@app.delete("/delete-room", response_model=RoomDataResponse)
async def delete_db_room_(room_data: RoomData):
    # Validiert den Raumnamen
    roomname = _validate_non_empty(room_data.roomname, "Room name")
    # Validiert das Passwort
    password = _validate_non_empty(room_data.password, "Password")

    # Überprüft, ob der Raum existiert
    if not check_if_db_room_exists(roomname):
        # Wirft Fehler, wenn Raum nicht existiert
        raise HTTPException(status_code=404, detail="Room does not exist!")

    # Überprüft das Passwort
    if not check_if_password_is_correct(roomname, password):
        # Wirft Fehler, wenn Passwort falsch ist
        raise HTTPException(status_code=401, detail="The entered password is wrong!")

    # Löscht den Raum aus der Datenbank
    result = delete_db_room(roomname, password)
    # Entfernt den Raum aus dem Speicher
    rooms.pop(roomname, None)
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen aller Räume
@app.delete("/delete_rooms_table_content")
async def delete_rooms_table_content_():
    # Löscht den Inhalt der Raumtabelle
    result = delete_rooms_table_content()
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen aller Benutzer
@app.delete("/delete_users_table_content")
async def delete_users_table_content_():
    # Löscht den Inhalt der Benutzertabelle
    result = delete_users_table_content()
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen aller Nachrichten
@app.delete("/delete_messages_table_content")
async def delete_messages_table_content_():
    # Löscht den Inhalt der Nachrichtentabelle
    result = delete_messages_table_content()
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen aller Tabelleninhalte
@app.delete("/delete_all_tables_content")
async def delete_all_tables_content_():
    # Löscht den Inhalt aller Tabellen
    result = delete_all_tables_content()
    # Gibt das Ergebnis zurück
    return result

# Definiert den Endpunkt zum Löschen der Datenbank
@app.delete("/delete_db")
async def delete_db_():
    # Überprüft, ob die Datenbankdatei existiert
    if not db_path.exists():
        # Wirft Fehler, wenn Datenbank nicht existiert
        raise HTTPException(status_code=404, detail="Database does not exist!")
    # Löscht die Datenbankdatei
    result = delete_db(db_path)
    # Gibt das Ergebnis zurück
    return result
