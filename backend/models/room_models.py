from pydantic import BaseModel

class RoomData(BaseModel):
    roomname: str
    password: str

class JoinRoomData(BaseModel):
    roomname: str
    password: str
    username: str

class RoomDataResponse(BaseModel):
    message: str

