#Este archivo gestiona la creacion y verificacion de tokens JWT para el sistema de autenticacion.
from jose import JWTError, jwt
from datetime import datetime, timedelta #Para trabajar con expiracion de tokens
from app.core.config import settings

#Constantes que controlan el token
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #Minutos para que el token expire

#Crear un token
def create_access_token(data: dict):
    #Hacemos una copia del diccionario original, para evitar modificar el argumento data directamente.
    to_encode = data.copy()
    
    #Calculamos la fecha de expiracion del token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #Agregamos una nueva clave "exp" al diccionario copiado.
    #Esta clave es requerida por el estándar JWT, ya que indica cuándo caduca el token.
    to_encode.update({"exp": expire}) 
    
    #Aqui generamos el token JWT cifrado.
    #Recibe: "to_encode": el diccionario
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    #Retornamos el token generado
    return encoded_jwt


#Verificar el token.
def verify_access_token(token: str, credentials_exception):
    try:
        #Decodificamos el token:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #Obtenemos el user_id que guardamos dentro del token que creamos en la funcion anterior
        user_id: int = payload.get("user_id")
        #Si el token no tiene el user_id:
        if user_id is None: 
            #Lanzamos una excepcion
            raise credentials_exception
        #Deolvemos el id del usuario autenticado
        return user_id   
    #Manejo de errores:      
    except JWTError:
        raise credentials_exception