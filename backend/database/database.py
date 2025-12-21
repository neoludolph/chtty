# Imports
import sqlalchemy as sqla
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import uuid
import bcrypt
from models.room_models import RoomDataResponse
from database.models import rooms, users, messages, metadata
import shutil
import os


# Passwort-Hashing-Funktionen
def hash_password(password: str) -> str:
    """Hasht ein Passwort mit bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Überprüft ein Passwort gegen einen bcrypt-Hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Datenbankpfad-Konfiguration
current_file = Path(__file__).parent
db_path = current_file / 'database.db'
template_db_path = current_file / 'database_empty.db'

# Initialisierung: Erstelle Datenbank aus Template, falls nicht vorhanden
if not os.path.exists(db_path):
    print("-> No database found! Create new from template ...")
    shutil.copy(template_db_path, db_path)

# Datenbank-Engine erstellen
engine = sqla.create_engine(f"sqlite:///{db_path}", echo=True)

# Datenbank-Lebenszyklus-Funktionen
def create_db():
    """Erstellt alle Datenbanktabellen"""
    metadata.create_all(engine)

def dispose_db():
    """Schließt die Datenbankverbindung"""
    engine.dispose()

# Raum-Verwaltungsfunktionen
def create_db_room(roomname, password):
    """Erstellt einen neuen Raum in der Datenbank"""
    hashed_pw = hash_password(password)
    with engine.begin() as connect:
        connect.execute(rooms.insert().values(roomname=roomname, password=hashed_pw))
    message = "Room successfully created!"
    response = RoomDataResponse(response_message=message)
    return response

def delete_db_room(roomname, password):
    """Löscht einen Raum aus der Datenbank nach Passwortüberprüfung"""
    # Passwort des Raums abrufen
    with engine.begin() as connect:
       password_query = connect.execute(sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)).first()
    
    # Raum existiert nicht
    if (password_query is None):
        message = "Room does not exist!"
        response = RoomDataResponse(response_message=message)
        return response
    
    # Passwort ist korrekt - Raum und zugehörige Daten löschen
    elif verify_password(password, password_query[0]):
        with engine.begin() as connect:
            connect.execute(sqla.delete(messages).where(messages.c.roomname == roomname))
            connect.execute(sqla.delete(users).where(users.c.roomname == roomname))
            connect.execute(sqla.delete(rooms).where(rooms.c.roomname == roomname))
        message = "Room successfully deleted!"
        response = RoomDataResponse(response_message=message)
        return response
    
    # Passwort ist falsch
    else:
        message = "The entered password is wrong!"
        response = RoomDataResponse(response_message=message)
        return response

# API-Funktionen zum Löschen von Tabelleninhalten
def delete_rooms_table_content():
    """Löscht alle Einträge aus der Tabelle 'rooms'"""
    with engine.begin() as connect:
        connect.execute(sqla.delete(rooms))
    message = "Table content of rooms successfully deleted!"
    return message

def delete_users_table_content():
    """Löscht alle Einträge aus der Tabelle 'users'"""
    with engine.begin() as connect:
        connect.execute(sqla.delete(users))
    message = "Table content of users successfully deleted!"
    return message

def delete_messages_table_content():
    """Löscht alle Einträge aus der Tabelle 'messages'"""
    with engine.begin() as connect:
        connect.execute(sqla.delete(messages))
    message = "Table content of messages successfully deleted!"
    return message

def delete_all_tables_content():
    """Löscht alle Einträge aus allen Tabellen"""
    with engine.begin() as connect:
        connect.execute(sqla.delete(messages))
        connect.execute(sqla.delete(users))
        connect.execute(sqla.delete(rooms))
    message = "Content of all tables deleted!"
    return message

def delete_db(db_path):
    """Löscht die Datenbankdatei"""
    if (os.path.exists(db_path)):
        os.remove(db_path)
        return "Database deleted!"
    else:
        return "Database does not exist!"

# Datenbank-Überprüfungsfunktionen
def check_if_db_room_exists(roomname):
    """Überprüft, ob ein Raum in der Datenbank existiert"""
    check = sqla.select(rooms.c.roomname).where(rooms.c.roomname == roomname)
    with engine.begin() as connect:
        result = connect.execute(check).first()
    return result is not None
    
def check_if_password_is_correct(roomname, password):
    """Überprüft, ob das Passwort für einen Raum korrekt ist"""
    check = sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)
    with engine.begin() as connect:
        result = connect.execute(check).first()
    
    if result is not None and verify_password(password, result[0]):
        return True
    else: 
        return False
    
# Nachrichten- und Benutzerverwaltung
def save_message_in_db(roomname, message, username):
    """Speichert eine Nachricht in der Datenbank"""
    message_id = str(uuid.uuid4())
    with engine.begin() as connect:
        message_query = sqla.insert(messages).values(
            message_id=message_id,
            chat_message=message,
            roomname=roomname,
            username=username
        )
        connect.execute(message_query)
    
def save_user_in_db(roomname, username):
    """Speichert einen Benutzer in der Datenbank (löscht vorherige Einträge)"""
    with engine.begin() as connect:
        # Lösche vorherigen Eintrag, falls vorhanden
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        connect.execute(delete_user_from_users)
        
        # Füge Benutzer hinzu
        user_insertion = sqla.insert(users).values(
            username=username,
            roomname=roomname,
        )
        connect.execute(user_insertion)
    
def delete_user_from_db(username):
    """Löscht einen Benutzer aus der Datenbank"""
    with engine.begin() as connect:
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        connect.execute(delete_user_from_users)

def check_if_user_exists_in_db(username):
    """Überprüft, ob ein Benutzer in der Datenbank existiert"""
    user_check = sqla.select(users.c.username).where(users.c.username == username)
    with engine.begin() as connect:
        result = connect.execute(user_check).first()
    return result is not None
    
# Abruffunktionen
def get_messages_from_db(roomname):
    """Ruft alle Nachrichten eines Raums ab, sortiert nach Zeitstempel"""
    with engine.begin() as connect:
        get_messages = sqla.select(messages.c.chat_message, messages.c.username, messages.c.timestamp).where(messages.c.roomname == roomname).order_by(messages.c.timestamp)
        result = connect.execute(get_messages).fetchall()
    return result

def get_users_in_room(roomname):
    """Ruft alle Benutzer in einem Raum ab, sortiert nach Benutzername"""
    with engine.begin() as connect:
        query = sqla.select(users.c.username).where(users.c.roomname == roomname).order_by(users.c.username)
        result = connect.execute(query).fetchall()
    return [row[0] for row in result]
