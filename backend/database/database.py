from sqlalchemy import create_engine, delete
from pathlib import Path
import uuid
from backend.models.room_models import RoomDataResponse
from backend.database.models import rooms, users, messages, metadata
import shutil
import os

current_file = Path(__file__).parent
db_path = current_file / 'database.db'
template_db_path = current_file / 'database_empty.db'

if not os.path.exists(db_path):
    print("-> No database found! Create new from template ...")
    shutil.copy(template_db_path, db_path)

engine = create_engine(f"sqlite:///{db_path}", echo=True)

def create_db():
    metadata.create_all(engine)

def dispose_db():
    engine.dispose()

def create_room(room_name, room_password, username):
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with engine.begin() as connect:
        connect.execute(rooms.insert().values(room_id=str(room_id), room_name=room_name, password=room_password))
        connect.execute(users.insert().values(user_id=str(user_id), username=username, room_id=str(room_id)))
    message = "Room successfully created!"
    response = RoomDataResponse(room_id=str(room_id), message=message)
    return response

def delete_room(room_id):
    with engine.begin() as connect:
        connect.execute(delete(rooms).where(rooms.c.room_id == room_id))
    message = "Room successfully deleted!"
    response = RoomDataResponse(room_id=str(room_id), message=message)
    return response

def delete_rooms_table_content():
    with engine.begin() as connect:
        connect.execute(delete(rooms))
    message = "Table content of rooms successfully deleted!"
    return message

def delete_users_table_content():
    with engine.begin() as connect:
        connect.execute(delete(users))
    message = "Table content of users successfully deleted!"
    return message

def delete_messages_table_content():
    with engine.begin() as connect:
        connect.execute(delete(messages))
    message = "Table content of messages successfully deleted!"
    return message