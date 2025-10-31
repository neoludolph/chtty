import sqlalchemy as db

metadata = db.MetaData()

rooms = db.Table('rooms', metadata,
    db.Column('room_id', db.String(36), primary_key=True),
    db.Column('room_name', db.String(30)),
    db.Column('password', db.String(50), nullable=True)
) 

users = db.Table('users', metadata,
    db.Column('user_id', db.String(36), primary_key=True),
    db.Column('username', db.String),
    db.Column('room_id', db.ForeignKey('rooms.room_id'))
)

messages = db.Table('messages', metadata,
    db.Column('message_id', db.String(36), primary_key=True),
    db.Column('timestamp', db.TIMESTAMP, server_default=db.func.current_timestamp()),
    db.Column('room_id', db.ForeignKey('rooms.room_id')),
    db.Column('user_id', db.ForeignKey('users.user_id'))
)