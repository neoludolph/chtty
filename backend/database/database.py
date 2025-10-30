from sqlalchemy import create_engine, MetaData
from pathlib import Path
import uuid
from backend.models.room_models import RoomDataResponse
from backend.models import rooms, users, messages

current_file = Path(__file__).parent
db_path = current_file / 'database.db'

engine = create_engine(f"sqlite:///{db_path}", echo=True)
metadata = MetaData()

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

