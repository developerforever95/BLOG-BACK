from sqlalchemy import Column, Integer, String, Text, ForeignKey

from database import Base

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), index=True, unique=True)
    password = Column(String(30), index=True)
    email = Column(String(100), index=True)
    
class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)  
    description = Column(Text) 
    image_name = Column(String(100)) 
    link = Column(String(255))  
    category = Column(String(50))  
    user_id = Column(Integer, ForeignKey('users.id'))  