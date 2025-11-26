
import sqlalchemy as sqla
from sqlalchemy.exc import SQLAlchemyError
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

engine = sqla.create_engine(f"sqlite:///{db_path}", echo=True)

def create_db():
    metadata.create_all(engine)

def dispose_db():
    engine.dispose()

def create_db_room(roomname, password):
    with engine.begin() as connect:
        connect.execute(rooms.insert().values(roomname=roomname, password=password))
    message = "Room successfully created!"
    response = RoomDataResponse(response_message=message)
    return response

def delete_db_room(roomname, password):
    with engine.begin() as connect:
       password_query = connect.execute(sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)).first()
    if (password_query is None):
        message = "Room does not exist!"
        response = RoomDataResponse(response_message=message)
        return response
    elif (password == password_query[0]):
        with engine.begin() as connect:
            connect.execute(sqla.delete(rooms).where(rooms.c.roomname == roomname))
        message = "Room successfully deleted!"
        response = RoomDataResponse(response_message=message)
        return response
    else:
        message = "The entered password is wrong!"
        response = RoomDataResponse(response_message=message)
        return response

# For API-Routes
def delete_rooms_table_content():
    with engine.begin() as connect:
        connect.execute(sqla.delete(rooms))
    message = "Table content of rooms successfully deleted!"
    return message

def delete_users_table_content():
    with engine.begin() as connect:
        connect.execute(sqla.delete(users))
    message = "Table content of users successfully deleted!"
    return message

def delete_messages_table_content():
    with engine.begin() as connect:
        connect.execute(sqla.delete(messages))
    message = "Table content of messages successfully deleted!"
    return message

def delete_all_tables_content():
    with engine.begin() as connect:
        connect.execute(sqla.delete(messages))
        connect.execute(sqla.delete(users))
        connect.execute(sqla.delete(rooms))
    message = "Content of all tables deleted!"
    return message

def delete_db(db_path):
    if (os.path.exists(db_path)):
        os.remove(db_path)
        return "Database deleted!"
    else:
        return "Database does not exist!"

# db checking functions
def check_if_db_room_exists(roomname):
    check = sqla.select(rooms.c.roomname).where(rooms.c.roomname == roomname)
    with engine.begin() as connect:
        result = connect.execute(check).first()
    if (result is None):
        return False
    else:
        return True 
    
def check_if_password_is_correct(roomname, password):
    check = sqla.select(rooms.c.password).where(rooms.c.roomname == roomname)
    with engine.begin() as connect:
        result = connect.execute(check).first()
    if (result is not None and result[0] == password):
        return True
    else: 
        return False
    
def save_message_in_db(roomname, message, username):
    message_id = str(uuid.uuid4())
    with engine.begin() as connect:
        message_query = sqla.insert(messages).values(
            message_id=message_id,
            chat_message=message,
            roomname=roomname,
            username=username
        )
        connect.execute(message_query)
    
def save_user_in_db(roomname, username):
    with engine.begin() as connect:
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        connect.execute(delete_user_from_users)
        user_insertion = sqla.insert(users).values(
            username=username,
            roomname=roomname,
        )
        connect.execute(user_insertion)
    
def delete_user_from_db(username):
    with engine.begin() as connect:
        delete_user_from_users = sqla.delete(users).where(users.c.username == username)
        connect.execute(delete_user_from_users)

def check_if_user_exists_in_db(username):
    user_check = sqla.select(users.c.username).where(users.c.username == username)
    with engine.begin() as connect:
        result = connect.execute(user_check).first()
    if (result is None):
        return False
    else:
        return True 
    
def get_messages_from_db(roomname):
    with engine.begin() as connect:
        get_messages = sqla.select(messages.c.chat_message, messages.c.username, messages.c.timestamp).where(messages.c.roomname == roomname).order_by(messages.c.timestamp)
        result = connect.execute(get_messages).fetchall()
    return result
