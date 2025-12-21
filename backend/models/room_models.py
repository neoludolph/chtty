# Imports
from pydantic import BaseModel
from typing import Union

# Pydantic-Modelle für API-Datenvalidierung
class RoomData(BaseModel):
    """Datenmodell für Raumdaten (Erstellen/Löschen)"""
    roomname: str
    password: str

class JoinRoomData(BaseModel):
    """Datenmodell für den Beitritt zu einem Raum"""
    type: str
    roomname: str
    password: str
    username: str

class ChatMessage(BaseModel):
    """Datenmodell für Chat-Nachrichten"""
    type: str
    username: str
    chat_message: str

class RoomDataResponse(BaseModel):
    """Datenmodell für Antworten auf Raumanfragen"""
    response_message: str

class CheckResult(BaseModel):
    """Datenmodell für Überprüfungsergebnisse"""
    result: bool
    error_message: str | None = None

class LoginData(BaseModel):
    """Datenmodell für Login-Daten"""
    username: str
    roomname: str
    password: str