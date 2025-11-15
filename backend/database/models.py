import sqlalchemy as db

metadata = db.MetaData()

rooms = db.Table('rooms', metadata,
    db.Column('room_name', db.String(30), primary_key=True),
    db.Column('password', db.String(50))
) 

users = db.Table('users', metadata,
    db.Column('username', db.String(30), primary_key=True),
    db.Column('room_name', db.ForeignKey('rooms.room_name'))
)

messages = db.Table('messages', metadata,
    db.Column('message_id', db.String(36), primary_key=True),
    db.Column('timestamp', db.TIMESTAMP, server_default=db.func.current_timestamp()),
    db.Column('room_name', db.ForeignKey('rooms.room_name')),
    db.Column('username', db.ForeignKey('users.username'))
)