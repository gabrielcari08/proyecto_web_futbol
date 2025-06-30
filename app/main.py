from fastapi import FastAPI
from app.routers import user, auth, players, team

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(players.router)
app.include_router(team.router)

@app.get("/")
def hello_fastapi():
    return {"message": "¡Bienvenido a Titulares App!"}