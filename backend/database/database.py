from sqlalchemy import create_engine, MetaData
from pathlib import Path

current_file = Path(__file__).parent
db_path = current_file / 'database.db'

engine = create_engine(f"sqlite:///{db_path}", echo=True)

metadata = MetaData()