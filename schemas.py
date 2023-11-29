from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    password: str
    
class UserId(UserData):
    id: int 
    
class UserCreate(BaseModel):
    name: str
    email: str
    password: str    