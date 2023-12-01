from typing import List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

import crud
import os
from database import engine, localSession
from schemas import UserCreate, UserId, BlogCreate, BlogDisplay
from models import Base, Users, Blog 


Base.metadata.create_all(bind=engine)

app = FastAPI()

origin = [
    'http://localhost:5173'
]

app.mount("/imgs", StaticFiles(directory="imgs"), name="imgs")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.get('/api/users/', response_model=list[UserId])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db=db)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.post('/login')
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.name == username).first()
    if user and user.password == password:
        user_info = {
            "id": user.id,
            "username": user.name,
            "email": user.email,          
        }
        return {"token": "token-simulado", "user": user_info}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.post("/createBlog")
async def create_blog(
    title: str = Form(...), 
    description: str = Form(...),
    link: str = Form(...),
    category: str = Form(...),
    user_id: int = Form(...),
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)
):   
    try:
        file_location = f"imgs/{image.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image.file.read())
        
        new_blog = Blog(
            title=title,
            description=description,
            image_name=image.filename, 
            link=link,
            category=category,
            user_id=user_id
        )
        
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return True
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al crear el blog")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.get('/blogs', response_model=List[BlogDisplay])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = crud.get_blogs(db=db)

    for blog in blogs:
        blog.image_url = f"http://127.0.0.1:8000/imgs/{blog.image_name}" 

    return blogs

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.get('/blogs/{blog_id}', response_model=BlogDisplay)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog no encontrado")

    blog.image_url = f"http://127.0.0.1:8000/imgs/{blog.image_name}"
    return blog

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.get("/user/{user_id}/blogs")
def get_user_blogs(user_id: int, db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.user_id == user_id).all()
    return blogs

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.delete("/blogdelete/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog no encontrado")

    db.delete(blog)
    db.commit()
    return {"message": "Blog eliminado con éxito"}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.put("/blogedit/{blog_id}", response_model=BlogDisplay)
def edit_blog(blog_id: int, 
              title: str = Form(...), 
              description: str = Form(...),
              link: str = Form(...),
              category: str = Form(...),
              user_id: int = Form(...), 
              image: UploadFile = File(None),  
              db: Session = Depends(get_db)):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog no encontrado")

    if blog.user_id != user_id:
        raise HTTPException(status_code=403, detail="Operación no permitida")

    # Si se proporciona una nueva imagen, elimina la antigua del servidor
    if image:
        old_image_file = f"imgs/{blog.image_name}"
        if os.path.exists(old_image_file):
            os.remove(old_image_file)

        # Guardar la nueva imagen
        new_image_file = f"imgs/{image.filename}"
        with open(new_image_file, "wb+") as file_object:
            file_object.write(image.file.read())
        blog.image_name = image.filename

    # Actualizar otros campos
    blog.title = title
    blog.description = description
    blog.link = link
    blog.category = category

    db.commit()
    blog.image_url = f"http://127.0.0.1:8000/imgs/{blog.image_name}"
    return blog