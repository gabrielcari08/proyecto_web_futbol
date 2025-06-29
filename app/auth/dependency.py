from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.auth.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar las credenciales"
    )
    
    user_id = verify_access_token(token, credential_exception)
    
    #Equivalente a: SELECT * FROM users WHERE id = 'valor_de_user_credentials.id' LIMIT 1;
    user = db.query(User).filter(User.id == user_id).first()
    
    #Si el usuario no existe lanzamos la excepcion que creamos al principio.
    if user is None:
        raise credential_exception
    
    #Retornamos el usuario si es que existe.
    return user