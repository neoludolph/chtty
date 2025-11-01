from sqlalchemy import create_engine
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

def create_room(username, room_name, room_password):
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with engine.begin() as connect:
        connect.execute(rooms.insert().values(room_id=room_id, room_name=room_name, password=room_password)) 
        connect.execute(users.insert().values(user_id=user_id, username=username, room_id=room_id)) 
    message = "Room successfully created!"
    response = RoomDataResponse(room_id=str(room_id), message=message)
    return response

