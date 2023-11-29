from sqlalchemy.orm import Session

from models import Users, Blog 
from schemas import UserData

def get_users(db: Session):
    return db.query(Users).all()

def get_user_by_id(db: Session, id: int):
    return db.query(Users).filter(Users.id == id).first

def get_user_by_name(db: Session, name: str):
    return db.query(Users).filter(Users.name == name).first()

def create_user(db: Session, user: UserData):
    fake_password = user.password
    new_user = Users(name=user.name, password=fake_password)
    db.add(new_user)
    db.commit()
    db.flush(new_user)
    return new_user

def get_blogs(db: Session):
    return db.query(Blog).all()
    