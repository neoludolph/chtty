# Importiert BaseModel von Pydantic für Datenvalidierung
from pydantic import BaseModel
# Importiert Union für Typ-Hinweise (wird hier aber nicht explizit genutzt)
from typing import Union

# Definiert das Datenmodell für Raumdaten
class RoomData(BaseModel):
    # Definiert den Raumnamen als String
    roomname: str
    # Definiert das Passwort als String
    password: str

# Definiert das Datenmodell für den Beitritt zu einem Raum
class JoinRoomData(BaseModel):
    # Definiert den Nachrichtentyp als String
    type: str
    # Definiert den Raumnamen als String
    roomname: str
    # Definiert das Passwort als String
    password: str
    # Definiert den Benutzernamen als String
    username: str

# Definiert das Datenmodell für Chat-Nachrichten
class ChatMessage(BaseModel):
    # Definiert den Nachrichtentyp als String
    type: str
    # Definiert den Benutzernamen als String
    username: str
    # Definiert die Chat-Nachricht als String
    chat_message: str

# Definiert das Datenmodell für Antworten auf Raumanfragen
class RoomDataResponse(BaseModel):
    # Definiert die Antwortnachricht als String
    response_message: str

# Definiert das Datenmodell für Überprüfungsergebnisse
class CheckResult(BaseModel):
    # Definiert das Ergebnis als Boolean
    result: bool
    # Definiert eine optionale Fehlermeldung
    error_message: str | None = None

# Definiert das Datenmodell für Login-Daten
class LoginData(BaseModel):
    # Definiert den Benutzernamen als String
    username: str
    # Definiert den Raumnamen als String
    roomname: str
    # Definiert das Passwort als String
    password: str