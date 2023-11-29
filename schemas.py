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
    
class BlogCreate(BaseModel):
    title: str
    description: str
    image_name: str 
    link: str  
    category: str   
    user_id: int

class BlogDisplay(BaseModel):
    id: int
    title: str
    description: str
    image_name: str
    link: str
    category: str
    user_id: int  
    image_url: str 

