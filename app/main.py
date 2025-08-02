from fastapi import FastAPI
from app.routers import user, auth, player, team, performance, ranking, user_history

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(player.router)
app.include_router(team.router)
app.include_router(performance.router)
app.include_router(ranking.router)
app.include_router(user_history.router)

@app.get("/")
def hello_fastapi():
    return {"message": "¡Bienvenido a Titulares App!"}