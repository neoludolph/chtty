from sqlalchemy import create_engine, MetaData
from pathlib import Path
import uuid
from backend.models.room_models import RoomDataResponse

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
    with engine.begin() as connect:
        connect.execute() # <- Insert
    message = "Room successfully created!"
    response = RoomDataResponse(room_id=str(room_id), message=message)
    return response

