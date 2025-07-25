from fastapi import FastAPI
from app.routers import user, auth, player, team, performance, ranking

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(player.router)
app.include_router(team.router)
app.include_router(performance.router)
app.include_router(ranking.router)

@app.get("/")
def hello_fastapi():
    return {"message": "¡Bienvenido a Titulares App!"}