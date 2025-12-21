# Imports
import sqlalchemy as db

# Metadaten für Datenbankstruktur
metadata = db.MetaData()

# Tabellendefinitionen
rooms = db.Table('rooms', metadata,
    db.Column('roomname', db.String(30), primary_key=True),
    db.Column('password', db.String(60))  # bcrypt-Hash (60 Zeichen)
) 

users = db.Table('users', metadata,
    db.Column('username', db.String(30), primary_key=True),
    db.Column('roomname', db.ForeignKey('rooms.roomname'))
)

messages = db.Table('messages', metadata,
    db.Column('message_id', db.String(36), primary_key=True),
    db.Column("chat_message", db.Text()),
    db.Column('timestamp', db.TIMESTAMP, server_default=db.func.current_timestamp()),
    db.Column('roomname', db.ForeignKey('rooms.roomname')),
    db.Column('username', db.ForeignKey('users.username'))
)