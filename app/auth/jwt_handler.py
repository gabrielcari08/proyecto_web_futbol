#Este archivo gestiona la creacion y verificacion de tokens JWT para el sistema de autenticacion.
from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta #Para trabajar con expiracion de tokens
from app.core.config import settings
from jwt import PyJWTError, ExpiredSignatureError

#Constantes que controlan el token
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes #Minutos para que el token expire
JWT_AUDIENCE = settings.jwt_audience #Nueva constante añadida desde "user-setup"

#Crear un token
def create_access_token(user_id: str):
    #1. Preparar el payload con estandares JWT
    to_encode = {
        "sub": str(user_id),
        "aud": JWT_AUDIENCE,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "token_type": "access"
    }
    
    #2. Generar el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    #3. Retornamos el token JWT
    return encoded_jwt

#Verificar el token.
def verify_access_token(token: str, credentials_exception):
    try:
        #3. Decodificar el token incluyendo la audiencia
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=JWT_AUDIENCE
        )
        #4. Convertimos user_id a int, extrayendolo desde "sub"
        user_id = int(payload.get("sub")) #Ahora usamos 'sub' en vez de 'user_id'
        
        if user_id is None:
            raise credentials_exception
        return user_id
    
    except ExpiredSignatureError:
        # Token vencido
        raise HTTPException(
            status_code=401,
            detail="El token ha expirado. Por favor inicia sesión nuevamente."
        )
      
    except JWTError:
        raise credentials_exception