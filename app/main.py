from fastapi import FastAPI
from routers import user

app = FastAPI()

app.include_router(user.router)

@app.get("/")
def hello_fastapi():
    return {"message": "¡Bienvenido a Titulares App!"}