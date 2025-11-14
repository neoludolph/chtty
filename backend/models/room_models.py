from pydantic import BaseModel

class RoomData(BaseModel):
    username: str
    roomname: str
    password: str

class RoomDataResponse(BaseModel):
    room_id: str
    message: str

class DeleteRoom(BaseModel):
    room_id: str
    password: str

