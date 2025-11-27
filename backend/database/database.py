
# Importiert SQLAlchemy als sqla
import sqlalchemy as sqla
# Importiert SQLAlchemyError für Fehlerbehandlung
from sqlalchemy.exc import SQLAlchemyError
# Importiert Path für Dateipfadoperationen
from pathlib import Path
# Importiert uuid für eindeutige IDs
import uuid
# Importiert bcrypt für Passwort-Hashing
import bcrypt
# Importiert RoomDataResponse aus den Raummodellen
from models.room_models import RoomDataResponse
# Importiert Tabellendefinitionen aus den Datenbankmodellen
from database.models import rooms, users, messages, metadata
# Importiert shutil für Dateioperationen
import shutil
# Importiert os für Betriebssystemfunktionen
import os


# Definiert eine Funktion zum Hashen von Passwörtern
def hash_password(password: str) -> str:
    # Generiert ein Salt für das Hashing
    salt = bcrypt.gensalt()
    # Hasht das Passwort mit dem Salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Gibt das gehashte Passwort als String zurück
    return hashed.decode('utf-8')


# Definiert eine Funktion zum Überprüfen von Passwörtern
def verify_password(password: str, hashed_password: str) -> bool:
    # Überprüft das Passwort gegen den Hash
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Ermittelt den Pfad der aktuellen Datei
current_file = Path(__file__).parent
# Setzt den Pfad zur Datenbankdatei
db_path = current_file / 'database.db'
# Setzt den Pfad zur Vorlagen-Datenbankdatei
template_db_path = current_file / 'database_empty.db'

# Überprüft, ob die Datenbankdatei existiert
if not os.path.exists(db_path):
    # Gibt eine Meldung aus, dass eine neue Datenbank erstellt wird
    print("-> No database found! Create new from template ...")
    # Kopiert die Vorlagen-Datenbank zur Datenbankdatei
    shutil.copy(template_db_path, db_path)

# Erstellt die Datenbank-Engine
engine = sqla.create_engine(f"sqlite:///{db_path}", echo=True)

# Definiert eine Funktion zum Erstellen der Datenbanktabellen
def create_db():
    # Erstellt alle Tabellen basierend auf den Metadaten
    metadata.create_all(engine)

# Definiert eine Funktion zum Schließen der Datenbankverbindung
def dispose_db():
    # Schließt die Engine-Verbindung
    engine.dispose()

# Definiert eine Funktion zum Erstellen eines Raums in der Datenbank
def create_db_room(roomname, password):
    # Hasht das Passwort
    hashed_pw = hash_password(password)
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Fügt den neuen Raum in die Tabelle ein
        connect.execute(rooms.insert().values(roomname=roomname, password=hashed_pw))
    # Setzt die Erfolgsmeldung
    message = "Room successfully created!"
    # Erstellt die Antwort
    response = RoomDataResponse(response_message=message)
    # Gibt die Antwort zurück
    return response

# Definiert eine Funktion zum Löschen eines Raums aus der Datenbank
def delete_db_room(roomname, password):
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
       # Fragt das Passwort des Raums ab
       password_query = connect.execute(sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)).first()
    # Überprüft, ob der Raum existiert
    if (password_query is None):
        # Setzt die Fehlermeldung
        message = "Room does not exist!"
        # Erstellt die Antwort
        response = RoomDataResponse(response_message=message)
        # Gibt die Antwort zurück
        return response
    # Überprüft das Passwort
    elif verify_password(password, password_query[0]):
        # Startet eine Datenbanktransaktion
        with engine.begin() as connect:
            # Löscht alle Nachrichten dieses Raums
            connect.execute(sqla.delete(messages).where(messages.c.roomname == roomname))
            # Löscht alle Benutzer dieses Raums
            connect.execute(sqla.delete(users).where(users.c.roomname == roomname))
            # Löscht den Raum selbst
            connect.execute(sqla.delete(rooms).where(rooms.c.roomname == roomname))
        # Setzt die Erfolgsmeldung
        message = "Room successfully deleted!"
        # Erstellt die Antwort
        response = RoomDataResponse(response_message=message)
        # Gibt die Antwort zurück
        return response
    # Wenn das Passwort falsch ist
    else:
        # Setzt die Fehlermeldung
        message = "The entered password is wrong!"
        # Erstellt die Antwort
        response = RoomDataResponse(response_message=message)
        # Gibt die Antwort zurück
        return response

# Funktionen für API-Routen
# Definiert eine Funktion zum Löschen aller Räume
def delete_rooms_table_content():
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Löscht alle Einträge aus der Tabelle 'rooms'
        connect.execute(sqla.delete(rooms))
    # Setzt die Erfolgsmeldung
    message = "Table content of rooms successfully deleted!"
    # Gibt die Meldung zurück
    return message

# Definiert eine Funktion zum Löschen aller Benutzer
def delete_users_table_content():
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Löscht alle Einträge aus der Tabelle 'users'
        connect.execute(sqla.delete(users))
    # Setzt die Erfolgsmeldung
    message = "Table content of users successfully deleted!"
    # Gibt die Meldung zurück
    return message

