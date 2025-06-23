from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

#Endpoint de prueba
@router.get("/")
async def hello_router():
    return {"message":"Hello router!"}