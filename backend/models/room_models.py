from pydantic import BaseModel

class RoomData(BaseModel):
    roomname: str
    password: str

class JoinRoomData(BaseModel):
    type: str
    roomname: str
    password: str
    username: str

class ChatMessage(BaseModel):
    type: str
    username: str
    chat_message: str

class RoomDataResponse(BaseModel):
    response_message: str

