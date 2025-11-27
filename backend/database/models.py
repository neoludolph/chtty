# Importiert SQLAlchemy als db
import sqlalchemy as db

# Erstellt ein MetaData-Objekt für die Datenbankstruktur
metadata = db.MetaData()

# Definiert die Tabelle 'rooms'
rooms = db.Table('rooms', metadata,
    # Definiert die Spalte 'roomname' als Primärschlüssel
    db.Column('roomname', db.String(30), primary_key=True),
    # Definiert die Spalte 'password' für bcrypt-Hashes (60 Zeichen)
    db.Column('password', db.String(60))
) 

# Definiert die Tabelle 'users'
users = db.Table('users', metadata,
    # Definiert die Spalte 'username' als Primärschlüssel
    db.Column('username', db.String(30), primary_key=True),
    # Definiert die Spalte 'roomname' als Fremdschlüssel zu 'rooms'
    db.Column('roomname', db.ForeignKey('rooms.roomname'))
)

# Definiert die Tabelle 'messages'
messages = db.Table('messages', metadata,
    # Definiert die Spalte 'message_id' als Primärschlüssel
    db.Column('message_id', db.String(36), primary_key=True),
    # Definiert die Spalte 'chat_message' als Text
    db.Column("chat_message", db.Text()),
    # Definiert die Spalte 'timestamp' mit aktuellem Zeitstempel als Standard
    db.Column('timestamp', db.TIMESTAMP, server_default=db.func.current_timestamp()),
    # Definiert die Spalte 'roomname' als Fremdschlüssel zu 'rooms'
    db.Column('roomname', db.ForeignKey('rooms.roomname')),
    # Definiert die Spalte 'username' als Fremdschlüssel zu 'users'
    db.Column('username', db.ForeignKey('users.username'))
)