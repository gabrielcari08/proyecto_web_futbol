#Este archivo contiene funciones para hashear una contraseña
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    
    #Genera un hash de una contraseña pasada en texto plano.
    @staticmethod
    def bcrypt(password: str):
        return pwd_context.hash(password)
    
    #Verifica si la contraseña pasada en texto plano coincide con la hasheada.
    @staticmethod
    def verify(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)