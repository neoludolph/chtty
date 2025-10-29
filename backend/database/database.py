from sqlalchemy import create_engine, MetaData
from pathlib import Path
import uuid

current_file = Path(__file__).parent
db_path = current_file / 'database.db'

engine = create_engine(f"sqlite:///{db_path}", echo=True)
metadata = MetaData()

def create_db():
    metadata.create_all(engine)

def dispose_db():
    engine.dispose()

def create_room(username, room_password, room_name):
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with engine.begin() as connect:
        connect.execute()
    