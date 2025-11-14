from pydantic import BaseModel

class RoomData(BaseModel):
    roomname: str
    password: str

class RoomDataResponse(BaseModel):
    message: str