# Definiert eine Funktion zum Löschen aller Nachrichten
def delete_messages_table_content():
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Löscht alle Einträge aus der Tabelle 'messages'
        connect.execute(sqla.delete(messages))
    # Setzt die Erfolgsmeldung
    message = "Table content of messages successfully deleted!"
    # Gibt die Meldung zurück
    return message

# Definiert eine Funktion zum Löschen aller Tabelleninhalte
def delete_all_tables_content():
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Löscht alle Nachrichten
        connect.execute(sqla.delete(messages))
        # Löscht alle Benutzer
        connect.execute(sqla.delete(users))
        # Löscht alle Räume
        connect.execute(sqla.delete(rooms))
    # Setzt die Erfolgsmeldung
    message = "Content of all tables deleted!"
    # Gibt die Meldung zurück
    return message

# Definiert eine Funktion zum Löschen der Datenbankdatei
def delete_db(db_path):
    # Überprüft, ob die Datei existiert
    if (os.path.exists(db_path)):
        # Löscht die Datei
        os.remove(db_path)
        # Gibt eine Erfolgsmeldung zurück
        return "Database deleted!"
    # Wenn die Datei nicht existiert
    else:
        # Gibt eine Fehlermeldung zurück
        return "Database does not exist!"

# Datenbank-Überprüfungsfunktionen
# Definiert eine Funktion zum Überprüfen, ob ein Raum existiert
def check_if_db_room_exists(roomname):
    # Erstellt die Abfrage
    check = sqla.select(rooms.c.roomname).where(rooms.c.roomname == roomname)
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Führt die Abfrage aus
        result = connect.execute(check).first()
    # Wenn kein Ergebnis gefunden wurde
    if (result is None):
        # Gibt False zurück
        return False
    # Wenn ein Ergebnis gefunden wurde
    else:
        # Gibt True zurück
        return True 
    
# Definiert eine Funktion zum Überprüfen des Passworts
def check_if_password_is_correct(roomname, password):
    # Erstellt die Abfrage für das Passwort
    check = sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Führt die Abfrage aus
        result = connect.execute(check).first()
    # Überprüft das Passwort, falls ein Ergebnis gefunden wurde
    if result is not None and verify_password(password, result[0]):
        # Gibt True zurück
        return True
    # Wenn das Passwort falsch ist oder der Raum nicht existiert
    else: 
        # Gibt False zurück
        return False
    
# Definiert eine Funktion zum Speichern einer Nachricht
def save_message_in_db(roomname, message, username):
    # Generiert eine eindeutige Nachrichten-ID
    message_id = str(uuid.uuid4())
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Erstellt die Einfüge-Anweisung
        message_query = sqla.insert(messages).values(
            message_id=message_id,
            chat_message=message,
            roomname=roomname,
            username=username
        )
        # Führt die Anweisung aus
        connect.execute(message_query)
    
# Definiert eine Funktion zum Speichern eines Benutzers
def save_user_in_db(roomname, username):
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Löscht den Benutzer, falls er bereits existiert
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        # Führt die Löschung aus
        connect.execute(delete_user_from_users)
        # Erstellt die Einfüge-Anweisung für den Benutzer
        user_insertion = sqla.insert(users).values(
            username=username,
            roomname=roomname,
        )
        # Führt die Einfügung aus
        connect.execute(user_insertion)
    
# Definiert eine Funktion zum Löschen eines Benutzers
def delete_user_from_db(username):
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Erstellt die Lösch-Anweisung
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        # Führt die Löschung aus
        connect.execute(delete_user_from_users)

# Definiert eine Funktion zum Überprüfen, ob ein Benutzer existiert
def check_if_user_exists_in_db(username):
    # Erstellt die Abfrage
    user_check = sqla.select(users.c.username).where(users.c.username == username)
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Führt die Abfrage aus
        result = connect.execute(user_check).first()
    # Wenn kein Ergebnis gefunden wurde
    if (result is None):
        # Gibt False zurück
        return False
    # Wenn ein Ergebnis gefunden wurde
    else:
        # Gibt True zurück
        return True 
    
# Definiert eine Funktion zum Abrufen von Nachrichten
def get_messages_from_db(roomname):
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Erstellt die Abfrage für Nachrichten, sortiert nach Zeitstempel
        get_messages = sqla.select(messages.c.chat_message, messages.c.username, messages.c.timestamp).where(messages.c.roomname == roomname).order_by(messages.c.timestamp)
        # Führt die Abfrage aus und holt alle Ergebnisse
        result = connect.execute(get_messages).fetchall()
    # Gibt die Ergebnisse zurück
    return result

# Definiert eine Funktion zum Abrufen der Benutzer in einem Raum
def get_users_in_room(roomname):
    # Startet eine Datenbanktransaktion
    with engine.begin() as connect:
        # Erstellt die Abfrage für Benutzernamen, sortiert nach Benutzername
        query = sqla.select(users.c.username).where(users.c.roomname == roomname).order_by(users.c.username)
        # Führt die Abfrage aus und holt alle Ergebnisse
        result = connect.execute(query).fetchall()
    # Gibt eine Liste der Benutzernamen zurück
    return [row[0] for row in result]
