from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from database import engine, localSession
from schemas import UserCreate, UserId
from models import Base, Users


Base.metadata.create_all(bind=engine)

app = FastAPI()

origin = [
    'http://localhost:5174'
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origines (ajusta según tus necesidades)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)


def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return 'Hi my name is FastAPI'


@app.get('/api/users/', response_model=list[UserId])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db=db)


@app.post('/login')
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.name == username).first()
    if user and user.password == password:  
        return {"token": "token-simulado"}  
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")


@app.post('/register')
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
  
    existing_user = db.query(Users).filter(Users.name == user_data.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = user_data.password  

    # Crear un nuevo usuario
    new_user = Users(name=user_data.name, email=user_data.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario creado con éxito", "user_id": new_user.id}
