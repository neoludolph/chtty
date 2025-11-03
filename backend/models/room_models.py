from pydantic import BaseModel
from typing import Union

class RoomData(BaseModel):
    username: str
    roomname: str
    password: Union[str, None]

class RoomDataResponse(BaseModel):
    room_id: str
    message: str

class DeleteRoom(BaseModel):
    room_id: str