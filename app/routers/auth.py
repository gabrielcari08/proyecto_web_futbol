from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.user import Token, UserLogin
from app.models.user import User
from app.auth.jwt_handler import create_access_token
from app.auth.hashing import Hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpoint de prueba
@router.get("/")
async def hello_router():
    return {"Hello": "Auth"}

#Enpoint para logear usuario y retornar un token
@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    #Buscamos en la base de datos si el email del usuario coincide con el ingresado
    #Equivalente a: SELECT * FROM users WHERE username = 'valor_de_user_credentials.username' LIMIT 1;
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    #Si no existe el usuario lanzamos una excepcion.
    if not user:
        raise HTTPException(
            status_code=401,    
            detail="Credenciales incorrectas"
        )
        
    #Verificamos que la contraseña ingresada coincida con la almacenada y hasheada.
    if not Hash.verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,    
            detail="Credenciales incorrectas"
        )
    
    #Si todo es correcto, generamos el token con el id del usuario.
    access_token = create_access_token(user_id=user.id) #Antes: data={"user_id": user.id} 
    
    #Retornamos el token JWT
    return {"access_token": access_token, "token_type": "bearer"}
        
    