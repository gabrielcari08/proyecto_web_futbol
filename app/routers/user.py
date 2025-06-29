from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.database import SessionLocal
from app.models.user import User
from app.auth.hashing import Hash
from app.auth.dependency import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

#Endpoint de prueba
@router.get("/")
async def hello_router():
    return {"message":"Hello router!"}

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpoint para registrar un nuevo usuario en la base de datos.
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    #Buscamos al usuario en la base de datos:
    #Equivalente a: SELECT * FROM users WHERE username = '[valor_del_usuario]' LIMIT 1;
    existing_user = db.query(User).filter(User.username == user.username).first()
    
    #Si el usuario existe en la base de datos nos salta una excepcion.
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe.")
    
    #Hasheo de contraseña.
    hashed_password = Hash.bcrypt(user.password)
    
    #Creamos una nueva instancia de User.
    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password,
        region = user.region
    )
    
    #Almacenamos esta instancia en la base de datos.
    db.add(new_user)
    #Guardamos los cambios.
    db.commit()
    #Refrescamos la base de datos.
    db.refresh(new_user)
    
    #Retornamos el usuario creado.
    return new_user

#Endpoint para que un usuario autenticado pueda ver su perfil.
@router.get("/profile", response_model=UserResponse)
async def view_profile(current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    
    return current_user
